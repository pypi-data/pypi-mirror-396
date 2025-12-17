from ..Base import *
from ..AcadObject import *
from ..Proxy import AccessMode as AccessMode, proxy_property as proxy_property

class AcadTextStyle(AcadObject):
    def __init__(self, obj) -> None: ...
    BigFontFile: str
    FontFile: str
    Height: float
    LastHeight: float
    Name: str
    ObliqueAngle: float
    TextGenerationFlag: AcTextGenerationFlag
    Width: float
    def GetFont(self) -> tuple[str, bool, bool, int, int]: ...
    def SetFont(self, Typeface: In[str], Bold: In[bool], Italic: In[bool], CharSet: In[int], PitchAndFamily: In[int]) -> None: ...
