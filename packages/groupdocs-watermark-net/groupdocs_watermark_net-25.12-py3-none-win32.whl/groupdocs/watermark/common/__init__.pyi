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

class Attachment:
    '''Represents a file attached to a document.'''
    
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
    

class AttachmentWatermarkableImage(groupdocs.watermark.contents.image.WatermarkableImage):
    '''Represents an attached image inside a content of any supported type.'''
    
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
    

class FileType:
    '''Represents file type.'''
    
    def equals(self, other : groupdocs.watermark.common.FileType) -> bool:
        '''Determines whether the current :py:class:`groupdocs.watermark.common.FileType` is the same as the specified :py:class:`groupdocs.watermark.common.FileType` object.
        
        :param other: The object to compare with the current :py:class:`groupdocs.watermark.common.FileType` object.
        :returns: true
        if both :py:class:`groupdocs.watermark.common.FileType` objects are the same; otherwise,     false
        .'''
        raise NotImplementedError()
    
    @staticmethod
    def from_extension(extension : str) -> groupdocs.watermark.common.FileType:
        '''Maps the file extension to the file type.
        
        :param extension: The file extension (including the period ".").
        :returns: When the file type is supported returns it, otherwise returns the default :py:attr:`groupdocs.watermark.common.FileType.UNKNOWN` file type.'''
        raise NotImplementedError()
    
    @staticmethod
    def get_supported_file_types() -> System.Collections.Generic.IEnumerable`1[[GroupDocs.Watermark.Common.FileType]]:
        '''Retrieves the supported file types.
        
        :returns: Returns the sequence of the supported file types.'''
        raise NotImplementedError()
    
    @property
    def file_format_name(self) -> str:
        '''Gets the file type name e.g., "Microsoft Word Document".'''
        raise NotImplementedError()
    
    @property
    def extension(self) -> str:
        '''Gets the file name suffix (including the period ".") e.g., ".doc".'''
        raise NotImplementedError()
    
    @property
    def format_family(self) -> groupdocs.watermark.common.FormatFamily:
        '''Gets the format family.'''
        raise NotImplementedError()
    
    @property
    def UNKNOWN(self) -> groupdocs.watermark.common.FileType:
        '''Represents unknown file type.'''
        raise NotImplementedError()

    @property
    def OOXML(self) -> groupdocs.watermark.common.FileType:
        '''Office open xml file (.ooxml).'''
        raise NotImplementedError()

    @property
    def VSD(self) -> groupdocs.watermark.common.FileType:
        '''VSD files are drawings created with Microsoft Visio application to represent variety of graphical
        objects and the interconnection between these. Learn more about this file format
        `here <https://wiki.fileformat.com/image/vsd/>`.'''
        raise NotImplementedError()

    @property
    def VSDX(self) -> groupdocs.watermark.common.FileType:
        '''Files with .VSDX extension represent Microsoft Visio file format introduced from Microsoft
        Office 2013 onwards. Learn more about this file format
        `here <https://wiki.fileformat.com/image/vsdx/>`.'''
        raise NotImplementedError()

    @property
    def VSS(self) -> groupdocs.watermark.common.FileType:
        '''VSS are stencil files created with Microsoft Visio 2007 and earlier. Stencil files provide drawing
        objects that can be included in a .VSD Visio drawing. Learn more about this file format
        `here <https://wiki.fileformat.com/image/vss/>`.'''
        raise NotImplementedError()

    @property
    def VSSX(self) -> groupdocs.watermark.common.FileType:
        '''Files with .VSSX extension are drawing stencils created with Microsoft Visio 2013 and above.
        Learn more about this file format
        `here <https://wiki.fileformat.com/image/vssx/>`.'''
        raise NotImplementedError()

    @property
    def VSDM(self) -> groupdocs.watermark.common.FileType:
        '''Files with VSDM extension are drawing files created with Microsoft Visio application that supports macros.
        Learn more about this file format
        `here <https://wiki.fileformat.com/image/vsdm/>`.'''
        raise NotImplementedError()

    @property
    def VST(self) -> groupdocs.watermark.common.FileType:
        '''Files with VST extension are vector image files created with Microsoft Visio and act as template for
        creating further files. Learn more about this file format
        `here <https://wiki.fileformat.com/image/vst/>`.'''
        raise NotImplementedError()

    @property
    def VSTX(self) -> groupdocs.watermark.common.FileType:
        '''Files with VSTX extensions are drawing template files created with Microsoft Visio 2013 and above.
        Learn more about this file format
        `here <https://wiki.fileformat.com/image/vstx/>`.'''
        raise NotImplementedError()

    @property
    def VSTM(self) -> groupdocs.watermark.common.FileType:
        '''Files with VSTM extension are template files created with Microsoft Visio that support macros.
        Learn more about this file format `here <https://wiki.fileformat.com/image/vstm/>`.'''
        raise NotImplementedError()

    @property
    def VSSM(self) -> groupdocs.watermark.common.FileType:
        '''Files with .VSSM extension are Microsoft Visio Stencil files that support provide support for macros.
        Learn more about this file format `here <https://wiki.fileformat.com/image/vssm/>`.'''
        raise NotImplementedError()

    @property
    def VSX(self) -> groupdocs.watermark.common.FileType:
        '''Files with .VSX extension refer to stencils that consist of drawings and shapes that are used for
        creating diagrams in Microsoft Visio. Learn more about this file format
        `here <https://wiki.fileformat.com/image/vsx/>`.'''
        raise NotImplementedError()

    @property
    def VTX(self) -> groupdocs.watermark.common.FileType:
        '''A file with VTX extension is a Microsoft Visio drawing template that is saved to disc in XML file format.
        Learn more about this file format `here <https://wiki.fileformat.com/image/vtx/>`.'''
        raise NotImplementedError()

    @property
    def VDW(self) -> groupdocs.watermark.common.FileType:
        '''VDW is the Visio Graphics Service file format that specifies the streams and storages required for
        rendering a Web drawing. Learn more about this file format
        `here <https://wiki.fileformat.com/web/vdw/>`.'''
        raise NotImplementedError()

    @property
    def VDX(self) -> groupdocs.watermark.common.FileType:
        '''Any drawing or chart created in Microsoft Visio, but saved in XML format have .VDX extension.
        Learn more about this file format `here <https://wiki.fileformat.com/image/vdx/>`.'''
        raise NotImplementedError()

    @property
    def MSG(self) -> groupdocs.watermark.common.FileType:
        '''MSG is a file format used by Microsoft Outlook and Exchange to store email messages, contact,
        appointment, or other tasks. Learn more about this file format
        `here <https://wiki.fileformat.com/email/msg/>`.'''
        raise NotImplementedError()

    @property
    def EML(self) -> groupdocs.watermark.common.FileType:
        '''EML file format represents email messages saved using Outlook and other relevant applications.
        Learn more about this file format `here <https://wiki.fileformat.com/email/eml/>`.'''
        raise NotImplementedError()

    @property
    def EMLX(self) -> groupdocs.watermark.common.FileType:
        '''The EMLX file format is implemented and developed by Apple. The Apple Mail application uses the EMLX
        file format for exporting the emails.  Learn more about this file format
        `here <https://wiki.fileformat.com/email/emlx/>`.'''
        raise NotImplementedError()

    @property
    def OFT(self) -> groupdocs.watermark.common.FileType:
        '''Files with .OFT extension represent message template files that are created using Microsoft Outlook.
        Learn more about this file format `here <https://wiki.fileformat.com/email/oft/>`.'''
        raise NotImplementedError()

    @property
    def TIF(self) -> groupdocs.watermark.common.FileType:
        '''TIFF or TIF, Tagged Image File Format, represents raster images that are meant for usage on a variety
        of devices that comply with this file format standard. Learn more about this file format
        `here <https://wiki.fileformat.com/image/tiff/>`.'''
        raise NotImplementedError()

    @property
    def TIFF(self) -> groupdocs.watermark.common.FileType:
        '''TIFF or TIF, Tagged Image File Format, represents raster images that are meant for usage on a variety
        of devices that comply with this file format standard. Learn more about this file format
        `here <https://wiki.fileformat.com/image/tiff/>`.'''
        raise NotImplementedError()

    @property
    def JPG(self) -> groupdocs.watermark.common.FileType:
        '''A JPEG is a type of image format that is saved using the method of lossy compression.
        Learn more about this file format `here <https://wiki.fileformat.com/image/jpeg/>`.'''
        raise NotImplementedError()

    @property
    def JPEG(self) -> groupdocs.watermark.common.FileType:
        '''A JPEG is a type of image format that is saved using the method of lossy compression.
        Learn more about this file format `here <https://wiki.fileformat.com/image/jpeg/>`.'''
        raise NotImplementedError()

    @property
    def PNG(self) -> groupdocs.watermark.common.FileType:
        '''PNG, Portable Network Graphics, refers to a type of raster image file format that use loseless compression.
        Learn more about this file format `here <https://wiki.fileformat.com/image/png/>`.'''
        raise NotImplementedError()

    @property
    def GIF(self) -> groupdocs.watermark.common.FileType:
        '''A GIF or Graphical Interchange Format is a type of highly compressed image.
        Learn more about this file format `here <https://wiki.fileformat.com/image/gif/>`.'''
        raise NotImplementedError()

    @property
    def BMP(self) -> groupdocs.watermark.common.FileType:
        '''Files having extension .BMP represent Bitmap Image files that are used to store bitmap digital images.
        These images are independent of graphics adapter and are also called device independent bitmap (DIB) file
        format. Learn more about this file format `here <https://wiki.fileformat.com/image/bmp/>`.'''
        raise NotImplementedError()

    @property
    def JPF(self) -> groupdocs.watermark.common.FileType:
        '''JPEG 2000 (JPF) is an image coding system and state-of-the-art image compression standard. Designed,
        using wavelet technology JPEG 2000 can code lossless content in any quality at once. Learn more about
        this file format `here <https://wiki.fileformat.com/image/jp2/>`.'''
        raise NotImplementedError()

    @property
    def JPX(self) -> groupdocs.watermark.common.FileType:
        '''JPEG 2000 (JPX) is an image coding system and state-of-the-art image compression standard. Designed,
        using wavelet technology JPEG 2000 can code lossless content in any quality at once. Learn more about
        this file format `here <https://wiki.fileformat.com/image/jp2/>`.'''
        raise NotImplementedError()

    @property
    def JPM(self) -> groupdocs.watermark.common.FileType:
        '''JPEG 2000 (JPM) is an image coding system and state-of-the-art image compression standard. Designed,
        using wavelet technology JPEG 2000 can code lossless content in any quality at once. Learn more about
        this file format `here <https://wiki.fileformat.com/image/jp2/>`.'''
        raise NotImplementedError()

    @property
    def WEBP(self) -> groupdocs.watermark.common.FileType:
        '''WebP, introduced by Google, is a modern raster web image file format that is based on lossless and
        lossy compression. It provides same image quality while considerably reducing the image size.
        Learn more about this file format `here <https://wiki.fileformat.com/image/webp/>`.'''
        raise NotImplementedError()

    @property
    def PDF(self) -> groupdocs.watermark.common.FileType:
        '''Portable Document Format (PDF) is a type of document created by Adobe back in 1990s. The purpose of this
        file format was to introduce a standard for representation of documents and other reference material in
        a format that is independent of application software, hardware as well as Operating System. Learn more
        about this file format `here <https://wiki.fileformat.com/view/pdf/>`.'''
        raise NotImplementedError()

    @property
    def PPT(self) -> groupdocs.watermark.common.FileType:
        '''A file with PPT extension represents PowerPoint file that consists of a collection of slides for
        displaying as SlideShow. It specifies the Binary File Format used by Microsoft PowerPoint 97-2003.
        Learn more about this file format `here <https://wiki.fileformat.com/presentation/ppt/>`.'''
        raise NotImplementedError()

    @property
    def PPTX(self) -> groupdocs.watermark.common.FileType:
        '''Files with PPTX extension are presentation files created with popular Microsoft PowerPoint application.
        Unlike the previous version of presentation file format PPT which was binary, the PPTX format is based
        on the Microsoft PowerPoint open XML presentation file format. Learn more about this file format
        `here <https://wiki.fileformat.com/presentation/pptx/>`.'''
        raise NotImplementedError()

    @property
    def PPS(self) -> groupdocs.watermark.common.FileType:
        '''PPS, PowerPoint Slide Show, files are created using Microsoft PowerPoint for Slide Show purpose.
        PPS file reading and creation is supported by Microsoft PowerPoint 97-2003. Learn more about this file format
        `here <https://wiki.fileformat.com/presentation/pps/>`.'''
        raise NotImplementedError()

    @property
    def PPSX(self) -> groupdocs.watermark.common.FileType:
        '''PPSX, Power Point Slide Show, file are created using Microsoft PowerPoint 2007 and above for
        Slide Show purpose.  Learn more about this file format
        `here <https://wiki.fileformat.com/presentation/ppsx/>`.'''
        raise NotImplementedError()

    @property
    def PPTM(self) -> groupdocs.watermark.common.FileType:
        '''Files with PPTM extension are Macro-enabled Presentation files that are created with
        Microsoft PowerPoint 2007 or higher versions. Learn more about this file format
        `here <https://wiki.fileformat.com/presentation/pptm/>`.'''
        raise NotImplementedError()

    @property
    def POTX(self) -> groupdocs.watermark.common.FileType:
        '''Files with .POTX extension represent Microsoft PowerPoint template presentations that are created with
        Microsoft PowerPoint 2007 and above. Learn more about this file format
        `here <https://wiki.fileformat.com/presentation/potx/>`.'''
        raise NotImplementedError()

    @property
    def POTM(self) -> groupdocs.watermark.common.FileType:
        '''Files with POTM extension are Microsoft PowerPoint template files with support for Macros. POTM files
        are created with PowerPoint 2007 or above and contains default settings that can be used to create
        further presentation files. Learn more about this file format
        `here <https://wiki.fileformat.com/presentation/potm/>`.'''
        raise NotImplementedError()

    @property
    def PPSM(self) -> groupdocs.watermark.common.FileType:
        '''Files with PPSM extension represent Macro-enabled Slide Show file format created with Microsoft
        PowerPoint 2007 or higher. Learn more about this file format
        `here <https://wiki.fileformat.com/presentation/ppsm/>`.'''
        raise NotImplementedError()

    @property
    def XLS(self) -> groupdocs.watermark.common.FileType:
        '''Files with XLS extension represent Excel Binary File Format. Such files can be created by Microsoft Excel
        as well as other similar spreadsheet programs such as OpenOffice Calc or Apple Numbers. Learn more about
        this file format `here <https://wiki.fileformat.com/specification/spreadsheet/xls/>`.'''
        raise NotImplementedError()

    @property
    def XLSX(self) -> groupdocs.watermark.common.FileType:
        '''XLSX is well-known format for Microsoft Excel documents that was introduced by Microsoft with the release
        of Microsoft Office 2007. Learn more about this file format
        `here <https://wiki.fileformat.com/specification/spreadsheet/xlsx/>`.'''
        raise NotImplementedError()

    @property
    def XLSM(self) -> groupdocs.watermark.common.FileType:
        '''Files with XLSM extension is a type of Spreasheet files that support Macros. Learn more about this file format
        `here <https://wiki.fileformat.com/specification/spreadsheet/xlsm/>`.'''
        raise NotImplementedError()

    @property
    def XLTX(self) -> groupdocs.watermark.common.FileType:
        '''Files with XLTX extension represent Microsoft Excel Template files that are based on the Office OpenXML
        file format specifications. Learn more about this file format
        `here <https://wiki.fileformat.com/specification/spreadsheet/xltx/>`.'''
        raise NotImplementedError()

    @property
    def XLTM(self) -> groupdocs.watermark.common.FileType:
        '''The XLTM file extension represents files that are generated by Microsoft Excel as Macro-enabled
        template files. Learn more about this file format
        `here <https://wiki.fileformat.com/specification/spreadsheet/xltm/>`.'''
        raise NotImplementedError()

    @property
    def XLSB(self) -> groupdocs.watermark.common.FileType:
        '''XLSB file format specifies the Excel Binary File Format, which is a collection of records and
        structures that specify Excel workbook content. Learn more about this file format
        `here <https://wiki.fileformat.com/specification/spreadsheet/xlsb/>`.'''
        raise NotImplementedError()

    @property
    def XLT(self) -> groupdocs.watermark.common.FileType:
        '''Files with .XLT extension are template files created with Microsoft Excel which is a spreadsheet
        application which comes as part of Microsoft Office suite. Learn more about this file format
        `here <https://wiki.fileformat.com/specification/spreadsheet/xlt/>`.'''
        raise NotImplementedError()

    @property
    def DOC(self) -> groupdocs.watermark.common.FileType:
        '''Files with .doc extension represent documents generated by Microsoft Word or other word processing
        documents in binary file format. Learn more about this file format
        `here <https://wiki.fileformat.com/word-processing/doc/>`.'''
        raise NotImplementedError()

    @property
    def DOCX(self) -> groupdocs.watermark.common.FileType:
        '''DOCX is a well-known format for Microsoft Word documents. Introduced from 2007 with the release
        of Microsoft Office 2007, the structure of this new Document format was changed from plain binary
        to a combination of XML and binary files. Learn more about this file format
        `here <https://wiki.fileformat.com/word-processing/docx/>`.'''
        raise NotImplementedError()

    @property
    def DOCM(self) -> groupdocs.watermark.common.FileType:
        '''DOCM files are Microsoft Word 2007 or higher generated documents with the ability to run macros.
        Learn more about this file format `here <https://wiki.fileformat.com/word-processing/docm/>`.'''
        raise NotImplementedError()

    @property
    def DOT(self) -> groupdocs.watermark.common.FileType:
        '''Files with .DOT extension are template files created by Microsoft Word to have pre-formatted settings
        for generation of further DOC or DOCX files. Learn more about this file format
        `here <https://wiki.fileformat.com/word-processing/dot/>`.'''
        raise NotImplementedError()

    @property
    def DOTX(self) -> groupdocs.watermark.common.FileType:
        '''Files with DOTX extension are template files created by Microsoft Word to have pre-formatted settings
        for generation of further DOCX files. Learn more about this file format
        `here <https://wiki.fileformat.com/word-processing/dotx/>`.'''
        raise NotImplementedError()

    @property
    def DOTM(self) -> groupdocs.watermark.common.FileType:
        '''A file with DOTM extension represents template file created with Microsoft Word 2007 or higher.
        Learn more about this file format `here <https://wiki.fileformat.com/word-processing/dotm/>`.'''
        raise NotImplementedError()

    @property
    def RTF(self) -> groupdocs.watermark.common.FileType:
        '''Introduced and documented by Microsoft, the Rich Text Format (RTF) represents a method of encoding
        formatted text and graphics for use within applications. The format facilitates cross-platform document
        exchange with other Microsoft Products, thus serving the purpose of interoperability. Learn more about
        this file format `here <https://wiki.fileformat.com/word-processing/rtf/>`.'''
        raise NotImplementedError()

    @property
    def ODT(self) -> groupdocs.watermark.common.FileType:
        '''ODT files are type of documents created with word processing applications that are based on OpenDocument
        Text File format. These are created with word processor applications such as free OpenOffice Writer and
        can hold content such as text, images, objects and styles. Learn more about this file format
        `here <https://wiki.fileformat.com/word-processing/odt/>`.'''
        raise NotImplementedError()

    @property
    def FLAT_OPC(self) -> groupdocs.watermark.common.FileType:
        '''Office Open XML WordprocessingML stored in a flat XML file instead of a ZIP package (.xml).
        Learn more about this file format `here <https://en.wikipedia.org/wiki/Office_Open_XML>`.'''
        raise NotImplementedError()

    @property
    def FLAT_OPC_MACRO_ENABLED(self) -> groupdocs.watermark.common.FileType:
        '''Office Open XML WordprocessingML Macro-Enabled Document stored in a flat XML file instead of a ZIP package (.xml).
        Learn more about this file format `here <https://en.wikipedia.org/wiki/Office_Open_XML>`.'''
        raise NotImplementedError()

    @property
    def FLAT_OPC_TEMPLATE(self) -> groupdocs.watermark.common.FileType:
        '''Office Open XML WordprocessingML Template (macro-free) stored in a flat XML file instead of a ZIP package (.xml).
        Learn more about this file format `here <https://en.wikipedia.org/wiki/Office_Open_XML>`.'''
        raise NotImplementedError()

    @property
    def FLAT_OPC_TEMPLATE_MACRO_ENABLED(self) -> groupdocs.watermark.common.FileType:
        '''Office Open XML WordprocessingML Macro-Enabled Template stored in a flat XML file instead of a ZIP package (.xml).
        Learn more about this file format `here <https://en.wikipedia.org/wiki/Office_Open_XML>`.'''
        raise NotImplementedError()


class IDocumentInfo:
    '''Defines the methods that are required for getting the basic document information.'''
    
    @property
    def file_type(self) -> groupdocs.watermark.common.FileType:
        '''Gets the file format description.'''
        raise NotImplementedError()
    
    @property
    def page_count(self) -> int:
        '''Gets the total page count.'''
        raise NotImplementedError()
    
    @property
    def pages(self) -> System.Collections.Generic.IList`1[[GroupDocs.Watermark.Common.PageInfo]]:
        '''Gets the collection of document pages descriptions.'''
        raise NotImplementedError()
    
    @property
    def size(self) -> int:
        '''Gets the document size in bytes.'''
        raise NotImplementedError()
    
    @property
    def is_encrypted(self) -> bool:
        '''Gets a value indicating whether the document is encrypted and requires a password to open.'''
        raise NotImplementedError()
    

class PageInfo:
    '''Represents a document page description.'''
    
    @property
    def height(self) -> float:
        '''Gets the document page height.'''
        raise NotImplementedError()
    
    @property
    def width(self) -> float:
        '''Gets the document page width.'''
        raise NotImplementedError()
    
    @property
    def page_number(self) -> int:
        '''Gets the document page number.'''
        raise NotImplementedError()
    

class Dimension:
    '''Represents dimensions of a 2d object.'''
    
    WIDTH : Dimension
    '''Object width.'''
    HEIGHT : Dimension
    '''Object height.'''

class FormatFamily:
    '''Enumeration of supported format families.'''
    
    UNKNOWN : FormatFamily
    '''Unknown format family.'''
    DIAGRAM : FormatFamily
    '''Diagram format family.'''
    EMAIL : FormatFamily
    '''Email format family.'''
    IMAGE : FormatFamily
    '''Image format family.'''
    MULTIFRAME_IMAGE : FormatFamily
    '''Multi frame image format family.'''
    PDF : FormatFamily
    '''PDF format family.'''
    PRESENTATION : FormatFamily
    '''Presentation format family.'''
    SPREADSHEET : FormatFamily
    '''Spreadsheet format family.'''
    WORD_PROCESSING : FormatFamily
    '''Word processing format family.'''

class HorizontalAlignment:
    '''Enumeration of possible horizontal alignment values.'''
    
    NONE : HorizontalAlignment
    '''No alignment (use specified position).'''
    LEFT : HorizontalAlignment
    '''Align to left.'''
    CENTER : HorizontalAlignment
    '''Center alignment.'''
    RIGHT : HorizontalAlignment
    '''Align to right.'''

class VerticalAlignment:
    '''Enumeration of possible vertical alignment values.'''
    
    NONE : VerticalAlignment
    '''No alignment (use specified position).'''
    TOP : VerticalAlignment
    '''Align to top.'''
    CENTER : VerticalAlignment
    '''Center alignment.'''
    BOTTOM : VerticalAlignment
    '''Align to bottom.'''

