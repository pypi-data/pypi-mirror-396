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

class Content(ContentPart):
    '''Represents a content where a watermark can be placed.'''
    
    @overload
    def find_images(self, search_criteria : groupdocs.watermark.search.searchcriteria.ImageSearchCriteria) -> groupdocs.watermark.contents.image.WatermarkableImageCollection:
        '''Finds images according to the specified search criteria.
        The search is conducted in the objects specified in :py:attr:`groupdocs.watermark.Watermarker.searchable_objects`.
        
        :param search_criteria: The search criteria to use.
        :returns: The collection of the found images.'''
        raise NotImplementedError()
    
    @overload
    def find_images(self) -> groupdocs.watermark.contents.image.WatermarkableImageCollection:
        '''Finds all images in the content.
        The search is conducted in the objects specified in :py:attr:`groupdocs.watermark.Watermarker.searchable_objects`.
        
        :returns: The collection of the found images.'''
        raise NotImplementedError()
    
    @overload
    def search(self, search_criteria : groupdocs.watermark.search.searchcriteria.SearchCriteria) -> groupdocs.watermark.search.PossibleWatermarkCollection:
        '''Finds possible watermarks according to specified search criteria.
        The search is conducted in the objects specified in :py:attr:`groupdocs.watermark.Watermarker.searchable_objects`.
        
        :param search_criteria: The search criteria to use.
        :returns: The collection of the possible watermarks.'''
        raise NotImplementedError()
    
    @overload
    def search(self) -> groupdocs.watermark.search.PossibleWatermarkCollection:
        '''Finds all possible watermarks in the content.
        The search is conducted in the objects specified in :py:attr:`groupdocs.watermark.Watermarker.searchable_objects`.
        
        :returns: The collection of the possible watermarks.'''
        raise NotImplementedError()
    

class ContentPart:
    '''Represents any logical part of a content (page, frame, header or
    a whole content) where watermark can be placed.'''
    
    @overload
    def find_images(self, search_criteria : groupdocs.watermark.search.searchcriteria.ImageSearchCriteria) -> groupdocs.watermark.contents.image.WatermarkableImageCollection:
        '''Finds images according to the specified search criteria.
        The search is conducted in the objects specified in :py:attr:`groupdocs.watermark.Watermarker.searchable_objects`.
        
        :param search_criteria: The search criteria to use.
        :returns: The collection of the found images.'''
        raise NotImplementedError()
    
    @overload
    def find_images(self) -> groupdocs.watermark.contents.image.WatermarkableImageCollection:
        '''Finds all images in the content.
        The search is conducted in the objects specified in :py:attr:`groupdocs.watermark.Watermarker.searchable_objects`.
        
        :returns: The collection of the found images.'''
        raise NotImplementedError()
    
    @overload
    def search(self, search_criteria : groupdocs.watermark.search.searchcriteria.SearchCriteria) -> groupdocs.watermark.search.PossibleWatermarkCollection:
        '''Finds possible watermarks according to specified search criteria.
        The search is conducted in the objects specified in :py:attr:`groupdocs.watermark.Watermarker.searchable_objects`.
        
        :param search_criteria: The search criteria to use.
        :returns: The collection of the possible watermarks.'''
        raise NotImplementedError()
    
    @overload
    def search(self) -> groupdocs.watermark.search.PossibleWatermarkCollection:
        '''Finds all possible watermarks in the content.
        The search is conducted in the objects specified in :py:attr:`groupdocs.watermark.Watermarker.searchable_objects`.
        
        :returns: The collection of the possible watermarks.'''
        raise NotImplementedError()
    

class OfficeImageEffects:
    '''Represents effects that can be applied to an image watermark for an office content.'''
    
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
    

class OfficeLineFormat:
    '''Represents a shape line format.'''
    
    def __init__(self) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.watermark.contents.OfficeLineFormat` class.'''
        raise NotImplementedError()
    
    @property
    def weight(self) -> float:
        '''Gets the brush thickness that strokes the path of a shape.'''
        raise NotImplementedError()
    
    @weight.setter
    def weight(self, value : float) -> None:
        '''Sets the brush thickness that strokes the path of a shape.'''
        raise NotImplementedError()
    
    @property
    def color(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets the color of the line.'''
        raise NotImplementedError()
    
    @color.setter
    def color(self, value : groupdocs.watermark.watermarks.Color) -> None:
        '''Sets the color of the line.'''
        raise NotImplementedError()
    
    @property
    def opacity(self) -> float:
        '''Gets the line opacity.'''
        raise NotImplementedError()
    
    @opacity.setter
    def opacity(self, value : float) -> None:
        '''Sets the line opacity.'''
        raise NotImplementedError()
    
    @property
    def enabled(self) -> bool:
        '''Gets a value indicating whether a shape will be stroked.'''
        raise NotImplementedError()
    
    @enabled.setter
    def enabled(self, value : bool) -> None:
        '''Sets a value indicating whether a shape will be stroked.'''
        raise NotImplementedError()
    
    @property
    def dash_style(self) -> groupdocs.watermark.contents.OfficeDashStyle:
        '''Gets the dot and dash pattern for a line.'''
        raise NotImplementedError()
    
    @dash_style.setter
    def dash_style(self, value : groupdocs.watermark.contents.OfficeDashStyle) -> None:
        '''Sets the dot and dash pattern for a line.'''
        raise NotImplementedError()
    
    @property
    def line_style(self) -> groupdocs.watermark.contents.OfficeLineStyle:
        '''Gets the line style.'''
        raise NotImplementedError()
    
    @line_style.setter
    def line_style(self, value : groupdocs.watermark.contents.OfficeLineStyle) -> None:
        '''Sets the line style.'''
        raise NotImplementedError()
    

class OfficeShapeSettings:
    '''Represents settings that can be applied to a shape watermark for an office content.'''
    
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
    

class OfficeTextEffects:
    '''Represents effects that can be applied to a text watermark for an office content.'''
    
    @property
    def line_format(self) -> groupdocs.watermark.contents.OfficeLineFormat:
        '''Gets the line format settings.'''
        raise NotImplementedError()
    
    @line_format.setter
    def line_format(self, value : groupdocs.watermark.contents.OfficeLineFormat) -> None:
        '''Sets the line format settings.'''
        raise NotImplementedError()
    

class OfficeDashStyle:
    '''Represents a dashed line style.'''
    
    SOLID : OfficeDashStyle
    '''Solid (continuous) pen.'''
    DEFAULT : OfficeDashStyle
    '''Same as :py:attr:`groupdocs.watermark.contents.OfficeDashStyle.SOLID`.'''
    DOT : OfficeDashStyle
    '''Dot style.'''
    DASH : OfficeDashStyle
    '''Dash style.'''
    DASH_DOT : OfficeDashStyle
    '''Dash dot style.'''
    DASH_DOT_DOT : OfficeDashStyle
    '''Dash dot dot style.'''

class OfficeHeaderFooterType:
    '''Identifies the type of header or footer.'''
    
    HEADER_PRIMARY : OfficeHeaderFooterType
    '''Primary header, also used for odd numbered pages.'''
    HEADER_EVEN : OfficeHeaderFooterType
    '''Header for even numbered pages.'''
    HEADER_FIRST : OfficeHeaderFooterType
    '''Header for the first page.'''
    FOOTER_PRIMARY : OfficeHeaderFooterType
    '''Primary footer, also used for odd numbered pages.'''
    FOOTER_EVEN : OfficeHeaderFooterType
    '''Footer for even numbered pages.'''
    FOOTER_FIRST : OfficeHeaderFooterType
    '''Footer for the first page.'''

class OfficeLineStyle:
    '''Represents the compound line style of a :py:class:`groupdocs.watermark.contents.OfficeLineFormat`.'''
    
    SINGLE : OfficeLineStyle
    '''Single line.'''
    DEFAULT : OfficeLineStyle
    '''Default value is :py:attr:`groupdocs.watermark.contents.OfficeLineStyle.SINGLE`.'''
    DOUBLE : OfficeLineStyle
    '''Double lines of equal width.'''
    THICK_THIN : OfficeLineStyle
    '''Double lines, one thick, one thin.'''
    THIN_THICK : OfficeLineStyle
    '''Double lines, one thin, one thick.'''
    TRIPLE : OfficeLineStyle
    '''Three lines, thin, thick, thin.'''

