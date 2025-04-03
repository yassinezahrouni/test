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
model = genai.GenerativeModel(model_name="gemini-2.5-pro-exp-03-25", generation_config=generation_config)

# Start a chat session
convo = model.start_chat(history=[])

prompt = """ 
You are a supply chain news classification assistant.

You will be given:
- A news article
- A list of suppliers and shipments

Your task is to follow three reasoning steps and return a structured JSON output:

---

Step 1: Determine if the news article is **supply chain relevant**.  
Classify it as "Relevant" if the article includes or implies anything that could affect supply chains, including:
- Production, logistics, trade, regulations, raw materials, or demand
- Natural disasters, strikes, war, infrastructure issues, port closures, new laws, or geopolitical changes
Even weak or indirect signals should be considered relevant.

---

Step 2: If the article is relevant, identify the **risk dimensions**, such as:
- Location disruption
- Transport route disruption
- Industry-specific or material impact
- Regulatory or economic impact

Use this to reason about what might be impacted in the supply chain.

---

Step 3: From the provided supplier and shipment list, identify any that could be impacted.
- Match **suppliers** by location (city or country), industry, or product category mentioned in the article.
- Match **shipments** if their origin, destination, or route overlaps with impacted regions or routes mentioned in the article.

---

Return a JSON in the following format:

If relevant:
{
  "news_id": 250,
  "classification": "Relevant",
  "impacted_suppliers": [
    {"id": "S001", "reason": "Located in Kaohsiung, which is affected by port disruption."}
  ],
  "impacted_shipments": [
    {"id": "SHP123", "reason": "Departs from Kaohsiung, which is mentioned in the news."}
  ]
}

If not relevant:
{
  "news_id": 250,
  "classification": "Not relevant"
}

---

News Article:
"[INSERT ARTICLE TEXT HERE]"

Supplier and Shipment Data:
[INSERT SUPPLIER & SHIPMENT JSON HERE]

Now perform the analysis and return your output in the specified JSON format only.

 """


# Send a message to the model
convo.send_message(prompt)

# Print the response
print(convo.last.text)

