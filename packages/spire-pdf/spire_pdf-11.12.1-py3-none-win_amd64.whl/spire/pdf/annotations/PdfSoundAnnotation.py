from enum import Enum
from plum import dispatch
from typing import TypeVar, Union, Generic, List, Tuple
from spire.pdf.common import *
from spire.pdf import *
from ctypes import *
import abc

class PdfSoundAnnotation(PdfFileAnnotation):
    """
    Represents the sound annotation.
    """

    @property
    def Icon(self) -> 'PdfSoundIcon':
        """
        Gets or sets the icon to be used in displaying the annotation.
        
        Returns:
            The enumeration member specifying the icon for the annotation.
        """
        GetDllLibPdf().PdfSoundAnnotation_get_Icon.argtypes = [c_void_p]
        GetDllLibPdf().PdfSoundAnnotation_get_Icon.restype = c_int
        ret = CallCFunction(GetDllLibPdf().PdfSoundAnnotation_get_Icon,self.Ptr)
        objwrapped = PdfSoundIcon(ret)
        return objwrapped

    @Icon.setter
    def Icon(self, value: 'PdfSoundIcon'):
        """
        Sets the icon to be used in displaying the annotation.
        
        Args:
            value: The enumeration member specifying the icon for the annotation.
        """
        GetDllLibPdf().PdfSoundAnnotation_set_Icon.argtypes = [c_void_p, c_int]
        CallCFunction(GetDllLibPdf().PdfSoundAnnotation_set_Icon,self.Ptr, value.value)

    @property
    def Sound(self) -> 'PdfSound':
        """
        Gets or sets the sound.
        
        Returns:
            The object specified a sound for the annotation.
        """
        GetDllLibPdf().PdfSoundAnnotation_get_Sound.argtypes = [c_void_p]
        GetDllLibPdf().PdfSoundAnnotation_get_Sound.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfSoundAnnotation_get_Sound,self.Ptr)
        ret = None if intPtr == None else PdfSound(intPtr)
        return ret

    @Sound.setter
    def Sound(self, value: 'PdfSound'):
        """
        Sets the sound.
        
        Args:
            value: The object specifying a sound for the annotation.
        """
        GetDllLibPdf().PdfSoundAnnotation_set_Sound.argtypes = [c_void_p, c_void_p]
        CallCFunction(GetDllLibPdf().PdfSoundAnnotation_set_Sound,self.Ptr, value.Ptr)

    @property
    def FileName(self) -> str:
        """
        Gets or sets the file name of the sound annotation.
        
        Returns:
            The string specifying the file name of the sound annotation.
        """
        GetDllLibPdf().PdfSoundAnnotation_get_FileName.argtypes = [c_void_p]
        GetDllLibPdf().PdfSoundAnnotation_get_FileName.restype = c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPdf().PdfSoundAnnotation_get_FileName,self.Ptr))
        return ret

    @FileName.setter
    def FileName(self, value: str):
        """
        Sets the file name of the sound annotation.
        
        Args:
            value: The string specifying the file name of the sound annotation.
        """
        GetDllLibPdf().PdfSoundAnnotation_set_FileName.argtypes = [c_void_p, c_wchar_p]
        CallCFunction(GetDllLibPdf().PdfSoundAnnotation_set_FileName,self.Ptr, value)