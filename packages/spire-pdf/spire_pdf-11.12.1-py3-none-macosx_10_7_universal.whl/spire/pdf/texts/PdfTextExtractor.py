from enum import Enum
from plum import dispatch
from typing import TypeVar, Union, Generic, List, Tuple
from spire.pdf.common import *
from spire.pdf import *
from ctypes import *
import abc

class PdfTextExtractor(SpireObject):
    """
    Represents the PDF text extractor.
    """
    def __init__(self, page:PdfPageBase):
        intPtrpage:c_void_p = page.Ptr
        GetDllLibPdf().PdfTextExtractor_CreatePdfTextExtractorP.argtypes=[c_void_p]
        GetDllLibPdf().PdfTextExtractor_CreatePdfTextExtractorP.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfTextExtractor_CreatePdfTextExtractorP,intPtrpage)
        super(PdfTextExtractor, self).__init__(intPtr)

    def ExtractText(self, options: 'PdfTextExtractOptions') -> str:
        """
        Extracts text from the page.

        Args:
            options: The options.

        Returns:
            The extracted text.
        """
        intPtroptions: c_void_p = options.Ptr

        GetDllLibPdf().PdfTextExtractor_ExtractText.argtypes = [c_void_p, c_void_p]
        GetDllLibPdf().PdfTextExtractor_ExtractText.restype = c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPdf().PdfTextExtractor_ExtractText,self.Ptr, intPtroptions))
        return ret