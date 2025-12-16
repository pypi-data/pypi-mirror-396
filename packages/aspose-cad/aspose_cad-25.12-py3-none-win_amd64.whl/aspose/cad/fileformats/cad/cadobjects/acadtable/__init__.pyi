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

class CadFormattedTableData:
    '''The cad formatted table data'''
    
    @property
    def cell_style(self) -> aspose.cad.fileformats.cad.cadobjects.tablestyle.CadTableStyleCell:
        ...
    
    @cell_style.setter
    def cell_style(self, value : aspose.cad.fileformats.cad.cadobjects.tablestyle.CadTableStyleCell):
        ...
    
    @property
    def merged_cell_ranges(self) -> List[aspose.cad.fileformats.cad.cadobjects.acadtable.FormattedTableCellRange]:
        ...
    
    @merged_cell_ranges.setter
    def merged_cell_ranges(self, value : List[aspose.cad.fileformats.cad.cadobjects.acadtable.FormattedTableCellRange]):
        ...
    
    ...

class CadLinkedTableData:
    '''The cad linked table data'''
    
    @property
    def columns(self) -> List[aspose.cad.fileformats.cad.cadobjects.acadtable.TableDataColumn]:
        '''The linked table columns data'''
        ...
    
    @columns.setter
    def columns(self, value : List[aspose.cad.fileformats.cad.cadobjects.acadtable.TableDataColumn]):
        '''The linked table columns data'''
        ...
    
    @property
    def rows(self) -> List[aspose.cad.fileformats.cad.cadobjects.acadtable.TableDataRow]:
        '''The linked table rows data'''
        ...
    
    @rows.setter
    def rows(self, value : List[aspose.cad.fileformats.cad.cadobjects.acadtable.TableDataRow]):
        '''The linked table rows data'''
        ...
    
    @property
    def number_of_cell_that_contains_field_refs(self) -> int:
        ...
    
    @number_of_cell_that_contains_field_refs.setter
    def number_of_cell_that_contains_field_refs(self, value : int):
        ...
    
    ...

class CadTableCell:
    '''The TableStyleCell data'''
    
    @property
    def cell_content_color(self) -> int:
        ...
    
    @cell_content_color.setter
    def cell_content_color(self, value : int):
        ...
    
    @property
    def cell_content_background_color(self) -> int:
        ...
    
    @cell_content_background_color.setter
    def cell_content_background_color(self, value : int):
        ...
    
    @property
    def cell_top_border_color(self) -> int:
        ...
    
    @cell_top_border_color.setter
    def cell_top_border_color(self, value : int):
        ...
    
    @property
    def cell_right_border_color(self) -> int:
        ...
    
    @cell_right_border_color.setter
    def cell_right_border_color(self, value : int):
        ...
    
    @property
    def cell_bottom_border_color(self) -> int:
        ...
    
    @cell_bottom_border_color.setter
    def cell_bottom_border_color(self, value : int):
        ...
    
    @property
    def cell_left_border_color(self) -> int:
        ...
    
    @cell_left_border_color.setter
    def cell_left_border_color(self, value : int):
        ...
    
    @property
    def cell_top_border_lineweight(self) -> int:
        ...
    
    @cell_top_border_lineweight.setter
    def cell_top_border_lineweight(self, value : int):
        ...
    
    @property
    def cell_right_border_lineweight(self) -> int:
        ...
    
    @cell_right_border_lineweight.setter
    def cell_right_border_lineweight(self, value : int):
        ...
    
    @property
    def cell_bottom_border_lineweight(self) -> int:
        ...
    
    @cell_bottom_border_lineweight.setter
    def cell_bottom_border_lineweight(self, value : int):
        ...
    
    @property
    def cell_left_border_lineweight(self) -> int:
        ...
    
    @cell_left_border_lineweight.setter
    def cell_left_border_lineweight(self, value : int):
        ...
    
    @property
    def fill_color_flag(self) -> int:
        ...
    
    @fill_color_flag.setter
    def fill_color_flag(self, value : int):
        ...
    
    @property
    def top_border_visibility_flag(self) -> int:
        ...
    
    @top_border_visibility_flag.setter
    def top_border_visibility_flag(self, value : int):
        ...
    
    @property
    def right_border_visibility_flag(self) -> int:
        ...
    
    @right_border_visibility_flag.setter
    def right_border_visibility_flag(self, value : int):
        ...
    
    @property
    def bottom_border_visibility_flag(self) -> int:
        ...
    
    @bottom_border_visibility_flag.setter
    def bottom_border_visibility_flag(self, value : int):
        ...
    
    @property
    def left_border_visibility_flag(self) -> int:
        ...
    
    @left_border_visibility_flag.setter
    def left_border_visibility_flag(self, value : int):
        ...
    
    @property
    def text_style_name(self) -> str:
        ...
    
    @text_style_name.setter
    def text_style_name(self, value : str):
        ...
    
    @property
    def attrib_def_soft_pointer(self) -> str:
        ...
    
    @attrib_def_soft_pointer.setter
    def attrib_def_soft_pointer(self, value : str):
        ...
    
    @property
    def attribute_definitions_count(self) -> int:
        ...
    
    @attribute_definitions_count.setter
    def attribute_definitions_count(self, value : int):
        ...
    
    @property
    def attribute_definitions_index(self) -> int:
        ...
    
    @attribute_definitions_index.setter
    def attribute_definitions_index(self, value : int):
        ...
    
    @property
    def hard_pointer_id(self) -> str:
        ...
    
    @hard_pointer_id.setter
    def hard_pointer_id(self, value : str):
        ...
    
    @property
    def block_scale(self) -> str:
        ...
    
    @block_scale.setter
    def block_scale(self, value : str):
        ...
    
    @property
    def cell_alignment(self) -> int:
        ...
    
    @cell_alignment.setter
    def cell_alignment(self, value : int):
        ...
    
    @property
    def cell_type(self) -> int:
        ...
    
    @cell_type.setter
    def cell_type(self, value : int):
        ...
    
    @property
    def cell_flag_value(self) -> int:
        ...
    
    @cell_flag_value.setter
    def cell_flag_value(self, value : int):
        ...
    
    @property
    def cell_merged_value(self) -> int:
        ...
    
    @cell_merged_value.setter
    def cell_merged_value(self, value : int):
        ...
    
    @property
    def boolean_flag(self) -> int:
        ...
    
    @boolean_flag.setter
    def boolean_flag(self, value : int):
        ...
    
    @property
    def cell_border_width(self) -> int:
        ...
    
    @cell_border_width.setter
    def cell_border_width(self, value : int):
        ...
    
    @property
    def cell_border_height(self) -> int:
        ...
    
    @cell_border_height.setter
    def cell_border_height(self, value : int):
        ...
    
    @property
    def cell_override_flag(self) -> int:
        ...
    
    @cell_override_flag.setter
    def cell_override_flag(self, value : int):
        ...
    
    @property
    def virtual_edge_flag_value(self) -> int:
        ...
    
    @virtual_edge_flag_value.setter
    def virtual_edge_flag_value(self, value : int):
        ...
    
    @property
    def rotation_value(self) -> int:
        ...
    
    @rotation_value.setter
    def rotation_value(self, value : int):
        ...
    
    @property
    def hard_pointer_to_field(self) -> str:
        ...
    
    @hard_pointer_to_field.setter
    def hard_pointer_to_field(self, value : str):
        ...
    
    @property
    def text_height_value(self) -> float:
        ...
    
    @text_height_value.setter
    def text_height_value(self, value : float):
        ...
    
    @property
    def extended_cell_flag(self) -> int:
        ...
    
    @extended_cell_flag.setter
    def extended_cell_flag(self, value : int):
        ...
    
    @property
    def cell_value_block_begin(self) -> str:
        ...
    
    @cell_value_block_begin.setter
    def cell_value_block_begin(self, value : str):
        ...
    
    @property
    def attribute93(self) -> int:
        '''Gets the attribute93.'''
        ...
    
    @attribute93.setter
    def attribute93(self, value : int):
        '''Sets the attribute93.'''
        ...
    
    @property
    def attribute90(self) -> int:
        '''Gets the attribute90.'''
        ...
    
    @attribute90.setter
    def attribute90(self, value : int):
        '''Sets the attribute90.'''
        ...
    
    @property
    def text_string(self) -> str:
        ...
    
    @text_string.setter
    def text_string(self, value : str):
        ...
    
    @property
    def additional_string(self) -> str:
        ...
    
    @additional_string.setter
    def additional_string(self, value : str):
        ...
    
    @property
    def attribute94(self) -> int:
        '''Gets the attribute94.'''
        ...
    
    @attribute94.setter
    def attribute94(self, value : int):
        '''Sets the attribute94.'''
        ...
    
    @property
    def attribute_definition_text_string(self) -> str:
        ...
    
    @attribute_definition_text_string.setter
    def attribute_definition_text_string(self, value : str):
        ...
    
    @property
    def text_string_in_cell(self) -> str:
        ...
    
    @text_string_in_cell.setter
    def text_string_in_cell(self, value : str):
        ...
    
    @property
    def attribute304(self) -> str:
        '''Gets the attribute304.'''
        ...
    
    @attribute304.setter
    def attribute304(self, value : str):
        '''Sets the attribute304.'''
        ...
    
    ...

class CadTableEntity(aspose.cad.fileformats.cad.cadobjects.CadEntityBase):
    '''The Cad table'''
    
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
    def table_cell_list(self) -> List[aspose.cad.fileformats.cad.cadobjects.acadtable.CadTableCell]:
        ...
    
    @table_cell_list.setter
    def table_cell_list(self, value : List[aspose.cad.fileformats.cad.cadobjects.acadtable.CadTableCell]):
        ...
    
    @property
    def attribute_140_list(self) -> List[float]:
        ...
    
    @attribute_140_list.setter
    def attribute_140_list(self, value : List[float]):
        ...
    
    @property
    def horizontal_cell_margin(self) -> float:
        ...
    
    @horizontal_cell_margin.setter
    def horizontal_cell_margin(self, value : float):
        ...
    
    @property
    def vertical_cell_margin(self) -> float:
        ...
    
    @vertical_cell_margin.setter
    def vertical_cell_margin(self, value : float):
        ...
    
    @property
    def block_name(self) -> str:
        ...
    
    @block_name.setter
    def block_name(self, value : str):
        ...
    
    @property
    def flag_for_table_value(self) -> int:
        ...
    
    @flag_for_table_value.setter
    def flag_for_table_value(self, value : int):
        ...
    
    @property
    def flag_override(self) -> int:
        ...
    
    @flag_override.setter
    def flag_override(self, value : int):
        ...
    
    @property
    def flag_override_border_color(self) -> int:
        ...
    
    @flag_override_border_color.setter
    def flag_override_border_color(self, value : int):
        ...
    
    @property
    def flag_override_border_line_weight(self) -> int:
        ...
    
    @flag_override_border_line_weight.setter
    def flag_override_border_line_weight(self, value : int):
        ...
    
    @property
    def flag_override_border_visibility(self) -> int:
        ...
    
    @flag_override_border_visibility.setter
    def flag_override_border_visibility(self, value : int):
        ...
    
    @property
    def insertion_point(self) -> aspose.cad.fileformats.cad.cadobjects.Cad3DPoint:
        ...
    
    @insertion_point.setter
    def insertion_point(self, value : aspose.cad.fileformats.cad.cadobjects.Cad3DPoint):
        ...
    
    @property
    def scale_x(self) -> float:
        ...
    
    @scale_x.setter
    def scale_x(self, value : float):
        ...
    
    @property
    def scale_y(self) -> float:
        ...
    
    @scale_y.setter
    def scale_y(self, value : float):
        ...
    
    @property
    def scale_z(self) -> float:
        ...
    
    @scale_z.setter
    def scale_z(self, value : float):
        ...
    
    @property
    def number_of_columns(self) -> int:
        ...
    
    @number_of_columns.setter
    def number_of_columns(self, value : int):
        ...
    
    @property
    def number_of_rows(self) -> int:
        ...
    
    @number_of_rows.setter
    def number_of_rows(self, value : int):
        ...
    
    @property
    def pointer_id_to_owner_block(self) -> str:
        ...
    
    @pointer_id_to_owner_block.setter
    def pointer_id_to_owner_block(self, value : str):
        ...
    
    @property
    def pointer_id_totablestyle(self) -> str:
        ...
    
    @pointer_id_totablestyle.setter
    def pointer_id_totablestyle(self, value : str):
        ...
    
    @property
    def table_data_version_number(self) -> int:
        ...
    
    @table_data_version_number.setter
    def table_data_version_number(self, value : int):
        ...
    
    @property
    def suppress_title(self) -> int:
        ...
    
    @suppress_title.setter
    def suppress_title(self, value : int):
        ...
    
    @property
    def suppress_header_row(self) -> int:
        ...
    
    @suppress_header_row.setter
    def suppress_header_row(self, value : int):
        ...
    
    @property
    def text_style_name(self) -> List[str]:
        ...
    
    @text_style_name.setter
    def text_style_name(self, value : List[str]):
        ...
    
    @property
    def flow_direction(self) -> int:
        ...
    
    @flow_direction.setter
    def flow_direction(self, value : int):
        ...
    
    @property
    def title_row_color(self) -> int:
        ...
    
    @title_row_color.setter
    def title_row_color(self, value : int):
        ...
    
    @property
    def header_row_color(self) -> int:
        ...
    
    @header_row_color.setter
    def header_row_color(self, value : int):
        ...
    
    @property
    def data_row_color(self) -> int:
        ...
    
    @data_row_color.setter
    def data_row_color(self, value : int):
        ...
    
    @property
    def title_row_fill_none(self) -> bool:
        ...
    
    @title_row_fill_none.setter
    def title_row_fill_none(self, value : bool):
        ...
    
    @property
    def header_row_fill_none(self) -> bool:
        ...
    
    @header_row_fill_none.setter
    def header_row_fill_none(self, value : bool):
        ...
    
    @property
    def data_row_fill_none(self) -> bool:
        ...
    
    @data_row_fill_none.setter
    def data_row_fill_none(self, value : bool):
        ...
    
    @property
    def title_row_fill_color(self) -> int:
        ...
    
    @title_row_fill_color.setter
    def title_row_fill_color(self, value : int):
        ...
    
    @property
    def header_row_fill_color(self) -> int:
        ...
    
    @header_row_fill_color.setter
    def header_row_fill_color(self, value : int):
        ...
    
    @property
    def data_row_fill_color(self) -> int:
        ...
    
    @data_row_fill_color.setter
    def data_row_fill_color(self, value : int):
        ...
    
    @property
    def title_row_align(self) -> int:
        ...
    
    @title_row_align.setter
    def title_row_align(self, value : int):
        ...
    
    @property
    def header_row_align(self) -> int:
        ...
    
    @header_row_align.setter
    def header_row_align(self, value : int):
        ...
    
    @property
    def data_row_align(self) -> int:
        ...
    
    @data_row_align.setter
    def data_row_align(self, value : int):
        ...
    
    @property
    def title_row_height(self) -> float:
        ...
    
    @title_row_height.setter
    def title_row_height(self, value : float):
        ...
    
    @property
    def header_row_height(self) -> float:
        ...
    
    @header_row_height.setter
    def header_row_height(self, value : float):
        ...
    
    @property
    def data_row_height(self) -> float:
        ...
    
    @data_row_height.setter
    def data_row_height(self, value : float):
        ...
    
    @property
    def linked_data_name(self) -> str:
        ...
    
    @linked_data_name.setter
    def linked_data_name(self, value : str):
        ...
    
    @property
    def linked_data_description(self) -> str:
        ...
    
    @linked_data_description.setter
    def linked_data_description(self, value : str):
        ...
    
    @property
    def linked_table_data(self) -> aspose.cad.fileformats.cad.cadobjects.acadtable.CadLinkedTableData:
        ...
    
    @linked_table_data.setter
    def linked_table_data(self, value : aspose.cad.fileformats.cad.cadobjects.acadtable.CadLinkedTableData):
        ...
    
    @property
    def formatted_table_data(self) -> aspose.cad.fileformats.cad.cadobjects.acadtable.CadFormattedTableData:
        ...
    
    @formatted_table_data.setter
    def formatted_table_data(self, value : aspose.cad.fileformats.cad.cadobjects.acadtable.CadFormattedTableData):
        ...
    
    @property
    def has_break_data(self) -> bool:
        ...
    
    @has_break_data.setter
    def has_break_data(self, value : bool):
        ...
    
    @property
    def break_option_flag(self) -> aspose.cad.fileformats.cad.cadconsts.CadTableOptionFlag:
        ...
    
    @break_option_flag.setter
    def break_option_flag(self, value : aspose.cad.fileformats.cad.cadconsts.CadTableOptionFlag):
        ...
    
    @property
    def table_data_break_heights(self) -> List[aspose.cad.fileformats.cad.cadobjects.acadtable.TableDataBreakHeight]:
        ...
    
    @table_data_break_heights.setter
    def table_data_break_heights(self, value : List[aspose.cad.fileformats.cad.cadobjects.acadtable.TableDataBreakHeight]):
        ...
    
    @property
    def break_flow_direction(self) -> int:
        ...
    
    @break_flow_direction.setter
    def break_flow_direction(self, value : int):
        ...
    
    @property
    def break_spacing(self) -> float:
        ...
    
    @break_spacing.setter
    def break_spacing(self, value : float):
        ...
    
    @property
    def table_data_break_rows(self) -> List[aspose.cad.fileformats.cad.cadobjects.acadtable.TableDataBreakRow]:
        ...
    
    @table_data_break_rows.setter
    def table_data_break_rows(self, value : List[aspose.cad.fileformats.cad.cadobjects.acadtable.TableDataBreakRow]):
        ...
    
    ...

class CellContentGeometry:
    '''The cell content geometry'''
    
    @property
    def distance_to_top_left(self) -> aspose.cad.fileformats.cad.cadobjects.Cad3DPoint:
        ...
    
    @distance_to_top_left.setter
    def distance_to_top_left(self, value : aspose.cad.fileformats.cad.cadobjects.Cad3DPoint):
        ...
    
    @property
    def distance_to_center(self) -> aspose.cad.fileformats.cad.cadobjects.Cad3DPoint:
        ...
    
    @distance_to_center.setter
    def distance_to_center(self, value : aspose.cad.fileformats.cad.cadobjects.Cad3DPoint):
        ...
    
    @property
    def content_width(self) -> float:
        ...
    
    @content_width.setter
    def content_width(self, value : float):
        ...
    
    @property
    def content_height(self) -> float:
        ...
    
    @content_height.setter
    def content_height(self, value : float):
        ...
    
    @property
    def width(self) -> float:
        '''The width'''
        ...
    
    @width.setter
    def width(self, value : float):
        '''The width'''
        ...
    
    @property
    def height(self) -> float:
        '''The height'''
        ...
    
    @height.setter
    def height(self, value : float):
        '''The height'''
        ...
    
    @property
    def unknown(self) -> int:
        '''The unknown flags'''
        ...
    
    @unknown.setter
    def unknown(self, value : int):
        '''The unknown flags'''
        ...
    
    ...

class FormattedTableCellRange:
    '''The formatted table cell range'''
    
    @property
    def top_row_index(self) -> int:
        ...
    
    @top_row_index.setter
    def top_row_index(self, value : int):
        ...
    
    @property
    def left_column_index(self) -> int:
        ...
    
    @left_column_index.setter
    def left_column_index(self, value : int):
        ...
    
    @property
    def bottom_row_index(self) -> int:
        ...
    
    @bottom_row_index.setter
    def bottom_row_index(self, value : int):
        ...
    
    @property
    def right_column_index(self) -> int:
        ...
    
    @right_column_index.setter
    def right_column_index(self, value : int):
        ...
    
    ...

class TableCustomData:
    '''The linked table custom data'''
    
    @property
    def name(self) -> str:
        '''The custom data name'''
        ...
    
    @name.setter
    def name(self, value : str):
        '''The custom data name'''
        ...
    
    @property
    def field_data(self) -> aspose.cad.fileformats.cad.cadobjects.field.CadFieldData:
        ...
    
    @field_data.setter
    def field_data(self, value : aspose.cad.fileformats.cad.cadobjects.field.CadFieldData):
        ...
    
    ...

class TableDataBreakHeight:
    '''The table break height data'''
    
    @property
    def position(self) -> aspose.cad.fileformats.cad.cadobjects.Cad3DPoint:
        '''The break position'''
        ...
    
    @position.setter
    def position(self, value : aspose.cad.fileformats.cad.cadobjects.Cad3DPoint):
        '''The break position'''
        ...
    
    @property
    def height(self) -> float:
        '''The break height'''
        ...
    
    @height.setter
    def height(self, value : float):
        '''The break height'''
        ...
    
    @property
    def flags(self) -> int:
        '''The break flags'''
        ...
    
    @flags.setter
    def flags(self, value : int):
        '''The break flags'''
        ...
    
    ...

class TableDataBreakRow:
    '''The table break rows data'''
    
    @property
    def position(self) -> aspose.cad.fileformats.cad.cadobjects.Cad3DPoint:
        '''The break row position'''
        ...
    
    @position.setter
    def position(self, value : aspose.cad.fileformats.cad.cadobjects.Cad3DPoint):
        '''The break row position'''
        ...
    
    @property
    def start_row_index(self) -> int:
        ...
    
    @start_row_index.setter
    def start_row_index(self, value : int):
        ...
    
    @property
    def end_row_index(self) -> int:
        ...
    
    @end_row_index.setter
    def end_row_index(self, value : int):
        ...
    
    ...

class TableDataCell:
    '''The cad linked table cell data'''
    
    @property
    def state_flag(self) -> int:
        ...
    
    @state_flag.setter
    def state_flag(self, value : int):
        ...
    
    @property
    def tooltip(self) -> str:
        '''The cell tooltip'''
        ...
    
    @tooltip.setter
    def tooltip(self, value : str):
        '''The cell tooltip'''
        ...
    
    @property
    def custom_data(self) -> int:
        ...
    
    @custom_data.setter
    def custom_data(self, value : int):
        ...
    
    @property
    def custom_data_collection(self) -> List[aspose.cad.fileformats.cad.cadobjects.acadtable.TableCustomData]:
        ...
    
    @custom_data_collection.setter
    def custom_data_collection(self, value : List[aspose.cad.fileformats.cad.cadobjects.acadtable.TableCustomData]):
        ...
    
    @property
    def has_linked_flags(self) -> int:
        ...
    
    @has_linked_flags.setter
    def has_linked_flags(self, value : int):
        ...
    
    @property
    def row_count(self) -> int:
        ...
    
    @row_count.setter
    def row_count(self, value : int):
        ...
    
    @property
    def column_count(self) -> int:
        ...
    
    @column_count.setter
    def column_count(self, value : int):
        ...
    
    @property
    def unknown_linked_value(self) -> int:
        ...
    
    @unknown_linked_value.setter
    def unknown_linked_value(self, value : int):
        ...
    
    @property
    def cell_contents(self) -> List[aspose.cad.fileformats.cad.cadobjects.acadtable.TableDataCellContent]:
        ...
    
    @cell_contents.setter
    def cell_contents(self, value : List[aspose.cad.fileformats.cad.cadobjects.acadtable.TableDataCellContent]):
        ...
    
    @property
    def cell_style(self) -> aspose.cad.fileformats.cad.cadobjects.tablestyle.CadTableStyleCell:
        ...
    
    @cell_style.setter
    def cell_style(self, value : aspose.cad.fileformats.cad.cadobjects.tablestyle.CadTableStyleCell):
        ...
    
    @property
    def style_id(self) -> int:
        ...
    
    @style_id.setter
    def style_id(self, value : int):
        ...
    
    @property
    def unknown_flag(self) -> int:
        ...
    
    @unknown_flag.setter
    def unknown_flag(self, value : int):
        ...
    
    @property
    def unknown1(self) -> int:
        '''The unknown int value'''
        ...
    
    @unknown1.setter
    def unknown1(self, value : int):
        '''The unknown int value'''
        ...
    
    @property
    def unknown2(self) -> float:
        '''The unknown double value'''
        ...
    
    @unknown2.setter
    def unknown2(self, value : float):
        '''The unknown double value'''
        ...
    
    @property
    def unknown3(self) -> float:
        '''The unknown double value'''
        ...
    
    @unknown3.setter
    def unknown3(self, value : float):
        '''The unknown double value'''
        ...
    
    @property
    def geometry_data_flags(self) -> int:
        ...
    
    @geometry_data_flags.setter
    def geometry_data_flags(self, value : int):
        ...
    
    @property
    def content_geometry(self) -> aspose.cad.fileformats.cad.cadobjects.acadtable.CellContentGeometry:
        ...
    
    @content_geometry.setter
    def content_geometry(self, value : aspose.cad.fileformats.cad.cadobjects.acadtable.CellContentGeometry):
        ...
    
    ...

class TableDataCellContent:
    '''The cad linked table cell content data'''
    
    @property
    def type(self) -> int:
        '''The content type'''
        ...
    
    @type.setter
    def type(self, value : int):
        '''The content type'''
        ...
    
    @property
    def field_value(self) -> aspose.cad.fileformats.cad.cadobjects.field.CadFieldData:
        ...
    
    @field_value.setter
    def field_value(self, value : aspose.cad.fileformats.cad.cadobjects.field.CadFieldData):
        ...
    
    @property
    def has_content(self) -> int:
        ...
    
    @has_content.setter
    def has_content(self, value : int):
        ...
    
    @property
    def property_override_flags2(self) -> int:
        ...
    
    @property_override_flags2.setter
    def property_override_flags2(self, value : int):
        ...
    
    @property
    def property_flags(self) -> int:
        ...
    
    @property_flags.setter
    def property_flags(self, value : int):
        ...
    
    @property
    def value_data_type(self) -> int:
        ...
    
    @value_data_type.setter
    def value_data_type(self, value : int):
        ...
    
    @property
    def value_unit_type(self) -> int:
        ...
    
    @value_unit_type.setter
    def value_unit_type(self, value : int):
        ...
    
    @property
    def value_format_string(self) -> str:
        ...
    
    @value_format_string.setter
    def value_format_string(self, value : str):
        ...
    
    @property
    def rotation(self) -> float:
        '''The Rotation'''
        ...
    
    @rotation.setter
    def rotation(self, value : float):
        '''The Rotation'''
        ...
    
    @property
    def block_scale(self) -> float:
        ...
    
    @block_scale.setter
    def block_scale(self, value : float):
        ...
    
    @property
    def alignment(self) -> int:
        '''The Cell Alignment: Top left = 1, Top center = 2, Top right = 3, Middle left = 4, Middle center = 5,
        Middle right = 6, Bottom left = 7, Bottom center = 8, Bottom right = 9'''
        ...
    
    @alignment.setter
    def alignment(self, value : int):
        '''The Cell Alignment: Top left = 1, Top center = 2, Top right = 3, Middle left = 4, Middle center = 5,
        Middle right = 6, Bottom left = 7, Bottom center = 8, Bottom right = 9'''
        ...
    
    @property
    def content_color(self) -> int:
        ...
    
    @content_color.setter
    def content_color(self, value : int):
        ...
    
    @property
    def text_height(self) -> float:
        ...
    
    @text_height.setter
    def text_height(self, value : float):
        ...
    
    ...

class TableDataColumn:
    '''The cad linked table column data'''
    
    @property
    def column_name(self) -> str:
        ...
    
    @column_name.setter
    def column_name(self, value : str):
        ...
    
    @property
    def custom_data(self) -> int:
        ...
    
    @custom_data.setter
    def custom_data(self, value : int):
        ...
    
    @property
    def custom_data_collection(self) -> List[aspose.cad.fileformats.cad.cadobjects.acadtable.TableCustomData]:
        ...
    
    @custom_data_collection.setter
    def custom_data_collection(self, value : List[aspose.cad.fileformats.cad.cadobjects.acadtable.TableCustomData]):
        ...
    
    @property
    def cell_style(self) -> aspose.cad.fileformats.cad.cadobjects.tablestyle.CadTableStyleCell:
        ...
    
    @cell_style.setter
    def cell_style(self, value : aspose.cad.fileformats.cad.cadobjects.tablestyle.CadTableStyleCell):
        ...
    
    @property
    def style_id(self) -> int:
        ...
    
    @style_id.setter
    def style_id(self, value : int):
        ...
    
    @property
    def width(self) -> float:
        '''The column width'''
        ...
    
    @width.setter
    def width(self, value : float):
        '''The column width'''
        ...
    
    ...

class TableDataRow:
    '''The cad linked table row data'''
    
    @property
    def custom_data(self) -> int:
        ...
    
    @custom_data.setter
    def custom_data(self, value : int):
        ...
    
    @property
    def custom_data_collection(self) -> List[aspose.cad.fileformats.cad.cadobjects.acadtable.TableCustomData]:
        ...
    
    @custom_data_collection.setter
    def custom_data_collection(self, value : List[aspose.cad.fileformats.cad.cadobjects.acadtable.TableCustomData]):
        ...
    
    @property
    def cell_style(self) -> aspose.cad.fileformats.cad.cadobjects.tablestyle.CadTableStyleCell:
        ...
    
    @cell_style.setter
    def cell_style(self, value : aspose.cad.fileformats.cad.cadobjects.tablestyle.CadTableStyleCell):
        ...
    
    @property
    def style_id(self) -> int:
        ...
    
    @style_id.setter
    def style_id(self, value : int):
        ...
    
    @property
    def height(self) -> float:
        '''The row height'''
        ...
    
    @height.setter
    def height(self, value : float):
        '''The row height'''
        ...
    
    @property
    def cells(self) -> List[aspose.cad.fileformats.cad.cadobjects.acadtable.TableDataCell]:
        '''The linked table cells data'''
        ...
    
    @cells.setter
    def cells(self, value : List[aspose.cad.fileformats.cad.cadobjects.acadtable.TableDataCell]):
        '''The linked table cells data'''
        ...
    
    ...

