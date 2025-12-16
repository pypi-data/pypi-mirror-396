from enum import Enum
from plum import dispatch
from typing import TypeVar, Union, Generic, List, Tuple
from spire.pdf.common import *
from spire.pdf import *
from ctypes import *
import abc

class PdfList(PdfListBase):
    """
    Represents a PDF list.
    """

    @dispatch
    def __init__(self):
        """
        Initializes a new instance of the PdfList class.
        """
        GetDllLibPdf().PdfList_CreatePdfList.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfList_CreatePdfList)
        super(PdfList, self).__init__(intPtr)

    @dispatch
    def __init__(self, items: PdfListItemCollection):
        """
        Initializes a new instance of the PdfList class with the specified items.
        
        Args: items: The items to be added to the list.
        """
        ptrItem: c_void_p = items.Ptr
        GetDllLibPdf().PdfList_CreatePdfListI.argtypes = [c_void_p]
        GetDllLibPdf().PdfList_CreatePdfListI.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfList_CreatePdfListI,ptrItem)
        super(PdfList, self).__init__(intPtr)

    @dispatch
    def __init__(self, font: PdfFontBase):
        """
        Initializes a new instance of the PdfList class with the specified font.
        
        Args: font: The font to be used in the list.
        """
        ptrFont: c_void_p = font.Ptr
        GetDllLibPdf().PdfList_CreatePdfListF.argtypes = [c_void_p]
        GetDllLibPdf().PdfList_CreatePdfListF.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfList_CreatePdfListF,ptrFont)
        super(PdfList, self).__init__(intPtr)

    @dispatch
    def __init__(self, marker: PdfMarker):
        """
        Initializes a new instance of the PdfList class with the specified marker.
        
        Args: marker: The marker to be used in the list.
        """
        ptrMarker: c_void_p = marker.Ptr
        GetDllLibPdf().PdfList_CreatePdfListM.argtypes = [c_void_p]
        GetDllLibPdf().PdfList_CreatePdfListM.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfList_CreatePdfListM,ptrMarker)
        super(PdfList, self).__init__(intPtr)

    @dispatch
    def __init__(self, items: PdfListItemCollection, marker: PdfMarker):
        """
        Initializes a new instance of the PdfList class with the specified items and marker.
        
        Args: items: The items to be added to the list.
        Args: marker: The marker to be used in the list.
        """
        ptrItem: c_void_p = items.Ptr
        ptrMarker: c_void_p = marker.Ptr
        GetDllLibPdf().PdfList_CreatePdfListIM.argtypes = [c_void_p, c_void_p]
        GetDllLibPdf().PdfList_CreatePdfListIM.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfList_CreatePdfListIM,ptrItem, ptrMarker)
        super(PdfList, self).__init__(intPtr)

    @dispatch
    def __init__(self, text: str):
        """
        Initializes a new instance of the PdfList class with the specified text.
        
        Args: text: The text to be added to the list.
        """
        GetDllLibPdf().PdfList_CreatePdfListT.argtypes = [c_wchar_p]
        GetDllLibPdf().PdfList_CreatePdfListT.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfList_CreatePdfListT,text)
        super(PdfList, self).__init__(intPtr)

    @dispatch
    def __init__(self, text: str, marker: PdfMarker):
        """
        Initializes a new instance of the PdfList class with the specified text and marker.
        
        Args: text: The text to be added to the list.
        Args: marker: The marker to be used in the list.
        """
        ptrMarker: c_void_p = marker.Ptr
        GetDllLibPdf().PdfList_CreatePdfListTM.argtypes = [c_wchar_p, c_void_p]
        GetDllLibPdf().PdfList_CreatePdfListTM.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfList_CreatePdfListTM,text, ptrMarker)
        super(PdfList, self).__init__(intPtr)

    @property
    def Marker(self) -> 'PdfMarker':
        """
        Gets or sets the marker of the list.
        """
        GetDllLibPdf().PdfList_get_Marker.argtypes = [c_void_p]
        GetDllLibPdf().PdfList_get_Marker.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfList_get_Marker,self.Ptr)
        ret = None if intPtr == None else PdfMarker(intPtr)
        return ret

    @Marker.setter
    def Marker(self, value: 'PdfMarker'):
        """
        Sets the marker of the list.
        
        Args: value: The marker to be set.
        """
        GetDllLibPdf().PdfList_set_Marker.argtypes = [c_void_p, c_void_p]
        CallCFunction(GetDllLibPdf().PdfList_set_Marker,self.Ptr, value.Ptr)