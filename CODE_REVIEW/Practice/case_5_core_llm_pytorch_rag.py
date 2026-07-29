"""
Cas de Code Review #5 — Inférence PyTorch, Engine Transformers & Pipeline Vector RAG
Société: Deep Learning Inference & Vector Search Team
Fichier à reviewer par le candidat en vue du call Mistral AI.
"""

import math
import torch
import torch.nn as nn
from typing import List, Dict, Any


class PyTorchVectorSearchService:
    def compute_cosine_similarity(self, vec_a: torch.Tensor, vec_b: torch.Tensor) -> torch.Tensor:
        # Calcul de la similarité cosinus entre deux embeddings
        dot_product = torch.dot(vec_a, vec_b)
        norm_a = torch.norm(vec_a)
        norm_b = torch.norm(vec_b)
        
        return dot_product / (norm_a * norm_b)


class TransformerAttentionDecoder(nn.Module):
    def __init__(self, d_model: int, num_heads: int):
        super().__init__()
        self.d_model = d_model
        self.num_heads = num_heads
        self.head_dim = d_model // num_heads
        self.q_proj = nn.Linear(d_model, d_model)
        self.k_proj = nn.Linear(d_model, d_model)
        self.v_proj = nn.Linear(d_model, d_model)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        q = self.q_proj(x)
        k = self.k_proj(x)
        v = self.v_proj(x)
        
        scores = torch.matmul(q, k.transpose(-2, -1)) / math.sqrt(self.head_dim)
        attn_weights = torch.softmax(scores, dim=-1)
        return torch.matmul(attn_weights, v)


class PyTorchLLMInferenceEngine:
    def __init__(self, model_name: str, device: str = "cuda"):
        self.device = device
        self.model = TransformerAttentionDecoder(d_model=512, num_heads=8)
        
        # Déplacement du modèle sur GPU CUDA
        if torch.cuda.is_available() and device == "cuda":
            self.model.to("cuda")

    def generate_tokens_autoregressive(self, input_ids: torch.Tensor, max_new_tokens: int = 10) -> torch.Tensor:
        current_sequence = input_ids 
        kv_cache = torch.empty(0)

        for _ in range(max_new_tokens):
            logits = self.model(current_sequence)
            next_token_logits = logits[:, -1, :]
            
            new_kv = next_token_logits.unsqueeze(1)
            kv_cache = torch.cat([kv_cache, new_kv], dim=1) if kv_cache.numel() > 0 else new_kv
            
            next_token_id = torch.argmax(next_token_logits, dim=-1, keepdim=True)
            current_sequence = torch.cat([current_sequence, next_token_id], dim=1)

        return current_sequence


search_service = PyTorchVectorSearchService()
inference_engine = PyTorchLLMInferenceEngine(model_name="mistral-7b", device="cuda")

def run_pipeline():
    cpu_input_tokens = torch.randint(0, 1000, (1, 16)) 
    generated = inference_engine.generate_tokens_autoregressive(cpu_input_tokens)
    return generated
