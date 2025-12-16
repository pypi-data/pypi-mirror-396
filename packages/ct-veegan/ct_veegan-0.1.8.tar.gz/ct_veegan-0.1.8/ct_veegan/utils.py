import torch
import torch.nn.functional as F
from torch import autograd
import numpy as np
from collections import defaultdict
import random
from imblearn.combine import SMOTEENN
from sklearn.metrics.pairwise import cosine_similarity

def gradient_penalty(critic, real, fake, labels):
    alpha = torch.rand(real.size(0), 1, 1, device=real.device).expand_as(real)
    interpolates = (alpha * real + (1 - alpha) * fake).requires_grad_(True)
    with torch.backends.cudnn.flags(enabled=False):
        d_interpolates, _ = critic(interpolates, labels)
    fake_out = torch.ones(d_interpolates.size(), device=real.device)
    grads = autograd.grad(
        outputs=d_interpolates,
        inputs=interpolates,
        grad_outputs=fake_out,
        create_graph=True,
        retain_graph=True,
        only_inputs=True
    )[0]
    grads = grads.reshape(grads.size(0), -1)
    gp = ((grads.norm(2, dim=1) - 1) ** 2).mean()
    return gp

def gradient_penalty_joint(D_zx, x_real, x_fake, z_fake, z_real):
    batch_size = x_real.size(0)
    alpha_x = torch.rand(batch_size, 1, 1, device=x_real.device)
    alpha_z = torch.rand(batch_size, 1, device=z_fake.device)
    interpolated_x = (alpha_x * x_real + (1 - alpha_x) * x_fake).requires_grad_(True)
    interpolated_z = (alpha_z * z_real + (1 - alpha_z) * z_fake).requires_grad_(True)
    d_interpolates = D_zx(interpolated_z, interpolated_x)
    fake_out = torch.ones_like(d_interpolates, device=x_real.device)
    grads = torch.autograd.grad(
        outputs=d_interpolates,
        inputs=[interpolated_x, interpolated_z],
        grad_outputs=fake_out,
        create_graph=True,
        retain_graph=True,
        only_inputs=True
    )
    grad_x, grad_z = grads
    grad_x = grad_x.reshape(batch_size, -1)
    grad_z = grad_z.reshape(batch_size, -1)
    grad_norm = torch.sqrt(torch.sum(grad_x**2, dim=1) + torch.sum(grad_z**2, dim=1) + 1e-12)
    gp = ((grad_norm - 1) ** 2).mean()
    return gp

def pad_vector_sequences(seqs, maxlen, token_dim):
    N = len(seqs)
    out = np.zeros((N, maxlen, token_dim), dtype=np.float32)
    lengths = np.zeros(N, dtype=np.int64)
    for i, s in enumerate(seqs):
        L = min(len(s), maxlen)
        out[i, :L] = s[:L]
        lengths[i] = L
    return out, lengths

def build_label_index_map(label_tensor, lengths_tensor=None):
    label_to_idx = defaultdict(list)
    labels_cpu = label_tensor.cpu().numpy()
    for i, lab in enumerate(labels_cpu):
        label_to_idx[int(lab)].append(i)
    return label_to_idx

def sample_real_by_labels(data_tensor, label_tensor, gen_y, lengths_tensor=None, label_to_idx=None, device='cpu'):
    if label_to_idx is None:
        label_to_idx = build_label_index_map(label_tensor, lengths_tensor)
    batch_real, batch_lab, batch_len = [], [], []
    for lab in gen_y.cpu().tolist():
        idx_list = label_to_idx.get(int(lab), None)
        if not idx_list:
            idx = random.randrange(0, data_tensor.size(0))
        else:
            idx = random.choice(idx_list)
        batch_real.append(data_tensor[idx].cpu().numpy())
        batch_lab.append(int(lab))
        if lengths_tensor is not None:
            batch_len.append(int(lengths_tensor[idx].cpu().item()))
        else:
            batch_len.append(data_tensor.size(1))
    real_x = torch.tensor(np.stack(batch_real), dtype=torch.float32, device=device)
    real_y = torch.tensor(batch_lab, dtype=torch.long, device=device)
    real_lengths = torch.tensor(batch_len, dtype=torch.long, device=device)
    return real_x, real_y, real_lengths


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
