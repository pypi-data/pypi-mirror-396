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

class Cad2DPointAttribute(CadPropertyAttribute):
    '''class attribute for cad 2D point'''
    
    @property
    def parameter_type(self) -> aspose.cad.fileformats.cad.cadconsts.CadParameterType:
        ...
    
    @parameter_type.setter
    def parameter_type(self, value : aspose.cad.fileformats.cad.cadconsts.CadParameterType):
        ...
    
    @property
    def sub_class_name(self) -> str:
        ...
    
    @sub_class_name.setter
    def sub_class_name(self, value : str):
        ...
    
    @property
    def has_default_value(self) -> bool:
        ...
    
    @has_default_value.setter
    def has_default_value(self, value : bool):
        ...
    
    @property
    def x(self) -> aspose.cad.fileformats.cad.CadEntityAttribute:
        '''Gets X attribute.'''
        ...
    
    @x.setter
    def x(self, value : aspose.cad.fileformats.cad.CadEntityAttribute):
        '''Sets X attribute.'''
        ...
    
    @property
    def y(self) -> aspose.cad.fileformats.cad.CadEntityAttribute:
        '''Gets Y attribute.'''
        ...
    
    @y.setter
    def y(self, value : aspose.cad.fileformats.cad.CadEntityAttribute):
        '''Sets Y attribute.'''
        ...
    
    ...

class Cad3DPointAttribute(Cad2DPointAttribute):
    '''class attribute for cad 3D point'''
    
    @property
    def parameter_type(self) -> aspose.cad.fileformats.cad.cadconsts.CadParameterType:
        ...
    
    @parameter_type.setter
    def parameter_type(self, value : aspose.cad.fileformats.cad.cadconsts.CadParameterType):
        ...
    
    @property
    def sub_class_name(self) -> str:
        ...
    
    @sub_class_name.setter
    def sub_class_name(self, value : str):
        ...
    
    @property
    def has_default_value(self) -> bool:
        ...
    
    @has_default_value.setter
    def has_default_value(self, value : bool):
        ...
    
    @property
    def x(self) -> aspose.cad.fileformats.cad.CadEntityAttribute:
        '''Gets X attribute.'''
        ...
    
    @x.setter
    def x(self, value : aspose.cad.fileformats.cad.CadEntityAttribute):
        '''Sets X attribute.'''
        ...
    
    @property
    def y(self) -> aspose.cad.fileformats.cad.CadEntityAttribute:
        '''Gets Y attribute.'''
        ...
    
    @y.setter
    def y(self, value : aspose.cad.fileformats.cad.CadEntityAttribute):
        '''Sets Y attribute.'''
        ...
    
    @property
    def z(self) -> aspose.cad.fileformats.cad.CadEntityAttribute:
        '''Gets Z attribute.'''
        ...
    
    @z.setter
    def z(self, value : aspose.cad.fileformats.cad.CadEntityAttribute):
        '''Sets Z attribute.'''
        ...
    
    ...

class CadAcdsList(aspose.cad.NonGenericList):
    '''The Cad Object List'''
    
    def clone(self) -> any:
        '''The clone.
        
        :returns: The :py:class:`any`.'''
        ...
    
    ...

class CadAppIdDictionary(aspose.cad.NonGenericDictionary):
    '''Collection of cad layouts'''
    
    @overload
    def remove(self, key : str) -> bool:
        '''Removes the :py:class:`aspose.cad.fileformats.cad.cadtables.CadAppIdTableObject` with the specified key.
        
        :param key: The :py:class:`aspose.cad.fileformats.cad.cadtables.CadAppIdTableObject` key to remove.
        :returns: True if the element is successfully removed; otherwise, false. This method also returns false if ``key`` was not found in the dictionary.'''
        ...
    
    @overload
    def remove(self, key : any) -> None:
        '''Removes the element with the specified key from the
        :py:class:`dict` object.
        
        :param key: The key of the element to remove.'''
        ...
    
    @overload
    def add(self, key : str, value : aspose.cad.fileformats.cad.cadtables.CadAppIdTableObject) -> None:
        '''Adds a :py:class:`aspose.cad.fileformats.cad.cadtables.CadAppIdTableObject` to the dictionary.
        
        :param key: The :py:class:`aspose.cad.fileformats.cad.cadtables.CadAppIdTableObject` key.
        :param value: The :py:class:`aspose.cad.fileformats.cad.cadtables.CadAppIdTableObject` to add.'''
        ...
    
    @overload
    def add(self, key : any, value : any) -> None:
        '''Adds an element with the provided key and value to the
        :py:class:`dict` object.
        
        :param key: The
        :py:class:`any` to use as the key of the element to add.
        :param value: The
        :py:class:`any` to use as the value of the element to add.'''
        ...
    
    def clear(self) -> None:
        '''Removes all elements from the
        :py:class:`dict` object.'''
        ...
    
    def contains_key(self, key : str) -> bool:
        '''Determines whether :py:class:`aspose.cad.fileformats.cad.cadtables.CadAppIdTableObject` contained within this dictionary.
        
        :param key: The :py:class:`aspose.cad.fileformats.cad.cadtables.CadAppIdTableObject` key.
        :returns: True if the current dictionary contains an element with the key; otherwise, false.'''
        ...
    
    def try_get_value(self, key : str, value : Any) -> bool:
        '''Gets the value associated with the specified key.
        
        :param key: The key whose value to get.
        :param value: When this method returns, the value associated with the specified key, if the key is found; otherwise, the default value for the type of the ``value`` parameter. This parameter is passed uninitialized.
        :returns: True if the dictionary contains an element with the specified key; otherwise, false.'''
        ...
    
    def clone(self) -> any:
        '''Clones the dictionary.
        
        :returns: A new object that is a shallow copy of this instance.'''
        ...
    
    @property
    def is_fixed_size(self) -> bool:
        ...
    
    @property
    def is_read_only(self) -> bool:
        ...
    
    @property
    def keys(self) -> list:
        '''Gets an
        :py:class:`list` object containing the keys of the
        :py:class:`dict` object.'''
        ...
    
    @property
    def values(self) -> list:
        '''Gets an
        :py:class:`list` object containing the values in the
        :py:class:`dict` object.'''
        ...
    
    @property
    def cad_symbol_table_group_codes(self) -> aspose.cad.fileformats.cad.cadtables.CadSymbolTableGroupCodes:
        ...
    
    @cad_symbol_table_group_codes.setter
    def cad_symbol_table_group_codes(self, value : aspose.cad.fileformats.cad.cadtables.CadSymbolTableGroupCodes):
        ...
    
    @property
    def keys_typed(self) -> List[str]:
        ...
    
    @property
    def values_typed(self) -> List[aspose.cad.fileformats.cad.cadtables.CadAppIdTableObject]:
        ...
    
    ...

class CadBinaryAttribute(CadSingleValueProperty):
    '''class attribute for cad binary properties'''
    
    @property
    def parameter_type(self) -> aspose.cad.fileformats.cad.cadconsts.CadParameterType:
        ...
    
    @parameter_type.setter
    def parameter_type(self, value : aspose.cad.fileformats.cad.cadconsts.CadParameterType):
        ...
    
    @property
    def sub_class_name(self) -> str:
        ...
    
    @sub_class_name.setter
    def sub_class_name(self, value : str):
        ...
    
    @property
    def has_default_value(self) -> bool:
        ...
    
    @has_default_value.setter
    def has_default_value(self, value : bool):
        ...
    
    @property
    def attribute(self) -> aspose.cad.fileformats.cad.CadEntityAttribute:
        '''Gets property attribute.'''
        ...
    
    @attribute.setter
    def attribute(self, value : aspose.cad.fileformats.cad.CadEntityAttribute):
        '''Sets property attribute.'''
        ...
    
    ...

class CadBinaryCodeValue(CadCodeValue):
    '''Cad binary Code Value class'''
    
    def get_string_value(self) -> str:
        '''Gets the string value.
        
        :returns: Value as string'''
        ...
    
    def get_binary_data(self) -> bytes:
        '''Gets the binary data.
        
        :returns: Byte array from hexadecimal data.'''
        ...
    
    def get_bool_value(self) -> bool:
        '''Gets the boolean value.
        
        :returns: The :py:class:`bool`.'''
        ...
    
    def get_short_value(self) -> int:
        '''The get short value.
        
        :returns: The :py:class:`int`.'''
        ...
    
    def get_int_value(self) -> int:
        '''The get integer value.
        
        :returns: The :py:class:`int`.'''
        ...
    
    def get_long_value(self) -> int:
        '''The get long value.
        
        :returns: The :py:class:`int`.'''
        ...
    
    def get_double_value(self) -> float:
        '''The get double value.
        
        :returns: The :py:class:`float`.'''
        ...
    
    def equals(self, obj : aspose.cad.fileformats.cad.CadCodeValue) -> bool:
        '''Determines whether the specified :py:class:`aspose.cad.fileformats.cad.CadCodeValue`, is equal to this instance.
        
        :param obj: The :py:class:`aspose.cad.fileformats.cad.CadCodeValue` to compare with this instance.
        :returns: ``true`` if the specified :py:class:`aspose.cad.fileformats.cad.CadCodeValue` is equal to this instance; otherwise, ``false``.'''
        ...
    
    @property
    def attribute(self) -> aspose.cad.fileformats.cad.CadEntityAttribute:
        '''Gets the attribute.'''
        ...
    
    @property
    def code(self) -> int:
        '''Gets the code.'''
        ...
    
    @code.setter
    def code(self, value : int):
        '''Sets the code.'''
        ...
    
    @property
    def value(self) -> str:
        '''Gets the value.'''
        ...
    
    @value.setter
    def value(self, value : str):
        '''Sets the value.'''
        ...
    
    @property
    def data(self) -> bytes:
        '''Gets the value.'''
        ...
    
    @data.setter
    def data(self, value : bytes):
        '''Sets the value.'''
        ...
    
    ...

class CadBlockDictionary(aspose.cad.NonGenericDictionary):
    '''CAD blocks collection'''
    
    @overload
    def remove(self, key : str) -> bool:
        '''Removes the :py:class:`aspose.cad.fileformats.cad.cadobjects.CadBlockEntity` with the specified key.
        
        :param key: The :py:class:`aspose.cad.fileformats.cad.cadobjects.CadBlockEntity` key to remove.
        :returns: True if the element is successfully removed; otherwise, false. This method also returns false if ``key`` was not found in the dictionary.'''
        ...
    
    @overload
    def remove(self, key : any) -> None:
        '''Removes the element with the specified key from the
        :py:class:`dict` object.
        
        :param key: The key of the element to remove.'''
        ...
    
    @overload
    def add(self, key : str, value : aspose.cad.fileformats.cad.cadobjects.CadBlockEntity) -> None:
        '''Adds a :py:class:`aspose.cad.fileformats.cad.cadobjects.CadBlockEntity` to the dictionary.
        
        :param key: The :py:class:`aspose.cad.fileformats.cad.cadobjects.CadBlockEntity` key.
        :param value: The :py:class:`aspose.cad.fileformats.cad.cadobjects.CadBlockEntity` to add.'''
        ...
    
    @overload
    def add(self, key : any, value : any) -> None:
        '''Adds an element with the provided key and value to the
        :py:class:`dict` object.
        
        :param key: The
        :py:class:`any` to use as the key of the element to add.
        :param value: The
        :py:class:`any` to use as the value of the element to add.'''
        ...
    
    def clear(self) -> None:
        '''Removes all elements from the
        :py:class:`dict` object.'''
        ...
    
    def contains_key(self, key : str) -> bool:
        '''Determines whether :py:class:`aspose.cad.fileformats.cad.cadobjects.CadBlockEntity` contained within this dictionary.
        
        :param key: The :py:class:`aspose.cad.fileformats.cad.cadobjects.CadBlockEntity` key.
        :returns: True if the current dictionary contains an element with the key; otherwise, false.'''
        ...
    
    def try_get_value(self, key : str, value : Any) -> bool:
        '''Gets the value associated with the specified key.
        
        :param key: The key whose value to get.
        :param value: When this method returns, the value associated with the specified key, if the key is found; otherwise, the default value for the type of the ``value`` parameter. This parameter is passed uninitialized.
        :returns: True if the dictionary contains an element with the specified key; otherwise, false.'''
        ...
    
    def clone(self) -> any:
        '''Clones the dictionary.
        
        :returns: A new object that is a shallow copy of this instance.'''
        ...
    
    @property
    def is_fixed_size(self) -> bool:
        ...
    
    @property
    def is_read_only(self) -> bool:
        ...
    
    @property
    def keys(self) -> list:
        '''Gets an
        :py:class:`list` object containing the keys of the
        :py:class:`dict` object.'''
        ...
    
    @property
    def values(self) -> list:
        '''Gets an
        :py:class:`list` object containing the values in the
        :py:class:`dict` object.'''
        ...
    
    @property
    def keys_typed(self) -> List[str]:
        ...
    
    @property
    def values_typed(self) -> List[aspose.cad.fileformats.cad.cadobjects.CadBlockEntity]:
        ...
    
    ...

class CadBlockRecordList(aspose.cad.NonGenericList):
    '''The cad view dictionary
    The following group codes apply to VPORT symbol table entries. The VPORT
    table is unique: it may contain several entries with the same name (indicating
    a multiple-viewport configuration). The entries corresponding to the active
    viewport configuration all have the name *ACTIVE. The first such entry
    describes the current viewport.
    Since the name is not unique, we use List as a container'''
    
    def clone(self) -> any:
        '''The clone.
        
        :returns: The :py:class:`any`.'''
        ...
    
    def add_range(self, objects : List[aspose.cad.fileformats.cad.cadtables.CadBlockTableObject]) -> None:
        '''Adds the range of the objects to container.
        
        :param objects: The objects array.'''
        ...
    
    def get_block_by_layout_handle(self, layout_handle : str) -> aspose.cad.fileformats.cad.cadtables.CadBlockTableObject:
        '''Gets block table by layout handle
        
        :param layout_handle: The layout handle.
        :returns: The :py:class:`aspose.cad.fileformats.cad.cadtables.CadBlockTableObject`.'''
        ...
    
    @property
    def cad_symbol_table_group_codes(self) -> aspose.cad.fileformats.cad.cadtables.CadSymbolTableGroupCodes:
        ...
    
    @cad_symbol_table_group_codes.setter
    def cad_symbol_table_group_codes(self, value : aspose.cad.fileformats.cad.cadtables.CadSymbolTableGroupCodes):
        ...
    
    ...

class CadBoolAttribute(CadSingleValueProperty):
    '''class attribute for cad bool properties'''
    
    @property
    def parameter_type(self) -> aspose.cad.fileformats.cad.cadconsts.CadParameterType:
        ...
    
    @parameter_type.setter
    def parameter_type(self, value : aspose.cad.fileformats.cad.cadconsts.CadParameterType):
        ...
    
    @property
    def sub_class_name(self) -> str:
        ...
    
    @sub_class_name.setter
    def sub_class_name(self, value : str):
        ...
    
    @property
    def has_default_value(self) -> bool:
        ...
    
    @has_default_value.setter
    def has_default_value(self, value : bool):
        ...
    
    @property
    def attribute(self) -> aspose.cad.fileformats.cad.CadEntityAttribute:
        '''Gets property attribute.'''
        ...
    
    @attribute.setter
    def attribute(self, value : aspose.cad.fileformats.cad.CadEntityAttribute):
        '''Sets property attribute.'''
        ...
    
    ...

class CadClassList:
    '''CAD classes collection'''
    
    def clone(self) -> any:
        '''Clones the list.
        
        :returns: A new object that is a shallow copy of this instance.'''
        ...
    
    ...

class CadCodeValue:
    '''Code Value class'''
    
    def get_string_value(self) -> str:
        '''Gets the string value.
        
        :returns: Value as string'''
        ...
    
    def get_binary_data(self) -> bytes:
        '''Gets the binary data.
        
        :returns: Byte array from hexadecimal data.'''
        ...
    
    def get_bool_value(self) -> bool:
        '''Gets the boolean value.
        
        :returns: The :py:class:`bool`.'''
        ...
    
    def get_short_value(self) -> int:
        '''The get short value.
        
        :returns: The :py:class:`int`.'''
        ...
    
    def get_int_value(self) -> int:
        '''The get integer value.
        
        :returns: The :py:class:`int`.'''
        ...
    
    def get_long_value(self) -> int:
        '''The get long value.
        
        :returns: The :py:class:`int`.'''
        ...
    
    def get_double_value(self) -> float:
        '''The get double value.
        
        :returns: The :py:class:`float`.'''
        ...
    
    def equals(self, obj : aspose.cad.fileformats.cad.CadCodeValue) -> bool:
        '''Determines whether the specified :py:class:`aspose.cad.fileformats.cad.CadCodeValue`, is equal to this instance.
        
        :param obj: The :py:class:`aspose.cad.fileformats.cad.CadCodeValue` to compare with this instance.
        :returns: ``true`` if the specified :py:class:`aspose.cad.fileformats.cad.CadCodeValue` is equal to this instance; otherwise, ``false``.'''
        ...
    
    @property
    def attribute(self) -> aspose.cad.fileformats.cad.CadEntityAttribute:
        '''Gets the attribute.'''
        ...
    
    @property
    def code(self) -> int:
        '''Gets the code.'''
        ...
    
    @code.setter
    def code(self, value : int):
        '''Sets the code.'''
        ...
    
    @property
    def value(self) -> str:
        '''Gets the value.'''
        ...
    
    @value.setter
    def value(self, value : str):
        '''Sets the value.'''
        ...
    
    ...

class CadDimensionDictionary(aspose.cad.NonGenericDictionary):
    '''Dimension styles dictionary.'''
    
    @overload
    def remove(self, key : str) -> bool:
        '''Removes the :py:class:`aspose.cad.fileformats.cad.cadtables.CadDimensionStyleTable` with the specified key.
        
        :param key: The :py:class:`aspose.cad.fileformats.cad.cadtables.CadDimensionStyleTable` key to remove.
        :returns: True if the element is successfully removed; otherwise, false. This method also returns false if ``key`` was not found in the dictionary.'''
        ...
    
    @overload
    def remove(self, key : any) -> None:
        '''Removes the element with the specified key from the
        :py:class:`dict` object.
        
        :param key: The key of the element to remove.'''
        ...
    
    @overload
    def add(self, key : str, value : aspose.cad.fileformats.cad.cadtables.CadDimensionStyleTable) -> None:
        '''Adds a :py:class:`aspose.cad.fileformats.cad.cadtables.CadDimensionStyleTable` to the dictionary.
        
        :param key: The :py:class:`aspose.cad.fileformats.cad.cadtables.CadDimensionStyleTable` key.
        :param value: The :py:class:`aspose.cad.fileformats.cad.cadtables.CadDimensionStyleTable` to add.'''
        ...
    
    @overload
    def add(self, key : any, value : any) -> None:
        '''Adds an element with the provided key and value to the
        :py:class:`dict` object.
        
        :param key: The
        :py:class:`any` to use as the key of the element to add.
        :param value: The
        :py:class:`any` to use as the value of the element to add.'''
        ...
    
    def clear(self) -> None:
        '''Removes all elements from the
        :py:class:`dict` object.'''
        ...
    
    def contains_key(self, key : str) -> bool:
        '''Determines whether :py:class:`aspose.cad.fileformats.cad.cadtables.CadDimensionStyleTable` contained within this dictionary.
        
        :param key: The :py:class:`aspose.cad.fileformats.cad.cadtables.CadDimensionStyleTable` key.
        :returns: True if the current dictionary contains an element with the key; otherwise, false.'''
        ...
    
    def try_get_value(self, key : str, value : Any) -> bool:
        '''Gets the value associated with the specified key.
        
        :param key: The key whose value to get.
        :param value: When this method returns, the value associated with the specified key, if the key is found; otherwise, the default value for the type of the ``value`` parameter. This parameter is passed uninitialized.
        :returns: True if the dictionary contains an element with the specified key; otherwise, false.'''
        ...
    
    def clone(self) -> any:
        '''Clones the dictionary.
        
        :returns: A new object that is a shallow copy of this instance.'''
        ...
    
    @property
    def is_fixed_size(self) -> bool:
        ...
    
    @property
    def is_read_only(self) -> bool:
        ...
    
    @property
    def keys(self) -> list:
        '''Gets an
        :py:class:`list` object containing the keys of the
        :py:class:`dict` object.'''
        ...
    
    @property
    def values(self) -> list:
        '''Gets an
        :py:class:`list` object containing the values in the
        :py:class:`dict` object.'''
        ...
    
    @property
    def keys_typed(self) -> List[str]:
        ...
    
    @property
    def values_typed(self) -> List[aspose.cad.fileformats.cad.cadtables.CadDimensionStyleTable]:
        ...
    
    @property
    def cad_symbol_table_group_codes(self) -> aspose.cad.fileformats.cad.cadtables.CadSymbolTableGroupCodes:
        ...
    
    @cad_symbol_table_group_codes.setter
    def cad_symbol_table_group_codes(self, value : aspose.cad.fileformats.cad.cadtables.CadSymbolTableGroupCodes):
        ...
    
    ...

class CadDoubleAttribute(CadSingleValueProperty):
    '''class attribute for cad double properties'''
    
    @property
    def parameter_type(self) -> aspose.cad.fileformats.cad.cadconsts.CadParameterType:
        ...
    
    @parameter_type.setter
    def parameter_type(self, value : aspose.cad.fileformats.cad.cadconsts.CadParameterType):
        ...
    
    @property
    def sub_class_name(self) -> str:
        ...
    
    @sub_class_name.setter
    def sub_class_name(self, value : str):
        ...
    
    @property
    def has_default_value(self) -> bool:
        ...
    
    @has_default_value.setter
    def has_default_value(self, value : bool):
        ...
    
    @property
    def attribute(self) -> aspose.cad.fileformats.cad.CadEntityAttribute:
        '''Gets property attribute.'''
        ...
    
    @attribute.setter
    def attribute(self, value : aspose.cad.fileformats.cad.CadEntityAttribute):
        '''Sets property attribute.'''
        ...
    
    ...

class CadImage(aspose.cad.Image):
    '''Cad image class'''
    
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
    
    @overload
    def get_bounds(self) -> None:
        '''Fills Bounds property (contain minimum and maximum point of entity) for all entities.'''
        ...
    
    @overload
    def get_bounds(self, entity : aspose.cad.fileformats.cad.cadobjects.CadEntityBase) -> None:
        '''Fills Bounds property (contains minimum and maximum point) for entity.'''
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
    
    def update_size(self, include_beyond_size : bool) -> None:
        '''Updates size of an image after changes, that may affect initial size, e.g. removing of entities.
        MinPoint, MaxPoint, Width and Height properties of image are updated.
        
        :param include_beyond_size: Determines whether entities that lie outside the boundaries of the image size
        should affect the new image size.'''
        ...
    
    def change_custom_property(self, custom_prop_name : str, new_custom_prop_value : str) -> None:
        '''Updates a custom property and related CAD field objects with a new value.
        
        :param custom_prop_name: The custom property name.
        :param new_custom_prop_value: The new property value.'''
        ...
    
    def add_custom_property(self, custom_prop_name : str, custom_prop_value : str) -> None:
        '''Adds a custom property to the drawing
        
        :param custom_prop_name: The name of the custom property to add.
        :param custom_prop_value: The value of the custom property.'''
        ...
    
    def remove_custom_property(self, custom_prop_name : str) -> None:
        '''Removes a custom property from the drawing.
        
        :param custom_prop_name: The name of the custom property to remove.'''
        ...
    
    def try_remove_entity(self, entity_to_remove : aspose.cad.fileformats.cad.cadobjects.CadEntityBase) -> None:
        '''Removes entity from blocks for DWG format.
        
        :param entity_to_remove: Entity to be removed.'''
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
    def active_page(self) -> aspose.cad.fileformats.cad.cadobjects.CadLayout:
        ...
    
    @property
    def default_line_weight(self) -> float:
        ...
    
    @default_line_weight.setter
    def default_line_weight(self, value : float):
        ...
    
    @property
    def default_font(self) -> str:
        ...
    
    @default_font.setter
    def default_font(self, value : str):
        ...
    
    @property
    def file_encoding(self) -> aspose.cad.CodePages:
        ...
    
    @file_encoding.setter
    def file_encoding(self, value : aspose.cad.CodePages):
        ...
    
    @property
    def application_version(self) -> int:
        ...
    
    @application_version.setter
    def application_version(self, value : int):
        ...
    
    @property
    def maintenance_version(self) -> int:
        ...
    
    @maintenance_version.setter
    def maintenance_version(self, value : int):
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
    def line_types(self) -> aspose.cad.fileformats.cad.CadLineTypesDictionary:
        ...
    
    @line_types.setter
    def line_types(self, value : aspose.cad.fileformats.cad.CadLineTypesDictionary):
        ...
    
    @property
    def block_entities(self) -> aspose.cad.fileformats.cad.CadBlockDictionary:
        ...
    
    @block_entities.setter
    def block_entities(self, value : aspose.cad.fileformats.cad.CadBlockDictionary):
        ...
    
    @property
    def class_entities(self) -> aspose.cad.fileformats.cad.CadClassList:
        ...
    
    @class_entities.setter
    def class_entities(self, value : aspose.cad.fileformats.cad.CadClassList):
        ...
    
    @property
    def thumbnail_image(self) -> aspose.cad.fileformats.cad.cadobjects.CadThumbnailImage:
        ...
    
    @thumbnail_image.setter
    def thumbnail_image(self, value : aspose.cad.fileformats.cad.cadobjects.CadThumbnailImage):
        ...
    
    @property
    def blocks_tables(self) -> aspose.cad.fileformats.cad.CadBlockRecordList:
        ...
    
    @blocks_tables.setter
    def blocks_tables(self, value : aspose.cad.fileformats.cad.CadBlockRecordList):
        ...
    
    @property
    def dimension_styles(self) -> aspose.cad.fileformats.cad.CadDimensionDictionary:
        ...
    
    @dimension_styles.setter
    def dimension_styles(self, value : aspose.cad.fileformats.cad.CadDimensionDictionary):
        ...
    
    @property
    def entities(self) -> Iterable[aspose.cad.fileformats.cad.cadobjects.CadEntityBase]:
        '''Gets the entities.'''
        ...
    
    @entities.setter
    def entities(self, value : Iterable[aspose.cad.fileformats.cad.cadobjects.CadEntityBase]):
        '''Sets the entities.'''
        ...
    
    @property
    def objects(self) -> List[aspose.cad.fileformats.cad.cadobjects.CadBaseObject]:
        '''Gets the objects.'''
        ...
    
    @objects.setter
    def objects(self, value : List[aspose.cad.fileformats.cad.cadobjects.CadBaseObject]):
        '''Sets the objects.'''
        ...
    
    @property
    def layers(self) -> aspose.cad.fileformats.cad.CadLayersList:
        '''Gets the layers.'''
        ...
    
    @layers.setter
    def layers(self, value : aspose.cad.fileformats.cad.CadLayersList):
        '''Sets the layers.'''
        ...
    
    @property
    def max_point(self) -> aspose.cad.fileformats.cad.cadobjects.Cad3DPoint:
        ...
    
    @property
    def min_point(self) -> aspose.cad.fileformats.cad.cadobjects.Cad3DPoint:
        ...
    
    @property
    def styles(self) -> aspose.cad.fileformats.cad.CadStylesList:
        '''Gets the styles.'''
        ...
    
    @styles.setter
    def styles(self, value : aspose.cad.fileformats.cad.CadStylesList):
        '''Sets the styles.'''
        ...
    
    @property
    def header(self) -> aspose.cad.fileformats.cad.cadobjects.CadHeader:
        '''Gets the header.'''
        ...
    
    @header.setter
    def header(self, value : aspose.cad.fileformats.cad.cadobjects.CadHeader):
        '''Sets the header.'''
        ...
    
    @property
    def view_ports(self) -> aspose.cad.fileformats.cad.CadVportList:
        ...
    
    @view_ports.setter
    def view_ports(self, value : aspose.cad.fileformats.cad.CadVportList):
        ...
    
    @property
    def views(self) -> aspose.cad.fileformats.cad.CadViewList:
        '''Gets the views.'''
        ...
    
    @views.setter
    def views(self, value : aspose.cad.fileformats.cad.CadViewList):
        '''Sets the views.'''
        ...
    
    @property
    def uc_ss(self) -> aspose.cad.fileformats.cad.CadUcsList:
        ...
    
    @uc_ss.setter
    def uc_ss(self, value : aspose.cad.fileformats.cad.CadUcsList):
        ...
    
    @property
    def cad_acds(self) -> aspose.cad.fileformats.cad.CadAcdsList:
        ...
    
    @cad_acds.setter
    def cad_acds(self, value : aspose.cad.fileformats.cad.CadAcdsList):
        ...
    
    @property
    def app_id_tables(self) -> aspose.cad.fileformats.cad.CadAppIdDictionary:
        ...
    
    @app_id_tables.setter
    def app_id_tables(self, value : aspose.cad.fileformats.cad.CadAppIdDictionary):
        ...
    
    ...

class CadIntAttribute(CadSingleValueProperty):
    '''class attribute for cad int properties'''
    
    @property
    def parameter_type(self) -> aspose.cad.fileformats.cad.cadconsts.CadParameterType:
        ...
    
    @parameter_type.setter
    def parameter_type(self, value : aspose.cad.fileformats.cad.cadconsts.CadParameterType):
        ...
    
    @property
    def sub_class_name(self) -> str:
        ...
    
    @sub_class_name.setter
    def sub_class_name(self, value : str):
        ...
    
    @property
    def has_default_value(self) -> bool:
        ...
    
    @has_default_value.setter
    def has_default_value(self, value : bool):
        ...
    
    @property
    def attribute(self) -> aspose.cad.fileformats.cad.CadEntityAttribute:
        '''Gets property attribute.'''
        ...
    
    @attribute.setter
    def attribute(self, value : aspose.cad.fileformats.cad.CadEntityAttribute):
        '''Sets property attribute.'''
        ...
    
    ...

class CadLayersList(aspose.cad.NonGenericList):
    '''Layer tables list
    Since the name is not unique, we use List as a container'''
    
    def clone(self) -> any:
        '''The clone.
        
        :returns: The :py:class:`any`.'''
        ...
    
    def add_range(self, objects : List[aspose.cad.fileformats.cad.cadtables.CadLayerTable]) -> None:
        '''Adds the range of the objects to container.
        
        :param objects: The objects array.'''
        ...
    
    def get_layer(self, name : str) -> aspose.cad.fileformats.cad.cadtables.CadLayerTable:
        '''Gets list of layers by name.
        
        :param name: The name parameter.
        :returns: The list of :py:class:`aspose.cad.fileformats.cad.cadtables.CadLayerTable`'''
        ...
    
    def get_layers_names(self) -> List[str]:
        '''Gets the layers names.
        
        :returns: The list of :py:class:`str`layers names'''
        ...
    
    @property
    def application_codes_container(self) -> aspose.cad.fileformats.cad.cadobjects.CadApplicationCodesContainer:
        ...
    
    @application_codes_container.setter
    def application_codes_container(self, value : aspose.cad.fileformats.cad.cadobjects.CadApplicationCodesContainer):
        ...
    
    @property
    def cad_symbol_table_group_codes(self) -> aspose.cad.fileformats.cad.cadtables.CadSymbolTableGroupCodes:
        ...
    
    @cad_symbol_table_group_codes.setter
    def cad_symbol_table_group_codes(self, value : aspose.cad.fileformats.cad.cadtables.CadSymbolTableGroupCodes):
        ...
    
    ...

class CadLayoutDictionary:
    '''Collection of cad layouts'''
    
    def clone(self) -> any:
        '''Clones the dictionary.
        
        :returns: A new object that is a shallow copy of this instance.'''
        ...
    
    @classmethod
    @property
    def MODEL_SPACE_NAME(cls) -> str:
        ...
    
    ...

class CadLineTypesDictionary(aspose.cad.NonGenericDictionary):
    '''Represents dictionary with types of lines.'''
    
    @overload
    def remove(self, key : str) -> bool:
        '''Removes the :py:class:`aspose.cad.fileformats.cad.cadtables.CadLineTypeTableObject` with the specified key.
        
        :param key: The :py:class:`aspose.cad.fileformats.cad.cadtables.CadLineTypeTableObject` key to remove.
        :returns: True if the element is successfully removed; otherwise, false. This method also returns false if ``key`` was not found in the dictionary.'''
        ...
    
    @overload
    def remove(self, key : any) -> None:
        '''Removes the element with the specified key from the
        :py:class:`dict` object.
        
        :param key: The key of the element to remove.'''
        ...
    
    @overload
    def add(self, key : str, value : aspose.cad.fileformats.cad.cadtables.CadLineTypeTableObject) -> None:
        '''Adds a :py:class:`aspose.cad.fileformats.cad.cadtables.CadLineTypeTableObject` to the dictionary.
        
        :param key: The :py:class:`aspose.cad.fileformats.cad.cadtables.CadLineTypeTableObject` key.
        :param value: The :py:class:`aspose.cad.fileformats.cad.cadtables.CadLineTypeTableObject` to add.'''
        ...
    
    @overload
    def add(self, key : any, value : any) -> None:
        '''Adds an element with the provided key and value to the
        :py:class:`dict` object.
        
        :param key: The
        :py:class:`any` to use as the key of the element to add.
        :param value: The
        :py:class:`any` to use as the value of the element to add.'''
        ...
    
    def clear(self) -> None:
        '''Removes all elements from the
        :py:class:`dict` object.'''
        ...
    
    def contains_key(self, key : str) -> bool:
        '''Determines whether :py:class:`aspose.cad.fileformats.cad.cadtables.CadLineTypeTableObject` contained within this dictionary.
        
        :param key: The :py:class:`aspose.cad.fileformats.cad.cadtables.CadLineTypeTableObject` key.
        :returns: True if the current dictionary contains an element with the key; otherwise, false.'''
        ...
    
    def try_get_value(self, key : str, value : Any) -> bool:
        '''Gets the value associated with the specified key.
        
        :param key: The key whose value to get.
        :param value: When this method returns, the value associated with the specified key, if the key is found; otherwise, the default value for the type of the ``value`` parameter. This parameter is passed uninitialized.
        :returns: True if the dictionary contains an element with the specified key; otherwise, false.'''
        ...
    
    def clone(self) -> any:
        '''Clones the dictionary.
        
        :returns: A new object that is a shallow copy of this instance.'''
        ...
    
    @property
    def is_fixed_size(self) -> bool:
        ...
    
    @property
    def is_read_only(self) -> bool:
        ...
    
    @property
    def keys(self) -> list:
        '''Gets an
        :py:class:`list` object containing the keys of the
        :py:class:`dict` object.'''
        ...
    
    @property
    def values(self) -> list:
        '''Gets an
        :py:class:`list` object containing the values in the
        :py:class:`dict` object.'''
        ...
    
    @property
    def cad_symbol_table_group_codes(self) -> aspose.cad.fileformats.cad.cadtables.CadSymbolTableGroupCodes:
        ...
    
    @cad_symbol_table_group_codes.setter
    def cad_symbol_table_group_codes(self, value : aspose.cad.fileformats.cad.cadtables.CadSymbolTableGroupCodes):
        ...
    
    @property
    def keys_typed(self) -> List[str]:
        ...
    
    @property
    def values_typed(self) -> List[aspose.cad.fileformats.cad.cadtables.CadLineTypeTableObject]:
        ...
    
    ...

class CadLongAttribute(CadSingleValueProperty):
    '''class attribute for cad long properties'''
    
    @property
    def parameter_type(self) -> aspose.cad.fileformats.cad.cadconsts.CadParameterType:
        ...
    
    @parameter_type.setter
    def parameter_type(self, value : aspose.cad.fileformats.cad.cadconsts.CadParameterType):
        ...
    
    @property
    def sub_class_name(self) -> str:
        ...
    
    @sub_class_name.setter
    def sub_class_name(self, value : str):
        ...
    
    @property
    def has_default_value(self) -> bool:
        ...
    
    @has_default_value.setter
    def has_default_value(self, value : bool):
        ...
    
    @property
    def attribute(self) -> aspose.cad.fileformats.cad.CadEntityAttribute:
        '''Gets property attribute.'''
        ...
    
    @attribute.setter
    def attribute(self, value : aspose.cad.fileformats.cad.CadEntityAttribute):
        '''Sets property attribute.'''
        ...
    
    ...

class CadPropertyAttribute:
    '''Base class attribute for dxf properties'''
    
    @property
    def parameter_type(self) -> aspose.cad.fileformats.cad.cadconsts.CadParameterType:
        ...
    
    @parameter_type.setter
    def parameter_type(self, value : aspose.cad.fileformats.cad.cadconsts.CadParameterType):
        ...
    
    @property
    def sub_class_name(self) -> str:
        ...
    
    @sub_class_name.setter
    def sub_class_name(self, value : str):
        ...
    
    @property
    def has_default_value(self) -> bool:
        ...
    
    @has_default_value.setter
    def has_default_value(self, value : bool):
        ...
    
    ...

class CadShortAttribute(CadSingleValueProperty):
    '''class attribute for cad short properties'''
    
    @property
    def parameter_type(self) -> aspose.cad.fileformats.cad.cadconsts.CadParameterType:
        ...
    
    @parameter_type.setter
    def parameter_type(self, value : aspose.cad.fileformats.cad.cadconsts.CadParameterType):
        ...
    
    @property
    def sub_class_name(self) -> str:
        ...
    
    @sub_class_name.setter
    def sub_class_name(self, value : str):
        ...
    
    @property
    def has_default_value(self) -> bool:
        ...
    
    @has_default_value.setter
    def has_default_value(self, value : bool):
        ...
    
    @property
    def attribute(self) -> aspose.cad.fileformats.cad.CadEntityAttribute:
        '''Gets property attribute.'''
        ...
    
    @attribute.setter
    def attribute(self, value : aspose.cad.fileformats.cad.CadEntityAttribute):
        '''Sets property attribute.'''
        ...
    
    ...

class CadSingleValueProperty(CadPropertyAttribute):
    '''Base class attribute for cad single value properties'''
    
    @property
    def parameter_type(self) -> aspose.cad.fileformats.cad.cadconsts.CadParameterType:
        ...
    
    @parameter_type.setter
    def parameter_type(self, value : aspose.cad.fileformats.cad.cadconsts.CadParameterType):
        ...
    
    @property
    def sub_class_name(self) -> str:
        ...
    
    @sub_class_name.setter
    def sub_class_name(self, value : str):
        ...
    
    @property
    def has_default_value(self) -> bool:
        ...
    
    @has_default_value.setter
    def has_default_value(self, value : bool):
        ...
    
    @property
    def attribute(self) -> aspose.cad.fileformats.cad.CadEntityAttribute:
        '''Gets property attribute.'''
        ...
    
    @attribute.setter
    def attribute(self, value : aspose.cad.fileformats.cad.CadEntityAttribute):
        '''Sets property attribute.'''
        ...
    
    ...

class CadSizeAttribute(CadPropertyAttribute):
    '''class attribute for cad size'''
    
    @property
    def parameter_type(self) -> aspose.cad.fileformats.cad.cadconsts.CadParameterType:
        ...
    
    @parameter_type.setter
    def parameter_type(self, value : aspose.cad.fileformats.cad.cadconsts.CadParameterType):
        ...
    
    @property
    def sub_class_name(self) -> str:
        ...
    
    @sub_class_name.setter
    def sub_class_name(self, value : str):
        ...
    
    @property
    def has_default_value(self) -> bool:
        ...
    
    @has_default_value.setter
    def has_default_value(self, value : bool):
        ...
    
    @property
    def width(self) -> aspose.cad.fileformats.cad.CadEntityAttribute:
        '''Gets width.'''
        ...
    
    @width.setter
    def width(self, value : aspose.cad.fileformats.cad.CadEntityAttribute):
        '''Sets width.'''
        ...
    
    @property
    def height(self) -> aspose.cad.fileformats.cad.CadEntityAttribute:
        '''Gets height.'''
        ...
    
    @height.setter
    def height(self, value : aspose.cad.fileformats.cad.CadEntityAttribute):
        '''Sets height.'''
        ...
    
    ...

class CadStringAttribute(CadSingleValueProperty):
    '''class attribute for cad string properties'''
    
    @property
    def parameter_type(self) -> aspose.cad.fileformats.cad.cadconsts.CadParameterType:
        ...
    
    @parameter_type.setter
    def parameter_type(self, value : aspose.cad.fileformats.cad.cadconsts.CadParameterType):
        ...
    
    @property
    def sub_class_name(self) -> str:
        ...
    
    @sub_class_name.setter
    def sub_class_name(self, value : str):
        ...
    
    @property
    def has_default_value(self) -> bool:
        ...
    
    @has_default_value.setter
    def has_default_value(self, value : bool):
        ...
    
    @property
    def attribute(self) -> aspose.cad.fileformats.cad.CadEntityAttribute:
        '''Gets property attribute.'''
        ...
    
    @attribute.setter
    def attribute(self, value : aspose.cad.fileformats.cad.CadEntityAttribute):
        '''Sets property attribute.'''
        ...
    
    ...

class CadStylesList(aspose.cad.NonGenericList):
    '''List of Cad styles'''
    
    def add_range(self, objects : List[aspose.cad.fileformats.cad.cadtables.CadStyleTableObject]) -> None:
        '''Adds the range of the objects to container.
        
        :param objects: The objects array.'''
        ...
    
    def clone(self) -> any:
        '''Clones the list.
        
        :returns: A new object that is a shallow copy of this instance.'''
        ...
    
    @property
    def cad_symbol_table_group_codes(self) -> aspose.cad.fileformats.cad.cadtables.CadSymbolTableGroupCodes:
        ...
    
    @cad_symbol_table_group_codes.setter
    def cad_symbol_table_group_codes(self, value : aspose.cad.fileformats.cad.cadtables.CadSymbolTableGroupCodes):
        ...
    
    @property
    def application_codes_container(self) -> aspose.cad.fileformats.cad.cadobjects.CadApplicationCodesContainer:
        ...
    
    @application_codes_container.setter
    def application_codes_container(self, value : aspose.cad.fileformats.cad.cadobjects.CadApplicationCodesContainer):
        ...
    
    ...

class CadUcsList(aspose.cad.NonGenericList):
    '''The cad view dictionary
    The following group codes apply to VPORT symbol table entries. The VPORT
    table is unique: it may contain several entries with the same name (indicating
    a multiple-viewport configuration). The entries corresponding to the active
    viewport configuration all have the name *ACTIVE. The first such entry
    describes the current viewport.
    Since the name is not unique, we use List as a container'''
    
    def clone(self) -> any:
        '''The clone.
        
        :returns: The :py:class:`any`.'''
        ...
    
    def add_range(self, objects : List[aspose.cad.fileformats.cad.cadtables.CadUcsTableObject]) -> None:
        '''Adds the range of the objects to container.
        
        :param objects: The objects array.'''
        ...
    
    @property
    def cad_symbol_table_group_codes(self) -> aspose.cad.fileformats.cad.cadtables.CadSymbolTableGroupCodes:
        ...
    
    @cad_symbol_table_group_codes.setter
    def cad_symbol_table_group_codes(self, value : aspose.cad.fileformats.cad.cadtables.CadSymbolTableGroupCodes):
        ...
    
    ...

class CadViewList(aspose.cad.NonGenericList):
    '''The cad view dictionary
    The following group codes apply to VPORT symbol table entries. The VPORT
    table is unique: it may contain several entries with the same name (indicating
    a multiple-viewport configuration). The entries corresponding to the active
    viewport configuration all have the name *ACTIVE. The first such entry
    describes the current viewport.
    Since the name is not unique, we use List as a container'''
    
    def clone(self) -> any:
        '''The clone.
        
        :returns: The :py:class:`any`.'''
        ...
    
    def add_range(self, objects : List[aspose.cad.fileformats.cad.cadtables.CadViewTableObject]) -> None:
        '''Adds the range of the objects to container.
        
        :param objects: The objects array.'''
        ...
    
    @property
    def cad_symbol_table_group_codes(self) -> aspose.cad.fileformats.cad.cadtables.CadSymbolTableGroupCodes:
        ...
    
    @cad_symbol_table_group_codes.setter
    def cad_symbol_table_group_codes(self, value : aspose.cad.fileformats.cad.cadtables.CadSymbolTableGroupCodes):
        ...
    
    ...

class CadVportList(aspose.cad.NonGenericList):
    '''The cad viewport dictionary
    The following group codes apply to VPORT symbol table entries. The VPORT
    table is unique: it may contain several entries with the same name (indicating
    a multiple-viewport configuration). The entries corresponding to the active
    viewport configuration all have the name *ACTIVE. The first such entry
    describes the current viewport.
    Since the name is not unique, we use List as a container'''
    
    def clone(self) -> any:
        '''The clone.
        
        :returns: The :py:class:`any`.'''
        ...
    
    def add_range(self, objects : List[aspose.cad.fileformats.cad.cadtables.CadVportTableObject]) -> None:
        '''Adds the range of the objects to container.
        
        :param objects: The objects array.'''
        ...
    
    @property
    def cad_symbol_table_group_codes(self) -> aspose.cad.fileformats.cad.cadtables.CadSymbolTableGroupCodes:
        ...
    
    @cad_symbol_table_group_codes.setter
    def cad_symbol_table_group_codes(self, value : aspose.cad.fileformats.cad.cadtables.CadSymbolTableGroupCodes):
        ...
    
    ...

class DwgImage(CadImage):
    '''Dwg image class'''
    
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
    
    @overload
    def get_bounds(self) -> None:
        '''Fills Bounds property (contain minimum and maximum point of entity) for all entities.'''
        ...
    
    @overload
    def get_bounds(self, entity : aspose.cad.fileformats.cad.cadobjects.CadEntityBase) -> None:
        '''Fills Bounds property (contains minimum and maximum point) for entity.'''
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
    
    def update_size(self, include_beyond_size : bool) -> None:
        '''Updates size of an image after changes, that may affect initial size, e.g. removing of entities.
        MinPoint, MaxPoint, Width and Height properties of image are updated.
        
        :param include_beyond_size: Determines whether entities that lie outside the boundaries of the image size
        should affect the new image size.'''
        ...
    
    def change_custom_property(self, custom_prop_name : str, new_custom_prop_value : str) -> None:
        '''Updates a custom property and related CAD field objects with a new value.
        
        :param custom_prop_name: The custom property name.
        :param new_custom_prop_value: The new property value.'''
        ...
    
    def add_custom_property(self, custom_prop_name : str, custom_prop_value : str) -> None:
        '''Adds a custom property to the drawing
        
        :param custom_prop_name: The name of the custom property to add.
        :param custom_prop_value: The value of the custom property.'''
        ...
    
    def remove_custom_property(self, custom_prop_name : str) -> None:
        '''Removes a custom property from the drawing.
        
        :param custom_prop_name: The name of the custom property to remove.'''
        ...
    
    def try_remove_entity(self, entity_to_remove : aspose.cad.fileformats.cad.cadobjects.CadEntityBase) -> None:
        '''Removes entity from blocks for DWG format.
        
        :param entity_to_remove: Entity to be removed.'''
        ...
    
    def add_entity(self, entity : aspose.cad.fileformats.cad.cadobjects.CadEntityBase) -> None:
        '''Add entity to drawing'''
        ...
    
    def add_layer(self, layer_name : str) -> aspose.cad.fileformats.cad.cadtables.CadLayerTable:
        '''Add layer to drawing
        
        :param layer_name: The layer name'''
        ...
    
    def add_block(self, block_name : str, layer_name : str) -> None:
        '''Adds a new block to the drawing.
        
        :param block_name: The name of the block.
        :param layer_name: The layer name.'''
        ...
    
    def add_entity_to_block(self, block_name : str, entity : aspose.cad.fileformats.cad.cadobjects.CadEntityBase) -> None:
        '''Adds an entity to the specified block.
        
        :param block_name: The name of the block.
        :param entity: The entity to add.'''
        ...
    
    def insert_block(self, block_name : str, insert_points : List[aspose.cad.fileformats.cad.cadobjects.Cad3DPoint]) -> None:
        '''Inserts a block into the drawing at the specified points.
        
        :param block_name: The name of the block to insert.
        :param insert_points: The insertion points for the block.'''
        ...
    
    def add_ole_2_frame(self, image_data : bytes, insert_point : aspose.cad.fileformats.cad.cadobjects.Cad3DPoint, width : Optional[float], height : Optional[float], lock_aspect_ratio : bool) -> None:
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
    def active_page(self) -> aspose.cad.fileformats.cad.cadobjects.CadLayout:
        ...
    
    @property
    def default_line_weight(self) -> float:
        ...
    
    @default_line_weight.setter
    def default_line_weight(self, value : float):
        ...
    
    @property
    def default_font(self) -> str:
        ...
    
    @default_font.setter
    def default_font(self, value : str):
        ...
    
    @property
    def file_encoding(self) -> aspose.cad.CodePages:
        ...
    
    @file_encoding.setter
    def file_encoding(self, value : aspose.cad.CodePages):
        ...
    
    @property
    def application_version(self) -> int:
        ...
    
    @application_version.setter
    def application_version(self, value : int):
        ...
    
    @property
    def maintenance_version(self) -> int:
        ...
    
    @maintenance_version.setter
    def maintenance_version(self, value : int):
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
    def line_types(self) -> aspose.cad.fileformats.cad.CadLineTypesDictionary:
        ...
    
    @line_types.setter
    def line_types(self, value : aspose.cad.fileformats.cad.CadLineTypesDictionary):
        ...
    
    @property
    def block_entities(self) -> aspose.cad.fileformats.cad.CadBlockDictionary:
        ...
    
    @block_entities.setter
    def block_entities(self, value : aspose.cad.fileformats.cad.CadBlockDictionary):
        ...
    
    @property
    def class_entities(self) -> aspose.cad.fileformats.cad.CadClassList:
        ...
    
    @class_entities.setter
    def class_entities(self, value : aspose.cad.fileformats.cad.CadClassList):
        ...
    
    @property
    def thumbnail_image(self) -> aspose.cad.fileformats.cad.cadobjects.CadThumbnailImage:
        ...
    
    @thumbnail_image.setter
    def thumbnail_image(self, value : aspose.cad.fileformats.cad.cadobjects.CadThumbnailImage):
        ...
    
    @property
    def blocks_tables(self) -> aspose.cad.fileformats.cad.CadBlockRecordList:
        ...
    
    @blocks_tables.setter
    def blocks_tables(self, value : aspose.cad.fileformats.cad.CadBlockRecordList):
        ...
    
    @property
    def dimension_styles(self) -> aspose.cad.fileformats.cad.CadDimensionDictionary:
        ...
    
    @dimension_styles.setter
    def dimension_styles(self, value : aspose.cad.fileformats.cad.CadDimensionDictionary):
        ...
    
    @property
    def entities(self) -> Iterable[aspose.cad.fileformats.cad.cadobjects.CadEntityBase]:
        '''Gets the entities.'''
        ...
    
    @entities.setter
    def entities(self, value : Iterable[aspose.cad.fileformats.cad.cadobjects.CadEntityBase]):
        '''Sets the entities.'''
        ...
    
    @property
    def objects(self) -> List[aspose.cad.fileformats.cad.cadobjects.CadBaseObject]:
        '''Gets the objects.'''
        ...
    
    @objects.setter
    def objects(self, value : List[aspose.cad.fileformats.cad.cadobjects.CadBaseObject]):
        '''Sets the objects.'''
        ...
    
    @property
    def layers(self) -> aspose.cad.fileformats.cad.CadLayersList:
        '''Gets the layers.'''
        ...
    
    @layers.setter
    def layers(self, value : aspose.cad.fileformats.cad.CadLayersList):
        '''Sets the layers.'''
        ...
    
    @property
    def max_point(self) -> aspose.cad.fileformats.cad.cadobjects.Cad3DPoint:
        ...
    
    @property
    def min_point(self) -> aspose.cad.fileformats.cad.cadobjects.Cad3DPoint:
        ...
    
    @property
    def styles(self) -> aspose.cad.fileformats.cad.CadStylesList:
        '''Gets the styles.'''
        ...
    
    @styles.setter
    def styles(self, value : aspose.cad.fileformats.cad.CadStylesList):
        '''Sets the styles.'''
        ...
    
    @property
    def header(self) -> aspose.cad.fileformats.cad.cadobjects.CadHeader:
        '''Gets the header.'''
        ...
    
    @header.setter
    def header(self, value : aspose.cad.fileformats.cad.cadobjects.CadHeader):
        '''Sets the header.'''
        ...
    
    @property
    def view_ports(self) -> aspose.cad.fileformats.cad.CadVportList:
        ...
    
    @view_ports.setter
    def view_ports(self, value : aspose.cad.fileformats.cad.CadVportList):
        ...
    
    @property
    def views(self) -> aspose.cad.fileformats.cad.CadViewList:
        '''Gets the views.'''
        ...
    
    @views.setter
    def views(self, value : aspose.cad.fileformats.cad.CadViewList):
        '''Sets the views.'''
        ...
    
    @property
    def uc_ss(self) -> aspose.cad.fileformats.cad.CadUcsList:
        ...
    
    @uc_ss.setter
    def uc_ss(self, value : aspose.cad.fileformats.cad.CadUcsList):
        ...
    
    @property
    def cad_acds(self) -> aspose.cad.fileformats.cad.CadAcdsList:
        ...
    
    @cad_acds.setter
    def cad_acds(self, value : aspose.cad.fileformats.cad.CadAcdsList):
        ...
    
    @property
    def app_id_tables(self) -> aspose.cad.fileformats.cad.CadAppIdDictionary:
        ...
    
    @app_id_tables.setter
    def app_id_tables(self, value : aspose.cad.fileformats.cad.CadAppIdDictionary):
        ...
    
    ...

class DxfImage(CadImage):
    '''Dxf image class'''
    
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
    
    @overload
    def get_bounds(self) -> None:
        '''Fills Bounds property (contain minimum and maximum point of entity) for all entities.'''
        ...
    
    @overload
    def get_bounds(self, entity : aspose.cad.fileformats.cad.cadobjects.CadEntityBase) -> None:
        '''Fills Bounds property (contains minimum and maximum point) for entity.'''
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
    
    def update_size(self, include_beyond_size : bool) -> None:
        '''Updates size of an image after changes, that may affect initial size, e.g. removing of entities.
        MinPoint, MaxPoint, Width and Height properties of image are updated.
        
        :param include_beyond_size: Determines whether entities that lie outside the boundaries of the image size
        should affect the new image size.'''
        ...
    
    def change_custom_property(self, custom_prop_name : str, new_custom_prop_value : str) -> None:
        '''Updates a custom property and related CAD field objects with a new value.
        
        :param custom_prop_name: The custom property name.
        :param new_custom_prop_value: The new property value.'''
        ...
    
    def add_custom_property(self, custom_prop_name : str, custom_prop_value : str) -> None:
        '''Adds a custom property to the drawing
        
        :param custom_prop_name: The name of the custom property to add.
        :param custom_prop_value: The value of the custom property.'''
        ...
    
    def remove_custom_property(self, custom_prop_name : str) -> None:
        '''Removes a custom property from the drawing.
        
        :param custom_prop_name: The name of the custom property to remove.'''
        ...
    
    def try_remove_entity(self, entity_to_remove : aspose.cad.fileformats.cad.cadobjects.CadEntityBase) -> None:
        '''Removes entity from blocks for DWG format.
        
        :param entity_to_remove: Entity to be removed.'''
        ...
    
    def add_entity(self, entity : aspose.cad.fileformats.cad.cadobjects.CadEntityBase) -> None:
        '''Adds entity.
        
        :param entity: Entity to add.'''
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
    def active_page(self) -> aspose.cad.fileformats.cad.cadobjects.CadLayout:
        ...
    
    @property
    def default_line_weight(self) -> float:
        ...
    
    @default_line_weight.setter
    def default_line_weight(self, value : float):
        ...
    
    @property
    def default_font(self) -> str:
        ...
    
    @default_font.setter
    def default_font(self, value : str):
        ...
    
    @property
    def file_encoding(self) -> aspose.cad.CodePages:
        ...
    
    @file_encoding.setter
    def file_encoding(self, value : aspose.cad.CodePages):
        ...
    
    @property
    def application_version(self) -> int:
        ...
    
    @application_version.setter
    def application_version(self, value : int):
        ...
    
    @property
    def maintenance_version(self) -> int:
        ...
    
    @maintenance_version.setter
    def maintenance_version(self, value : int):
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
    def line_types(self) -> aspose.cad.fileformats.cad.CadLineTypesDictionary:
        ...
    
    @line_types.setter
    def line_types(self, value : aspose.cad.fileformats.cad.CadLineTypesDictionary):
        ...
    
    @property
    def block_entities(self) -> aspose.cad.fileformats.cad.CadBlockDictionary:
        ...
    
    @block_entities.setter
    def block_entities(self, value : aspose.cad.fileformats.cad.CadBlockDictionary):
        ...
    
    @property
    def class_entities(self) -> aspose.cad.fileformats.cad.CadClassList:
        ...
    
    @class_entities.setter
    def class_entities(self, value : aspose.cad.fileformats.cad.CadClassList):
        ...
    
    @property
    def thumbnail_image(self) -> aspose.cad.fileformats.cad.cadobjects.CadThumbnailImage:
        ...
    
    @thumbnail_image.setter
    def thumbnail_image(self, value : aspose.cad.fileformats.cad.cadobjects.CadThumbnailImage):
        ...
    
    @property
    def blocks_tables(self) -> aspose.cad.fileformats.cad.CadBlockRecordList:
        ...
    
    @blocks_tables.setter
    def blocks_tables(self, value : aspose.cad.fileformats.cad.CadBlockRecordList):
        ...
    
    @property
    def dimension_styles(self) -> aspose.cad.fileformats.cad.CadDimensionDictionary:
        ...
    
    @dimension_styles.setter
    def dimension_styles(self, value : aspose.cad.fileformats.cad.CadDimensionDictionary):
        ...
    
    @property
    def entities(self) -> Iterable[aspose.cad.fileformats.cad.cadobjects.CadEntityBase]:
        '''Gets the entities.'''
        ...
    
    @entities.setter
    def entities(self, value : Iterable[aspose.cad.fileformats.cad.cadobjects.CadEntityBase]):
        '''Sets the entities.'''
        ...
    
    @property
    def objects(self) -> List[aspose.cad.fileformats.cad.cadobjects.CadBaseObject]:
        '''Gets the objects.'''
        ...
    
    @objects.setter
    def objects(self, value : List[aspose.cad.fileformats.cad.cadobjects.CadBaseObject]):
        '''Sets the objects.'''
        ...
    
    @property
    def layers(self) -> aspose.cad.fileformats.cad.CadLayersList:
        '''Gets the layers.'''
        ...
    
    @layers.setter
    def layers(self, value : aspose.cad.fileformats.cad.CadLayersList):
        '''Sets the layers.'''
        ...
    
    @property
    def max_point(self) -> aspose.cad.fileformats.cad.cadobjects.Cad3DPoint:
        ...
    
    @property
    def min_point(self) -> aspose.cad.fileformats.cad.cadobjects.Cad3DPoint:
        ...
    
    @property
    def styles(self) -> aspose.cad.fileformats.cad.CadStylesList:
        '''Gets the styles.'''
        ...
    
    @styles.setter
    def styles(self, value : aspose.cad.fileformats.cad.CadStylesList):
        '''Sets the styles.'''
        ...
    
    @property
    def header(self) -> aspose.cad.fileformats.cad.cadobjects.CadHeader:
        '''Gets the header.'''
        ...
    
    @header.setter
    def header(self, value : aspose.cad.fileformats.cad.cadobjects.CadHeader):
        '''Sets the header.'''
        ...
    
    @property
    def view_ports(self) -> aspose.cad.fileformats.cad.CadVportList:
        ...
    
    @view_ports.setter
    def view_ports(self, value : aspose.cad.fileformats.cad.CadVportList):
        ...
    
    @property
    def views(self) -> aspose.cad.fileformats.cad.CadViewList:
        '''Gets the views.'''
        ...
    
    @views.setter
    def views(self, value : aspose.cad.fileformats.cad.CadViewList):
        '''Sets the views.'''
        ...
    
    @property
    def uc_ss(self) -> aspose.cad.fileformats.cad.CadUcsList:
        ...
    
    @uc_ss.setter
    def uc_ss(self, value : aspose.cad.fileformats.cad.CadUcsList):
        ...
    
    @property
    def cad_acds(self) -> aspose.cad.fileformats.cad.CadAcdsList:
        ...
    
    @cad_acds.setter
    def cad_acds(self, value : aspose.cad.fileformats.cad.CadAcdsList):
        ...
    
    @property
    def app_id_tables(self) -> aspose.cad.fileformats.cad.CadAppIdDictionary:
        ...
    
    @app_id_tables.setter
    def app_id_tables(self, value : aspose.cad.fileformats.cad.CadAppIdDictionary):
        ...
    
    ...

class CadDrawTypeMode:
    '''Represents possible modes for colorization of objects.'''
    
    @classmethod
    @property
    def USE_DRAW_COLOR(cls) -> CadDrawTypeMode:
        '''Allows to use common color.'''
        ...
    
    @classmethod
    @property
    def USE_OBJECT_COLOR(cls) -> CadDrawTypeMode:
        '''Allows to use separate color for every object.'''
        ...
    
    ...

class CadEntityAttribute:
    '''Entities enum'''
    
    @classmethod
    @property
    def CAD_APP_ENTITY_NAME(cls) -> CadEntityAttribute:
        '''APP: entity name (changes each time a drawing is opened)'''
        ...
    
    @classmethod
    @property
    def CAD000(cls) -> CadEntityAttribute:
        '''Entity type'''
        ...
    
    @classmethod
    @property
    def CAD001(cls) -> CadEntityAttribute:
        '''Entity attribute value'''
        ...
    
    @classmethod
    @property
    def CAD002(cls) -> CadEntityAttribute:
        '''The Cad two'''
        ...
    
    @classmethod
    @property
    def CAD003(cls) -> CadEntityAttribute:
        '''The Cad 003.'''
        ...
    
    @classmethod
    @property
    def CAD005(cls) -> CadEntityAttribute:
        '''Handle of the object'''
        ...
    
    @classmethod
    @property
    def CAD102(cls) -> CadEntityAttribute:
        '''102 Start or End of application-defined group “{application_name” (optional)'''
        ...
    
    @classmethod
    @property
    def CAD330(cls) -> CadEntityAttribute:
        '''Soft-pointer ID/handle to.. depends on situation'''
        ...
    
    @classmethod
    @property
    def CAD331(cls) -> CadEntityAttribute:
        '''The Cad 331.'''
        ...
    
    @classmethod
    @property
    def CAD360(cls) -> CadEntityAttribute:
        '''Hard-owner ID/handle to owner dictionary (optional)'''
        ...
    
    @classmethod
    @property
    def CAD100(cls) -> CadEntityAttribute:
        '''Subclass marker'''
        ...
    
    @classmethod
    @property
    def CAD101(cls) -> CadEntityAttribute:
        '''The Cad 101'''
        ...
    
    @classmethod
    @property
    def CAD067(cls) -> CadEntityAttribute:
        '''Absent or zero indicates entity is in model space. 1 indicates entity is in paper space (optional)'''
        ...
    
    @classmethod
    @property
    def CAD410(cls) -> CadEntityAttribute:
        '''APP: layout tab name'''
        ...
    
    @classmethod
    @property
    def CAD008(cls) -> CadEntityAttribute:
        '''Layer name'''
        ...
    
    @classmethod
    @property
    def CAD006(cls) -> CadEntityAttribute:
        '''Linetype name (present if not BYLAYER). The special name BYBLOCK indicates a floating linetype (optional)'''
        ...
    
    @classmethod
    @property
    def CAD007(cls) -> CadEntityAttribute:
        '''The Cad007'''
        ...
    
    @classmethod
    @property
    def CAD347(cls) -> CadEntityAttribute:
        '''Hard-pointer ID/handle to material object (present if not BYLAYER)'''
        ...
    
    @classmethod
    @property
    def CAD350(cls) -> CadEntityAttribute:
        '''The Cad350'''
        ...
    
    @classmethod
    @property
    def CAD062(cls) -> CadEntityAttribute:
        '''Color number (present if not BYLAYER);'''
        ...
    
    @classmethod
    @property
    def CAD105(cls) -> CadEntityAttribute:
        '''The cad105'''
        ...
    
    @classmethod
    @property
    def CAD160(cls) -> CadEntityAttribute:
        '''The cad 160.'''
        ...
    
    @classmethod
    @property
    def CAD161(cls) -> CadEntityAttribute:
        '''The cad 161.'''
        ...
    
    @classmethod
    @property
    def CAD162(cls) -> CadEntityAttribute:
        '''The cad 160.'''
        ...
    
    @classmethod
    @property
    def CAD064(cls) -> CadEntityAttribute:
        '''The Cad 064.'''
        ...
    
    @classmethod
    @property
    def CAD065(cls) -> CadEntityAttribute:
        '''The Cad 065.'''
        ...
    
    @classmethod
    @property
    def CAD068(cls) -> CadEntityAttribute:
        '''The Cad 068.'''
        ...
    
    @classmethod
    @property
    def CAD069(cls) -> CadEntityAttribute:
        '''The Cad 069.'''
        ...
    
    @classmethod
    @property
    def CAD370(cls) -> CadEntityAttribute:
        '''Lineweight enum value. Stored and moved around as a 16-bit integer'''
        ...
    
    @classmethod
    @property
    def CAD048(cls) -> CadEntityAttribute:
        '''Linetype scale (optional)'''
        ...
    
    @classmethod
    @property
    def CAD049(cls) -> CadEntityAttribute:
        '''The Cad049'''
        ...
    
    @classmethod
    @property
    def CAD060(cls) -> CadEntityAttribute:
        '''Object visibility (optional): 0 = Visible; 1 = Invisible'''
        ...
    
    @classmethod
    @property
    def CAD092(cls) -> CadEntityAttribute:
        '''Number of bytes in the proxy entity graphics represented in the subsequent 310 groups,
        which are binary chunk records (optional)'''
        ...
    
    @classmethod
    @property
    def CAD310(cls) -> CadEntityAttribute:
        '''Proxy entity graphics data (multiple lines; 256 characters max. per line)'''
        ...
    
    @classmethod
    @property
    def CAD420(cls) -> CadEntityAttribute:
        '''A 24-bit color value that should be dealt with in terms of bytes with values
        of 0 to 255. The lowest byte is the blue value, the middle byte is the
        green value, and the third byte is the red value. The top byte is always 0'''
        ...
    
    @classmethod
    @property
    def CAD421(cls) -> CadEntityAttribute:
        '''The Cad 421.'''
        ...
    
    @classmethod
    @property
    def CAD422(cls) -> CadEntityAttribute:
        '''The Cad 422.'''
        ...
    
    @classmethod
    @property
    def CAD423(cls) -> CadEntityAttribute:
        '''The Cad 423.'''
        ...
    
    @classmethod
    @property
    def CAD424(cls) -> CadEntityAttribute:
        '''The Cad 424.'''
        ...
    
    @classmethod
    @property
    def CAD425(cls) -> CadEntityAttribute:
        '''The Cad 425.'''
        ...
    
    @classmethod
    @property
    def CAD426(cls) -> CadEntityAttribute:
        '''The Cad 426.'''
        ...
    
    @classmethod
    @property
    def CAD427(cls) -> CadEntityAttribute:
        '''The Cad 427.'''
        ...
    
    @classmethod
    @property
    def CAD428(cls) -> CadEntityAttribute:
        '''The Cad 428.'''
        ...
    
    @classmethod
    @property
    def CAD429(cls) -> CadEntityAttribute:
        '''The Cad 429.'''
        ...
    
    @classmethod
    @property
    def CAD430(cls) -> CadEntityAttribute:
        '''The Cad 430.'''
        ...
    
    @classmethod
    @property
    def CAD431(cls) -> CadEntityAttribute:
        '''The Cad 431.'''
        ...
    
    @classmethod
    @property
    def CAD432(cls) -> CadEntityAttribute:
        '''The Cad 432.'''
        ...
    
    @classmethod
    @property
    def CAD433(cls) -> CadEntityAttribute:
        '''The Cad 433.'''
        ...
    
    @classmethod
    @property
    def CAD434(cls) -> CadEntityAttribute:
        '''The Cad 434.'''
        ...
    
    @classmethod
    @property
    def CAD435(cls) -> CadEntityAttribute:
        '''The Cad 435.'''
        ...
    
    @classmethod
    @property
    def CAD436(cls) -> CadEntityAttribute:
        '''The Cad 436.'''
        ...
    
    @classmethod
    @property
    def CAD437(cls) -> CadEntityAttribute:
        '''The Cad 437.'''
        ...
    
    @classmethod
    @property
    def CAD438(cls) -> CadEntityAttribute:
        '''The Cad 438.'''
        ...
    
    @classmethod
    @property
    def CAD439(cls) -> CadEntityAttribute:
        '''The Cad 439.'''
        ...
    
    @classmethod
    @property
    def CAD440(cls) -> CadEntityAttribute:
        '''Transparency value.'''
        ...
    
    @classmethod
    @property
    def CAD441(cls) -> CadEntityAttribute:
        '''The Cad 441.'''
        ...
    
    @classmethod
    @property
    def CAD390(cls) -> CadEntityAttribute:
        '''390 Hard-pointer ID/handle to the plot style object'''
        ...
    
    @classmethod
    @property
    def CAD284(cls) -> CadEntityAttribute:
        '''Shadow mode'''
        ...
    
    @classmethod
    @property
    def CAD090(cls) -> CadEntityAttribute:
        '''Points count'''
        ...
    
    @classmethod
    @property
    def CAD010(cls) -> CadEntityAttribute:
        '''First point or corner X'''
        ...
    
    @classmethod
    @property
    def CAD020(cls) -> CadEntityAttribute:
        '''First point or corner Y'''
        ...
    
    @classmethod
    @property
    def CAD030(cls) -> CadEntityAttribute:
        '''First point or corner Z'''
        ...
    
    @classmethod
    @property
    def CAD011(cls) -> CadEntityAttribute:
        '''End point or corner X'''
        ...
    
    @classmethod
    @property
    def CAD021(cls) -> CadEntityAttribute:
        '''End point or corner Y'''
        ...
    
    @classmethod
    @property
    def CAD022(cls) -> CadEntityAttribute:
        '''The Cad022'''
        ...
    
    @classmethod
    @property
    def CAD031(cls) -> CadEntityAttribute:
        '''End point or corner Z'''
        ...
    
    @classmethod
    @property
    def CAD012(cls) -> CadEntityAttribute:
        '''Start tangent X'''
        ...
    
    @classmethod
    @property
    def CAD032(cls) -> CadEntityAttribute:
        '''Start tangent Z'''
        ...
    
    @classmethod
    @property
    def CAD013(cls) -> CadEntityAttribute:
        '''End tangent X'''
        ...
    
    @classmethod
    @property
    def CAD016(cls) -> CadEntityAttribute:
        '''The Cad 016.'''
        ...
    
    @classmethod
    @property
    def CAD023(cls) -> CadEntityAttribute:
        '''End tangent Y'''
        ...
    
    @classmethod
    @property
    def CAD026(cls) -> CadEntityAttribute:
        '''The Cad 026.'''
        ...
    
    @classmethod
    @property
    def CAD033(cls) -> CadEntityAttribute:
        '''End tangent Z'''
        ...
    
    @classmethod
    @property
    def CAD036(cls) -> CadEntityAttribute:
        '''The Cad 036.'''
        ...
    
    @classmethod
    @property
    def CAD040(cls) -> CadEntityAttribute:
        '''Radius or width'''
        ...
    
    @classmethod
    @property
    def CAD050(cls) -> CadEntityAttribute:
        '''First angle or Rotation angle or...'''
        ...
    
    @classmethod
    @property
    def CAD051(cls) -> CadEntityAttribute:
        '''First angle or Rotation angle or...'''
        ...
    
    @classmethod
    @property
    def CAD053(cls) -> CadEntityAttribute:
        '''The Cad fifty three'''
        ...
    
    @classmethod
    @property
    def CAD210(cls) -> CadEntityAttribute:
        '''Extrusion Direction X Value'''
        ...
    
    @classmethod
    @property
    def CAD211(cls) -> CadEntityAttribute:
        '''Extrusion Direction Y Value'''
        ...
    
    @classmethod
    @property
    def CAD212(cls) -> CadEntityAttribute:
        '''Extrusion Direction Z Value'''
        ...
    
    @classmethod
    @property
    def CAD220(cls) -> CadEntityAttribute:
        '''Extrusion Direction Y Value'''
        ...
    
    @classmethod
    @property
    def CAD221(cls) -> CadEntityAttribute:
        '''The cad 221 attribute'''
        ...
    
    @classmethod
    @property
    def CAD222(cls) -> CadEntityAttribute:
        '''The cad 222 attribute'''
        ...
    
    @classmethod
    @property
    def CAD230(cls) -> CadEntityAttribute:
        '''Extrusion Direction Z Value'''
        ...
    
    @classmethod
    @property
    def CAD231(cls) -> CadEntityAttribute:
        '''The cad 231 attribute'''
        ...
    
    @classmethod
    @property
    def CAD232(cls) -> CadEntityAttribute:
        '''The cad 232 attribute'''
        ...
    
    @classmethod
    @property
    def CAD213(cls) -> CadEntityAttribute:
        '''The annotation placement point offset x value'''
        ...
    
    @classmethod
    @property
    def CAD223(cls) -> CadEntityAttribute:
        '''The annotation placement point offset y value'''
        ...
    
    @classmethod
    @property
    def CAD233(cls) -> CadEntityAttribute:
        '''The annotation placement point offset z value'''
        ...
    
    @classmethod
    @property
    def CAD039(cls) -> CadEntityAttribute:
        '''Thickness (optional; default = 0)'''
        ...
    
    @classmethod
    @property
    def CAD066(cls) -> CadEntityAttribute:
        '''Obsolete; formerly an “entities follow flag” (optional; ignore if present)'''
        ...
    
    @classmethod
    @property
    def CAD041(cls) -> CadEntityAttribute:
        '''Default end width (optional; default = 0)'''
        ...
    
    @classmethod
    @property
    def CAD071(cls) -> CadEntityAttribute:
        '''Polygon mesh M vertex count (optional; default = 0)'''
        ...
    
    @classmethod
    @property
    def CAD072(cls) -> CadEntityAttribute:
        '''Polygon mesh N vertex count (optional; default = 0)'''
        ...
    
    @classmethod
    @property
    def CAD073(cls) -> CadEntityAttribute:
        '''Smooth surface M density (optional; default = 0)'''
        ...
    
    @classmethod
    @property
    def CAD074(cls) -> CadEntityAttribute:
        '''Smooth surface N density (optional; default = 0)'''
        ...
    
    @classmethod
    @property
    def CAD075(cls) -> CadEntityAttribute:
        '''Curves and smooth surface type (optional; default = 0); integer codes, not bit-coded:'''
        ...
    
    @classmethod
    @property
    def CAD076(cls) -> CadEntityAttribute:
        '''The Cad 076.'''
        ...
    
    @classmethod
    @property
    def CAD078(cls) -> CadEntityAttribute:
        '''The Cad 078.'''
        ...
    
    @classmethod
    @property
    def CAD079(cls) -> CadEntityAttribute:
        '''The Cad 079.'''
        ...
    
    @classmethod
    @property
    def CAD042(cls) -> CadEntityAttribute:
        '''Bulge (optional; default is 0). The bulge is the tangent of one fourth the included angle for an
        arc segment, made negative if the arc goes clockwise from the start point to the endpoint. A
        bulge of 0 indicates a straight segment, and a bulge of 1 is a semicircle'''
        ...
    
    @classmethod
    @property
    def CAD043(cls) -> CadEntityAttribute:
        '''Control Point Tolerance'''
        ...
    
    @classmethod
    @property
    def CAD070(cls) -> CadEntityAttribute:
        '''Vertex flags'''
        ...
    
    @classmethod
    @property
    def CAD091(cls) -> CadEntityAttribute:
        '''Vertex identifier'''
        ...
    
    @classmethod
    @property
    def CAD290(cls) -> CadEntityAttribute:
        '''Handendness of the helix'''
        ...
    
    @classmethod
    @property
    def CAD280(cls) -> CadEntityAttribute:
        '''Constrain type'''
        ...
    
    @classmethod
    @property
    def CAD281(cls) -> CadEntityAttribute:
        '''The Cad 281.'''
        ...
    
    @classmethod
    @property
    def CAD282(cls) -> CadEntityAttribute:
        '''The Cad 282.'''
        ...
    
    @classmethod
    @property
    def CAD283(cls) -> CadEntityAttribute:
        '''The Cad 283.'''
        ...
    
    @classmethod
    @property
    def CAD289(cls) -> CadEntityAttribute:
        '''The Cad 289.'''
        ...
    
    @classmethod
    @property
    def CAD340(cls) -> CadEntityAttribute:
        '''Leader Style Id'''
        ...
    
    @classmethod
    @property
    def CAD341(cls) -> CadEntityAttribute:
        '''Leader Style Id'''
        ...
    
    @classmethod
    @property
    def CAD171(cls) -> CadEntityAttribute:
        '''LeaderLine wight'''
        ...
    
    @classmethod
    @property
    def CAD291(cls) -> CadEntityAttribute:
        '''Enable Dogleg'''
        ...
    
    @classmethod
    @property
    def CAD172(cls) -> CadEntityAttribute:
        '''Content Type'''
        ...
    
    @classmethod
    @property
    def CAD343(cls) -> CadEntityAttribute:
        '''Text Style ID'''
        ...
    
    @classmethod
    @property
    def CAD173(cls) -> CadEntityAttribute:
        '''Text Left Attachment Type'''
        ...
    
    @classmethod
    @property
    def CAD271(cls) -> CadEntityAttribute:
        '''Text attachment direction'''
        ...
    
    @classmethod
    @property
    def CAD272(cls) -> CadEntityAttribute:
        '''Bottom text attachment direction'''
        ...
    
    @classmethod
    @property
    def CAD273(cls) -> CadEntityAttribute:
        '''Top text attachment direction'''
        ...
    
    @classmethod
    @property
    def CAD275(cls) -> CadEntityAttribute:
        '''The Cad 275.'''
        ...
    
    @classmethod
    @property
    def CAD276(cls) -> CadEntityAttribute:
        '''The Cad 276.'''
        ...
    
    @classmethod
    @property
    def CAD277(cls) -> CadEntityAttribute:
        '''The Cad 277.'''
        ...
    
    @classmethod
    @property
    def CAD278(cls) -> CadEntityAttribute:
        '''The Cad 278.'''
        ...
    
    @classmethod
    @property
    def CAD279(cls) -> CadEntityAttribute:
        '''The Cad 279.'''
        ...
    
    @classmethod
    @property
    def CAD178(cls) -> CadEntityAttribute:
        '''Text Align in IPE'''
        ...
    
    @classmethod
    @property
    def CAD179(cls) -> CadEntityAttribute:
        '''Text Attachment Point'''
        ...
    
    @classmethod
    @property
    def CAD294(cls) -> CadEntityAttribute:
        '''Text Direction Negative'''
        ...
    
    @classmethod
    @property
    def CAD302(cls) -> CadEntityAttribute:
        '''Block Attribute Text String'''
        ...
    
    @classmethod
    @property
    def CAD044(cls) -> CadEntityAttribute:
        '''Block Attribute Width'''
        ...
    
    @classmethod
    @property
    def CAD177(cls) -> CadEntityAttribute:
        '''Block Attribute Index'''
        ...
    
    @classmethod
    @property
    def CAD345(cls) -> CadEntityAttribute:
        '''Arrowhead ID'''
        ...
    
    @classmethod
    @property
    def CAD094(cls) -> CadEntityAttribute:
        '''Arrowhead Index'''
        ...
    
    @classmethod
    @property
    def CAD293(cls) -> CadEntityAttribute:
        '''Enable Annotation Scale'''
        ...
    
    @classmethod
    @property
    def CAD176(cls) -> CadEntityAttribute:
        '''Block Content Connection Type'''
        ...
    
    @classmethod
    @property
    def CAD093(cls) -> CadEntityAttribute:
        '''Block Content Color'''
        ...
    
    @classmethod
    @property
    def CAD292(cls) -> CadEntityAttribute:
        '''Enable Frame Text'''
        ...
    
    @classmethod
    @property
    def CAD344(cls) -> CadEntityAttribute:
        '''Block Content ID'''
        ...
    
    @classmethod
    @property
    def CAD174(cls) -> CadEntityAttribute:
        '''Text Angle Type'''
        ...
    
    @classmethod
    @property
    def CAD175(cls) -> CadEntityAttribute:
        '''Text Alignment Type'''
        ...
    
    @classmethod
    @property
    def CAD095(cls) -> CadEntityAttribute:
        '''Text Right Attachment Type'''
        ...
    
    @classmethod
    @property
    def CAD096(cls) -> CadEntityAttribute:
        '''The Cad 096.'''
        ...
    
    @classmethod
    @property
    def CAD342(cls) -> CadEntityAttribute:
        '''Arrowhead ID'''
        ...
    
    @classmethod
    @property
    def CAD170(cls) -> CadEntityAttribute:
        '''Leader Line Type'''
        ...
    
    @classmethod
    @property
    def CAD140(cls) -> CadEntityAttribute:
        '''Arrowhead Size'''
        ...
    
    @classmethod
    @property
    def CAD145(cls) -> CadEntityAttribute:
        '''Landing Gap'''
        ...
    
    @classmethod
    @property
    def CAD303(cls) -> CadEntityAttribute:
        '''The cad 303 attribute'''
        ...
    
    @classmethod
    @property
    def CAD304(cls) -> CadEntityAttribute:
        '''Default Text Contents'''
        ...
    
    @classmethod
    @property
    def CAD305(cls) -> CadEntityAttribute:
        '''The cad 305 attribute'''
        ...
    
    @classmethod
    @property
    def CAD306(cls) -> CadEntityAttribute:
        '''The cad 306 attribute'''
        ...
    
    @classmethod
    @property
    def CAD307(cls) -> CadEntityAttribute:
        '''The cad 307 attribute'''
        ...
    
    @classmethod
    @property
    def CAD308(cls) -> CadEntityAttribute:
        '''The cad 308 attribute'''
        ...
    
    @classmethod
    @property
    def CAD045(cls) -> CadEntityAttribute:
        '''Line Spacing Factor'''
        ...
    
    @classmethod
    @property
    def CAD141(cls) -> CadEntityAttribute:
        '''Text Background Scale Factor'''
        ...
    
    @classmethod
    @property
    def CAD142(cls) -> CadEntityAttribute:
        '''Text Column Width'''
        ...
    
    @classmethod
    @property
    def CAD143(cls) -> CadEntityAttribute:
        '''Text Column Gutter Width'''
        ...
    
    @classmethod
    @property
    def CAD144(cls) -> CadEntityAttribute:
        '''144 Text Column Height'''
        ...
    
    @classmethod
    @property
    def CAD295(cls) -> CadEntityAttribute:
        '''Text Use Word Break'''
        ...
    
    @classmethod
    @property
    def CAD296(cls) -> CadEntityAttribute:
        '''296 Enumeration'''
        ...
    
    @classmethod
    @property
    def CAD298(cls) -> CadEntityAttribute:
        '''The cad 298'''
        ...
    
    @classmethod
    @property
    def CAD014(cls) -> CadEntityAttribute:
        '''Block Content Normal Direction X'''
        ...
    
    @classmethod
    @property
    def CAD024(cls) -> CadEntityAttribute:
        '''Block Content Normal Direction Y'''
        ...
    
    @classmethod
    @property
    def CAD034(cls) -> CadEntityAttribute:
        '''Block Content Normal Direction Z'''
        ...
    
    @classmethod
    @property
    def CAD015(cls) -> CadEntityAttribute:
        '''Block Content Position X'''
        ...
    
    @classmethod
    @property
    def CAD025(cls) -> CadEntityAttribute:
        '''Block Content Position Y'''
        ...
    
    @classmethod
    @property
    def CAD035(cls) -> CadEntityAttribute:
        '''Block Content Position Z'''
        ...
    
    @classmethod
    @property
    def CAD038(cls) -> CadEntityAttribute:
        '''The Cad 038.'''
        ...
    
    @classmethod
    @property
    def CAD16(cls) -> CadEntityAttribute:
        '''Block Content Scale'''
        ...
    
    @classmethod
    @property
    def CAD046(cls) -> CadEntityAttribute:
        '''Block Content Rotation'''
        ...
    
    @classmethod
    @property
    def CAD047(cls) -> CadEntityAttribute:
        '''Block Transformation Matrix'''
        ...
    
    @classmethod
    @property
    def CAD110(cls) -> CadEntityAttribute:
        '''MLeader Plane Origin Point'''
        ...
    
    @classmethod
    @property
    def CAD111(cls) -> CadEntityAttribute:
        '''MLeader Plane X-Axis Direction'''
        ...
    
    @classmethod
    @property
    def CAD112(cls) -> CadEntityAttribute:
        '''MLeader Plane Y-Axis Direction'''
        ...
    
    @classmethod
    @property
    def CAD297(cls) -> CadEntityAttribute:
        '''MLeader Plane Normal Reversed'''
        ...
    
    @classmethod
    @property
    def CAD300(cls) -> CadEntityAttribute:
        '''Context data'''
        ...
    
    @classmethod
    @property
    def CAD301(cls) -> CadEntityAttribute:
        '''The cad301'''
        ...
    
    @classmethod
    @property
    def CAD309(cls) -> CadEntityAttribute:
        '''End context data'''
        ...
    
    @classmethod
    @property
    def CAD063(cls) -> CadEntityAttribute:
        '''Indicator color'''
        ...
    
    @classmethod
    @property
    def CAD411(cls) -> CadEntityAttribute:
        '''The Cad 411.'''
        ...
    
    @classmethod
    @property
    def CAD017(cls) -> CadEntityAttribute:
        '''The Cad 017.'''
        ...
    
    @classmethod
    @property
    def CAD037(cls) -> CadEntityAttribute:
        '''The Cad 037.'''
        ...
    
    @classmethod
    @property
    def CAD027(cls) -> CadEntityAttribute:
        '''The Cad 027.'''
        ...
    
    @classmethod
    @property
    def CAD120(cls) -> CadEntityAttribute:
        '''The Cad 120.'''
        ...
    
    @classmethod
    @property
    def CAD130(cls) -> CadEntityAttribute:
        '''The Cad 130.'''
        ...
    
    @classmethod
    @property
    def CAD121(cls) -> CadEntityAttribute:
        '''The Cad 121.'''
        ...
    
    @classmethod
    @property
    def CAD131(cls) -> CadEntityAttribute:
        '''The Cad 131.'''
        ...
    
    @classmethod
    @property
    def CAD132(cls) -> CadEntityAttribute:
        '''The Cad 132.'''
        ...
    
    @classmethod
    @property
    def CAD122(cls) -> CadEntityAttribute:
        '''The Cad 122.'''
        ...
    
    @classmethod
    @property
    def CAD346(cls) -> CadEntityAttribute:
        '''The Cad 346.'''
        ...
    
    @classmethod
    @property
    def CAD146(cls) -> CadEntityAttribute:
        '''The Cad 146.'''
        ...
    
    @classmethod
    @property
    def CAD061(cls) -> CadEntityAttribute:
        '''The Cad 061.'''
        ...
    
    @classmethod
    @property
    def CAD311(cls) -> CadEntityAttribute:
        '''The Cad 311.'''
        ...
    
    @classmethod
    @property
    def CAD332(cls) -> CadEntityAttribute:
        '''The Cad 332.'''
        ...
    
    @classmethod
    @property
    def CAD333(cls) -> CadEntityAttribute:
        '''The Cad 333.'''
        ...
    
    @classmethod
    @property
    def CAD334(cls) -> CadEntityAttribute:
        '''The Cad 334'''
        ...
    
    @classmethod
    @property
    def CAD348(cls) -> CadEntityAttribute:
        '''The Cad 348.'''
        ...
    
    @classmethod
    @property
    def CAD361(cls) -> CadEntityAttribute:
        '''The Cad 361.'''
        ...
    
    @classmethod
    @property
    def CAD335(cls) -> CadEntityAttribute:
        '''The Cad 335.'''
        ...
    
    @classmethod
    @property
    def CAD004(cls) -> CadEntityAttribute:
        '''The Cad 004.'''
        ...
    
    @classmethod
    @property
    def CAD052(cls) -> CadEntityAttribute:
        '''The Cad 052.'''
        ...
    
    @classmethod
    @property
    def CAD077(cls) -> CadEntityAttribute:
        '''The Cad 077.'''
        ...
    
    @classmethod
    @property
    def CAD098(cls) -> CadEntityAttribute:
        '''The Cad 098.'''
        ...
    
    @classmethod
    @property
    def CAD099(cls) -> CadEntityAttribute:
        '''The Cad 099.'''
        ...
    
    @classmethod
    @property
    def CAD450(cls) -> CadEntityAttribute:
        '''The Cad 450.'''
        ...
    
    @classmethod
    @property
    def CAD451(cls) -> CadEntityAttribute:
        '''The Cad 450.'''
        ...
    
    @classmethod
    @property
    def CAD452(cls) -> CadEntityAttribute:
        '''The Cad 452.'''
        ...
    
    @classmethod
    @property
    def CAD453(cls) -> CadEntityAttribute:
        '''The Cad 453.'''
        ...
    
    @classmethod
    @property
    def CAD460(cls) -> CadEntityAttribute:
        '''The Cad 460.'''
        ...
    
    @classmethod
    @property
    def CAD461(cls) -> CadEntityAttribute:
        '''The Cad 461.'''
        ...
    
    @classmethod
    @property
    def CAD462(cls) -> CadEntityAttribute:
        '''The Cad 462.'''
        ...
    
    @classmethod
    @property
    def CAD463(cls) -> CadEntityAttribute:
        '''The cad 463.'''
        ...
    
    @classmethod
    @property
    def CAD464(cls) -> CadEntityAttribute:
        '''The cad 464.'''
        ...
    
    @classmethod
    @property
    def CAD465(cls) -> CadEntityAttribute:
        '''The cad 465.'''
        ...
    
    @classmethod
    @property
    def CAD468(cls) -> CadEntityAttribute:
        '''The cad 468.'''
        ...
    
    @classmethod
    @property
    def CAD469(cls) -> CadEntityAttribute:
        '''The cad 469.'''
        ...
    
    @classmethod
    @property
    def CAD470(cls) -> CadEntityAttribute:
        '''The cad 470.'''
        ...
    
    @classmethod
    @property
    def CAD097(cls) -> CadEntityAttribute:
        '''The Cad 097.'''
        ...
    
    @classmethod
    @property
    def CAD147(cls) -> CadEntityAttribute:
        '''The Cad 147.'''
        ...
    
    @classmethod
    @property
    def CAD148(cls) -> CadEntityAttribute:
        '''The Cad 148.'''
        ...
    
    @classmethod
    @property
    def CAD149(cls) -> CadEntityAttribute:
        '''The cad149'''
        ...
    
    @classmethod
    @property
    def CAD270(cls) -> CadEntityAttribute:
        '''The Cad 270.'''
        ...
    
    @classmethod
    @property
    def CAD274(cls) -> CadEntityAttribute:
        '''The Cad 274.'''
        ...
    
    @classmethod
    @property
    def CAD285(cls) -> CadEntityAttribute:
        '''The Cad 285.'''
        ...
    
    @classmethod
    @property
    def CAD286(cls) -> CadEntityAttribute:
        '''The Cad 286.'''
        ...
    
    @classmethod
    @property
    def CAD287(cls) -> CadEntityAttribute:
        '''The Cad 287.'''
        ...
    
    @classmethod
    @property
    def CAD288(cls) -> CadEntityAttribute:
        '''The Cad 288.'''
        ...
    
    @classmethod
    @property
    def CAD371(cls) -> CadEntityAttribute:
        '''The Cad 371.'''
        ...
    
    @classmethod
    @property
    def CAD372(cls) -> CadEntityAttribute:
        '''The Cad 372.'''
        ...
    
    @classmethod
    @property
    def CAD380(cls) -> CadEntityAttribute:
        '''The Cad 380.'''
        ...
    
    @classmethod
    @property
    def CAD1000(cls) -> CadEntityAttribute:
        '''The Cad 1000.'''
        ...
    
    @classmethod
    @property
    def CAD1001(cls) -> CadEntityAttribute:
        '''The Cad 1001.'''
        ...
    
    @classmethod
    @property
    def CAD1002(cls) -> CadEntityAttribute:
        '''The Cad 1002.'''
        ...
    
    @classmethod
    @property
    def CAD1003(cls) -> CadEntityAttribute:
        '''The Cad 1003.'''
        ...
    
    @classmethod
    @property
    def CAD1004(cls) -> CadEntityAttribute:
        '''The Cad 1004.'''
        ...
    
    @classmethod
    @property
    def CAD1005(cls) -> CadEntityAttribute:
        '''The Cad 1005.'''
        ...
    
    @classmethod
    @property
    def CAD1006(cls) -> CadEntityAttribute:
        '''The Cad 1006.'''
        ...
    
    @classmethod
    @property
    def CAD1007(cls) -> CadEntityAttribute:
        '''The Cad 1007.'''
        ...
    
    @classmethod
    @property
    def CAD1008(cls) -> CadEntityAttribute:
        '''The Cad 1008.'''
        ...
    
    @classmethod
    @property
    def CAD1009(cls) -> CadEntityAttribute:
        '''The Cad 1009.'''
        ...
    
    @classmethod
    @property
    def CAD1010(cls) -> CadEntityAttribute:
        '''The Cad 1010.'''
        ...
    
    @classmethod
    @property
    def CAD1011(cls) -> CadEntityAttribute:
        '''The Cad 1011.'''
        ...
    
    @classmethod
    @property
    def CAD1012(cls) -> CadEntityAttribute:
        '''The Cad 1012.'''
        ...
    
    @classmethod
    @property
    def CAD1013(cls) -> CadEntityAttribute:
        '''The Cad 1013.'''
        ...
    
    @classmethod
    @property
    def CAD1014(cls) -> CadEntityAttribute:
        '''The Cad 1014.'''
        ...
    
    @classmethod
    @property
    def CAD1015(cls) -> CadEntityAttribute:
        '''The Cad 1015.'''
        ...
    
    @classmethod
    @property
    def CAD1016(cls) -> CadEntityAttribute:
        '''The Cad 1016.'''
        ...
    
    @classmethod
    @property
    def CAD1017(cls) -> CadEntityAttribute:
        '''The Cad 1017.'''
        ...
    
    @classmethod
    @property
    def CAD1018(cls) -> CadEntityAttribute:
        '''The Cad 1018.'''
        ...
    
    @classmethod
    @property
    def CAD1019(cls) -> CadEntityAttribute:
        '''The Cad 1019.'''
        ...
    
    @classmethod
    @property
    def CAD1020(cls) -> CadEntityAttribute:
        '''The Cad 1020.'''
        ...
    
    @classmethod
    @property
    def CAD1021(cls) -> CadEntityAttribute:
        '''The Cad 1021.'''
        ...
    
    @classmethod
    @property
    def CAD1022(cls) -> CadEntityAttribute:
        '''The Cad 1022.'''
        ...
    
    @classmethod
    @property
    def CAD1023(cls) -> CadEntityAttribute:
        '''The Cad 1023.'''
        ...
    
    @classmethod
    @property
    def CAD1024(cls) -> CadEntityAttribute:
        '''The Cad 1024.'''
        ...
    
    @classmethod
    @property
    def CAD1025(cls) -> CadEntityAttribute:
        '''The Cad 1025.'''
        ...
    
    @classmethod
    @property
    def CAD1026(cls) -> CadEntityAttribute:
        '''The Cad 1026.'''
        ...
    
    @classmethod
    @property
    def CAD1027(cls) -> CadEntityAttribute:
        '''The Cad 1027.'''
        ...
    
    @classmethod
    @property
    def CAD1028(cls) -> CadEntityAttribute:
        '''The Cad 1028.'''
        ...
    
    @classmethod
    @property
    def CAD1029(cls) -> CadEntityAttribute:
        '''The Cad 1029.'''
        ...
    
    @classmethod
    @property
    def CAD1030(cls) -> CadEntityAttribute:
        '''The Cad 1030.'''
        ...
    
    @classmethod
    @property
    def CAD1031(cls) -> CadEntityAttribute:
        '''The Cad 1031.'''
        ...
    
    @classmethod
    @property
    def CAD1032(cls) -> CadEntityAttribute:
        '''The Cad 1032.'''
        ...
    
    @classmethod
    @property
    def CAD1033(cls) -> CadEntityAttribute:
        '''The Cad 1033.'''
        ...
    
    @classmethod
    @property
    def CAD1034(cls) -> CadEntityAttribute:
        '''The Cad 1034.'''
        ...
    
    @classmethod
    @property
    def CAD1035(cls) -> CadEntityAttribute:
        '''The Cad 1035.'''
        ...
    
    @classmethod
    @property
    def CAD1036(cls) -> CadEntityAttribute:
        '''The Cad 1036.'''
        ...
    
    @classmethod
    @property
    def CAD1037(cls) -> CadEntityAttribute:
        '''The Cad 1037.'''
        ...
    
    @classmethod
    @property
    def CAD1038(cls) -> CadEntityAttribute:
        '''The Cad 1038.'''
        ...
    
    @classmethod
    @property
    def CAD1039(cls) -> CadEntityAttribute:
        '''The Cad 1039.'''
        ...
    
    @classmethod
    @property
    def CAD1040(cls) -> CadEntityAttribute:
        '''The Cad 1040.'''
        ...
    
    @classmethod
    @property
    def CAD1041(cls) -> CadEntityAttribute:
        '''The Cad 1041.'''
        ...
    
    @classmethod
    @property
    def CAD1042(cls) -> CadEntityAttribute:
        '''The Cad 1042.'''
        ...
    
    @classmethod
    @property
    def CAD1043(cls) -> CadEntityAttribute:
        '''The Cad 1043.'''
        ...
    
    @classmethod
    @property
    def CAD1044(cls) -> CadEntityAttribute:
        '''The Cad 1044.'''
        ...
    
    @classmethod
    @property
    def CAD1045(cls) -> CadEntityAttribute:
        '''The Cad 1045.'''
        ...
    
    @classmethod
    @property
    def CAD1046(cls) -> CadEntityAttribute:
        '''The Cad 1046.'''
        ...
    
    @classmethod
    @property
    def CAD1047(cls) -> CadEntityAttribute:
        '''The Cad 1047.'''
        ...
    
    @classmethod
    @property
    def CAD1048(cls) -> CadEntityAttribute:
        '''The Cad 1048.'''
        ...
    
    @classmethod
    @property
    def CAD1049(cls) -> CadEntityAttribute:
        '''The Cad 1049.'''
        ...
    
    @classmethod
    @property
    def CAD1050(cls) -> CadEntityAttribute:
        '''The Cad 1050.'''
        ...
    
    @classmethod
    @property
    def CAD1051(cls) -> CadEntityAttribute:
        '''The Cad 1051.'''
        ...
    
    @classmethod
    @property
    def CAD1052(cls) -> CadEntityAttribute:
        '''The Cad 1052.'''
        ...
    
    @classmethod
    @property
    def CAD1053(cls) -> CadEntityAttribute:
        '''The Cad 1053.'''
        ...
    
    @classmethod
    @property
    def CAD1054(cls) -> CadEntityAttribute:
        '''The Cad 1054.'''
        ...
    
    @classmethod
    @property
    def CAD1055(cls) -> CadEntityAttribute:
        '''The Cad 1055.'''
        ...
    
    @classmethod
    @property
    def CAD1056(cls) -> CadEntityAttribute:
        '''The Cad 1056.'''
        ...
    
    @classmethod
    @property
    def CAD1057(cls) -> CadEntityAttribute:
        '''The Cad 1057.'''
        ...
    
    @classmethod
    @property
    def CAD1058(cls) -> CadEntityAttribute:
        '''The Cad 1058.'''
        ...
    
    @classmethod
    @property
    def CAD1059(cls) -> CadEntityAttribute:
        '''The Cad 1059.'''
        ...
    
    @classmethod
    @property
    def CAD1060(cls) -> CadEntityAttribute:
        '''The Cad 1060.'''
        ...
    
    @classmethod
    @property
    def CAD1061(cls) -> CadEntityAttribute:
        '''The Cad 1061.'''
        ...
    
    @classmethod
    @property
    def CAD1062(cls) -> CadEntityAttribute:
        '''The Cad 1062.'''
        ...
    
    @classmethod
    @property
    def CAD1063(cls) -> CadEntityAttribute:
        '''The Cad 1063.'''
        ...
    
    @classmethod
    @property
    def CAD1064(cls) -> CadEntityAttribute:
        '''The Cad 1064.'''
        ...
    
    @classmethod
    @property
    def CAD1065(cls) -> CadEntityAttribute:
        '''The Cad 1065.'''
        ...
    
    @classmethod
    @property
    def CAD1066(cls) -> CadEntityAttribute:
        '''The Cad 1066.'''
        ...
    
    @classmethod
    @property
    def CAD1067(cls) -> CadEntityAttribute:
        '''The Cad 1067.'''
        ...
    
    @classmethod
    @property
    def CAD1068(cls) -> CadEntityAttribute:
        '''The Cad 1068.'''
        ...
    
    @classmethod
    @property
    def CAD1069(cls) -> CadEntityAttribute:
        '''The Cad 1069.'''
        ...
    
    @classmethod
    @property
    def CAD1070(cls) -> CadEntityAttribute:
        '''The Cad 1070.'''
        ...
    
    @classmethod
    @property
    def CAD1071(cls) -> CadEntityAttribute:
        '''The Cad 1071.'''
        ...
    
    @classmethod
    @property
    def CAD009(cls) -> CadEntityAttribute:
        '''The Cad009'''
        ...
    
    @classmethod
    @property
    def CAD349(cls) -> CadEntityAttribute:
        '''Hard-pointer ID to visual style while creating 3D solid primitives. The default value is NULL'''
        ...
    
    @classmethod
    @property
    def CAD466(cls) -> CadEntityAttribute:
        '''The cad466'''
        ...
    
    @classmethod
    @property
    def CAD467(cls) -> CadEntityAttribute:
        '''The cad467'''
        ...
    
    ...

class ScaleType:
    '''Represents possible modes for automatic scale of an image.'''
    
    @classmethod
    @property
    def SHRINK_TO_FIT(cls) -> ScaleType:
        '''Automatically shrink image to fit on canvas.'''
        ...
    
    @classmethod
    @property
    def GROW_TO_FIT(cls) -> ScaleType:
        '''Automatically increase image to fit on canvas.'''
        ...
    
    @classmethod
    @property
    def NONE(cls) -> ScaleType:
        '''Do not use automatic scaling.'''
        ...
    
    ...

