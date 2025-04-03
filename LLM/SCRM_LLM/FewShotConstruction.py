# Prompt.py
import sys
import os
import json
from SCRM_LLM.FewShotPromptingSetup import FSP_Similarity, FSP_Embedding


def load_few_shot_examples(json_path="Shots.json"):
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)

def construct_few_shot_prompt(input_text, few_shot_examples, top_n=3):
    relevant_examples = retrieve_relevant_examples(input_text, few_shot_examples, top_n)
    
    prompt = "Based on the following examples, analyze the input text and assess the supply chain risk:\n\n"
    
    for idx, example in enumerate(relevant_examples, 1):
        prompt += f"Example {idx}:\n"
        prompt += f"Input: {example['input']}\n"
        prompt += f"Output: {json.dumps(example['output'], indent=2)}\n\n"
    
    prompt += "Input for Assessment:\n"
    prompt += input_text + "\n\n"
    prompt += "Output:"
    
    return prompt

if __name__ == "__main__":
    # Load examples from JSON file
    few_shot_examples = load_few_shot_examples("Shots.json")

    # Define your input text
    input_text = "A powerful earthquake has struck central Japan, damaging multiple factories and affecting shipments of semiconductors and auto parts."
    
    # Generate the prompt
    prompt = construct_few_shot_prompt(input_text, few_shot_examples, top_n=3)
    
    print(prompt)
