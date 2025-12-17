from __future__ import annotations
from ..Base import *
from ..Proxy import *
from ..AcadEntity import AcadEntity



class AcadTable(AcadEntity):
    def __init__(self, obj) -> None: super().__init__(obj)

    AllowManualHeights: bool = proxy_property(bool,'AllowManualHeights',AccessMode.ReadWrite)
    AllowManualPositions: bool = proxy_property(bool,'AllowManualPositions',AccessMode.ReadWrite)
    BreaksEnabled: bool = proxy_property(bool,'BreaksEnabled',AccessMode.ReadWrite)
    BreakSpacing: float = proxy_property(float,'BreakSpacing',AccessMode.ReadWrite)
    Columns: int = proxy_property(int,'Columns',AccessMode.ReadWrite)
    ColumnWidth: float = proxy_property(float,'ColumnWidth',AccessMode.ReadWrite)
    Direction: PyGeVector3d = proxy_property(PyGeVector3d,'Direction',AccessMode.ReadWrite)
    EnableBreak: bool = proxy_property(bool,'EnableBreak',AccessMode.ReadWrite)
    FlowDirection: AcTableDirection = proxy_property('AcTableDirection','FlowDirection',AccessMode.ReadWrite)
    HasSubSelection: bool = proxy_property(bool,'HasSubSelection',AccessMode.ReadWrite)
    HeaderSuppressed: bool = proxy_property(bool,'HeaderSuppressed',AccessMode.ReadWrite)
    Height: float = proxy_property(float,'Height',AccessMode.ReadWrite)
    HorzCellMargin: float = proxy_property(float,'HorzCellMargin',AccessMode.ReadWrite)
    InsertionPoint: PyGePoint3d = proxy_property('PyGePoint3d','InsertionPoint',AccessMode.ReadWrite)
    MinimumTableHeight: float = proxy_property(float,'MinimumTableHeight',AccessMode.ReadOnly)
    MinimumTableWidth: float = proxy_property(float,'MinimumTableWidth',AccessMode.ReadOnly)
    RegenerateTableSuppressed: bool = proxy_property(bool,'RegenerateTableSuppressed',AccessMode.ReadWrite)
    RepeatBottomLabels: bool = proxy_property(bool,'RepeatBottomLabels',AccessMode.ReadWrite)
    RowHeight: float = proxy_property(float,'RowHeight',AccessMode.ReadWrite)
    Rows: int = proxy_property(int,'Rows',AccessMode.ReadWrite)
    StyleName: str = proxy_property(str,'StyleName',AccessMode.ReadWrite)
    TableBreakFlowDirection: AcTableFlowDirection = proxy_property('AcTableFlowDirection','TableBreakFlowDirection',AccessMode.ReadWrite)
    TableBreakHeight: float = proxy_property(float,'TableBreakHeight',AccessMode.ReadWrite)
    TableStyleOverrides: AcTableStyleOverrides = proxy_property('AcTableStyleOverrides','TableBreakHeight',AccessMode.ReadWrite)
    TitleSuppressed: bool = proxy_property(bool,'TitleSuppressed',AccessMode.ReadWrite)
    VertCellMargin: float = proxy_property(float,'VertCellMargin',AccessMode.ReadWrite)
    Width: float = proxy_property(float,'Width',AccessMode.ReadWrite)

    def ClearSubSelection(self) -> None:
        self._obj.ClearSubSelection()
        
    def ClearTableStyleOverrides(self, flag: In[int]) -> None:
        self._obj.ClearTableStyleOverrides(flag)
        
    def Copy(self, flag: In[int]) -> AcadTable:
        return AcadTable(self._obj.Copy(flag))
            
    def CreateContent(self, nRow: In[int], nCol: In[int], nIndex: In[int]) -> int:
        return self._obj.CreateContent(nRow, nCol, nIndex)
        
    def DeleteCellContent(self, row: In[int], col: In[int]) -> None:
        self._obj.DeleteCellContent(row, col)
        
    def DeleteColumns(self, col: In[int], cols: In[int]) -> None:
        self._obj.DeleteColumns(col, cols)

    def DeleteContent(self, nRow: In[int], nCol: In[int]) -> None:
        self._obj.DeleteContent(nRow, nCol)

    def DeleteRows(self, row: In[int], Rows: In[int]) -> None:
        self._obj.DeleteContent(row, Rows)

    def EnableMergeAll(self, nRow: In[int], nCol: In[int], bEnable: In[bool]) -> None:
        self._obj.EnableMergeAll(nRow, nCol, bEnable)

    def FormatValue(self, row: In[int], col: In[int], nOption: In[AcFormatOption]) -> str:
        return self._obj.FormatValue(row, col, nOption)

    def GenerateLayout(self) -> None:
        self._obj.GenerateLayout()

    def GetAlignment(self, rowType: In[AcRowType]) -> AcCellAlignment:
        return AcCellAlignment(self._obj.GetAlignment(rowType))

    def GetAttachmentPoint(self, row: In[int], col: In[int]) -> AcAttachmentPoint:
        return AcAttachmentPoint(self._obj.GetAttachmentPoint(row, col))

    def GetAutoScale(self, row: In[int], col: In[int]) -> bool:
        return self._obj.GetAutoScale(row, col)

    def GetAutoScale2(self, nRow: In[int], nCol: In[int], nContent: In[int]) -> bool:
        return self._obj.GetAutoScale2(nRow, nCol, nContent)

    def GetBackgroundColor(self, rowType: In[AcRowType]) -> AcadAcCmColor:
        return AcadAcCmColor(self._obj.GetBackgroundColor(rowType))

    def GetBackgroundColorNone(self, rowType: In[AcRowType]) -> bool:
        return self._obj.GetBackgroundColorNone(rowType)

    def GetBlockAttributeValue(self, row: In[int], col: In[int], attdefId: In[int]) -> str:
        return self._obj.GetBlockAttributeValue(row, col, attdefId)

    def GetBlockAttributeValue2(self, nRow: In[int], nCol: In[int], nContent: In[int], blkId: In[int]) -> str:
        return self._obj.GetBlockAttributeValue2(nRow, nCol, nContent, blkId)

    def GetBlockRotation(self, row: In[int], col: In[int]) -> float:
        return self._obj.GetBlockRotation(row, col)

    def GetBlockScale(self, row: In[int], col: In[int]) -> float:
        return self._obj.GetBlockScale(row, col)

    def GetBlockTableRecordId(self, row: In[int], col: In[int]) -> int:
        return self._obj.GetBlockTableRecordId(row, col)

    def GetBlockTableRecordId2(self, nRow: In[int], nCol: In[int], nContent: In[int]) -> int:
        return self._obj.GetBlockTableRecordId2(nRow, nCol, nContent)

    def GetBreakHeight(self, nIndex: In[int]) -> float:
        return self._obj.GetBreakHeight(nIndex)

    def GetCellAlignment(self, row: In[int], col: In[int]) -> AcCellAlignment:
        return AcCellAlignment(self._obj.GetCellAlignment(row, col))

    def GetCellBackgroundColor(self, row: In[int], col: In[int]) -> AcadAcCmColor:
        return AcadAcCmColor(self._obj.GetCellBackgroundColor(row, col))

    def GetCellBackgroundColorNone(self, row: In[int], col: In[int]) -> bool:
        return self._obj.GetCellBackgroundColorNone(row, col)

    def GetCellContentColor(self, row: In[int], col: In[int]) -> AcadAcCmColor:
        return AcadAcCmColor(self._obj.GetCellContentColor(row, col))

    def GetCellDataType(self, row: In[int], col: In[int], pDataType: In[AcValueDataType], pUnitType: In[AcValueUnitType]) -> None:
        self._obj.GetCellDataType(row, col, pDataType, pUnitType)

    def GetCellExtents(self, row: In[int], col: In[int], bOuterCell: In[bool]) -> None:
        self._obj.GetCellExtents(row, col, bOuterCell)

    def GetCellFormat(self, row: In[int], col: In[int]) -> str:
        return self._obj.GetCellFormat(row, col)

    def GetCellGridColor(self, row: In[int], col: In[int], edge: In[AcCellEdgeMask]) -> AcadAcCmColor:
        return AcadAcCmColor(self._obj.GetCellGridColor(row, col, edge))

    def GetCellGridLineWeight(self, row: In[int], col: In[int], edge: In[AcCellEdgeMask]) -> AcLineWeight:
        return AcLineWeight(self._obj.GetCellGridLineWeight(row, col, edge))

    def GetCellGridVisibility(self, row: In[int], col: In[int], edge: In[AcCellEdgeMask]) -> bool:
        return self._obj.GetCellGridVisibility(row, col, edge)

    def GetCellState(self, nRow: In[int], nCol: In[int]) -> AcCellState:
        return AcCellState(self._obj.GetCellState(nRow, nCol))

    def GetCellStyle(self, nRow: In[int], nCol: In[int]) -> str:
        return self._obj.GetCellStyle(nRow, nCol)

    def GetCellStyleOverrides(self, row: In[int], col: In[int]) -> str:
        return self._obj.GetCellStyleOverrides(row, col)

    def GetCellTextHeight(self, row: In[int], col: In[int]) -> float:
        return self._obj.GetCellTextHeight(row, col)

    def GetCellTextStyle(self, row: In[int], col: In[int]) -> str:
        return self._obj.GetCellTextStyle(row, col)

    def GetCellType(self, row: In[int], col: In[int]) -> AcCellType:
        return AcCellType(self._obj.GetCellType(row, col))

    def GetCellValue(self, row: In[int], col: In[int]) -> Variant:
        return Variant(self._obj.GetCellValue(row, col))

    def GetColumnName(self, nIndex: In[int]) -> str:
        return self._obj.GetColumnName(nIndex)

    def GetColumnWidth(self, col: In[int]) -> float:
        return self._obj.GetColumnWidth(col)

    def GetContentColor(self, rowType: In[AcRowType]) -> AcadAcCmColor:
        return AcadAcCmColor(self._obj.GetContentColor(rowType))

    def GetCellContentColor2(self, nRow: In[int], nCol: In[int], nContent: In[int]) -> AcadAcCmColor:
        return AcadAcCmColor(self._obj.GetCellContentColor2(nRow, nCol, nContent))

    def GetContentLayout(self, nRow: In[int], nCol: In[int]) -> AcCellContentLayout:
        return AcCellContentLayout(self._obj.GetContentLayout(nRow, nCol))

    def GetContentType(self, nRow: In[int], nCol: In[int]) -> AcCellContentType:
        return AcCellContentType(self._obj.GetContentType(nRow, nCol))

    def GetCustomData(self, nRow: In[int], nCol: In[int], szKey: In[str]) -> Variant:
        pData = self._obj.GetCustomData(nRow, nCol, szKey)
        return Variant(pData)

    def GetDataFormat(self, nRow: In[int], nCol: In[int], nContent: In[int]) -> str:
        return self._obj.GetDataFormat(nRow, nCol, nContent)
    
    def GetDataType(self, rowType: In[AcRowType]) -> tuple[AcValueDataType,AcValueUnitType]:
        pDataType, pUnitType = self._obj.GetDataType(rowType)
        return AcValueDataType(pDataType), AcValueUnitType(pUnitType)
        
    def GetDataType2(self, nRow: In[int], nCol: In[int], nContent: In[int]) -> tuple[AcValueDataType,AcValueUnitType]:
        pDataType, pUnitType = self._obj.GetDataType2(nRow, nCol, nContent)
        return AcValueDataType(pDataType), AcValueUnitType(pUnitType)
    
    def GetFieldId(self, row: In[int], col: In[int]) -> int:
        return self._obj.GetFieldId(row, col)
    
    def GetFieldId2(self, nRow: In[int], nCol: In[int], nContent: In[int]) -> int:
        return self._obj.GetFieldId2(nRow, nCol, nContent)

    def GetFormat(self, rowType: In[AcRowType]) -> str:
        return self._obj.GetFormat(rowType)

    def GetFormula(self, nRow: In[int], nCol: In[int], nContent: In[int]) -> str:
        return self._obj.GetFormula(nRow, nCol, nContent)

    def GetGridColor(self, gridLineType: In[AcGridLineType], rowType: In[AcRowType]) -> AcadAcCmColor:
        return AcadAcCmColor(self._obj.GetGridColor(gridLineType, rowType))
    
    def GetGridColor2(self, nRow: In[int], nCol: In[int], nGridLineType: In[AcGridLineType]) -> AcadAcCmColor:
        return AcadAcCmColor(self._obj.GetGridColor2(nRow, nCol, nGridLineType))
        
    def GetGridDoubleLineSpacing(self, nRow: In[int], nCol: In[int], nGridLineType: In[AcGridLineType]) -> float:
        return self._obj.GetGridDoubleLineSpacing(nRow, nCol, nGridLineType)
        
    def GetGridLineStyle(self, nRow: In[int], nCol: In[int], nGridLineType: In[AcGridLineType]) -> AcGridLineStyle:
        return AcGridLineStyle(self._obj.GetGridLineStyle(nRow, nCol, nGridLineType))
        
    def GetGridLinetype(self, nRow: In[int], nCol: In[int], nGridLineType: In[AcGridLineType]) -> int:
        return self._obj.GetGridLinetype(nRow, nCol, nGridLineType)
            
    def GetGridLineWeight(self, gridLineType: In[AcGridLineType], rowType: In[AcRowType]) -> AcLineWeight:
        return AcLineWeight(self._obj.GetGridLineWeight(gridLineType, rowType))
        
    def GetGridLineWeight2(self, nRow: In[int], nCol: In[int], nGridLineType: In[AcGridLineType]) -> AcLineWeight:
        return AcLineWeight(self._obj.GetGridLineWeight2(nRow, nCol, nGridLineType))
            
    def GetGridVisibility(self, gridLineType: In[AcGridLineType], rowType: In[AcRowType]) -> bool:
        return self._obj.GetGridVisibility(gridLineType, rowType)
            
    def GetGridVisibility2(self, nRow: In[int], nCol: In[int], nGridLineType: In[AcGridLineType]) -> bool:
        return self._obj.GetGridVisibility2(nRow, nCol, nGridLineType)

    def GetHasFormula(self, nRow: In[int], nCol: In[int], nContent: In[int]) -> bool:
        return self._obj.GetHasFormula(nRow, nCol, nContent)
    
    def GetMargin(self, nRow: In[int], nCol: In[int], nMargin: In[AcCellMargin]) -> float:
        return self._obj.GetMargin(nRow, nCol, nMargin)
        
    def GetMinimumColumnWidth(self, col: In[int]) -> float:
        return self._obj.GetMinimumColumnWidth(col)
        
    def GetMinimumRowHeight(self, row: In[int]) -> float:
        return self._obj.GetMinimumRowHeight(row)

    def GetOverride(self, nRow: In[int], nCol: In[int], nContent: In[int]) -> AcCellProperty:
        return AcCellProperty(self._obj.GetOverride(nRow, nCol, nContent))
    
    def GetRotation(self, nRow: In[int], nCol: In[int], nContent: In[int]) -> float:
        return self._obj.GetRotation(nRow, nCol, nContent)

    def GetRowHeight(self, row: In[int]) -> float:
        return self._obj.GetRowHeight(row)
    
    def GetRowType(self, row: In[int]) -> AcRowType:
        return AcRowType(self._obj.GetRowType(row))
    
    def GetScale(self, nRow: In[int], nCol: In[int], nContent: In[int]) -> float:
        return self._obj.GetScale(nRow, nCol, nContent)
    
    def GetSubSelection(self) -> tuple:
        rowMin, rowMax, colMin, colMax = self._obj.GetSubSelection()
        return rowMin, rowMax, colMin, colMax

    def GetText(self, row: In[int], col: In[int]) -> str:
        return self._obj.GetText(row, col)
    
    def GetTextHeight(self, rowType: In[AcRowType]) -> float:
        return self._obj.GetTextHeight(rowType)
    
    def GetTextHeight2(self, nRow: In[int], nCol: In[int], nContent: In[int]) -> float:
        return self._obj.GetTextHeight2(nRow, nCol, nContent)
        
    def GetTextRotation(self, row: In[int], col: In[int]) -> AcRotationAngle:
        return AcRotationAngle(self._obj.GetTextRotation(row, col))
        
    def GetTextString(self, nRow: In[int], nCol: In[int], nContent: In[int]) -> str:
        return self._obj.GetTextString(nRow, nCol, nContent)
        
    def GetTextStyle(self, rowTypes: In[AcRowType]) -> str:
        return self._obj.GetTextStyle(rowTypes)

    def GetTextStyle2(self, nRow: In[int], nCol: In[int], nContent: In[int]) -> str:
        return self._obj.GetTextStyle2(nRow, nCol, nContent)

    def GetValue(self, nRow: In[int], nCol: In[int], nContent: In[int]) -> Variant:
        return Variant(self._obj.GetValue(nRow, nCol, nContent))

    def HitTest(self, wpt: In[PyGePoint3d], wviewVec: In[PyGeVector3d]) -> vIntegerArray:
        resultRowIndex, resultColumnIndex = self._obj.HitTest(wpt(), wviewVec())
        return vIntegerArray(resultRowIndex, resultColumnIndex)

    def InsertColumns(self, col: In[int], Width: In[float], cols: In[int]) -> None:
        self._obj.InsertColumns(col, Width, cols)

    def InsertColumnsAndInherit(self, col: In[int], nInheritFrom: In[int], nNumCols: In[int]) -> None:
        self._obj.InsertColumnsAndInherit(col, nInheritFrom, nNumCols)

    def InsertRows(self, row: In[int], Height: In[float], Rows: In[int]) -> None:
        self._obj.InsertRows(row, Height, Rows)

    def InsertRowsAndInherit(self, nIndex: In[int], nInheritFrom: In[int], nNumRows: In[int]) -> None:
        self._obj.InsertRowsAndInherit(nIndex, nInheritFrom, nNumRows)

    def IsContentEditable(self, nRow: In[int], nCol: In[int]) -> bool:
        return self._obj.IsContentEditable(nRow, nCol)

    def IsEmpty(self, nRow: In[int], nCol: In[int]) -> bool:
        return self._obj.IsEmpty(nRow, nCol)
    
    def IsFormatEditable(self, nRow: In[int], nCol: In[int]) -> bool:
        return self._obj.IsFormatEditable(nRow, nCol)
    
    def IsMergeAllEnabled(self, nRow: In[int], nCol: In[int]) -> bool:
        return self._obj.IsMergeAllEnabled(nRow, nCol)

    def IsMergedCell(self, row: In[int], col: In[int], minRow: In[int], maxRow: In[int], minCol: In[int], maxCol: In[int]) -> bool:
        return self._obj.IsMergedCell(row, col, minRow, maxRow, minCol, maxCol)

    def MergeCells(self, minRow: In[int], maxRow: In[int], minCol: In[int], maxCol: In[int]) -> None:
        self._obj.MergeCells(minRow, maxRow, minCol, maxCol)

    def MoveContent(self, nRow: In[int], nCol: In[int], nFromIndex: In[int], nToIndex: In[int]) -> None:
        self._obj.MoveContent(nRow, nCol, nFromIndex, nToIndex)

    def RecomputeTableBlock(self, bForceUpdate: In[bool]) -> None:
        self._obj.RecomputeTableBlock(bForceUpdate)

    def RemoveAllOverrides(self, nRow: In[int], nCol: In[int]) -> None:
        self._obj.RemoveAllOverrides(nRow, nCol)

    def ReselectSubRegion(self) -> None:
        self._obj.ReselectSubRegion()

    def ResetCellValue(self, row: In[int], col: In[int]) -> None:
        self._obj.RemoveAllOverrides(row, col)

    def Select(self, wpt: In[PyGePoint3d], wvwVec: In[PyGeVector3d], wvwxvec: In[PyGeVector3d], allowOutside: In[bool]) -> tuple[float,float,int,int]:
        wxaper, wyaper, resultRowIndex, resultColumnIndex = self._obj.RemoveAllOverrides(wpt=wpt(), wvwVec=wvwVec(), wvwxvec=wvwxvec(), allowOutside=allowOutside)
        return float(wxaper), float(wyaper), int(resultRowIndex), int(resultColumnIndex)
    
    def SelectSubRegion(self, wpt1: In[PyGePoint3d], wpt2: In[PyGePoint3d], wvwVec: In[PyGeVector3d], wvwxVec: In[PyGeVector3d], seltype: In[AcSelectType], bIncludeCurrentSelection: In[bool]) -> tuple[int,int,int,int]:
        rowMin, rowMax, colMin, colMax = self._obj.RemoveAllOverrides(wpt1(), wpt2(), wvwVec(), wvwxVec(), seltype, bIncludeCurrentSelection)
        return int(rowMin), int(rowMax), int(colMin), int(colMax)

    def SetAlignment(self, rowTypes: In[AcRowType], cellAlignment: In[AcCellAlignment]) -> None:
        self._obj.SetAlignment(rowTypes, cellAlignment)
    
    def SetAutoScale(self, row: In[int], col: In[int], bValue: In[bool]) -> None:
        self._obj.SetAutoScale(row, col, bValue)
    
    def SetAutoScale2(self, nRow: In[int], nCol: In[int], nContent: In[int], bAutoFit: In[bool]) -> None:
        self._obj.SetAutoScale2(nRow, nCol, nContent, bAutoFit)
    
    def SetBackgroundColor(self, rowTypes: In[AcRowType], pColor: In[AcadAcCmColor]) -> None:
        self._obj.SetBackgroundColor(rowTypes, pColor())
    
    def SetBackgroundColorNone(self, rowTypes: In[AcRowType], bValue: In[bool]) -> None:
        self._obj.SetBackgroundColorNone(rowTypes, bValue)
    
    def SetBlockAttributeValue(self, row: In[int], col: In[int], attdefId: In[int], StringValue: In[str]) -> None:
        self._obj.SetBlockAttributeValue(row, col, attdefId, StringValue)

    def SetBlockAttributeValue2(self, nRow: In[int], nCol: In[int], nContent: In[int], blkId: In[int], value: In[str]) -> None:
        self._obj.SetBlockAttributeValue2(nRow, nCol, nContent, blkId, value)
    
    def SetBlockRotation(self, row: In[int], col: In[int], blkRotation: In[float]) -> None:
        self._obj.SetBlockRotation(row, col, blkRotation)
    
    def SetBlockScale(self, row: In[int], col: In[int], blkScale: In[float]) -> None:
        self._obj.SetBlockScale(row, col, blkScale)
    
    def SetBlockTableRecordId(self, row: In[int], col: In[int], blkId: In[int], bAutoFit: In[bool]) -> None:
        self._obj.SetBlockTableRecordId(row, col, blkId, bAutoFit)
    
    def SetBlockTableRecordId2(self, nRow: In[int], nCol: In[int], nContent: In[int], blkId: In[int], autoFit: In[bool]) -> None:
        self._obj.SetBlockTableRecordId2(nRow, nCol, nContent, blkId, autoFit)
    
    def SetBreakHeight(self, nIndex: In[int], dHeight: In[float]) -> None:
        self._obj.SetBreakHeight(nIndex, dHeight)
    
    def SetCellAlignment(self, row: In[int], col: In[int], cellAlignment: In[AcCellAlignment]) -> None:
        self._obj.SetCellAlignment(row, col, cellAlignment)
    
    def SetCellBackgroundColor(self, row: In[int], col: In[int], pColor: In[AcadAcCmColor]) -> None:
        self._obj.SetCellBackgroundColor(row, col, pColor())
    
    def SetCellBackgroundColorNone(self, row: In[int], col: In[int], bValue: In[bool]) -> None:
        self._obj.SetCellBackgroundColorNone(row, col, bValue)
    
    def SetCellContentColor(self, row: In[int], col: In[int], pColor: In[AcadAcCmColor]) -> None:
        self._obj.SetCellContentColor(row, col, pColor())
    
    def SetCellDataType(self, row: In[int], col: In[int], dataType: In[AcValueDataType], unitType: In[AcValueUnitType]) -> None:
        self._obj.SetCellDataType(row, col, dataType, unitType)
    
    def SetCellFormat(self, row: In[int], col: In[int], pFormat: In[str]) -> None:
        self._obj.SetCellFormat(row, col, pFormat)
    
    def SetCellGridColor(self, row: In[int], col: In[int], edges: In[AcCellEdgeMask], pColor: In[AcadAcCmColor]) -> None:
        self._obj.SetCellGridColor(row, col, edges, pColor())
    
    def SetCellGridLineWeight(self, row: In[int], col: In[int], edges: In[AcCellEdgeMask], Lineweight: In[AcLineWeight]) -> None:
        self._obj.SetCellGridColor(row, col, edges, Lineweight)
    
    def SetCellGridVisibility(self, row: In[int], col: In[int], edges: In[AcCellEdgeMask], bValue: In[bool]) -> None:
        self._obj.SetCellGridVisibility(row, col, edges, bValue)
    
    def SetCellState(self, nRow: In[int], nCol: In[int], nLock: In[AcCellState]) -> None:
        self._obj.SetCellState(nRow, nCol, nLock)
    
    def SetCellStyle(self, nRow: In[int], nCol: In[int], szCellStyle: In[str]) -> None:
        self._obj.SetCellStyle(nRow, nCol, szCellStyle)
    
    def SetCellTextHeight(self, row: In[int], col: In[int], TextHeight: In[float]) -> None:
        self._obj.SetCellTextHeight(row, col, TextHeight)
    
    def SetCellTextStyle(self, row: In[int], col: In[int], bstrName: In[str]) -> None:
        self._obj.SetCellTextStyle(row, col, bstrName)
    
    def SetCellType(self, row: In[int], col: In[int], CellType: In[AcCellType]) -> None:
        self._obj.SetCellType(row, col, CellType)
    
    def SetCellValue(self, row: In[int], col: In[int]) -> Variant:
        val = self._obj.SetCellValue(row, col)
        return Variant(val)
    
    def SetCellValueFromText(self, row: In[int], col: In[int], val: In[str], nOption: In[AcParseOption]) -> None:
        self._obj.SetCellValueFromText(row, col, val, nOption)
    
    def SetColumnName(self, nIndex: In[int], name: In[str]) -> None:
        self._obj.SetColumnName(nIndex, name)
    
    def SetColumnWidth(self, col: In[int], Width: In[float]) -> None:
        self._obj.SetColumnWidth(col, Width)
    
    def SetContentColor(self, rowTypes: In[AcRowType], pColor: In[AcadAcCmColor]) -> None:
        self._obj.SetContentColor(rowTypes, pColor())
    
    def SetContentColor2(self, nRow: In[int], nCol: In[int], nContent: In[int], pColor: In[AcadAcCmColor]) -> None:
        self._obj.SetContentColor2(nRow, nCol, nContent, pColor())
    
    def SetContentLayout(self, nRow: In[int], nCol: In[int], nLayout: In[AcCellContentLayout]) -> None:
        self._obj.SetContentLayout(nRow, nCol, nLayout)
    
    def SetCustomData(self, nRow: In[int], nCol: In[int], szKey: In[str], data: In[Variant]) -> None:
        self._obj.SetCustomData(nRow, nCol, szKey, data())
    
    def SetDataFormat(self, nRow: In[int], nCol: In[int], nContent: In[int], szFormat: In[str]) -> None:
        self._obj.SetDataFormat(nRow, nCol, nContent, szFormat)
    
    def SetDataType(self, rowTypes: In[AcRowType], nDataType: In[AcValueDataType], nUnitType: In[AcValueUnitType]) -> None:
        self._obj.SetDataType(rowTypes, nDataType, nUnitType)
    
    def SetDataType2(self, nRow: In[int], nCol: In[int], nContent: In[int], dataType: In[AcValueDataType], unitType: In[AcValueUnitType]) -> None:
        self._obj.SetDataType2(nRow, nCol, nContent, dataType, unitType)
    
    def SetFieldId(self, row: In[int], col: In[int], fieldId: In[int]) -> None:
        self._obj.SetFieldId(row, col, fieldId)
    
    def SetFieldId2(self, nRow: In[int], nCol: In[int], nContent: In[int], acDbObjectId: In[int], nflag: In[AcCellOption]) -> None:
        self._obj.SetFieldId2(nRow, nCol, nContent, acDbObjectId, nflag)
    
    def SetFormat(self, rowTypes: In[AcRowType], pFormat: In[str]) -> None:
        self._obj.SetFormat(rowTypes, pFormat)
    
    def SetFormula(self, nRow: In[int], nCol: In[int], nContent: In[int], pszFormula: In[str]) -> None:
        self._obj.SetFormula(nRow, nCol, nContent, pszFormula)
    
    def SetGridColor(self, gridLineTypes: In[AcGridLineType], rowTypes: In[AcRowType], pColor: In[AcadAcCmColor]) -> None:
        self._obj.SetGridColor(gridLineTypes, rowTypes, pColor())
    
    def SetGridColor2(self, nRow: In[int], nCol: In[int], nGridLineType: In[AcGridLineType], pColor: In[AcadAcCmColor]) -> None:
        self._obj.SetGridColor2(nRow, nCol, nGridLineType, pColor())
    
    def SetGridDoubleLineSpacing(self, nRow: In[int], nCol: In[int], nGridLineType: In[AcGridLineType], fSpacing: In[float]) -> None:
        self._obj.SetGridDoubleLineSpacing(nRow, nCol, nGridLineType, fSpacing)
    
    def SetGridLineStyle(self, nRow: In[int], nCol: In[int], nGridLineType: In[AcGridLineType], nLineStyle: In[AcGridLineStyle]) -> None:
        self._obj.SetGridLineStyle(nRow, nCol, nGridLineType, nLineStyle)
    
    def SetGridLinetype(self, nRow: In[int], nCol: In[int], nGridLineType: In[AcGridLineType], idLinetype: In[int]) -> None:
        self._obj.SetGridLinetype(nRow, nCol, nGridLineType, idLinetype)
    
    def SetGridLineWeight(self, gridLineTypes: In[AcGridLineType], rowTypes: In[AcRowType], Lineweight: In[AcLineWeight]) -> None:
        self._obj.SetGridLineWeight(gridLineTypes, rowTypes, Lineweight)
    
    def SetGridLineWeight2(self, nRow: In[int], nCol: In[int], nGridLineType: In[AcGridLineType], lineWeight: In[AcLineWeight]) -> None:
        self._obj.SetGridLineWeight2(nRow, nCol, nGridLineType, lineWeight)
    
    def SetGridVisibility(self, gridLineTypes: In[AcGridLineType], rowTypes: In[AcRowType], bValue: In[bool]) -> None:
        self._obj.SetGridVisibility(gridLineTypes, rowTypes, bValue)
    
    def SetGridVisibility2(self, nRow: In[int], nCol: In[int], nGridLineType: In[AcGridLineType], bVisible: In[bool]) -> None:
        self._obj.SetGridVisibility2(nRow, nCol, nGridLineType, bVisible)
    
    def SetMargin(self, nRow: In[int], nCol: In[int], nMargins: In[AcCellMargin], fMargin: In[float]) -> None:
        self._obj.SetMargin(nRow, nCol, nMargins, fMargin)
    
    def SetOverride(self, nRow: In[int], nCol: In[int], nContent: In[int], nProp: In[AcCellProperty]) -> None:
        self._obj.SetOverride(nRow, nCol, nContent, nProp)
    
    def SetRotation(self, nRow: In[int], nCol: In[int], nContent: In[int], pValue: In[float]) -> None:
        self._obj.SetRotation(nRow, nCol, nContent, pValue)
    
    def SetRowHeight(self, row: In[int], Height: In[float]) -> None:
        self._obj.SetRowHeight(row, Height)
    
    def SetScale(self, nRow: In[int], nCol: In[int], nContent: In[int], scale: In[float]) -> None:
        self._obj.SetScale(nRow, nCol, nContent, scale)
    
    def SetSubSelection(self, rowMin: In[int], rowMax: In[int], colMin: In[int], colMax: In[int]) -> None:
        self._obj.SetSubSelection(rowMin, rowMax, colMin, colMax)
    
    def SetText(self, row: In[int], col: In[int], pStr: In[str]) -> None:
        self._obj.SetText(row, col, pStr)
    
    def SetTextHeight(self, rowTypes: In[AcRowType], TextHeight: In[float]) -> None:
        self._obj.SetTextHeight(rowTypes, TextHeight)
    
    def SetTextHeight2(self, nRow: In[int], nCol: In[int], nContent: In[int], height: In[float]) -> None:
        self._obj.SetTextHeight2(nRow, nCol, nContent, height)
    
    def SetTextRotation(self, row: In[int], col: In[int], TextRotation: In[AcRotationAngle]) -> None:
        self._obj.SetTextRotation(row, col, TextRotation)
    
    def SetTextString(self, nRow: In[int], nCol: In[int], nContent: In[int], text: In[str]) -> None:
        self._obj.SetTextString(nRow, nCol, nContent, text)
    
    def SetTextStyle(self, rowTypes: In[AcRowType], bstrName: In[str]) -> None:
        self._obj.SetTextStyle(rowTypes, bstrName)
    
    def SetTextStyle2(self, nRow: In[int], nCol: In[int], nContent: In[int], StringStyleName: In[str]) -> None:
        self._obj.SetTextStyle2(nRow, nCol, nContent, StringStyleName)
    
    def SetToolTip(self, nRow: In[int], nCol: In[int], tip: In[str]) -> None:
        self._obj.SetToolTip(nRow, nCol, tip)
    
    def SetValue(self, nRow: In[int], nCol: In[int], nContent: In[int], acValue: In[Variant]) -> None:
        self._obj.SetValue(nRow, nCol, nContent, acValue())
    
    def SetValueFromText(self, nRow: In[int], nCol: In[int], nContent: In[int], szText: In[str], nOption: In[AcParseOption]) -> None:
        self._obj.SetValueFromText(nRow, nCol, nContent, szText, nOption)
    
    def UnmergeCells(self, minRow: In[int], maxRow: In[int], minCol: In[int], maxCol: In[int]) -> None:
        self._obj.UnmergeCells(minRow, maxRow, minCol, maxCol)