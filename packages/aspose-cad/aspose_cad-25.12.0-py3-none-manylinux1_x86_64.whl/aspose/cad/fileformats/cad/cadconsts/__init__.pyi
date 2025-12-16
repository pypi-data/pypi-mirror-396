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

class CadApplicationCodesContainerValues:
    '''Constants values for containers code values'''
    
    @classmethod
    @property
    def VISUAL_STYLE(cls) -> str:
        '''The visual style'''
        ...
    
    @classmethod
    @property
    def GRID_DISPLAY(cls) -> str:
        '''The grid display'''
        ...
    
    @classmethod
    @property
    def GRID_MAJOR(cls) -> str:
        '''The grid major'''
        ...
    
    @classmethod
    @property
    def DEFAULT_LIGHTING(cls) -> str:
        '''The default lighting'''
        ...
    
    @classmethod
    @property
    def DEFAULT_LIGHTING_TYPE(cls) -> str:
        '''The default lighting type'''
        ...
    
    @classmethod
    @property
    def BRIGHTNESS(cls) -> str:
        '''The brightness'''
        ...
    
    @classmethod
    @property
    def CONTRAST(cls) -> str:
        '''The contrast'''
        ...
    
    @classmethod
    @property
    def DISPLAY_NAME(cls) -> str:
        '''The display name'''
        ...
    
    @classmethod
    @property
    def FLAGS(cls) -> str:
        '''The flags value'''
        ...
    
    @classmethod
    @property
    def ACAD(cls) -> str:
        '''The acad prefix.'''
        ...
    
    @classmethod
    @property
    def RTVS_PROPERTIES_PREFIX(cls) -> str:
        '''The RTVS properties prefix.'''
        ...
    
    ...

class CadCommon:
    '''General constant values for Cad file format.'''
    
    @staticmethod
    def get_type_name(enum_object : any, front_additive : str) -> str:
        '''Gets the name of the enum variable type.
        
        :param enum_object: Name of the enum object.
        :param front_additive: string added to the front.
        :returns: string name of the enum variable type'''
        ...
    
    @classmethod
    @property
    def DIVIDER(cls) -> int:
        '''Begin section marker'''
        ...
    
    @classmethod
    @property
    def END_SECTION(cls) -> str:
        ...
    
    @classmethod
    @property
    def END_TABLE(cls) -> str:
        ...
    
    @classmethod
    @property
    def END_BLOCK(cls) -> str:
        ...
    
    @classmethod
    @property
    def BLOCK_NAME(cls) -> int:
        ...
    
    @classmethod
    @property
    def EOF(cls) -> str:
        '''Variable namning for EOF'''
        ...
    
    @classmethod
    @property
    def HELPER_SYMBOL(cls) -> str:
        ...
    
    @classmethod
    @property
    def SECTION_TITLE(cls) -> int:
        ...
    
    @classmethod
    @property
    def START_SECTION(cls) -> str:
        ...
    
    @classmethod
    @property
    def THUMBNAIL_IMAGE(cls) -> str:
        ...
    
    @classmethod
    @property
    def START_HEADER(cls) -> str:
        ...
    
    @classmethod
    @property
    def START_TABLES(cls) -> str:
        ...
    
    @classmethod
    @property
    def START_TABLE(cls) -> str:
        ...
    
    @classmethod
    @property
    def SUBCLASS_MARKER(cls) -> int:
        ...
    
    @classmethod
    @property
    def VAR_NAME_MARKER(cls) -> int:
        ...
    
    @classmethod
    @property
    def VAR_PREFIX(cls) -> str:
        ...
    
    @classmethod
    @property
    def DICTIONARY(cls) -> str:
        '''The dictionary'''
        ...
    
    @classmethod
    @property
    def DEFAULT_TEXT_STYLE(cls) -> str:
        '''The DEFAULT TEXT STYLE const'''
        ...
    
    @classmethod
    @property
    def FACE3D_ENTITY_NAME(cls) -> str:
        '''The face 3d entity name'''
        ...
    
    @classmethod
    @property
    def COORDINATION_MODEL_NAME(cls) -> str:
        '''The coordination model'''
        ...
    
    @classmethod
    @property
    def SOLID3D_ENTITY_NAME(cls) -> str:
        '''The solid 3d entity name'''
        ...
    
    @classmethod
    @property
    def MLEADER_ENTITY_NAME(cls) -> str:
        '''The mleader entity name'''
        ...
    
    @classmethod
    @property
    def WFPREC3DD_HEADER_VARIABLE(cls) -> str:
        '''The WFPREC3DD header variable'''
        ...
    
    @classmethod
    @property
    def REVERSE_WFPREC3DD_HEADER_VARIABLE(cls) -> str:
        '''The reverse WFPREC3DD header variable'''
        ...
    
    @classmethod
    @property
    def DWGCODEPAGE(cls) -> str:
        '''Codepage used for strings in the file'''
        ...
    
    @classmethod
    @property
    def ACADVER(cls) -> str:
        '''Version of file format'''
        ...
    
    @classmethod
    @property
    def standard_style(cls) -> str:
        '''The standard style.'''
        ...
    
    @classmethod
    @standard_style.setter
    def standard_style(cls, value : str):
        '''The standard style.'''
        ...
    
    @classmethod
    @property
    def BY_LAYER(cls) -> str:
        ...
    
    @classmethod
    @property
    def CUSTOM_PROPERTY_TAG(cls) -> str:
        ...
    
    @classmethod
    @property
    def CUSTOM_PROPERTY(cls) -> str:
        ...
    
    ...

class CadTableNames:
    '''The Cad table names.'''
    
    @classmethod
    @property
    def APPLICATION_ID_TABLE(cls) -> str:
        ...
    
    @classmethod
    @property
    def BEGIN_BLOCK(cls) -> str:
        ...
    
    @classmethod
    @property
    def BEGIN_CLASS(cls) -> str:
        ...
    
    @classmethod
    @property
    def BEGIN_SECTION(cls) -> str:
        ...
    
    @classmethod
    @property
    def BLOCK_RECORD_TABLE(cls) -> str:
        ...
    
    @classmethod
    @property
    def BLOCKS_SECTION(cls) -> str:
        ...
    
    @classmethod
    @property
    def CLASSES_SECTION(cls) -> str:
        ...
    
    @classmethod
    @property
    def DICTIONARY(cls) -> str:
        '''dictionary'''
        ...
    
    @classmethod
    @property
    def DIMENSION_STYLE_TABLE(cls) -> str:
        ...
    
    @classmethod
    @property
    def END_BLOCK(cls) -> str:
        ...
    
    @classmethod
    @property
    def END_OF_FILE(cls) -> str:
        ...
    
    @classmethod
    @property
    def END_SECTION(cls) -> str:
        ...
    
    @classmethod
    @property
    def END_SEQUENCE(cls) -> str:
        ...
    
    @classmethod
    @property
    def END_TABLE(cls) -> str:
        ...
    
    @classmethod
    @property
    def ENTITIES_SECTION(cls) -> str:
        ...
    
    @classmethod
    @property
    def HEADER_SECTION(cls) -> str:
        ...
    
    @classmethod
    @property
    def LAYER_TABLE(cls) -> str:
        ...
    
    @classmethod
    @property
    def LINE_TYPE_TABLE(cls) -> str:
        ...
    
    @classmethod
    @property
    def OBJECTS_SECTION(cls) -> str:
        ...
    
    @classmethod
    @property
    def TABLE(cls) -> str:
        '''Cad name string.'''
        ...
    
    @classmethod
    @property
    def TABLES_SECTION(cls) -> str:
        ...
    
    @classmethod
    @property
    def TEXT_STYLE_TABLE(cls) -> str:
        ...
    
    @classmethod
    @property
    def UCS_TABLE(cls) -> str:
        ...
    
    @classmethod
    @property
    def UNKNOWN(cls) -> str:
        '''not defined .'''
        ...
    
    @classmethod
    @property
    def VIEW_PORT_TABLE(cls) -> str:
        ...
    
    @classmethod
    @property
    def VIEW_TABLE(cls) -> str:
        ...
    
    ...

class CadAcadVersion:
    '''Autocad version enum'''
    
    @classmethod
    @property
    def NONE(cls) -> CadAcadVersion:
        '''Value for non-versioned'''
        ...
    
    @classmethod
    @property
    def AC1006(cls) -> CadAcadVersion:
        '''Value the AutoCAD drawing database R10 version number string marker'''
        ...
    
    @classmethod
    @property
    def AC1009(cls) -> CadAcadVersion:
        '''Value the AutoCAD drawing database R11 and R12 version number string marker'''
        ...
    
    @classmethod
    @property
    def AC1012(cls) -> CadAcadVersion:
        '''Value the AutoCAD drawing database R13 version number string marker'''
        ...
    
    @classmethod
    @property
    def AC1014(cls) -> CadAcadVersion:
        '''Value the AutoCAD drawing database R14 version number string marker'''
        ...
    
    @classmethod
    @property
    def AC1015(cls) -> CadAcadVersion:
        '''Value the AutoCAD drawing database AutoCAD 2000 version number string marker'''
        ...
    
    @classmethod
    @property
    def AC1018(cls) -> CadAcadVersion:
        '''Value the AutoCAD drawing database AutoCAD 2004 version number string marker'''
        ...
    
    @classmethod
    @property
    def AC1021(cls) -> CadAcadVersion:
        '''Value the AutoCAD drawing database AutoCAD 2007 version number string marker'''
        ...
    
    @classmethod
    @property
    def AC1024(cls) -> CadAcadVersion:
        '''Value the AutoCAD drawing database AutoCAD 2010 version number string marker'''
        ...
    
    @classmethod
    @property
    def AC1027(cls) -> CadAcadVersion:
        '''Value the AutoCAD drawing database AutoCAD 2013 version number string marker'''
        ...
    
    @classmethod
    @property
    def AC1032(cls) -> CadAcadVersion:
        '''Value the AutoCAD drawing database AutoCAD 2018 version number string marker'''
        ...
    
    ...

class CadAcdsTypeName:
    '''Contains Acds names'''
    
    @classmethod
    @property
    def NONE(cls) -> CadAcdsTypeName:
        '''NONE - default type'''
        ...
    
    @classmethod
    @property
    def ACDSDATA(cls) -> CadAcdsTypeName:
        '''The ACDSDATA object'''
        ...
    
    @classmethod
    @property
    def ACDSSCHEMA(cls) -> CadAcdsTypeName:
        '''The ACDSSCHEMA object'''
        ...
    
    @classmethod
    @property
    def ACDSRECORD(cls) -> CadAcdsTypeName:
        '''The ACDSRECORD object'''
        ...
    
    ...

class CadAttachmentPoint:
    '''The Cad attachment point.'''
    
    @classmethod
    @property
    def TOP_LEFT(cls) -> CadAttachmentPoint:
        '''Top left attachment point.'''
        ...
    
    @classmethod
    @property
    def TOP_CENTER(cls) -> CadAttachmentPoint:
        '''Top center  attachment point.'''
        ...
    
    @classmethod
    @property
    def TOP_RIGHT(cls) -> CadAttachmentPoint:
        '''Top right attachment point.'''
        ...
    
    @classmethod
    @property
    def MIDDLE_LEFT(cls) -> CadAttachmentPoint:
        '''Middle left attachment point.'''
        ...
    
    @classmethod
    @property
    def MIDDLE_CENTER(cls) -> CadAttachmentPoint:
        '''Middle center attachment point.'''
        ...
    
    @classmethod
    @property
    def MIDDLE_RIGHT(cls) -> CadAttachmentPoint:
        '''Middle right attachment point.'''
        ...
    
    @classmethod
    @property
    def BOTTOM_LEFT(cls) -> CadAttachmentPoint:
        '''Bottom left attachment point.'''
        ...
    
    @classmethod
    @property
    def BOTTOM_CENTER(cls) -> CadAttachmentPoint:
        '''Bottom center attachment point.'''
        ...
    
    @classmethod
    @property
    def BOTTOM_RIGHT(cls) -> CadAttachmentPoint:
        '''Bottom right attachment point.'''
        ...
    
    ...

class CadAttachmentType:
    '''Cad attachment point type'''
    
    @classmethod
    @property
    def TOP_LEFT(cls) -> CadAttachmentType:
        '''The top left'''
        ...
    
    @classmethod
    @property
    def TOP_CENTER(cls) -> CadAttachmentType:
        '''The top center'''
        ...
    
    @classmethod
    @property
    def TOP_RIGHT(cls) -> CadAttachmentType:
        '''The top right'''
        ...
    
    @classmethod
    @property
    def MIDDLE_LEFT(cls) -> CadAttachmentType:
        '''The middle left'''
        ...
    
    @classmethod
    @property
    def MIDDLE_CENTER(cls) -> CadAttachmentType:
        '''The middle center'''
        ...
    
    @classmethod
    @property
    def MIDDLE_RIGHT(cls) -> CadAttachmentType:
        '''The middle right'''
        ...
    
    @classmethod
    @property
    def BOTTOM_LEFT(cls) -> CadAttachmentType:
        '''The bottom left'''
        ...
    
    @classmethod
    @property
    def BOTTOM_CENTER(cls) -> CadAttachmentType:
        '''The bottom center'''
        ...
    
    @classmethod
    @property
    def BOTTOM_RIGHT(cls) -> CadAttachmentType:
        '''The bottom right'''
        ...
    
    ...

class CadBoundaryPathTypeFlag:
    '''The boundary path type flag.'''
    
    @classmethod
    @property
    def DEFAULT(cls) -> CadBoundaryPathTypeFlag:
        '''Default boundary type.'''
        ...
    
    @classmethod
    @property
    def EXTERNAL(cls) -> CadBoundaryPathTypeFlag:
        '''External  boundary type.'''
        ...
    
    @classmethod
    @property
    def POLYLINE(cls) -> CadBoundaryPathTypeFlag:
        '''Polyline boundary type.'''
        ...
    
    @classmethod
    @property
    def DERIVED(cls) -> CadBoundaryPathTypeFlag:
        '''Derived boundary type.'''
        ...
    
    @classmethod
    @property
    def TEXTBOX(cls) -> CadBoundaryPathTypeFlag:
        '''Textbox boundary type.'''
        ...
    
    @classmethod
    @property
    def OUTERMOST(cls) -> CadBoundaryPathTypeFlag:
        '''Outermost boundary type.'''
        ...
    
    ...

class CadDimensionType:
    '''Cad Dimension type enum'''
    
    @classmethod
    @property
    def ROTATED(cls) -> CadDimensionType:
        '''The rotated dimension type'''
        ...
    
    @classmethod
    @property
    def ALIGNED(cls) -> CadDimensionType:
        '''The aligned dimension type'''
        ...
    
    @classmethod
    @property
    def ANGULAR(cls) -> CadDimensionType:
        '''The angular dimension type'''
        ...
    
    @classmethod
    @property
    def DIAMETER(cls) -> CadDimensionType:
        '''The diameter dimension type'''
        ...
    
    @classmethod
    @property
    def RADIUS(cls) -> CadDimensionType:
        '''The radius dimension type'''
        ...
    
    @classmethod
    @property
    def ANGULAR_3_POINT(cls) -> CadDimensionType:
        '''The angular3 point dimension type'''
        ...
    
    @classmethod
    @property
    def ORDINATE(cls) -> CadDimensionType:
        '''The ordinate dimension type'''
        ...
    
    @classmethod
    @property
    def BLOCK(cls) -> CadDimensionType:
        '''The block dimension type'''
        ...
    
    ...

class CadDrawingDirection:
    '''The Cad drawing direction.'''
    
    @classmethod
    @property
    def LEFT_TO_RIGHT(cls) -> CadDrawingDirection:
        '''The left to right.'''
        ...
    
    @classmethod
    @property
    def TOP_TO_BOTTOM(cls) -> CadDrawingDirection:
        '''The top to bottom.'''
        ...
    
    @classmethod
    @property
    def BY_STYLE(cls) -> CadDrawingDirection:
        '''The by style.'''
        ...
    
    ...

class CadEntityCoordinates:
    '''The Cad entity coordinates.'''
    
    @classmethod
    @property
    def CAD10(cls) -> CadEntityCoordinates:
        '''The Cad 10.'''
        ...
    
    @classmethod
    @property
    def CAD11(cls) -> CadEntityCoordinates:
        '''The Cad 11.'''
        ...
    
    @classmethod
    @property
    def CAD12(cls) -> CadEntityCoordinates:
        '''The Cad 12.'''
        ...
    
    @classmethod
    @property
    def CAD13(cls) -> CadEntityCoordinates:
        '''The Cad 13.'''
        ...
    
    @classmethod
    @property
    def CAD14(cls) -> CadEntityCoordinates:
        '''The Cad 14.'''
        ...
    
    @classmethod
    @property
    def CAD15(cls) -> CadEntityCoordinates:
        '''The Cad 15.'''
        ...
    
    @classmethod
    @property
    def CAD16(cls) -> CadEntityCoordinates:
        '''The Cad 16.'''
        ...
    
    @classmethod
    @property
    def CAD17(cls) -> CadEntityCoordinates:
        '''The Cad 17.'''
        ...
    
    @classmethod
    @property
    def CAD18(cls) -> CadEntityCoordinates:
        '''The Cad 18.'''
        ...
    
    @classmethod
    @property
    def CAD210(cls) -> CadEntityCoordinates:
        '''The Cad 210.'''
        ...
    
    ...

class CadEntitySpaceMode:
    '''The Cad entity space mode.'''
    
    @classmethod
    @property
    def MODEL_SPACE(cls) -> CadEntitySpaceMode:
        '''The model space.'''
        ...
    
    @classmethod
    @property
    def PAPER_SPACE(cls) -> CadEntitySpaceMode:
        '''The paper space.'''
        ...
    
    ...

class CadEntityTypeName:
    '''Contains Entity names'''
    
    @classmethod
    @property
    def NONE(cls) -> CadEntityTypeName:
        '''NONE - default type'''
        ...
    
    @classmethod
    @property
    def FACE3D(cls) -> CadEntityTypeName:
        '''3DFACE entity'''
        ...
    
    @classmethod
    @property
    def SOLID3D(cls) -> CadEntityTypeName:
        '''3DSOLID entity'''
        ...
    
    @classmethod
    @property
    def ACAD_PROXY_ENTITY(cls) -> CadEntityTypeName:
        '''ACAD_PROXY_ENTITY entity'''
        ...
    
    @classmethod
    @property
    def ARC(cls) -> CadEntityTypeName:
        '''ARC entity'''
        ...
    
    @classmethod
    @property
    def ATTDEF(cls) -> CadEntityTypeName:
        '''ATTDEF entity'''
        ...
    
    @classmethod
    @property
    def ATTRIB(cls) -> CadEntityTypeName:
        '''ATTRIB entity'''
        ...
    
    @classmethod
    @property
    def BODY(cls) -> CadEntityTypeName:
        '''BODY entity'''
        ...
    
    @classmethod
    @property
    def COORDINATIONMODEL(cls) -> CadEntityTypeName:
        '''The coordination model entity'''
        ...
    
    @classmethod
    @property
    def DIMENSION(cls) -> CadEntityTypeName:
        '''DIMENSION entity'''
        ...
    
    @classmethod
    @property
    def ELLIPSE(cls) -> CadEntityTypeName:
        '''ELLIPSE entity'''
        ...
    
    @classmethod
    @property
    def HATCH(cls) -> CadEntityTypeName:
        '''HATCH entity'''
        ...
    
    @classmethod
    @property
    def HELIX(cls) -> CadEntityTypeName:
        '''HELIX entity'''
        ...
    
    @classmethod
    @property
    def HEADER(cls) -> CadEntityTypeName:
        '''HEADER entity'''
        ...
    
    @classmethod
    @property
    def IMAGE(cls) -> CadEntityTypeName:
        '''IMAGE entity'''
        ...
    
    @classmethod
    @property
    def INSERT(cls) -> CadEntityTypeName:
        '''INSERT entity'''
        ...
    
    @classmethod
    @property
    def CAD_CALLOUT_LINE(cls) -> CadEntityTypeName:
        '''Callout line entity'''
        ...
    
    @classmethod
    @property
    def CAD_CALLOUT_DATA(cls) -> CadEntityTypeName:
        '''Callout context data entity'''
        ...
    
    @classmethod
    @property
    def LEADER(cls) -> CadEntityTypeName:
        '''Callout LEADER entity'''
        ...
    
    @classmethod
    @property
    def LIGHT(cls) -> CadEntityTypeName:
        '''LIGHT entity'''
        ...
    
    @classmethod
    @property
    def LWPOLYLINE(cls) -> CadEntityTypeName:
        '''LWPOLYLINE entity'''
        ...
    
    @classmethod
    @property
    def MESH(cls) -> CadEntityTypeName:
        '''MESH entity'''
        ...
    
    @classmethod
    @property
    def MLINE(cls) -> CadEntityTypeName:
        '''MLINE entity'''
        ...
    
    @classmethod
    @property
    def CAD_CALL_OUT_STYLE(cls) -> CadEntityTypeName:
        '''MLEADERSTYLE entity'''
        ...
    
    @classmethod
    @property
    def MLEADERSTYLE(cls) -> CadEntityTypeName:
        '''MLEADERSTYLE entity'''
        ...
    
    @classmethod
    @property
    def MULTILEADER(cls) -> CadEntityTypeName:
        '''MULTILEADER entity'''
        ...
    
    @classmethod
    @property
    def MTEXT(cls) -> CadEntityTypeName:
        '''MTEXT entity'''
        ...
    
    @classmethod
    @property
    def OLEFRAME(cls) -> CadEntityTypeName:
        '''OLEFRAME entity'''
        ...
    
    @classmethod
    @property
    def OLE2FRAME(cls) -> CadEntityTypeName:
        '''OLE@FRAME entity'''
        ...
    
    @classmethod
    @property
    def POINT(cls) -> CadEntityTypeName:
        '''POINT entity'''
        ...
    
    @classmethod
    @property
    def POLYLINE(cls) -> CadEntityTypeName:
        '''POLYLINE entity'''
        ...
    
    @classmethod
    @property
    def RAY(cls) -> CadEntityTypeName:
        '''RAY entity'''
        ...
    
    @classmethod
    @property
    def REGION(cls) -> CadEntityTypeName:
        '''REGION entity'''
        ...
    
    @classmethod
    @property
    def SECTION(cls) -> CadEntityTypeName:
        '''SECTION entity'''
        ...
    
    @classmethod
    @property
    def SEQEND(cls) -> CadEntityTypeName:
        '''SEQEND entity'''
        ...
    
    @classmethod
    @property
    def SHAPE(cls) -> CadEntityTypeName:
        '''SHAPE entity'''
        ...
    
    @classmethod
    @property
    def SOLID(cls) -> CadEntityTypeName:
        '''SOLID entity'''
        ...
    
    @classmethod
    @property
    def SPLINE(cls) -> CadEntityTypeName:
        '''SPLINE entity'''
        ...
    
    @classmethod
    @property
    def SUN(cls) -> CadEntityTypeName:
        '''SUN entity'''
        ...
    
    @classmethod
    @property
    def SURFACE(cls) -> CadEntityTypeName:
        '''SURFACE entity'''
        ...
    
    @classmethod
    @property
    def ACAD_TABLE(cls) -> CadEntityTypeName:
        '''TABLE entity'''
        ...
    
    @classmethod
    @property
    def TEXT(cls) -> CadEntityTypeName:
        '''TEXT entity'''
        ...
    
    @classmethod
    @property
    def UNDERLAY(cls) -> CadEntityTypeName:
        '''UNDERLAY entity'''
        ...
    
    @classmethod
    @property
    def PDFUNDERLAY(cls) -> CadEntityTypeName:
        '''PDFUNDERLAY entity'''
        ...
    
    @classmethod
    @property
    def DWFUNDERLAY(cls) -> CadEntityTypeName:
        '''DWFUNDERLAY entity'''
        ...
    
    @classmethod
    @property
    def DGNUNDERLAY(cls) -> CadEntityTypeName:
        '''DGNUNDERLAY entity'''
        ...
    
    @classmethod
    @property
    def VERTEX(cls) -> CadEntityTypeName:
        '''VERTEX entity'''
        ...
    
    @classmethod
    @property
    def VIEWPORT(cls) -> CadEntityTypeName:
        '''VIEWPORT entity'''
        ...
    
    @classmethod
    @property
    def WIPEOUT(cls) -> CadEntityTypeName:
        '''WIPEOUT entity'''
        ...
    
    @classmethod
    @property
    def LINE(cls) -> CadEntityTypeName:
        '''The line entity'''
        ...
    
    @classmethod
    @property
    def XLINE(cls) -> CadEntityTypeName:
        '''The Xline entity'''
        ...
    
    @classmethod
    @property
    def CIRCLE(cls) -> CadEntityTypeName:
        '''The circle entity'''
        ...
    
    @classmethod
    @property
    def TRACE(cls) -> CadEntityTypeName:
        '''The trace entity'''
        ...
    
    @classmethod
    @property
    def TOLERANCE(cls) -> CadEntityTypeName:
        '''The tolerance entity'''
        ...
    
    @classmethod
    @property
    def PLANESURFACE(cls) -> CadEntityTypeName:
        '''Plane surface'''
        ...
    
    @classmethod
    @property
    def REVOLVEDSURFACE(cls) -> CadEntityTypeName:
        '''Revolved surface'''
        ...
    
    @classmethod
    @property
    def EXTRUDEDSURFACE(cls) -> CadEntityTypeName:
        '''Extruded surface'''
        ...
    
    @classmethod
    @property
    def SWEPTSURFACE(cls) -> CadEntityTypeName:
        '''Swept surface'''
        ...
    
    @classmethod
    @property
    def LOFTEDSURFACE(cls) -> CadEntityTypeName:
        '''The lofted surface'''
        ...
    
    @classmethod
    @property
    def ACIDBLOCKREFERENCE(cls) -> CadEntityTypeName:
        '''ACIDBLOCKREFERENCE'''
        ...
    
    @classmethod
    @property
    def ARC_DIMENSION(cls) -> CadEntityTypeName:
        '''ARC_DIMENSION entity'''
        ...
    
    @classmethod
    @property
    def EMBEDDEDIMAGE(cls) -> CadEntityTypeName:
        '''EMBEDDED IMAGE entity'''
        ...
    
    ...

class CadFileFormat:
    '''CAD file formats'''
    
    @classmethod
    @property
    def ASCII(cls) -> CadFileFormat:
        '''ASCII CAD file format.'''
        ...
    
    @classmethod
    @property
    def BINARY(cls) -> CadFileFormat:
        '''Binary CAD file format'''
        ...
    
    ...

class CadFillSetting:
    '''The Cad fill setting.'''
    
    @classmethod
    @property
    def FILL_OFF(cls) -> CadFillSetting:
        '''The fill off.'''
        ...
    
    @classmethod
    @property
    def USE_BACKGROUND_COLOR(cls) -> CadFillSetting:
        '''The use background color.'''
        ...
    
    @classmethod
    @property
    def USE_WINDOW_COLOR(cls) -> CadFillSetting:
        '''The use window color.'''
        ...
    
    @classmethod
    @property
    def USE_TEXT_FRAME(cls) -> CadFillSetting:
        '''The use text frame (R2018+)'''
        ...
    
    ...

class CadFontStyleTableFlag:
    '''Font style table flags.'''
    
    @classmethod
    @property
    def NONE(cls) -> CadFontStyleTableFlag:
        '''Empty flag.'''
        ...
    
    @classmethod
    @property
    def FIXED_PITCH(cls) -> CadFontStyleTableFlag:
        '''Fixed pitch (monospace font).'''
        ...
    
    @classmethod
    @property
    def VARIABLE_PITCH(cls) -> CadFontStyleTableFlag:
        '''Variable pitch.'''
        ...
    
    @classmethod
    @property
    def ROMAN(cls) -> CadFontStyleTableFlag:
        '''Roman family (serif).'''
        ...
    
    @classmethod
    @property
    def SWISS(cls) -> CadFontStyleTableFlag:
        '''Swiss family (sans serif).'''
        ...
    
    @classmethod
    @property
    def ITALIC(cls) -> CadFontStyleTableFlag:
        '''Italic style.'''
        ...
    
    @classmethod
    @property
    def BOLD(cls) -> CadFontStyleTableFlag:
        '''Bold style.'''
        ...
    
    @classmethod
    @property
    def BOLD_ITALIC(cls) -> CadFontStyleTableFlag:
        '''Bold italic style.'''
        ...
    
    ...

class CadGroupCodeTypes:
    '''Cad group code value types'''
    
    @classmethod
    @property
    def UNKNOWN(cls) -> CadGroupCodeTypes:
        '''Unknown group'''
        ...
    
    @classmethod
    @property
    def STRING_EX(cls) -> CadGroupCodeTypes:
        '''String (with the introduction of extended symbol names in AutoCAD 2000, the 255-character
        limit has been increased to 2049 single-byte characters not including the newline at the end of the line)'''
        ...
    
    @classmethod
    @property
    def STRING255(cls) -> CadGroupCodeTypes:
        '''String (255-character maximum; less for Unicode strings)'''
        ...
    
    @classmethod
    @property
    def STRING_HEX_HANDLE(cls) -> CadGroupCodeTypes:
        '''String representing hexadecimal (hex) handle value'''
        ...
    
    @classmethod
    @property
    def ARBITRARY_TEXT(cls) -> CadGroupCodeTypes:
        '''Arbitrary text string'''
        ...
    
    @classmethod
    @property
    def STRING_HEX_BINARY_CHUNK(cls) -> CadGroupCodeTypes:
        '''String representing hex value of binary chunk'''
        ...
    
    @classmethod
    @property
    def STRING(cls) -> CadGroupCodeTypes:
        '''String value'''
        ...
    
    @classmethod
    @property
    def COMMENT(cls) -> CadGroupCodeTypes:
        '''Comment (string)'''
        ...
    
    @classmethod
    @property
    def STRING_HEX_IDS(cls) -> CadGroupCodeTypes:
        '''String representing hex object IDs'''
        ...
    
    @classmethod
    @property
    def DOUBLE_PRECISION_3D_POINT(cls) -> CadGroupCodeTypes:
        '''Double precision 3D point value'''
        ...
    
    @classmethod
    @property
    def DOUBLE_PRECISION_FLOAT(cls) -> CadGroupCodeTypes:
        '''Double precision floating-point value'''
        ...
    
    @classmethod
    @property
    def DOUBLE_PRECISION_SCALAR_FLOAT(cls) -> CadGroupCodeTypes:
        '''Double precision scalar floating-point value'''
        ...
    
    @classmethod
    @property
    def INT16(cls) -> CadGroupCodeTypes:
        '''16-bit integer value'''
        ...
    
    @classmethod
    @property
    def INT32(cls) -> CadGroupCodeTypes:
        '''32-bit integer value'''
        ...
    
    @classmethod
    @property
    def INT64(cls) -> CadGroupCodeTypes:
        '''64-bit integer value'''
        ...
    
    @classmethod
    @property
    def LONG(cls) -> CadGroupCodeTypes:
        '''Long value (32 bit)'''
        ...
    
    @classmethod
    @property
    def BOOLEAN_FLAG(cls) -> CadGroupCodeTypes:
        '''Boolean flag value'''
        ...
    
    ...

class CadHatchBoundaryType:
    '''Polyline type hatch'''
    
    @classmethod
    @property
    def LINE(cls) -> CadHatchBoundaryType:
        '''The line boundary type'''
        ...
    
    @classmethod
    @property
    def CIRCLE(cls) -> CadHatchBoundaryType:
        '''The circle boundary type'''
        ...
    
    @classmethod
    @property
    def ELLIPSE(cls) -> CadHatchBoundaryType:
        '''The ellipse boundary type'''
        ...
    
    @classmethod
    @property
    def SPLINE(cls) -> CadHatchBoundaryType:
        '''The spline boundary type'''
        ...
    
    ...

class CadHeaderAttribute:
    '''Contains Header Variable names'''
    
    @classmethod
    @property
    def NONE(cls) -> CadHeaderAttribute:
        '''Default attrbute'''
        ...
    
    @classmethod
    @property
    def ACADVER(cls) -> CadHeaderAttribute:
        '''The acad version.'''
        ...
    
    @classmethod
    @property
    def ACADMAINTVER(cls) -> CadHeaderAttribute:
        '''The acadmaintver.'''
        ...
    
    @classmethod
    @property
    def AUTHOR(cls) -> CadHeaderAttribute:
        '''The author header'''
        ...
    
    @classmethod
    @property
    def KEYWORDS(cls) -> CadHeaderAttribute:
        '''The keywords header'''
        ...
    
    @classmethod
    @property
    def DWGCODEPAGE(cls) -> CadHeaderAttribute:
        '''The dwgcodepage.'''
        ...
    
    @classmethod
    @property
    def TITLE(cls) -> CadHeaderAttribute:
        '''The title header'''
        ...
    
    @classmethod
    @property
    def SUBJECT(cls) -> CadHeaderAttribute:
        '''The subject header'''
        ...
    
    @classmethod
    @property
    def DRAGMODE(cls) -> CadHeaderAttribute:
        '''The Dragmode.'''
        ...
    
    @classmethod
    @property
    def DRAGVS(cls) -> CadHeaderAttribute:
        '''The Dragvs.'''
        ...
    
    @classmethod
    @property
    def OSMODE(cls) -> CadHeaderAttribute:
        '''The Osmode.'''
        ...
    
    @classmethod
    @property
    def BLIPMODE(cls) -> CadHeaderAttribute:
        '''The Blipmode.'''
        ...
    
    @classmethod
    @property
    def COORDS(cls) -> CadHeaderAttribute:
        '''The Coords.'''
        ...
    
    @classmethod
    @property
    def ATTDIA(cls) -> CadHeaderAttribute:
        '''The Attdia.'''
        ...
    
    @classmethod
    @property
    def ATTREQ(cls) -> CadHeaderAttribute:
        '''The Attreq.'''
        ...
    
    @classmethod
    @property
    def HANDLING(cls) -> CadHeaderAttribute:
        '''The Handling.'''
        ...
    
    @classmethod
    @property
    def LASTSAVEDBY(cls) -> CadHeaderAttribute:
        '''The lastsavedby.'''
        ...
    
    @classmethod
    @property
    def CUSTOMPROPERTYTAG(cls) -> CadHeaderAttribute:
        '''The custompropertytag'''
        ...
    
    @classmethod
    @property
    def CUSTOMPROPERTY(cls) -> CadHeaderAttribute:
        '''The customproperty'''
        ...
    
    @classmethod
    @property
    def INSBASE(cls) -> CadHeaderAttribute:
        '''The insbase.'''
        ...
    
    @classmethod
    @property
    def REQUIREDVERSIONS(cls) -> CadHeaderAttribute:
        '''The requiredversions'''
        ...
    
    @classmethod
    @property
    def EXTMIN(cls) -> CadHeaderAttribute:
        '''The extmin.'''
        ...
    
    @classmethod
    @property
    def EXTMAX(cls) -> CadHeaderAttribute:
        '''The extmax.'''
        ...
    
    @classmethod
    @property
    def LIMMIN(cls) -> CadHeaderAttribute:
        '''The limmin.'''
        ...
    
    @classmethod
    @property
    def LIMMAX(cls) -> CadHeaderAttribute:
        '''The limmax.'''
        ...
    
    @classmethod
    @property
    def ORTHOMODE(cls) -> CadHeaderAttribute:
        '''The orthomode.'''
        ...
    
    @classmethod
    @property
    def REGENMODE(cls) -> CadHeaderAttribute:
        '''The regenmode.'''
        ...
    
    @classmethod
    @property
    def FILLMODE(cls) -> CadHeaderAttribute:
        '''The fillmode.'''
        ...
    
    @classmethod
    @property
    def QTEXTMODE(cls) -> CadHeaderAttribute:
        '''The qtextmode.'''
        ...
    
    @classmethod
    @property
    def MIRRTEXT(cls) -> CadHeaderAttribute:
        '''The mirrtext.'''
        ...
    
    @classmethod
    @property
    def LTSCALE(cls) -> CadHeaderAttribute:
        '''The ltscale.'''
        ...
    
    @classmethod
    @property
    def ATTMODE(cls) -> CadHeaderAttribute:
        '''The attmode.'''
        ...
    
    @classmethod
    @property
    def TEXTSIZE(cls) -> CadHeaderAttribute:
        '''The textsize.'''
        ...
    
    @classmethod
    @property
    def TRACEWID(cls) -> CadHeaderAttribute:
        '''The tracewid.'''
        ...
    
    @classmethod
    @property
    def TEXTSTYLE(cls) -> CadHeaderAttribute:
        '''The textstyle.'''
        ...
    
    @classmethod
    @property
    def CLAYER(cls) -> CadHeaderAttribute:
        '''The clayer.'''
        ...
    
    @classmethod
    @property
    def CELTYPE(cls) -> CadHeaderAttribute:
        '''The celtype.'''
        ...
    
    @classmethod
    @property
    def CECOLOR(cls) -> CadHeaderAttribute:
        '''The cecolor.'''
        ...
    
    @classmethod
    @property
    def CELTSCALE(cls) -> CadHeaderAttribute:
        '''The celtscale.'''
        ...
    
    @classmethod
    @property
    def COMMENTS(cls) -> CadHeaderAttribute:
        '''The comments'''
        ...
    
    @classmethod
    @property
    def DELOBJ(cls) -> CadHeaderAttribute:
        '''The delobj'''
        ...
    
    @classmethod
    @property
    def DISPSILH(cls) -> CadHeaderAttribute:
        '''The dispsilh.'''
        ...
    
    @classmethod
    @property
    def DIMSCALE(cls) -> CadHeaderAttribute:
        '''The dimscale.'''
        ...
    
    @classmethod
    @property
    def DIMASZ(cls) -> CadHeaderAttribute:
        '''The dimasz.'''
        ...
    
    @classmethod
    @property
    def DIMEXO(cls) -> CadHeaderAttribute:
        '''The dimexo.'''
        ...
    
    @classmethod
    @property
    def DIMDLI(cls) -> CadHeaderAttribute:
        '''The dimdli.'''
        ...
    
    @classmethod
    @property
    def DIMRND(cls) -> CadHeaderAttribute:
        '''The dimrnd.'''
        ...
    
    @classmethod
    @property
    def DIMDLE(cls) -> CadHeaderAttribute:
        '''The dimdle.'''
        ...
    
    @classmethod
    @property
    def DIMEXE(cls) -> CadHeaderAttribute:
        '''The dimexe.'''
        ...
    
    @classmethod
    @property
    def DIMTP(cls) -> CadHeaderAttribute:
        '''The dimtp.'''
        ...
    
    @classmethod
    @property
    def DIMTM(cls) -> CadHeaderAttribute:
        '''The dimtm.'''
        ...
    
    @classmethod
    @property
    def DIMTXT(cls) -> CadHeaderAttribute:
        '''The dimtxt.'''
        ...
    
    @classmethod
    @property
    def DIMCEN(cls) -> CadHeaderAttribute:
        '''The dimcen.'''
        ...
    
    @classmethod
    @property
    def DIMTSZ(cls) -> CadHeaderAttribute:
        '''The dimtsz.'''
        ...
    
    @classmethod
    @property
    def DIMTOL(cls) -> CadHeaderAttribute:
        '''The dimtol.'''
        ...
    
    @classmethod
    @property
    def DIMLIM(cls) -> CadHeaderAttribute:
        '''The dimlim.'''
        ...
    
    @classmethod
    @property
    def DIMTIH(cls) -> CadHeaderAttribute:
        '''The dimtih.'''
        ...
    
    @classmethod
    @property
    def DIMTOH(cls) -> CadHeaderAttribute:
        '''The dimtoh.'''
        ...
    
    @classmethod
    @property
    def DIMSE1(cls) -> CadHeaderAttribute:
        '''The dims e 1.'''
        ...
    
    @classmethod
    @property
    def DIMSE2(cls) -> CadHeaderAttribute:
        '''The dims e 2.'''
        ...
    
    @classmethod
    @property
    def DIMTAD(cls) -> CadHeaderAttribute:
        '''The dimtad.'''
        ...
    
    @classmethod
    @property
    def DIMZIN(cls) -> CadHeaderAttribute:
        '''The dimzin.'''
        ...
    
    @classmethod
    @property
    def DIMBLK(cls) -> CadHeaderAttribute:
        '''The dimblk.'''
        ...
    
    @classmethod
    @property
    def DIMASO(cls) -> CadHeaderAttribute:
        '''The dimaso.'''
        ...
    
    @classmethod
    @property
    def DIMSHO(cls) -> CadHeaderAttribute:
        '''The dimsho.'''
        ...
    
    @classmethod
    @property
    def DIMPOST(cls) -> CadHeaderAttribute:
        '''The dimpost.'''
        ...
    
    @classmethod
    @property
    def DIMAPOST(cls) -> CadHeaderAttribute:
        '''The dimapost.'''
        ...
    
    @classmethod
    @property
    def DIMALT(cls) -> CadHeaderAttribute:
        '''The dimalt.'''
        ...
    
    @classmethod
    @property
    def DIMALTD(cls) -> CadHeaderAttribute:
        '''The dimaltd.'''
        ...
    
    @classmethod
    @property
    def DIMALTF(cls) -> CadHeaderAttribute:
        '''The dimaltf.'''
        ...
    
    @classmethod
    @property
    def DIMLFAC(cls) -> CadHeaderAttribute:
        '''The dimlfac.'''
        ...
    
    @classmethod
    @property
    def DIMTOFL(cls) -> CadHeaderAttribute:
        '''The dimtofl.'''
        ...
    
    @classmethod
    @property
    def DIMTVP(cls) -> CadHeaderAttribute:
        '''The dimtvp.'''
        ...
    
    @classmethod
    @property
    def DIMTIX(cls) -> CadHeaderAttribute:
        '''The dimtix.'''
        ...
    
    @classmethod
    @property
    def DIMSOXD(cls) -> CadHeaderAttribute:
        '''The dimsoxd.'''
        ...
    
    @classmethod
    @property
    def DIMSAH(cls) -> CadHeaderAttribute:
        '''The dimsah.'''
        ...
    
    @classmethod
    @property
    def DIMBLK1(cls) -> CadHeaderAttribute:
        '''The dimbl k 1.'''
        ...
    
    @classmethod
    @property
    def DIMBLK2(cls) -> CadHeaderAttribute:
        '''The dimbl k 2.'''
        ...
    
    @classmethod
    @property
    def DIMSTYLE(cls) -> CadHeaderAttribute:
        '''The dimstyle.'''
        ...
    
    @classmethod
    @property
    def DIMCLRD(cls) -> CadHeaderAttribute:
        '''The dimclrd.'''
        ...
    
    @classmethod
    @property
    def DIMCLRE(cls) -> CadHeaderAttribute:
        '''The dimclre.'''
        ...
    
    @classmethod
    @property
    def DIMCLRT(cls) -> CadHeaderAttribute:
        '''The dimclrt.'''
        ...
    
    @classmethod
    @property
    def DIMTFAC(cls) -> CadHeaderAttribute:
        '''The dimtfac.'''
        ...
    
    @classmethod
    @property
    def DIMGAP(cls) -> CadHeaderAttribute:
        '''The dimgap.'''
        ...
    
    @classmethod
    @property
    def DIMJUST(cls) -> CadHeaderAttribute:
        '''The dimjust.'''
        ...
    
    @classmethod
    @property
    def DIMSD1(cls) -> CadHeaderAttribute:
        '''The dims d 1.'''
        ...
    
    @classmethod
    @property
    def DIMSD2(cls) -> CadHeaderAttribute:
        '''The dims d 2.'''
        ...
    
    @classmethod
    @property
    def DIMTOLJ(cls) -> CadHeaderAttribute:
        '''The dimtolj.'''
        ...
    
    @classmethod
    @property
    def DIMTZIN(cls) -> CadHeaderAttribute:
        '''The dimtzin.'''
        ...
    
    @classmethod
    @property
    def DIMALTZ(cls) -> CadHeaderAttribute:
        '''The dimaltz.'''
        ...
    
    @classmethod
    @property
    def DIMALTTZ(cls) -> CadHeaderAttribute:
        '''The dimalttz.'''
        ...
    
    @classmethod
    @property
    def DIMFIT(cls) -> CadHeaderAttribute:
        '''The dimfit'''
        ...
    
    @classmethod
    @property
    def DIMUPT(cls) -> CadHeaderAttribute:
        '''The dimupt.'''
        ...
    
    @classmethod
    @property
    def DIMDEC(cls) -> CadHeaderAttribute:
        '''The dimdec.'''
        ...
    
    @classmethod
    @property
    def DIMTDEC(cls) -> CadHeaderAttribute:
        '''The dimtdec.'''
        ...
    
    @classmethod
    @property
    def DIMALTU(cls) -> CadHeaderAttribute:
        '''The dimaltu.'''
        ...
    
    @classmethod
    @property
    def DIMALTTD(cls) -> CadHeaderAttribute:
        '''The dimalttd.'''
        ...
    
    @classmethod
    @property
    def DIMTXSTY(cls) -> CadHeaderAttribute:
        '''The dimtxsty.'''
        ...
    
    @classmethod
    @property
    def DIMAUNIT(cls) -> CadHeaderAttribute:
        '''The dimaunit.'''
        ...
    
    @classmethod
    @property
    def DIMADEC(cls) -> CadHeaderAttribute:
        '''The dimadec.'''
        ...
    
    @classmethod
    @property
    def DIMALTRND(cls) -> CadHeaderAttribute:
        '''The dimaltrnd.'''
        ...
    
    @classmethod
    @property
    def DIMAZIN(cls) -> CadHeaderAttribute:
        '''The dimazin.'''
        ...
    
    @classmethod
    @property
    def DIMDSEP(cls) -> CadHeaderAttribute:
        '''The dimdsep.'''
        ...
    
    @classmethod
    @property
    def DIMATFIT(cls) -> CadHeaderAttribute:
        '''The dimatfit.'''
        ...
    
    @classmethod
    @property
    def DIMFRAC(cls) -> CadHeaderAttribute:
        '''The dimfrac.'''
        ...
    
    @classmethod
    @property
    def DIMFAC(cls) -> CadHeaderAttribute:
        '''The dimfac.'''
        ...
    
    @classmethod
    @property
    def DIMLDRBLK(cls) -> CadHeaderAttribute:
        '''The dimldrblk.'''
        ...
    
    @classmethod
    @property
    def DIMLUNIT(cls) -> CadHeaderAttribute:
        '''The dimlunit.'''
        ...
    
    @classmethod
    @property
    def DIMLWD(cls) -> CadHeaderAttribute:
        '''The dimlwd.'''
        ...
    
    @classmethod
    @property
    def DIMLWE(cls) -> CadHeaderAttribute:
        '''The dimlwe.'''
        ...
    
    @classmethod
    @property
    def DIMTMOVE(cls) -> CadHeaderAttribute:
        '''The dimtmove.'''
        ...
    
    @classmethod
    @property
    def DIMFXL(cls) -> CadHeaderAttribute:
        '''The dimfxl.'''
        ...
    
    @classmethod
    @property
    def DIMFXLON(cls) -> CadHeaderAttribute:
        '''The dimfxlon.'''
        ...
    
    @classmethod
    @property
    def DIMJOGANG(cls) -> CadHeaderAttribute:
        '''The dimjogang.'''
        ...
    
    @classmethod
    @property
    def DIMTFILL(cls) -> CadHeaderAttribute:
        '''The dimtfill.'''
        ...
    
    @classmethod
    @property
    def DIMTFILLCLR(cls) -> CadHeaderAttribute:
        '''The dimtfillclr.'''
        ...
    
    @classmethod
    @property
    def DIMARCSYM(cls) -> CadHeaderAttribute:
        '''The dimarcsym.'''
        ...
    
    @classmethod
    @property
    def DIMLTYPE(cls) -> CadHeaderAttribute:
        '''The dimltype.'''
        ...
    
    @classmethod
    @property
    def DIMLTEX1(cls) -> CadHeaderAttribute:
        '''The dimlte x 1.'''
        ...
    
    @classmethod
    @property
    def DIMLTEX2(cls) -> CadHeaderAttribute:
        '''The dimlte x 2.'''
        ...
    
    @classmethod
    @property
    def DIMTXTDIRECTION(cls) -> CadHeaderAttribute:
        '''The dimtxtdirection.'''
        ...
    
    @classmethod
    @property
    def LUNITS(cls) -> CadHeaderAttribute:
        '''The lunits.'''
        ...
    
    @classmethod
    @property
    def LUPREC(cls) -> CadHeaderAttribute:
        '''The luprec.'''
        ...
    
    @classmethod
    @property
    def SKETCHINC(cls) -> CadHeaderAttribute:
        '''The sketchinc.'''
        ...
    
    @classmethod
    @property
    def FILLETRAD(cls) -> CadHeaderAttribute:
        '''The filletrad.'''
        ...
    
    @classmethod
    @property
    def AUNITS(cls) -> CadHeaderAttribute:
        '''The aunits.'''
        ...
    
    @classmethod
    @property
    def AUPREC(cls) -> CadHeaderAttribute:
        '''The auprec.'''
        ...
    
    @classmethod
    @property
    def MENU(cls) -> CadHeaderAttribute:
        '''The menu attribute.'''
        ...
    
    @classmethod
    @property
    def ELEVATION(cls) -> CadHeaderAttribute:
        '''The elevation.'''
        ...
    
    @classmethod
    @property
    def PELEVATION(cls) -> CadHeaderAttribute:
        '''The pelevation.'''
        ...
    
    @classmethod
    @property
    def THICKNESS(cls) -> CadHeaderAttribute:
        '''The thickness.'''
        ...
    
    @classmethod
    @property
    def LIMCHECK(cls) -> CadHeaderAttribute:
        '''The limcheck.'''
        ...
    
    @classmethod
    @property
    def CHAMFERA(cls) -> CadHeaderAttribute:
        '''The chamfera.'''
        ...
    
    @classmethod
    @property
    def CHAMFERB(cls) -> CadHeaderAttribute:
        '''The chamferb.'''
        ...
    
    @classmethod
    @property
    def CHAMFERC(cls) -> CadHeaderAttribute:
        '''The chamferc.'''
        ...
    
    @classmethod
    @property
    def CHAMFERD(cls) -> CadHeaderAttribute:
        '''The chamferd.'''
        ...
    
    @classmethod
    @property
    def SKPOLY(cls) -> CadHeaderAttribute:
        '''The skpoly.'''
        ...
    
    @classmethod
    @property
    def TDCREATE(cls) -> CadHeaderAttribute:
        '''The tdcreate.'''
        ...
    
    @classmethod
    @property
    def TDUCREATE(cls) -> CadHeaderAttribute:
        '''The tducreate.'''
        ...
    
    @classmethod
    @property
    def TDUPDATE(cls) -> CadHeaderAttribute:
        '''The tdupdate.'''
        ...
    
    @classmethod
    @property
    def TDUUPDATE(cls) -> CadHeaderAttribute:
        '''The tduupdate.'''
        ...
    
    @classmethod
    @property
    def TDINDWG(cls) -> CadHeaderAttribute:
        '''The tdindwg.'''
        ...
    
    @classmethod
    @property
    def TDUSRTIMER(cls) -> CadHeaderAttribute:
        '''The tdusrtimer.'''
        ...
    
    @classmethod
    @property
    def USRTIMER(cls) -> CadHeaderAttribute:
        '''The usrtimer.'''
        ...
    
    @classmethod
    @property
    def ANGBASE(cls) -> CadHeaderAttribute:
        '''The angbase.'''
        ...
    
    @classmethod
    @property
    def ANGDIR(cls) -> CadHeaderAttribute:
        '''The angdir.'''
        ...
    
    @classmethod
    @property
    def PDMODE(cls) -> CadHeaderAttribute:
        '''The pdmode.'''
        ...
    
    @classmethod
    @property
    def PDSIZE(cls) -> CadHeaderAttribute:
        '''The pdsize.'''
        ...
    
    @classmethod
    @property
    def PLINEWID(cls) -> CadHeaderAttribute:
        '''The plinewid.'''
        ...
    
    @classmethod
    @property
    def SPLFRAME(cls) -> CadHeaderAttribute:
        '''The splframe.'''
        ...
    
    @classmethod
    @property
    def SPLINETYPE(cls) -> CadHeaderAttribute:
        '''The splinetype.'''
        ...
    
    @classmethod
    @property
    def SPLINESEGS(cls) -> CadHeaderAttribute:
        '''The splinesegs.'''
        ...
    
    @classmethod
    @property
    def HANDSEED(cls) -> CadHeaderAttribute:
        '''The handseed.'''
        ...
    
    @classmethod
    @property
    def SURFTAB1(cls) -> CadHeaderAttribute:
        '''The surfta b 1.'''
        ...
    
    @classmethod
    @property
    def SURFTAB2(cls) -> CadHeaderAttribute:
        '''The surfta b 2.'''
        ...
    
    @classmethod
    @property
    def SURFTYPE(cls) -> CadHeaderAttribute:
        '''The surftype.'''
        ...
    
    @classmethod
    @property
    def SURFU(cls) -> CadHeaderAttribute:
        '''The surfu.'''
        ...
    
    @classmethod
    @property
    def SURFV(cls) -> CadHeaderAttribute:
        '''The surfv.'''
        ...
    
    @classmethod
    @property
    def UCSBASE(cls) -> CadHeaderAttribute:
        '''The ucsbase.'''
        ...
    
    @classmethod
    @property
    def UCSNAME(cls) -> CadHeaderAttribute:
        '''The ucsname.'''
        ...
    
    @classmethod
    @property
    def UCSORG(cls) -> CadHeaderAttribute:
        '''The ucsorg.'''
        ...
    
    @classmethod
    @property
    def UCSXDIR(cls) -> CadHeaderAttribute:
        '''The ucsxdir.'''
        ...
    
    @classmethod
    @property
    def UCSYDIR(cls) -> CadHeaderAttribute:
        '''The ucsydir.'''
        ...
    
    @classmethod
    @property
    def UCSORTHOREF(cls) -> CadHeaderAttribute:
        '''The ucsorthoref.'''
        ...
    
    @classmethod
    @property
    def UCSORTHOVIEW(cls) -> CadHeaderAttribute:
        '''The ucsorthoview.'''
        ...
    
    @classmethod
    @property
    def UCSORGTOP(cls) -> CadHeaderAttribute:
        '''The ucsorgtop.'''
        ...
    
    @classmethod
    @property
    def UCSORGBOTTOM(cls) -> CadHeaderAttribute:
        '''The ucsorgbottom.'''
        ...
    
    @classmethod
    @property
    def UCSORGLEFT(cls) -> CadHeaderAttribute:
        '''The ucsorgleft.'''
        ...
    
    @classmethod
    @property
    def UCSORGRIGHT(cls) -> CadHeaderAttribute:
        '''The ucsorgright.'''
        ...
    
    @classmethod
    @property
    def UCSORGFRONT(cls) -> CadHeaderAttribute:
        '''The ucsorgfront.'''
        ...
    
    @classmethod
    @property
    def UCSORGBACK(cls) -> CadHeaderAttribute:
        '''The ucsorgback.'''
        ...
    
    @classmethod
    @property
    def PUCSBASE(cls) -> CadHeaderAttribute:
        '''The pucsbase.'''
        ...
    
    @classmethod
    @property
    def PUCSNAME(cls) -> CadHeaderAttribute:
        '''The pucsname.'''
        ...
    
    @classmethod
    @property
    def PUCSORG(cls) -> CadHeaderAttribute:
        '''The pucsorg.'''
        ...
    
    @classmethod
    @property
    def PUCSXDIR(cls) -> CadHeaderAttribute:
        '''The pucsxdir.'''
        ...
    
    @classmethod
    @property
    def PUCSYDIR(cls) -> CadHeaderAttribute:
        '''The pucsydir.'''
        ...
    
    @classmethod
    @property
    def PUCSORTHOREF(cls) -> CadHeaderAttribute:
        '''The pucsorthoref.'''
        ...
    
    @classmethod
    @property
    def PUCSORTHOVIEW(cls) -> CadHeaderAttribute:
        '''The pucsorthoview.'''
        ...
    
    @classmethod
    @property
    def PUCSORGTOP(cls) -> CadHeaderAttribute:
        '''The pucsorgtop.'''
        ...
    
    @classmethod
    @property
    def PUCSORGBOTTOM(cls) -> CadHeaderAttribute:
        '''The pucsorgbottom.'''
        ...
    
    @classmethod
    @property
    def PUCSORGLEFT(cls) -> CadHeaderAttribute:
        '''The pucsorgleft.'''
        ...
    
    @classmethod
    @property
    def PUCSORGRIGHT(cls) -> CadHeaderAttribute:
        '''The pucsorgright.'''
        ...
    
    @classmethod
    @property
    def PUCSORGFRONT(cls) -> CadHeaderAttribute:
        '''The pucsorgfront.'''
        ...
    
    @classmethod
    @property
    def PUCSORGBACK(cls) -> CadHeaderAttribute:
        '''The pucsorgback.'''
        ...
    
    @classmethod
    @property
    def USERI1(cls) -> CadHeaderAttribute:
        '''The user i 1.'''
        ...
    
    @classmethod
    @property
    def USERI2(cls) -> CadHeaderAttribute:
        '''The user i 2.'''
        ...
    
    @classmethod
    @property
    def USERI3(cls) -> CadHeaderAttribute:
        '''The user i 3.'''
        ...
    
    @classmethod
    @property
    def USERI4(cls) -> CadHeaderAttribute:
        '''The user i 4.'''
        ...
    
    @classmethod
    @property
    def USERI5(cls) -> CadHeaderAttribute:
        '''The user i 5.'''
        ...
    
    @classmethod
    @property
    def USERR1(cls) -> CadHeaderAttribute:
        '''The user r 1.'''
        ...
    
    @classmethod
    @property
    def USERR2(cls) -> CadHeaderAttribute:
        '''The user r 2.'''
        ...
    
    @classmethod
    @property
    def USERR3(cls) -> CadHeaderAttribute:
        '''The user r 3.'''
        ...
    
    @classmethod
    @property
    def USERR4(cls) -> CadHeaderAttribute:
        '''The user r 4.'''
        ...
    
    @classmethod
    @property
    def USERR5(cls) -> CadHeaderAttribute:
        '''The user r 5.'''
        ...
    
    @classmethod
    @property
    def WORLDVIEW(cls) -> CadHeaderAttribute:
        '''The worldview.'''
        ...
    
    @classmethod
    @property
    def SAVEIMAGES(cls) -> CadHeaderAttribute:
        '''The saveimages'''
        ...
    
    @classmethod
    @property
    def SHADEDGE(cls) -> CadHeaderAttribute:
        '''The shadedge.'''
        ...
    
    @classmethod
    @property
    def SHADEDIF(cls) -> CadHeaderAttribute:
        '''The shadedif.'''
        ...
    
    @classmethod
    @property
    def TILEMODE(cls) -> CadHeaderAttribute:
        '''The tilemode.'''
        ...
    
    @classmethod
    @property
    def MAXACTVP(cls) -> CadHeaderAttribute:
        '''The maxactvp.'''
        ...
    
    @classmethod
    @property
    def PICKSTYLE(cls) -> CadHeaderAttribute:
        '''The pickstyle'''
        ...
    
    @classmethod
    @property
    def PINSBASE(cls) -> CadHeaderAttribute:
        '''The pinsbase.'''
        ...
    
    @classmethod
    @property
    def PLIMCHECK(cls) -> CadHeaderAttribute:
        '''The plimcheck.'''
        ...
    
    @classmethod
    @property
    def PEXTMIN(cls) -> CadHeaderAttribute:
        '''The pextmin.'''
        ...
    
    @classmethod
    @property
    def PEXTMAX(cls) -> CadHeaderAttribute:
        '''The pextmax.'''
        ...
    
    @classmethod
    @property
    def PLIMMIN(cls) -> CadHeaderAttribute:
        '''The plimmin.'''
        ...
    
    @classmethod
    @property
    def PLIMMAX(cls) -> CadHeaderAttribute:
        '''The plimmax.'''
        ...
    
    @classmethod
    @property
    def UNITMODE(cls) -> CadHeaderAttribute:
        '''The unitmode.'''
        ...
    
    @classmethod
    @property
    def VISRETAIN(cls) -> CadHeaderAttribute:
        '''The visretain.'''
        ...
    
    @classmethod
    @property
    def PLINEGEN(cls) -> CadHeaderAttribute:
        '''The plinegen.'''
        ...
    
    @classmethod
    @property
    def PSLTSCALE(cls) -> CadHeaderAttribute:
        '''The psltscale.'''
        ...
    
    @classmethod
    @property
    def TREEDEPTH(cls) -> CadHeaderAttribute:
        '''The treedepth.'''
        ...
    
    @classmethod
    @property
    def CMLSTYLE(cls) -> CadHeaderAttribute:
        '''The cmlstyle.'''
        ...
    
    @classmethod
    @property
    def CMLJUST(cls) -> CadHeaderAttribute:
        '''The cmljust.'''
        ...
    
    @classmethod
    @property
    def CMLSCALE(cls) -> CadHeaderAttribute:
        '''The cmlscale.'''
        ...
    
    @classmethod
    @property
    def PROXYGRAPHICS(cls) -> CadHeaderAttribute:
        '''The proxygraphics.'''
        ...
    
    @classmethod
    @property
    def MEASUREMENT(cls) -> CadHeaderAttribute:
        '''The measurement.'''
        ...
    
    @classmethod
    @property
    def CELWEIGHT(cls) -> CadHeaderAttribute:
        '''The celweight.'''
        ...
    
    @classmethod
    @property
    def CEPSNID(cls) -> CadHeaderAttribute:
        '''The cepsnid.'''
        ...
    
    @classmethod
    @property
    def ENDCAPS(cls) -> CadHeaderAttribute:
        '''The endcaps.'''
        ...
    
    @classmethod
    @property
    def JOINSTYLE(cls) -> CadHeaderAttribute:
        '''The joinstyle.'''
        ...
    
    @classmethod
    @property
    def LWDISPLAY(cls) -> CadHeaderAttribute:
        '''The lwdisplay.'''
        ...
    
    @classmethod
    @property
    def INSUNITS(cls) -> CadHeaderAttribute:
        '''The insunits.'''
        ...
    
    @classmethod
    @property
    def HYPERLINKBASE(cls) -> CadHeaderAttribute:
        '''The hyperlinkbase.'''
        ...
    
    @classmethod
    @property
    def STYLESHEET(cls) -> CadHeaderAttribute:
        '''The stylesheet.'''
        ...
    
    @classmethod
    @property
    def XEDIT(cls) -> CadHeaderAttribute:
        '''The xedit.'''
        ...
    
    @classmethod
    @property
    def CEPSNTYPE(cls) -> CadHeaderAttribute:
        '''The cepsntype.'''
        ...
    
    @classmethod
    @property
    def PSTYLEMODE(cls) -> CadHeaderAttribute:
        '''The pstylemode.'''
        ...
    
    @classmethod
    @property
    def FINGERPRINTGUID(cls) -> CadHeaderAttribute:
        '''The fingerprintguid.'''
        ...
    
    @classmethod
    @property
    def VERSIONGUID(cls) -> CadHeaderAttribute:
        '''The versionguid.'''
        ...
    
    @classmethod
    @property
    def EXTNAMES(cls) -> CadHeaderAttribute:
        '''The extnames.'''
        ...
    
    @classmethod
    @property
    def PSVPSCALE(cls) -> CadHeaderAttribute:
        '''The psvpscale.'''
        ...
    
    @classmethod
    @property
    def OLESTARTUP(cls) -> CadHeaderAttribute:
        '''The olestartup.'''
        ...
    
    @classmethod
    @property
    def SORTENTS(cls) -> CadHeaderAttribute:
        '''The sortents.'''
        ...
    
    @classmethod
    @property
    def INDEXCTL(cls) -> CadHeaderAttribute:
        '''The indexctl.'''
        ...
    
    @classmethod
    @property
    def HIDETEXT(cls) -> CadHeaderAttribute:
        '''The hidetext.'''
        ...
    
    @classmethod
    @property
    def XCLIPFRAME(cls) -> CadHeaderAttribute:
        '''The xclipframe.'''
        ...
    
    @classmethod
    @property
    def HALOGAP(cls) -> CadHeaderAttribute:
        '''The halogap.'''
        ...
    
    @classmethod
    @property
    def OBSCOLOR(cls) -> CadHeaderAttribute:
        '''The obscolor.'''
        ...
    
    @classmethod
    @property
    def OBSLTYPE(cls) -> CadHeaderAttribute:
        '''The obsltype.'''
        ...
    
    @classmethod
    @property
    def INTERSECTIONDISPLAY(cls) -> CadHeaderAttribute:
        '''The intersectiondisplay.'''
        ...
    
    @classmethod
    @property
    def INTERSECTIONCOLOR(cls) -> CadHeaderAttribute:
        '''The intersectioncolor.'''
        ...
    
    @classmethod
    @property
    def DIMASSOC(cls) -> CadHeaderAttribute:
        '''The dimassoc.'''
        ...
    
    @classmethod
    @property
    def PROJECTNAME(cls) -> CadHeaderAttribute:
        '''The projectname.'''
        ...
    
    @classmethod
    @property
    def CAMERADISPLAY(cls) -> CadHeaderAttribute:
        '''The cameradisplay.'''
        ...
    
    @classmethod
    @property
    def LENSLENGTH(cls) -> CadHeaderAttribute:
        '''The lenslength.'''
        ...
    
    @classmethod
    @property
    def CAMERAHEIGHT(cls) -> CadHeaderAttribute:
        '''The cameraheight.'''
        ...
    
    @classmethod
    @property
    def STEPSPERSEC(cls) -> CadHeaderAttribute:
        '''The stepspersec.'''
        ...
    
    @classmethod
    @property
    def STEPSIZE(cls) -> CadHeaderAttribute:
        '''The stepsize.'''
        ...
    
    @classmethod
    @property
    def _3DDWFPREC(cls) -> CadHeaderAttribute:
        '''The _3 ddwfprec.'''
        ...
    
    @classmethod
    @property
    def PSOLWIDTH(cls) -> CadHeaderAttribute:
        '''The psolwidth.'''
        ...
    
    @classmethod
    @property
    def PSOLHEIGHT(cls) -> CadHeaderAttribute:
        '''The psolheight.'''
        ...
    
    @classmethod
    @property
    def LOFTANG1(cls) -> CadHeaderAttribute:
        '''The loftan g 1.'''
        ...
    
    @classmethod
    @property
    def LOFTANG2(cls) -> CadHeaderAttribute:
        '''The loftan g 2.'''
        ...
    
    @classmethod
    @property
    def LOFTMAG1(cls) -> CadHeaderAttribute:
        '''The loftma g 1.'''
        ...
    
    @classmethod
    @property
    def LOFTMAG2(cls) -> CadHeaderAttribute:
        '''The loftma g 2.'''
        ...
    
    @classmethod
    @property
    def LOFTPARAM(cls) -> CadHeaderAttribute:
        '''The loftparam.'''
        ...
    
    @classmethod
    @property
    def LOFTNORMALS(cls) -> CadHeaderAttribute:
        '''The loftnormals.'''
        ...
    
    @classmethod
    @property
    def LATITUDE(cls) -> CadHeaderAttribute:
        '''The latitude.'''
        ...
    
    @classmethod
    @property
    def LONGITUDE(cls) -> CadHeaderAttribute:
        '''The longitude.'''
        ...
    
    @classmethod
    @property
    def NORTHDIRECTION(cls) -> CadHeaderAttribute:
        '''The northdirection.'''
        ...
    
    @classmethod
    @property
    def TIMEZONE(cls) -> CadHeaderAttribute:
        '''The timezone.'''
        ...
    
    @classmethod
    @property
    def LIGHTGLYPHDISPLAY(cls) -> CadHeaderAttribute:
        '''The lightglyphdisplay.'''
        ...
    
    @classmethod
    @property
    def TILEMODELIGHTSYNCH(cls) -> CadHeaderAttribute:
        '''The tilemodelightsynch.'''
        ...
    
    @classmethod
    @property
    def CMATERIAL(cls) -> CadHeaderAttribute:
        '''The cmaterial.'''
        ...
    
    @classmethod
    @property
    def SOLIDHIST(cls) -> CadHeaderAttribute:
        '''The solidhist.'''
        ...
    
    @classmethod
    @property
    def SHOWHIST(cls) -> CadHeaderAttribute:
        '''The showhist.'''
        ...
    
    @classmethod
    @property
    def DWFFRAME(cls) -> CadHeaderAttribute:
        '''The dwfframe.'''
        ...
    
    @classmethod
    @property
    def DGNFRAME(cls) -> CadHeaderAttribute:
        '''The dgnframe.'''
        ...
    
    @classmethod
    @property
    def REALWORLDSCALE(cls) -> CadHeaderAttribute:
        '''The realworldscale.'''
        ...
    
    @classmethod
    @property
    def INTERFERECOLOR(cls) -> CadHeaderAttribute:
        '''The interferecolor.'''
        ...
    
    @classmethod
    @property
    def INTERFEREOBJVS(cls) -> CadHeaderAttribute:
        '''The interfereobjvs.'''
        ...
    
    @classmethod
    @property
    def INTERFEREVPVS(cls) -> CadHeaderAttribute:
        '''The interferevpvs.'''
        ...
    
    @classmethod
    @property
    def CSHADOW(cls) -> CadHeaderAttribute:
        '''The cshadow.'''
        ...
    
    @classmethod
    @property
    def SHADOWPLANELOCATION(cls) -> CadHeaderAttribute:
        '''The shadowplanelocation.'''
        ...
    
    @classmethod
    @property
    def WFPREC3DD(cls) -> CadHeaderAttribute:
        '''The wfpre c 3 dd.'''
        ...
    
    @classmethod
    @property
    def FPREC3DD(cls) -> CadHeaderAttribute:
        '''The fpre c 3 dd.'''
        ...
    
    @classmethod
    @property
    def DIMUNIT(cls) -> CadHeaderAttribute:
        '''Dim unit value.'''
        ...
    
    @classmethod
    @property
    def VIEWCTR(cls) -> CadHeaderAttribute:
        '''The VIEWCTR'''
        ...
    
    @classmethod
    @property
    def VIEWSIZE(cls) -> CadHeaderAttribute:
        '''The VIEWSIZE'''
        ...
    
    @classmethod
    @property
    def REVISIONNUMBER(cls) -> CadHeaderAttribute:
        '''The revisionnumber'''
        ...
    
    @classmethod
    @property
    def ISOLINES(cls) -> CadHeaderAttribute:
        '''The ISOLINES'''
        ...
    
    @classmethod
    @property
    def TEXTQLTY(cls) -> CadHeaderAttribute:
        '''The TEXTQLTY'''
        ...
    
    @classmethod
    @property
    def FACETRES(cls) -> CadHeaderAttribute:
        '''The FACETRES'''
        ...
    
    @classmethod
    @property
    def PELLIPSE(cls) -> CadHeaderAttribute:
        '''The PELLIPSE'''
        ...
    
    @classmethod
    @property
    def BLOCK_CONTROL_OBJECT(cls) -> CadHeaderAttribute:
        '''The BLOCK_CONTROL_OBJECT'''
        ...
    
    @classmethod
    @property
    def LAYER_CONTROL_OBJECT(cls) -> CadHeaderAttribute:
        '''The LAYER_CONTROL_OBJECT'''
        ...
    
    @classmethod
    @property
    def STYLE_CONTROL_OBJECT(cls) -> CadHeaderAttribute:
        '''The STYLE_CONTROL_OBJECT'''
        ...
    
    @classmethod
    @property
    def LINETYPE_CONTROL_OBJECT(cls) -> CadHeaderAttribute:
        '''The LINETYPE_CONTROL_OBJECT'''
        ...
    
    @classmethod
    @property
    def VIEW_CONTROL_OBJECT(cls) -> CadHeaderAttribute:
        '''The VIEW_CONTROL_OBJECT'''
        ...
    
    @classmethod
    @property
    def UCS_CONTROL_OBJECT(cls) -> CadHeaderAttribute:
        '''The UCS_CONTROL_OBJECT'''
        ...
    
    @classmethod
    @property
    def VPORT_CONTROL_OBJECT(cls) -> CadHeaderAttribute:
        '''The VPORT_CONTROL_OBJECT'''
        ...
    
    @classmethod
    @property
    def APPID_CONTROL_OBJECT(cls) -> CadHeaderAttribute:
        '''The APPID_CONTROL_OBJECT'''
        ...
    
    @classmethod
    @property
    def SNAPMODE(cls) -> CadHeaderAttribute:
        '''Snapmode'''
        ...
    
    @classmethod
    @property
    def SNAPUNIT(cls) -> CadHeaderAttribute:
        '''Snapunit'''
        ...
    
    @classmethod
    @property
    def SNAPBASE(cls) -> CadHeaderAttribute:
        '''Snapbase'''
        ...
    
    @classmethod
    @property
    def SNAPANG(cls) -> CadHeaderAttribute:
        '''Snapangle'''
        ...
    
    @classmethod
    @property
    def SNAPSTYL(cls) -> CadHeaderAttribute:
        '''Snapstyle'''
        ...
    
    @classmethod
    @property
    def SNAPISOPAIR(cls) -> CadHeaderAttribute:
        '''Snap iso pair'''
        ...
    
    @classmethod
    @property
    def GRIDMODE(cls) -> CadHeaderAttribute:
        '''Gridmode'''
        ...
    
    @classmethod
    @property
    def GRIDUNIT(cls) -> CadHeaderAttribute:
        '''grid unit'''
        ...
    
    @classmethod
    @property
    def DIMSTYLE_CONTROL_OBJECT(cls) -> CadHeaderAttribute:
        '''The DIMSTYLE_CONTROL_OBJECT'''
        ...
    
    @classmethod
    @property
    def ACAD_GROUP(cls) -> CadHeaderAttribute:
        '''The DIMSTYLE_CONTROL_OBJECT'''
        ...
    
    @classmethod
    @property
    def ACAD_MLINESTYLE(cls) -> CadHeaderAttribute:
        '''The DIMSTYLE_CONTROL_OBJECT'''
        ...
    
    @classmethod
    @property
    def NAMED_OBJECTS(cls) -> CadHeaderAttribute:
        '''The DIMSTYLE_CONTROL_OBJECT'''
        ...
    
    @classmethod
    @property
    def LTYPE_BLOCK_RECORD_PAPER_SPACE(cls) -> CadHeaderAttribute:
        '''The LTYPE_BLOCK_RECORD_PAPER_SPACE'''
        ...
    
    @classmethod
    @property
    def LTYPE_BLOCK_RECORD_MODEL_SPACE(cls) -> CadHeaderAttribute:
        '''The DIMSTYLE_CONTROL_OBJECT'''
        ...
    
    @classmethod
    @property
    def LTYPE_BYLAYER(cls) -> CadHeaderAttribute:
        '''The DIMSTYLE_CONTROL_OBJECT'''
        ...
    
    @classmethod
    @property
    def LTYPE_BYBLOCK(cls) -> CadHeaderAttribute:
        '''The DIMSTYLE_CONTROL_OBJECT'''
        ...
    
    @classmethod
    @property
    def LTYPE_CONTINUOUS(cls) -> CadHeaderAttribute:
        '''The DIMSTYLE_CONTROL_OBJECT'''
        ...
    
    @classmethod
    @property
    def MENUNAME(cls) -> CadHeaderAttribute:
        '''The MENUNAME'''
        ...
    
    @classmethod
    @property
    def DICTIONARY_LAYOUTS(cls) -> CadHeaderAttribute:
        '''The DICTIONARY_LAYOUTS'''
        ...
    
    @classmethod
    @property
    def DICTIONARY_PLOTSETTINGS(cls) -> CadHeaderAttribute:
        '''The DICTIONARY_PLOTSETTINGS'''
        ...
    
    @classmethod
    @property
    def DICTIONARY_PLOTSTYLES(cls) -> CadHeaderAttribute:
        '''The DICTIONARY_PLOTSTYLES'''
        ...
    
    @classmethod
    @property
    def DICTIONARY_MATERIALS(cls) -> CadHeaderAttribute:
        '''The DICTIONARY_MATERIALS'''
        ...
    
    @classmethod
    @property
    def DICTIONARY_COLORS(cls) -> CadHeaderAttribute:
        '''The DICTIONARY_COLORS'''
        ...
    
    @classmethod
    @property
    def DICTIONARY_VISUALSTYLE(cls) -> CadHeaderAttribute:
        '''The DICTIONARY_VISUALSTYLE'''
        ...
    
    @classmethod
    @property
    def CURRENT_VIEWPORT(cls) -> CadHeaderAttribute:
        '''The CURRENT_VIEWPORT'''
        ...
    
    @classmethod
    @property
    def VIEWPORT_ENTITY_HEADER_CONTROL_OBJECT(cls) -> CadHeaderAttribute:
        '''The VIEWPORT_ENTITY_HEADER_CONTROL_OBJECT'''
        ...
    
    @classmethod
    @property
    def DIMALTMZF(cls) -> CadHeaderAttribute:
        '''The DIMALTMZF'''
        ...
    
    @classmethod
    @property
    def DIMALTMZS(cls) -> CadHeaderAttribute:
        '''The DIMALTMZS'''
        ...
    
    @classmethod
    @property
    def DIMMZF(cls) -> CadHeaderAttribute:
        '''The DIMMZF'''
        ...
    
    @classmethod
    @property
    def DIMMZS(cls) -> CadHeaderAttribute:
        '''The DIMMZS'''
        ...
    
    @classmethod
    @property
    def TSTACKALIGN(cls) -> CadHeaderAttribute:
        '''The TSTACKALIGN'''
        ...
    
    @classmethod
    @property
    def TSTACKSIZE(cls) -> CadHeaderAttribute:
        '''The TSTACKSIZE'''
        ...
    
    @classmethod
    @property
    def DICTIONARY_LIGHTLIST(cls) -> CadHeaderAttribute:
        '''The DICTIONARY_LIGHTLIST'''
        ...
    
    ...

class CadHelixLimitation:
    '''The Cad helix limitation.'''
    
    @classmethod
    @property
    def TURN_HEIGHT(cls) -> CadHelixLimitation:
        '''The turn height.'''
        ...
    
    @classmethod
    @property
    def TURN_COUNT(cls) -> CadHelixLimitation:
        '''The turn count.'''
        ...
    
    @classmethod
    @property
    def HEIGHT(cls) -> CadHelixLimitation:
        '''The height.'''
        ...
    
    ...

class CadHorizontalDirection:
    '''The Cad horizontal direcrtion.'''
    
    @classmethod
    @property
    def LEFT(cls) -> CadHorizontalDirection:
        '''The left direction.'''
        ...
    
    @classmethod
    @property
    def RIGHT(cls) -> CadHorizontalDirection:
        '''The right direction.'''
        ...
    
    ...

class CadIntegralParameterType:
    '''The Cad integral parameter type.'''
    
    @classmethod
    @property
    def UNKNOWN(cls) -> CadIntegralParameterType:
        '''The unknown parameter.'''
        ...
    
    @classmethod
    @property
    def BOOLEAN(cls) -> CadIntegralParameterType:
        '''The boolean parameter.'''
        ...
    
    @classmethod
    @property
    def DOUBLE(cls) -> CadIntegralParameterType:
        '''The double parameter.'''
        ...
    
    @classmethod
    @property
    def INTEGER(cls) -> CadIntegralParameterType:
        '''The integer parameter.'''
        ...
    
    @classmethod
    @property
    def SHORT(cls) -> CadIntegralParameterType:
        '''The short parameter.'''
        ...
    
    @classmethod
    @property
    def STRING(cls) -> CadIntegralParameterType:
        '''The string parameter.'''
        ...
    
    @classmethod
    @property
    def LONG(cls) -> CadIntegralParameterType:
        '''The long parameter'''
        ...
    
    @classmethod
    @property
    def BINARY(cls) -> CadIntegralParameterType:
        '''The binary parameter'''
        ...
    
    ...

class CadLayoutControlFlag:
    '''Flag to control.
    :py:class:`aspose.cad.fileformats.cad.cadobjects.CadLayout`'''
    
    @classmethod
    @property
    def PSLT_SCALE(cls) -> CadLayoutControlFlag:
        '''Indicates the PSLTSCALE value for this layout when this layout is current'''
        ...
    
    @classmethod
    @property
    def LIM_CHECK(cls) -> CadLayoutControlFlag:
        '''Indicates the LIMCHECK value for this layout when this layout is current'''
        ...
    
    ...

class CadLayoutUcsOrthographicType:
    '''Orthographic type of UCS.
    :py:class:`aspose.cad.fileformats.cad.cadobjects.CadLayout`'''
    
    @classmethod
    @property
    def IS_NOT_ORTHOGRAPHIC(cls) -> CadLayoutUcsOrthographicType:
        '''Is not orthographic'''
        ...
    
    @classmethod
    @property
    def TOP(cls) -> CadLayoutUcsOrthographicType:
        '''Orthographic is top'''
        ...
    
    @classmethod
    @property
    def BOTTOM(cls) -> CadLayoutUcsOrthographicType:
        '''Orthographic is bottom'''
        ...
    
    @classmethod
    @property
    def FRONT(cls) -> CadLayoutUcsOrthographicType:
        '''Orthographic is front'''
        ...
    
    @classmethod
    @property
    def BACK(cls) -> CadLayoutUcsOrthographicType:
        '''Orthographic is back'''
        ...
    
    @classmethod
    @property
    def LEFT(cls) -> CadLayoutUcsOrthographicType:
        '''Orthographic is left'''
        ...
    
    @classmethod
    @property
    def RIGHT(cls) -> CadLayoutUcsOrthographicType:
        '''Orthographic is right'''
        ...
    
    ...

class CadLineSpacing:
    '''The Cad line spacing.'''
    
    @classmethod
    @property
    def AT_LEAST(cls) -> CadLineSpacing:
        '''The at least.'''
        ...
    
    @classmethod
    @property
    def EXACT(cls) -> CadLineSpacing:
        '''The exact.'''
        ...
    
    ...

class CadLineSpacingType:
    '''Cad Line spacing enum'''
    
    @classmethod
    @property
    def AT_LEAST(cls) -> CadLineSpacingType:
        '''At least (taller characters will override)'''
        ...
    
    @classmethod
    @property
    def EXACT(cls) -> CadLineSpacingType:
        '''The exact (taller characters will not override)'''
        ...
    
    ...

class CadLineStyle:
    '''Line style'''
    
    @classmethod
    @property
    def SOLID(cls) -> CadLineStyle:
        '''Solid line style'''
        ...
    
    @classmethod
    @property
    def DOTTED(cls) -> CadLineStyle:
        '''Dotted line style'''
        ...
    
    @classmethod
    @property
    def MEDIUM_DASHED(cls) -> CadLineStyle:
        '''Medium dashed'''
        ...
    
    @classmethod
    @property
    def LONG_DASHED(cls) -> CadLineStyle:
        '''Long dashed'''
        ...
    
    @classmethod
    @property
    def DOT_DASHED(cls) -> CadLineStyle:
        '''Dot dashed'''
        ...
    
    @classmethod
    @property
    def SHORT_DASHED(cls) -> CadLineStyle:
        '''Short dashed'''
        ...
    
    @classmethod
    @property
    def DASH_DOUBLE_DOT(cls) -> CadLineStyle:
        '''Dash double dot'''
        ...
    
    @classmethod
    @property
    def LONG_DASH_SHORT_DASH(cls) -> CadLineStyle:
        '''Long dash-short dash'''
        ...
    
    ...

class CadLwPolylineFlag:
    '''The Cad LWPOLYLINE flags.'''
    
    @classmethod
    @property
    def NONE(cls) -> CadLwPolylineFlag:
        '''The none flags.'''
        ...
    
    @classmethod
    @property
    def CLOSED(cls) -> CadLwPolylineFlag:
        '''The close polyline.'''
        ...
    
    @classmethod
    @property
    def PLINEGEN(cls) -> CadLwPolylineFlag:
        '''The Plinegen.'''
        ...
    
    ...

class CadMultiLineFlag:
    '''The Cad MULTILINE flags.'''
    
    @classmethod
    @property
    def UNLOCKED(cls) -> CadMultiLineFlag:
        '''The unlocked flag.'''
        ...
    
    @classmethod
    @property
    def CLOSED(cls) -> CadMultiLineFlag:
        '''The closed flag.'''
        ...
    
    @classmethod
    @property
    def SUPPRESS_START_CAPS(cls) -> CadMultiLineFlag:
        '''The suppress start caps flag.'''
        ...
    
    @classmethod
    @property
    def SUPPRESS_END_CAPS(cls) -> CadMultiLineFlag:
        '''The suppress end caps flag.'''
        ...
    
    ...

class CadObjectTypeName:
    '''Contains Object names'''
    
    @classmethod
    @property
    def NONE(cls) -> CadObjectTypeName:
        '''NONE - default type'''
        ...
    
    @classmethod
    @property
    def ACSH_HISTORY_CLASS(cls) -> CadObjectTypeName:
        '''The ACSH_HISTORY_CLASS object'''
        ...
    
    @classmethod
    @property
    def ACSH_PYRAMID_CLASS(cls) -> CadObjectTypeName:
        '''The ACSH_PYRAMID_CLASS object'''
        ...
    
    @classmethod
    @property
    def ACAD_PROXY_OBJECT(cls) -> CadObjectTypeName:
        '''ACAD_PROXY_OBJECT object'''
        ...
    
    @classmethod
    @property
    def ACDBNAVISWORKSMODELDEF(cls) -> CadObjectTypeName:
        '''ACDBNAVISWORKSMODELDEF object'''
        ...
    
    @classmethod
    @property
    def ACMDATAENTRYBLOCK(cls) -> CadObjectTypeName:
        '''The ACMDATAENTRYBLOCK object'''
        ...
    
    @classmethod
    @property
    def ACDB_BLOCKREPRESENTATION_DATA(cls) -> CadObjectTypeName:
        '''The ACDB_BLOCKREPRESENTATION_DATA object'''
        ...
    
    @classmethod
    @property
    def ACDB_ALDIMOBJECTCONTEXTDATA_CLASS(cls) -> CadObjectTypeName:
        '''The ACDB_ALDIMOBJECTCONTEXTDATA_CLASS object'''
        ...
    
    @classmethod
    @property
    def ACDB_MTEXTOBJECTCONTEXTDATA_CLASS(cls) -> CadObjectTypeName:
        '''The ACDB_MTEXTOBJECTCONTEXTDATA_CLASS'''
        ...
    
    @classmethod
    @property
    def ACDB_MLEADEROBJECTCONTEXTDATA_CLASS(cls) -> CadObjectTypeName:
        '''The ACDB_MLEADEROBJECTCONTEXTDATA_CLASS'''
        ...
    
    @classmethod
    @property
    def ACDB_DYNAMICBLOCKPURGEPREVENTER_VERSION(cls) -> CadObjectTypeName:
        '''The ACDB_DYNAMICBLOCKPURGEPREVENTER_VERSION object'''
        ...
    
    @classmethod
    @property
    def ACAD_EVALUATION_GRAPH(cls) -> CadObjectTypeName:
        '''The acad evaluation graph'''
        ...
    
    @classmethod
    @property
    def BLOCKVISIBILITYGRIP(cls) -> CadObjectTypeName:
        '''The BLOCKVISIBILITYGRIP object'''
        ...
    
    @classmethod
    @property
    def BLOCKFLIPGRIP(cls) -> CadObjectTypeName:
        '''The BLOCKFLIPGRIP object'''
        ...
    
    @classmethod
    @property
    def BLOCKLINEARGRIP(cls) -> CadObjectTypeName:
        '''The BLOCKLINEARGRIP object'''
        ...
    
    @classmethod
    @property
    def BLOCKXYGRIP(cls) -> CadObjectTypeName:
        '''The blockxygrip object'''
        ...
    
    @classmethod
    @property
    def BLOCKALIGNMENTGRIP(cls) -> CadObjectTypeName:
        '''The blockalignmentgrip object'''
        ...
    
    @classmethod
    @property
    def BLOCKSTRETCHACTION(cls) -> CadObjectTypeName:
        '''The BLOCKSTRETCHACTION object'''
        ...
    
    @classmethod
    @property
    def BLOCKSCALEACTION(cls) -> CadObjectTypeName:
        '''The BLOCKSCALEACTION object'''
        ...
    
    @classmethod
    @property
    def BLOCKFLIPACTION(cls) -> CadObjectTypeName:
        '''The BLOCKFLIPACTION object'''
        ...
    
    @classmethod
    @property
    def BLOCKMOVEACTION(cls) -> CadObjectTypeName:
        '''The BLOCKMOVEACTION object'''
        ...
    
    @classmethod
    @property
    def BLOCKGRIPLOCATIONCOMPONENT(cls) -> CadObjectTypeName:
        '''The BLOCKGRIPLOCATIONCOMPONENT object.'''
        ...
    
    @classmethod
    @property
    def BLOCKROTATIONGRIP(cls) -> CadObjectTypeName:
        '''The BLOCKROTATIONGRIP object'''
        ...
    
    @classmethod
    @property
    def BLOCKPOINTPARAMETER(cls) -> CadObjectTypeName:
        '''The BLOCKPOINTPARAMETER object.'''
        ...
    
    @classmethod
    @property
    def ACAMGFILTERDAT(cls) -> CadObjectTypeName:
        '''ACAMGFILTERDAT object'''
        ...
    
    @classmethod
    @property
    def ACDBASSOCPERSSUBENTMANAGER(cls) -> CadObjectTypeName:
        '''The ACDBASSOCPERSSUBENTMANAGER object'''
        ...
    
    @classmethod
    @property
    def ACDBPERSSUBENTMANAGER(cls) -> CadObjectTypeName:
        '''The ACDBPERSSUBENTMANAGER object'''
        ...
    
    @classmethod
    @property
    def ACDBDICTIONARYWDFLT(cls) -> CadObjectTypeName:
        '''ACDBDICTIONARYWDFLT object'''
        ...
    
    @classmethod
    @property
    def ACDBASSOCNETWORK(cls) -> CadObjectTypeName:
        '''The acdbassocnetwork'''
        ...
    
    @classmethod
    @property
    def ACDBPLACEHOLDER(cls) -> CadObjectTypeName:
        '''ACDBPLACEHOLDER object'''
        ...
    
    @classmethod
    @property
    def BREAKDATA(cls) -> CadObjectTypeName:
        '''The breakdata object'''
        ...
    
    @classmethod
    @property
    def BLOCKVISIBILITYPARAMETER(cls) -> CadObjectTypeName:
        '''The block visibility parameter object'''
        ...
    
    @classmethod
    @property
    def BLOCKBASEPOINTPARAMETER(cls) -> CadObjectTypeName:
        '''The block basepoint parameter object'''
        ...
    
    @classmethod
    @property
    def BLOCKALIGNMENTPARAMETER(cls) -> CadObjectTypeName:
        '''The block alignment parameter object'''
        ...
    
    @classmethod
    @property
    def BLOCKROTATIONPARAMETER(cls) -> CadObjectTypeName:
        '''The block rotation parameter object'''
        ...
    
    @classmethod
    @property
    def BLOCKROTATEACTION(cls) -> CadObjectTypeName:
        '''The BLOCKROTATEACTION parameter object'''
        ...
    
    @classmethod
    @property
    def BLOCKLINEARPARAMETER(cls) -> CadObjectTypeName:
        '''The block linear parameter object'''
        ...
    
    @classmethod
    @property
    def BLOCKFLIPPARAMETER(cls) -> CadObjectTypeName:
        '''The block flip parameter object'''
        ...
    
    @classmethod
    @property
    def DATATABLE(cls) -> CadObjectTypeName:
        '''DATATABLE object'''
        ...
    
    @classmethod
    @property
    def DBCOLOR(cls) -> CadObjectTypeName:
        '''The DBCOLOR object'''
        ...
    
    @classmethod
    @property
    def DGNDEFINITION(cls) -> CadObjectTypeName:
        '''The DGNDEFINITION object'''
        ...
    
    @classmethod
    @property
    def DWFDEFINITION(cls) -> CadObjectTypeName:
        '''The DWFDEFINITION object'''
        ...
    
    @classmethod
    @property
    def PDFDEFINITION(cls) -> CadObjectTypeName:
        '''The PDFDEFINITION object'''
        ...
    
    @classmethod
    @property
    def DICTIONARY(cls) -> CadObjectTypeName:
        '''DICTIONARY object'''
        ...
    
    @classmethod
    @property
    def ACMDATADICTIONARY(cls) -> CadObjectTypeName:
        '''The ACMDATADICTIONARY object'''
        ...
    
    @classmethod
    @property
    def DICTIONARYVAR(cls) -> CadObjectTypeName:
        '''DICTIONARYVAR object'''
        ...
    
    @classmethod
    @property
    def DIMASSOC(cls) -> CadObjectTypeName:
        '''DIMASSOC object'''
        ...
    
    @classmethod
    @property
    def FIELD(cls) -> CadObjectTypeName:
        '''FIELD object'''
        ...
    
    @classmethod
    @property
    def FIELDLIST(cls) -> CadObjectTypeName:
        '''The fieldlist object'''
        ...
    
    @classmethod
    @property
    def GEODATA(cls) -> CadObjectTypeName:
        '''GEODATA object'''
        ...
    
    @classmethod
    @property
    def GROUP(cls) -> CadObjectTypeName:
        '''GROUP object'''
        ...
    
    @classmethod
    @property
    def IDBUFFER(cls) -> CadObjectTypeName:
        '''IDBUFFER object'''
        ...
    
    @classmethod
    @property
    def IMAGEDEF(cls) -> CadObjectTypeName:
        '''IMAGEDEF object'''
        ...
    
    @classmethod
    @property
    def IMAGEDATA(cls) -> CadObjectTypeName:
        '''IMAGEDEF object'''
        ...
    
    @classmethod
    @property
    def IMAGEDEF_REACTOR(cls) -> CadObjectTypeName:
        '''IMAGEDEF_REACTOR object'''
        ...
    
    @classmethod
    @property
    def LAYER_INDEX(cls) -> CadObjectTypeName:
        '''LAYER_INDEX object'''
        ...
    
    @classmethod
    @property
    def LAYER_FILTER(cls) -> CadObjectTypeName:
        '''LAYER_FILTER object'''
        ...
    
    @classmethod
    @property
    def LAYOUT(cls) -> CadObjectTypeName:
        '''LAYOUT object'''
        ...
    
    @classmethod
    @property
    def LIGHTLIST(cls) -> CadObjectTypeName:
        '''LIGHTLIST object'''
        ...
    
    @classmethod
    @property
    def MATERIAL(cls) -> CadObjectTypeName:
        '''MATERIAL object'''
        ...
    
    @classmethod
    @property
    def MLINESTYLE(cls) -> CadObjectTypeName:
        '''MLINESTYLE object'''
        ...
    
    @classmethod
    @property
    def OBJECT_PTR(cls) -> CadObjectTypeName:
        '''OBJECT_PTR object'''
        ...
    
    @classmethod
    @property
    def PLOTSETTINGS(cls) -> CadObjectTypeName:
        '''PLOTSETTINGS  object'''
        ...
    
    @classmethod
    @property
    def RASTERVARIABLES(cls) -> CadObjectTypeName:
        '''RASTERVARIABLES object'''
        ...
    
    @classmethod
    @property
    def RENDERENVIRONMENT(cls) -> CadObjectTypeName:
        '''RENDERENVIRONMENT object'''
        ...
    
    @classmethod
    @property
    def RENDERGLOBAL(cls) -> CadObjectTypeName:
        '''RENDERGLOBAL object'''
        ...
    
    @classmethod
    @property
    def MENTALRAYRENDERSETTINGS(cls) -> CadObjectTypeName:
        '''MENTALRAYRENDERSETTINGS object'''
        ...
    
    @classmethod
    @property
    def RAPIDRTRENDERENVIRONMENT(cls) -> CadObjectTypeName:
        '''The RAPIDRTRENDERENVIRONMENT object'''
        ...
    
    @classmethod
    @property
    def RAPIDRTRENDERSETTINGS(cls) -> CadObjectTypeName:
        '''The RAPIDRTRENDERSETTINGS object'''
        ...
    
    @classmethod
    @property
    def SECTIONMANAGER(cls) -> CadObjectTypeName:
        '''SECTIONMANAGER object'''
        ...
    
    @classmethod
    @property
    def SECTIONSETTINGS(cls) -> CadObjectTypeName:
        '''The SECTIONSETTINGS object'''
        ...
    
    @classmethod
    @property
    def SECTION(cls) -> CadObjectTypeName:
        '''SECTIONSETTINGS object'''
        ...
    
    @classmethod
    @property
    def SPATIAL_INDEX(cls) -> CadObjectTypeName:
        '''SPATIAL_INDEX object'''
        ...
    
    @classmethod
    @property
    def SPATIAL_FILTER(cls) -> CadObjectTypeName:
        '''SPATIAL_FILTER object'''
        ...
    
    @classmethod
    @property
    def SORTENTSTABLE(cls) -> CadObjectTypeName:
        '''SORTENTSTABLE object'''
        ...
    
    @classmethod
    @property
    def SKYLIGHT_BACKGROUND(cls) -> CadObjectTypeName:
        '''SKYLIGHT_BACKGROUND object'''
        ...
    
    @classmethod
    @property
    def TABLESTYLE(cls) -> CadObjectTypeName:
        '''TABLESTYLE object'''
        ...
    
    @classmethod
    @property
    def UNDERLAYDEFINITION(cls) -> CadObjectTypeName:
        '''UNDERLAYDEFINITION object'''
        ...
    
    @classmethod
    @property
    def VISUALSTYLE(cls) -> CadObjectTypeName:
        '''VISUALSTYLE object'''
        ...
    
    @classmethod
    @property
    def ACDBDETAILVIEWSTYLE(cls) -> CadObjectTypeName:
        '''The detailviewstyle object'''
        ...
    
    @classmethod
    @property
    def VBA_PROJECT(cls) -> CadObjectTypeName:
        '''VBA_PROJECT object'''
        ...
    
    @classmethod
    @property
    def WIPEOUTVARIABLES(cls) -> CadObjectTypeName:
        '''WIPEOUTVARIABLES object'''
        ...
    
    @classmethod
    @property
    def SUNSTUDY(cls) -> CadObjectTypeName:
        '''The sunstudy object'''
        ...
    
    @classmethod
    @property
    def TABLECONTENT(cls) -> CadObjectTypeName:
        '''The tablecontent object'''
        ...
    
    @classmethod
    @property
    def TABLEGEOMETRY(cls) -> CadObjectTypeName:
        '''The tablegeometry object'''
        ...
    
    @classmethod
    @property
    def SUN(cls) -> CadObjectTypeName:
        '''The sun object'''
        ...
    
    @classmethod
    @property
    def XRECORD(cls) -> CadObjectTypeName:
        '''XRECORD object'''
        ...
    
    @classmethod
    @property
    def CELLSTYLEMAP(cls) -> CadObjectTypeName:
        '''CELLSTYLEMAP object'''
        ...
    
    @classmethod
    @property
    def TABLEFORMAT(cls) -> CadObjectTypeName:
        '''TABLEFORMAT object'''
        ...
    
    @classmethod
    @property
    def CONTENTFORMAT(cls) -> CadObjectTypeName:
        '''CONTENTFORMAT object'''
        ...
    
    @classmethod
    @property
    def MARGIN(cls) -> CadObjectTypeName:
        '''MARGIN object'''
        ...
    
    @classmethod
    @property
    def GRIDFORMAT(cls) -> CadObjectTypeName:
        '''GRIDFORMAT object'''
        ...
    
    @classmethod
    @property
    def CELLMARGIN(cls) -> CadObjectTypeName:
        '''CELLMARGIN object'''
        ...
    
    @classmethod
    @property
    def CELLSTYLE(cls) -> CadObjectTypeName:
        '''CELLSTYLE object'''
        ...
    
    @classmethod
    @property
    def MLEADERSTYLE(cls) -> CadObjectTypeName:
        '''MLEADERSTYLE object'''
        ...
    
    @classmethod
    @property
    def SCALE(cls) -> CadObjectTypeName:
        '''The scale object'''
        ...
    
    @classmethod
    @property
    def ACDBSECTIONVIEWSTYLE(cls) -> CadObjectTypeName:
        '''The acdbsectionviewstyle'''
        ...
    
    @classmethod
    @property
    def ACDBASSOCVARIABLE(cls) -> CadObjectTypeName:
        '''The ACDBASSOCVARIABLE'''
        ...
    
    ...

class CadOrdinate:
    '''Cad Ordinate position'''
    
    @classmethod
    @property
    def YORDINATE(cls) -> CadOrdinate:
        '''The y ordinate'''
        ...
    
    @classmethod
    @property
    def XORDINATE(cls) -> CadOrdinate:
        '''The x ordinate'''
        ...
    
    ...

class CadParameterType:
    '''Type of parsing parameters'''
    
    @classmethod
    @property
    def MUST_HAVE(cls) -> CadParameterType:
        '''The must have.'''
        ...
    
    @classmethod
    @property
    def OPTIONAL(cls) -> CadParameterType:
        '''The optional.'''
        ...
    
    ...

class CadPlotLayoutFlag:
    '''Plot layout flag.
    :py:attr:`aspose.cad.fileformats.cad.cadobjects.CadPlotSettings.plot_layout_flag`'''
    
    @classmethod
    @property
    def PLOT_VIEWPORT_BORDERS(cls) -> CadPlotLayoutFlag:
        '''The plot viewport borders'''
        ...
    
    @classmethod
    @property
    def SHOW_PLOT_STYLES(cls) -> CadPlotLayoutFlag:
        '''The show plot styles'''
        ...
    
    @classmethod
    @property
    def PLOT_CENTERED(cls) -> CadPlotLayoutFlag:
        '''The plot centered'''
        ...
    
    @classmethod
    @property
    def PLOT_HIDDEN(cls) -> CadPlotLayoutFlag:
        '''The plot hidden'''
        ...
    
    @classmethod
    @property
    def USE_STANDARD_SCALE(cls) -> CadPlotLayoutFlag:
        '''The use standard scale'''
        ...
    
    @classmethod
    @property
    def PLOT_PLOT_STYLES(cls) -> CadPlotLayoutFlag:
        '''The plot plot styles'''
        ...
    
    @classmethod
    @property
    def SCALE_LINE_WEIGHTS(cls) -> CadPlotLayoutFlag:
        '''The scale line weights'''
        ...
    
    @classmethod
    @property
    def PRINT_LINE_WEIGHTS(cls) -> CadPlotLayoutFlag:
        '''The print line weights'''
        ...
    
    @classmethod
    @property
    def DRAW_VIEWPORTS_FIRST(cls) -> CadPlotLayoutFlag:
        '''The draw viewports first'''
        ...
    
    @classmethod
    @property
    def MODEL_TYPE(cls) -> CadPlotLayoutFlag:
        '''The model type'''
        ...
    
    @classmethod
    @property
    def UPDATE_PAPER(cls) -> CadPlotLayoutFlag:
        '''The update paper'''
        ...
    
    @classmethod
    @property
    def ZOOM_TO_PAPER_ON_UPDATE(cls) -> CadPlotLayoutFlag:
        '''The zoom to paper on update'''
        ...
    
    @classmethod
    @property
    def INITIALIZING(cls) -> CadPlotLayoutFlag:
        '''The initializing'''
        ...
    
    @classmethod
    @property
    def PREV_PLOT_INIT(cls) -> CadPlotLayoutFlag:
        '''The previous plot initialize'''
        ...
    
    ...

class CadPlotPaperUnits:
    '''Plot paper units.
    :py:class:`aspose.cad.fileformats.cad.cadobjects.CadPlotSettings`'''
    
    @classmethod
    @property
    def PLOT_IN_INCHES(cls) -> CadPlotPaperUnits:
        '''The plot in inches'''
        ...
    
    @classmethod
    @property
    def PLOT_IN_MILLIMETERS(cls) -> CadPlotPaperUnits:
        '''The plot in millimeters'''
        ...
    
    @classmethod
    @property
    def PLOT_IN_PIXELS(cls) -> CadPlotPaperUnits:
        '''The plot in pixels'''
        ...
    
    ...

class CadPlotRotation:
    '''Plot rotation.
    :py:class:`aspose.cad.fileformats.cad.cadobjects.CadPlotSettings`'''
    
    @classmethod
    @property
    def NO_ROTATION(cls) -> CadPlotRotation:
        '''The no rotation'''
        ...
    
    @classmethod
    @property
    def COUNTERCLOCKWISE_90_DEGREES(cls) -> CadPlotRotation:
        '''The counterclockwise90 degrees'''
        ...
    
    @classmethod
    @property
    def UPSIDE_DOWN(cls) -> CadPlotRotation:
        '''The upside down'''
        ...
    
    @classmethod
    @property
    def CLOCKWISE_90_DEGREES(cls) -> CadPlotRotation:
        '''The clockwise90 degrees'''
        ...
    
    ...

class CadPlotStandardScaleType:
    '''Standard scale type.
    :py:class:`aspose.cad.fileformats.cad.cadobjects.CadPlotSettings`'''
    
    @classmethod
    @property
    def SCALED_TO_FIT(cls) -> CadPlotStandardScaleType:
        '''The scaled To fit'''
        ...
    
    @classmethod
    @property
    def SCALE_1_TO_128_SEC(cls) -> CadPlotStandardScaleType:
        '''Scale is 1/128"=1''''
        ...
    
    @classmethod
    @property
    def SCALE_1_TO_64_SEC(cls) -> CadPlotStandardScaleType:
        '''Scale is 1/64"=1''''
        ...
    
    @classmethod
    @property
    def SCALE_1_TO_32_SEC(cls) -> CadPlotStandardScaleType:
        '''Scale is 1/32"=1''''
        ...
    
    @classmethod
    @property
    def SCALE_1_TO_16_SEC(cls) -> CadPlotStandardScaleType:
        '''Scale is 1/16"=1''''
        ...
    
    @classmethod
    @property
    def SCALE_3_TO_32_SEC(cls) -> CadPlotStandardScaleType:
        '''Scale is 3/32"=1''''
        ...
    
    @classmethod
    @property
    def SCALE_1_TO_8_SEC(cls) -> CadPlotStandardScaleType:
        '''Scale is 1/8"=1''''
        ...
    
    @classmethod
    @property
    def SCALE_3_TO_16_SEC(cls) -> CadPlotStandardScaleType:
        '''Scale is 3/16"=1''''
        ...
    
    @classmethod
    @property
    def SCALE_1_TO_4_SEC(cls) -> CadPlotStandardScaleType:
        '''Scale is 1/4"=1''''
        ...
    
    @classmethod
    @property
    def SCALE_3_TO_8_SEC(cls) -> CadPlotStandardScaleType:
        '''Scale is 3/8"=1''''
        ...
    
    @classmethod
    @property
    def SCALE_1_TO_2_SEC(cls) -> CadPlotStandardScaleType:
        '''Scale is 1/2"=1''''
        ...
    
    @classmethod
    @property
    def SCALE_3_TO_4_SEC(cls) -> CadPlotStandardScaleType:
        '''Scale is 3/4"=1''''
        ...
    
    @classmethod
    @property
    def SCALE_1_SEC(cls) -> CadPlotStandardScaleType:
        '''Scale is 1"=1''''
        ...
    
    @classmethod
    @property
    def SCALE_3_SEC(cls) -> CadPlotStandardScaleType:
        '''Scale is 3"=1''''
        ...
    
    @classmethod
    @property
    def SCALE_6_SEC(cls) -> CadPlotStandardScaleType:
        '''Scale is 6"=1''''
        ...
    
    @classmethod
    @property
    def SCALE_1_MIN(cls) -> CadPlotStandardScaleType:
        '''Scale is 1'=1''''
        ...
    
    @classmethod
    @property
    def SCALE_1_TO_1(cls) -> CadPlotStandardScaleType:
        '''Scale is 1:1'''
        ...
    
    @classmethod
    @property
    def SCALE_1_TO_2(cls) -> CadPlotStandardScaleType:
        '''Scale is 1:2'''
        ...
    
    @classmethod
    @property
    def SCALE_1_TO_4(cls) -> CadPlotStandardScaleType:
        '''Scale is 1:4'''
        ...
    
    @classmethod
    @property
    def SCALE_1_TO_8(cls) -> CadPlotStandardScaleType:
        '''Scale is 1:8'''
        ...
    
    @classmethod
    @property
    def SCALE_1_TO_10(cls) -> CadPlotStandardScaleType:
        '''Scale is 1:10'''
        ...
    
    @classmethod
    @property
    def SCALE_1_TO_16(cls) -> CadPlotStandardScaleType:
        '''Scale is 1:16'''
        ...
    
    @classmethod
    @property
    def SCALE_1_TO_20(cls) -> CadPlotStandardScaleType:
        '''Scale is 1:20'''
        ...
    
    @classmethod
    @property
    def SCALE_1_TO_30(cls) -> CadPlotStandardScaleType:
        '''Scale is 1:30'''
        ...
    
    @classmethod
    @property
    def SCALE_1_TO_40(cls) -> CadPlotStandardScaleType:
        '''Scale is 1:40'''
        ...
    
    @classmethod
    @property
    def SCALE_1_TO_50(cls) -> CadPlotStandardScaleType:
        '''Scale is 1:50'''
        ...
    
    @classmethod
    @property
    def SCALE_1_TO_100(cls) -> CadPlotStandardScaleType:
        '''Scale is 1:100'''
        ...
    
    @classmethod
    @property
    def SCALE_2_TO_1(cls) -> CadPlotStandardScaleType:
        '''Scale is 2:1'''
        ...
    
    @classmethod
    @property
    def SCALE_4_TO_1(cls) -> CadPlotStandardScaleType:
        '''Scale is 4:1'''
        ...
    
    @classmethod
    @property
    def SCALE_8_TO_1(cls) -> CadPlotStandardScaleType:
        '''Scale is 8:1'''
        ...
    
    @classmethod
    @property
    def SCALE_10_TO_1(cls) -> CadPlotStandardScaleType:
        '''Scale is 10:1'''
        ...
    
    @classmethod
    @property
    def SCALE_100_TO_1(cls) -> CadPlotStandardScaleType:
        '''Scale is 100:1'''
        ...
    
    @classmethod
    @property
    def SCALE_1000_TO_1(cls) -> CadPlotStandardScaleType:
        '''Scale is 1000:1'''
        ...
    
    ...

class CadPlotType:
    '''Plot type (portion of paper space to output to the media).
    :py:class:`aspose.cad.fileformats.cad.cadobjects.CadPlotSettings`'''
    
    @classmethod
    @property
    def LAST_SCREEN_DISPLAY(cls) -> CadPlotType:
        '''Last screen display.'''
        ...
    
    @classmethod
    @property
    def EXTENTS(cls) -> CadPlotType:
        '''Drawing extents.'''
        ...
    
    @classmethod
    @property
    def LIMITS(cls) -> CadPlotType:
        '''Drawing limits.'''
        ...
    
    @classmethod
    @property
    def VIEW6(cls) -> CadPlotType:
        '''View specified by code 6.'''
        ...
    
    @classmethod
    @property
    def WINDOW(cls) -> CadPlotType:
        '''Window specified by codes 48, 49, 140, 141.'''
        ...
    
    @classmethod
    @property
    def LAYOUT_INFORMATION(cls) -> CadPlotType:
        '''Layout information.'''
        ...
    
    ...

class CadPolylineFlag:
    '''The Cad POLYLINE flags.'''
    
    @classmethod
    @property
    def NONE(cls) -> CadPolylineFlag:
        '''The none flags.'''
        ...
    
    @classmethod
    @property
    def CLOSED_POLY(cls) -> CadPolylineFlag:
        '''The close d_ poly.'''
        ...
    
    @classmethod
    @property
    def CURVE_FIT(cls) -> CadPolylineFlag:
        '''The curv e_ fit.'''
        ...
    
    @classmethod
    @property
    def SPLINE_FIT(cls) -> CadPolylineFlag:
        '''The splin e_ fit.'''
        ...
    
    @classmethod
    @property
    def POLY_3D(cls) -> CadPolylineFlag:
        '''The pol y_3 d.'''
        ...
    
    @classmethod
    @property
    def POLYMESH_3D(cls) -> CadPolylineFlag:
        '''The polymes h_3 d.'''
        ...
    
    @classmethod
    @property
    def CLOSED_POLY_MESH(cls) -> CadPolylineFlag:
        '''The close d_ pol y_ mesh.'''
        ...
    
    @classmethod
    @property
    def POLYFACE_MESH(cls) -> CadPolylineFlag:
        '''The polyfac e_ mesh.'''
        ...
    
    @classmethod
    @property
    def GENERATED_PATTERN(cls) -> CadPolylineFlag:
        '''The generate d_ pattern.'''
        ...
    
    ...

class CadSectionType:
    '''Contains Section type'''
    
    @classmethod
    @property
    def NOT_SET(cls) -> CadSectionType:
        '''Section is not set - default'''
        ...
    
    @classmethod
    @property
    def ANOTHER(cls) -> CadSectionType:
        '''Another section'''
        ...
    
    @classmethod
    @property
    def HEADER(cls) -> CadSectionType:
        '''Header string marker'''
        ...
    
    @classmethod
    @property
    def TABLES(cls) -> CadSectionType:
        '''Tables string marker'''
        ...
    
    @classmethod
    @property
    def BLOCKS(cls) -> CadSectionType:
        '''Blocks string marker'''
        ...
    
    @classmethod
    @property
    def ENTITIES(cls) -> CadSectionType:
        '''Entities string marker'''
        ...
    
    @classmethod
    @property
    def CLASSES(cls) -> CadSectionType:
        '''Classes string marker'''
        ...
    
    @classmethod
    @property
    def OBJECTS(cls) -> CadSectionType:
        '''Objects string marker'''
        ...
    
    @classmethod
    @property
    def THUMBNAILIMAGE(cls) -> CadSectionType:
        '''Entities string marker'''
        ...
    
    @classmethod
    @property
    def ACDSDATA(cls) -> CadSectionType:
        '''ACDS string marker'''
        ...
    
    ...

class CadShadePlotMode:
    '''ShadePlot mode.
    :py:class:`aspose.cad.fileformats.cad.cadobjects.CadPlotSettings`'''
    
    @classmethod
    @property
    def AS_DISPLAYED(cls) -> CadShadePlotMode:
        '''As displayed'''
        ...
    
    @classmethod
    @property
    def WIREFRAME(cls) -> CadShadePlotMode:
        '''The wireframe'''
        ...
    
    @classmethod
    @property
    def HIDDEN(cls) -> CadShadePlotMode:
        '''The hidden'''
        ...
    
    @classmethod
    @property
    def RENDERED(cls) -> CadShadePlotMode:
        '''The rendered'''
        ...
    
    ...

class CadShadePlotResolutionLevel:
    '''ShadePlot resolution level.
    :py:class:`aspose.cad.fileformats.cad.cadobjects.CadPlotSettings`'''
    
    @classmethod
    @property
    def DRAFT(cls) -> CadShadePlotResolutionLevel:
        '''Resolution is draft'''
        ...
    
    @classmethod
    @property
    def PREVIEW(cls) -> CadShadePlotResolutionLevel:
        '''Resolution is preview'''
        ...
    
    @classmethod
    @property
    def NORMAL(cls) -> CadShadePlotResolutionLevel:
        '''Resolution is normal'''
        ...
    
    @classmethod
    @property
    def PRESENTATION(cls) -> CadShadePlotResolutionLevel:
        '''Resolution is presentation'''
        ...
    
    @classmethod
    @property
    def MAXIMUM(cls) -> CadShadePlotResolutionLevel:
        '''Resolution is maximum'''
        ...
    
    @classmethod
    @property
    def CUSTOM(cls) -> CadShadePlotResolutionLevel:
        '''Resolution is custom'''
        ...
    
    ...

class CadShadowMode:
    '''Shadow enumeration'''
    
    @classmethod
    @property
    def CAST_AND_RECEIVE_SHADOW(cls) -> CadShadowMode:
        '''The cast and receive shadow.'''
        ...
    
    @classmethod
    @property
    def CAST_SHADOW(cls) -> CadShadowMode:
        '''The cast shadow.'''
        ...
    
    @classmethod
    @property
    def RECEIVE_SHADOW(cls) -> CadShadowMode:
        '''The receive shadow.'''
        ...
    
    @classmethod
    @property
    def IGNORE_SHADOW(cls) -> CadShadowMode:
        '''The ignore shadow.'''
        ...
    
    ...

class CadTableBorderOverrideFlag:
    '''Specifies the flags that indicate which border override values are present for different sections, orientations, and positions of a table entity.
    These flags can be used for overrides of color, line weight, or visibility.'''
    
    @classmethod
    @property
    def NONE(cls) -> CadTableBorderOverrideFlag:
        '''No border overrides are defined.'''
        ...
    
    @classmethod
    @property
    def TITLE_HORIZONTAL_TOP(cls) -> CadTableBorderOverrideFlag:
        '''The title horizontal top border override is present.'''
        ...
    
    @classmethod
    @property
    def TITLE_HORIZONTAL_INSIDE(cls) -> CadTableBorderOverrideFlag:
        '''The title horizontal inside border override is present.'''
        ...
    
    @classmethod
    @property
    def TITLE_HORIZONTAL_BOTTOM(cls) -> CadTableBorderOverrideFlag:
        '''The title horizontal bottom border override is present.'''
        ...
    
    @classmethod
    @property
    def TITLE_VERTICAL_LEFT(cls) -> CadTableBorderOverrideFlag:
        '''The title vertical left border override is present.'''
        ...
    
    @classmethod
    @property
    def TITLE_VERTICAL_INSIDE(cls) -> CadTableBorderOverrideFlag:
        '''The title vertical inside border override is present.'''
        ...
    
    @classmethod
    @property
    def TITLE_VERTICAL_RIGHT(cls) -> CadTableBorderOverrideFlag:
        '''The title vertical right border override is present.'''
        ...
    
    @classmethod
    @property
    def HEADER_HORIZONTAL_TOP(cls) -> CadTableBorderOverrideFlag:
        '''The header horizontal top border override is present.'''
        ...
    
    @classmethod
    @property
    def HEADER_HORIZONTAL_INSIDE(cls) -> CadTableBorderOverrideFlag:
        '''The header horizontal inside border override is present.'''
        ...
    
    @classmethod
    @property
    def HEADER_HORIZONTAL_BOTTOM(cls) -> CadTableBorderOverrideFlag:
        '''The header horizontal bottom border override is present.'''
        ...
    
    @classmethod
    @property
    def HEADER_VERTICAL_LEFT(cls) -> CadTableBorderOverrideFlag:
        '''The header vertical left border override is present.'''
        ...
    
    @classmethod
    @property
    def HEADER_VERTICAL_INSIDE(cls) -> CadTableBorderOverrideFlag:
        '''The header vertical inside border override is present.'''
        ...
    
    @classmethod
    @property
    def HEADER_VERTICAL_RIGHT(cls) -> CadTableBorderOverrideFlag:
        '''The header vertical right border override is present.'''
        ...
    
    @classmethod
    @property
    def DATA_HORIZONTAL_TOP(cls) -> CadTableBorderOverrideFlag:
        '''The data horizontal top border override is present.'''
        ...
    
    @classmethod
    @property
    def DATA_HORIZONTAL_INSIDE(cls) -> CadTableBorderOverrideFlag:
        '''The data horizontal inside border override is present.'''
        ...
    
    @classmethod
    @property
    def DATA_HORIZONTAL_BOTTOM(cls) -> CadTableBorderOverrideFlag:
        '''The data horizontal bottom border override is present.'''
        ...
    
    @classmethod
    @property
    def DATA_VERTICAL_LEFT(cls) -> CadTableBorderOverrideFlag:
        '''The data vertical left border override is present.'''
        ...
    
    @classmethod
    @property
    def DATA_VERTICAL_INSIDE(cls) -> CadTableBorderOverrideFlag:
        '''The data vertical inside border override is present.'''
        ...
    
    @classmethod
    @property
    def DATA_VERTICAL_RIGHT(cls) -> CadTableBorderOverrideFlag:
        '''The data vertical right border override is present.'''
        ...
    
    ...

class CadTableOptionFlag:
    '''Table option flag'''
    
    @classmethod
    @property
    def ENABLE_BREAKS(cls) -> CadTableOptionFlag:
        '''Enable breaks'''
        ...
    
    @classmethod
    @property
    def REPEAT_TOP_LABELS(cls) -> CadTableOptionFlag:
        '''Repeat top labels'''
        ...
    
    @classmethod
    @property
    def REPEAT_BOTTOM_LABELS(cls) -> CadTableOptionFlag:
        '''Repeat bottom labels'''
        ...
    
    @classmethod
    @property
    def ALLOW_MANUAL_POSITIONS(cls) -> CadTableOptionFlag:
        '''Allow manual positions'''
        ...
    
    @classmethod
    @property
    def ALLOW_MANUAL_HEIGHTS(cls) -> CadTableOptionFlag:
        '''Allow manual heights'''
        ...
    
    ...

class CadTableSymbols:
    '''Contains TABLE Types'''
    
    @classmethod
    @property
    def APPID(cls) -> CadTableSymbols:
        '''The application id.'''
        ...
    
    @classmethod
    @property
    def DIMSTYLE(cls) -> CadTableSymbols:
        '''The dimension style .'''
        ...
    
    @classmethod
    @property
    def LAYER(cls) -> CadTableSymbols:
        '''The layer table.'''
        ...
    
    @classmethod
    @property
    def LTYPE(cls) -> CadTableSymbols:
        '''The line type.'''
        ...
    
    @classmethod
    @property
    def STYLE(cls) -> CadTableSymbols:
        '''The style table.'''
        ...
    
    @classmethod
    @property
    def UCS(cls) -> CadTableSymbols:
        '''The ucs table.'''
        ...
    
    @classmethod
    @property
    def VIEW(cls) -> CadTableSymbols:
        '''The view table.'''
        ...
    
    @classmethod
    @property
    def VPORT(cls) -> CadTableSymbols:
        '''The view port.'''
        ...
    
    @classmethod
    @property
    def BLOCK_RECORD(cls) -> CadTableSymbols:
        '''The block record.'''
        ...
    
    ...

