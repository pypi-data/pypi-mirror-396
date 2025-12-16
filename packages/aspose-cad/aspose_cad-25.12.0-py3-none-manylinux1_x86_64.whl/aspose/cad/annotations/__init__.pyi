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

class AnnotationEntity:
    
    @property
    def id(self) -> Guid:
        ...
    
    @property
    def entity(self) -> aspose.cad.annotations.IAnnotateable:
        ...
    
    @entity.setter
    def entity(self, value : aspose.cad.annotations.IAnnotateable):
        ...
    
    @property
    def text(self) -> str:
        ...
    
    @text.setter
    def text(self, value : str):
        ...
    
    @property
    def text_size(self) -> int:
        ...
    
    @text_size.setter
    def text_size(self, value : int):
        ...
    
    @property
    def color(self) -> aspose.cad.Color:
        ...
    
    @color.setter
    def color(self, value : aspose.cad.Color):
        ...
    
    @property
    def insertion_point(self) -> aspose.cad.primitives.Point3D:
        ...
    
    @insertion_point.setter
    def insertion_point(self, value : aspose.cad.primitives.Point3D):
        ...
    
    @property
    def end_point(self) -> aspose.cad.primitives.Point3D:
        ...
    
    @end_point.setter
    def end_point(self, value : aspose.cad.primitives.Point3D):
        ...
    
    ...

class AnnotationEntityBuilder:
    
    def with_entity(self, entity : aspose.cad.annotations.IAnnotateable) -> aspose.cad.annotations.AnnotationEntityBuilder:
        ...
    
    def with_text(self, text : str) -> aspose.cad.annotations.AnnotationEntityBuilder:
        ...
    
    def with_text_size(self, text_size : int) -> aspose.cad.annotations.AnnotationEntityBuilder:
        ...
    
    def with_color(self, color : aspose.cad.Color) -> aspose.cad.annotations.AnnotationEntityBuilder:
        ...
    
    def with_insertion_point(self, insertion_point : aspose.cad.primitives.Point3D) -> aspose.cad.annotations.AnnotationEntityBuilder:
        ...
    
    def with_middle_point(self, middle_point : aspose.cad.primitives.Point3D) -> aspose.cad.annotations.AnnotationEntityBuilder:
        ...
    
    def with_end_point(self, end_point : aspose.cad.primitives.Point3D) -> aspose.cad.annotations.AnnotationEntityBuilder:
        ...
    
    def with_direction(self, annotation_direction : aspose.cad.annotations.AnnotationDirection) -> aspose.cad.annotations.AnnotationEntityBuilder:
        ...
    
    def build(self) -> aspose.cad.annotations.AnnotationEntity:
        ...
    
    ...

class IAnnotateable(aspose.cad.IDrawingEntity):
    '''IAnnotateable interface'''
    
    @property
    def default_point(self) -> aspose.cad.primitives.Point3D:
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

class IAnnotationService:
    
    def init(self, image : aspose.cad.Image) -> None:
        '''Initialize annotation service with image to process
        
        :param image: image instance'''
        ...
    
    def add_annotation(self, annotation : aspose.cad.annotations.AnnotationEntity) -> None:
        '''Adds the annotation.
        
        :param annotation: The annotation.'''
        ...
    
    def get_annotations(self) -> List[aspose.cad.annotations.AnnotationEntity]:
        '''Gets the annotations.'''
        ...
    
    def refresh_annotations(self) -> None:
        '''Refreshes the annotation positions.'''
        ...
    
    def delete_annotation(self, annotation : aspose.cad.annotations.AnnotationEntity) -> None:
        '''Deletes the annotation.
        
        :param annotation: The annotation.'''
        ...
    
    ...

class AnnotationDirection:
    
    @classmethod
    @property
    def TOP_RIGHT(cls) -> AnnotationDirection:
        ...
    
    @classmethod
    @property
    def BOTTOM_RIGHT(cls) -> AnnotationDirection:
        ...
    
    @classmethod
    @property
    def BOTTOM_LEFT(cls) -> AnnotationDirection:
        ...
    
    @classmethod
    @property
    def TOP_LEFT(cls) -> AnnotationDirection:
        ...
    
    ...

