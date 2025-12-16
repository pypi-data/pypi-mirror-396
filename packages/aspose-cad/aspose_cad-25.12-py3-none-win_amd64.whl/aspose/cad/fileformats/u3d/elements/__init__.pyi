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

class U3dAuthorFace:
    '''The face of the author (progressive) mesh.'''
    
    def indexer_get(self, index : int) -> int:
        ...
    
    def indexer_set(self, index : int, value : int) -> None:
        ...
    
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
    
    def __getitem__(self, key : int) -> int:
        ...
    
    def __setitem__(self, key : int, value : int):
        ...
    
    ...

class U3dAuthorLineSet(U3dModel):
    
    @property
    def positions(self) -> List[aspose.cad.Vector3F]:
        ...
    
    @positions.setter
    def positions(self, value : List[aspose.cad.Vector3F]):
        ...
    
    @property
    def position_lines(self) -> List[aspose.cad.fileformats.u3d.elements.U3dLine]:
        ...
    
    @position_lines.setter
    def position_lines(self, value : List[aspose.cad.fileformats.u3d.elements.U3dLine]):
        ...
    
    ...

class U3dAuthorLineSetDescription:
    '''The author (progressive) line set description.'''
    
    def copy(self) -> aspose.cad.fileformats.u3d.elements.U3dAuthorLineSetDescription:
        ...
    
    @property
    def shaders(self) -> List[aspose.cad.fileformats.u3d.elements.U3dAuthorMaterial]:
        ...
    
    @shaders.setter
    def shaders(self, value : List[aspose.cad.fileformats.u3d.elements.U3dAuthorMaterial]):
        ...
    
    @property
    def num_lines(self) -> int:
        ...
    
    @num_lines.setter
    def num_lines(self, value : int):
        ...
    
    @property
    def num_positions(self) -> int:
        ...
    
    @num_positions.setter
    def num_positions(self, value : int):
        ...
    
    @property
    def num_normals(self) -> int:
        ...
    
    @num_normals.setter
    def num_normals(self, value : int):
        ...
    
    @property
    def num_diffuse_colors(self) -> int:
        ...
    
    @num_diffuse_colors.setter
    def num_diffuse_colors(self, value : int):
        ...
    
    @property
    def num_specular_colors(self) -> int:
        ...
    
    @num_specular_colors.setter
    def num_specular_colors(self, value : int):
        ...
    
    @property
    def num_tex_coords(self) -> int:
        ...
    
    @num_tex_coords.setter
    def num_tex_coords(self, value : int):
        ...
    
    @property
    def num_materials(self) -> int:
        ...
    
    @num_materials.setter
    def num_materials(self, value : int):
        ...
    
    @property
    def inverse_quant_position(self) -> float:
        ...
    
    @inverse_quant_position.setter
    def inverse_quant_position(self, value : float):
        ...
    
    @property
    def inverse_quant_normal(self) -> float:
        ...
    
    @inverse_quant_normal.setter
    def inverse_quant_normal(self, value : float):
        ...
    
    @property
    def inverse_quant_tex_coord(self) -> float:
        ...
    
    @inverse_quant_tex_coord.setter
    def inverse_quant_tex_coord(self, value : float):
        ...
    
    @property
    def inverse_quant_diffuse_color(self) -> float:
        ...
    
    @inverse_quant_diffuse_color.setter
    def inverse_quant_diffuse_color(self, value : float):
        ...
    
    @property
    def inverse_quant_specular_color(self) -> float:
        ...
    
    @inverse_quant_specular_color.setter
    def inverse_quant_specular_color(self, value : float):
        ...
    
    ...

class U3dAuthorMaterial:
    
    @property
    def material_attributes(self) -> int:
        ...
    
    @material_attributes.setter
    def material_attributes(self, value : int):
        ...
    
    @property
    def num_texture_layers(self) -> int:
        ...
    
    @num_texture_layers.setter
    def num_texture_layers(self, value : int):
        ...
    
    @property
    def original_shading_id(self) -> int:
        ...
    
    @original_shading_id.setter
    def original_shading_id(self, value : int):
        ...
    
    @property
    def has_diffuse_colors(self) -> bool:
        ...
    
    @has_diffuse_colors.setter
    def has_diffuse_colors(self, value : bool):
        ...
    
    @property
    def has_specular_colors(self) -> bool:
        ...
    
    @has_specular_colors.setter
    def has_specular_colors(self, value : bool):
        ...
    
    @property
    def tex_coord_dimensions(self) -> List[int]:
        ...
    
    @tex_coord_dimensions.setter
    def tex_coord_dimensions(self, value : List[int]):
        ...
    
    @property
    def has_normals(self) -> bool:
        ...
    
    @has_normals.setter
    def has_normals(self, value : bool):
        ...
    
    ...

class U3dAuthorMesh(U3dModel):
    
    ...

class U3dAuthorMeshDescription:
    '''The author (progressive) mesh description.'''
    
    @property
    def shaders(self) -> List[aspose.cad.fileformats.u3d.elements.U3dAuthorMaterial]:
        ...
    
    @shaders.setter
    def shaders(self, value : List[aspose.cad.fileformats.u3d.elements.U3dAuthorMaterial]):
        ...
    
    @property
    def num_faces(self) -> int:
        ...
    
    @num_faces.setter
    def num_faces(self, value : int):
        ...
    
    @property
    def num_positions(self) -> int:
        ...
    
    @num_positions.setter
    def num_positions(self, value : int):
        ...
    
    @property
    def num_normals(self) -> int:
        ...
    
    @num_normals.setter
    def num_normals(self, value : int):
        ...
    
    @property
    def num_diffuse_colors(self) -> int:
        ...
    
    @num_diffuse_colors.setter
    def num_diffuse_colors(self, value : int):
        ...
    
    @property
    def num_specular_colors(self) -> int:
        ...
    
    @num_specular_colors.setter
    def num_specular_colors(self, value : int):
        ...
    
    @property
    def num_tex_coords(self) -> int:
        ...
    
    @num_tex_coords.setter
    def num_tex_coords(self, value : int):
        ...
    
    @property
    def num_materials(self) -> int:
        ...
    
    @num_materials.setter
    def num_materials(self, value : int):
        ...
    
    @property
    def num_base_vertices(self) -> int:
        ...
    
    @num_base_vertices.setter
    def num_base_vertices(self, value : int):
        ...
    
    @property
    def exclude_normals(self) -> bool:
        ...
    
    @exclude_normals.setter
    def exclude_normals(self, value : bool):
        ...
    
    @property
    def inverse_quant_position(self) -> float:
        ...
    
    @inverse_quant_position.setter
    def inverse_quant_position(self, value : float):
        ...
    
    @property
    def inverse_quant_normal(self) -> float:
        ...
    
    @inverse_quant_normal.setter
    def inverse_quant_normal(self, value : float):
        ...
    
    @property
    def inverse_quant_tex_coord(self) -> float:
        ...
    
    @inverse_quant_tex_coord.setter
    def inverse_quant_tex_coord(self, value : float):
        ...
    
    @property
    def inverse_quant_diffuse_color(self) -> float:
        ...
    
    @inverse_quant_diffuse_color.setter
    def inverse_quant_diffuse_color(self, value : float):
        ...
    
    @property
    def inverse_quant_specular_color(self) -> float:
        ...
    
    @inverse_quant_specular_color.setter
    def inverse_quant_specular_color(self, value : float):
        ...
    
    ...

class U3dAuthorVertexUpdate:
    '''The structure containing information on how vertex data is added to or
    removed from a mesh during mesh resolution changes.'''
    
    @property
    def num_new_faces(self) -> int:
        ...
    
    @num_new_faces.setter
    def num_new_faces(self, value : int):
        ...
    
    @property
    def num_new_normals(self) -> int:
        ...
    
    @num_new_normals.setter
    def num_new_normals(self, value : int):
        ...
    
    @property
    def num_new_diffuse_colors(self) -> int:
        ...
    
    @num_new_diffuse_colors.setter
    def num_new_diffuse_colors(self, value : int):
        ...
    
    @property
    def num_new_specular_colors(self) -> int:
        ...
    
    @num_new_specular_colors.setter
    def num_new_specular_colors(self, value : int):
        ...
    
    @property
    def num_new_tex_coords(self) -> int:
        ...
    
    @num_new_tex_coords.setter
    def num_new_tex_coords(self, value : int):
        ...
    
    @property
    def num_face_updates(self) -> int:
        ...
    
    @num_face_updates.setter
    def num_face_updates(self, value : int):
        ...
    
    ...

class U3dBaseMesh(U3dModel):
    
    ...

class U3dFace:
    
    @property
    def shading_id(self) -> int:
        ...
    
    @shading_id.setter
    def shading_id(self, value : int):
        ...
    
    @property
    def positions(self) -> aspose.cad.fileformats.u3d.elements.U3dPoly:
        ...
    
    @positions.setter
    def positions(self, value : aspose.cad.fileformats.u3d.elements.U3dPoly):
        ...
    
    @property
    def normals(self) -> aspose.cad.fileformats.u3d.elements.U3dPoly:
        ...
    
    @normals.setter
    def normals(self, value : aspose.cad.fileformats.u3d.elements.U3dPoly):
        ...
    
    @property
    def diffuse_colors(self) -> aspose.cad.fileformats.u3d.elements.U3dPoly:
        ...
    
    @diffuse_colors.setter
    def diffuse_colors(self, value : aspose.cad.fileformats.u3d.elements.U3dPoly):
        ...
    
    @property
    def specular_colors(self) -> aspose.cad.fileformats.u3d.elements.U3dPoly:
        ...
    
    @specular_colors.setter
    def specular_colors(self, value : aspose.cad.fileformats.u3d.elements.U3dPoly):
        ...
    
    @property
    def tex_coords(self) -> aspose.cad.fileformats.u3d.elements.U3dPoly:
        ...
    
    @tex_coords.setter
    def tex_coords(self, value : aspose.cad.fileformats.u3d.elements.U3dPoly):
        ...
    
    ...

class U3dLine:
    
    def indexer_get(self, index : int) -> int:
        ...
    
    def indexer_set(self, index : int, value : int) -> None:
        ...
    
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
    
    def __getitem__(self, key : int) -> int:
        ...
    
    def __setitem__(self, key : int, value : int):
        ...
    
    ...

class U3dMatrix4x4F:
    
    ...

class U3dModel:
    '''Abstract U3D Model.'''
    
    ...

class U3dPoly:
    
    def indexer_get(self, index : int) -> int:
        ...
    
    def indexer_set(self, index : int, value : int) -> None:
        ...
    
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
    
    def __getitem__(self, key : int) -> int:
        ...
    
    def __setitem__(self, key : int, value : int):
        ...
    
    ...

