from enum import Enum
from plum import dispatch
from typing import TypeVar, Union, Generic, List, Tuple
from spire.ocr.common import *
from spire.ocr import *
#from spire.ocr import OCRTTT
from ctypes import *

class OCRText(SpireObject):
    """
    Represents interface that work with ocr result text.
    """

    def ToString(self) -> str:
        """
        Gets whole ocr result plain text without formatting.
        """
        GetDllLibOcr().IOCRText_ToString.argtypes = [c_void_p]
        GetDllLibOcr().IOCRText_ToString.restype = c_void_p
        strIntPtr = CallCFunction(GetDllLibOcr().IOCRText_ToString,self.Ptr)
        ret = PtrToStr(strIntPtr)
        return ret

    @property
    def Blocks(self) -> List["OCRTextBlock"]:
        """
        Gets an array of ocr result text by blocks.
        """
        GetDllLibOcr().IOCRText_get_Blocks.argtypes = [c_void_p]
        GetDllLibOcr().IOCRText_get_Blocks.restype = IntPtrArray

        intPtrArr = CallCFunction(GetDllLibOcr().IOCRText_get_Blocks,self.Ptr)
        ret = None if intPtrArr == None else GetObjVectorFromArray(intPtrArr, OCRTextBlock)
        return ret