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

class Accessor(LogicalChildOfRoot):
    
    @overload
    def set_index_data(self, src : aspose.cad.fileformats.glb.memory.MemoryAccessor) -> None:
        ...
    
    @overload
    def set_index_data(self, buffer : aspose.cad.fileformats.glb.BufferView, buffer_byte_offset : int, item_count : int, encoding : aspose.cad.fileformats.glb.IndexEncodingType) -> None:
        '''Associates this :py:class:`aspose.cad.fileformats.glb.Accessor` with a :py:class:`aspose.cad.fileformats.glb.BufferView`
        
        :param buffer: The :py:class:`aspose.cad.fileformats.glb.BufferView` source.
        :param buffer_byte_offset: The start byte offset within ``buffer``.
        :param item_count: The number of items in the accessor.
        :param encoding: The :py:class:`aspose.cad.fileformats.glb.IndexEncodingType` item encoding.'''
        ...
    
    @overload
    def set_vertex_data(self, src : aspose.cad.fileformats.glb.memory.MemoryAccessor) -> None:
        ...
    
    @overload
    def set_vertex_data(self, buffer : aspose.cad.fileformats.glb.BufferView, buffer_byte_offset : int, item_count : int, dimensions : aspose.cad.fileformats.glb.DimensionType, encoding : aspose.cad.fileformats.glb.EncodingType, normalized : bool) -> None:
        '''Associates this :py:class:`aspose.cad.fileformats.glb.Accessor` with a :py:class:`aspose.cad.fileformats.glb.BufferView`
        
        :param buffer: The :py:class:`aspose.cad.fileformats.glb.BufferView` source.
        :param buffer_byte_offset: The start byte offset within ``buffer``.
        :param item_count: The number of items in the accessor.
        :param dimensions: The :py:class:`aspose.cad.fileformats.glb.DimensionType` item type.
        :param encoding: The :py:class:`aspose.cad.fileformats.glb.EncodingType` item encoding.
        :param normalized: The item normalization mode.'''
        ...
    
    def update_bounds(self) -> None:
        ...
    
    def set_data(self, buffer : aspose.cad.fileformats.glb.BufferView, buffer_byte_offset : int, item_count : int, dimensions : aspose.cad.fileformats.glb.DimensionType, encoding : aspose.cad.fileformats.glb.EncodingType, normalized : Optional[bool]) -> None:
        ...
    
    def as_indices_array(self) -> aspose.cad.fileformats.glb.memory.IntegerArray:
        ...
    
    def as_scalar_array(self) -> List[float]:
        ...
    
    def as_multi_array(self, dimensions : int) -> List[List[float]]:
        ...
    
    @property
    def extensions(self) -> List[aspose.cad.fileformats.glb.io.JsonSerializable]:
        '''Gets a collection of :py:class:`aspose.cad.fileformats.glb.io.JsonSerializable` instances.'''
        ...
    
    @property
    def extras(self) -> aspose.cad.fileformats.glb.io.JsonContent:
        '''Gets the extras content of this instance.'''
        ...
    
    @extras.setter
    def extras(self, value : aspose.cad.fileformats.glb.io.JsonContent):
        '''Sets the extras content of this instance.'''
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
    def logical_parent(self) -> aspose.cad.fileformats.glb.GlbData:
        ...
    
    @property
    def logical_index(self) -> int:
        ...
    
    @property
    def source_buffer_view(self) -> aspose.cad.fileformats.glb.BufferView:
        ...
    
    @property
    def count(self) -> int:
        '''Gets the number of items.'''
        ...
    
    @property
    def byte_offset(self) -> int:
        ...
    
    @property
    def byte_length(self) -> int:
        ...
    
    @property
    def dimensions(self) -> aspose.cad.fileformats.glb.DimensionType:
        '''Gets the :py:class:`aspose.cad.fileformats.glb.DimensionType` of an item.'''
        ...
    
    @property
    def encoding(self) -> aspose.cad.fileformats.glb.EncodingType:
        '''Gets the :py:class:`aspose.cad.fileformats.glb.EncodingType` of an item.'''
        ...
    
    @property
    def normalized(self) -> bool:
        '''Gets a value indicating whether the items values are normalized.'''
        ...
    
    @property
    def is_sparse(self) -> bool:
        ...
    
    @property
    def format(self) -> aspose.cad.fileformats.glb.memory.AttributeFormat:
        ...
    
    ...

class Animation(LogicalChildOfRoot):
    '''A keyframe animation.'''
    
    def find_channels(self, node : aspose.cad.fileformats.collada.fileparser.elements.Node) -> Iterable[aspose.cad.fileformats.glb.AnimationChannel]:
        ...
    
    def find_scale_channel(self, node : aspose.cad.fileformats.collada.fileparser.elements.Node) -> aspose.cad.fileformats.glb.AnimationChannel:
        ...
    
    def find_rotation_channel(self, node : aspose.cad.fileformats.collada.fileparser.elements.Node) -> aspose.cad.fileformats.glb.AnimationChannel:
        ...
    
    def find_translation_channel(self, node : aspose.cad.fileformats.collada.fileparser.elements.Node) -> aspose.cad.fileformats.glb.AnimationChannel:
        ...
    
    def find_morph_channel(self, node : aspose.cad.fileformats.collada.fileparser.elements.Node) -> aspose.cad.fileformats.glb.AnimationChannel:
        ...
    
    @property
    def extensions(self) -> List[aspose.cad.fileformats.glb.io.JsonSerializable]:
        '''Gets a collection of :py:class:`aspose.cad.fileformats.glb.io.JsonSerializable` instances.'''
        ...
    
    @property
    def extras(self) -> aspose.cad.fileformats.glb.io.JsonContent:
        '''Gets the extras content of this instance.'''
        ...
    
    @extras.setter
    def extras(self, value : aspose.cad.fileformats.glb.io.JsonContent):
        '''Sets the extras content of this instance.'''
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
    def logical_parent(self) -> aspose.cad.fileformats.glb.GlbData:
        ...
    
    @property
    def logical_index(self) -> int:
        ...
    
    @property
    def channels(self) -> List[aspose.cad.fileformats.glb.AnimationChannel]:
        ...
    
    @property
    def duration(self) -> float:
        ...
    
    ...

class AnimationChannel(ExtraProperties):
    
    @property
    def extensions(self) -> List[aspose.cad.fileformats.glb.io.JsonSerializable]:
        '''Gets a collection of :py:class:`aspose.cad.fileformats.glb.io.JsonSerializable` instances.'''
        ...
    
    @property
    def extras(self) -> aspose.cad.fileformats.glb.io.JsonContent:
        '''Gets the extras content of this instance.'''
        ...
    
    @extras.setter
    def extras(self, value : aspose.cad.fileformats.glb.io.JsonContent):
        '''Sets the extras content of this instance.'''
        ...
    
    @property
    def logical_index(self) -> int:
        ...
    
    @property
    def logical_parent(self) -> aspose.cad.fileformats.glb.Animation:
        ...
    
    @property
    def target_node(self) -> aspose.cad.fileformats.collada.fileparser.elements.Node:
        ...
    
    @property
    def target_node_path(self) -> aspose.cad.fileformats.glb.PropertyPath:
        ...
    
    ...

class Asset(ExtraProperties):
    '''Metadata about the glTF asset.'''
    
    @property
    def extensions(self) -> List[aspose.cad.fileformats.glb.io.JsonSerializable]:
        '''Gets a collection of :py:class:`aspose.cad.fileformats.glb.io.JsonSerializable` instances.'''
        ...
    
    @property
    def extras(self) -> aspose.cad.fileformats.glb.io.JsonContent:
        '''Gets the extras content of this instance.'''
        ...
    
    @extras.setter
    def extras(self, value : aspose.cad.fileformats.glb.io.JsonContent):
        '''Sets the extras content of this instance.'''
        ...
    
    @classmethod
    @property
    def assembly_informational_version(cls) -> str:
        ...
    
    @property
    def copyright(self) -> str:
        ...
    
    @copyright.setter
    def copyright(self, value : str):
        ...
    
    @property
    def generator(self) -> str:
        ...
    
    @generator.setter
    def generator(self, value : str):
        ...
    
    @property
    def version(self) -> Version:
        ...
    
    @property
    def min_version(self) -> Version:
        ...
    
    ...

class AttributeFormatTuple:
    
    ...

class Buffer(LogicalChildOfRoot):
    '''A buffer points to binary geometry, animation, or skins.'''
    
    @property
    def extensions(self) -> List[aspose.cad.fileformats.glb.io.JsonSerializable]:
        '''Gets a collection of :py:class:`aspose.cad.fileformats.glb.io.JsonSerializable` instances.'''
        ...
    
    @property
    def extras(self) -> aspose.cad.fileformats.glb.io.JsonContent:
        '''Gets the extras content of this instance.'''
        ...
    
    @extras.setter
    def extras(self, value : aspose.cad.fileformats.glb.io.JsonContent):
        '''Sets the extras content of this instance.'''
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
    def logical_parent(self) -> aspose.cad.fileformats.glb.GlbData:
        ...
    
    @property
    def logical_index(self) -> int:
        ...
    
    @property
    def content(self) -> bytes:
        ...
    
    ...

class BufferView(LogicalChildOfRoot):
    '''A view into a buffer generally representing a subset of the buffer.'''
    
    def find_images(self) -> Iterable[aspose.cad.fileformats.glb.ImageGlb]:
        ...
    
    def find_accessors(self) -> Iterable[aspose.cad.fileformats.collada.fileparser.elements.Accessor]:
        '''Finds all the accessors using this BufferView
        
        :returns: A collection of accessors'''
        ...
    
    def is_interleaved(self, accessors : Iterable[aspose.cad.fileformats.collada.fileparser.elements.Accessor]) -> bool:
        ...
    
    @property
    def extensions(self) -> List[aspose.cad.fileformats.glb.io.JsonSerializable]:
        '''Gets a collection of :py:class:`aspose.cad.fileformats.glb.io.JsonSerializable` instances.'''
        ...
    
    @property
    def extras(self) -> aspose.cad.fileformats.glb.io.JsonContent:
        '''Gets the extras content of this instance.'''
        ...
    
    @extras.setter
    def extras(self, value : aspose.cad.fileformats.glb.io.JsonContent):
        '''Sets the extras content of this instance.'''
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
    def logical_parent(self) -> aspose.cad.fileformats.glb.GlbData:
        ...
    
    @property
    def logical_index(self) -> int:
        ...
    
    @property
    def is_vertex_buffer(self) -> bool:
        ...
    
    @property
    def is_index_buffer(self) -> bool:
        ...
    
    @property
    def is_data_buffer(self) -> bool:
        ...
    
    @property
    def byte_stride(self) -> int:
        ...
    
    ...

class Camera(LogicalChildOfRoot):
    '''A camera's projection.
    A node **MAY** reference a camera to apply a transform to place the camera in the scene.'''
    
    def set_orthographic_mode(self, xmag : float, ymag : float, znear : float, zfar : float) -> None:
        '''Configures this :py:class:`aspose.cad.fileformats.glb.Camera` to use Orthographic projection.
        
        :param xmag: Magnification in the X axis.
        :param ymag: Magnification in the Y axis.
        :param znear: Distance to the near pane in the Z axis.
        :param zfar: Distance to the far plane in the Z axis.'''
        ...
    
    def set_perspective_mode(self, aspect_ratio : Optional[float], yfov : float, znear : float, zfar : float) -> None:
        ...
    
    @property
    def extensions(self) -> List[aspose.cad.fileformats.glb.io.JsonSerializable]:
        '''Gets a collection of :py:class:`aspose.cad.fileformats.glb.io.JsonSerializable` instances.'''
        ...
    
    @property
    def extras(self) -> aspose.cad.fileformats.glb.io.JsonContent:
        '''Gets the extras content of this instance.'''
        ...
    
    @extras.setter
    def extras(self, value : aspose.cad.fileformats.glb.io.JsonContent):
        '''Sets the extras content of this instance.'''
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
    def logical_parent(self) -> aspose.cad.fileformats.glb.GlbData:
        ...
    
    @property
    def logical_index(self) -> int:
        ...
    
    @property
    def settings(self) -> aspose.cad.fileformats.glb.ICamera:
        ...
    
    ...

class ExtensionsFactory:
    '''Global extensions manager.'''
    
    @classmethod
    @property
    def supported_extensions(cls) -> Iterable[str]:
        ...
    
    ...

class ExtraProperties(aspose.cad.fileformats.glb.io.JsonSerializable):
    '''Represents the base class for all glTF 2 Schema objects.'''
    
    @property
    def extensions(self) -> List[aspose.cad.fileformats.glb.io.JsonSerializable]:
        '''Gets a collection of :py:class:`aspose.cad.fileformats.glb.io.JsonSerializable` instances.'''
        ...
    
    @property
    def extras(self) -> aspose.cad.fileformats.glb.io.JsonContent:
        '''Gets the extras content of this instance.'''
        ...
    
    @extras.setter
    def extras(self, value : aspose.cad.fileformats.glb.io.JsonContent):
        '''Sets the extras content of this instance.'''
        ...
    
    ...

class GlbData(ExtraProperties):
    '''The root object for a glTF asset.'''
    
    @overload
    def merge_buffers(self) -> None:
        '''Merges all the :py:attr:`aspose.cad.fileformats.glb.GlbData.logical_buffers` instances into a single big one.'''
        ...
    
    @overload
    def merge_buffers(self, max_size : int) -> None:
        '''Merges all the :py:attr:`aspose.cad.fileformats.glb.GlbData.logical_buffers` instances into buffers of ``maxSize`` size.
        
        :param max_size: The maximum size of each buffer.
        Notice that if a single BufferView is larger than ``maxSize``, that buffer will be also larger.'''
        ...
    
    @overload
    def use_buffer_view(self, buffer : bytes, byte_offset : int, byte_length : Optional[int], byte_stride : int, target : Optional[aspose.cad.fileformats.glb.BufferMode]) -> aspose.cad.fileformats.glb.BufferView:
        ...
    
    @overload
    def use_buffer_view(self, buffer : aspose.cad.fileformats.glb.Buffer, byte_offset : int, byte_length : Optional[int], byte_stride : int, target : Optional[aspose.cad.fileformats.glb.BufferMode]) -> aspose.cad.fileformats.glb.BufferView:
        ...
    
    @overload
    def create_punctual_light(self, light_type : aspose.cad.fileformats.glb.PunctualLightType) -> aspose.cad.fileformats.glb.PunctualLight:
        '''Creates a new :py:class:`aspose.cad.fileformats.glb.PunctualLight` instance and
        adds it to :py:attr:`aspose.cad.fileformats.glb.GlbData.logical_punctual_lights`.
        
        :param light_type: A value of :py:class:`aspose.cad.fileformats.glb.PunctualLightType` describing the type of light to create.
        :returns: A :py:class:`aspose.cad.fileformats.glb.PunctualLight` instance.'''
        ...
    
    @overload
    def create_punctual_light(self, name : str, light_type : aspose.cad.fileformats.glb.PunctualLightType) -> aspose.cad.fileformats.glb.PunctualLight:
        '''Creates a new :py:class:`aspose.cad.fileformats.glb.PunctualLight` instance.
        and adds it to :py:attr:`aspose.cad.fileformats.glb.GlbData.logical_punctual_lights`.
        
        :param name: The name of the instance.
        :param light_type: A value of :py:class:`aspose.cad.fileformats.glb.PunctualLightType` describing the type of light to create.
        :returns: A :py:class:`aspose.cad.fileformats.glb.PunctualLight` instance.'''
        ...
    
    @overload
    def use_scene(self, index : int) -> aspose.cad.fileformats.collada.fileparser.elements.Scene:
        '''Creates or reuses a :py:class:`aspose.cad.fileformats.glb.Scene` instance
        at :py:attr:`aspose.cad.fileformats.glb.GlbData.logical_scenes`.
        
        :param index: The zero-based index of the :py:class:`aspose.cad.fileformats.glb.Scene` in :py:attr:`aspose.cad.fileformats.glb.GlbData.logical_scenes`.
        :returns: A :py:class:`aspose.cad.fileformats.glb.Scene` instance.'''
        ...
    
    @overload
    def use_scene(self, name : str) -> aspose.cad.fileformats.collada.fileparser.elements.Scene:
        '''Creates or reuses a :py:class:`aspose.cad.fileformats.glb.Scene` instance that has the
        same ``name`` at :py:attr:`aspose.cad.fileformats.glb.GlbData.logical_scenes`.
        
        :param name: The name of the instance.
        :returns: A :py:class:`aspose.cad.fileformats.glb.Scene` instance.'''
        ...
    
    @overload
    def use_texture(self, primary : aspose.cad.fileformats.glb.ImageGlb, sampler : aspose.cad.fileformats.glb.TextureSampler) -> aspose.cad.fileformats.glb.Texture:
        '''Creates or reuses a :py:class:`aspose.cad.fileformats.glb.Texture` instance
        at :py:attr:`aspose.cad.fileformats.glb.GlbData.logical_textures`.
        
        :param primary: The source :py:class:`aspose.cad.fileformats.glb.ImageGlb`.
        :param sampler: The source :py:class:`aspose.cad.fileformats.glb.TextureSampler`.
        :returns: A :py:class:`aspose.cad.fileformats.glb.Texture` instance.'''
        ...
    
    @overload
    def use_texture(self, primary : aspose.cad.fileformats.glb.ImageGlb, fallback : aspose.cad.fileformats.glb.ImageGlb, sampler : aspose.cad.fileformats.glb.TextureSampler) -> aspose.cad.fileformats.glb.Texture:
        '''Creates or reuses a :py:class:`aspose.cad.fileformats.glb.Texture` instance
        at :py:attr:`aspose.cad.fileformats.glb.GlbData.logical_textures`.
        
        :param primary: The source :py:class:`aspose.cad.fileformats.glb.ImageGlb`.
        :param fallback: The source :py:class:`aspose.cad.fileformats.glb.ImageGlb`.
        :param sampler: The source :py:class:`aspose.cad.fileformats.glb.TextureSampler`.
        :returns: A :py:class:`aspose.cad.fileformats.glb.Texture` instance.'''
        ...
    
    @overload
    def save_gltf(self, file_path : str, settings : aspose.cad.fileformats.glb.WriteSettings) -> None:
        '''Writes this :py:class:`aspose.cad.fileformats.glb.GlbData` to a file in GLTF format.
        
        :param file_path: A valid file path to write to.
        :param settings: Optional settings.'''
        ...
    
    @overload
    def save_gltf(self, stream : io.RawIOBase, gltf_stream : io.RawIOBase, bin_stream : io.RawIOBase, name : str, settings : aspose.cad.fileformats.glb.WriteSettings) -> None:
        ...
    
    @staticmethod
    def create_model() -> aspose.cad.fileformats.glb.GlbData:
        '''Creates a new :py:class:`aspose.cad.fileformats.glb.GlbData` instance.
        
        :returns: A :py:class:`aspose.cad.fileformats.glb.GlbData` instance.'''
        ...
    
    def deep_clone(self) -> aspose.cad.fileformats.glb.GlbData:
        '''Creates a complete clone of this :py:class:`aspose.cad.fileformats.glb.GlbData` instance.
        
        :returns: A new :py:class:`aspose.cad.fileformats.glb.GlbData` instance.'''
        ...
    
    def create_accessor(self, name : str) -> aspose.cad.fileformats.collada.fileparser.elements.Accessor:
        '''Creates a new :py:class:`aspose.cad.fileformats.glb.Accessor` instance
        and adds it to :py:class:`GLTF.Schema2.ModelRoot.LogicalAccessors`.
        
        :param name: The name of the instance.
        :returns: A :py:class:`aspose.cad.fileformats.glb.Accessor` instance.'''
        ...
    
    def create_animation(self, name : str) -> aspose.cad.fileformats.glb.Animation:
        '''Creates a new :py:class:`aspose.cad.fileformats.glb.Animation` instance and adds it to :py:attr:`aspose.cad.fileformats.glb.GlbData.logical_animations`.
        
        :param name: The name of the instance.
        :returns: A :py:class:`aspose.cad.fileformats.glb.Animation` instance.'''
        ...
    
    def create_buffer(self, byte_count : int) -> aspose.cad.fileformats.glb.Buffer:
        '''Creates a new :py:class:`aspose.cad.fileformats.glb.Buffer` instance
        and adds it to :py:attr:`aspose.cad.fileformats.glb.GlbData.logical_buffers`.
        
        :param byte_count: the size of the buffer, in bytes.
        :returns: A :py:class:`aspose.cad.fileformats.glb.Buffer` instance.'''
        ...
    
    def use_buffer(self, content : bytes) -> aspose.cad.fileformats.glb.Buffer:
        '''Creates or reuses a :py:class:`aspose.cad.fileformats.glb.Buffer` instance
        at :py:attr:`aspose.cad.fileformats.glb.GlbData.logical_buffers`.
        
        :param content: the byte array to be wrapped as a buffer
        :returns: A :py:class:`aspose.cad.fileformats.glb.Buffer` instance.'''
        ...
    
    def isolate_memory(self) -> None:
        '''Refreshes all internal memory buffers.'''
        ...
    
    def create_buffer_view(self, byte_size : int, byte_stride : int, target : Optional[aspose.cad.fileformats.glb.BufferMode]) -> aspose.cad.fileformats.glb.BufferView:
        ...
    
    def create_camera(self, name : str) -> aspose.cad.fileformats.collada.fileparser.elements.Camera:
        '''Creates a new :py:class:`aspose.cad.fileformats.glb.Camera` instance.
        and appends it to :py:attr:`aspose.cad.fileformats.glb.GlbData.logical_cameras`.
        
        :param name: The name of the instance.
        :returns: A :py:class:`aspose.cad.fileformats.glb.Camera` instance.'''
        ...
    
    def create_image(self, name : str) -> aspose.cad.fileformats.glb.ImageGlb:
        '''Creates a new :py:class:`aspose.cad.Image` instance.
        and appends it to :py:attr:`aspose.cad.fileformats.glb.GlbData.logical_images`.
        
        :param name: The name of the instance.
        :returns: A :py:class:`aspose.cad.Image` instance.'''
        ...
    
    def use_image(self, image_content : aspose.cad.fileformats.glb.memory.MemoryImage) -> aspose.cad.fileformats.glb.ImageGlb:
        '''Creates or reuses a :py:class:`aspose.cad.Image` instance.
        
        :param image_content: An image encoded in PNG, JPEG or DDS
        :returns: A :py:class:`aspose.cad.Image` instance.'''
        ...
    
    def merge_images(self) -> None:
        '''Transfers all the :py:attr:`aspose.cad.fileformats.glb.GlbData.logical_images` content into :py:class:`aspose.cad.fileformats.glb.BufferView` instances'''
        ...
    
    def create_material(self, name : str) -> aspose.cad.fileformats.collada.fileparser.elements.Material:
        '''Creates a new :py:class:`aspose.cad.fileformats.glb.Material` instance and appends it to :py:attr:`aspose.cad.fileformats.glb.GlbData.logical_materials`.
        
        :param name: The name of the instance.
        :returns: A :py:class:`aspose.cad.fileformats.glb.Material` instance.'''
        ...
    
    def create_mesh(self, name : str) -> aspose.cad.fileformats.collada.fileparser.elements.Mesh:
        '''Creates a new :py:class:`aspose.cad.fileformats.glb.Mesh` instance
        and appends it to :py:attr:`aspose.cad.fileformats.glb.GlbData.logical_meshes`.
        
        :param name: The name of the instance.
        :returns: A :py:class:`aspose.cad.fileformats.glb.Mesh` instance.'''
        ...
    
    def create_logical_node(self) -> aspose.cad.fileformats.collada.fileparser.elements.Node:
        ...
    
    @staticmethod
    def validate(file_path : str) -> aspose.cad.fileformats.glb.validation.ValidationResult:
        ...
    
    @staticmethod
    def load_glb_image(file_path : str, settings : aspose.cad.fileformats.glb.ReadSettings) -> aspose.cad.fileformats.glb.GlbData:
        '''Reads a :py:class:`aspose.cad.fileformats.glb.GlbData` instance from a path pointing to a GLB or a GLTF file
        
        :param file_path: A valid file path.
        :param settings: Optional settings.
        :returns: A :py:class:`aspose.cad.fileformats.glb.GlbData` instance.'''
        ...
    
    @staticmethod
    def load(stream : io.RawIOBase, settings : aspose.cad.fileformats.glb.ReadSettings) -> aspose.cad.fileformats.glb.GlbData:
        ...
    
    @staticmethod
    def read_glb(stream : io.RawIOBase, settings : aspose.cad.fileformats.glb.ReadSettings) -> aspose.cad.fileformats.glb.GlbData:
        '''Reads a :py:class:`aspose.cad.fileformats.glb.GlbData` instance from a :py:class:`io.RawIOBase` representing a GLB file
        
        :param stream: The source :py:class:`io.RawIOBase`.
        :param settings: Optional settings.
        :returns: A :py:class:`aspose.cad.fileformats.glb.GlbData` instance.'''
        ...
    
    @staticmethod
    def get_satellite_paths(file_path : str) -> List[str]:
        '''Gets the list of satellite / dependency files for a given glTF file.
        This includes binary blobs and texture images.
        
        :param file_path: A valid file path.
        :returns: A list of relative file paths, as found in the file.'''
        ...
    
    def create_skin(self, name : str) -> aspose.cad.fileformats.glb.Skin:
        '''Creates a new :py:class:`aspose.cad.fileformats.glb.Skin` instance
        and adds it to :py:attr:`aspose.cad.fileformats.glb.GlbData.logical_skins`.
        
        :param name: The name of the instance.
        :returns: A :py:class:`aspose.cad.fileformats.glb.Skin` instance.'''
        ...
    
    def use_texture_sampler(self, ws : aspose.cad.fileformats.glb.TextureWrapMode, wt : aspose.cad.fileformats.glb.TextureWrapMode, min : aspose.cad.fileformats.glb.TextureMipMapFilter, mag : aspose.cad.fileformats.glb.TextureInterpolationFilter) -> aspose.cad.fileformats.glb.TextureSampler:
        '''Creates or reuses a :py:class:`aspose.cad.fileformats.glb.TextureSampler` instance
        at :py:attr:`aspose.cad.fileformats.glb.GlbData.logical_texture_samplers`.
        
        :param ws: The :py:class:`aspose.cad.fileformats.glb.TextureWrapMode` in the S axis.
        :param wt: The :py:class:`aspose.cad.fileformats.glb.TextureWrapMode` in the T axis.
        :param min: A value of :py:class:`aspose.cad.fileformats.glb.TextureMipMapFilter`.
        :param mag: A value of :py:class:`aspose.cad.fileformats.glb.TextureInterpolationFilter`.
        :returns: A :py:class:`aspose.cad.fileformats.glb.TextureSampler` instance, or null if all the arguments are default values.'''
        ...
    
    def save(self, file_path : str, settings : aspose.cad.fileformats.glb.WriteSettings) -> None:
        '''Writes this :py:class:`aspose.cad.fileformats.glb.GlbData` to a file in GLTF or GLB based on the extension of ``filePath``.
        
        :param file_path: A valid file path to write to.
        :param settings: Optional settings.'''
        ...
    
    def save_glb(self, file_path : str, settings : aspose.cad.fileformats.glb.WriteSettings) -> None:
        '''Writes this :py:class:`aspose.cad.fileformats.glb.GlbData` to a file in GLB format.
        
        :param file_path: A valid file path to write to.
        :param settings: Optional settings.'''
        ...
    
    def save_glb_image(self, stream : io.RawIOBase, settings : aspose.cad.fileformats.glb.WriteSettings) -> None:
        ...
    
    def save_gltf_image(self, stream : io.RawIOBase, settings : aspose.cad.fileformats.glb.WriteSettings) -> None:
        ...
    
    def get_json_preview(self) -> str:
        '''Gets the JSON document of this :py:class:`aspose.cad.fileformats.glb.GlbData`.
        
        :returns: A JSON content.'''
        ...
    
    def write_glb(self, stream : io.RawIOBase, settings : aspose.cad.fileformats.glb.WriteSettings) -> None:
        '''Writes this :py:class:`aspose.cad.fileformats.glb.GlbData` to a :py:class:`io.RawIOBase` in GLB format.
        
        :param stream: A :py:class:`io.RawIOBase` open for writing.
        :param settings: Optional settings.'''
        ...
    
    @property
    def extensions(self) -> List[aspose.cad.fileformats.glb.io.JsonSerializable]:
        '''Gets a collection of :py:class:`aspose.cad.fileformats.glb.io.JsonSerializable` instances.'''
        ...
    
    @property
    def extras(self) -> aspose.cad.fileformats.glb.io.JsonContent:
        '''Gets the extras content of this instance.'''
        ...
    
    @extras.setter
    def extras(self, value : aspose.cad.fileformats.glb.io.JsonContent):
        '''Sets the extras content of this instance.'''
        ...
    
    @property
    def asset(self) -> aspose.cad.fileformats.collada.fileparser.elements.Asset:
        ...
    
    @property
    def extensions_used(self) -> Iterable[str]:
        ...
    
    @property
    def extensions_required(self) -> Iterable[str]:
        ...
    
    @property
    def incompatible_extensions(self) -> Iterable[str]:
        ...
    
    @property
    def logical_materials(self) -> List[aspose.cad.fileformats.collada.fileparser.elements.Material]:
        ...
    
    @property
    def logical_textures(self) -> List[aspose.cad.fileformats.glb.Texture]:
        ...
    
    @property
    def logical_texture_samplers(self) -> List[aspose.cad.fileformats.glb.TextureSampler]:
        ...
    
    @property
    def logical_images(self) -> List[aspose.cad.fileformats.glb.ImageGlb]:
        ...
    
    @property
    def logical_buffers(self) -> List[aspose.cad.fileformats.glb.Buffer]:
        ...
    
    @property
    def logical_buffer_views(self) -> List[aspose.cad.fileformats.glb.BufferView]:
        ...
    
    @property
    def logical_accessors(self) -> List[aspose.cad.fileformats.collada.fileparser.elements.Accessor]:
        ...
    
    @property
    def logical_meshes(self) -> List[aspose.cad.fileformats.collada.fileparser.elements.Mesh]:
        ...
    
    @property
    def logical_skins(self) -> List[aspose.cad.fileformats.glb.Skin]:
        ...
    
    @property
    def logical_cameras(self) -> List[aspose.cad.fileformats.collada.fileparser.elements.Camera]:
        ...
    
    @property
    def logical_nodes(self) -> List[aspose.cad.fileformats.collada.fileparser.elements.Node]:
        ...
    
    @property
    def logical_scenes(self) -> List[aspose.cad.fileformats.collada.fileparser.elements.Scene]:
        ...
    
    @property
    def logical_animations(self) -> List[aspose.cad.fileformats.glb.Animation]:
        ...
    
    @property
    def default_scene(self) -> aspose.cad.fileformats.collada.fileparser.elements.Scene:
        ...
    
    @default_scene.setter
    def default_scene(self, value : aspose.cad.fileformats.collada.fileparser.elements.Scene):
        ...
    
    @property
    def mesh_quantization_allowed(self) -> bool:
        ...
    
    @property
    def logical_punctual_lights(self) -> List[aspose.cad.fileformats.glb.PunctualLight]:
        ...
    
    ...

class GlbImage(GltfImageBase):
    
    @overload
    def save(self) -> None:
        '''Saves the image data to the underlying stream.'''
        ...
    
    @overload
    def save(self, file_path : str, options : aspose.cad.imageoptions.ImageOptionsBase) -> None:
        '''Saves the object's data to the specified file location in the specified file format according to save options.
        
        :param file_path: The file path.
        :param options: The options.'''
        ...
    
    @overload
    def save(self, stream : io.RawIOBase, options_base : aspose.cad.imageoptions.ImageOptionsBase) -> None:
        '''Saves the image's data to the specified stream in the specified file format according to save options.
        
        :param stream: The stream to save the image's data to.
        :param options_base: The save options.'''
        ...
    
    @overload
    def save(self, stream : io.RawIOBase) -> None:
        '''Saves the object's data to the specified stream.
        
        :param stream: The stream to save the object's data to.'''
        ...
    
    @overload
    def save(self, file_path : str) -> None:
        '''Saves the object's data to the specified file location.
        
        :param file_path: The file path to save the object's data to.'''
        ...
    
    @overload
    def save(self, file_path : str, over_write : bool) -> None:
        '''Saves the object's data to the specified file location.
        
        :param file_path: The file path to save the object's data to.
        :param over_write: if set to ``true`` over write the file contents, otherwise append will occur.'''
        ...
    
    @overload
    @staticmethod
    def can_load(file_path : str) -> bool:
        '''Determines whether image can be loaded from the specified file path.
        
        :param file_path: The file path.
        :returns: ``true`` if image can be loaded from the specified file; otherwise, ``false``.'''
        ...
    
    @overload
    @staticmethod
    def can_load(file_path : str, load_options : aspose.cad.LoadOptions) -> bool:
        '''Determines whether an image can be loaded from the specified file path and optionally using the specified open options
        
        :param file_path: The file path.
        :param load_options: The load options.
        :returns: ``true`` if an image can be loaded from the specified file; otherwise, ``false``.'''
        ...
    
    @overload
    @staticmethod
    def can_load(stream : io.RawIOBase) -> bool:
        '''Determines whether image can be loaded from the specified stream.
        
        :param stream: The stream to load from.
        :returns: ``true`` if image can be loaded from the specified stream; otherwise, ``false``.'''
        ...
    
    @overload
    @staticmethod
    def can_load(stream : io.RawIOBase, load_options : aspose.cad.LoadOptions) -> bool:
        '''Determines whether image can be loaded from the specified stream and optionally using the specified ``loadOptions``.
        
        :param stream: The stream to load from.
        :param load_options: The load options.
        :returns: ``true`` if image can be loaded from the specified stream; otherwise, ``false``.'''
        ...
    
    @overload
    @staticmethod
    def get_file_format(file_path : str) -> aspose.cad.FileFormat:
        '''Gets the file format.
        
        :param file_path: The file path.
        :returns: The determined file format.'''
        ...
    
    @overload
    @staticmethod
    def get_file_format(stream : io.RawIOBase) -> aspose.cad.FileFormat:
        '''Gets the file format.
        
        :param stream: The stream.
        :returns: The determined file format.'''
        ...
    
    @overload
    @staticmethod
    def load(file_path : str, load_options : aspose.cad.LoadOptions) -> aspose.cad.Image:
        '''Loads a new image from the specified file.
        
        :param file_path: The file path to load image from.
        :param load_options: The load options.
        :returns: The loaded drawing.'''
        ...
    
    @overload
    @staticmethod
    def load(file_path : str) -> aspose.cad.Image:
        '''Loads a new image from the specified file.
        
        :param file_path: The file path to load image from.
        :returns: The loaded drawing.'''
        ...
    
    @overload
    @staticmethod
    def load(stream : io.RawIOBase, load_options : aspose.cad.LoadOptions) -> aspose.cad.Image:
        '''Loads a new image from the specified stream.
        
        :param stream: The stream to load image from.
        :param load_options: The load options.
        :returns: The loaded drawing.'''
        ...
    
    @overload
    @staticmethod
    def load(stream : io.RawIOBase, file_name : str, load_options : aspose.cad.LoadOptions) -> aspose.cad.Image:
        '''Loads a new image from the specified stream.
        
        :param stream: The stream to load image from.
        :param file_name: The file name.
        :param load_options: The load options.
        :returns: The loaded drawing.'''
        ...
    
    @overload
    @staticmethod
    def load(stream : io.RawIOBase) -> aspose.cad.Image:
        '''Loads a new image from the specified stream.
        
        :param stream: The stream to load image from.
        :returns: The loaded drawing.'''
        ...
    
    def cache_data(self) -> None:
        '''Caches the data and ensures no additional data loading will be performed from the underlying :py:attr:`aspose.cad.DataStreamSupporter.data_stream_container`.'''
        ...
    
    def get_strings(self) -> List[str]:
        '''Gets all string values from image.
        
        :returns: The array with string values.'''
        ...
    
    def can_save(self, options : aspose.cad.imageoptions.ImageOptionsBase) -> bool:
        '''Determines whether image can be saved to the specified file format represented by the passed save options.
        
        :param options: The save options to use.
        :returns: ``true`` if image can be saved to the specified file format represented by the passed save options; otherwise, ``false``.'''
        ...
    
    @property
    def disposed(self) -> bool:
        '''Gets a value indicating whether this instance is disposed.'''
        ...
    
    @property
    def data_stream_container(self) -> aspose.cad.StreamContainer:
        ...
    
    @property
    def is_cached(self) -> bool:
        ...
    
    @property
    def bounds(self) -> aspose.cad.Rectangle:
        '''Gets the image bounds.'''
        ...
    
    @property
    def container(self) -> aspose.cad.Image:
        '''Gets the :py:class:`aspose.cad.Image` container.'''
        ...
    
    @property
    def height(self) -> int:
        '''Gets the image height.'''
        ...
    
    @property
    def depth(self) -> int:
        '''Gets the image depth.'''
        ...
    
    @property
    def palette(self) -> aspose.cad.IColorPalette:
        '''Gets the color palette.'''
        ...
    
    @palette.setter
    def palette(self, value : aspose.cad.IColorPalette):
        '''Sets the color palette.'''
        ...
    
    @property
    def size(self) -> aspose.cad.Size:
        '''Gets the image size.'''
        ...
    
    @property
    def width(self) -> int:
        '''Gets the image width.'''
        ...
    
    @property
    def unit_type(self) -> aspose.cad.imageoptions.UnitType:
        ...
    
    @property
    def unitless_default_unit_type(self) -> aspose.cad.imageoptions.UnitType:
        ...
    
    @property
    def annotation_service(self) -> aspose.cad.annotations.IAnnotationService:
        ...
    
    @property
    def watermark_guard_service(self) -> aspose.cad.watermarkguard.IWatermarkGuardService:
        ...
    
    @property
    def data(self) -> aspose.cad.fileformats.glb.GlbData:
        ...
    
    ...

class GltfImage(GltfImageBase):
    
    @overload
    def save(self) -> None:
        '''Saves the image data to the underlying stream.'''
        ...
    
    @overload
    def save(self, file_path : str, options : aspose.cad.imageoptions.ImageOptionsBase) -> None:
        '''Saves the object's data to the specified file location in the specified file format according to save options.
        
        :param file_path: The file path.
        :param options: The options.'''
        ...
    
    @overload
    def save(self, stream : io.RawIOBase, options_base : aspose.cad.imageoptions.ImageOptionsBase) -> None:
        '''Saves the image's data to the specified stream in the specified file format according to save options.
        
        :param stream: The stream to save the image's data to.
        :param options_base: The save options.'''
        ...
    
    @overload
    def save(self, stream : io.RawIOBase) -> None:
        '''Saves the object's data to the specified stream.
        
        :param stream: The stream to save the object's data to.'''
        ...
    
    @overload
    def save(self, file_path : str) -> None:
        '''Saves the object's data to the specified file location.
        
        :param file_path: The file path to save the object's data to.'''
        ...
    
    @overload
    def save(self, file_path : str, over_write : bool) -> None:
        '''Saves the object's data to the specified file location.
        
        :param file_path: The file path to save the object's data to.
        :param over_write: if set to ``true`` over write the file contents, otherwise append will occur.'''
        ...
    
    @overload
    @staticmethod
    def can_load(file_path : str) -> bool:
        '''Determines whether image can be loaded from the specified file path.
        
        :param file_path: The file path.
        :returns: ``true`` if image can be loaded from the specified file; otherwise, ``false``.'''
        ...
    
    @overload
    @staticmethod
    def can_load(file_path : str, load_options : aspose.cad.LoadOptions) -> bool:
        '''Determines whether an image can be loaded from the specified file path and optionally using the specified open options
        
        :param file_path: The file path.
        :param load_options: The load options.
        :returns: ``true`` if an image can be loaded from the specified file; otherwise, ``false``.'''
        ...
    
    @overload
    @staticmethod
    def can_load(stream : io.RawIOBase) -> bool:
        '''Determines whether image can be loaded from the specified stream.
        
        :param stream: The stream to load from.
        :returns: ``true`` if image can be loaded from the specified stream; otherwise, ``false``.'''
        ...
    
    @overload
    @staticmethod
    def can_load(stream : io.RawIOBase, load_options : aspose.cad.LoadOptions) -> bool:
        '''Determines whether image can be loaded from the specified stream and optionally using the specified ``loadOptions``.
        
        :param stream: The stream to load from.
        :param load_options: The load options.
        :returns: ``true`` if image can be loaded from the specified stream; otherwise, ``false``.'''
        ...
    
    @overload
    @staticmethod
    def get_file_format(file_path : str) -> aspose.cad.FileFormat:
        '''Gets the file format.
        
        :param file_path: The file path.
        :returns: The determined file format.'''
        ...
    
    @overload
    @staticmethod
    def get_file_format(stream : io.RawIOBase) -> aspose.cad.FileFormat:
        '''Gets the file format.
        
        :param stream: The stream.
        :returns: The determined file format.'''
        ...
    
    @overload
    @staticmethod
    def load(file_path : str, load_options : aspose.cad.LoadOptions) -> aspose.cad.Image:
        '''Loads a new image from the specified file.
        
        :param file_path: The file path to load image from.
        :param load_options: The load options.
        :returns: The loaded drawing.'''
        ...
    
    @overload
    @staticmethod
    def load(file_path : str) -> aspose.cad.Image:
        '''Loads a new image from the specified file.
        
        :param file_path: The file path to load image from.
        :returns: The loaded drawing.'''
        ...
    
    @overload
    @staticmethod
    def load(stream : io.RawIOBase, load_options : aspose.cad.LoadOptions) -> aspose.cad.Image:
        '''Loads a new image from the specified stream.
        
        :param stream: The stream to load image from.
        :param load_options: The load options.
        :returns: The loaded drawing.'''
        ...
    
    @overload
    @staticmethod
    def load(stream : io.RawIOBase, file_name : str, load_options : aspose.cad.LoadOptions) -> aspose.cad.Image:
        '''Loads a new image from the specified stream.
        
        :param stream: The stream to load image from.
        :param file_name: The file name.
        :param load_options: The load options.
        :returns: The loaded drawing.'''
        ...
    
    @overload
    @staticmethod
    def load(stream : io.RawIOBase) -> aspose.cad.Image:
        '''Loads a new image from the specified stream.
        
        :param stream: The stream to load image from.
        :returns: The loaded drawing.'''
        ...
    
    def cache_data(self) -> None:
        '''Caches the data and ensures no additional data loading will be performed from the underlying :py:attr:`aspose.cad.DataStreamSupporter.data_stream_container`.'''
        ...
    
    def get_strings(self) -> List[str]:
        '''Gets all string values from image.
        
        :returns: The array with string values.'''
        ...
    
    def can_save(self, options : aspose.cad.imageoptions.ImageOptionsBase) -> bool:
        '''Determines whether image can be saved to the specified file format represented by the passed save options.
        
        :param options: The save options to use.
        :returns: ``true`` if image can be saved to the specified file format represented by the passed save options; otherwise, ``false``.'''
        ...
    
    @property
    def disposed(self) -> bool:
        '''Gets a value indicating whether this instance is disposed.'''
        ...
    
    @property
    def data_stream_container(self) -> aspose.cad.StreamContainer:
        ...
    
    @property
    def is_cached(self) -> bool:
        ...
    
    @property
    def bounds(self) -> aspose.cad.Rectangle:
        '''Gets the image bounds.'''
        ...
    
    @property
    def container(self) -> aspose.cad.Image:
        '''Gets the :py:class:`aspose.cad.Image` container.'''
        ...
    
    @property
    def height(self) -> int:
        '''Gets the image height.'''
        ...
    
    @property
    def depth(self) -> int:
        '''Gets the image depth.'''
        ...
    
    @property
    def palette(self) -> aspose.cad.IColorPalette:
        '''Gets the color palette.'''
        ...
    
    @palette.setter
    def palette(self, value : aspose.cad.IColorPalette):
        '''Sets the color palette.'''
        ...
    
    @property
    def size(self) -> aspose.cad.Size:
        '''Gets the image size.'''
        ...
    
    @property
    def width(self) -> int:
        '''Gets the image width.'''
        ...
    
    @property
    def unit_type(self) -> aspose.cad.imageoptions.UnitType:
        ...
    
    @property
    def unitless_default_unit_type(self) -> aspose.cad.imageoptions.UnitType:
        ...
    
    @property
    def annotation_service(self) -> aspose.cad.annotations.IAnnotationService:
        ...
    
    @property
    def watermark_guard_service(self) -> aspose.cad.watermarkguard.IWatermarkGuardService:
        ...
    
    @property
    def data(self) -> aspose.cad.fileformats.glb.GlbData:
        ...
    
    ...

class GltfImageBase(aspose.cad.Image):
    '''Represents the base class of a serializable glTF schema2 object.
    Inherited by :py:class:`aspose.cad.fileformats.glb.ExtraProperties`.'''
    
    @overload
    def save(self) -> None:
        '''Saves the image data to the underlying stream.'''
        ...
    
    @overload
    def save(self, file_path : str, options : aspose.cad.imageoptions.ImageOptionsBase) -> None:
        '''Saves the object's data to the specified file location in the specified file format according to save options.
        
        :param file_path: The file path.
        :param options: The options.'''
        ...
    
    @overload
    def save(self, stream : io.RawIOBase, options_base : aspose.cad.imageoptions.ImageOptionsBase) -> None:
        '''Saves the image's data to the specified stream in the specified file format according to save options.
        
        :param stream: The stream to save the image's data to.
        :param options_base: The save options.'''
        ...
    
    @overload
    def save(self, stream : io.RawIOBase) -> None:
        '''Saves the object's data to the specified stream.
        
        :param stream: The stream to save the object's data to.'''
        ...
    
    @overload
    def save(self, file_path : str) -> None:
        '''Saves the object's data to the specified file location.
        
        :param file_path: The file path to save the object's data to.'''
        ...
    
    @overload
    def save(self, file_path : str, over_write : bool) -> None:
        '''Saves the object's data to the specified file location.
        
        :param file_path: The file path to save the object's data to.
        :param over_write: if set to ``true`` over write the file contents, otherwise append will occur.'''
        ...
    
    @overload
    @staticmethod
    def can_load(file_path : str) -> bool:
        '''Determines whether image can be loaded from the specified file path.
        
        :param file_path: The file path.
        :returns: ``true`` if image can be loaded from the specified file; otherwise, ``false``.'''
        ...
    
    @overload
    @staticmethod
    def can_load(file_path : str, load_options : aspose.cad.LoadOptions) -> bool:
        '''Determines whether an image can be loaded from the specified file path and optionally using the specified open options
        
        :param file_path: The file path.
        :param load_options: The load options.
        :returns: ``true`` if an image can be loaded from the specified file; otherwise, ``false``.'''
        ...
    
    @overload
    @staticmethod
    def can_load(stream : io.RawIOBase) -> bool:
        '''Determines whether image can be loaded from the specified stream.
        
        :param stream: The stream to load from.
        :returns: ``true`` if image can be loaded from the specified stream; otherwise, ``false``.'''
        ...
    
    @overload
    @staticmethod
    def can_load(stream : io.RawIOBase, load_options : aspose.cad.LoadOptions) -> bool:
        '''Determines whether image can be loaded from the specified stream and optionally using the specified ``loadOptions``.
        
        :param stream: The stream to load from.
        :param load_options: The load options.
        :returns: ``true`` if image can be loaded from the specified stream; otherwise, ``false``.'''
        ...
    
    @overload
    @staticmethod
    def get_file_format(file_path : str) -> aspose.cad.FileFormat:
        '''Gets the file format.
        
        :param file_path: The file path.
        :returns: The determined file format.'''
        ...
    
    @overload
    @staticmethod
    def get_file_format(stream : io.RawIOBase) -> aspose.cad.FileFormat:
        '''Gets the file format.
        
        :param stream: The stream.
        :returns: The determined file format.'''
        ...
    
    @overload
    @staticmethod
    def load(file_path : str, load_options : aspose.cad.LoadOptions) -> aspose.cad.Image:
        '''Loads a new image from the specified file.
        
        :param file_path: The file path to load image from.
        :param load_options: The load options.
        :returns: The loaded drawing.'''
        ...
    
    @overload
    @staticmethod
    def load(file_path : str) -> aspose.cad.Image:
        '''Loads a new image from the specified file.
        
        :param file_path: The file path to load image from.
        :returns: The loaded drawing.'''
        ...
    
    @overload
    @staticmethod
    def load(stream : io.RawIOBase, load_options : aspose.cad.LoadOptions) -> aspose.cad.Image:
        '''Loads a new image from the specified stream.
        
        :param stream: The stream to load image from.
        :param load_options: The load options.
        :returns: The loaded drawing.'''
        ...
    
    @overload
    @staticmethod
    def load(stream : io.RawIOBase, file_name : str, load_options : aspose.cad.LoadOptions) -> aspose.cad.Image:
        '''Loads a new image from the specified stream.
        
        :param stream: The stream to load image from.
        :param file_name: The file name.
        :param load_options: The load options.
        :returns: The loaded drawing.'''
        ...
    
    @overload
    @staticmethod
    def load(stream : io.RawIOBase) -> aspose.cad.Image:
        '''Loads a new image from the specified stream.
        
        :param stream: The stream to load image from.
        :returns: The loaded drawing.'''
        ...
    
    def cache_data(self) -> None:
        '''Caches the data and ensures no additional data loading will be performed from the underlying :py:attr:`aspose.cad.DataStreamSupporter.data_stream_container`.'''
        ...
    
    def get_strings(self) -> List[str]:
        '''Gets all string values from image.
        
        :returns: The array with string values.'''
        ...
    
    def can_save(self, options : aspose.cad.imageoptions.ImageOptionsBase) -> bool:
        '''Determines whether image can be saved to the specified file format represented by the passed save options.
        
        :param options: The save options to use.
        :returns: ``true`` if image can be saved to the specified file format represented by the passed save options; otherwise, ``false``.'''
        ...
    
    @property
    def disposed(self) -> bool:
        '''Gets a value indicating whether this instance is disposed.'''
        ...
    
    @property
    def data_stream_container(self) -> aspose.cad.StreamContainer:
        ...
    
    @property
    def is_cached(self) -> bool:
        ...
    
    @property
    def bounds(self) -> aspose.cad.Rectangle:
        '''Gets the image bounds.'''
        ...
    
    @property
    def container(self) -> aspose.cad.Image:
        '''Gets the :py:class:`aspose.cad.Image` container.'''
        ...
    
    @property
    def height(self) -> int:
        '''Gets the image height.'''
        ...
    
    @property
    def depth(self) -> int:
        '''Gets the image depth.'''
        ...
    
    @property
    def palette(self) -> aspose.cad.IColorPalette:
        '''Gets the color palette.'''
        ...
    
    @palette.setter
    def palette(self, value : aspose.cad.IColorPalette):
        '''Sets the color palette.'''
        ...
    
    @property
    def size(self) -> aspose.cad.Size:
        '''Gets the image size.'''
        ...
    
    @property
    def width(self) -> int:
        '''Gets the image width.'''
        ...
    
    @property
    def unit_type(self) -> aspose.cad.imageoptions.UnitType:
        ...
    
    @property
    def unitless_default_unit_type(self) -> aspose.cad.imageoptions.UnitType:
        ...
    
    @property
    def annotation_service(self) -> aspose.cad.annotations.IAnnotationService:
        ...
    
    @property
    def watermark_guard_service(self) -> aspose.cad.watermarkguard.IWatermarkGuardService:
        ...
    
    @property
    def data(self) -> aspose.cad.fileformats.glb.GlbData:
        ...
    
    ...

class GltfLoadOptions(aspose.cad.LoadOptions):
    '''Represents the loading options for GLTF/GLB image.'''
    
    @property
    def custom_font_folder_options(self) -> aspose.cad.CustomFontFolderOptions:
        ...
    
    @custom_font_folder_options.setter
    def custom_font_folder_options(self, value : aspose.cad.CustomFontFolderOptions):
        ...
    
    @property
    def custom_font_folders(self) -> List[str]:
        ...
    
    @custom_font_folders.setter
    def custom_font_folders(self, value : List[str]):
        ...
    
    @property
    def specified_encoding(self) -> aspose.cad.CodePages:
        ...
    
    @specified_encoding.setter
    def specified_encoding(self, value : aspose.cad.CodePages):
        ...
    
    @property
    def specified_mif_encoding(self) -> aspose.cad.MifCodePages:
        ...
    
    @specified_mif_encoding.setter
    def specified_mif_encoding(self, value : aspose.cad.MifCodePages):
        ...
    
    @property
    def data_background_color(self) -> aspose.cad.Color:
        ...
    
    @data_background_color.setter
    def data_background_color(self, value : aspose.cad.Color):
        ...
    
    @property
    def unload_on_dispose(self) -> bool:
        ...
    
    @unload_on_dispose.setter
    def unload_on_dispose(self, value : bool):
        ...
    
    @property
    def recover_malformed_cif_mif(self) -> bool:
        ...
    
    @recover_malformed_cif_mif.setter
    def recover_malformed_cif_mif(self, value : bool):
        ...
    
    @property
    def ignore_errors(self) -> bool:
        ...
    
    @ignore_errors.setter
    def ignore_errors(self, value : bool):
        ...
    
    @property
    def errors(self) -> List[aspose.cad.imageoptions.RenderResult]:
        '''Gets the list of loading errors.'''
        ...
    
    @property
    def vectorization_options(self) -> aspose.cad.VectorizationOptions:
        ...
    
    @vectorization_options.setter
    def vectorization_options(self, value : aspose.cad.VectorizationOptions):
        ...
    
    @property
    def skip_validation(self) -> bool:
        ...
    
    @skip_validation.setter
    def skip_validation(self, value : bool):
        ...
    
    @property
    def skip_tangents_calculation(self) -> bool:
        ...
    
    @skip_tangents_calculation.setter
    def skip_tangents_calculation(self, value : bool):
        ...
    
    ...

class ICamera:
    '''Common interface for :py:class:`Aspose.CAD.FileFormats.GLB.CameraOrthographic` and :py:class:`Aspose.CAD.FileFormats.GLB.CameraPerspective`.'''
    
    @property
    def is_orthographic(self) -> bool:
        ...
    
    @property
    def is_perspective(self) -> bool:
        ...
    
    ...

class IMaterialParameter:
    
    @property
    def name(self) -> str:
        ...
    
    @property
    def is_default(self) -> bool:
        ...
    
    @property
    def value_type(self) -> Type:
        ...
    
    @property
    def value(self) -> any:
        '''Gets the value of this parameter.
        
        Valid types are :py:class:`float`:py:class:`System.Numerics.Vector3` and :py:class:`System.Numerics.Vector4`'''
        ...
    
    @value.setter
    def value(self, value : any):
        '''Sets the value of this parameter.
        
        Valid types are :py:class:`float`:py:class:`System.Numerics.Vector3` and :py:class:`System.Numerics.Vector4`'''
        ...
    
    ...

class IVisualNodeContainer:
    '''Represents an abstract interface for a visual hierarchy.
    Implemented by :py:class:`aspose.cad.fileformats.glb.Node` and :py:class:`aspose.cad.fileformats.glb.Scene`.'''
    
    def create_node(self, name : str) -> aspose.cad.fileformats.collada.fileparser.elements.Node:
        ...
    
    @property
    def visual_children(self) -> Iterable[aspose.cad.fileformats.collada.fileparser.elements.Node]:
        ...
    
    ...

class ImageGlb(LogicalChildOfRoot):
    '''Image data used to create a texture. Image **MAY** be referenced by an URI (or IRI) or a buffer view index.'''
    
    @property
    def extensions(self) -> List[aspose.cad.fileformats.glb.io.JsonSerializable]:
        '''Gets a collection of :py:class:`aspose.cad.fileformats.glb.io.JsonSerializable` instances.'''
        ...
    
    @property
    def extras(self) -> aspose.cad.fileformats.glb.io.JsonContent:
        '''Gets the extras content of this instance.'''
        ...
    
    @extras.setter
    def extras(self, value : aspose.cad.fileformats.glb.io.JsonContent):
        '''Sets the extras content of this instance.'''
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
    def logical_parent(self) -> aspose.cad.fileformats.glb.GlbData:
        ...
    
    @property
    def logical_index(self) -> int:
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

class LogicalChildOfRoot(ExtraProperties):
    '''All gltf elements stored in ModelRoot must inherit from this class.'''
    
    @property
    def extensions(self) -> List[aspose.cad.fileformats.glb.io.JsonSerializable]:
        '''Gets a collection of :py:class:`aspose.cad.fileformats.glb.io.JsonSerializable` instances.'''
        ...
    
    @property
    def extras(self) -> aspose.cad.fileformats.glb.io.JsonContent:
        '''Gets the extras content of this instance.'''
        ...
    
    @extras.setter
    def extras(self, value : aspose.cad.fileformats.glb.io.JsonContent):
        '''Sets the extras content of this instance.'''
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
    def logical_parent(self) -> aspose.cad.fileformats.glb.GlbData:
        ...
    
    @property
    def logical_index(self) -> int:
        ...
    
    ...

class Material(LogicalChildOfRoot):
    '''The material appearance of a primitive.'''
    
    def initialize_unlit(self) -> None:
        '''Initializes this :py:class:`aspose.cad.fileformats.glb.Material` instance with Unlit attributes.'''
        ...
    
    def initialize_pbr_metallic_roughness(self, extension_names : List[str]) -> None:
        '''Initializes this :py:class:`aspose.cad.fileformats.glb.Material` instance with PBR Metallic Roughness attributes.
        
        :param extension_names: Extension names.
        Current valid names are: "ClearCoat", "Transmission", "Sheen"'''
        ...
    
    def initialize_pbr_specular_glossiness(self, use_fallback : bool) -> None:
        '''Initializes this :py:class:`aspose.cad.fileformats.glb.Material` instance with PBR Specular Glossiness attributes.
        
        :param use_fallback: true to add a PBRMetallicRoughness fallback material.'''
        ...
    
    def find_channel(self, channel_key : str) -> Optional[aspose.cad.fileformats.glb.MaterialChannel]:
        '''Finds an instance of :py:class:`aspose.cad.fileformats.glb.MaterialChannel`
        
        :param channel_key: The channel key. Currently, these values are used:
        - "Normal"
        - "Occlusion"
        - "Emissive"
        - When material is :py:class:`Aspose.CAD.FileFormats.GLB.MaterialPBRMetallicRoughness`:
        - "BaseColor"
        - "MetallicRoughness"
        - When material is :py:class:`Aspose.CAD.FileFormats.GLB.MaterialPBRSpecularGlossiness`:
        - "Diffuse"
        - "SpecularGlossiness"
        :returns: A :py:class:`aspose.cad.fileformats.glb.MaterialChannel` structure. or null if it does not exist'''
        ...
    
    @property
    def extensions(self) -> List[aspose.cad.fileformats.glb.io.JsonSerializable]:
        '''Gets a collection of :py:class:`aspose.cad.fileformats.glb.io.JsonSerializable` instances.'''
        ...
    
    @property
    def extras(self) -> aspose.cad.fileformats.glb.io.JsonContent:
        '''Gets the extras content of this instance.'''
        ...
    
    @extras.setter
    def extras(self, value : aspose.cad.fileformats.glb.io.JsonContent):
        '''Sets the extras content of this instance.'''
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
    def logical_parent(self) -> aspose.cad.fileformats.glb.GlbData:
        ...
    
    @property
    def logical_index(self) -> int:
        ...
    
    @property
    def alpha(self) -> aspose.cad.fileformats.glb.AlphaMode:
        '''Gets the :py:class:`aspose.cad.fileformats.glb.AlphaMode`.'''
        ...
    
    @alpha.setter
    def alpha(self, value : aspose.cad.fileformats.glb.AlphaMode):
        '''Sets the :py:class:`aspose.cad.fileformats.glb.AlphaMode`.'''
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
    def unlit(self) -> bool:
        '''Gets a value indicating whether this :py:class:`aspose.cad.fileformats.glb.Material` instance has Unlit extension.'''
        ...
    
    @property
    def channels(self) -> Iterable[aspose.cad.fileformats.glb.MaterialChannel]:
        '''Gets a collection of :py:class:`aspose.cad.fileformats.glb.MaterialChannel` elements available in this :py:class:`aspose.cad.fileformats.glb.Material` instance.'''
        ...
    
    @property
    def index_of_refraction(self) -> float:
        ...
    
    @index_of_refraction.setter
    def index_of_refraction(self, value : float):
        ...
    
    ...

class MaterialChannel:
    '''Represents a material sub-channel, which usually contains a texture.
    
    Use :py:attr:`aspose.cad.fileformats.glb.Material.channels` and :py:func:`aspose.cad.fileformats.glb.Material.find_channel` to access it.'''
    
    @overload
    def set_texture(self, tex_coord : int, primary_img : aspose.cad.fileformats.glb.ImageGlb, fallback_img : aspose.cad.fileformats.glb.ImageGlb, ws : aspose.cad.fileformats.glb.TextureWrapMode, wt : aspose.cad.fileformats.glb.TextureWrapMode, min : aspose.cad.fileformats.glb.TextureMipMapFilter, mag : aspose.cad.fileformats.glb.TextureInterpolationFilter) -> aspose.cad.fileformats.glb.Texture:
        ...
    
    @overload
    def set_texture(self, tex_set : int, tex : aspose.cad.fileformats.glb.Texture) -> None:
        ...
    
    def equals(self, other : aspose.cad.fileformats.glb.MaterialChannel) -> bool:
        ...
    
    def get_factor(self, key : str) -> float:
        ...
    
    def set_factor(self, key : str, value : float) -> None:
        ...
    
    @property
    def logical_parent(self) -> aspose.cad.fileformats.collada.fileparser.elements.Material:
        ...
    
    @property
    def key(self) -> str:
        ...
    
    @property
    def has_default_content(self) -> bool:
        ...
    
    @property
    def parameters(self) -> List[aspose.cad.fileformats.glb.IMaterialParameter]:
        ...
    
    @property
    def texture(self) -> aspose.cad.fileformats.glb.Texture:
        '''Gets the :py:attr:`aspose.cad.fileformats.glb.MaterialChannel.texture` instance used by this Material, or null.'''
        ...
    
    @property
    def texture_coordinate(self) -> int:
        ...
    
    @property
    def texture_transform(self) -> aspose.cad.fileformats.glb.TextureTransform:
        ...
    
    @property
    def texture_sampler(self) -> aspose.cad.fileformats.glb.TextureSampler:
        ...
    
    ...

class Mesh(LogicalChildOfRoot):
    '''A set of primitives to be rendered.
    Its global transform is defined by a node that references it.'''
    
    @overload
    def set_morph_weights(self, weights : List[float]) -> None:
        ...
    
    @overload
    def set_morph_weights(self, weights : aspose.cad.fileformats.glb.transforms.SparseWeight8) -> None:
        ...
    
    def get_morph_weights(self) -> List[float]:
        ...
    
    def create_primitive(self) -> aspose.cad.fileformats.glb.MeshPrimitive:
        '''Creates a new :py:class:`aspose.cad.fileformats.glb.MeshPrimitive` instance
        and adds it to the current :py:class:`aspose.cad.fileformats.glb.Mesh`.
        
        :returns: A :py:class:`aspose.cad.fileformats.glb.MeshPrimitive` instance.'''
        ...
    
    @property
    def extensions(self) -> List[aspose.cad.fileformats.glb.io.JsonSerializable]:
        '''Gets a collection of :py:class:`aspose.cad.fileformats.glb.io.JsonSerializable` instances.'''
        ...
    
    @property
    def extras(self) -> aspose.cad.fileformats.glb.io.JsonContent:
        '''Gets the extras content of this instance.'''
        ...
    
    @extras.setter
    def extras(self, value : aspose.cad.fileformats.glb.io.JsonContent):
        '''Sets the extras content of this instance.'''
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
    def logical_parent(self) -> aspose.cad.fileformats.glb.GlbData:
        ...
    
    @property
    def logical_index(self) -> int:
        ...
    
    @property
    def visual_parents(self) -> Iterable[aspose.cad.fileformats.collada.fileparser.elements.Node]:
        ...
    
    @property
    def primitives(self) -> List[aspose.cad.fileformats.glb.MeshPrimitive]:
        ...
    
    @property
    def morph_weights(self) -> List[float]:
        ...
    
    @property
    def all_primitives_have_joints(self) -> bool:
        ...
    
    ...

class MeshGpuInstancing(ExtraProperties):
    '''glTF extension defines instance attributes for a node with a mesh.'''
    
    def clear_accessors(self) -> None:
        ...
    
    def get_accessor(self, attribute_key : str) -> aspose.cad.fileformats.collada.fileparser.elements.Accessor:
        ...
    
    def set_accessor(self, attribute_key : str, accessor : aspose.cad.fileformats.collada.fileparser.elements.Accessor) -> None:
        ...
    
    def get_local_transform(self, index : int) -> aspose.cad.fileformats.glb.transforms.AffineTransform:
        ...
    
    @property
    def extensions(self) -> List[aspose.cad.fileformats.glb.io.JsonSerializable]:
        '''Gets a collection of :py:class:`aspose.cad.fileformats.glb.io.JsonSerializable` instances.'''
        ...
    
    @property
    def extras(self) -> aspose.cad.fileformats.glb.io.JsonContent:
        '''Gets the extras content of this instance.'''
        ...
    
    @extras.setter
    def extras(self, value : aspose.cad.fileformats.glb.io.JsonContent):
        '''Sets the extras content of this instance.'''
        ...
    
    @property
    def logical_parent(self) -> aspose.cad.fileformats.glb.io.JsonSerializable:
        ...
    
    @property
    def visual_parent(self) -> aspose.cad.fileformats.glb.io.JsonSerializable:
        ...
    
    @property
    def count(self) -> int:
        '''Gets a value indicating the number of instances to draw.'''
        ...
    
    @property
    def local_transforms(self) -> Iterable[aspose.cad.fileformats.glb.transforms.AffineTransform]:
        ...
    
    ...

class MeshPrimitive(ExtraProperties):
    '''Geometry to be rendered with the given material.'''
    
    def get_buffer_views(self, include_indices : bool, include_vertices : bool, include_morphs : bool) -> Iterable[aspose.cad.fileformats.glb.BufferView]:
        ...
    
    def get_vertex_accessor(self, attribute_key : str) -> aspose.cad.fileformats.collada.fileparser.elements.Accessor:
        ...
    
    def set_vertex_accessor(self, attribute_key : str, accessor : aspose.cad.fileformats.collada.fileparser.elements.Accessor) -> None:
        ...
    
    def get_vertices(self, attribute_key : str) -> aspose.cad.fileformats.glb.memory.MemoryAccessor:
        ...
    
    def get_index_accessor(self) -> aspose.cad.fileformats.collada.fileparser.elements.Accessor:
        ...
    
    def set_index_accessor(self, accessor : aspose.cad.fileformats.collada.fileparser.elements.Accessor) -> None:
        ...
    
    def get_indices(self) -> List[int]:
        '''Gets the raw list of indices of this primitive.
        
        :returns: A list of indices, or null.'''
        ...
    
    def get_point_indices(self) -> Iterable[int]:
        '''Decodes the raw indices and returns a list of indexed points.
        
        :returns: A sequence of indexed points.'''
        ...
    
    @property
    def extensions(self) -> List[aspose.cad.fileformats.glb.io.JsonSerializable]:
        '''Gets a collection of :py:class:`aspose.cad.fileformats.glb.io.JsonSerializable` instances.'''
        ...
    
    @property
    def extras(self) -> aspose.cad.fileformats.glb.io.JsonContent:
        '''Gets the extras content of this instance.'''
        ...
    
    @extras.setter
    def extras(self, value : aspose.cad.fileformats.glb.io.JsonContent):
        '''Sets the extras content of this instance.'''
        ...
    
    @property
    def logical_index(self) -> int:
        ...
    
    @property
    def logical_parent(self) -> aspose.cad.fileformats.collada.fileparser.elements.Mesh:
        ...
    
    @property
    def material(self) -> aspose.cad.fileformats.collada.fileparser.elements.Material:
        '''Gets the :py:attr:`aspose.cad.fileformats.glb.MeshPrimitive.material` instance, or null.'''
        ...
    
    @material.setter
    def material(self, value : aspose.cad.fileformats.collada.fileparser.elements.Material):
        '''Sets the :py:attr:`aspose.cad.fileformats.glb.MeshPrimitive.material` instance, or null.'''
        ...
    
    @property
    def draw_primitive_type(self) -> aspose.cad.fileformats.glb.PrimitiveType:
        ...
    
    @draw_primitive_type.setter
    def draw_primitive_type(self, value : aspose.cad.fileformats.glb.PrimitiveType):
        ...
    
    @property
    def morph_targets_count(self) -> int:
        ...
    
    @property
    def index_accessor(self) -> aspose.cad.fileformats.collada.fileparser.elements.Accessor:
        ...
    
    @index_accessor.setter
    def index_accessor(self, value : aspose.cad.fileformats.collada.fileparser.elements.Accessor):
        ...
    
    ...

class MeshPrimitiveDracoMesh(ExtraProperties):
    '''Geometry to be rendered with the given material.'''
    
    def get_buffer_views(self, include_indices : bool, include_vertices : bool, include_morphs : bool) -> Iterable[aspose.cad.fileformats.glb.BufferView]:
        ...
    
    def get_vertex_accessor(self, attribute_key : str) -> aspose.cad.fileformats.collada.fileparser.elements.Accessor:
        ...
    
    def set_vertex_accessor(self, attribute_key : str, accessor : aspose.cad.fileformats.collada.fileparser.elements.Accessor) -> None:
        ...
    
    def get_vertices(self, attribute_key : str) -> aspose.cad.fileformats.glb.memory.MemoryAccessor:
        ...
    
    def get_index_accessor(self) -> aspose.cad.fileformats.collada.fileparser.elements.Accessor:
        ...
    
    def set_index_accessor(self, accessor : aspose.cad.fileformats.collada.fileparser.elements.Accessor) -> None:
        ...
    
    def get_indices(self) -> List[int]:
        '''Gets the raw list of indices of this primitive.
        
        :returns: A list of indices, or null.'''
        ...
    
    def get_point_indices(self) -> Iterable[int]:
        '''Decodes the raw indices and returns a list of indexed points.
        
        :returns: A sequence of indexed points.'''
        ...
    
    @property
    def extensions(self) -> List[aspose.cad.fileformats.glb.io.JsonSerializable]:
        '''Gets a collection of :py:class:`aspose.cad.fileformats.glb.io.JsonSerializable` instances.'''
        ...
    
    @property
    def extras(self) -> aspose.cad.fileformats.glb.io.JsonContent:
        '''Gets the extras content of this instance.'''
        ...
    
    @extras.setter
    def extras(self, value : aspose.cad.fileformats.glb.io.JsonContent):
        '''Sets the extras content of this instance.'''
        ...
    
    @property
    def logical_index(self) -> int:
        ...
    
    @property
    def logical_parent(self) -> aspose.cad.fileformats.collada.fileparser.elements.Mesh:
        ...
    
    @property
    def material(self) -> aspose.cad.fileformats.collada.fileparser.elements.Material:
        '''Gets the :py:attr:`aspose.cad.fileformats.glb.MeshPrimitiveDracoMesh.material` instance, or null.'''
        ...
    
    @material.setter
    def material(self, value : aspose.cad.fileformats.collada.fileparser.elements.Material):
        '''Sets the :py:attr:`aspose.cad.fileformats.glb.MeshPrimitiveDracoMesh.material` instance, or null.'''
        ...
    
    @property
    def draw_primitive_type(self) -> aspose.cad.fileformats.glb.PrimitiveType:
        ...
    
    @draw_primitive_type.setter
    def draw_primitive_type(self, value : aspose.cad.fileformats.glb.PrimitiveType):
        ...
    
    @property
    def morph_targets_count(self) -> int:
        ...
    
    @property
    def index_accessor(self) -> aspose.cad.fileformats.collada.fileparser.elements.Accessor:
        ...
    
    @index_accessor.setter
    def index_accessor(self, value : aspose.cad.fileformats.collada.fileparser.elements.Accessor):
        ...
    
    ...

class Node(LogicalChildOfRoot):
    '''A node in the node hierarchy.
    When the node contains `skin`, all `mesh.primitives` **MUST** contain `JOINTS_0` and `WEIGHTS_0` attributes.
    A node **MAY** have either a `matrix` or any combination of `translation`/`rotation`/`scale` (TRS) properties. TRS properties are converted to matrices and postmultiplied in the `T * R * S` order to compose the transformation matrix; first the scale is applied to the vertices, then the rotation, and then the translation. If none are provided, the transform is the identity. When a node is targeted for animation (referenced by an animation.channel.target), `matrix` **MUST NOT** be present.'''
    
    def get_gpu_instancing(self) -> aspose.cad.fileformats.glb.MeshGpuInstancing:
        ...
    
    def use_gpu_instancing(self) -> aspose.cad.fileformats.glb.MeshGpuInstancing:
        ...
    
    def remove_gpu_instancing(self) -> None:
        ...
    
    def get_local_transform(self, animation : aspose.cad.fileformats.glb.Animation, time : float) -> aspose.cad.fileformats.glb.transforms.AffineTransform:
        '''Gets the local transform of this node in a given animation at a given time.
        
        :param animation: the animation to sample.
        :param time: the time offset within the animation.
        :returns: the sampled transform.'''
        ...
    
    def get_morph_weights(self) -> List[float]:
        ...
    
    def set_morph_weights(self, weights : aspose.cad.fileformats.glb.transforms.SparseWeight8) -> None:
        ...
    
    def create_node(self, name : str) -> aspose.cad.fileformats.collada.fileparser.elements.Node:
        '''Creates a new :py:class:`aspose.cad.fileformats.glb.Node` instance,
        adds it to :py:attr:`aspose.cad.fileformats.glb.GlbData.logical_nodes`
        and references it as a child in the current graph.
        
        :param name: The name of the instance.
        :returns: A :py:class:`aspose.cad.fileformats.glb.Node` instance.'''
        ...
    
    @staticmethod
    def flatten(container : aspose.cad.fileformats.glb.IVisualNodeContainer) -> Iterable[aspose.cad.fileformats.collada.fileparser.elements.Node]:
        '''Returns all the :py:class:`aspose.cad.fileformats.glb.Node` instances of a visual hierarchy as a flattened list.
        
        :param container: A :py:class:`aspose.cad.fileformats.glb.IVisualNodeContainer` instance.
        :returns: A collection of :py:class:`aspose.cad.fileformats.glb.Node` instances.'''
        ...
    
    @staticmethod
    def find_nodes_using_mesh(mesh : aspose.cad.fileformats.collada.fileparser.elements.Mesh) -> Iterable[aspose.cad.fileformats.collada.fileparser.elements.Node]:
        '''Gets a collection of :py:class:`aspose.cad.fileformats.glb.Node` instances using ``mesh``.
        
        :param mesh: A :py:attr:`aspose.cad.fileformats.glb.Node.mesh` instance.
        :returns: A collection of :py:class:`aspose.cad.fileformats.glb.Node` instances.'''
        ...
    
    @staticmethod
    def find_nodes_using_skin(skin : aspose.cad.fileformats.glb.Skin) -> Iterable[aspose.cad.fileformats.collada.fileparser.elements.Node]:
        '''Gets a collection of :py:class:`aspose.cad.fileformats.glb.Node` instances using ``skin``.
        
        :param skin: A :py:attr:`aspose.cad.fileformats.glb.Node.skin` instance.
        :returns: A collection of :py:class:`aspose.cad.fileformats.glb.Node` instances.'''
        ...
    
    def get_curve_samplers(self, animation : aspose.cad.fileformats.glb.Animation) -> aspose.cad.fileformats.glb.NodeCurveSamplers:
        ...
    
    @property
    def extensions(self) -> List[aspose.cad.fileformats.glb.io.JsonSerializable]:
        '''Gets a collection of :py:class:`aspose.cad.fileformats.glb.io.JsonSerializable` instances.'''
        ...
    
    @property
    def extras(self) -> aspose.cad.fileformats.glb.io.JsonContent:
        '''Gets the extras content of this instance.'''
        ...
    
    @extras.setter
    def extras(self, value : aspose.cad.fileformats.glb.io.JsonContent):
        '''Sets the extras content of this instance.'''
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
    def logical_parent(self) -> aspose.cad.fileformats.glb.GlbData:
        ...
    
    @property
    def logical_index(self) -> int:
        ...
    
    @property
    def punctual_light(self) -> aspose.cad.fileformats.glb.PunctualLight:
        ...
    
    @punctual_light.setter
    def punctual_light(self, value : aspose.cad.fileformats.glb.PunctualLight):
        ...
    
    @property
    def visual_parent(self) -> aspose.cad.fileformats.collada.fileparser.elements.Node:
        ...
    
    @property
    def visual_root(self) -> aspose.cad.fileformats.collada.fileparser.elements.Node:
        ...
    
    @property
    def visual_scenes(self) -> Iterable[aspose.cad.fileformats.collada.fileparser.elements.Scene]:
        ...
    
    @property
    def visual_children(self) -> Iterable[aspose.cad.fileformats.collada.fileparser.elements.Node]:
        ...
    
    @property
    def is_skin_joint(self) -> bool:
        ...
    
    @property
    def is_skin_skeleton(self) -> bool:
        ...
    
    @property
    def camera(self) -> aspose.cad.fileformats.collada.fileparser.elements.Camera:
        '''Gets the :py:class:`aspose.cad.fileformats.glb.Camera` of this :py:class:`aspose.cad.fileformats.glb.Node`.'''
        ...
    
    @camera.setter
    def camera(self, value : aspose.cad.fileformats.collada.fileparser.elements.Camera):
        '''Sets the :py:class:`aspose.cad.fileformats.glb.Camera` of this :py:class:`aspose.cad.fileformats.glb.Node`.'''
        ...
    
    @property
    def mesh(self) -> aspose.cad.fileformats.collada.fileparser.elements.Mesh:
        '''Gets the :py:class:`aspose.cad.fileformats.glb.Mesh` of this :py:class:`aspose.cad.fileformats.glb.Node`.'''
        ...
    
    @mesh.setter
    def mesh(self, value : aspose.cad.fileformats.collada.fileparser.elements.Mesh):
        '''Sets the :py:class:`aspose.cad.fileformats.glb.Mesh` of this :py:class:`aspose.cad.fileformats.glb.Node`.'''
        ...
    
    @property
    def skin(self) -> aspose.cad.fileformats.glb.Skin:
        '''Gets the :py:class:`aspose.cad.fileformats.glb.Skin` of this :py:class:`aspose.cad.fileformats.glb.Node`.'''
        ...
    
    @skin.setter
    def skin(self, value : aspose.cad.fileformats.glb.Skin):
        '''Sets the :py:class:`aspose.cad.fileformats.glb.Skin` of this :py:class:`aspose.cad.fileformats.glb.Node`.'''
        ...
    
    @property
    def morph_weights(self) -> List[float]:
        ...
    
    @property
    def local_transform(self) -> aspose.cad.fileformats.glb.transforms.AffineTransform:
        ...
    
    @local_transform.setter
    def local_transform(self, value : aspose.cad.fileformats.glb.transforms.AffineTransform):
        ...
    
    @property
    def is_transform_animated(self) -> bool:
        ...
    
    ...

class NodeCurveSamplers:
    '''Represents an proxy to acccess the animation curves of a :py:class:`aspose.cad.fileformats.glb.Node`.
    Use :py:func:`aspose.cad.fileformats.glb.Node.get_curve_samplers` for access.'''
    
    def equals(self, other : aspose.cad.fileformats.glb.NodeCurveSamplers) -> bool:
        ...
    
    def get_local_transform(self, time : float) -> aspose.cad.fileformats.glb.transforms.AffineTransform:
        ...
    
    def get_sparse_morphing_weights(self, time : float) -> aspose.cad.fileformats.glb.transforms.SparseWeight8:
        ...
    
    @property
    def has_transform_curves(self) -> bool:
        ...
    
    @property
    def has_morphing_curves(self) -> bool:
        ...
    
    @property
    def TARGET_NODE(self) -> aspose.cad.fileformats.collada.fileparser.elements.Node:
        ...
    
    @property
    def ANIMATION(self) -> aspose.cad.fileformats.glb.Animation:
        ...
    
    ...

class PunctualLight(LogicalChildOfRoot):
    '''A directional, point, or spot light.'''
    
    def set_spot_cone(self, inner_cone_angle : float, outer_cone_angle : float) -> None:
        '''Sets the cone angles for the :py:attr:`aspose.cad.fileformats.glb.PunctualLightType.SPOT` light.
        
        :param inner_cone_angle: Gets the Angle, in radians, from centre of spotlight where falloff begins.
        Must be greater than or equal to 0 and less than outerConeAngle.
        :param outer_cone_angle: Gets Angle, in radians, from centre of spotlight where falloff ends.
        Must be greater than innerConeAngle and less than or equal to PI / 2.0.'''
        ...
    
    @property
    def extensions(self) -> List[aspose.cad.fileformats.glb.io.JsonSerializable]:
        '''Gets a collection of :py:class:`aspose.cad.fileformats.glb.io.JsonSerializable` instances.'''
        ...
    
    @property
    def extras(self) -> aspose.cad.fileformats.glb.io.JsonContent:
        '''Gets the extras content of this instance.'''
        ...
    
    @extras.setter
    def extras(self, value : aspose.cad.fileformats.glb.io.JsonContent):
        '''Sets the extras content of this instance.'''
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
    def logical_parent(self) -> aspose.cad.fileformats.glb.GlbData:
        ...
    
    @property
    def logical_index(self) -> int:
        ...
    
    @property
    def light_type(self) -> aspose.cad.fileformats.glb.PunctualLightType:
        ...
    
    @property
    def inner_cone_angle(self) -> float:
        ...
    
    @property
    def outer_cone_angle(self) -> float:
        ...
    
    @property
    def intensity(self) -> float:
        '''Gets the Brightness of light in. The units that this is defined in depend on the type of light.
        point and spot lights use luminous intensity in candela (lm/sr) while directional
        lights use illuminance in lux (lm/m2)'''
        ...
    
    @intensity.setter
    def intensity(self, value : float):
        '''Sets the Brightness of light in. The units that this is defined in depend on the type of light.
        point and spot lights use luminous intensity in candela (lm/sr) while directional
        lights use illuminance in lux (lm/m2)'''
        ...
    
    @property
    def range(self) -> float:
        '''Gets a Hint defining a distance cutoff at which the light's intensity may be considered
        to have reached zero. Supported only for point and spot lights.
        When undefined, range is assumed to be infinite.'''
        ...
    
    @range.setter
    def range(self, value : float):
        '''Sets a Hint defining a distance cutoff at which the light's intensity may be considered
        to have reached zero. Supported only for point and spot lights.
        When undefined, range is assumed to be infinite.'''
        ...
    
    ...

class ReadSettings:
    '''Read settings and base class of :py:class:`Aspose.CAD.FileFormats.GLB.ReadContext`'''
    
    def copy_to(self, other : aspose.cad.fileformats.glb.ReadSettings) -> None:
        ...
    
    @property
    def validation(self) -> aspose.cad.fileformats.glb.validation.ValidationMode:
        '''Gets a value indicating the level of validation applied when loading a file.'''
        ...
    
    @validation.setter
    def validation(self, value : aspose.cad.fileformats.glb.validation.ValidationMode):
        '''Sets a value indicating the level of validation applied when loading a file.'''
        ...
    
    ...

class Scene(LogicalChildOfRoot):
    '''The root nodes of a scene.'''
    
    def create_node(self, name : str) -> aspose.cad.fileformats.collada.fileparser.elements.Node:
        '''Creates a new :py:class:`aspose.cad.fileformats.glb.Node` instance,
        adds it to :py:attr:`aspose.cad.fileformats.glb.GlbData.logical_nodes`
        and references it as a child in the current graph.
        
        :param name: The name of the instance.
        :returns: A :py:class:`aspose.cad.fileformats.glb.Node` instance.'''
        ...
    
    @property
    def extensions(self) -> List[aspose.cad.fileformats.glb.io.JsonSerializable]:
        '''Gets a collection of :py:class:`aspose.cad.fileformats.glb.io.JsonSerializable` instances.'''
        ...
    
    @property
    def extras(self) -> aspose.cad.fileformats.glb.io.JsonContent:
        '''Gets the extras content of this instance.'''
        ...
    
    @extras.setter
    def extras(self, value : aspose.cad.fileformats.glb.io.JsonContent):
        '''Sets the extras content of this instance.'''
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
    def logical_parent(self) -> aspose.cad.fileformats.glb.GlbData:
        ...
    
    @property
    def logical_index(self) -> int:
        ...
    
    @property
    def visual_children(self) -> Iterable[aspose.cad.fileformats.collada.fileparser.elements.Node]:
        ...
    
    ...

class Skin(LogicalChildOfRoot):
    '''Joints and matrices defining a skin.'''
    
    def get_inverse_bind_matrices_accessor(self) -> aspose.cad.fileformats.collada.fileparser.elements.Accessor:
        ...
    
    def bind_joints(self, joints : List[aspose.cad.fileformats.collada.fileparser.elements.Node]) -> None:
        ...
    
    @property
    def extensions(self) -> List[aspose.cad.fileformats.glb.io.JsonSerializable]:
        '''Gets a collection of :py:class:`aspose.cad.fileformats.glb.io.JsonSerializable` instances.'''
        ...
    
    @property
    def extras(self) -> aspose.cad.fileformats.glb.io.JsonContent:
        '''Gets the extras content of this instance.'''
        ...
    
    @extras.setter
    def extras(self, value : aspose.cad.fileformats.glb.io.JsonContent):
        '''Sets the extras content of this instance.'''
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
    def logical_parent(self) -> aspose.cad.fileformats.glb.GlbData:
        ...
    
    @property
    def logical_index(self) -> int:
        ...
    
    @property
    def visual_parents(self) -> Iterable[aspose.cad.fileformats.collada.fileparser.elements.Node]:
        ...
    
    @property
    def joints_count(self) -> int:
        ...
    
    @property
    def skeleton(self) -> aspose.cad.fileformats.collada.fileparser.elements.Node:
        '''Gets the Skeleton :py:class:`aspose.cad.fileformats.glb.Node`, which represents the root of a joints hierarchy.'''
        ...
    
    @skeleton.setter
    def skeleton(self, value : aspose.cad.fileformats.collada.fileparser.elements.Node):
        '''Sets the Skeleton :py:class:`aspose.cad.fileformats.glb.Node`, which represents the root of a joints hierarchy.'''
        ...
    
    ...

class Texture(LogicalChildOfRoot):
    '''A texture and its sampler.'''
    
    def set_image(self, primary_image : aspose.cad.fileformats.glb.ImageGlb) -> None:
        ...
    
    def set_images(self, primary_image : aspose.cad.fileformats.glb.ImageGlb, fallback_image : aspose.cad.fileformats.glb.ImageGlb) -> None:
        ...
    
    def clear_images(self) -> None:
        ...
    
    @property
    def extensions(self) -> List[aspose.cad.fileformats.glb.io.JsonSerializable]:
        '''Gets a collection of :py:class:`aspose.cad.fileformats.glb.io.JsonSerializable` instances.'''
        ...
    
    @property
    def extras(self) -> aspose.cad.fileformats.glb.io.JsonContent:
        '''Gets the extras content of this instance.'''
        ...
    
    @extras.setter
    def extras(self, value : aspose.cad.fileformats.glb.io.JsonContent):
        '''Sets the extras content of this instance.'''
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
    def logical_parent(self) -> aspose.cad.fileformats.glb.GlbData:
        ...
    
    @property
    def logical_index(self) -> int:
        ...
    
    @property
    def sampler(self) -> aspose.cad.fileformats.glb.TextureSampler:
        ...
    
    @sampler.setter
    def sampler(self, value : aspose.cad.fileformats.glb.TextureSampler):
        ...
    
    @property
    def primary_image(self) -> aspose.cad.fileformats.glb.ImageGlb:
        ...
    
    @property
    def fallback_image(self) -> aspose.cad.fileformats.glb.ImageGlb:
        ...
    
    ...

class TextureSampler(LogicalChildOfRoot):
    '''Texture sampler properties for filtering and wrapping modes.'''
    
    @staticmethod
    def are_equal_by_content(x : aspose.cad.fileformats.glb.TextureSampler, y : aspose.cad.fileformats.glb.TextureSampler) -> bool:
        ...
    
    def get_content_hash_code(self) -> int:
        ...
    
    @property
    def extensions(self) -> List[aspose.cad.fileformats.glb.io.JsonSerializable]:
        '''Gets a collection of :py:class:`aspose.cad.fileformats.glb.io.JsonSerializable` instances.'''
        ...
    
    @property
    def extras(self) -> aspose.cad.fileformats.glb.io.JsonContent:
        '''Gets the extras content of this instance.'''
        ...
    
    @extras.setter
    def extras(self, value : aspose.cad.fileformats.glb.io.JsonContent):
        '''Sets the extras content of this instance.'''
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
    def logical_parent(self) -> aspose.cad.fileformats.glb.GlbData:
        ...
    
    @property
    def logical_index(self) -> int:
        ...
    
    @property
    def min_filter(self) -> aspose.cad.fileformats.glb.TextureMipMapFilter:
        ...
    
    @property
    def mag_filter(self) -> aspose.cad.fileformats.glb.TextureInterpolationFilter:
        ...
    
    @property
    def wrap_s(self) -> aspose.cad.fileformats.glb.TextureWrapMode:
        ...
    
    @property
    def wrap_t(self) -> aspose.cad.fileformats.glb.TextureWrapMode:
        ...
    
    ...

class TextureTransform(ExtraProperties):
    '''glTF extension that enables shifting and scaling UV coordinates on a per-texture basis'''
    
    @property
    def extensions(self) -> List[aspose.cad.fileformats.glb.io.JsonSerializable]:
        '''Gets a collection of :py:class:`aspose.cad.fileformats.glb.io.JsonSerializable` instances.'''
        ...
    
    @property
    def extras(self) -> aspose.cad.fileformats.glb.io.JsonContent:
        '''Gets the extras content of this instance.'''
        ...
    
    @extras.setter
    def extras(self, value : aspose.cad.fileformats.glb.io.JsonContent):
        '''Sets the extras content of this instance.'''
        ...
    
    @property
    def rotation(self) -> float:
        ...
    
    @rotation.setter
    def rotation(self, value : float):
        ...
    
    @property
    def texture_coordinate_override(self) -> Optional[int]:
        ...
    
    @texture_coordinate_override.setter
    def texture_coordinate_override(self, value : Optional[int]):
        ...
    
    ...

class ValueLocationTuple:
    
    ...

class VertexColor2Texture2Tuple:
    
    ...

class VertexColor2TextureTuple:
    
    ...

class VertexColorTexture2Tuple:
    
    ...

class VertexColorTextureTuple:
    
    ...

class VertexGeometryTuple:
    
    ...

class VertexTextureTuple:
    
    ...

class WriteSettings:
    '''Write settings and base class of :py:class:`Aspose.CAD.FileFormats.GLB.WriteContext`'''
    
    def copy_to(self, other : aspose.cad.fileformats.glb.WriteSettings) -> None:
        ...
    
    @property
    def image_writing(self) -> aspose.cad.fileformats.glb.ResourceWriteMode:
        ...
    
    @image_writing.setter
    def image_writing(self, value : aspose.cad.fileformats.glb.ResourceWriteMode):
        ...
    
    @property
    def merge_buffers(self) -> bool:
        ...
    
    @merge_buffers.setter
    def merge_buffers(self, value : bool):
        ...
    
    @property
    def buffers_max_size(self) -> int:
        ...
    
    @buffers_max_size.setter
    def buffers_max_size(self, value : int):
        ...
    
    @property
    def json_indented(self) -> bool:
        ...
    
    @json_indented.setter
    def json_indented(self, value : bool):
        ...
    
    @property
    def validation(self) -> aspose.cad.fileformats.glb.validation.ValidationMode:
        '''Gets a value indicating the level of validation applied when loading a file.'''
        ...
    
    @validation.setter
    def validation(self, value : aspose.cad.fileformats.glb.validation.ValidationMode):
        '''Sets a value indicating the level of validation applied when loading a file.'''
        ...
    
    ...

class AgiArticulationTransformType:
    '''The type of motion applied by this articulation stage.'''
    
    @classmethod
    @property
    def X_TRANSLATE(cls) -> AgiArticulationTransformType:
        ...
    
    @classmethod
    @property
    def Y_TRANSLATE(cls) -> AgiArticulationTransformType:
        ...
    
    @classmethod
    @property
    def Z_TRANSLATE(cls) -> AgiArticulationTransformType:
        ...
    
    @classmethod
    @property
    def X_ROTATE(cls) -> AgiArticulationTransformType:
        ...
    
    @classmethod
    @property
    def Y_ROTATE(cls) -> AgiArticulationTransformType:
        ...
    
    @classmethod
    @property
    def Z_ROTATE(cls) -> AgiArticulationTransformType:
        ...
    
    @classmethod
    @property
    def X_SCALE(cls) -> AgiArticulationTransformType:
        ...
    
    @classmethod
    @property
    def Y_SCALE(cls) -> AgiArticulationTransformType:
        ...
    
    @classmethod
    @property
    def Z_SCALE(cls) -> AgiArticulationTransformType:
        ...
    
    @classmethod
    @property
    def UNIFORM_SCALE(cls) -> AgiArticulationTransformType:
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

class AnimationInterpolationMode:
    '''Interpolation algorithm.'''
    
    @classmethod
    @property
    def LINEAR(cls) -> AnimationInterpolationMode:
        ...
    
    @classmethod
    @property
    def STEP(cls) -> AnimationInterpolationMode:
        ...
    
    @classmethod
    @property
    def CUBICSPLINE(cls) -> AnimationInterpolationMode:
        ...
    
    ...

class BufferMode:
    '''The hint representing the intended GPU buffer type to use with this buffer view.'''
    
    @classmethod
    @property
    def ARRAY_BUFFER(cls) -> BufferMode:
        ...
    
    @classmethod
    @property
    def ELEMENT_ARRAY_BUFFER(cls) -> BufferMode:
        ...
    
    ...

class CameraType:
    '''Specifies if the camera uses a perspective or orthographic projection.'''
    
    @classmethod
    @property
    def PERSPECTIVE(cls) -> CameraType:
        ...
    
    @classmethod
    @property
    def ORTHOGRAPHIC(cls) -> CameraType:
        ...
    
    ...

class DimensionType:
    '''Specifies if the accessor's elements are scalars, vectors, or matrices.'''
    
    @classmethod
    @property
    def SCALAR(cls) -> DimensionType:
        ...
    
    @classmethod
    @property
    def VEC2(cls) -> DimensionType:
        ...
    
    @classmethod
    @property
    def VEC3(cls) -> DimensionType:
        ...
    
    @classmethod
    @property
    def VEC4(cls) -> DimensionType:
        ...
    
    @classmethod
    @property
    def MAT2(cls) -> DimensionType:
        ...
    
    @classmethod
    @property
    def MAT3(cls) -> DimensionType:
        ...
    
    @classmethod
    @property
    def MAT4(cls) -> DimensionType:
        ...
    
    @classmethod
    @property
    def CUSTOM(cls) -> DimensionType:
        ...
    
    ...

class EncodingType:
    '''The datatype of the accessor's components.'''
    
    @classmethod
    @property
    def BYTE(cls) -> EncodingType:
        ...
    
    @classmethod
    @property
    def UNSIGNED_BYTE(cls) -> EncodingType:
        ...
    
    @classmethod
    @property
    def SHORT(cls) -> EncodingType:
        ...
    
    @classmethod
    @property
    def UNSIGNED_SHORT(cls) -> EncodingType:
        ...
    
    @classmethod
    @property
    def UNSIGNED_INT(cls) -> EncodingType:
        ...
    
    @classmethod
    @property
    def FLOAT(cls) -> EncodingType:
        ...
    
    ...

class IndexEncodingType:
    '''The indices data type.'''
    
    @classmethod
    @property
    def UNSIGNED_BYTE(cls) -> IndexEncodingType:
        ...
    
    @classmethod
    @property
    def UNSIGNED_SHORT(cls) -> IndexEncodingType:
        ...
    
    @classmethod
    @property
    def UNSIGNED_INT(cls) -> IndexEncodingType:
        ...
    
    ...

class PrimitiveType:
    '''The topology type of primitives to render.'''
    
    @classmethod
    @property
    def POINTS(cls) -> PrimitiveType:
        ...
    
    @classmethod
    @property
    def LINES(cls) -> PrimitiveType:
        ...
    
    @classmethod
    @property
    def LINE_LOOP(cls) -> PrimitiveType:
        ...
    
    @classmethod
    @property
    def LINE_STRIP(cls) -> PrimitiveType:
        ...
    
    @classmethod
    @property
    def TRIANGLES(cls) -> PrimitiveType:
        ...
    
    @classmethod
    @property
    def TRIANGLE_STRIP(cls) -> PrimitiveType:
        ...
    
    @classmethod
    @property
    def TRIANGLE_FAN(cls) -> PrimitiveType:
        ...
    
    ...

class PropertyPath:
    '''The name of the node's TRS property to animate, or the :py:attr:`aspose.cad.fileformats.glb.PropertyPath.WEIGHTS` of the Morph Targets it instantiates. For the :py:attr:`aspose.cad.fileformats.glb.PropertyPath.TRANSLATION` property, the values that are provided by the sampler are the translation along the X, Y, and Z axes. For the :py:attr:`aspose.cad.fileformats.glb.PropertyPath.ROTATION` property, the values are a quaternion in the order (x, y, z, w), where w is the scalar. For the :py:attr:`aspose.cad.fileformats.glb.PropertyPath.SCALE` property, the values are the scaling factors along the X, Y, and Z axes.'''
    
    @classmethod
    @property
    def TRANSLATION(cls) -> PropertyPath:
        ...
    
    @classmethod
    @property
    def ROTATION(cls) -> PropertyPath:
        ...
    
    @classmethod
    @property
    def SCALE(cls) -> PropertyPath:
        ...
    
    @classmethod
    @property
    def WEIGHTS(cls) -> PropertyPath:
        ...
    
    ...

class PunctualLightType:
    '''Defines all the types of :py:class:`aspose.cad.fileformats.glb.PunctualLight` types.'''
    
    @classmethod
    @property
    def DIRECTIONAL(cls) -> PunctualLightType:
        ...
    
    @classmethod
    @property
    def POINT(cls) -> PunctualLightType:
        ...
    
    @classmethod
    @property
    def SPOT(cls) -> PunctualLightType:
        ...
    
    ...

class ResourceWriteMode:
    '''Determines how resources are written.'''
    
    @classmethod
    @property
    def DEFAULT(cls) -> ResourceWriteMode:
        '''Use the most appropiate mode.'''
        ...
    
    @classmethod
    @property
    def SATELLITE_FILE(cls) -> ResourceWriteMode:
        '''Resources will be stored as external satellite files.'''
        ...
    
    @classmethod
    @property
    def EMBEDDED_AS_BASE64(cls) -> ResourceWriteMode:
        '''Resources will be embedded into the JSON encoded in Base64.'''
        ...
    
    @classmethod
    @property
    def BUFFER_VIEW(cls) -> ResourceWriteMode:
        '''Resources will be stored as internal binary buffers. Valid only for :py:class:`aspose.cad.fileformats.glb.ImageGlb`'''
        ...
    
    ...

class TextureInterpolationFilter:
    '''Magnification filter.'''
    
    @classmethod
    @property
    def NEAREST(cls) -> TextureInterpolationFilter:
        ...
    
    @classmethod
    @property
    def LINEAR(cls) -> TextureInterpolationFilter:
        ...
    
    @classmethod
    @property
    def DEFAULT(cls) -> TextureInterpolationFilter:
        ...
    
    ...

class TextureMipMapFilter:
    '''Minification filter.'''
    
    @classmethod
    @property
    def NEAREST(cls) -> TextureMipMapFilter:
        ...
    
    @classmethod
    @property
    def LINEAR(cls) -> TextureMipMapFilter:
        ...
    
    @classmethod
    @property
    def NEAREST_MIPMAP_NEAREST(cls) -> TextureMipMapFilter:
        ...
    
    @classmethod
    @property
    def LINEAR_MIPMAP_NEAREST(cls) -> TextureMipMapFilter:
        ...
    
    @classmethod
    @property
    def NEAREST_MIPMAP_LINEAR(cls) -> TextureMipMapFilter:
        ...
    
    @classmethod
    @property
    def LINEAR_MIPMAP_LINEAR(cls) -> TextureMipMapFilter:
        ...
    
    @classmethod
    @property
    def DEFAULT(cls) -> TextureMipMapFilter:
        ...
    
    ...

class TextureWrapMode:
    '''T (V) wrapping mode.'''
    
    @classmethod
    @property
    def CLAMP_TO_EDGE(cls) -> TextureWrapMode:
        ...
    
    @classmethod
    @property
    def MIRRORED_REPEAT(cls) -> TextureWrapMode:
        ...
    
    @classmethod
    @property
    def REPEAT(cls) -> TextureWrapMode:
        ...
    
    ...

