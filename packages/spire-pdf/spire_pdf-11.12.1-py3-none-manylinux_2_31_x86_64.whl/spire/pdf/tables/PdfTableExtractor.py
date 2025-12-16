from enum import Enum
from plum import dispatch
from typing import TypeVar, Union, Generic, List, Tuple
from spire.pdf.common import *
from spire.pdf import *
from ctypes import *
import abc

class PdfTableExtractor(SpireObject):
    """
    Represents the PDF table extractor.
    """
    @dispatch
    def __init__(self, pdfDocument:PdfDocument):
        intPtrpdfDocument:c_void_p = pdfDocument.Ptr
        GetDllLibPdf().PdfTableExtractor_CreatePdfTableExtractorD.argtypes=[c_void_p]
        GetDllLibPdf().PdfTableExtractor_CreatePdfTableExtractorD.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfTableExtractor_CreatePdfTableExtractorD,intPtrpdfDocument)
        super(PdfTableExtractor, self).__init__(intPtr)

    def ExtractTable(self, pageIndex: int) -> List['Utilities_PdfTable']:
        """
        Extracts table from the PDF document.

        Args:
            pageIndex: The index of the page.

        Returns:
            An array of PdfTable.
        """
        GetDllLibPdf().PdfTableExtractor_ExtractTable.argtypes = [c_void_p, c_int]
        GetDllLibPdf().PdfTableExtractor_ExtractTable.restype = IntPtrArray
        intPtrArray = CallCFunction(GetDllLibPdf().PdfTableExtractor_ExtractTable,self.Ptr, pageIndex)
        ret = GetObjVectorFromArray(intPtrArray, Utilities_PdfTable)
        return ret

    def Dispose(self):
        """
        Disposes the PDF table extractor.
        """
        GetDllLibPdf().PdfTableExtractor_Dispose.argtypes = [c_void_p]
        CallCFunction(GetDllLibPdf().PdfTableExtractor_Dispose,self.Ptr)