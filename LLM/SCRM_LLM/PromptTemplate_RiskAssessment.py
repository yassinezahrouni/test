import json





# ---------- FEW SHOTS ----------

shot1 = {
        "input": "id: N3\nnews content:Hurricane Helene caused severe flooding and structural damage in Spruce Pine, North Carolina, a region known for its high-purity quartz mines. Mining operations were halted due to the storm’s impact.",
        "output": {
            "id": "N3",
            "event_type": "Environmental and Natural Risk",
            "location": "North Carolina, USA",
            "severity": "High",
            "potential_supply_chain_impact": [
                {
                    "risk_type": "Supply and Demand Risk",
                    "description": "Disruption of quartz mining operations may result in raw material shortages essential for semiconductor manufacturing."
                },
                {
                    "risk_type": "Logistics and Transportation Risk",
                    "description": "Flooded roads and damaged infrastructure can delay material transport and hinder recovery efforts."
                }
            ],
            "recommended_action": "Develop alternative sourcing strategies, invest in stockpiling critical raw materials, and reinforce infrastructure against severe weather events.",
            "rationale": "The shutdown of quartz mines due to flooding directly threatens semiconductor supply chains reliant on high-purity inputs. Resilience strategies are needed to prevent cascading disruptions."
        }
    }

shot2 = {
        "input": "id: N4\nnews content: Since July, widespread flooding has affected one-third of Thailand’s provinces, marking the worst in fifty years. The disaster has caused significant human and economic losses, especially in regions with concentrated industrial zones.",
        "output": {
            "id": "N4",
            "event_type": "Environmental and Natural Risk",
            "location": "Thailand",
            "severity": "High",
            "potential_supply_chain_impact": [
                {
                    "risk_type": "Operational and Labor Risk",
                    "description": "Flooded industrial parks may cause widespread production halts, particularly in electronics and automotive sectors."
                },
                {
                    "risk_type": "Logistics and Transportation Risk",
                    "description": "Severe damage to transportation infrastructure could delay deliveries and increase recovery time for affected supply routes."
                }
            ],
            "recommended_action": "Relocate critical operations out of high-risk flood zones, establish emergency logistics plans, and increase supplier diversification.",
            "rationale": "Flooding in industrial hubs severely affects production and transport. Diversification and mitigation strategies are crucial for maintaining supply chain stability during extreme weather events."
        }
    }

shot3 = {
        "input": "id: N5\nnews content: The Tohoku earthquake and tsunami struck the northeast coast of Japan, causing massive destruction to infrastructure, including roads, electricity networks, and ports.",
        "output": {
            "id": "N5",
            "event_type": "Environmental and Natural Risk",
            "location": "Japan, Tohoku Region",
            "severity": "High",
            "potential_supply_chain_impact": [
                {
                    "risk_type": "Logistics and Transportation Risk",
                    "description": "Severe disruptions in transportation networks can hinder the movement of goods and materials."
                },
                {
                    "risk_type": "Operational and Labor Risk",
                    "description": "Damage to infrastructure may lead to temporary closures of manufacturing facilities."
                },
                {
                    "risk_type": "Supply and Demand Risk",
                    "description": "Interruptions in production can reduce the availability of goods, affecting global trade."
                }
            ],
            "recommended_action": "Develop contingency sourcing plans, strengthen supply chain redundancy, and establish emergency logistics networks.",
            "rationale": "The earthquake and tsunami caused extensive infrastructure damage, which is critical for manufacturing and transportation. This damage can lead to operational halts and logistical challenges, thereby disrupting the supply chain. Implementing contingency plans and enhancing redundancy are essential to mitigate these risks."
        }
    }

shot4 = {
  "input": "id: N6\nnews content: A mild 3.0 earthquake occurred in a remote desert region in Western Australia, with no reported damage or disruption.",
  "output": {
    "id": "N6",
    "event_type": "Environmental and Natural Risk",
    "location": "Western Australia",
    "severity": "Low",
    "potential_supply_chain_impact": [],
    "recommended_action": "No immediate action required.",
    "rationale": "The earthquake occurred in a remote area without significant industrial or logistical infrastructure, and no damage was reported."
  }
}


# ---------- INPUT TO ASSESS ----------
input_to_assess = """id: N7\nnews content: A magnitude 4.9 earthquake shook central Tunisia on Monday, local authorities said. The quake hit at 10:45 a.m. local time (0945GMT) east of Meknassy in Sidi Bouzid province, Tunisia’s National Institute of Meteorology said. No injuries were recorded. Earthquakes are rarely reported in Tunisia. In April 2023, the North African country reported an earthquake measuring 4.9 magnitude in the southwestern Tozeur province, but no losses were recorded."""


# ---------- ROLE DEFINITION ----------
Role_description = (
  "You are a highly experienced Senior Supply Chain Manager with over 15 years of global experience "
  "across industries such as automotive, electronics, and consumer goods. You specialize in identifying, "
  "assessing, and mitigating risks in complex, international supply chains. You are skilled at analyzing "
  "real-time global events (such as natural disasters, geopolitical changes, labor strikes, and regulatory shifts) "
  "and understanding their downstream impact on logistics, inventory, production, and sourcing. You are also "
  "well-versed in risk modeling, contingency planning, and proactive mitigation strategies. Your recommendations "
  "are always pragmatic, data-driven, and aligned with business continuity and resilience best practices. "
  "You are adept at distinguishing between direct and indirect impacts, understand time sensitivity in disruption "
  "scenarios, and consider sourcing redundancy and supplier alternatives when making recommendations."
)

# ---------- TASK DESCRIPTION ----------
Task_description = "You will be given a news content describing a real-world event.\nYour job is to analyze the potential supply chain risks caused by this event. Follow these steps:\n\n"

# ---------- STEPS DESCRIPTION ----------
Steps = f"""
            1. Carefully read and understand the event described in the input.\n 
            2. Identify whether the event could affect the supply chain in any way, even indirectly. If it is unlikely to have any significant impact, clearly state so and assign a 'Low' severity.\n 
            3. If applicable, describe potential supply chain impacts across the following dimensions:\n   - Logistics and Transportation Risk\n   - Supply and Demand Risk\n   - Operational and Labor Risk\n   - Financial and Economic Risk\n   - Technological and System Risk\n   - Environmental and Natural Risk\n   - Political and Regulatory Risk 
            4. Justify each impact with logical reasoning based on the input.\n
            5. Evaluate the **severity** of the impact (Low / Medium / High).\n
            6. Recommend concrete mitigation actions.\n
            7. Provide a clear **rationale** for your risk assessment.\n\n"""

# ---------- OUTPUT FORMAT ----------
Output_format = """Your output should follow the same JSON structure as the few-shot examples with Output keys: 
                    - id (string)
                    - event_type (string)
                    - location (string)
                    - severity (Low | Medium | High)
                    - potential_supply_chain_impact (list of dicts with keys: risk_type, description)
                    - recommended_action (string)
                    - rationale (string)
                    """


# ---------- BUILD PROMPT ----------
prompt = f"""[INST] <<SYS>> {Role_description} <</SYS>>

{Task_description}
**Step-by-step reasoning**:
{Steps}

{Output_format}

Here are examples to follow:
### Example 1:
{json.dumps(shot1, indent=2)}
### Example 2:
{json.dumps(shot2, indent=2)}
### Example 3:
{json.dumps(shot3, indent=2)}

Now analyze the following input:
{json.dumps(input_to_assess, indent=2)}

Return your response as valid JSON.
[/INST]"""

# ---------- PRINT FINAL PROMPT ----------
print(prompt)
