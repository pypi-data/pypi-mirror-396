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

class PdfAnnotationWatermarkOptions(PdfWatermarkOptions):
    '''Represents watermark adding options when adding annotation watermark to a pdf document.'''
    
    def __init__(self) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.watermark.options.pdf.PdfAnnotationWatermarkOptions` class.'''
        raise NotImplementedError()
    
    @property
    def default(self) -> groupdocs.watermark.options.WatermarkOptions:
        '''Gets the default value for the :py:class:`groupdocs.watermark.options.WatermarkOptions` class.'''
        raise NotImplementedError()

    @property
    def page_index(self) -> int:
        '''Gets the page index to add watermark to.'''
        raise NotImplementedError()
    
    @page_index.setter
    def page_index(self, value : int) -> None:
        '''Sets the page index to add watermark to.'''
        raise NotImplementedError()
    
    @property
    def print_only(self) -> bool:
        '''Get the value indicating whether annotation will be printed, but not displayed
        in pdf viewing application.'''
        raise NotImplementedError()
    
    @print_only.setter
    def print_only(self, value : bool) -> None:
        '''Get or sets the value indicating whether annotation will be printed, but not displayed
        in pdf viewing application.'''
        raise NotImplementedError()
    

class PdfArtifactWatermarkOptions(PdfWatermarkOptions):
    '''Represents watermark adding options when adding artifact watermark to a pdf document.'''
    
    def __init__(self) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.watermark.options.pdf.PdfArtifactWatermarkOptions` class.'''
        raise NotImplementedError()
    
    @property
    def default(self) -> groupdocs.watermark.options.WatermarkOptions:
        '''Gets the default value for the :py:class:`groupdocs.watermark.options.WatermarkOptions` class.'''
        raise NotImplementedError()

    @property
    def page_index(self) -> int:
        '''Gets the page index to add watermark to.'''
        raise NotImplementedError()
    
    @page_index.setter
    def page_index(self, value : int) -> None:
        '''Sets the page index to add watermark to.'''
        raise NotImplementedError()
    

class PdfLoadOptions(groupdocs.watermark.options.LoadOptions):
    '''Represents document loading options for a pdf document.'''
    
    @overload
    def __init__(self) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.watermark.options.pdf.PdfLoadOptions` class.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, password : str) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.watermark.options.pdf.PdfLoadOptions` class with a specified password.
        
        :param password: The password for opening an encrypted document.'''
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
    def default(self) -> groupdocs.watermark.options.pdf.PdfLoadOptions:
        '''Gets the default value for the :py:class:`groupdocs.watermark.options.pdf.PdfLoadOptions` class.'''
        raise NotImplementedError()


class PdfPreviewOptions(groupdocs.watermark.options.PreviewOptions):
    '''Provides options to sets requirements and stream delegates for preview generation of PDF document.'''
    
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
    def resolution(self) -> int:
        '''Gets the resolution for the generated images, in dots per inch.'''
        raise NotImplementedError()
    
    @resolution.setter
    def resolution(self, value : int) -> None:
        '''Sets the resolution for the generated images, in dots per inch.'''
        raise NotImplementedError()
    
    @property
    def DEFAULT_RESOLUTION(self) -> int:
        '''Default resolution in dots per inch.'''
        raise NotImplementedError()


class PdfSaveOptions(groupdocs.watermark.options.SaveOptions):
    '''Represents document saving options when saving a pdf document.'''
    
    def __init__(self) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.watermark.options.pdf.PdfSaveOptions` class.'''
        raise NotImplementedError()
    
    @property
    def default(self) -> groupdocs.watermark.options.pdf.PdfSaveOptions:
        '''Gets the default value for the :py:class:`groupdocs.watermark.options.pdf.PdfSaveOptions` class.'''
        raise NotImplementedError()


class PdfWatermarkOptions(groupdocs.watermark.options.WatermarkOptions):
    '''Base class for watermark adding options to a pdf document.'''
    
    @property
    def default(self) -> groupdocs.watermark.options.WatermarkOptions:
        '''Gets the default value for the :py:class:`groupdocs.watermark.options.WatermarkOptions` class.'''
        raise NotImplementedError()


class PdfXObjectWatermarkOptions(PdfWatermarkOptions):
    '''Represents watermark adding options when adding XObject watermark to a pdf document.'''
    
    def __init__(self) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.watermark.options.pdf.PdfXObjectWatermarkOptions` class.'''
        raise NotImplementedError()
    
    @property
    def default(self) -> groupdocs.watermark.options.WatermarkOptions:
        '''Gets the default value for the :py:class:`groupdocs.watermark.options.WatermarkOptions` class.'''
        raise NotImplementedError()

    @property
    def page_index(self) -> int:
        '''Gets the page index to add watermark to.'''
        raise NotImplementedError()
    
    @page_index.setter
    def page_index(self, value : int) -> None:
        '''Sets the page index to add watermark to.'''
        raise NotImplementedError()
    

