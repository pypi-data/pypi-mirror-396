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

class AndSearchCriteria(SearchCriteria):
    '''Represents AND composite search criteria.'''
    
    def both(self, other : groupdocs.watermark.search.searchcriteria.SearchCriteria) -> groupdocs.watermark.search.searchcriteria.SearchCriteria:
        '''Combines this :py:class:`groupdocs.watermark.search.searchcriteria.SearchCriteria` with other criteria using logical AND operator.
        
        :param other: Search criteria to combine with.
        :returns: Combined search criteria.'''
        raise NotImplementedError()
    
    def either(self, other : groupdocs.watermark.search.searchcriteria.SearchCriteria) -> groupdocs.watermark.search.searchcriteria.SearchCriteria:
        '''Combines this :py:class:`groupdocs.watermark.search.searchcriteria.SearchCriteria` with other criteria using logical OR operator.
        
        :param other: Search criteria to combine with.
        :returns: Combined search criteria.'''
        raise NotImplementedError()
    
    def is_not(self) -> groupdocs.watermark.search.searchcriteria.SearchCriteria:
        '''Negates this :py:class:`groupdocs.watermark.search.searchcriteria.SearchCriteria`.
        
        :returns: Combined search criteria.'''
        raise NotImplementedError()
    
    @property
    def right(self) -> groupdocs.watermark.search.searchcriteria.SearchCriteria:
        '''Gets the right search criteria.'''
        raise NotImplementedError()
    
    @property
    def left(self) -> groupdocs.watermark.search.searchcriteria.SearchCriteria:
        '''Gets the left search criteria.'''
        raise NotImplementedError()
    

class ColorRange:
    '''Represents a range of colors. Specifies ranges using HSB representation of RGB color.'''
    
    @overload
    def __init__(self) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.watermark.search.searchcriteria.ColorRange` class.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, exact_color : groupdocs.watermark.watermarks.Color) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.watermark.search.searchcriteria.ColorRange` class with a specified exact color.
        
        :param exact_color: The exact color from which the range is created.'''
        raise NotImplementedError()
    
    @property
    def min_hue(self) -> float:
        '''Gets the starting hue value, in degrees.'''
        raise NotImplementedError()
    
    @min_hue.setter
    def min_hue(self, value : float) -> None:
        '''Sets the starting hue value, in degrees.'''
        raise NotImplementedError()
    
    @property
    def max_hue(self) -> float:
        '''Gets the ending hue value, in degrees.'''
        raise NotImplementedError()
    
    @max_hue.setter
    def max_hue(self, value : float) -> None:
        '''Sets the ending hue value, in degrees.'''
        raise NotImplementedError()
    
    @property
    def min_saturation(self) -> float:
        '''Gets the starting saturation value.'''
        raise NotImplementedError()
    
    @min_saturation.setter
    def min_saturation(self, value : float) -> None:
        '''Sets the starting saturation value.'''
        raise NotImplementedError()
    
    @property
    def max_saturation(self) -> float:
        '''Gets the ending saturation value.'''
        raise NotImplementedError()
    
    @max_saturation.setter
    def max_saturation(self, value : float) -> None:
        '''Sets the ending saturation value.'''
        raise NotImplementedError()
    
    @property
    def min_brightness(self) -> float:
        '''Gets the starting brightness value.'''
        raise NotImplementedError()
    
    @min_brightness.setter
    def min_brightness(self, value : float) -> None:
        '''Sets the starting brightness value.'''
        raise NotImplementedError()
    
    @property
    def max_brightness(self) -> float:
        '''Gets the ending brightness value.'''
        raise NotImplementedError()
    
    @max_brightness.setter
    def max_brightness(self, value : float) -> None:
        '''Sets the ending brightness value.'''
        raise NotImplementedError()
    
    @property
    def is_empty(self) -> bool:
        '''Gets a value indicating whether only the empty color is in range.'''
        raise NotImplementedError()
    
    @is_empty.setter
    def is_empty(self, value : bool) -> None:
        '''Sets a value indicating whether only the empty color is in range.'''
        raise NotImplementedError()
    

class ImageColorHistogramSearchCriteria(ImageSearchCriteria):
    '''Represents search criteria for finding images in a content.'''
    
    @overload
    def __init__(self, file_path : str) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.watermark.search.searchcriteria.ImageColorHistogramSearchCriteria` class with a specified file path.
        
        :param file_path: The file path to load image from.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, stream : io._IOBase) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.watermark.search.searchcriteria.ImageColorHistogramSearchCriteria` class with a specified stream.
        
        :param stream: The stream to load image from.'''
        raise NotImplementedError()
    
    def both(self, other : groupdocs.watermark.search.searchcriteria.SearchCriteria) -> groupdocs.watermark.search.searchcriteria.SearchCriteria:
        '''Combines this :py:class:`groupdocs.watermark.search.searchcriteria.SearchCriteria` with other criteria using logical AND operator.
        
        :param other: Search criteria to combine with.
        :returns: Combined search criteria.'''
        raise NotImplementedError()
    
    def either(self, other : groupdocs.watermark.search.searchcriteria.SearchCriteria) -> groupdocs.watermark.search.searchcriteria.SearchCriteria:
        '''Combines this :py:class:`groupdocs.watermark.search.searchcriteria.SearchCriteria` with other criteria using logical OR operator.
        
        :param other: Search criteria to combine with.
        :returns: Combined search criteria.'''
        raise NotImplementedError()
    
    def is_not(self) -> groupdocs.watermark.search.searchcriteria.SearchCriteria:
        '''Negates this :py:class:`groupdocs.watermark.search.searchcriteria.SearchCriteria`.
        
        :returns: Combined search criteria.'''
        raise NotImplementedError()
    
    @property
    def pages(self) -> System.Collections.Generic.List`1[[System.Int32]]:
        '''Gets the list of specific page numbers'''
        raise NotImplementedError()
    
    @pages.setter
    def pages(self, value : System.Collections.Generic.List`1[[System.Int32]]) -> None:
        '''Sets the list of specific page numbers'''
        raise NotImplementedError()
    
    @property
    def max_difference(self) -> float:
        '''Gets maximum allowed difference between images.'''
        raise NotImplementedError()
    
    @max_difference.setter
    def max_difference(self, value : float) -> None:
        '''Sets maximum allowed difference between images.'''
        raise NotImplementedError()
    
    @property
    def bins_count(self) -> int:
        '''Gets a count of bins that will be used for building color histograms.'''
        raise NotImplementedError()
    
    @bins_count.setter
    def bins_count(self, value : int) -> None:
        '''Sets a count of bins that will be used for building color histograms.'''
        raise NotImplementedError()
    

class ImageDctHashSearchCriteria(ImageSearchCriteria):
    '''Represents a search criteria for finding images in a document.'''
    
    @overload
    def __init__(self, file_path : str) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.watermark.search.searchcriteria.ImageDctHashSearchCriteria` class with a specified file path.
        
        :param file_path: The file path to load image from.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, stream : io._IOBase) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.watermark.search.searchcriteria.ImageDctHashSearchCriteria` class with a specified stream.
        
        :param stream: The stream to load image from.'''
        raise NotImplementedError()
    
    def both(self, other : groupdocs.watermark.search.searchcriteria.SearchCriteria) -> groupdocs.watermark.search.searchcriteria.SearchCriteria:
        '''Combines this :py:class:`groupdocs.watermark.search.searchcriteria.SearchCriteria` with other criteria using logical AND operator.
        
        :param other: Search criteria to combine with.
        :returns: Combined search criteria.'''
        raise NotImplementedError()
    
    def either(self, other : groupdocs.watermark.search.searchcriteria.SearchCriteria) -> groupdocs.watermark.search.searchcriteria.SearchCriteria:
        '''Combines this :py:class:`groupdocs.watermark.search.searchcriteria.SearchCriteria` with other criteria using logical OR operator.
        
        :param other: Search criteria to combine with.
        :returns: Combined search criteria.'''
        raise NotImplementedError()
    
    def is_not(self) -> groupdocs.watermark.search.searchcriteria.SearchCriteria:
        '''Negates this :py:class:`groupdocs.watermark.search.searchcriteria.SearchCriteria`.
        
        :returns: Combined search criteria.'''
        raise NotImplementedError()
    
    @property
    def pages(self) -> System.Collections.Generic.List`1[[System.Int32]]:
        '''Gets the list of specific page numbers'''
        raise NotImplementedError()
    
    @pages.setter
    def pages(self, value : System.Collections.Generic.List`1[[System.Int32]]) -> None:
        '''Sets the list of specific page numbers'''
        raise NotImplementedError()
    
    @property
    def max_difference(self) -> float:
        '''Gets maximum allowed difference between images.'''
        raise NotImplementedError()
    
    @max_difference.setter
    def max_difference(self, value : float) -> None:
        '''Sets maximum allowed difference between images.'''
        raise NotImplementedError()
    

class ImageSearchCriteria(PageSearchCriteria):
    '''Provides base class for image search criteria.'''
    
    def both(self, other : groupdocs.watermark.search.searchcriteria.SearchCriteria) -> groupdocs.watermark.search.searchcriteria.SearchCriteria:
        '''Combines this :py:class:`groupdocs.watermark.search.searchcriteria.SearchCriteria` with other criteria using logical AND operator.
        
        :param other: Search criteria to combine with.
        :returns: Combined search criteria.'''
        raise NotImplementedError()
    
    def either(self, other : groupdocs.watermark.search.searchcriteria.SearchCriteria) -> groupdocs.watermark.search.searchcriteria.SearchCriteria:
        '''Combines this :py:class:`groupdocs.watermark.search.searchcriteria.SearchCriteria` with other criteria using logical OR operator.
        
        :param other: Search criteria to combine with.
        :returns: Combined search criteria.'''
        raise NotImplementedError()
    
    def is_not(self) -> groupdocs.watermark.search.searchcriteria.SearchCriteria:
        '''Negates this :py:class:`groupdocs.watermark.search.searchcriteria.SearchCriteria`.
        
        :returns: Combined search criteria.'''
        raise NotImplementedError()
    
    @property
    def pages(self) -> System.Collections.Generic.List`1[[System.Int32]]:
        '''Gets the list of specific page numbers'''
        raise NotImplementedError()
    
    @pages.setter
    def pages(self, value : System.Collections.Generic.List`1[[System.Int32]]) -> None:
        '''Sets the list of specific page numbers'''
        raise NotImplementedError()
    
    @property
    def max_difference(self) -> float:
        '''Gets maximum allowed difference between images.'''
        raise NotImplementedError()
    
    @max_difference.setter
    def max_difference(self, value : float) -> None:
        '''Sets maximum allowed difference between images.'''
        raise NotImplementedError()
    

class ImageThumbnailSearchCriteria(ImageSearchCriteria):
    '''Represents search criteria for finding images in a content.'''
    
    @overload
    def __init__(self, file_path : str) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.watermark.search.searchcriteria.ImageThumbnailSearchCriteria` class with a specified file path.
        
        :param file_path: The file path to load image from.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, stream : io._IOBase) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.watermark.search.searchcriteria.ImageThumbnailSearchCriteria` class with a specified stream.
        
        :param stream: The stream to load image from.'''
        raise NotImplementedError()
    
    def both(self, other : groupdocs.watermark.search.searchcriteria.SearchCriteria) -> groupdocs.watermark.search.searchcriteria.SearchCriteria:
        '''Combines this :py:class:`groupdocs.watermark.search.searchcriteria.SearchCriteria` with other criteria using logical AND operator.
        
        :param other: Search criteria to combine with.
        :returns: Combined search criteria.'''
        raise NotImplementedError()
    
    def either(self, other : groupdocs.watermark.search.searchcriteria.SearchCriteria) -> groupdocs.watermark.search.searchcriteria.SearchCriteria:
        '''Combines this :py:class:`groupdocs.watermark.search.searchcriteria.SearchCriteria` with other criteria using logical OR operator.
        
        :param other: Search criteria to combine with.
        :returns: Combined search criteria.'''
        raise NotImplementedError()
    
    def is_not(self) -> groupdocs.watermark.search.searchcriteria.SearchCriteria:
        '''Negates this :py:class:`groupdocs.watermark.search.searchcriteria.SearchCriteria`.
        
        :returns: Combined search criteria.'''
        raise NotImplementedError()
    
    @property
    def pages(self) -> System.Collections.Generic.List`1[[System.Int32]]:
        '''Gets the list of specific page numbers'''
        raise NotImplementedError()
    
    @pages.setter
    def pages(self, value : System.Collections.Generic.List`1[[System.Int32]]) -> None:
        '''Sets the list of specific page numbers'''
        raise NotImplementedError()
    
    @property
    def max_difference(self) -> float:
        '''Gets maximum allowed difference between images.'''
        raise NotImplementedError()
    
    @max_difference.setter
    def max_difference(self, value : float) -> None:
        '''Sets maximum allowed difference between images.'''
        raise NotImplementedError()
    
    @property
    def thumbnail_size(self) -> int:
        '''Gets thumbnail size.'''
        raise NotImplementedError()
    
    @thumbnail_size.setter
    def thumbnail_size(self, value : int) -> None:
        '''Sets thumbnail size.'''
        raise NotImplementedError()
    

class IsImageSearchCriteria(SearchCriteria):
    '''Represents search criteria for filtering image watermarks only.'''
    
    def __init__(self) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.watermark.search.searchcriteria.IsImageSearchCriteria` class.'''
        raise NotImplementedError()
    
    def both(self, other : groupdocs.watermark.search.searchcriteria.SearchCriteria) -> groupdocs.watermark.search.searchcriteria.SearchCriteria:
        '''Combines this :py:class:`groupdocs.watermark.search.searchcriteria.SearchCriteria` with other criteria using logical AND operator.
        
        :param other: Search criteria to combine with.
        :returns: Combined search criteria.'''
        raise NotImplementedError()
    
    def either(self, other : groupdocs.watermark.search.searchcriteria.SearchCriteria) -> groupdocs.watermark.search.searchcriteria.SearchCriteria:
        '''Combines this :py:class:`groupdocs.watermark.search.searchcriteria.SearchCriteria` with other criteria using logical OR operator.
        
        :param other: Search criteria to combine with.
        :returns: Combined search criteria.'''
        raise NotImplementedError()
    
    def is_not(self) -> groupdocs.watermark.search.searchcriteria.SearchCriteria:
        '''Negates this :py:class:`groupdocs.watermark.search.searchcriteria.SearchCriteria`.
        
        :returns: Combined search criteria.'''
        raise NotImplementedError()
    

class IsTextSearchCriteria(SearchCriteria):
    '''Represents search criteria for filtering text watermarks only.'''
    
    def __init__(self) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.watermark.search.searchcriteria.IsTextSearchCriteria` class.'''
        raise NotImplementedError()
    
    def both(self, other : groupdocs.watermark.search.searchcriteria.SearchCriteria) -> groupdocs.watermark.search.searchcriteria.SearchCriteria:
        '''Combines this :py:class:`groupdocs.watermark.search.searchcriteria.SearchCriteria` with other criteria using logical AND operator.
        
        :param other: Search criteria to combine with.
        :returns: Combined search criteria.'''
        raise NotImplementedError()
    
    def either(self, other : groupdocs.watermark.search.searchcriteria.SearchCriteria) -> groupdocs.watermark.search.searchcriteria.SearchCriteria:
        '''Combines this :py:class:`groupdocs.watermark.search.searchcriteria.SearchCriteria` with other criteria using logical OR operator.
        
        :param other: Search criteria to combine with.
        :returns: Combined search criteria.'''
        raise NotImplementedError()
    
    def is_not(self) -> groupdocs.watermark.search.searchcriteria.SearchCriteria:
        '''Negates this :py:class:`groupdocs.watermark.search.searchcriteria.SearchCriteria`.
        
        :returns: Combined search criteria.'''
        raise NotImplementedError()
    

class NotSearchCriteria(SearchCriteria):
    '''Represents NOT composite search criteria.'''
    
    def both(self, other : groupdocs.watermark.search.searchcriteria.SearchCriteria) -> groupdocs.watermark.search.searchcriteria.SearchCriteria:
        '''Combines this :py:class:`groupdocs.watermark.search.searchcriteria.SearchCriteria` with other criteria using logical AND operator.
        
        :param other: Search criteria to combine with.
        :returns: Combined search criteria.'''
        raise NotImplementedError()
    
    def either(self, other : groupdocs.watermark.search.searchcriteria.SearchCriteria) -> groupdocs.watermark.search.searchcriteria.SearchCriteria:
        '''Combines this :py:class:`groupdocs.watermark.search.searchcriteria.SearchCriteria` with other criteria using logical OR operator.
        
        :param other: Search criteria to combine with.
        :returns: Combined search criteria.'''
        raise NotImplementedError()
    
    def is_not(self) -> groupdocs.watermark.search.searchcriteria.SearchCriteria:
        '''Negates this :py:class:`groupdocs.watermark.search.searchcriteria.SearchCriteria`.
        
        :returns: Combined search criteria.'''
        raise NotImplementedError()
    

class OrSearchCriteria(SearchCriteria):
    '''Represents OR composite search criteria.'''
    
    def both(self, other : groupdocs.watermark.search.searchcriteria.SearchCriteria) -> groupdocs.watermark.search.searchcriteria.SearchCriteria:
        '''Combines this :py:class:`groupdocs.watermark.search.searchcriteria.SearchCriteria` with other criteria using logical AND operator.
        
        :param other: Search criteria to combine with.
        :returns: Combined search criteria.'''
        raise NotImplementedError()
    
    def either(self, other : groupdocs.watermark.search.searchcriteria.SearchCriteria) -> groupdocs.watermark.search.searchcriteria.SearchCriteria:
        '''Combines this :py:class:`groupdocs.watermark.search.searchcriteria.SearchCriteria` with other criteria using logical OR operator.
        
        :param other: Search criteria to combine with.
        :returns: Combined search criteria.'''
        raise NotImplementedError()
    
    def is_not(self) -> groupdocs.watermark.search.searchcriteria.SearchCriteria:
        '''Negates this :py:class:`groupdocs.watermark.search.searchcriteria.SearchCriteria`.
        
        :returns: Combined search criteria.'''
        raise NotImplementedError()
    
    @property
    def left(self) -> groupdocs.watermark.search.searchcriteria.SearchCriteria:
        '''Gets the left search criteria.'''
        raise NotImplementedError()
    
    @property
    def right(self) -> groupdocs.watermark.search.searchcriteria.SearchCriteria:
        '''Gets the right search criteria.'''
        raise NotImplementedError()
    

class PageSearchCriteria(SearchCriteria):
    '''Represents criteria allowing filtering by page number'''
    
    def both(self, other : groupdocs.watermark.search.searchcriteria.SearchCriteria) -> groupdocs.watermark.search.searchcriteria.SearchCriteria:
        '''Combines this :py:class:`groupdocs.watermark.search.searchcriteria.SearchCriteria` with other criteria using logical AND operator.
        
        :param other: Search criteria to combine with.
        :returns: Combined search criteria.'''
        raise NotImplementedError()
    
    def either(self, other : groupdocs.watermark.search.searchcriteria.SearchCriteria) -> groupdocs.watermark.search.searchcriteria.SearchCriteria:
        '''Combines this :py:class:`groupdocs.watermark.search.searchcriteria.SearchCriteria` with other criteria using logical OR operator.
        
        :param other: Search criteria to combine with.
        :returns: Combined search criteria.'''
        raise NotImplementedError()
    
    def is_not(self) -> groupdocs.watermark.search.searchcriteria.SearchCriteria:
        '''Negates this :py:class:`groupdocs.watermark.search.searchcriteria.SearchCriteria`.
        
        :returns: Combined search criteria.'''
        raise NotImplementedError()
    
    @property
    def pages(self) -> System.Collections.Generic.List`1[[System.Int32]]:
        '''Gets the list of specific page numbers'''
        raise NotImplementedError()
    
    @pages.setter
    def pages(self, value : System.Collections.Generic.List`1[[System.Int32]]) -> None:
        '''Sets the list of specific page numbers'''
        raise NotImplementedError()
    

class RotateAngleSearchCriteria(SearchCriteria):
    '''Represents criteria allowing filtering by watermark rotate angle.'''
    
    def __init__(self, min_angle : float, max_angle : float) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.watermark.search.searchcriteria.RotateAngleSearchCriteria` class
        with a starting angle and a ending angle.
        
        :param min_angle: The starting angle in degrees.
        :param max_angle: The ending angle in degrees.'''
        raise NotImplementedError()
    
    def both(self, other : groupdocs.watermark.search.searchcriteria.SearchCriteria) -> groupdocs.watermark.search.searchcriteria.SearchCriteria:
        '''Combines this :py:class:`groupdocs.watermark.search.searchcriteria.SearchCriteria` with other criteria using logical AND operator.
        
        :param other: Search criteria to combine with.
        :returns: Combined search criteria.'''
        raise NotImplementedError()
    
    def either(self, other : groupdocs.watermark.search.searchcriteria.SearchCriteria) -> groupdocs.watermark.search.searchcriteria.SearchCriteria:
        '''Combines this :py:class:`groupdocs.watermark.search.searchcriteria.SearchCriteria` with other criteria using logical OR operator.
        
        :param other: Search criteria to combine with.
        :returns: Combined search criteria.'''
        raise NotImplementedError()
    
    def is_not(self) -> groupdocs.watermark.search.searchcriteria.SearchCriteria:
        '''Negates this :py:class:`groupdocs.watermark.search.searchcriteria.SearchCriteria`.
        
        :returns: Combined search criteria.'''
        raise NotImplementedError()
    
    @property
    def minimum_angle(self) -> float:
        '''Gets the starting angle in degrees.'''
        raise NotImplementedError()
    
    @property
    def maximum_angle(self) -> float:
        '''Gets the ending angle in degrees.'''
        raise NotImplementedError()
    

class SearchCriteria:
    '''Class that can be used to construct criteria when searching for watermarks.'''
    
    def both(self, other : groupdocs.watermark.search.searchcriteria.SearchCriteria) -> groupdocs.watermark.search.searchcriteria.SearchCriteria:
        '''Combines this :py:class:`groupdocs.watermark.search.searchcriteria.SearchCriteria` with other criteria using logical AND operator.
        
        :param other: Search criteria to combine with.
        :returns: Combined search criteria.'''
        raise NotImplementedError()
    
    def either(self, other : groupdocs.watermark.search.searchcriteria.SearchCriteria) -> groupdocs.watermark.search.searchcriteria.SearchCriteria:
        '''Combines this :py:class:`groupdocs.watermark.search.searchcriteria.SearchCriteria` with other criteria using logical OR operator.
        
        :param other: Search criteria to combine with.
        :returns: Combined search criteria.'''
        raise NotImplementedError()
    
    def is_not(self) -> groupdocs.watermark.search.searchcriteria.SearchCriteria:
        '''Negates this :py:class:`groupdocs.watermark.search.searchcriteria.SearchCriteria`.
        
        :returns: Combined search criteria.'''
        raise NotImplementedError()
    

class SizeSearchCriteria(SearchCriteria):
    '''Represents criteria allowing filtering by watermark size.'''
    
    def __init__(self, dimension : groupdocs.watermark.common.Dimension, min : float, max : float) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.watermark.search.searchcriteria.SizeSearchCriteria` class
        with a specified dimension, a starting value and an ending value.
        
        :param dimension: The dimension of a watermark to search by.
        :param min: The starting value.
        :param max: The ending value.'''
        raise NotImplementedError()
    
    def both(self, other : groupdocs.watermark.search.searchcriteria.SearchCriteria) -> groupdocs.watermark.search.searchcriteria.SearchCriteria:
        '''Combines this :py:class:`groupdocs.watermark.search.searchcriteria.SearchCriteria` with other criteria using logical AND operator.
        
        :param other: Search criteria to combine with.
        :returns: Combined search criteria.'''
        raise NotImplementedError()
    
    def either(self, other : groupdocs.watermark.search.searchcriteria.SearchCriteria) -> groupdocs.watermark.search.searchcriteria.SearchCriteria:
        '''Combines this :py:class:`groupdocs.watermark.search.searchcriteria.SearchCriteria` with other criteria using logical OR operator.
        
        :param other: Search criteria to combine with.
        :returns: Combined search criteria.'''
        raise NotImplementedError()
    
    def is_not(self) -> groupdocs.watermark.search.searchcriteria.SearchCriteria:
        '''Negates this :py:class:`groupdocs.watermark.search.searchcriteria.SearchCriteria`.
        
        :returns: Combined search criteria.'''
        raise NotImplementedError()
    
    @property
    def minimum(self) -> float:
        '''Gets the starting value.'''
        raise NotImplementedError()
    
    @property
    def maximum(self) -> float:
        '''Gets the ending value.'''
        raise NotImplementedError()
    
    @property
    def dimension(self) -> groupdocs.watermark.common.Dimension:
        '''Gets the dimension of watermark to search by.'''
        raise NotImplementedError()
    

class TextFormattingSearchCriteria(SearchCriteria):
    '''Represents criteria allowing filtering by text formatting.'''
    
    def __init__(self) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.watermark.search.searchcriteria.TextFormattingSearchCriteria` class.'''
        raise NotImplementedError()
    
    def both(self, other : groupdocs.watermark.search.searchcriteria.SearchCriteria) -> groupdocs.watermark.search.searchcriteria.SearchCriteria:
        '''Combines this :py:class:`groupdocs.watermark.search.searchcriteria.SearchCriteria` with other criteria using logical AND operator.
        
        :param other: Search criteria to combine with.
        :returns: Combined search criteria.'''
        raise NotImplementedError()
    
    def either(self, other : groupdocs.watermark.search.searchcriteria.SearchCriteria) -> groupdocs.watermark.search.searchcriteria.SearchCriteria:
        '''Combines this :py:class:`groupdocs.watermark.search.searchcriteria.SearchCriteria` with other criteria using logical OR operator.
        
        :param other: Search criteria to combine with.
        :returns: Combined search criteria.'''
        raise NotImplementedError()
    
    def is_not(self) -> groupdocs.watermark.search.searchcriteria.SearchCriteria:
        '''Negates this :py:class:`groupdocs.watermark.search.searchcriteria.SearchCriteria`.
        
        :returns: Combined search criteria.'''
        raise NotImplementedError()
    
    @property
    def foreground_color_range(self) -> groupdocs.watermark.search.searchcriteria.ColorRange:
        '''Gets the range of colors which are used to filter watermarks by text foreground color.'''
        raise NotImplementedError()
    
    @foreground_color_range.setter
    def foreground_color_range(self, value : groupdocs.watermark.search.searchcriteria.ColorRange) -> None:
        '''Sets the range of colors which are used to filter watermarks by text foreground color.'''
        raise NotImplementedError()
    
    @property
    def background_color_range(self) -> groupdocs.watermark.search.searchcriteria.ColorRange:
        '''Gets the range of colors which are used to filter watermarks by text background color.'''
        raise NotImplementedError()
    
    @background_color_range.setter
    def background_color_range(self, value : groupdocs.watermark.search.searchcriteria.ColorRange) -> None:
        '''Sets the range of colors which are used to filter watermarks by text background color.'''
        raise NotImplementedError()
    
    @property
    def font_name(self) -> str:
        '''Gets the name of the font which is used in possible watermark text formatting.'''
        raise NotImplementedError()
    
    @font_name.setter
    def font_name(self, value : str) -> None:
        '''Sets the name of the font which is used in possible watermark text formatting.'''
        raise NotImplementedError()
    
    @property
    def min_font_size(self) -> float:
        '''Gets the starting value of the font size.'''
        raise NotImplementedError()
    
    @min_font_size.setter
    def min_font_size(self, value : float) -> None:
        '''Sets the starting value of the font size.'''
        raise NotImplementedError()
    
    @property
    def max_font_size(self) -> float:
        '''Gets the ending value of the font size.'''
        raise NotImplementedError()
    
    @max_font_size.setter
    def max_font_size(self, value : float) -> None:
        '''Sets the ending value of the font size.'''
        raise NotImplementedError()
    
    @property
    def font_bold(self) -> System.Nullable`1[[System.Boolean]]:
        '''Gets a value indicating whether the font used in watermark text formatting is bold.'''
        raise NotImplementedError()
    
    @font_bold.setter
    def font_bold(self, value : System.Nullable`1[[System.Boolean]]) -> None:
        '''Sets a value indicating whether the font used in watermark text formatting is bold.'''
        raise NotImplementedError()
    
    @property
    def font_italic(self) -> System.Nullable`1[[System.Boolean]]:
        '''Gets a value indicating whether the font used in watermark text formatting is italic.'''
        raise NotImplementedError()
    
    @font_italic.setter
    def font_italic(self, value : System.Nullable`1[[System.Boolean]]) -> None:
        '''Sets a value indicating whether the font used in watermark text formatting is italic.'''
        raise NotImplementedError()
    
    @property
    def font_underline(self) -> System.Nullable`1[[System.Boolean]]:
        '''Gets a value indicating whether the font used in watermark text formatting is underline.'''
        raise NotImplementedError()
    
    @font_underline.setter
    def font_underline(self, value : System.Nullable`1[[System.Boolean]]) -> None:
        '''Sets a value indicating whether the font used in watermark text formatting is underline.'''
        raise NotImplementedError()
    
    @property
    def font_strikeout(self) -> System.Nullable`1[[System.Boolean]]:
        '''Gets a value indicating whether the font used in watermark text formatting is strikeout.'''
        raise NotImplementedError()
    
    @font_strikeout.setter
    def font_strikeout(self, value : System.Nullable`1[[System.Boolean]]) -> None:
        '''Sets a value indicating whether the font used in watermark text formatting is strikeout.'''
        raise NotImplementedError()
    

class TextSearchCriteria(PageSearchCriteria):
    '''Represents criteria allowing filtering by watermark text.'''
    
    @overload
    def __init__(self, search_string : str, is_match_case : bool) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.watermark.search.searchcriteria.TextSearchCriteria` class
        with a search string and a flag for comparison.
        
        :param search_string: The exact string to search for.
        :param is_match_case: false
        to ignore case during the comparison; otherwise,     true
        .'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, search_string : str) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.watermark.search.searchcriteria.TextSearchCriteria` class with a search string.
        
        :param search_string: The exact string to search for.'''
        raise NotImplementedError()
    
    def both(self, other : groupdocs.watermark.search.searchcriteria.SearchCriteria) -> groupdocs.watermark.search.searchcriteria.SearchCriteria:
        '''Combines this :py:class:`groupdocs.watermark.search.searchcriteria.SearchCriteria` with other criteria using logical AND operator.
        
        :param other: Search criteria to combine with.
        :returns: Combined search criteria.'''
        raise NotImplementedError()
    
    def either(self, other : groupdocs.watermark.search.searchcriteria.SearchCriteria) -> groupdocs.watermark.search.searchcriteria.SearchCriteria:
        '''Combines this :py:class:`groupdocs.watermark.search.searchcriteria.SearchCriteria` with other criteria using logical OR operator.
        
        :param other: Search criteria to combine with.
        :returns: Combined search criteria.'''
        raise NotImplementedError()
    
    def is_not(self) -> groupdocs.watermark.search.searchcriteria.SearchCriteria:
        '''Negates this :py:class:`groupdocs.watermark.search.searchcriteria.SearchCriteria`.
        
        :returns: Combined search criteria.'''
        raise NotImplementedError()
    
    @property
    def pages(self) -> System.Collections.Generic.List`1[[System.Int32]]:
        '''Gets the list of specific page numbers'''
        raise NotImplementedError()
    
    @pages.setter
    def pages(self, value : System.Collections.Generic.List`1[[System.Int32]]) -> None:
        '''Sets the list of specific page numbers'''
        raise NotImplementedError()
    
    @property
    def skip_unreadable_characters(self) -> bool:
        '''Gets a value indicating that unreadable characters will be skipped during string comparison.'''
        raise NotImplementedError()
    
    @skip_unreadable_characters.setter
    def skip_unreadable_characters(self, value : bool) -> None:
        '''Sets a value indicating that unreadable characters will be skipped during string comparison.'''
        raise NotImplementedError()
    

class VectorSearchCriteria(SearchCriteria):
    '''Represents criteria allowing filtering by watermark color.'''
    
    def __init__(self) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.watermark.search.searchcriteria.VectorSearchCriteria` class.'''
        raise NotImplementedError()
    
    def both(self, other : groupdocs.watermark.search.searchcriteria.SearchCriteria) -> groupdocs.watermark.search.searchcriteria.SearchCriteria:
        '''Combines this :py:class:`groupdocs.watermark.search.searchcriteria.SearchCriteria` with other criteria using logical AND operator.
        
        :param other: Search criteria to combine with.
        :returns: Combined search criteria.'''
        raise NotImplementedError()
    
    def either(self, other : groupdocs.watermark.search.searchcriteria.SearchCriteria) -> groupdocs.watermark.search.searchcriteria.SearchCriteria:
        '''Combines this :py:class:`groupdocs.watermark.search.searchcriteria.SearchCriteria` with other criteria using logical OR operator.
        
        :param other: Search criteria to combine with.
        :returns: Combined search criteria.'''
        raise NotImplementedError()
    
    def is_not(self) -> groupdocs.watermark.search.searchcriteria.SearchCriteria:
        '''Negates this :py:class:`groupdocs.watermark.search.searchcriteria.SearchCriteria`.
        
        :returns: Combined search criteria.'''
        raise NotImplementedError()
    
    @property
    def vector_color_range(self) -> groupdocs.watermark.search.searchcriteria.ColorRange:
        '''Gets the range of colors which are used to filter vector watermarks by foreground color.'''
        raise NotImplementedError()
    
    @vector_color_range.setter
    def vector_color_range(self, value : groupdocs.watermark.search.searchcriteria.ColorRange) -> None:
        '''Sets the range of colors which are used to filter vector watermarks by foreground color.'''
        raise NotImplementedError()
    

