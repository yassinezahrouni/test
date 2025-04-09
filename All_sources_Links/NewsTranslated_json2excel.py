import pandas as pd
import os
from transformers import MarianMTModel, MarianTokenizer
from langdetect import detect, DetectorFactory

# Ensure reproducible language detection
DetectorFactory.seed = 0

# ---------------------------
# Define a mapping for source languages to their MarianMT model (for translation to English)
# Extended mapping of 20 languages (source language codes) to their corresponding MarianMT model checkpoints for translating to English.
translation_models = {
    "de": "Helsinki-NLP/opus-mt-de-en",  # German → English
    "fr": "Helsinki-NLP/opus-mt-fr-en",  # French → English
    "es": "Helsinki-NLP/opus-mt-es-en",  # Spanish → English
    "it": "Helsinki-NLP/opus-mt-it-en",  # Italian → English
    "nl": "Helsinki-NLP/opus-mt-nl-en",  # Dutch → English
    "ru": "Helsinki-NLP/opus-mt-ru-en",  # Russian → English
    "ja": "Helsinki-NLP/opus-mt-ja-en",  # Japanese → English
    "zh": "Helsinki-NLP/opus-mt-zh-en",  # Chinese (Simplified) → English
    "ko": "Helsinki-NLP/opus-mt-ko-en",  # Korean → English
    "pt": "Helsinki-NLP/opus-mt-pt-en",  # Portuguese → English
    "sv": "Helsinki-NLP/opus-mt-sv-en",  # Swedish → English
    "da": "Helsinki-NLP/opus-mt-da-en",  # Danish → English
    "no": "Helsinki-NLP/opus-mt-no-en",  # Norwegian → English
    "fi": "Helsinki-NLP/opus-mt-fi-en",  # Finnish → English
    "pl": "Helsinki-NLP/opus-mt-pl-en",  # Polish → English
    "cs": "Helsinki-NLP/opus-mt-cs-en",  # Czech → English
    "ro": "Helsinki-NLP/opus-mt-ro-en",  # Romanian → English
    "tr": "Helsinki-NLP/opus-mt-tr-en",  # Turkish → English
    "ar": "Helsinki-NLP/opus-mt-ar-en",  # Arabic → English
    "hi": "Helsinki-NLP/opus-mt-hi-en"   # Hindi → English
}


# Preload the models/tokenizers into a cache for efficiency.
model_cache = {}
for lang, model_name in translation_models.items():
    tokenizer = MarianTokenizer.from_pretrained(model_name)
    model = MarianMTModel.from_pretrained(model_name)
    model_cache[lang] = (tokenizer, model)

def translate_to_english(text):
    """
    Detects the language of the text. If it is not English,
    translates it to English using the appropriate MarianMT model.
    If no model is available for the detected language or text is empty,
    returns the original text.
    """
    if not isinstance(text, str) or text.strip() == "":
        return text
    try:
        detected_lang = detect(text)
    except Exception as e:
        # If detection fails, return original text.
        return text
    if detected_lang == "en":
        return text
    if detected_lang in model_cache:
        tokenizer, model = model_cache[detected_lang]
        batch = tokenizer([text], return_tensors="pt", truncation=True, max_length=512)
        gen = model.generate(**batch)
        english_text = tokenizer.decode(gen[0], skip_special_tokens=True)
        return english_text
    else:
        # If no model is available for the detected language, return original text.
        return text

# ---------------------------
# Read JSON file into DataFrame, remove duplicates, add newsID column, and translate text
# ---------------------------
json_path = "All_sources_Links/Pool_NewsData.json"

df = pd.read_json(json_path)
df = df.drop_duplicates()

# Add newsID column: number rows from N1, N2, ...
df.reset_index(drop=True, inplace=True)
df['newsID'] = ["N" + str(i+1) for i in range(len(df))]

# Optional: Reorder columns so that "newsID" comes first.
cols = df.columns.tolist()
cols = ['newsID'] + [col for col in cols if col != 'newsID']
df = df[cols]

# Apply translation to all object (string) columns.
for col in df.columns:
    if df[col].dtype == object:
        df[col] = df[col].apply(translate_to_english)

# Construct output Excel file path (same folder, same base name with .xlsx extension)
output_path = os.path.splitext(json_path)[0] + ".xlsx"
df.to_excel(output_path, index=False)

print("Excel file saved at:", output_path)
