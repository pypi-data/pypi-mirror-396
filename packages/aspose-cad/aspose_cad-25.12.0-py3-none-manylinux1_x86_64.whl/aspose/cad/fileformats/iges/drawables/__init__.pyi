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

class BezierCurve(IgesDrawableBase):
    '''Provides intermediate Drawable representation in form of cubic Bezier curve'''
    
    def get_transformed_drawable(self, new_points : List[aspose.cad.primitives.Point3D]) -> aspose.cad.fileformats.iges.drawables.IIgesDrawable:
        '''Creates a new Bezier curve using provided points and non-geometric properties of current Bezier curve
        
        :param new_points: All points defining new geometry
        :returns: New Bezier curve with new geometry and current non-geometric properties'''
        ...
    
    def get_new_props_drawable(self, props : aspose.cad.fileformats.iges.drawables.IDrawableProperties) -> aspose.cad.fileformats.iges.drawables.IIgesDrawable:
        '''Creates a new Bezier curve using geometry of current BEzier curve and provided non-geometric properties
        
        :param props: New non-geometric properties
        :returns: New Bezier curve with current geometry and new non-geometric properties'''
        ...
    
    @property
    def properties(self) -> aspose.cad.fileformats.iges.drawables.IDrawableProperties:
        '''Non-geometric properties for geometry'''
        ...
    
    @property
    def all_points(self) -> List[aspose.cad.primitives.Point3D]:
        ...
    
    @property
    def entity_uid(self) -> str:
        ...
    
    @entity_uid.setter
    def entity_uid(self, value : str):
        ...
    
    @property
    def id(self) -> str:
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        ...
    
    ...

class IDrawableProperties:
    '''Interface for Non-geometric properties for geometric representations'''
    
    @property
    def color(self) -> Optional[aspose.cad.fileformats.iges.commondefinitions.ColorRGB]:
        '''Color to represent geometry with'''
        ...
    
    @property
    def line_thickness(self) -> float:
        ...
    
    @property
    def visible(self) -> bool:
        '''Visibility of geometry'''
        ...
    
    @property
    def unit_to_mm_rate(self) -> float:
        ...
    
    @property
    def line_pattern(self) -> aspose.cad.fileformats.iges.drawables.LinePatternPredef:
        ...
    
    ...

class IIgesDrawable:
    '''Parent Interface for Simple geometric representation of an entity or its part'''
    
    def get_transformed_drawable(self, new_points : List[aspose.cad.primitives.Point3D]) -> aspose.cad.fileformats.iges.drawables.IIgesDrawable:
        '''Creates a new drawable using provided points and non-geometric properties of current drawable
        
        :param new_points: All points defining new geometry
        :returns: New drawable with new geometry and current non-geometric properties'''
        ...
    
    def get_new_props_drawable(self, props : aspose.cad.fileformats.iges.drawables.IDrawableProperties) -> aspose.cad.fileformats.iges.drawables.IIgesDrawable:
        '''Creates a new drawable using geometry of current drawable and provided non-geometric properties
        
        :param props: New non-geometric properties
        :returns: New drawable with current geometry and new non-geometric properties'''
        ...
    
    @property
    def properties(self) -> aspose.cad.fileformats.iges.drawables.IDrawableProperties:
        '''Non-geometric properties of geometric representation'''
        ...
    
    @property
    def all_points(self) -> List[aspose.cad.primitives.Point3D]:
        ...
    
    @property
    def entity_uid(self) -> str:
        ...
    
    @entity_uid.setter
    def entity_uid(self, value : str):
        ...
    
    ...

class IgesDrawableBase(IIgesDrawable):
    '''Provides a base class for intermediate representation of document entities in simple geometric form'''
    
    def get_transformed_drawable(self, new_points : List[aspose.cad.primitives.Point3D]) -> aspose.cad.fileformats.iges.drawables.IIgesDrawable:
        '''Creates a new drawable using provided points and non-geometric properties of current drawable
        
        :param new_points: All points defining new geometry
        :returns: New drawable with new geometry and current non-geometric properties'''
        ...
    
    def get_new_props_drawable(self, props : aspose.cad.fileformats.iges.drawables.IDrawableProperties) -> aspose.cad.fileformats.iges.drawables.IIgesDrawable:
        '''Creates a new drawable using geometry of current drawable and provided non-geometric properties
        
        :param props: New non-geometric properties
        :returns: New drawable with current geometry and new non-geometric properties'''
        ...
    
    @property
    def properties(self) -> aspose.cad.fileformats.iges.drawables.IDrawableProperties:
        '''Non-geometric properties for geometry'''
        ...
    
    @property
    def all_points(self) -> List[aspose.cad.primitives.Point3D]:
        ...
    
    @property
    def entity_uid(self) -> str:
        ...
    
    @entity_uid.setter
    def entity_uid(self, value : str):
        ...
    
    @property
    def id(self) -> str:
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        ...
    
    ...

class Polygon(IgesDrawableBase):
    
    def get_transformed_drawable(self, new_points : List[aspose.cad.primitives.Point3D]) -> aspose.cad.fileformats.iges.drawables.IIgesDrawable:
        '''Creates a new drawable using provided points and non-geometric properties of current drawable
        
        :param new_points: All points defining new geometry
        :returns: New drawable with new geometry and current non-geometric properties'''
        ...
    
    def get_new_props_drawable(self, props : aspose.cad.fileformats.iges.drawables.IDrawableProperties) -> aspose.cad.fileformats.iges.drawables.IIgesDrawable:
        '''Creates a new drawable using geometry of current drawable and provided non-geometric properties
        
        :param props: New non-geometric properties
        :returns: New drawable with current geometry and new non-geometric properties'''
        ...
    
    @property
    def properties(self) -> aspose.cad.fileformats.iges.drawables.IDrawableProperties:
        '''Non-geometric properties for geometry'''
        ...
    
    @property
    def all_points(self) -> List[aspose.cad.primitives.Point3D]:
        ...
    
    @property
    def entity_uid(self) -> str:
        ...
    
    @entity_uid.setter
    def entity_uid(self, value : str):
        ...
    
    @property
    def id(self) -> str:
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        ...
    
    ...

class Polyline(IgesDrawableBase):
    '''Provides intermediate Drawable representation in form of segmented line'''
    
    def get_transformed_drawable(self, new_points : List[aspose.cad.primitives.Point3D]) -> aspose.cad.fileformats.iges.drawables.IIgesDrawable:
        '''Creates a new drawable using provided points and non-geometric properties of current drawable
        
        :param new_points: All points defining new geometry
        :returns: New drawable with new geometry and current non-geometric properties'''
        ...
    
    def get_new_props_drawable(self, props : aspose.cad.fileformats.iges.drawables.IDrawableProperties) -> aspose.cad.fileformats.iges.drawables.IIgesDrawable:
        '''Creates a new drawable using geometry of current drawable and provided non-geometric properties
        
        :param props: New non-geometric properties
        :returns: New drawable with current geometry and new non-geometric properties'''
        ...
    
    @property
    def properties(self) -> aspose.cad.fileformats.iges.drawables.IDrawableProperties:
        '''Non-geometric properties for geometry'''
        ...
    
    @property
    def all_points(self) -> List[aspose.cad.primitives.Point3D]:
        ...
    
    @property
    def entity_uid(self) -> str:
        ...
    
    @entity_uid.setter
    def entity_uid(self, value : str):
        ...
    
    @property
    def id(self) -> str:
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        ...
    
    ...

class TextDrawable(IgesDrawableBase):
    '''Provides intermediate Drawable representation of a text in a drawing'''
    
    def get_transformed_drawable(self, new_points : List[aspose.cad.primitives.Point3D]) -> aspose.cad.fileformats.iges.drawables.IIgesDrawable:
        '''Creates a new Text drawable using provided points and non-geometric properties of current Text drawable
        
        :param new_points: All points defining new geometry
        :returns: New Text drawable with new geometry and current non-geometric properties'''
        ...
    
    def get_new_props_drawable(self, props : aspose.cad.fileformats.iges.drawables.IDrawableProperties) -> aspose.cad.fileformats.iges.drawables.IIgesDrawable:
        '''Creates a new Text drawable using geometry of current Text drawable and provided non-geometric properties
        
        :param props: New non-geometric properties
        :returns: New Text drawable with current geometry and new non-geometric properties'''
        ...
    
    @property
    def properties(self) -> aspose.cad.fileformats.iges.drawables.IDrawableProperties:
        '''Non-geometric properties for geometry'''
        ...
    
    @property
    def all_points(self) -> List[aspose.cad.primitives.Point3D]:
        ...
    
    @property
    def entity_uid(self) -> str:
        ...
    
    @entity_uid.setter
    def entity_uid(self, value : str):
        ...
    
    @property
    def id(self) -> str:
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        ...
    
    @property
    def orientation(self) -> aspose.cad.fileformats.iges.drawables.TextOrientation:
        '''Horizontal or vertical text'''
        ...
    
    @property
    def mirrioring(self) -> aspose.cad.fileformats.iges.drawables.TextMirrioring:
        '''Mirroring of text'''
        ...
    
    @property
    def text(self) -> str:
        '''Text'''
        ...
    
    @property
    def origin(self) -> aspose.cad.primitives.Point3D:
        '''Left bottom point of text boundary, used as origin point of primitive,maps to AllPoints[0]'''
        ...
    
    @property
    def end_bottom_line(self) -> aspose.cad.primitives.Point3D:
        ...
    
    @property
    def upper_left(self) -> aspose.cad.primitives.Point3D:
        ...
    
    @property
    def upper_right(self) -> aspose.cad.primitives.Point3D:
        ...
    
    ...

class LinePatternPredef:
    '''Defines line style'''
    
    @classmethod
    @property
    def SOLID(cls) -> LinePatternPredef:
        '''Solid'''
        ...
    
    @classmethod
    @property
    def DASHED(cls) -> LinePatternPredef:
        '''Dashed'''
        ...
    
    @classmethod
    @property
    def DOTTED(cls) -> LinePatternPredef:
        '''Dotted'''
        ...
    
    @classmethod
    @property
    def DASH_DOT(cls) -> LinePatternPredef:
        '''Dashed + Dotted'''
        ...
    
    @classmethod
    @property
    def PHANTOM(cls) -> LinePatternPredef:
        '''Phantom'''
        ...
    
    @classmethod
    @property
    def CUSTOM(cls) -> LinePatternPredef:
        '''Custom'''
        ...
    
    ...

class TextMirrioring:
    '''Defines text mirrioring'''
    
    @classmethod
    @property
    def NONE(cls) -> TextMirrioring:
        '''None'''
        ...
    
    @classmethod
    @property
    def TEXT_BASE_LINE(cls) -> TextMirrioring:
        '''About horizontal "underscore" line below text'''
        ...
    
    @classmethod
    @property
    def TEXT_BEGIN_LINE(cls) -> TextMirrioring:
        '''About vertical line before first letter of the text.'''
        ...
    
    ...

class TextOrientation:
    '''Defines orientation of text'''
    
    @classmethod
    @property
    def HORIZONTAL(cls) -> TextOrientation:
        '''Horizontal'''
        ...
    
    @classmethod
    @property
    def VERTICAL(cls) -> TextOrientation:
        '''Vertical'''
        ...
    
    ...

