# ct_veegan/wrapper.py
import torch
from .models import LSTMGenerator
import os
import requests
import numpy as np
from imblearn.combine import SMOTEENN
from sklearn.metrics.pairwise import cosine_similarity
import torch.nn as nn


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


    # -------------------------------------------------------------------------
    # 1) GENERATOR SEDERHANA
    # -------------------------------------------------------------------------
    def generate(self, batch_size=1, labels=None):
        z = torch.randn(batch_size, self.latent_dim, device=self.device)
        z_step = torch.randn(batch_size, self.seq_len, self.latent_step_dim, device=self.device)

        if labels is None:
            labels = torch.randint(0, self.num_classes, (batch_size,), device=self.device)
        elif isinstance(labels, list):
            labels = torch.tensor(labels, device=self.device)

        with torch.no_grad():
            return self.model(z, z_step, labels)


    # -------------------------------------------------------------------------
    # 2) GENERATE SEKUENS (method rapi)
    # -------------------------------------------------------------------------
    def generate_sequence(self, n_generate, label_class):
        z = torch.randn((n_generate, self.latent_dim), device=self.device)
        z_step = torch.randn((n_generate, self.seq_len, self.latent_step_dim), device=self.device)
        labels = torch.full((n_generate,), label_class, dtype=torch.long, device=self.device)

        with torch.no_grad():
            x = self.model(z, z_step, labels)

        return x.detach().cpu().numpy()


    # -------------------------------------------------------------------------
    # 3) KONVERSI TOKEN (cosine similarity → Word2Vec)
    # -------------------------------------------------------------------------
    def tokens_to_words_batch(self, generated_sequences, model_word2vec, shared_vocab, pad_threshold=1e-8):

        vocab_list = list(shared_vocab)
        vocab_vectors = np.array([model_word2vec.wv[w] for w in vocab_list])

        all_sentences = []
        for seq in generated_sequences:
            words = []

            for vec in seq:
                if np.all(np.abs(vec) < pad_threshold):
                    continue

                scores = cosine_similarity([vec], vocab_vectors)[0]
                best_word = vocab_list[int(np.argmax(scores))]
                words.append(best_word)

            all_sentences.append(" ".join(words))

        return all_sentences


    def balance(
        self,
        X_train,
        y_train,
        reconstructor,
        minor_class,
        noise_scale=0.05,
        pad_value=0.0,
    ):
        device = torch.device(self.device)

        X = torch.tensor(X_train, dtype=torch.float32, device=device)
        y = torch.tensor(y_train, dtype=torch.long, device=device)

        unique, counts = torch.unique(y, return_counts=True)
        class_counts = dict(zip(unique.cpu().numpy(), counts.cpu().numpy()))
        max_count = max(class_counts.values())
        minor_count = int(class_counts.get(minor_class, 0))

        need = max_count - minor_count
        if need <= 0:
            mask = (X != pad_value).any(-1).cpu().numpy()
            return X.cpu().numpy(), y.cpu().numpy(), mask

        seq_len = X.shape[1]
        token_dim = X.shape[2]


        X_flat = X.mean(dim=1).cpu().numpy()
        y_np = y.cpu().numpy()

        sm = SMOTEENN(sampling_strategy='not majority', random_state=42)
        X_res, y_res = sm.fit_resample(X_flat, y_np)

        minor_mask = (y_res == minor_class)
        X_minor = X_res[minor_mask]
        X_minor_seq = np.repeat(X_minor[:, None, :], seq_len, axis=1)

        X_minor_seq_t = torch.tensor(X_minor_seq, dtype=torch.float32, device=device)


        reconstructor.eval()
        self.model.eval()

        X_rec = X_minor_seq_t.reshape(X_minor_seq_t.size(0), -1)

        # Sesuaikan dimensi input reconstructor
        expected_dim = None
        for m in reconstructor.modules():
            if isinstance(m, nn.Linear):
                expected_dim = m.in_features
                break

        if expected_dim is None:
            expected_dim = X_rec.shape[1]

        if X_rec.shape[1] < expected_dim:
            pad = expected_dim - X_rec.shape[1]
            X_rec = torch.cat([X_rec, torch.zeros((X_rec.size(0), pad), device=device)], dim=1)
        elif X_rec.shape[1] > expected_dim:
            X_rec = X_rec[:, :expected_dim]

        with torch.no_grad():
            z_pool = reconstructor(X_rec)


        if z_pool.shape[0] >= need:
            idx = torch.randperm(z_pool.shape[0], device=device)[:need]
        else:
            idx = torch.randint(0, z_pool.shape[0], (need,), device=device)

        z = z_pool[idx] + noise_scale * torch.randn_like(z_pool[idx])

        # ---------------------------------------------------------------------
        # Latent-step noise
        # ---------------------------------------------------------------------
        z_step = torch.randn((need, seq_len, self.latent_step_dim), device=device)
        labels = torch.full((need,), minor_class, dtype=torch.long, device=device)

        # ---------------------------------------------------------------------
        # GENERATOR
        # ---------------------------------------------------------------------
        with torch.no_grad():
            X_fake = self.model(z, z_step, labels)

        # reshape jika perlu
        if X_fake.ndim == 2 and X_fake.shape[1] == seq_len * token_dim:
            X_fake = X_fake.reshape(need, seq_len, token_dim)

        # padding mengikuti minor class
        if minor_count > 0:
            X_minor_orig = X[y == minor_class][0]
            padmask = (X_minor_orig == pad_value).all(dim=1)
            if padmask.any():
                X_fake[:, padmask, :] = pad_value

        # ---------------------------------------------------------------------
        # Gabungkan hasil
        # ---------------------------------------------------------------------
        X_final = torch.cat([X, X_fake], dim=0).cpu().numpy()
        y_fake = np.full((need,), minor_class, dtype=y_train.dtype)
        y_final = np.concatenate([y_train, y_fake], axis=0)

        mask_final = (X_final != pad_value).any(axis=(1, 2)).astype(float)

        return X_final, y_final, mask_final
