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

class HandleCodes:
    '''Handles codes'''
    
    @classmethod
    @property
    def SOFT_OWNERSHIP_REFERENCE(cls) -> int:
        '''Soft ownership reference: the owner does not need the owned object. The owned object
        cannot exist by itself. Code - 2'''
        ...
    
    @classmethod
    @property
    def HARD_OWNERSHIP_REFERENCE(cls) -> int:
        '''Hard ownership reference: the owner needs the owned object. The owned object cannot exist
        by itself. Code - 3'''
        ...
    
    @classmethod
    @property
    def SOFT_POINTER_REFERENCE(cls) -> int:
        '''Soft pointer reference: the referencing object does not need the referenced object and vice
        versa. Code - 4'''
        ...
    
    @classmethod
    @property
    def HARD_POINTER_REFERENCE(cls) -> int:
        '''Hard pointer reference: the referencing object needs the referenced object, but both are
        owned by another object. Code - 5'''
        ...
    
    @classmethod
    @property
    def HANDLE_PLUS_ONE_REFERENCE(cls) -> int:
        '''The handle plus one reference. Code - 6'''
        ...
    
    @classmethod
    @property
    def HANDLE_MINUS_ONE_REFERENCE(cls) -> int:
        '''The handle minus one reference. Code - 8'''
        ...
    
    @classmethod
    @property
    def HANDLE_PLUS_OFFSET_REFERENCE(cls) -> int:
        '''The handle plus offset reference. Code - 10 (0xA)'''
        ...
    
    @classmethod
    @property
    def HANDLE_MINUS_OFFSET_REFERENCE(cls) -> int:
        '''The handle minus offset reference. Code - 12 (0xC)'''
        ...
    
    ...

class AcDbObjectType:
    '''Internal Dwg entity type codes.'''
    
    @classmethod
    @property
    def UNUSED(cls) -> AcDbObjectType:
        '''The unused'''
        ...
    
    @classmethod
    @property
    def TEXT(cls) -> AcDbObjectType:
        '''The text'''
        ...
    
    @classmethod
    @property
    def ATTRIB(cls) -> AcDbObjectType:
        '''The attribute'''
        ...
    
    @classmethod
    @property
    def ATTDEF(cls) -> AcDbObjectType:
        '''The attribute definition'''
        ...
    
    @classmethod
    @property
    def BLOCK(cls) -> AcDbObjectType:
        '''The block'''
        ...
    
    @classmethod
    @property
    def ENDBLK(cls) -> AcDbObjectType:
        '''The end block'''
        ...
    
    @classmethod
    @property
    def SEQEND(cls) -> AcDbObjectType:
        '''The entity'''
        ...
    
    @classmethod
    @property
    def INSERT(cls) -> AcDbObjectType:
        '''The insert'''
        ...
    
    @classmethod
    @property
    def MINSERT(cls) -> AcDbObjectType:
        '''The entity'''
        ...
    
    @classmethod
    @property
    def VERTEX_2D(cls) -> AcDbObjectType:
        '''The 2D-vertex'''
        ...
    
    @classmethod
    @property
    def VERTEX_3D(cls) -> AcDbObjectType:
        '''The 3D-vertex'''
        ...
    
    @classmethod
    @property
    def VERTEX_MESH(cls) -> AcDbObjectType:
        '''The vertex mesh'''
        ...
    
    @classmethod
    @property
    def VERTEX_PFACE(cls) -> AcDbObjectType:
        '''The vertex face'''
        ...
    
    @classmethod
    @property
    def VERTEX_PFACE_FACE(cls) -> AcDbObjectType:
        '''The vertex face'''
        ...
    
    @classmethod
    @property
    def POLYLINE_2D(cls) -> AcDbObjectType:
        '''The polyline 2D'''
        ...
    
    @classmethod
    @property
    def POLYLINE_3D(cls) -> AcDbObjectType:
        '''The polyline 3D'''
        ...
    
    @classmethod
    @property
    def ARC(cls) -> AcDbObjectType:
        '''The arc'''
        ...
    
    @classmethod
    @property
    def CIRCLE(cls) -> AcDbObjectType:
        '''The circle'''
        ...
    
    @classmethod
    @property
    def LINE(cls) -> AcDbObjectType:
        '''The line'''
        ...
    
    @classmethod
    @property
    def DIMENSION_ORDINATE(cls) -> AcDbObjectType:
        '''The dimension ordinate'''
        ...
    
    @classmethod
    @property
    def DIMENSION_LINEAR(cls) -> AcDbObjectType:
        '''The dimension linear'''
        ...
    
    @classmethod
    @property
    def DIMENSION_ALIGNED(cls) -> AcDbObjectType:
        '''The dimension aligned'''
        ...
    
    @classmethod
    @property
    def DIMENSION_ANG_3_PT(cls) -> AcDbObjectType:
        '''The dimension angle 3 point'''
        ...
    
    @classmethod
    @property
    def DIMENSION_ANG_2_LN(cls) -> AcDbObjectType:
        '''The dimension angle'''
        ...
    
    @classmethod
    @property
    def DIMENSION_RADIUS(cls) -> AcDbObjectType:
        '''The dimension radius'''
        ...
    
    @classmethod
    @property
    def DIMENSION_DIAMETER(cls) -> AcDbObjectType:
        '''The dimension diameter'''
        ...
    
    @classmethod
    @property
    def POINT(cls) -> AcDbObjectType:
        '''The point'''
        ...
    
    @classmethod
    @property
    def FACE3D(cls) -> AcDbObjectType:
        '''The face 3d'''
        ...
    
    @classmethod
    @property
    def POLYLINE_PFACE(cls) -> AcDbObjectType:
        '''The polyline face'''
        ...
    
    @classmethod
    @property
    def POLYLINE_MESH(cls) -> AcDbObjectType:
        '''The polyline mesh'''
        ...
    
    @classmethod
    @property
    def SOLID(cls) -> AcDbObjectType:
        '''The solid'''
        ...
    
    @classmethod
    @property
    def TRACE(cls) -> AcDbObjectType:
        '''The trace'''
        ...
    
    @classmethod
    @property
    def SHAPE(cls) -> AcDbObjectType:
        '''The shape'''
        ...
    
    @classmethod
    @property
    def VIEWPORT(cls) -> AcDbObjectType:
        '''The viewport'''
        ...
    
    @classmethod
    @property
    def ELLIPSE(cls) -> AcDbObjectType:
        '''The ellipse'''
        ...
    
    @classmethod
    @property
    def SPLINE(cls) -> AcDbObjectType:
        '''The spline'''
        ...
    
    @classmethod
    @property
    def REGION(cls) -> AcDbObjectType:
        '''The region'''
        ...
    
    @classmethod
    @property
    def SOLID3D(cls) -> AcDbObjectType:
        '''The solid 3d'''
        ...
    
    @classmethod
    @property
    def BODY(cls) -> AcDbObjectType:
        '''The body'''
        ...
    
    @classmethod
    @property
    def RAY(cls) -> AcDbObjectType:
        '''The ray'''
        ...
    
    @classmethod
    @property
    def XLINE(cls) -> AcDbObjectType:
        '''The line'''
        ...
    
    @classmethod
    @property
    def DICTIONARY(cls) -> AcDbObjectType:
        '''The dictionary'''
        ...
    
    @classmethod
    @property
    def OLEFRAME(cls) -> AcDbObjectType:
        '''The ole frame'''
        ...
    
    @classmethod
    @property
    def MTEXT(cls) -> AcDbObjectType:
        '''The text'''
        ...
    
    @classmethod
    @property
    def LEADER(cls) -> AcDbObjectType:
        '''The leader'''
        ...
    
    @classmethod
    @property
    def TOLERANCE(cls) -> AcDbObjectType:
        '''The tolerance'''
        ...
    
    @classmethod
    @property
    def MLINE(cls) -> AcDbObjectType:
        '''The line'''
        ...
    
    @classmethod
    @property
    def BLOCK_CONTROL(cls) -> AcDbObjectType:
        '''The block control'''
        ...
    
    @classmethod
    @property
    def BLOCK_HEADER(cls) -> AcDbObjectType:
        '''The block header'''
        ...
    
    @classmethod
    @property
    def LAYER_CONTROL(cls) -> AcDbObjectType:
        '''The layer control'''
        ...
    
    @classmethod
    @property
    def LAYER(cls) -> AcDbObjectType:
        '''The layer'''
        ...
    
    @classmethod
    @property
    def STYLE_CONTROL(cls) -> AcDbObjectType:
        '''The style control'''
        ...
    
    @classmethod
    @property
    def STYLE(cls) -> AcDbObjectType:
        '''The style'''
        ...
    
    @classmethod
    @property
    def LTYPE_CONTROL(cls) -> AcDbObjectType:
        '''The ltype control'''
        ...
    
    @classmethod
    @property
    def LTYPE(cls) -> AcDbObjectType:
        '''The type'''
        ...
    
    @classmethod
    @property
    def VIEW_CONTROL(cls) -> AcDbObjectType:
        '''The view control'''
        ...
    
    @classmethod
    @property
    def VIEW(cls) -> AcDbObjectType:
        '''The view'''
        ...
    
    @classmethod
    @property
    def UCS_CONTROL(cls) -> AcDbObjectType:
        '''The ucs control'''
        ...
    
    @classmethod
    @property
    def UCS(cls) -> AcDbObjectType:
        '''The entity'''
        ...
    
    @classmethod
    @property
    def VPORT_CONTROL(cls) -> AcDbObjectType:
        '''The vport control'''
        ...
    
    @classmethod
    @property
    def VPORT(cls) -> AcDbObjectType:
        '''The view port'''
        ...
    
    @classmethod
    @property
    def APPID_BLOCK(cls) -> AcDbObjectType:
        '''The application id block'''
        ...
    
    @classmethod
    @property
    def APPID(cls) -> AcDbObjectType:
        '''The application id'''
        ...
    
    @classmethod
    @property
    def DIMSTYLE_BLOCK(cls) -> AcDbObjectType:
        '''The dimstyle block'''
        ...
    
    @classmethod
    @property
    def DIMSTYLE(cls) -> AcDbObjectType:
        '''The dimension style'''
        ...
    
    @classmethod
    @property
    def VP_ENT_HDR(cls) -> AcDbObjectType:
        '''The entity'''
        ...
    
    @classmethod
    @property
    def GROUP(cls) -> AcDbObjectType:
        '''The group'''
        ...
    
    @classmethod
    @property
    def MLINESTYLE(cls) -> AcDbObjectType:
        '''The line style'''
        ...
    
    @classmethod
    @property
    def OLE2FRAME(cls) -> AcDbObjectType:
        '''The ole frame'''
        ...
    
    @classmethod
    @property
    def DUMMY(cls) -> AcDbObjectType:
        '''The dummy'''
        ...
    
    @classmethod
    @property
    def LONG_TRANSACTION(cls) -> AcDbObjectType:
        '''The long transaction'''
        ...
    
    @classmethod
    @property
    def LWPOLYLINE(cls) -> AcDbObjectType:
        '''The polyline'''
        ...
    
    @classmethod
    @property
    def HATCH(cls) -> AcDbObjectType:
        '''The hatch'''
        ...
    
    @classmethod
    @property
    def XRECORD(cls) -> AcDbObjectType:
        '''The record'''
        ...
    
    @classmethod
    @property
    def ACDBPLACEHOLDER(cls) -> AcDbObjectType:
        '''The place holder'''
        ...
    
    @classmethod
    @property
    def VBA_PROJECT(cls) -> AcDbObjectType:
        '''The visual basic project'''
        ...
    
    @classmethod
    @property
    def LAYOUT(cls) -> AcDbObjectType:
        '''The layout'''
        ...
    
    @classmethod
    @property
    def ACAD_TABLE(cls) -> AcDbObjectType:
        '''The table'''
        ...
    
    @classmethod
    @property
    def TABLECONTENT(cls) -> AcDbObjectType:
        '''The table content'''
        ...
    
    @classmethod
    @property
    def CELLSTYLEMAP(cls) -> AcDbObjectType:
        '''The cell style map'''
        ...
    
    @classmethod
    @property
    def DBCOLOR(cls) -> AcDbObjectType:
        '''The color'''
        ...
    
    @classmethod
    @property
    def DICTIONARYVAR(cls) -> AcDbObjectType:
        '''The dictionary entity'''
        ...
    
    @classmethod
    @property
    def FIELD(cls) -> AcDbObjectType:
        '''The field'''
        ...
    
    @classmethod
    @property
    def GROUP_500(cls) -> AcDbObjectType:
        '''The group'''
        ...
    
    @classmethod
    @property
    def HATCH_500(cls) -> AcDbObjectType:
        '''The hatch'''
        ...
    
    @classmethod
    @property
    def IDBUFFER(cls) -> AcDbObjectType:
        '''The id buffer'''
        ...
    
    @classmethod
    @property
    def IMAGE(cls) -> AcDbObjectType:
        '''The image'''
        ...
    
    @classmethod
    @property
    def IMAGEDEF(cls) -> AcDbObjectType:
        '''The image definition'''
        ...
    
    @classmethod
    @property
    def IMAGEDEFREACTOR(cls) -> AcDbObjectType:
        '''The image reactor'''
        ...
    
    @classmethod
    @property
    def LAYER_INDEX(cls) -> AcDbObjectType:
        '''The layer index'''
        ...
    
    @classmethod
    @property
    def LIGHT(cls) -> AcDbObjectType:
        '''Light for 3D render'''
        ...
    
    @classmethod
    @property
    def LWPLINE(cls) -> AcDbObjectType:
        '''The line'''
        ...
    
    @classmethod
    @property
    def MATERIAL(cls) -> AcDbObjectType:
        '''The material'''
        ...
    
    @classmethod
    @property
    def MLEADER(cls) -> AcDbObjectType:
        '''The leader'''
        ...
    
    @classmethod
    @property
    def MLEADERSTYLE(cls) -> AcDbObjectType:
        '''The leader style'''
        ...
    
    @classmethod
    @property
    def MESH(cls) -> AcDbObjectType:
        '''The mesh'''
        ...
    
    @classmethod
    @property
    def OLE2FRAME_500(cls) -> AcDbObjectType:
        '''The ole frame'''
        ...
    
    @classmethod
    @property
    def PLACEHOLDER(cls) -> AcDbObjectType:
        '''The place holder'''
        ...
    
    @classmethod
    @property
    def PLOTSETTINGS(cls) -> AcDbObjectType:
        '''The plot settings'''
        ...
    
    @classmethod
    @property
    def RASTERVARIABLES(cls) -> AcDbObjectType:
        '''The raster variables'''
        ...
    
    @classmethod
    @property
    def SCALE(cls) -> AcDbObjectType:
        '''The scale'''
        ...
    
    @classmethod
    @property
    def SORTENTSTABLE(cls) -> AcDbObjectType:
        '''The sort table'''
        ...
    
    @classmethod
    @property
    def SPATIAL_FILTER(cls) -> AcDbObjectType:
        '''The spatial filter'''
        ...
    
    @classmethod
    @property
    def SPATIAL_INDEX(cls) -> AcDbObjectType:
        '''The spatial index'''
        ...
    
    @classmethod
    @property
    def SUN(cls) -> AcDbObjectType:
        '''Sun for 3D render'''
        ...
    
    @classmethod
    @property
    def TABLEGEOMETRY(cls) -> AcDbObjectType:
        '''The table geometry'''
        ...
    
    @classmethod
    @property
    def TABLESTYLES(cls) -> AcDbObjectType:
        '''The table styles'''
        ...
    
    @classmethod
    @property
    def SECTIONVIEWSTYLE(cls) -> AcDbObjectType:
        '''The section view style'''
        ...
    
    @classmethod
    @property
    def DETAILVIEWSTYLE(cls) -> AcDbObjectType:
        '''The detail view style'''
        ...
    
    @classmethod
    @property
    def RAPIDRTRENDERSETTINGS(cls) -> AcDbObjectType:
        '''The rapid rt render setting'''
        ...
    
    @classmethod
    @property
    def ACDBPERSSUBENTMANAGER(cls) -> AcDbObjectType:
        '''The pers subent manager'''
        ...
    
    @classmethod
    @property
    def ACDBASSOCPERSSUBENTMANAGER(cls) -> AcDbObjectType:
        '''The assoc pers subent manager'''
        ...
    
    @classmethod
    @property
    def ACAD_EVALUATION_GRAPH(cls) -> AcDbObjectType:
        '''The acad evaluation graph'''
        ...
    
    @classmethod
    @property
    def DIMASSOC(cls) -> AcDbObjectType:
        '''The dim assoc'''
        ...
    
    @classmethod
    @property
    def ARC_DIMENSION(cls) -> AcDbObjectType:
        '''The arc dimension'''
        ...
    
    @classmethod
    @property
    def LARGE_RADIAL_DIMENSION(cls) -> AcDbObjectType:
        '''The jogged dimension'''
        ...
    
    @classmethod
    @property
    def FIELDLIST(cls) -> AcDbObjectType:
        ...
    
    @classmethod
    @property
    def SOLID_BACKGROUND(cls) -> AcDbObjectType:
        '''The solid background'''
        ...
    
    @classmethod
    @property
    def GRADIENT_BACKGROUND(cls) -> AcDbObjectType:
        '''The gradient background'''
        ...
    
    @classmethod
    @property
    def SKYLIGHT_BACKGROUND(cls) -> AcDbObjectType:
        '''The skyLight background'''
        ...
    
    @classmethod
    @property
    def ACSH_BOX_CLASS(cls) -> AcDbObjectType:
        '''The Acsh Box Class'''
        ...
    
    @classmethod
    @property
    def ACSH_CONE_CLASS(cls) -> AcDbObjectType:
        '''The Acsh Cone Class'''
        ...
    
    @classmethod
    @property
    def ACSH_CYLINDER_CLASS(cls) -> AcDbObjectType:
        '''The Acsh Cylinder Class'''
        ...
    
    @classmethod
    @property
    def ACSH_PYRAMID_CLASS(cls) -> AcDbObjectType:
        '''The Acsh Pyramid Class'''
        ...
    
    @classmethod
    @property
    def ACSH_SPHERE_CLASS(cls) -> AcDbObjectType:
        '''The Acsh Sphere Class'''
        ...
    
    @classmethod
    @property
    def ACSH_TORUS_CLASS(cls) -> AcDbObjectType:
        '''The Acsh Torus Class'''
        ...
    
    @classmethod
    @property
    def ACSH_WEDGE_CLASS(cls) -> AcDbObjectType:
        '''The Acsh Wedge Class'''
        ...
    
    @classmethod
    @property
    def VLO_VL(cls) -> AcDbObjectType:
        '''The VLO-VL object'''
        ...
    
    @classmethod
    @property
    def LSDEFINITION(cls) -> AcDbObjectType:
        '''The LSDEFINITION object'''
        ...
    
    @classmethod
    @property
    def LSSTROKEPATTERNCOMPONENT(cls) -> AcDbObjectType:
        '''The LSSTROKEPATTERNCOMPONENT object'''
        ...
    
    @classmethod
    @property
    def LSINTERNALCOMPONENT(cls) -> AcDbObjectType:
        '''The LSINTERNALCOMPONENT object'''
        ...
    
    @classmethod
    @property
    def LSCOMPOUNDCOMPONENT(cls) -> AcDbObjectType:
        '''The LSCOMPOUNDCOMPONENT object'''
        ...
    
    @classmethod
    @property
    def LSPOINTCOMPONENT(cls) -> AcDbObjectType:
        '''The LSPOINTCOMPONENT object'''
        ...
    
    @classmethod
    @property
    def LSSYMBOLCOMPONENT(cls) -> AcDbObjectType:
        '''The LSSYMBOLCOMPONENT object'''
        ...
    
    @classmethod
    @property
    def ACDBASSOCNETWORK(cls) -> AcDbObjectType:
        '''The ACDBASSOCNETWORK'''
        ...
    
    @classmethod
    @property
    def ACDBASSOCVARIABLE(cls) -> AcDbObjectType:
        '''The ACDBASSOCVARIABLE'''
        ...
    
    @classmethod
    @property
    def ACDBASSOC2DCONSTRAINTGROUP(cls) -> AcDbObjectType:
        '''The ACDBASSOC2DCONSTRAINTGROUP'''
        ...
    
    @classmethod
    @property
    def ACDBASSOCDEPENDENCY(cls) -> AcDbObjectType:
        '''The ACDBASSOCDEPENDENCY'''
        ...
    
    @classmethod
    @property
    def ACDBASSOCVALUEDEPENDENCY(cls) -> AcDbObjectType:
        '''The ACDBASSOCVALUEDEPENDENCY'''
        ...
    
    @classmethod
    @property
    def ACDBASSOCGEOMDEPENDENCY(cls) -> AcDbObjectType:
        '''The ACDBASSOCGEOMDEPENDENCY'''
        ...
    
    @classmethod
    @property
    def VBA_PROJECT_500(cls) -> AcDbObjectType:
        '''The project'''
        ...
    
    @classmethod
    @property
    def VISUALSTYLE(cls) -> AcDbObjectType:
        '''The visual style'''
        ...
    
    @classmethod
    @property
    def WIPEOUTVARIABLE(cls) -> AcDbObjectType:
        '''The wipe out variable'''
        ...
    
    @classmethod
    @property
    def XRECORD_500(cls) -> AcDbObjectType:
        '''The record'''
        ...
    
    @classmethod
    @property
    def DGNUNDERLAY(cls) -> AcDbObjectType:
        '''The dgnunderlay'''
        ...
    
    @classmethod
    @property
    def DGNDEFINITION(cls) -> AcDbObjectType:
        '''The dgndefinition'''
        ...
    
    @classmethod
    @property
    def DWFUNDERLAY(cls) -> AcDbObjectType:
        '''The dwfunderlay'''
        ...
    
    @classmethod
    @property
    def DWFDEFINITION(cls) -> AcDbObjectType:
        '''The dwfdefinition'''
        ...
    
    @classmethod
    @property
    def PDFUNDERLAY(cls) -> AcDbObjectType:
        '''The pdfunderlay'''
        ...
    
    @classmethod
    @property
    def PDFDEFINITION(cls) -> AcDbObjectType:
        '''The pdfdefinition'''
        ...
    
    @classmethod
    @property
    def AECIDBIMAGEDEF(cls) -> AcDbObjectType:
        '''The embedded image definition'''
        ...
    
    @classmethod
    @property
    def IMAGEDATA(cls) -> AcDbObjectType:
        '''The embedded image data'''
        ...
    
    @classmethod
    @property
    def EMBEDDEDIMAGE(cls) -> AcDbObjectType:
        '''The embedded image'''
        ...
    
    @classmethod
    @property
    def ACIDBLOCKREFERENCE(cls) -> AcDbObjectType:
        '''The block reference'''
        ...
    
    @classmethod
    @property
    def ACAD_PROXY_ENTITY(cls) -> AcDbObjectType:
        '''The ACAD_PROXY_ENTITY'''
        ...
    
    @classmethod
    @property
    def ACAD_PROXY_OBJECT(cls) -> AcDbObjectType:
        '''The ACAD_PROXY_OBJECT'''
        ...
    
    @classmethod
    @property
    def WIPEOUT(cls) -> AcDbObjectType:
        '''The wipe out'''
        ...
    
    @classmethod
    @property
    def HISTORY(cls) -> AcDbObjectType:
        '''The history'''
        ...
    
    @classmethod
    @property
    def PLANESURFACE(cls) -> AcDbObjectType:
        '''The plane surface'''
        ...
    
    @classmethod
    @property
    def EXTRUDEDSURFACE(cls) -> AcDbObjectType:
        '''The extruded surface'''
        ...
    
    @classmethod
    @property
    def REVOLVEDSURFACE(cls) -> AcDbObjectType:
        '''The revolved surface'''
        ...
    
    @classmethod
    @property
    def LOFTEDSURFACE(cls) -> AcDbObjectType:
        '''The lofted surface'''
        ...
    
    @classmethod
    @property
    def SWEPTSURFACE(cls) -> AcDbObjectType:
        '''The swept surface'''
        ...
    
    @classmethod
    @property
    def R11_COMMON_POLYLINE(cls) -> AcDbObjectType:
        '''Arbitraty proxy code for an R11 polyline entity to create intermediate reader that creates reader for specific polyline type. Feel free to change if it interferes with anything.'''
        ...
    
    @classmethod
    @property
    def R11_COMMON_VERTEX(cls) -> AcDbObjectType:
        '''Arbitraty proxy code for an R11 vertex entity to create intermediate reader that creates reader for specific vertex type. Feel free to change if it interferes with anything.'''
        ...
    
    @classmethod
    @property
    def R11_COMMON_DIMENSION(cls) -> AcDbObjectType:
        '''Arbitraty proxy code for an R11 dimension entity to create intermediate reader that creates reader for specific dimension type. Feel free to change if it interferes with anything.'''
        ...
    
    @classmethod
    @property
    def DICTIONARYWDFLT(cls) -> AcDbObjectType:
        '''The DICTIONARYWDFLT'''
        ...
    
    ...

