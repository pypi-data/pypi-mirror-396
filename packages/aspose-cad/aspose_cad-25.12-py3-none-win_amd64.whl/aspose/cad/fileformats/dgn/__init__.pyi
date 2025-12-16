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

class DgnCircle(aspose.cad.fileformats.dgn.dgnelements.DgnArcBasedElement):
    '''Represents circle'''
    
    @property
    def id(self) -> str:
        '''Gets the unique identifier of an object inside a drawing.'''
        ...
    
    @property
    def childs(self) -> Iterable[aspose.cad.IDrawingEntity]:
        '''Gets the collection of a nested entities.'''
        ...
    
    @property
    def metadata(self) -> aspose.cad.fileformats.dgn.DgnElementMetadata:
        '''Gets element metadata'''
        ...
    
    @property
    def min_point(self) -> aspose.cad.fileformats.cad.cadobjects.Cad3DPoint:
        ...
    
    @property
    def max_point(self) -> aspose.cad.fileformats.cad.cadobjects.Cad3DPoint:
        ...
    
    @property
    def quaternion_rotations(self) -> aspose.cad.fileformats.dgn.dgntransform.DgnQuaternion:
        ...
    
    @property
    def origin(self) -> aspose.cad.fileformats.dgn.DgnPoint:
        '''Gets Origin of ellipse'''
        ...
    
    @property
    def primary_axis(self) -> float:
        ...
    
    @property
    def secondary_axis(self) -> float:
        ...
    
    @property
    def rotation(self) -> float:
        '''Gets Counterclockwise rotation in degrees'''
        ...
    
    @property
    def start_angle(self) -> float:
        ...
    
    @property
    def sweep_angle(self) -> float:
        ...
    
    @property
    def center(self) -> aspose.cad.fileformats.dgn.DgnPoint:
        '''Gets  center point of circle'''
        ...
    
    @property
    def radius(self) -> float:
        '''Gets radius of circle'''
        ...
    
    ...

class DgnElementDimension:
    '''Element container constraints'''
    
    @property
    def x_low(self) -> int:
        ...
    
    @x_low.setter
    def x_low(self, value : int):
        ...
    
    @property
    def y_low(self) -> int:
        ...
    
    @y_low.setter
    def y_low(self, value : int):
        ...
    
    @property
    def z_low(self) -> int:
        ...
    
    @z_low.setter
    def z_low(self, value : int):
        ...
    
    @property
    def x_high(self) -> int:
        ...
    
    @x_high.setter
    def x_high(self, value : int):
        ...
    
    @property
    def y_high(self) -> int:
        ...
    
    @y_high.setter
    def y_high(self, value : int):
        ...
    
    @property
    def z_high(self) -> int:
        ...
    
    @z_high.setter
    def z_high(self, value : int):
        ...
    
    ...

class DgnElementMetadata:
    '''Represents summary of a file element was read'''
    
    @property
    def type(self) -> aspose.cad.fileformats.dgn.DgnElementType:
        '''Gets the Type of a file element'''
        ...
    
    @type.setter
    def type(self, value : aspose.cad.fileformats.dgn.DgnElementType):
        '''Sets the Type of a file element'''
        ...
    
    @property
    def is_deleted(self) -> bool:
        ...
    
    @is_deleted.setter
    def is_deleted(self, value : bool):
        ...
    
    @property
    def is_part_of_compound(self) -> bool:
        ...
    
    @is_part_of_compound.setter
    def is_part_of_compound(self, value : bool):
        ...
    
    @property
    def color(self) -> aspose.cad.Color:
        '''Gets Color corresponding to Color index'''
        ...
    
    @color.setter
    def color(self, value : aspose.cad.Color):
        '''Sets Color corresponding to Color index'''
        ...
    
    @property
    def line_weight(self) -> byte:
        ...
    
    @line_weight.setter
    def line_weight(self, value : byte):
        ...
    
    @property
    def line_style(self) -> aspose.cad.fileformats.cad.cadconsts.CadLineStyle:
        ...
    
    @line_style.setter
    def line_style(self, value : aspose.cad.fileformats.cad.cadconsts.CadLineStyle):
        ...
    
    @property
    def properties(self) -> aspose.cad.fileformats.dgn.DgnElementProperties:
        '''Gets properties'''
        ...
    
    ...

class DgnElementProperties:
    '''Represents element properties'''
    
    @property
    def class_element(self) -> int:
        ...
    
    @property
    def is_locked(self) -> bool:
        ...
    
    @property
    def is_new(self) -> bool:
        ...
    
    @property
    def is_modified(self) -> bool:
        ...
    
    @property
    def is_attribute_data_present(self) -> bool:
        ...
    
    @property
    def orientation(self) -> aspose.cad.fileformats.dgn.DgnElementOrientation:
        '''Gets element orientation'''
        ...
    
    @property
    def is_planar(self) -> bool:
        ...
    
    @property
    def is_snapable(self) -> bool:
        ...
    
    @property
    def attribute(self) -> bytes:
        '''Gets the Attribute data of a file element'''
        ...
    
    @attribute.setter
    def attribute(self, value : bytes):
        '''Sets the Attribute data of a file element'''
        ...
    
    ...

class DgnExtLocks:
    '''Represents view locks'''
    
    @property
    def locks(self) -> int:
        '''Gets locks'''
        ...
    
    ...

class DgnExtViewFlags:
    '''Represents view flags'''
    
    @property
    def is_filled(self) -> bool:
        ...
    
    ...

class DgnExtendedViewInfo:
    '''Represents view info'''
    
    @property
    def dgn_ext_flags(self) -> aspose.cad.fileformats.dgn.DgnExtViewFlags:
        ...
    
    @property
    def class_mask(self) -> int:
        ...
    
    @property
    def unused(self) -> int:
        '''Gets unused area
        reserved for future use'''
        ...
    
    @property
    def perspective(self) -> float:
        '''Gets perspective disappearing point'''
        ...
    
    ...

class DgnImage(aspose.cad.Image):
    '''Dgn image class'''
    
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
    
    def try_remove_entity(self, entity_to_remove : aspose.cad.fileformats.dgn.dgnelements.DgnDrawableEntityBase) -> None:
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
        '''Gets the image height.
        Defines the Y-axis distance between the bottommost point of all graphical objects in the image and their topmost point.
        The distance is measured in units corresponding to the value of the property :py:attr:`aspose.cad.Image.unit_type`'''
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
        '''Gets the image width.
        Defines the X-axis distance between the leftmost point of all graphic objects in the image and their rightmost point.
        The distance is measured in units corresponding to the value of the property :py:attr:`aspose.cad.Image.unit_type`'''
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
    def entities(self) -> Iterable[aspose.cad.fileformats.dgn.dgnelements.DgnDrawableEntityBase]:
        ...
    
    @property
    def sub_unit_type(self) -> aspose.cad.imageoptions.UnitType:
        ...
    
    @property
    def version(self) -> aspose.cad.fileformats.dgn.DgnFileVersion:
        '''Gets DGN version of loaded image'''
        ...
    
    @property
    def is_3d_image(self) -> bool:
        ...
    
    @property
    def tags(self) -> List[aspose.cad.fileformats.dgn.dgnelements.DgnElementBase]:
        '''Gets the tags.'''
        ...
    
    @property
    def max_point(self) -> aspose.cad.fileformats.cad.cadobjects.Cad3DPoint:
        ...
    
    @property
    def min_point(self) -> aspose.cad.fileformats.cad.cadobjects.Cad3DPoint:
        ...
    
    @property
    def views(self) -> List[aspose.cad.fileformats.dgn.DgnViewInfo]:
        '''Gets the views.'''
        ...
    
    ...

class DgnPoint:
    '''Represents point for DGN format'''
    
    @property
    def x(self) -> float:
        '''Gets X coordinate'''
        ...
    
    @x.setter
    def x(self, value : float):
        '''Sets X coordinate'''
        ...
    
    @property
    def y(self) -> float:
        '''Gets Y coordinate'''
        ...
    
    @y.setter
    def y(self, value : float):
        '''Sets Y coordinate'''
        ...
    
    @property
    def z(self) -> float:
        '''Gets Z coordinate'''
        ...
    
    @z.setter
    def z(self, value : float):
        '''Sets Z coordinate'''
        ...
    
    ...

class DgnTag:
    '''Represents dgn tag'''
    
    @property
    def name(self) -> str:
        '''Gets tag name'''
        ...
    
    @name.setter
    def name(self, value : str):
        '''Sets tag name'''
        ...
    
    @property
    def id(self) -> int:
        '''Gets tag id'''
        ...
    
    @id.setter
    def id(self, value : int):
        '''Sets tag id'''
        ...
    
    @property
    def user_prompt(self) -> str:
        ...
    
    @user_prompt.setter
    def user_prompt(self, value : str):
        ...
    
    @property
    def default_tag_value(self) -> aspose.cad.fileformats.dgn.DgnTagValue:
        ...
    
    @default_tag_value.setter
    def default_tag_value(self, value : aspose.cad.fileformats.dgn.DgnTagValue):
        ...
    
    ...

class DgnTagValue:
    '''DgnTagValue class'''
    
    @property
    def type(self) -> aspose.cad.fileformats.dgn.DgnTagType:
        '''Gets tag type'''
        ...
    
    @type.setter
    def type(self, value : aspose.cad.fileformats.dgn.DgnTagType):
        '''Sets tag type'''
        ...
    
    @property
    def string_value(self) -> str:
        ...
    
    @string_value.setter
    def string_value(self, value : str):
        ...
    
    @property
    def integer_value(self) -> int:
        ...
    
    @integer_value.setter
    def integer_value(self, value : int):
        ...
    
    @property
    def float_value(self) -> float:
        ...
    
    @float_value.setter
    def float_value(self, value : float):
        ...
    
    ...

class DgnViewInfo:
    '''DgnViewInfo class'''
    
    @property
    def flags(self) -> int:
        '''Gets the flags.'''
        ...
    
    @flags.setter
    def flags(self, value : int):
        '''Sets the flags.'''
        ...
    
    @property
    def origin(self) -> aspose.cad.fileformats.dgn.DgnPoint:
        '''Gets the origin.'''
        ...
    
    @origin.setter
    def origin(self, value : aspose.cad.fileformats.dgn.DgnPoint):
        '''Sets the origin.'''
        ...
    
    @property
    def delta(self) -> aspose.cad.fileformats.dgn.DgnPoint:
        '''Gets the delta.'''
        ...
    
    @delta.setter
    def delta(self, value : aspose.cad.fileformats.dgn.DgnPoint):
        '''Sets the delta.'''
        ...
    
    @property
    def conversion(self) -> float:
        '''Gets the conversion.'''
        ...
    
    @conversion.setter
    def conversion(self, value : float):
        '''Sets the conversion.'''
        ...
    
    @property
    def active_z(self) -> int:
        ...
    
    @active_z.setter
    def active_z(self, value : int):
        ...
    
    @property
    def levels(self) -> bytes:
        '''The levels'''
        ...
    
    @levels.setter
    def levels(self, value : bytes):
        '''The levels'''
        ...
    
    ...

class DgnElementOrientation:
    '''Represents element orientation'''
    
    @classmethod
    @property
    def ON_DESIGN(cls) -> DgnElementOrientation:
        '''design related'''
        ...
    
    @classmethod
    @property
    def ON_SCREEN(cls) -> DgnElementOrientation:
        '''screen related'''
        ...
    
    ...

class DgnElementType:
    '''Element type'''
    
    @classmethod
    @property
    def CELL_LIBRARY(cls) -> DgnElementType:
        '''Cell library'''
        ...
    
    @classmethod
    @property
    def CELL_HEADER(cls) -> DgnElementType:
        '''Cell header'''
        ...
    
    @classmethod
    @property
    def LINE(cls) -> DgnElementType:
        '''Line element'''
        ...
    
    @classmethod
    @property
    def POLY_LINE(cls) -> DgnElementType:
        '''Poly-line element'''
        ...
    
    @classmethod
    @property
    def GROUP_DATA(cls) -> DgnElementType:
        '''Group data'''
        ...
    
    @classmethod
    @property
    def SHAPE(cls) -> DgnElementType:
        '''Shape element'''
        ...
    
    @classmethod
    @property
    def TEXT_NODE(cls) -> DgnElementType:
        '''Text element node'''
        ...
    
    @classmethod
    @property
    def DIGITIZER_SETUP(cls) -> DgnElementType:
        '''Digitizer setup'''
        ...
    
    @classmethod
    @property
    def TCB(cls) -> DgnElementType:
        '''Root element'''
        ...
    
    @classmethod
    @property
    def SYMBOLOGY(cls) -> DgnElementType:
        '''Symbology element'''
        ...
    
    @classmethod
    @property
    def CURVE(cls) -> DgnElementType:
        '''Curve element'''
        ...
    
    @classmethod
    @property
    def COMPLEX_CHAIN_HEADER(cls) -> DgnElementType:
        '''Complex chain header'''
        ...
    
    @classmethod
    @property
    def COMPLEX_SHAPE_HEADER(cls) -> DgnElementType:
        '''Complex shape header'''
        ...
    
    @classmethod
    @property
    def ELLIPSE(cls) -> DgnElementType:
        '''Ellipse element'''
        ...
    
    @classmethod
    @property
    def ARC(cls) -> DgnElementType:
        '''Arc element'''
        ...
    
    @classmethod
    @property
    def TEXT(cls) -> DgnElementType:
        '''Text element'''
        ...
    
    @classmethod
    @property
    def SURFACE_HEADER_3D(cls) -> DgnElementType:
        '''Surface Header'''
        ...
    
    @classmethod
    @property
    def SOLID_HEADER_3D(cls) -> DgnElementType:
        '''3D solid header'''
        ...
    
    @classmethod
    @property
    def B_SPLINE_POLE(cls) -> DgnElementType:
        '''B-spline element'''
        ...
    
    @classmethod
    @property
    def POINT_STRING(cls) -> DgnElementType:
        '''Point string'''
        ...
    
    @classmethod
    @property
    def B_SPLINE_SURFACE_HEADER(cls) -> DgnElementType:
        '''B-spline surface header'''
        ...
    
    @classmethod
    @property
    def B_SPLINE_SURFACE_BOUNDARY(cls) -> DgnElementType:
        '''B-spline surface boundary'''
        ...
    
    @classmethod
    @property
    def B_SPLINE_KNOT(cls) -> DgnElementType:
        '''B-spline KNOT'''
        ...
    
    @classmethod
    @property
    def B_SPLINE_CURVE_HEADER(cls) -> DgnElementType:
        '''B-spline curve'''
        ...
    
    @classmethod
    @property
    def B_SPLINE_WEIGTH_FACTOR(cls) -> DgnElementType:
        '''B-spline weight'''
        ...
    
    @classmethod
    @property
    def CONE(cls) -> DgnElementType:
        '''Cone element'''
        ...
    
    @classmethod
    @property
    def DIMENSION_ELEMENT(cls) -> DgnElementType:
        '''Dimension element'''
        ...
    
    @classmethod
    @property
    def SHARED_CELL_DEFINITION(cls) -> DgnElementType:
        '''Shared cell'''
        ...
    
    @classmethod
    @property
    def SHARED_CELL_ELEMENT(cls) -> DgnElementType:
        '''Shared cell'''
        ...
    
    @classmethod
    @property
    def TAG_VALUE(cls) -> DgnElementType:
        '''Tag element value'''
        ...
    
    @classmethod
    @property
    def UNKNOWN(cls) -> DgnElementType:
        '''Unknown for now'''
        ...
    
    @classmethod
    @property
    def APPLICATION_ELEMENT(cls) -> DgnElementType:
        '''Application Element'''
        ...
    
    @classmethod
    @property
    def NON_GRAPHICAL_EXTENDED_ELEMENT(cls) -> DgnElementType:
        '''NonGraphical extended element (complex)'''
        ...
    
    @classmethod
    @property
    def END_OF_DESIGN_MARKER(cls) -> DgnElementType:
        '''End of design marker'''
        ...
    
    ...

class DgnFileVersion:
    '''File format version'''
    
    @classmethod
    @property
    def V7(cls) -> DgnFileVersion:
        '''Version 7 (documented)'''
        ...
    
    @classmethod
    @property
    def V8(cls) -> DgnFileVersion:
        '''Version 8 (non-documented)'''
        ...
    
    ...

class DgnJustificationType:
    '''Justification type'''
    
    @classmethod
    @property
    def LEFT_TOP(cls) -> DgnJustificationType:
        '''Left Top justification'''
        ...
    
    @classmethod
    @property
    def LEFT_CENTER(cls) -> DgnJustificationType:
        '''Left Center justification'''
        ...
    
    @classmethod
    @property
    def LEFT_BOTTOM(cls) -> DgnJustificationType:
        '''Left Bottom justification'''
        ...
    
    @classmethod
    @property
    def LEFT_MARGIN_TOP(cls) -> DgnJustificationType:
        '''Left Margin Top justification'''
        ...
    
    @classmethod
    @property
    def LEFT_MARGIN_CENTER(cls) -> DgnJustificationType:
        '''Left Margin Center justification'''
        ...
    
    @classmethod
    @property
    def LEFT_MARGIN_BOTTOM(cls) -> DgnJustificationType:
        '''Left Margin Bottom justification'''
        ...
    
    @classmethod
    @property
    def CENTER_TOP(cls) -> DgnJustificationType:
        '''Center Top justification'''
        ...
    
    @classmethod
    @property
    def CENTER_CENTER(cls) -> DgnJustificationType:
        '''Center Center justification'''
        ...
    
    @classmethod
    @property
    def CENTER_BOTTOM(cls) -> DgnJustificationType:
        '''Center Bottom justification'''
        ...
    
    @classmethod
    @property
    def RIGHT_MARGIN_TOP(cls) -> DgnJustificationType:
        '''Right Margin Top justification'''
        ...
    
    @classmethod
    @property
    def RIGHT_MARGIN_CENTER(cls) -> DgnJustificationType:
        '''Curve element justification'''
        ...
    
    @classmethod
    @property
    def RIGHT_MARGIN_BOTTOM(cls) -> DgnJustificationType:
        '''Right Margin Bottom justification'''
        ...
    
    @classmethod
    @property
    def RIGHT_TOP(cls) -> DgnJustificationType:
        '''Right Top justification'''
        ...
    
    @classmethod
    @property
    def RIGHT_CENTER(cls) -> DgnJustificationType:
        '''Right Center justification'''
        ...
    
    @classmethod
    @property
    def RIGHT_BOTTOM(cls) -> DgnJustificationType:
        '''Right Bottom justification'''
        ...
    
    ...

class DgnSurface3DType:
    '''Represents 3d surface type'''
    
    @classmethod
    @property
    def SURFACE(cls) -> DgnSurface3DType:
        '''3d surface'''
        ...
    
    @classmethod
    @property
    def SOLID(cls) -> DgnSurface3DType:
        '''Solid 3d element'''
        ...
    
    ...

class DgnSurfaceCreationMethod:
    '''Represents creation method of 3d surface and 3d solid'''
    
    @classmethod
    @property
    def SURFACE_OF_PROJECTION(cls) -> DgnSurfaceCreationMethod:
        '''Surface of projection'''
        ...
    
    @classmethod
    @property
    def BOUNDED_PLANE(cls) -> DgnSurfaceCreationMethod:
        '''Bounded Plane'''
        ...
    
    @classmethod
    @property
    def BOUNDED_PLANE2(cls) -> DgnSurfaceCreationMethod:
        '''Bounded Plane'''
        ...
    
    @classmethod
    @property
    def RIGHT_CIRCULAR_CYLINDER(cls) -> DgnSurfaceCreationMethod:
        '''Right circular cylinder'''
        ...
    
    @classmethod
    @property
    def RIGHT_CIRCULAR_CONE(cls) -> DgnSurfaceCreationMethod:
        '''Right circular cone'''
        ...
    
    @classmethod
    @property
    def TABULATED_CYLINDER(cls) -> DgnSurfaceCreationMethod:
        '''Tabulated cylinder'''
        ...
    
    @classmethod
    @property
    def TABULATED_CONE(cls) -> DgnSurfaceCreationMethod:
        '''Tabulated cone'''
        ...
    
    @classmethod
    @property
    def CONVOLUTE(cls) -> DgnSurfaceCreationMethod:
        '''Convolute object'''
        ...
    
    @classmethod
    @property
    def SURFACE_OF_REVOLUTION(cls) -> DgnSurfaceCreationMethod:
        '''Surface of revolution'''
        ...
    
    @classmethod
    @property
    def WARPED_SURFACE(cls) -> DgnSurfaceCreationMethod:
        '''Warped surface'''
        ...
    
    @classmethod
    @property
    def VOLUME_OF_PROJECTION(cls) -> DgnSurfaceCreationMethod:
        '''Volume of projection'''
        ...
    
    @classmethod
    @property
    def VOLUME_OF_REVOLUTION(cls) -> DgnSurfaceCreationMethod:
        '''Volume of revolution'''
        ...
    
    @classmethod
    @property
    def VOLUME_DEFINED_BY_BOUNDARY_ELEMENT(cls) -> DgnSurfaceCreationMethod:
        '''Volume defined by boundary element'''
        ...
    
    ...

class DgnTagType:
    '''Represents dgn tag type'''
    
    @classmethod
    @property
    def TAG_STRING(cls) -> DgnTagType:
        '''String tag style'''
        ...
    
    @classmethod
    @property
    def TAG_INTEGER(cls) -> DgnTagType:
        '''Integer tag style'''
        ...
    
    @classmethod
    @property
    def TAG_FLOAT(cls) -> DgnTagType:
        '''Float tag style'''
        ...
    
    ...

