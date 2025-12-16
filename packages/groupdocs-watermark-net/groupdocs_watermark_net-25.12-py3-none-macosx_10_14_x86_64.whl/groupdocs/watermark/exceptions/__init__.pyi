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

class DetachedImageException(WatermarkException):
    '''The exception that is thrown when manipulating detached image.'''
    
    def __init__(self) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.watermark.exceptions.DetachedImageException` class.'''
        raise NotImplementedError()
    

class EncryptionIsNotSupportedException(WatermarkException):
    '''The exception that is thrown when content encryption is not supported.'''
    
    def __init__(self) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.watermark.exceptions.EncryptionIsNotSupportedException` class.'''
        raise NotImplementedError()
    

class FontNotFoundException(WatermarkException):
    '''The exception that is thrown when requested font is not found.'''
    
    @overload
    def __init__(self) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.watermark.exceptions.FontNotFoundException` class.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, font_name : str) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.watermark.exceptions.FontNotFoundException` class with a specified font name.
        
        :param font_name: The requested font name.'''
        raise NotImplementedError()
    
    @property
    def font_name(self) -> str:
        '''Gets the requested font name.'''
        raise NotImplementedError()
    

class ImageEffectsForTextWatermarkException(WatermarkException):
    '''The exception that is thrown when :py:class:`groupdocs.watermark.contents.OfficeImageEffects` is supplied for :py:class:`groupdocs.watermark.watermarks.TextWatermark`.'''
    
    def __init__(self) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.watermark.exceptions.ImageEffectsForTextWatermarkException` class.'''
        raise NotImplementedError()
    

class InvalidPasswordException(WatermarkException):
    '''The exception that is thrown when supplied password is incorrect.'''
    
    def __init__(self) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.watermark.exceptions.InvalidPasswordException` class.'''
        raise NotImplementedError()
    

class PreviewNotSupportedException(WatermarkException):
    '''The exception that is thrown when a preview image cannot be generated for the content.'''
    
    def __init__(self) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.watermark.exceptions.PreviewNotSupportedException` class.'''
        raise NotImplementedError()
    

class TextEffectsForImageWatermarkException(WatermarkException):
    '''The exception that is thrown when :py:class:`groupdocs.watermark.contents.OfficeTextEffects` is supplied for :py:class:`groupdocs.watermark.watermarks.ImageWatermark`.'''
    
    def __init__(self) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.watermark.exceptions.TextEffectsForImageWatermarkException` class.'''
        raise NotImplementedError()
    

class UnexpectedDocumentStructureException(WatermarkException):
    '''The exception that is thrown when a content cannot be parsed due to unexpected structure.'''
    
    def __init__(self) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.watermark.exceptions.UnexpectedDocumentStructureException` class.'''
        raise NotImplementedError()
    

class UnknownLoadOptionsTypeException(WatermarkException):
    '''The exception that is thrown when a document cannot be loaded with supplied :py:class:`groupdocs.watermark.options.LoadOptions`.'''
    
    def __init__(self) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.watermark.exceptions.UnknownLoadOptionsTypeException` class.'''
        raise NotImplementedError()
    

class UnknownWatermarkOptionsTypeException(WatermarkException):
    '''The exception that is thrown when a watermark cannot be added with supplied :py:class:`groupdocs.watermark.options.WatermarkOptions`.'''
    
    def __init__(self) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.watermark.exceptions.UnknownWatermarkOptionsTypeException` class.'''
        raise NotImplementedError()
    

class UnsupportedFileTypeException(WatermarkException):
    '''The exception that is thrown when a file cannot be loaded.'''
    
    def __init__(self) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.watermark.exceptions.UnsupportedFileTypeException` class.'''
        raise NotImplementedError()
    

class WatermarkException:
    '''Represents base exception in **GroupDocs.Watermark** product.'''
    
    @overload
    def __init__(self) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.watermark.exceptions.WatermarkException` class.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, message : str) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.watermark.exceptions.WatermarkException` class with a specified error message.
        
        :param message: The message that describes the error.'''
        raise NotImplementedError()
    

