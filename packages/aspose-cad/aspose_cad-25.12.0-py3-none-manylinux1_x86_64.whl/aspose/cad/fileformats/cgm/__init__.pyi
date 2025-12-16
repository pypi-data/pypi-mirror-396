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

class CgmFile:
    '''CGM image class.'''
    
    def reset_meta_definitions(self) -> None:
        '''Resets settings like VDCRealPrecision or ColourModel'''
        ...
    
    def apply_values(self, file : aspose.cad.fileformats.cgm.CgmFile) -> None:
        '''Copies the current meta information
        
        :param file: The cgm file to copy from'''
        ...
    
    def contains_text_element(self, text : str) -> bool:
        '''Determines whether any text element equals the specified text.
        
        :param text: The text.'''
        ...
    
    def get_meta_title(self) -> str:
        '''Gets the title.'''
        ...
    
    def get_graphic_name(self) -> str:
        '''Gets the title of the illustration.'''
        ...
    
    def get_figure_item_texts(self, ignore_color : bool) -> List[str]:
        '''Gets all texts of the figure items.'''
        ...
    
    def contains_figure_item_text(self, text_to_check : str) -> bool:
        '''Determines whether CGM contains a specific figure item text.
        
        :param text_to_check: The text to check.'''
        ...
    
    def contains_consumable_number(self, text_to_check : str) -> bool:
        '''Determines whether CGM contains a specific consumable number text
        
        :param text_to_check: The text to check.'''
        ...
    
    def contains_torque_text_to_fig_item(self, torque_text : str, figure_item_number : str) -> bool:
        '''Determines whether the torque text ("20 Nm (177 lb-in)" exists nearby the figure item)
        
        :param torque_text: The torque text.
        :param figure_item_number: The figure item number.
        :returns: ``true`` if [contains torque text to fig item] [the specified torque text]; otherwise, ``false``.'''
        ...
    
    def get_information(self, command : aspose.cad.fileformats.cgm.commands.TextCommand) -> aspose.cad.fileformats.cgm.classes.TextInformation:
        ...
    
    def is_written_down_to_up(self, command : aspose.cad.fileformats.cgm.commands.TextCommand) -> bool:
        '''Determines whether text is rotated 90 dec counterwise
        
        :param command: The command.'''
        ...
    
    def get_rectangles(self) -> List[aspose.cad.fileformats.cgm.classes.CgmRectangle]:
        '''Gets all found rectangles.'''
        ...
    
    @property
    def name(self) -> str:
        '''Gets the name of the file'''
        ...
    
    @property
    def colour_index_precision(self) -> int:
        ...
    
    @colour_index_precision.setter
    def colour_index_precision(self, value : int):
        ...
    
    @property
    def colour_precision(self) -> int:
        ...
    
    @colour_precision.setter
    def colour_precision(self, value : int):
        ...
    
    @property
    def colour_model(self) -> Aspose.CAD.FileFormats.Cgm.Commands.ColourModel.Model:
        ...
    
    @colour_model.setter
    def colour_model(self, value : Aspose.CAD.FileFormats.Cgm.Commands.ColourModel.Model):
        ...
    
    @property
    def colour_selection_mode(self) -> Aspose.CAD.FileFormats.Cgm.Commands.ColourSelectionMode.Type:
        ...
    
    @colour_selection_mode.setter
    def colour_selection_mode(self, value : Aspose.CAD.FileFormats.Cgm.Commands.ColourSelectionMode.Type):
        ...
    
    @property
    def colour_value_extent_minimum_color_value_rgb(self) -> List[int]:
        ...
    
    @colour_value_extent_minimum_color_value_rgb.setter
    def colour_value_extent_minimum_color_value_rgb(self, value : List[int]):
        ...
    
    @property
    def colour_value_extent_maximum_color_value_rgb(self) -> List[int]:
        ...
    
    @colour_value_extent_maximum_color_value_rgb.setter
    def colour_value_extent_maximum_color_value_rgb(self, value : List[int]):
        ...
    
    @property
    def device_viewport_specification_mode(self) -> Aspose.CAD.FileFormats.Cgm.Commands.DeviceViewportSpecificationMode.Mode:
        ...
    
    @device_viewport_specification_mode.setter
    def device_viewport_specification_mode(self, value : Aspose.CAD.FileFormats.Cgm.Commands.DeviceViewportSpecificationMode.Mode):
        ...
    
    @property
    def edge_width_specification_mode(self) -> aspose.cad.fileformats.cgm.enums.SpecificationMode:
        ...
    
    @edge_width_specification_mode.setter
    def edge_width_specification_mode(self, value : aspose.cad.fileformats.cgm.enums.SpecificationMode):
        ...
    
    @property
    def index_precision(self) -> int:
        ...
    
    @index_precision.setter
    def index_precision(self, value : int):
        ...
    
    @property
    def integer_precision(self) -> int:
        ...
    
    @integer_precision.setter
    def integer_precision(self, value : int):
        ...
    
    @property
    def name_precision(self) -> int:
        ...
    
    @name_precision.setter
    def name_precision(self, value : int):
        ...
    
    @property
    def vdc_integer_precision(self) -> int:
        ...
    
    @vdc_integer_precision.setter
    def vdc_integer_precision(self, value : int):
        ...
    
    @property
    def vdc_real_precision(self) -> aspose.cad.fileformats.cgm.commands.Precision:
        ...
    
    @vdc_real_precision.setter
    def vdc_real_precision(self, value : aspose.cad.fileformats.cgm.commands.Precision):
        ...
    
    @property
    def real_precision(self) -> aspose.cad.fileformats.cgm.commands.Precision:
        ...
    
    @real_precision.setter
    def real_precision(self, value : aspose.cad.fileformats.cgm.commands.Precision):
        ...
    
    @property
    def real_precision_processed(self) -> bool:
        ...
    
    @real_precision_processed.setter
    def real_precision_processed(self, value : bool):
        ...
    
    @property
    def line_width_specification_mode(self) -> aspose.cad.fileformats.cgm.enums.SpecificationMode:
        ...
    
    @line_width_specification_mode.setter
    def line_width_specification_mode(self, value : aspose.cad.fileformats.cgm.enums.SpecificationMode):
        ...
    
    @property
    def marker_size_specification_mode(self) -> aspose.cad.fileformats.cgm.enums.SpecificationMode:
        ...
    
    @marker_size_specification_mode.setter
    def marker_size_specification_mode(self, value : aspose.cad.fileformats.cgm.enums.SpecificationMode):
        ...
    
    @property
    def interior_style_specification_mode(self) -> aspose.cad.fileformats.cgm.enums.SpecificationMode:
        ...
    
    @interior_style_specification_mode.setter
    def interior_style_specification_mode(self, value : aspose.cad.fileformats.cgm.enums.SpecificationMode):
        ...
    
    @property
    def restricted_text_type(self) -> Aspose.CAD.FileFormats.Cgm.Commands.RestrictedTextType.Type:
        ...
    
    @restricted_text_type.setter
    def restricted_text_type(self, value : Aspose.CAD.FileFormats.Cgm.Commands.RestrictedTextType.Type):
        ...
    
    @property
    def vdc_type(self) -> Aspose.CAD.FileFormats.Cgm.Commands.VdcType.Type:
        ...
    
    @vdc_type.setter
    def vdc_type(self, value : Aspose.CAD.FileFormats.Cgm.Commands.VdcType.Type):
        ...
    
    @property
    def commands(self) -> List[aspose.cad.fileformats.cgm.commands.Command]:
        '''The read CGM commands'''
        ...
    
    @property
    def messages(self) -> Iterable[aspose.cad.fileformats.cgm.Message]:
        '''Any messages occured while reading or writing the file'''
        ...
    
    ...

class CgmImage(aspose.cad.Image):
    '''Represents a CGM file in binary mode'''
    
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
    def data(self) -> aspose.cad.fileformats.cgm.CgmFile:
        '''Provides CGM data structure'''
        ...
    
    ...

class IBinaryReader:
    '''Interface to read binary CGM files'''
    
    @overload
    def read_color(self) -> aspose.cad.fileformats.cgm.classes.CgmColor:
        ...
    
    @overload
    def read_color(self, local_color_precision : int) -> aspose.cad.fileformats.cgm.classes.CgmColor:
        ...
    
    @overload
    def read_color_index(self) -> int:
        ...
    
    @overload
    def read_color_index(self, local_color_precision : int) -> int:
        ...
    
    def read_enum(self) -> int:
        ...
    
    def read_string(self) -> str:
        ...
    
    def read_index(self) -> int:
        ...
    
    def read_int(self) -> int:
        ...
    
    def read_argument_end(self) -> int:
        ...
    
    def read_fixed_string(self) -> str:
        ...
    
    def read_sdr(self) -> aspose.cad.fileformats.cgm.classes.StructuredDataRecord:
        ...
    
    def read_vdc(self) -> float:
        ...
    
    def read_name(self) -> int:
        ...
    
    def read_direct_color(self) -> aspose.pydrawing.Color:
        ...
    
    def read_viewport_point(self) -> aspose.cad.fileformats.cgm.classes.ViewportPoint:
        ...
    
    def read_embedded_command(self) -> aspose.cad.fileformats.cgm.commands.Command:
        ...
    
    def read_real(self) -> float:
        ...
    
    def read_fixed_string_with_fallback(self, length : int) -> str:
        ...
    
    def read_point(self) -> aspose.cad.fileformats.cgm.classes.CgmPoint:
        ...
    
    def read_byte(self) -> byte:
        ...
    
    def align_on_word(self) -> None:
        ...
    
    def size_of_enum(self) -> int:
        ...
    
    def size_of_point(self) -> int:
        ...
    
    def read_u_int(self, precision : int) -> int:
        ...
    
    def read_bool(self) -> bool:
        ...
    
    def read_size_specification(self, edge_width_specification_mode : aspose.cad.fileformats.cgm.enums.SpecificationMode) -> float:
        ...
    
    def read_floating_point(self) -> float:
        ...
    
    def read_floating_point32(self) -> float:
        ...
    
    def size_of_int(self) -> int:
        ...
    
    def unsupported(self, message : str) -> None:
        ...
    
    def size_of_direct_color(self) -> int:
        ...
    
    @property
    def current_arg(self) -> int:
        ...
    
    @property
    def arguments_count(self) -> int:
        ...
    
    @property
    def arguments(self) -> bytes:
        ...
    
    ...

class IBinaryWriter:
    '''Writer interface to write binary values'''
    
    @overload
    def write_color_index(self, index : int) -> None:
        ...
    
    @overload
    def write_color_index(self, index : int, local_color_precision : int) -> None:
        ...
    
    def write_string(self, data : str) -> None:
        ...
    
    def write_fixed_string(self, data : str) -> None:
        ...
    
    def write_int(self, data : int) -> None:
        ...
    
    def write_u_int(self, data : int, precision : int) -> None:
        ...
    
    def write_enum(self, data : int) -> None:
        ...
    
    def write_bool(self, data : bool) -> None:
        ...
    
    def write_index(self, data : int) -> None:
        ...
    
    def write_name(self, data : int) -> None:
        ...
    
    def write_color(self, color : aspose.cad.fileformats.cgm.classes.CgmColor, local_color_precision : int) -> None:
        ...
    
    def write_direct_color(self, color : aspose.pydrawing.Color) -> None:
        ...
    
    def write_vdc(self, data : float) -> None:
        ...
    
    def write_point(self, point : aspose.cad.fileformats.cgm.classes.CgmPoint) -> None:
        ...
    
    def write_real(self, data : float) -> None:
        ...
    
    def write_sdr(self, data : aspose.cad.fileformats.cgm.classes.StructuredDataRecord) -> None:
        ...
    
    def write_floating_point32(self, data : float) -> None:
        ...
    
    def write_floating_point(self, data : float) -> None:
        ...
    
    def fill_to_word(self) -> None:
        ...
    
    def write_viewport_point(self, data : aspose.cad.fileformats.cgm.classes.ViewportPoint) -> None:
        ...
    
    def write_size_specification(self, data : float, specification_mode : aspose.cad.fileformats.cgm.enums.SpecificationMode) -> None:
        ...
    
    def write_embedded_command(self, command : aspose.cad.fileformats.cgm.commands.Command) -> None:
        ...
    
    def unsupported(self, message : str) -> None:
        ...
    
    def write_byte(self, data : byte) -> None:
        ...
    
    ...

class IClearTextWriter:
    '''Writer interface to write clear text values'''
    
    def write_line(self, line : str) -> None:
        '''Writes the line to the text file
        
        :param line: The line to write'''
        ...
    
    def write(self, text : str) -> None:
        ...
    
    def info(self, message : str) -> None:
        '''Logs a info message
        
        :param message: The message to log'''
        ...
    
    ...

class Message:
    
    @property
    def text(self) -> str:
        ...
    
    @property
    def command_description(self) -> str:
        ...
    
    @property
    def element_class(self) -> aspose.cad.fileformats.cgm.enums.ClassCode:
        ...
    
    @property
    def element_id(self) -> int:
        ...
    
    @property
    def severity(self) -> aspose.cad.fileformats.cgm.enums.Severity:
        ...
    
    ...

class CgmFileFormat:
    '''Type of the cgm file format'''
    
    @classmethod
    @property
    def BINARY(cls) -> CgmFileFormat:
        ...
    
    @classmethod
    @property
    def CLEAR_TEXT(cls) -> CgmFileFormat:
        ...
    
    ...

