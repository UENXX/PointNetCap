import os
import sys
import torch
import numpy as np

import datetime
import logging
import provider
import importlib
import shutil
import argparse

from pathlib import Path
from tqdm import tqdm
from PointNetCap.data_utils.PointCapDataset import PointCapDataset

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = BASE_DIR
sys.path.append(os.path.join(ROOT_DIR, 'models'))

torch.backends.cudnn.enable =True
torch.backends.cudnn.benchmark = True

data_path = '/pub/zwz/PointNetCap/data/dataset/'
train_dataset = PointCapDataset(root=data_path, train=True)
test_dataset = PointCapDataset(root=data_path, train=False)
trainDataLoader = torch.utils.data.DataLoader(train_dataset, batch_size=64, shuffle=True, num_workers=10, drop_last=True)
testDataLoader = torch.utils.data.DataLoader(test_dataset, batch_size=32, shuffle=False, num_workers=10)

model = importlib.import_module("pointnet_cap")
cap_extractor = model.get_model(1)
cap_extractor = cap_extractor.cuda()
criterion = model.get_loss()
criterion = criterion.cuda()
# optimizer = torch.optim.Adam(
#         cap_extractor.parameters(),
#         lr=0.001,
#         betas=(0.9, 0.999),
#         eps=1e-08,
#         weight_decay=1e-4
#     )
optimizer = torch.optim.SGD(cap_extractor.parameters(), lr=0.01, momentum=0.9)
scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=20, gamma=0.7)

epoch_num = 1000
start_epoch = 0
print("Train Start")
for epoch in range(start_epoch, epoch_num):
    print("epoch: " + str(epoch + 1))
    cap_extractor = cap_extractor.train()
    scheduler.step()
    mean_correct = []
    epoch_loss = 0
    for batch_id, (points, target) in tqdm(enumerate(trainDataLoader, 0), total=len(trainDataLoader), smoothing=0.9):
        optimizer.zero_grad()

        points = points.data.numpy()
        points[:, :, 0:3] = provider.random_scale_point_cloud(points[:, :, 0:3])
        points[:, :, 0:3] = provider.shift_point_cloud(points[:, :, 0:3])
        points = torch.Tensor(points)
        points = points.transpose(2, 1)

        points, target = points.cuda(), target.cuda()

        pred, trans_feat = cap_extractor(points)
        target = target.to(torch.float32)
        loss = criterion(pred, target, trans_feat)
        epoch_loss += loss.cpu()

        loss.backward()
        optimizer.step()


    print('Train Loss: %.3f' % (epoch_loss / (batch_id + 1)))

    if (epoch + 1) % 5 == 0:
        print("Test")
        total_mse = 0
        cap_extractor = cap_extractor.eval()
        for batch_id, (points, target) in tqdm(enumerate(testDataLoader, 0), total=len(testDataLoader)):
            points, target = points.cuda(), target.cuda()
            points = points.transpose(2, 1)

            points = points.to(torch.float32)

            pred, trans_feat = cap_extractor(points)
            target = target.to(torch.float32)
            mse = criterion(pred, target, trans_feat)
            total_mse += mse.cpu()

        print("total_mse: %.3f" % (total_mse / (batch_id + 1)))


