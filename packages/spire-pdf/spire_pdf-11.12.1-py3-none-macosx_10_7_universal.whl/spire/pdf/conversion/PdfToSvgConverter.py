from enum import Enum
from plum import dispatch
from typing import TypeVar, Union, Generic, List, Tuple
from spire.pdf.common import *
from spire.pdf import *
from ctypes import *
import abc

class PdfToSvgConverter(SpireObject):
    """
    The pdf to svg converter.
    """
    @dispatch
    def __init__(self, filePath:str):
        GetDllLibPdf().PdfToSvgConverter_CreatePdfToSvgConverterF.argtypes=[c_wchar_p]
        GetDllLibPdf().PdfToSvgConverter_CreatePdfToSvgConverterF.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfToSvgConverter_CreatePdfToSvgConverterF,filePath)
        super(PdfToSvgConverter, self).__init__(intPtr)
    @dispatch
    def __init__(self, filePath:str,password:str):
        GetDllLibPdf().PdfToSvgConverter_CreatePdfToSvgConverterFP.argtypes=[c_wchar_p,c_wchar_p]
        GetDllLibPdf().PdfToSvgConverter_CreatePdfToSvgConverterFP.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfToSvgConverter_CreatePdfToSvgConverterFP,filePath,password)
        super(PdfToSvgConverter, self).__init__(intPtr)

    @dispatch
    def __init__(self, stream:Stream):
        ptrStream:c_void_p = stream.Ptr
        GetDllLibPdf().PdfToSvgConverter_CreatePdfToSvgConverterS.argtypes=[c_void_p]
        GetDllLibPdf().PdfToSvgConverter_CreatePdfToSvgConverterS.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfToSvgConverter_CreatePdfToSvgConverterS,ptrStream)
        super(PdfToSvgConverter, self).__init__(intPtr)
    @dispatch
    def __init__(self, stream:Stream,password:str):
        ptrStream:c_void_p = stream.Ptr
        GetDllLibPdf().PdfToSvgConverter_CreatePdfToSvgConverterSP.argtypes=[c_void_p,c_wchar_p]
        GetDllLibPdf().PdfToSvgConverter_CreatePdfToSvgConverterSP.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfToSvgConverter_CreatePdfToSvgConverterSP,ptrStream,password)
        super(PdfToSvgConverter, self).__init__(intPtr)

    @property
    def SvgOptions(self) -> 'SvgOptions':
        """
        Gets or sets the options for SvgOptions.

        Returns:
            MarkdownOptions: The option for svg. 
        """
        GetDllLibPdf().PdfToSvgConverter_get_SvgOptions.argtypes = [c_void_p]
        GetDllLibPdf().PdfToSvgConverter_get_SvgOptions.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfToSvgConverter_get_SvgOptions,self.Ptr)
        ret = None if intPtr == None else SvgOptions(intPtr)
        return ret

    @SvgOptions.setter
    def SvgOptions(self, value: 'SvgOptions'):
        """
        Gets or sets the options for SvgOptions.

        Args:
            value (SvgOptions): The option for svg. 
        """
        GetDllLibPdf().PdfToSvgConverter_set_SvgOptions.argtypes = [c_void_p, c_void_p]
        CallCFunction(GetDllLibPdf().PdfToSvgConverter_set_SvgOptions,self.Ptr, value.Ptr)

    @dispatch
    def Convert(self ,filePath:str):
        """
        Convert to svg document.
		
        Args:
            filePath (str): The out file path.
        """
        
        GetDllLibPdf().PdfToSvgConverter_ConvertF.argtypes=[c_void_p ,c_wchar_p]
        CallCFunction(GetDllLibPdf().PdfToSvgConverter_ConvertF,self.Ptr, filePath)

    @dispatch
    def Convert(self )->List['Stream']:
        """
        Convert to svg document.

        Args:
            stream (Stream): The out stream.	
        """
        GetDllLibPdf().PdfToSvgConverter_ConvertS.argtypes=[c_void_p]
        GetDllLibPdf().PdfToSvgConverter_ConvertS.restype=IntPtrArray
        intPtrArray = CallCFunction(GetDllLibPdf().PdfToSvgConverter_ConvertS,self.Ptr)
        ret = GetObjVectorFromArray(intPtrArray, Stream)
        return ret