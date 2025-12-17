from ..Base import *
from ..Proxy import *
from ..AcadObject import *
from .AcadBlock import IAcadBlock as IAcadBlock

class AcadPaperSpace(IAcadBlock):
    def __init__(self, obj) -> None: ...
    Name: str
    def AddPViewport(self, Center: In[PyGePoint3d], Width: In[float], Height: In[float]) -> AcadPViewport: ...
