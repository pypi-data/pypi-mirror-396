from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.pdf.common import *
from spire.pdf import *
from ctypes import *
import abc

class PdfTextFinder (SpireObject) :
    """
    Representing the way how to find text on a page.
    """
    @dispatch
    def __init__(self, page:PdfPageBase):
        intPtrPage:c_void_p = page.Ptr

        GetDllLibPdf().PdfTextFinder_CreatePdfTextFinderP.argtypes=[c_void_p]
        GetDllLibPdf().PdfTextFinder_CreatePdfTextFinderP.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfTextFinder_CreatePdfTextFinderP,intPtrPage)
        super(PdfTextFinder, self).__init__(intPtr)

    @property

    def Options(self)->'PdfTextFindOptions':
        """

        """
        GetDllLibPdf().PdfTextFinder_get_Options.argtypes=[c_void_p]
        GetDllLibPdf().PdfTextFinder_get_Options.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfTextFinder_get_Options,self.Ptr)
        ret = None if intPtr==None else PdfTextFindOptions(intPtr)
        return ret


    @Options.setter
    def Options(self, value:'PdfTextFindOptions'):
        GetDllLibPdf().PdfTextFinder_set_Options.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPdf().PdfTextFinder_set_Options,self.Ptr, value.Ptr)


    def Find(self ,text:str)->List[PdfTextFragment]:
        """
        Find target text.

        Args:
            text (str): The target text.

        Returns:
            List[PdfTextFragment]: Returns the PdfTextFragment as PdfTextFragment[].
        """		
        GetDllLibPdf().PdfTextFinder_Find.argtypes=[c_void_p ,c_wchar_p]
        GetDllLibPdf().PdfTextFinder_Find.restype=IntPtrArray
        intPtrArray = CallCFunction(GetDllLibPdf().PdfTextFinder_Find,self.Ptr, text)
        ret = GetObjVectorFromArray(intPtrArray, PdfTextFragment)
        return ret




    def FindAllText(self)->List[PdfTextFragment]:
        """
        Find all text in the page

        Returns:
            List[PdfTextFragment]: All text find in the page.
        """		
        GetDllLibPdf().PdfTextFinder_FindAllText.argtypes=[c_void_p]
        GetDllLibPdf().PdfTextFinder_FindAllText.restype=IntPtrArray
        intPtrArray = CallCFunction(GetDllLibPdf().PdfTextFinder_FindAllText,self.Ptr)
        ret = GetObjVectorFromArray(intPtrArray, PdfTextFragment)
        return ret



    def Dispose(self):
        """
        Releases all resources used.
        """
        GetDllLibPdf().PdfTextFinder_Dispose.argtypes=[c_void_p]
        CallCFunction(GetDllLibPdf().PdfTextFinder_Dispose,self.Ptr)

