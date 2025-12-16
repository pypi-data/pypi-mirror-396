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

class ThreeDSCoordinateSystem:
    
    @property
    def axis_x(self) -> aspose.cad.Vector3F:
        ...
    
    @axis_x.setter
    def axis_x(self, value : aspose.cad.Vector3F):
        ...
    
    @property
    def axis_y(self) -> aspose.cad.Vector3F:
        ...
    
    @axis_y.setter
    def axis_y(self, value : aspose.cad.Vector3F):
        ...
    
    @property
    def axis_z(self) -> aspose.cad.Vector3F:
        ...
    
    @axis_z.setter
    def axis_z(self, value : aspose.cad.Vector3F):
        ...
    
    @property
    def center(self) -> aspose.cad.Vector3F:
        ...
    
    @center.setter
    def center(self, value : aspose.cad.Vector3F):
        ...
    
    ...

class ThreeDSFace:
    
    @property
    def poly(self) -> aspose.cad.fileformats.threeds.elements.ThreeDSPoly:
        ...
    
    @poly.setter
    def poly(self, value : aspose.cad.fileformats.threeds.elements.ThreeDSPoly):
        ...
    
    @property
    def face_info(self) -> int:
        ...
    
    @face_info.setter
    def face_info(self, value : int):
        ...
    
    ...

class ThreeDSFaceMaterialGroup:
    
    @property
    def name(self) -> str:
        ...
    
    @property
    def has_faces(self) -> bool:
        ...
    
    @property
    def faces(self) -> List[int]:
        ...
    
    ...

class ThreeDSMaterial:
    
    @property
    def name(self) -> str:
        ...
    
    @name.setter
    def name(self, value : str):
        ...
    
    @property
    def ambient_color(self) -> aspose.cad.Vector3F:
        ...
    
    @ambient_color.setter
    def ambient_color(self, value : aspose.cad.Vector3F):
        ...
    
    @property
    def diffuse_color(self) -> aspose.cad.Vector3F:
        ...
    
    @diffuse_color.setter
    def diffuse_color(self, value : aspose.cad.Vector3F):
        ...
    
    @property
    def specular_color(self) -> aspose.cad.Vector3F:
        ...
    
    @specular_color.setter
    def specular_color(self, value : aspose.cad.Vector3F):
        ...
    
    @property
    def shininess_percent(self) -> int:
        ...
    
    @shininess_percent.setter
    def shininess_percent(self, value : int):
        ...
    
    @property
    def shininess_2_percent(self) -> int:
        ...
    
    @shininess_2_percent.setter
    def shininess_2_percent(self, value : int):
        ...
    
    @property
    def transparency_percent(self) -> int:
        ...
    
    @transparency_percent.setter
    def transparency_percent(self, value : int):
        ...
    
    @property
    def transparency_fallof_percent(self) -> int:
        ...
    
    @transparency_fallof_percent.setter
    def transparency_fallof_percent(self, value : int):
        ...
    
    @property
    def reflection_blur_percent(self) -> int:
        ...
    
    @reflection_blur_percent.setter
    def reflection_blur_percent(self, value : int):
        ...
    
    @property
    def shading(self) -> int:
        ...
    
    @shading.setter
    def shading(self, value : int):
        ...
    
    @property
    def texture(self) -> aspose.cad.fileformats.threeds.elements.ThreeDSTexture:
        ...
    
    @texture.setter
    def texture(self, value : aspose.cad.fileformats.threeds.elements.ThreeDSTexture):
        ...
    
    ...

class ThreeDSMesh:
    
    @property
    def name(self) -> str:
        ...
    
    @name.setter
    def name(self, value : str):
        ...
    
    @property
    def visible(self) -> bool:
        ...
    
    @visible.setter
    def visible(self, value : bool):
        ...
    
    @property
    def local_coordinate_system(self) -> aspose.cad.fileformats.threeds.elements.ThreeDSCoordinateSystem:
        ...
    
    @local_coordinate_system.setter
    def local_coordinate_system(self, value : aspose.cad.fileformats.threeds.elements.ThreeDSCoordinateSystem):
        ...
    
    @property
    def has_vertices(self) -> bool:
        ...
    
    @property
    def vertices(self) -> List[aspose.cad.Vector3F]:
        ...
    
    @property
    def has_faces(self) -> bool:
        ...
    
    @property
    def faces(self) -> List[aspose.cad.fileformats.threeds.elements.ThreeDSFace]:
        ...
    
    @property
    def has_face_material_groups(self) -> bool:
        ...
    
    @property
    def face_material_groups(self) -> List[aspose.cad.fileformats.threeds.elements.ThreeDSFaceMaterialGroup]:
        ...
    
    @property
    def has_mapping_coordinates(self) -> bool:
        ...
    
    @property
    def mapping_coordinates(self) -> List[aspose.cad.fileformats.threeds.elements.ThreeDSVectorUV]:
        ...
    
    ...

class ThreeDSPoly:
    
    @property
    def a(self) -> int:
        ...
    
    @a.setter
    def a(self, value : int):
        ...
    
    @property
    def b(self) -> int:
        ...
    
    @b.setter
    def b(self, value : int):
        ...
    
    @property
    def c(self) -> int:
        ...
    
    @c.setter
    def c(self, value : int):
        ...
    
    ...

class ThreeDSTexture:
    
    @property
    def percent(self) -> int:
        ...
    
    @percent.setter
    def percent(self, value : int):
        ...
    
    @property
    def file_name(self) -> str:
        ...
    
    @file_name.setter
    def file_name(self, value : str):
        ...
    
    @property
    def u_scale(self) -> float:
        ...
    
    @u_scale.setter
    def u_scale(self, value : float):
        ...
    
    @property
    def v_scale(self) -> float:
        ...
    
    @v_scale.setter
    def v_scale(self, value : float):
        ...
    
    @property
    def u_offset(self) -> float:
        ...
    
    @u_offset.setter
    def u_offset(self, value : float):
        ...
    
    @property
    def v_offset(self) -> float:
        ...
    
    @v_offset.setter
    def v_offset(self, value : float):
        ...
    
    @property
    def tiling(self) -> int:
        ...
    
    @tiling.setter
    def tiling(self, value : int):
        ...
    
    ...

class ThreeDSVectorUV:
    
    @property
    def u(self) -> float:
        ...
    
    @u.setter
    def u(self, value : float):
        ...
    
    @property
    def v(self) -> float:
        ...
    
    @v.setter
    def v(self, value : float):
        ...
    
    ...

