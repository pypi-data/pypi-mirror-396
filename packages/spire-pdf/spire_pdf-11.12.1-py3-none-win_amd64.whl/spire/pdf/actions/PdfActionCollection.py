from enum import Enum
from plum import dispatch
from typing import TypeVar, Union, Generic, List, Tuple
from spire.pdf.common import *
from spire.pdf import *
from ctypes import *
import abc

class PdfActionCollection(PdfCollection):
    """
    Represents collection of actions.
    """

    def Add(self, action: 'PdfAction') -> int:
        """
        Adds the specified action.

        Args:
            action: The action.

        Returns:
            The index of the added action.
        """
        intPtraction: c_void_p = action.Ptr

        GetDllLibPdf().PdfActionCollection_Add.argtypes = [c_void_p, c_void_p]
        GetDllLibPdf().PdfActionCollection_Add.restype = c_int
        ret = CallCFunction(GetDllLibPdf().PdfActionCollection_Add,self.Ptr, intPtraction)
        return ret


    def Insert(self, index: int, action: 'PdfAction'):
        """
        Inserts the action at the specified position.

        Args:
            index: The index.
            action: The action.
        """
        intPtraction: c_void_p = action.Ptr

        GetDllLibPdf().PdfActionCollection_Insert.argtypes = [c_void_p, c_int, c_void_p]
        CallCFunction(GetDllLibPdf().PdfActionCollection_Insert,self.Ptr, index, intPtraction)


    def IndexOf(self, action: 'PdfAction') -> int:
        """
        Gets the index of the action.

        Args:
            action: The action.

        Returns:
            The index of the action.
        """
        intPtraction: c_void_p = action.Ptr

        GetDllLibPdf().PdfActionCollection_IndexOf.argtypes = [c_void_p, c_void_p]
        GetDllLibPdf().PdfActionCollection_IndexOf.restype = c_int
        ret = CallCFunction(GetDllLibPdf().PdfActionCollection_IndexOf,self.Ptr, intPtraction)
        return ret


    def Contains(self, action: 'PdfAction') -> bool:
        """
        Determines whether the action is contained within collection.

        Args:
            action: The action.

        Returns:
            A boolean value indicating the presence of the action in the collection.
        """
        intPtraction: c_void_p = action.Ptr

        GetDllLibPdf().PdfActionCollection_Contains.argtypes = [c_void_p, c_void_p]
        GetDllLibPdf().PdfActionCollection_Contains.restype = c_bool
        ret = CallCFunction(GetDllLibPdf().PdfActionCollection_Contains,self.Ptr, intPtraction)
        return ret

    def Clear(self):
        """
        Clears this collection.
        """
        GetDllLibPdf().PdfActionCollection_Clear.argtypes = [c_void_p]
        CallCFunction(GetDllLibPdf().PdfActionCollection_Clear,self.Ptr)


    def Remove(self, action: 'PdfAction'):
        """
        Removes the specified action.

        Args:
            action: The action.
        """
        intPtraction: c_void_p = action.Ptr

        GetDllLibPdf().PdfActionCollection_Remove.argtypes = [c_void_p, c_void_p]
        CallCFunction(GetDllLibPdf().PdfActionCollection_Remove,self.Ptr, intPtraction)


    def RemoveAt(self, index: int):
        """
        Removes the action at the specified position.

        Args:
            index: The index.
        """
        GetDllLibPdf().PdfActionCollection_RemoveAt.argtypes = [c_void_p, c_int]
        CallCFunction(GetDllLibPdf().PdfActionCollection_RemoveAt,self.Ptr, index)