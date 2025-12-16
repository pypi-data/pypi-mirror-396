from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.pdf.common import *
from spire.pdf import *
from ctypes import *
import abc

class PdfTrueTypeFont (  PdfFontBase) :
    """
    Represents TrueType font.
    """
    @dispatch
    def __init__(self, fontFile:str,size:float):
        GetDllLibPdf().PdfTrueTypeFont_CreatePdfTrueTypeFontFfS.argtypes=[c_wchar_p,c_float]
        GetDllLibPdf().PdfTrueTypeFont_CreatePdfTrueTypeFontFfS.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfTrueTypeFont_CreatePdfTrueTypeFontFfS,fontFile,size)
        super(PdfTrueTypeFont, self).__init__(intPtr)

    @dispatch
    def __init__(self, fontFile:str,size:float,style:PdfFontStyle):
        enumfontStyle:c_int = style.value
        GetDllLibPdf().PdfTrueTypeFont_CreatePdfTrueTypeFontFSS.argtypes=[c_wchar_p,c_float,c_int]
        GetDllLibPdf().PdfTrueTypeFont_CreatePdfTrueTypeFontFSS.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfTrueTypeFont_CreatePdfTrueTypeFontFSS,fontFile,size,enumfontStyle)
        super(PdfTrueTypeFont, self).__init__(intPtr)

    @dispatch
    def __init__(self, fontName:str,size:float,style:PdfFontStyle,unicodeBl:bool):
        enumfontStyle:c_int = style.value
        GetDllLibPdf().PdfTrueTypeFont_CreatePdfTrueTypeFontFSSU.argtypes=[c_wchar_p,c_float,c_int,c_bool]
        GetDllLibPdf().PdfTrueTypeFont_CreatePdfTrueTypeFontFSSU.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfTrueTypeFont_CreatePdfTrueTypeFontFSSU,fontName,size,enumfontStyle,unicodeBl)
        super(PdfTrueTypeFont, self).__init__(intPtr)
    @dispatch
    def __init__(self, fontName:str,size:float,intFontStyle:int,unicodeBl:bool):
        GetDllLibPdf().PdfTrueTypeFont_CreatePdfTrueTypeFontFSSU.argtypes=[c_wchar_p,c_float,c_int,c_bool]
        GetDllLibPdf().PdfTrueTypeFont_CreatePdfTrueTypeFontFSSU.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfTrueTypeFont_CreatePdfTrueTypeFontFSSU,fontName,size,intFontStyle,unicodeBl)
        super(PdfTrueTypeFont, self).__init__(intPtr)

    @property
    def Unicode(self)->bool:
        """

        """
        GetDllLibPdf().PdfTrueTypeFont_get_Unicode.argtypes=[c_void_p]
        GetDllLibPdf().PdfTrueTypeFont_get_Unicode.restype=c_bool
        ret = CallCFunction(GetDllLibPdf().PdfTrueTypeFont_get_Unicode,self.Ptr)
        return ret

    def Dispose(self):
        """

        """
        GetDllLibPdf().PdfTrueTypeFont_Dispose.argtypes=[c_void_p]
        CallCFunction(GetDllLibPdf().PdfTrueTypeFont_Dispose,self.Ptr)

