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

class CadField(aspose.cad.fileformats.cad.cadobjects.CadBaseObject):
    '''Class describing FIELD object.'''
    
    def get_uid(self) -> str:
        '''Identifier to use if object handle doesn't work. Done as method not to disturb FileComparer's property comparer'''
        ...
    
    def set_uid(self, id : str) -> None:
        '''Sets'''
        ...
    
    @property
    def embedded_objects_container(self) -> aspose.cad.fileformats.cad.cadobjects.CadEmbeddedObjectContainer:
        ...
    
    @embedded_objects_container.setter
    def embedded_objects_container(self, value : aspose.cad.fileformats.cad.cadobjects.CadEmbeddedObjectContainer):
        ...
    
    @property
    def object_handle(self) -> str:
        ...
    
    @object_handle.setter
    def object_handle(self, value : str):
        ...
    
    @property
    def xdata_container(self) -> aspose.cad.fileformats.cad.cadobjects.CadXdataContainer:
        ...
    
    @xdata_container.setter
    def xdata_container(self, value : aspose.cad.fileformats.cad.cadobjects.CadXdataContainer):
        ...
    
    @property
    def attributes(self) -> List[aspose.cad.fileformats.cad.cadobjects.CadObjectAttribute]:
        '''Gets the attributes.'''
        ...
    
    @attributes.setter
    def attributes(self, value : List[aspose.cad.fileformats.cad.cadobjects.CadObjectAttribute]):
        '''Sets the attributes.'''
        ...
    
    @property
    def application_codes_container(self) -> aspose.cad.fileformats.cad.cadobjects.CadApplicationCodesContainer:
        ...
    
    @application_codes_container.setter
    def application_codes_container(self, value : aspose.cad.fileformats.cad.cadobjects.CadApplicationCodesContainer):
        ...
    
    @property
    def attribute_102_values(self) -> List[aspose.cad.fileformats.cad.CadCodeValue]:
        ...
    
    @attribute_102_values.setter
    def attribute_102_values(self, value : List[aspose.cad.fileformats.cad.CadCodeValue]):
        ...
    
    @property
    def numreactors(self) -> int:
        '''The Numreactors'''
        ...
    
    @numreactors.setter
    def numreactors(self, value : int):
        '''The Numreactors'''
        ...
    
    @property
    def reactors(self) -> List[str]:
        '''Get the reactors handle'''
        ...
    
    @reactors.setter
    def reactors(self, value : List[str]):
        '''Get or sets the reactors handle'''
        ...
    
    @property
    def storage_flag(self) -> bool:
        ...
    
    @storage_flag.setter
    def storage_flag(self, value : bool):
        ...
    
    @property
    def hard_owner(self) -> str:
        ...
    
    @hard_owner.setter
    def hard_owner(self, value : str):
        ...
    
    @property
    def soft_owner(self) -> str:
        ...
    
    @soft_owner.setter
    def soft_owner(self, value : str):
        ...
    
    @property
    def is_soft_owner_set(self) -> bool:
        ...
    
    @property
    def type_name(self) -> aspose.cad.fileformats.cad.cadconsts.CadObjectTypeName:
        ...
    
    @property
    def child_objects(self) -> List[aspose.cad.fileformats.cad.cadobjects.CadObjectBase]:
        ...
    
    @child_objects.setter
    def child_objects(self, value : List[aspose.cad.fileformats.cad.cadobjects.CadObjectBase]):
        ...
    
    @property
    def attribute300(self) -> str:
        '''Gets the attribute 300.'''
        ...
    
    @attribute300.setter
    def attribute300(self, value : str):
        '''Sets the attribute 300.'''
        ...
    
    @property
    def attribute96(self) -> Optional[int]:
        '''Gets the attribute 96.'''
        ...
    
    @attribute96.setter
    def attribute96(self, value : Optional[int]):
        '''Sets the attribute 96.'''
        ...
    
    @property
    def attribute95(self) -> Optional[int]:
        '''Gets the attribute 95.'''
        ...
    
    @attribute95.setter
    def attribute95(self, value : Optional[int]):
        '''Sets the attribute 95.'''
        ...
    
    @property
    def attribute94(self) -> Optional[int]:
        '''Gets the attribute 94.'''
        ...
    
    @attribute94.setter
    def attribute94(self, value : Optional[int]):
        '''Sets the attribute 94.'''
        ...
    
    @property
    def attribute92(self) -> Optional[int]:
        '''Gets the attribute 92.'''
        ...
    
    @attribute92.setter
    def attribute92(self, value : Optional[int]):
        '''Sets the attribute 92.'''
        ...
    
    @property
    def attribute91(self) -> Optional[int]:
        '''Gets the attribute 91.'''
        ...
    
    @attribute91.setter
    def attribute91(self, value : Optional[int]):
        '''Sets the attribute 91.'''
        ...
    
    @property
    def cad_field_data(self) -> List[aspose.cad.fileformats.cad.cadobjects.field.CadFieldData]:
        ...
    
    @cad_field_data.setter
    def cad_field_data(self, value : List[aspose.cad.fileformats.cad.cadobjects.field.CadFieldData]):
        ...
    
    @property
    def format_string_length(self) -> int:
        ...
    
    @format_string_length.setter
    def format_string_length(self, value : int):
        ...
    
    @property
    def format_string_overflow(self) -> str:
        ...
    
    @format_string_overflow.setter
    def format_string_overflow(self, value : str):
        ...
    
    @property
    def format_string(self) -> str:
        ...
    
    @format_string.setter
    def format_string(self, value : str):
        ...
    
    @property
    def data_set_in_the_field(self) -> int:
        ...
    
    @data_set_in_the_field.setter
    def data_set_in_the_field(self, value : int):
        ...
    
    @property
    def object_ids(self) -> List[str]:
        ...
    
    @object_ids.setter
    def object_ids(self, value : List[str]):
        ...
    
    @property
    def object_i_ds_number(self) -> int:
        ...
    
    @object_i_ds_number.setter
    def object_i_ds_number(self, value : int):
        ...
    
    @property
    def child_field_ids(self) -> List[str]:
        ...
    
    @child_field_ids.setter
    def child_field_ids(self, value : List[str]):
        ...
    
    @property
    def evaluator_id(self) -> str:
        ...
    
    @evaluator_id.setter
    def evaluator_id(self, value : str):
        ...
    
    @property
    def field_code_string(self) -> str:
        ...
    
    @field_code_string.setter
    def field_code_string(self, value : str):
        ...
    
    @property
    def field_code_string_overflow(self) -> str:
        ...
    
    @field_code_string_overflow.setter
    def field_code_string_overflow(self, value : str):
        ...
    
    @property
    def child_fields_number(self) -> int:
        ...
    
    @child_fields_number.setter
    def child_fields_number(self, value : int):
        ...
    
    ...

class CadFieldData:
    '''The Field data'''
    
    @property
    def attribute001(self) -> str:
        '''Gets the attribute 1.'''
        ...
    
    @attribute001.setter
    def attribute001(self, value : str):
        '''Sets the attribute 1.'''
        ...
    
    @property
    def attribute300(self) -> str:
        '''Gets the attribute 300.'''
        ...
    
    @attribute300.setter
    def attribute300(self, value : str):
        '''Sets the attribute 300.'''
        ...
    
    @property
    def attribute302(self) -> str:
        '''Gets the attribute 302.'''
        ...
    
    @attribute302.setter
    def attribute302(self, value : str):
        '''Sets the attribute 302.'''
        ...
    
    @property
    def attribute304(self) -> str:
        '''Gets the attribute304.'''
        ...
    
    @attribute304.setter
    def attribute304(self, value : str):
        '''Sets the attribute304.'''
        ...
    
    @property
    def evaluated_cache_key_string(self) -> str:
        ...
    
    @evaluated_cache_key_string.setter
    def evaluated_cache_key_string(self, value : str):
        ...
    
    @property
    def binary_data(self) -> bytes:
        ...
    
    @binary_data.setter
    def binary_data(self, value : bytes):
        ...
    
    @property
    def binary_data_buffer_size(self) -> Optional[int]:
        ...
    
    @binary_data_buffer_size.setter
    def binary_data_buffer_size(self, value : Optional[int]):
        ...
    
    @property
    def value_id(self) -> str:
        ...
    
    @value_id.setter
    def value_id(self, value : str):
        ...
    
    @property
    def double_value(self) -> Optional[float]:
        ...
    
    @double_value.setter
    def double_value(self, value : Optional[float]):
        ...
    
    @property
    def long_value(self) -> Optional[int]:
        ...
    
    @long_value.setter
    def long_value(self, value : Optional[int]):
        ...
    
    @property
    def field_value_data_type(self) -> int:
        ...
    
    @field_value_data_type.setter
    def field_value_data_type(self, value : int):
        ...
    
    @property
    def attribute93(self) -> Optional[int]:
        '''Gets the attribute 93.'''
        ...
    
    @attribute93.setter
    def attribute93(self, value : Optional[int]):
        '''Sets the attribute 93.'''
        ...
    
    @property
    def attribute94(self) -> Optional[int]:
        '''Gets the attribute94.'''
        ...
    
    @attribute94.setter
    def attribute94(self, value : Optional[int]):
        '''Sets the attribute94.'''
        ...
    
    @property
    def field_data_key_string(self) -> str:
        ...
    
    @field_data_key_string.setter
    def field_data_key_string(self, value : str):
        ...
    
    ...

