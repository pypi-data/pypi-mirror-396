from ..Base import *
from ..Proxy import *
from ..AcadEntity import AcadEntity as AcadEntity

class AcadPolygonMesh(AcadEntity):
    def __init__(self, obj) -> None: ...
    Coordinates: PyGePoint3dArray
    MClose: bool
    MDensity: int
    MVertexCount: int
    NClose: bool
    NDensity: int
    NVertexCount: int
    Type: AcPolymeshType
    def Coordinate(self, Index: In[int]) -> PyGePoint3d: ...
    def Copy(self) -> AcadPolygonMesh: ...
    def AppendVertex(self, Point: In[PyGePoint3d]) -> None: ...
    def Explode(self) -> vObjectArray: ...
