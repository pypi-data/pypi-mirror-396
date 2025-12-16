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

class AssocActionDependency:
    '''Class describing dependencies between Assoc actions'''
    
    @property
    def is_owned(self) -> bool:
        ...
    
    @is_owned.setter
    def is_owned(self, value : bool):
        ...
    
    @property
    def dependency(self) -> str:
        '''Gets dependency handle value.'''
        ...
    
    @dependency.setter
    def dependency(self, value : str):
        '''Sets dependency handle value.'''
        ...
    
    ...

class AssocEvaluatedVariant:
    '''Сlass describing variant values for Assoc objects'''
    
    @property
    def dxf_code(self) -> aspose.cad.fileformats.cad.CadEntityAttribute:
        ...
    
    @dxf_code.setter
    def dxf_code(self, value : aspose.cad.fileformats.cad.CadEntityAttribute):
        ...
    
    @property
    def bit_double_value(self) -> float:
        ...
    
    @bit_double_value.setter
    def bit_double_value(self, value : float):
        ...
    
    @property
    def bit_long_value(self) -> int:
        ...
    
    @bit_long_value.setter
    def bit_long_value(self, value : int):
        ...
    
    @property
    def text_value(self) -> str:
        ...
    
    @text_value.setter
    def text_value(self, value : str):
        ...
    
    ...

class CadAcDbAssoc2dConstraintGroup(CadAcDbAssocAction):
    '''Class describing Assoc 2D Constraint Group.'''
    
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
    def class_version(self) -> int:
        ...
    
    @class_version.setter
    def class_version(self, value : int):
        ...
    
    @property
    def geometry_status(self) -> int:
        ...
    
    @geometry_status.setter
    def geometry_status(self, value : int):
        ...
    
    @property
    def owning_network(self) -> str:
        ...
    
    @owning_network.setter
    def owning_network(self, value : str):
        ...
    
    @property
    def action_body(self) -> str:
        ...
    
    @action_body.setter
    def action_body(self, value : str):
        ...
    
    @property
    def action_index(self) -> int:
        ...
    
    @action_index.setter
    def action_index(self, value : int):
        ...
    
    @property
    def max_assoc_dependency_index(self) -> int:
        ...
    
    @max_assoc_dependency_index.setter
    def max_assoc_dependency_index(self, value : int):
        ...
    
    @property
    def dependencies(self) -> List[aspose.cad.fileformats.cad.cadobjects.assoc.AssocActionDependency]:
        '''Gets dependencies.'''
        ...
    
    @dependencies.setter
    def dependencies(self, value : List[aspose.cad.fileformats.cad.cadobjects.assoc.AssocActionDependency]):
        '''Sets dependencies.'''
        ...
    
    @property
    def owned_params(self) -> List[str]:
        ...
    
    @owned_params.setter
    def owned_params(self, value : List[str]):
        ...
    
    @property
    def constraint_group_version(self) -> int:
        ...
    
    @constraint_group_version.setter
    def constraint_group_version(self, value : int):
        ...
    
    @property
    def workplanes(self) -> List[aspose.cad.fileformats.cad.cadobjects.Cad3DPoint]:
        '''Gets workplanes.'''
        ...
    
    @workplanes.setter
    def workplanes(self, value : List[aspose.cad.fileformats.cad.cadobjects.Cad3DPoint]):
        '''Sets workplanes.'''
        ...
    
    @property
    def constraint_group_actions(self) -> List[str]:
        ...
    
    @constraint_group_actions.setter
    def constraint_group_actions(self, value : List[str]):
        ...
    
    ...

class CadAcDbAssocAction(aspose.cad.fileformats.cad.cadobjects.CadBaseObject):
    '''Class describing Assoc Action'''
    
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
    def class_version(self) -> int:
        ...
    
    @class_version.setter
    def class_version(self, value : int):
        ...
    
    @property
    def geometry_status(self) -> int:
        ...
    
    @geometry_status.setter
    def geometry_status(self, value : int):
        ...
    
    @property
    def owning_network(self) -> str:
        ...
    
    @owning_network.setter
    def owning_network(self, value : str):
        ...
    
    @property
    def action_body(self) -> str:
        ...
    
    @action_body.setter
    def action_body(self, value : str):
        ...
    
    @property
    def action_index(self) -> int:
        ...
    
    @action_index.setter
    def action_index(self, value : int):
        ...
    
    @property
    def max_assoc_dependency_index(self) -> int:
        ...
    
    @max_assoc_dependency_index.setter
    def max_assoc_dependency_index(self, value : int):
        ...
    
    @property
    def dependencies(self) -> List[aspose.cad.fileformats.cad.cadobjects.assoc.AssocActionDependency]:
        '''Gets dependencies.'''
        ...
    
    @dependencies.setter
    def dependencies(self, value : List[aspose.cad.fileformats.cad.cadobjects.assoc.AssocActionDependency]):
        '''Sets dependencies.'''
        ...
    
    @property
    def owned_params(self) -> List[str]:
        ...
    
    @owned_params.setter
    def owned_params(self, value : List[str]):
        ...
    
    ...

class CadAcDbAssocDependency(aspose.cad.fileformats.cad.cadobjects.CadBaseObject):
    '''Class describing Assoc Dependency.'''
    
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
    def status(self) -> aspose.cad.fileformats.cad.cadobjects.assoc.AssocStatus:
        '''Gets the current AssocStatus of this dependency.'''
        ...
    
    @status.setter
    def status(self, value : aspose.cad.fileformats.cad.cadobjects.assoc.AssocStatus):
        '''Sets the current AssocStatus of this dependency.'''
        ...
    
    @property
    def order(self) -> int:
        '''Gets and sets the order of the dependency.'''
        ...
    
    @order.setter
    def order(self, value : int):
        '''Gets and sets the order of the dependency.'''
        ...
    
    @property
    def name(self) -> str:
        '''Gets the dependency name.'''
        ...
    
    @name.setter
    def name(self, value : str):
        '''Sets the dependency name.'''
        ...
    
    @property
    def dependency_body_id(self) -> int:
        ...
    
    @dependency_body_id.setter
    def dependency_body_id(self, value : int):
        ...
    
    @property
    def dependent_on_object(self) -> str:
        ...
    
    @dependent_on_object.setter
    def dependent_on_object(self, value : str):
        ...
    
    @property
    def prev_dependency_on_object(self) -> str:
        ...
    
    @prev_dependency_on_object.setter
    def prev_dependency_on_object(self, value : str):
        ...
    
    @property
    def next_dependency_on_object(self) -> str:
        ...
    
    @next_dependency_on_object.setter
    def next_dependency_on_object(self, value : str):
        ...
    
    @property
    def dependency_body(self) -> str:
        ...
    
    @dependency_body.setter
    def dependency_body(self, value : str):
        ...
    
    ...

class CadAcDbAssocGeomDependency(CadAcDbAssocDependency):
    '''Class describing Assoc Geom Dependency.'''
    
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
    def status(self) -> aspose.cad.fileformats.cad.cadobjects.assoc.AssocStatus:
        '''Gets the current AssocStatus of this dependency.'''
        ...
    
    @status.setter
    def status(self, value : aspose.cad.fileformats.cad.cadobjects.assoc.AssocStatus):
        '''Sets the current AssocStatus of this dependency.'''
        ...
    
    @property
    def order(self) -> int:
        '''Gets and sets the order of the dependency.'''
        ...
    
    @order.setter
    def order(self, value : int):
        '''Gets and sets the order of the dependency.'''
        ...
    
    @property
    def name(self) -> str:
        '''Gets the dependency name.'''
        ...
    
    @name.setter
    def name(self, value : str):
        '''Sets the dependency name.'''
        ...
    
    @property
    def dependency_body_id(self) -> int:
        ...
    
    @dependency_body_id.setter
    def dependency_body_id(self, value : int):
        ...
    
    @property
    def dependent_on_object(self) -> str:
        ...
    
    @dependent_on_object.setter
    def dependent_on_object(self, value : str):
        ...
    
    @property
    def prev_dependency_on_object(self) -> str:
        ...
    
    @prev_dependency_on_object.setter
    def prev_dependency_on_object(self, value : str):
        ...
    
    @property
    def next_dependency_on_object(self) -> str:
        ...
    
    @next_dependency_on_object.setter
    def next_dependency_on_object(self, value : str):
        ...
    
    @property
    def dependency_body(self) -> str:
        ...
    
    @dependency_body.setter
    def dependency_body(self, value : str):
        ...
    
    @property
    def geom_dependency_class_version(self) -> int:
        ...
    
    @geom_dependency_class_version.setter
    def geom_dependency_class_version(self, value : int):
        ...
    
    @property
    def is_enabled(self) -> bool:
        ...
    
    @is_enabled.setter
    def is_enabled(self, value : bool):
        ...
    
    @property
    def index1(self) -> int:
        '''Gets and sets the unknown index.'''
        ...
    
    @index1.setter
    def index1(self, value : int):
        '''Gets and sets the unknown index.'''
        ...
    
    @property
    def index2(self) -> int:
        '''Gets and sets the unknown index.'''
        ...
    
    @index2.setter
    def index2(self, value : int):
        '''Gets and sets the unknown index.'''
        ...
    
    @property
    def is_dependent_on_compound_object(self) -> bool:
        ...
    
    @is_dependent_on_compound_object.setter
    def is_dependent_on_compound_object(self, value : bool):
        ...
    
    ...

class CadAcDbAssocNetwork(CadAcDbAssocAction):
    '''Class describing Assoc Network.'''
    
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
    def class_version(self) -> int:
        ...
    
    @class_version.setter
    def class_version(self, value : int):
        ...
    
    @property
    def geometry_status(self) -> int:
        ...
    
    @geometry_status.setter
    def geometry_status(self, value : int):
        ...
    
    @property
    def owning_network(self) -> str:
        ...
    
    @owning_network.setter
    def owning_network(self, value : str):
        ...
    
    @property
    def action_body(self) -> str:
        ...
    
    @action_body.setter
    def action_body(self, value : str):
        ...
    
    @property
    def action_index(self) -> int:
        ...
    
    @action_index.setter
    def action_index(self, value : int):
        ...
    
    @property
    def max_assoc_dependency_index(self) -> int:
        ...
    
    @max_assoc_dependency_index.setter
    def max_assoc_dependency_index(self, value : int):
        ...
    
    @property
    def dependencies(self) -> List[aspose.cad.fileformats.cad.cadobjects.assoc.AssocActionDependency]:
        '''Gets dependencies.'''
        ...
    
    @dependencies.setter
    def dependencies(self, value : List[aspose.cad.fileformats.cad.cadobjects.assoc.AssocActionDependency]):
        '''Sets dependencies.'''
        ...
    
    @property
    def owned_params(self) -> List[str]:
        ...
    
    @owned_params.setter
    def owned_params(self, value : List[str]):
        ...
    
    @property
    def accos_network_list(self) -> List[aspose.cad.fileformats.cad.cadparameters.CadParameter]:
        ...
    
    @accos_network_list.setter
    def accos_network_list(self, value : List[aspose.cad.fileformats.cad.cadparameters.CadParameter]):
        ...
    
    @property
    def accos_actions_list(self) -> List[aspose.cad.fileformats.cad.cadparameters.CadParameter]:
        ...
    
    @accos_actions_list.setter
    def accos_actions_list(self, value : List[aspose.cad.fileformats.cad.cadparameters.CadParameter]):
        ...
    
    @property
    def network_version(self) -> int:
        ...
    
    @network_version.setter
    def network_version(self, value : int):
        ...
    
    @property
    def network_action_index(self) -> int:
        ...
    
    @network_action_index.setter
    def network_action_index(self, value : int):
        ...
    
    @property
    def network_actions(self) -> List[aspose.cad.fileformats.cad.cadobjects.assoc.AssocActionDependency]:
        ...
    
    @network_actions.setter
    def network_actions(self, value : List[aspose.cad.fileformats.cad.cadobjects.assoc.AssocActionDependency]):
        ...
    
    @property
    def owned_network_actions(self) -> List[str]:
        ...
    
    @owned_network_actions.setter
    def owned_network_actions(self, value : List[str]):
        ...
    
    ...

class CadAcDbAssocValueDependency(CadAcDbAssocDependency):
    '''Class describing Assoc Value Dependency.'''
    
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
    def status(self) -> aspose.cad.fileformats.cad.cadobjects.assoc.AssocStatus:
        '''Gets the current AssocStatus of this dependency.'''
        ...
    
    @status.setter
    def status(self, value : aspose.cad.fileformats.cad.cadobjects.assoc.AssocStatus):
        '''Sets the current AssocStatus of this dependency.'''
        ...
    
    @property
    def order(self) -> int:
        '''Gets and sets the order of the dependency.'''
        ...
    
    @order.setter
    def order(self, value : int):
        '''Gets and sets the order of the dependency.'''
        ...
    
    @property
    def name(self) -> str:
        '''Gets the dependency name.'''
        ...
    
    @name.setter
    def name(self, value : str):
        '''Sets the dependency name.'''
        ...
    
    @property
    def dependency_body_id(self) -> int:
        ...
    
    @dependency_body_id.setter
    def dependency_body_id(self, value : int):
        ...
    
    @property
    def dependent_on_object(self) -> str:
        ...
    
    @dependent_on_object.setter
    def dependent_on_object(self, value : str):
        ...
    
    @property
    def prev_dependency_on_object(self) -> str:
        ...
    
    @prev_dependency_on_object.setter
    def prev_dependency_on_object(self, value : str):
        ...
    
    @property
    def next_dependency_on_object(self) -> str:
        ...
    
    @next_dependency_on_object.setter
    def next_dependency_on_object(self, value : str):
        ...
    
    @property
    def dependency_body(self) -> str:
        ...
    
    @dependency_body.setter
    def dependency_body(self, value : str):
        ...
    
    @property
    def value_name(self) -> str:
        ...
    
    @value_name.setter
    def value_name(self, value : str):
        ...
    
    @property
    def dependent_on_object_value(self) -> aspose.cad.fileformats.cad.cadobjects.assoc.AssocEvaluatedVariant:
        ...
    
    @dependent_on_object_value.setter
    def dependent_on_object_value(self, value : aspose.cad.fileformats.cad.cadobjects.assoc.AssocEvaluatedVariant):
        ...
    
    ...

class CadAcDbAssocVariable(CadAcDbAssocAction):
    '''Class describing Ac Db Assoc Variable.'''
    
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
    def class_version(self) -> int:
        ...
    
    @class_version.setter
    def class_version(self, value : int):
        ...
    
    @property
    def geometry_status(self) -> int:
        ...
    
    @geometry_status.setter
    def geometry_status(self, value : int):
        ...
    
    @property
    def owning_network(self) -> str:
        ...
    
    @owning_network.setter
    def owning_network(self, value : str):
        ...
    
    @property
    def action_body(self) -> str:
        ...
    
    @action_body.setter
    def action_body(self, value : str):
        ...
    
    @property
    def action_index(self) -> int:
        ...
    
    @action_index.setter
    def action_index(self, value : int):
        ...
    
    @property
    def max_assoc_dependency_index(self) -> int:
        ...
    
    @max_assoc_dependency_index.setter
    def max_assoc_dependency_index(self, value : int):
        ...
    
    @property
    def dependencies(self) -> List[aspose.cad.fileformats.cad.cadobjects.assoc.AssocActionDependency]:
        '''Gets dependencies.'''
        ...
    
    @dependencies.setter
    def dependencies(self, value : List[aspose.cad.fileformats.cad.cadobjects.assoc.AssocActionDependency]):
        '''Sets dependencies.'''
        ...
    
    @property
    def owned_params(self) -> List[str]:
        ...
    
    @owned_params.setter
    def owned_params(self, value : List[str]):
        ...
    
    @property
    def variable_class_version(self) -> int:
        ...
    
    @variable_class_version.setter
    def variable_class_version(self, value : int):
        ...
    
    @property
    def variable_name(self) -> str:
        ...
    
    @variable_name.setter
    def variable_name(self, value : str):
        ...
    
    @property
    def variable_value(self) -> str:
        ...
    
    @variable_value.setter
    def variable_value(self, value : str):
        ...
    
    @property
    def expression(self) -> str:
        '''Gets the evaluatorId.'''
        ...
    
    @expression.setter
    def expression(self, value : str):
        '''Sets the evaluatorId.'''
        ...
    
    @property
    def evaluator_id(self) -> str:
        ...
    
    @evaluator_id.setter
    def evaluator_id(self, value : str):
        ...
    
    @property
    def description(self) -> str:
        '''Gets the description.'''
        ...
    
    @description.setter
    def description(self, value : str):
        '''Sets the description.'''
        ...
    
    @property
    def dependent_on_object_value(self) -> aspose.cad.fileformats.cad.cadobjects.assoc.AssocEvaluatedVariant:
        ...
    
    @dependent_on_object_value.setter
    def dependent_on_object_value(self, value : aspose.cad.fileformats.cad.cadobjects.assoc.AssocEvaluatedVariant):
        ...
    
    ...

class AssocStatus:
    '''The status of AssocActions and AssocDependencies'''
    
    @classmethod
    @property
    def IS_UP_TO_DATE_ASSOC_STATUS(cls) -> AssocStatus:
        '''Everything is in sync'''
        ...
    
    @classmethod
    @property
    def CHANGED_DIRECTLY_ASSOC_STATUS(cls) -> AssocStatus:
        '''Explicitly changed (such as by the user).'''
        ...
    
    @classmethod
    @property
    def CHANGED_TRANSITIVELY_ASSOC_STATUS(cls) -> AssocStatus:
        '''Changed indirectly due to something else changed.'''
        ...
    
    @classmethod
    @property
    def CHANGED_NO_DIFFERENCE_ASSOC_STATUS(cls) -> AssocStatus:
        '''No real change, only forces to evaluate.'''
        ...
    
    @classmethod
    @property
    def FAILED_TO_EVALUATE_ASSOC_STATUS(cls) -> AssocStatus:
        '''Unable to evaluate AssocStatus'''
        ...
    
    @classmethod
    @property
    def ERASED_ASSOC_STATUS(cls) -> AssocStatus:
        '''Dependent-on object erased or action is to be erased.'''
        ...
    
    @classmethod
    @property
    def SUPPRESSED_ASSOC_STATUS(cls) -> AssocStatus:
        '''Action evaluation suppressed, treated as if evaluated.'''
        ...
    
    ...

