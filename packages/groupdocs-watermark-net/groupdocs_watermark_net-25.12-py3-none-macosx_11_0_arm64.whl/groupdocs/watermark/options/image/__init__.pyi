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

class GifImageLoadOptions(MultiframeImageLoadOptions):
    '''Represents image loading options for a GIF image.'''
    
    def __init__(self) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.watermark.options.image.GifImageLoadOptions` class.'''
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
    def default(self) -> groupdocs.watermark.options.image.GifImageLoadOptions:
        '''Gets the default value for :py:class:`groupdocs.watermark.options.image.GifImageLoadOptions` class.'''
        raise NotImplementedError()


class GifImageSaveOptions(ImageSaveOptions):
    '''Represents image saving options when saving a GIF image.'''
    
    def __init__(self) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.watermark.options.image.GifImageSaveOptions` class.'''
        raise NotImplementedError()
    
    @property
    def default(self) -> groupdocs.watermark.options.image.GifImageSaveOptions:
        '''Gets the default value for the :py:class:`groupdocs.watermark.options.image.GifImageSaveOptions` class.'''
        raise NotImplementedError()


class GifImageWatermarkOptions(MultiframeImageWatermarkOptions):
    '''Represents watermark adding options when adding watermark to a GIF image.'''
    
    @overload
    def __init__(self) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.watermark.options.image.GifImageWatermarkOptions` class.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, frame_index : int) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.watermark.options.image.GifImageWatermarkOptions` class with a specified index of a frame.
        
        :param frame_index: The index of frame to add watermark.'''
        raise NotImplementedError()
    
    @property
    def default(self) -> groupdocs.watermark.options.WatermarkOptions:
        '''Gets the default value for the :py:class:`groupdocs.watermark.options.WatermarkOptions` class.'''
        raise NotImplementedError()

    @property
    def frame_index(self) -> int:
        '''Gets the index of frame to add watermark.'''
        raise NotImplementedError()
    
    @frame_index.setter
    def frame_index(self, value : int) -> None:
        '''Sets the index of frame to add watermark.'''
        raise NotImplementedError()
    

class ImageLoadOptions(groupdocs.watermark.options.LoadOptions):
    '''Represents image loading options when loading an image.'''
    
    def __init__(self) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.watermark.options.image.ImageLoadOptions` class.'''
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
    def default(self) -> groupdocs.watermark.options.image.ImageLoadOptions:
        '''Gets the default value for the :py:class:`groupdocs.watermark.options.image.ImageLoadOptions` class.'''
        raise NotImplementedError()


class ImageSaveOptions(groupdocs.watermark.options.SaveOptions):
    '''Represents image saving options when saving an image.'''
    
    def __init__(self) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.watermark.options.image.ImageSaveOptions` class.'''
        raise NotImplementedError()
    
    @property
    def default(self) -> groupdocs.watermark.options.image.ImageSaveOptions:
        '''Gets the default value for the :py:class:`groupdocs.watermark.options.image.ImageSaveOptions` class.'''
        raise NotImplementedError()


class MultiframeImageLoadOptions(ImageLoadOptions):
    '''Represents image loading options when loading a multiframe image.'''
    
    def __init__(self) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.watermark.options.image.MultiframeImageLoadOptions` class.'''
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
    def default(self) -> groupdocs.watermark.options.image.MultiframeImageLoadOptions:
        '''Gets the default value for the :py:class:`groupdocs.watermark.options.image.MultiframeImageLoadOptions` class.'''
        raise NotImplementedError()


class MultiframeImageWatermarkOptions(groupdocs.watermark.options.WatermarkOptions):
    '''Represents watermark adding options when adding watermark to a multi-frame image.'''
    
    @overload
    def __init__(self) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.watermark.options.image.MultiframeImageWatermarkOptions` class.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, frame_index : int) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.watermark.options.image.MultiframeImageWatermarkOptions` class
        with a specified index of the frame.
        
        :param frame_index: The index of frame to add watermark.'''
        raise NotImplementedError()
    
    @property
    def default(self) -> groupdocs.watermark.options.WatermarkOptions:
        '''Gets the default value for the :py:class:`groupdocs.watermark.options.WatermarkOptions` class.'''
        raise NotImplementedError()

    @property
    def frame_index(self) -> int:
        '''Gets the index of frame to add watermark.'''
        raise NotImplementedError()
    
    @frame_index.setter
    def frame_index(self, value : int) -> None:
        '''Sets the index of frame to add watermark.'''
        raise NotImplementedError()
    

class TiffImageLoadOptions(MultiframeImageLoadOptions):
    '''Represents image loading options for a TIFF image.'''
    
    def __init__(self) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.watermark.options.image.TiffImageLoadOptions` class.'''
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
    def default(self) -> groupdocs.watermark.options.image.TiffImageLoadOptions:
        '''Gets the default value for :py:class:`groupdocs.watermark.options.image.TiffImageLoadOptions` class.'''
        raise NotImplementedError()


class TiffImageSaveOptions(ImageSaveOptions):
    '''Represents image saving options when saving a TIFF image.'''
    
    def __init__(self) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.watermark.options.image.TiffImageSaveOptions` class.'''
        raise NotImplementedError()
    
    @property
    def default(self) -> groupdocs.watermark.options.image.TiffImageSaveOptions:
        '''Gets the default value for the :py:class:`groupdocs.watermark.options.image.TiffImageSaveOptions` class.'''
        raise NotImplementedError()


class TiffImageWatermarkOptions(MultiframeImageWatermarkOptions):
    '''Represents watermark adding options when adding watermark to a TIFF image.'''
    
    @overload
    def __init__(self) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.watermark.options.image.TiffImageWatermarkOptions` class.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, frame_index : int) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.watermark.options.image.TiffImageWatermarkOptions` class
        with a specified index of the frame.
        
        :param frame_index: The index of frame to add watermark.'''
        raise NotImplementedError()
    
    @property
    def default(self) -> groupdocs.watermark.options.WatermarkOptions:
        '''Gets the default value for the :py:class:`groupdocs.watermark.options.WatermarkOptions` class.'''
        raise NotImplementedError()

    @property
    def frame_index(self) -> int:
        '''Gets the index of frame to add watermark.'''
        raise NotImplementedError()
    
    @frame_index.setter
    def frame_index(self, value : int) -> None:
        '''Sets the index of frame to add watermark.'''
        raise NotImplementedError()
    

