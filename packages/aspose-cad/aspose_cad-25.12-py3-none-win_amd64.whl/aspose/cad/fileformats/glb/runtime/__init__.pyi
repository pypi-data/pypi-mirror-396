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

class AnimationTrackInfo:
    
    @property
    def name(self) -> str:
        ...
    
    @property
    def extras(self) -> any:
        ...
    
    @property
    def duration(self) -> float:
        ...
    
    ...

class ArmatureInstance:
    '''Represents the transform states of a collection of bones.'''
    
    def set_pose_transforms(self) -> None:
        '''Resets the bone transforms to their default positions.'''
        ...
    
    def set_animation_frame(self, track_logical_index : int, time : float, looped : bool) -> None:
        '''Sets the bone transforms from an animation frame.
        
        :param track_logical_index: The animation track index.
        :param time: The animation time frame.
        :param looped: True to use the animation as a looped animation.'''
        ...
    
    @property
    def logical_nodes(self) -> List[aspose.cad.fileformats.glb.runtime.NodeInstance]:
        ...
    
    @property
    def visual_nodes(self) -> Iterable[aspose.cad.fileformats.glb.runtime.NodeInstance]:
        ...
    
    @property
    def animation_tracks(self) -> List[aspose.cad.fileformats.glb.runtime.AnimationTrackInfo]:
        ...
    
    ...

class DrawableInstance:
    
    @property
    def instance_count(self) -> int:
        ...
    
    @property
    def TEMPLATE(self) -> aspose.cad.fileformats.glb.runtime.IDrawableTemplate:
        '''Represents WHAT to draw.'''
        ...
    
    ...

class IDrawableTemplate:
    
    @property
    def node_name(self) -> str:
        ...
    
    @property
    def logical_mesh_index(self) -> int:
        ...
    
    ...

class NodeInstance:
    '''Defines a node of a scene graph in :py:class:`aspose.cad.fileformats.glb.runtime.SceneInstance`'''
    
    @overload
    def set_animation_frame(self, track_logical_index : int, time : float) -> None:
        ...
    
    @overload
    def set_animation_frame(self, track : List[int], time : List[float], weight : List[float]) -> None:
        ...
    
    def set_pose_transform(self) -> None:
        ...
    
    @property
    def name(self) -> str:
        ...
    
    @property
    def extras(self) -> any:
        ...
    
    @property
    def visual_parent(self) -> aspose.cad.fileformats.glb.runtime.NodeInstance:
        ...
    
    @property
    def morph_weights(self) -> aspose.cad.fileformats.glb.transforms.SparseWeight8:
        ...
    
    @morph_weights.setter
    def morph_weights(self, value : aspose.cad.fileformats.glb.transforms.SparseWeight8):
        ...
    
    ...

class RuntimeOptions:
    
    @property
    def isolate_memory(self) -> bool:
        ...
    
    @isolate_memory.setter
    def isolate_memory(self, value : bool):
        ...
    
    @property
    def gpu_mesh_instancing(self) -> aspose.cad.fileformats.glb.runtime.MeshInstancing:
        ...
    
    @gpu_mesh_instancing.setter
    def gpu_mesh_instancing(self, value : aspose.cad.fileformats.glb.runtime.MeshInstancing):
        ...
    
    ...

class SceneInstance:
    '''Represents a specific and independent state of a :py:class:`Aspose.CAD.FileFormats.GLB.Runtime.SceneTemplate`.'''
    
    def get_drawable_instance(self, index : int) -> aspose.cad.fileformats.glb.runtime.DrawableInstance:
        '''Gets a :py:class:`aspose.cad.fileformats.glb.runtime.DrawableInstance` object, where:
        - Name is the name of this drawable instance. Originally, it was the name of :py:class:`aspose.cad.fileformats.glb.Node`.
        - MeshIndex is the logical Index of a :py:class:`aspose.cad.fileformats.glb.Mesh` in :py:attr:`aspose.cad.fileformats.glb.GlbData.logical_meshes`.
        - Transform is an :py:class:`Aspose.CAD.FileFormats.GLB.Transforms.IGeometryTransform` that can be used to transform the :py:class:`aspose.cad.fileformats.glb.Mesh` into world space.
        
        :param index: The index of the drawable reference, from 0 to :py:attr:`aspose.cad.fileformats.glb.runtime.SceneInstance.DrawableInstancesCount`
        :returns: :py:class:`aspose.cad.fileformats.glb.runtime.DrawableInstance` object.'''
        ...
    
    @property
    def armature(self) -> aspose.cad.fileformats.glb.runtime.ArmatureInstance:
        ...
    
    ...

class MeshInstancing:
    
    @classmethod
    @property
    def DISCARD(cls) -> MeshInstancing:
        ...
    
    @classmethod
    @property
    def ENABLED(cls) -> MeshInstancing:
        ...
    
    @classmethod
    @property
    def SINGLE_MESH(cls) -> MeshInstancing:
        ...
    
    ...

