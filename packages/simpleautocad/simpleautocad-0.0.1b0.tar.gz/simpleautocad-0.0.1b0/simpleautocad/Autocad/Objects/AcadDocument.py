from __future__ import annotations
from ..Base import *
from ..Proxy import *
from .AcadDatabase import AcadDatabase, IAcadDatabase
from .AcadUCS import AcadUCS



class AcadDocument(AcadDatabase):
    def __init__(self, obj) -> None: super().__init__(obj)

    Active: bool = proxy_property(bool,'Active',AccessMode.ReadOnly)
    ActiveDimStyle: AcadDimStyle = proxy_property('AcadDimStyle','ActiveDimStyle',AccessMode.ReadWrite)
    ActiveLayer: AcadLayer = proxy_property('AcadLayer','ActiveLayer',AccessMode.ReadWrite)
    ActiveLayout: AcadLayout = proxy_property('AcadLayout','ActiveLayout',AccessMode.ReadWrite)
    ActiveLinetype: AcadLineType = proxy_property('AcadLineType','ActiveLinetype',AccessMode.ReadWrite)
    ActiveMaterial: AcadMaterial = proxy_property('AcadMaterial','ActiveMaterial',AccessMode.ReadWrite)
    ActivePViewport: AcadPViewport = proxy_property('AcadPViewport','ActivePViewport',AccessMode.ReadWrite)
    ActiveSelectionSet: AcadSelectionSet = proxy_property('AcadSelectionSet','ActiveSelectionSet',AccessMode.ReadOnly)
    ActiveSpace: AcActiveSpace = proxy_property('AcActiveSpace','ActiveSpace',AccessMode.ReadWrite)
    ActiveTextStyle: AcadTextStyle = proxy_property('AcadTextStyle','ActiveTextStyle',AccessMode.ReadWrite)
    ActiveUCS: AcadUCS = proxy_property('AcadUCS','ActiveUCS',AccessMode.ReadWrite)
    ActiveViewport: AcadViewport = proxy_property('AcadViewport','ActiveViewport',AccessMode.ReadWrite)
    Application: AcadApplication = proxy_property('AcadApplication','Application',AccessMode.ReadOnly)
    Database: IAcadDatabase = proxy_property('IAcadDatabase','Database',AccessMode.ReadOnly)
    FullName: str = proxy_property(str,'FullName',AccessMode.ReadOnly)
    Height: float = proxy_property(float,'Height',AccessMode.ReadWrite)
    HWND: int = proxy_property(int,'HWND',AccessMode.ReadOnly)
    MSpace: bool = proxy_property(bool,'MSpace',AccessMode.ReadWrite)
    Name: str = proxy_property(str,'Name',AccessMode.ReadOnly)
    ObjectSnapMode: bool = proxy_property(bool,'ObjectSnapMode',AccessMode.ReadWrite)
    Path: str = proxy_property(str,'Path',AccessMode.ReadOnly)
    PickfirstSelectionSet: AcadSelectionSet = proxy_property('AcadSelectionSet','PickfirstSelectionSet',AccessMode.ReadOnly)
    Plot: AcadPlot = proxy_property('AcadPlot','Plot',AccessMode.ReadOnly)
    ReadOnly: bool = proxy_property(bool,'ReadOnly',AccessMode.ReadOnly)
    Saved: bool = proxy_property(bool,'Saved',AccessMode.ReadOnly)
    SelectionSets: AcadSelectionSet = proxy_property('AcadSelectionSet','SelectionSets',AccessMode.ReadOnly)
    SummaryInfo: AcadSummaryInfo = proxy_property('AcadSummaryInfo','SummaryInfo',AccessMode.ReadOnly)
    Utility: AcadUtility = proxy_property('AcadUtility','Utility',AccessMode.ReadOnly)
    Width: float = proxy_property(float,'Width',AccessMode.ReadWrite)
    WindowState: AcWindowState = proxy_property('AcWindowState','WindowState',AccessMode.ReadWrite)
    WindowTitle: str = proxy_property(str,'WindowTitle',AccessMode.ReadOnly)

    def Activate(self) -> None: 
        self._obj.Activate()

    def AuditInfo(self, FixError: In[bool]) -> None: 
        self._obj.AuditInfo(FixError)

    def Close(self, SaveChanges: In[bool] = False, FileName: In[str] = '') -> None: 
        self._obj.Close(SaveChanges, FileName)

    def EndUndoMark(self) -> None: 
        self._obj.EndUndoMark()

    def Export(self, FileName: In[str], Extension: In[str], SelectionSet: In[AcadSelectionSet]) -> None: 
        self._obj.Export(FileName, Extension, SelectionSet)

    def GetVariable(self, Name: In[str]) -> any: 
        return self._obj.GetVariable(Name)

    def Import(self, FileName: In[str], InsertionPoint: In[PyGePoint3d], ScaleFactor: In[float]) -> AcadBlockReference | None: 
        ref = self._obj.Import(FileName, InsertionPoint(), ScaleFactor)
        return AcadBlockReference(ref) if ref else None

    def LoadShapeFile(self, FullName: In[str]) -> None: 
        self._obj.LoadShapeFile(FullName)

    def New(self, TemplateFileName: In[str]) -> AcadDocument: 
        return AcadDocument(self._obj.New(TemplateFileName))

    def Open(self, Name: In[str], ReadOnly: In[bool] = False) -> AcadDocument: # Password: In[Variant] = None
        return self._obj.Open(Name, ReadOnly)

    def PostCommand(self, Command: In[str]) -> None: 
        self._obj.PostCommand(Command)

    def PurgeAll(self) -> None: 
        self._obj.PurgeAll()
        
    def Regen(self, WhichViewports: In[AcRegenType]) -> None: 
        self._obj.Regen(WhichViewports)

    def Save(self) -> None: 
        self._obj.Save()

    def SaveAs(self, FileName: In[str], FileType: In[AcSaveAsType] = AcSaveAsType.acNative, SecurityParams: In[AcadSecurityParams] = None) -> None: 
        if SecurityParams is None:
            self._obj.SaveAs(FileName, FileType)
        else:
            raise Exception('AcadSecurityParams не поддерживается') 
            self._obj.SaveAs(FileName, FileType, SecurityParams)

    def SendCommand(self, Command: In[str]) -> None: 
        self._obj.SendCommand(Command)

    def SetVariable(self, Name: In[str], Value: In[Variant]) -> None: 
        self._obj.SetVariable(Name, Value())

    def StartUndoMark(self) -> None: 
        self._obj.StartUndoMark()

    def WBlock(self, FileName: In[str], SelectionSet: In[AcadSelectionSet]) -> None: 
        self._obj.WBlock(FileName, SelectionSet)

