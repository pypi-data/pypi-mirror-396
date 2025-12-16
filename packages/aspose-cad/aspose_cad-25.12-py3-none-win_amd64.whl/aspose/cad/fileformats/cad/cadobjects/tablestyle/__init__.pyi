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

class CadTableStyle(aspose.cad.fileformats.cad.cadobjects.CadBaseObject):
    '''Class describing CadTableStyle'''
    
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
    def table_style_cell_list(self) -> List[aspose.cad.fileformats.cad.cadobjects.tablestyle.CadTableStyleCell]:
        ...
    
    @table_style_cell_list.setter
    def table_style_cell_list(self, value : List[aspose.cad.fileformats.cad.cadobjects.tablestyle.CadTableStyleCell]):
        ...
    
    @property
    def version_number(self) -> int:
        ...
    
    @version_number.setter
    def version_number(self, value : int):
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
    def flow_direction(self) -> int:
        ...
    
    @flow_direction.setter
    def flow_direction(self, value : int):
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
    def horizontal_cell_margin(self) -> Optional[float]:
        ...
    
    @horizontal_cell_margin.setter
    def horizontal_cell_margin(self, value : Optional[float]):
        ...
    
    @property
    def vertical_cell_margin(self) -> Optional[float]:
        ...
    
    @vertical_cell_margin.setter
    def vertical_cell_margin(self, value : Optional[float]):
        ...
    
    @property
    def flag_for_whether_title_is_suppressed(self) -> int:
        ...
    
    @flag_for_whether_title_is_suppressed.setter
    def flag_for_whether_title_is_suppressed(self, value : int):
        ...
    
    @property
    def flag_for_whether_column_heading_is_suppressed(self) -> int:
        ...
    
    @flag_for_whether_column_heading_is_suppressed.setter
    def flag_for_whether_column_heading_is_suppressed(self, value : int):
        ...
    
    @property
    def unknown1(self) -> byte:
        '''The Unknown1 parameter'''
        ...
    
    @unknown1.setter
    def unknown1(self, value : byte):
        '''The Unknown1 parameter'''
        ...
    
    @property
    def unknown2(self) -> int:
        '''The Unknown2 parameter'''
        ...
    
    @unknown2.setter
    def unknown2(self, value : int):
        '''The Unknown2 parameter'''
        ...
    
    @property
    def unknown3(self) -> int:
        '''The Unknown3 parameter'''
        ...
    
    @unknown3.setter
    def unknown3(self, value : int):
        '''The Unknown3 parameter'''
        ...
    
    @property
    def unknown_hard_owner(self) -> str:
        ...
    
    @unknown_hard_owner.setter
    def unknown_hard_owner(self, value : str):
        ...
    
    @property
    def table_style_content(self) -> aspose.cad.fileformats.cad.cadobjects.tablestyle.TableStyleCellContent:
        ...
    
    @table_style_content.setter
    def table_style_content(self, value : aspose.cad.fileformats.cad.cadobjects.tablestyle.TableStyleCellContent):
        ...
    
    ...

class CadTableStyleCell:
    '''The TableStyleCell data'''
    
    @property
    def attribute1(self) -> str:
        '''Gets the attribute1.'''
        ...
    
    @attribute1.setter
    def attribute1(self, value : str):
        '''Sets the attribute1.'''
        ...
    
    @property
    def text_style_name(self) -> str:
        ...
    
    @text_style_name.setter
    def text_style_name(self, value : str):
        ...
    
    @property
    def text_height(self) -> float:
        ...
    
    @text_height.setter
    def text_height(self, value : float):
        ...
    
    @property
    def cell_alignment(self) -> int:
        ...
    
    @cell_alignment.setter
    def cell_alignment(self, value : int):
        ...
    
    @property
    def text_color(self) -> Optional[int]:
        ...
    
    @text_color.setter
    def text_color(self, value : Optional[int]):
        ...
    
    @property
    def cell_fill_color(self) -> Optional[int]:
        ...
    
    @cell_fill_color.setter
    def cell_fill_color(self, value : Optional[int]):
        ...
    
    @property
    def flag_for_whether_background_color_is_enabled(self) -> Optional[int]:
        ...
    
    @flag_for_whether_background_color_is_enabled.setter
    def flag_for_whether_background_color_is_enabled(self, value : Optional[int]):
        ...
    
    @property
    def cell_data_type(self) -> int:
        ...
    
    @cell_data_type.setter
    def cell_data_type(self, value : int):
        ...
    
    @property
    def cell_unit_type(self) -> int:
        ...
    
    @cell_unit_type.setter
    def cell_unit_type(self, value : int):
        ...
    
    @property
    def line_weight1(self) -> Optional[int]:
        ...
    
    @line_weight1.setter
    def line_weight1(self, value : Optional[int]):
        ...
    
    @property
    def visibility_flag1(self) -> Optional[int]:
        ...
    
    @visibility_flag1.setter
    def visibility_flag1(self, value : Optional[int]):
        ...
    
    @property
    def color_value1(self) -> Optional[int]:
        ...
    
    @color_value1.setter
    def color_value1(self, value : Optional[int]):
        ...
    
    @property
    def line_weight2(self) -> Optional[int]:
        ...
    
    @line_weight2.setter
    def line_weight2(self, value : Optional[int]):
        ...
    
    @property
    def visibility_flag2(self) -> Optional[int]:
        ...
    
    @visibility_flag2.setter
    def visibility_flag2(self, value : Optional[int]):
        ...
    
    @property
    def color_value2(self) -> Optional[int]:
        ...
    
    @color_value2.setter
    def color_value2(self, value : Optional[int]):
        ...
    
    @property
    def line_weight3(self) -> Optional[int]:
        ...
    
    @line_weight3.setter
    def line_weight3(self, value : Optional[int]):
        ...
    
    @property
    def visibility_flag3(self) -> Optional[int]:
        ...
    
    @visibility_flag3.setter
    def visibility_flag3(self, value : Optional[int]):
        ...
    
    @property
    def color_value3(self) -> Optional[int]:
        ...
    
    @color_value3.setter
    def color_value3(self, value : Optional[int]):
        ...
    
    @property
    def line_weight4(self) -> Optional[int]:
        ...
    
    @line_weight4.setter
    def line_weight4(self, value : Optional[int]):
        ...
    
    @property
    def visibility_flag4(self) -> Optional[int]:
        ...
    
    @visibility_flag4.setter
    def visibility_flag4(self, value : Optional[int]):
        ...
    
    @property
    def color_value4(self) -> Optional[int]:
        ...
    
    @color_value4.setter
    def color_value4(self, value : Optional[int]):
        ...
    
    @property
    def line_weight5(self) -> Optional[int]:
        ...
    
    @line_weight5.setter
    def line_weight5(self, value : Optional[int]):
        ...
    
    @property
    def visibility_flag5(self) -> Optional[int]:
        ...
    
    @visibility_flag5.setter
    def visibility_flag5(self, value : Optional[int]):
        ...
    
    @property
    def color_value5(self) -> Optional[int]:
        ...
    
    @color_value5.setter
    def color_value5(self, value : Optional[int]):
        ...
    
    @property
    def line_weight6(self) -> Optional[int]:
        ...
    
    @line_weight6.setter
    def line_weight6(self, value : Optional[int]):
        ...
    
    @property
    def visibility_flag6(self) -> Optional[int]:
        ...
    
    @visibility_flag6.setter
    def visibility_flag6(self, value : Optional[int]):
        ...
    
    @property
    def color_value6(self) -> Optional[int]:
        ...
    
    @color_value6.setter
    def color_value6(self, value : Optional[int]):
        ...
    
    @property
    def cell_content(self) -> aspose.cad.fileformats.cad.cadobjects.tablestyle.TableStyleCellContent:
        ...
    
    @cell_content.setter
    def cell_content(self, value : aspose.cad.fileformats.cad.cadobjects.tablestyle.TableStyleCellContent):
        ...
    
    ...

class TableStyleCellBorder:
    '''The TableStyleCellBorder data'''
    
    @property
    def edge_flag(self) -> aspose.cad.fileformats.cad.cadobjects.tablestyle.CellBorderEdgeType:
        ...
    
    @edge_flag.setter
    def edge_flag(self, value : aspose.cad.fileformats.cad.cadobjects.tablestyle.CellBorderEdgeType):
        ...
    
    @property
    def overrides(self) -> int:
        '''The Border property override flags'''
        ...
    
    @overrides.setter
    def overrides(self, value : int):
        '''The Border property override flags'''
        ...
    
    @property
    def type(self) -> int:
        '''The Border Type'''
        ...
    
    @type.setter
    def type(self, value : int):
        '''The Border Type'''
        ...
    
    @property
    def color(self) -> int:
        '''The Color'''
        ...
    
    @color.setter
    def color(self, value : int):
        '''The Color'''
        ...
    
    @property
    def line_weight(self) -> int:
        ...
    
    @line_weight.setter
    def line_weight(self, value : int):
        ...
    
    @property
    def invisibility(self) -> int:
        '''The Invisibility: 1 = invisible, 0 = visible'''
        ...
    
    @invisibility.setter
    def invisibility(self, value : int):
        '''The Invisibility: 1 = invisible, 0 = visible'''
        ...
    
    @property
    def line_spacing(self) -> float:
        ...
    
    @line_spacing.setter
    def line_spacing(self, value : float):
        ...
    
    @property
    def line_type_handle(self) -> str:
        ...
    
    @line_type_handle.setter
    def line_type_handle(self, value : str):
        ...
    
    ...

class TableStyleCellContent:
    '''The TableStyleCellContent data'''
    
    @property
    def cell_style_type(self) -> int:
        ...
    
    @cell_style_type.setter
    def cell_style_type(self, value : int):
        ...
    
    @property
    def unknown1(self) -> int:
        '''The Unknown1 parameter'''
        ...
    
    @unknown1.setter
    def unknown1(self, value : int):
        '''The Unknown1 parameter'''
        ...
    
    @property
    def data_flags(self) -> int:
        ...
    
    @data_flags.setter
    def data_flags(self, value : int):
        ...
    
    @property
    def merge_flags(self) -> int:
        ...
    
    @merge_flags.setter
    def merge_flags(self, value : int):
        ...
    
    @property
    def background_color(self) -> int:
        ...
    
    @background_color.setter
    def background_color(self, value : int):
        ...
    
    @property
    def content_layout_flags(self) -> int:
        ...
    
    @content_layout_flags.setter
    def content_layout_flags(self, value : int):
        ...
    
    @property
    def property_override_flags1(self) -> int:
        ...
    
    @property_override_flags1.setter
    def property_override_flags1(self, value : int):
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
    def cell_alignment(self) -> int:
        ...
    
    @cell_alignment.setter
    def cell_alignment(self, value : int):
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
    
    @property
    def margin_flag(self) -> int:
        ...
    
    @margin_flag.setter
    def margin_flag(self, value : int):
        ...
    
    @property
    def vertical_margin(self) -> float:
        ...
    
    @vertical_margin.setter
    def vertical_margin(self, value : float):
        ...
    
    @property
    def horizontal_margin(self) -> float:
        ...
    
    @horizontal_margin.setter
    def horizontal_margin(self, value : float):
        ...
    
    @property
    def bottom_margin(self) -> float:
        ...
    
    @bottom_margin.setter
    def bottom_margin(self, value : float):
        ...
    
    @property
    def right_margin(self) -> float:
        ...
    
    @right_margin.setter
    def right_margin(self, value : float):
        ...
    
    @property
    def margin_horizontal_spacing(self) -> float:
        ...
    
    @margin_horizontal_spacing.setter
    def margin_horizontal_spacing(self, value : float):
        ...
    
    @property
    def margin_vertical_spacing(self) -> float:
        ...
    
    @margin_vertical_spacing.setter
    def margin_vertical_spacing(self, value : float):
        ...
    
    @property
    def cell_style_id(self) -> int:
        ...
    
    @cell_style_id.setter
    def cell_style_id(self, value : int):
        ...
    
    @property
    def cell_style_class(self) -> int:
        ...
    
    @cell_style_class.setter
    def cell_style_class(self, value : int):
        ...
    
    @property
    def cell_style_name(self) -> str:
        ...
    
    @cell_style_name.setter
    def cell_style_name(self, value : str):
        ...
    
    @property
    def text_style_handle(self) -> str:
        ...
    
    @text_style_handle.setter
    def text_style_handle(self, value : str):
        ...
    
    @property
    def cell_borders(self) -> List[aspose.cad.fileformats.cad.cadobjects.tablestyle.TableStyleCellBorder]:
        ...
    
    @cell_borders.setter
    def cell_borders(self, value : List[aspose.cad.fileformats.cad.cadobjects.tablestyle.TableStyleCellBorder]):
        ...
    
    ...

class CellBorderEdgeType:
    '''The cell border edge type'''
    
    @classmethod
    @property
    def TOP(cls) -> CellBorderEdgeType:
        ...
    
    @classmethod
    @property
    def RIGHT(cls) -> CellBorderEdgeType:
        ...
    
    @classmethod
    @property
    def BOTTOM(cls) -> CellBorderEdgeType:
        ...
    
    @classmethod
    @property
    def LEFT(cls) -> CellBorderEdgeType:
        ...
    
    @classmethod
    @property
    def INSIDE_VERTICAL(cls) -> CellBorderEdgeType:
        ...
    
    @classmethod
    @property
    def INSIDE_HORIZONTAL(cls) -> CellBorderEdgeType:
        ...
    
    ...

