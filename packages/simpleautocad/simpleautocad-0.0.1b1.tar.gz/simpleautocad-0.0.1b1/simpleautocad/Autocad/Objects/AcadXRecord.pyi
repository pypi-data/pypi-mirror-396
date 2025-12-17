from ..Base import *
from ..Proxy import *
from ..AcadObject import *

class AcadXRecord(AcadObject):
    def __init__(self, obj) -> None: ...
    Name: str
    TranslateIDs: bool
    def GetXRecordData(self) -> tuple: ...
    def SetXRecordData(self, XRecordDataType: In[Variant], XRecordData: In[Variant]) -> None: ...
