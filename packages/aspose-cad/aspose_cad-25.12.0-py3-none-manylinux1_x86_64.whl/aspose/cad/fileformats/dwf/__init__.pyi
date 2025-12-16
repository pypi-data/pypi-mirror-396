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

class DwfImage(aspose.cad.Image):
    '''DWF image class.
    Provides reading of DWF/DWFX format files, their processing and their export to other formats.'''
    
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
        '''Caches the data and ensures no additional data loading will be performed from the underlying :py:attr:`aspose.cad.DataStreamSupporter.data_stream_container`.
        Depending on the loading options only the necessary part of the data can be loaded into the cache from the image data.
        In this case, we can use this method to load all image data into the cache.'''
        ...
    
    def get_strings(self) -> List[str]:
        '''Gets all string values from image.
        Provides an opportunity to get the values of all text graphic elements present
        in the image in the form of an array of strings.
        
        :returns: The array with string values.'''
        ...
    
    def can_save(self, options : aspose.cad.imageoptions.ImageOptionsBase) -> bool:
        '''Determines whether image can be saved to the specified file format represented by the passed save options.
        
        :param options: The save options to use.
        :returns: ``true`` if image can be saved to the specified file format represented by the passed save options; otherwise, ``false``.'''
        ...
    
    def add_element(self, page_number : int, element : aspose.cad.fileformats.dwf.whip.objects.drawable.DwfWhipDrawable) -> None:
        '''Adds graphic element to specified page.
        Provides an opportunity to add a new graphic element to the existing ones in the image.
        To add it, you need to create a new graphic element and
        specify the index of the page in :py:attr:`aspose.cad.fileformats.dwf.DwfImage.pages` array to which the element should be added.
        
        :param page_number: Index of the page in :py:attr:`aspose.cad.fileformats.dwf.DwfImage.pages` array to add element to.
        :param element: Element to be added.'''
        ...
    
    def remove_element(self, page_number : int, element_index : int) -> None:
        '''Removes graphic element from specified page.
        Provides the ability to remove a graphic element from the image.
        To remove it, you need to specify the page index in :py:attr:`aspose.cad.fileformats.dwf.DwfImage.pages` array from which the element should be removed
        and the index of the element in :py:attr:`aspose.cad.fileformats.dwf.DwfPage.entities` array.
        
        :param page_number: Index of page in :py:attr:`aspose.cad.fileformats.dwf.DwfImage.pages` array to remove element from.
        :param element_index: Index of element to be removed.'''
        ...
    
    def get_element_count(self, page_number : int) -> int:
        '''Gets count of graphic elements from specified page.
        Provides the ability to determine the number of graphic elements on a specific image page.
        To get this value, you need to specify the page index in the array :py:attr:`aspose.cad.fileformats.dwf.DwfImage.pages`, the number of elements of which you want to get.
        
        :param page_number: Index of page to get count of graphic elements from.
        :returns: Count of graphic elements in specified page.'''
        ...
    
    def update_size(self) -> None:
        '''Updates the image size.
        Provides forced calculation of image size parameters. This calculation must be performed
        before using the image size parameters after changing the graphic content of the image
        that affects the image size parameters.'''
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
    def pages(self) -> List[aspose.cad.fileformats.dwf.DwfPage]:
        '''Gets the DWF pages.
        Returns an array of all DWF pages that are contained in the DWF image.
        Each DWF page defines all its available graphical parameters and all the objects that are drawn on it.'''
        ...
    
    @property
    def metadata(self) -> List[aspose.cad.fileformats.dwf.DwfMetadata]:
        '''Gets the metadata information.
        Returns the array of metadata records from manifest and descriptors resources of Dwf/Dwfx package.'''
        ...
    
    @metadata.setter
    def metadata(self, value : List[aspose.cad.fileformats.dwf.DwfMetadata]):
        '''Sets the metadata information.
        Returns the array of metadata records from manifest and descriptors resources of Dwf/Dwfx package.'''
        ...
    
    @property
    def layers(self) -> aspose.cad.fileformats.dwf.DwfLayersList:
        '''Gets DWF pages layers.
        Returns the enumerable collection of DWF layers.
        The DWF data can be assigned to a specific DWF layer, which is a grouping drawing objects.'''
        ...
    
    ...

class DwfLayersList:
    '''Layer tables list'''
    
    def get_layer_by_name(self, name : str) -> aspose.cad.fileformats.dwf.whip.objects.DwfWhipLayer:
        '''Gets first layer by name.
        
        :param name: The name of layer.
        :returns: The layer or null if layer with "name" does not exist in the collection:py:class:`aspose.cad.fileformats.dwf.whip.objects.DwfWhipLayer`'''
        ...
    
    def get_layers_by_name(self, name : str) -> List[aspose.cad.fileformats.dwf.whip.objects.DwfWhipLayer]:
        '''Gets layer by name.
        
        :param name: The name of layer.
        :returns: The layers collection of:py:class:`aspose.cad.fileformats.dwf.whip.objects.DwfWhipLayer`'''
        ...
    
    def get_layers_by_names(self, layers_names : List[str]) -> List[aspose.cad.fileformats.dwf.whip.objects.DwfWhipLayer]:
        '''Gets layers by names.
        
        :param layers_names: Array names of layers.
        :returns: The list of :py:class:`aspose.cad.fileformats.dwf.whip.objects.DwfWhipLayer`layer objects'''
        ...
    
    def get_layers_names(self) -> List[str]:
        '''Gets the layers names.
        
        :returns: The list of :py:class:`str`layers names'''
        ...
    
    ...

class DwfLoadOptions(aspose.cad.LoadOptions):
    '''Represents the loading options for DWF image.'''
    
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
    def apply_camera_fields_clip(self) -> bool:
        ...
    
    @apply_camera_fields_clip.setter
    def apply_camera_fields_clip(self, value : bool):
        ...
    
    ...

class DwfMergeOptions:
    '''The DWF merge options.'''
    
    @property
    def merge_type(self) -> aspose.cad.fileformats.dwf.DwfMergeType:
        ...
    
    @merge_type.setter
    def merge_type(self, value : aspose.cad.fileformats.dwf.DwfMergeType):
        ...
    
    @property
    def source_path(self) -> str:
        ...
    
    @source_path.setter
    def source_path(self, value : str):
        ...
    
    @property
    def source_page_names(self) -> List[str]:
        ...
    
    @source_page_names.setter
    def source_page_names(self, value : List[str]):
        ...
    
    @property
    def destination_page_names(self) -> List[str]:
        ...
    
    @destination_page_names.setter
    def destination_page_names(self, value : List[str]):
        ...
    
    ...

class DwfMetadata:
    '''A class for storing information about a single record unit from a set of metadata and page descriptors in a Dwf/Dwfx file.'''
    
    @property
    def source(self) -> str:
        '''Gets the source (manifest or page descriptor) of the metadata information.'''
        ...
    
    @source.setter
    def source(self, value : str):
        '''Sets the source (manifest or page descriptor) of the metadata information.'''
        ...
    
    @property
    def category(self) -> str:
        '''Gets the category of the metadata information.'''
        ...
    
    @category.setter
    def category(self, value : str):
        '''Sets the category of the metadata information.'''
        ...
    
    @property
    def name(self) -> str:
        '''Gets the name of the metadata information.'''
        ...
    
    @name.setter
    def name(self, value : str):
        '''Sets the name of the metadata information.'''
        ...
    
    @property
    def value(self) -> str:
        '''Gets the value of the metadata information.'''
        ...
    
    @value.setter
    def value(self, value : str):
        '''Sets the value of the metadata information.'''
        ...
    
    ...

class DwfPage:
    '''Represents base class for DWF page.'''
    
    @property
    def name(self) -> str:
        '''Gets page name'''
        ...
    
    @property
    def unit_type(self) -> aspose.cad.imageoptions.UnitType:
        ...
    
    @property
    def object_id(self) -> str:
        ...
    
    @property
    def max_point(self) -> aspose.cad.fileformats.cad.cadobjects.Cad3DPoint:
        ...
    
    @property
    def min_point(self) -> aspose.cad.fileformats.cad.cadobjects.Cad3DPoint:
        ...
    
    @property
    def entities(self) -> List[aspose.cad.fileformats.dwf.whip.objects.drawable.DwfWhipDrawable]:
        '''Gets read only collection of draw objects'''
        ...
    
    @property
    def paper_width(self) -> float:
        ...
    
    @property
    def paper_height(self) -> float:
        ...
    
    @property
    def page_rotation(self) -> float:
        ...
    
    ...

class DwfMergeType:
    '''The DWF merge type.'''
    
    @classmethod
    @property
    def ADD_RASTER_OVERLAY(cls) -> DwfMergeType:
        '''Add raster overlay.'''
        ...
    
    @classmethod
    @property
    def ADD_PAGES(cls) -> DwfMergeType:
        '''Add pages.'''
        ...
    
    @classmethod
    @property
    def ADD_DGN_FILE(cls) -> DwfMergeType:
        '''Add DGN file.'''
        ...
    
    ...

