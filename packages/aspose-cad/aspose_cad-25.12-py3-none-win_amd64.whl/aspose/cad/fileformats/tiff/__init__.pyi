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

class TiffDataType:
    '''The tiff data type.'''
    
    @staticmethod
    def read_tag(data_stream : aspose.cad.fileformats.tiff.filemanagement.TiffStreamReader, position : int) -> aspose.cad.fileformats.tiff.TiffDataType:
        '''Reads the tag data.
        
        :param data_stream: The data stream.
        :param position: The tag position.
        :returns: The read tag.'''
        ...
    
    def compare_to(self, obj : any) -> int:
        '''Compares the current instance with another object of the same type and returns an integer that indicates whether the current instance precedes, follows, or occurs in the same position in the sort order as the other object.
        
        :param obj: An object to compare with this instance.
        :returns: A 32-bit signed integer that indicates the relative order of the objects being compared. The return value has these meanings:
        Value
        Meaning
        Less than zero
        This instance is less than ``obj``.
        Zero
        This instance is equal to ``obj``.
        Greater than zero
        This instance is greater than ``obj``.'''
        ...
    
    def get_aligned_data_size(self, size_of_tag_value : byte) -> int:
        '''Gets the data size aligned in 4-byte (int) or 8-byte (long) boundary.
        
        :param size_of_tag_value: Size of tag value.
        :returns: The aligned data size in bytes.'''
        ...
    
    def deep_clone(self) -> aspose.cad.fileformats.tiff.TiffDataType:
        '''Performs a deep clone of this instance.
        
        :returns: A deep clone of the current instance.'''
        ...
    
    def write_tag(self, data_stream : aspose.cad.fileformats.tiff.filemanagement.TiffStreamWriter, additional_data_offset : int) -> None:
        '''Writes the tag data.
        
        :param data_stream: The data stream.
        :param additional_data_offset: The offset to write additional data to.'''
        ...
    
    def write_additional_data(self, data_stream : aspose.cad.fileformats.tiff.filemanagement.TiffStreamWriter) -> int:
        '''Writes the additional tag data.
        
        :param data_stream: The data stream.
        :returns: The actual bytes written.'''
        ...
    
    @property
    def count(self) -> int:
        '''Gets the count of elements.'''
        ...
    
    @property
    def id(self) -> int:
        '''Gets tag id integer representation.'''
        ...
    
    @property
    def tag_id(self) -> aspose.cad.fileformats.tiff.enums.TiffTags:
        ...
    
    @property
    def tag_type(self) -> aspose.cad.fileformats.tiff.enums.TiffDataTypes:
        ...
    
    @property
    def aligned_data_size(self) -> int:
        ...
    
    @property
    def data_size(self) -> int:
        ...
    
    @property
    def value(self) -> any:
        '''Gets the value this data type contains.'''
        ...
    
    @value.setter
    def value(self, value : any):
        '''Sets the value this data type contains.'''
        ...
    
    @property
    def is_valid(self) -> bool:
        ...
    
    ...

class TiffExifIfd:
    '''The TIFF Exif image file directory class.'''
    
    @property
    def has_value(self) -> bool:
        ...
    
    @property
    def offset(self) -> int:
        '''Gets the pointer to EXIF IFD.'''
        ...
    
    @offset.setter
    def offset(self, value : int):
        '''Sets the pointer to EXIF IFD.'''
        ...
    
    ...

class TiffRational:
    '''The tiff rational type.'''
    
    @overload
    @staticmethod
    def approximate_fraction(value : float, epsilon : float) -> aspose.cad.fileformats.tiff.TiffRational:
        '''Approximates the provided value to a fraction.
        
        :param value: The value.
        :param epsilon: The error allowed.
        :returns: A rational number having error less than ``epsilon``.'''
        ...
    
    @overload
    @staticmethod
    def approximate_fraction(value : float) -> aspose.cad.fileformats.tiff.TiffRational:
        '''Approximates the provided value to a fraction.
        
        :param value: The value.
        :returns: A rational number having error less than :py:attr:`aspose.cad.fileformats.tiff.TiffRational.EPSILON`.'''
        ...
    
    @overload
    @staticmethod
    def approximate_fraction(value : float, epsilon : float) -> aspose.cad.fileformats.tiff.TiffRational:
        '''Approximates the provided value to a fraction.
        
        :param value: The value.
        :param epsilon: The error allowed.
        :returns: A rational number having error less than ``epsilon``.'''
        ...
    
    @overload
    @staticmethod
    def approximate_fraction(value : float) -> aspose.cad.fileformats.tiff.TiffRational:
        '''Approximates the provided value to a fraction.
        
        :param value: The value.
        :returns: A rational number having error less than :py:attr:`aspose.cad.fileformats.tiff.TiffRational.EPSILON`.'''
        ...
    
    @property
    def denominator(self) -> int:
        '''Gets the denominator.'''
        ...
    
    @property
    def nominator(self) -> int:
        '''Gets the nominator.'''
        ...
    
    @property
    def value(self) -> float:
        '''Gets the float value.'''
        ...
    
    @property
    def value_d(self) -> float:
        ...
    
    @classmethod
    @property
    def EPSILON(cls) -> float:
        '''The epsilon for fraction calculation'''
        ...
    
    ...

class TiffSRational:
    '''The tiff rational type.'''
    
    @overload
    @staticmethod
    def approximate_fraction(value : float, epsilon : float) -> aspose.cad.fileformats.tiff.TiffSRational:
        '''Approximates the provided value to a fraction.
        
        :param value: The value.
        :param epsilon: The error allowed.
        :returns: A rational number having error less than ``epsilon``.'''
        ...
    
    @overload
    @staticmethod
    def approximate_fraction(value : float) -> aspose.cad.fileformats.tiff.TiffSRational:
        '''Approximates the provided value to a fraction.
        
        :param value: The value.
        :returns: A rational number having error less than :py:attr:`aspose.cad.fileformats.tiff.TiffSRational.EPSILON`.'''
        ...
    
    @overload
    @staticmethod
    def approximate_fraction(value : float, epsilon : float) -> aspose.cad.fileformats.tiff.TiffSRational:
        '''Approximates the provided value to a fraction.
        
        :param value: The value.
        :param epsilon: The error allowed.
        :returns: A rational number having error less than ``epsilon``.'''
        ...
    
    @overload
    @staticmethod
    def approximate_fraction(value : float) -> aspose.cad.fileformats.tiff.TiffSRational:
        '''Approximates the provided value to a fraction.
        
        :param value: The value.
        :returns: A rational number having error less than :py:attr:`aspose.cad.fileformats.tiff.TiffSRational.EPSILON`.'''
        ...
    
    @property
    def denominator(self) -> int:
        '''Gets the denominator.'''
        ...
    
    @property
    def nominator(self) -> int:
        '''Gets the nominator.'''
        ...
    
    @property
    def value(self) -> float:
        '''Gets the float value.'''
        ...
    
    @property
    def value_d(self) -> float:
        ...
    
    @classmethod
    @property
    def EPSILON(cls) -> float:
        '''The epsilon for fraction calculation'''
        ...
    
    ...

