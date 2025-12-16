from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.pdf.common import *
from spire.pdf import *
from ctypes import *
import abc

class PdfPageSettings (SpireObject) :
    """
    Represent class with setting of page.
    """
    @dispatch
    def __init__(self):
        GetDllLibPdf().PdfPageSettings_CreatePdfPageSettings.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfPageSettings_CreatePdfPageSettings)
        super(PdfPageSettings, self).__init__(intPtr)
    @dispatch
    def __init__(self, sizef:SizeF):
        ptrsizef:c_void_p = sizef.Ptr
        GetDllLibPdf().PdfPageSettings_CreatePdfPageSettingsS.argtypes=[c_void_p]
        GetDllLibPdf().PdfPageSettings_CreatePdfPageSettingsS.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfPageSettings_CreatePdfPageSettingsS,ptrsizef)
        super(PdfPageSettings, self).__init__(intPtr)
    @dispatch
    def __init__(self, pageOrientation:PdfPageOrientation):
        enumpageOrientation:c_int = pageOrientation.value
        GetDllLibPdf().PdfPageSettings_CreatePdfPageSettingsP.argtypes=[c_int]
        GetDllLibPdf().PdfPageSettings_CreatePdfPageSettingsP.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfPageSettings_CreatePdfPageSettingsP,enumpageOrientation)
        super(PdfPageSettings, self).__init__(intPtr)
    @dispatch
    def __init__(self, sizef:SizeF,pageOrientation:PdfPageOrientation):
        ptrsizef:c_void_p = sizef.Ptr
        enumpageOrientation:c_int = pageOrientation.value
        GetDllLibPdf().PdfPageSettings_CreatePdfPageSettingsSP.argtypes=[c_void_p,c_int]
        GetDllLibPdf().PdfPageSettings_CreatePdfPageSettingsSP.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfPageSettings_CreatePdfPageSettingsSP,ptrsizef,enumpageOrientation)
        super(PdfPageSettings, self).__init__(intPtr)
    @dispatch
    def __init__(self, margins:float):
        GetDllLibPdf().PdfPageSettings_CreatePdfPageSettingsM.argtypes=[c_float]
        GetDllLibPdf().PdfPageSettings_CreatePdfPageSettingsM.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfPageSettings_CreatePdfPageSettingsM,margins)
        super(PdfPageSettings, self).__init__(intPtr)
    @dispatch
    def __init__(self,leftMargin:float, topMargin:float,rightMargin:float, bottomMargin:float):
        GetDllLibPdf().PdfPageSettings_CreatePdfPageSettingsLTRB.argtypes=[c_float,c_float,c_float,c_float]
        GetDllLibPdf().PdfPageSettings_CreatePdfPageSettingsLTRB.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfPageSettings_CreatePdfPageSettingsLTRB,leftMargin,topMargin,rightMargin,bottomMargin)
        super(PdfPageSettings, self).__init__(intPtr)
    @dispatch
    def __init__(self, sizef:SizeF,margins:float):
        ptrsizef:c_void_p = sizef.Ptr
        GetDllLibPdf().PdfPageSettings_CreatePdfPageSettingsSM.argtypes=[c_void_p,c_float]
        GetDllLibPdf().PdfPageSettings_CreatePdfPageSettingsSM.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfPageSettings_CreatePdfPageSettingsSM,ptrsizef,margins)
        super(PdfPageSettings, self).__init__(intPtr)
    @dispatch
    def __init__(self,sizef:SizeF,leftMargin:float, topMargin:float,rightMargin:float, bottomMargin:float):
        ptrsizef:c_void_p = sizef.Ptr
        GetDllLibPdf().PdfPageSettings_CreatePdfPageSettingsSLTRB.argtypes=[c_void_p,c_float,c_float,c_float,c_float]
        GetDllLibPdf().PdfPageSettings_CreatePdfPageSettingsSLTRB.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfPageSettings_CreatePdfPageSettingsSLTRB,ptrsizef,leftMargin,topMargin,rightMargin,bottomMargin)
        super(PdfPageSettings, self).__init__(intPtr)
    @dispatch
    def __init__(self, sizef:SizeF,pageOrientation:PdfPageOrientation,margins:float):
        ptrsizef:c_void_p = sizef.Ptr
        enumpageOrientation:c_int = pageOrientation.value
        GetDllLibPdf().PdfPageSettings_CreatePdfPageSettingsSPM.argtypes=[c_void_p,c_int,c_float]
        GetDllLibPdf().PdfPageSettings_CreatePdfPageSettingsSPM.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfPageSettings_CreatePdfPageSettingsSPM,ptrsizef,enumpageOrientation,margins)
        super(PdfPageSettings, self).__init__(intPtr)
    @dispatch
    def __init__(self, sizef:SizeF,pageOrientation:PdfPageOrientation,leftMargin:float,topMargin:float,rightMargin:float, bottomMargin:float):
        ptrsizef:c_void_p = sizef.Ptr
        enumpageOrientation:c_int = pageOrientation.value
        GetDllLibPdf().PdfPageSettings_CreatePdfPageSettingsSPLTRB.argtypes=[c_void_p,c_int,c_float,c_float,c_float,c_float]
        GetDllLibPdf().PdfPageSettings_CreatePdfPageSettingsSPLTRB.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfPageSettings_CreatePdfPageSettingsSPLTRB,ptrsizef,enumpageOrientation,leftMargin,topMargin,rightMargin,bottomMargin)
        super(PdfPageSettings, self).__init__(intPtr)

#    @property
#
#    def ListPaperSourceTray(self)->'List1':
#        """
#
#        """
#        GetDllLibPdf().PdfPageSettings_get_ListPaperSourceTray.argtypes=[c_void_p]
#        GetDllLibPdf().PdfPageSettings_get_ListPaperSourceTray.restype=c_void_p
#        intPtr = CallCFunction(GetDllLibPdf().PdfPageSettings_get_ListPaperSourceTray,self.Ptr)
#        ret = None if intPtr==None else List1(intPtr)
#        return ret
#


#    @ListPaperSourceTray.setter
#    def ListPaperSourceTray(self, value:'List1'):
#        GetDllLibPdf().PdfPageSettings_set_ListPaperSourceTray.argtypes=[c_void_p, c_void_p]
#        CallCFunction(GetDllLibPdf().PdfPageSettings_set_ListPaperSourceTray,self.Ptr, value.Ptr)


    @property

    def Orientation(self)->'PdfPageOrientation':
        """
        Gets or sets the page orientation.
        """
        GetDllLibPdf().PdfPageSettings_get_Orientation.argtypes=[c_void_p]
        GetDllLibPdf().PdfPageSettings_get_Orientation.restype=c_int
        ret = CallCFunction(GetDllLibPdf().PdfPageSettings_get_Orientation,self.Ptr)
        objwraped = PdfPageOrientation(ret)
        return objwraped

    @Orientation.setter
    def Orientation(self, value:'PdfPageOrientation'):
        GetDllLibPdf().PdfPageSettings_set_Orientation.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPdf().PdfPageSettings_set_Orientation,self.Ptr, value.value)

    @property

    def Size(self)->'SizeF':
        """
        Gets or sets the size of the page.
        """
        GetDllLibPdf().PdfPageSettings_get_Size.argtypes=[c_void_p]
        GetDllLibPdf().PdfPageSettings_get_Size.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfPageSettings_get_Size,self.Ptr)
        ret = None if intPtr==None else SizeF(intPtr)
        return ret


    @Size.setter
    def Size(self, value:'SizeF'):
        GetDllLibPdf().PdfPageSettings_set_Size.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPdf().PdfPageSettings_set_Size,self.Ptr, value.Ptr)

    @property
    def Width(self)->float:
        """
        Gets or sets the width of the page.
        """
        GetDllLibPdf().PdfPageSettings_get_Width.argtypes=[c_void_p]
        GetDllLibPdf().PdfPageSettings_get_Width.restype=c_float
        ret = CallCFunction(GetDllLibPdf().PdfPageSettings_get_Width,self.Ptr)
        return ret

    @Width.setter
    def Width(self, value:float):
        GetDllLibPdf().PdfPageSettings_set_Width.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPdf().PdfPageSettings_set_Width,self.Ptr, value)

    @property
    def Height(self)->float:
        """
        Gets or sets the height of the page.
        """
        GetDllLibPdf().PdfPageSettings_get_Height.argtypes=[c_void_p]
        GetDllLibPdf().PdfPageSettings_get_Height.restype=c_float
        ret = CallCFunction(GetDllLibPdf().PdfPageSettings_get_Height,self.Ptr)
        return ret

    @Height.setter
    def Height(self, value:float):
        GetDllLibPdf().PdfPageSettings_set_Height.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPdf().PdfPageSettings_set_Height,self.Ptr, value)

    @property

    def Margins(self)->'PdfMargins':
        """
        Gets or sets the margins of the page.
        """
        GetDllLibPdf().PdfPageSettings_get_Margins.argtypes=[c_void_p]
        GetDllLibPdf().PdfPageSettings_get_Margins.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfPageSettings_get_Margins,self.Ptr)
        ret = None if intPtr==None else PdfMargins(intPtr)
        return ret


    @Margins.setter
    def Margins(self, value:'PdfMargins'):
        GetDllLibPdf().PdfPageSettings_set_Margins.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPdf().PdfPageSettings_set_Margins,self.Ptr, value.Ptr)

    @property

    def Rotate(self)->'PdfPageRotateAngle':
        """
        Gets or sets the number of degrees by which the page should be rotated clockwise when displayed or printed.
        """
        GetDllLibPdf().PdfPageSettings_get_Rotate.argtypes=[c_void_p]
        GetDllLibPdf().PdfPageSettings_get_Rotate.restype=c_int
        ret = CallCFunction(GetDllLibPdf().PdfPageSettings_get_Rotate,self.Ptr)
        objwraped = PdfPageRotateAngle(ret)
        return objwraped

    @Rotate.setter
    def Rotate(self, value:'PdfPageRotateAngle'):
        GetDllLibPdf().PdfPageSettings_set_Rotate.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPdf().PdfPageSettings_set_Rotate,self.Ptr, value.value)

    @property

    def Transition(self)->'PdfPageTransition':
        """
        Gets or sets the transition.
        """
        GetDllLibPdf().PdfPageSettings_get_Transition.argtypes=[c_void_p]
        GetDllLibPdf().PdfPageSettings_get_Transition.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfPageSettings_get_Transition,self.Ptr)
        ret = None if intPtr==None else PdfPageTransition(intPtr)
        return ret


    @Transition.setter
    def Transition(self, value:'PdfPageTransition'):
        GetDllLibPdf().PdfPageSettings_set_Transition.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPdf().PdfPageSettings_set_Transition,self.Ptr, value.Ptr)

    @dispatch

    def SetMargins(self ,margins:float):
        """
        Sets the margins.

        Args:
            margins (float): The margins.
        """        
        GetDllLibPdf().PdfPageSettings_SetMargins.argtypes=[c_void_p ,c_float]
        CallCFunction(GetDllLibPdf().PdfPageSettings_SetMargins,self.Ptr, margins)

    @dispatch

    def SetMargins(self ,leftRight:float,topBottom:float):
        """
        Sets the margins.

        Args:
            leftRight (float): The left right.
			topBottom (float): The top bottom.
        """        
        GetDllLibPdf().PdfPageSettings_SetMarginsLT.argtypes=[c_void_p ,c_float,c_float]
        CallCFunction(GetDllLibPdf().PdfPageSettings_SetMarginsLT,self.Ptr, leftRight,topBottom)

    @dispatch

    def SetMargins(self ,left:float,top:float,right:float,bottom:float):
        """
        Sets the margins.

        Args:
            left (float): The left.
			top (float): The top.
            right (float): The right.
			bottom (float): The bottom.			
        """        
        GetDllLibPdf().PdfPageSettings_SetMarginsLTRB.argtypes=[c_void_p ,c_float,c_float,c_float,c_float]
        CallCFunction(GetDllLibPdf().PdfPageSettings_SetMarginsLTRB,self.Ptr, left,top,right,bottom)


    def Clone(self)->'SpireObject':
        """
        Creates a clone of the object.

        Returns:
            Cloned object.
        """ 		
        GetDllLibPdf().PdfPageSettings_Clone.argtypes=[c_void_p]
        GetDllLibPdf().PdfPageSettings_Clone.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfPageSettings_Clone,self.Ptr)
        ret = None if intPtr==None else SpireObject(intPtr)
        return ret


