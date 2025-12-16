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

def __static_File_getExecutablePath() -> Union[bytes, str, String]:
    """
    Cython signature: String getExecutablePath()
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

def __static_File_isDirectory(path: Union[bytes, str, String] ) -> bool:
    """
    Cython signature: bool isDirectory(String path)
    """
    ...

def __static_ExperimentalDesignFile_load(tsv_file: Union[bytes, str, String] , in_1: bool ) -> ExperimentalDesign:
    """
    Cython signature: ExperimentalDesign load(const String & tsv_file, bool)
    """
    ...

def mergeFAIMSFeatures(feature_map: FeatureMap , max_rt_diff: float , max_mz_diff: float ) -> None:
    """
    Cython signature: void mergeFAIMSFeatures(FeatureMap & feature_map, double max_rt_diff, double max_mz_diff)
        Merge FAIMS features that represent the same analyte detected at different CV values.
    """
    ...

def mergeOverlappingFeatures(feature_map: FeatureMap , max_rt_diff: float , max_mz_diff: float , require_same_charge: bool , require_same_im: bool , intensity_mode: int , write_meta_values: bool ) -> None:
    """
    Cython signature: void mergeOverlappingFeatures(FeatureMap & feature_map, double max_rt_diff, double max_mz_diff, bool require_same_charge, bool require_same_im, MergeIntensityMode intensity_mode, bool write_meta_values)
        Merge overlapping features based on centroid distances.
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


class AAIndex:
    """
    Cython implementation of _AAIndex

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1AAIndex.html>`_
    """
    
    def aliphatic(self, aa: bytes ) -> float:
        """
        Cython signature: double aliphatic(char aa)
        """
        ...
    
    def acidic(self, aa: bytes ) -> float:
        """
        Cython signature: double acidic(char aa)
        """
        ...
    
    def basic(self, aa: bytes ) -> float:
        """
        Cython signature: double basic(char aa)
        """
        ...
    
    def polar(self, aa: bytes ) -> float:
        """
        Cython signature: double polar(char aa)
        """
        ...
    
    def getKHAG800101(self, aa: bytes ) -> float:
        """
        Cython signature: double getKHAG800101(char aa)
        """
        ...
    
    def getVASM830103(self, aa: bytes ) -> float:
        """
        Cython signature: double getVASM830103(char aa)
        """
        ...
    
    def getNADH010106(self, aa: bytes ) -> float:
        """
        Cython signature: double getNADH010106(char aa)
        """
        ...
    
    def getNADH010107(self, aa: bytes ) -> float:
        """
        Cython signature: double getNADH010107(char aa)
        """
        ...
    
    def getWILM950102(self, aa: bytes ) -> float:
        """
        Cython signature: double getWILM950102(char aa)
        """
        ...
    
    def getROBB760107(self, aa: bytes ) -> float:
        """
        Cython signature: double getROBB760107(char aa)
        """
        ...
    
    def getOOBM850104(self, aa: bytes ) -> float:
        """
        Cython signature: double getOOBM850104(char aa)
        """
        ...
    
    def getFAUJ880111(self, aa: bytes ) -> float:
        """
        Cython signature: double getFAUJ880111(char aa)
        """
        ...
    
    def getFINA770101(self, aa: bytes ) -> float:
        """
        Cython signature: double getFINA770101(char aa)
        """
        ...
    
    def getARGP820102(self, aa: bytes ) -> float:
        """
        Cython signature: double getARGP820102(char aa)
        """
        ...
    
    def calculateGB(self, seq: AASequence , T: float ) -> float:
        """
        Cython signature: double calculateGB(AASequence & seq, double T)
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


class Acquisition:
    """
    Cython implementation of _Acquisition

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1Acquisition.html>`_
      -- Inherits from ['MetaInfoInterface']
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void Acquisition()
        """
        ...
    
    @overload
    def __init__(self, in_0: Acquisition ) -> None:
        """
        Cython signature: void Acquisition(Acquisition &)
        """
        ...
    
    def getIdentifier(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getIdentifier()
        """
        ...
    
    def setIdentifier(self, identifier: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setIdentifier(const String & identifier)
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
    
    def __richcmp__(self, other: Acquisition, op: int) -> Any:
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


class CVTermListInterface:
    """
    Cython implementation of _CVTermListInterface

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1CVTermListInterface.html>`_
      -- Inherits from ['MetaInfoInterface']
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void CVTermListInterface()
        """
        ...
    
    @overload
    def __init__(self, in_0: CVTermListInterface ) -> None:
        """
        Cython signature: void CVTermListInterface(CVTermListInterface &)
        """
        ...
    
    @overload
    def replaceCVTerms(self, cv_terms: Dict[bytes,List[CVTerm]] ) -> None:
        """
        Cython signature: void replaceCVTerms(libcpp_map[String,libcpp_vector[CVTerm]] & cv_terms)
        """
        ...
    
    @overload
    def replaceCVTerms(self, cv_terms: List[CVTerm] , accession: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void replaceCVTerms(libcpp_vector[CVTerm] & cv_terms, const String & accession)
        """
        ...
    
    def setCVTerms(self, terms: List[CVTerm] ) -> None:
        """
        Cython signature: void setCVTerms(libcpp_vector[CVTerm] & terms)
        """
        ...
    
    def replaceCVTerm(self, cv_term: CVTerm ) -> None:
        """
        Cython signature: void replaceCVTerm(CVTerm & cv_term)
        """
        ...
    
    def consumeCVTerms(self, cv_term_map: Dict[bytes,List[CVTerm]] ) -> None:
        """
        Cython signature: void consumeCVTerms(libcpp_map[String,libcpp_vector[CVTerm]] & cv_term_map)
        Merges the given map into the member map, no duplicate checking
        """
        ...
    
    def getCVTerms(self) -> Dict[bytes,List[CVTerm]]:
        """
        Cython signature: libcpp_map[String,libcpp_vector[CVTerm]] getCVTerms()
        """
        ...
    
    def addCVTerm(self, term: CVTerm ) -> None:
        """
        Cython signature: void addCVTerm(CVTerm & term)
        Adds a CV term
        """
        ...
    
    def hasCVTerm(self, accession: Union[bytes, str, String] ) -> bool:
        """
        Cython signature: bool hasCVTerm(const String & accession)
        Checks whether the term has a value
        """
        ...
    
    def empty(self) -> bool:
        """
        Cython signature: bool empty()
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
    
    def __richcmp__(self, other: CVTermListInterface, op: int) -> Any:
        ... 


class CachedMzMLHandler:
    """
    Cython implementation of _CachedMzMLHandler

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS::Internal_1_1CachedMzMLHandler.html>`_
      -- Inherits from ['ProgressLogger']
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void CachedMzMLHandler()
        An internal class that handles single spectra and chromatograms
        """
        ...
    
    @overload
    def __init__(self, in_0: CachedMzMLHandler ) -> None:
        """
        Cython signature: void CachedMzMLHandler(CachedMzMLHandler &)
        """
        ...
    
    def writeMemdump(self, exp: MSExperiment , out: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void writeMemdump(MSExperiment exp, String out)
        Write complete spectra as a dump to the disk
        """
        ...
    
    def writeMetadata(self, exp: MSExperiment , out_meta: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void writeMetadata(MSExperiment exp, String out_meta)
        Write only the meta data of an MSExperiment
        """
        ...
    
    def readMemdump(self, exp: MSExperiment , filename: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void readMemdump(MSExperiment exp, String filename)
        Read all spectra from a dump from the disk
        """
        ...
    
    def getSpectraIndex(self) -> List[streampos]:
        """
        Cython signature: libcpp_vector[streampos] getSpectraIndex()
        """
        ...
    
    def getChromatogramIndex(self) -> List[streampos]:
        """
        Cython signature: libcpp_vector[streampos] getChromatogramIndex()
        """
        ...
    
    def createMemdumpIndex(self, filename: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void createMemdumpIndex(String filename)
        Create an index on the location of all the spectra and chromatograms
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


class ChargedIndexSet:
    """
    Cython implementation of _ChargedIndexSet

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1ChargedIndexSet.html>`_
    """
    
    charge: int
    
    def __init__(self) -> None:
        """
        Cython signature: void ChargedIndexSet()
        Index set with associated charge estimate
        """
        ... 


class ChromatogramPeak:
    """
    Cython implementation of _ChromatogramPeak

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS::ChromatogramPeak_1_1ChromatogramPeak.html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void ChromatogramPeak()
        A 1-dimensional raw data point or peak for chromatograms
        """
        ...
    
    @overload
    def __init__(self, in_0: ChromatogramPeak ) -> None:
        """
        Cython signature: void ChromatogramPeak(ChromatogramPeak &)
        """
        ...
    
    def getIntensity(self) -> float:
        """
        Cython signature: double getIntensity()
        Returns the intensity
        """
        ...
    
    def setIntensity(self, in_0: float ) -> None:
        """
        Cython signature: void setIntensity(double)
        Sets the intensity
        """
        ...
    
    def getRT(self) -> float:
        """
        Cython signature: double getRT()
        Returns the retention time
        """
        ...
    
    def setRT(self, in_0: float ) -> None:
        """
        Cython signature: void setRT(double)
        Sets retention time
        """
        ...
    
    def getPos(self) -> float:
        """
        Cython signature: double getPos()
        Alias for getRT()
        """
        ...
    
    def setPos(self, in_0: float ) -> None:
        """
        Cython signature: void setPos(double)
        Alias for setRT()
        """
        ...
    
    def __richcmp__(self, other: ChromatogramPeak, op: int) -> Any:
        ... 


class ChromatogramSettings:
    """
    Cython implementation of _ChromatogramSettings

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1ChromatogramSettings.html>`_
      -- Inherits from ['MetaInfoInterface']

    Description of the chromatogram settings, provides meta-information
    about a single chromatogram.
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void ChromatogramSettings()
        """
        ...
    
    @overload
    def __init__(self, in_0: ChromatogramSettings ) -> None:
        """
        Cython signature: void ChromatogramSettings(ChromatogramSettings &)
        """
        ...
    
    def getProduct(self) -> Product:
        """
        Cython signature: Product getProduct()
        Returns the product ion
        """
        ...
    
    def setProduct(self, p: Product ) -> None:
        """
        Cython signature: void setProduct(Product p)
        Sets the product ion
        """
        ...
    
    def getNativeID(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getNativeID()
        Returns the native identifier for the spectrum, used by the acquisition software.
        """
        ...
    
    def setNativeID(self, native_id: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setNativeID(String native_id)
        Sets the native identifier for the spectrum, used by the acquisition software.
        """
        ...
    
    def getComment(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getComment()
        Returns the free-text comment
        """
        ...
    
    def setComment(self, comment: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setComment(String comment)
        Sets the free-text comment
        """
        ...
    
    def getInstrumentSettings(self) -> InstrumentSettings:
        """
        Cython signature: InstrumentSettings getInstrumentSettings()
        Returns the instrument settings of the current spectrum
        """
        ...
    
    def setInstrumentSettings(self, instrument_settings: InstrumentSettings ) -> None:
        """
        Cython signature: void setInstrumentSettings(InstrumentSettings instrument_settings)
        Sets the instrument settings of the current spectrum
        """
        ...
    
    def getAcquisitionInfo(self) -> AcquisitionInfo:
        """
        Cython signature: AcquisitionInfo getAcquisitionInfo()
        Returns the acquisition info
        """
        ...
    
    def setAcquisitionInfo(self, acquisition_info: AcquisitionInfo ) -> None:
        """
        Cython signature: void setAcquisitionInfo(AcquisitionInfo acquisition_info)
        Sets the acquisition info
        """
        ...
    
    def getSourceFile(self) -> SourceFile:
        """
        Cython signature: SourceFile getSourceFile()
        Returns the source file
        """
        ...
    
    def setSourceFile(self, source_file: SourceFile ) -> None:
        """
        Cython signature: void setSourceFile(SourceFile source_file)
        Sets the source file
        """
        ...
    
    def getPrecursor(self) -> Precursor:
        """
        Cython signature: Precursor getPrecursor()
        Returns the precursors
        """
        ...
    
    def setPrecursor(self, precursor: Precursor ) -> None:
        """
        Cython signature: void setPrecursor(Precursor precursor)
        Sets the precursors
        """
        ...
    
    def getDataProcessing(self) -> List[DataProcessing]:
        """
        Cython signature: libcpp_vector[shared_ptr[DataProcessing]] getDataProcessing()
        Returns the description of the applied processing
        """
        ...
    
    def setDataProcessing(self, in_0: List[DataProcessing] ) -> None:
        """
        Cython signature: void setDataProcessing(libcpp_vector[shared_ptr[DataProcessing]])
        Sets the description of the applied processing
        """
        ...
    
    def setChromatogramType(self, type: int ) -> None:
        """
        Cython signature: void setChromatogramType(ChromatogramType type)
        Sets the chromatogram type
        """
        ...
    
    def getChromatogramType(self) -> int:
        """
        Cython signature: ChromatogramType getChromatogramType()
        Get the chromatogram type
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
    
    def __richcmp__(self, other: ChromatogramSettings, op: int) -> Any:
        ...
    ChromatogramType : __ChromatogramType 


class ClusteringGrid:
    """
    Cython implementation of _ClusteringGrid

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1ClusteringGrid.html>`_
    """
    
    @overload
    def __init__(self, grid_spacing_x: List[float] , grid_spacing_y: List[float] ) -> None:
        """
        Cython signature: void ClusteringGrid(libcpp_vector[double] & grid_spacing_x, libcpp_vector[double] & grid_spacing_y)
        """
        ...
    
    @overload
    def __init__(self, in_0: ClusteringGrid ) -> None:
        """
        Cython signature: void ClusteringGrid(ClusteringGrid &)
        """
        ...
    
    def getGridSpacingX(self) -> List[float]:
        """
        Cython signature: libcpp_vector[double] getGridSpacingX()
        """
        ...
    
    def getGridSpacingY(self) -> List[float]:
        """
        Cython signature: libcpp_vector[double] getGridSpacingY()
        """
        ...
    
    def addCluster(self, cell_index: List[int, int] , cluster_index: int ) -> None:
        """
        Cython signature: void addCluster(libcpp_pair[int,int] cell_index, int & cluster_index)
        Adds a cluster to this grid cell
        """
        ...
    
    def removeCluster(self, cell_index: List[int, int] , cluster_index: int ) -> None:
        """
        Cython signature: void removeCluster(libcpp_pair[int,int] cell_index, int & cluster_index)
        Removes a cluster from this grid cell and removes the cell if no other cluster left
        """
        ...
    
    def removeAllClusters(self) -> None:
        """
        Cython signature: void removeAllClusters()
        Removes all clusters from this grid (and hence all cells)
        """
        ...
    
    def getIndex(self, position: Union[Sequence[int], Sequence[float]] ) -> List[int, int]:
        """
        Cython signature: libcpp_pair[int,int] getIndex(DPosition2 position)
        """
        ...
    
    def isNonEmptyCell(self, cell_index: List[int, int] ) -> bool:
        """
        Cython signature: bool isNonEmptyCell(libcpp_pair[int,int] cell_index)
        Checks if there are clusters at this cell index
        """
        ...
    
    def getCellCount(self) -> int:
        """
        Cython signature: int getCellCount()
        Returns number of grid cells occupied by one or more clusters
        """
        ... 


class ConsensusIDAlgorithmPEPMatrix:
    """
    Cython implementation of _ConsensusIDAlgorithmPEPMatrix

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1ConsensusIDAlgorithmPEPMatrix.html>`_
      -- Inherits from ['ConsensusIDAlgorithmSimilarity']
    """
    
    def __init__(self) -> None:
        """
        Cython signature: void ConsensusIDAlgorithmPEPMatrix()
        """
        ...
    
    def apply(self, ids: PeptideIdentificationList , number_of_runs: int ) -> None:
        """
        Cython signature: void apply(PeptideIdentificationList & ids, size_t number_of_runs)
        Calculates the consensus ID for a set of peptide identifications of one spectrum or (consensus) feature
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


class ConsensusMapNormalizerAlgorithmQuantile:
    """
    Cython implementation of _ConsensusMapNormalizerAlgorithmQuantile

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1ConsensusMapNormalizerAlgorithmQuantile.html>`_
    """
    
    def __init__(self) -> None:
        """
        Cython signature: void ConsensusMapNormalizerAlgorithmQuantile()
        """
        ...
    
    def normalizeMaps(self, input_map: ConsensusMap ) -> None:
        """
        Cython signature: void normalizeMaps(ConsensusMap & input_map)
        """
        ...
    
    def resample(self, data_in: List[float] , data_out: List[float] , n_resampling_points: int ) -> None:
        """
        Cython signature: void resample(libcpp_vector[double] & data_in, libcpp_vector[double] & data_out, unsigned int n_resampling_points)
        Resamples data_in and writes the results to data_out
        """
        ...
    
    def extractIntensityVectors(self, map_: ConsensusMap , out_intensities: List[List[float]] ) -> None:
        """
        Cython signature: void extractIntensityVectors(ConsensusMap & map_, libcpp_vector[libcpp_vector[double]] & out_intensities)
        Extracts the intensities of the features of the different maps
        """
        ...
    
    def setNormalizedIntensityValues(self, feature_ints: List[List[float]] , map_: ConsensusMap ) -> None:
        """
        Cython signature: void setNormalizedIntensityValues(libcpp_vector[libcpp_vector[double]] & feature_ints, ConsensusMap & map_)
        Writes the intensity values in feature_ints to the corresponding features in map
        """
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


class DigestionEnzymeRNA:
    """
    Cython implementation of _DigestionEnzymeRNA

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1DigestionEnzymeRNA.html>`_
      -- Inherits from ['DigestionEnzyme']

    Representation of a digestion enzyme for RNA (RNase)
    
    The cutting sites of these enzymes are defined using two different mechanisms:
    First, a single regular expression that is applied to strings of unmodified RNA sequence and defines cutting sites via zero-length matches (using lookahead/lookbehind assertions).
    This is the same mechanism that is used for proteases (see ProteaseDigestion).
    However, due to the complex notation involved, this approach is not practical for modification-aware digestion.
    Thus, the second mechanism uses two regular expressions ("cuts after"/"cuts before"), which are applied to the short codes (e.g. "m6A") of sequential ribonucleotides.
    If both expressions match, then there is a cutting site between the two ribonucleotides.
    
    There is support for terminal (5'/3') modifications that may be generated on fragments as a result of RNase cleavage.
    A typical example is 3'-phosphate, resulting from cleavage of the phosphate backbone.
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void DigestionEnzymeRNA()
        """
        ...
    
    @overload
    def __init__(self, in_0: DigestionEnzymeRNA ) -> None:
        """
        Cython signature: void DigestionEnzymeRNA(DigestionEnzymeRNA &)
        """
        ...
    
    def setCutsAfterRegEx(self, value: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setCutsAfterRegEx(String value)
        Sets the "cuts after ..." regular expression
        """
        ...
    
    def getCutsAfterRegEx(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getCutsAfterRegEx()
        Returns the "cuts after ..." regular expression
        """
        ...
    
    def setCutsBeforeRegEx(self, value: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setCutsBeforeRegEx(String value)
        Sets the "cuts before ..." regular expression
        """
        ...
    
    def getCutsBeforeRegEx(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getCutsBeforeRegEx()
        Returns the "cuts before ..." regular expression
        """
        ...
    
    def setThreePrimeGain(self, value: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setThreePrimeGain(String value)
        Sets the 3' gain
        """
        ...
    
    def setFivePrimeGain(self, value: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setFivePrimeGain(String value)
        Sets the 5' gain
        """
        ...
    
    def getThreePrimeGain(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getThreePrimeGain()
        Returns the 3' gain
        """
        ...
    
    def getFivePrimeGain(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getFivePrimeGain()
        Returns the 5' gain
        """
        ...
    
    def setName(self, name: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setName(const String & name)
        Sets the name of the enzyme
        """
        ...
    
    def getName(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getName()
        Returns the name of the enzyme
        """
        ...
    
    def setSynonyms(self, synonyms: Set[bytes] ) -> None:
        """
        Cython signature: void setSynonyms(libcpp_set[String] & synonyms)
        Sets the synonyms
        """
        ...
    
    def addSynonym(self, synonym: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void addSynonym(const String & synonym)
        Adds a synonym
        """
        ...
    
    def getSynonyms(self) -> Set[bytes]:
        """
        Cython signature: libcpp_set[String] getSynonyms()
        Returns the synonyms
        """
        ...
    
    def setRegEx(self, cleavage_regex: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setRegEx(const String & cleavage_regex)
        Sets the cleavage regex
        """
        ...
    
    def getRegEx(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getRegEx()
        Returns the cleavage regex
        """
        ...
    
    def setRegExDescription(self, value: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setRegExDescription(const String & value)
        Sets the regex description
        """
        ...
    
    def getRegExDescription(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getRegExDescription()
        Returns the regex description
        """
        ...
    
    def setValueFromFile(self, key: Union[bytes, str, String] , value: Union[bytes, str, String] ) -> bool:
        """
        Cython signature: bool setValueFromFile(String key, String value)
        Sets the value of a member variable based on an entry from an input file
        """
        ...
    
    def __richcmp__(self, other: DigestionEnzymeRNA, op: int) -> Any:
        ... 


class ExperimentalDesignFile:
    """
    Cython implementation of _ExperimentalDesignFile

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1ExperimentalDesignFile.html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void ExperimentalDesignFile()
        """
        ...
    
    @overload
    def __init__(self, in_0: ExperimentalDesignFile ) -> None:
        """
        Cython signature: void ExperimentalDesignFile(ExperimentalDesignFile &)
        """
        ...
    
    load: __static_ExperimentalDesignFile_load 


class FASTAEntry:
    """
    Cython implementation of _FASTAEntry

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1FASTAEntry.html>`_
    """
    
    identifier: Union[bytes, str, String]
    
    description: Union[bytes, str, String]
    
    sequence: Union[bytes, str, String]
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void FASTAEntry()
        """
        ...
    
    @overload
    def __init__(self, in_0: FASTAEntry ) -> None:
        """
        Cython signature: void FASTAEntry(FASTAEntry)
        """
        ...
    
    def headerMatches(self, rhs: FASTAEntry ) -> bool:
        """
        Cython signature: bool headerMatches(const FASTAEntry & rhs)
        """
        ...
    
    def sequenceMatches(self, rhs: FASTAEntry ) -> bool:
        """
        Cython signature: bool sequenceMatches(const FASTAEntry & rhs)
        """
        ... 


class FASTAFile:
    """
    Cython implementation of _FASTAFile

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1FASTAFile.html>`_
    """
    
    def __init__(self) -> None:
        """
        Cython signature: void FASTAFile()
        This class serves for reading in and writing FASTA files
        """
        ...
    
    def load(self, filename: Union[bytes, str, String] , data: List[FASTAEntry] ) -> None:
        """
        Cython signature: void load(const String & filename, libcpp_vector[FASTAEntry] & data)
        Loads a FASTA file given by 'filename' and stores the information in 'data'
        """
        ...
    
    def store(self, filename: Union[bytes, str, String] , data: List[FASTAEntry] ) -> None:
        """
        Cython signature: void store(const String & filename, libcpp_vector[FASTAEntry] & data)
        Stores the data given by 'data' at the file 'filename'
        """
        ...
    
    def readStart(self, filename: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void readStart(const String & filename)
        Prepares a FASTA file given by 'filename' for streamed reading using readNext()
        
        :raises:
            Exception:FileNotFound is thrown if the file does not exists
        :raises:
            Exception:ParseError is thrown if the file does not suit to the standard
        """
        ...
    
    def readNext(self, protein: FASTAEntry ) -> bool:
        """
        Cython signature: bool readNext(FASTAEntry & protein)
        Reads the next FASTA entry from file
        
        If you want to read all entries in one go, use load()
        
        :return: true if entry was read; false if eof was reached
        :raises:
            Exception:FileNotFound is thrown if the file does not exists
        :raises:
            Exception:ParseError is thrown if the file does not suit to the standard
        """
        ...
    
    def atEnd(self) -> bool:
        """
        Cython signature: bool atEnd()
        Boolean function to check if streams is at end of file
        """
        ...
    
    def writeStart(self, filename: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void writeStart(const String & filename)
        Prepares a FASTA file given by 'filename' for streamed writing using writeNext()
        
        :raises:
            Exception:UnableToCreateFile is thrown if the process is not able to write to the file (disk full?)
        """
        ...
    
    def writeNext(self, protein: FASTAEntry ) -> None:
        """
        Cython signature: void writeNext(const FASTAEntry & protein)
        Stores the data given by `protein`. Call writeStart() once before calling writeNext()
        
        Call writeEnd() when done to close the file!
        
        :raises:
            Exception:UnableToCreateFile is thrown if the process is not able to write to the file (disk full?)
        """
        ...
    
    def writeEnd(self) -> None:
        """
        Cython signature: void writeEnd()
        Closes the file (flush). Called implicitly when FASTAFile object does out of scope
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


class FeatureOverlapFilter:
    """
    Cython implementation of _FeatureOverlapFilter

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1FeatureOverlapFilter.html>`_

    Filters and merges overlapping features in a FeatureMap.
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void FeatureOverlapFilter()
        """
        ...
    
    @overload
    def __init__(self, in_0: FeatureOverlapFilter ) -> None:
        """
        Cython signature: void FeatureOverlapFilter(FeatureOverlapFilter &)
        """
        ...
    MergeIntensityMode : __MergeIntensityMode 


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


class InterpolationModel:
    """
    Cython implementation of _InterpolationModel

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1InterpolationModel.html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void InterpolationModel()
        Abstract class for 1D-models that are approximated using linear interpolation
        """
        ...
    
    @overload
    def __init__(self, in_0: InterpolationModel ) -> None:
        """
        Cython signature: void InterpolationModel(InterpolationModel &)
        """
        ...
    
    def getIntensity(self, coord: float ) -> float:
        """
        Cython signature: double getIntensity(double coord)
        Access model predicted intensity at position 'pos'
        """
        ...
    
    def getScalingFactor(self) -> float:
        """
        Cython signature: double getScalingFactor()
        Returns the interpolation class
        """
        ...
    
    def setOffset(self, offset: float ) -> None:
        """
        Cython signature: void setOffset(double offset)
        Sets the offset of the model
        """
        ...
    
    def getCenter(self) -> float:
        """
        Cython signature: double getCenter()
        Returns the "center" of the model, particular definition (depends on the derived model)
        """
        ...
    
    def setSamples(self) -> None:
        """
        Cython signature: void setSamples()
        Sets sample/supporting points of interpolation wrt params
        """
        ...
    
    def setInterpolationStep(self, interpolation_step: float ) -> None:
        """
        Cython signature: void setInterpolationStep(double interpolation_step)
        Sets the interpolation step for the linear interpolation of the model
        """
        ...
    
    def setScalingFactor(self, scaling: float ) -> None:
        """
        Cython signature: void setScalingFactor(double scaling)
        Sets the scaling factor of the model
        """
        ...
    
    def getInterpolation(self) -> LinearInterpolation:
        """
        Cython signature: LinearInterpolation getInterpolation()
        Returns the interpolation class
        """
        ... 


class IsobaricChannelInformation:
    """
    Cython implementation of _IsobaricChannelInformation

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS::IsobaricQuantitationMethod_1_1IsobaricChannelInformation.html>`_
    """
    
    name: Union[bytes, str, String]
    
    id: int
    
    description: Union[bytes, str, String]
    
    center: float
    
    affected_channels: List[int]
    
    @overload
    def __init__(self, name: Union[bytes, str, String] , id_: int , description: Union[bytes, str, String] , center: float , affected_channels: List[int] ) -> None:
        """
        Cython signature: void IsobaricChannelInformation(String name, int id_, String description, double center, libcpp_vector[int] affected_channels)
        """
        ...
    
    @overload
    def __init__(self, in_0: IsobaricChannelInformation ) -> None:
        """
        Cython signature: void IsobaricChannelInformation(IsobaricChannelInformation &)
        """
        ... 


class IsobaricIsotopeCorrector:
    """
    Cython implementation of _IsobaricIsotopeCorrector

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1IsobaricIsotopeCorrector.html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void IsobaricIsotopeCorrector()
        """
        ...
    
    @overload
    def __init__(self, in_0: IsobaricIsotopeCorrector ) -> None:
        """
        Cython signature: void IsobaricIsotopeCorrector(IsobaricIsotopeCorrector &)
        """
        ...
    
    @overload
    def correctIsotopicImpurities(self, consensus_map_in: ConsensusMap , consensus_map_out: ConsensusMap , quant_method: ItraqEightPlexQuantitationMethod ) -> IsobaricQuantifierStatistics:
        """
        Cython signature: IsobaricQuantifierStatistics correctIsotopicImpurities(ConsensusMap & consensus_map_in, ConsensusMap & consensus_map_out, ItraqEightPlexQuantitationMethod * quant_method)
        """
        ...
    
    @overload
    def correctIsotopicImpurities(self, consensus_map_in: ConsensusMap , consensus_map_out: ConsensusMap , quant_method: ItraqFourPlexQuantitationMethod ) -> IsobaricQuantifierStatistics:
        """
        Cython signature: IsobaricQuantifierStatistics correctIsotopicImpurities(ConsensusMap & consensus_map_in, ConsensusMap & consensus_map_out, ItraqFourPlexQuantitationMethod * quant_method)
        """
        ...
    
    @overload
    def correctIsotopicImpurities(self, consensus_map_in: ConsensusMap , consensus_map_out: ConsensusMap , quant_method: TMTSixPlexQuantitationMethod ) -> IsobaricQuantifierStatistics:
        """
        Cython signature: IsobaricQuantifierStatistics correctIsotopicImpurities(ConsensusMap & consensus_map_in, ConsensusMap & consensus_map_out, TMTSixPlexQuantitationMethod * quant_method)
        """
        ...
    
    @overload
    def correctIsotopicImpurities(self, consensus_map_in: ConsensusMap , consensus_map_out: ConsensusMap , quant_method: TMTTenPlexQuantitationMethod ) -> IsobaricQuantifierStatistics:
        """
        Cython signature: IsobaricQuantifierStatistics correctIsotopicImpurities(ConsensusMap & consensus_map_in, ConsensusMap & consensus_map_out, TMTTenPlexQuantitationMethod * quant_method)
        """
        ... 


class IsotopeCluster:
    """
    Cython implementation of _IsotopeCluster

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1IsotopeCluster.html>`_
    """
    
    peaks: ChargedIndexSet
    
    scans: List[int]
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void IsotopeCluster()
        Stores information about an isotopic cluster (i.e. potential peptide charge variants)
        """
        ...
    
    @overload
    def __init__(self, in_0: IsotopeCluster ) -> None:
        """
        Cython signature: void IsotopeCluster(IsotopeCluster &)
        """
        ... 


class ItraqEightPlexQuantitationMethod:
    """
    Cython implementation of _ItraqEightPlexQuantitationMethod

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1ItraqEightPlexQuantitationMethod.html>`_
      -- Inherits from ['IsobaricQuantitationMethod']
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void ItraqEightPlexQuantitationMethod()
        iTRAQ 8 plex quantitation to be used with the IsobaricQuantitation
        """
        ...
    
    @overload
    def __init__(self, in_0: ItraqEightPlexQuantitationMethod ) -> None:
        """
        Cython signature: void ItraqEightPlexQuantitationMethod(ItraqEightPlexQuantitationMethod &)
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


class KroenikFile:
    """
    Cython implementation of _KroenikFile

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1KroenikFile.html>`_

    File adapter for Kroenik (HardKloer sibling) files
    
    The first line is the header and contains the column names:
    File,  First Scan,  Last Scan,  Num of Scans,  Charge,  Monoisotopic Mass,  Base Isotope Peak,  Best Intensity,  Summed Intensity,  First RTime,  Last RTime,  Best RTime,  Best Correlation,  Modifications
    
    Every subsequent line is a feature
    
    All properties in the file are converted to Feature properties, whereas "First Scan", "Last Scan", "Num of Scans" and "Modifications" are stored as
    metavalues with the following names "FirstScan", "LastScan", "NumOfScans" and "AveragineModifications"
    
    The width in m/z of the overall convex hull of each feature is set to 3 Th in lack of a value provided by the Kroenik file
    """
    
    def __init__(self) -> None:
        """
        Cython signature: void KroenikFile()
        """
        ...
    
    def store(self, filename: Union[bytes, str, String] , spectrum: MSSpectrum ) -> None:
        """
        Cython signature: void store(String filename, MSSpectrum & spectrum)
        Stores a MSExperiment into a Kroenik file
        """
        ...
    
    def load(self, filename: Union[bytes, str, String] , feature_map: FeatureMap ) -> None:
        """
        Cython signature: void load(String filename, FeatureMap & feature_map)
        Loads a Kroenik file into a featureXML
        
        The content of the file is stored in `features`
        
        :raises:
          Exception: FileNotFound is thrown if the file could not be opened
        :raises:
          Exception: ParseError is thrown if an error occurs during parsing
        """
        ... 


class MSstatsFile:
    """
    Cython implementation of _MSstatsFile

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1MSstatsFile.html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void MSstatsFile()
        """
        ...
    
    @overload
    def __init__(self, in_0: MSstatsFile ) -> None:
        """
        Cython signature: void MSstatsFile(MSstatsFile &)
        """
        ...
    
    def storeLFQ(self, filename: String , consensus_map: ConsensusMap , design: ExperimentalDesign , reannotate_filenames: List[bytes] , is_isotope_label_type: bool , bioreplicate: String , condition: String , retention_time_summarization_method: String ) -> None:
        """
        Cython signature: void storeLFQ(String & filename, ConsensusMap & consensus_map, ExperimentalDesign & design, StringList & reannotate_filenames, bool is_isotope_label_type, String & bioreplicate, String & condition, String & retention_time_summarization_method)
        Store label free experiment (MSstats)
        """
        ...
    
    def storeISO(self, filename: String , consensus_map: ConsensusMap , design: ExperimentalDesign , reannotate_filenames: List[bytes] , bioreplicate: String , condition: String , mixture: String , retention_time_summarization_method: String ) -> None:
        """
        Cython signature: void storeISO(String & filename, ConsensusMap & consensus_map, ExperimentalDesign & design, StringList & reannotate_filenames, String & bioreplicate, String & condition, String & mixture, String & retention_time_summarization_method)
        Store isobaric experiment (MSstatsTMT)
        """
        ... 


class MascotGenericFile:
    """
    Cython implementation of _MascotGenericFile

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1MascotGenericFile.html>`_
      -- Inherits from ['ProgressLogger', 'DefaultParamHandler']
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void MascotGenericFile()
        """
        ...
    
    @overload
    def __init__(self, in_0: MascotGenericFile ) -> None:
        """
        Cython signature: void MascotGenericFile(MascotGenericFile &)
        """
        ...
    
    def store(self, filename: Union[bytes, str, String] , experiment: MSExperiment ) -> None:
        """
        Cython signature: void store(const String & filename, MSExperiment & experiment)
        """
        ...
    
    def load(self, filename: Union[bytes, str, String] , exp: MSExperiment ) -> None:
        """
        Cython signature: void load(const String & filename, MSExperiment & exp)
        Loads a Mascot Generic File into a PeakMap
        
        
        :param filename: File name which the map should be read from
        :param exp: The map which is filled with the data from the given file
        :raises:
          Exception: FileNotFound is thrown if the given file could not be found
        """
        ...
    
    def getHTTPPeakListEnclosure(self, filename: Union[bytes, str, String] ) -> List[Union[bytes, str, String], Union[bytes, str, String]]:
        """
        Cython signature: libcpp_pair[String,String] getHTTPPeakListEnclosure(const String & filename)
        Enclosing Strings of the peak list body for HTTP submission\n
        
        Can be used to embed custom content into HTTP submission (when writing only the MGF header in HTTP format and then
        adding the peaks (in whatever format, e.g. mzXML) enclosed in this body
        The `filename` can later be found in the Mascot response
        """
        ...
    
    def updateMembers_(self) -> None:
        """
        Cython signature: void updateMembers_()
        Docu in base class
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


class MassAnalyzer:
    """
    Cython implementation of _MassAnalyzer

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1MassAnalyzer.html>`_
      -- Inherits from ['MetaInfoInterface']
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void MassAnalyzer()
        """
        ...
    
    @overload
    def __init__(self, in_0: MassAnalyzer ) -> None:
        """
        Cython signature: void MassAnalyzer(MassAnalyzer &)
        """
        ...
    
    def getType(self) -> int:
        """
        Cython signature: AnalyzerType getType()
        Returns the analyzer type
        """
        ...
    
    def setType(self, type: int ) -> None:
        """
        Cython signature: void setType(AnalyzerType type)
        Sets the analyzer type
        """
        ...
    
    def getResolutionMethod(self) -> int:
        """
        Cython signature: ResolutionMethod getResolutionMethod()
        Returns the method used for determination of the resolution
        """
        ...
    
    def setResolutionMethod(self, resolution_method: int ) -> None:
        """
        Cython signature: void setResolutionMethod(ResolutionMethod resolution_method)
        Sets the method used for determination of the resolution
        """
        ...
    
    def getResolutionType(self) -> int:
        """
        Cython signature: ResolutionType getResolutionType()
        Returns the resolution type
        """
        ...
    
    def setResolutionType(self, resolution_type: int ) -> None:
        """
        Cython signature: void setResolutionType(ResolutionType resolution_type)
        Sets the resolution type
        """
        ...
    
    def getScanDirection(self) -> int:
        """
        Cython signature: ScanDirection getScanDirection()
        Returns the direction of scanning
        """
        ...
    
    def setScanDirection(self, scan_direction: int ) -> None:
        """
        Cython signature: void setScanDirection(ScanDirection scan_direction)
        Sets the direction of scanning
        """
        ...
    
    def getScanLaw(self) -> int:
        """
        Cython signature: ScanLaw getScanLaw()
        Returns the scan law
        """
        ...
    
    def setScanLaw(self, scan_law: int ) -> None:
        """
        Cython signature: void setScanLaw(ScanLaw scan_law)
        Sets the scan law
        """
        ...
    
    def getReflectronState(self) -> int:
        """
        Cython signature: ReflectronState getReflectronState()
        Returns the reflectron state (for TOF)
        """
        ...
    
    def setReflectronState(self, reflecton_state: int ) -> None:
        """
        Cython signature: void setReflectronState(ReflectronState reflecton_state)
        Sets the reflectron state (for TOF)
        """
        ...
    
    def getResolution(self) -> float:
        """
        Cython signature: double getResolution()
        Returns the resolution. The maximum m/z value at which two peaks can be resolved, according to one of the standard measures
        """
        ...
    
    def setResolution(self, resolution: float ) -> None:
        """
        Cython signature: void setResolution(double resolution)
        Sets the resolution
        """
        ...
    
    def getAccuracy(self) -> float:
        """
        Cython signature: double getAccuracy()
        Returns the mass accuracy i.e. how much the theoretical mass may differ from the measured mass (in ppm)
        """
        ...
    
    def setAccuracy(self, accuracy: float ) -> None:
        """
        Cython signature: void setAccuracy(double accuracy)
        Sets the accuracy i.e. how much the theoretical mass may differ from the measured mass (in ppm)
        """
        ...
    
    def getScanRate(self) -> float:
        """
        Cython signature: double getScanRate()
        Returns the scan rate (in s)
        """
        ...
    
    def setScanRate(self, scan_rate: float ) -> None:
        """
        Cython signature: void setScanRate(double scan_rate)
        Sets the scan rate (in s)
        """
        ...
    
    def getScanTime(self) -> float:
        """
        Cython signature: double getScanTime()
        Returns the scan time for a single scan (in s)
        """
        ...
    
    def setScanTime(self, scan_time: float ) -> None:
        """
        Cython signature: void setScanTime(double scan_time)
        Sets the scan time for a single scan (in s)
        """
        ...
    
    def getTOFTotalPathLength(self) -> float:
        """
        Cython signature: double getTOFTotalPathLength()
        Returns the path length for a TOF mass analyzer (in meter)
        """
        ...
    
    def setTOFTotalPathLength(self, TOF_total_path_length: float ) -> None:
        """
        Cython signature: void setTOFTotalPathLength(double TOF_total_path_length)
        Sets the path length for a TOF mass analyzer (in meter)
        """
        ...
    
    def getIsolationWidth(self) -> float:
        """
        Cython signature: double getIsolationWidth()
        Returns the isolation width i.e. in which m/z range the precursor ion is selected for MS to the n (in m/z)
        """
        ...
    
    def setIsolationWidth(self, isolation_width: float ) -> None:
        """
        Cython signature: void setIsolationWidth(double isolation_width)
        Sets the isolation width i.e. in which m/z range the precursor ion is selected for MS to the n (in m/z)
        """
        ...
    
    def getFinalMSExponent(self) -> int:
        """
        Cython signature: int getFinalMSExponent()
        Returns the final MS exponent
        """
        ...
    
    def setFinalMSExponent(self, final_MS_exponent: int ) -> None:
        """
        Cython signature: void setFinalMSExponent(int final_MS_exponent)
        Sets the final MS exponent
        """
        ...
    
    def getMagneticFieldStrength(self) -> float:
        """
        Cython signature: double getMagneticFieldStrength()
        Returns the strength of the magnetic field (in T)
        """
        ...
    
    def setMagneticFieldStrength(self, magnetic_field_strength: float ) -> None:
        """
        Cython signature: void setMagneticFieldStrength(double magnetic_field_strength)
        Sets the strength of the magnetic field (in T)
        """
        ...
    
    def getOrder(self) -> int:
        """
        Cython signature: int getOrder()
        Returns the position of this part in the whole Instrument
        """
        ...
    
    def setOrder(self, order: int ) -> None:
        """
        Cython signature: void setOrder(int order)
        Sets the order
        """
        ...
    
    @staticmethod
    def getAllNamesOfAnalyzerType() -> List[bytes]:
        """
        Cython signature: libcpp_vector[String] getAllNamesOfAnalyzerType()
        Returns all analyzer type names known to OpenMS
        """
        ...
    
    @staticmethod
    def getAllNamesOfResolutionMethod() -> List[bytes]:
        """
        Cython signature: libcpp_vector[String] getAllNamesOfResolutionMethod()
        Returns all resolution method names known to OpenMS
        """
        ...
    
    @staticmethod
    def getAllNamesOfResolutionType() -> List[bytes]:
        """
        Cython signature: libcpp_vector[String] getAllNamesOfResolutionType()
        Returns all resolution type names known to OpenMS
        """
        ...
    
    @staticmethod
    def getAllNamesOfScanDirection() -> List[bytes]:
        """
        Cython signature: libcpp_vector[String] getAllNamesOfScanDirection()
        Returns all scan direction names known to OpenMS
        """
        ...
    
    @staticmethod
    def getAllNamesOfScanLaw() -> List[bytes]:
        """
        Cython signature: libcpp_vector[String] getAllNamesOfScanLaw()
        Returns all scan law names known to OpenMS
        """
        ...
    
    @staticmethod
    def getAllNamesOfReflectronState() -> List[bytes]:
        """
        Cython signature: libcpp_vector[String] getAllNamesOfReflectronState()
        Returns all reflectron state names known to OpenMS
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
    
    def __richcmp__(self, other: MassAnalyzer, op: int) -> Any:
        ...
    AnalyzerType : __AnalyzerType
    ReflectronState : __ReflectronState
    ResolutionMethod : __ResolutionMethod
    ResolutionType : __ResolutionType
    ScanDirection : __ScanDirection
    ScanLaw : __ScanLaw 


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


class ModificationDefinitionsSet:
    """
    Cython implementation of _ModificationDefinitionsSet

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1ModificationDefinitionsSet.html>`_

    Representation of a set of modification definitions
    
    This class enhances the modification definitions as defined in the
    class ModificationDefinition into a set of definitions. This is also
    e.g. used as input parameters in search engines.
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void ModificationDefinitionsSet()
        """
        ...
    
    @overload
    def __init__(self, in_0: ModificationDefinitionsSet ) -> None:
        """
        Cython signature: void ModificationDefinitionsSet(ModificationDefinitionsSet &)
        """
        ...
    
    @overload
    def __init__(self, fixed_modifications: List[bytes] , variable_modifications: List[bytes] ) -> None:
        """
        Cython signature: void ModificationDefinitionsSet(StringList fixed_modifications, StringList variable_modifications)
        """
        ...
    
    def setMaxModifications(self, max_mod: int ) -> None:
        """
        Cython signature: void setMaxModifications(size_t max_mod)
        Sets the maximal number of modifications allowed per peptide
        """
        ...
    
    def getMaxModifications(self) -> int:
        """
        Cython signature: size_t getMaxModifications()
        Return the maximal number of modifications allowed per peptide
        """
        ...
    
    def getNumberOfModifications(self) -> int:
        """
        Cython signature: size_t getNumberOfModifications()
        Returns the number of modifications stored in this set
        """
        ...
    
    def getNumberOfFixedModifications(self) -> int:
        """
        Cython signature: size_t getNumberOfFixedModifications()
        Returns the number of fixed modifications stored in this set
        """
        ...
    
    def getNumberOfVariableModifications(self) -> int:
        """
        Cython signature: size_t getNumberOfVariableModifications()
        Returns the number of variable modifications stored in this set
        """
        ...
    
    def addModification(self, mod_def: ModificationDefinition ) -> None:
        """
        Cython signature: void addModification(ModificationDefinition & mod_def)
        Adds a modification definition to the set
        """
        ...
    
    @overload
    def setModifications(self, mod_defs: Set[ModificationDefinition] ) -> None:
        """
        Cython signature: void setModifications(libcpp_set[ModificationDefinition] & mod_defs)
        Sets the modification definitions
        """
        ...
    
    @overload
    def setModifications(self, fixed_modifications: Union[bytes, str, String] , variable_modifications: String ) -> None:
        """
        Cython signature: void setModifications(const String & fixed_modifications, String & variable_modifications)
        Set the modification definitions from a string
        
        The strings should contain a comma separated list of modifications. The names
        can be PSI-MOD identifier or any other unique name supported by PSI-MOD. TermSpec
        definitions and other specific definitions are given by the modifications themselves.
        """
        ...
    
    @overload
    def setModifications(self, fixed_modifications: List[bytes] , variable_modifications: List[bytes] ) -> None:
        """
        Cython signature: void setModifications(StringList & fixed_modifications, StringList & variable_modifications)
        Same as above, but using StringList instead of comma separated strings
        """
        ...
    
    def getModifications(self) -> Set[ModificationDefinition]:
        """
        Cython signature: libcpp_set[ModificationDefinition] getModifications()
        Returns the stored modification definitions
        """
        ...
    
    def getFixedModifications(self) -> Set[ModificationDefinition]:
        """
        Cython signature: libcpp_set[ModificationDefinition] getFixedModifications()
        Returns the stored fixed modification definitions
        """
        ...
    
    def getVariableModifications(self) -> Set[ModificationDefinition]:
        """
        Cython signature: libcpp_set[ModificationDefinition] getVariableModifications()
        Returns the stored variable modification definitions
        """
        ...
    
    @overload
    def getModificationNames(self, fixed_modifications: List[bytes] , variable_modifications: List[bytes] ) -> None:
        """
        Cython signature: void getModificationNames(StringList & fixed_modifications, StringList & variable_modifications)
        Populates the output lists with the modification names (use e.g. for
        """
        ...
    
    @overload
    def getModificationNames(self, ) -> Set[bytes]:
        """
        Cython signature: libcpp_set[String] getModificationNames()
        Returns only the names of the modifications stored in the set
        """
        ...
    
    def getFixedModificationNames(self) -> Set[bytes]:
        """
        Cython signature: libcpp_set[String] getFixedModificationNames()
        Returns only the names of the fixed modifications
        """
        ...
    
    def getVariableModificationNames(self) -> Set[bytes]:
        """
        Cython signature: libcpp_set[String] getVariableModificationNames()
        Returns only the names of the variable modifications
        """
        ...
    
    def isCompatible(self, peptide: AASequence ) -> bool:
        """
        Cython signature: bool isCompatible(AASequence & peptide)
        Returns true if the peptide is compatible with the definitions, e.g. does not contain other modifications
        """
        ...
    
    def inferFromPeptides(self, peptides: PeptideIdentificationList ) -> None:
        """
        Cython signature: void inferFromPeptides(PeptideIdentificationList peptides)
        Infers the sets of defined modifications from the modifications present on peptide identifications
        """
        ... 


class MorpheusScore:
    """
    Cython implementation of _MorpheusScore

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1MorpheusScore.html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void MorpheusScore()
        """
        ...
    
    @overload
    def __init__(self, in_0: MorpheusScore ) -> None:
        """
        Cython signature: void MorpheusScore(MorpheusScore &)
        """
        ...
    
    def compute(self, fragment_mass_tolerance: float , fragment_mass_tolerance_unit_ppm: bool , exp_spectrum: MSSpectrum , theo_spectrum: MSSpectrum ) -> MorpheusScore_Result:
        """
        Cython signature: MorpheusScore_Result compute(double fragment_mass_tolerance, bool fragment_mass_tolerance_unit_ppm, const MSSpectrum & exp_spectrum, const MSSpectrum & theo_spectrum)
        Returns Morpheus Score
        """
        ... 


class MorpheusScore_Result:
    """
    Cython implementation of _MorpheusScore_Result

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1MorpheusScore_Result.html>`_
    """
    
    matches: int
    
    n_peaks: int
    
    score: float
    
    MIC: float
    
    TIC: float
    
    err: float
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void MorpheusScore_Result()
        """
        ...
    
    @overload
    def __init__(self, in_0: MorpheusScore_Result ) -> None:
        """
        Cython signature: void MorpheusScore_Result(MorpheusScore_Result &)
        """
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


class MzTabM:
    """
    Cython implementation of _MzTabM

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1MzTabM.html>`_

    Data model of MzTabM files
    
    Please see the official MzTabM specification at https://github.com/HUPO-PSI/mzTab/tree/master/specification_document-releases/2_0-Metabolomics-Release
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void MzTabM()
        """
        ...
    
    @overload
    def __init__(self, in_0: MzTabM ) -> None:
        """
        Cython signature: void MzTabM(MzTabM &)
        """
        ...
    
    def exportFeatureMapToMzTabM(self, feature_map: FeatureMap ) -> MzTabM:
        """
        Cython signature: MzTabM exportFeatureMapToMzTabM(FeatureMap feature_map)
        Export FeatureMap with Identifications to MzTabM
        """
        ... 


class NLargest:
    """
    Cython implementation of _NLargest

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1NLargest.html>`_
      -- Inherits from ['DefaultParamHandler']

    NLargest removes all but the n largest peaks
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void NLargest()
        """
        ...
    
    @overload
    def __init__(self, in_0: NLargest ) -> None:
        """
        Cython signature: void NLargest(NLargest &)
        """
        ...
    
    def filterSpectrum(self, spec: MSSpectrum ) -> None:
        """
        Cython signature: void filterSpectrum(MSSpectrum & spec)
        Keep only n-largest peaks in spectrum
        """
        ...
    
    def filterPeakSpectrum(self, spec: MSSpectrum ) -> None:
        """
        Cython signature: void filterPeakSpectrum(MSSpectrum & spec)
        Keep only n-largest peaks in spectrum
        """
        ...
    
    def filterPeakMap(self, exp: MSExperiment ) -> None:
        """
        Cython signature: void filterPeakMap(MSExperiment & exp)
        Keep only n-largest peaks in each spectrum of a peak map
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


class NoiseEstimator:
    """
    Cython implementation of _NoiseEstimator

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1NoiseEstimator.html>`_
    """
    
    nr_windows: int
    
    mz_start: float
    
    window_length: float
    
    result_windows_even: List[float]
    
    result_windows_odd: List[float]
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void NoiseEstimator()
        """
        ...
    
    @overload
    def __init__(self, in_0: NoiseEstimator ) -> None:
        """
        Cython signature: void NoiseEstimator(NoiseEstimator &)
        """
        ...
    
    @overload
    def __init__(self, nr_windows_: float , mz_start_: float , win_len_: float ) -> None:
        """
        Cython signature: void NoiseEstimator(double nr_windows_, double mz_start_, double win_len_)
        """
        ...
    
    def get_noise_value(self, mz: float ) -> float:
        """
        Cython signature: double get_noise_value(double mz)
        """
        ...
    
    def get_noise_even(self, mz: float ) -> float:
        """
        Cython signature: double get_noise_even(double mz)
        """
        ...
    
    def get_noise_odd(self, mz: float ) -> float:
        """
        Cython signature: double get_noise_odd(double mz)
        """
        ... 


class PI_PeakArea:
    """
    Cython implementation of _PI_PeakArea

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1PI_PeakArea.html>`_
    """
    
    area: float
    
    height: float
    
    apex_pos: float
    
    hull_points: '_np.ndarray[Any, _np.dtype[_np.float32]]'
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void PI_PeakArea()
        """
        ...
    
    @overload
    def __init__(self, in_0: PI_PeakArea ) -> None:
        """
        Cython signature: void PI_PeakArea(PI_PeakArea &)
        """
        ... 


class PI_PeakBackground:
    """
    Cython implementation of _PI_PeakBackground

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1PI_PeakBackground.html>`_
    """
    
    area: float
    
    height: float
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void PI_PeakBackground()
        """
        ...
    
    @overload
    def __init__(self, in_0: PI_PeakBackground ) -> None:
        """
        Cython signature: void PI_PeakBackground(PI_PeakBackground &)
        """
        ... 


class PI_PeakShapeMetrics:
    """
    Cython implementation of _PI_PeakShapeMetrics

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1PI_PeakShapeMetrics.html>`_
    """
    
    width_at_5: float
    
    width_at_10: float
    
    width_at_50: float
    
    start_position_at_5: float
    
    start_position_at_10: float
    
    start_position_at_50: float
    
    end_position_at_5: float
    
    end_position_at_10: float
    
    end_position_at_50: float
    
    total_width: float
    
    tailing_factor: float
    
    asymmetry_factor: float
    
    slope_of_baseline: float
    
    baseline_delta_2_height: float
    
    points_across_baseline: int
    
    points_across_half_height: int
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void PI_PeakShapeMetrics()
        """
        ...
    
    @overload
    def __init__(self, in_0: PI_PeakShapeMetrics ) -> None:
        """
        Cython signature: void PI_PeakShapeMetrics(PI_PeakShapeMetrics &)
        """
        ... 


class PeakFileOptions:
    """
    Cython implementation of _PeakFileOptions

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1PeakFileOptions.html>`_

    Options for loading files containing peak data
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void PeakFileOptions()
        """
        ...
    
    @overload
    def __init__(self, in_0: PeakFileOptions ) -> None:
        """
        Cython signature: void PeakFileOptions(PeakFileOptions &)
        """
        ...
    
    def setMetadataOnly(self, in_0: bool ) -> None:
        """
        Cython signature: void setMetadataOnly(bool)
        Sets whether or not to load only meta data
        """
        ...
    
    def getMetadataOnly(self) -> bool:
        """
        Cython signature: bool getMetadataOnly()
        Returns whether or not to load only meta data
        """
        ...
    
    def setWriteSupplementalData(self, in_0: bool ) -> None:
        """
        Cython signature: void setWriteSupplementalData(bool)
        Sets whether or not to write supplemental peak data in MzData files
        """
        ...
    
    def getWriteSupplementalData(self) -> bool:
        """
        Cython signature: bool getWriteSupplementalData()
        Returns whether or not to write supplemental peak data in MzData files
        """
        ...
    
    def setMSLevels(self, levels: List[int] ) -> None:
        """
        Cython signature: void setMSLevels(libcpp_vector[int] levels)
        Sets the desired MS levels for peaks to load
        """
        ...
    
    def addMSLevel(self, level: int ) -> None:
        """
        Cython signature: void addMSLevel(int level)
        Adds a desired MS level for peaks to load
        """
        ...
    
    def clearMSLevels(self) -> None:
        """
        Cython signature: void clearMSLevels()
        Clears the MS levels
        """
        ...
    
    def hasMSLevels(self) -> bool:
        """
        Cython signature: bool hasMSLevels()
        Returns true, if MS levels have been set
        """
        ...
    
    def containsMSLevel(self, level: int ) -> bool:
        """
        Cython signature: bool containsMSLevel(int level)
        Returns true, if MS level `level` has been set
        """
        ...
    
    def getMSLevels(self) -> List[int]:
        """
        Cython signature: libcpp_vector[int] getMSLevels()
        Returns the set MS levels
        """
        ...
    
    def setCompression(self, in_0: bool ) -> None:
        """
        Cython signature: void setCompression(bool)
        Sets if data should be compressed when writing
        """
        ...
    
    def getCompression(self) -> bool:
        """
        Cython signature: bool getCompression()
        Returns true, if data should be compressed when writing
        """
        ...
    
    def setMz32Bit(self, mz_32_bit: bool ) -> None:
        """
        Cython signature: void setMz32Bit(bool mz_32_bit)
        Sets if mz-data and rt-data should be stored with 32bit or 64bit precision
        """
        ...
    
    def getMz32Bit(self) -> bool:
        """
        Cython signature: bool getMz32Bit()
        Returns true, if mz-data and rt-data should be stored with 32bit precision
        """
        ...
    
    def setIntensity32Bit(self, int_32_bit: bool ) -> None:
        """
        Cython signature: void setIntensity32Bit(bool int_32_bit)
        Sets if intensity data should be stored with 32bit or 64bit precision
        """
        ...
    
    def getIntensity32Bit(self) -> bool:
        """
        Cython signature: bool getIntensity32Bit()
        Returns true, if intensity data should be stored with 32bit precision
        """
        ...
    
    def setRTRange(self, range_: DRange1 ) -> None:
        """
        Cython signature: void setRTRange(DRange1 & range_)
        Restricts the range of RT values for peaks to load
        """
        ...
    
    def hasRTRange(self) -> bool:
        """
        Cython signature: bool hasRTRange()
        Returns true if an RT range has been set
        """
        ...
    
    def getRTRange(self) -> DRange1:
        """
        Cython signature: DRange1 getRTRange()
        Returns the RT range
        """
        ...
    
    def setMZRange(self, range_: DRange1 ) -> None:
        """
        Cython signature: void setMZRange(DRange1 & range_)
        Restricts the range of MZ values for peaks to load
        """
        ...
    
    def hasMZRange(self) -> bool:
        """
        Cython signature: bool hasMZRange()
        Returns true if an MZ range has been set
        """
        ...
    
    def getMZRange(self) -> DRange1:
        """
        Cython signature: DRange1 getMZRange()
        Returns the MZ range
        """
        ...
    
    def setIntensityRange(self, range_: DRange1 ) -> None:
        """
        Cython signature: void setIntensityRange(DRange1 & range_)
        Restricts the range of intensity values for peaks to load
        """
        ...
    
    def hasIntensityRange(self) -> bool:
        """
        Cython signature: bool hasIntensityRange()
        Returns true if an intensity range has been set
        """
        ...
    
    def getIntensityRange(self) -> DRange1:
        """
        Cython signature: DRange1 getIntensityRange()
        Returns the intensity range
        """
        ...
    
    def getMaxDataPoolSize(self) -> int:
        """
        Cython signature: size_t getMaxDataPoolSize()
        Returns maximal size of the data pool
        """
        ...
    
    def setMaxDataPoolSize(self, s: int ) -> None:
        """
        Cython signature: void setMaxDataPoolSize(size_t s)
        Sets maximal size of the data pool
        """
        ...
    
    def setSortSpectraByMZ(self, doSort: bool ) -> None:
        """
        Cython signature: void setSortSpectraByMZ(bool doSort)
        Sets whether or not to sort peaks in spectra
        """
        ...
    
    def getSortSpectraByMZ(self) -> bool:
        """
        Cython signature: bool getSortSpectraByMZ()
        Returns whether or not peaks in spectra should be sorted
        """
        ...
    
    def setSortChromatogramsByRT(self, doSort: bool ) -> None:
        """
        Cython signature: void setSortChromatogramsByRT(bool doSort)
        Sets whether or not to sort peaks in chromatograms
        """
        ...
    
    def getSortChromatogramsByRT(self) -> bool:
        """
        Cython signature: bool getSortChromatogramsByRT()
        Returns whether or not peaks in chromatograms should be sorted
        """
        ...
    
    def hasFilters(self) -> bool:
        """
        Cython signature: bool hasFilters()
        """
        ...
    
    def setFillData(self, only: bool ) -> None:
        """
        Cython signature: void setFillData(bool only)
        Sets whether to fill the actual data into the container (spectrum/chromatogram)
        """
        ...
    
    def getFillData(self) -> bool:
        """
        Cython signature: bool getFillData()
        Returns whether to fill the actual data into the container (spectrum/chromatogram)
        """
        ...
    
    def setSkipXMLChecks(self, only: bool ) -> None:
        """
        Cython signature: void setSkipXMLChecks(bool only)
        Sets whether to skip some XML checks and be fast instead
        """
        ...
    
    def getSkipXMLChecks(self) -> bool:
        """
        Cython signature: bool getSkipXMLChecks()
        Returns whether to skip some XML checks and be fast instead
        """
        ...
    
    def getWriteIndex(self) -> bool:
        """
        Cython signature: bool getWriteIndex()
        Returns whether to write an index at the end of the file (e.g. indexedmzML file format)
        """
        ...
    
    def setWriteIndex(self, write_index: bool ) -> None:
        """
        Cython signature: void setWriteIndex(bool write_index)
        Returns whether to write an index at the end of the file (e.g. indexedmzML file format)
        """
        ...
    
    def getNumpressConfigurationMassTime(self) -> NumpressConfig:
        """
        Cython signature: NumpressConfig getNumpressConfigurationMassTime()
        Sets numpress configuration options for m/z or rt dimension
        """
        ...
    
    def setNumpressConfigurationMassTime(self, config: NumpressConfig ) -> None:
        """
        Cython signature: void setNumpressConfigurationMassTime(NumpressConfig config)
        Returns numpress configuration options for m/z or rt dimension
        """
        ...
    
    def getNumpressConfigurationIntensity(self) -> NumpressConfig:
        """
        Cython signature: NumpressConfig getNumpressConfigurationIntensity()
        Sets numpress configuration options for intensity dimension
        """
        ...
    
    def setNumpressConfigurationIntensity(self, config: NumpressConfig ) -> None:
        """
        Cython signature: void setNumpressConfigurationIntensity(NumpressConfig config)
        Returns numpress configuration options for intensity dimension
        """
        ...
    
    def getNumpressConfigurationFloatDataArray(self) -> NumpressConfig:
        """
        Cython signature: NumpressConfig getNumpressConfigurationFloatDataArray()
        Sets numpress configuration options for float data arrays
        """
        ...
    
    def setNumpressConfigurationFloatDataArray(self, config: NumpressConfig ) -> None:
        """
        Cython signature: void setNumpressConfigurationFloatDataArray(NumpressConfig config)
        Returns numpress configuration options for float data arrays
        """
        ...
    
    def setForceMQCompatability(self, forceMQ: bool ) -> None:
        """
        Cython signature: void setForceMQCompatability(bool forceMQ)
        [mzXML only!]Returns Whether to write a scan-index and meta data to indicate a Thermo FTMS/ITMS instrument (required to have parameter control in MQ)
        """
        ...
    
    def getForceMQCompatability(self) -> bool:
        """
        Cython signature: bool getForceMQCompatability()
        [mzXML only!]Returns Whether to write a scan-index and meta data to indicate a Thermo FTMS/ITMS instrument (required to have parameter control in MQ)
        """
        ...
    
    def setForceTPPCompatability(self, forceTPP: bool ) -> None:
        """
        Cython signature: void setForceTPPCompatability(bool forceTPP)
        [ mzML only!]Returns Whether to skip writing the \<isolationWindow\> tag so that TPP finds the correct precursor m/z
        """
        ...
    
    def getForceTPPCompatability(self) -> bool:
        """
        Cython signature: bool getForceTPPCompatability()
        [mzML only!]Returns Whether to skip writing the \<isolationWindow\> tag so that TPP finds the correct precursor m/z
        """
        ... 


class PeakIntegrator:
    """
    Cython implementation of _PeakIntegrator

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1PeakIntegrator.html>`_
      -- Inherits from ['DefaultParamHandler']

    Compute the area, background and shape metrics of a peak
    
    The area computation is performed in integratePeak() and it supports
    integration by simple sum of the intensity, integration by Simpson's rule
    implementations for an odd number of unequally spaced points or integration
    by the trapezoid rule
    
    The background computation is performed in estimateBackground() and it
    supports three different approaches to baseline correction, namely
    computing a rectangular shape under the peak based on the minimum value of
    the peak borders (vertical_division_min), a rectangular shape based on the
    maximum value of the beak borders (vertical_division_max) or a trapezoidal
    shape based on a straight line between the peak borders (base_to_base)
    
    Peak shape metrics are computed in calculatePeakShapeMetrics() and multiple
    metrics are supported
    
    The containers supported by the methods are MSChromatogram and MSSpectrum
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void PeakIntegrator()
        """
        ...
    
    @overload
    def __init__(self, in_0: PeakIntegrator ) -> None:
        """
        Cython signature: void PeakIntegrator(PeakIntegrator &)
        """
        ...
    
    def getDefaultParameters(self, in_0: Param ) -> None:
        """
        Cython signature: void getDefaultParameters(Param)
        """
        ...
    
    @overload
    def integratePeak(self, chromatogram: MSChromatogram , left: float , right: float ) -> PI_PeakArea:
        """
        Cython signature: PI_PeakArea integratePeak(MSChromatogram & chromatogram, double left, double right)
        """
        ...
    
    @overload
    def integratePeak(self, spectrum: MSSpectrum , left: float , right: float ) -> PI_PeakArea:
        """
        Cython signature: PI_PeakArea integratePeak(MSSpectrum & spectrum, double left, double right)
        """
        ...
    
    @overload
    def estimateBackground(self, chromatogram: MSChromatogram , left: float , right: float , peak_apex_pos: float ) -> PI_PeakBackground:
        """
        Cython signature: PI_PeakBackground estimateBackground(MSChromatogram & chromatogram, double left, double right, double peak_apex_pos)
        """
        ...
    
    @overload
    def estimateBackground(self, spectrum: MSSpectrum , left: float , right: float , peak_apex_pos: float ) -> PI_PeakBackground:
        """
        Cython signature: PI_PeakBackground estimateBackground(MSSpectrum & spectrum, double left, double right, double peak_apex_pos)
        """
        ...
    
    @overload
    def calculatePeakShapeMetrics(self, chromatogram: MSChromatogram , left: float , right: float , peak_height: float , peak_apex_pos: float ) -> PI_PeakShapeMetrics:
        """
        Cython signature: PI_PeakShapeMetrics calculatePeakShapeMetrics(MSChromatogram & chromatogram, double left, double right, double peak_height, double peak_apex_pos)
        """
        ...
    
    @overload
    def calculatePeakShapeMetrics(self, spectrum: MSSpectrum , left: float , right: float , peak_height: float , peak_apex_pos: float ) -> PI_PeakShapeMetrics:
        """
        Cython signature: PI_PeakShapeMetrics calculatePeakShapeMetrics(MSSpectrum & spectrum, double left, double right, double peak_height, double peak_apex_pos)
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


class PeptideHit:
    """
    Cython implementation of _PeptideHit

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1PeptideHit.html>`_
      -- Inherits from ['MetaInfoInterface']

    Represents a single peptide identification hit from a database search
    
    A PeptideHit stores information about a candidate peptide sequence that was
    matched to a spectrum. Each hit contains:
    
    - The peptide sequence (as AASequence)
    - A score from the search engine
    - The rank among all candidates
    - The charge state
    - Protein mappings (PeptideEvidence objects)
    
    Multiple PeptideHit objects are typically stored in a PeptideIdentification,
    sorted by score to show the most likely candidates first.
    
    Example usage:
    
    .. code-block:: python
    
       hit = oms.PeptideHit()
       hit.setSequence(oms.AASequence.fromString("PEPTIDER"))
       hit.setScore(95.5)
       hit.setRank(1)
       hit.setCharge(2)
       # Access information
       print(f"Sequence: {hit.getSequence().toString()}")
       print(f"Score: {hit.getScore()}, Rank: {hit.getRank()}")
       print(f"Charge: {hit.getCharge()}")
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void PeptideHit()
        """
        ...
    
    @overload
    def __init__(self, score: float , rank: int , charge: int , sequence: AASequence ) -> None:
        """
        Cython signature: void PeptideHit(double score, unsigned int rank, int charge, AASequence sequence)
        """
        ...
    
    @overload
    def __init__(self, in_0: PeptideHit ) -> None:
        """
        Cython signature: void PeptideHit(PeptideHit &)
        """
        ...
    
    def getScore(self) -> float:
        """
        Cython signature: float getScore()
        Returns the score of this peptide-spectrum match (PSM)
        
        :return: The search engine score
        
        Interpretation depends on the score type (check isHigherScoreBetter)
        """
        ...
    
    def getRank(self) -> int:
        """
        Cython signature: unsigned int getRank()
        Returns the rank of this hit among all candidates
        
        :return: Rank (1 = best hit, 2 = second best, etc.)
        """
        ...
    
    def getSequence(self) -> AASequence:
        """
        Cython signature: AASequence getSequence()
        Returns the peptide sequence
        
        :return: The peptide amino acid sequence with modifications
        """
        ...
    
    def getCharge(self) -> int:
        """
        Cython signature: int getCharge()
        Returns the charge state of the peptide
        
        :return: Charge state (e.g., 2 for doubly charged)
        """
        ...
    
    def getPeptideEvidences(self) -> List[PeptideEvidence]:
        """
        Cython signature: libcpp_vector[PeptideEvidence] getPeptideEvidences()
        Returns protein mapping information for this peptide
        
        :return: List of proteins where this peptide was found
        
        Each evidence contains protein accession, start/end positions, and if it's a decoy
        """
        ...
    
    def setPeptideEvidences(self, in_0: List[PeptideEvidence] ) -> None:
        """
        Cython signature: void setPeptideEvidences(libcpp_vector[PeptideEvidence])
        Sets the protein mapping information
        
        :param evidences: Protein locations for this peptide
        """
        ...
    
    def addPeptideEvidence(self, in_0: PeptideEvidence ) -> None:
        """
        Cython signature: void addPeptideEvidence(PeptideEvidence)
        Adds a single protein mapping
        
        :param evidence: Protein location information to add
        """
        ...
    
    def extractProteinAccessionsSet(self) -> Set[bytes]:
        """
        Cython signature: libcpp_set[String] extractProteinAccessionsSet()
        Extracts all unique protein accessions
        
        :return: Set of unique protein accession strings
        
        Empty accessions are excluded from the result
        """
        ...
    
    def isDecoy(self) -> bool:
        """
        Cython signature: bool isDecoy()
        Checks if this hit maps only to decoy proteins
        
        :return: True if all protein mappings are decoys, False otherwise
        
        Returns False if no target/decoy information is available
        """
        ...
    
    def setAnalysisResults(self, aresult: List[PeptideHit_AnalysisResult] ) -> None:
        """
        Cython signature: void setAnalysisResults(libcpp_vector[PeptideHit_AnalysisResult] aresult)
        Sets search engine sub-scores
        
        :param aresult: Sub-score information from search engine
        """
        ...
    
    def addAnalysisResults(self, aresult: PeptideHit_AnalysisResult ) -> None:
        """
        Cython signature: void addAnalysisResults(PeptideHit_AnalysisResult aresult)
        Adds a search engine sub-score
        
        :param aresult: Sub-score to add
        """
        ...
    
    def getAnalysisResults(self) -> List[PeptideHit_AnalysisResult]:
        """
        Cython signature: libcpp_vector[PeptideHit_AnalysisResult] getAnalysisResults()
        Returns all search engine sub-scores
        
        :return: Sub-score information
        """
        ...
    
    def setPeakAnnotations(self, in_0: List[PeptideHit_PeakAnnotation] ) -> None:
        """
        Cython signature: void setPeakAnnotations(libcpp_vector[PeptideHit_PeakAnnotation])
        Sets fragment ion annotations
        
        :param annotations: Fragment peak annotations
        """
        ...
    
    def getPeakAnnotations(self) -> List[PeptideHit_PeakAnnotation]:
        """
        Cython signature: libcpp_vector[PeptideHit_PeakAnnotation] getPeakAnnotations()
        Returns fragment ion annotations
        
        :return: Annotated fragment peaks
        """
        ...
    
    def setScore(self, in_0: float ) -> None:
        """
        Cython signature: void setScore(double)
        Sets the PSM score
        
        :param score: The search engine score to set
        """
        ...
    
    def setRank(self, in_0: int ) -> None:
        """
        Cython signature: void setRank(unsigned int)
        Sets the rank of this hit
        
        :param rank: Rank among all candidates (1 = best)
        """
        ...
    
    def setSequence(self, in_0: AASequence ) -> None:
        """
        Cython signature: void setSequence(AASequence)
        Sets the peptide sequence
        
        :param sequence: The peptide amino acid sequence
        """
        ...
    
    def setCharge(self, in_0: int ) -> None:
        """
        Cython signature: void setCharge(int)
        Sets the charge state
        
        :param charge: Charge state of the peptide ion
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
    
    def __richcmp__(self, other: PeptideHit, op: int) -> Any:
        ... 


class PeptideHit_AnalysisResult:
    """
    Cython implementation of _PeptideHit_AnalysisResult

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1PeptideHit_AnalysisResult.html>`_
    """
    
    score_type: Union[bytes, str, String]
    
    higher_is_better: bool
    
    main_score: float
    
    sub_scores: Dict[Union[bytes, str, String], float]
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void PeptideHit_AnalysisResult()
        """
        ...
    
    @overload
    def __init__(self, in_0: PeptideHit_AnalysisResult ) -> None:
        """
        Cython signature: void PeptideHit_AnalysisResult(PeptideHit_AnalysisResult &)
        """
        ... 


class PeptideHit_PeakAnnotation:
    """
    Cython implementation of _PeptideHit_PeakAnnotation

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1PeptideHit_PeakAnnotation.html>`_
    """
    
    annotation: Union[bytes, str, String]
    
    charge: int
    
    mz: float
    
    intensity: float
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void PeptideHit_PeakAnnotation()
        """
        ...
    
    @overload
    def __init__(self, in_0: PeptideHit_PeakAnnotation ) -> None:
        """
        Cython signature: void PeptideHit_PeakAnnotation(PeptideHit_PeakAnnotation &)
        """
        ...
    
    def writePeakAnnotationsString_(self, annotation_string: String , annotations: List[PeptideHit_PeakAnnotation] ) -> None:
        """
        Cython signature: void writePeakAnnotationsString_(String & annotation_string, libcpp_vector[PeptideHit_PeakAnnotation] annotations)
        """
        ...
    
    def __richcmp__(self, other: PeptideHit_PeakAnnotation, op: int) -> Any:
        ... 


class PeptideIndexing:
    """
    Cython implementation of _PeptideIndexing

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1PeptideIndexing.html>`_
      -- Inherits from ['DefaultParamHandler']

    Refreshes the protein references for all peptide hits in a vector of PeptideIdentifications and adds target/decoy information
    
    All peptide and protein hits are annotated with target/decoy information, using the meta value "target_decoy". For proteins the possible values are "target" and "decoy",
    depending on whether the protein accession contains the decoy pattern (parameter `decoy_string`) as a suffix or prefix, respectively (see parameter `prefix`).
    For peptides, the possible values are "target", "decoy" and "target+decoy", depending on whether the peptide sequence is found only in target proteins,
    only in decoy proteins, or in both. The target/decoy information is crucial for the @ref TOPP_FalseDiscoveryRate tool.
    (For FDR calculations, "target+decoy" peptide hits count as target hits.)
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void PeptideIndexing()
        """
        ...
    
    @overload
    def __init__(self, in_0: PeptideIndexing ) -> None:
        """
        Cython signature: void PeptideIndexing(PeptideIndexing &)
        """
        ...
    
    def run(self, proteins: List[FASTAEntry] , prot_ids: List[ProteinIdentification] , pep_ids: PeptideIdentificationList ) -> int:
        """
        Cython signature: PeptideIndexing_ExitCodes run(libcpp_vector[FASTAEntry] & proteins, libcpp_vector[ProteinIdentification] & prot_ids, PeptideIdentificationList & pep_ids)
        """
        ...
    
    def getDecoyString(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getDecoyString()
        """
        ...
    
    def isPrefix(self) -> bool:
        """
        Cython signature: bool isPrefix()
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
    PeptideIndexing_ExitCodes : __PeptideIndexing_ExitCodes 


class PercolatorOutfile:
    """
    Cython implementation of _PercolatorOutfile

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1PercolatorOutfile.html>`_

    Class for reading Percolator tab-delimited output files
    
    For PSM-level output, the file extension should be ".psms"
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void PercolatorOutfile()
        """
        ...
    
    @overload
    def __init__(self, in_0: PercolatorOutfile ) -> None:
        """
        Cython signature: void PercolatorOutfile(PercolatorOutfile &)
        """
        ...
    
    def getScoreType(self, score_type_name: Union[bytes, str, String] ) -> int:
        """
        Cython signature: PercolatorOutfile_ScoreType getScoreType(String score_type_name)
        Returns a score type given its name
        """
        ...
    
    def load(self, filename: Union[bytes, str, String] , proteins: ProteinIdentification , peptides: PeptideIdentificationList , lookup: SpectrumMetaDataLookup , output_score: int ) -> None:
        """
        Cython signature: void load(const String & filename, ProteinIdentification & proteins, PeptideIdentificationList & peptides, SpectrumMetaDataLookup & lookup, PercolatorOutfile_ScoreType output_score)
        Loads a Percolator output file
        """
        ...
    PercolatorOutfile_ScoreType : __PercolatorOutfile_ScoreType 


class ProgressLogger:
    """
    Cython implementation of _ProgressLogger

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1ProgressLogger.html>`_

    Base class for all classes that want to report their progress
    
    Per default the progress log is disabled. Use setLogType to enable it
    
    Use startProgress, setProgress and endProgress for the actual logging
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void ProgressLogger()
        """
        ...
    
    @overload
    def __init__(self, in_0: ProgressLogger ) -> None:
        """
        Cython signature: void ProgressLogger(ProgressLogger &)
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


class RANSAC:
    """
    Cython implementation of _RANSAC[_RansacModelLinear]

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS::Math_1_1RANSAC[_RansacModelLinear].html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void RANSAC()
        """
        ...
    
    @overload
    def __init__(self, seed: int ) -> None:
        """
        Cython signature: void RANSAC(uint64_t seed)
        """
        ...
    
    def ransac(self, pairs: List[List[float, float]] , n: int , k: int , t: float , d: int , relative_d: bool ) -> List[List[float, float]]:
        """
        Cython signature: libcpp_vector[libcpp_pair[double,double]] ransac(libcpp_vector[libcpp_pair[double,double]] pairs, size_t n, size_t k, double t, size_t d, bool relative_d)
        """
        ... 


class RANSACParam:
    """
    Cython implementation of _RANSACParam

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS::Math_1_1RANSACParam.html>`_
    """
    
    n: int
    
    k: int
    
    t: float
    
    d: int
    
    relative_d: bool
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void RANSACParam()
        A simple struct to carry all the parameters required for a RANSAC run
        """
        ...
    
    @overload
    def __init__(self, p_n: int , p_k: int , p_t: float , p_d: int , p_relative_d: bool ) -> None:
        """
        Cython signature: void RANSACParam(size_t p_n, size_t p_k, double p_t, size_t p_d, bool p_relative_d)
        """
        ...
    
    def toString(self) -> Union[bytes, str, String]:
        """
        Cython signature: String toString()
        """
        ...
    
    def __str__(self) -> Union[bytes, str, String]:
        """
        Cython signature: String toString()
        """
        ... 


class RANSACQuadratic:
    """
    Cython implementation of _RANSAC[_RansacModelQuadratic]

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS::Math_1_1RANSAC[_RansacModelQuadratic].html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void RANSACQuadratic()
        """
        ...
    
    @overload
    def __init__(self, seed: int ) -> None:
        """
        Cython signature: void RANSACQuadratic(uint64_t seed)
        """
        ...
    
    def ransac(self, pairs: List[List[float, float]] , n: int , k: int , t: float , d: int , relative_d: bool ) -> List[List[float, float]]:
        """
        Cython signature: libcpp_vector[libcpp_pair[double,double]] ransac(libcpp_vector[libcpp_pair[double,double]] pairs, size_t n, size_t k, double t, size_t d, bool relative_d)
        """
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


class RibonucleotideDB:
    """
    Cython implementation of _RibonucleotideDB

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1RibonucleotideDB.html>`_
    """
    
    def getRibonucleotide(self, code: bytes ) -> Ribonucleotide:
        """
        Cython signature: const Ribonucleotide * getRibonucleotide(const libcpp_string & code)
        """
        ...
    
    def getRibonucleotidePrefix(self, code: bytes ) -> Ribonucleotide:
        """
        Cython signature: const Ribonucleotide * getRibonucleotidePrefix(const libcpp_string & code)
        """
        ... 


class RichPeak2D:
    """
    Cython implementation of _RichPeak2D

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1RichPeak2D.html>`_
      -- Inherits from ['Peak2D', 'UniqueIdInterface', 'MetaInfoInterface']
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void RichPeak2D()
        A 2-dimensional raw data point or peak with meta information
        """
        ...
    
    @overload
    def __init__(self, in_0: RichPeak2D ) -> None:
        """
        Cython signature: void RichPeak2D(RichPeak2D &)
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
    
    def __richcmp__(self, other: RichPeak2D, op: int) -> Any:
        ... 


class SavitzkyGolayFilter:
    """
    Cython implementation of _SavitzkyGolayFilter

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1SavitzkyGolayFilter.html>`_
      -- Inherits from ['DefaultParamHandler', 'ProgressLogger']
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void SavitzkyGolayFilter()
        """
        ...
    
    @overload
    def __init__(self, in_0: SavitzkyGolayFilter ) -> None:
        """
        Cython signature: void SavitzkyGolayFilter(SavitzkyGolayFilter &)
        """
        ...
    
    def filter(self, spectrum: MSSpectrum ) -> None:
        """
        Cython signature: void filter(MSSpectrum & spectrum)
        Removed the noise from an MSSpectrum containing profile data
        """
        ...
    
    def filterExperiment(self, exp: MSExperiment ) -> None:
        """
        Cython signature: void filterExperiment(MSExperiment & exp)
        Removed the noise from an MSExperiment containing profile data
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


class SignalToNoiseEstimatorMeanIterative:
    """
    Cython implementation of _SignalToNoiseEstimatorMeanIterative[_MSSpectrum]

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1SignalToNoiseEstimatorMeanIterative[_MSSpectrum].html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void SignalToNoiseEstimatorMeanIterative()
        """
        ...
    
    @overload
    def __init__(self, in_0: SignalToNoiseEstimatorMeanIterative ) -> None:
        """
        Cython signature: void SignalToNoiseEstimatorMeanIterative(SignalToNoiseEstimatorMeanIterative &)
        """
        ...
    
    def init(self, c: MSSpectrum ) -> None:
        """
        Cython signature: void init(MSSpectrum & c)
        """
        ...
    
    def getSignalToNoise(self, index: int ) -> float:
        """
        Cython signature: double getSignalToNoise(size_t index)
        """
        ...
    IntensityThresholdCalculation : __IntensityThresholdCalculation 


class SignalToNoiseEstimatorMedianRapid:
    """
    Cython implementation of _SignalToNoiseEstimatorMedianRapid

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1SignalToNoiseEstimatorMedianRapid.html>`_
    """
    
    @overload
    def __init__(self, in_0: SignalToNoiseEstimatorMedianRapid ) -> None:
        """
        Cython signature: void SignalToNoiseEstimatorMedianRapid(SignalToNoiseEstimatorMedianRapid &)
        """
        ...
    
    @overload
    def __init__(self, window_length: float ) -> None:
        """
        Cython signature: void SignalToNoiseEstimatorMedianRapid(double window_length)
        """
        ...
    
    @overload
    def estimateNoise(self, in_0: _Interfaces_Spectrum ) -> NoiseEstimator:
        """
        Cython signature: NoiseEstimator estimateNoise(shared_ptr[_Interfaces_Spectrum])
        """
        ...
    
    @overload
    def estimateNoise(self, in_0: _Interfaces_Chromatogram ) -> NoiseEstimator:
        """
        Cython signature: NoiseEstimator estimateNoise(shared_ptr[_Interfaces_Chromatogram])
        """
        ...
    
    @overload
    def estimateNoise(self, mz_array: List[float] , int_array: List[float] ) -> NoiseEstimator:
        """
        Cython signature: NoiseEstimator estimateNoise(libcpp_vector[double] mz_array, libcpp_vector[double] int_array)
        """
        ... 


class SimpleSearchEngineAlgorithm:
    """
    Cython implementation of _SimpleSearchEngineAlgorithm

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1SimpleSearchEngineAlgorithm.html>`_
      -- Inherits from ['DefaultParamHandler', 'ProgressLogger']
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void SimpleSearchEngineAlgorithm()
        """
        ...
    
    @overload
    def __init__(self, in_0: SimpleSearchEngineAlgorithm ) -> None:
        """
        Cython signature: void SimpleSearchEngineAlgorithm(SimpleSearchEngineAlgorithm &)
        """
        ...
    
    def search(self, in_mzML: Union[bytes, str, String] , in_db: Union[bytes, str, String] , prot_ids: List[ProteinIdentification] , pep_ids: PeptideIdentificationList ) -> None:
        """
        Cython signature: void search(const String & in_mzML, const String & in_db, libcpp_vector[ProteinIdentification] & prot_ids, PeptideIdentificationList & pep_ids)
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


class SpectrumAccessSqMass:
    """
    Cython implementation of _SpectrumAccessSqMass

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1SpectrumAccessSqMass.html>`_
      -- Inherits from ['ISpectrumAccess']
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void SpectrumAccessSqMass()
        """
        ...
    
    @overload
    def __init__(self, in_0: SpectrumAccessSqMass ) -> None:
        """
        Cython signature: void SpectrumAccessSqMass(SpectrumAccessSqMass &)
        """
        ...
    
    @overload
    def __init__(self, in_0: MzMLSqliteHandler , indices: List[int] ) -> None:
        """
        Cython signature: void SpectrumAccessSqMass(MzMLSqliteHandler, libcpp_vector[int] indices)
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


class SpectrumAnnotator:
    """
    Cython implementation of _SpectrumAnnotator

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1SpectrumAnnotator.html>`_
      -- Inherits from ['DefaultParamHandler']
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void SpectrumAnnotator()
        Annotates spectra from identifications and theoretical spectra or
        identifications from spectra and theoretical spectra matching
        with various options
        """
        ...
    
    @overload
    def __init__(self, in_0: SpectrumAnnotator ) -> None:
        """
        Cython signature: void SpectrumAnnotator(SpectrumAnnotator &)
        """
        ...
    
    def annotateMatches(self, spec: MSSpectrum , ph: PeptideHit , tg: TheoreticalSpectrumGenerator , sa: SpectrumAlignment ) -> None:
        """
        Cython signature: void annotateMatches(MSSpectrum & spec, PeptideHit & ph, TheoreticalSpectrumGenerator & tg, SpectrumAlignment & sa)
        Adds ion match annotation to the `spec` input spectrum
        
        :param spec: A PeakSpectrum containing the peaks from which the `pi` identifications are made
        :param ph: A spectrum identifications to be used for the annotation, looking up matches from a spectrum and the theoretical spectrum inferred from the identifications sequence
        :param tg: A TheoreticalSpectrumGenerator to infer the theoretical spectrum. Its own parameters define which ion types are referred
        :param sa: A SpectrumAlignment to match the theoretical spectrum with the measured. Its own parameters define the match tolerance
        """
        ...
    
    def addIonMatchStatistics(self, pi: PeptideIdentification , spec: MSSpectrum , tg: TheoreticalSpectrumGenerator , sa: SpectrumAlignment ) -> None:
        """
        Cython signature: void addIonMatchStatistics(PeptideIdentification & pi, MSSpectrum & spec, TheoreticalSpectrumGenerator & tg, SpectrumAlignment & sa)
        Adds ion match statistics to `pi` PeptideIdentifcation
        
        :param pi: A spectrum identifications to be annotated, looking up matches from a spectrum and the theoretical spectrum inferred from the identifications sequence
        :param spec: A PeakSpectrum containing the peaks from which the `pi` identifications are made
        :param tg: A TheoreticalSpectrumGenerator to infer the theoretical spectrum. Its own parameters define which ion types are referred
        :param sa: A SpectrumAlignment to match the theoretical spectrum with the measured. Its own parameters define the match tolerance
        """
        ...
    
    def addPeakAnnotationsToPeptideHit(self, ph: PeptideHit , spec: MSSpectrum , tg: TheoreticalSpectrumGenerator , sa: SpectrumAlignment , include_unmatched_peaks: bool ) -> None:
        """
        Cython signature: void addPeakAnnotationsToPeptideHit(PeptideHit & ph, MSSpectrum & spec, TheoreticalSpectrumGenerator & tg, SpectrumAlignment & sa, bool include_unmatched_peaks)
        Adds peak annotations to the `ph` PeptideHit
        
        :param ph: A PeptideHit whose PeakAnnotations vector will be filled with the ion matches
        :param spec: A PeakSpectrum containing the peaks from which the `ph` identifications are made
        :param tg: A TheoreticalSpectrumGenerator to infer the theoretical spectrum. Its own parameters define which ion types are referred
        :param sa: A SpectrumAlignment to match the theoretical spectrum with the measured. Its own parameters define the match tolerance
        :param include_unmatched_peaks: If true, all spectrum peaks will be included in the PeakAnnotations vector. Unmatched peaks will have empty annotation strings. If false, only matched peaks are included.
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


class SplinePackage:
    """
    Cython implementation of _SplinePackage

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1SplinePackage.html>`_
    """
    
    @overload
    def __init__(self, pos: List[float] , intensity: List[float] ) -> None:
        """
        Cython signature: void SplinePackage(libcpp_vector[double] pos, libcpp_vector[double] intensity)
        """
        ...
    
    @overload
    def __init__(self, in_0: SplinePackage ) -> None:
        """
        Cython signature: void SplinePackage(SplinePackage &)
        """
        ...
    
    def getPosMin(self) -> float:
        """
        Cython signature: double getPosMin()
        Returns the minimum position for which the spline fit is valid
        """
        ...
    
    def getPosMax(self) -> float:
        """
        Cython signature: double getPosMax()
        Returns the maximum position for which the spline fit is valid
        """
        ...
    
    def getPosStepWidth(self) -> float:
        """
        Cython signature: double getPosStepWidth()
        Returns a sensible position step width for the package
        """
        ...
    
    def isInPackage(self, pos: float ) -> bool:
        """
        Cython signature: bool isInPackage(double pos)
        Returns true if position in
        """
        ...
    
    def eval(self, pos: float ) -> float:
        """
        Cython signature: double eval(double pos)
        Returns interpolated intensity position `pos`
        """
        ... 


class SqMassConfig:
    """
    Cython implementation of _SqMassConfig

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1SqMassConfig.html>`_
    """
    
    write_full_meta: bool
    
    use_lossy_numpress: bool
    
    linear_fp_mass_acc: float
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void SqMassConfig()
        """
        ...
    
    @overload
    def __init__(self, in_0: SqMassConfig ) -> None:
        """
        Cython signature: void SqMassConfig(SqMassConfig &)
        """
        ... 


class SqMassFile:
    """
    Cython implementation of _SqMassFile

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1SqMassFile.html>`_

    An class that uses on-disk SQLite database to read and write spectra and chromatograms
    
    This class provides functions to read and write spectra and chromatograms
    to disk using a SQLite database and store them in sqMass format. This
    allows users to access, select and filter spectra and chromatograms
    on-demand even in a large collection of data
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void SqMassFile()
        """
        ...
    
    @overload
    def __init__(self, in_0: SqMassFile ) -> None:
        """
        Cython signature: void SqMassFile(SqMassFile &)
        """
        ...
    
    def load(self, filename: Union[bytes, str, String] , map_: MSExperiment ) -> None:
        """
        Cython signature: void load(const String & filename, MSExperiment & map_)
        Read / Write a complete mass spectrometric experiment
        """
        ...
    
    def store(self, filename: Union[bytes, str, String] , map_: MSExperiment ) -> None:
        """
        Cython signature: void store(const String & filename, MSExperiment & map_)
        Store an MSExperiment in sqMass format
        """
        ...
    
    def setConfig(self, config: SqMassConfig ) -> None:
        """
        Cython signature: void setConfig(SqMassConfig config)
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


class TransitionTSVFile:
    """
    Cython implementation of _TransitionTSVFile

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1TransitionTSVFile.html>`_
      -- Inherits from ['ProgressLogger']
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void TransitionTSVFile()
        """
        ...
    
    @overload
    def __init__(self, in_0: TransitionTSVFile ) -> None:
        """
        Cython signature: void TransitionTSVFile(TransitionTSVFile &)
        """
        ...
    
    def convertTargetedExperimentToTSV(self, filename: bytes , targeted_exp: TargetedExperiment ) -> None:
        """
        Cython signature: void convertTargetedExperimentToTSV(char * filename, TargetedExperiment & targeted_exp)
        Write out a targeted experiment (TraML structure) into a tsv file
        """
        ...
    
    @overload
    def convertTSVToTargetedExperiment(self, filename: bytes , filetype: int , targeted_exp: TargetedExperiment ) -> None:
        """
        Cython signature: void convertTSVToTargetedExperiment(char * filename, FileType filetype, TargetedExperiment & targeted_exp)
        Read in a tsv/mrm file and construct a targeted experiment (TraML structure)
        """
        ...
    
    @overload
    def convertTSVToTargetedExperiment(self, filename: bytes , filetype: int , targeted_exp: LightTargetedExperiment ) -> None:
        """
        Cython signature: void convertTSVToTargetedExperiment(char * filename, FileType filetype, LightTargetedExperiment & targeted_exp)
        Read in a tsv file and construct a targeted experiment (Light transition structure)
        """
        ...
    
    def validateTargetedExperiment(self, targeted_exp: TargetedExperiment ) -> None:
        """
        Cython signature: void validateTargetedExperiment(TargetedExperiment targeted_exp)
        Validate a TargetedExperiment (check that all ids are unique)
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


class __AnalyzerType:
    None
    ANALYZERNULL : int
    QUADRUPOLE : int
    PAULIONTRAP : int
    RADIALEJECTIONLINEARIONTRAP : int
    AXIALEJECTIONLINEARIONTRAP : int
    TOF : int
    SECTOR : int
    FOURIERTRANSFORM : int
    IONSTORAGE : int
    ESA : int
    IT : int
    SWIFT : int
    CYCLOTRON : int
    ORBITRAP : int
    LIT : int
    SIZE_OF_ANALYZERTYPE : int

    def getMapping(self) -> Dict[int, str]:
       ... 


class __ChromatogramType:
    None
    MASS_CHROMATOGRAM : int
    TOTAL_ION_CURRENT_CHROMATOGRAM : int
    SELECTED_ION_CURRENT_CHROMATOGRAM : int
    BASEPEAK_CHROMATOGRAM : int
    SELECTED_ION_MONITORING_CHROMATOGRAM : int
    SELECTED_REACTION_MONITORING_CHROMATOGRAM : int
    ELECTROMAGNETIC_RADIATION_CHROMATOGRAM : int
    ABSORPTION_CHROMATOGRAM : int
    EMISSION_CHROMATOGRAM : int
    SIZE_OF_CHROMATOGRAM_TYPE : int

    def getMapping(self) -> Dict[int, str]:
       ... 


class __IntensityThresholdCalculation:
    None
    MANUAL : int
    AUTOMAXBYSTDEV : int
    AUTOMAXBYPERCENT : int

    def getMapping(self) -> Dict[int, str]:
       ... 


class LogType:
    None
    CMD : int
    GUI : int
    NONE : int

    def getMapping(self) -> Dict[int, str]:
       ... 


class __MergeIntensityMode:
    None
    SUM : int
    MAX : int

    def getMapping(self) -> Dict[int, str]:
       ... 


class __PeptideIndexing_ExitCodes:
    None
    EXECUTION_OK : int
    DATABASE_EMPTY : int
    PEPTIDE_IDS_EMPTY : int
    ILLEGAL_PARAMETERS : int
    UNEXPECTED_RESULT : int
    DECOYSTRING_EMPTY : int

    def getMapping(self) -> Dict[int, str]:
       ... 


class __PercolatorOutfile_ScoreType:
    None
    QVALUE : int
    POSTERRPROB : int
    SCORE : int
    SIZE_OF_SCORETYPE : int

    def getMapping(self) -> Dict[int, str]:
       ... 


class __ReflectronState:
    None
    REFLSTATENULL : int
    ON : int
    OFF : int
    NONE : int
    SIZE_OF_REFLECTRONSTATE : int

    def getMapping(self) -> Dict[int, str]:
       ... 


class __ResolutionMethod:
    None
    RESMETHNULL : int
    FWHM : int
    TENPERCENTVALLEY : int
    BASELINE : int
    SIZE_OF_RESOLUTIONMETHOD : int

    def getMapping(self) -> Dict[int, str]:
       ... 


class __ResolutionType:
    None
    RESTYPENULL : int
    CONSTANT : int
    PROPORTIONAL : int
    SIZE_OF_RESOLUTIONTYPE : int

    def getMapping(self) -> Dict[int, str]:
       ... 


class __ScanDirection:
    None
    SCANDIRNULL : int
    UP : int
    DOWN : int
    SIZE_OF_SCANDIRECTION : int

    def getMapping(self) -> Dict[int, str]:
       ... 


class __ScanLaw:
    None
    SCANLAWNULL : int
    EXPONENTIAL : int
    LINEAR : int
    QUADRATIC : int
    SIZE_OF_SCANLAW : int

    def getMapping(self) -> Dict[int, str]:
       ... 

