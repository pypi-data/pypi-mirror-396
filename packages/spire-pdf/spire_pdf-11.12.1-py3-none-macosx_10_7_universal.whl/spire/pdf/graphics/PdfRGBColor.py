from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.pdf.common import *
from spire.pdf import *
from ctypes import *
import abc

class PdfRGBColor (SpireObject) :
    """
    Implements structures and routines working with color.
    """
    @dispatch
    def __init__(self, color:Color):
        ptrColor:c_void_p = color.Ptr
        GetDllLibPdf().PdfRGBColor_CreatePdfRGBColorC.argtypes=[c_void_p]
        GetDllLibPdf().PdfRGBColor_CreatePdfRGBColorC.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfRGBColor_CreatePdfRGBColorC,ptrColor)
        super(PdfRGBColor, self).__init__(intPtr)

    @dispatch
    def __init__(self, gray:float ):
        GetDllLibPdf().PdfRGBColor_CreatePdfRGBColorG.argtypes=[c_float]
        GetDllLibPdf().PdfRGBColor_CreatePdfRGBColorG.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfRGBColor_CreatePdfRGBColorG,gray)
        super(PdfRGBColor, self).__init__(intPtr)

    @dispatch
    def __init__(self, red:int , green:int , blue:int ):
        GetDllLibPdf().PdfRGBColor_CreatePdfRGBColorRGB.argtypes=[c_int,c_int,c_int]
        GetDllLibPdf().PdfRGBColor_CreatePdfRGBColorRGB.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfRGBColor_CreatePdfRGBColorRGB,red, green, blue)
        super(PdfRGBColor, self).__init__(intPtr)

    @dispatch
    def __init__(self, cyan:float, magenta:float, yellow:float, black:float):
        GetDllLibPdf().PdfRGBColor_CreatePdfRGBColorCMYB.argtypes=[c_float,c_float,c_float,c_float]
        GetDllLibPdf().PdfRGBColor_CreatePdfRGBColorCMYB.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfRGBColor_CreatePdfRGBColorCMYB,cyan, magenta, yellow, black)
        super(PdfRGBColor, self).__init__(intPtr)


    @staticmethod

    def get_Empty()->'PdfRGBColor':
        """
        Gets a null color.
        """
        #GetDllLibPdf().PdfRGBColor_get_Empty.argtypes=[]
        GetDllLibPdf().PdfRGBColor_get_Empty.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfRGBColor_get_Empty)
        ret = None if intPtr==None else PdfRGBColor(intPtr)
        return ret


    @property
    def IsEmpty(self)->bool:
        """
        Gets whether the PDFColor is Empty or not.
        """
        GetDllLibPdf().PdfRGBColor_get_IsEmpty.argtypes=[c_void_p]
        GetDllLibPdf().PdfRGBColor_get_IsEmpty.restype=c_bool
        ret = CallCFunction(GetDllLibPdf().PdfRGBColor_get_IsEmpty,self.Ptr)
        return ret

    @property
    def B(self)->int:
        """
        Gets or sets Blue channel value.
        """
        GetDllLibPdf().PdfRGBColor_get_B.argtypes=[c_void_p]
        GetDllLibPdf().PdfRGBColor_get_B.restype=c_int
        ret = CallCFunction(GetDllLibPdf().PdfRGBColor_get_B,self.Ptr)
        return ret

    @B.setter
    def B(self, value:int):
        GetDllLibPdf().PdfRGBColor_set_B.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPdf().PdfRGBColor_set_B,self.Ptr, value)

    @property
    def Blue(self)->float:
        """
        Gets the blue.
        """
        GetDllLibPdf().PdfRGBColor_get_Blue.argtypes=[c_void_p]
        GetDllLibPdf().PdfRGBColor_get_Blue.restype=c_float
        ret = CallCFunction(GetDllLibPdf().PdfRGBColor_get_Blue,self.Ptr)
        return ret

    @property
    def C(self)->float:
        """
        Gets or sets Cyan channel value.
        """
        GetDllLibPdf().PdfRGBColor_get_C.argtypes=[c_void_p]
        GetDllLibPdf().PdfRGBColor_get_C.restype=c_float
        ret = CallCFunction(GetDllLibPdf().PdfRGBColor_get_C,self.Ptr)
        return ret

    @C.setter
    def C(self, value:float):
        GetDllLibPdf().PdfRGBColor_set_C.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPdf().PdfRGBColor_set_C,self.Ptr, value)

    @property
    def G(self)->int:
        """
        Gets or sets Green channel value.
        """
        GetDllLibPdf().PdfRGBColor_get_G.argtypes=[c_void_p]
        GetDllLibPdf().PdfRGBColor_get_G.restype=c_int
        ret = CallCFunction(GetDllLibPdf().PdfRGBColor_get_G,self.Ptr)
        return ret

    @G.setter
    def G(self, value:int):
        GetDllLibPdf().PdfRGBColor_set_G.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPdf().PdfRGBColor_set_G,self.Ptr, value)

    @property
    def Green(self)->float:
        """
        Gets the green.
        """
        GetDllLibPdf().PdfRGBColor_get_Green.argtypes=[c_void_p]
        GetDllLibPdf().PdfRGBColor_get_Green.restype=c_float
        ret = CallCFunction(GetDllLibPdf().PdfRGBColor_get_Green,self.Ptr)
        return ret

    @property
    def Gray(self)->float:
        """
        Gets or sets Gray channel value.
        """
        GetDllLibPdf().PdfRGBColor_get_Gray.argtypes=[c_void_p]
        GetDllLibPdf().PdfRGBColor_get_Gray.restype=c_float
        ret = CallCFunction(GetDllLibPdf().PdfRGBColor_get_Gray,self.Ptr)
        return ret

    @Gray.setter
    def Gray(self, value:float):
        GetDllLibPdf().PdfRGBColor_set_Gray.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPdf().PdfRGBColor_set_Gray,self.Ptr, value)

    @property
    def K(self)->float:
        """
        Gets or sets Black channel value.
        """
        GetDllLibPdf().PdfRGBColor_get_K.argtypes=[c_void_p]
        GetDllLibPdf().PdfRGBColor_get_K.restype=c_float
        ret = CallCFunction(GetDllLibPdf().PdfRGBColor_get_K,self.Ptr)
        return ret

    @K.setter
    def K(self, value:float):
        GetDllLibPdf().PdfRGBColor_set_K.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPdf().PdfRGBColor_set_K,self.Ptr, value)

    @property
    def M(self)->float:
        """
        Gets or sets Magenta channel value.
        """
        GetDllLibPdf().PdfRGBColor_get_M.argtypes=[c_void_p]
        GetDllLibPdf().PdfRGBColor_get_M.restype=c_float
        ret = CallCFunction(GetDllLibPdf().PdfRGBColor_get_M,self.Ptr)
        return ret

    @M.setter
    def M(self, value:float):
        GetDllLibPdf().PdfRGBColor_set_M.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPdf().PdfRGBColor_set_M,self.Ptr, value)

    @property
    def R(self)->int:
        """
        Gets or sets Red channel value.
        """
        GetDllLibPdf().PdfRGBColor_get_R.argtypes=[c_void_p]
        GetDllLibPdf().PdfRGBColor_get_R.restype=c_int
        ret = CallCFunction(GetDllLibPdf().PdfRGBColor_get_R,self.Ptr)
        return ret

    @R.setter
    def R(self, value:int):
        GetDllLibPdf().PdfRGBColor_set_R.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPdf().PdfRGBColor_set_R,self.Ptr, value)

    @property
    def Red(self)->float:
        """
        Gets the red.
        """
        GetDllLibPdf().PdfRGBColor_get_Red.argtypes=[c_void_p]
        GetDllLibPdf().PdfRGBColor_get_Red.restype=c_float
        ret = CallCFunction(GetDllLibPdf().PdfRGBColor_get_Red,self.Ptr)
        return ret

    @property
    def Y(self)->float:
        """
        Gets or sets Yellow channel value.
        """
        GetDllLibPdf().PdfRGBColor_get_Y.argtypes=[c_void_p]
        GetDllLibPdf().PdfRGBColor_get_Y.restype=c_float
        ret = CallCFunction(GetDllLibPdf().PdfRGBColor_get_Y,self.Ptr)
        return ret

    @Y.setter
    def Y(self, value:float):
        GetDllLibPdf().PdfRGBColor_set_Y.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPdf().PdfRGBColor_set_Y,self.Ptr, value)

    def ToArgb(self)->int:
        """
        Creates the Alpha ,Red ,Green, and Blue value of this PDFColor structure.
        """
        GetDllLibPdf().PdfRGBColor_ToArgb.argtypes=[c_void_p]
        GetDllLibPdf().PdfRGBColor_ToArgb.restype=c_int
        ret = CallCFunction(GetDllLibPdf().PdfRGBColor_ToArgb,self.Ptr)
        return ret

    @staticmethod
    @dispatch

    def op_Implicit(color:Color)->'PdfRGBColor':
        """

        """
        intPtrcolor:c_void_p = color.Ptr

        GetDllLibPdf().PdfRGBColor_op_Implicit.argtypes=[ c_void_p]
        GetDllLibPdf().PdfRGBColor_op_Implicit.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfRGBColor_op_Implicit, intPtrcolor)
        ret = None if intPtr==None else PdfRGBColor(intPtr)
        return ret


    @staticmethod
    @dispatch

    def op_Implicit(color:'PdfRGBColor')->Color:
        """

        """
        intPtrcolor:c_void_p = color.Ptr

        GetDllLibPdf().PdfRGBColor_op_ImplicitC.argtypes=[ c_void_p]
        GetDllLibPdf().PdfRGBColor_op_ImplicitC.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfRGBColor_op_ImplicitC, intPtrcolor)
        ret = None if intPtr==None else Color(intPtr)
        return ret


    @staticmethod

    def op_Equality(colour1:'PdfRGBColor',colour2:'PdfRGBColor')->bool:
        """
        Operator ==.

        Args:
            colour1 (PdfRGBColor): he color 1.
			colour2 (PdfRGBColor): he color 1.
        
		Returns:
            True if color 1 is not equal to color 2; otherwise False.
        """		
        intPtrcolour1:c_void_p = colour1.Ptr
        intPtrcolour2:c_void_p = colour2.Ptr

        GetDllLibPdf().PdfRGBColor_op_Equality.argtypes=[ c_void_p,c_void_p]
        GetDllLibPdf().PdfRGBColor_op_Equality.restype=c_bool
        ret = CallCFunction(GetDllLibPdf().PdfRGBColor_op_Equality, intPtrcolour1,intPtrcolour2)
        return ret

    @staticmethod

    def op_Inequality(colour1:'PdfRGBColor',colour2:'PdfRGBColor')->bool:
        """
        Operator !=.

        Args:
            colour1 (PdfRGBColor): The color 1.
			colour2 (PdfRGBColor): The color 1.
			
        Returns:
            True if color 1 is not equal to color 2; otherwise False.
        """			
        intPtrcolour1:c_void_p = colour1.Ptr
        intPtrcolour2:c_void_p = colour2.Ptr

        GetDllLibPdf().PdfRGBColor_op_Inequality.argtypes=[ c_void_p,c_void_p]
        GetDllLibPdf().PdfRGBColor_op_Inequality.restype=c_bool
        ret = CallCFunction(GetDllLibPdf().PdfRGBColor_op_Inequality, intPtrcolour1,intPtrcolour2)
        return ret

    @dispatch

    def Equals(self ,obj:SpireObject)->bool:
        """
        Determines whether the specified 
            is equal to the current .

        Args:
            obj (SpireObject): The to compare with the current .
        
		Returns:
            True if the specified is equal to the current ; otherwise - False.
        """		
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPdf().PdfRGBColor_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPdf().PdfRGBColor_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPdf().PdfRGBColor_Equals,self.Ptr, intPtrobj)
        return ret

    @dispatch

    def Equals(self ,colour:'PdfRGBColor')->bool:
        """
        Determines if the specified color is equal to this one.

        Args:
            colour (PdfRGBColor): The color.
        
		Returns:
            True if the color is equal; otherwise - False.
        """		
        intPtrcolour:c_void_p = colour.Ptr

        GetDllLibPdf().PdfRGBColor_EqualsC.argtypes=[c_void_p ,c_void_p]
        GetDllLibPdf().PdfRGBColor_EqualsC.restype=c_bool
        ret = CallCFunction(GetDllLibPdf().PdfRGBColor_EqualsC,self.Ptr, intPtrcolour)
        return ret

    def GetHashCode(self)->int:
        """
        Serves as a hash function for a particular type, suitable for
            use in hashing algorithms and data structures like a hash
            table.
        
		Returns:
            A hash code for the current .
        """		
        GetDllLibPdf().PdfRGBColor_GetHashCode.argtypes=[c_void_p]
        GetDllLibPdf().PdfRGBColor_GetHashCode.restype=c_int
        ret = CallCFunction(GetDllLibPdf().PdfRGBColor_GetHashCode,self.Ptr)
        return ret

