import torch
import torch.nn as nn

class LSTMGenerator(nn.Module):
    def __init__(self, latent_dim, latent_step_dim, num_classes, embed_dim, seq_len, token_dim, hidden_dim):
        super().__init__()
        self.seq_len = seq_len
        self.token_dim = token_dim
        self.label_emb = nn.Embedding(num_classes, embed_dim)
        self.fc = nn.Linear(latent_dim + embed_dim, hidden_dim)
        self.step_proj = nn.Linear(latent_step_dim + embed_dim, hidden_dim)
        self.lstm = nn.LSTM(input_size=hidden_dim, hidden_size=hidden_dim, num_layers=1, batch_first=True)
        self.to_token = nn.Linear(hidden_dim, token_dim)

    def forward(self, z, z_step, labels):
        c = self.label_emb(labels)
        init = torch.cat([z, c], dim=1)
        h0 = torch.tanh(self.fc(init)).unsqueeze(0)
        c0 = torch.zeros_like(h0, device=h0.device)
        c_rep = c.unsqueeze(1).repeat(1, self.seq_len, 1)
        step_input = torch.cat([z_step, c_rep], dim=2)
        lstm_input = self.step_proj(step_input)
        out, _ = self.lstm(lstm_input, (h0, c0))
        tokens = self.to_token(out)
        return tokens

class LSTMDiscriminator(nn.Module):
    def __init__(self, num_classes, embed_dim, seq_len, token_dim, hidden_dim):
        super().__init__()
        self.label_emb = nn.Embedding(num_classes, embed_dim)
        self.label_fc = nn.Linear(embed_dim, seq_len * token_dim)
        self.lstm = nn.LSTM(input_size=token_dim*2, hidden_size=hidden_dim, num_layers=1, batch_first=True)
        self.critic_fc = nn.Linear(hidden_dim, 1)
        self.cls_fc = nn.Linear(hidden_dim, num_classes)

    def forward(self, x, labels):
        c = self.label_emb(labels)
        c_map = self.label_fc(c).view(x.size(0), x.size(1), x.size(2))
        x_cond = torch.cat([x, c_map], dim=2)
        _, (h_last, _) = self.lstm(x_cond)
        h = h_last.squeeze(0)
        score = self.critic_fc(h)
        class_logits = self.cls_fc(h)
        return score, class_logits

class LSTMReconstructor(nn.Module):
    def __init__(self, seq_len, token_dim, latent_dim, hidden_dim):
        super().__init__()
        input_size = seq_len * token_dim
        self.net = nn.Sequential(
            nn.Linear(input_size, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Linear(hidden_dim // 2, latent_dim)
        )

    def forward(self, x):
        x_flat = x.reshape(x.size(0), -1)
        return self.net(x_flat)

class JointDisc(nn.Module):
    def __init__(self, seq_len, token_dim, latent_dim, hidden_dim):
        super().__init__()
        self.x_dim = seq_len * token_dim
        self.latent_dim = latent_dim
        self.net = nn.Sequential(
            nn.Linear(self.x_dim + latent_dim, hidden_dim),
            nn.LeakyReLU(0.2),
            nn.Dropout(0.3),
            nn.Linear(hidden_dim, hidden_dim//2),
            nn.LeakyReLU(0.2),
            nn.Dropout(0.3),
            nn.Linear(hidden_dim//2, 1)
        )

    def forward(self, z, x):
        x_flat = x.reshape(x.size(0), -1)
        inp = torch.cat([z, x_flat], dim=1)
        return self.net(inp).squeeze(1)
