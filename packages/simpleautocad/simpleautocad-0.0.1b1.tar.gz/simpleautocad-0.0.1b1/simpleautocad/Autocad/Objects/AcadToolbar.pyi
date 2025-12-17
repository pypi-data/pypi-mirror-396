from ..Base import *
from ..Proxy import *
from ..AcadObject import *

class AcadToolbar(AppObject):
    def __init__(self, obj) -> None: ...
    Application: AcadApplication
    Count: int
    DockStatus: AcToolbarDockStatus
    FloatingRows: int
    Height: int
    HelpString: str
    LargeButtons: bool
    Left: int
    Name: str
    Parent: AppObject
    TagString: str
    Top: int
    Visible: bool
    Width: float
    def AddSeparator(self, Index: In[int | str]) -> AcadToolbarItem: ...
    def AddToolbarButton(self, Index: In[int | str], Name: In[str], HelpString: In[str], Macro: In[str], FlyoutButton: In[vBool] = None) -> AcadToolbarItem: ...
    def Delete(self) -> None: ...
    def Dock(self, Side: In[AcToolbarDockStatus]) -> None: ...
    def Float(self, Top: In[int], Left: In[int], NumberFloatRows: In[int]) -> None: ...
    def Item(self, Index: In[int | str]) -> AcadObject: ...
