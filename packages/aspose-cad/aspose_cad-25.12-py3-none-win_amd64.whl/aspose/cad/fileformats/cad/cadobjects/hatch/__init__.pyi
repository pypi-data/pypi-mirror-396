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

class CadBoundaryPathCircularArc(ICadBoundaryPathEntity):
    '''The Cad boundary path circular arc.'''
    
    def to_cad_base_entity(self) -> aspose.cad.fileformats.cad.cadobjects.CadEntityBase:
        '''Converet a boundary path entity to cad base entity.
        
        :returns: Cad base entity'''
        ...
    
    @property
    def center_point(self) -> aspose.cad.primitives.Point2D:
        ...
    
    @center_point.setter
    def center_point(self, value : aspose.cad.primitives.Point2D):
        ...
    
    @property
    def radius(self) -> float:
        '''Gets the radius.'''
        ...
    
    @radius.setter
    def radius(self, value : float):
        '''Sets the radius.'''
        ...
    
    @property
    def start_angle(self) -> float:
        ...
    
    @start_angle.setter
    def start_angle(self, value : float):
        ...
    
    @property
    def end_angle(self) -> float:
        ...
    
    @end_angle.setter
    def end_angle(self, value : float):
        ...
    
    @property
    def counter_clockwize(self) -> int:
        ...
    
    @counter_clockwize.setter
    def counter_clockwize(self, value : int):
        ...
    
    ...

class CadBoundaryPathCircularEllipse(ICadBoundaryPathEntity):
    '''The Cad boundary path circular ellipse.'''
    
    def to_cad_base_entity(self) -> aspose.cad.fileformats.cad.cadobjects.CadEntityBase:
        '''Converet a boundary path entity to cad base entity.
        
        :returns: Cad base entity'''
        ...
    
    @property
    def center_point(self) -> aspose.cad.primitives.Point2D:
        ...
    
    @center_point.setter
    def center_point(self, value : aspose.cad.primitives.Point2D):
        ...
    
    @property
    def major_end_point(self) -> aspose.cad.primitives.Point2D:
        ...
    
    @major_end_point.setter
    def major_end_point(self, value : aspose.cad.primitives.Point2D):
        ...
    
    @property
    def axis_ratio(self) -> float:
        ...
    
    @axis_ratio.setter
    def axis_ratio(self, value : float):
        ...
    
    @property
    def start_angle(self) -> float:
        ...
    
    @start_angle.setter
    def start_angle(self, value : float):
        ...
    
    @property
    def end_angle(self) -> float:
        ...
    
    @end_angle.setter
    def end_angle(self, value : float):
        ...
    
    @property
    def counterclockwise_flag(self) -> int:
        ...
    
    @counterclockwise_flag.setter
    def counterclockwise_flag(self, value : int):
        ...
    
    ...

class CadBoundaryPathLine(ICadBoundaryPathEntity):
    '''The Cad boundary path line.'''
    
    def to_cad_base_entity(self) -> aspose.cad.fileformats.cad.cadobjects.CadEntityBase:
        '''Converet a boundary path entity to cad base entity.
        
        :returns: Cad base entity'''
        ...
    
    @property
    def first_point(self) -> aspose.cad.primitives.Point2D:
        ...
    
    @first_point.setter
    def first_point(self, value : aspose.cad.primitives.Point2D):
        ...
    
    @property
    def second_point(self) -> aspose.cad.primitives.Point2D:
        ...
    
    @second_point.setter
    def second_point(self, value : aspose.cad.primitives.Point2D):
        ...
    
    ...

class CadBoundaryPathSpline(ICadBoundaryPathEntity):
    '''The Cad boundary path spline.'''
    
    def to_cad_base_entity(self) -> aspose.cad.fileformats.cad.cadobjects.CadEntityBase:
        '''Converet a boundary path entity to cad base entity.
        
        :returns: Cad base entity'''
        ...
    
    @property
    def degree(self) -> int:
        '''Gets the degree.'''
        ...
    
    @degree.setter
    def degree(self, value : int):
        '''Sets the degree.'''
        ...
    
    @property
    def rational(self) -> int:
        '''Gets the rational'''
        ...
    
    @rational.setter
    def rational(self, value : int):
        '''Sets the rational'''
        ...
    
    @property
    def periodirc(self) -> int:
        '''Gets the periodic'''
        ...
    
    @periodirc.setter
    def periodirc(self, value : int):
        '''Sets the periodic'''
        ...
    
    @property
    def knots_number(self) -> int:
        ...
    
    @knots_number.setter
    def knots_number(self, value : int):
        ...
    
    @property
    def knot_values(self) -> List[float]:
        ...
    
    @knot_values.setter
    def knot_values(self, value : List[float]):
        ...
    
    @property
    def control_points_number(self) -> int:
        ...
    
    @control_points_number.setter
    def control_points_number(self, value : int):
        ...
    
    @property
    def control_points(self) -> List[aspose.cad.primitives.Point2D]:
        ...
    
    @control_points.setter
    def control_points(self, value : List[aspose.cad.primitives.Point2D]):
        ...
    
    @property
    def weight_params(self) -> List[float]:
        ...
    
    @weight_params.setter
    def weight_params(self, value : List[float]):
        ...
    
    @property
    def fit_points_number(self) -> int:
        ...
    
    @fit_points_number.setter
    def fit_points_number(self, value : int):
        ...
    
    @property
    def fit_points(self) -> List[aspose.cad.primitives.Point2D]:
        ...
    
    @fit_points.setter
    def fit_points(self, value : List[aspose.cad.primitives.Point2D]):
        ...
    
    @property
    def start_tangent(self) -> aspose.cad.primitives.Point2D:
        ...
    
    @start_tangent.setter
    def start_tangent(self, value : aspose.cad.primitives.Point2D):
        ...
    
    @property
    def end_tangent(self) -> aspose.cad.primitives.Point2D:
        ...
    
    @end_tangent.setter
    def end_tangent(self, value : aspose.cad.primitives.Point2D):
        ...
    
    ...

class CadEdgeBoundaryPath(ICadBoundaryPath):
    '''The Cad edge boundary path.'''
    
    @property
    def objects(self) -> List[aspose.cad.fileformats.cad.cadobjects.hatch.ICadBoundaryPathEntity]:
        '''Gets the objects.'''
        ...
    
    @objects.setter
    def objects(self, value : List[aspose.cad.fileformats.cad.cadobjects.hatch.ICadBoundaryPathEntity]):
        '''Sets the objects.'''
        ...
    
    @property
    def number_of_edges(self) -> int:
        ...
    
    @number_of_edges.setter
    def number_of_edges(self, value : int):
        ...
    
    @property
    def edge_types(self) -> List[int]:
        ...
    
    @edge_types.setter
    def edge_types(self, value : List[int]):
        ...
    
    ...

class CadHatch(aspose.cad.fileformats.cad.cadobjects.CadExtrudedEntityBase):
    '''The Cad hatch.'''
    
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
    def reserved_for_future_values(self) -> List[aspose.cad.fileformats.cad.cadobjects.hatch.CadReservedForFutureValues]:
        ...
    
    @reserved_for_future_values.setter
    def reserved_for_future_values(self, value : List[aspose.cad.fileformats.cad.cadobjects.hatch.CadReservedForFutureValues]):
        ...
    
    @property
    def hatch_string(self) -> str:
        ...
    
    @hatch_string.setter
    def hatch_string(self, value : str):
        ...
    
    @property
    def zero_is_reserved(self) -> int:
        ...
    
    @zero_is_reserved.setter
    def zero_is_reserved(self, value : int):
        ...
    
    @property
    def associative_flag(self) -> int:
        ...
    
    @associative_flag.setter
    def associative_flag(self, value : int):
        ...
    
    @property
    def boundary_annotation(self) -> int:
        ...
    
    @boundary_annotation.setter
    def boundary_annotation(self, value : int):
        ...
    
    @property
    def boundary_paths(self) -> List[aspose.cad.fileformats.cad.cadobjects.hatch.CadHatchBoundaryPathContainer]:
        ...
    
    @boundary_paths.setter
    def boundary_paths(self, value : List[aspose.cad.fileformats.cad.cadobjects.hatch.CadHatchBoundaryPathContainer]):
        ...
    
    @property
    def elevation(self) -> float:
        '''Gets the elevation.'''
        ...
    
    @elevation.setter
    def elevation(self, value : float):
        '''Sets the elevation.'''
        ...
    
    @property
    def gradient_color_tint(self) -> float:
        ...
    
    @gradient_color_tint.setter
    def gradient_color_tint(self, value : float):
        ...
    
    @property
    def gradient_colors_type(self) -> int:
        ...
    
    @gradient_colors_type.setter
    def gradient_colors_type(self, value : int):
        ...
    
    @property
    def gradient_definition(self) -> float:
        ...
    
    @gradient_definition.setter
    def gradient_definition(self, value : float):
        ...
    
    @property
    def gradient_rotation_angle(self) -> float:
        ...
    
    @gradient_rotation_angle.setter
    def gradient_rotation_angle(self, value : float):
        ...
    
    @property
    def gradient_type(self) -> int:
        ...
    
    @gradient_type.setter
    def gradient_type(self, value : int):
        ...
    
    @property
    def hatch_angle(self) -> float:
        ...
    
    @hatch_angle.setter
    def hatch_angle(self, value : float):
        ...
    
    @property
    def hatch_pattern_double_flag(self) -> int:
        ...
    
    @hatch_pattern_double_flag.setter
    def hatch_pattern_double_flag(self, value : int):
        ...
    
    @property
    def hatch_pattern_type(self) -> int:
        ...
    
    @hatch_pattern_type.setter
    def hatch_pattern_type(self, value : int):
        ...
    
    @property
    def hatch_scale_or_spacing(self) -> float:
        ...
    
    @hatch_scale_or_spacing.setter
    def hatch_scale_or_spacing(self, value : float):
        ...
    
    @property
    def hatch_style(self) -> int:
        ...
    
    @hatch_style.setter
    def hatch_style(self, value : int):
        ...
    
    @property
    def ignored_boundaries(self) -> int:
        ...
    
    @ignored_boundaries.setter
    def ignored_boundaries(self, value : int):
        ...
    
    @property
    def number_of_boundaries(self) -> int:
        ...
    
    @number_of_boundaries.setter
    def number_of_boundaries(self, value : int):
        ...
    
    @property
    def number_of_pattern_definitions(self) -> int:
        ...
    
    @number_of_pattern_definitions.setter
    def number_of_pattern_definitions(self, value : int):
        ...
    
    @property
    def number_of_seed_points(self) -> int:
        ...
    
    @number_of_seed_points.setter
    def number_of_seed_points(self, value : int):
        ...
    
    @property
    def offset_vector(self) -> float:
        ...
    
    @offset_vector.setter
    def offset_vector(self, value : float):
        ...
    
    @property
    def pattern_fill_color(self) -> int:
        ...
    
    @pattern_fill_color.setter
    def pattern_fill_color(self, value : int):
        ...
    
    @property
    def pattern_name(self) -> str:
        ...
    
    @pattern_name.setter
    def pattern_name(self, value : str):
        ...
    
    @property
    def pixel_size(self) -> float:
        ...
    
    @pixel_size.setter
    def pixel_size(self, value : float):
        ...
    
    @property
    def seed_points(self) -> List[aspose.cad.fileformats.cad.cadobjects.Cad2DPoint]:
        ...
    
    @seed_points.setter
    def seed_points(self, value : List[aspose.cad.fileformats.cad.cadobjects.Cad2DPoint]):
        ...
    
    @property
    def fit_points(self) -> List[aspose.cad.fileformats.cad.cadobjects.Cad2DPoint]:
        ...
    
    @fit_points.setter
    def fit_points(self, value : List[aspose.cad.fileformats.cad.cadobjects.Cad2DPoint]):
        ...
    
    @property
    def start_tangent(self) -> aspose.cad.fileformats.cad.cadobjects.Cad2DPoint:
        ...
    
    @start_tangent.setter
    def start_tangent(self, value : aspose.cad.fileformats.cad.cadobjects.Cad2DPoint):
        ...
    
    @property
    def end_tangent(self) -> aspose.cad.fileformats.cad.cadobjects.Cad2DPoint:
        ...
    
    @end_tangent.setter
    def end_tangent(self, value : aspose.cad.fileformats.cad.cadobjects.Cad2DPoint):
        ...
    
    @property
    def solid_fill_flag(self) -> int:
        ...
    
    @solid_fill_flag.setter
    def solid_fill_flag(self, value : int):
        ...
    
    @property
    def solid_or_gradient(self) -> int:
        ...
    
    @solid_or_gradient.setter
    def solid_or_gradient(self, value : int):
        ...
    
    @property
    def pattern_definitions(self) -> List[aspose.cad.fileformats.cad.cadobjects.hatch.CadHatchPatternData]:
        ...
    
    @pattern_definitions.setter
    def pattern_definitions(self, value : List[aspose.cad.fileformats.cad.cadobjects.hatch.CadHatchPatternData]):
        ...
    
    ...

class CadHatchBoundaryPathContainer:
    '''Boundary for hatch'''
    
    @property
    def boundary_path(self) -> List[aspose.cad.fileformats.cad.cadobjects.hatch.ICadBoundaryPath]:
        ...
    
    @boundary_path.setter
    def boundary_path(self, value : List[aspose.cad.fileformats.cad.cadobjects.hatch.ICadBoundaryPath]):
        ...
    
    @property
    def boundary_object_count(self) -> int:
        ...
    
    @boundary_object_count.setter
    def boundary_object_count(self, value : int):
        ...
    
    @property
    def source_boundary_objects(self) -> List[str]:
        ...
    
    @source_boundary_objects.setter
    def source_boundary_objects(self, value : List[str]):
        ...
    
    @property
    def path_type(self) -> int:
        ...
    
    @path_type.setter
    def path_type(self, value : int):
        ...
    
    ...

class CadHatchPatternData:
    '''Cad hatch pattern class'''
    
    @property
    def dash_length_count(self) -> int:
        ...
    
    @dash_length_count.setter
    def dash_length_count(self, value : int):
        ...
    
    @property
    def dash_lengths(self) -> List[float]:
        ...
    
    @dash_lengths.setter
    def dash_lengths(self, value : List[float]):
        ...
    
    @property
    def line_angle(self) -> float:
        ...
    
    @line_angle.setter
    def line_angle(self, value : float):
        ...
    
    @property
    def line_base_point(self) -> aspose.cad.fileformats.cad.cadobjects.Cad2DPoint:
        ...
    
    @line_base_point.setter
    def line_base_point(self, value : aspose.cad.fileformats.cad.cadobjects.Cad2DPoint):
        ...
    
    @property
    def line_offset(self) -> aspose.cad.fileformats.cad.cadobjects.Cad2DPoint:
        ...
    
    @line_offset.setter
    def line_offset(self, value : aspose.cad.fileformats.cad.cadobjects.Cad2DPoint):
        ...
    
    ...

class CadPolylineBoundaryPath(ICadBoundaryPath):
    '''The Cad polyline boundary path.'''
    
    @property
    def has_bugle(self) -> bool:
        ...
    
    @has_bugle.setter
    def has_bugle(self, value : bool):
        ...
    
    @property
    def is_closed(self) -> bool:
        ...
    
    @is_closed.setter
    def is_closed(self, value : bool):
        ...
    
    @property
    def max_array_len(self) -> int:
        ...
    
    @max_array_len.setter
    def max_array_len(self, value : int):
        ...
    
    @property
    def vertices(self) -> List[aspose.cad.primitives.Point2D]:
        '''Gets list of vertices.'''
        ...
    
    @vertices.setter
    def vertices(self, value : List[aspose.cad.primitives.Point2D]):
        '''Gets list of vertices.'''
        ...
    
    @property
    def bugles(self) -> List[float]:
        '''Gets list of bugles.'''
        ...
    
    @bugles.setter
    def bugles(self, value : List[float]):
        '''Gets list of bugles.'''
        ...
    
    ...

class CadReservedForFutureValues:
    '''The reserved for future values'''
    
    @property
    def attribute463(self) -> Optional[float]:
        '''Gets the attribute 463.'''
        ...
    
    @attribute463.setter
    def attribute463(self, value : Optional[float]):
        '''Sets the attribute 463.'''
        ...
    
    @property
    def attribute63(self) -> Optional[int]:
        '''Gets the attribute63.'''
        ...
    
    @attribute63.setter
    def attribute63(self, value : Optional[int]):
        '''Sets the attribute63.'''
        ...
    
    @property
    def attribute421(self) -> Optional[int]:
        '''Gets the attribute421.'''
        ...
    
    @attribute421.setter
    def attribute421(self, value : Optional[int]):
        '''Sets the attribute421.'''
        ...
    
    ...

class ICadBoundaryPath:
    '''The Cad  boundary path.'''
    
    ...

class ICadBoundaryPathEntity:
    '''The Cad boundary path entity interface.'''
    
    def to_cad_base_entity(self) -> aspose.cad.fileformats.cad.cadobjects.CadEntityBase:
        '''Converet a boundary path entity to cad base entity.
        
        :returns: Cad base entity'''
        ...
    
    ...

