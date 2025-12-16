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

class AffineTransform:
    '''Represents an affine transform in 3D space, with two mutually exclusive representantions:'''
    
    def equals(self, other : aspose.cad.fileformats.glb.transforms.AffineTransform) -> bool:
        ...
    
    @staticmethod
    def are_geometrically_equivalent(a : Any, b : Any, tolerance : float) -> bool:
        '''Checks whether two transform represent the same geometric spatial transformation.
        
        :param a: the first transform to check.
        :param b: the second transform to check.
        :param tolerance: the tolerance to handle floating point error.
        :returns: true if both transforms can be considered geometryically equivalent.'''
        ...
    
    def get_decomposed(self) -> aspose.cad.fileformats.glb.transforms.AffineTransform:
        '''If this object represents a :py:class:`System.Numerics.Matrix4x4`, it returns a decomposed representation.'''
        ...
    
    def try_decompose(self, transform : Any) -> bool:
        ...
    
    @staticmethod
    def blend(transforms : List[aspose.cad.fileformats.glb.transforms.AffineTransform], weights : List[float]) -> aspose.cad.fileformats.glb.transforms.AffineTransform:
        ...
    
    @staticmethod
    def multiply(a : Any, b : Any) -> aspose.cad.fileformats.glb.transforms.AffineTransform:
        '''Multiplies ``a`` by ``b``.
        
        :param a: The left transform.
        :param b: The right transform.
        :returns: A new :py:class:`aspose.cad.fileformats.glb.transforms.AffineTransform` structure.
        
        
        The returned value will use a decomposed
        
        representation it these two conditions are met:
        
        Otherwise the returned value will use a Matrix representation.'''
        ...
    
    @staticmethod
    def try_invert(xform : Any, inverse : Any) -> bool:
        '''Inverts the specified transform. The return value indicates whether the operation succeeded.
        
        :param xform: The transform to invert.
        :param inverse: The inverted result.
        :returns: True if the operation succeeds.'''
        ...
    
    @property
    def is_valid(self) -> bool:
        ...
    
    @property
    def is_matrix(self) -> bool:
        ...
    
    @property
    def is_srt(self) -> bool:
        ...
    
    @property
    def is_lossless_decomposable(self) -> bool:
        ...
    
    @property
    def is_identity(self) -> bool:
        ...
    
    @classmethod
    @property
    def IDENTITY(cls) -> aspose.cad.fileformats.glb.transforms.AffineTransform:
        ...
    
    ...

class Matrix4x4Double:
    
    @staticmethod
    def create_translation(x_position : float, y_position : float, z_position : float) -> aspose.cad.fileformats.glb.transforms.Matrix4x4Double:
        '''Creates a translation matrix.
        
        :param x_position: The amount to translate on the X-axis.
        :param y_position: The amount to translate on the Y-axis.
        :param z_position: The amount to translate on the Z-axis.
        :returns: The translation matrix.'''
        ...
    
    @staticmethod
    def create_scale(x_scale : float, y_scale : float, z_scale : float) -> aspose.cad.fileformats.glb.transforms.Matrix4x4Double:
        '''Creates a scaling matrix.
        
        :param x_scale: Value to scale by on the X-axis.
        :param y_scale: Value to scale by on the Y-axis.
        :param z_scale: Value to scale by on the Z-axis.
        :returns: The scaling matrix.'''
        ...
    
    def equals(self, other : aspose.cad.fileformats.glb.transforms.Matrix4x4Double) -> bool:
        '''Returns a boolean indicating whether this matrix instance is equal to the other given matrix.
        
        :param other: The matrix to compare this instance to.
        :returns: True if the matrices are equal; False otherwise.'''
        ...
    
    @staticmethod
    def invert(matrix : aspose.cad.fileformats.glb.transforms.Matrix4x4Double, result : Any) -> bool:
        '''Attempts to calculate the inverse of the given matrix. If successful, result will contain the inverted matrix.
        
        :param matrix: The source matrix to invert.
        :param result: If successful, contains the inverted matrix.
        :returns: True if the source matrix could be inverted; False otherwise.'''
        ...
    
    @staticmethod
    def multiply(value1 : aspose.cad.fileformats.glb.transforms.Matrix4x4Double, value2 : aspose.cad.fileformats.glb.transforms.Matrix4x4Double) -> aspose.cad.fileformats.glb.transforms.Matrix4x4Double:
        '''Multiplies a matrix by another matrix.
        
        :param value1: The first source matrix.
        :param value2: The second source matrix.
        :returns: The result of the multiplication.'''
        ...
    
    @classmethod
    @property
    def identity(cls) -> aspose.cad.fileformats.glb.transforms.Matrix4x4Double:
        '''Returns the multiplicative identity matrix.'''
        ...
    
    @property
    def m11(self) -> float:
        '''Value at row 1, column 1 of the matrix.'''
        ...
    
    @m11.setter
    def m11(self, value : float):
        '''Value at row 1, column 1 of the matrix.'''
        ...
    
    @property
    def m12(self) -> float:
        '''Value at row 1, column 2 of the matrix.'''
        ...
    
    @m12.setter
    def m12(self, value : float):
        '''Value at row 1, column 2 of the matrix.'''
        ...
    
    @property
    def m13(self) -> float:
        '''Value at row 1, column 3 of the matrix.'''
        ...
    
    @m13.setter
    def m13(self, value : float):
        '''Value at row 1, column 3 of the matrix.'''
        ...
    
    @property
    def m14(self) -> float:
        '''Value at row 1, column 4 of the matrix.'''
        ...
    
    @m14.setter
    def m14(self, value : float):
        '''Value at row 1, column 4 of the matrix.'''
        ...
    
    @property
    def m21(self) -> float:
        '''Value at row 2, column 1 of the matrix.'''
        ...
    
    @m21.setter
    def m21(self, value : float):
        '''Value at row 2, column 1 of the matrix.'''
        ...
    
    @property
    def m22(self) -> float:
        '''Value at row 2, column 2 of the matrix.'''
        ...
    
    @m22.setter
    def m22(self, value : float):
        '''Value at row 2, column 2 of the matrix.'''
        ...
    
    @property
    def m23(self) -> float:
        '''Value at row 2, column 3 of the matrix.'''
        ...
    
    @m23.setter
    def m23(self, value : float):
        '''Value at row 2, column 3 of the matrix.'''
        ...
    
    @property
    def m24(self) -> float:
        '''Value at row 2, column 4 of the matrix.'''
        ...
    
    @m24.setter
    def m24(self, value : float):
        '''Value at row 2, column 4 of the matrix.'''
        ...
    
    @property
    def m31(self) -> float:
        '''Value at row 3, column 1 of the matrix.'''
        ...
    
    @m31.setter
    def m31(self, value : float):
        '''Value at row 3, column 1 of the matrix.'''
        ...
    
    @property
    def m32(self) -> float:
        '''Value at row 3, column 2 of the matrix.'''
        ...
    
    @m32.setter
    def m32(self, value : float):
        '''Value at row 3, column 2 of the matrix.'''
        ...
    
    @property
    def m33(self) -> float:
        '''Value at row 3, column 3 of the matrix.'''
        ...
    
    @m33.setter
    def m33(self, value : float):
        '''Value at row 3, column 3 of the matrix.'''
        ...
    
    @property
    def m34(self) -> float:
        '''Value at row 3, column 4 of the matrix.'''
        ...
    
    @m34.setter
    def m34(self, value : float):
        '''Value at row 3, column 4 of the matrix.'''
        ...
    
    @property
    def m41(self) -> float:
        '''Value at row 4, column 1 of the matrix.'''
        ...
    
    @m41.setter
    def m41(self, value : float):
        '''Value at row 4, column 1 of the matrix.'''
        ...
    
    @property
    def m42(self) -> float:
        '''Value at row 4, column 2 of the matrix.'''
        ...
    
    @m42.setter
    def m42(self, value : float):
        '''Value at row 4, column 2 of the matrix.'''
        ...
    
    @property
    def m43(self) -> float:
        '''Value at row 4, column 3 of the matrix.'''
        ...
    
    @m43.setter
    def m43(self, value : float):
        '''Value at row 4, column 3 of the matrix.'''
        ...
    
    @property
    def m44(self) -> float:
        '''Value at row 4, column 4 of the matrix.'''
        ...
    
    @m44.setter
    def m44(self, value : float):
        '''Value at row 4, column 4 of the matrix.'''
        ...
    
    ...

class Matrix4x4Factory:
    
    ...

class Projection:
    '''Utility class to calculate camera matrices'''
    
    ...

class SparseWeight8:
    '''Represents a sparse collection of non zero weight values, with a maximum of 8 weights.'''
    
    def equals(self, other : aspose.cad.fileformats.glb.transforms.SparseWeight8) -> bool:
        ...
    
    def expand(self, count : int) -> Iterable[float]:
        ...
    
    def get_trimmed(self, max_weights : int) -> aspose.cad.fileformats.glb.transforms.SparseWeight8:
        ...
    
    def get_normalized(self) -> aspose.cad.fileformats.glb.transforms.SparseWeight8:
        ...
    
    @property
    def count(self) -> int:
        ...
    
    @property
    def is_weightless(self) -> bool:
        ...
    
    @property
    def weight_sum(self) -> float:
        ...
    
    @property
    def max_index(self) -> int:
        ...
    
    @property
    def INDEX0(self) -> int:
        ...
    
    @property
    def WEIGHT0(self) -> float:
        ...
    
    @property
    def INDEX1(self) -> int:
        ...
    
    @property
    def WEIGHT1(self) -> float:
        ...
    
    @property
    def INDEX2(self) -> int:
        ...
    
    @property
    def WEIGHT2(self) -> float:
        ...
    
    @property
    def INDEX3(self) -> int:
        ...
    
    @property
    def WEIGHT3(self) -> float:
        ...
    
    @property
    def INDEX4(self) -> int:
        ...
    
    @property
    def WEIGHT4(self) -> float:
        ...
    
    @property
    def INDEX5(self) -> int:
        ...
    
    @property
    def WEIGHT5(self) -> float:
        ...
    
    @property
    def INDEX6(self) -> int:
        ...
    
    @property
    def WEIGHT6(self) -> float:
        ...
    
    @property
    def INDEX7(self) -> int:
        ...
    
    @property
    def WEIGHT7(self) -> float:
        ...
    
    def __getitem__(self, key : int) -> float:
        ...
    
    ...

