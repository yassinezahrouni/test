import json

def add_slash_to_links(file_path):
    """Ensure '/' after 'https://onlinenewspapers.com' in the link field."""
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    for entry in data:
        link = entry.get("link", "")
        # Ensure the link starts with the correct base and check for the slash
        if link.startswith("https://onlinenewspapers.com") and not link.startswith("https://onlinenewspapers.com/"):
            entry["link"] = link.replace("https://onlinenewspapers.com", "https://onlinenewspapers.com/")
    
    # Save the updated JSON back to the same file
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)
    print(f"Updated links in JSON file: {file_path}")

# Example usage
if __name__ == "__main__":
    file_path = "onlinenewspapers_countries_links.json"  # Path to your JSON file
    add_slash_to_links(file_path)

