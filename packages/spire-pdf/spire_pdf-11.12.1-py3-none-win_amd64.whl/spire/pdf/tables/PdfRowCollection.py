from enum import Enum
from plum import dispatch
from typing import TypeVar, Union, Generic, List, Tuple
from spire.pdf.common import *
from spire.pdf import *
from ctypes import *
import abc

class PdfRowCollection(PdfCollection):
    """
    Represents the collection of the columns.
    """

    def get_Item(self, index: int) -> 'PdfRow':
        """
        Gets the row at the specified index.
        """

        GetDllLibPdf().PdfRowCollection_get_Item.argtypes = [c_void_p, c_int]
        GetDllLibPdf().PdfRowCollection_get_Item.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfRowCollection_get_Item,self.Ptr, index)
        ret = None if intPtr == None else PdfRow(intPtr)
        return ret


    @dispatch
    def Add(self, row: PdfRow):
        """
        Adds the specified row.
        Args:
            row: The row.
        """
        intPtrrow: c_void_p = row.Ptr

        GetDllLibPdf().PdfRowCollection_Add.argtypes = [c_void_p, c_void_p]
        CallCFunction(GetDllLibPdf().PdfRowCollection_Add,self.Ptr, intPtrrow)

    @dispatch
    def Add(self, values: List[SpireObject]):
        """
        Adds a new row using the array of values.
        """

        countvalues = len(values)
        ArrayTypevalues = c_void_p * countvalues
        arrayvalues = ArrayTypevalues()
        for i in range(0, countvalues):
            arrayvalues[i] = values[i].Ptr

        GetDllLibPdf().PdfRowCollection_AddV.argtypes = [c_void_p, ArrayTypevalues]
        CallCFunction(GetDllLibPdf().PdfRowCollection_AddV,self.Ptr, arrayvalues)