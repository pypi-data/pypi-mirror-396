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

class CadAttDef(CadXrecordObject):
    '''Class describing Cad AttributeDefinitions'''
    
    def get_uid(self) -> str:
        '''Identifier to use if object handle doesn't work. Done as method not to disturb FileComparer's property comparer'''
        ...
    
    def set_uid(self, id : str) -> None:
        '''Sets'''
        ...
    
    def clone(self) -> any:
        '''Clones current object
        
        :returns: Clone of current object'''
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
    def id(self) -> str:
        '''Gets the id.'''
        ...
    
    @id.setter
    def id(self, value : str):
        '''Sets the id.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        ...
    
    @property
    def type_name(self) -> aspose.cad.fileformats.cad.cadconsts.CadEntityTypeName:
        ...
    
    @property
    def child_objects(self) -> List[aspose.cad.fileformats.cad.cadobjects.CadEntityBase]:
        ...
    
    @child_objects.setter
    def child_objects(self, value : List[aspose.cad.fileformats.cad.cadobjects.CadEntityBase]):
        ...
    
    @property
    def color_id(self) -> int:
        ...
    
    @color_id.setter
    def color_id(self, value : int):
        ...
    
    @property
    def layout_tab_name(self) -> str:
        ...
    
    @layout_tab_name.setter
    def layout_tab_name(self, value : str):
        ...
    
    @property
    def color_name(self) -> str:
        ...
    
    @color_name.setter
    def color_name(self, value : str):
        ...
    
    @property
    def color_value(self) -> Optional[int]:
        ...
    
    @color_value.setter
    def color_value(self, value : Optional[int]):
        ...
    
    @property
    def layer_name(self) -> str:
        ...
    
    @layer_name.setter
    def layer_name(self, value : str):
        ...
    
    @property
    def line_scale(self) -> float:
        ...
    
    @line_scale.setter
    def line_scale(self, value : float):
        ...
    
    @property
    def line_type_name(self) -> str:
        ...
    
    @line_type_name.setter
    def line_type_name(self, value : str):
        ...
    
    @property
    def line_weight(self) -> int:
        ...
    
    @line_weight.setter
    def line_weight(self, value : int):
        ...
    
    @property
    def material(self) -> str:
        '''Gets the material.'''
        ...
    
    @material.setter
    def material(self, value : str):
        '''Sets the material.'''
        ...
    
    @property
    def color_handle(self) -> str:
        ...
    
    @color_handle.setter
    def color_handle(self, value : str):
        ...
    
    @property
    def plot_style(self) -> str:
        ...
    
    @plot_style.setter
    def plot_style(self, value : str):
        ...
    
    @property
    def proxy_bytes_count(self) -> Optional[int]:
        ...
    
    @proxy_bytes_count.setter
    def proxy_bytes_count(self, value : Optional[int]):
        ...
    
    @property
    def proxy_data(self) -> bytes:
        ...
    
    @proxy_data.setter
    def proxy_data(self, value : bytes):
        ...
    
    @property
    def shadow_mode(self) -> Optional[aspose.cad.fileformats.cad.cadconsts.CadShadowMode]:
        ...
    
    @shadow_mode.setter
    def shadow_mode(self, value : Optional[aspose.cad.fileformats.cad.cadconsts.CadShadowMode]):
        ...
    
    @property
    def space_mode(self) -> aspose.cad.fileformats.cad.cadconsts.CadEntitySpaceMode:
        ...
    
    @space_mode.setter
    def space_mode(self, value : aspose.cad.fileformats.cad.cadconsts.CadEntitySpaceMode):
        ...
    
    @property
    def bounds(self) -> List[aspose.cad.fileformats.cad.cadobjects.Cad3DPoint]:
        '''Minimal and maximal points of entity. Filled after GetBounds is called for CadImage.'''
        ...
    
    @bounds.setter
    def bounds(self, value : List[aspose.cad.fileformats.cad.cadobjects.Cad3DPoint]):
        '''Minimal and maximal points of entity. Filled after GetBounds is called for CadImage.'''
        ...
    
    @property
    def transparency(self) -> Optional[int]:
        '''Gets the transparency value for the entity.'''
        ...
    
    @transparency.setter
    def transparency(self, value : Optional[int]):
        '''Sets the transparency value for the entity.'''
        ...
    
    @property
    def visible(self) -> int:
        '''Gets a value indicating whether this :py:class:`aspose.cad.fileformats.cad.cadobjects.CadEntityBase` is visible.'''
        ...
    
    @visible.setter
    def visible(self, value : int):
        '''Sets a value indicating whether this :py:class:`aspose.cad.fileformats.cad.cadobjects.CadEntityBase` is visible.'''
        ...
    
    @property
    def hyperlink(self) -> str:
        '''Gets a hyperlink to an entity and displays the hyperlink name or description (if one is specified).'''
        ...
    
    @hyperlink.setter
    def hyperlink(self, value : str):
        '''Sets a hyperlink to an entity and displays the hyperlink name or description (if one is specified).'''
        ...
    
    @property
    def entmode(self) -> byte:
        '''Gets the entity mode'''
        ...
    
    @entmode.setter
    def entmode(self, value : byte):
        '''Sets the entity mode'''
        ...
    
    @property
    def x_dir_missing_flag(self) -> bool:
        ...
    
    @x_dir_missing_flag.setter
    def x_dir_missing_flag(self, value : bool):
        ...
    
    @property
    def is_by_layer(self) -> bool:
        ...
    
    @is_by_layer.setter
    def is_by_layer(self, value : bool):
        ...
    
    @property
    def is_no_links(self) -> bool:
        ...
    
    @is_no_links.setter
    def is_no_links(self, value : bool):
        ...
    
    @property
    def l_type(self) -> byte:
        ...
    
    @l_type.setter
    def l_type(self, value : byte):
        ...
    
    @property
    def plot_style_flag(self) -> byte:
        ...
    
    @plot_style_flag.setter
    def plot_style_flag(self, value : byte):
        ...
    
    @property
    def assoc_view_port_handle(self) -> str:
        ...
    
    @property
    def is_assoc_view_port_handle_set(self) -> bool:
        ...
    
    @property
    def area(self) -> float:
        '''Gets the area of the entity.'''
        ...
    
    @property
    def length(self) -> float:
        '''Gets the length of the entity.'''
        ...
    
    @property
    def group_handle(self) -> str:
        ...
    
    @group_handle.setter
    def group_handle(self, value : str):
        ...
    
    @property
    def extrusion_direction(self) -> aspose.cad.fileformats.cad.cadobjects.Cad3DPoint:
        ...
    
    @extrusion_direction.setter
    def extrusion_direction(self, value : aspose.cad.fileformats.cad.cadobjects.Cad3DPoint):
        ...
    
    @property
    def duplicate_record_cloning_flag(self) -> Optional[int]:
        ...
    
    @duplicate_record_cloning_flag.setter
    def duplicate_record_cloning_flag(self, value : Optional[int]):
        ...
    
    @property
    def m_text_flag(self) -> Optional[int]:
        ...
    
    @m_text_flag.setter
    def m_text_flag(self, value : Optional[int]):
        ...
    
    @property
    def is_really_locked_flag(self) -> Optional[int]:
        ...
    
    @is_really_locked_flag.setter
    def is_really_locked_flag(self, value : Optional[int]):
        ...
    
    @property
    def secondary_attributes_or_attribute_definitions_number(self) -> Optional[int]:
        ...
    
    @secondary_attributes_or_attribute_definitions_number.setter
    def secondary_attributes_or_attribute_definitions_number(self, value : Optional[int]):
        ...
    
    @property
    def hard_pointer_ids(self) -> List[str]:
        ...
    
    @hard_pointer_ids.setter
    def hard_pointer_ids(self, value : List[str]):
        ...
    
    @property
    def current_annotation_scale(self) -> Optional[float]:
        ...
    
    @current_annotation_scale.setter
    def current_annotation_scale(self, value : Optional[float]):
        ...
    
    @property
    def definition_tag_string(self) -> str:
        ...
    
    @definition_tag_string.setter
    def definition_tag_string(self, value : str):
        ...
    
    @property
    def multi_text(self) -> aspose.cad.fileformats.cad.cadobjects.CadMText:
        ...
    
    @multi_text.setter
    def multi_text(self, value : aspose.cad.fileformats.cad.cadobjects.CadMText):
        ...
    
    @property
    def version_number(self) -> Optional[int]:
        ...
    
    @version_number.setter
    def version_number(self, value : Optional[int]):
        ...
    
    @property
    def lock_position_flag(self) -> int:
        ...
    
    @lock_position_flag.setter
    def lock_position_flag(self, value : int):
        ...
    
    @property
    def default_string(self) -> str:
        ...
    
    @default_string.setter
    def default_string(self, value : str):
        ...
    
    @property
    def field_length(self) -> int:
        ...
    
    @field_length.setter
    def field_length(self, value : int):
        ...
    
    @property
    def first_alignment(self) -> aspose.cad.fileformats.cad.cadobjects.Cad3DPoint:
        ...
    
    @first_alignment.setter
    def first_alignment(self, value : aspose.cad.fileformats.cad.cadobjects.Cad3DPoint):
        ...
    
    @property
    def flags(self) -> int:
        '''Gets the flags.'''
        ...
    
    @flags.setter
    def flags(self, value : int):
        '''Sets the flags.'''
        ...
    
    @property
    def generation_flag(self) -> int:
        ...
    
    @generation_flag.setter
    def generation_flag(self, value : int):
        ...
    
    @property
    def horizontal_alignment(self) -> int:
        ...
    
    @horizontal_alignment.setter
    def horizontal_alignment(self, value : int):
        ...
    
    @property
    def oblique_angle(self) -> float:
        ...
    
    @oblique_angle.setter
    def oblique_angle(self, value : float):
        ...
    
    @property
    def prompt_string(self) -> str:
        ...
    
    @prompt_string.setter
    def prompt_string(self, value : str):
        ...
    
    @property
    def rotation_angle(self) -> float:
        ...
    
    @rotation_angle.setter
    def rotation_angle(self, value : float):
        ...
    
    @property
    def scale_x(self) -> float:
        ...
    
    @scale_x.setter
    def scale_x(self, value : float):
        ...
    
    @property
    def second_alignment(self) -> aspose.cad.fileformats.cad.cadobjects.Cad3DPoint:
        ...
    
    @second_alignment.setter
    def second_alignment(self, value : aspose.cad.fileformats.cad.cadobjects.Cad3DPoint):
        ...
    
    @property
    def style_name(self) -> str:
        ...
    
    @style_name.setter
    def style_name(self, value : str):
        ...
    
    @property
    def text_height(self) -> float:
        ...
    
    @text_height.setter
    def text_height(self, value : float):
        ...
    
    @property
    def thickness(self) -> float:
        '''Gets the thickness.'''
        ...
    
    @thickness.setter
    def thickness(self, value : float):
        '''Sets the thickness.'''
        ...
    
    @property
    def vertical_justification(self) -> int:
        ...
    
    @vertical_justification.setter
    def vertical_justification(self, value : int):
        ...
    
    ...

class CadAttrib(CadXrecordObject):
    '''The Cad attrib.'''
    
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
    def id(self) -> str:
        '''Gets the identifier.'''
        ...
    
    @id.setter
    def id(self, value : str):
        '''Gets the identifier.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        ...
    
    @property
    def type_name(self) -> aspose.cad.fileformats.cad.cadconsts.CadEntityTypeName:
        ...
    
    @property
    def child_objects(self) -> List[aspose.cad.fileformats.cad.cadobjects.CadEntityBase]:
        ...
    
    @child_objects.setter
    def child_objects(self, value : List[aspose.cad.fileformats.cad.cadobjects.CadEntityBase]):
        ...
    
    @property
    def color_id(self) -> int:
        ...
    
    @color_id.setter
    def color_id(self, value : int):
        ...
    
    @property
    def layout_tab_name(self) -> str:
        ...
    
    @layout_tab_name.setter
    def layout_tab_name(self, value : str):
        ...
    
    @property
    def color_name(self) -> str:
        ...
    
    @color_name.setter
    def color_name(self, value : str):
        ...
    
    @property
    def color_value(self) -> Optional[int]:
        ...
    
    @color_value.setter
    def color_value(self, value : Optional[int]):
        ...
    
    @property
    def layer_name(self) -> str:
        ...
    
    @layer_name.setter
    def layer_name(self, value : str):
        ...
    
    @property
    def line_scale(self) -> float:
        ...
    
    @line_scale.setter
    def line_scale(self, value : float):
        ...
    
    @property
    def line_type_name(self) -> str:
        ...
    
    @line_type_name.setter
    def line_type_name(self, value : str):
        ...
    
    @property
    def line_weight(self) -> int:
        ...
    
    @line_weight.setter
    def line_weight(self, value : int):
        ...
    
    @property
    def material(self) -> str:
        '''Gets the material.'''
        ...
    
    @material.setter
    def material(self, value : str):
        '''Sets the material.'''
        ...
    
    @property
    def color_handle(self) -> str:
        ...
    
    @color_handle.setter
    def color_handle(self, value : str):
        ...
    
    @property
    def plot_style(self) -> str:
        ...
    
    @plot_style.setter
    def plot_style(self, value : str):
        ...
    
    @property
    def proxy_bytes_count(self) -> Optional[int]:
        ...
    
    @proxy_bytes_count.setter
    def proxy_bytes_count(self, value : Optional[int]):
        ...
    
    @property
    def proxy_data(self) -> bytes:
        ...
    
    @proxy_data.setter
    def proxy_data(self, value : bytes):
        ...
    
    @property
    def shadow_mode(self) -> Optional[aspose.cad.fileformats.cad.cadconsts.CadShadowMode]:
        ...
    
    @shadow_mode.setter
    def shadow_mode(self, value : Optional[aspose.cad.fileformats.cad.cadconsts.CadShadowMode]):
        ...
    
    @property
    def space_mode(self) -> aspose.cad.fileformats.cad.cadconsts.CadEntitySpaceMode:
        ...
    
    @space_mode.setter
    def space_mode(self, value : aspose.cad.fileformats.cad.cadconsts.CadEntitySpaceMode):
        ...
    
    @property
    def bounds(self) -> List[aspose.cad.fileformats.cad.cadobjects.Cad3DPoint]:
        '''Minimal and maximal points of entity. Filled after GetBounds is called for CadImage.'''
        ...
    
    @bounds.setter
    def bounds(self, value : List[aspose.cad.fileformats.cad.cadobjects.Cad3DPoint]):
        '''Minimal and maximal points of entity. Filled after GetBounds is called for CadImage.'''
        ...
    
    @property
    def transparency(self) -> Optional[int]:
        '''Gets the transparency value for the entity.'''
        ...
    
    @transparency.setter
    def transparency(self, value : Optional[int]):
        '''Sets the transparency value for the entity.'''
        ...
    
    @property
    def visible(self) -> int:
        '''Gets a value indicating whether this :py:class:`aspose.cad.fileformats.cad.cadobjects.CadEntityBase` is visible.'''
        ...
    
    @visible.setter
    def visible(self, value : int):
        '''Sets a value indicating whether this :py:class:`aspose.cad.fileformats.cad.cadobjects.CadEntityBase` is visible.'''
        ...
    
    @property
    def hyperlink(self) -> str:
        '''Gets a hyperlink to an entity and displays the hyperlink name or description (if one is specified).'''
        ...
    
    @hyperlink.setter
    def hyperlink(self, value : str):
        '''Sets a hyperlink to an entity and displays the hyperlink name or description (if one is specified).'''
        ...
    
    @property
    def entmode(self) -> byte:
        '''Gets the entity mode'''
        ...
    
    @entmode.setter
    def entmode(self, value : byte):
        '''Sets the entity mode'''
        ...
    
    @property
    def x_dir_missing_flag(self) -> bool:
        ...
    
    @x_dir_missing_flag.setter
    def x_dir_missing_flag(self, value : bool):
        ...
    
    @property
    def is_by_layer(self) -> bool:
        ...
    
    @is_by_layer.setter
    def is_by_layer(self, value : bool):
        ...
    
    @property
    def is_no_links(self) -> bool:
        ...
    
    @is_no_links.setter
    def is_no_links(self, value : bool):
        ...
    
    @property
    def l_type(self) -> byte:
        ...
    
    @l_type.setter
    def l_type(self, value : byte):
        ...
    
    @property
    def plot_style_flag(self) -> byte:
        ...
    
    @plot_style_flag.setter
    def plot_style_flag(self, value : byte):
        ...
    
    @property
    def assoc_view_port_handle(self) -> str:
        ...
    
    @property
    def is_assoc_view_port_handle_set(self) -> bool:
        ...
    
    @property
    def area(self) -> float:
        '''Gets the area of the entity.'''
        ...
    
    @property
    def length(self) -> float:
        '''Gets the length of the entity.'''
        ...
    
    @property
    def group_handle(self) -> str:
        ...
    
    @group_handle.setter
    def group_handle(self, value : str):
        ...
    
    @property
    def extrusion_direction(self) -> aspose.cad.fileformats.cad.cadobjects.Cad3DPoint:
        ...
    
    @extrusion_direction.setter
    def extrusion_direction(self, value : aspose.cad.fileformats.cad.cadobjects.Cad3DPoint):
        ...
    
    @property
    def duplicate_record_cloning_flag(self) -> Optional[int]:
        ...
    
    @duplicate_record_cloning_flag.setter
    def duplicate_record_cloning_flag(self, value : Optional[int]):
        ...
    
    @property
    def m_text_flag(self) -> Optional[int]:
        ...
    
    @m_text_flag.setter
    def m_text_flag(self, value : Optional[int]):
        ...
    
    @property
    def is_really_locked_flag(self) -> Optional[int]:
        ...
    
    @is_really_locked_flag.setter
    def is_really_locked_flag(self, value : Optional[int]):
        ...
    
    @property
    def secondary_attributes_or_attribute_definitions_number(self) -> Optional[int]:
        ...
    
    @secondary_attributes_or_attribute_definitions_number.setter
    def secondary_attributes_or_attribute_definitions_number(self, value : Optional[int]):
        ...
    
    @property
    def hard_pointer_ids(self) -> List[str]:
        ...
    
    @hard_pointer_ids.setter
    def hard_pointer_ids(self, value : List[str]):
        ...
    
    @property
    def current_annotation_scale(self) -> Optional[float]:
        ...
    
    @current_annotation_scale.setter
    def current_annotation_scale(self, value : Optional[float]):
        ...
    
    @property
    def definition_tag_string(self) -> str:
        ...
    
    @definition_tag_string.setter
    def definition_tag_string(self, value : str):
        ...
    
    @property
    def text_sub_class_attribute51(self) -> Optional[float]:
        ...
    
    @text_sub_class_attribute51.setter
    def text_sub_class_attribute51(self, value : Optional[float]):
        ...
    
    @property
    def field_length(self) -> int:
        ...
    
    @field_length.setter
    def field_length(self, value : int):
        ...
    
    @property
    def lock_position_flag(self) -> Optional[int]:
        ...
    
    @lock_position_flag.setter
    def lock_position_flag(self, value : Optional[int]):
        ...
    
    @property
    def attrib_alignment_point(self) -> aspose.cad.fileformats.cad.cadobjects.Cad3DPoint:
        ...
    
    @attrib_alignment_point.setter
    def attrib_alignment_point(self, value : aspose.cad.fileformats.cad.cadobjects.Cad3DPoint):
        ...
    
    @property
    def attribute_flags(self) -> int:
        ...
    
    @attribute_flags.setter
    def attribute_flags(self, value : int):
        ...
    
    @property
    def style_type(self) -> str:
        ...
    
    @style_type.setter
    def style_type(self, value : str):
        ...
    
    @property
    def attribute_text_style_name(self) -> str:
        ...
    
    @attribute_text_style_name.setter
    def attribute_text_style_name(self, value : str):
        ...
    
    @property
    def attribute_text_rotation(self) -> float:
        ...
    
    @attribute_text_rotation.setter
    def attribute_text_rotation(self, value : float):
        ...
    
    @property
    def text_rotation(self) -> float:
        ...
    
    @text_rotation.setter
    def text_rotation(self, value : float):
        ...
    
    @property
    def default_text(self) -> str:
        ...
    
    @default_text.setter
    def default_text(self, value : str):
        ...
    
    @property
    def multi_text(self) -> aspose.cad.fileformats.cad.cadobjects.CadMText:
        ...
    
    @multi_text.setter
    def multi_text(self, value : aspose.cad.fileformats.cad.cadobjects.CadMText):
        ...
    
    @property
    def text_height(self) -> float:
        ...
    
    @text_height.setter
    def text_height(self, value : float):
        ...
    
    @property
    def text_start_point(self) -> aspose.cad.fileformats.cad.cadobjects.Cad3DPoint:
        ...
    
    @text_start_point.setter
    def text_start_point(self, value : aspose.cad.fileformats.cad.cadobjects.Cad3DPoint):
        ...
    
    @property
    def thickness(self) -> float:
        '''Gets the thickness.'''
        ...
    
    @thickness.setter
    def thickness(self, value : float):
        '''Sets the thickness.'''
        ...
    
    @property
    def oblique_angle(self) -> float:
        ...
    
    @oblique_angle.setter
    def oblique_angle(self, value : float):
        ...
    
    @property
    def relative_scale(self) -> float:
        ...
    
    @relative_scale.setter
    def relative_scale(self, value : float):
        ...
    
    @property
    def attribute_relative_scale(self) -> float:
        ...
    
    @attribute_relative_scale.setter
    def attribute_relative_scale(self, value : float):
        ...
    
    @property
    def text_flags(self) -> int:
        ...
    
    @text_flags.setter
    def text_flags(self, value : int):
        ...
    
    @property
    def text_just_h(self) -> int:
        ...
    
    @text_just_h.setter
    def text_just_h(self, value : int):
        ...
    
    @property
    def text_just_v(self) -> int:
        ...
    
    @text_just_v.setter
    def text_just_v(self, value : int):
        ...
    
    @property
    def version(self) -> Optional[int]:
        '''Gets the version.'''
        ...
    
    @version.setter
    def version(self, value : Optional[int]):
        '''Sets the version.'''
        ...
    
    @property
    def attribute_string(self) -> str:
        ...
    
    @attribute_string.setter
    def attribute_string(self, value : str):
        ...
    
    ...

class CadXrecordObject(aspose.cad.fileformats.cad.cadobjects.CadExtrudedEntityBase):
    '''Class describing Xrecord object.'''
    
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
    def id(self) -> str:
        '''Gets the identifier.'''
        ...
    
    @id.setter
    def id(self, value : str):
        '''Gets the identifier.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        ...
    
    @property
    def type_name(self) -> aspose.cad.fileformats.cad.cadconsts.CadEntityTypeName:
        ...
    
    @property
    def child_objects(self) -> List[aspose.cad.fileformats.cad.cadobjects.CadEntityBase]:
        ...
    
    @child_objects.setter
    def child_objects(self, value : List[aspose.cad.fileformats.cad.cadobjects.CadEntityBase]):
        ...
    
    @property
    def color_id(self) -> int:
        ...
    
    @color_id.setter
    def color_id(self, value : int):
        ...
    
    @property
    def layout_tab_name(self) -> str:
        ...
    
    @layout_tab_name.setter
    def layout_tab_name(self, value : str):
        ...
    
    @property
    def color_name(self) -> str:
        ...
    
    @color_name.setter
    def color_name(self, value : str):
        ...
    
    @property
    def color_value(self) -> Optional[int]:
        ...
    
    @color_value.setter
    def color_value(self, value : Optional[int]):
        ...
    
    @property
    def layer_name(self) -> str:
        ...
    
    @layer_name.setter
    def layer_name(self, value : str):
        ...
    
    @property
    def line_scale(self) -> float:
        ...
    
    @line_scale.setter
    def line_scale(self, value : float):
        ...
    
    @property
    def line_type_name(self) -> str:
        ...
    
    @line_type_name.setter
    def line_type_name(self, value : str):
        ...
    
    @property
    def line_weight(self) -> int:
        ...
    
    @line_weight.setter
    def line_weight(self, value : int):
        ...
    
    @property
    def material(self) -> str:
        '''Gets the material.'''
        ...
    
    @material.setter
    def material(self, value : str):
        '''Sets the material.'''
        ...
    
    @property
    def color_handle(self) -> str:
        ...
    
    @color_handle.setter
    def color_handle(self, value : str):
        ...
    
    @property
    def plot_style(self) -> str:
        ...
    
    @plot_style.setter
    def plot_style(self, value : str):
        ...
    
    @property
    def proxy_bytes_count(self) -> Optional[int]:
        ...
    
    @proxy_bytes_count.setter
    def proxy_bytes_count(self, value : Optional[int]):
        ...
    
    @property
    def proxy_data(self) -> bytes:
        ...
    
    @proxy_data.setter
    def proxy_data(self, value : bytes):
        ...
    
    @property
    def shadow_mode(self) -> Optional[aspose.cad.fileformats.cad.cadconsts.CadShadowMode]:
        ...
    
    @shadow_mode.setter
    def shadow_mode(self, value : Optional[aspose.cad.fileformats.cad.cadconsts.CadShadowMode]):
        ...
    
    @property
    def space_mode(self) -> aspose.cad.fileformats.cad.cadconsts.CadEntitySpaceMode:
        ...
    
    @space_mode.setter
    def space_mode(self, value : aspose.cad.fileformats.cad.cadconsts.CadEntitySpaceMode):
        ...
    
    @property
    def bounds(self) -> List[aspose.cad.fileformats.cad.cadobjects.Cad3DPoint]:
        '''Minimal and maximal points of entity. Filled after GetBounds is called for CadImage.'''
        ...
    
    @bounds.setter
    def bounds(self, value : List[aspose.cad.fileformats.cad.cadobjects.Cad3DPoint]):
        '''Minimal and maximal points of entity. Filled after GetBounds is called for CadImage.'''
        ...
    
    @property
    def transparency(self) -> Optional[int]:
        '''Gets the transparency value for the entity.'''
        ...
    
    @transparency.setter
    def transparency(self, value : Optional[int]):
        '''Sets the transparency value for the entity.'''
        ...
    
    @property
    def visible(self) -> int:
        '''Gets a value indicating whether this :py:class:`aspose.cad.fileformats.cad.cadobjects.CadEntityBase` is visible.'''
        ...
    
    @visible.setter
    def visible(self, value : int):
        '''Sets a value indicating whether this :py:class:`aspose.cad.fileformats.cad.cadobjects.CadEntityBase` is visible.'''
        ...
    
    @property
    def hyperlink(self) -> str:
        '''Gets a hyperlink to an entity and displays the hyperlink name or description (if one is specified).'''
        ...
    
    @hyperlink.setter
    def hyperlink(self, value : str):
        '''Sets a hyperlink to an entity and displays the hyperlink name or description (if one is specified).'''
        ...
    
    @property
    def entmode(self) -> byte:
        '''Gets the entity mode'''
        ...
    
    @entmode.setter
    def entmode(self, value : byte):
        '''Sets the entity mode'''
        ...
    
    @property
    def x_dir_missing_flag(self) -> bool:
        ...
    
    @x_dir_missing_flag.setter
    def x_dir_missing_flag(self, value : bool):
        ...
    
    @property
    def is_by_layer(self) -> bool:
        ...
    
    @is_by_layer.setter
    def is_by_layer(self, value : bool):
        ...
    
    @property
    def is_no_links(self) -> bool:
        ...
    
    @is_no_links.setter
    def is_no_links(self, value : bool):
        ...
    
    @property
    def l_type(self) -> byte:
        ...
    
    @l_type.setter
    def l_type(self, value : byte):
        ...
    
    @property
    def plot_style_flag(self) -> byte:
        ...
    
    @plot_style_flag.setter
    def plot_style_flag(self, value : byte):
        ...
    
    @property
    def assoc_view_port_handle(self) -> str:
        ...
    
    @property
    def is_assoc_view_port_handle_set(self) -> bool:
        ...
    
    @property
    def area(self) -> float:
        '''Gets the area of the entity.'''
        ...
    
    @property
    def length(self) -> float:
        '''Gets the length of the entity.'''
        ...
    
    @property
    def group_handle(self) -> str:
        ...
    
    @group_handle.setter
    def group_handle(self, value : str):
        ...
    
    @property
    def extrusion_direction(self) -> aspose.cad.fileformats.cad.cadobjects.Cad3DPoint:
        ...
    
    @extrusion_direction.setter
    def extrusion_direction(self, value : aspose.cad.fileformats.cad.cadobjects.Cad3DPoint):
        ...
    
    @property
    def duplicate_record_cloning_flag(self) -> Optional[int]:
        ...
    
    @duplicate_record_cloning_flag.setter
    def duplicate_record_cloning_flag(self, value : Optional[int]):
        ...
    
    @property
    def m_text_flag(self) -> Optional[int]:
        ...
    
    @m_text_flag.setter
    def m_text_flag(self, value : Optional[int]):
        ...
    
    @property
    def is_really_locked_flag(self) -> Optional[int]:
        ...
    
    @is_really_locked_flag.setter
    def is_really_locked_flag(self, value : Optional[int]):
        ...
    
    @property
    def secondary_attributes_or_attribute_definitions_number(self) -> Optional[int]:
        ...
    
    @secondary_attributes_or_attribute_definitions_number.setter
    def secondary_attributes_or_attribute_definitions_number(self, value : Optional[int]):
        ...
    
    @property
    def hard_pointer_ids(self) -> List[str]:
        ...
    
    @hard_pointer_ids.setter
    def hard_pointer_ids(self, value : List[str]):
        ...
    
    @property
    def current_annotation_scale(self) -> Optional[float]:
        ...
    
    @current_annotation_scale.setter
    def current_annotation_scale(self, value : Optional[float]):
        ...
    
    @property
    def definition_tag_string(self) -> str:
        ...
    
    @definition_tag_string.setter
    def definition_tag_string(self, value : str):
        ...
    
    ...

