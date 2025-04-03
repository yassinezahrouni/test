# Pseudocode for retrieving high-quality few-shot examples 

def retrieve_few_shots(input_text, example_db, max_shots=3):

    def predict_category(text):
        # Basic rule-based category prediction. Will be updated to use another LLM for the classification
        text = text.lower()
        if any(keyword in text for keyword in ["flood", "earthquake", "hurricane", "storm", "tsunami"]):
            return "Environmental and Natural Risk"
        if "strike" in text or "labor" in text:
            return "Operational and Labor Risk"
        if "regulation" in text or "sanction" in text:
            return "Political and Regulatory Risk"
        if "cyber" in text or "system failure" in text:
            return "Technological and System Risk"
        return "Unknown"

    def extract_metadata(example):
        """Extract simple metadata used for diversity scoring."""
        return {
            "cause": predict_event_cause(example["input"]),
            "severity": example["output"].get("severity", ""),
            "region": extract_region(example["output"].get("location", ""))
        }

    def predict_event_cause(text):
        """Heuristic cause classification from input text."""
        text = text.lower()
        if "flood" in text: return "flood"
        if "earthquake" in text: return "earthquake"
        if "hurricane" in text: return "hurricane"
        if "strike" in text: return "strike"
        if "collision" in text: return "collision"
        if "tsunami" in text: return "tsunami"
        return "other"

    def score_diversity(examples):
        """Score examples based on diversity in cause, severity, and region."""
        seen_causes, seen_severities, seen_regions = set(), set(), set()
        scored = []
        for ex in examples:
            meta = extract_metadata(ex)
            score = 0
            if meta["cause"] not in seen_causes:
                score += 1
                seen_causes.add(meta["cause"])
            if meta["severity"] not in seen_severities:
                score += 1
                seen_severities.add(meta["severity"])
            if meta["region"] not in seen_regions:
                score += 1
                seen_regions.add(meta["region"])
            scored.append((score, ex))
        # Sort by score descending
        scored.sort(key=lambda x: -x[0])
        return [ex for _, ex in scored]

    # Step 1: Predict category from input
    category = predict_category(input_text)

    # Step 2: Filter examples in same category
    filtered = [
        ex for ex in example_db
        if predict_category(ex["input"]) == category
    ]

    # Step 3: Score for diversity and select top
    diverse_examples = score_diversity(filtered)
    selected_examples = diverse_examples[:max_shots]

    return selected_examples


# Step 1: Load the example database from JSON file
with open("LLM/SCRM_LLM/FewShotPromptingSetup/Shots.json", "r", encoding="utf-8") as f:
    example_db = json.load(f)

# Step 2: Define your input text
input_to_assess = """id: N7\nnews content: A magnitude 4.9 earthquake shook central Tunisia on Monday, local authorities said. The quake hit at 10:45 a.m. local time (0945GMT) east of Meknassy in Sidi Bouzid province, Tunisia’s National Institute of Meteorology said. No injuries were recorded. Earthquakes are rarely reported in Tunisia. In April 2023, the North African country reported an earthquake measuring 4.9 magnitude in the southwestern Tozeur province, but no losses were recorded."""

# Step 3: Call the retrieval function
retrieved_shots = retrieve_few_shots(input_text=input_to_assess, example_db=example_db, max_shots=3)

# Step 4: Assign to shot1, shot2, shot3 variables
shot1 = retrieved_shots[0] if len(retrieved_shots) > 0 else None
shot2 = retrieved_shots[1] if len(retrieved_shots) > 1 else None
shot3 = retrieved_shots[2] if len(retrieved_shots) > 2 else None