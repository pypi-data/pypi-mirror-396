from enum import Enum
from plum import dispatch
from typing import TypeVar, Union, Generic, List, Tuple
from spire.pdf.common import *
from spire.pdf import *
from ctypes import *
import abc

class PdfListWidgetItemCollection(PdfCollection):
    """
    Represents a collection of list box field items.
    """

    def get_Item(self, index: int) -> 'PdfListWidgetItem':
        """
        Gets the item at the specified index.
        Args:
            index: The index of the item.
        Returns:
            The PdfListWidgetItem at the specified index.
        """
        GetDllLibPdf().PdfListWidgetItemCollection_get_Item.argtypes = [c_void_p, c_int]
        GetDllLibPdf().PdfListWidgetItemCollection_get_Item.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfListWidgetItemCollection_get_Item,self.Ptr, index)
        ret = None if intPtr == None else PdfListWidgetItem(intPtr)
        return ret

    def Add(self, widgetItem: 'PdfListWidgetItem') -> int:
        """
        Inserts an item at the end of the collection.
        Args:
            widgetItem: The PdfListWidgetItem to be added to the collection.
        Returns:
            The index of the added item.
        """
        intPtrwidgetItem: c_void_p = widgetItem.Ptr

        GetDllLibPdf().PdfListWidgetItemCollection_Add.argtypes = [c_void_p, c_void_p]
        GetDllLibPdf().PdfListWidgetItemCollection_Add.restype = c_int
        ret = CallCFunction(GetDllLibPdf().PdfListWidgetItemCollection_Add,self.Ptr, intPtrwidgetItem)
        return ret

    def Insert(self, index: int, widgetItem: 'PdfListWidgetItem'):
        """
        Inserts the list item at the specified index.
        Args:
            index: The index at which to insert the item.
            widgetItem: The item to be inserted.
        """
        intPtrwidgetItem: c_void_p = widgetItem.Ptr

        GetDllLibPdf().PdfListWidgetItemCollection_Insert.argtypes = [c_void_p, c_int, c_void_p]
        CallCFunction(GetDllLibPdf().PdfListWidgetItemCollection_Insert,self.Ptr, index, intPtrwidgetItem)

    def RemoveAt(self, index: int):
        """
        Removes the element at the specified index.
        Args:
            index: The index of the item to be removed.
        Remarks:
            Throws IndexOutOfRange exception if the index is out of bounds.
        """
        GetDllLibPdf().PdfListWidgetItemCollection_RemoveAt.argtypes = [c_void_p, c_int]
        CallCFunction(GetDllLibPdf().PdfListWidgetItemCollection_RemoveAt,self.Ptr, index)

    def Clear(self):
        """
        Clears the item collection.
        """
        GetDllLibPdf().PdfListWidgetItemCollection_Clear.argtypes = [c_void_p]
        CallCFunction(GetDllLibPdf().PdfListWidgetItemCollection_Clear,self.Ptr)