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

class SpecificationModeTools:
    
    @staticmethod
    def get_mode(mode : int) -> aspose.cad.fileformats.cgm.enums.SpecificationMode:
        ...
    
    ...

class ClassCode:
    
    @classmethod
    @property
    def DELIMITER_ELEMENT(cls) -> ClassCode:
        ...
    
    @classmethod
    @property
    def METAFILE_DESCRIPTOR_ELEMENTS(cls) -> ClassCode:
        ...
    
    @classmethod
    @property
    def PICTURE_DESCRIPTOR_ELEMENTS(cls) -> ClassCode:
        ...
    
    @classmethod
    @property
    def CONTROL_ELEMENTS(cls) -> ClassCode:
        ...
    
    @classmethod
    @property
    def GRAPHICAL_PRIMITIVE_ELEMENTS(cls) -> ClassCode:
        ...
    
    @classmethod
    @property
    def ATTRIBUTE_ELEMENTS(cls) -> ClassCode:
        ...
    
    @classmethod
    @property
    def ESCAPE_ELEMENT(cls) -> ClassCode:
        ...
    
    @classmethod
    @property
    def EXTERNAL_ELEMENTS(cls) -> ClassCode:
        ...
    
    @classmethod
    @property
    def SEGMENT_CONTROLAND_SEGMENT_ATTRIBUTE_ELEMENTS(cls) -> ClassCode:
        ...
    
    @classmethod
    @property
    def APPLICATION_STRUCTURE_DESCRIPTOR_ELEMENTS(cls) -> ClassCode:
        ...
    
    @classmethod
    @property
    def RESERVED_FOR_FUTURE_USE1(cls) -> ClassCode:
        ...
    
    @classmethod
    @property
    def RESERVED_FOR_FUTURE_USE2(cls) -> ClassCode:
        ...
    
    @classmethod
    @property
    def RESERVED_FOR_FUTURE_USE3(cls) -> ClassCode:
        ...
    
    @classmethod
    @property
    def RESERVED_FOR_FUTURE_USE4(cls) -> ClassCode:
        ...
    
    @classmethod
    @property
    def RESERVED_FOR_FUTURE_USE5(cls) -> ClassCode:
        ...
    
    @classmethod
    @property
    def RESERVED_FOR_FUTURE_USE6(cls) -> ClassCode:
        ...
    
    ...

class ClippingMode:
    
    @classmethod
    @property
    def LOCUS(cls) -> ClippingMode:
        ...
    
    @classmethod
    @property
    def SHAPE(cls) -> ClippingMode:
        ...
    
    @classmethod
    @property
    def LOCUSTHENSHAPE(cls) -> ClippingMode:
        ...
    
    ...

class ClosureType:
    
    @classmethod
    @property
    def PIE(cls) -> ClosureType:
        ...
    
    @classmethod
    @property
    def CHORD(cls) -> ClosureType:
        ...
    
    ...

class CompressionType:
    
    @classmethod
    @property
    def NULL_BACKGROUND(cls) -> CompressionType:
        ...
    
    @classmethod
    @property
    def NULL_FOREGROUND(cls) -> CompressionType:
        ...
    
    @classmethod
    @property
    def T6(cls) -> CompressionType:
        ...
    
    @classmethod
    @property
    def T4_1(cls) -> CompressionType:
        ...
    
    @classmethod
    @property
    def T4_2(cls) -> CompressionType:
        ...
    
    @classmethod
    @property
    def BITMAP(cls) -> CompressionType:
        ...
    
    @classmethod
    @property
    def RUN_LENGTH(cls) -> CompressionType:
        ...
    
    @classmethod
    @property
    def BASELINE_JPEG(cls) -> CompressionType:
        ...
    
    @classmethod
    @property
    def LZW(cls) -> CompressionType:
        ...
    
    @classmethod
    @property
    def PNG(cls) -> CompressionType:
        ...
    
    ...

class DashCapIndicator:
    
    @classmethod
    @property
    def UNSPECIFIED(cls) -> DashCapIndicator:
        ...
    
    @classmethod
    @property
    def BUTT(cls) -> DashCapIndicator:
        ...
    
    @classmethod
    @property
    def MATCH(cls) -> DashCapIndicator:
        ...
    
    ...

class DashType:
    
    @classmethod
    @property
    def SOLID(cls) -> DashType:
        ...
    
    @classmethod
    @property
    def DASH(cls) -> DashType:
        ...
    
    @classmethod
    @property
    def DOT(cls) -> DashType:
        ...
    
    @classmethod
    @property
    def DASH_DOT(cls) -> DashType:
        ...
    
    @classmethod
    @property
    def DASH_DOT_DOT(cls) -> DashType:
        ...
    
    ...

class JoinIndicator:
    
    @classmethod
    @property
    def UNSPECIFIED(cls) -> JoinIndicator:
        ...
    
    @classmethod
    @property
    def MITRE(cls) -> JoinIndicator:
        ...
    
    @classmethod
    @property
    def ROUND(cls) -> JoinIndicator:
        ...
    
    @classmethod
    @property
    def BEVEL(cls) -> JoinIndicator:
        ...
    
    ...

class LineCapIndicator:
    
    @classmethod
    @property
    def UNSPECIFIED(cls) -> LineCapIndicator:
        ...
    
    @classmethod
    @property
    def BUTT(cls) -> LineCapIndicator:
        ...
    
    @classmethod
    @property
    def ROUND(cls) -> LineCapIndicator:
        ...
    
    @classmethod
    @property
    def PROJECTING_SQUARE(cls) -> LineCapIndicator:
        ...
    
    @classmethod
    @property
    def TRIANGLE(cls) -> LineCapIndicator:
        ...
    
    ...

class Severity:
    
    @classmethod
    @property
    def INFO(cls) -> Severity:
        ...
    
    @classmethod
    @property
    def UNSUPPORTED(cls) -> Severity:
        ...
    
    @classmethod
    @property
    def UNIMPLEMENTED(cls) -> Severity:
        ...
    
    @classmethod
    @property
    def FATAL(cls) -> Severity:
        ...
    
    ...

class SpecificationMode:
    
    @classmethod
    @property
    def ABS(cls) -> SpecificationMode:
        ...
    
    @classmethod
    @property
    def SCALED(cls) -> SpecificationMode:
        ...
    
    @classmethod
    @property
    def FRACTIONAL(cls) -> SpecificationMode:
        ...
    
    @classmethod
    @property
    def MM(cls) -> SpecificationMode:
        ...
    
    ...

