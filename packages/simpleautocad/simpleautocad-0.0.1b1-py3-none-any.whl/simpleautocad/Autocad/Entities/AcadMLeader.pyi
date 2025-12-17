from ..Base import *
from ..Proxy import *
from ..AcadEntity import AcadEntity as AcadEntity
from .AcadLeader import AcadLeader as AcadLeader
from _typeshed import Incomplete

class AcadMLeader(AcadEntity):
    leaderLineIndex: Incomplete
    def __init__(self, obj, leaderLineIndex: int = 0) -> None: ...
    ArrowheadBlock: str
    ArrowheadSize: float
    ArrowheadType: AcDimArrowheadType
    BlockConnectionType: AcBlockConnectionType
    BlockScale: int
    ContentBlockName: str
    ContentBlockType: AcPredefBlockType
    ContentType: AcMLeaderContentType
    DogLegged: bool
    DoglegLength: float
    LandingGap: float
    LeaderCount: int
    LeaderLineColor: AcadAcCmColor
    LeaderLinetype: str
    LeaderLineWeight: AcLineWeight
    LeaderType: AcMLeaderType
    Normal: PyGeVector3d
    ScaleFactor: float
    StyleName: str
    TextAttachmentDirection: AcTextAttachmentDirection
    TextBackgroundFill: bool
    TextBottomAttachmentType: AcVerticalTextAttachmentType
    TextDirection: AcDrawingDirection
    TextFrameDisplay: bool
    TextHeight: float
    TextJustify: AcAttachmentPoint
    TextLeftAttachmentType: AcTextAttachmentType
    TextLineSpacingDistance: float
    TextLineSpacingFactor: float
    TextLineSpacingStyle: AcLineSpacingStyle
    TextRightAttachmentType: AcTextAttachmentType
    TextRotation: float
    TextString: str
    TextStyleName: str
    TextTopAttachmentType: AcVerticalTextAttachmentType
    TextWidth: float
    Type: AcLeaderType
    def AddLeader(self) -> AcadLeader: ...
    def AddLeaderLine(self, leaderIndex: In[int], pointArray: In[PyGePoint3dArray]) -> int: ...
    def AddLeaderLineEx(self, pointArray: In[PyGePoint3dArray]) -> int: ...
    def Evaluate(self) -> None: ...
    def GetBlockAttributeValue(self, attdefId: In[int]) -> str: ...
    def GetDoglegDirection(self, leaderIndex: In[int]) -> PyGeVector3d: ...
    def GetLeaderIndex(self, leaderLineIndex: In[int]) -> int: ...
    def GetLeaderLineIndexes(self, leaderIndex: In[int]) -> vDoubleArray: ...
    def GetLeaderLineVertices(self, leaderLineIndex: In[int]) -> PyGePoint3dArray: ...
    def GetVertexCount(self, leaderLineIndex: In[int]) -> int: ...
    def RemoveLeader(self, leaderIndex: In[int]) -> None: ...
    def RemoveLeaderLine(self, leaderLineIndex: In[int]) -> None: ...
    def SetBlockAttributeValue(self, attdefId: In[int], value: In[str]) -> None: ...
    def SetDoglegDirection(self, leaderIndex: In[int], dirVec: In[vDoubleArray]) -> None: ...
    def SetLeaderLineVertices(self, leaderLineIndex: In[int], pointArray: In[PyGePoint3dArray]) -> None: ...
