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

class EmailAddress:
    '''Represents an address of an email message.'''
    
    @property
    def address(self) -> str:
        '''Gets the string representation of the email address.'''
        raise NotImplementedError()
    
    @property
    def display_name(self) -> str:
        '''Gets the display name associated with the address.'''
        raise NotImplementedError()
    
    @property
    def original_address_string(self) -> str:
        '''Gets the original address string.'''
        raise NotImplementedError()
    
    @property
    def host(self) -> str:
        '''Gets the host portion of the address.'''
        raise NotImplementedError()
    
    @property
    def user(self) -> str:
        '''Gets the username.'''
        raise NotImplementedError()
    

class EmailAddressCollection:
    '''Represents a collection of addresses in an email message.'''
    

class EmailAttachment(EmailAttachmentBase):
    '''Represents a file attached to an email message.'''
    
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
    def content_id(self) -> str:
        '''Gets the content id of this :py:class:`groupdocs.watermark.contents.email.EmailAttachmentBase`.'''
        raise NotImplementedError()
    
    @property
    def media_type(self) -> str:
        '''Gets the media type of this :py:class:`groupdocs.watermark.contents.email.EmailAttachmentBase`.'''
        raise NotImplementedError()
    
    @property
    def name(self) -> str:
        '''Gets the name of the attached file.'''
        raise NotImplementedError()
    
    @name.setter
    def name(self, value : str) -> None:
        '''Sets the name of the attached file.'''
        raise NotImplementedError()
    

class EmailAttachmentBase(groupdocs.watermark.common.Attachment):
    '''Provides a base class for email attachments.'''
    
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
    def content_id(self) -> str:
        '''Gets the content id of this :py:class:`groupdocs.watermark.contents.email.EmailAttachmentBase`.'''
        raise NotImplementedError()
    
    @property
    def media_type(self) -> str:
        '''Gets the media type of this :py:class:`groupdocs.watermark.contents.email.EmailAttachmentBase`.'''
        raise NotImplementedError()
    

class EmailAttachmentCollection:
    '''Represents a collection of attachments in an email message.'''
    
    def add(self, file_content : List[int], name : str) -> None:
        '''Adds an attachment to the :py:class:`groupdocs.watermark.contents.email.EmailContent`.
        
        :param file_content: The content of the file to be attached.
        :param name: The name of the file.'''
        raise NotImplementedError()
    

class EmailContent(groupdocs.watermark.contents.Content):
    '''Represents an email message.'''
    
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
    def attachments(self) -> groupdocs.watermark.contents.email.EmailAttachmentCollection:
        '''Gets the collection of all attachments of the email message.'''
        raise NotImplementedError()
    
    @property
    def embedded_objects(self) -> groupdocs.watermark.contents.email.EmailEmbeddedObjectCollection:
        '''Gets the collection of all embedded objects of the email message.'''
        raise NotImplementedError()
    
    @property
    def from_address(self) -> groupdocs.watermark.contents.email.EmailAddress:
        '''Gets the from address of the email message.'''
        raise NotImplementedError()
    
    @property
    def to(self) -> groupdocs.watermark.contents.email.EmailAddressCollection:
        '''Gets the collection of recipients of the email message.'''
        raise NotImplementedError()
    
    @property
    def cc(self) -> groupdocs.watermark.contents.email.EmailAddressCollection:
        '''Gets the collection of CC (carbon copy) recipients of the email message.'''
        raise NotImplementedError()
    
    @property
    def bcc(self) -> groupdocs.watermark.contents.email.EmailAddressCollection:
        '''Gets the collection of BCC (blind carbon copy) recipients of the email message.'''
        raise NotImplementedError()
    
    @property
    def subject(self) -> str:
        '''Gets the subject of the email message.'''
        raise NotImplementedError()
    
    @subject.setter
    def subject(self, value : str) -> None:
        '''Sets the subject of the email message.'''
        raise NotImplementedError()
    
    @property
    def body(self) -> str:
        '''Gets the plain text representation of the message body.'''
        raise NotImplementedError()
    
    @body.setter
    def body(self, value : str) -> None:
        '''Sets the plain text representation of the message body.'''
        raise NotImplementedError()
    
    @property
    def html_body(self) -> str:
        '''Gets the html representation of the message body.'''
        raise NotImplementedError()
    
    @html_body.setter
    def html_body(self, value : str) -> None:
        '''Sets the html representation of the message body.'''
        raise NotImplementedError()
    
    @property
    def body_type(self) -> groupdocs.watermark.contents.email.EmailBodyType:
        '''Gets the type of the email message body.'''
        raise NotImplementedError()
    

class EmailEmbeddedObject(EmailAttachmentBase):
    '''Represents an object embedded to an email message body.'''
    
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
    def content_id(self) -> str:
        '''Gets the content id of this :py:class:`groupdocs.watermark.contents.email.EmailAttachmentBase`.'''
        raise NotImplementedError()
    
    @property
    def media_type(self) -> str:
        '''Gets the media type of this :py:class:`groupdocs.watermark.contents.email.EmailAttachmentBase`.'''
        raise NotImplementedError()
    

class EmailEmbeddedObjectCollection:
    '''Represents a collection of embedded objects in an email message.'''
    
    def add(self, file_content : List[int], name : str) -> None:
        '''Adds an embedded resource to the :py:class:`groupdocs.watermark.contents.email.EmailContent`.
        
        :param file_content: The content of the file to be added.
        :param name: The name of the file.'''
        raise NotImplementedError()
    

class EmailBodyType:
    '''Represents a content type of an email message body.'''
    
    PLAIN_TEXT : EmailBodyType
    '''Plain text body.'''
    HTML : EmailBodyType
    '''Html-formatted body.'''

