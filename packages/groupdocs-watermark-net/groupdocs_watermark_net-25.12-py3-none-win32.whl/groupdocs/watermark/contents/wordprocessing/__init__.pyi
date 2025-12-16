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

class WordProcessingContent(groupdocs.watermark.contents.Content):
    '''Class representing Word document (doc, docx etc) where watermark should be placed.'''
    
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
    
    def encrypt(self, password : str) -> None:
        '''Encrypts the document.
        
        :param password: The password that will be required to open the document.'''
        raise NotImplementedError()
    
    def decrypt(self) -> None:
        '''Decrypts the document.'''
        raise NotImplementedError()
    
    def protect(self, protection_type : groupdocs.watermark.contents.wordprocessing.WordProcessingProtectionType, password : str) -> None:
        '''Protects the document from changes and sets a protection password.
        
        :param protection_type: Specifies the protection type for the document.
        :param password: The password to protect the document with.'''
        raise NotImplementedError()
    
    def unprotect(self) -> None:
        '''Removes protection from the document regardless of the password.'''
        raise NotImplementedError()
    
    @property
    def sections(self) -> groupdocs.watermark.contents.wordprocessing.WordProcessingSectionCollection:
        '''Gets the collection of all sections of this :py:class:`groupdocs.watermark.contents.wordprocessing.WordProcessingContent`.'''
        raise NotImplementedError()
    
    @property
    def page_count(self) -> int:
        '''Gets the number of pages in the document.'''
        raise NotImplementedError()
    

class WordProcessingFormattedTextFragmentCollection(groupdocs.watermark.search.FormattedTextFragmentCollection):
    '''Represents a collection of formatted text fragments in a Word document.'''
    
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
    

class WordProcessingHeaderFooter(groupdocs.watermark.contents.ContentPart):
    '''Represents a header/footer in a Word document.'''
    
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
    def header_footer_type(self) -> groupdocs.watermark.contents.OfficeHeaderFooterType:
        '''Gets the type of this :py:class:`groupdocs.watermark.contents.wordprocessing.WordProcessingHeaderFooter`.'''
        raise NotImplementedError()
    
    @property
    def section(self) -> groupdocs.watermark.contents.wordprocessing.WordProcessingSection:
        '''Gets the parent section of this :py:class:`groupdocs.watermark.contents.wordprocessing.WordProcessingHeaderFooter`.'''
        raise NotImplementedError()
    
    @property
    def is_linked_to_previous(self) -> bool:
        '''Gets a value indicating whether this header/footer is linked to
        the corresponding header/footer in the previous section.'''
        raise NotImplementedError()
    
    @is_linked_to_previous.setter
    def is_linked_to_previous(self, value : bool) -> None:
        '''Sets a value indicating whether this header/footer is linked to
        the corresponding header/footer in the previous section.'''
        raise NotImplementedError()
    

class WordProcessingHeaderFooterCollection:
    '''Represents a collection of headers and footers in a Word document.'''
    
    def link_to_previous(self, is_link_to_previous : bool) -> None:
        '''Links or unlinks all headers and footers to the corresponding
        headers and footers in the previous section.
        
        :param is_link_to_previous: True to link the headers and footers to the previous section;
        false to unlink them.'''
        raise NotImplementedError()
    

class WordProcessingPageSetup:
    '''Represents printing page properties for a section of a Word document.'''
    
    @property
    def width(self) -> float:
        '''Gets the width of a printing page in points.'''
        raise NotImplementedError()
    
    @property
    def height(self) -> float:
        '''Gets the height of a printing page in points.'''
        raise NotImplementedError()
    
    @property
    def left_margin(self) -> float:
        '''Gets the size of the left margin in points.'''
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
    def different_first_page_header_footer(self) -> bool:
        '''Gets a value indicating whether a different header/footer is used for the first page.'''
        raise NotImplementedError()
    
    @different_first_page_header_footer.setter
    def different_first_page_header_footer(self, value : bool) -> None:
        '''Sets a value indicating whether a different header/footer is used for the first page.'''
        raise NotImplementedError()
    
    @property
    def odd_and_even_pages_header_footer(self) -> bool:
        '''Gets a value indicating whether different headers/footers are used for odd-numbered and even-numbered
        pages.
        Note, changing this property affects all sections in the content.'''
        raise NotImplementedError()
    
    @odd_and_even_pages_header_footer.setter
    def odd_and_even_pages_header_footer(self, value : bool) -> None:
        '''Sets a value indicating whether different headers/footers are used for odd-numbered and even-numbered
        pages.
        Note, changing this property affects all sections in the content.'''
        raise NotImplementedError()
    

class WordProcessingSection(groupdocs.watermark.contents.ContentPart):
    '''Represents a Word document section.'''
    
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
    def page_setup(self) -> groupdocs.watermark.contents.wordprocessing.WordProcessingPageSetup:
        '''Gets the printing page setup for this :py:class:`groupdocs.watermark.contents.wordprocessing.WordProcessingSection`.'''
        raise NotImplementedError()
    
    @property
    def headers_footers(self) -> groupdocs.watermark.contents.wordprocessing.WordProcessingHeaderFooterCollection:
        '''Gets the collection of all headers and footers of this :py:class:`groupdocs.watermark.contents.wordprocessing.WordProcessingSection`.'''
        raise NotImplementedError()
    
    @property
    def shapes(self) -> groupdocs.watermark.contents.wordprocessing.WordProcessingShapeCollection:
        '''Gets the collection of all shapes contained in this :py:class:`groupdocs.watermark.contents.wordprocessing.WordProcessingSection`.'''
        raise NotImplementedError()
    

class WordProcessingSectionCollection:
    '''Represents a collection of sections in a Word document.'''
    

class WordProcessingShape(groupdocs.watermark.search.ShapeSearchAdapter):
    '''Represents a drawing shape in a Word document.'''
    
    @property
    def section(self) -> groupdocs.watermark.contents.wordprocessing.WordProcessingSection:
        '''Gets the parent section of this :py:class:`groupdocs.watermark.contents.wordprocessing.WordProcessingShape`.'''
        raise NotImplementedError()
    
    @property
    def header_footer(self) -> groupdocs.watermark.contents.wordprocessing.WordProcessingHeaderFooter:
        '''Gets the parent header/footer of this :py:class:`groupdocs.watermark.contents.wordprocessing.WordProcessingShape` (if presents).'''
        raise NotImplementedError()
    
    @property
    def shape_type(self) -> groupdocs.watermark.contents.wordprocessing.WordProcessingShapeType:
        '''Gets the shape type.'''
        raise NotImplementedError()
    
    @property
    def is_word_art(self) -> bool:
        '''Gets a value indicating whether this :py:class:`groupdocs.watermark.contents.wordprocessing.WordProcessingShape` is a WordArt object.'''
        raise NotImplementedError()
    
    @property
    def alternative_text(self) -> str:
        '''Gets the descriptive (alternative) text associated with this :py:class:`groupdocs.watermark.contents.wordprocessing.WordProcessingShape`.'''
        raise NotImplementedError()
    
    @alternative_text.setter
    def alternative_text(self, value : str) -> None:
        '''Sets the descriptive (alternative) text associated with this :py:class:`groupdocs.watermark.contents.wordprocessing.WordProcessingShape`.'''
        raise NotImplementedError()
    
    @property
    def name(self) -> str:
        '''Gets the name of this :py:class:`groupdocs.watermark.contents.wordprocessing.WordProcessingShape`.'''
        raise NotImplementedError()
    
    @property
    def behind_text(self) -> bool:
        '''Gets a value indicating whether the shape is over or behind the text.'''
        raise NotImplementedError()
    
    @behind_text.setter
    def behind_text(self, value : bool) -> None:
        '''Sets a value indicating whether the shape is over or behind the text.'''
        raise NotImplementedError()
    
    @property
    def text(self) -> str:
        '''Gets the text of this :py:class:`groupdocs.watermark.contents.wordprocessing.WordProcessingShape`.'''
        raise NotImplementedError()
    
    @text.setter
    def text(self, value : str) -> None:
        '''Sets the text of this :py:class:`groupdocs.watermark.contents.wordprocessing.WordProcessingShape`.'''
        raise NotImplementedError()
    
    @property
    def formatted_text_fragments(self) -> groupdocs.watermark.search.FormattedTextFragmentCollection:
        '''Gets the collection of formatted text fragments of this :py:class:`groupdocs.watermark.contents.wordprocessing.WordProcessingShape`.'''
        raise NotImplementedError()
    
    @property
    def image(self) -> groupdocs.watermark.contents.wordprocessing.WordProcessingWatermarkableImage:
        '''Gets the image of this :py:class:`groupdocs.watermark.contents.wordprocessing.WordProcessingShape`.'''
        raise NotImplementedError()
    
    @image.setter
    def image(self, value : groupdocs.watermark.contents.wordprocessing.WordProcessingWatermarkableImage) -> None:
        '''Sets the image of this :py:class:`groupdocs.watermark.contents.wordprocessing.WordProcessingShape`.'''
        raise NotImplementedError()
    
    @property
    def horizontal_alignment(self) -> groupdocs.watermark.contents.wordprocessing.WordProcessingHorizontalAlignment:
        '''Gets a value specifying how the shape is positioned horizontally.'''
        raise NotImplementedError()
    
    @property
    def vertical_alignment(self) -> groupdocs.watermark.contents.wordprocessing.WordProcessingVerticalAlignment:
        '''Gets a value specifying how the shape is positioned vertically.'''
        raise NotImplementedError()
    
    @property
    def relative_horizontal_position(self) -> groupdocs.watermark.contents.wordprocessing.WordProcessingRelativeHorizontalPosition:
        '''Gets a value specifying to what the shape is positioned horizontally.'''
        raise NotImplementedError()
    
    @property
    def relative_vertical_position(self) -> groupdocs.watermark.contents.wordprocessing.WordProcessingRelativeVerticalPosition:
        '''Gets a value specifying to what the shape is positioned vertically.'''
        raise NotImplementedError()
    
    @property
    def hyperlink(self) -> str:
        '''Gets the hyperlink associated with this :py:class:`groupdocs.watermark.contents.wordprocessing.WordProcessingShape`.'''
        raise NotImplementedError()
    
    @hyperlink.setter
    def hyperlink(self, value : str) -> None:
        '''Sets the hyperlink associated with this :py:class:`groupdocs.watermark.contents.wordprocessing.WordProcessingShape`.'''
        raise NotImplementedError()
    
    @property
    def width(self) -> float:
        '''Gets the width of this :py:class:`groupdocs.watermark.contents.wordprocessing.WordProcessingShape` in points.'''
        raise NotImplementedError()
    
    @width.setter
    def width(self, value : float) -> None:
        '''Sets the width of this :py:class:`groupdocs.watermark.contents.wordprocessing.WordProcessingShape` in points.'''
        raise NotImplementedError()
    
    @property
    def height(self) -> float:
        '''Gets the height of this :py:class:`groupdocs.watermark.contents.wordprocessing.WordProcessingShape` in points.'''
        raise NotImplementedError()
    
    @height.setter
    def height(self, value : float) -> None:
        '''Sets the height of this :py:class:`groupdocs.watermark.contents.wordprocessing.WordProcessingShape` in points.'''
        raise NotImplementedError()
    
    @property
    def rotate_angle(self) -> float:
        '''Gets the rotate angle of this :py:class:`groupdocs.watermark.contents.wordprocessing.WordProcessingShape` in degrees.'''
        raise NotImplementedError()
    
    @rotate_angle.setter
    def rotate_angle(self, value : float) -> None:
        '''Sets the rotate angle of this :py:class:`groupdocs.watermark.contents.wordprocessing.WordProcessingShape` in degrees.'''
        raise NotImplementedError()
    
    @property
    def x(self) -> float:
        '''Gets the horizontal offset of this :py:class:`groupdocs.watermark.contents.wordprocessing.WordProcessingShape` from page left border in points.'''
        raise NotImplementedError()
    
    @x.setter
    def x(self, value : float) -> None:
        '''Sets the horizontal offset of this :py:class:`groupdocs.watermark.contents.wordprocessing.WordProcessingShape` from page left border in points.'''
        raise NotImplementedError()
    
    @property
    def y(self) -> float:
        '''Gets the vertical offset of this :py:class:`groupdocs.watermark.contents.wordprocessing.WordProcessingShape` from page top border in points.'''
        raise NotImplementedError()
    
    @y.setter
    def y(self, value : float) -> None:
        '''Sets the vertical offset of this :py:class:`groupdocs.watermark.contents.wordprocessing.WordProcessingShape` from page top border in points.'''
        raise NotImplementedError()
    

class WordProcessingShapeCollection:
    '''Represents a collection of shapes in a Word document.'''
    

class WordProcessingShapeFormattedTextFragmentCollection(WordProcessingFormattedTextFragmentCollection):
    '''Represents a collection of formatted text fragments in a Word document shape.'''
    
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
    

class WordProcessingTextFormattedTextFragment(groupdocs.watermark.search.FormattedTextFragment):
    '''Represents a fragment of formatted text in a Word document.'''
    
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
    

class WordProcessingTextFormattedTextFragmentCollection(WordProcessingFormattedTextFragmentCollection):
    '''Represents a collection of formatted text fragments in a Word document main text.'''
    
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
    

class WordProcessingWatermarkableImage(groupdocs.watermark.contents.image.WatermarkableImage):
    '''Represents an image inside a Word document.'''
    
    def __init__(self, image_data : List[int]) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.watermark.contents.wordprocessing.WordProcessingWatermarkableImage` class using specified image data.
        
        :param image_data: The array of unsigned bytes from which to create the :py:class:`groupdocs.watermark.contents.wordprocessing.WordProcessingWatermarkableImage`.'''
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
    

class WordProcessingWordArtShapeFormattedTextFragment(groupdocs.watermark.search.FormattedTextFragment):
    '''Represents a fragment of formatted text in a WordArt shape.'''
    
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
    

class WordProcessingWordArtShapeFormattedTextFragmentCollection(WordProcessingFormattedTextFragmentCollection):
    '''Represents a collection of formatted text fragments in a Word document WordArt shape.'''
    
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
    

class WordProcessingHorizontalAlignment:
    '''Specifies horizontal alignment of a floating object.'''
    
    NONE : WordProcessingHorizontalAlignment
    '''Object is explicitly positioned using its x-coordinate.'''
    LEFT : WordProcessingHorizontalAlignment
    '''Specifies that the object is left aligned to the horizontal alignment base.'''
    CENTER : WordProcessingHorizontalAlignment
    '''Specifies that the object is centered with respect to the horizontal alignment base.'''
    RIGHT : WordProcessingHorizontalAlignment
    '''Specifies that the object is right aligned to the horizontal alignment base.'''
    INSIDE : WordProcessingHorizontalAlignment
    '''Specifies that the object is inside of the horizontal alignment base.'''
    OUTSIDE : WordProcessingHorizontalAlignment
    '''Specifies that the object is outside of the horizontal alignment base.'''

class WordProcessingProtectionType:
    '''Represents protection type for a Word document.'''
    
    ALLOW_ONLY_REVISIONS : WordProcessingProtectionType
    '''User can only add revision marks to the document.'''
    ALLOW_ONLY_COMMENTS : WordProcessingProtectionType
    '''User can only modify comments in the document.'''
    ALLOW_ONLY_FORM_FIELDS : WordProcessingProtectionType
    '''User can only enter data in the form fields in the document.'''
    READ_ONLY : WordProcessingProtectionType
    '''No changes are allowed to the document.'''

class WordProcessingRelativeHorizontalPosition:
    '''Specifies to what the horizontal position of an object is relative.'''
    
    MARGIN : WordProcessingRelativeHorizontalPosition
    '''Specifies that the horizontal positioning is relative to the page margins.'''
    PAGE : WordProcessingRelativeHorizontalPosition
    '''The object is positioned relative to the left edge of the page.'''
    COLUMN : WordProcessingRelativeHorizontalPosition
    '''The object is positioned relative to the left side of the column.'''
    CHARACTER : WordProcessingRelativeHorizontalPosition
    '''The object is positioned relative to the left side of the paragraph.'''
    LEFT_MARGIN : WordProcessingRelativeHorizontalPosition
    '''Specifies that the horizontal positioning is relative to the left margin of the page.'''
    RIGHT_MARGIN : WordProcessingRelativeHorizontalPosition
    '''Specifies that the horizontal positioning is relative to the right margin of the page.'''
    INSIDE_MARGIN : WordProcessingRelativeHorizontalPosition
    '''Specifies that the horizontal positioning is relative to the inside margin
    of the current page (the left margin on odd pages, right on even pages).'''
    OUTSIDE_MARGIN : WordProcessingRelativeHorizontalPosition
    '''Specifies that the horizontal positioning is relative to the outside margin
    of the current page (the right margin on odd pages, left on even pages).'''

class WordProcessingRelativeVerticalPosition:
    '''Specifies to what the vertical position of an object is relative.'''
    
    MARGIN : WordProcessingRelativeVerticalPosition
    '''Specifies that the vertical positioning is relative to the page margins.'''
    PAGE : WordProcessingRelativeVerticalPosition
    '''The object is positioned relative to the top edge of the page.'''
    PARAGRAPH : WordProcessingRelativeVerticalPosition
    '''The object is positioned relative to the top of the paragraph that contains the anchor.'''
    LINE : WordProcessingRelativeVerticalPosition
    '''Undocumented feature.'''
    TOP_MARGIN : WordProcessingRelativeVerticalPosition
    '''Specifies that the vertical positioning is relative to the top margin of
    the current page.'''
    BOTTOM_MARGIN : WordProcessingRelativeVerticalPosition
    '''Specifies that the vertical positioning is relative to the bottom margin
    of the current page.'''
    INSIDE_MARGIN : WordProcessingRelativeVerticalPosition
    '''Specifies that the vertical positioning is relative to the inside margin
    of the current page.'''
    OUTSIDE_MARGIN : WordProcessingRelativeVerticalPosition
    '''Specifies that the vertical positioning is relative to the outside margin
    of the current page.'''

class WordProcessingShapeType:
    '''Represents the type of a shape in a Word document.'''
    
    MIN_VALUE : WordProcessingShapeType
    '''Built-in shape type.'''
    OLE_OBJECT : WordProcessingShapeType
    '''Built-in shape type.'''
    GROUP : WordProcessingShapeType
    '''Built-in shape type.'''
    NON_PRIMITIVE : WordProcessingShapeType
    '''Built-in shape type.'''
    RECTANGLE : WordProcessingShapeType
    '''Built-in shape type.'''
    ROUND_RECTANGLE : WordProcessingShapeType
    '''Built-in shape type.'''
    ELLIPSE : WordProcessingShapeType
    '''Built-in shape type.'''
    DIAMOND : WordProcessingShapeType
    '''Built-in shape type.'''
    TRIANGLE : WordProcessingShapeType
    '''Built-in shape type.'''
    RIGHT_TRIANGLE : WordProcessingShapeType
    '''Built-in shape type.'''
    PARALLELOGRAM : WordProcessingShapeType
    '''Built-in shape type.'''
    TRAPEZOID : WordProcessingShapeType
    '''Built-in shape type.'''
    HEXAGON : WordProcessingShapeType
    '''Built-in shape type.'''
    OCTAGON : WordProcessingShapeType
    '''Built-in shape type.'''
    PLUS : WordProcessingShapeType
    '''Built-in shape type.'''
    STAR : WordProcessingShapeType
    '''Built-in shape type.'''
    ARROW : WordProcessingShapeType
    '''Built-in shape type.'''
    THICK_ARROW : WordProcessingShapeType
    '''Built-in shape type.'''
    HOME_PLATE : WordProcessingShapeType
    '''Built-in shape type.'''
    CUBE : WordProcessingShapeType
    '''Built-in shape type.'''
    BALLOON : WordProcessingShapeType
    '''Built-in shape type.'''
    SEAL : WordProcessingShapeType
    '''Built-in shape type.'''
    ARC : WordProcessingShapeType
    '''Built-in shape type.'''
    LINE : WordProcessingShapeType
    '''Built-in shape type.'''
    PLAQUE : WordProcessingShapeType
    '''Built-in shape type.'''
    CAN : WordProcessingShapeType
    '''Built-in shape type.'''
    DONUT : WordProcessingShapeType
    '''Built-in shape type.'''
    TEXT_SIMPLE : WordProcessingShapeType
    '''Built-in shape type.'''
    TEXT_OCTAGON : WordProcessingShapeType
    '''Built-in shape type.'''
    TEXT_HEXAGON : WordProcessingShapeType
    '''Built-in shape type.'''
    TEXT_CURVE : WordProcessingShapeType
    '''Built-in shape type.'''
    TEXT_WAVE : WordProcessingShapeType
    '''Built-in shape type.'''
    TEXT_RING : WordProcessingShapeType
    '''Built-in shape type.'''
    TEXT_ON_CURVE : WordProcessingShapeType
    '''Built-in shape type.'''
    TEXT_ON_RING : WordProcessingShapeType
    '''Built-in shape type.'''
    STRAIGHT_CONNECTOR1 : WordProcessingShapeType
    '''Built-in shape type.'''
    BENT_CONNECTOR2 : WordProcessingShapeType
    '''Built-in shape type.'''
    BENT_CONNECTOR3 : WordProcessingShapeType
    '''Built-in shape type.'''
    BENT_CONNECTOR4 : WordProcessingShapeType
    '''Built-in shape type.'''
    BENT_CONNECTOR5 : WordProcessingShapeType
    '''Built-in shape type.'''
    CURVED_CONNECTOR2 : WordProcessingShapeType
    '''Built-in shape type.'''
    CURVED_CONNECTOR3 : WordProcessingShapeType
    '''Built-in shape type.'''
    CURVED_CONNECTOR4 : WordProcessingShapeType
    '''Built-in shape type.'''
    CURVED_CONNECTOR5 : WordProcessingShapeType
    '''Built-in shape type.'''
    CALLOUT1 : WordProcessingShapeType
    '''Built-in shape type.'''
    CALLOUT2 : WordProcessingShapeType
    '''Built-in shape type.'''
    CALLOUT3 : WordProcessingShapeType
    '''Built-in shape type.'''
    ACCENT_CALLOUT1 : WordProcessingShapeType
    '''Built-in shape type.'''
    ACCENT_CALLOUT2 : WordProcessingShapeType
    '''Built-in shape type.'''
    ACCENT_CALLOUT3 : WordProcessingShapeType
    '''Built-in shape type.'''
    BORDER_CALLOUT1 : WordProcessingShapeType
    '''Built-in shape type.'''
    BORDER_CALLOUT2 : WordProcessingShapeType
    '''Built-in shape type.'''
    BORDER_CALLOUT3 : WordProcessingShapeType
    '''Built-in shape type.'''
    ACCENT_BORDER_CALLOUT1 : WordProcessingShapeType
    '''Built-in shape type.'''
    ACCENT_BORDER_CALLOUT2 : WordProcessingShapeType
    '''Built-in shape type.'''
    ACCENT_BORDER_CALLOUT3 : WordProcessingShapeType
    '''Built-in shape type.'''
    RIBBON : WordProcessingShapeType
    '''Built-in shape type.'''
    RIBBON2 : WordProcessingShapeType
    '''Built-in shape type.'''
    CHEVRON : WordProcessingShapeType
    '''Built-in shape type.'''
    PENTAGON : WordProcessingShapeType
    '''Built-in shape type.'''
    NO_SMOKING : WordProcessingShapeType
    '''Built-in shape type.'''
    SEAL8 : WordProcessingShapeType
    '''Built-in shape type.'''
    SEAL16 : WordProcessingShapeType
    '''Built-in shape type.'''
    SEAL32 : WordProcessingShapeType
    '''Built-in shape type.'''
    WEDGE_RECT_CALLOUT : WordProcessingShapeType
    '''Built-in shape type.'''
    WEDGE_R_RECT_CALLOUT : WordProcessingShapeType
    '''Built-in shape type.'''
    WEDGE_ELLIPSE_CALLOUT : WordProcessingShapeType
    '''Built-in shape type.'''
    WAVE : WordProcessingShapeType
    '''Built-in shape type.'''
    FOLDED_CORNER : WordProcessingShapeType
    '''Built-in shape type.'''
    LEFT_ARROW : WordProcessingShapeType
    '''Built-in shape type.'''
    DOWN_ARROW : WordProcessingShapeType
    '''Built-in shape type.'''
    UP_ARROW : WordProcessingShapeType
    '''Built-in shape type.'''
    LEFT_RIGHT_ARROW : WordProcessingShapeType
    '''Built-in shape type.'''
    UP_DOWN_ARROW : WordProcessingShapeType
    '''Built-in shape type.'''
    IRREGULAR_SEAL1 : WordProcessingShapeType
    '''Built-in shape type.'''
    IRREGULAR_SEAL2 : WordProcessingShapeType
    '''Built-in shape type.'''
    LIGHTNING_BOLT : WordProcessingShapeType
    '''Built-in shape type.'''
    HEART : WordProcessingShapeType
    '''Built-in shape type.'''
    IMAGE : WordProcessingShapeType
    '''Built-in shape type.'''
    QUAD_ARROW : WordProcessingShapeType
    '''Built-in shape type.'''
    LEFT_ARROW_CALLOUT : WordProcessingShapeType
    '''Built-in shape type.'''
    RIGHT_ARROW_CALLOUT : WordProcessingShapeType
    '''Built-in shape type.'''
    UP_ARROW_CALLOUT : WordProcessingShapeType
    '''Built-in shape type.'''
    DOWN_ARROW_CALLOUT : WordProcessingShapeType
    '''Built-in shape type.'''
    LEFT_RIGHT_ARROW_CALLOUT : WordProcessingShapeType
    '''Built-in shape type.'''
    UP_DOWN_ARROW_CALLOUT : WordProcessingShapeType
    '''Built-in shape type.'''
    QUAD_ARROW_CALLOUT : WordProcessingShapeType
    '''Built-in shape type.'''
    BEVEL : WordProcessingShapeType
    '''Built-in shape type.'''
    LEFT_BRACKET : WordProcessingShapeType
    '''Built-in shape type.'''
    RIGHT_BRACKET : WordProcessingShapeType
    '''Built-in shape type.'''
    LEFT_BRACE : WordProcessingShapeType
    '''Built-in shape type.'''
    RIGHT_BRACE : WordProcessingShapeType
    '''Built-in shape type.'''
    LEFT_UP_ARROW : WordProcessingShapeType
    '''Built-in shape type.'''
    BENT_UP_ARROW : WordProcessingShapeType
    '''Built-in shape type.'''
    BENT_ARROW : WordProcessingShapeType
    '''Built-in shape type.'''
    SEAL24 : WordProcessingShapeType
    '''Built-in shape type.'''
    STRIPED_RIGHT_ARROW : WordProcessingShapeType
    '''Built-in shape type.'''
    NOTCHED_RIGHT_ARROW : WordProcessingShapeType
    '''Built-in shape type.'''
    BLOCK_ARC : WordProcessingShapeType
    '''Built-in shape type.'''
    SMILEY_FACE : WordProcessingShapeType
    '''Built-in shape type.'''
    VERTICAL_SCROLL : WordProcessingShapeType
    '''Built-in shape type.'''
    HORIZONTAL_SCROLL : WordProcessingShapeType
    '''Built-in shape type.'''
    CIRCULAR_ARROW : WordProcessingShapeType
    '''Built-in shape type.'''
    CUSTOM_SHAPE : WordProcessingShapeType
    '''Built-in shape type.'''
    UTURN_ARROW : WordProcessingShapeType
    '''Built-in shape type.'''
    CURVED_RIGHT_ARROW : WordProcessingShapeType
    '''Built-in shape type.'''
    CURVED_LEFT_ARROW : WordProcessingShapeType
    '''Built-in shape type.'''
    CURVED_UP_ARROW : WordProcessingShapeType
    '''Built-in shape type.'''
    CURVED_DOWN_ARROW : WordProcessingShapeType
    '''Built-in shape type.'''
    CLOUD_CALLOUT : WordProcessingShapeType
    '''Built-in shape type.'''
    ELLIPSE_RIBBON : WordProcessingShapeType
    '''Built-in shape type.'''
    ELLIPSE_RIBBON2 : WordProcessingShapeType
    '''Built-in shape type.'''
    FLOW_CHART_PROCESS : WordProcessingShapeType
    '''Built-in shape type.'''
    FLOW_CHART_DECISION : WordProcessingShapeType
    '''Built-in shape type.'''
    FLOW_CHART_INPUT_OUTPUT : WordProcessingShapeType
    '''Built-in shape type.'''
    FLOW_CHART_PREDEFINED_PROCESS : WordProcessingShapeType
    '''Built-in shape type.'''
    FLOW_CHART_INTERNAL_STORAGE : WordProcessingShapeType
    '''Built-in shape type.'''
    FLOW_CHART_DOCUMENT : WordProcessingShapeType
    '''Built-in shape type.'''
    FLOW_CHART_MULTIDOCUMENT : WordProcessingShapeType
    '''Built-in shape type.'''
    FLOW_CHART_TERMINATOR : WordProcessingShapeType
    '''Built-in shape type.'''
    FLOW_CHART_PREPARATION : WordProcessingShapeType
    '''Built-in shape type.'''
    FLOW_CHART_MANUAL_INPUT : WordProcessingShapeType
    '''Built-in shape type.'''
    FLOW_CHART_MANUAL_OPERATION : WordProcessingShapeType
    '''Built-in shape type.'''
    FLOW_CHART_CONNECTOR : WordProcessingShapeType
    '''Built-in shape type.'''
    FLOW_CHART_PUNCHED_CARD : WordProcessingShapeType
    '''Built-in shape type.'''
    FLOW_CHART_PUNCHED_TAPE : WordProcessingShapeType
    '''Built-in shape type.'''
    FLOW_CHART_SUMMING_JUNCTION : WordProcessingShapeType
    '''Built-in shape type.'''
    FLOW_CHART_OR : WordProcessingShapeType
    '''Built-in shape type.'''
    FLOW_CHART_COLLATE : WordProcessingShapeType
    '''Built-in shape type.'''
    FLOW_CHART_SORT : WordProcessingShapeType
    '''Built-in shape type.'''
    FLOW_CHART_EXTRACT : WordProcessingShapeType
    '''Built-in shape type.'''
    FLOW_CHART_MERGE : WordProcessingShapeType
    '''Built-in shape type.'''
    FLOW_CHART_OFFLINE_STORAGE : WordProcessingShapeType
    '''Built-in shape type.'''
    FLOW_CHART_ONLINE_STORAGE : WordProcessingShapeType
    '''Built-in shape type.'''
    FLOW_CHART_MAGNETIC_TAPE : WordProcessingShapeType
    '''Built-in shape type.'''
    FLOW_CHART_MAGNETIC_DISK : WordProcessingShapeType
    '''Built-in shape type.'''
    FLOW_CHART_MAGNETIC_DRUM : WordProcessingShapeType
    '''Built-in shape type.'''
    FLOW_CHART_DISPLAY : WordProcessingShapeType
    '''Built-in shape type.'''
    FLOW_CHART_DELAY : WordProcessingShapeType
    '''Built-in shape type.'''
    TEXT_PLAIN_TEXT : WordProcessingShapeType
    '''Built-in shape type.'''
    TEXT_STOP : WordProcessingShapeType
    '''Built-in shape type.'''
    TEXT_TRIANGLE : WordProcessingShapeType
    '''Built-in shape type.'''
    TEXT_TRIANGLE_INVERTED : WordProcessingShapeType
    '''Built-in shape type.'''
    TEXT_CHEVRON : WordProcessingShapeType
    '''Built-in shape type.'''
    TEXT_CHEVRON_INVERTED : WordProcessingShapeType
    '''Built-in shape type.'''
    TEXT_RING_INSIDE : WordProcessingShapeType
    '''Built-in shape type.'''
    TEXT_RING_OUTSIDE : WordProcessingShapeType
    '''Built-in shape type.'''
    TEXT_ARCH_UP_CURVE : WordProcessingShapeType
    '''Built-in shape type.'''
    TEXT_ARCH_DOWN_CURVE : WordProcessingShapeType
    '''Built-in shape type.'''
    TEXT_CIRCLE_CURVE : WordProcessingShapeType
    '''Built-in shape type.'''
    TEXT_BUTTON_CURVE : WordProcessingShapeType
    '''Built-in shape type.'''
    TEXT_ARCH_UP_POUR : WordProcessingShapeType
    '''Built-in shape type.'''
    TEXT_ARCH_DOWN_POUR : WordProcessingShapeType
    '''Built-in shape type.'''
    TEXT_CIRCLE_POUR : WordProcessingShapeType
    '''Built-in shape type.'''
    TEXT_BUTTON_POUR : WordProcessingShapeType
    '''Built-in shape type.'''
    TEXT_CURVE_UP : WordProcessingShapeType
    '''Built-in shape type.'''
    TEXT_CURVE_DOWN : WordProcessingShapeType
    '''Built-in shape type.'''
    TEXT_CASCADE_UP : WordProcessingShapeType
    '''Built-in shape type.'''
    TEXT_CASCADE_DOWN : WordProcessingShapeType
    '''Built-in shape type.'''
    TEXT_WAVE1 : WordProcessingShapeType
    '''Built-in shape type.'''
    TEXT_WAVE2 : WordProcessingShapeType
    '''Built-in shape type.'''
    TEXT_WAVE3 : WordProcessingShapeType
    '''Built-in shape type.'''
    TEXT_WAVE4 : WordProcessingShapeType
    '''Built-in shape type.'''
    TEXT_INFLATE : WordProcessingShapeType
    '''Built-in shape type.'''
    TEXT_DEFLATE : WordProcessingShapeType
    '''Built-in shape type.'''
    TEXT_INFLATE_BOTTOM : WordProcessingShapeType
    '''Built-in shape type.'''
    TEXT_DEFLATE_BOTTOM : WordProcessingShapeType
    '''Built-in shape type.'''
    TEXT_INFLATE_TOP : WordProcessingShapeType
    '''Built-in shape type.'''
    TEXT_DEFLATE_TOP : WordProcessingShapeType
    '''Built-in shape type.'''
    TEXT_DEFLATE_INFLATE : WordProcessingShapeType
    '''Built-in shape type.'''
    TEXT_DEFLATE_INFLATE_DEFLATE : WordProcessingShapeType
    '''Built-in shape type.'''
    TEXT_FADE_RIGHT : WordProcessingShapeType
    '''Built-in shape type.'''
    TEXT_FADE_LEFT : WordProcessingShapeType
    '''Built-in shape type.'''
    TEXT_FADE_UP : WordProcessingShapeType
    '''Built-in shape type.'''
    TEXT_FADE_DOWN : WordProcessingShapeType
    '''Built-in shape type.'''
    TEXT_SLANT_UP : WordProcessingShapeType
    '''Built-in shape type.'''
    TEXT_SLANT_DOWN : WordProcessingShapeType
    '''Built-in shape type.'''
    TEXT_CAN_UP : WordProcessingShapeType
    '''Built-in shape type.'''
    TEXT_CAN_DOWN : WordProcessingShapeType
    '''Built-in shape type.'''
    FLOW_CHART_ALTERNATE_PROCESS : WordProcessingShapeType
    '''Built-in shape type.'''
    FLOW_CHART_OFFPAGE_CONNECTOR : WordProcessingShapeType
    '''Built-in shape type.'''
    CALLOUT90 : WordProcessingShapeType
    '''Built-in shape type.'''
    ACCENT_CALLOUT90 : WordProcessingShapeType
    '''Built-in shape type.'''
    BORDER_CALLOUT90 : WordProcessingShapeType
    '''Built-in shape type.'''
    ACCENT_BORDER_CALLOUT90 : WordProcessingShapeType
    '''Built-in shape type.'''
    LEFT_RIGHT_UP_ARROW : WordProcessingShapeType
    '''Built-in shape type.'''
    SUN : WordProcessingShapeType
    '''Built-in shape type.'''
    MOON : WordProcessingShapeType
    '''Built-in shape type.'''
    BRACKET_PAIR : WordProcessingShapeType
    '''Built-in shape type.'''
    BRACE_PAIR : WordProcessingShapeType
    '''Built-in shape type.'''
    SEAL4 : WordProcessingShapeType
    '''Built-in shape type.'''
    DOUBLE_WAVE : WordProcessingShapeType
    '''Built-in shape type.'''
    ACTION_BUTTON_BLANK : WordProcessingShapeType
    '''Built-in shape type.'''
    ACTION_BUTTON_HOME : WordProcessingShapeType
    '''Built-in shape type.'''
    ACTION_BUTTON_HELP : WordProcessingShapeType
    '''Built-in shape type.'''
    ACTION_BUTTON_INFORMATION : WordProcessingShapeType
    '''Built-in shape type.'''
    ACTION_BUTTON_FORWARD_NEXT : WordProcessingShapeType
    '''Built-in shape type.'''
    ACTION_BUTTON_BACK_PREVIOUS : WordProcessingShapeType
    '''Built-in shape type.'''
    ACTION_BUTTON_END : WordProcessingShapeType
    '''Built-in shape type.'''
    ACTION_BUTTON_BEGINNING : WordProcessingShapeType
    '''Built-in shape type.'''
    ACTION_BUTTON_RETURN : WordProcessingShapeType
    '''Built-in shape type.'''
    ACTION_BUTTON_DOCUMENT : WordProcessingShapeType
    '''Built-in shape type.'''
    ACTION_BUTTON_SOUND : WordProcessingShapeType
    '''Built-in shape type.'''
    ACTION_BUTTON_MOVIE : WordProcessingShapeType
    '''Built-in shape type.'''
    OLE_CONTROL : WordProcessingShapeType
    '''Built-in shape type.'''
    TEXT_BOX : WordProcessingShapeType
    '''Built-in shape type.'''
    SINGLE_CORNER_SNIPPED : WordProcessingShapeType
    '''Built-in shape type.'''
    TOP_CORNERS_SNIPPED : WordProcessingShapeType
    '''Built-in shape type.'''
    DIAGONAL_CORNERS_SNIPPED : WordProcessingShapeType
    '''Built-in shape type.'''
    TOP_CORNERS_ONE_ROUNDED_ONE_SNIPPED : WordProcessingShapeType
    '''Built-in shape type.'''
    SINGLE_CORNER_ROUNDED : WordProcessingShapeType
    '''Built-in shape type.'''
    TOP_CORNERS_ROUNDED : WordProcessingShapeType
    '''Built-in shape type.'''
    DIAGONAL_CORNERS_ROUNDED : WordProcessingShapeType
    '''Built-in shape type.'''

class WordProcessingVerticalAlignment:
    '''Specifies vertical alignment of a floating object.'''
    
    INLINE : WordProcessingVerticalAlignment
    '''Not documented. Seems to be a possible value for floating paragraphs and tables.'''
    NONE : WordProcessingVerticalAlignment
    '''The object is explicitly positioned using its y-coordinate.'''
    TOP : WordProcessingVerticalAlignment
    '''Specifies that the object is at the top of the vertical alignment base.'''
    CENTER : WordProcessingVerticalAlignment
    '''Specifies that the object is centered with respect to the vertical alignment bas.'''
    BOTTOM : WordProcessingVerticalAlignment
    '''Specifies that the object is at the bottom of the vertical alignment base.'''
    INSIDE : WordProcessingVerticalAlignment
    '''Specifies that the object is inside of the horizontal alignment base.'''
    OUTSIDE : WordProcessingVerticalAlignment
    '''Specifies that the object is outside of the vertical alignment base.'''

