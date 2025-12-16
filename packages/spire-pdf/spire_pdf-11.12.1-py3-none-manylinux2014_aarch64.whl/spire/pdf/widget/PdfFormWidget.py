from enum import Enum
from plum import dispatch
from typing import TypeVar, Union, Generic, List, Tuple
from spire.pdf.common import *
from spire.pdf import *
from ctypes import *
import abc

class PdfFormWidget(PdfForm):
    """
    Represents Loaded form.
    """

    @property
    def FieldsWidget(self) -> 'PdfFormFieldWidgetCollection':
        """
        Gets the field collection.
        """
        GetDllLibPdf().PdfFormWidget_get_FieldsWidget.argtypes = [c_void_p]
        GetDllLibPdf().PdfFormWidget_get_FieldsWidget.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfFormWidget_get_FieldsWidget,self.Ptr)
        ret = None if intPtr == None else PdfFormFieldWidgetCollection(intPtr)
        return ret

    @property
    def ReadOnly(self) -> bool:
        """
        Gets or sets a value indicating whether the form is read only.
        True if the field is read-only, false otherwise. Default is false.
        """
        GetDllLibPdf().PdfFormWidget_get_ReadOnly.argtypes = [c_void_p]
        GetDllLibPdf().PdfFormWidget_get_ReadOnly.restype = c_bool
        ret = CallCFunction(GetDllLibPdf().PdfFormWidget_get_ReadOnly,self.Ptr)
        return ret

    @ReadOnly.setter
    def ReadOnly(self, value: bool):
        GetDllLibPdf().PdfFormWidget_set_ReadOnly.argtypes = [c_void_p, c_bool]
        CallCFunction(GetDllLibPdf().PdfFormWidget_set_ReadOnly,self.Ptr, value)

    @property
    def XFAForm(self) -> 'XFAForm':
        """
        Gets XFA data of the form.
        """
        GetDllLibPdf().PdfFormWidget_get_XFAForm.argtypes = [c_void_p]
        GetDllLibPdf().PdfFormWidget_get_XFAForm.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfFormWidget_get_XFAForm,self.Ptr)
        ret = None if intPtr == None else XFAForm(intPtr)
        return ret

    @property
    def IsDynamicForm(self) -> bool:
        """
        Gets a value indicating whether the form is dynamic.
        """
        GetDllLibPdf().PdfFormWidget_get_IsDynamicForm.argtypes = [c_void_p]
        GetDllLibPdf().PdfFormWidget_get_IsDynamicForm.restype = c_bool
        ret = CallCFunction(GetDllLibPdf().PdfFormWidget_get_IsDynamicForm,self.Ptr)
        return ret

    @property
    def NeedAppearances(self) -> bool:
        """
        Gets or sets a value indicating whether need appearances.
        """
        GetDllLibPdf().PdfFormWidget_get_NeedAppearances.argtypes = [c_void_p]
        GetDllLibPdf().PdfFormWidget_get_NeedAppearances.restype = c_bool
        ret = CallCFunction(GetDllLibPdf().PdfFormWidget_get_NeedAppearances,self.Ptr)
        return ret

    @NeedAppearances.setter
    def NeedAppearances(self, value: bool):
        GetDllLibPdf().PdfFormWidget_set_NeedAppearances.argtypes = [c_void_p, c_bool]
        CallCFunction(GetDllLibPdf().PdfFormWidget_set_NeedAppearances,self.Ptr, value)

    def SetFieldValueForXFAForm(self, field: 'PdfField', value: str) -> bool:
        """
        Sets the field value for XFA form.
        """
        intPtrfield: c_void_p = field.Ptr

        GetDllLibPdf().PdfFormWidget_SetFieldValueForXFAForm.argtypes = [c_void_p, c_void_p, c_wchar_p]
        GetDllLibPdf().PdfFormWidget_SetFieldValueForXFAForm.restype = c_bool
        ret = CallCFunction(GetDllLibPdf().PdfFormWidget_SetFieldValueForXFAForm,self.Ptr, intPtrfield, value)
        return ret

    @dispatch
    def ExportData(self, fileName: str, dataFormat: DataFormat, formName: str):
        """
        Export the form data to a file.
        """
        enumdataFormat: c_int = dataFormat.value

        GetDllLibPdf().PdfFormWidget_ExportData.argtypes = [c_void_p, c_wchar_p, c_int, c_wchar_p]
        CallCFunction(GetDllLibPdf().PdfFormWidget_ExportData,self.Ptr, fileName, enumdataFormat, formName)

    @dispatch
    def ExportData(self, stream: Stream, dataFormat: DataFormat, formName: str):
        """
        Export the form data to a file.
        """
        intPtrstream: c_void_p = stream.Ptr
        enumdataFormat: c_int = dataFormat.value

        GetDllLibPdf().PdfFormWidget_ExportDataSDF.argtypes = [c_void_p, c_void_p, c_int, c_wchar_p]
        CallCFunction(GetDllLibPdf().PdfFormWidget_ExportDataSDF,self.Ptr, intPtrstream, enumdataFormat, formName)

    @dispatch
    def ImportData(self, fileName: str, dataFormat: DataFormat):
        """
        Imports the data.
        """
        enumdataFormat: c_int = dataFormat.value

        GetDllLibPdf().PdfFormWidget_ImportData.argtypes = [c_void_p, c_wchar_p, c_int]
        CallCFunction(GetDllLibPdf().PdfFormWidget_ImportData,self.Ptr, fileName, enumdataFormat)

    def ImportDataXFDF(self, fileName: str):
        """
        Import form data from XFDF file.
        """
        GetDllLibPdf().PdfFormWidget_ImportDataXFDF.argtypes = [c_void_p, c_wchar_p]
        CallCFunction(GetDllLibPdf().PdfFormWidget_ImportDataXFDF,self.Ptr, fileName)

    def HighlightFields(self, highlight: bool):
        """
        Sets/Resets the form field highlight option.
        """
        GetDllLibPdf().PdfFormWidget_HighlightFields.argtypes = [c_void_p, c_bool]
        CallCFunction(GetDllLibPdf().PdfFormWidget_HighlightFields,self.Ptr, highlight)

    def OnlyHexInString(self, test: str) -> bool:
        """
        Checks if the string contains only hexadecimal characters.
        """
        GetDllLibPdf().PdfFormWidget_OnlyHexInString.argtypes = [c_void_p, c_wchar_p]
        GetDllLibPdf().PdfFormWidget_OnlyHexInString.restype = c_bool
        ret = CallCFunction(GetDllLibPdf().PdfFormWidget_OnlyHexInString,self.Ptr, test)
        return ret

    @property
    def ExtractSignatureAsImages(self)->List['Stream']:
        GetDllLibPdf().PdfFormWidget_ExtractSignatureAsImages.argtypes=[c_void_p]
        GetDllLibPdf().PdfFormWidget_ExtractSignatureAsImages.restype=IntPtrArray
        intPtrArray = CallCFunction(GetDllLibPdf().PdfFormWidget_ExtractSignatureAsImages,self.Ptr)
        ret = GetObjVectorFromArray(intPtrArray, Stream)
        return ret