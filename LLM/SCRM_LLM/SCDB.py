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
#print(SuppliersProfiles)
#print(ShipmentsProfiles)

# Input news article instance
News_article = "major Chinese copper smelters, including Tongling Nonferrous Metals Group, initiated extensive maintenance shutdowns due to a severe shortage of copper concentrate and negative processing fees. Nearly 8% of China's total smelting capacity was taken offline, significantly higher than usual."

# Few-shot examples in CSV format
few_shots = """news_article,supply_chain_relevance,reason,impacted_supplier_ids,impacted_shipment_ids
"Argentina celebrates victory as they win the Copa América 2024, with Lionel Messi scoring the winning goal in a dramatic final against Brazil.",false,"This news is about a sports event and has no connection to suppliers, shipments, logistics, or transportation infrastructure.",,
"A new species of deep-sea jellyfish was discovered by marine biologists in the Mariana Trench, showcasing a unique bioluminescent pattern.",false,"This scientific discovery is not related to any supply chain operation, risk, or infrastructure.",,
"Mass protests erupt in Tunisia's capital, Tunis, leading to the resignation of key government officials.",true,"The news mentions unrest in Tunisia, which can directly impact suppliers based in Tunisia due to security issues, limited truck logistics, and shutdown of plant/port operations.","S001",
"Tensions rise in the South China Sea as naval forces from multiple countries conduct military deployment.",true,"The article discusses geopolitical conflict in the South China Sea, a critical maritime route. Shipments passing through this region may face disruptions or delays, making it highly relevant to supply chain operations.",,"SHIP123"
"""

# Adjusted prompt template expecting CSV output
Prompt_Template = f"""
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
- Return the IDs of these suppliers and shipments in your output (list multiple IDs separated by a semicolon).

Follow these steps and return your output strictly in CSV format with a header row:

---
Step 1: Determine if the news article is supply chain relevant.
- Classify it as "true" if the article includes or implies any factors that could affect supply chains, such as:
  - Production, logistics, trade, regulations, raw materials, or demand disruptions.
  - Natural disasters, strikes, war, infrastructure issues, port closures, new laws, or geopolitical changes.
  - Even weak or indirect signals should be considered relevant.
- Otherwise, classify as "false".

---
Step 2: If the article is relevant, identify the risk dimensions (e.g., location disruption, transport route disruption, industry-specific impact, regulatory/economic impact) as part of your reasoning.

---
Step 3: From the provided supplier and shipment lists, identify any that could be impacted.
- For suppliers, match by location (city or country), industry, or product category mentioned in the article.
- For shipments, match if their origin, destination, or route overlaps with the regions or routes mentioned in the article.
- Include the IDs of any suppliers or shipments that are even slightly potentially concerned.
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

supply_chain_relevance,reason,impacted_supplier_ids,impacted_shipment_ids
"""

print(Prompt_Template)



########## Running the prompt in the LLLM





########## Saving the Output in an excel if supply chain relevant 
import pandas as pd
import os
import io

# CSV string input (example)
csv_data = """supply_chain_relevance,reason,impacted_supplier_ids,impacted_shipment_ids
true,"The article highlights a major disruption in copper production in China due to extensive maintenance shutdowns at smelters, which could lead to a shortage of a critical raw material. This risk dimension of production disruption and raw material shortage may affect downstream manufacturing and supply chain operations. In our supplier list, Foxconn (SupplierID 1) is based in Shanghai, China, making it potentially vulnerable. Additionally, the shipment from Shanghai (Route-A1-Seg1) is likely to be impacted due to its origin in the affected region.","1","Route-A1-Seg1"
"""

# Read the CSV string into a DataFrame
df = pd.read_csv(io.StringIO(csv_data))

# Filter only rows with supply_chain_relevance as "true"
df_true = df[df['supply_chain_relevance'].str.lower() == "true"].copy()

if not df_true.empty:
    # Function to split impacted_shipment_ids into shipmentitinerary_number and segmentnumber
    def split_shipment(shipment_str):
        # Remove any extra spaces and process each shipment id
        shipments = [s.strip() for s in shipment_str.split(';') if s.strip()]
        itinerary_numbers = []
        segment_numbers = []
        for s in shipments:
            # Find the last '-' to separate the itinerary number from the segment part
            if '-' in s:
                parts = s.rsplit('-', 1)
                itinerary = parts[0]
                seg = parts[1]
                # Remove any leading "Seg" (case-insensitive) from seg to get the segment number
                segment = seg.replace("Seg", "").replace("seg", "")
                itinerary_numbers.append(itinerary)
                segment_numbers.append(segment)
            else:
                # If no '-' exists, add the full string and leave segment empty
                itinerary_numbers.append(s)
                segment_numbers.append("")
        # Join multiple entries by semicolon if there are more than one
        return ";".join(itinerary_numbers), ";".join(segment_numbers)

    # Apply the splitting function on the impacted_shipment_ids column
    df_true[['shipmentitinerary_number', 'segmentnumber']] = df_true.apply(
        lambda row: pd.Series(split_shipment(row['impacted_shipment_ids'])), axis=1
    )

    # Define the output Excel file name
    excel_file = "LLM_classifier_output.xlsx"

    # If the Excel file exists, read it, otherwise create a new DataFrame
    if os.path.exists(excel_file):
        df_existing = pd.read_excel(excel_file)
        # Append new rows to the existing DataFrame
        df_result = pd.concat([df_existing, df_true], ignore_index=True)
    else:
        df_result = df_true

    # Save the DataFrame back to the Excel file
    df_result.to_excel(excel_file, index=False)
    print("Output appended to Excel file:", excel_file)
else:
    print("No relevant supply chain data to save.")
