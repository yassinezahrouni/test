import pandas as pd
import json
import os
import io
import re
from datetime import datetime
#import google.generativeai as genai

# ============================
# Step 1: Load LLM1 Output and Filter by Today's Date
# ============================
llm1_output_file = "LLM/SCRM_LLM/LLM_Classifier_Output.xlsx"
llm1_df = pd.read_excel(llm1_output_file)

today_date = datetime.today().strftime("%Y-%m-%d")
llm1_today_df = llm1_df[llm1_df["output_date"] == today_date]

news_ids = llm1_today_df["news_article_id"].unique().tolist()

# ============================
# Step 2: Load Few-Shot Examples from JSON
# ============================
few_shots_path = "LLM/SCRM_LLM/FewShotPromptingSetup/Shots.json"
with open(few_shots_path, "r") as f:
    few_shots = json.load(f)

few_shots_text = ""
for shot in few_shots:
    few_shots_text += f"Input: {shot.get('input', '')}\nOutput: {json.dumps(shot.get('output', {}), indent=2)}\n\n"

# ============================
# Step 3: Load Supply Chain Data (Overview_SC)
# ============================
excel_path = "/Users/yassinezahrouni/coding/test/CountryIndexes/DB_SupplyChain_MA.xlsx"
suppliers_df = pd.read_excel(excel_path, sheet_name='Suppliers')
parts_df = pd.read_excel(excel_path, sheet_name='Parts')
purchase_orders_df = pd.read_excel(excel_path, sheet_name='PurchaseOrders')
deliveries_df = pd.read_excel(excel_path, sheet_name='Deliveries')
shipments_df = pd.read_excel(excel_path, sheet_name='Shipments')
segments_df = pd.read_excel(excel_path, sheet_name='ShipmentSegments')

Overview_SC = (
    purchase_orders_df
    .merge(suppliers_df, on='SupplierID', how='left')
    .merge(deliveries_df, on='purchaseordernumber', how='left')
    .merge(shipments_df, on='deliverynumber', how='left')
    .merge(segments_df, on='shipment_itinerarynumber', how='left')
    .merge(parts_df, on='partnumber', how='left')
).drop_duplicates()

# ============================
# Step 4: Load News Articles
# ============================
news_articles_file = "/Users/yassinezahrouni/coding/test/NewsArticles.csv"
news_articles_df = pd.read_csv(news_articles_file)

# ============================
# Step 5: Define Risk Categories, Causes, and Impacts Text Block
# ============================
risk_categories_text = """
1. Political and Regulatory Risk
   - Potential Causes: War, terrorism, political unrest, civil conflicts; trade policies, tariffs, sanctions, regulatory changes; corruption, government intervention, regime changes.
   - Impacts on Supply Chain: Disrupted supply routes; increased operational costs; production and sourcing uncertainty; delays and interruptions in product flows.

2. Environmental and Natural Risk:
   - Potential Causes: Natural disasters (earthquakes, floods, hurricanes, tsunamis, fires); climate-related events, ecosystem disruptions; sustainability and environmental regulations.
   - Impacts on Supply Chain: Asset destruction and infrastructure damage; production halts and operational delays; increased costs and prolonged lead times; reduced customer satisfaction due to delays.

3. Financial and Economic Risk
   - Potential Causes: Inflation, market fluctuations, economic downturns; credit risks, bankruptcy, price volatility; insurance issues, asset devaluation, currency fluctuations.
   - Impacts on Supply Chain: Increased operational and financial costs; reduced profitability and liquidity; difficulty securing financing or investment; potential disruption in payment flows to suppliers.

4. Supply and Demand Risk
   - Potential Causes: Material shortages, inventory imbalances, demand fluctuations; supplier failures or limited sourcing options; overstock or understock situations.
   - Impacts on Supply Chain: Production delays and interruptions; higher costs due to scarcity and competition for resources; inability to meet customer demand; reduced customer satisfaction and market share loss.

5. Logistics and Transportation Risk
   - Potential Causes: Transportation disruptions (delays, inadequate infrastructure, unreliable services); limited storage or distribution capacity; route inefficiencies, congestion, coordination issues.
   - Impacts on Supply Chain: Increased transportation and operational costs; delivery delays and longer lead times; lower customer satisfaction and reliability; disrupted inventory management and production scheduling.

6. Technological and System Risk
   - Potential Causes: Technology breakdowns, hardware and software failures; cybersecurity breaches, data integrity issues; poor visibility, inadequate process integration, communication failures.
   - Impacts on Supply Chain: Reduced production efficiency and resource availability; delays due to technology failures or cybersecurity incidents; higher operational costs due to disruptions; decreased quality control and reliability.

7. Operational and Labor Risk
   - Potential Causes: Labor shortages, strikes, low employee satisfaction; capacity constraints, production bottlenecks, operational inefficiencies; poor process management and scheduling errors.
   - Impacts on Supply Chain: Reduced operational efficiency and productivity; delayed production schedules and shipments; increased labor and operational costs; lower product quality and customer dissatisfaction.
"""

# ============================
# Step 6: Helper Functions for Parsing
# ============================
def parse_annotated_supplier_ids(suppliers_str):
    """
    From a string like "36 (location-based); 38 (shipment-based)" return a list of supplier IDs as strings: [ "36", "38" ].
    """
    if not suppliers_str.strip():
        return []
    parts = [p.strip() for p in suppliers_str.split(";") if p.strip()]
    supplier_ids = []
    for part in parts:
        match = re.match(r"(\d+)", part)
        if match:
            supplier_ids.append(match.group(1))
    return supplier_ids

def parse_route_segments(route_seg_str):
    """
    Splits a string like "Route-A15-Seg1; Route-A16-Seg2" into a list of route segments.
    """
    if not route_seg_str.strip():
        return []
    parts = [p.strip() for p in route_seg_str.split(";") if p.strip()]
    return parts

def split_shipment(shipment_str):
    """
    Splits "Route-A16-Seg2" into ("Route-A16", "2").
    """
    shipment_str = shipment_str.strip()
    if '-' in shipment_str:
        parts = shipment_str.rsplit('-', 1)
        itinerary = parts[0].strip()
        seg = parts[1].strip()
        segment = seg.lower().replace("seg", "").strip()
        return itinerary, segment
    else:
        return shipment_str, ""

def parse_categories_and_causes(categories_str):
    """
    Parses a string like "Environmental and Natural Risk (natural disasters); Logistics and Transportation Risk (transportation disruptions)"
    and returns a list of dicts.
    """
    if not categories_str.strip():
        return []
    segments = [seg.strip() for seg in categories_str.split(";") if seg.strip()]
    results = []
    pattern = r"^(.*?)\s*\((.*?)\)$"
    for seg in segments:
        match = re.match(pattern, seg)
        if match:
            category = match.group(1).strip()
            cause = match.group(2).strip()
            results.append({"category": category, "cause": cause})
        else:
            results.append({"category": seg, "cause": ""})
    return results

# ============================
# Step 7: Loop Through Each News Article from Today's LLM1 Outputs and Build Prompt for LLM2
# ============================
# For shipment filtering: convert "deliverydate" to datetime; today is already defined.
Overview_SC["deliverydate"] = pd.to_datetime(Overview_SC["deliverydate"], errors='coerce')
today = pd.to_datetime(today_date)

# Loop through each news_id
for news_id in news_ids:
    # Filter LLM1 output for the current news_id
    current_llm1 = llm1_today_df[llm1_today_df["news_article_id"] == news_id]
    llm1_text = current_llm1.to_csv(index=False)
    
    # Retrieve the corresponding news article text
    news_row = news_articles_df[news_articles_df["news_article_id"] == news_id]
    if not news_row.empty:
        news_article_text = news_row.iloc[0]["news_article"]
    else:
        news_article_text = "News article not found."
    
    # Parse impacted supplier IDs (remove annotations)
    impacted_suppliers = []
    for idx, row in current_llm1.iterrows():
        supp_str = str(row.get("impacted_supplier_ids", "")).strip()
        impacted_suppliers.extend(parse_annotated_supplier_ids(supp_str))
    impacted_suppliers = list(set(impacted_suppliers))
    
    # Parse route segments (as provided, no splitting here)
    impacted_routesegs = []
    for idx, row in current_llm1.iterrows():
        route_str = str(row.get("impacted_routesegments", "")).strip()
        impacted_routesegs.extend(parse_route_segments(route_str))
    impacted_routesegs = list(set(impacted_routesegs))
    
    # Parse categories and causes (if needed)
    categories_causes = []
    for idx, row in current_llm1.iterrows():
        cat_str = str(row.get("risk categories and potential causes", "")).strip()
        categories_causes.extend(parse_categories_and_causes(cat_str))
    
    # ---------------------------
    # Supplier Context: Filter Overview_SC for these suppliers (using SupplierID)
    # ---------------------------
    suppliers_context_text = "No supplier details available."
    if impacted_suppliers:
        parsed_supp_ids = []
        for s in impacted_suppliers:
            try:
                parsed_supp_ids.append(int(s))
            except ValueError:
                parsed_supp_ids.append(s)
        supp_context_df = Overview_SC[Overview_SC["SupplierID"].isin(parsed_supp_ids)].drop_duplicates()
        if not supp_context_df.empty:
            suppliers_context_text = supp_context_df.to_csv(index=False)
    
    # ---------------------------
    # Shipment/Route Context:
    # Filter Overview_SC based on shipment_itinerarynumber and Segment number,
    # and then for each group, keep only the next 5 shipments with deliverydate > today.
    # ---------------------------
    routeseg_context_text = "No route segment details available."
    if impacted_routesegs:
        # For each impacted route segment, parse into itinerary and segment parts.
        itinerary_list = []
        segment_list = []
        for seg in impacted_routesegs:
            it, sr = split_shipment(seg)
            itinerary_list.append(it)
            segment_list.append(sr)
        itinerary_list = list(set(itinerary_list))
        segment_list = list(set(segment_list))
        
        filtered_routeseg = Overview_SC[
            (Overview_SC["shipment_itinerarynumber"].isin(itinerary_list)) &
            (Overview_SC["Segment number"].astype(str).isin(segment_list)) &
            (Overview_SC["deliverydate"] > today)
        ].drop_duplicates()
        
        if not filtered_routeseg.empty:
            group_cols = ["SupplierID", "shipment_itinerarynumber", "Segment number"]
            # Group by supplier and route, sort by deliverydate, and take up to 5 rows per group.
            routeseg_context_df = filtered_routeseg.sort_values("deliverydate").groupby(group_cols).head(5)
            routeseg_context_text = routeseg_context_df.to_csv(index=False)
    
    # ---------------------------
    # Compose the Prompt for LLM2
    # ---------------------------
    prompt_for_llm2 = f"""
You are a highly experienced Senior Supply Chain Manager responsible for extensive risk assessment.

Below are few-shot examples to guide your risk assessment:
{few_shots_text}

Risk Categories, Causes, and Impacts to consider:
{risk_categories_text}

The output from the previous classification (LLM1) for news article ID "{news_id}" is:
{llm1_text}

Supplier details relevant to the assessment:
{suppliers_context_text}

Shipment details relevant to the assessment (using shipment_itinerarynumber and Segment number):
{routeseg_context_text}

The full news article text is:
{news_article_text}

Using the above context and the historical risk assessments, please perform an extensive risk assessment. In your response, please include:
- A detailed analysis of potential risk categories, their causes, and impacts.
- Identification of the impacted suppliers and shipments (by supplier IDs and shipment_itinerarynumber plus Segment rank).
- Specific recommendations to mitigate the identified risks.
- A clear rationale that explains any changes or escalations in risks based on previous assessments (if available).

Return your response as valid JSON.
"""
    print("\n============================")
    print(f"PROMPT for news_article_id={news_id}")
    print("============================\n", prompt_for_llm2)
    
    # Send the prompt to LLM2
    convo = model.start_chat(history=[])
    convo.send_message(prompt_for_llm2)
    llm2_response = convo.last.text
    
    print("LLM2 Response for news article ID", news_id, ":")
    print(llm2_response)
    
    # Save LLM2 output (e.g., one file per news_id)
    output_file = f"LLM/SCRM_LLM/LLM2_Risk_Assessment_{news_id}.json"
    with open(output_file, "w") as f:
        f.write(llm2_response)
    
    print("LLM2 output for news article ID", news_id, "saved to", output_file)
