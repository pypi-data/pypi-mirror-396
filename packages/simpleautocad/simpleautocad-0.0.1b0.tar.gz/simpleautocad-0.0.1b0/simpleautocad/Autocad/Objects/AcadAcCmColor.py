from __future__ import annotations
# from ..Base import *
from ..Proxy import proxy_property, AccessMode
from ..AcadObject import *



class AcadAcCmColor(AppObject):
    def __init__(self, obj) -> None: super().__init__(obj)

    Blue: int = proxy_property(int,'Blue',AccessMode.ReadOnly)
    BookName: str = proxy_property(str,'BookName',AccessMode.ReadOnly)
    ColorIndex: AcColor = proxy_property('AcColor','ColorIndex',AccessMode.ReadWrite)
    ColorMethod: AcColorMethod = proxy_property('AcColorMethod','ColorMethod',AccessMode.ReadWrite)
    ColorName: str = proxy_property(str,'ColorName',AccessMode.ReadOnly)
    EntityColor: int = proxy_property(int,'EntityColor',AccessMode.ReadWrite)
    Green: int = proxy_property(int,'Green',AccessMode.ReadOnly)
    Red: int = proxy_property(int,'Red',AccessMode.ReadOnly)

    def Delete(self) -> None: 
        self._obj.Delete()
        
    def SetColorBookColor(self, BookName: In[str], ColorName: In[str]) -> None: 
        self._obj.SetColorBookColor(BookName, ColorName)

    def SetNames(self, ColorName: In[str], ColorBook: In[str]) -> None: 
        self._obj.SetNames(ColorName, ColorBook)
        
    def SetRGB(self, Red: In[int], Green: In[int], Blue: In[int]) -> None: 
        self._obj.SetRGB(Red, Green, Blue)
    