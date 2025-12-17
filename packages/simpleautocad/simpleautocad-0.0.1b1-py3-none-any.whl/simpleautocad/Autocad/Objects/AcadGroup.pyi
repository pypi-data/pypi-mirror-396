from ..Base import *
from ..AcadObject import *
from ..Proxy import AccessMode as AccessMode, proxy_property as proxy_property

class AcadGroup(IAcadObjectCollection):
    def __init__(self, obj) -> None: ...
    Layer: str
    Linetype: str
    LinetypeScale: float
    Lineweight: AcLineWeight
    Material: str
    Name: str
    PlotStyleName: str
    TrueColor: AcadAcCmColor
    Visible: bool
    def AppendItems(self, Objects: In[vObjectArray]) -> None: ...
    def Highlight(self, HighlightFlag: In[bool]) -> None: ...
    def RemoveItems(self, Objects: In[vObjectArray]) -> None: ...
    def Update(self) -> None: ...
