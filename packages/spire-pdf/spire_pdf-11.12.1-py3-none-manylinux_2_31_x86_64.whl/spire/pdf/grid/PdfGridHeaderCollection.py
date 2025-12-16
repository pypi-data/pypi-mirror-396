from enum import Enum
from plum import dispatch
from typing import TypeVar, Union, Generic, List, Tuple
from spire.pdf.common import *
from spire.pdf import *
from ctypes import *
import abc

class PdfGridHeaderCollection(IEnumerable):
    """
    Represents a collection of PdfGridRow objects.
    """

    def get_Item(self, index: int) -> 'PdfGridRow':
        """
        Gets the PdfGridRow at the specified index.

        Args:
            index: The index of the PdfGridRow.

        Returns:
            The PdfGridRow at the specified index.
        """
        GetDllLibPdf().PdfGridHeaderCollection_get_Item.argtypes = [c_void_p, c_int]
        GetDllLibPdf().PdfGridHeaderCollection_get_Item.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfGridHeaderCollection_get_Item,self.Ptr, index)
        ret = None if intPtr == None else PdfGridRow(intPtr)
        return ret

    @property
    def Count(self) -> int:
        """
        Gets the count of PdfGridRow objects in the collection.

        Returns:
            The count of PdfGridRow objects.
        """
        GetDllLibPdf().PdfGridHeaderCollection_get_Count.argtypes = [c_void_p]
        GetDllLibPdf().PdfGridHeaderCollection_get_Count.restype = c_int
        ret = CallCFunction(GetDllLibPdf().PdfGridHeaderCollection_get_Count,self.Ptr)
        return ret

    def Clear(self):
        """
        Clears the collection.
        """
        GetDllLibPdf().PdfGridHeaderCollection_Clear.argtypes = [c_void_p]
        CallCFunction(GetDllLibPdf().PdfGridHeaderCollection_Clear,self.Ptr)

    def ApplyStyle(self, style: 'PdfGridStyleBase'):
        """
        Applies the specified style to the collection.

        Args:
            style: The style to apply.
        """
        intPtrstyle: c_void_p = style.Ptr

        GetDllLibPdf().PdfGridHeaderCollection_ApplyStyle.argtypes = [c_void_p, c_void_p]
        CallCFunction(GetDllLibPdf().PdfGridHeaderCollection_ApplyStyle,self.Ptr, intPtrstyle)

    def GetEnumerator(self) -> 'IEnumerator':
        """
        Gets an enumerator for the collection.

        Returns:
            An IEnumerator object for the collection.
        """
        GetDllLibPdf().PdfGridHeaderCollection_GetEnumerator.argtypes = [c_void_p]
        GetDllLibPdf().PdfGridHeaderCollection_GetEnumerator.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfGridHeaderCollection_GetEnumerator,self.Ptr)
        ret = None if intPtr == None else IEnumerator(intPtr)
        return ret