from __future__ import annotations
from typing import overload, Any, List, Dict, Tuple, Set, Sequence, Union
from pyopenms import *  # pylint: disable=wildcard-import; lgtm(py/polluting-import)
import numpy as _np

from enum import IntEnum as _PyEnum


def __static_NASequence_fromString(s: Union[bytes, str, String] ) -> NASequence:
    """
    Cython signature: NASequence fromString(const String & s)
    """
    ...

def __static_CalibrationData_getMetaValues() -> List[bytes]:
    """
    Cython signature: StringList getMetaValues()
    """
    ...

def __static_FLASHDeconvAlgorithm_getScanNumber(exp: MSExperiment , index: int ) -> int:
    """
    Cython signature: int getScanNumber(MSExperiment & exp, size_t index)
    """
    ...

def __static_ExperimentalDesignFile_load(tsv_file: Union[bytes, str, String] , in_1: bool ) -> ExperimentalDesign:
    """
    Cython signature: ExperimentalDesign load(const String & tsv_file, bool)
    """
    ...

def __static_DateTime_now() -> DateTime:
    """
    Cython signature: DateTime now()
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


class AnnotatedMSRun:
    """
    Cython implementation of _AnnotatedMSRun

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1AnnotatedMSRun.html>`_

    Class for storing MS run data with peptide and protein identifications
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void AnnotatedMSRun()
        """
        ...
    
    @overload
    def __init__(self, in_0: AnnotatedMSRun ) -> None:
        """
        Cython signature: void AnnotatedMSRun(AnnotatedMSRun)
        """
        ...
    
    def getProteinIdentifications(self) -> List[ProteinIdentification]:
        """
        Cython signature: libcpp_vector[ProteinIdentification] getProteinIdentifications()
        """
        ...
    
    def setProteinIdentifications(self, ids: List[ProteinIdentification] ) -> None:
        """
        Cython signature: void setProteinIdentifications(libcpp_vector[ProteinIdentification] & ids)
        """
        ...
    
    def getPeptideIdentifications(self) -> PeptideIdentificationList:
        """
        Cython signature: PeptideIdentificationList getPeptideIdentifications()
        """
        ...
    
    def setPeptideIdentifications(self, ids: PeptideIdentificationList ) -> None:
        """
        Cython signature: void setPeptideIdentifications(PeptideIdentificationList ids)
        """
        ...
    
    def getMSExperiment(self) -> MSExperiment:
        """
        Cython signature: MSExperiment getMSExperiment()
        """
        ...
    
    def setMSExperiment(self, experiment: MSExperiment ) -> None:
        """
        Cython signature: void setMSExperiment(MSExperiment & experiment)
        """
        ... 


class Base64:
    """
    Cython implementation of _Base64

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1Base64.html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void Base64()
        Class to encode and decode Base64, it supports two precisions 32 bit (float) and 64 bit (double).
        """
        ...
    
    @overload
    def __init__(self, in_0: Base64 ) -> None:
        """
        Cython signature: void Base64(Base64 &)
        """
        ...
    
    def encodeIntegers(self, in_: List[int] , to_byte_order: int , out: String , zlib_compression: bool ) -> None:
        """
        Cython signature: void encodeIntegers(libcpp_vector[int] & in_, ByteOrder to_byte_order, String & out, bool zlib_compression)
        Encodes a vector of integer point numbers to a Base64 string
        """
        ...
    
    def decodeIntegers(self, in_: Union[bytes, str, String] , from_byte_order: int , out: List[int] , zlib_compression: bool ) -> None:
        """
        Cython signature: void decodeIntegers(const String & in_, ByteOrder from_byte_order, libcpp_vector[int] & out, bool zlib_compression)
        Decodes a Base64 string to a vector of integer numbers
        """
        ...
    
    def encodeStrings(self, in_: List[bytes] , out: String , zlib_compression: bool ) -> None:
        """
        Cython signature: void encodeStrings(libcpp_vector[String] & in_, String & out, bool zlib_compression)
        Encodes a vector of strings to a Base64 string
        """
        ...
    
    def decodeStrings(self, in_: Union[bytes, str, String] , out: List[bytes] , zlib_compression: bool ) -> None:
        """
        Cython signature: void decodeStrings(const String & in_, libcpp_vector[String] & out, bool zlib_compression)
        Decodes a Base64 string to a vector of (null-terminated) strings
        """
        ...
    ByteOrder : __ByteOrder 


class BaseFeature:
    """
    Cython implementation of _BaseFeature

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1BaseFeature.html>`_
      -- Inherits from ['UniqueIdInterface', 'RichPeak2D']
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void BaseFeature()
        """
        ...
    
    @overload
    def __init__(self, in_0: BaseFeature ) -> None:
        """
        Cython signature: void BaseFeature(BaseFeature &)
        """
        ...
    
    def getQuality(self) -> float:
        """
        Cython signature: float getQuality()
        Returns the overall quality
        """
        ...
    
    def setQuality(self, q: float ) -> None:
        """
        Cython signature: void setQuality(float q)
        Sets the overall quality
        """
        ...
    
    def getWidth(self) -> float:
        """
        Cython signature: float getWidth()
        Returns the features width (full width at half max, FWHM)
        """
        ...
    
    def setWidth(self, q: float ) -> None:
        """
        Cython signature: void setWidth(float q)
        Sets the width of the feature (FWHM)
        """
        ...
    
    def getCharge(self) -> int:
        """
        Cython signature: int getCharge()
        Returns the charge state
        """
        ...
    
    def setCharge(self, q: int ) -> None:
        """
        Cython signature: void setCharge(int q)
        Sets the charge state
        """
        ...
    
    def getAnnotationState(self) -> int:
        """
        Cython signature: AnnotationState getAnnotationState()
        State of peptide identifications attached to this feature. If one ID has multiple hits, the output depends on the top-hit only
        """
        ...
    
    def getPeptideIdentifications(self) -> PeptideIdentificationList:
        """
        Cython signature: PeptideIdentificationList getPeptideIdentifications()
        Returns the PeptideIdentification vector
        """
        ...
    
    @overload
    def setPeptideIdentifications(self, peptides: PeptideIdentificationList ) -> None:
        """
        Cython signature: void setPeptideIdentifications(PeptideIdentificationList & peptides)
        Sets the PeptideIdentification vector
        """
        ...
    
    @overload
    def setPeptideIdentifications(self, peptides: PeptideIdentificationList ) -> None:
        """
        Cython signature: void setPeptideIdentifications(PeptideIdentificationList & peptides)
        Sets the PeptideIdentificationList
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
    
    def __richcmp__(self, other: BaseFeature, op: int) -> Any:
        ... 


class CVMappingRule:
    """
    Cython implementation of _CVMappingRule

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1CVMappingRule.html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void CVMappingRule()
        """
        ...
    
    @overload
    def __init__(self, in_0: CVMappingRule ) -> None:
        """
        Cython signature: void CVMappingRule(CVMappingRule &)
        """
        ...
    
    def setIdentifier(self, identifier: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setIdentifier(String identifier)
        Sets the identifier of the rule
        """
        ...
    
    def getIdentifier(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getIdentifier()
        Returns the identifier of the rule
        """
        ...
    
    def setElementPath(self, element_path: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setElementPath(String element_path)
        Sets the path of the DOM element, where this rule is allowed
        """
        ...
    
    def getElementPath(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getElementPath()
        Returns the path of the DOM element, where this rule is allowed
        """
        ...
    
    def setRequirementLevel(self, level: int ) -> None:
        """
        Cython signature: void setRequirementLevel(RequirementLevel level)
        Sets the requirement level of this rule
        """
        ...
    
    def getRequirementLevel(self) -> int:
        """
        Cython signature: RequirementLevel getRequirementLevel()
        Returns the requirement level of this rule
        """
        ...
    
    def setCombinationsLogic(self, combinations_logic: int ) -> None:
        """
        Cython signature: void setCombinationsLogic(CombinationsLogic combinations_logic)
        Sets the combination operator of the rule
        """
        ...
    
    def getCombinationsLogic(self) -> int:
        """
        Cython signature: CombinationsLogic getCombinationsLogic()
        Returns the combinations operator of the rule
        """
        ...
    
    def setScopePath(self, path: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setScopePath(String path)
        Sets the scope path of the rule
        """
        ...
    
    def getScopePath(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getScopePath()
        Returns the scope path of the rule
        """
        ...
    
    def setCVTerms(self, cv_terms: List[CVMappingTerm] ) -> None:
        """
        Cython signature: void setCVTerms(libcpp_vector[CVMappingTerm] cv_terms)
        Sets the terms which are allowed
        """
        ...
    
    def getCVTerms(self) -> List[CVMappingTerm]:
        """
        Cython signature: libcpp_vector[CVMappingTerm] getCVTerms()
        Returns the allowed terms
        """
        ...
    
    def addCVTerm(self, cv_terms: CVMappingTerm ) -> None:
        """
        Cython signature: void addCVTerm(CVMappingTerm cv_terms)
        Adds a term to the allowed terms
        """
        ...
    
    def __richcmp__(self, other: CVMappingRule, op: int) -> Any:
        ...
    CombinationsLogic : __CombinationsLogic
    RequirementLevel : __RequirementLevel 


class CVTerm:
    """
    Cython implementation of _CVTerm

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1CVTerm.html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void CVTerm()
        """
        ...
    
    @overload
    def __init__(self, in_0: CVTerm ) -> None:
        """
        Cython signature: void CVTerm(CVTerm &)
        """
        ...
    
    def setAccession(self, accession: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setAccession(String accession)
        Sets the accession string of the term
        """
        ...
    
    def getAccession(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getAccession()
        Returns the accession string of the term
        """
        ...
    
    def setName(self, name: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setName(String name)
        Sets the name of the term
        """
        ...
    
    def getName(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getName()
        Returns the name of the term
        """
        ...
    
    def setCVIdentifierRef(self, cv_id_ref: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setCVIdentifierRef(String cv_id_ref)
        Sets the CV identifier reference string, e.g. UO for unit obo
        """
        ...
    
    def getCVIdentifierRef(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getCVIdentifierRef()
        Returns the CV identifier reference string
        """
        ...
    
    def getValue(self) -> Union[int, float, bytes, str, List[int], List[float], List[bytes]]:
        """
        Cython signature: DataValue getValue()
        Returns the value of the term
        """
        ...
    
    def setValue(self, value: Union[int, float, bytes, str, List[int], List[float], List[bytes]] ) -> None:
        """
        Cython signature: void setValue(DataValue value)
        Sets the value of the term
        """
        ...
    
    def setUnit(self, unit: Unit ) -> None:
        """
        Cython signature: void setUnit(Unit & unit)
        Sets the unit of the term
        """
        ...
    
    def getUnit(self) -> Unit:
        """
        Cython signature: Unit getUnit()
        Returns the unit
        """
        ...
    
    def hasValue(self) -> bool:
        """
        Cython signature: bool hasValue()
        Checks whether the term has a value
        """
        ...
    
    def hasUnit(self) -> bool:
        """
        Cython signature: bool hasUnit()
        Checks whether the term has a unit
        """
        ...
    
    def __richcmp__(self, other: CVTerm, op: int) -> Any:
        ... 


class CalibrationData:
    """
    Cython implementation of _CalibrationData

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1CalibrationData.html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void CalibrationData()
        """
        ...
    
    @overload
    def __init__(self, in_0: CalibrationData ) -> None:
        """
        Cython signature: void CalibrationData(CalibrationData &)
        """
        ...
    
    def getMZ(self, in_0: int ) -> float:
        """
        Cython signature: double getMZ(size_t)
        Retrieve the observed m/z of the i'th calibration point
        """
        ...
    
    def getRT(self, in_0: int ) -> float:
        """
        Cython signature: double getRT(size_t)
        Retrieve the observed RT of the i'th calibration point
        """
        ...
    
    def getIntensity(self, in_0: int ) -> float:
        """
        Cython signature: double getIntensity(size_t)
        Retrieve the intensity of the i'th calibration point
        """
        ...
    
    def size(self) -> int:
        """
        Cython signature: size_t size()
        Number of calibration points
        """
        ...
    
    def empty(self) -> bool:
        """
        Cython signature: bool empty()
        Returns `True` if there are no peaks
        """
        ...
    
    def clear(self) -> None:
        """
        Cython signature: void clear()
        Remove all calibration points
        """
        ...
    
    def setUsePPM(self, in_0: bool ) -> None:
        """
        Cython signature: void setUsePPM(bool)
        """
        ...
    
    def usePPM(self) -> bool:
        """
        Cython signature: bool usePPM()
        Current error unit (ppm or Th)
        """
        ...
    
    def insertCalibrationPoint(self, rt: float , mz_obs: float , intensity: float , mz_ref: float , weight: float , group: int ) -> None:
        """
        Cython signature: void insertCalibrationPoint(double rt, double mz_obs, float intensity, double mz_ref, double weight, int group)
        """
        ...
    
    def getNrOfGroups(self) -> int:
        """
        Cython signature: size_t getNrOfGroups()
        Number of peak groups (can be 0)
        """
        ...
    
    def getError(self, in_0: int ) -> float:
        """
        Cython signature: double getError(size_t)
        Retrieve the error for i'th calibrant in either ppm or Th (depending on usePPM())
        """
        ...
    
    def getRefMZ(self, in_0: int ) -> float:
        """
        Cython signature: double getRefMZ(size_t)
        Retrieve the theoretical m/z of the i'th calibration point
        """
        ...
    
    def getWeight(self, in_0: int ) -> float:
        """
        Cython signature: double getWeight(size_t)
        Retrieve the weight of the i'th calibration point
        """
        ...
    
    def getGroup(self, i: int ) -> int:
        """
        Cython signature: int getGroup(size_t i)
        Retrieve the group of the i'th calibration point
        """
        ...
    
    def median(self, in_0: float , in_1: float ) -> CalibrationData:
        """
        Cython signature: CalibrationData median(double, double)
        Compute the median in the given RT range for every peak group
        """
        ...
    
    def sortByRT(self) -> None:
        """
        Cython signature: void sortByRT()
        Sort calibration points by RT, to allow for valid RT chunking
        """
        ...
    
    getMetaValues: __static_CalibrationData_getMetaValues 


class ChromatogramTools:
    """
    Cython implementation of _ChromatogramTools

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1ChromatogramTools.html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void ChromatogramTools()
        """
        ...
    
    @overload
    def __init__(self, in_0: ChromatogramTools ) -> None:
        """
        Cython signature: void ChromatogramTools(ChromatogramTools &)
        """
        ...
    
    def convertChromatogramsToSpectra(self, epx: MSExperiment ) -> None:
        """
        Cython signature: void convertChromatogramsToSpectra(MSExperiment & epx)
        Converts the chromatogram to a list of spectra with instrument settings
        """
        ...
    
    def convertSpectraToChromatograms(self, epx: MSExperiment , remove_spectra: bool , force_conversion: bool ) -> None:
        """
        Cython signature: void convertSpectraToChromatograms(MSExperiment & epx, bool remove_spectra, bool force_conversion)
        Converts e.g. SRM spectra to chromatograms
        """
        ... 


class ChromeleonFile:
    """
    Cython implementation of _ChromeleonFile

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1ChromeleonFile.html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void ChromeleonFile()
        Load Chromeleon HPLC text file and save it into a `MSExperiment`.
        """
        ...
    
    @overload
    def __init__(self, in_0: ChromeleonFile ) -> None:
        """
        Cython signature: void ChromeleonFile(ChromeleonFile &)
        """
        ...
    
    def load(self, filename: Union[bytes, str, String] , experiment: MSExperiment ) -> None:
        """
        Cython signature: void load(const String & filename, MSExperiment & experiment)
        Load the file's data and metadata, and save it into a `MSExperiment`
        """
        ... 


class ConfidenceScoring:
    """
    Cython implementation of _ConfidenceScoring

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1ConfidenceScoring.html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void ConfidenceScoring()
        """
        ...
    
    @overload
    def __init__(self, in_0: ConfidenceScoring ) -> None:
        """
        Cython signature: void ConfidenceScoring(ConfidenceScoring &)
        """
        ...
    
    def initialize(self, targeted: TargetedExperiment , n_decoys: int , n_transitions: int , trafo: TransformationDescription ) -> None:
        """
        Cython signature: void initialize(TargetedExperiment & targeted, size_t n_decoys, size_t n_transitions, TransformationDescription trafo)
        """
        ...
    
    def initializeGlm(self, intercept: float , rt_coef: float , int_coef: float ) -> None:
        """
        Cython signature: void initializeGlm(double intercept, double rt_coef, double int_coef)
        """
        ...
    
    def scoreMap(self, map: FeatureMap ) -> None:
        """
        Cython signature: void scoreMap(FeatureMap & map)
        Score a feature map -> make sure the class is properly initialized
        """
        ... 


class DIAScoring:
    """
    Cython implementation of _DIAScoring

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1DIAScoring.html>`_
      -- Inherits from ['DefaultParamHandler']
    """
    
    def __init__(self) -> None:
        """
        Cython signature: void DIAScoring()
        """
        ...
    
    def dia_ms1_massdiff_score(self, precursor_mz: float , spectrum: List[OSSpectrum] , im_range: RangeMobility , ppm_score: float ) -> bool:
        """
        Cython signature: bool dia_ms1_massdiff_score(double precursor_mz, libcpp_vector[shared_ptr[OSSpectrum]] spectrum, RangeMobility & im_range, double & ppm_score)
        """
        ...
    
    def dia_ms1_isotope_scores_averagine(self, precursor_mz: float , spectrum: List[OSSpectrum] , charge_state: int , im_range: RangeMobility , isotope_corr: float , isotope_overlap: float ) -> None:
        """
        Cython signature: void dia_ms1_isotope_scores_averagine(double precursor_mz, libcpp_vector[shared_ptr[OSSpectrum]] spectrum, int charge_state, RangeMobility & im_range, double & isotope_corr, double & isotope_overlap)
        """
        ...
    
    def dia_ms1_isotope_scores(self, precursor_mz: float , spectrum: List[OSSpectrum] , im_range: RangeMobility , isotope_corr: float , isotope_overlap: float , sum_formula: EmpiricalFormula ) -> None:
        """
        Cython signature: void dia_ms1_isotope_scores(double precursor_mz, libcpp_vector[shared_ptr[OSSpectrum]] spectrum, RangeMobility & im_range, double & isotope_corr, double & isotope_overlap, EmpiricalFormula & sum_formula)
        """
        ...
    
    def score_with_isotopes(self, spectrum: List[OSSpectrum] , transitions: List[LightTransition] , im_range: RangeMobility , dotprod: float , manhattan: float ) -> None:
        """
        Cython signature: void score_with_isotopes(libcpp_vector[shared_ptr[OSSpectrum]] spectrum, libcpp_vector[LightTransition] transitions, RangeMobility & im_range, double & dotprod, double & manhattan)
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


class DTAFile:
    """
    Cython implementation of _DTAFile

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1DTAFile.html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void DTAFile()
        """
        ...
    
    @overload
    def __init__(self, in_0: DTAFile ) -> None:
        """
        Cython signature: void DTAFile(DTAFile &)
        """
        ...
    
    def load(self, filename: Union[bytes, str, String] , spectrum: MSSpectrum ) -> None:
        """
        Cython signature: void load(String filename, MSSpectrum & spectrum)
        """
        ...
    
    def store(self, filename: Union[bytes, str, String] , spectrum: MSSpectrum ) -> None:
        """
        Cython signature: void store(String filename, MSSpectrum & spectrum)
        """
        ... 


class DateTime:
    """
    Cython implementation of _DateTime

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1DateTime.html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void DateTime()
        """
        ...
    
    @overload
    def __init__(self, in_0: DateTime ) -> None:
        """
        Cython signature: void DateTime(DateTime &)
        """
        ...
    
    def setDate(self, date: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setDate(String date)
        """
        ...
    
    def setTime(self, date: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setTime(String date)
        """
        ...
    
    def getDate(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getDate()
        """
        ...
    
    def getTime(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getTime()
        """
        ...
    
    def now(self) -> DateTime:
        """
        Cython signature: DateTime now()
        """
        ...
    
    def clear(self) -> None:
        """
        Cython signature: void clear()
        """
        ...
    
    def get(self) -> Union[bytes, str, String]:
        """
        Cython signature: String get()
        """
        ...
    
    def set(self, date: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void set(String date)
        """
        ...
    
    now: __static_DateTime_now 


class DigestionEnzymeProtein:
    """
    Cython implementation of _DigestionEnzymeProtein

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1DigestionEnzymeProtein.html>`_
      -- Inherits from ['DigestionEnzyme']

    Representation of a digestion enzyme for proteins (protease)
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void DigestionEnzymeProtein()
        """
        ...
    
    @overload
    def __init__(self, in_0: DigestionEnzymeProtein ) -> None:
        """
        Cython signature: void DigestionEnzymeProtein(DigestionEnzymeProtein &)
        """
        ...
    
    @overload
    def __init__(self, name: Union[bytes, str, String] , cleavage_regex: Union[bytes, str, String] , synonyms: Set[bytes] , regex_description: Union[bytes, str, String] , n_term_gain: EmpiricalFormula , c_term_gain: EmpiricalFormula , psi_id: Union[bytes, str, String] , xtandem_id: Union[bytes, str, String] , comet_id: int , omssa_id: int ) -> None:
        """
        Cython signature: void DigestionEnzymeProtein(String name, String cleavage_regex, libcpp_set[String] synonyms, String regex_description, EmpiricalFormula n_term_gain, EmpiricalFormula c_term_gain, String psi_id, String xtandem_id, unsigned int comet_id, unsigned int omssa_id)
        """
        ...
    
    def setNTermGain(self, value: EmpiricalFormula ) -> None:
        """
        Cython signature: void setNTermGain(EmpiricalFormula value)
        Sets the N-term gain
        """
        ...
    
    def setCTermGain(self, value: EmpiricalFormula ) -> None:
        """
        Cython signature: void setCTermGain(EmpiricalFormula value)
        Sets the C-term gain
        """
        ...
    
    def getNTermGain(self) -> EmpiricalFormula:
        """
        Cython signature: EmpiricalFormula getNTermGain()
        Returns the N-term gain
        """
        ...
    
    def getCTermGain(self) -> EmpiricalFormula:
        """
        Cython signature: EmpiricalFormula getCTermGain()
        Returns the C-term gain
        """
        ...
    
    def setPSIID(self, value: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setPSIID(String value)
        Sets the PSI ID
        """
        ...
    
    def getPSIID(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getPSIID()
        Returns the PSI ID
        """
        ...
    
    def setXTandemID(self, value: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setXTandemID(String value)
        Sets the X! Tandem enzyme ID
        """
        ...
    
    def getXTandemID(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getXTandemID()
        Returns the X! Tandem enzyme ID
        """
        ...
    
    def setCometID(self, value: int ) -> None:
        """
        Cython signature: void setCometID(int value)
        Sets the Comet enzyme ID
        """
        ...
    
    def getCometID(self) -> int:
        """
        Cython signature: int getCometID()
        Returns the Comet enzyme ID
        """
        ...
    
    def setOMSSAID(self, value: int ) -> None:
        """
        Cython signature: void setOMSSAID(int value)
        Sets the OMSSA enzyme ID
        """
        ...
    
    def getOMSSAID(self) -> int:
        """
        Cython signature: int getOMSSAID()
        Returns the OMSSA enzyme ID
        """
        ...
    
    def setMSGFID(self, value: int ) -> None:
        """
        Cython signature: void setMSGFID(int value)
        Sets the MSGFPlus enzyme id
        """
        ...
    
    def getMSGFID(self) -> int:
        """
        Cython signature: int getMSGFID()
        Returns the MSGFPlus enzyme id
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
    
    def __richcmp__(self, other: DigestionEnzymeProtein, op: int) -> Any:
        ... 


class EmgFitter1D:
    """
    Cython implementation of _EmgFitter1D

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1EmgFitter1D.html>`_
      -- Inherits from ['LevMarqFitter1D']
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void EmgFitter1D()
        Exponentially modified gaussian distribution fitter (1-dim.) using Levenberg-Marquardt algorithm (Eigen implementation) for parameter optimization
        """
        ...
    
    @overload
    def __init__(self, in_0: EmgFitter1D ) -> None:
        """
        Cython signature: void EmgFitter1D(EmgFitter1D &)
        """
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


class FLASHDeconvAlgorithm:
    """
    Cython implementation of _FLASHDeconvAlgorithm

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1FLASHDeconvAlgorithm.html>`_
      -- Inherits from ['DefaultParamHandler', 'ProgressLogger']

    FLASHDeconv algorithm: ultrafast mass deconvolution algorithm for top down mass spectrometry dataset.
    From MSSpectrum, this class outputs DeconvolvedSpectrum.
    Deconvolution takes three steps:
      i) decharging and select candidate masses - speed up via binning
      ii) collecting isotopes from the candidate masses and deisotoping - peak groups are defined here
      iii) scoring and filter out low scoring masses (i.e., peak groups)
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void FLASHDeconvAlgorithm()
        """
        ...
    
    @overload
    def __init__(self, in_0: FLASHDeconvAlgorithm ) -> None:
        """
        Cython signature: void FLASHDeconvAlgorithm(FLASHDeconvAlgorithm &)
        """
        ...
    
    def run(self, input_map: MSExperiment , deconvolved_spectra: List[DeconvolvedSpectrum] , deconvolved_features: List[MassFeature_FDHS] ) -> None:
        """
        Cython signature: void run(MSExperiment & input_map, libcpp_vector[DeconvolvedSpectrum] & deconvolved_spectra, libcpp_vector[MassFeature_FDHS] & deconvolved_features)
        Run FLASHDeconv algorithm for input_map and store deconvolved_spectra and deconvolved_features.
        :param input_map: The input MSExperiment containing spectra to deconvolve
        :param deconvolved_spectra: Output vector to store deconvolved spectra
        :param deconvolved_features: Output vector to store mass features
        """
        ...
    
    def getAveragine(self) -> PrecalAveragine:
        """
        Cython signature: PrecalAveragine & getAveragine()
        """
        ...
    
    def getDecoyAveragine(self) -> PrecalAveragine:
        """
        Cython signature: PrecalAveragine & getDecoyAveragine()
        """
        ...
    
    def getTolerances(self) -> List[float]:
        """
        Cython signature: libcpp_vector[double] getTolerances()
        """
        ...
    
    def getNoiseDecoyWeight(self) -> float:
        """
        Cython signature: double getNoiseDecoyWeight()
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
    
    getScanNumber: __static_FLASHDeconvAlgorithm_getScanNumber 


class FeatureDistance:
    """
    Cython implementation of _FeatureDistance

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1FeatureDistance.html>`_
      -- Inherits from ['DefaultParamHandler']
    """
    
    @overload
    def __init__(self, max_intensity: float , force_constraints: bool ) -> None:
        """
        Cython signature: void FeatureDistance(double max_intensity, bool force_constraints)
        """
        ...
    
    @overload
    def __init__(self, in_0: FeatureDistance ) -> None:
        """
        Cython signature: void FeatureDistance(FeatureDistance &)
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


class FeatureFinderIdentificationAlgorithm:
    """
    Cython implementation of _FeatureFinderIdentificationAlgorithm

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1FeatureFinderIdentificationAlgorithm.html>`_
      -- Inherits from ['DefaultParamHandler']

    Algorithm class for FeatureFinderIdentification
    
    External IDs (peptides_ext, proteins_ext) may be empty,
    in which case no machine learning or FDR estimation will be performed.
    Optional seeds from e.g. untargeted FeatureFinders can be added with
    seeds.
    Results will be written to features .
    Caution: peptide IDs will be shrunk to best hit, FFid metavalues added
    and potential seed IDs added.
    
    Usage:
    """
    
    def __init__(self) -> None:
        """
        Cython signature: void FeatureFinderIdentificationAlgorithm()
        """
        ...
    
    @overload
    def run(self, peptides: PeptideIdentificationList , proteins: List[ProteinIdentification] , peptides_ext: PeptideIdentificationList , proteins_ext: List[ProteinIdentification] , features: FeatureMap ) -> None:
        """
        Cython signature: void run(PeptideIdentificationList peptides, libcpp_vector[ProteinIdentification] & proteins, PeptideIdentificationList peptides_ext, libcpp_vector[ProteinIdentification] proteins_ext, FeatureMap & features)
        Run feature detection
        
        
        :param peptides: Vector of identified peptides
        :param proteins: Vector of identified proteins
        :param peptides_ext: Vector of external identified peptides, can be used to transfer ids from other runs
        :param proteins_ext: Vector of external identified proteins, can be used to transfer ids from other runs
        :param features: Feature detection results will be added here
        """
        ...
    
    @overload
    def run(self, peptides: PeptideIdentificationList , proteins: List[ProteinIdentification] , peptides_ext: PeptideIdentificationList , proteins_ext: List[ProteinIdentification] , features: FeatureMap , seeds: FeatureMap ) -> None:
        """
        Cython signature: void run(PeptideIdentificationList peptides, libcpp_vector[ProteinIdentification] & proteins, PeptideIdentificationList peptides_ext, libcpp_vector[ProteinIdentification] proteins_ext, FeatureMap & features, FeatureMap & seeds)
        Run feature detection
        
        
        :param peptides: Vector of identified peptides
        :param proteins: Vector of identified proteins
        :param peptides_ext: Vector of external identified peptides, can be used to transfer ids from other runs
        :param proteins_ext: Vector of external identified proteins, can be used to transfer ids from other runs
        :param features: Feature detection results will be added here
        :param seeds: Optional seeds for feature detection from e.g. untargeted FeatureFinders
        """
        ...
    
    @overload
    def run(self, peptides: PeptideIdentificationList , proteins: List[ProteinIdentification] , peptides_ext: PeptideIdentificationList , proteins_ext: List[ProteinIdentification] , features: FeatureMap , seeds: FeatureMap , spectra_file: String ) -> None:
        """
        Cython signature: void run(PeptideIdentificationList peptides, libcpp_vector[ProteinIdentification] & proteins, PeptideIdentificationList peptides_ext, libcpp_vector[ProteinIdentification] proteins_ext, FeatureMap & features, FeatureMap & seeds, String & spectra_file)
        Run feature detection
        
        
        :param peptides: Vector of identified peptides
        :param proteins: Vector of identified proteins
        :param peptides_ext: Vector of external identified peptides, can be used to transfer ids from other runs
        :param proteins_ext: Vector of external identified proteins, can be used to transfer ids from other runs
        :param features: Feature detection results will be added here
        :param seeds: Optional seeds for feature detection from e.g. untargeted FeatureFinders
        :param spectra_file: Path will be stored in features in case the MSExperiment has no proper primaryMSRunPath
        """
        ...
    
    def runOnCandidates(self, features: FeatureMap ) -> None:
        """
        Cython signature: void runOnCandidates(FeatureMap & features)
        Run feature detection on identified features (e.g. loaded from an IdXML file)
        """
        ...
    
    def setMSData(self, in_0: MSExperiment ) -> None:
        """
        Cython signature: void setMSData(const MSExperiment &)
        Sets ms data
        """
        ...
    
    def getMSData(self) -> MSExperiment:
        """
        Cython signature: MSExperiment getMSData()
        Returns ms data as MSExperiment
        """
        ...
    
    def getChromatograms(self) -> MSExperiment:
        """
        Cython signature: MSExperiment getChromatograms()
        Returns chromatogram data as MSExperiment
        """
        ...
    
    def getLibrary(self) -> TargetedExperiment:
        """
        Cython signature: TargetedExperiment getLibrary()
        Returns constructed assay library
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


class FeatureGroupingAlgorithmUnlabeled:
    """
    Cython implementation of _FeatureGroupingAlgorithmUnlabeled

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1FeatureGroupingAlgorithmUnlabeled.html>`_
      -- Inherits from ['FeatureGroupingAlgorithm']
    """
    
    def __init__(self) -> None:
        """
        Cython signature: void FeatureGroupingAlgorithmUnlabeled()
        """
        ...
    
    def group(self, maps: List[FeatureMap] , out: ConsensusMap ) -> None:
        """
        Cython signature: void group(const libcpp_vector[FeatureMap] & maps, ConsensusMap & out)
        """
        ...
    
    def addToGroup(self, map_id: int , feature_map: FeatureMap ) -> None:
        """
        Cython signature: void addToGroup(int map_id, FeatureMap feature_map)
        """
        ...
    
    def setReference(self, map_id: int , map: FeatureMap ) -> None:
        """
        Cython signature: void setReference(int map_id, FeatureMap map)
        """
        ...
    
    def getResultMap(self) -> ConsensusMap:
        """
        Cython signature: ConsensusMap getResultMap()
        """
        ...
    
    def transferSubelements(self, maps: List[ConsensusMap] , out: ConsensusMap ) -> None:
        """
        Cython signature: void transferSubelements(libcpp_vector[ConsensusMap] maps, ConsensusMap & out)
        Transfers subelements (grouped features) from input consensus maps to the result consensus map
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


class GNPSMGFFile:
    """
    Cython implementation of _GNPSMGFFile

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1GNPSMGFFile.html>`_
      -- Inherits from ['DefaultParamHandler']
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void GNPSMGFFile()
        """
        ...
    
    @overload
    def __init__(self, in_0: GNPSMGFFile ) -> None:
        """
        Cython signature: void GNPSMGFFile(GNPSMGFFile &)
        """
        ...
    
    def store(self, consensus_file_path: Union[bytes, str, String] , mzml_file_paths: List[bytes] , out: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void store(const String & consensus_file_path, const StringList & mzml_file_paths, const String & out)
        Export consensus file from default workflow to GNPS MGF format
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


class IDConflictResolverAlgorithm:
    """
    Cython implementation of _IDConflictResolverAlgorithm

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1IDConflictResolverAlgorithm.html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void IDConflictResolverAlgorithm()
        Resolves ambiguous annotations of features with peptide identifications
        """
        ...
    
    @overload
    def __init__(self, in_0: IDConflictResolverAlgorithm ) -> None:
        """
        Cython signature: void IDConflictResolverAlgorithm(IDConflictResolverAlgorithm &)
        """
        ...
    
    @overload
    def resolve(self, features: FeatureMap ) -> None:
        """
        Cython signature: void resolve(FeatureMap & features)
        Resolves ambiguous annotations of features with peptide identifications\n
        
        The the filtered identifications are added to the vector of unassigned peptides
        and also reduced to a single best hit
        
        
        :param keep_matching: Keeps all IDs that match the modified sequence of the best hit in the feature (e.g. keeps all IDs in a ConsensusMap if id'd same across multiple runs)
        """
        ...
    
    @overload
    def resolve(self, features: ConsensusMap ) -> None:
        """
        Cython signature: void resolve(ConsensusMap & features)
        Resolves ambiguous annotations of consensus features with peptide identifications\n
        
        The the filtered identifications are added to the vector of unassigned peptides
        and also reduced to a single best hit
        
        
        :param keep_matching: Keeps all IDs that match the modified sequence of the best hit in the feature (e.g. keeps all IDs in a ConsensusMap if id'd same across multiple runs)
        """
        ...
    
    @overload
    def resolveBetweenFeatures(self, features: FeatureMap ) -> None:
        """
        Cython signature: void resolveBetweenFeatures(FeatureMap & features)
        In a single (feature/consensus) map, features with the same (possibly modified) sequence and charge state may appear\n
        
        This filter removes the peptide sequence annotations from features, if a higher-intensity feature with the same (charge, sequence)
        combination exists in the map. The total number of features remains unchanged. In the final output, each (charge, sequence) combination
        appears only once, i.e. no multiplicities
        """
        ...
    
    @overload
    def resolveBetweenFeatures(self, features: ConsensusMap ) -> None:
        """
        Cython signature: void resolveBetweenFeatures(ConsensusMap & features)
        In a single (feature/consensus) map, features with the same (possibly modified) sequence and charge state may appear\n
        
        This filter removes the peptide sequence annotations from features, if a higher-intensity feature with the same (charge, sequence)
        combination exists in the map. The total number of features remains unchanged. In the final output, each (charge, sequence) combination
        appears only once, i.e. no multiplicities
        """
        ... 


class InspectInfile:
    """
    Cython implementation of _InspectInfile

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1InspectInfile.html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void InspectInfile()
        Inspect input file adapter
        """
        ...
    
    @overload
    def __init__(self, in_0: InspectInfile ) -> None:
        """
        Cython signature: void InspectInfile(InspectInfile &)
        """
        ...
    
    def store(self, filename: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void store(const String & filename)
        Stores the experiment data in an Inspect input file that can be used as input for Inspect shell execution
        """
        ...
    
    def handlePTMs(self, modification_line: Union[bytes, str, String] , modifications_filename: Union[bytes, str, String] , monoisotopic: bool ) -> None:
        """
        Cython signature: void handlePTMs(const String & modification_line, const String & modifications_filename, bool monoisotopic)
        Retrieves the name, mass change, affected residues, type and position for all modifications from a string
        
        
        :param modification_line:
        :param modifications_filename:
        :param monoisotopic: if true, masses are considered to be monoisotopic
        :raises:
          Exception: FileNotReadable if the modifications_filename could not be read
        :raises:
          Exception: FileNotFound if modifications_filename could not be found
        :raises:
          Exception: ParseError if modifications_filename could not be parsed
        """
        ...
    
    def getSpectra(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getSpectra()
        Specifies a spectrum file to search
        """
        ...
    
    def setSpectra(self, spectra: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setSpectra(const String & spectra)
        Specifies a spectrum file to search
        """
        ...
    
    def getDb(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getDb()
        Specifies the name of a database (.trie file) to search
        """
        ...
    
    def setDb(self, db: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setDb(const String & db)
        Specifies the name of a database (.trie file) to search
        """
        ...
    
    def getEnzyme(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getEnzyme()
        Specifies the name of a enzyme. "Trypsin", "None", and "Chymotrypsin" are the available values
        """
        ...
    
    def setEnzyme(self, enzyme: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setEnzyme(const String & enzyme)
        Specifies the name of a enzyme. "Trypsin", "None", and "Chymotrypsin" are the available values
        """
        ...
    
    def getModificationsPerPeptide(self) -> int:
        """
        Cython signature: int getModificationsPerPeptide()
        Number of PTMs permitted in a single peptide
        """
        ...
    
    def setModificationsPerPeptide(self, modifications_per_peptide: int ) -> None:
        """
        Cython signature: void setModificationsPerPeptide(int modifications_per_peptide)
        Number of PTMs permitted in a single peptide
        """
        ...
    
    def getBlind(self) -> int:
        """
        Cython signature: unsigned int getBlind()
        Run inspect in a blind mode
        """
        ...
    
    def setBlind(self, blind: int ) -> None:
        """
        Cython signature: void setBlind(unsigned int blind)
        Run inspect in a blind mode
        """
        ...
    
    def getMaxPTMsize(self) -> float:
        """
        Cython signature: float getMaxPTMsize()
        The maximum modification size (in Da) to consider in a blind search
        """
        ...
    
    def setMaxPTMsize(self, maxptmsize: float ) -> None:
        """
        Cython signature: void setMaxPTMsize(float maxptmsize)
        The maximum modification size (in Da) to consider in a blind search
        """
        ...
    
    def getPrecursorMassTolerance(self) -> float:
        """
        Cython signature: float getPrecursorMassTolerance()
        Specifies the parent mass tolerance, in Daltons
        """
        ...
    
    def setPrecursorMassTolerance(self, precursor_mass_tolerance: float ) -> None:
        """
        Cython signature: void setPrecursorMassTolerance(float precursor_mass_tolerance)
        Specifies the parent mass tolerance, in Daltons
        """
        ...
    
    def getPeakMassTolerance(self) -> float:
        """
        Cython signature: float getPeakMassTolerance()
        How far b and y peaks can be shifted from their expected masses.
        """
        ...
    
    def setPeakMassTolerance(self, peak_mass_tolerance: float ) -> None:
        """
        Cython signature: void setPeakMassTolerance(float peak_mass_tolerance)
        How far b and y peaks can be shifted from their expected masses
        """
        ...
    
    def getMulticharge(self) -> int:
        """
        Cython signature: unsigned int getMulticharge()
        If set to true, attempt to guess the precursor charge and mass, and consider multiple charge states if feasible
        """
        ...
    
    def setMulticharge(self, multicharge: int ) -> None:
        """
        Cython signature: void setMulticharge(unsigned int multicharge)
        If set to true, attempt to guess the precursor charge and mass, and consider multiple charge states if feasible
        """
        ...
    
    def getInstrument(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getInstrument()
        If set to QTOF, uses a QTOF-derived fragmentation model, and does not attempt to correct the parent mass
        """
        ...
    
    def setInstrument(self, instrument: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setInstrument(const String & instrument)
        If set to QTOF, uses a QTOF-derived fragmentation model, and does not attempt to correct the parent mass
        """
        ...
    
    def getTagCount(self) -> int:
        """
        Cython signature: int getTagCount()
        Number of tags to generate
        """
        ...
    
    def setTagCount(self, TagCount: int ) -> None:
        """
        Cython signature: void setTagCount(int TagCount)
        Number of tags to generate
        """
        ...
    
    def __richcmp__(self, other: InspectInfile, op: int) -> Any:
        ... 


class Kernel_MassTrace:
    """
    Cython implementation of _Kernel_MassTrace

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1Kernel_MassTrace.html>`_
    """
    
    fwhm_mz_avg: float
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void Kernel_MassTrace()
        """
        ...
    
    @overload
    def __init__(self, in_0: Kernel_MassTrace ) -> None:
        """
        Cython signature: void Kernel_MassTrace(Kernel_MassTrace &)
        """
        ...
    
    @overload
    def __init__(self, trace_peaks: List[Peak2D] ) -> None:
        """
        Cython signature: void Kernel_MassTrace(const libcpp_vector[Peak2D] & trace_peaks)
        """
        ...
    
    def getSize(self) -> int:
        """
        Cython signature: size_t getSize()
        Returns the number of peaks contained in the mass trace
        """
        ...
    
    def getLabel(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getLabel()
        Returns label of mass trace
        """
        ...
    
    def setLabel(self, label: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setLabel(String label)
        Sets label of mass trace
        """
        ...
    
    def getCentroidMZ(self) -> float:
        """
        Cython signature: double getCentroidMZ()
        Returns the centroid m/z
        """
        ...
    
    def getCentroidRT(self) -> float:
        """
        Cython signature: double getCentroidRT()
        Returns the centroid RT
        """
        ...
    
    def getCentroidSD(self) -> float:
        """
        Cython signature: double getCentroidSD()
        Returns the centroid SD
        """
        ...
    
    def getFWHM(self) -> float:
        """
        Cython signature: double getFWHM()
        Returns FWHM
        """
        ...
    
    def getTraceLength(self) -> float:
        """
        Cython signature: double getTraceLength()
        Returns the length of the trace (as difference in RT)
        """
        ...
    
    def getFWHMborders(self) -> List[int, int]:
        """
        Cython signature: libcpp_pair[size_t,size_t] getFWHMborders()
        Returns FWHM boarders
        """
        ...
    
    def getSmoothedIntensities(self) -> List[float]:
        """
        Cython signature: libcpp_vector[double] getSmoothedIntensities()
        Returns smoothed intensities (empty if no smoothing was explicitly done beforehand!)
        """
        ...
    
    def getAverageMS1CycleTime(self) -> float:
        """
        Cython signature: double getAverageMS1CycleTime()
        Returns average scan time of mass trace
        """
        ...
    
    def computeSmoothedPeakArea(self) -> float:
        """
        Cython signature: double computeSmoothedPeakArea()
        Sums all non-negative (smoothed!) intensities in the mass trace
        """
        ...
    
    def computePeakArea(self) -> float:
        """
        Cython signature: double computePeakArea()
        Sums intensities of all peaks in the mass trace
        """
        ...
    
    def computeIntensitySum(self) -> float:
        """
        Cython signature: double computeIntensitySum()
        Sum all peak intensities in the mass trace
        """
        ...
    
    def findMaxByIntPeak(self, in_0: bool ) -> int:
        """
        Cython signature: size_t findMaxByIntPeak(bool)
        Returns the index of the mass trace's highest peak within the MassTrace container (based either on raw or smoothed intensities)
        """
        ...
    
    def estimateFWHM(self, in_0: bool ) -> int:
        """
        Cython signature: size_t estimateFWHM(bool)
        Estimates FWHM of chromatographic peak in seconds (based on either raw or smoothed intensities)
        """
        ...
    
    def computeFwhmArea(self) -> float:
        """
        Cython signature: double computeFwhmArea()
        """
        ...
    
    def computeFwhmAreaSmooth(self) -> float:
        """
        Cython signature: double computeFwhmAreaSmooth()
        Computes chromatographic peak area within the FWHM range.
        """
        ...
    
    def getIntensity(self, in_0: bool ) -> float:
        """
        Cython signature: double getIntensity(bool)
        Returns the intensity
        """
        ...
    
    def getMaxIntensity(self, in_0: bool ) -> float:
        """
        Cython signature: double getMaxIntensity(bool)
        Returns the max intensity
        """
        ...
    
    def getConvexhull(self) -> ConvexHull2D:
        """
        Cython signature: ConvexHull2D getConvexhull()
        Returns the mass trace's convex hull
        """
        ...
    
    def setCentroidSD(self, tmp_sd: float ) -> None:
        """
        Cython signature: void setCentroidSD(double & tmp_sd)
        """
        ...
    
    def setSmoothedIntensities(self, db_vec: List[float] ) -> None:
        """
        Cython signature: void setSmoothedIntensities(libcpp_vector[double] & db_vec)
        Sets smoothed intensities (smoothing is done externally, e.g. by LowessSmoothing)
        """
        ...
    
    def updateSmoothedMaxRT(self) -> None:
        """
        Cython signature: void updateSmoothedMaxRT()
        """
        ...
    
    def updateWeightedMeanRT(self) -> None:
        """
        Cython signature: void updateWeightedMeanRT()
        Compute & update centroid RT as a intensity-weighted mean of RTs
        """
        ...
    
    def updateSmoothedWeightedMeanRT(self) -> None:
        """
        Cython signature: void updateSmoothedWeightedMeanRT()
        """
        ...
    
    def updateMedianRT(self) -> None:
        """
        Cython signature: void updateMedianRT()
        Compute & update centroid RT as median position of intensities
        """
        ...
    
    def updateMedianMZ(self) -> None:
        """
        Cython signature: void updateMedianMZ()
        Compute & update centroid m/z as median of m/z values
        """
        ...
    
    def updateMeanMZ(self) -> None:
        """
        Cython signature: void updateMeanMZ()
        Compute & update centroid m/z as mean of m/z values
        """
        ...
    
    def updateWeightedMeanMZ(self) -> None:
        """
        Cython signature: void updateWeightedMeanMZ()
        Compute & update centroid m/z as weighted mean of m/z values
        """
        ...
    
    def updateWeightedMZsd(self) -> None:
        """
        Cython signature: void updateWeightedMZsd()
        Compute & update m/z standard deviation of mass trace as weighted mean of m/z values
        
        Make sure to call update(Weighted)(Mean|Median)MZ() first! <br>
        use getCentroidSD() to get result
        """
        ...
    
    def setQuantMethod(self, method: int ) -> None:
        """
        Cython signature: void setQuantMethod(MT_QUANTMETHOD method)
        Determine if area or median is used for quantification
        """
        ...
    
    def getQuantMethod(self) -> int:
        """
        Cython signature: MT_QUANTMETHOD getQuantMethod()
        Check if area or median is used for quantification
        """
        ... 


class LightMRMTransitionGroupCP:
    """
    Cython implementation of _MRMTransitionGroup[_MSChromatogram,_LightTransition]

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1MRMTransitionGroup[_MSChromatogram,_LightTransition].html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void LightMRMTransitionGroupCP()
        """
        ...
    
    @overload
    def __init__(self, in_0: LightMRMTransitionGroupCP ) -> None:
        """
        Cython signature: void LightMRMTransitionGroupCP(LightMRMTransitionGroupCP &)
        """
        ...
    
    def size(self) -> int:
        """
        Cython signature: size_t size()
        """
        ...
    
    def getTransitionGroupID(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getTransitionGroupID()
        """
        ...
    
    def setTransitionGroupID(self, tr_gr_id: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setTransitionGroupID(String tr_gr_id)
        """
        ...
    
    def getTransitions(self) -> List[LightTransition]:
        """
        Cython signature: libcpp_vector[LightTransition] getTransitions()
        """
        ...
    
    def getTransitionsMuteable(self) -> List[LightTransition]:
        """
        Cython signature: libcpp_vector[LightTransition] getTransitionsMuteable()
        """
        ...
    
    def addTransition(self, transition: LightTransition , key: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void addTransition(LightTransition transition, String key)
        """
        ...
    
    def getTransition(self, key: Union[bytes, str, String] ) -> LightTransition:
        """
        Cython signature: LightTransition getTransition(String key)
        """
        ...
    
    def hasTransition(self, key: Union[bytes, str, String] ) -> bool:
        """
        Cython signature: bool hasTransition(String key)
        """
        ...
    
    def getChromatograms(self) -> List[MSChromatogram]:
        """
        Cython signature: libcpp_vector[MSChromatogram] getChromatograms()
        """
        ...
    
    def addChromatogram(self, chromatogram: MSChromatogram , key: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void addChromatogram(MSChromatogram chromatogram, String key)
        """
        ...
    
    def getChromatogram(self, key: Union[bytes, str, String] ) -> MSChromatogram:
        """
        Cython signature: MSChromatogram getChromatogram(String key)
        """
        ...
    
    def hasChromatogram(self, key: Union[bytes, str, String] ) -> bool:
        """
        Cython signature: bool hasChromatogram(String key)
        """
        ...
    
    def getPrecursorChromatograms(self) -> List[MSChromatogram]:
        """
        Cython signature: libcpp_vector[MSChromatogram] getPrecursorChromatograms()
        """
        ...
    
    def addPrecursorChromatogram(self, chromatogram: MSChromatogram , key: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void addPrecursorChromatogram(MSChromatogram chromatogram, String key)
        """
        ...
    
    def getPrecursorChromatogram(self, key: Union[bytes, str, String] ) -> MSChromatogram:
        """
        Cython signature: MSChromatogram getPrecursorChromatogram(String key)
        """
        ...
    
    def hasPrecursorChromatogram(self, key: Union[bytes, str, String] ) -> bool:
        """
        Cython signature: bool hasPrecursorChromatogram(String key)
        """
        ...
    
    def getFeatures(self) -> List[MRMFeature]:
        """
        Cython signature: libcpp_vector[MRMFeature] getFeatures()
        """
        ...
    
    def getFeaturesMuteable(self) -> List[MRMFeature]:
        """
        Cython signature: libcpp_vector[MRMFeature] getFeaturesMuteable()
        """
        ...
    
    def addFeature(self, feature: MRMFeature ) -> None:
        """
        Cython signature: void addFeature(MRMFeature feature)
        """
        ...
    
    def getBestFeature(self) -> MRMFeature:
        """
        Cython signature: MRMFeature getBestFeature()
        """
        ...
    
    def getLibraryIntensity(self, result: List[float] ) -> None:
        """
        Cython signature: void getLibraryIntensity(libcpp_vector[double] result)
        """
        ...
    
    def subset(self, tr_ids: List[Union[bytes, str]] ) -> LightMRMTransitionGroupCP:
        """
        Cython signature: LightMRMTransitionGroupCP subset(libcpp_vector[libcpp_utf8_string] tr_ids)
        """
        ...
    
    def isInternallyConsistent(self) -> bool:
        """
        Cython signature: bool isInternallyConsistent()
        """
        ...
    
    def chromatogramIdsMatch(self) -> bool:
        """
        Cython signature: bool chromatogramIdsMatch()
        """
        ... 


class LinearInterpolation:
    """
    Cython implementation of _LinearInterpolation[double,double]

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS::Math_1_1LinearInterpolation[double,double].html>`_

    Provides access to linearly interpolated values (and
    derivatives) from discrete data points.  Values beyond the given range
    of data points are implicitly taken as zero.
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void LinearInterpolation()
        """
        ...
    
    @overload
    def __init__(self, in_0: LinearInterpolation ) -> None:
        """
        Cython signature: void LinearInterpolation(LinearInterpolation &)
        """
        ...
    
    @overload
    def __init__(self, scale: float , offset: float ) -> None:
        """
        Cython signature: void LinearInterpolation(double scale, double offset)
        """
        ...
    
    def value(self, arg_pos: float ) -> float:
        """
        Cython signature: double value(double arg_pos)
        Returns the interpolated value
        """
        ...
    
    def addValue(self, arg_pos: float , arg_value: float ) -> None:
        """
        Cython signature: void addValue(double arg_pos, double arg_value)
        Performs linear resampling. The `arg_value` is split up and added to the data points around `arg_pos`
        """
        ...
    
    def derivative(self, arg_pos: float ) -> float:
        """
        Cython signature: double derivative(double arg_pos)
        Returns the interpolated derivative
        """
        ...
    
    def getData(self) -> List[float]:
        """
        Cython signature: libcpp_vector[double] getData()
        Returns the internal random access container from which interpolated values are being sampled
        """
        ...
    
    def setData(self, data: List[float] ) -> None:
        """
        Cython signature: void setData(libcpp_vector[double] & data)
        Assigns data to the internal random access container from which interpolated values are being sampled
        """
        ...
    
    def empty(self) -> bool:
        """
        Cython signature: bool empty()
        Returns `true` if getData() is empty
        """
        ...
    
    def key2index(self, pos: float ) -> float:
        """
        Cython signature: double key2index(double pos)
        The transformation from "outside" to "inside" coordinates
        """
        ...
    
    def index2key(self, pos: float ) -> float:
        """
        Cython signature: double index2key(double pos)
        The transformation from "inside" to "outside" coordinates
        """
        ...
    
    def getScale(self) -> float:
        """
        Cython signature: double getScale()
        "Scale" is the difference (in "outside" units) between consecutive entries in "Data"
        """
        ...
    
    def setScale(self, scale: float ) -> None:
        """
        Cython signature: void setScale(double & scale)
        "Scale" is the difference (in "outside" units) between consecutive entries in "Data"
        """
        ...
    
    def getOffset(self) -> float:
        """
        Cython signature: double getOffset()
        "Offset" is the point (in "outside" units) which corresponds to "Data[0]"
        """
        ...
    
    def setOffset(self, offset: float ) -> None:
        """
        Cython signature: void setOffset(double & offset)
        "Offset" is the point (in "outside" units) which corresponds to "Data[0]"
        """
        ...
    
    @overload
    def setMapping(self, scale: float , inside: float , outside: float ) -> None:
        """
        Cython signature: void setMapping(double & scale, double & inside, double & outside)
        """
        ...
    
    @overload
    def setMapping(self, inside_low: float , outside_low: float , inside_high: float , outside_high: float ) -> None:
        """
        Cython signature: void setMapping(double & inside_low, double & outside_low, double & inside_high, double & outside_high)
        """
        ...
    
    def getInsideReferencePoint(self) -> float:
        """
        Cython signature: double getInsideReferencePoint()
        """
        ...
    
    def getOutsideReferencePoint(self) -> float:
        """
        Cython signature: double getOutsideReferencePoint()
        """
        ...
    
    def supportMin(self) -> float:
        """
        Cython signature: double supportMin()
        """
        ...
    
    def supportMax(self) -> float:
        """
        Cython signature: double supportMax()
        """
        ... 


class MRMFeatureFilter:
    """
    Cython implementation of _MRMFeatureFilter

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1MRMFeatureFilter.html>`_
      -- Inherits from ['DefaultParamHandler']
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void MRMFeatureFilter()
        """
        ...
    
    @overload
    def __init__(self, in_0: MRMFeatureFilter ) -> None:
        """
        Cython signature: void MRMFeatureFilter(MRMFeatureFilter &)
        """
        ...
    
    def FilterFeatureMap(self, features: FeatureMap , filter_criteria: MRMFeatureQC , transitions: TargetedExperiment ) -> None:
        """
        Cython signature: void FilterFeatureMap(FeatureMap features, MRMFeatureQC filter_criteria, TargetedExperiment transitions)
        Flags or filters features and subordinates in a FeatureMap
        
        
        :param features: FeatureMap to flag or filter
        :param filter_criteria: MRMFeatureQC class defining QC parameters
        :param transitions: Transitions from a TargetedExperiment
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


class MRMFeatureFinderScoring:
    """
    Cython implementation of _MRMFeatureFinderScoring

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1MRMFeatureFinderScoring.html>`_
      -- Inherits from ['DefaultParamHandler', 'ProgressLogger']
    """
    
    def __init__(self) -> None:
        """
        Cython signature: void MRMFeatureFinderScoring()
        """
        ...
    
    def pickExperiment(self, chromatograms: MSExperiment , output: FeatureMap , transition_exp_: TargetedExperiment , trafo: TransformationDescription , swath_map: MSExperiment ) -> None:
        """
        Cython signature: void pickExperiment(MSExperiment & chromatograms, FeatureMap & output, TargetedExperiment & transition_exp_, TransformationDescription trafo, MSExperiment & swath_map)
        Pick features in one experiment containing chromatogram
        
        Function for for wrapping in Python, only uses OpenMS datastructures and does not return the map
        
        
        :param chromatograms: The input chromatograms
        :param output: The output features with corresponding scores
        :param transition_exp: The transition list describing the experiment
        :param trafo: Optional transformation of the experimental retention time to the normalized retention time space used in the transition list
        :param swath_map: Optional SWATH-MS (DIA) map corresponding from which the chromatograms were extracted
        """
        ...
    
    def setStrictFlag(self, flag: bool ) -> None:
        """
        Cython signature: void setStrictFlag(bool flag)
        """
        ...
    
    @overload
    def setMS1Map(self, ms1_map: SpectrumAccessOpenMS ) -> None:
        """
        Cython signature: void setMS1Map(shared_ptr[SpectrumAccessOpenMS] ms1_map)
        """
        ...
    
    @overload
    def setMS1Map(self, ms1_map: SpectrumAccessOpenMSCached ) -> None:
        """
        Cython signature: void setMS1Map(shared_ptr[SpectrumAccessOpenMSCached] ms1_map)
        """
        ...
    
    def scorePeakgroups(self, transition_group: LightMRMTransitionGroupCP , trafo: TransformationDescription , swath_maps: List[SwathMap] , output: FeatureMap , ms1only: bool ) -> None:
        """
        Cython signature: void scorePeakgroups(LightMRMTransitionGroupCP transition_group, TransformationDescription trafo, libcpp_vector[SwathMap] swath_maps, FeatureMap & output, bool ms1only)
        Score all peak groups of a transition group
        
        Iterate through all features found along the chromatograms of the transition group and score each one individually
        
        
        :param transition_group: The MRMTransitionGroup to be scored (input)
        :param trafo: Optional transformation of the experimental retention time
            to the normalized retention time space used in thetransition list
        :param swath_maps: Optional SWATH-MS (DIA) map corresponding from which
            the chromatograms were extracted. Use empty map if no data is available
        :param output: The output features with corresponding scores (the found
            features will be added to this FeatureMap)
        :param ms1only: Whether to only do MS1 scoring and skip all MS2 scoring
        """
        ...
    
    def prepareProteinPeptideMaps_(self, transition_exp: LightTargetedExperiment ) -> None:
        """
        Cython signature: void prepareProteinPeptideMaps_(LightTargetedExperiment & transition_exp)
        Prepares the internal mappings of peptides and proteins
        
        Calling this method _is_ required before calling scorePeakgroups
        
        
        :param transition_exp: The transition list describing the experiment
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


class MRMTransitionGroupCP:
    """
    Cython implementation of _MRMTransitionGroup[_MSChromatogram,_ReactionMonitoringTransition]

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1MRMTransitionGroup[_MSChromatogram,_ReactionMonitoringTransition].html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void MRMTransitionGroupCP()
        """
        ...
    
    @overload
    def __init__(self, in_0: MRMTransitionGroupCP ) -> None:
        """
        Cython signature: void MRMTransitionGroupCP(MRMTransitionGroupCP &)
        """
        ...
    
    def size(self) -> int:
        """
        Cython signature: size_t size()
        """
        ...
    
    def getTransitionGroupID(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getTransitionGroupID()
        """
        ...
    
    def setTransitionGroupID(self, tr_gr_id: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setTransitionGroupID(String tr_gr_id)
        """
        ...
    
    def getTransitions(self) -> List[ReactionMonitoringTransition]:
        """
        Cython signature: libcpp_vector[ReactionMonitoringTransition] getTransitions()
        """
        ...
    
    def getTransitionsMuteable(self) -> List[ReactionMonitoringTransition]:
        """
        Cython signature: libcpp_vector[ReactionMonitoringTransition] getTransitionsMuteable()
        """
        ...
    
    def addTransition(self, transition: ReactionMonitoringTransition , key: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void addTransition(ReactionMonitoringTransition transition, String key)
        """
        ...
    
    def getTransition(self, key: Union[bytes, str, String] ) -> ReactionMonitoringTransition:
        """
        Cython signature: ReactionMonitoringTransition getTransition(String key)
        """
        ...
    
    def hasTransition(self, key: Union[bytes, str, String] ) -> bool:
        """
        Cython signature: bool hasTransition(String key)
        """
        ...
    
    def getChromatograms(self) -> List[MSChromatogram]:
        """
        Cython signature: libcpp_vector[MSChromatogram] getChromatograms()
        """
        ...
    
    def addChromatogram(self, chromatogram: MSChromatogram , key: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void addChromatogram(MSChromatogram chromatogram, String key)
        """
        ...
    
    def getChromatogram(self, key: Union[bytes, str, String] ) -> MSChromatogram:
        """
        Cython signature: MSChromatogram getChromatogram(String key)
        """
        ...
    
    def hasChromatogram(self, key: Union[bytes, str, String] ) -> bool:
        """
        Cython signature: bool hasChromatogram(String key)
        """
        ...
    
    def getPrecursorChromatograms(self) -> List[MSChromatogram]:
        """
        Cython signature: libcpp_vector[MSChromatogram] getPrecursorChromatograms()
        """
        ...
    
    def addPrecursorChromatogram(self, chromatogram: MSChromatogram , key: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void addPrecursorChromatogram(MSChromatogram chromatogram, String key)
        """
        ...
    
    def getPrecursorChromatogram(self, key: Union[bytes, str, String] ) -> MSChromatogram:
        """
        Cython signature: MSChromatogram getPrecursorChromatogram(String key)
        """
        ...
    
    def hasPrecursorChromatogram(self, key: Union[bytes, str, String] ) -> bool:
        """
        Cython signature: bool hasPrecursorChromatogram(String key)
        """
        ...
    
    def getFeatures(self) -> List[MRMFeature]:
        """
        Cython signature: libcpp_vector[MRMFeature] getFeatures()
        """
        ...
    
    def getFeaturesMuteable(self) -> List[MRMFeature]:
        """
        Cython signature: libcpp_vector[MRMFeature] getFeaturesMuteable()
        """
        ...
    
    def addFeature(self, feature: MRMFeature ) -> None:
        """
        Cython signature: void addFeature(MRMFeature feature)
        """
        ...
    
    def getBestFeature(self) -> MRMFeature:
        """
        Cython signature: MRMFeature getBestFeature()
        """
        ...
    
    def getLibraryIntensity(self, result: List[float] ) -> None:
        """
        Cython signature: void getLibraryIntensity(libcpp_vector[double] result)
        """
        ...
    
    def subset(self, tr_ids: List[Union[bytes, str]] ) -> MRMTransitionGroupCP:
        """
        Cython signature: MRMTransitionGroupCP subset(libcpp_vector[libcpp_utf8_string] tr_ids)
        """
        ...
    
    def isInternallyConsistent(self) -> bool:
        """
        Cython signature: bool isInternallyConsistent()
        """
        ...
    
    def chromatogramIdsMatch(self) -> bool:
        """
        Cython signature: bool chromatogramIdsMatch()
        """
        ... 


class MSNumpressCoder:
    """
    Cython implementation of _MSNumpressCoder

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1MSNumpressCoder.html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void MSNumpressCoder()
        """
        ...
    
    @overload
    def __init__(self, in_0: MSNumpressCoder ) -> None:
        """
        Cython signature: void MSNumpressCoder(MSNumpressCoder &)
        """
        ...
    
    def encodeNP(self, in_: List[float] , result: String , zlib_compression: bool , config: NumpressConfig ) -> None:
        """
        Cython signature: void encodeNP(libcpp_vector[double] in_, String & result, bool zlib_compression, NumpressConfig config)
        Encodes a vector of floating point numbers into a Base64 string using numpress
        
        This code is obtained from the proteowizard implementation
        ./pwiz/pwiz/data/msdata/BinaryDataEncoder.cpp (adapted by Hannes Roest)
        
        This function will first apply the numpress encoding to the data, then
        encode the result in base64 (with optional zlib compression before
        base64 encoding)
        
        :note In case of error, result string is empty
        
        
        :param in: The vector of floating point numbers to be encoded
        :param result: The resulting string
        :param zlib_compression: Whether to apply zlib compression after numpress compression
        :param config: The numpress configuration defining the compression strategy
        """
        ...
    
    def decodeNP(self, in_: Union[bytes, str, String] , out: List[float] , zlib_compression: bool , config: NumpressConfig ) -> None:
        """
        Cython signature: void decodeNP(const String & in_, libcpp_vector[double] & out, bool zlib_compression, NumpressConfig config)
        Decodes a Base64 string to a vector of floating point numbers using numpress
        
        This code is obtained from the proteowizard implementation
        ./pwiz/pwiz/data/msdata/BinaryDataEncoder.cpp (adapted by Hannes Roest)
        
        This function will first decode the input base64 string (with optional
        zlib decompression after decoding) and then apply numpress decoding to
        the data
        
        
        :param in: The base64 encoded string
        :param out: The resulting vector of doubles
        :param zlib_compression: Whether to apply zlib de-compression before numpress de-compression
        :param config: The numpress configuration defining the compression strategy
        :raises:
          Exception: ConversionError if the string cannot be converted
        """
        ...
    
    def encodeNPRaw(self, in_: List[float] , result: String , config: NumpressConfig ) -> None:
        """
        Cython signature: void encodeNPRaw(libcpp_vector[double] in_, String & result, NumpressConfig config)
        Encode the data vector "in" to a raw byte array
        
        :note In case of error, "result" is given back unmodified
        :note The result is not a string but a raw byte array and may contain zero bytes
        
        This performs the raw numpress encoding on a set of data and does no
        Base64 encoding on the result. Therefore the result string is likely
        *unsafe* to handle and is a raw byte array.
        
        Please use the safe versions above unless you need access to the raw
        byte arrays
        
        
        :param in: The vector of floating point numbers to be encoded
        :param result: The resulting string
        :param config: The numpress configuration defining the compression strategy
        """
        ...
    
    def decodeNPRaw(self, in_: Union[bytes, str, String] , out: List[float] , config: NumpressConfig ) -> None:
        """
        Cython signature: void decodeNPRaw(const String & in_, libcpp_vector[double] & out, NumpressConfig config)
        Decode the raw byte array "in" to the result vector "out"
        
        :note The string in should *only* contain the data and _no_ extra
        null terminating byte
        
        This performs the raw numpress decoding on a raw byte array (not Base64
        encoded). Therefore the input string is likely *unsafe* to handle and is
        basically a byte container
        
        Please use the safe versions above unless you need access to the raw
        byte arrays
        
        
        :param in: The base64 encoded string
        :param out: The resulting vector of doubles
        :param config: The numpress configuration defining the compression strategy
        """
        ...
    NumpressCompression : __NumpressCompression 


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


class MatrixDouble:
    """
    Cython implementation of _Matrix[double]

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1Matrix[double].html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void MatrixDouble()
        """
        ...
    
    @overload
    def __init__(self, in_0: MatrixDouble ) -> None:
        """
        Cython signature: void MatrixDouble(MatrixDouble)
        """
        ...
    
    @overload
    def __init__(self, rows: int , cols: int , value: float ) -> None:
        """
        Cython signature: void MatrixDouble(size_t rows, size_t cols, double value)
        """
        ...
    
    def getValue(self, i: int , j: int ) -> float:
        """
        Cython signature: double getValue(size_t i, size_t j)
        """
        ...
    
    def setValue(self, i: int , j: int , value: float ) -> None:
        """
        Cython signature: void setValue(size_t i, size_t j, double value)
        """
        ...
    
    def rows(self) -> int:
        """
        Cython signature: size_t rows()
        """
        ...
    
    def cols(self) -> int:
        """
        Cython signature: size_t cols()
        """
        ...
    
    def size(self) -> int:
        """
        Cython signature: size_t size()
        """
        ...
    
    def resize(self, rows: int , cols: int ) -> None:
        """
        Cython signature: void resize(size_t rows, size_t cols)
        """
        ... 


class ModifiedPeptideGenerator:
    """
    Cython implementation of _ModifiedPeptideGenerator

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1ModifiedPeptideGenerator.html>`_

    Generates modified peptides/proteins.
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void ModifiedPeptideGenerator()
        """
        ...
    
    @overload
    def __init__(self, in_0: ModifiedPeptideGenerator ) -> None:
        """
        Cython signature: void ModifiedPeptideGenerator(ModifiedPeptideGenerator &)
        """
        ...
    
    @staticmethod
    def getModifications(modNames: List[bytes] ) -> ModifiedPeptideGenerator_MapToResidueType:
        """
        Cython signature: ModifiedPeptideGenerator_MapToResidueType getModifications(const StringList & modNames)
        """
        ...
    
    @staticmethod
    def applyFixedModifications(fixed_mods: ModifiedPeptideGenerator_MapToResidueType , peptide: AASequence ) -> None:
        """
        Cython signature: void applyFixedModifications(const ModifiedPeptideGenerator_MapToResidueType & fixed_mods, AASequence & peptide)
        """
        ...
    
    @staticmethod
    def applyVariableModifications(var_mods: ModifiedPeptideGenerator_MapToResidueType , peptide: AASequence , max_variable_mods_per_peptide: int , all_modified_peptides: List[AASequence] , keep_original: bool ) -> None:
        """
        Cython signature: void applyVariableModifications(const ModifiedPeptideGenerator_MapToResidueType & var_mods, const AASequence & peptide, size_t max_variable_mods_per_peptide, libcpp_vector[AASequence] & all_modified_peptides, bool keep_original)
        """
        ... 


class ModifiedPeptideGenerator_MapToResidueType:
    """
    Cython implementation of _ModifiedPeptideGenerator_MapToResidueType

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1ModifiedPeptideGenerator_MapToResidueType.html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void ModifiedPeptideGenerator_MapToResidueType()
        """
        ...
    
    @overload
    def __init__(self, in_0: ModifiedPeptideGenerator_MapToResidueType ) -> None:
        """
        Cython signature: void ModifiedPeptideGenerator_MapToResidueType(ModifiedPeptideGenerator_MapToResidueType &)
        """
        ... 


class MultiplexDeltaMasses:
    """
    Cython implementation of _MultiplexDeltaMasses

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1MultiplexDeltaMasses.html>`_

    Data structure for mass shift pattern
    
    Groups of labelled peptides appear with characteristic mass shifts
    
    For example, for an Arg6 labeled SILAC peptide pair we expect to see
    mass shifts of 0 and 6 Da. Or as second example, for a
    peptide pair of a dimethyl labelled sample with a single lysine
    we will see mass shifts of 56 Da and 64 Da.
    28 Da (N-term) + 28 Da (K) and 34 Da (N-term) + 34 Da (K)
    for light and heavy partners respectively
    
    The data structure stores the mass shifts and corresponding labels
    for a group of matching peptide features
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void MultiplexDeltaMasses()
        """
        ...
    
    @overload
    def __init__(self, in_0: MultiplexDeltaMasses ) -> None:
        """
        Cython signature: void MultiplexDeltaMasses(MultiplexDeltaMasses &)
        """
        ...
    
    @overload
    def __init__(self, dm: List[MultiplexDeltaMasses_DeltaMass] ) -> None:
        """
        Cython signature: void MultiplexDeltaMasses(libcpp_vector[MultiplexDeltaMasses_DeltaMass] & dm)
        """
        ...
    
    def getDeltaMasses(self) -> List[MultiplexDeltaMasses_DeltaMass]:
        """
        Cython signature: libcpp_vector[MultiplexDeltaMasses_DeltaMass] getDeltaMasses()
        """
        ... 


class MultiplexDeltaMasses_DeltaMass:
    """
    Cython implementation of _MultiplexDeltaMasses_DeltaMass

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1MultiplexDeltaMasses_DeltaMass.html>`_
    """
    
    delta_mass: float
    
    @overload
    def __init__(self, dm: float , l: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void MultiplexDeltaMasses_DeltaMass(double dm, String l)
        """
        ...
    
    @overload
    def __init__(self, in_0: MultiplexDeltaMasses_DeltaMass ) -> None:
        """
        Cython signature: void MultiplexDeltaMasses_DeltaMass(MultiplexDeltaMasses_DeltaMass &)
        """
        ... 


class MultiplexIsotopicPeakPattern:
    """
    Cython implementation of _MultiplexIsotopicPeakPattern

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1MultiplexIsotopicPeakPattern.html>`_
    """
    
    @overload
    def __init__(self, c: int , ppp: int , ms: MultiplexDeltaMasses , msi: int ) -> None:
        """
        Cython signature: void MultiplexIsotopicPeakPattern(int c, int ppp, MultiplexDeltaMasses ms, int msi)
        """
        ...
    
    @overload
    def __init__(self, in_0: MultiplexIsotopicPeakPattern ) -> None:
        """
        Cython signature: void MultiplexIsotopicPeakPattern(MultiplexIsotopicPeakPattern &)
        """
        ...
    
    def getCharge(self) -> int:
        """
        Cython signature: int getCharge()
        Returns charge
        """
        ...
    
    def getPeaksPerPeptide(self) -> int:
        """
        Cython signature: int getPeaksPerPeptide()
        Returns peaks per peptide
        """
        ...
    
    def getMassShifts(self) -> MultiplexDeltaMasses:
        """
        Cython signature: MultiplexDeltaMasses getMassShifts()
        Returns mass shifts
        """
        ...
    
    def getMassShiftIndex(self) -> int:
        """
        Cython signature: int getMassShiftIndex()
        Returns mass shift index
        """
        ...
    
    def getMassShiftCount(self) -> int:
        """
        Cython signature: unsigned int getMassShiftCount()
        Returns number of mass shifts i.e. the number of peptides in the multiplet
        """
        ...
    
    def getMassShiftAt(self, i: int ) -> float:
        """
        Cython signature: double getMassShiftAt(int i)
        Returns mass shift at position i
        """
        ...
    
    def getMZShiftAt(self, i: int ) -> float:
        """
        Cython signature: double getMZShiftAt(int i)
        Returns m/z shift at position i
        """
        ...
    
    def getMZShiftCount(self) -> int:
        """
        Cython signature: unsigned int getMZShiftCount()
        Returns number of m/z shifts
        """
        ... 


class MzTabFile:
    """
    Cython implementation of _MzTabFile

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1MzTabFile.html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void MzTabFile()
        """
        ...
    
    @overload
    def __init__(self, in_0: MzTabFile ) -> None:
        """
        Cython signature: void MzTabFile(MzTabFile &)
        """
        ...
    
    def store(self, filename: Union[bytes, str, String] , mz_tab: MzTab ) -> None:
        """
        Cython signature: void store(String filename, MzTab & mz_tab)
        Stores MzTab file
        """
        ...
    
    def load(self, filename: Union[bytes, str, String] , mz_tab: MzTab ) -> None:
        """
        Cython signature: void load(String filename, MzTab & mz_tab)
        Loads MzTab file
        """
        ... 


class NASequence:
    """
    Cython implementation of _NASequence

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1NASequence.html>`_

    Representation of an RNA sequence
    This class represents nucleic acid sequences in OpenMS. An NASequence
    instance primarily contains a sequence of ribonucleotides.
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void NASequence()
        """
        ...
    
    @overload
    def __init__(self, in_0: NASequence ) -> None:
        """
        Cython signature: void NASequence(NASequence &)
        """
        ...
    
    def getSequence(self) -> List[Ribonucleotide]:
        """
        Cython signature: libcpp_vector[const Ribonucleotide *] getSequence()
        """
        ...
    
    def __getitem__(self, index: int ) -> Ribonucleotide:
        """
        Cython signature: const Ribonucleotide * operator[](size_t index)
        """
        ...
    
    def empty(self) -> bool:
        """
        Cython signature: bool empty()
        Check if sequence is empty
        """
        ...
    
    def setSequence(self, seq: List[Ribonucleotide] ) -> None:
        """
        Cython signature: void setSequence(const libcpp_vector[const Ribonucleotide *] & seq)
        """
        ...
    
    def toString(self) -> Union[bytes, str, String]:
        """
        Cython signature: String toString()
        Returns the peptide as string with modifications embedded in brackets
        """
        ...
    
    def setFivePrimeMod(self, modification: Ribonucleotide ) -> None:
        """
        Cython signature: void setFivePrimeMod(const Ribonucleotide * modification)
        Sets the 5' modification
        """
        ...
    
    def getFivePrimeMod(self) -> Ribonucleotide:
        """
        Cython signature: const Ribonucleotide * getFivePrimeMod()
        Returns the name (ID) of the N-terminal modification, or an empty string if none is set
        """
        ...
    
    def setThreePrimeMod(self, modification: Ribonucleotide ) -> None:
        """
        Cython signature: void setThreePrimeMod(const Ribonucleotide * modification)
        Sets the 3' modification
        """
        ...
    
    def getThreePrimeMod(self) -> Ribonucleotide:
        """
        Cython signature: const Ribonucleotide * getThreePrimeMod()
        """
        ...
    
    def get(self, index: int ) -> Ribonucleotide:
        """
        Cython signature: const Ribonucleotide * get(size_t index)
        Returns the residue at position index
        """
        ...
    
    def set(self, index: int , r: Ribonucleotide ) -> None:
        """
        Cython signature: void set(size_t index, const Ribonucleotide * r)
        Sets the residue at position index
        """
        ...
    
    @overload
    def getFormula(self, ) -> EmpiricalFormula:
        """
        Cython signature: EmpiricalFormula getFormula()
        Returns the formula of the peptide
        """
        ...
    
    @overload
    def getFormula(self, type_: int , charge: int ) -> EmpiricalFormula:
        """
        Cython signature: EmpiricalFormula getFormula(NASFragmentType type_, int charge)
        """
        ...
    
    @overload
    def getAverageWeight(self, ) -> float:
        """
        Cython signature: double getAverageWeight()
        Returns the average weight of the peptide
        """
        ...
    
    @overload
    def getAverageWeight(self, type_: int , charge: int ) -> float:
        """
        Cython signature: double getAverageWeight(NASFragmentType type_, int charge)
        """
        ...
    
    @overload
    def getMonoWeight(self, ) -> float:
        """
        Cython signature: double getMonoWeight()
        Returns the mono isotopic weight of the peptide
        """
        ...
    
    @overload
    def getMonoWeight(self, type_: int , charge: int ) -> float:
        """
        Cython signature: double getMonoWeight(NASFragmentType type_, int charge)
        """
        ...
    
    def size(self) -> int:
        """
        Cython signature: size_t size()
        Returns the number of residues
        """
        ...
    
    def getPrefix(self, length: int ) -> NASequence:
        """
        Cython signature: NASequence getPrefix(size_t length)
        Returns a peptide sequence of the first index residues
        """
        ...
    
    def getSuffix(self, length: int ) -> NASequence:
        """
        Cython signature: NASequence getSuffix(size_t length)
        Returns a peptide sequence of the last index residues
        """
        ...
    
    def getSubsequence(self, start: int , length: int ) -> NASequence:
        """
        Cython signature: NASequence getSubsequence(size_t start, size_t length)
        Returns a peptide sequence of number residues, beginning at position index
        """
        ...
    
    def __str__(self) -> Union[bytes, str, String]:
        """
        Cython signature: String toString()
        Returns the peptide as string with modifications embedded in brackets
        """
        ...
    
    def __richcmp__(self, other: NASequence, op: int) -> Any:
        ...
    NASFragmentType : __NASFragmentType
    
    fromString: __static_NASequence_fromString 


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


class NumpressConfig:
    """
    Cython implementation of _NumpressConfig

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1NumpressConfig.html>`_
    """
    
    numpressFixedPoint: float
    
    numpressErrorTolerance: float
    
    np_compression: int
    
    estimate_fixed_point: bool
    
    linear_fp_mass_acc: float
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void NumpressConfig()
        """
        ...
    
    @overload
    def __init__(self, in_0: NumpressConfig ) -> None:
        """
        Cython signature: void NumpressConfig(NumpressConfig &)
        """
        ...
    
    def setCompression(self, compression: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setCompression(const String & compression)
        """
        ... 


class OPXLHelper:
    """
    Cython implementation of _OPXLHelper

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1OPXLHelper.html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void OPXLHelper()
        """
        ...
    
    @overload
    def __init__(self, in_0: OPXLHelper ) -> None:
        """
        Cython signature: void OPXLHelper(OPXLHelper &)
        """
        ...
    
    def enumerateCrossLinksAndMasses(self, peptides: List[AASeqWithMass] , cross_link_mass_light: float , cross_link_mass_mono_link: List[float] , cross_link_residue1: List[bytes] , cross_link_residue2: List[bytes] , spectrum_precursors: List[float] , precursor_correction_positions: List[int] , precursor_mass_tolerance: float , precursor_mass_tolerance_unit_ppm: bool ) -> List[XLPrecursor]:
        """
        Cython signature: libcpp_vector[XLPrecursor] enumerateCrossLinksAndMasses(const libcpp_vector[AASeqWithMass] peptides, double cross_link_mass_light, DoubleList cross_link_mass_mono_link, StringList cross_link_residue1, StringList cross_link_residue2, const libcpp_vector[double] & spectrum_precursors, libcpp_vector[int] & precursor_correction_positions, double precursor_mass_tolerance, bool precursor_mass_tolerance_unit_ppm)
        """
        ...
    
    def digestDatabase(self, fasta_db: List[FASTAEntry] , digestor: EnzymaticDigestion , min_peptide_length: int , cross_link_residue1: List[bytes] , cross_link_residue2: List[bytes] , fixed_modifications: ModifiedPeptideGenerator_MapToResidueType , variable_modifications: ModifiedPeptideGenerator_MapToResidueType , max_variable_mods_per_peptide: int ) -> List[AASeqWithMass]:
        """
        Cython signature: libcpp_vector[AASeqWithMass] digestDatabase(libcpp_vector[FASTAEntry] fasta_db, EnzymaticDigestion digestor, size_t min_peptide_length, StringList cross_link_residue1, StringList cross_link_residue2, ModifiedPeptideGenerator_MapToResidueType & fixed_modifications, ModifiedPeptideGenerator_MapToResidueType & variable_modifications, size_t max_variable_mods_per_peptide)
        """
        ...
    
    def buildCandidates(self, candidates: List[XLPrecursor] , precursor_corrections: List[int] , precursor_correction_positions: List[int] , peptide_masses: List[AASeqWithMass] , cross_link_residue1: List[bytes] , cross_link_residue2: List[bytes] , cross_link_mass: float , cross_link_mass_mono_link: List[float] , spectrum_precursor_vector: List[float] , allowed_error_vector: List[float] , cross_link_name: Union[bytes, str, String] ) -> List[ProteinProteinCrossLink]:
        """
        Cython signature: libcpp_vector[ProteinProteinCrossLink] buildCandidates(libcpp_vector[XLPrecursor] & candidates, libcpp_vector[int] & precursor_corrections, libcpp_vector[int] & precursor_correction_positions, libcpp_vector[AASeqWithMass] & peptide_masses, const StringList & cross_link_residue1, const StringList & cross_link_residue2, double cross_link_mass, DoubleList cross_link_mass_mono_link, libcpp_vector[double] & spectrum_precursor_vector, libcpp_vector[double] & allowed_error_vector, String cross_link_name)
        """
        ...
    
    def buildFragmentAnnotations(self, frag_annotations: List[PeptideHit_PeakAnnotation] , matching: List[List[int, int]] , theoretical_spectrum: MSSpectrum , experiment_spectrum: MSSpectrum ) -> None:
        """
        Cython signature: void buildFragmentAnnotations(libcpp_vector[PeptideHit_PeakAnnotation] & frag_annotations, libcpp_vector[libcpp_pair[size_t,size_t]] matching, MSSpectrum theoretical_spectrum, MSSpectrum experiment_spectrum)
        """
        ...
    
    def buildPeptideIDs(self, peptide_ids: PeptideIdentificationList , top_csms_spectrum: List[CrossLinkSpectrumMatch] , all_top_csms: List[List[CrossLinkSpectrumMatch]] , all_top_csms_current_index: int , spectra: MSExperiment , scan_index: int , scan_index_heavy: int ) -> None:
        """
        Cython signature: void buildPeptideIDs(PeptideIdentificationList & peptide_ids, libcpp_vector[CrossLinkSpectrumMatch] top_csms_spectrum, libcpp_vector[libcpp_vector[CrossLinkSpectrumMatch]] & all_top_csms, size_t all_top_csms_current_index, MSExperiment spectra, size_t scan_index, size_t scan_index_heavy)
        """
        ...
    
    def addProteinPositionMetaValues(self, peptide_ids: PeptideIdentificationList ) -> None:
        """
        Cython signature: void addProteinPositionMetaValues(PeptideIdentificationList & peptide_ids)
        """
        ...
    
    def addXLTargetDecoyMV(self, peptide_ids: PeptideIdentificationList ) -> None:
        """
        Cython signature: void addXLTargetDecoyMV(PeptideIdentificationList & peptide_ids)
        """
        ...
    
    def addBetaAccessions(self, peptide_ids: PeptideIdentificationList ) -> None:
        """
        Cython signature: void addBetaAccessions(PeptideIdentificationList & peptide_ids)
        """
        ...
    
    def removeBetaPeptideHits(self, peptide_ids: PeptideIdentificationList ) -> None:
        """
        Cython signature: void removeBetaPeptideHits(PeptideIdentificationList & peptide_ids)
        """
        ...
    
    def addPercolatorFeatureList(self, prot_id: ProteinIdentification ) -> None:
        """
        Cython signature: void addPercolatorFeatureList(ProteinIdentification & prot_id)
        """
        ...
    
    def computeDeltaScores(self, peptide_ids: PeptideIdentificationList ) -> None:
        """
        Cython signature: void computeDeltaScores(PeptideIdentificationList & peptide_ids)
        """
        ...
    
    def combineTopRanksFromPairs(self, peptide_ids: PeptideIdentificationList , number_top_hits: int ) -> PeptideIdentificationList:
        """
        Cython signature: PeptideIdentificationList combineTopRanksFromPairs(PeptideIdentificationList & peptide_ids, size_t number_top_hits)
        """
        ...
    
    def collectPrecursorCandidates(self, precursor_correction_steps: List[int] , precursor_mass: float , precursor_mass_tolerance: float , precursor_mass_tolerance_unit_ppm: bool , filtered_peptide_masses: List[AASeqWithMass] , cross_link_mass: float , cross_link_mass_mono_link: List[float] , cross_link_residue1: List[bytes] , cross_link_residue2: List[bytes] , cross_link_name: Union[bytes, str, String] , use_sequence_tags: bool , tags: List[Union[bytes, str]] ) -> List[ProteinProteinCrossLink]:
        """
        Cython signature: libcpp_vector[ProteinProteinCrossLink] collectPrecursorCandidates(IntList precursor_correction_steps, double precursor_mass, double precursor_mass_tolerance, bool precursor_mass_tolerance_unit_ppm, libcpp_vector[AASeqWithMass] filtered_peptide_masses, double cross_link_mass, DoubleList cross_link_mass_mono_link, StringList cross_link_residue1, StringList cross_link_residue2, String cross_link_name, bool use_sequence_tags, const libcpp_vector[libcpp_utf8_string] & tags)
        """
        ...
    
    def computePrecursorError(self, csm: CrossLinkSpectrumMatch , precursor_mz: float , precursor_charge: int ) -> float:
        """
        Cython signature: double computePrecursorError(CrossLinkSpectrumMatch csm, double precursor_mz, int precursor_charge)
        """
        ...
    
    def isoPeakMeans(self, csm: CrossLinkSpectrumMatch , num_iso_peaks_array: IntegerDataArray , matched_spec_linear_alpha: List[List[int, int]] , matched_spec_linear_beta: List[List[int, int]] , matched_spec_xlinks_alpha: List[List[int, int]] , matched_spec_xlinks_beta: List[List[int, int]] ) -> None:
        """
        Cython signature: void isoPeakMeans(CrossLinkSpectrumMatch & csm, IntegerDataArray & num_iso_peaks_array, libcpp_vector[libcpp_pair[size_t,size_t]] & matched_spec_linear_alpha, libcpp_vector[libcpp_pair[size_t,size_t]] & matched_spec_linear_beta, libcpp_vector[libcpp_pair[size_t,size_t]] & matched_spec_xlinks_alpha, libcpp_vector[libcpp_pair[size_t,size_t]] & matched_spec_xlinks_beta)
        """
        ... 


class OSW_ChromExtractParams:
    """
    Cython implementation of _OSW_ChromExtractParams

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1OSW_ChromExtractParams.html>`_
    """
    
    min_upper_edge_dist: float
    
    mz_extraction_window: float
    
    ppm: bool
    
    extraction_function: bytes
    
    rt_extraction_window: float
    
    extra_rt_extract: float
    
    im_extraction_window: float
    
    def __init__(self, in_0: OSW_ChromExtractParams ) -> None:
        """
        Cython signature: void OSW_ChromExtractParams(OSW_ChromExtractParams &)
        """
        ... 


class OpenSwathHelper:
    """
    Cython implementation of _OpenSwathHelper

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1OpenSwathHelper.html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void OpenSwathHelper()
        """
        ...
    
    @overload
    def __init__(self, in_0: OpenSwathHelper ) -> None:
        """
        Cython signature: void OpenSwathHelper(OpenSwathHelper &)
        """
        ...
    
    def checkSwathMapAndSelectTransitions(self, exp: MSExperiment , targeted_exp: TargetedExperiment , transition_exp_used: TargetedExperiment , min_upper_edge_dist: float ) -> bool:
        """
        Cython signature: bool checkSwathMapAndSelectTransitions(MSExperiment & exp, TargetedExperiment & targeted_exp, TargetedExperiment & transition_exp_used, double min_upper_edge_dist)
        """
        ...
    
    def estimateRTRange(self, exp: LightTargetedExperiment ) -> List[float, float]:
        """
        Cython signature: libcpp_pair[double,double] estimateRTRange(LightTargetedExperiment exp)
        Computes the min and max retention time value
        
        Estimate the retention time span of a targeted experiment by returning the min/max values in retention time as a pair
        
        
        :return: A std `pair` that contains (min,max)
        """
        ...
    
    def computePrecursorId(self, transition_group_id: Union[bytes, str, String] , isotope: int ) -> Union[bytes, str, String]:
        """
        Cython signature: String computePrecursorId(const String & transition_group_id, int isotope)
        Computes unique precursor identifier
        
        Uses transition_group_id and isotope number to compute a unique precursor
        id of the form "groupID_Precursor_ix" where x is the isotope number, e.g.
        the monoisotopic precursor would become "groupID_Precursor_i0"
        
        
        :param transition_group_id: Unique id of the transition group (peptide/compound)
        :param isotope: Precursor isotope number
        :return: Unique precursor identifier
        """
        ... 


class OpenSwathOSWWriter:
    """
    Cython implementation of _OpenSwathOSWWriter

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1OpenSwathOSWWriter.html>`_
    """
    
    @overload
    def __init__(self, output_filename: Union[bytes, str, String] , run_id: int , input_filename: Union[bytes, str, String] , uis_scores: bool ) -> None:
        """
        Cython signature: void OpenSwathOSWWriter(String output_filename, uint64_t run_id, String input_filename, bool uis_scores)
        """
        ...
    
    @overload
    def __init__(self, in_0: OpenSwathOSWWriter ) -> None:
        """
        Cython signature: void OpenSwathOSWWriter(OpenSwathOSWWriter &)
        """
        ...
    
    def isActive(self) -> bool:
        """
        Cython signature: bool isActive()
        """
        ...
    
    def writeHeader(self) -> None:
        """
        Cython signature: void writeHeader()
        Initializes file by generating SQLite tables
        """
        ...
    
    def prepareLine(self, compound: LightCompound , tr: LightTransition , output: FeatureMap , id_: Union[bytes, str, String] ) -> Union[bytes, str, String]:
        """
        Cython signature: String prepareLine(LightCompound & compound, LightTransition * tr, FeatureMap & output, String id_)
        Prepare a single line (feature) for output
        
        The result can be flushed to disk using writeLines (either line by line or after collecting several lines)
        
        
        :param pep: The compound (peptide/metabolite) used for extraction
        :param transition: The transition used for extraction
        :param output: The feature map containing all features (each feature will generate one entry in the output)
        :param id: The transition group identifier (peptide/metabolite id)
        :return: A String to be written using writeLines
        """
        ...
    
    def writeLines(self, to_osw_output: List[bytes] ) -> None:
        """
        Cython signature: void writeLines(libcpp_vector[String] to_osw_output)
        Write data to disk
        
        Takes a set of pre-prepared data statements from prepareLine and flushes them to disk
        
        
        :param to_osw_output: Statements generated by prepareLine
        """
        ... 


class Peak2D:
    """
    Cython implementation of _Peak2D

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1Peak2D.html>`_

    A 2-dimensional raw data point or peak.
    
    This data structure is intended for continuous data or peak data.
    If you want to annotated single peaks with meta data, use RichPeak2D instead
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void Peak2D()
        """
        ...
    
    @overload
    def __init__(self, in_0: Peak2D ) -> None:
        """
        Cython signature: void Peak2D(Peak2D &)
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
    
    def __richcmp__(self, other: Peak2D, op: int) -> Any:
        ... 


class PepXMLFile:
    """
    Cython implementation of _PepXMLFile

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1PepXMLFile.html>`_
    """
    
    def __init__(self) -> None:
        """
        Cython signature: void PepXMLFile()
        """
        ...
    
    @overload
    def load(self, filename: Union[bytes, str, String] , protein_ids: List[ProteinIdentification] , peptide_ids: PeptideIdentificationList ) -> None:
        """
        Cython signature: void load(String filename, libcpp_vector[ProteinIdentification] & protein_ids, PeptideIdentificationList & peptide_ids)
        """
        ...
    
    @overload
    def load(self, filename: Union[bytes, str, String] , protein_ids: List[ProteinIdentification] , peptide_ids: PeptideIdentificationList , experiment_name: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void load(String filename, libcpp_vector[ProteinIdentification] & protein_ids, PeptideIdentificationList & peptide_ids, String experiment_name)
        """
        ...
    
    @overload
    def load(self, filename: Union[bytes, str, String] , protein_ids: List[ProteinIdentification] , peptide_ids: PeptideIdentificationList , experiment_name: Union[bytes, str, String] , lookup: SpectrumMetaDataLookup ) -> None:
        """
        Cython signature: void load(String filename, libcpp_vector[ProteinIdentification] & protein_ids, PeptideIdentificationList & peptide_ids, String experiment_name, SpectrumMetaDataLookup lookup)
        """
        ...
    
    @overload
    def store(self, filename: Union[bytes, str, String] , protein_ids: List[ProteinIdentification] , peptide_ids: PeptideIdentificationList ) -> None:
        """
        Cython signature: void store(String filename, libcpp_vector[ProteinIdentification] & protein_ids, PeptideIdentificationList & peptide_ids)
        """
        ...
    
    @overload
    def store(self, filename: Union[bytes, str, String] , protein_ids: List[ProteinIdentification] , peptide_ids: PeptideIdentificationList , mz_file: Union[bytes, str, String] , mz_name: Union[bytes, str, String] , peptideprophet_analyzed: bool , rt_tolerance: float ) -> None:
        """
        Cython signature: void store(String filename, libcpp_vector[ProteinIdentification] & protein_ids, PeptideIdentificationList & peptide_ids, String mz_file, String mz_name, bool peptideprophet_analyzed, double rt_tolerance)
        """
        ...
    
    def keepNativeSpectrumName(self, keep: bool ) -> None:
        """
        Cython signature: void keepNativeSpectrumName(bool keep)
        """
        ...
    
    def setParseUnknownScores(self, parse_unknown_scores: bool ) -> None:
        """
        Cython signature: void setParseUnknownScores(bool parse_unknown_scores)
        """
        ... 


class PeptideEvidence:
    """
    Cython implementation of _PeptideEvidence

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1PeptideEvidence.html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void PeptideEvidence()
        """
        ...
    
    @overload
    def __init__(self, in_0: PeptideEvidence ) -> None:
        """
        Cython signature: void PeptideEvidence(PeptideEvidence &)
        """
        ...
    
    def setStart(self, start: int ) -> None:
        """
        Cython signature: void setStart(int start)
        Sets the position of the last AA of the peptide in protein coordinates (starting at 0 for the N-terminus). If not available, set to UNKNOWN_POSITION. N-terminal positions must be marked with `N_TERMINAL_AA`
        """
        ...
    
    def getStart(self) -> int:
        """
        Cython signature: int getStart()
        Returns the position in the protein (starting at 0 for the N-terminus). If not available UNKNOWN_POSITION constant is returned
        """
        ...
    
    def setEnd(self, end: int ) -> None:
        """
        Cython signature: void setEnd(int end)
        Sets the position of the last AA of the peptide in protein coordinates (starting at 0 for the N-terminus). If not available, set UNKNOWN_POSITION. C-terminal positions must be marked with C_TERMINAL_AA
        """
        ...
    
    def getEnd(self) -> int:
        """
        Cython signature: int getEnd()
        Returns the position of the last AA of the peptide in protein coordinates (starting at 0 for the N-terminus). If not available UNKNOWN_POSITION constant is returned
        """
        ...
    
    def setAABefore(self, rhs: bytes ) -> None:
        """
        Cython signature: void setAABefore(char rhs)
        Sets the amino acid single letter code before the sequence (preceding amino acid in the protein). If not available, set to UNKNOWN_AA. If N-terminal set to N_TERMINAL_AA
        """
        ...
    
    def getAABefore(self) -> bytes:
        """
        Cython signature: char getAABefore()
        Returns the amino acid single letter code before the sequence (preceding amino acid in the protein). If not available, UNKNOWN_AA is returned. If N-terminal, N_TERMINAL_AA is returned
        """
        ...
    
    def setAAAfter(self, rhs: bytes ) -> None:
        """
        Cython signature: void setAAAfter(char rhs)
        Sets the amino acid single letter code after the sequence (subsequent amino acid in the protein). If not available, set to UNKNOWN_AA. If C-terminal set to C_TERMINAL_AA
        """
        ...
    
    def getAAAfter(self) -> bytes:
        """
        Cython signature: char getAAAfter()
        Returns the amino acid single letter code after the sequence (subsequent amino acid in the protein). If not available, UNKNOWN_AA is returned. If C-terminal, C_TERMINAL_AA is returned
        """
        ...
    
    def setProteinAccession(self, s: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setProteinAccession(String s)
        Sets the protein accession the peptide matches to. If not available set to empty string
        """
        ...
    
    def getProteinAccession(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getProteinAccession()
        Returns the protein accession the peptide matches to. If not available the empty string is returned
        """
        ...
    
    def hasValidLimits(self) -> bool:
        """
        Cython signature: bool hasValidLimits()
        Start and end numbers in evidence represent actual numeric indices
        """
        ...
    
    def __richcmp__(self, other: PeptideEvidence, op: int) -> Any:
        ... 


class PeptideIdentification:
    """
    Cython implementation of _PeptideIdentification

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1PeptideIdentification.html>`_
      -- Inherits from ['MetaInfoInterface']

    Represents peptide identification results for a single spectrum or feature
    
    PeptideIdentification stores the results of peptide identification from database
    search engines (e.g., Mascot, X!Tandem, MSGF+). Each PeptideIdentification contains:
    
    - A list of peptide hits (candidate sequences) ranked by score
    - The precursor m/z and retention time
    - Score type and significance threshold
    - Link to the ProteinIdentification (via identifier)
    
    Multiple PeptideIdentifications can belong to one ProteinIdentification, which
    stores the search parameters and protein-level results.
    
    Example usage:
    
    .. code-block:: python
    
       pep_id = oms.PeptideIdentification()
       pep_id.setRT(1234.5)  # Set retention time
       pep_id.setMZ(445.678)  # Set precursor m/z
       pep_id.setScoreType("XTandem")
       # Add a peptide hit
       hit = oms.PeptideHit()
       hit.setScore(50.5)
       hit.setRank(1)
       hit.setSequence(oms.AASequence.fromString("PEPTIDE"))
       hit.setCharge(2)
       pep_id.insertHit(hit)
       # Access hits
       for hit in pep_id.getHits():
           print(f"Sequence: {hit.getSequence().toString()}, Score: {hit.getScore()}")
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void PeptideIdentification()
        """
        ...
    
    @overload
    def __init__(self, in_0: PeptideIdentification ) -> None:
        """
        Cython signature: void PeptideIdentification(PeptideIdentification &)
        """
        ...
    
    def getHits(self) -> List[PeptideHit]:
        """
        Cython signature: libcpp_vector[PeptideHit] getHits()
        Returns all peptide hits (candidate sequences)
        
        :return: List of peptide candidates ranked by score
        
        Hits are typically sorted by score, with the best hit at index 0
        """
        ...
    
    def insertHit(self, in_0: PeptideHit ) -> None:
        """
        Cython signature: void insertHit(PeptideHit)
        Appends a peptide hit to the list
        
        :param hit: The peptide hit to add
        """
        ...
    
    def setHits(self, in_0: List[PeptideHit] ) -> None:
        """
        Cython signature: void setHits(libcpp_vector[PeptideHit])
        Sets all peptide hits at once
        
        :param hits: List of peptide hits to store
        """
        ...
    
    def getSignificanceThreshold(self) -> float:
        """
        Cython signature: double getSignificanceThreshold()
        Returns the significance threshold value
        
        :return: The threshold value (interpretation depends on score type)
        
        Hits with scores below/above this threshold (depending on score direction) may be considered insignificant
        """
        ...
    
    def setSignificanceThreshold(self, value: float ) -> None:
        """
        Cython signature: void setSignificanceThreshold(double value)
        Sets the significance threshold value
        
        :param value: The threshold value to set
        """
        ...
    
    def getScoreType(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getScoreType()
        Returns the type of score (e.g., "Mascot", "XTandem", "q-value")
        
        :return: Name of the score type
        """
        ...
    
    def setScoreType(self, in_0: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setScoreType(String)
        Sets the score type
        
        :param score_type: Name of the score type (e.g., "Mascot", "XTandem")
        """
        ...
    
    def isHigherScoreBetter(self) -> bool:
        """
        Cython signature: bool isHigherScoreBetter()
        Returns whether higher scores are better
        
        :return: True if higher scores indicate better matches, False if lower is better
        """
        ...
    
    def setHigherScoreBetter(self, in_0: bool ) -> None:
        """
        Cython signature: void setHigherScoreBetter(bool)
        Sets whether higher scores are better
        
        :param higher_better: True if higher scores are better, False otherwise
        """
        ...
    
    def getIdentifier(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getIdentifier()
        Returns the identifier linking to the parent ProteinIdentification
        
        :return: Unique identifier string
        
        Use this to find the corresponding ProteinIdentification with search parameters
        """
        ...
    
    def setIdentifier(self, in_0: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setIdentifier(String)
        Sets the identifier linking to a ProteinIdentification
        
        :param identifier: Unique identifier string
        """
        ...
    
    def hasMZ(self) -> bool:
        """
        Cython signature: bool hasMZ()
        Checks if m/z value is set
        
        :return: True if m/z is available, False otherwise
        """
        ...
    
    def getMZ(self) -> float:
        """
        Cython signature: double getMZ()
        Returns the precursor m/z value
        
        :return: Mass-to-charge ratio of the precursor ion
        """
        ...
    
    def setMZ(self, in_0: float ) -> None:
        """
        Cython signature: void setMZ(double)
        Sets the precursor m/z value
        
        :param mz: Mass-to-charge ratio of the precursor
        """
        ...
    
    def hasRT(self) -> bool:
        """
        Cython signature: bool hasRT()
        Checks if retention time is set
        
        :return: True if RT is available, False otherwise
        """
        ...
    
    def getRT(self) -> float:
        """
        Cython signature: double getRT()
        Returns the retention time of the precursor
        
        :return: Retention time in seconds
        """
        ...
    
    def setRT(self, in_0: float ) -> None:
        """
        Cython signature: void setRT(double)
        Sets the retention time of the precursor
        
        :param rt: Retention time in seconds
        """
        ...
    
    def getBaseName(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getBaseName()
        """
        ...
    
    def setBaseName(self, in_0: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setBaseName(String)
        """
        ...
    
    def getExperimentLabel(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getExperimentLabel()
        """
        ...
    
    def setExperimentLabel(self, in_0: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setExperimentLabel(String)
        """
        ...
    
    def sort(self) -> None:
        """
        Cython signature: void sort()
        """
        ...
    
    def empty(self) -> bool:
        """
        Cython signature: bool empty()
        """
        ...
    
    def getReferencingHits(self, in_0: List[PeptideHit] , in_1: Set[bytes] ) -> List[PeptideHit]:
        """
        Cython signature: libcpp_vector[PeptideHit] getReferencingHits(libcpp_vector[PeptideHit], libcpp_set[String] &)
        Returns all peptide hits which reference to a given protein accession (i.e. filter by protein accession)
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
    
    def __richcmp__(self, other: PeptideIdentification, op: int) -> Any:
        ... 


class PercolatorFeatureSetHelper:
    """
    Cython implementation of _PercolatorFeatureSetHelper

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1PercolatorFeatureSetHelper.html>`_

    Percolator feature set and integration helper
    
    This class contains functions to handle (compute, aggregate, integrate)
    Percolator features. This includes the calculation or extraction of
    Percolator features depending on the search engine(s) for later use with
    PercolatorAdapter. It also includes handling the reintegration of the
    percolator result into the set of Identifications
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void PercolatorFeatureSetHelper()
        """
        ...
    
    @overload
    def __init__(self, in_0: PercolatorFeatureSetHelper ) -> None:
        """
        Cython signature: void PercolatorFeatureSetHelper(PercolatorFeatureSetHelper &)
        """
        ...
    
    def concatMULTISEPeptideIds(self, all_peptide_ids: PeptideIdentificationList , new_peptide_ids: PeptideIdentificationList , search_engine: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void concatMULTISEPeptideIds(PeptideIdentificationList & all_peptide_ids, PeptideIdentificationList & new_peptide_ids, String search_engine)
        Appends a vector of PeptideIdentification to another and prepares Percolator features in MetaInfo (With the respective key "CONCAT:" + search_engine)
        
        
        :param all_peptide_ids: PeptideIdentification vector to append to
        :param new_peptide_ids: PeptideIdentification vector to be appended
        :param search_engine: Search engine to depend on for feature creation
        """
        ...
    
    def mergeMULTISEPeptideIds(self, all_peptide_ids: PeptideIdentificationList , new_peptide_ids: PeptideIdentificationList , search_engine: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void mergeMULTISEPeptideIds(PeptideIdentificationList & all_peptide_ids, PeptideIdentificationList & new_peptide_ids, String search_engine)
        Merges a vector of PeptideIdentification into another and prepares the merged MetaInfo and scores for collection in addMULTISEFeatures for feature registration
        
        
        :param all_peptide_idsL: PeptideIdentification vector to be merged into
        :param new_peptide_idsL: PeptideIdentification vector to merge
        :param search_engineL: Search engine to create features from their scores
        """
        ...
    
    def mergeMULTISEProteinIds(self, all_protein_ids: List[ProteinIdentification] , new_protein_ids: List[ProteinIdentification] ) -> None:
        """
        Cython signature: void mergeMULTISEProteinIds(libcpp_vector[ProteinIdentification] & all_protein_ids, libcpp_vector[ProteinIdentification] & new_protein_ids)
        Concatenates SearchParameter of multiple search engine runs and merges PeptideEvidences, collects used search engines in MetaInfo for collection in addMULTISEFeatures for feature registration
        
        
        :param all_protein_ids: ProteinIdentification vector to be merged into
        :param new_protein_ids: ProteinIdentification vector to merge
        """
        ...
    
    def addMSGFFeatures(self, peptide_ids: PeptideIdentificationList , feature_set: List[bytes] ) -> None:
        """
        Cython signature: void addMSGFFeatures(PeptideIdentificationList & peptide_ids, StringList & feature_set)
        Creates and adds MSGF+ specific Percolator features and registers them in feature_set. MSGF+ should be run with the addFeatures flag enabled
        
        
        :param peptide_ids: PeptideIdentification vector to create Percolator features in
        :param feature_set: Register of added features
        """
        ...
    
    def addXTANDEMFeatures(self, peptide_ids: PeptideIdentificationList , feature_set: List[bytes] ) -> None:
        """
        Cython signature: void addXTANDEMFeatures(PeptideIdentificationList & peptide_ids, StringList & feature_set)
        Creates and adds X!Tandem specific Percolator features and registers them in feature_set
        
        
        :param peptide_ids: PeptideIdentification vector to create Percolator features in
        :param feature_set: Register of added features
        """
        ...
    
    def addCOMETFeatures(self, peptide_ids: PeptideIdentificationList , feature_set: List[bytes] ) -> None:
        """
        Cython signature: void addCOMETFeatures(PeptideIdentificationList & peptide_ids, StringList & feature_set)
        Creates and adds Comet specific Percolator features and registers them in feature_set
        
        
        :param peptide_ids: PeptideIdentification vector to create Percolator features in
        :param feature_set: Register of added features
        """
        ...
    
    def addMASCOTFeatures(self, peptide_ids: PeptideIdentificationList , feature_set: List[bytes] ) -> None:
        """
        Cython signature: void addMASCOTFeatures(PeptideIdentificationList & peptide_ids, StringList & feature_set)
        Creates and adds Mascot specific Percolator features and registers them in feature_set
        
        
        :param peptide_ids: PeptideIdentification vector to create Percolator features in
        :param feature_set: Register of added features
        """
        ...
    
    def addMULTISEFeatures(self, peptide_ids: PeptideIdentificationList , search_engines_used: List[bytes] , feature_set: List[bytes] , complete_only: bool , limits_imputation: bool ) -> None:
        """
        Cython signature: void addMULTISEFeatures(PeptideIdentificationList & peptide_ids, StringList & search_engines_used, StringList & feature_set, bool complete_only, bool limits_imputation)
        Adds multiple search engine specific Percolator features and registers them in feature_set
        
        
        :param peptide_ids: PeptideIdentification vector to create Percolator features in
        :param search_engines_used: The list of search engines to be considered
        :param feature_set: Register of added features
        :param complete_only: Will only add features for PeptideIdentifications where all given search engines identified something
        :param limits_imputation: Uses C++ numeric limits as imputed values instead of min/max of that feature
        """
        ...
    
    def addCONCATSEFeatures(self, peptide_id_list: PeptideIdentificationList , search_engines_used: List[bytes] , feature_set: List[bytes] ) -> None:
        """
        Cython signature: void addCONCATSEFeatures(PeptideIdentificationList & peptide_id_list, StringList & search_engines_used, StringList & feature_set)
        Adds multiple search engine specific Percolator features and registers them in feature_set
        
        This struct can be used to store both peak or feature indices
        
        
        :param peptide_ids: PeptideIdentification vector to create Percolator features in
        :param search_engines_used: The list of search engines to be considered
        :param feature_set: Register of added features
        """
        ...
    
    def checkExtraFeatures(self, psms: List[PeptideHit] , extra_features: List[bytes] ) -> None:
        """
        Cython signature: void checkExtraFeatures(libcpp_vector[PeptideHit] & psms, StringList & extra_features)
        Checks and removes requested extra Percolator features that are actually unavailable (to compute)
        
        
        :param psms: The vector of PeptideHit to be checked
        :param extra_features: The list of requested extra features
        """
        ... 


class ProtXMLFile:
    """
    Cython implementation of _ProtXMLFile

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1ProtXMLFile.html>`_

    Used to load (storing not supported, yet) ProtXML files
    
    This class is used to load (storing not supported, yet) documents that implement
    the schema of ProtXML files
    """
    
    def __init__(self) -> None:
        """
        Cython signature: void ProtXMLFile()
        """
        ...
    
    def load(self, filename: Union[bytes, str, String] , protein_ids: ProteinIdentification , peptide_ids: PeptideIdentification ) -> None:
        """
        Cython signature: void load(String filename, ProteinIdentification & protein_ids, PeptideIdentification & peptide_ids)
        Loads the identifications of an ProtXML file without identifier
        
        The information is read in and the information is stored in the
        corresponding variables
        
        :raises:
          Exception: FileNotFound is thrown if the file could not be found
        :raises:
          Exception: ParseError is thrown if an error occurs during parsing
        """
        ...
    
    def store(self, filename: Union[bytes, str, String] , protein_ids: ProteinIdentification , peptide_ids: PeptideIdentification , document_id: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void store(String filename, ProteinIdentification & protein_ids, PeptideIdentification & peptide_ids, String document_id)
        """
        ... 


class SeedListGenerator:
    """
    Cython implementation of _SeedListGenerator

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1SeedListGenerator.html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void SeedListGenerator()
        """
        ...
    
    @overload
    def __init__(self, in_0: SeedListGenerator ) -> None:
        """
        Cython signature: void SeedListGenerator(SeedListGenerator &)
        """
        ...
    
    @overload
    def generateSeedList(self, exp: MSExperiment , seeds: '_np.ndarray[Any, _np.dtype[_np.float32]]' ) -> None:
        """
        Cython signature: void generateSeedList(MSExperiment exp, libcpp_vector[DPosition2] & seeds)
        Generate a seed list based on an MS experiment
        """
        ...
    
    @overload
    def generateSeedList(self, peptides: PeptideIdentificationList , seeds: '_np.ndarray[Any, _np.dtype[_np.float32]]' , use_peptide_mass: bool ) -> None:
        """
        Cython signature: void generateSeedList(PeptideIdentificationList & peptides, libcpp_vector[DPosition2] & seeds, bool use_peptide_mass)
        Generates a seed list based on a list of peptide identifications
        """
        ...
    
    @overload
    def convertSeedList(self, seeds: '_np.ndarray[Any, _np.dtype[_np.float32]]' , features: FeatureMap ) -> None:
        """
        Cython signature: void convertSeedList(libcpp_vector[DPosition2] & seeds, FeatureMap & features)
        Converts a list of seed positions to a feature map (expected format for FeatureFinder)
        """
        ...
    
    @overload
    def convertSeedList(self, features: FeatureMap , seeds: '_np.ndarray[Any, _np.dtype[_np.float32]]' ) -> None:
        """
        Cython signature: void convertSeedList(FeatureMap & features, libcpp_vector[DPosition2] & seeds)
        Converts a feature map with seed positions back to a simple list
        """
        ... 


class SignalToNoiseEstimatorMedian:
    """
    Cython implementation of _SignalToNoiseEstimatorMedian[_MSSpectrum]

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1SignalToNoiseEstimatorMedian[_MSSpectrum].html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void SignalToNoiseEstimatorMedian()
        """
        ...
    
    @overload
    def __init__(self, in_0: SignalToNoiseEstimatorMedian ) -> None:
        """
        Cython signature: void SignalToNoiseEstimatorMedian(SignalToNoiseEstimatorMedian &)
        """
        ...
    
    def init(self, spectrum: MSSpectrum ) -> None:
        """
        Cython signature: void init(MSSpectrum & spectrum)
        """
        ...
    
    def getSignalToNoise(self, index: int ) -> float:
        """
        Cython signature: double getSignalToNoise(size_t index)
        """
        ...
    
    def getSparseWindowPercent(self) -> float:
        """
        Cython signature: double getSparseWindowPercent()
        """
        ...
    
    def getHistogramRightmostPercent(self) -> float:
        """
        Cython signature: double getHistogramRightmostPercent()
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


class SiriusExportAlgorithm:
    """
    Cython implementation of _SiriusExportAlgorithm

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1SiriusExportAlgorithm.html>`_
      -- Inherits from ['DefaultParamHandler']
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void SiriusExportAlgorithm()
        """
        ...
    
    @overload
    def __init__(self, in_0: SiriusExportAlgorithm ) -> None:
        """
        Cython signature: void SiriusExportAlgorithm(SiriusExportAlgorithm &)
        """
        ...
    
    def isFeatureOnly(self) -> bool:
        """
        Cython signature: bool isFeatureOnly()
        """
        ...
    
    def getFilterByNumMassTraces(self) -> int:
        """
        Cython signature: unsigned int getFilterByNumMassTraces()
        """
        ...
    
    def getPrecursorMzTolerance(self) -> float:
        """
        Cython signature: double getPrecursorMzTolerance()
        """
        ...
    
    def getPrecursorRtTolerance(self) -> float:
        """
        Cython signature: double getPrecursorRtTolerance()
        """
        ...
    
    def precursorMzToleranceUnitIsPPM(self) -> bool:
        """
        Cython signature: bool precursorMzToleranceUnitIsPPM()
        """
        ...
    
    def isNoMasstraceInfoIsotopePattern(self) -> bool:
        """
        Cython signature: bool isNoMasstraceInfoIsotopePattern()
        """
        ...
    
    def getIsotopePatternIterations(self) -> int:
        """
        Cython signature: int getIsotopePatternIterations()
        """
        ...
    
    def preprocessing(self, featureXML_path: Union[bytes, str, String] , spectra: MSExperiment , feature_mapping_info: FeatureMapping_FeatureMappingInfo , feature_ms2_indices: FeatureMapping_FeatureToMs2Indices ) -> None:
        """
        Cython signature: void preprocessing(const String & featureXML_path, MSExperiment & spectra, FeatureMapping_FeatureMappingInfo & feature_mapping_info, FeatureMapping_FeatureToMs2Indices & feature_ms2_indices)
        Preprocessing needed for SIRIUS
        
        Filter number of masstraces and perform feature mapping
        
        :param featureXML_path: Path to featureXML
        :param spectra: Input of MSExperiment with spectra information
        :param feature_mapping_info: Emtpy - stores FeatureMaps and KDTreeMaps internally
        :param feature_ms2_indices: Empty FeatureToMs2Indices
        """
        ...
    
    def logFeatureSpectraNumber(self, featureXML_path: Union[bytes, str, String] , feature_ms2_indices: FeatureMapping_FeatureToMs2Indices , spectra: MSExperiment ) -> None:
        """
        Cython signature: void logFeatureSpectraNumber(const String & featureXML_path, FeatureMapping_FeatureToMs2Indices & feature_ms2_indices, MSExperiment & spectra)
        Logs number of features and spectra used
        
        Prints the number of features and spectra used (OPENMS_LOG_INFO)
        
        :param featureXML_path: Path to featureXML
        :param feature_ms2_indices: FeatureToMs2Indices with feature mapping
        :param spectra: Input of MSExperiment with spectra information
        """
        ...
    
    def run(self, mzML_files: List[bytes] , featureXML_files: List[bytes] , out_ms: Union[bytes, str, String] , out_compoundinfo: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void run(const StringList & mzML_files, const StringList & featureXML_files, const String & out_ms, const String & out_compoundinfo)
        Runs SiriusExport with mzML and featureXML (optional) files as input.
        
        Generates a SIRIUS .ms file and compound info table (optional).
        
        :param mzML_files: List with paths to mzML files
        :param featureXML_files: List with paths to featureXML files
        :param out_ms: Output file name for SIRIUS .ms file
        :param out_compoundinfo: Output file name for tsv file with compound info
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


class SwathWindowLoader:
    """
    Cython implementation of _SwathWindowLoader

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1SwathWindowLoader.html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void SwathWindowLoader()
        """
        ...
    
    @overload
    def __init__(self, in_0: SwathWindowLoader ) -> None:
        """
        Cython signature: void SwathWindowLoader(SwathWindowLoader &)
        """
        ...
    
    def annotateSwathMapsFromFile(self, filename: Union[bytes, str, String] , swath_maps: List[SwathMap] , do_sort: bool , force: bool ) -> None:
        """
        Cython signature: void annotateSwathMapsFromFile(String filename, libcpp_vector[SwathMap] & swath_maps, bool do_sort, bool force)
        """
        ...
    
    def readSwathWindows(self, filename: Union[bytes, str, String] , swath_prec_lower: List[float] , swath_prec_upper: List[float] ) -> None:
        """
        Cython signature: void readSwathWindows(String filename, libcpp_vector[double] & swath_prec_lower, libcpp_vector[double] & swath_prec_upper)
        """
        ... 


class TextFile:
    """
    Cython implementation of _TextFile

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1TextFile.html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void TextFile()
        This class provides some basic file handling methods for text files
        """
        ...
    
    @overload
    def __init__(self, in_0: TextFile ) -> None:
        """
        Cython signature: void TextFile(TextFile &)
        """
        ...
    
    @overload
    def __init__(self, filename: Union[bytes, str, String] , trim_linesalse: bool , first_n1: int ) -> None:
        """
        Cython signature: void TextFile(const String & filename, bool trim_linesalse, int first_n1)
        """
        ...
    
    def load(self, filename: Union[bytes, str, String] , trim_linesalse: bool , first_n1: int ) -> None:
        """
        Cython signature: void load(const String & filename, bool trim_linesalse, int first_n1)
        Loads data from a text file
        
        :param filename: The input file name
        :param trim_lines: Whether or not the lines are trimmed when reading them from file
        :param first_n: If set, only `first_n` lines the lines from the beginning of the file are read
        :param skip_empty_lines: Should empty lines be skipped? If used in conjunction with `trim_lines`, also lines with only whitespace will be skipped. Skipped lines do not count towards the total number of read lines
        """
        ...
    
    def store(self, filename: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void store(const String & filename)
        Writes the data to a file
        """
        ...
    
    def addLine(self, line: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void addLine(const String line)
        """
        ... 


class TransitionPQPFile:
    """
    Cython implementation of _TransitionPQPFile

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1TransitionPQPFile.html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void TransitionPQPFile()
        """
        ...
    
    @overload
    def __init__(self, in_0: TransitionPQPFile ) -> None:
        """
        Cython signature: void TransitionPQPFile(TransitionPQPFile &)
        """
        ...
    
    def convertTargetedExperimentToPQP(self, filename: bytes , targeted_exp: TargetedExperiment ) -> None:
        """
        Cython signature: void convertTargetedExperimentToPQP(char * filename, TargetedExperiment & targeted_exp)
        Write out a targeted experiment (TraML structure) into a PQP file
        
        :param filename: The output file
        :param targeted_exp: The targeted experiment
        """
        ...
    
    @overload
    def convertPQPToTargetedExperiment(self, filename: bytes , targeted_exp: TargetedExperiment , legacy_traml_id: bool ) -> None:
        """
        Cython signature: void convertPQPToTargetedExperiment(char * filename, TargetedExperiment & targeted_exp, bool legacy_traml_id)
        Read in a PQP file and construct a targeted experiment (TraML structure)
        
        :param filename: The input file
        :param targeted_exp: The output targeted experiment
        :param legacy_traml_id: Should legacy TraML IDs be used (boolean)?
        """
        ...
    
    @overload
    def convertPQPToTargetedExperiment(self, filename: bytes , targeted_exp: LightTargetedExperiment , legacy_traml_id: bool ) -> None:
        """
        Cython signature: void convertPQPToTargetedExperiment(char * filename, LightTargetedExperiment & targeted_exp, bool legacy_traml_id)
        Read in a PQP file and construct a targeted experiment (Light transition structure)
        
        :param filename: The input file
        :param targeted_exp: The output targeted experiment
        :param legacy_traml_id: Should legacy TraML IDs be used (boolean)?
        """
        ...
    
    def convertTargetedExperimentToTSV(self, filename: bytes , targeted_exp: TargetedExperiment ) -> None:
        """
        Cython signature: void convertTargetedExperimentToTSV(char * filename, TargetedExperiment & targeted_exp)
        """
        ...
    
    @overload
    def convertTSVToTargetedExperiment(self, filename: bytes , filetype: int , targeted_exp: TargetedExperiment ) -> None:
        """
        Cython signature: void convertTSVToTargetedExperiment(char * filename, FileType filetype, TargetedExperiment & targeted_exp)
        """
        ...
    
    @overload
    def convertTSVToTargetedExperiment(self, filename: bytes , filetype: int , targeted_exp: LightTargetedExperiment ) -> None:
        """
        Cython signature: void convertTSVToTargetedExperiment(char * filename, FileType filetype, LightTargetedExperiment & targeted_exp)
        """
        ...
    
    def validateTargetedExperiment(self, targeted_exp: TargetedExperiment ) -> None:
        """
        Cython signature: void validateTargetedExperiment(TargetedExperiment targeted_exp)
        """
        ... 


class Unit:
    """
    Cython implementation of _Unit

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1Unit.html>`_
    """
    
    accession: Union[bytes, str, String]
    
    name: Union[bytes, str, String]
    
    cv_ref: Union[bytes, str, String]
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void Unit()
        """
        ...
    
    @overload
    def __init__(self, in_0: Unit ) -> None:
        """
        Cython signature: void Unit(Unit)
        """
        ...
    
    @overload
    def __init__(self, p_accession: Union[bytes, str, String] , p_name: Union[bytes, str, String] , p_cv_ref: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void Unit(const String & p_accession, const String & p_name, const String & p_cv_ref)
        """
        ...
    
    def __richcmp__(self, other: Unit, op: int) -> Any:
        ... 


class AnnotationState:
    None
    FEATURE_ID_NONE : int
    FEATURE_ID_SINGLE : int
    FEATURE_ID_MULTIPLE_SAME : int
    FEATURE_ID_MULTIPLE_DIVERGENT : int
    SIZE_OF_ANNOTATIONSTATE : int

    def getMapping(self) -> Dict[int, str]:
       ... 


class __ByteOrder:
    None
    BYTEORDER_BIGENDIAN : int
    BYTEORDER_LITTLEENDIAN : int

    def getMapping(self) -> Dict[int, str]:
       ... 


class __CombinationsLogic:
    None
    OR : int
    AND : int
    XOR : int

    def getMapping(self) -> Dict[int, str]:
       ... 


class DimensionDescription:
    None
    RT : int
    MZ : int
    DIMENSION : int

    def getMapping(self) -> Dict[int, str]:
       ... 


class __IntensityThresholdCalculation:
    None
    MANUAL : int
    AUTOMAXBYSTDEV : int
    AUTOMAXBYPERCENT : int

    def getMapping(self) -> Dict[int, str]:
       ... 


class MT_QUANTMETHOD:
    None
    MT_QUANT_AREA : int
    MT_QUANT_MEDIAN : int
    SIZE_OF_MT_QUANTMETHOD : int

    def getMapping(self) -> Dict[int, str]:
       ... 


class __NASFragmentType:
    None
    Full : int
    Internal : int
    FivePrime : int
    ThreePrime : int
    AIon : int
    BIon : int
    CIon : int
    XIon : int
    YIon : int
    ZIon : int
    Precursor : int
    BIonMinusH20 : int
    YIonMinusH20 : int
    BIonMinusNH3 : int
    YIonMinusNH3 : int
    NonIdentified : int
    Unannotated : int
    WIon : int
    AminusB : int
    DIon : int
    SizeOfNASFragmentType : int

    def getMapping(self) -> Dict[int, str]:
       ... 


class __NumpressCompression:
    None
    NONE : int
    LINEAR : int
    PIC : int
    SLOF : int
    SIZE_OF_NUMPRESSCOMPRESSION : int

    def getMapping(self) -> Dict[int, str]:
       ... 


class __RequirementLevel:
    None
    MUST : int
    SHOULD : int
    MAY : int

    def getMapping(self) -> Dict[int, str]:
       ... 

