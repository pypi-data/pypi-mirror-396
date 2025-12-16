from __future__ import annotations
from ..Base import *
from ..Proxy import proxy_property, AccessMode
from ..AcadObject import *
from .AcadViewport import AcadViewport



class AcadViewports(IAcadObjectCollection):
    def __init__(self, obj) -> None: super().__init__(obj)

    def Add(self, Name: In[str]) -> AcadViewport: 
        return AcadViewport(self._obj.Add(Name))

    def DeleteConfiguration (self, Name: In[str]) -> None: 
        self._obj.DeleteConfiguration(Name)

    def Item(self, Index: In[int|str]) -> AcadViewport:
        return AcadViewport(self._obj.Item(Index))

    def __iter__(self):
        for item in self._obj:
            obj = AcadViewport(item)
            yield obj
