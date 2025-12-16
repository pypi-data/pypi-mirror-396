from enum import Enum
from plum import dispatch
from typing import TypeVar, Union, Generic, List, Tuple
from spire.pdf.common import *
from spire.pdf import *
from ctypes import *
import abc

class PdfAttributeOwner(SpireObject):
    """
    The attribute owners.
    """

    @property
    def Name(self) -> str:
        """
        The name of the application or plug-in extension owning the attribute data.
        """
        GetDllLibPdf().PdfAttributeOwner_get_Name.argtypes = [c_void_p]
        GetDllLibPdf().PdfAttributeOwner_get_Name.restype = c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPdf().PdfAttributeOwner_get_Name,self.Ptr))
        return ret

    @staticmethod
    def Layout() -> 'PdfAttributeOwner':
        """
        Attributes governing the layout of content.
        """
        GetDllLibPdf().PdfAttributeOwner_Layout.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfAttributeOwner_Layout)
        ret = None if intPtr == None else PdfAttributeOwner(intPtr)
        return ret

    @staticmethod
    def List() -> 'PdfAttributeOwner':
        """
        Attributes governing the numbering of lists.
        """
        GetDllLibPdf().PdfAttributeOwner_List.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfAttributeOwner_List)
        ret = None if intPtr == None else PdfAttributeOwner(intPtr)
        return ret

    @staticmethod
    def PrintField() -> 'PdfAttributeOwner':
        """
        Attributes governing Form structure elements for non-interactive form fields.
        """
        GetDllLibPdf().PdfAttributeOwner_PrintField.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfAttributeOwner_PrintField)
        ret = None if intPtr == None else PdfAttributeOwner(intPtr)
        return ret

    @staticmethod
    def Table() -> 'PdfAttributeOwner':
        """
        Attributes governing the organization of cells in tables.
        """
        GetDllLibPdf().PdfAttributeOwner_Table.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfAttributeOwner_Table)
        ret = None if intPtr == None else PdfAttributeOwner(intPtr)
        return ret

    @staticmethod
    def Xml_100() -> 'PdfAttributeOwner':
        """
        Additional attributes governing translation to XML, version 1.00
        """
        GetDllLibPdf().PdfAttributeOwner_Xml_100.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfAttributeOwner_Xml_100)
        ret = None if intPtr == None else PdfAttributeOwner(intPtr)
        return ret

    @staticmethod
    def Html_320() -> 'PdfAttributeOwner':
        """
        Additional attributes governing translation to HTML, version 3.20
        """
        GetDllLibPdf().PdfAttributeOwner_Html_320.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfAttributeOwner_Html_320)
        ret = None if intPtr == None else PdfAttributeOwner(intPtr)
        return ret

    @staticmethod
    def Html_401() -> 'PdfAttributeOwner':
        """
        Additional attributes governing translation to HTML, version 4.01
        """
        GetDllLibPdf().PdfAttributeOwner_Html_401.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfAttributeOwner_Html_401)
        ret = None if intPtr == None else PdfAttributeOwner(intPtr)
        return ret

    @staticmethod
    def Oeb_100() -> 'PdfAttributeOwner':
        """
        Additional attributes governing translation to OEB, version 1.0
        """
        GetDllLibPdf().PdfAttributeOwner_Oeb_100.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfAttributeOwner_Oeb_100)
        ret = None if intPtr == None else PdfAttributeOwner(intPtr)
        return ret

    @staticmethod
    def Rtf_105() -> 'PdfAttributeOwner':
        """
        Additional attributes governing translation to Microsoft Rich Text Format, version 1.05
        """
        GetDllLibPdf().PdfAttributeOwner_Rtf_105.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfAttributeOwner_Rtf_105)
        ret = None if intPtr == None else PdfAttributeOwner(intPtr)
        return ret

    @staticmethod
    def Css_100() -> 'PdfAttributeOwner':
        """
        Additional attributes governing translation to a format using CSS, version 1.00
        """
        GetDllLibPdf().PdfAttributeOwner_Css_100.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfAttributeOwner_Css_100)
        ret = None if intPtr == None else PdfAttributeOwner(intPtr)
        return ret

    @staticmethod
    def Css_200() -> 'PdfAttributeOwner':
        """
        Additional attributes governing translation to a format using CSS, version 2.00
        """
        GetDllLibPdf().PdfAttributeOwner_Css_200.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfAttributeOwner_Css_200)
        ret = None if intPtr == None else PdfAttributeOwner(intPtr)
        return ret