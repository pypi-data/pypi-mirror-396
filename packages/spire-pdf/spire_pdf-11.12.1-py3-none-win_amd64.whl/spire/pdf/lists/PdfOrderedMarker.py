from enum import Enum
from plum import dispatch
from typing import TypeVar, Union, Generic, List, Tuple
from spire.pdf.common import *
from spire.pdf import *
from ctypes import *
import abc

class PdfOrderedMarker(PdfMarkerBase):
    """
    Represents marker for ordered list.
    """

    @dispatch
    def __init__(self, style: PdfNumberStyle, delimiter: str, suffix: str, font: 'PdfFontBase'):
        """
        Initializes a new instance of the PdfOrderedMarker class with the specified style, delimiter, suffix, and font.
        """
        enumStyle: c_int = style.value
        ptrFont: c_void_p = font.Ptr

        GetDllLibPdf().PdfOrderedMarker_CreatePdfOrderedMarkerSDSF.argtypes = [c_int, c_wchar_p, c_wchar_p, c_void_p]
        GetDllLibPdf().PdfOrderedMarker_CreatePdfOrderedMarkerSDSF.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfOrderedMarker_CreatePdfOrderedMarkerSDSF,enumStyle, delimiter, suffix, ptrFont)
        super(PdfOrderedMarker, self).__init__(intPtr)

    @dispatch
    def __init__(self, style: PdfNumberStyle, suffix: str, font: 'PdfFontBase'):
        """
        Initializes a new instance of the PdfOrderedMarker class with the specified style, suffix, and font.
        """
        enumStyle: c_int = style.value
        ptrFont: c_void_p = font.Ptr

        GetDllLibPdf().PdfOrderedMarker_CreatePdfOrderedMarkerSSF.argtypes = [c_int, c_wchar_p, c_void_p]
        GetDllLibPdf().PdfOrderedMarker_CreatePdfOrderedMarkerSSF.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfOrderedMarker_CreatePdfOrderedMarkerSSF,enumStyle, suffix, ptrFont)
        super(PdfOrderedMarker, self).__init__(intPtr)

    @dispatch
    def __init__(self, style: PdfNumberStyle, font: 'PdfFontBase'):
        """
        Initializes a new instance of the PdfOrderedMarker class with the specified style and font.
        """
        enumStyle: c_int = style.value
        ptrFont: c_void_p = font.Ptr

        GetDllLibPdf().PdfOrderedMarker_CreatePdfOrderedMarkerSF.argtypes = [c_int, c_void_p]
        GetDllLibPdf().PdfOrderedMarker_CreatePdfOrderedMarkerSF.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfOrderedMarker_CreatePdfOrderedMarkerSF,enumStyle, ptrFont)
        super(PdfOrderedMarker, self).__init__(intPtr)

    @property
    def Style(self) -> 'PdfNumberStyle':
        """
        Gets or sets the list numbering style.
        """
        GetDllLibPdf().PdfOrderedMarker_get_Style.argtypes = [c_void_p]
        GetDllLibPdf().PdfOrderedMarker_get_Style.restype = c_int
        ret = CallCFunction(GetDllLibPdf().PdfOrderedMarker_get_Style,self.Ptr)
        objwrapped = PdfNumberStyle(ret)
        return objwrapped

    @Style.setter
    def Style(self, value: 'PdfNumberStyle'):
        GetDllLibPdf().PdfOrderedMarker_set_Style.argtypes = [c_void_p, c_int]
        CallCFunction(GetDllLibPdf().PdfOrderedMarker_set_Style,self.Ptr, value.value)

    @property
    def StartNumber(self) -> int:
        """
        Gets or sets start number for ordered list. Default value is 1.
        """
        GetDllLibPdf().PdfOrderedMarker_get_StartNumber.argtypes = [c_void_p]
        GetDllLibPdf().PdfOrderedMarker_get_StartNumber.restype = c_int
        ret = CallCFunction(GetDllLibPdf().PdfOrderedMarker_get_StartNumber,self.Ptr)
        return ret

    @StartNumber.setter
    def StartNumber(self, value: int):
        GetDllLibPdf().PdfOrderedMarker_set_StartNumber.argtypes = [c_void_p, c_int]
        CallCFunction(GetDllLibPdf().PdfOrderedMarker_set_StartNumber,self.Ptr, value)

    @property
    def Delimiter(self) -> str:
        """
        Gets or sets the delimiter.
        """
        GetDllLibPdf().PdfOrderedMarker_get_Delimiter.argtypes = [c_void_p]
        GetDllLibPdf().PdfOrderedMarker_get_Delimiter.restype = c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPdf().PdfOrderedMarker_get_Delimiter,self.Ptr))
        return ret

    @Delimiter.setter
    def Delimiter(self, value: str):
        GetDllLibPdf().PdfOrderedMarker_set_Delimiter.argtypes = [c_void_p, c_wchar_p]
        CallCFunction(GetDllLibPdf().PdfOrderedMarker_set_Delimiter,self.Ptr, value)

    @property
    def Suffix(self) -> str:
        """
        Gets or sets the suffix of the marker.
        """
        GetDllLibPdf().PdfOrderedMarker_get_Suffix.argtypes = [c_void_p]
        GetDllLibPdf().PdfOrderedMarker_get_Suffix.restype = c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPdf().PdfOrderedMarker_get_Suffix,self.Ptr))
        return ret

    @Suffix.setter
    def Suffix(self, value: str):
        GetDllLibPdf().PdfOrderedMarker_set_Suffix.argtypes = [c_void_p, c_wchar_p]
        CallCFunction(GetDllLibPdf().PdfOrderedMarker_set_Suffix,self.Ptr, value)