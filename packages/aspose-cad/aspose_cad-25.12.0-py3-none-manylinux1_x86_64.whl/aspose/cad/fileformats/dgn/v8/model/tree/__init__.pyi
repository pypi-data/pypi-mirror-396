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

class Tree:
    '''Displays a hierarchical list of items, or nodes. Each
    node includes a caption and an optional bitmap. The user can select a node. If
    it has sub-nodes, the user can collapse or expand the node.'''
    
    def get_node_count(self, include_sub_trees : bool) -> int:
        '''Returns count of nodes at root, optionally including all subtrees.'''
        ...
    
    @property
    def nodes(self) -> aspose.cad.fileformats.dgn.v8.model.tree.TreeNodeCollection:
        '''The collection of nodes associated with this TreeView control'''
        ...
    
    @property
    def path_separator(self) -> str:
        ...
    
    @path_separator.setter
    def path_separator(self, value : str):
        ...
    
    @property
    def root(self) -> aspose.cad.fileformats.dgn.v8.model.tree.TreeNode:
        ...
    
    @root.setter
    def root(self, value : aspose.cad.fileformats.dgn.v8.model.tree.TreeNode):
        ...
    
    ...

class TreeNode:
    '''Implements a node of a :py:attr:`aspose.cad.fileformats.dgn.v8.model.tree.TreeNode.tree`.'''
    
    def get_node_count(self, include_sub_trees : bool) -> int:
        '''Returns number of child nodes.'''
        ...
    
    def remove(self) -> None:
        '''Remove this node from the TreeView control.  Child nodes are also removed from the
        TreeView, but are still attached to this node.'''
        ...
    
    @property
    def first_node(self) -> aspose.cad.fileformats.dgn.v8.model.tree.TreeNode:
        ...
    
    @property
    def full_path(self) -> str:
        ...
    
    @property
    def last_node(self) -> aspose.cad.fileformats.dgn.v8.model.tree.TreeNode:
        ...
    
    @property
    def level(self) -> int:
        '''This denotes the depth of nesting of the TreeNode.'''
        ...
    
    @property
    def next_node(self) -> aspose.cad.fileformats.dgn.v8.model.tree.TreeNode:
        ...
    
    @property
    def nodes(self) -> aspose.cad.fileformats.dgn.v8.model.tree.TreeNodeCollection:
        ...
    
    @property
    def parent(self) -> aspose.cad.fileformats.dgn.v8.model.tree.TreeNode:
        '''Retrieves parent node.'''
        ...
    
    @property
    def prev_node(self) -> aspose.cad.fileformats.dgn.v8.model.tree.TreeNode:
        ...
    
    @property
    def tag(self) -> any:
        ...
    
    @tag.setter
    def tag(self, value : any):
        ...
    
    @property
    def text(self) -> str:
        '''The label text for the tree node'''
        ...
    
    @text.setter
    def text(self, value : str):
        '''The label text for the tree node'''
        ...
    
    @property
    def name(self) -> str:
        '''The name for the tree node - useful for indexing.'''
        ...
    
    @name.setter
    def name(self, value : str):
        '''The name for the tree node - useful for indexing.'''
        ...
    
    @property
    def tree(self) -> aspose.cad.fileformats.dgn.v8.model.tree.Tree:
        '''Return the TreeView control this node belongs to.'''
        ...
    
    ...

class TreeNodeCollection:
    
    @overload
    def add(self, text : str) -> aspose.cad.fileformats.dgn.v8.model.tree.TreeNode:
        '''Creates a new child node under this node.  Child node is positioned after siblings.'''
        ...
    
    @overload
    def add(self, key : str, text : str) -> aspose.cad.fileformats.dgn.v8.model.tree.TreeNode:
        '''Creates a new child node under this node.  Child node is positioned after siblings.'''
        ...
    
    @overload
    def add(self, key : str, text : str, image_index : int) -> aspose.cad.fileformats.dgn.v8.model.tree.TreeNode:
        '''Creates a new child node under this node.  Child node is positioned after siblings.'''
        ...
    
    @overload
    def add(self, key : str, text : str, image_key : str) -> aspose.cad.fileformats.dgn.v8.model.tree.TreeNode:
        '''Creates a new child node under this node.  Child node is positioned after siblings.'''
        ...
    
    @overload
    def add(self, key : str, text : str, image_key : str, selected_image_key : str) -> aspose.cad.fileformats.dgn.v8.model.tree.TreeNode:
        '''Creates a new child node under this node.  Child node is positioned after siblings.'''
        ...
    
    @overload
    def add(self, node : aspose.cad.fileformats.dgn.v8.model.tree.TreeNode) -> int:
        '''Adds a new child node to this node.  Child node is positioned after siblings.'''
        ...
    
    def add_range(self, nodes : List[aspose.cad.fileformats.dgn.v8.model.tree.TreeNode]) -> None:
        ...
    
    def find(self, key : str, search_all_children : bool) -> List[aspose.cad.fileformats.dgn.v8.model.tree.TreeNode]:
        ...
    
    def contains_key(self, key : str) -> bool:
        '''Returns true if the collection contains an item with the specified key, false otherwise.'''
        ...
    
    def index_of(self, node : aspose.cad.fileformats.dgn.v8.model.tree.TreeNode) -> int:
        ...
    
    def index_of_key(self, key : str) -> int:
        '''The zero-based index of the first occurrence of value within the entire CollectionBase, if found; otherwise, -1.'''
        ...
    
    def remove_by_key(self, key : str) -> None:
        '''Removes the child control with the specified key.'''
        ...
    
    ...

