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

class IPresentationWatermarkEffects:
    '''Represents interface for watermark effects that should be applied to the watermark.'''
    

class PresentationImageEffects(groupdocs.watermark.contents.OfficeImageEffects):
    '''Represents effects that can be applied to an image watermark for a PowerPoint document.'''
    
    def __init__(self) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.watermark.options.presentation.PresentationImageEffects` class.'''
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
    

class PresentationLoadOptions(groupdocs.watermark.options.LoadOptions):
    '''Represents document loading options for a Presentation document.'''
    
    @overload
    def __init__(self) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.watermark.options.presentation.PresentationLoadOptions` class.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, password : str) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.watermark.options.presentation.PresentationLoadOptions` class with a specified password.
        
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
    def default(self) -> groupdocs.watermark.options.presentation.PresentationLoadOptions:
        '''Gets the default value for the :py:class:`groupdocs.watermark.options.presentation.PresentationLoadOptions` class.'''
        raise NotImplementedError()


class PresentationPreviewOptions(groupdocs.watermark.options.PreviewOptions):
    '''Provides options to sets requirements and stream delegates for preview generation of Presentation document.'''
    
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


class PresentationSaveOptions(groupdocs.watermark.options.SaveOptions):
    '''Represents document saving options when saving a Presentation document.'''
    
    def __init__(self) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.watermark.options.presentation.PresentationSaveOptions` class.'''
        raise NotImplementedError()
    
    @property
    def default(self) -> groupdocs.watermark.options.presentation.PresentationSaveOptions:
        '''Gets the default value for the :py:class:`groupdocs.watermark.options.presentation.PresentationSaveOptions` class.'''
        raise NotImplementedError()


class PresentationTextEffects(groupdocs.watermark.contents.OfficeTextEffects):
    '''Represents effects that can be applied to a text watermark for a PowerPoint content.'''
    
    def __init__(self) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.watermark.options.presentation.PresentationTextEffects` class.'''
        raise NotImplementedError()
    
    @property
    def line_format(self) -> groupdocs.watermark.contents.OfficeLineFormat:
        '''Gets the line format settings.'''
        raise NotImplementedError()
    
    @line_format.setter
    def line_format(self, value : groupdocs.watermark.contents.OfficeLineFormat) -> None:
        '''Sets the line format settings.'''
        raise NotImplementedError()
    

class PresentationWatermarkBaseSlideOptions(PresentationWatermarkOptions):
    '''Base class for watermark adding options to a Presentation document.'''
    
    @property
    def default(self) -> groupdocs.watermark.options.WatermarkOptions:
        '''Gets the default value for the :py:class:`groupdocs.watermark.options.WatermarkOptions` class.'''
        raise NotImplementedError()

    @property
    def is_locked(self) -> bool:
        '''Gets a value indicating whether an editing of the shape in PowerPoint is forbidden.'''
        raise NotImplementedError()
    
    @is_locked.setter
    def is_locked(self, value : bool) -> None:
        '''Sets a value indicating whether an editing of the shape in PowerPoint is forbidden.'''
        raise NotImplementedError()
    
    @property
    def protect_with_unreadable_characters(self) -> bool:
        '''Gets a value indicating whether the text watermark characters are mixed with unreadable characters.'''
        raise NotImplementedError()
    
    @protect_with_unreadable_characters.setter
    def protect_with_unreadable_characters(self, value : bool) -> None:
        '''Sets a value indicating whether the text watermark characters are mixed with unreadable characters.'''
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
    def effects(self) -> groupdocs.watermark.options.presentation.IPresentationWatermarkEffects:
        '''Gets a value of :py:class:`groupdocs.watermark.options.presentation.PresentationImageEffects` or
        :py:class:`groupdocs.watermark.options.presentation.PresentationTextEffects` for effects that should be applied to the watermark.'''
        raise NotImplementedError()
    
    @effects.setter
    def effects(self, value : groupdocs.watermark.options.presentation.IPresentationWatermarkEffects) -> None:
        '''Sets a value of :py:class:`groupdocs.watermark.options.presentation.PresentationImageEffects` or
        :py:class:`groupdocs.watermark.options.presentation.PresentationTextEffects` for effects that should be applied to the watermark.'''
        raise NotImplementedError()
    

class PresentationWatermarkLayoutSlideOptions(PresentationWatermarkBaseSlideOptions):
    '''Represents options when adding watermark to a Presentation document layout slide.'''
    
    def __init__(self) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.watermark.options.presentation.PresentationWatermarkOptions` class.'''
        raise NotImplementedError()
    
    @property
    def default(self) -> groupdocs.watermark.options.WatermarkOptions:
        '''Gets the default value for the :py:class:`groupdocs.watermark.options.WatermarkOptions` class.'''
        raise NotImplementedError()

    @property
    def is_locked(self) -> bool:
        '''Gets a value indicating whether an editing of the shape in PowerPoint is forbidden.'''
        raise NotImplementedError()
    
    @is_locked.setter
    def is_locked(self, value : bool) -> None:
        '''Sets a value indicating whether an editing of the shape in PowerPoint is forbidden.'''
        raise NotImplementedError()
    
    @property
    def protect_with_unreadable_characters(self) -> bool:
        '''Gets a value indicating whether the text watermark characters are mixed with unreadable characters.'''
        raise NotImplementedError()
    
    @protect_with_unreadable_characters.setter
    def protect_with_unreadable_characters(self, value : bool) -> None:
        '''Sets a value indicating whether the text watermark characters are mixed with unreadable characters.'''
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
    def effects(self) -> groupdocs.watermark.options.presentation.IPresentationWatermarkEffects:
        '''Gets a value of :py:class:`groupdocs.watermark.options.presentation.PresentationImageEffects` or
        :py:class:`groupdocs.watermark.options.presentation.PresentationTextEffects` for effects that should be applied to the watermark.'''
        raise NotImplementedError()
    
    @effects.setter
    def effects(self, value : groupdocs.watermark.options.presentation.IPresentationWatermarkEffects) -> None:
        '''Sets a value of :py:class:`groupdocs.watermark.options.presentation.PresentationImageEffects` or
        :py:class:`groupdocs.watermark.options.presentation.PresentationTextEffects` for effects that should be applied to the watermark.'''
        raise NotImplementedError()
    
    @property
    def layout_slide_index(self) -> int:
        '''Gets the index of layout slide to add the watermark to.'''
        raise NotImplementedError()
    
    @layout_slide_index.setter
    def layout_slide_index(self, value : int) -> None:
        '''Sets the index of layout slide to add the watermark to.'''
        raise NotImplementedError()
    

class PresentationWatermarkMasterHandoutSlideOptions(PresentationWatermarkBaseSlideOptions):
    '''Represents options when adding watermark to a Presentation document master handout slide.'''
    
    def __init__(self) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.watermark.options.presentation.PresentationWatermarkMasterHandoutSlideOptions` class.'''
        raise NotImplementedError()
    
    @property
    def default(self) -> groupdocs.watermark.options.WatermarkOptions:
        '''Gets the default value for the :py:class:`groupdocs.watermark.options.WatermarkOptions` class.'''
        raise NotImplementedError()

    @property
    def is_locked(self) -> bool:
        '''Gets a value indicating whether an editing of the shape in PowerPoint is forbidden.'''
        raise NotImplementedError()
    
    @is_locked.setter
    def is_locked(self, value : bool) -> None:
        '''Sets a value indicating whether an editing of the shape in PowerPoint is forbidden.'''
        raise NotImplementedError()
    
    @property
    def protect_with_unreadable_characters(self) -> bool:
        '''Gets a value indicating whether the text watermark characters are mixed with unreadable characters.'''
        raise NotImplementedError()
    
    @protect_with_unreadable_characters.setter
    def protect_with_unreadable_characters(self, value : bool) -> None:
        '''Sets a value indicating whether the text watermark characters are mixed with unreadable characters.'''
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
    def effects(self) -> groupdocs.watermark.options.presentation.IPresentationWatermarkEffects:
        '''Gets a value of :py:class:`groupdocs.watermark.options.presentation.PresentationImageEffects` or
        :py:class:`groupdocs.watermark.options.presentation.PresentationTextEffects` for effects that should be applied to the watermark.'''
        raise NotImplementedError()
    
    @effects.setter
    def effects(self, value : groupdocs.watermark.options.presentation.IPresentationWatermarkEffects) -> None:
        '''Sets a value of :py:class:`groupdocs.watermark.options.presentation.PresentationImageEffects` or
        :py:class:`groupdocs.watermark.options.presentation.PresentationTextEffects` for effects that should be applied to the watermark.'''
        raise NotImplementedError()
    

class PresentationWatermarkMasterNotesSlideOptions(PresentationWatermarkBaseSlideOptions):
    '''Represents options when adding watermark to a Presentation document master notes slide.'''
    
    def __init__(self) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.watermark.options.presentation.PresentationWatermarkMasterNotesSlideOptions` class.'''
        raise NotImplementedError()
    
    @property
    def default(self) -> groupdocs.watermark.options.WatermarkOptions:
        '''Gets the default value for the :py:class:`groupdocs.watermark.options.WatermarkOptions` class.'''
        raise NotImplementedError()

    @property
    def is_locked(self) -> bool:
        '''Gets a value indicating whether an editing of the shape in PowerPoint is forbidden.'''
        raise NotImplementedError()
    
    @is_locked.setter
    def is_locked(self, value : bool) -> None:
        '''Sets a value indicating whether an editing of the shape in PowerPoint is forbidden.'''
        raise NotImplementedError()
    
    @property
    def protect_with_unreadable_characters(self) -> bool:
        '''Gets a value indicating whether the text watermark characters are mixed with unreadable characters.'''
        raise NotImplementedError()
    
    @protect_with_unreadable_characters.setter
    def protect_with_unreadable_characters(self, value : bool) -> None:
        '''Sets a value indicating whether the text watermark characters are mixed with unreadable characters.'''
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
    def effects(self) -> groupdocs.watermark.options.presentation.IPresentationWatermarkEffects:
        '''Gets a value of :py:class:`groupdocs.watermark.options.presentation.PresentationImageEffects` or
        :py:class:`groupdocs.watermark.options.presentation.PresentationTextEffects` for effects that should be applied to the watermark.'''
        raise NotImplementedError()
    
    @effects.setter
    def effects(self, value : groupdocs.watermark.options.presentation.IPresentationWatermarkEffects) -> None:
        '''Sets a value of :py:class:`groupdocs.watermark.options.presentation.PresentationImageEffects` or
        :py:class:`groupdocs.watermark.options.presentation.PresentationTextEffects` for effects that should be applied to the watermark.'''
        raise NotImplementedError()
    

class PresentationWatermarkMasterSlideOptions(PresentationWatermarkBaseSlideOptions):
    '''Represents options when adding watermark to a Presentation document master slide.'''
    
    def __init__(self) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.watermark.options.presentation.PresentationWatermarkMasterSlideOptions` class.'''
        raise NotImplementedError()
    
    @property
    def default(self) -> groupdocs.watermark.options.WatermarkOptions:
        '''Gets the default value for the :py:class:`groupdocs.watermark.options.WatermarkOptions` class.'''
        raise NotImplementedError()

    @property
    def is_locked(self) -> bool:
        '''Gets a value indicating whether an editing of the shape in PowerPoint is forbidden.'''
        raise NotImplementedError()
    
    @is_locked.setter
    def is_locked(self, value : bool) -> None:
        '''Sets a value indicating whether an editing of the shape in PowerPoint is forbidden.'''
        raise NotImplementedError()
    
    @property
    def protect_with_unreadable_characters(self) -> bool:
        '''Gets a value indicating whether the text watermark characters are mixed with unreadable characters.'''
        raise NotImplementedError()
    
    @protect_with_unreadable_characters.setter
    def protect_with_unreadable_characters(self, value : bool) -> None:
        '''Sets a value indicating whether the text watermark characters are mixed with unreadable characters.'''
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
    def effects(self) -> groupdocs.watermark.options.presentation.IPresentationWatermarkEffects:
        '''Gets a value of :py:class:`groupdocs.watermark.options.presentation.PresentationImageEffects` or
        :py:class:`groupdocs.watermark.options.presentation.PresentationTextEffects` for effects that should be applied to the watermark.'''
        raise NotImplementedError()
    
    @effects.setter
    def effects(self, value : groupdocs.watermark.options.presentation.IPresentationWatermarkEffects) -> None:
        '''Sets a value of :py:class:`groupdocs.watermark.options.presentation.PresentationImageEffects` or
        :py:class:`groupdocs.watermark.options.presentation.PresentationTextEffects` for effects that should be applied to the watermark.'''
        raise NotImplementedError()
    
    @property
    def master_slide_index(self) -> int:
        '''Gets the index of master slide to add the watermark to.'''
        raise NotImplementedError()
    
    @master_slide_index.setter
    def master_slide_index(self, value : int) -> None:
        '''Sets the index of master slide to add the watermark to.'''
        raise NotImplementedError()
    

class PresentationWatermarkNoteSlideOptions(PresentationWatermarkBaseSlideOptions):
    '''Represents options when adding watermark to a Presentation document note slide.'''
    
    def __init__(self) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.watermark.options.presentation.PresentationWatermarkNoteSlideOptions` class.'''
        raise NotImplementedError()
    
    @property
    def default(self) -> groupdocs.watermark.options.WatermarkOptions:
        '''Gets the default value for the :py:class:`groupdocs.watermark.options.WatermarkOptions` class.'''
        raise NotImplementedError()

    @property
    def is_locked(self) -> bool:
        '''Gets a value indicating whether an editing of the shape in PowerPoint is forbidden.'''
        raise NotImplementedError()
    
    @is_locked.setter
    def is_locked(self, value : bool) -> None:
        '''Sets a value indicating whether an editing of the shape in PowerPoint is forbidden.'''
        raise NotImplementedError()
    
    @property
    def protect_with_unreadable_characters(self) -> bool:
        '''Gets a value indicating whether the text watermark characters are mixed with unreadable characters.'''
        raise NotImplementedError()
    
    @protect_with_unreadable_characters.setter
    def protect_with_unreadable_characters(self, value : bool) -> None:
        '''Sets a value indicating whether the text watermark characters are mixed with unreadable characters.'''
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
    def effects(self) -> groupdocs.watermark.options.presentation.IPresentationWatermarkEffects:
        '''Gets a value of :py:class:`groupdocs.watermark.options.presentation.PresentationImageEffects` or
        :py:class:`groupdocs.watermark.options.presentation.PresentationTextEffects` for effects that should be applied to the watermark.'''
        raise NotImplementedError()
    
    @effects.setter
    def effects(self, value : groupdocs.watermark.options.presentation.IPresentationWatermarkEffects) -> None:
        '''Sets a value of :py:class:`groupdocs.watermark.options.presentation.PresentationImageEffects` or
        :py:class:`groupdocs.watermark.options.presentation.PresentationTextEffects` for effects that should be applied to the watermark.'''
        raise NotImplementedError()
    
    @property
    def slide_index(self) -> int:
        '''Gets the index of a slide to add the watermark to note slide of it.'''
        raise NotImplementedError()
    
    @slide_index.setter
    def slide_index(self, value : int) -> None:
        '''Sets the index of a slide to add the watermark to note slide of it.'''
        raise NotImplementedError()
    

class PresentationWatermarkOptions(groupdocs.watermark.options.WatermarkOptions):
    '''Base class for watermark adding options to a Presentation document.'''
    
    @property
    def default(self) -> groupdocs.watermark.options.WatermarkOptions:
        '''Gets the default value for the :py:class:`groupdocs.watermark.options.WatermarkOptions` class.'''
        raise NotImplementedError()


class PresentationWatermarkSlideOptions(PresentationWatermarkBaseSlideOptions):
    '''Represents options when adding watermark to a Presentation document slide.'''
    
    def __init__(self) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.watermark.options.presentation.PresentationWatermarkSlideOptions` class.'''
        raise NotImplementedError()
    
    @property
    def default(self) -> groupdocs.watermark.options.WatermarkOptions:
        '''Gets the default value for the :py:class:`groupdocs.watermark.options.WatermarkOptions` class.'''
        raise NotImplementedError()

    @property
    def is_locked(self) -> bool:
        '''Gets a value indicating whether an editing of the shape in PowerPoint is forbidden.'''
        raise NotImplementedError()
    
    @is_locked.setter
    def is_locked(self, value : bool) -> None:
        '''Sets a value indicating whether an editing of the shape in PowerPoint is forbidden.'''
        raise NotImplementedError()
    
    @property
    def protect_with_unreadable_characters(self) -> bool:
        '''Gets a value indicating whether the text watermark characters are mixed with unreadable characters.'''
        raise NotImplementedError()
    
    @protect_with_unreadable_characters.setter
    def protect_with_unreadable_characters(self, value : bool) -> None:
        '''Sets a value indicating whether the text watermark characters are mixed with unreadable characters.'''
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
    def effects(self) -> groupdocs.watermark.options.presentation.IPresentationWatermarkEffects:
        '''Gets a value of :py:class:`groupdocs.watermark.options.presentation.PresentationImageEffects` or
        :py:class:`groupdocs.watermark.options.presentation.PresentationTextEffects` for effects that should be applied to the watermark.'''
        raise NotImplementedError()
    
    @effects.setter
    def effects(self, value : groupdocs.watermark.options.presentation.IPresentationWatermarkEffects) -> None:
        '''Sets a value of :py:class:`groupdocs.watermark.options.presentation.PresentationImageEffects` or
        :py:class:`groupdocs.watermark.options.presentation.PresentationTextEffects` for effects that should be applied to the watermark.'''
        raise NotImplementedError()
    
    @property
    def slide_index(self) -> int:
        '''Gets the index of slide to add the watermark to.'''
        raise NotImplementedError()
    
    @slide_index.setter
    def slide_index(self, value : int) -> None:
        '''Sets the index of slide to add the watermark to.'''
        raise NotImplementedError()
    

