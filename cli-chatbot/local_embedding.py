import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List,Union
import torch
from __init__ import embed_model_name

class LocalEmbeddingEngine:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LocalEmbeddingEngine, cls).__new__(cls)
            
            cls._instance.model_name = embed_model_name
            
            if torch.cuda.is_available():
                cls._instance.device = "cuda"
            elif torch.backends.mps.is_available():
                cls._instance.device = "mps"
            else:
                cls._instance.device = "cpu"

            print(f"Initializing {cls._instance.model_name} on {cls._instance.device}...")
            cls._instance.model = SentenceTransformer(cls._instance.model_name, device=cls._instance.device)

        return cls._instance
    
    def create_embedding(self, texts:Union[str, List[str]], batch_size:int =32)-> np.ndarray:
        
        if isinstance(texts, str):
            texts = [texts]

        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=False,
            convert_to_numpy=True,
            normalize_embeddings=True
        )

        return embeddings
    
if __name__ == "__main__":
    engine = LocalEmbeddingEngine()

    data_to_embed = []

    vectors = engine.create_embedding(data_to_embed)