from __future__ import annotations
from typing import overload, Any, List, Dict, Tuple, Set, Sequence, Union
from pyopenms import *  # pylint: disable=wildcard-import; lgtm(py/polluting-import)
import numpy as _np

from enum import IntEnum as _PyEnum


def __static_File_absolutePath(file: Union[bytes, str, String] ) -> Union[bytes, str, String]:
    """
    Cython signature: String absolutePath(String file)
    """
    ...

def __static_File_basename(file: Union[bytes, str, String] ) -> Union[bytes, str, String]:
    """
    Cython signature: String basename(String file)
    """
    ...

def __static_FileHandler_computeFileHash(filename: Union[bytes, str, String] ) -> Union[bytes, str, String]:
    """
    Cython signature: String computeFileHash(const String & filename)
    """
    ...

def __static_MetaboliteSpectralMatching_computeHyperScore(fragment_mass_error: float , fragment_mass_tolerance_unit_ppm: bool , exp_spectrum: MSSpectrum , db_spectrum: MSSpectrum , annotations: List[PeptideHit_PeakAnnotation] , mz_lower_bound: float ) -> float:
    """
    Cython signature: double computeHyperScore(double fragment_mass_error, bool fragment_mass_tolerance_unit_ppm, MSSpectrum exp_spectrum, MSSpectrum db_spectrum, libcpp_vector[PeptideHit_PeakAnnotation] & annotations, double mz_lower_bound)
    """
    ...

def __static_File_empty(file: Union[bytes, str, String] ) -> bool:
    """
    Cython signature: bool empty(String file)
    """
    ...

def __static_File_exists(file: Union[bytes, str, String] ) -> bool:
    """
    Cython signature: bool exists(String file)
    """
    ...

def __static_File_fileList(dir: Union[bytes, str, String] , file_pattern: Union[bytes, str, String] , output: List[bytes] , full_path: bool ) -> bool:
    """
    Cython signature: bool fileList(String dir, String file_pattern, StringList output, bool full_path)
    """
    ...

def __static_File_find(filename: Union[bytes, str, String] , directories: List[bytes] ) -> Union[bytes, str, String]:
    """
    Cython signature: String find(String filename, StringList directories)
    """
    ...

def __static_File_findDatabase(db_name: Union[bytes, str, String] ) -> Union[bytes, str, String]:
    """
    Cython signature: String findDatabase(String db_name)
    """
    ...

def __static_File_findDoc(filename: Union[bytes, str, String] ) -> Union[bytes, str, String]:
    """
    Cython signature: String findDoc(String filename)
    """
    ...

def __static_File_findExecutable(toolName: Union[bytes, str, String] ) -> Union[bytes, str, String]:
    """
    Cython signature: String findExecutable(String toolName)
    """
    ...

def __static_OpenMSOSInfo_getBinaryArchitecture() -> Union[bytes, str, String]:
    """
    Cython signature: String getBinaryArchitecture()
    """
    ...

def __static_OpenMSBuildInfo_getBuildType() -> Union[bytes, str, String]:
    """
    Cython signature: String getBuildType()
    """
    ...

def __static_TransformationModelBSpline_getDefaultParameters(params: Param ) -> None:
    """
    Cython signature: void getDefaultParameters(Param & params)
    """
    ...

def __static_File_getExecutablePath() -> Union[bytes, str, String]:
    """
    Cython signature: String getExecutablePath()
    """
    ...

def __static_OpenMSOSInfo_getOSInfo() -> OpenMSOSInfo:
    """
    Cython signature: OpenMSOSInfo getOSInfo()
    """
    ...

def __static_OpenMSBuildInfo_getOpenMPMaxNumThreads() -> int:
    """
    Cython signature: size_t getOpenMPMaxNumThreads()
    """
    ...

def __static_File_getOpenMSDataPath() -> Union[bytes, str, String]:
    """
    Cython signature: String getOpenMSDataPath()
    """
    ...

def __static_File_getOpenMSHomePath() -> Union[bytes, str, String]:
    """
    Cython signature: String getOpenMSHomePath()
    """
    ...

def __static_File_getSystemParameters() -> Param:
    """
    Cython signature: Param getSystemParameters()
    """
    ...

def __static_File_getTempDirectory() -> Union[bytes, str, String]:
    """
    Cython signature: String getTempDirectory()
    """
    ...

def __static_File_getTemporaryFile(alternative_file: Union[bytes, str, String] ) -> Union[bytes, str, String]:
    """
    Cython signature: String getTemporaryFile(const String & alternative_file)
    """
    ...

def __static_FileHandler_getType(filename: Union[bytes, str, String] ) -> int:
    """
    Cython signature: int getType(const String & filename)
    """
    ...

def __static_FileHandler_getTypeByContent(filename: Union[bytes, str, String] ) -> int:
    """
    Cython signature: FileType getTypeByContent(const String & filename)
    """
    ...

def __static_FileHandler_getTypeByFileName(filename: Union[bytes, str, String] ) -> int:
    """
    Cython signature: FileType getTypeByFileName(const String & filename)
    """
    ...

def __static_File_getUniqueName() -> Union[bytes, str, String]:
    """
    Cython signature: String getUniqueName()
    """
    ...

def __static_File_getUserDirectory() -> Union[bytes, str, String]:
    """
    Cython signature: String getUserDirectory()
    """
    ...

def __static_FileHandler_hasValidExtension(filename: Union[bytes, str, String] , type_: int ) -> bool:
    """
    Cython signature: bool hasValidExtension(const String & filename, FileType type_)
    """
    ...

def __static_File_isDirectory(path: Union[bytes, str, String] ) -> bool:
    """
    Cython signature: bool isDirectory(String path)
    """
    ...

def __static_OpenMSBuildInfo_isOpenMPEnabled() -> bool:
    """
    Cython signature: bool isOpenMPEnabled()
    """
    ...

def __static_FileHandler_isSupported(type_: int ) -> bool:
    """
    Cython signature: bool isSupported(FileType type_)
    """
    ...

def __static_File_path(file: Union[bytes, str, String] ) -> Union[bytes, str, String]:
    """
    Cython signature: String path(String file)
    """
    ...

def __static_File_readable(file: Union[bytes, str, String] ) -> bool:
    """
    Cython signature: bool readable(String file)
    """
    ...

def __static_File_remove(file: Union[bytes, str, String] ) -> bool:
    """
    Cython signature: bool remove(String file)
    """
    ...

def __static_File_removeDirRecursively(dir_name: Union[bytes, str, String] ) -> bool:
    """
    Cython signature: bool removeDirRecursively(String dir_name)
    """
    ...

def __static_File_rename(old_filename: Union[bytes, str, String] , new_filename: Union[bytes, str, String] , overwrite_existing: bool , verbose: bool ) -> bool:
    """
    Cython signature: bool rename(const String & old_filename, const String & new_filename, bool overwrite_existing, bool verbose)
    """
    ...

def __static_OpenMSBuildInfo_setOpenMPNumThreads(num_threads: int ) -> None:
    """
    Cython signature: void setOpenMPNumThreads(int num_threads)
    """
    ...

def __static_FileHandler_stripExtension(file: Union[bytes, str, String] ) -> Union[bytes, str, String]:
    """
    Cython signature: String stripExtension(String file)
    """
    ...

def __static_FileHandler_swapExtension(filename: Union[bytes, str, String] , new_type: int ) -> Union[bytes, str, String]:
    """
    Cython signature: String swapExtension(String filename, FileType new_type)
    """
    ...

def __static_File_writable(file: Union[bytes, str, String] ) -> bool:
    """
    Cython signature: bool writable(String file)
    """
    ...

def __static_FLASHDeconvSpectrumFile_writeMzML(map_in: MSExperiment , deconvolved_spectra: List[DeconvolvedSpectrum] , deconvolved_mzML_file: String , annotated_mzML_file: String , mzml_charge: int , tols: List[float] ) -> None:
    """
    Cython signature: void writeMzML(MSExperiment & map_in, libcpp_vector[DeconvolvedSpectrum] & deconvolved_spectra, String & deconvolved_mzML_file, String & annotated_mzML_file, int mzml_charge, libcpp_vector[double] tols)
        Write deconvolved and annotated mzML files.
        :param map_in: The original MSExperiment
        :param deconvolved_spectra: The deconvolved spectra
        :param deconvolved_mzML_file: Output path for deconvolved mzML
        :param annotated_mzML_file: Output path for annotated mzML
        :param mzml_charge: Charge to use in output mzML
        :param tols: Mass tolerances per MS level
    """
    ...


class AbsoluteQuantitationMethodFile:
    """
    Cython implementation of _AbsoluteQuantitationMethodFile

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1AbsoluteQuantitationMethodFile.html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void AbsoluteQuantitationMethodFile()
        """
        ...
    
    @overload
    def __init__(self, in_0: AbsoluteQuantitationMethodFile ) -> None:
        """
        Cython signature: void AbsoluteQuantitationMethodFile(AbsoluteQuantitationMethodFile &)
        """
        ...
    
    def load(self, filename: Union[bytes, str, String] , aqm_list: List[AbsoluteQuantitationMethod] ) -> None:
        """
        Cython signature: void load(const String & filename, libcpp_vector[AbsoluteQuantitationMethod] & aqm_list)
        """
        ...
    
    def store(self, filename: Union[bytes, str, String] , aqm_list: List[AbsoluteQuantitationMethod] ) -> None:
        """
        Cython signature: void store(const String & filename, const libcpp_vector[AbsoluteQuantitationMethod] & aqm_list)
        """
        ... 


class AbsoluteQuantitationStandardsFile:
    """
    Cython implementation of _AbsoluteQuantitationStandardsFile

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1AbsoluteQuantitationStandardsFile.html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void AbsoluteQuantitationStandardsFile()
        """
        ...
    
    @overload
    def __init__(self, in_0: AbsoluteQuantitationStandardsFile ) -> None:
        """
        Cython signature: void AbsoluteQuantitationStandardsFile(AbsoluteQuantitationStandardsFile &)
        """
        ...
    
    def load(self, filename: Union[bytes, str, String] , run_concentrations: List[AQS_runConcentration] ) -> None:
        """
        Cython signature: void load(const String & filename, libcpp_vector[AQS_runConcentration] & run_concentrations)
        """
        ... 


class Adduct:
    """
    Cython implementation of _Adduct

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1Adduct.html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void Adduct()
        """
        ...
    
    @overload
    def __init__(self, in_0: Adduct ) -> None:
        """
        Cython signature: void Adduct(Adduct &)
        """
        ...
    
    @overload
    def __init__(self, charge: int ) -> None:
        """
        Cython signature: void Adduct(int charge)
        """
        ...
    
    @overload
    def __init__(self, charge: int , amount: int , singleMass: float , formula: Union[bytes, str, String] , log_prob: float , rt_shift: float , label: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void Adduct(int charge, int amount, double singleMass, String formula, double log_prob, double rt_shift, String label)
        """
        ...
    
    def getCharge(self) -> int:
        """
        Cython signature: int getCharge()
        """
        ...
    
    def setCharge(self, charge: int ) -> None:
        """
        Cython signature: void setCharge(int charge)
        """
        ...
    
    def getAmount(self) -> int:
        """
        Cython signature: int getAmount()
        """
        ...
    
    def setAmount(self, amount: int ) -> None:
        """
        Cython signature: void setAmount(int amount)
        """
        ...
    
    def getSingleMass(self) -> float:
        """
        Cython signature: double getSingleMass()
        """
        ...
    
    def setSingleMass(self, singleMass: float ) -> None:
        """
        Cython signature: void setSingleMass(double singleMass)
        """
        ...
    
    def getLogProb(self) -> float:
        """
        Cython signature: double getLogProb()
        """
        ...
    
    def setLogProb(self, log_prob: float ) -> None:
        """
        Cython signature: void setLogProb(double log_prob)
        """
        ...
    
    def getFormula(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getFormula()
        """
        ...
    
    def setFormula(self, formula: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setFormula(String formula)
        """
        ...
    
    def getRTShift(self) -> float:
        """
        Cython signature: double getRTShift()
        """
        ...
    
    def getLabel(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getLabel()
        """
        ... 


class BiGaussModel:
    """
    Cython implementation of _BiGaussModel

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1BiGaussModel.html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void BiGaussModel()
        """
        ...
    
    @overload
    def __init__(self, in_0: BiGaussModel ) -> None:
        """
        Cython signature: void BiGaussModel(BiGaussModel &)
        """
        ...
    
    def setOffset(self, offset: float ) -> None:
        """
        Cython signature: void setOffset(double offset)
        """
        ...
    
    def setSamples(self) -> None:
        """
        Cython signature: void setSamples()
        """
        ...
    
    def getCenter(self) -> float:
        """
        Cython signature: double getCenter()
        """
        ... 


class ChannelInfo:
    """
    Cython implementation of _ChannelInfo

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1ChannelInfo.html>`_
    """
    
    description: bytes
    
    name: int
    
    id: int
    
    center: float
    
    active: bool 


class ChromatogramRangeManager:
    """
    Cython implementation of _ChromatogramRangeManager

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1ChromatogramRangeManager.html>`_

    Range manager for chromatograms
    
    This class manages retention time, m/z, and intensity ranges for multiple chromatograms.
    It extends the basic RangeManager to provide specialized functionality for chromatogram data.
    
    The template parameters for the base RangeManager are ordered differently than in SpectrumRangeManager:
    - RangeRT (retention time) is the first parameter, as it's the primary dimension for chromatograms
    - RangeIntensity is the second parameter
    - RangeMZ is the third parameter
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void ChromatogramRangeManager()
        """
        ...
    
    @overload
    def __init__(self, in_0: ChromatogramRangeManager ) -> None:
        """
        Cython signature: void ChromatogramRangeManager(ChromatogramRangeManager &)
        """
        ...
    
    def clearRanges(self) -> None:
        """
        Cython signature: void clearRanges()
        """
        ...
    
    def getMinRT(self) -> float:
        """
        Cython signature: double getMinRT()
        """
        ...
    
    def getMaxRT(self) -> float:
        """
        Cython signature: double getMaxRT()
        """
        ...
    
    def getMinMZ(self) -> float:
        """
        Cython signature: double getMinMZ()
        """
        ...
    
    def getMaxMZ(self) -> float:
        """
        Cython signature: double getMaxMZ()
        """
        ...
    
    def getMinIntensity(self) -> float:
        """
        Cython signature: double getMinIntensity()
        """
        ...
    
    def getMaxIntensity(self) -> float:
        """
        Cython signature: double getMaxIntensity()
        """
        ... 


class ContactPerson:
    """
    Cython implementation of _ContactPerson

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1ContactPerson.html>`_
      -- Inherits from ['MetaInfoInterface']
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void ContactPerson()
        """
        ...
    
    @overload
    def __init__(self, in_0: ContactPerson ) -> None:
        """
        Cython signature: void ContactPerson(ContactPerson &)
        """
        ...
    
    def getFirstName(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getFirstName()
        Returns the first name of the person
        """
        ...
    
    def setFirstName(self, name: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setFirstName(String name)
        Sets the first name of the person
        """
        ...
    
    def getLastName(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getLastName()
        Returns the last name of the person
        """
        ...
    
    def setLastName(self, name: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setLastName(String name)
        Sets the last name of the person
        """
        ...
    
    def setName(self, name: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setName(String name)
        Sets the full name of the person (gets split into first and last name internally)
        """
        ...
    
    def getInstitution(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getInstitution()
        Returns the affiliation
        """
        ...
    
    def setInstitution(self, institution: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setInstitution(String institution)
        Sets the affiliation
        """
        ...
    
    def getEmail(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getEmail()
        Returns the email address
        """
        ...
    
    def setEmail(self, email: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setEmail(String email)
        Sets the email address
        """
        ...
    
    def getURL(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getURL()
        Returns the URL associated with the contact person (e.g., the institute webpage
        """
        ...
    
    def setURL(self, email: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setURL(String email)
        Sets the URL associated with the contact person (e.g., the institute webpage
        """
        ...
    
    def getAddress(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getAddress()
        Returns the address
        """
        ...
    
    def setAddress(self, email: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setAddress(String email)
        Sets the address
        """
        ...
    
    def getContactInfo(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getContactInfo()
        Returns miscellaneous info about the contact person
        """
        ...
    
    def setContactInfo(self, contact_info: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setContactInfo(String contact_info)
        Sets miscellaneous info about the contact person
        """
        ...
    
    def isMetaEmpty(self) -> bool:
        """
        Cython signature: bool isMetaEmpty()
        Returns if the MetaInfo is empty
        """
        ...
    
    def clearMetaInfo(self) -> None:
        """
        Cython signature: void clearMetaInfo()
        Removes all meta values
        """
        ...
    
    def metaRegistry(self) -> MetaInfoRegistry:
        """
        Cython signature: MetaInfoRegistry metaRegistry()
        Returns a reference to the MetaInfoRegistry
        """
        ...
    
    def getKeys(self, keys: List[bytes] ) -> None:
        """
        Cython signature: void getKeys(libcpp_vector[String] & keys)
        Fills the given vector with a list of all keys for which a value is set
        """
        ...
    
    def getMetaValue(self, in_0: Union[bytes, str, String] ) -> Union[int, float, bytes, str, List[int], List[float], List[bytes]]:
        """
        Cython signature: DataValue getMetaValue(String)
        Returns the value corresponding to a string, or
        """
        ...
    
    def setMetaValue(self, in_0: Union[bytes, str, String] , in_1: Union[int, float, bytes, str, List[int], List[float], List[bytes]] ) -> None:
        """
        Cython signature: void setMetaValue(String, DataValue)
        Sets the DataValue corresponding to a name
        """
        ...
    
    def metaValueExists(self, in_0: Union[bytes, str, String] ) -> bool:
        """
        Cython signature: bool metaValueExists(String)
        Returns whether an entry with the given name exists
        """
        ...
    
    def removeMetaValue(self, in_0: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void removeMetaValue(String)
        Removes the DataValue corresponding to `name` if it exists
        """
        ...
    
    def __richcmp__(self, other: ContactPerson, op: int) -> Any:
        ... 


class CrossLinksDB:
    """
    Cython implementation of _CrossLinksDB

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1CrossLinksDB.html>`_
    """
    
    def getNumberOfModifications(self) -> int:
        """
        Cython signature: size_t getNumberOfModifications()
        """
        ...
    
    def searchModifications(self, mods: Set[ResidueModification] , mod_name: Union[bytes, str, String] , residue: Union[bytes, str, String] , term_spec: int ) -> None:
        """
        Cython signature: void searchModifications(libcpp_set[const ResidueModification *] & mods, const String & mod_name, const String & residue, TermSpecificity term_spec)
        """
        ...
    
    @overload
    def getModification(self, index: int ) -> ResidueModification:
        """
        Cython signature: const ResidueModification * getModification(size_t index)
        """
        ...
    
    @overload
    def getModification(self, mod_name: Union[bytes, str, String] ) -> ResidueModification:
        """
        Cython signature: const ResidueModification * getModification(const String & mod_name)
        """
        ...
    
    @overload
    def getModification(self, mod_name: Union[bytes, str, String] , residue: Union[bytes, str, String] , term_spec: int ) -> ResidueModification:
        """
        Cython signature: const ResidueModification * getModification(const String & mod_name, const String & residue, TermSpecificity term_spec)
        """
        ...
    
    def has(self, modification: Union[bytes, str, String] ) -> bool:
        """
        Cython signature: bool has(String modification)
        """
        ...
    
    def findModificationIndex(self, mod_name: Union[bytes, str, String] ) -> int:
        """
        Cython signature: size_t findModificationIndex(const String & mod_name)
        """
        ...
    
    def searchModificationsByDiffMonoMass(self, mods: List[bytes] , mass: float , max_error: float , residue: Union[bytes, str, String] , term_spec: int ) -> None:
        """
        Cython signature: void searchModificationsByDiffMonoMass(libcpp_vector[String] & mods, double mass, double max_error, const String & residue, TermSpecificity term_spec)
        """
        ...
    
    def getBestModificationByDiffMonoMass(self, mass: float , max_error: float , residue: Union[bytes, str, String] , term_spec: int ) -> ResidueModification:
        """
        Cython signature: const ResidueModification * getBestModificationByDiffMonoMass(double mass, double max_error, const String residue, TermSpecificity term_spec)
        """
        ...
    
    def getAllSearchModifications(self, modifications: List[bytes] ) -> None:
        """
        Cython signature: void getAllSearchModifications(libcpp_vector[String] & modifications)
        """
        ...
    
    def readFromOBOFile(self, filename: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void readFromOBOFile(const String & filename)
        """
        ...
    
    def isInstantiated(self) -> bool:
        """
        Cython signature: bool isInstantiated()
        """
        ... 


class CsvFile:
    """
    Cython implementation of _CsvFile

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1CsvFile.html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void CsvFile()
        """
        ...
    
    @overload
    def __init__(self, in_0: CsvFile ) -> None:
        """
        Cython signature: void CsvFile(CsvFile &)
        """
        ...
    
    def load(self, filename: Union[bytes, str, String] , is_: bytes , ie_: bool , first_n: int ) -> None:
        """
        Cython signature: void load(const String & filename, char is_, bool ie_, int first_n)
        Loads data from a text file
        """
        ...
    
    def store(self, filename: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void store(const String & filename)
        Stores the buffer's content into a file
        """
        ...
    
    def addRow(self, list: List[bytes] ) -> None:
        """
        Cython signature: void addRow(const StringList & list)
        Add a row to the buffer
        """
        ...
    
    def clear(self) -> None:
        """
        Cython signature: void clear()
        Clears the buffer
        """
        ...
    
    def getRow(self, row: int , list: List[bytes] ) -> bool:
        """
        Cython signature: bool getRow(int row, StringList & list)
        Writes all items from a row to list
        """
        ... 


class DBoundingBox2:
    """
    Cython implementation of _DBoundingBox2

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1DBoundingBox2.html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void DBoundingBox2()
        """
        ...
    
    @overload
    def __init__(self, in_0: DBoundingBox2 ) -> None:
        """
        Cython signature: void DBoundingBox2(DBoundingBox2 &)
        """
        ...
    
    def minPosition(self) -> Union[Sequence[int], Sequence[float]]:
        """
        Cython signature: DPosition2 minPosition()
        """
        ...
    
    def maxPosition(self) -> Union[Sequence[int], Sequence[float]]:
        """
        Cython signature: DPosition2 maxPosition()
        """
        ... 


class DeconvolvedSpectrum:
    """
    Cython implementation of _DeconvolvedSpectrum

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1DeconvolvedSpectrum.html>`_

    A class representing a deconvolved spectrum.
    DeconvolvedSpectrum consists of PeakGroup instances representing masses.
    For MSn n>1, a PeakGroup representing the precursor mass is also added.
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void DeconvolvedSpectrum()
        """
        ...
    
    @overload
    def __init__(self, in_0: DeconvolvedSpectrum ) -> None:
        """
        Cython signature: void DeconvolvedSpectrum(DeconvolvedSpectrum &)
        """
        ...
    
    @overload
    def __init__(self, scan_number: int ) -> None:
        """
        Cython signature: void DeconvolvedSpectrum(int scan_number)
        Constructor with scan number
        """
        ...
    
    def toSpectrum(self, to_charge: int , tol: float , retain_undeconvolved: bool ) -> MSSpectrum:
        """
        Cython signature: MSSpectrum toSpectrum(int to_charge, double tol, bool retain_undeconvolved)
        Convert DeconvolvedSpectrum to MSSpectrum.
        :param to_charge: The charge of each peak in output
        :param tol: The ppm tolerance
        :param retain_undeconvolved: If true, undeconvolved peaks are included
        """
        ...
    
    def getOriginalSpectrum(self) -> MSSpectrum:
        """
        Cython signature: MSSpectrum getOriginalSpectrum()
        Returns the original spectrum
        """
        ...
    
    def getPrecursorPeakGroup(self) -> PeakGroup:
        """
        Cython signature: PeakGroup getPrecursorPeakGroup()
        Returns the precursor peak group (MSn, n>1)
        """
        ...
    
    def getPrecursorCharge(self) -> int:
        """
        Cython signature: int getPrecursorCharge()
        Returns the precursor charge
        """
        ...
    
    def getPrecursor(self) -> Precursor:
        """
        Cython signature: Precursor getPrecursor()
        Returns the precursor peak
        """
        ...
    
    def getScanNumber(self) -> int:
        """
        Cython signature: int getScanNumber()
        Returns the scan number
        """
        ...
    
    def getPrecursorScanNumber(self) -> int:
        """
        Cython signature: int getPrecursorScanNumber()
        Returns the precursor scan number
        """
        ...
    
    def getCurrentMaxMass(self, max_mass: float ) -> float:
        """
        Cython signature: double getCurrentMaxMass(double max_mass)
        Returns the current max mass
        """
        ...
    
    def getCurrentMinMass(self, min_mass: float ) -> float:
        """
        Cython signature: double getCurrentMinMass(double min_mass)
        Returns the current min mass
        """
        ...
    
    def getCurrentMaxAbsCharge(self, max_abs_charge: int ) -> int:
        """
        Cython signature: int getCurrentMaxAbsCharge(int max_abs_charge)
        Returns the current max charge
        """
        ...
    
    def getQuantities(self) -> IsobaricQuantities:
        """
        Cython signature: IsobaricQuantities getQuantities()
        Returns isobaric quantities
        """
        ...
    
    def isDecoy(self) -> bool:
        """
        Cython signature: bool isDecoy()
        Returns true if this is a decoy spectrum
        """
        ...
    
    def setOriginalSpectrum(self, spec: MSSpectrum ) -> None:
        """
        Cython signature: void setOriginalSpectrum(MSSpectrum & spec)
        Sets the original spectrum
        """
        ...
    
    def setPrecursor(self, precursor: Precursor ) -> None:
        """
        Cython signature: void setPrecursor(Precursor & precursor)
        Sets the precursor
        """
        ...
    
    def setPrecursorScanNumber(self, scan_number: int ) -> None:
        """
        Cython signature: void setPrecursorScanNumber(int scan_number)
        Sets the precursor scan number
        """
        ...
    
    def setPrecursorPeakGroup(self, pg: PeakGroup ) -> None:
        """
        Cython signature: void setPrecursorPeakGroup(PeakGroup & pg)
        Sets the precursor peak group
        """
        ...
    
    def setPeakGroups(self, x: List[PeakGroup] ) -> None:
        """
        Cython signature: void setPeakGroups(libcpp_vector[PeakGroup] & x)
        Sets peak groups
        """
        ...
    
    def setQuantities(self, quantities: IsobaricQuantities ) -> None:
        """
        Cython signature: void setQuantities(IsobaricQuantities & quantities)
        Sets isobaric quantities
        """
        ...
    
    def size(self) -> int:
        """
        Cython signature: size_t size()
        Returns number of peak groups
        """
        ...
    
    def empty(self) -> bool:
        """
        Cython signature: bool empty()
        Returns true if no peak groups
        """
        ...
    
    def clear(self) -> None:
        """
        Cython signature: void clear()
        Clears all peak groups
        """
        ...
    
    def reserve(self, n: int ) -> None:
        """
        Cython signature: void reserve(size_t n)
        Reserves space for n peak groups
        """
        ...
    
    def push_back(self, pg: PeakGroup ) -> None:
        """
        Cython signature: void push_back(PeakGroup & pg)
        Adds a peak group
        """
        ...
    
    def pop_back(self) -> None:
        """
        Cython signature: void pop_back()
        Removes the last peak group
        """
        ...
    
    def __getitem__(self, i: int ) -> PeakGroup:
        """
        Cython signature: PeakGroup & operator[](size_t i)
        """
        ...
    def __setitem__(self, key: int, value: PeakGroup) -> None:
        """Cython signature: PeakGroup & operator[](size_t i)"""
        ...
    
    def sort(self) -> None:
        """
        Cython signature: void sort()
        Sorts peak groups by monoisotopic mass
        """
        ...
    
    def sortByQscore(self) -> None:
        """
        Cython signature: void sortByQscore()
        Sorts peak groups by Qscore
        """
        ...
    
    def __richcmp__(self, other: DeconvolvedSpectrum, op: int) -> Any:
        ...
    
    def __iter__(self) -> PeakGroup:
       ... 


class DecoyGenerator:
    """
    Cython implementation of _DecoyGenerator

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1DecoyGenerator.html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void DecoyGenerator()
        """
        ...
    
    @overload
    def __init__(self, in_0: DecoyGenerator ) -> None:
        """
        Cython signature: void DecoyGenerator(DecoyGenerator &)
        """
        ...
    
    def setSeed(self, in_0: int ) -> None:
        """
        Cython signature: void setSeed(uint64_t)
        """
        ...
    
    def reverseProtein(self, protein: AASequence ) -> AASequence:
        """
        Cython signature: AASequence reverseProtein(const AASequence & protein)
        Reverses the protein sequence
        """
        ...
    
    def reversePeptides(self, protein: AASequence , protease: Union[bytes, str, String] ) -> AASequence:
        """
        Cython signature: AASequence reversePeptides(const AASequence & protein, const String & protease)
        Reverses the protein's peptide sequences between enzymatic cutting positions
        """
        ...
    
    def shufflePeptides(self, aas: AASequence , protease: Union[bytes, str, String] , max_attempts: int ) -> AASequence:
        """
        Cython signature: AASequence shufflePeptides(const AASequence & aas, const String & protease, const int max_attempts)
        Shuffle the protein's peptide sequences between enzymatic cutting positions, each peptide is shuffled @param max_attempts times to minimize sequence identity
        """
        ...
    
    def shuffle(self, protein: AASequence , protease: Union[bytes, str, String] , decoy_factor: int ) -> List[AASequence]:
        """
        Cython signature: libcpp_vector[AASequence] shuffle(const AASequence & protein, const String & protease, int decoy_factor)
        Generate decoy protein sequences using shuffle algorithm. Digests protein using specified protease and shuffles each peptide. For top-down proteomics use "no cleavage". decoy_factor is the number of complete decoy proteins to generate. Returns vector of AASequence
        """
        ... 


class EDTAFile:
    """
    Cython implementation of _EDTAFile

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1EDTAFile.html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void EDTAFile()
        """
        ...
    
    @overload
    def __init__(self, in_0: EDTAFile ) -> None:
        """
        Cython signature: void EDTAFile(EDTAFile &)
        """
        ...
    
    @overload
    def store(self, filename: Union[bytes, str, String] , map: FeatureMap ) -> None:
        """
        Cython signature: void store(String filename, FeatureMap & map)
        """
        ...
    
    @overload
    def store(self, filename: Union[bytes, str, String] , map: ConsensusMap ) -> None:
        """
        Cython signature: void store(String filename, ConsensusMap & map)
        """
        ...
    
    def load(self, filename: Union[bytes, str, String] , consensus_map: ConsensusMap ) -> None:
        """
        Cython signature: void load(String filename, ConsensusMap & consensus_map)
        """
        ... 


class ElutionPeakDetection:
    """
    Cython implementation of _ElutionPeakDetection

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1ElutionPeakDetection.html>`_
      -- Inherits from ['ProgressLogger', 'DefaultParamHandler']
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void ElutionPeakDetection()
        """
        ...
    
    @overload
    def __init__(self, in_0: ElutionPeakDetection ) -> None:
        """
        Cython signature: void ElutionPeakDetection(ElutionPeakDetection &)
        """
        ...
    
    @overload
    def detectPeaks(self, in_: Kernel_MassTrace , out: List[Kernel_MassTrace] ) -> None:
        """
        Cython signature: void detectPeaks(Kernel_MassTrace & in_, libcpp_vector[Kernel_MassTrace] & out)
        """
        ...
    
    @overload
    def detectPeaks(self, in_: List[Kernel_MassTrace] , out: List[Kernel_MassTrace] ) -> None:
        """
        Cython signature: void detectPeaks(libcpp_vector[Kernel_MassTrace] & in_, libcpp_vector[Kernel_MassTrace] & out)
        """
        ...
    
    def filterByPeakWidth(self, in_: List[Kernel_MassTrace] , out: List[Kernel_MassTrace] ) -> None:
        """
        Cython signature: void filterByPeakWidth(libcpp_vector[Kernel_MassTrace] & in_, libcpp_vector[Kernel_MassTrace] & out)
        """
        ...
    
    def computeMassTraceNoise(self, in_0: Kernel_MassTrace ) -> float:
        """
        Cython signature: double computeMassTraceNoise(Kernel_MassTrace &)
        Compute noise level (as RMSE of the actual signal and the smoothed signal)
        """
        ...
    
    def computeMassTraceSNR(self, in_0: Kernel_MassTrace ) -> float:
        """
        Cython signature: double computeMassTraceSNR(Kernel_MassTrace &)
        Compute the signal to noise ratio (estimated by computeMassTraceNoise)
        """
        ...
    
    def computeApexSNR(self, in_0: Kernel_MassTrace ) -> float:
        """
        Cython signature: double computeApexSNR(Kernel_MassTrace &)
        Compute the signal to noise ratio at the apex (estimated by computeMassTraceNoise)
        """
        ...
    
    def findLocalExtrema(self, in_0: Kernel_MassTrace , in_1: int , in_2: List[int] , in_3: List[int] ) -> None:
        """
        Cython signature: void findLocalExtrema(Kernel_MassTrace &, size_t &, libcpp_vector[size_t] &, libcpp_vector[size_t] &)
        """
        ...
    
    def smoothData(self, mt: Kernel_MassTrace , win_size: int ) -> None:
        """
        Cython signature: void smoothData(Kernel_MassTrace & mt, int win_size)
        """
        ...
    
    def setLogType(self, in_0: int ) -> None:
        """
        Cython signature: void setLogType(LogType)
        Sets the progress log that should be used. The default type is NONE!
        """
        ...
    
    def getLogType(self) -> int:
        """
        Cython signature: LogType getLogType()
        Returns the type of progress log being used
        """
        ...
    
    def startProgress(self, begin: int , end: int , label: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void startProgress(ptrdiff_t begin, ptrdiff_t end, String label)
        """
        ...
    
    def setProgress(self, value: int ) -> None:
        """
        Cython signature: void setProgress(ptrdiff_t value)
        Sets the current progress
        """
        ...
    
    def endProgress(self) -> None:
        """
        Cython signature: void endProgress()
        Ends the progress display
        """
        ...
    
    def nextProgress(self) -> None:
        """
        Cython signature: void nextProgress()
        Increment progress by 1 (according to range begin-end)
        """
        ...
    
    def getSubsections(self) -> List[bytes]:
        """
        Cython signature: libcpp_vector[String] getSubsections()
        """
        ...
    
    def setParameters(self, param: Param ) -> None:
        """
        Cython signature: void setParameters(Param & param)
        Sets the parameters
        """
        ...
    
    def getParameters(self) -> Param:
        """
        Cython signature: Param getParameters()
        Returns the parameters
        """
        ...
    
    def getDefaults(self) -> Param:
        """
        Cython signature: Param getDefaults()
        Returns the default parameters
        """
        ...
    
    def getName(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getName()
        Returns the name
        """
        ...
    
    def setName(self, in_0: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setName(const String &)
        Sets the name
        """
        ... 


class EmgGradientDescent:
    """
    Cython implementation of _EmgGradientDescent

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1EmgGradientDescent.html>`_
      -- Inherits from ['DefaultParamHandler']
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void EmgGradientDescent()
        Compute the area, background and shape metrics of a peak
        """
        ...
    
    @overload
    def __init__(self, in_0: EmgGradientDescent ) -> None:
        """
        Cython signature: void EmgGradientDescent(EmgGradientDescent &)
        """
        ...
    
    def getDefaultParameters(self, in_0: Param ) -> None:
        """
        Cython signature: void getDefaultParameters(Param &)
        """
        ...
    
    @overload
    def fitEMGPeakModel(self, input_peak: MSChromatogram , output_peak: MSChromatogram ) -> None:
        """
        Cython signature: void fitEMGPeakModel(MSChromatogram & input_peak, MSChromatogram & output_peak)
        """
        ...
    
    @overload
    def fitEMGPeakModel(self, input_peak: MSSpectrum , output_peak: MSSpectrum ) -> None:
        """
        Cython signature: void fitEMGPeakModel(MSSpectrum & input_peak, MSSpectrum & output_peak)
        """
        ...
    
    @overload
    def fitEMGPeakModel(self, input_peak: MSChromatogram , output_peak: MSChromatogram , left_pos: float , right_pos: float ) -> None:
        """
        Cython signature: void fitEMGPeakModel(MSChromatogram & input_peak, MSChromatogram & output_peak, double left_pos, double right_pos)
        """
        ...
    
    @overload
    def fitEMGPeakModel(self, input_peak: MSSpectrum , output_peak: MSSpectrum , left_pos: float , right_pos: float ) -> None:
        """
        Cython signature: void fitEMGPeakModel(MSSpectrum & input_peak, MSSpectrum & output_peak, double left_pos, double right_pos)
        """
        ...
    
    def getSubsections(self) -> List[bytes]:
        """
        Cython signature: libcpp_vector[String] getSubsections()
        """
        ...
    
    def setParameters(self, param: Param ) -> None:
        """
        Cython signature: void setParameters(Param & param)
        Sets the parameters
        """
        ...
    
    def getParameters(self) -> Param:
        """
        Cython signature: Param getParameters()
        Returns the parameters
        """
        ...
    
    def getDefaults(self) -> Param:
        """
        Cython signature: Param getDefaults()
        Returns the default parameters
        """
        ...
    
    def getName(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getName()
        Returns the name
        """
        ...
    
    def setName(self, in_0: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setName(const String &)
        Sets the name
        """
        ... 


class FLASHDeconvSpectrumFile:
    """
    Cython implementation of _FLASHDeconvSpectrumFile

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1FLASHDeconvSpectrumFile.html>`_

    FLASHDeconv Spectrum level output *.tsv, *.msalign (for TopPIC) file formats.
    This class provides static methods for writing deconvolved spectrum data.
    Note: Methods taking std::ostream are not directly exposed. Use file-based workflows.
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void FLASHDeconvSpectrumFile()
        """
        ...
    
    @overload
    def __init__(self, in_0: FLASHDeconvSpectrumFile ) -> None:
        """
        Cython signature: void FLASHDeconvSpectrumFile(FLASHDeconvSpectrumFile &)
        """
        ...
    
    writeMzML: __static_FLASHDeconvSpectrumFile_writeMzML 


class Feature:
    """
    Cython implementation of _Feature

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1Feature.html>`_
      -- Inherits from ['UniqueIdInterface', 'RichPeak2D']

    An LC-MS feature representing a detected analyte signal
    
    The Feature class represents a two-dimensional (RT and m/z) signal from an analyte
    in LC-MS data. It is one of the core data structures in OpenMS for representing
    detected peaks or compounds.
    
    A Feature stores:
    
    - Position: retention time (RT) and mass-to-charge ratio (m/z)
    - Intensity: the signal strength (typically total ion count)
    - Quality metrics: scores indicating detection confidence
    - Charge state: the charge of the ion
    - Convex hulls: the 2D area occupied by the feature in RT-m/z space
    - Peptide identifications: for identified peptides (optional)
    - Subordinate features: for isotopic peaks or related signals
    
    By convention, the feature's position is at the maximum of the elution profile
    (RT dimension) and at the monoisotopic peak (m/z dimension).
    
    Example usage:
    
    .. code-block:: python
    
       feature = oms.Feature()
       feature.setRT(1234.5)  # Set retention time in seconds
       feature.setMZ(445.678)  # Set m/z value
       feature.setIntensity(100000.0)  # Set intensity
       feature.setCharge(2)  # Set charge state
       feature.setOverallQuality(0.95)  # Set quality score (0-1)
       # Access the values
       print(f"RT: {feature.getRT()}, m/z: {feature.getMZ()}, charge: {feature.getCharge()}")
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void Feature()
        """
        ...
    
    @overload
    def __init__(self, in_0: Feature ) -> None:
        """
        Cython signature: void Feature(Feature &)
        """
        ...
    
    def getQuality(self, index: int ) -> float:
        """
        Cython signature: float getQuality(size_t index)
        Returns the quality score in a specific dimension
        
        :param index: The dimension index (0 for RT, 1 for m/z)
        :return: Quality score for the specified dimension (typically 0-1 range)
        """
        ...
    
    def setQuality(self, index: int , q: float ) -> None:
        """
        Cython signature: void setQuality(size_t index, float q)
        Sets the quality score for a specific dimension
        
        :param index: The dimension index (0 for RT, 1 for m/z)
        :param q: Quality score to set (typically 0-1 range)
        """
        ...
    
    def getOverallQuality(self) -> float:
        """
        Cython signature: float getOverallQuality()
        Returns the overall quality score of the feature
        
        :return: Overall quality score (typically 0-1, where 1 is highest quality)
        
        This score represents the overall confidence in the feature detection
        """
        ...
    
    def setOverallQuality(self, q: float ) -> None:
        """
        Cython signature: void setOverallQuality(float q)
        Sets the overall quality score of the feature
        
        :param q: Overall quality score (typically 0-1, where 1 is highest quality)
        """
        ...
    
    def getSubordinates(self) -> List[Feature]:
        """
        Cython signature: libcpp_vector[Feature] getSubordinates()
        Returns subordinate features (e.g., isotopic peaks)
        
        :return: List of subordinate features associated with this feature
        
        Subordinate features often represent individual isotopic peaks of the same compound
        """
        ...
    
    def setSubordinates(self, in_0: List[Feature] ) -> None:
        """
        Cython signature: void setSubordinates(libcpp_vector[Feature])
        Sets the subordinate features
        
        :param subordinates: List of subordinate features to associate with this feature
        """
        ...
    
    def encloses(self, rt: float , mz: float ) -> bool:
        """
        Cython signature: bool encloses(double rt, double mz)
        Checks if the feature's convex hulls enclose a given position
        
        :param rt: Retention time in seconds
        :param mz: Mass-to-charge ratio
        :return: True if the position (rt, mz) is within the feature's convex hulls, False otherwise
        
        This uses the feature's convex hull representation to determine spatial containment
        """
        ...
    
    def getConvexHull(self) -> ConvexHull2D:
        """
        Cython signature: ConvexHull2D getConvexHull()
        Returns the overall convex hull of the feature
        
        :return: The overall 2D convex hull encompassing all mass traces
        
        This is the union of all individual mass trace convex hulls
        """
        ...
    
    def getConvexHulls(self) -> List[ConvexHull2D]:
        """
        Cython signature: libcpp_vector[ConvexHull2D] getConvexHulls()
        Returns the convex hulls of individual mass traces
        
        :return: List of convex hulls, one for each isotopic mass trace
        
        Each isotopic peak typically has its own convex hull in RT-m/z space
        """
        ...
    
    def setConvexHulls(self, in_0: List[ConvexHull2D] ) -> None:
        """
        Cython signature: void setConvexHulls(libcpp_vector[ConvexHull2D])
        Sets the convex hulls for individual mass traces
        
        :param hulls: List of convex hulls to set for this feature
        """
        ...
    
    def getWidth(self) -> float:
        """
        Cython signature: float getWidth()
        Returns the width (FWHM) of the feature in RT dimension
        
        :return: Full Width at Half Maximum (FWHM) in seconds
        
        Represents the elution peak width
        """
        ...
    
    def setWidth(self, q: float ) -> None:
        """
        Cython signature: void setWidth(float q)
        Sets the width (FWHM) of the feature in RT dimension
        
        :param q: Full Width at Half Maximum in seconds
        """
        ...
    
    def getCharge(self) -> int:
        """
        Cython signature: int getCharge()
        Returns the charge state of the feature
        
        :return: Charge state (e.g., 2 for doubly charged ions, 0 if unknown)
        """
        ...
    
    def setCharge(self, q: int ) -> None:
        """
        Cython signature: void setCharge(int q)
        Sets the charge state of the feature
        
        :param q: Charge state (e.g., 2 for doubly charged ions)
        """
        ...
    
    def getAnnotationState(self) -> int:
        """
        Cython signature: AnnotationState getAnnotationState()
        Returns the annotation state of the feature
        
        :return: Enum indicating the annotation status of this feature
        """
        ...
    
    def getPeptideIdentifications(self) -> PeptideIdentificationList:
        """
        Cython signature: PeptideIdentificationList getPeptideIdentifications()
        Returns the peptide identifications associated with this feature
        
        :return: List of peptide identifications from database search
        
        Only relevant for peptide features. Contains results from peptide identification tools
        """
        ...
    
    def setPeptideIdentifications(self, peptides: PeptideIdentificationList ) -> None:
        """
        Cython signature: void setPeptideIdentifications(PeptideIdentificationList & peptides)
        Sets the peptide identifications for this feature
        
        :param peptides: List of peptide identifications to associate with this feature
        """
        ...
    
    def getUniqueId(self) -> int:
        """
        Cython signature: size_t getUniqueId()
        Returns the unique id
        """
        ...
    
    def clearUniqueId(self) -> int:
        """
        Cython signature: size_t clearUniqueId()
        Clear the unique id. The new unique id will be invalid. Returns 1 if the unique id was changed, 0 otherwise
        """
        ...
    
    def hasValidUniqueId(self) -> int:
        """
        Cython signature: size_t hasValidUniqueId()
        Returns whether the unique id is valid. Returns 1 if the unique id is valid, 0 otherwise
        """
        ...
    
    def hasInvalidUniqueId(self) -> int:
        """
        Cython signature: size_t hasInvalidUniqueId()
        Returns whether the unique id is invalid. Returns 1 if the unique id is invalid, 0 otherwise
        """
        ...
    
    def setUniqueId(self, rhs: int ) -> None:
        """
        Cython signature: void setUniqueId(uint64_t rhs)
        Assigns a new, valid unique id. Always returns 1
        """
        ...
    
    def ensureUniqueId(self) -> int:
        """
        Cython signature: size_t ensureUniqueId()
        Assigns a valid unique id, but only if the present one is invalid. Returns 1 if the unique id was changed, 0 otherwise
        """
        ...
    
    def isValid(self, unique_id: int ) -> bool:
        """
        Cython signature: bool isValid(uint64_t unique_id)
        Returns true if the unique_id is valid, false otherwise
        """
        ...
    
    def getIntensity(self) -> float:
        """
        Cython signature: float getIntensity()
        Returns the data point intensity (height)
        """
        ...
    
    def getMZ(self) -> float:
        """
        Cython signature: double getMZ()
        Returns the m/z coordinate (index 1)
        """
        ...
    
    def getRT(self) -> float:
        """
        Cython signature: double getRT()
        Returns the RT coordinate (index 0)
        """
        ...
    
    def setMZ(self, in_0: float ) -> None:
        """
        Cython signature: void setMZ(double)
        Returns the m/z coordinate (index 1)
        """
        ...
    
    def setRT(self, in_0: float ) -> None:
        """
        Cython signature: void setRT(double)
        Returns the RT coordinate (index 0)
        """
        ...
    
    def setIntensity(self, in_0: float ) -> None:
        """
        Cython signature: void setIntensity(float)
        Returns the data point intensity (height)
        """
        ...
    
    def isMetaEmpty(self) -> bool:
        """
        Cython signature: bool isMetaEmpty()
        Returns if the MetaInfo is empty
        """
        ...
    
    def clearMetaInfo(self) -> None:
        """
        Cython signature: void clearMetaInfo()
        Removes all meta values
        """
        ...
    
    def metaRegistry(self) -> MetaInfoRegistry:
        """
        Cython signature: MetaInfoRegistry metaRegistry()
        Returns a reference to the MetaInfoRegistry
        """
        ...
    
    def getKeys(self, keys: List[bytes] ) -> None:
        """
        Cython signature: void getKeys(libcpp_vector[String] & keys)
        Fills the given vector with a list of all keys for which a value is set
        """
        ...
    
    def getMetaValue(self, in_0: Union[bytes, str, String] ) -> Union[int, float, bytes, str, List[int], List[float], List[bytes]]:
        """
        Cython signature: DataValue getMetaValue(String)
        Returns the value corresponding to a string, or
        """
        ...
    
    def setMetaValue(self, in_0: Union[bytes, str, String] , in_1: Union[int, float, bytes, str, List[int], List[float], List[bytes]] ) -> None:
        """
        Cython signature: void setMetaValue(String, DataValue)
        Sets the DataValue corresponding to a name
        """
        ...
    
    def metaValueExists(self, in_0: Union[bytes, str, String] ) -> bool:
        """
        Cython signature: bool metaValueExists(String)
        Returns whether an entry with the given name exists
        """
        ...
    
    def removeMetaValue(self, in_0: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void removeMetaValue(String)
        Removes the DataValue corresponding to `name` if it exists
        """
        ...
    
    def __richcmp__(self, other: Feature, op: int) -> Any:
        ... 


class FeatureHandle:
    """
    Cython implementation of _FeatureHandle

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1FeatureHandle.html>`_
      -- Inherits from ['Peak2D', 'UniqueIdInterface']
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void FeatureHandle()
        Representation of a Peak2D, RichPeak2D or Feature
        """
        ...
    
    @overload
    def __init__(self, in_0: FeatureHandle ) -> None:
        """
        Cython signature: void FeatureHandle(FeatureHandle &)
        """
        ...
    
    @overload
    def __init__(self, map_index: int , point: Peak2D , element_index: int ) -> None:
        """
        Cython signature: void FeatureHandle(uint64_t map_index, Peak2D & point, uint64_t element_index)
        """
        ...
    
    def getMapIndex(self) -> int:
        """
        Cython signature: uint64_t getMapIndex()
        Returns the map index
        """
        ...
    
    def setMapIndex(self, i: int ) -> None:
        """
        Cython signature: void setMapIndex(uint64_t i)
        Sets the map index
        """
        ...
    
    def setCharge(self, charge: int ) -> None:
        """
        Cython signature: void setCharge(int charge)
        Sets the charge
        """
        ...
    
    def getCharge(self) -> int:
        """
        Cython signature: int getCharge()
        Returns the charge
        """
        ...
    
    def setWidth(self, width: float ) -> None:
        """
        Cython signature: void setWidth(float width)
        Sets the width (FWHM)
        """
        ...
    
    def getWidth(self) -> float:
        """
        Cython signature: float getWidth()
        Returns the width (FWHM)
        """
        ...
    
    def getIntensity(self) -> float:
        """
        Cython signature: float getIntensity()
        Returns the data point intensity (height)
        """
        ...
    
    def getMZ(self) -> float:
        """
        Cython signature: double getMZ()
        Returns the m/z coordinate (index 1)
        """
        ...
    
    def getRT(self) -> float:
        """
        Cython signature: double getRT()
        Returns the RT coordinate (index 0)
        """
        ...
    
    def setMZ(self, in_0: float ) -> None:
        """
        Cython signature: void setMZ(double)
        Returns the m/z coordinate (index 1)
        """
        ...
    
    def setRT(self, in_0: float ) -> None:
        """
        Cython signature: void setRT(double)
        Returns the RT coordinate (index 0)
        """
        ...
    
    def setIntensity(self, in_0: float ) -> None:
        """
        Cython signature: void setIntensity(float)
        Returns the data point intensity (height)
        """
        ...
    
    def getUniqueId(self) -> int:
        """
        Cython signature: size_t getUniqueId()
        Returns the unique id
        """
        ...
    
    def clearUniqueId(self) -> int:
        """
        Cython signature: size_t clearUniqueId()
        Clear the unique id. The new unique id will be invalid. Returns 1 if the unique id was changed, 0 otherwise
        """
        ...
    
    def hasValidUniqueId(self) -> int:
        """
        Cython signature: size_t hasValidUniqueId()
        Returns whether the unique id is valid. Returns 1 if the unique id is valid, 0 otherwise
        """
        ...
    
    def hasInvalidUniqueId(self) -> int:
        """
        Cython signature: size_t hasInvalidUniqueId()
        Returns whether the unique id is invalid. Returns 1 if the unique id is invalid, 0 otherwise
        """
        ...
    
    def setUniqueId(self, rhs: int ) -> None:
        """
        Cython signature: void setUniqueId(uint64_t rhs)
        Assigns a new, valid unique id. Always returns 1
        """
        ...
    
    def ensureUniqueId(self) -> int:
        """
        Cython signature: size_t ensureUniqueId()
        Assigns a valid unique id, but only if the present one is invalid. Returns 1 if the unique id was changed, 0 otherwise
        """
        ...
    
    def isValid(self, unique_id: int ) -> bool:
        """
        Cython signature: bool isValid(uint64_t unique_id)
        Returns true if the unique_id is valid, false otherwise
        """
        ...
    
    def __richcmp__(self, other: FeatureHandle, op: int) -> Any:
        ... 


class File:
    """
    Cython implementation of _File

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1File.html>`_
    """
    
    absolutePath: __static_File_absolutePath
    
    basename: __static_File_basename
    
    empty: __static_File_empty
    
    exists: __static_File_exists
    
    fileList: __static_File_fileList
    
    find: __static_File_find
    
    findDatabase: __static_File_findDatabase
    
    findDoc: __static_File_findDoc
    
    findExecutable: __static_File_findExecutable
    
    getExecutablePath: __static_File_getExecutablePath
    
    getOpenMSDataPath: __static_File_getOpenMSDataPath
    
    getOpenMSHomePath: __static_File_getOpenMSHomePath
    
    getSystemParameters: __static_File_getSystemParameters
    
    getTempDirectory: __static_File_getTempDirectory
    
    getTemporaryFile: __static_File_getTemporaryFile
    
    getUniqueName: __static_File_getUniqueName
    
    getUserDirectory: __static_File_getUserDirectory
    
    isDirectory: __static_File_isDirectory
    
    path: __static_File_path
    
    readable: __static_File_readable
    
    remove: __static_File_remove
    
    removeDirRecursively: __static_File_removeDirRecursively
    
    rename: __static_File_rename
    
    writable: __static_File_writable 


class FileHandler:
    """
    Cython implementation of _FileHandler

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1FileHandler.html>`_
    """
    
    def __init__(self) -> None:
        """
        Cython signature: void FileHandler()
        """
        ...
    
    def loadExperiment(self, in_0: Union[bytes, str, String] , in_1: MSExperiment ) -> None:
        """
        Cython signature: void loadExperiment(String, MSExperiment &)
        Loads a file into an MSExperiment
        
        
        :param filename: The file name of the file to load
        :param exp: The experiment to load the data into
        :param force_type: Forces to load the file with that file type. If no type is forced, it is determined from the extension (or from the content if that fails)
        :param log: Progress logging mode
        :param rewrite_source_file: Set's the SourceFile name and path to the current file. Note that this looses the link to the primary MS run the file originated from
        :param compute_hash: If source files are rewritten, this flag triggers a recomputation of hash values. A SHA1 string gets stored in the checksum member of SourceFile
        :return: true if the file could be loaded, false otherwise
        :raises:
          Exception: FileNotFound is thrown if the file could not be opened
        :raises:
          Exception: ParseError is thrown if an error occurs during parsing
        """
        ...
    
    def storeExperiment(self, in_0: Union[bytes, str, String] , in_1: MSExperiment ) -> None:
        """
        Cython signature: void storeExperiment(String, MSExperiment)
        Stores an MSExperiment to a file\n
        
        The file type to store the data in is determined by the file name. Supported formats for storing are mzML, mzXML, mzData and DTA2D. If the file format cannot be determined from the file name, the mzML format is used
        
        
        :param filename: The name of the file to store the data in
        :param exp: The experiment to store
        :param log: Progress logging mode
        :raises:
          Exception: UnableToCreateFile is thrown if the file could not be written
        """
        ...
    
    def loadFeatures(self, in_0: Union[bytes, str, String] , in_1: FeatureMap ) -> None:
        """
        Cython signature: void loadFeatures(String, FeatureMap &)
        Loads a file into a FeatureMap
        
        
        :param filename: The file name of the file to load
        :param map: The FeatureMap to load the data into
        :param force_type: Forces to load the file with that file type. If no type is forced, it is determined from the extension (or from the content if that fails)
        :return: true if the file could be loaded, false otherwise
        :raises:
          Exception: FileNotFound is thrown if the file could not be opened
        :raises:
          Exception: ParseError is thrown if an error occurs during parsing
        """
        ...
    
    def getOptions(self) -> PeakFileOptions:
        """
        Cython signature: PeakFileOptions getOptions()
        Access to the options for loading/storing
        """
        ...
    
    def setOptions(self, in_0: PeakFileOptions ) -> None:
        """
        Cython signature: void setOptions(PeakFileOptions)
        Sets options for loading/storing
        """
        ...
    
    computeFileHash: __static_FileHandler_computeFileHash
    
    getType: __static_FileHandler_getType
    
    getTypeByContent: __static_FileHandler_getTypeByContent
    
    getTypeByFileName: __static_FileHandler_getTypeByFileName
    
    hasValidExtension: __static_FileHandler_hasValidExtension
    
    isSupported: __static_FileHandler_isSupported
    
    stripExtension: __static_FileHandler_stripExtension
    
    swapExtension: __static_FileHandler_swapExtension 


class GaussFitResult:
    """
    Cython implementation of _GaussFitResult

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS::Math_1_1GaussFitResult.html>`_
    """
    
    A: float
    
    x0: float
    
    sigma: float
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void GaussFitResult()
        """
        ...
    
    @overload
    def __init__(self, in_0: float , in_1: float , in_2: float ) -> None:
        """
        Cython signature: void GaussFitResult(double, double, double)
        """
        ...
    
    @overload
    def __init__(self, in_0: GaussFitResult ) -> None:
        """
        Cython signature: void GaussFitResult(GaussFitResult &)
        """
        ...
    
    def eval(self, in_0: float ) -> float:
        """
        Cython signature: double eval(double)
        """
        ... 


class GaussFitter:
    """
    Cython implementation of _GaussFitter

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS::Math_1_1GaussFitter.html>`_
    """
    
    def __init__(self) -> None:
        """
        Cython signature: void GaussFitter()
        Implements a fitter for Gaussian functions
        """
        ...
    
    def setInitialParameters(self, result: GaussFitResult ) -> None:
        """
        Cython signature: void setInitialParameters(GaussFitResult & result)
        Sets the initial parameters used by the fit method as initial guess for the Gaussian
        """
        ...
    
    def fit(self, points: '_np.ndarray[Any, _np.dtype[_np.float32]]' ) -> GaussFitResult:
        """
        Cython signature: GaussFitResult fit(libcpp_vector[DPosition2] points)
        Fits a Gaussian distribution to the given data points
        """
        ... 


class GaussTraceFitter:
    """
    Cython implementation of _GaussTraceFitter

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1GaussTraceFitter.html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void GaussTraceFitter()
        Fitter for RT profiles using a Gaussian background model
        """
        ...
    
    @overload
    def __init__(self, in_0: GaussTraceFitter ) -> None:
        """
        Cython signature: void GaussTraceFitter(GaussTraceFitter &)
        """
        ...
    
    def fit(self, traces: MassTraces ) -> None:
        """
        Cython signature: void fit(MassTraces & traces)
        Override important methods
        """
        ...
    
    def getLowerRTBound(self) -> float:
        """
        Cython signature: double getLowerRTBound()
        Returns the lower RT bound
        """
        ...
    
    def getUpperRTBound(self) -> float:
        """
        Cython signature: double getUpperRTBound()
        Returns the upper RT bound
        """
        ...
    
    def getHeight(self) -> float:
        """
        Cython signature: double getHeight()
        Returns height of the fitted gaussian model
        """
        ...
    
    def getCenter(self) -> float:
        """
        Cython signature: double getCenter()
        Returns center of the fitted gaussian model
        """
        ...
    
    def getFWHM(self) -> float:
        """
        Cython signature: double getFWHM()
        Returns FWHM of the fitted gaussian model
        """
        ...
    
    def getSigma(self) -> float:
        """
        Cython signature: double getSigma()
        Returns Sigma of the fitted gaussian model
        """
        ...
    
    def checkMaximalRTSpan(self, max_rt_span: float ) -> bool:
        """
        Cython signature: bool checkMaximalRTSpan(double max_rt_span)
        """
        ...
    
    def checkMinimalRTSpan(self, rt_bounds: List[float, float] , min_rt_span: float ) -> bool:
        """
        Cython signature: bool checkMinimalRTSpan(libcpp_pair[double,double] & rt_bounds, double min_rt_span)
        """
        ...
    
    def computeTheoretical(self, trace: MassTrace , k: int ) -> float:
        """
        Cython signature: double computeTheoretical(MassTrace & trace, size_t k)
        """
        ...
    
    def getArea(self) -> float:
        """
        Cython signature: double getArea()
        Returns area of the fitted gaussian model
        """
        ...
    
    def getGnuplotFormula(self, trace: MassTrace , function_name: bytes , baseline: float , rt_shift: float ) -> Union[bytes, str, String]:
        """
        Cython signature: String getGnuplotFormula(MassTrace & trace, char function_name, double baseline, double rt_shift)
        """
        ...
    
    def getValue(self, rt: float ) -> float:
        """
        Cython signature: double getValue(double rt)
        Returns value of the fitted gaussian model
        """
        ... 


class Gradient:
    """
    Cython implementation of _Gradient

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1Gradient.html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void Gradient()
        Representation of a HPLC gradient
        """
        ...
    
    @overload
    def __init__(self, in_0: Gradient ) -> None:
        """
        Cython signature: void Gradient(Gradient &)
        """
        ...
    
    def addEluent(self, eluent: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void addEluent(String eluent)
        Adds an eluent at the end of the eluent array
        """
        ...
    
    def clearEluents(self) -> None:
        """
        Cython signature: void clearEluents()
        Removes all eluents
        """
        ...
    
    def getEluents(self) -> List[bytes]:
        """
        Cython signature: libcpp_vector[String] getEluents()
        Returns a reference to the list of eluents
        """
        ...
    
    def addTimepoint(self, timepoint: int ) -> None:
        """
        Cython signature: void addTimepoint(int timepoint)
        Adds a timepoint at the end of the timepoint array
        """
        ...
    
    def clearTimepoints(self) -> None:
        """
        Cython signature: void clearTimepoints()
        Removes all timepoints
        """
        ...
    
    def getTimepoints(self) -> List[int]:
        """
        Cython signature: libcpp_vector[int] getTimepoints()
        Returns a reference to the list of timepoints
        """
        ...
    
    def setPercentage(self, eluent: Union[bytes, str, String] , timepoint: int , percentage: int ) -> None:
        """
        Cython signature: void setPercentage(String eluent, int timepoint, unsigned int percentage)
        Sets the percentage of 'eluent' at 'timepoint'
        """
        ...
    
    def getPercentage(self, eluent: Union[bytes, str, String] , timepoint: int ) -> int:
        """
        Cython signature: unsigned int getPercentage(String eluent, int timepoint)
        Returns a const reference to the percentages
        """
        ...
    
    def clearPercentages(self) -> None:
        """
        Cython signature: void clearPercentages()
        Sets all percentage values to 0
        """
        ...
    
    def isValid(self) -> bool:
        """
        Cython signature: bool isValid()
        Checks if the percentages of all timepoints add up to 100%
        """
        ... 


class ILPDCWrapper:
    """
    Cython implementation of _ILPDCWrapper

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1ILPDCWrapper.html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void ILPDCWrapper()
        """
        ...
    
    @overload
    def __init__(self, in_0: ILPDCWrapper ) -> None:
        """
        Cython signature: void ILPDCWrapper(ILPDCWrapper &)
        """
        ...
    
    def compute(self, fm: FeatureMap , pairs: List[ChargePair] , verbose_level: int ) -> float:
        """
        Cython signature: double compute(FeatureMap fm, libcpp_vector[ChargePair] & pairs, size_t verbose_level)
        Compute optimal solution and return value of objective function. If the input feature map is empty, a warning is issued and -1 is returned
        """
        ... 


class IMSIsotopeDistribution:
    """
    Cython implementation of _IMSIsotopeDistribution

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS::ims::IMSIsotopeDistribution_1_1IMSIsotopeDistribution.html>`_

    Represents a distribution of isotopes restricted to the first K elements
    
    Represents a distribution of isotopes of chemical elements as a list
    of peaks each as a pair of mass and abundance. 'IsotopeDistribution'
    unlike 'IsotopeSpecies' has one abundance per a nominal mass.
    Here is an example in the format (mass; abundance %)
    for molecule H2O (values are taken randomly):
    
    - IsotopeDistribution
        (18.00221; 99.03 %)
        (19.00334; 0.8 %)
        (20.00476; 0.17 %)
    
    - IsotopeSpecies
        (18.00197; 98.012 %)
        (18.00989; 1.018 %)
        (19.00312; 0.683 %)
        (19.00531; 0.117 %)
        (20.00413; 0.134 %)
        (20.00831; 0.036 %)
    
    To the sake of faster computations distribution is restricted
    to the first K elements, where K can be set by adjusting size
    'SIZE' of distribution. @note For the elements most abundant in
    living beings (CHNOPS) this restriction is negligible, since abundances
    decrease dramatically in isotopes order and are usually of no interest
    starting from +10 isotope.
    
    'IsotopeDistribution' implements folding with other distribution using an
    algorithm described in details in paper:
    Boecker et al. "Decomposing metabolic isotope patterns" WABI 2006. doi: 10.1007/11851561_2
    
    Folding with itself is done using Russian Multiplication Scheme
    """
    
    ABUNDANCES_SUM_ERROR: float
    
    SIZE: int
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void IMSIsotopeDistribution()
        """
        ...
    
    @overload
    def __init__(self, in_0: IMSIsotopeDistribution ) -> None:
        """
        Cython signature: void IMSIsotopeDistribution(IMSIsotopeDistribution &)
        """
        ...
    
    @overload
    def __init__(self, nominalMass: int ) -> None:
        """
        Cython signature: void IMSIsotopeDistribution(unsigned int nominalMass)
        """
        ...
    
    @overload
    def __init__(self, mass: float ) -> None:
        """
        Cython signature: void IMSIsotopeDistribution(double mass)
        """
        ...
    
    @overload
    def __init__(self, peaks: List[IMSIsotopeDistribution_Peak] , nominalMass: int ) -> None:
        """
        Cython signature: void IMSIsotopeDistribution(libcpp_vector[IMSIsotopeDistribution_Peak] & peaks, unsigned int nominalMass)
        """
        ...
    
    def size(self) -> int:
        """
        Cython signature: int size()
        """
        ...
    
    def getMass(self, i: int ) -> float:
        """
        Cython signature: double getMass(int i)
        """
        ...
    
    def getAbundance(self, i: int ) -> float:
        """
        Cython signature: double getAbundance(int i)
        """
        ...
    
    def getAverageMass(self) -> float:
        """
        Cython signature: double getAverageMass()
        """
        ...
    
    def getNominalMass(self) -> int:
        """
        Cython signature: unsigned int getNominalMass()
        """
        ...
    
    def setNominalMass(self, nominalMass: int ) -> None:
        """
        Cython signature: void setNominalMass(unsigned int nominalMass)
        """
        ...
    
    def getMasses(self) -> List[float]:
        """
        Cython signature: libcpp_vector[double] getMasses()
        Gets a mass of isotope 'i'
        """
        ...
    
    def getAbundances(self) -> List[float]:
        """
        Cython signature: libcpp_vector[double] getAbundances()
        Gets an abundance of isotope 'i'
        """
        ...
    
    def normalize(self) -> None:
        """
        Cython signature: void normalize()
        Normalizes distribution, i.e. scaling abundances to be summed up to 1 with an error
        """
        ...
    
    def empty(self) -> bool:
        """
        Cython signature: bool empty()
        Returns true if the distribution has no peaks, false - otherwise
        """
        ...
    
    def __richcmp__(self, other: IMSIsotopeDistribution, op: int) -> Any:
        ... 


class IMSIsotopeDistribution_Peak:
    """
    Cython implementation of _IMSIsotopeDistribution_Peak

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS::ims::IMSIsotopeDistribution_1_1IMSIsotopeDistribution_Peak.html>`_
    """
    
    mass: float
    
    abundance: float
    
    def __init__(self, mass: float , abundance: float ) -> None:
        """
        Cython signature: void IMSIsotopeDistribution_Peak(double mass, double abundance)
        """
        ...
    
    def __richcmp__(self, other: IMSIsotopeDistribution_Peak, op: int) -> Any:
        ... 


class IonSource:
    """
    Cython implementation of _IonSource

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1IonSource.html>`_
      -- Inherits from ['MetaInfoInterface']
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void IonSource()
        Description of an ion source (part of a MS Instrument)
        """
        ...
    
    @overload
    def __init__(self, in_0: IonSource ) -> None:
        """
        Cython signature: void IonSource(IonSource &)
        """
        ...
    
    def getPolarity(self) -> int:
        """
        Cython signature: Polarity getPolarity()
        Returns the ionization mode
        """
        ...
    
    def setPolarity(self, polarity: int ) -> None:
        """
        Cython signature: void setPolarity(Polarity polarity)
        Sets the ionization mode
        """
        ...
    
    def getInletType(self) -> int:
        """
        Cython signature: InletType getInletType()
        Returns the inlet type
        """
        ...
    
    def setInletType(self, inlet_type: int ) -> None:
        """
        Cython signature: void setInletType(InletType inlet_type)
        Sets the inlet type
        """
        ...
    
    def getIonizationMethod(self) -> int:
        """
        Cython signature: IonizationMethod getIonizationMethod()
        Returns the ionization method
        """
        ...
    
    def setIonizationMethod(self, ionization_type: int ) -> None:
        """
        Cython signature: void setIonizationMethod(IonizationMethod ionization_type)
        Sets the ionization method
        """
        ...
    
    def getOrder(self) -> int:
        """
        Cython signature: int getOrder()
        Returns the position of this part in the whole Instrument
        
        Order can be ignored, as long the instrument has this default setup:
          - one ion source
          - one or many mass analyzers
          - one ion detector
        
        For more complex instruments, the order should be defined.
        """
        ...
    
    def setOrder(self, order: int ) -> None:
        """
        Cython signature: void setOrder(int order)
        Sets the order
        """
        ...
    
    @staticmethod
    def getAllNamesOfInletType() -> List[bytes]:
        """
        Cython signature: libcpp_vector[String] getAllNamesOfInletType()
        Returns all inlet type names known to OpenMS
        """
        ...
    
    @staticmethod
    def getAllNamesOfIonizationMethod() -> List[bytes]:
        """
        Cython signature: libcpp_vector[String] getAllNamesOfIonizationMethod()
        Returns all ionization method names known to OpenMS
        """
        ...
    
    @staticmethod
    def getAllNamesOfPolarity() -> List[bytes]:
        """
        Cython signature: libcpp_vector[String] getAllNamesOfPolarity()
        Returns all polarity names known to OpenMS
        """
        ...
    
    def isMetaEmpty(self) -> bool:
        """
        Cython signature: bool isMetaEmpty()
        Returns if the MetaInfo is empty
        """
        ...
    
    def clearMetaInfo(self) -> None:
        """
        Cython signature: void clearMetaInfo()
        Removes all meta values
        """
        ...
    
    def metaRegistry(self) -> MetaInfoRegistry:
        """
        Cython signature: MetaInfoRegistry metaRegistry()
        Returns a reference to the MetaInfoRegistry
        """
        ...
    
    def getKeys(self, keys: List[bytes] ) -> None:
        """
        Cython signature: void getKeys(libcpp_vector[String] & keys)
        Fills the given vector with a list of all keys for which a value is set
        """
        ...
    
    def getMetaValue(self, in_0: Union[bytes, str, String] ) -> Union[int, float, bytes, str, List[int], List[float], List[bytes]]:
        """
        Cython signature: DataValue getMetaValue(String)
        Returns the value corresponding to a string, or
        """
        ...
    
    def setMetaValue(self, in_0: Union[bytes, str, String] , in_1: Union[int, float, bytes, str, List[int], List[float], List[bytes]] ) -> None:
        """
        Cython signature: void setMetaValue(String, DataValue)
        Sets the DataValue corresponding to a name
        """
        ...
    
    def metaValueExists(self, in_0: Union[bytes, str, String] ) -> bool:
        """
        Cython signature: bool metaValueExists(String)
        Returns whether an entry with the given name exists
        """
        ...
    
    def removeMetaValue(self, in_0: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void removeMetaValue(String)
        Removes the DataValue corresponding to `name` if it exists
        """
        ...
    
    def __richcmp__(self, other: IonSource, op: int) -> Any:
        ...
    InletType : __InletType
    IonizationMethod : __IonizationMethod
    Polarity : __Polarity 


class ItraqConstants:
    """
    Cython implementation of _ItraqConstants

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1ItraqConstants.html>`_

    Some constants used throughout iTRAQ classes
    
    Constants for iTRAQ experiments and a ChannelInfo structure to store information about a single channel
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void ItraqConstants()
        """
        ...
    
    @overload
    def __init__(self, in_0: ItraqConstants ) -> None:
        """
        Cython signature: void ItraqConstants(ItraqConstants &)
        """
        ...
    
    def getIsotopeMatrixAsStringList(self, itraq_type: int , isotope_corrections: List[MatrixDouble] ) -> List[bytes]:
        """
        Cython signature: StringList getIsotopeMatrixAsStringList(int itraq_type, libcpp_vector[MatrixDouble] & isotope_corrections)
        Convert isotope correction matrix to stringlist\n
        
        Each line is converted into a string of the format channel:-2Da/-1Da/+1Da/+2Da ; e.g. '114:0/0.3/4/0'
        Useful for creating parameters or debug output
        
        
        :param itraq_type: Which matrix to stringify. Should be of values from enum ITRAQ_TYPES
        :param isotope_corrections: Vector of the two matrices (4plex, 8plex)
        """
        ...
    
    def updateIsotopeMatrixFromStringList(self, itraq_type: int , channels: List[bytes] , isotope_corrections: List[MatrixDouble] ) -> None:
        """
        Cython signature: void updateIsotopeMatrixFromStringList(int itraq_type, StringList & channels, libcpp_vector[MatrixDouble] & isotope_corrections)
        Convert strings to isotope correction matrix rows\n
        
        Each string of format channel:-2Da/-1Da/+1Da/+2Da ; e.g. '114:0/0.3/4/0'
        is parsed and the corresponding channel(row) in the matrix is updated
        Not all channels need to be present, missing channels will be left untouched
        Useful to update the matrix with user isotope correction values
        
        
        :param itraq_type: Which matrix to stringify. Should be of values from enum ITRAQ_TYPES
        :param channels: New channel isotope values as strings
        :param isotope_corrections: Vector of the two matrices (4plex, 8plex)
        """
        ...
    
    def translateIsotopeMatrix(self, itraq_type: int , isotope_corrections: List[MatrixDouble] ) -> MatrixDouble:
        """
        Cython signature: MatrixDouble translateIsotopeMatrix(int & itraq_type, libcpp_vector[MatrixDouble] & isotope_corrections)
        """
        ... 


class JavaInfo:
    """
    Cython implementation of _JavaInfo

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1JavaInfo.html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void JavaInfo()
        Detect Java and retrieve information
        """
        ...
    
    @overload
    def __init__(self, in_0: JavaInfo ) -> None:
        """
        Cython signature: void JavaInfo(JavaInfo &)
        """
        ...
    
    def canRun(self, java_executable: Union[bytes, str, String] ) -> bool:
        """
        Cython signature: bool canRun(String java_executable)
        Determine if Java is installed and reachable\n
        
        The call fails if either Java is not installed or if a relative location is given and Java is not on the search PATH
        
        
        :param java_executable: Path to Java executable. Can be absolute, relative or just a filename
        :return: Returns false if Java executable can not be called; true if Java executable can be executed
        """
        ... 


class LabeledPairFinder:
    """
    Cython implementation of _LabeledPairFinder

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1LabeledPairFinder.html>`_
      -- Inherits from ['BaseGroupFinder']

    The LabeledPairFinder allows the matching of labeled features (features with a fixed distance)
    
    Finds feature pairs that have a defined distance in RT and m/z in the same map
    """
    
    def __init__(self) -> None:
        """
        Cython signature: void LabeledPairFinder()
        """
        ...
    
    def run(self, input_maps: List[ConsensusMap] , result_map: ConsensusMap ) -> None:
        """
        Cython signature: void run(libcpp_vector[ConsensusMap] & input_maps, ConsensusMap & result_map)
        Runs the LabeledPairFinder algorithm
        """
        ...
    
    def getSubsections(self) -> List[bytes]:
        """
        Cython signature: libcpp_vector[String] getSubsections()
        """
        ...
    
    def setParameters(self, param: Param ) -> None:
        """
        Cython signature: void setParameters(Param & param)
        Sets the parameters
        """
        ...
    
    def getParameters(self) -> Param:
        """
        Cython signature: Param getParameters()
        Returns the parameters
        """
        ...
    
    def getDefaults(self) -> Param:
        """
        Cython signature: Param getDefaults()
        Returns the default parameters
        """
        ...
    
    def getName(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getName()
        Returns the name
        """
        ...
    
    def setName(self, in_0: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setName(const String &)
        Sets the name
        """
        ...
    
    def setLogType(self, in_0: int ) -> None:
        """
        Cython signature: void setLogType(LogType)
        Sets the progress log that should be used. The default type is NONE!
        """
        ...
    
    def getLogType(self) -> int:
        """
        Cython signature: LogType getLogType()
        Returns the type of progress log being used
        """
        ...
    
    def startProgress(self, begin: int , end: int , label: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void startProgress(ptrdiff_t begin, ptrdiff_t end, String label)
        """
        ...
    
    def setProgress(self, value: int ) -> None:
        """
        Cython signature: void setProgress(ptrdiff_t value)
        Sets the current progress
        """
        ...
    
    def endProgress(self) -> None:
        """
        Cython signature: void endProgress()
        Ends the progress display
        """
        ...
    
    def nextProgress(self) -> None:
        """
        Cython signature: void nextProgress()
        Increment progress by 1 (according to range begin-end)
        """
        ... 


class LightCompound:
    """
    Cython implementation of _LightCompound

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenSwath_1_1LightCompound.html>`_
    """
    
    rt: float
    
    drift_time: float
    
    charge: int
    
    sequence: bytes
    
    protein_refs: List[bytes]
    
    peptide_group_label: bytes
    
    id: bytes
    
    sum_formula: bytes
    
    compound_name: bytes
    
    modifications: List[LightModification]
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void LightCompound()
        """
        ...
    
    @overload
    def __init__(self, in_0: LightCompound ) -> None:
        """
        Cython signature: void LightCompound(LightCompound &)
        """
        ...
    
    def setDriftTime(self, d: float ) -> None:
        """
        Cython signature: void setDriftTime(double d)
        """
        ...
    
    def getDriftTime(self) -> float:
        """
        Cython signature: double getDriftTime()
        """
        ...
    
    def getChargeState(self) -> int:
        """
        Cython signature: int getChargeState()
        """
        ...
    
    def isPeptide(self) -> bool:
        """
        Cython signature: bool isPeptide()
        """
        ...
    
    def setChargeState(self, ch: int ) -> None:
        """
        Cython signature: void setChargeState(int ch)
        """
        ... 


class LightModification:
    """
    Cython implementation of _LightModification

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenSwath_1_1LightModification.html>`_
    """
    
    location: int
    
    unimod_id: int
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void LightModification()
        """
        ...
    
    @overload
    def __init__(self, in_0: LightModification ) -> None:
        """
        Cython signature: void LightModification(LightModification &)
        """
        ... 


class LightProtein:
    """
    Cython implementation of _LightProtein

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenSwath_1_1LightProtein.html>`_
    """
    
    id: bytes
    
    sequence: bytes
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void LightProtein()
        """
        ...
    
    @overload
    def __init__(self, in_0: LightProtein ) -> None:
        """
        Cython signature: void LightProtein(LightProtein &)
        """
        ... 


class LightTargetedExperiment:
    """
    Cython implementation of _LightTargetedExperiment

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenSwath_1_1LightTargetedExperiment.html>`_
    """
    
    transitions: List[LightTransition]
    
    compounds: List[LightCompound]
    
    proteins: List[LightProtein]
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void LightTargetedExperiment()
        """
        ...
    
    @overload
    def __init__(self, in_0: LightTargetedExperiment ) -> None:
        """
        Cython signature: void LightTargetedExperiment(LightTargetedExperiment &)
        """
        ...
    
    def getTransitions(self) -> List[LightTransition]:
        """
        Cython signature: libcpp_vector[LightTransition] getTransitions()
        """
        ...
    
    def getCompounds(self) -> List[LightCompound]:
        """
        Cython signature: libcpp_vector[LightCompound] getCompounds()
        """
        ...
    
    def getProteins(self) -> List[LightProtein]:
        """
        Cython signature: libcpp_vector[LightProtein] getProteins()
        """
        ...
    
    def getCompoundByRef(self, ref: bytes ) -> LightCompound:
        """
        Cython signature: LightCompound getCompoundByRef(libcpp_string & ref)
        """
        ...
    
    def getPeptideByRef(self, ref: bytes ) -> LightCompound:
        """
        Cython signature: LightCompound getPeptideByRef(libcpp_string & ref)
        """
        ... 


class LightTransition:
    """
    Cython implementation of _LightTransition

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenSwath_1_1LightTransition.html>`_
    """
    
    transition_name: bytes
    
    peptide_ref: bytes
    
    library_intensity: float
    
    product_mz: float
    
    precursor_mz: float
    
    fragment_charge: int
    
    decoy: bool
    
    detecting_transition: bool
    
    quantifying_transition: bool
    
    identifying_transition: bool
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void LightTransition()
        """
        ...
    
    @overload
    def __init__(self, in_0: LightTransition ) -> None:
        """
        Cython signature: void LightTransition(LightTransition &)
        """
        ...
    
    def getProductChargeState(self) -> int:
        """
        Cython signature: int getProductChargeState()
        """
        ...
    
    def isProductChargeStateSet(self) -> bool:
        """
        Cython signature: bool isProductChargeStateSet()
        """
        ...
    
    def getNativeID(self) -> bytes:
        """
        Cython signature: libcpp_string getNativeID()
        """
        ...
    
    def getPeptideRef(self) -> bytes:
        """
        Cython signature: libcpp_string getPeptideRef()
        """
        ...
    
    def getLibraryIntensity(self) -> float:
        """
        Cython signature: double getLibraryIntensity()
        """
        ...
    
    def setLibraryIntensity(self, l: float ) -> None:
        """
        Cython signature: void setLibraryIntensity(double l)
        """
        ...
    
    def getProductMZ(self) -> float:
        """
        Cython signature: double getProductMZ()
        """
        ...
    
    def getPrecursorMZ(self) -> float:
        """
        Cython signature: double getPrecursorMZ()
        """
        ...
    
    def getCompoundRef(self) -> bytes:
        """
        Cython signature: libcpp_string getCompoundRef()
        """
        ...
    
    def setDetectingTransition(self, d: bool ) -> None:
        """
        Cython signature: void setDetectingTransition(bool d)
        """
        ...
    
    def isDetectingTransition(self) -> bool:
        """
        Cython signature: bool isDetectingTransition()
        """
        ...
    
    def setQuantifyingTransition(self, q: bool ) -> None:
        """
        Cython signature: void setQuantifyingTransition(bool q)
        """
        ...
    
    def isQuantifyingTransition(self) -> bool:
        """
        Cython signature: bool isQuantifyingTransition()
        """
        ...
    
    def setIdentifyingTransition(self, i: bool ) -> None:
        """
        Cython signature: void setIdentifyingTransition(bool i)
        """
        ...
    
    def isIdentifyingTransition(self) -> bool:
        """
        Cython signature: bool isIdentifyingTransition()
        """
        ... 


class MRMAssay:
    """
    Cython implementation of _MRMAssay

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1MRMAssay.html>`_
      -- Inherits from ['ProgressLogger']
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void MRMAssay()
        """
        ...
    
    @overload
    def __init__(self, in_0: MRMAssay ) -> None:
        """
        Cython signature: void MRMAssay(MRMAssay &)
        """
        ...
    
    def reannotateTransitions(self, exp: TargetedExperiment , precursor_mz_threshold: float , product_mz_threshold: float , fragment_types: List[bytes] , fragment_charges: List[int] , enable_specific_losses: bool , enable_unspecific_losses: bool , round_decPow: int ) -> None:
        """
        Cython signature: void reannotateTransitions(TargetedExperiment & exp, double precursor_mz_threshold, double product_mz_threshold, libcpp_vector[String] fragment_types, libcpp_vector[size_t] fragment_charges, bool enable_specific_losses, bool enable_unspecific_losses, int round_decPow)
        Annotates and filters transitions in a TargetedExperiment
        
        
        :param exp: The input, unfiltered transitions
        :param precursor_mz_threshold: The precursor m/z threshold in Th for annotation
        :param product_mz_threshold: The product m/z threshold in Th for annotation
        :param fragment_types: The fragment types to consider for annotation
        :param fragment_charges: The fragment charges to consider for annotation
        :param enable_specific_losses: Whether specific neutral losses should be considered
        :param enable_unspecific_losses: Whether unspecific neutral losses (H2O1, H3N1, C1H2N2, C1H2N1O1) should be considered
        :param round_decPow: Round product m/z values to decimal power (default: -4)
        """
        ...
    
    def restrictTransitions(self, exp: TargetedExperiment , lower_mz_limit: float , upper_mz_limit: float , swathes: List[List[float, float]] ) -> None:
        """
        Cython signature: void restrictTransitions(TargetedExperiment & exp, double lower_mz_limit, double upper_mz_limit, libcpp_vector[libcpp_pair[double,double]] swathes)
        Restrict and filter transitions in a TargetedExperiment
        
        
        :param exp: The input, unfiltered transitions
        :param lower_mz_limit: The lower product m/z limit in Th
        :param upper_mz_limit: The upper product m/z limit in Th
        :param swathes: The swath window settings (to exclude fragment ions falling into the precursor isolation window)
        """
        ...
    
    def detectingTransitions(self, exp: TargetedExperiment , min_transitions: int , max_transitions: int ) -> None:
        """
        Cython signature: void detectingTransitions(TargetedExperiment & exp, int min_transitions, int max_transitions)
        Select detecting fragment ions
        
        
        :param exp: The input, unfiltered transitions
        :param min_transitions: The minimum number of transitions required per assay
        :param max_transitions: The maximum number of transitions required per assay
        """
        ...
    
    def filterMinMaxTransitionsCompound(self, exp: TargetedExperiment , min_transitions: int , max_transitions: int ) -> None:
        """
        Cython signature: void filterMinMaxTransitionsCompound(TargetedExperiment & exp, int min_transitions, int max_transitions)
        Filters target and decoy transitions by intensity, only keeping the top N transitions
        
        
        :param exp: The transition list which will be filtered
        :param min_transitions: The minimum number of transitions required per assay (targets only)
        :param max_transitions: The maximum number of transitions allowed per assay
        """
        ...
    
    def filterUnreferencedDecoysCompound(self, exp: TargetedExperiment ) -> None:
        """
        Cython signature: void filterUnreferencedDecoysCompound(TargetedExperiment & exp)
        Filters decoy transitions, which do not have respective target transition
        based on the transitionID.
        
        References between targets and decoys will be constructed based on the transitionsID
        and the "_decoy_" string. For example:
        
        target: 84_CompoundName_[M+H]+_88_22
        decoy: 84_CompoundName_decoy_[M+H]+_88_22
        
        
        :param exp: The transition list which will be filtered
        """
        ...
    
    def uisTransitions(self, exp: TargetedExperiment , fragment_types: List[bytes] , fragment_charges: List[int] , enable_specific_losses: bool , enable_unspecific_losses: bool , enable_ms2_precursors: bool , mz_threshold: float , swathes: List[List[float, float]] , round_decPow: int , max_num_alternative_localizations: int , shuffle_seed: int ) -> None:
        """
        Cython signature: void uisTransitions(TargetedExperiment & exp, libcpp_vector[String] fragment_types, libcpp_vector[size_t] fragment_charges, bool enable_specific_losses, bool enable_unspecific_losses, bool enable_ms2_precursors, double mz_threshold, libcpp_vector[libcpp_pair[double,double]] swathes, int round_decPow, size_t max_num_alternative_localizations, int shuffle_seed)
        Annotate UIS / site-specific transitions
        
        Performs the following actions:
        
        - Step 1: For each peptide, compute all theoretical alternative peptidoforms; see transitions generateTargetInSilicoMap_()
        - Step 2: Generate target identification transitions; see generateTargetAssays_()
        
        - Step 3a: Generate decoy sequences that share peptidoform properties with targets; see generateDecoySequences_()
        - Step 3b: Generate decoy in silico peptide map containing theoretical transition; see generateDecoyInSilicoMap_()
        - Step 4: Generate decoy identification transitions; see generateDecoyAssays_()
        
        The IPF algorithm uses the concept of "identification transitions" that
        are used to discriminate different peptidoforms, these are generated in
        this function.  In brief, the algorithm takes the existing set of
        peptides and transitions and then appends these "identification
        transitions" for targets and decoys. The novel transitions are set to be
        non-detecting and non-quantifying and are annotated with the set of
        peptidoforms to which they map.
        
        
        :param exp: The input, unfiltered transitions
        :param fragment_types: The fragment types to consider for annotation
        :param fragment_charges: The fragment charges to consider for annotation
        :param enable_specific_losses: Whether specific neutral losses should be considered
        :param enable_unspecific_losses: Whether unspecific neutral losses (H2O1, H3N1, C1H2N2, C1H2N1O1) should be considered
        :param enable_ms2_precursors: Whether MS2 precursors should be considered
        :param mz_threshold: The product m/z threshold in Th for annotation
        :param swathes: The swath window settings (to exclude fragment ions falling
        :param round_decPow: Round product m/z values to decimal power (default: -4)
        :param max_num_alternative_localizations: Maximum number of allowed peptide sequence permutations
        :param shuffle_seed: Set seed for shuffle (-1: select seed based on time)
        :param disable_decoy_transitions: Whether to disable generation of decoy UIS transitions
        """
        ...
    
    def setLogType(self, in_0: int ) -> None:
        """
        Cython signature: void setLogType(LogType)
        Sets the progress log that should be used. The default type is NONE!
        """
        ...
    
    def getLogType(self) -> int:
        """
        Cython signature: LogType getLogType()
        Returns the type of progress log being used
        """
        ...
    
    def startProgress(self, begin: int , end: int , label: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void startProgress(ptrdiff_t begin, ptrdiff_t end, String label)
        """
        ...
    
    def setProgress(self, value: int ) -> None:
        """
        Cython signature: void setProgress(ptrdiff_t value)
        Sets the current progress
        """
        ...
    
    def endProgress(self) -> None:
        """
        Cython signature: void endProgress()
        Ends the progress display
        """
        ...
    
    def nextProgress(self) -> None:
        """
        Cython signature: void nextProgress()
        Increment progress by 1 (according to range begin-end)
        """
        ... 


class MRMMapping:
    """
    Cython implementation of _MRMMapping

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1MRMMapping.html>`_
      -- Inherits from ['DefaultParamHandler']
    """
    
    def __init__(self) -> None:
        """
        Cython signature: void MRMMapping()
        """
        ...
    
    def mapExperiment(self, input_chromatograms: MSExperiment , targeted_exp: TargetedExperiment , output: MSExperiment ) -> None:
        """
        Cython signature: void mapExperiment(MSExperiment input_chromatograms, TargetedExperiment targeted_exp, MSExperiment & output)
        Maps input chromatograms to assays in a targeted experiment
        
        The output chromatograms are an annotated copy of the input chromatograms
        with native id, precursor information and peptide sequence (if available)
        annotated in the chromatogram files
        
        The algorithm tries to match a given set of chromatograms and targeted
        assays. It iterates through all the chromatograms retrieves one or more
        matching targeted assay for the chromatogram. By default, the algorithm
        assumes that a 1:1 mapping exists. If a chromatogram cannot be mapped
        (does not have a corresponding assay) the algorithm issues a warning, the
        user can specify that the program should abort in such a case (see
        error_on_unmapped)
        
        :note If multiple mapping is enabled (see map_multiple_assays parameter)
        then each mapped assay will get its own chromatogram that contains the
        same raw data but different meta-annotation. This *can* be useful if the
        same transition is used to monitor multiple analytes but may also
        indicate a problem with too wide mapping tolerances
        """
        ...
    
    def getSubsections(self) -> List[bytes]:
        """
        Cython signature: libcpp_vector[String] getSubsections()
        """
        ...
    
    def setParameters(self, param: Param ) -> None:
        """
        Cython signature: void setParameters(Param & param)
        Sets the parameters
        """
        ...
    
    def getParameters(self) -> Param:
        """
        Cython signature: Param getParameters()
        Returns the parameters
        """
        ...
    
    def getDefaults(self) -> Param:
        """
        Cython signature: Param getDefaults()
        Returns the default parameters
        """
        ...
    
    def getName(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getName()
        Returns the name
        """
        ...
    
    def setName(self, in_0: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setName(const String &)
        Sets the name
        """
        ... 


class MapAlignmentEvaluationAlgorithmPrecision:
    """
    Cython implementation of _MapAlignmentEvaluationAlgorithmPrecision

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1MapAlignmentEvaluationAlgorithmPrecision.html>`_
      -- Inherits from ['MapAlignmentEvaluationAlgorithm']
    """
    
    def __init__(self) -> None:
        """
        Cython signature: void MapAlignmentEvaluationAlgorithmPrecision()
        """
        ... 


class MassDecompositionAlgorithm:
    """
    Cython implementation of _MassDecompositionAlgorithm

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1MassDecompositionAlgorithm.html>`_
      -- Inherits from ['DefaultParamHandler']
    """
    
    def __init__(self) -> None:
        """
        Cython signature: void MassDecompositionAlgorithm()
        """
        ...
    
    def getDecompositions(self, decomps: List[MassDecomposition] , weight: float ) -> None:
        """
        Cython signature: void getDecompositions(libcpp_vector[MassDecomposition] & decomps, double weight)
        Returns the possible decompositions given the weight
        """
        ...
    
    def getSubsections(self) -> List[bytes]:
        """
        Cython signature: libcpp_vector[String] getSubsections()
        """
        ...
    
    def setParameters(self, param: Param ) -> None:
        """
        Cython signature: void setParameters(Param & param)
        Sets the parameters
        """
        ...
    
    def getParameters(self) -> Param:
        """
        Cython signature: Param getParameters()
        Returns the parameters
        """
        ...
    
    def getDefaults(self) -> Param:
        """
        Cython signature: Param getDefaults()
        Returns the default parameters
        """
        ...
    
    def getName(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getName()
        Returns the name
        """
        ...
    
    def setName(self, in_0: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setName(const String &)
        Sets the name
        """
        ... 


class MassTraceDetection:
    """
    Cython implementation of _MassTraceDetection

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1MassTraceDetection.html>`_
      -- Inherits from ['ProgressLogger', 'DefaultParamHandler']
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void MassTraceDetection()
        """
        ...
    
    @overload
    def __init__(self, in_0: MassTraceDetection ) -> None:
        """
        Cython signature: void MassTraceDetection(MassTraceDetection &)
        """
        ...
    
    def run(self, input_map: MSExperiment , traces: List[Kernel_MassTrace] , max_traces: int ) -> None:
        """
        Cython signature: void run(MSExperiment & input_map, libcpp_vector[Kernel_MassTrace] & traces, size_t max_traces)
        """
        ...
    
    def setLogType(self, in_0: int ) -> None:
        """
        Cython signature: void setLogType(LogType)
        Sets the progress log that should be used. The default type is NONE!
        """
        ...
    
    def getLogType(self) -> int:
        """
        Cython signature: LogType getLogType()
        Returns the type of progress log being used
        """
        ...
    
    def startProgress(self, begin: int , end: int , label: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void startProgress(ptrdiff_t begin, ptrdiff_t end, String label)
        """
        ...
    
    def setProgress(self, value: int ) -> None:
        """
        Cython signature: void setProgress(ptrdiff_t value)
        Sets the current progress
        """
        ...
    
    def endProgress(self) -> None:
        """
        Cython signature: void endProgress()
        Ends the progress display
        """
        ...
    
    def nextProgress(self) -> None:
        """
        Cython signature: void nextProgress()
        Increment progress by 1 (according to range begin-end)
        """
        ...
    
    def getSubsections(self) -> List[bytes]:
        """
        Cython signature: libcpp_vector[String] getSubsections()
        """
        ...
    
    def setParameters(self, param: Param ) -> None:
        """
        Cython signature: void setParameters(Param & param)
        Sets the parameters
        """
        ...
    
    def getParameters(self) -> Param:
        """
        Cython signature: Param getParameters()
        Returns the parameters
        """
        ...
    
    def getDefaults(self) -> Param:
        """
        Cython signature: Param getDefaults()
        Returns the default parameters
        """
        ...
    
    def getName(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getName()
        Returns the name
        """
        ...
    
    def setName(self, in_0: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setName(const String &)
        Sets the name
        """
        ... 


class MetaInfoInterface:
    """
    Cython implementation of _MetaInfoInterface

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1MetaInfoInterface.html>`_

    Interface for classes that can store arbitrary meta information
    (Type-Name-Value tuples).
    
    MetaInfoInterface is a base class for all classes that use one MetaInfo
    object as member.  If you want to add meta information to a class, let it
    publicly inherit the MetaInfoInterface.  Meta information is an array of
    Type-Name-Value tuples.
    
    Usage:
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void MetaInfoInterface()
        """
        ...
    
    @overload
    def __init__(self, in_0: MetaInfoInterface ) -> None:
        """
        Cython signature: void MetaInfoInterface(MetaInfoInterface &)
        """
        ...
    
    def isMetaEmpty(self) -> bool:
        """
        Cython signature: bool isMetaEmpty()
        Returns if the MetaInfo is empty
        """
        ...
    
    def clearMetaInfo(self) -> None:
        """
        Cython signature: void clearMetaInfo()
        Removes all meta values
        """
        ...
    
    def metaRegistry(self) -> MetaInfoRegistry:
        """
        Cython signature: MetaInfoRegistry metaRegistry()
        Returns a reference to the MetaInfoRegistry
        """
        ...
    
    def getKeys(self, keys: List[bytes] ) -> None:
        """
        Cython signature: void getKeys(libcpp_vector[String] & keys)
        Fills the given vector with a list of all keys for which a value is set
        """
        ...
    
    def getMetaValue(self, in_0: Union[bytes, str, String] ) -> Union[int, float, bytes, str, List[int], List[float], List[bytes]]:
        """
        Cython signature: DataValue getMetaValue(String)
        Returns the value corresponding to a string, or
        """
        ...
    
    def setMetaValue(self, in_0: Union[bytes, str, String] , in_1: Union[int, float, bytes, str, List[int], List[float], List[bytes]] ) -> None:
        """
        Cython signature: void setMetaValue(String, DataValue)
        Sets the DataValue corresponding to a name
        """
        ...
    
    def metaValueExists(self, in_0: Union[bytes, str, String] ) -> bool:
        """
        Cython signature: bool metaValueExists(String)
        Returns whether an entry with the given name exists
        """
        ...
    
    def removeMetaValue(self, in_0: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void removeMetaValue(String)
        Removes the DataValue corresponding to `name` if it exists
        """
        ...
    
    def __richcmp__(self, other: MetaInfoInterface, op: int) -> Any:
        ... 


class MetaboliteFeatureDeconvolution:
    """
    Cython implementation of _MetaboliteFeatureDeconvolution

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1MetaboliteFeatureDeconvolution.html>`_
      -- Inherits from ['DefaultParamHandler']

    An algorithm to decharge small molecule features (i.e. as found by FeatureFinder)
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void MetaboliteFeatureDeconvolution()
        """
        ...
    
    @overload
    def __init__(self, in_0: MetaboliteFeatureDeconvolution ) -> None:
        """
        Cython signature: void MetaboliteFeatureDeconvolution(MetaboliteFeatureDeconvolution &)
        """
        ...
    
    def compute(self, fm_in: FeatureMap , fm_out: FeatureMap , cons_map: ConsensusMap , cons_map_p: ConsensusMap ) -> None:
        """
        Cython signature: void compute(FeatureMap & fm_in, FeatureMap & fm_out, ConsensusMap & cons_map, ConsensusMap & cons_map_p)
        Compute a zero-charge feature map from a set of charged features
        
        Find putative ChargePairs, then score them and hand over to ILP
        
        
        :param fm_in: Input feature-map
        :param fm_out: Output feature-map (sorted by position and augmented with user params)
        :param cons_map: Output of grouped features belonging to a charge group
        :param cons_map_p: Output of paired features connected by an edge
        """
        ...
    
    def getSubsections(self) -> List[bytes]:
        """
        Cython signature: libcpp_vector[String] getSubsections()
        """
        ...
    
    def setParameters(self, param: Param ) -> None:
        """
        Cython signature: void setParameters(Param & param)
        Sets the parameters
        """
        ...
    
    def getParameters(self) -> Param:
        """
        Cython signature: Param getParameters()
        Returns the parameters
        """
        ...
    
    def getDefaults(self) -> Param:
        """
        Cython signature: Param getDefaults()
        Returns the default parameters
        """
        ...
    
    def getName(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getName()
        Returns the name
        """
        ...
    
    def setName(self, in_0: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setName(const String &)
        Sets the name
        """
        ...
    CHARGEMODE_MFD : __CHARGEMODE_MFD 


class MetaboliteSpectralMatching:
    """
    Cython implementation of _MetaboliteSpectralMatching

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1MetaboliteSpectralMatching.html>`_
      -- Inherits from ['ProgressLogger', 'DefaultParamHandler']
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void MetaboliteSpectralMatching()
        """
        ...
    
    @overload
    def __init__(self, in_0: MetaboliteSpectralMatching ) -> None:
        """
        Cython signature: void MetaboliteSpectralMatching(MetaboliteSpectralMatching &)
        """
        ...
    
    def run(self, exp: MSExperiment , speclib: MSExperiment , mz_tab: MzTab , out_spectra: String ) -> None:
        """
        Cython signature: void run(MSExperiment & exp, MSExperiment & speclib, MzTab & mz_tab, String & out_spectra)
        """
        ...
    
    def setLogType(self, in_0: int ) -> None:
        """
        Cython signature: void setLogType(LogType)
        Sets the progress log that should be used. The default type is NONE!
        """
        ...
    
    def getLogType(self) -> int:
        """
        Cython signature: LogType getLogType()
        Returns the type of progress log being used
        """
        ...
    
    def startProgress(self, begin: int , end: int , label: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void startProgress(ptrdiff_t begin, ptrdiff_t end, String label)
        """
        ...
    
    def setProgress(self, value: int ) -> None:
        """
        Cython signature: void setProgress(ptrdiff_t value)
        Sets the current progress
        """
        ...
    
    def endProgress(self) -> None:
        """
        Cython signature: void endProgress()
        Ends the progress display
        """
        ...
    
    def nextProgress(self) -> None:
        """
        Cython signature: void nextProgress()
        Increment progress by 1 (according to range begin-end)
        """
        ...
    
    def getSubsections(self) -> List[bytes]:
        """
        Cython signature: libcpp_vector[String] getSubsections()
        """
        ...
    
    def setParameters(self, param: Param ) -> None:
        """
        Cython signature: void setParameters(Param & param)
        Sets the parameters
        """
        ...
    
    def getParameters(self) -> Param:
        """
        Cython signature: Param getParameters()
        Returns the parameters
        """
        ...
    
    def getDefaults(self) -> Param:
        """
        Cython signature: Param getDefaults()
        Returns the default parameters
        """
        ...
    
    def getName(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getName()
        Returns the name
        """
        ...
    
    def setName(self, in_0: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setName(const String &)
        Sets the name
        """
        ...
    
    computeHyperScore: __static_MetaboliteSpectralMatching_computeHyperScore 


class ModificationDefinition:
    """
    Cython implementation of _ModificationDefinition

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1ModificationDefinition.html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void ModificationDefinition()
        """
        ...
    
    @overload
    def __init__(self, in_0: ModificationDefinition ) -> None:
        """
        Cython signature: void ModificationDefinition(ModificationDefinition &)
        """
        ...
    
    @overload
    def __init__(self, mod: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void ModificationDefinition(const String & mod)
        """
        ...
    
    @overload
    def __init__(self, mod: Union[bytes, str, String] , fixed: bool ) -> None:
        """
        Cython signature: void ModificationDefinition(const String & mod, bool fixed)
        """
        ...
    
    @overload
    def __init__(self, mod: Union[bytes, str, String] , fixed: bool , max_occur: int ) -> None:
        """
        Cython signature: void ModificationDefinition(const String & mod, bool fixed, unsigned int max_occur)
        """
        ...
    
    @overload
    def __init__(self, mod: ResidueModification ) -> None:
        """
        Cython signature: void ModificationDefinition(ResidueModification & mod)
        """
        ...
    
    @overload
    def __init__(self, mod: ResidueModification , fixed: bool ) -> None:
        """
        Cython signature: void ModificationDefinition(ResidueModification & mod, bool fixed)
        """
        ...
    
    @overload
    def __init__(self, mod: ResidueModification , fixed: bool , max_occur: int ) -> None:
        """
        Cython signature: void ModificationDefinition(ResidueModification & mod, bool fixed, unsigned int max_occur)
        """
        ...
    
    def setFixedModification(self, fixed: bool ) -> None:
        """
        Cython signature: void setFixedModification(bool fixed)
        Sets whether this modification definition is fixed or variable (modification must occur vs. can occur)
        """
        ...
    
    def isFixedModification(self) -> bool:
        """
        Cython signature: bool isFixedModification()
        Returns if the modification if fixed true, else false
        """
        ...
    
    def setMaxOccurrences(self, num: int ) -> None:
        """
        Cython signature: void setMaxOccurrences(unsigned int num)
        Sets the maximal number of occurrences per peptide (unbounded if 0)
        """
        ...
    
    def getMaxOccurrences(self) -> int:
        """
        Cython signature: unsigned int getMaxOccurrences()
        Returns the maximal number of occurrences per peptide
        """
        ...
    
    def getModificationName(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getModificationName()
        Returns the name of the modification
        """
        ...
    
    def setModification(self, modification: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setModification(const String & modification)
        Sets the modification, allowed are unique names provided by ModificationsDB
        """
        ...
    
    def getModification(self) -> ResidueModification:
        """
        Cython signature: ResidueModification getModification()
        """
        ...
    
    def __richcmp__(self, other: ModificationDefinition, op: int) -> Any:
        ... 


class MzQCFile:
    """
    Cython implementation of _MzQCFile

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1MzQCFile.html>`_

    File adapter for mzQC files used to load and store mzQC files
    
    This class collects the data for the mzQC File
    """
    
    def __init__(self) -> None:
        """
        Cython signature: void MzQCFile()
        """
        ...
    
    def store(self, input_file: Union[bytes, str, String] , output_file: Union[bytes, str, String] , exp: MSExperiment , contact_name: Union[bytes, str, String] , contact_address: Union[bytes, str, String] , description: Union[bytes, str, String] , label: Union[bytes, str, String] , feature_map: FeatureMap , prot_ids: List[ProteinIdentification] , pep_ids: PeptideIdentificationList ) -> None:
        """
        Cython signature: void store(String input_file, String output_file, MSExperiment & exp, String contact_name, String contact_address, String description, String label, FeatureMap & feature_map, libcpp_vector[ProteinIdentification] & prot_ids, PeptideIdentificationList & pep_ids)
        Stores QC data in mzQC file with JSON format
        
        
        :param input_file: MzML input file name
        :param output_file: MzQC output file name
        :param exp: MSExperiment to extract QC data from, prior sortSpectra() and updateRanges() required
        :param contact_name: Name of the person creating the mzQC file
        :param contact_address: Contact address (mail/e-mail or phone) of the person creating the mzQC file
        :param description: Description and comments about the mzQC file contents
        :param label: Qnique and informative label for the run
        :param feature_map: FeatureMap from feature file (featureXML)
        :param prot_ids: Protein identifications from ID file (idXML)
        :param pep_ids: Protein identifications from ID file (idXML)
        """
        ... 


class MzXMLFile:
    """
    Cython implementation of _MzXMLFile

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1MzXMLFile.html>`_
      -- Inherits from ['ProgressLogger']
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void MzXMLFile()
        """
        ...
    
    @overload
    def __init__(self, in_0: MzXMLFile ) -> None:
        """
        Cython signature: void MzXMLFile(MzXMLFile &)
        """
        ...
    
    def load(self, filename: Union[bytes, str, String] , exp: MSExperiment ) -> None:
        """
        Cython signature: void load(String filename, MSExperiment & exp)
        Loads a MSExperiment from a MzXML file
        
        
        :param exp: MSExperiment
        """
        ...
    
    def store(self, filename: Union[bytes, str, String] , exp: MSExperiment ) -> None:
        """
        Cython signature: void store(String filename, MSExperiment & exp)
        Stores a MSExperiment in a MzXML file
        
        
        :param exp: MSExperiment
        """
        ...
    
    def getOptions(self) -> PeakFileOptions:
        """
        Cython signature: PeakFileOptions getOptions()
        Returns the options for loading/storing
        """
        ...
    
    def setOptions(self, in_0: PeakFileOptions ) -> None:
        """
        Cython signature: void setOptions(PeakFileOptions)
        Sets options for loading/storing
        """
        ...
    
    def setLogType(self, in_0: int ) -> None:
        """
        Cython signature: void setLogType(LogType)
        Sets the progress log that should be used. The default type is NONE!
        """
        ...
    
    def getLogType(self) -> int:
        """
        Cython signature: LogType getLogType()
        Returns the type of progress log being used
        """
        ...
    
    def startProgress(self, begin: int , end: int , label: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void startProgress(ptrdiff_t begin, ptrdiff_t end, String label)
        """
        ...
    
    def setProgress(self, value: int ) -> None:
        """
        Cython signature: void setProgress(ptrdiff_t value)
        Sets the current progress
        """
        ...
    
    def endProgress(self) -> None:
        """
        Cython signature: void endProgress()
        Ends the progress display
        """
        ...
    
    def nextProgress(self) -> None:
        """
        Cython signature: void nextProgress()
        Increment progress by 1 (according to range begin-end)
        """
        ... 


class OPXLSpectrumProcessingAlgorithms:
    """
    Cython implementation of _OPXLSpectrumProcessingAlgorithms

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1OPXLSpectrumProcessingAlgorithms.html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void OPXLSpectrumProcessingAlgorithms()
        """
        ...
    
    @overload
    def __init__(self, in_0: OPXLSpectrumProcessingAlgorithms ) -> None:
        """
        Cython signature: void OPXLSpectrumProcessingAlgorithms(OPXLSpectrumProcessingAlgorithms &)
        """
        ...
    
    def mergeAnnotatedSpectra(self, first_spectrum: MSSpectrum , second_spectrum: MSSpectrum ) -> MSSpectrum:
        """
        Cython signature: MSSpectrum mergeAnnotatedSpectra(MSSpectrum & first_spectrum, MSSpectrum & second_spectrum)
        """
        ...
    
    def preprocessSpectra(self, exp: MSExperiment , fragment_mass_tolerance: float , fragment_mass_tolerance_unit_ppm: bool , peptide_min_size: int , min_precursor_charge: int , max_precursor_charge: int , deisotope: bool , labeled: bool ) -> MSExperiment:
        """
        Cython signature: MSExperiment preprocessSpectra(MSExperiment & exp, double fragment_mass_tolerance, bool fragment_mass_tolerance_unit_ppm, size_t peptide_min_size, int min_precursor_charge, int max_precursor_charge, bool deisotope, bool labeled)
        """
        ...
    
    def getSpectrumAlignmentFastCharge(self, alignment: List[List[int, int]] , fragment_mass_tolerance: float , fragment_mass_tolerance_unit_ppm: bool , theo_spectrum: MSSpectrum , exp_spectrum: MSSpectrum , theo_charges: IntegerDataArray , exp_charges: IntegerDataArray , ppm_error_array: FloatDataArray , intensity_cutoff: float ) -> None:
        """
        Cython signature: void getSpectrumAlignmentFastCharge(libcpp_vector[libcpp_pair[size_t,size_t]] & alignment, double fragment_mass_tolerance, bool fragment_mass_tolerance_unit_ppm, const MSSpectrum & theo_spectrum, const MSSpectrum & exp_spectrum, const IntegerDataArray & theo_charges, const IntegerDataArray & exp_charges, FloatDataArray & ppm_error_array, double intensity_cutoff)
        """
        ...
    
    def getSpectrumAlignmentSimple(self, alignment: List[List[int, int]] , fragment_mass_tolerance: float , fragment_mass_tolerance_unit_ppm: bool , theo_spectrum: List[SimplePeak] , exp_spectrum: MSSpectrum , exp_charges: IntegerDataArray ) -> None:
        """
        Cython signature: void getSpectrumAlignmentSimple(libcpp_vector[libcpp_pair[size_t,size_t]] & alignment, double fragment_mass_tolerance, bool fragment_mass_tolerance_unit_ppm, const libcpp_vector[SimplePeak] & theo_spectrum, const MSSpectrum & exp_spectrum, const IntegerDataArray & exp_charges)
        """
        ... 


class OpenMSBuildInfo:
    """
    Cython implementation of _OpenMSBuildInfo

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS::Internal_1_1OpenMSBuildInfo.html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void OpenMSBuildInfo()
        """
        ...
    
    @overload
    def __init__(self, in_0: OpenMSBuildInfo ) -> None:
        """
        Cython signature: void OpenMSBuildInfo(OpenMSBuildInfo &)
        """
        ...
    
    getBuildType: __static_OpenMSBuildInfo_getBuildType
    
    getOpenMPMaxNumThreads: __static_OpenMSBuildInfo_getOpenMPMaxNumThreads
    
    isOpenMPEnabled: __static_OpenMSBuildInfo_isOpenMPEnabled
    
    setOpenMPNumThreads: __static_OpenMSBuildInfo_setOpenMPNumThreads 


class OpenMSOSInfo:
    """
    Cython implementation of _OpenMSOSInfo

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS::Internal_1_1OpenMSOSInfo.html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void OpenMSOSInfo()
        """
        ...
    
    @overload
    def __init__(self, in_0: OpenMSOSInfo ) -> None:
        """
        Cython signature: void OpenMSOSInfo(OpenMSOSInfo &)
        """
        ...
    
    def getOSAsString(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getOSAsString()
        """
        ...
    
    def getArchAsString(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getArchAsString()
        """
        ...
    
    def getOSVersionAsString(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getOSVersionAsString()
        """
        ...
    
    getBinaryArchitecture: __static_OpenMSOSInfo_getBinaryArchitecture
    
    getOSInfo: __static_OpenMSOSInfo_getOSInfo 


class PeakBoundary:
    """
    Cython implementation of _PeakBoundary

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1PeakBoundary.html>`_
    """
    
    mz_min: float
    
    mz_max: float
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void PeakBoundary()
        """
        ...
    
    @overload
    def __init__(self, in_0: PeakBoundary ) -> None:
        """
        Cython signature: void PeakBoundary(PeakBoundary &)
        """
        ... 


class PeakPickerHiRes:
    """
    Cython implementation of _PeakPickerHiRes

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1PeakPickerHiRes.html>`_
      -- Inherits from ['DefaultParamHandler', 'ProgressLogger']
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void PeakPickerHiRes()
        """
        ...
    
    @overload
    def __init__(self, in_0: PeakPickerHiRes ) -> None:
        """
        Cython signature: void PeakPickerHiRes(PeakPickerHiRes &)
        """
        ...
    
    @overload
    def pick(self, input: MSSpectrum , output: MSSpectrum ) -> None:
        """
        Cython signature: void pick(MSSpectrum & input, MSSpectrum & output)
        """
        ...
    
    @overload
    def pick(self, input: MSChromatogram , output: MSChromatogram ) -> None:
        """
        Cython signature: void pick(MSChromatogram & input, MSChromatogram & output)
        """
        ...
    
    @overload
    def pickExperiment(self, input: MSExperiment , output: MSExperiment , check_spectrum_type: bool ) -> None:
        """
        Cython signature: void pickExperiment(MSExperiment & input, MSExperiment & output, bool check_spectrum_type)
        Applies the peak-picking algorithm to a map (MSExperiment). This method picks peaks for each scan in the map consecutively. The resulting
        picked peaks are written to the output map
        
        
        :param input: Input map in profile mode
        :param output: Output map with picked peaks
        :param check_spectrum_type: If set, checks spectrum type and throws an exception if a centroided spectrum is passed
        """
        ...
    
    @overload
    def pickExperiment(self, input: MSExperiment , output: MSExperiment , boundaries_spec: List[List[PeakBoundary]] , boundaries_chrom: List[List[PeakBoundary]] , check_spectrum_type: bool ) -> None:
        """
        Cython signature: void pickExperiment(MSExperiment & input, MSExperiment & output, libcpp_vector[libcpp_vector[PeakBoundary]] & boundaries_spec, libcpp_vector[libcpp_vector[PeakBoundary]] & boundaries_chrom, bool check_spectrum_type)
        """
        ...
    
    def getSubsections(self) -> List[bytes]:
        """
        Cython signature: libcpp_vector[String] getSubsections()
        """
        ...
    
    def setParameters(self, param: Param ) -> None:
        """
        Cython signature: void setParameters(Param & param)
        Sets the parameters
        """
        ...
    
    def getParameters(self) -> Param:
        """
        Cython signature: Param getParameters()
        Returns the parameters
        """
        ...
    
    def getDefaults(self) -> Param:
        """
        Cython signature: Param getDefaults()
        Returns the default parameters
        """
        ...
    
    def getName(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getName()
        Returns the name
        """
        ...
    
    def setName(self, in_0: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setName(const String &)
        Sets the name
        """
        ...
    
    def setLogType(self, in_0: int ) -> None:
        """
        Cython signature: void setLogType(LogType)
        Sets the progress log that should be used. The default type is NONE!
        """
        ...
    
    def getLogType(self) -> int:
        """
        Cython signature: LogType getLogType()
        Returns the type of progress log being used
        """
        ...
    
    def startProgress(self, begin: int , end: int , label: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void startProgress(ptrdiff_t begin, ptrdiff_t end, String label)
        """
        ...
    
    def setProgress(self, value: int ) -> None:
        """
        Cython signature: void setProgress(ptrdiff_t value)
        Sets the current progress
        """
        ...
    
    def endProgress(self) -> None:
        """
        Cython signature: void endProgress()
        Ends the progress display
        """
        ...
    
    def nextProgress(self) -> None:
        """
        Cython signature: void nextProgress()
        Increment progress by 1 (according to range begin-end)
        """
        ... 


class ProteinGroup:
    """
    Cython implementation of _ProteinGroup

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1ProteinGroup.html>`_
    """
    
    probability: float
    
    accessions: List[bytes]
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void ProteinGroup()
        """
        ...
    
    @overload
    def __init__(self, in_0: ProteinGroup ) -> None:
        """
        Cython signature: void ProteinGroup(ProteinGroup &)
        """
        ... 


class ProteinIdentification:
    """
    Cython implementation of _ProteinIdentification

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1ProteinIdentification.html>`_
      -- Inherits from ['MetaInfoInterface']
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void ProteinIdentification()
        """
        ...
    
    @overload
    def __init__(self, in_0: ProteinIdentification ) -> None:
        """
        Cython signature: void ProteinIdentification(ProteinIdentification &)
        """
        ...
    
    def getHits(self) -> List[ProteinHit]:
        """
        Cython signature: libcpp_vector[ProteinHit] getHits()
        Returns the protein hits
        """
        ...
    
    def insertHit(self, input: ProteinHit ) -> None:
        """
        Cython signature: void insertHit(ProteinHit input)
        Appends a protein hit
        """
        ...
    
    def setHits(self, hits: List[ProteinHit] ) -> None:
        """
        Cython signature: void setHits(libcpp_vector[ProteinHit] hits)
        Sets the protein hits
        """
        ...
    
    def getProteinGroups(self) -> List[ProteinGroup]:
        """
        Cython signature: libcpp_vector[ProteinGroup] getProteinGroups()
        Returns the protein groups
        """
        ...
    
    def insertProteinGroup(self, group: ProteinGroup ) -> None:
        """
        Cython signature: void insertProteinGroup(ProteinGroup group)
        Appends a new protein group
        """
        ...
    
    def getIndistinguishableProteins(self) -> List[ProteinGroup]:
        """
        Cython signature: libcpp_vector[ProteinGroup] getIndistinguishableProteins()
        Returns the indistinguishable proteins
        """
        ...
    
    def insertIndistinguishableProteins(self, group: ProteinGroup ) -> None:
        """
        Cython signature: void insertIndistinguishableProteins(ProteinGroup group)
        Appends new indistinguishable proteins
        """
        ...
    
    def getSignificanceThreshold(self) -> float:
        """
        Cython signature: double getSignificanceThreshold()
        Returns the protein significance threshold value
        """
        ...
    
    def setSignificanceThreshold(self, value: float ) -> None:
        """
        Cython signature: void setSignificanceThreshold(double value)
        Sets the protein significance threshold value
        """
        ...
    
    def getScoreType(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getScoreType()
        Returns the protein score type
        """
        ...
    
    def setScoreType(self, type: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setScoreType(String type)
        Sets the protein score type
        """
        ...
    
    def isHigherScoreBetter(self) -> bool:
        """
        Cython signature: bool isHigherScoreBetter()
        Returns true if a higher score represents a better score
        """
        ...
    
    def setHigherScoreBetter(self, higher_is_better: bool ) -> None:
        """
        Cython signature: void setHigherScoreBetter(bool higher_is_better)
        Sets the orientation of the score (is higher better?)
        """
        ...
    
    def sort(self) -> None:
        """
        Cython signature: void sort()
        Sorts the protein hits according to their score
        """
        ...
    
    def computeCoverage(self, pep_ids: PeptideIdentificationList ) -> None:
        """
        Cython signature: void computeCoverage(PeptideIdentificationList pep_ids)
        Compute the coverage (in percent) of all ProteinHits given PeptideHits
        """
        ...
    
    def getDateTime(self) -> DateTime:
        """
        Cython signature: DateTime getDateTime()
        Returns the date of the protein identification run
        """
        ...
    
    def setDateTime(self, date: DateTime ) -> None:
        """
        Cython signature: void setDateTime(DateTime date)
        Sets the date of the protein identification run
        """
        ...
    
    def setSearchEngine(self, search_engine: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setSearchEngine(String search_engine)
        Sets the search engine type
        """
        ...
    
    def getSearchEngine(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getSearchEngine()
        Returns the type of search engine used
        """
        ...
    
    def setSearchEngineVersion(self, search_engine_version: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setSearchEngineVersion(String search_engine_version)
        Sets the search engine version
        """
        ...
    
    def getSearchEngineVersion(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getSearchEngineVersion()
        Returns the search engine version
        """
        ...
    
    def setSearchParameters(self, search_parameters: SearchParameters ) -> None:
        """
        Cython signature: void setSearchParameters(SearchParameters search_parameters)
        Sets the search parameters
        """
        ...
    
    def getSearchParameters(self) -> SearchParameters:
        """
        Cython signature: SearchParameters getSearchParameters()
        Returns the search parameters
        """
        ...
    
    def getIdentifier(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getIdentifier()
        Returns the identifier
        """
        ...
    
    def setIdentifier(self, id_: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setIdentifier(String id_)
        Sets the identifier
        """
        ...
    
    @overload
    def setPrimaryMSRunPath(self, s: List[bytes] ) -> None:
        """
        Cython signature: void setPrimaryMSRunPath(StringList & s)
        Set the file paths to the primary MS runs (usually the mzML files obtained after data conversion from raw files)
        
        
        :param raw: Store paths to the raw files (or equivalent) rather than mzMLs
        """
        ...
    
    @overload
    def setPrimaryMSRunPath(self, s: List[bytes] , raw: bool ) -> None:
        """
        Cython signature: void setPrimaryMSRunPath(StringList & s, bool raw)
        """
        ...
    
    @overload
    def addPrimaryMSRunPath(self, s: List[bytes] ) -> None:
        """
        Cython signature: void addPrimaryMSRunPath(StringList & s)
        """
        ...
    
    @overload
    def addPrimaryMSRunPath(self, s: List[bytes] , raw: bool ) -> None:
        """
        Cython signature: void addPrimaryMSRunPath(StringList & s, bool raw)
        """
        ...
    
    @overload
    def getPrimaryMSRunPath(self, output: List[bytes] ) -> None:
        """
        Cython signature: void getPrimaryMSRunPath(StringList & output)
        """
        ...
    
    @overload
    def getPrimaryMSRunPath(self, output: List[bytes] , raw: bool ) -> None:
        """
        Cython signature: void getPrimaryMSRunPath(StringList & output, bool raw)
        """
        ...
    
    @staticmethod
    def getAllNamesOfPeakMassType() -> List[bytes]:
        """
        Cython signature: libcpp_vector[String] getAllNamesOfPeakMassType()
        Returns all peak mass type names known to OpenMS
        """
        ...
    
    def isMetaEmpty(self) -> bool:
        """
        Cython signature: bool isMetaEmpty()
        Returns if the MetaInfo is empty
        """
        ...
    
    def clearMetaInfo(self) -> None:
        """
        Cython signature: void clearMetaInfo()
        Removes all meta values
        """
        ...
    
    def metaRegistry(self) -> MetaInfoRegistry:
        """
        Cython signature: MetaInfoRegistry metaRegistry()
        Returns a reference to the MetaInfoRegistry
        """
        ...
    
    def getKeys(self, keys: List[bytes] ) -> None:
        """
        Cython signature: void getKeys(libcpp_vector[String] & keys)
        Fills the given vector with a list of all keys for which a value is set
        """
        ...
    
    def getMetaValue(self, in_0: Union[bytes, str, String] ) -> Union[int, float, bytes, str, List[int], List[float], List[bytes]]:
        """
        Cython signature: DataValue getMetaValue(String)
        Returns the value corresponding to a string, or
        """
        ...
    
    def setMetaValue(self, in_0: Union[bytes, str, String] , in_1: Union[int, float, bytes, str, List[int], List[float], List[bytes]] ) -> None:
        """
        Cython signature: void setMetaValue(String, DataValue)
        Sets the DataValue corresponding to a name
        """
        ...
    
    def metaValueExists(self, in_0: Union[bytes, str, String] ) -> bool:
        """
        Cython signature: bool metaValueExists(String)
        Returns whether an entry with the given name exists
        """
        ...
    
    def removeMetaValue(self, in_0: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void removeMetaValue(String)
        Removes the DataValue corresponding to `name` if it exists
        """
        ...
    
    def __richcmp__(self, other: ProteinIdentification, op: int) -> Any:
        ...
    PeakMassType : __PeakMassType 


class QcMLFile:
    """
    Cython implementation of _QcMLFile

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1QcMLFile.html>`_
      -- Inherits from ['XMLHandler', 'XMLFile', 'ProgressLogger']

    File adapter for QcML files used to load and store QcML files
    
    This Class is supposed to internally collect the data for the qcML File
    """
    
    def __init__(self) -> None:
        """
        Cython signature: void QcMLFile()
        """
        ...
    
    def exportIDstats(self, filename: Union[bytes, str, String] ) -> Union[bytes, str, String]:
        """
        Cython signature: String exportIDstats(const String & filename)
        """
        ...
    
    def addRunQualityParameter(self, r: Union[bytes, str, String] , qp: QualityParameter ) -> None:
        """
        Cython signature: void addRunQualityParameter(String r, QualityParameter qp)
        Adds a QualityParameter to run by the name r
        """
        ...
    
    def addRunAttachment(self, r: Union[bytes, str, String] , at: Attachment ) -> None:
        """
        Cython signature: void addRunAttachment(String r, Attachment at)
        Adds a attachment to run by the name r
        """
        ...
    
    def addSetQualityParameter(self, r: Union[bytes, str, String] , qp: QualityParameter ) -> None:
        """
        Cython signature: void addSetQualityParameter(String r, QualityParameter qp)
        Adds a QualityParameter to set by the name r
        """
        ...
    
    def addSetAttachment(self, r: Union[bytes, str, String] , at: Attachment ) -> None:
        """
        Cython signature: void addSetAttachment(String r, Attachment at)
        Adds a attachment to set by the name r
        """
        ...
    
    @overload
    def removeAttachment(self, r: Union[bytes, str, String] , ids: List[bytes] , at: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void removeAttachment(String r, libcpp_vector[String] & ids, String at)
        Removes attachments referencing an id given in ids, from run/set r. All attachments if no attachment name is given with at
        """
        ...
    
    @overload
    def removeAttachment(self, r: Union[bytes, str, String] , at: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void removeAttachment(String r, String at)
        Removes attachment with cv accession at from run/set r
        """
        ...
    
    def removeAllAttachments(self, at: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void removeAllAttachments(String at)
        Removes attachment with cv accession at from all runs/sets
        """
        ...
    
    def removeQualityParameter(self, r: Union[bytes, str, String] , ids: List[bytes] ) -> None:
        """
        Cython signature: void removeQualityParameter(String r, libcpp_vector[String] & ids)
        Removes QualityParameter going by one of the ID attributes given in ids
        """
        ...
    
    def merge(self, addendum: QcMLFile , setname: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void merge(QcMLFile & addendum, String setname)
        Merges the given QCFile into this one
        """
        ...
    
    def collectSetParameter(self, setname: Union[bytes, str, String] , qp: Union[bytes, str, String] , ret: List[bytes] ) -> None:
        """
        Cython signature: void collectSetParameter(String setname, String qp, libcpp_vector[String] & ret)
        Collects the values of given QPs (as CVid) of the given set
        """
        ...
    
    def exportAttachment(self, filename: Union[bytes, str, String] , qpname: Union[bytes, str, String] ) -> Union[bytes, str, String]:
        """
        Cython signature: String exportAttachment(String filename, String qpname)
        Returns a String of a tab separated rows if found empty string else from run/set by the name filename of the qualityparameter by the name qpname
        """
        ...
    
    def getRunNames(self, ids: List[bytes] ) -> None:
        """
        Cython signature: void getRunNames(libcpp_vector[String] & ids)
        Gives the names of the registered runs in the vector ids
        """
        ...
    
    def existsRun(self, filename: Union[bytes, str, String] ) -> bool:
        """
        Cython signature: bool existsRun(String filename)
        Returns true if the given run id is present in this file, if checkname is true it also checks the names
        """
        ...
    
    def existsSet(self, filename: Union[bytes, str, String] ) -> bool:
        """
        Cython signature: bool existsSet(String filename)
        Returns true if the given set id is present in this file, if checkname is true it also checks the names
        """
        ...
    
    def existsRunQualityParameter(self, filename: Union[bytes, str, String] , qpname: Union[bytes, str, String] , ids: List[bytes] ) -> None:
        """
        Cython signature: void existsRunQualityParameter(String filename, String qpname, libcpp_vector[String] & ids)
        Returns the ids of the parameter name given if found in given run empty else
        """
        ...
    
    def existsSetQualityParameter(self, filename: Union[bytes, str, String] , qpname: Union[bytes, str, String] , ids: List[bytes] ) -> None:
        """
        Cython signature: void existsSetQualityParameter(String filename, String qpname, libcpp_vector[String] & ids)
        Returns the ids of the parameter name given if found in given set, empty else
        """
        ...
    
    def store(self, filename: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void store(const String & filename)
        Store the qcML file
        """
        ...
    
    def load(self, filename: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void load(const String & filename)
        Load a QCFile
        """
        ...
    
    def registerRun(self, id_: Union[bytes, str, String] , name: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void registerRun(String id_, String name)
        Registers a run in the qcml file with the respective mappings
        """
        ...
    
    def registerSet(self, id_: Union[bytes, str, String] , name: Union[bytes, str, String] , names: Set[bytes] ) -> None:
        """
        Cython signature: void registerSet(String id_, String name, libcpp_set[String] & names)
        Registers a set in the qcml file with the respective mappings
        """
        ...
    
    def exportQP(self, filename: Union[bytes, str, String] , qpname: Union[bytes, str, String] ) -> Union[bytes, str, String]:
        """
        Cython signature: String exportQP(String filename, String qpname)
        Returns a String value in quotation of a QualityParameter by the name qpname in run/set by the name filename
        """
        ...
    
    def exportQPs(self, filename: Union[bytes, str, String] , qpnames: List[bytes] ) -> Union[bytes, str, String]:
        """
        Cython signature: String exportQPs(String filename, StringList qpnames)
        Returns a String of a tab separated QualityParameter by the name qpname in run/set by the name filename
        """
        ...
    
    def getRunIDs(self, ids: List[bytes] ) -> None:
        """
        Cython signature: void getRunIDs(libcpp_vector[String] & ids)
        Gives the ids of the registered runs in the vector ids
        """
        ...
    
    def reset(self) -> None:
        """
        Cython signature: void reset()
        """
        ...
    
    def error(self, mode: int , msg: Union[bytes, str, String] , line: int , column: int ) -> None:
        """
        Cython signature: void error(ActionMode mode, const String & msg, unsigned int line, unsigned int column)
        """
        ...
    
    def warning(self, mode: int , msg: Union[bytes, str, String] , line: int , column: int ) -> None:
        """
        Cython signature: void warning(ActionMode mode, const String & msg, unsigned int line, unsigned int column)
        """
        ...
    
    def getVersion(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getVersion()
        Return the version of the schema
        """
        ...
    
    def setLogType(self, in_0: int ) -> None:
        """
        Cython signature: void setLogType(LogType)
        Sets the progress log that should be used. The default type is NONE!
        """
        ...
    
    def getLogType(self) -> int:
        """
        Cython signature: LogType getLogType()
        Returns the type of progress log being used
        """
        ...
    
    def startProgress(self, begin: int , end: int , label: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void startProgress(ptrdiff_t begin, ptrdiff_t end, String label)
        """
        ...
    
    def setProgress(self, value: int ) -> None:
        """
        Cython signature: void setProgress(ptrdiff_t value)
        Sets the current progress
        """
        ...
    
    def endProgress(self) -> None:
        """
        Cython signature: void endProgress()
        Ends the progress display
        """
        ...
    
    def nextProgress(self) -> None:
        """
        Cython signature: void nextProgress()
        Increment progress by 1 (according to range begin-end)
        """
        ... 


class QualityParameter:
    """
    Cython implementation of _QualityParameter

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1QualityParameter.html>`_
    """
    
    name: Union[bytes, str, String]
    
    id: Union[bytes, str, String]
    
    value: Union[bytes, str, String]
    
    cvRef: Union[bytes, str, String]
    
    cvAcc: Union[bytes, str, String]
    
    unitRef: Union[bytes, str, String]
    
    unitAcc: Union[bytes, str, String]
    
    flag: Union[bytes, str, String]
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void QualityParameter()
        """
        ...
    
    @overload
    def __init__(self, in_0: QualityParameter ) -> None:
        """
        Cython signature: void QualityParameter(QualityParameter &)
        """
        ...
    
    def toXMLString(self, indentation_level: int ) -> Union[bytes, str, String]:
        """
        Cython signature: String toXMLString(unsigned int indentation_level)
        """
        ...
    
    def __richcmp__(self, other: QualityParameter, op: int) -> Any:
        ... 


class RankScaler:
    """
    Cython implementation of _RankScaler

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1RankScaler.html>`_
      -- Inherits from ['DefaultParamHandler']
    """
    
    def __init__(self) -> None:
        """
        Cython signature: void RankScaler()
        """
        ...
    
    def filterSpectrum(self, spec: MSSpectrum ) -> None:
        """
        Cython signature: void filterSpectrum(MSSpectrum & spec)
        """
        ...
    
    def filterPeakSpectrum(self, spec: MSSpectrum ) -> None:
        """
        Cython signature: void filterPeakSpectrum(MSSpectrum & spec)
        """
        ...
    
    def filterPeakMap(self, exp: MSExperiment ) -> None:
        """
        Cython signature: void filterPeakMap(MSExperiment & exp)
        """
        ...
    
    def getSubsections(self) -> List[bytes]:
        """
        Cython signature: libcpp_vector[String] getSubsections()
        """
        ...
    
    def setParameters(self, param: Param ) -> None:
        """
        Cython signature: void setParameters(Param & param)
        Sets the parameters
        """
        ...
    
    def getParameters(self) -> Param:
        """
        Cython signature: Param getParameters()
        Returns the parameters
        """
        ...
    
    def getDefaults(self) -> Param:
        """
        Cython signature: Param getDefaults()
        Returns the default parameters
        """
        ...
    
    def getName(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getName()
        Returns the name
        """
        ...
    
    def setName(self, in_0: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setName(const String &)
        Sets the name
        """
        ... 


class SearchParameters:
    """
    Cython implementation of _SearchParameters

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1SearchParameters.html>`_
      -- Inherits from ['MetaInfoInterface']
    """
    
    db: Union[bytes, str, String]
    
    db_version: Union[bytes, str, String]
    
    taxonomy: Union[bytes, str, String]
    
    charges: Union[bytes, str, String]
    
    mass_type: int
    
    fixed_modifications: List[bytes]
    
    variable_modifications: List[bytes]
    
    missed_cleavages: int
    
    fragment_mass_tolerance: float
    
    fragment_mass_tolerance_ppm: bool
    
    precursor_mass_tolerance: float
    
    precursor_mass_tolerance_ppm: bool
    
    digestion_enzyme: DigestionEnzymeProtein
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void SearchParameters()
        """
        ...
    
    @overload
    def __init__(self, in_0: SearchParameters ) -> None:
        """
        Cython signature: void SearchParameters(SearchParameters &)
        """
        ...
    
    def isMetaEmpty(self) -> bool:
        """
        Cython signature: bool isMetaEmpty()
        Returns if the MetaInfo is empty
        """
        ...
    
    def clearMetaInfo(self) -> None:
        """
        Cython signature: void clearMetaInfo()
        Removes all meta values
        """
        ...
    
    def metaRegistry(self) -> MetaInfoRegistry:
        """
        Cython signature: MetaInfoRegistry metaRegistry()
        Returns a reference to the MetaInfoRegistry
        """
        ...
    
    def getKeys(self, keys: List[bytes] ) -> None:
        """
        Cython signature: void getKeys(libcpp_vector[String] & keys)
        Fills the given vector with a list of all keys for which a value is set
        """
        ...
    
    def getMetaValue(self, in_0: Union[bytes, str, String] ) -> Union[int, float, bytes, str, List[int], List[float], List[bytes]]:
        """
        Cython signature: DataValue getMetaValue(String)
        Returns the value corresponding to a string, or
        """
        ...
    
    def setMetaValue(self, in_0: Union[bytes, str, String] , in_1: Union[int, float, bytes, str, List[int], List[float], List[bytes]] ) -> None:
        """
        Cython signature: void setMetaValue(String, DataValue)
        Sets the DataValue corresponding to a name
        """
        ...
    
    def metaValueExists(self, in_0: Union[bytes, str, String] ) -> bool:
        """
        Cython signature: bool metaValueExists(String)
        Returns whether an entry with the given name exists
        """
        ...
    
    def removeMetaValue(self, in_0: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void removeMetaValue(String)
        Removes the DataValue corresponding to `name` if it exists
        """
        ...
    
    def __richcmp__(self, other: SearchParameters, op: int) -> Any:
        ... 


class SpectralMatch:
    """
    Cython implementation of _SpectralMatch

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1SpectralMatch.html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void SpectralMatch()
        """
        ...
    
    @overload
    def __init__(self, in_0: SpectralMatch ) -> None:
        """
        Cython signature: void SpectralMatch(SpectralMatch &)
        """
        ...
    
    def getObservedPrecursorMass(self) -> float:
        """
        Cython signature: double getObservedPrecursorMass()
        """
        ...
    
    def setObservedPrecursorMass(self, in_0: float ) -> None:
        """
        Cython signature: void setObservedPrecursorMass(double)
        """
        ...
    
    def getObservedPrecursorRT(self) -> float:
        """
        Cython signature: double getObservedPrecursorRT()
        """
        ...
    
    def setObservedPrecursorRT(self, in_0: float ) -> None:
        """
        Cython signature: void setObservedPrecursorRT(double)
        """
        ...
    
    def getFoundPrecursorMass(self) -> float:
        """
        Cython signature: double getFoundPrecursorMass()
        """
        ...
    
    def setFoundPrecursorMass(self, in_0: float ) -> None:
        """
        Cython signature: void setFoundPrecursorMass(double)
        """
        ...
    
    def getFoundPrecursorCharge(self) -> int:
        """
        Cython signature: int getFoundPrecursorCharge()
        """
        ...
    
    def setFoundPrecursorCharge(self, in_0: int ) -> None:
        """
        Cython signature: void setFoundPrecursorCharge(int)
        """
        ...
    
    def getMatchingScore(self) -> float:
        """
        Cython signature: double getMatchingScore()
        """
        ...
    
    def setMatchingScore(self, in_0: float ) -> None:
        """
        Cython signature: void setMatchingScore(double)
        """
        ...
    
    def getObservedSpectrumIndex(self) -> int:
        """
        Cython signature: size_t getObservedSpectrumIndex()
        """
        ...
    
    def setObservedSpectrumIndex(self, in_0: int ) -> None:
        """
        Cython signature: void setObservedSpectrumIndex(size_t)
        """
        ...
    
    def getMatchingSpectrumIndex(self) -> int:
        """
        Cython signature: size_t getMatchingSpectrumIndex()
        """
        ...
    
    def setMatchingSpectrumIndex(self, in_0: int ) -> None:
        """
        Cython signature: void setMatchingSpectrumIndex(size_t)
        """
        ...
    
    def getPrimaryIdentifier(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getPrimaryIdentifier()
        """
        ...
    
    def setPrimaryIdentifier(self, in_0: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setPrimaryIdentifier(String)
        """
        ...
    
    def getSecondaryIdentifier(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getSecondaryIdentifier()
        """
        ...
    
    def setSecondaryIdentifier(self, in_0: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setSecondaryIdentifier(String)
        """
        ...
    
    def getCommonName(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getCommonName()
        """
        ...
    
    def setCommonName(self, in_0: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setCommonName(String)
        """
        ...
    
    def getSumFormula(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getSumFormula()
        """
        ...
    
    def setSumFormula(self, in_0: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setSumFormula(String)
        """
        ...
    
    def getInchiString(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getInchiString()
        """
        ...
    
    def setInchiString(self, in_0: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setInchiString(String)
        """
        ...
    
    def getSMILESString(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getSMILESString()
        """
        ...
    
    def setSMILESString(self, in_0: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setSMILESString(String)
        """
        ...
    
    def getPrecursorAdduct(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getPrecursorAdduct()
        """
        ...
    
    def setPrecursorAdduct(self, in_0: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setPrecursorAdduct(String)
        """
        ... 


class SpectrumAccessQuadMZTransforming:
    """
    Cython implementation of _SpectrumAccessQuadMZTransforming

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1SpectrumAccessQuadMZTransforming.html>`_
      -- Inherits from ['SpectrumAccessTransforming']
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void SpectrumAccessQuadMZTransforming()
        """
        ...
    
    @overload
    def __init__(self, in_0: SpectrumAccessQuadMZTransforming ) -> None:
        """
        Cython signature: void SpectrumAccessQuadMZTransforming(SpectrumAccessQuadMZTransforming &)
        """
        ...
    
    @overload
    def __init__(self, in_0: SpectrumAccessOpenMS , a: float , b: float , c: float , ppm: bool ) -> None:
        """
        Cython signature: void SpectrumAccessQuadMZTransforming(shared_ptr[SpectrumAccessOpenMS], double a, double b, double c, bool ppm)
        """
        ...
    
    @overload
    def __init__(self, in_0: SpectrumAccessOpenMSCached , a: float , b: float , c: float , ppm: bool ) -> None:
        """
        Cython signature: void SpectrumAccessQuadMZTransforming(shared_ptr[SpectrumAccessOpenMSCached], double a, double b, double c, bool ppm)
        """
        ...
    
    @overload
    def __init__(self, in_0: SpectrumAccessOpenMSInMemory , a: float , b: float , c: float , ppm: bool ) -> None:
        """
        Cython signature: void SpectrumAccessQuadMZTransforming(shared_ptr[SpectrumAccessOpenMSInMemory], double a, double b, double c, bool ppm)
        """
        ...
    
    def getSpectrumById(self, id_: int ) -> OSSpectrum:
        """
        Cython signature: shared_ptr[OSSpectrum] getSpectrumById(int id_)
        Returns a pointer to a spectrum at the given string id
        """
        ...
    
    def getSpectraByRT(self, RT: float , deltaRT: float ) -> List[int]:
        """
        Cython signature: libcpp_vector[size_t] getSpectraByRT(double RT, double deltaRT)
        Returns a vector of ids of spectra that are within RT +/- deltaRT
        """
        ...
    
    def getNrSpectra(self) -> int:
        """
        Cython signature: size_t getNrSpectra()
        Returns the number of spectra available
        """
        ...
    
    def getChromatogramById(self, id_: int ) -> OSChromatogram:
        """
        Cython signature: shared_ptr[OSChromatogram] getChromatogramById(int id_)
        Returns a pointer to a chromatogram at the given id
        """
        ...
    
    def getNrChromatograms(self) -> int:
        """
        Cython signature: size_t getNrChromatograms()
        Returns the number of chromatograms available
        """
        ...
    
    def getChromatogramNativeID(self, id_: int ) -> str:
        """
        Cython signature: libcpp_utf8_output_string getChromatogramNativeID(int id_)
        """
        ... 


class SpectrumAlignment:
    """
    Cython implementation of _SpectrumAlignment

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1SpectrumAlignment.html>`_
      -- Inherits from ['DefaultParamHandler']

    Aligns the peaks of two sorted spectra
    Method 1: Using a banded (width via 'tolerance' parameter) alignment if absolute tolerances are given
        Scoring function is the m/z distance between peaks. Intensity does not play a role!
    Method 2: If relative tolerance (ppm) is specified a simple matching of peaks is performed:
    Peaks from s1 (usually the theoretical spectrum) are assigned to the closest peak in s2 if it lies in the tolerance window
    
    note: A peak in s2 can be matched to none, one or multiple peaks in s1. Peaks in s1 may be matched to none or one peak in s2
    note: Intensity is ignored
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void SpectrumAlignment()
        """
        ...
    
    @overload
    def __init__(self, in_0: SpectrumAlignment ) -> None:
        """
        Cython signature: void SpectrumAlignment(SpectrumAlignment &)
        """
        ...
    
    def getSubsections(self) -> List[bytes]:
        """
        Cython signature: libcpp_vector[String] getSubsections()
        """
        ...
    
    def setParameters(self, param: Param ) -> None:
        """
        Cython signature: void setParameters(Param & param)
        Sets the parameters
        """
        ...
    
    def getParameters(self) -> Param:
        """
        Cython signature: Param getParameters()
        Returns the parameters
        """
        ...
    
    def getDefaults(self) -> Param:
        """
        Cython signature: Param getDefaults()
        Returns the default parameters
        """
        ...
    
    def getName(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getName()
        Returns the name
        """
        ...
    
    def setName(self, in_0: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setName(const String &)
        Sets the name
        """
        ... 


class StablePairFinder:
    """
    Cython implementation of _StablePairFinder

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1StablePairFinder.html>`_
      -- Inherits from ['BaseGroupFinder']
    """
    
    def __init__(self) -> None:
        """
        Cython signature: void StablePairFinder()
        """
        ...
    
    def run(self, input_maps: List[ConsensusMap] , result_map: ConsensusMap ) -> None:
        """
        Cython signature: void run(libcpp_vector[ConsensusMap] & input_maps, ConsensusMap & result_map)
        """
        ...
    
    def getSubsections(self) -> List[bytes]:
        """
        Cython signature: libcpp_vector[String] getSubsections()
        """
        ...
    
    def setParameters(self, param: Param ) -> None:
        """
        Cython signature: void setParameters(Param & param)
        Sets the parameters
        """
        ...
    
    def getParameters(self) -> Param:
        """
        Cython signature: Param getParameters()
        Returns the parameters
        """
        ...
    
    def getDefaults(self) -> Param:
        """
        Cython signature: Param getDefaults()
        Returns the default parameters
        """
        ...
    
    def getName(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getName()
        Returns the name
        """
        ...
    
    def setName(self, in_0: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setName(const String &)
        Sets the name
        """
        ...
    
    def setLogType(self, in_0: int ) -> None:
        """
        Cython signature: void setLogType(LogType)
        Sets the progress log that should be used. The default type is NONE!
        """
        ...
    
    def getLogType(self) -> int:
        """
        Cython signature: LogType getLogType()
        Returns the type of progress log being used
        """
        ...
    
    def startProgress(self, begin: int , end: int , label: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void startProgress(ptrdiff_t begin, ptrdiff_t end, String label)
        """
        ...
    
    def setProgress(self, value: int ) -> None:
        """
        Cython signature: void setProgress(ptrdiff_t value)
        Sets the current progress
        """
        ...
    
    def endProgress(self) -> None:
        """
        Cython signature: void endProgress()
        Ends the progress display
        """
        ...
    
    def nextProgress(self) -> None:
        """
        Cython signature: void nextProgress()
        Increment progress by 1 (according to range begin-end)
        """
        ... 


class StringView:
    """
    Cython implementation of _StringView

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1StringView.html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void StringView()
        """
        ...
    
    @overload
    def __init__(self, in_0: bytes ) -> None:
        """
        Cython signature: void StringView(const libcpp_string &)
        """
        ...
    
    @overload
    def __init__(self, in_0: StringView ) -> None:
        """
        Cython signature: void StringView(StringView &)
        """
        ...
    
    def substr(self, start: int , end: int ) -> StringView:
        """
        Cython signature: StringView substr(size_t start, size_t end)
        """
        ...
    
    def size(self) -> int:
        """
        Cython signature: size_t size()
        """
        ...
    
    def getString(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getString()
        """
        ...
    
    def __richcmp__(self, other: StringView, op: int) -> Any:
        ... 


class SwathMapMassCorrection:
    """
    Cython implementation of _SwathMapMassCorrection

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1SwathMapMassCorrection.html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void SwathMapMassCorrection()
        """
        ...
    
    @overload
    def __init__(self, in_0: SwathMapMassCorrection ) -> None:
        """
        Cython signature: void SwathMapMassCorrection(SwathMapMassCorrection)
        """
        ... 


class TMTSixteenPlexQuantitationMethod:
    """
    Cython implementation of _TMTSixteenPlexQuantitationMethod

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1TMTSixteenPlexQuantitationMethod.html>`_
      -- Inherits from ['IsobaricQuantitationMethod']
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void TMTSixteenPlexQuantitationMethod()
        """
        ...
    
    @overload
    def __init__(self, in_0: TMTSixteenPlexQuantitationMethod ) -> None:
        """
        Cython signature: void TMTSixteenPlexQuantitationMethod(TMTSixteenPlexQuantitationMethod &)
        """
        ...
    
    def getName(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getName()
        """
        ...
    
    def getChannelInformation(self) -> List[IsobaricChannelInformation]:
        """
        Cython signature: libcpp_vector[IsobaricChannelInformation] getChannelInformation()
        """
        ...
    
    def getNumberOfChannels(self) -> int:
        """
        Cython signature: size_t getNumberOfChannels()
        """
        ...
    
    def getIsotopeCorrectionMatrix(self) -> MatrixDouble:
        """
        Cython signature: MatrixDouble getIsotopeCorrectionMatrix()
        """
        ...
    
    def getReferenceChannel(self) -> int:
        """
        Cython signature: size_t getReferenceChannel()
        """
        ...
    
    def getSubsections(self) -> List[bytes]:
        """
        Cython signature: libcpp_vector[String] getSubsections()
        """
        ...
    
    def setParameters(self, param: Param ) -> None:
        """
        Cython signature: void setParameters(Param & param)
        Sets the parameters
        """
        ...
    
    def getParameters(self) -> Param:
        """
        Cython signature: Param getParameters()
        Returns the parameters
        """
        ...
    
    def getDefaults(self) -> Param:
        """
        Cython signature: Param getDefaults()
        Returns the default parameters
        """
        ...
    
    def setName(self, in_0: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setName(const String &)
        Sets the name
        """
        ... 


class TransformationModelBSpline:
    """
    Cython implementation of _TransformationModelBSpline

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1TransformationModelBSpline.html>`_
      -- Inherits from ['TransformationModel']
    """
    
    def __init__(self, data: List[TM_DataPoint] , params: Param ) -> None:
        """
        Cython signature: void TransformationModelBSpline(libcpp_vector[TM_DataPoint] & data, Param & params)
        """
        ...
    
    def getDefaultParameters(self, in_0: Param ) -> None:
        """
        Cython signature: void getDefaultParameters(Param &)
        Gets the default parameters
        """
        ...
    
    def evaluate(self, value: float ) -> float:
        """
        Cython signature: double evaluate(double value)
        Evaluates the model at the given values
        """
        ...
    
    def getParameters(self) -> Param:
        """
        Cython signature: Param getParameters()
        """
        ...
    
    def weightData(self, data: List[TM_DataPoint] ) -> None:
        """
        Cython signature: void weightData(libcpp_vector[TM_DataPoint] & data)
        Weight the data by the given weight function
        """
        ...
    
    def checkValidWeight(self, weight: Union[bytes, str, String] , valid_weights: List[bytes] ) -> bool:
        """
        Cython signature: bool checkValidWeight(const String & weight, const libcpp_vector[String] & valid_weights)
        Check for a valid weighting function string
        """
        ...
    
    def weightDatum(self, datum: float , weight: Union[bytes, str, String] ) -> float:
        """
        Cython signature: double weightDatum(double & datum, const String & weight)
        Weight the data according to the weighting function
        """
        ...
    
    def unWeightDatum(self, datum: float , weight: Union[bytes, str, String] ) -> float:
        """
        Cython signature: double unWeightDatum(double & datum, const String & weight)
        Apply the reverse of the weighting function to the data
        """
        ...
    
    def getValidXWeights(self) -> List[bytes]:
        """
        Cython signature: libcpp_vector[String] getValidXWeights()
        Returns a list of valid x weight function stringss
        """
        ...
    
    def getValidYWeights(self) -> List[bytes]:
        """
        Cython signature: libcpp_vector[String] getValidYWeights()
        Returns a list of valid y weight function strings
        """
        ...
    
    def unWeightData(self, data: List[TM_DataPoint] ) -> None:
        """
        Cython signature: void unWeightData(libcpp_vector[TM_DataPoint] & data)
        Unweight the data by the given weight function
        """
        ...
    
    def checkDatumRange(self, datum: float , datum_min: float , datum_max: float ) -> float:
        """
        Cython signature: double checkDatumRange(const double & datum, const double & datum_min, const double & datum_max)
        Check that the datum is within the valid min and max bounds
        """
        ...
    
    getDefaultParameters: __static_TransformationModelBSpline_getDefaultParameters 


class XLPrecursor:
    """
    Cython implementation of _XLPrecursor

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1XLPrecursor.html>`_
    """
    
    precursor_mass: float
    
    alpha_index: int
    
    beta_index: int
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void XLPrecursor()
        """
        ...
    
    @overload
    def __init__(self, in_0: XLPrecursor ) -> None:
        """
        Cython signature: void XLPrecursor(XLPrecursor &)
        """
        ... 


class XMLFile:
    """
    Cython implementation of _XMLFile

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS::Internal_1_1XMLFile.html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void XMLFile()
        """
        ...
    
    @overload
    def __init__(self, in_0: XMLFile ) -> None:
        """
        Cython signature: void XMLFile(XMLFile &)
        """
        ...
    
    @overload
    def __init__(self, schema_location: Union[bytes, str, String] , version: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void XMLFile(const String & schema_location, const String & version)
        """
        ...
    
    def getVersion(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getVersion()
        Return the version of the schema
        """
        ... 


class __CHARGEMODE_MFD:
    None
    QFROMFEATURE : int
    QHEURISTIC : int
    QALL : int

    def getMapping(self) -> Dict[int, str]:
       ... 


class ITRAQ_TYPES:
    None
    FOURPLEX : int
    EIGHTPLEX : int
    TMT_SIXPLEX : int
    SIZE_OF_ITRAQ_TYPES : int

    def getMapping(self) -> Dict[int, str]:
       ... 


class __InletType:
    None
    INLETNULL : int
    DIRECT : int
    BATCH : int
    CHROMATOGRAPHY : int
    PARTICLEBEAM : int
    MEMBRANESEPARATOR : int
    OPENSPLIT : int
    JETSEPARATOR : int
    SEPTUM : int
    RESERVOIR : int
    MOVINGBELT : int
    MOVINGWIRE : int
    FLOWINJECTIONANALYSIS : int
    ELECTROSPRAYINLET : int
    THERMOSPRAYINLET : int
    INFUSION : int
    CONTINUOUSFLOWFASTATOMBOMBARDMENT : int
    INDUCTIVELYCOUPLEDPLASMA : int
    MEMBRANE : int
    NANOSPRAY : int
    SIZE_OF_INLETTYPE : int

    def getMapping(self) -> Dict[int, str]:
       ... 


class __IonizationMethod:
    None
    IONMETHODNULL : int
    ESI : int
    EI : int
    CI : int
    FAB : int
    TSP : int
    LD : int
    FD : int
    FI : int
    PD : int
    SI : int
    TI : int
    API : int
    ISI : int
    CID : int
    CAD : int
    HN : int
    APCI : int
    APPI : int
    ICP : int
    NESI : int
    MESI : int
    SELDI : int
    SEND : int
    FIB : int
    MALDI : int
    MPI : int
    DI : int
    FA : int
    FII : int
    GD_MS : int
    NICI : int
    NRMS : int
    PI : int
    PYMS : int
    REMPI : int
    AI : int
    ASI : int
    AD : int
    AUI : int
    CEI : int
    CHEMI : int
    DISSI : int
    LSI : int
    PEI : int
    SOI : int
    SPI : int
    SUI : int
    VI : int
    AP_MALDI : int
    SILI : int
    SALDI : int
    SIZE_OF_IONIZATIONMETHOD : int

    def getMapping(self) -> Dict[int, str]:
       ... 


class __PeakMassType:
    None
    MONOISOTOPIC : int
    AVERAGE : int
    SIZE_OF_PEAKMASSTYPE : int

    def getMapping(self) -> Dict[int, str]:
       ... 


class __Polarity:
    None
    POLNULL : int
    POSITIVE : int
    NEGATIVE : int
    SIZE_OF_POLARITY : int

    def getMapping(self) -> Dict[int, str]:
       ... 

