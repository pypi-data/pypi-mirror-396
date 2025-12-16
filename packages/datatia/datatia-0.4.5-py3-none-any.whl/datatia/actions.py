import math
import torch
from typing import Union, Callable, TYPE_CHECKING
from datatia.tensor_source import TensorSource
from enum import Enum

FieldData = Union[str, int, float, bool, torch.Tensor]
FieldDataProxied = Union[str, int, float, bool, TensorSource]
RowData = dict[str, FieldData]
RowDataProxied = dict[str, FieldDataProxied]

class Action:
    """
    Base class for all actions
    """
    def __init__(self):
        pass

    def resolveRow(self, row : RowDataProxied) -> RowData:
        return {
            k: v.get() if isinstance(v, TensorSource) else v for k, v in row.items()}

class Truncate(Action):
    """
    Truncate a tensor field from the beginning. 
    Applied on first data load (or live if keep_in_memory is False).
    Truncation is always performed before any other action.
    """
    def __init__(self, field : str, 
        dims : list[int], max_lengths : list[int]):
        super().__init__()
        self.field = field
        self.dims = dims
        self.max_lengths = max_lengths

    def apply(self, tensor : torch.Tensor):
        for dim, max_length in zip(self.dims, self.max_lengths):
            tensor = tensor.narrow(dim, 0, max_length)
        return tensor

class Drop(Action):
    """
    Drop a row if a condition is met (True means drop the row).
    Applied only on first data load
    """
    def __init__(self, condition : Callable[[RowData], bool]):
        super().__init__()
        self.condition = condition

    def test(self, row : RowDataProxied):
        return self.condition(self.resolveRow(row))

class PreMap(Action):
    """
    Apply an operation on a field value on first data load
    (cannot be used if keep_in_memory is False)
    """
    def __init__(self, 
        field : str, 
        operation : Callable[[FieldData], FieldData]):
        super().__init__()
        self.field = field
        self.operation = operation

    def apply(self, field : FieldData):
        return self.operation(field)

class LiveMapRow(Action):
    """
    Apply an operation on a row on every data access 
    (i.e. for random data augmentation)
    """
    def __init__(self, 
        operation : Callable[[RowData], RowData]):
        super().__init__()
        self.operation = operation

    def apply(self, row : RowData):
        return self.operation(row)

class RandomSubsample(Action):
    """
    Randomly subsample sequence dimensions of one or more tensor fields
    on every data access, using the same starting index across all fields.
    Use frame_multiples for frame-aligned features (e.g., spectrogram vs waveform)
    Only runs if is_train=True for the dataset.
    """
    def __init__(self,
        fields: list[str],
        dims: list[int],
        length: int,  # Single length since all fields represent same time duration
        frame_multiples: list[int] = []):
        super().__init__()
        self.fields = fields 
        self.dims = dims
        self.length = length
        if len(frame_multiples) == 0:
            self.frame_multiples = [1 for _ in range(len(fields))]
        else:
            self.frame_multiples = frame_multiples
    
    def apply(self, field_tensors: list[torch.Tensor]):
        if not field_tensors:
            return field_tensors
        
        # Find the constraining field (one that limits how much we can sample)
        max_possible_length = float('inf')
        for i, tensor in enumerate(field_tensors):
            dim = self.dims[i] if i < len(self.dims) else self.dims[-1]
            frame_mult = self.frame_multiples[i]
            tensor_length = tensor.shape[dim]
            target_length = self.length * frame_mult
            
            possible_length = tensor_length // frame_mult
            max_possible_length = min(max_possible_length, possible_length)
        
        # Determine single start index in "time units"
        if max_possible_length <= self.length:
            start_time = 0
        else:
            start_time = torch.randint(0, max_possible_length - self.length + 1, (1,))[0]
        
        new_tensors = []
        for i, tensor in enumerate(field_tensors):
            dim = self.dims[i] if i < len(self.dims) else self.dims[-1]
            frame_mult = self.frame_multiples[i]
            
            # Convert time units to actual indices for this tensor
            start_idx = start_time * frame_mult
            target_length = self.length * frame_mult
            target_length = min(target_length, tensor.shape[dim] - start_idx)
            
            new_tensor = tensor.narrow(dim, start_idx, target_length)
            new_tensors.append(new_tensor)
        
        return new_tensors

class PadGroupMode(Enum):
    UNDEFINED = 0
    MAXIMUM = 1
    MULTIPLE = 2
    LENGTH = 3

class PadGroup(Action):
    """
    For batched data, right-pad dimensions of one or more tensor fields to the
    same length per dimension using fill values.

    This assumes that the padded dimensions are the same across all fields.

    If LENGTH is specified, this assumes that the dimension to be padded is smaller or equal to the specified length.
    Use Truncate to ensure that the dimension to be padded is smaller than the specified length.

    Dimension indexing uses unbatched dimensions.
    For example, if we expect a 3D tensor with shape [batch, height, width],
    and we want to pad the height and width dimensions to the same length,
    we should specify dims=[0, 1] and to_length=[height, width].

    If neither to_multiple or to_length are specified, use the maximum length.
    """
    def __init__(self,
        fields : list[str],
        dims : list[int],
        values : list[Union[float, int]],
        to_multiple : list[Union[int, None]] = [],
        to_length : list[Union[int, None]] = [],
        ):
        super().__init__()
        self.fields = fields
        self.dims = dims
        self.to_multiple = to_multiple
        self.to_length = to_length
        self.values = values

    def determine_pad_mode(self, i):
        if len(self.to_multiple) > i and self.to_multiple[i] is not None:
            if len (self.to_length) > i and self.to_length[i] is not None:
                raise ValueError(
                    f"PadGroup cannot have both to_multiple and to_length specified at dim {i}")
            return PadGroupMode.MULTIPLE
        elif len(self.to_length) > i and self.to_length[i] is not None:
            return PadGroupMode.LENGTH
        else:
            return PadGroupMode.MAXIMUM

    def apply(self, batch_tensors : list[list[torch.Tensor]]):
        # [ [field1, field2] , [field1, field2] ]
        if not len(batch_tensors) or not len(batch_tensors[0]):
            return batch_tensors

        # 1. Determine target padding length
        target_lengths = [0 for _ in range(len(self.dims))]
        unpadded_lengths = {}

        for i in range(len(self.dims)):
            pad_group_mode = self.determine_pad_mode(i)
            if pad_group_mode == PadGroupMode.LENGTH:
                target_lengths = self.to_length
                for batch in batch_tensors:
                    for field_tensor in batch:
                        target_lengths[i] = max(
                            field_tensor.shape[self.dims[i]], target_lengths[i])
            else:
                for batch in batch_tensors:
                    for field_tensor in batch:
                        target_lengths[i] = max(
                            field_tensor.shape[self.dims[i]], target_lengths[i])
                if pad_group_mode == PadGroupMode.MULTIPLE:
                    target_lengths[i] = int(
                        math.ceil(target_lengths[i] / self.to_multiple[i]) * self.to_multiple[i])

        for i,field in enumerate(self.fields):
            unpadded_lengths[field] = [
                batch_tensors[j][i].shape[self.dims[i]] for j in range(len(batch_tensors))
            ]
 
        # 2. Pad tensors to correct length
        new_batch_tensors = []
        for batch in batch_tensors:
            new_tensors = []
            # [field1, field2]
            for field_tensor in batch: # field1
                for i in range(len(self.dims)):
                    dim = self.dims[i]
                    target_length = target_lengths[i]
                    field_tensor = field_tensor.transpose(dim, -1)
                    field_tensor = torch.nn.functional.pad(
                        field_tensor, (
                            0, target_length - field_tensor.shape[-1]), value=self.values[i])    
                    field_tensor = field_tensor.transpose(-1, dim)
                new_tensors.append(field_tensor)
                # [pad_field1, pad_field2]
            new_batch_tensors.append(new_tensors) # [ [pad_field1, pad_field2] , [pad_field1, pad_field2] ]
        
        return new_batch_tensors, unpadded_lengths