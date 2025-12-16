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

class SearchableObjects:
    '''Specifies document objects that are to be included in a watermark search.'''
    
    def __init__(self) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.watermark.search.objects.SearchableObjects` class.'''
        raise NotImplementedError()
    
    @property
    def spreadsheet_searchable_objects(self) -> groupdocs.watermark.search.objects.SpreadsheetSearchableObjects:
        '''Gets the objects inside an Excel document that are to be included in a watermark search.'''
        raise NotImplementedError()
    
    @spreadsheet_searchable_objects.setter
    def spreadsheet_searchable_objects(self, value : groupdocs.watermark.search.objects.SpreadsheetSearchableObjects) -> None:
        '''Sets the objects inside an Excel document that are to be included in a watermark search.'''
        raise NotImplementedError()
    
    @property
    def diagram_searchable_objects(self) -> groupdocs.watermark.search.objects.DiagramSearchableObjects:
        '''Gets the objects inside a Visio document that are to be included in a watermark search.'''
        raise NotImplementedError()
    
    @diagram_searchable_objects.setter
    def diagram_searchable_objects(self, value : groupdocs.watermark.search.objects.DiagramSearchableObjects) -> None:
        '''Sets the objects inside a Visio document that are to be included in a watermark search.'''
        raise NotImplementedError()
    
    @property
    def presentation_searchable_objects(self) -> groupdocs.watermark.search.objects.PresentationSearchableObjects:
        '''Gets the objects inside a PowerPoint document that are to be included in a watermark search.'''
        raise NotImplementedError()
    
    @presentation_searchable_objects.setter
    def presentation_searchable_objects(self, value : groupdocs.watermark.search.objects.PresentationSearchableObjects) -> None:
        '''Sets the objects inside a PowerPoint document that are to be included in a watermark search.'''
        raise NotImplementedError()
    
    @property
    def word_processing_searchable_objects(self) -> groupdocs.watermark.search.objects.WordProcessingSearchableObjects:
        '''Gets the objects inside a Word document that are to be included in a watermark search.'''
        raise NotImplementedError()
    
    @word_processing_searchable_objects.setter
    def word_processing_searchable_objects(self, value : groupdocs.watermark.search.objects.WordProcessingSearchableObjects) -> None:
        '''Sets the objects inside a Word document that are to be included in a watermark search.'''
        raise NotImplementedError()
    
    @property
    def pdf_searchable_objects(self) -> groupdocs.watermark.search.objects.PdfSearchableObjects:
        '''Gets the objects inside a PDF document that are to be included in a watermark search.'''
        raise NotImplementedError()
    
    @pdf_searchable_objects.setter
    def pdf_searchable_objects(self, value : groupdocs.watermark.search.objects.PdfSearchableObjects) -> None:
        '''Sets the objects inside a PDF document that are to be included in a watermark search.'''
        raise NotImplementedError()
    
    @property
    def email_searchable_objects(self) -> groupdocs.watermark.search.objects.EmailSearchableObjects:
        '''Gets the objects inside an email message that are to be included in a watermark search.'''
        raise NotImplementedError()
    
    @email_searchable_objects.setter
    def email_searchable_objects(self, value : groupdocs.watermark.search.objects.EmailSearchableObjects) -> None:
        '''Sets the objects inside an email message that are to be included in a watermark search.'''
        raise NotImplementedError()
    

class DiagramSearchableObjects:
    '''Specifies flags representing Visio document objects that are to be included in a watermark search.'''
    
    NONE : DiagramSearchableObjects
    '''Specifies no search objects.'''
    SHAPES : DiagramSearchableObjects
    '''Search in shapes.'''
    COMMENTS : DiagramSearchableObjects
    '''Search in comments.'''
    HEADERS_FOOTERS : DiagramSearchableObjects
    '''Search in headers and footers.'''
    HYPERLINKS : DiagramSearchableObjects
    '''Search in hyperlinks.'''
    ALL : DiagramSearchableObjects
    '''Search in all content objects.'''

class EmailSearchableObjects:
    '''Specifies flags representing email message objects that are to be included in a watermark search.'''
    
    NONE : EmailSearchableObjects
    '''Specifies no search objects.'''
    SUBJECT : EmailSearchableObjects
    '''Search in message subject.'''
    PLAIN_TEXT_BODY : EmailSearchableObjects
    '''Search in message plain text body.'''
    HTML_BODY : EmailSearchableObjects
    '''Search in message html body.'''
    ATTACHED_IMAGES : EmailSearchableObjects
    '''Search in attached images.'''
    EMBEDDED_IMAGES : EmailSearchableObjects
    '''Search in embedded images.'''
    ALL : EmailSearchableObjects
    '''Search in all email objects.'''

class PdfSearchableObjects:
    '''Specifies flags representing pdf content objects that are to be included in a watermark search.'''
    
    NONE : PdfSearchableObjects
    '''Specifies no search objects.'''
    X_OBJECTS : PdfSearchableObjects
    '''Search in XObjects.'''
    ARTIFACTS : PdfSearchableObjects
    '''Search in artifacts.'''
    ANNOTATIONS : PdfSearchableObjects
    '''Search in annotations.'''
    TEXT : PdfSearchableObjects
    '''Search in content text.'''
    HYPERLINKS : PdfSearchableObjects
    '''Search in hyperlinks.'''
    ATTACHED_IMAGES : PdfSearchableObjects
    '''Search in attached images.'''
    VECTOR : PdfSearchableObjects
    '''Search in operators.'''
    ALL : PdfSearchableObjects
    '''Search in all content objects.'''

class PresentationSearchableObjects:
    '''Specifies flags representing PowerPoint content objects that are to be included in a watermark search.'''
    
    NONE : PresentationSearchableObjects
    '''Specifies no search objects.'''
    SHAPES : PresentationSearchableObjects
    '''Search in shapes.'''
    CHARTS_BACKGROUNDS : PresentationSearchableObjects
    '''Search in charts backgrounds.'''
    SLIDES_BACKGROUNDS : PresentationSearchableObjects
    '''Search in slides backgrounds.'''
    HYPERLINKS : PresentationSearchableObjects
    '''Search in hyperlinks.'''
    ALL : PresentationSearchableObjects
    '''Search in all content objects.'''

class SpreadsheetSearchableObjects:
    '''Specifies flags representing Excel content objects that are to be included in a watermark search.'''
    
    NONE : SpreadsheetSearchableObjects
    '''Specifies no search objects.'''
    SHAPES : SpreadsheetSearchableObjects
    '''Search in shapes.'''
    CHARTS_BACKGROUNDS : SpreadsheetSearchableObjects
    '''Search in charts backgrounds.'''
    HEADERS_FOOTERS : SpreadsheetSearchableObjects
    '''Search in headers and footers.'''
    WORKSHEET_BACKGROUNDS : SpreadsheetSearchableObjects
    '''Search in worksheets backgrounds.'''
    CELLS : SpreadsheetSearchableObjects
    '''Search in cells.'''
    HYPERLINKS : SpreadsheetSearchableObjects
    '''Search in hyperlinks.'''
    ATTACHED_IMAGES : SpreadsheetSearchableObjects
    '''Search in attached images.'''
    ALL : SpreadsheetSearchableObjects
    '''Search in all content objects.'''

class WordProcessingSearchableObjects:
    '''Specifies flags representing Word content objects that are to be included in a watermark search.'''
    
    NONE : WordProcessingSearchableObjects
    '''Specifies no search objects.'''
    SHAPES : WordProcessingSearchableObjects
    '''Search in shapes.'''
    TEXT : WordProcessingSearchableObjects
    '''Search in content text.'''
    HYPERLINKS : WordProcessingSearchableObjects
    '''Search in hyperlinks.'''
    ALL : WordProcessingSearchableObjects
    '''Search in all content objects.'''

