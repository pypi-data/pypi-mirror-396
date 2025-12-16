import torch
import torch.nn.functional as F
from torch import autograd
import numpy as np
from collections import defaultdict
import random

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
