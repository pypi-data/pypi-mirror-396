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

class PdfAnnotation(PdfShape):
    '''Represents an annotation in a pdf document.'''
    
    @property
    def text(self) -> str:
        '''Gets the text of this :py:class:`groupdocs.watermark.contents.pdf.PdfShape`.'''
        raise NotImplementedError()
    
    @text.setter
    def text(self, value : str) -> None:
        '''Sets the text of this :py:class:`groupdocs.watermark.contents.pdf.PdfShape`.'''
        raise NotImplementedError()
    
    @property
    def formatted_text_fragments(self) -> groupdocs.watermark.search.FormattedTextFragmentCollection:
        '''Gets the collection of formatted text fragments of this :py:class:`groupdocs.watermark.contents.pdf.PdfShape`.'''
        raise NotImplementedError()
    
    @property
    def image(self) -> groupdocs.watermark.contents.pdf.PdfWatermarkableImage:
        '''Gets the image of this :py:class:`groupdocs.watermark.contents.pdf.PdfShape`.'''
        raise NotImplementedError()
    
    @image.setter
    def image(self, value : groupdocs.watermark.contents.pdf.PdfWatermarkableImage) -> None:
        '''Sets the image of this :py:class:`groupdocs.watermark.contents.pdf.PdfShape`.'''
        raise NotImplementedError()
    
    @property
    def x(self) -> float:
        '''Gets the horizontal offset of this :py:class:`groupdocs.watermark.contents.pdf.PdfAnnotation` from page left border in points.'''
        raise NotImplementedError()
    
    @property
    def y(self) -> float:
        '''Gets the vertical offset of this :py:class:`groupdocs.watermark.contents.pdf.PdfAnnotation` from worksheet bottom border in points.'''
        raise NotImplementedError()
    
    @property
    def width(self) -> float:
        '''Gets the width of this :py:class:`groupdocs.watermark.contents.pdf.PdfAnnotation` in points.'''
        raise NotImplementedError()
    
    @property
    def height(self) -> float:
        '''Gets the height of this :py:class:`groupdocs.watermark.contents.pdf.PdfAnnotation` in points.'''
        raise NotImplementedError()
    
    @property
    def rotate_angle(self) -> float:
        '''Gets the rotate angle of this :py:class:`groupdocs.watermark.contents.pdf.PdfAnnotation` in degrees.'''
        raise NotImplementedError()
    
    @property
    def page(self) -> groupdocs.watermark.contents.pdf.PdfPage:
        '''Gets the parent page of this :py:class:`groupdocs.watermark.contents.pdf.PdfAnnotation`.'''
        raise NotImplementedError()
    
    @property
    def annotation_type(self) -> groupdocs.watermark.contents.pdf.PdfAnnotationType:
        '''Gets the type of this :py:class:`groupdocs.watermark.contents.pdf.PdfAnnotation`.'''
        raise NotImplementedError()
    

class PdfAnnotationCollection:
    '''Represents a collection of annotations in a pdf document.'''
    

class PdfArtifact(PdfShape):
    '''Represents an artifact in a pdf content.'''
    
    @property
    def text(self) -> str:
        '''Gets the text of this :py:class:`groupdocs.watermark.contents.pdf.PdfArtifact`.'''
        raise NotImplementedError()
    
    @text.setter
    def text(self, value : str) -> None:
        '''Sets the text of this :py:class:`groupdocs.watermark.contents.pdf.PdfArtifact`.'''
        raise NotImplementedError()
    
    @property
    def formatted_text_fragments(self) -> groupdocs.watermark.search.FormattedTextFragmentCollection:
        '''Gets the collection of formatted text fragments of this :py:class:`groupdocs.watermark.contents.pdf.PdfShape`.'''
        raise NotImplementedError()
    
    @property
    def image(self) -> groupdocs.watermark.contents.pdf.PdfWatermarkableImage:
        '''Gets the image of this :py:class:`groupdocs.watermark.contents.pdf.PdfShape`.'''
        raise NotImplementedError()
    
    @image.setter
    def image(self, value : groupdocs.watermark.contents.pdf.PdfWatermarkableImage) -> None:
        '''Sets the image of this :py:class:`groupdocs.watermark.contents.pdf.PdfShape`.'''
        raise NotImplementedError()
    
    @property
    def x(self) -> float:
        '''Gets the horizontal offset of this :py:class:`groupdocs.watermark.contents.pdf.PdfArtifact` from page left border in points.'''
        raise NotImplementedError()
    
    @property
    def y(self) -> float:
        '''Gets the vertical offset of this :py:class:`groupdocs.watermark.contents.pdf.PdfArtifact` from page bottom border in points.'''
        raise NotImplementedError()
    
    @property
    def width(self) -> float:
        '''Gets the width of this :py:class:`groupdocs.watermark.contents.pdf.PdfArtifact` in points.'''
        raise NotImplementedError()
    
    @property
    def height(self) -> float:
        '''Gets the height of this :py:class:`groupdocs.watermark.contents.pdf.PdfArtifact` in points.'''
        raise NotImplementedError()
    
    @property
    def rotate_angle(self) -> float:
        '''Gets the rotate angle of this :py:class:`groupdocs.watermark.contents.pdf.PdfArtifact` in degrees.'''
        raise NotImplementedError()
    
    @property
    def page(self) -> groupdocs.watermark.contents.pdf.PdfPage:
        '''Gets the parent page of this :py:class:`groupdocs.watermark.contents.pdf.PdfArtifact`.'''
        raise NotImplementedError()
    
    @property
    def artifact_type(self) -> groupdocs.watermark.contents.pdf.PdfArtifactType:
        '''Gets the type of this :py:class:`groupdocs.watermark.contents.pdf.PdfArtifact`.'''
        raise NotImplementedError()
    
    @property
    def artifact_subtype(self) -> groupdocs.watermark.contents.pdf.PdfArtifactSubtype:
        '''Gets the subtype of this :py:class:`groupdocs.watermark.contents.pdf.PdfArtifact`.'''
        raise NotImplementedError()
    
    @property
    def opacity(self) -> float:
        '''Gets the opacity of this :py:class:`groupdocs.watermark.contents.pdf.PdfArtifact`.'''
        raise NotImplementedError()
    

class PdfArtifactCollection:
    '''Represents a collection of artifacts in a pdf content.'''
    

class PdfAttachment(groupdocs.watermark.common.Attachment):
    '''Represents a file attached to a pdf content.'''
    
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
    def name(self) -> str:
        '''Gets the name of the attached file.'''
        raise NotImplementedError()
    
    @name.setter
    def name(self, value : str) -> None:
        '''Sets the name of the attached file.'''
        raise NotImplementedError()
    
    @property
    def description(self) -> str:
        '''Gets the description of the attached file.'''
        raise NotImplementedError()
    
    @description.setter
    def description(self, value : str) -> None:
        '''Sets the description of the attached file.'''
        raise NotImplementedError()
    

class PdfAttachmentCollection:
    '''Represents a collection of attachments in a pdf document.'''
    
    def add(self, file_content : List[int], name : str, description : str) -> None:
        '''Adds an attachment to the :py:class:`groupdocs.watermark.contents.pdf.PdfContent`.
        
        :param file_content: The content of the file to be attached.
        :param name: The name of the file.
        :param description: The description of the file.'''
        raise NotImplementedError()
    

class PdfContent(groupdocs.watermark.contents.Content):
    '''Represents a pdf document where a watermark can be placed.'''
    
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
    
    @overload
    def encrypt(self, password : str) -> None:
        '''Encrypts the document using the same password as user password and owner password.
        
        :param password: User and owner password.'''
        raise NotImplementedError()
    
    @overload
    def encrypt(self, user_password : str, owner_password : str, permissions : groupdocs.watermark.contents.pdf.PdfPermissions, crypto_algorithm : groupdocs.watermark.contents.pdf.PdfCryptoAlgorithm) -> None:
        '''Encrypts the content.
        
        :param user_password: User password.
        :param owner_password: Owner password.
        :param permissions: Content permissions.
        :param crypto_algorithm: Cryptographic algorithm.'''
        raise NotImplementedError()
    
    def decrypt(self) -> None:
        '''Decrypts the content.'''
        raise NotImplementedError()
    
    def rasterize(self, horizontal_resolution : int, vertical_resolution : int, image_format : groupdocs.watermark.contents.pdf.PdfImageConversionFormat) -> None:
        '''Converts all content pages into images.
        
        :param horizontal_resolution: Horizontal image resolution.
        :param vertical_resolution: Vertical image resolution.
        :param image_format: Image format.'''
        raise NotImplementedError()
    
    @property
    def pages(self) -> groupdocs.watermark.contents.pdf.PdfPageCollection:
        '''Gets the collection of all pages of this :py:class:`groupdocs.watermark.contents.pdf.PdfContent`.'''
        raise NotImplementedError()
    
    @property
    def attachments(self) -> groupdocs.watermark.contents.pdf.PdfAttachmentCollection:
        '''Gets the collection of all attachments of this :py:class:`groupdocs.watermark.contents.pdf.PdfContent`.'''
        raise NotImplementedError()
    
    @property
    def page_margin_type(self) -> groupdocs.watermark.contents.pdf.PdfPageMarginType:
        '''Gets pdf page margins to be used during watermark adding.'''
        raise NotImplementedError()
    
    @page_margin_type.setter
    def page_margin_type(self, value : groupdocs.watermark.contents.pdf.PdfPageMarginType) -> None:
        '''Sets pdf page margins to be used during watermark adding.'''
        raise NotImplementedError()
    

class PdfFormattedTextFragment(groupdocs.watermark.search.FormattedTextFragment):
    '''Represents a fragment of formatted text in a pdf document.'''
    
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
    

class PdfFormattedTextFragmentCollection(groupdocs.watermark.search.FormattedTextFragmentCollection):
    '''Represents a collection of formatted text fragments in a pdf document.'''
    
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
    

class PdfOperator:
    '''Represents an operator of vector content in a pdf document.'''
    
    @property
    def foreground_color(self) -> groupdocs.watermark.watermarks.Color:
        '''Gets the foreground color of this :py:class:`groupdocs.watermark.contents.pdf.PdfOperator`.'''
        raise NotImplementedError()
    

class PdfOperatorCollection:
    '''Represents a collection of operators in a pdf content.'''
    

class PdfPage(groupdocs.watermark.contents.ContentPart):
    '''Represents pdf document page.'''
    
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
    
    def rasterize(self, horizontal_resolution : int, vertical_resolution : int, image_format : groupdocs.watermark.contents.pdf.PdfImageConversionFormat) -> None:
        '''Converts page content into an image.
        
        :param horizontal_resolution: Horizontal image resolution.
        :param vertical_resolution: Vertical image resolution.
        :param image_format: Image format.'''
        raise NotImplementedError()
    
    @property
    def width(self) -> float:
        '''Gets the width of this :py:class:`groupdocs.watermark.contents.pdf.PdfPage` in points.'''
        raise NotImplementedError()
    
    @property
    def height(self) -> float:
        '''Gets the height of this :py:class:`groupdocs.watermark.contents.pdf.PdfPage` in points.'''
        raise NotImplementedError()
    
    @property
    def artifacts(self) -> groupdocs.watermark.contents.pdf.PdfArtifactCollection:
        '''Gets the collection of all artifacts of this :py:class:`groupdocs.watermark.contents.pdf.PdfPage`.'''
        raise NotImplementedError()
    
    @property
    def x_objects(self) -> groupdocs.watermark.contents.pdf.PdfXObjectCollection:
        '''Gets the collection of all XObjects of this :py:class:`groupdocs.watermark.contents.pdf.PdfPage`.'''
        raise NotImplementedError()
    
    @property
    def annotations(self) -> groupdocs.watermark.contents.pdf.PdfAnnotationCollection:
        '''Gets the collection of all annotations of this :py:class:`groupdocs.watermark.contents.pdf.PdfPage`.'''
        raise NotImplementedError()
    

class PdfPageCollection:
    '''Represents a collection of pages in a pdf content.'''
    

class PdfShape(groupdocs.watermark.search.ShapeSearchAdapter):
    '''Provides base class for XObjects, Artifacts and Annotations.'''
    
    @property
    def text(self) -> str:
        '''Gets the text of this :py:class:`groupdocs.watermark.contents.pdf.PdfShape`.'''
        raise NotImplementedError()
    
    @text.setter
    def text(self, value : str) -> None:
        '''Sets the text of this :py:class:`groupdocs.watermark.contents.pdf.PdfShape`.'''
        raise NotImplementedError()
    
    @property
    def formatted_text_fragments(self) -> groupdocs.watermark.search.FormattedTextFragmentCollection:
        '''Gets the collection of formatted text fragments of this :py:class:`groupdocs.watermark.contents.pdf.PdfShape`.'''
        raise NotImplementedError()
    
    @property
    def image(self) -> groupdocs.watermark.contents.pdf.PdfWatermarkableImage:
        '''Gets the image of this :py:class:`groupdocs.watermark.contents.pdf.PdfShape`.'''
        raise NotImplementedError()
    
    @image.setter
    def image(self, value : groupdocs.watermark.contents.pdf.PdfWatermarkableImage) -> None:
        '''Sets the image of this :py:class:`groupdocs.watermark.contents.pdf.PdfShape`.'''
        raise NotImplementedError()
    
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
    
    @property
    def rotate_angle(self) -> float:
        '''Gets the rotate angle of the object in degrees.'''
        raise NotImplementedError()
    

class PdfShapeFormattedTextFragmentCollection(PdfFormattedTextFragmentCollection):
    '''Represents a collection of formatted text fragments in a pdf document XObject, Artifact or Annotation.'''
    
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
    

class PdfTextFormattedTextFragmentCollection(PdfFormattedTextFragmentCollection):
    '''Represents a collection of formatted text fragments in a pdf content main text.'''
    
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
    

class PdfWatermarkableImage(groupdocs.watermark.contents.image.WatermarkableImage):
    '''Represents an image inside a Pdf document.'''
    
    def __init__(self, image_data : List[int]) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.watermark.contents.pdf.PdfWatermarkableImage` class using specified image data.
        
        :param image_data: The array of unsigned bytes from which to create
        the :py:class:`groupdocs.watermark.contents.pdf.PdfWatermarkableImage`.'''
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
    

class PdfXForm(PdfXObject):
    '''Represents an XForm in a pdf content.'''
    
    @property
    def text(self) -> str:
        '''Gets the text of this :py:class:`groupdocs.watermark.contents.pdf.PdfShape`.'''
        raise NotImplementedError()
    
    @text.setter
    def text(self, value : str) -> None:
        '''Sets the text of this :py:class:`groupdocs.watermark.contents.pdf.PdfShape`.'''
        raise NotImplementedError()
    
    @property
    def formatted_text_fragments(self) -> groupdocs.watermark.search.FormattedTextFragmentCollection:
        '''Gets the collection of formatted text fragments of this :py:class:`groupdocs.watermark.contents.pdf.PdfShape`.'''
        raise NotImplementedError()
    
    @property
    def image(self) -> groupdocs.watermark.contents.pdf.PdfWatermarkableImage:
        '''Gets the image of this :py:class:`groupdocs.watermark.contents.pdf.PdfShape`.'''
        raise NotImplementedError()
    
    @image.setter
    def image(self, value : groupdocs.watermark.contents.pdf.PdfWatermarkableImage) -> None:
        '''Sets the image of this :py:class:`groupdocs.watermark.contents.pdf.PdfShape`.'''
        raise NotImplementedError()
    
    @property
    def x(self) -> float:
        '''Gets the horizontal offset of this :py:class:`groupdocs.watermark.contents.pdf.PdfXObject` from page left border in points.'''
        raise NotImplementedError()
    
    @property
    def y(self) -> float:
        '''Gets the vertical offset of this :py:class:`groupdocs.watermark.contents.pdf.PdfXObject` from page bottom border in points.'''
        raise NotImplementedError()
    
    @property
    def width(self) -> float:
        '''Gets the width of this :py:class:`groupdocs.watermark.contents.pdf.PdfXObject` in points.'''
        raise NotImplementedError()
    
    @property
    def height(self) -> float:
        '''Gets the height of this :py:class:`groupdocs.watermark.contents.pdf.PdfXObject` in points.'''
        raise NotImplementedError()
    
    @property
    def rotate_angle(self) -> float:
        '''Gets the rotate angle of this :py:class:`groupdocs.watermark.contents.pdf.PdfXObject` in degrees.'''
        raise NotImplementedError()
    
    @property
    def page(self) -> groupdocs.watermark.contents.pdf.PdfPage:
        '''Gets the parent page of this :py:class:`groupdocs.watermark.contents.pdf.PdfXObject`.'''
        raise NotImplementedError()
    

class PdfXImage(PdfXObject):
    '''Represents an XImage in a pdf content.'''
    
    @property
    def text(self) -> str:
        '''Gets the text of this :py:class:`groupdocs.watermark.contents.pdf.PdfShape`.'''
        raise NotImplementedError()
    
    @text.setter
    def text(self, value : str) -> None:
        '''Sets the text of this :py:class:`groupdocs.watermark.contents.pdf.PdfShape`.'''
        raise NotImplementedError()
    
    @property
    def formatted_text_fragments(self) -> groupdocs.watermark.search.FormattedTextFragmentCollection:
        '''Gets the collection of formatted text fragments of this :py:class:`groupdocs.watermark.contents.pdf.PdfShape`.'''
        raise NotImplementedError()
    
    @property
    def image(self) -> groupdocs.watermark.contents.pdf.PdfWatermarkableImage:
        '''Gets the image of this :py:class:`groupdocs.watermark.contents.pdf.PdfShape`.'''
        raise NotImplementedError()
    
    @image.setter
    def image(self, value : groupdocs.watermark.contents.pdf.PdfWatermarkableImage) -> None:
        '''Sets the image of this :py:class:`groupdocs.watermark.contents.pdf.PdfShape`.'''
        raise NotImplementedError()
    
    @property
    def x(self) -> float:
        '''Gets the horizontal offset of this :py:class:`groupdocs.watermark.contents.pdf.PdfXObject` from page left border in points.'''
        raise NotImplementedError()
    
    @property
    def y(self) -> float:
        '''Gets the vertical offset of this :py:class:`groupdocs.watermark.contents.pdf.PdfXObject` from page bottom border in points.'''
        raise NotImplementedError()
    
    @property
    def width(self) -> float:
        '''Gets the width of this :py:class:`groupdocs.watermark.contents.pdf.PdfXObject` in points.'''
        raise NotImplementedError()
    
    @property
    def height(self) -> float:
        '''Gets the height of this :py:class:`groupdocs.watermark.contents.pdf.PdfXObject` in points.'''
        raise NotImplementedError()
    
    @property
    def rotate_angle(self) -> float:
        '''Gets the rotate angle of this :py:class:`groupdocs.watermark.contents.pdf.PdfXObject` in degrees.'''
        raise NotImplementedError()
    
    @property
    def page(self) -> groupdocs.watermark.contents.pdf.PdfPage:
        '''Gets the parent page of this :py:class:`groupdocs.watermark.contents.pdf.PdfXObject`.'''
        raise NotImplementedError()
    

class PdfXObject(PdfShape):
    '''Represents an XObject in a pdf document.'''
    
    @property
    def text(self) -> str:
        '''Gets the text of this :py:class:`groupdocs.watermark.contents.pdf.PdfShape`.'''
        raise NotImplementedError()
    
    @text.setter
    def text(self, value : str) -> None:
        '''Sets the text of this :py:class:`groupdocs.watermark.contents.pdf.PdfShape`.'''
        raise NotImplementedError()
    
    @property
    def formatted_text_fragments(self) -> groupdocs.watermark.search.FormattedTextFragmentCollection:
        '''Gets the collection of formatted text fragments of this :py:class:`groupdocs.watermark.contents.pdf.PdfShape`.'''
        raise NotImplementedError()
    
    @property
    def image(self) -> groupdocs.watermark.contents.pdf.PdfWatermarkableImage:
        '''Gets the image of this :py:class:`groupdocs.watermark.contents.pdf.PdfShape`.'''
        raise NotImplementedError()
    
    @image.setter
    def image(self, value : groupdocs.watermark.contents.pdf.PdfWatermarkableImage) -> None:
        '''Sets the image of this :py:class:`groupdocs.watermark.contents.pdf.PdfShape`.'''
        raise NotImplementedError()
    
    @property
    def x(self) -> float:
        '''Gets the horizontal offset of this :py:class:`groupdocs.watermark.contents.pdf.PdfXObject` from page left border in points.'''
        raise NotImplementedError()
    
    @property
    def y(self) -> float:
        '''Gets the vertical offset of this :py:class:`groupdocs.watermark.contents.pdf.PdfXObject` from page bottom border in points.'''
        raise NotImplementedError()
    
    @property
    def width(self) -> float:
        '''Gets the width of this :py:class:`groupdocs.watermark.contents.pdf.PdfXObject` in points.'''
        raise NotImplementedError()
    
    @property
    def height(self) -> float:
        '''Gets the height of this :py:class:`groupdocs.watermark.contents.pdf.PdfXObject` in points.'''
        raise NotImplementedError()
    
    @property
    def rotate_angle(self) -> float:
        '''Gets the rotate angle of this :py:class:`groupdocs.watermark.contents.pdf.PdfXObject` in degrees.'''
        raise NotImplementedError()
    
    @property
    def page(self) -> groupdocs.watermark.contents.pdf.PdfPage:
        '''Gets the parent page of this :py:class:`groupdocs.watermark.contents.pdf.PdfXObject`.'''
        raise NotImplementedError()
    

class PdfXObjectCollection:
    '''Represents a collection of XObjects in a pdf document.'''
    

class PdfAnnotationType:
    '''Enumeration of annotation types.'''
    
    TEXT : PdfAnnotationType
    '''Text annotation type.'''
    CIRCLE : PdfAnnotationType
    '''Circle annotation type.'''
    POLYGON : PdfAnnotationType
    '''Polygon annotation type.'''
    POLY_LINE : PdfAnnotationType
    '''Polyline annotation type.'''
    LINE : PdfAnnotationType
    '''Line annotation type.'''
    SQUARE : PdfAnnotationType
    '''Square annotation type.'''
    FREE_TEXT : PdfAnnotationType
    '''Free text annotation type.'''
    HIGHLIGHT : PdfAnnotationType
    '''Highlight annotation type.'''
    UNDERLINE : PdfAnnotationType
    '''Underline annotation type.'''
    SQUIGGLY : PdfAnnotationType
    '''Squiggle annotation type.'''
    STRIKE_OUT : PdfAnnotationType
    '''Strikeout annotation type.'''
    CARET : PdfAnnotationType
    '''Caret annotation type.'''
    INK : PdfAnnotationType
    '''Ink annotation type.'''
    LINK : PdfAnnotationType
    '''Link annotation type.'''
    POPUP : PdfAnnotationType
    '''Popup annotation type.'''
    FILE_ATTACHMENT : PdfAnnotationType
    '''File attachment annotation type.'''
    SOUND : PdfAnnotationType
    '''Sound annotation type.'''
    MOVIE : PdfAnnotationType
    '''Movie annotation type.'''
    SCREEN : PdfAnnotationType
    '''Screen annotation type.'''
    WIDGET : PdfAnnotationType
    '''Widget annotation type.'''
    WATERMARK : PdfAnnotationType
    '''Watermark annotation type.'''
    TRAP_NET : PdfAnnotationType
    '''Trap network annotation type.'''
    PRINTER_MARK : PdfAnnotationType
    '''Printer mark annotation type.'''
    REDACTION : PdfAnnotationType
    '''Redaction annotation type.'''
    STAMP : PdfAnnotationType
    '''Rubber stamp annotation type.'''
    RICH_MEDIA : PdfAnnotationType
    '''RichMedia annotation type.'''
    UNKNOWN : PdfAnnotationType
    '''Unknown annotation.'''
    PDF_3D : PdfAnnotationType
    '''PDF3D annotation.'''
    COLOR_BAR : PdfAnnotationType
    '''ColorBar annotation.'''
    TRIM_MARK : PdfAnnotationType
    '''Trim mark annotation.'''
    BLEED_MARK : PdfAnnotationType
    '''Bleed mark annotation.'''
    REGISTRATION_MARK : PdfAnnotationType
    '''Registration mark annotation.'''
    PAGE_INFORMATION : PdfAnnotationType
    '''Page information annotation.'''

class PdfArtifactSubtype:
    '''Enumeration of possible artifacts subtype.'''
    
    HEADER : PdfArtifactSubtype
    '''Header subtype.'''
    FOOTER : PdfArtifactSubtype
    '''Footer subtype.'''
    WATERMARK : PdfArtifactSubtype
    '''Watermark subtype.'''
    BACKGROUND : PdfArtifactSubtype
    '''Background subtype.'''
    UNDEFINED : PdfArtifactSubtype
    '''UndefinedDocument subtype.'''

class PdfArtifactType:
    '''Enumeration of possible artifact types.'''
    
    PAGINATION : PdfArtifactType
    '''Pagination type.'''
    LAYOUT : PdfArtifactType
    '''Layout type.'''
    PAGE : PdfArtifactType
    '''Page type.'''
    BACKGROUND : PdfArtifactType
    '''Background type.'''
    UNDEFINED : PdfArtifactType
    '''UndefinedDocument type.'''

class PdfCryptoAlgorithm:
    '''Represent type of cryptographic algorithm that used in encryption routine.'''
    
    RC4X40 : PdfCryptoAlgorithm
    '''RC4 with key length 40.'''
    RC4X128 : PdfCryptoAlgorithm
    '''RC4 with key length 128.'''
    AE_SX128 : PdfCryptoAlgorithm
    '''AES with key length 128.'''
    AE_SX256 : PdfCryptoAlgorithm
    '''AES with key length 256.'''

class PdfImageConversionFormat:
    '''Represents image formats that can be used for pdf document pages rasterization.'''
    
    JPEG : PdfImageConversionFormat
    '''Jpeg image.'''
    PNG : PdfImageConversionFormat
    '''Png image.'''
    GIF : PdfImageConversionFormat
    '''Gif image.'''

class PdfPageMarginType:
    '''Represents pdf crop margins to be used during watermark adding.'''
    
    BLEED_BOX : PdfPageMarginType
    '''Pdf BleedBox is used as watermarking area.'''
    TRIM_BOX : PdfPageMarginType
    '''Pdf TrimBox is used as watermarking area.'''
    ART_BOX : PdfPageMarginType
    '''Pdf ArtBox is used as watermarking area.'''

class PdfPermissions:
    '''Represents user\'s permissions for a pdf document.'''
    
    PRINT_DOCUMENT : PdfPermissions
    '''Print the content.'''
    MODIFY_CONTENT : PdfPermissions
    '''Modify the content.'''
    EXTRACT_CONTENT : PdfPermissions
    '''Copy or otherwise extract text and graphics from the document.'''
    MODIFY_TEXT_ANNOTATIONS : PdfPermissions
    '''Add or modify text annotations.'''
    FILL_FORM : PdfPermissions
    '''Fill in existing interactive form fields.'''
    EXTRACT_CONTENT_WITH_DISABILITIES : PdfPermissions
    '''Extract text and graphics.'''
    ASSEMBLE_DOCUMENT : PdfPermissions
    '''Assemble the content.'''
    PRINTING_QUALITY : PdfPermissions
    '''Print the content to a representation from which a faithful digital copy of the PDF document could be generated.'''

