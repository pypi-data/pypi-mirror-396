from enum import Enum
from plum import dispatch
from typing import TypeVar, Union, Generic, List, Tuple
from spire.pdf.common import *
from spire.pdf import *
from ctypes import *
import abc

class PdfToMarkdownConverter(SpireObject):
    """
    This class provides support for converting PDF into an Markdown Document. 
    """
    @dispatch
    def __init__(self, filePath:str):
        GetDllLibPdf().PdfToMarkdownConverter_CreatePdfToMarkdownConverterF.argtypes=[c_wchar_p]
        GetDllLibPdf().PdfToMarkdownConverter_CreatePdfToMarkdownConverterF.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfToMarkdownConverter_CreatePdfToMarkdownConverterF,filePath)
        super(PdfToMarkdownConverter, self).__init__(intPtr)
    @dispatch
    def __init__(self, filePath:str,password:str):
        GetDllLibPdf().PdfToMarkdownConverter_CreatePdfToMarkdownConverterFP.argtypes=[c_wchar_p,c_wchar_p]
        GetDllLibPdf().PdfToMarkdownConverter_CreatePdfToMarkdownConverterFP.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfToMarkdownConverter_CreatePdfToMarkdownConverterFP,filePath,password)
        super(PdfToMarkdownConverter, self).__init__(intPtr)

    @dispatch
    def __init__(self, stream:Stream):
        ptrStream:c_void_p = stream.Ptr
        GetDllLibPdf().PdfToMarkdownConverter_CreatePdfToMarkdownConverterS.argtypes=[c_void_p]
        GetDllLibPdf().PdfToMarkdownConverter_CreatePdfToMarkdownConverterS.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfToMarkdownConverter_CreatePdfToMarkdownConverterS,ptrStream)
        super(PdfToMarkdownConverter, self).__init__(intPtr)
    @dispatch
    def __init__(self, stream:Stream,password:str):
        ptrStream:c_void_p = stream.Ptr
        GetDllLibPdf().PdfToMarkdownConverter_CreatePdfToMarkdownConverterSP.argtypes=[c_void_p,c_wchar_p]
        GetDllLibPdf().PdfToMarkdownConverter_CreatePdfToMarkdownConverterSP.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfToMarkdownConverter_CreatePdfToMarkdownConverterSP,ptrStream,password)
        super(PdfToMarkdownConverter, self).__init__(intPtr)

    @dispatch
    def ConvertToMarkdown(self ,filePath:str):
        """
        Convert to markdown document.
		
        Args:
            filePath (str): The out file path.
        """
        
        GetDllLibPdf().PdfToMarkdownConverter_ConvertToMarkdownF.argtypes=[c_void_p ,c_wchar_p]
        CallCFunction(GetDllLibPdf().PdfToMarkdownConverter_ConvertToMarkdownF,self.Ptr, filePath)

    @dispatch
    def ConvertToMarkdown(self ,stream:Stream):
        """
        Convert to markdown document.

        Args:
            stream (Stream): The out stream.	
        """
        intPtrstream:c_void_p = stream.Ptr

        GetDllLibPdf().PdfToMarkdownConverter_ConvertToMarkdownS.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibPdf().PdfToMarkdownConverter_ConvertToMarkdownS,self.Ptr, intPtrstream)

    @property
    def MarkdownOptions(self) -> 'MarkdownOptions':
        """
        Gets or sets the options for markdown conversion.

        Returns:
            MarkdownOptions: The option for markdown document. 
        """
        GetDllLibPdf().PdfToMarkdownConverter_get_MarkdownOptions.argtypes = [c_void_p]
        GetDllLibPdf().PdfToMarkdownConverter_get_MarkdownOptions.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfToMarkdownConverter_get_MarkdownOptions,self.Ptr)
        ret = None if intPtr == None else MarkdownOptions(intPtr)
        return ret

    @MarkdownOptions.setter
    def MarkdownOptions(self, value: 'MarkdownOptions'):
        """
        Gets or sets the options for markdown conversion.

        Args:
            value (MarkdownOptions): The option for markdown document. 
        """
        GetDllLibPdf().PdfToMarkdownConverter_set_MarkdownOptions.argtypes = [c_void_p, c_void_p]
        CallCFunction(GetDllLibPdf().PdfToMarkdownConverter_set_MarkdownOptions,self.Ptr, value.Ptr)
