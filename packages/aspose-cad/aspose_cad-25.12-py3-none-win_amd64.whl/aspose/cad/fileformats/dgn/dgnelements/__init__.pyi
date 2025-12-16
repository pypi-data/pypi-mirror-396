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

class Dgn3DSurfaceElement(DgnCompoundElement):
    '''Represents 3d surface or 3d solid element'''
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
        ...
    
    @property
    def metadata(self) -> aspose.cad.fileformats.dgn.DgnElementMetadata:
        '''Gets element metadata'''
        ...
    
    @property
    def min_point(self) -> aspose.cad.fileformats.cad.cadobjects.Cad3DPoint:
        ...
    
    @property
    def max_point(self) -> aspose.cad.fileformats.cad.cadobjects.Cad3DPoint:
        ...
    
    @property
    def total_length(self) -> int:
        ...
    
    @property
    def elements_count(self) -> int:
        ...
    
    @property
    def elements(self) -> Iterable[aspose.cad.fileformats.dgn.dgnelements.DgnDrawableEntityBase]:
        '''Gets related elements'''
        ...
    
    @property
    def surface_type(self) -> aspose.cad.fileformats.dgn.DgnSurface3DType:
        ...
    
    @property
    def creation_method(self) -> aspose.cad.fileformats.dgn.DgnSurfaceCreationMethod:
        ...
    
    @property
    def bound_elements_count(self) -> int:
        ...
    
    ...

class DgnArcBasedElement(DgnDrawingElementBaseQuaternion):
    '''Represents base class for arc-based elements'''
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
        ...
    
    @property
    def metadata(self) -> aspose.cad.fileformats.dgn.DgnElementMetadata:
        '''Gets element metadata'''
        ...
    
    @property
    def min_point(self) -> aspose.cad.fileformats.cad.cadobjects.Cad3DPoint:
        ...
    
    @property
    def max_point(self) -> aspose.cad.fileformats.cad.cadobjects.Cad3DPoint:
        ...
    
    @property
    def quaternion_rotations(self) -> aspose.cad.fileformats.dgn.dgntransform.DgnQuaternion:
        ...
    
    @property
    def origin(self) -> aspose.cad.fileformats.dgn.DgnPoint:
        '''Gets Origin of ellipse'''
        ...
    
    @property
    def primary_axis(self) -> float:
        ...
    
    @property
    def secondary_axis(self) -> float:
        ...
    
    @property
    def rotation(self) -> float:
        '''Gets Counterclockwise rotation in degrees'''
        ...
    
    @property
    def start_angle(self) -> float:
        ...
    
    @property
    def sweep_angle(self) -> float:
        ...
    
    ...

class DgnArcElement(DgnArcBasedElement):
    '''Represents arc element'''
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
        ...
    
    @property
    def metadata(self) -> aspose.cad.fileformats.dgn.DgnElementMetadata:
        '''Gets element metadata'''
        ...
    
    @property
    def min_point(self) -> aspose.cad.fileformats.cad.cadobjects.Cad3DPoint:
        ...
    
    @property
    def max_point(self) -> aspose.cad.fileformats.cad.cadobjects.Cad3DPoint:
        ...
    
    @property
    def quaternion_rotations(self) -> aspose.cad.fileformats.dgn.dgntransform.DgnQuaternion:
        ...
    
    @property
    def origin(self) -> aspose.cad.fileformats.dgn.DgnPoint:
        '''Gets Origin of ellipse'''
        ...
    
    @property
    def primary_axis(self) -> float:
        ...
    
    @property
    def secondary_axis(self) -> float:
        ...
    
    @property
    def rotation(self) -> float:
        '''Gets Counterclockwise rotation in degrees'''
        ...
    
    @property
    def start_angle(self) -> float:
        ...
    
    @property
    def sweep_angle(self) -> float:
        ...
    
    ...

class DgnBSplineCurveElement(DgnDrawableEntityBase):
    '''B-spline curve element'''
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
        ...
    
    @property
    def metadata(self) -> aspose.cad.fileformats.dgn.DgnElementMetadata:
        '''Gets element metadata'''
        ...
    
    @property
    def min_point(self) -> aspose.cad.fileformats.cad.cadobjects.Cad3DPoint:
        ...
    
    @property
    def max_point(self) -> aspose.cad.fileformats.cad.cadobjects.Cad3DPoint:
        ...
    
    @property
    def order(self) -> byte:
        '''Gets B-spline order: 2-15'''
        ...
    
    @property
    def is_closed(self) -> bool:
        ...
    
    @property
    def is_rational(self) -> bool:
        ...
    
    @property
    def curve_type(self) -> byte:
        ...
    
    @property
    def knot_element(self) -> aspose.cad.fileformats.dgn.dgnelements.DgnSplineKnotElement:
        ...
    
    @knot_element.setter
    def knot_element(self, value : aspose.cad.fileformats.dgn.dgnelements.DgnSplineKnotElement):
        ...
    
    @property
    def pole_element(self) -> aspose.cad.fileformats.dgn.dgnelements.DgnSplinePoleElement:
        ...
    
    @pole_element.setter
    def pole_element(self, value : aspose.cad.fileformats.dgn.dgnelements.DgnSplinePoleElement):
        ...
    
    ...

class DgnCellHeaderElement(DgnDrawableEntityBase):
    '''Represents cell header element'''
    
    def add_child(self, child : aspose.cad.fileformats.dgn.dgnelements.DgnElementBase) -> None:
        '''Adds element as a child
        
        :param child: element to add as a child'''
        ...
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> List[aspose.cad.fileformats.dgn.dgnelements.DgnDrawableEntityBase]:
        '''Gets childs of the composite element'''
        ...
    
    @property
    def metadata(self) -> aspose.cad.fileformats.dgn.DgnElementMetadata:
        '''Gets element metadata'''
        ...
    
    @property
    def min_point(self) -> aspose.cad.fileformats.cad.cadobjects.Cad3DPoint:
        ...
    
    @property
    def max_point(self) -> aspose.cad.fileformats.cad.cadobjects.Cad3DPoint:
        ...
    
    @property
    def name(self) -> str:
        '''Gets cell name'''
        ...
    
    @property
    def class_bitmap(self) -> int:
        ...
    
    @property
    def levels(self) -> List[int]:
        '''Gets array of levels used in cell'''
        ...
    
    @property
    def range_block_low(self) -> aspose.cad.fileformats.dgn.DgnPoint:
        ...
    
    @property
    def range_block_hi(self) -> aspose.cad.fileformats.dgn.DgnPoint:
        ...
    
    @property
    def trans_formation_matrix(self) -> List[float]:
        ...
    
    @property
    def origin(self) -> aspose.cad.fileformats.dgn.DgnPoint:
        '''Gets cell's origin point'''
        ...
    
    @property
    def x_scale(self) -> float:
        ...
    
    @property
    def y_scale(self) -> float:
        ...
    
    @property
    def rotation(self) -> float:
        '''Gets cell's rotation angle'''
        ...
    
    ...

class DgnCompoundElement(DgnDrawableEntityBase):
    '''Represents compound element'''
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
        ...
    
    @property
    def metadata(self) -> aspose.cad.fileformats.dgn.DgnElementMetadata:
        '''Gets element metadata'''
        ...
    
    @property
    def min_point(self) -> aspose.cad.fileformats.cad.cadobjects.Cad3DPoint:
        ...
    
    @property
    def max_point(self) -> aspose.cad.fileformats.cad.cadobjects.Cad3DPoint:
        ...
    
    @property
    def total_length(self) -> int:
        ...
    
    @property
    def elements_count(self) -> int:
        ...
    
    @property
    def elements(self) -> Iterable[aspose.cad.fileformats.dgn.dgnelements.DgnDrawableEntityBase]:
        '''Gets related elements'''
        ...
    
    ...

class DgnConeElement(DgnDrawingElementBaseQuaternion):
    '''Represents Cone element'''
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
        ...
    
    @property
    def metadata(self) -> aspose.cad.fileformats.dgn.DgnElementMetadata:
        '''Gets element metadata'''
        ...
    
    @property
    def min_point(self) -> aspose.cad.fileformats.cad.cadobjects.Cad3DPoint:
        ...
    
    @property
    def max_point(self) -> aspose.cad.fileformats.cad.cadobjects.Cad3DPoint:
        ...
    
    @property
    def quaternion_rotations(self) -> aspose.cad.fileformats.dgn.dgntransform.DgnQuaternion:
        ...
    
    @property
    def first_circle(self) -> aspose.cad.fileformats.dgn.DgnCircle:
        ...
    
    @property
    def second_circle(self) -> aspose.cad.fileformats.dgn.DgnCircle:
        ...
    
    ...

class DgnCoreElement(DgnElementBase):
    '''Represents 'core' element'''
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
        ...
    
    @property
    def metadata(self) -> aspose.cad.fileformats.dgn.DgnElementMetadata:
        '''Gets element metadata'''
        ...
    
    ...

class DgnCurveLineElement(DgnLineElement):
    '''Represents curve line element element'''
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
        ...
    
    @property
    def metadata(self) -> aspose.cad.fileformats.dgn.DgnElementMetadata:
        '''Gets element metadata'''
        ...
    
    @property
    def min_point(self) -> aspose.cad.fileformats.cad.cadobjects.Cad3DPoint:
        ...
    
    @property
    def max_point(self) -> aspose.cad.fileformats.cad.cadobjects.Cad3DPoint:
        ...
    
    @property
    def vertices(self) -> List[aspose.cad.fileformats.dgn.DgnPoint]:
        '''Gets vertices of the line'''
        ...
    
    ...

class DgnDigitizerElement(DgnElementBase):
    '''Represents digitizer element'''
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
        ...
    
    @property
    def metadata(self) -> aspose.cad.fileformats.dgn.DgnElementMetadata:
        '''Gets element metadata'''
        ...
    
    ...

class DgnDimensionElement(DgnDrawableEntityBase):
    '''Represents dimension'''
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
        ...
    
    @property
    def metadata(self) -> aspose.cad.fileformats.dgn.DgnElementMetadata:
        '''Gets element metadata'''
        ...
    
    @property
    def min_point(self) -> aspose.cad.fileformats.cad.cadobjects.Cad3DPoint:
        ...
    
    @property
    def max_point(self) -> aspose.cad.fileformats.cad.cadobjects.Cad3DPoint:
        ...
    
    ...

class DgnDrawableEntityBase(DgnElementBase):
    '''Represents base class for drawing Dgn elements'''
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
        ...
    
    @property
    def metadata(self) -> aspose.cad.fileformats.dgn.DgnElementMetadata:
        '''Gets element metadata'''
        ...
    
    @property
    def min_point(self) -> aspose.cad.fileformats.cad.cadobjects.Cad3DPoint:
        ...
    
    @property
    def max_point(self) -> aspose.cad.fileformats.cad.cadobjects.Cad3DPoint:
        ...
    
    ...

class DgnDrawingElementBaseQuaternion(DgnDrawableEntityBase):
    '''DgnDrawingElementBase class'''
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
        ...
    
    @property
    def metadata(self) -> aspose.cad.fileformats.dgn.DgnElementMetadata:
        '''Gets element metadata'''
        ...
    
    @property
    def min_point(self) -> aspose.cad.fileformats.cad.cadobjects.Cad3DPoint:
        ...
    
    @property
    def max_point(self) -> aspose.cad.fileformats.cad.cadobjects.Cad3DPoint:
        ...
    
    @property
    def quaternion_rotations(self) -> aspose.cad.fileformats.dgn.dgntransform.DgnQuaternion:
        ...
    
    ...

class DgnElementBase(aspose.cad.IDrawingEntity):
    '''Represents base class for all elements'''
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
        ...
    
    @property
    def metadata(self) -> aspose.cad.fileformats.dgn.DgnElementMetadata:
        '''Gets element metadata'''
        ...
    
    ...

class DgnEllipseElement(DgnArcBasedElement):
    '''Represents ellipse element'''
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
        ...
    
    @property
    def metadata(self) -> aspose.cad.fileformats.dgn.DgnElementMetadata:
        '''Gets element metadata'''
        ...
    
    @property
    def min_point(self) -> aspose.cad.fileformats.cad.cadobjects.Cad3DPoint:
        ...
    
    @property
    def max_point(self) -> aspose.cad.fileformats.cad.cadobjects.Cad3DPoint:
        ...
    
    @property
    def quaternion_rotations(self) -> aspose.cad.fileformats.dgn.dgntransform.DgnQuaternion:
        ...
    
    @property
    def origin(self) -> aspose.cad.fileformats.dgn.DgnPoint:
        '''Gets Origin of ellipse'''
        ...
    
    @property
    def primary_axis(self) -> float:
        ...
    
    @property
    def secondary_axis(self) -> float:
        ...
    
    @property
    def rotation(self) -> float:
        '''Gets Counterclockwise rotation in degrees'''
        ...
    
    @property
    def start_angle(self) -> float:
        ...
    
    @property
    def sweep_angle(self) -> float:
        ...
    
    ...

class DgnKnotWeightElement(DgnElementBase):
    '''Knot weight element'''
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
        ...
    
    @property
    def metadata(self) -> aspose.cad.fileformats.dgn.DgnElementMetadata:
        '''Gets element metadata'''
        ...
    
    @property
    def weights(self) -> List[float]:
        '''Gets weights of knot'''
        ...
    
    ...

class DgnLineElement(DgnDrawableEntityBase):
    '''Represents line'''
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
        ...
    
    @property
    def metadata(self) -> aspose.cad.fileformats.dgn.DgnElementMetadata:
        '''Gets element metadata'''
        ...
    
    @property
    def min_point(self) -> aspose.cad.fileformats.cad.cadobjects.Cad3DPoint:
        ...
    
    @property
    def max_point(self) -> aspose.cad.fileformats.cad.cadobjects.Cad3DPoint:
        ...
    
    @property
    def vertices(self) -> List[aspose.cad.fileformats.dgn.DgnPoint]:
        '''Gets vertices of the line'''
        ...
    
    ...

class DgnMultiTextElement(DgnTextElement):
    '''Represents multi-line text element'''
    
    def add_entity(self, entity : aspose.cad.fileformats.dgn.dgnelements.DgnDrawableEntityBase) -> None:
        '''Adds text element'''
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
    def metadata(self) -> aspose.cad.fileformats.dgn.DgnElementMetadata:
        '''Gets element metadata'''
        ...
    
    @property
    def min_point(self) -> aspose.cad.fileformats.cad.cadobjects.Cad3DPoint:
        ...
    
    @property
    def max_point(self) -> aspose.cad.fileformats.cad.cadobjects.Cad3DPoint:
        ...
    
    @property
    def quaternion_rotations(self) -> aspose.cad.fileformats.dgn.dgntransform.DgnQuaternion:
        ...
    
    @property
    def font_id(self) -> int:
        ...
    
    @property
    def justification(self) -> aspose.cad.fileformats.dgn.DgnJustificationType:
        '''Gets justification'''
        ...
    
    @property
    def length_multiplier(self) -> float:
        ...
    
    @property
    def height_multiplier(self) -> float:
        ...
    
    @property
    def rotation(self) -> float:
        '''Gets counterclockwise rotation in degrees'''
        ...
    
    @property
    def origin(self) -> aspose.cad.fileformats.dgn.DgnPoint:
        '''Gets Bottom left corner of text'''
        ...
    
    @property
    def text(self) -> str:
        '''Gets actual text'''
        ...
    
    @property
    def text_size(self) -> aspose.cad.SizeF:
        ...
    
    @property
    def lines_number(self) -> int:
        ...
    
    @property
    def node_number(self) -> int:
        ...
    
    @property
    def line_spacing(self) -> int:
        ...
    
    @property
    def maximumlength_allowed(self) -> int:
        ...
    
    @property
    def maximumlength_allow_used(self) -> int:
        ...
    
    @property
    def strings(self) -> List[aspose.cad.fileformats.dgn.dgnelements.DgnDrawableEntityBase]:
        '''Gets lines'''
        ...
    
    ...

class DgnPolyLineElement(DgnLineElement):
    '''Represents poly-line'''
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
        ...
    
    @property
    def metadata(self) -> aspose.cad.fileformats.dgn.DgnElementMetadata:
        '''Gets element metadata'''
        ...
    
    @property
    def min_point(self) -> aspose.cad.fileformats.cad.cadobjects.Cad3DPoint:
        ...
    
    @property
    def max_point(self) -> aspose.cad.fileformats.cad.cadobjects.Cad3DPoint:
        ...
    
    @property
    def vertices(self) -> List[aspose.cad.fileformats.dgn.DgnPoint]:
        '''Gets vertices of the line'''
        ...
    
    ...

class DgnRootElement(DgnElementBase):
    '''Represents root element of a DGN file'''
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
        ...
    
    @property
    def metadata(self) -> aspose.cad.fileformats.dgn.DgnElementMetadata:
        '''Gets element metadata'''
        ...
    
    @property
    def is_3d(self) -> bool:
        ...
    
    @property
    def scale(self) -> float:
        '''Gets global scale factor'''
        ...
    
    @property
    def origin_point(self) -> aspose.cad.fileformats.dgn.DgnPoint:
        ...
    
    @property
    def axis_lock_angel(self) -> float:
        ...
    
    @property
    def axis_lock_origin(self) -> float:
        ...
    
    @property
    def active_cell(self) -> int:
        ...
    
    @property
    def active_pattering_scale(self) -> float:
        ...
    
    @property
    def active_pattering_cell(self) -> int:
        ...
    
    @property
    def active_pattering_row_spacing(self) -> int:
        ...
    
    @property
    def active_pattering_angle(self) -> float:
        ...
    
    @property
    def active_pattering_angle2(self) -> float:
        ...
    
    @property
    def active_pattering_column_spacing(self) -> int:
        ...
    
    @property
    def active_point(self) -> int:
        ...
    
    @property
    def active_line_terminator_scale(self) -> float:
        ...
    
    @property
    def active_line_terminator(self) -> int:
        ...
    
    @property
    def key_point_snap_flag(self) -> int:
        ...
    
    @property
    def key_point_snap_divisor(self) -> int:
        ...
    
    @property
    def unit_type(self) -> aspose.cad.imageoptions.UnitType:
        ...
    
    @property
    def sub_unit_type(self) -> aspose.cad.imageoptions.UnitType:
        ...
    
    ...

class DgnShapeElement(DgnLineElement):
    '''Represents shape element'''
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
        ...
    
    @property
    def metadata(self) -> aspose.cad.fileformats.dgn.DgnElementMetadata:
        '''Gets element metadata'''
        ...
    
    @property
    def min_point(self) -> aspose.cad.fileformats.cad.cadobjects.Cad3DPoint:
        ...
    
    @property
    def max_point(self) -> aspose.cad.fileformats.cad.cadobjects.Cad3DPoint:
        ...
    
    @property
    def vertices(self) -> List[aspose.cad.fileformats.dgn.DgnPoint]:
        '''Gets vertices of the line'''
        ...
    
    @property
    def filled(self) -> bool:
        '''Gets a value indicating whether this :py:class:`aspose.cad.fileformats.dgn.dgnelements.DgnShapeElement` is filled.'''
        ...
    
    ...

class DgnSharedCellDefinitionElement(DgnElementBase):
    '''Represents shared cell definition element'''
    
    def add_child(self, child : aspose.cad.fileformats.dgn.dgnelements.DgnElementBase) -> None:
        '''Adds element as a child
        
        :param child: element to add as a child'''
        ...
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> List[aspose.cad.fileformats.dgn.dgnelements.DgnDrawableEntityBase]:
        '''Gets childs of the composite element'''
        ...
    
    @property
    def metadata(self) -> aspose.cad.fileformats.dgn.DgnElementMetadata:
        '''Gets element metadata'''
        ...
    
    @property
    def totallength(self) -> int:
        '''Gets cell total length'''
        ...
    
    @property
    def name(self) -> str:
        '''Gets the name.'''
        ...
    
    ...

class DgnSharedCellElement(DgnDrawableEntityBase):
    '''Represents shared cell definition element'''
    
    @property
    def id(self) -> str:
        '''Gets the identifier.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
        ...
    
    @property
    def metadata(self) -> aspose.cad.fileformats.dgn.DgnElementMetadata:
        '''Gets element metadata'''
        ...
    
    @property
    def min_point(self) -> aspose.cad.fileformats.cad.cadobjects.Cad3DPoint:
        ...
    
    @property
    def max_point(self) -> aspose.cad.fileformats.cad.cadobjects.Cad3DPoint:
        ...
    
    @property
    def name(self) -> str:
        '''Gets the name.'''
        ...
    
    @property
    def origin(self) -> aspose.cad.fileformats.dgn.DgnPoint:
        '''Gets cell's origin point'''
        ...
    
    @property
    def definition(self) -> aspose.cad.fileformats.dgn.dgnelements.DgnSharedCellDefinitionElement:
        '''Gets the definition.'''
        ...
    
    ...

class DgnSplineKnotElement(DgnKnotWeightElement):
    '''Represents spline knot element'''
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
        ...
    
    @property
    def metadata(self) -> aspose.cad.fileformats.dgn.DgnElementMetadata:
        '''Gets element metadata'''
        ...
    
    @property
    def weights(self) -> List[float]:
        '''Gets weights of knot'''
        ...
    
    ...

class DgnSplinePoleElement(DgnLineElement):
    '''Represents spline pole element'''
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
        ...
    
    @property
    def metadata(self) -> aspose.cad.fileformats.dgn.DgnElementMetadata:
        '''Gets element metadata'''
        ...
    
    @property
    def min_point(self) -> aspose.cad.fileformats.cad.cadobjects.Cad3DPoint:
        ...
    
    @property
    def max_point(self) -> aspose.cad.fileformats.cad.cadobjects.Cad3DPoint:
        ...
    
    @property
    def vertices(self) -> List[aspose.cad.fileformats.dgn.DgnPoint]:
        '''Gets vertices of the line'''
        ...
    
    ...

class DgnSplineWeightFactorElement(DgnKnotWeightElement):
    '''Represents spline weight factor element'''
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
        ...
    
    @property
    def metadata(self) -> aspose.cad.fileformats.dgn.DgnElementMetadata:
        '''Gets element metadata'''
        ...
    
    @property
    def weights(self) -> List[float]:
        '''Gets weights of knot'''
        ...
    
    ...

class DgnSurfaceElement(DgnDrawableEntityBase):
    '''Represents surface element'''
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
        ...
    
    @property
    def metadata(self) -> aspose.cad.fileformats.dgn.DgnElementMetadata:
        '''Gets element metadata'''
        ...
    
    @property
    def min_point(self) -> aspose.cad.fileformats.cad.cadobjects.Cad3DPoint:
        ...
    
    @property
    def max_point(self) -> aspose.cad.fileformats.cad.cadobjects.Cad3DPoint:
        ...
    
    @property
    def is_rational(self) -> bool:
        ...
    
    @property
    def is_uniform(self) -> bool:
        ...
    
    @is_uniform.setter
    def is_uniform(self, value : bool):
        ...
    
    @property
    def properties_u(self) -> byte:
        ...
    
    @property
    def order_u(self) -> byte:
        ...
    
    @property
    def poles_count_u(self) -> int:
        ...
    
    @property
    def knots_count_u(self) -> int:
        ...
    
    @property
    def rule_lines_u(self) -> int:
        ...
    
    @property
    def properties_v(self) -> byte:
        ...
    
    @property
    def order_v(self) -> byte:
        ...
    
    @property
    def poles_count_v(self) -> int:
        ...
    
    @property
    def knots_count_v(self) -> int:
        ...
    
    @property
    def rule_lines_v(self) -> int:
        ...
    
    @property
    def surface_type(self) -> int:
        ...
    
    @property
    def bound_elements_count(self) -> int:
        ...
    
    @property
    def boundaries(self) -> List[aspose.cad.fileformats.dgn.dgnelements.DgnDrawableEntityBase]:
        '''Gets bound elements'''
        ...
    
    @property
    def poles(self) -> List[aspose.cad.fileformats.dgn.dgnelements.DgnSplinePoleElement]:
        '''Gets poles'''
        ...
    
    @property
    def knot(self) -> aspose.cad.fileformats.dgn.dgnelements.DgnSplineKnotElement:
        '''Gets knot'''
        ...
    
    @property
    def weights(self) -> List[aspose.cad.fileformats.dgn.dgnelements.DgnSplineWeightFactorElement]:
        '''Gets weights'''
        ...
    
    ...

class DgnSymbologyLevelElement(DgnElementBase):
    '''Represents Symbology element'''
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
        ...
    
    @property
    def metadata(self) -> aspose.cad.fileformats.dgn.DgnElementMetadata:
        '''Gets element metadata'''
        ...
    
    ...

class DgnTagSetElement(DgnElementBase):
    '''Represents 'Tag Set Definition' element'''
    
    @property
    def id(self) -> str:
        '''Gets the identifier.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
        ...
    
    @property
    def metadata(self) -> aspose.cad.fileformats.dgn.DgnElementMetadata:
        '''Gets element metadata'''
        ...
    
    @property
    def tags(self) -> List[aspose.cad.fileformats.dgn.DgnTag]:
        '''Gets tags of the tag definition'''
        ...
    
    ...

class DgnTagValueElement(DgnElementBase):
    '''Represents 'Tag Value' element'''
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
        ...
    
    @property
    def metadata(self) -> aspose.cad.fileformats.dgn.DgnElementMetadata:
        '''Gets element metadata'''
        ...
    
    @property
    def tag_set(self) -> int:
        ...
    
    @property
    def tag_index(self) -> int:
        ...
    
    @property
    def tag_length(self) -> int:
        ...
    
    @property
    def tag_value(self) -> aspose.cad.fileformats.dgn.DgnTagValue:
        ...
    
    @tag_value.setter
    def tag_value(self, value : aspose.cad.fileformats.dgn.DgnTagValue):
        ...
    
    ...

class DgnTextElement(DgnDrawingElementBaseQuaternion):
    '''Represents text element'''
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
        ...
    
    @property
    def metadata(self) -> aspose.cad.fileformats.dgn.DgnElementMetadata:
        '''Gets element metadata'''
        ...
    
    @property
    def min_point(self) -> aspose.cad.fileformats.cad.cadobjects.Cad3DPoint:
        ...
    
    @property
    def max_point(self) -> aspose.cad.fileformats.cad.cadobjects.Cad3DPoint:
        ...
    
    @property
    def quaternion_rotations(self) -> aspose.cad.fileformats.dgn.dgntransform.DgnQuaternion:
        ...
    
    @property
    def font_id(self) -> int:
        ...
    
    @property
    def justification(self) -> aspose.cad.fileformats.dgn.DgnJustificationType:
        '''Gets justification'''
        ...
    
    @property
    def length_multiplier(self) -> float:
        ...
    
    @property
    def height_multiplier(self) -> float:
        ...
    
    @property
    def rotation(self) -> float:
        '''Gets counterclockwise rotation in degrees'''
        ...
    
    @property
    def origin(self) -> aspose.cad.fileformats.dgn.DgnPoint:
        '''Gets Bottom left corner of text'''
        ...
    
    @property
    def text(self) -> str:
        '''Gets actual text'''
        ...
    
    @property
    def text_size(self) -> aspose.cad.SizeF:
        ...
    
    ...

class ICompositeDgnElement(aspose.cad.IDrawingEntity):
    '''Represents composite elements (like cell header)'''
    
    def add_child(self, child : aspose.cad.fileformats.dgn.dgnelements.DgnElementBase) -> None:
        '''Adds element as a child
        
        :param child: element to add as a child'''
        ...
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
        ...
    
    ...

