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

class FormattedTextFragment:
    '''Provides abstract base class for a fragment of formatted text in a content.'''
    
    @property
    def text(self) -> str:
        '''Gets the fragment text.'''
        raise NotImplementedError()
    
    @property
    def font(self) -> groupdocs.watermark.watermarks.Font:
        '''Gets the font of the text.'''
        raise NotImplementedError()
    
    @property
    def foreground_color(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets the foreground color of the text.'''
        raise NotImplementedError()
    
    @property
    def background_color(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets the background color of the text.'''
        raise NotImplementedError()
    

class FormattedTextFragmentCollection:
    '''Represents a mutable collection of formatted text fragments.'''
    
    @overload
    def add(self, text : str) -> None:
        '''Adds a formatted text fragment to the collection.
        
        :param text: The fragment text.'''
        raise NotImplementedError()
    
    @overload
    def add(self, text : str, font : groupdocs.watermark.watermarks.Font) -> None:
        '''Adds a formatted text fragment to the collection.
        
        :param text: The fragment text.
        :param font: The font of the text.'''
        raise NotImplementedError()
    
    @overload
    def add(self, text : str, font : groupdocs.watermark.watermarks.Font, foreground_color : groupdocs.watermark.watermarks.Color) -> None:
        '''Adds a formatted text fragment to the collection.
        
        :param text: The fragment text.
        :param font: The font of the text.
        :param foreground_color: The foreground color of the text.'''
        raise NotImplementedError()
    
    @overload
    def add(self, text : str, font : groupdocs.watermark.watermarks.Font, foreground_color : groupdocs.watermark.watermarks.Color, background_color : groupdocs.watermark.watermarks.Color) -> None:
        '''Adds a formatted text fragment to the collection.
        
        :param text: The fragment text.
        :param font: The font of the text.
        :param foreground_color: The foreground color of the text.
        :param background_color: The background color of the text.'''
        raise NotImplementedError()
    
    @property
    def collection_type(self) -> groupdocs.watermark.search.FormattedTextFragmentCollectionType:
        '''Gets the formatted fragment collection type.'''
        raise NotImplementedError()
    

class HyperlinkPossibleWatermark(PossibleWatermark):
    '''Represents possible hyperlink watermark in a PowerPoint content.'''
    
    @property
    def parent(self) -> groupdocs.watermark.contents.ContentPart:
        '''Gets the parent of this :py:class:`groupdocs.watermark.search.HyperlinkPossibleWatermark`.'''
        raise NotImplementedError()
    
    @property
    def page_number(self) -> System.Nullable`1[[System.Int32]]:
        '''Gets the page watermark is placed on.'''
        raise NotImplementedError()
    
    @property
    def width(self) -> float:
        '''Gets the width of this :py:class:`groupdocs.watermark.search.HyperlinkPossibleWatermark`.'''
        raise NotImplementedError()
    
    @property
    def height(self) -> float:
        '''Gets the height of this :py:class:`groupdocs.watermark.search.HyperlinkPossibleWatermark`.'''
        raise NotImplementedError()
    
    @property
    def x(self) -> float:
        '''Gets the x-coordinate of this :py:class:`groupdocs.watermark.search.HyperlinkPossibleWatermark`.'''
        raise NotImplementedError()
    
    @property
    def y(self) -> float:
        '''Gets the y-coordinate of this :py:class:`groupdocs.watermark.search.HyperlinkPossibleWatermark`.'''
        raise NotImplementedError()
    
    @property
    def rotate_angle(self) -> float:
        '''Gets the rotate angle of this :py:class:`groupdocs.watermark.search.HyperlinkPossibleWatermark` in degrees.'''
        raise NotImplementedError()
    
    @property
    def text(self) -> str:
        '''Gets the url of this :py:class:`groupdocs.watermark.search.HyperlinkPossibleWatermark`.'''
        raise NotImplementedError()
    
    @text.setter
    def text(self, value : str) -> None:
        '''Sets the url of this :py:class:`groupdocs.watermark.search.HyperlinkPossibleWatermark`.'''
        raise NotImplementedError()
    
    @property
    def formatted_text_fragments(self) -> groupdocs.watermark.search.FormattedTextFragmentCollection:
        '''Gets the collection of formatted text fragments of this :py:class:`groupdocs.watermark.search.PossibleWatermark`.'''
        raise NotImplementedError()
    
    @property
    def image_data(self) -> List[int]:
        '''Gets the image of this :py:class:`groupdocs.watermark.search.PossibleWatermark`.'''
        raise NotImplementedError()
    
    @image_data.setter
    def image_data(self, value : List[int]) -> None:
        '''Sets the image of this :py:class:`groupdocs.watermark.search.PossibleWatermark`.'''
        raise NotImplementedError()
    
    @property
    def unit_of_measurement(self) -> groupdocs.watermark.UnitOfMeasurement:
        '''Gets the unit of measurement of this :py:class:`groupdocs.watermark.search.HyperlinkPossibleWatermark`.'''
        raise NotImplementedError()
    

class IRotatableTwoDObject:
    '''Represents any rotatable two dimensional object in a content structure.'''
    
    @property
    def rotate_angle(self) -> float:
        '''Gets the rotate angle of the object in degrees.'''
        raise NotImplementedError()
    

class ITwoDObject:
    '''Represents any two dimensional object in a content structure.'''
    
    @property
    def x(self) -> float:
        '''Gets the x-coordinate of the object.'''
        raise NotImplementedError()
    
    @property
    def y(self) -> float:
        '''Gets the y-coordinate of the object.'''
        raise NotImplementedError()
    
    @property
    def width(self) -> float:
        '''Gets the width of the object.'''
        raise NotImplementedError()
    
    @property
    def height(self) -> float:
        '''Gets the height of the object.'''
        raise NotImplementedError()
    

class PossibleWatermark:
    '''Represents possible watermark found in a document.'''
    
    @property
    def parent(self) -> groupdocs.watermark.contents.ContentPart:
        '''Gets the parent of this :py:class:`groupdocs.watermark.search.PossibleWatermark`.'''
        raise NotImplementedError()
    
    @property
    def page_number(self) -> System.Nullable`1[[System.Int32]]:
        '''Gets the page watermark is placed on.'''
        raise NotImplementedError()
    
    @property
    def width(self) -> float:
        '''Gets the width of this :py:class:`groupdocs.watermark.search.PossibleWatermark`.'''
        raise NotImplementedError()
    
    @property
    def height(self) -> float:
        '''Gets the height of this :py:class:`groupdocs.watermark.search.PossibleWatermark`.'''
        raise NotImplementedError()
    
    @property
    def x(self) -> float:
        '''Gets the x-coordinate of this :py:class:`groupdocs.watermark.search.PossibleWatermark`.'''
        raise NotImplementedError()
    
    @property
    def y(self) -> float:
        '''Gets the y-coordinate of this :py:class:`groupdocs.watermark.search.PossibleWatermark`.'''
        raise NotImplementedError()
    
    @property
    def rotate_angle(self) -> float:
        '''Gets the rotate angle of this :py:class:`groupdocs.watermark.search.PossibleWatermark` in degrees.'''
        raise NotImplementedError()
    
    @property
    def text(self) -> str:
        '''Gets the text of this :py:class:`groupdocs.watermark.search.PossibleWatermark`.'''
        raise NotImplementedError()
    
    @text.setter
    def text(self, value : str) -> None:
        '''Sets the text of this :py:class:`groupdocs.watermark.search.PossibleWatermark`.'''
        raise NotImplementedError()
    
    @property
    def formatted_text_fragments(self) -> groupdocs.watermark.search.FormattedTextFragmentCollection:
        '''Gets the collection of formatted text fragments of this :py:class:`groupdocs.watermark.search.PossibleWatermark`.'''
        raise NotImplementedError()
    
    @property
    def image_data(self) -> List[int]:
        '''Gets the image of this :py:class:`groupdocs.watermark.search.PossibleWatermark`.'''
        raise NotImplementedError()
    
    @image_data.setter
    def image_data(self, value : List[int]) -> None:
        '''Sets the image of this :py:class:`groupdocs.watermark.search.PossibleWatermark`.'''
        raise NotImplementedError()
    
    @property
    def unit_of_measurement(self) -> groupdocs.watermark.UnitOfMeasurement:
        '''Gets the unit of measurement of this :py:class:`groupdocs.watermark.search.PossibleWatermark`.'''
        raise NotImplementedError()
    

class PossibleWatermarkCollection:
    '''Represents a collection of possible watermarks found in a content.'''
    

class ShapeSearchAdapter:
    '''Provides base class for a shape containing specific pieces of document that are to be included in watermark
    search.'''
    

class TwoDObjectPossibleWatermark(PossibleWatermark):
    '''Represents 2D object watermark in a content of any supported format.'''
    
    @property
    def parent(self) -> groupdocs.watermark.contents.ContentPart:
        '''Gets the parent of this :py:class:`groupdocs.watermark.search.PossibleWatermark`.'''
        raise NotImplementedError()
    
    @property
    def page_number(self) -> System.Nullable`1[[System.Int32]]:
        '''Gets the page watermark is placed on.'''
        raise NotImplementedError()
    
    @property
    def width(self) -> float:
        '''Gets the width of the 2D object.'''
        raise NotImplementedError()
    
    @property
    def height(self) -> float:
        '''Gets the height of the 2D object.'''
        raise NotImplementedError()
    
    @property
    def x(self) -> float:
        '''Gets the x-coordinate of the 2D object.'''
        raise NotImplementedError()
    
    @property
    def y(self) -> float:
        '''Gets the y-coordinate of the 2D object.'''
        raise NotImplementedError()
    
    @property
    def rotate_angle(self) -> float:
        '''Gets the rotate angle of the 2D object in degrees.'''
        raise NotImplementedError()
    
    @property
    def text(self) -> str:
        '''Gets the text of this :py:class:`groupdocs.watermark.search.PossibleWatermark`.'''
        raise NotImplementedError()
    
    @text.setter
    def text(self, value : str) -> None:
        '''Sets the text of this :py:class:`groupdocs.watermark.search.PossibleWatermark`.'''
        raise NotImplementedError()
    
    @property
    def formatted_text_fragments(self) -> groupdocs.watermark.search.FormattedTextFragmentCollection:
        '''Gets the collection of formatted text fragments of this :py:class:`groupdocs.watermark.search.PossibleWatermark`.'''
        raise NotImplementedError()
    
    @property
    def image_data(self) -> List[int]:
        '''Gets the image of this :py:class:`groupdocs.watermark.search.PossibleWatermark`.'''
        raise NotImplementedError()
    
    @image_data.setter
    def image_data(self, value : List[int]) -> None:
        '''Sets the image of this :py:class:`groupdocs.watermark.search.PossibleWatermark`.'''
        raise NotImplementedError()
    
    @property
    def unit_of_measurement(self) -> groupdocs.watermark.UnitOfMeasurement:
        '''Gets the unit of measurement of the 2D object.'''
        raise NotImplementedError()
    

class FormattedTextFragmentCollectionType:
    '''Specifies the number of elements a formatted text fragment collection can contain.'''
    
    UNLIMITED_FRAGMENTS : FormattedTextFragmentCollectionType
    '''Multiple styles are allowed, the collection can contain unlimited count of fragments.'''
    SINGLE_FRAGMENT : FormattedTextFragmentCollectionType
    '''Whole text can be formatted with a single style, the collection can contain only one fragment.'''
    NO_FORMATTED_TEXT : FormattedTextFragmentCollectionType
    '''Parent object doesn\'t support text formatting, the collection is always empty.'''

