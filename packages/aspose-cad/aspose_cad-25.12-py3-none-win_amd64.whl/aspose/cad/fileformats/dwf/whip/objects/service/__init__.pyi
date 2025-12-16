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

class DwfWhipFont(aspose.cad.fileformats.dwf.whip.objects.DwfWhipAttribute):
    '''Represents Font'''
    
    @property
    def is_materialized(self) -> bool:
        ...
    
    @property
    def name(self) -> aspose.cad.fileformats.dwf.whip.objects.service.font.DwfWhipOptionFontName:
        '''Gets font name'''
        ...
    
    @name.setter
    def name(self, value : aspose.cad.fileformats.dwf.whip.objects.service.font.DwfWhipOptionFontName):
        '''Gets font name'''
        ...
    
    @property
    def height(self) -> aspose.cad.fileformats.dwf.whip.objects.service.font.DwfWhipOptionFontHeight:
        '''Gets Height'''
        ...
    
    @height.setter
    def height(self, value : aspose.cad.fileformats.dwf.whip.objects.service.font.DwfWhipOptionFontHeight):
        '''Sets Height'''
        ...
    
    @property
    def rotation(self) -> aspose.cad.fileformats.dwf.whip.objects.service.font.DwfWhipOptionFontRotation:
        '''Gets rotation'''
        ...
    
    @rotation.setter
    def rotation(self, value : aspose.cad.fileformats.dwf.whip.objects.service.font.DwfWhipOptionFontRotation):
        '''Sets rotation'''
        ...
    
    @property
    def oblique(self) -> aspose.cad.fileformats.dwf.whip.objects.service.font.DwfWhipOptionFontOblique:
        '''Gets oblique'''
        ...
    
    @oblique.setter
    def oblique(self, value : aspose.cad.fileformats.dwf.whip.objects.service.font.DwfWhipOptionFontOblique):
        '''Sets oblique'''
        ...
    
    @property
    def char_set(self) -> aspose.cad.fileformats.dwf.whip.objects.service.font.DwfWhipOptionFontCharSet:
        ...
    
    @property
    def family(self) -> aspose.cad.fileformats.dwf.whip.objects.service.font.DwfWhipOptionFontFamily:
        '''Gets font family'''
        ...
    
    @property
    def width_scale(self) -> aspose.cad.fileformats.dwf.whip.objects.service.font.DwfWhipOptionFontWidthScale:
        ...
    
    @property
    def flags(self) -> aspose.cad.fileformats.dwf.whip.objects.service.font.DwfWhipOptionFontFlags:
        '''Gets options flags'''
        ...
    
    @property
    def pitch(self) -> aspose.cad.fileformats.dwf.whip.objects.service.font.DwfWhipOptionPitch:
        '''Gets pitch'''
        ...
    
    @property
    def style(self) -> aspose.cad.fileformats.dwf.whip.objects.service.font.DwfWhipOptionFontStyle:
        '''Gets style'''
        ...
    
    ...

class DwfWhipLineCapStyle(aspose.cad.fileformats.dwf.whip.objects.DwfWhipAttribute):
    '''Represents line cap style'''
    
    @property
    def is_materialized(self) -> bool:
        ...
    
    @property
    def style(self) -> aspose.cad.fileformats.dwf.whip.objects.service.DwfWhipCapStyleID:
        '''Gets cap style'''
        ...
    
    ...

class DwfWhipLineJoinStyle(aspose.cad.fileformats.dwf.whip.objects.DwfWhipAttribute):
    '''Represents Line join style'''
    
    @property
    def is_materialized(self) -> bool:
        ...
    
    @property
    def style(self) -> aspose.cad.fileformats.dwf.whip.objects.service.DwfWhipJoinstyleID:
        '''Gets line join style'''
        ...
    
    ...

class DwfWhipLineStyle(aspose.cad.fileformats.dwf.whip.objects.DwfWhipAttribute):
    '''Represents line style'''
    
    @property
    def is_materialized(self) -> bool:
        ...
    
    @property
    def join_style(self) -> aspose.cad.fileformats.dwf.whip.objects.service.DwfWhipLineJoinStyle:
        ...
    
    @property
    def start_cap(self) -> aspose.cad.fileformats.dwf.whip.objects.service.DwfWhipLineCapStyle:
        ...
    
    @property
    def end_cap(self) -> aspose.cad.fileformats.dwf.whip.objects.service.DwfWhipLineCapStyle:
        ...
    
    ...

class DwfWhipLineWeight(aspose.cad.fileformats.dwf.whip.objects.DwfWhipAttribute):
    '''Represents weight of line'''
    
    @property
    def is_materialized(self) -> bool:
        ...
    
    ...

class DwfWhipCapStyleID:
    '''Represents An enumeration of cap styles used by WT_Line_End_Cap, WT_Line_Start_Cap, WT_Dash_End_Cap, and WT_Dash_Start_Cap.'''
    
    @classmethod
    @property
    def BUTT(cls) -> DwfWhipCapStyleID:
        '''Butt cap style'''
        ...
    
    @classmethod
    @property
    def SQUARE(cls) -> DwfWhipCapStyleID:
        '''Square cap style'''
        ...
    
    @classmethod
    @property
    def ROUND(cls) -> DwfWhipCapStyleID:
        '''Round cap style'''
        ...
    
    @classmethod
    @property
    def DIAMOND(cls) -> DwfWhipCapStyleID:
        '''Diamond cap style'''
        ...
    
    @classmethod
    @property
    def CAPSTYLE(cls) -> DwfWhipCapStyleID:
        '''Capstyle cap style'''
        ...
    
    @classmethod
    @property
    def UNDEFINED(cls) -> DwfWhipCapStyleID:
        '''Undefined cap style'''
        ...
    
    ...

class DwfWhipJoinstyleID:
    '''Represents join style IDs'''
    
    @classmethod
    @property
    def MITER(cls) -> DwfWhipJoinstyleID:
        '''Miter join style'''
        ...
    
    @classmethod
    @property
    def BEVEL(cls) -> DwfWhipJoinstyleID:
        '''Bevel join style'''
        ...
    
    @classmethod
    @property
    def ROUND(cls) -> DwfWhipJoinstyleID:
        '''Round join style'''
        ...
    
    @classmethod
    @property
    def DIAMOND(cls) -> DwfWhipJoinstyleID:
        '''Diamond join style'''
        ...
    
    @classmethod
    @property
    def JOINSTYLE(cls) -> DwfWhipJoinstyleID:
        '''Joinstyle join style'''
        ...
    
    @classmethod
    @property
    def UNDEFINED(cls) -> DwfWhipJoinstyleID:
        '''Undefined join style'''
        ...
    
    ...

