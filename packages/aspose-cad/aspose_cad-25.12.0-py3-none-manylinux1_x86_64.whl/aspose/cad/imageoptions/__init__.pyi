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

class ApsGroupOptions(ImageOptionsBase):
    '''The CGM options.'''
    
    @property
    def target_format(self) -> aspose.cad.FileFormat:
        ...
    
    @property
    def output_mode(self) -> aspose.cad.imageoptions.CadOutputMode:
        ...
    
    @output_mode.setter
    def output_mode(self, value : aspose.cad.imageoptions.CadOutputMode):
        ...
    
    @property
    def rotation(self) -> aspose.cad.RotateFlipType:
        '''Gets the parameter for rotate, flip, or rotate and flip the image..'''
        ...
    
    @rotation.setter
    def rotation(self, value : aspose.cad.RotateFlipType):
        '''Sets the parameter for rotate, flip, or rotate and flip the image..'''
        ...
    
    @property
    def layers(self) -> List[str]:
        '''Gets a of layer names must be exported.
        All data will be exported without layers if names is not sets.'''
        ...
    
    @layers.setter
    def layers(self, value : List[str]):
        '''Sets a of layer names must be exported.
        All data will be exported without layers if names is not sets.'''
        ...
    
    @property
    def xmp_data(self) -> aspose.cad.XmpPacketWrapper:
        ...
    
    @xmp_data.setter
    def xmp_data(self, value : aspose.cad.XmpPacketWrapper):
        ...
    
    @property
    def source(self) -> aspose.cad.Source:
        '''Gets the source to create image in.'''
        ...
    
    @source.setter
    def source(self, value : aspose.cad.Source):
        '''Sets the source to create image in.'''
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
    def resolution_settings(self) -> aspose.cad.ResolutionSetting:
        ...
    
    @resolution_settings.setter
    def resolution_settings(self, value : aspose.cad.ResolutionSetting):
        ...
    
    @property
    def vector_rasterization_options(self) -> aspose.cad.imageoptions.VectorRasterizationOptions:
        ...
    
    @vector_rasterization_options.setter
    def vector_rasterization_options(self, value : aspose.cad.imageoptions.VectorRasterizationOptions):
        ...
    
    @property
    def timeout(self) -> int:
        '''Timeout value for export operation (in milliseconds)'''
        ...
    
    @timeout.setter
    def timeout(self, value : int):
        '''Timeout value for export operation (in milliseconds)'''
        ...
    
    @property
    def pc_3_file(self) -> str:
        ...
    
    @pc_3_file.setter
    def pc_3_file(self, value : str):
        ...
    
    @property
    def render_to_graphics_bound(self) -> bool:
        ...
    
    @render_to_graphics_bound.setter
    def render_to_graphics_bound(self, value : bool):
        ...
    
    @property
    def user_watermark_text(self) -> str:
        ...
    
    @user_watermark_text.setter
    def user_watermark_text(self, value : str):
        ...
    
    @property
    def user_watermark_color(self) -> aspose.cad.Color:
        ...
    
    @user_watermark_color.setter
    def user_watermark_color(self, value : aspose.cad.Color):
        ...
    
    ...

class BmpOptions(ImageOptionsBase):
    '''The bmp file format creation options.'''
    
    @property
    def target_format(self) -> aspose.cad.FileFormat:
        ...
    
    @property
    def output_mode(self) -> aspose.cad.imageoptions.CadOutputMode:
        ...
    
    @output_mode.setter
    def output_mode(self, value : aspose.cad.imageoptions.CadOutputMode):
        ...
    
    @property
    def rotation(self) -> aspose.cad.RotateFlipType:
        '''Gets the parameter for rotate, flip, or rotate and flip the image..'''
        ...
    
    @rotation.setter
    def rotation(self, value : aspose.cad.RotateFlipType):
        '''Sets the parameter for rotate, flip, or rotate and flip the image..'''
        ...
    
    @property
    def layers(self) -> List[str]:
        '''Gets a of layer names must be exported.
        All data will be exported without layers if names is not sets.'''
        ...
    
    @layers.setter
    def layers(self, value : List[str]):
        '''Sets a of layer names must be exported.
        All data will be exported without layers if names is not sets.'''
        ...
    
    @property
    def xmp_data(self) -> aspose.cad.XmpPacketWrapper:
        ...
    
    @xmp_data.setter
    def xmp_data(self, value : aspose.cad.XmpPacketWrapper):
        ...
    
    @property
    def source(self) -> aspose.cad.Source:
        '''Gets the source to create image in.'''
        ...
    
    @source.setter
    def source(self, value : aspose.cad.Source):
        '''Sets the source to create image in.'''
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
    def resolution_settings(self) -> aspose.cad.ResolutionSetting:
        ...
    
    @resolution_settings.setter
    def resolution_settings(self, value : aspose.cad.ResolutionSetting):
        ...
    
    @property
    def vector_rasterization_options(self) -> aspose.cad.imageoptions.VectorRasterizationOptions:
        ...
    
    @vector_rasterization_options.setter
    def vector_rasterization_options(self, value : aspose.cad.imageoptions.VectorRasterizationOptions):
        ...
    
    @property
    def timeout(self) -> int:
        '''Timeout value for export operation (in milliseconds)'''
        ...
    
    @timeout.setter
    def timeout(self, value : int):
        '''Timeout value for export operation (in milliseconds)'''
        ...
    
    @property
    def pc_3_file(self) -> str:
        ...
    
    @pc_3_file.setter
    def pc_3_file(self, value : str):
        ...
    
    @property
    def render_to_graphics_bound(self) -> bool:
        ...
    
    @render_to_graphics_bound.setter
    def render_to_graphics_bound(self, value : bool):
        ...
    
    @property
    def user_watermark_text(self) -> str:
        ...
    
    @user_watermark_text.setter
    def user_watermark_text(self, value : str):
        ...
    
    @property
    def user_watermark_color(self) -> aspose.cad.Color:
        ...
    
    @user_watermark_color.setter
    def user_watermark_color(self, value : aspose.cad.Color):
        ...
    
    @property
    def bits_per_pixel(self) -> int:
        ...
    
    @bits_per_pixel.setter
    def bits_per_pixel(self, value : int):
        ...
    
    @property
    def compression(self) -> aspose.cad.fileformats.bmp.BitmapCompression:
        '''Gets the compression.'''
        ...
    
    @compression.setter
    def compression(self, value : aspose.cad.fileformats.bmp.BitmapCompression):
        '''Sets the compression.'''
        ...
    
    @property
    def horizontal_resolution(self) -> float:
        ...
    
    @horizontal_resolution.setter
    def horizontal_resolution(self, value : float):
        ...
    
    @property
    def vertical_resolution(self) -> float:
        ...
    
    @vertical_resolution.setter
    def vertical_resolution(self, value : float):
        ...
    
    ...

class CadRasterizationOptions(VectorRasterizationOptions):
    '''The Cad rasterization options.'''
    
    @property
    def border_x(self) -> float:
        ...
    
    @border_x.setter
    def border_x(self, value : float):
        ...
    
    @property
    def margins(self) -> aspose.cad.imageoptions.Margins:
        '''Gets Margins.'''
        ...
    
    @margins.setter
    def margins(self, value : aspose.cad.imageoptions.Margins):
        '''Sets Margins.'''
        ...
    
    @property
    def border_y(self) -> float:
        ...
    
    @border_y.setter
    def border_y(self, value : float):
        ...
    
    @property
    def page_height(self) -> float:
        ...
    
    @page_height.setter
    def page_height(self, value : float):
        ...
    
    @property
    def page_size(self) -> aspose.cad.SizeF:
        ...
    
    @page_size.setter
    def page_size(self, value : aspose.cad.SizeF):
        ...
    
    @property
    def page_width(self) -> float:
        ...
    
    @page_width.setter
    def page_width(self, value : float):
        ...
    
    @property
    def page_depth(self) -> float:
        ...
    
    @page_depth.setter
    def page_depth(self, value : float):
        ...
    
    @property
    def background_color(self) -> aspose.cad.Color:
        ...
    
    @background_color.setter
    def background_color(self, value : aspose.cad.Color):
        ...
    
    @property
    def embed_background(self) -> bool:
        ...
    
    @embed_background.setter
    def embed_background(self, value : bool):
        ...
    
    @property
    def draw_color(self) -> aspose.cad.Color:
        ...
    
    @draw_color.setter
    def draw_color(self, value : aspose.cad.Color):
        ...
    
    @property
    def unit_type(self) -> aspose.cad.imageoptions.UnitType:
        ...
    
    @unit_type.setter
    def unit_type(self, value : aspose.cad.imageoptions.UnitType):
        ...
    
    @property
    def content_as_bitmap(self) -> bool:
        ...
    
    @content_as_bitmap.setter
    def content_as_bitmap(self, value : bool):
        ...
    
    @property
    def graphics_options(self) -> aspose.cad.imageoptions.GraphicsOptions:
        ...
    
    @graphics_options.setter
    def graphics_options(self, value : aspose.cad.imageoptions.GraphicsOptions):
        ...
    
    @property
    def line_scale(self) -> float:
        ...
    
    @line_scale.setter
    def line_scale(self, value : float):
        ...
    
    @property
    def relative_scale(self) -> float:
        ...
    
    @relative_scale.setter
    def relative_scale(self, value : float):
        ...
    
    @property
    def relative_position(self) -> aspose.cad.PointF:
        ...
    
    @relative_position.setter
    def relative_position(self, value : aspose.cad.PointF):
        ...
    
    @property
    def zoom(self) -> float:
        '''Gets zoom factor. Allows to zoom drawing relatively to canvas size. Value of 1 corresponds to exact fit, value below 1 allows to preserve margins, value above 1 allows to scale drawing up.'''
        ...
    
    @zoom.setter
    def zoom(self, value : float):
        '''Sets zoom factor. Allows to zoom drawing relatively to canvas size. Value of 1 corresponds to exact fit, value below 1 allows to preserve margins, value above 1 allows to scale drawing up.'''
        ...
    
    @property
    def pen_options(self) -> aspose.cad.imageoptions.PenOptions:
        ...
    
    @pen_options.setter
    def pen_options(self, value : aspose.cad.imageoptions.PenOptions):
        ...
    
    @property
    def observer_point(self) -> aspose.cad.fileformats.ObserverPoint:
        ...
    
    @observer_point.setter
    def observer_point(self, value : aspose.cad.fileformats.ObserverPoint):
        ...
    
    @property
    def automatic_layouts_scaling(self) -> bool:
        ...
    
    @automatic_layouts_scaling.setter
    def automatic_layouts_scaling(self, value : bool):
        ...
    
    @property
    def layers(self) -> List[str]:
        '''Gets layers of DXF file to export.'''
        ...
    
    @layers.setter
    def layers(self, value : List[str]):
        '''Sets layers of DXF file to export.'''
        ...
    
    @property
    def layouts(self) -> List[str]:
        '''Gets the layoutName.'''
        ...
    
    @layouts.setter
    def layouts(self, value : List[str]):
        '''Sets the layoutName.'''
        ...
    
    @property
    def draw_type(self) -> aspose.cad.fileformats.cad.CadDrawTypeMode:
        ...
    
    @draw_type.setter
    def draw_type(self, value : aspose.cad.fileformats.cad.CadDrawTypeMode):
        ...
    
    @property
    def scale_method(self) -> aspose.cad.fileformats.cad.ScaleType:
        ...
    
    @scale_method.setter
    def scale_method(self, value : aspose.cad.fileformats.cad.ScaleType):
        ...
    
    @property
    def no_scaling(self) -> bool:
        ...
    
    @no_scaling.setter
    def no_scaling(self, value : bool):
        ...
    
    @property
    def pdf_product_location(self) -> str:
        ...
    
    @pdf_product_location.setter
    def pdf_product_location(self, value : str):
        ...
    
    @property
    def quality(self) -> aspose.cad.imageoptions.RasterizationQuality:
        '''Gets the quality.'''
        ...
    
    @quality.setter
    def quality(self, value : aspose.cad.imageoptions.RasterizationQuality):
        '''Sets the quality.'''
        ...
    
    @property
    def export_all_layout_content(self) -> bool:
        ...
    
    @export_all_layout_content.setter
    def export_all_layout_content(self, value : bool):
        ...
    
    @property
    def shx_fonts(self) -> List[str]:
        ...
    
    @shx_fonts.setter
    def shx_fonts(self, value : List[str]):
        ...
    
    @property
    def shx_code_pages(self) -> List[aspose.cad.fileformats.shx.ShxCodePage]:
        ...
    
    @shx_code_pages.setter
    def shx_code_pages(self, value : List[aspose.cad.fileformats.shx.ShxCodePage]):
        ...
    
    @property
    def render_mode_3d(self) -> aspose.cad.imageoptions.RenderMode3D:
        ...
    
    @render_mode_3d.setter
    def render_mode_3d(self, value : aspose.cad.imageoptions.RenderMode3D):
        ...
    
    @property
    def visibility_mode(self) -> aspose.cad.imageoptions.VisibilityMode:
        ...
    
    @visibility_mode.setter
    def visibility_mode(self, value : aspose.cad.imageoptions.VisibilityMode):
        ...
    
    ...

class CadRenderResult:
    '''Represents result of rendering'''
    
    @property
    def failures(self) -> List[aspose.cad.imageoptions.RenderResult]:
        '''List of rendering errors'''
        ...
    
    @property
    def is_render_complete(self) -> bool:
        ...
    
    ...

class CgmOptions(ImageOptionsBase):
    '''The CGM options.'''
    
    @property
    def target_format(self) -> aspose.cad.FileFormat:
        ...
    
    @property
    def output_mode(self) -> aspose.cad.imageoptions.CadOutputMode:
        ...
    
    @output_mode.setter
    def output_mode(self, value : aspose.cad.imageoptions.CadOutputMode):
        ...
    
    @property
    def rotation(self) -> aspose.cad.RotateFlipType:
        '''Gets the parameter for rotate, flip, or rotate and flip the image..'''
        ...
    
    @rotation.setter
    def rotation(self, value : aspose.cad.RotateFlipType):
        '''Sets the parameter for rotate, flip, or rotate and flip the image..'''
        ...
    
    @property
    def layers(self) -> List[str]:
        '''Gets a of layer names must be exported.
        All data will be exported without layers if names is not sets.'''
        ...
    
    @layers.setter
    def layers(self, value : List[str]):
        '''Sets a of layer names must be exported.
        All data will be exported without layers if names is not sets.'''
        ...
    
    @property
    def xmp_data(self) -> aspose.cad.XmpPacketWrapper:
        ...
    
    @xmp_data.setter
    def xmp_data(self, value : aspose.cad.XmpPacketWrapper):
        ...
    
    @property
    def source(self) -> aspose.cad.Source:
        '''Gets the source to create image in.'''
        ...
    
    @source.setter
    def source(self, value : aspose.cad.Source):
        '''Sets the source to create image in.'''
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
    def resolution_settings(self) -> aspose.cad.ResolutionSetting:
        ...
    
    @resolution_settings.setter
    def resolution_settings(self, value : aspose.cad.ResolutionSetting):
        ...
    
    @property
    def vector_rasterization_options(self) -> aspose.cad.imageoptions.VectorRasterizationOptions:
        ...
    
    @vector_rasterization_options.setter
    def vector_rasterization_options(self, value : aspose.cad.imageoptions.VectorRasterizationOptions):
        ...
    
    @property
    def timeout(self) -> int:
        '''Timeout value for export operation (in milliseconds)'''
        ...
    
    @timeout.setter
    def timeout(self, value : int):
        '''Timeout value for export operation (in milliseconds)'''
        ...
    
    @property
    def pc_3_file(self) -> str:
        ...
    
    @pc_3_file.setter
    def pc_3_file(self, value : str):
        ...
    
    @property
    def render_to_graphics_bound(self) -> bool:
        ...
    
    @render_to_graphics_bound.setter
    def render_to_graphics_bound(self, value : bool):
        ...
    
    @property
    def user_watermark_text(self) -> str:
        ...
    
    @user_watermark_text.setter
    def user_watermark_text(self, value : str):
        ...
    
    @property
    def user_watermark_color(self) -> aspose.cad.Color:
        ...
    
    @user_watermark_color.setter
    def user_watermark_color(self, value : aspose.cad.Color):
        ...
    
    ...

class DicomOptions(ImageOptionsBase):
    '''The DICOM file format creation options.'''
    
    @property
    def target_format(self) -> aspose.cad.FileFormat:
        ...
    
    @property
    def output_mode(self) -> aspose.cad.imageoptions.CadOutputMode:
        ...
    
    @output_mode.setter
    def output_mode(self, value : aspose.cad.imageoptions.CadOutputMode):
        ...
    
    @property
    def rotation(self) -> aspose.cad.RotateFlipType:
        '''Gets the parameter for rotate, flip, or rotate and flip the image..'''
        ...
    
    @rotation.setter
    def rotation(self, value : aspose.cad.RotateFlipType):
        '''Sets the parameter for rotate, flip, or rotate and flip the image..'''
        ...
    
    @property
    def layers(self) -> List[str]:
        '''Gets a of layer names must be exported.
        All data will be exported without layers if names is not sets.'''
        ...
    
    @layers.setter
    def layers(self, value : List[str]):
        '''Sets a of layer names must be exported.
        All data will be exported without layers if names is not sets.'''
        ...
    
    @property
    def xmp_data(self) -> aspose.cad.XmpPacketWrapper:
        ...
    
    @xmp_data.setter
    def xmp_data(self, value : aspose.cad.XmpPacketWrapper):
        ...
    
    @property
    def source(self) -> aspose.cad.Source:
        '''Gets the source to create image in.'''
        ...
    
    @source.setter
    def source(self, value : aspose.cad.Source):
        '''Sets the source to create image in.'''
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
    def resolution_settings(self) -> aspose.cad.ResolutionSetting:
        ...
    
    @resolution_settings.setter
    def resolution_settings(self, value : aspose.cad.ResolutionSetting):
        ...
    
    @property
    def vector_rasterization_options(self) -> aspose.cad.imageoptions.VectorRasterizationOptions:
        ...
    
    @vector_rasterization_options.setter
    def vector_rasterization_options(self, value : aspose.cad.imageoptions.VectorRasterizationOptions):
        ...
    
    @property
    def timeout(self) -> int:
        '''Timeout value for export operation (in milliseconds)'''
        ...
    
    @timeout.setter
    def timeout(self, value : int):
        '''Timeout value for export operation (in milliseconds)'''
        ...
    
    @property
    def pc_3_file(self) -> str:
        ...
    
    @pc_3_file.setter
    def pc_3_file(self, value : str):
        ...
    
    @property
    def render_to_graphics_bound(self) -> bool:
        ...
    
    @render_to_graphics_bound.setter
    def render_to_graphics_bound(self, value : bool):
        ...
    
    @property
    def user_watermark_text(self) -> str:
        ...
    
    @user_watermark_text.setter
    def user_watermark_text(self, value : str):
        ...
    
    @property
    def user_watermark_color(self) -> aspose.cad.Color:
        ...
    
    @user_watermark_color.setter
    def user_watermark_color(self, value : aspose.cad.Color):
        ...
    
    @property
    def compression(self) -> aspose.cad.fileformats.dicom.Compression:
        '''Gets the compression.'''
        ...
    
    @compression.setter
    def compression(self, value : aspose.cad.fileformats.dicom.Compression):
        '''Sets the compression.'''
        ...
    
    @property
    def color_type(self) -> aspose.cad.fileformats.dicom.ColorType:
        ...
    
    @color_type.setter
    def color_type(self, value : aspose.cad.fileformats.dicom.ColorType):
        ...
    
    ...

class DracoOptions(ImageOptionsBase):
    '''The Draco options.'''
    
    @property
    def target_format(self) -> aspose.cad.FileFormat:
        ...
    
    @property
    def output_mode(self) -> aspose.cad.imageoptions.CadOutputMode:
        ...
    
    @output_mode.setter
    def output_mode(self, value : aspose.cad.imageoptions.CadOutputMode):
        ...
    
    @property
    def rotation(self) -> aspose.cad.RotateFlipType:
        '''Gets the parameter for rotate, flip, or rotate and flip the image..'''
        ...
    
    @rotation.setter
    def rotation(self, value : aspose.cad.RotateFlipType):
        '''Sets the parameter for rotate, flip, or rotate and flip the image..'''
        ...
    
    @property
    def layers(self) -> List[str]:
        '''Gets a of layer names must be exported.
        All data will be exported without layers if names is not sets.'''
        ...
    
    @layers.setter
    def layers(self, value : List[str]):
        '''Sets a of layer names must be exported.
        All data will be exported without layers if names is not sets.'''
        ...
    
    @property
    def xmp_data(self) -> aspose.cad.XmpPacketWrapper:
        ...
    
    @xmp_data.setter
    def xmp_data(self, value : aspose.cad.XmpPacketWrapper):
        ...
    
    @property
    def source(self) -> aspose.cad.Source:
        '''Gets the source to create image in.'''
        ...
    
    @source.setter
    def source(self, value : aspose.cad.Source):
        '''Sets the source to create image in.'''
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
    def resolution_settings(self) -> aspose.cad.ResolutionSetting:
        ...
    
    @resolution_settings.setter
    def resolution_settings(self, value : aspose.cad.ResolutionSetting):
        ...
    
    @property
    def vector_rasterization_options(self) -> aspose.cad.imageoptions.VectorRasterizationOptions:
        ...
    
    @vector_rasterization_options.setter
    def vector_rasterization_options(self, value : aspose.cad.imageoptions.VectorRasterizationOptions):
        ...
    
    @property
    def timeout(self) -> int:
        '''Timeout value for export operation (in milliseconds)'''
        ...
    
    @timeout.setter
    def timeout(self, value : int):
        '''Timeout value for export operation (in milliseconds)'''
        ...
    
    @property
    def pc_3_file(self) -> str:
        ...
    
    @pc_3_file.setter
    def pc_3_file(self, value : str):
        ...
    
    @property
    def render_to_graphics_bound(self) -> bool:
        ...
    
    @render_to_graphics_bound.setter
    def render_to_graphics_bound(self, value : bool):
        ...
    
    @property
    def user_watermark_text(self) -> str:
        ...
    
    @user_watermark_text.setter
    def user_watermark_text(self, value : str):
        ...
    
    @property
    def user_watermark_color(self) -> aspose.cad.Color:
        ...
    
    @user_watermark_color.setter
    def user_watermark_color(self, value : aspose.cad.Color):
        ...
    
    ...

class DwfOptions(ImageOptionsBase):
    '''The DWF options.'''
    
    @property
    def target_format(self) -> aspose.cad.FileFormat:
        ...
    
    @property
    def output_mode(self) -> aspose.cad.imageoptions.CadOutputMode:
        ...
    
    @output_mode.setter
    def output_mode(self, value : aspose.cad.imageoptions.CadOutputMode):
        ...
    
    @property
    def rotation(self) -> aspose.cad.RotateFlipType:
        '''Gets the parameter for rotate, flip, or rotate and flip the image..'''
        ...
    
    @rotation.setter
    def rotation(self, value : aspose.cad.RotateFlipType):
        '''Sets the parameter for rotate, flip, or rotate and flip the image..'''
        ...
    
    @property
    def layers(self) -> List[str]:
        '''Gets a of layer names must be exported.
        All data will be exported without layers if names is not sets.'''
        ...
    
    @layers.setter
    def layers(self, value : List[str]):
        '''Sets a of layer names must be exported.
        All data will be exported without layers if names is not sets.'''
        ...
    
    @property
    def xmp_data(self) -> aspose.cad.XmpPacketWrapper:
        ...
    
    @xmp_data.setter
    def xmp_data(self, value : aspose.cad.XmpPacketWrapper):
        ...
    
    @property
    def source(self) -> aspose.cad.Source:
        '''Gets the source to create image in.'''
        ...
    
    @source.setter
    def source(self, value : aspose.cad.Source):
        '''Sets the source to create image in.'''
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
    def resolution_settings(self) -> aspose.cad.ResolutionSetting:
        ...
    
    @resolution_settings.setter
    def resolution_settings(self, value : aspose.cad.ResolutionSetting):
        ...
    
    @property
    def vector_rasterization_options(self) -> aspose.cad.imageoptions.VectorRasterizationOptions:
        ...
    
    @vector_rasterization_options.setter
    def vector_rasterization_options(self, value : aspose.cad.imageoptions.VectorRasterizationOptions):
        ...
    
    @property
    def timeout(self) -> int:
        '''Timeout value for export operation (in milliseconds)'''
        ...
    
    @timeout.setter
    def timeout(self, value : int):
        '''Timeout value for export operation (in milliseconds)'''
        ...
    
    @property
    def pc_3_file(self) -> str:
        ...
    
    @pc_3_file.setter
    def pc_3_file(self, value : str):
        ...
    
    @property
    def render_to_graphics_bound(self) -> bool:
        ...
    
    @render_to_graphics_bound.setter
    def render_to_graphics_bound(self, value : bool):
        ...
    
    @property
    def user_watermark_text(self) -> str:
        ...
    
    @user_watermark_text.setter
    def user_watermark_text(self, value : str):
        ...
    
    @property
    def user_watermark_color(self) -> aspose.cad.Color:
        ...
    
    @user_watermark_color.setter
    def user_watermark_color(self, value : aspose.cad.Color):
        ...
    
    @property
    def target_dwf_interface(self) -> int:
        ...
    
    @target_dwf_interface.setter
    def target_dwf_interface(self, value : int):
        ...
    
    @property
    def merge_options(self) -> aspose.cad.fileformats.dwf.DwfMergeOptions:
        ...
    
    @merge_options.setter
    def merge_options(self, value : aspose.cad.fileformats.dwf.DwfMergeOptions):
        ...
    
    @property
    def bezier_point_count(self) -> byte:
        ...
    
    @bezier_point_count.setter
    def bezier_point_count(self, value : byte):
        ...
    
    ...

class DwfxOptions(DwfOptions):
    '''The DWFx options.'''
    
    @property
    def target_format(self) -> aspose.cad.FileFormat:
        ...
    
    @property
    def output_mode(self) -> aspose.cad.imageoptions.CadOutputMode:
        ...
    
    @output_mode.setter
    def output_mode(self, value : aspose.cad.imageoptions.CadOutputMode):
        ...
    
    @property
    def rotation(self) -> aspose.cad.RotateFlipType:
        '''Gets the parameter for rotate, flip, or rotate and flip the image..'''
        ...
    
    @rotation.setter
    def rotation(self, value : aspose.cad.RotateFlipType):
        '''Sets the parameter for rotate, flip, or rotate and flip the image..'''
        ...
    
    @property
    def layers(self) -> List[str]:
        '''Gets a of layer names must be exported.
        All data will be exported without layers if names is not sets.'''
        ...
    
    @layers.setter
    def layers(self, value : List[str]):
        '''Sets a of layer names must be exported.
        All data will be exported without layers if names is not sets.'''
        ...
    
    @property
    def xmp_data(self) -> aspose.cad.XmpPacketWrapper:
        ...
    
    @xmp_data.setter
    def xmp_data(self, value : aspose.cad.XmpPacketWrapper):
        ...
    
    @property
    def source(self) -> aspose.cad.Source:
        '''Gets the source to create image in.'''
        ...
    
    @source.setter
    def source(self, value : aspose.cad.Source):
        '''Sets the source to create image in.'''
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
    def resolution_settings(self) -> aspose.cad.ResolutionSetting:
        ...
    
    @resolution_settings.setter
    def resolution_settings(self, value : aspose.cad.ResolutionSetting):
        ...
    
    @property
    def vector_rasterization_options(self) -> aspose.cad.imageoptions.VectorRasterizationOptions:
        ...
    
    @vector_rasterization_options.setter
    def vector_rasterization_options(self, value : aspose.cad.imageoptions.VectorRasterizationOptions):
        ...
    
    @property
    def timeout(self) -> int:
        '''Timeout value for export operation (in milliseconds)'''
        ...
    
    @timeout.setter
    def timeout(self, value : int):
        '''Timeout value for export operation (in milliseconds)'''
        ...
    
    @property
    def pc_3_file(self) -> str:
        ...
    
    @pc_3_file.setter
    def pc_3_file(self, value : str):
        ...
    
    @property
    def render_to_graphics_bound(self) -> bool:
        ...
    
    @render_to_graphics_bound.setter
    def render_to_graphics_bound(self, value : bool):
        ...
    
    @property
    def user_watermark_text(self) -> str:
        ...
    
    @user_watermark_text.setter
    def user_watermark_text(self, value : str):
        ...
    
    @property
    def user_watermark_color(self) -> aspose.cad.Color:
        ...
    
    @user_watermark_color.setter
    def user_watermark_color(self, value : aspose.cad.Color):
        ...
    
    @property
    def target_dwf_interface(self) -> int:
        ...
    
    @target_dwf_interface.setter
    def target_dwf_interface(self, value : int):
        ...
    
    @property
    def merge_options(self) -> aspose.cad.fileformats.dwf.DwfMergeOptions:
        ...
    
    @merge_options.setter
    def merge_options(self, value : aspose.cad.fileformats.dwf.DwfMergeOptions):
        ...
    
    @property
    def bezier_point_count(self) -> byte:
        ...
    
    @bezier_point_count.setter
    def bezier_point_count(self, value : byte):
        ...
    
    ...

class DwgOptions(ImageOptionsBase):
    '''The DWG file format creation options.'''
    
    @property
    def target_format(self) -> aspose.cad.FileFormat:
        ...
    
    @property
    def output_mode(self) -> aspose.cad.imageoptions.CadOutputMode:
        ...
    
    @output_mode.setter
    def output_mode(self, value : aspose.cad.imageoptions.CadOutputMode):
        ...
    
    @property
    def rotation(self) -> aspose.cad.RotateFlipType:
        '''Gets the parameter for rotate, flip, or rotate and flip the image..'''
        ...
    
    @rotation.setter
    def rotation(self, value : aspose.cad.RotateFlipType):
        '''Sets the parameter for rotate, flip, or rotate and flip the image..'''
        ...
    
    @property
    def layers(self) -> List[str]:
        '''Gets a of layer names must be exported.
        All data will be exported without layers if names is not sets.'''
        ...
    
    @layers.setter
    def layers(self, value : List[str]):
        '''Sets a of layer names must be exported.
        All data will be exported without layers if names is not sets.'''
        ...
    
    @property
    def xmp_data(self) -> aspose.cad.XmpPacketWrapper:
        ...
    
    @xmp_data.setter
    def xmp_data(self, value : aspose.cad.XmpPacketWrapper):
        ...
    
    @property
    def source(self) -> aspose.cad.Source:
        '''Gets the source to create image in.'''
        ...
    
    @source.setter
    def source(self, value : aspose.cad.Source):
        '''Sets the source to create image in.'''
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
    def resolution_settings(self) -> aspose.cad.ResolutionSetting:
        ...
    
    @resolution_settings.setter
    def resolution_settings(self, value : aspose.cad.ResolutionSetting):
        ...
    
    @property
    def vector_rasterization_options(self) -> aspose.cad.imageoptions.VectorRasterizationOptions:
        ...
    
    @vector_rasterization_options.setter
    def vector_rasterization_options(self, value : aspose.cad.imageoptions.VectorRasterizationOptions):
        ...
    
    @property
    def timeout(self) -> int:
        '''Timeout value for export operation (in milliseconds)'''
        ...
    
    @timeout.setter
    def timeout(self, value : int):
        '''Timeout value for export operation (in milliseconds)'''
        ...
    
    @property
    def pc_3_file(self) -> str:
        ...
    
    @pc_3_file.setter
    def pc_3_file(self, value : str):
        ...
    
    @property
    def render_to_graphics_bound(self) -> bool:
        ...
    
    @render_to_graphics_bound.setter
    def render_to_graphics_bound(self, value : bool):
        ...
    
    @property
    def user_watermark_text(self) -> str:
        ...
    
    @user_watermark_text.setter
    def user_watermark_text(self, value : str):
        ...
    
    @property
    def user_watermark_color(self) -> aspose.cad.Color:
        ...
    
    @user_watermark_color.setter
    def user_watermark_color(self, value : aspose.cad.Color):
        ...
    
    @property
    def origin_position(self) -> aspose.cad.primitives.Point3D:
        ...
    
    @origin_position.setter
    def origin_position(self, value : aspose.cad.primitives.Point3D):
        ...
    
    ...

class DxfOptions(ImageOptionsBase):
    '''Class for DXF format output creation options'''
    
    @property
    def target_format(self) -> aspose.cad.FileFormat:
        ...
    
    @property
    def output_mode(self) -> aspose.cad.imageoptions.CadOutputMode:
        ...
    
    @output_mode.setter
    def output_mode(self, value : aspose.cad.imageoptions.CadOutputMode):
        ...
    
    @property
    def rotation(self) -> aspose.cad.RotateFlipType:
        '''Gets the parameter for rotate, flip, or rotate and flip the image..'''
        ...
    
    @rotation.setter
    def rotation(self, value : aspose.cad.RotateFlipType):
        '''Sets the parameter for rotate, flip, or rotate and flip the image..'''
        ...
    
    @property
    def layers(self) -> List[str]:
        '''Gets a of layer names must be exported.
        All data will be exported without layers if names is not sets.'''
        ...
    
    @layers.setter
    def layers(self, value : List[str]):
        '''Sets a of layer names must be exported.
        All data will be exported without layers if names is not sets.'''
        ...
    
    @property
    def xmp_data(self) -> aspose.cad.XmpPacketWrapper:
        ...
    
    @xmp_data.setter
    def xmp_data(self, value : aspose.cad.XmpPacketWrapper):
        ...
    
    @property
    def source(self) -> aspose.cad.Source:
        '''Gets the source to create image in.'''
        ...
    
    @source.setter
    def source(self, value : aspose.cad.Source):
        '''Sets the source to create image in.'''
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
    def resolution_settings(self) -> aspose.cad.ResolutionSetting:
        ...
    
    @resolution_settings.setter
    def resolution_settings(self, value : aspose.cad.ResolutionSetting):
        ...
    
    @property
    def vector_rasterization_options(self) -> aspose.cad.imageoptions.VectorRasterizationOptions:
        ...
    
    @vector_rasterization_options.setter
    def vector_rasterization_options(self, value : aspose.cad.imageoptions.VectorRasterizationOptions):
        ...
    
    @property
    def timeout(self) -> int:
        '''Timeout value for export operation (in milliseconds)'''
        ...
    
    @timeout.setter
    def timeout(self, value : int):
        '''Timeout value for export operation (in milliseconds)'''
        ...
    
    @property
    def pc_3_file(self) -> str:
        ...
    
    @pc_3_file.setter
    def pc_3_file(self, value : str):
        ...
    
    @property
    def render_to_graphics_bound(self) -> bool:
        ...
    
    @render_to_graphics_bound.setter
    def render_to_graphics_bound(self, value : bool):
        ...
    
    @property
    def user_watermark_text(self) -> str:
        ...
    
    @user_watermark_text.setter
    def user_watermark_text(self, value : str):
        ...
    
    @property
    def user_watermark_color(self) -> aspose.cad.Color:
        ...
    
    @user_watermark_color.setter
    def user_watermark_color(self, value : aspose.cad.Color):
        ...
    
    @property
    def version(self) -> aspose.cad.imageoptions.DxfOutputVersion:
        '''Version of output DXF format'''
        ...
    
    @version.setter
    def version(self, value : aspose.cad.imageoptions.DxfOutputVersion):
        '''Version of output DXF format'''
        ...
    
    @property
    def dxf_file_format(self) -> aspose.cad.fileformats.cad.cadconsts.CadFileFormat:
        ...
    
    @dxf_file_format.setter
    def dxf_file_format(self, value : aspose.cad.fileformats.cad.cadconsts.CadFileFormat):
        ...
    
    @property
    def merge_lines_inside_contour(self) -> bool:
        ...
    
    @merge_lines_inside_contour.setter
    def merge_lines_inside_contour(self, value : bool):
        ...
    
    @property
    def bezier_point_count(self) -> byte:
        ...
    
    @bezier_point_count.setter
    def bezier_point_count(self, value : byte):
        ...
    
    @property
    def convert_text_beziers(self) -> bool:
        ...
    
    @convert_text_beziers.setter
    def convert_text_beziers(self, value : bool):
        ...
    
    @property
    def text_as_lines(self) -> bool:
        ...
    
    @text_as_lines.setter
    def text_as_lines(self, value : bool):
        ...
    
    @property
    def origin_position(self) -> aspose.cad.primitives.Point3D:
        ...
    
    @origin_position.setter
    def origin_position(self, value : aspose.cad.primitives.Point3D):
        ...
    
    @property
    def pretty_formatting(self) -> bool:
        ...
    
    @pretty_formatting.setter
    def pretty_formatting(self, value : bool):
        ...
    
    @property
    def try_convert_to_mesh(self) -> bool:
        ...
    
    @try_convert_to_mesh.setter
    def try_convert_to_mesh(self, value : bool):
        ...
    
    ...

class EmfOptions(ImageOptionsBase):
    '''The EMF file format creation options.'''
    
    @property
    def target_format(self) -> aspose.cad.FileFormat:
        ...
    
    @property
    def output_mode(self) -> aspose.cad.imageoptions.CadOutputMode:
        ...
    
    @output_mode.setter
    def output_mode(self, value : aspose.cad.imageoptions.CadOutputMode):
        ...
    
    @property
    def rotation(self) -> aspose.cad.RotateFlipType:
        '''Gets the parameter for rotate, flip, or rotate and flip the image..'''
        ...
    
    @rotation.setter
    def rotation(self, value : aspose.cad.RotateFlipType):
        '''Sets the parameter for rotate, flip, or rotate and flip the image..'''
        ...
    
    @property
    def layers(self) -> List[str]:
        '''Gets a of layer names must be exported.
        All data will be exported without layers if names is not sets.'''
        ...
    
    @layers.setter
    def layers(self, value : List[str]):
        '''Sets a of layer names must be exported.
        All data will be exported without layers if names is not sets.'''
        ...
    
    @property
    def xmp_data(self) -> aspose.cad.XmpPacketWrapper:
        ...
    
    @xmp_data.setter
    def xmp_data(self, value : aspose.cad.XmpPacketWrapper):
        ...
    
    @property
    def source(self) -> aspose.cad.Source:
        '''Gets the source to create image in.'''
        ...
    
    @source.setter
    def source(self, value : aspose.cad.Source):
        '''Sets the source to create image in.'''
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
    def resolution_settings(self) -> aspose.cad.ResolutionSetting:
        ...
    
    @resolution_settings.setter
    def resolution_settings(self, value : aspose.cad.ResolutionSetting):
        ...
    
    @property
    def vector_rasterization_options(self) -> aspose.cad.imageoptions.VectorRasterizationOptions:
        ...
    
    @vector_rasterization_options.setter
    def vector_rasterization_options(self, value : aspose.cad.imageoptions.VectorRasterizationOptions):
        ...
    
    @property
    def timeout(self) -> int:
        '''Timeout value for export operation (in milliseconds)'''
        ...
    
    @timeout.setter
    def timeout(self, value : int):
        '''Timeout value for export operation (in milliseconds)'''
        ...
    
    @property
    def pc_3_file(self) -> str:
        ...
    
    @pc_3_file.setter
    def pc_3_file(self, value : str):
        ...
    
    @property
    def render_to_graphics_bound(self) -> bool:
        ...
    
    @render_to_graphics_bound.setter
    def render_to_graphics_bound(self, value : bool):
        ...
    
    @property
    def user_watermark_text(self) -> str:
        ...
    
    @user_watermark_text.setter
    def user_watermark_text(self, value : str):
        ...
    
    @property
    def user_watermark_color(self) -> aspose.cad.Color:
        ...
    
    @user_watermark_color.setter
    def user_watermark_color(self, value : aspose.cad.Color):
        ...
    
    @property
    def compress(self) -> bool:
        '''Gets a value indicating whether this instance is compressed.'''
        ...
    
    @compress.setter
    def compress(self, value : bool):
        '''Sets a value indicating whether this instance is compressed.'''
        ...
    
    ...

class FbxOptions(ImageOptionsBase):
    '''The Fbx options.'''
    
    @property
    def target_format(self) -> aspose.cad.FileFormat:
        ...
    
    @property
    def output_mode(self) -> aspose.cad.imageoptions.CadOutputMode:
        ...
    
    @output_mode.setter
    def output_mode(self, value : aspose.cad.imageoptions.CadOutputMode):
        ...
    
    @property
    def rotation(self) -> aspose.cad.RotateFlipType:
        '''Gets the parameter for rotate, flip, or rotate and flip the image..'''
        ...
    
    @rotation.setter
    def rotation(self, value : aspose.cad.RotateFlipType):
        '''Sets the parameter for rotate, flip, or rotate and flip the image..'''
        ...
    
    @property
    def layers(self) -> List[str]:
        '''Gets a of layer names must be exported.
        All data will be exported without layers if names is not sets.'''
        ...
    
    @layers.setter
    def layers(self, value : List[str]):
        '''Sets a of layer names must be exported.
        All data will be exported without layers if names is not sets.'''
        ...
    
    @property
    def xmp_data(self) -> aspose.cad.XmpPacketWrapper:
        ...
    
    @xmp_data.setter
    def xmp_data(self, value : aspose.cad.XmpPacketWrapper):
        ...
    
    @property
    def source(self) -> aspose.cad.Source:
        '''Gets the source to create image in.'''
        ...
    
    @source.setter
    def source(self, value : aspose.cad.Source):
        '''Sets the source to create image in.'''
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
    def resolution_settings(self) -> aspose.cad.ResolutionSetting:
        ...
    
    @resolution_settings.setter
    def resolution_settings(self, value : aspose.cad.ResolutionSetting):
        ...
    
    @property
    def vector_rasterization_options(self) -> aspose.cad.imageoptions.VectorRasterizationOptions:
        ...
    
    @vector_rasterization_options.setter
    def vector_rasterization_options(self, value : aspose.cad.imageoptions.VectorRasterizationOptions):
        ...
    
    @property
    def timeout(self) -> int:
        '''Timeout value for export operation (in milliseconds)'''
        ...
    
    @timeout.setter
    def timeout(self, value : int):
        '''Timeout value for export operation (in milliseconds)'''
        ...
    
    @property
    def pc_3_file(self) -> str:
        ...
    
    @pc_3_file.setter
    def pc_3_file(self, value : str):
        ...
    
    @property
    def render_to_graphics_bound(self) -> bool:
        ...
    
    @render_to_graphics_bound.setter
    def render_to_graphics_bound(self, value : bool):
        ...
    
    @property
    def user_watermark_text(self) -> str:
        ...
    
    @user_watermark_text.setter
    def user_watermark_text(self, value : str):
        ...
    
    @property
    def user_watermark_color(self) -> aspose.cad.Color:
        ...
    
    @user_watermark_color.setter
    def user_watermark_color(self, value : aspose.cad.Color):
        ...
    
    ...

class GifOptions(ImageOptionsBase):
    '''The gif file format creation options.'''
    
    @property
    def target_format(self) -> aspose.cad.FileFormat:
        ...
    
    @property
    def output_mode(self) -> aspose.cad.imageoptions.CadOutputMode:
        ...
    
    @output_mode.setter
    def output_mode(self, value : aspose.cad.imageoptions.CadOutputMode):
        ...
    
    @property
    def rotation(self) -> aspose.cad.RotateFlipType:
        '''Gets the parameter for rotate, flip, or rotate and flip the image..'''
        ...
    
    @rotation.setter
    def rotation(self, value : aspose.cad.RotateFlipType):
        '''Sets the parameter for rotate, flip, or rotate and flip the image..'''
        ...
    
    @property
    def layers(self) -> List[str]:
        '''Gets a of layer names must be exported.
        All data will be exported without layers if names is not sets.'''
        ...
    
    @layers.setter
    def layers(self, value : List[str]):
        '''Sets a of layer names must be exported.
        All data will be exported without layers if names is not sets.'''
        ...
    
    @property
    def xmp_data(self) -> aspose.cad.XmpPacketWrapper:
        ...
    
    @xmp_data.setter
    def xmp_data(self, value : aspose.cad.XmpPacketWrapper):
        ...
    
    @property
    def source(self) -> aspose.cad.Source:
        '''Gets the source to create image in.'''
        ...
    
    @source.setter
    def source(self, value : aspose.cad.Source):
        '''Sets the source to create image in.'''
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
    def resolution_settings(self) -> aspose.cad.ResolutionSetting:
        ...
    
    @resolution_settings.setter
    def resolution_settings(self, value : aspose.cad.ResolutionSetting):
        ...
    
    @property
    def vector_rasterization_options(self) -> aspose.cad.imageoptions.VectorRasterizationOptions:
        ...
    
    @vector_rasterization_options.setter
    def vector_rasterization_options(self, value : aspose.cad.imageoptions.VectorRasterizationOptions):
        ...
    
    @property
    def timeout(self) -> int:
        '''Timeout value for export operation (in milliseconds)'''
        ...
    
    @timeout.setter
    def timeout(self, value : int):
        '''Timeout value for export operation (in milliseconds)'''
        ...
    
    @property
    def pc_3_file(self) -> str:
        ...
    
    @pc_3_file.setter
    def pc_3_file(self, value : str):
        ...
    
    @property
    def render_to_graphics_bound(self) -> bool:
        ...
    
    @render_to_graphics_bound.setter
    def render_to_graphics_bound(self, value : bool):
        ...
    
    @property
    def user_watermark_text(self) -> str:
        ...
    
    @user_watermark_text.setter
    def user_watermark_text(self, value : str):
        ...
    
    @property
    def user_watermark_color(self) -> aspose.cad.Color:
        ...
    
    @user_watermark_color.setter
    def user_watermark_color(self, value : aspose.cad.Color):
        ...
    
    @property
    def do_palette_correction(self) -> bool:
        ...
    
    @do_palette_correction.setter
    def do_palette_correction(self, value : bool):
        ...
    
    @property
    def color_resolution(self) -> byte:
        ...
    
    @color_resolution.setter
    def color_resolution(self, value : byte):
        ...
    
    @property
    def is_palette_sorted(self) -> bool:
        ...
    
    @is_palette_sorted.setter
    def is_palette_sorted(self, value : bool):
        ...
    
    @property
    def pixel_aspect_ratio(self) -> byte:
        ...
    
    @pixel_aspect_ratio.setter
    def pixel_aspect_ratio(self, value : byte):
        ...
    
    @property
    def background_color_index(self) -> byte:
        ...
    
    @background_color_index.setter
    def background_color_index(self, value : byte):
        ...
    
    @property
    def has_trailer(self) -> bool:
        ...
    
    @has_trailer.setter
    def has_trailer(self, value : bool):
        ...
    
    @property
    def interlaced(self) -> bool:
        '''True if image should be interlaced.'''
        ...
    
    @interlaced.setter
    def interlaced(self, value : bool):
        '''True if image should be interlaced.'''
        ...
    
    ...

class GlbGltfOptionsBase(ImageOptionsBase):
    '''The GLTF options.'''
    
    @property
    def target_format(self) -> aspose.cad.FileFormat:
        ...
    
    @property
    def output_mode(self) -> aspose.cad.imageoptions.CadOutputMode:
        ...
    
    @output_mode.setter
    def output_mode(self, value : aspose.cad.imageoptions.CadOutputMode):
        ...
    
    @property
    def rotation(self) -> aspose.cad.RotateFlipType:
        '''Gets the parameter for rotate, flip, or rotate and flip the image..'''
        ...
    
    @rotation.setter
    def rotation(self, value : aspose.cad.RotateFlipType):
        '''Sets the parameter for rotate, flip, or rotate and flip the image..'''
        ...
    
    @property
    def layers(self) -> List[str]:
        '''Gets a of layer names must be exported.
        All data will be exported without layers if names is not sets.'''
        ...
    
    @layers.setter
    def layers(self, value : List[str]):
        '''Sets a of layer names must be exported.
        All data will be exported without layers if names is not sets.'''
        ...
    
    @property
    def xmp_data(self) -> aspose.cad.XmpPacketWrapper:
        ...
    
    @xmp_data.setter
    def xmp_data(self, value : aspose.cad.XmpPacketWrapper):
        ...
    
    @property
    def source(self) -> aspose.cad.Source:
        '''Gets the source to create image in.'''
        ...
    
    @source.setter
    def source(self, value : aspose.cad.Source):
        '''Sets the source to create image in.'''
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
    def resolution_settings(self) -> aspose.cad.ResolutionSetting:
        ...
    
    @resolution_settings.setter
    def resolution_settings(self, value : aspose.cad.ResolutionSetting):
        ...
    
    @property
    def vector_rasterization_options(self) -> aspose.cad.imageoptions.VectorRasterizationOptions:
        ...
    
    @vector_rasterization_options.setter
    def vector_rasterization_options(self, value : aspose.cad.imageoptions.VectorRasterizationOptions):
        ...
    
    @property
    def timeout(self) -> int:
        '''Timeout value for export operation (in milliseconds)'''
        ...
    
    @timeout.setter
    def timeout(self, value : int):
        '''Timeout value for export operation (in milliseconds)'''
        ...
    
    @property
    def pc_3_file(self) -> str:
        ...
    
    @pc_3_file.setter
    def pc_3_file(self, value : str):
        ...
    
    @property
    def render_to_graphics_bound(self) -> bool:
        ...
    
    @render_to_graphics_bound.setter
    def render_to_graphics_bound(self, value : bool):
        ...
    
    @property
    def user_watermark_text(self) -> str:
        ...
    
    @user_watermark_text.setter
    def user_watermark_text(self, value : str):
        ...
    
    @property
    def user_watermark_color(self) -> aspose.cad.Color:
        ...
    
    @user_watermark_color.setter
    def user_watermark_color(self, value : aspose.cad.Color):
        ...
    
    ...

class GlbOptions(GlbGltfOptionsBase):
    '''The GLB options.'''
    
    @property
    def target_format(self) -> aspose.cad.FileFormat:
        ...
    
    @property
    def output_mode(self) -> aspose.cad.imageoptions.CadOutputMode:
        ...
    
    @output_mode.setter
    def output_mode(self, value : aspose.cad.imageoptions.CadOutputMode):
        ...
    
    @property
    def rotation(self) -> aspose.cad.RotateFlipType:
        '''Gets the parameter for rotate, flip, or rotate and flip the image..'''
        ...
    
    @rotation.setter
    def rotation(self, value : aspose.cad.RotateFlipType):
        '''Sets the parameter for rotate, flip, or rotate and flip the image..'''
        ...
    
    @property
    def layers(self) -> List[str]:
        '''Gets a of layer names must be exported.
        All data will be exported without layers if names is not sets.'''
        ...
    
    @layers.setter
    def layers(self, value : List[str]):
        '''Sets a of layer names must be exported.
        All data will be exported without layers if names is not sets.'''
        ...
    
    @property
    def xmp_data(self) -> aspose.cad.XmpPacketWrapper:
        ...
    
    @xmp_data.setter
    def xmp_data(self, value : aspose.cad.XmpPacketWrapper):
        ...
    
    @property
    def source(self) -> aspose.cad.Source:
        '''Gets the source to create image in.'''
        ...
    
    @source.setter
    def source(self, value : aspose.cad.Source):
        '''Sets the source to create image in.'''
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
    def resolution_settings(self) -> aspose.cad.ResolutionSetting:
        ...
    
    @resolution_settings.setter
    def resolution_settings(self, value : aspose.cad.ResolutionSetting):
        ...
    
    @property
    def vector_rasterization_options(self) -> aspose.cad.imageoptions.VectorRasterizationOptions:
        ...
    
    @vector_rasterization_options.setter
    def vector_rasterization_options(self, value : aspose.cad.imageoptions.VectorRasterizationOptions):
        ...
    
    @property
    def timeout(self) -> int:
        '''Timeout value for export operation (in milliseconds)'''
        ...
    
    @timeout.setter
    def timeout(self, value : int):
        '''Timeout value for export operation (in milliseconds)'''
        ...
    
    @property
    def pc_3_file(self) -> str:
        ...
    
    @pc_3_file.setter
    def pc_3_file(self, value : str):
        ...
    
    @property
    def render_to_graphics_bound(self) -> bool:
        ...
    
    @render_to_graphics_bound.setter
    def render_to_graphics_bound(self, value : bool):
        ...
    
    @property
    def user_watermark_text(self) -> str:
        ...
    
    @user_watermark_text.setter
    def user_watermark_text(self, value : str):
        ...
    
    @property
    def user_watermark_color(self) -> aspose.cad.Color:
        ...
    
    @user_watermark_color.setter
    def user_watermark_color(self, value : aspose.cad.Color):
        ...
    
    ...

class GltfOptions(GlbGltfOptionsBase):
    '''The GLTF options.'''
    
    @property
    def target_format(self) -> aspose.cad.FileFormat:
        ...
    
    @property
    def output_mode(self) -> aspose.cad.imageoptions.CadOutputMode:
        ...
    
    @output_mode.setter
    def output_mode(self, value : aspose.cad.imageoptions.CadOutputMode):
        ...
    
    @property
    def rotation(self) -> aspose.cad.RotateFlipType:
        '''Gets the parameter for rotate, flip, or rotate and flip the image..'''
        ...
    
    @rotation.setter
    def rotation(self, value : aspose.cad.RotateFlipType):
        '''Sets the parameter for rotate, flip, or rotate and flip the image..'''
        ...
    
    @property
    def layers(self) -> List[str]:
        '''Gets a of layer names must be exported.
        All data will be exported without layers if names is not sets.'''
        ...
    
    @layers.setter
    def layers(self, value : List[str]):
        '''Sets a of layer names must be exported.
        All data will be exported without layers if names is not sets.'''
        ...
    
    @property
    def xmp_data(self) -> aspose.cad.XmpPacketWrapper:
        ...
    
    @xmp_data.setter
    def xmp_data(self, value : aspose.cad.XmpPacketWrapper):
        ...
    
    @property
    def source(self) -> aspose.cad.Source:
        '''Gets the source to create image in.'''
        ...
    
    @source.setter
    def source(self, value : aspose.cad.Source):
        '''Sets the source to create image in.'''
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
    def resolution_settings(self) -> aspose.cad.ResolutionSetting:
        ...
    
    @resolution_settings.setter
    def resolution_settings(self, value : aspose.cad.ResolutionSetting):
        ...
    
    @property
    def vector_rasterization_options(self) -> aspose.cad.imageoptions.VectorRasterizationOptions:
        ...
    
    @vector_rasterization_options.setter
    def vector_rasterization_options(self, value : aspose.cad.imageoptions.VectorRasterizationOptions):
        ...
    
    @property
    def timeout(self) -> int:
        '''Timeout value for export operation (in milliseconds)'''
        ...
    
    @timeout.setter
    def timeout(self, value : int):
        '''Timeout value for export operation (in milliseconds)'''
        ...
    
    @property
    def pc_3_file(self) -> str:
        ...
    
    @pc_3_file.setter
    def pc_3_file(self, value : str):
        ...
    
    @property
    def render_to_graphics_bound(self) -> bool:
        ...
    
    @render_to_graphics_bound.setter
    def render_to_graphics_bound(self, value : bool):
        ...
    
    @property
    def user_watermark_text(self) -> str:
        ...
    
    @user_watermark_text.setter
    def user_watermark_text(self, value : str):
        ...
    
    @property
    def user_watermark_color(self) -> aspose.cad.Color:
        ...
    
    @user_watermark_color.setter
    def user_watermark_color(self, value : aspose.cad.Color):
        ...
    
    ...

class GraphicsOptions:
    '''Represents graphics options for embedded bitmap.'''
    
    @property
    def text_rendering_hint(self) -> aspose.cad.TextRenderingHint:
        ...
    
    @text_rendering_hint.setter
    def text_rendering_hint(self, value : aspose.cad.TextRenderingHint):
        ...
    
    @property
    def smoothing_mode(self) -> aspose.cad.SmoothingMode:
        ...
    
    @smoothing_mode.setter
    def smoothing_mode(self, value : aspose.cad.SmoothingMode):
        ...
    
    @property
    def interpolation_mode(self) -> aspose.cad.InterpolationMode:
        ...
    
    @interpolation_mode.setter
    def interpolation_mode(self, value : aspose.cad.InterpolationMode):
        ...
    
    ...

class Html5Options(ImageOptionsBase):
    '''HTML5 Canvas image format creation options'''
    
    @property
    def target_format(self) -> aspose.cad.FileFormat:
        ...
    
    @property
    def output_mode(self) -> aspose.cad.imageoptions.CadOutputMode:
        ...
    
    @output_mode.setter
    def output_mode(self, value : aspose.cad.imageoptions.CadOutputMode):
        ...
    
    @property
    def rotation(self) -> aspose.cad.RotateFlipType:
        '''Gets the parameter for rotate, flip, or rotate and flip the image..'''
        ...
    
    @rotation.setter
    def rotation(self, value : aspose.cad.RotateFlipType):
        '''Sets the parameter for rotate, flip, or rotate and flip the image..'''
        ...
    
    @property
    def layers(self) -> List[str]:
        '''Gets a of layer names must be exported.
        All data will be exported without layers if names is not sets.'''
        ...
    
    @layers.setter
    def layers(self, value : List[str]):
        '''Sets a of layer names must be exported.
        All data will be exported without layers if names is not sets.'''
        ...
    
    @property
    def xmp_data(self) -> aspose.cad.XmpPacketWrapper:
        ...
    
    @xmp_data.setter
    def xmp_data(self, value : aspose.cad.XmpPacketWrapper):
        ...
    
    @property
    def source(self) -> aspose.cad.Source:
        '''Gets the source to create image in.'''
        ...
    
    @source.setter
    def source(self, value : aspose.cad.Source):
        '''Sets the source to create image in.'''
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
    def resolution_settings(self) -> aspose.cad.ResolutionSetting:
        ...
    
    @resolution_settings.setter
    def resolution_settings(self, value : aspose.cad.ResolutionSetting):
        ...
    
    @property
    def vector_rasterization_options(self) -> aspose.cad.imageoptions.VectorRasterizationOptions:
        ...
    
    @vector_rasterization_options.setter
    def vector_rasterization_options(self, value : aspose.cad.imageoptions.VectorRasterizationOptions):
        ...
    
    @property
    def timeout(self) -> int:
        '''Timeout value for export operation (in milliseconds)'''
        ...
    
    @timeout.setter
    def timeout(self, value : int):
        '''Timeout value for export operation (in milliseconds)'''
        ...
    
    @property
    def pc_3_file(self) -> str:
        ...
    
    @pc_3_file.setter
    def pc_3_file(self, value : str):
        ...
    
    @property
    def render_to_graphics_bound(self) -> bool:
        ...
    
    @render_to_graphics_bound.setter
    def render_to_graphics_bound(self, value : bool):
        ...
    
    @property
    def user_watermark_text(self) -> str:
        ...
    
    @user_watermark_text.setter
    def user_watermark_text(self, value : str):
        ...
    
    @property
    def user_watermark_color(self) -> aspose.cad.Color:
        ...
    
    @user_watermark_color.setter
    def user_watermark_color(self, value : aspose.cad.Color):
        ...
    
    @property
    def canvas_tag_id(self) -> str:
        ...
    
    @canvas_tag_id.setter
    def canvas_tag_id(self, value : str):
        ...
    
    @property
    def full_html_page(self) -> bool:
        ...
    
    @full_html_page.setter
    def full_html_page(self, value : bool):
        ...
    
    @property
    def encoding(self) -> System.Text.Encoding:
        '''Gets the encoding.'''
        ...
    
    @encoding.setter
    def encoding(self, value : System.Text.Encoding):
        '''Sets the encoding.'''
        ...
    
    ...

class ITextAsLinesOptions:
    '''The TextAsLines options.'''
    
    @property
    def text_as_lines(self) -> bool:
        ...
    
    @text_as_lines.setter
    def text_as_lines(self, value : bool):
        ...
    
    ...

class ITextAsShapesOptions:
    '''The TextAsShapes options.'''
    
    @property
    def text_as_shapes(self) -> bool:
        ...
    
    @text_as_shapes.setter
    def text_as_shapes(self, value : bool):
        ...
    
    ...

class IfcOptions(ImageOptionsBase):
    '''The IFC options.'''
    
    @property
    def target_format(self) -> aspose.cad.FileFormat:
        ...
    
    @property
    def output_mode(self) -> aspose.cad.imageoptions.CadOutputMode:
        ...
    
    @output_mode.setter
    def output_mode(self, value : aspose.cad.imageoptions.CadOutputMode):
        ...
    
    @property
    def rotation(self) -> aspose.cad.RotateFlipType:
        '''Gets the parameter for rotate, flip, or rotate and flip the image..'''
        ...
    
    @rotation.setter
    def rotation(self, value : aspose.cad.RotateFlipType):
        '''Sets the parameter for rotate, flip, or rotate and flip the image..'''
        ...
    
    @property
    def layers(self) -> List[str]:
        '''Gets a of layer names must be exported.
        All data will be exported without layers if names is not sets.'''
        ...
    
    @layers.setter
    def layers(self, value : List[str]):
        '''Sets a of layer names must be exported.
        All data will be exported without layers if names is not sets.'''
        ...
    
    @property
    def xmp_data(self) -> aspose.cad.XmpPacketWrapper:
        ...
    
    @xmp_data.setter
    def xmp_data(self, value : aspose.cad.XmpPacketWrapper):
        ...
    
    @property
    def source(self) -> aspose.cad.Source:
        '''Gets the source to create image in.'''
        ...
    
    @source.setter
    def source(self, value : aspose.cad.Source):
        '''Sets the source to create image in.'''
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
    def resolution_settings(self) -> aspose.cad.ResolutionSetting:
        ...
    
    @resolution_settings.setter
    def resolution_settings(self, value : aspose.cad.ResolutionSetting):
        ...
    
    @property
    def vector_rasterization_options(self) -> aspose.cad.imageoptions.VectorRasterizationOptions:
        ...
    
    @vector_rasterization_options.setter
    def vector_rasterization_options(self, value : aspose.cad.imageoptions.VectorRasterizationOptions):
        ...
    
    @property
    def timeout(self) -> int:
        '''Timeout value for export operation (in milliseconds)'''
        ...
    
    @timeout.setter
    def timeout(self, value : int):
        '''Timeout value for export operation (in milliseconds)'''
        ...
    
    @property
    def pc_3_file(self) -> str:
        ...
    
    @pc_3_file.setter
    def pc_3_file(self, value : str):
        ...
    
    @property
    def render_to_graphics_bound(self) -> bool:
        ...
    
    @render_to_graphics_bound.setter
    def render_to_graphics_bound(self, value : bool):
        ...
    
    @property
    def user_watermark_text(self) -> str:
        ...
    
    @user_watermark_text.setter
    def user_watermark_text(self, value : str):
        ...
    
    @property
    def user_watermark_color(self) -> aspose.cad.Color:
        ...
    
    @user_watermark_color.setter
    def user_watermark_color(self, value : aspose.cad.Color):
        ...
    
    @property
    def version(self) -> aspose.cad.fileformats.ifc.IfcVersion:
        ...
    
    @version.setter
    def version(self, value : aspose.cad.fileformats.ifc.IfcVersion):
        ...
    
    ...

class ImageOptionsBase:
    '''The image base options.'''
    
    @property
    def target_format(self) -> aspose.cad.FileFormat:
        ...
    
    @property
    def output_mode(self) -> aspose.cad.imageoptions.CadOutputMode:
        ...
    
    @output_mode.setter
    def output_mode(self, value : aspose.cad.imageoptions.CadOutputMode):
        ...
    
    @property
    def rotation(self) -> aspose.cad.RotateFlipType:
        '''Gets the parameter for rotate, flip, or rotate and flip the image..'''
        ...
    
    @rotation.setter
    def rotation(self, value : aspose.cad.RotateFlipType):
        '''Sets the parameter for rotate, flip, or rotate and flip the image..'''
        ...
    
    @property
    def layers(self) -> List[str]:
        '''Gets a of layer names must be exported.
        All data will be exported without layers if names is not sets.'''
        ...
    
    @layers.setter
    def layers(self, value : List[str]):
        '''Sets a of layer names must be exported.
        All data will be exported without layers if names is not sets.'''
        ...
    
    @property
    def xmp_data(self) -> aspose.cad.XmpPacketWrapper:
        ...
    
    @xmp_data.setter
    def xmp_data(self, value : aspose.cad.XmpPacketWrapper):
        ...
    
    @property
    def source(self) -> aspose.cad.Source:
        '''Gets the source to create image in.'''
        ...
    
    @source.setter
    def source(self, value : aspose.cad.Source):
        '''Sets the source to create image in.'''
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
    def resolution_settings(self) -> aspose.cad.ResolutionSetting:
        ...
    
    @resolution_settings.setter
    def resolution_settings(self, value : aspose.cad.ResolutionSetting):
        ...
    
    @property
    def vector_rasterization_options(self) -> aspose.cad.imageoptions.VectorRasterizationOptions:
        ...
    
    @vector_rasterization_options.setter
    def vector_rasterization_options(self, value : aspose.cad.imageoptions.VectorRasterizationOptions):
        ...
    
    @property
    def timeout(self) -> int:
        '''Timeout value for export operation (in milliseconds)'''
        ...
    
    @timeout.setter
    def timeout(self, value : int):
        '''Timeout value for export operation (in milliseconds)'''
        ...
    
    @property
    def pc_3_file(self) -> str:
        ...
    
    @pc_3_file.setter
    def pc_3_file(self, value : str):
        ...
    
    @property
    def render_to_graphics_bound(self) -> bool:
        ...
    
    @render_to_graphics_bound.setter
    def render_to_graphics_bound(self, value : bool):
        ...
    
    @property
    def user_watermark_text(self) -> str:
        ...
    
    @user_watermark_text.setter
    def user_watermark_text(self, value : str):
        ...
    
    @property
    def user_watermark_color(self) -> aspose.cad.Color:
        ...
    
    @user_watermark_color.setter
    def user_watermark_color(self, value : aspose.cad.Color):
        ...
    
    ...

class Jpeg2000Options(ImageOptionsBase):
    '''The Jpeg2000 file format options.'''
    
    @property
    def target_format(self) -> aspose.cad.FileFormat:
        ...
    
    @property
    def output_mode(self) -> aspose.cad.imageoptions.CadOutputMode:
        ...
    
    @output_mode.setter
    def output_mode(self, value : aspose.cad.imageoptions.CadOutputMode):
        ...
    
    @property
    def rotation(self) -> aspose.cad.RotateFlipType:
        '''Gets the parameter for rotate, flip, or rotate and flip the image..'''
        ...
    
    @rotation.setter
    def rotation(self, value : aspose.cad.RotateFlipType):
        '''Sets the parameter for rotate, flip, or rotate and flip the image..'''
        ...
    
    @property
    def layers(self) -> List[str]:
        '''Gets a of layer names must be exported.
        All data will be exported without layers if names is not sets.'''
        ...
    
    @layers.setter
    def layers(self, value : List[str]):
        '''Sets a of layer names must be exported.
        All data will be exported without layers if names is not sets.'''
        ...
    
    @property
    def xmp_data(self) -> aspose.cad.XmpPacketWrapper:
        ...
    
    @xmp_data.setter
    def xmp_data(self, value : aspose.cad.XmpPacketWrapper):
        ...
    
    @property
    def source(self) -> aspose.cad.Source:
        '''Gets the source to create image in.'''
        ...
    
    @source.setter
    def source(self, value : aspose.cad.Source):
        '''Sets the source to create image in.'''
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
    def resolution_settings(self) -> aspose.cad.ResolutionSetting:
        ...
    
    @resolution_settings.setter
    def resolution_settings(self, value : aspose.cad.ResolutionSetting):
        ...
    
    @property
    def vector_rasterization_options(self) -> aspose.cad.imageoptions.VectorRasterizationOptions:
        ...
    
    @vector_rasterization_options.setter
    def vector_rasterization_options(self, value : aspose.cad.imageoptions.VectorRasterizationOptions):
        ...
    
    @property
    def timeout(self) -> int:
        '''Timeout value for export operation (in milliseconds)'''
        ...
    
    @timeout.setter
    def timeout(self, value : int):
        '''Timeout value for export operation (in milliseconds)'''
        ...
    
    @property
    def pc_3_file(self) -> str:
        ...
    
    @pc_3_file.setter
    def pc_3_file(self, value : str):
        ...
    
    @property
    def render_to_graphics_bound(self) -> bool:
        ...
    
    @render_to_graphics_bound.setter
    def render_to_graphics_bound(self, value : bool):
        ...
    
    @property
    def user_watermark_text(self) -> str:
        ...
    
    @user_watermark_text.setter
    def user_watermark_text(self, value : str):
        ...
    
    @property
    def user_watermark_color(self) -> aspose.cad.Color:
        ...
    
    @user_watermark_color.setter
    def user_watermark_color(self, value : aspose.cad.Color):
        ...
    
    @property
    def comments(self) -> List[str]:
        '''Gets the Jpeg comment markers.'''
        ...
    
    @comments.setter
    def comments(self, value : List[str]):
        '''Sets the Jpeg comment markers.'''
        ...
    
    @property
    def codec(self) -> aspose.cad.fileformats.jpeg2000.Jpeg2000Codec:
        '''Gets the JPEG2000 codec'''
        ...
    
    @codec.setter
    def codec(self, value : aspose.cad.fileformats.jpeg2000.Jpeg2000Codec):
        '''Sets the JPEG2000 codec'''
        ...
    
    ...

class JpegOptions(ImageOptionsBase):
    '''The jpeg file format create options.'''
    
    @property
    def target_format(self) -> aspose.cad.FileFormat:
        ...
    
    @property
    def output_mode(self) -> aspose.cad.imageoptions.CadOutputMode:
        ...
    
    @output_mode.setter
    def output_mode(self, value : aspose.cad.imageoptions.CadOutputMode):
        ...
    
    @property
    def rotation(self) -> aspose.cad.RotateFlipType:
        '''Gets the parameter for rotate, flip, or rotate and flip the image..'''
        ...
    
    @rotation.setter
    def rotation(self, value : aspose.cad.RotateFlipType):
        '''Sets the parameter for rotate, flip, or rotate and flip the image..'''
        ...
    
    @property
    def layers(self) -> List[str]:
        '''Gets a of layer names must be exported.
        All data will be exported without layers if names is not sets.'''
        ...
    
    @layers.setter
    def layers(self, value : List[str]):
        '''Sets a of layer names must be exported.
        All data will be exported without layers if names is not sets.'''
        ...
    
    @property
    def xmp_data(self) -> aspose.cad.XmpPacketWrapper:
        ...
    
    @xmp_data.setter
    def xmp_data(self, value : aspose.cad.XmpPacketWrapper):
        ...
    
    @property
    def source(self) -> aspose.cad.Source:
        '''Gets the source to create image in.'''
        ...
    
    @source.setter
    def source(self, value : aspose.cad.Source):
        '''Sets the source to create image in.'''
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
    def resolution_settings(self) -> aspose.cad.ResolutionSetting:
        ...
    
    @resolution_settings.setter
    def resolution_settings(self, value : aspose.cad.ResolutionSetting):
        ...
    
    @property
    def vector_rasterization_options(self) -> aspose.cad.imageoptions.VectorRasterizationOptions:
        ...
    
    @vector_rasterization_options.setter
    def vector_rasterization_options(self, value : aspose.cad.imageoptions.VectorRasterizationOptions):
        ...
    
    @property
    def timeout(self) -> int:
        '''Timeout value for export operation (in milliseconds)'''
        ...
    
    @timeout.setter
    def timeout(self, value : int):
        '''Timeout value for export operation (in milliseconds)'''
        ...
    
    @property
    def pc_3_file(self) -> str:
        ...
    
    @pc_3_file.setter
    def pc_3_file(self, value : str):
        ...
    
    @property
    def render_to_graphics_bound(self) -> bool:
        ...
    
    @render_to_graphics_bound.setter
    def render_to_graphics_bound(self, value : bool):
        ...
    
    @property
    def user_watermark_text(self) -> str:
        ...
    
    @user_watermark_text.setter
    def user_watermark_text(self, value : str):
        ...
    
    @property
    def user_watermark_color(self) -> aspose.cad.Color:
        ...
    
    @user_watermark_color.setter
    def user_watermark_color(self, value : aspose.cad.Color):
        ...
    
    @property
    def jfif(self) -> aspose.cad.fileformats.jpeg.JFIFData:
        '''Gets the jfif.'''
        ...
    
    @jfif.setter
    def jfif(self, value : aspose.cad.fileformats.jpeg.JFIFData):
        '''Sets the jfif.'''
        ...
    
    @property
    def comment(self) -> str:
        '''Gets the jpeg file comment.'''
        ...
    
    @comment.setter
    def comment(self, value : str):
        '''Sets the jpeg file comment.'''
        ...
    
    @property
    def exif_data(self) -> aspose.cad.exif.JpegExifData:
        ...
    
    @exif_data.setter
    def exif_data(self, value : aspose.cad.exif.JpegExifData):
        ...
    
    @property
    def compression_type(self) -> aspose.cad.fileformats.jpeg.JpegCompressionMode:
        ...
    
    @compression_type.setter
    def compression_type(self, value : aspose.cad.fileformats.jpeg.JpegCompressionMode):
        ...
    
    @property
    def color_type(self) -> aspose.cad.fileformats.jpeg.JpegCompressionColorMode:
        ...
    
    @color_type.setter
    def color_type(self, value : aspose.cad.fileformats.jpeg.JpegCompressionColorMode):
        ...
    
    @property
    def quality(self) -> int:
        '''Gets image quality.'''
        ...
    
    @quality.setter
    def quality(self, value : int):
        '''Sets image quality.'''
        ...
    
    @property
    def scaled_quality(self) -> int:
        ...
    
    @property
    def rd_opt_settings(self) -> aspose.cad.imageoptions.RdOptimizerSettings:
        ...
    
    @rd_opt_settings.setter
    def rd_opt_settings(self, value : aspose.cad.imageoptions.RdOptimizerSettings):
        ...
    
    @property
    def rgb_color_profile(self) -> aspose.cad.sources.StreamSource:
        ...
    
    @rgb_color_profile.setter
    def rgb_color_profile(self, value : aspose.cad.sources.StreamSource):
        ...
    
    @property
    def cmyk_color_profile(self) -> aspose.cad.sources.StreamSource:
        ...
    
    @cmyk_color_profile.setter
    def cmyk_color_profile(self, value : aspose.cad.sources.StreamSource):
        ...
    
    ...

class Margins:
    '''Margins class.'''
    
    @property
    def left(self) -> int:
        '''Gets left margin.'''
        ...
    
    @left.setter
    def left(self, value : int):
        '''Sets left margin.'''
        ...
    
    @property
    def right(self) -> int:
        '''Gets right margin.'''
        ...
    
    @right.setter
    def right(self, value : int):
        '''Sets right margin.'''
        ...
    
    @property
    def top(self) -> int:
        '''Gets top margin.'''
        ...
    
    @top.setter
    def top(self, value : int):
        '''Sets top margin.'''
        ...
    
    @property
    def bottom(self) -> int:
        '''Gets bottom margin.'''
        ...
    
    @bottom.setter
    def bottom(self, value : int):
        '''Sets bottom margin.'''
        ...
    
    ...

class MultiPageOptions:
    '''Base class for multiple pages supported formats'''
    
    def init_pages(self, ranges : List[aspose.cad.IntRange]) -> None:
        '''Initializes the pages from ranges array
        
        :param ranges: The ranges.'''
        ...
    
    @property
    def pages(self) -> List[int]:
        '''Gets the pages.'''
        ...
    
    @pages.setter
    def pages(self, value : List[int]):
        '''Sets the pages.'''
        ...
    
    @property
    def page_titles(self) -> List[str]:
        ...
    
    @page_titles.setter
    def page_titles(self, value : List[str]):
        ...
    
    @property
    def export_area(self) -> aspose.cad.Rectangle:
        ...
    
    @export_area.setter
    def export_area(self, value : aspose.cad.Rectangle):
        ...
    
    @property
    def mode(self) -> aspose.cad.imageoptions.MultiPageMode:
        '''Gets the mode.'''
        ...
    
    @mode.setter
    def mode(self, value : aspose.cad.imageoptions.MultiPageMode):
        '''Sets the mode.'''
        ...
    
    @property
    def output_layers_names(self) -> List[str]:
        ...
    
    @output_layers_names.setter
    def output_layers_names(self, value : List[str]):
        ...
    
    @property
    def merge_layers(self) -> bool:
        ...
    
    @merge_layers.setter
    def merge_layers(self, value : bool):
        ...
    
    ...

class ObjOptions(ImageOptionsBase):
    '''The OBJ options.'''
    
    @property
    def target_format(self) -> aspose.cad.FileFormat:
        ...
    
    @property
    def output_mode(self) -> aspose.cad.imageoptions.CadOutputMode:
        ...
    
    @output_mode.setter
    def output_mode(self, value : aspose.cad.imageoptions.CadOutputMode):
        ...
    
    @property
    def rotation(self) -> aspose.cad.RotateFlipType:
        '''Gets the parameter for rotate, flip, or rotate and flip the image..'''
        ...
    
    @rotation.setter
    def rotation(self, value : aspose.cad.RotateFlipType):
        '''Sets the parameter for rotate, flip, or rotate and flip the image..'''
        ...
    
    @property
    def layers(self) -> List[str]:
        '''Gets a of layer names must be exported.
        All data will be exported without layers if names is not sets.'''
        ...
    
    @layers.setter
    def layers(self, value : List[str]):
        '''Sets a of layer names must be exported.
        All data will be exported without layers if names is not sets.'''
        ...
    
    @property
    def xmp_data(self) -> aspose.cad.XmpPacketWrapper:
        ...
    
    @xmp_data.setter
    def xmp_data(self, value : aspose.cad.XmpPacketWrapper):
        ...
    
    @property
    def source(self) -> aspose.cad.Source:
        '''Gets the source to create image in.'''
        ...
    
    @source.setter
    def source(self, value : aspose.cad.Source):
        '''Sets the source to create image in.'''
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
    def resolution_settings(self) -> aspose.cad.ResolutionSetting:
        ...
    
    @resolution_settings.setter
    def resolution_settings(self, value : aspose.cad.ResolutionSetting):
        ...
    
    @property
    def vector_rasterization_options(self) -> aspose.cad.imageoptions.VectorRasterizationOptions:
        ...
    
    @vector_rasterization_options.setter
    def vector_rasterization_options(self, value : aspose.cad.imageoptions.VectorRasterizationOptions):
        ...
    
    @property
    def timeout(self) -> int:
        '''Timeout value for export operation (in milliseconds)'''
        ...
    
    @timeout.setter
    def timeout(self, value : int):
        '''Timeout value for export operation (in milliseconds)'''
        ...
    
    @property
    def pc_3_file(self) -> str:
        ...
    
    @pc_3_file.setter
    def pc_3_file(self, value : str):
        ...
    
    @property
    def render_to_graphics_bound(self) -> bool:
        ...
    
    @render_to_graphics_bound.setter
    def render_to_graphics_bound(self, value : bool):
        ...
    
    @property
    def user_watermark_text(self) -> str:
        ...
    
    @user_watermark_text.setter
    def user_watermark_text(self, value : str):
        ...
    
    @property
    def user_watermark_color(self) -> aspose.cad.Color:
        ...
    
    @user_watermark_color.setter
    def user_watermark_color(self, value : aspose.cad.Color):
        ...
    
    @property
    def mtl_file_name(self) -> str:
        ...
    
    @mtl_file_name.setter
    def mtl_file_name(self, value : str):
        ...
    
    @property
    def mtl_file_stream(self) -> io.RawIOBase:
        ...
    
    @mtl_file_stream.setter
    def mtl_file_stream(self, value : io.RawIOBase):
        ...
    
    @property
    def precision(self) -> float:
        '''Gets the precision during faces formation.
        Lower value means more faces and details. Bigger value could lead to missing small parts of the drawing, e.g., small text.'''
        ...
    
    @precision.setter
    def precision(self, value : float):
        '''Sets the precision during faces formation.
        Lower value means more faces and details. Bigger value could lead to missing small parts of the drawing, e.g., small text.'''
        ...
    
    ...

class PdfDigitalSignatureDetailsCore:
    '''Contains details for a PDF digital signature.'''
    
    @property
    def reason(self) -> str:
        '''The reason of signing.'''
        ...
    
    @reason.setter
    def reason(self, value : str):
        '''The reason of signing.'''
        ...
    
    @property
    def location(self) -> str:
        '''Location of signing.'''
        ...
    
    @location.setter
    def location(self, value : str):
        '''Location of signing.'''
        ...
    
    @property
    def signature_date(self) -> DateTime:
        ...
    
    @signature_date.setter
    def signature_date(self, value : DateTime):
        ...
    
    @property
    def hash_algorithm(self) -> aspose.cad.imageoptions.PdfDigitalSignatureHashAlgorithmCore:
        ...
    
    @hash_algorithm.setter
    def hash_algorithm(self, value : aspose.cad.imageoptions.PdfDigitalSignatureHashAlgorithmCore):
        ...
    
    ...

class PdfDocumentOptions:
    '''The PDF options.'''
    
    @property
    def compliance(self) -> aspose.cad.imageoptions.PdfCompliance:
        '''Desired conformance level for generated PDF document.
        Important note: This option should not be changed after PdfDocument object is constructed.
        Default is :py:attr:`aspose.cad.imageoptions.PdfCompliance.PDF15`.'''
        ...
    
    @compliance.setter
    def compliance(self, value : aspose.cad.imageoptions.PdfCompliance):
        '''Desired conformance level for generated PDF document.
        Important note: This option should not be changed after PdfDocument object is constructed.
        Default is :py:attr:`aspose.cad.imageoptions.PdfCompliance.PDF15`.'''
        ...
    
    @property
    def digital_signature_details(self) -> aspose.cad.imageoptions.PdfDigitalSignatureDetailsCore:
        ...
    
    @digital_signature_details.setter
    def digital_signature_details(self, value : aspose.cad.imageoptions.PdfDigitalSignatureDetailsCore):
        ...
    
    ...

class PdfOptions(ImageOptionsBase):
    '''The PDF options.'''
    
    @property
    def target_format(self) -> aspose.cad.FileFormat:
        ...
    
    @property
    def output_mode(self) -> aspose.cad.imageoptions.CadOutputMode:
        ...
    
    @output_mode.setter
    def output_mode(self, value : aspose.cad.imageoptions.CadOutputMode):
        ...
    
    @property
    def rotation(self) -> aspose.cad.RotateFlipType:
        '''Gets the parameter for rotate, flip, or rotate and flip the image..'''
        ...
    
    @rotation.setter
    def rotation(self, value : aspose.cad.RotateFlipType):
        '''Sets the parameter for rotate, flip, or rotate and flip the image..'''
        ...
    
    @property
    def layers(self) -> List[str]:
        '''Gets a of layer names must be exported.
        All data will be exported without layers if names is not sets.'''
        ...
    
    @layers.setter
    def layers(self, value : List[str]):
        '''Sets a of layer names must be exported.
        All data will be exported without layers if names is not sets.'''
        ...
    
    @property
    def xmp_data(self) -> aspose.cad.XmpPacketWrapper:
        ...
    
    @xmp_data.setter
    def xmp_data(self, value : aspose.cad.XmpPacketWrapper):
        ...
    
    @property
    def source(self) -> aspose.cad.Source:
        '''Gets the source to create image in.'''
        ...
    
    @source.setter
    def source(self, value : aspose.cad.Source):
        '''Sets the source to create image in.'''
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
    def resolution_settings(self) -> aspose.cad.ResolutionSetting:
        ...
    
    @resolution_settings.setter
    def resolution_settings(self, value : aspose.cad.ResolutionSetting):
        ...
    
    @property
    def vector_rasterization_options(self) -> aspose.cad.imageoptions.VectorRasterizationOptions:
        ...
    
    @vector_rasterization_options.setter
    def vector_rasterization_options(self, value : aspose.cad.imageoptions.VectorRasterizationOptions):
        ...
    
    @property
    def timeout(self) -> int:
        '''Timeout value for export operation (in milliseconds)'''
        ...
    
    @timeout.setter
    def timeout(self, value : int):
        '''Timeout value for export operation (in milliseconds)'''
        ...
    
    @property
    def pc_3_file(self) -> str:
        ...
    
    @pc_3_file.setter
    def pc_3_file(self, value : str):
        ...
    
    @property
    def render_to_graphics_bound(self) -> bool:
        ...
    
    @render_to_graphics_bound.setter
    def render_to_graphics_bound(self, value : bool):
        ...
    
    @property
    def user_watermark_text(self) -> str:
        ...
    
    @user_watermark_text.setter
    def user_watermark_text(self, value : str):
        ...
    
    @property
    def user_watermark_color(self) -> aspose.cad.Color:
        ...
    
    @user_watermark_color.setter
    def user_watermark_color(self, value : aspose.cad.Color):
        ...
    
    @property
    def pdf_document_info(self) -> aspose.cad.fileformats.pdf.PdfDocumentInfo:
        ...
    
    @pdf_document_info.setter
    def pdf_document_info(self, value : aspose.cad.fileformats.pdf.PdfDocumentInfo):
        ...
    
    @property
    def core_pdf_options(self) -> aspose.cad.imageoptions.PdfDocumentOptions:
        ...
    
    @core_pdf_options.setter
    def core_pdf_options(self, value : aspose.cad.imageoptions.PdfDocumentOptions):
        ...
    
    @property
    def is_3d_content(self) -> bool:
        ...
    
    @is_3d_content.setter
    def is_3d_content(self, value : bool):
        ...
    
    ...

class PenOptions:
    '''Drawing pen options'''
    
    @property
    def start_cap(self) -> aspose.cad.LineCap:
        ...
    
    @start_cap.setter
    def start_cap(self, value : aspose.cad.LineCap):
        ...
    
    @property
    def end_cap(self) -> aspose.cad.LineCap:
        ...
    
    @end_cap.setter
    def end_cap(self, value : aspose.cad.LineCap):
        ...
    
    ...

class PngOptions(ImageOptionsBase):
    '''The png file format create options.'''
    
    @property
    def target_format(self) -> aspose.cad.FileFormat:
        ...
    
    @property
    def output_mode(self) -> aspose.cad.imageoptions.CadOutputMode:
        ...
    
    @output_mode.setter
    def output_mode(self, value : aspose.cad.imageoptions.CadOutputMode):
        ...
    
    @property
    def rotation(self) -> aspose.cad.RotateFlipType:
        '''Gets the parameter for rotate, flip, or rotate and flip the image..'''
        ...
    
    @rotation.setter
    def rotation(self, value : aspose.cad.RotateFlipType):
        '''Sets the parameter for rotate, flip, or rotate and flip the image..'''
        ...
    
    @property
    def layers(self) -> List[str]:
        '''Gets a of layer names must be exported.
        All data will be exported without layers if names is not sets.'''
        ...
    
    @layers.setter
    def layers(self, value : List[str]):
        '''Sets a of layer names must be exported.
        All data will be exported without layers if names is not sets.'''
        ...
    
    @property
    def xmp_data(self) -> aspose.cad.XmpPacketWrapper:
        ...
    
    @xmp_data.setter
    def xmp_data(self, value : aspose.cad.XmpPacketWrapper):
        ...
    
    @property
    def source(self) -> aspose.cad.Source:
        '''Gets the source to create image in.'''
        ...
    
    @source.setter
    def source(self, value : aspose.cad.Source):
        '''Sets the source to create image in.'''
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
    def resolution_settings(self) -> aspose.cad.ResolutionSetting:
        ...
    
    @resolution_settings.setter
    def resolution_settings(self, value : aspose.cad.ResolutionSetting):
        ...
    
    @property
    def vector_rasterization_options(self) -> aspose.cad.imageoptions.VectorRasterizationOptions:
        ...
    
    @vector_rasterization_options.setter
    def vector_rasterization_options(self, value : aspose.cad.imageoptions.VectorRasterizationOptions):
        ...
    
    @property
    def timeout(self) -> int:
        '''Timeout value for export operation (in milliseconds)'''
        ...
    
    @timeout.setter
    def timeout(self, value : int):
        '''Timeout value for export operation (in milliseconds)'''
        ...
    
    @property
    def pc_3_file(self) -> str:
        ...
    
    @pc_3_file.setter
    def pc_3_file(self, value : str):
        ...
    
    @property
    def render_to_graphics_bound(self) -> bool:
        ...
    
    @render_to_graphics_bound.setter
    def render_to_graphics_bound(self, value : bool):
        ...
    
    @property
    def user_watermark_text(self) -> str:
        ...
    
    @user_watermark_text.setter
    def user_watermark_text(self, value : str):
        ...
    
    @property
    def user_watermark_color(self) -> aspose.cad.Color:
        ...
    
    @user_watermark_color.setter
    def user_watermark_color(self, value : aspose.cad.Color):
        ...
    
    @property
    def color_type(self) -> aspose.cad.fileformats.png.PngColorType:
        ...
    
    @color_type.setter
    def color_type(self, value : aspose.cad.fileformats.png.PngColorType):
        ...
    
    @property
    def progressive(self) -> bool:
        '''Gets a value indicating whether this :py:class:`aspose.cad.imageoptions.PngOptions` is progressive.'''
        ...
    
    @progressive.setter
    def progressive(self, value : bool):
        '''Sets a value indicating whether this :py:class:`aspose.cad.imageoptions.PngOptions` is progressive.'''
        ...
    
    @property
    def filter_type(self) -> aspose.cad.fileformats.png.PngFilterType:
        ...
    
    @filter_type.setter
    def filter_type(self, value : aspose.cad.fileformats.png.PngFilterType):
        ...
    
    @property
    def compression_level(self) -> int:
        ...
    
    @compression_level.setter
    def compression_level(self, value : int):
        ...
    
    @property
    def bit_depth(self) -> byte:
        ...
    
    @bit_depth.setter
    def bit_depth(self, value : byte):
        ...
    
    ...

class PsdOptions(ImageOptionsBase):
    '''The psd file format create options.'''
    
    @property
    def target_format(self) -> aspose.cad.FileFormat:
        ...
    
    @property
    def output_mode(self) -> aspose.cad.imageoptions.CadOutputMode:
        ...
    
    @output_mode.setter
    def output_mode(self, value : aspose.cad.imageoptions.CadOutputMode):
        ...
    
    @property
    def rotation(self) -> aspose.cad.RotateFlipType:
        '''Gets the parameter for rotate, flip, or rotate and flip the image..'''
        ...
    
    @rotation.setter
    def rotation(self, value : aspose.cad.RotateFlipType):
        '''Sets the parameter for rotate, flip, or rotate and flip the image..'''
        ...
    
    @property
    def layers(self) -> List[str]:
        '''Gets a of layer names must be exported.
        All data will be exported without layers if names is not sets.'''
        ...
    
    @layers.setter
    def layers(self, value : List[str]):
        '''Sets a of layer names must be exported.
        All data will be exported without layers if names is not sets.'''
        ...
    
    @property
    def xmp_data(self) -> aspose.cad.XmpPacketWrapper:
        ...
    
    @xmp_data.setter
    def xmp_data(self, value : aspose.cad.XmpPacketWrapper):
        ...
    
    @property
    def source(self) -> aspose.cad.Source:
        '''Gets the source to create image in.'''
        ...
    
    @source.setter
    def source(self, value : aspose.cad.Source):
        '''Sets the source to create image in.'''
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
    def resolution_settings(self) -> aspose.cad.ResolutionSetting:
        ...
    
    @resolution_settings.setter
    def resolution_settings(self, value : aspose.cad.ResolutionSetting):
        ...
    
    @property
    def vector_rasterization_options(self) -> aspose.cad.imageoptions.VectorRasterizationOptions:
        ...
    
    @vector_rasterization_options.setter
    def vector_rasterization_options(self, value : aspose.cad.imageoptions.VectorRasterizationOptions):
        ...
    
    @property
    def timeout(self) -> int:
        '''Timeout value for export operation (in milliseconds)'''
        ...
    
    @timeout.setter
    def timeout(self, value : int):
        '''Timeout value for export operation (in milliseconds)'''
        ...
    
    @property
    def pc_3_file(self) -> str:
        ...
    
    @pc_3_file.setter
    def pc_3_file(self, value : str):
        ...
    
    @property
    def render_to_graphics_bound(self) -> bool:
        ...
    
    @render_to_graphics_bound.setter
    def render_to_graphics_bound(self, value : bool):
        ...
    
    @property
    def user_watermark_text(self) -> str:
        ...
    
    @user_watermark_text.setter
    def user_watermark_text(self, value : str):
        ...
    
    @property
    def user_watermark_color(self) -> aspose.cad.Color:
        ...
    
    @user_watermark_color.setter
    def user_watermark_color(self, value : aspose.cad.Color):
        ...
    
    @property
    def version(self) -> int:
        '''Gets the psd file version.'''
        ...
    
    @version.setter
    def version(self, value : int):
        '''Sets the psd file version.'''
        ...
    
    @property
    def compression_method(self) -> aspose.cad.fileformats.psd.CompressionMethod:
        ...
    
    @compression_method.setter
    def compression_method(self, value : aspose.cad.fileformats.psd.CompressionMethod):
        ...
    
    @property
    def color_mode(self) -> aspose.cad.fileformats.psd.ColorModes:
        ...
    
    @color_mode.setter
    def color_mode(self, value : aspose.cad.fileformats.psd.ColorModes):
        ...
    
    @property
    def channel_bits_count(self) -> int:
        ...
    
    @channel_bits_count.setter
    def channel_bits_count(self, value : int):
        ...
    
    @property
    def channels_count(self) -> int:
        ...
    
    @channels_count.setter
    def channels_count(self, value : int):
        ...
    
    ...

class RasterizationQuality:
    '''RasterizationQuality class'''
    
    @property
    def text(self) -> aspose.cad.imageoptions.RasterizationQualityValue:
        '''Gets the text quality.'''
        ...
    
    @text.setter
    def text(self, value : aspose.cad.imageoptions.RasterizationQualityValue):
        '''Sets the text quality.'''
        ...
    
    @property
    def hatch(self) -> aspose.cad.imageoptions.RasterizationQualityValue:
        '''Gets the hatch quality.'''
        ...
    
    @hatch.setter
    def hatch(self, value : aspose.cad.imageoptions.RasterizationQualityValue):
        '''Sets the hatch quality.'''
        ...
    
    @property
    def arc(self) -> aspose.cad.imageoptions.RasterizationQualityValue:
        '''Gets the arc and spline quality.'''
        ...
    
    @arc.setter
    def arc(self, value : aspose.cad.imageoptions.RasterizationQualityValue):
        '''Sets the arc and spline quality.'''
        ...
    
    @property
    def ole(self) -> aspose.cad.imageoptions.RasterizationQualityValue:
        '''Gets the OLE.'''
        ...
    
    @ole.setter
    def ole(self, value : aspose.cad.imageoptions.RasterizationQualityValue):
        '''Sets the OLE.'''
        ...
    
    @property
    def text_thickness_normalization(self) -> bool:
        ...
    
    @text_thickness_normalization.setter
    def text_thickness_normalization(self, value : bool):
        ...
    
    @property
    def objects_precision(self) -> aspose.cad.imageoptions.RasterizationQualityValue:
        ...
    
    @objects_precision.setter
    def objects_precision(self, value : aspose.cad.imageoptions.RasterizationQualityValue):
        ...
    
    ...

class RdOptimizerSettings:
    '''RD optimizer settings class'''
    
    @staticmethod
    def create() -> aspose.cad.imageoptions.RdOptimizerSettings:
        '''Creates this instance.
        
        :returns: returns RDOptimizerSettings class instance'''
        ...
    
    @property
    def bpp_scale(self) -> int:
        ...
    
    @bpp_scale.setter
    def bpp_scale(self, value : int):
        ...
    
    @property
    def bpp_max(self) -> float:
        ...
    
    @bpp_max.setter
    def bpp_max(self, value : float):
        ...
    
    @property
    def max_q(self) -> int:
        ...
    
    @max_q.setter
    def max_q(self, value : int):
        ...
    
    @property
    def min_q(self) -> int:
        ...
    
    @property
    def max_pixel_value(self) -> int:
        ...
    
    @property
    def psnr_max(self) -> int:
        ...
    
    @property
    def discretized_bpp_max(self) -> int:
        ...
    
    ...

class RenderResult:
    '''Represents information with results of rendering'''
    
    @property
    def message(self) -> str:
        '''Gets string message'''
        ...
    
    @message.setter
    def message(self, value : str):
        '''Sets string message'''
        ...
    
    @property
    def render_code(self) -> aspose.cad.imageoptions.RenderErrorCode:
        ...
    
    @render_code.setter
    def render_code(self, value : aspose.cad.imageoptions.RenderErrorCode):
        ...
    
    ...

class StlOptions(ImageOptionsBase):
    '''The STL options.'''
    
    @property
    def target_format(self) -> aspose.cad.FileFormat:
        ...
    
    @property
    def output_mode(self) -> aspose.cad.imageoptions.CadOutputMode:
        ...
    
    @output_mode.setter
    def output_mode(self, value : aspose.cad.imageoptions.CadOutputMode):
        ...
    
    @property
    def rotation(self) -> aspose.cad.RotateFlipType:
        '''Gets the parameter for rotate, flip, or rotate and flip the image..'''
        ...
    
    @rotation.setter
    def rotation(self, value : aspose.cad.RotateFlipType):
        '''Sets the parameter for rotate, flip, or rotate and flip the image..'''
        ...
    
    @property
    def layers(self) -> List[str]:
        '''Gets a of layer names must be exported.
        All data will be exported without layers if names is not sets.'''
        ...
    
    @layers.setter
    def layers(self, value : List[str]):
        '''Sets a of layer names must be exported.
        All data will be exported without layers if names is not sets.'''
        ...
    
    @property
    def xmp_data(self) -> aspose.cad.XmpPacketWrapper:
        ...
    
    @xmp_data.setter
    def xmp_data(self, value : aspose.cad.XmpPacketWrapper):
        ...
    
    @property
    def source(self) -> aspose.cad.Source:
        '''Gets the source to create image in.'''
        ...
    
    @source.setter
    def source(self, value : aspose.cad.Source):
        '''Sets the source to create image in.'''
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
    def resolution_settings(self) -> aspose.cad.ResolutionSetting:
        ...
    
    @resolution_settings.setter
    def resolution_settings(self, value : aspose.cad.ResolutionSetting):
        ...
    
    @property
    def vector_rasterization_options(self) -> aspose.cad.imageoptions.VectorRasterizationOptions:
        ...
    
    @vector_rasterization_options.setter
    def vector_rasterization_options(self, value : aspose.cad.imageoptions.VectorRasterizationOptions):
        ...
    
    @property
    def timeout(self) -> int:
        '''Timeout value for export operation (in milliseconds)'''
        ...
    
    @timeout.setter
    def timeout(self, value : int):
        '''Timeout value for export operation (in milliseconds)'''
        ...
    
    @property
    def pc_3_file(self) -> str:
        ...
    
    @pc_3_file.setter
    def pc_3_file(self, value : str):
        ...
    
    @property
    def render_to_graphics_bound(self) -> bool:
        ...
    
    @render_to_graphics_bound.setter
    def render_to_graphics_bound(self, value : bool):
        ...
    
    @property
    def user_watermark_text(self) -> str:
        ...
    
    @user_watermark_text.setter
    def user_watermark_text(self, value : str):
        ...
    
    @property
    def user_watermark_color(self) -> aspose.cad.Color:
        ...
    
    @user_watermark_color.setter
    def user_watermark_color(self, value : aspose.cad.Color):
        ...
    
    @property
    def pen_width(self) -> float:
        ...
    
    @pen_width.setter
    def pen_width(self, value : float):
        ...
    
    @property
    def cad_file_format(self) -> aspose.cad.fileformats.cad.cadconsts.CadFileFormat:
        ...
    
    @cad_file_format.setter
    def cad_file_format(self, value : aspose.cad.fileformats.cad.cadconsts.CadFileFormat):
        ...
    
    ...

class StpOptions(ImageOptionsBase):
    '''The STP options.'''
    
    @property
    def target_format(self) -> aspose.cad.FileFormat:
        ...
    
    @property
    def output_mode(self) -> aspose.cad.imageoptions.CadOutputMode:
        ...
    
    @output_mode.setter
    def output_mode(self, value : aspose.cad.imageoptions.CadOutputMode):
        ...
    
    @property
    def rotation(self) -> aspose.cad.RotateFlipType:
        '''Gets the parameter for rotate, flip, or rotate and flip the image..'''
        ...
    
    @rotation.setter
    def rotation(self, value : aspose.cad.RotateFlipType):
        '''Sets the parameter for rotate, flip, or rotate and flip the image..'''
        ...
    
    @property
    def layers(self) -> List[str]:
        '''Gets a of layer names must be exported.
        All data will be exported without layers if names is not sets.'''
        ...
    
    @layers.setter
    def layers(self, value : List[str]):
        '''Sets a of layer names must be exported.
        All data will be exported without layers if names is not sets.'''
        ...
    
    @property
    def xmp_data(self) -> aspose.cad.XmpPacketWrapper:
        ...
    
    @xmp_data.setter
    def xmp_data(self, value : aspose.cad.XmpPacketWrapper):
        ...
    
    @property
    def source(self) -> aspose.cad.Source:
        '''Gets the source to create image in.'''
        ...
    
    @source.setter
    def source(self, value : aspose.cad.Source):
        '''Sets the source to create image in.'''
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
    def resolution_settings(self) -> aspose.cad.ResolutionSetting:
        ...
    
    @resolution_settings.setter
    def resolution_settings(self, value : aspose.cad.ResolutionSetting):
        ...
    
    @property
    def vector_rasterization_options(self) -> aspose.cad.imageoptions.VectorRasterizationOptions:
        ...
    
    @vector_rasterization_options.setter
    def vector_rasterization_options(self, value : aspose.cad.imageoptions.VectorRasterizationOptions):
        ...
    
    @property
    def timeout(self) -> int:
        '''Timeout value for export operation (in milliseconds)'''
        ...
    
    @timeout.setter
    def timeout(self, value : int):
        '''Timeout value for export operation (in milliseconds)'''
        ...
    
    @property
    def pc_3_file(self) -> str:
        ...
    
    @pc_3_file.setter
    def pc_3_file(self, value : str):
        ...
    
    @property
    def render_to_graphics_bound(self) -> bool:
        ...
    
    @render_to_graphics_bound.setter
    def render_to_graphics_bound(self, value : bool):
        ...
    
    @property
    def user_watermark_text(self) -> str:
        ...
    
    @user_watermark_text.setter
    def user_watermark_text(self, value : str):
        ...
    
    @property
    def user_watermark_color(self) -> aspose.cad.Color:
        ...
    
    @user_watermark_color.setter
    def user_watermark_color(self, value : aspose.cad.Color):
        ...
    
    ...

class SvgOptions(ImageOptionsBase):
    '''The SVG file format creation options.'''
    
    @property
    def target_format(self) -> aspose.cad.FileFormat:
        ...
    
    @property
    def output_mode(self) -> aspose.cad.imageoptions.CadOutputMode:
        ...
    
    @output_mode.setter
    def output_mode(self, value : aspose.cad.imageoptions.CadOutputMode):
        ...
    
    @property
    def rotation(self) -> aspose.cad.RotateFlipType:
        '''Gets the parameter for rotate, flip, or rotate and flip the image..'''
        ...
    
    @rotation.setter
    def rotation(self, value : aspose.cad.RotateFlipType):
        '''Sets the parameter for rotate, flip, or rotate and flip the image..'''
        ...
    
    @property
    def layers(self) -> List[str]:
        '''Gets a of layer names must be exported.
        All data will be exported without layers if names is not sets.'''
        ...
    
    @layers.setter
    def layers(self, value : List[str]):
        '''Sets a of layer names must be exported.
        All data will be exported without layers if names is not sets.'''
        ...
    
    @property
    def xmp_data(self) -> aspose.cad.XmpPacketWrapper:
        ...
    
    @xmp_data.setter
    def xmp_data(self, value : aspose.cad.XmpPacketWrapper):
        ...
    
    @property
    def source(self) -> aspose.cad.Source:
        '''Gets the source to create image in.'''
        ...
    
    @source.setter
    def source(self, value : aspose.cad.Source):
        '''Sets the source to create image in.'''
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
    def resolution_settings(self) -> aspose.cad.ResolutionSetting:
        ...
    
    @resolution_settings.setter
    def resolution_settings(self, value : aspose.cad.ResolutionSetting):
        ...
    
    @property
    def vector_rasterization_options(self) -> aspose.cad.imageoptions.VectorRasterizationOptions:
        ...
    
    @vector_rasterization_options.setter
    def vector_rasterization_options(self, value : aspose.cad.imageoptions.VectorRasterizationOptions):
        ...
    
    @property
    def timeout(self) -> int:
        '''Timeout value for export operation (in milliseconds)'''
        ...
    
    @timeout.setter
    def timeout(self, value : int):
        '''Timeout value for export operation (in milliseconds)'''
        ...
    
    @property
    def pc_3_file(self) -> str:
        ...
    
    @pc_3_file.setter
    def pc_3_file(self, value : str):
        ...
    
    @property
    def render_to_graphics_bound(self) -> bool:
        ...
    
    @render_to_graphics_bound.setter
    def render_to_graphics_bound(self, value : bool):
        ...
    
    @property
    def user_watermark_text(self) -> str:
        ...
    
    @user_watermark_text.setter
    def user_watermark_text(self, value : str):
        ...
    
    @property
    def user_watermark_color(self) -> aspose.cad.Color:
        ...
    
    @user_watermark_color.setter
    def user_watermark_color(self, value : aspose.cad.Color):
        ...
    
    @property
    def text_as_shapes(self) -> bool:
        ...
    
    @text_as_shapes.setter
    def text_as_shapes(self, value : bool):
        ...
    
    @property
    def callback(self) -> aspose.cad.imageoptions.svgoptionsparameters.ISvgResourceKeeperCallback:
        '''Gets the callback that can be used to store image and font binary data as user needs'''
        ...
    
    @callback.setter
    def callback(self, value : aspose.cad.imageoptions.svgoptionsparameters.ISvgResourceKeeperCallback):
        '''Sets the callback that can be used to store image and font binary data as user needs'''
        ...
    
    @property
    def rescale_subpixel_linewidths(self) -> bool:
        ...
    
    @rescale_subpixel_linewidths.setter
    def rescale_subpixel_linewidths(self, value : bool):
        ...
    
    @property
    def use_absolute_rescaling(self) -> bool:
        ...
    
    @use_absolute_rescaling.setter
    def use_absolute_rescaling(self, value : bool):
        ...
    
    @property
    def minimum_relative_linewidth_ratio(self) -> float:
        ...
    
    @minimum_relative_linewidth_ratio.setter
    def minimum_relative_linewidth_ratio(self, value : float):
        ...
    
    @property
    def minimum_absolute_nonscaled_linewidth(self) -> float:
        ...
    
    @minimum_absolute_nonscaled_linewidth.setter
    def minimum_absolute_nonscaled_linewidth(self, value : float):
        ...
    
    @property
    def minimum_linewidth(self) -> float:
        ...
    
    @minimum_linewidth.setter
    def minimum_linewidth(self, value : float):
        ...
    
    @property
    def omit_declaration(self) -> bool:
        ...
    
    @omit_declaration.setter
    def omit_declaration(self, value : bool):
        ...
    
    ...

class ThreeDSOptions(ImageOptionsBase):
    '''The 3DS options.'''
    
    @property
    def target_format(self) -> aspose.cad.FileFormat:
        ...
    
    @property
    def output_mode(self) -> aspose.cad.imageoptions.CadOutputMode:
        ...
    
    @output_mode.setter
    def output_mode(self, value : aspose.cad.imageoptions.CadOutputMode):
        ...
    
    @property
    def rotation(self) -> aspose.cad.RotateFlipType:
        '''Gets the parameter for rotate, flip, or rotate and flip the image..'''
        ...
    
    @rotation.setter
    def rotation(self, value : aspose.cad.RotateFlipType):
        '''Sets the parameter for rotate, flip, or rotate and flip the image..'''
        ...
    
    @property
    def layers(self) -> List[str]:
        '''Gets a of layer names must be exported.
        All data will be exported without layers if names is not sets.'''
        ...
    
    @layers.setter
    def layers(self, value : List[str]):
        '''Sets a of layer names must be exported.
        All data will be exported without layers if names is not sets.'''
        ...
    
    @property
    def xmp_data(self) -> aspose.cad.XmpPacketWrapper:
        ...
    
    @xmp_data.setter
    def xmp_data(self, value : aspose.cad.XmpPacketWrapper):
        ...
    
    @property
    def source(self) -> aspose.cad.Source:
        '''Gets the source to create image in.'''
        ...
    
    @source.setter
    def source(self, value : aspose.cad.Source):
        '''Sets the source to create image in.'''
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
    def resolution_settings(self) -> aspose.cad.ResolutionSetting:
        ...
    
    @resolution_settings.setter
    def resolution_settings(self, value : aspose.cad.ResolutionSetting):
        ...
    
    @property
    def vector_rasterization_options(self) -> aspose.cad.imageoptions.VectorRasterizationOptions:
        ...
    
    @vector_rasterization_options.setter
    def vector_rasterization_options(self, value : aspose.cad.imageoptions.VectorRasterizationOptions):
        ...
    
    @property
    def timeout(self) -> int:
        '''Timeout value for export operation (in milliseconds)'''
        ...
    
    @timeout.setter
    def timeout(self, value : int):
        '''Timeout value for export operation (in milliseconds)'''
        ...
    
    @property
    def pc_3_file(self) -> str:
        ...
    
    @pc_3_file.setter
    def pc_3_file(self, value : str):
        ...
    
    @property
    def render_to_graphics_bound(self) -> bool:
        ...
    
    @render_to_graphics_bound.setter
    def render_to_graphics_bound(self, value : bool):
        ...
    
    @property
    def user_watermark_text(self) -> str:
        ...
    
    @user_watermark_text.setter
    def user_watermark_text(self, value : str):
        ...
    
    @property
    def user_watermark_color(self) -> aspose.cad.Color:
        ...
    
    @user_watermark_color.setter
    def user_watermark_color(self, value : aspose.cad.Color):
        ...
    
    ...

class TiffOptions(ImageOptionsBase):
    '''The tiff file format options.
    Note that width and height tags will get overwritten on image creation by width and height parameters so there is no need to specify them directly.
    Note that many options return a default value but that does not mean that this option is set explicitly as a tag value. To verify the tag is present use Tags property or the corresponding IsTagPresent method.'''
    
    def is_tag_present(self, tag : aspose.cad.fileformats.tiff.enums.TiffTags) -> bool:
        '''Determines whether tag is present in the options or not.
        
        :param tag: The tag id to check.
        :returns: ``true`` if tag is present; otherwise, ``false``.'''
        ...
    
    @staticmethod
    def get_valid_tags_count(tags : List[aspose.cad.fileformats.tiff.TiffDataType]) -> int:
        '''Gets the valid tags count.
        
        :param tags: The tags to validate.
        :returns: The valid tags count.'''
        ...
    
    def remove_tag(self, tag : aspose.cad.fileformats.tiff.enums.TiffTags) -> bool:
        '''Removes the tag.
        
        :param tag: The tag to remove.
        :returns: true if successfully removed'''
        ...
    
    def validate(self) -> None:
        '''Validates if options have valid combination of tags'''
        ...
    
    def add_tags(self, tags_to_add : List[aspose.cad.fileformats.tiff.TiffDataType]) -> None:
        '''Adds the tags.
        
        :param tags_to_add: The tags to add.'''
        ...
    
    def add_tag(self, tag_to_add : aspose.cad.fileformats.tiff.TiffDataType) -> None:
        '''Adds a new tag.
        
        :param tag_to_add: The tag to add.'''
        ...
    
    def get_tag_by_type(self, tag_key : aspose.cad.fileformats.tiff.enums.TiffTags) -> aspose.cad.fileformats.tiff.TiffDataType:
        '''Gets the instance of the tag by type.
        
        :param tag_key: The tag key.
        :returns: Instance of the tag if exists or null otherwise.'''
        ...
    
    @property
    def target_format(self) -> aspose.cad.FileFormat:
        ...
    
    @property
    def output_mode(self) -> aspose.cad.imageoptions.CadOutputMode:
        ...
    
    @output_mode.setter
    def output_mode(self, value : aspose.cad.imageoptions.CadOutputMode):
        ...
    
    @property
    def rotation(self) -> aspose.cad.RotateFlipType:
        '''Gets the parameter for rotate, flip, or rotate and flip the image..'''
        ...
    
    @rotation.setter
    def rotation(self, value : aspose.cad.RotateFlipType):
        '''Sets the parameter for rotate, flip, or rotate and flip the image..'''
        ...
    
    @property
    def layers(self) -> List[str]:
        '''Gets a of layer names must be exported.
        All data will be exported without layers if names is not sets.'''
        ...
    
    @layers.setter
    def layers(self, value : List[str]):
        '''Sets a of layer names must be exported.
        All data will be exported without layers if names is not sets.'''
        ...
    
    @property
    def xmp_data(self) -> aspose.cad.XmpPacketWrapper:
        ...
    
    @xmp_data.setter
    def xmp_data(self, value : aspose.cad.XmpPacketWrapper):
        ...
    
    @property
    def source(self) -> aspose.cad.Source:
        '''Gets the source to create image in.'''
        ...
    
    @source.setter
    def source(self, value : aspose.cad.Source):
        '''Sets the source to create image in.'''
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
    def resolution_settings(self) -> aspose.cad.ResolutionSetting:
        ...
    
    @resolution_settings.setter
    def resolution_settings(self, value : aspose.cad.ResolutionSetting):
        ...
    
    @property
    def vector_rasterization_options(self) -> aspose.cad.imageoptions.VectorRasterizationOptions:
        ...
    
    @vector_rasterization_options.setter
    def vector_rasterization_options(self, value : aspose.cad.imageoptions.VectorRasterizationOptions):
        ...
    
    @property
    def timeout(self) -> int:
        '''Timeout value for export operation (in milliseconds)'''
        ...
    
    @timeout.setter
    def timeout(self, value : int):
        '''Timeout value for export operation (in milliseconds)'''
        ...
    
    @property
    def pc_3_file(self) -> str:
        ...
    
    @pc_3_file.setter
    def pc_3_file(self, value : str):
        ...
    
    @property
    def render_to_graphics_bound(self) -> bool:
        ...
    
    @render_to_graphics_bound.setter
    def render_to_graphics_bound(self, value : bool):
        ...
    
    @property
    def user_watermark_text(self) -> str:
        ...
    
    @user_watermark_text.setter
    def user_watermark_text(self, value : str):
        ...
    
    @property
    def user_watermark_color(self) -> aspose.cad.Color:
        ...
    
    @user_watermark_color.setter
    def user_watermark_color(self, value : aspose.cad.Color):
        ...
    
    @property
    def is_valid(self) -> bool:
        ...
    
    @property
    def artist(self) -> str:
        '''Gets the artist.'''
        ...
    
    @artist.setter
    def artist(self, value : str):
        '''Sets the artist.'''
        ...
    
    @property
    def byte_order(self) -> aspose.cad.fileformats.tiff.enums.TiffByteOrder:
        ...
    
    @byte_order.setter
    def byte_order(self, value : aspose.cad.fileformats.tiff.enums.TiffByteOrder):
        ...
    
    @property
    def bits_per_sample(self) -> List[int]:
        ...
    
    @bits_per_sample.setter
    def bits_per_sample(self, value : List[int]):
        ...
    
    @property
    def compression(self) -> aspose.cad.fileformats.tiff.enums.TiffCompressions:
        '''Gets the compression.'''
        ...
    
    @compression.setter
    def compression(self, value : aspose.cad.fileformats.tiff.enums.TiffCompressions):
        '''Sets the compression.'''
        ...
    
    @property
    def copyright(self) -> str:
        '''Gets the copyright.'''
        ...
    
    @copyright.setter
    def copyright(self, value : str):
        '''Sets the copyright.'''
        ...
    
    @property
    def color_map(self) -> List[int]:
        ...
    
    @color_map.setter
    def color_map(self, value : List[int]):
        ...
    
    @property
    def date_time(self) -> str:
        ...
    
    @date_time.setter
    def date_time(self, value : str):
        ...
    
    @property
    def document_name(self) -> str:
        ...
    
    @document_name.setter
    def document_name(self, value : str):
        ...
    
    @property
    def alpha_storage(self) -> aspose.cad.fileformats.tiff.enums.TiffAlphaStorage:
        ...
    
    @alpha_storage.setter
    def alpha_storage(self, value : aspose.cad.fileformats.tiff.enums.TiffAlphaStorage):
        ...
    
    @property
    def is_extra_samples_present(self) -> bool:
        ...
    
    @property
    def fill_order(self) -> aspose.cad.fileformats.tiff.enums.TiffFillOrders:
        ...
    
    @fill_order.setter
    def fill_order(self, value : aspose.cad.fileformats.tiff.enums.TiffFillOrders):
        ...
    
    @property
    def half_tone_hints(self) -> List[int]:
        ...
    
    @half_tone_hints.setter
    def half_tone_hints(self, value : List[int]):
        ...
    
    @property
    def image_description(self) -> str:
        ...
    
    @image_description.setter
    def image_description(self, value : str):
        ...
    
    @property
    def ink_names(self) -> str:
        ...
    
    @ink_names.setter
    def ink_names(self, value : str):
        ...
    
    @property
    def scanner_manufacturer(self) -> str:
        ...
    
    @scanner_manufacturer.setter
    def scanner_manufacturer(self, value : str):
        ...
    
    @property
    def max_sample_value(self) -> List[int]:
        ...
    
    @max_sample_value.setter
    def max_sample_value(self, value : List[int]):
        ...
    
    @property
    def min_sample_value(self) -> List[int]:
        ...
    
    @min_sample_value.setter
    def min_sample_value(self, value : List[int]):
        ...
    
    @property
    def scanner_model(self) -> str:
        ...
    
    @scanner_model.setter
    def scanner_model(self, value : str):
        ...
    
    @property
    def orientation(self) -> aspose.cad.fileformats.tiff.enums.TiffOrientations:
        '''Gets the orientation.'''
        ...
    
    @orientation.setter
    def orientation(self, value : aspose.cad.fileformats.tiff.enums.TiffOrientations):
        '''Sets the orientation.'''
        ...
    
    @property
    def page_name(self) -> str:
        ...
    
    @page_name.setter
    def page_name(self, value : str):
        ...
    
    @property
    def page_number(self) -> List[int]:
        ...
    
    @page_number.setter
    def page_number(self, value : List[int]):
        ...
    
    @property
    def photometric(self) -> aspose.cad.fileformats.tiff.enums.TiffPhotometrics:
        '''Gets the photometric.'''
        ...
    
    @photometric.setter
    def photometric(self, value : aspose.cad.fileformats.tiff.enums.TiffPhotometrics):
        '''Sets the photometric.'''
        ...
    
    @property
    def planar_configuration(self) -> aspose.cad.fileformats.tiff.enums.TiffPlanarConfigs:
        ...
    
    @planar_configuration.setter
    def planar_configuration(self, value : aspose.cad.fileformats.tiff.enums.TiffPlanarConfigs):
        ...
    
    @property
    def resolution_unit(self) -> aspose.cad.fileformats.tiff.enums.TiffResolutionUnits:
        ...
    
    @resolution_unit.setter
    def resolution_unit(self, value : aspose.cad.fileformats.tiff.enums.TiffResolutionUnits):
        ...
    
    @property
    def rows_per_strip(self) -> int:
        ...
    
    @rows_per_strip.setter
    def rows_per_strip(self, value : int):
        ...
    
    @property
    def sample_format(self) -> List[aspose.cad.fileformats.tiff.enums.TiffSampleFormats]:
        ...
    
    @sample_format.setter
    def sample_format(self, value : List[aspose.cad.fileformats.tiff.enums.TiffSampleFormats]):
        ...
    
    @property
    def samples_per_pixel(self) -> int:
        ...
    
    @property
    def smax_sample_value(self) -> List[int]:
        ...
    
    @smax_sample_value.setter
    def smax_sample_value(self, value : List[int]):
        ...
    
    @property
    def smin_sample_value(self) -> List[int]:
        ...
    
    @smin_sample_value.setter
    def smin_sample_value(self, value : List[int]):
        ...
    
    @property
    def software_type(self) -> str:
        ...
    
    @software_type.setter
    def software_type(self, value : str):
        ...
    
    @property
    def strip_byte_counts(self) -> List[int]:
        ...
    
    @strip_byte_counts.setter
    def strip_byte_counts(self, value : List[int]):
        ...
    
    @property
    def strip_offsets(self) -> List[int]:
        ...
    
    @strip_offsets.setter
    def strip_offsets(self, value : List[int]):
        ...
    
    @property
    def sub_file_type(self) -> aspose.cad.fileformats.tiff.enums.TiffNewSubFileTypes:
        ...
    
    @sub_file_type.setter
    def sub_file_type(self, value : aspose.cad.fileformats.tiff.enums.TiffNewSubFileTypes):
        ...
    
    @property
    def target_printer(self) -> str:
        ...
    
    @target_printer.setter
    def target_printer(self, value : str):
        ...
    
    @property
    def threshholding(self) -> aspose.cad.fileformats.tiff.enums.TiffThresholds:
        '''Gets the threshholding.'''
        ...
    
    @threshholding.setter
    def threshholding(self, value : aspose.cad.fileformats.tiff.enums.TiffThresholds):
        '''Sets the threshholding.'''
        ...
    
    @property
    def total_pages(self) -> int:
        ...
    
    @property
    def xposition(self) -> aspose.cad.fileformats.tiff.TiffRational:
        '''Gets the x position.'''
        ...
    
    @xposition.setter
    def xposition(self, value : aspose.cad.fileformats.tiff.TiffRational):
        '''Sets the x position.'''
        ...
    
    @property
    def xresolution(self) -> aspose.cad.fileformats.tiff.TiffRational:
        '''Gets the x resolution.'''
        ...
    
    @xresolution.setter
    def xresolution(self, value : aspose.cad.fileformats.tiff.TiffRational):
        '''Sets the x resolution.'''
        ...
    
    @property
    def yposition(self) -> aspose.cad.fileformats.tiff.TiffRational:
        '''Gets the y position.'''
        ...
    
    @yposition.setter
    def yposition(self, value : aspose.cad.fileformats.tiff.TiffRational):
        '''Sets the y position.'''
        ...
    
    @property
    def yresolution(self) -> aspose.cad.fileformats.tiff.TiffRational:
        '''Gets the y resolution.'''
        ...
    
    @yresolution.setter
    def yresolution(self, value : aspose.cad.fileformats.tiff.TiffRational):
        '''Sets the y resolution.'''
        ...
    
    @property
    def fax_t4_options(self) -> aspose.cad.fileformats.tiff.enums.Group3Options:
        ...
    
    @fax_t4_options.setter
    def fax_t4_options(self, value : aspose.cad.fileformats.tiff.enums.Group3Options):
        ...
    
    @property
    def predictor(self) -> aspose.cad.fileformats.tiff.enums.TiffPredictor:
        '''Gets the predictor for LZW compression.'''
        ...
    
    @predictor.setter
    def predictor(self, value : aspose.cad.fileformats.tiff.enums.TiffPredictor):
        '''Sets the predictor for LZW compression.'''
        ...
    
    @property
    def image_length(self) -> int:
        ...
    
    @image_length.setter
    def image_length(self, value : int):
        ...
    
    @property
    def image_width(self) -> int:
        ...
    
    @image_width.setter
    def image_width(self, value : int):
        ...
    
    @property
    def tags(self) -> List[aspose.cad.fileformats.tiff.TiffDataType]:
        '''Gets the tags.'''
        ...
    
    @tags.setter
    def tags(self, value : List[aspose.cad.fileformats.tiff.TiffDataType]):
        '''Sets the tags.'''
        ...
    
    @property
    def valid_tag_count(self) -> int:
        ...
    
    @property
    def bits_per_pixel(self) -> int:
        ...
    
    ...

class U3dOptions(ImageOptionsBase):
    '''The U3D options.'''
    
    @property
    def target_format(self) -> aspose.cad.FileFormat:
        ...
    
    @property
    def output_mode(self) -> aspose.cad.imageoptions.CadOutputMode:
        ...
    
    @output_mode.setter
    def output_mode(self, value : aspose.cad.imageoptions.CadOutputMode):
        ...
    
    @property
    def rotation(self) -> aspose.cad.RotateFlipType:
        '''Gets the parameter for rotate, flip, or rotate and flip the image..'''
        ...
    
    @rotation.setter
    def rotation(self, value : aspose.cad.RotateFlipType):
        '''Sets the parameter for rotate, flip, or rotate and flip the image..'''
        ...
    
    @property
    def layers(self) -> List[str]:
        '''Gets a of layer names must be exported.
        All data will be exported without layers if names is not sets.'''
        ...
    
    @layers.setter
    def layers(self, value : List[str]):
        '''Sets a of layer names must be exported.
        All data will be exported without layers if names is not sets.'''
        ...
    
    @property
    def xmp_data(self) -> aspose.cad.XmpPacketWrapper:
        ...
    
    @xmp_data.setter
    def xmp_data(self, value : aspose.cad.XmpPacketWrapper):
        ...
    
    @property
    def source(self) -> aspose.cad.Source:
        '''Gets the source to create image in.'''
        ...
    
    @source.setter
    def source(self, value : aspose.cad.Source):
        '''Sets the source to create image in.'''
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
    def resolution_settings(self) -> aspose.cad.ResolutionSetting:
        ...
    
    @resolution_settings.setter
    def resolution_settings(self, value : aspose.cad.ResolutionSetting):
        ...
    
    @property
    def vector_rasterization_options(self) -> aspose.cad.imageoptions.VectorRasterizationOptions:
        ...
    
    @vector_rasterization_options.setter
    def vector_rasterization_options(self, value : aspose.cad.imageoptions.VectorRasterizationOptions):
        ...
    
    @property
    def timeout(self) -> int:
        '''Timeout value for export operation (in milliseconds)'''
        ...
    
    @timeout.setter
    def timeout(self, value : int):
        '''Timeout value for export operation (in milliseconds)'''
        ...
    
    @property
    def pc_3_file(self) -> str:
        ...
    
    @pc_3_file.setter
    def pc_3_file(self, value : str):
        ...
    
    @property
    def render_to_graphics_bound(self) -> bool:
        ...
    
    @render_to_graphics_bound.setter
    def render_to_graphics_bound(self, value : bool):
        ...
    
    @property
    def user_watermark_text(self) -> str:
        ...
    
    @user_watermark_text.setter
    def user_watermark_text(self, value : str):
        ...
    
    @property
    def user_watermark_color(self) -> aspose.cad.Color:
        ...
    
    @user_watermark_color.setter
    def user_watermark_color(self, value : aspose.cad.Color):
        ...
    
    ...

class VectorRasterizationOptions:
    '''The vector rasterization options.'''
    
    @property
    def border_x(self) -> float:
        ...
    
    @border_x.setter
    def border_x(self, value : float):
        ...
    
    @property
    def margins(self) -> aspose.cad.imageoptions.Margins:
        '''Gets Margins.'''
        ...
    
    @margins.setter
    def margins(self, value : aspose.cad.imageoptions.Margins):
        '''Sets Margins.'''
        ...
    
    @property
    def border_y(self) -> float:
        ...
    
    @border_y.setter
    def border_y(self, value : float):
        ...
    
    @property
    def page_height(self) -> float:
        ...
    
    @page_height.setter
    def page_height(self, value : float):
        ...
    
    @property
    def page_size(self) -> aspose.cad.SizeF:
        ...
    
    @page_size.setter
    def page_size(self, value : aspose.cad.SizeF):
        ...
    
    @property
    def page_width(self) -> float:
        ...
    
    @page_width.setter
    def page_width(self, value : float):
        ...
    
    @property
    def page_depth(self) -> float:
        ...
    
    @page_depth.setter
    def page_depth(self, value : float):
        ...
    
    @property
    def background_color(self) -> aspose.cad.Color:
        ...
    
    @background_color.setter
    def background_color(self, value : aspose.cad.Color):
        ...
    
    @property
    def embed_background(self) -> bool:
        ...
    
    @embed_background.setter
    def embed_background(self, value : bool):
        ...
    
    @property
    def draw_color(self) -> aspose.cad.Color:
        ...
    
    @draw_color.setter
    def draw_color(self, value : aspose.cad.Color):
        ...
    
    @property
    def unit_type(self) -> aspose.cad.imageoptions.UnitType:
        ...
    
    @unit_type.setter
    def unit_type(self, value : aspose.cad.imageoptions.UnitType):
        ...
    
    @property
    def content_as_bitmap(self) -> bool:
        ...
    
    @content_as_bitmap.setter
    def content_as_bitmap(self, value : bool):
        ...
    
    @property
    def graphics_options(self) -> aspose.cad.imageoptions.GraphicsOptions:
        ...
    
    @graphics_options.setter
    def graphics_options(self, value : aspose.cad.imageoptions.GraphicsOptions):
        ...
    
    @property
    def line_scale(self) -> float:
        ...
    
    @line_scale.setter
    def line_scale(self, value : float):
        ...
    
    @property
    def relative_scale(self) -> float:
        ...
    
    @relative_scale.setter
    def relative_scale(self, value : float):
        ...
    
    @property
    def relative_position(self) -> aspose.cad.PointF:
        ...
    
    @relative_position.setter
    def relative_position(self, value : aspose.cad.PointF):
        ...
    
    ...

class WebPOptions(ImageOptionsBase):
    '''WEBP image options'''
    
    @property
    def target_format(self) -> aspose.cad.FileFormat:
        ...
    
    @property
    def output_mode(self) -> aspose.cad.imageoptions.CadOutputMode:
        ...
    
    @output_mode.setter
    def output_mode(self, value : aspose.cad.imageoptions.CadOutputMode):
        ...
    
    @property
    def rotation(self) -> aspose.cad.RotateFlipType:
        '''Gets the parameter for rotate, flip, or rotate and flip the image..'''
        ...
    
    @rotation.setter
    def rotation(self, value : aspose.cad.RotateFlipType):
        '''Sets the parameter for rotate, flip, or rotate and flip the image..'''
        ...
    
    @property
    def layers(self) -> List[str]:
        '''Gets a of layer names must be exported.
        All data will be exported without layers if names is not sets.'''
        ...
    
    @layers.setter
    def layers(self, value : List[str]):
        '''Sets a of layer names must be exported.
        All data will be exported without layers if names is not sets.'''
        ...
    
    @property
    def xmp_data(self) -> aspose.cad.XmpPacketWrapper:
        ...
    
    @xmp_data.setter
    def xmp_data(self, value : aspose.cad.XmpPacketWrapper):
        ...
    
    @property
    def source(self) -> aspose.cad.Source:
        '''Gets the source to create image in.'''
        ...
    
    @source.setter
    def source(self, value : aspose.cad.Source):
        '''Sets the source to create image in.'''
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
    def resolution_settings(self) -> aspose.cad.ResolutionSetting:
        ...
    
    @resolution_settings.setter
    def resolution_settings(self, value : aspose.cad.ResolutionSetting):
        ...
    
    @property
    def vector_rasterization_options(self) -> aspose.cad.imageoptions.VectorRasterizationOptions:
        ...
    
    @vector_rasterization_options.setter
    def vector_rasterization_options(self, value : aspose.cad.imageoptions.VectorRasterizationOptions):
        ...
    
    @property
    def timeout(self) -> int:
        '''Timeout value for export operation (in milliseconds)'''
        ...
    
    @timeout.setter
    def timeout(self, value : int):
        '''Timeout value for export operation (in milliseconds)'''
        ...
    
    @property
    def pc_3_file(self) -> str:
        ...
    
    @pc_3_file.setter
    def pc_3_file(self, value : str):
        ...
    
    @property
    def render_to_graphics_bound(self) -> bool:
        ...
    
    @render_to_graphics_bound.setter
    def render_to_graphics_bound(self, value : bool):
        ...
    
    @property
    def user_watermark_text(self) -> str:
        ...
    
    @user_watermark_text.setter
    def user_watermark_text(self, value : str):
        ...
    
    @property
    def user_watermark_color(self) -> aspose.cad.Color:
        ...
    
    @user_watermark_color.setter
    def user_watermark_color(self, value : aspose.cad.Color):
        ...
    
    @property
    def lossless(self) -> bool:
        '''Gets a value indicating whether this :py:class:`aspose.cad.imageoptions.WebPOptions` is lossless.'''
        ...
    
    @lossless.setter
    def lossless(self, value : bool):
        '''Sets a value indicating whether this :py:class:`aspose.cad.imageoptions.WebPOptions` is lossless.'''
        ...
    
    @property
    def quality(self) -> float:
        '''Gets the quality.'''
        ...
    
    @quality.setter
    def quality(self, value : float):
        '''Sets the quality.'''
        ...
    
    @property
    def anim_loop_count(self) -> int:
        ...
    
    @anim_loop_count.setter
    def anim_loop_count(self, value : int):
        ...
    
    @property
    def anim_background_color(self) -> int:
        ...
    
    @anim_background_color.setter
    def anim_background_color(self, value : int):
        ...
    
    ...

class WmfOptions(ImageOptionsBase):
    '''The wmf file format creation options.'''
    
    @property
    def target_format(self) -> aspose.cad.FileFormat:
        ...
    
    @property
    def output_mode(self) -> aspose.cad.imageoptions.CadOutputMode:
        ...
    
    @output_mode.setter
    def output_mode(self, value : aspose.cad.imageoptions.CadOutputMode):
        ...
    
    @property
    def rotation(self) -> aspose.cad.RotateFlipType:
        '''Gets the parameter for rotate, flip, or rotate and flip the image..'''
        ...
    
    @rotation.setter
    def rotation(self, value : aspose.cad.RotateFlipType):
        '''Sets the parameter for rotate, flip, or rotate and flip the image..'''
        ...
    
    @property
    def layers(self) -> List[str]:
        '''Gets a of layer names must be exported.
        All data will be exported without layers if names is not sets.'''
        ...
    
    @layers.setter
    def layers(self, value : List[str]):
        '''Sets a of layer names must be exported.
        All data will be exported without layers if names is not sets.'''
        ...
    
    @property
    def xmp_data(self) -> aspose.cad.XmpPacketWrapper:
        ...
    
    @xmp_data.setter
    def xmp_data(self, value : aspose.cad.XmpPacketWrapper):
        ...
    
    @property
    def source(self) -> aspose.cad.Source:
        '''Gets the source to create image in.'''
        ...
    
    @source.setter
    def source(self, value : aspose.cad.Source):
        '''Sets the source to create image in.'''
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
    def resolution_settings(self) -> aspose.cad.ResolutionSetting:
        ...
    
    @resolution_settings.setter
    def resolution_settings(self, value : aspose.cad.ResolutionSetting):
        ...
    
    @property
    def vector_rasterization_options(self) -> aspose.cad.imageoptions.VectorRasterizationOptions:
        ...
    
    @vector_rasterization_options.setter
    def vector_rasterization_options(self, value : aspose.cad.imageoptions.VectorRasterizationOptions):
        ...
    
    @property
    def timeout(self) -> int:
        '''Timeout value for export operation (in milliseconds)'''
        ...
    
    @timeout.setter
    def timeout(self, value : int):
        '''Timeout value for export operation (in milliseconds)'''
        ...
    
    @property
    def pc_3_file(self) -> str:
        ...
    
    @pc_3_file.setter
    def pc_3_file(self, value : str):
        ...
    
    @property
    def render_to_graphics_bound(self) -> bool:
        ...
    
    @render_to_graphics_bound.setter
    def render_to_graphics_bound(self, value : bool):
        ...
    
    @property
    def user_watermark_text(self) -> str:
        ...
    
    @user_watermark_text.setter
    def user_watermark_text(self, value : str):
        ...
    
    @property
    def user_watermark_color(self) -> aspose.cad.Color:
        ...
    
    @user_watermark_color.setter
    def user_watermark_color(self, value : aspose.cad.Color):
        ...
    
    @property
    def bits_per_pixel(self) -> int:
        ...
    
    @bits_per_pixel.setter
    def bits_per_pixel(self, value : int):
        ...
    
    ...

class CadOutputMode:
    
    @classmethod
    @property
    def RENDER(cls) -> CadOutputMode:
        '''Render all the objects to lines and save in specified format'''
        ...
    
    @classmethod
    @property
    def CONVERT(cls) -> CadOutputMode:
        '''Convert image from CAD format to CAD format preserving all the objects as they are'''
        ...
    
    ...

class DxfOutputVersion:
    '''Specifies version of DXF file'''
    
    @classmethod
    @property
    def R12(cls) -> DxfOutputVersion:
        '''R11-R12 DXF version'''
        ...
    
    ...

class MultiPageMode:
    '''Represents multipage mode'''
    
    @classmethod
    @property
    def PAGES(cls) -> MultiPageMode:
        '''Used page indicies'''
        ...
    
    @classmethod
    @property
    def TITLES(cls) -> MultiPageMode:
        '''Used page titles'''
        ...
    
    @classmethod
    @property
    def RANGE(cls) -> MultiPageMode:
        '''Used range of pages'''
        ...
    
    @classmethod
    @property
    def TIME_INTERVAL(cls) -> MultiPageMode:
        '''Used pages in time interval'''
        ...
    
    @classmethod
    @property
    def ALL_PAGES(cls) -> MultiPageMode:
        '''Used all pages'''
        ...
    
    ...

class PdfCompliance:
    '''Specifies the PDF compliance level to output file.'''
    
    @classmethod
    @property
    def PDF15(cls) -> PdfCompliance:
        '''The output file will be PDF 1.5 compliant.'''
        ...
    
    @classmethod
    @property
    def PDF_A1A(cls) -> PdfCompliance:
        '''The output file will be PDF/A-1a compliant.'''
        ...
    
    @classmethod
    @property
    def PDF_A1B(cls) -> PdfCompliance:
        '''The output file will be PDF/A-1b compliant.'''
        ...
    
    ...

class PdfDigitalSignatureHashAlgorithmCore:
    '''Specifies digital hash algorithm used by digital signature.'''
    
    @classmethod
    @property
    def SHA1(cls) -> PdfDigitalSignatureHashAlgorithmCore:
        '''SHA-1 hash algorithm.'''
        ...
    
    @classmethod
    @property
    def SHA256(cls) -> PdfDigitalSignatureHashAlgorithmCore:
        '''SHA-256 hash algorithm.'''
        ...
    
    @classmethod
    @property
    def SHA384(cls) -> PdfDigitalSignatureHashAlgorithmCore:
        '''SHA-384 hash algorithm.'''
        ...
    
    @classmethod
    @property
    def SHA512(cls) -> PdfDigitalSignatureHashAlgorithmCore:
        '''SHA-512 hash algorithm.'''
        ...
    
    @classmethod
    @property
    def MD5(cls) -> PdfDigitalSignatureHashAlgorithmCore:
        '''SHA-1 hash algorithm.'''
        ...
    
    ...

class RasterizationQualityValue:
    '''Copy of RasterizationQualityValue enum for use in Aspose.SVG for
    avoiding of dependency from Aspose.CAD.ImageOptions namespace.'''
    
    @classmethod
    @property
    def LOW(cls) -> RasterizationQualityValue:
        '''The low'''
        ...
    
    @classmethod
    @property
    def MEDIUM(cls) -> RasterizationQualityValue:
        '''The medium'''
        ...
    
    @classmethod
    @property
    def HIGH(cls) -> RasterizationQualityValue:
        '''The high'''
        ...
    
    ...

class RenderErrorCode:
    '''Represents possible missing sections in CAD file'''
    
    @classmethod
    @property
    def MISSING_HEADER(cls) -> RenderErrorCode:
        '''Header is missing'''
        ...
    
    @classmethod
    @property
    def MISSING_LAYOUTS(cls) -> RenderErrorCode:
        '''Layouts information is missing'''
        ...
    
    @classmethod
    @property
    def MISSING_BLOCKS(cls) -> RenderErrorCode:
        '''Block information is missing'''
        ...
    
    @classmethod
    @property
    def MISSING_DIMENSION_STYLES(cls) -> RenderErrorCode:
        '''Dimension styles information is missing'''
        ...
    
    @classmethod
    @property
    def MISSING_STYLES(cls) -> RenderErrorCode:
        '''Styles information is missing'''
        ...
    
    @classmethod
    @property
    def PDF_RENDERER_FAILED(cls) -> RenderErrorCode:
        '''Unable to render drawing parts with PDF'''
        ...
    
    @classmethod
    @property
    def EMBEDDED_IMAGE_FAILED(cls) -> RenderErrorCode:
        '''Unable to export embedded image'''
        ...
    
    @classmethod
    @property
    def MISSING_CLASS(cls) -> RenderErrorCode:
        '''Class is not registered'''
        ...
    
    ...

class RenderMode3D:
    
    @classmethod
    @property
    def SOLID(cls) -> RenderMode3D:
        ...
    
    @classmethod
    @property
    def WIREFRAME(cls) -> RenderMode3D:
        ...
    
    @classmethod
    @property
    def SOLID_WITH_EDGES(cls) -> RenderMode3D:
        ...
    
    ...

class TiffOptionsError:
    '''The tiff options error codes.'''
    
    @classmethod
    @property
    def NO_ERROR(cls) -> TiffOptionsError:
        '''No error code.'''
        ...
    
    @classmethod
    @property
    def NO_COLOR_MAP(cls) -> TiffOptionsError:
        '''The color map is not defined.'''
        ...
    
    @classmethod
    @property
    def COLOR_MAP_LENGTH_INVALID(cls) -> TiffOptionsError:
        '''The color map length is invalid.'''
        ...
    
    @classmethod
    @property
    def COMPRESSION_SPP_MISMATCH(cls) -> TiffOptionsError:
        '''The compression does not match the samples per pixel count.'''
        ...
    
    @classmethod
    @property
    def PHOTOMETRIC_COMPRESSION_MISMATCH(cls) -> TiffOptionsError:
        '''The compression does not match the photometric settings.'''
        ...
    
    @classmethod
    @property
    def PHOTOMETRIC_SPP_MISMATCH(cls) -> TiffOptionsError:
        '''The photometric does not match the samples per pixel count.'''
        ...
    
    @classmethod
    @property
    def NOT_SUPPORTED_ALPHA_STORAGE(cls) -> TiffOptionsError:
        '''The alpha storage is not supported.'''
        ...
    
    @classmethod
    @property
    def PHOTOMETRIC_BITS_PER_SAMPLE_MISMATCH(cls) -> TiffOptionsError:
        '''The photometric bits per sample is invalid'''
        ...
    
    @classmethod
    @property
    def BASELINE_6_OPTIONS_MISMATCH(cls) -> TiffOptionsError:
        '''The specified TIFF options parameters don't conform to TIFF Baseline 6.0 standard'''
        ...
    
    ...

class UnitType:
    '''Represents unit types.'''
    
    @classmethod
    @property
    def KILOMETER(cls) -> UnitType:
        '''Kilometer unit'''
        ...
    
    @classmethod
    @property
    def METER(cls) -> UnitType:
        '''Meter unit'''
        ...
    
    @classmethod
    @property
    def CENTIMENTER(cls) -> UnitType:
        '''Centimeter unit'''
        ...
    
    @classmethod
    @property
    def MILLIMETER(cls) -> UnitType:
        '''Millimeter unit'''
        ...
    
    @classmethod
    @property
    def MICROMETER(cls) -> UnitType:
        '''Micrometer unit, the same as micron'''
        ...
    
    @classmethod
    @property
    def NANOMETER(cls) -> UnitType:
        '''Nanometer unit'''
        ...
    
    @classmethod
    @property
    def ANGSTROM(cls) -> UnitType:
        '''Angstrom unit'''
        ...
    
    @classmethod
    @property
    def DECIMETER(cls) -> UnitType:
        '''Decimeter unit'''
        ...
    
    @classmethod
    @property
    def DECAMETER(cls) -> UnitType:
        '''Decameter unit'''
        ...
    
    @classmethod
    @property
    def HECTOMETER(cls) -> UnitType:
        '''Hectometer unit'''
        ...
    
    @classmethod
    @property
    def GIGAMETER(cls) -> UnitType:
        '''Gigameter unit'''
        ...
    
    @classmethod
    @property
    def ASTRONOMICAL_UNIT(cls) -> UnitType:
        '''Astronomical unit'''
        ...
    
    @classmethod
    @property
    def LIGHT_YEAR(cls) -> UnitType:
        '''Light year unit'''
        ...
    
    @classmethod
    @property
    def PARSEC(cls) -> UnitType:
        '''Parsec unit'''
        ...
    
    @classmethod
    @property
    def MILE(cls) -> UnitType:
        '''Mile unit value.'''
        ...
    
    @classmethod
    @property
    def YARD(cls) -> UnitType:
        '''Yard unit value.'''
        ...
    
    @classmethod
    @property
    def FOOT(cls) -> UnitType:
        '''Foot unit value.'''
        ...
    
    @classmethod
    @property
    def INCH(cls) -> UnitType:
        '''Inch unit value.'''
        ...
    
    @classmethod
    @property
    def MIL(cls) -> UnitType:
        '''Mil unit (thousandth of an inch).'''
        ...
    
    @classmethod
    @property
    def MICRO_INCH(cls) -> UnitType:
        '''MicroInch unit'''
        ...
    
    @classmethod
    @property
    def CUSTOM(cls) -> UnitType:
        '''Custom unit.'''
        ...
    
    @classmethod
    @property
    def UNITLESS(cls) -> UnitType:
        '''Unitless unit.'''
        ...
    
    ...

class VisibilityMode:
    '''Defines entity visibility checking - CAD platforms typically allow separate entity visibilities for print and screen display'''
    
    @classmethod
    @property
    def AS_PRINT(cls) -> VisibilityMode:
        '''Render as printed'''
        ...
    
    @classmethod
    @property
    def AS_SCREEN(cls) -> VisibilityMode:
        '''Render as seen on screen'''
        ...
    
    ...

