# app/utils/safe_loader.py

from torch.serialization import add_safe_globals
from ultralytics.nn.modules import Conv
from ultralytics.nn.tasks import DetectionModel
from torch.nn import Module
from torch.nn.modules.container import Sequential

def register_safe_classes():
    add_safe_globals([
        Conv,
        DetectionModel,
        Module,
        Sequential,
    ])
