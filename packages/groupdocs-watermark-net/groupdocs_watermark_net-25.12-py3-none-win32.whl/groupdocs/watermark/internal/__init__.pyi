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

class WatermarkResult:
    '''Represents the result of watermarking operation, including details such as document sizes, processing time, and the number of applied watermarks.'''
    
    @overload
    def __init__(self) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.watermark.internal.WatermarkResult` class.'''
        raise NotImplementedError()
    
    @overload
    def __init__(self, source_document_size : int, processing_time : System.TimeSpan, final_document_size : int, number_watermarks_applied : int) -> None:
        '''Initializes a new instance of the :py:class:`groupdocs.watermark.internal.WatermarkResult` class with specific values.
        
        :param source_document_size: The size of the source document in bytes.
        :param processing_time: The processing time in milliseconds.
        :param final_document_size: The size of the final processed document in bytes.
        :param number_watermarks_applied: The total number of watermarks applied to the document.'''
        raise NotImplementedError()
    
    @property
    def source_document_size(self) -> int:
        '''Gets the size of the source document in bytes.'''
        raise NotImplementedError()
    
    @property
    def processing_time(self) -> System.TimeSpan:
        '''Gets the processing time for the watermarking operation.'''
        raise NotImplementedError()
    
    @property
    def final_document_size(self) -> int:
        '''Gets the size of the final processed document in bytes.'''
        raise NotImplementedError()
    
    @property
    def number_watermarks_applied(self) -> int:
        '''Gets the total number of watermarks applied to the document.'''
        raise NotImplementedError()
    

