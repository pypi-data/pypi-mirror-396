from __future__ import annotations
from ..Base import *
from ..Proxy import proxy_property, AccessMode
from ..AcadObject import *



class AcadLayerStateManager(AppObject):
    def __init__(self, obj) -> None: super().__init__(obj)

    def Mask(self, Name: In[str]) -> AcLayerStateMask|int:
        return self._obj.Mask(Name)

    def Delete(self, Name: In[str]) -> None: 
        self._obj.Delete(Name)
        
    def Export(self, Name: In[str], FileName: In[str]) -> None: 
        self._obj.Export(Name, FileName)
        
    def Import(self,FileName: In[str]) -> None: 
        self._obj.Import(FileName)

    def Rename(self, OldName: In[str], NewName: In[str]) -> None: 
        self._obj.Rename(OldName, NewName)
        
    def Restore(self, Name: In[str]) -> None: 
        self._obj.Restore(Name)
        
    def Save(self, Name: In[str], Mask: In[AcLayerStateMask|int]) -> None: 
        self._obj.Save(Name, Mask)
        
    def SetDatabase(self, Database: In[AcadDatabase]) -> None: 
        self._obj.SetDatabase(Database)
