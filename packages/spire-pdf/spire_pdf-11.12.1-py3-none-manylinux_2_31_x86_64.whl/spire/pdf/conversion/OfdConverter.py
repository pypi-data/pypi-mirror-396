from enum import Enum
from plum import dispatch
from typing import TypeVar, Union, Generic, List, Tuple
from spire.pdf.common import *
from spire.pdf import *
from ctypes import *
import abc

class OfdConverter(SpireObject):
    """
    This class provides support for converting ofd into pdf or image.
    """
    @dispatch
    def __init__(self, filename:str):
        GetDllLibPdf().OfdConverter_CreateOfdConverterF.argtypes=[c_wchar_p]
        GetDllLibPdf().OfdConverter_CreateOfdConverterF.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().OfdConverter_CreateOfdConverterF,filename)
        super(OfdConverter, self).__init__(intPtr)

    @dispatch
    def __init__(self, stream:Stream):
        intPtrstream:c_void_p = stream.Ptr
        GetDllLibPdf().OfdConverter_CreateOfdConverterS.argtypes=[c_void_p]
        GetDllLibPdf().OfdConverter_CreateOfdConverterS.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().OfdConverter_CreateOfdConverterS,intPtrstream)
        super(OfdConverter, self).__init__(intPtr)

    @property
    def PageCount(self) -> int:
        """
        Gets the document page count.
        """
        GetDllLibPdf().OfdConverter_get_PageCount.argtypes = [c_void_p]
        GetDllLibPdf().OfdConverter_get_PageCount.restype = c_int
        ret = CallCFunction(GetDllLibPdf().OfdConverter_get_PageCount,self.Ptr)
        return ret

    @dispatch
    def ToPdf(self, filename: str):
        """
        Save ofd document to pdf.
        Args: filename: A relative or absolute path for the file.
        """
        GetDllLibPdf().OfdConverter_ToPdf.argtypes = [c_void_p, c_wchar_p]
        CallCFunction(GetDllLibPdf().OfdConverter_ToPdf,self.Ptr, filename)

    @dispatch
    def ToPdf(self, stream: Stream):
        """
        Save ofd document to pdf.
        Args: stream: The pdf file stream.
        """
        intPtrstream: c_void_p = stream.Ptr
        GetDllLibPdf().OfdConverter_ToPdfS.argtypes = [c_void_p, c_void_p]
        CallCFunction(GetDllLibPdf().OfdConverter_ToPdfS,self.Ptr, intPtrstream)

    @dispatch
    def ToImage(self, pageIndex: int) -> Stream:
        """
        Saves OFD document page as image.
        Args: pageIndex: Page index.
        Returns: Returns page as Image.
        """
        GetDllLibPdf().OfdConverter_ToImage.argtypes = [c_void_p, c_int]
        GetDllLibPdf().OfdConverter_ToImage.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().OfdConverter_ToImage,self.Ptr, pageIndex)
        ret = None if intPtr == None else Stream(intPtr)
        return ret

    @dispatch
    def ToImage(self, pageIndex: int, dpiX: int, dpiY: int) -> Stream:
        """
        Saves OFD document page as image.
        Args: pageIndex: Page index.
        Args: dpiX: Pictures X resolution.
        Args: dpiY: Pictures Y resolution.
        Returns: Returns page as Image.
        """
        GetDllLibPdf().OfdConverter_ToImagePDD.argtypes = [c_void_p, c_int, c_int, c_int]
        GetDllLibPdf().OfdConverter_ToImagePDD.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().OfdConverter_ToImagePDD,self.Ptr, pageIndex, dpiX, dpiY)
        ret = None if intPtr == None else Stream(intPtr)
        return ret

    def Dispose(self):
        """
        """
        GetDllLibPdf().OfdConverter_Dispose.argtypes = [c_void_p]
        CallCFunction(GetDllLibPdf().OfdConverter_Dispose,self.Ptr)