from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.pdf.common import *
from spire.pdf import *
from ctypes import *
import abc

class PdfSeparationColor (  PdfComplexColor) :
    """
    Represents a separation color, based on a separation colorspace. 
    """
    @dispatch
    def __init__(self, colorspace:PdfColorSpaces,tint:float):
        ptrColor:c_void_p = colorspace.Ptr

        GetDllLibPdf().PdfSeparationColor_CreatePdfSeparationColorCT.argtypes=[c_void_p,c_float]
        GetDllLibPdf().PdfSeparationColor_CreatePdfSeparationColorCT.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfSeparationColor_CreatePdfSeparationColorCT,ptrColor,tint)
        super(PdfSeparationColor, self).__init__(intPtr)

    @property
    def Tint(self)->float:
        """
        The acceptable range for this value is [0.0 1.0]. 0.0 means the lightest color that can be achieved, and 1.0 means the darkest color.
        """
        GetDllLibPdf().PdfSeparationColor_get_Tint.argtypes=[c_void_p]
        GetDllLibPdf().PdfSeparationColor_get_Tint.restype=c_float
        ret = CallCFunction(GetDllLibPdf().PdfSeparationColor_get_Tint,self.Ptr)
        return ret

    @Tint.setter
    def Tint(self, value:float):
        GetDllLibPdf().PdfSeparationColor_set_Tint.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPdf().PdfSeparationColor_set_Tint,self.Ptr, value)

