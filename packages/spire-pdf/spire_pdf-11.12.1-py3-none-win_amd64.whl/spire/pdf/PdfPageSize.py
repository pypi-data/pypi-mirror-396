from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.pdf.common import *
from spire.pdf import *
from ctypes import *
import abc

class PdfPageSize (SpireObject) :
    """
    Represents information about page size.
    """
    @staticmethod

    def Letter()->'SizeF':
        """
        Letter format.
        """
        #GetDllLibPdf().PdfPageSize_Letter.argtypes=[]
        GetDllLibPdf().PdfPageSize_Letter.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfPageSize_Letter)
        ret = None if intPtr==None else SizeF(intPtr)
        return ret


    @staticmethod

    def Note()->'SizeF':
        """
        Note format.
        """
        #GetDllLibPdf().PdfPageSize_Note.argtypes=[]
        GetDllLibPdf().PdfPageSize_Note.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfPageSize_Note)
        ret = None if intPtr==None else SizeF(intPtr)
        return ret


    @staticmethod

    def Legal()->'SizeF':
        """
        Legal format.
        """
        #GetDllLibPdf().PdfPageSize_Legal.argtypes=[]
        GetDllLibPdf().PdfPageSize_Legal.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfPageSize_Legal)
        ret = None if intPtr==None else SizeF(intPtr)
        return ret


    @staticmethod

    def A0()->'SizeF':
        """
        A0 format.
        """
        #GetDllLibPdf().PdfPageSize_A0.argtypes=[]
        GetDllLibPdf().PdfPageSize_A0.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfPageSize_A0)
        ret = None if intPtr==None else SizeF(intPtr)
        return ret


    @staticmethod

    def A1()->'SizeF':
        """
        A1 format.
        """
        #GetDllLibPdf().PdfPageSize_A1.argtypes=[]
        GetDllLibPdf().PdfPageSize_A1.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfPageSize_A1)
        ret = None if intPtr==None else SizeF(intPtr)
        return ret


    @staticmethod

    def A2()->'SizeF':
        """
        A2 format.
        """
        #GetDllLibPdf().PdfPageSize_A2.argtypes=[]
        GetDllLibPdf().PdfPageSize_A2.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfPageSize_A2)
        ret = None if intPtr==None else SizeF(intPtr)
        return ret


    @staticmethod

    def A3()->'SizeF':
        """
        A3 format.
        """
        #GetDllLibPdf().PdfPageSize_A3.argtypes=[]
        GetDllLibPdf().PdfPageSize_A3.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfPageSize_A3)
        ret = None if intPtr==None else SizeF(intPtr)
        return ret


    @staticmethod

    def A4()->'SizeF':
        """
        A4 format.
        """
        #GetDllLibPdf().PdfPageSize_A4.argtypes=[]
        GetDllLibPdf().PdfPageSize_A4.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfPageSize_A4)
        ret = None if intPtr==None else SizeF(intPtr)
        return ret


    @staticmethod

    def A5()->'SizeF':
        """
        A5 format.
        """
        #GetDllLibPdf().PdfPageSize_A5.argtypes=[]
        GetDllLibPdf().PdfPageSize_A5.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfPageSize_A5)
        ret = None if intPtr==None else SizeF(intPtr)
        return ret


    @staticmethod

    def A6()->'SizeF':
        """
        A6 format.
        """
        #GetDllLibPdf().PdfPageSize_A6.argtypes=[]
        GetDllLibPdf().PdfPageSize_A6.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfPageSize_A6)
        ret = None if intPtr==None else SizeF(intPtr)
        return ret


    @staticmethod

    def A7()->'SizeF':
        """
        A7 format.
        """
        #GetDllLibPdf().PdfPageSize_A7.argtypes=[]
        GetDllLibPdf().PdfPageSize_A7.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfPageSize_A7)
        ret = None if intPtr==None else SizeF(intPtr)
        return ret


    @staticmethod

    def A8()->'SizeF':
        """
        A8 format.
        """
        #GetDllLibPdf().PdfPageSize_A8.argtypes=[]
        GetDllLibPdf().PdfPageSize_A8.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfPageSize_A8)
        ret = None if intPtr==None else SizeF(intPtr)
        return ret


    @staticmethod

    def A9()->'SizeF':
        """
        A9 format.
        """
        #GetDllLibPdf().PdfPageSize_A9.argtypes=[]
        GetDllLibPdf().PdfPageSize_A9.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfPageSize_A9)
        ret = None if intPtr==None else SizeF(intPtr)
        return ret


    @staticmethod

    def A10()->'SizeF':
        """
        A10 format.
        """
        #GetDllLibPdf().PdfPageSize_A10.argtypes=[]
        GetDllLibPdf().PdfPageSize_A10.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfPageSize_A10)
        ret = None if intPtr==None else SizeF(intPtr)
        return ret


    @staticmethod

    def B0()->'SizeF':
        """
        B0 format.
        """
        #GetDllLibPdf().PdfPageSize_B0.argtypes=[]
        GetDllLibPdf().PdfPageSize_B0.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfPageSize_B0)
        ret = None if intPtr==None else SizeF(intPtr)
        return ret


    @staticmethod

    def B1()->'SizeF':
        """
        B1 format.
        """
        #GetDllLibPdf().PdfPageSize_B1.argtypes=[]
        GetDllLibPdf().PdfPageSize_B1.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfPageSize_B1)
        ret = None if intPtr==None else SizeF(intPtr)
        return ret


    @staticmethod

    def B2()->'SizeF':
        """
        B2 format.
        """
        #GetDllLibPdf().PdfPageSize_B2.argtypes=[]
        GetDllLibPdf().PdfPageSize_B2.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfPageSize_B2)
        ret = None if intPtr==None else SizeF(intPtr)
        return ret


    @staticmethod

    def B3()->'SizeF':
        """
        B3 format.
        """
        #GetDllLibPdf().PdfPageSize_B3.argtypes=[]
        GetDllLibPdf().PdfPageSize_B3.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfPageSize_B3)
        ret = None if intPtr==None else SizeF(intPtr)
        return ret


    @staticmethod

    def B4()->'SizeF':
        """
        B4 format.
        """
        #GetDllLibPdf().PdfPageSize_B4.argtypes=[]
        GetDllLibPdf().PdfPageSize_B4.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfPageSize_B4)
        ret = None if intPtr==None else SizeF(intPtr)
        return ret


    @staticmethod

    def B5()->'SizeF':
        """
        B5 format.
        """
        #GetDllLibPdf().PdfPageSize_B5.argtypes=[]
        GetDllLibPdf().PdfPageSize_B5.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfPageSize_B5)
        ret = None if intPtr==None else SizeF(intPtr)
        return ret


    @staticmethod

    def ArchE()->'SizeF':
        """
        ArchE format.
        """
        #GetDllLibPdf().PdfPageSize_ArchE.argtypes=[]
        GetDllLibPdf().PdfPageSize_ArchE.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfPageSize_ArchE)
        ret = None if intPtr==None else SizeF(intPtr)
        return ret


    @staticmethod

    def ArchD()->'SizeF':
        """
        ArchD format.
        """
        #GetDllLibPdf().PdfPageSize_ArchD.argtypes=[]
        GetDllLibPdf().PdfPageSize_ArchD.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfPageSize_ArchD)
        ret = None if intPtr==None else SizeF(intPtr)
        return ret


    @staticmethod

    def ArchC()->'SizeF':
        """
        ArchC format.
        """
        #GetDllLibPdf().PdfPageSize_ArchC.argtypes=[]
        GetDllLibPdf().PdfPageSize_ArchC.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfPageSize_ArchC)
        ret = None if intPtr==None else SizeF(intPtr)
        return ret


    @staticmethod

    def ArchB()->'SizeF':
        """
        ArchB format.
        """
        #GetDllLibPdf().PdfPageSize_ArchB.argtypes=[]
        GetDllLibPdf().PdfPageSize_ArchB.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfPageSize_ArchB)
        ret = None if intPtr==None else SizeF(intPtr)
        return ret


    @staticmethod

    def ArchA()->'SizeF':
        """
        ArchA format.
        """
        #GetDllLibPdf().PdfPageSize_ArchA.argtypes=[]
        GetDllLibPdf().PdfPageSize_ArchA.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfPageSize_ArchA)
        ret = None if intPtr==None else SizeF(intPtr)
        return ret


    @staticmethod

    def Flsa()->'SizeF':
        """
        The American Foolscap format.
        """
        #GetDllLibPdf().PdfPageSize_Flsa.argtypes=[]
        GetDllLibPdf().PdfPageSize_Flsa.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfPageSize_Flsa)
        ret = None if intPtr==None else SizeF(intPtr)
        return ret


    @staticmethod

    def HalfLetter()->'SizeF':
        """
        HalfLetter format.
        """
        #GetDllLibPdf().PdfPageSize_HalfLetter.argtypes=[]
        GetDllLibPdf().PdfPageSize_HalfLetter.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfPageSize_HalfLetter)
        ret = None if intPtr==None else SizeF(intPtr)
        return ret


    @staticmethod

    def Letter11x17()->'SizeF':
        """
        11x17 format.
        """
        #GetDllLibPdf().PdfPageSize_Letter11x17.argtypes=[]
        GetDllLibPdf().PdfPageSize_Letter11x17.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfPageSize_Letter11x17)
        ret = None if intPtr==None else SizeF(intPtr)
        return ret


    @staticmethod

    def Ledger()->'SizeF':
        """
        Ledger format.
        """
        #GetDllLibPdf().PdfPageSize_Ledger.argtypes=[]
        GetDllLibPdf().PdfPageSize_Ledger.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfPageSize_Ledger)
        ret = None if intPtr==None else SizeF(intPtr)
        return ret


