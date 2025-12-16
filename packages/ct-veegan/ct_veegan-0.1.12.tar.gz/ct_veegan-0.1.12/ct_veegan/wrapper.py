# ct_veegan/wrapper.py
import torch
from .models import LSTMGenerator
import os
import requests

GITHUB_MODEL_URL = "https://github.com/Benylaode/ct_veegans/releases/download/v0.1.1/ct_veegan_siap.pt"

class CTVeeGANWrapper:
    def __init__(
        self,
        device=None,
        checkpoint_path=None,
    ):
        self.device = device if device else ('cuda' if torch.cuda.is_available() else 'cpu')

        if checkpoint_path is None:
            checkpoint_path = os.path.join(os.path.dirname(__file__), "checkpoints", "ct_veegan_siap.pt")
        self.checkpoint_path = checkpoint_path

        self._ensure_checkpoint()
        self._load_checkpoint_dims()
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

    def _load_checkpoint_dims(self):
        """Baca dimensi dari checkpoint untuk memastikan kompatibilitas model"""
        checkpoint = torch.load(self.checkpoint_path, map_location=self.device)
        config = checkpoint.get("config", {})

        # fallback ke default jika config tidak ada
        self.latent_dim = config.get("latent_dim", 128)
        self.latent_step_dim = config.get("latent_step_dim", 128)
        self.seq_len = config.get("seq_len", 105)
        self.token_dim = config.get("token_dim", 400)
        self.num_classes = config.get("num_classes", 2)
        self.embed_dim = config.get("embed_dim", 32)
        self.hidden_dim = config.get("hidden_dim", 256)

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
        model.load_state_dict(checkpoint["G_state_dict"], strict=False)
        model.eval()

        return model
