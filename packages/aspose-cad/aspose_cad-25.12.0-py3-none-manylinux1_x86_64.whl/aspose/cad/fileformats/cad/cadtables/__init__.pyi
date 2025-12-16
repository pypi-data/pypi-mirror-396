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

class CadAppIdTableObject(aspose.cad.fileformats.cad.cadobjects.CadOwnedObjectBase):
    '''The Cad app id table.'''
    
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
    def app_name(self) -> str:
        ...
    
    @app_name.setter
    def app_name(self, value : str):
        ...
    
    @property
    def application_flag(self) -> int:
        ...
    
    @application_flag.setter
    def application_flag(self, value : int):
        ...
    
    ...

class CadBlockTableObject(aspose.cad.fileformats.cad.cadobjects.CadOwnedObjectBase):
    '''The Cad block table object.'''
    
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
    def block_insertion_units(self) -> int:
        ...
    
    @block_insertion_units.setter
    def block_insertion_units(self, value : int):
        ...
    
    @property
    def bitmap_preview_data(self) -> bytes:
        ...
    
    @bitmap_preview_data.setter
    def bitmap_preview_data(self, value : bytes):
        ...
    
    @property
    def block_scalability(self) -> int:
        ...
    
    @block_scalability.setter
    def block_scalability(self, value : int):
        ...
    
    @property
    def block_explodability(self) -> int:
        ...
    
    @block_explodability.setter
    def block_explodability(self, value : int):
        ...
    
    @property
    def block_name(self) -> str:
        ...
    
    @block_name.setter
    def block_name(self, value : str):
        ...
    
    @property
    def hard_pointer_to_layout(self) -> str:
        ...
    
    @hard_pointer_to_layout.setter
    def hard_pointer_to_layout(self, value : str):
        ...
    
    @property
    def x_data_app_name(self) -> str:
        ...
    
    @x_data_app_name.setter
    def x_data_app_name(self, value : str):
        ...
    
    @property
    def x_data_string_data(self) -> str:
        ...
    
    @x_data_string_data.setter
    def x_data_string_data(self, value : str):
        ...
    
    @property
    def original_block_name(self) -> str:
        ...
    
    @property
    def is_anonymous(self) -> bool:
        ...
    
    @is_anonymous.setter
    def is_anonymous(self, value : bool):
        ...
    
    @property
    def has_att_defs(self) -> bool:
        ...
    
    @has_att_defs.setter
    def has_att_defs(self, value : bool):
        ...
    
    @property
    def block_is_x_ref(self) -> bool:
        ...
    
    @block_is_x_ref.setter
    def block_is_x_ref(self, value : bool):
        ...
    
    ...

class CadDimensionStyleTable(aspose.cad.fileformats.cad.cadobjects.CadOwnedObjectBase):
    '''The Cad dimension style table.'''
    
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
    def handle_dimstyle(self) -> str:
        ...
    
    @handle_dimstyle.setter
    def handle_dimstyle(self, value : str):
        ...
    
    @property
    def dim_txt_direction(self) -> bool:
        ...
    
    @dim_txt_direction.setter
    def dim_txt_direction(self, value : bool):
        ...
    
    @property
    def dimfxlon(self) -> bool:
        '''Gets whether the lengths of the extension are fixed.
        If the value is true (1), the lengths of the extension lines are set in DIMFXL.'''
        ...
    
    @dimfxlon.setter
    def dimfxlon(self, value : bool):
        '''Sets whether the lengths of the extension are fixed.
        If the value is true (1), the lengths of the extension lines are set in DIMFXL.'''
        ...
    
    @property
    def dimblk(self) -> str:
        '''Gets the arrowhead block name used at the ends of dimension lines.
        Valid standard names are ".", "_DOT", "_DOTSMALL", "_DOTBLANK",
        "_ORIGIN", "_ORIGIN2", "_OPEN", "_OPEN90", "_OPEN30", "_CLOSED", "_SMALL",
        "_NONE", "_OBLIQUE", "_BOXFILLED", "_BOXBLANK", "_CLOSEDBLANK","_DATUMFILLED",
        "_DATUMBLANK", "_INTEGRAL", "_ARCHTICK".'''
        ...
    
    @dimblk.setter
    def dimblk(self, value : str):
        '''Sets the arrowhead block name used at the ends of dimension lines.
        Valid standard names are ".", "_DOT", "_DOTSMALL", "_DOTBLANK",
        "_ORIGIN", "_ORIGIN2", "_OPEN", "_OPEN90", "_OPEN30", "_CLOSED", "_SMALL",
        "_NONE", "_OBLIQUE", "_BOXFILLED", "_BOXBLANK", "_CLOSEDBLANK","_DATUMFILLED",
        "_DATUMBLANK", "_INTEGRAL", "_ARCHTICK".'''
        ...
    
    @property
    def dimblk1(self) -> str:
        '''Gets the arrowhead for the first dimension line if Dimsah is 1.'''
        ...
    
    @dimblk1.setter
    def dimblk1(self, value : str):
        '''Sets the arrowhead for the first dimension line if Dimsah is 1.'''
        ...
    
    @property
    def dimblk2(self) -> str:
        '''Gets the arrowhead for the second dimension line if Dimsah is 1.'''
        ...
    
    @dimblk2.setter
    def dimblk2(self, value : str):
        '''Sets the arrowhead for the second dimension line if Dimsah is 1.'''
        ...
    
    @property
    def dimarcsym(self) -> int:
        '''Gets the mode to display arc symbols for arc length dimension.
        Possible values are: 0 (the arc length symbol is before the text of dimension), 1 (the arc length symbol is above
        the text of dimension), 2 (the arc length symbol is not shown).'''
        ...
    
    @dimarcsym.setter
    def dimarcsym(self, value : int):
        '''Sets the mode to display arc symbols for arc length dimension.
        Possible values are: 0 (the arc length symbol is before the text of dimension), 1 (the arc length symbol is above
        the text of dimension), 2 (the arc length symbol is not shown).'''
        ...
    
    @property
    def dimadec(self) -> int:
        '''Gets the number of precision places displayed in angular dimensions.'''
        ...
    
    @dimadec.setter
    def dimadec(self, value : int):
        '''Sets the number of precision places displayed in angular dimensions.'''
        ...
    
    @property
    def dimalt(self) -> int:
        '''Gets the mode for displaying alternate units in dimension.
        If value is 0 alternate units are off, if the value is 1 alternate units are on.'''
        ...
    
    @dimalt.setter
    def dimalt(self, value : int):
        '''Sets the mode for displaying alternate units in dimension.
        If value is 0 alternate units are off, if the value is 1 alternate units are on.'''
        ...
    
    @property
    def dimaltd(self) -> int:
        '''Gets the number of decimal places in alternate units.
        If Dimalt is turned on, this value sets the number of digits displayed after the decimal point.'''
        ...
    
    @dimaltd.setter
    def dimaltd(self, value : int):
        '''Sets the number of decimal places in alternate units.
        If Dimalt is turned on, this value sets the number of digits displayed after the decimal point.'''
        ...
    
    @property
    def dimaltf(self) -> float:
        '''Gets the multiplier for the alternate units.
        If Dimalt is turned on, this value sets the factor of multiplying linear dimensions.
        Represents the number of millimeters in an inch.'''
        ...
    
    @dimaltf.setter
    def dimaltf(self, value : float):
        '''Sets the multiplier for the alternate units.
        If Dimalt is turned on, this value sets the factor of multiplying linear dimensions.
        Represents the number of millimeters in an inch.'''
        ...
    
    @property
    def dimaltrnd(self) -> float:
        '''Gets the rounding value for the alternate units, e.g., 0.0000.'''
        ...
    
    @dimaltrnd.setter
    def dimaltrnd(self, value : float):
        '''Sets the rounding value for the alternate units, e.g., 0.0000.'''
        ...
    
    @property
    def dimalttd(self) -> int:
        '''Gets the number of decimal places for the tolerance values in the alternate units of a dimension.'''
        ...
    
    @dimalttd.setter
    def dimalttd(self, value : int):
        '''Sets the number of decimal places for the tolerance values in the alternate units of a dimension.'''
        ...
    
    @property
    def dimalttz(self) -> int:
        '''Gets the mode for alternate tolerance zero suppression.'''
        ...
    
    @dimalttz.setter
    def dimalttz(self, value : int):
        '''Sets the mode for alternate tolerance zero suppression.'''
        ...
    
    @property
    def dimaltu(self) -> int:
        '''Gets the format for alternate units of all dimension styles (except angular).'''
        ...
    
    @dimaltu.setter
    def dimaltu(self, value : int):
        '''Sets the format for alternate units of all dimension styles (except angular).'''
        ...
    
    @property
    def dimaltz(self) -> int:
        '''Gets the suppression of zeros for alternate unit dimension values.'''
        ...
    
    @dimaltz.setter
    def dimaltz(self, value : int):
        '''Sets the suppression of zeros for alternate unit dimension values.'''
        ...
    
    @property
    def dimapost(self) -> str:
        '''Gets a text prefix and/or suffix to the alternate dimension test for all dimensions styles (except angular).'''
        ...
    
    @dimapost.setter
    def dimapost(self, value : str):
        '''Sets a text prefix and/or suffix to the alternate dimension test for all dimensions styles (except angular).'''
        ...
    
    @property
    def dimasz(self) -> float:
        '''Gets the size of dimension arrowheads.
        Applicable only when Dimtsz is 0.'''
        ...
    
    @dimasz.setter
    def dimasz(self, value : float):
        '''Sets the size of dimension arrowheads.
        Applicable only when Dimtsz is 0.'''
        ...
    
    @property
    def dimatfit(self) -> int:
        '''Gets the mode for the arranging dimension text and arrows when there is not enough space.
        Possible values are: 0 (text and arrows will be outside extension lines), 1 (arrows will be moved first),
        2 (text will be moved first), 3 (the best move of arrows or text will be applied).'''
        ...
    
    @dimatfit.setter
    def dimatfit(self, value : int):
        '''Sets the mode for the arranging dimension text and arrows when there is not enough space.
        Possible values are: 0 (text and arrows will be outside extension lines), 1 (arrows will be moved first),
        2 (text will be moved first), 3 (the best move of arrows or text will be applied).'''
        ...
    
    @property
    def dimaunit(self) -> int:
        '''Gets the units for angular dimensions.
        Possible values are: 0 (decimal degrees), 1 (degrees/minutes/seconds), 2 (gradians), 3 (radians).'''
        ...
    
    @dimaunit.setter
    def dimaunit(self, value : int):
        '''Sets the units for angular dimensions.
        Possible values are: 0 (decimal degrees), 1 (degrees/minutes/seconds), 2 (gradians), 3 (radians).'''
        ...
    
    @property
    def dimazin(self) -> int:
        '''Gets the mode to suppress zeros for angular dimensions.
        Possible values are: 0 (displays all zeros), 1 (suppresses leading zeros), 2 (suppresses trailing zeros),
        3 (suppresses leading and trailing zeros).'''
        ...
    
    @dimazin.setter
    def dimazin(self, value : int):
        '''Sets the mode to suppress zeros for angular dimensions.
        Possible values are: 0 (displays all zeros), 1 (suppresses leading zeros), 2 (suppresses trailing zeros),
        3 (suppresses leading and trailing zeros).'''
        ...
    
    @property
    def dimblk_handle(self) -> str:
        ...
    
    @dimblk_handle.setter
    def dimblk_handle(self, value : str):
        ...
    
    @property
    def dimblk_1_handle(self) -> str:
        ...
    
    @dimblk_1_handle.setter
    def dimblk_1_handle(self, value : str):
        ...
    
    @property
    def dimblk_2_handle(self) -> str:
        ...
    
    @dimblk_2_handle.setter
    def dimblk_2_handle(self, value : str):
        ...
    
    @property
    def dimcen(self) -> float:
        '''Gets the mode of drawing arc/circle center marks and centerlines.
        If the value is 0 no center marks are drawn, if negative cernterlines are drawn, if positive center marks are drawn.'''
        ...
    
    @dimcen.setter
    def dimcen(self, value : float):
        '''Sets the mode of drawing arc/circle center marks and centerlines.
        If the value is 0 no center marks are drawn, if negative cernterlines are drawn, if positive center marks are drawn.'''
        ...
    
    @property
    def dimclrd(self) -> int:
        '''Gets color to dimension lines, arrowheads, and dimension leader lines.
        Possible values are 1-225 (color index), 0 - by block, 256 - by layer.'''
        ...
    
    @dimclrd.setter
    def dimclrd(self, value : int):
        '''Sets color to dimension lines, arrowheads, and dimension leader lines.
        Possible values are 1-225 (color index), 0 - by block, 256 - by layer.'''
        ...
    
    @property
    def dimclre(self) -> int:
        '''Gets color to dimension extension lines.
        Possible values are 1-225 (color index), 0 - by block, 256 - by layer.'''
        ...
    
    @dimclre.setter
    def dimclre(self, value : int):
        '''Sets color to dimension extension lines.
        Possible values are 1-225 (color index), 0 - by block, 256 - by layer.'''
        ...
    
    @property
    def dimclrt(self) -> int:
        '''Gets color to dimension text.
        Possible values are 1-225 (color index), 0 - by block, 256 - by layer.'''
        ...
    
    @dimclrt.setter
    def dimclrt(self, value : int):
        '''Sets color to dimension text.
        Possible values are 1-225 (color index), 0 - by block, 256 - by layer.'''
        ...
    
    @property
    def dimdec(self) -> int:
        '''Gets the number of decimal places displayed for the primary units of a dimension.'''
        ...
    
    @dimdec.setter
    def dimdec(self, value : int):
        '''Sets the number of decimal places displayed for the primary units of a dimension.'''
        ...
    
    @property
    def dimdle(self) -> float:
        '''Gets the distance the dimension line extends beyond the extension line.
        Applied when oblique strokes (not arrowheads) are drawn.'''
        ...
    
    @dimdle.setter
    def dimdle(self, value : float):
        '''Sets the distance the dimension line extends beyond the extension line.
        Applied when oblique strokes (not arrowheads) are drawn.'''
        ...
    
    @property
    def dimdli(self) -> float:
        '''Gets the spacing of the dimension lines in baseline dimensions.
        Each dimension line is offset from the previous one by this value, if necessary, to avoid drawing over it.'''
        ...
    
    @dimdli.setter
    def dimdli(self, value : float):
        '''Sets the spacing of the dimension lines in baseline dimensions.
        Each dimension line is offset from the previous one by this value, if necessary, to avoid drawing over it.'''
        ...
    
    @property
    def dimdsep(self) -> int:
        '''Gets a decimal separator.
        Decimal point is used be default.'''
        ...
    
    @dimdsep.setter
    def dimdsep(self, value : int):
        '''Sets a decimal separator.
        Decimal point is used be default.'''
        ...
    
    @property
    def dimexe(self) -> float:
        '''Gets the distance between extension line and dimension line.'''
        ...
    
    @dimexe.setter
    def dimexe(self, value : float):
        '''Sets the distance between extension line and dimension line.'''
        ...
    
    @property
    def dimexo(self) -> float:
        '''Gets the distance between extension lines and origin points.'''
        ...
    
    @dimexo.setter
    def dimexo(self, value : float):
        '''Sets the distance between extension lines and origin points.'''
        ...
    
    @property
    def dimfit(self) -> int:
        '''Gets the combination of Dimatfit and Dimtmove.
        If this value is in range 0 � 3, then Dimatfit is also set to 0 � 3 and Dumtmove is set to 0.
        It this value is 4 or 5, then Dimatfit is 3 and Dimtmove is 1 or 2.'''
        ...
    
    @dimfit.setter
    def dimfit(self, value : int):
        '''Sets the combination of Dimatfit and Dimtmove.
        If this value is in range 0 � 3, then Dimatfit is also set to 0 � 3 and Dumtmove is set to 0.
        It this value is 4 or 5, then Dimatfit is 3 and Dimtmove is 1 or 2.'''
        ...
    
    @property
    def dimfrac(self) -> int:
        '''Gets the fraction mode for architectural or fractional units (Dimlunit).
        Possible values are 0 (horizontal stacking), 1 (diagonal stacking), 2 (no stacking).'''
        ...
    
    @dimfrac.setter
    def dimfrac(self, value : int):
        '''Sets the fraction mode for architectural or fractional units (Dimlunit).
        Possible values are 0 (horizontal stacking), 1 (diagonal stacking), 2 (no stacking).'''
        ...
    
    @property
    def dimgap(self) -> float:
        '''Gets the distance around the dimension text when the dimension line breaks it.'''
        ...
    
    @dimgap.setter
    def dimgap(self, value : float):
        '''Sets the distance around the dimension text when the dimension line breaks it.'''
        ...
    
    @property
    def dimjust(self) -> int:
        '''Gets the mode for horizontal positioning of text.
        Possible values are: 0 (text is above the dimension line and centered between the extension lines),
        1 (the text is next to the first extension line), 2 (the text is next to the second extension line),
        3 (the text is above and aligned with the first extension line), 4 (the text is above and aligned with the second extension line).'''
        ...
    
    @dimjust.setter
    def dimjust(self, value : int):
        '''Sets the mode for horizontal positioning of text.
        Possible values are: 0 (text is above the dimension line and centered between the extension lines),
        1 (the text is next to the first extension line), 2 (the text is next to the second extension line),
        3 (the text is above and aligned with the first extension line), 4 (the text is above and aligned with the second extension line).'''
        ...
    
    @property
    def dimldrblk(self) -> str:
        '''Gets the arrow type for leaders.
        The list of available values is the same as for Dimblk.'''
        ...
    
    @dimldrblk.setter
    def dimldrblk(self, value : str):
        '''Sets the arrow type for leaders.
        The list of available values is the same as for Dimblk.'''
        ...
    
    @property
    def dimlfac(self) -> float:
        '''Gets a scale factor for linear dimension measurements.'''
        ...
    
    @dimlfac.setter
    def dimlfac(self, value : float):
        '''Sets a scale factor for linear dimension measurements.'''
        ...
    
    @property
    def dimlim(self) -> int:
        '''Gets dimension limits as the default text.
        Possible values are: 0 (limits are not generated as default text), 1 (limits are generated as default text).
        If this value is 1 Dimtol value is considered as off.'''
        ...
    
    @dimlim.setter
    def dimlim(self, value : int):
        '''Sets dimension limits as the default text.
        Possible values are: 0 (limits are not generated as default text), 1 (limits are generated as default text).
        If this value is 1 Dimtol value is considered as off.'''
        ...
    
    @property
    def dimlunit(self) -> int:
        '''Gets units mode (not applied to angular dimensions).
        Possible values are: 1 (scientific), 2 (decimal), 3 (engineering), 4 (architectural stacked),
        5 (fractional stacked), 6 (Microsoft Windows Desktop).'''
        ...
    
    @dimlunit.setter
    def dimlunit(self, value : int):
        '''Sets units mode (not applied to angular dimensions).
        Possible values are: 1 (scientific), 2 (decimal), 3 (engineering), 4 (architectural stacked),
        5 (fractional stacked), 6 (Microsoft Windows Desktop).'''
        ...
    
    @property
    def dimlwd(self) -> int:
        '''Gets the lineweight of dimension lines.
        Possible values are: -3 (default LWDEFAULT value), -2 (by block), -1 (by layer).'''
        ...
    
    @dimlwd.setter
    def dimlwd(self, value : int):
        '''Sets the lineweight of dimension lines.
        Possible values are: -3 (default LWDEFAULT value), -2 (by block), -1 (by layer).'''
        ...
    
    @property
    def dimlwe(self) -> int:
        '''Gets the lineweight of extension lines.
        Possible values are: -3 (default LWDEFAULT value), -2 (by block), -1 (by layer).'''
        ...
    
    @dimlwe.setter
    def dimlwe(self, value : int):
        '''Sets the lineweight of extension lines.
        Possible values are: -3 (default LWDEFAULT value), -2 (by block), -1 (by layer).'''
        ...
    
    @property
    def dimpost(self) -> str:
        ...
    
    @dimpost.setter
    def dimpost(self, value : str):
        ...
    
    @property
    def dimrnd(self) -> float:
        '''Gets rounding precision for dimension distance (except angular dimensions).'''
        ...
    
    @dimrnd.setter
    def dimrnd(self, value : float):
        '''Sets rounding precision for dimension distance (except angular dimensions).'''
        ...
    
    @property
    def dimsah(self) -> int:
        '''Gets which arrowhead bocks should be used.
        If the value is 0 the arrowheads set up by Dimblk are used, if the value is 1 the arrwheads from Dimblk1 and Dimblk2 are used.'''
        ...
    
    @dimsah.setter
    def dimsah(self, value : int):
        '''Sets which arrowhead bocks should be used.
        If the value is 0 the arrowheads set up by Dimblk are used, if the value is 1 the arrwheads from Dimblk1 and Dimblk2 are used.'''
        ...
    
    @property
    def dimscale(self) -> float:
        '''Gets the scale of the dimension.
        Applicable to the sizes, distances, and offsets but not to the measured lengths, coordinates, and angles.'''
        ...
    
    @dimscale.setter
    def dimscale(self, value : float):
        '''Sets the scale of the dimension.
        Applicable to the sizes, distances, and offsets but not to the measured lengths, coordinates, and angles.'''
        ...
    
    @property
    def dimsd1(self) -> int:
        '''Gets the suppression of the first dimension line and arrowhead.
        Possible values are: 0 (not suppressed), 1 (suppressed).'''
        ...
    
    @dimsd1.setter
    def dimsd1(self, value : int):
        '''Sets the suppression of the first dimension line and arrowhead.
        Possible values are: 0 (not suppressed), 1 (suppressed).'''
        ...
    
    @property
    def dimsd2(self) -> int:
        '''Gets the suppression of the second dimension line and arrowhead.
        Possible values are: 0 (not suppressed), 1 (suppressed).'''
        ...
    
    @dimsd2.setter
    def dimsd2(self, value : int):
        '''Sets the suppression of the second dimension line and arrowhead.
        Possible values are: 0 (not suppressed), 1 (suppressed).'''
        ...
    
    @property
    def dimse1(self) -> int:
        '''Gets the suppression of the first extension line.
        Possible values are: 0 (not suppressed), 1 (suppressed).'''
        ...
    
    @dimse1.setter
    def dimse1(self, value : int):
        '''Sets the suppression of the first extension line.
        Possible values are: 0 (not suppressed), 1 (suppressed).'''
        ...
    
    @property
    def dimse2(self) -> int:
        '''Gets the suppression of the second extension line.
        Possible values are: 0 (not suppressed), 1 (suppressed).'''
        ...
    
    @dimse2.setter
    def dimse2(self, value : int):
        '''Sets the suppression of the second extension line.
        Possible values are: 0 (not suppressed), 1 (suppressed).'''
        ...
    
    @property
    def dimsoxd(self) -> int:
        '''Gets the suppression of arrowheads if there is not enough space inside the extension lines.
        Possible values are: 0 (not suppressed), 1 (suppressed).'''
        ...
    
    @dimsoxd.setter
    def dimsoxd(self, value : int):
        '''Sets the suppression of arrowheads if there is not enough space inside the extension lines.
        Possible values are: 0 (not suppressed), 1 (suppressed).'''
        ...
    
    @property
    def dimtad(self) -> int:
        '''Gets the mode for vertical position of text in relation to the dimension line.
        Possible values are: 0 (centered between the extension lines), 1 (above the dimension line),
        2 (on the side of the dimension line farthest away from the defining points), 3 (position is according to Japanese Industrial Standards (JIS)),
        4 (below the dimension line).'''
        ...
    
    @dimtad.setter
    def dimtad(self, value : int):
        '''Sets the mode for vertical position of text in relation to the dimension line.
        Possible values are: 0 (centered between the extension lines), 1 (above the dimension line),
        2 (on the side of the dimension line farthest away from the defining points), 3 (position is according to Japanese Industrial Standards (JIS)),
        4 (below the dimension line).'''
        ...
    
    @property
    def dimtdec(self) -> int:
        '''Gets the number of decimal places to display in tolerance values for the primary units in a dimension.
        Applicable only when Dimtol is on.'''
        ...
    
    @dimtdec.setter
    def dimtdec(self, value : int):
        '''Sets the number of decimal places to display in tolerance values for the primary units in a dimension.
        Applicable only when Dimtol is on.'''
        ...
    
    @property
    def dimtfac(self) -> float:
        '''Gets a scale factor for the text height of fractions and tolerance values relative to the dimension text height.'''
        ...
    
    @dimtfac.setter
    def dimtfac(self, value : float):
        '''Sets a scale factor for the text height of fractions and tolerance values relative to the dimension text height.'''
        ...
    
    @property
    def dimtih(self) -> Optional[int]:
        '''Gets the position of dimension text inside the extension lines (except ordinate dimensions).
        Possible values are: 0 (aligns text with the dimension line),  1 (horizontal text).'''
        ...
    
    @dimtih.setter
    def dimtih(self, value : Optional[int]):
        '''Sets the position of dimension text inside the extension lines (except ordinate dimensions).
        Possible values are: 0 (aligns text with the dimension line),  1 (horizontal text).'''
        ...
    
    @property
    def dimtix(self) -> int:
        '''Gets whether text should be drawn between extension lines.
        Possible values are: 0 (text is inside the extension lines), 1 (text is between the extension lines even if it would ordinarily be placed outside those lines).'''
        ...
    
    @dimtix.setter
    def dimtix(self, value : int):
        '''Sets whether text should be drawn between extension lines.
        Possible values are: 0 (text is inside the extension lines), 1 (text is between the extension lines even if it would ordinarily be placed outside those lines).'''
        ...
    
    @property
    def dimtm(self) -> float:
        '''Gets the minimum tolerance limit for dimension text.
        Applied when Dimtol or Dimlim is on.'''
        ...
    
    @dimtm.setter
    def dimtm(self, value : float):
        '''Sets the minimum tolerance limit for dimension text.
        Applied when Dimtol or Dimlim is on.'''
        ...
    
    @property
    def dimfxl(self) -> float:
        ...
    
    @dimfxl.setter
    def dimfxl(self, value : float):
        ...
    
    @property
    def dimjogang(self) -> float:
        '''Gets the angle of the transverse segment of the dimension line in a jogged radius dimension.'''
        ...
    
    @dimjogang.setter
    def dimjogang(self, value : float):
        '''Sets the angle of the transverse segment of the dimension line in a jogged radius dimension.'''
        ...
    
    @property
    def dimtfill(self) -> int:
        '''Gets the fill background of dimension text.
        Possible values are: 0 (no background), 1 (the background color of the drawing), 2 (the color specified by Dimtfillclr).'''
        ...
    
    @dimtfill.setter
    def dimtfill(self, value : int):
        '''Sets the fill background of dimension text.
        Possible values are: 0 (no background), 1 (the background color of the drawing), 2 (the color specified by Dimtfillclr).'''
        ...
    
    @property
    def dimtmove(self) -> int:
        '''Gets the mode for dimension text movement.
        Possible values are: 0 (move the dimension line with dimension text), 1 (Add a leader when dimension text is moved),
        2 (move text freely).'''
        ...
    
    @dimtmove.setter
    def dimtmove(self, value : int):
        '''Sets the mode for dimension text movement.
        Possible values are: 0 (move the dimension line with dimension text), 1 (Add a leader when dimension text is moved),
        2 (move text freely).'''
        ...
    
    @property
    def dimtofl(self) -> int:
        '''Gets the mode to draw a dimension line between the extension lines even when the text is placed outside.
        Possible values are: 0 (do not draw dimension lines between the measured points),
        1 (draw dimension lines between the measured points).'''
        ...
    
    @dimtofl.setter
    def dimtofl(self, value : int):
        '''Sets the mode to draw a dimension line between the extension lines even when the text is placed outside.
        Possible values are: 0 (do not draw dimension lines between the measured points),
        1 (draw dimension lines between the measured points).'''
        ...
    
    @property
    def dimtoh(self) -> Optional[int]:
        '''Gets the position of dimension text outside the extension lines.
        Possible values are: 0 (align text with the dimension line), 1 (text is horizontal).'''
        ...
    
    @dimtoh.setter
    def dimtoh(self, value : Optional[int]):
        '''Sets the position of dimension text outside the extension lines.
        Possible values are: 0 (align text with the dimension line), 1 (text is horizontal).'''
        ...
    
    @property
    def dimtol(self) -> int:
        '''Gets whether tolerances should be added to dimension text.
        Possible values are: 0 (off), 1 (on, Dimlim is considered as off).'''
        ...
    
    @dimtol.setter
    def dimtol(self, value : int):
        '''Sets whether tolerances should be added to dimension text.
        Possible values are: 0 (off), 1 (on, Dimlim is considered as off).'''
        ...
    
    @property
    def dimtolj(self) -> int:
        '''Gets the vertical justification for tolerance values relative to the text.
        Possible values are: 0 (bottom), 1 (middle), 2 (top).'''
        ...
    
    @dimtolj.setter
    def dimtolj(self, value : int):
        '''Sets the vertical justification for tolerance values relative to the text.
        Possible values are: 0 (bottom), 1 (middle), 2 (top).'''
        ...
    
    @property
    def dimtp(self) -> float:
        '''Gets the maximum tolerance limit for dimension text.
        Applied when Dimtol or Dimlim is on.'''
        ...
    
    @dimtp.setter
    def dimtp(self, value : float):
        '''Sets the maximum tolerance limit for dimension text.
        Applied when Dimtol or Dimlim is on.'''
        ...
    
    @property
    def dimtsz(self) -> float:
        '''Gets mode of drawing strokes and arrowheads for linear, radius, and diameter diensions.
        If the value is 0 arrowheads will be drawn, positive value defines the size of oblique strokes instead of arrowheads.
        The value is multiplied by the Dimscale.'''
        ...
    
    @dimtsz.setter
    def dimtsz(self, value : float):
        '''Sets mode of drawing strokes and arrowheads for linear, radius, and diameter diensions.
        If the value is 0 arrowheads will be drawn, positive value defines the size of oblique strokes instead of arrowheads.
        The value is multiplied by the Dimscale.'''
        ...
    
    @property
    def dimtvp(self) -> float:
        '''Gets the vertical position of dimension text above or below the dimension line.'''
        ...
    
    @dimtvp.setter
    def dimtvp(self, value : float):
        '''Sets the vertical position of dimension text above or below the dimension line.'''
        ...
    
    @property
    def dimtxsty(self) -> str:
        '''Gets the text style name of the dimension.'''
        ...
    
    @dimtxsty.setter
    def dimtxsty(self, value : str):
        '''Sets the text style name of the dimension.'''
        ...
    
    @property
    def dimtxt(self) -> float:
        '''Gets the height of dimension text.'''
        ...
    
    @dimtxt.setter
    def dimtxt(self, value : float):
        '''Sets the height of dimension text.'''
        ...
    
    @property
    def dimtzin(self) -> int:
        '''Gets the suppression of zeros in tolerance values.
        Possible values are:  0 (suppresses zero feet and precisely zero inches), 1 (uncludes zero feet and precisely zero inches),
        2 (includes zero feet and suppresses zero inches), 3 (includes zero inches and suppresses zero feet),
        4 (suppresses leading zeros), 8 (suppresses trailing zeros), 12 (suppresses both leading and trailing zeros).'''
        ...
    
    @dimtzin.setter
    def dimtzin(self, value : int):
        '''Sets the suppression of zeros in tolerance values.
        Possible values are:  0 (suppresses zero feet and precisely zero inches), 1 (uncludes zero feet and precisely zero inches),
        2 (includes zero feet and suppresses zero inches), 3 (includes zero inches and suppresses zero feet),
        4 (suppresses leading zeros), 8 (suppresses trailing zeros), 12 (suppresses both leading and trailing zeros).'''
        ...
    
    @property
    def dimunit(self) -> int:
        '''Gets the value, that was used to set units but now is replaced with Dimlunit and Dimfrac.'''
        ...
    
    @dimunit.setter
    def dimunit(self, value : int):
        '''Sets the value, that was used to set units but now is replaced with Dimlunit and Dimfrac.'''
        ...
    
    @property
    def dimupt(self) -> int:
        '''Gets the mode for user-positioned text.
        Possible values are: 0 (cursor controls only the dimension line location),
        1 (cursor controls both the text position and the dimension line location).'''
        ...
    
    @dimupt.setter
    def dimupt(self, value : int):
        '''Sets the mode for user-positioned text.
        Possible values are: 0 (cursor controls only the dimension line location),
        1 (cursor controls both the text position and the dimension line location).'''
        ...
    
    @property
    def dimzin(self) -> int:
        '''Gets the suppression of zeros in the primary unit value.
        Possible values arer: 0 (suppresses zero feet and precisely zero inches), 1 (includes zero feet and precisely zero inches),
        2 (includes zero feet and suppresses zero inches), 3 (includes zero inches and suppresses zero feet),
        4 (bit 3, suppresses leading zeros), 8 (bit 4, suppresses trailing zeros), 12 (bit 3 and bit 4, suppresses both leading and trailing zeros).'''
        ...
    
    @dimzin.setter
    def dimzin(self, value : int):
        '''Sets the suppression of zeros in the primary unit value.
        Possible values arer: 0 (suppresses zero feet and precisely zero inches), 1 (includes zero feet and precisely zero inches),
        2 (includes zero feet and suppresses zero inches), 3 (includes zero inches and suppresses zero feet),
        4 (bit 3, suppresses leading zeros), 8 (bit 4, suppresses trailing zeros), 12 (bit 3 and bit 4, suppresses both leading and trailing zeros).'''
        ...
    
    @property
    def standard_flag(self) -> int:
        ...
    
    @standard_flag.setter
    def standard_flag(self, value : int):
        ...
    
    @property
    def style_name(self) -> str:
        ...
    
    @style_name.setter
    def style_name(self, value : str):
        ...
    
    @property
    def dim_alt_mzf(self) -> float:
        ...
    
    @dim_alt_mzf.setter
    def dim_alt_mzf(self, value : float):
        ...
    
    @property
    def dim_mzf(self) -> float:
        ...
    
    @dim_mzf.setter
    def dim_mzf(self, value : float):
        ...
    
    @property
    def dim_alt_mzs(self) -> str:
        ...
    
    @dim_alt_mzs.setter
    def dim_alt_mzs(self, value : str):
        ...
    
    @property
    def dim_mzs(self) -> str:
        ...
    
    @dim_mzs.setter
    def dim_mzs(self, value : str):
        ...
    
    ...

class CadLayerTable(aspose.cad.fileformats.cad.cadobjects.CadOwnedObjectBase):
    '''The Cad layer table.'''
    
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
    def attribute420(self) -> Optional[int]:
        '''Gets the attribute420.'''
        ...
    
    @attribute420.setter
    def attribute420(self, value : Optional[int]):
        '''Sets the attribute420.'''
        ...
    
    @property
    def color_id(self) -> int:
        ...
    
    @color_id.setter
    def color_id(self, value : int):
        ...
    
    @property
    def flags(self) -> int:
        '''Gets the flags.'''
        ...
    
    @flags.setter
    def flags(self, value : int):
        '''Sets the flags.'''
        ...
    
    @property
    def line_type_name(self) -> str:
        ...
    
    @line_type_name.setter
    def line_type_name(self, value : str):
        ...
    
    @property
    def line_weight(self) -> int:
        ...
    
    @line_weight.setter
    def line_weight(self, value : int):
        ...
    
    @property
    def attribute348(self) -> str:
        '''Gets the attribute348.'''
        ...
    
    @attribute348.setter
    def attribute348(self, value : str):
        '''Sets the attribute348.'''
        ...
    
    @property
    def material_hanlde(self) -> str:
        ...
    
    @material_hanlde.setter
    def material_hanlde(self, value : str):
        ...
    
    @property
    def name(self) -> str:
        '''Gets the name.'''
        ...
    
    @name.setter
    def name(self, value : str):
        '''Sets the name.'''
        ...
    
    @property
    def plot_flag(self) -> Optional[bool]:
        ...
    
    @plot_flag.setter
    def plot_flag(self, value : Optional[bool]):
        ...
    
    @property
    def plot_style_handle(self) -> str:
        ...
    
    @plot_style_handle.setter
    def plot_style_handle(self, value : str):
        ...
    
    ...

class CadLineTypeTableObject(aspose.cad.fileformats.cad.cadobjects.CadOwnedObjectBase):
    '''The Cad line type table object.'''
    
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
    def offset_y_element_index(self) -> List[int]:
        ...
    
    @offset_y_element_index.setter
    def offset_y_element_index(self, value : List[int]):
        ...
    
    @property
    def offset_x_element_index(self) -> List[int]:
        ...
    
    @offset_x_element_index.setter
    def offset_x_element_index(self, value : List[int]):
        ...
    
    @property
    def scale_linetype_element_index(self) -> List[int]:
        ...
    
    @scale_linetype_element_index.setter
    def scale_linetype_element_index(self, value : List[int]):
        ...
    
    @property
    def alignment_code(self) -> int:
        ...
    
    @alignment_code.setter
    def alignment_code(self, value : int):
        ...
    
    @property
    def dash_dot_length(self) -> List[float]:
        ...
    
    @dash_dot_length.setter
    def dash_dot_length(self, value : List[float]):
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
    def flags(self) -> int:
        '''Gets the flags.'''
        ...
    
    @flags.setter
    def flags(self, value : int):
        '''Sets the flags.'''
        ...
    
    @property
    def line_type_element(self) -> List[int]:
        ...
    
    @line_type_element.setter
    def line_type_element(self, value : List[int]):
        ...
    
    @property
    def name(self) -> str:
        '''Gets the name.'''
        ...
    
    @name.setter
    def name(self, value : str):
        '''Sets the name.'''
        ...
    
    @property
    def number_of_linetype_elements(self) -> int:
        ...
    
    @number_of_linetype_elements.setter
    def number_of_linetype_elements(self, value : int):
        ...
    
    @property
    def offset_x(self) -> List[float]:
        ...
    
    @offset_x.setter
    def offset_x(self, value : List[float]):
        ...
    
    @property
    def offset_y(self) -> List[float]:
        ...
    
    @offset_y.setter
    def offset_y(self, value : List[float]):
        ...
    
    @property
    def pattern_length(self) -> float:
        ...
    
    @pattern_length.setter
    def pattern_length(self, value : float):
        ...
    
    @property
    def rotation_angle(self) -> List[float]:
        ...
    
    @rotation_angle.setter
    def rotation_angle(self, value : List[float]):
        ...
    
    @property
    def scale(self) -> List[float]:
        '''Gets the scale.'''
        ...
    
    @scale.setter
    def scale(self, value : List[float]):
        '''Sets the scale.'''
        ...
    
    @property
    def shape_number(self) -> List[int]:
        ...
    
    @shape_number.setter
    def shape_number(self, value : List[int]):
        ...
    
    @property
    def style_reference(self) -> List[str]:
        ...
    
    @style_reference.setter
    def style_reference(self, value : List[str]):
        ...
    
    @property
    def text_strings(self) -> List[str]:
        ...
    
    @text_strings.setter
    def text_strings(self, value : List[str]):
        ...
    
    ...

class CadStyleTableObject(aspose.cad.fileformats.cad.cadobjects.CadOwnedObjectBase):
    '''The Cad style table object.'''
    
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
    def big_font_name(self) -> str:
        ...
    
    @big_font_name.setter
    def big_font_name(self, value : str):
        ...
    
    @property
    def fixed_height(self) -> float:
        ...
    
    @fixed_height.setter
    def fixed_height(self, value : float):
        ...
    
    @property
    def last_height(self) -> float:
        ...
    
    @last_height.setter
    def last_height(self, value : float):
        ...
    
    @property
    def oblique_angle(self) -> float:
        ...
    
    @oblique_angle.setter
    def oblique_angle(self, value : float):
        ...
    
    @property
    def primary_font_name(self) -> str:
        ...
    
    @primary_font_name.setter
    def primary_font_name(self, value : str):
        ...
    
    @property
    def style_flag(self) -> int:
        ...
    
    @style_flag.setter
    def style_flag(self, value : int):
        ...
    
    @property
    def style_name(self) -> str:
        ...
    
    @style_name.setter
    def style_name(self, value : str):
        ...
    
    @property
    def text_generation_flag(self) -> int:
        ...
    
    @text_generation_flag.setter
    def text_generation_flag(self, value : int):
        ...
    
    @property
    def width_factor(self) -> float:
        ...
    
    @width_factor.setter
    def width_factor(self, value : float):
        ...
    
    ...

class CadSymbolTableGroupCodes(aspose.cad.fileformats.cad.cadobjects.CadOwnedObjectBase):
    '''Group codes that apply to all symbol tables.'''
    
    def get_uid(self) -> str:
        '''Identifier to use if object handle doesn't work. Done as method not to disturb FileComparer's property comparer'''
        ...
    
    def set_uid(self, id : str) -> None:
        '''Sets'''
        ...
    
    def init(self) -> None:
        '''Initializes this instance.'''
        ...
    
    def clone(self) -> any:
        '''Creates a new object that is a copy of the current instance.
        
        :returns: A new object that is a copy of this instance.'''
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
    def is_init(self) -> bool:
        ...
    
    @property
    def max_table_entries_count(self) -> Optional[int]:
        ...
    
    @max_table_entries_count.setter
    def max_table_entries_count(self, value : Optional[int]):
        ...
    
    @property
    def symbol_table_parameters(self) -> List[aspose.cad.fileformats.cad.CadCodeValue]:
        ...
    
    @symbol_table_parameters.setter
    def symbol_table_parameters(self, value : List[aspose.cad.fileformats.cad.CadCodeValue]):
        ...
    
    @property
    def sub_class(self) -> str:
        ...
    
    @sub_class.setter
    def sub_class(self, value : str):
        ...
    
    ...

class CadUcsTableObject(aspose.cad.fileformats.cad.cadobjects.CadOwnedObjectBase):
    '''ucsPorts table class'''
    
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
    def name(self) -> str:
        '''Gets the name.'''
        ...
    
    @name.setter
    def name(self, value : str):
        '''Sets the name.'''
        ...
    
    @property
    def standard_flag_values(self) -> int:
        ...
    
    @standard_flag_values.setter
    def standard_flag_values(self, value : int):
        ...
    
    @property
    def origin(self) -> aspose.cad.fileformats.cad.cadobjects.Cad3DPoint:
        '''Gets the origin.'''
        ...
    
    @origin.setter
    def origin(self, value : aspose.cad.fileformats.cad.cadobjects.Cad3DPoint):
        '''Sets the origin.'''
        ...
    
    @property
    def direction_x(self) -> aspose.cad.fileformats.cad.cadobjects.Cad3DPoint:
        ...
    
    @direction_x.setter
    def direction_x(self, value : aspose.cad.fileformats.cad.cadobjects.Cad3DPoint):
        ...
    
    @property
    def direction_y(self) -> aspose.cad.fileformats.cad.cadobjects.Cad3DPoint:
        ...
    
    @direction_y.setter
    def direction_y(self, value : aspose.cad.fileformats.cad.cadobjects.Cad3DPoint):
        ...
    
    @property
    def elevation(self) -> float:
        '''Gets the elevation.'''
        ...
    
    @elevation.setter
    def elevation(self, value : float):
        '''Sets the elevation.'''
        ...
    
    @property
    def base_ucs_handle(self) -> str:
        ...
    
    @base_ucs_handle.setter
    def base_ucs_handle(self, value : str):
        ...
    
    @property
    def named_ucs_handle(self) -> str:
        ...
    
    @named_ucs_handle.setter
    def named_ucs_handle(self, value : str):
        ...
    
    @property
    def orthographic_view_type(self) -> int:
        ...
    
    @orthographic_view_type.setter
    def orthographic_view_type(self, value : int):
        ...
    
    @property
    def orthographic_type(self) -> Optional[int]:
        ...
    
    @orthographic_type.setter
    def orthographic_type(self, value : Optional[int]):
        ...
    
    @property
    def orthographic_type_origin(self) -> aspose.cad.fileformats.cad.cadobjects.Cad3DPoint:
        ...
    
    @orthographic_type_origin.setter
    def orthographic_type_origin(self, value : aspose.cad.fileformats.cad.cadobjects.Cad3DPoint):
        ...
    
    ...

class CadViewTableObject(aspose.cad.fileformats.cad.cadobjects.CadOwnedObjectBase):
    '''viewPorts table class'''
    
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
    def name(self) -> str:
        '''Gets the name.'''
        ...
    
    @name.setter
    def name(self, value : str):
        '''Sets the name.'''
        ...
    
    @property
    def flag(self) -> int:
        '''Gets the flag.'''
        ...
    
    @flag.setter
    def flag(self, value : int):
        '''Sets the flag.'''
        ...
    
    @property
    def view_height(self) -> float:
        ...
    
    @view_height.setter
    def view_height(self, value : float):
        ...
    
    @property
    def center_point(self) -> aspose.cad.fileformats.cad.cadobjects.Cad2DPoint:
        ...
    
    @center_point.setter
    def center_point(self, value : aspose.cad.fileformats.cad.cadobjects.Cad2DPoint):
        ...
    
    @property
    def view_width(self) -> float:
        ...
    
    @view_width.setter
    def view_width(self, value : float):
        ...
    
    @property
    def view_direction(self) -> aspose.cad.fileformats.cad.cadobjects.Cad3DPoint:
        ...
    
    @view_direction.setter
    def view_direction(self, value : aspose.cad.fileformats.cad.cadobjects.Cad3DPoint):
        ...
    
    @property
    def target_point(self) -> aspose.cad.fileformats.cad.cadobjects.Cad3DPoint:
        ...
    
    @target_point.setter
    def target_point(self, value : aspose.cad.fileformats.cad.cadobjects.Cad3DPoint):
        ...
    
    @property
    def lens_length(self) -> float:
        ...
    
    @lens_length.setter
    def lens_length(self, value : float):
        ...
    
    @property
    def front_clipping(self) -> float:
        ...
    
    @front_clipping.setter
    def front_clipping(self, value : float):
        ...
    
    @property
    def back_clipping(self) -> float:
        ...
    
    @back_clipping.setter
    def back_clipping(self, value : float):
        ...
    
    @property
    def twist_angle(self) -> float:
        ...
    
    @twist_angle.setter
    def twist_angle(self, value : float):
        ...
    
    @property
    def view_mode(self) -> int:
        ...
    
    @view_mode.setter
    def view_mode(self, value : int):
        ...
    
    @property
    def associated_ucs(self) -> int:
        ...
    
    @associated_ucs.setter
    def associated_ucs(self, value : int):
        ...
    
    @property
    def camera_plottable(self) -> int:
        ...
    
    @camera_plottable.setter
    def camera_plottable(self, value : int):
        ...
    
    @property
    def render_mode(self) -> int:
        ...
    
    @render_mode.setter
    def render_mode(self, value : int):
        ...
    
    @property
    def background_handle(self) -> str:
        ...
    
    @background_handle.setter
    def background_handle(self, value : str):
        ...
    
    @property
    def live_section_handle(self) -> str:
        ...
    
    @live_section_handle.setter
    def live_section_handle(self, value : str):
        ...
    
    @property
    def visual_style_handle(self) -> str:
        ...
    
    @visual_style_handle.setter
    def visual_style_handle(self, value : str):
        ...
    
    @property
    def sun_hard_ownership(self) -> str:
        ...
    
    @sun_hard_ownership.setter
    def sun_hard_ownership(self, value : str):
        ...
    
    @property
    def ucs_origin(self) -> aspose.cad.fileformats.cad.cadobjects.Cad3DPoint:
        ...
    
    @ucs_origin.setter
    def ucs_origin(self, value : aspose.cad.fileformats.cad.cadobjects.Cad3DPoint):
        ...
    
    @property
    def ucs_xaxis(self) -> aspose.cad.fileformats.cad.cadobjects.Cad3DPoint:
        ...
    
    @ucs_xaxis.setter
    def ucs_xaxis(self, value : aspose.cad.fileformats.cad.cadobjects.Cad3DPoint):
        ...
    
    @property
    def ucs_yaxis(self) -> aspose.cad.fileformats.cad.cadobjects.Cad3DPoint:
        ...
    
    @ucs_yaxis.setter
    def ucs_yaxis(self, value : aspose.cad.fileformats.cad.cadobjects.Cad3DPoint):
        ...
    
    @property
    def ucs_type(self) -> Optional[int]:
        ...
    
    @ucs_type.setter
    def ucs_type(self, value : Optional[int]):
        ...
    
    @property
    def elevation(self) -> Optional[float]:
        '''Gets the elevation.'''
        ...
    
    @elevation.setter
    def elevation(self, value : Optional[float]):
        '''Sets the elevation.'''
        ...
    
    @property
    def ucs_handle(self) -> str:
        ...
    
    @ucs_handle.setter
    def ucs_handle(self, value : str):
        ...
    
    @property
    def ucs_base_handle(self) -> str:
        ...
    
    @ucs_base_handle.setter
    def ucs_base_handle(self, value : str):
        ...
    
    @property
    def use_default_lights(self) -> bool:
        ...
    
    @use_default_lights.setter
    def use_default_lights(self, value : bool):
        ...
    
    @property
    def default_lighting_type(self) -> byte:
        ...
    
    @default_lighting_type.setter
    def default_lighting_type(self, value : byte):
        ...
    
    @property
    def brightness(self) -> float:
        '''Gets the brightness.'''
        ...
    
    @brightness.setter
    def brightness(self, value : float):
        '''Sets the brightness.'''
        ...
    
    @property
    def contrast(self) -> float:
        '''Gets the contrast.'''
        ...
    
    @contrast.setter
    def contrast(self, value : float):
        '''Sets the contrast.'''
        ...
    
    @property
    def abient_color(self) -> float:
        ...
    
    @abient_color.setter
    def abient_color(self, value : float):
        ...
    
    ...

class CadVportTableObject(aspose.cad.fileformats.cad.cadobjects.CadOwnedObjectBase):
    '''viewPorts table class'''
    
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
    def soft_frozen_layer_object(self) -> List[str]:
        ...
    
    @soft_frozen_layer_object.setter
    def soft_frozen_layer_object(self, value : List[str]):
        ...
    
    @property
    def hard_frozen_layer_object(self) -> List[str]:
        ...
    
    @hard_frozen_layer_object.setter
    def hard_frozen_layer_object(self, value : List[str]):
        ...
    
    @property
    def name(self) -> str:
        '''Gets the name.'''
        ...
    
    @name.setter
    def name(self, value : str):
        '''Sets the name.'''
        ...
    
    @property
    def flags(self) -> int:
        '''Gets the flags.'''
        ...
    
    @flags.setter
    def flags(self, value : int):
        '''Sets the flags.'''
        ...
    
    @property
    def lower_left(self) -> aspose.cad.fileformats.cad.cadobjects.Cad2DPoint:
        ...
    
    @lower_left.setter
    def lower_left(self, value : aspose.cad.fileformats.cad.cadobjects.Cad2DPoint):
        ...
    
    @property
    def upper_right(self) -> aspose.cad.fileformats.cad.cadobjects.Cad2DPoint:
        ...
    
    @upper_right.setter
    def upper_right(self, value : aspose.cad.fileformats.cad.cadobjects.Cad2DPoint):
        ...
    
    @property
    def center_point(self) -> aspose.cad.fileformats.cad.cadobjects.Cad2DPoint:
        ...
    
    @center_point.setter
    def center_point(self, value : aspose.cad.fileformats.cad.cadobjects.Cad2DPoint):
        ...
    
    @property
    def snap_point(self) -> aspose.cad.fileformats.cad.cadobjects.Cad2DPoint:
        ...
    
    @snap_point.setter
    def snap_point(self, value : aspose.cad.fileformats.cad.cadobjects.Cad2DPoint):
        ...
    
    @property
    def snap_spacing(self) -> aspose.cad.fileformats.cad.cadobjects.Cad2DPoint:
        ...
    
    @snap_spacing.setter
    def snap_spacing(self, value : aspose.cad.fileformats.cad.cadobjects.Cad2DPoint):
        ...
    
    @property
    def grid_spacing(self) -> aspose.cad.fileformats.cad.cadobjects.Cad2DPoint:
        ...
    
    @grid_spacing.setter
    def grid_spacing(self, value : aspose.cad.fileformats.cad.cadobjects.Cad2DPoint):
        ...
    
    @property
    def view_direction(self) -> aspose.cad.fileformats.cad.cadobjects.Cad3DPoint:
        ...
    
    @view_direction.setter
    def view_direction(self, value : aspose.cad.fileformats.cad.cadobjects.Cad3DPoint):
        ...
    
    @property
    def view_target_point(self) -> aspose.cad.fileformats.cad.cadobjects.Cad3DPoint:
        ...
    
    @view_target_point.setter
    def view_target_point(self, value : aspose.cad.fileformats.cad.cadobjects.Cad3DPoint):
        ...
    
    @property
    def lens_length(self) -> float:
        ...
    
    @lens_length.setter
    def lens_length(self, value : float):
        ...
    
    @property
    def view_aspect_ratio(self) -> float:
        ...
    
    @view_aspect_ratio.setter
    def view_aspect_ratio(self, value : float):
        ...
    
    @property
    def use_aspect_ratio(self) -> bool:
        ...
    
    @use_aspect_ratio.setter
    def use_aspect_ratio(self, value : bool):
        ...
    
    @property
    def front_clipping(self) -> float:
        ...
    
    @front_clipping.setter
    def front_clipping(self, value : float):
        ...
    
    @property
    def back_clipping(self) -> float:
        ...
    
    @back_clipping.setter
    def back_clipping(self, value : float):
        ...
    
    @property
    def view_height(self) -> float:
        ...
    
    @view_height.setter
    def view_height(self, value : float):
        ...
    
    @property
    def snap_rotation_angle(self) -> float:
        ...
    
    @snap_rotation_angle.setter
    def snap_rotation_angle(self, value : float):
        ...
    
    @property
    def view_twist_angle(self) -> float:
        ...
    
    @view_twist_angle.setter
    def view_twist_angle(self, value : float):
        ...
    
    @property
    def circle_sides(self) -> int:
        ...
    
    @circle_sides.setter
    def circle_sides(self, value : int):
        ...
    
    @property
    def fast_zoom(self) -> int:
        ...
    
    @fast_zoom.setter
    def fast_zoom(self, value : int):
        ...
    
    @property
    def grid_on_off(self) -> int:
        ...
    
    @grid_on_off.setter
    def grid_on_off(self, value : int):
        ...
    
    @property
    def style_sheet(self) -> str:
        ...
    
    @style_sheet.setter
    def style_sheet(self, value : str):
        ...
    
    @property
    def render_mode(self) -> int:
        ...
    
    @render_mode.setter
    def render_mode(self, value : int):
        ...
    
    @property
    def view_mode(self) -> int:
        ...
    
    @view_mode.setter
    def view_mode(self, value : int):
        ...
    
    @property
    def ucs_icon(self) -> int:
        ...
    
    @ucs_icon.setter
    def ucs_icon(self, value : int):
        ...
    
    @property
    def snap_on_off(self) -> int:
        ...
    
    @snap_on_off.setter
    def snap_on_off(self, value : int):
        ...
    
    @property
    def snap_style(self) -> int:
        ...
    
    @snap_style.setter
    def snap_style(self, value : int):
        ...
    
    @property
    def snap_isopair(self) -> int:
        ...
    
    @snap_isopair.setter
    def snap_isopair(self, value : int):
        ...
    
    @property
    def ucs_origin(self) -> aspose.cad.fileformats.cad.cadobjects.Cad3DPoint:
        ...
    
    @ucs_origin.setter
    def ucs_origin(self, value : aspose.cad.fileformats.cad.cadobjects.Cad3DPoint):
        ...
    
    @property
    def ucs_xaxis(self) -> aspose.cad.fileformats.cad.cadobjects.Cad3DPoint:
        ...
    
    @ucs_xaxis.setter
    def ucs_xaxis(self, value : aspose.cad.fileformats.cad.cadobjects.Cad3DPoint):
        ...
    
    @property
    def ucs_yaxis(self) -> aspose.cad.fileformats.cad.cadobjects.Cad3DPoint:
        ...
    
    @ucs_yaxis.setter
    def ucs_yaxis(self, value : aspose.cad.fileformats.cad.cadobjects.Cad3DPoint):
        ...
    
    @property
    def ucs_handle(self) -> str:
        ...
    
    @ucs_handle.setter
    def ucs_handle(self, value : str):
        ...
    
    @property
    def ucs_base_handle(self) -> str:
        ...
    
    @ucs_base_handle.setter
    def ucs_base_handle(self, value : str):
        ...
    
    @property
    def ucs_type(self) -> int:
        ...
    
    @ucs_type.setter
    def ucs_type(self, value : int):
        ...
    
    @property
    def elevation(self) -> float:
        '''Gets the elevation.'''
        ...
    
    @elevation.setter
    def elevation(self, value : float):
        '''Sets the elevation.'''
        ...
    
    @property
    def shade_plot_setting(self) -> Optional[int]:
        ...
    
    @shade_plot_setting.setter
    def shade_plot_setting(self, value : Optional[int]):
        ...
    
    @property
    def major_grid_lines(self) -> int:
        ...
    
    @major_grid_lines.setter
    def major_grid_lines(self, value : int):
        ...
    
    @property
    def background_handle(self) -> str:
        ...
    
    @background_handle.setter
    def background_handle(self, value : str):
        ...
    
    @property
    def shade_handle(self) -> str:
        ...
    
    @shade_handle.setter
    def shade_handle(self, value : str):
        ...
    
    @property
    def visual_style_handle(self) -> str:
        ...
    
    @visual_style_handle.setter
    def visual_style_handle(self, value : str):
        ...
    
    @property
    def default_lights(self) -> bool:
        ...
    
    @default_lights.setter
    def default_lights(self, value : bool):
        ...
    
    @property
    def default_light_type(self) -> int:
        ...
    
    @default_light_type.setter
    def default_light_type(self, value : int):
        ...
    
    @property
    def table_contrast(self) -> float:
        ...
    
    @table_contrast.setter
    def table_contrast(self, value : float):
        ...
    
    @property
    def table_brightness(self) -> float:
        ...
    
    @table_brightness.setter
    def table_brightness(self, value : float):
        ...
    
    @property
    def ambient_color1(self) -> int:
        ...
    
    @ambient_color1.setter
    def ambient_color1(self, value : int):
        ...
    
    @property
    def ambient_color2(self) -> int:
        ...
    
    @ambient_color2.setter
    def ambient_color2(self, value : int):
        ...
    
    @property
    def ambient_color3(self) -> str:
        ...
    
    @ambient_color3.setter
    def ambient_color3(self, value : str):
        ...
    
    ...

