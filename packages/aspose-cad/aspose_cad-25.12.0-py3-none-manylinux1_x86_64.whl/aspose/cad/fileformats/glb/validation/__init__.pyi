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

class DataException(ModelException):
    '''Represents an exception produced by invalid data.'''
    
    ...

class LinkException(ModelException):
    '''Represents an exception produced by invalid objects relationships.'''
    
    ...

class ModelException:
    '''Represents an exception produced by the serialization or validation of a gltf model.'''
    
    ...

class SchemaException(ModelException):
    '''Represents an exception produced by an invalid JSON document.'''
    
    ...

class SemanticException(ModelException):
    '''Represents an esception produced by invalid values.'''
    
    ...

class ValidationContext:
    '''Utility class used in the process of model validation.'''
    
    def get_context(self, target : aspose.cad.fileformats.glb.io.JsonSerializable) -> aspose.cad.fileformats.glb.validation.ValidationContext:
        ...
    
    def is_true(self, parameter_name : aspose.cad.fileformats.glb.validation.ValueLocation, value : bool, msg : str, severity : aspose.cad.fileformats.glb.validation.ExceptionSeverity) -> aspose.cad.fileformats.glb.validation.ValidationContext:
        ...
    
    def not_null(self, parameter_name : aspose.cad.fileformats.glb.validation.ValueLocation, target : any) -> aspose.cad.fileformats.glb.validation.ValidationContext:
        ...
    
    def must_be_null(self, parameter_name : aspose.cad.fileformats.glb.validation.ValueLocation, target : any) -> aspose.cad.fileformats.glb.validation.ValidationContext:
        ...
    
    def is_multiple_of(self, parameter_name : aspose.cad.fileformats.glb.validation.ValueLocation, value : int, multiple : int) -> aspose.cad.fileformats.glb.validation.ValidationContext:
        ...
    
    def non_negative(self, parameter_name : aspose.cad.fileformats.glb.validation.ValueLocation, value : Optional[int]) -> aspose.cad.fileformats.glb.validation.ValidationContext:
        ...
    
    def is_null_or_valid_uri(self, parameter_name : aspose.cad.fileformats.glb.validation.ValueLocation, gltf_uri : str, valid_headers : List[str]) -> aspose.cad.fileformats.glb.validation.ValidationContext:
        ...
    
    def is_valid_uri(self, parameter_name : aspose.cad.fileformats.glb.validation.ValueLocation, gltf_uri : str, valid_headers : List[str]) -> aspose.cad.fileformats.glb.validation.ValidationContext:
        ...
    
    def is_json_serializable(self, parameter_name : aspose.cad.fileformats.glb.validation.ValueLocation, value : any) -> aspose.cad.fileformats.glb.validation.ValidationContext:
        ...
    
    def is_any_of(self, parameter_name : aspose.cad.fileformats.glb.validation.ValueLocation, value : aspose.cad.fileformats.glb.memory.AttributeFormat, values : List[aspose.cad.fileformats.glb.memory.AttributeFormat]) -> aspose.cad.fileformats.glb.validation.ValidationContext:
        ...
    
    @property
    def root(self) -> aspose.cad.fileformats.glb.GlbData:
        ...
    
    @property
    def try_fix(self) -> bool:
        ...
    
    ...

class ValidationResult:
    
    def set_schema_error(self, model : aspose.cad.fileformats.glb.GlbData, error : str) -> None:
        ...
    
    def set_error(self, ex : aspose.cad.fileformats.glb.validation.ModelException) -> None:
        ...
    
    @property
    def root(self) -> aspose.cad.fileformats.glb.GlbData:
        ...
    
    @property
    def mode(self) -> aspose.cad.fileformats.glb.validation.ValidationMode:
        ...
    
    @property
    def has_errors(self) -> bool:
        ...
    
    ...

class ValueLocation:
    
    ...

class ExceptionSeverity:
    '''Represents an exception severity.'''
    
    @classmethod
    @property
    def ERROR(cls) -> ExceptionSeverity:
        ...
    
    @classmethod
    @property
    def WARNING(cls) -> ExceptionSeverity:
        ...
    
    @classmethod
    @property
    def INFO(cls) -> ExceptionSeverity:
        ...
    
    @classmethod
    @property
    def HINT(cls) -> ExceptionSeverity:
        ...
    
    ...

class ValidationMode:
    '''Defines validation modes for reading files.'''
    
    @classmethod
    @property
    def SKIP(cls) -> ValidationMode:
        '''Skips validation completely.'''
        ...
    
    @classmethod
    @property
    def TRY_FIX(cls) -> ValidationMode:
        '''In some specific cases, the file can be fixed, at which point the errors successfully
        fixed will be reported as warnings.'''
        ...
    
    @classmethod
    @property
    def STRICT(cls) -> ValidationMode:
        '''Full validation, any error throws an exception.'''
        ...
    
    ...

