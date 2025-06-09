import torch
import torch.nn as nn
import os
import cv2
import numpy as np
from torch.utils.data import Dataset

class CRNN(nn.Module):
    def __init__(self, imgH, nc, nclass, nh):
        super(CRNN, self).__init__()
        self.cnn = nn.Sequential(
            nn.Conv2d(nc, 64, 3, 1, 1), nn.ReLU(), nn.MaxPool2d(2, 2),
            nn.Conv2d(64, 128, 3, 1, 1), nn.ReLU(), nn.MaxPool2d(2, 2),
            nn.Conv2d(128, 256, 3, 1, 1), nn.ReLU(),
            nn.Conv2d(256, 256, 3, 1, 1), nn.ReLU(), nn.MaxPool2d((2,1), (2,1)),
            nn.Conv2d(256, 512, 3, 1, 1), nn.BatchNorm2d(512), nn.ReLU(),
            nn.Conv2d(512, 512, 3, 1, 1), nn.BatchNorm2d(512), nn.ReLU(), nn.MaxPool2d((2,1), (2,1)),
            nn.Conv2d(512, 512, 2, 1, 0), nn.ReLU(),
            nn.AdaptiveAvgPool2d((1, None))  # height → 1
        )

        self.rnn1 = nn.LSTM(512, nh, bidirectional=True)  
        self.rnn2 = nn.LSTM(nh * 2, nh, bidirectional=True)
        self.embedding = nn.Linear(nh * 2, nclass)

    def forward(self, x):
        conv = self.cnn(x)           # (B, C, H, W)
        b, c, h, w = conv.size()
        # assert h == 3               ❌ 제거하거나 아래처럼 수정
        assert h == 1, f"Expected height=1 but got {h}"

        conv = conv.squeeze(2)       # (B, C, W)
        conv = conv.permute(2, 0, 1) # (W, B, C)

        rnn_out, _ = self.rnn1(conv)
        rnn_out, _ = self.rnn2(rnn_out)
        output = self.embedding(rnn_out)  # (T, B, nclass)
        return output

class HandwrittenDataset(Dataset):
    def __init__(self, image_dir, label_path, transform=None, img_size=(64, 64)):
        self.image_dir = image_dir
        self.samples = []
        with open(label_path, "r") as f:
            for line in f:
                fname, label = line.strip().split('\t')
                self.samples.append((fname, label))
        self.img_size = img_size
        self.transform = transform
        self.charset = "0123456789"

    def __len__(self):
        return len(self.samples)

    def encode_label(self, label):
        return [self.charset.index(c) for c in label]

    def __getitem__(self, idx):
        fname, label = self.samples[idx]
        img_path = os.path.join(self.image_dir, fname)
        img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
        img = cv2.resize(img, self.img_size)
        img = img.astype(np.float32) / 255.0
        img = np.expand_dims(img, axis=0)
        img_tensor = torch.from_numpy(img).clone() 
        label_encoded = torch.tensor(self.encode_label(label), dtype=torch.long)
        return img_tensor, label_encoded
