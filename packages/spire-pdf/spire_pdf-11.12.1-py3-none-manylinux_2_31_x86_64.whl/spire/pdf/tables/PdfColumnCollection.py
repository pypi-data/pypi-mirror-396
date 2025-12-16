from enum import Enum
from plum import dispatch
from typing import TypeVar, Union, Generic, List, Tuple
from spire.pdf.common import *
from spire.pdf import *
from ctypes import *
import abc

class PdfColumnCollection(PdfCollection):
    """
    Represents the collection of the columns.
    """

    def get_Item(self, index: int) -> 'PdfColumn':
        """
        Gets the column at the specified index.
        Args: index: The index of the column.
        Returns: The column at the specified index.
        """
        GetDllLibPdf().PdfColumnCollection_get_Item.argtypes = [c_void_p, c_int]
        GetDllLibPdf().PdfColumnCollection_get_Item.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfColumnCollection_get_Item,self.Ptr, index)
        ret = None if intPtr == None else PdfColumn(intPtr)
        return ret

    def Add(self, column: 'PdfColumn'):
        """
        Adds the specified column.
        Args: column: The column to be added.
        """
        intPtrcolumn: c_void_p = column.Ptr

        GetDllLibPdf().PdfColumnCollection_Add.argtypes = [c_void_p, c_void_p]
        CallCFunction(GetDllLibPdf().PdfColumnCollection_Add,self.Ptr, intPtrcolumn)