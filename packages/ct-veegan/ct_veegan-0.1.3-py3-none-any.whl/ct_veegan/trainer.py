import os
import torch
import torch.nn as nn
import torch.optim as optim
from tqdm import tqdm
from .models import LSTMGenerator, LSTMDiscriminator, LSTMReconstructor, JointDisc
from .utils import gradient_penalty, gradient_penalty_joint

class Trainer:
    def __init__(self,
                 generator: LSTMGenerator,
                 discriminator: LSTMDiscriminator,
                 reconstructor: LSTMReconstructor = None,
                 joint_disc: JointDisc = None,
                 device='cpu',
                 lr_g=1e-4,
                 lr_d=1e-4,
                 gp_weight=10.0,
                 save_dir='checkpoints',
                 checkpoint_every=5,
                 early_stopping_patience=10):
        self.device = device
        self.G = generator.to(device)
        self.D = discriminator.to(device)
        self.F = reconstructor.to(device) if reconstructor else None
        self.D_zx = joint_disc.to(device) if joint_disc else None
        self.gp_weight = gp_weight
        self.save_dir = save_dir
        os.makedirs(save_dir, exist_ok=True)
        self.checkpoint_every = checkpoint_every
        self.early_stopping_patience = early_stopping_patience

        self.opt_g = optim.Adam(self.G.parameters(), lr=lr_g, betas=(0.5, 0.999))
        self.opt_d = optim.Adam(self.D.parameters(), lr=lr_d, betas=(0.5, 0.999))
        self.criterion_cls = nn.CrossEntropyLoss()
        
        self.scheduler_g = None
        self.scheduler_d = None

    def set_scheduler(self, scheduler_g=None, scheduler_d=None):
        """Set optional LR schedulers"""
        self.scheduler_g = scheduler_g
        self.scheduler_d = scheduler_d

    def save_checkpoint(self, epoch, g_loss, d_loss):
        path = os.path.join(self.save_dir, f'checkpoint_epoch_{epoch}.pt')
        state = {
            'epoch': epoch,
            'G_state_dict': self.G.state_dict(),
            'D_state_dict': self.D.state_dict(),
            'opt_g_state_dict': self.opt_g.state_dict(),
            'opt_d_state_dict': self.opt_d.state_dict(),
            'g_loss': g_loss,
            'd_loss': d_loss
        }
        if self.F:
            state['F_state_dict'] = self.F.state_dict()
        if self.D_zx:
            state['D_zx_state_dict'] = self.D_zx.state_dict()
        torch.save(state, path)
        print(f"Checkpoint saved at {path}")

    def train(self, dataloader, epochs=50, transfer_learning=False, freeze_layers=False):
        """
        Main training loop for conditional GAN.
        - dataloader: yields (x_real, y_labels) batches
        - transfer_learning: load pretrained weights
        - freeze_layers: freeze all but last layers
        """
        if transfer_learning:
            print("Transfer learning mode activated. Freeze layers:", freeze_layers)
            if freeze_layers:
                for name, param in self.G.named_parameters():
                    param.requires_grad = False
                if hasattr(self.G, 'to_token'):
                    for param in self.G.to_token.parameters():
                        param.requires_grad = True
                print("Frozen generator layers except output.")

        best_g_loss = float('inf')
        patience_counter = 0

        for epoch in range(epochs):
            g_losses, d_losses = [], []
            pbar = tqdm(dataloader, desc=f"Epoch {epoch+1}/{epochs}")
            for x_real, y_labels in pbar:
                x_real = x_real.to(self.device)
                y_labels = y_labels.to(self.device)
                batch_size = x_real.size(0)

                # latent vector
                latent_dim = self.G.fc.in_features - self.G.label_emb.embedding_dim
                z = torch.randn(batch_size, latent_dim, device=self.device)
                z_step = torch.randn(batch_size, self.G.seq_len, self.G.step_proj.in_features - self.G.label_emb.embedding_dim, device=self.device)

                # -------------------
                # Train Discriminator
                # -------------------
                self.D.zero_grad()
                x_fake = self.G(z, z_step, y_labels).detach()
                real_score, _ = self.D(x_real, y_labels)
                fake_score, _ = self.D(x_fake, y_labels)
                gp = gradient_penalty(self.D, x_real, x_fake, y_labels)
                d_loss = fake_score.mean() - real_score.mean() + self.gp_weight * gp
                d_loss.backward()
                self.opt_d.step()

                # -------------------
                # Train Generator
                # -------------------
                self.G.zero_grad()
                gen_x = self.G(z, z_step, y_labels)
                gen_score, _ = self.D(gen_x, y_labels)
                g_loss = -gen_score.mean()
                g_loss.backward()
                self.opt_g.step()

                g_losses.append(g_loss.item())
                d_losses.append(d_loss.item())

                pbar.set_postfix({
                    "D_loss": d_loss.item(),
                    "G_loss": g_loss.item()
                })

            # Scheduler step
            if self.scheduler_g:
                self.scheduler_g.step()
            if self.scheduler_d:
                self.scheduler_d.step()

            avg_g_loss = sum(g_losses)/len(g_losses)
            avg_d_loss = sum(d_losses)/len(d_losses)
            print(f"Epoch {epoch+1} finished → Avg G_loss: {avg_g_loss:.4f}, D_loss: {avg_d_loss:.4f}")

            # Early stopping
            if avg_g_loss < best_g_loss:
                best_g_loss = avg_g_loss
                patience_counter = 0
            else:
                patience_counter += 1
                if patience_counter >= self.early_stopping_patience:
                    print("Early stopping triggered.")
                    break

            # Save checkpoint
            if (epoch+1) % self.checkpoint_every == 0:
                self.save_checkpoint(epoch+1, avg_g_loss, avg_d_loss)
        
        print("Training completed.")
        return self.G, self.D
