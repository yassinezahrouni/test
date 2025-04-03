API_KEY = "AIzaSyDEZW5ab9s8DN_sFS4nP9PkAh8ZhsFf8pU"
import google.generativeai as genai

# Configure API key (replace with your actual API key)
genai.configure(api_key=API_KEY)

# Define generation configuration
generation_config = {
    "temperature": 0.7,  # Controls randomness (0 = deterministic, 1 = more creative)
    "max_output_tokens": 700,  # Limits the length of output
}

# Initialize the model with the correct argument name
model = genai.GenerativeModel(model_name="gemini-2.0-flash", generation_config=generation_config)

# Start a chat session
convo = model.start_chat(history=[])

prompt = """
news article:
"headline": "Nissan Could Nab Foxconn Exec For Its New CEO",
"link": "https://insideevs.com/news/752625/nissan-foxconn-executive-replace-ceo/",
"source": "InsideEVs",
"snippet": "Nissan's falling out with Honda was just as unexpected as talks of its potential merger. Yet, somehow, it felt inevitable—neither brand seemed interested in a true 50/50 partnership. Soon, rumors arose that the deal was to avoid a hostile takeover from Taiwanese electronics giant Foxconn. Ironically, Nissan may now tap a Foxconn executive to replace its CEO.",
"date_published": "3 days ago"

Context:
Assume you are an expert in supply chain management. I represent a company that sources materials, components, and products from various suppliers across different regions. My goal is to assess the potential risks to my supply chain based on the provided news article.

The news article may be related to:
- One of my suppliers as a company (e.g., financial instability, management decisions, operational risks, factory shutdowns, strikes, quality issues, or other potential disruptive events)
- The location where my supplier’s factory or distribution center is based (e.g., political instability, regulatory changes, economic downturns, natural disasters, energy crises, or other potential disruptive events)
- **Itineraries and locations along the shipment routes that transport parts from my supplier’s location to my warehouses or factories (e.g., shipping disruptions, port congestion, labor strikes, customs delays, highway closures, or other potential disruptive events)

Task:
1. First, classify the type of news article as one of the following:
   - Supplier-related
   - Location-related
   - Shipment-related
   - Other (if applicable)

2. Then, generate the output in the following nested structure:

Output Format:
The output must start with:
{
  "News Classification": "Supplier-related",
  "Headline": "Magna price target lowered to $36.50 from $44 at CIBC",
  "Supplier Name": "Magna",
  "Link": "https://finance.yahoo.com/news/magna-price-target-lowered-36-145611596.html",
  "Risk Assessment": {
    "Flow-Based Risks": [
      {
        "Risk Type": "Money Flow Disruptions",
        "Risk Explanation": "The price target downgrade could lead to reduced investor confidence and financial strain on Magna.",
        "Risk Reasoning": "CIBC lowered Magna's price target due to concerns over U.S. tariffs, impacting financial stability.",
        "Risk Score": 7
      }
    ],
    "Supply Chain Risks": [
      {
        "Risk Type": "Supply Side Risks",
        "Risk Explanation": "Tariffs could increase raw material costs for Magna, leading to supply chain delays or price hikes.",
        "Risk Reasoning": "The analyst notes that tariffs create uncertainty for the auto industry, disrupting supply chains.",
        "Risk Score": 6
      }
    ],
    "Economic Impact Risks": [
      {
        "Risk Type": "Economic Impact",
        "Risk Explanation": "Potential cost-cutting measures or reduced capital expenditure (CAPEX) in response to financial pressures could affect supply chain resilience and innovation.",
        "Risk Reasoning": "The price downgrade may force Magna to cut costs, impacting future investments.",
        "Risk Score": 4
      }
    ],
    "Overall Risk Score": 6
  }
}

Risk Classification Framework:
Characteristics-Based Risk Classification:
- Endogenous Risks: Internal financial management issues affecting procurement, R&D investments, or manufacturing operations.
- Exogenous Risks: External factors like economic instability, regulatory changes, or geopolitical tensions impacting Magna’s supply chain.

Intentional vs. Unintentional Risks:
- Intentional Risks: Financial decisions like dividend payouts, stock price volatility, or government defense spending policies leading to supply chain risks.
- Unintentional Risks: Unexpected market downturns, reduced investor confidence, or cash flow challenges affecting supplier payments and production.

Location-Based Risk Classification:
- Manufacturing Side Risks: Delayed production, quality control issues, or reduced investment in new technologies.
- Supply Side Risks: Supplier disruptions due to financial instability, procurement delays, or raw material shortages.
- Demand Side Risks: Stock price fluctuations signaling potential reductions in contracts or delayed orders.

Flow-Based Risk Classification:
- Money Flow Disruptions: Declining stock prices and cash flow uncertainty leading to payment delays, credit risks, or reduced supplier confidence.
- Information Flow Disruptions: Lack of transparency in financial disclosures causing uncertainty for stakeholders.
- Goods Flow Disruptions: Financial instability leading to procurement restrictions, transportation bottlenecks, or export-import delays.

Impact-Based Risk Classification:
- Social Impact: Workforce reductions, salary freezes, or labor unrest due to financial constraints.
- Economic Impact: Cost-cutting measures, reduced CAPEX, or shifting financial priorities affecting supply chain resilience.
- Environmental Impact: Sustainability initiatives or compliance with green regulations being deprioritized due to financial strain.

Ensure the output follows the requested format exactly and starts with { for the news classification. Don t start the output by ```json, or additional commentary. give back the output like in the example starting with ' {"News Classification": '
"""


# Send a message to the model
convo.send_message(prompt)

# Print the response
print(convo.last.text)

