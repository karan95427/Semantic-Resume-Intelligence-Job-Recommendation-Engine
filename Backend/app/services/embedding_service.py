import os

# Disable XET
os.environ["HF_HUB_DISABLE_XET"] = "1"

from sentence_transformers import SentenceTransformer

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "hf_cache")

model = SentenceTransformer(
    'all-MiniLM-L6-v2',
    cache_folder=MODEL_PATH
)

def generate_embedding(text: str):

    embedding = model.encode(text)

    return embedding.tolist()
