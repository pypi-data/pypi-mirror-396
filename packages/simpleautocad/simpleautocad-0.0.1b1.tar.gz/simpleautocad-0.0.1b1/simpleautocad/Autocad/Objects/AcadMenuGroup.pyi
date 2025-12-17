from ..Base import *
from ..AcadObject import *
from ..Proxy import AccessMode as AccessMode, proxy_property as proxy_property

class AcadMenuGroup(AppObject):
    def __init__(self, obj) -> None: ...
    Application: AcadApplication
    MenuFileName: str
    Menus: AcadPopupMenus
    Name: str
    Parent: AppObject
    Toolbars: AcadToolbars
    Type: AcMenuGroupType
    def Save(self, MenuFileType: In[AcMenuFileType]) -> None: ...
    def SaveAs(self, MenuFileName: In[str], MenuFileType: In[AcMenuFileType]) -> None: ...
    def Unload(self) -> None: ...
