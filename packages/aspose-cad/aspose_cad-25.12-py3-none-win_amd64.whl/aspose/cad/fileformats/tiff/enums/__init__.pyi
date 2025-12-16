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

class Group3Options:
    '''Options for CCITT Group 3/4 fax encoding.
    
    Possible values for GROUP3OPTIONS / TiffTag.T4OPTIONS and
    TiffTag.GROUP4OPTIONS / TiffTag.T6OPTIONS tags.'''
    
    @classmethod
    @property
    def ENCODING_1D(cls) -> Group3Options:
        '''1-dimensional coding. (default)'''
        ...
    
    @classmethod
    @property
    def ENCODING_2D(cls) -> Group3Options:
        '''2-dimensional coding.'''
        ...
    
    @classmethod
    @property
    def UNCOMPRESSED(cls) -> Group3Options:
        '''Data not compressed.'''
        ...
    
    @classmethod
    @property
    def FILL_BITS(cls) -> Group3Options:
        '''Fill to byte boundary.'''
        ...
    
    ...

class TiffAlphaStorage:
    '''Specifies the alpha storage for tiff documents.'''
    
    @classmethod
    @property
    def UNSPECIFIED(cls) -> TiffAlphaStorage:
        '''The alpha is not specified and stored in the tiff file.'''
        ...
    
    @classmethod
    @property
    def ASSOCIATED(cls) -> TiffAlphaStorage:
        '''The alpha value is stored in premultiplied form. When alpha is restored there may be some rounding effects and restored value may be different from the original.'''
        ...
    
    @classmethod
    @property
    def UNASSOCIATED(cls) -> TiffAlphaStorage:
        '''The alpha value is stored in unassociated form. That means that alpha restored is exactly the same as it was stored to the tiff.'''
        ...
    
    ...

class TiffByteOrder:
    '''The byte order for the tiff image'''
    
    @classmethod
    @property
    def BIG_ENDIAN(cls) -> TiffByteOrder:
        '''The big endian byte order (Motorola).'''
        ...
    
    @classmethod
    @property
    def LITTLE_ENDIAN(cls) -> TiffByteOrder:
        '''The little endian byte order (Intel).'''
        ...
    
    ...

class TiffCompressions:
    '''Holds compression types'''
    
    @classmethod
    @property
    def NONE(cls) -> TiffCompressions:
        '''Dump mode.'''
        ...
    
    @classmethod
    @property
    def CCITT_RLE(cls) -> TiffCompressions:
        '''CCITT modified Huffman RLE.'''
        ...
    
    @classmethod
    @property
    def CCITT_FAX3(cls) -> TiffCompressions:
        '''CCITT Group 3 fax encoding.'''
        ...
    
    @classmethod
    @property
    def CCITT_FAX4(cls) -> TiffCompressions:
        '''CCITT Group 4 fax encoding.'''
        ...
    
    @classmethod
    @property
    def LZW(cls) -> TiffCompressions:
        '''Lempel-Ziv & Welch.'''
        ...
    
    @classmethod
    @property
    def OJPEG(cls) -> TiffCompressions:
        '''Original JPEG / Old-style JPEG (6.0).'''
        ...
    
    @classmethod
    @property
    def JPEG(cls) -> TiffCompressions:
        '''JPEG DCT compression. Introduced post TIFF rev 6.0.'''
        ...
    
    @classmethod
    @property
    def NEXT(cls) -> TiffCompressions:
        '''NeXT 2-bit RLE.'''
        ...
    
    @classmethod
    @property
    def CCITT_RLE_W(cls) -> TiffCompressions:
        '''CCITT RLE.'''
        ...
    
    @classmethod
    @property
    def PACKBITS(cls) -> TiffCompressions:
        '''Macintosh RLE.'''
        ...
    
    @classmethod
    @property
    def THUNDERSCAN(cls) -> TiffCompressions:
        '''ThunderScan RLE.'''
        ...
    
    @classmethod
    @property
    def IT_8_CTPAD(cls) -> TiffCompressions:
        '''IT8 CT w/padding. Reserved for ANSI IT8 TIFF/IT.'''
        ...
    
    @classmethod
    @property
    def IT_8_LW(cls) -> TiffCompressions:
        '''IT8 Linework RLE. Reserved for ANSI IT8 TIFF/IT.'''
        ...
    
    @classmethod
    @property
    def IT_8_MP(cls) -> TiffCompressions:
        '''IT8 Monochrome picture. Reserved for ANSI IT8 TIFF/IT.'''
        ...
    
    @classmethod
    @property
    def IT_8_BL(cls) -> TiffCompressions:
        '''IT8 Binary line art. Reserved for ANSI IT8 TIFF/IT.'''
        ...
    
    @classmethod
    @property
    def PIXAR_FILM(cls) -> TiffCompressions:
        '''Pixar companded 10bit LZW. Reserved for Pixar.'''
        ...
    
    @classmethod
    @property
    def PIXAR_LOG(cls) -> TiffCompressions:
        '''Pixar companded 11bit ZIP. Reserved for Pixar.'''
        ...
    
    @classmethod
    @property
    def DEFLATE(cls) -> TiffCompressions:
        '''Deflate compression.'''
        ...
    
    @classmethod
    @property
    def ADOBE_DEFLATE(cls) -> TiffCompressions:
        '''Deflate compression, as recognized by Adobe.'''
        ...
    
    @classmethod
    @property
    def DCS(cls) -> TiffCompressions:
        '''Kodak DCS encoding.
        Reserved for Oceana Matrix'''
        ...
    
    @classmethod
    @property
    def JBIG(cls) -> TiffCompressions:
        '''ISO Jpeg big.'''
        ...
    
    @classmethod
    @property
    def SGILOG(cls) -> TiffCompressions:
        '''SGI Log Luminance RLE.'''
        ...
    
    @classmethod
    @property
    def SGILOG24(cls) -> TiffCompressions:
        '''SGI Log 24-bit packed.'''
        ...
    
    @classmethod
    @property
    def JP2000(cls) -> TiffCompressions:
        '''Leadtools JPEG2000.'''
        ...
    
    ...

class TiffDataTypes:
    '''The tiff data type enum.'''
    
    @classmethod
    @property
    def BYTE(cls) -> TiffDataTypes:
        '''8-bit unsigned integer.'''
        ...
    
    @classmethod
    @property
    def ASCII(cls) -> TiffDataTypes:
        '''8-bit bytes with last byte ``null``.'''
        ...
    
    @classmethod
    @property
    def SHORT(cls) -> TiffDataTypes:
        '''16-bit unsigned integer.'''
        ...
    
    @classmethod
    @property
    def LONG(cls) -> TiffDataTypes:
        '''32-bit unsigned integer.'''
        ...
    
    @classmethod
    @property
    def RATIONAL(cls) -> TiffDataTypes:
        '''64-bit unsigned fraction.'''
        ...
    
    @classmethod
    @property
    def SBYTE(cls) -> TiffDataTypes:
        '''8-bit signed integer.'''
        ...
    
    @classmethod
    @property
    def UNDEFINED(cls) -> TiffDataTypes:
        '''8-bit untyped data.'''
        ...
    
    @classmethod
    @property
    def SSHORT(cls) -> TiffDataTypes:
        '''16-bit signed integer.'''
        ...
    
    @classmethod
    @property
    def SLONG(cls) -> TiffDataTypes:
        '''32-bit signed integer.'''
        ...
    
    @classmethod
    @property
    def SRATIONAL(cls) -> TiffDataTypes:
        '''64-bit signed fraction.'''
        ...
    
    @classmethod
    @property
    def FLOAT(cls) -> TiffDataTypes:
        '''32-bit IEEE floating point.'''
        ...
    
    @classmethod
    @property
    def DOUBLE(cls) -> TiffDataTypes:
        '''64-bit IEEE floating point.'''
        ...
    
    @classmethod
    @property
    def IFD(cls) -> TiffDataTypes:
        '''Pointer to Exif image file directory (IFD).'''
        ...
    
    ...

class TiffExpectedFormat:
    '''The expected tiff file format.'''
    
    @classmethod
    @property
    def DEFAULT(cls) -> TiffExpectedFormat:
        '''The default tiff format is no compression with B/W 1 bit per pixel only format. You can also use this setting to get an empty options and initialize with your tags or other settings.'''
        ...
    
    @classmethod
    @property
    def TIFF_LZW_BW(cls) -> TiffExpectedFormat:
        '''The tiff having LZW compression and B/W 1 bit per pixel only format.'''
        ...
    
    @classmethod
    @property
    def TIFF_LZW_RGB(cls) -> TiffExpectedFormat:
        '''The tiff having LZW compression and RGB color format.'''
        ...
    
    @classmethod
    @property
    def TIFF_LZW_RGBA(cls) -> TiffExpectedFormat:
        '''The tiff having LZW compression and RGBA with transparency color format.'''
        ...
    
    @classmethod
    @property
    def TIFF_LZW_CMYK(cls) -> TiffExpectedFormat:
        '''The tiff LZW cmyk'''
        ...
    
    @classmethod
    @property
    def TIFF_CCITT_FAX3(cls) -> TiffExpectedFormat:
        '''The tiff CCITT FAX3 encoding. B/W 1 bit per pixel only supported for that scheme.'''
        ...
    
    @classmethod
    @property
    def TIFF_CCITT_FAX4(cls) -> TiffExpectedFormat:
        '''The tiff CCITT FAX4 encoding. B/W 1 bit per pixel only supported for that scheme.'''
        ...
    
    @classmethod
    @property
    def TIFF_DEFLATE_BW(cls) -> TiffExpectedFormat:
        '''The tiff having deflate compression and B/W 1 bit per pixel only format.'''
        ...
    
    @classmethod
    @property
    def TIFF_DEFLATE_RGB(cls) -> TiffExpectedFormat:
        '''The tiff having deflate compression and RGB color format.'''
        ...
    
    @classmethod
    @property
    def TIFF_DEFLATE_RGBA(cls) -> TiffExpectedFormat:
        '''The tiff having deflate compression and RGBA color format.'''
        ...
    
    @classmethod
    @property
    def TIFF_CCIT_RLE(cls) -> TiffExpectedFormat:
        '''The tiff CCITT RLE encoding. B/W 1 bit per pixel only supported for that scheme.'''
        ...
    
    @classmethod
    @property
    def TIFF_JPEG_RGB(cls) -> TiffExpectedFormat:
        '''The tiff having Jpeg compression and RGB color format.'''
        ...
    
    @classmethod
    @property
    def TIFF_JPEG_Y_CB_CR(cls) -> TiffExpectedFormat:
        '''The tiff having Jpeg compression and YCBCR color format.'''
        ...
    
    @classmethod
    @property
    def TIFF_NO_COMPRESSION_BW(cls) -> TiffExpectedFormat:
        '''The uncompressed tiff and B/W 1 bit per pixel only format.'''
        ...
    
    @classmethod
    @property
    def TIFF_NO_COMPRESSION_RGB(cls) -> TiffExpectedFormat:
        '''The uncompressed tiff and RGB color format.'''
        ...
    
    @classmethod
    @property
    def TIFF_NO_COMPRESSION_RGBA(cls) -> TiffExpectedFormat:
        '''The uncompressed tiff and RGBA with transparency color format.'''
        ...
    
    ...

class TiffFileStandards:
    '''Specifies the TIFF file format standards.'''
    
    @classmethod
    @property
    def BASELINE(cls) -> TiffFileStandards:
        '''The Baseline TIFF 6.0 file standard. This standard is formally known as TIFF 6.0, Part 1: Baseline TIFF.'''
        ...
    
    @classmethod
    @property
    def EXTENDED(cls) -> TiffFileStandards:
        '''The Extended TIFF 6.0 file standard. This standard is formally known as Extended TIFF 6.0, Part 2: TIFF Extensions.'''
        ...
    
    ...

class TiffFillOrders:
    '''Data order within a byte.
    
    Possible values for FILLORDER tag.'''
    
    @classmethod
    @property
    def MSB_2_LSB(cls) -> TiffFillOrders:
        '''Most significant -> least.'''
        ...
    
    @classmethod
    @property
    def LSB_2_MSB(cls) -> TiffFillOrders:
        '''Least significant -> most.'''
        ...
    
    ...

class TiffNewSubFileTypes:
    '''The tiff new sub file type enum.'''
    
    @classmethod
    @property
    def FILE_TYPE_DEFAULT(cls) -> TiffNewSubFileTypes:
        '''The default filetype.'''
        ...
    
    @classmethod
    @property
    def FILE_TYPE_REDUCED_IMAGE(cls) -> TiffNewSubFileTypes:
        '''The reduced image filetype.'''
        ...
    
    @classmethod
    @property
    def FILE_TYPE_PAGE(cls) -> TiffNewSubFileTypes:
        '''The page filetype.'''
        ...
    
    @classmethod
    @property
    def FILE_TYPE_MASK(cls) -> TiffNewSubFileTypes:
        '''The mask filetype.'''
        ...
    
    @classmethod
    @property
    def FILE_TYPE_LAST(cls) -> TiffNewSubFileTypes:
        '''The last filetype.'''
        ...
    
    ...

class TiffOrientations:
    '''Image orientation.
    
    Possible values for ORIENTATION tag.'''
    
    @classmethod
    @property
    def TOP_LEFT(cls) -> TiffOrientations:
        '''Row 0 top, Column 0 lhs.'''
        ...
    
    @classmethod
    @property
    def TOP_RIGHT(cls) -> TiffOrientations:
        '''Row 0 top, Column 0 rhs.'''
        ...
    
    @classmethod
    @property
    def BOTTOM_RIGHT(cls) -> TiffOrientations:
        '''Row 0 bottom, Column 0 rhs.'''
        ...
    
    @classmethod
    @property
    def BOTTOM_LEFT(cls) -> TiffOrientations:
        '''Row 0 bottom, Column 0 lhs.'''
        ...
    
    @classmethod
    @property
    def LEFT_TOP(cls) -> TiffOrientations:
        '''Row 0 lhs, Column 0 top.'''
        ...
    
    @classmethod
    @property
    def RIGHT_TOP(cls) -> TiffOrientations:
        '''Row 0 rhs, Column 0 top.'''
        ...
    
    @classmethod
    @property
    def RIGHT_BOTTOM(cls) -> TiffOrientations:
        '''Row 0 rhs, Column 0 bottom.'''
        ...
    
    @classmethod
    @property
    def LEFT_BOTTOM(cls) -> TiffOrientations:
        '''Row 0 lhs, Column 0 bottom.'''
        ...
    
    ...

class TiffPhotometrics:
    '''Photometric interpolation enum'''
    
    @classmethod
    @property
    def MIN_IS_WHITE(cls) -> TiffPhotometrics:
        '''Min value is white.'''
        ...
    
    @classmethod
    @property
    def MIN_IS_BLACK(cls) -> TiffPhotometrics:
        '''Min value is black.'''
        ...
    
    @classmethod
    @property
    def RGB(cls) -> TiffPhotometrics:
        '''RGB color model.'''
        ...
    
    @classmethod
    @property
    def PALETTE(cls) -> TiffPhotometrics:
        '''Color map indexed.'''
        ...
    
    @classmethod
    @property
    def MASK(cls) -> TiffPhotometrics:
        '''[obsoleted by TIFF rev. 6.0] Holdout mask.'''
        ...
    
    @classmethod
    @property
    def SEPARATED(cls) -> TiffPhotometrics:
        '''Color separations.'''
        ...
    
    @classmethod
    @property
    def YCBCR(cls) -> TiffPhotometrics:
        '''The CCIR 601.'''
        ...
    
    @classmethod
    @property
    def CIELAB(cls) -> TiffPhotometrics:
        '''1976 CIE L*a*b*.'''
        ...
    
    @classmethod
    @property
    def ICCLAB(cls) -> TiffPhotometrics:
        '''ICC L*a*b*. Introduced post TIFF rev 6.0 by Adobe TIFF Technote 4.'''
        ...
    
    @classmethod
    @property
    def ITULAB(cls) -> TiffPhotometrics:
        '''ITU L*a*b*.'''
        ...
    
    @classmethod
    @property
    def LOGL(cls) -> TiffPhotometrics:
        '''CIE Log2(L).'''
        ...
    
    @classmethod
    @property
    def LOGLUV(cls) -> TiffPhotometrics:
        '''CIE Log2(L) (u',v').'''
        ...
    
    ...

class TiffPlanarConfigs:
    '''Storage organization.
    
    Possible values for PLANARCONFIG tag.'''
    
    @classmethod
    @property
    def CONTIGUOUS(cls) -> TiffPlanarConfigs:
        '''Single image plane.'''
        ...
    
    @classmethod
    @property
    def SEPARATE(cls) -> TiffPlanarConfigs:
        '''Separate planes of data.'''
        ...
    
    ...

class TiffPredictor:
    '''Prediction scheme for LZW'''
    
    @classmethod
    @property
    def NONE(cls) -> TiffPredictor:
        '''No prediction scheme used.'''
        ...
    
    @classmethod
    @property
    def HORIZONTAL(cls) -> TiffPredictor:
        '''Horizontal differencing.'''
        ...
    
    ...

class TiffResolutionUnits:
    '''Tiff Resolution Unit Enum'''
    
    @classmethod
    @property
    def NONE(cls) -> TiffResolutionUnits:
        '''No meaningful units.'''
        ...
    
    @classmethod
    @property
    def INCH(cls) -> TiffResolutionUnits:
        '''English system.'''
        ...
    
    @classmethod
    @property
    def CENTIMETER(cls) -> TiffResolutionUnits:
        '''Metric system.'''
        ...
    
    ...

class TiffSampleFormats:
    '''Sample format enum'''
    
    @classmethod
    @property
    def UINT(cls) -> TiffSampleFormats:
        '''Unsigned integer data'''
        ...
    
    @classmethod
    @property
    def INT(cls) -> TiffSampleFormats:
        '''Signed integer data'''
        ...
    
    @classmethod
    @property
    def IEEE_FP(cls) -> TiffSampleFormats:
        '''IEEE floating point data'''
        ...
    
    @classmethod
    @property
    def VOID(cls) -> TiffSampleFormats:
        '''Untyped data'''
        ...
    
    @classmethod
    @property
    def COMPLEX_INT(cls) -> TiffSampleFormats:
        '''Complex signed int'''
        ...
    
    @classmethod
    @property
    def COMPLEX_IEEE_FP(cls) -> TiffSampleFormats:
        '''Complex ieee floating'''
        ...
    
    ...

class TiffTags:
    '''The tiff tag enum.'''
    
    @classmethod
    @property
    def SUB_FILE_TYPE(cls) -> TiffTags:
        '''Subfile data descriptor.'''
        ...
    
    @classmethod
    @property
    def OSUBFILE_TYPE(cls) -> TiffTags:
        '''[obsoleted by TIFF rev. 5.0]
        
        Kind of data in subfile.'''
        ...
    
    @classmethod
    @property
    def IMAGE_WIDTH(cls) -> TiffTags:
        '''Image width in pixels.'''
        ...
    
    @classmethod
    @property
    def IMAGE_LENGTH(cls) -> TiffTags:
        '''Image height in pixels.'''
        ...
    
    @classmethod
    @property
    def BITS_PER_SAMPLE(cls) -> TiffTags:
        '''Bits per channel (sample).'''
        ...
    
    @classmethod
    @property
    def COMPRESSION(cls) -> TiffTags:
        '''Data compression technique.'''
        ...
    
    @classmethod
    @property
    def PHOTOMETRIC(cls) -> TiffTags:
        '''Photometric interpretation.'''
        ...
    
    @classmethod
    @property
    def THRESHOLDING(cls) -> TiffTags:
        '''[obsoleted by TIFF rev. 5.0]
        
        Thresholding used on data.'''
        ...
    
    @classmethod
    @property
    def CELL_WIDTH(cls) -> TiffTags:
        '''[obsoleted by TIFF rev. 5.0]
        
        Dithering matrix width.'''
        ...
    
    @classmethod
    @property
    def CELL_LENGTH(cls) -> TiffTags:
        '''[obsoleted by TIFF rev. 5.0]
        
        Dithering matrix height.'''
        ...
    
    @classmethod
    @property
    def FILL_ORDER(cls) -> TiffTags:
        '''Data order within a byte.'''
        ...
    
    @classmethod
    @property
    def DOCUMENT_NAME(cls) -> TiffTags:
        '''Name of document which holds for image.'''
        ...
    
    @classmethod
    @property
    def IMAGE_DESCRIPTION(cls) -> TiffTags:
        '''Information about image.'''
        ...
    
    @classmethod
    @property
    def MAKE(cls) -> TiffTags:
        '''Scanner manufacturer name.'''
        ...
    
    @classmethod
    @property
    def MODEL(cls) -> TiffTags:
        '''Scanner model name/number.'''
        ...
    
    @classmethod
    @property
    def STRIP_OFFSETS(cls) -> TiffTags:
        '''Offsets to data strips.'''
        ...
    
    @classmethod
    @property
    def ORIENTATION(cls) -> TiffTags:
        '''[obsoleted by TIFF rev. 5.0]
        
        Image orientation.'''
        ...
    
    @classmethod
    @property
    def SAMPLES_PER_PIXEL(cls) -> TiffTags:
        '''Samples per pixel.'''
        ...
    
    @classmethod
    @property
    def ROWS_PER_STRIP(cls) -> TiffTags:
        '''Rows per strip of data.'''
        ...
    
    @classmethod
    @property
    def STRIP_BYTE_COUNTS(cls) -> TiffTags:
        '''Bytes counts for strips.'''
        ...
    
    @classmethod
    @property
    def MIN_SAMPLE_VALUE(cls) -> TiffTags:
        '''[obsoleted by TIFF rev. 5.0]
        
        Minimum sample value.'''
        ...
    
    @classmethod
    @property
    def MAX_SAMPLE_VALUE(cls) -> TiffTags:
        '''[obsoleted by TIFF rev. 5.0]
        
        Maximum sample value.'''
        ...
    
    @classmethod
    @property
    def XRESOLUTION(cls) -> TiffTags:
        '''Pixels/resolution in x.'''
        ...
    
    @classmethod
    @property
    def YRESOLUTION(cls) -> TiffTags:
        '''Pixels/resolution in y.'''
        ...
    
    @classmethod
    @property
    def PLANAR_CONFIG(cls) -> TiffTags:
        '''Storage organization.'''
        ...
    
    @classmethod
    @property
    def PAGE_NAME(cls) -> TiffTags:
        '''Page name image is from.'''
        ...
    
    @classmethod
    @property
    def XPOSITION(cls) -> TiffTags:
        '''X page offset of image lhs.'''
        ...
    
    @classmethod
    @property
    def YPOSITION(cls) -> TiffTags:
        '''Y page offset of image lhs.'''
        ...
    
    @classmethod
    @property
    def FREE_OFFSETS(cls) -> TiffTags:
        '''[obsoleted by TIFF rev. 5.0]
        
        Byte offset to free block.'''
        ...
    
    @classmethod
    @property
    def FREE_BYTE_COUNTS(cls) -> TiffTags:
        '''[obsoleted by TIFF rev. 5.0]
        
        Sizes of free blocks.'''
        ...
    
    @classmethod
    @property
    def GRAY_RESPONSE_UNIT(cls) -> TiffTags:
        '''[obsoleted by TIFF rev. 6.0]
        
        Gray scale curve accuracy.'''
        ...
    
    @classmethod
    @property
    def GRAY_RESPONSE_CURVE(cls) -> TiffTags:
        '''[obsoleted by TIFF rev. 6.0]
        
        Gray scale response curve.'''
        ...
    
    @classmethod
    @property
    def T4_OPTIONS(cls) -> TiffTags:
        '''TIFF 6.0 proper name alias for GROUP3OPTIONS.
        Options for CCITT Group 3 fax encoding. 32 flag bits.'''
        ...
    
    @classmethod
    @property
    def T6_OPTIONS(cls) -> TiffTags:
        '''Options for CCITT Group 4 fax encoding. 32 flag bits.
        TIFF 6.0 proper name alias for GROUP4OPTIONS.'''
        ...
    
    @classmethod
    @property
    def RESOLUTION_UNIT(cls) -> TiffTags:
        '''Units of resolutions.'''
        ...
    
    @classmethod
    @property
    def PAGE_NUMBER(cls) -> TiffTags:
        '''Page numbers of multi-page.'''
        ...
    
    @classmethod
    @property
    def COLOR_RESPONSE_UNIT(cls) -> TiffTags:
        '''[obsoleted by TIFF rev. 6.0]
        
        Color curve accuracy.'''
        ...
    
    @classmethod
    @property
    def TRANSFER_FUNCTION(cls) -> TiffTags:
        '''Colorimetry info.'''
        ...
    
    @classmethod
    @property
    def SOFTWARE(cls) -> TiffTags:
        '''Name & release.'''
        ...
    
    @classmethod
    @property
    def DATE_TIME(cls) -> TiffTags:
        '''Creation date and time.'''
        ...
    
    @classmethod
    @property
    def ARTIST(cls) -> TiffTags:
        '''Creator of image.'''
        ...
    
    @classmethod
    @property
    def HOST_COMPUTER(cls) -> TiffTags:
        '''Machine where created.'''
        ...
    
    @classmethod
    @property
    def PREDICTOR(cls) -> TiffTags:
        '''Prediction scheme w/ LZW.'''
        ...
    
    @classmethod
    @property
    def WHITE_POINT(cls) -> TiffTags:
        '''Image white point.'''
        ...
    
    @classmethod
    @property
    def PRIMARY_CHROMATICITIES(cls) -> TiffTags:
        '''Primary chromaticities.'''
        ...
    
    @classmethod
    @property
    def COLOR_MAP(cls) -> TiffTags:
        '''RGB map for pallette image.'''
        ...
    
    @classmethod
    @property
    def HALFTONE_HINTS(cls) -> TiffTags:
        '''Highlight + shadow info.'''
        ...
    
    @classmethod
    @property
    def TILE_WIDTH(cls) -> TiffTags:
        '''Tile width in pixels.'''
        ...
    
    @classmethod
    @property
    def TILE_LENGTH(cls) -> TiffTags:
        '''Tile height in pixels.'''
        ...
    
    @classmethod
    @property
    def TILE_OFFSETS(cls) -> TiffTags:
        '''Offsets to data tiles.'''
        ...
    
    @classmethod
    @property
    def TILE_BYTE_COUNTS(cls) -> TiffTags:
        '''Byte counts for tiles.'''
        ...
    
    @classmethod
    @property
    def BAD_FAX_LINES(cls) -> TiffTags:
        '''Lines with wrong pixel count.'''
        ...
    
    @classmethod
    @property
    def CLEAN_FAX_DATA(cls) -> TiffTags:
        '''Regenerated line info.'''
        ...
    
    @classmethod
    @property
    def CONSECUTIVE_BAD_FAX_LINES(cls) -> TiffTags:
        '''Max consecutive bad lines.'''
        ...
    
    @classmethod
    @property
    def SUB_IFD(cls) -> TiffTags:
        '''Subimage descriptors.'''
        ...
    
    @classmethod
    @property
    def INK_SET(cls) -> TiffTags:
        '''Inks in separated image.'''
        ...
    
    @classmethod
    @property
    def INK_NAMES(cls) -> TiffTags:
        '''ASCII names of inks.'''
        ...
    
    @classmethod
    @property
    def NUMBER_OF_INKS(cls) -> TiffTags:
        '''Number of inks.'''
        ...
    
    @classmethod
    @property
    def DOT_RANGE(cls) -> TiffTags:
        '''0% and 100% dot codes.'''
        ...
    
    @classmethod
    @property
    def TARGET_PRINTER(cls) -> TiffTags:
        '''Separation target.'''
        ...
    
    @classmethod
    @property
    def EXTRA_SAMPLES(cls) -> TiffTags:
        '''Information about extra samples.'''
        ...
    
    @classmethod
    @property
    def SAMPLE_FORMAT(cls) -> TiffTags:
        '''Data sample format.'''
        ...
    
    @classmethod
    @property
    def SMIN_SAMPLE_VALUE(cls) -> TiffTags:
        '''Variable MinSampleValue.'''
        ...
    
    @classmethod
    @property
    def SMAX_SAMPLE_VALUE(cls) -> TiffTags:
        '''Variable MaxSampleValue.'''
        ...
    
    @classmethod
    @property
    def TRANSFER_RANGE(cls) -> TiffTags:
        '''Variable TransferRange'''
        ...
    
    @classmethod
    @property
    def CLIP_PATH(cls) -> TiffTags:
        '''ClipPath. Introduced post TIFF rev 6.0 by Adobe TIFF technote 2.'''
        ...
    
    @classmethod
    @property
    def XCLIPPATHUNITS(cls) -> TiffTags:
        '''XClipPathUnits. Introduced post TIFF rev 6.0 by Adobe TIFF technote 2.'''
        ...
    
    @classmethod
    @property
    def YCLIPPATHUNITS(cls) -> TiffTags:
        '''YClipPathUnits. Introduced post TIFF rev 6.0 by Adobe TIFF technote 2.'''
        ...
    
    @classmethod
    @property
    def INDEXED(cls) -> TiffTags:
        '''Indexed. Introduced post TIFF rev 6.0 by Adobe TIFF Technote 3.'''
        ...
    
    @classmethod
    @property
    def JPEG_TABLES(cls) -> TiffTags:
        '''JPEG table stream. Introduced post TIFF rev 6.0.'''
        ...
    
    @classmethod
    @property
    def OPI_PROXY(cls) -> TiffTags:
        '''OPI Proxy. Introduced post TIFF rev 6.0 by Adobe TIFF technote.'''
        ...
    
    @classmethod
    @property
    def JPEG_PROC(cls) -> TiffTags:
        '''[obsoleted by Technical Note #2 which specifies a revised JPEG-in-TIFF scheme]
        
        JPEG processing algorithm.'''
        ...
    
    @classmethod
    @property
    def JPEG_INERCHANGE_FORMAT(cls) -> TiffTags:
        '''[obsoleted by Technical Note #2 which specifies a revised JPEG-in-TIFF scheme]
        
        Pointer to SOI marker.'''
        ...
    
    @classmethod
    @property
    def JPEG_INTERCHANGE_FORMAT_LENGTH(cls) -> TiffTags:
        '''[obsoleted by Technical Note #2 which specifies a revised JPEG-in-TIFF scheme]
        
        JFIF stream length'''
        ...
    
    @classmethod
    @property
    def JPEG_RESTART_INTERVAL(cls) -> TiffTags:
        '''[obsoleted by Technical Note #2 which specifies a revised JPEG-in-TIFF scheme]
        
        Restart interval length.'''
        ...
    
    @classmethod
    @property
    def JPEG_LOSSLESS_PREDICTORS(cls) -> TiffTags:
        '''[obsoleted by Technical Note #2 which specifies a revised JPEG-in-TIFF scheme]
        
        Lossless proc predictor.'''
        ...
    
    @classmethod
    @property
    def JPEG_POINT_TRANSFORM(cls) -> TiffTags:
        '''[obsoleted by Technical Note #2 which specifies a revised JPEG-in-TIFF scheme]
        
        Lossless point transform.'''
        ...
    
    @classmethod
    @property
    def JPEG_Q_TABLES(cls) -> TiffTags:
        '''[obsoleted by Technical Note #2 which specifies a revised JPEG-in-TIFF scheme]
        
        Q matrice offsets.'''
        ...
    
    @classmethod
    @property
    def JPEG_D_CTABLES(cls) -> TiffTags:
        '''[obsoleted by Technical Note #2 which specifies a revised JPEG-in-TIFF scheme]
        
        DCT table offsets.'''
        ...
    
    @classmethod
    @property
    def JPEG_A_CTABLES(cls) -> TiffTags:
        '''[obsoleted by Technical Note #2 which specifies a revised JPEG-in-TIFF scheme]
        
        AC coefficient offsets.'''
        ...
    
    @classmethod
    @property
    def YCBCR_COEFFICIENTS(cls) -> TiffTags:
        '''RGB -> YCbCr transform.'''
        ...
    
    @classmethod
    @property
    def YCBCR_SUB_SAMPLING(cls) -> TiffTags:
        '''YCbCr subsampling factors.'''
        ...
    
    @classmethod
    @property
    def YCBCR_POSITIONING(cls) -> TiffTags:
        '''Subsample positioning.'''
        ...
    
    @classmethod
    @property
    def REFERENCE_BLACK_WHITE(cls) -> TiffTags:
        '''Colorimetry info.'''
        ...
    
    @classmethod
    @property
    def XML_PACKET(cls) -> TiffTags:
        '''XML packet. Introduced post TIFF rev 6.0 by Adobe XMP Specification, January 2004.'''
        ...
    
    @classmethod
    @property
    def OPI_IMAGEID(cls) -> TiffTags:
        '''OPI ImageID. Introduced post TIFF rev 6.0 by Adobe TIFF technote.'''
        ...
    
    @classmethod
    @property
    def REFPTS(cls) -> TiffTags:
        '''Image reference points. Private tag registered to Island Graphics.'''
        ...
    
    @classmethod
    @property
    def COPYRIGHT(cls) -> TiffTags:
        '''Copyright string. This tag is listed in the TIFF rev. 6.0 w/ unknown ownership.'''
        ...
    
    @classmethod
    @property
    def PHOTOSHOP_RESOURCES(cls) -> TiffTags:
        '''Photoshop image resources.'''
        ...
    
    @classmethod
    @property
    def ICC_PROFILE(cls) -> TiffTags:
        '''The embedded ICC device profile'''
        ...
    
    @classmethod
    @property
    def EXIF_IFD_POINTER(cls) -> TiffTags:
        '''A pointer to the Exif IFD.'''
        ...
    
    @classmethod
    @property
    def XP_TITLE(cls) -> TiffTags:
        '''Information about image, used by Windows Explorer.
        The :py:attr:`aspose.cad.fileformats.tiff.enums.TiffTags.XP_TITLE` is ignored by Windows Explorer if the :py:attr:`aspose.cad.fileformats.tiff.enums.TiffTags.IMAGE_DESCRIPTION` tag exists.'''
        ...
    
    @classmethod
    @property
    def XP_COMMENT(cls) -> TiffTags:
        '''Comment on image, used by Windows Explorer.'''
        ...
    
    @classmethod
    @property
    def XP_AUTHOR(cls) -> TiffTags:
        '''Image Author, used by Windows Explorer.
        The :py:attr:`aspose.cad.fileformats.tiff.enums.TiffTags.XP_AUTHOR` is ignored by Windows Explorer if the :py:attr:`aspose.cad.fileformats.tiff.enums.TiffTags.ARTIST` tag exists.'''
        ...
    
    @classmethod
    @property
    def XP_KEYWORDS(cls) -> TiffTags:
        '''Image Keywords, used by Windows Explorer.'''
        ...
    
    @classmethod
    @property
    def XP_SUBJECT(cls) -> TiffTags:
        '''Subject image, used by Windows Explorer.'''
        ...
    
    ...

class TiffThresholds:
    '''Thresholding used on data.'''
    
    @classmethod
    @property
    def NO_DITHERING(cls) -> TiffThresholds:
        '''No dithering is performed.'''
        ...
    
    @classmethod
    @property
    def HALF_TONE(cls) -> TiffThresholds:
        '''Dithered scan.'''
        ...
    
    @classmethod
    @property
    def ERROR_DIFFUSE(cls) -> TiffThresholds:
        '''Usually Floyd-Steinberg.'''
        ...
    
    ...

