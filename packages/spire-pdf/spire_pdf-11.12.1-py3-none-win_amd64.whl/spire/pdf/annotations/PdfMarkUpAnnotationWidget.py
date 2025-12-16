from enum import Enum
from plum import dispatch
from typing import TypeVar, Union, Generic, List, Tuple
from spire.pdf.common import *
from spire.pdf import *
from ctypes import *
from datetime import datetime
import abc

class PdfMarkUpAnnotationWidget(PdfStyledAnnotationWidget):
    """
    Represents the loaded markup annotation class.
    """

    @property
    def Intent(self) -> str:
        """
        Gets or sets the intent.
        """
        GetDllLibPdf().PdfMarkUpAnnotationWidget_get_Intent.argtypes = [c_void_p]
        GetDllLibPdf().PdfMarkUpAnnotationWidget_get_Intent.restype = c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPdf().PdfMarkUpAnnotationWidget_get_Intent,self.Ptr))
        return ret

    @Intent.setter
    def Intent(self, value: str):
        """
        Sets the intent.
        """
        GetDllLibPdf().PdfMarkUpAnnotationWidget_set_Intent.argtypes = [c_void_p, c_wchar_p]
        CallCFunction(GetDllLibPdf().PdfMarkUpAnnotationWidget_set_Intent,self.Ptr, value)

    @property
    def Author(self) -> str:
        """
        Gets or sets the annotation's author.
        """
        GetDllLibPdf().PdfMarkUpAnnotationWidget_get_Author.argtypes = [c_void_p]
        GetDllLibPdf().PdfMarkUpAnnotationWidget_get_Author.restype = c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPdf().PdfMarkUpAnnotationWidget_get_Author,self.Ptr))
        return ret

    @Author.setter
    def Author(self, value: str):
        """
        Sets the annotation's author.
        """
        GetDllLibPdf().PdfMarkUpAnnotationWidget_set_Author.argtypes = [c_void_p, c_wchar_p]
        CallCFunction(GetDllLibPdf().PdfMarkUpAnnotationWidget_set_Author,self.Ptr, value)

    @property
    def CreationDate(self) -> datetime:
        """
        Gets or sets the date and time when the annotation was created.
        """
        GetDllLibPdf().PdfMarkUpAnnotationWidget_get_CreationDate.argtypes = [c_void_p]
        GetDllLibPdf().PdfMarkUpAnnotationWidget_get_CreationDate.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfMarkUpAnnotationWidget_get_CreationDate,self.Ptr)
        ret = None if intPtr == None else PtrToDatetime(intPtr)
        return ret

    @CreationDate.setter
    def CreationDate(self, value: datetime):
        """
        Sets the date and time when the annotation was created.
        """
        GetDllLibPdf().PdfMarkUpAnnotationWidget_set_CreationDate.argtypes = [c_void_p, c_void_p]
        CallCFunction(GetDllLibPdf().PdfMarkUpAnnotationWidget_set_CreationDate,self.Ptr, DatetimeToPtr(value))

    @property
    def Subject(self) -> str:
        """
        Gets or sets the annotation's subject.
        """
        GetDllLibPdf().PdfMarkUpAnnotationWidget_get_Subject.argtypes = [c_void_p]
        GetDllLibPdf().PdfMarkUpAnnotationWidget_get_Subject.restype = c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPdf().PdfMarkUpAnnotationWidget_get_Subject,self.Ptr))
        return ret

    @Subject.setter
    def Subject(self, value: str):
        """
        Sets the annotation's subject.
        """
        GetDllLibPdf().PdfMarkUpAnnotationWidget_set_Subject.argtypes = [c_void_p, c_wchar_p]
        CallCFunction(GetDllLibPdf().PdfMarkUpAnnotationWidget_set_Subject,self.Ptr, value)

    @property
    def Opacity(self) -> float:
        """
        Gets the opacity value to be used.
        """
        GetDllLibPdf().PdfMarkUpAnnotationWidget_get_Opacity.argtypes = [c_void_p]
        GetDllLibPdf().PdfMarkUpAnnotationWidget_get_Opacity.restype = c_float
        ret = CallCFunction(GetDllLibPdf().PdfMarkUpAnnotationWidget_get_Opacity,self.Ptr)
        return ret

    def SetTitleText(self, text: str):
        """
        Sets the name of the annotation, the entry is deleted by default when the input value is an empty string.
        """
        GetDllLibPdf().PdfMarkUpAnnotationWidget_SetTitleText.argtypes = [c_void_p, c_wchar_p]
        CallCFunction(GetDllLibPdf().PdfMarkUpAnnotationWidget_SetTitleText,self.Ptr, text)

    def ObjectID(self) -> int:
        """
        Represents the Form field identifier.
        """
        GetDllLibPdf().PdfMarkUpAnnotationWidget_ObjectID.argtypes = [c_void_p]
        GetDllLibPdf().PdfMarkUpAnnotationWidget_ObjectID.restype = c_int
        ret = CallCFunction(GetDllLibPdf().PdfMarkUpAnnotationWidget_ObjectID,self.Ptr)
        return ret
