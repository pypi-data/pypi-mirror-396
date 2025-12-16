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

class DwfResult:
    '''Represents operations result'''
    
    @classmethod
    @property
    def SUCCESS(cls) -> DwfResult:
        '''Success result'''
        ...
    
    @classmethod
    @property
    def WAITING_FOR_DATA(cls) -> DwfResult:
        '''Waiting_For_Data'''
        ...
    
    @classmethod
    @property
    def CORRUPT_FILE_ERROR(cls) -> DwfResult:
        '''Corrupt file error'''
        ...
    
    @classmethod
    @property
    def END_OF_FILE_ERROR(cls) -> DwfResult:
        '''End of file error'''
        ...
    
    @classmethod
    @property
    def UNKNOWN_FILE_READ_ERROR(cls) -> DwfResult:
        '''UnknownFileReadError'''
        ...
    
    @classmethod
    @property
    def OUT_OF_MEMORY_ERROR(cls) -> DwfResult:
        '''Out of memory error'''
        ...
    
    @classmethod
    @property
    def FILE_ALREADY_OPEN_ERROR(cls) -> DwfResult:
        '''File already open error'''
        ...
    
    @classmethod
    @property
    def NO_FILE_OPEN_ERROR(cls) -> DwfResult:
        '''No file open error'''
        ...
    
    @classmethod
    @property
    def FILE_WRITE_ERROR(cls) -> DwfResult:
        '''File write error'''
        ...
    
    @classmethod
    @property
    def FILE_OPEN_ERROR(cls) -> DwfResult:
        '''File open error'''
        ...
    
    @classmethod
    @property
    def INTERNAL_ERROR(cls) -> DwfResult:
        '''Internal error'''
        ...
    
    @classmethod
    @property
    def NOT_ADWF_FILE_ERROR(cls) -> DwfResult:
        '''Not a DWF file error'''
        ...
    
    @classmethod
    @property
    def USER_REQUESTED_ABORT(cls) -> DwfResult:
        '''User requested abort'''
        ...
    
    @classmethod
    @property
    def DWF_VERSION_HIGHER_THAN_TOOLKIT(cls) -> DwfResult:
        '''DWF Version Higher Than Toolkit'''
        ...
    
    @classmethod
    @property
    def UNSUPPORTED_DWF_OPCODE(cls) -> DwfResult:
        '''Unsupported DWF Opcode'''
        ...
    
    @classmethod
    @property
    def UNSUPPORTED_DWF_EXTENSION_ERROR(cls) -> DwfResult:
        '''Unsupported DWF ExtensionError'''
        ...
    
    @classmethod
    @property
    def END_OF_DWF_OPCODE_FOUND(cls) -> DwfResult:
        '''End of DWF OpcodeFound'''
        ...
    
    @classmethod
    @property
    def FILE_INCONSISTENCY_WARNING(cls) -> DwfResult:
        '''File inconsistency warning'''
        ...
    
    @classmethod
    @property
    def TOOLKIT_USAGE_ERROR(cls) -> DwfResult:
        '''Toolkit usage error'''
        ...
    
    @classmethod
    @property
    def DECOMPRESSION_TERMINATED(cls) -> DwfResult:
        '''Decompression terminated'''
        ...
    
    @classmethod
    @property
    def FILE_CLOSE_ERROR(cls) -> DwfResult:
        '''File close error'''
        ...
    
    @classmethod
    @property
    def OPCODE_NOT_VALID_FOR_THIS_OBJECT(cls) -> DwfResult:
        '''OpcodeNotValidForThisObject'''
        ...
    
    @classmethod
    @property
    def DWF_PACKAGE_FORMAT(cls) -> DwfResult:
        '''DWF Package Format'''
        ...
    
    @classmethod
    @property
    def MINOR_VERSION_WARNING(cls) -> DwfResult:
        '''Minor version warning'''
        ...
    
    @classmethod
    @property
    def UNDEFINED(cls) -> DwfResult:
        '''Undefined result'''
        ...
    
    ...

class DwfWhipImageFormat:
    '''Represents image format'''
    
    @classmethod
    @property
    def UNDEFINED(cls) -> DwfWhipImageFormat:
        '''The undefined.'''
        ...
    
    @classmethod
    @property
    def BITONAL_MAPPED(cls) -> DwfWhipImageFormat:
        '''The bitonal mapped'''
        ...
    
    @classmethod
    @property
    def GROUP_3X_MAPPED(cls) -> DwfWhipImageFormat:
        '''The group3 x mapped'''
        ...
    
    @classmethod
    @property
    def INDEXED(cls) -> DwfWhipImageFormat:
        '''The indexed'''
        ...
    
    @classmethod
    @property
    def MAPPED(cls) -> DwfWhipImageFormat:
        '''The mapped'''
        ...
    
    @classmethod
    @property
    def RGB(cls) -> DwfWhipImageFormat:
        '''The RGB'''
        ...
    
    @classmethod
    @property
    def RGBA(cls) -> DwfWhipImageFormat:
        '''The RGB'''
        ...
    
    @classmethod
    @property
    def JPEG(cls) -> DwfWhipImageFormat:
        '''The JPEG'''
        ...
    
    ...

class DwfWhipPNGGroup4ImageFormat:
    '''Represents PNG group image format'''
    
    @classmethod
    @property
    def GROUP_4X_MAPPED(cls) -> DwfWhipPNGGroup4ImageFormat:
        '''Group4X mapped image format'''
        ...
    
    @classmethod
    @property
    def GROUP4(cls) -> DwfWhipPNGGroup4ImageFormat:
        '''Group4 image format'''
        ...
    
    @classmethod
    @property
    def PNG(cls) -> DwfWhipPNGGroup4ImageFormat:
        '''PNG image format'''
        ...
    
    ...

class MaterializeStage:
    '''Represents materialization stage'''
    
    @classmethod
    @property
    def EATING_INITIAL_WHITESPACE(cls) -> MaterializeStage:
        '''Eating initial whitespace'''
        ...
    
    @classmethod
    @property
    def GATHERING_STRING(cls) -> MaterializeStage:
        '''Gathering String'''
        ...
    
    @classmethod
    @property
    def EATING_END_WHITESPACE(cls) -> MaterializeStage:
        '''Eating end whitespace'''
        ...
    
    ...

