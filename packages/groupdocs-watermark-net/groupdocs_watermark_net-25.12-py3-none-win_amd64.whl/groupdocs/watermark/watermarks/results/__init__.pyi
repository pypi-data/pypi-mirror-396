from typing import List, Optional, Dict, Iterable, Any, overload
import io
import collections.abc
from collections.abc import Sequence
from datetime import datetime
from aspose.pyreflection import Type
import aspose.pycore
import aspose.pydrawing
from uuid import UUID
import groupdocs.watermark
import groupdocs.watermark.common
import groupdocs.watermark.contents
import groupdocs.watermark.contents.diagram
import groupdocs.watermark.contents.email
import groupdocs.watermark.contents.image
import groupdocs.watermark.contents.pdf
import groupdocs.watermark.contents.presentation
import groupdocs.watermark.contents.spreadsheet
import groupdocs.watermark.contents.wordprocessing
import groupdocs.watermark.exceptions
import groupdocs.watermark.internal
import groupdocs.watermark.options
import groupdocs.watermark.options.diagram
import groupdocs.watermark.options.email
import groupdocs.watermark.options.image
import groupdocs.watermark.options.pdf
import groupdocs.watermark.options.presentation
import groupdocs.watermark.options.spreadsheet
import groupdocs.watermark.options.wordprocessing
import groupdocs.watermark.search
import groupdocs.watermark.search.objects
import groupdocs.watermark.search.searchcriteria
import groupdocs.watermark.search.watermarks
import groupdocs.watermark.watermarks
import groupdocs.watermark.watermarks.results

class AddWatermarkResult:
    '''Represents the result of adding watermarks to a document.'''
    
    @property
    def number_applied_watermarks(self) -> int:
        '''Gets the number of applied watermarks.'''
        raise NotImplementedError()
    
    @property
    def succeeded(self) -> System.Collections.Generic.IEnumerable`1[[GroupDocs.Watermark.Watermarks.Results.BaseWatermarkResult]]:
        '''List of newly created watermarks'''
        raise NotImplementedError()
    

class BaseWatermarkResult:
    '''Describes base class for watermark result'''
    
    @property
    def watermark_type(self) -> groupdocs.watermark.watermarks.results.WatermarkType:
        '''Specifies the type of watermark.'''
        raise NotImplementedError()
    
    @property
    def watermark_position(self) -> groupdocs.watermark.watermarks.results.WatermarkPosition:
        '''Specifies watermark position'''
        raise NotImplementedError()
    
    @property
    def page_number(self) -> System.Nullable`1[[System.Int32]]:
        '''Specifies the page watermark was placed on.'''
        raise NotImplementedError()
    
    @property
    def watermark_id(self) -> str:
        '''Unique watermark identifier to modify watermark in the document over Update or Delete methods.
        This property will be set automatically after Add method being called.
        If this property was saved before it can be set manually to manipulate the watermark.'''
        raise NotImplementedError()
    
    @property
    def created_on(self) -> datetime:
        '''Get or set the watermark creation date.'''
        raise NotImplementedError()
    
    @created_on.setter
    def created_on(self, value : datetime) -> None:
        '''Get or set the watermark creation date.'''
        raise NotImplementedError()
    
    @property
    def modified_on(self) -> datetime:
        '''Get or set the watermark modification date.'''
        raise NotImplementedError()
    
    @modified_on.setter
    def modified_on(self, value : datetime) -> None:
        '''Get or set the watermark modification date.'''
        raise NotImplementedError()
    
    @property
    def top(self) -> int:
        '''Specifies top position of watermark.'''
        raise NotImplementedError()
    
    @top.setter
    def top(self, value : int) -> None:
        '''Specifies top position of watermark.'''
        raise NotImplementedError()
    
    @property
    def left(self) -> int:
        '''Specifies left position of watermark.'''
        raise NotImplementedError()
    
    @left.setter
    def left(self, value : int) -> None:
        '''Specifies left position of watermark.'''
        raise NotImplementedError()
    
    @property
    def width(self) -> int:
        '''Specifies width of watermark.'''
        raise NotImplementedError()
    
    @width.setter
    def width(self, value : int) -> None:
        '''Specifies width of watermark.'''
        raise NotImplementedError()
    
    @property
    def height(self) -> int:
        '''Specifies height of watermark.'''
        raise NotImplementedError()
    
    @height.setter
    def height(self, value : int) -> None:
        '''Specifies height of watermark.'''
        raise NotImplementedError()
    

class ImageWatermarkResult(BaseWatermarkResult):
    '''Contains Image watermark properties.'''
    
    def __init__(self, watermark_id : str) -> None:
        '''Initialize ImageWatermarkResult object with watermark identifier that was obtained after search process.
        This unique identifier is used to find additional properties for this watermark from document watermark information layer.
        
        :param watermark_id: Unique watermark identifier obtained by Sign or Search method of Signature class :py:class:`GroupDocs.Signature.Signature`.'''
        raise NotImplementedError()
    
    @property
    def watermark_type(self) -> groupdocs.watermark.watermarks.results.WatermarkType:
        '''Specifies the type of watermark.'''
        raise NotImplementedError()
    
    @property
    def watermark_position(self) -> groupdocs.watermark.watermarks.results.WatermarkPosition:
        '''Specifies watermark position'''
        raise NotImplementedError()
    
    @property
    def page_number(self) -> System.Nullable`1[[System.Int32]]:
        '''Specifies the page watermark was placed on.'''
        raise NotImplementedError()
    
    @property
    def watermark_id(self) -> str:
        '''Unique watermark identifier to modify watermark in the document over Update or Delete methods.
        This property will be set automatically after Add method being called.
        If this property was saved before it can be set manually to manipulate the watermark.'''
        raise NotImplementedError()
    
    @property
    def created_on(self) -> datetime:
        '''Get or set the watermark creation date.'''
        raise NotImplementedError()
    
    @created_on.setter
    def created_on(self, value : datetime) -> None:
        '''Get or set the watermark creation date.'''
        raise NotImplementedError()
    
    @property
    def modified_on(self) -> datetime:
        '''Get or set the watermark modification date.'''
        raise NotImplementedError()
    
    @modified_on.setter
    def modified_on(self, value : datetime) -> None:
        '''Get or set the watermark modification date.'''
        raise NotImplementedError()
    
    @property
    def top(self) -> int:
        '''Specifies top position of watermark.'''
        raise NotImplementedError()
    
    @top.setter
    def top(self, value : int) -> None:
        '''Specifies top position of watermark.'''
        raise NotImplementedError()
    
    @property
    def left(self) -> int:
        '''Specifies left position of watermark.'''
        raise NotImplementedError()
    
    @left.setter
    def left(self, value : int) -> None:
        '''Specifies left position of watermark.'''
        raise NotImplementedError()
    
    @property
    def width(self) -> int:
        '''Specifies width of watermark.'''
        raise NotImplementedError()
    
    @width.setter
    def width(self, value : int) -> None:
        '''Specifies width of watermark.'''
        raise NotImplementedError()
    
    @property
    def height(self) -> int:
        '''Specifies height of watermark.'''
        raise NotImplementedError()
    
    @height.setter
    def height(self, value : int) -> None:
        '''Specifies height of watermark.'''
        raise NotImplementedError()
    
    @property
    def size(self) -> int:
        '''Specifies the size in bytes of watermark image.'''
        raise NotImplementedError()
    

class TextWatermarkResult(BaseWatermarkResult):
    '''Contains Text watermark properties.'''
    
    def __init__(self, watermark_id : str) -> None:
        '''Initialize TextWatermarkResult object with watermark identifier that was obtained after search process.
        This unique identifier is used to find additional properties for this watermark from document watermark information layer.
        
        :param watermark_id: Unique watermark identifier obtained by sign or search method.'''
        raise NotImplementedError()
    
    @property
    def watermark_type(self) -> groupdocs.watermark.watermarks.results.WatermarkType:
        '''Specifies the type of watermark.'''
        raise NotImplementedError()
    
    @property
    def watermark_position(self) -> groupdocs.watermark.watermarks.results.WatermarkPosition:
        '''Specifies watermark position'''
        raise NotImplementedError()
    
    @property
    def page_number(self) -> System.Nullable`1[[System.Int32]]:
        '''Specifies the page watermark was placed on.'''
        raise NotImplementedError()
    
    @property
    def watermark_id(self) -> str:
        '''Unique watermark identifier to modify watermark in the document over Update or Delete methods.
        This property will be set automatically after Add method being called.
        If this property was saved before it can be set manually to manipulate the watermark.'''
        raise NotImplementedError()
    
    @property
    def created_on(self) -> datetime:
        '''Get or set the watermark creation date.'''
        raise NotImplementedError()
    
    @created_on.setter
    def created_on(self, value : datetime) -> None:
        '''Get or set the watermark creation date.'''
        raise NotImplementedError()
    
    @property
    def modified_on(self) -> datetime:
        '''Get or set the watermark modification date.'''
        raise NotImplementedError()
    
    @modified_on.setter
    def modified_on(self, value : datetime) -> None:
        '''Get or set the watermark modification date.'''
        raise NotImplementedError()
    
    @property
    def top(self) -> int:
        '''Specifies top position of watermark.'''
        raise NotImplementedError()
    
    @top.setter
    def top(self, value : int) -> None:
        '''Specifies top position of watermark.'''
        raise NotImplementedError()
    
    @property
    def left(self) -> int:
        '''Specifies left position of watermark.'''
        raise NotImplementedError()
    
    @left.setter
    def left(self, value : int) -> None:
        '''Specifies left position of watermark.'''
        raise NotImplementedError()
    
    @property
    def width(self) -> int:
        '''Specifies width of watermark.'''
        raise NotImplementedError()
    
    @width.setter
    def width(self, value : int) -> None:
        '''Specifies width of watermark.'''
        raise NotImplementedError()
    
    @property
    def height(self) -> int:
        '''Specifies height of watermark.'''
        raise NotImplementedError()
    
    @height.setter
    def height(self, value : int) -> None:
        '''Specifies height of watermark.'''
        raise NotImplementedError()
    
    @property
    def text(self) -> str:
        '''Specifies text in watermark.'''
        raise NotImplementedError()
    
    @text.setter
    def text(self, value : str) -> None:
        '''Specifies text in watermark.'''
        raise NotImplementedError()
    

class WatermarkPosition:
    '''Defines watermark position in the document layout'''
    
    DEFAULT : WatermarkPosition
    '''The Watermark is placed in the document body'''
    HEADER_FOOTER : WatermarkPosition
    '''The Watermark is placed in the document header or footer'''
    BACKGROUND : WatermarkPosition
    '''The watermark is placed as the background of the document'''

class WatermarkType:
    '''Defines supported types of watermarks for various processes'''
    
    TEXT : WatermarkType
    '''The Text type'''
    IMAGE : WatermarkType
    '''The Image type'''

