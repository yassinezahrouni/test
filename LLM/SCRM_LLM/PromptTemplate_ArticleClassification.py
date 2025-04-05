import pandas as pd

# Path to your Excel file
excel_path = "/Users/yassinezahrouni/coding/test/CountryIndexes/DB_SupplyChain_MA.xlsx"

# Read the relevant sheets into DataFrames
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
)

#print(Overview_SC.columns)

SuppliersProfileData = Overview_SC[[ 'suppliername', 'SupplierID', 'City', 'Country', 'Region/Province/State', 'Continent', 'World Region', 'Nearest Port', 'shipment_itinerarynumber']].copy()

SuppliersProfileData = SuppliersProfileData.drop_duplicates()

ShipmentsProfileData = Overview_SC[['shipment_itinerarynumber', 'Segment_From', 'Segment_To', 'Roads', 'Country of roads', 'Segment description', 'Segment number']].copy()

ShipmentsProfileData['RouteSegment'] = (ShipmentsProfileData['shipment_itinerarynumber'].astype(str) +
                                          '-Seg' +
                                          ShipmentsProfileData['Segment number'].astype(str))

ShipmentsProfileData.drop(['shipment_itinerarynumber', 'Segment number'], axis=1, inplace=True)
ShipmentsProfileData = ShipmentsProfileData.drop_duplicates()

# Grouping the shipment numbers
SuppliersProfileDataGrouped = SuppliersProfileData.groupby(
    ['suppliername', 'SupplierID', 'City', 'Country', 'Region/Province/State', 
     'Continent', 'World Region', 'Nearest Port']).agg({'shipment_itinerarynumber': lambda x: '; '.join(map(str, sorted(set(x))))}).reset_index()

ShipmentsProfileDataGrouped = ShipmentsProfileData.groupby(
       ['Segment_From', 'Segment_To', 'Roads', 'Country of roads']).agg({
        'RouteSegment': lambda x: '; '.join(map(str, sorted(set(x))))}).reset_index()


# Convert the df to CSV format as a string
SuppliersProfiles = SuppliersProfileDataGrouped.to_csv(index=False)
ShipmentsProfiles = ShipmentsProfileDataGrouped.to_csv(index=False)
print('###### SUPPLIERDATA', SuppliersProfiles)
print('###### SHIPMENTDATA', ShipmentsProfiles)

# Input news article instance
from datetime import datetime
# today = datetime.date.today()
# News_article_ID, News_article = Pull_News_article(today)

# Example: Assume you have pulled the news article ID and article text as follows:
News_article_ID = "NA123"  # Example news article ID
News_article = "major Chinese copper smelters, including Tongling Nonferrous Metals Group, initiated extensive maintenance shutdowns due to a severe shortage of copper concentrate and negative processing fees. Nearly 8% of China's total smelting capacity was taken offline, significantly higher than usual."

# News_article = "major Chinese copper smelters, including Tongling Nonferrous Metals Group, initiated extensive maintenance shutdowns due to a severe shortage of copper concentrate and negative processing fees. Nearly 8% of China's total smelting capacity was taken offline, significantly higher than usual."

# Few-shot examples in CSV format
few_shots = """
news_article,supply_chain_relevance,reason,impacted_supplier_ids,impacted_routesegments,Risk categories and potential causes
"Argentina celebrates victory as they win the Copa América 2024, with Lionel Messi scoring the winning goal in a dramatic final against Brazil.",false,"This news is about a sports event and has no connection to suppliers, shipments, logistics, or transportation infrastructure.",,,""
"A new species of deep-sea jellyfish was discovered by marine biologists in the Mariana Trench, showcasing a unique bioluminescent pattern.",false,"This scientific discovery is not related to any supply chain operation, risk, or infrastructure.",,,""
"Mass protests erupt in Tunisia's capital, Tunis, leading to the resignation of key government officials.",true,"The news mentions unrest in Tunisia, which can directly impact suppliers based in Tunisia due to security issues, limited truck logistics, and shutdown of plant/port operations.","4","Route-A11_Seg1","Political and Regulatory Risk (political unrest, government intervention)"
"Tensions rise in the South China Sea as naval forces from multiple countries conduct military deployment.",true,"The article discusses geopolitical conflict in the South China Sea, a critical maritime route. Shipments passing through this region may face disruptions or delays, making it highly relevant to supply chain operations.",1,"Route-A2_Seg1","Political and Regulatory Risk (geopolitical tension); Logistics and Transportation Risk (maritime route disruption)"
"""

# Adjusted prompt template expecting CSV output
Prompt = f"""
You are a supply chain news classification assistant.

You are provided with:
1. A list of suppliers (in CSV format) that includes information like supplier name, ID, location, and nearest port.
2. A list of shipments (in CSV format) showing route segments, countries passed through, and relevant ports.
3. A news article to analyze.
4. Few-shot examples in CSV format that provide guidance for classification and reasoning.

Your job is to assess the news article based on the supply chain relevance criteria described below. Use the few-shot examples as guidance for your classification and reasoning. With the context of the supplier and shipment profiles provided, you must:
- Classify the news article as relevant ("true") or not ("false").
- Explain your reasoning.
- Identify any suppliers or shipments that might be even slightly impacted by the risks mentioned in the article.
- Identify which risk categories are relevant and list the potential causes associated with each category.
- Return the IDs of these suppliers and Route segments (format the route segments like this example 'Route-A1-Seg1' ) , and also include the identified risk categories and potential causes in an extra column, in the format:  
  *Category (potential cause1, potential cause2, ...); Category (potential cause1, potential cause2, ...); ...*

Follow these steps and return your output strictly in CSV format with a header row:

---
Step 1: Determine if the news article is supply chain relevant.
Before reaching any conclusion, carefully analyze and think about the content of the article. First, consider whether the article describes or implies any events that could lead to any of the potential risk causes—whether these are explicitly mentioned or implicitly suggested—and then identify the appropriate risk categories that are relevant based on the content:

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

Assess the article's content in detail. Identify which of these risk categories might be relevant, and explicitly list the potential causes that could be a consequence of the article's content. If the article mentions or implies any of these potential causes or impacts (even if indirectly) it should be considered relevant. Otherwise, classify it as "false".

---
Step 2: If the article is relevant, identify the risk dimensions (e.g., location disruption, transport route disruption, industry-specific impact, regulatory/economic impact) as part of your reasoning.

---
Step 3: From the provided supplier and shipment lists, identify any that could be impacted.
- For suppliers, match by location (city or country), industry, or product category mentioned in the article.
- For shipments, match if their origin, destination, or route segments overlaps with the regions or routes mentioned in the article.
- Include the IDs of any suppliers or Route segments  that are even slightly potentially concerned.
- List multiple IDs separated by a semicolon (;).

---
"news_article": {News_article}

Supplier Data:
{SuppliersProfiles}

Shipment Data:
{ShipmentsProfiles}

Few-shot Examples (CSV format for classification and reasoning guidance):
{few_shots}

Now perform the analysis and return your output in CSV format only, with the following header:

supply_chain_relevance,reason,impacted_supplier_ids,impacted_routesegments,Risk categories and potential causes
"""

#print(Prompt)



########## Running the prompt in the LLLM

API_KEY = "AIzaSyDEZW5ab9s8DN_sFS4nP9PkAh8ZhsFf8pU"
import google.generativeai as genai

# Configure API key (replace with your actual API key)
genai.configure(api_key=API_KEY)

# Define generation configuration
generation_config = {
    "temperature": 0.5,  # Controls randomness (0 = deterministic, 1 = more creative)
    "max_output_tokens": 4000,  # Limits the length of output
}

# Initialize the model with the correct argument name
model = genai.GenerativeModel(model_name="gemini-2.0-flash", generation_config=generation_config)

# Start a chat session
convo = model.start_chat(history=[])

# Send a message to the model
convo.send_message(Prompt)

# Print the response
csv_LLM_classifier_output = convo.last.text

print(csv_LLM_classifier_output)


########## Saving the Output in an excel if supply chain relevant 
import pandas as pd
import os
import io
import re

# Assume csv_LLM_classifier_output contains the raw output from your LLM
raw_csv = csv_LLM_classifier_output

# Remove any markdown triple backticks and extra text before/after the CSV content.
match = re.search(r"(supply_chain_relevance.*)", raw_csv, re.DOTALL)
if match:
    csv_data = match.group(1).strip()
else:
    raise ValueError("CSV header not found in the LLM output.")

# Optionally, remove enclosing backticks if present
csv_data = csv_data.strip("`").strip()

# Read the CSV string into a DataFrame using skipinitialspace to help with spacing
df = pd.read_csv(io.StringIO(csv_data), skipinitialspace=True)

# Normalize column names (strip whitespace and convert to lower case)
df.columns = df.columns.str.strip().str.lower()

# Debug: Print columns to verify
print("Columns in CSV:", df.columns.tolist())

# Filter rows where supply_chain_relevance is "true" (convert to string first)
if 'supply_chain_relevance' not in df.columns:
    raise ValueError("Expected column 'supply_chain_relevance' not found in the CSV data.")

df = df[df['supply_chain_relevance'].astype(str).str.lower() == "true"]

# List to hold the separated rows
separated_rows = []

# Helper function to split route segment id into shipment itinerary and segment rank
def split_shipment(shipment_str):
    shipment_str = shipment_str.strip()
    if '-' in shipment_str:
        parts = shipment_str.rsplit('-', 1)
        itinerary = parts[0].strip()
        seg = parts[1].strip()
        # Remove any leading "Seg" (case-insensitive)
        segment = seg.lower().replace("seg", "").strip()
        return itinerary, segment
    else:
        return shipment_str, ""

# Process each row that is supply chain relevant and include the news article ID
for idx, row in df.iterrows():
    base_data = {
        "news_article_id": News_article_ID,
        "supply_chain_relevance": row["supply_chain_relevance"],
        "relevance_reason": row["reason"],
        "Risk categories and potential causes": row["risk categories and potential causes"] if "risk categories and potential causes" in df.columns else ""
    }
    
    # Convert impacted_supplier_ids to string if not NaN
    supplier_str = ""
    if pd.notna(row["impacted_supplier_ids"]):
        supplier_str = str(row["impacted_supplier_ids"]).strip()
        if supplier_str.lower() == "nan":
            supplier_str = ""
    
    # Convert impacted_routesegments to string if not NaN
    routeseg_str = ""
    if pd.notna(row["impacted_routesegments"]):
        routeseg_str = str(row["impacted_routesegments"]).strip()
        if routeseg_str.lower() == "nan":
            routeseg_str = ""
    
    # Process impacted_supplier_ids: if available, split by semicolon
    supplier_ids = []
    if supplier_str != "":
        supplier_ids = [s.strip() for s in supplier_str.split(";") if s.strip()]
    
    # Process impacted_routesegments similarly.
    route_segments = []
    if routeseg_str != "":
        route_segments = [s.strip() for s in routeseg_str.split(";") if s.strip()]
    
    # Create separate rows for each supplier id
    for sid in supplier_ids:
        new_row = base_data.copy()
        new_row["impacted_supplier_ids"] = sid
        new_row["impacted_routesegments"] = ""
        new_row["shipment_itinerarynumber"] = ""
        new_row["Segment_rank"] = ""
        separated_rows.append(new_row)
    
    # Create separate rows for each route segment (splitting into shipment itinerary and segment rank)
    for segment in route_segments:
        itinerary, seg_rank = split_shipment(segment)
        new_row = base_data.copy()
        new_row["impacted_supplier_ids"] = ""
        new_row["impacted_routesegments"] = segment
        new_row["shipment_itinerarynumber"] = itinerary
        new_row["Segment_rank"] = seg_rank
        separated_rows.append(new_row)

# Create a new DataFrame from the separated rows with the required columns
df_separated = pd.DataFrame(separated_rows, columns=[
    "news_article_id", "supply_chain_relevance", "relevance_reason", 
    "impacted_supplier_ids", "impacted_routesegments", 
    "shipment_itinerarynumber", "Segment_rank",
    "Risk categories and potential causes"
])

# Define the Excel file name
excel_file = "LLM/SCRM_LLM/LLM_Classifier_Output.xlsx"

# If the Excel file exists, load existing data and append; otherwise, start fresh.
if os.path.exists(excel_file):
    df_existing = pd.read_excel(excel_file)
    df_result = pd.concat([df_existing, df_separated], ignore_index=True)
else:
    df_result = df_separated

# Save the resulting DataFrame to the Excel file
df_result.to_excel(excel_file, index=False)
print("Data appended to Excel file:", excel_file)

