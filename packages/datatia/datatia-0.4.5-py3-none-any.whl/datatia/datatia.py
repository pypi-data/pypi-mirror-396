from torch.utils.data import Dataset as torchDataset, DataLoader
from typing import Union
from pathlib import Path
from dataclasses import dataclass
from datatia.actions import (
    Action, Truncate, Drop, PreMap, FieldData, LiveMapRow, RandomSubsample, PadGroup,
    RowData)
from datatia.tensor_source import TensorSource
import torch

@dataclass
class FieldSpec:
    name : str
    datatype : type
    dim : Union[torch.Size, None] = None # -1 should specify a variable dimension

    # For use with PadGroup only: create an extra output field with name {name}_length
    provide_length : bool = False 

    keep_in_memory : bool = True
    
    # Set to False -> will not be loaded, will be replaced with None
    do_load : bool = True

    def validate(self):
        """
        Validate a FieldSpec

        This checks that all the fields are valid: name is not empty, datatype is one of the allowed types,
        and dim is either None or a torch.Size.

        Raises:
            ValueError: if the FieldSpec is invalid
        """
        if self.name is None or len(self.name) == 0:
            raise ValueError(f"FieldSpec {self.name} has no name")
        allowed_types = [str, int, float, bool, torch.Tensor]
        if self.datatype not in allowed_types:
            raise ValueError(f"FieldSpec {self.name} has invalid datatype {self.datatype}")
        if self.dim is not None and not isinstance(self.dim, torch.Size):
            raise ValueError(f"FieldSpec {self.name} has invalid dim {self.dim}")
        if not self.keep_in_memory and not self.datatype is torch.Tensor:
            raise ValueError(f"keep_in_memory=False is only supported for torch.Tensor datatypes")
        if not self.datatype is torch.Tensor and self.dim is not None:
            raise ValueError(f"FieldSpec {self.name} has dim {self.dim} but datatype is not torch.Tensor")

    def data_validate(self, data):
        """
        Validate the data against the FieldSpec.

        This function checks if the datatype of the provided data matches the
        specified datatype of the FieldSpec. If the datatype is torch.Tensor,
        it also verifies that the shape of the data matches the specified dim
        field, considering -1 as a wildcard dimension.

        Args:
            data: The data to validate against the FieldSpec.

        Raises:
            ValueError: If the datatype of data does not match the FieldSpec's
            datatype, or if data is a torch.Tensor and its shape does not match
            the specified dim.
        """

        if type(data) is not self.datatype:
            raise ValueError(f"FieldSpec {self.name} has datatype {self.datatype} but data is of type {type(data)}")
        if type(data) is torch.Tensor and self.dim is not None:
            if not self.shape_matches(data):
                raise ValueError(f"FieldSpec {self.name} has dim {self.dim} but data has shape {data.shape}")

    def shape_matches(self, data):
        """
        Check that the shape of a tensor matches the specified dim field of the FieldSpec.

        If dim is None, this function always returns True. If dim is a torch.Size, this
        function checks that the shape of the tensor matches this, ignoring any dimensions
        that are -1 in the FieldSpec.

        Args:
            data: the tensor to check

        Returns:
            True if the shape matches, False otherwise
        """
        for dim in self.dim:
            if dim == -1:
                continue
            if data.shape[dim] != self.dim[dim]:
                return False
        return True

class Dataset(torchDataset):
    def __init__(self,
        filelist: Union[str, Path, list[str]],
        field_specs: list[FieldSpec],
        is_train: bool = True, # controls training-only actions like random subsampling
        actions: list[Action] = [],
        *args, **kwargs):
        """
        Create a new Dataset.

        Args:
            filelist: path to filelist file, or a list of filelist entries
            field_specs: list of FieldSpecs describing each column in the filelist
            is_train: whether to apply training-only actions like random subsampling
            actions: list of Actions to apply to data
            args/kwargs: passed to torch.utils.data.Dataset.__init__

        Raises:
            ValueError: if the number of fields in the filelist does not match the number of FieldSpecs

        """
        super().__init__(*args, **kwargs)

        self.validate_specs(field_specs)
        filelist = self.process_filelist_file(filelist)
        filelist = self.create_filelist_rows(filelist)

        if len(filelist) and len(filelist[0]) != len(field_specs):
            raise ValueError(f"Number of fields in filelist ({len(filelist[0])}) does not match number of FieldSpecs ({len(field_specs)})")

        self.actions = actions

        self.live_actions = {
            'live_map_row': [ action for action in actions if isinstance(action, LiveMapRow) ],
            'random_subsample': [ action for action in actions if isinstance(action, RandomSubsample) ],
            'pad_group': [ action for action in actions if isinstance(action, PadGroup) ]
        }

        self.load_data(filelist, field_specs)
        self.field_specs = field_specs
        self.field_specs_map = { field_spec.name: field_spec for field_spec in field_specs }
        self.is_train = is_train

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        data = self.data[idx]
        
        def resolve_tensor_source(k, v):
            if k == '__filelist_entry__':
                return v
            field_spec_name = k
            field_spec = self.field_specs_map[field_spec_name]
            if not field_spec.do_load:
                return None
            if isinstance(v, TensorSource):
                return v.get()
            return v

        # Resolve any TensorSources
        data : RowData = {
            k: resolve_tensor_source(k, v) for k, v in data.items()
        }
        for action in self.live_actions['live_map_row']:
            data = action.apply(data)
        if self.is_train:
            for action in self.live_actions['random_subsample']:
                field_names = action.fields
                field_datas = [ data[field_name] for field_name in field_names ]
                new_tensors = action.apply(field_datas)
                for i, field_name in enumerate(field_names):
                    data[field_name] = new_tensors[i]
        return data

    def collate_fn(self, batch):
        ret = {}
        for action in self.live_actions['pad_group']:
            field_names = action.fields
            batch_tensors = [ [ data[field_name] for field_name in field_names ] for data in batch ]
            new_batch_tensors, unpadded_lengths = action.apply(batch_tensors)
            for row in range(len(batch)):
                for i, field_name in enumerate(field_names):
                    batch[row][field_name] = new_batch_tensors[row][i]
                    if self.field_specs_map[field_name].provide_length:
                        batch[row][f'{field_name}_length'] = unpadded_lengths[field_name][row]

        for field_spec in self.field_specs:
            if not field_spec.do_load:
                continue
            if field_spec.datatype is torch.Tensor:
                ret[field_spec.name] = torch.stack([d[field_spec.name] for d in batch])
                if field_spec.provide_length:
                    ret[f'{field_spec.name}_length'] = torch.tensor([d[f'{field_spec.name}_length'] for d in batch])
            elif field_spec.datatype is int:
                ret[field_spec.name] = torch.tensor([d[field_spec.name] for d in batch])
            else:
                ret[field_spec.name] = [d[field_spec.name] for d in batch]

        ret['__filelist_entry__'] = [d['__filelist_entry__'] for d in batch]
        return ret

    def loader(self, *args, **kwargs):
        return DataLoader(self, collate_fn=self.collate_fn, *args, **kwargs)

    def load_data(self, 
        filelist: Union[str, Path, list[str]],
        field_specs: list[FieldSpec]):
        """
        Load the data from the filelist into memory
        and apply Truncate, Drop, and PreMap actions.

        For each row in the filelist, and for each field in the row, this
        method creates a dictionary mapping the field name to the value.
        The value is converted to the type specified in the FieldSpec.

        If the FieldSpec.datatype is torch.Tensor, then the value is treated as
        a path to a torch tensor, and the tensor is loaded from disk. If
        FieldSpec.keep_in_memory is true, the tensor is loaded immediately and
        stored in memory. If FieldSpec.keep_in_memory is false, the path to the
        tensor is stored instead.

        The resulting list of dictionaries is stored in the self.data attribute.

        Args:
            filelist: the filelist to load data from
            field_specs: the list of FieldSpecs to use to interpret the filelist
        """
        self.data = []

        self.field_specs_map = {
            field_spec.name: field_spec for field_spec in field_specs
        }

        self.drop_actions = [
            action for action in self.actions if isinstance(action, Drop)
        ]
        self.truncate_actions = {
            field: [] for field in [field_spec.name for field_spec in field_specs]
        }
        self.premap_actions = {
            field: [] for field in [field_spec.name for field_spec in field_specs]
        }

        for action in self.actions:
            if isinstance(action, Truncate):
                action : Truncate
                if self.field_specs_map[action.field].datatype != torch.Tensor:
                    raise ValueError(f"Truncate action on non-tensor field {action.field}")
                self.truncate_actions[action.field].append(action)
            if isinstance(action, PreMap):
                if self.field_specs_map[action.field].keep_in_memory == False:
                    raise ValueError(f"PreMap action on non-memory field {action.field}")
                self.premap_actions[action.field].append(action)

        for i, row in enumerate(filelist):
            data : RowData = {}
            if not len(row) == len(field_specs):
                raise ValueError(f"Number of fields in row {i} ({len(row)}) does not match number of FieldSpecs ({len(field_specs)}): {row}")
            for field_spec, value in zip(field_specs, row):
                if field_spec.datatype == torch.Tensor:
                    # Treat the text value as a path to a torch tensor
                    value = TensorSource(value, 
                        self.truncate_actions[field_spec.name],
                        self.premap_actions[field_spec.name],
                        field_spec.keep_in_memory)
                    data[field_spec.name] = value
                else:
                    data[field_spec.name] = field_spec.datatype(value)
                    data[field_spec.name] = self.premap(field_spec.name, data[field_spec.name])

            data['__filelist_entry__'] = str(row)

            do_append = True
            for action in self.drop_actions:
                if action.test(data):
                    do_append = False
                    break

            if do_append:
                self.data.append(data)

    def premap(self, field_name : str, value : FieldData):
        for action in self.premap_actions[field_name]:
            value = action.apply(value)
        return value

    def validate_specs(self,
        field_specs: list[FieldSpec]):
        """
        Validate all FieldSpecs in a list

        This calls the validate() method on each FieldSpec in the list.

        Args:
            field_specs: list of FieldSpecs to validate

        Raises:
            ValueError: if any FieldSpec is invalid
        """
        for field_spec in field_specs:
            field_spec.validate()

    def create_filelist_rows(self,
        true_filelist: list[str],
        delimiter: str = '|'):
        """
        Split a list of strings into a list of lists of strings, split by delimiter.

        Args:
            true_filelist: the list of strings to split
            delimiter: the delimiter to split the strings with

        Returns:
            A list of lists of strings, where each inner list is the split version of the corresponding input string.
        """
        rows = []
        for line in true_filelist:
            line = line.removesuffix('\n')
            rows.append([e for e in line.split(delimiter)])
        return rows

    def process_filelist_file(self,
        filelist: Union[str, Path, list[str]]):
        """
        Convert a filelist input into a list of strings.

        Args:
            filelist: the filelist, which can be either a string (interpreted as a
                path to a filelist file), a Path object (interpreted as a path to a
                filelist file), or a list of strings (interpreted as the filelist)

        Returns:
            a list of strings, which is the filelist
        """
        
        if type(filelist) is list:
            return filelist
        if type(filelist) is str:
            filelist_path = Path(filelist)
            if not filelist_path.exists():
                raise ValueError(f"Filelist path {filelist_path} does not exist")
        filelist : Path
        with open(filelist, encoding='utf-8') as f:
            lines = f.readlines()
        return lines
