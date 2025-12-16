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

class ChannelBuilder:
    '''Represents a material channel at :py:class:`aspose.cad.fileformats.glb.materials.MaterialBuilder`.'''
    
    @staticmethod
    def are_equal_by_content(x : aspose.cad.fileformats.glb.materials.ChannelBuilder, y : aspose.cad.fileformats.glb.materials.ChannelBuilder) -> bool:
        ...
    
    @staticmethod
    def get_content_hash_code(x : aspose.cad.fileformats.glb.materials.ChannelBuilder) -> int:
        ...
    
    def get_valid_texture(self) -> aspose.cad.fileformats.glb.materials.TextureBuilder:
        ...
    
    def use_texture(self) -> aspose.cad.fileformats.glb.materials.TextureBuilder:
        ...
    
    def remove_texture(self) -> None:
        ...
    
    @property
    def texture(self) -> aspose.cad.fileformats.glb.materials.TextureBuilder:
        ...
    
    @property
    def key(self) -> aspose.cad.fileformats.glb.materials.KnownChannel:
        '''Gets the :py:class:`aspose.cad.fileformats.glb.materials.ChannelBuilder` name. It must be a name of :py:class:`aspose.cad.fileformats.glb.materials.KnownChannel`.'''
        ...
    
    @property
    def parameters(self) -> MaterialValue.Collection:
        '''Gets the collection of parameters of this channel'''
        ...
    
    ...

class ImageBuilder(aspose.cad.fileformats.glb.geometry.BaseBuilder):
    '''Represents an image that can be used at :py:attr:`aspose.cad.fileformats.glb.materials.TextureBuilder.primary_image` and :py:attr:`aspose.cad.fileformats.glb.materials.TextureBuilder.fallback_image`.'''
    
    @overload
    @staticmethod
    def from_address(content : aspose.cad.fileformats.glb.memory.MemoryImage, name : str) -> aspose.cad.fileformats.glb.materials.ImageBuilder:
        ...
    
    @overload
    @staticmethod
    def from_address(content : aspose.cad.fileformats.glb.memory.MemoryImage, name : str, extras : aspose.cad.fileformats.glb.io.JsonContent) -> aspose.cad.fileformats.glb.materials.ImageBuilder:
        ...
    
    @staticmethod
    def are_equal_by_content(x : aspose.cad.fileformats.glb.materials.ImageBuilder, y : aspose.cad.fileformats.glb.materials.ImageBuilder) -> bool:
        ...
    
    @staticmethod
    def get_content_hash_code(x : aspose.cad.fileformats.glb.materials.ImageBuilder) -> int:
        ...
    
    @staticmethod
    def is_empty(ib : aspose.cad.fileformats.glb.materials.ImageBuilder) -> bool:
        ...
    
    @staticmethod
    def is_valid(ib : aspose.cad.fileformats.glb.materials.ImageBuilder) -> bool:
        ...
    
    @property
    def name(self) -> str:
        '''Gets the display text name, or null.
        
        **⚠️ DO NOT USE AS AN OBJECT ID ⚠️** see remarks.'''
        ...
    
    @name.setter
    def name(self, value : str):
        '''Sets the display text name, or null.
        
        **⚠️ DO NOT USE AS AN OBJECT ID ⚠️** see remarks.'''
        ...
    
    @property
    def extras(self) -> aspose.cad.fileformats.glb.io.JsonContent:
        '''Gets the custom data of this object.'''
        ...
    
    @extras.setter
    def extras(self, value : aspose.cad.fileformats.glb.io.JsonContent):
        '''Sets the custom data of this object.'''
        ...
    
    @property
    def content(self) -> aspose.cad.fileformats.glb.memory.MemoryImage:
        '''Gets the in-memory representation of the image file.'''
        ...
    
    @content.setter
    def content(self, value : aspose.cad.fileformats.glb.memory.MemoryImage):
        '''Sets the in-memory representation of the image file.'''
        ...
    
    @property
    def alternate_write_file_name(self) -> str:
        ...
    
    @alternate_write_file_name.setter
    def alternate_write_file_name(self, value : str):
        ...
    
    ...

class MaterialBuilder(aspose.cad.fileformats.glb.geometry.BaseBuilder):
    '''Represents the root object of a material instance structure.'''
    
    @overload
    def get_channel(self, channel_key : aspose.cad.fileformats.glb.materials.KnownChannel) -> aspose.cad.fileformats.glb.materials.ChannelBuilder:
        ...
    
    @overload
    def get_channel(self, channel_key : str) -> aspose.cad.fileformats.glb.materials.ChannelBuilder:
        ...
    
    @overload
    def use_channel(self, channel_key : aspose.cad.fileformats.glb.materials.KnownChannel) -> aspose.cad.fileformats.glb.materials.ChannelBuilder:
        ...
    
    @overload
    def use_channel(self, channel_key : str) -> aspose.cad.fileformats.glb.materials.ChannelBuilder:
        ...
    
    @overload
    def with_channel_image(self, channel_key : aspose.cad.fileformats.glb.materials.KnownChannel, primary_image : aspose.cad.fileformats.glb.materials.ImageBuilder) -> aspose.cad.fileformats.glb.materials.MaterialBuilder:
        ...
    
    @overload
    def with_channel_image(self, channel_key : str, primary_image : aspose.cad.fileformats.glb.materials.ImageBuilder) -> aspose.cad.fileformats.glb.materials.MaterialBuilder:
        ...
    
    @overload
    def with_metallic_roughness(self, metallic : Optional[float], roughness : Optional[float]) -> aspose.cad.fileformats.glb.materials.MaterialBuilder:
        ...
    
    @overload
    def with_metallic_roughness(self, image_file : aspose.cad.fileformats.glb.materials.ImageBuilder, metallic : Optional[float], roughness : Optional[float]) -> aspose.cad.fileformats.glb.materials.MaterialBuilder:
        ...
    
    @staticmethod
    def create_default() -> aspose.cad.fileformats.glb.materials.MaterialBuilder:
        ...
    
    def clone(self) -> aspose.cad.fileformats.glb.materials.MaterialBuilder:
        ...
    
    @staticmethod
    def are_equal_by_content(x : aspose.cad.fileformats.glb.materials.MaterialBuilder, y : aspose.cad.fileformats.glb.materials.MaterialBuilder) -> bool:
        ...
    
    @staticmethod
    def get_content_hash_code(x : aspose.cad.fileformats.glb.materials.MaterialBuilder) -> int:
        ...
    
    def remove_channel(self, key : aspose.cad.fileformats.glb.materials.KnownChannel) -> None:
        ...
    
    def with_shader(self, shader : str) -> aspose.cad.fileformats.glb.materials.MaterialBuilder:
        '''Sets :py:attr:`aspose.cad.fileformats.glb.materials.MaterialBuilder.shader_style`.
        
        :param shader: A valid shader style, which can be one of these values:
        :py:attr:`aspose.cad.fileformats.glb.materials.MaterialBuilder.SHADERUNLIT`,
        :py:attr:`aspose.cad.fileformats.glb.materials.MaterialBuilder.SHADERPBRMETALLICROUGHNESS`,
        :py:attr:`aspose.cad.fileformats.glb.materials.MaterialBuilder.SHADERPBRSPECULARGLOSSINESS`
        :returns: This :py:class:`aspose.cad.fileformats.glb.materials.MaterialBuilder`.'''
        ...
    
    def with_unlit_shader(self) -> aspose.cad.fileformats.glb.materials.MaterialBuilder:
        '''Sets :py:attr:`aspose.cad.fileformats.glb.materials.MaterialBuilder.shader_style` to use :py:attr:`aspose.cad.fileformats.glb.materials.MaterialBuilder.SHADERUNLIT`.
        
        :returns: This :py:class:`aspose.cad.fileformats.glb.materials.MaterialBuilder`.'''
        ...
    
    def with_metallic_roughness_shader(self) -> aspose.cad.fileformats.glb.materials.MaterialBuilder:
        '''Sets :py:attr:`aspose.cad.fileformats.glb.materials.MaterialBuilder.shader_style` to use :py:attr:`aspose.cad.fileformats.glb.materials.MaterialBuilder.SHADERPBRMETALLICROUGHNESS`.
        
        :returns: This :py:class:`aspose.cad.fileformats.glb.materials.MaterialBuilder`.'''
        ...
    
    def with_specular_glossiness_shader(self) -> aspose.cad.fileformats.glb.materials.MaterialBuilder:
        '''Sets :py:attr:`aspose.cad.fileformats.glb.materials.MaterialBuilder.shader_style` to use :py:attr:`aspose.cad.fileformats.glb.materials.MaterialBuilder.SHADERPBRSPECULARGLOSSINESS`.
        
        :returns: This :py:class:`aspose.cad.fileformats.glb.materials.MaterialBuilder`.'''
        ...
    
    def with_alpha(self, alpha_mode : aspose.cad.fileformats.glb.AlphaMode, alpha_cutoff : float) -> aspose.cad.fileformats.glb.materials.MaterialBuilder:
        ...
    
    def with_double_side(self, enabled : bool) -> aspose.cad.fileformats.glb.materials.MaterialBuilder:
        ...
    
    def with_channel_param(self, channel_key : aspose.cad.fileformats.glb.materials.KnownChannel, property_name : aspose.cad.fileformats.glb.materials.KnownProperty, parameter : any) -> aspose.cad.fileformats.glb.materials.MaterialBuilder:
        ...
    
    def with_fallback(self, fallback : aspose.cad.fileformats.glb.materials.MaterialBuilder) -> aspose.cad.fileformats.glb.materials.MaterialBuilder:
        '''Defines a fallback :py:class:`aspose.cad.fileformats.glb.materials.MaterialBuilder` instance for the current :py:class:`aspose.cad.fileformats.glb.materials.MaterialBuilder`.
        
        :param fallback: A :py:class:`aspose.cad.fileformats.glb.materials.MaterialBuilder` instance
        that must have a :py:attr:`aspose.cad.fileformats.glb.materials.MaterialBuilder.shader_style`
        of type :py:attr:`aspose.cad.fileformats.glb.materials.MaterialBuilder.SHADERPBRMETALLICROUGHNESS`
        :returns: This :py:class:`aspose.cad.fileformats.glb.materials.MaterialBuilder`.'''
        ...
    
    def with_normal(self, image_file : aspose.cad.fileformats.glb.materials.ImageBuilder, scale : float) -> aspose.cad.fileformats.glb.materials.MaterialBuilder:
        ...
    
    def with_occlusion(self, image_file : aspose.cad.fileformats.glb.materials.ImageBuilder, strength : float) -> aspose.cad.fileformats.glb.materials.MaterialBuilder:
        ...
    
    def with_clear_coat_normal(self, image_file : aspose.cad.fileformats.glb.materials.ImageBuilder) -> aspose.cad.fileformats.glb.materials.MaterialBuilder:
        ...
    
    def with_clear_coat(self, image_file : aspose.cad.fileformats.glb.materials.ImageBuilder, intensity : float) -> aspose.cad.fileformats.glb.materials.MaterialBuilder:
        ...
    
    def with_clear_coat_roughness(self, image_file : aspose.cad.fileformats.glb.materials.ImageBuilder, roughness : float) -> aspose.cad.fileformats.glb.materials.MaterialBuilder:
        ...
    
    def with_transmission(self, image_file : aspose.cad.fileformats.glb.materials.ImageBuilder, intensity : float) -> aspose.cad.fileformats.glb.materials.MaterialBuilder:
        ...
    
    def with_specular_factor(self, image_file : aspose.cad.fileformats.glb.materials.ImageBuilder, factor : float) -> aspose.cad.fileformats.glb.materials.MaterialBuilder:
        ...
    
    def with_volume_thickness(self, image_file : aspose.cad.fileformats.glb.materials.ImageBuilder, factor : float) -> aspose.cad.fileformats.glb.materials.MaterialBuilder:
        ...
    
    def with_iridiscence(self, image_file : aspose.cad.fileformats.glb.materials.ImageBuilder, factor : float, ior : float) -> aspose.cad.fileformats.glb.materials.MaterialBuilder:
        ...
    
    def with_iridiscence_thickness(self, image_file : aspose.cad.fileformats.glb.materials.ImageBuilder, min : float, max : float) -> aspose.cad.fileformats.glb.materials.MaterialBuilder:
        ...
    
    @property
    def name(self) -> str:
        '''Gets the display text name, or null.
        
        **⚠️ DO NOT USE AS AN OBJECT ID ⚠️** see remarks.'''
        ...
    
    @name.setter
    def name(self, value : str):
        '''Sets the display text name, or null.
        
        **⚠️ DO NOT USE AS AN OBJECT ID ⚠️** see remarks.'''
        ...
    
    @property
    def extras(self) -> aspose.cad.fileformats.glb.io.JsonContent:
        '''Gets the custom data of this object.'''
        ...
    
    @extras.setter
    def extras(self, value : aspose.cad.fileformats.glb.io.JsonContent):
        '''Sets the custom data of this object.'''
        ...
    
    @property
    def alpha_mode(self) -> aspose.cad.fileformats.glb.AlphaMode:
        ...
    
    @alpha_mode.setter
    def alpha_mode(self, value : aspose.cad.fileformats.glb.AlphaMode):
        ...
    
    @property
    def alpha_cutoff(self) -> float:
        ...
    
    @alpha_cutoff.setter
    def alpha_cutoff(self, value : float):
        ...
    
    @property
    def double_sided(self) -> bool:
        ...
    
    @double_sided.setter
    def double_sided(self, value : bool):
        ...
    
    @property
    def shader_style(self) -> str:
        ...
    
    @shader_style.setter
    def shader_style(self, value : str):
        ...
    
    @property
    def index_of_refraction(self) -> float:
        ...
    
    @index_of_refraction.setter
    def index_of_refraction(self, value : float):
        ...
    
    @property
    def channels(self) -> List[aspose.cad.fileformats.glb.materials.ChannelBuilder]:
        ...
    
    @property
    def compatibility_fallback(self) -> aspose.cad.fileformats.glb.materials.MaterialBuilder:
        ...
    
    @compatibility_fallback.setter
    def compatibility_fallback(self, value : aspose.cad.fileformats.glb.materials.MaterialBuilder):
        ...
    
    @classmethod
    @property
    def SHADERUNLIT(cls) -> str:
        ...
    
    @classmethod
    @property
    def SHADERPBRMETALLICROUGHNESS(cls) -> str:
        ...
    
    @classmethod
    @property
    def SHADERPBRSPECULARGLOSSINESS(cls) -> str:
        ...
    
    ...

class MaterialValue:
    
    @staticmethod
    def create_from(value : any) -> aspose.cad.fileformats.glb.materials.MaterialValue:
        ...
    
    def equals(self, other : aspose.cad.fileformats.glb.materials.MaterialValue) -> bool:
        ...
    
    @staticmethod
    def are_equal(a : Any, b : Any) -> bool:
        ...
    
    def to_typeless(self) -> any:
        ...
    
    @property
    def value_type(self) -> Type:
        ...
    
    ...

class TextureBuilder(aspose.cad.fileformats.glb.geometry.BaseBuilder):
    '''Represents the texture used by a :py:class:`aspose.cad.fileformats.glb.materials.ChannelBuilder`'''
    
    @staticmethod
    def are_equal_by_content(x : aspose.cad.fileformats.glb.materials.TextureBuilder, y : aspose.cad.fileformats.glb.materials.TextureBuilder) -> bool:
        ...
    
    @staticmethod
    def get_content_hash_code(x : aspose.cad.fileformats.glb.materials.TextureBuilder) -> int:
        ...
    
    def with_coordinate_set(self, cset : int) -> aspose.cad.fileformats.glb.materials.TextureBuilder:
        ...
    
    def with_primary_image(self, image : aspose.cad.fileformats.glb.materials.ImageBuilder) -> aspose.cad.fileformats.glb.materials.TextureBuilder:
        ...
    
    def with_fallback_image(self, image : aspose.cad.fileformats.glb.materials.ImageBuilder) -> aspose.cad.fileformats.glb.materials.TextureBuilder:
        ...
    
    def with_sampler(self, ws : aspose.cad.fileformats.glb.TextureWrapMode, wt : aspose.cad.fileformats.glb.TextureWrapMode, min : aspose.cad.fileformats.glb.TextureMipMapFilter, mag : aspose.cad.fileformats.glb.TextureInterpolationFilter) -> aspose.cad.fileformats.glb.materials.TextureBuilder:
        ...
    
    def with_transform(self, offset_x : float, offset_y : float, scale_x : float, scale_y : float, rotation : float, coord_set_override : Optional[int]) -> aspose.cad.fileformats.glb.materials.TextureBuilder:
        ...
    
    @property
    def name(self) -> str:
        '''Gets the display text name, or null.
        
        **⚠️ DO NOT USE AS AN OBJECT ID ⚠️** see remarks.'''
        ...
    
    @name.setter
    def name(self, value : str):
        '''Sets the display text name, or null.
        
        **⚠️ DO NOT USE AS AN OBJECT ID ⚠️** see remarks.'''
        ...
    
    @property
    def extras(self) -> aspose.cad.fileformats.glb.io.JsonContent:
        '''Gets the custom data of this object.'''
        ...
    
    @extras.setter
    def extras(self, value : aspose.cad.fileformats.glb.io.JsonContent):
        '''Sets the custom data of this object.'''
        ...
    
    @property
    def coordinate_set(self) -> int:
        ...
    
    @coordinate_set.setter
    def coordinate_set(self, value : int):
        ...
    
    @property
    def min_filter(self) -> aspose.cad.fileformats.glb.TextureMipMapFilter:
        ...
    
    @min_filter.setter
    def min_filter(self, value : aspose.cad.fileformats.glb.TextureMipMapFilter):
        ...
    
    @property
    def mag_filter(self) -> aspose.cad.fileformats.glb.TextureInterpolationFilter:
        ...
    
    @mag_filter.setter
    def mag_filter(self, value : aspose.cad.fileformats.glb.TextureInterpolationFilter):
        ...
    
    @property
    def wrap_s(self) -> aspose.cad.fileformats.glb.TextureWrapMode:
        ...
    
    @wrap_s.setter
    def wrap_s(self, value : aspose.cad.fileformats.glb.TextureWrapMode):
        ...
    
    @property
    def wrap_t(self) -> aspose.cad.fileformats.glb.TextureWrapMode:
        ...
    
    @wrap_t.setter
    def wrap_t(self, value : aspose.cad.fileformats.glb.TextureWrapMode):
        ...
    
    @property
    def primary_image(self) -> aspose.cad.fileformats.glb.materials.ImageBuilder:
        ...
    
    @primary_image.setter
    def primary_image(self, value : aspose.cad.fileformats.glb.materials.ImageBuilder):
        ...
    
    @property
    def fallback_image(self) -> aspose.cad.fileformats.glb.materials.ImageBuilder:
        ...
    
    @fallback_image.setter
    def fallback_image(self, value : aspose.cad.fileformats.glb.materials.ImageBuilder):
        ...
    
    @property
    def transform(self) -> aspose.cad.fileformats.glb.materials.TextureTransformBuilder:
        ...
    
    ...

class TextureTransformBuilder:
    
    @staticmethod
    def are_equal_by_content(a : aspose.cad.fileformats.glb.materials.TextureTransformBuilder, b : aspose.cad.fileformats.glb.materials.TextureTransformBuilder) -> bool:
        ...
    
    @property
    def rotation(self) -> float:
        ...
    
    @rotation.setter
    def rotation(self, value : float):
        ...
    
    @property
    def coordinate_set_override(self) -> Optional[int]:
        ...
    
    @coordinate_set_override.setter
    def coordinate_set_override(self, value : Optional[int]):
        ...
    
    ...

class AlphaMode:
    '''The alpha rendering mode of the material.'''
    
    @classmethod
    @property
    def OPAQUE(cls) -> AlphaMode:
        ...
    
    @classmethod
    @property
    def MASK(cls) -> AlphaMode:
        ...
    
    @classmethod
    @property
    def BLEND(cls) -> AlphaMode:
        ...
    
    ...

class KnownChannel:
    
    @classmethod
    @property
    def NORMAL(cls) -> KnownChannel:
        ...
    
    @classmethod
    @property
    def OCCLUSION(cls) -> KnownChannel:
        ...
    
    @classmethod
    @property
    def EMISSIVE(cls) -> KnownChannel:
        ...
    
    @classmethod
    @property
    def BASE_COLOR(cls) -> KnownChannel:
        ...
    
    @classmethod
    @property
    def METALLIC_ROUGHNESS(cls) -> KnownChannel:
        ...
    
    @classmethod
    @property
    def DIFFUSE(cls) -> KnownChannel:
        ...
    
    @classmethod
    @property
    def SPECULAR_GLOSSINESS(cls) -> KnownChannel:
        ...
    
    @classmethod
    @property
    def CLEAR_COAT(cls) -> KnownChannel:
        ...
    
    @classmethod
    @property
    def CLEAR_COAT_NORMAL(cls) -> KnownChannel:
        ...
    
    @classmethod
    @property
    def CLEAR_COAT_ROUGHNESS(cls) -> KnownChannel:
        ...
    
    @classmethod
    @property
    def TRANSMISSION(cls) -> KnownChannel:
        ...
    
    @classmethod
    @property
    def SHEEN_COLOR(cls) -> KnownChannel:
        ...
    
    @classmethod
    @property
    def SHEEN_ROUGHNESS(cls) -> KnownChannel:
        ...
    
    @classmethod
    @property
    def SPECULAR_COLOR(cls) -> KnownChannel:
        ...
    
    @classmethod
    @property
    def SPECULAR_FACTOR(cls) -> KnownChannel:
        ...
    
    @classmethod
    @property
    def VOLUME_THICKNESS(cls) -> KnownChannel:
        ...
    
    @classmethod
    @property
    def VOLUME_ATTENUATION(cls) -> KnownChannel:
        ...
    
    @classmethod
    @property
    def IRIDESCENCE(cls) -> KnownChannel:
        ...
    
    @classmethod
    @property
    def IRIDESCENCE_THICKNESS(cls) -> KnownChannel:
        ...
    
    ...

class KnownProperty:
    '''Enumeration of channel properties used in :py:attr:`aspose.cad.fileformats.glb.materials.ChannelBuilder.parameters`'''
    
    @classmethod
    @property
    def UNKNOWN(cls) -> KnownProperty:
        ...
    
    @classmethod
    @property
    def RGB(cls) -> KnownProperty:
        ...
    
    @classmethod
    @property
    def RGBA(cls) -> KnownProperty:
        ...
    
    @classmethod
    @property
    def NORMAL_SCALE(cls) -> KnownProperty:
        ...
    
    @classmethod
    @property
    def OCCLUSION_STRENGTH(cls) -> KnownProperty:
        ...
    
    @classmethod
    @property
    def EMISSIVE_STRENGTH(cls) -> KnownProperty:
        ...
    
    @classmethod
    @property
    def MINIMUM(cls) -> KnownProperty:
        ...
    
    @classmethod
    @property
    def MAXIMUM(cls) -> KnownProperty:
        ...
    
    @classmethod
    @property
    def INDEX_OF_REFRACTION(cls) -> KnownProperty:
        ...
    
    @classmethod
    @property
    def METALLIC_FACTOR(cls) -> KnownProperty:
        ...
    
    @classmethod
    @property
    def ROUGHNESS_FACTOR(cls) -> KnownProperty:
        ...
    
    @classmethod
    @property
    def SPECULAR_FACTOR(cls) -> KnownProperty:
        ...
    
    @classmethod
    @property
    def GLOSSINESS_FACTOR(cls) -> KnownProperty:
        ...
    
    @classmethod
    @property
    def CLEAR_COAT_FACTOR(cls) -> KnownProperty:
        ...
    
    @classmethod
    @property
    def THICKNESS_FACTOR(cls) -> KnownProperty:
        ...
    
    @classmethod
    @property
    def TRANSMISSION_FACTOR(cls) -> KnownProperty:
        ...
    
    @classmethod
    @property
    def IRIDESCENCE_FACTOR(cls) -> KnownProperty:
        ...
    
    @classmethod
    @property
    def ATTENUATION_DISTANCE(cls) -> KnownProperty:
        ...
    
    ...

