from __future__ import annotations
from ..Base import *
from ..Proxy import proxy_property, AccessMode
from ..AcadObject import *



class AcadLineTypes(IAcadObjectCollection):
    def __init__(self, obj) -> None: super().__init__(obj)

    def Add(self, Name: In[str]) -> AcadLineType: 
        return AcadLineType(self._obj.Add(Name))

    def Item(self, Index: In[int|str]) -> AcadLineType:
        return AcadLineType(self._obj.Item(Index))
        
    def Load(self, LineTypeName: In[str], FileName: In[str]) -> None:
        self._obj.Load(LineTypeName, FileName)

    def __iter__(self):
        for item in self._obj:
            yield AcadLineType(item)