# FSP_Similarity.py
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from FSP_Embedding import compute_embedding

def retrieve_similar_examples(input_embedding, example_embeddings, top_n=3):
    similarities = cosine_similarity([input_embedding], example_embeddings)
    top_indices = np.argsort(similarities[0])[::-1][:top_n]
    return top_indices

def retrieve_relevant_examples(input_text, few_shot_examples, top_n=3):
    input_embedding = compute_embedding(input_text)
    example_embeddings = [compute_embedding(ex['input']) for ex in few_shot_examples]
    top_indices = retrieve_similar_examples(input_embedding, example_embeddings, top_n)
    return [few_shot_examples[i] for i in top_indices]
