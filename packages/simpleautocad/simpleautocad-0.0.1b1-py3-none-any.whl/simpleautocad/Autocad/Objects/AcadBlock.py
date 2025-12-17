from __future__ import annotations
from ..Base import *
from ..Proxy import *
from ..AcadObject import *
from ..Objects import *
from ..AcadEntity import *
from ..Entities import *


class IAcadBlock(IAcadObjectCollection):
    def __init__(self, obj) -> None: super().__init__(obj)

    def Add3DFace(self, Point1: In[PyGePoint3d], 
                        Point2: In[PyGePoint3d], 
                        Point3: In[PyGePoint3d], 
                        Point4: In[PyGePoint3d] = None) -> Acad3DFace:
        return Acad3DFace(self._obj.Add3DFace(Point1(), Point2(), Point3(), Point4()))

    def Add3DMesh(self, M: In[int], 
                        N: In[int], 
                        PointsMatrix: In[vDoubleArray]) -> AcadPolygonMesh:
        return AcadPolygonMesh(self._obj.Add3DMesh(M, N, PointsMatrix()))

    def Add3DPoly(self, PointsArray: In[PyGePoint3dArray]) -> Acad3DPolyline:
        return Acad3DPolyline(self._obj.Add3Dpoly(PointsArray()))
        
    def AddArc(self, Center: In[PyGePoint3d], 
                        Radius: In[float], 
                        StartAngle: In[float], 
                        EndAngle: In[float]) -> AcadArc:
        return AcadArc(self._obj.AddArc(Center(), Radius, StartAngle, EndAngle))

    def AddAttribute(self, Height: In[float], 
                        Mode: In[AcAttributeMode], 
                        Prompt: In[str], 
                        InsertionPoint: In[PyGePoint3d], 
                        Tag: In[str], 
                        Value: In[str]) -> AcadAttribute:
        return AcadAttribute(self._obj.AddAttribute(Height, Mode.value, Prompt, InsertionPoint(), Tag, Value))
        
    def AddBox(self, Origin: In[PyGePoint3d], 
                        Length: In[float], 
                        Width: In[float], 
                        Height: In[float]) -> Acad3DSolid:
        return Acad3DSolid(self._obj.AddBox(Origin(), Length, Width, Height))

    def AddCircle(self, Center: In[PyGePoint3d], 
                        Radius: In[float]) -> AcadCircle:
        return AcadCircle(self._obj.AddCircle(Center(), Radius))
    
    def AddCone(self, Center: In[PyGePoint3d], 
                        BaseRadius: In[float], 
                        Height: In[float]) -> Acad3DSolid:
        return Acad3DSolid(self._obj.AddCone(Center(), BaseRadius, Height))

    def AddCustomObject(self, ClassName: In[str]) -> AcadObject:
        return AcadObject(self._obj.AddCustomObject(ClassName))

    def AddCylinder(self, Center: In[PyGePoint3d], 
                        Radius: In[float], 
                        Height: In[float]) -> Acad3DSolid:
        return Acad3DSolid(self._obj.AddCylinder(Center(), Radius, Height))

    def AddDim3PointAngular(self, AngleVertex: In[PyGePoint3d], 
                        FirstEndPoint: In[PyGePoint3d], 
                        SecondEndPoint: In[PyGePoint3d], 
                        TextPoint: In[PyGePoint3d]) -> AcadDim3PointAngular:
        return AcadDim3PointAngular(self._obj.AddDim3PointAngular(AngleVertex(), FirstEndPoint(), SecondEndPoint(), TextPoint()))

    def AddDimAligned(self, ExtLine1Point: In[PyGePoint3d], 
                        ExtLine2Point: In[PyGePoint3d], 
                        TextPosition: In[PyGePoint3d]) -> AcadDimAligned:
        return AcadDimAligned(self._obj.AddDimAligned(ExtLine1Point(), ExtLine2Point(), TextPosition()))

    def AddDimArc(self, ArcCenter: In[PyGePoint3d], 
                        FirstEndPoint: In[PyGePoint3d], 
                        SecondEndPoint: In[PyGePoint3d], 
                        ArcPoint: In[PyGePoint3d]) -> AcadDimArcLength:
        return AcadDimArcLength(self._obj.AddDimArc(ArcCenter(), FirstEndPoint(), SecondEndPoint(), ArcPoint()))

    def AddDimDiametric(self, ChordPoint: In[PyGePoint3d], 
                        FarChordPoint: In[PyGePoint3d], 
                        LeaderLength: In[float]) -> AcadDimDiametric:
        return AcadDimDiametric(self._obj.AddDimDiametric(ChordPoint(), FarChordPoint(), LeaderLength))

    def AddDimOrdinate(self, DefinitionPoint: In[PyGePoint3d], 
                        LeaderEndPoint: In[PyGePoint3d], 
                        UseXAxis: In[bool]) -> AcadDimOrdinate:
        return AcadDimOrdinate(self._obj.AddDimOrdinate(DefinitionPoint, LeaderEndPoint, UseXAxis))

    def AddDimRadial(self, Center: In[PyGePoint3d], 
                        ChordPoint: In[PyGePoint3d], 
                        LeaderLength: In[float]) -> AcadDimRadial:
        return AcadDimRadial(self._obj.AddDimRadial(Center(), ChordPoint(), LeaderLength))

    def AddDimRadialLarge(self, Center: In[PyGePoint3d], 
                        ChordPoint: In[PyGePoint3d], 
                        OverrideCenter: In[PyGePoint3d], 
                        JogPoint: In[PyGePoint3d], 
                        JogAngle: In[float]) -> AcadDimRadialLarge:
        return AcadDimRadialLarge(self._obj.AddDimRadialLarge(Center(), ChordPoint(), OverrideCenter(), JogPoint(), JogAngle))

    def AddDimRotated(self, XLine1Point: In[PyGePoint3d], 
                        XLine2Point: In[PyGePoint3d], 
                        DimLineLocation: In[PyGePoint3d], 
                        RotationAngle: In[float]) -> AcadDimRotated:
        return AcadDimRotated(self._obj.AddDimRotated(XLine1Point(), XLine2Point(), DimLineLocation(), RotationAngle))

    def AddEllipse(self, Center: In[PyGePoint3d], 
                        MajorAxis: In[PyGeVector3d], 
                        RadiusRatio: In[float]) -> AcadEllipse:
        return AcadEllipse(self._obj.AddEllipse(Center(), MajorAxis(), RadiusRatio))

    def AddEllipticalCone(self, Center: In[PyGePoint3d], 
                        MajorRadius: In[float], 
                        MinorRadius: In[float], 
                        Height: In[float]) -> Acad3DSolid:
        return Acad3DSolid(self._obj.AddEllipticalCone(Center(), MajorRadius, MinorRadius, Height))

    def AddEllipticalCylinder(self, Center: In[PyGePoint3d], 
                        MajorRadius: In[float], 
                        MinorRadius: In[float], 
                        Height: In[float]) -> Acad3DSolid:
        return Acad3DSolid(self._obj.AddEllipticalCylinder(Center(), MajorRadius, MinorRadius, Height))

    def AddExtrudedSolid(self, Profile: In[AcadRegion], 
                        Height: In[float], 
                        TaperAngle: In[float]) -> Acad3DSolid:
        return Acad3DSolid(self._obj.AddExtrudedSolid(Profile(), Height, TaperAngle))

    def AddExtrudedSolidAlongPath(self, Profile: In[AcadRegion], 
                        Path: In[AcadArc|AcadCircle|AcadEllipse|AcadPolyline|AcadSpline]) -> Acad3DSolid:
        return Acad3DSolid(self._obj.AddExtrudedSolidAlongPath(Profile(), Path))

    def AddHatch(self, PatternType: In[AcPatternType|AcGradientPatternType], 
                        PatternName: In[str], 
                        Associativity: In[bool], 
                        HatchObjectType: In[AcHatchObjectType] = None) -> AcadHatch:
        return AcadHatch(self._obj.AddHatch(PatternType, PatternName, Associativity, HatchObjectType))

    def AddLeader(self, PointsArray: In[PyGePoint3d], 
                        Annotation: In[AcadBlockReference|AcadMtext|AcadTolerance], 
                        Type: In[AcLeaderType]) -> AcadLeader:
        return AcadLeader(self._obj.AddLeader(PointsArray(), Annotation, Type))

    def AddLightWeightPolyline(self, VerticesList: In[PyGePoint2dArray]) -> AcadLWPolyline:
        return AcadLWPolyline(self._obj.AddLightWeightPolyline(VerticesList()))

    def AddLine(self, StartPoint: In[PyGePoint3d], 
                        EndPoint: In[PyGePoint3d]) -> AcadLine: 
        return AcadLine(self._obj.AddLine(StartPoint(), EndPoint()))

    def AddMInsertBlock(self, InsertionPoint: In[PyGePoint3d], 
                        Name: In[str], 
                        XScale: In[float], 
                        YScale: In[float], 
                        ZScale: In[float], 
                        Rotation: In[float], 
                        NumRows: In[int], 
                        NumColumns: In[int], 
                        RowSpacing: In[float], 
                        ColumnSpacing: In[float], 
                        Password: In[Variant] = vObjectEmpty) -> AcadMInsertBlock: 
        return AcadMInsertBlock(self._obj.AddMInsertBlock(InsertionPoint(), Name, XScale, YScale, ZScale, Rotation, NumRows, NumColumns, RowSpacing, ColumnSpacing, Password()))

    def AddMLeader(self, pointsArray: In[PyGePoint3dArray]) -> AcadMLeader: 
        return AcadMLeader(*self._obj.AddMLeader(pointsArray()))

    def AddMLine(self, VertexList: In[PyGePoint3dArray]) -> AcadMLine: 
        return AcadMLine(self._obj.AddMLine(VertexList()))

    def AddMText(self, InsertionPoint: In[PyGePoint3d], 
                        Width: In[float], 
                        Text: In[str]) -> AcadMtext: 
        return AcadMtext(self._obj.AddMText(InsertionPoint(), Width, Text))

    def AddPoint(self, Point: In[PyGePoint3d]) -> AcadPoint: 
        return AcadPoint(self._obj.AddPoint(Point()))

    def AddPolyfaceMesh(self, VerticesList: In[PyGePoint3dArray], 
                        FaceList: In[vShortArray]) -> AcadPolyfaceMesh: 
        return AcadPolyfaceMesh(self._obj.AddPolyfaceMesh(VerticesList(), FaceList()))

    def AddPolyline(self, VerticesList: In[PyGePoint3dArray]) -> AcadPolyline: 
        return AcadPolyline(self._obj.AddPolyline(VerticesList()))

    def AddRaster(self, ImageFileName: In[str], 
                        InsertionPoint: In[PyGePoint3d], 
                        ScaleFactor: In[float], 
                        RotationAngle: In[float]) -> AcadRasterImage: 
        return AcadRasterImage(self._obj.AddRaster(ImageFileName, InsertionPoint(), ScaleFactor, RotationAngle))

    def AddRay(self, Point1: In[PyGePoint3d], 
                        Point2: In[PyGePoint3d]) -> AcadRay: 
        return AcadRay(self._obj.AddRay(Point1(), Point2()))

    def AddRegion(self, ObjectList: In[vObjectArray[AcadArc|AcadCircle|AcadEllipse|AcadLine|AcadLWPolyline|AcadSpline]]) -> vObjectArray[AcadRegion]: 
        return vObjectArray([AcadRegion(region) for region in self._obj.AddRegion(ObjectList())])

    def AddRevolvedSolid(self, Profile: In[AcadRegion], 
                        AxisPoint: In[PyGePoint3d], 
                        AxisDir: In[PyGeVector3d], 
                        Angle: In[float]) -> Acad3DSolid: 
        return Acad3DSolid(self._obj.AddRevolvedSolid(Profile, AxisPoint(), AxisDir(), Angle))

    def AddSection(self, FromPoint: In[PyGePoint3d], 
                        ToPoint: In[PyGePoint3d], 
                        planeVector: In[PyGeVector3d]) -> AcadSection: 
        return AcadSection(self._obj.AddSection(FromPoint(), ToPoint(), planeVector()))

    def AddShape(self, Name: In[str], 
                        InsertionPoint: In[PyGePoint3d], 
                        ScaleFactor: In[float], 
                        Rotation: In[float]) -> AcadShape: 
        return AcadShape(self._obj.AddShape(Name, InsertionPoint(), ScaleFactor, Rotation))

    def AddSolid(self, Point1: In[PyGePoint3d], 
                        Point2: In[PyGePoint3d], 
                        Point3: In[PyGePoint3d], 
                        Point4: In[PyGePoint3d]) -> AcadSolid: 
        return AcadSolid(self._obj.AddSolid(Point1(), Point2(), Point3(), Point4()))

    def AddSphere(self, Center: In[PyGePoint3d], 
                        Radius: In[float]) -> Acad3DSolid: 
        return Acad3DSolid(self._obj.AddSphere(Center(), Radius))

    def AddSpline(self, PointsArray: In[PyGePoint3dArray], 
                        StartTangent: In[PyGeVector3d], 
                        EndTangent: In[PyGeVector3d]) -> AcadSpline: 
        return AcadSpline(self._obj.AddSpline(PointsArray(), StartTangent(), EndTangent()))

    def AddTable(self, InsertionPoint: In[PyGePoint3d], 
                        NumRows: In[int], 
                        NumColumns: In[int], 
                        RowHeight: In[float], 
                        ColWidth: In[float]) -> AcadTable: 
        return AcadTable(self._obj.AddTable(InsertionPoint(), NumRows, NumColumns, RowHeight, ColWidth))

    def AddText(self, TextString: In[str], 
                        InsertionPoint: In[PyGePoint3d], 
                        Height: In[float]) -> AcadText: 
        return AcadText(self._obj.AddText(TextString, InsertionPoint(), Height))

    def AddTolerance(self, Text: In[str], 
                        InsertionPoint: In[PyGePoint3d], 
                        Direction: In[PyGeVector3d]) -> AcadTolerance: 
        return AcadTolerance(self._obj.AddTolerance(Text, InsertionPoint(), Direction()))

    def AddTorus(self, Center: In[PyGePoint3d], 
                        TorusRadius: In[float], 
                        TubeRadius: In[float]) -> Acad3DSolid: 
        return Acad3DSolid(self._obj.AddTorus(Center(), TorusRadius, TubeRadius))

    def AddTrace(self, PointsArray: In[PyGePoint3dArray]) -> AcadTrace: 
        return AcadTrace(self._obj.AddTrace(PointsArray()))

    def AddWedge(self, Center: In[PyGePoint3d], 
                        Length: In[float], 
                        Width: In[float], 
                        Height: In[float]) -> Acad3DSolid: 
        return Acad3DSolid(self._obj.AddWedge(Center(), Length, Width, Height))

    def AddXline(self, Point1: In[PyGePoint3d], 
                        Point2: In[PyGePoint3d]) -> AcadXline: 
        return AcadXline(self._obj.AddXline(Point1(), Point2()))

    def AttachExternalReference(self,PathName: In[str], 
                        Name: In[str], 
                        InsertionPoint: In[PyGePoint3d], 
                        XScale: In[float],
                        YScale: In[float],
                        ZScale: In[float],
                        Rotation: In[float],
                        Overlay: In[bool],
                        Password: In[Variant] = vObjectEmpty) -> AcadExternalReference: 
        return AcadExternalReference(self._obj.AttachExternalReference(PathName, Name, InsertionPoint(), XScale, YScale, ZScale, Rotation, Overlay, Password()))

    def InsertBlock(self, InsertionPoint: In[PyGePoint3d], 
                        Name: In[str], 
                        Xscale: In[float] = 1.0, 
                        Yscale: In[float] = 1.0, 
                        ZScale: In[float] = 1.0, 
                        Rotation: In[float] = 0.0, 
                        Password: In[Variant] = vObjectEmpty) -> AcadBlockReference:
        return AcadBlockReference(self._obj.InsertBlock(InsertionPoint(), Name, Xscale, Yscale, ZScale, Rotation, Password()))

class AcadBlock(IAcadBlock):
    def __init__(self, obj) -> None: super().__init__(obj)

    BlockScaling: AcBlockScaling = proxy_property('AcBlockScaling','BlockScaling',AccessMode.ReadWrite)
    Comments: str = proxy_property(str,'Comments',AccessMode.ReadWrite)
    Explodable: bool = proxy_property(bool,'Explodable',AccessMode.ReadWrite)
    IsDynamicBlock: bool = proxy_property(bool,'IsDynamicBlock',AccessMode.ReadOnly)
    IsLayout: bool = proxy_property(bool,'IsLayout',AccessMode.ReadOnly)
    IsXRef: bool = proxy_property(bool,'IsXRef',AccessMode.ReadOnly)
    Layout: AcadLayout = proxy_property('AcadLayout','Layout',AccessMode.ReadWrite)
    Material: str = proxy_property(str,'Material',AccessMode.ReadWrite)
    Name: str = proxy_property(str,'Name',AccessMode.ReadOnly)
    Origin: PyGePoint3d = proxy_property('PyGePoint3d','Origin',AccessMode.ReadWrite)
    Path: str = proxy_property(str,'Path',AccessMode.ReadWrite)
    Units: AcInsertUnits = proxy_property('AcInsertUnits','Units',AccessMode.ReadWrite)
    XRefDatabase: AcadDatabase = proxy_property('AcadDatabase','XRefDatabase',AccessMode.ReadOnly)

    def Bind(self, bPrefixName: In[bool]) -> None:
        self._obj.Bind(bPrefixName)

    def Delete(self) -> None:
        self._obj.Delete()

    def Detach(self) -> None:
        self._obj.Detach()

    def Reload(self) -> None:
        self._obj.Reload()

    def Unload(self) -> None:
        self._obj.Unload()
