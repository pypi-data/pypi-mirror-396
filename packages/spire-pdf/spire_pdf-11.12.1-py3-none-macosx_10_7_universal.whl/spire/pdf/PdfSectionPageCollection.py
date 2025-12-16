from enum import Enum
from plum import dispatch
from typing import TypeVar, Union, Generic, List, Tuple
from spire.pdf.common import *
from spire.pdf import *
from ctypes import *
import abc

class PdfSectionPageCollection(IEnumerable):
    """
    Manipulates pages within a section.
    """

    def get_Item(self, index: int) -> 'PdfNewPage':
        """
        Gets the page at the specified index.
        """
        GetDllLibPdf().PdfSectionPageCollection_get_Item.argtypes = [c_void_p, c_int]
        GetDllLibPdf().PdfSectionPageCollection_get_Item.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfSectionPageCollection_get_Item,self.Ptr, index)
        ret = None if intPtr == None else PdfNewPage(intPtr)
        return ret

    @property
    def Count(self) -> int:
        """
        Gets the count of the pages.
        """
        GetDllLibPdf().PdfSectionPageCollection_get_Count.argtypes = [c_void_p]
        GetDllLibPdf().PdfSectionPageCollection_get_Count.restype = c_int
        ret = CallCFunction(GetDllLibPdf().PdfSectionPageCollection_get_Count,self.Ptr)
        return ret

    @dispatch
    def Add(self) -> PdfNewPage:
        """
        Creates a new page and adds it into the collection.
        Returns the new page.
        """
        GetDllLibPdf().PdfSectionPageCollection_Add.argtypes = [c_void_p]
        GetDllLibPdf().PdfSectionPageCollection_Add.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfSectionPageCollection_Add,self.Ptr)
        ret = None if intPtr == None else PdfNewPage(intPtr)
        return ret

    @dispatch
    def Add(self, page: PdfNewPage):
        """
        Adds a page into the collection.
        Args: page: The page.
        """
        intPtrpage: c_void_p = page.Ptr
        GetDllLibPdf().PdfSectionPageCollection_AddP.argtypes = [c_void_p, c_void_p]
        CallCFunction(GetDllLibPdf().PdfSectionPageCollection_AddP,self.Ptr, intPtrpage)

    def Insert(self, index: int, page: 'PdfNewPage'):
        """
        Inserts a page at the specified index.
        Args: index: The index.
        Args: page: The page.
        """
        intPtrpage: c_void_p = page.Ptr
        GetDllLibPdf().PdfSectionPageCollection_Insert.argtypes = [c_void_p, c_int, c_void_p]
        CallCFunction(GetDllLibPdf().PdfSectionPageCollection_Insert,self.Ptr, index, intPtrpage)

    def IndexOf(self, page: 'PdfNewPage') -> int:
        """
        Returns the index of the specified page.
        Args: page: The page.
        Returns: The index of the page.
        """
        intPtrpage: c_void_p = page.Ptr
        GetDllLibPdf().PdfSectionPageCollection_IndexOf.argtypes = [c_void_p, c_void_p]
        GetDllLibPdf().PdfSectionPageCollection_IndexOf.restype = c_int
        ret = CallCFunction(GetDllLibPdf().PdfSectionPageCollection_IndexOf,self.Ptr, intPtrpage)
        return ret

    def Contains(self, page: 'PdfNewPage') -> bool:
        """
        Determines whether the specified page is within the collection.
        Args: page: The page.
        Returns: True if the collection contains the specified page; otherwise, False.
        """
        intPtrpage: c_void_p = page.Ptr
        GetDllLibPdf().PdfSectionPageCollection_Contains.argtypes = [c_void_p, c_void_p]
        GetDllLibPdf().PdfSectionPageCollection_Contains.restype = c_bool
        ret = CallCFunction(GetDllLibPdf().PdfSectionPageCollection_Contains,self.Ptr, intPtrpage)
        return ret

    def Remove(self, page: 'PdfNewPage'):
        """
        Removes the specified page.
        Args: page: The page.
        """
        intPtrpage: c_void_p = page.Ptr
        GetDllLibPdf().PdfSectionPageCollection_Remove.argtypes = [c_void_p, c_void_p]
        CallCFunction(GetDllLibPdf().PdfSectionPageCollection_Remove,self.Ptr, intPtrpage)

    def RemoveAt(self, index: int):
        """
        Removes a page at the index specified.
        Args: index: The index.
        """
        GetDllLibPdf().PdfSectionPageCollection_RemoveAt.argtypes = [c_void_p, c_int]
        CallCFunction(GetDllLibPdf().PdfSectionPageCollection_RemoveAt,self.Ptr, index)

    def Clear(self):
        """
        Clears this collection.
        """
        GetDllLibPdf().PdfSectionPageCollection_Clear.argtypes = [c_void_p]
        CallCFunction(GetDllLibPdf().PdfSectionPageCollection_Clear,self.Ptr)