import datatia as dt
import torch
import os

TEST_FILES_DIR = 'test/test_files'
TEST_FILES_LIST = 'test/filelist.txt'

def generate_dummy_files():
    """
    Generate a set of dummy files for testing datatia.

    This function writes a bunch of random tensors to disk, and creates a filelist
    that points to them. The filelist is written to the file specified by
    TEST_FILES_LIST.

    The dummy files are written to the directory specified by TEST_FILES_DIR.

    The filelist has the following format:

    tensor1_0.pt|tensor2_0.pt|0
    tensor1_1.pt|tensor2_1.pt|1
    tensor1_2.pt|tensor2_2.pt|2
    tensor1_3.pt|tensor2_3.pt|3

    The first column is the path to the first tensor, the second column is the
    path to the second tensor, and the third column is the label.

    The tensors are all of shape (8, 32) for tensor1 and (10, 32) for tensor2, 
    and the labels are all integers from 0 to 7, 
    EXCEPT the first tensor1 which is of shape (4, 32).

    """
    os.makedirs(TEST_FILES_DIR, exist_ok=True)
    
    filelist = []
    for i in range(8):
        if i == 0:
            tensor1 = torch.randn([4, 32])
        else:
            tensor1 = torch.randn([8, 32])
        tensor2 = torch.randn([10, 32])

        tensor1_path = os.path.join(TEST_FILES_DIR, f'tensor1_{i}.pt')
        torch.save(tensor1, tensor1_path)
        tensor2_path = os.path.join(TEST_FILES_DIR, f'tensor2_{i}.pt')
        torch.save(tensor2, tensor2_path)

        line = f'{tensor1_path}|{tensor2_path}|{i}'
        filelist.append(line)

    with open(TEST_FILES_LIST, 'w') as f:
        f.write('\n'.join(filelist))

def test_datatia():
    generate_dummy_files()
    field_specs = [dt.FieldSpec(
            name='tensor1', datatype=torch.Tensor, provide_length=True),
            dt.FieldSpec(
            name='tensor2', datatype=torch.Tensor, keep_in_memory=False),
            dt.FieldSpec(
            name='label', datatype=int)]

    # Test dataset loading and truncate
    dataset = dt.Dataset(filelist=TEST_FILES_LIST,
        field_specs = field_specs,
        actions=[dt.Truncate(field='tensor1', dims=[0], max_lengths=[4])])
    assert dataset[0]['tensor1'].shape == torch.Size([4, 32])
    assert dataset[0]['tensor2'].shape == torch.Size([10, 32])
    assert len(dataset[0]['__filelist_entry__'])

    # Test dropping
    dataset = dt.Dataset(filelist=TEST_FILES_LIST,
        field_specs = field_specs,
        actions=[dt.Drop(condition=lambda row: row['label'] == 0)])
    assert len(dataset) == 7

    # Test premap on literal field
    dataset = dt.Dataset(filelist=TEST_FILES_LIST,
        field_specs = field_specs,
        actions=[dt.PreMap(field='label', operation=lambda x: x + 1)])
    assert dataset[0]['label'] == 1

    # Test premap on tensor field
    dataset = dt.Dataset(filelist=TEST_FILES_LIST,
        field_specs = field_specs,
        actions=[dt.PreMap(field='tensor1', operation=lambda x: x * 0)])
    assert dataset[0]['tensor1'].abs().sum() == 0

    # Test live map row
    dataset = dt.Dataset(filelist=TEST_FILES_LIST,
        field_specs = field_specs,
        actions=[dt.LiveMapRow(operation=lambda row: {k: v * 0 for k, v in row.items()})])
    assert dataset[1]['tensor1'].abs().sum() == 0
    assert dataset[1]['tensor2'].abs().sum() == 0
    assert dataset[1]['label'] == 0

    # Test random subsample
    dataset = dt.Dataset(filelist=TEST_FILES_LIST,
        field_specs = field_specs,
        actions=[dt.RandomSubsample(fields=['tensor1', 'tensor2'], 
            dims=[0], length=4)])
    assert dataset[0]['tensor1'].shape[0] == 4
    assert dataset[0]['tensor2'].shape[0] == 4

    # Test pad group
    dataset = dt.Dataset(filelist=TEST_FILES_LIST,
        field_specs = field_specs,
        actions=[dt.PadGroup(fields=['tensor1', 'tensor2'], 
            dims=[0, 1], values=[0, 0], to_multiple=[4, 5])])
    loader = dataset.loader(batch_size=4)
    batch = next(iter(loader))
    assert batch['tensor1'][0].shape[0] == 12
    assert batch['tensor1'][0].shape[1] == 35
    assert batch['tensor2'][0].shape[0] == 12
    assert batch['tensor2'][0].shape[1] == 35
    assert batch['tensor1'][0][8:, :].abs().sum() == 0
    assert batch.get('tensor1_length') is not None
    assert batch.get('tensor1_length')[0] == 4
    assert batch['label'][0] == 0
    assert batch['label'].shape == torch.Size([4])

    field_specs = [dt.FieldSpec(
            name='tensor1', datatype=torch.Tensor, provide_length=True),
            dt.FieldSpec(
            name='tensor2', datatype=torch.Tensor, keep_in_memory=False, do_load=False),
            dt.FieldSpec(
            name='label', datatype=int)]
    dataset = dt.Dataset(filelist=TEST_FILES_LIST,
        field_specs = field_specs,
        actions=[dt.PadGroup(fields=['tensor1'], 
            dims=[0], values=[0], to_multiple=[4])])
    loader = dataset.loader(batch_size=4)
    batch = next(iter(loader))
    assert 'tensor2' not in batch
    assert batch['__filelist_entry__']
