from typing import List, Optional, Dict, Iterable, Any, overload
import io
import collections.abc
from collections.abc import Sequence
from datetime import datetime
from aspose.pyreflection import Type
import aspose.pycore
import aspose.pydrawing
from uuid import UUID
import aspose.diagram
import aspose.diagram.activexcontrols
import aspose.diagram.autolayout
import aspose.diagram.lowcode
import aspose.diagram.manipulation
import aspose.diagram.printing
import aspose.diagram.properties
import aspose.diagram.saving
import aspose.diagram.vba

class DiagramConverter:
    
    @overload
    @staticmethod
    def process(template_file : str, result_file : str) -> None:
        raise NotImplementedError()
    
    @overload
    @staticmethod
    def process(load_options : aspose.diagram.lowcode.LowCodeLoadOptions, save_options : aspose.diagram.lowcode.LowCodeSaveOptions) -> None:
        raise NotImplementedError()
    

class LowCodeLoadOptions:
    
    def __init__(self) -> None:
        raise NotImplementedError()
    
    @property
    def input_file(self) -> str:
        raise NotImplementedError()
    
    @input_file.setter
    def input_file(self, value : str) -> None:
        raise NotImplementedError()
    
    @property
    def input_stream(self) -> io._IOBase:
        raise NotImplementedError()
    
    @input_stream.setter
    def input_stream(self, value : io._IOBase) -> None:
        raise NotImplementedError()
    

class LowCodePdfSaveOptions(LowCodeSaveOptions):
    
    def __init__(self) -> None:
        raise NotImplementedError()
    
    @property
    def output_file(self) -> str:
        raise NotImplementedError()
    
    @output_file.setter
    def output_file(self, value : str) -> None:
        raise NotImplementedError()
    
    @property
    def output_stream(self) -> io._IOBase:
        raise NotImplementedError()
    
    @output_stream.setter
    def output_stream(self, value : io._IOBase) -> None:
        raise NotImplementedError()
    
    @property
    def save_format(self) -> aspose.diagram.SaveFileFormat:
        raise NotImplementedError()
    
    @save_format.setter
    def save_format(self, value : aspose.diagram.SaveFileFormat) -> None:
        raise NotImplementedError()
    
    @property
    def pdf_options(self) -> aspose.diagram.saving.PdfSaveOptions:
        raise NotImplementedError()
    
    @pdf_options.setter
    def pdf_options(self, value : aspose.diagram.saving.PdfSaveOptions) -> None:
        raise NotImplementedError()
    

class LowCodeSaveOptions:
    
    def __init__(self) -> None:
        raise NotImplementedError()
    
    @property
    def output_file(self) -> str:
        raise NotImplementedError()
    
    @output_file.setter
    def output_file(self, value : str) -> None:
        raise NotImplementedError()
    
    @property
    def output_stream(self) -> io._IOBase:
        raise NotImplementedError()
    
    @output_stream.setter
    def output_stream(self, value : io._IOBase) -> None:
        raise NotImplementedError()
    
    @property
    def save_format(self) -> aspose.diagram.SaveFileFormat:
        raise NotImplementedError()
    
    @save_format.setter
    def save_format(self, value : aspose.diagram.SaveFileFormat) -> None:
        raise NotImplementedError()
    

class PdfConverter:
    
    @overload
    @staticmethod
    def process(template_file : str, result_file : str) -> None:
        raise NotImplementedError()
    
    @overload
    @staticmethod
    def process(load_options : aspose.diagram.lowcode.LowCodeLoadOptions, save_options : aspose.diagram.lowcode.LowCodeSaveOptions) -> None:
        raise NotImplementedError()
    

