from enum import Enum
from plum import dispatch
from typing import TypeVar, Union, Generic, List, Tuple
from spire.pdf.common import *
from spire.pdf import *
from ctypes import *
import abc

class PdfGridRowCollection(SpireObject):
    """
    Represents a collection of rows in a PDF grid.
    """

    def Add(self) -> 'PdfGridRow':
        """
        Adds a new row to the collection.

        Returns:
            PdfGridRow: The newly added row.
        """
        GetDllLibPdf().PdfGridRowCollection_Add.argtypes = [c_void_p]
        GetDllLibPdf().PdfGridRowCollection_Add.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfGridRowCollection_Add,self.Ptr)
        ret = None if intPtr == None else PdfGridRow(intPtr)
        return ret

    def SetSpan(self, rowIndex: int, cellIndex: int, rowSpan: int, colSpan: int):
        """
        Sets the span of a cell in the grid.

        Args:
            rowIndex (int): The index of the row.
            cellIndex (int): The index of the cell.
            rowSpan (int): The number of rows the cell should span.
            colSpan (int): The number of columns the cell should span.
        """
        GetDllLibPdf().PdfGridRowCollection_SetSpan.argtypes = [c_void_p, c_int, c_int, c_int, c_int]
        CallCFunction(GetDllLibPdf().PdfGridRowCollection_SetSpan,self.Ptr, rowIndex, cellIndex, rowSpan, colSpan)

    def ApplyStyle(self, style: 'PdfGridStyleBase'):
        """
        Applies a style to the grid.

        Args:
            style (PdfGridStyleBase): The style to apply.
        """
        intPtrstyle: c_void_p = style.Ptr

        GetDllLibPdf().PdfGridRowCollection_ApplyStyle.argtypes = [c_void_p, c_void_p]
        CallCFunction(GetDllLibPdf().PdfGridRowCollection_ApplyStyle,self.Ptr, intPtrstyle)

    def get_Item(self, index: int) -> 'PdfGridRow':
        """
        Gets the PdfGridRow at the specified index.

        Args:
            index: The index of the PdfGridRow.

        Returns:
            The PdfGridRow at the specified index.
        """
        GetDllLibPdf().PdfGridRowCollection_get_Item.argtypes = [c_void_p, c_int]
        GetDllLibPdf().PdfGridRowCollection_get_Item.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfGridRowCollection_get_Item,self.Ptr, index)
        ret = None if intPtr == None else PdfGridRow(intPtr)
        return ret

    @property
    def Count(self) -> int:
        """
        Gets the count of PdfGridRowCollection in the collection.

        Returns:
            The count of PdfGridRowCollection.
        """
        GetDllLibPdf().PdfGridRowCollection_get_Count.argtypes = [c_void_p]
        GetDllLibPdf().PdfGridRowCollection_get_Count.restype = c_int
        ret = CallCFunction(GetDllLibPdf().PdfGridRowCollection_get_Count,self.Ptr)
        return ret