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

class CadWipeout(CadWipeoutBase):
    '''The Cad wipeout.'''
    
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
    def clipping_boundary_type(self) -> int:
        ...
    
    @clipping_boundary_type.setter
    def clipping_boundary_type(self, value : int):
        ...
    
    @property
    def wipeout_brightness(self) -> int:
        ...
    
    @wipeout_brightness.setter
    def wipeout_brightness(self, value : int):
        ...
    
    @property
    def class_version(self) -> int:
        ...
    
    @class_version.setter
    def class_version(self, value : int):
        ...
    
    @property
    def clip_boundaries(self) -> List[aspose.cad.fileformats.cad.cadobjects.Cad2DPoint]:
        ...
    
    @clip_boundaries.setter
    def clip_boundaries(self, value : List[aspose.cad.fileformats.cad.cadobjects.Cad2DPoint]):
        ...
    
    @property
    def clip_boundaries_count(self) -> int:
        ...
    
    @clip_boundaries_count.setter
    def clip_boundaries_count(self, value : int):
        ...
    
    @property
    def clipping_state(self) -> int:
        ...
    
    @clipping_state.setter
    def clipping_state(self, value : int):
        ...
    
    @property
    def wipeout_contrast(self) -> int:
        ...
    
    @wipeout_contrast.setter
    def wipeout_contrast(self, value : int):
        ...
    
    @property
    def fade(self) -> int:
        '''Gets the fade.'''
        ...
    
    @fade.setter
    def fade(self, value : int):
        '''Sets the fade.'''
        ...
    
    @property
    def image_def_reactor_reference(self) -> str:
        ...
    
    @image_def_reactor_reference.setter
    def image_def_reactor_reference(self, value : str):
        ...
    
    @property
    def image_def_reference(self) -> str:
        ...
    
    @image_def_reference.setter
    def image_def_reference(self, value : str):
        ...
    
    @property
    def image_display_prop(self) -> int:
        ...
    
    @image_display_prop.setter
    def image_display_prop(self, value : int):
        ...
    
    @property
    def image_size_in_pixels(self) -> aspose.cad.fileformats.cad.cadobjects.Cad2DPoint:
        ...
    
    @image_size_in_pixels.setter
    def image_size_in_pixels(self, value : aspose.cad.fileformats.cad.cadobjects.Cad2DPoint):
        ...
    
    @property
    def insertion_point(self) -> aspose.cad.fileformats.cad.cadobjects.Cad3DPoint:
        ...
    
    @insertion_point.setter
    def insertion_point(self, value : aspose.cad.fileformats.cad.cadobjects.Cad3DPoint):
        ...
    
    @property
    def vector_u(self) -> aspose.cad.fileformats.cad.cadobjects.Cad3DPoint:
        ...
    
    @vector_u.setter
    def vector_u(self, value : aspose.cad.fileformats.cad.cadobjects.Cad3DPoint):
        ...
    
    @property
    def vector_v(self) -> aspose.cad.fileformats.cad.cadobjects.Cad3DPoint:
        ...
    
    @vector_v.setter
    def vector_v(self, value : aspose.cad.fileformats.cad.cadobjects.Cad3DPoint):
        ...
    
    @property
    def clipping_mode(self) -> bool:
        ...
    
    @clipping_mode.setter
    def clipping_mode(self, value : bool):
        ...
    
    ...

class CadWipeoutBase(aspose.cad.fileformats.cad.cadobjects.CadEntityBase):
    '''The Cad wipeout.'''
    
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
    def clipping_boundary_type(self) -> int:
        ...
    
    @clipping_boundary_type.setter
    def clipping_boundary_type(self, value : int):
        ...
    
    @property
    def wipeout_brightness(self) -> int:
        ...
    
    @wipeout_brightness.setter
    def wipeout_brightness(self, value : int):
        ...
    
    @property
    def class_version(self) -> int:
        ...
    
    @class_version.setter
    def class_version(self, value : int):
        ...
    
    @property
    def clip_boundaries(self) -> List[aspose.cad.fileformats.cad.cadobjects.Cad2DPoint]:
        ...
    
    @clip_boundaries.setter
    def clip_boundaries(self, value : List[aspose.cad.fileformats.cad.cadobjects.Cad2DPoint]):
        ...
    
    @property
    def clip_boundaries_count(self) -> int:
        ...
    
    @clip_boundaries_count.setter
    def clip_boundaries_count(self, value : int):
        ...
    
    @property
    def clipping_state(self) -> int:
        ...
    
    @clipping_state.setter
    def clipping_state(self, value : int):
        ...
    
    @property
    def wipeout_contrast(self) -> int:
        ...
    
    @wipeout_contrast.setter
    def wipeout_contrast(self, value : int):
        ...
    
    @property
    def fade(self) -> int:
        '''Gets the fade.'''
        ...
    
    @fade.setter
    def fade(self, value : int):
        '''Sets the fade.'''
        ...
    
    @property
    def image_def_reactor_reference(self) -> str:
        ...
    
    @image_def_reactor_reference.setter
    def image_def_reactor_reference(self, value : str):
        ...
    
    @property
    def image_def_reference(self) -> str:
        ...
    
    @image_def_reference.setter
    def image_def_reference(self, value : str):
        ...
    
    @property
    def image_display_prop(self) -> int:
        ...
    
    @image_display_prop.setter
    def image_display_prop(self, value : int):
        ...
    
    @property
    def image_size_in_pixels(self) -> aspose.cad.fileformats.cad.cadobjects.Cad2DPoint:
        ...
    
    @image_size_in_pixels.setter
    def image_size_in_pixels(self, value : aspose.cad.fileformats.cad.cadobjects.Cad2DPoint):
        ...
    
    @property
    def insertion_point(self) -> aspose.cad.fileformats.cad.cadobjects.Cad3DPoint:
        ...
    
    @insertion_point.setter
    def insertion_point(self, value : aspose.cad.fileformats.cad.cadobjects.Cad3DPoint):
        ...
    
    @property
    def vector_u(self) -> aspose.cad.fileformats.cad.cadobjects.Cad3DPoint:
        ...
    
    @vector_u.setter
    def vector_u(self, value : aspose.cad.fileformats.cad.cadobjects.Cad3DPoint):
        ...
    
    @property
    def vector_v(self) -> aspose.cad.fileformats.cad.cadobjects.Cad3DPoint:
        ...
    
    @vector_v.setter
    def vector_v(self, value : aspose.cad.fileformats.cad.cadobjects.Cad3DPoint):
        ...
    
    ...

class CadWipeoutRasterImage(CadWipeoutBase):
    '''The Cad Wipeout RasterImage.'''
    
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
    def clipping_boundary_type(self) -> int:
        ...
    
    @clipping_boundary_type.setter
    def clipping_boundary_type(self, value : int):
        ...
    
    @property
    def wipeout_brightness(self) -> int:
        ...
    
    @wipeout_brightness.setter
    def wipeout_brightness(self, value : int):
        ...
    
    @property
    def class_version(self) -> int:
        ...
    
    @class_version.setter
    def class_version(self, value : int):
        ...
    
    @property
    def clip_boundaries(self) -> List[aspose.cad.fileformats.cad.cadobjects.Cad2DPoint]:
        ...
    
    @clip_boundaries.setter
    def clip_boundaries(self, value : List[aspose.cad.fileformats.cad.cadobjects.Cad2DPoint]):
        ...
    
    @property
    def clip_boundaries_count(self) -> int:
        ...
    
    @clip_boundaries_count.setter
    def clip_boundaries_count(self, value : int):
        ...
    
    @property
    def clipping_state(self) -> int:
        ...
    
    @clipping_state.setter
    def clipping_state(self, value : int):
        ...
    
    @property
    def wipeout_contrast(self) -> int:
        ...
    
    @wipeout_contrast.setter
    def wipeout_contrast(self, value : int):
        ...
    
    @property
    def fade(self) -> int:
        '''Gets the fade.'''
        ...
    
    @fade.setter
    def fade(self, value : int):
        '''Sets the fade.'''
        ...
    
    @property
    def image_def_reactor_reference(self) -> str:
        ...
    
    @image_def_reactor_reference.setter
    def image_def_reactor_reference(self, value : str):
        ...
    
    @property
    def image_def_reference(self) -> str:
        ...
    
    @image_def_reference.setter
    def image_def_reference(self, value : str):
        ...
    
    @property
    def image_display_prop(self) -> int:
        ...
    
    @image_display_prop.setter
    def image_display_prop(self, value : int):
        ...
    
    @property
    def image_size_in_pixels(self) -> aspose.cad.fileformats.cad.cadobjects.Cad2DPoint:
        ...
    
    @image_size_in_pixels.setter
    def image_size_in_pixels(self, value : aspose.cad.fileformats.cad.cadobjects.Cad2DPoint):
        ...
    
    @property
    def insertion_point(self) -> aspose.cad.fileformats.cad.cadobjects.Cad3DPoint:
        ...
    
    @insertion_point.setter
    def insertion_point(self, value : aspose.cad.fileformats.cad.cadobjects.Cad3DPoint):
        ...
    
    @property
    def vector_u(self) -> aspose.cad.fileformats.cad.cadobjects.Cad3DPoint:
        ...
    
    @vector_u.setter
    def vector_u(self, value : aspose.cad.fileformats.cad.cadobjects.Cad3DPoint):
        ...
    
    @property
    def vector_v(self) -> aspose.cad.fileformats.cad.cadobjects.Cad3DPoint:
        ...
    
    @vector_v.setter
    def vector_v(self, value : aspose.cad.fileformats.cad.cadobjects.Cad3DPoint):
        ...
    
    ...

