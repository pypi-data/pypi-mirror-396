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

class AttributeFormat:
    '''Defines the formatting in which a byte sequence can be encoded/decoded to attribute elements.'''
    
    @staticmethod
    def are_equal(a : aspose.cad.fileformats.glb.memory.AttributeFormat, b : aspose.cad.fileformats.glb.memory.AttributeFormat) -> bool:
        ...
    
    def equals(self, other : aspose.cad.fileformats.glb.memory.AttributeFormat) -> bool:
        ...
    
    @property
    def byte_size_padded(self) -> int:
        ...
    
    @property
    def ENCODING(self) -> aspose.cad.fileformats.glb.EncodingType:
        ...
    
    @property
    def DIMENSIONS(self) -> aspose.cad.fileformats.glb.DimensionType:
        ...
    
    @property
    def NORMALIZED(self) -> bool:
        ...
    
    @property
    def BYTE_SIZE(self) -> int:
        ...
    
    ...

class IntegerArray:
    '''Wraps an encoded :py:class:`System.ArraySegment`1` and exposes it as an :py:class:`System.Collections.Generic.IList`1`.'''
    
    @overload
    def fill(self, values : Iterable[int], dst_start : int) -> None:
        ...
    
    @overload
    def fill(self, values : Iterable[int], dst_start : int) -> None:
        ...
    
    ...

class Matrix2x2Array:
    '''Wraps an encoded :py:class:`System.ArraySegment`1` and exposes it as an :py:class:`System.Collections.Generic.IList`1`.'''
    
    @property
    def count(self) -> int:
        ...
    
    ...

class Matrix3x2Array:
    '''Wraps an encoded :py:class:`System.ArraySegment`1` and exposes it as an :py:class:`System.Collections.Generic.IList`1`.'''
    
    @property
    def count(self) -> int:
        ...
    
    ...

class Matrix3x3Array:
    '''Wraps an encoded :py:class:`System.ArraySegment`1` and exposes it as an :py:class:`System.Collections.Generic.IList`1`.'''
    
    @property
    def count(self) -> int:
        ...
    
    ...

class Matrix4x3Array:
    '''Wraps an encoded :py:class:`System.ArraySegment`1` and exposes it as an :py:class:`System.Collections.Generic.IList`1`.'''
    
    @property
    def count(self) -> int:
        ...
    
    ...

class Matrix4x4Array:
    '''Wraps an encoded :py:class:`System.ArraySegment`1` and exposes it as an :py:class:`System.Collections.Generic.IList`1`.'''
    
    @property
    def count(self) -> int:
        ...
    
    ...

class MemoryAccessor:
    '''Wraps a :py:class:`System.ArraySegment`1` decoding it and exposing its content as arrays of different types.'''
    
    def as_vector_2_array(self) -> aspose.cad.fileformats.glb.memory.Vector2Array:
        ...
    
    def as_vector_3_array(self) -> aspose.cad.fileformats.glb.memory.Vector3Array:
        ...
    
    def as_vector_4_array(self) -> aspose.cad.fileformats.glb.memory.Vector4Array:
        ...
    
    def as_quaternion_array(self) -> aspose.cad.fileformats.glb.memory.QuaternionArray:
        ...
    
    def as_matrix_2x2_array(self) -> aspose.cad.fileformats.glb.memory.Matrix2x2Array:
        ...
    
    def as_matrix_3x3_array(self) -> aspose.cad.fileformats.glb.memory.Matrix3x3Array:
        ...
    
    def as_matrix_4x4_array(self) -> aspose.cad.fileformats.glb.memory.Matrix4x4Array:
        ...
    
    def as_multi_array(self, dimensions : int) -> aspose.cad.fileformats.glb.memory.MultiArray:
        ...
    
    @staticmethod
    def sanitize_weights_sum(weights0 : aspose.cad.fileformats.glb.memory.MemoryAccessor, weights1 : aspose.cad.fileformats.glb.memory.MemoryAccessor) -> None:
        ...
    
    @staticmethod
    def verify_weights_sum(weights0 : aspose.cad.fileformats.glb.memory.MemoryAccessor, weights1 : aspose.cad.fileformats.glb.memory.MemoryAccessor) -> None:
        ...
    
    @staticmethod
    def verify_accessor_bounds(memory : aspose.cad.fileformats.glb.memory.MemoryAccessor, min : List[float], max : List[float]) -> None:
        ...
    
    @staticmethod
    def verify_vertex_indices(memory : aspose.cad.fileformats.glb.memory.MemoryAccessor, vertex_count : int) -> None:
        ...
    
    ...

class MemoryImage:
    '''Represents an image file stored as an in-memory byte array'''
    
    def to_debugger_display(self) -> str:
        ...
    
    @staticmethod
    def try_parse_mime64(mime_64content : str, image : Any) -> bool:
        '''Tries to parse a Mime64 string to :py:class:`aspose.cad.fileformats.glb.memory.MemoryImage`
        
        :param mime_64content: The Mime64 string source.
        :param image: if decoding succeeds, it will contain the image file.
        :returns: true if decoding succeeded.'''
        ...
    
    @staticmethod
    def are_equal(a : aspose.cad.fileformats.glb.memory.MemoryImage, b : aspose.cad.fileformats.glb.memory.MemoryImage) -> bool:
        ...
    
    def equals(self, other : aspose.cad.fileformats.glb.memory.MemoryImage) -> bool:
        ...
    
    def open(self) -> io.RawIOBase:
        '''Opens the image file for reading its contents
        
        :returns: A read only :py:class:`io.RawIOBase`.'''
        ...
    
    def save_to_file(self, file_path : str) -> None:
        '''Saves the image stored in this :py:class:`aspose.cad.fileformats.glb.memory.MemoryImage` to a file.
        
        :param file_path: A destination file path, with an extension matching :py:attr:`aspose.cad.fileformats.glb.memory.MemoryImage.file_extension`'''
        ...
    
    def is_image_of_type(self, format : str) -> bool:
        '''identifies an image of a specific type.
        
        :param format: A string representing the format: png, jpg, dds...
        :returns: True if this image is of the given type.'''
        ...
    
    @classmethod
    @property
    def empty(cls) -> aspose.cad.fileformats.glb.memory.MemoryImage:
        ...
    
    @property
    def is_empty(self) -> bool:
        ...
    
    @property
    def content(self) -> bytes:
        '''Gets the file bytes of the image.'''
        ...
    
    @property
    def source_path(self) -> str:
        ...
    
    @property
    def is_png(self) -> bool:
        ...
    
    @property
    def is_jpg(self) -> bool:
        ...
    
    @property
    def is_dds(self) -> bool:
        ...
    
    @property
    def is_webp(self) -> bool:
        ...
    
    @property
    def is_ktx2(self) -> bool:
        ...
    
    @property
    def is_extended_format(self) -> bool:
        ...
    
    @property
    def is_valid(self) -> bool:
        ...
    
    @property
    def file_extension(self) -> str:
        ...
    
    @property
    def mime_type(self) -> str:
        ...
    
    ...

class MultiArray:
    '''Wraps an encoded :py:class:`System.ArraySegment`1` and exposes it as an IList{Single[]}/>.'''
    
    def copy_item_to(self, index : int, dst_item : List[float]) -> None:
        ...
    
    def fill(self, values : Iterable[List[float]], dst_start : int) -> None:
        ...
    
    @property
    def dimensions(self) -> int:
        ...
    
    ...

class QuaternionArray:
    '''Wraps an encoded :py:class:`System.ArraySegment`1` and exposes it as an :py:class:`System.Collections.Generic.IList`1`.'''
    
    @property
    def count(self) -> int:
        ...
    
    ...

class ScalarArray:
    '''Wraps an encoded :py:class:`System.ArraySegment`1` and exposes it as an :py:class:`System.Collections.Generic.IList`1`.'''
    
    def fill(self, values : Iterable[float], dst_start : int) -> None:
        ...
    
    ...

class Vector2Array:
    '''Wraps an encoded :py:class:`System.ArraySegment`1` and exposes it as an :py:class:`System.Collections.Generic.IList`1`.'''
    
    @property
    def count(self) -> int:
        ...
    
    ...

class Vector3Array:
    '''Wraps an encoded :py:class:`System.ArraySegment`1` and exposes it as an :py:class:`System.Collections.Generic.IList`1`.'''
    
    @property
    def count(self) -> int:
        ...
    
    ...

class Vector4Array:
    '''Wraps an encoded :py:class:`System.ArraySegment`1` and exposes it as an :py:class:`System.Collections.Generic.IList`1`.'''
    
    @property
    def count(self) -> int:
        ...
    
    ...

