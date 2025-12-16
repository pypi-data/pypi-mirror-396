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

class BezierCurve:
    
    ...

class CgmColor:
    '''Represents a color parameter type'''
    
    def equals(self, other : aspose.cad.fileformats.cgm.classes.CgmColor) -> bool:
        ...
    
    @property
    def color(self) -> aspose.pydrawing.Color:
        ...
    
    @color.setter
    def color(self, value : aspose.pydrawing.Color):
        ...
    
    @property
    def color_index(self) -> int:
        ...
    
    @color_index.setter
    def color_index(self, value : int):
        ...
    
    ...

class CgmPoint:
    '''Represents a point parameter type'''
    
    def equals(self, other : aspose.cad.fileformats.cgm.classes.CgmPoint) -> bool:
        ...
    
    def compare_to(self, other : aspose.cad.fileformats.cgm.classes.CgmPoint) -> int:
        '''sort CGMPoints to the leftest upper corner
        
        :param other: An object to compare with this instance.
        :returns: A value that indicates the relative order of the objects being compared. The return value has these meanings: Value Meaning Less than zero This instance precedes ``other`` in the sort order.  Zero This instance occurs in the same position in the sort order as ``other``. Greater than zero This instance follows ``other`` in the sort order.'''
        ...
    
    @staticmethod
    def is_same(x : float, y : float) -> bool:
        ...
    
    @staticmethod
    def compare_values(x : float, y : float) -> int:
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
    
    ...

class CgmPointComparer:
    '''Comparer to sort CGMPoints to the leftest upper corner'''
    
    def compare(self, x : aspose.cad.fileformats.cgm.classes.CgmPoint, y : aspose.cad.fileformats.cgm.classes.CgmPoint) -> int:
        ...
    
    ...

class CgmRectangle:
    
    @overload
    def contains(self, point : aspose.cad.fileformats.cgm.classes.CgmPoint) -> bool:
        '''Determines if the specified point is contained within this rectangle.
        
        :param point: The point to test.
        :returns: This method returns true if the point defined by ``x`` and ``y`` is contained within this rectangle; otherwise false.'''
        ...
    
    @overload
    def contains(self, x : float, y : float) -> bool:
        '''Determines if the specified point is contained within this rectangle.
        
        :param x: The x-coordinate of the point to test.
        :param y: The y-coordinate of the point to test.
        :returns: This method returns true if the point defined by ``x`` and ``y`` is contained within this rectangle; otherwise false.'''
        ...
    
    @overload
    def contains(self, point : aspose.cad.fileformats.cgm.classes.CgmPoint, max_distance : float) -> bool:
        '''Determines if the specified point is contained within this rectangle.
        
        :param point: The point to test.
        :param max_distance: The maximum distance to the rectangle border.
        :returns: This method returns true if the point defined by ``x`` and ``y`` is contained within this rectangle; otherwise false.'''
        ...
    
    @overload
    def contains(self, x : float, y : float, max_dinstance : float) -> bool:
        '''Determines if the specified point is contained within this rectangle.
        
        :param x: The x-coordinate of the point to test.
        :param y: The y-coordinate of the point to test.
        :returns: This method returns true if the point defined by ``x`` and ``y`` is contained within this rectangle; otherwise false.'''
        ...
    
    @staticmethod
    def from_points(left_upper_corner : aspose.cad.fileformats.cgm.classes.CgmPoint, right_upper_corner : aspose.cad.fileformats.cgm.classes.CgmPoint, left_lower_corner : aspose.cad.fileformats.cgm.classes.CgmPoint, right_lower_corner : aspose.cad.fileformats.cgm.classes.CgmPoint) -> aspose.cad.fileformats.cgm.classes.CgmRectangle:
        '''Create a rectangle from the rectangle points.
        
        :param left_upper_corner: The left upper corner.
        :param right_upper_corner: The right upper corner.
        :param left_lower_corner: The left lower corner.
        :param right_lower_corner: The right lower corner.'''
        ...
    
    @property
    def x(self) -> float:
        ...
    
    @property
    def y(self) -> float:
        ...
    
    @property
    def height(self) -> float:
        ...
    
    @property
    def width(self) -> float:
        ...
    
    @property
    def is_empty(self) -> bool:
        ...
    
    @classmethod
    @property
    def EMPTY(cls) -> aspose.cad.fileformats.cgm.classes.CgmRectangle:
        '''Represents an instance of the CGMRectangle class with its members uninitialized.'''
        ...
    
    ...

class StructuredDataRecord:
    '''Structured Data Record container'''
    
    @overload
    def add(self, type : StructuredDataRecord.StructuredDataType, count : int, data : List[any]) -> None:
        ...
    
    @overload
    def add(self, type : StructuredDataRecord.StructuredDataType, data : List[any]) -> None:
        ...
    
    @property
    def members(self) -> List[StructuredDataRecord.Member]:
        ...
    
    ...

class TextInformation:
    '''Information bundle of text elements'''
    
    @property
    def text_command(self) -> aspose.cad.fileformats.cgm.commands.TextCommand:
        ...
    
    @text_command.setter
    def text_command(self, value : aspose.cad.fileformats.cgm.commands.TextCommand):
        ...
    
    @property
    def color_command(self) -> aspose.cad.fileformats.cgm.commands.TextColour:
        ...
    
    @color_command.setter
    def color_command(self, value : aspose.cad.fileformats.cgm.commands.TextColour):
        ...
    
    @property
    def height_command(self) -> aspose.cad.fileformats.cgm.commands.CharacterHeight:
        ...
    
    @height_command.setter
    def height_command(self, value : aspose.cad.fileformats.cgm.commands.CharacterHeight):
        ...
    
    ...

class VC:
    '''Represents the abstract VC parameter type'''
    
    @property
    def value_int(self) -> int:
        ...
    
    @value_int.setter
    def value_int(self, value : int):
        ...
    
    @property
    def value_real(self) -> float:
        ...
    
    @value_real.setter
    def value_real(self, value : float):
        ...
    
    ...

class ViewportPoint:
    '''The abstract parameter type VC is a single value; a viewport point, VP, is an ordered pair of VC'''
    
    @property
    def first_point(self) -> aspose.cad.fileformats.cgm.classes.VC:
        ...
    
    @first_point.setter
    def first_point(self, value : aspose.cad.fileformats.cgm.classes.VC):
        ...
    
    @property
    def second_point(self) -> aspose.cad.fileformats.cgm.classes.VC:
        ...
    
    @second_point.setter
    def second_point(self, value : aspose.cad.fileformats.cgm.classes.VC):
        ...
    
    ...

