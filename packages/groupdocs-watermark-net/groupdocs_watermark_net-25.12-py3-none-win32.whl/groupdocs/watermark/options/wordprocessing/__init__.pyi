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

class IWordProcessingWatermarkEffects:
    '''Represents interface for watermark effects that should be applied to the watermark.'''
    

class WordProcessingImageEffects(groupdocs.watermark.contents.OfficeImageEffects):
    '''Represents effects that can be applied to an image watermark for a Word document.'''
    
    def __init__(self) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.watermark.options.wordprocessing.WordProcessingImageEffects` class.'''
        raise NotImplementedError()
    
    @property
    def border_line_format(self) -> groupdocs.watermark.contents.OfficeLineFormat:
        '''Gets a line format settings for the image border.'''
        raise NotImplementedError()
    
    @border_line_format.setter
    def border_line_format(self, value : groupdocs.watermark.contents.OfficeLineFormat) -> None:
        '''Sets a line format settings for the image border.'''
        raise NotImplementedError()
    
    @property
    def gray_scale(self) -> bool:
        '''Gets a value indicating whether a picture will be displayed in grayscale mode.'''
        raise NotImplementedError()
    
    @gray_scale.setter
    def gray_scale(self, value : bool) -> None:
        '''Sets a value indicating whether a picture will be displayed in grayscale mode.'''
        raise NotImplementedError()
    
    @property
    def chroma_key(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets the color value of the image that will be treated as transparent.'''
        raise NotImplementedError()
    
    @chroma_key.setter
    def chroma_key(self, value : groupdocs.watermark.watermarks.Color) -> None:
        '''Sets the color value of the image that will be treated as transparent.'''
        raise NotImplementedError()
    
    @property
    def brightness(self) -> float:
        '''Gets the brightness of the picture. The value for this property must
        be a number from 0.0 (dimmest) to 1.0 (brightest).'''
        raise NotImplementedError()
    
    @brightness.setter
    def brightness(self, value : float) -> None:
        '''Sets the brightness of the picture. The value for this property must
        be a number from 0.0 (dimmest) to 1.0 (brightest).'''
        raise NotImplementedError()
    
    @property
    def contrast(self) -> float:
        '''Gets the contrast for the specified picture. The value for this property
        must be a number from 0.0 (the least contrast) to 1.0 (the greatest contrast).'''
        raise NotImplementedError()
    
    @contrast.setter
    def contrast(self, value : float) -> None:
        '''Sets the contrast for the specified picture. The value for this property
        must be a number from 0.0 (the least contrast) to 1.0 (the greatest contrast).'''
        raise NotImplementedError()
    

class WordProcessingLoadOptions(groupdocs.watermark.options.LoadOptions):
    '''Represents document loading options for a Word document.'''
    
    @overload
    def __init__(self) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.watermark.options.wordprocessing.WordProcessingLoadOptions` class.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, password : str) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.watermark.options.wordprocessing.WordProcessingLoadOptions` class with a specified password.
        
        :param password: The password for opening an encrypted content.'''
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
    def default(self) -> groupdocs.watermark.options.wordprocessing.WordProcessingLoadOptions:
        '''Gets the default value for the :py:class:`groupdocs.watermark.options.wordprocessing.WordProcessingLoadOptions` class.'''
        raise NotImplementedError()


class WordProcessingPreviewOptions(groupdocs.watermark.options.PreviewOptions):
    '''Provides options to sets requirements and stream delegates for preview generation of WordProcessing document.'''
    
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


class WordProcessingSaveOptions(groupdocs.watermark.options.SaveOptions):
    '''Represents document saving options when saving a Word document.'''
    
    def __init__(self) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.watermark.options.wordprocessing.WordProcessingSaveOptions` class.'''
        raise NotImplementedError()
    
    @property
    def default(self) -> groupdocs.watermark.options.wordprocessing.WordProcessingSaveOptions:
        '''Gets the default value for the :py:class:`groupdocs.watermark.options.wordprocessing.WordProcessingSaveOptions` class.'''
        raise NotImplementedError()


class WordProcessingTextEffects(groupdocs.watermark.contents.OfficeTextEffects):
    '''Represents effects that can be applied to a text watermark for a Word document.'''
    
    def __init__(self) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.watermark.options.wordprocessing.WordProcessingTextEffects` class.'''
        raise NotImplementedError()
    
    @property
    def line_format(self) -> groupdocs.watermark.contents.OfficeLineFormat:
        '''Gets the line format settings.'''
        raise NotImplementedError()
    
    @line_format.setter
    def line_format(self, value : groupdocs.watermark.contents.OfficeLineFormat) -> None:
        '''Sets the line format settings.'''
        raise NotImplementedError()
    
    @property
    def flip_orientation(self) -> groupdocs.watermark.options.wordprocessing.WordProcessingFlipOrientation:
        '''Gets the orientation of a shape.'''
        raise NotImplementedError()
    
    @flip_orientation.setter
    def flip_orientation(self, value : groupdocs.watermark.options.wordprocessing.WordProcessingFlipOrientation) -> None:
        '''Sets the orientation of a shape.'''
        raise NotImplementedError()
    
    @property
    def DEFAULT(self) -> groupdocs.watermark.options.wordprocessing.WordProcessingTextEffects:
        '''Gets the default value for the :py:class:`groupdocs.watermark.options.wordprocessing.WordProcessingTextEffects` class.'''
        raise NotImplementedError()


class WordProcessingWatermarkBaseOptions(groupdocs.watermark.options.WatermarkOptions):
    '''Base class for watermark adding options to a Word document.'''
    
    @property
    def default(self) -> groupdocs.watermark.options.WatermarkOptions:
        '''Gets the default value for the :py:class:`groupdocs.watermark.options.WatermarkOptions` class.'''
        raise NotImplementedError()

    @property
    def is_locked(self) -> bool:
        '''Gets a value indicating whether an editing of the shape in Word is forbidden.'''
        raise NotImplementedError()
    
    @is_locked.setter
    def is_locked(self, value : bool) -> None:
        '''Sets a value indicating whether an editing of the shape in Word is forbidden.'''
        raise NotImplementedError()
    
    @property
    def lock_type(self) -> groupdocs.watermark.options.wordprocessing.WordProcessingLockType:
        '''Gets the watermark lock type.'''
        raise NotImplementedError()
    
    @lock_type.setter
    def lock_type(self, value : groupdocs.watermark.options.wordprocessing.WordProcessingLockType) -> None:
        '''Sets the watermark lock type.'''
        raise NotImplementedError()
    
    @property
    def password(self) -> str:
        '''Gets a password used to lock the watermark.'''
        raise NotImplementedError()
    
    @password.setter
    def password(self, value : str) -> None:
        '''Sets a password used to lock the watermark.'''
        raise NotImplementedError()
    
    @property
    def name(self) -> str:
        '''Gets the name a shape.'''
        raise NotImplementedError()
    
    @name.setter
    def name(self, value : str) -> None:
        '''Sets the name a shape.'''
        raise NotImplementedError()
    
    @property
    def alternative_text(self) -> str:
        '''Gets the descriptive (alternative) text that will be associated with a shape.'''
        raise NotImplementedError()
    
    @alternative_text.setter
    def alternative_text(self, value : str) -> None:
        '''Sets the descriptive (alternative) text that will be associated with a shape.'''
        raise NotImplementedError()
    
    @property
    def effects(self) -> groupdocs.watermark.options.wordprocessing.IWordProcessingWatermarkEffects:
        '''Gets a value of :py:class:`groupdocs.watermark.options.wordprocessing.WordProcessingImageEffects` or
        :py:class:`groupdocs.watermark.options.wordprocessing.WordProcessingTextEffects` for effects that should be applied to the watermark.'''
        raise NotImplementedError()
    
    @effects.setter
    def effects(self, value : groupdocs.watermark.options.wordprocessing.IWordProcessingWatermarkEffects) -> None:
        '''Sets a value of :py:class:`groupdocs.watermark.options.wordprocessing.WordProcessingImageEffects` or
        :py:class:`groupdocs.watermark.options.wordprocessing.WordProcessingTextEffects` for effects that should be applied to the watermark.'''
        raise NotImplementedError()
    

class WordProcessingWatermarkHeaderFooterOptions(WordProcessingWatermarkBaseOptions):
    '''Represents options when adding the watermark to a Word section header/footer.'''
    
    def __init__(self) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.watermark.options.wordprocessing.WordProcessingWatermarkHeaderFooterOptions` class.'''
        raise NotImplementedError()
    
    @property
    def default(self) -> groupdocs.watermark.options.WatermarkOptions:
        '''Gets the default value for the :py:class:`groupdocs.watermark.options.WatermarkOptions` class.'''
        raise NotImplementedError()

    @property
    def is_locked(self) -> bool:
        '''Gets a value indicating whether an editing of the shape in Word is forbidden.'''
        raise NotImplementedError()
    
    @is_locked.setter
    def is_locked(self, value : bool) -> None:
        '''Sets a value indicating whether an editing of the shape in Word is forbidden.'''
        raise NotImplementedError()
    
    @property
    def lock_type(self) -> groupdocs.watermark.options.wordprocessing.WordProcessingLockType:
        '''Gets the watermark lock type.'''
        raise NotImplementedError()
    
    @lock_type.setter
    def lock_type(self, value : groupdocs.watermark.options.wordprocessing.WordProcessingLockType) -> None:
        '''Sets the watermark lock type.'''
        raise NotImplementedError()
    
    @property
    def password(self) -> str:
        '''Gets a password used to lock the watermark.'''
        raise NotImplementedError()
    
    @password.setter
    def password(self, value : str) -> None:
        '''Sets a password used to lock the watermark.'''
        raise NotImplementedError()
    
    @property
    def name(self) -> str:
        '''Gets the name a shape.'''
        raise NotImplementedError()
    
    @name.setter
    def name(self, value : str) -> None:
        '''Sets the name a shape.'''
        raise NotImplementedError()
    
    @property
    def alternative_text(self) -> str:
        '''Gets the descriptive (alternative) text that will be associated with a shape.'''
        raise NotImplementedError()
    
    @alternative_text.setter
    def alternative_text(self, value : str) -> None:
        '''Sets the descriptive (alternative) text that will be associated with a shape.'''
        raise NotImplementedError()
    
    @property
    def effects(self) -> groupdocs.watermark.options.wordprocessing.IWordProcessingWatermarkEffects:
        '''Gets a value of :py:class:`groupdocs.watermark.options.wordprocessing.WordProcessingImageEffects` or
        :py:class:`groupdocs.watermark.options.wordprocessing.WordProcessingTextEffects` for effects that should be applied to the watermark.'''
        raise NotImplementedError()
    
    @effects.setter
    def effects(self, value : groupdocs.watermark.options.wordprocessing.IWordProcessingWatermarkEffects) -> None:
        '''Sets a value of :py:class:`groupdocs.watermark.options.wordprocessing.WordProcessingImageEffects` or
        :py:class:`groupdocs.watermark.options.wordprocessing.WordProcessingTextEffects` for effects that should be applied to the watermark.'''
        raise NotImplementedError()
    
    @property
    def section_index(self) -> int:
        '''Gets the index of a section to add the watermark to.'''
        raise NotImplementedError()
    
    @section_index.setter
    def section_index(self, value : int) -> None:
        '''Sets the index of a section to add the watermark to.'''
        raise NotImplementedError()
    
    @property
    def header_footer_type(self) -> groupdocs.watermark.contents.OfficeHeaderFooterType:
        '''Gets the value that identifies the type of header or footer to add the watermark to.'''
        raise NotImplementedError()
    
    @header_footer_type.setter
    def header_footer_type(self, value : groupdocs.watermark.contents.OfficeHeaderFooterType) -> None:
        '''Sets the value that identifies the type of header or footer to add the watermark to.'''
        raise NotImplementedError()
    

class WordProcessingWatermarkPagesOptions(WordProcessingWatermarkBaseOptions):
    '''Represents options when adding watermark to Word document pages.'''
    
    def __init__(self) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.watermark.options.wordprocessing.WordProcessingWatermarkPagesOptions` class.'''
        raise NotImplementedError()
    
    @property
    def default(self) -> groupdocs.watermark.options.WatermarkOptions:
        '''Gets the default value for the :py:class:`groupdocs.watermark.options.WatermarkOptions` class.'''
        raise NotImplementedError()

    @property
    def is_locked(self) -> bool:
        '''Gets a value indicating whether an editing of the shape in Word is forbidden.'''
        raise NotImplementedError()
    
    @is_locked.setter
    def is_locked(self, value : bool) -> None:
        '''Sets a value indicating whether an editing of the shape in Word is forbidden.'''
        raise NotImplementedError()
    
    @property
    def lock_type(self) -> groupdocs.watermark.options.wordprocessing.WordProcessingLockType:
        '''Gets the watermark lock type.'''
        raise NotImplementedError()
    
    @lock_type.setter
    def lock_type(self, value : groupdocs.watermark.options.wordprocessing.WordProcessingLockType) -> None:
        '''Sets the watermark lock type.'''
        raise NotImplementedError()
    
    @property
    def password(self) -> str:
        '''Gets a password used to lock the watermark.'''
        raise NotImplementedError()
    
    @password.setter
    def password(self, value : str) -> None:
        '''Sets a password used to lock the watermark.'''
        raise NotImplementedError()
    
    @property
    def name(self) -> str:
        '''Gets the name a shape.'''
        raise NotImplementedError()
    
    @name.setter
    def name(self, value : str) -> None:
        '''Sets the name a shape.'''
        raise NotImplementedError()
    
    @property
    def alternative_text(self) -> str:
        '''Gets the descriptive (alternative) text that will be associated with a shape.'''
        raise NotImplementedError()
    
    @alternative_text.setter
    def alternative_text(self, value : str) -> None:
        '''Sets the descriptive (alternative) text that will be associated with a shape.'''
        raise NotImplementedError()
    
    @property
    def effects(self) -> groupdocs.watermark.options.wordprocessing.IWordProcessingWatermarkEffects:
        '''Gets a value of :py:class:`groupdocs.watermark.options.wordprocessing.WordProcessingImageEffects` or
        :py:class:`groupdocs.watermark.options.wordprocessing.WordProcessingTextEffects` for effects that should be applied to the watermark.'''
        raise NotImplementedError()
    
    @effects.setter
    def effects(self, value : groupdocs.watermark.options.wordprocessing.IWordProcessingWatermarkEffects) -> None:
        '''Sets a value of :py:class:`groupdocs.watermark.options.wordprocessing.WordProcessingImageEffects` or
        :py:class:`groupdocs.watermark.options.wordprocessing.WordProcessingTextEffects` for effects that should be applied to the watermark.'''
        raise NotImplementedError()
    
    @property
    def page_numbers(self) -> List[int]:
        '''Gets the page numbers to add the watermark.'''
        raise NotImplementedError()
    
    @page_numbers.setter
    def page_numbers(self, value : List[int]) -> None:
        '''Sets the page numbers to add the watermark.'''
        raise NotImplementedError()
    

class WordProcessingWatermarkSectionOptions(WordProcessingWatermarkBaseOptions):
    '''Represents options when adding shape watermark to a Word document section.'''
    
    def __init__(self) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.watermark.options.wordprocessing.WordProcessingWatermarkSectionOptions` class.'''
        raise NotImplementedError()
    
    @property
    def default(self) -> groupdocs.watermark.options.WatermarkOptions:
        '''Gets the default value for the :py:class:`groupdocs.watermark.options.WatermarkOptions` class.'''
        raise NotImplementedError()

    @property
    def is_locked(self) -> bool:
        '''Gets a value indicating whether an editing of the shape in Word is forbidden.'''
        raise NotImplementedError()
    
    @is_locked.setter
    def is_locked(self, value : bool) -> None:
        '''Sets a value indicating whether an editing of the shape in Word is forbidden.'''
        raise NotImplementedError()
    
    @property
    def lock_type(self) -> groupdocs.watermark.options.wordprocessing.WordProcessingLockType:
        '''Gets the watermark lock type.'''
        raise NotImplementedError()
    
    @lock_type.setter
    def lock_type(self, value : groupdocs.watermark.options.wordprocessing.WordProcessingLockType) -> None:
        '''Sets the watermark lock type.'''
        raise NotImplementedError()
    
    @property
    def password(self) -> str:
        '''Gets a password used to lock the watermark.'''
        raise NotImplementedError()
    
    @password.setter
    def password(self, value : str) -> None:
        '''Sets a password used to lock the watermark.'''
        raise NotImplementedError()
    
    @property
    def name(self) -> str:
        '''Gets the name a shape.'''
        raise NotImplementedError()
    
    @name.setter
    def name(self, value : str) -> None:
        '''Sets the name a shape.'''
        raise NotImplementedError()
    
    @property
    def alternative_text(self) -> str:
        '''Gets the descriptive (alternative) text that will be associated with a shape.'''
        raise NotImplementedError()
    
    @alternative_text.setter
    def alternative_text(self, value : str) -> None:
        '''Sets the descriptive (alternative) text that will be associated with a shape.'''
        raise NotImplementedError()
    
    @property
    def effects(self) -> groupdocs.watermark.options.wordprocessing.IWordProcessingWatermarkEffects:
        '''Gets a value of :py:class:`groupdocs.watermark.options.wordprocessing.WordProcessingImageEffects` or
        :py:class:`groupdocs.watermark.options.wordprocessing.WordProcessingTextEffects` for effects that should be applied to the watermark.'''
        raise NotImplementedError()
    
    @effects.setter
    def effects(self, value : groupdocs.watermark.options.wordprocessing.IWordProcessingWatermarkEffects) -> None:
        '''Sets a value of :py:class:`groupdocs.watermark.options.wordprocessing.WordProcessingImageEffects` or
        :py:class:`groupdocs.watermark.options.wordprocessing.WordProcessingTextEffects` for effects that should be applied to the watermark.'''
        raise NotImplementedError()
    
    @property
    def section_index(self) -> int:
        '''Gets the index of a section to add the watermark to.'''
        raise NotImplementedError()
    
    @section_index.setter
    def section_index(self, value : int) -> None:
        '''Sets the index of a section to add the watermark to.'''
        raise NotImplementedError()
    

class WordProcessingFlipOrientation:
    '''Possible values for the orientation of a shape.'''
    
    NONE : WordProcessingFlipOrientation
    '''Coordinates are not flipped.'''
    HORIZONTAL : WordProcessingFlipOrientation
    '''Flip along the y-axis, reversing the x-coordinates.'''
    VERTICAL : WordProcessingFlipOrientation
    '''Flip along the x-axis, reversing the y-coordinates.'''
    BOTH : WordProcessingFlipOrientation
    '''Flip along both the y- and x-axis.'''

class WordProcessingLockType:
    '''Specifies watermark lock type in Word document.'''
    
    ALLOW_ONLY_REVISIONS : WordProcessingLockType
    '''User can only add revision marks to the document.'''
    ALLOW_ONLY_COMMENTS : WordProcessingLockType
    '''User can only modify comments in the document.'''
    ALLOW_ONLY_FORM_FIELDS : WordProcessingLockType
    '''User can only enter data in the form fields in the document.'''
    READ_ONLY : WordProcessingLockType
    '''The entire document is read-only.'''
    READ_ONLY_WITH_EDITABLE_CONTENT : WordProcessingLockType
    '''The document is read-only, but all the content except of the watermark is marked as editable.'''
    NO_LOCK : WordProcessingLockType
    '''Disable any lock on watermark and document.'''

