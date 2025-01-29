import json
import re

def update_json_file(file_path):
    """Update the JSON file by modifying entries with empty language fields."""
    with open(file_path, 'r', encoding='utf-8') as file:
        newspapers = json.load(file)
    
    for newspaper in newspapers:
        if not newspaper.get("language"):
            region = newspaper.get("region", "")
            state = newspaper.get("state", "")
            
            # Extract state value from region (e.g., "Missouri [MO] (129)")
            match = re.search(r"([^\[\(]+)", region)  # Extract part before "[" or "("
            if match:
                extracted_state = match.group(1).strip()
                newspaper["language"] = state
                newspaper["state"] = extracted_state
                newspaper["region"] = "United States"
    
    # Save the updated JSON back to the same file
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(newspapers, file, indent=4, ensure_ascii=False)
    print(f"JSON file updated successfully: {file_path}")

# Example usage
if __name__ == "__main__":
    file_path = "newspapers_websitelinks.json"  # Path to your JSON file
    update_json_file(file_path)
