from ..Base import *
from ..Proxy import *
from ..AcadObject import *
from .AcadToolbar import *

class AcadToolbarItem(AppObject):
    def __init__(self, obj) -> None: ...
    Application: AcadApplication
    CommandDisplayName: str
    Flyout: AcadToolbar
    HelpString: str
    Index: int
    Macro: str
    Name: str
    Parent: AppObject
    TagString: str
    Type: AcToolbarItemType
    def AttachToolbarToFlyout(self, MenuGroupName: In[str], ToolbarName: In[str]) -> None: ...
    def Delete(self) -> None: ...
    def GetBitmaps(self) -> tuple[str]: ...
    def SetBitmaps(self, SmallIconName: In[str], LargeIconName: In[str]) -> None: ...
