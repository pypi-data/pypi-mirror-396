from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.pdf.common import *
from spire.pdf import *
from ctypes import *
import abc

class PdfConvertOptions (SpireObject) :
    """
        The class can be used to set some options when do convert operation.
    """
    @property
    def FindTextByAbsolutePosition(self)->bool:
        """
        Find Text in PDF file by absolute position or operator order.default is true. 
        """
        GetDllLibPdf().PdfConvertOptions_get_FindTextByAbsolutePosition.argtypes=[c_void_p]
        GetDllLibPdf().PdfConvertOptions_get_FindTextByAbsolutePosition.restype=c_bool
        ret = CallCFunction(GetDllLibPdf().PdfConvertOptions_get_FindTextByAbsolutePosition,self.Ptr)
        return ret

    @FindTextByAbsolutePosition.setter
    def FindTextByAbsolutePosition(self, value:bool):
        GetDllLibPdf().PdfConvertOptions_set_FindTextByAbsolutePosition.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPdf().PdfConvertOptions_set_FindTextByAbsolutePosition,self.Ptr, value)


    def SetPdfToImageOptions(self ,bgTransparentValue:int):
        """
        Set pdf to image convert options.

        Args:
            bgTransparentValue (int): Alpha values rang from 0 to 255
        """        
        GetDllLibPdf().PdfConvertOptions_SetPdfToImageOptions.argtypes=[c_void_p ,c_int]
        CallCFunction(GetDllLibPdf().PdfConvertOptions_SetPdfToImageOptions,self.Ptr, bgTransparentValue)


    def SetPdfToXlsxOptions(self ,options:'XlsxOptions'):
        """
        Set pdf to xlsx convert options
            the parameter is：the implementation class the xlsxOptions class
            The implementation class:XlsxLineLayoutOptions or XlsxTextLayoutOptions

        Args:
            options (XlsxOptions): 
        """ 		
        intPtroptions:c_void_p = options.Ptr

        GetDllLibPdf().PdfConvertOptions_SetPdfToXlsxOptions.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibPdf().PdfConvertOptions_SetPdfToXlsxOptions,self.Ptr, intPtroptions)

    def SetPdfToOfdOptions(self ,options:'OfdOptions'):
        """
        Set pdf to ofd convert options
            the parameter is：the implementation class the OfdOptions class

        Args:
            options (OfdOptions): 
        """ 		
        intPtroptions:c_void_p = options.Ptr

        GetDllLibPdf().PdfConvertOptions_SetPdfToOfdOptions.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibPdf().PdfConvertOptions_SetPdfToOfdOptions,self.Ptr, intPtroptions)
    @dispatch
    def SetPdfToXpsOptions(self):
        """
        Set pdf to xps convert options.
            Default usePsMode = true,useInvariantCulture = false,useHighQualityImg = false.
        """
        GetDllLibPdf().PdfConvertOptions_SetPdfToXpsOptions.argtypes=[c_void_p]
        CallCFunction(GetDllLibPdf().PdfConvertOptions_SetPdfToXpsOptions,self.Ptr)

    @dispatch

    def SetPdfToXpsOptions(self ,usePsMode:bool):
        """
        Set pdf to xps convert options.

        Args:
            usePsMode (bool): Indicates whether to use PS mode.
        """        
        GetDllLibPdf().PdfConvertOptions_SetPdfToXpsOptionsU.argtypes=[c_void_p ,c_bool]
        CallCFunction(GetDllLibPdf().PdfConvertOptions_SetPdfToXpsOptionsU,self.Ptr, usePsMode)

    @dispatch

    def SetPdfToXpsOptions(self ,usePsMode:bool,useInvariantCulture:bool):
        """
        Set pdf to xps convert options.

        Args:
            usePsMode (bool): Indicates whether to use PS mode.
			useInvariantCulture (bool): Indicates whether to use invariant culture.
        """          
        GetDllLibPdf().PdfConvertOptions_SetPdfToXpsOptionsUU.argtypes=[c_void_p ,c_bool,c_bool]
        CallCFunction(GetDllLibPdf().PdfConvertOptions_SetPdfToXpsOptionsUU,self.Ptr, usePsMode,useInvariantCulture)

    @dispatch

    def SetPdfToXpsOptions(self ,usePsMode:bool,useInvariantCulture:bool,useHighQualityImg:bool):
        """
        Set pdf to xps convert options.

        Args:
            usePsMode (bool): Indicates whether to use PS mode.
			useInvariantCulture (bool): Indicates whether to use invariant culture.
			useHighQualityImg (bool): Indicates whether to use the high qulity image.
        """         
        GetDllLibPdf().PdfConvertOptions_SetPdfToXpsOptionsUUU.argtypes=[c_void_p ,c_bool,c_bool,c_bool]
        CallCFunction(GetDllLibPdf().PdfConvertOptions_SetPdfToXpsOptionsUUU,self.Ptr, usePsMode,useInvariantCulture,useHighQualityImg)

    @dispatch
    def SetPdfToDocOptions(self):
        """
        Set pdf to doc convert options.
            Default usePsMode = true.
        """
        GetDllLibPdf().PdfConvertOptions_SetPdfToDocOptions.argtypes=[c_void_p]
        CallCFunction(GetDllLibPdf().PdfConvertOptions_SetPdfToDocOptions,self.Ptr)

    @dispatch

    def SetPdfToDocOptions(self ,usePsMode:bool):
        """
        Set pdf to doc convert options.

        Args:
            usePsMode (bool): Indicates whether to use PS mode.
        """        
        GetDllLibPdf().PdfConvertOptions_SetPdfToDocOptionsU.argtypes=[c_void_p ,c_bool]
        CallCFunction(GetDllLibPdf().PdfConvertOptions_SetPdfToDocOptionsU,self.Ptr, usePsMode)

    @dispatch

    def SetPdfToDocOptions(self ,usePsMode:bool,useFlowRecognitionMode:bool):
        """
        Set pdf to doc convert options.

        Args:
            usePsMode (bool): Indicates whether to use PS mode.
			useFlowRecognitionMode (bool): Indicates whether to use flow recognition mode.
        """         
        GetDllLibPdf().PdfConvertOptions_SetPdfToDocOptionsUU.argtypes=[c_void_p ,c_bool,c_bool]
        CallCFunction(GetDllLibPdf().PdfConvertOptions_SetPdfToDocOptionsUU,self.Ptr, usePsMode,useFlowRecognitionMode)

    @dispatch
    def SetXpsToPdfOptions(self):
        """
        Set xps to pdf convert options.
            Default useHighQualityImg = false.
        """
        GetDllLibPdf().PdfConvertOptions_SetXpsToPdfOptions.argtypes=[c_void_p]
        CallCFunction(GetDllLibPdf().PdfConvertOptions_SetXpsToPdfOptions,self.Ptr)

    @dispatch

    def SetXpsToPdfOptions(self ,useHighQualityImg:bool):
        """
        Set xps to pdf convert options.

        Args:
            useHighQualityImg (bool): Indicates whether to use the high qulity image.
        """        
        GetDllLibPdf().PdfConvertOptions_SetXpsToPdfOptionsU.argtypes=[c_void_p ,c_bool]
        CallCFunction(GetDllLibPdf().PdfConvertOptions_SetXpsToPdfOptionsU,self.Ptr, useHighQualityImg)

    @dispatch
    def SetPdfToHtmlOptions(self):
        """
        Set pdf to html convert options.
            Default useEmbeddedSvg = true, useEmbeddedImg = false, maxPageOneFile = 500, useHighQualityEmbeddedSvg=true.
        """
        GetDllLibPdf().PdfConvertOptions_SetPdfToHtmlOptions.argtypes=[c_void_p]
        CallCFunction(GetDllLibPdf().PdfConvertOptions_SetPdfToHtmlOptions,self.Ptr)

    @dispatch

    def SetPdfToHtmlOptions(self ,useEmbeddedSvg:bool):
        """
        Set pdf to html convert options.

        Args:
            useEmbeddedSvg (bool): Indicates whether to use the embedded svg in html file.
        """  
        GetDllLibPdf().PdfConvertOptions_SetPdfToHtmlOptionsU.argtypes=[c_void_p ,c_bool]
        CallCFunction(GetDllLibPdf().PdfConvertOptions_SetPdfToHtmlOptionsU,self.Ptr, useEmbeddedSvg)

    @dispatch

    def SetPdfToHtmlOptions(self ,useEmbeddedSvg:bool,useEmbeddedImg:bool):
        """
        Set pdf to html convert options.

        Args:
            useEmbeddedSvg (bool): Indicates whether to use the embedded svg in html file.
			useEmbeddedImg (bool): Indicates whether to embed image data in html file, works only when useEmbeddedSvg is set to false.
        """        
        GetDllLibPdf().PdfConvertOptions_SetPdfToHtmlOptionsUU.argtypes=[c_void_p ,c_bool,c_bool]
        CallCFunction(GetDllLibPdf().PdfConvertOptions_SetPdfToHtmlOptionsUU,self.Ptr, useEmbeddedSvg,useEmbeddedImg)

    @dispatch

    def SetPdfToHtmlOptions(self ,useEmbeddedSvg:bool,useEmbeddedImg:bool,maxPageOneFile:int):
        """
        Set pdf to html convert options.

        Args:
            useEmbeddedSvg (bool): Indicates whether to use the embedded svg in html file.
			useEmbeddedImg (bool): Indicates whether to embed image data in html file, works only when useEmbeddedSvg is set to false.
			maxPageOneFile (bool): Indicates the count of page contents in one html file, works only when useEmbeddedSvg is set to false.
        """         
        GetDllLibPdf().PdfConvertOptions_SetPdfToHtmlOptionsUUM.argtypes=[c_void_p ,c_bool,c_bool,c_int]
        CallCFunction(GetDllLibPdf().PdfConvertOptions_SetPdfToHtmlOptionsUUM,self.Ptr, useEmbeddedSvg,useEmbeddedImg,maxPageOneFile)

    @dispatch

    def SetPdfToHtmlOptions(self ,useEmbeddedSvg:bool,useEmbeddedImg:bool,maxPageOneFile:int,useHighQualityEmbeddedSvg:bool):
        """
        Set pdf to html convert options.

        Args:
            useEmbeddedSvg (bool): Indicates whether to use the embedded svg in html file.
			useEmbeddedImg (bool): Indicates whether to embed image data in html file, works only when useEmbeddedSvg is set to false.
			maxPageOneFile (bool): Indicates the count of page contents in one html file, works only when useEmbeddedSvg is set to false.
			useHighQualityEmbeddedSvg (bool): Indicates whether to use the high quality embedded svg in html file, works only when useEmbeddedSvg is set to true.
        """ 		
        
        GetDllLibPdf().PdfConvertOptions_SetPdfToHtmlOptionsUUMU.argtypes=[c_void_p ,c_bool,c_bool,c_int,c_bool]
        CallCFunction(GetDllLibPdf().PdfConvertOptions_SetPdfToHtmlOptionsUUMU,self.Ptr, useEmbeddedSvg,useEmbeddedImg,maxPageOneFile,useHighQualityEmbeddedSvg)

  

