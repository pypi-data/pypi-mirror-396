import torch
import torch.nn as nn
import torch.nn.functional as F
import math

class SimpleTokenizer:
    """
    A very simple character-level tokenizer for our 'from scratch' LLM.
    In a real scenario, you'd use Byte-Pair Encoding (BPE).
    """
    def __init__(self):
        self.char_to_idx = {}
        self.idx_to_char = {}
        # Basic ASCII + some common symbols
        chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 !\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~\n\t"
        for i, c in enumerate(chars):
            self.char_to_idx[c] = i + 1 # 0 is reserved for padding/unknown
            self.idx_to_char[i + 1] = c
        self.vocab_size = len(chars) + 1
        self.pad_token_id = 0

    def encode(self, text, max_len=128):
        indices = [self.char_to_idx.get(c, 0) for c in text]
        if len(indices) > max_len:
            indices = indices[:max_len]
        else:
            indices += [self.pad_token_id] * (max_len - len(indices))
        return torch.tensor(indices, dtype=torch.long)

    def decode(self, indices):
        return "".join([self.idx_to_char.get(idx.item(), "") for idx in indices if idx != 0])


class ImageEncoder(nn.Module):
    """
    A simple Convolutional Neural Network to extract features from 
    the failed test screenshot.
    """
    def __init__(self, embed_dim=256):
        super().__init__()
        # Input: (Batch, 3, 256, 256) -> Output: (Batch, embed_dim)
        self.conv1 = nn.Conv2d(3, 32, kernel_size=3, stride=2, padding=1)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, stride=2, padding=1)
        self.conv3 = nn.Conv2d(64, 128, kernel_size=3, stride=2, padding=1)
        self.flatten = nn.Flatten()
        # Mapping flattened visual features to the same dimension as text embeddings
        self.fc = nn.Linear(128 * 32 * 32, embed_dim) 

    def forward(self, x):
        x = F.relu(self.conv1(x))
        x = F.relu(self.conv2(x))
        x = F.relu(self.conv3(x))
        x = self.flatten(x)
        x = self.fc(x)
        return x # (Batch, embed_dim)


class SelfAttention(nn.Module):
    """
    Multi-head Self Attention mechanism.
    The core of the Transformer.
    """
    def __init__(self, embed_dim, num_heads):
        super().__init__()
        self.embed_dim = embed_dim
        self.num_heads = num_heads
        self.head_dim = embed_dim // num_heads

        assert (
            self.head_dim * num_heads == embed_dim
        ), "Embed dim must be divisible by num heads"

        self.q_proj = nn.Linear(embed_dim, embed_dim)
        self.k_proj = nn.Linear(embed_dim, embed_dim)
        self.v_proj = nn.Linear(embed_dim, embed_dim)
        self.out_proj = nn.Linear(embed_dim, embed_dim)

    def forward(self, x, mask=None):
        batch_size, seq_len, _ = x.shape
        
        # Linear projections
        q = self.q_proj(x).view(batch_size, seq_len, self.num_heads, self.head_dim).transpose(1, 2)
        k = self.k_proj(x).view(batch_size, seq_len, self.num_heads, self.head_dim).transpose(1, 2)
        v = self.v_proj(x).view(batch_size, seq_len, self.num_heads, self.head_dim).transpose(1, 2)

        # Scaled Dot-Product Attention
        scores = torch.matmul(q, k.transpose(-2, -1)) / math.sqrt(self.head_dim)
        
        if mask is not None:
             scores = scores.masked_fill(mask == 0, float('-inf'))

        attn_weights = F.softmax(scores, dim=-1)
        out = torch.matmul(attn_weights, v)
        
        # Combine heads
        out = out.transpose(1, 2).contiguous().view(batch_size, seq_len, self.embed_dim)
        return self.out_proj(out)


class TransformerBlock(nn.Module):
    def __init__(self, embed_dim, num_heads, ff_hidden_dim, dropout=0.1):
        super().__init__()
        self.attention = SelfAttention(embed_dim, num_heads)
        self.norm1 = nn.LayerNorm(embed_dim)
        self.dropout1 = nn.Dropout(dropout)
        
        self.ff = nn.Sequential(
            nn.Linear(embed_dim, ff_hidden_dim),
            nn.ReLU(),
            nn.Linear(ff_hidden_dim, embed_dim)
        )
        self.norm2 = nn.LayerNorm(embed_dim)
        self.dropout2 = nn.Dropout(dropout)

    def forward(self, x, mask=None):
        # Attention with Residual Connection & Norm
        attn_out = self.attention(x, mask)
        x = self.norm1(x + self.dropout1(attn_out))
        
        # Feed Forward with Residual Connection & Norm
        ff_out = self.ff(x)
        x = self.norm2(x + self.dropout2(ff_out))
        return x


class ScratchMultimodalLLM(nn.Module):
    """
    A custom Multimodal LLM built from scratch.
    It takes an image (screenshot) and text (error log/page source) 
    and predicts the next tokens (analysis).
    """
    def __init__(self, vocab_size, embed_dim=256, num_heads=4, num_layers=4, max_seq_len=512):
        super().__init__()
        self.embed_dim = embed_dim
        
        # Image Encoder
        self.image_encoder = ImageEncoder(embed_dim)
        
        # Text Embedding
        self.token_embedding = nn.Embedding(vocab_size, embed_dim)
        self.position_embedding = nn.Embedding(max_seq_len, embed_dim)
        
        # Transformer Decoder Layers
        self.layers = nn.ModuleList([
            TransformerBlock(embed_dim, num_heads, ff_hidden_dim=embed_dim*4)
            for _ in range(num_layers)
        ])
        
        # Final prediction head
        self.fc_out = nn.Linear(embed_dim, vocab_size)

    def forward(self, images, input_ids):
        """
        Args:
            images: (Batch, 3, 256, 256)
            input_ids: (Batch, Seq_Len)
        """
        batch_size, seq_len = input_ids.shape
        
        # 1. Encode Image
        # Image features become the first "token" in our sequence (Simplification)
        img_features = self.image_encoder(images) # (Batch, embed_dim)
        img_features = img_features.unsqueeze(1)  # (Batch, 1, embed_dim)
        
        # 2. Embed Text
        positions = torch.arange(0, seq_len).unsqueeze(0).to(input_ids.device)
        text_embeddings = self.token_embedding(input_ids) + self.position_embedding(positions)
        
        # 3. Concatenate (Multimodal Fusion)
        # We prepend image features to the text sequence
        x = torch.cat([img_features, text_embeddings], dim=1) # (Batch, 1 + Seq_Len, embed_dim)
        
        # 4. Pass through Transformer
        for layer in self.layers:
            x = layer(x) # We are omitting masking for simplicity of the 'scratch' demo
            
        # 5. Output Logits
        logits = self.fc_out(x)
        return logits

