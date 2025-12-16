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

class ColorDataUnit:
    '''Customize the color of the surface.'''
    
    def to_argb(self) -> int:
        '''Gets ARGB value.
        
        :returns: The result.'''
        ...
    
    @property
    def use_color(self) -> bool:
        ...
    
    @use_color.setter
    def use_color(self, value : bool):
        ...
    
    @property
    def r(self) -> byte:
        '''Gets the intensity level of red color (values from 0 to 31).'''
        ...
    
    @r.setter
    def r(self, value : byte):
        '''Sets the intensity level of red color (values from 0 to 31).'''
        ...
    
    @property
    def g(self) -> byte:
        '''Gets the intensity level of green color (values from 0 to 31).'''
        ...
    
    @g.setter
    def g(self, value : byte):
        '''Sets the intensity level of green color (values from 0 to 31).'''
        ...
    
    @property
    def b(self) -> byte:
        '''Gets the intensity level of blue color (values from 0 to 31).'''
        ...
    
    @b.setter
    def b(self, value : byte):
        '''Sets the intensity level of blue color (values from 0 to 31).'''
        ...
    
    ...

class NormalDataUnit:
    '''Normal to the surface.'''
    
    ...

class StlFace:
    '''Represents the face object for Stl image.
    It stores indices of vertex, texture and normal.'''
    
    @property
    def normal_inds(self) -> List[int]:
        ...
    
    @normal_inds.setter
    def normal_inds(self, value : List[int]):
        ...
    
    @property
    def vertex_inds(self) -> List[int]:
        ...
    
    @vertex_inds.setter
    def vertex_inds(self, value : List[int]):
        ...
    
    ...

class StlRoot:
    '''Represents root information for STL drawing.
    StlRoot contains data about vertices, materials, and shapes.
    Each shape contains information about set of faces with corresponding material, vertex and normal indices.'''
    
    def add_vertex(self, stl_vertex : aspose.cad.fileformats.stl.stlobjects.VertexDataUnit) -> int:
        '''Add vertex.
        
        :param stl_vertex: The vertex.
        :returns: The index of added vertex in collection.'''
        ...
    
    @property
    def shapes(self) -> List[aspose.cad.fileformats.stl.stlobjects.StlShape]:
        '''Gets the shapes.'''
        ...
    
    @shapes.setter
    def shapes(self, value : List[aspose.cad.fileformats.stl.stlobjects.StlShape]):
        '''Sets the shapes.'''
        ...
    
    ...

class StlShape:
    '''Represents a shape object for Stl format.
    Contains information about set of faces with corresponding material, vertex, texture, and normal indices.'''
    
    @property
    def name(self) -> str:
        '''Gets the name.'''
        ...
    
    @name.setter
    def name(self, value : str):
        '''Sets the name.'''
        ...
    
    @property
    def faces(self) -> List[aspose.cad.fileformats.stl.stlobjects.StlFace]:
        '''Gets the faces.'''
        ...
    
    @faces.setter
    def faces(self, value : List[aspose.cad.fileformats.stl.stlobjects.StlFace]):
        '''Sets the faces.'''
        ...
    
    @property
    def facets(self) -> List[aspose.cad.fileformats.stl.stlobjects.TriangularFacet]:
        ...
    
    @facets.setter
    def facets(self, value : List[aspose.cad.fileformats.stl.stlobjects.TriangularFacet]):
        ...
    
    @property
    def material_id(self) -> int:
        ...
    
    @material_id.setter
    def material_id(self, value : int):
        ...
    
    ...

class TriangularFacet(aspose.cad.IDrawingEntity):
    '''Triangular facet of the surface.'''
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
        ...
    
    @property
    def normal(self) -> aspose.cad.fileformats.stl.stlobjects.NormalDataUnit:
        '''Gets the surface normal to the triangular facet.'''
        ...
    
    @normal.setter
    def normal(self, value : aspose.cad.fileformats.stl.stlobjects.NormalDataUnit):
        '''Sets the surface normal to the triangular facet.'''
        ...
    
    @property
    def vertex1(self) -> aspose.cad.fileformats.stl.stlobjects.VertexDataUnit:
        '''Gets the coordinates of the first vertex.'''
        ...
    
    @vertex1.setter
    def vertex1(self, value : aspose.cad.fileformats.stl.stlobjects.VertexDataUnit):
        '''Sets the coordinates of the first vertex.'''
        ...
    
    @property
    def vertex2(self) -> aspose.cad.fileformats.stl.stlobjects.VertexDataUnit:
        '''Gets the coordinates of the second vertex.'''
        ...
    
    @vertex2.setter
    def vertex2(self, value : aspose.cad.fileformats.stl.stlobjects.VertexDataUnit):
        '''Sets the coordinates of the second vertex.'''
        ...
    
    @property
    def vertex3(self) -> aspose.cad.fileformats.stl.stlobjects.VertexDataUnit:
        '''Gets the coordinates of the third vertex.'''
        ...
    
    @vertex3.setter
    def vertex3(self, value : aspose.cad.fileformats.stl.stlobjects.VertexDataUnit):
        '''Sets the coordinates of the third vertex.'''
        ...
    
    @property
    def color_data(self) -> aspose.cad.fileformats.stl.stlobjects.ColorDataUnit:
        ...
    
    @color_data.setter
    def color_data(self, value : aspose.cad.fileformats.stl.stlobjects.ColorDataUnit):
        ...
    
    ...

class VertexDataUnit:
    '''The coordinates of the vertices triangle facets.'''
    
    def equals(self, other : aspose.cad.fileformats.stl.stlobjects.VertexDataUnit) -> bool:
        '''Indicates whether the current object is equal to another object of the same type.
        
        :param other: An object to compare with this object.
        :returns: true if the current object is equal to the ``other`` parameter; otherwise, false.'''
        ...
    
    @property
    def x(self) -> float:
        '''Gets the X-Coordinate.'''
        ...
    
    @property
    def y(self) -> float:
        '''Gets the Y-Coordinate.'''
        ...
    
    @property
    def z(self) -> float:
        '''Gets the Z-Coordinate.'''
        ...
    
    ...

