from enum import Enum
from plum import dispatch
from typing import TypeVar, Union, Generic, List, Tuple
from spire.pdf.common import *
from spire.pdf import *
from ctypes import *
import abc

class PdfDrawWidget(PdfShapeWidget):
    """
    Describes a graphics element which can be drawn by a pen.
    """

    @property
    def Pen(self) -> 'PdfPen':
        """
        Gets or sets a pen that will be used to draw the element.
        """
        GetDllLibPdf().PdfDrawWidget_get_Pen.argtypes = [c_void_p]
        GetDllLibPdf().PdfDrawWidget_get_Pen.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfDrawWidget_get_Pen,self.Ptr)
        ret = None if intPtr == None else PdfPen(intPtr)
        return ret

    @Pen.setter
    def Pen(self, value: 'PdfPen'):
        GetDllLibPdf().PdfDrawWidget_set_Pen.argtypes = [c_void_p, c_void_p]
        CallCFunction(GetDllLibPdf().PdfDrawWidget_set_Pen,self.Ptr, value.Ptr)