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

class ArcSegment:
    '''The arc segment.
    Represents an elliptical arc between two points.'''
    
    @property
    def point(self) -> str:
        '''Gets the point.
        Specifies the endpoint of the elliptical arc.'''
        ...
    
    @point.setter
    def point(self, value : str):
        '''Sets the point.
        Specifies the endpoint of the elliptical arc.'''
        ...
    
    @property
    def size(self) -> str:
        '''Gets the size.
        Specifies the x and y radius of the elliptical arc as an x, y pair.'''
        ...
    
    @size.setter
    def size(self, value : str):
        '''Sets the size.
        Specifies the x and y radius of the elliptical arc as an x, y pair.'''
        ...
    
    @property
    def rotation_angle(self) -> float:
        ...
    
    @rotation_angle.setter
    def rotation_angle(self, value : float):
        ...
    
    @property
    def is_large_arc(self) -> bool:
        ...
    
    @is_large_arc.setter
    def is_large_arc(self, value : bool):
        ...
    
    @property
    def sweep_direction(self) -> aspose.cad.fileformats.dwf.dwfxps.fixedpage.dto.SweepDirection:
        ...
    
    @sweep_direction.setter
    def sweep_direction(self, value : aspose.cad.fileformats.dwf.dwfxps.fixedpage.dto.SweepDirection):
        ...
    
    @property
    def is_stroked(self) -> bool:
        ...
    
    @is_stroked.setter
    def is_stroked(self, value : bool):
        ...
    
    ...

class Brush:
    '''The brush.
    Brushes are used to paint the interior of the geometric shapes defined by a Path element
    and the characters rendered with a Glyphs element.
    They are also used to define the alpha transparency mask in the Canvas.OpacityMask,
    Path.OpacityMask, and Glyphs.OpacityMask property elements.'''
    
    @property
    def item(self) -> any:
        '''Gets the item.
        Solid color brush - Fills a region with a solid color.
        Image brush - Fills a region with an image.
        Visual brush - Fills a region with a drawing.
        Linear gradient brush - Fills a region with a linear gradient.
        Radial gradient brush - Fills a region with a radial gradient.'''
        ...
    
    @item.setter
    def item(self, value : any):
        '''Sets the item.
        Solid color brush - Fills a region with a solid color.
        Image brush - Fills a region with an image.
        Visual brush - Fills a region with a drawing.
        Linear gradient brush - Fills a region with a linear gradient.
        Radial gradient brush - Fills a region with a radial gradient.'''
        ...
    
    ...

class Canvas:
    '''The canvas.
    The Canvas element groups elements together.
    Glyphs and Path elements can be grouped in a canvas in order to be identified as a unit(as a hyperlink destination)
    or to apply a composed property value to each child and ancestor element.'''
    
    @property
    def canvas_resources(self) -> aspose.cad.fileformats.dwf.dwfxps.fixedpage.dto.Resources:
        ...
    
    @canvas_resources.setter
    def canvas_resources(self, value : aspose.cad.fileformats.dwf.dwfxps.fixedpage.dto.Resources):
        ...
    
    @property
    def canvas_render_transform(self) -> aspose.cad.fileformats.dwf.dwfxps.fixedpage.dto.Transform:
        ...
    
    @canvas_render_transform.setter
    def canvas_render_transform(self, value : aspose.cad.fileformats.dwf.dwfxps.fixedpage.dto.Transform):
        ...
    
    @property
    def canvas_clip(self) -> aspose.cad.fileformats.collada.fileparser.elements.Geometry:
        ...
    
    @canvas_clip.setter
    def canvas_clip(self, value : aspose.cad.fileformats.collada.fileparser.elements.Geometry):
        ...
    
    @property
    def canvas_opacity_mask(self) -> aspose.cad.fileformats.dwf.dwfxps.fixedpage.dto.Brush:
        ...
    
    @canvas_opacity_mask.setter
    def canvas_opacity_mask(self, value : aspose.cad.fileformats.dwf.dwfxps.fixedpage.dto.Brush):
        ...
    
    @property
    def items(self) -> List[any]:
        '''Gets the items.
        Grouped together FixedPage descendant elements.'''
        ...
    
    @items.setter
    def items(self, value : List[any]):
        '''Sets the items.
        Grouped together FixedPage descendant elements.'''
        ...
    
    @property
    def render_transform(self) -> str:
        ...
    
    @render_transform.setter
    def render_transform(self, value : str):
        ...
    
    @property
    def clip(self) -> str:
        '''Gets the clip.
        Limits the rendered region of the element.'''
        ...
    
    @clip.setter
    def clip(self, value : str):
        '''Sets the clip.
        Limits the rendered region of the element.'''
        ...
    
    @property
    def opacity(self) -> float:
        '''Gets the opacity.
        Defines the uniform transparency of the canvas.
        Values range from 0 (fully transparent) to 1 (fully opaque), inclusive.
        Values outside of this range are invalid.'''
        ...
    
    @opacity.setter
    def opacity(self, value : float):
        '''Sets the opacity.
        Defines the uniform transparency of the canvas.
        Values range from 0 (fully transparent) to 1 (fully opaque), inclusive.
        Values outside of this range are invalid.'''
        ...
    
    @property
    def opacity_mask(self) -> str:
        ...
    
    @opacity_mask.setter
    def opacity_mask(self, value : str):
        ...
    
    @property
    def name(self) -> str:
        '''Gets the name.
        Contains a string value that identifies the current element as a named,
        addressable point in the document for the purpose of hyperlinking.'''
        ...
    
    @name.setter
    def name(self, value : str):
        '''Sets the name.
        Contains a string value that identifies the current element as a named,
        addressable point in the document for the purpose of hyperlinking.'''
        ...
    
    @property
    def render_options_edge_mode(self) -> aspose.cad.fileformats.dwf.dwfxps.fixedpage.dto.EdgeMode:
        ...
    
    @render_options_edge_mode.setter
    def render_options_edge_mode(self, value : aspose.cad.fileformats.dwf.dwfxps.fixedpage.dto.EdgeMode):
        ...
    
    @property
    def render_options_edge_mode_specified(self) -> bool:
        ...
    
    @render_options_edge_mode_specified.setter
    def render_options_edge_mode_specified(self, value : bool):
        ...
    
    @property
    def fixed_page_navigate_uri(self) -> str:
        ...
    
    @fixed_page_navigate_uri.setter
    def fixed_page_navigate_uri(self, value : str):
        ...
    
    @property
    def language(self) -> str:
        '''Gets the language.
        Specifies the default language used for the current element and for any child or descendant elements.
        The language is specified according to RFC 3066.'''
        ...
    
    @language.setter
    def language(self, value : str):
        '''Sets the language.
        Specifies the default language used for the current element and for any child or descendant elements.
        The language is specified according to RFC 3066.'''
        ...
    
    @property
    def automation_properties_name(self) -> str:
        ...
    
    @automation_properties_name.setter
    def automation_properties_name(self, value : str):
        ...
    
    @property
    def automation_properties_help_text(self) -> str:
        ...
    
    @automation_properties_help_text.setter
    def automation_properties_help_text(self, value : str):
        ...
    
    ...

class FixedPage:
    '''The fixed page.
    The FixedPage element contains the contents of a page and is the root element of a FixedPage part.
    The fixed page contains the elements that together form the basis for all markings rendered on the page: Paths, Glyphs,
    and the optional Canvas grouping element.'''
    
    @property
    def fixed_page_resources(self) -> aspose.cad.fileformats.dwf.dwfxps.fixedpage.dto.Resources:
        ...
    
    @fixed_page_resources.setter
    def fixed_page_resources(self, value : aspose.cad.fileformats.dwf.dwfxps.fixedpage.dto.Resources):
        ...
    
    @property
    def items(self) -> List[any]:
        '''Gets the elements array.
        The fixed page contains the elements that together form the basis for all markings rendered on the page: Paths, Glyphs,
        and the optional Canvas grouping element.'''
        ...
    
    @items.setter
    def items(self, value : List[any]):
        '''Sets the elements array.
        The fixed page contains the elements that together form the basis for all markings rendered on the page: Paths, Glyphs,
        and the optional Canvas grouping element.'''
        ...
    
    @property
    def width(self) -> float:
        '''Gets the width.
        Width of the page, expressed as a real number
        in units of the effective coordinate space.'''
        ...
    
    @width.setter
    def width(self, value : float):
        '''Sets the width.
        Width of the page, expressed as a real number
        in units of the effective coordinate space.'''
        ...
    
    @property
    def height(self) -> float:
        '''Gets the height.
        Height of the page, expressed as a real number
        in units of the effective coordinate space.'''
        ...
    
    @height.setter
    def height(self, value : float):
        '''Sets the height.
        Height of the page, expressed as a real number
        in units of the effective coordinate space.'''
        ...
    
    @property
    def content_box(self) -> str:
        ...
    
    @content_box.setter
    def content_box(self, value : str):
        ...
    
    @property
    def bleed_box(self) -> str:
        ...
    
    @bleed_box.setter
    def bleed_box(self, value : str):
        ...
    
    @property
    def language(self) -> str:
        '''Gets the language.
        Specifies the default language used for the current element and for any child or descendant elements.
        The language is specified according to RFC 3066.'''
        ...
    
    @language.setter
    def language(self, value : str):
        '''Sets the language.
        Specifies the default language used for the current element and for any child or descendant elements.
        The language is specified according to RFC 3066.'''
        ...
    
    @property
    def name(self) -> str:
        '''Gets the name.
        Contains a string value that identifies the current element as a named,
        addressable point in the document for the purpose of hyperlinking.'''
        ...
    
    @name.setter
    def name(self, value : str):
        '''Sets the name.
        Contains a string value that identifies the current element as a named,
        addressable point in the document for the purpose of hyperlinking.'''
        ...
    
    ...

class FixedPageFileParser:
    '''The fixed page file parser.
    Deserializes DTO objects from xml FixedPage file.'''
    
    ...

class Geometry:
    '''The geometry.
    Geometries are used to build visual representations of geometric shapes.
    The smallest atomic unit in a geometry is a segment.
    Segments can be lines or curves.
    One or more segments are combined into a path figure definition.
    A path figure is a single shape comprised of continuous segments.
    One or more path figures collectively define an entire path geometry.
    A path geometry MAY define the fill algorithm to be used on the component path figures.'''
    
    @property
    def path_geometry(self) -> aspose.cad.fileformats.dwf.dwfxps.fixedpage.dto.PathGeometry:
        ...
    
    @path_geometry.setter
    def path_geometry(self, value : aspose.cad.fileformats.dwf.dwfxps.fixedpage.dto.PathGeometry):
        ...
    
    ...

class Glyphs:
    '''The glyphs.
    The Glyphs element represents a run of uniformly-formatted text from a single font.
    It provides information necessary for accurate rendering and supports search
    and selection features in viewing consumers.'''
    
    @property
    def glyphs_render_transform(self) -> aspose.cad.fileformats.dwf.dwfxps.fixedpage.dto.Transform:
        ...
    
    @glyphs_render_transform.setter
    def glyphs_render_transform(self, value : aspose.cad.fileformats.dwf.dwfxps.fixedpage.dto.Transform):
        ...
    
    @property
    def glyphs_clip(self) -> aspose.cad.fileformats.collada.fileparser.elements.Geometry:
        ...
    
    @glyphs_clip.setter
    def glyphs_clip(self, value : aspose.cad.fileformats.collada.fileparser.elements.Geometry):
        ...
    
    @property
    def glyphs_opacity_mask(self) -> aspose.cad.fileformats.dwf.dwfxps.fixedpage.dto.Brush:
        ...
    
    @glyphs_opacity_mask.setter
    def glyphs_opacity_mask(self, value : aspose.cad.fileformats.dwf.dwfxps.fixedpage.dto.Brush):
        ...
    
    @property
    def glyphs_fill(self) -> aspose.cad.fileformats.dwf.dwfxps.fixedpage.dto.Brush:
        ...
    
    @glyphs_fill.setter
    def glyphs_fill(self, value : aspose.cad.fileformats.dwf.dwfxps.fixedpage.dto.Brush):
        ...
    
    @property
    def bidi_level(self) -> str:
        ...
    
    @bidi_level.setter
    def bidi_level(self, value : str):
        ...
    
    @property
    def caret_stops(self) -> str:
        ...
    
    @caret_stops.setter
    def caret_stops(self, value : str):
        ...
    
    @property
    def device_font_name(self) -> str:
        ...
    
    @device_font_name.setter
    def device_font_name(self, value : str):
        ...
    
    @property
    def fill(self) -> str:
        '''Gets the fill.'''
        ...
    
    @fill.setter
    def fill(self, value : str):
        '''Sets the fill.'''
        ...
    
    @property
    def font_rendering_em_size(self) -> float:
        ...
    
    @font_rendering_em_size.setter
    def font_rendering_em_size(self, value : float):
        ...
    
    @property
    def font_uri(self) -> str:
        ...
    
    @font_uri.setter
    def font_uri(self, value : str):
        ...
    
    @property
    def origin_x(self) -> float:
        ...
    
    @origin_x.setter
    def origin_x(self, value : float):
        ...
    
    @property
    def origin_y(self) -> float:
        ...
    
    @origin_y.setter
    def origin_y(self, value : float):
        ...
    
    @property
    def is_sideways(self) -> bool:
        ...
    
    @is_sideways.setter
    def is_sideways(self, value : bool):
        ...
    
    @property
    def indices(self) -> str:
        '''Gets the indices.
        Specifies a series of glyph indices and their attributes used for rendering the glyph run.
        If the UnicodeString attribute of the Glyphs element is not specified
        or contains an empty value (“” or “{ }”), and if the Indices attribute is not specified or  contains no glyph indices,
        then a consumer MUST instantiate an error condition.'''
        ...
    
    @indices.setter
    def indices(self, value : str):
        '''Sets the indices.
        Specifies a series of glyph indices and their attributes used for rendering the glyph run.
        If the UnicodeString attribute of the Glyphs element is not specified
        or contains an empty value (“” or “{ }”), and if the Indices attribute is not specified or  contains no glyph indices,
        then a consumer MUST instantiate an error condition.'''
        ...
    
    @property
    def unicode_string(self) -> str:
        ...
    
    @unicode_string.setter
    def unicode_string(self, value : str):
        ...
    
    @property
    def style_simulations(self) -> aspose.cad.fileformats.dwf.dwfxps.fixedpage.dto.StyleSimulations:
        ...
    
    @style_simulations.setter
    def style_simulations(self, value : aspose.cad.fileformats.dwf.dwfxps.fixedpage.dto.StyleSimulations):
        ...
    
    @property
    def render_transform(self) -> str:
        ...
    
    @render_transform.setter
    def render_transform(self, value : str):
        ...
    
    @property
    def clip(self) -> str:
        '''Gets the clip.
        Limits the rendered region of the element.
        Only portions of the Glyphs element that fall within
        the clip region (even partially clipped characters) produce marks on the page.'''
        ...
    
    @clip.setter
    def clip(self, value : str):
        '''Sets the clip.
        Limits the rendered region of the element.
        Only portions of the Glyphs element that fall within
        the clip region (even partially clipped characters) produce marks on the page.'''
        ...
    
    @property
    def opacity(self) -> float:
        '''Gets the opacity.
        Defines the uniform transparency of the glyph element.
        Values range from 0 (fully transparent) to 1 (fully opaque),
        inclusive.Values outside of this range are invalid.'''
        ...
    
    @opacity.setter
    def opacity(self, value : float):
        '''Sets the opacity.
        Defines the uniform transparency of the glyph element.
        Values range from 0 (fully transparent) to 1 (fully opaque),
        inclusive.Values outside of this range are invalid.'''
        ...
    
    @property
    def opacity_mask(self) -> str:
        ...
    
    @opacity_mask.setter
    def opacity_mask(self, value : str):
        ...
    
    @property
    def name(self) -> str:
        '''Gets the name.
        Contains a string value that identifies the current element as a named,
        addressable point in the document for the purpose of hyperlinking.'''
        ...
    
    @name.setter
    def name(self, value : str):
        '''Sets the name.
        Contains a string value that identifies the current element as a named,
        addressable point in the document for the purpose of hyperlinking.'''
        ...
    
    @property
    def fixed_page_navigate_uri(self) -> str:
        ...
    
    @fixed_page_navigate_uri.setter
    def fixed_page_navigate_uri(self, value : str):
        ...
    
    @property
    def language(self) -> str:
        '''Gets the language.
        Specifies the default language used for the current element and for any child or descendant elements.
        The language is specified according to RFC 3066.'''
        ...
    
    @language.setter
    def language(self, value : str):
        '''Sets the language.
        Specifies the default language used for the current element and for any child or descendant elements.
        The language is specified according to RFC 3066.'''
        ...
    
    ...

class GradientStop:
    '''The gradient stop.
    The GradientStop element is used by both the LinearGradientBrush and RadialGradientBrush elements to define the location
    and range of color progression for rendering a gradient.
    For linear gradient brushes, the offset value of 0.0 is mapped to the start point of the gradient,
    and the offset value of 1.0 is mapped to the end point.
    Intermediate offset values are interpolated between these two points to determine their location.
    For radial gradient brushes, the offset value of 0.0 is mapped to the gradient origin location.
    The offset value of 1.0 is mapped to the circumference of the ellipse as determined by the center,
    x radius, and y radius.Offsets between 0.0 and 1.0 are positioned at a location interpolated between these points.'''
    
    @property
    def color(self) -> str:
        '''Gets the color.
        Specifies the gradient stop color.'''
        ...
    
    @color.setter
    def color(self, value : str):
        '''Sets the color.
        Specifies the gradient stop color.'''
        ...
    
    @property
    def offset(self) -> float:
        '''Gets the offset.
        Specifies the gradient offset.
        The offset indicates a point along the progression of the gradient at which a color is specified.
        Colors between gradient offsets in the progression are interpolated.'''
        ...
    
    @offset.setter
    def offset(self, value : float):
        '''Sets the offset.
        Specifies the gradient offset.
        The offset indicates a point along the progression of the gradient at which a color is specified.
        Colors between gradient offsets in the progression are interpolated.'''
        ...
    
    ...

class ImageBrush:
    '''The image brush.
    The ImageBrush element is used to fill a region with an image.
    The image is defined in a coordinate space specified by the resolution of the image.
    The image MUST refer to a JPEG, PNG, TIFF, or JPEG XR image part within the document package.'''
    
    @property
    def image_brush_transform(self) -> aspose.cad.fileformats.dwf.dwfxps.fixedpage.dto.Transform:
        ...
    
    @image_brush_transform.setter
    def image_brush_transform(self, value : aspose.cad.fileformats.dwf.dwfxps.fixedpage.dto.Transform):
        ...
    
    @property
    def opacity(self) -> float:
        '''Gets the opacity.
        Defines the uniform transparency of the brush fill.
        Values range from 0 (fully transparent) to 1 (fully opaque),
        inclusive.Values outside of this range are invalid.'''
        ...
    
    @opacity.setter
    def opacity(self, value : float):
        '''Sets the opacity.
        Defines the uniform transparency of the brush fill.
        Values range from 0 (fully transparent) to 1 (fully opaque),
        inclusive.Values outside of this range are invalid.'''
        ...
    
    @property
    def transform(self) -> str:
        '''Gets the transform.
        Describes the matrix transformation applied to the coordinate space of the brush.
        The Transform property is concatenated with the current effective render
        transform to yield an effective render transform local to the brush.
        The viewport for the brush is transformed using the local effective render transform.'''
        ...
    
    @transform.setter
    def transform(self, value : str):
        '''Sets the transform.
        Describes the matrix transformation applied to the coordinate space of the brush.
        The Transform property is concatenated with the current effective render
        transform to yield an effective render transform local to the brush.
        The viewport for the brush is transformed using the local effective render transform.'''
        ...
    
    @property
    def viewbox(self) -> str:
        '''Gets the view box.
        Specifies the position and dimensions of the brush's source content.
        Specifies four comma separated real numbers(x, y, width, height),
        where width and height are non-negative.
        The dimensions specified are relative to the image’s physical dimensions expressed in units of 1/96".
        The corners of the view box are mapped to the corners of the viewport,
        thereby providing the default clipping and transform for the brush’s source content.'''
        ...
    
    @viewbox.setter
    def viewbox(self, value : str):
        '''Sets the view box.
        Specifies the position and dimensions of the brush's source content.
        Specifies four comma separated real numbers(x, y, width, height),
        where width and height are non-negative.
        The dimensions specified are relative to the image’s physical dimensions expressed in units of 1/96".
        The corners of the view box are mapped to the corners of the viewport,
        thereby providing the default clipping and transform for the brush’s source content.'''
        ...
    
    @property
    def viewport(self) -> str:
        '''Gets the viewport.
        Specifies the region in the containing coordinate space of
        the prime brush tile that is (possibly repeatedly) applied
        to fill the region to which the brush is applied.
        Specifies four comma-separated real numbers(x, y, width, height),
        where width and height are non-negative.The alignment of
        the brush pattern is controlled by adjusting the x and y values.'''
        ...
    
    @viewport.setter
    def viewport(self, value : str):
        '''Sets the viewport.
        Specifies the region in the containing coordinate space of
        the prime brush tile that is (possibly repeatedly) applied
        to fill the region to which the brush is applied.
        Specifies four comma-separated real numbers(x, y, width, height),
        where width and height are non-negative.The alignment of
        the brush pattern is controlled by adjusting the x and y values.'''
        ...
    
    @property
    def tile_mode(self) -> aspose.cad.fileformats.dwf.dwfxps.fixedpage.dto.TileMode:
        ...
    
    @tile_mode.setter
    def tile_mode(self, value : aspose.cad.fileformats.dwf.dwfxps.fixedpage.dto.TileMode):
        ...
    
    @property
    def viewbox_units(self) -> aspose.cad.fileformats.dwf.dwfxps.fixedpage.dto.ViewUnits:
        ...
    
    @viewbox_units.setter
    def viewbox_units(self, value : aspose.cad.fileformats.dwf.dwfxps.fixedpage.dto.ViewUnits):
        ...
    
    @property
    def viewport_units(self) -> aspose.cad.fileformats.dwf.dwfxps.fixedpage.dto.ViewUnits:
        ...
    
    @viewport_units.setter
    def viewport_units(self, value : aspose.cad.fileformats.dwf.dwfxps.fixedpage.dto.ViewUnits):
        ...
    
    @property
    def image_source(self) -> str:
        ...
    
    @image_source.setter
    def image_source(self, value : str):
        ...
    
    ...

class LinearGradientBrush:
    '''The linear gradient brush.
    The LinearGradientBrush element is used to specify a linear gradient brush along a vector.
    Fills a region with a linear gradient.'''
    
    @property
    def linear_gradient_brush_transform(self) -> aspose.cad.fileformats.dwf.dwfxps.fixedpage.dto.Transform:
        ...
    
    @linear_gradient_brush_transform.setter
    def linear_gradient_brush_transform(self, value : aspose.cad.fileformats.dwf.dwfxps.fixedpage.dto.Transform):
        ...
    
    @property
    def linear_gradient_brush_gradient_stops(self) -> List[aspose.cad.fileformats.dwf.dwfxps.fixedpage.dto.GradientStop]:
        ...
    
    @linear_gradient_brush_gradient_stops.setter
    def linear_gradient_brush_gradient_stops(self, value : List[aspose.cad.fileformats.dwf.dwfxps.fixedpage.dto.GradientStop]):
        ...
    
    @property
    def opacity(self) -> float:
        '''Gets the opacity.
        Defines the uniform transparency of the linear gradient.
        Values range from 0 (fully transparent) to 1 (fully opaque),
        inclusive.Values outside of this range are invalid.'''
        ...
    
    @opacity.setter
    def opacity(self, value : float):
        '''Sets the opacity.
        Defines the uniform transparency of the linear gradient.
        Values range from 0 (fully transparent) to 1 (fully opaque),
        inclusive.Values outside of this range are invalid.'''
        ...
    
    @property
    def color_interpolation_mode(self) -> aspose.cad.fileformats.dwf.dwfxps.fixedpage.dto.ClrIntMode:
        ...
    
    @color_interpolation_mode.setter
    def color_interpolation_mode(self, value : aspose.cad.fileformats.dwf.dwfxps.fixedpage.dto.ClrIntMode):
        ...
    
    @property
    def spread_method(self) -> aspose.cad.fileformats.dwf.dwfxps.fixedpage.dto.SpreadMethod:
        ...
    
    @spread_method.setter
    def spread_method(self, value : aspose.cad.fileformats.dwf.dwfxps.fixedpage.dto.SpreadMethod):
        ...
    
    @property
    def mapping_mode(self) -> aspose.cad.fileformats.dwf.dwfxps.fixedpage.dto.MappingMode:
        ...
    
    @mapping_mode.setter
    def mapping_mode(self, value : aspose.cad.fileformats.dwf.dwfxps.fixedpage.dto.MappingMode):
        ...
    
    @property
    def transform(self) -> str:
        '''Gets the transform.
        Describes the matrix transformation applied to the coordinate space of the brush.
        The Transform property on a brush is concatenated with the current effective
        render transform to yield an effective render transform local to the brush.
        The start point and end point are transformed using the local effective render transform.'''
        ...
    
    @transform.setter
    def transform(self, value : str):
        '''Sets the transform.
        Describes the matrix transformation applied to the coordinate space of the brush.
        The Transform property on a brush is concatenated with the current effective
        render transform to yield an effective render transform local to the brush.
        The start point and end point are transformed using the local effective render transform.'''
        ...
    
    @property
    def start_point(self) -> str:
        ...
    
    @start_point.setter
    def start_point(self, value : str):
        ...
    
    @property
    def end_point(self) -> str:
        ...
    
    @end_point.setter
    def end_point(self, value : str):
        ...
    
    ...

class MatrixTransform:
    '''The matrix transform.
    Creates an arbitrary affine matrix transformation that manipulates objects or coordinate systems in a two dimensional plane.'''
    
    @property
    def matrix(self) -> str:
        '''Gets the matrix.
        Specifies the matrix structure that defines the transformation.'''
        ...
    
    @matrix.setter
    def matrix(self, value : str):
        '''Sets the matrix.
        Specifies the matrix structure that defines the transformation.'''
        ...
    
    ...

class Path:
    '''The path.
    Defines a single graphical effect to be rendered to the page.
    It paints a geometry with a brush and draws a stroke around it.'''
    
    @property
    def path_render_transform(self) -> aspose.cad.fileformats.dwf.dwfxps.fixedpage.dto.Transform:
        ...
    
    @path_render_transform.setter
    def path_render_transform(self, value : aspose.cad.fileformats.dwf.dwfxps.fixedpage.dto.Transform):
        ...
    
    @property
    def path_clip(self) -> aspose.cad.fileformats.collada.fileparser.elements.Geometry:
        ...
    
    @path_clip.setter
    def path_clip(self, value : aspose.cad.fileformats.collada.fileparser.elements.Geometry):
        ...
    
    @property
    def path_opacity_mask(self) -> aspose.cad.fileformats.dwf.dwfxps.fixedpage.dto.Brush:
        ...
    
    @path_opacity_mask.setter
    def path_opacity_mask(self, value : aspose.cad.fileformats.dwf.dwfxps.fixedpage.dto.Brush):
        ...
    
    @property
    def path_fill(self) -> aspose.cad.fileformats.dwf.dwfxps.fixedpage.dto.Brush:
        ...
    
    @path_fill.setter
    def path_fill(self, value : aspose.cad.fileformats.dwf.dwfxps.fixedpage.dto.Brush):
        ...
    
    @property
    def path_stroke(self) -> aspose.cad.fileformats.dwf.dwfxps.fixedpage.dto.Brush:
        ...
    
    @path_stroke.setter
    def path_stroke(self, value : aspose.cad.fileformats.dwf.dwfxps.fixedpage.dto.Brush):
        ...
    
    @property
    def path_data(self) -> aspose.cad.fileformats.collada.fileparser.elements.Geometry:
        ...
    
    @path_data.setter
    def path_data(self, value : aspose.cad.fileformats.collada.fileparser.elements.Geometry):
        ...
    
    @property
    def data(self) -> str:
        '''Gets the data.
        Describes the geometry of the path.'''
        ...
    
    @data.setter
    def data(self, value : str):
        '''Sets the data.
        Describes the geometry of the path.'''
        ...
    
    @property
    def fill(self) -> str:
        '''Gets the fill.
        Describes the brush used to paint the geometry
        specified by the Data property of the path.'''
        ...
    
    @fill.setter
    def fill(self, value : str):
        '''Sets the fill.
        Describes the brush used to paint the geometry
        specified by the Data property of the path.'''
        ...
    
    @property
    def render_transform(self) -> str:
        ...
    
    @render_transform.setter
    def render_transform(self, value : str):
        ...
    
    @property
    def clip(self) -> str:
        '''Gets the clip.
        Limits the rendered region of the element.'''
        ...
    
    @clip.setter
    def clip(self, value : str):
        '''Sets the clip.
        Limits the rendered region of the element.'''
        ...
    
    @property
    def opacity(self) -> float:
        '''Gets the opacity.
        Defines the uniform transparency of the path element.
        Values range from 0 (fully transparent) to 1 (fully opaque),
        inclusive.Values outside of this range are invalid.'''
        ...
    
    @opacity.setter
    def opacity(self, value : float):
        '''Sets the opacity.
        Defines the uniform transparency of the path element.
        Values range from 0 (fully transparent) to 1 (fully opaque),
        inclusive.Values outside of this range are invalid.'''
        ...
    
    @property
    def opacity_mask(self) -> str:
        ...
    
    @opacity_mask.setter
    def opacity_mask(self, value : str):
        ...
    
    @property
    def stroke(self) -> str:
        '''Gets the stroke.
        Specifies the brush used to draw the stroke.'''
        ...
    
    @stroke.setter
    def stroke(self, value : str):
        '''Sets the stroke.
        Specifies the brush used to draw the stroke.'''
        ...
    
    @property
    def stroke_dash_array(self) -> str:
        ...
    
    @stroke_dash_array.setter
    def stroke_dash_array(self, value : str):
        ...
    
    @property
    def stroke_dash_cap(self) -> aspose.cad.fileformats.dwf.dwfxps.fixedpage.dto.DashCap:
        ...
    
    @stroke_dash_cap.setter
    def stroke_dash_cap(self, value : aspose.cad.fileformats.dwf.dwfxps.fixedpage.dto.DashCap):
        ...
    
    @property
    def stroke_dash_offset(self) -> float:
        ...
    
    @stroke_dash_offset.setter
    def stroke_dash_offset(self, value : float):
        ...
    
    @property
    def stroke_end_line_cap(self) -> aspose.cad.LineCap:
        ...
    
    @stroke_end_line_cap.setter
    def stroke_end_line_cap(self, value : aspose.cad.LineCap):
        ...
    
    @property
    def stroke_start_line_cap(self) -> aspose.cad.LineCap:
        ...
    
    @stroke_start_line_cap.setter
    def stroke_start_line_cap(self, value : aspose.cad.LineCap):
        ...
    
    @property
    def stroke_line_join(self) -> aspose.cad.fileformats.cgm.commands.LineJoin:
        ...
    
    @stroke_line_join.setter
    def stroke_line_join(self, value : aspose.cad.fileformats.cgm.commands.LineJoin):
        ...
    
    @property
    def stroke_miter_limit(self) -> float:
        ...
    
    @stroke_miter_limit.setter
    def stroke_miter_limit(self, value : float):
        ...
    
    @property
    def stroke_thickness(self) -> float:
        ...
    
    @stroke_thickness.setter
    def stroke_thickness(self, value : float):
        ...
    
    @property
    def name(self) -> str:
        '''Gets the name.
        Contains a string value that identifies the current element as a named,
        addressable point in the document for the purpose of hyperlinking.'''
        ...
    
    @name.setter
    def name(self, value : str):
        '''Sets the name.
        Contains a string value that identifies the current element as a named,
        addressable point in the document for the purpose of hyperlinking.'''
        ...
    
    @property
    def fixed_page_navigate_uri(self) -> str:
        ...
    
    @fixed_page_navigate_uri.setter
    def fixed_page_navigate_uri(self, value : str):
        ...
    
    @property
    def language(self) -> str:
        '''Gets the language.
        Specifies the default language used for the current element and for any child or descendant elements.
        The language is specified according to RFC 3066.'''
        ...
    
    @language.setter
    def language(self, value : str):
        '''Sets the language.
        Specifies the default language used for the current element and for any child or descendant elements.
        The language is specified according to RFC 3066.'''
        ...
    
    @property
    def automation_properties_name(self) -> str:
        ...
    
    @automation_properties_name.setter
    def automation_properties_name(self, value : str):
        ...
    
    @property
    def automation_properties_help_text(self) -> str:
        ...
    
    @automation_properties_help_text.setter
    def automation_properties_help_text(self, value : str):
        ...
    
    @property
    def snaps_to_device_pixels(self) -> bool:
        ...
    
    @snaps_to_device_pixels.setter
    def snaps_to_device_pixels(self, value : bool):
        ...
    
    @property
    def snaps_to_device_pixels_specified(self) -> bool:
        ...
    
    @snaps_to_device_pixels_specified.setter
    def snaps_to_device_pixels_specified(self, value : bool):
        ...
    
    ...

class PathFigure:
    '''The path figure.
    A PathFigure element is composed of a set of one or more line or curve segments.
    The segment elements define the shape of the path figure.
    The initial point of the first segment element is specified as the StartPoint attribute of the path figure.
    The last point of each segment element is the first point of the following segment element.'''
    
    @property
    def items(self) -> List[any]:
        '''Gets the segment elements.
        Segment elements are:
        • ArcSegment.
        • PolyBezierSegment.
        • PolyLineSegment.
        • PolyQuadraticBezierSegment.'''
        ...
    
    @items.setter
    def items(self, value : List[any]):
        '''Sets the segment elements.
        Segment elements are:
        • ArcSegment.
        • PolyBezierSegment.
        • PolyLineSegment.
        • PolyQuadraticBezierSegment.'''
        ...
    
    @property
    def is_closed(self) -> bool:
        ...
    
    @is_closed.setter
    def is_closed(self, value : bool):
        ...
    
    @property
    def start_point(self) -> str:
        ...
    
    @start_point.setter
    def start_point(self, value : str):
        ...
    
    @property
    def is_filled(self) -> bool:
        ...
    
    @is_filled.setter
    def is_filled(self, value : bool):
        ...
    
    ...

class PathGeometry:
    '''The path geometry.
    A PathGeometry element contains a set of path figures specified either
    with the Figures attribute or with a child PathFigure element.
    Producers MUST NOT specify the path figures of a geometry with both the Figures attribute and a child PathFigure element.'''
    
    @property
    def path_geometry_transform(self) -> aspose.cad.fileformats.dwf.dwfxps.fixedpage.dto.Transform:
        ...
    
    @path_geometry_transform.setter
    def path_geometry_transform(self, value : aspose.cad.fileformats.dwf.dwfxps.fixedpage.dto.Transform):
        ...
    
    @property
    def path_figure(self) -> List[aspose.cad.fileformats.dwf.dwfxps.fixedpage.dto.PathFigure]:
        ...
    
    @path_figure.setter
    def path_figure(self, value : List[aspose.cad.fileformats.dwf.dwfxps.fixedpage.dto.PathFigure]):
        ...
    
    @property
    def figures(self) -> str:
        '''Gets the figures.
        Describes the geometry of the path.'''
        ...
    
    @figures.setter
    def figures(self, value : str):
        '''Sets the figures.
        Describes the geometry of the path.'''
        ...
    
    @property
    def fill_rule(self) -> aspose.cad.fileformats.dwf.dwfxps.fixedpage.dto.FillRule:
        ...
    
    @fill_rule.setter
    def fill_rule(self, value : aspose.cad.fileformats.dwf.dwfxps.fixedpage.dto.FillRule):
        ...
    
    @property
    def transform(self) -> str:
        '''Gets the transform.
        Specifies the local matrix transformation that is applied to
        all child and descendant elements of the path geometry
        before it is used for filling, clipping, or stroking.'''
        ...
    
    @transform.setter
    def transform(self, value : str):
        '''Sets the transform.
        Specifies the local matrix transformation that is applied to
        all child and descendant elements of the path geometry
        before it is used for filling, clipping, or stroking.'''
        ...
    
    ...

class PolyBezierSegment:
    '''The poly bezier segment.
    A series of BÉZIER segments.'''
    
    @property
    def points(self) -> str:
        '''Gets the points.
        Specifies control points for multiple BÉZIER segments.
        Coordinate values within each pair are comma-separated and additional whitespace can appear.
        Coordinate pairs are separated from other coordinate pairs by whitespace.'''
        ...
    
    @points.setter
    def points(self, value : str):
        '''Sets the points.
        Specifies control points for multiple BÉZIER segments.
        Coordinate values within each pair are comma-separated and additional whitespace can appear.
        Coordinate pairs are separated from other coordinate pairs by whitespace.'''
        ...
    
    @property
    def is_stroked(self) -> bool:
        ...
    
    @is_stroked.setter
    def is_stroked(self, value : bool):
        ...
    
    ...

class PolyLineSegment:
    '''The poly line segment.
    Specifies a set of points between which lines are drawn.'''
    
    @property
    def points(self) -> str:
        '''Gets the points.
        Specifies a set of coordinates for the multiple segments that define the
        poly line segment.Coordinate values within each pair are comma-separated
        and additional whitespace can appear.
        Coordinate pairs are separated from other coordinate pairs by whitespace.'''
        ...
    
    @points.setter
    def points(self, value : str):
        '''Sets the points.
        Specifies a set of coordinates for the multiple segments that define the
        poly line segment.Coordinate values within each pair are comma-separated
        and additional whitespace can appear.
        Coordinate pairs are separated from other coordinate pairs by whitespace.'''
        ...
    
    @property
    def is_stroked(self) -> bool:
        ...
    
    @is_stroked.setter
    def is_stroked(self, value : bool):
        ...
    
    ...

class PolyQuadraticBezierSegment:
    '''The poly quadratic bezier segment.
    A series of quadratic BÉZIER segments.'''
    
    @property
    def points(self) -> str:
        '''Gets the points.
        Specifies control points for multiple quadratic BÉZIER segments.
        Coordinate values within each pair are comma-separated and additional whitespace can appear.
        Coordinate pairs are separated from other coordinate pairs by whitespace.'''
        ...
    
    @points.setter
    def points(self, value : str):
        '''Sets the points.
        Specifies control points for multiple quadratic BÉZIER segments.
        Coordinate values within each pair are comma-separated and additional whitespace can appear.
        Coordinate pairs are separated from other coordinate pairs by whitespace.'''
        ...
    
    @property
    def is_stroked(self) -> bool:
        ...
    
    @is_stroked.setter
    def is_stroked(self, value : bool):
        ...
    
    ...

class RadialGradientBrush:
    '''The radial gradient brush.'''
    
    @property
    def radial_gradient_brush_transform(self) -> aspose.cad.fileformats.dwf.dwfxps.fixedpage.dto.Transform:
        ...
    
    @radial_gradient_brush_transform.setter
    def radial_gradient_brush_transform(self, value : aspose.cad.fileformats.dwf.dwfxps.fixedpage.dto.Transform):
        ...
    
    @property
    def radial_gradient_brush_gradient_stops(self) -> List[aspose.cad.fileformats.dwf.dwfxps.fixedpage.dto.GradientStop]:
        ...
    
    @radial_gradient_brush_gradient_stops.setter
    def radial_gradient_brush_gradient_stops(self, value : List[aspose.cad.fileformats.dwf.dwfxps.fixedpage.dto.GradientStop]):
        ...
    
    @property
    def opacity(self) -> float:
        '''Gets the opacity.
        Defines the uniform transparency of the radial gradient.
        Values range from 0 (fully transparent) to 1 (fully opaque), inclusive.
        Values outside of this range are invalid.'''
        ...
    
    @opacity.setter
    def opacity(self, value : float):
        '''Sets the opacity.
        Defines the uniform transparency of the radial gradient.
        Values range from 0 (fully transparent) to 1 (fully opaque), inclusive.
        Values outside of this range are invalid.'''
        ...
    
    @property
    def color_interpolation_mode(self) -> aspose.cad.fileformats.dwf.dwfxps.fixedpage.dto.ClrIntMode:
        ...
    
    @color_interpolation_mode.setter
    def color_interpolation_mode(self, value : aspose.cad.fileformats.dwf.dwfxps.fixedpage.dto.ClrIntMode):
        ...
    
    @property
    def spread_method(self) -> aspose.cad.fileformats.dwf.dwfxps.fixedpage.dto.SpreadMethod:
        ...
    
    @spread_method.setter
    def spread_method(self, value : aspose.cad.fileformats.dwf.dwfxps.fixedpage.dto.SpreadMethod):
        ...
    
    @property
    def mapping_mode(self) -> aspose.cad.fileformats.dwf.dwfxps.fixedpage.dto.MappingMode:
        ...
    
    @mapping_mode.setter
    def mapping_mode(self, value : aspose.cad.fileformats.dwf.dwfxps.fixedpage.dto.MappingMode):
        ...
    
    @property
    def transform(self) -> str:
        '''Gets the transform.
        Describes the matrix transformation applied to the coordinate space of the brush.
        The Transform property is concatenated with the current effective render transform
        to yield an effective render transform local to the brush.
        The ellipse defined by the center, gradient origin, x radius,
        and y radius values is transformed using the local effective render transform.'''
        ...
    
    @transform.setter
    def transform(self, value : str):
        '''Sets the transform.
        Describes the matrix transformation applied to the coordinate space of the brush.
        The Transform property is concatenated with the current effective render transform
        to yield an effective render transform local to the brush.
        The ellipse defined by the center, gradient origin, x radius,
        and y radius values is transformed using the local effective render transform.'''
        ...
    
    @property
    def center(self) -> str:
        '''Gets the center.
        Specifies the center point of the radial gradient(that is, the center of the ellipse).
        The radial gradient brush interpolates the colors from the gradient origin to the circumference of the ellipse.
        The circumference is determined by the center and the radii.'''
        ...
    
    @center.setter
    def center(self, value : str):
        '''Sets the center.
        Specifies the center point of the radial gradient(that is, the center of the ellipse).
        The radial gradient brush interpolates the colors from the gradient origin to the circumference of the ellipse.
        The circumference is determined by the center and the radii.'''
        ...
    
    @property
    def gradient_origin(self) -> str:
        ...
    
    @gradient_origin.setter
    def gradient_origin(self, value : str):
        ...
    
    @property
    def radius_x(self) -> float:
        ...
    
    @radius_x.setter
    def radius_x(self, value : float):
        ...
    
    @property
    def radius_y(self) -> float:
        ...
    
    @radius_y.setter
    def radius_y(self, value : float):
        ...
    
    ...

class ResourceDictionary:
    '''The resource dictionary.
    The FixedPage.Resources and Canvas.Resources property elements contain exactly one ResourceDictionary element.
    A resource dictionary contains resource definition element entries.
    Each resource definition has a key specified in the x:Key attribute that is unique within the scope of the resource dictionary.
    The x:Key attribute is included in the Resource Dictionary.'''
    
    @property
    def items(self) -> List[any]:
        '''Gets the items.
        Defines a set of reusable resource definitions that can be used as property values in the fixed page markup.'''
        ...
    
    @items.setter
    def items(self, value : List[any]):
        '''Sets the items.
        Defines a set of reusable resource definitions that can be used as property values in the fixed page markup.'''
        ...
    
    @property
    def source(self) -> str:
        '''Gets the source.
        Specifies the URI of a part containing markup for a resource dictionary.
        The URI MUST refer to a part in the package'''
        ...
    
    @source.setter
    def source(self, value : str):
        '''Sets the source.
        Specifies the URI of a part containing markup for a resource dictionary.
        The URI MUST refer to a part in the package'''
        ...
    
    ...

class Resources:
    '''The resources.
    The Canvas and FixedPage elements can carry a resource dictionary.
    A resource dictionary is expressed in markup by the FixedPage.Resources or Canvas.Resources property element.
    Individual resource values MUST be specified within a resource dictionary.'''
    
    @property
    def resource_dictionary(self) -> aspose.cad.fileformats.dwf.dwfxps.fixedpage.dto.ResourceDictionary:
        ...
    
    @resource_dictionary.setter
    def resource_dictionary(self, value : aspose.cad.fileformats.dwf.dwfxps.fixedpage.dto.ResourceDictionary):
        ...
    
    ...

class SolidColorBrush:
    '''The solid color brush.
    The SolidColorBrush element is used to fill defined geometric regions with a solid color.
    If there is an alpha component of the color, it is combined in a multiplicative way with the corresponding Opacity attribute.'''
    
    @property
    def opacity(self) -> float:
        '''Gets the opacity.
        Defines the uniform transparency of the brush fill.
        Values range from 0 (fully transparent) to 1 (fully opaque), inclusive.
        Values outside of this range are invalid.'''
        ...
    
    @opacity.setter
    def opacity(self, value : float):
        '''Sets the opacity.
        Defines the uniform transparency of the brush fill.
        Values range from 0 (fully transparent) to 1 (fully opaque), inclusive.
        Values outside of this range are invalid.'''
        ...
    
    @property
    def color(self) -> str:
        '''Gets the color.
        Specifies the color for filled elements.'''
        ...
    
    @color.setter
    def color(self, value : str):
        '''Sets the color.
        Specifies the color for filled elements.'''
        ...
    
    ...

class Transform:
    '''The transform.
    OpenXPS Document markup supports affine transforms as expressed through
    the RenderTransform and Transform properties.An affine transform is represented
    as a list of six real numbers: m11, m12, m21, m22, OffsetX, OffsetY.
    The RenderTransform and Transform properties both specify an affine matrix transformation
    to the local coordinate space, using the MatrixTransform element as their value.
    An abbreviated matrix transformation syntax MAY be used to specify a RenderTransform or Transform attribute value.'''
    
    @property
    def matrix_transform(self) -> aspose.cad.fileformats.dwf.dwfxps.fixedpage.dto.MatrixTransform:
        ...
    
    @matrix_transform.setter
    def matrix_transform(self, value : aspose.cad.fileformats.dwf.dwfxps.fixedpage.dto.MatrixTransform):
        ...
    
    ...

class Visual:
    '''The visual.
    Specifies a Path element, Glyphs element, or Canvas element used to draw the visual contents.'''
    
    @property
    def item(self) -> any:
        '''Gets the element.
        Path element, Glyphs element, or Canvas element.'''
        ...
    
    @item.setter
    def item(self, value : any):
        '''Sets the element.
        Path element, Glyphs element, or Canvas element.'''
        ...
    
    ...

class VisualBrush:
    '''The visual brush.
    The VisualBrush element is used to fill a region with a drawing.
    The drawing can be specified as either a VisualBrush.Visual property element  or as a resource reference.
    Drawing content can include exactly one Canvas, Path, or Glyphs element and that element’s child and descendant elements.'''
    
    @property
    def visual_brush_transform(self) -> aspose.cad.fileformats.dwf.dwfxps.fixedpage.dto.Transform:
        ...
    
    @visual_brush_transform.setter
    def visual_brush_transform(self, value : aspose.cad.fileformats.dwf.dwfxps.fixedpage.dto.Transform):
        ...
    
    @property
    def visual_brush_visual(self) -> aspose.cad.fileformats.dwf.dwfxps.fixedpage.dto.Visual:
        ...
    
    @visual_brush_visual.setter
    def visual_brush_visual(self, value : aspose.cad.fileformats.dwf.dwfxps.fixedpage.dto.Visual):
        ...
    
    @property
    def opacity(self) -> float:
        '''Gets the opacity.
        Defines the uniform transparency of the brush fill.
        Values range from 0 (fully transparent) to 1 (fully opaque),
        inclusive.Values outside of this range are invalid.'''
        ...
    
    @opacity.setter
    def opacity(self, value : float):
        '''Sets the opacity.
        Defines the uniform transparency of the brush fill.
        Values range from 0 (fully transparent) to 1 (fully opaque),
        inclusive.Values outside of this range are invalid.'''
        ...
    
    @property
    def transform(self) -> str:
        '''Gets the transform.
        Describes the matrix transformation applied to the coordinate space of the brush.
        The Transform property is concatenated with the current effective render transform to yield an effective render transform local to the brush.
        The viewport for the brush is transformed using that local effective render transform.'''
        ...
    
    @transform.setter
    def transform(self, value : str):
        '''Sets the transform.
        Describes the matrix transformation applied to the coordinate space of the brush.
        The Transform property is concatenated with the current effective render transform to yield an effective render transform local to the brush.
        The viewport for the brush is transformed using that local effective render transform.'''
        ...
    
    @property
    def viewbox(self) -> str:
        '''Gets the view box.
        Specifies the position and dimensions of the brush's source content.
        Specifies four comma separated real numbers (x, y, Width, Height), where width and height are non-negative.
        The view box defines the default coordinate system for the element specified in the VisualBrush.Visual property element.
        The corners of the view box are mapped to the corners of the viewport, thereby providing the default clipping and transform for the brush’s source content.'''
        ...
    
    @viewbox.setter
    def viewbox(self, value : str):
        '''Sets the view box.
        Specifies the position and dimensions of the brush's source content.
        Specifies four comma separated real numbers (x, y, Width, Height), where width and height are non-negative.
        The view box defines the default coordinate system for the element specified in the VisualBrush.Visual property element.
        The corners of the view box are mapped to the corners of the viewport, thereby providing the default clipping and transform for the brush’s source content.'''
        ...
    
    @property
    def viewport(self) -> str:
        '''Gets the viewport.
        Specifies the region in the containing coordinate space of the prime brush tile that is
        (possibly repeatedly) applied to fill the region to which the brush is applied.
        Specifies four comma-separated real numbers(x, y, Width, Height), where width and height are non-negative.
        The alignment of the brush pattern is controlled by adjusting the x and y values.'''
        ...
    
    @viewport.setter
    def viewport(self, value : str):
        '''Sets the viewport.
        Specifies the region in the containing coordinate space of the prime brush tile that is
        (possibly repeatedly) applied to fill the region to which the brush is applied.
        Specifies four comma-separated real numbers(x, y, Width, Height), where width and height are non-negative.
        The alignment of the brush pattern is controlled by adjusting the x and y values.'''
        ...
    
    @property
    def tile_mode(self) -> aspose.cad.fileformats.dwf.dwfxps.fixedpage.dto.TileMode:
        ...
    
    @tile_mode.setter
    def tile_mode(self, value : aspose.cad.fileformats.dwf.dwfxps.fixedpage.dto.TileMode):
        ...
    
    @property
    def viewbox_units(self) -> aspose.cad.fileformats.dwf.dwfxps.fixedpage.dto.ViewUnits:
        ...
    
    @viewbox_units.setter
    def viewbox_units(self, value : aspose.cad.fileformats.dwf.dwfxps.fixedpage.dto.ViewUnits):
        ...
    
    @property
    def viewport_units(self) -> aspose.cad.fileformats.dwf.dwfxps.fixedpage.dto.ViewUnits:
        ...
    
    @viewport_units.setter
    def viewport_units(self, value : aspose.cad.fileformats.dwf.dwfxps.fixedpage.dto.ViewUnits):
        ...
    
    @property
    def visual(self) -> str:
        '''Gets the visual.
        Specifies resource reference to a Path, Glyphs, or Canvas element defined in a resource dictionary and used to draw the brush’s source content.'''
        ...
    
    @visual.setter
    def visual(self, value : str):
        '''Sets the visual.
        Specifies resource reference to a Path, Glyphs, or Canvas element defined in a resource dictionary and used to draw the brush’s source content.'''
        ...
    
    ...

class ClrIntMode:
    '''The CLR INT mode.
    Specifies the gamma function for color interpolation.
    The gamma adjustment should not be applied to the alpha component, if specified.'''
    
    @classmethod
    @property
    def SC_RGB_LINEAR_INTERPOLATION(cls) -> ClrIntMode:
        '''The SCRGB linear interpolation.'''
        ...
    
    @classmethod
    @property
    def S_RGB_LINEAR_INTERPOLATION(cls) -> ClrIntMode:
        '''The SRGB linear interpolation.'''
        ...
    
    ...

class DashCap:
    '''The dash cap.
    The effective render transform of the path being stroked is used
    to transform the control points of the contour of the dash.'''
    
    @classmethod
    @property
    def FLAT(cls) -> DashCap:
        '''The flat.
        The length of the dash is the approximate distance on the curve
        between the two intersections of the flat lines ending the dash and the contour of the shape.
        The distance from the end of one dash to the start of the next dash is the specified dash gap length.
        Dashes with a length greater than 0 are drawn, and degenerate dashes with a length of 0 are not drawn.'''
        ...
    
    @classmethod
    @property
    def ROUND(cls) -> DashCap:
        '''The round.
        The length of the dash is the approximate distance on the curve between the two contour intersection points,
        that is, the intersection of the flat line ending the dash (without the round caps attached) and the contour of the shape.
        The caps are drawn as half-circles attached to the ends of the dash.
        The boundaries of the round caps are not distorted to follow the contour, but are transformed using the effective render transform.
        The distance between the contour intersection points of consecutive dashes is the specified dash gap length.
        Degenerate dashes with a length of 0 are drawn as circles.'''
        ...
    
    @classmethod
    @property
    def SQUARE(cls) -> DashCap:
        '''The square.
        The length of the dash is the approximate distance on the curve between the two contour intersection points, that is,
        the intersection of the flat line ending the dash (without the square caps attached) and the contour of the shape.
        The caps are drawn as half-squares attached to the ends of the dash.
        The boundaries of the square caps are not curved to follow the contour, but are transformed using the effective render transform.
        The distance between the contour intersection points of consecutive dashes is the specified dash gap length.
        Degenerate dashes with a length of 0 are drawn as squares.
        If a dash with a length of 0 appears at, or very near to, a join in a path then differences in rendering resolution
        and in precision in the calculation of coordinates may lead to differing orientation of the dash caps between consumers.'''
        ...
    
    @classmethod
    @property
    def TRIANGLE(cls) -> DashCap:
        '''The triangle.
        The length of the dash is the approximate distance on the curve between the two contour intersection points,
        that is, the intersection of the flat line ending the dash (without the triangular caps attached) and the contour of the shape.
        The caps are drawn as triangles attached with their base to the ends of the dash.
        The boundaries of the triangular caps are not distorted to follow the contour, but are transformed using the effective render transform.
        The height of the triangles is half of the stroke width.
        The distance between the contour intersection points of consecutive dashes is the specified dash gap length.
        Degenerate dashes with a length of 0 are drawn as diamonds.
        If a dash with a length of 0 appears at, or very near to, a join in a path then differences in rendering resolution
        and in precision in the calculation of coordinates may lead to differing orientation of the dash caps between consumers.'''
        ...
    
    ...

class EdgeMode:
    '''The edge mode.
    The EdgeMode can instruct to render the contents of the element
    and all child and descendant elements without performing anti-aliasing,
    including child brushes and their contents as well as contents included
    via resource dictionary references.'''
    
    @classmethod
    @property
    def ALIASED(cls) -> EdgeMode:
        '''The aliased.'''
        ...
    
    ...

class FillRule:
    '''The fill rule.
    The FillRule attribute specifies a fill algorithm.
    The filling area of a geometry is defined by taking all
    of the contained path figures and applying the fill algorithm to determine the enclosed area.
    Fill algorithms determine how the intersecting areas of geometric shapes are combined to form a region.'''
    
    @classmethod
    @property
    def EVEN_ODD(cls) -> FillRule:
        '''The even odd.
        This rule determines the “INSIDENESS” of a point on the canvas
        by drawing a ray from the point to infinity in any direction and counting
        the number of segments from the given shape that the ray crosses.
        If this number is odd, the point is inside;
        if it is even, the point is outside.
        This is the default rule used throughout document markup.'''
        ...
    
    @classmethod
    @property
    def NON_ZERO(cls) -> FillRule:
        '''The non zero.
        This rule determines the “INSIDENESS” of a point on the canvas
        by drawing a ray from the point to infinity in any direction
        and then examining the places where a segment of the shape crosses the ray.
        Starting with a count of zero, add one each time a segment crosses
        the ray from left to right and subtract one each time a path segment crosses the ray from right to left.
        After counting the crossings, if the result is zero then the point is outside the path; otherwise, it is inside.'''
        ...
    
    ...

class LineCap:
    '''The line cap.
    Specifies the appearance of line caps.'''
    
    @classmethod
    @property
    def FLAT(cls) -> LineCap:
        '''The flat.
        The length of the line is the approximate distance on the curve
        between the two intersections of the flat lines ending the line and the contour of the shape.
        Lines with a length greater than 0 are drawn, and degenerate lines with a length of 0 are not drawn.'''
        ...
    
    @classmethod
    @property
    def ROUND(cls) -> LineCap:
        '''The round.
        The length of the line is the approximate distance on the curve between the two contour intersection points,
        that is, the intersection of the flat line ending the line (without the round caps attached) and the contour of the shape.
        The caps are drawn as half-circles attached to the ends of the line.
        The boundaries of the round caps are not distorted to follow the contour, but are transformed using the effective render transform.
        Degenerate line with a length of 0 are drawn as circles.'''
        ...
    
    @classmethod
    @property
    def SQUARE(cls) -> LineCap:
        '''The square.
        The length of the line is the approximate distance on the curve between the two contour intersection points, that is,
        the intersection of the flat line ending the line (without the square caps attached) and the contour of the shape.
        The caps are drawn as half-squares attached to the ends of the line.
        The boundaries of the square caps are not curved to follow the contour, but are transformed using the effective render transform.
        Degenerate lines with a length of 0 are drawn as squares.
        If a line with a length of 0 appears at, or very near to, a join in a path then differences in rendering resolution
        and in precision in the calculation of coordinates may lead to differing orientation of the line caps between consumers.'''
        ...
    
    @classmethod
    @property
    def TRIANGLE(cls) -> LineCap:
        '''The triangle.
        The length of the Line is the approximate distance on the curve between the two contour intersection points,
        that is, the intersection of the flat line ending the Line (without the triangular caps attached) and the contour of the shape.
        The caps are drawn as triangles attached with their base to the ends of the Line.
        The boundaries of the triangular caps are not distorted to follow the contour, but are transformed using the effective render transform.
        The height of the triangles is half of the stroke width.
        Degenerate Lines with a length of 0 are drawn as diamonds.
        If a line with a length of 0 appears at, or very near to, a join in a path then differences in rendering resolution
        and in precision in the calculation of coordinates may lead to differing orientation of the line caps between consumers.'''
        ...
    
    ...

class LineJoin:
    '''The line join.
    Specifies the appearance of line joins.'''
    
    @classmethod
    @property
    def MITER(cls) -> LineJoin:
        '''The miter.
        Indicates that the region to be filled includes the intersection of the strokes projected to infinity,
        and then clipped at a specific distance. The intersection of the strokes is clipped at
        a line perpendicular to the bisector of the angle between the strokes, at the distance
        equal to the stroke miter limit value multiplied by half the stroke thickness value.'''
        ...
    
    @classmethod
    @property
    def BEVEL(cls) -> LineJoin:
        '''The bevel.
        Indicates that the outer corner of the joined lines should be filled by enclosing
        the triangular region of the corner with a straight line between the outer corners of each stroke.'''
        ...
    
    @classmethod
    @property
    def ROUND(cls) -> LineJoin:
        '''The round.
        Indicates that the outer corner of the joined lines should be filled by enclosing
        the rounded region with its center point at the point of intersection between the
        two lines and a radius of one-half the stroke thickness value.'''
        ...
    
    ...

class MappingMode:
    '''The mapping mode.
    Specifies that center, x radius, and y radius
    are defined in the effective coordinate space
    (includes the Transform attribute of the brush).'''
    
    @classmethod
    @property
    def ABSOLUTE(cls) -> MappingMode:
        '''The absolute.'''
        ...
    
    ...

class SpreadMethod:
    '''The spread method.
    Describes how the brush should fill the content area outside of the primary, initial gradient area.'''
    
    @classmethod
    @property
    def PAD(cls) -> SpreadMethod:
        '''The pad.
        In this method, the first color and the last color are used
        to fill the remaining fill area at the beginning and end.'''
        ...
    
    @classmethod
    @property
    def REFLECT(cls) -> SpreadMethod:
        '''The reflect.
        In this method, the gradient stops are replayed
        in reverse order repeatedly to cover the fill area.'''
        ...
    
    @classmethod
    @property
    def REPEAT(cls) -> SpreadMethod:
        '''The repeat.
        In this method, the gradient stops are repeated
        in order until the fill area is covered.'''
        ...
    
    ...

class StyleSimulations:
    '''The style simulations.
    Synthetic style simulations can be applied to the shape of the glyphs
    by using the StyleSimulations attribute.
    Style simulations can be applied in addition to the designed style of a font.
    The default value for the StyleSimulations attribute is None,
    in which case the shapes of glyphs are not modified from their original design.'''
    
    @classmethod
    @property
    def NONE(cls) -> StyleSimulations:
        '''The none.
        The shapes of glyphs are not modified from their original design.'''
        ...
    
    @classmethod
    @property
    def ITALIC_SIMULATION(cls) -> StyleSimulations:
        '''The italic simulation.
        Synthetic italicizing is applied to glyphs with an IsSideways value of false
        by skewing the top edge of the alignment box of the character by 20° to the right,
        relative to the baseline of the character.'''
        ...
    
    @classmethod
    @property
    def BOLD_SIMULATION(cls) -> StyleSimulations:
        '''The bold simulation.
        Synthetic emboldening is applied by geometrically widening the strokes of glyphs
        by 1% of the EM size for each of the two boundaries of the stroke,
        so that the centers of strokes remain at the same position relative to the character coordinate system.'''
        ...
    
    @classmethod
    @property
    def BOLD_ITALIC_SIMULATION(cls) -> StyleSimulations:
        '''The bold italic simulation.
        Both BoldSimulation and ItalicSimulation are applied.'''
        ...
    
    ...

class SweepDirection:
    '''The sweep direction.
    Determines which of the two possible arcs(selected by the Large Arc Flag) is used.
    Beginning at the starting point, one arc proceeds in the positive(clockwise) direction,
    while the other proceeds in the negative(counter-clockwise) direction.'''
    
    @classmethod
    @property
    def CLOCKWISE(cls) -> SweepDirection:
        '''The clockwise.'''
        ...
    
    @classmethod
    @property
    def COUNTERCLOCKWISE(cls) -> SweepDirection:
        '''The counterclockwise.'''
        ...
    
    ...

class TileMode:
    '''The tile mode.
    Specifies how tiling is performed in the filled geometry.'''
    
    @classmethod
    @property
    def NONE(cls) -> TileMode:
        '''The none.
        In this mode, only the single base tile is drawn.
        The remaining area is left transparent.'''
        ...
    
    @classmethod
    @property
    def TILE(cls) -> TileMode:
        '''The tile.
        In this mode, the base tile is drawn and the remaining area
        is filled by repeating the base tile such that the right edge
        of each tile abuts the left edge of the next, and the bottom
        edge of each tile abuts the top edge of the next.'''
        ...
    
    @classmethod
    @property
    def FLIP_X(cls) -> TileMode:
        '''The flip x.
        In this mode, the tile arrangement is similar to the Tile tile mode,
        but alternate columns of tiles are flipped horizontally.
        The base tile is positioned as specified by the viewport.
        Tiles in the columns to the left and right of this tile are flipped horizontally.'''
        ...
    
    @classmethod
    @property
    def FLIP_Y(cls) -> TileMode:
        '''The flip y.
        In this mode, the tile arrangement is similar to the Tile tile mode,
        but alternate rows of tiles are flipped vertically.
        The base tile is positioned as specified by the viewport.
        Rows above and below are flipped vertically.'''
        ...
    
    @classmethod
    @property
    def FLIP_XY(cls) -> TileMode:
        '''The flip xy.
        In this mode, the tile arrangement is similar to the Tile tile mode,
        but alternate columns of tiles are flipped horizontally and alternate
        rows of tiles are flipped vertically.
        The base tile is positioned as specified by the viewport.'''
        ...
    
    ...

class ViewUnits:
    '''The view units.
    Specifies the relationship of the view coordinates to the containing coordinate space.'''
    
    @classmethod
    @property
    def ABSOLUTE(cls) -> ViewUnits:
        '''The absolute.'''
        ...
    
    ...

