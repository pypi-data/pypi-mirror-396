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

class DiagramLoadOptions(groupdocs.watermark.options.LoadOptions):
    '''Represents document loading options for a Visio document.'''
    
    @overload
    def __init__(self) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.watermark.options.diagram.DiagramLoadOptions` class.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, password : str) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.watermark.options.diagram.DiagramLoadOptions` class with a specified password.
        
        :param password: The password for opening an encrypted Visio document.'''
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
    def default(self) -> groupdocs.watermark.options.diagram.DiagramLoadOptions:
        '''Gets the default value for the :py:class:`groupdocs.watermark.options.diagram.DiagramLoadOptions` class.'''
        raise NotImplementedError()


class DiagramPageWatermarkOptions(DiagramWatermarkOptions):
    '''Represents watermark adding options when adding shape watermark to a particular page of a Visio document.'''
    
    def __init__(self) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.watermark.options.diagram.DiagramPageWatermarkOptions` class.'''
        raise NotImplementedError()
    
    @property
    def default(self) -> groupdocs.watermark.options.WatermarkOptions:
        '''Gets the default value for the :py:class:`groupdocs.watermark.options.WatermarkOptions` class.'''
        raise NotImplementedError()

    @property
    def is_locked(self) -> bool:
        '''Gets a value indicating whether an editing of the shape in Visio is forbidden.'''
        raise NotImplementedError()
    
    @is_locked.setter
    def is_locked(self, value : bool) -> None:
        '''Sets a value indicating whether an editing of the shape in Visio is forbidden.'''
        raise NotImplementedError()
    
    @property
    def page_index(self) -> int:
        '''Gets the page index to add watermark to.'''
        raise NotImplementedError()
    
    @page_index.setter
    def page_index(self, value : int) -> None:
        '''Sets the page index to add watermark to.'''
        raise NotImplementedError()
    

class DiagramPreviewOptions(groupdocs.watermark.options.PreviewOptions):
    '''Provides options to sets requirements and stream delegates for preview generation of Diagram document.'''
    
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
    def high_quality_rendering(self) -> bool:
        '''Gets the flag for high quality rendering.'''
        raise NotImplementedError()
    
    @high_quality_rendering.setter
    def high_quality_rendering(self, value : bool) -> None:
        '''Sets the flag for high quality rendering.'''
        raise NotImplementedError()
    
    @property
    def DEFAULT_RESOLUTION(self) -> float:
        '''Default resolution in dots per inch.'''
        raise NotImplementedError()


class DiagramSaveOptions(groupdocs.watermark.options.SaveOptions):
    '''Represents document saving options when saving a Visio document.'''
    
    def __init__(self) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.watermark.options.diagram.DiagramSaveOptions` class.'''
        raise NotImplementedError()
    
    @property
    def default(self) -> groupdocs.watermark.options.diagram.DiagramSaveOptions:
        '''Gets the default value for the :py:class:`groupdocs.watermark.options.diagram.DiagramSaveOptions` class.'''
        raise NotImplementedError()


class DiagramShapeWatermarkOptions(DiagramWatermarkOptions):
    '''Represents watermark adding options when adding shape watermark to a Visio document.'''
    
    def __init__(self) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.watermark.options.diagram.DiagramShapeWatermarkOptions` class.'''
        raise NotImplementedError()
    
    @property
    def default(self) -> groupdocs.watermark.options.WatermarkOptions:
        '''Gets the default value for the :py:class:`groupdocs.watermark.options.WatermarkOptions` class.'''
        raise NotImplementedError()

    @property
    def is_locked(self) -> bool:
        '''Gets a value indicating whether an editing of the shape in Visio is forbidden.'''
        raise NotImplementedError()
    
    @is_locked.setter
    def is_locked(self, value : bool) -> None:
        '''Sets a value indicating whether an editing of the shape in Visio is forbidden.'''
        raise NotImplementedError()
    
    @property
    def placement_type(self) -> groupdocs.watermark.contents.diagram.DiagramWatermarkPlacementType:
        '''Gets a value specifying to what pages a watermark should be added.'''
        raise NotImplementedError()
    
    @placement_type.setter
    def placement_type(self, value : groupdocs.watermark.contents.diagram.DiagramWatermarkPlacementType) -> None:
        '''Sets a value specifying to what pages a watermark should be added.'''
        raise NotImplementedError()
    

class DiagramWatermarkOptions(groupdocs.watermark.options.WatermarkOptions):
    '''Base class for watermark adding options to a Visio document.'''
    
    @property
    def default(self) -> groupdocs.watermark.options.WatermarkOptions:
        '''Gets the default value for the :py:class:`groupdocs.watermark.options.WatermarkOptions` class.'''
        raise NotImplementedError()

    @property
    def is_locked(self) -> bool:
        '''Gets a value indicating whether an editing of the shape in Visio is forbidden.'''
        raise NotImplementedError()
    
    @is_locked.setter
    def is_locked(self, value : bool) -> None:
        '''Sets a value indicating whether an editing of the shape in Visio is forbidden.'''
        raise NotImplementedError()
    

