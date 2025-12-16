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

class SpreadsheetAttachment(groupdocs.watermark.common.Attachment):
    '''Represents a file attached to an Excel document.'''
    
    @overload
    def create_watermarker(self) -> groupdocs.watermark.Watermarker:
        '''Loads a content from the attached file.
        
        :returns: The instance of appropriate descendant of :py:class:`groupdocs.watermark.contents.Content` class.'''
        raise NotImplementedError()
    
    @overload
    def create_watermarker(self, load_options : groupdocs.watermark.options.LoadOptions) -> groupdocs.watermark.Watermarker:
        '''Loads a content from the attached file with the specified load options.
        
        :param load_options: Additional options to use when loading an attachment content.
        :returns: The instance of appropriate descendant of :py:class:`groupdocs.watermark.contents.Content` class.'''
        raise NotImplementedError()
    
    @overload
    def create_watermarker(self, load_options : groupdocs.watermark.options.LoadOptions, watermarker_settings : groupdocs.watermark.WatermarkerSettings) -> groupdocs.watermark.Watermarker:
        '''Loads a content from the attached file with the specified load options and settings.
        
        :param load_options: Additional options to use when loading an attachment content.
        :param watermarker_settings: Additional settings to use when working with loaded document.
        :returns: The instance of appropriate descendant of :py:class:`groupdocs.watermark.contents.Content` class.'''
        raise NotImplementedError()
    
    def get_document_info(self) -> groupdocs.watermark.common.IDocumentInfo:
        '''Gets the information about a document stored in the attached file.
        
        :returns: The :py:class:`groupdocs.watermark.common.IDocumentInfo` instance that contains detected information'''
        raise NotImplementedError()
    
    @property
    def content(self) -> List[int]:
        '''Gets the attached file content.'''
        raise NotImplementedError()
    
    @content.setter
    def content(self, value : List[int]) -> None:
        '''Sets the attached file content.'''
        raise NotImplementedError()
    
    @property
    def preview_image_content(self) -> List[int]:
        '''Gets the attached file preview image as a byte array.'''
        raise NotImplementedError()
    
    @preview_image_content.setter
    def preview_image_content(self, value : List[int]) -> None:
        '''Sets the attached file preview image as a byte array.'''
        raise NotImplementedError()
    
    @property
    def is_link(self) -> bool:
        '''Gets a value indicating whether the content contains only a link to the file.'''
        raise NotImplementedError()
    
    @property
    def source_full_name(self) -> str:
        '''Gets the full name of the attached file.'''
        raise NotImplementedError()
    
    @property
    def alternative_text(self) -> str:
        '''Gets the descriptive (alternative) text associated with the attached file.'''
        raise NotImplementedError()
    
    @alternative_text.setter
    def alternative_text(self, value : str) -> None:
        '''Sets the descriptive (alternative) text associated with the attached file.'''
        raise NotImplementedError()
    
    @property
    def x(self) -> float:
        '''Gets the horizontal offset of the attachment frame from worksheet left border in points.'''
        raise NotImplementedError()
    
    @x.setter
    def x(self, value : float) -> None:
        '''Sets the horizontal offset of the attachment frame from worksheet left border in points.'''
        raise NotImplementedError()
    
    @property
    def y(self) -> float:
        '''Gets the vertical offset of the attachment frame from worksheet top border in points.'''
        raise NotImplementedError()
    
    @y.setter
    def y(self, value : float) -> None:
        '''Sets the vertical offset of the attachment frame from worksheet top border in points.'''
        raise NotImplementedError()
    
    @property
    def width(self) -> float:
        '''Gets the width of the attachment frame in points.'''
        raise NotImplementedError()
    
    @width.setter
    def width(self, value : float) -> None:
        '''Sets the width of the attachment frame in points.'''
        raise NotImplementedError()
    
    @property
    def height(self) -> float:
        '''Gets the height of the attachment frame in points.'''
        raise NotImplementedError()
    
    @height.setter
    def height(self, value : float) -> None:
        '''Sets the height of the attachment frame in points.'''
        raise NotImplementedError()
    

class SpreadsheetAttachmentCollection:
    '''Represents a collection of attachments in an Excel document.'''
    
    def add_attachment(self, file_content : List[int], source_full_name : str, preview_image_content : List[int], x : float, y : float, width : float, height : float) -> None:
        '''Adds an attachment to the :py:class:`groupdocs.watermark.contents.spreadsheet.SpreadsheetWorksheet`.
        
        :param file_content: The content of the file to be attached.
        :param source_full_name: The full name of the attached file (The extension is used to
        determine appropriate application to open the file).
        :param preview_image_content: The attached file preview image as a byte array.
        :param x: The x-coordinate of the attachment frame (in points).
        :param y: The y-coordinate of the attachment frame (in points).
        :param width: The width of the attachment frame in points.
        :param height: The height of the attachment frame in points.'''
        raise NotImplementedError()
    
    def add_link(self, source_full_name : str, preview_image_content : List[int], x : float, y : float, width : float, height : float) -> None:
        '''Adds an attachment by a link (the document will not contain attached file content).
        
        :param source_full_name: The linked file path.
        :param preview_image_content: The attached file preview image as a byte array.
        :param x: The x-coordinate of the attachment frame (in points).
        :param y: The y-coordinate of the attachment frame (in points).
        :param width: The width of the attachment frame in points.
        :param height: The height of the attachment frame in points.'''
        raise NotImplementedError()
    

class SpreadsheetCellFormattedTextFragment(groupdocs.watermark.search.FormattedTextFragment):
    '''Represents a fragment of formatted text in Excel document cell.'''
    
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
    

class SpreadsheetCellFormattedTextFragmentCollection(groupdocs.watermark.search.FormattedTextFragmentCollection):
    '''Represents a collection of formatted text fragments in an Excel document cell.'''
    
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
    

class SpreadsheetChart(groupdocs.watermark.search.ITwoDObject):
    '''Represents a chart in an Excel document.'''
    
    @property
    def worksheet(self) -> groupdocs.watermark.contents.spreadsheet.SpreadsheetWorksheet:
        '''Gets the parent worksheet of this :py:class:`groupdocs.watermark.contents.spreadsheet.SpreadsheetChart`.'''
        raise NotImplementedError()
    
    @property
    def id(self) -> int:
        '''Gets the identifier of this :py:class:`groupdocs.watermark.contents.spreadsheet.SpreadsheetChart`.'''
        raise NotImplementedError()
    
    @property
    def image_fill_format(self) -> groupdocs.watermark.contents.spreadsheet.SpreadsheetImageFillFormat:
        '''Gets the image fill format settings of this :py:class:`groupdocs.watermark.contents.spreadsheet.SpreadsheetChart`.'''
        raise NotImplementedError()
    
    @property
    def name(self) -> str:
        '''Gets the name of this :py:class:`groupdocs.watermark.contents.spreadsheet.SpreadsheetChart`.'''
        raise NotImplementedError()
    
    @property
    def alternative_text(self) -> str:
        '''Gets the descriptive (alternative) text associated with this :py:class:`groupdocs.watermark.contents.spreadsheet.SpreadsheetChart`.'''
        raise NotImplementedError()
    
    @property
    def hyperlink(self) -> str:
        '''Gets the hyperlink associated with this :py:class:`groupdocs.watermark.contents.spreadsheet.SpreadsheetChart`.'''
        raise NotImplementedError()
    
    @hyperlink.setter
    def hyperlink(self, value : str) -> None:
        '''Sets the hyperlink associated with this :py:class:`groupdocs.watermark.contents.spreadsheet.SpreadsheetChart`.'''
        raise NotImplementedError()
    
    @property
    def x(self) -> float:
        '''Gets the horizontal offset of this :py:class:`groupdocs.watermark.contents.spreadsheet.SpreadsheetChart` from worksheet left border in points.'''
        raise NotImplementedError()
    
    @property
    def y(self) -> float:
        '''Gets the vertical offset of this :py:class:`groupdocs.watermark.contents.spreadsheet.SpreadsheetChart` from worksheet top border in points.'''
        raise NotImplementedError()
    
    @property
    def width(self) -> float:
        '''Gets the width of this :py:class:`groupdocs.watermark.contents.spreadsheet.SpreadsheetChart` in points.'''
        raise NotImplementedError()
    
    @property
    def height(self) -> float:
        '''Gets the height of this :py:class:`groupdocs.watermark.contents.spreadsheet.SpreadsheetChart` in points.'''
        raise NotImplementedError()
    

class SpreadsheetChartCollection:
    '''Represents a collection of charts in an Excel document.'''
    

class SpreadsheetContent(groupdocs.watermark.contents.Content):
    '''Represents an Excel document where a watermark can be placed.'''
    
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
        '''Encrypts the content.
        
        :param password: The password that will be required to open the document.'''
        raise NotImplementedError()
    
    def decrypt(self) -> None:
        '''Decrypts the document.'''
        raise NotImplementedError()
    
    @property
    def worksheets(self) -> groupdocs.watermark.contents.spreadsheet.SpreadsheetWorksheetCollection:
        '''Gets the collection of all worksheets of this :py:class:`groupdocs.watermark.contents.spreadsheet.SpreadsheetContent`.'''
        raise NotImplementedError()
    

class SpreadsheetHeaderFooter:
    '''Represents a header/footer in an Excel document.'''
    
    @property
    def header_footer_type(self) -> groupdocs.watermark.contents.OfficeHeaderFooterType:
        '''Gets the type of this :py:class:`groupdocs.watermark.contents.spreadsheet.SpreadsheetHeaderFooter`.'''
        raise NotImplementedError()
    
    @property
    def sections(self) -> groupdocs.watermark.contents.spreadsheet.SpreadsheetHeaderFooterSectionCollection:
        '''Gets the collection of header/footer sections.'''
        raise NotImplementedError()
    
    @property
    def worksheet(self) -> groupdocs.watermark.contents.spreadsheet.SpreadsheetWorksheet:
        '''Gets the parent worksheet of this :py:class:`groupdocs.watermark.contents.spreadsheet.SpreadsheetHeaderFooter`.'''
        raise NotImplementedError()
    

class SpreadsheetHeaderFooterCollection:
    '''Represents a collection of headers and footers in an Excel document.'''
    

class SpreadsheetHeaderFooterSection:
    '''Represents a header/footer section in an Excel document.'''
    
    @property
    def section_type(self) -> groupdocs.watermark.contents.spreadsheet.SpreadsheetHeaderFooterSectionType:
        '''Gets the type of this :py:class:`groupdocs.watermark.contents.spreadsheet.SpreadsheetHeaderFooterSection`.'''
        raise NotImplementedError()
    
    @property
    def header_footer(self) -> groupdocs.watermark.contents.spreadsheet.SpreadsheetHeaderFooter:
        '''Gets the parent header/footer of this :py:class:`groupdocs.watermark.contents.spreadsheet.SpreadsheetHeaderFooterSection`.'''
        raise NotImplementedError()
    
    @property
    def script(self) -> str:
        '''Gets the script formatting of this :py:class:`groupdocs.watermark.contents.spreadsheet.SpreadsheetHeaderFooterSection`.'''
        raise NotImplementedError()
    
    @script.setter
    def script(self, value : str) -> None:
        '''Sets the script formatting of this :py:class:`groupdocs.watermark.contents.spreadsheet.SpreadsheetHeaderFooterSection`.'''
        raise NotImplementedError()
    
    @property
    def image(self) -> groupdocs.watermark.contents.spreadsheet.SpreadsheetWatermarkableImage:
        '''Gets the image of this :py:class:`groupdocs.watermark.contents.spreadsheet.SpreadsheetHeaderFooterSection`.'''
        raise NotImplementedError()
    
    @image.setter
    def image(self, value : groupdocs.watermark.contents.spreadsheet.SpreadsheetWatermarkableImage) -> None:
        '''Sets the image of this :py:class:`groupdocs.watermark.contents.spreadsheet.SpreadsheetHeaderFooterSection`.'''
        raise NotImplementedError()
    

class SpreadsheetHeaderFooterSectionCollection:
    '''Represents a collection of header/footer sections.'''
    

class SpreadsheetImageFillFormat:
    '''Represents the image fill format settings in an Excel document.'''
    
    @property
    def tile_as_texture(self) -> bool:
        '''Gets a value indicating whether the image is tiled across the background.'''
        raise NotImplementedError()
    
    @tile_as_texture.setter
    def tile_as_texture(self, value : bool) -> None:
        '''Sets a value indicating whether the image is tiled across the background.'''
        raise NotImplementedError()
    
    @property
    def transparency(self) -> float:
        '''Gets the transparency of the background image as a value from 0.0 (opaque)
        through 1.0 (fully transparent).'''
        raise NotImplementedError()
    
    @transparency.setter
    def transparency(self, value : float) -> None:
        '''Sets the transparency of the background image as a value from 0.0 (opaque)
        through 1.0 (fully transparent).'''
        raise NotImplementedError()
    
    @property
    def background_image(self) -> groupdocs.watermark.contents.spreadsheet.SpreadsheetWatermarkableImage:
        '''Gets the background image.'''
        raise NotImplementedError()
    
    @background_image.setter
    def background_image(self, value : groupdocs.watermark.contents.spreadsheet.SpreadsheetWatermarkableImage) -> None:
        '''Sets the background image.'''
        raise NotImplementedError()
    

class SpreadsheetPageSetup:
    '''Represents printing page properties for a worksheet.'''
    
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
    def right_margin(self) -> float:
        '''Gets the size of the right margin in points.'''
        raise NotImplementedError()
    
    @property
    def top_margin(self) -> float:
        '''Gets the size of the top margin in points.'''
        raise NotImplementedError()
    
    @property
    def bottom_margin(self) -> float:
        '''Gets the size of the bottom margin in points.'''
        raise NotImplementedError()
    

class SpreadsheetShape(groupdocs.watermark.search.ShapeSearchAdapter):
    '''Represents a drawing shape in an Excel document.'''
    
    @property
    def worksheet(self) -> groupdocs.watermark.contents.spreadsheet.SpreadsheetWorksheet:
        '''Gets the parent worksheet of this :py:class:`groupdocs.watermark.contents.spreadsheet.SpreadsheetShape`.'''
        raise NotImplementedError()
    
    @property
    def auto_shape_type(self) -> groupdocs.watermark.contents.spreadsheet.SpreadsheetAutoShapeType:
        '''Gets the auto shape type.'''
        raise NotImplementedError()
    
    @property
    def mso_drawing_type(self) -> groupdocs.watermark.contents.spreadsheet.SpreadsheetMsoDrawingType:
        '''Gets the mso drawing type.'''
        raise NotImplementedError()
    
    @property
    def text(self) -> str:
        '''Gets the text of this :py:class:`groupdocs.watermark.contents.spreadsheet.SpreadsheetShape`.'''
        raise NotImplementedError()
    
    @text.setter
    def text(self, value : str) -> None:
        '''Sets the text of this :py:class:`groupdocs.watermark.contents.spreadsheet.SpreadsheetShape`.'''
        raise NotImplementedError()
    
    @property
    def formatted_text_fragments(self) -> groupdocs.watermark.search.FormattedTextFragmentCollection:
        '''Gets the collection of formatted text fragments of this :py:class:`groupdocs.watermark.contents.spreadsheet.SpreadsheetShape`.'''
        raise NotImplementedError()
    
    @property
    def image(self) -> groupdocs.watermark.contents.spreadsheet.SpreadsheetWatermarkableImage:
        '''Gets the image of this :py:class:`groupdocs.watermark.contents.spreadsheet.SpreadsheetShape`.'''
        raise NotImplementedError()
    
    @image.setter
    def image(self, value : groupdocs.watermark.contents.spreadsheet.SpreadsheetWatermarkableImage) -> None:
        '''Sets the image of this :py:class:`groupdocs.watermark.contents.spreadsheet.SpreadsheetShape`.'''
        raise NotImplementedError()
    
    @property
    def image_fill_format(self) -> groupdocs.watermark.contents.spreadsheet.SpreadsheetImageFillFormat:
        '''Gets the image fill format settings of this :py:class:`groupdocs.watermark.contents.spreadsheet.SpreadsheetShape`.'''
        raise NotImplementedError()
    
    @property
    def id(self) -> int:
        '''Gets the identifier of this :py:class:`groupdocs.watermark.contents.spreadsheet.SpreadsheetShape`.'''
        raise NotImplementedError()
    
    @property
    def alternative_text(self) -> str:
        '''Gets the descriptive (alternative) text associated with this :py:class:`groupdocs.watermark.contents.spreadsheet.SpreadsheetShape`.'''
        raise NotImplementedError()
    
    @alternative_text.setter
    def alternative_text(self, value : str) -> None:
        '''Sets the descriptive (alternative) text associated with this :py:class:`groupdocs.watermark.contents.spreadsheet.SpreadsheetShape`.'''
        raise NotImplementedError()
    
    @property
    def is_word_art(self) -> bool:
        '''Gets a value indicating whether this :py:class:`groupdocs.watermark.contents.spreadsheet.SpreadsheetShape` is a WordArt object.'''
        raise NotImplementedError()
    
    @property
    def name(self) -> str:
        '''Gets the name of this :py:class:`groupdocs.watermark.contents.spreadsheet.SpreadsheetShape`.'''
        raise NotImplementedError()
    
    @property
    def hyperlink(self) -> str:
        '''Gets the hyperlink associated with this :py:class:`groupdocs.watermark.contents.spreadsheet.SpreadsheetShape`.'''
        raise NotImplementedError()
    
    @hyperlink.setter
    def hyperlink(self, value : str) -> None:
        '''Sets the hyperlink associated with this :py:class:`groupdocs.watermark.contents.spreadsheet.SpreadsheetShape`.'''
        raise NotImplementedError()
    
    @property
    def x(self) -> float:
        '''Gets the horizontal offset of this :py:class:`groupdocs.watermark.contents.spreadsheet.SpreadsheetShape` from worksheet left border in points.'''
        raise NotImplementedError()
    
    @x.setter
    def x(self, value : float) -> None:
        '''Sets the horizontal offset of this :py:class:`groupdocs.watermark.contents.spreadsheet.SpreadsheetShape` from worksheet left border in points.'''
        raise NotImplementedError()
    
    @property
    def y(self) -> float:
        '''Gets the vertical offset of this :py:class:`groupdocs.watermark.contents.spreadsheet.SpreadsheetShape` from worksheet top border in points.'''
        raise NotImplementedError()
    
    @y.setter
    def y(self, value : float) -> None:
        '''Sets the vertical offset of this :py:class:`groupdocs.watermark.contents.spreadsheet.SpreadsheetShape` from worksheet top border in points.'''
        raise NotImplementedError()
    
    @property
    def width(self) -> float:
        '''Gets the width of this :py:class:`groupdocs.watermark.contents.spreadsheet.SpreadsheetShape` in points.'''
        raise NotImplementedError()
    
    @width.setter
    def width(self, value : float) -> None:
        '''Sets the width of this :py:class:`groupdocs.watermark.contents.spreadsheet.SpreadsheetShape` in points.'''
        raise NotImplementedError()
    
    @property
    def height(self) -> float:
        '''Gets the height of this :py:class:`groupdocs.watermark.contents.spreadsheet.SpreadsheetShape` in points.'''
        raise NotImplementedError()
    
    @height.setter
    def height(self, value : float) -> None:
        '''Sets the height of this :py:class:`groupdocs.watermark.contents.spreadsheet.SpreadsheetShape` in points.'''
        raise NotImplementedError()
    
    @property
    def rotate_angle(self) -> float:
        '''Gets the rotate angle of this :py:class:`groupdocs.watermark.contents.spreadsheet.SpreadsheetShape` in degrees.'''
        raise NotImplementedError()
    
    @rotate_angle.setter
    def rotate_angle(self, value : float) -> None:
        '''Sets the rotate angle of this :py:class:`groupdocs.watermark.contents.spreadsheet.SpreadsheetShape` in degrees.'''
        raise NotImplementedError()
    

class SpreadsheetShapeCollection:
    '''Represents a collection of drawing shapes in an Excel document.'''
    

class SpreadsheetShapeFormattedTextFragment(groupdocs.watermark.search.FormattedTextFragment):
    '''Represents a fragment of formatted text in Excel document shape.'''
    
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
    

class SpreadsheetShapeFormattedTextFragmentCollection(groupdocs.watermark.search.FormattedTextFragmentCollection):
    '''Represents a collection of formatted text fragments in an Excel document text shape.'''
    
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
    

class SpreadsheetTextEffectFormattedTextFragment(groupdocs.watermark.search.FormattedTextFragment):
    '''Represents a fragment of formatted text in Excel document WordArt shape.'''
    
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
    

class SpreadsheetTextEffectFormattedTextFragmentCollection(groupdocs.watermark.search.FormattedTextFragmentCollection):
    '''Represents a collection of formatted text fragments in an Excel document WordArt shape.'''
    
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
    

class SpreadsheetWatermarkableImage(groupdocs.watermark.contents.image.WatermarkableImage):
    '''Represents an image inside an Excel document.'''
    
    def __init__(self, image_data : List[int]) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.watermark.contents.spreadsheet.SpreadsheetWatermarkableImage` class
        using specified image data.
        
        :param image_data: The array of unsigned bytes from which to create the :py:class:`groupdocs.watermark.contents.spreadsheet.SpreadsheetWatermarkableImage`.'''
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
    

class SpreadsheetWorksheet(groupdocs.watermark.contents.ContentPart):
    '''Represents an Excel document worksheet.'''
    
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
    
    def get_column_width(self, column : int) -> float:
        '''Gets the width of the specified column in points.
        
        :param column: The column index.
        :returns: The width of the column in points.'''
        raise NotImplementedError()
    
    def get_column_width_px(self, column : int) -> int:
        '''Gets the width of the specified column in pixels.
        
        :param column: The column index.
        :returns: The width of the column in pixels.'''
        raise NotImplementedError()
    
    def get_row_height(self, row : int) -> float:
        '''Gets the height of the specified row in points.
        
        :param row: The row index.
        :returns: The height of the row in points.'''
        raise NotImplementedError()
    
    def get_row_height_px(self, row : int) -> int:
        '''Gets the height of the specified row in pixels.
        
        :param row: The row index.
        :returns: The height of the row in pixels.'''
        raise NotImplementedError()
    
    @property
    def page_setup(self) -> groupdocs.watermark.contents.spreadsheet.SpreadsheetPageSetup:
        '''Gets the printing page setup for this :py:class:`groupdocs.watermark.contents.spreadsheet.SpreadsheetWorksheet`.'''
        raise NotImplementedError()
    
    @property
    def content_area_width(self) -> float:
        '''Gets the width of the content area in points.'''
        raise NotImplementedError()
    
    @property
    def content_area_width_px(self) -> int:
        '''Gets the width of the content area in pixels.'''
        raise NotImplementedError()
    
    @property
    def content_area_height(self) -> float:
        '''Gets the height of the content area in points.'''
        raise NotImplementedError()
    
    @property
    def content_area_height_px(self) -> int:
        '''Gets the height of the content area in pixels.'''
        raise NotImplementedError()
    
    @property
    def shapes(self) -> groupdocs.watermark.contents.spreadsheet.SpreadsheetShapeCollection:
        '''Gets the collection of all shapes of this :py:class:`groupdocs.watermark.contents.spreadsheet.SpreadsheetWorksheet`.'''
        raise NotImplementedError()
    
    @property
    def attachments(self) -> groupdocs.watermark.contents.spreadsheet.SpreadsheetAttachmentCollection:
        '''Gets the collection of all attachments of this :py:class:`groupdocs.watermark.contents.spreadsheet.SpreadsheetWorksheet`.'''
        raise NotImplementedError()
    
    @property
    def charts(self) -> groupdocs.watermark.contents.spreadsheet.SpreadsheetChartCollection:
        '''Gets the collection of all charts of this :py:class:`groupdocs.watermark.contents.spreadsheet.SpreadsheetWorksheet`.'''
        raise NotImplementedError()
    
    @property
    def background_image(self) -> groupdocs.watermark.contents.spreadsheet.SpreadsheetWatermarkableImage:
        '''Gets the background image of this :py:class:`groupdocs.watermark.contents.spreadsheet.SpreadsheetWorksheet`.'''
        raise NotImplementedError()
    
    @background_image.setter
    def background_image(self, value : groupdocs.watermark.contents.spreadsheet.SpreadsheetWatermarkableImage) -> None:
        '''Sets the background image of this :py:class:`groupdocs.watermark.contents.spreadsheet.SpreadsheetWorksheet`.'''
        raise NotImplementedError()
    
    @property
    def headers_footers(self) -> groupdocs.watermark.contents.spreadsheet.SpreadsheetHeaderFooterCollection:
        '''Gets the collection of worksheet headers and footers.'''
        raise NotImplementedError()
    

class SpreadsheetWorksheetCollection:
    '''Represents a collection of worksheets in an Excel document.'''
    

class SpreadsheetAutoShapeType:
    '''Represents auto shape type.'''
    
    NOT_PRIMITIVE : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    RECTANGLE : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    ROUNDED_RECTANGLE : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    OVAL : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    DIAMOND : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    ISOSCELES_TRIANGLE : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    RIGHT_TRIANGLE : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    PARALLELOGRAM : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    TRAPEZOID : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    HEXAGON : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    OCTAGON : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    CROSS : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    STAR5 : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    RIGHT_ARROW : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    HOME_PLATE : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    CUBE : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    BALLOON : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    SEAL : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    ARC : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    LINE : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    PLAQUE : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    CAN : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    DONUT : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    TEXT_SIMPLE : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    TEXT_OCTAGON : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    TEXT_HEXAGON : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    TEXT_CURVE : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    TEXT_WAVE : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    TEXT_RING : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    TEXT_ON_CURVE : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    TEXT_ON_RING : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    STRAIGHT_CONNECTOR : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    BENT_CONNECTOR2 : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    ELBOW_CONNECTOR : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    BENT_CONNECTOR4 : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    BENT_CONNECTOR5 : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    CURVED_CONNECTOR2 : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    CURVED_CONNECTOR : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    CURVED_CONNECTOR4 : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    CURVED_CONNECTOR5 : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    LINE_CALLOUT_NO_BORDER2 : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    LINE_CALLOUT_NO_BORDER3 : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    LINE_CALLOUT_NO_BORDER4 : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    LINE_CALLOUT_WITH_ACCENT_BAR2 : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    LINE_CALLOUT_WITH_ACCENT_BAR3 : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    LINE_CALLOUT_WITH_ACCENT_BAR4 : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    LINE_CALLOUT_WITH_BORDER2 : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    LINE_CALLOUT_WITH_BORDER3 : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    LINE_CALLOUT_WITH_BORDER4 : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    LINE_CALLOUT_WITH_BORDER_AND_ACCENT_BAR2 : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    LINE_CALLOUT_WITH_BORDER_AND_ACCENT_BAR3 : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    LINE_CALLOUT_WITH_BORDER_AND_ACCENT_BAR4 : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    DOWN_RIBBON : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    UP_RIBBON : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    CHEVRON : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    REGULAR_PENTAGON : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    NO_SYMBOL : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    STAR8 : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    STAR16 : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    STAR32 : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    RECTANGULAR_CALLOUT : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    ROUNDED_RECTANGULAR_CALLOUT : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    OVAL_CALLOUT : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    WAVE : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    FOLDED_CORNER : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    LEFT_ARROW : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    DOWN_ARROW : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    UP_ARROW : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    LEFT_RIGHT_ARROW : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    UP_DOWN_ARROW : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    EXPLOSION1 : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    EXPLOSION2 : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    LIGHTNING_BOLT : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    HEART : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    PICTURE_FRAME : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    QUAD_ARROW : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    LEFT_ARROW_CALLOUT : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    RIGHT_ARROW_CALLOUT : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    UP_ARROW_CALLOUT : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    DOWN_ARROW_CALLOUT : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    LEFT_RIGHT_ARROW_CALLOUT : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    UP_DOWN_ARROW_CALLOUT : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    QUAD_ARROW_CALLOUT : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    BEVEL : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    LEFT_BRACKET : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    RIGHT_BRACKET : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    LEFT_BRACE : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    RIGHT_BRACE : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    LEFT_UP_ARROW : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    BENT_UP_ARROW : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    BENT_ARROW : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    STAR24 : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    STRIPED_RIGHT_ARROW : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    NOTCHED_RIGHT_ARROW : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    BLOCK_ARC : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    SMILEY_FACE : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    VERTICAL_SCROLL : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    HORIZONTAL_SCROLL : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    CIRCULAR_ARROW : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    NOTCHED_CIRCULAR_ARROW : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    U_TURN_ARROW : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    CURVED_RIGHT_ARROW : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    CURVED_LEFT_ARROW : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    CURVED_UP_ARROW : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    CURVED_DOWN_ARROW : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    CLOUD_CALLOUT : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    CURVED_DOWN_RIBBON : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    CURVED_UP_RIBBON : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    FLOW_CHART_PROCESS : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    FLOW_CHART_DECISION : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    FLOW_CHART_DATA : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    FLOW_CHART_PREDEFINED_PROCESS : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    FLOW_CHART_INTERNAL_STORAGE : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    FLOW_CHART_DOCUMENT : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    FLOW_CHART_MULTIDOCUMENT : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    FLOW_CHART_TERMINATOR : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    FLOW_CHART_PREPARATION : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    FLOW_CHART_MANUAL_INPUT : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    FLOW_CHART_MANUAL_OPERATION : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    FLOW_CHART_CONNECTOR : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    FLOW_CHART_CARD : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    FLOW_CHART_PUNCHED_TAPE : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    FLOW_CHART_SUMMING_JUNCTION : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    FLOW_CHART_OR : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    FLOW_CHART_COLLATE : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    FLOW_CHART_SORT : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    FLOW_CHART_EXTRACT : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    FLOW_CHART_MERGE : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    FLOW_CHART_OFFLINE_STORAGE : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    FLOW_CHART_STORED_DATA : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    FLOW_CHART_SEQUENTIAL_ACCESS_STORAGE : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    FLOW_CHART_MAGNETIC_DISK : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    FLOW_CHART_DIRECT_ACCESS_STORAGE : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    FLOW_CHART_DISPLAY : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    FLOW_CHART_DELAY : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    TEXT_PLAIN_TEXT : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    TEXT_STOP : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    TEXT_TRIANGLE : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    TEXT_TRIANGLE_INVERTED : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    TEXT_CHEVRON : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    TEXT_CHEVRON_INVERTED : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    TEXT_RING_INSIDE : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    TEXT_RING_OUTSIDE : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    TEXT_ARCH_UP_CURVE : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    TEXT_ARCH_DOWN_CURVE : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    TEXT_CIRCLE_CURVE : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    TEXT_BUTTON_CURVE : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    TEXT_ARCH_UP_POUR : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    TEXT_ARCH_DOWN_POUR : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    TEXT_CIRCLE_POUR : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    TEXT_BUTTON_POUR : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    TEXT_CURVE_UP : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    TEXT_CURVE_DOWN : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    TEXT_CASCADE_UP : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    TEXT_CASCADE_DOWN : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    TEXT_WAVE1 : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    TEXT_WAVE2 : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    TEXT_DOUBLE_WAVE1 : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    TEXT_DOUBLE_WAVE2 : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    TEXT_INFLATE : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    TEXT_DEFLATE : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    TEXT_INFLATE_BOTTOM : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    TEXT_DEFLATE_BOTTOM : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    TEXT_INFLATE_TOP : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    TEXT_DEFLATE_TOP : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    TEXT_DEFLATE_INFLATE : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    TEXT_DEFLATE_INFLATE_DEFLATE : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    TEXT_FADE_RIGHT : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    TEXT_FADE_LEFT : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    TEXT_FADE_UP : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    TEXT_FADE_DOWN : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    TEXT_SLANT_UP : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    TEXT_SLANT_DOWN : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    TEXT_CAN_UP : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    TEXT_CAN_DOWN : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    FLOW_CHART_ALTERNATE_PROCESS : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    FLOW_CHART_OFFPAGE_CONNECTOR : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    LINE_CALLOUT_NO_BORDER1 : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    LINE_CALLOUT_WITH_ACCENT_BAR1 : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    LINE_CALLOUT_WITH_BORDER1 : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    LINE_CALLOUT_WITH_BORDER_AND_ACCENT_BAR1 : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    LEFT_RIGHT_UP_ARROW : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    SUN : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    MOON : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    DOUBLE_BRACKET : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    DOUBLE_BRACE : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    STAR4 : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    DOUBLE_WAVE : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    BLANK_ACTION_BUTTON : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    HOME_ACTION_BUTTON : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    HELP_ACTION_BUTTON : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    INFORMATION_ACTION_BUTTON : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    FORWARD_NEXT_ACTION_BUTTON : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    BACK_PREVIOUS_ACTION_BUTTON : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    END_ACTION_BUTTON : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    BEGINNING_ACTION_BUTTON : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    RETURN_ACTION_BUTTON : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    DOCUMENT_ACTION_BUTTON : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    SOUND_ACTION_BUTTON : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    MOVIE_ACTION_BUTTON : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    HOST_CONTROL : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    TEXT_BOX : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    HEPTAGON : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    DECAGON : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    DODECAGON : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    STAR6 : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    STAR7 : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    STAR10 : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    STAR12 : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    ROUND_SINGLE_CORNER_RECTANGLE : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    ROUND_SAME_SIDE_CORNER_RECTANGLE : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    ROUND_DIAGONAL_CORNER_RECTANGLE : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    SNIP_ROUND_SINGLE_CORNER_RECTANGLE : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    SNIP_SINGLE_CORNER_RECTANGLE : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    SNIP_SAME_SIDE_CORNER_RECTANGLE : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    SNIP_DIAGONAL_CORNER_RECTANGLE : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    TEARDROP : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    PIE : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    HALF_FRAME : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    L_SHAPE : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    DIAGONAL_STRIPE : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    CHORD : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    CLOUD : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    MATH_PLUS : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    MATH_MINUS : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    MATH_MULTIPLY : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    MATH_DIVIDE : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    MATH_EQUAL : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    MATH_NOT_EQUAL : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    LINE_INV : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    NON_ISOSCELES_TRAPEZOID : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    PIE_WEDGE : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    LEFT_CIRCULAR_ARROW : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    LEFT_RIGHT_CIRCULAR_ARROW : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    SWOOSH_ARROW : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    LEFT_RIGHT_RIBBON : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    TEXT_NO_SHAPE : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    GEAR6 : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    GEAR9 : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    FUNNEL : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    CORNER_TABS : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    SQUARE_TABS : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    PLAQUE_TABS : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    CHART_X : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    CHART_STAR : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    CHART_PLUS : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    FRAME : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    MODEL_3D : SpreadsheetAutoShapeType
    '''Built-in auto shape type.'''
    ROUND_CALLOUT : SpreadsheetAutoShapeType
    '''There is no such type in Excel.'''
    TEXT_ARCH_LEFT_POUR : SpreadsheetAutoShapeType
    '''There is no such type in Excel.'''
    TEXT_ARCH_RIGHT_POUR : SpreadsheetAutoShapeType
    '''There is no such type in Excel.'''
    TEXT_ARCH_LEFT_CURVE : SpreadsheetAutoShapeType
    '''There is no such type in Excel.'''
    TEXT_ARCH_RIGHT_CURVE : SpreadsheetAutoShapeType
    '''There is no such type in Excel.'''
    UNKNOWN : SpreadsheetAutoShapeType
    '''Unknown auto shape type.'''

class SpreadsheetHeaderFooterSectionType:
    '''Represents header/footer section in Excel document.'''
    
    LEFT : SpreadsheetHeaderFooterSectionType
    '''Left section.'''
    CENTER : SpreadsheetHeaderFooterSectionType
    '''Center section.'''
    RIGHT : SpreadsheetHeaderFooterSectionType
    '''Right section.'''

class SpreadsheetMsoDrawingType:
    '''Represents office drawing object type.'''
    
    GROUP : SpreadsheetMsoDrawingType
    '''Built-in drawing type.'''
    LINE : SpreadsheetMsoDrawingType
    '''Built-in drawing type.'''
    RECTANGLE : SpreadsheetMsoDrawingType
    '''Built-in drawing type.'''
    OVAL : SpreadsheetMsoDrawingType
    '''Built-in drawing type.'''
    ARC : SpreadsheetMsoDrawingType
    '''Built-in drawing type.'''
    CHART : SpreadsheetMsoDrawingType
    '''Built-in drawing type.'''
    TEXT_BOX : SpreadsheetMsoDrawingType
    '''Built-in drawing type.'''
    BUTTON : SpreadsheetMsoDrawingType
    '''Built-in drawing type.'''
    PICTURE : SpreadsheetMsoDrawingType
    '''Built-in drawing type.'''
    POLYGON : SpreadsheetMsoDrawingType
    '''Built-in drawing type.'''
    CHECK_BOX : SpreadsheetMsoDrawingType
    '''Built-in drawing type.'''
    RADIO_BUTTON : SpreadsheetMsoDrawingType
    '''Built-in drawing type.'''
    LABEL : SpreadsheetMsoDrawingType
    '''Built-in drawing type.'''
    DIALOG_BOX : SpreadsheetMsoDrawingType
    '''Built-in drawing type.'''
    SPINNER : SpreadsheetMsoDrawingType
    '''Built-in drawing type.'''
    SCROLL_BAR : SpreadsheetMsoDrawingType
    '''Built-in drawing type.'''
    LIST_BOX : SpreadsheetMsoDrawingType
    '''Built-in drawing type.'''
    GROUP_BOX : SpreadsheetMsoDrawingType
    '''Built-in drawing type.'''
    COMBO_BOX : SpreadsheetMsoDrawingType
    '''Built-in drawing type.'''
    OLE_OBJECT : SpreadsheetMsoDrawingType
    '''Built-in drawing type.'''
    COMMENT : SpreadsheetMsoDrawingType
    '''Built-in drawing type.'''
    UNKNOWN : SpreadsheetMsoDrawingType
    '''Built-in drawing type.'''
    CELLS_DRAWING : SpreadsheetMsoDrawingType
    '''Built-in drawing type.'''
    SLICER : SpreadsheetMsoDrawingType
    '''Built-in drawing type.'''
    WEB_EXTENSION : SpreadsheetMsoDrawingType
    '''Built-in drawing type.'''
    SMART_ART : SpreadsheetMsoDrawingType
    '''Built-in drawing type.'''
    CUSTOM_XML : SpreadsheetMsoDrawingType
    '''Built-in drawing type.'''
    TIMELINE : SpreadsheetMsoDrawingType
    '''Built-in drawing type.'''
    MODEL_3D : SpreadsheetMsoDrawingType
    '''Built-in drawing type.'''

