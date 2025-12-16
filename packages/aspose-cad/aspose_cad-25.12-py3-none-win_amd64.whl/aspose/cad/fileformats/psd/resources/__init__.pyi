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

class GridAndGuidesResouce(aspose.cad.fileformats.psd.ResourceBlock):
    '''Represents the grid and guides resource.'''
    
    def save(self, stream : aspose.cad.StreamContainer) -> None:
        '''Saves the resource block to the specified stream.
        
        :param stream: The stream to save the resource block to.'''
        ...
    
    def validate_values(self) -> None:
        '''Validates the resource values.'''
        ...
    
    @property
    def signature(self) -> int:
        '''Gets the resource signature. Should be always '8BIM'.'''
        ...
    
    @property
    def id(self) -> int:
        '''Gets the unique identifier for the resource.'''
        ...
    
    @id.setter
    def id(self, value : int):
        '''Sets the unique identifier for the resource.'''
        ...
    
    @property
    def name(self) -> str:
        '''Gets the resource name. Pascal string, padded to make the size even (a null name consists of two bytes of 0).'''
        ...
    
    @name.setter
    def name(self, value : str):
        '''Sets the resource name. Pascal string, padded to make the size even (a null name consists of two bytes of 0).'''
        ...
    
    @property
    def data_size(self) -> int:
        ...
    
    @property
    def size(self) -> int:
        '''Gets the resource block size in bytes including its data.'''
        ...
    
    @property
    def minimal_version(self) -> int:
        ...
    
    @classmethod
    @property
    def RESOUCE_BLOCK_SIGNATURE(cls) -> int:
        ...
    
    @property
    def guide_count(self) -> int:
        ...
    
    @property
    def header_version(self) -> int:
        ...
    
    @header_version.setter
    def header_version(self, value : int):
        ...
    
    @property
    def grid_cycle_x(self) -> int:
        ...
    
    @grid_cycle_x.setter
    def grid_cycle_x(self, value : int):
        ...
    
    @property
    def grid_cycle_y(self) -> int:
        ...
    
    @grid_cycle_y.setter
    def grid_cycle_y(self, value : int):
        ...
    
    ...

class Thumbnail4Resource(ThumbnailResource):
    '''Represents the thumbnail resource for psd 4.0.'''
    
    def save(self, stream : aspose.cad.StreamContainer) -> None:
        '''Saves the resource block to the specified stream.
        
        :param stream: The stream to save the resource block to.'''
        ...
    
    def validate_values(self) -> None:
        '''Validates the resource values.'''
        ...
    
    @property
    def signature(self) -> int:
        '''Gets the resource signature. Should be always '8BIM'.'''
        ...
    
    @property
    def id(self) -> int:
        '''Gets the unique identifier for the resource.'''
        ...
    
    @id.setter
    def id(self, value : int):
        '''Sets the unique identifier for the resource.'''
        ...
    
    @property
    def name(self) -> str:
        '''Gets the resource name. Pascal string, padded to make the size even (a null name consists of two bytes of 0).'''
        ...
    
    @name.setter
    def name(self, value : str):
        '''Sets the resource name. Pascal string, padded to make the size even (a null name consists of two bytes of 0).'''
        ...
    
    @property
    def data_size(self) -> int:
        ...
    
    @property
    def size(self) -> int:
        '''Gets the resource block size in bytes including its data.'''
        ...
    
    @property
    def minimal_version(self) -> int:
        ...
    
    @classmethod
    @property
    def RESOUCE_BLOCK_SIGNATURE(cls) -> int:
        ...
    
    @property
    def jpeg_options(self) -> aspose.cad.imageoptions.JpegOptions:
        ...
    
    @jpeg_options.setter
    def jpeg_options(self, value : aspose.cad.imageoptions.JpegOptions):
        ...
    
    @property
    def width(self) -> int:
        '''Gets the width of thumbnail in pixels.'''
        ...
    
    @width.setter
    def width(self, value : int):
        '''Sets the width of thumbnail in pixels.'''
        ...
    
    @property
    def height(self) -> int:
        '''Gets the height of thumbnail in pixels.'''
        ...
    
    @height.setter
    def height(self, value : int):
        '''Sets the height of thumbnail in pixels.'''
        ...
    
    @property
    def width_bytes(self) -> int:
        ...
    
    @property
    def total_size(self) -> int:
        ...
    
    @property
    def size_after_compression(self) -> int:
        ...
    
    @property
    def bits_pixel(self) -> int:
        ...
    
    @bits_pixel.setter
    def bits_pixel(self, value : int):
        ...
    
    @property
    def planes_count(self) -> int:
        ...
    
    @planes_count.setter
    def planes_count(self, value : int):
        ...
    
    @property
    def thumbnail_argb_32_data(self) -> List[int]:
        ...
    
    @thumbnail_argb_32_data.setter
    def thumbnail_argb_32_data(self, value : List[int]):
        ...
    
    @property
    def thumbnail_data(self) -> List[aspose.cad.Color]:
        ...
    
    @thumbnail_data.setter
    def thumbnail_data(self, value : List[aspose.cad.Color]):
        ...
    
    ...

class ThumbnailResource(aspose.cad.fileformats.psd.ResourceBlock):
    '''The thumbnail resource block.'''
    
    def save(self, stream : aspose.cad.StreamContainer) -> None:
        '''Saves the resource block to the specified stream.
        
        :param stream: The stream to save the resource block to.'''
        ...
    
    def validate_values(self) -> None:
        '''Validates the resource values.'''
        ...
    
    @property
    def signature(self) -> int:
        '''Gets the resource signature. Should be always '8BIM'.'''
        ...
    
    @property
    def id(self) -> int:
        '''Gets the unique identifier for the resource.'''
        ...
    
    @id.setter
    def id(self, value : int):
        '''Sets the unique identifier for the resource.'''
        ...
    
    @property
    def name(self) -> str:
        '''Gets the resource name. Pascal string, padded to make the size even (a null name consists of two bytes of 0).'''
        ...
    
    @name.setter
    def name(self, value : str):
        '''Sets the resource name. Pascal string, padded to make the size even (a null name consists of two bytes of 0).'''
        ...
    
    @property
    def data_size(self) -> int:
        ...
    
    @property
    def size(self) -> int:
        '''Gets the resource block size in bytes including its data.'''
        ...
    
    @property
    def minimal_version(self) -> int:
        ...
    
    @classmethod
    @property
    def RESOUCE_BLOCK_SIGNATURE(cls) -> int:
        ...
    
    @property
    def jpeg_options(self) -> aspose.cad.imageoptions.JpegOptions:
        ...
    
    @jpeg_options.setter
    def jpeg_options(self, value : aspose.cad.imageoptions.JpegOptions):
        ...
    
    @property
    def width(self) -> int:
        '''Gets the width of thumbnail in pixels.'''
        ...
    
    @width.setter
    def width(self, value : int):
        '''Sets the width of thumbnail in pixels.'''
        ...
    
    @property
    def height(self) -> int:
        '''Gets the height of thumbnail in pixels.'''
        ...
    
    @height.setter
    def height(self, value : int):
        '''Sets the height of thumbnail in pixels.'''
        ...
    
    @property
    def width_bytes(self) -> int:
        ...
    
    @property
    def total_size(self) -> int:
        ...
    
    @property
    def size_after_compression(self) -> int:
        ...
    
    @property
    def bits_pixel(self) -> int:
        ...
    
    @bits_pixel.setter
    def bits_pixel(self, value : int):
        ...
    
    @property
    def planes_count(self) -> int:
        ...
    
    @planes_count.setter
    def planes_count(self, value : int):
        ...
    
    @property
    def thumbnail_argb_32_data(self) -> List[int]:
        ...
    
    @thumbnail_argb_32_data.setter
    def thumbnail_argb_32_data(self, value : List[int]):
        ...
    
    @property
    def thumbnail_data(self) -> List[aspose.cad.Color]:
        ...
    
    @thumbnail_data.setter
    def thumbnail_data(self, value : List[aspose.cad.Color]):
        ...
    
    ...

class TransparencyIndexResource(aspose.cad.fileformats.psd.ResourceBlock):
    '''The transparency index resource block.'''
    
    def save(self, stream : aspose.cad.StreamContainer) -> None:
        '''Saves the resource block to the specified stream.
        
        :param stream: The stream to save the resource block to.'''
        ...
    
    def validate_values(self) -> None:
        '''Validates the resource values.'''
        ...
    
    @property
    def signature(self) -> int:
        '''Gets the resource signature. Should be always '8BIM'.'''
        ...
    
    @property
    def id(self) -> int:
        '''Gets the unique identifier for the resource.'''
        ...
    
    @id.setter
    def id(self, value : int):
        '''Sets the unique identifier for the resource.'''
        ...
    
    @property
    def name(self) -> str:
        '''Gets the resource name. Pascal string, padded to make the size even (a null name consists of two bytes of 0).'''
        ...
    
    @name.setter
    def name(self, value : str):
        '''Sets the resource name. Pascal string, padded to make the size even (a null name consists of two bytes of 0).'''
        ...
    
    @property
    def data_size(self) -> int:
        ...
    
    @property
    def size(self) -> int:
        '''Gets the resource block size in bytes including its data.'''
        ...
    
    @property
    def minimal_version(self) -> int:
        ...
    
    @classmethod
    @property
    def RESOUCE_BLOCK_SIGNATURE(cls) -> int:
        ...
    
    @property
    def transparency_index(self) -> int:
        ...
    
    @transparency_index.setter
    def transparency_index(self, value : int):
        ...
    
    ...

class UnknownResource(aspose.cad.fileformats.psd.ResourceBlock):
    '''The unknown resource. When a resource block is not recognized then this resource block is created.'''
    
    def save(self, stream : aspose.cad.StreamContainer) -> None:
        '''Saves the resource block to the specified stream.
        
        :param stream: The stream to save the resource block to.'''
        ...
    
    def validate_values(self) -> None:
        '''Validates the resource values.'''
        ...
    
    @property
    def signature(self) -> int:
        '''Gets the resource signature. Should be always '8BIM'.'''
        ...
    
    @property
    def id(self) -> int:
        '''Gets the unique identifier for the resource.'''
        ...
    
    @id.setter
    def id(self, value : int):
        '''Sets the unique identifier for the resource.'''
        ...
    
    @property
    def name(self) -> str:
        '''Gets the resource name. Pascal string, padded to make the size even (a null name consists of two bytes of 0).'''
        ...
    
    @name.setter
    def name(self, value : str):
        '''Sets the resource name. Pascal string, padded to make the size even (a null name consists of two bytes of 0).'''
        ...
    
    @property
    def data_size(self) -> int:
        ...
    
    @property
    def size(self) -> int:
        '''Gets the resource block size in bytes including its data.'''
        ...
    
    @property
    def minimal_version(self) -> int:
        ...
    
    @classmethod
    @property
    def RESOUCE_BLOCK_SIGNATURE(cls) -> int:
        ...
    
    @property
    def data(self) -> bytes:
        '''Gets the resource data.'''
        ...
    
    ...

class XmpResouce(aspose.cad.fileformats.psd.ResourceBlock):
    '''Represents the XMP metadata resource.'''
    
    def save(self, stream : aspose.cad.StreamContainer) -> None:
        '''Saves the resource block to the specified stream.
        
        :param stream: The stream to save the resource block to.'''
        ...
    
    def validate_values(self) -> None:
        '''Validates the resource values.'''
        ...
    
    @property
    def signature(self) -> int:
        '''Gets the resource signature. Should be always '8BIM'.'''
        ...
    
    @property
    def id(self) -> int:
        '''Gets the unique identifier for the resource.'''
        ...
    
    @id.setter
    def id(self, value : int):
        '''Sets the unique identifier for the resource.'''
        ...
    
    @property
    def name(self) -> str:
        '''Gets the resource name. Pascal string, padded to make the size even (a null name consists of two bytes of 0).'''
        ...
    
    @name.setter
    def name(self, value : str):
        '''Sets the resource name. Pascal string, padded to make the size even (a null name consists of two bytes of 0).'''
        ...
    
    @property
    def data_size(self) -> int:
        ...
    
    @property
    def size(self) -> int:
        '''Gets the resource block size in bytes including its data.'''
        ...
    
    @property
    def minimal_version(self) -> int:
        ...
    
    @classmethod
    @property
    def RESOUCE_BLOCK_SIGNATURE(cls) -> int:
        ...
    
    ...

