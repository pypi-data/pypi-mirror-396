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

class DiagramCommentPossibleWatermark(groupdocs.watermark.search.PossibleWatermark):
    '''Represents possible watermark in a Visio document comment.'''
    
    @property
    def parent(self) -> groupdocs.watermark.contents.ContentPart:
        '''Gets the parent of this :py:class:`groupdocs.watermark.search.watermarks.DiagramCommentPossibleWatermark`.'''
        raise NotImplementedError()
    
    @property
    def page_number(self) -> System.Nullable`1[[System.Int32]]:
        '''Gets the page watermark is placed on.'''
        raise NotImplementedError()
    
    @property
    def width(self) -> float:
        '''Gets the width of this :py:class:`groupdocs.watermark.search.watermarks.DiagramCommentPossibleWatermark` in points.'''
        raise NotImplementedError()
    
    @property
    def height(self) -> float:
        '''Gets the height of this :py:class:`groupdocs.watermark.search.watermarks.DiagramCommentPossibleWatermark` in points.'''
        raise NotImplementedError()
    
    @property
    def x(self) -> float:
        '''Gets the horizontal offset of this :py:class:`groupdocs.watermark.search.watermarks.DiagramCommentPossibleWatermark`
        from page left border in points.'''
        raise NotImplementedError()
    
    @property
    def y(self) -> float:
        '''Gets the vertical offset of this :py:class:`groupdocs.watermark.search.watermarks.DiagramCommentPossibleWatermark`
        from page bottom border in points.'''
        raise NotImplementedError()
    
    @property
    def rotate_angle(self) -> float:
        '''Gets the rotate angle of this :py:class:`groupdocs.watermark.search.watermarks.DiagramCommentPossibleWatermark` in degrees.'''
        raise NotImplementedError()
    
    @property
    def text(self) -> str:
        '''Gets the text of this :py:class:`groupdocs.watermark.search.watermarks.DiagramCommentPossibleWatermark`.'''
        raise NotImplementedError()
    
    @text.setter
    def text(self, value : str) -> None:
        '''Sets the text of this :py:class:`groupdocs.watermark.search.watermarks.DiagramCommentPossibleWatermark`.'''
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
        '''Gets the unit of measurement of this :py:class:`groupdocs.watermark.search.watermarks.DiagramCommentPossibleWatermark`.'''
        raise NotImplementedError()
    

class DiagramHeaderFooterPossibleWatermark(groupdocs.watermark.search.PossibleWatermark):
    '''Represents possible watermark in a Visio document header/footer.'''
    
    @property
    def parent(self) -> groupdocs.watermark.contents.ContentPart:
        '''Gets the parent of this :py:class:`groupdocs.watermark.search.watermarks.DiagramHeaderFooterPossibleWatermark`.'''
        raise NotImplementedError()
    
    @property
    def page_number(self) -> System.Nullable`1[[System.Int32]]:
        '''Gets the page watermark is placed on.'''
        raise NotImplementedError()
    
    @property
    def width(self) -> float:
        '''Gets the width of this :py:class:`groupdocs.watermark.search.watermarks.DiagramHeaderFooterPossibleWatermark` in points.'''
        raise NotImplementedError()
    
    @property
    def height(self) -> float:
        '''Gets the height of this :py:class:`groupdocs.watermark.search.watermarks.DiagramHeaderFooterPossibleWatermark` in points.'''
        raise NotImplementedError()
    
    @property
    def x(self) -> float:
        '''Gets the horizontal offset of this :py:class:`groupdocs.watermark.search.watermarks.DiagramHeaderFooterPossibleWatermark`
        from page left border in points.'''
        raise NotImplementedError()
    
    @property
    def y(self) -> float:
        '''Gets the vertical offset of this :py:class:`groupdocs.watermark.search.watermarks.DiagramHeaderFooterPossibleWatermark`
        from page bottom border in points.'''
        raise NotImplementedError()
    
    @property
    def rotate_angle(self) -> float:
        '''Gets the rotate angle of this :py:class:`groupdocs.watermark.search.watermarks.DiagramHeaderFooterPossibleWatermark` in degrees.'''
        raise NotImplementedError()
    
    @property
    def text(self) -> str:
        '''Gets the text of this :py:class:`groupdocs.watermark.search.watermarks.DiagramHeaderFooterPossibleWatermark`.'''
        raise NotImplementedError()
    
    @text.setter
    def text(self, value : str) -> None:
        '''Sets the text of this :py:class:`groupdocs.watermark.search.watermarks.DiagramHeaderFooterPossibleWatermark`.'''
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
        '''Gets the unit of measurement of this :py:class:`groupdocs.watermark.search.watermarks.DiagramHeaderFooterPossibleWatermark`.'''
        raise NotImplementedError()
    

class DiagramHyperlinkPossibleWatermark(groupdocs.watermark.search.HyperlinkPossibleWatermark):
    '''Represents possible hyperlink watermark in a Visio document.'''
    
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
        '''Gets the url of this :py:class:`groupdocs.watermark.search.watermarks.DiagramHyperlinkPossibleWatermark`.'''
        raise NotImplementedError()
    
    @text.setter
    def text(self, value : str) -> None:
        '''Sets the url of this :py:class:`groupdocs.watermark.search.watermarks.DiagramHyperlinkPossibleWatermark`.'''
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
    

class DiagramShapePossibleWatermark(groupdocs.watermark.search.TwoDObjectPossibleWatermark):
    '''Represents possible shape watermark in a Visio document.'''
    
    @property
    def parent(self) -> groupdocs.watermark.contents.ContentPart:
        '''Gets the parent of this :py:class:`groupdocs.watermark.search.watermarks.DiagramShapePossibleWatermark`.'''
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
    

class EmailAttachedImagePossibleWatermark(groupdocs.watermark.search.PossibleWatermark):
    '''Represents possible image watermark in email message attachment.'''
    
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
    

class EmailBodyTextPossibleWatermark(EmailTextPossibleWatermark):
    '''Represents possible watermark in email message body.'''
    
    @property
    def parent(self) -> groupdocs.watermark.contents.ContentPart:
        '''Gets the parent of this :py:class:`groupdocs.watermark.search.watermarks.EmailTextPossibleWatermark`.'''
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
        '''Gets the text of this :py:class:`groupdocs.watermark.search.watermarks.EmailTextPossibleWatermark`.'''
        raise NotImplementedError()
    
    @text.setter
    def text(self, value : str) -> None:
        '''Sets the text of this :py:class:`groupdocs.watermark.search.watermarks.EmailTextPossibleWatermark`.'''
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
    

class EmailEmbeddedImagePossibleWatermark(groupdocs.watermark.search.PossibleWatermark):
    '''Represents possible image watermark embedded to email message body.'''
    
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
    

class EmailHtmlBodyTextPossibleWatermark(EmailTextPossibleWatermark):
    '''Represents possible watermark in email message html body.'''
    
    @property
    def parent(self) -> groupdocs.watermark.contents.ContentPart:
        '''Gets the parent of this :py:class:`groupdocs.watermark.search.watermarks.EmailTextPossibleWatermark`.'''
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
        '''Gets the text of this :py:class:`groupdocs.watermark.search.watermarks.EmailTextPossibleWatermark`.'''
        raise NotImplementedError()
    
    @text.setter
    def text(self, value : str) -> None:
        '''Sets the text of this :py:class:`groupdocs.watermark.search.watermarks.EmailTextPossibleWatermark`.'''
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
    

class EmailSubjectTextPossibleWatermark(EmailTextPossibleWatermark):
    '''Represents possible watermark in email message subject.'''
    
    @property
    def parent(self) -> groupdocs.watermark.contents.ContentPart:
        '''Gets the parent of this :py:class:`groupdocs.watermark.search.watermarks.EmailTextPossibleWatermark`.'''
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
        '''Gets the text of this :py:class:`groupdocs.watermark.search.watermarks.EmailTextPossibleWatermark`.'''
        raise NotImplementedError()
    
    @text.setter
    def text(self, value : str) -> None:
        '''Sets the text of this :py:class:`groupdocs.watermark.search.watermarks.EmailTextPossibleWatermark`.'''
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
    

class EmailTextPossibleWatermark(groupdocs.watermark.search.PossibleWatermark):
    '''Represents possible watermark in email message text fields.'''
    
    @property
    def parent(self) -> groupdocs.watermark.contents.ContentPart:
        '''Gets the parent of this :py:class:`groupdocs.watermark.search.watermarks.EmailTextPossibleWatermark`.'''
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
        '''Gets the text of this :py:class:`groupdocs.watermark.search.watermarks.EmailTextPossibleWatermark`.'''
        raise NotImplementedError()
    
    @text.setter
    def text(self, value : str) -> None:
        '''Sets the text of this :py:class:`groupdocs.watermark.search.watermarks.EmailTextPossibleWatermark`.'''
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
    

class PdfAnnotationPossibleWatermark(groupdocs.watermark.search.TwoDObjectPossibleWatermark):
    '''Represents possible annotation watermark in a pdf document.'''
    
    @property
    def parent(self) -> groupdocs.watermark.contents.ContentPart:
        '''Gets the parent of this :py:class:`groupdocs.watermark.search.watermarks.PdfAnnotationPossibleWatermark`.'''
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
    

class PdfArtifactPossibleWatermark(groupdocs.watermark.search.TwoDObjectPossibleWatermark):
    '''Represents possible artifact watermark in a pdf content.'''
    
    @property
    def parent(self) -> groupdocs.watermark.contents.ContentPart:
        '''Gets the parent of this :py:class:`groupdocs.watermark.search.watermarks.PdfArtifactPossibleWatermark`.'''
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
    

class PdfAttachedImagePossibleWatermark(groupdocs.watermark.search.PossibleWatermark):
    '''Represents possible image watermark in pdf document attachment.'''
    
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
    

class PdfHyperlinkPossibleWatermark(groupdocs.watermark.search.HyperlinkPossibleWatermark):
    '''Represents possible hyperlink watermark in a pdf document.'''
    
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
        '''Gets the url of this :py:class:`groupdocs.watermark.search.watermarks.PdfHyperlinkPossibleWatermark`.'''
        raise NotImplementedError()
    
    @text.setter
    def text(self, value : str) -> None:
        '''Sets the url of this :py:class:`groupdocs.watermark.search.watermarks.PdfHyperlinkPossibleWatermark`.'''
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
    

class PdfTextPossibleWatermark(groupdocs.watermark.search.PossibleWatermark):
    '''Represents possible watermark in a pdf document text.'''
    
    @property
    def parent(self) -> groupdocs.watermark.contents.ContentPart:
        '''Gets the parent of this :py:class:`groupdocs.watermark.search.watermarks.PdfTextPossibleWatermark`.'''
        raise NotImplementedError()
    
    @property
    def page_number(self) -> System.Nullable`1[[System.Int32]]:
        '''Gets the page watermark is placed on.'''
        raise NotImplementedError()
    
    @property
    def width(self) -> float:
        '''Gets the width of this :py:class:`groupdocs.watermark.search.watermarks.PdfTextPossibleWatermark` in points.'''
        raise NotImplementedError()
    
    @property
    def height(self) -> float:
        '''Gets the height of this :py:class:`groupdocs.watermark.search.watermarks.PdfTextPossibleWatermark` in points.'''
        raise NotImplementedError()
    
    @property
    def x(self) -> float:
        '''Gets the horizontal offset of this :py:class:`groupdocs.watermark.search.watermarks.PdfTextPossibleWatermark`
        from page left border in points.'''
        raise NotImplementedError()
    
    @property
    def y(self) -> float:
        '''Gets the vertical offset of this :py:class:`groupdocs.watermark.search.watermarks.PdfTextPossibleWatermark`
        from page bottom border in points.'''
        raise NotImplementedError()
    
    @property
    def rotate_angle(self) -> float:
        '''Gets the rotate angle of this :py:class:`groupdocs.watermark.search.watermarks.PdfTextPossibleWatermark` in degrees.'''
        raise NotImplementedError()
    
    @property
    def text(self) -> str:
        '''Gets the text of this :py:class:`groupdocs.watermark.search.watermarks.PdfTextPossibleWatermark`.'''
        raise NotImplementedError()
    
    @text.setter
    def text(self, value : str) -> None:
        '''Sets the text of this :py:class:`groupdocs.watermark.search.watermarks.PdfTextPossibleWatermark`.'''
        raise NotImplementedError()
    
    @property
    def formatted_text_fragments(self) -> groupdocs.watermark.search.FormattedTextFragmentCollection:
        '''Gets the collection of formatted text fragments of this :py:class:`groupdocs.watermark.search.watermarks.PdfTextPossibleWatermark`.'''
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
        '''Gets the unit of measurement of this :py:class:`groupdocs.watermark.search.watermarks.PdfTextPossibleWatermark`.'''
        raise NotImplementedError()
    

class PdfVectorPossibleWatermark(groupdocs.watermark.search.PossibleWatermark):
    '''Represents possible vector watermark in a pdf document.'''
    
    @property
    def parent(self) -> groupdocs.watermark.contents.ContentPart:
        '''Gets the parent of this :py:class:`groupdocs.watermark.search.watermarks.PdfVectorPossibleWatermark`.'''
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
    
    @property
    def pdf_operator_collection(self) -> groupdocs.watermark.contents.pdf.PdfOperatorCollection:
        '''Gets the collection of vector operators of this :py:class:`groupdocs.watermark.search.watermarks.PdfVectorPossibleWatermark`.'''
        raise NotImplementedError()
    

class PdfXObjectPossibleWatermark(groupdocs.watermark.search.TwoDObjectPossibleWatermark):
    '''Represents possible XObject watermark in a pdf content.'''
    
    @property
    def parent(self) -> groupdocs.watermark.contents.ContentPart:
        '''Gets the parent of this :py:class:`groupdocs.watermark.search.watermarks.PdfXObjectPossibleWatermark`.'''
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
    

class PresentationBackgroundPossibleWatermark(groupdocs.watermark.search.PossibleWatermark):
    '''Represents possible background watermark in a PowerPoint document.'''
    
    @property
    def parent(self) -> groupdocs.watermark.contents.ContentPart:
        '''Gets the parent of this :py:class:`groupdocs.watermark.search.watermarks.PresentationBackgroundPossibleWatermark`.'''
        raise NotImplementedError()
    
    @property
    def page_number(self) -> System.Nullable`1[[System.Int32]]:
        '''Gets the page watermark is placed on.'''
        raise NotImplementedError()
    
    @property
    def width(self) -> float:
        '''Gets the width of this :py:class:`groupdocs.watermark.search.watermarks.PresentationBackgroundPossibleWatermark` in points.'''
        raise NotImplementedError()
    
    @property
    def height(self) -> float:
        '''Gets the height of this :py:class:`groupdocs.watermark.search.watermarks.PresentationBackgroundPossibleWatermark` in points.'''
        raise NotImplementedError()
    
    @property
    def x(self) -> float:
        '''Gets the horizontal offset of this :py:class:`groupdocs.watermark.search.watermarks.PresentationBackgroundPossibleWatermark`
        from slide left border in points.'''
        raise NotImplementedError()
    
    @property
    def y(self) -> float:
        '''Gets the vertical offset of this :py:class:`groupdocs.watermark.search.watermarks.PresentationBackgroundPossibleWatermark`
        from slide top border in points.'''
        raise NotImplementedError()
    
    @property
    def rotate_angle(self) -> float:
        '''Gets the rotate angle of this :py:class:`groupdocs.watermark.search.watermarks.PresentationBackgroundPossibleWatermark` in degrees.'''
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
        '''Gets the unit of measurement of this :py:class:`groupdocs.watermark.search.watermarks.PresentationBackgroundPossibleWatermark`.'''
        raise NotImplementedError()
    

class PresentationChartBackgroundPossibleWatermark(groupdocs.watermark.search.TwoDObjectPossibleWatermark):
    '''Represents possible background watermark in a PowerPoint chart.'''
    
    @property
    def parent(self) -> groupdocs.watermark.contents.ContentPart:
        '''Gets the parent of this :py:class:`groupdocs.watermark.search.watermarks.PresentationChartBackgroundPossibleWatermark`.'''
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
        '''Gets the rotate angle of this :py:class:`groupdocs.watermark.search.watermarks.PresentationChartBackgroundPossibleWatermark` in degrees.'''
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
        '''Gets the unit of measurement of this :py:class:`groupdocs.watermark.search.watermarks.PresentationChartBackgroundPossibleWatermark`.'''
        raise NotImplementedError()
    

class PresentationHyperlinkPossibleWatermark(groupdocs.watermark.search.HyperlinkPossibleWatermark):
    '''Represents possible hyperlink watermark in a PowerPoint document.'''
    
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
    

class PresentationShapePossibleWatermark(groupdocs.watermark.search.TwoDObjectPossibleWatermark):
    '''Represents possible shape watermark in a PowerPoint document.'''
    
    @property
    def parent(self) -> groupdocs.watermark.contents.ContentPart:
        '''Gets the parent of this :py:class:`groupdocs.watermark.search.watermarks.PresentationShapePossibleWatermark`.'''
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
    

class SpreadsheetAttachedImagePossibleWatermark(groupdocs.watermark.search.PossibleWatermark):
    '''Represents possible image watermark in Excel document attachment.'''
    
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
    

class SpreadsheetBackgroundPossibleWatermark(groupdocs.watermark.search.PossibleWatermark):
    '''Represents possible background watermark in an Excel document.'''
    
    @property
    def parent(self) -> groupdocs.watermark.contents.ContentPart:
        '''Gets the parent of this :py:class:`groupdocs.watermark.search.watermarks.SpreadsheetBackgroundPossibleWatermark`.'''
        raise NotImplementedError()
    
    @property
    def page_number(self) -> System.Nullable`1[[System.Int32]]:
        '''Gets the page watermark is placed on.'''
        raise NotImplementedError()
    
    @property
    def width(self) -> float:
        '''Gets the width of this :py:class:`groupdocs.watermark.search.watermarks.SpreadsheetBackgroundPossibleWatermark` in pixels.'''
        raise NotImplementedError()
    
    @property
    def height(self) -> float:
        '''Gets the height of this :py:class:`groupdocs.watermark.search.watermarks.SpreadsheetBackgroundPossibleWatermark` in pixels.'''
        raise NotImplementedError()
    
    @property
    def x(self) -> float:
        '''Gets the horizontal offset of this :py:class:`groupdocs.watermark.search.watermarks.SpreadsheetBackgroundPossibleWatermark` from worksheet left border
        in pixels.'''
        raise NotImplementedError()
    
    @property
    def y(self) -> float:
        '''Gets the vertical offset of this :py:class:`groupdocs.watermark.search.watermarks.SpreadsheetBackgroundPossibleWatermark` from worksheet top border in
        pixels.'''
        raise NotImplementedError()
    
    @property
    def rotate_angle(self) -> float:
        '''Gets the rotate angle of this :py:class:`groupdocs.watermark.search.watermarks.SpreadsheetBackgroundPossibleWatermark` in degrees.'''
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
        '''Gets the unit of measurement of this :py:class:`groupdocs.watermark.search.watermarks.SpreadsheetBackgroundPossibleWatermark`.'''
        raise NotImplementedError()
    

class SpreadsheetCellPossibleWatermark(groupdocs.watermark.search.PossibleWatermark):
    '''Represents possible cell watermark in an Excel document.'''
    
    @property
    def parent(self) -> groupdocs.watermark.contents.ContentPart:
        '''Gets the parent of this :py:class:`groupdocs.watermark.search.watermarks.SpreadsheetCellPossibleWatermark`.'''
        raise NotImplementedError()
    
    @property
    def page_number(self) -> System.Nullable`1[[System.Int32]]:
        '''Gets the page watermark is placed on.'''
        raise NotImplementedError()
    
    @property
    def width(self) -> float:
        '''Gets the width of this :py:class:`groupdocs.watermark.search.watermarks.SpreadsheetCellPossibleWatermark` in points.'''
        raise NotImplementedError()
    
    @property
    def height(self) -> float:
        '''Gets the height of this :py:class:`groupdocs.watermark.search.watermarks.SpreadsheetCellPossibleWatermark` in points.'''
        raise NotImplementedError()
    
    @property
    def x(self) -> float:
        '''Gets the horizontal offset of this :py:class:`groupdocs.watermark.search.watermarks.SpreadsheetCellPossibleWatermark`
        from content left border in points.'''
        raise NotImplementedError()
    
    @property
    def y(self) -> float:
        '''Gets the vertical offset of this :py:class:`groupdocs.watermark.search.watermarks.SpreadsheetCellPossibleWatermark` from content
        top border in points.'''
        raise NotImplementedError()
    
    @property
    def rotate_angle(self) -> float:
        '''Gets the rotate angle of this :py:class:`groupdocs.watermark.search.watermarks.SpreadsheetCellPossibleWatermark` in degrees.'''
        raise NotImplementedError()
    
    @property
    def text(self) -> str:
        '''Gets the text of this :py:class:`groupdocs.watermark.search.watermarks.SpreadsheetCellPossibleWatermark`.'''
        raise NotImplementedError()
    
    @text.setter
    def text(self, value : str) -> None:
        '''Sets the text of this :py:class:`groupdocs.watermark.search.watermarks.SpreadsheetCellPossibleWatermark`.'''
        raise NotImplementedError()
    
    @property
    def formatted_text_fragments(self) -> groupdocs.watermark.search.FormattedTextFragmentCollection:
        '''Gets the collection of formatted text fragments of this :py:class:`groupdocs.watermark.search.watermarks.SpreadsheetCellPossibleWatermark`.'''
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
        '''Gets the unit of measurement of this :py:class:`groupdocs.watermark.search.watermarks.SpreadsheetCellPossibleWatermark`.'''
        raise NotImplementedError()
    

class SpreadsheetChartBackgroundPossibleWatermark(groupdocs.watermark.search.TwoDObjectPossibleWatermark):
    '''Represents possible image watermark in Excel chart background.'''
    
    @property
    def parent(self) -> groupdocs.watermark.contents.ContentPart:
        '''Gets the parent of this :py:class:`groupdocs.watermark.search.watermarks.SpreadsheetChartBackgroundPossibleWatermark`.'''
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
        '''Gets the rotate angle of this :py:class:`groupdocs.watermark.search.watermarks.SpreadsheetChartBackgroundPossibleWatermark` in degrees.'''
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
        '''Gets the unit of measurement of this :py:class:`groupdocs.watermark.search.watermarks.SpreadsheetChartBackgroundPossibleWatermark`.'''
        raise NotImplementedError()
    

class SpreadsheetHeaderFooterPossibleWatermark(groupdocs.watermark.search.PossibleWatermark):
    '''Represents possible watermark in a header or footer of an Excel document.'''
    
    @property
    def parent(self) -> groupdocs.watermark.contents.ContentPart:
        '''Gets the parent of this :py:class:`groupdocs.watermark.search.watermarks.SpreadsheetHeaderFooterPossibleWatermark`.'''
        raise NotImplementedError()
    
    @property
    def page_number(self) -> System.Nullable`1[[System.Int32]]:
        '''Gets the page watermark is placed on.'''
        raise NotImplementedError()
    
    @property
    def width(self) -> float:
        '''Gets the width of this :py:class:`groupdocs.watermark.search.watermarks.SpreadsheetHeaderFooterPossibleWatermark` in points.'''
        raise NotImplementedError()
    
    @property
    def height(self) -> float:
        '''Gets the height of this :py:class:`groupdocs.watermark.search.watermarks.SpreadsheetHeaderFooterPossibleWatermark` in points.'''
        raise NotImplementedError()
    
    @property
    def x(self) -> float:
        '''Gets the horizontal offset of this :py:class:`groupdocs.watermark.search.watermarks.SpreadsheetHeaderFooterPossibleWatermark`
        from worksheet left border in points.'''
        raise NotImplementedError()
    
    @property
    def y(self) -> float:
        '''Gets the vertical offset of this :py:class:`groupdocs.watermark.search.watermarks.SpreadsheetHeaderFooterPossibleWatermark` from
        worksheet top border in points.'''
        raise NotImplementedError()
    
    @property
    def rotate_angle(self) -> float:
        '''Gets the rotate angle of this :py:class:`groupdocs.watermark.search.watermarks.SpreadsheetHeaderFooterPossibleWatermark` in degrees.'''
        raise NotImplementedError()
    
    @property
    def text(self) -> str:
        '''Gets the text of this :py:class:`groupdocs.watermark.search.watermarks.SpreadsheetHeaderFooterPossibleWatermark`.'''
        raise NotImplementedError()
    
    @text.setter
    def text(self, value : str) -> None:
        '''Sets the text of this :py:class:`groupdocs.watermark.search.watermarks.SpreadsheetHeaderFooterPossibleWatermark`.'''
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
        '''Gets the unit of measurement of this :py:class:`groupdocs.watermark.search.watermarks.SpreadsheetHeaderFooterPossibleWatermark`.'''
        raise NotImplementedError()
    

class SpreadsheetHyperlinkPossibleWatermark(groupdocs.watermark.search.HyperlinkPossibleWatermark):
    '''Represents possible hyperlink watermark in an Excel document.'''
    
    @property
    def parent(self) -> groupdocs.watermark.contents.ContentPart:
        '''Gets the parent of this :py:class:`groupdocs.watermark.search.watermarks.SpreadsheetHyperlinkPossibleWatermark`.'''
        raise NotImplementedError()
    
    @property
    def page_number(self) -> System.Nullable`1[[System.Int32]]:
        '''Gets the page watermark is placed on.'''
        raise NotImplementedError()
    
    @property
    def width(self) -> float:
        '''Gets the width of this :py:class:`groupdocs.watermark.search.watermarks.SpreadsheetHyperlinkPossibleWatermark` in points.'''
        raise NotImplementedError()
    
    @property
    def height(self) -> float:
        '''Gets the height of this :py:class:`groupdocs.watermark.search.watermarks.SpreadsheetHyperlinkPossibleWatermark` in points.'''
        raise NotImplementedError()
    
    @property
    def x(self) -> float:
        '''Gets the horizontal offset of this :py:class:`groupdocs.watermark.search.watermarks.SpreadsheetHyperlinkPossibleWatermark` from
        worksheet left border in points.'''
        raise NotImplementedError()
    
    @property
    def y(self) -> float:
        '''Gets the vertical offset of this :py:class:`groupdocs.watermark.search.watermarks.SpreadsheetHyperlinkPossibleWatermark` from
        worksheet top border in points.'''
        raise NotImplementedError()
    
    @property
    def rotate_angle(self) -> float:
        '''Gets the rotate angle of this :py:class:`groupdocs.watermark.search.watermarks.SpreadsheetHyperlinkPossibleWatermark` in degrees.'''
        raise NotImplementedError()
    
    @property
    def text(self) -> str:
        '''Gets the url of this :py:class:`groupdocs.watermark.search.watermarks.SpreadsheetHyperlinkPossibleWatermark`.'''
        raise NotImplementedError()
    
    @text.setter
    def text(self, value : str) -> None:
        '''Sets the url of this :py:class:`groupdocs.watermark.search.watermarks.SpreadsheetHyperlinkPossibleWatermark`.'''
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
        '''Gets the unit of measurement of this :py:class:`groupdocs.watermark.search.watermarks.SpreadsheetHyperlinkPossibleWatermark`.'''
        raise NotImplementedError()
    

class SpreadsheetShapePossibleWatermark(groupdocs.watermark.search.TwoDObjectPossibleWatermark):
    '''Represents possible shape watermark in an Excel document.'''
    
    @property
    def parent(self) -> groupdocs.watermark.contents.ContentPart:
        '''Gets the parent of this :py:class:`groupdocs.watermark.search.watermarks.SpreadsheetShapePossibleWatermark`.'''
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
    

class WordProcessingShapePossibleWatermark(groupdocs.watermark.search.TwoDObjectPossibleWatermark):
    '''Represents possible shape watermark in a Word document.'''
    
    @property
    def parent(self) -> groupdocs.watermark.contents.ContentPart:
        '''Gets the parent of this :py:class:`groupdocs.watermark.search.watermarks.WordProcessingShapePossibleWatermark`.'''
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
    

class WordProcessingTextHyperlinkPossibleWatermark(groupdocs.watermark.search.HyperlinkPossibleWatermark):
    '''Represents possible hyperlink watermark in a Word document.'''
    
    @property
    def parent(self) -> groupdocs.watermark.contents.ContentPart:
        '''Gets the parent of this :py:class:`groupdocs.watermark.search.watermarks.WordProcessingTextHyperlinkPossibleWatermark`.'''
        raise NotImplementedError()
    
    @property
    def page_number(self) -> System.Nullable`1[[System.Int32]]:
        '''Gets the page watermark is placed on.'''
        raise NotImplementedError()
    
    @property
    def width(self) -> float:
        '''Gets the width of this :py:class:`groupdocs.watermark.search.watermarks.WordProcessingTextHyperlinkPossibleWatermark`.'''
        raise NotImplementedError()
    
    @property
    def height(self) -> float:
        '''Gets the height of this :py:class:`groupdocs.watermark.search.watermarks.WordProcessingTextHyperlinkPossibleWatermark`.'''
        raise NotImplementedError()
    
    @property
    def x(self) -> float:
        '''Gets the x-coordinate of this :py:class:`groupdocs.watermark.search.watermarks.WordProcessingTextHyperlinkPossibleWatermark`.'''
        raise NotImplementedError()
    
    @property
    def y(self) -> float:
        '''Gets the y-coordinate of this :py:class:`groupdocs.watermark.search.watermarks.WordProcessingTextHyperlinkPossibleWatermark`.'''
        raise NotImplementedError()
    
    @property
    def rotate_angle(self) -> float:
        '''Gets the rotate angle of this :py:class:`groupdocs.watermark.search.watermarks.WordProcessingTextHyperlinkPossibleWatermark` in degrees.'''
        raise NotImplementedError()
    
    @property
    def text(self) -> str:
        '''Gets the url of this :py:class:`groupdocs.watermark.search.watermarks.WordProcessingTextHyperlinkPossibleWatermark`.'''
        raise NotImplementedError()
    
    @text.setter
    def text(self, value : str) -> None:
        '''Sets the url of this :py:class:`groupdocs.watermark.search.watermarks.WordProcessingTextHyperlinkPossibleWatermark`.'''
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
        '''Gets the unit of measurement of this :py:class:`groupdocs.watermark.search.watermarks.WordProcessingTextHyperlinkPossibleWatermark`.'''
        raise NotImplementedError()
    

class WordProcessingTextPossibleWatermark(groupdocs.watermark.search.PossibleWatermark):
    '''Represents possible watermark in a Word document text.'''
    
    @property
    def parent(self) -> groupdocs.watermark.contents.ContentPart:
        '''Gets the parent of this :py:class:`groupdocs.watermark.search.watermarks.WordProcessingTextPossibleWatermark`.'''
        raise NotImplementedError()
    
    @property
    def page_number(self) -> System.Nullable`1[[System.Int32]]:
        '''Gets the page watermark is placed on.'''
        raise NotImplementedError()
    
    @property
    def width(self) -> float:
        '''Gets the width of this :py:class:`groupdocs.watermark.search.watermarks.WordProcessingTextPossibleWatermark` in points.'''
        raise NotImplementedError()
    
    @property
    def height(self) -> float:
        '''Gets the height of this :py:class:`groupdocs.watermark.search.watermarks.WordProcessingTextPossibleWatermark` in points.'''
        raise NotImplementedError()
    
    @property
    def x(self) -> float:
        '''Gets the horizontal offset of this :py:class:`groupdocs.watermark.search.watermarks.WordProcessingTextPossibleWatermark`
        from document left border in points.'''
        raise NotImplementedError()
    
    @property
    def y(self) -> float:
        '''Gets the vertical offset of this :py:class:`groupdocs.watermark.search.watermarks.WordProcessingTextPossibleWatermark`
        from document top border in points.'''
        raise NotImplementedError()
    
    @property
    def rotate_angle(self) -> float:
        '''Gets the rotate angle of this :py:class:`groupdocs.watermark.search.watermarks.WordProcessingTextPossibleWatermark` in degrees.'''
        raise NotImplementedError()
    
    @property
    def text(self) -> str:
        '''Gets the text of this :py:class:`groupdocs.watermark.search.watermarks.WordProcessingTextPossibleWatermark`.'''
        raise NotImplementedError()
    
    @text.setter
    def text(self, value : str) -> None:
        '''Sets the text of this :py:class:`groupdocs.watermark.search.watermarks.WordProcessingTextPossibleWatermark`.'''
        raise NotImplementedError()
    
    @property
    def formatted_text_fragments(self) -> groupdocs.watermark.search.FormattedTextFragmentCollection:
        '''Gets the collection of formatted text fragments of this :py:class:`groupdocs.watermark.search.watermarks.WordProcessingTextPossibleWatermark`.'''
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
        '''Gets the unit of measurement of this :py:class:`groupdocs.watermark.search.watermarks.WordProcessingTextPossibleWatermark`.'''
        raise NotImplementedError()
    

