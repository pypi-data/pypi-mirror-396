from __future__ import annotations
from ..Base import *
from ..Proxy import *
from ..AcadObject import *

class AcadUtility(AppObject):
    def __init__(self, obj) -> None: super().__init__(obj)

    def AngleFromXAxis(self, Point1: In[PyGePoint3d], Point2: In[PyGePoint3d]) -> float:
        return self._obj.AngleFromXAxis(Point1(), Point2())
        
    def AngleToReal(self, Angle: In[str], Unit: In[AcAngleUnits]) -> float:
        return self._obj.AngleToReal(Angle, Unit)
        
    def AngleToString(self, Angle: In[float], Unit: In[AcAngleUnits], Precision: In[int]) -> str:
        return self._obj.AngleToString(Angle, Unit, Precision)
        
    def CreateTypedArray(self, Type: In[VbVarType], Value1, *args):
        VarArr = vObjectEmpty
        self._obj.CreateTypedArray(VarArr, Type, Value1, *args)
        return VarArr
        
    def DistanceToReal(self, Distance: In[str], Unit: In[AcUnits]) -> float:
        return self._obj.DistanceToReal(Distance, Unit)

    def GetAngle(self, Point: In[PyGePoint3d] = None, Prompt: In[str] = '') -> float:
        if Point is None:
            return self._obj.GetAngle()
        return self._obj.GetAngle(Point(),Prompt)

    def GetCorner(self, Point: In[PyGePoint3d], Prompt: In[str] = '') -> tuple:
        return self._obj.GetCorner(Point(), Prompt)
        
    def GetDistance(self, Point: In[PyGePoint3d] = None, Prompt: In[str] = None) -> float:
        return self._obj.GetDistance(Point(), Prompt)
        
    def GetEntity(self, Prompt: In[str] = '') -> tuple: #Object: Out[AppObject], PickedPoint: Out[VARIANT], 
        Object, PickedPoint = self._obj.GetEntity()
        return Object, PickedPoint
        
    def GetInput(self) -> str: 
        return self._obj.GetInput()

    def GetInteger(self, Prompt: In[str] = '') -> int: 
        return self._obj.GetInteger(Prompt)
        
    def GetKeyword(self, Prompt: In[str] = '') -> str: 
        return self._obj.GetKeyword(Prompt)

    def GetObjectIdString(self, acadObject: In[AcadObject], bHex: In[bool]) -> str: 
        return self._obj.GetObjectIdString(acadObject(), int(bHex))
        
    def GetOrientation(self, Point: In[PyGePoint3d], Prompt: In[str] = '') -> float: 
        return self._obj.GetOrientation(Point(), Prompt)
        
    def GetPoint(self, Point: In[PyGePoint3d] = None, Prompt: In[str] = '') -> tuple: 
        if Point is None:
            return PyGePoint3d(self._obj.GetPoint())
        return PyGePoint3d(self._obj.GetPoint(Point, Prompt))

    def GetReal(self, Prompt: In[str] = '') -> float: 
        return self._obj.GetReal(Prompt)
        
    def GetRemoteFile(self, URL: In[str], IgnoreCache: In[bool]) -> None:
        LocalFile: str = ''
        self._obj.GetRemoteFile(URL, LocalFile, IgnoreCache)
        return LocalFile

    def GetString(self, HasSpaces : In[int], Prompt: In[str] = '') -> float: 
        return self._obj.GetString(HasSpaces, Prompt)
        
    def GetSubEntity(self, Prompt: In[str] = '') -> tuple: 
        Object = None
        PickedPoint = None
        TransMatrix = None
        ContextData = None
        Object, PickedPoint, TransMatrix, ContextData = self._obj.GetSubEntity()
        return Object, PickedPoint, TransMatrix, ContextData

    def InitializeUserInput(self, Bits : In[int], Keyword: In[str] = None) -> None: 
        if Keyword:
            self._obj.InitializeUserInput(Bits, Keyword)
        else:
            self._obj.InitializeUserInput(Bits)

    def IsRemoteFile(self, LocalFile : In[str], URL: In[str]) -> bool: 
        return self._obj.IsRemoteFile(LocalFile, URL)

    def IsURL(self, URL: In[str]) -> bool: 
        return self._obj.IsURL(URL)

    def LaunchBrowserDialog(self, DialogTitle: In[str], OpenButtonCaption: In[str], StartPageURL: In[str], RegistryRootKey: In[str], OpenButtonAlwaysEnabled: In[bool]) -> bool: 
        SelectedURL:str = ''
        return self._obj.LaunchBrowserDialog(SelectedURL, DialogTitle, OpenButtonCaption, StartPageURL, RegistryRootKey, OpenButtonAlwaysEnabled)
        return SelectedURL

    def PolarPoint(self, Point: In[PyGePoint3d], Angle: In[float], Distance: In[float]) -> PyGePoint3d: 
        return PyGePoint3d(self._obj.PolarPoint(Point(), Angle, Distance))

    def Prompt(self, Message: In[str]) -> None: 
        self._obj.Prompt(Message)

    def PutRemoteFile(self, URL: In[str], LocalFile: In[str]) -> None: 
        self._obj.PutRemoteFile(URL, LocalFile)
        
    def RealToString(self, Value: In[float], Unit: In[AcUnits], Precision: In[int]) -> str: 
        return self._obj.RealToString(Value, Unit, Precision)
        
    def SendModelessOperationEnded(self) -> str: 
        Context = self._obj.SendModelessOperationEnded()
        return Context
        
    def SendModelessOperationStart(self, Context: In[str]) -> None: 
        self._obj.SendModelessOperationStart(Context)
        
    def TranslateCoordinates(self, Point: In[PyGePoint3d], FromCoordSystem: In[AcCoordinateSystem], ToCoordSystem: In[AcCoordinateSystem], Displacement: In[int], OCSNormal: In[PyGeVector3d] = None) -> tuple: 
        if OCSNormal:
            return self._obj.TranslateCoordinates(Point(), FromCoordSystem, ToCoordSystem, Displacement, OCSNormal())
        return self._obj.TranslateCoordinates(Point(), FromCoordSystem, ToCoordSystem, Displacement, OCSNormal)

class VbVarType(IntEnum):
    vbBoolean = 11
    vbInteger = 2
    vbLong = 3
    vbSingle = 4
    vbDouble = 5
    # vbEmpty = 0
    # vbNull = 1
    # vbString = 8
    # vbObject = 9
    # vbArray = 8192
    # vbCurrency = 6
    # vbDate = 7
    # vbError = 10