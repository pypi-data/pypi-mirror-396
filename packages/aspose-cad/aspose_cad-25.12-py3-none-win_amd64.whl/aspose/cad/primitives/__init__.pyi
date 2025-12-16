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

class Point2D:
    '''The 2D point.'''
    
    @overload
    @staticmethod
    def distance(point1 : aspose.cad.primitives.Point2D, point2 : aspose.cad.primitives.Point2D) -> float:
        '''Gets distance between points
        
        :param point1: First point
        :param point2: Second point
        :returns: Euclidean distance'''
        ...
    
    @overload
    def distance(self, point2 : aspose.cad.primitives.Point2D) -> float:
        ...
    
    def equals(self, other : aspose.cad.primitives.Point2D) -> bool:
        ...
    
    @property
    def x(self) -> float:
        '''Gets the x.'''
        ...
    
    @x.setter
    def x(self, value : float):
        '''Sets the x.'''
        ...
    
    @property
    def y(self) -> float:
        '''Gets the y.'''
        ...
    
    @y.setter
    def y(self, value : float):
        '''Sets the y.'''
        ...
    
    ...

class Point3D(Point2D):
    '''Represents class to work with 3D point and special operations for it.'''
    
    @overload
    @staticmethod
    def distance(point1 : aspose.cad.primitives.Point3D, point2 : aspose.cad.primitives.Point3D) -> float:
        '''Gets distance between points
        
        :param point1: First point
        :param point2: Second point
        :returns: Euclidean distance'''
        ...
    
    @overload
    def distance(self, point2 : aspose.cad.primitives.Point3D) -> float:
        ...
    
    @overload
    @staticmethod
    def distance(point1 : aspose.cad.primitives.Point2D, point2 : aspose.cad.primitives.Point2D) -> float:
        '''Gets distance between points
        
        :param point1: First point
        :param point2: Second point
        :returns: Euclidean distance'''
        ...
    
    @overload
    def distance(self, point2 : aspose.cad.primitives.Point2D) -> float:
        ...
    
    def equals(self, other : aspose.cad.primitives.Point2D) -> bool:
        '''Overrides the Equals of 2D point so the called comparison would be 3D
        
        :returns: True if points are equal.'''
        ...
    
    @staticmethod
    def spherical(r : float, theta : float, phi : float) -> aspose.cad.primitives.Point3D:
        '''Get point in spherical coordinates
        
        :param r: R value
        :param theta: Theta value
        :param phi: Phi value
        :returns: Spherical coordinates point'''
        ...
    
    @staticmethod
    def cross_product(point1 : aspose.cad.primitives.Point3D, point2 : aspose.cad.primitives.Point3D) -> aspose.cad.primitives.Point3D:
        '''Gets cross-product of a points
        
        :param point1: First point
        :param point2: Second point
        :returns: Cross product point'''
        ...
    
    @staticmethod
    def dot_product(point1 : aspose.cad.primitives.Point3D, point2 : aspose.cad.primitives.Point3D) -> float:
        '''Gets dot product between two vectors.
        
        :param point1: First vector.
        :param point2: Second vector.
        :returns: Dor product'''
        ...
    
    @staticmethod
    def normal_vector(point1 : aspose.cad.primitives.Point3D, point2 : aspose.cad.primitives.Point3D, point3 : aspose.cad.primitives.Point3D) -> aspose.cad.primitives.Point3D:
        '''Get normal vector of a plane.
        
        :param point1: First vector of a plane.
        :param point2: Second vector of a plane.
        :param point3: Third vector of a plane.
        :returns: Normal vector of a plane'''
        ...
    
    def equality(self, obj : any) -> bool:
        '''Does the real comparison of 3D points
        
        :param obj: Point to compare current object with.
        :returns: True if points are equal.'''
        ...
    
    def equals_soft(self, obj : any, eps : float) -> bool:
        '''Allows to compare 3D points with specified threshold.
        
        :param obj: Point to compare current object with.
        :param eps: Epsilon threshold.
        :returns: True if points are equal.'''
        ...
    
    def copy(self) -> aspose.cad.primitives.Point3D:
        '''Creates copy of current point
        
        :returns: Copy of a point'''
        ...
    
    def normalize(self) -> aspose.cad.primitives.Point3D:
        '''Normalizes the specified origin.'''
        ...
    
    @property
    def x(self) -> float:
        '''Gets the x.'''
        ...
    
    @x.setter
    def x(self, value : float):
        '''Sets the x.'''
        ...
    
    @property
    def y(self) -> float:
        '''Gets the y.'''
        ...
    
    @y.setter
    def y(self, value : float):
        '''Sets the y.'''
        ...
    
    @property
    def z(self) -> float:
        '''Gets Z coordinate'''
        ...
    
    @z.setter
    def z(self, value : float):
        '''Sets Z coordinate'''
        ...
    
    @property
    def w(self) -> float:
        '''Gets W coordinate'''
        ...
    
    @w.setter
    def w(self, value : float):
        '''Sets W coordinate'''
        ...
    
    @property
    def coordinate_array(self) -> List[float]:
        ...
    
    @classmethod
    @property
    def ZERO(cls) -> aspose.cad.primitives.Point3D:
        ...
    
    ...

