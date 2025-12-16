# ct_veegan/wrapper.py
import torch
from .models import LSTMGenerator
import os
import requests

GITHUB_MODEL_URL = "https://github.com/Benylaode/ct_veegans/releases/download/v0.1.1/ct_veegan_siap.pt"

class CTVeeGANWrapper:
    def __init__(self, device=None, checkpoint_path=None):
        self.device = device if device else ('cuda' if torch.cuda.is_available() else 'cpu')

        if checkpoint_path is None:
            checkpoint_path = os.path.join(os.path.dirname(__file__), "checkpoints", "ct_veegan_siap.pt")
        self.checkpoint_path = checkpoint_path

        self._ensure_checkpoint()
        self._set_fixed_dims()
        self.model = self._load_model()

    def _ensure_checkpoint(self):
        if os.path.exists(self.checkpoint_path):
            return

        os.makedirs(os.path.dirname(self.checkpoint_path), exist_ok=True)

        response = requests.get(GITHUB_MODEL_URL, stream=True)
        if response.status_code == 200:
            with open(self.checkpoint_path, "wb") as f:
                for c in response.iter_content(1024):
                    f.write(c)
        else:
            raise FileNotFoundError("Gagal mengunduh checkpoint dari GitHub.")

    def _set_fixed_dims(self):
        """Tetapkan dimensi sesuai checkpoint sebenarnya"""
        self.num_classes = 2            # label_emb.weight.shape[0]
        self.embed_dim = 32             # label_emb.weight.shape[1]
        self.hidden_dim = 256           # fc.weight.shape[0]
        self.latent_dim = 5             # fc.weight.shape[1] // embed_dim = 160 // 32
        self.latent_step_dim = 2        # step_proj.weight.shape[1] // embed_dim = 64 // 32
        self.token_dim = 400            # to_token.weight.shape[0]
        self.seq_len = 105              # bisa tetap default

    def _load_model(self):
        model = LSTMGenerator(
            latent_dim=self.latent_dim,
            latent_step_dim=self.latent_step_dim,
            num_classes=self.num_classes,
            embed_dim=self.embed_dim,
            seq_len=self.seq_len,
            token_dim=self.token_dim,
            hidden_dim=self.hidden_dim,
        ).to(self.device)

        checkpoint = torch.load(self.checkpoint_path, map_location=self.device)
        model.load_state_dict(checkpoint["G_state_dict"], strict=True)
        model.eval()
        return model
