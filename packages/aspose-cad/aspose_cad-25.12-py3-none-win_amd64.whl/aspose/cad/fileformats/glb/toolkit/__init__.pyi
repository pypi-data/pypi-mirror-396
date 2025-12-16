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

class Toolkit:
    
    @overload
    @staticmethod
    def with_indices_accessor(primitive : aspose.cad.fileformats.glb.MeshPrimitive, primitive_type : aspose.cad.fileformats.glb.PrimitiveType, values : List[int]) -> aspose.cad.fileformats.glb.MeshPrimitive:
        ...
    
    @overload
    @staticmethod
    def with_indices_accessor(primitive : aspose.cad.fileformats.glb.MeshPrimitive, primitive_type : aspose.cad.fileformats.glb.PrimitiveType, mem_accessor : aspose.cad.fileformats.glb.memory.MemoryAccessor) -> aspose.cad.fileformats.glb.MeshPrimitive:
        ...
    
    @overload
    @staticmethod
    def with_vertex_accessor(primitive : aspose.cad.fileformats.glb.MeshPrimitive, attribute : str, values : List[float]) -> aspose.cad.fileformats.glb.MeshPrimitive:
        ...
    
    @overload
    @staticmethod
    def with_vertex_accessor(primitive : aspose.cad.fileformats.glb.MeshPrimitive, mem_accessor : aspose.cad.fileformats.glb.memory.MemoryAccessor) -> aspose.cad.fileformats.glb.MeshPrimitive:
        ...
    
    @overload
    @staticmethod
    def save_as_wavefront(model : aspose.cad.fileformats.glb.GlbData, file_path : str) -> None:
        ...
    
    @overload
    @staticmethod
    def save_as_wavefront(model : aspose.cad.fileformats.glb.GlbData, file_path : str, animation : aspose.cad.fileformats.glb.Animation, time : float) -> None:
        ...
    
    @overload
    @staticmethod
    def with_channel_texture(material : aspose.cad.fileformats.collada.fileparser.elements.Material, channel_name : str, texture_set : int, image_file_path : str) -> aspose.cad.fileformats.collada.fileparser.elements.Material:
        ...
    
    @overload
    @staticmethod
    def with_channel_texture(material : aspose.cad.fileformats.collada.fileparser.elements.Material, channel_name : str, texture_set : int, image : aspose.cad.fileformats.glb.ImageGlb) -> aspose.cad.fileformats.collada.fileparser.elements.Material:
        ...
    
    @overload
    @staticmethod
    def copy_to(src_material : aspose.cad.fileformats.collada.fileparser.elements.Material, dst_material : aspose.cad.fileformats.glb.materials.MaterialBuilder) -> None:
        ...
    
    @overload
    @staticmethod
    def copy_to(src_channel : aspose.cad.fileformats.glb.MaterialChannel, dst_channel : aspose.cad.fileformats.glb.materials.ChannelBuilder) -> None:
        ...
    
    @overload
    @staticmethod
    def copy_to(src_material : aspose.cad.fileformats.glb.materials.MaterialBuilder, dst_material : aspose.cad.fileformats.collada.fileparser.elements.Material) -> None:
        ...
    
    @overload
    @staticmethod
    def copy_to(src_channel : aspose.cad.fileformats.glb.materials.ChannelBuilder, dst_channel : aspose.cad.fileformats.glb.MaterialChannel) -> None:
        ...
    
    @overload
    @staticmethod
    def copy_channels_to(src_material : aspose.cad.fileformats.collada.fileparser.elements.Material, dst_material : aspose.cad.fileformats.glb.materials.MaterialBuilder, channel_keys : List[str]) -> None:
        ...
    
    @overload
    @staticmethod
    def copy_channels_to(src_material : aspose.cad.fileformats.glb.materials.MaterialBuilder, dst_material : aspose.cad.fileformats.collada.fileparser.elements.Material, channel_keys : List[str]) -> None:
        ...
    
    @staticmethod
    def with_local_transform(node : aspose.cad.fileformats.collada.fileparser.elements.Node, xform : aspose.cad.fileformats.glb.transforms.AffineTransform) -> aspose.cad.fileformats.collada.fileparser.elements.Node:
        ...
    
    @staticmethod
    def with_mesh(node : aspose.cad.fileformats.collada.fileparser.elements.Node, mesh : aspose.cad.fileformats.collada.fileparser.elements.Mesh) -> aspose.cad.fileformats.collada.fileparser.elements.Node:
        ...
    
    @staticmethod
    def with_skin(node : aspose.cad.fileformats.collada.fileparser.elements.Node, skin : aspose.cad.fileformats.glb.Skin) -> aspose.cad.fileformats.collada.fileparser.elements.Node:
        ...
    
    @staticmethod
    def with_perspective_camera(node : aspose.cad.fileformats.collada.fileparser.elements.Node, aspect_ratio : Optional[float], fovy : float, znear : float, zfar : float) -> aspose.cad.fileformats.collada.fileparser.elements.Node:
        ...
    
    @staticmethod
    def with_orthographic_camera(node : aspose.cad.fileformats.collada.fileparser.elements.Node, xmag : float, ymag : float, znear : float, zfar : float) -> aspose.cad.fileformats.collada.fileparser.elements.Node:
        ...
    
    @staticmethod
    def to_scene_builder(src_scene : aspose.cad.fileformats.collada.fileparser.elements.Scene) -> aspose.cad.fileformats.glb.scenes.SceneBuilder:
        ...
    
    @staticmethod
    def with_indices_automatic(primitive : aspose.cad.fileformats.glb.MeshPrimitive, primitive_type : aspose.cad.fileformats.glb.PrimitiveType) -> aspose.cad.fileformats.glb.MeshPrimitive:
        ...
    
    @staticmethod
    def with_vertex_accessors(primitive : aspose.cad.fileformats.glb.MeshPrimitive, mem_accessors : Iterable[aspose.cad.fileformats.glb.memory.MemoryAccessor]) -> aspose.cad.fileformats.glb.MeshPrimitive:
        ...
    
    @staticmethod
    def with_morph_target_accessors(primitive : aspose.cad.fileformats.glb.MeshPrimitive, target_index : int, mem_accessors : Iterable[aspose.cad.fileformats.glb.memory.MemoryAccessor]) -> aspose.cad.fileformats.glb.MeshPrimitive:
        ...
    
    @staticmethod
    def with_instance_accessors(instancing : aspose.cad.fileformats.glb.MeshGpuInstancing, transforms : List[aspose.cad.fileformats.glb.transforms.AffineTransform]) -> aspose.cad.fileformats.glb.MeshGpuInstancing:
        ...
    
    @staticmethod
    def with_instance_custom_accessors(instancing : aspose.cad.fileformats.glb.MeshGpuInstancing, extras : List[aspose.cad.fileformats.glb.io.JsonContent]) -> aspose.cad.fileformats.glb.MeshGpuInstancing:
        ...
    
    @staticmethod
    def with_instance_custom_accessor(instancing : aspose.cad.fileformats.glb.MeshGpuInstancing, attribute : str, values : List[any]) -> aspose.cad.fileformats.glb.MeshGpuInstancing:
        ...
    
    @staticmethod
    def with_material(primitive : aspose.cad.fileformats.glb.MeshPrimitive, material : aspose.cad.fileformats.collada.fileparser.elements.Material) -> aspose.cad.fileformats.glb.MeshPrimitive:
        ...
    
    @staticmethod
    def with_default(material : aspose.cad.fileformats.collada.fileparser.elements.Material) -> aspose.cad.fileformats.collada.fileparser.elements.Material:
        ...
    
    @staticmethod
    def with_double_side(material : aspose.cad.fileformats.collada.fileparser.elements.Material, enabled : bool) -> aspose.cad.fileformats.collada.fileparser.elements.Material:
        ...
    
    @staticmethod
    def with_channel_factor(material : aspose.cad.fileformats.collada.fileparser.elements.Material, channel_name : str, param_name : str, factor : float) -> aspose.cad.fileformats.collada.fileparser.elements.Material:
        ...
    
    @staticmethod
    def with_pbr_metallic_roughness(material : aspose.cad.fileformats.collada.fileparser.elements.Material) -> aspose.cad.fileformats.collada.fileparser.elements.Material:
        ...
    
    @staticmethod
    def with_pbr_specular_glossiness(material : aspose.cad.fileformats.collada.fileparser.elements.Material) -> aspose.cad.fileformats.collada.fileparser.elements.Material:
        ...
    
    @staticmethod
    def with_unlit(material : aspose.cad.fileformats.collada.fileparser.elements.Material) -> aspose.cad.fileformats.collada.fileparser.elements.Material:
        ...
    
    @staticmethod
    def use_image_with_file(root : aspose.cad.fileformats.glb.GlbData, file_path : str) -> aspose.cad.fileformats.glb.ImageGlb:
        '''Creates or reuses an :py:class:`aspose.cad.fileformats.glb.GlbImage` with the file set by ``filePath``
        
        :param root: The :py:class:`aspose.cad.fileformats.glb.GlbImage` root instance.
        :param file_path: A valid file path pointing to a valid image
        :returns: A :py:class:`aspose.cad.fileformats.glb.GlbImage` instance.'''
        ...
    
    @staticmethod
    def use_image_with_content(root : aspose.cad.fileformats.glb.GlbData, image : aspose.cad.fileformats.glb.memory.MemoryImage) -> aspose.cad.fileformats.glb.ImageGlb:
        '''Creates or reuses an :py:class:`aspose.cad.fileformats.glb.GlbImage` with the image content set by ``image``
        
        :param root: The :py:class:`aspose.cad.fileformats.glb.GlbImage` root instance.
        :param image: A buffer containing the bytes of the image file.
        :returns: A :py:class:`aspose.cad.fileformats.glb.GlbImage` instance.'''
        ...
    
    @staticmethod
    def create_material(root : aspose.cad.fileformats.glb.GlbData, mb : aspose.cad.fileformats.glb.materials.MaterialBuilder) -> aspose.cad.fileformats.collada.fileparser.elements.Material:
        ...
    
    @staticmethod
    def to_material_builder(src_material : aspose.cad.fileformats.collada.fileparser.elements.Material) -> aspose.cad.fileformats.glb.materials.MaterialBuilder:
        ...
    
    @staticmethod
    def to_schema2(alpha : aspose.cad.fileformats.glb.materials.AlphaMode) -> aspose.cad.fileformats.glb.AlphaMode:
        ...
    
    @staticmethod
    def to_toolkit(alpha : aspose.cad.fileformats.glb.AlphaMode) -> aspose.cad.fileformats.glb.materials.AlphaMode:
        ...
    
    @staticmethod
    def get_diffuse_texture(material : aspose.cad.fileformats.collada.fileparser.elements.Material) -> aspose.cad.fileformats.glb.Texture:
        ...
    
    @staticmethod
    def get_diffuse_texture_transform(material : aspose.cad.fileformats.collada.fileparser.elements.Material) -> aspose.cad.fileformats.glb.TextureTransform:
        ...
    
    @staticmethod
    def with_spot_cone(light : aspose.cad.fileformats.glb.PunctualLight, inner_cone_angle : float, outer_cone_angle : float) -> aspose.cad.fileformats.glb.PunctualLight:
        '''Sets the cone angles for the :py:attr:`aspose.cad.fileformats.glb.PunctualLightType.SPOT` light.
        
        :param light: This :py:class:`aspose.cad.fileformats.glb.PunctualLight` instance.
        :param inner_cone_angle: Gets the Angle, in radians, from centre of spotlight where falloff begins.
        Must be greater than or equal to 0 and less than outerConeAngle.
        :param outer_cone_angle: Gets Angle, in radians, from centre of spotlight where falloff ends.
        Must be greater than innerConeAngle and less than or equal to PI / 2.0.
        :returns: This :py:class:`aspose.cad.fileformats.glb.PunctualLight` instance.'''
        ...
    
    @staticmethod
    def use_animation(root : aspose.cad.fileformats.glb.GlbData, name : str) -> aspose.cad.fileformats.glb.Animation:
        ...
    
    @staticmethod
    def create_vertex_accessor(root : aspose.cad.fileformats.glb.GlbData, mem_accessor : aspose.cad.fileformats.glb.memory.MemoryAccessor) -> aspose.cad.fileformats.collada.fileparser.elements.Accessor:
        ...
    
    ...

