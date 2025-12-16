# What is it?
Opinionated declarative utility library for writing dataset classes. Intended for small pytorch experiments.

# Rationale
Pytorch dataset loading often involves certain common tasks:
- Load tensors or values from a filelist
- Truncate sequence/spatial dims to a maximum length
- Drop items that don't satisfy particular requirements
- Pad sequence/spatial dims to a multiple of a number or a maximum per-batch length
- Pad sequence/spatial dims in groups across multiple data fields in a batch
- Or (on training datasets only) randomly subsample sequence/spatial dims to meet a maximum length constraint, and add a "length" field for the pre-padding lengths
- Apply data augmentations

Implementing these tasks is often highly repetitive and error prone.

Dataset loading code can be further simplified by making certain assumptions:
- All data to be loaded takes the form of either a literal or a single file tensor which can be loaded from disk.
- Each dataset class takes only one filelist.
- Filelists contain only paths to tensors or python literals (such as class IDs).

# Example usage
We use an example a 3-column dataset specified as a filelist:
```yaml
# filelist.txt
test/test_files/tensor1_0.pt|test/test_files/tensor2_0.pt|0
test/test_files/tensor1_1.pt|test/test_files/tensor2_1.pt|1
test/test_files/tensor1_2.pt|test/test_files/tensor2_2.pt|2
```

When creating a `dt.Dataset` we specify names and datatypes for the columns in order.
```python
import datatia as dt
dataset = dt.Dataset(filelist='filelist.txt',
    field_specs=[
        dt.FieldSpec(name='tensor1', datatype=torch.Tensor),
        dt.FieldSpec(name='tensor2', datatype=torch.Tensor),
        dt.FieldSpec(name='id', datatype=int),
    ],
    actions=[dt.PadGroup(fields=['tensor1', 'tensor2'], 
        dims=[0, 1], values=[0, 0], to_multiple=[4, 5])])
loader = dataset.loader(batch_size=4)
batch = next(iter(loader))
```
The `PadGroup` action pads dimensions within a group of tensor columns for a
batch to either the next largest common multiple of a number (`to_multiple`), to
a fixed length (`to_length`), or to the maximum size of the dimensions within
the batch.

See `datatia/actions.py` for other actions (`Truncate`, `Drop`, `PreMap`, `LiveMapRow`, `RandomSubsample`, `PadGroup`) and `datatia/datatia.py` for `FieldSpec` and `dt.Dataset` API.

# Action order
Actions may be provided to the API in any order, but they are always executed
in a predefined order:

When the dataset initializes:
- `Truncate`
- `PreMap` (only works on in-memory tensors)
- `Drop`
Before collation:
- `LiveMapRow`
- `RandomSubsample`
During collation:
- `PadGroup`