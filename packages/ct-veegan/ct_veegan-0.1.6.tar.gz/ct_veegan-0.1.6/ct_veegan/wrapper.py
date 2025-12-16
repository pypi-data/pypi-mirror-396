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
        latent_dim=128,
        latent_step_dim=128,
        seq_len=105,
        token_dim=400,
        num_classes=2,
        embed_dim=256,
        hidden_dim=256
    ):

        self.device = device if device else ('cuda' if torch.cuda.is_available() else 'cpu')
        self.latent_dim = latent_dim
        self.latent_step_dim = latent_step_dim
        self.seq_len = seq_len
        self.token_dim = token_dim
        self.num_classes = num_classes
        self.embed_dim = embed_dim
        self.hidden_dim = hidden_dim

        if checkpoint_path is None:
            checkpoint_path = os.path.join(os.path.dirname(__file__), "checkpoints", "ct_veegan_siap.pt")
        self.checkpoint_path = checkpoint_path

        self._ensure_checkpoint()

        self.model = self._load_model()


    def _ensure_checkpoint(self):
        """Download checkpoint jika tidak ada."""
        if os.path.exists(self.checkpoint_path):
            return

        print("⏳ Checkpoint tidak ditemukan. Mengunduh dari GitHub...")
        os.makedirs(os.path.dirname(self.checkpoint_path), exist_ok=True)

        response = requests.get(GITHUB_MODEL_URL, stream=True)
        if response.status_code == 200:
            with open(self.checkpoint_path, "wb") as f:
                for c in response.iter_content(1024):
                    f.write(c)
            print("✅ Checkpoint berhasil diunduh!")

        else:
            raise FileNotFoundError("Gagal mengunduh checkpoint dari GitHub.")


    def _load_model(self):
        """Load model + adjust strict=False + check dimension mismatch"""
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

        missing, unexpected = model.load_state_dict(checkpoint["G_state_dict"], strict=False)

        if missing or unexpected:
            print("⚠ WARNING: Ada parameter yang tidak cocok saat load checkpoint.")
            print("Missing keys:", missing)
            print("Unexpected keys:", unexpected)

        model.eval()
        return model


    def generate(self, batch_size=1, labels=None):
        z = torch.randn(batch_size, self.latent_dim, device=self.device)
        z_step = torch.randn(batch_size, self.seq_len, self.latent_step_dim, device=self.device)

        if labels is None:
            labels = torch.randint(0, self.num_classes, (batch_size,), device=self.device)
        elif isinstance(labels, list):
            labels = torch.tensor(labels, device=self.device)

        with torch.no_grad():
            return self.model(z, z_step, labels)
