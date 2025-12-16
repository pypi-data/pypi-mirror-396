from __future__ import annotations
from ..Base import *
from ..Proxy import *
from ..AcadObject import *



class AcadSelectionSet(AppObject):
    def __init__(self, obj) -> None: super().__init__(obj)

    Application: AcadApplication = proxy_property('AcadApplication','Application',AccessMode.ReadOnly)
    Count: int = proxy_property(int,'Count',AccessMode.ReadOnly)
    Name: str = proxy_property(str,'Name',AccessMode.ReadOnly)

    def AddItems(self, Items: In[vObjectArray]) -> None:
        self._obj.AddItems(Items())

    def Clear(self) -> None:
        self._obj.Clear()

    def Delete(self) -> None:
        self._obj.Delete()

    def Erase(self) -> None:
        self._obj.Erase()

    def Highlight(self, HighlightFlag: In[bool]) -> None:
        self._obj.Highlight(HighlightFlag)

    def Item(self, Index: In[int|str]) -> AcadObject:
        return AcadObject(self._obj.Item(Index))

    def RemoveItems(self, Objects: In[vObjectArray]) -> None:
        self._obj.RemoveItems(Objects())

    def Select(self, Mode: In[AcSelect], Point1: In[PyGePoint3d] = None, Point2: In[PyGePoint3d] = None, FilterType: In[Variant[AdeskDxfCode]] = None, FilterData: In[Variant] = None) -> None:
        kwargs = {'Mode':Mode}
        if Point1 is not None: kwargs.update({'Point1':Point1()}) 
        if Point2 is not None: kwargs.update({'Point2':Point2()}) 
        if (FilterType is not None) and (FilterData is not None): kwargs.update({'FilterType':FilterType(),'FilterData':FilterData()}) 
        self._obj.Select(*kwargs)

    def SelectAtPoint(self, Point: In[PyGePoint3d], FilterType: In[Variant[AdeskDxfCode]] = None, FilterData: In[Variant] = None) -> None:
        kwargs = {'Point':Point()}
        if (FilterType is not None) and (FilterData is not None): kwargs.update({'FilterType':FilterType(),'FilterData':FilterData()}) 
        self._obj.SelectAtPoint(*kwargs)

    def SelectByPolygon(self, Mode: In[AcSelect], PointsList: In[PyGePoint3dArray], FilterType: In[Variant[AdeskDxfCode]] = None, FilterData: In[Variant] = None) -> None:
        kwargs = {'Mode':Mode,'PointsList':PointsList()}
        if (FilterType is not None) and (FilterData is not None): kwargs.update({'FilterType':FilterType(),'FilterData':FilterData()}) 
        self._obj.SelectByPolygon(*kwargs)

    def SelectOnScreen(self, FilterType: In[Variant[AdeskDxfCode]] = None, FilterData: In[Variant] = None) -> None:
        if (FilterType is not None) and (FilterData is not None):
            self._obj.SelectOnScreen(FilterType(), FilterData())
        else:
            self._obj.SelectOnScreen()

    def Update(self) -> None:
        self._obj.Update()