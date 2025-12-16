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

class ExifColorSpace:
    '''exif color space enum.'''
    
    @classmethod
    @property
    def S_RGB(cls) -> ExifColorSpace:
        '''SRGB color space.'''
        ...
    
    @classmethod
    @property
    def ADOBE_RGB(cls) -> ExifColorSpace:
        '''Adobe rgb color space.'''
        ...
    
    @classmethod
    @property
    def UNCALIBRATED(cls) -> ExifColorSpace:
        '''Uncalibrated color space.'''
        ...
    
    ...

class ExifContrast:
    '''exif normal soft hard enum.'''
    
    @classmethod
    @property
    def NORMAL(cls) -> ExifContrast:
        '''Normal contrast.'''
        ...
    
    @classmethod
    @property
    def LOW(cls) -> ExifContrast:
        '''Low contrast.'''
        ...
    
    @classmethod
    @property
    def HIGH(cls) -> ExifContrast:
        '''High contrast.'''
        ...
    
    ...

class ExifCustomRendered:
    '''exif custom rendered enum.'''
    
    @classmethod
    @property
    def NORMAL_PROCESS(cls) -> ExifCustomRendered:
        '''Normal render process.'''
        ...
    
    @classmethod
    @property
    def CUSTOM_PROCESS(cls) -> ExifCustomRendered:
        '''Custom render process.'''
        ...
    
    ...

class ExifExposureMode:
    '''exif exposure mode enum.'''
    
    @classmethod
    @property
    def AUTO(cls) -> ExifExposureMode:
        '''Auto exposure.'''
        ...
    
    @classmethod
    @property
    def MANUAL(cls) -> ExifExposureMode:
        '''Manual exposure.'''
        ...
    
    @classmethod
    @property
    def AUTO_BRACKET(cls) -> ExifExposureMode:
        '''Auto bracket.'''
        ...
    
    ...

class ExifExposureProgram:
    '''exif exposure program enum.'''
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> ExifExposureProgram:
        '''Not defined.'''
        ...
    
    @classmethod
    @property
    def MANUAL(cls) -> ExifExposureProgram:
        '''Manual program.'''
        ...
    
    @classmethod
    @property
    def AUTO(cls) -> ExifExposureProgram:
        '''Auto exposure.'''
        ...
    
    @classmethod
    @property
    def APERTUREPRIORITY(cls) -> ExifExposureProgram:
        '''Aperture priority.'''
        ...
    
    @classmethod
    @property
    def SHUTTERPRIORITY(cls) -> ExifExposureProgram:
        '''Shutter priority.'''
        ...
    
    @classmethod
    @property
    def CREATIVEPROGRAM(cls) -> ExifExposureProgram:
        '''Creative program.'''
        ...
    
    @classmethod
    @property
    def ACTIONPROGRAM(cls) -> ExifExposureProgram:
        '''Action program.'''
        ...
    
    @classmethod
    @property
    def PORTRAITMODE(cls) -> ExifExposureProgram:
        '''Portrait mode.'''
        ...
    
    @classmethod
    @property
    def LANDSCAPEMODE(cls) -> ExifExposureProgram:
        '''Landscape mode.'''
        ...
    
    ...

class ExifFileSource:
    '''exif file source enum.'''
    
    @classmethod
    @property
    def OTHERS(cls) -> ExifFileSource:
        '''The others.'''
        ...
    
    @classmethod
    @property
    def FILM_SCANNER(cls) -> ExifFileSource:
        '''Film scanner.'''
        ...
    
    @classmethod
    @property
    def REFLEXION_PRINT_SCANNER(cls) -> ExifFileSource:
        '''Reflexion print scanner.'''
        ...
    
    @classmethod
    @property
    def DIGITAL_STILL_CAMERA(cls) -> ExifFileSource:
        '''Digital still camera.'''
        ...
    
    ...

class ExifFlash:
    '''Flash mode.'''
    
    @classmethod
    @property
    def NOFLASH(cls) -> ExifFlash:
        '''No flash fired.'''
        ...
    
    @classmethod
    @property
    def FIRED(cls) -> ExifFlash:
        '''Flash fired.'''
        ...
    
    @classmethod
    @property
    def FIRED_RETURN_LIGHT_NOT_DETECTED(cls) -> ExifFlash:
        '''Flash fired, return light not detected.'''
        ...
    
    @classmethod
    @property
    def FIRED_RETURN_LIGHT_DETECTED(cls) -> ExifFlash:
        '''Flash fired, return light detected.'''
        ...
    
    @classmethod
    @property
    def YES_COMPULSORY(cls) -> ExifFlash:
        '''Flash fired, compulsory flash mode.'''
        ...
    
    @classmethod
    @property
    def YES_COMPULSORY_RETURN_LIGHT_NOT_DETECTED(cls) -> ExifFlash:
        '''Flash fired, compulsory mode, return light not detected.'''
        ...
    
    @classmethod
    @property
    def YES_COMPULSORY_RETURN_LIGHT_DETECTED(cls) -> ExifFlash:
        '''Flash fired, compulsory mode, return light detected.'''
        ...
    
    @classmethod
    @property
    def NO_COMPULSORY(cls) -> ExifFlash:
        '''Flash did not fire, compulsory flash mode.'''
        ...
    
    @classmethod
    @property
    def NO_DID_NOT_FIRE_RETURN_LIGHT_NOT_DETECTED(cls) -> ExifFlash:
        '''Flash did not fire, return light not detected.'''
        ...
    
    @classmethod
    @property
    def NO_AUTO(cls) -> ExifFlash:
        '''Flash did not fire, auto mode.'''
        ...
    
    @classmethod
    @property
    def YES_AUTO(cls) -> ExifFlash:
        '''Flash firedm auto mode.'''
        ...
    
    @classmethod
    @property
    def YES_AUTO_RETURN_LIGHT_NOT_DETECTED(cls) -> ExifFlash:
        '''Flash fired, auto mode, return light not detected.'''
        ...
    
    @classmethod
    @property
    def YES_AUTO_RETURN_LIGHT_DETECTED(cls) -> ExifFlash:
        '''Flash fired, auto mode, return light detected.'''
        ...
    
    @classmethod
    @property
    def NO_FLASH_FUNCTION(cls) -> ExifFlash:
        '''No flash function.'''
        ...
    
    ...

class ExifGPSAltitudeRef:
    '''exif gps altitude ref enum.'''
    
    @classmethod
    @property
    def ABOVE_SEA_LEVEL(cls) -> ExifGPSAltitudeRef:
        '''Above sea level.'''
        ...
    
    @classmethod
    @property
    def BELOW_SEA_LEVEL(cls) -> ExifGPSAltitudeRef:
        '''Below sea level.'''
        ...
    
    ...

class ExifGainControl:
    '''exif gain control enum.'''
    
    @classmethod
    @property
    def NONE(cls) -> ExifGainControl:
        '''No gain control.'''
        ...
    
    @classmethod
    @property
    def LOW_GAIN_UP(cls) -> ExifGainControl:
        '''Low gain up.'''
        ...
    
    @classmethod
    @property
    def HIGH_GAIN_UP(cls) -> ExifGainControl:
        '''High gain up.'''
        ...
    
    @classmethod
    @property
    def LOW_GAIN_DOWN(cls) -> ExifGainControl:
        '''Low gain down.'''
        ...
    
    @classmethod
    @property
    def HIGH_GAIN_DOWN(cls) -> ExifGainControl:
        '''High gain down.'''
        ...
    
    ...

class ExifLightSource:
    '''The exif light source.'''
    
    @classmethod
    @property
    def UNKNOWN(cls) -> ExifLightSource:
        '''The unknown.'''
        ...
    
    @classmethod
    @property
    def DAYLIGHT(cls) -> ExifLightSource:
        '''The daylight.'''
        ...
    
    @classmethod
    @property
    def FLUORESCENT(cls) -> ExifLightSource:
        '''The fluorescent.'''
        ...
    
    @classmethod
    @property
    def TUNGSTEN(cls) -> ExifLightSource:
        '''The tungsten.'''
        ...
    
    @classmethod
    @property
    def FLASH(cls) -> ExifLightSource:
        '''The flash.'''
        ...
    
    @classmethod
    @property
    def FINEWEATHER(cls) -> ExifLightSource:
        '''The fineweather.'''
        ...
    
    @classmethod
    @property
    def CLOUDYWEATHER(cls) -> ExifLightSource:
        '''The cloudyweather.'''
        ...
    
    @classmethod
    @property
    def SHADE(cls) -> ExifLightSource:
        '''The shade.'''
        ...
    
    @classmethod
    @property
    def DAYLIGHT_FLUORESCENT(cls) -> ExifLightSource:
        '''The daylight fluorescent.'''
        ...
    
    @classmethod
    @property
    def DAY_WHITE_FLUORESCENT(cls) -> ExifLightSource:
        '''The day white fluorescent.'''
        ...
    
    @classmethod
    @property
    def COOL_WHITE_FLUORESCENT(cls) -> ExifLightSource:
        '''The cool white fluorescent.'''
        ...
    
    @classmethod
    @property
    def WHITE_FLUORESCENT(cls) -> ExifLightSource:
        '''The white fluorescent.'''
        ...
    
    @classmethod
    @property
    def STANDARDLIGHT_A(cls) -> ExifLightSource:
        '''The standardlight a.'''
        ...
    
    @classmethod
    @property
    def STANDARDLIGHT_B(cls) -> ExifLightSource:
        '''The standardlight b.'''
        ...
    
    @classmethod
    @property
    def STANDARDLIGHT_C(cls) -> ExifLightSource:
        '''The standardlight c.'''
        ...
    
    @classmethod
    @property
    def D55(cls) -> ExifLightSource:
        '''The d55 value(5500K).'''
        ...
    
    @classmethod
    @property
    def D65(cls) -> ExifLightSource:
        '''The d65 value(6500K).'''
        ...
    
    @classmethod
    @property
    def D75(cls) -> ExifLightSource:
        '''The d75 value(7500K).'''
        ...
    
    @classmethod
    @property
    def D50(cls) -> ExifLightSource:
        '''The d50 value(5000K).'''
        ...
    
    @classmethod
    @property
    def IS_OSTUDIOTUNGSTEN(cls) -> ExifLightSource:
        '''The iso studio tungsten lightsource.'''
        ...
    
    @classmethod
    @property
    def OTHERLIGHTSOURCE(cls) -> ExifLightSource:
        '''The otherlightsource.'''
        ...
    
    ...

class ExifMeteringMode:
    '''exif metering mode enum.'''
    
    @classmethod
    @property
    def UNKNOWN(cls) -> ExifMeteringMode:
        '''Undefined mode'''
        ...
    
    @classmethod
    @property
    def AVERAGE(cls) -> ExifMeteringMode:
        '''Average metering'''
        ...
    
    @classmethod
    @property
    def CENTERWEIGHTEDAVERAGE(cls) -> ExifMeteringMode:
        '''Center weighted average.'''
        ...
    
    @classmethod
    @property
    def SPOT(cls) -> ExifMeteringMode:
        '''Spot metering'''
        ...
    
    @classmethod
    @property
    def MULTI_SPOT(cls) -> ExifMeteringMode:
        '''Multi spot metering'''
        ...
    
    @classmethod
    @property
    def MULTI_SEGMENT(cls) -> ExifMeteringMode:
        '''Multi segment metering.'''
        ...
    
    @classmethod
    @property
    def PARTIAL(cls) -> ExifMeteringMode:
        '''Partial metering.'''
        ...
    
    @classmethod
    @property
    def OTHER(cls) -> ExifMeteringMode:
        '''For other modes.'''
        ...
    
    ...

class ExifOrientation:
    '''Exif image orientation.'''
    
    @classmethod
    @property
    def TOP_LEFT(cls) -> ExifOrientation:
        '''Top left. Default orientation.'''
        ...
    
    @classmethod
    @property
    def TOP_RIGHT(cls) -> ExifOrientation:
        '''Top right. Horizontally reversed.'''
        ...
    
    @classmethod
    @property
    def BOTTOM_RIGHT(cls) -> ExifOrientation:
        '''Bottom right. Rotated by 180 degrees.'''
        ...
    
    @classmethod
    @property
    def BOTTOM_LEFT(cls) -> ExifOrientation:
        '''Bottom left. Rotated by 180 degrees and then horizontally reversed.'''
        ...
    
    @classmethod
    @property
    def LEFT_TOP(cls) -> ExifOrientation:
        '''Left top. Rotated by 90 degrees counterclockwise and then horizontally reversed.'''
        ...
    
    @classmethod
    @property
    def RIGHT_TOP(cls) -> ExifOrientation:
        '''Right top. Rotated by 90 degrees clockwise.'''
        ...
    
    @classmethod
    @property
    def RIGHT_BOTTOM(cls) -> ExifOrientation:
        '''Right bottom. Rotated by 90 degrees clockwise and then horizontally reversed.'''
        ...
    
    @classmethod
    @property
    def LEFT_BOTTOM(cls) -> ExifOrientation:
        '''Left bottom. Rotated by 90 degrees counterclockwise.'''
        ...
    
    ...

class ExifSaturation:
    '''exif saturation enum.'''
    
    @classmethod
    @property
    def NORMAL(cls) -> ExifSaturation:
        '''Normal saturation.'''
        ...
    
    @classmethod
    @property
    def LOW(cls) -> ExifSaturation:
        '''Low saturation.'''
        ...
    
    @classmethod
    @property
    def HIGH(cls) -> ExifSaturation:
        '''High saturation.'''
        ...
    
    ...

class ExifSceneCaptureType:
    '''exif scene capture type enum.'''
    
    @classmethod
    @property
    def STANDARD(cls) -> ExifSceneCaptureType:
        '''Standard scene.'''
        ...
    
    @classmethod
    @property
    def LANDSCAPE(cls) -> ExifSceneCaptureType:
        '''Landscape scene.'''
        ...
    
    @classmethod
    @property
    def PORTRAIT(cls) -> ExifSceneCaptureType:
        '''Portrait scene.'''
        ...
    
    @classmethod
    @property
    def NIGHT_SCENE(cls) -> ExifSceneCaptureType:
        '''Night scene.'''
        ...
    
    ...

class ExifSensingMethod:
    '''exif sensing method enum.'''
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> ExifSensingMethod:
        '''Not defined.'''
        ...
    
    @classmethod
    @property
    def ONE_CHIP_COLOR_AREA(cls) -> ExifSensingMethod:
        '''One chip color area.'''
        ...
    
    @classmethod
    @property
    def TWO_CHIP_COLOR_AREA(cls) -> ExifSensingMethod:
        '''Two chip color area.'''
        ...
    
    @classmethod
    @property
    def THREE_CHIP_COLOR_AREA(cls) -> ExifSensingMethod:
        '''Three chip color area.'''
        ...
    
    @classmethod
    @property
    def COLORSEQUENTIALAREA(cls) -> ExifSensingMethod:
        '''Color Sequential area.'''
        ...
    
    @classmethod
    @property
    def TRILINEARSENSOR(cls) -> ExifSensingMethod:
        '''Trilinear sensor.'''
        ...
    
    @classmethod
    @property
    def COLORSEQUENTIALLINEAR(cls) -> ExifSensingMethod:
        '''Color sequential linear sensor.'''
        ...
    
    ...

class ExifSubjectDistanceRange:
    '''exif subject distance range enum.'''
    
    @classmethod
    @property
    def UNKNOWN(cls) -> ExifSubjectDistanceRange:
        '''Unknown subject distance range'''
        ...
    
    @classmethod
    @property
    def MACRO(cls) -> ExifSubjectDistanceRange:
        '''Macro range'''
        ...
    
    @classmethod
    @property
    def CLOSE_VIEW(cls) -> ExifSubjectDistanceRange:
        '''Close view.'''
        ...
    
    @classmethod
    @property
    def DISTANT_VIEW(cls) -> ExifSubjectDistanceRange:
        '''Distant view.'''
        ...
    
    ...

class ExifUnit:
    '''exif unit enum.'''
    
    @classmethod
    @property
    def NONE(cls) -> ExifUnit:
        '''Undefined units'''
        ...
    
    @classmethod
    @property
    def INCH(cls) -> ExifUnit:
        '''Inch units'''
        ...
    
    @classmethod
    @property
    def CM(cls) -> ExifUnit:
        '''Metric centimeter units'''
        ...
    
    ...

class ExifWhiteBalance:
    '''exif white balance enum.'''
    
    @classmethod
    @property
    def AUTO(cls) -> ExifWhiteBalance:
        '''Auto white balance'''
        ...
    
    @classmethod
    @property
    def MANUAL(cls) -> ExifWhiteBalance:
        '''Manual  white balance'''
        ...
    
    ...

class ExifYCbCrPositioning:
    '''exif y cb cr positioning enum.'''
    
    @classmethod
    @property
    def CENTERED(cls) -> ExifYCbCrPositioning:
        '''Centered YCbCr'''
        ...
    
    @classmethod
    @property
    def CO_SITED(cls) -> ExifYCbCrPositioning:
        '''Co-sited position'''
        ...
    
    ...

