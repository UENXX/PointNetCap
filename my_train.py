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
from data_utils.my_dataloader import MyDataLoader

data_path = '/pub/zwz/Pointnet_Pointnet2_pytorch/data/Cap_Dataset/dataset'
train_dataset = MyDataLoader(root=data_path)
test_dataset = MyDataLoader(root=data_path)
trainDataLoader = torch.utils.data.DataLoader(train_dataset, batch_size=32, shuffle=True, num_workers=10, drop_last=True)
testDataLoader = torch.utils.data.DataLoader(test_dataset, batch_size=32, shuffle=False, num_workers=10)

