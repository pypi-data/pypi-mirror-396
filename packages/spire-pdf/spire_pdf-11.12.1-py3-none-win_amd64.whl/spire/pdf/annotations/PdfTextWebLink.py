from enum import Enum
from plum import dispatch
from typing import TypeVar, Union, Generic, List, Tuple
from spire.pdf.common import *
from spire.pdf import *
from ctypes import *
import abc

class PdfTextWebLink(PdfTextWidget):
    """
    Represents the class for text web link annotation.
    """

    @dispatch
    def __init__(self):
        GetDllLibPdf().PdfTextWebLink_CreatePdfTextWebLink.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfTextWebLink_CreatePdfTextWebLink)
        super(PdfTextWebLink, self).__init__(intPtr)

    @property
    def Url(self) -> str:
        """
        Gets or sets the Url address.
        """
        GetDllLibPdf().PdfTextWebLink_get_Url.argtypes = [c_void_p]
        GetDllLibPdf().PdfTextWebLink_get_Url.restype = c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPdf().PdfTextWebLink_get_Url,self.Ptr))
        return ret

    @Url.setter
    def Url(self, value: str):
        GetDllLibPdf().PdfTextWebLink_set_Url.argtypes = [c_void_p, c_wchar_p]
        CallCFunction(GetDllLibPdf().PdfTextWebLink_set_Url,self.Ptr, value)

    @dispatch
    def DrawTextWebLink(self, newPage, location: PointF) -> PdfLayoutResult:
        """
        Draws a Text Web Link on the Page
        Args: newPage: The page where the annotation should be placed.
        Args: location: The location of the annotation.
        Returns: Pdf Layout result
        """
        intPtrpage: c_void_p = newPage.Ptr
        intPtrlocation: c_void_p = location.Ptr

        GetDllLibPdf().PdfTextWebLink_DrawTextWebLink.argtypes = [c_void_p, c_void_p, c_void_p]
        GetDllLibPdf().PdfTextWebLink_DrawTextWebLink.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfTextWebLink_DrawTextWebLink,self.Ptr, intPtrpage, intPtrlocation)
        ret = None if intPtr == None else PdfLayoutResult(intPtr)
        return ret

    @dispatch
    def DrawTextWebLink(self, graphics: PdfCanvas, location: PointF):
        """
        Draw a Text Web Link on the Graphics
        Args: graphics: The object specifies where annotation should be placed.
        Args: location: The location of the annotation.
        """
        intPtrgraphics: c_void_p = graphics.Ptr
        intPtrlocation: c_void_p = location.Ptr

        GetDllLibPdf().PdfTextWebLink_DrawTextWebLinkGL.argtypes = [c_void_p, c_void_p, c_void_p]
        CallCFunction(GetDllLibPdf().PdfTextWebLink_DrawTextWebLinkGL,self.Ptr, intPtrgraphics, intPtrlocation)