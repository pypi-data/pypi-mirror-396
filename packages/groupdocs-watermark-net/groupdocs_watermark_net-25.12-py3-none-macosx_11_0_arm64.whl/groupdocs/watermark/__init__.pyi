
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

class License:
    '''Provides methods to license the component.'''
    
    def __init__(self) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.watermark.License` class.'''
        raise NotImplementedError()
    
    @overload
    def set_license(self, file_path : str) -> None:
        '''Licenses the component.
        
        :param file_path: Absolute path to license file.'''
        raise NotImplementedError()
    
    @overload
    def set_license(self, stream : io._IOBase) -> None:
        '''Licenses the component.
        
        :param stream: License stream.'''
        raise NotImplementedError()
    

class Metered:
    '''Provides methods to license the component with Metered license.'''
    
    def __init__(self) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.watermark.Metered` class.'''
        raise NotImplementedError()
    
    def set_metered_key(self, public_key : str, private_key : str) -> None:
        '''Activates product with Metered keys.
        
        :param public_key: The public key.
        :param private_key: The private key.'''
        raise NotImplementedError()
    
    @staticmethod
    def get_consumption_quantity() -> System.Decimal:
        '''Retrieves amount of MBs processed.
        
        :returns: The amount of MBs processed.'''
        raise NotImplementedError()
    
    @staticmethod
    def get_consumption_credit() -> int:
        '''Retrieves count of credits consumed.
        
        :returns: The count of credits consumed.'''
        raise NotImplementedError()
    

class Watermark:
    '''Represents a watermark to be added to a document.'''
    
    @property
    def opacity(self) -> float:
        '''Gets the opacity of this :py:class:`groupdocs.watermark.Watermark`.'''
        raise NotImplementedError()
    
    @opacity.setter
    def opacity(self, value : float) -> None:
        '''Sets the opacity of this :py:class:`groupdocs.watermark.Watermark`.'''
        raise NotImplementedError()
    
    @property
    def y(self) -> float:
        '''Gets the y-coordinate of this :py:class:`groupdocs.watermark.Watermark`.'''
        raise NotImplementedError()
    
    @y.setter
    def y(self, value : float) -> None:
        '''Sets the y-coordinate of this :py:class:`groupdocs.watermark.Watermark`.'''
        raise NotImplementedError()
    
    @property
    def x(self) -> float:
        '''Gets the x-coordinate of this :py:class:`groupdocs.watermark.Watermark`.'''
        raise NotImplementedError()
    
    @x.setter
    def x(self, value : float) -> None:
        '''Sets the x-coordinate of this :py:class:`groupdocs.watermark.Watermark`.'''
        raise NotImplementedError()
    
    @property
    def vertical_alignment(self) -> groupdocs.watermark.common.VerticalAlignment:
        '''Gets the vertical alignment of this :py:class:`groupdocs.watermark.Watermark`.'''
        raise NotImplementedError()
    
    @vertical_alignment.setter
    def vertical_alignment(self, value : groupdocs.watermark.common.VerticalAlignment) -> None:
        '''Sets the vertical alignment of this :py:class:`groupdocs.watermark.Watermark`.'''
        raise NotImplementedError()
    
    @property
    def horizontal_alignment(self) -> groupdocs.watermark.common.HorizontalAlignment:
        '''Gets the horizontal alignment of this :py:class:`groupdocs.watermark.Watermark`.'''
        raise NotImplementedError()
    
    @horizontal_alignment.setter
    def horizontal_alignment(self, value : groupdocs.watermark.common.HorizontalAlignment) -> None:
        '''Sets the horizontal alignment of this :py:class:`groupdocs.watermark.Watermark`.'''
        raise NotImplementedError()
    
    @property
    def rotate_angle(self) -> float:
        '''Gets the rotate angle of this :py:class:`groupdocs.watermark.Watermark` in degrees.'''
        raise NotImplementedError()
    
    @rotate_angle.setter
    def rotate_angle(self, value : float) -> None:
        '''Sets the rotate angle of this :py:class:`groupdocs.watermark.Watermark` in degrees.'''
        raise NotImplementedError()
    
    @property
    def is_background(self) -> bool:
        '''Gets a value indicating whether the watermark should be placed at background.'''
        raise NotImplementedError()
    
    @is_background.setter
    def is_background(self, value : bool) -> None:
        '''Sets a value indicating whether the watermark should be placed at background.'''
        raise NotImplementedError()
    
    @property
    def margins(self) -> groupdocs.watermark.watermarks.Margins:
        '''Gets the margin settings of this :py:class:`groupdocs.watermark.Watermark`.'''
        raise NotImplementedError()
    
    @margins.setter
    def margins(self, value : groupdocs.watermark.watermarks.Margins) -> None:
        '''Sets the margin settings of this :py:class:`groupdocs.watermark.Watermark`.'''
        raise NotImplementedError()
    
    @property
    def pages_setup(self) -> groupdocs.watermark.watermarks.PagesSetup:
        '''Gets the pages setup settings of this :py:class:`groupdocs.watermark.Watermark`.'''
        raise NotImplementedError()
    
    @pages_setup.setter
    def pages_setup(self, value : groupdocs.watermark.watermarks.PagesSetup) -> None:
        '''Sets the pages setup settings of this :py:class:`groupdocs.watermark.Watermark`.'''
        raise NotImplementedError()
    
    @property
    def height(self) -> float:
        '''Gets the desired height of this :py:class:`groupdocs.watermark.Watermark`.'''
        raise NotImplementedError()
    
    @height.setter
    def height(self, value : float) -> None:
        '''Sets the desired height of this :py:class:`groupdocs.watermark.Watermark`.'''
        raise NotImplementedError()
    
    @property
    def width(self) -> float:
        '''Gets the desired width of this :py:class:`groupdocs.watermark.Watermark`.'''
        raise NotImplementedError()
    
    @width.setter
    def width(self, value : float) -> None:
        '''Sets the desired width of this :py:class:`groupdocs.watermark.Watermark`.'''
        raise NotImplementedError()
    
    @property
    def scale_factor(self) -> float:
        '''Gets a value that defines how watermark size depends on parent size.'''
        raise NotImplementedError()
    
    @scale_factor.setter
    def scale_factor(self, value : float) -> None:
        '''Sets a value that defines how watermark size depends on parent size.'''
        raise NotImplementedError()
    
    @property
    def sizing_type(self) -> groupdocs.watermark.watermarks.SizingType:
        '''Gets a value specifying a way watermark should be sized.'''
        raise NotImplementedError()
    
    @sizing_type.setter
    def sizing_type(self, value : groupdocs.watermark.watermarks.SizingType) -> None:
        '''Sets a value specifying a way watermark should be sized.'''
        raise NotImplementedError()
    
    @property
    def consider_parent_margins(self) -> bool:
        '''Gets a value indicating whether the watermark size and coordinates are calculated
        considering parent margins.'''
        raise NotImplementedError()
    
    @consider_parent_margins.setter
    def consider_parent_margins(self, value : bool) -> None:
        '''Sets a value indicating whether the watermark size and coordinates are calculated
        considering parent margins.'''
        raise NotImplementedError()
    
    @property
    def save_result_in_metadata(self) -> bool:
        '''Gets a value indicating whether to save information about added watermarks in the document metadata.'''
        raise NotImplementedError()
    
    @save_result_in_metadata.setter
    def save_result_in_metadata(self, value : bool) -> None:
        '''Sets a value indicating whether to save information about added watermarks in the document metadata.'''
        raise NotImplementedError()
    
    @property
    def tile_options(self) -> groupdocs.watermark.watermarks.TileOptions:
        '''Get options to define repeated watermark'''
        raise NotImplementedError()
    
    @tile_options.setter
    def tile_options(self, value : groupdocs.watermark.watermarks.TileOptions) -> None:
        '''Get or sets options to define repeated watermark'''
        raise NotImplementedError()
    

class Watermarker:
    '''Represents a class for watermark management in a document.'''
    
    @overload
    def __init__(self, file_path : str) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.watermark.Watermarker` class with the specified document path.
        
        :param file_path: The file path to load the document from.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, file_path : str, options : groupdocs.watermark.options.LoadOptions) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.watermark.Watermarker` class with the specified
        document path and load options.
        
        :param file_path: The file path to load document from.
        :param options: Additional options to use when loading a document.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, file_path : str, settings : groupdocs.watermark.WatermarkerSettings) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.watermark.Watermarker` class with the specified
        document path and settings.
        
        :param file_path: The file path to load document from.
        :param settings: Additional settings to use when working with loaded document.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, file_path : str, options : groupdocs.watermark.options.LoadOptions, settings : groupdocs.watermark.WatermarkerSettings) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.watermark.Watermarker` class with the specified
        document path, load options and settings.
        
        :param file_path: The file path to load document from.
        :param options: Additional options to use when loading a document.
        :param settings: Additional settings to use when working with loaded document.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, document : io._IOBase) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.watermark.Watermarker` class with the specified stream.
        
        :param document: The stream to load document from.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, document : io._IOBase, options : groupdocs.watermark.options.LoadOptions) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.watermark.Watermarker` class with the specified stream
        and load options.
        
        :param document: The stream to load document from.
        :param options: Additional options to use when loading a document.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, document : io._IOBase, settings : groupdocs.watermark.WatermarkerSettings) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.watermark.Watermarker` class with the specified stream
        and settings.
        
        :param document: The stream to load document from.
        :param settings: Additional settings to use when working with loaded document.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, document : io._IOBase, options : groupdocs.watermark.options.LoadOptions, settings : groupdocs.watermark.WatermarkerSettings) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.watermark.Watermarker` class with the specified stream,
        load options and settings.
        
        :param document: The stream to load document from.
        :param options: Additional options to use when loading a document.
        :param settings: Additional settings to use when working with loaded document.'''
        raise NotImplementedError()
    
    @overload
    def add(self, watermark : groupdocs.watermark.Watermark) -> groupdocs.watermark.watermarks.results.AddWatermarkResult:
        '''Adds a watermark to the loaded document.
        
        :param watermark: The watermark to add to the document.'''
        raise NotImplementedError()
    
    @overload
    def add(self, watermark : groupdocs.watermark.Watermark, options : groupdocs.watermark.options.WatermarkOptions) -> groupdocs.watermark.watermarks.results.AddWatermarkResult:
        '''Adds a watermark to the loaded document using watermark options.
        
        :param watermark: The watermark to add to the document.
        :param options: Additional options to use when adding the watermark.'''
        raise NotImplementedError()
    
    @overload
    def remove(self, possible_watermark : groupdocs.watermark.search.PossibleWatermark) -> None:
        '''Removes watermark from the document.
        
        :param possible_watermark: The watermark to remove.'''
        raise NotImplementedError()
    
    @overload
    def remove(self, possible_watermarks : groupdocs.watermark.search.PossibleWatermarkCollection) -> None:
        '''Removes all watermarks in the collection from the document.
        
        :param possible_watermarks: The collection of watermarks to remove.'''
        raise NotImplementedError()
    
    @overload
    def save(self) -> groupdocs.watermark.internal.WatermarkResult:
        '''Saves the document data to the underlying stream.'''
        raise NotImplementedError()
    
    @overload
    def save(self, file_path : str) -> groupdocs.watermark.internal.WatermarkResult:
        '''Saves the document to the specified file location.
        
        :param file_path: The file path to save the document data to.'''
        raise NotImplementedError()
    
    @overload
    def save(self, document : io._IOBase) -> groupdocs.watermark.internal.WatermarkResult:
        '''Saves the document to the specified stream.
        
        :param document: The stream to save the document data to.'''
        raise NotImplementedError()
    
    @overload
    def save(self, options : groupdocs.watermark.options.SaveOptions) -> groupdocs.watermark.internal.WatermarkResult:
        '''Saves the document data to the underlying stream using save options.
        
        :param options: Additional options to use when saving a document.'''
        raise NotImplementedError()
    
    @overload
    def save(self, file_path : str, options : groupdocs.watermark.options.SaveOptions) -> groupdocs.watermark.internal.WatermarkResult:
        '''Saves the document to the specified file location using save options.
        
        :param file_path: The file path to save the document data to.
        :param options: Additional options to use when saving a document.'''
        raise NotImplementedError()
    
    @overload
    def save(self, document : io._IOBase, options : groupdocs.watermark.options.SaveOptions) -> groupdocs.watermark.internal.WatermarkResult:
        '''Saves the document to the specified stream using save options.
        
        :param document: The stream to save the document data to.
        :param options: Additional options to use when saving a document.'''
        raise NotImplementedError()
    
    @overload
    def search(self) -> groupdocs.watermark.search.PossibleWatermarkCollection:
        '''Searches all possible watermarks in the document.
        
        :returns: The collection of possible watermarks.'''
        raise NotImplementedError()
    
    @overload
    def search(self, search_criteria : groupdocs.watermark.search.searchcriteria.SearchCriteria) -> groupdocs.watermark.search.PossibleWatermarkCollection:
        '''Searches possible watermarks according to specified search criteria.
        
        :param search_criteria: The search criteria to use.
        :returns: The collection of possible watermarks.'''
        raise NotImplementedError()
    
    @overload
    def get_images(self, search_criteria : groupdocs.watermark.search.searchcriteria.ImageSearchCriteria) -> groupdocs.watermark.contents.image.WatermarkableImageCollection:
        '''Finds images according to specified search criteria.
        
        :param search_criteria: The search criteria to use.
        :returns: The collection of found images.'''
        raise NotImplementedError()
    
    @overload
    def get_images(self) -> groupdocs.watermark.contents.image.WatermarkableImageCollection:
        '''Finds all images in the document.
        
        :returns: The collection of found images.'''
        raise NotImplementedError()
    
    def get_document_info(self) -> groupdocs.watermark.common.IDocumentInfo:
        '''Gets the information about the format of the loaded document.
        
        :returns: The :py:class:`groupdocs.watermark.common.IDocumentInfo` instance that contains detected information.'''
        raise NotImplementedError()
    
    def generate_preview(self, preview_options : groupdocs.watermark.options.PreviewOptions) -> None:
        '''Generates preview images for the document.
        
        :param preview_options: Additional options to use when generating preview images.'''
        raise NotImplementedError()
    
    @property
    def searchable_objects(self) -> groupdocs.watermark.search.objects.SearchableObjects:
        '''Gets the content objects that are to be included in a watermark search.'''
        raise NotImplementedError()
    
    @searchable_objects.setter
    def searchable_objects(self, value : groupdocs.watermark.search.objects.SearchableObjects) -> None:
        '''Sets the content objects that are to be included in a watermark search.'''
        raise NotImplementedError()
    

class WatermarkerSettings:
    '''Defines settings for customizing Watermarker behaviour.'''
    
    def __init__(self) -> None:
        '''Initializes new instance of :py:class:`groupdocs.watermark.WatermarkerSettings` class.'''
        raise NotImplementedError()
    
    @property
    def default(self) -> groupdocs.watermark.WatermarkerSettings:
        '''Gets the default value for the :py:class:`groupdocs.watermark.WatermarkerSettings` class.'''
        raise NotImplementedError()

    @property
    def searchable_objects(self) -> groupdocs.watermark.search.objects.SearchableObjects:
        '''Gets :py:attr:`groupdocs.watermark.WatermarkerSettings.searchable_objects` that are to be included in a watermark search.'''
        raise NotImplementedError()
    
    @searchable_objects.setter
    def searchable_objects(self, value : groupdocs.watermark.search.objects.SearchableObjects) -> None:
        '''Sets :py:attr:`groupdocs.watermark.WatermarkerSettings.searchable_objects` that are to be included in a watermark search.'''
        raise NotImplementedError()
    
    @property
    def logger(self) -> groupdocs.watermark.options.ILogger:
        '''Gets the logger which is used for logging events and errors during watermarking.'''
        raise NotImplementedError()
    
    @logger.setter
    def logger(self, value : groupdocs.watermark.options.ILogger) -> None:
        '''Sets the logger which is used for logging events and errors during watermarking.'''
        raise NotImplementedError()
    

class UnitOfMeasurement:
    '''Represents units of measurement.'''
    
    PIXEL : UnitOfMeasurement
    '''Specifies that the unit of measurement is pixel.'''
    POINT : UnitOfMeasurement
    '''Specifies that the unit of measurement is point.'''

