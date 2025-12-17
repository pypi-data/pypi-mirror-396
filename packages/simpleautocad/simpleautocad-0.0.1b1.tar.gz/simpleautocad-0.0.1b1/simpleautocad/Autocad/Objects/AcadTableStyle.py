from __future__ import annotations
from ..Base import *
from ..Proxy import *
from ..AcadObject import *

class AcadTableStyle(AcadObject):
    def __init__(self, obj) -> None: super().__init__(obj)
    
    BitFlags: int = proxy_property(int,'BitFlags',AccessMode.ReadWrite)
    Description: str = proxy_property(str,'Description',AccessMode.ReadWrite)
    FlowDirection: AcTableDirection = proxy_property('AcTableDirection','FlowDirection',AccessMode.ReadWrite)
    HeaderSuppressed: bool = proxy_property(bool,'HeaderSuppressed',AccessMode.ReadWrite)
    HorzCellMargin: float = proxy_property(float,'HorzCellMargin',AccessMode.ReadWrite)
    Name: str = proxy_property(str,'Name',AccessMode.ReadWrite)
    NumCellStyles: int = proxy_property(int,'NumCellStyles',AccessMode.ReadOnly)
    TemplateId: int = proxy_property(int,'TemplateId',AccessMode.ReadWrite)
    TitleSuppressed: bool = proxy_property(bool,'TitleSuppressed',AccessMode.ReadWrite)
    VertCellMargin: float = proxy_property(float,'VertCellMargin',AccessMode.ReadWrite)

    def CreateCellStyle(self, StringCellStyle: In[str]) -> None:
        self._obj.CreateCellStyle(StringCellStyle)

    def CreateCellStyleFromStyle(self, StringCellStyle: In[str], StringSourceCellStyle: In[str]) -> None:
        self._obj.CreateCellStyleFromStyle(StringCellStyle, StringSourceCellStyle)

    def DeleteCellStyle(self, StringCellStyle: In[str]) -> None:
        self._obj.DeleteCellStyle(StringCellStyle)

    def EnableMergeAll(self, nRow: In[int], nCol: In[int], bEnable: In[bool]) -> None:
        self._obj.EnableMergeAll(nRow, nCol, bEnable)

    def GetAlignment(self, rowType: In[AcRowType]) -> AcCellAlignment:
        return AcCellAlignment(self._obj.GetAlignment(rowType))

    def GetAlignment2(self, bstrCellStyle: In[str]) -> AcCellAlignment:
        return AcCellAlignment(self._obj.GetAlignment2(bstrCellStyle))

    def GetBackgroundColor(self, rowType: In[AcRowType]) -> AcadAcCmColor:
        return AcadAcCmColor(self._obj.GetBackgroundColor(rowType))

    def GetBackgroundColor2(self, bstrCellStyle: In[str]) -> AcadAcCmColor:
        return AcadAcCmColor(self._obj.GetBackgroundColor2(bstrCellStyle))

    def GetBackgroundColorNone(self, rowType: In[AcRowType]) -> bool:
        return self._obj.GetBackgroundColorNone(rowType)

    def GetCellClass(self, StringCellStyle: In[str]) -> int:
        return self._obj.GetCellClass(StringCellStyle)

    def GetCellStyles(self) -> Variant:
        cellStylesArray = self._obj.GetCellStyles()
        return Variant(cellStylesArray)

    def GetColor(self, rowType: In[AcRowType]) -> AcadAcCmColor:
        return AcadAcCmColor(self._obj.GetColor(rowType))

    def GetColor2(self, bstrCellStyle: In[str]) -> AcadAcCmColor:
        return AcadAcCmColor(self._obj.GetColor2(bstrCellStyle))

    def GetDataType(self, rowType: In[AcRowType]) -> tuple:
        pDataType, pUnitType = self._obj.GetDataType(rowType)
        return AcValueDataType(pDataType), AcValueUnitType(pUnitType)

    def GetDataType2(self, nRow: In[int], nCol: In[int], nContent: In[int]) -> tuple:
        pDataType, pUnitType = self._obj.GetDataType2(nRow, nCol, nContent)
        return AcValueDataType(pDataType), AcValueUnitType(pUnitType)

    def GetFormat(self, rowType: In[AcRowType]) -> str:
        return self._obj.GetFormat(rowType)

    def GetFormat2(self, StringCellStyle: In[str]) -> str:
        pbstrFormat = self._obj.GetFormat2(StringCellStyle)
        return pbstrFormat

    def GetGridColor(self, gridLineType: In[AcGridLineType], rowType: In[AcRowType]) -> AcadAcCmColor:
        return AcadAcCmColor(self._obj.GetGridColor(gridLineType, rowType))

    def GetGridColor2(self, bstrCellStyle: In[str], gridLineType: In[AcGridLineType]) -> AcadAcCmColor:
        return AcadAcCmColor(self._obj.GetGridColor2(bstrCellStyle, gridLineType))

    def GetGridLineWeight(self, gridLineType: In[AcGridLineType], rowType: In[AcRowType]) -> AcLineWeight:
        return AcLineWeight(self._obj.GetGridLineWeight(gridLineType, rowType))

    def GetGridLineWeight2(self, nRow: In[int], nCol: In[int], nGridLineType: In[AcGridLineType]) -> AcLineWeight:
        return AcLineWeight(self._obj.GetGridLineWeight2(nRow, nCol, nGridLineType))

    def GetGridVisibility(self, gridLineType: In[AcGridLineType], rowType: In[AcRowType]) -> bool:
        return self._obj.GetGridVisibility(gridLineType, rowType)

    def GetGridVisibility2(self, nRow: In[int], nCol: In[int], nGridLineType: In[AcGridLineType]) -> bool:
        return self._obj.GetGridVisibility2(nRow, nCol, nGridLineType)

    def GetIsCellStyleInUse(self, pszCellStyle: In[str]) -> bool:
        return self._obj.GetIsCellStyleInUse(pszCellStyle)

    def GetIsMergeAllEnabled(self, StringCellStyle: In[str]) -> bool:
        return self._obj.GetIsMergeAllEnabled(StringCellStyle)

    def GetRotation(self, StringCellStyle: In[str]) -> float:
        return self._obj.GetRotation(StringCellStyle)

    def GetTextHeight(self, rowType: In[AcRowType]) -> float:
        return self._obj.GetTextHeight(rowType)

    def GetTextHeight2(self, StringCellStyle: In[str]) -> float:
        return self._obj.GetTextHeight2(StringCellStyle)

    def GetTextStyle(self, rowType: In[AcRowType]) -> str:
        return self._obj.GetTextStyle(rowType)

    def GetTextStyleId(self, bstrCellStyle: In[str]) -> float:
        return self._obj.GetTextStyleId(bstrCellStyle)

    def GetUniqueCellStyleName(self, pszBaseName: In[str]) -> str:
        return self._obj.GetUniqueCellStyleName(pszBaseName)

    def RenameCellStyle(self, StringOldName: In[str], StringNewName: In[str]) -> None:
        self._obj.RenameCellStyle(StringOldName, StringNewName)

    def SetAlignment(self, rowTypes: In[AcRowType], cellAlignment: In[AcCellAlignment]) -> None:
        self._obj.SetAlignment(rowTypes, cellAlignment)

    def SetAlignment2(self, bstrCellStyle: In[str], cellAlignment: In[AcCellAlignment]) -> None:
        self._obj.SetAlignment2(bstrCellStyle, cellAlignment)

    def SetBackgroundColor(self, rowTypes: In[AcRowType], pColor: In[AcadAcCmColor]) -> None:
        self._obj.SetBackgroundColor(rowTypes, pColor())

    def SetBackgroundColor2(self, bstrCellStyle: In[str], color: In[AcadAcCmColor]) -> None:
        self._obj.SetBackgroundColor2(bstrCellStyle, color())

    def SetBackgroundColorNone(self, rowTypes: In[AcRowType], bValue: In[bool]) -> None:
        self._obj.SetBackgroundColorNone(rowTypes, bValue)

    def SetCellClass(self, StringCellStyle: In[str], cellClass: In[int]) -> None:
        self._obj.SetCellClass(StringCellStyle, cellClass)

    def SetColor(self, rowTypes: In[AcRowType], pColor: In[AcadAcCmColor]) -> None:
        self._obj.SetColor(rowTypes, pColor())

    def SetColor2(self, bstrCellStyle: In[str], color: In[AcadAcCmColor]) -> None:
        self._obj.SetColor2(bstrCellStyle, color())

    def SetDataType(self, rowTypes: In[AcRowType], nDataType: In[AcValueDataType], nUnitType: In[AcValueUnitType]) -> None:
        self._obj.SetDataType(rowTypes, nDataType, nUnitType)

    def SetDataType2(self, nRow: In[int], nCol: In[int], nContent: In[int], dataType: In[AcValueDataType], unitType: In[AcValueUnitType]) -> None:
        self._obj.SetDataType2(nRow, nCol, nContent, dataType, unitType)

    def SetFormat(self, rowTypes: In[AcRowType], pFormat: In[str]) -> None:
        self._obj.SetFormat(rowTypes, pFormat)

    def SetFormat2(self, bstrCellStyle: In[str], bstrFormat: In[str]) -> None:
        self._obj.SetFormat2(bstrCellStyle, bstrFormat)

    def SetGridColor(self, gridLineTypes: In[AcGridLineType], rowTypes: In[AcRowType], pColor: In[AcadAcCmColor]) -> None:
        self._obj.SetGridColor(gridLineTypes, rowTypes, pColor())

    def SetGridColor2(self, nRow: In[int], nCol: In[int], nGridLineType: In[AcGridLineType], pColor: In[AcadAcCmColor]) -> None:
        self._obj.SetGridColor2(nRow, nCol, nGridLineType, pColor())

    def SetGridLineWeight(self, gridLineTypes: In[AcGridLineType], rowTypes: In[AcRowType], Lineweight: In[AcLineWeight]) -> None:
        self._obj.SetGridLineWeight(gridLineTypes, rowTypes, Lineweight)

    def SetGridLineWeight2(self, bstrCellStyle: In[str], gridLineType: In[AcGridLineType], Lineweight: In[AcLineWeight]) -> None:
        self._obj.SetGridLineWeight2(bstrCellStyle, gridLineType, Lineweight)

    def SetGridVisibility(self, gridLineTypes: In[AcGridLineType], rowTypes: In[AcRowType], bVisible: In[bool]) -> None:
        self._obj.SetGridVisibility(gridLineTypes, rowTypes, bVisible)

    def SetGridVisibility2(self, bstrCellStyle: In[str], gridLineType: In[AcGridLineType], bValue: In[bool]) -> None:
        self._obj.SetGridVisibility2(bstrCellStyle, gridLineType, bValue)

    def SetRotation(self, bstrCellStyle: In[str], Rotation: In[float]) -> None:
        self._obj.SetRotation(bstrCellStyle, Rotation)

    def SetTemplateId(self, val: In[int], option: In[AcMergeCellStyleOption]) -> None:
        self._obj.SetTemplateId(val, option)

    def SetTextHeight(self, rowTypes: In[AcRowType], TextHeight: In[float]) -> None:
        self._obj.SetTextHeight(rowTypes, TextHeight)

    def SetTextHeight2(self, bstrCellStyle: In[str], Height: In[float]) -> None:
        self._obj.SetTextHeight2(bstrCellStyle, Height)

    def SetTextStyle(self, rowTypes: In[AcRowType], bstrName: In[str]) -> None:
        self._obj.SetTextStyle(rowTypes, bstrName)

    def SetTextStyleId(self, bstrCellStyle: In[str], val: In[int]) -> None:
        self._obj.SetTextStyleId(bstrCellStyle, val)