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
        self._set_fixed_dims_from_checkpoint()
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

    def _set_fixed_dims_from_checkpoint(self):
        """Tetapkan semua dimensi persis sesuai checkpoint state_dict"""
        checkpoint = torch.load(self.checkpoint_path, map_location=self.device)
        state_dict = checkpoint["G_state_dict"]

        # embed_dim dari label_emb.weight
        self.embed_dim = state_dict["label_emb.weight"].shape[1]       # 32
        self.num_classes = state_dict["label_emb.weight"].shape[0]    # 2
        self.hidden_dim = state_dict["fc.weight"].shape[0]            # 256

        # latent_dim dari fc.weight
        self.latent_dim = state_dict["fc.weight"].shape[1] // self.embed_dim   # 160/32 = 5

        # latent_step_dim dari step_proj.weight
        self.latent_step_dim = state_dict["step_proj.weight"].shape[1] // self.embed_dim  # 64/32 = 2

        # token_dim dari to_token.weight
        self.token_dim = state_dict["to_token.weight"].shape[0]       # 400

        # seq_len bisa default
        self.seq_len = 105

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
