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

class EmailLoadOptions(groupdocs.watermark.options.LoadOptions):
    '''Represents the document loading options for an email message.'''
    
    def __init__(self) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.watermark.options.email.EmailLoadOptions` class.'''
        raise NotImplementedError()
    
    @property
    def password(self) -> str:
        '''Gets the password for opening an encrypted document.'''
        raise NotImplementedError()
    
    @password.setter
    def password(self, value : str) -> None:
        '''Sets the password for opening an encrypted document.'''
        raise NotImplementedError()
    
    @property
    def format_family(self) -> System.Nullable`1[[GroupDocs.Watermark.Common.FormatFamily]]:
        '''Gets the format family of the document,
        indicating its type (e.g., Image, Pdf, Spreadsheet, etc.).'''
        raise NotImplementedError()
    
    @format_family.setter
    def format_family(self, value : System.Nullable`1[[GroupDocs.Watermark.Common.FormatFamily]]) -> None:
        '''Sets the format family of the document,
        indicating its type (e.g., Image, Pdf, Spreadsheet, etc.).'''
        raise NotImplementedError()
    
    @property
    def file_type(self) -> groupdocs.watermark.common.FileType:
        '''Gets the type of the file,
        indicating its type (e.g., docx, pdf, xlsx, etc.).'''
        raise NotImplementedError()
    
    @file_type.setter
    def file_type(self, value : groupdocs.watermark.common.FileType) -> None:
        '''Sets the type of the file,
        indicating its type (e.g., docx, pdf, xlsx, etc.).'''
        raise NotImplementedError()
    
    @property
    def default(self) -> groupdocs.watermark.options.email.EmailLoadOptions:
        '''Gets the default value for :py:class:`groupdocs.watermark.options.email.EmailLoadOptions` class.'''
        raise NotImplementedError()


class EmailPreviewOptions(groupdocs.watermark.options.PreviewOptions):
    '''Provides options to sets requirements and stream delegates for preview generation of Email document.'''
    
    @property
    def width(self) -> int:
        '''Gets the page preview width.'''
        raise NotImplementedError()
    
    @width.setter
    def width(self, value : int) -> None:
        '''Sets the page preview width.'''
        raise NotImplementedError()
    
    @property
    def height(self) -> int:
        '''Gets the page preview height.'''
        raise NotImplementedError()
    
    @height.setter
    def height(self, value : int) -> None:
        '''Sets the page preview height.'''
        raise NotImplementedError()
    
    @property
    def page_numbers(self) -> List[int]:
        '''Gets an array of page numbers to generate previews.'''
        raise NotImplementedError()
    
    @page_numbers.setter
    def page_numbers(self, value : List[int]) -> None:
        '''Sets an array of page numbers to generate previews.'''
        raise NotImplementedError()
    
    @property
    def preview_format(self) -> GroupDocs.Watermark.Options.PreviewOptions+PreviewFormats:
        '''Gets the preview image format.'''
        raise NotImplementedError()
    
    @preview_format.setter
    def preview_format(self, value : GroupDocs.Watermark.Options.PreviewOptions+PreviewFormats) -> None:
        '''Sets the preview image format.'''
        raise NotImplementedError()
    
    @property
    def resolution(self) -> float:
        '''Gets the resolution for the generated images, in dots per inch.'''
        raise NotImplementedError()
    
    @resolution.setter
    def resolution(self, value : float) -> None:
        '''Sets the resolution for the generated images, in dots per inch.'''
        raise NotImplementedError()
    
    @property
    def DEFAULT_RESOLUTION(self) -> float:
        '''Default resolution in dots per inch.'''
        raise NotImplementedError()


class EmailSaveOptions(groupdocs.watermark.options.SaveOptions):
    '''Represents the document saving options when saving an email message.'''
    
    def __init__(self) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.watermark.options.email.EmailSaveOptions` class.'''
        raise NotImplementedError()
    
    @property
    def default(self) -> groupdocs.watermark.options.email.EmailSaveOptions:
        '''Gets the default value for the :py:class:`groupdocs.watermark.options.email.EmailSaveOptions` class.'''
        raise NotImplementedError()


