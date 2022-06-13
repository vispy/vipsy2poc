# -----------------------------------------------------------------------------
# Graphic Server Protocol (GSP) — reference implementation
# Copyright 2022 Nicolas P. Rougier - BSD 2 Clauses licence
# -----------------------------------------------------------------------------
import numpy as np
from typing import Union
from GSP import OID, Object, command
from typeguard import typechecked
from datatype import Datatype

class Array(Object):

    # Convenience method, not part of the protocol
    @classmethod
    def from_numpy(cls, Z):
        if (isinstance(Z, np.ndarray)):
            datatype = Datatype.from_numpy(Z.dtype)
            shape = list(Z.shape)
            data = Z.tobytes()
            return Array(shape, datatype, data)
        raise ValueError(f"Unknown type for {Z}, cannot convert to Array")

    
    @typechecked
    @command("")
    def __init__(self, shape : Union[int,list],
                       datatype : Union[str,Datatype],
                       data  : bytes):
        Object.__init__(self)
        self.shape = shape
        if isinstance(datatype, (Datatype,)):
            self.datatype = datatype
        else:
            self.datatype = Datatype(datatype)
        self.data = data
        dtype = Datatype.to_numpy(self.datatype.datatype)
        self._array = np.frombuffer(data, dtype=dtype).reshape(shape).copy()

    @typechecked
    @command("set_data")
    def set_data(self, offset : int,
                       data   : bytes ):
        size = len(data) // self._array.dtype.itemsize
        data = np.frombuffer(data, dtype=self._array.dtype)
        self._array.ravel()[offset:offset+size] = data

    def __repr__(self):
        return f"Array [id={self.id}]: {tuple(self.shape)}, {self.datatype}, {self._array}"
        
    def __eq__(self, other):
        for key in ("shape", "datatype"):
            if getattr(self, key) != getattr(other, key):
                return False
        if not np.array_equal(self._array, other._array):
            return False
        return True

    # Convenience method, not part of the protocol
    def __getitem__(self, key):
        import array_view
        return array_view.ArrayView(self, key)
