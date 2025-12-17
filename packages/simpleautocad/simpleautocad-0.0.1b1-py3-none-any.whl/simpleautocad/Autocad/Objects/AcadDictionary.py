from __future__ import annotations
from ..Proxy import *
from ..AcadObject import AcadObject
from .AcadXRecord import AcadXRecord


class AcadDictionary(AcadObject):
    def __init__(self, obj) -> None: super().__init__(obj)

    Name: str = proxy_property(str,'Name',AccessMode.ReadOnly)
    Count: int = proxy_property(int,'Count',AccessMode.ReadOnly)

    def AddObject(self, Keyword: In[str], ObjectName: In[str]) -> AcadObject: 
        return AcadObject(self._obj.AddObject(Keyword, ObjectName))

    def AddXRecord(self, Keyword: In[str]) -> AcadXRecord: 
        return AcadXRecord(self._obj.AddXRecord(Keyword))

    def GetName(self, Object: In[AppObject]) -> str: 
        return self._obj.GetName(Object())

    def GetObject(self, Name: In[str]) -> AcadObject: 
        return AcadObject(self._obj.GetObject(Name))

    def Item(self, Index: In[int|str]) -> AcadObject: 
        return AcadObject(self._obj.Item(Index))

    def Remove(self, Name: In[str]) -> AcadObject: 
        return AcadObject(self._obj.Remove(Name))

    def Rename(self, OldName: In[str], NewName: In[str]) -> None: 
        self._obj.Rename(OldName, NewName)
        
    def Replace(self, Name: In[str], NewObject: In[AppObject]) -> None: 
        self._obj.Replace(Name, NewObject())
