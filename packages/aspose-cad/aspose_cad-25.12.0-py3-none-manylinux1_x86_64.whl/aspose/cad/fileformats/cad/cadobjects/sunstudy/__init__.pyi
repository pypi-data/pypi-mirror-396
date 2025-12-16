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

class CadSunStudy(aspose.cad.fileformats.cad.cadobjects.CadBaseObject):
    '''Class describing SUNSTUDY object.'''
    
    def get_uid(self) -> str:
        '''Identifier to use if object handle doesn't work. Done as method not to disturb FileComparer's property comparer'''
        ...
    
    def set_uid(self, id : str) -> None:
        '''Sets'''
        ...
    
    @property
    def embedded_objects_container(self) -> aspose.cad.fileformats.cad.cadobjects.CadEmbeddedObjectContainer:
        ...
    
    @embedded_objects_container.setter
    def embedded_objects_container(self, value : aspose.cad.fileformats.cad.cadobjects.CadEmbeddedObjectContainer):
        ...
    
    @property
    def object_handle(self) -> str:
        ...
    
    @object_handle.setter
    def object_handle(self, value : str):
        ...
    
    @property
    def xdata_container(self) -> aspose.cad.fileformats.cad.cadobjects.CadXdataContainer:
        ...
    
    @xdata_container.setter
    def xdata_container(self, value : aspose.cad.fileformats.cad.cadobjects.CadXdataContainer):
        ...
    
    @property
    def attributes(self) -> List[aspose.cad.fileformats.cad.cadobjects.CadObjectAttribute]:
        '''Gets the attributes.'''
        ...
    
    @attributes.setter
    def attributes(self, value : List[aspose.cad.fileformats.cad.cadobjects.CadObjectAttribute]):
        '''Sets the attributes.'''
        ...
    
    @property
    def application_codes_container(self) -> aspose.cad.fileformats.cad.cadobjects.CadApplicationCodesContainer:
        ...
    
    @application_codes_container.setter
    def application_codes_container(self, value : aspose.cad.fileformats.cad.cadobjects.CadApplicationCodesContainer):
        ...
    
    @property
    def attribute_102_values(self) -> List[aspose.cad.fileformats.cad.CadCodeValue]:
        ...
    
    @attribute_102_values.setter
    def attribute_102_values(self, value : List[aspose.cad.fileformats.cad.CadCodeValue]):
        ...
    
    @property
    def numreactors(self) -> int:
        '''The Numreactors'''
        ...
    
    @numreactors.setter
    def numreactors(self, value : int):
        '''The Numreactors'''
        ...
    
    @property
    def reactors(self) -> List[str]:
        '''Get the reactors handle'''
        ...
    
    @reactors.setter
    def reactors(self, value : List[str]):
        '''Get or sets the reactors handle'''
        ...
    
    @property
    def storage_flag(self) -> bool:
        ...
    
    @storage_flag.setter
    def storage_flag(self, value : bool):
        ...
    
    @property
    def hard_owner(self) -> str:
        ...
    
    @hard_owner.setter
    def hard_owner(self, value : str):
        ...
    
    @property
    def soft_owner(self) -> str:
        ...
    
    @soft_owner.setter
    def soft_owner(self, value : str):
        ...
    
    @property
    def is_soft_owner_set(self) -> bool:
        ...
    
    @property
    def type_name(self) -> aspose.cad.fileformats.cad.cadconsts.CadObjectTypeName:
        ...
    
    @property
    def child_objects(self) -> List[aspose.cad.fileformats.cad.cadobjects.CadObjectBase]:
        ...
    
    @child_objects.setter
    def child_objects(self, value : List[aspose.cad.fileformats.cad.cadobjects.CadObjectBase]):
        ...
    
    @property
    def sun_study_dates(self) -> List[aspose.cad.fileformats.cad.cadobjects.sunstudy.CadSunStudyDate]:
        ...
    
    @sun_study_dates.setter
    def sun_study_dates(self, value : List[aspose.cad.fileformats.cad.cadobjects.sunstudy.CadSunStudyDate]):
        ...
    
    @property
    def sun_setup_name(self) -> str:
        ...
    
    @sun_setup_name.setter
    def sun_setup_name(self, value : str):
        ...
    
    @property
    def description(self) -> str:
        '''Gets the description.'''
        ...
    
    @description.setter
    def description(self, value : str):
        '''Sets the description.'''
        ...
    
    @property
    def output_type(self) -> int:
        ...
    
    @output_type.setter
    def output_type(self, value : int):
        ...
    
    @property
    def sheet_set_name(self) -> str:
        ...
    
    @sheet_set_name.setter
    def sheet_set_name(self, value : str):
        ...
    
    @property
    def use_subset_flag(self) -> bool:
        ...
    
    @use_subset_flag.setter
    def use_subset_flag(self, value : bool):
        ...
    
    @property
    def sheet_subset_name(self) -> str:
        ...
    
    @sheet_subset_name.setter
    def sheet_subset_name(self, value : str):
        ...
    
    @property
    def select_dates(self) -> bool:
        ...
    
    @select_dates.setter
    def select_dates(self, value : bool):
        ...
    
    @property
    def date_input_array_size(self) -> int:
        ...
    
    @date_input_array_size.setter
    def date_input_array_size(self, value : int):
        ...
    
    @property
    def dates_flag_select_range(self) -> bool:
        ...
    
    @dates_flag_select_range.setter
    def dates_flag_select_range(self, value : bool):
        ...
    
    @property
    def start_time(self) -> int:
        ...
    
    @start_time.setter
    def start_time(self, value : int):
        ...
    
    @property
    def end_time(self) -> int:
        ...
    
    @end_time.setter
    def end_time(self, value : int):
        ...
    
    @property
    def interval_in_seconds(self) -> int:
        ...
    
    @interval_in_seconds.setter
    def interval_in_seconds(self, value : int):
        ...
    
    @property
    def hours_number(self) -> int:
        ...
    
    @hours_number.setter
    def hours_number(self, value : int):
        ...
    
    @property
    def hours_list(self) -> List[bool]:
        ...
    
    @hours_list.setter
    def hours_list(self, value : List[bool]):
        ...
    
    @property
    def page_setup_wizard_hard_pointer_id(self) -> str:
        ...
    
    @page_setup_wizard_hard_pointer_id.setter
    def page_setup_wizard_hard_pointer_id(self, value : str):
        ...
    
    @property
    def view_hard_pointer_id(self) -> str:
        ...
    
    @view_hard_pointer_id.setter
    def view_hard_pointer_id(self, value : str):
        ...
    
    @property
    def visual_style_id(self) -> str:
        ...
    
    @visual_style_id.setter
    def visual_style_id(self, value : str):
        ...
    
    @property
    def shade_plot_type(self) -> int:
        ...
    
    @shade_plot_type.setter
    def shade_plot_type(self, value : int):
        ...
    
    @property
    def viewports_per_page(self) -> int:
        ...
    
    @viewports_per_page.setter
    def viewports_per_page(self, value : int):
        ...
    
    @property
    def viewport_distribution_rows_number(self) -> int:
        ...
    
    @viewport_distribution_rows_number.setter
    def viewport_distribution_rows_number(self, value : int):
        ...
    
    @property
    def viewport_distribution_columns_number(self) -> int:
        ...
    
    @viewport_distribution_columns_number.setter
    def viewport_distribution_columns_number(self, value : int):
        ...
    
    @property
    def spacing(self) -> float:
        '''Gets the spacing.'''
        ...
    
    @spacing.setter
    def spacing(self, value : float):
        '''Sets the spacing.'''
        ...
    
    @property
    def lock_viewports_flag(self) -> bool:
        ...
    
    @lock_viewports_flag.setter
    def lock_viewports_flag(self, value : bool):
        ...
    
    @property
    def label_viewports_flag(self) -> bool:
        ...
    
    @label_viewports_flag.setter
    def label_viewports_flag(self, value : bool):
        ...
    
    @property
    def text_style_id(self) -> str:
        ...
    
    @text_style_id.setter
    def text_style_id(self, value : str):
        ...
    
    @property
    def class_version(self) -> int:
        ...
    
    @class_version.setter
    def class_version(self, value : int):
        ...
    
    ...

class CadSunStudyDate:
    '''The Field data'''
    
    @property
    def julian_day(self) -> str:
        ...
    
    @julian_day.setter
    def julian_day(self, value : str):
        ...
    
    @property
    def seconds_past_midnight(self) -> str:
        ...
    
    @seconds_past_midnight.setter
    def seconds_past_midnight(self, value : str):
        ...
    
    ...

