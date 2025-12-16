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

class ApplicationStructureDescriptorElements:
    
    @staticmethod
    def create_command(element_id : int, element_class : int, container : aspose.cad.fileformats.cgm.CgmFile) -> aspose.cad.fileformats.cgm.commands.Command:
        ...
    
    ...

class AttributeElements:
    
    @staticmethod
    def create_command(element_id : int, element_class : int, container : aspose.cad.fileformats.cgm.CgmFile) -> aspose.cad.fileformats.cgm.commands.Command:
        ...
    
    ...

class ControlElements:
    
    @staticmethod
    def create_command(element_id : int, element_class : int, container : aspose.cad.fileformats.cgm.CgmFile) -> aspose.cad.fileformats.cgm.commands.Command:
        ...
    
    ...

class DelimiterElements:
    
    @staticmethod
    def create_command(element_id : int, element_class : int, container : aspose.cad.fileformats.cgm.CgmFile) -> aspose.cad.fileformats.cgm.commands.Command:
        ...
    
    ...

class ExternalElements:
    
    @staticmethod
    def create_command(element_id : int, element_class : int, container : aspose.cad.fileformats.cgm.CgmFile) -> aspose.cad.fileformats.cgm.commands.Command:
        ...
    
    ...

class GraphicalPrimitiveElements:
    
    @staticmethod
    def create_command(element_id : int, element_class : int, container : aspose.cad.fileformats.cgm.CgmFile) -> aspose.cad.fileformats.cgm.commands.Command:
        ...
    
    ...

class MetaFileDescriptorElements:
    
    @staticmethod
    def create_command(element_id : int, element_class : int, container : aspose.cad.fileformats.cgm.CgmFile) -> aspose.cad.fileformats.cgm.commands.Command:
        ...
    
    ...

class PictureDescriptorElements:
    
    @staticmethod
    def create_command(element_id : int, element_class : int, container : aspose.cad.fileformats.cgm.CgmFile) -> aspose.cad.fileformats.cgm.commands.Command:
        ...
    
    ...

class SegmentControlElements:
    
    @staticmethod
    def create_command(element_id : int, element_class : int, container : aspose.cad.fileformats.cgm.CgmFile) -> aspose.cad.fileformats.cgm.commands.Command:
        ...
    
    ...

class ApplicationStructureDescriptorElement:
    
    @classmethod
    @property
    def UNUSED_0(cls) -> ApplicationStructureDescriptorElement:
        ...
    
    @classmethod
    @property
    def APPLICATION_STRUCTURE_ATTRIBUTE(cls) -> ApplicationStructureDescriptorElement:
        ...
    
    ...

class AttributeElement:
    
    @classmethod
    @property
    def UNUSED_0(cls) -> AttributeElement:
        ...
    
    @classmethod
    @property
    def LINE_BUNDLE_INDEX(cls) -> AttributeElement:
        ...
    
    @classmethod
    @property
    def LINE_TYPE(cls) -> AttributeElement:
        ...
    
    @classmethod
    @property
    def LINE_WIDTH(cls) -> AttributeElement:
        ...
    
    @classmethod
    @property
    def LINE_COLOUR(cls) -> AttributeElement:
        ...
    
    @classmethod
    @property
    def MARKER_BUNDLE_INDEX(cls) -> AttributeElement:
        ...
    
    @classmethod
    @property
    def MARKER_TYPE(cls) -> AttributeElement:
        ...
    
    @classmethod
    @property
    def MARKER_SIZE(cls) -> AttributeElement:
        ...
    
    @classmethod
    @property
    def MARKER_COLOUR(cls) -> AttributeElement:
        ...
    
    @classmethod
    @property
    def TEXT_BUNDLE_INDEX(cls) -> AttributeElement:
        ...
    
    @classmethod
    @property
    def TEXT_FONT_INDEX(cls) -> AttributeElement:
        ...
    
    @classmethod
    @property
    def TEXT_PRECISION(cls) -> AttributeElement:
        ...
    
    @classmethod
    @property
    def CHARACTER_EXPANSION_FACTOR(cls) -> AttributeElement:
        ...
    
    @classmethod
    @property
    def CHARACTER_SPACING(cls) -> AttributeElement:
        ...
    
    @classmethod
    @property
    def TEXT_COLOUR(cls) -> AttributeElement:
        ...
    
    @classmethod
    @property
    def CHARACTER_HEIGHT(cls) -> AttributeElement:
        ...
    
    @classmethod
    @property
    def CHARACTER_ORIENTATION(cls) -> AttributeElement:
        ...
    
    @classmethod
    @property
    def TEXT_PATH(cls) -> AttributeElement:
        ...
    
    @classmethod
    @property
    def TEXT_ALIGNMENT(cls) -> AttributeElement:
        ...
    
    @classmethod
    @property
    def CHARACTER_SET_INDEX(cls) -> AttributeElement:
        ...
    
    @classmethod
    @property
    def ALTERNATE_CHARACTER_SET_INDEX(cls) -> AttributeElement:
        ...
    
    @classmethod
    @property
    def FILL_BUNDLE_INDEX(cls) -> AttributeElement:
        ...
    
    @classmethod
    @property
    def INTERIOR_STYLE(cls) -> AttributeElement:
        ...
    
    @classmethod
    @property
    def FILL_COLOUR(cls) -> AttributeElement:
        ...
    
    @classmethod
    @property
    def HATCH_INDEX(cls) -> AttributeElement:
        ...
    
    @classmethod
    @property
    def PATTERN_INDEX(cls) -> AttributeElement:
        ...
    
    @classmethod
    @property
    def EDGE_BUNDLE_INDEX(cls) -> AttributeElement:
        ...
    
    @classmethod
    @property
    def EDGE_TYPE(cls) -> AttributeElement:
        ...
    
    @classmethod
    @property
    def EDGE_WIDTH(cls) -> AttributeElement:
        ...
    
    @classmethod
    @property
    def EDGE_COLOUR(cls) -> AttributeElement:
        ...
    
    @classmethod
    @property
    def EDGE_VISIBILITY(cls) -> AttributeElement:
        ...
    
    @classmethod
    @property
    def FILL_REFERENCE_POINT(cls) -> AttributeElement:
        ...
    
    @classmethod
    @property
    def PATTERN_TABLE(cls) -> AttributeElement:
        ...
    
    @classmethod
    @property
    def PATTERN_SIZE(cls) -> AttributeElement:
        ...
    
    @classmethod
    @property
    def COLOUR_TABLE(cls) -> AttributeElement:
        ...
    
    @classmethod
    @property
    def ASPECT_SOURCE_FLAGS(cls) -> AttributeElement:
        ...
    
    @classmethod
    @property
    def PICK_IDENTIFIER(cls) -> AttributeElement:
        ...
    
    @classmethod
    @property
    def LINE_CAP(cls) -> AttributeElement:
        ...
    
    @classmethod
    @property
    def LINE_JOIN(cls) -> AttributeElement:
        ...
    
    @classmethod
    @property
    def LINE_TYPE_CONTINUATION(cls) -> AttributeElement:
        ...
    
    @classmethod
    @property
    def LINE_TYPE_INITIAL_OFFSET(cls) -> AttributeElement:
        ...
    
    @classmethod
    @property
    def TEXT_SCORE_TYPE(cls) -> AttributeElement:
        ...
    
    @classmethod
    @property
    def RESTRICTED_TEXT_TYPE(cls) -> AttributeElement:
        ...
    
    @classmethod
    @property
    def INTERPOLATED_INTERIOR(cls) -> AttributeElement:
        ...
    
    @classmethod
    @property
    def EDGE_CAP(cls) -> AttributeElement:
        ...
    
    @classmethod
    @property
    def EDGE_JOIN(cls) -> AttributeElement:
        ...
    
    @classmethod
    @property
    def EDGE_TYPE_CONTINUATION(cls) -> AttributeElement:
        ...
    
    @classmethod
    @property
    def EDGE_TYPE_INITIAL_OFFSET(cls) -> AttributeElement:
        ...
    
    @classmethod
    @property
    def SYMBOL_LIBRARY_INDEX(cls) -> AttributeElement:
        ...
    
    @classmethod
    @property
    def SYMBOL_COLOUR(cls) -> AttributeElement:
        ...
    
    @classmethod
    @property
    def SYMBOL_SIZE(cls) -> AttributeElement:
        ...
    
    @classmethod
    @property
    def SYMBOL_ORIENTATION(cls) -> AttributeElement:
        ...
    
    ...

class ControlElement:
    
    @classmethod
    @property
    def UNUSED_0(cls) -> ControlElement:
        ...
    
    @classmethod
    @property
    def VDC_INTEGER_PRECISION(cls) -> ControlElement:
        ...
    
    @classmethod
    @property
    def VDC_REAL_PRECISION(cls) -> ControlElement:
        ...
    
    @classmethod
    @property
    def AUXILIARY_COLOUR(cls) -> ControlElement:
        ...
    
    @classmethod
    @property
    def TRANSPARENCY(cls) -> ControlElement:
        ...
    
    @classmethod
    @property
    def CLIP_RECTANGLE(cls) -> ControlElement:
        ...
    
    @classmethod
    @property
    def CLIP_INDICATOR(cls) -> ControlElement:
        ...
    
    @classmethod
    @property
    def LINE_CLIPPING_MODE(cls) -> ControlElement:
        ...
    
    @classmethod
    @property
    def MARKER_CLIPPING_MODE(cls) -> ControlElement:
        ...
    
    @classmethod
    @property
    def EDGE_CLIPPING_MODE(cls) -> ControlElement:
        ...
    
    @classmethod
    @property
    def NEW_REGION(cls) -> ControlElement:
        ...
    
    @classmethod
    @property
    def SAVE_PRIMITIVE_CONTEXT(cls) -> ControlElement:
        ...
    
    @classmethod
    @property
    def RESTORE_PRIMITIVE_CONTEXT(cls) -> ControlElement:
        ...
    
    @classmethod
    @property
    def UNUSED_13(cls) -> ControlElement:
        ...
    
    @classmethod
    @property
    def UNUSED_14(cls) -> ControlElement:
        ...
    
    @classmethod
    @property
    def UNUSED_15(cls) -> ControlElement:
        ...
    
    @classmethod
    @property
    def UNUSED_16(cls) -> ControlElement:
        ...
    
    @classmethod
    @property
    def PROTECTION_REGION_INDICATOR(cls) -> ControlElement:
        ...
    
    @classmethod
    @property
    def GENERALIZED_TEXT_PATH_MODE(cls) -> ControlElement:
        ...
    
    @classmethod
    @property
    def MITRE_LIMIT(cls) -> ControlElement:
        ...
    
    @classmethod
    @property
    def TRANSPARENT_CELL_COLOUR(cls) -> ControlElement:
        ...
    
    ...

class DelimiterElement:
    '''Delimiter Elements'''
    
    @classmethod
    @property
    def NO_OP(cls) -> DelimiterElement:
        ...
    
    @classmethod
    @property
    def BEGIN_METAFILE(cls) -> DelimiterElement:
        ...
    
    @classmethod
    @property
    def END_METAFILE(cls) -> DelimiterElement:
        ...
    
    @classmethod
    @property
    def BEGIN_PICTURE(cls) -> DelimiterElement:
        ...
    
    @classmethod
    @property
    def BEGIN_PICTURE_BODY(cls) -> DelimiterElement:
        ...
    
    @classmethod
    @property
    def END_PICTURE(cls) -> DelimiterElement:
        ...
    
    @classmethod
    @property
    def BEGIN_SEGMENT(cls) -> DelimiterElement:
        ...
    
    @classmethod
    @property
    def END_SEGMENT(cls) -> DelimiterElement:
        ...
    
    @classmethod
    @property
    def BEGIN_FIGURE(cls) -> DelimiterElement:
        ...
    
    @classmethod
    @property
    def END_FIGURE(cls) -> DelimiterElement:
        ...
    
    @classmethod
    @property
    def UNUSED_10(cls) -> DelimiterElement:
        ...
    
    @classmethod
    @property
    def UNUSED_11(cls) -> DelimiterElement:
        ...
    
    @classmethod
    @property
    def UNUSED_12(cls) -> DelimiterElement:
        ...
    
    @classmethod
    @property
    def BEGIN_PROTECTION_REGION(cls) -> DelimiterElement:
        ...
    
    @classmethod
    @property
    def END_PROTECTION_REGION(cls) -> DelimiterElement:
        ...
    
    @classmethod
    @property
    def BEGIN_COMPOUND_LINE(cls) -> DelimiterElement:
        ...
    
    @classmethod
    @property
    def END_COMPOUND_LINE(cls) -> DelimiterElement:
        ...
    
    @classmethod
    @property
    def BEGIN_COMPOUND_TEXT_PATH(cls) -> DelimiterElement:
        ...
    
    @classmethod
    @property
    def END_COMPOUND_TEXT_PATH(cls) -> DelimiterElement:
        ...
    
    @classmethod
    @property
    def BEGIN_TILE_ARRAY(cls) -> DelimiterElement:
        ...
    
    @classmethod
    @property
    def END_TILE_ARRAY(cls) -> DelimiterElement:
        ...
    
    @classmethod
    @property
    def BEGIN_APPLICATION_STRUCTURE(cls) -> DelimiterElement:
        ...
    
    @classmethod
    @property
    def BEGIN_APPLICATION_STRUCTURE_BODY(cls) -> DelimiterElement:
        ...
    
    @classmethod
    @property
    def END_APPLICATION_STRUCTURE(cls) -> DelimiterElement:
        ...
    
    ...

class ExternalElement:
    
    @classmethod
    @property
    def UNUSED_0(cls) -> ExternalElement:
        ...
    
    @classmethod
    @property
    def MESSAGE(cls) -> ExternalElement:
        ...
    
    @classmethod
    @property
    def APPLICATION_DATA(cls) -> ExternalElement:
        ...
    
    ...

class GraphicalPrimitiveElement:
    
    @classmethod
    @property
    def UNUSED_0(cls) -> GraphicalPrimitiveElement:
        ...
    
    @classmethod
    @property
    def POLYLINE(cls) -> GraphicalPrimitiveElement:
        ...
    
    @classmethod
    @property
    def DISJOINT_POLYLINE(cls) -> GraphicalPrimitiveElement:
        ...
    
    @classmethod
    @property
    def POLYMARKER(cls) -> GraphicalPrimitiveElement:
        ...
    
    @classmethod
    @property
    def TEXT(cls) -> GraphicalPrimitiveElement:
        ...
    
    @classmethod
    @property
    def RESTRICTED_TEXT(cls) -> GraphicalPrimitiveElement:
        ...
    
    @classmethod
    @property
    def APPEND_TEXT(cls) -> GraphicalPrimitiveElement:
        ...
    
    @classmethod
    @property
    def POLYGON(cls) -> GraphicalPrimitiveElement:
        ...
    
    @classmethod
    @property
    def POLYGON_SET(cls) -> GraphicalPrimitiveElement:
        ...
    
    @classmethod
    @property
    def CELL_ARRAY(cls) -> GraphicalPrimitiveElement:
        ...
    
    @classmethod
    @property
    def GENERALIZED_DRAWING_PRIMITIVE(cls) -> GraphicalPrimitiveElement:
        ...
    
    @classmethod
    @property
    def RECTANGLE(cls) -> GraphicalPrimitiveElement:
        ...
    
    @classmethod
    @property
    def CIRCLE(cls) -> GraphicalPrimitiveElement:
        ...
    
    @classmethod
    @property
    def CIRCULAR_ARC_3_POINT(cls) -> GraphicalPrimitiveElement:
        ...
    
    @classmethod
    @property
    def CIRCULAR_ARC_3_POINT_CLOSE(cls) -> GraphicalPrimitiveElement:
        ...
    
    @classmethod
    @property
    def CIRCULAR_ARC_CENTRE(cls) -> GraphicalPrimitiveElement:
        ...
    
    @classmethod
    @property
    def CIRCULAR_ARC_CENTRE_CLOSE(cls) -> GraphicalPrimitiveElement:
        ...
    
    @classmethod
    @property
    def ELLIPSE(cls) -> GraphicalPrimitiveElement:
        ...
    
    @classmethod
    @property
    def ELLIPTICAL_ARC(cls) -> GraphicalPrimitiveElement:
        ...
    
    @classmethod
    @property
    def ELLIPTICAL_ARC_CLOSE(cls) -> GraphicalPrimitiveElement:
        ...
    
    @classmethod
    @property
    def CIRCULAR_ARC_CENTRE_REVERSED(cls) -> GraphicalPrimitiveElement:
        ...
    
    @classmethod
    @property
    def CONNECTING_EDGE(cls) -> GraphicalPrimitiveElement:
        ...
    
    @classmethod
    @property
    def HYPERBOLIC_ARC(cls) -> GraphicalPrimitiveElement:
        ...
    
    @classmethod
    @property
    def PARABOLIC_ARC(cls) -> GraphicalPrimitiveElement:
        ...
    
    @classmethod
    @property
    def NON_UNIFORM_B_SPLINE(cls) -> GraphicalPrimitiveElement:
        ...
    
    @classmethod
    @property
    def NON_UNIFORM_RATIONAL_B_SPLINE(cls) -> GraphicalPrimitiveElement:
        ...
    
    @classmethod
    @property
    def POLYBEZIER(cls) -> GraphicalPrimitiveElement:
        ...
    
    @classmethod
    @property
    def POLYSYMBOL(cls) -> GraphicalPrimitiveElement:
        ...
    
    @classmethod
    @property
    def BITONAL_TILE(cls) -> GraphicalPrimitiveElement:
        ...
    
    @classmethod
    @property
    def TILE(cls) -> GraphicalPrimitiveElement:
        ...
    
    ...

class MetaFileDescriptorElement:
    
    @classmethod
    @property
    def UNUSED_0(cls) -> MetaFileDescriptorElement:
        ...
    
    @classmethod
    @property
    def METAFILE_VERSION(cls) -> MetaFileDescriptorElement:
        ...
    
    @classmethod
    @property
    def METAFILE_DESCRIPTION(cls) -> MetaFileDescriptorElement:
        ...
    
    @classmethod
    @property
    def VDC_TYPE(cls) -> MetaFileDescriptorElement:
        ...
    
    @classmethod
    @property
    def INTEGER_PRECISION(cls) -> MetaFileDescriptorElement:
        ...
    
    @classmethod
    @property
    def REAL_PRECISION(cls) -> MetaFileDescriptorElement:
        ...
    
    @classmethod
    @property
    def INDEX_PRECISION(cls) -> MetaFileDescriptorElement:
        ...
    
    @classmethod
    @property
    def COLOUR_PRECISION(cls) -> MetaFileDescriptorElement:
        ...
    
    @classmethod
    @property
    def COLOUR_INDEX_PRECISION(cls) -> MetaFileDescriptorElement:
        ...
    
    @classmethod
    @property
    def MAXIMUM_COLOUR_INDEX(cls) -> MetaFileDescriptorElement:
        ...
    
    @classmethod
    @property
    def COLOUR_VALUE_EXTENT(cls) -> MetaFileDescriptorElement:
        ...
    
    @classmethod
    @property
    def METAFILE_ELEMENT_LIST(cls) -> MetaFileDescriptorElement:
        ...
    
    @classmethod
    @property
    def METAFILE_DEFAULTS_REPLACEMENT(cls) -> MetaFileDescriptorElement:
        ...
    
    @classmethod
    @property
    def FONT_LIST(cls) -> MetaFileDescriptorElement:
        ...
    
    @classmethod
    @property
    def CHARACTER_SET_LIST(cls) -> MetaFileDescriptorElement:
        ...
    
    @classmethod
    @property
    def CHARACTER_CODING_ANNOUNCER(cls) -> MetaFileDescriptorElement:
        ...
    
    @classmethod
    @property
    def NAME_PRECISION(cls) -> MetaFileDescriptorElement:
        ...
    
    @classmethod
    @property
    def MAXIMUM_VDC_EXTENT(cls) -> MetaFileDescriptorElement:
        ...
    
    @classmethod
    @property
    def SEGMENT_PRIORITY_EXTENT(cls) -> MetaFileDescriptorElement:
        ...
    
    @classmethod
    @property
    def COLOUR_MODEL(cls) -> MetaFileDescriptorElement:
        ...
    
    @classmethod
    @property
    def COLOUR_CALIBRATION(cls) -> MetaFileDescriptorElement:
        ...
    
    @classmethod
    @property
    def FONT_PROPERTIES(cls) -> MetaFileDescriptorElement:
        ...
    
    @classmethod
    @property
    def GLYPH_MAPPING(cls) -> MetaFileDescriptorElement:
        ...
    
    @classmethod
    @property
    def SYMBOL_LIBRARY_LIST(cls) -> MetaFileDescriptorElement:
        ...
    
    @classmethod
    @property
    def PICTURE_DIRECTORY(cls) -> MetaFileDescriptorElement:
        ...
    
    ...

class PictureDescriptorElement:
    
    @classmethod
    @property
    def UNUSED_0(cls) -> PictureDescriptorElement:
        ...
    
    @classmethod
    @property
    def SCALING_MODE(cls) -> PictureDescriptorElement:
        ...
    
    @classmethod
    @property
    def COLOUR_SELECTION_MODE(cls) -> PictureDescriptorElement:
        ...
    
    @classmethod
    @property
    def LINE_WIDTH_SPECIFICATION_MODE(cls) -> PictureDescriptorElement:
        ...
    
    @classmethod
    @property
    def MARKER_SIZE_SPECIFICATION_MODE(cls) -> PictureDescriptorElement:
        ...
    
    @classmethod
    @property
    def EDGE_WIDTH_SPECIFICATION_MODE(cls) -> PictureDescriptorElement:
        ...
    
    @classmethod
    @property
    def VDC_EXTENT(cls) -> PictureDescriptorElement:
        ...
    
    @classmethod
    @property
    def BACKGROUND_COLOUR(cls) -> PictureDescriptorElement:
        ...
    
    @classmethod
    @property
    def DEVICE_VIEWPORT(cls) -> PictureDescriptorElement:
        ...
    
    @classmethod
    @property
    def DEVICE_VIEWPORT_SPECIFICATION_MODE(cls) -> PictureDescriptorElement:
        ...
    
    @classmethod
    @property
    def DEVICE_VIEWPORT_MAPPING(cls) -> PictureDescriptorElement:
        ...
    
    @classmethod
    @property
    def LINE_REPRESENTATION(cls) -> PictureDescriptorElement:
        ...
    
    @classmethod
    @property
    def MARKER_REPRESENTATION(cls) -> PictureDescriptorElement:
        ...
    
    @classmethod
    @property
    def TEXT_REPRESENTATION(cls) -> PictureDescriptorElement:
        ...
    
    @classmethod
    @property
    def FILL_REPRESENTATION(cls) -> PictureDescriptorElement:
        ...
    
    @classmethod
    @property
    def EDGE_REPRESENTATION(cls) -> PictureDescriptorElement:
        ...
    
    @classmethod
    @property
    def INTERIOR_STYLE_SPECIFICATION_MODE(cls) -> PictureDescriptorElement:
        ...
    
    @classmethod
    @property
    def LINE_AND_EDGE_TYPE_DEFINITION(cls) -> PictureDescriptorElement:
        ...
    
    @classmethod
    @property
    def HATCH_STYLE_DEFINITION(cls) -> PictureDescriptorElement:
        ...
    
    @classmethod
    @property
    def GEOMETRIC_PATTERN_DEFINITION(cls) -> PictureDescriptorElement:
        ...
    
    @classmethod
    @property
    def APPLICATION_STRUCTURE_DIRECTORY(cls) -> PictureDescriptorElement:
        ...
    
    ...

class SegmentControlElement:
    
    @classmethod
    @property
    def COPY_SEGMENT(cls) -> SegmentControlElement:
        ...
    
    @classmethod
    @property
    def INHERITANCE_FILTER(cls) -> SegmentControlElement:
        ...
    
    @classmethod
    @property
    def CLIP_INHERITANCE(cls) -> SegmentControlElement:
        ...
    
    @classmethod
    @property
    def SEGMENT_TRANSFORMATION(cls) -> SegmentControlElement:
        ...
    
    @classmethod
    @property
    def SEGMENT_HIGHLIGHTING(cls) -> SegmentControlElement:
        ...
    
    @classmethod
    @property
    def SEGMENT_DISPLAY_PRIORITY(cls) -> SegmentControlElement:
        ...
    
    @classmethod
    @property
    def SEGMENT_PICK_PRIORITY(cls) -> SegmentControlElement:
        ...
    
    ...

