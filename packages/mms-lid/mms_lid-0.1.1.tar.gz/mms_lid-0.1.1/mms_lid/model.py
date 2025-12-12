# omni_lid/model.py
import torch
import torch.nn as nn
from transformers import Wav2Vec2Model
from .config import MODEL_ID

class OmniLIDModel(nn.Module):
    def __init__(self, num_langs):
        super().__init__()
        # Backbone 로드
        self.encoder = Wav2Vec2Model.from_pretrained(MODEL_ID)
        
        # Classification Head
        # Class 개수 = 언어 수 + silence(1)
        self.num_classes = num_langs + 1
        self.lid_head = nn.Linear(self.encoder.config.hidden_size, self.num_classes)

    def forward(self, x):
        # Inference 모드에서는 gradient 불필요
        features = self.encoder(x).last_hidden_state
        logits = self.lid_head(features)
        return logits