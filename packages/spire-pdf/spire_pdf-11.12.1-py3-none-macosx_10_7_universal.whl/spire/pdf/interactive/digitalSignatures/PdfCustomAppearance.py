from enum import Enum
from plum import dispatch
from typing import TypeVar, Union, Generic, List, Tuple
from spire.pdf.common import *
from spire.pdf import *
from ctypes import *
import abc

class PdfCustomAppearance(IPdfSignatureAppearance):
    def __init__(self,s:str,fontSize:float,font:PdfFontBase,brush:PdfBrush,strPoint:PointF,imageFile:str,imgPoint:PointF):
        intPtrfont:c_void_p = font.Ptr if font!=None else None
        intPtrbrush:c_void_p = brush.Ptr if brush!=None else None
        intPtrsPoint:c_void_p = strPoint.Ptr if strPoint!=None else None
        intPtriPoint:c_void_p = imgPoint.Ptr if imgPoint!=None else None
        GetDllLibPdf().PdfSignatureAppearance_CreatePdfCustomAppearance.argtypes=[c_wchar_p,c_float,c_void_p,c_void_p,c_void_p,c_wchar_p,c_void_p]
        GetDllLibPdf().PdfSignatureAppearance_CreatePdfCustomAppearance.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfSignatureAppearance_CreatePdfCustomAppearance,s,fontSize,intPtrfont,intPtrbrush,intPtrsPoint,imageFile,intPtriPoint)
        super(PdfCustomAppearance, self).__init__(intPtr)
    def Generate(self):
    #    """
    #    Generate custom signature appearance by a graphics context.
    #    Args: g: A graphics context of signature appearance.
    #    """
    #    #intPtrg: c_void_p = g.Ptr

    #    #GetDllLibPdf().PdfSignatureAppearance_Generate.argtypes = [c_void_p, c_void_p]
    #    #CallCFunction(GetDllLibPdf().PdfSignatureAppearance_Generate,self.Ptr, intPtrg)
        pass
