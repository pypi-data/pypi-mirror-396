from enum import Enum
from plum import dispatch
from typing import TypeVar, Union, Generic, List, Tuple
from spire.pdf.common import *
from spire.pdf import *
from ctypes import *
import abc

class PdfTextReplacer(SpireObject):
    """
    Represents the text replace.
    """

    @dispatch
    def __init__(self, page: PdfPageBase):
        """
        Initializes a new instance of the PdfTextReplacer class.
        
        Args:
            page: The PdfPageBase object.
        """
        ptrPage: c_void_p = page.Ptr

        GetDllLibPdf().PdfTextReplacer_CreatePdfTextReplacerP.argtypes = [c_void_p]
        GetDllLibPdf().PdfTextReplacer_CreatePdfTextReplacerP.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfTextReplacer_CreatePdfTextReplacerP,ptrPage)
        super(PdfTextReplacer, self).__init__(intPtr)

    def ReplaceText(self, oldText: str, newText: str):
        """
        Replaces the target text in the page.
        
        Args:
            oldText: The old text.
            newText: The new text.
        """
        GetDllLibPdf().PdfTextReplacer_ReplaceText.argtypes = [c_void_p, c_wchar_p, c_wchar_p]
        CallCFunction(GetDllLibPdf().PdfTextReplacer_ReplaceText,self.Ptr, oldText, newText)

    @dispatch
    def ReplaceAllText(self, oldText: str, newText: str):
        """
        Replaces all the text in the page.
        
        Args:
            oldText: The old text.
            newText: The new text.
        """
        GetDllLibPdf().PdfTextReplacer_ReplaceAllText.argtypes = [c_void_p, c_wchar_p, c_wchar_p]
        CallCFunction(GetDllLibPdf().PdfTextReplacer_ReplaceAllText,self.Ptr, oldText, newText)

    @dispatch
    def ReplaceAllText(self, oldText: str, newText: str, textColor: Color):
        """
        Replaces all target text in the page.
        
        Args:
            oldText: The old text.
            newText: The new text.
            textColor: The color of the new text.
        """
        intPtrtextColor: c_void_p = textColor.Ptr

        GetDllLibPdf().PdfTextReplacer_ReplaceAllTextONT.argtypes = [c_void_p, c_wchar_p, c_wchar_p, c_void_p]
        CallCFunction(GetDllLibPdf().PdfTextReplacer_ReplaceAllTextONT,self.Ptr, oldText, newText, intPtrtextColor)

    def Dispose(self):
        """
        Releases all resources used.
        """
        GetDllLibPdf().PdfTextReplacer_Dispose.argtypes = [c_void_p]
        CallCFunction(GetDllLibPdf().PdfTextReplacer_Dispose,self.Ptr)

    @property
    def Options(self)->'PdfTextReplaceOptions':
        """

        """
        GetDllLibPdf().PdfTextReplacer_get_TextReplaceOptions.argtypes=[c_void_p]
        GetDllLibPdf().PdfTextReplacer_get_TextReplaceOptions.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfTextReplacer_get_TextReplaceOptions,self.Ptr)
        ret = None if intPtr==None else PdfTextReplaceOptions(intPtr)
        return ret


    @Options.setter
    def Options(self, value:'PdfTextReplaceOptions'):
        GetDllLibPdf().PdfTextReplacer_set_TextReplaceOptions.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPdf().PdfTextReplacer_set_TextReplaceOptions,self.Ptr, value.Ptr)