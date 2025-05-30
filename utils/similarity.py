from typing import List

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Initialize the model (this will be done once when the module is imported)
model = SentenceTransformer('all-MiniLM-L6-v2')


def compute_cosine_similarity(text1: str, text2: str) -> float:
  """
    Compute cosine similarity between two texts using sentence embeddings.
    
    Args:
        text1: First text
        text2: Second text
        
    Returns:
        Cosine similarity score between 0 and 1
    """
  # Generate sentence embeddings
  embedding1 = model.encode([text1])
  embedding2 = model.encode([text2])

  # Calculate cosine similarity
  similarity = cosine_similarity(embedding1, embedding2)

  return float(similarity[0][0])
