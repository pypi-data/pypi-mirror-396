import torch
from typing import TYPE_CHECKING
from pathlib import Path
from datatia.utils import longpath
if TYPE_CHECKING:
    from datatia.actions import Truncate, PreMap

class TensorSource:
    def __init__(self, path : str,
            this_truncate_actions : list['Truncate'] = [],
            this_premap_actions : list['PreMap'] = [],
            keep_in_memory : bool = False):
        self.path = Path(path)
        self.keep_in_memory = keep_in_memory

        self.this_truncate_actions = this_truncate_actions
        if not self.path.exists():
            raise ValueError(f"TensorProxy path {self.path} does not exist")

        if self.keep_in_memory:
            self.tensor = self.truncate(torch.load(longpath(self.path), map_location='cpu'))
            self.tensor = self.premap(this_premap_actions, self.tensor)

    def premap(self,
            this_premap_actions : list['PreMap'],
            tensor : torch.Tensor):
        for action in (this_premap_actions):
            tensor = action.apply(tensor)
        return tensor

    def truncate(self, tensor):
        for action in (self.this_truncate_actions):
            tensor = action.apply(tensor)
        return tensor

    def get(self):
        if self.keep_in_memory:
            return self.tensor
        else:
            return self.truncate(torch.load(longpath(self.path)))