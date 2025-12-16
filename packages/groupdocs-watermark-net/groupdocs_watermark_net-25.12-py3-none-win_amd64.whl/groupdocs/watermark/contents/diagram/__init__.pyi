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

class DiagramContent(groupdocs.watermark.contents.Content):
    '''Represents a Visio document.'''
    
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
    
    @property
    def pages(self) -> groupdocs.watermark.contents.diagram.DiagramPageCollection:
        '''Gets the collection of all pages of this :py:class:`groupdocs.watermark.contents.diagram.DiagramContent`.'''
        raise NotImplementedError()
    
    @property
    def header_footer(self) -> groupdocs.watermark.contents.diagram.DiagramHeaderFooter:
        '''Gets the header and footer of this :py:class:`groupdocs.watermark.contents.diagram.DiagramContent`.'''
        raise NotImplementedError()
    

class DiagramFormattedTextFragment(groupdocs.watermark.search.FormattedTextFragment):
    '''Represents a fragment of formatted text in a Visio document.'''
    
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
    

class DiagramFormattedTextFragmentCollection(groupdocs.watermark.search.FormattedTextFragmentCollection):
    '''Represents a collection of formatted text fragments in a Visio document.'''
    
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
    

class DiagramHeaderFooter:
    '''Represents a header/footer in a Visio document.'''
    
    @property
    def header_left(self) -> str:
        '''Gets the text string that appears in the left portion of document header.'''
        raise NotImplementedError()
    
    @header_left.setter
    def header_left(self, value : str) -> None:
        '''Sets the text string that appears in the left portion of document header.'''
        raise NotImplementedError()
    
    @property
    def header_center(self) -> str:
        '''Gets the text string that appears in the center portion of document header.'''
        raise NotImplementedError()
    
    @header_center.setter
    def header_center(self, value : str) -> None:
        '''Sets the text string that appears in the center portion of document header.'''
        raise NotImplementedError()
    
    @property
    def header_right(self) -> str:
        '''Gets the text string that appears in the right portion of document header.'''
        raise NotImplementedError()
    
    @header_right.setter
    def header_right(self, value : str) -> None:
        '''Sets the text string that appears in the right portion of document header.'''
        raise NotImplementedError()
    
    @property
    def footer_left(self) -> str:
        '''Gets the text string that appears in the left portion of document footer.'''
        raise NotImplementedError()
    
    @footer_left.setter
    def footer_left(self, value : str) -> None:
        '''Sets the text string that appears in the left portion of document footer.'''
        raise NotImplementedError()
    
    @property
    def footer_center(self) -> str:
        '''Gets the text string that appears in the center portion of document footer.'''
        raise NotImplementedError()
    
    @footer_center.setter
    def footer_center(self, value : str) -> None:
        '''Sets the text string that appears in the center portion of document footer.'''
        raise NotImplementedError()
    
    @property
    def footer_right(self) -> str:
        '''Gets the text string that appears in the right portion of document footer.'''
        raise NotImplementedError()
    
    @footer_right.setter
    def footer_right(self, value : str) -> None:
        '''Sets the text string that appears in the right portion of document footer.'''
        raise NotImplementedError()
    
    @property
    def header_margin(self) -> float:
        '''Gets the margin of document header.'''
        raise NotImplementedError()
    
    @header_margin.setter
    def header_margin(self, value : float) -> None:
        '''Sets the margin of document header.'''
        raise NotImplementedError()
    
    @property
    def footer_margin(self) -> float:
        '''Gets the margin of document header.'''
        raise NotImplementedError()
    
    @footer_margin.setter
    def footer_margin(self, value : float) -> None:
        '''Sets the margin of document header.'''
        raise NotImplementedError()
    
    @property
    def text_color(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets the text color for header and footer.'''
        raise NotImplementedError()
    
    @text_color.setter
    def text_color(self, value : groupdocs.watermark.watermarks.Color) -> None:
        '''Sets the text color for header and footer.'''
        raise NotImplementedError()
    
    @property
    def font(self) -> groupdocs.watermark.contents.diagram.DiagramHeaderFooterFont:
        '''Gets the font used for header and footer text.'''
        raise NotImplementedError()
    

class DiagramHeaderFooterFont:
    '''Represents a font that is used in Visio header/footer.'''
    
    @property
    def family_name(self) -> str:
        '''Gets the font family name.'''
        raise NotImplementedError()
    
    @family_name.setter
    def family_name(self, value : str) -> None:
        '''Sets the font family name.'''
        raise NotImplementedError()
    
    @property
    def size(self) -> int:
        '''Gets the height of the font.'''
        raise NotImplementedError()
    
    @size.setter
    def size(self, value : int) -> None:
        '''Sets the height of the font.'''
        raise NotImplementedError()
    
    @property
    def italic(self) -> bool:
        '''Gets a value indicating whether the font is italic.'''
        raise NotImplementedError()
    
    @italic.setter
    def italic(self, value : bool) -> None:
        '''Sets a value indicating whether the font is italic.'''
        raise NotImplementedError()
    
    @property
    def underline(self) -> bool:
        '''Gets a value indicating whether the font is underline.'''
        raise NotImplementedError()
    
    @underline.setter
    def underline(self, value : bool) -> None:
        '''Sets a value indicating whether the font is underline.'''
        raise NotImplementedError()
    
    @property
    def strikeout(self) -> bool:
        '''Gets a value indicating whether the font is strikeout.'''
        raise NotImplementedError()
    
    @strikeout.setter
    def strikeout(self, value : bool) -> None:
        '''Sets a value indicating whether the font is strikeout.'''
        raise NotImplementedError()
    
    @property
    def bold(self) -> bool:
        '''Gets a value indicating whether the font is bold.'''
        raise NotImplementedError()
    
    @bold.setter
    def bold(self, value : bool) -> None:
        '''Sets a value indicating whether the font is bold.'''
        raise NotImplementedError()
    

class DiagramHyperlink:
    '''Represents a hyperlink in a Visio document.'''
    
    @property
    def address(self) -> str:
        '''Gets the hyperlink address.'''
        raise NotImplementedError()
    
    @property
    def sub_address(self) -> str:
        '''Gets a location within the target content to link to.'''
        raise NotImplementedError()
    
    @property
    def description(self) -> str:
        '''Gets the description of the hyperlink.'''
        raise NotImplementedError()
    

class DiagramHyperlinkCollection:
    '''Represents a collection of hyperlinks in a Visio document.'''
    

class DiagramPage(groupdocs.watermark.contents.ContentPart):
    '''Represents a Visio document page.'''
    
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
    
    @property
    def shapes(self) -> groupdocs.watermark.contents.diagram.DiagramShapeCollection:
        '''Gets the collection of all shapes of the page.'''
        raise NotImplementedError()
    
    @property
    def is_background(self) -> bool:
        '''Gets a value indicating whether the page is a background page.'''
        raise NotImplementedError()
    
    @property
    def background_page(self) -> groupdocs.watermark.contents.diagram.DiagramPage:
        '''Gets the background page for this :py:class:`groupdocs.watermark.contents.diagram.DiagramPage`.'''
        raise NotImplementedError()
    
    @property
    def width(self) -> float:
        '''Gets the width of this :py:class:`groupdocs.watermark.contents.diagram.DiagramPage` in points.'''
        raise NotImplementedError()
    
    @property
    def height(self) -> float:
        '''Gets the height of this :py:class:`groupdocs.watermark.contents.diagram.DiagramPage` in points.'''
        raise NotImplementedError()
    
    @property
    def top_margin(self) -> float:
        '''Gets the size of the top margin in points.'''
        raise NotImplementedError()
    
    @property
    def right_margin(self) -> float:
        '''Gets the size of the right margin in points.'''
        raise NotImplementedError()
    
    @property
    def bottom_margin(self) -> float:
        '''Gets the size of the bottom margin in points.'''
        raise NotImplementedError()
    
    @property
    def left_margin(self) -> float:
        '''Gets the size of the left margin in points.'''
        raise NotImplementedError()
    
    @property
    def is_visible(self) -> bool:
        '''Gets a value indicating whether the page is visible in UI.'''
        raise NotImplementedError()
    
    @is_visible.setter
    def is_visible(self, value : bool) -> None:
        '''Sets a value indicating whether the page is visible in UI.'''
        raise NotImplementedError()
    
    @property
    def name(self) -> str:
        '''Gets the name of this :py:class:`groupdocs.watermark.contents.diagram.DiagramPage`.'''
        raise NotImplementedError()
    

class DiagramPageCollection:
    '''Represents a collection of pages in a Visio document.'''
    

class DiagramShape(groupdocs.watermark.search.ShapeSearchAdapter):
    '''Represents a drawing shape in a Visio document.'''
    
    @property
    def page(self) -> groupdocs.watermark.contents.diagram.DiagramPage:
        '''Gets the parent page of this :py:class:`groupdocs.watermark.contents.diagram.DiagramShape`.'''
        raise NotImplementedError()
    
    @property
    def width(self) -> float:
        '''Gets the width of this :py:class:`groupdocs.watermark.contents.diagram.DiagramShape` in points.'''
        raise NotImplementedError()
    
    @width.setter
    def width(self, value : float) -> None:
        '''Sets the width of this :py:class:`groupdocs.watermark.contents.diagram.DiagramShape` in points.'''
        raise NotImplementedError()
    
    @property
    def height(self) -> float:
        '''Gets the height of this :py:class:`groupdocs.watermark.contents.diagram.DiagramShape` in points.'''
        raise NotImplementedError()
    
    @height.setter
    def height(self, value : float) -> None:
        '''Sets the height of this :py:class:`groupdocs.watermark.contents.diagram.DiagramShape` in points.'''
        raise NotImplementedError()
    
    @property
    def x(self) -> float:
        '''Gets the horizontal offset of this :py:class:`groupdocs.watermark.contents.diagram.DiagramShape` from page left border in points.'''
        raise NotImplementedError()
    
    @x.setter
    def x(self, value : float) -> None:
        '''Sets the horizontal offset of this :py:class:`groupdocs.watermark.contents.diagram.DiagramShape` from page left border in points.'''
        raise NotImplementedError()
    
    @property
    def y(self) -> float:
        '''Gets the vertical offset of this :py:class:`groupdocs.watermark.contents.diagram.DiagramShape` from page bottom border in points.'''
        raise NotImplementedError()
    
    @y.setter
    def y(self, value : float) -> None:
        '''Sets the vertical offset of this :py:class:`groupdocs.watermark.contents.diagram.DiagramShape` from page bottom border in points.'''
        raise NotImplementedError()
    
    @property
    def rotate_angle(self) -> float:
        '''Gets the rotate angle of this :py:class:`groupdocs.watermark.contents.diagram.DiagramShape` in degrees.'''
        raise NotImplementedError()
    
    @rotate_angle.setter
    def rotate_angle(self, value : float) -> None:
        '''Sets the rotate angle of this :py:class:`groupdocs.watermark.contents.diagram.DiagramShape` in degrees.'''
        raise NotImplementedError()
    
    @property
    def text(self) -> str:
        '''Gets the text of this :py:class:`groupdocs.watermark.contents.diagram.DiagramShape`.'''
        raise NotImplementedError()
    
    @text.setter
    def text(self, value : str) -> None:
        '''Sets the text of this :py:class:`groupdocs.watermark.contents.diagram.DiagramShape`.'''
        raise NotImplementedError()
    
    @property
    def formatted_text_fragments(self) -> groupdocs.watermark.search.FormattedTextFragmentCollection:
        '''Gets the collection of formatted text fragments of this :py:class:`groupdocs.watermark.contents.diagram.DiagramShape`.'''
        raise NotImplementedError()
    
    @property
    def image(self) -> groupdocs.watermark.contents.diagram.DiagramWatermarkableImage:
        '''Gets the image of this :py:class:`groupdocs.watermark.contents.diagram.DiagramShape`.'''
        raise NotImplementedError()
    
    @image.setter
    def image(self, value : groupdocs.watermark.contents.diagram.DiagramWatermarkableImage) -> None:
        '''Sets the image of this :py:class:`groupdocs.watermark.contents.diagram.DiagramShape`.'''
        raise NotImplementedError()
    
    @property
    def id(self) -> int:
        '''Gets the identifier of this :py:class:`groupdocs.watermark.contents.diagram.DiagramShape`.'''
        raise NotImplementedError()
    
    @property
    def name(self) -> str:
        '''Gets the name of this :py:class:`groupdocs.watermark.contents.diagram.DiagramShape`.'''
        raise NotImplementedError()
    
    @property
    def hyperlinks(self) -> groupdocs.watermark.contents.diagram.DiagramHyperlinkCollection:
        '''Gets the collection of hyperlinks attached to this :py:class:`groupdocs.watermark.contents.diagram.DiagramShape`.'''
        raise NotImplementedError()
    

class DiagramShapeCollection:
    '''Represents a collection of drawing shapes in a Visio document.'''
    

class DiagramWatermarkableImage(groupdocs.watermark.contents.image.WatermarkableImage):
    '''Represents an image inside a Visio document.'''
    
    def __init__(self, image_data : List[int]) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.watermark.contents.diagram.DiagramWatermarkableImage` class using specified image data.
        
        :param image_data: The array of unsigned bytes from which to create the
        :py:class:`groupdocs.watermark.contents.diagram.DiagramWatermarkableImage`.'''
        raise NotImplementedError()
    
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
    
    def add(self, watermark : groupdocs.watermark.Watermark) -> None:
        '''Adds a watermark to this :py:class:`groupdocs.watermark.contents.image.WatermarkableImage`.
        This method assumes that watermark offset and size are measured in pixels (if they are assigned).
        
        :param watermark: The watermark to add to the image.'''
        raise NotImplementedError()
    
    def get_bytes(self) -> List[int]:
        '''Gets the image as byte array.
        
        :returns: The image data.'''
        raise NotImplementedError()
    
    @property
    def height(self) -> int:
        '''Gets the height of this :py:class:`groupdocs.watermark.contents.image.WatermarkableImage` in pixels.'''
        raise NotImplementedError()
    
    @property
    def width(self) -> int:
        '''Gets the width of this :py:class:`groupdocs.watermark.contents.image.WatermarkableImage` in pixels.'''
        raise NotImplementedError()
    

class DiagramWatermarkPlacementType:
    '''Specifies to what pages a watermark should be added.'''
    
    FOREGROUND_PAGES : DiagramWatermarkPlacementType
    '''A watermark should be added to foreground pages only.'''
    BACKGROUND_PAGES : DiagramWatermarkPlacementType
    '''A watermark should be added to background pages only.'''
    ALL_PAGES : DiagramWatermarkPlacementType
    '''A watermark should be added to all pages.'''
    SEPARATE_BACKGROUNDS : DiagramWatermarkPlacementType
    '''Separate background pages with a watermark should be created and assigned to all pages without background.'''
    DEFAULT : DiagramWatermarkPlacementType
    '''The same as :py:attr:`groupdocs.watermark.contents.diagram.DiagramWatermarkPlacementType.FOREGROUND_PAGES`.'''

