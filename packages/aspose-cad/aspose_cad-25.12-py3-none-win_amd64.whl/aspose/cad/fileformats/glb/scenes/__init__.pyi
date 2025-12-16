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

class CameraBuilder(aspose.cad.fileformats.glb.geometry.BaseBuilder):
    '''Represents an camera object.'''
    
    def clone(self) -> aspose.cad.fileformats.glb.scenes.CameraBuilder:
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
    def z_near(self) -> float:
        ...
    
    @z_near.setter
    def z_near(self, value : float):
        ...
    
    @property
    def z_far(self) -> float:
        ...
    
    @z_far.setter
    def z_far(self, value : float):
        ...
    
    @property
    def is_valid(self) -> bool:
        ...
    
    ...

class ContentTransformer:
    '''Represents the transform of a :py:attr:`aspose.cad.fileformats.glb.scenes.InstanceBuilder.content`.
    
    Applies a transform to the underlaying content object (usually a Mesh, a Camera or a light)'''
    
    def deep_clone(self, args : ContentTransformer.DeepCloneContext) -> aspose.cad.fileformats.glb.scenes.ContentTransformer:
        ...
    
    def get_camera_asset(self) -> aspose.cad.fileformats.glb.scenes.CameraBuilder:
        '''It this :py:class:`aspose.cad.fileformats.glb.scenes.ContentTransformer` contains a :py:class:`aspose.cad.fileformats.glb.scenes.CameraBuilder`
        
        :returns: A :py:class:`aspose.cad.fileformats.glb.scenes.CameraBuilder` instance, or NULL.'''
        ...
    
    def get_light_asset(self) -> aspose.cad.fileformats.glb.scenes.LightBuilder:
        '''It this :py:class:`aspose.cad.fileformats.glb.scenes.ContentTransformer` contains a :py:class:`aspose.cad.fileformats.glb.scenes.LightBuilder`
        
        :returns: A :py:class:`aspose.cad.fileformats.glb.scenes.LightBuilder` instance, or NULL.'''
        ...
    
    def get_armature_root(self) -> aspose.cad.fileformats.glb.scenes.NodeBuilder:
        '''If this :py:class:`aspose.cad.fileformats.glb.scenes.ContentTransformer` uses a :py:class:`aspose.cad.fileformats.glb.scenes.NodeBuilder` armature, it returns the root of the armature.
        
        :returns: A :py:class:`aspose.cad.fileformats.glb.scenes.NodeBuilder` instance, or NULL.'''
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
    def has_renderable_content(self) -> bool:
        ...
    
    ...

class FixedTransformer(ContentTransformer):
    '''Represents the transform of a :py:attr:`aspose.cad.fileformats.glb.scenes.InstanceBuilder.content`.
    
    Applies a fixed :py:class:`System.Numerics.Matrix4x4` transform to the underlaying content.'''
    
    def deep_clone(self, args : ContentTransformer.DeepCloneContext) -> aspose.cad.fileformats.glb.scenes.ContentTransformer:
        ...
    
    def get_camera_asset(self) -> aspose.cad.fileformats.glb.scenes.CameraBuilder:
        '''It this :py:class:`aspose.cad.fileformats.glb.scenes.ContentTransformer` contains a :py:class:`aspose.cad.fileformats.glb.scenes.CameraBuilder`
        
        :returns: A :py:class:`aspose.cad.fileformats.glb.scenes.CameraBuilder` instance, or NULL.'''
        ...
    
    def get_light_asset(self) -> aspose.cad.fileformats.glb.scenes.LightBuilder:
        '''It this :py:class:`aspose.cad.fileformats.glb.scenes.ContentTransformer` contains a :py:class:`aspose.cad.fileformats.glb.scenes.LightBuilder`
        
        :returns: A :py:class:`aspose.cad.fileformats.glb.scenes.LightBuilder` instance, or NULL.'''
        ...
    
    def get_armature_root(self) -> aspose.cad.fileformats.glb.scenes.NodeBuilder:
        '''If this :py:class:`aspose.cad.fileformats.glb.scenes.ContentTransformer` uses a :py:class:`aspose.cad.fileformats.glb.scenes.NodeBuilder` armature, it returns the root of the armature.
        
        :returns: A :py:class:`aspose.cad.fileformats.glb.scenes.NodeBuilder` instance, or NULL.'''
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
    def has_renderable_content(self) -> bool:
        ...
    
    @property
    def parent_node(self) -> aspose.cad.fileformats.glb.scenes.NodeBuilder:
        ...
    
    @property
    def child_transform(self) -> aspose.cad.fileformats.glb.transforms.AffineTransform:
        ...
    
    @child_transform.setter
    def child_transform(self, value : aspose.cad.fileformats.glb.transforms.AffineTransform):
        ...
    
    ...

class InstanceBuilder:
    '''Represents an element within :py:attr:`aspose.cad.fileformats.glb.scenes.SceneBuilder.instances`'''
    
    def with_name(self, name : str) -> aspose.cad.fileformats.glb.scenes.InstanceBuilder:
        ...
    
    def with_extras(self, extras : aspose.cad.fileformats.glb.io.JsonContent) -> aspose.cad.fileformats.glb.scenes.InstanceBuilder:
        ...
    
    def remove(self) -> None:
        '''Removes this instance from its parent :py:class:`aspose.cad.fileformats.glb.scenes.SceneBuilder`.'''
        ...
    
    @property
    def name(self) -> str:
        '''Gets the display text name of this object, or null.
        
        **⚠️ DO NOT USE AS AN OBJECT ID ⚠️** see remarks.'''
        ...
    
    @property
    def extras(self) -> aspose.cad.fileformats.glb.io.JsonContent:
        '''Gets the custom data of this object.'''
        ...
    
    @property
    def content(self) -> aspose.cad.fileformats.glb.scenes.ContentTransformer:
        '''Gets the content of this instance.
        
        It can be one of those types:
        
        - :py:class:`aspose.cad.fileformats.glb.scenes.FixedTransformer`
        
        - :py:class:`aspose.cad.fileformats.glb.scenes.RigidTransformer`
        
        - :py:class:`aspose.cad.fileformats.glb.scenes.SkinnedTransformer`'''
        ...
    
    @content.setter
    def content(self, value : aspose.cad.fileformats.glb.scenes.ContentTransformer):
        '''Sets the content of this instance.
        
        It can be one of those types:
        
        - :py:class:`aspose.cad.fileformats.glb.scenes.FixedTransformer`
        
        - :py:class:`aspose.cad.fileformats.glb.scenes.RigidTransformer`
        
        - :py:class:`aspose.cad.fileformats.glb.scenes.SkinnedTransformer`'''
        ...
    
    @property
    def materials(self) -> Iterable[aspose.cad.fileformats.glb.materials.MaterialBuilder]:
        '''Gets the materials used by :py:attr:`aspose.cad.fileformats.glb.scenes.InstanceBuilder.content`.'''
        ...
    
    ...

class LightBuilder(aspose.cad.fileformats.glb.geometry.BaseBuilder):
    '''Represents the base class light object.'''
    
    def clone(self) -> aspose.cad.fileformats.glb.scenes.LightBuilder:
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
    def intensity(self) -> float:
        '''Gets the Brightness of light in.
        
        The units that this is defined in depend on the type of light.
        
        Point and spot lights use luminous intensity in candela (lm/sr)
        while directional lights use illuminance in lux (lm/m2)'''
        ...
    
    @intensity.setter
    def intensity(self, value : float):
        '''Sets the Brightness of light in.
        
        The units that this is defined in depend on the type of light.
        
        Point and spot lights use luminous intensity in candela (lm/sr)
        while directional lights use illuminance in lux (lm/m2)'''
        ...
    
    ...

class NodeBuilder(aspose.cad.fileformats.glb.geometry.BaseBuilder):
    '''Defines a node object within an armature.'''
    
    def create_node(self, name : str) -> aspose.cad.fileformats.glb.scenes.NodeBuilder:
        ...
    
    def add_node(self, node : aspose.cad.fileformats.glb.scenes.NodeBuilder) -> None:
        ...
    
    @staticmethod
    def is_valid_armature(joints : Iterable[aspose.cad.fileformats.glb.scenes.NodeBuilder]) -> bool:
        ...
    
    @staticmethod
    def flatten(container : aspose.cad.fileformats.glb.scenes.NodeBuilder) -> Iterable[aspose.cad.fileformats.glb.scenes.NodeBuilder]:
        ...
    
    def get_local_transform(self, animation_track : str, time : float) -> aspose.cad.fileformats.glb.transforms.AffineTransform:
        ...
    
    def set_local_transform(self, new_local_transform : aspose.cad.fileformats.glb.transforms.AffineTransform, keep_children_in_place : bool) -> None:
        '''Sets the local transform of this node.
        Optionally it is possible keep children from being affected by this node transformation change.
        
        :param new_local_transform: the new local transform
        :param keep_children_in_place: true to keep children in their world positions.'''
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
    def parent(self) -> aspose.cad.fileformats.glb.scenes.NodeBuilder:
        ...
    
    @property
    def root(self) -> aspose.cad.fileformats.glb.scenes.NodeBuilder:
        ...
    
    @property
    def visual_children(self) -> List[aspose.cad.fileformats.glb.scenes.NodeBuilder]:
        ...
    
    @property
    def animation_tracks_names(self) -> Iterable[str]:
        ...
    
    @property
    def has_animations(self) -> bool:
        ...
    
    @property
    def local_transform(self) -> aspose.cad.fileformats.glb.transforms.AffineTransform:
        ...
    
    @local_transform.setter
    def local_transform(self, value : aspose.cad.fileformats.glb.transforms.AffineTransform):
        ...
    
    ...

class RigidTransformer(ContentTransformer):
    '''Represents the transform of a :py:attr:`aspose.cad.fileformats.glb.scenes.InstanceBuilder.content`.
    
    Applies the transform of a single :py:class:`aspose.cad.fileformats.glb.scenes.NodeBuilder` to the underlaying content.'''
    
    def deep_clone(self, args : ContentTransformer.DeepCloneContext) -> aspose.cad.fileformats.glb.scenes.ContentTransformer:
        ...
    
    def get_camera_asset(self) -> aspose.cad.fileformats.glb.scenes.CameraBuilder:
        '''It this :py:class:`aspose.cad.fileformats.glb.scenes.ContentTransformer` contains a :py:class:`aspose.cad.fileformats.glb.scenes.CameraBuilder`
        
        :returns: A :py:class:`aspose.cad.fileformats.glb.scenes.CameraBuilder` instance, or NULL.'''
        ...
    
    def get_light_asset(self) -> aspose.cad.fileformats.glb.scenes.LightBuilder:
        '''It this :py:class:`aspose.cad.fileformats.glb.scenes.ContentTransformer` contains a :py:class:`aspose.cad.fileformats.glb.scenes.LightBuilder`
        
        :returns: A :py:class:`aspose.cad.fileformats.glb.scenes.LightBuilder` instance, or NULL.'''
        ...
    
    def get_armature_root(self) -> aspose.cad.fileformats.glb.scenes.NodeBuilder:
        '''If this :py:class:`aspose.cad.fileformats.glb.scenes.ContentTransformer` uses a :py:class:`aspose.cad.fileformats.glb.scenes.NodeBuilder` armature, it returns the root of the armature.
        
        :returns: A :py:class:`aspose.cad.fileformats.glb.scenes.NodeBuilder` instance, or NULL.'''
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
    def has_renderable_content(self) -> bool:
        ...
    
    @property
    def transform(self) -> aspose.cad.fileformats.glb.scenes.NodeBuilder:
        ...
    
    @transform.setter
    def transform(self, value : aspose.cad.fileformats.glb.scenes.NodeBuilder):
        ...
    
    ...

class SceneBuilder(aspose.cad.fileformats.glb.geometry.BaseBuilder):
    '''Represents the root scene for models, cameras and lights.'''
    
    @overload
    def add_camera(self, camera : aspose.cad.fileformats.glb.scenes.CameraBuilder, node : aspose.cad.fileformats.glb.scenes.NodeBuilder) -> aspose.cad.fileformats.glb.scenes.InstanceBuilder:
        ...
    
    @overload
    def add_camera(self, camera : aspose.cad.fileformats.glb.scenes.CameraBuilder, camera_transform : aspose.cad.fileformats.glb.transforms.AffineTransform) -> aspose.cad.fileformats.glb.scenes.InstanceBuilder:
        ...
    
    @overload
    def add_light(self, light : aspose.cad.fileformats.glb.scenes.LightBuilder, light_transform : aspose.cad.fileformats.glb.transforms.AffineTransform) -> aspose.cad.fileformats.glb.scenes.InstanceBuilder:
        ...
    
    @overload
    def add_light(self, light : aspose.cad.fileformats.glb.scenes.LightBuilder, node : aspose.cad.fileformats.glb.scenes.NodeBuilder) -> aspose.cad.fileformats.glb.scenes.InstanceBuilder:
        ...
    
    @overload
    def to_gltf2(self) -> aspose.cad.fileformats.glb.GlbData:
        '''Converts this :py:class:`aspose.cad.fileformats.glb.scenes.SceneBuilder` instance into a :py:class:`aspose.cad.fileformats.glb.GlbImage` instance.
        
        :returns: A new :py:class:`aspose.cad.fileformats.glb.GlbImage` instance.'''
        ...
    
    @overload
    def to_gltf2(self, settings : aspose.cad.fileformats.glb.scenes.SceneBuilderSchema2Settings) -> aspose.cad.fileformats.glb.GlbData:
        '''Converts this :py:class:`aspose.cad.fileformats.glb.scenes.SceneBuilder` instance into a :py:class:`aspose.cad.fileformats.glb.GlbImage` instance.
        
        :param settings: Conversion settings.
        :returns: A new :py:class:`aspose.cad.fileformats.glb.GlbImage` instance.'''
        ...
    
    @overload
    @staticmethod
    def to_gltf2(src_scenes : Iterable[aspose.cad.fileformats.glb.scenes.SceneBuilder], settings : aspose.cad.fileformats.glb.scenes.SceneBuilderSchema2Settings) -> aspose.cad.fileformats.glb.GlbData:
        ...
    
    @overload
    @staticmethod
    def create_from(model : aspose.cad.fileformats.glb.GlbData) -> List[aspose.cad.fileformats.glb.scenes.SceneBuilder]:
        ...
    
    @overload
    @staticmethod
    def create_from(src_scene : aspose.cad.fileformats.collada.fileparser.elements.Scene) -> aspose.cad.fileformats.glb.scenes.SceneBuilder:
        ...
    
    @overload
    @staticmethod
    def create_from(src_scenes : Iterable[aspose.cad.fileformats.collada.fileparser.elements.Scene]) -> Iterable[aspose.cad.fileformats.glb.scenes.SceneBuilder]:
        ...
    
    def deep_clone(self, clone_armatures : bool) -> aspose.cad.fileformats.glb.scenes.SceneBuilder:
        ...
    
    @staticmethod
    def load_default_scene(file_path : str, settings : aspose.cad.fileformats.glb.ReadSettings) -> aspose.cad.fileformats.glb.scenes.SceneBuilder:
        ...
    
    @staticmethod
    def load_all_scenes(file_path : str, settings : aspose.cad.fileformats.glb.ReadSettings) -> List[aspose.cad.fileformats.glb.scenes.SceneBuilder]:
        ...
    
    def add_node(self, node : aspose.cad.fileformats.glb.scenes.NodeBuilder) -> aspose.cad.fileformats.glb.scenes.InstanceBuilder:
        ...
    
    def find_armatures(self) -> List[aspose.cad.fileformats.glb.scenes.NodeBuilder]:
        '''Gets all the unique armatures used by this :py:class:`aspose.cad.fileformats.glb.scenes.SceneBuilder`.
        
        :returns: A collection of :py:class:`aspose.cad.fileformats.glb.scenes.NodeBuilder` objects representing the root of each armature.'''
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
    def instances(self) -> List[aspose.cad.fileformats.glb.scenes.InstanceBuilder]:
        '''Gets all the instances in this scene.'''
        ...
    
    @property
    def materials(self) -> Iterable[aspose.cad.fileformats.glb.materials.MaterialBuilder]:
        '''Gets all the unique material references shared by all the meshes in this scene.'''
        ...
    
    ...

class SceneBuilderSchema2Settings:
    '''Defines configurable options for converting :py:class:`aspose.cad.fileformats.glb.scenes.SceneBuilder` to :py:class:`aspose.cad.fileformats.glb.GlbImage`'''
    
    @classmethod
    @property
    def default(cls) -> aspose.cad.fileformats.glb.scenes.SceneBuilderSchema2Settings:
        ...
    
    @classmethod
    @property
    def with_gpu_instancing(cls) -> aspose.cad.fileformats.glb.scenes.SceneBuilderSchema2Settings:
        ...
    
    @property
    def use_strided_buffers(self) -> bool:
        ...
    
    @use_strided_buffers.setter
    def use_strided_buffers(self, value : bool):
        ...
    
    @property
    def compact_vertex_weights(self) -> bool:
        ...
    
    @compact_vertex_weights.setter
    def compact_vertex_weights(self, value : bool):
        ...
    
    @property
    def gpu_mesh_instancing_min_count(self) -> int:
        ...
    
    @gpu_mesh_instancing_min_count.setter
    def gpu_mesh_instancing_min_count(self, value : int):
        ...
    
    @property
    def merge_buffers(self) -> bool:
        ...
    
    @merge_buffers.setter
    def merge_buffers(self, value : bool):
        ...
    
    ...

class SkinnedTransformer(ContentTransformer):
    '''Represents the transform of a :py:attr:`aspose.cad.fileformats.glb.scenes.InstanceBuilder.content`.
    
    Applies the transforms of many :py:class:`aspose.cad.fileformats.glb.scenes.NodeBuilder` to the underlaying content.'''
    
    def deep_clone(self, args : ContentTransformer.DeepCloneContext) -> aspose.cad.fileformats.glb.scenes.ContentTransformer:
        ...
    
    def get_camera_asset(self) -> aspose.cad.fileformats.glb.scenes.CameraBuilder:
        '''It this :py:class:`aspose.cad.fileformats.glb.scenes.ContentTransformer` contains a :py:class:`aspose.cad.fileformats.glb.scenes.CameraBuilder`
        
        :returns: A :py:class:`aspose.cad.fileformats.glb.scenes.CameraBuilder` instance, or NULL.'''
        ...
    
    def get_light_asset(self) -> aspose.cad.fileformats.glb.scenes.LightBuilder:
        '''It this :py:class:`aspose.cad.fileformats.glb.scenes.ContentTransformer` contains a :py:class:`aspose.cad.fileformats.glb.scenes.LightBuilder`
        
        :returns: A :py:class:`aspose.cad.fileformats.glb.scenes.LightBuilder` instance, or NULL.'''
        ...
    
    def get_armature_root(self) -> aspose.cad.fileformats.glb.scenes.NodeBuilder:
        '''If this :py:class:`aspose.cad.fileformats.glb.scenes.ContentTransformer` uses a :py:class:`aspose.cad.fileformats.glb.scenes.NodeBuilder` armature, it returns the root of the armature.
        
        :returns: A :py:class:`aspose.cad.fileformats.glb.scenes.NodeBuilder` instance, or NULL.'''
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
    def has_renderable_content(self) -> bool:
        ...
    
    ...

class TransformChainBuilder:
    
    @property
    def parent(self) -> aspose.cad.fileformats.glb.scenes.NodeBuilder:
        ...
    
    @property
    def child(self) -> Optional[aspose.cad.fileformats.glb.transforms.AffineTransform]:
        ...
    
    ...

