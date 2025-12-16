from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.ocr.common import *
from spire.ocr import *
from ctypes import *
import abc

class OcrScanner (SpireObject) :
    """
        OcrScanner provides logic for image ocr processing, choosing language and recognition process.
        Chinese and English are supported by default, and no language package needs to be loaded 
    """

    def __init__(self):
        GetDllLibOcr().OcrScanner_Create.restype = c_void_p
        intPtr = CallCFunction(GetDllLibOcr().OcrScanner_Create)
        super(OcrScanner, self).__init__(intPtr)

    def __del__(self):
        GetDllLibOcr().OcrScanner_Dispose.argtypes = [c_void_p]
        CallCFunction(GetDllLibOcr().OcrScanner_Dispose,self.Ptr)
        super(OcrScanner, self).__del__()

    @property
    def Text(self) -> 'OCRText':
        """
        Gets Ocr result text.
        """
        GetDllLibOcr().OcrScanner_get_Text.argtypes = [c_void_p]
        GetDllLibOcr().OcrScanner_get_Text.restype = c_void_p
        intPtr = CallCFunction(GetDllLibOcr().OcrScanner_get_Text,self.Ptr)
        ret = None if intPtr==None else OCRText(intPtr) 
        return ret


    @dispatch
    def Scan(self,fileName:str) -> bool:
        """
        Runs the ocr process.

        Returns:
            bool: Indicating whether text has been recognized succesfully.
        """		
        GetDllLibOcr().OcrScanner_ScanF.argtypes=[c_void_p ,c_wchar_p]
        GetDllLibOcr().OcrScanner_ScanF.restype=c_bool
        ret = CallCFunction(GetDllLibOcr().OcrScanner_ScanF,self.Ptr,fileName)
        return ret

    @dispatch
    def Scan(self,stream:Stream,imageFormat:OCRImageFormat) -> bool:
        """
        Runs the ocr process.

        Returns:
            bool: Indicating whether text has been recognized succesfully. 
        """	
        intPtrstream:c_void_p = stream.Ptr
        enumfileformat:c_int = imageFormat.value

        GetDllLibOcr().OcrScanner_ScanSI.argtypes=[c_void_p ,c_void_p,c_int]
        GetDllLibOcr().OcrScanner_ScanSI.restype=c_bool
        ret = CallCFunction(GetDllLibOcr().OcrScanner_ScanSI,self.Ptr,intPtrstream,enumfileformat)
        return ret

    def ConfigureDependencies(self, configureOptions:ConfigureOptions):
        """
        Configure the ocr dependencies.

        Param:
            ConfigureOptions : The configure Options of ocr dependencies.
        """	
        intPtrConfig:c_void_p = configureOptions.Ptr
        GetDllLibOcr().OcrScanner_ConfigureDependencies.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibOcr().OcrScanner_ConfigureDependencies,self.Ptr,intPtrConfig)