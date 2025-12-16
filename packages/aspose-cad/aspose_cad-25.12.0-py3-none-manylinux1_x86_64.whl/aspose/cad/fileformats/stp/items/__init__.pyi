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

class StepAdavncedBrepShapeRepresentation(StepShapeRepresentation):
    '''An extended representation of the brep form.'''
    
    @property
    def item_type(self) -> aspose.cad.fileformats.stp.items.StepItemType:
        ...
    
    @property
    def name(self) -> str:
        ...
    
    @name.setter
    def name(self, value : str):
        ...
    
    @property
    def u_id(self) -> int:
        ...
    
    @u_id.setter
    def u_id(self, value : int):
        ...
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
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
    def shape_items(self) -> List[aspose.cad.fileformats.stp.items.StepRepresentationItem]:
        ...
    
    @shape_items.setter
    def shape_items(self, value : List[aspose.cad.fileformats.stp.items.StepRepresentationItem]):
        ...
    
    @property
    def representation_context(self) -> aspose.cad.fileformats.stp.items.StepRepresentationItem:
        ...
    
    ...

class StepAdvancedFace(StepFaceSurface):
    '''AdvancedFace class for STP file.'''
    
    @property
    def item_type(self) -> aspose.cad.fileformats.stp.items.StepItemType:
        ...
    
    @property
    def name(self) -> str:
        ...
    
    @name.setter
    def name(self, value : str):
        ...
    
    @property
    def u_id(self) -> int:
        ...
    
    @u_id.setter
    def u_id(self, value : int):
        ...
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
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
    def bounds(self) -> List[aspose.cad.fileformats.stp.items.StepFaceBound]:
        ...
    
    @bounds.setter
    def bounds(self, value : List[aspose.cad.fileformats.stp.items.StepFaceBound]):
        ...
    
    @property
    def face_geometry(self) -> aspose.cad.fileformats.stp.items.StepSurface:
        ...
    
    @face_geometry.setter
    def face_geometry(self, value : aspose.cad.fileformats.stp.items.StepSurface):
        ...
    
    @property
    def same_sense(self) -> bool:
        ...
    
    @same_sense.setter
    def same_sense(self, value : bool):
        ...
    
    @property
    def plane(self) -> aspose.cad.fileformats.stp.items.StepRepresentationItem:
        ...
    
    @plane.setter
    def plane(self, value : aspose.cad.fileformats.stp.items.StepRepresentationItem):
        ...
    
    ...

class StepAxis2Placement(StepPlacement):
    '''Axis2Placement class for STP file.'''
    
    @property
    def item_type(self) -> aspose.cad.fileformats.stp.items.StepItemType:
        ...
    
    @property
    def name(self) -> str:
        ...
    
    @name.setter
    def name(self, value : str):
        ...
    
    @property
    def u_id(self) -> int:
        ...
    
    @u_id.setter
    def u_id(self, value : int):
        ...
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
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
    def location(self) -> aspose.cad.fileformats.stp.items.StepCartesianPoint:
        '''The location attribute defines the spatial position of the reference
        point and origin of the associated placement coordinate system.'''
        ...
    
    @location.setter
    def location(self, value : aspose.cad.fileformats.stp.items.StepCartesianPoint):
        '''The location attribute defines the spatial position of the reference
        point and origin of the associated placement coordinate system.'''
        ...
    
    @property
    def ref_direction(self) -> aspose.cad.fileformats.stp.items.StepDirection:
        ...
    
    @ref_direction.setter
    def ref_direction(self, value : aspose.cad.fileformats.stp.items.StepDirection):
        ...
    
    ...

class StepAxis2Placement2D(StepAxis2Placement):
    '''Axis2Placement2D class for STP file.'''
    
    @property
    def item_type(self) -> aspose.cad.fileformats.stp.items.StepItemType:
        ...
    
    @property
    def name(self) -> str:
        ...
    
    @name.setter
    def name(self, value : str):
        ...
    
    @property
    def u_id(self) -> int:
        ...
    
    @u_id.setter
    def u_id(self, value : int):
        ...
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
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
    def location(self) -> aspose.cad.fileformats.stp.items.StepCartesianPoint:
        '''The location attribute defines the spatial position of the reference
        point and origin of the associated placement coordinate system.'''
        ...
    
    @location.setter
    def location(self, value : aspose.cad.fileformats.stp.items.StepCartesianPoint):
        '''The location attribute defines the spatial position of the reference
        point and origin of the associated placement coordinate system.'''
        ...
    
    @property
    def ref_direction(self) -> aspose.cad.fileformats.stp.items.StepDirection:
        ...
    
    @ref_direction.setter
    def ref_direction(self, value : aspose.cad.fileformats.stp.items.StepDirection):
        ...
    
    ...

class StepAxis2Placement3D(StepAxis2Placement):
    '''Axis2Placement3D class for STP file.'''
    
    @property
    def item_type(self) -> aspose.cad.fileformats.stp.items.StepItemType:
        ...
    
    @property
    def name(self) -> str:
        ...
    
    @name.setter
    def name(self, value : str):
        ...
    
    @property
    def u_id(self) -> int:
        ...
    
    @u_id.setter
    def u_id(self, value : int):
        ...
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
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
    def location(self) -> aspose.cad.fileformats.stp.items.StepCartesianPoint:
        '''The location attribute defines the spatial position of the reference
        point and origin of the associated placement coordinate system.'''
        ...
    
    @location.setter
    def location(self, value : aspose.cad.fileformats.stp.items.StepCartesianPoint):
        '''The location attribute defines the spatial position of the reference
        point and origin of the associated placement coordinate system.'''
        ...
    
    @property
    def ref_direction(self) -> aspose.cad.fileformats.stp.items.StepDirection:
        ...
    
    @ref_direction.setter
    def ref_direction(self, value : aspose.cad.fileformats.stp.items.StepDirection):
        ...
    
    @property
    def axis(self) -> aspose.cad.fileformats.stp.items.StepDirection:
        '''The axis attribute defines the exact direction of the local Z axis.'''
        ...
    
    @axis.setter
    def axis(self, value : aspose.cad.fileformats.stp.items.StepDirection):
        '''The axis attribute defines the exact direction of the local Z axis.'''
        ...
    
    ...

class StepBSplineCurve(StepBoundedCurve):
    '''BSplineCurve class for STP file.'''
    
    @property
    def item_type(self) -> aspose.cad.fileformats.stp.items.StepItemType:
        ...
    
    @property
    def name(self) -> str:
        ...
    
    @name.setter
    def name(self, value : str):
        ...
    
    @property
    def u_id(self) -> int:
        ...
    
    @u_id.setter
    def u_id(self, value : int):
        ...
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
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
    def degree(self) -> int:
        ...
    
    @degree.setter
    def degree(self, value : int):
        ...
    
    @property
    def control_points_list(self) -> List[aspose.cad.fileformats.stp.items.StepCartesianPoint]:
        ...
    
    @property
    def curve_form(self) -> aspose.cad.fileformats.stp.items.StepBSplineCurveForm:
        ...
    
    @curve_form.setter
    def curve_form(self, value : aspose.cad.fileformats.stp.items.StepBSplineCurveForm):
        ...
    
    @property
    def closed_curve(self) -> bool:
        ...
    
    @closed_curve.setter
    def closed_curve(self, value : bool):
        ...
    
    @property
    def self_intersect(self) -> bool:
        ...
    
    @self_intersect.setter
    def self_intersect(self, value : bool):
        ...
    
    ...

class StepBSplineCurveWithKnots(StepBSplineCurve):
    '''BSplineCurveWithKnots class for STP file.'''
    
    @property
    def item_type(self) -> aspose.cad.fileformats.stp.items.StepItemType:
        ...
    
    @property
    def name(self) -> str:
        ...
    
    @name.setter
    def name(self, value : str):
        ...
    
    @property
    def u_id(self) -> int:
        ...
    
    @u_id.setter
    def u_id(self, value : int):
        ...
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
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
    def degree(self) -> int:
        ...
    
    @degree.setter
    def degree(self, value : int):
        ...
    
    @property
    def control_points_list(self) -> List[aspose.cad.fileformats.stp.items.StepCartesianPoint]:
        ...
    
    @property
    def curve_form(self) -> aspose.cad.fileformats.stp.items.StepBSplineCurveForm:
        ...
    
    @curve_form.setter
    def curve_form(self, value : aspose.cad.fileformats.stp.items.StepBSplineCurveForm):
        ...
    
    @property
    def closed_curve(self) -> bool:
        ...
    
    @closed_curve.setter
    def closed_curve(self, value : bool):
        ...
    
    @property
    def self_intersect(self) -> bool:
        ...
    
    @self_intersect.setter
    def self_intersect(self, value : bool):
        ...
    
    @property
    def knot_multiplicities(self) -> List[int]:
        ...
    
    @property
    def knots(self) -> List[float]:
        ...
    
    @property
    def knot_spec(self) -> aspose.cad.fileformats.stp.items.StepKnotType:
        ...
    
    @knot_spec.setter
    def knot_spec(self, value : aspose.cad.fileformats.stp.items.StepKnotType):
        ...
    
    ...

class StepBSplineSurface(StepSurface):
    '''BsplineSurface class for STP file.'''
    
    @property
    def item_type(self) -> aspose.cad.fileformats.stp.items.StepItemType:
        ...
    
    @property
    def name(self) -> str:
        ...
    
    @name.setter
    def name(self, value : str):
        ...
    
    @property
    def u_id(self) -> int:
        ...
    
    @u_id.setter
    def u_id(self, value : int):
        ...
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
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
    def u_degree(self) -> int:
        ...
    
    @u_degree.setter
    def u_degree(self, value : int):
        ...
    
    @property
    def v_degree(self) -> int:
        ...
    
    @v_degree.setter
    def v_degree(self, value : int):
        ...
    
    @property
    def control_points_list(self) -> List[List[aspose.cad.fileformats.stp.items.StepCartesianPoint]]:
        ...
    
    @control_points_list.setter
    def control_points_list(self, value : List[List[aspose.cad.fileformats.stp.items.StepCartesianPoint]]):
        ...
    
    @property
    def surface_form(self) -> aspose.cad.fileformats.stp.items.StepBSplineSurfaceForm:
        ...
    
    @surface_form.setter
    def surface_form(self, value : aspose.cad.fileformats.stp.items.StepBSplineSurfaceForm):
        ...
    
    @property
    def u_closed(self) -> bool:
        ...
    
    @u_closed.setter
    def u_closed(self, value : bool):
        ...
    
    @property
    def v_closed(self) -> bool:
        ...
    
    @v_closed.setter
    def v_closed(self, value : bool):
        ...
    
    @property
    def self_intersect(self) -> bool:
        ...
    
    @self_intersect.setter
    def self_intersect(self, value : bool):
        ...
    
    ...

class StepBSplineSurfaceFormUtils:
    '''Class with utility methods for BSplineSurfaceForm enum.'''
    
    @staticmethod
    def get_b_spline_surface_form(form : aspose.cad.fileformats.stp.items.StepBSplineSurfaceForm) -> str:
        ...
    
    @staticmethod
    def parse_b_spline_surface_form(value : str) -> aspose.cad.fileformats.stp.items.StepBSplineSurfaceForm:
        ...
    
    ...

class StepBSplineSurfaceWithKnots(StepBSplineSurface):
    '''BSplineSurfaceWithKnots class for STP file.'''
    
    @property
    def item_type(self) -> aspose.cad.fileformats.stp.items.StepItemType:
        ...
    
    @property
    def name(self) -> str:
        ...
    
    @name.setter
    def name(self, value : str):
        ...
    
    @property
    def u_id(self) -> int:
        ...
    
    @u_id.setter
    def u_id(self, value : int):
        ...
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
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
    def u_degree(self) -> int:
        ...
    
    @u_degree.setter
    def u_degree(self, value : int):
        ...
    
    @property
    def v_degree(self) -> int:
        ...
    
    @v_degree.setter
    def v_degree(self, value : int):
        ...
    
    @property
    def control_points_list(self) -> List[List[aspose.cad.fileformats.stp.items.StepCartesianPoint]]:
        ...
    
    @control_points_list.setter
    def control_points_list(self, value : List[List[aspose.cad.fileformats.stp.items.StepCartesianPoint]]):
        ...
    
    @property
    def surface_form(self) -> aspose.cad.fileformats.stp.items.StepBSplineSurfaceForm:
        ...
    
    @surface_form.setter
    def surface_form(self, value : aspose.cad.fileformats.stp.items.StepBSplineSurfaceForm):
        ...
    
    @property
    def u_closed(self) -> bool:
        ...
    
    @u_closed.setter
    def u_closed(self, value : bool):
        ...
    
    @property
    def v_closed(self) -> bool:
        ...
    
    @v_closed.setter
    def v_closed(self, value : bool):
        ...
    
    @property
    def self_intersect(self) -> bool:
        ...
    
    @self_intersect.setter
    def self_intersect(self, value : bool):
        ...
    
    @property
    def step_b_spline_surface(self) -> aspose.cad.fileformats.stp.items.StepBSplineSurface:
        ...
    
    @property
    def u_multiplicities(self) -> List[int]:
        ...
    
    @property
    def v_multiplicities(self) -> List[int]:
        ...
    
    @property
    def u_knots(self) -> List[float]:
        ...
    
    @property
    def v_knots(self) -> List[float]:
        ...
    
    @property
    def knot_spec(self) -> aspose.cad.fileformats.stp.items.StepKnotType:
        ...
    
    @knot_spec.setter
    def knot_spec(self, value : aspose.cad.fileformats.stp.items.StepKnotType):
        ...
    
    ...

class StepBoundedCurve(StepCurve):
    '''BoundedCurve class for STP file.'''
    
    @property
    def item_type(self) -> aspose.cad.fileformats.stp.items.StepItemType:
        ...
    
    @property
    def name(self) -> str:
        ...
    
    @name.setter
    def name(self, value : str):
        ...
    
    @property
    def u_id(self) -> int:
        ...
    
    @u_id.setter
    def u_id(self, value : int):
        ...
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
        ...
    
    @property
    def area(self) -> float:
        '''Gets the area of the entity.'''
        ...
    
    @property
    def length(self) -> float:
        '''Gets the length of the entity.'''
        ...
    
    ...

class StepBoundedSurface(StepSurface):
    '''BoundedSurface class for STP file.'''
    
    @property
    def item_type(self) -> aspose.cad.fileformats.stp.items.StepItemType:
        ...
    
    @property
    def name(self) -> str:
        ...
    
    @name.setter
    def name(self, value : str):
        ...
    
    @property
    def u_id(self) -> int:
        ...
    
    @u_id.setter
    def u_id(self, value : int):
        ...
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
        ...
    
    @property
    def area(self) -> float:
        '''Gets the area of the entity.'''
        ...
    
    @property
    def length(self) -> float:
        '''Gets the length of the entity.'''
        ...
    
    ...

class StepCartesianPoint(StepTriple):
    '''CartesianPoint class for STP file.'''
    
    def equals(self, other : aspose.cad.fileformats.stp.items.StepTriple) -> bool:
        ...
    
    @property
    def item_type(self) -> aspose.cad.fileformats.stp.items.StepItemType:
        ...
    
    @property
    def name(self) -> str:
        ...
    
    @name.setter
    def name(self, value : str):
        ...
    
    @property
    def u_id(self) -> int:
        ...
    
    @u_id.setter
    def u_id(self, value : int):
        ...
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
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
    def x(self) -> float:
        ...
    
    @x.setter
    def x(self, value : float):
        ...
    
    @property
    def y(self) -> float:
        ...
    
    @y.setter
    def y(self, value : float):
        ...
    
    @property
    def z(self) -> float:
        ...
    
    @z.setter
    def z(self, value : float):
        ...
    
    ...

class StepCircle(StepConic):
    '''Circle class for STP file.'''
    
    @property
    def item_type(self) -> aspose.cad.fileformats.stp.items.StepItemType:
        ...
    
    @property
    def name(self) -> str:
        ...
    
    @name.setter
    def name(self, value : str):
        ...
    
    @property
    def u_id(self) -> int:
        ...
    
    @u_id.setter
    def u_id(self, value : int):
        ...
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
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
    def position(self) -> aspose.cad.fileformats.stp.items.StepAxis2Placement:
        ...
    
    @position.setter
    def position(self, value : aspose.cad.fileformats.stp.items.StepAxis2Placement):
        ...
    
    @property
    def radius(self) -> float:
        ...
    
    @radius.setter
    def radius(self, value : float):
        ...
    
    ...

class StepClosedShell(StepConnectedFaceSet):
    '''ClosedShell class for STP file.'''
    
    @property
    def item_type(self) -> aspose.cad.fileformats.stp.items.StepItemType:
        ...
    
    @property
    def name(self) -> str:
        ...
    
    @name.setter
    def name(self, value : str):
        ...
    
    @property
    def u_id(self) -> int:
        ...
    
    @u_id.setter
    def u_id(self, value : int):
        ...
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
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
    def faces(self) -> List[aspose.cad.fileformats.stp.items.StepRepresentationItem]:
        ...
    
    @faces.setter
    def faces(self, value : List[aspose.cad.fileformats.stp.items.StepRepresentationItem]):
        ...
    
    ...

class StepColour(StepRepresentationItem):
    '''Colour class for STP file.'''
    
    @property
    def item_type(self) -> aspose.cad.fileformats.stp.items.StepItemType:
        ...
    
    @property
    def name(self) -> str:
        ...
    
    @name.setter
    def name(self, value : str):
        ...
    
    @property
    def u_id(self) -> int:
        ...
    
    @u_id.setter
    def u_id(self, value : int):
        ...
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
        ...
    
    @property
    def area(self) -> float:
        '''Gets the area of the entity.'''
        ...
    
    @property
    def length(self) -> float:
        '''Gets the length of the entity.'''
        ...
    
    ...

class StepColourRGB(StepColour):
    '''ColourRGB class for STP file.'''
    
    @property
    def item_type(self) -> aspose.cad.fileformats.stp.items.StepItemType:
        ...
    
    @property
    def name(self) -> str:
        ...
    
    @name.setter
    def name(self, value : str):
        ...
    
    @property
    def u_id(self) -> int:
        ...
    
    @u_id.setter
    def u_id(self, value : int):
        ...
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
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
    def red(self) -> float:
        ...
    
    @red.setter
    def red(self, value : float):
        ...
    
    @property
    def green(self) -> float:
        ...
    
    @green.setter
    def green(self, value : float):
        ...
    
    @property
    def blue(self) -> float:
        ...
    
    @blue.setter
    def blue(self, value : float):
        ...
    
    ...

class StepComplexItem(StepRepresentationItem):
    '''Complex item class for holding a list of STP items.'''
    
    @property
    def item_type(self) -> aspose.cad.fileformats.stp.items.StepItemType:
        ...
    
    @property
    def name(self) -> str:
        ...
    
    @name.setter
    def name(self, value : str):
        ...
    
    @property
    def u_id(self) -> int:
        ...
    
    @u_id.setter
    def u_id(self, value : int):
        ...
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
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
    def items(self) -> List[aspose.cad.fileformats.stp.items.StepRepresentationItem]:
        ...
    
    @items.setter
    def items(self, value : List[aspose.cad.fileformats.stp.items.StepRepresentationItem]):
        ...
    
    ...

class StepComplexTriangulatedFace(StepTessellatedFace):
    '''ComplexTriangulatedFace class for STP file.
    Class represents complex tessellated face.
    A tessellated geometry can be defined either by a TRIANGULATED_FACE or by
    a COMPLEX_TRIANGULATED_FACE. These entities are similar to the entities
    TRIANGULATED_SURFACE_SET and COMPLEX_TRIANGULATED_SURFACE_SET.
    The only difference between a tessellated face and a tessellated surface set
    is that the tesselated face has an additional attribute GeometricLink.
    This optional attribute can be used for preserving the exact definition of
    the underlying exact geometry.'''
    
    @property
    def item_type(self) -> aspose.cad.fileformats.stp.items.StepItemType:
        ...
    
    @property
    def name(self) -> str:
        ...
    
    @name.setter
    def name(self, value : str):
        ...
    
    @property
    def u_id(self) -> int:
        ...
    
    @u_id.setter
    def u_id(self, value : int):
        ...
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
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
    def coordinates(self) -> aspose.cad.fileformats.stp.items.StepCoordinatesList:
        ...
    
    @coordinates.setter
    def coordinates(self, value : aspose.cad.fileformats.stp.items.StepCoordinatesList):
        ...
    
    @property
    def pn_max(self) -> int:
        ...
    
    @pn_max.setter
    def pn_max(self, value : int):
        ...
    
    @property
    def normals(self) -> List[List[float]]:
        ...
    
    @normals.setter
    def normals(self, value : List[List[float]]):
        ...
    
    @property
    def geometric_link(self) -> aspose.cad.fileformats.stp.items.StepRepresentationItem:
        ...
    
    @geometric_link.setter
    def geometric_link(self, value : aspose.cad.fileformats.stp.items.StepRepresentationItem):
        ...
    
    @property
    def pn_index(self) -> List[int]:
        ...
    
    @pn_index.setter
    def pn_index(self, value : List[int]):
        ...
    
    @property
    def triangle_strips(self) -> List[List[int]]:
        ...
    
    @triangle_strips.setter
    def triangle_strips(self, value : List[List[int]]):
        ...
    
    @property
    def triangle_fans(self) -> List[List[int]]:
        ...
    
    @triangle_fans.setter
    def triangle_fans(self, value : List[List[int]]):
        ...
    
    ...

class StepComplexTriangulatedSurfaceSet(StepTessellatedItem):
    '''ComplexTriangulatedSurfaceSet class for STP file.
    Class represents complex tessellated surface set.
    A tessellated geometry can be defined either by a TRIANGULATED_FACE or by
    a COMPLEX_TRIANGULATED_FACE. These entities are similar to the entities
    TRIANGULATED_SURFACE_SET and COMPLEX_TRIANGULATED_SURFACE_SET.
    The only difference between a tessellated face and a tessellated surface set
    is that the tesselated face has an additional attribute GeometricLink.
    This optional attribute can be used for preserving the exact definition of
    the underlying exact geometry.'''
    
    @property
    def item_type(self) -> aspose.cad.fileformats.stp.items.StepItemType:
        ...
    
    @property
    def name(self) -> str:
        ...
    
    @name.setter
    def name(self, value : str):
        ...
    
    @property
    def u_id(self) -> int:
        ...
    
    @u_id.setter
    def u_id(self, value : int):
        ...
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
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
    def coordinates(self) -> aspose.cad.fileformats.stp.items.StepCoordinatesList:
        ...
    
    @coordinates.setter
    def coordinates(self, value : aspose.cad.fileformats.stp.items.StepCoordinatesList):
        ...
    
    @property
    def pn_max(self) -> int:
        ...
    
    @pn_max.setter
    def pn_max(self, value : int):
        ...
    
    @property
    def normals(self) -> List[List[float]]:
        ...
    
    @normals.setter
    def normals(self, value : List[List[float]]):
        ...
    
    @property
    def pn_index(self) -> List[int]:
        ...
    
    @pn_index.setter
    def pn_index(self, value : List[int]):
        ...
    
    @property
    def triangle_strips(self) -> List[List[int]]:
        ...
    
    @triangle_strips.setter
    def triangle_strips(self, value : List[List[int]]):
        ...
    
    @property
    def triangle_fans(self) -> List[List[int]]:
        ...
    
    @triangle_fans.setter
    def triangle_fans(self, value : List[List[int]]):
        ...
    
    ...

class StepCompositeCurve(StepBoundedCurve):
    '''CompositeCurve class for STP file.'''
    
    @property
    def item_type(self) -> aspose.cad.fileformats.stp.items.StepItemType:
        ...
    
    @property
    def name(self) -> str:
        ...
    
    @name.setter
    def name(self, value : str):
        ...
    
    @property
    def u_id(self) -> int:
        ...
    
    @u_id.setter
    def u_id(self, value : int):
        ...
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
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
    def segments(self) -> List[aspose.cad.fileformats.stp.items.StepRepresentationItem]:
        ...
    
    @segments.setter
    def segments(self, value : List[aspose.cad.fileformats.stp.items.StepRepresentationItem]):
        ...
    
    @property
    def self_intersect(self) -> bool:
        ...
    
    @self_intersect.setter
    def self_intersect(self, value : bool):
        ...
    
    ...

class StepCompositeCurveSegment(StepFoundedItem):
    '''CompositeCurveSegment class for STP file.'''
    
    @property
    def item_type(self) -> aspose.cad.fileformats.stp.items.StepItemType:
        ...
    
    @property
    def name(self) -> str:
        ...
    
    @name.setter
    def name(self, value : str):
        ...
    
    @property
    def u_id(self) -> int:
        ...
    
    @u_id.setter
    def u_id(self, value : int):
        ...
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
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
    def transition(self) -> aspose.cad.fileformats.stp.items.StepTransitionCode:
        ...
    
    @transition.setter
    def transition(self, value : aspose.cad.fileformats.stp.items.StepTransitionCode):
        ...
    
    @property
    def same_sense(self) -> bool:
        ...
    
    @same_sense.setter
    def same_sense(self, value : bool):
        ...
    
    @property
    def parent_curve(self) -> aspose.cad.fileformats.stp.items.StepCurve:
        ...
    
    @parent_curve.setter
    def parent_curve(self, value : aspose.cad.fileformats.stp.items.StepCurve):
        ...
    
    ...

class StepConic(StepCurve):
    '''StepConic class for STP file.'''
    
    @property
    def item_type(self) -> aspose.cad.fileformats.stp.items.StepItemType:
        ...
    
    @property
    def name(self) -> str:
        ...
    
    @name.setter
    def name(self, value : str):
        ...
    
    @property
    def u_id(self) -> int:
        ...
    
    @u_id.setter
    def u_id(self, value : int):
        ...
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
        ...
    
    @property
    def area(self) -> float:
        '''Gets the area of the entity.'''
        ...
    
    @property
    def length(self) -> float:
        '''Gets the length of the entity.'''
        ...
    
    ...

class StepConicalSurface(StepSurface):
    '''ConicalSurface class for STP file.'''
    
    @property
    def item_type(self) -> aspose.cad.fileformats.stp.items.StepItemType:
        ...
    
    @property
    def name(self) -> str:
        ...
    
    @name.setter
    def name(self, value : str):
        ...
    
    @property
    def u_id(self) -> int:
        ...
    
    @u_id.setter
    def u_id(self, value : int):
        ...
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
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
    def conical_surface(self) -> aspose.cad.fileformats.stp.items.StepConicalSurface:
        ...
    
    @property
    def radius(self) -> float:
        ...
    
    @radius.setter
    def radius(self, value : float):
        ...
    
    @property
    def semi_angle(self) -> float:
        ...
    
    @semi_angle.setter
    def semi_angle(self, value : float):
        ...
    
    @property
    def axis(self) -> aspose.cad.fileformats.stp.items.StepAxis2Placement3D:
        ...
    
    @axis.setter
    def axis(self, value : aspose.cad.fileformats.stp.items.StepAxis2Placement3D):
        ...
    
    ...

class StepConnectedFaceSet(StepTopologicalRepresentationItem):
    '''ConnectedFaceSet class.'''
    
    @property
    def item_type(self) -> aspose.cad.fileformats.stp.items.StepItemType:
        ...
    
    @property
    def name(self) -> str:
        ...
    
    @name.setter
    def name(self, value : str):
        ...
    
    @property
    def u_id(self) -> int:
        ...
    
    @u_id.setter
    def u_id(self, value : int):
        ...
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
        ...
    
    @property
    def area(self) -> float:
        '''Gets the area of the entity.'''
        ...
    
    @property
    def length(self) -> float:
        '''Gets the length of the entity.'''
        ...
    
    ...

class StepCoordinatesList(StepTessellatedItem):
    '''CoordinatesList class for STP file.'''
    
    @property
    def item_type(self) -> aspose.cad.fileformats.stp.items.StepItemType:
        ...
    
    @property
    def name(self) -> str:
        ...
    
    @name.setter
    def name(self, value : str):
        ...
    
    @property
    def u_id(self) -> int:
        ...
    
    @u_id.setter
    def u_id(self, value : int):
        ...
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
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
    def n_points(self) -> int:
        ...
    
    @n_points.setter
    def n_points(self, value : int):
        ...
    
    @property
    def position_coords(self) -> List[List[float]]:
        ...
    
    @position_coords.setter
    def position_coords(self, value : List[List[float]]):
        ...
    
    ...

class StepCurve(StepGeometricRepresentationItem):
    '''Curve class for STP file.'''
    
    @property
    def item_type(self) -> aspose.cad.fileformats.stp.items.StepItemType:
        ...
    
    @property
    def name(self) -> str:
        ...
    
    @name.setter
    def name(self, value : str):
        ...
    
    @property
    def u_id(self) -> int:
        ...
    
    @u_id.setter
    def u_id(self, value : int):
        ...
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
        ...
    
    @property
    def area(self) -> float:
        '''Gets the area of the entity.'''
        ...
    
    @property
    def length(self) -> float:
        '''Gets the length of the entity.'''
        ...
    
    ...

class StepCurveStyle(StepFoundedItem):
    '''CurveStyle class for STP file.'''
    
    @property
    def item_type(self) -> aspose.cad.fileformats.stp.items.StepItemType:
        ...
    
    @property
    def name(self) -> str:
        ...
    
    @name.setter
    def name(self, value : str):
        ...
    
    @property
    def u_id(self) -> int:
        ...
    
    @u_id.setter
    def u_id(self, value : int):
        ...
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
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
    def curve_font(self) -> aspose.cad.fileformats.stp.items.StepRepresentationItem:
        ...
    
    @curve_font.setter
    def curve_font(self, value : aspose.cad.fileformats.stp.items.StepRepresentationItem):
        ...
    
    @property
    def curve_width(self) -> float:
        ...
    
    @curve_width.setter
    def curve_width(self, value : float):
        ...
    
    @property
    def curve_colour(self) -> aspose.cad.fileformats.stp.items.StepColour:
        ...
    
    @curve_colour.setter
    def curve_colour(self, value : aspose.cad.fileformats.stp.items.StepColour):
        ...
    
    ...

class StepCylindricalSurface(StepElementarySurface):
    '''CylindricalSurface class for STP file.'''
    
    @property
    def item_type(self) -> aspose.cad.fileformats.stp.items.StepItemType:
        ...
    
    @property
    def name(self) -> str:
        ...
    
    @name.setter
    def name(self, value : str):
        ...
    
    @property
    def u_id(self) -> int:
        ...
    
    @u_id.setter
    def u_id(self, value : int):
        ...
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
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
    def position(self) -> aspose.cad.fileformats.stp.items.StepAxis2Placement3D:
        ...
    
    @position.setter
    def position(self, value : aspose.cad.fileformats.stp.items.StepAxis2Placement3D):
        ...
    
    @property
    def radius(self) -> float:
        ...
    
    @radius.setter
    def radius(self, value : float):
        ...
    
    ...

class StepDefinitionalRepresentation(StepGeometricRepresentationItem):
    '''DefinitionalRepresentation class for STP file.'''
    
    @property
    def item_type(self) -> aspose.cad.fileformats.stp.items.StepItemType:
        ...
    
    @property
    def name(self) -> str:
        ...
    
    @name.setter
    def name(self, value : str):
        ...
    
    @property
    def u_id(self) -> int:
        ...
    
    @u_id.setter
    def u_id(self, value : int):
        ...
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
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
    def representation_items(self) -> List[aspose.cad.fileformats.stp.items.StepRepresentationItem]:
        ...
    
    @representation_items.setter
    def representation_items(self, value : List[aspose.cad.fileformats.stp.items.StepRepresentationItem]):
        ...
    
    @property
    def definition_context(self) -> aspose.cad.fileformats.stp.items.StepRepresentationItem:
        ...
    
    ...

class StepDirection(StepTriple):
    '''Direction class for STP file.'''
    
    def equals(self, other : aspose.cad.fileformats.stp.items.StepTriple) -> bool:
        ...
    
    @property
    def item_type(self) -> aspose.cad.fileformats.stp.items.StepItemType:
        ...
    
    @property
    def name(self) -> str:
        ...
    
    @name.setter
    def name(self, value : str):
        ...
    
    @property
    def u_id(self) -> int:
        ...
    
    @u_id.setter
    def u_id(self, value : int):
        ...
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
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
    def x(self) -> float:
        ...
    
    @x.setter
    def x(self, value : float):
        ...
    
    @property
    def y(self) -> float:
        ...
    
    @y.setter
    def y(self, value : float):
        ...
    
    @property
    def z(self) -> float:
        ...
    
    @z.setter
    def z(self, value : float):
        ...
    
    ...

class StepDraughtingPreDefinedColour(StepPreDefinedColour):
    '''DraughtingPreDefinedColour class for STP file.'''
    
    @property
    def item_type(self) -> aspose.cad.fileformats.stp.items.StepItemType:
        ...
    
    @property
    def name(self) -> str:
        ...
    
    @name.setter
    def name(self, value : str):
        ...
    
    @property
    def u_id(self) -> int:
        ...
    
    @u_id.setter
    def u_id(self, value : int):
        ...
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
        ...
    
    @property
    def area(self) -> float:
        '''Gets the area of the entity.'''
        ...
    
    @property
    def length(self) -> float:
        '''Gets the length of the entity.'''
        ...
    
    ...

class StepDraughtingPreDefinedCurveFont(StepRepresentationItem):
    '''DraughtingPreDefinedCurveFont class for STP file.'''
    
    @property
    def item_type(self) -> aspose.cad.fileformats.stp.items.StepItemType:
        ...
    
    @property
    def name(self) -> str:
        ...
    
    @name.setter
    def name(self, value : str):
        ...
    
    @property
    def u_id(self) -> int:
        ...
    
    @u_id.setter
    def u_id(self, value : int):
        ...
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
        ...
    
    @property
    def area(self) -> float:
        '''Gets the area of the entity.'''
        ...
    
    @property
    def length(self) -> float:
        '''Gets the length of the entity.'''
        ...
    
    ...

class StepEdge(StepTopologicalRepresentationItem):
    '''Edge class for STP file.'''
    
    @property
    def item_type(self) -> aspose.cad.fileformats.stp.items.StepItemType:
        ...
    
    @property
    def name(self) -> str:
        ...
    
    @name.setter
    def name(self, value : str):
        ...
    
    @property
    def u_id(self) -> int:
        ...
    
    @u_id.setter
    def u_id(self, value : int):
        ...
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
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
    def edge_start(self) -> aspose.cad.fileformats.stp.items.StepVertexPoint:
        ...
    
    @edge_start.setter
    def edge_start(self, value : aspose.cad.fileformats.stp.items.StepVertexPoint):
        ...
    
    @property
    def edge_end(self) -> aspose.cad.fileformats.stp.items.StepVertexPoint:
        ...
    
    @edge_end.setter
    def edge_end(self, value : aspose.cad.fileformats.stp.items.StepVertexPoint):
        ...
    
    ...

class StepEdgeCurve(StepEdge):
    '''EdgeCurve class for STP file.'''
    
    @property
    def item_type(self) -> aspose.cad.fileformats.stp.items.StepItemType:
        ...
    
    @property
    def name(self) -> str:
        ...
    
    @name.setter
    def name(self, value : str):
        ...
    
    @property
    def u_id(self) -> int:
        ...
    
    @u_id.setter
    def u_id(self, value : int):
        ...
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
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
    def edge_start(self) -> aspose.cad.fileformats.stp.items.StepVertexPoint:
        ...
    
    @edge_start.setter
    def edge_start(self, value : aspose.cad.fileformats.stp.items.StepVertexPoint):
        ...
    
    @property
    def edge_end(self) -> aspose.cad.fileformats.stp.items.StepVertexPoint:
        ...
    
    @edge_end.setter
    def edge_end(self, value : aspose.cad.fileformats.stp.items.StepVertexPoint):
        ...
    
    @property
    def edge_geometry(self) -> aspose.cad.fileformats.stp.items.StepRepresentationItem:
        ...
    
    @edge_geometry.setter
    def edge_geometry(self, value : aspose.cad.fileformats.stp.items.StepRepresentationItem):
        ...
    
    @property
    def is_same_sense(self) -> bool:
        ...
    
    @is_same_sense.setter
    def is_same_sense(self, value : bool):
        ...
    
    ...

class StepEdgeLoop(StepLoop):
    '''EdgeLoop class for STP file.'''
    
    @property
    def item_type(self) -> aspose.cad.fileformats.stp.items.StepItemType:
        ...
    
    @property
    def name(self) -> str:
        ...
    
    @name.setter
    def name(self, value : str):
        ...
    
    @property
    def u_id(self) -> int:
        ...
    
    @u_id.setter
    def u_id(self, value : int):
        ...
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
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
    def edge_list(self) -> List[aspose.cad.fileformats.stp.items.StepOrientedEdge]:
        ...
    
    ...

class StepElementarySurface(StepSurface):
    '''ElementarySurface class for STP file.'''
    
    @property
    def item_type(self) -> aspose.cad.fileformats.stp.items.StepItemType:
        ...
    
    @property
    def name(self) -> str:
        ...
    
    @name.setter
    def name(self, value : str):
        ...
    
    @property
    def u_id(self) -> int:
        ...
    
    @u_id.setter
    def u_id(self, value : int):
        ...
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
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
    def position(self) -> aspose.cad.fileformats.stp.items.StepAxis2Placement3D:
        ...
    
    @position.setter
    def position(self, value : aspose.cad.fileformats.stp.items.StepAxis2Placement3D):
        ...
    
    ...

class StepEllipse(StepConic):
    '''Ellipse class for STP file.'''
    
    @property
    def item_type(self) -> aspose.cad.fileformats.stp.items.StepItemType:
        ...
    
    @property
    def name(self) -> str:
        ...
    
    @name.setter
    def name(self, value : str):
        ...
    
    @property
    def u_id(self) -> int:
        ...
    
    @u_id.setter
    def u_id(self, value : int):
        ...
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
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
    def position(self) -> aspose.cad.fileformats.stp.items.StepAxis2Placement:
        ...
    
    @position.setter
    def position(self, value : aspose.cad.fileformats.stp.items.StepAxis2Placement):
        ...
    
    @property
    def semi_axis1(self) -> float:
        ...
    
    @semi_axis1.setter
    def semi_axis1(self, value : float):
        ...
    
    @property
    def semi_axis2(self) -> float:
        ...
    
    @semi_axis2.setter
    def semi_axis2(self, value : float):
        ...
    
    ...

class StepFace(StepTopologicalRepresentationItem):
    '''Face class for STP file.'''
    
    @property
    def item_type(self) -> aspose.cad.fileformats.stp.items.StepItemType:
        ...
    
    @property
    def name(self) -> str:
        ...
    
    @name.setter
    def name(self, value : str):
        ...
    
    @property
    def u_id(self) -> int:
        ...
    
    @u_id.setter
    def u_id(self, value : int):
        ...
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
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
    def bounds(self) -> List[aspose.cad.fileformats.stp.items.StepFaceBound]:
        ...
    
    @bounds.setter
    def bounds(self, value : List[aspose.cad.fileformats.stp.items.StepFaceBound]):
        ...
    
    ...

class StepFaceBound(StepTopologicalRepresentationItem):
    '''FaceBound class for STP file.'''
    
    @property
    def item_type(self) -> aspose.cad.fileformats.stp.items.StepItemType:
        ...
    
    @property
    def name(self) -> str:
        ...
    
    @name.setter
    def name(self, value : str):
        ...
    
    @property
    def u_id(self) -> int:
        ...
    
    @u_id.setter
    def u_id(self, value : int):
        ...
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
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
    def bound(self) -> aspose.cad.fileformats.stp.items.StepLoop:
        ...
    
    @bound.setter
    def bound(self, value : aspose.cad.fileformats.stp.items.StepLoop):
        ...
    
    @property
    def orientation(self) -> bool:
        ...
    
    @orientation.setter
    def orientation(self, value : bool):
        ...
    
    ...

class StepFaceOuterBound(StepFaceBound):
    '''FaceOuterBound class for STP file.'''
    
    @property
    def item_type(self) -> aspose.cad.fileformats.stp.items.StepItemType:
        ...
    
    @property
    def name(self) -> str:
        ...
    
    @name.setter
    def name(self, value : str):
        ...
    
    @property
    def u_id(self) -> int:
        ...
    
    @u_id.setter
    def u_id(self, value : int):
        ...
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
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
    def bound(self) -> aspose.cad.fileformats.stp.items.StepLoop:
        ...
    
    @bound.setter
    def bound(self, value : aspose.cad.fileformats.stp.items.StepLoop):
        ...
    
    @property
    def orientation(self) -> bool:
        ...
    
    @orientation.setter
    def orientation(self, value : bool):
        ...
    
    ...

class StepFaceSurface(StepFace):
    '''FaceSurface class for STP file.'''
    
    @property
    def item_type(self) -> aspose.cad.fileformats.stp.items.StepItemType:
        ...
    
    @property
    def name(self) -> str:
        ...
    
    @name.setter
    def name(self, value : str):
        ...
    
    @property
    def u_id(self) -> int:
        ...
    
    @u_id.setter
    def u_id(self, value : int):
        ...
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
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
    def bounds(self) -> List[aspose.cad.fileformats.stp.items.StepFaceBound]:
        ...
    
    @bounds.setter
    def bounds(self, value : List[aspose.cad.fileformats.stp.items.StepFaceBound]):
        ...
    
    @property
    def face_geometry(self) -> aspose.cad.fileformats.stp.items.StepSurface:
        ...
    
    @face_geometry.setter
    def face_geometry(self, value : aspose.cad.fileformats.stp.items.StepSurface):
        ...
    
    @property
    def same_sense(self) -> bool:
        ...
    
    @same_sense.setter
    def same_sense(self, value : bool):
        ...
    
    ...

class StepFacetedBrep(StepRepresentationItem):
    '''FacetedBrep class for STP file.'''
    
    @property
    def item_type(self) -> aspose.cad.fileformats.stp.items.StepItemType:
        ...
    
    @property
    def name(self) -> str:
        ...
    
    @name.setter
    def name(self, value : str):
        ...
    
    @property
    def u_id(self) -> int:
        ...
    
    @u_id.setter
    def u_id(self, value : int):
        ...
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
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
    def closed_shell(self) -> aspose.cad.fileformats.stp.items.StepClosedShell:
        ...
    
    @closed_shell.setter
    def closed_shell(self, value : aspose.cad.fileformats.stp.items.StepClosedShell):
        ...
    
    ...

class StepFacetedBrepShapeRepresentation(StepShapeRepresentation):
    '''FacetedBrepShapeRepresentation class for STP file.'''
    
    @property
    def item_type(self) -> aspose.cad.fileformats.stp.items.StepItemType:
        ...
    
    @property
    def name(self) -> str:
        ...
    
    @name.setter
    def name(self, value : str):
        ...
    
    @property
    def u_id(self) -> int:
        ...
    
    @u_id.setter
    def u_id(self, value : int):
        ...
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
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
    def shape_items(self) -> List[aspose.cad.fileformats.stp.items.StepRepresentationItem]:
        ...
    
    @shape_items.setter
    def shape_items(self, value : List[aspose.cad.fileformats.stp.items.StepRepresentationItem]):
        ...
    
    @property
    def representation_context(self) -> aspose.cad.fileformats.stp.items.StepRepresentationItem:
        ...
    
    ...

class StepFillAreaStyle(StepFoundedItem):
    '''FillAreaStyle class for STP file.'''
    
    @property
    def item_type(self) -> aspose.cad.fileformats.stp.items.StepItemType:
        ...
    
    @property
    def name(self) -> str:
        ...
    
    @name.setter
    def name(self, value : str):
        ...
    
    @property
    def u_id(self) -> int:
        ...
    
    @u_id.setter
    def u_id(self, value : int):
        ...
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
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
    def fill_styles(self) -> List[aspose.cad.fileformats.stp.items.StepRepresentationItem]:
        ...
    
    @fill_styles.setter
    def fill_styles(self, value : List[aspose.cad.fileformats.stp.items.StepRepresentationItem]):
        ...
    
    ...

class StepFillAreaStyleColour(StepRepresentationItem):
    '''FillAreaStyleColour class for STP file.'''
    
    @property
    def item_type(self) -> aspose.cad.fileformats.stp.items.StepItemType:
        ...
    
    @property
    def name(self) -> str:
        ...
    
    @name.setter
    def name(self, value : str):
        ...
    
    @property
    def u_id(self) -> int:
        ...
    
    @u_id.setter
    def u_id(self, value : int):
        ...
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
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
    def colour(self) -> aspose.cad.fileformats.stp.items.StepColour:
        ...
    
    @colour.setter
    def colour(self, value : aspose.cad.fileformats.stp.items.StepColour):
        ...
    
    ...

class StepFoundedItem(StepRepresentationItem):
    '''FoundedItem class for STP file.'''
    
    @property
    def item_type(self) -> aspose.cad.fileformats.stp.items.StepItemType:
        ...
    
    @property
    def name(self) -> str:
        ...
    
    @name.setter
    def name(self, value : str):
        ...
    
    @property
    def u_id(self) -> int:
        ...
    
    @u_id.setter
    def u_id(self, value : int):
        ...
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
        ...
    
    @property
    def area(self) -> float:
        '''Gets the area of the entity.'''
        ...
    
    @property
    def length(self) -> float:
        '''Gets the length of the entity.'''
        ...
    
    ...

class StepGeometricCurveSet(StepGeometricSet):
    '''Geometric CurveSet class for STP file.'''
    
    @property
    def item_type(self) -> aspose.cad.fileformats.stp.items.StepItemType:
        ...
    
    @property
    def name(self) -> str:
        ...
    
    @name.setter
    def name(self, value : str):
        ...
    
    @property
    def u_id(self) -> int:
        ...
    
    @u_id.setter
    def u_id(self, value : int):
        ...
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
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
    def curves(self) -> List[aspose.cad.fileformats.stp.items.StepRepresentationItem]:
        ...
    
    @curves.setter
    def curves(self, value : List[aspose.cad.fileformats.stp.items.StepRepresentationItem]):
        ...
    
    ...

class StepGeometricRepresentationItem(StepRepresentationItem):
    '''Geometric RepresentationItem class for STP file.'''
    
    @property
    def item_type(self) -> aspose.cad.fileformats.stp.items.StepItemType:
        ...
    
    @property
    def name(self) -> str:
        ...
    
    @name.setter
    def name(self, value : str):
        ...
    
    @property
    def u_id(self) -> int:
        ...
    
    @u_id.setter
    def u_id(self, value : int):
        ...
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
        ...
    
    @property
    def area(self) -> float:
        '''Gets the area of the entity.'''
        ...
    
    @property
    def length(self) -> float:
        '''Gets the length of the entity.'''
        ...
    
    ...

class StepGeometricSet(StepGeometricRepresentationItem):
    '''Geometric Set class for STP file.'''
    
    @property
    def item_type(self) -> aspose.cad.fileformats.stp.items.StepItemType:
        ...
    
    @property
    def name(self) -> str:
        ...
    
    @name.setter
    def name(self, value : str):
        ...
    
    @property
    def u_id(self) -> int:
        ...
    
    @u_id.setter
    def u_id(self, value : int):
        ...
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
        ...
    
    @property
    def area(self) -> float:
        '''Gets the area of the entity.'''
        ...
    
    @property
    def length(self) -> float:
        '''Gets the length of the entity.'''
        ...
    
    ...

class StepGeometricallyBoundedWireframeShapeRepresentation(StepShapeRepresentation):
    '''ShapeRepresentation class.'''
    
    @property
    def item_type(self) -> aspose.cad.fileformats.stp.items.StepItemType:
        ...
    
    @property
    def name(self) -> str:
        ...
    
    @name.setter
    def name(self, value : str):
        ...
    
    @property
    def u_id(self) -> int:
        ...
    
    @u_id.setter
    def u_id(self, value : int):
        ...
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
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
    def shape_items(self) -> List[aspose.cad.fileformats.stp.items.StepRepresentationItem]:
        ...
    
    @shape_items.setter
    def shape_items(self, value : List[aspose.cad.fileformats.stp.items.StepRepresentationItem]):
        ...
    
    @property
    def representation_context(self) -> aspose.cad.fileformats.stp.items.StepRepresentationItem:
        ...
    
    ...

class StepItemDefinedTransformation(StepTransformation):
    '''ItemDefinedTransformation class for STP.'''
    
    @property
    def item_type(self) -> aspose.cad.fileformats.stp.items.StepItemType:
        ...
    
    @property
    def name(self) -> str:
        ...
    
    @name.setter
    def name(self, value : str):
        ...
    
    @property
    def u_id(self) -> int:
        ...
    
    @u_id.setter
    def u_id(self, value : int):
        ...
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
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
    def description(self) -> str:
        ...
    
    @description.setter
    def description(self, value : str):
        ...
    
    @property
    def transform_item1(self) -> aspose.cad.fileformats.stp.items.StepRepresentationItem:
        ...
    
    @transform_item1.setter
    def transform_item1(self, value : aspose.cad.fileformats.stp.items.StepRepresentationItem):
        ...
    
    @property
    def transform_item2(self) -> aspose.cad.fileformats.stp.items.StepRepresentationItem:
        ...
    
    @transform_item2.setter
    def transform_item2(self, value : aspose.cad.fileformats.stp.items.StepRepresentationItem):
        ...
    
    ...

class StepKnotTypeUtils:
    '''Class with utility methods for KnotType enum.'''
    
    @staticmethod
    def get_knot_spec(spec : aspose.cad.fileformats.stp.items.StepKnotType) -> str:
        ...
    
    @staticmethod
    def parse_knot_spec(enumeration_value : str) -> aspose.cad.fileformats.stp.items.StepKnotType:
        ...
    
    ...

class StepLine(StepCurve):
    '''Line class for STP file.'''
    
    @staticmethod
    def from_points(x1 : float, y1 : float, z1 : float, x2 : float, y2 : float, z2 : float) -> aspose.cad.fileformats.stp.items.StepLine:
        ...
    
    @property
    def item_type(self) -> aspose.cad.fileformats.stp.items.StepItemType:
        ...
    
    @property
    def name(self) -> str:
        ...
    
    @name.setter
    def name(self, value : str):
        ...
    
    @property
    def u_id(self) -> int:
        ...
    
    @u_id.setter
    def u_id(self, value : int):
        ...
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
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
    def point(self) -> aspose.cad.fileformats.stp.items.StepCartesianPoint:
        ...
    
    @point.setter
    def point(self, value : aspose.cad.fileformats.stp.items.StepCartesianPoint):
        ...
    
    @property
    def vector(self) -> aspose.cad.fileformats.stp.items.StepVector:
        ...
    
    @vector.setter
    def vector(self, value : aspose.cad.fileformats.stp.items.StepVector):
        ...
    
    ...

class StepLoop(StepTopologicalRepresentationItem):
    '''Loop class for STP file.'''
    
    @property
    def item_type(self) -> aspose.cad.fileformats.stp.items.StepItemType:
        ...
    
    @property
    def name(self) -> str:
        ...
    
    @name.setter
    def name(self, value : str):
        ...
    
    @property
    def u_id(self) -> int:
        ...
    
    @u_id.setter
    def u_id(self, value : int):
        ...
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
        ...
    
    @property
    def area(self) -> float:
        '''Gets the area of the entity.'''
        ...
    
    @property
    def length(self) -> float:
        '''Gets the length of the entity.'''
        ...
    
    ...

class StepManifoldSolidBrep(StepRepresentationItem):
    '''ManifoldSolidBrep class for STP file.'''
    
    @property
    def item_type(self) -> aspose.cad.fileformats.stp.items.StepItemType:
        ...
    
    @property
    def name(self) -> str:
        ...
    
    @name.setter
    def name(self, value : str):
        ...
    
    @property
    def u_id(self) -> int:
        ...
    
    @u_id.setter
    def u_id(self, value : int):
        ...
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
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
    def closed_shell(self) -> aspose.cad.fileformats.stp.items.StepClosedShell:
        ...
    
    @closed_shell.setter
    def closed_shell(self, value : aspose.cad.fileformats.stp.items.StepClosedShell):
        ...
    
    ...

class StepManifoldSurfaceShapeRepresentation(StepShapeRepresentation):
    '''ManifoldSurfaceShapeRepresentation class.'''
    
    @property
    def item_type(self) -> aspose.cad.fileformats.stp.items.StepItemType:
        ...
    
    @property
    def name(self) -> str:
        ...
    
    @name.setter
    def name(self, value : str):
        ...
    
    @property
    def u_id(self) -> int:
        ...
    
    @u_id.setter
    def u_id(self, value : int):
        ...
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
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
    def shape_items(self) -> List[aspose.cad.fileformats.stp.items.StepRepresentationItem]:
        ...
    
    @shape_items.setter
    def shape_items(self, value : List[aspose.cad.fileformats.stp.items.StepRepresentationItem]):
        ...
    
    @property
    def representation_context(self) -> aspose.cad.fileformats.stp.items.StepRepresentationItem:
        ...
    
    ...

class StepOpenShell(StepConnectedFaceSet):
    '''OpenShell class for STP file.'''
    
    @property
    def item_type(self) -> aspose.cad.fileformats.stp.items.StepItemType:
        ...
    
    @property
    def name(self) -> str:
        ...
    
    @name.setter
    def name(self, value : str):
        ...
    
    @property
    def u_id(self) -> int:
        ...
    
    @u_id.setter
    def u_id(self, value : int):
        ...
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
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
    def faces(self) -> List[aspose.cad.fileformats.stp.items.StepRepresentationItem]:
        ...
    
    @faces.setter
    def faces(self, value : List[aspose.cad.fileformats.stp.items.StepRepresentationItem]):
        ...
    
    ...

class StepOrientedEdge(StepEdge):
    '''OrientedEdge class for STP file.'''
    
    @property
    def item_type(self) -> aspose.cad.fileformats.stp.items.StepItemType:
        ...
    
    @property
    def name(self) -> str:
        ...
    
    @name.setter
    def name(self, value : str):
        ...
    
    @property
    def u_id(self) -> int:
        ...
    
    @u_id.setter
    def u_id(self, value : int):
        ...
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
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
    def edge_start(self) -> aspose.cad.fileformats.stp.items.StepVertexPoint:
        ...
    
    @edge_start.setter
    def edge_start(self, value : aspose.cad.fileformats.stp.items.StepVertexPoint):
        ...
    
    @property
    def edge_end(self) -> aspose.cad.fileformats.stp.items.StepVertexPoint:
        ...
    
    @edge_end.setter
    def edge_end(self, value : aspose.cad.fileformats.stp.items.StepVertexPoint):
        ...
    
    @property
    def edge_element(self) -> aspose.cad.fileformats.stp.items.StepEdge:
        ...
    
    @edge_element.setter
    def edge_element(self, value : aspose.cad.fileformats.stp.items.StepEdge):
        ...
    
    @property
    def orientation(self) -> bool:
        ...
    
    @orientation.setter
    def orientation(self, value : bool):
        ...
    
    ...

class StepPCurve(StepCurve):
    '''PCurve class for STP file.'''
    
    @property
    def item_type(self) -> aspose.cad.fileformats.stp.items.StepItemType:
        ...
    
    @property
    def name(self) -> str:
        ...
    
    @name.setter
    def name(self, value : str):
        ...
    
    @property
    def u_id(self) -> int:
        ...
    
    @u_id.setter
    def u_id(self, value : int):
        ...
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
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
    def surface(self) -> aspose.cad.fileformats.stp.items.StepElementarySurface:
        ...
    
    @surface.setter
    def surface(self, value : aspose.cad.fileformats.stp.items.StepElementarySurface):
        ...
    
    @property
    def representation(self) -> aspose.cad.fileformats.stp.items.StepDefinitionalRepresentation:
        ...
    
    ...

class StepPlacement(StepGeometricRepresentationItem):
    '''Placement class for STP file.'''
    
    @property
    def item_type(self) -> aspose.cad.fileformats.stp.items.StepItemType:
        ...
    
    @property
    def name(self) -> str:
        ...
    
    @name.setter
    def name(self, value : str):
        ...
    
    @property
    def u_id(self) -> int:
        ...
    
    @u_id.setter
    def u_id(self, value : int):
        ...
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
        ...
    
    @property
    def area(self) -> float:
        '''Gets the area of the entity.'''
        ...
    
    @property
    def length(self) -> float:
        '''Gets the length of the entity.'''
        ...
    
    ...

class StepPlane(StepElementarySurface):
    '''Plane class for STP file.'''
    
    @property
    def item_type(self) -> aspose.cad.fileformats.stp.items.StepItemType:
        ...
    
    @property
    def name(self) -> str:
        ...
    
    @name.setter
    def name(self, value : str):
        ...
    
    @property
    def u_id(self) -> int:
        ...
    
    @u_id.setter
    def u_id(self, value : int):
        ...
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
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
    def position(self) -> aspose.cad.fileformats.stp.items.StepAxis2Placement3D:
        ...
    
    @position.setter
    def position(self, value : aspose.cad.fileformats.stp.items.StepAxis2Placement3D):
        ...
    
    ...

class StepPoint(StepGeometricRepresentationItem):
    '''Point class for STP file.'''
    
    @property
    def item_type(self) -> aspose.cad.fileformats.stp.items.StepItemType:
        ...
    
    @property
    def name(self) -> str:
        ...
    
    @name.setter
    def name(self, value : str):
        ...
    
    @property
    def u_id(self) -> int:
        ...
    
    @u_id.setter
    def u_id(self, value : int):
        ...
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
        ...
    
    @property
    def area(self) -> float:
        '''Gets the area of the entity.'''
        ...
    
    @property
    def length(self) -> float:
        '''Gets the length of the entity.'''
        ...
    
    ...

class StepPolyLoop(StepLoop):
    '''PolyLoop class for STP file.'''
    
    @property
    def item_type(self) -> aspose.cad.fileformats.stp.items.StepItemType:
        ...
    
    @property
    def name(self) -> str:
        ...
    
    @name.setter
    def name(self, value : str):
        ...
    
    @property
    def u_id(self) -> int:
        ...
    
    @u_id.setter
    def u_id(self, value : int):
        ...
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
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
    def polygon(self) -> List[aspose.cad.fileformats.stp.items.StepCartesianPoint]:
        ...
    
    @polygon.setter
    def polygon(self, value : List[aspose.cad.fileformats.stp.items.StepCartesianPoint]):
        ...
    
    ...

class StepPreDefinedColour(StepColour):
    '''PreDefinedColour class for STP file.'''
    
    @property
    def item_type(self) -> aspose.cad.fileformats.stp.items.StepItemType:
        ...
    
    @property
    def name(self) -> str:
        ...
    
    @name.setter
    def name(self, value : str):
        ...
    
    @property
    def u_id(self) -> int:
        ...
    
    @u_id.setter
    def u_id(self, value : int):
        ...
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
        ...
    
    @property
    def area(self) -> float:
        '''Gets the area of the entity.'''
        ...
    
    @property
    def length(self) -> float:
        '''Gets the length of the entity.'''
        ...
    
    ...

class StepPresentationStyleAssignment(StepFoundedItem):
    '''PresentationStyleAssignment class for STP file.'''
    
    @property
    def item_type(self) -> aspose.cad.fileformats.stp.items.StepItemType:
        ...
    
    @property
    def name(self) -> str:
        ...
    
    @name.setter
    def name(self, value : str):
        ...
    
    @property
    def u_id(self) -> int:
        ...
    
    @u_id.setter
    def u_id(self, value : int):
        ...
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
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
    def styles(self) -> List[aspose.cad.fileformats.stp.items.StepFoundedItem]:
        ...
    
    @styles.setter
    def styles(self, value : List[aspose.cad.fileformats.stp.items.StepFoundedItem]):
        ...
    
    ...

class StepProduct(StepRepresentationItem):
    '''Product class for STP file.'''
    
    @property
    def item_type(self) -> aspose.cad.fileformats.stp.items.StepItemType:
        ...
    
    @property
    def name(self) -> str:
        ...
    
    @name.setter
    def name(self, value : str):
        ...
    
    @property
    def u_id(self) -> int:
        ...
    
    @u_id.setter
    def u_id(self, value : int):
        ...
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
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
    def frame_of_reference(self) -> List[aspose.cad.fileformats.stp.items.StepRepresentationItem]:
        ...
    
    @frame_of_reference.setter
    def frame_of_reference(self, value : List[aspose.cad.fileformats.stp.items.StepRepresentationItem]):
        ...
    
    @property
    def label_name(self) -> str:
        ...
    
    @label_name.setter
    def label_name(self, value : str):
        ...
    
    @property
    def description(self) -> str:
        ...
    
    @description.setter
    def description(self, value : str):
        ...
    
    ...

class StepProductDefinition(StepRepresentationItem):
    '''ProductDefinition class for STP file.'''
    
    @property
    def item_type(self) -> aspose.cad.fileformats.stp.items.StepItemType:
        ...
    
    @property
    def name(self) -> str:
        ...
    
    @name.setter
    def name(self, value : str):
        ...
    
    @property
    def u_id(self) -> int:
        ...
    
    @u_id.setter
    def u_id(self, value : int):
        ...
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
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
    def product_definition_formation(self) -> aspose.cad.fileformats.stp.items.StepProductDefinitionFormation:
        ...
    
    @product_definition_formation.setter
    def product_definition_formation(self, value : aspose.cad.fileformats.stp.items.StepProductDefinitionFormation):
        ...
    
    @property
    def definition_context(self) -> aspose.cad.fileformats.stp.items.StepRepresentationItem:
        ...
    
    @property
    def description(self) -> str:
        ...
    
    @description.setter
    def description(self, value : str):
        ...
    
    ...

class StepProductDefinitionFormation(StepRepresentationItem):
    '''ProductDefinitionFormation class for STP file.'''
    
    @property
    def item_type(self) -> aspose.cad.fileformats.stp.items.StepItemType:
        ...
    
    @property
    def name(self) -> str:
        ...
    
    @name.setter
    def name(self, value : str):
        ...
    
    @property
    def u_id(self) -> int:
        ...
    
    @u_id.setter
    def u_id(self, value : int):
        ...
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
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
    def product(self) -> aspose.cad.fileformats.stp.items.StepProduct:
        ...
    
    @product.setter
    def product(self, value : aspose.cad.fileformats.stp.items.StepProduct):
        ...
    
    @property
    def description(self) -> str:
        ...
    
    @description.setter
    def description(self, value : str):
        ...
    
    ...

class StepProductDefinitionShape(StepRepresentationItem):
    '''ProductDefinitionShape class for STP file.'''
    
    @property
    def item_type(self) -> aspose.cad.fileformats.stp.items.StepItemType:
        ...
    
    @property
    def name(self) -> str:
        ...
    
    @name.setter
    def name(self, value : str):
        ...
    
    @property
    def u_id(self) -> int:
        ...
    
    @u_id.setter
    def u_id(self, value : int):
        ...
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
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
    def definition(self) -> aspose.cad.fileformats.stp.items.StepProductDefinition:
        ...
    
    @definition.setter
    def definition(self, value : aspose.cad.fileformats.stp.items.StepProductDefinition):
        ...
    
    @property
    def description(self) -> str:
        ...
    
    @description.setter
    def description(self, value : str):
        ...
    
    ...

class StepRationalBSplineSurface(StepBSplineSurface):
    '''RationalBSplineSurface class for STP file.'''
    
    @property
    def item_type(self) -> aspose.cad.fileformats.stp.items.StepItemType:
        ...
    
    @property
    def name(self) -> str:
        ...
    
    @name.setter
    def name(self, value : str):
        ...
    
    @property
    def u_id(self) -> int:
        ...
    
    @u_id.setter
    def u_id(self, value : int):
        ...
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
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
    def u_degree(self) -> int:
        ...
    
    @u_degree.setter
    def u_degree(self, value : int):
        ...
    
    @property
    def v_degree(self) -> int:
        ...
    
    @v_degree.setter
    def v_degree(self, value : int):
        ...
    
    @property
    def control_points_list(self) -> List[List[aspose.cad.fileformats.stp.items.StepCartesianPoint]]:
        ...
    
    @control_points_list.setter
    def control_points_list(self, value : List[List[aspose.cad.fileformats.stp.items.StepCartesianPoint]]):
        ...
    
    @property
    def surface_form(self) -> aspose.cad.fileformats.stp.items.StepBSplineSurfaceForm:
        ...
    
    @surface_form.setter
    def surface_form(self, value : aspose.cad.fileformats.stp.items.StepBSplineSurfaceForm):
        ...
    
    @property
    def u_closed(self) -> bool:
        ...
    
    @u_closed.setter
    def u_closed(self, value : bool):
        ...
    
    @property
    def v_closed(self) -> bool:
        ...
    
    @v_closed.setter
    def v_closed(self, value : bool):
        ...
    
    @property
    def self_intersect(self) -> bool:
        ...
    
    @self_intersect.setter
    def self_intersect(self, value : bool):
        ...
    
    @property
    def weights_data(self) -> List[List[float]]:
        ...
    
    ...

class StepRepresentation(StepSurface):
    '''Representation StepSurface class.'''
    
    @property
    def item_type(self) -> aspose.cad.fileformats.stp.items.StepItemType:
        ...
    
    @property
    def name(self) -> str:
        ...
    
    @name.setter
    def name(self, value : str):
        ...
    
    @property
    def u_id(self) -> int:
        ...
    
    @u_id.setter
    def u_id(self, value : int):
        ...
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
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
    def representation(self) -> aspose.cad.fileformats.stp.items.StepRepresentation:
        ...
    
    @property
    def value_representation_item(self) -> aspose.cad.fileformats.stp.items.StepValueRepresentationItem:
        ...
    
    @value_representation_item.setter
    def value_representation_item(self, value : aspose.cad.fileformats.stp.items.StepValueRepresentationItem):
        ...
    
    ...

class StepRepresentationItem(aspose.cad.IDrawingEntity):
    '''RepresentationItem class for STP file.'''
    
    @property
    def item_type(self) -> aspose.cad.fileformats.stp.items.StepItemType:
        ...
    
    @property
    def name(self) -> str:
        ...
    
    @name.setter
    def name(self, value : str):
        ...
    
    @property
    def u_id(self) -> int:
        ...
    
    @u_id.setter
    def u_id(self, value : int):
        ...
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
        ...
    
    @property
    def area(self) -> float:
        '''Gets the area of the entity.'''
        ...
    
    @property
    def length(self) -> float:
        '''Gets the length of the entity.'''
        ...
    
    ...

class StepRepresentationRelationship(StepRepresentationItem):
    '''RepresentationRelationship class for STP.'''
    
    @property
    def item_type(self) -> aspose.cad.fileformats.stp.items.StepItemType:
        ...
    
    @property
    def name(self) -> str:
        ...
    
    @name.setter
    def name(self, value : str):
        ...
    
    @property
    def u_id(self) -> int:
        ...
    
    @u_id.setter
    def u_id(self, value : int):
        ...
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
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
    def description(self) -> str:
        ...
    
    @description.setter
    def description(self, value : str):
        ...
    
    @property
    def rep1(self) -> aspose.cad.fileformats.stp.items.StepRepresentationItem:
        ...
    
    @rep1.setter
    def rep1(self, value : aspose.cad.fileformats.stp.items.StepRepresentationItem):
        ...
    
    @property
    def rep2(self) -> aspose.cad.fileformats.stp.items.StepRepresentationItem:
        ...
    
    @rep2.setter
    def rep2(self, value : aspose.cad.fileformats.stp.items.StepRepresentationItem):
        ...
    
    ...

class StepRepresentationRelationshipWithTransformation(StepRepresentationItem):
    '''RepresentationRelationshipWithTransformation class for STP.'''
    
    @property
    def item_type(self) -> aspose.cad.fileformats.stp.items.StepItemType:
        ...
    
    @property
    def name(self) -> str:
        ...
    
    @name.setter
    def name(self, value : str):
        ...
    
    @property
    def u_id(self) -> int:
        ...
    
    @u_id.setter
    def u_id(self, value : int):
        ...
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
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
    def transformation(self) -> aspose.cad.fileformats.stp.items.StepTransformation:
        ...
    
    @transformation.setter
    def transformation(self, value : aspose.cad.fileformats.stp.items.StepTransformation):
        ...
    
    ...

class StepShapeDefinitionRepresentation(StepRepresentationItem):
    '''ShapeDefinitionRepresentation class.'''
    
    @property
    def item_type(self) -> aspose.cad.fileformats.stp.items.StepItemType:
        ...
    
    @property
    def name(self) -> str:
        ...
    
    @name.setter
    def name(self, value : str):
        ...
    
    @property
    def u_id(self) -> int:
        ...
    
    @u_id.setter
    def u_id(self, value : int):
        ...
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
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
    def product_definition_shape(self) -> aspose.cad.fileformats.stp.items.StepProductDefinitionShape:
        ...
    
    @product_definition_shape.setter
    def product_definition_shape(self, value : aspose.cad.fileformats.stp.items.StepProductDefinitionShape):
        ...
    
    @property
    def shape_representation(self) -> aspose.cad.fileformats.stp.items.StepShapeRepresentation:
        ...
    
    @shape_representation.setter
    def shape_representation(self, value : aspose.cad.fileformats.stp.items.StepShapeRepresentation):
        ...
    
    ...

class StepShapeRepresentation(StepRepresentationItem):
    '''ShapeRepresentation class.'''
    
    @property
    def item_type(self) -> aspose.cad.fileformats.stp.items.StepItemType:
        ...
    
    @property
    def name(self) -> str:
        ...
    
    @name.setter
    def name(self, value : str):
        ...
    
    @property
    def u_id(self) -> int:
        ...
    
    @u_id.setter
    def u_id(self, value : int):
        ...
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
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
    def shape_items(self) -> List[aspose.cad.fileformats.stp.items.StepRepresentationItem]:
        ...
    
    @shape_items.setter
    def shape_items(self, value : List[aspose.cad.fileformats.stp.items.StepRepresentationItem]):
        ...
    
    @property
    def representation_context(self) -> aspose.cad.fileformats.stp.items.StepRepresentationItem:
        ...
    
    ...

class StepShapeRepresentationRelationship(StepTopologicalRepresentationItem):
    '''ShapeRepresentationRelationship class.'''
    
    @property
    def item_type(self) -> aspose.cad.fileformats.stp.items.StepItemType:
        ...
    
    @property
    def name(self) -> str:
        ...
    
    @name.setter
    def name(self, value : str):
        ...
    
    @property
    def u_id(self) -> int:
        ...
    
    @u_id.setter
    def u_id(self, value : int):
        ...
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
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
    def text(self) -> str:
        ...
    
    @text.setter
    def text(self, value : str):
        ...
    
    @property
    def rep1(self) -> aspose.cad.fileformats.stp.items.StepRepresentationItem:
        ...
    
    @rep1.setter
    def rep1(self, value : aspose.cad.fileformats.stp.items.StepRepresentationItem):
        ...
    
    @property
    def rep2(self) -> aspose.cad.fileformats.stp.items.StepRepresentationItem:
        ...
    
    @rep2.setter
    def rep2(self, value : aspose.cad.fileformats.stp.items.StepRepresentationItem):
        ...
    
    ...

class StepShellBasedSurfaceModel(StepGeometricRepresentationItem):
    '''ShellBasedSurfaceModel class.'''
    
    @property
    def item_type(self) -> aspose.cad.fileformats.stp.items.StepItemType:
        ...
    
    @property
    def name(self) -> str:
        ...
    
    @name.setter
    def name(self, value : str):
        ...
    
    @property
    def u_id(self) -> int:
        ...
    
    @u_id.setter
    def u_id(self, value : int):
        ...
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
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
    def boundary(self) -> List[aspose.cad.fileformats.stp.items.StepConnectedFaceSet]:
        ...
    
    @boundary.setter
    def boundary(self, value : List[aspose.cad.fileformats.stp.items.StepConnectedFaceSet]):
        ...
    
    ...

class StepSphericalSurface(StepSurface):
    '''SphericalSurface class for STP file.'''
    
    @property
    def item_type(self) -> aspose.cad.fileformats.stp.items.StepItemType:
        ...
    
    @property
    def name(self) -> str:
        ...
    
    @name.setter
    def name(self, value : str):
        ...
    
    @property
    def u_id(self) -> int:
        ...
    
    @u_id.setter
    def u_id(self, value : int):
        ...
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
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
    def position(self) -> aspose.cad.fileformats.stp.items.StepAxis2Placement3D:
        ...
    
    @position.setter
    def position(self, value : aspose.cad.fileformats.stp.items.StepAxis2Placement3D):
        ...
    
    @property
    def radius(self) -> float:
        ...
    
    @radius.setter
    def radius(self, value : float):
        ...
    
    ...

class StepStyledItem(StepRepresentationItem):
    '''StyledItem class for STP file.'''
    
    @property
    def item_type(self) -> aspose.cad.fileformats.stp.items.StepItemType:
        ...
    
    @property
    def name(self) -> str:
        ...
    
    @name.setter
    def name(self, value : str):
        ...
    
    @property
    def u_id(self) -> int:
        ...
    
    @u_id.setter
    def u_id(self, value : int):
        ...
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
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
    def styles(self) -> List[aspose.cad.fileformats.stp.items.StepPresentationStyleAssignment]:
        ...
    
    @styles.setter
    def styles(self, value : List[aspose.cad.fileformats.stp.items.StepPresentationStyleAssignment]):
        ...
    
    @property
    def item(self) -> aspose.cad.fileformats.stp.items.StepRepresentationItem:
        ...
    
    @item.setter
    def item(self, value : aspose.cad.fileformats.stp.items.StepRepresentationItem):
        ...
    
    ...

class StepSurface(StepGeometricRepresentationItem):
    '''Surface class for STP file.'''
    
    @property
    def item_type(self) -> aspose.cad.fileformats.stp.items.StepItemType:
        ...
    
    @property
    def name(self) -> str:
        ...
    
    @name.setter
    def name(self, value : str):
        ...
    
    @property
    def u_id(self) -> int:
        ...
    
    @u_id.setter
    def u_id(self, value : int):
        ...
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
        ...
    
    @property
    def area(self) -> float:
        '''Gets the area of the entity.'''
        ...
    
    @property
    def length(self) -> float:
        '''Gets the length of the entity.'''
        ...
    
    ...

class StepSurfaceCurve(StepCurve):
    '''SurfaceCurve class for STP file.'''
    
    @property
    def item_type(self) -> aspose.cad.fileformats.stp.items.StepItemType:
        ...
    
    @property
    def name(self) -> str:
        ...
    
    @name.setter
    def name(self, value : str):
        ...
    
    @property
    def u_id(self) -> int:
        ...
    
    @u_id.setter
    def u_id(self, value : int):
        ...
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
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
    def curve(self) -> aspose.cad.fileformats.stp.items.StepCurve:
        ...
    
    @property
    def associated_geometry(self) -> List[aspose.cad.fileformats.stp.items.StepGeometricRepresentationItem]:
        ...
    
    @associated_geometry.setter
    def associated_geometry(self, value : List[aspose.cad.fileformats.stp.items.StepGeometricRepresentationItem]):
        ...
    
    @property
    def master_representation(self) -> aspose.cad.fileformats.stp.items.StepPreferredSurfaceCurveRepresentation:
        ...
    
    @master_representation.setter
    def master_representation(self, value : aspose.cad.fileformats.stp.items.StepPreferredSurfaceCurveRepresentation):
        ...
    
    ...

class StepSurfaceOfLinearExtrusion(StepSweptSurface):
    '''SurfaceOfLinearExtrusion class for STP file.'''
    
    @property
    def item_type(self) -> aspose.cad.fileformats.stp.items.StepItemType:
        ...
    
    @property
    def name(self) -> str:
        ...
    
    @name.setter
    def name(self, value : str):
        ...
    
    @property
    def u_id(self) -> int:
        ...
    
    @u_id.setter
    def u_id(self, value : int):
        ...
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
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
    def swept_curve(self) -> aspose.cad.fileformats.stp.items.StepCurve:
        ...
    
    @swept_curve.setter
    def swept_curve(self, value : aspose.cad.fileformats.stp.items.StepCurve):
        ...
    
    @property
    def extrusion_axis(self) -> aspose.cad.fileformats.stp.items.StepVector:
        ...
    
    @extrusion_axis.setter
    def extrusion_axis(self, value : aspose.cad.fileformats.stp.items.StepVector):
        ...
    
    ...

class StepSurfaceSideStyle(StepFoundedItem):
    '''SurfaceSideStyle class for STP file.'''
    
    @property
    def item_type(self) -> aspose.cad.fileformats.stp.items.StepItemType:
        ...
    
    @property
    def name(self) -> str:
        ...
    
    @name.setter
    def name(self, value : str):
        ...
    
    @property
    def u_id(self) -> int:
        ...
    
    @u_id.setter
    def u_id(self, value : int):
        ...
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
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
    def style_elements(self) -> List[aspose.cad.fileformats.stp.items.StepFoundedItem]:
        ...
    
    @style_elements.setter
    def style_elements(self, value : List[aspose.cad.fileformats.stp.items.StepFoundedItem]):
        ...
    
    ...

class StepSurfaceStyleFillArea(StepFoundedItem):
    '''SurfaceStyleFillArea class for STP file.'''
    
    @property
    def item_type(self) -> aspose.cad.fileformats.stp.items.StepItemType:
        ...
    
    @property
    def name(self) -> str:
        ...
    
    @name.setter
    def name(self, value : str):
        ...
    
    @property
    def u_id(self) -> int:
        ...
    
    @u_id.setter
    def u_id(self, value : int):
        ...
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
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
    def fill_area(self) -> aspose.cad.fileformats.stp.items.StepFillAreaStyle:
        ...
    
    @fill_area.setter
    def fill_area(self, value : aspose.cad.fileformats.stp.items.StepFillAreaStyle):
        ...
    
    ...

class StepSurfaceStyleUsage(StepFoundedItem):
    '''SurfaceStyleUsage class for STP file.'''
    
    @property
    def item_type(self) -> aspose.cad.fileformats.stp.items.StepItemType:
        ...
    
    @property
    def name(self) -> str:
        ...
    
    @name.setter
    def name(self, value : str):
        ...
    
    @property
    def u_id(self) -> int:
        ...
    
    @u_id.setter
    def u_id(self, value : int):
        ...
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
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
    def side(self) -> aspose.cad.fileformats.stp.items.StepSurfaceSide:
        ...
    
    @side.setter
    def side(self, value : aspose.cad.fileformats.stp.items.StepSurfaceSide):
        ...
    
    @property
    def style(self) -> aspose.cad.fileformats.stp.items.StepSurfaceSideStyle:
        ...
    
    @style.setter
    def style(self, value : aspose.cad.fileformats.stp.items.StepSurfaceSideStyle):
        ...
    
    ...

class StepSweptSurface(StepSurface):
    '''SweptSurface class for STP file.'''
    
    @property
    def item_type(self) -> aspose.cad.fileformats.stp.items.StepItemType:
        ...
    
    @property
    def name(self) -> str:
        ...
    
    @name.setter
    def name(self, value : str):
        ...
    
    @property
    def u_id(self) -> int:
        ...
    
    @u_id.setter
    def u_id(self, value : int):
        ...
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
        ...
    
    @property
    def area(self) -> float:
        '''Gets the area of the entity.'''
        ...
    
    @property
    def length(self) -> float:
        '''Gets the length of the entity.'''
        ...
    
    ...

class StepTessellatedFace(StepTessellatedStructuredItem):
    '''TessellatedFace class for STP file.'''
    
    @property
    def item_type(self) -> aspose.cad.fileformats.stp.items.StepItemType:
        ...
    
    @property
    def name(self) -> str:
        ...
    
    @name.setter
    def name(self, value : str):
        ...
    
    @property
    def u_id(self) -> int:
        ...
    
    @u_id.setter
    def u_id(self, value : int):
        ...
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
        ...
    
    @property
    def area(self) -> float:
        '''Gets the area of the entity.'''
        ...
    
    @property
    def length(self) -> float:
        '''Gets the length of the entity.'''
        ...
    
    ...

class StepTessellatedItem(StepGeometricRepresentationItem):
    '''TessellatedItem class for STP file.'''
    
    @property
    def item_type(self) -> aspose.cad.fileformats.stp.items.StepItemType:
        ...
    
    @property
    def name(self) -> str:
        ...
    
    @name.setter
    def name(self, value : str):
        ...
    
    @property
    def u_id(self) -> int:
        ...
    
    @u_id.setter
    def u_id(self, value : int):
        ...
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
        ...
    
    @property
    def area(self) -> float:
        '''Gets the area of the entity.'''
        ...
    
    @property
    def length(self) -> float:
        '''Gets the length of the entity.'''
        ...
    
    ...

class StepTessellatedShapeRepresentation(StepShapeRepresentation):
    '''TessellatedShapeRepresentation class.'''
    
    @property
    def item_type(self) -> aspose.cad.fileformats.stp.items.StepItemType:
        ...
    
    @property
    def name(self) -> str:
        ...
    
    @name.setter
    def name(self, value : str):
        ...
    
    @property
    def u_id(self) -> int:
        ...
    
    @u_id.setter
    def u_id(self, value : int):
        ...
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
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
    def shape_items(self) -> List[aspose.cad.fileformats.stp.items.StepRepresentationItem]:
        ...
    
    @shape_items.setter
    def shape_items(self, value : List[aspose.cad.fileformats.stp.items.StepRepresentationItem]):
        ...
    
    @property
    def representation_context(self) -> aspose.cad.fileformats.stp.items.StepRepresentationItem:
        ...
    
    ...

class StepTessellatedShell(StepTessellatedItem):
    '''TessellatedShell class for STP file.'''
    
    @property
    def item_type(self) -> aspose.cad.fileformats.stp.items.StepItemType:
        ...
    
    @property
    def name(self) -> str:
        ...
    
    @name.setter
    def name(self, value : str):
        ...
    
    @property
    def u_id(self) -> int:
        ...
    
    @u_id.setter
    def u_id(self, value : int):
        ...
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
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
    def items(self) -> List[aspose.cad.fileformats.stp.items.StepTessellatedStructuredItem]:
        ...
    
    @items.setter
    def items(self, value : List[aspose.cad.fileformats.stp.items.StepTessellatedStructuredItem]):
        ...
    
    @property
    def topological_link(self) -> aspose.cad.fileformats.stp.items.StepConnectedFaceSet:
        ...
    
    @topological_link.setter
    def topological_link(self, value : aspose.cad.fileformats.stp.items.StepConnectedFaceSet):
        ...
    
    ...

class StepTessellatedStructuredItem(StepTessellatedItem):
    '''TessellatedStructuredItem class for STP file.'''
    
    @property
    def item_type(self) -> aspose.cad.fileformats.stp.items.StepItemType:
        ...
    
    @property
    def name(self) -> str:
        ...
    
    @name.setter
    def name(self, value : str):
        ...
    
    @property
    def u_id(self) -> int:
        ...
    
    @u_id.setter
    def u_id(self, value : int):
        ...
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
        ...
    
    @property
    def area(self) -> float:
        '''Gets the area of the entity.'''
        ...
    
    @property
    def length(self) -> float:
        '''Gets the length of the entity.'''
        ...
    
    ...

class StepTessellatedSurfaceSet(StepTessellatedItem):
    '''TessellatedSurfaceSet class for STP file.'''
    
    @property
    def item_type(self) -> aspose.cad.fileformats.stp.items.StepItemType:
        ...
    
    @property
    def name(self) -> str:
        ...
    
    @name.setter
    def name(self, value : str):
        ...
    
    @property
    def u_id(self) -> int:
        ...
    
    @u_id.setter
    def u_id(self, value : int):
        ...
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
        ...
    
    @property
    def area(self) -> float:
        '''Gets the area of the entity.'''
        ...
    
    @property
    def length(self) -> float:
        '''Gets the length of the entity.'''
        ...
    
    ...

class StepTopologicalRepresentationItem(StepRepresentationItem):
    '''TopologicalRepresentationItem class.'''
    
    @property
    def item_type(self) -> aspose.cad.fileformats.stp.items.StepItemType:
        ...
    
    @property
    def name(self) -> str:
        ...
    
    @name.setter
    def name(self, value : str):
        ...
    
    @property
    def u_id(self) -> int:
        ...
    
    @u_id.setter
    def u_id(self, value : int):
        ...
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
        ...
    
    @property
    def area(self) -> float:
        '''Gets the area of the entity.'''
        ...
    
    @property
    def length(self) -> float:
        '''Gets the length of the entity.'''
        ...
    
    ...

class StepToroidalSurface(StepSurface):
    '''ToroidalSurface class for STP file.'''
    
    @property
    def item_type(self) -> aspose.cad.fileformats.stp.items.StepItemType:
        ...
    
    @property
    def name(self) -> str:
        ...
    
    @name.setter
    def name(self, value : str):
        ...
    
    @property
    def u_id(self) -> int:
        ...
    
    @u_id.setter
    def u_id(self, value : int):
        ...
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
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
    def toroidal_surface(self) -> aspose.cad.fileformats.stp.items.StepToroidalSurface:
        ...
    
    @property
    def major_radius(self) -> float:
        ...
    
    @major_radius.setter
    def major_radius(self, value : float):
        ...
    
    @property
    def minor_radius(self) -> float:
        ...
    
    @minor_radius.setter
    def minor_radius(self, value : float):
        ...
    
    @property
    def axis(self) -> aspose.cad.fileformats.stp.items.StepAxis2Placement3D:
        ...
    
    @axis.setter
    def axis(self, value : aspose.cad.fileformats.stp.items.StepAxis2Placement3D):
        ...
    
    ...

class StepTransformation(StepRepresentationItem):
    '''Transformation class for STP.'''
    
    @property
    def item_type(self) -> aspose.cad.fileformats.stp.items.StepItemType:
        ...
    
    @property
    def name(self) -> str:
        ...
    
    @name.setter
    def name(self, value : str):
        ...
    
    @property
    def u_id(self) -> int:
        ...
    
    @u_id.setter
    def u_id(self, value : int):
        ...
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
        ...
    
    @property
    def area(self) -> float:
        '''Gets the area of the entity.'''
        ...
    
    @property
    def length(self) -> float:
        '''Gets the length of the entity.'''
        ...
    
    ...

class StepTriangulatedFace(StepTessellatedFace):
    '''TriangulatedFace class for STP file.
    Class represents simple tessellated face.
    A tessellated geometry can be defined either by a TRIANGULATED_FACE or by
    a COMPLEX_TRIANGULATED_FACE. These entities are similar to the entities
    TRIANGULATED_SURFACE_SET and COMPLEX_TRIANGULATED_SURFACE_SET.
    The only difference between a tessellated face and a tessellated surface set
    is that the tesselated face has an additional attribute GeometricLink.
    This optional attribute can be used for preserving the exact definition of
    the underlying exact geometry.'''
    
    @property
    def item_type(self) -> aspose.cad.fileformats.stp.items.StepItemType:
        ...
    
    @property
    def name(self) -> str:
        ...
    
    @name.setter
    def name(self, value : str):
        ...
    
    @property
    def u_id(self) -> int:
        ...
    
    @u_id.setter
    def u_id(self, value : int):
        ...
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
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
    def coordinates(self) -> aspose.cad.fileformats.stp.items.StepCoordinatesList:
        ...
    
    @coordinates.setter
    def coordinates(self, value : aspose.cad.fileformats.stp.items.StepCoordinatesList):
        ...
    
    @property
    def pn_max(self) -> int:
        ...
    
    @pn_max.setter
    def pn_max(self, value : int):
        ...
    
    @property
    def normals(self) -> List[List[float]]:
        ...
    
    @normals.setter
    def normals(self, value : List[List[float]]):
        ...
    
    @property
    def geometric_link(self) -> aspose.cad.fileformats.stp.items.StepRepresentationItem:
        ...
    
    @geometric_link.setter
    def geometric_link(self, value : aspose.cad.fileformats.stp.items.StepRepresentationItem):
        ...
    
    @property
    def pn_index(self) -> List[int]:
        ...
    
    @pn_index.setter
    def pn_index(self, value : List[int]):
        ...
    
    @property
    def triangles(self) -> List[List[int]]:
        ...
    
    @triangles.setter
    def triangles(self, value : List[List[int]]):
        ...
    
    ...

class StepTriangulatedSurfaceSet(StepTessellatedItem):
    '''TriangulatedSurfaceSet class for STP file.
    Class represents simple tessellated surface set.
    A tessellated geometry can be defined either by a TRIANGULATED_FACE or by
    a COMPLEX_TRIANGULATED_FACE. These entities are similar to the entities
    TRIANGULATED_SURFACE_SET and COMPLEX_TRIANGULATED_SURFACE_SET.
    The only difference between a tessellated face and a tessellated surface set
    is that the tesselated face has an additional attribute GeometricLink.
    This optional attribute can be used for preserving the exact definition of
    the underlying exact geometry.'''
    
    @property
    def item_type(self) -> aspose.cad.fileformats.stp.items.StepItemType:
        ...
    
    @property
    def name(self) -> str:
        ...
    
    @name.setter
    def name(self, value : str):
        ...
    
    @property
    def u_id(self) -> int:
        ...
    
    @u_id.setter
    def u_id(self, value : int):
        ...
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
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
    def coordinates(self) -> aspose.cad.fileformats.stp.items.StepCoordinatesList:
        ...
    
    @coordinates.setter
    def coordinates(self, value : aspose.cad.fileformats.stp.items.StepCoordinatesList):
        ...
    
    @property
    def pn_max(self) -> int:
        ...
    
    @pn_max.setter
    def pn_max(self, value : int):
        ...
    
    @property
    def normals(self) -> List[List[float]]:
        ...
    
    @normals.setter
    def normals(self, value : List[List[float]]):
        ...
    
    @property
    def pn_index(self) -> List[int]:
        ...
    
    @pn_index.setter
    def pn_index(self, value : List[int]):
        ...
    
    @property
    def triangles(self) -> List[List[int]]:
        ...
    
    @triangles.setter
    def triangles(self, value : List[List[int]]):
        ...
    
    ...

class StepTrimmedCurve(StepBoundedCurve):
    '''TrimmedCurve class for STP file.'''
    
    @property
    def item_type(self) -> aspose.cad.fileformats.stp.items.StepItemType:
        ...
    
    @property
    def name(self) -> str:
        ...
    
    @name.setter
    def name(self, value : str):
        ...
    
    @property
    def u_id(self) -> int:
        ...
    
    @u_id.setter
    def u_id(self, value : int):
        ...
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
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
    def curve(self) -> aspose.cad.fileformats.stp.items.StepCurve:
        ...
    
    @curve.setter
    def curve(self, value : aspose.cad.fileformats.stp.items.StepCurve):
        ...
    
    @property
    def trim_1_point(self) -> aspose.cad.fileformats.stp.items.StepCartesianPoint:
        ...
    
    @trim_1_point.setter
    def trim_1_point(self, value : aspose.cad.fileformats.stp.items.StepCartesianPoint):
        ...
    
    @property
    def trim_1_param(self) -> float:
        ...
    
    @trim_1_param.setter
    def trim_1_param(self, value : float):
        ...
    
    @property
    def trim_2_point(self) -> aspose.cad.fileformats.stp.items.StepCartesianPoint:
        ...
    
    @trim_2_point.setter
    def trim_2_point(self, value : aspose.cad.fileformats.stp.items.StepCartesianPoint):
        ...
    
    @property
    def trim_2_param(self) -> float:
        ...
    
    @trim_2_param.setter
    def trim_2_param(self, value : float):
        ...
    
    @property
    def sense_agreement(self) -> bool:
        ...
    
    @sense_agreement.setter
    def sense_agreement(self, value : bool):
        ...
    
    @property
    def trimming_preference(self) -> aspose.cad.fileformats.stp.items.StepTrimmingPreference:
        ...
    
    @trimming_preference.setter
    def trimming_preference(self, value : aspose.cad.fileformats.stp.items.StepTrimmingPreference):
        ...
    
    ...

class StepTriple(StepPoint):
    '''Triple point class for STP file.'''
    
    def equals(self, other : aspose.cad.fileformats.stp.items.StepTriple) -> bool:
        ...
    
    @property
    def item_type(self) -> aspose.cad.fileformats.stp.items.StepItemType:
        ...
    
    @property
    def name(self) -> str:
        ...
    
    @name.setter
    def name(self, value : str):
        ...
    
    @property
    def u_id(self) -> int:
        ...
    
    @u_id.setter
    def u_id(self, value : int):
        ...
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
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
    def x(self) -> float:
        ...
    
    @x.setter
    def x(self, value : float):
        ...
    
    @property
    def y(self) -> float:
        ...
    
    @y.setter
    def y(self, value : float):
        ...
    
    @property
    def z(self) -> float:
        ...
    
    @z.setter
    def z(self, value : float):
        ...
    
    ...

class StepValueRepresentationItem(StepSurface):
    '''ValueRepresentationItem class.'''
    
    @property
    def item_type(self) -> aspose.cad.fileformats.stp.items.StepItemType:
        ...
    
    @property
    def name(self) -> str:
        ...
    
    @name.setter
    def name(self, value : str):
        ...
    
    @property
    def u_id(self) -> int:
        ...
    
    @u_id.setter
    def u_id(self, value : int):
        ...
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
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
    def value_representation_item(self) -> aspose.cad.fileformats.stp.items.StepValueRepresentationItem:
        ...
    
    @property
    def count_measure(self) -> float:
        ...
    
    @count_measure.setter
    def count_measure(self, value : float):
        ...
    
    ...

class StepVector(StepGeometricRepresentationItem):
    '''Vector class for STP file.'''
    
    @property
    def item_type(self) -> aspose.cad.fileformats.stp.items.StepItemType:
        ...
    
    @property
    def name(self) -> str:
        ...
    
    @name.setter
    def name(self, value : str):
        ...
    
    @property
    def u_id(self) -> int:
        ...
    
    @u_id.setter
    def u_id(self, value : int):
        ...
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
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
    def direction(self) -> aspose.cad.fileformats.stp.items.StepDirection:
        ...
    
    @direction.setter
    def direction(self, value : aspose.cad.fileformats.stp.items.StepDirection):
        ...
    
    @property
    def len(self) -> float:
        ...
    
    @len.setter
    def len(self, value : float):
        ...
    
    ...

class StepVertex(StepTopologicalRepresentationItem):
    '''Vertex class for STP file.'''
    
    @property
    def item_type(self) -> aspose.cad.fileformats.stp.items.StepItemType:
        ...
    
    @property
    def name(self) -> str:
        ...
    
    @name.setter
    def name(self, value : str):
        ...
    
    @property
    def u_id(self) -> int:
        ...
    
    @u_id.setter
    def u_id(self, value : int):
        ...
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
        ...
    
    @property
    def area(self) -> float:
        '''Gets the area of the entity.'''
        ...
    
    @property
    def length(self) -> float:
        '''Gets the length of the entity.'''
        ...
    
    ...

class StepVertexLoop(StepLoop):
    '''VertexLoop class for STP file.'''
    
    @property
    def item_type(self) -> aspose.cad.fileformats.stp.items.StepItemType:
        ...
    
    @property
    def name(self) -> str:
        ...
    
    @name.setter
    def name(self, value : str):
        ...
    
    @property
    def u_id(self) -> int:
        ...
    
    @u_id.setter
    def u_id(self, value : int):
        ...
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
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
    def loop_vertex(self) -> aspose.cad.fileformats.stp.items.StepVertex:
        ...
    
    @loop_vertex.setter
    def loop_vertex(self, value : aspose.cad.fileformats.stp.items.StepVertex):
        ...
    
    ...

class StepVertexPoint(StepVertex):
    '''VertexPoint class for STP file.'''
    
    @property
    def item_type(self) -> aspose.cad.fileformats.stp.items.StepItemType:
        ...
    
    @property
    def name(self) -> str:
        ...
    
    @name.setter
    def name(self, value : str):
        ...
    
    @property
    def u_id(self) -> int:
        ...
    
    @u_id.setter
    def u_id(self, value : int):
        ...
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
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
    def location(self) -> aspose.cad.fileformats.stp.items.StepCartesianPoint:
        ...
    
    @location.setter
    def location(self, value : aspose.cad.fileformats.stp.items.StepCartesianPoint):
        ...
    
    ...

class StepBSplineCurveForm:
    '''BSplineCurveForm enum for STP file.'''
    
    @classmethod
    @property
    def POLYLINE(cls) -> StepBSplineCurveForm:
        ...
    
    @classmethod
    @property
    def CIRCULAR_ARC(cls) -> StepBSplineCurveForm:
        ...
    
    @classmethod
    @property
    def ELLIPTICAL_ARC(cls) -> StepBSplineCurveForm:
        ...
    
    @classmethod
    @property
    def PARABOLIC_ARC(cls) -> StepBSplineCurveForm:
        ...
    
    @classmethod
    @property
    def HYPERBOLIC_ARC(cls) -> StepBSplineCurveForm:
        ...
    
    @classmethod
    @property
    def UNSPECIFIED(cls) -> StepBSplineCurveForm:
        ...
    
    ...

class StepBSplineSurfaceForm:
    '''BSplineSurfaceForm enum for STP file.'''
    
    @classmethod
    @property
    def PLANE_SURF(cls) -> StepBSplineSurfaceForm:
        ...
    
    @classmethod
    @property
    def CYLINDRICAL_SURF(cls) -> StepBSplineSurfaceForm:
        ...
    
    @classmethod
    @property
    def CONICAL_SURF(cls) -> StepBSplineSurfaceForm:
        ...
    
    @classmethod
    @property
    def SPHERICAL_SURF(cls) -> StepBSplineSurfaceForm:
        ...
    
    @classmethod
    @property
    def TOROIDAL_SURF(cls) -> StepBSplineSurfaceForm:
        ...
    
    @classmethod
    @property
    def SURF_OF_REVOLUTION(cls) -> StepBSplineSurfaceForm:
        ...
    
    @classmethod
    @property
    def RULED_SURF(cls) -> StepBSplineSurfaceForm:
        ...
    
    @classmethod
    @property
    def GENERALISED_CONE(cls) -> StepBSplineSurfaceForm:
        ...
    
    @classmethod
    @property
    def QUADRIC_SURF(cls) -> StepBSplineSurfaceForm:
        ...
    
    @classmethod
    @property
    def SURF_OF_LINEAR_EXTRUSION(cls) -> StepBSplineSurfaceForm:
        ...
    
    @classmethod
    @property
    def UNSPECIFIED(cls) -> StepBSplineSurfaceForm:
        ...
    
    ...

class StepItemType:
    '''ItemType RepresentationItem enum for STP file.'''
    
    @classmethod
    @property
    def ADVANCED_FACE(cls) -> StepItemType:
        ...
    
    @classmethod
    @property
    def AXIS_PLACEMENT_2D(cls) -> StepItemType:
        ...
    
    @classmethod
    @property
    def AXIS_PLACEMENT_3D(cls) -> StepItemType:
        ...
    
    @classmethod
    @property
    def B_SPLINE_CURVE_WITH_KNOTS(cls) -> StepItemType:
        ...
    
    @classmethod
    @property
    def CARTESIAN_POINT(cls) -> StepItemType:
        ...
    
    @classmethod
    @property
    def CIRCLE(cls) -> StepItemType:
        ...
    
    @classmethod
    @property
    def COORDINATES_LIST(cls) -> StepItemType:
        ...
    
    @classmethod
    @property
    def CYLINDRICAL_SURFACE(cls) -> StepItemType:
        ...
    
    @classmethod
    @property
    def SURFACE_OF_LINEAR_EXTRUSION(cls) -> StepItemType:
        ...
    
    @classmethod
    @property
    def DIRECTION(cls) -> StepItemType:
        ...
    
    @classmethod
    @property
    def EDGE_CURVE(cls) -> StepItemType:
        ...
    
    @classmethod
    @property
    def EDGE_LOOP(cls) -> StepItemType:
        ...
    
    @classmethod
    @property
    def ELLIPSE(cls) -> StepItemType:
        ...
    
    @classmethod
    @property
    def FACE(cls) -> StepItemType:
        ...
    
    @classmethod
    @property
    def FACE_BOUND(cls) -> StepItemType:
        ...
    
    @classmethod
    @property
    def FACE_OUTER_BOUND(cls) -> StepItemType:
        ...
    
    @classmethod
    @property
    def FACE_SURFACE(cls) -> StepItemType:
        ...
    
    @classmethod
    @property
    def FACETED_BREP(cls) -> StepItemType:
        ...
    
    @classmethod
    @property
    def FACETED_BREP_SHAPE_REPRESENTATION(cls) -> StepItemType:
        ...
    
    @classmethod
    @property
    def MANIFOLD_SURFACE_SHAPE_REPRESENTATION(cls) -> StepItemType:
        ...
    
    @classmethod
    @property
    def SHELL_BASED_SURFACE_MODEL(cls) -> StepItemType:
        ...
    
    @classmethod
    @property
    def LINE(cls) -> StepItemType:
        ...
    
    @classmethod
    @property
    def ORIENTED_EDGE(cls) -> StepItemType:
        ...
    
    @classmethod
    @property
    def PLANE(cls) -> StepItemType:
        ...
    
    @classmethod
    @property
    def VECTOR(cls) -> StepItemType:
        ...
    
    @classmethod
    @property
    def VERTEX_POINT(cls) -> StepItemType:
        ...
    
    @classmethod
    @property
    def VERTEX_LOOP(cls) -> StepItemType:
        ...
    
    @classmethod
    @property
    def SURFACE_CURVE(cls) -> StepItemType:
        ...
    
    @classmethod
    @property
    def P_CURVE(cls) -> StepItemType:
        ...
    
    @classmethod
    @property
    def DEFINITIONAL_REPRESENTATION(cls) -> StepItemType:
        ...
    
    @classmethod
    @property
    def TOROIDAL_SURFACE(cls) -> StepItemType:
        ...
    
    @classmethod
    @property
    def B_SPLINE_SURFACE(cls) -> StepItemType:
        ...
    
    @classmethod
    @property
    def B_SPLINE_SURFACE_WITH_KNOTS(cls) -> StepItemType:
        ...
    
    @classmethod
    @property
    def RATIONAL_B_SPLINE_SURFACE(cls) -> StepItemType:
        ...
    
    @classmethod
    @property
    def CONICAL_SURFACE(cls) -> StepItemType:
        ...
    
    @classmethod
    @property
    def SPHERICAL_SURFACE(cls) -> StepItemType:
        ...
    
    @classmethod
    @property
    def BOUNDED_SURFACE(cls) -> StepItemType:
        ...
    
    @classmethod
    @property
    def VALUE_REPRESENTATION_ITEM(cls) -> StepItemType:
        ...
    
    @classmethod
    @property
    def REPRESENTATION(cls) -> StepItemType:
        ...
    
    @classmethod
    @property
    def SHAPE_REPRESENTATION_RELATIONSHIP(cls) -> StepItemType:
        ...
    
    @classmethod
    @property
    def ADAVNCED_BREP_SHAPE_REPRESENTATION(cls) -> StepItemType:
        ...
    
    @classmethod
    @property
    def MANIFOLD_SOLID_BREP(cls) -> StepItemType:
        ...
    
    @classmethod
    @property
    def CLOSED_SHELL(cls) -> StepItemType:
        ...
    
    @classmethod
    @property
    def OPEN_SHELL(cls) -> StepItemType:
        ...
    
    @classmethod
    @property
    def SHAPE_DEFINITION_REPRESENTATION(cls) -> StepItemType:
        ...
    
    @classmethod
    @property
    def PRODUCT_DEFINITION_SHAPE(cls) -> StepItemType:
        ...
    
    @classmethod
    @property
    def SHAPE_REPRESENTATION(cls) -> StepItemType:
        ...
    
    @classmethod
    @property
    def GEOMETRICALLY_BOUNDED_WIREFRAME_SHAPE_REPRESENTATION(cls) -> StepItemType:
        ...
    
    @classmethod
    @property
    def TRIANGULATED_SURFACE_SET(cls) -> StepItemType:
        ...
    
    @classmethod
    @property
    def COMPLEX_TRIANGULATED_SURFACE_SET(cls) -> StepItemType:
        ...
    
    @classmethod
    @property
    def TRIANGULATED_FACE(cls) -> StepItemType:
        ...
    
    @classmethod
    @property
    def COMPLEX_TRIANGULATED_FACE(cls) -> StepItemType:
        ...
    
    @classmethod
    @property
    def TESSELLATED_SHELL(cls) -> StepItemType:
        ...
    
    @classmethod
    @property
    def TESSELLATED_SHAPE_REPRESENTATION(cls) -> StepItemType:
        ...
    
    @classmethod
    @property
    def GEOMETRIC_CURVE_SET(cls) -> StepItemType:
        ...
    
    @classmethod
    @property
    def POLY_LOOP(cls) -> StepItemType:
        ...
    
    @classmethod
    @property
    def PRODUCT(cls) -> StepItemType:
        ...
    
    @classmethod
    @property
    def PRODUCT_DEFINITION(cls) -> StepItemType:
        ...
    
    @classmethod
    @property
    def PRODUCT_DEFINITION_FORMATION(cls) -> StepItemType:
        ...
    
    @classmethod
    @property
    def TRIMMED_CURVE(cls) -> StepItemType:
        ...
    
    @classmethod
    @property
    def STYLED_ITEM(cls) -> StepItemType:
        ...
    
    @classmethod
    @property
    def PRESENTATION_STYLE_ASSIGNMENT(cls) -> StepItemType:
        ...
    
    @classmethod
    @property
    def SURFACE_STYLE_USAGE(cls) -> StepItemType:
        ...
    
    @classmethod
    @property
    def SURFACE_SIDE_STYLE(cls) -> StepItemType:
        ...
    
    @classmethod
    @property
    def SURFACE_STYLE_FILL_AREA(cls) -> StepItemType:
        ...
    
    @classmethod
    @property
    def FILL_AREA_STYLE(cls) -> StepItemType:
        ...
    
    @classmethod
    @property
    def FILL_AREA_STYLE_COLOUR(cls) -> StepItemType:
        ...
    
    @classmethod
    @property
    def COLOUR_RGB(cls) -> StepItemType:
        ...
    
    @classmethod
    @property
    def DRAUGHTING_PRE_DEFINED_COLOUR(cls) -> StepItemType:
        ...
    
    @classmethod
    @property
    def DRAUGHTING_PRE_DEFINED_CURVE_FONT(cls) -> StepItemType:
        ...
    
    @classmethod
    @property
    def REPRESENTATION_RELATIONSHIP(cls) -> StepItemType:
        ...
    
    @classmethod
    @property
    def REPRESENTATION_RELATIONSHIP_WITH_TRANSFORMATION(cls) -> StepItemType:
        ...
    
    @classmethod
    @property
    def COMPLEX_ITEM(cls) -> StepItemType:
        ...
    
    @classmethod
    @property
    def ITEM_DEFINED_TRANSFORMATION(cls) -> StepItemType:
        ...
    
    @classmethod
    @property
    def COMPOSITE_CURVE(cls) -> StepItemType:
        ...
    
    @classmethod
    @property
    def COMPOSITE_CURVE_SEGMENT(cls) -> StepItemType:
        ...
    
    @classmethod
    @property
    def CURVE_STYLE(cls) -> StepItemType:
        ...
    
    ...

class StepKnotType:
    '''KnotType enum for STP file.'''
    
    @classmethod
    @property
    def UNIFORM_KNOTS(cls) -> StepKnotType:
        ...
    
    @classmethod
    @property
    def QUASI_UNIFORM_KNOTS(cls) -> StepKnotType:
        ...
    
    @classmethod
    @property
    def PIECEWISE_BEZIER_KNOTS(cls) -> StepKnotType:
        ...
    
    @classmethod
    @property
    def UNSPECIFIED(cls) -> StepKnotType:
        ...
    
    ...

class StepPreferredSurfaceCurveRepresentation:
    '''PreferredSurfaceCurveRepresentation enum for STP file.'''
    
    @classmethod
    @property
    def CURVE_3D(cls) -> StepPreferredSurfaceCurveRepresentation:
        ...
    
    @classmethod
    @property
    def PCURVE_S1(cls) -> StepPreferredSurfaceCurveRepresentation:
        ...
    
    @classmethod
    @property
    def PCURVE_S2(cls) -> StepPreferredSurfaceCurveRepresentation:
        ...
    
    ...

class StepSurfaceSide:
    '''SurfaceSide enum for STP file.'''
    
    @classmethod
    @property
    def POSITIVE(cls) -> StepSurfaceSide:
        ...
    
    @classmethod
    @property
    def NEGATIVE(cls) -> StepSurfaceSide:
        ...
    
    @classmethod
    @property
    def BOTH(cls) -> StepSurfaceSide:
        ...
    
    ...

class StepTransitionCode:
    '''TransitionCode enum for STP file.'''
    
    @classmethod
    @property
    def DISCONTINUOUS(cls) -> StepTransitionCode:
        ...
    
    @classmethod
    @property
    def CONTINUOUS(cls) -> StepTransitionCode:
        ...
    
    @classmethod
    @property
    def CONT_SAME_GRADIENT(cls) -> StepTransitionCode:
        ...
    
    @classmethod
    @property
    def CONT_SAME_GRADIENT_SAME_CURVATURE(cls) -> StepTransitionCode:
        ...
    
    ...

class StepTrimmingPreference:
    '''TrimmingPreference enum for STP file.'''
    
    @classmethod
    @property
    def CARTESIAN(cls) -> StepTrimmingPreference:
        ...
    
    @classmethod
    @property
    def PARAMETER(cls) -> StepTrimmingPreference:
        ...
    
    @classmethod
    @property
    def UNSPECIFIED(cls) -> StepTrimmingPreference:
        ...
    
    ...

