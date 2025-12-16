from typing import List, Optional, Dict, Iterable
import io
import aspose.pycore
import aspose.pydrawing
import aspose.cad
import aspose.cad.annotations
import aspose.cad.cadexceptions
import aspose.cad.cadexceptions.compressors
import aspose.cad.cadexceptions.imageformats
import aspose.cad.exif
import aspose.cad.exif.enums
import aspose.cad.fileformats
import aspose.cad.fileformats.bitmap
import aspose.cad.fileformats.bmp
import aspose.cad.fileformats.cad
import aspose.cad.fileformats.cad.cadconsts
import aspose.cad.fileformats.cad.cadobjects
import aspose.cad.fileformats.cad.cadobjects.acadtable
import aspose.cad.fileformats.cad.cadobjects.assoc
import aspose.cad.fileformats.cad.cadobjects.attentities
import aspose.cad.fileformats.cad.cadobjects.background
import aspose.cad.fileformats.cad.cadobjects.blocks
import aspose.cad.fileformats.cad.cadobjects.datatable
import aspose.cad.fileformats.cad.cadobjects.dictionary
import aspose.cad.fileformats.cad.cadobjects.dimassoc
import aspose.cad.fileformats.cad.cadobjects.field
import aspose.cad.fileformats.cad.cadobjects.hatch
import aspose.cad.fileformats.cad.cadobjects.mlinestyleobject
import aspose.cad.fileformats.cad.cadobjects.objectcontextdata
import aspose.cad.fileformats.cad.cadobjects.perssubentmanager
import aspose.cad.fileformats.cad.cadobjects.polylines
import aspose.cad.fileformats.cad.cadobjects.section
import aspose.cad.fileformats.cad.cadobjects.sunstudy
import aspose.cad.fileformats.cad.cadobjects.tablestyle
import aspose.cad.fileformats.cad.cadobjects.underlaydefinition
import aspose.cad.fileformats.cad.cadobjects.vertices
import aspose.cad.fileformats.cad.cadobjects.wipeout
import aspose.cad.fileformats.cad.cadparameters
import aspose.cad.fileformats.cad.cadtables
import aspose.cad.fileformats.cad.dwg
import aspose.cad.fileformats.cad.dwg.acdbobjects
import aspose.cad.fileformats.cad.dwg.appinfo
import aspose.cad.fileformats.cad.dwg.r2004
import aspose.cad.fileformats.cad.dwg.revhistory
import aspose.cad.fileformats.cad.dwg.summaryinfo
import aspose.cad.fileformats.cad.dwg.vbaproject
import aspose.cad.fileformats.cf2
import aspose.cad.fileformats.cgm
import aspose.cad.fileformats.cgm.classes
import aspose.cad.fileformats.cgm.commands
import aspose.cad.fileformats.cgm.elements
import aspose.cad.fileformats.cgm.enums
import aspose.cad.fileformats.cgm.export
import aspose.cad.fileformats.cgm.import
import aspose.cad.fileformats.collada
import aspose.cad.fileformats.collada.fileparser
import aspose.cad.fileformats.collada.fileparser.elements
import aspose.cad.fileformats.dgn
import aspose.cad.fileformats.dgn.dgnelements
import aspose.cad.fileformats.dgn.dgntransform
import aspose.cad.fileformats.dgn.v8
import aspose.cad.fileformats.dgn.v8.model
import aspose.cad.fileformats.dgn.v8.model.structs
import aspose.cad.fileformats.dgn.v8.model.tree
import aspose.cad.fileformats.dicom
import aspose.cad.fileformats.draco
import aspose.cad.fileformats.dwf
import aspose.cad.fileformats.dwf.dwfxps
import aspose.cad.fileformats.dwf.dwfxps.fixedpage
import aspose.cad.fileformats.dwf.dwfxps.fixedpage.dto
import aspose.cad.fileformats.dwf.emodelinterface
import aspose.cad.fileformats.dwf.eplotinterface
import aspose.cad.fileformats.dwf.whip
import aspose.cad.fileformats.dwf.whip.objects
import aspose.cad.fileformats.dwf.whip.objects.drawable
import aspose.cad.fileformats.dwf.whip.objects.drawable.text
import aspose.cad.fileformats.dwf.whip.objects.service
import aspose.cad.fileformats.dwf.whip.objects.service.font
import aspose.cad.fileformats.fbx
import aspose.cad.fileformats.glb
import aspose.cad.fileformats.glb.animations
import aspose.cad.fileformats.glb.geometry
import aspose.cad.fileformats.glb.geometry.vertextypes
import aspose.cad.fileformats.glb.io
import aspose.cad.fileformats.glb.materials
import aspose.cad.fileformats.glb.memory
import aspose.cad.fileformats.glb.runtime
import aspose.cad.fileformats.glb.scenes
import aspose.cad.fileformats.glb.toolkit
import aspose.cad.fileformats.glb.transforms
import aspose.cad.fileformats.glb.validation
import aspose.cad.fileformats.ifc
import aspose.cad.fileformats.ifc.header
import aspose.cad.fileformats.ifc.ifc2x3
import aspose.cad.fileformats.ifc.ifc2x3.entities
import aspose.cad.fileformats.ifc.ifc2x3.types
import aspose.cad.fileformats.ifc.ifc4
import aspose.cad.fileformats.ifc.ifc4.entities
import aspose.cad.fileformats.ifc.ifc4.types
import aspose.cad.fileformats.ifc.ifc4x3
import aspose.cad.fileformats.ifc.ifc4x3.entities
import aspose.cad.fileformats.ifc.ifc4x3.types
import aspose.cad.fileformats.iges
import aspose.cad.fileformats.iges.commondefinitions
import aspose.cad.fileformats.iges.drawables
import aspose.cad.fileformats.jpeg
import aspose.cad.fileformats.jpeg2000
import aspose.cad.fileformats.obj
import aspose.cad.fileformats.obj.elements
import aspose.cad.fileformats.obj.mtl
import aspose.cad.fileformats.obj.vertexdata
import aspose.cad.fileformats.obj.vertexdata.index
import aspose.cad.fileformats.pdf
import aspose.cad.fileformats.plt
import aspose.cad.fileformats.plt.pltparsers
import aspose.cad.fileformats.plt.pltparsers.pltparser
import aspose.cad.fileformats.plt.pltparsers.pltparser.pltplotitems
import aspose.cad.fileformats.png
import aspose.cad.fileformats.postscript
import aspose.cad.fileformats.psd
import aspose.cad.fileformats.psd.resources
import aspose.cad.fileformats.shx
import aspose.cad.fileformats.stl
import aspose.cad.fileformats.stl.stlobjects
import aspose.cad.fileformats.stp
import aspose.cad.fileformats.stp.helpers
import aspose.cad.fileformats.stp.items
import aspose.cad.fileformats.stp.reader
import aspose.cad.fileformats.stp.stplibrary
import aspose.cad.fileformats.stp.stplibrary.core
import aspose.cad.fileformats.stp.stplibrary.core.models
import aspose.cad.fileformats.svg
import aspose.cad.fileformats.threeds
import aspose.cad.fileformats.threeds.elements
import aspose.cad.fileformats.tiff
import aspose.cad.fileformats.tiff.enums
import aspose.cad.fileformats.tiff.filemanagement
import aspose.cad.fileformats.tiff.instancefactory
import aspose.cad.fileformats.tiff.tifftagtypes
import aspose.cad.fileformats.u3d
import aspose.cad.fileformats.u3d.elements
import aspose.cad.fileformats.u3d.helpers
import aspose.cad.imageoptions
import aspose.cad.imageoptions.svgoptionsparameters
import aspose.cad.measurement
import aspose.cad.palettehelper
import aspose.cad.primitives
import aspose.cad.sources
import aspose.cad.timeprovision
import aspose.cad.watermarkguard

class FontStoringArgs:
    '''Parameters for font storage in SVG'''
    
    @property
    def source_font_file_name(self) -> str:
        ...
    
    @property
    def source_font_stream(self) -> io.RawIOBase:
        ...
    
    @property
    def dest_font_stream(self) -> io.RawIOBase:
        ...
    
    @dest_font_stream.setter
    def dest_font_stream(self, value : io.RawIOBase):
        ...
    
    @property
    def font_file_uri(self) -> str:
        ...
    
    @font_file_uri.setter
    def font_file_uri(self, value : str):
        ...
    
    @property
    def dispose_stream(self) -> bool:
        ...
    
    @dispose_stream.setter
    def dispose_stream(self, value : bool):
        ...
    
    @property
    def font_store_type(self) -> aspose.cad.imageoptions.svgoptionsparameters.FontStoreType:
        ...
    
    @font_store_type.setter
    def font_store_type(self, value : aspose.cad.imageoptions.svgoptionsparameters.FontStoreType):
        ...
    
    ...

class ISvgResourceKeeperCallback:
    '''The svg callback interface'''
    
    def on_image_resource_ready(self, image_data : bytes, image_type : aspose.cad.imageoptions.svgoptionsparameters.SvgImageType, suggested_file_name : str, use_embedded_image : Any) -> str:
        '''Called for each raster image in SVG. Use it to specify how to store the raster image.
        
        :param image_data: The bytes of the raster image content
        :param image_type: Type of the image.
        :param suggested_file_name: Name of the suggested file.
        :param use_embedded_image: if set to ``true`` then image will be embedded into SVG.
        :returns: Should return path to saved resource. Path will be used in SVG image to refer to raster content. Path should be relative to target SVG document.'''
        ...
    
    def on_font_resource_ready(self, args : aspose.cad.imageoptions.svgoptionsparameters.FontStoringArgs) -> None:
        '''Called for each font used in SVG. Use it to specify how to store the font.
        
        :param args: The font storage parameters'''
        ...
    
    def on_svg_document_ready(self, html_data : bytes, suggested_file_name : str) -> str:
        '''Called when SVG document is ready.
        
        :param html_data: The SVG document conent bytes.
        :param suggested_file_name: Suggested name for the file.
        :returns: Should return path to saved svg document.'''
        ...
    
    ...

class FontStoreType:
    '''The font store type'''
    
    @classmethod
    @property
    def NONE(cls) -> FontStoreType:
        '''The none, fonts not stored'''
        ...
    
    @classmethod
    @property
    def STREAM(cls) -> FontStoreType:
        '''The Stream, fonts stored to stream'''
        ...
    
    @classmethod
    @property
    def EMBEDDED(cls) -> FontStoreType:
        '''The embedded, fonts embedded in svg file as base64'''
        ...
    
    ...

class SvgColorMode:
    '''Сolor mode for SVG images.'''
    
    @classmethod
    @property
    def GRAYSCALE(cls) -> SvgColorMode:
        '''The Grayscale image.'''
        ...
    
    @classmethod
    @property
    def Y_CB_CR(cls) -> SvgColorMode:
        '''YCbCr image, standard option for SVG images.'''
        ...
    
    @classmethod
    @property
    def CMYK(cls) -> SvgColorMode:
        '''CMYK image.'''
        ...
    
    @classmethod
    @property
    def YCCK(cls) -> SvgColorMode:
        '''The YCCK color image.'''
        ...
    
    @classmethod
    @property
    def RGB(cls) -> SvgColorMode:
        '''The RGB Color mode.'''
        ...
    
    ...

class SvgImageType:
    '''Represents type of raster image within SVG image.'''
    
    @classmethod
    @property
    def JPEG(cls) -> SvgImageType:
        '''JPEG JFIF.'''
        ...
    
    @classmethod
    @property
    def PNG(cls) -> SvgImageType:
        '''Portable Network Graphics.'''
        ...
    
    @classmethod
    @property
    def BMP(cls) -> SvgImageType:
        '''Windows Bitmap.'''
        ...
    
    @classmethod
    @property
    def GIF(cls) -> SvgImageType:
        '''Gif image format'''
        ...
    
    @classmethod
    @property
    def TIFF(cls) -> SvgImageType:
        '''Tiff image format'''
        ...
    
    @classmethod
    @property
    def UNKNOWN(cls) -> SvgImageType:
        '''Unknown format'''
        ...
    
    ...

