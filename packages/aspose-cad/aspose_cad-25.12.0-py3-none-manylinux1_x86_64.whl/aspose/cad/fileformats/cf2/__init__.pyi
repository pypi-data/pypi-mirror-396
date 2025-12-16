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

class CF2Aux:
    '''The Aux section of the CF2 format'''
    
    @property
    def line_type_definitions(self) -> List[aspose.cad.fileformats.cf2.CF2LineTypeDefinition]:
        ...
    
    ...

class CF2DrawnElement:
    '''The Basic of the drawn elements'''
    
    @property
    def start_point(self) -> aspose.cad.PointF:
        ...
    
    @start_point.setter
    def start_point(self, value : aspose.cad.PointF):
        ...
    
    @property
    def type_d_element(self) -> aspose.cad.fileformats.cf2.CF2TypeDElement:
        ...
    
    ...

class CF2GeometryElement(CF2DrawnElement):
    '''The basic of the geometry elements'''
    
    @property
    def start_point(self) -> aspose.cad.PointF:
        ...
    
    @start_point.setter
    def start_point(self, value : aspose.cad.PointF):
        ...
    
    @property
    def type_d_element(self) -> aspose.cad.fileformats.cf2.CF2TypeDElement:
        ...
    
    @property
    def line_thickness(self) -> int:
        ...
    
    @line_thickness.setter
    def line_thickness(self, value : int):
        ...
    
    @property
    def line_type(self) -> aspose.cad.fileformats.cf2.CF2LineTypes:
        ...
    
    @line_type.setter
    def line_type(self, value : aspose.cad.fileformats.cf2.CF2LineTypes):
        ...
    
    @property
    def addition_line_type(self) -> int:
        ...
    
    @addition_line_type.setter
    def addition_line_type(self, value : int):
        ...
    
    ...

class CF2Image(aspose.cad.Image):
    '''CF2 image class'''
    
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
    def load_message_file(self, file_path : str) -> None:
        '''Loads a message file from the specified path.
        
        :param file_path: The file path of the message file.'''
        ...
    
    @overload
    def load_message_file(self, stream : io.RawIOBase) -> None:
        '''Loads a message file from the specified stream.
        
        :param stream: The stream of the message file.'''
        ...
    
    def cache_data(self) -> None:
        '''Caches data'''
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
    
    def update_size(self) -> None:
        '''Update size'''
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
    def max_point(self) -> aspose.cad.fileformats.cad.cadobjects.Cad3DPoint:
        ...
    
    @property
    def min_point(self) -> aspose.cad.fileformats.cad.cadobjects.Cad3DPoint:
        ...
    
    @property
    def order_secton(self) -> aspose.cad.fileformats.cf2.CF2Order:
        ...
    
    @property
    def aux_secton(self) -> aspose.cad.fileformats.cf2.CF2Aux:
        ...
    
    @property
    def main_secton(self) -> aspose.cad.fileformats.cf2.CF2Main:
        ...
    
    @property
    def sub_sectons(self) -> List[aspose.cad.fileformats.cf2.CF2Sub]:
        ...
    
    @property
    def order_output_describing(self) -> aspose.cad.fileformats.cf2.CF2OrderOutputDescribing:
        ...
    
    @order_output_describing.setter
    def order_output_describing(self, value : aspose.cad.fileformats.cf2.CF2OrderOutputDescribing):
        ...
    
    @property
    def lines_output_describing(self) -> aspose.cad.fileformats.cf2.CF2LinesOutputDescribing:
        ...
    
    @lines_output_describing.setter
    def lines_output_describing(self, value : aspose.cad.fileformats.cf2.CF2LinesOutputDescribing):
        ...
    
    ...

class CF2Line(CF2LinearElement):
    '''The line'''
    
    @property
    def start_point(self) -> aspose.cad.PointF:
        ...
    
    @start_point.setter
    def start_point(self, value : aspose.cad.PointF):
        ...
    
    @property
    def type_d_element(self) -> aspose.cad.fileformats.cf2.CF2TypeDElement:
        ...
    
    @property
    def line_thickness(self) -> int:
        ...
    
    @line_thickness.setter
    def line_thickness(self, value : int):
        ...
    
    @property
    def line_type(self) -> aspose.cad.fileformats.cf2.CF2LineTypes:
        ...
    
    @line_type.setter
    def line_type(self, value : aspose.cad.fileformats.cf2.CF2LineTypes):
        ...
    
    @property
    def addition_line_type(self) -> int:
        ...
    
    @addition_line_type.setter
    def addition_line_type(self, value : int):
        ...
    
    @property
    def n_bridges(self) -> int:
        ...
    
    @n_bridges.setter
    def n_bridges(self, value : int):
        ...
    
    @property
    def w_bridges(self) -> float:
        ...
    
    @w_bridges.setter
    def w_bridges(self, value : float):
        ...
    
    @property
    def end_point(self) -> aspose.cad.PointF:
        ...
    
    @end_point.setter
    def end_point(self, value : aspose.cad.PointF):
        ...
    
    ...

class CF2LineTypeDefinition:
    '''The line type definition'''
    
    @property
    def index(self) -> int:
        '''The index'''
        ...
    
    @index.setter
    def index(self, value : int):
        '''The index'''
        ...
    
    @property
    def line_type(self) -> aspose.cad.fileformats.cf2.CF2LineTypes:
        ...
    
    @line_type.setter
    def line_type(self, value : aspose.cad.fileformats.cf2.CF2LineTypes):
        ...
    
    @property
    def parameters(self) -> List[any]:
        '''The parameters'''
        ...
    
    ...

class CF2LinearElement(CF2GeometryElement):
    '''The basic of the linear elements'''
    
    @property
    def start_point(self) -> aspose.cad.PointF:
        ...
    
    @start_point.setter
    def start_point(self, value : aspose.cad.PointF):
        ...
    
    @property
    def type_d_element(self) -> aspose.cad.fileformats.cf2.CF2TypeDElement:
        ...
    
    @property
    def line_thickness(self) -> int:
        ...
    
    @line_thickness.setter
    def line_thickness(self, value : int):
        ...
    
    @property
    def line_type(self) -> aspose.cad.fileformats.cf2.CF2LineTypes:
        ...
    
    @line_type.setter
    def line_type(self, value : aspose.cad.fileformats.cf2.CF2LineTypes):
        ...
    
    @property
    def addition_line_type(self) -> int:
        ...
    
    @addition_line_type.setter
    def addition_line_type(self, value : int):
        ...
    
    @property
    def n_bridges(self) -> int:
        ...
    
    @n_bridges.setter
    def n_bridges(self, value : int):
        ...
    
    @property
    def w_bridges(self) -> float:
        ...
    
    @w_bridges.setter
    def w_bridges(self, value : float):
        ...
    
    ...

class CF2LinesOutputDescribing(CF2OutputDescribing):
    '''Description of the line types output'''
    
    @property
    def start_point(self) -> aspose.cad.PointF:
        ...
    
    @start_point.setter
    def start_point(self, value : aspose.cad.PointF):
        ...
    
    @property
    def type_d_element(self) -> aspose.cad.fileformats.cf2.CF2TypeDElement:
        ...
    
    @property
    def font_size(self) -> float:
        ...
    
    @font_size.setter
    def font_size(self, value : float):
        ...
    
    @property
    def font_name(self) -> str:
        ...
    
    @font_name.setter
    def font_name(self, value : str):
        ...
    
    @property
    def angle(self) -> float:
        '''The angle'''
        ...
    
    @angle.setter
    def angle(self, value : float):
        '''The angle'''
        ...
    
    ...

class CF2Main:
    '''The Main section of the CF2 format'''
    
    @property
    def name(self) -> str:
        '''The name of section.'''
        ...
    
    @name.setter
    def name(self, value : str):
        '''The name of section.'''
        ...
    
    @property
    def system_coordinate(self) -> aspose.cad.fileformats.cf2.CF2SystemCoordinate:
        ...
    
    @system_coordinate.setter
    def system_coordinate(self, value : aspose.cad.fileformats.cf2.CF2SystemCoordinate):
        ...
    
    @property
    def left_lower_corner(self) -> aspose.cad.PointF:
        ...
    
    @left_lower_corner.setter
    def left_lower_corner(self, value : aspose.cad.PointF):
        ...
    
    @property
    def upper_right_corner(self) -> aspose.cad.PointF:
        ...
    
    @upper_right_corner.setter
    def upper_right_corner(self, value : aspose.cad.PointF):
        ...
    
    @property
    def scale(self) -> aspose.cad.PointF:
        '''The scale'''
        ...
    
    @scale.setter
    def scale(self, value : aspose.cad.PointF):
        '''The scale'''
        ...
    
    @property
    def drawn_elements(self) -> List[aspose.cad.fileformats.cf2.CF2DrawnElement]:
        ...
    
    ...

class CF2Order:
    '''The Order section of the CF2 format'''
    
    @property
    def properties(self) -> List[aspose.cad.fileformats.cf2.CF2Property]:
        '''The properties of the CF2 format'''
        ...
    
    ...

class CF2OrderOutputDescribing(CF2OutputDescribing):
    '''Description of the order section output'''
    
    @property
    def start_point(self) -> aspose.cad.PointF:
        ...
    
    @start_point.setter
    def start_point(self, value : aspose.cad.PointF):
        ...
    
    @property
    def type_d_element(self) -> aspose.cad.fileformats.cf2.CF2TypeDElement:
        ...
    
    @property
    def font_size(self) -> float:
        ...
    
    @font_size.setter
    def font_size(self, value : float):
        ...
    
    @property
    def font_name(self) -> str:
        ...
    
    @font_name.setter
    def font_name(self, value : str):
        ...
    
    @property
    def angle(self) -> float:
        '''The angle'''
        ...
    
    @angle.setter
    def angle(self, value : float):
        '''The angle'''
        ...
    
    @property
    def language(self) -> str:
        '''The language'''
        ...
    
    @language.setter
    def language(self, value : str):
        '''The language'''
        ...
    
    ...

class CF2OutputDescribing(CF2DrawnElement):
    '''Description of the output'''
    
    @property
    def start_point(self) -> aspose.cad.PointF:
        ...
    
    @start_point.setter
    def start_point(self, value : aspose.cad.PointF):
        ...
    
    @property
    def type_d_element(self) -> aspose.cad.fileformats.cf2.CF2TypeDElement:
        ...
    
    @property
    def font_size(self) -> float:
        ...
    
    @font_size.setter
    def font_size(self, value : float):
        ...
    
    @property
    def font_name(self) -> str:
        ...
    
    @font_name.setter
    def font_name(self, value : str):
        ...
    
    @property
    def angle(self) -> float:
        '''The angle'''
        ...
    
    @angle.setter
    def angle(self, value : float):
        '''The angle'''
        ...
    
    ...

class CF2Property:
    '''The property'''
    
    @property
    def containt(self) -> str:
        '''The containt'''
        ...
    
    @containt.setter
    def containt(self, value : str):
        '''The containt'''
        ...
    
    ...

class CF2PropertyCustom(CF2Property):
    '''The custom property'''
    
    @property
    def containt(self) -> str:
        '''The containt'''
        ...
    
    @containt.setter
    def containt(self, value : str):
        '''The containt'''
        ...
    
    @property
    def name(self) -> str:
        '''The property name'''
        ...
    
    @name.setter
    def name(self, value : str):
        '''The property name'''
        ...
    
    ...

class CF2PropertyStandard(CF2Property):
    '''The standart property'''
    
    @property
    def containt(self) -> str:
        '''The containt'''
        ...
    
    @containt.setter
    def containt(self, value : str):
        '''The containt'''
        ...
    
    @property
    def index_name(self) -> int:
        ...
    
    @index_name.setter
    def index_name(self, value : int):
        ...
    
    ...

class CF2StandardMessage:
    '''The standart message'''
    
    @property
    def group_index(self) -> int:
        ...
    
    @group_index.setter
    def group_index(self, value : int):
        ...
    
    @property
    def language(self) -> str:
        '''The language'''
        ...
    
    @language.setter
    def language(self, value : str):
        '''The language'''
        ...
    
    @property
    def containt(self) -> str:
        '''The containt'''
        ...
    
    @containt.setter
    def containt(self, value : str):
        '''The containt'''
        ...
    
    ...

class CF2Sub:
    '''The Sub section of the CF2 format'''
    
    @property
    def name(self) -> str:
        '''The name of section.'''
        ...
    
    @name.setter
    def name(self, value : str):
        '''The name of section.'''
        ...
    
    @property
    def drawn_elements(self) -> List[aspose.cad.fileformats.cf2.CF2DrawnElement]:
        ...
    
    ...

class CF2SubInsert(CF2DrawnElement):
    '''The insert of the Sub element'''
    
    @property
    def start_point(self) -> aspose.cad.PointF:
        ...
    
    @start_point.setter
    def start_point(self, value : aspose.cad.PointF):
        ...
    
    @property
    def type_d_element(self) -> aspose.cad.fileformats.cf2.CF2TypeDElement:
        ...
    
    @property
    def name(self) -> str:
        '''The name'''
        ...
    
    @name.setter
    def name(self, value : str):
        '''The name'''
        ...
    
    @property
    def angle(self) -> float:
        '''The angle'''
        ...
    
    @angle.setter
    def angle(self, value : float):
        '''The angle'''
        ...
    
    @property
    def scale(self) -> aspose.cad.PointF:
        '''The scale'''
        ...
    
    @scale.setter
    def scale(self, value : aspose.cad.PointF):
        '''The scale'''
        ...
    
    ...

class CF2Text(CF2GeometryElement):
    '''The Text'''
    
    @property
    def start_point(self) -> aspose.cad.PointF:
        ...
    
    @start_point.setter
    def start_point(self, value : aspose.cad.PointF):
        ...
    
    @property
    def type_d_element(self) -> aspose.cad.fileformats.cf2.CF2TypeDElement:
        ...
    
    @property
    def line_thickness(self) -> int:
        ...
    
    @line_thickness.setter
    def line_thickness(self, value : int):
        ...
    
    @property
    def line_type(self) -> aspose.cad.fileformats.cf2.CF2LineTypes:
        ...
    
    @line_type.setter
    def line_type(self, value : aspose.cad.fileformats.cf2.CF2LineTypes):
        ...
    
    @property
    def addition_line_type(self) -> int:
        ...
    
    @addition_line_type.setter
    def addition_line_type(self, value : int):
        ...
    
    @property
    def containt(self) -> str:
        '''The containt'''
        ...
    
    @containt.setter
    def containt(self, value : str):
        '''The containt'''
        ...
    
    @property
    def angle(self) -> float:
        '''The angle'''
        ...
    
    @angle.setter
    def angle(self, value : float):
        '''The angle'''
        ...
    
    @property
    def size(self) -> aspose.cad.SizeF:
        '''The size'''
        ...
    
    @size.setter
    def size(self, value : aspose.cad.SizeF):
        '''The size'''
        ...
    
    ...

class CF2DimensionLineTypes:
    '''CF2 dimension line types'''
    
    @classmethod
    @property
    def WITHOUT_ARROWS_AT_ENDS(cls) -> CF2DimensionLineTypes:
        '''Line without arrows at the ends'''
        ...
    
    @classmethod
    @property
    def WITH_AN_ARROW_AT_BEGINNING(cls) -> CF2DimensionLineTypes:
        '''Line with an arrow at the beginning'''
        ...
    
    @classmethod
    @property
    def WITH_AN_ARROW_AT_END(cls) -> CF2DimensionLineTypes:
        '''Line with an arrow at the end'''
        ...
    
    @classmethod
    @property
    def ARROWS_AT_BOTH_ENDS(cls) -> CF2DimensionLineTypes:
        '''Arrows at both ends of the line'''
        ...
    
    ...

class CF2InstructionCodes:
    '''CF2 instruction codes'''
    
    @classmethod
    @property
    def ALONG_DIR_PAPER_FIBERS(cls) -> CF2InstructionCodes:
        '''Along direction of the paper fibers'''
        ...
    
    @classmethod
    @property
    def CROSS_DIRECTION_OF_PAPER_FIBERS(cls) -> CF2InstructionCodes:
        '''Cross the direction of paper fibers'''
        ...
    
    @classmethod
    @property
    def HOLE(cls) -> CF2InstructionCodes:
        '''Place for a hole'''
        ...
    
    @classmethod
    @property
    def PERIPHERAL_CUTTING(cls) -> CF2InstructionCodes:
        '''Peripheral cutting'''
        ...
    
    @classmethod
    @property
    def EXPANDING_CHAMFER(cls) -> CF2InstructionCodes:
        '''Expanding chamfer'''
        ...
    
    ...

class CF2LineTypes:
    '''CF2 line types'''
    
    @classmethod
    @property
    def ALIGNMENT_MARK(cls) -> CF2LineTypes:
        '''Line alignment marks'''
        ...
    
    @classmethod
    @property
    def CUTTING(cls) -> CF2LineTypes:
        '''Cutting line'''
        ...
    
    @classmethod
    @property
    def SCORING(cls) -> CF2LineTypes:
        '''Scoring line'''
        ...
    
    @classmethod
    @property
    def PUNCHING_RULER(cls) -> CF2LineTypes:
        '''Punching ruler'''
        ...
    
    @classmethod
    @property
    def COMBINED_CUTTING_STRIP(cls) -> CF2LineTypes:
        '''Combined cutting strip'''
        ...
    
    @classmethod
    @property
    def INSTRUCTIONS_USE_CS_ELEMENTS(cls) -> CF2LineTypes:
        '''Instructions on the use of counter-stamp elements'''
        ...
    
    @classmethod
    @property
    def CORNER_PUNCHING_KNIFE(cls) -> CF2LineTypes:
        '''Corner punching knife'''
        ...
    
    @classmethod
    @property
    def PUNCHING_KNIFE(cls) -> CF2LineTypes:
        '''Punching knife'''
        ...
    
    @classmethod
    @property
    def APPLIED_BUT_NOT_BURNED(cls) -> CF2LineTypes:
        '''The line is applied but not burned on the form.'''
        ...
    
    @classmethod
    @property
    def BURNED_BUT_NOT_CARRY_RULERS(cls) -> CF2LineTypes:
        '''The line is burned, but does not carry rulers and knives.'''
        ...
    
    @classmethod
    @property
    def WAVY_KNIFE_WITH_SYMMETRIC_WAVE(cls) -> CF2LineTypes:
        '''Wavy knife with symmetric wave'''
        ...
    
    @classmethod
    @property
    def DIMENSIONS(cls) -> CF2LineTypes:
        '''Dimension lines'''
        ...
    
    @classmethod
    @property
    def PERFORATOR(cls) -> CF2LineTypes:
        '''Perforator application line'''
        ...
    
    ...

class CF2SystemCoordinate:
    '''The type of coordinate system.'''
    
    @classmethod
    @property
    def UM(cls) -> CF2SystemCoordinate:
        '''Millimeters'''
        ...
    
    @classmethod
    @property
    def UI(cls) -> CF2SystemCoordinate:
        '''Inches'''
        ...
    
    ...

class CF2TypeDElement:
    '''CF2 type of drawn elements'''
    
    @classmethod
    @property
    def LINE(cls) -> CF2TypeDElement:
        '''The Line type'''
        ...
    
    @classmethod
    @property
    def ARC(cls) -> CF2TypeDElement:
        '''The Arc type'''
        ...
    
    @classmethod
    @property
    def TEXT(cls) -> CF2TypeDElement:
        '''The text type'''
        ...
    
    @classmethod
    @property
    def SUB_INSERT(cls) -> CF2TypeDElement:
        '''The sub insert type'''
        ...
    
    @classmethod
    @property
    def LINES_OUTPUT_DESCRIBING(cls) -> CF2TypeDElement:
        '''The description lines output'''
        ...
    
    @classmethod
    @property
    def ORDER_OUTPUT_DESCRIBING(cls) -> CF2TypeDElement:
        '''The description order section output'''
        ...
    
    ...

