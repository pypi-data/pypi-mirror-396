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

class IPresentationHyperlinkContainer:
    '''Represents PowerPoint document object that contains a hyperlink.'''
    
    def get_hyperlink(self, action_type : groupdocs.watermark.contents.presentation.PresentationHyperlinkActionType) -> str:
        '''Gets the hyperlink associated with this :py:class:`groupdocs.watermark.contents.presentation.IPresentationHyperlinkContainer`.
        
        :param action_type: The action that activates the hyperlink.
        :returns: The url of the hyperlink that is activated on specified action.'''
        raise NotImplementedError()
    
    def set_hyperlink(self, action_type : groupdocs.watermark.contents.presentation.PresentationHyperlinkActionType, url : str) -> None:
        '''Sets the hyperlink associated with this :py:class:`groupdocs.watermark.contents.presentation.PresentationBaseShape`.
        
        :param action_type: The action that activates the hyperlink.
        :param url: The hyperlink url.'''
        raise NotImplementedError()
    

class PresentationBaseShape(groupdocs.watermark.search.ShapeSearchAdapter):
    '''Provides the abstract base class for shapes of all types in a PowerPoint document.'''
    
    def get_hyperlink(self, action_type : groupdocs.watermark.contents.presentation.PresentationHyperlinkActionType) -> str:
        '''Gets the hyperlink associated with this :py:class:`groupdocs.watermark.contents.presentation.PresentationBaseShape`.
        
        :param action_type: The action that activates the hyperlink.
        :returns: The url of the hyperlink that is activated on specified action.'''
        raise NotImplementedError()
    
    def set_hyperlink(self, action_type : groupdocs.watermark.contents.presentation.PresentationHyperlinkActionType, url : str) -> None:
        '''Sets the hyperlink associated with this :py:class:`groupdocs.watermark.contents.presentation.PresentationBaseShape`.
        
        :param action_type: The action that activates the hyperlink.
        :param url: The hyperlink url.'''
        raise NotImplementedError()
    
    @property
    def presentation(self) -> groupdocs.watermark.contents.presentation.PresentationBaseSlide:
        '''Gets the parent presentation of this :py:class:`groupdocs.watermark.contents.presentation.PresentationBaseShape`.'''
        raise NotImplementedError()
    
    @property
    def image_fill_format(self) -> groupdocs.watermark.contents.presentation.PresentationImageFillFormat:
        '''Gets the image fill format settings of this :py:class:`groupdocs.watermark.contents.presentation.PresentationBaseShape`.'''
        raise NotImplementedError()
    
    @property
    def name(self) -> str:
        '''Gets the name of this :py:class:`groupdocs.watermark.contents.presentation.PresentationBaseShape`.'''
        raise NotImplementedError()
    
    @property
    def alternative_text(self) -> str:
        '''Gets the descriptive (alternative) text associated with
        this :py:class:`groupdocs.watermark.contents.presentation.PresentationBaseShape`.'''
        raise NotImplementedError()
    
    @alternative_text.setter
    def alternative_text(self, value : str) -> None:
        '''Sets the descriptive (alternative) text associated with
        this :py:class:`groupdocs.watermark.contents.presentation.PresentationBaseShape`.'''
        raise NotImplementedError()
    
    @property
    def id(self) -> int:
        '''Gets the identifier of this :py:class:`groupdocs.watermark.contents.presentation.PresentationBaseShape`.'''
        raise NotImplementedError()
    
    @property
    def z_order_position(self) -> int:
        '''Gets the position of this :py:class:`groupdocs.watermark.contents.presentation.PresentationBaseShape` in the z-order.'''
        raise NotImplementedError()
    
    @property
    def x(self) -> float:
        '''Gets the horizontal offset of this :py:class:`groupdocs.watermark.contents.presentation.PresentationBaseShape`
        from presentation left border in points.'''
        raise NotImplementedError()
    
    @x.setter
    def x(self, value : float) -> None:
        '''Sets the horizontal offset of this :py:class:`groupdocs.watermark.contents.presentation.PresentationBaseShape`
        from presentation left border in points.'''
        raise NotImplementedError()
    
    @property
    def y(self) -> float:
        '''Gets the vertical offset of this :py:class:`groupdocs.watermark.contents.presentation.PresentationBaseShape` from
        presentation top border in points.'''
        raise NotImplementedError()
    
    @y.setter
    def y(self, value : float) -> None:
        '''Sets the vertical offset of this :py:class:`groupdocs.watermark.contents.presentation.PresentationBaseShape` from
        presentation top border in points.'''
        raise NotImplementedError()
    
    @property
    def width(self) -> float:
        '''Gets the width of this :py:class:`groupdocs.watermark.contents.presentation.PresentationBaseShape` in points.'''
        raise NotImplementedError()
    
    @width.setter
    def width(self, value : float) -> None:
        '''Sets the width of this :py:class:`groupdocs.watermark.contents.presentation.PresentationBaseShape` in points.'''
        raise NotImplementedError()
    
    @property
    def height(self) -> float:
        '''Gets the height of this :py:class:`groupdocs.watermark.contents.presentation.PresentationBaseShape` in points.'''
        raise NotImplementedError()
    
    @height.setter
    def height(self, value : float) -> None:
        '''Sets the height of this :py:class:`groupdocs.watermark.contents.presentation.PresentationBaseShape` in points.'''
        raise NotImplementedError()
    

class PresentationBaseSlide(groupdocs.watermark.contents.ContentPart):
    '''Provides the abstract base class for slides of all types in a PowerPoint document.'''
    
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
    def shapes(self) -> groupdocs.watermark.contents.presentation.PresentationShapeCollection:
        '''Gets the collection of all shapes of the presentation.'''
        raise NotImplementedError()
    
    @property
    def charts(self) -> groupdocs.watermark.contents.presentation.PresentationChartCollection:
        '''Gets the collection of all charts on the presentation.'''
        raise NotImplementedError()
    
    @property
    def image_fill_format(self) -> groupdocs.watermark.contents.presentation.PresentationImageFillFormat:
        '''Gets the image fill format settings of the presentation.'''
        raise NotImplementedError()
    

class PresentationChart(PresentationBaseShape):
    '''Represents a chart in a PowerPoint document.'''
    
    def get_hyperlink(self, action_type : groupdocs.watermark.contents.presentation.PresentationHyperlinkActionType) -> str:
        '''Gets the hyperlink associated with this :py:class:`groupdocs.watermark.contents.presentation.PresentationBaseShape`.
        
        :param action_type: The action that activates the hyperlink.
        :returns: The url of the hyperlink that is activated on specified action.'''
        raise NotImplementedError()
    
    def set_hyperlink(self, action_type : groupdocs.watermark.contents.presentation.PresentationHyperlinkActionType, url : str) -> None:
        '''Sets the hyperlink associated with this :py:class:`groupdocs.watermark.contents.presentation.PresentationBaseShape`.
        
        :param action_type: The action that activates the hyperlink.
        :param url: The hyperlink url.'''
        raise NotImplementedError()
    
    @property
    def presentation(self) -> groupdocs.watermark.contents.presentation.PresentationBaseSlide:
        '''Gets the parent presentation of this :py:class:`groupdocs.watermark.contents.presentation.PresentationBaseShape`.'''
        raise NotImplementedError()
    
    @property
    def image_fill_format(self) -> groupdocs.watermark.contents.presentation.PresentationImageFillFormat:
        '''Gets the image fill format settings of this :py:class:`groupdocs.watermark.contents.presentation.PresentationBaseShape`.'''
        raise NotImplementedError()
    
    @property
    def name(self) -> str:
        '''Gets the name of this :py:class:`groupdocs.watermark.contents.presentation.PresentationBaseShape`.'''
        raise NotImplementedError()
    
    @property
    def alternative_text(self) -> str:
        '''Gets the descriptive (alternative) text associated with
        this :py:class:`groupdocs.watermark.contents.presentation.PresentationBaseShape`.'''
        raise NotImplementedError()
    
    @alternative_text.setter
    def alternative_text(self, value : str) -> None:
        '''Sets the descriptive (alternative) text associated with
        this :py:class:`groupdocs.watermark.contents.presentation.PresentationBaseShape`.'''
        raise NotImplementedError()
    
    @property
    def id(self) -> int:
        '''Gets the identifier of this :py:class:`groupdocs.watermark.contents.presentation.PresentationBaseShape`.'''
        raise NotImplementedError()
    
    @property
    def z_order_position(self) -> int:
        '''Gets the position of this :py:class:`groupdocs.watermark.contents.presentation.PresentationBaseShape` in the z-order.'''
        raise NotImplementedError()
    
    @property
    def x(self) -> float:
        '''Gets the horizontal offset of this :py:class:`groupdocs.watermark.contents.presentation.PresentationBaseShape`
        from presentation left border in points.'''
        raise NotImplementedError()
    
    @x.setter
    def x(self, value : float) -> None:
        '''Sets the horizontal offset of this :py:class:`groupdocs.watermark.contents.presentation.PresentationBaseShape`
        from presentation left border in points.'''
        raise NotImplementedError()
    
    @property
    def y(self) -> float:
        '''Gets the vertical offset of this :py:class:`groupdocs.watermark.contents.presentation.PresentationBaseShape` from
        presentation top border in points.'''
        raise NotImplementedError()
    
    @y.setter
    def y(self, value : float) -> None:
        '''Sets the vertical offset of this :py:class:`groupdocs.watermark.contents.presentation.PresentationBaseShape` from
        presentation top border in points.'''
        raise NotImplementedError()
    
    @property
    def width(self) -> float:
        '''Gets the width of this :py:class:`groupdocs.watermark.contents.presentation.PresentationBaseShape` in points.'''
        raise NotImplementedError()
    
    @width.setter
    def width(self, value : float) -> None:
        '''Sets the width of this :py:class:`groupdocs.watermark.contents.presentation.PresentationBaseShape` in points.'''
        raise NotImplementedError()
    
    @property
    def height(self) -> float:
        '''Gets the height of this :py:class:`groupdocs.watermark.contents.presentation.PresentationBaseShape` in points.'''
        raise NotImplementedError()
    
    @height.setter
    def height(self, value : float) -> None:
        '''Sets the height of this :py:class:`groupdocs.watermark.contents.presentation.PresentationBaseShape` in points.'''
        raise NotImplementedError()
    

class PresentationChartCollection:
    '''Represents a collection of charts in a PowerPoint document.'''
    

class PresentationContent(groupdocs.watermark.contents.Content):
    '''Represents a PowerPoint document where a watermark can be placed.'''
    
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
    
    @property
    def slide_width(self) -> float:
        '''Gets the width of a slide in points.'''
        raise NotImplementedError()
    
    @property
    def slide_height(self) -> float:
        '''Gets the height of a slide in points.'''
        raise NotImplementedError()
    
    @property
    def notes_slide_width(self) -> float:
        '''Gets the width of a notes slide in points.'''
        raise NotImplementedError()
    
    @property
    def notes_slide_height(self) -> float:
        '''Gets the height of a notes slide in points.'''
        raise NotImplementedError()
    
    @property
    def slides(self) -> groupdocs.watermark.contents.presentation.PresentationSlideCollection:
        '''Gets the collection of all slides of this :py:class:`groupdocs.watermark.contents.presentation.PresentationContent`.'''
        raise NotImplementedError()
    
    @property
    def master_slides(self) -> groupdocs.watermark.contents.presentation.PresentationMasterSlideCollection:
        '''Gets the collection of all master slides of this :py:class:`groupdocs.watermark.contents.presentation.PresentationContent`.'''
        raise NotImplementedError()
    
    @property
    def layout_slides(self) -> groupdocs.watermark.contents.presentation.PresentationLayoutSlideCollection:
        '''Gets the collection of all layout slides of this :py:class:`groupdocs.watermark.contents.presentation.PresentationContent`.'''
        raise NotImplementedError()
    
    @property
    def master_notes_slide(self) -> groupdocs.watermark.contents.presentation.PresentationMasterNotesSlide:
        '''Gets the master slide for all notes slides of this :py:class:`groupdocs.watermark.contents.presentation.PresentationContent`.'''
        raise NotImplementedError()
    
    @property
    def master_handout_slide(self) -> groupdocs.watermark.contents.presentation.PresentationMasterHandoutSlide:
        '''Gets the master handout slide of this :py:class:`groupdocs.watermark.contents.presentation.PresentationContent`.'''
        raise NotImplementedError()
    

class PresentationFormattedTextFragment(groupdocs.watermark.search.FormattedTextFragment):
    '''Represents a fragment of formatted text in a PowerPoint document.'''
    
    def get_hyperlink(self, action_type : groupdocs.watermark.contents.presentation.PresentationHyperlinkActionType) -> str:
        '''Gets the hyperlink associated with the text.
        
        :param action_type: The action that activates the hyperlink.
        :returns: The url of the hyperlink that is activated on specified action.'''
        raise NotImplementedError()
    
    def set_hyperlink(self, action_type : groupdocs.watermark.contents.presentation.PresentationHyperlinkActionType, url : str) -> None:
        '''Sets the hyperlink associated with the text.
        
        :param action_type: The action that activates the hyperlink.
        :param url: The hyperlink url.'''
        raise NotImplementedError()
    
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
    

class PresentationFormattedTextFragmentCollection(groupdocs.watermark.search.FormattedTextFragmentCollection):
    '''Represents a collection of formatted text fragments in a PowerPoint document.'''
    
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
    

class PresentationImageFillFormat:
    '''Represents the image fill format settings in a PowerPoint document.'''
    
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
        '''Gets the transparency of the background image as a value from 0.0 (opaque) through 1.0
        (fully transparent).'''
        raise NotImplementedError()
    
    @transparency.setter
    def transparency(self, value : float) -> None:
        '''Sets the transparency of the background image as a value from 0.0 (opaque) through 1.0
        (fully transparent).'''
        raise NotImplementedError()
    
    @property
    def background_image(self) -> groupdocs.watermark.contents.presentation.PresentationWatermarkableImage:
        '''Gets the background image.'''
        raise NotImplementedError()
    
    @background_image.setter
    def background_image(self, value : groupdocs.watermark.contents.presentation.PresentationWatermarkableImage) -> None:
        '''Sets the background image.'''
        raise NotImplementedError()
    

class PresentationLayoutSlide(PresentationBaseSlide):
    '''Represents a PowerPoint content layout slide.'''
    
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
    def shapes(self) -> groupdocs.watermark.contents.presentation.PresentationShapeCollection:
        '''Gets the collection of all shapes of the presentation.'''
        raise NotImplementedError()
    
    @property
    def charts(self) -> groupdocs.watermark.contents.presentation.PresentationChartCollection:
        '''Gets the collection of all charts on the presentation.'''
        raise NotImplementedError()
    
    @property
    def image_fill_format(self) -> groupdocs.watermark.contents.presentation.PresentationImageFillFormat:
        '''Gets the image fill format settings of the presentation.'''
        raise NotImplementedError()
    
    @property
    def master_slide(self) -> groupdocs.watermark.contents.presentation.PresentationMasterSlide:
        '''Gets the master slide for this :py:class:`groupdocs.watermark.contents.presentation.PresentationLayoutSlide`.'''
        raise NotImplementedError()
    

class PresentationLayoutSlideCollection:
    '''Represents a collection of layout slides in a PowerPoint document.'''
    

class PresentationMasterHandoutSlide(PresentationBaseSlide):
    '''Represents a master handout slide in a PowerPoint content.'''
    
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
    def shapes(self) -> groupdocs.watermark.contents.presentation.PresentationShapeCollection:
        '''Gets the collection of all shapes of the presentation.'''
        raise NotImplementedError()
    
    @property
    def charts(self) -> groupdocs.watermark.contents.presentation.PresentationChartCollection:
        '''Gets the collection of all charts on the presentation.'''
        raise NotImplementedError()
    
    @property
    def image_fill_format(self) -> groupdocs.watermark.contents.presentation.PresentationImageFillFormat:
        '''Gets the image fill format settings of the presentation.'''
        raise NotImplementedError()
    

class PresentationMasterNotesSlide(PresentationBaseSlide):
    '''Represents a master slide for all notes slides in a PowerPoint document.'''
    
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
    def shapes(self) -> groupdocs.watermark.contents.presentation.PresentationShapeCollection:
        '''Gets the collection of all shapes of the presentation.'''
        raise NotImplementedError()
    
    @property
    def charts(self) -> groupdocs.watermark.contents.presentation.PresentationChartCollection:
        '''Gets the collection of all charts on the presentation.'''
        raise NotImplementedError()
    
    @property
    def image_fill_format(self) -> groupdocs.watermark.contents.presentation.PresentationImageFillFormat:
        '''Gets the image fill format settings of the presentation.'''
        raise NotImplementedError()
    

class PresentationMasterSlide(PresentationBaseSlide):
    '''Represents a PowerPoint document master slide.'''
    
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
    def shapes(self) -> groupdocs.watermark.contents.presentation.PresentationShapeCollection:
        '''Gets the collection of all shapes of the presentation.'''
        raise NotImplementedError()
    
    @property
    def charts(self) -> groupdocs.watermark.contents.presentation.PresentationChartCollection:
        '''Gets the collection of all charts on the presentation.'''
        raise NotImplementedError()
    
    @property
    def image_fill_format(self) -> groupdocs.watermark.contents.presentation.PresentationImageFillFormat:
        '''Gets the image fill format settings of the presentation.'''
        raise NotImplementedError()
    

class PresentationMasterSlideCollection:
    '''Represents a collection of master slides in a PowerPoint document.'''
    

class PresentationNotesSlide(PresentationBaseSlide):
    '''Represents a PowerPoint document notes slide.'''
    
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
    def shapes(self) -> groupdocs.watermark.contents.presentation.PresentationShapeCollection:
        '''Gets the collection of all shapes of the presentation.'''
        raise NotImplementedError()
    
    @property
    def charts(self) -> groupdocs.watermark.contents.presentation.PresentationChartCollection:
        '''Gets the collection of all charts on the presentation.'''
        raise NotImplementedError()
    
    @property
    def image_fill_format(self) -> groupdocs.watermark.contents.presentation.PresentationImageFillFormat:
        '''Gets the image fill format settings of the presentation.'''
        raise NotImplementedError()
    

class PresentationShape(PresentationBaseShape):
    '''Represents a drawing shape in a PowerPoint document.'''
    
    def get_hyperlink(self, action_type : groupdocs.watermark.contents.presentation.PresentationHyperlinkActionType) -> str:
        '''Gets the hyperlink associated with this :py:class:`groupdocs.watermark.contents.presentation.PresentationBaseShape`.
        
        :param action_type: The action that activates the hyperlink.
        :returns: The url of the hyperlink that is activated on specified action.'''
        raise NotImplementedError()
    
    def set_hyperlink(self, action_type : groupdocs.watermark.contents.presentation.PresentationHyperlinkActionType, url : str) -> None:
        '''Sets the hyperlink associated with this :py:class:`groupdocs.watermark.contents.presentation.PresentationBaseShape`.
        
        :param action_type: The action that activates the hyperlink.
        :param url: The hyperlink url.'''
        raise NotImplementedError()
    
    @property
    def presentation(self) -> groupdocs.watermark.contents.presentation.PresentationBaseSlide:
        '''Gets the parent presentation of this :py:class:`groupdocs.watermark.contents.presentation.PresentationBaseShape`.'''
        raise NotImplementedError()
    
    @property
    def image_fill_format(self) -> groupdocs.watermark.contents.presentation.PresentationImageFillFormat:
        '''Gets the image fill format settings of this :py:class:`groupdocs.watermark.contents.presentation.PresentationBaseShape`.'''
        raise NotImplementedError()
    
    @property
    def name(self) -> str:
        '''Gets the name of this :py:class:`groupdocs.watermark.contents.presentation.PresentationBaseShape`.'''
        raise NotImplementedError()
    
    @property
    def alternative_text(self) -> str:
        '''Gets the descriptive (alternative) text associated with
        this :py:class:`groupdocs.watermark.contents.presentation.PresentationBaseShape`.'''
        raise NotImplementedError()
    
    @alternative_text.setter
    def alternative_text(self, value : str) -> None:
        '''Sets the descriptive (alternative) text associated with
        this :py:class:`groupdocs.watermark.contents.presentation.PresentationBaseShape`.'''
        raise NotImplementedError()
    
    @property
    def id(self) -> int:
        '''Gets the identifier of this :py:class:`groupdocs.watermark.contents.presentation.PresentationBaseShape`.'''
        raise NotImplementedError()
    
    @property
    def z_order_position(self) -> int:
        '''Gets the position of this :py:class:`groupdocs.watermark.contents.presentation.PresentationBaseShape` in the z-order.'''
        raise NotImplementedError()
    
    @property
    def x(self) -> float:
        '''Gets the horizontal offset of this :py:class:`groupdocs.watermark.contents.presentation.PresentationBaseShape`
        from presentation left border in points.'''
        raise NotImplementedError()
    
    @x.setter
    def x(self, value : float) -> None:
        '''Sets the horizontal offset of this :py:class:`groupdocs.watermark.contents.presentation.PresentationBaseShape`
        from presentation left border in points.'''
        raise NotImplementedError()
    
    @property
    def y(self) -> float:
        '''Gets the vertical offset of this :py:class:`groupdocs.watermark.contents.presentation.PresentationBaseShape` from
        presentation top border in points.'''
        raise NotImplementedError()
    
    @y.setter
    def y(self, value : float) -> None:
        '''Sets the vertical offset of this :py:class:`groupdocs.watermark.contents.presentation.PresentationBaseShape` from
        presentation top border in points.'''
        raise NotImplementedError()
    
    @property
    def width(self) -> float:
        '''Gets the width of this :py:class:`groupdocs.watermark.contents.presentation.PresentationBaseShape` in points.'''
        raise NotImplementedError()
    
    @width.setter
    def width(self, value : float) -> None:
        '''Sets the width of this :py:class:`groupdocs.watermark.contents.presentation.PresentationBaseShape` in points.'''
        raise NotImplementedError()
    
    @property
    def height(self) -> float:
        '''Gets the height of this :py:class:`groupdocs.watermark.contents.presentation.PresentationBaseShape` in points.'''
        raise NotImplementedError()
    
    @height.setter
    def height(self, value : float) -> None:
        '''Sets the height of this :py:class:`groupdocs.watermark.contents.presentation.PresentationBaseShape` in points.'''
        raise NotImplementedError()
    
    @property
    def rotate_angle(self) -> float:
        '''Gets the rotate angle of this :py:class:`groupdocs.watermark.contents.presentation.PresentationShape` in degrees.'''
        raise NotImplementedError()
    
    @rotate_angle.setter
    def rotate_angle(self, value : float) -> None:
        '''Sets the rotate angle of this :py:class:`groupdocs.watermark.contents.presentation.PresentationShape` in degrees.'''
        raise NotImplementedError()
    
    @property
    def text(self) -> str:
        '''Gets the text of this :py:class:`groupdocs.watermark.contents.presentation.PresentationShape`.'''
        raise NotImplementedError()
    
    @text.setter
    def text(self, value : str) -> None:
        '''Sets the text of this :py:class:`groupdocs.watermark.contents.presentation.PresentationShape`.'''
        raise NotImplementedError()
    
    @property
    def formatted_text_fragments(self) -> groupdocs.watermark.search.FormattedTextFragmentCollection:
        '''Gets the collection of formatted text fragments of this :py:class:`groupdocs.watermark.contents.presentation.PresentationShape`.'''
        raise NotImplementedError()
    
    @property
    def shape_type(self) -> groupdocs.watermark.contents.presentation.PresentationShapeType:
        '''Gets the shape geometry preset type.'''
        raise NotImplementedError()
    
    @property
    def image(self) -> groupdocs.watermark.contents.presentation.PresentationWatermarkableImage:
        '''Gets the image of this :py:class:`groupdocs.watermark.contents.presentation.PresentationShape`.'''
        raise NotImplementedError()
    
    @image.setter
    def image(self, value : groupdocs.watermark.contents.presentation.PresentationWatermarkableImage) -> None:
        '''Sets the image of this :py:class:`groupdocs.watermark.contents.presentation.PresentationShape`.'''
        raise NotImplementedError()
    

class PresentationShapeCollection:
    '''Represents a collection of drawing shapes in a PowerPoint document.'''
    

class PresentationShapeSettings(groupdocs.watermark.contents.OfficeShapeSettings):
    '''Represents settings that can be applied to a shape watermark for a PowerPoint document.'''
    
    def __init__(self) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.watermark.contents.presentation.PresentationShapeSettings` class.'''
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
    

class PresentationSlide(PresentationBaseSlide):
    '''Represents a PowerPoint document slide.'''
    
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
    def shapes(self) -> groupdocs.watermark.contents.presentation.PresentationShapeCollection:
        '''Gets the collection of all shapes of the presentation.'''
        raise NotImplementedError()
    
    @property
    def charts(self) -> groupdocs.watermark.contents.presentation.PresentationChartCollection:
        '''Gets the collection of all charts on the presentation.'''
        raise NotImplementedError()
    
    @property
    def image_fill_format(self) -> groupdocs.watermark.contents.presentation.PresentationImageFillFormat:
        '''Gets the image fill format settings of the presentation.'''
        raise NotImplementedError()
    
    @property
    def layout_slide(self) -> groupdocs.watermark.contents.presentation.PresentationLayoutSlide:
        '''Gets the layout slide for this :py:class:`groupdocs.watermark.contents.presentation.PresentationSlide`.'''
        raise NotImplementedError()
    
    @property
    def master_slide(self) -> groupdocs.watermark.contents.presentation.PresentationMasterSlide:
        '''Gets the master slide for this :py:class:`groupdocs.watermark.contents.presentation.PresentationSlide`.'''
        raise NotImplementedError()
    
    @property
    def notes_slide(self) -> groupdocs.watermark.contents.presentation.PresentationNotesSlide:
        '''Gets the notes slide for this :py:class:`groupdocs.watermark.contents.presentation.PresentationSlide`.'''
        raise NotImplementedError()
    

class PresentationSlideCollection:
    '''Represents a collection of slides in a PowerPoint document.'''
    

class PresentationSlideImageFillFormat(PresentationImageFillFormat):
    '''Represents the image fill format settings for a slide in a PowerPoint document.'''
    
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
        '''Gets the transparency of the background image as a value from 0.0 (opaque) through 1.0
        (fully transparent).'''
        raise NotImplementedError()
    
    @transparency.setter
    def transparency(self, value : float) -> None:
        '''Sets the transparency of the background image as a value from 0.0 (opaque) through 1.0
        (fully transparent).'''
        raise NotImplementedError()
    
    @property
    def background_image(self) -> groupdocs.watermark.contents.presentation.PresentationWatermarkableImage:
        '''Gets the background image.'''
        raise NotImplementedError()
    
    @background_image.setter
    def background_image(self, value : groupdocs.watermark.contents.presentation.PresentationWatermarkableImage) -> None:
        '''Sets the background image.'''
        raise NotImplementedError()
    

class PresentationWatermarkableImage(groupdocs.watermark.contents.image.WatermarkableImage):
    '''Represents an image inside a PowerPoint document.'''
    
    def __init__(self, image_data : List[int]) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.watermark.contents.presentation.PresentationWatermarkableImage`
        class using specified image data.
        
        :param image_data: The array of unsigned bytes from which to create the
        :py:class:`groupdocs.watermark.contents.presentation.PresentationWatermarkableImage`.'''
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
    

class PresentationHyperlinkActionType:
    '''Specifies hyperlink action type.'''
    
    MOUSE_CLICK : PresentationHyperlinkActionType
    '''Hyperlink is activated on mouse click.'''
    MOUSE_OVER : PresentationHyperlinkActionType
    '''Hyperlink is activated on mouse over.'''

class PresentationShapeType:
    '''Represents a shape geometry preset type.'''
    
    NOT_DEFINED : PresentationShapeType
    '''UndefinedDocument shape type.'''
    CUSTOM : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    LINE : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    LINE_INVERSE : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    TRIANGLE : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    RIGHT_TRIANGLE : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    RECTANGLE : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    DIAMOND : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    PARALLELOGRAM : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    TRAPEZOID : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    NON_ISOSCELES_TRAPEZOID : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    PENTAGON : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    HEXAGON : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    HEPTAGON : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    OCTAGON : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    DECAGON : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    DODECAGON : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    FOUR_POINTED_STAR : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    FIVE_POINTED_STAR : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    SIX_POINTED_STAR : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    SEVEN_POINTED_STAR : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    EIGHT_POINTED_STAR : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    TEN_POINTED_STAR : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    TWELVE_POINTED_STAR : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    SIXTEEN_POINTED_STAR : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    TWENTY_FOUR_POINTED_STAR : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    THIRTY_TWO_POINTED_STAR : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    ROUND_CORNER_RECTANGLE : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    ONE_ROUND_CORNER_RECTANGLE : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    TWO_SAMESIDE_ROUND_CORNER_RECTANGLE : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    TWO_DIAGONAL_ROUND_CORNER_RECTANGLE : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    ONE_SNIP_ONE_ROUND_CORNER_RECTANGLE : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    ONE_SNIP_CORNER_RECTANGLE : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    TWO_SAMESIDE_SNIP_CORNER_RECTANGLE : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    TWO_DIAGONAL_SNIP_CORNER_RECTANGLE : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    PLAQUE : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    ELLIPSE : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    TEARDROP : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    HOME_PLATE : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    CHEVRON : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    PIE_WEDGE : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    PIE : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    BLOCK_ARC : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    DONUT : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    NO_SMOKING : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    RIGHT_ARROW : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    LEFT_ARROW : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    UP_ARROW : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    DOWN_ARROW : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    STRIPED_RIGHT_ARROW : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    NOTCHED_RIGHT_ARROW : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    BENT_UP_ARROW : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    LEFT_RIGHT_ARROW : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    UP_DOWN_ARROW : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    LEFT_UP_ARROW : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    LEFT_RIGHT_UP_ARROW : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    QUAD_ARROW : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    CALLOUT_LEFT_ARROW : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    CALLOUT_RIGHT_ARROW : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    CALLOUT_UP_ARROW : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    CALLOUT_DOWN_ARROW : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    CALLOUT_LEFT_RIGHT_ARROW : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    CALLOUT_UP_DOWN_ARROW : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    CALLOUT_QUAD_ARROW : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    BENT_ARROW : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    U_TURN_ARROW : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    CIRCULAR_ARROW : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    LEFT_CIRCULAR_ARROW : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    LEFT_RIGHT_CIRCULAR_ARROW : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    CURVED_RIGHT_ARROW : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    CURVED_LEFT_ARROW : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    CURVED_UP_ARROW : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    CURVED_DOWN_ARROW : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    SWOOSH_ARROW : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    CUBE : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    CAN : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    LIGHTNING_BOLT : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    HEART : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    SUN : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    MOON : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    SMILEY_FACE : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    IRREGULAR_SEAL1 : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    IRREGULAR_SEAL2 : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    FOLDED_CORNER : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    BEVEL : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    FRAME : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    HALF_FRAME : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    CORNER : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    DIAGONAL_STRIPE : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    CHORD : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    CURVED_ARC : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    LEFT_BRACKET : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    RIGHT_BRACKET : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    LEFT_BRACE : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    RIGHT_BRACE : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    BRACKET_PAIR : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    BRACE_PAIR : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    STRAIGHT_CONNECTOR1 : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    BENT_CONNECTOR2 : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    BENT_CONNECTOR3 : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    BENT_CONNECTOR4 : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    BENT_CONNECTOR5 : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    CURVED_CONNECTOR2 : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    CURVED_CONNECTOR3 : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    CURVED_CONNECTOR4 : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    CURVED_CONNECTOR5 : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    CALLOUT1 : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    CALLOUT2 : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    CALLOUT3 : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    CALLOUT_1_WITH_ACCENT : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    CALLOUT_2_WITH_ACCENT : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    CALLOUT_3_WITH_ACCENT : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    CALLOUT_1_WITH_BORDER : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    CALLOUT_2_WITH_BORDER : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    CALLOUT_3_WITH_BORDER : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    CALLOUT_1_WITH_BORDER_AND_ACCENT : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    CALLOUT_2_WITH_BORDER_AND_ACCENT : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    CALLOUT_3_WITH_BORDER_AND_ACCENT : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    CALLOUT_WEDGE_RECTANGLE : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    CALLOUT_WEDGE_ROUND_RECTANGLE : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    CALLOUT_WEDGE_ELLIPSE : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    CALLOUT_CLOUD : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    CLOUD : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    RIBBON : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    RIBBON2 : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    ELLIPSE_RIBBON : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    ELLIPSE_RIBBON2 : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    LEFT_RIGHT_RIBBON : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    VERTICAL_SCROLL : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    HORIZONTAL_SCROLL : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    WAVE : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    DOUBLE_WAVE : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    PLUS : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    PROCESS_FLOW : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    DECISION_FLOW : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    INPUT_OUTPUT_FLOW : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    PREDEFINED_PROCESS_FLOW : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    INTERNAL_STORAGE_FLOW : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    DOCUMENT_FLOW : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    MULTI_DOCUMENT_FLOW : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    TERMINATOR_FLOW : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    PREPARATION_FLOW : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    MANUAL_INPUT_FLOW : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    MANUAL_OPERATION_FLOW : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    CONNECTOR_FLOW : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    PUNCHED_CARD_FLOW : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    PUNCHED_TAPE_FLOW : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    SUMMING_JUNCTION_FLOW : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    OR_FLOW : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    COLLATE_FLOW : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    SORT_FLOW : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    EXTRACT_FLOW : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    MERGE_FLOW : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    OFFLINE_STORAGE_FLOW : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    ONLINE_STORAGE_FLOW : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    MAGNETIC_TAPE_FLOW : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    MAGNETIC_DISK_FLOW : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    MAGNETIC_DRUM_FLOW : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    DISPLAY_FLOW : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    DELAY_FLOW : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    ALTERNATE_PROCESS_FLOW : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    OFF_PAGE_CONNECTOR_FLOW : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    BLANK_BUTTON : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    HOME_BUTTON : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    HELP_BUTTON : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    INFORMATION_BUTTON : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    FORWARD_OR_NEXT_BUTTON : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    BACK_OR_PREVIOUS_BUTTON : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    END_BUTTON : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    BEGINNING_BUTTON : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    RETURN_BUTTON : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    DOCUMENT_BUTTON : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    SOUND_BUTTON : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    MOVIE_BUTTON : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    GEAR6 : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    GEAR9 : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    FUNNEL : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    PLUS_MATH : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    MINUS_MATH : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    MULTIPLY_MATH : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    DIVIDE_MATH : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    EQUAL_MATH : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    NOT_EQUAL_MATH : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    CORNER_TABS : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    SQUARE_TABS : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    PLAQUE_TABS : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    CHART_X : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    CHART_STAR : PresentationShapeType
    '''Built-in shape geometry preset type.'''
    CHART_PLUS : PresentationShapeType
    '''Built-in shape geometry preset type.'''

