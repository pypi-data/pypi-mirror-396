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

class TiffStreamReader(TiffStreamSeeker):
    '''The tiff stream for handling little endian tiff file format.'''
    
    @overload
    def read_bytes(self, array : bytes, array_index : int, position : int, count : int) -> int:
        '''Reads an array of byte values from the stream.
        
        :param array: The array to fill.
        :param array_index: The array index to start putting values to.
        :param position: The stream position to read from.
        :param count: The elements count to read.
        :returns: The array of byte values.'''
        ...
    
    @overload
    def read_bytes(self, position : int, count : int) -> bytes:
        '''Reads an array of unsigned byte values from the stream.
        
        :param position: The position to read from.
        :param count: The elements count.
        :returns: The array of unsigned byte values.'''
        ...
    
    def read_double(self, position : int) -> float:
        '''Read a single double value from the stream.
        
        :param position: The position to read from.
        :returns: The single double value.'''
        ...
    
    def read_double_array(self, position : int, count : int) -> List[float]:
        '''Reads an array of double values from the stream.
        
        :param position: The position to read from.
        :param count: The elements count.
        :returns: The array of double values.'''
        ...
    
    def read_float(self, position : int) -> float:
        '''Read a single float value from the stream.
        
        :param position: The position to read from.
        :returns: The single float value.'''
        ...
    
    def read_float_array(self, position : int, count : int) -> List[float]:
        '''Reads an array of float values from the stream.
        
        :param position: The position to read from.
        :param count: The elements count.
        :returns: The array of float values.'''
        ...
    
    def read_rational(self, position : int) -> aspose.cad.fileformats.tiff.TiffRational:
        '''Read a single rational number value from the stream.
        
        :param position: The position to read from.
        :returns: The rational number.'''
        ...
    
    def read_s_rational(self, position : int) -> aspose.cad.fileformats.tiff.TiffSRational:
        '''Read a single signed rational number value from the stream.
        
        :param position: The position to read from.
        :returns: The signed rational number.'''
        ...
    
    def read_rational_array(self, position : int, count : int) -> List[aspose.cad.fileformats.tiff.TiffRational]:
        '''Reads an array of rational values from the stream.
        
        :param position: The position to read from.
        :param count: The elements count.
        :returns: The array of rational values.'''
        ...
    
    def read_s_rational_array(self, position : int, count : int) -> List[aspose.cad.fileformats.tiff.TiffSRational]:
        '''Reads an array of signed rational values from the stream.
        
        :param position: The position to read from.
        :param count: The elements count.
        :returns: The array of signed rational values.'''
        ...
    
    def read_s_byte(self, position : int) -> sbyte:
        '''Reads signed byte data from the stream.
        
        :param position: The position to read from.
        :returns: The signed byte value.'''
        ...
    
    def read_s_byte_array(self, position : int, count : int) -> List[sbyte]:
        '''Reads an array of signed byte values from the stream.
        
        :param position: The position to read from.
        :param count: The elements count.
        :returns: The array of signed byte values.'''
        ...
    
    def read_s_long(self, position : int) -> int:
        '''Read signed integer value from the stream.
        
        :param position: The position to read from.
        :returns: A signed integer value.'''
        ...
    
    def read_s_long_array(self, position : int, count : int) -> List[int]:
        '''Reads an array of signed integer values from the stream.
        
        :param position: The position to read from.
        :param count: The elements count.
        :returns: The array of signed integer values.'''
        ...
    
    def read_s_short(self, position : int) -> int:
        '''Read signed short value from the stream.
        
        :param position: The position to read from.
        :returns: A signed short value.'''
        ...
    
    def read_s_short_array(self, position : int, count : int) -> List[int]:
        '''Reads an array of signed short values from the stream.
        
        :param position: The position to read from.
        :param count: The elements count.
        :returns: The array of signed short values.'''
        ...
    
    def read_u_int(self, position : int) -> int:
        '''Read unsigned integer value from the stream.
        
        :param position: The position to read from.
        :returns: An unsigned integer value.'''
        ...
    
    def read_u_int_array(self, position : int, count : int) -> List[int]:
        '''Reads an array of unsigned integer values from the stream.
        
        :param position: The position to read from.
        :param count: The elements count.
        :returns: The array of unsigned integer values.'''
        ...
    
    def read_u_long(self, position : int) -> int:
        '''Read unsigned integer value from the stream.
        
        :param position: The position to read from.
        :returns: An unsigned integer value.'''
        ...
    
    def read_u_long_array(self, position : int, count : int) -> List[int]:
        '''Reads an array of unsigned integer values from the stream.
        
        :param position: The position to read from.
        :param count: The elements count.
        :returns: The array of unsigned integer values.'''
        ...
    
    def read_u_short(self, position : int) -> int:
        '''Read unsigned short value from the stream.
        
        :param position: The position to read from.
        :returns: An unsigned short value.'''
        ...
    
    def read_u_short_array(self, position : int, count : int) -> List[int]:
        '''Reads an array of unsigned integer values from the stream.
        
        :param position: The position to read from.
        :param count: The elements count.
        :returns: The array of unsigned integer values.'''
        ...
    
    def to_stream_container(self, start_position : int) -> aspose.cad.StreamContainer:
        '''Converts the underlying data to the stream container.
        
        :param start_position: The start position to start conversion from.
        :returns: The :py:class:`aspose.cad.StreamContainer` with converted data.'''
        ...
    
    @property
    def length(self) -> int:
        '''Gets the reader length.'''
        ...
    
    @property
    def throw_exceptions(self) -> bool:
        ...
    
    @throw_exceptions.setter
    def throw_exceptions(self, value : bool):
        ...
    
    ...

class TiffStreamSeeker:
    '''Class providing Tiff byte-size offsets for reading/writing.'''
    
    ...

class TiffStreamWriter:
    '''Tiff stream writer.'''
    
    @overload
    def write(self, data : bytes, offset : int, data_length : int) -> None:
        '''Writes the specified data.
        
        :param data: The data to write.
        :param offset: The data offset.
        :param data_length: Length of the data to writer.'''
        ...
    
    @overload
    def write(self, data : bytes) -> None:
        '''Writes the specified data.
        
        :param data: The data to write.'''
        ...
    
    def write_double(self, data : float) -> None:
        '''Writes a single double value to the stream.
        
        :param data: The value to write.'''
        ...
    
    def write_double_array(self, data : List[float]) -> None:
        '''Writes an array of double values to the stream.
        
        :param data: The array to write.'''
        ...
    
    def write_float(self, data : float) -> None:
        '''Writes a single float value to the stream.
        
        :param data: The value to write.'''
        ...
    
    def write_float_array(self, data : List[float]) -> None:
        '''Writes an array of float values to the stream.
        
        :param data: The array to write.'''
        ...
    
    def write_rational(self, data : aspose.cad.fileformats.tiff.TiffRational) -> None:
        '''Writes a single rational number value to the stream.
        
        :param data: The value to write.'''
        ...
    
    def write_s_rational(self, data : aspose.cad.fileformats.tiff.TiffSRational) -> None:
        '''Writes a single signed rational number value to the stream.
        
        :param data: The value to write.'''
        ...
    
    def write_rational_array(self, data : List[aspose.cad.fileformats.tiff.TiffRational]) -> None:
        '''Writes an array of unsigned rational values to the stream.
        
        :param data: The array to write.'''
        ...
    
    def write_s_rational_array(self, data : List[aspose.cad.fileformats.tiff.TiffSRational]) -> None:
        '''Writes an array of signed rational values to the stream.
        
        :param data: The array to write.'''
        ...
    
    def write_s_byte(self, data : sbyte) -> None:
        '''Writes a single signed byte value to the stream.
        
        :param data: The value to write.'''
        ...
    
    def write_s_byte_array(self, data : List[sbyte]) -> None:
        '''Writes an array of signed byte values to the stream.
        
        :param data: The array to write.'''
        ...
    
    def write_s_long_array(self, data : List[int]) -> None:
        '''Writes an array of integer values to the stream.
        
        :param data: The array to write.'''
        ...
    
    def write_s_short(self, data : int) -> None:
        '''Writes a single short value to the stream.
        
        :param data: The value to write.'''
        ...
    
    def write_s_short_array(self, data : List[int]) -> None:
        '''Writes an array of short values to the stream.
        
        :param data: The array to write.'''
        ...
    
    def write_slong(self, data : int) -> None:
        '''Writes a single integer value to the stream.
        
        :param data: The value to write.'''
        ...
    
    def write_u_byte(self, data : byte) -> None:
        '''Writes a single byte value to the stream.
        
        :param data: The value to write.'''
        ...
    
    def write_u_long(self, data : int) -> None:
        '''Writes a single unsigned integer value to the stream.
        
        :param data: The value to write.'''
        ...
    
    def write_u_long_array(self, data : List[int]) -> None:
        '''Writes an array of unsigned integer values to the stream.
        
        :param data: The array to write.'''
        ...
    
    def write_u_short(self, data : int) -> None:
        '''Writes a single unsigned short value to the stream.
        
        :param data: The value to write.'''
        ...
    
    def write_u_short_array(self, data : List[int]) -> None:
        '''Writes an array of unsigned short values to the stream.
        
        :param data: The array to write.'''
        ...
    
    @property
    def sync_root(self) -> any:
        ...
    
    @property
    def position(self) -> int:
        '''Gets the stream position.'''
        ...
    
    @position.setter
    def position(self, value : int):
        '''Sets the stream position.'''
        ...
    
    ...

