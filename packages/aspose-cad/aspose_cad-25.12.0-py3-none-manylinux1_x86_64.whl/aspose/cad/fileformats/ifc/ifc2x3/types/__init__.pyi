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

class IfcAbsorbedDoseMeasure2X3(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcAbsorbedDoseMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcAccelerationMeasure2X3(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcAccelerationMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcActorSelect2X3(aspose.cad.fileformats.ifc.IfcSelect):
    '''IfcActorSelect'''
    
    @property
    def value(self) -> any:
        '''Gets the value.'''
        ...
    
    @value.setter
    def value(self, value : any):
        '''Sets the value.'''
        ...
    
    ...

class IfcAmountOfSubstanceMeasure2X3(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcAmountOfSubstanceMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcAngularVelocityMeasure2X3(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcAngularVelocityMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcAppliedValueSelect2X3(aspose.cad.fileformats.ifc.IfcSelect):
    '''IfcAppliedValueSelect'''
    
    @property
    def value(self) -> any:
        '''Gets the value.'''
        ...
    
    @value.setter
    def value(self, value : any):
        '''Sets the value.'''
        ...
    
    ...

class IfcAreaMeasure2X3(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcAreaMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcAxis2Placement2X3(aspose.cad.fileformats.ifc.IfcSelect):
    '''IfcAxis2Placement'''
    
    @property
    def value(self) -> any:
        '''Gets the value.'''
        ...
    
    @value.setter
    def value(self, value : any):
        '''Sets the value.'''
        ...
    
    ...

class IfcBoolean2X3(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcBoolean'''
    
    @property
    def value(self) -> bool:
        ...
    
    @value.setter
    def value(self, value : bool):
        ...
    
    ...

class IfcBooleanOperand2X3(aspose.cad.fileformats.ifc.IfcSelect):
    '''IfcBooleanOperand'''
    
    @property
    def value(self) -> any:
        '''Gets the value.'''
        ...
    
    @value.setter
    def value(self, value : any):
        '''Sets the value.'''
        ...
    
    ...

class IfcBoxAlignment2X3(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcBoxAlignment'''
    
    @property
    def value(self) -> aspose.cad.fileformats.ifc.ifc2x3.types.IfcLabel2X3:
        ...
    
    @value.setter
    def value(self, value : aspose.cad.fileformats.ifc.ifc2x3.types.IfcLabel2X3):
        ...
    
    ...

class IfcCharacterStyleSelect2X3(aspose.cad.fileformats.ifc.IfcSelect):
    '''IfcCharacterStyleSelect'''
    
    @property
    def value(self) -> any:
        '''Gets the value.'''
        ...
    
    @value.setter
    def value(self, value : any):
        '''Sets the value.'''
        ...
    
    ...

class IfcClassificationNotationSelect2X3(aspose.cad.fileformats.ifc.IfcSelect):
    '''IfcClassificationNotationSelect'''
    
    @property
    def value(self) -> any:
        '''Gets the value.'''
        ...
    
    @value.setter
    def value(self, value : any):
        '''Sets the value.'''
        ...
    
    ...

class IfcColour2X3(aspose.cad.fileformats.ifc.IfcSelect):
    '''IfcColour'''
    
    @property
    def value(self) -> any:
        '''Gets the value.'''
        ...
    
    @value.setter
    def value(self, value : any):
        '''Sets the value.'''
        ...
    
    ...

class IfcColourOrFactor2X3(aspose.cad.fileformats.ifc.IfcSelect):
    '''IfcColourOrFactor'''
    
    @property
    def value(self) -> any:
        '''Gets the value.'''
        ...
    
    @value.setter
    def value(self, value : any):
        '''Sets the value.'''
        ...
    
    ...

class IfcComplexNumber2X3(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcComplexNumber'''
    
    ...

class IfcCompoundPlaneAngleMeasure2X3(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcCompoundPlaneAngleMeasure'''
    
    ...

class IfcConditionCriterionSelect2X3(aspose.cad.fileformats.ifc.IfcSelect):
    '''IfcConditionCriterionSelect'''
    
    @property
    def value(self) -> any:
        '''Gets the value.'''
        ...
    
    @value.setter
    def value(self, value : any):
        '''Sets the value.'''
        ...
    
    ...

class IfcContextDependentMeasure2X3(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcContextDependentMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcCountMeasure2X3(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcCountMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcCsgSelect2X3(aspose.cad.fileformats.ifc.IfcSelect):
    '''IfcCsgSelect'''
    
    @property
    def value(self) -> any:
        '''Gets the value.'''
        ...
    
    @value.setter
    def value(self, value : any):
        '''Sets the value.'''
        ...
    
    ...

class IfcCurvatureMeasure2X3(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcCurvatureMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcCurveFontOrScaledCurveFontSelect2X3(aspose.cad.fileformats.ifc.IfcSelect):
    '''IfcCurveFontOrScaledCurveFontSelect'''
    
    @property
    def value(self) -> any:
        '''Gets the value.'''
        ...
    
    @value.setter
    def value(self, value : any):
        '''Sets the value.'''
        ...
    
    ...

class IfcCurveOrEdgeCurve2X3(aspose.cad.fileformats.ifc.IfcSelect):
    '''IfcCurveOrEdgeCurve'''
    
    @property
    def value(self) -> any:
        '''Gets the value.'''
        ...
    
    @value.setter
    def value(self, value : any):
        '''Sets the value.'''
        ...
    
    ...

class IfcCurveStyleFontSelect2X3(aspose.cad.fileformats.ifc.IfcSelect):
    '''IfcCurveStyleFontSelect'''
    
    @property
    def value(self) -> any:
        '''Gets the value.'''
        ...
    
    @value.setter
    def value(self, value : any):
        '''Sets the value.'''
        ...
    
    ...

class IfcDateTimeSelect2X3(aspose.cad.fileformats.ifc.IfcSelect):
    '''IfcDateTimeSelect'''
    
    @property
    def value(self) -> any:
        '''Gets the value.'''
        ...
    
    @value.setter
    def value(self, value : any):
        '''Sets the value.'''
        ...
    
    ...

class IfcDayInMonthNumber2X3(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcDayInMonthNumber'''
    
    @property
    def value(self) -> int:
        ...
    
    @value.setter
    def value(self, value : int):
        ...
    
    ...

class IfcDaylightSavingHour2X3(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcDaylightSavingHour'''
    
    @property
    def value(self) -> int:
        ...
    
    @value.setter
    def value(self, value : int):
        ...
    
    ...

class IfcDefinedSymbolSelect2X3(aspose.cad.fileformats.ifc.IfcSelect):
    '''IfcDefinedSymbolSelect'''
    
    @property
    def value(self) -> any:
        '''Gets the value.'''
        ...
    
    @value.setter
    def value(self, value : any):
        '''Sets the value.'''
        ...
    
    ...

class IfcDerivedMeasureValue2X3(aspose.cad.fileformats.ifc.IfcSelect):
    '''IfcDerivedMeasureValue'''
    
    @property
    def value(self) -> any:
        '''Gets the value.'''
        ...
    
    @value.setter
    def value(self, value : any):
        '''Sets the value.'''
        ...
    
    ...

class IfcDescriptiveMeasure2X3(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcDescriptiveMeasure'''
    
    @property
    def value(self) -> str:
        ...
    
    @value.setter
    def value(self, value : str):
        ...
    
    ...

class IfcDimensionCount2X3(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcDimensionCount'''
    
    @property
    def value(self) -> int:
        ...
    
    @value.setter
    def value(self, value : int):
        ...
    
    ...

class IfcDocumentSelect2X3(aspose.cad.fileformats.ifc.IfcSelect):
    '''IfcDocumentSelect'''
    
    @property
    def value(self) -> any:
        '''Gets the value.'''
        ...
    
    @value.setter
    def value(self, value : any):
        '''Sets the value.'''
        ...
    
    ...

class IfcDoseEquivalentMeasure2X3(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcDoseEquivalentMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcDraughtingCalloutElement2X3(aspose.cad.fileformats.ifc.IfcSelect):
    '''IfcDraughtingCalloutElement'''
    
    @property
    def value(self) -> any:
        '''Gets the value.'''
        ...
    
    @value.setter
    def value(self, value : any):
        '''Sets the value.'''
        ...
    
    ...

class IfcDynamicViscosityMeasure2X3(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcDynamicViscosityMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcElectricCapacitanceMeasure2X3(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcElectricCapacitanceMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcElectricChargeMeasure2X3(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcElectricChargeMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcElectricConductanceMeasure2X3(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcElectricConductanceMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcElectricCurrentMeasure2X3(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcElectricCurrentMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcElectricResistanceMeasure2X3(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcElectricResistanceMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcElectricVoltageMeasure2X3(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcElectricVoltageMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcEnergyMeasure2X3(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcEnergyMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcFillAreaStyleTileShapeSelect2X3(aspose.cad.fileformats.ifc.IfcSelect):
    '''IfcFillAreaStyleTileShapeSelect'''
    
    @property
    def value(self) -> any:
        '''Gets the value.'''
        ...
    
    @value.setter
    def value(self, value : any):
        '''Sets the value.'''
        ...
    
    ...

class IfcFillStyleSelect2X3(aspose.cad.fileformats.ifc.IfcSelect):
    '''IfcFillStyleSelect'''
    
    @property
    def value(self) -> any:
        '''Gets the value.'''
        ...
    
    @value.setter
    def value(self, value : any):
        '''Sets the value.'''
        ...
    
    ...

class IfcFontStyle2X3(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcFontStyle'''
    
    @property
    def value(self) -> str:
        ...
    
    @value.setter
    def value(self, value : str):
        ...
    
    ...

class IfcFontVariant2X3(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcFontVariant'''
    
    @property
    def value(self) -> str:
        ...
    
    @value.setter
    def value(self, value : str):
        ...
    
    ...

class IfcFontWeight2X3(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcFontWeight'''
    
    @property
    def value(self) -> str:
        ...
    
    @value.setter
    def value(self, value : str):
        ...
    
    ...

class IfcForceMeasure2X3(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcForceMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcFrequencyMeasure2X3(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcFrequencyMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcGeometricSetSelect2X3(aspose.cad.fileformats.ifc.IfcSelect):
    '''IfcGeometricSetSelect'''
    
    @property
    def value(self) -> any:
        '''Gets the value.'''
        ...
    
    @value.setter
    def value(self, value : any):
        '''Sets the value.'''
        ...
    
    ...

class IfcGloballyUniqueId2X3(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcGloballyUniqueId'''
    
    @property
    def value(self) -> str:
        ...
    
    @value.setter
    def value(self, value : str):
        ...
    
    ...

class IfcHatchLineDistanceSelect2X3(aspose.cad.fileformats.ifc.IfcSelect):
    '''IfcHatchLineDistanceSelect'''
    
    @property
    def value(self) -> any:
        '''Gets the value.'''
        ...
    
    @value.setter
    def value(self, value : any):
        '''Sets the value.'''
        ...
    
    ...

class IfcHeatFluxDensityMeasure2X3(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcHeatFluxDensityMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcHeatingValueMeasure2X3(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcHeatingValueMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcHourInDay2X3(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcHourInDay'''
    
    @property
    def value(self) -> int:
        ...
    
    @value.setter
    def value(self, value : int):
        ...
    
    ...

class IfcIdentifier2X3(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcIdentifier'''
    
    @property
    def value(self) -> str:
        ...
    
    @value.setter
    def value(self, value : str):
        ...
    
    ...

class IfcIlluminanceMeasure2X3(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcIlluminanceMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcInductanceMeasure2X3(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcInductanceMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcInteger2X3(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcInteger'''
    
    @property
    def value(self) -> int:
        ...
    
    @value.setter
    def value(self, value : int):
        ...
    
    ...

class IfcIntegerCountRateMeasure2X3(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcIntegerCountRateMeasure'''
    
    @property
    def value(self) -> int:
        ...
    
    @value.setter
    def value(self, value : int):
        ...
    
    ...

class IfcIonConcentrationMeasure2X3(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcIonConcentrationMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcIsothermalMoistureCapacityMeasure2X3(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcIsothermalMoistureCapacityMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcKinematicViscosityMeasure2X3(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcKinematicViscosityMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcLabel2X3(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcLabel'''
    
    @property
    def value(self) -> str:
        ...
    
    @value.setter
    def value(self, value : str):
        ...
    
    ...

class IfcLayeredItem2X3(aspose.cad.fileformats.ifc.IfcSelect):
    '''IfcLayeredItem'''
    
    @property
    def value(self) -> any:
        '''Gets the value.'''
        ...
    
    @value.setter
    def value(self, value : any):
        '''Sets the value.'''
        ...
    
    ...

class IfcLengthMeasure2X3(aspose.cad.fileformats.ifc.IIfcType):
    '''Partial IIfc entity class'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcLibrarySelect2X3(aspose.cad.fileformats.ifc.IfcSelect):
    '''IfcLibrarySelect'''
    
    @property
    def value(self) -> any:
        '''Gets the value.'''
        ...
    
    @value.setter
    def value(self, value : any):
        '''Sets the value.'''
        ...
    
    ...

class IfcLightDistributionDataSourceSelect2X3(aspose.cad.fileformats.ifc.IfcSelect):
    '''IfcLightDistributionDataSourceSelect'''
    
    @property
    def value(self) -> any:
        '''Gets the value.'''
        ...
    
    @value.setter
    def value(self, value : any):
        '''Sets the value.'''
        ...
    
    ...

class IfcLinearForceMeasure2X3(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcLinearForceMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcLinearMomentMeasure2X3(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcLinearMomentMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcLinearStiffnessMeasure2X3(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcLinearStiffnessMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcLinearVelocityMeasure2X3(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcLinearVelocityMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcLogical2X3(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcLogical'''
    
    @property
    def value(self) -> Optional[bool]:
        ...
    
    @value.setter
    def value(self, value : Optional[bool]):
        ...
    
    ...

class IfcLuminousFluxMeasure2X3(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcLuminousFluxMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcLuminousIntensityDistributionMeasure2X3(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcLuminousIntensityDistributionMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcLuminousIntensityMeasure2X3(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcLuminousIntensityMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcMagneticFluxDensityMeasure2X3(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcMagneticFluxDensityMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcMagneticFluxMeasure2X3(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcMagneticFluxMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcMassDensityMeasure2X3(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcMassDensityMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcMassFlowRateMeasure2X3(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcMassFlowRateMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcMassMeasure2X3(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcMassMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcMassPerLengthMeasure2X3(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcMassPerLengthMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcMaterialSelect2X3(aspose.cad.fileformats.ifc.IfcSelect):
    '''IfcMaterialSelect'''
    
    @property
    def value(self) -> any:
        '''Gets the value.'''
        ...
    
    @value.setter
    def value(self, value : any):
        '''Sets the value.'''
        ...
    
    ...

class IfcMeasureValue2X3(aspose.cad.fileformats.ifc.IfcSelect):
    '''IfcMeasureValue'''
    
    @property
    def value(self) -> any:
        '''Gets the value.'''
        ...
    
    @value.setter
    def value(self, value : any):
        '''Sets the value.'''
        ...
    
    ...

class IfcMetricValueSelect2X3(aspose.cad.fileformats.ifc.IfcSelect):
    '''IfcMetricValueSelect'''
    
    @property
    def value(self) -> any:
        '''Gets the value.'''
        ...
    
    @value.setter
    def value(self, value : any):
        '''Sets the value.'''
        ...
    
    ...

class IfcMinuteInHour2X3(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcMinuteInHour'''
    
    @property
    def value(self) -> int:
        ...
    
    @value.setter
    def value(self, value : int):
        ...
    
    ...

class IfcModulusOfElasticityMeasure2X3(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcModulusOfElasticityMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcModulusOfLinearSubgradeReactionMeasure2X3(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcModulusOfLinearSubgradeReactionMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcModulusOfRotationalSubgradeReactionMeasure2X3(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcModulusOfRotationalSubgradeReactionMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcModulusOfSubgradeReactionMeasure2X3(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcModulusOfSubgradeReactionMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcMoistureDiffusivityMeasure2X3(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcMoistureDiffusivityMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcMolecularWeightMeasure2X3(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcMolecularWeightMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcMomentOfInertiaMeasure2X3(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcMomentOfInertiaMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcMonetaryMeasure2X3(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcMonetaryMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcMonthInYearNumber2X3(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcMonthInYearNumber'''
    
    @property
    def value(self) -> int:
        ...
    
    @value.setter
    def value(self, value : int):
        ...
    
    ...

class IfcNormalisedRatioMeasure2X3(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcNormalisedRatioMeasure'''
    
    @property
    def value(self) -> aspose.cad.fileformats.ifc.ifc2x3.types.IfcRatioMeasure2X3:
        ...
    
    @value.setter
    def value(self, value : aspose.cad.fileformats.ifc.ifc2x3.types.IfcRatioMeasure2X3):
        ...
    
    ...

class IfcNumericMeasure2X3(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcNumericMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcObjectReferenceSelect2X3(aspose.cad.fileformats.ifc.IfcSelect):
    '''IfcObjectReferenceSelect'''
    
    @property
    def value(self) -> any:
        '''Gets the value.'''
        ...
    
    @value.setter
    def value(self, value : any):
        '''Sets the value.'''
        ...
    
    ...

class IfcOrientationSelect2X3(aspose.cad.fileformats.ifc.IfcSelect):
    '''IfcOrientationSelect'''
    
    @property
    def value(self) -> any:
        '''Gets the value.'''
        ...
    
    @value.setter
    def value(self, value : any):
        '''Sets the value.'''
        ...
    
    ...

class IfcPHMeasure2X3(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcPHMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcParameterValue2X3(aspose.cad.fileformats.ifc.IIfcType):
    '''Partial IIfc entity class'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcPlanarForceMeasure2X3(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcPlanarForceMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcPlaneAngleMeasure2X3(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcPlaneAngleMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcPointOrVertexPoint2X3(aspose.cad.fileformats.ifc.IfcSelect):
    '''IfcPointOrVertexPoint'''
    
    @property
    def value(self) -> any:
        '''Gets the value.'''
        ...
    
    @value.setter
    def value(self, value : any):
        '''Sets the value.'''
        ...
    
    ...

class IfcPositiveLengthMeasure2X3(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcPositiveLengthMeasure'''
    
    @property
    def value(self) -> aspose.cad.fileformats.ifc.ifc2x3.types.IfcLengthMeasure2X3:
        ...
    
    @value.setter
    def value(self, value : aspose.cad.fileformats.ifc.ifc2x3.types.IfcLengthMeasure2X3):
        ...
    
    ...

class IfcPositivePlaneAngleMeasure2X3(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcPositivePlaneAngleMeasure'''
    
    @property
    def value(self) -> aspose.cad.fileformats.ifc.ifc2x3.types.IfcPlaneAngleMeasure2X3:
        ...
    
    @value.setter
    def value(self, value : aspose.cad.fileformats.ifc.ifc2x3.types.IfcPlaneAngleMeasure2X3):
        ...
    
    ...

class IfcPositiveRatioMeasure2X3(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcPositiveRatioMeasure'''
    
    @property
    def value(self) -> aspose.cad.fileformats.ifc.ifc2x3.types.IfcRatioMeasure2X3:
        ...
    
    @value.setter
    def value(self, value : aspose.cad.fileformats.ifc.ifc2x3.types.IfcRatioMeasure2X3):
        ...
    
    ...

class IfcPowerMeasure2X3(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcPowerMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcPresentableText2X3(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcPresentableText'''
    
    @property
    def value(self) -> str:
        ...
    
    @value.setter
    def value(self, value : str):
        ...
    
    ...

class IfcPresentationStyleSelect2X3(aspose.cad.fileformats.ifc.IfcSelect):
    '''IfcPresentationStyleSelect'''
    
    @property
    def value(self) -> any:
        '''Gets the value.'''
        ...
    
    @value.setter
    def value(self, value : any):
        '''Sets the value.'''
        ...
    
    ...

class IfcPressureMeasure2X3(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcPressureMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcRadioActivityMeasure2X3(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcRadioActivityMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcRatioMeasure2X3(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcRatioMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcReal2X3(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcReal'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcRotationalFrequencyMeasure2X3(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcRotationalFrequencyMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcRotationalMassMeasure2X3(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcRotationalMassMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcRotationalStiffnessMeasure2X3(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcRotationalStiffnessMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcSecondInMinute2X3(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcSecondInMinute'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcSectionModulusMeasure2X3(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcSectionModulusMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcSectionalAreaIntegralMeasure2X3(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcSectionalAreaIntegralMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcShearModulusMeasure2X3(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcShearModulusMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcShell2X3(aspose.cad.fileformats.ifc.IfcSelect):
    '''IfcShell'''
    
    @property
    def value(self) -> any:
        '''Gets the value.'''
        ...
    
    @value.setter
    def value(self, value : any):
        '''Sets the value.'''
        ...
    
    ...

class IfcSimpleValue2X3(aspose.cad.fileformats.ifc.IfcSelect):
    '''IfcSimpleValue'''
    
    @property
    def value(self) -> any:
        '''Gets the value.'''
        ...
    
    @value.setter
    def value(self, value : any):
        '''Sets the value.'''
        ...
    
    ...

class IfcSizeSelect2X3(aspose.cad.fileformats.ifc.IfcSelect):
    '''IfcSizeSelect'''
    
    @property
    def value(self) -> any:
        '''Gets the value.'''
        ...
    
    @value.setter
    def value(self, value : any):
        '''Sets the value.'''
        ...
    
    ...

class IfcSolidAngleMeasure2X3(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcSolidAngleMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcSoundPowerMeasure2X3(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcSoundPowerMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcSoundPressureMeasure2X3(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcSoundPressureMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcSpecificHeatCapacityMeasure2X3(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcSpecificHeatCapacityMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcSpecularExponent2X3(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcSpecularExponent'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcSpecularHighlightSelect2X3(aspose.cad.fileformats.ifc.IfcSelect):
    '''IfcSpecularHighlightSelect'''
    
    @property
    def value(self) -> any:
        '''Gets the value.'''
        ...
    
    @value.setter
    def value(self, value : any):
        '''Sets the value.'''
        ...
    
    ...

class IfcSpecularRoughness2X3(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcSpecularRoughness'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcStructuralActivityAssignmentSelect2X3(aspose.cad.fileformats.ifc.IfcSelect):
    '''IfcStructuralActivityAssignmentSelect'''
    
    @property
    def value(self) -> any:
        '''Gets the value.'''
        ...
    
    @value.setter
    def value(self, value : any):
        '''Sets the value.'''
        ...
    
    ...

class IfcSurfaceOrFaceSurface2X3(aspose.cad.fileformats.ifc.IfcSelect):
    '''IfcSurfaceOrFaceSurface'''
    
    @property
    def value(self) -> any:
        '''Gets the value.'''
        ...
    
    @value.setter
    def value(self, value : any):
        '''Sets the value.'''
        ...
    
    ...

class IfcSurfaceStyleElementSelect2X3(aspose.cad.fileformats.ifc.IfcSelect):
    '''IfcSurfaceStyleElementSelect'''
    
    @property
    def value(self) -> any:
        '''Gets the value.'''
        ...
    
    @value.setter
    def value(self, value : any):
        '''Sets the value.'''
        ...
    
    ...

class IfcSymbolStyleSelect2X3(aspose.cad.fileformats.ifc.IfcSelect):
    '''IfcSymbolStyleSelect'''
    
    @property
    def value(self) -> any:
        '''Gets the value.'''
        ...
    
    @value.setter
    def value(self, value : any):
        '''Sets the value.'''
        ...
    
    ...

class IfcTemperatureGradientMeasure2X3(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcTemperatureGradientMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcText2X3(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcText'''
    
    @property
    def value(self) -> str:
        ...
    
    @value.setter
    def value(self, value : str):
        ...
    
    ...

class IfcTextAlignment2X3(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcTextAlignment'''
    
    @property
    def value(self) -> str:
        ...
    
    @value.setter
    def value(self, value : str):
        ...
    
    ...

class IfcTextDecoration2X3(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcTextDecoration'''
    
    @property
    def value(self) -> str:
        ...
    
    @value.setter
    def value(self, value : str):
        ...
    
    ...

class IfcTextFontName2X3(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcTextFontName'''
    
    @property
    def value(self) -> str:
        ...
    
    @value.setter
    def value(self, value : str):
        ...
    
    ...

class IfcTextFontSelect2X3(aspose.cad.fileformats.ifc.IfcSelect):
    '''IfcTextFontSelect'''
    
    @property
    def value(self) -> any:
        '''Gets the value.'''
        ...
    
    @value.setter
    def value(self, value : any):
        '''Sets the value.'''
        ...
    
    ...

class IfcTextStyleSelect2X3(aspose.cad.fileformats.ifc.IfcSelect):
    '''IfcTextStyleSelect'''
    
    @property
    def value(self) -> any:
        '''Gets the value.'''
        ...
    
    @value.setter
    def value(self, value : any):
        '''Sets the value.'''
        ...
    
    ...

class IfcTextTransformation2X3(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcTextTransformation'''
    
    @property
    def value(self) -> str:
        ...
    
    @value.setter
    def value(self, value : str):
        ...
    
    ...

class IfcThermalAdmittanceMeasure2X3(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcThermalAdmittanceMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcThermalConductivityMeasure2X3(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcThermalConductivityMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcThermalExpansionCoefficientMeasure2X3(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcThermalExpansionCoefficientMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcThermalResistanceMeasure2X3(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcThermalResistanceMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcThermalTransmittanceMeasure2X3(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcThermalTransmittanceMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcThermodynamicTemperatureMeasure2X3(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcThermodynamicTemperatureMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcTimeMeasure2X3(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcTimeMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcTimeStamp2X3(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcTimeStamp'''
    
    @property
    def value(self) -> int:
        ...
    
    @value.setter
    def value(self, value : int):
        ...
    
    ...

class IfcTorqueMeasure2X3(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcTorqueMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcTrimmingSelect2X3(aspose.cad.fileformats.ifc.IfcSelect):
    '''IfcTrimmingSelect'''
    
    @property
    def value(self) -> any:
        '''Gets the value.'''
        ...
    
    @value.setter
    def value(self, value : any):
        '''Sets the value.'''
        ...
    
    ...

class IfcUnit2X3(aspose.cad.fileformats.ifc.IfcSelect):
    '''IfcUnit'''
    
    @property
    def value(self) -> any:
        '''Gets the value.'''
        ...
    
    @value.setter
    def value(self, value : any):
        '''Sets the value.'''
        ...
    
    ...

class IfcValue2X3(aspose.cad.fileformats.ifc.IfcSelect):
    '''IfcValue'''
    
    @property
    def value(self) -> any:
        '''Gets the value.'''
        ...
    
    @value.setter
    def value(self, value : any):
        '''Sets the value.'''
        ...
    
    ...

class IfcVaporPermeabilityMeasure2X3(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcVaporPermeabilityMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcVectorOrDirection2X3(aspose.cad.fileformats.ifc.IfcSelect):
    '''IfcVectorOrDirection'''
    
    @property
    def value(self) -> any:
        '''Gets the value.'''
        ...
    
    @value.setter
    def value(self, value : any):
        '''Sets the value.'''
        ...
    
    ...

class IfcVolumeMeasure2X3(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcVolumeMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcVolumetricFlowRateMeasure2X3(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcVolumetricFlowRateMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcWarpingConstantMeasure2X3(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcWarpingConstantMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcWarpingMomentMeasure2X3(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcWarpingMomentMeasure'''
    
    @property
    def value(self) -> float:
        ...
    
    @value.setter
    def value(self, value : float):
        ...
    
    ...

class IfcYearNumber2X3(aspose.cad.fileformats.ifc.IIfcType):
    '''IfcYearNumber'''
    
    @property
    def value(self) -> int:
        ...
    
    @value.setter
    def value(self, value : int):
        ...
    
    ...

class IfcActionSourceTypeEnum2X3:
    '''IfcActionSourceTypeEnum'''
    
    @classmethod
    @property
    def DEAD_LOAD_G(cls) -> IfcActionSourceTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def COMPLETION_G1(cls) -> IfcActionSourceTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def LIVE_LOAD_Q(cls) -> IfcActionSourceTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def SNOW_S(cls) -> IfcActionSourceTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def WIND_W(cls) -> IfcActionSourceTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def PRESTRESSING_P(cls) -> IfcActionSourceTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def SETTLEMENT_U(cls) -> IfcActionSourceTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def TEMPERATURE_T(cls) -> IfcActionSourceTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def EARTHQUAKE_E(cls) -> IfcActionSourceTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def FIRE(cls) -> IfcActionSourceTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def IMPULSE(cls) -> IfcActionSourceTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def IMPACT(cls) -> IfcActionSourceTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def TRANSPORT(cls) -> IfcActionSourceTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def ERECTION(cls) -> IfcActionSourceTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def PROPPING(cls) -> IfcActionSourceTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def SYSTEM_IMPERFECTION(cls) -> IfcActionSourceTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def SHRINKAGE(cls) -> IfcActionSourceTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def CREEP(cls) -> IfcActionSourceTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def LACK_OF_FIT(cls) -> IfcActionSourceTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def BUOYANCY(cls) -> IfcActionSourceTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def ICE(cls) -> IfcActionSourceTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def CURRENT(cls) -> IfcActionSourceTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def WAVE(cls) -> IfcActionSourceTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def RAIN(cls) -> IfcActionSourceTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def BRAKES(cls) -> IfcActionSourceTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcActionSourceTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcActionSourceTypeEnum2X3:
        ...
    
    ...

class IfcActionTypeEnum2X3:
    '''IfcActionTypeEnum'''
    
    @classmethod
    @property
    def PERMANENT_G(cls) -> IfcActionTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def VARIABLE_Q(cls) -> IfcActionTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def EXTRAORDINARY_A(cls) -> IfcActionTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcActionTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcActionTypeEnum2X3:
        ...
    
    ...

class IfcActuatorTypeEnum2X3:
    '''IfcActuatorTypeEnum'''
    
    @classmethod
    @property
    def ELECTRICACTUATOR(cls) -> IfcActuatorTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def HANDOPERATEDACTUATOR(cls) -> IfcActuatorTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def HYDRAULICACTUATOR(cls) -> IfcActuatorTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def PNEUMATICACTUATOR(cls) -> IfcActuatorTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def THERMOSTATICACTUATOR(cls) -> IfcActuatorTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcActuatorTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcActuatorTypeEnum2X3:
        ...
    
    ...

class IfcAddressTypeEnum2X3:
    '''IfcAddressTypeEnum'''
    
    @classmethod
    @property
    def OFFICE(cls) -> IfcAddressTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def SITE(cls) -> IfcAddressTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def HOME(cls) -> IfcAddressTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def DISTRIBUTIONPOINT(cls) -> IfcAddressTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcAddressTypeEnum2X3:
        ...
    
    ...

class IfcAheadOrBehind2X3:
    '''IfcAheadOrBehind'''
    
    @classmethod
    @property
    def AHEAD(cls) -> IfcAheadOrBehind2X3:
        ...
    
    @classmethod
    @property
    def BEHIND(cls) -> IfcAheadOrBehind2X3:
        ...
    
    ...

class IfcAirTerminalBoxTypeEnum2X3:
    '''IfcAirTerminalBoxTypeEnum'''
    
    @classmethod
    @property
    def CONSTANTFLOW(cls) -> IfcAirTerminalBoxTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def VARIABLEFLOWPRESSUREDEPENDANT(cls) -> IfcAirTerminalBoxTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def VARIABLEFLOWPRESSUREINDEPENDANT(cls) -> IfcAirTerminalBoxTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcAirTerminalBoxTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcAirTerminalBoxTypeEnum2X3:
        ...
    
    ...

class IfcAirTerminalTypeEnum2X3:
    '''IfcAirTerminalTypeEnum'''
    
    @classmethod
    @property
    def GRILLE(cls) -> IfcAirTerminalTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def REGISTER(cls) -> IfcAirTerminalTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def DIFFUSER(cls) -> IfcAirTerminalTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def EYEBALL(cls) -> IfcAirTerminalTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def IRIS(cls) -> IfcAirTerminalTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def LINEARGRILLE(cls) -> IfcAirTerminalTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def LINEARDIFFUSER(cls) -> IfcAirTerminalTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcAirTerminalTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcAirTerminalTypeEnum2X3:
        ...
    
    ...

class IfcAirToAirHeatRecoveryTypeEnum2X3:
    '''IfcAirToAirHeatRecoveryTypeEnum'''
    
    @classmethod
    @property
    def FIXEDPLATECOUNTERFLOWEXCHANGER(cls) -> IfcAirToAirHeatRecoveryTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def FIXEDPLATECROSSFLOWEXCHANGER(cls) -> IfcAirToAirHeatRecoveryTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def FIXEDPLATEPARALLELFLOWEXCHANGER(cls) -> IfcAirToAirHeatRecoveryTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def ROTARYWHEEL(cls) -> IfcAirToAirHeatRecoveryTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def RUNAROUNDCOILLOOP(cls) -> IfcAirToAirHeatRecoveryTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def HEATPIPE(cls) -> IfcAirToAirHeatRecoveryTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def TWINTOWERENTHALPYRECOVERYLOOPS(cls) -> IfcAirToAirHeatRecoveryTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def THERMOSIPHONSEALEDTUBEHEATEXCHANGERS(cls) -> IfcAirToAirHeatRecoveryTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def THERMOSIPHONCOILTYPEHEATEXCHANGERS(cls) -> IfcAirToAirHeatRecoveryTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcAirToAirHeatRecoveryTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcAirToAirHeatRecoveryTypeEnum2X3:
        ...
    
    ...

class IfcAlarmTypeEnum2X3:
    '''IfcAlarmTypeEnum'''
    
    @classmethod
    @property
    def BELL(cls) -> IfcAlarmTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def BREAKGLASSBUTTON(cls) -> IfcAlarmTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def LIGHT(cls) -> IfcAlarmTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def MANUALPULLBOX(cls) -> IfcAlarmTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def SIREN(cls) -> IfcAlarmTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def WHISTLE(cls) -> IfcAlarmTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcAlarmTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcAlarmTypeEnum2X3:
        ...
    
    ...

class IfcAnalysisModelTypeEnum2X3:
    '''IfcAnalysisModelTypeEnum'''
    
    @classmethod
    @property
    def IN_PLANE_LOADING_2D(cls) -> IfcAnalysisModelTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def OUT_PLANE_LOADING_2D(cls) -> IfcAnalysisModelTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def LOADING_3D(cls) -> IfcAnalysisModelTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcAnalysisModelTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcAnalysisModelTypeEnum2X3:
        ...
    
    ...

class IfcAnalysisTheoryTypeEnum2X3:
    '''IfcAnalysisTheoryTypeEnum'''
    
    @classmethod
    @property
    def FIRST_ORDER_THEORY(cls) -> IfcAnalysisTheoryTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def SECOND_ORDER_THEORY(cls) -> IfcAnalysisTheoryTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def THIRD_ORDER_THEORY(cls) -> IfcAnalysisTheoryTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def FULL_NONLINEAR_THEORY(cls) -> IfcAnalysisTheoryTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcAnalysisTheoryTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcAnalysisTheoryTypeEnum2X3:
        ...
    
    ...

class IfcArithmeticOperatorEnum2X3:
    '''IfcArithmeticOperatorEnum'''
    
    @classmethod
    @property
    def ADD(cls) -> IfcArithmeticOperatorEnum2X3:
        ...
    
    @classmethod
    @property
    def DIVIDE(cls) -> IfcArithmeticOperatorEnum2X3:
        ...
    
    @classmethod
    @property
    def MULTIPLY(cls) -> IfcArithmeticOperatorEnum2X3:
        ...
    
    @classmethod
    @property
    def SUBTRACT(cls) -> IfcArithmeticOperatorEnum2X3:
        ...
    
    ...

class IfcAssemblyPlaceEnum2X3:
    '''IfcAssemblyPlaceEnum'''
    
    @classmethod
    @property
    def SITE(cls) -> IfcAssemblyPlaceEnum2X3:
        ...
    
    @classmethod
    @property
    def FACTORY(cls) -> IfcAssemblyPlaceEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcAssemblyPlaceEnum2X3:
        ...
    
    ...

class IfcBSplineCurveForm2X3:
    '''IfcBSplineCurveForm'''
    
    @classmethod
    @property
    def POLYLINE_FORM(cls) -> IfcBSplineCurveForm2X3:
        ...
    
    @classmethod
    @property
    def CIRCULAR_ARC(cls) -> IfcBSplineCurveForm2X3:
        ...
    
    @classmethod
    @property
    def ELLIPTIC_ARC(cls) -> IfcBSplineCurveForm2X3:
        ...
    
    @classmethod
    @property
    def PARABOLIC_ARC(cls) -> IfcBSplineCurveForm2X3:
        ...
    
    @classmethod
    @property
    def HYPERBOLIC_ARC(cls) -> IfcBSplineCurveForm2X3:
        ...
    
    @classmethod
    @property
    def UNSPECIFIED(cls) -> IfcBSplineCurveForm2X3:
        ...
    
    ...

class IfcBeamTypeEnum2X3:
    '''IfcBeamTypeEnum'''
    
    @classmethod
    @property
    def BEAM(cls) -> IfcBeamTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def JOIST(cls) -> IfcBeamTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def LINTEL(cls) -> IfcBeamTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def T_BEAM(cls) -> IfcBeamTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcBeamTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcBeamTypeEnum2X3:
        ...
    
    ...

class IfcBenchmarkEnum2X3:
    '''IfcBenchmarkEnum'''
    
    @classmethod
    @property
    def GREATERTHAN(cls) -> IfcBenchmarkEnum2X3:
        ...
    
    @classmethod
    @property
    def GREATERTHANOREQUALTO(cls) -> IfcBenchmarkEnum2X3:
        ...
    
    @classmethod
    @property
    def LESSTHAN(cls) -> IfcBenchmarkEnum2X3:
        ...
    
    @classmethod
    @property
    def LESSTHANOREQUALTO(cls) -> IfcBenchmarkEnum2X3:
        ...
    
    @classmethod
    @property
    def EQUALTO(cls) -> IfcBenchmarkEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTEQUALTO(cls) -> IfcBenchmarkEnum2X3:
        ...
    
    ...

class IfcBoilerTypeEnum2X3:
    '''IfcBoilerTypeEnum'''
    
    @classmethod
    @property
    def WATER(cls) -> IfcBoilerTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def STEAM(cls) -> IfcBoilerTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcBoilerTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcBoilerTypeEnum2X3:
        ...
    
    ...

class IfcBooleanOperator2X3:
    '''IfcBooleanOperator'''
    
    @classmethod
    @property
    def UNION(cls) -> IfcBooleanOperator2X3:
        ...
    
    @classmethod
    @property
    def INTERSECTION(cls) -> IfcBooleanOperator2X3:
        ...
    
    @classmethod
    @property
    def DIFFERENCE(cls) -> IfcBooleanOperator2X3:
        ...
    
    ...

class IfcBuildingElementProxyTypeEnum2X3:
    '''IfcBuildingElementProxyTypeEnum'''
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcBuildingElementProxyTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcBuildingElementProxyTypeEnum2X3:
        ...
    
    ...

class IfcCableCarrierFittingTypeEnum2X3:
    '''IfcCableCarrierFittingTypeEnum'''
    
    @classmethod
    @property
    def BEND(cls) -> IfcCableCarrierFittingTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def CROSS(cls) -> IfcCableCarrierFittingTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def REDUCER(cls) -> IfcCableCarrierFittingTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def TEE(cls) -> IfcCableCarrierFittingTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcCableCarrierFittingTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcCableCarrierFittingTypeEnum2X3:
        ...
    
    ...

class IfcCableCarrierSegmentTypeEnum2X3:
    '''IfcCableCarrierSegmentTypeEnum'''
    
    @classmethod
    @property
    def CABLELADDERSEGMENT(cls) -> IfcCableCarrierSegmentTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def CABLETRAYSEGMENT(cls) -> IfcCableCarrierSegmentTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def CABLETRUNKINGSEGMENT(cls) -> IfcCableCarrierSegmentTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def CONDUITSEGMENT(cls) -> IfcCableCarrierSegmentTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcCableCarrierSegmentTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcCableCarrierSegmentTypeEnum2X3:
        ...
    
    ...

class IfcCableSegmentTypeEnum2X3:
    '''IfcCableSegmentTypeEnum'''
    
    @classmethod
    @property
    def CABLESEGMENT(cls) -> IfcCableSegmentTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def CONDUCTORSEGMENT(cls) -> IfcCableSegmentTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcCableSegmentTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcCableSegmentTypeEnum2X3:
        ...
    
    ...

class IfcChangeActionEnum2X3:
    '''IfcChangeActionEnum'''
    
    @classmethod
    @property
    def NOCHANGE(cls) -> IfcChangeActionEnum2X3:
        ...
    
    @classmethod
    @property
    def MODIFIED(cls) -> IfcChangeActionEnum2X3:
        ...
    
    @classmethod
    @property
    def ADDED(cls) -> IfcChangeActionEnum2X3:
        ...
    
    @classmethod
    @property
    def DELETED(cls) -> IfcChangeActionEnum2X3:
        ...
    
    @classmethod
    @property
    def MODIFIEDADDED(cls) -> IfcChangeActionEnum2X3:
        ...
    
    @classmethod
    @property
    def MODIFIEDDELETED(cls) -> IfcChangeActionEnum2X3:
        ...
    
    ...

class IfcChillerTypeEnum2X3:
    '''IfcChillerTypeEnum'''
    
    @classmethod
    @property
    def AIRCOOLED(cls) -> IfcChillerTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def WATERCOOLED(cls) -> IfcChillerTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def HEATRECOVERY(cls) -> IfcChillerTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcChillerTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcChillerTypeEnum2X3:
        ...
    
    ...

class IfcCoilTypeEnum2X3:
    '''IfcCoilTypeEnum'''
    
    @classmethod
    @property
    def DXCOOLINGCOIL(cls) -> IfcCoilTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def WATERCOOLINGCOIL(cls) -> IfcCoilTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def STEAMHEATINGCOIL(cls) -> IfcCoilTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def WATERHEATINGCOIL(cls) -> IfcCoilTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def ELECTRICHEATINGCOIL(cls) -> IfcCoilTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def GASHEATINGCOIL(cls) -> IfcCoilTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcCoilTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcCoilTypeEnum2X3:
        ...
    
    ...

class IfcColumnTypeEnum2X3:
    '''IfcColumnTypeEnum'''
    
    @classmethod
    @property
    def COLUMN(cls) -> IfcColumnTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcColumnTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcColumnTypeEnum2X3:
        ...
    
    ...

class IfcCompressorTypeEnum2X3:
    '''IfcCompressorTypeEnum'''
    
    @classmethod
    @property
    def DYNAMIC(cls) -> IfcCompressorTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def RECIPROCATING(cls) -> IfcCompressorTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def ROTARY(cls) -> IfcCompressorTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def SCROLL(cls) -> IfcCompressorTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def TROCHOIDAL(cls) -> IfcCompressorTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def SINGLESTAGE(cls) -> IfcCompressorTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def BOOSTER(cls) -> IfcCompressorTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def OPENTYPE(cls) -> IfcCompressorTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def HERMETIC(cls) -> IfcCompressorTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def SEMIHERMETIC(cls) -> IfcCompressorTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def WELDEDSHELLHERMETIC(cls) -> IfcCompressorTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def ROLLINGPISTON(cls) -> IfcCompressorTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def ROTARYVANE(cls) -> IfcCompressorTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def SINGLESCREW(cls) -> IfcCompressorTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def TWINSCREW(cls) -> IfcCompressorTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcCompressorTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcCompressorTypeEnum2X3:
        ...
    
    ...

class IfcCondenserTypeEnum2X3:
    '''IfcCondenserTypeEnum'''
    
    @classmethod
    @property
    def WATERCOOLEDSHELLTUBE(cls) -> IfcCondenserTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def WATERCOOLEDSHELLCOIL(cls) -> IfcCondenserTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def WATERCOOLEDTUBEINTUBE(cls) -> IfcCondenserTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def WATERCOOLEDBRAZEDPLATE(cls) -> IfcCondenserTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def AIRCOOLED(cls) -> IfcCondenserTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def EVAPORATIVECOOLED(cls) -> IfcCondenserTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcCondenserTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcCondenserTypeEnum2X3:
        ...
    
    ...

class IfcConnectionTypeEnum2X3:
    '''IfcConnectionTypeEnum'''
    
    @classmethod
    @property
    def ATPATH(cls) -> IfcConnectionTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def ATSTART(cls) -> IfcConnectionTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def ATEND(cls) -> IfcConnectionTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcConnectionTypeEnum2X3:
        ...
    
    ...

class IfcConstraintEnum2X3:
    '''IfcConstraintEnum'''
    
    @classmethod
    @property
    def HARD(cls) -> IfcConstraintEnum2X3:
        ...
    
    @classmethod
    @property
    def SOFT(cls) -> IfcConstraintEnum2X3:
        ...
    
    @classmethod
    @property
    def ADVISORY(cls) -> IfcConstraintEnum2X3:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcConstraintEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcConstraintEnum2X3:
        ...
    
    ...

class IfcControllerTypeEnum2X3:
    '''IfcControllerTypeEnum'''
    
    @classmethod
    @property
    def FLOATING(cls) -> IfcControllerTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def PROPORTIONAL(cls) -> IfcControllerTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def PROPORTIONALINTEGRAL(cls) -> IfcControllerTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def PROPORTIONALINTEGRALDERIVATIVE(cls) -> IfcControllerTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def TIMEDTWOPOSITION(cls) -> IfcControllerTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def TWOPOSITION(cls) -> IfcControllerTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcControllerTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcControllerTypeEnum2X3:
        ...
    
    ...

class IfcCooledBeamTypeEnum2X3:
    '''IfcCooledBeamTypeEnum'''
    
    @classmethod
    @property
    def ACTIVE(cls) -> IfcCooledBeamTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def PASSIVE(cls) -> IfcCooledBeamTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcCooledBeamTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcCooledBeamTypeEnum2X3:
        ...
    
    ...

class IfcCoolingTowerTypeEnum2X3:
    '''IfcCoolingTowerTypeEnum'''
    
    @classmethod
    @property
    def NATURALDRAFT(cls) -> IfcCoolingTowerTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def MECHANICALINDUCEDDRAFT(cls) -> IfcCoolingTowerTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def MECHANICALFORCEDDRAFT(cls) -> IfcCoolingTowerTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcCoolingTowerTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcCoolingTowerTypeEnum2X3:
        ...
    
    ...

class IfcCostScheduleTypeEnum2X3:
    '''IfcCostScheduleTypeEnum'''
    
    @classmethod
    @property
    def BUDGET(cls) -> IfcCostScheduleTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def COSTPLAN(cls) -> IfcCostScheduleTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def ESTIMATE(cls) -> IfcCostScheduleTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def TENDER(cls) -> IfcCostScheduleTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def PRICEDBILLOFQUANTITIES(cls) -> IfcCostScheduleTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def UNPRICEDBILLOFQUANTITIES(cls) -> IfcCostScheduleTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def SCHEDULEOFRATES(cls) -> IfcCostScheduleTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcCostScheduleTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcCostScheduleTypeEnum2X3:
        ...
    
    ...

class IfcCoveringTypeEnum2X3:
    '''IfcCoveringTypeEnum'''
    
    @classmethod
    @property
    def CEILING(cls) -> IfcCoveringTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def FLOORING(cls) -> IfcCoveringTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def CLADDING(cls) -> IfcCoveringTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def ROOFING(cls) -> IfcCoveringTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def INSULATION(cls) -> IfcCoveringTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def MEMBRANE(cls) -> IfcCoveringTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def SLEEVING(cls) -> IfcCoveringTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def WRAPPING(cls) -> IfcCoveringTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcCoveringTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcCoveringTypeEnum2X3:
        ...
    
    ...

class IfcCurrencyEnum2X3:
    '''IfcCurrencyEnum'''
    
    @classmethod
    @property
    def AED(cls) -> IfcCurrencyEnum2X3:
        ...
    
    @classmethod
    @property
    def AES(cls) -> IfcCurrencyEnum2X3:
        ...
    
    @classmethod
    @property
    def ATS(cls) -> IfcCurrencyEnum2X3:
        ...
    
    @classmethod
    @property
    def AUD(cls) -> IfcCurrencyEnum2X3:
        ...
    
    @classmethod
    @property
    def BBD(cls) -> IfcCurrencyEnum2X3:
        ...
    
    @classmethod
    @property
    def BEG(cls) -> IfcCurrencyEnum2X3:
        ...
    
    @classmethod
    @property
    def BGL(cls) -> IfcCurrencyEnum2X3:
        ...
    
    @classmethod
    @property
    def BHD(cls) -> IfcCurrencyEnum2X3:
        ...
    
    @classmethod
    @property
    def BMD(cls) -> IfcCurrencyEnum2X3:
        ...
    
    @classmethod
    @property
    def BND(cls) -> IfcCurrencyEnum2X3:
        ...
    
    @classmethod
    @property
    def BRL(cls) -> IfcCurrencyEnum2X3:
        ...
    
    @classmethod
    @property
    def BSD(cls) -> IfcCurrencyEnum2X3:
        ...
    
    @classmethod
    @property
    def BWP(cls) -> IfcCurrencyEnum2X3:
        ...
    
    @classmethod
    @property
    def BZD(cls) -> IfcCurrencyEnum2X3:
        ...
    
    @classmethod
    @property
    def CAD(cls) -> IfcCurrencyEnum2X3:
        ...
    
    @classmethod
    @property
    def CBD(cls) -> IfcCurrencyEnum2X3:
        ...
    
    @classmethod
    @property
    def CHF(cls) -> IfcCurrencyEnum2X3:
        ...
    
    @classmethod
    @property
    def CLP(cls) -> IfcCurrencyEnum2X3:
        ...
    
    @classmethod
    @property
    def CNY(cls) -> IfcCurrencyEnum2X3:
        ...
    
    @classmethod
    @property
    def CYS(cls) -> IfcCurrencyEnum2X3:
        ...
    
    @classmethod
    @property
    def CZK(cls) -> IfcCurrencyEnum2X3:
        ...
    
    @classmethod
    @property
    def DDP(cls) -> IfcCurrencyEnum2X3:
        ...
    
    @classmethod
    @property
    def DEM(cls) -> IfcCurrencyEnum2X3:
        ...
    
    @classmethod
    @property
    def DKK(cls) -> IfcCurrencyEnum2X3:
        ...
    
    @classmethod
    @property
    def EGL(cls) -> IfcCurrencyEnum2X3:
        ...
    
    @classmethod
    @property
    def EST(cls) -> IfcCurrencyEnum2X3:
        ...
    
    @classmethod
    @property
    def EUR(cls) -> IfcCurrencyEnum2X3:
        ...
    
    @classmethod
    @property
    def FAK(cls) -> IfcCurrencyEnum2X3:
        ...
    
    @classmethod
    @property
    def FIM(cls) -> IfcCurrencyEnum2X3:
        ...
    
    @classmethod
    @property
    def FJD(cls) -> IfcCurrencyEnum2X3:
        ...
    
    @classmethod
    @property
    def FKP(cls) -> IfcCurrencyEnum2X3:
        ...
    
    @classmethod
    @property
    def FRF(cls) -> IfcCurrencyEnum2X3:
        ...
    
    @classmethod
    @property
    def GBP(cls) -> IfcCurrencyEnum2X3:
        ...
    
    @classmethod
    @property
    def GIP(cls) -> IfcCurrencyEnum2X3:
        ...
    
    @classmethod
    @property
    def GMD(cls) -> IfcCurrencyEnum2X3:
        ...
    
    @classmethod
    @property
    def GRX(cls) -> IfcCurrencyEnum2X3:
        ...
    
    @classmethod
    @property
    def HKD(cls) -> IfcCurrencyEnum2X3:
        ...
    
    @classmethod
    @property
    def HUF(cls) -> IfcCurrencyEnum2X3:
        ...
    
    @classmethod
    @property
    def ICK(cls) -> IfcCurrencyEnum2X3:
        ...
    
    @classmethod
    @property
    def IDR(cls) -> IfcCurrencyEnum2X3:
        ...
    
    @classmethod
    @property
    def ILS(cls) -> IfcCurrencyEnum2X3:
        ...
    
    @classmethod
    @property
    def INR(cls) -> IfcCurrencyEnum2X3:
        ...
    
    @classmethod
    @property
    def IRP(cls) -> IfcCurrencyEnum2X3:
        ...
    
    @classmethod
    @property
    def ITL(cls) -> IfcCurrencyEnum2X3:
        ...
    
    @classmethod
    @property
    def JMD(cls) -> IfcCurrencyEnum2X3:
        ...
    
    @classmethod
    @property
    def JOD(cls) -> IfcCurrencyEnum2X3:
        ...
    
    @classmethod
    @property
    def JPY(cls) -> IfcCurrencyEnum2X3:
        ...
    
    @classmethod
    @property
    def KES(cls) -> IfcCurrencyEnum2X3:
        ...
    
    @classmethod
    @property
    def KRW(cls) -> IfcCurrencyEnum2X3:
        ...
    
    @classmethod
    @property
    def KWD(cls) -> IfcCurrencyEnum2X3:
        ...
    
    @classmethod
    @property
    def KYD(cls) -> IfcCurrencyEnum2X3:
        ...
    
    @classmethod
    @property
    def LKR(cls) -> IfcCurrencyEnum2X3:
        ...
    
    @classmethod
    @property
    def LUF(cls) -> IfcCurrencyEnum2X3:
        ...
    
    @classmethod
    @property
    def MTL(cls) -> IfcCurrencyEnum2X3:
        ...
    
    @classmethod
    @property
    def MUR(cls) -> IfcCurrencyEnum2X3:
        ...
    
    @classmethod
    @property
    def MXN(cls) -> IfcCurrencyEnum2X3:
        ...
    
    @classmethod
    @property
    def MYR(cls) -> IfcCurrencyEnum2X3:
        ...
    
    @classmethod
    @property
    def NLG(cls) -> IfcCurrencyEnum2X3:
        ...
    
    @classmethod
    @property
    def NZD(cls) -> IfcCurrencyEnum2X3:
        ...
    
    @classmethod
    @property
    def OMR(cls) -> IfcCurrencyEnum2X3:
        ...
    
    @classmethod
    @property
    def PGK(cls) -> IfcCurrencyEnum2X3:
        ...
    
    @classmethod
    @property
    def PHP(cls) -> IfcCurrencyEnum2X3:
        ...
    
    @classmethod
    @property
    def PKR(cls) -> IfcCurrencyEnum2X3:
        ...
    
    @classmethod
    @property
    def PLN(cls) -> IfcCurrencyEnum2X3:
        ...
    
    @classmethod
    @property
    def PTN(cls) -> IfcCurrencyEnum2X3:
        ...
    
    @classmethod
    @property
    def QAR(cls) -> IfcCurrencyEnum2X3:
        ...
    
    @classmethod
    @property
    def RUR(cls) -> IfcCurrencyEnum2X3:
        ...
    
    @classmethod
    @property
    def SAR(cls) -> IfcCurrencyEnum2X3:
        ...
    
    @classmethod
    @property
    def SCR(cls) -> IfcCurrencyEnum2X3:
        ...
    
    @classmethod
    @property
    def SEK(cls) -> IfcCurrencyEnum2X3:
        ...
    
    @classmethod
    @property
    def SGD(cls) -> IfcCurrencyEnum2X3:
        ...
    
    @classmethod
    @property
    def SKP(cls) -> IfcCurrencyEnum2X3:
        ...
    
    @classmethod
    @property
    def THB(cls) -> IfcCurrencyEnum2X3:
        ...
    
    @classmethod
    @property
    def TRL(cls) -> IfcCurrencyEnum2X3:
        ...
    
    @classmethod
    @property
    def TTD(cls) -> IfcCurrencyEnum2X3:
        ...
    
    @classmethod
    @property
    def TWD(cls) -> IfcCurrencyEnum2X3:
        ...
    
    @classmethod
    @property
    def USD(cls) -> IfcCurrencyEnum2X3:
        ...
    
    @classmethod
    @property
    def VEB(cls) -> IfcCurrencyEnum2X3:
        ...
    
    @classmethod
    @property
    def VND(cls) -> IfcCurrencyEnum2X3:
        ...
    
    @classmethod
    @property
    def XEU(cls) -> IfcCurrencyEnum2X3:
        ...
    
    @classmethod
    @property
    def ZAR(cls) -> IfcCurrencyEnum2X3:
        ...
    
    @classmethod
    @property
    def ZWD(cls) -> IfcCurrencyEnum2X3:
        ...
    
    @classmethod
    @property
    def NOK(cls) -> IfcCurrencyEnum2X3:
        ...
    
    ...

class IfcCurtainWallTypeEnum2X3:
    '''IfcCurtainWallTypeEnum'''
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcCurtainWallTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcCurtainWallTypeEnum2X3:
        ...
    
    ...

class IfcDamperTypeEnum2X3:
    '''IfcDamperTypeEnum'''
    
    @classmethod
    @property
    def CONTROLDAMPER(cls) -> IfcDamperTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def FIREDAMPER(cls) -> IfcDamperTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def SMOKEDAMPER(cls) -> IfcDamperTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def FIRESMOKEDAMPER(cls) -> IfcDamperTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def BACKDRAFTDAMPER(cls) -> IfcDamperTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def RELIEFDAMPER(cls) -> IfcDamperTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def BLASTDAMPER(cls) -> IfcDamperTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def GRAVITYDAMPER(cls) -> IfcDamperTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def GRAVITYRELIEFDAMPER(cls) -> IfcDamperTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def BALANCINGDAMPER(cls) -> IfcDamperTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def FUMEHOODEXHAUST(cls) -> IfcDamperTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcDamperTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcDamperTypeEnum2X3:
        ...
    
    ...

class IfcDataOriginEnum2X3:
    '''IfcDataOriginEnum'''
    
    @classmethod
    @property
    def MEASURED(cls) -> IfcDataOriginEnum2X3:
        ...
    
    @classmethod
    @property
    def PREDICTED(cls) -> IfcDataOriginEnum2X3:
        ...
    
    @classmethod
    @property
    def SIMULATED(cls) -> IfcDataOriginEnum2X3:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcDataOriginEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcDataOriginEnum2X3:
        ...
    
    ...

class IfcDerivedUnitEnum2X3:
    '''IfcDerivedUnitEnum'''
    
    @classmethod
    @property
    def ANGULARVELOCITYUNIT(cls) -> IfcDerivedUnitEnum2X3:
        ...
    
    @classmethod
    @property
    def COMPOUNDPLANEANGLEUNIT(cls) -> IfcDerivedUnitEnum2X3:
        ...
    
    @classmethod
    @property
    def DYNAMICVISCOSITYUNIT(cls) -> IfcDerivedUnitEnum2X3:
        ...
    
    @classmethod
    @property
    def HEATFLUXDENSITYUNIT(cls) -> IfcDerivedUnitEnum2X3:
        ...
    
    @classmethod
    @property
    def INTEGERCOUNTRATEUNIT(cls) -> IfcDerivedUnitEnum2X3:
        ...
    
    @classmethod
    @property
    def ISOTHERMALMOISTURECAPACITYUNIT(cls) -> IfcDerivedUnitEnum2X3:
        ...
    
    @classmethod
    @property
    def KINEMATICVISCOSITYUNIT(cls) -> IfcDerivedUnitEnum2X3:
        ...
    
    @classmethod
    @property
    def LINEARVELOCITYUNIT(cls) -> IfcDerivedUnitEnum2X3:
        ...
    
    @classmethod
    @property
    def MASSDENSITYUNIT(cls) -> IfcDerivedUnitEnum2X3:
        ...
    
    @classmethod
    @property
    def MASSFLOWRATEUNIT(cls) -> IfcDerivedUnitEnum2X3:
        ...
    
    @classmethod
    @property
    def MOISTUREDIFFUSIVITYUNIT(cls) -> IfcDerivedUnitEnum2X3:
        ...
    
    @classmethod
    @property
    def MOLECULARWEIGHTUNIT(cls) -> IfcDerivedUnitEnum2X3:
        ...
    
    @classmethod
    @property
    def SPECIFICHEATCAPACITYUNIT(cls) -> IfcDerivedUnitEnum2X3:
        ...
    
    @classmethod
    @property
    def THERMALADMITTANCEUNIT(cls) -> IfcDerivedUnitEnum2X3:
        ...
    
    @classmethod
    @property
    def THERMALCONDUCTANCEUNIT(cls) -> IfcDerivedUnitEnum2X3:
        ...
    
    @classmethod
    @property
    def THERMALRESISTANCEUNIT(cls) -> IfcDerivedUnitEnum2X3:
        ...
    
    @classmethod
    @property
    def THERMALTRANSMITTANCEUNIT(cls) -> IfcDerivedUnitEnum2X3:
        ...
    
    @classmethod
    @property
    def VAPORPERMEABILITYUNIT(cls) -> IfcDerivedUnitEnum2X3:
        ...
    
    @classmethod
    @property
    def VOLUMETRICFLOWRATEUNIT(cls) -> IfcDerivedUnitEnum2X3:
        ...
    
    @classmethod
    @property
    def ROTATIONALFREQUENCYUNIT(cls) -> IfcDerivedUnitEnum2X3:
        ...
    
    @classmethod
    @property
    def TORQUEUNIT(cls) -> IfcDerivedUnitEnum2X3:
        ...
    
    @classmethod
    @property
    def MOMENTOFINERTIAUNIT(cls) -> IfcDerivedUnitEnum2X3:
        ...
    
    @classmethod
    @property
    def LINEARMOMENTUNIT(cls) -> IfcDerivedUnitEnum2X3:
        ...
    
    @classmethod
    @property
    def LINEARFORCEUNIT(cls) -> IfcDerivedUnitEnum2X3:
        ...
    
    @classmethod
    @property
    def PLANARFORCEUNIT(cls) -> IfcDerivedUnitEnum2X3:
        ...
    
    @classmethod
    @property
    def MODULUSOFELASTICITYUNIT(cls) -> IfcDerivedUnitEnum2X3:
        ...
    
    @classmethod
    @property
    def SHEARMODULUSUNIT(cls) -> IfcDerivedUnitEnum2X3:
        ...
    
    @classmethod
    @property
    def LINEARSTIFFNESSUNIT(cls) -> IfcDerivedUnitEnum2X3:
        ...
    
    @classmethod
    @property
    def ROTATIONALSTIFFNESSUNIT(cls) -> IfcDerivedUnitEnum2X3:
        ...
    
    @classmethod
    @property
    def MODULUSOFSUBGRADEREACTIONUNIT(cls) -> IfcDerivedUnitEnum2X3:
        ...
    
    @classmethod
    @property
    def ACCELERATIONUNIT(cls) -> IfcDerivedUnitEnum2X3:
        ...
    
    @classmethod
    @property
    def CURVATUREUNIT(cls) -> IfcDerivedUnitEnum2X3:
        ...
    
    @classmethod
    @property
    def HEATINGVALUEUNIT(cls) -> IfcDerivedUnitEnum2X3:
        ...
    
    @classmethod
    @property
    def IONCONCENTRATIONUNIT(cls) -> IfcDerivedUnitEnum2X3:
        ...
    
    @classmethod
    @property
    def LUMINOUSINTENSITYDISTRIBUTIONUNIT(cls) -> IfcDerivedUnitEnum2X3:
        ...
    
    @classmethod
    @property
    def MASSPERLENGTHUNIT(cls) -> IfcDerivedUnitEnum2X3:
        ...
    
    @classmethod
    @property
    def MODULUSOFLINEARSUBGRADEREACTIONUNIT(cls) -> IfcDerivedUnitEnum2X3:
        ...
    
    @classmethod
    @property
    def MODULUSOFROTATIONALSUBGRADEREACTIONUNIT(cls) -> IfcDerivedUnitEnum2X3:
        ...
    
    @classmethod
    @property
    def PHUNIT(cls) -> IfcDerivedUnitEnum2X3:
        ...
    
    @classmethod
    @property
    def ROTATIONALMASSUNIT(cls) -> IfcDerivedUnitEnum2X3:
        ...
    
    @classmethod
    @property
    def SECTIONAREAINTEGRALUNIT(cls) -> IfcDerivedUnitEnum2X3:
        ...
    
    @classmethod
    @property
    def SECTIONMODULUSUNIT(cls) -> IfcDerivedUnitEnum2X3:
        ...
    
    @classmethod
    @property
    def SOUNDPOWERUNIT(cls) -> IfcDerivedUnitEnum2X3:
        ...
    
    @classmethod
    @property
    def SOUNDPRESSUREUNIT(cls) -> IfcDerivedUnitEnum2X3:
        ...
    
    @classmethod
    @property
    def TEMPERATUREGRADIENTUNIT(cls) -> IfcDerivedUnitEnum2X3:
        ...
    
    @classmethod
    @property
    def THERMALEXPANSIONCOEFFICIENTUNIT(cls) -> IfcDerivedUnitEnum2X3:
        ...
    
    @classmethod
    @property
    def WARPINGCONSTANTUNIT(cls) -> IfcDerivedUnitEnum2X3:
        ...
    
    @classmethod
    @property
    def WARPINGMOMENTUNIT(cls) -> IfcDerivedUnitEnum2X3:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcDerivedUnitEnum2X3:
        ...
    
    ...

class IfcDimensionExtentUsage2X3:
    '''IfcDimensionExtentUsage'''
    
    @classmethod
    @property
    def ORIGIN(cls) -> IfcDimensionExtentUsage2X3:
        ...
    
    @classmethod
    @property
    def TARGET(cls) -> IfcDimensionExtentUsage2X3:
        ...
    
    ...

class IfcDirectionSenseEnum2X3:
    '''IfcDirectionSenseEnum'''
    
    @classmethod
    @property
    def POSITIVE(cls) -> IfcDirectionSenseEnum2X3:
        ...
    
    @classmethod
    @property
    def NEGATIVE(cls) -> IfcDirectionSenseEnum2X3:
        ...
    
    ...

class IfcDistributionChamberElementTypeEnum2X3:
    '''IfcDistributionChamberElementTypeEnum'''
    
    @classmethod
    @property
    def FORMEDDUCT(cls) -> IfcDistributionChamberElementTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def INSPECTIONCHAMBER(cls) -> IfcDistributionChamberElementTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def INSPECTIONPIT(cls) -> IfcDistributionChamberElementTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def MANHOLE(cls) -> IfcDistributionChamberElementTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def METERCHAMBER(cls) -> IfcDistributionChamberElementTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def SUMP(cls) -> IfcDistributionChamberElementTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def TRENCH(cls) -> IfcDistributionChamberElementTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def VALVECHAMBER(cls) -> IfcDistributionChamberElementTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcDistributionChamberElementTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcDistributionChamberElementTypeEnum2X3:
        ...
    
    ...

class IfcDocumentConfidentialityEnum2X3:
    '''IfcDocumentConfidentialityEnum'''
    
    @classmethod
    @property
    def PUBLIC(cls) -> IfcDocumentConfidentialityEnum2X3:
        ...
    
    @classmethod
    @property
    def RESTRICTED(cls) -> IfcDocumentConfidentialityEnum2X3:
        ...
    
    @classmethod
    @property
    def CONFIDENTIAL(cls) -> IfcDocumentConfidentialityEnum2X3:
        ...
    
    @classmethod
    @property
    def PERSONAL(cls) -> IfcDocumentConfidentialityEnum2X3:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcDocumentConfidentialityEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcDocumentConfidentialityEnum2X3:
        ...
    
    ...

class IfcDocumentStatusEnum2X3:
    '''IfcDocumentStatusEnum'''
    
    @classmethod
    @property
    def DRAFT(cls) -> IfcDocumentStatusEnum2X3:
        ...
    
    @classmethod
    @property
    def FINALDRAFT(cls) -> IfcDocumentStatusEnum2X3:
        ...
    
    @classmethod
    @property
    def FINAL(cls) -> IfcDocumentStatusEnum2X3:
        ...
    
    @classmethod
    @property
    def REVISION(cls) -> IfcDocumentStatusEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcDocumentStatusEnum2X3:
        ...
    
    ...

class IfcDoorPanelOperationEnum2X3:
    '''IfcDoorPanelOperationEnum'''
    
    @classmethod
    @property
    def SWINGING(cls) -> IfcDoorPanelOperationEnum2X3:
        ...
    
    @classmethod
    @property
    def DOUBLE_ACTING(cls) -> IfcDoorPanelOperationEnum2X3:
        ...
    
    @classmethod
    @property
    def SLIDING(cls) -> IfcDoorPanelOperationEnum2X3:
        ...
    
    @classmethod
    @property
    def FOLDING(cls) -> IfcDoorPanelOperationEnum2X3:
        ...
    
    @classmethod
    @property
    def REVOLVING(cls) -> IfcDoorPanelOperationEnum2X3:
        ...
    
    @classmethod
    @property
    def ROLLINGUP(cls) -> IfcDoorPanelOperationEnum2X3:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcDoorPanelOperationEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcDoorPanelOperationEnum2X3:
        ...
    
    ...

class IfcDoorPanelPositionEnum2X3:
    '''IfcDoorPanelPositionEnum'''
    
    @classmethod
    @property
    def LEFT(cls) -> IfcDoorPanelPositionEnum2X3:
        ...
    
    @classmethod
    @property
    def MIDDLE(cls) -> IfcDoorPanelPositionEnum2X3:
        ...
    
    @classmethod
    @property
    def RIGHT(cls) -> IfcDoorPanelPositionEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcDoorPanelPositionEnum2X3:
        ...
    
    ...

class IfcDoorStyleConstructionEnum2X3:
    '''IfcDoorStyleConstructionEnum'''
    
    @classmethod
    @property
    def ALUMINIUM(cls) -> IfcDoorStyleConstructionEnum2X3:
        ...
    
    @classmethod
    @property
    def HIGH_GRADE_STEEL(cls) -> IfcDoorStyleConstructionEnum2X3:
        ...
    
    @classmethod
    @property
    def STEEL(cls) -> IfcDoorStyleConstructionEnum2X3:
        ...
    
    @classmethod
    @property
    def WOOD(cls) -> IfcDoorStyleConstructionEnum2X3:
        ...
    
    @classmethod
    @property
    def ALUMINIUM_WOOD(cls) -> IfcDoorStyleConstructionEnum2X3:
        ...
    
    @classmethod
    @property
    def ALUMINIUM_PLASTIC(cls) -> IfcDoorStyleConstructionEnum2X3:
        ...
    
    @classmethod
    @property
    def PLASTIC(cls) -> IfcDoorStyleConstructionEnum2X3:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcDoorStyleConstructionEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcDoorStyleConstructionEnum2X3:
        ...
    
    ...

class IfcDoorStyleOperationEnum2X3:
    '''IfcDoorStyleOperationEnum'''
    
    @classmethod
    @property
    def SINGLE_SWING_LEFT(cls) -> IfcDoorStyleOperationEnum2X3:
        ...
    
    @classmethod
    @property
    def SINGLE_SWING_RIGHT(cls) -> IfcDoorStyleOperationEnum2X3:
        ...
    
    @classmethod
    @property
    def DOUBLE_DOOR_SINGLE_SWING(cls) -> IfcDoorStyleOperationEnum2X3:
        ...
    
    @classmethod
    @property
    def DOUBLE_DOOR_SINGLE_SWING_OPPOSITE_LEFT(cls) -> IfcDoorStyleOperationEnum2X3:
        ...
    
    @classmethod
    @property
    def DOUBLE_DOOR_SINGLE_SWING_OPPOSITE_RIGHT(cls) -> IfcDoorStyleOperationEnum2X3:
        ...
    
    @classmethod
    @property
    def DOUBLE_SWING_LEFT(cls) -> IfcDoorStyleOperationEnum2X3:
        ...
    
    @classmethod
    @property
    def DOUBLE_SWING_RIGHT(cls) -> IfcDoorStyleOperationEnum2X3:
        ...
    
    @classmethod
    @property
    def DOUBLE_DOOR_DOUBLE_SWING(cls) -> IfcDoorStyleOperationEnum2X3:
        ...
    
    @classmethod
    @property
    def SLIDING_TO_LEFT(cls) -> IfcDoorStyleOperationEnum2X3:
        ...
    
    @classmethod
    @property
    def SLIDING_TO_RIGHT(cls) -> IfcDoorStyleOperationEnum2X3:
        ...
    
    @classmethod
    @property
    def DOUBLE_DOOR_SLIDING(cls) -> IfcDoorStyleOperationEnum2X3:
        ...
    
    @classmethod
    @property
    def FOLDING_TO_LEFT(cls) -> IfcDoorStyleOperationEnum2X3:
        ...
    
    @classmethod
    @property
    def FOLDING_TO_RIGHT(cls) -> IfcDoorStyleOperationEnum2X3:
        ...
    
    @classmethod
    @property
    def DOUBLE_DOOR_FOLDING(cls) -> IfcDoorStyleOperationEnum2X3:
        ...
    
    @classmethod
    @property
    def REVOLVING(cls) -> IfcDoorStyleOperationEnum2X3:
        ...
    
    @classmethod
    @property
    def ROLLINGUP(cls) -> IfcDoorStyleOperationEnum2X3:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcDoorStyleOperationEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcDoorStyleOperationEnum2X3:
        ...
    
    ...

class IfcDuctFittingTypeEnum2X3:
    '''IfcDuctFittingTypeEnum'''
    
    @classmethod
    @property
    def BEND(cls) -> IfcDuctFittingTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def CONNECTOR(cls) -> IfcDuctFittingTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def ENTRY(cls) -> IfcDuctFittingTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def EXIT(cls) -> IfcDuctFittingTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def JUNCTION(cls) -> IfcDuctFittingTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def OBSTRUCTION(cls) -> IfcDuctFittingTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def TRANSITION(cls) -> IfcDuctFittingTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcDuctFittingTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcDuctFittingTypeEnum2X3:
        ...
    
    ...

class IfcDuctSegmentTypeEnum2X3:
    '''IfcDuctSegmentTypeEnum'''
    
    @classmethod
    @property
    def RIGIDSEGMENT(cls) -> IfcDuctSegmentTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def FLEXIBLESEGMENT(cls) -> IfcDuctSegmentTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcDuctSegmentTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcDuctSegmentTypeEnum2X3:
        ...
    
    ...

class IfcDuctSilencerTypeEnum2X3:
    '''IfcDuctSilencerTypeEnum'''
    
    @classmethod
    @property
    def FLATOVAL(cls) -> IfcDuctSilencerTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def RECTANGULAR(cls) -> IfcDuctSilencerTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def ROUND(cls) -> IfcDuctSilencerTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcDuctSilencerTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcDuctSilencerTypeEnum2X3:
        ...
    
    ...

class IfcElectricApplianceTypeEnum2X3:
    '''IfcElectricApplianceTypeEnum'''
    
    @classmethod
    @property
    def COMPUTER(cls) -> IfcElectricApplianceTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def DIRECTWATERHEATER(cls) -> IfcElectricApplianceTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def DISHWASHER(cls) -> IfcElectricApplianceTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def ELECTRICCOOKER(cls) -> IfcElectricApplianceTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def ELECTRICHEATER(cls) -> IfcElectricApplianceTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def FACSIMILE(cls) -> IfcElectricApplianceTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def FREESTANDINGFAN(cls) -> IfcElectricApplianceTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def FREEZER(cls) -> IfcElectricApplianceTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def FRIDGE_FREEZER(cls) -> IfcElectricApplianceTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def HANDDRYER(cls) -> IfcElectricApplianceTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def INDIRECTWATERHEATER(cls) -> IfcElectricApplianceTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def MICROWAVE(cls) -> IfcElectricApplianceTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def PHOTOCOPIER(cls) -> IfcElectricApplianceTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def PRINTER(cls) -> IfcElectricApplianceTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def REFRIGERATOR(cls) -> IfcElectricApplianceTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def RADIANTHEATER(cls) -> IfcElectricApplianceTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def SCANNER(cls) -> IfcElectricApplianceTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def TELEPHONE(cls) -> IfcElectricApplianceTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def TUMBLEDRYER(cls) -> IfcElectricApplianceTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def TV(cls) -> IfcElectricApplianceTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def VENDINGMACHINE(cls) -> IfcElectricApplianceTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def WASHINGMACHINE(cls) -> IfcElectricApplianceTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def WATERHEATER(cls) -> IfcElectricApplianceTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def WATERCOOLER(cls) -> IfcElectricApplianceTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcElectricApplianceTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcElectricApplianceTypeEnum2X3:
        ...
    
    ...

class IfcElectricCurrentEnum2X3:
    '''IfcElectricCurrentEnum'''
    
    @classmethod
    @property
    def ALTERNATING(cls) -> IfcElectricCurrentEnum2X3:
        ...
    
    @classmethod
    @property
    def DIRECT(cls) -> IfcElectricCurrentEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcElectricCurrentEnum2X3:
        ...
    
    ...

class IfcElectricDistributionPointFunctionEnum2X3:
    '''IfcElectricDistributionPointFunctionEnum'''
    
    @classmethod
    @property
    def ALARMPANEL(cls) -> IfcElectricDistributionPointFunctionEnum2X3:
        ...
    
    @classmethod
    @property
    def CONSUMERUNIT(cls) -> IfcElectricDistributionPointFunctionEnum2X3:
        ...
    
    @classmethod
    @property
    def CONTROLPANEL(cls) -> IfcElectricDistributionPointFunctionEnum2X3:
        ...
    
    @classmethod
    @property
    def DISTRIBUTIONBOARD(cls) -> IfcElectricDistributionPointFunctionEnum2X3:
        ...
    
    @classmethod
    @property
    def GASDETECTORPANEL(cls) -> IfcElectricDistributionPointFunctionEnum2X3:
        ...
    
    @classmethod
    @property
    def INDICATORPANEL(cls) -> IfcElectricDistributionPointFunctionEnum2X3:
        ...
    
    @classmethod
    @property
    def MIMICPANEL(cls) -> IfcElectricDistributionPointFunctionEnum2X3:
        ...
    
    @classmethod
    @property
    def MOTORCONTROLCENTRE(cls) -> IfcElectricDistributionPointFunctionEnum2X3:
        ...
    
    @classmethod
    @property
    def SWITCHBOARD(cls) -> IfcElectricDistributionPointFunctionEnum2X3:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcElectricDistributionPointFunctionEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcElectricDistributionPointFunctionEnum2X3:
        ...
    
    ...

class IfcElectricFlowStorageDeviceTypeEnum2X3:
    '''IfcElectricFlowStorageDeviceTypeEnum'''
    
    @classmethod
    @property
    def BATTERY(cls) -> IfcElectricFlowStorageDeviceTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def CAPACITORBANK(cls) -> IfcElectricFlowStorageDeviceTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def HARMONICFILTER(cls) -> IfcElectricFlowStorageDeviceTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def INDUCTORBANK(cls) -> IfcElectricFlowStorageDeviceTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def UPS(cls) -> IfcElectricFlowStorageDeviceTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcElectricFlowStorageDeviceTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcElectricFlowStorageDeviceTypeEnum2X3:
        ...
    
    ...

class IfcElectricGeneratorTypeEnum2X3:
    '''IfcElectricGeneratorTypeEnum'''
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcElectricGeneratorTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcElectricGeneratorTypeEnum2X3:
        ...
    
    ...

class IfcElectricHeaterTypeEnum2X3:
    '''IfcElectricHeaterTypeEnum'''
    
    @classmethod
    @property
    def ELECTRICPOINTHEATER(cls) -> IfcElectricHeaterTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def ELECTRICCABLEHEATER(cls) -> IfcElectricHeaterTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def ELECTRICMATHEATER(cls) -> IfcElectricHeaterTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcElectricHeaterTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcElectricHeaterTypeEnum2X3:
        ...
    
    ...

class IfcElectricMotorTypeEnum2X3:
    '''IfcElectricMotorTypeEnum'''
    
    @classmethod
    @property
    def DC(cls) -> IfcElectricMotorTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def INDUCTION(cls) -> IfcElectricMotorTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def POLYPHASE(cls) -> IfcElectricMotorTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def RELUCTANCESYNCHRONOUS(cls) -> IfcElectricMotorTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def SYNCHRONOUS(cls) -> IfcElectricMotorTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcElectricMotorTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcElectricMotorTypeEnum2X3:
        ...
    
    ...

class IfcElectricTimeControlTypeEnum2X3:
    '''IfcElectricTimeControlTypeEnum'''
    
    @classmethod
    @property
    def TIMECLOCK(cls) -> IfcElectricTimeControlTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def TIMEDELAY(cls) -> IfcElectricTimeControlTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def RELAY(cls) -> IfcElectricTimeControlTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcElectricTimeControlTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcElectricTimeControlTypeEnum2X3:
        ...
    
    ...

class IfcElementAssemblyTypeEnum2X3:
    '''IfcElementAssemblyTypeEnum'''
    
    @classmethod
    @property
    def ACCESSORY_ASSEMBLY(cls) -> IfcElementAssemblyTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def ARCH(cls) -> IfcElementAssemblyTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def BEAM_GRID(cls) -> IfcElementAssemblyTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def BRACED_FRAME(cls) -> IfcElementAssemblyTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def GIRDER(cls) -> IfcElementAssemblyTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def REINFORCEMENT_UNIT(cls) -> IfcElementAssemblyTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def RIGID_FRAME(cls) -> IfcElementAssemblyTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def SLAB_FIELD(cls) -> IfcElementAssemblyTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def TRUSS(cls) -> IfcElementAssemblyTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcElementAssemblyTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcElementAssemblyTypeEnum2X3:
        ...
    
    ...

class IfcElementCompositionEnum2X3:
    '''IfcElementCompositionEnum'''
    
    @classmethod
    @property
    def COMPLEX(cls) -> IfcElementCompositionEnum2X3:
        ...
    
    @classmethod
    @property
    def ELEMENT(cls) -> IfcElementCompositionEnum2X3:
        ...
    
    @classmethod
    @property
    def PARTIAL(cls) -> IfcElementCompositionEnum2X3:
        ...
    
    ...

class IfcEnergySequenceEnum2X3:
    '''IfcEnergySequenceEnum'''
    
    @classmethod
    @property
    def PRIMARY(cls) -> IfcEnergySequenceEnum2X3:
        ...
    
    @classmethod
    @property
    def SECONDARY(cls) -> IfcEnergySequenceEnum2X3:
        ...
    
    @classmethod
    @property
    def TERTIARY(cls) -> IfcEnergySequenceEnum2X3:
        ...
    
    @classmethod
    @property
    def AUXILIARY(cls) -> IfcEnergySequenceEnum2X3:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcEnergySequenceEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcEnergySequenceEnum2X3:
        ...
    
    ...

class IfcEnvironmentalImpactCategoryEnum2X3:
    '''IfcEnvironmentalImpactCategoryEnum'''
    
    @classmethod
    @property
    def COMBINEDVALUE(cls) -> IfcEnvironmentalImpactCategoryEnum2X3:
        ...
    
    @classmethod
    @property
    def DISPOSAL(cls) -> IfcEnvironmentalImpactCategoryEnum2X3:
        ...
    
    @classmethod
    @property
    def EXTRACTION(cls) -> IfcEnvironmentalImpactCategoryEnum2X3:
        ...
    
    @classmethod
    @property
    def INSTALLATION(cls) -> IfcEnvironmentalImpactCategoryEnum2X3:
        ...
    
    @classmethod
    @property
    def MANUFACTURE(cls) -> IfcEnvironmentalImpactCategoryEnum2X3:
        ...
    
    @classmethod
    @property
    def TRANSPORTATION(cls) -> IfcEnvironmentalImpactCategoryEnum2X3:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcEnvironmentalImpactCategoryEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcEnvironmentalImpactCategoryEnum2X3:
        ...
    
    ...

class IfcEvaporativeCoolerTypeEnum2X3:
    '''IfcEvaporativeCoolerTypeEnum'''
    
    @classmethod
    @property
    def DIRECTEVAPORATIVERANDOMMEDIAAIRCOOLER(cls) -> IfcEvaporativeCoolerTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def DIRECTEVAPORATIVERIGIDMEDIAAIRCOOLER(cls) -> IfcEvaporativeCoolerTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def DIRECTEVAPORATIVESLINGERSPACKAGEDAIRCOOLER(cls) -> IfcEvaporativeCoolerTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def DIRECTEVAPORATIVEPACKAGEDROTARYAIRCOOLER(cls) -> IfcEvaporativeCoolerTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def DIRECTEVAPORATIVEAIRWASHER(cls) -> IfcEvaporativeCoolerTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def INDIRECTEVAPORATIVEPACKAGEAIRCOOLER(cls) -> IfcEvaporativeCoolerTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def INDIRECTEVAPORATIVEWETCOIL(cls) -> IfcEvaporativeCoolerTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def INDIRECTEVAPORATIVECOOLINGTOWERORCOILCOOLER(cls) -> IfcEvaporativeCoolerTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def INDIRECTDIRECTCOMBINATION(cls) -> IfcEvaporativeCoolerTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcEvaporativeCoolerTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcEvaporativeCoolerTypeEnum2X3:
        ...
    
    ...

class IfcEvaporatorTypeEnum2X3:
    '''IfcEvaporatorTypeEnum'''
    
    @classmethod
    @property
    def DIRECTEXPANSIONSHELLANDTUBE(cls) -> IfcEvaporatorTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def DIRECTEXPANSIONTUBEINTUBE(cls) -> IfcEvaporatorTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def DIRECTEXPANSIONBRAZEDPLATE(cls) -> IfcEvaporatorTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def FLOODEDSHELLANDTUBE(cls) -> IfcEvaporatorTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def SHELLANDCOIL(cls) -> IfcEvaporatorTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcEvaporatorTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcEvaporatorTypeEnum2X3:
        ...
    
    ...

class IfcFanTypeEnum2X3:
    '''IfcFanTypeEnum'''
    
    @classmethod
    @property
    def CENTRIFUGALFORWARDCURVED(cls) -> IfcFanTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def CENTRIFUGALRADIAL(cls) -> IfcFanTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def CENTRIFUGALBACKWARDINCLINEDCURVED(cls) -> IfcFanTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def CENTRIFUGALAIRFOIL(cls) -> IfcFanTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def TUBEAXIAL(cls) -> IfcFanTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def VANEAXIAL(cls) -> IfcFanTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def PROPELLORAXIAL(cls) -> IfcFanTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcFanTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcFanTypeEnum2X3:
        ...
    
    ...

class IfcFilterTypeEnum2X3:
    '''IfcFilterTypeEnum'''
    
    @classmethod
    @property
    def AIRPARTICLEFILTER(cls) -> IfcFilterTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def ODORFILTER(cls) -> IfcFilterTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def OILFILTER(cls) -> IfcFilterTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def STRAINER(cls) -> IfcFilterTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def WATERFILTER(cls) -> IfcFilterTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcFilterTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcFilterTypeEnum2X3:
        ...
    
    ...

class IfcFireSuppressionTerminalTypeEnum2X3:
    '''IfcFireSuppressionTerminalTypeEnum'''
    
    @classmethod
    @property
    def BREECHINGINLET(cls) -> IfcFireSuppressionTerminalTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def FIREHYDRANT(cls) -> IfcFireSuppressionTerminalTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def HOSEREEL(cls) -> IfcFireSuppressionTerminalTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def SPRINKLER(cls) -> IfcFireSuppressionTerminalTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def SPRINKLERDEFLECTOR(cls) -> IfcFireSuppressionTerminalTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcFireSuppressionTerminalTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcFireSuppressionTerminalTypeEnum2X3:
        ...
    
    ...

class IfcFlowDirectionEnum2X3:
    '''IfcFlowDirectionEnum'''
    
    @classmethod
    @property
    def SOURCE(cls) -> IfcFlowDirectionEnum2X3:
        ...
    
    @classmethod
    @property
    def SINK(cls) -> IfcFlowDirectionEnum2X3:
        ...
    
    @classmethod
    @property
    def SOURCEANDSINK(cls) -> IfcFlowDirectionEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcFlowDirectionEnum2X3:
        ...
    
    ...

class IfcFlowInstrumentTypeEnum2X3:
    '''IfcFlowInstrumentTypeEnum'''
    
    @classmethod
    @property
    def PRESSUREGAUGE(cls) -> IfcFlowInstrumentTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def THERMOMETER(cls) -> IfcFlowInstrumentTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def AMMETER(cls) -> IfcFlowInstrumentTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def FREQUENCYMETER(cls) -> IfcFlowInstrumentTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def POWERFACTORMETER(cls) -> IfcFlowInstrumentTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def PHASEANGLEMETER(cls) -> IfcFlowInstrumentTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def VOLTMETER_PEAK(cls) -> IfcFlowInstrumentTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def VOLTMETER_RMS(cls) -> IfcFlowInstrumentTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcFlowInstrumentTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcFlowInstrumentTypeEnum2X3:
        ...
    
    ...

class IfcFlowMeterTypeEnum2X3:
    '''IfcFlowMeterTypeEnum'''
    
    @classmethod
    @property
    def ELECTRICMETER(cls) -> IfcFlowMeterTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def ENERGYMETER(cls) -> IfcFlowMeterTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def FLOWMETER(cls) -> IfcFlowMeterTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def GASMETER(cls) -> IfcFlowMeterTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def OILMETER(cls) -> IfcFlowMeterTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def WATERMETER(cls) -> IfcFlowMeterTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcFlowMeterTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcFlowMeterTypeEnum2X3:
        ...
    
    ...

class IfcFootingTypeEnum2X3:
    '''IfcFootingTypeEnum'''
    
    @classmethod
    @property
    def FOOTING_BEAM(cls) -> IfcFootingTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def PAD_FOOTING(cls) -> IfcFootingTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def PILE_CAP(cls) -> IfcFootingTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def STRIP_FOOTING(cls) -> IfcFootingTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcFootingTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcFootingTypeEnum2X3:
        ...
    
    ...

class IfcGasTerminalTypeEnum2X3:
    '''IfcGasTerminalTypeEnum'''
    
    @classmethod
    @property
    def GASAPPLIANCE(cls) -> IfcGasTerminalTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def GASBOOSTER(cls) -> IfcGasTerminalTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def GASBURNER(cls) -> IfcGasTerminalTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcGasTerminalTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcGasTerminalTypeEnum2X3:
        ...
    
    ...

class IfcGeometricProjectionEnum2X3:
    '''IfcGeometricProjectionEnum'''
    
    @classmethod
    @property
    def GRAPH_VIEW(cls) -> IfcGeometricProjectionEnum2X3:
        ...
    
    @classmethod
    @property
    def SKETCH_VIEW(cls) -> IfcGeometricProjectionEnum2X3:
        ...
    
    @classmethod
    @property
    def MODEL_VIEW(cls) -> IfcGeometricProjectionEnum2X3:
        ...
    
    @classmethod
    @property
    def PLAN_VIEW(cls) -> IfcGeometricProjectionEnum2X3:
        ...
    
    @classmethod
    @property
    def REFLECTED_PLAN_VIEW(cls) -> IfcGeometricProjectionEnum2X3:
        ...
    
    @classmethod
    @property
    def SECTION_VIEW(cls) -> IfcGeometricProjectionEnum2X3:
        ...
    
    @classmethod
    @property
    def ELEVATION_VIEW(cls) -> IfcGeometricProjectionEnum2X3:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcGeometricProjectionEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcGeometricProjectionEnum2X3:
        ...
    
    ...

class IfcGlobalOrLocalEnum2X3:
    '''IfcGlobalOrLocalEnum'''
    
    @classmethod
    @property
    def GLOBAL_COORDS(cls) -> IfcGlobalOrLocalEnum2X3:
        ...
    
    @classmethod
    @property
    def LOCAL_COORDS(cls) -> IfcGlobalOrLocalEnum2X3:
        ...
    
    ...

class IfcHeatExchangerTypeEnum2X3:
    '''IfcHeatExchangerTypeEnum'''
    
    @classmethod
    @property
    def PLATE(cls) -> IfcHeatExchangerTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def SHELLANDTUBE(cls) -> IfcHeatExchangerTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcHeatExchangerTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcHeatExchangerTypeEnum2X3:
        ...
    
    ...

class IfcHumidifierTypeEnum2X3:
    '''IfcHumidifierTypeEnum'''
    
    @classmethod
    @property
    def STEAMINJECTION(cls) -> IfcHumidifierTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def ADIABATICAIRWASHER(cls) -> IfcHumidifierTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def ADIABATICPAN(cls) -> IfcHumidifierTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def ADIABATICWETTEDELEMENT(cls) -> IfcHumidifierTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def ADIABATICATOMIZING(cls) -> IfcHumidifierTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def ADIABATICULTRASONIC(cls) -> IfcHumidifierTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def ADIABATICRIGIDMEDIA(cls) -> IfcHumidifierTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def ADIABATICCOMPRESSEDAIRNOZZLE(cls) -> IfcHumidifierTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def ASSISTEDELECTRIC(cls) -> IfcHumidifierTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def ASSISTEDNATURALGAS(cls) -> IfcHumidifierTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def ASSISTEDPROPANE(cls) -> IfcHumidifierTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def ASSISTEDBUTANE(cls) -> IfcHumidifierTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def ASSISTEDSTEAM(cls) -> IfcHumidifierTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcHumidifierTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcHumidifierTypeEnum2X3:
        ...
    
    ...

class IfcInternalOrExternalEnum2X3:
    '''IfcInternalOrExternalEnum'''
    
    @classmethod
    @property
    def INTERNAL(cls) -> IfcInternalOrExternalEnum2X3:
        ...
    
    @classmethod
    @property
    def EXTERNAL(cls) -> IfcInternalOrExternalEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcInternalOrExternalEnum2X3:
        ...
    
    ...

class IfcInventoryTypeEnum2X3:
    '''IfcInventoryTypeEnum'''
    
    @classmethod
    @property
    def ASSETINVENTORY(cls) -> IfcInventoryTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def SPACEINVENTORY(cls) -> IfcInventoryTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def FURNITUREINVENTORY(cls) -> IfcInventoryTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcInventoryTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcInventoryTypeEnum2X3:
        ...
    
    ...

class IfcJunctionBoxTypeEnum2X3:
    '''IfcJunctionBoxTypeEnum'''
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcJunctionBoxTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcJunctionBoxTypeEnum2X3:
        ...
    
    ...

class IfcLampTypeEnum2X3:
    '''IfcLampTypeEnum'''
    
    @classmethod
    @property
    def COMPACTFLUORESCENT(cls) -> IfcLampTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def FLUORESCENT(cls) -> IfcLampTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def HIGHPRESSUREMERCURY(cls) -> IfcLampTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def HIGHPRESSURESODIUM(cls) -> IfcLampTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def METALHALIDE(cls) -> IfcLampTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def TUNGSTENFILAMENT(cls) -> IfcLampTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcLampTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcLampTypeEnum2X3:
        ...
    
    ...

class IfcLayerSetDirectionEnum2X3:
    '''IfcLayerSetDirectionEnum'''
    
    @classmethod
    @property
    def AXIS1(cls) -> IfcLayerSetDirectionEnum2X3:
        ...
    
    @classmethod
    @property
    def AXIS2(cls) -> IfcLayerSetDirectionEnum2X3:
        ...
    
    @classmethod
    @property
    def AXIS3(cls) -> IfcLayerSetDirectionEnum2X3:
        ...
    
    ...

class IfcLightDistributionCurveEnum2X3:
    '''IfcLightDistributionCurveEnum'''
    
    @classmethod
    @property
    def TYPE_A(cls) -> IfcLightDistributionCurveEnum2X3:
        ...
    
    @classmethod
    @property
    def TYPE_B(cls) -> IfcLightDistributionCurveEnum2X3:
        ...
    
    @classmethod
    @property
    def TYPE_C(cls) -> IfcLightDistributionCurveEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcLightDistributionCurveEnum2X3:
        ...
    
    ...

class IfcLightEmissionSourceEnum2X3:
    '''IfcLightEmissionSourceEnum'''
    
    @classmethod
    @property
    def COMPACTFLUORESCENT(cls) -> IfcLightEmissionSourceEnum2X3:
        ...
    
    @classmethod
    @property
    def FLUORESCENT(cls) -> IfcLightEmissionSourceEnum2X3:
        ...
    
    @classmethod
    @property
    def HIGHPRESSUREMERCURY(cls) -> IfcLightEmissionSourceEnum2X3:
        ...
    
    @classmethod
    @property
    def HIGHPRESSURESODIUM(cls) -> IfcLightEmissionSourceEnum2X3:
        ...
    
    @classmethod
    @property
    def LIGHTEMITTINGDIODE(cls) -> IfcLightEmissionSourceEnum2X3:
        ...
    
    @classmethod
    @property
    def LOWPRESSURESODIUM(cls) -> IfcLightEmissionSourceEnum2X3:
        ...
    
    @classmethod
    @property
    def LOWVOLTAGEHALOGEN(cls) -> IfcLightEmissionSourceEnum2X3:
        ...
    
    @classmethod
    @property
    def MAINVOLTAGEHALOGEN(cls) -> IfcLightEmissionSourceEnum2X3:
        ...
    
    @classmethod
    @property
    def METALHALIDE(cls) -> IfcLightEmissionSourceEnum2X3:
        ...
    
    @classmethod
    @property
    def TUNGSTENFILAMENT(cls) -> IfcLightEmissionSourceEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcLightEmissionSourceEnum2X3:
        ...
    
    ...

class IfcLightFixtureTypeEnum2X3:
    '''IfcLightFixtureTypeEnum'''
    
    @classmethod
    @property
    def POINTSOURCE(cls) -> IfcLightFixtureTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def DIRECTIONSOURCE(cls) -> IfcLightFixtureTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcLightFixtureTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcLightFixtureTypeEnum2X3:
        ...
    
    ...

class IfcLoadGroupTypeEnum2X3:
    '''IfcLoadGroupTypeEnum'''
    
    @classmethod
    @property
    def LOAD_GROUP(cls) -> IfcLoadGroupTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def LOAD_CASE(cls) -> IfcLoadGroupTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def LOAD_COMBINATION_GROUP(cls) -> IfcLoadGroupTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def LOAD_COMBINATION(cls) -> IfcLoadGroupTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcLoadGroupTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcLoadGroupTypeEnum2X3:
        ...
    
    ...

class IfcLogicalOperatorEnum2X3:
    '''IfcLogicalOperatorEnum'''
    
    @classmethod
    @property
    def LOGICALAND(cls) -> IfcLogicalOperatorEnum2X3:
        ...
    
    @classmethod
    @property
    def LOGICALOR(cls) -> IfcLogicalOperatorEnum2X3:
        ...
    
    ...

class IfcMemberTypeEnum2X3:
    '''IfcMemberTypeEnum'''
    
    @classmethod
    @property
    def BRACE(cls) -> IfcMemberTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def CHORD(cls) -> IfcMemberTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def COLLAR(cls) -> IfcMemberTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def MEMBER(cls) -> IfcMemberTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def MULLION(cls) -> IfcMemberTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def PLATE(cls) -> IfcMemberTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def POST(cls) -> IfcMemberTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def PURLIN(cls) -> IfcMemberTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def RAFTER(cls) -> IfcMemberTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def STRINGER(cls) -> IfcMemberTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def STRUT(cls) -> IfcMemberTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def STUD(cls) -> IfcMemberTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcMemberTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcMemberTypeEnum2X3:
        ...
    
    ...

class IfcMotorConnectionTypeEnum2X3:
    '''IfcMotorConnectionTypeEnum'''
    
    @classmethod
    @property
    def BELTDRIVE(cls) -> IfcMotorConnectionTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def COUPLING(cls) -> IfcMotorConnectionTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def DIRECTDRIVE(cls) -> IfcMotorConnectionTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcMotorConnectionTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcMotorConnectionTypeEnum2X3:
        ...
    
    ...

class IfcNullStyle2X3:
    '''IfcNullStyle'''
    
    @classmethod
    @property
    def NULL(cls) -> IfcNullStyle2X3:
        ...
    
    ...

class IfcObjectTypeEnum2X3:
    '''IfcObjectTypeEnum'''
    
    @classmethod
    @property
    def PRODUCT(cls) -> IfcObjectTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def PROCESS(cls) -> IfcObjectTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def CONTROL(cls) -> IfcObjectTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def RESOURCE(cls) -> IfcObjectTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def ACTOR(cls) -> IfcObjectTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def GROUP(cls) -> IfcObjectTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def PROJECT(cls) -> IfcObjectTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcObjectTypeEnum2X3:
        ...
    
    ...

class IfcObjectiveEnum2X3:
    '''IfcObjectiveEnum'''
    
    @classmethod
    @property
    def CODECOMPLIANCE(cls) -> IfcObjectiveEnum2X3:
        ...
    
    @classmethod
    @property
    def DESIGNINTENT(cls) -> IfcObjectiveEnum2X3:
        ...
    
    @classmethod
    @property
    def HEALTHANDSAFETY(cls) -> IfcObjectiveEnum2X3:
        ...
    
    @classmethod
    @property
    def REQUIREMENT(cls) -> IfcObjectiveEnum2X3:
        ...
    
    @classmethod
    @property
    def SPECIFICATION(cls) -> IfcObjectiveEnum2X3:
        ...
    
    @classmethod
    @property
    def TRIGGERCONDITION(cls) -> IfcObjectiveEnum2X3:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcObjectiveEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcObjectiveEnum2X3:
        ...
    
    ...

class IfcOccupantTypeEnum2X3:
    '''IfcOccupantTypeEnum'''
    
    @classmethod
    @property
    def ASSIGNEE(cls) -> IfcOccupantTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def ASSIGNOR(cls) -> IfcOccupantTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def LESSEE(cls) -> IfcOccupantTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def LESSOR(cls) -> IfcOccupantTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def LETTINGAGENT(cls) -> IfcOccupantTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def OWNER(cls) -> IfcOccupantTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def TENANT(cls) -> IfcOccupantTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcOccupantTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcOccupantTypeEnum2X3:
        ...
    
    ...

class IfcOutletTypeEnum2X3:
    '''IfcOutletTypeEnum'''
    
    @classmethod
    @property
    def AUDIOVISUALOUTLET(cls) -> IfcOutletTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def COMMUNICATIONSOUTLET(cls) -> IfcOutletTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def POWEROUTLET(cls) -> IfcOutletTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcOutletTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcOutletTypeEnum2X3:
        ...
    
    ...

class IfcPermeableCoveringOperationEnum2X3:
    '''IfcPermeableCoveringOperationEnum'''
    
    @classmethod
    @property
    def GRILL(cls) -> IfcPermeableCoveringOperationEnum2X3:
        ...
    
    @classmethod
    @property
    def LOUVER(cls) -> IfcPermeableCoveringOperationEnum2X3:
        ...
    
    @classmethod
    @property
    def SCREEN(cls) -> IfcPermeableCoveringOperationEnum2X3:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcPermeableCoveringOperationEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcPermeableCoveringOperationEnum2X3:
        ...
    
    ...

class IfcPhysicalOrVirtualEnum2X3:
    '''IfcPhysicalOrVirtualEnum'''
    
    @classmethod
    @property
    def PHYSICAL(cls) -> IfcPhysicalOrVirtualEnum2X3:
        ...
    
    @classmethod
    @property
    def VIRTUAL(cls) -> IfcPhysicalOrVirtualEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcPhysicalOrVirtualEnum2X3:
        ...
    
    ...

class IfcPileConstructionEnum2X3:
    '''IfcPileConstructionEnum'''
    
    @classmethod
    @property
    def CAST_IN_PLACE(cls) -> IfcPileConstructionEnum2X3:
        ...
    
    @classmethod
    @property
    def COMPOSITE(cls) -> IfcPileConstructionEnum2X3:
        ...
    
    @classmethod
    @property
    def PRECAST_CONCRETE(cls) -> IfcPileConstructionEnum2X3:
        ...
    
    @classmethod
    @property
    def PREFAB_STEEL(cls) -> IfcPileConstructionEnum2X3:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcPileConstructionEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcPileConstructionEnum2X3:
        ...
    
    ...

class IfcPileTypeEnum2X3:
    '''IfcPileTypeEnum'''
    
    @classmethod
    @property
    def COHESION(cls) -> IfcPileTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def FRICTION(cls) -> IfcPileTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def SUPPORT(cls) -> IfcPileTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcPileTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcPileTypeEnum2X3:
        ...
    
    ...

class IfcPipeFittingTypeEnum2X3:
    '''IfcPipeFittingTypeEnum'''
    
    @classmethod
    @property
    def BEND(cls) -> IfcPipeFittingTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def CONNECTOR(cls) -> IfcPipeFittingTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def ENTRY(cls) -> IfcPipeFittingTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def EXIT(cls) -> IfcPipeFittingTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def JUNCTION(cls) -> IfcPipeFittingTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def OBSTRUCTION(cls) -> IfcPipeFittingTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def TRANSITION(cls) -> IfcPipeFittingTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcPipeFittingTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcPipeFittingTypeEnum2X3:
        ...
    
    ...

class IfcPipeSegmentTypeEnum2X3:
    '''IfcPipeSegmentTypeEnum'''
    
    @classmethod
    @property
    def FLEXIBLESEGMENT(cls) -> IfcPipeSegmentTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def RIGIDSEGMENT(cls) -> IfcPipeSegmentTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def GUTTER(cls) -> IfcPipeSegmentTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def SPOOL(cls) -> IfcPipeSegmentTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcPipeSegmentTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcPipeSegmentTypeEnum2X3:
        ...
    
    ...

class IfcPlateTypeEnum2X3:
    '''IfcPlateTypeEnum'''
    
    @classmethod
    @property
    def CURTAIN_PANEL(cls) -> IfcPlateTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def SHEET(cls) -> IfcPlateTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcPlateTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcPlateTypeEnum2X3:
        ...
    
    ...

class IfcProcedureTypeEnum2X3:
    '''IfcProcedureTypeEnum'''
    
    @classmethod
    @property
    def ADVICE_CAUTION(cls) -> IfcProcedureTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def ADVICE_NOTE(cls) -> IfcProcedureTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def ADVICE_WARNING(cls) -> IfcProcedureTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def CALIBRATION(cls) -> IfcProcedureTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def DIAGNOSTIC(cls) -> IfcProcedureTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def SHUTDOWN(cls) -> IfcProcedureTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def STARTUP(cls) -> IfcProcedureTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcProcedureTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcProcedureTypeEnum2X3:
        ...
    
    ...

class IfcProfileTypeEnum2X3:
    '''IfcProfileTypeEnum'''
    
    @classmethod
    @property
    def CURVE(cls) -> IfcProfileTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def AREA(cls) -> IfcProfileTypeEnum2X3:
        ...
    
    ...

class IfcProjectOrderRecordTypeEnum2X3:
    '''IfcProjectOrderRecordTypeEnum'''
    
    @classmethod
    @property
    def CHANGE(cls) -> IfcProjectOrderRecordTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def MAINTENANCE(cls) -> IfcProjectOrderRecordTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def MOVE(cls) -> IfcProjectOrderRecordTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def PURCHASE(cls) -> IfcProjectOrderRecordTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def WORK(cls) -> IfcProjectOrderRecordTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcProjectOrderRecordTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcProjectOrderRecordTypeEnum2X3:
        ...
    
    ...

class IfcProjectOrderTypeEnum2X3:
    '''IfcProjectOrderTypeEnum'''
    
    @classmethod
    @property
    def CHANGEORDER(cls) -> IfcProjectOrderTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def MAINTENANCEWORKORDER(cls) -> IfcProjectOrderTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def MOVEORDER(cls) -> IfcProjectOrderTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def PURCHASEORDER(cls) -> IfcProjectOrderTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def WORKORDER(cls) -> IfcProjectOrderTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcProjectOrderTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcProjectOrderTypeEnum2X3:
        ...
    
    ...

class IfcProjectedOrTrueLengthEnum2X3:
    '''IfcProjectedOrTrueLengthEnum'''
    
    @classmethod
    @property
    def PROJECTED_LENGTH(cls) -> IfcProjectedOrTrueLengthEnum2X3:
        ...
    
    @classmethod
    @property
    def TRUE_LENGTH(cls) -> IfcProjectedOrTrueLengthEnum2X3:
        ...
    
    ...

class IfcPropertySourceEnum2X3:
    '''IfcPropertySourceEnum'''
    
    @classmethod
    @property
    def DESIGN(cls) -> IfcPropertySourceEnum2X3:
        ...
    
    @classmethod
    @property
    def DESIGNMAXIMUM(cls) -> IfcPropertySourceEnum2X3:
        ...
    
    @classmethod
    @property
    def DESIGNMINIMUM(cls) -> IfcPropertySourceEnum2X3:
        ...
    
    @classmethod
    @property
    def SIMULATED(cls) -> IfcPropertySourceEnum2X3:
        ...
    
    @classmethod
    @property
    def ASBUILT(cls) -> IfcPropertySourceEnum2X3:
        ...
    
    @classmethod
    @property
    def COMMISSIONING(cls) -> IfcPropertySourceEnum2X3:
        ...
    
    @classmethod
    @property
    def MEASURED(cls) -> IfcPropertySourceEnum2X3:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcPropertySourceEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTKNOWN(cls) -> IfcPropertySourceEnum2X3:
        ...
    
    ...

class IfcProtectiveDeviceTypeEnum2X3:
    '''IfcProtectiveDeviceTypeEnum'''
    
    @classmethod
    @property
    def FUSEDISCONNECTOR(cls) -> IfcProtectiveDeviceTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def CIRCUITBREAKER(cls) -> IfcProtectiveDeviceTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def EARTHFAILUREDEVICE(cls) -> IfcProtectiveDeviceTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def RESIDUALCURRENTCIRCUITBREAKER(cls) -> IfcProtectiveDeviceTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def RESIDUALCURRENTSWITCH(cls) -> IfcProtectiveDeviceTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def VARISTOR(cls) -> IfcProtectiveDeviceTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcProtectiveDeviceTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcProtectiveDeviceTypeEnum2X3:
        ...
    
    ...

class IfcPumpTypeEnum2X3:
    '''IfcPumpTypeEnum'''
    
    @classmethod
    @property
    def CIRCULATOR(cls) -> IfcPumpTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def ENDSUCTION(cls) -> IfcPumpTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def SPLITCASE(cls) -> IfcPumpTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def VERTICALINLINE(cls) -> IfcPumpTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def VERTICALTURBINE(cls) -> IfcPumpTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcPumpTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcPumpTypeEnum2X3:
        ...
    
    ...

class IfcRailingTypeEnum2X3:
    '''IfcRailingTypeEnum'''
    
    @classmethod
    @property
    def HANDRAIL(cls) -> IfcRailingTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def GUARDRAIL(cls) -> IfcRailingTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def BALUSTRADE(cls) -> IfcRailingTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcRailingTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcRailingTypeEnum2X3:
        ...
    
    ...

class IfcRampFlightTypeEnum2X3:
    '''IfcRampFlightTypeEnum'''
    
    @classmethod
    @property
    def STRAIGHT(cls) -> IfcRampFlightTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def SPIRAL(cls) -> IfcRampFlightTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcRampFlightTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcRampFlightTypeEnum2X3:
        ...
    
    ...

class IfcRampTypeEnum2X3:
    '''IfcRampTypeEnum'''
    
    @classmethod
    @property
    def STRAIGHT_RUN_RAMP(cls) -> IfcRampTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def TWO_STRAIGHT_RUN_RAMP(cls) -> IfcRampTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def QUARTER_TURN_RAMP(cls) -> IfcRampTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def TWO_QUARTER_TURN_RAMP(cls) -> IfcRampTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def HALF_TURN_RAMP(cls) -> IfcRampTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def SPIRAL_RAMP(cls) -> IfcRampTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcRampTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcRampTypeEnum2X3:
        ...
    
    ...

class IfcReflectanceMethodEnum2X3:
    '''IfcReflectanceMethodEnum'''
    
    @classmethod
    @property
    def BLINN(cls) -> IfcReflectanceMethodEnum2X3:
        ...
    
    @classmethod
    @property
    def FLAT(cls) -> IfcReflectanceMethodEnum2X3:
        ...
    
    @classmethod
    @property
    def GLASS(cls) -> IfcReflectanceMethodEnum2X3:
        ...
    
    @classmethod
    @property
    def MATT(cls) -> IfcReflectanceMethodEnum2X3:
        ...
    
    @classmethod
    @property
    def METAL(cls) -> IfcReflectanceMethodEnum2X3:
        ...
    
    @classmethod
    @property
    def MIRROR(cls) -> IfcReflectanceMethodEnum2X3:
        ...
    
    @classmethod
    @property
    def PHONG(cls) -> IfcReflectanceMethodEnum2X3:
        ...
    
    @classmethod
    @property
    def PLASTIC(cls) -> IfcReflectanceMethodEnum2X3:
        ...
    
    @classmethod
    @property
    def STRAUSS(cls) -> IfcReflectanceMethodEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcReflectanceMethodEnum2X3:
        ...
    
    ...

class IfcReinforcingBarRoleEnum2X3:
    '''IfcReinforcingBarRoleEnum'''
    
    @classmethod
    @property
    def MAIN(cls) -> IfcReinforcingBarRoleEnum2X3:
        ...
    
    @classmethod
    @property
    def SHEAR(cls) -> IfcReinforcingBarRoleEnum2X3:
        ...
    
    @classmethod
    @property
    def LIGATURE(cls) -> IfcReinforcingBarRoleEnum2X3:
        ...
    
    @classmethod
    @property
    def STUD(cls) -> IfcReinforcingBarRoleEnum2X3:
        ...
    
    @classmethod
    @property
    def PUNCHING(cls) -> IfcReinforcingBarRoleEnum2X3:
        ...
    
    @classmethod
    @property
    def EDGE(cls) -> IfcReinforcingBarRoleEnum2X3:
        ...
    
    @classmethod
    @property
    def RING(cls) -> IfcReinforcingBarRoleEnum2X3:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcReinforcingBarRoleEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcReinforcingBarRoleEnum2X3:
        ...
    
    ...

class IfcReinforcingBarSurfaceEnum2X3:
    '''IfcReinforcingBarSurfaceEnum'''
    
    @classmethod
    @property
    def PLAIN(cls) -> IfcReinforcingBarSurfaceEnum2X3:
        ...
    
    @classmethod
    @property
    def TEXTURED(cls) -> IfcReinforcingBarSurfaceEnum2X3:
        ...
    
    ...

class IfcResourceConsumptionEnum2X3:
    '''IfcResourceConsumptionEnum'''
    
    @classmethod
    @property
    def CONSUMED(cls) -> IfcResourceConsumptionEnum2X3:
        ...
    
    @classmethod
    @property
    def PARTIALLYCONSUMED(cls) -> IfcResourceConsumptionEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTCONSUMED(cls) -> IfcResourceConsumptionEnum2X3:
        ...
    
    @classmethod
    @property
    def OCCUPIED(cls) -> IfcResourceConsumptionEnum2X3:
        ...
    
    @classmethod
    @property
    def PARTIALLYOCCUPIED(cls) -> IfcResourceConsumptionEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTOCCUPIED(cls) -> IfcResourceConsumptionEnum2X3:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcResourceConsumptionEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcResourceConsumptionEnum2X3:
        ...
    
    ...

class IfcRibPlateDirectionEnum2X3:
    '''IfcRibPlateDirectionEnum'''
    
    @classmethod
    @property
    def DIRECTION_X(cls) -> IfcRibPlateDirectionEnum2X3:
        ...
    
    @classmethod
    @property
    def DIRECTION_Y(cls) -> IfcRibPlateDirectionEnum2X3:
        ...
    
    ...

class IfcRoleEnum2X3:
    '''IfcRoleEnum'''
    
    @classmethod
    @property
    def SUPPLIER(cls) -> IfcRoleEnum2X3:
        ...
    
    @classmethod
    @property
    def MANUFACTURER(cls) -> IfcRoleEnum2X3:
        ...
    
    @classmethod
    @property
    def CONTRACTOR(cls) -> IfcRoleEnum2X3:
        ...
    
    @classmethod
    @property
    def SUBCONTRACTOR(cls) -> IfcRoleEnum2X3:
        ...
    
    @classmethod
    @property
    def ARCHITECT(cls) -> IfcRoleEnum2X3:
        ...
    
    @classmethod
    @property
    def STRUCTURALENGINEER(cls) -> IfcRoleEnum2X3:
        ...
    
    @classmethod
    @property
    def COSTENGINEER(cls) -> IfcRoleEnum2X3:
        ...
    
    @classmethod
    @property
    def CLIENT(cls) -> IfcRoleEnum2X3:
        ...
    
    @classmethod
    @property
    def BUILDINGOWNER(cls) -> IfcRoleEnum2X3:
        ...
    
    @classmethod
    @property
    def BUILDINGOPERATOR(cls) -> IfcRoleEnum2X3:
        ...
    
    @classmethod
    @property
    def MECHANICALENGINEER(cls) -> IfcRoleEnum2X3:
        ...
    
    @classmethod
    @property
    def ELECTRICALENGINEER(cls) -> IfcRoleEnum2X3:
        ...
    
    @classmethod
    @property
    def PROJECTMANAGER(cls) -> IfcRoleEnum2X3:
        ...
    
    @classmethod
    @property
    def FACILITIESMANAGER(cls) -> IfcRoleEnum2X3:
        ...
    
    @classmethod
    @property
    def CIVILENGINEER(cls) -> IfcRoleEnum2X3:
        ...
    
    @classmethod
    @property
    def COMISSIONINGENGINEER(cls) -> IfcRoleEnum2X3:
        ...
    
    @classmethod
    @property
    def ENGINEER(cls) -> IfcRoleEnum2X3:
        ...
    
    @classmethod
    @property
    def OWNER(cls) -> IfcRoleEnum2X3:
        ...
    
    @classmethod
    @property
    def CONSULTANT(cls) -> IfcRoleEnum2X3:
        ...
    
    @classmethod
    @property
    def CONSTRUCTIONMANAGER(cls) -> IfcRoleEnum2X3:
        ...
    
    @classmethod
    @property
    def FIELDCONSTRUCTIONMANAGER(cls) -> IfcRoleEnum2X3:
        ...
    
    @classmethod
    @property
    def RESELLER(cls) -> IfcRoleEnum2X3:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcRoleEnum2X3:
        ...
    
    ...

class IfcRoofTypeEnum2X3:
    '''IfcRoofTypeEnum'''
    
    @classmethod
    @property
    def FLAT_ROOF(cls) -> IfcRoofTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def SHED_ROOF(cls) -> IfcRoofTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def GABLE_ROOF(cls) -> IfcRoofTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def HIP_ROOF(cls) -> IfcRoofTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def HIPPED_GABLE_ROOF(cls) -> IfcRoofTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def GAMBREL_ROOF(cls) -> IfcRoofTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def MANSARD_ROOF(cls) -> IfcRoofTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def BARREL_ROOF(cls) -> IfcRoofTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def RAINBOW_ROOF(cls) -> IfcRoofTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def BUTTERFLY_ROOF(cls) -> IfcRoofTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def PAVILION_ROOF(cls) -> IfcRoofTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def DOME_ROOF(cls) -> IfcRoofTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def FREEFORM(cls) -> IfcRoofTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcRoofTypeEnum2X3:
        ...
    
    ...

class IfcSIPrefix2X3:
    '''IfcSIPrefix'''
    
    @classmethod
    @property
    def EXA(cls) -> IfcSIPrefix2X3:
        ...
    
    @classmethod
    @property
    def PETA(cls) -> IfcSIPrefix2X3:
        ...
    
    @classmethod
    @property
    def TERA(cls) -> IfcSIPrefix2X3:
        ...
    
    @classmethod
    @property
    def GIGA(cls) -> IfcSIPrefix2X3:
        ...
    
    @classmethod
    @property
    def MEGA(cls) -> IfcSIPrefix2X3:
        ...
    
    @classmethod
    @property
    def KILO(cls) -> IfcSIPrefix2X3:
        ...
    
    @classmethod
    @property
    def HECTO(cls) -> IfcSIPrefix2X3:
        ...
    
    @classmethod
    @property
    def DECA(cls) -> IfcSIPrefix2X3:
        ...
    
    @classmethod
    @property
    def DECI(cls) -> IfcSIPrefix2X3:
        ...
    
    @classmethod
    @property
    def CENTI(cls) -> IfcSIPrefix2X3:
        ...
    
    @classmethod
    @property
    def MILLI(cls) -> IfcSIPrefix2X3:
        ...
    
    @classmethod
    @property
    def MICRO(cls) -> IfcSIPrefix2X3:
        ...
    
    @classmethod
    @property
    def NANO(cls) -> IfcSIPrefix2X3:
        ...
    
    @classmethod
    @property
    def PICO(cls) -> IfcSIPrefix2X3:
        ...
    
    @classmethod
    @property
    def FEMTO(cls) -> IfcSIPrefix2X3:
        ...
    
    @classmethod
    @property
    def ATTO(cls) -> IfcSIPrefix2X3:
        ...
    
    ...

class IfcSIUnitName2X3:
    '''IfcSIUnitName'''
    
    @classmethod
    @property
    def AMPERE(cls) -> IfcSIUnitName2X3:
        ...
    
    @classmethod
    @property
    def BECQUEREL(cls) -> IfcSIUnitName2X3:
        ...
    
    @classmethod
    @property
    def CANDELA(cls) -> IfcSIUnitName2X3:
        ...
    
    @classmethod
    @property
    def COULOMB(cls) -> IfcSIUnitName2X3:
        ...
    
    @classmethod
    @property
    def CUBIC_METRE(cls) -> IfcSIUnitName2X3:
        ...
    
    @classmethod
    @property
    def DEGREE_CELSIUS(cls) -> IfcSIUnitName2X3:
        ...
    
    @classmethod
    @property
    def FARAD(cls) -> IfcSIUnitName2X3:
        ...
    
    @classmethod
    @property
    def GRAM(cls) -> IfcSIUnitName2X3:
        ...
    
    @classmethod
    @property
    def GRAY(cls) -> IfcSIUnitName2X3:
        ...
    
    @classmethod
    @property
    def HENRY(cls) -> IfcSIUnitName2X3:
        ...
    
    @classmethod
    @property
    def HERTZ(cls) -> IfcSIUnitName2X3:
        ...
    
    @classmethod
    @property
    def JOULE(cls) -> IfcSIUnitName2X3:
        ...
    
    @classmethod
    @property
    def KELVIN(cls) -> IfcSIUnitName2X3:
        ...
    
    @classmethod
    @property
    def LUMEN(cls) -> IfcSIUnitName2X3:
        ...
    
    @classmethod
    @property
    def LUX(cls) -> IfcSIUnitName2X3:
        ...
    
    @classmethod
    @property
    def METRE(cls) -> IfcSIUnitName2X3:
        ...
    
    @classmethod
    @property
    def MOLE(cls) -> IfcSIUnitName2X3:
        ...
    
    @classmethod
    @property
    def NEWTON(cls) -> IfcSIUnitName2X3:
        ...
    
    @classmethod
    @property
    def OHM(cls) -> IfcSIUnitName2X3:
        ...
    
    @classmethod
    @property
    def PASCAL(cls) -> IfcSIUnitName2X3:
        ...
    
    @classmethod
    @property
    def RADIAN(cls) -> IfcSIUnitName2X3:
        ...
    
    @classmethod
    @property
    def SECOND(cls) -> IfcSIUnitName2X3:
        ...
    
    @classmethod
    @property
    def SIEMENS(cls) -> IfcSIUnitName2X3:
        ...
    
    @classmethod
    @property
    def SIEVERT(cls) -> IfcSIUnitName2X3:
        ...
    
    @classmethod
    @property
    def SQUARE_METRE(cls) -> IfcSIUnitName2X3:
        ...
    
    @classmethod
    @property
    def STERADIAN(cls) -> IfcSIUnitName2X3:
        ...
    
    @classmethod
    @property
    def TESLA(cls) -> IfcSIUnitName2X3:
        ...
    
    @classmethod
    @property
    def VOLT(cls) -> IfcSIUnitName2X3:
        ...
    
    @classmethod
    @property
    def WATT(cls) -> IfcSIUnitName2X3:
        ...
    
    @classmethod
    @property
    def WEBER(cls) -> IfcSIUnitName2X3:
        ...
    
    ...

class IfcSanitaryTerminalTypeEnum2X3:
    '''IfcSanitaryTerminalTypeEnum'''
    
    @classmethod
    @property
    def BATH(cls) -> IfcSanitaryTerminalTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def BIDET(cls) -> IfcSanitaryTerminalTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def CISTERN(cls) -> IfcSanitaryTerminalTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def SHOWER(cls) -> IfcSanitaryTerminalTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def SINK(cls) -> IfcSanitaryTerminalTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def SANITARYFOUNTAIN(cls) -> IfcSanitaryTerminalTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def TOILETPAN(cls) -> IfcSanitaryTerminalTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def URINAL(cls) -> IfcSanitaryTerminalTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def WASHHANDBASIN(cls) -> IfcSanitaryTerminalTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def WCSEAT(cls) -> IfcSanitaryTerminalTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcSanitaryTerminalTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcSanitaryTerminalTypeEnum2X3:
        ...
    
    ...

class IfcSectionTypeEnum2X3:
    '''IfcSectionTypeEnum'''
    
    @classmethod
    @property
    def UNIFORM(cls) -> IfcSectionTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def TAPERED(cls) -> IfcSectionTypeEnum2X3:
        ...
    
    ...

class IfcSensorTypeEnum2X3:
    '''IfcSensorTypeEnum'''
    
    @classmethod
    @property
    def CO2SENSOR(cls) -> IfcSensorTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def FIRESENSOR(cls) -> IfcSensorTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def FLOWSENSOR(cls) -> IfcSensorTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def GASSENSOR(cls) -> IfcSensorTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def HEATSENSOR(cls) -> IfcSensorTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def HUMIDITYSENSOR(cls) -> IfcSensorTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def LIGHTSENSOR(cls) -> IfcSensorTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def MOISTURESENSOR(cls) -> IfcSensorTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def MOVEMENTSENSOR(cls) -> IfcSensorTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def PRESSURESENSOR(cls) -> IfcSensorTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def SMOKESENSOR(cls) -> IfcSensorTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def SOUNDSENSOR(cls) -> IfcSensorTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def TEMPERATURESENSOR(cls) -> IfcSensorTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcSensorTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcSensorTypeEnum2X3:
        ...
    
    ...

class IfcSequenceEnum2X3:
    '''IfcSequenceEnum'''
    
    @classmethod
    @property
    def START_START(cls) -> IfcSequenceEnum2X3:
        ...
    
    @classmethod
    @property
    def START_FINISH(cls) -> IfcSequenceEnum2X3:
        ...
    
    @classmethod
    @property
    def FINISH_START(cls) -> IfcSequenceEnum2X3:
        ...
    
    @classmethod
    @property
    def FINISH_FINISH(cls) -> IfcSequenceEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcSequenceEnum2X3:
        ...
    
    ...

class IfcServiceLifeFactorTypeEnum2X3:
    '''IfcServiceLifeFactorTypeEnum'''
    
    @classmethod
    @property
    def A_QUALITYOFCOMPONENTS(cls) -> IfcServiceLifeFactorTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def B_DESIGNLEVEL(cls) -> IfcServiceLifeFactorTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def C_WORKEXECUTIONLEVEL(cls) -> IfcServiceLifeFactorTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def D_INDOORENVIRONMENT(cls) -> IfcServiceLifeFactorTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def E_OUTDOORENVIRONMENT(cls) -> IfcServiceLifeFactorTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def F_INUSECONDITIONS(cls) -> IfcServiceLifeFactorTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def G_MAINTENANCELEVEL(cls) -> IfcServiceLifeFactorTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcServiceLifeFactorTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcServiceLifeFactorTypeEnum2X3:
        ...
    
    ...

class IfcServiceLifeTypeEnum2X3:
    '''IfcServiceLifeTypeEnum'''
    
    @classmethod
    @property
    def ACTUALSERVICELIFE(cls) -> IfcServiceLifeTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def EXPECTEDSERVICELIFE(cls) -> IfcServiceLifeTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def OPTIMISTICREFERENCESERVICELIFE(cls) -> IfcServiceLifeTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def PESSIMISTICREFERENCESERVICELIFE(cls) -> IfcServiceLifeTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def REFERENCESERVICELIFE(cls) -> IfcServiceLifeTypeEnum2X3:
        ...
    
    ...

class IfcSlabTypeEnum2X3:
    '''IfcSlabTypeEnum'''
    
    @classmethod
    @property
    def FLOOR(cls) -> IfcSlabTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def ROOF(cls) -> IfcSlabTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def LANDING(cls) -> IfcSlabTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def BASESLAB(cls) -> IfcSlabTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcSlabTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcSlabTypeEnum2X3:
        ...
    
    ...

class IfcSoundScaleEnum2X3:
    '''IfcSoundScaleEnum'''
    
    @classmethod
    @property
    def DBA(cls) -> IfcSoundScaleEnum2X3:
        ...
    
    @classmethod
    @property
    def DBB(cls) -> IfcSoundScaleEnum2X3:
        ...
    
    @classmethod
    @property
    def DBC(cls) -> IfcSoundScaleEnum2X3:
        ...
    
    @classmethod
    @property
    def NC(cls) -> IfcSoundScaleEnum2X3:
        ...
    
    @classmethod
    @property
    def NR(cls) -> IfcSoundScaleEnum2X3:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcSoundScaleEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcSoundScaleEnum2X3:
        ...
    
    ...

class IfcSpaceHeaterTypeEnum2X3:
    '''IfcSpaceHeaterTypeEnum'''
    
    @classmethod
    @property
    def SECTIONALRADIATOR(cls) -> IfcSpaceHeaterTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def PANELRADIATOR(cls) -> IfcSpaceHeaterTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def TUBULARRADIATOR(cls) -> IfcSpaceHeaterTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def CONVECTOR(cls) -> IfcSpaceHeaterTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def BASEBOARDHEATER(cls) -> IfcSpaceHeaterTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def FINNEDTUBEUNIT(cls) -> IfcSpaceHeaterTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def UNITHEATER(cls) -> IfcSpaceHeaterTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcSpaceHeaterTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcSpaceHeaterTypeEnum2X3:
        ...
    
    ...

class IfcSpaceTypeEnum2X3:
    '''IfcSpaceTypeEnum'''
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcSpaceTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcSpaceTypeEnum2X3:
        ...
    
    ...

class IfcStackTerminalTypeEnum2X3:
    '''IfcStackTerminalTypeEnum'''
    
    @classmethod
    @property
    def BIRDCAGE(cls) -> IfcStackTerminalTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def COWL(cls) -> IfcStackTerminalTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def RAINWATERHOPPER(cls) -> IfcStackTerminalTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcStackTerminalTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcStackTerminalTypeEnum2X3:
        ...
    
    ...

class IfcStairFlightTypeEnum2X3:
    '''IfcStairFlightTypeEnum'''
    
    @classmethod
    @property
    def STRAIGHT(cls) -> IfcStairFlightTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def WINDER(cls) -> IfcStairFlightTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def SPIRAL(cls) -> IfcStairFlightTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def CURVED(cls) -> IfcStairFlightTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def FREEFORM(cls) -> IfcStairFlightTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcStairFlightTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcStairFlightTypeEnum2X3:
        ...
    
    ...

class IfcStairTypeEnum2X3:
    '''IfcStairTypeEnum'''
    
    @classmethod
    @property
    def STRAIGHT_RUN_STAIR(cls) -> IfcStairTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def TWO_STRAIGHT_RUN_STAIR(cls) -> IfcStairTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def QUARTER_WINDING_STAIR(cls) -> IfcStairTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def QUARTER_TURN_STAIR(cls) -> IfcStairTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def HALF_WINDING_STAIR(cls) -> IfcStairTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def HALF_TURN_STAIR(cls) -> IfcStairTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def TWO_QUARTER_WINDING_STAIR(cls) -> IfcStairTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def TWO_QUARTER_TURN_STAIR(cls) -> IfcStairTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def THREE_QUARTER_WINDING_STAIR(cls) -> IfcStairTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def THREE_QUARTER_TURN_STAIR(cls) -> IfcStairTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def SPIRAL_STAIR(cls) -> IfcStairTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def DOUBLE_RETURN_STAIR(cls) -> IfcStairTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def CURVED_RUN_STAIR(cls) -> IfcStairTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def TWO_CURVED_RUN_STAIR(cls) -> IfcStairTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcStairTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcStairTypeEnum2X3:
        ...
    
    ...

class IfcStateEnum2X3:
    '''IfcStateEnum'''
    
    @classmethod
    @property
    def READWRITE(cls) -> IfcStateEnum2X3:
        ...
    
    @classmethod
    @property
    def READONLY(cls) -> IfcStateEnum2X3:
        ...
    
    @classmethod
    @property
    def LOCKED(cls) -> IfcStateEnum2X3:
        ...
    
    @classmethod
    @property
    def READWRITELOCKED(cls) -> IfcStateEnum2X3:
        ...
    
    @classmethod
    @property
    def READONLYLOCKED(cls) -> IfcStateEnum2X3:
        ...
    
    ...

class IfcStructuralCurveTypeEnum2X3:
    '''IfcStructuralCurveTypeEnum'''
    
    @classmethod
    @property
    def RIGID_JOINED_MEMBER(cls) -> IfcStructuralCurveTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def PIN_JOINED_MEMBER(cls) -> IfcStructuralCurveTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def CABLE(cls) -> IfcStructuralCurveTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def TENSION_MEMBER(cls) -> IfcStructuralCurveTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def COMPRESSION_MEMBER(cls) -> IfcStructuralCurveTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcStructuralCurveTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcStructuralCurveTypeEnum2X3:
        ...
    
    ...

class IfcStructuralSurfaceTypeEnum2X3:
    '''IfcStructuralSurfaceTypeEnum'''
    
    @classmethod
    @property
    def BENDING_ELEMENT(cls) -> IfcStructuralSurfaceTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def MEMBRANE_ELEMENT(cls) -> IfcStructuralSurfaceTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def SHELL(cls) -> IfcStructuralSurfaceTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcStructuralSurfaceTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcStructuralSurfaceTypeEnum2X3:
        ...
    
    ...

class IfcSurfaceSide2X3:
    '''IfcSurfaceSide'''
    
    @classmethod
    @property
    def POSITIVE(cls) -> IfcSurfaceSide2X3:
        ...
    
    @classmethod
    @property
    def NEGATIVE(cls) -> IfcSurfaceSide2X3:
        ...
    
    @classmethod
    @property
    def BOTH(cls) -> IfcSurfaceSide2X3:
        ...
    
    ...

class IfcSurfaceTextureEnum2X3:
    '''IfcSurfaceTextureEnum'''
    
    @classmethod
    @property
    def BUMP(cls) -> IfcSurfaceTextureEnum2X3:
        ...
    
    @classmethod
    @property
    def OPACITY(cls) -> IfcSurfaceTextureEnum2X3:
        ...
    
    @classmethod
    @property
    def REFLECTION(cls) -> IfcSurfaceTextureEnum2X3:
        ...
    
    @classmethod
    @property
    def SELFILLUMINATION(cls) -> IfcSurfaceTextureEnum2X3:
        ...
    
    @classmethod
    @property
    def SHININESS(cls) -> IfcSurfaceTextureEnum2X3:
        ...
    
    @classmethod
    @property
    def SPECULAR(cls) -> IfcSurfaceTextureEnum2X3:
        ...
    
    @classmethod
    @property
    def TEXTURE(cls) -> IfcSurfaceTextureEnum2X3:
        ...
    
    @classmethod
    @property
    def TRANSPARENCYMAP(cls) -> IfcSurfaceTextureEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcSurfaceTextureEnum2X3:
        ...
    
    ...

class IfcSwitchingDeviceTypeEnum2X3:
    '''IfcSwitchingDeviceTypeEnum'''
    
    @classmethod
    @property
    def CONTACTOR(cls) -> IfcSwitchingDeviceTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def EMERGENCYSTOP(cls) -> IfcSwitchingDeviceTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def STARTER(cls) -> IfcSwitchingDeviceTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def SWITCHDISCONNECTOR(cls) -> IfcSwitchingDeviceTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def TOGGLESWITCH(cls) -> IfcSwitchingDeviceTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcSwitchingDeviceTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcSwitchingDeviceTypeEnum2X3:
        ...
    
    ...

class IfcTankTypeEnum2X3:
    '''IfcTankTypeEnum'''
    
    @classmethod
    @property
    def PREFORMED(cls) -> IfcTankTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def SECTIONAL(cls) -> IfcTankTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def EXPANSION(cls) -> IfcTankTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def PRESSUREVESSEL(cls) -> IfcTankTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcTankTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcTankTypeEnum2X3:
        ...
    
    ...

class IfcTendonTypeEnum2X3:
    '''IfcTendonTypeEnum'''
    
    @classmethod
    @property
    def STRAND(cls) -> IfcTendonTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def WIRE(cls) -> IfcTendonTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def BAR(cls) -> IfcTendonTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def COATED(cls) -> IfcTendonTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcTendonTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcTendonTypeEnum2X3:
        ...
    
    ...

class IfcTextPath2X3:
    '''IfcTextPath'''
    
    @classmethod
    @property
    def LEFT(cls) -> IfcTextPath2X3:
        ...
    
    @classmethod
    @property
    def RIGHT(cls) -> IfcTextPath2X3:
        ...
    
    @classmethod
    @property
    def UP(cls) -> IfcTextPath2X3:
        ...
    
    @classmethod
    @property
    def DOWN(cls) -> IfcTextPath2X3:
        ...
    
    ...

class IfcThermalLoadSourceEnum2X3:
    '''IfcThermalLoadSourceEnum'''
    
    @classmethod
    @property
    def PEOPLE(cls) -> IfcThermalLoadSourceEnum2X3:
        ...
    
    @classmethod
    @property
    def LIGHTING(cls) -> IfcThermalLoadSourceEnum2X3:
        ...
    
    @classmethod
    @property
    def EQUIPMENT(cls) -> IfcThermalLoadSourceEnum2X3:
        ...
    
    @classmethod
    @property
    def VENTILATIONINDOORAIR(cls) -> IfcThermalLoadSourceEnum2X3:
        ...
    
    @classmethod
    @property
    def VENTILATIONOUTSIDEAIR(cls) -> IfcThermalLoadSourceEnum2X3:
        ...
    
    @classmethod
    @property
    def RECIRCULATEDAIR(cls) -> IfcThermalLoadSourceEnum2X3:
        ...
    
    @classmethod
    @property
    def EXHAUSTAIR(cls) -> IfcThermalLoadSourceEnum2X3:
        ...
    
    @classmethod
    @property
    def AIREXCHANGERATE(cls) -> IfcThermalLoadSourceEnum2X3:
        ...
    
    @classmethod
    @property
    def DRYBULBTEMPERATURE(cls) -> IfcThermalLoadSourceEnum2X3:
        ...
    
    @classmethod
    @property
    def RELATIVEHUMIDITY(cls) -> IfcThermalLoadSourceEnum2X3:
        ...
    
    @classmethod
    @property
    def INFILTRATION(cls) -> IfcThermalLoadSourceEnum2X3:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcThermalLoadSourceEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcThermalLoadSourceEnum2X3:
        ...
    
    ...

class IfcThermalLoadTypeEnum2X3:
    '''IfcThermalLoadTypeEnum'''
    
    @classmethod
    @property
    def SENSIBLE(cls) -> IfcThermalLoadTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def LATENT(cls) -> IfcThermalLoadTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def RADIANT(cls) -> IfcThermalLoadTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcThermalLoadTypeEnum2X3:
        ...
    
    ...

class IfcTimeSeriesDataTypeEnum2X3:
    '''IfcTimeSeriesDataTypeEnum'''
    
    @classmethod
    @property
    def CONTINUOUS(cls) -> IfcTimeSeriesDataTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def DISCRETE(cls) -> IfcTimeSeriesDataTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def DISCRETEBINARY(cls) -> IfcTimeSeriesDataTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def PIECEWISEBINARY(cls) -> IfcTimeSeriesDataTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def PIECEWISECONSTANT(cls) -> IfcTimeSeriesDataTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def PIECEWISECONTINUOUS(cls) -> IfcTimeSeriesDataTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcTimeSeriesDataTypeEnum2X3:
        ...
    
    ...

class IfcTimeSeriesScheduleTypeEnum2X3:
    '''IfcTimeSeriesScheduleTypeEnum'''
    
    @classmethod
    @property
    def ANNUAL(cls) -> IfcTimeSeriesScheduleTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def MONTHLY(cls) -> IfcTimeSeriesScheduleTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def WEEKLY(cls) -> IfcTimeSeriesScheduleTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def DAILY(cls) -> IfcTimeSeriesScheduleTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcTimeSeriesScheduleTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcTimeSeriesScheduleTypeEnum2X3:
        ...
    
    ...

class IfcTransformerTypeEnum2X3:
    '''IfcTransformerTypeEnum'''
    
    @classmethod
    @property
    def CURRENT(cls) -> IfcTransformerTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def FREQUENCY(cls) -> IfcTransformerTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def VOLTAGE(cls) -> IfcTransformerTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcTransformerTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcTransformerTypeEnum2X3:
        ...
    
    ...

class IfcTransitionCode2X3:
    '''IfcTransitionCode'''
    
    @classmethod
    @property
    def DISCONTINUOUS(cls) -> IfcTransitionCode2X3:
        ...
    
    @classmethod
    @property
    def CONTINUOUS(cls) -> IfcTransitionCode2X3:
        ...
    
    @classmethod
    @property
    def CONTSAMEGRADIENT(cls) -> IfcTransitionCode2X3:
        ...
    
    @classmethod
    @property
    def CONTSAMEGRADIENTSAMECURVATURE(cls) -> IfcTransitionCode2X3:
        ...
    
    ...

class IfcTransportElementTypeEnum2X3:
    '''IfcTransportElementTypeEnum'''
    
    @classmethod
    @property
    def ELEVATOR(cls) -> IfcTransportElementTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def ESCALATOR(cls) -> IfcTransportElementTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def MOVINGWALKWAY(cls) -> IfcTransportElementTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcTransportElementTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcTransportElementTypeEnum2X3:
        ...
    
    ...

class IfcTrimmingPreference2X3:
    '''IfcTrimmingPreference'''
    
    @classmethod
    @property
    def CARTESIAN(cls) -> IfcTrimmingPreference2X3:
        ...
    
    @classmethod
    @property
    def PARAMETER(cls) -> IfcTrimmingPreference2X3:
        ...
    
    @classmethod
    @property
    def UNSPECIFIED(cls) -> IfcTrimmingPreference2X3:
        ...
    
    ...

class IfcTubeBundleTypeEnum2X3:
    '''IfcTubeBundleTypeEnum'''
    
    @classmethod
    @property
    def FINNED(cls) -> IfcTubeBundleTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcTubeBundleTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcTubeBundleTypeEnum2X3:
        ...
    
    ...

class IfcUnitEnum2X3:
    '''IfcUnitEnum'''
    
    @classmethod
    @property
    def ABSORBEDDOSEUNIT(cls) -> IfcUnitEnum2X3:
        ...
    
    @classmethod
    @property
    def AMOUNTOFSUBSTANCEUNIT(cls) -> IfcUnitEnum2X3:
        ...
    
    @classmethod
    @property
    def AREAUNIT(cls) -> IfcUnitEnum2X3:
        ...
    
    @classmethod
    @property
    def DOSEEQUIVALENTUNIT(cls) -> IfcUnitEnum2X3:
        ...
    
    @classmethod
    @property
    def ELECTRICCAPACITANCEUNIT(cls) -> IfcUnitEnum2X3:
        ...
    
    @classmethod
    @property
    def ELECTRICCHARGEUNIT(cls) -> IfcUnitEnum2X3:
        ...
    
    @classmethod
    @property
    def ELECTRICCONDUCTANCEUNIT(cls) -> IfcUnitEnum2X3:
        ...
    
    @classmethod
    @property
    def ELECTRICCURRENTUNIT(cls) -> IfcUnitEnum2X3:
        ...
    
    @classmethod
    @property
    def ELECTRICRESISTANCEUNIT(cls) -> IfcUnitEnum2X3:
        ...
    
    @classmethod
    @property
    def ELECTRICVOLTAGEUNIT(cls) -> IfcUnitEnum2X3:
        ...
    
    @classmethod
    @property
    def ENERGYUNIT(cls) -> IfcUnitEnum2X3:
        ...
    
    @classmethod
    @property
    def FORCEUNIT(cls) -> IfcUnitEnum2X3:
        ...
    
    @classmethod
    @property
    def FREQUENCYUNIT(cls) -> IfcUnitEnum2X3:
        ...
    
    @classmethod
    @property
    def ILLUMINANCEUNIT(cls) -> IfcUnitEnum2X3:
        ...
    
    @classmethod
    @property
    def INDUCTANCEUNIT(cls) -> IfcUnitEnum2X3:
        ...
    
    @classmethod
    @property
    def LENGTHUNIT(cls) -> IfcUnitEnum2X3:
        ...
    
    @classmethod
    @property
    def LUMINOUSFLUXUNIT(cls) -> IfcUnitEnum2X3:
        ...
    
    @classmethod
    @property
    def LUMINOUSINTENSITYUNIT(cls) -> IfcUnitEnum2X3:
        ...
    
    @classmethod
    @property
    def MAGNETICFLUXDENSITYUNIT(cls) -> IfcUnitEnum2X3:
        ...
    
    @classmethod
    @property
    def MAGNETICFLUXUNIT(cls) -> IfcUnitEnum2X3:
        ...
    
    @classmethod
    @property
    def MASSUNIT(cls) -> IfcUnitEnum2X3:
        ...
    
    @classmethod
    @property
    def PLANEANGLEUNIT(cls) -> IfcUnitEnum2X3:
        ...
    
    @classmethod
    @property
    def POWERUNIT(cls) -> IfcUnitEnum2X3:
        ...
    
    @classmethod
    @property
    def PRESSUREUNIT(cls) -> IfcUnitEnum2X3:
        ...
    
    @classmethod
    @property
    def RADIOACTIVITYUNIT(cls) -> IfcUnitEnum2X3:
        ...
    
    @classmethod
    @property
    def SOLIDANGLEUNIT(cls) -> IfcUnitEnum2X3:
        ...
    
    @classmethod
    @property
    def THERMODYNAMICTEMPERATUREUNIT(cls) -> IfcUnitEnum2X3:
        ...
    
    @classmethod
    @property
    def TIMEUNIT(cls) -> IfcUnitEnum2X3:
        ...
    
    @classmethod
    @property
    def VOLUMEUNIT(cls) -> IfcUnitEnum2X3:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcUnitEnum2X3:
        ...
    
    ...

class IfcUnitaryEquipmentTypeEnum2X3:
    '''IfcUnitaryEquipmentTypeEnum'''
    
    @classmethod
    @property
    def AIRHANDLER(cls) -> IfcUnitaryEquipmentTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def AIRCONDITIONINGUNIT(cls) -> IfcUnitaryEquipmentTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def SPLITSYSTEM(cls) -> IfcUnitaryEquipmentTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def ROOFTOPUNIT(cls) -> IfcUnitaryEquipmentTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcUnitaryEquipmentTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcUnitaryEquipmentTypeEnum2X3:
        ...
    
    ...

class IfcValveTypeEnum2X3:
    '''IfcValveTypeEnum'''
    
    @classmethod
    @property
    def AIRRELEASE(cls) -> IfcValveTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def ANTIVACUUM(cls) -> IfcValveTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def CHANGEOVER(cls) -> IfcValveTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def CHECK(cls) -> IfcValveTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def COMMISSIONING(cls) -> IfcValveTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def DIVERTING(cls) -> IfcValveTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def DRAWOFFCOCK(cls) -> IfcValveTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def DOUBLECHECK(cls) -> IfcValveTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def DOUBLEREGULATING(cls) -> IfcValveTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def FAUCET(cls) -> IfcValveTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def FLUSHING(cls) -> IfcValveTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def GASCOCK(cls) -> IfcValveTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def GASTAP(cls) -> IfcValveTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def ISOLATING(cls) -> IfcValveTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def MIXING(cls) -> IfcValveTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def PRESSUREREDUCING(cls) -> IfcValveTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def PRESSURERELIEF(cls) -> IfcValveTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def REGULATING(cls) -> IfcValveTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def SAFETYCUTOFF(cls) -> IfcValveTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def STEAMTRAP(cls) -> IfcValveTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def STOPCOCK(cls) -> IfcValveTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcValveTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcValveTypeEnum2X3:
        ...
    
    ...

class IfcVibrationIsolatorTypeEnum2X3:
    '''IfcVibrationIsolatorTypeEnum'''
    
    @classmethod
    @property
    def COMPRESSION(cls) -> IfcVibrationIsolatorTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def SPRING(cls) -> IfcVibrationIsolatorTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcVibrationIsolatorTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcVibrationIsolatorTypeEnum2X3:
        ...
    
    ...

class IfcWallTypeEnum2X3:
    '''IfcWallTypeEnum'''
    
    @classmethod
    @property
    def STANDARD(cls) -> IfcWallTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def POLYGONAL(cls) -> IfcWallTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def SHEAR(cls) -> IfcWallTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def ELEMENTEDWALL(cls) -> IfcWallTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def PLUMBINGWALL(cls) -> IfcWallTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcWallTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcWallTypeEnum2X3:
        ...
    
    ...

class IfcWasteTerminalTypeEnum2X3:
    '''IfcWasteTerminalTypeEnum'''
    
    @classmethod
    @property
    def FLOORTRAP(cls) -> IfcWasteTerminalTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def FLOORWASTE(cls) -> IfcWasteTerminalTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def GULLYSUMP(cls) -> IfcWasteTerminalTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def GULLYTRAP(cls) -> IfcWasteTerminalTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def GREASEINTERCEPTOR(cls) -> IfcWasteTerminalTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def OILINTERCEPTOR(cls) -> IfcWasteTerminalTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def PETROLINTERCEPTOR(cls) -> IfcWasteTerminalTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def ROOFDRAIN(cls) -> IfcWasteTerminalTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def WASTEDISPOSALUNIT(cls) -> IfcWasteTerminalTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def WASTETRAP(cls) -> IfcWasteTerminalTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcWasteTerminalTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcWasteTerminalTypeEnum2X3:
        ...
    
    ...

class IfcWindowPanelOperationEnum2X3:
    '''IfcWindowPanelOperationEnum'''
    
    @classmethod
    @property
    def SIDEHUNGRIGHTHAND(cls) -> IfcWindowPanelOperationEnum2X3:
        ...
    
    @classmethod
    @property
    def SIDEHUNGLEFTHAND(cls) -> IfcWindowPanelOperationEnum2X3:
        ...
    
    @classmethod
    @property
    def TILTANDTURNRIGHTHAND(cls) -> IfcWindowPanelOperationEnum2X3:
        ...
    
    @classmethod
    @property
    def TILTANDTURNLEFTHAND(cls) -> IfcWindowPanelOperationEnum2X3:
        ...
    
    @classmethod
    @property
    def TOPHUNG(cls) -> IfcWindowPanelOperationEnum2X3:
        ...
    
    @classmethod
    @property
    def BOTTOMHUNG(cls) -> IfcWindowPanelOperationEnum2X3:
        ...
    
    @classmethod
    @property
    def PIVOTHORIZONTAL(cls) -> IfcWindowPanelOperationEnum2X3:
        ...
    
    @classmethod
    @property
    def PIVOTVERTICAL(cls) -> IfcWindowPanelOperationEnum2X3:
        ...
    
    @classmethod
    @property
    def SLIDINGHORIZONTAL(cls) -> IfcWindowPanelOperationEnum2X3:
        ...
    
    @classmethod
    @property
    def SLIDINGVERTICAL(cls) -> IfcWindowPanelOperationEnum2X3:
        ...
    
    @classmethod
    @property
    def REMOVABLECASEMENT(cls) -> IfcWindowPanelOperationEnum2X3:
        ...
    
    @classmethod
    @property
    def FIXEDCASEMENT(cls) -> IfcWindowPanelOperationEnum2X3:
        ...
    
    @classmethod
    @property
    def OTHEROPERATION(cls) -> IfcWindowPanelOperationEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcWindowPanelOperationEnum2X3:
        ...
    
    ...

class IfcWindowPanelPositionEnum2X3:
    '''IfcWindowPanelPositionEnum'''
    
    @classmethod
    @property
    def LEFT(cls) -> IfcWindowPanelPositionEnum2X3:
        ...
    
    @classmethod
    @property
    def MIDDLE(cls) -> IfcWindowPanelPositionEnum2X3:
        ...
    
    @classmethod
    @property
    def RIGHT(cls) -> IfcWindowPanelPositionEnum2X3:
        ...
    
    @classmethod
    @property
    def BOTTOM(cls) -> IfcWindowPanelPositionEnum2X3:
        ...
    
    @classmethod
    @property
    def TOP(cls) -> IfcWindowPanelPositionEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcWindowPanelPositionEnum2X3:
        ...
    
    ...

class IfcWindowStyleConstructionEnum2X3:
    '''IfcWindowStyleConstructionEnum'''
    
    @classmethod
    @property
    def ALUMINIUM(cls) -> IfcWindowStyleConstructionEnum2X3:
        ...
    
    @classmethod
    @property
    def HIGH_GRADE_STEEL(cls) -> IfcWindowStyleConstructionEnum2X3:
        ...
    
    @classmethod
    @property
    def STEEL(cls) -> IfcWindowStyleConstructionEnum2X3:
        ...
    
    @classmethod
    @property
    def WOOD(cls) -> IfcWindowStyleConstructionEnum2X3:
        ...
    
    @classmethod
    @property
    def ALUMINIUM_WOOD(cls) -> IfcWindowStyleConstructionEnum2X3:
        ...
    
    @classmethod
    @property
    def PLASTIC(cls) -> IfcWindowStyleConstructionEnum2X3:
        ...
    
    @classmethod
    @property
    def OTHER_CONSTRUCTION(cls) -> IfcWindowStyleConstructionEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcWindowStyleConstructionEnum2X3:
        ...
    
    ...

class IfcWindowStyleOperationEnum2X3:
    '''IfcWindowStyleOperationEnum'''
    
    @classmethod
    @property
    def SINGLE_PANEL(cls) -> IfcWindowStyleOperationEnum2X3:
        ...
    
    @classmethod
    @property
    def DOUBLE_PANEL_VERTICAL(cls) -> IfcWindowStyleOperationEnum2X3:
        ...
    
    @classmethod
    @property
    def DOUBLE_PANEL_HORIZONTAL(cls) -> IfcWindowStyleOperationEnum2X3:
        ...
    
    @classmethod
    @property
    def TRIPLE_PANEL_VERTICAL(cls) -> IfcWindowStyleOperationEnum2X3:
        ...
    
    @classmethod
    @property
    def TRIPLE_PANEL_BOTTOM(cls) -> IfcWindowStyleOperationEnum2X3:
        ...
    
    @classmethod
    @property
    def TRIPLE_PANEL_TOP(cls) -> IfcWindowStyleOperationEnum2X3:
        ...
    
    @classmethod
    @property
    def TRIPLE_PANEL_LEFT(cls) -> IfcWindowStyleOperationEnum2X3:
        ...
    
    @classmethod
    @property
    def TRIPLE_PANEL_RIGHT(cls) -> IfcWindowStyleOperationEnum2X3:
        ...
    
    @classmethod
    @property
    def TRIPLE_PANEL_HORIZONTAL(cls) -> IfcWindowStyleOperationEnum2X3:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcWindowStyleOperationEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcWindowStyleOperationEnum2X3:
        ...
    
    ...

class IfcWorkControlTypeEnum2X3:
    '''IfcWorkControlTypeEnum'''
    
    @classmethod
    @property
    def ACTUAL(cls) -> IfcWorkControlTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def BASELINE(cls) -> IfcWorkControlTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def PLANNED(cls) -> IfcWorkControlTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def USERDEFINED(cls) -> IfcWorkControlTypeEnum2X3:
        ...
    
    @classmethod
    @property
    def NOTDEFINED(cls) -> IfcWorkControlTypeEnum2X3:
        ...
    
    ...

