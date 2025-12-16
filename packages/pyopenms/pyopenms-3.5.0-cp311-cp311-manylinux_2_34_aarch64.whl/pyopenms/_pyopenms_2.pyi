from __future__ import annotations
from typing import overload, Any, List, Dict, Tuple, Set, Sequence, Union
from pyopenms import *  # pylint: disable=wildcard-import; lgtm(py/polluting-import)
import numpy as _np

from enum import IntEnum as _PyEnum


def __static_InternalCalibration_applyTransformation(pcs: List[Precursor] , trafo: MZTrafoModel ) -> None:
    """
    Cython signature: void applyTransformation(libcpp_vector[Precursor] & pcs, MZTrafoModel & trafo)
    """
    ...

def __static_InternalCalibration_applyTransformation(spec: MSSpectrum , target_mslvl: List[int] , trafo: MZTrafoModel ) -> None:
    """
    Cython signature: void applyTransformation(MSSpectrum & spec, IntList & target_mslvl, MZTrafoModel & trafo)
    """
    ...

def __static_InternalCalibration_applyTransformation(exp: MSExperiment , target_mslvl: List[int] , trafo: MZTrafoModel ) -> None:
    """
    Cython signature: void applyTransformation(MSExperiment & exp, IntList & target_mslvl, MZTrafoModel & trafo)
    """
    ...

def __static_TransformationDescription_getModelTypes(result: List[bytes] ) -> None:
    """
    Cython signature: void getModelTypes(StringList result)
    """
    ...

def __static_IMTypes_toDriftTimeUnit(dtu_string: bytes ) -> int:
    """
    Cython signature: DriftTimeUnit toDriftTimeUnit(const libcpp_string & dtu_string)
    """
    ...

def __static_IMTypes_toIMFormat(IM_format: bytes ) -> int:
    """
    Cython signature: IMFormat toIMFormat(const libcpp_string & IM_format)
    """
    ...

def __static_IMTypes_toString(value: int ) -> bytes:
    """
    Cython signature: libcpp_string toString(const DriftTimeUnit value)
    """
    ...

def __static_IMTypes_toString(value: int ) -> bytes:
    """
    Cython signature: libcpp_string toString(const IMFormat value)
    """
    ...


class AQS_featureConcentration:
    """
    Cython implementation of _AQS_featureConcentration

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1AQS_featureConcentration.html>`_
    """
    
    feature: Feature
    
    IS_feature: Feature
    
    actual_concentration: float
    
    IS_actual_concentration: float
    
    concentration_units: Union[bytes, str, String]
    
    dilution_factor: float
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void AQS_featureConcentration()
        """
        ...
    
    @overload
    def __init__(self, in_0: AQS_featureConcentration ) -> None:
        """
        Cython signature: void AQS_featureConcentration(AQS_featureConcentration &)
        """
        ... 


class AQS_runConcentration:
    """
    Cython implementation of _AQS_runConcentration

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1AQS_runConcentration.html>`_
    """
    
    sample_name: Union[bytes, str, String]
    
    component_name: Union[bytes, str, String]
    
    IS_component_name: Union[bytes, str, String]
    
    actual_concentration: float
    
    IS_actual_concentration: float
    
    concentration_units: Union[bytes, str, String]
    
    dilution_factor: float
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void AQS_runConcentration()
        """
        ...
    
    @overload
    def __init__(self, in_0: AQS_runConcentration ) -> None:
        """
        Cython signature: void AQS_runConcentration(AQS_runConcentration &)
        """
        ... 


class AbsoluteQuantitationStandards:
    """
    Cython implementation of _AbsoluteQuantitationStandards

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1AbsoluteQuantitationStandards.html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void AbsoluteQuantitationStandards()
        """
        ...
    
    @overload
    def __init__(self, in_0: AbsoluteQuantitationStandards ) -> None:
        """
        Cython signature: void AbsoluteQuantitationStandards(AbsoluteQuantitationStandards &)
        """
        ...
    
    def getComponentFeatureConcentrations(self, run_concentrations: List[AQS_runConcentration] , feature_maps: List[FeatureMap] , component_name: Union[bytes, str, String] , feature_concentrations: List[AQS_featureConcentration] ) -> None:
        """
        Cython signature: void getComponentFeatureConcentrations(libcpp_vector[AQS_runConcentration] & run_concentrations, libcpp_vector[FeatureMap] & feature_maps, const String & component_name, libcpp_vector[AQS_featureConcentration] & feature_concentrations)
        """
        ... 


class CVTerm_ControlledVocabulary:
    """
    Cython implementation of _CVTerm_ControlledVocabulary

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1CVTerm_ControlledVocabulary.html>`_
    """
    
    name: Union[bytes, str, String]
    
    id: Union[bytes, str, String]
    
    parents: Set[bytes]
    
    children: Set[bytes]
    
    obsolete: bool
    
    description: Union[bytes, str, String]
    
    synonyms: List[bytes]
    
    unparsed: List[bytes]
    
    xref_type: int
    
    xref_binary: List[bytes]
    
    units: Set[bytes]
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void CVTerm_ControlledVocabulary()
        """
        ...
    
    @overload
    def __init__(self, rhs: CVTerm_ControlledVocabulary ) -> None:
        """
        Cython signature: void CVTerm_ControlledVocabulary(CVTerm_ControlledVocabulary rhs)
        """
        ...
    
    @overload
    def toXMLString(self, ref: Union[bytes, str, String] , value: Union[bytes, str, String] ) -> Union[bytes, str, String]:
        """
        Cython signature: String toXMLString(String ref, String value)
        Get mzidentml formatted string. i.e. a cvparam xml element, ref should be the name of the ControlledVocabulary (i.e. cv.name()) containing the CVTerm (e.g. PSI-MS for the psi-ms.obo - gets loaded in all cases like that??), value can be empty if not available
        """
        ...
    
    @overload
    def toXMLString(self, ref: Union[bytes, str, String] , value: Union[int, float, bytes, str, List[int], List[float], List[bytes]] ) -> Union[bytes, str, String]:
        """
        Cython signature: String toXMLString(String ref, DataValue value)
        Get mzidentml formatted string. i.e. a cvparam xml element, ref should be the name of the ControlledVocabulary (i.e. cv.name()) containing the CVTerm (e.g. PSI-MS for the psi-ms.obo - gets loaded in all cases like that??), value can be empty if not available
        """
        ...
    
    def getXRefTypeName(self, type: int ) -> Union[bytes, str, String]:
        """
        Cython signature: String getXRefTypeName(XRefType_CVTerm_ControlledVocabulary type)
        """
        ...
    
    def isHigherBetterScore(self, term: CVTerm_ControlledVocabulary ) -> bool:
        """
        Cython signature: bool isHigherBetterScore(CVTerm_ControlledVocabulary term)
        """
        ... 


class ClusterProxyKD:
    """
    Cython implementation of _ClusterProxyKD

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1ClusterProxyKD.html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void ClusterProxyKD()
        """
        ...
    
    @overload
    def __init__(self, in_0: ClusterProxyKD ) -> None:
        """
        Cython signature: void ClusterProxyKD(ClusterProxyKD &)
        """
        ...
    
    @overload
    def __init__(self, size: int , avg_distance: float , center_index: int ) -> None:
        """
        Cython signature: void ClusterProxyKD(size_t size, double avg_distance, size_t center_index)
        """
        ...
    
    def getSize(self) -> int:
        """
        Cython signature: size_t getSize()
        """
        ...
    
    def isValid(self) -> bool:
        """
        Cython signature: bool isValid()
        """
        ...
    
    def getAvgDistance(self) -> float:
        """
        Cython signature: double getAvgDistance()
        """
        ...
    
    def getCenterIndex(self) -> int:
        """
        Cython signature: size_t getCenterIndex()
        """
        ...
    
    def __richcmp__(self, other: ClusterProxyKD, op: int) -> Any:
        ... 


class ConsensusFeature:
    """
    Cython implementation of _ConsensusFeature

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1ConsensusFeature.html>`_
      -- Inherits from ['UniqueIdInterface', 'BaseFeature']

    A consensus feature spanning multiple LC-MS/MS experiments.
    
    A ConsensusFeature represents analytes that have been
    quantified across multiple LC-MS/MS experiments. Each analyte in a
    ConsensusFeature is linked to its original LC-MS/MS run through a
    unique identifier.
    
    Get access to the underlying features through getFeatureList()
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void ConsensusFeature()
        """
        ...
    
    @overload
    def __init__(self, in_0: ConsensusFeature ) -> None:
        """
        Cython signature: void ConsensusFeature(ConsensusFeature &)
        """
        ...
    
    @overload
    def __init__(self, in_0: int , in_1: Peak2D , in_2: int ) -> None:
        """
        Cython signature: void ConsensusFeature(uint64_t, Peak2D, uint64_t)
        """
        ...
    
    @overload
    def __init__(self, in_0: int , in_1: BaseFeature ) -> None:
        """
        Cython signature: void ConsensusFeature(uint64_t, BaseFeature)
        """
        ...
    
    @overload
    def __init__(self, in_0: int , in_1: ConsensusFeature ) -> None:
        """
        Cython signature: void ConsensusFeature(uint64_t, ConsensusFeature)
        """
        ...
    
    def computeConsensus(self) -> None:
        """
        Cython signature: void computeConsensus()
        Computes and updates the consensus position, intensity, and charge
        """
        ...
    
    def computeMonoisotopicConsensus(self) -> None:
        """
        Cython signature: void computeMonoisotopicConsensus()
        Computes and updates the consensus position, intensity, and charge
        """
        ...
    
    def computeDechargeConsensus(self, in_0: FeatureMap , in_1: bool ) -> None:
        """
        Cython signature: void computeDechargeConsensus(FeatureMap, bool)
        Computes the uncharged parent RT & mass, assuming the handles are charge variants
        """
        ...
    
    @overload
    def insert(self, map_idx: int , in_1: Peak2D , element_idx: int ) -> None:
        """
        Cython signature: void insert(uint64_t map_idx, Peak2D, uint64_t element_idx)
        """
        ...
    
    @overload
    def insert(self, map_idx: int , in_1: BaseFeature ) -> None:
        """
        Cython signature: void insert(uint64_t map_idx, BaseFeature)
        """
        ...
    
    @overload
    def insert(self, map_idx: int , in_1: ConsensusFeature ) -> None:
        """
        Cython signature: void insert(uint64_t map_idx, ConsensusFeature)
        """
        ...
    
    def getFeatureList(self) -> List[FeatureHandle]:
        """
        Cython signature: libcpp_vector[FeatureHandle] getFeatureList()
        """
        ...
    
    def size(self) -> int:
        """
        Cython signature: size_t size()
        """
        ...
    
    def addRatio(self, r: Ratio ) -> None:
        """
        Cython signature: void addRatio(Ratio r)
        Connects a ratio to the ConsensusFeature.
        """
        ...
    
    def setRatios(self, rs: List[Ratio] ) -> None:
        """
        Cython signature: void setRatios(libcpp_vector[Ratio] rs)
        Connects the ratios to the ConsensusFeature.
        """
        ...
    
    def getRatios(self) -> List[Ratio]:
        """
        Cython signature: libcpp_vector[Ratio] getRatios()
        Get the ratio vector.
        """
        ...
    
    def clear(self) -> None:
        """
        Cython signature: void clear()
        """
        ...
    
    def empty(self) -> bool:
        """
        Cython signature: bool empty()
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
    
    def setPeptideIdentifications(self, peptides: PeptideIdentificationList ) -> None:
        """
        Cython signature: void setPeptideIdentifications(PeptideIdentificationList & peptides)
        Sets the PeptideIdentification vector
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
    
    def __richcmp__(self, other: ConsensusFeature, op: int) -> Any:
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


class ConsensusIDAlgorithmWorst:
    """
    Cython implementation of _ConsensusIDAlgorithmWorst

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1ConsensusIDAlgorithmWorst.html>`_
      -- Inherits from ['ConsensusIDAlgorithmIdentity']
    """
    
    def __init__(self) -> None:
        """
        Cython signature: void ConsensusIDAlgorithmWorst()
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


class ConsensusMapNormalizerAlgorithmThreshold:
    """
    Cython implementation of _ConsensusMapNormalizerAlgorithmThreshold

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1ConsensusMapNormalizerAlgorithmThreshold.html>`_
    """
    
    def __init__(self) -> None:
        """
        Cython signature: void ConsensusMapNormalizerAlgorithmThreshold()
        """
        ...
    
    def computeCorrelation(self, input_map: ConsensusMap , ratio_threshold: float , acc_filter: Union[bytes, str, String] , desc_filter: Union[bytes, str, String] ) -> List[float]:
        """
        Cython signature: libcpp_vector[double] computeCorrelation(ConsensusMap & input_map, double ratio_threshold, const String & acc_filter, const String & desc_filter)
        Determines the ratio of all maps to the map with the most features
        """
        ...
    
    def normalizeMaps(self, input_map: ConsensusMap , ratios: List[float] ) -> None:
        """
        Cython signature: void normalizeMaps(ConsensusMap & input_map, const libcpp_vector[double] & ratios)
        Applies the given ratio to the maps of the consensusMap
        """
        ... 


class ConsensusXMLFile:
    """
    Cython implementation of _ConsensusXMLFile

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1ConsensusXMLFile.html>`_
    """
    
    def __init__(self) -> None:
        """
        Cython signature: void ConsensusXMLFile()
        """
        ...
    
    def load(self, in_0: Union[bytes, str, String] , in_1: ConsensusMap ) -> None:
        """
        Cython signature: void load(String, ConsensusMap &)
        Loads a consensus map from file and calls updateRanges
        """
        ...
    
    def store(self, in_0: Union[bytes, str, String] , in_1: ConsensusMap ) -> None:
        """
        Cython signature: void store(String, ConsensusMap &)
        Stores a consensus map to file
        """
        ...
    
    def getOptions(self) -> PeakFileOptions:
        """
        Cython signature: PeakFileOptions getOptions()
        Mutable access to the options for loading/storing
        """
        ... 


class ControlledVocabulary:
    """
    Cython implementation of _ControlledVocabulary

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1ControlledVocabulary.html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void ControlledVocabulary()
        """
        ...
    
    @overload
    def __init__(self, in_0: ControlledVocabulary ) -> None:
        """
        Cython signature: void ControlledVocabulary(ControlledVocabulary &)
        """
        ...
    
    def name(self) -> Union[bytes, str, String]:
        """
        Cython signature: String name()
        Returns the CV name (set in the load method)
        """
        ...
    
    def loadFromOBO(self, name: Union[bytes, str, String] , filename: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void loadFromOBO(String name, String filename)
        Loads the CV from an OBO file
        """
        ...
    
    def exists(self, id: Union[bytes, str, String] ) -> bool:
        """
        Cython signature: bool exists(String id)
        Returns true if the term is in the CV. Returns false otherwise.
        """
        ...
    
    def hasTermWithName(self, name: Union[bytes, str, String] ) -> bool:
        """
        Cython signature: bool hasTermWithName(String name)
        Returns true if a term with the given name is in the CV. Returns false otherwise
        """
        ...
    
    def getTerm(self, id: Union[bytes, str, String] ) -> CVTerm_ControlledVocabulary:
        """
        Cython signature: CVTerm_ControlledVocabulary getTerm(String id)
        Returns a term specified by ID
        """
        ...
    
    def getTermByName(self, name: Union[bytes, str, String] , desc: Union[bytes, str, String] ) -> CVTerm_ControlledVocabulary:
        """
        Cython signature: CVTerm_ControlledVocabulary getTermByName(String name, String desc)
        Returns a term specified by name
        """
        ...
    
    def getAllChildTerms(self, terms: Set[bytes] , parent: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void getAllChildTerms(libcpp_set[String] terms, String parent)
        Writes all child terms recursively into terms
        """
        ...
    
    def isChildOf(self, child: Union[bytes, str, String] , parent: Union[bytes, str, String] ) -> bool:
        """
        Cython signature: bool isChildOf(String child, String parent)
        Returns True if `child` is a child of `parent`
        """
        ... 


class DataProcessing:
    """
    Cython implementation of _DataProcessing

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1DataProcessing.html>`_
      -- Inherits from ['MetaInfoInterface']
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void DataProcessing()
        """
        ...
    
    @overload
    def __init__(self, in_0: DataProcessing ) -> None:
        """
        Cython signature: void DataProcessing(DataProcessing &)
        """
        ...
    
    def setProcessingActions(self, in_0: Set[int] ) -> None:
        """
        Cython signature: void setProcessingActions(libcpp_set[ProcessingAction])
        """
        ...
    
    def getProcessingActions(self) -> Set[int]:
        """
        Cython signature: libcpp_set[ProcessingAction] getProcessingActions()
        """
        ...
    
    def getSoftware(self) -> Software:
        """
        Cython signature: Software getSoftware()
        """
        ...
    
    def setSoftware(self, s: Software ) -> None:
        """
        Cython signature: void setSoftware(Software s)
        """
        ...
    
    def getCompletionTime(self) -> DateTime:
        """
        Cython signature: DateTime getCompletionTime()
        """
        ...
    
    def setCompletionTime(self, t: DateTime ) -> None:
        """
        Cython signature: void setCompletionTime(DateTime t)
        """
        ...
    
    @staticmethod
    def getAllNamesOfProcessingAction() -> List[bytes]:
        """
        Cython signature: libcpp_vector[String] getAllNamesOfProcessingAction()
        Returns all processing action names known to OpenMS
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
    
    def __richcmp__(self, other: DataProcessing, op: int) -> Any:
        ...
    ProcessingAction : __ProcessingAction 


class DigestionEnzyme:
    """
    Cython implementation of _DigestionEnzyme

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1DigestionEnzyme.html>`_

      Base class for digestion enzymes
    """
    
    @overload
    def __init__(self, in_0: DigestionEnzyme ) -> None:
        """
        Cython signature: void DigestionEnzyme(DigestionEnzyme &)
        """
        ...
    
    @overload
    def __init__(self, name: Union[bytes, str, String] , cleavage_regex: Union[bytes, str, String] , synonyms: Set[bytes] , regex_description: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void DigestionEnzyme(const String & name, const String & cleavage_regex, libcpp_set[String] & synonyms, String regex_description)
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
    
    def __richcmp__(self, other: DigestionEnzyme, op: int) -> Any:
        ... 


class DocumentIdentifier:
    """
    Cython implementation of _DocumentIdentifier

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1DocumentIdentifier.html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void DocumentIdentifier()
        """
        ...
    
    @overload
    def __init__(self, in_0: DocumentIdentifier ) -> None:
        """
        Cython signature: void DocumentIdentifier(DocumentIdentifier &)
        """
        ...
    
    def setIdentifier(self, id: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setIdentifier(String id)
        Sets document identifier (e.g. an LSID)
        """
        ...
    
    def getIdentifier(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getIdentifier()
        Retrieve document identifier (e.g. an LSID)
        """
        ...
    
    def setLoadedFileType(self, file_name: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setLoadedFileType(String file_name)
        Sets the file_type according to the type of the file loaded from, preferably done whilst loading
        """
        ...
    
    def getLoadedFileType(self) -> int:
        """
        Cython signature: int getLoadedFileType()
        Returns the file_type (e.g. featureXML, consensusXML, mzData, mzXML, mzML, ...) of the file loaded
        """
        ...
    
    def setLoadedFilePath(self, file_name: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setLoadedFilePath(String file_name)
        Sets the file_name according to absolute path of the file loaded, preferably done whilst loading
        """
        ...
    
    def getLoadedFilePath(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getLoadedFilePath()
        Returns the file_name which is the absolute path to the file loaded
        """
        ... 


class FLASHDeconvFeatureFile:
    """
    Cython implementation of _FLASHDeconvFeatureFile

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1FLASHDeconvFeatureFile.html>`_

    FLASHDeconv feature level output *.tsv, *.ms1ft (for Promex), *.feature (for TopPIC) file formats.
    This class provides static methods for writing mass feature data.
    Note: Methods taking std::ostream are not directly exposed. Use file-based workflows.
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void FLASHDeconvFeatureFile()
        """
        ...
    
    @overload
    def __init__(self, in_0: FLASHDeconvFeatureFile ) -> None:
        """
        Cython signature: void FLASHDeconvFeatureFile(FLASHDeconvFeatureFile &)
        """
        ... 


class FalseDiscoveryRate:
    """
    Cython implementation of _FalseDiscoveryRate

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1FalseDiscoveryRate.html>`_
      -- Inherits from ['DefaultParamHandler']
    """
    
    def __init__(self) -> None:
        """
        Cython signature: void FalseDiscoveryRate()
        """
        ...
    
    @overload
    def apply(self, forward_ids: PeptideIdentificationList , reverse_ids: PeptideIdentificationList ) -> None:
        """
        Cython signature: void apply(PeptideIdentificationList & forward_ids, PeptideIdentificationList & reverse_ids)
        """
        ...
    
    @overload
    def apply(self, id: PeptideIdentificationList ) -> None:
        """
        Cython signature: void apply(PeptideIdentificationList & id)
        """
        ...
    
    @overload
    def apply(self, forward_ids: List[ProteinIdentification] , reverse_ids: List[ProteinIdentification] ) -> None:
        """
        Cython signature: void apply(libcpp_vector[ProteinIdentification] & forward_ids, libcpp_vector[ProteinIdentification] & reverse_ids)
        """
        ...
    
    @overload
    def apply(self, id: List[ProteinIdentification] ) -> None:
        """
        Cython signature: void apply(libcpp_vector[ProteinIdentification] & id)
        """
        ...
    
    def applyEstimated(self, ids: List[ProteinIdentification] ) -> None:
        """
        Cython signature: void applyEstimated(libcpp_vector[ProteinIdentification] & ids)
        """
        ...
    
    @overload
    def applyEvaluateProteinIDs(self, ids: List[ProteinIdentification] , pepCutoff: float , fpCutoff: int , diffWeight: float ) -> float:
        """
        Cython signature: double applyEvaluateProteinIDs(libcpp_vector[ProteinIdentification] & ids, double pepCutoff, unsigned int fpCutoff, double diffWeight)
        """
        ...
    
    @overload
    def applyEvaluateProteinIDs(self, ids: ProteinIdentification , pepCutoff: float , fpCutoff: int , diffWeight: float ) -> float:
        """
        Cython signature: double applyEvaluateProteinIDs(ProteinIdentification & ids, double pepCutoff, unsigned int fpCutoff, double diffWeight)
        """
        ...
    
    @overload
    def applyBasic(self, run_info: List[ProteinIdentification] , ids: PeptideIdentificationList ) -> None:
        """
        Cython signature: void applyBasic(libcpp_vector[ProteinIdentification] & run_info, PeptideIdentificationList & ids)
        """
        ...
    
    @overload
    def applyBasic(self, ids: PeptideIdentificationList , higher_score_better: bool , charge: int , identifier: Union[bytes, str, String] , only_best_per_pep: bool ) -> None:
        """
        Cython signature: void applyBasic(PeptideIdentificationList & ids, bool higher_score_better, int charge, String identifier, bool only_best_per_pep)
        """
        ...
    
    @overload
    def applyBasic(self, cmap: ConsensusMap , use_unassigned_peptides: bool ) -> None:
        """
        Cython signature: void applyBasic(ConsensusMap & cmap, bool use_unassigned_peptides)
        """
        ...
    
    @overload
    def applyBasic(self, id: ProteinIdentification , groups_too: bool ) -> None:
        """
        Cython signature: void applyBasic(ProteinIdentification & id, bool groups_too)
        """
        ...
    
    def applyPickedProteinFDR(self, id: ProteinIdentification , decoy_string: String , decoy_prefix: bool , groups_too: bool ) -> None:
        """
        Cython signature: void applyPickedProteinFDR(ProteinIdentification & id, String & decoy_string, bool decoy_prefix, bool groups_too)
        """
        ...
    
    @overload
    def rocN(self, ids: PeptideIdentificationList , fp_cutoff: int ) -> float:
        """
        Cython signature: double rocN(PeptideIdentificationList & ids, size_t fp_cutoff)
        """
        ...
    
    @overload
    def rocN(self, ids: ConsensusMap , fp_cutoff: int , include_unassigned_peptides: bool ) -> float:
        """
        Cython signature: double rocN(ConsensusMap & ids, size_t fp_cutoff, bool include_unassigned_peptides)
        """
        ...
    
    @overload
    def rocN(self, ids: ConsensusMap , fp_cutoff: int , identifier: Union[bytes, str, String] , include_unassigned_peptides: bool ) -> float:
        """
        Cython signature: double rocN(ConsensusMap & ids, size_t fp_cutoff, const String & identifier, bool include_unassigned_peptides)
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


class FeatureFinderAlgorithmPicked:
    """
    Cython implementation of _FeatureFinderAlgorithmPicked

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1FeatureFinderAlgorithmPicked.html>`_
      -- Inherits from ['DefaultParamHandler']
    """
    
    def __init__(self) -> None:
        """
        Cython signature: void FeatureFinderAlgorithmPicked()
        """
        ...
    
    def run(self, input_map: MSExperiment , output: FeatureMap , param: Param , seeds: FeatureMap ) -> None:
        """
        Cython signature: void run(MSExperiment & input_map, FeatureMap & output, Param & param, FeatureMap & seeds)
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


class FeatureGroupingAlgorithmQT:
    """
    Cython implementation of _FeatureGroupingAlgorithmQT

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1FeatureGroupingAlgorithmQT.html>`_
      -- Inherits from ['FeatureGroupingAlgorithm']
    """
    
    def __init__(self) -> None:
        """
        Cython signature: void FeatureGroupingAlgorithmQT()
        """
        ...
    
    @overload
    def group(self, maps: List[FeatureMap] , out: ConsensusMap ) -> None:
        """
        Cython signature: void group(const libcpp_vector[FeatureMap] & maps, ConsensusMap & out)
        """
        ...
    
    @overload
    def group(self, maps: List[ConsensusMap] , out: ConsensusMap ) -> None:
        """
        Cython signature: void group(const libcpp_vector[ConsensusMap] & maps, ConsensusMap & out)
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


class FeatureXMLFile:
    """
    Cython implementation of _FeatureXMLFile

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1FeatureXMLFile.html>`_
    """
    
    def __init__(self) -> None:
        """
        Cython signature: void FeatureXMLFile()
        This class provides Input/Output functionality for feature maps
        """
        ...
    
    def load(self, in_0: Union[bytes, str, String] , in_1: FeatureMap ) -> None:
        """
        Cython signature: void load(String, FeatureMap &)
        Loads the file with name `filename` into `map` and calls updateRanges()
        """
        ...
    
    def store(self, in_0: Union[bytes, str, String] , in_1: FeatureMap ) -> None:
        """
        Cython signature: void store(String, FeatureMap &)
        Stores the map `feature_map` in file with name `filename`
        """
        ...
    
    def getOptions(self) -> FeatureFileOptions:
        """
        Cython signature: FeatureFileOptions getOptions()
        Access to the options for loading/storing
        """
        ...
    
    def setOptions(self, in_0: FeatureFileOptions ) -> None:
        """
        Cython signature: void setOptions(FeatureFileOptions)
        Setter for options for loading/storing
        """
        ...
    
    def loadSize(self, path: Union[bytes, str, String] ) -> int:
        """
        Cython signature: size_t loadSize(String path)
        """
        ... 


class IMTypes:
    """
    Cython implementation of _IMTypes

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1IMTypes.html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void IMTypes()
        """
        ...
    
    @overload
    def __init__(self, in_0: IMTypes ) -> None:
        """
        Cython signature: void IMTypes(IMTypes &)
        """
        ...
    
    @overload
    def determineIMFormat(self, exp: MSExperiment ) -> int:
        """
        Cython signature: IMFormat determineIMFormat(const MSExperiment & exp)
        """
        ...
    
    @overload
    def determineIMFormat(self, spec: MSSpectrum ) -> int:
        """
        Cython signature: IMFormat determineIMFormat(const MSSpectrum & spec)
        """
        ...
    
    toDriftTimeUnit: __static_IMTypes_toDriftTimeUnit
    
    toIMFormat: __static_IMTypes_toIMFormat
    
    toString: __static_IMTypes_toString
    
    toString: __static_IMTypes_toString 


class IncludeExcludeTarget:
    """
    Cython implementation of _IncludeExcludeTarget

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1IncludeExcludeTarget.html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void IncludeExcludeTarget()
        This class stores a SRM/MRM transition
        """
        ...
    
    @overload
    def __init__(self, in_0: IncludeExcludeTarget ) -> None:
        """
        Cython signature: void IncludeExcludeTarget(IncludeExcludeTarget &)
        """
        ...
    
    def setName(self, name: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setName(const String & name)
        """
        ...
    
    def getName(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getName()
        """
        ...
    
    def setPeptideRef(self, peptide_ref: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setPeptideRef(const String & peptide_ref)
        """
        ...
    
    def getPeptideRef(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getPeptideRef()
        """
        ...
    
    def setCompoundRef(self, compound_ref: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setCompoundRef(const String & compound_ref)
        """
        ...
    
    def getCompoundRef(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getCompoundRef()
        """
        ...
    
    def setPrecursorMZ(self, mz: float ) -> None:
        """
        Cython signature: void setPrecursorMZ(double mz)
        """
        ...
    
    def getPrecursorMZ(self) -> float:
        """
        Cython signature: double getPrecursorMZ()
        """
        ...
    
    def setPrecursorCVTermList(self, list_: CVTermList ) -> None:
        """
        Cython signature: void setPrecursorCVTermList(CVTermList & list_)
        """
        ...
    
    def addPrecursorCVTerm(self, cv_term: CVTerm ) -> None:
        """
        Cython signature: void addPrecursorCVTerm(CVTerm & cv_term)
        """
        ...
    
    def getPrecursorCVTermList(self) -> CVTermList:
        """
        Cython signature: CVTermList getPrecursorCVTermList()
        """
        ...
    
    def setProductMZ(self, mz: float ) -> None:
        """
        Cython signature: void setProductMZ(double mz)
        """
        ...
    
    def getProductMZ(self) -> float:
        """
        Cython signature: double getProductMZ()
        """
        ...
    
    def setProductCVTermList(self, list_: CVTermList ) -> None:
        """
        Cython signature: void setProductCVTermList(CVTermList & list_)
        """
        ...
    
    def addProductCVTerm(self, cv_term: CVTerm ) -> None:
        """
        Cython signature: void addProductCVTerm(CVTerm & cv_term)
        """
        ...
    
    def getProductCVTermList(self) -> CVTermList:
        """
        Cython signature: CVTermList getProductCVTermList()
        """
        ...
    
    def setInterpretations(self, interpretations: List[CVTermList] ) -> None:
        """
        Cython signature: void setInterpretations(libcpp_vector[CVTermList] & interpretations)
        """
        ...
    
    def getInterpretations(self) -> List[CVTermList]:
        """
        Cython signature: libcpp_vector[CVTermList] getInterpretations()
        """
        ...
    
    def addInterpretation(self, interpretation: CVTermList ) -> None:
        """
        Cython signature: void addInterpretation(CVTermList & interpretation)
        """
        ...
    
    def setConfigurations(self, configuration: List[Configuration] ) -> None:
        """
        Cython signature: void setConfigurations(libcpp_vector[Configuration] & configuration)
        """
        ...
    
    def getConfigurations(self) -> List[Configuration]:
        """
        Cython signature: libcpp_vector[Configuration] getConfigurations()
        """
        ...
    
    def addConfiguration(self, configuration: Configuration ) -> None:
        """
        Cython signature: void addConfiguration(Configuration & configuration)
        """
        ...
    
    def setPrediction(self, prediction: CVTermList ) -> None:
        """
        Cython signature: void setPrediction(CVTermList & prediction)
        """
        ...
    
    def addPredictionTerm(self, prediction: CVTerm ) -> None:
        """
        Cython signature: void addPredictionTerm(CVTerm & prediction)
        """
        ...
    
    def getPrediction(self) -> CVTermList:
        """
        Cython signature: CVTermList getPrediction()
        """
        ...
    
    def setRetentionTime(self, rt: RetentionTime ) -> None:
        """
        Cython signature: void setRetentionTime(RetentionTime rt)
        """
        ...
    
    def getRetentionTime(self) -> RetentionTime:
        """
        Cython signature: RetentionTime getRetentionTime()
        """
        ...
    
    def setCVTerms(self, terms: List[CVTerm] ) -> None:
        """
        Cython signature: void setCVTerms(libcpp_vector[CVTerm] & terms)
        """
        ...
    
    def replaceCVTerm(self, term: CVTerm ) -> None:
        """
        Cython signature: void replaceCVTerm(CVTerm & term)
        """
        ...
    
    @overload
    def replaceCVTerms(self, cv_terms: List[CVTerm] , accession: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void replaceCVTerms(libcpp_vector[CVTerm] cv_terms, String accession)
        """
        ...
    
    @overload
    def replaceCVTerms(self, cv_term_map: Dict[bytes,List[CVTerm]] ) -> None:
        """
        Cython signature: void replaceCVTerms(libcpp_map[String,libcpp_vector[CVTerm]] cv_term_map)
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
        """
        ...
    
    def hasCVTerm(self, accession: Union[bytes, str, String] ) -> bool:
        """
        Cython signature: bool hasCVTerm(String accession)
        """
        ...
    
    def empty(self) -> bool:
        """
        Cython signature: bool empty()
        """
        ...
    
    def __richcmp__(self, other: IncludeExcludeTarget, op: int) -> Any:
        ... 


class IndexedMzMLDecoder:
    """
    Cython implementation of _IndexedMzMLDecoder

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1IndexedMzMLDecoder.html>`_

    A class to analyze indexedmzML files and extract the offsets of individual tags
    
    Specifically, this class allows one to extract the offsets of the <indexList>
    tag and of all <spectrum> and <chromatogram> tag using the indices found at
    the end of the indexedmzML XML structure
    
    While findIndexListOffset tries extracts the offset of the indexList tag from
    the last 1024 bytes of the file, this offset allows the function parseOffsets
    to extract all elements contained in the <indexList> tag and thus get access
    to all spectra and chromatogram offsets
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void IndexedMzMLDecoder()
        """
        ...
    
    @overload
    def __init__(self, in_0: IndexedMzMLDecoder ) -> None:
        """
        Cython signature: void IndexedMzMLDecoder(IndexedMzMLDecoder &)
        """
        ...
    
    def findIndexListOffset(self, in_: Union[bytes, str, String] , buffersize: int ) -> streampos:
        """
        Cython signature: streampos findIndexListOffset(String in_, int buffersize)
        Tries to extract the indexList offset from an indexedmzML\n
        
        This function reads by default the last few (1024) bytes of the given
        input file and tries to read the content of the <indexListOffset> tag
        The idea is that somewhere in the last parts of the file specified by the
        input string, the string <indexListOffset>xxx</indexListOffset> occurs
        This function returns the xxx part converted to an integer\n
        
        Since this function cannot determine where it will start reading
        the XML, no regular XML parser can be used for this. Therefore it uses
        regex to do its job. It matches the <indexListOffset> part and any
        numerical characters that follow
        
        
        :param in: Filename of the input indexedmzML file
        :param buffersize: How many bytes of the input file should be searched for the tag
        :return: A positive integer containing the content of the indexListOffset tag, returns -1 in case of failure no tag was found (you can re-try with a larger buffersize but most likely its not an indexed mzML). Using -1 is what the reference docu recommends: http://en.cppreference.com/w/cpp/io/streamoff
        :raises:
          Exception: FileNotFound is thrown if file cannot be found
        :raises:
          Exception: ParseError if offset cannot be parsed
        """
        ... 


class IndexedMzMLHandler:
    """
    Cython implementation of _IndexedMzMLHandler

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1IndexedMzMLHandler.html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void IndexedMzMLHandler()
        """
        ...
    
    @overload
    def __init__(self, in_0: IndexedMzMLHandler ) -> None:
        """
        Cython signature: void IndexedMzMLHandler(IndexedMzMLHandler &)
        """
        ...
    
    @overload
    def __init__(self, filename: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void IndexedMzMLHandler(String filename)
        """
        ...
    
    def openFile(self, filename: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void openFile(String filename)
        """
        ...
    
    def getParsingSuccess(self) -> bool:
        """
        Cython signature: bool getParsingSuccess()
        """
        ...
    
    def getNrSpectra(self) -> int:
        """
        Cython signature: size_t getNrSpectra()
        """
        ...
    
    def getNrChromatograms(self) -> int:
        """
        Cython signature: size_t getNrChromatograms()
        """
        ...
    
    def getSpectrumById(self, id_: int ) -> _Interfaces_Spectrum:
        """
        Cython signature: shared_ptr[_Interfaces_Spectrum] getSpectrumById(int id_)
        """
        ...
    
    def getChromatogramById(self, id_: int ) -> _Interfaces_Chromatogram:
        """
        Cython signature: shared_ptr[_Interfaces_Chromatogram] getChromatogramById(int id_)
        """
        ...
    
    def getMSSpectrumById(self, id_: int ) -> MSSpectrum:
        """
        Cython signature: MSSpectrum getMSSpectrumById(int id_)
        """
        ...
    
    def getMSSpectrumByNativeId(self, id_: bytes , spec: MSSpectrum ) -> None:
        """
        Cython signature: void getMSSpectrumByNativeId(libcpp_string id_, MSSpectrum & spec)
        """
        ...
    
    def getMSChromatogramById(self, id_: int ) -> MSChromatogram:
        """
        Cython signature: MSChromatogram getMSChromatogramById(int id_)
        """
        ...
    
    def getMSChromatogramByNativeId(self, id_: bytes , chrom: MSChromatogram ) -> None:
        """
        Cython signature: void getMSChromatogramByNativeId(libcpp_string id_, MSChromatogram & chrom)
        """
        ...
    
    def setSkipXMLChecks(self, skip: bool ) -> None:
        """
        Cython signature: void setSkipXMLChecks(bool skip)
        """
        ... 


class InternalCalibration:
    """
    Cython implementation of _InternalCalibration

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1InternalCalibration.html>`_
      -- Inherits from ['ProgressLogger']
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void InternalCalibration()
        A mass recalibration method using linear/quadratic interpolation (robust/weighted) of given reference masses
        """
        ...
    
    @overload
    def __init__(self, in_0: InternalCalibration ) -> None:
        """
        Cython signature: void InternalCalibration(InternalCalibration &)
        """
        ...
    
    @overload
    def fillCalibrants(self, in_0: MSExperiment , in_1: List[InternalCalibration_LockMass] , tol_ppm: float , lock_require_mono: bool , lock_require_iso: bool , failed_lock_masses: CalibrationData , verbose: bool ) -> int:
        """
        Cython signature: size_t fillCalibrants(MSExperiment, libcpp_vector[InternalCalibration_LockMass], double tol_ppm, bool lock_require_mono, bool lock_require_iso, CalibrationData & failed_lock_masses, bool verbose)
        Extract calibrants from Raw data (mzML)\n
        
        Lock masses are searched in each spectrum and added to the internal calibrant database\n
        
        Filters can be used to exclude spurious peaks, i.e. require the calibrant peak to be monoisotopic or
        to have a +1 isotope (should not be used for very low abundant calibrants)
        If a calibrant is not found, it is added to a 'failed_lock_masses' database which is returned and not stored internally.
        The intensity of the peaks describe the reason for failed detection: 0.0 - peak not found with the given ppm tolerance;
        1.0 - peak is not monoisotopic (can only occur if 'lock_require_mono' is true)
        2.0 - peak has no +1 isotope (can only occur if 'lock_require_iso' is true)
        
        
        :param exp: Peak map containing the lock masses
        :param ref_masses: List of lock masses
        :param tol_ppm: Search window for lock masses in 'exp'
        :param lock_require_mono: Require that a lock mass is the monoisotopic peak (i.e. not an isotope peak) -- lock mass is rejected otherwise
        :param lock_require_iso: Require that a lock mass has isotope peaks to its right -- lock mass is rejected otherwise
        :param failed_lock_masses: Set of calibration masses which were not found, i.e. their expected m/z and RT positions
        :param verbose: Print information on 'lock_require_XXX' matches during search
        :return: Number of calibration masses found
        """
        ...
    
    @overload
    def fillCalibrants(self, in_0: FeatureMap , in_1: float ) -> int:
        """
        Cython signature: size_t fillCalibrants(FeatureMap, double)
        Extract calibrants from identifications\n
        
        Extracts only the first hit from the first peptide identification of each feature
        Hits are sorted beforehand
        Ambiguities should be resolved before, e.g. using IDFilter
        RT and m/z are taken from the features, not from the identifications (for an exception see below)!\n
        
        Unassigned peptide identifications are also taken into account!
        RT and m/z are naturally taken from the IDs, since to feature is assigned
        If you do not want these IDs, remove them from the feature map before calling this function\n
        
        A filtering step is done in the m/z dimension using 'tol_ppm'
        Since precursor masses could be annotated wrongly (e.g. isotope peak instead of mono),
        larger outliers are removed before accepting an ID as calibrant
        
        
        :param fm: FeatureMap with peptide identifications
        :param tol_ppm: Only accept ID's whose theoretical mass deviates at most this much from annotated
        :return: Number of calibration masses found
        """
        ...
    
    @overload
    def fillCalibrants(self, in_0: PeptideIdentificationList , in_1: float ) -> int:
        """
        Cython signature: size_t fillCalibrants(PeptideIdentificationList, double)
        Extract calibrants from identifications\n
        
        Extracts only the first hit from each peptide identification
        Hits are sorted beforehand
        Ambiguities should be resolved before, e.g. using IDFilter\n
        
        Unassigned peptide identifications are also taken into account!
        RT and m/z are naturally taken from the IDs, since to feature is assigned
        If you do not want these IDs, remove them from the feature map before calling this function\n
        
        A filtering step is done in the m/z dimension using 'tol_ppm'
        Since precursor masses could be annotated wrongly (e.g. isotope peak instead of mono),
        larger outliers are removed before accepting an ID as calibrant
        
        
        :param pep_ids: Peptide ids (e.g. from an idXML file)
        :param tol_ppm: Only accept ID's whose theoretical mass deviates at most this much from annotated
        :return: Number of calibration masses found
        """
        ...
    
    def getCalibrationPoints(self) -> CalibrationData:
        """
        Cython signature: CalibrationData getCalibrationPoints()
        Get container of calibration points\n
        
        Filled using fillCalibrants() methods
        
        
        :return: Container of calibration points
        """
        ...
    
    def calibrate(self, in_0: MSExperiment , in_1: List[int] , in_2: int , rt_chunk: float , use_RANSAC: bool , post_ppm_median: float , post_ppm_MAD: float , file_models: Union[bytes, str, String] , file_models_plot: Union[bytes, str, String] , file_residuals: Union[bytes, str, String] , file_residuals_plot: Union[bytes, str, String] , rscript_executable: Union[bytes, str, String] ) -> bool:
        """
        Cython signature: bool calibrate(MSExperiment, libcpp_vector[int], MZTrafoModel_MODELTYPE, double rt_chunk, bool use_RANSAC, double post_ppm_median, double post_ppm_MAD, String file_models, String file_models_plot, String file_residuals, String file_residuals_plot, String rscript_executable)
        Apply calibration to data\n
        
        For each spectrum, a calibration model will be computed and applied.
        Make sure to call fillCalibrants() before, so a model can be created.\n
        
        The MSExperiment will be sorted by RT and m/z if unsorted.
        
        
        :param exp: MSExperiment holding the Raw data to calibrate
        :param target_mslvl: MS-levels where calibration should be applied to
        :param model_type: Linear or quadratic model; select based on your instrument
        :param rt_chunk: RT-window size (one-sided) of calibration points to collect around each spectrum. Set to negative values, to build one global model instead.
        :param use_RANSAC: Remove outliers before fitting a model?!
        :param post_ppm_median: The median ppm error of the calibrants must be at least this good after calibration; otherwise this method returns false(fail)
        :param post_ppm_MAD: The median absolute deviation of the calibrants must be at least this good after calibration; otherwise this method returns false(fail)
        :param file_models: Output CSV filename, where model parameters are written to (pass empty string to skip)
        :param file_models_plot: Output PNG image model parameters (pass empty string to skip)
        :param file_residuals: Output CSV filename, where ppm errors of calibrants before and after model fitting parameters are written to (pass empty string to skip)
        :param file_residuals_plot: Output PNG image of the ppm errors of calibrants (pass empty string to skip)
        :param rscript_executable: Full path to the Rscript executable
        :return: true upon successful calibration
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
    
    applyTransformation: __static_InternalCalibration_applyTransformation
    
    applyTransformation: __static_InternalCalibration_applyTransformation
    
    applyTransformation: __static_InternalCalibration_applyTransformation 


class InternalCalibration_LockMass:
    """
    Cython implementation of _InternalCalibration_LockMass

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1InternalCalibration_LockMass.html>`_
    """
    
    mz: float
    
    ms_level: int
    
    charge: int
    
    @overload
    def __init__(self, mz_: float , lvl_: int , charge_: int ) -> None:
        """
        Cython signature: void InternalCalibration_LockMass(double mz_, int lvl_, int charge_)
        """
        ...
    
    @overload
    def __init__(self, in_0: InternalCalibration_LockMass ) -> None:
        """
        Cython signature: void InternalCalibration_LockMass(InternalCalibration_LockMass &)
        """
        ... 


class Internal_MzMLValidator:
    """
    Cython implementation of _Internal_MzMLValidator

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS::Internal_1_1Internal_MzMLValidator.html>`_
    """
    
    def __init__(self, mapping: CVMappings , cv: ControlledVocabulary ) -> None:
        """
        Cython signature: void Internal_MzMLValidator(CVMappings & mapping, ControlledVocabulary & cv)
        """
        ... 


class IonDetector:
    """
    Cython implementation of _IonDetector

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1IonDetector.html>`_
      -- Inherits from ['MetaInfoInterface']
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void IonDetector()
        Description of a ion detector (part of a MS Instrument)
        """
        ...
    
    @overload
    def __init__(self, in_0: IonDetector ) -> None:
        """
        Cython signature: void IonDetector(IonDetector &)
        """
        ...
    
    def getType(self) -> int:
        """
        Cython signature: Type_IonDetector getType()
        Returns the detector type
        """
        ...
    
    def setType(self, type_: int ) -> None:
        """
        Cython signature: void setType(Type_IonDetector type_)
        Sets the detector type
        """
        ...
    
    def getAcquisitionMode(self) -> int:
        """
        Cython signature: AcquisitionMode getAcquisitionMode()
        Returns the acquisition mode
        """
        ...
    
    def setAcquisitionMode(self, acquisition_mode: int ) -> None:
        """
        Cython signature: void setAcquisitionMode(AcquisitionMode acquisition_mode)
        Sets the acquisition mode
        """
        ...
    
    def getResolution(self) -> float:
        """
        Cython signature: double getResolution()
        Returns the resolution (in ns)
        """
        ...
    
    def setResolution(self, resolution: float ) -> None:
        """
        Cython signature: void setResolution(double resolution)
        Sets the resolution (in ns)
        """
        ...
    
    def getADCSamplingFrequency(self) -> float:
        """
        Cython signature: double getADCSamplingFrequency()
        Returns the analog-to-digital converter sampling frequency (in Hz)
        """
        ...
    
    def setADCSamplingFrequency(self, ADC_sampling_frequency: float ) -> None:
        """
        Cython signature: void setADCSamplingFrequency(double ADC_sampling_frequency)
        Sets the analog-to-digital converter sampling frequency (in Hz)
        """
        ...
    
    def getOrder(self) -> int:
        """
        Cython signature: int getOrder()
        Returns the order
        """
        ...
    
    def setOrder(self, order: int ) -> None:
        """
        Cython signature: void setOrder(int order)
        Sets the order
        """
        ...
    
    @staticmethod
    def getAllNamesOfType() -> List[bytes]:
        """
        Cython signature: libcpp_vector[String] getAllNamesOfType()
        Returns all detector type names known to OpenMS
        """
        ...
    
    @staticmethod
    def getAllNamesOfAcquisitionMode() -> List[bytes]:
        """
        Cython signature: libcpp_vector[String] getAllNamesOfAcquisitionMode()
        Returns all acquisition mode names known to OpenMS
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
    
    def __richcmp__(self, other: IonDetector, op: int) -> Any:
        ...
    AcquisitionMode : __AcquisitionMode
    Type_IonDetector : __Type_IonDetector 


class IsotopeModel:
    """
    Cython implementation of _IsotopeModel

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1IsotopeModel.html>`_

    Isotope distribution approximated using linear interpolation
    
    This models a smoothed (widened) distribution, i.e. can be used to sample actual raw peaks (depending on the points you query)
    If you only want the distribution (no widening), use either
    EmpiricalFormula::getIsotopeDistribution() // for a certain sum formula
    or
    IsotopeDistribution::estimateFromPeptideWeight (double average_weight)  // for averagine
    
    Peak widening is achieved by either a Gaussian or Lorentzian shape
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void IsotopeModel()
        """
        ...
    
    @overload
    def __init__(self, in_0: IsotopeModel ) -> None:
        """
        Cython signature: void IsotopeModel(IsotopeModel &)
        """
        ...
    
    def getCharge(self) -> int:
        """
        Cython signature: unsigned int getCharge()
        """
        ...
    
    def setOffset(self, offset: float ) -> None:
        """
        Cython signature: void setOffset(double offset)
        Set the offset of the model
        
        The whole model will be shifted to the new offset without being computing all over
        This leaves a discrepancy which is minor in small shifts (i.e. shifting by one or two
        standard deviations) but can get significant otherwise. In that case use setParameters()
        which enforces a recomputation of the model
        """
        ...
    
    def getOffset(self) -> float:
        """
        Cython signature: double getOffset()
        Get the offset of the model
        """
        ...
    
    def getFormula(self) -> EmpiricalFormula:
        """
        Cython signature: EmpiricalFormula getFormula()
        Return the Averagine peptide formula (mass calculated from mean mass and charge -- use .setParameters() to set them)
        """
        ...
    
    def setSamples(self, formula: EmpiricalFormula ) -> None:
        """
        Cython signature: void setSamples(EmpiricalFormula & formula)
        Set sample/supporting points of interpolation
        """
        ...
    
    def getCenter(self) -> float:
        """
        Cython signature: double getCenter()
        Get the center of the Isotope model
        
        This is a m/z-value not necessarily the monoisotopic mass
        """
        ...
    
    def getIsotopeDistribution(self) -> IsotopeDistribution:
        """
        Cython signature: IsotopeDistribution getIsotopeDistribution()
        Get the Isotope distribution (without widening) from the last setSamples() call
        
        Useful to determine the number of isotopes that the model contains and their position
        """
        ...
    Averagines : __Averagines 


class KDTreeFeatureNode:
    """
    Cython implementation of _KDTreeFeatureNode

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1KDTreeFeatureNode.html>`_

    A node of the kD-tree with pointer to corresponding data and index
    """
    
    @overload
    def __init__(self, in_0: KDTreeFeatureNode ) -> None:
        """
        Cython signature: void KDTreeFeatureNode(KDTreeFeatureNode &)
        """
        ...
    
    @overload
    def __init__(self, data: KDTreeFeatureMaps , idx: int ) -> None:
        """
        Cython signature: void KDTreeFeatureNode(KDTreeFeatureMaps * data, size_t idx)
        """
        ...
    
    def __getitem__(self, i: int ) -> float:
        """
        Cython signature: double operator[](size_t i)
        """
        ...
    
    def getIndex(self) -> int:
        """
        Cython signature: size_t getIndex()
        Returns index of corresponding feature in data_
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


class LogConfigHandler:
    """
    Cython implementation of _LogConfigHandler

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1LogConfigHandler.html>`_
    """
    
    def parse(self, setting: List[bytes] ) -> Param:
        """
        Cython signature: Param parse(const StringList & setting)
        Translates the given list of parameter settings into a LogStream configuration
        
        Translates the given list of parameter settings into a LogStream configuration.
        Usually this list stems from a command line call.
        
        Each element in the stringlist should follow this naming convention
        
        <LOG_NAME> <ACTION> <PARAMETER>
        
        with
        - LOG_NAME: DEBUG,INFO,WARNING,ERROR,FATAL_ERROR
        - ACTION: add,remove,clear
        - PARAMETER: for 'add'/'remove' it is the stream name (cout, cerr or a filename), 'clear' does not require any further parameter
        
        Example:
        `DEBUG add debug.log`
        
        This function will **not** apply to settings to the log handlers. Use configure() for that.
        
        :param setting: StringList containing the configuration options
        :raises ParseError: In case of an invalid configuration.
        :return: Param object containing all settings, that can be applied using the LogConfigHandler.configure() method
        """
        ...
    
    def configure(self, param: Param ) -> None:
        """
        Cython signature: void configure(const Param & param)
        Applies the given parameters (@p param) to the current configuration
        
        <LOG_NAME> <ACTION> <PARAMETER> <STREAMTYPE>
        
        LOG_NAME: DEBUG, INFO, WARNING, ERROR, FATAL_ERROR
        ACTION: add, remove, clear
        PARAMETER: for 'add'/'remove' it is the stream name ('cout', 'cerr' or a filename), 'clear' does not require any further parameter
        STREAMTYPE: FILE, STRING (for a StringStream, which you can grab by this name using getStream() )
        
        You cannot specify a file named "cout" or "cerr" even if you specify streamtype 'FILE' - the handler will mistake this for the
        internal streams, but you can use "./cout" to print to a file named cout.
        
        A classical configuration would contain a list of settings e.g.
        
        `DEBUG add debug.log FILE`
        `INFO remove cout FILE` (FILE will be ignored)
        `INFO add string_stream1 STRING`
        
        :raises ElementNotFound: If the LogStream (first argument) does not exist.
        :raises FileNotWritable: If a file (or stream) should be opened as log file (or stream) that is not accessible.
        :raises IllegalArgument: If a stream should be registered, that was already registered with a different type.
        """
        ...
    
    def setLogLevel(self, log_level: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setLogLevel(const String & log_level)
        Sets a minimum log_level by removing all streams from loggers lower than that level.
        Valid levels are from low to high: "DEBUG", "INFO", "WARNING", "ERROR", "FATAL_ERROR"
        """
        ... 


class MRMFP_ComponentGroupParams:
    """
    Cython implementation of _MRMFP_ComponentGroupParams

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1MRMFP_ComponentGroupParams.html>`_
    """
    
    component_group_name: Union[bytes, str, String]
    
    params: Param
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void MRMFP_ComponentGroupParams()
        """
        ...
    
    @overload
    def __init__(self, in_0: MRMFP_ComponentGroupParams ) -> None:
        """
        Cython signature: void MRMFP_ComponentGroupParams(MRMFP_ComponentGroupParams &)
        """
        ... 


class MRMFP_ComponentParams:
    """
    Cython implementation of _MRMFP_ComponentParams

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1MRMFP_ComponentParams.html>`_
    """
    
    component_name: Union[bytes, str, String]
    
    component_group_name: Union[bytes, str, String]
    
    params: Param
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void MRMFP_ComponentParams()
        """
        ...
    
    @overload
    def __init__(self, in_0: MRMFP_ComponentParams ) -> None:
        """
        Cython signature: void MRMFP_ComponentParams(MRMFP_ComponentParams &)
        """
        ... 


class MRMFeaturePicker:
    """
    Cython implementation of _MRMFeaturePicker

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1MRMFeaturePicker.html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void MRMFeaturePicker()
        """
        ...
    
    @overload
    def __init__(self, in_0: MRMFeaturePicker ) -> None:
        """
        Cython signature: void MRMFeaturePicker(MRMFeaturePicker &)
        """
        ... 


class MRMScoring:
    """
    Cython implementation of _MRMScoring

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenSwath_1_1MRMScoring.html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void MRMScoring()
        """
        ...
    
    @overload
    def __init__(self, in_0: MRMScoring ) -> None:
        """
        Cython signature: void MRMScoring(MRMScoring &)
        """
        ...
    
    def calcXcorrCoelutionScore(self) -> float:
        """
        Cython signature: double calcXcorrCoelutionScore()
        Calculate the cross-correlation coelution score. The score is a distance where zero indicates perfect coelution
        """
        ...
    
    def calcXcorrCoelutionWeightedScore(self, normalized_library_intensity: List[float] ) -> float:
        """
        Cython signature: double calcXcorrCoelutionWeightedScore(const libcpp_vector[double] & normalized_library_intensity)
        Calculate the weighted cross-correlation coelution score
        
        The score is a distance where zero indicates perfect coelution. The
        score is weighted by the transition intensities, non-perfect coelution
        in low-intensity transitions should thus become less important
        """
        ...
    
    def calcSeparateXcorrContrastCoelutionScore(self) -> List[float]:
        """
        Cython signature: libcpp_vector[double] calcSeparateXcorrContrastCoelutionScore()
        Calculate the separate cross-correlation contrast score
        """
        ...
    
    def calcXcorrPrecursorContrastCoelutionScore(self) -> float:
        """
        Cython signature: double calcXcorrPrecursorContrastCoelutionScore()
        Calculate the precursor cross-correlation contrast score against the transitions
        
        The score is a distance where zero indicates perfect coelution
        """
        ...
    
    def calcXcorrShapeScore(self) -> float:
        """
        Cython signature: double calcXcorrShapeScore()
        Calculate the cross-correlation shape score
        
        The score is a correlation measure where 1 indicates perfect correlation
        and 0 means no correlation.
        """
        ...
    
    def calcXcorrShapeWeightedScore(self, normalized_library_intensity: List[float] ) -> float:
        """
        Cython signature: double calcXcorrShapeWeightedScore(const libcpp_vector[double] & normalized_library_intensity)
        Calculate the weighted cross-correlation shape score
        
        The score is a correlation measure where 1 indicates perfect correlation
        and 0 means no correlation. The score is weighted by the transition
        intensities, non-perfect coelution in low-intensity transitions should
        thus become less important
        """
        ...
    
    def calcSeparateXcorrContrastShapeScore(self) -> List[float]:
        """
        Cython signature: libcpp_vector[double] calcSeparateXcorrContrastShapeScore()
        Calculate the separate cross-correlation contrast shape score
        """
        ...
    
    def calcXcorrPrecursorContrastShapeScore(self) -> float:
        """
        Cython signature: double calcXcorrPrecursorContrastShapeScore()
        Calculate the precursor cross-correlation shape score against the transitions
        """
        ...
    
    def calcRTScore(self, peptide: LightCompound , normalized_experimental_rt: float ) -> float:
        """
        Cython signature: double calcRTScore(LightCompound & peptide, double normalized_experimental_rt)
        """
        ...
    
    def calcMIScore(self) -> float:
        """
        Cython signature: double calcMIScore()
        """
        ...
    
    def calcMIWeightedScore(self, normalized_library_intensity: List[float] ) -> float:
        """
        Cython signature: double calcMIWeightedScore(const libcpp_vector[double] & normalized_library_intensity)
        """
        ...
    
    def calcMIPrecursorScore(self) -> float:
        """
        Cython signature: double calcMIPrecursorScore()
        """
        ...
    
    def calcMIPrecursorContrastScore(self) -> float:
        """
        Cython signature: double calcMIPrecursorContrastScore()
        """
        ...
    
    def calcMIPrecursorCombinedScore(self) -> float:
        """
        Cython signature: double calcMIPrecursorCombinedScore()
        """
        ...
    
    def calcSeparateMIContrastScore(self) -> List[float]:
        """
        Cython signature: libcpp_vector[double] calcSeparateMIContrastScore()
        """
        ...
    
    def getMIMatrix(self) -> MatrixDouble:
        """
        Cython signature: MatrixDouble getMIMatrix()
        """
        ... 


class MSPFile:
    """
    Cython implementation of _MSPFile

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1MSPFile.html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void MSPFile()
        File adapter for MSP files (NIST spectra library)
        """
        ...
    
    @overload
    def __init__(self, in_0: MSPFile ) -> None:
        """
        Cython signature: void MSPFile(MSPFile &)
        """
        ...
    
    def store(self, filename: Union[bytes, str, String] , exp: AnnotatedMSRun ) -> None:
        """
        Cython signature: void store(String filename, AnnotatedMSRun & exp)
        Stores a map in a MSPFile file
        """
        ...
    
    def load(self, filename: Union[bytes, str, String] , ids: PeptideIdentificationList , exp: MSExperiment ) -> None:
        """
        Cython signature: void load(String filename, PeptideIdentificationList & ids, MSExperiment & exp)
        Loads a map from a MSPFile file
        
        
        :param exp: PeakMap which contains the spectra after reading
        :param filename: The filename of the experiment
        :param ids: Output parameter which contains the peptide identifications from the spectra annotations
        """
        ... 


class MetaboTargetedTargetDecoy:
    """
    Cython implementation of _MetaboTargetedTargetDecoy

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1MetaboTargetedTargetDecoy.html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void MetaboTargetedTargetDecoy()
        Resolve overlapping fragments and missing decoys for experimental specific decoy generation in targeted/pseudo targeted metabolomics
        """
        ...
    
    @overload
    def __init__(self, in_0: MetaboTargetedTargetDecoy ) -> None:
        """
        Cython signature: void MetaboTargetedTargetDecoy(MetaboTargetedTargetDecoy &)
        """
        ...
    
    def constructTargetDecoyMassMapping(self, t_exp: TargetedExperiment ) -> List[MetaboTargetedTargetDecoy_MetaboTargetDecoyMassMapping]:
        """
        Cython signature: libcpp_vector[MetaboTargetedTargetDecoy_MetaboTargetDecoyMassMapping] constructTargetDecoyMassMapping(TargetedExperiment & t_exp)
        Constructs a mass mapping of targets and decoys using the unique m_id identifier
        
        
        :param t_exp: TransitionExperiment holds compound and transition information used for the mapping
        """
        ...
    
    def resolveOverlappingTargetDecoyMassesByDecoyMassShift(self, t_exp: TargetedExperiment , mappings: List[MetaboTargetedTargetDecoy_MetaboTargetDecoyMassMapping] , mass_to_add: float , mz_tol: float , mz_tol_unit: String ) -> None:
        """
        Cython signature: void resolveOverlappingTargetDecoyMassesByDecoyMassShift(TargetedExperiment & t_exp, libcpp_vector[MetaboTargetedTargetDecoy_MetaboTargetDecoyMassMapping] & mappings, double & mass_to_add, double & mz_tol, String & mz_tol_unit)
        Resolves overlapping target and decoy transition masses by adding a specifiable mass (e.g. CH2) to the overlapping decoy fragment
        
        
        :param t_exp: TransitionExperiment holds compound and transition information
        :param mappings: Map of identifier to target and decoy masses
        :param mass_to_add: (e.g. CH2)
        :param mz_tol: m/z tolerarance for target and decoy transition masses to be considered overlapping
        :param mz_tol_unit: m/z tolerance unit
        """
        ...
    
    def generateMissingDecoysByMassShift(self, t_exp: TargetedExperiment , mappings: List[MetaboTargetedTargetDecoy_MetaboTargetDecoyMassMapping] , mass_to_add: float ) -> None:
        """
        Cython signature: void generateMissingDecoysByMassShift(TargetedExperiment & t_exp, libcpp_vector[MetaboTargetedTargetDecoy_MetaboTargetDecoyMassMapping] & mappings, double & mass_to_add)
        Generate a decoy for targets where fragmentation tree re-rooting was not possible, by adding a specifiable mass to the target fragments
        
        
        :param t_exp: TransitionExperiment holds compound and transition information
        :param mappings: Map of identifier to target and decoy masses
        :param mass_to_add: The maximum number of transitions required per assay
        """
        ... 


class MetaboTargetedTargetDecoy_MetaboTargetDecoyMassMapping:
    """
    Cython implementation of _MetaboTargetedTargetDecoy_MetaboTargetDecoyMassMapping

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1MetaboTargetedTargetDecoy_MetaboTargetDecoyMassMapping.html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void MetaboTargetedTargetDecoy_MetaboTargetDecoyMassMapping()
        """
        ...
    
    @overload
    def __init__(self, in_0: MetaboTargetedTargetDecoy_MetaboTargetDecoyMassMapping ) -> None:
        """
        Cython signature: void MetaboTargetedTargetDecoy_MetaboTargetDecoyMassMapping(MetaboTargetedTargetDecoy_MetaboTargetDecoyMassMapping &)
        """
        ... 


class MobilityPeak1D:
    """
    Cython implementation of _MobilityPeak1D

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1MobilityPeak1D.html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void MobilityPeak1D()
        """
        ...
    
    @overload
    def __init__(self, in_0: MobilityPeak1D ) -> None:
        """
        Cython signature: void MobilityPeak1D(MobilityPeak1D &)
        """
        ...
    
    def getIntensity(self) -> float:
        """
        Cython signature: float getIntensity()
        """
        ...
    
    def getMobility(self) -> float:
        """
        Cython signature: double getMobility()
        """
        ...
    
    def setMobility(self, in_0: float ) -> None:
        """
        Cython signature: void setMobility(double)
        """
        ...
    
    def setIntensity(self, in_0: float ) -> None:
        """
        Cython signature: void setIntensity(float)
        """
        ...
    
    def getPos(self) -> float:
        """
        Cython signature: double getPos()
        """
        ...
    
    def setPos(self, pos: float ) -> None:
        """
        Cython signature: void setPos(double pos)
        """
        ...
    
    def __richcmp__(self, other: MobilityPeak1D, op: int) -> Any:
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


class MzMLSpectrumDecoder:
    """
    Cython implementation of _MzMLSpectrumDecoder

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1MzMLSpectrumDecoder.html>`_

    A class to decode input strings that contain an mzML chromatogram or spectrum tag
    
    It uses xercesc to parse a string containing either a exactly one mzML
    spectrum or chromatogram (from <chromatogram> to </chromatogram> or
    <spectrum> to </spectrum> tag). It returns the data contained in the
    binaryDataArray for Intensity / mass-to-charge or Intensity / time
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void MzMLSpectrumDecoder()
        """
        ...
    
    @overload
    def __init__(self, in_0: MzMLSpectrumDecoder ) -> None:
        """
        Cython signature: void MzMLSpectrumDecoder(MzMLSpectrumDecoder &)
        """
        ...
    
    def domParseChromatogram(self, in_: Union[bytes, str, String] , cptr: _Interfaces_Chromatogram ) -> None:
        """
        Cython signature: void domParseChromatogram(String in_, shared_ptr[_Interfaces_Chromatogram] & cptr)
        Extract data from a string which contains a full mzML chromatogram
        
        Extracts data from the input string which is expected to contain exactly
        one <chromatogram> tag (from <chromatogram> to </chromatogram>). This
        function will extract the contained binaryDataArray and provide the
        result as Chromatogram
        
        
        :param in: Input string containing the raw XML
        :param cptr: Resulting chromatogram
        """
        ...
    
    def domParseSpectrum(self, in_: Union[bytes, str, String] , cptr: _Interfaces_Spectrum ) -> None:
        """
        Cython signature: void domParseSpectrum(String in_, shared_ptr[_Interfaces_Spectrum] & cptr)
        Extract data from a string which contains a full mzML spectrum
        
        Extracts data from the input string which is expected to contain exactly
        one <spectrum> tag (from <spectrum> to </spectrum>). This function will
        extract the contained binaryDataArray and provide the result as Spectrum
        
        
        :param in: Input string containing the raw XML
        :param cptr: Resulting spectrum
        """
        ...
    
    def setSkipXMLChecks(self, only: bool ) -> None:
        """
        Cython signature: void setSkipXMLChecks(bool only)
        Whether to skip some XML checks (e.g. removing whitespace inside base64 arrays) and be fast instead
        """
        ... 


class NucleicAcidSpectrumGenerator:
    """
    Cython implementation of _NucleicAcidSpectrumGenerator

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1NucleicAcidSpectrumGenerator.html>`_
      -- Inherits from ['DefaultParamHandler']
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void NucleicAcidSpectrumGenerator()
        """
        ...
    
    @overload
    def __init__(self, in_0: NucleicAcidSpectrumGenerator ) -> None:
        """
        Cython signature: void NucleicAcidSpectrumGenerator(NucleicAcidSpectrumGenerator &)
        """
        ...
    
    def getSpectrum(self, spec: MSSpectrum , oligo: NASequence , min_charge: int , max_charge: int ) -> None:
        """
        Cython signature: void getSpectrum(MSSpectrum & spec, NASequence & oligo, int min_charge, int max_charge)
        Generates a spectrum for a peptide sequence, with the ion types that are set in the tool parameters. If precursor_charge is set to 0 max_charge + 1 will be used
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


class OPXL_PreprocessedPairSpectra:
    """
    Cython implementation of _OPXL_PreprocessedPairSpectra

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS::OPXLDataStructs_1_1OPXL_PreprocessedPairSpectra.html>`_
    """
    
    spectra_linear_peaks: MSExperiment
    
    spectra_xlink_peaks: MSExperiment
    
    spectra_all_peaks: MSExperiment
    
    @overload
    def __init__(self, size: int ) -> None:
        """
        Cython signature: void OPXL_PreprocessedPairSpectra(size_t size)
        """
        ...
    
    @overload
    def __init__(self, in_0: OPXL_PreprocessedPairSpectra ) -> None:
        """
        Cython signature: void OPXL_PreprocessedPairSpectra(OPXL_PreprocessedPairSpectra &)
        """
        ... 


class OnDiscMSExperiment:
    """
    Cython implementation of _OnDiscMSExperiment

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1OnDiscMSExperiment.html>`_

    Representation of a mass spectrometry experiment on disk.
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void OnDiscMSExperiment()
        """
        ...
    
    @overload
    def __init__(self, in_0: OnDiscMSExperiment ) -> None:
        """
        Cython signature: void OnDiscMSExperiment(OnDiscMSExperiment &)
        """
        ...
    
    @overload
    def openFile(self, filename: Union[bytes, str, String] ) -> bool:
        """
        Cython signature: bool openFile(String filename)
        """
        ...
    
    @overload
    def openFile(self, filename: Union[bytes, str, String] , skipLoadingMetaData: bool ) -> bool:
        """
        Cython signature: bool openFile(String filename, bool skipLoadingMetaData)
        Open a specific file on disk
        
        This tries to read the indexed mzML by parsing the index and then reading the meta information into memory
        
        returns: Whether the parsing of the file was successful (if false, the file most likely was not an indexed mzML file)
        """
        ...
    
    def getNrSpectra(self) -> int:
        """
        Cython signature: size_t getNrSpectra()
        Returns the total number of spectra available
        """
        ...
    
    def getNrChromatograms(self) -> int:
        """
        Cython signature: size_t getNrChromatograms()
        Returns the total number of chromatograms available
        """
        ...
    
    def getExperimentalSettings(self) -> ExperimentalSettings:
        """
        Cython signature: shared_ptr[const ExperimentalSettings] getExperimentalSettings()
        Returns the meta information of this experiment (const access)
        """
        ...
    
    def getMetaData(self) -> MSExperiment:
        """
        Cython signature: shared_ptr[MSExperiment] getMetaData()
        Returns the meta information of this experiment
        """
        ...
    
    def getSpectrum(self, id: int ) -> MSSpectrum:
        """
        Cython signature: MSSpectrum getSpectrum(size_t id)
        Returns a single spectrum
        
        
        :param id: The index of the spectrum
        """
        ...
    
    def getSpectrumByNativeId(self, id: Union[bytes, str, String] ) -> MSSpectrum:
        """
        Cython signature: MSSpectrum getSpectrumByNativeId(String id)
        Returns a single spectrum
        
        
        :param id: The native identifier of the spectrum
        """
        ...
    
    def getChromatogram(self, id: int ) -> MSChromatogram:
        """
        Cython signature: MSChromatogram getChromatogram(size_t id)
        Returns a single chromatogram
        
        
        :param id: The index of the chromatogram
        """
        ...
    
    def getChromatogramByNativeId(self, id: Union[bytes, str, String] ) -> MSChromatogram:
        """
        Cython signature: MSChromatogram getChromatogramByNativeId(String id)
        Returns a single chromatogram
        
        
        :param id: The native identifier of the chromatogram
        """
        ...
    
    def getSpectrumById(self, id_: int ) -> _Interfaces_Spectrum:
        """
        Cython signature: shared_ptr[_Interfaces_Spectrum] getSpectrumById(int id_)
        Returns a single spectrum
        """
        ...
    
    def getChromatogramById(self, id_: int ) -> _Interfaces_Chromatogram:
        """
        Cython signature: shared_ptr[_Interfaces_Chromatogram] getChromatogramById(int id_)
        Returns a single chromatogram
        """
        ...
    
    def setSkipXMLChecks(self, skip: bool ) -> None:
        """
        Cython signature: void setSkipXMLChecks(bool skip)
        Sets whether to skip some XML checks and be fast instead
        """
        ... 


class ParamNode:
    """
    Cython implementation of _ParamNode

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS::Param_1_1ParamNode.html>`_
    """
    
    name: Union[bytes, str, String]
    
    description: Union[bytes, str, String]
    
    entries: List[ParamEntry]
    
    nodes: List[ParamNode]
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void ParamNode()
        """
        ...
    
    @overload
    def __init__(self, in_0: ParamNode ) -> None:
        """
        Cython signature: void ParamNode(ParamNode &)
        """
        ...
    
    @overload
    def __init__(self, n: Union[bytes, str, String] , d: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void ParamNode(const String & n, const String & d)
        """
        ...
    
    def findParentOf(self, name: Union[bytes, str, String] ) -> ParamNode:
        """
        Cython signature: ParamNode * findParentOf(const String & name)
        """
        ...
    
    def findEntryRecursive(self, name: Union[bytes, str, String] ) -> ParamEntry:
        """
        Cython signature: ParamEntry * findEntryRecursive(const String & name)
        """
        ...
    
    @overload
    def insert(self, node: ParamNode , prefix: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void insert(ParamNode & node, const String & prefix)
        """
        ...
    
    @overload
    def insert(self, entry: ParamEntry , prefix: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void insert(ParamEntry & entry, const String & prefix)
        """
        ...
    
    def size(self) -> int:
        """
        Cython signature: size_t size()
        """
        ...
    
    def suffix(self, key: Union[bytes, str, String] ) -> Union[bytes, str, String]:
        """
        Cython signature: String suffix(const String & key)
        """
        ...
    
    def __richcmp__(self, other: ParamNode, op: int) -> Any:
        ... 


class Peak1D:
    """
    Cython implementation of _Peak1D

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1Peak1D.html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void Peak1D()
        """
        ...
    
    @overload
    def __init__(self, in_0: Peak1D ) -> None:
        """
        Cython signature: void Peak1D(Peak1D &)
        """
        ...
    
    def getIntensity(self) -> float:
        """
        Cython signature: float getIntensity()
        """
        ...
    
    def getMZ(self) -> float:
        """
        Cython signature: double getMZ()
        """
        ...
    
    def setMZ(self, in_0: float ) -> None:
        """
        Cython signature: void setMZ(double)
        """
        ...
    
    def setIntensity(self, in_0: float ) -> None:
        """
        Cython signature: void setIntensity(float)
        """
        ...
    
    def getPos(self) -> float:
        """
        Cython signature: double getPos()
        """
        ...
    
    def setPos(self, pos: float ) -> None:
        """
        Cython signature: void setPos(double pos)
        """
        ...
    
    def __richcmp__(self, other: Peak1D, op: int) -> Any:
        ... 


class PeptideIdentificationList:
    """
    Cython implementation of _PeptideIdentificationList

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1PeptideIdentificationList.html>`_

    A container for peptide identifications from multiple spectra.
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void PeptideIdentificationList()
        """
        ...
    
    @overload
    def __init__(self, in_0: PeptideIdentificationList ) -> None:
        """
        Cython signature: void PeptideIdentificationList(PeptideIdentificationList)
        """
        ...
    
    def size(self) -> int:
        """
        Cython signature: int size()
        Returns the number of peptide identifications
        """
        ...
    
    def empty(self) -> bool:
        """
        Cython signature: bool empty()
        Returns true if the container is empty
        """
        ...
    
    def clear(self) -> None:
        """
        Cython signature: void clear()
        Removes all peptide identifications from the container
        """
        ...
    
    def push_back(self, in_0: PeptideIdentification ) -> None:
        """
        Cython signature: void push_back(PeptideIdentification)
        Adds a peptide identification to the end of the container
        """
        ...
    
    def __getitem__(self, in_0: int ) -> PeptideIdentification:
        """
        Cython signature: PeptideIdentification & operator[](size_t)
        """
        ...
    def __setitem__(self, key: int, value: PeptideIdentification) -> None:
        """Cython signature: PeptideIdentification & operator[](size_t)"""
        ...
    
    def at(self, in_0: int ) -> PeptideIdentification:
        """
        Cython signature: PeptideIdentification at(size_t)
        Returns the peptide identification at the given index with bounds checking
        """
        ...
    
    def back(self) -> PeptideIdentification:
        """
        Cython signature: PeptideIdentification back()
        Returns the last peptide identification in the container
        """
        ...
    
    def front(self) -> PeptideIdentification:
        """
        Cython signature: PeptideIdentification front()
        Returns the first peptide identification in the container
        """
        ...
    
    def __iter__(self) -> PeptideIdentification:
       ... 


class PeptideSearchEngineFIAlgorithm:
    """
    Cython implementation of _PeptideSearchEngineFIAlgorithm

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1PeptideSearchEngineFIAlgorithm.html>`_
      -- Inherits from ['DefaultParamHandler', 'ProgressLogger']

     Fragment-index-based peptide database search algorithm (experimental).
    
     Provides a self-contained search engine that matches MS/MS spectra against a protein
     database using an FI (Fragment Index). Typical usage:
     - Configure parameters via DefaultParamHandler (mass tolerances, enzyme, charges, etc.)
     - Call search() with an input mzML file and a FASTA database to populate identification
       outputs (ProteinIdentification and PeptideIdentificationList)
     - Intended for educational/prototyping use and to demonstrate FI-backed searching
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void PeptideSearchEngineFIAlgorithm()
        """
        ...
    
    @overload
    def __init__(self, in_0: PeptideSearchEngineFIAlgorithm ) -> None:
        """
        Cython signature: void PeptideSearchEngineFIAlgorithm(PeptideSearchEngineFIAlgorithm &)
        """
        ...
    
    def search(self, in_mzML: Union[bytes, str, String] , in_db: Union[bytes, str, String] , prot_ids: List[ProteinIdentification] , pep_ids: PeptideIdentificationList ) -> int:
        """
        Cython signature: PeptideSearchEngineFIAlgorithm_ExitCodes search(const String & in_mzML, const String & in_db, libcpp_vector[ProteinIdentification] & prot_ids, PeptideIdentificationList & pep_ids)
         Search spectra in an mzML file against a protein database using an FI-backed workflow.
        
         Populates protein and peptide identifications, including search meta data, PSM hits,
         and search engine annotations. Parameters are taken from this instance.
        
         :param in_mzML: Input path to the mzML file containing MS/MS spectra to search
         :param in_db: Input path to the protein sequence database in FASTA format
         :param prot_ids: Output container receiving search meta data and protein-level information
         :param pep_ids: Output container receiving spectrum-level peptide identifications (PSMs)
         :returns: ExitCodes indicating success (EXECUTION_OK) or the encountered error condition
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
    PeptideSearchEngineFIAlgorithm_ExitCodes : __PeptideSearchEngineFIAlgorithm_ExitCodes 


class ProteaseDB:
    """
    Cython implementation of _ProteaseDB

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1ProteaseDB.html>`_
    """
    
    def getEnzyme(self, name: Union[bytes, str, String] ) -> DigestionEnzymeProtein:
        """
        Cython signature: const DigestionEnzymeProtein * getEnzyme(const String & name)
        """
        ...
    
    def getEnzymeByRegEx(self, cleavage_regex: Union[bytes, str, String] ) -> DigestionEnzymeProtein:
        """
        Cython signature: const DigestionEnzymeProtein * getEnzymeByRegEx(const String & cleavage_regex)
        """
        ...
    
    def getAllNames(self, all_names: List[bytes] ) -> None:
        """
        Cython signature: void getAllNames(libcpp_vector[String] & all_names)
        """
        ...
    
    def getAllXTandemNames(self, all_names: List[bytes] ) -> None:
        """
        Cython signature: void getAllXTandemNames(libcpp_vector[String] & all_names)
        Returns all the enzyme names available for XTandem
        """
        ...
    
    def getAllOMSSANames(self, all_names: List[bytes] ) -> None:
        """
        Cython signature: void getAllOMSSANames(libcpp_vector[String] & all_names)
        Returns all the enzyme names available for OMSSA
        """
        ...
    
    def getAllCometNames(self, all_names: List[bytes] ) -> None:
        """
        Cython signature: void getAllCometNames(libcpp_vector[String] & all_names)
        Returns all the enzyme names available for Comet
        """
        ...
    
    def getAllMSGFNames(self, all_names: List[bytes] ) -> None:
        """
        Cython signature: void getAllMSGFNames(libcpp_vector[String] & all_names)
        Returns all the enzyme names available for MSGFPlus
        """
        ...
    
    def hasEnzyme(self, name: Union[bytes, str, String] ) -> bool:
        """
        Cython signature: bool hasEnzyme(const String & name)
        """
        ...
    
    def hasRegEx(self, cleavage_regex: Union[bytes, str, String] ) -> bool:
        """
        Cython signature: bool hasRegEx(const String & cleavage_regex)
        """
        ... 


class ProteinInference:
    """
    Cython implementation of _ProteinInference

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1ProteinInference.html>`_

    [experimental class] given a peptide quantitation, infer corresponding protein quantities
    
    Infers protein ratios from peptide ratios (currently using unique peptides only).
    Use the IDMapper class to add protein and peptide information to a
    quantitative ConsensusMap prior to this step
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void ProteinInference()
        """
        ...
    
    @overload
    def __init__(self, in_0: ProteinInference ) -> None:
        """
        Cython signature: void ProteinInference(ProteinInference &)
        """
        ...
    
    def infer(self, consensus_map: ConsensusMap , reference_map: int ) -> None:
        """
        Cython signature: void infer(ConsensusMap & consensus_map, unsigned int reference_map)
        Given a peptide quantitation, infer corresponding protein quantities
        
        Infers protein ratios from peptide ratios (currently using unique peptides only).
        Use the IDMapper class to add protein and peptide information to a
        quantitative ConsensusMap prior to this step
        
        
        :param consensus_map: Peptide quantitation with ProteinIdentifications attached, where protein quantitation will be attached
        :param reference_map: Index of (iTRAQ) reference channel within the consensus map
        """
        ... 


class QTCluster:
    """
    Cython implementation of _QTCluster

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1QTCluster.html>`_
    """
    
    def __init__(self, in_0: QTCluster ) -> None:
        """
        Cython signature: void QTCluster(QTCluster &)
        """
        ...
    
    def getCenterRT(self) -> float:
        """
        Cython signature: double getCenterRT()
        Returns the RT value of the cluster
        """
        ...
    
    def getCenterMZ(self) -> float:
        """
        Cython signature: double getCenterMZ()
        Returns the m/z value of the cluster center
        """
        ...
    
    def getXCoord(self) -> int:
        """
        Cython signature: int getXCoord()
        Returns the x coordinate in the grid
        """
        ...
    
    def getYCoord(self) -> int:
        """
        Cython signature: int getYCoord()
        Returns the y coordinate in the grid
        """
        ...
    
    def size(self) -> int:
        """
        Cython signature: size_t size()
        Returns the size of the cluster (number of elements, incl. center)
        """
        ...
    
    def getQuality(self) -> float:
        """
        Cython signature: double getQuality()
        Returns the cluster quality and recomputes if necessary
        """
        ...
    
    def getAnnotations(self) -> Set[AASequence]:
        """
        Cython signature: libcpp_set[AASequence] getAnnotations()
        Returns the set of peptide sequences annotated to the cluster center
        """
        ...
    
    def setInvalid(self) -> None:
        """
        Cython signature: void setInvalid()
        Sets current cluster as invalid (also frees some memory)
        """
        ...
    
    def isInvalid(self) -> bool:
        """
        Cython signature: bool isInvalid()
        Whether current cluster is invalid
        """
        ...
    
    def initializeCluster(self) -> None:
        """
        Cython signature: void initializeCluster()
        Has to be called before adding elements (calling
        """
        ...
    
    def finalizeCluster(self) -> None:
        """
        Cython signature: void finalizeCluster()
        Has to be called after adding elements (after calling
        """
        ...
    
    def __richcmp__(self, other: QTCluster, op: int) -> Any:
        ... 


class RansacModelLinear:
    """
    Cython implementation of _RansacModelLinear

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS::Math_1_1RansacModelLinear.html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void RansacModelLinear()
        """
        ...
    
    @overload
    def __init__(self, in_0: RansacModelLinear ) -> None:
        """
        Cython signature: void RansacModelLinear(RansacModelLinear &)
        """
        ... 


class Ratio:
    """
    Cython implementation of _Ratio

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1Ratio.html>`_
    """
    
    ratio_value_: float
    
    denominator_ref_: Union[bytes, str, String]
    
    numerator_ref_: Union[bytes, str, String]
    
    description_: List[bytes]
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void Ratio()
        """
        ...
    
    @overload
    def __init__(self, rhs: Ratio ) -> None:
        """
        Cython signature: void Ratio(Ratio rhs)
        """
        ... 


class Residue:
    """
    Cython implementation of _Residue

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1Residue.html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void Residue()
        """
        ...
    
    @overload
    def __init__(self, in_0: Residue ) -> None:
        """
        Cython signature: void Residue(Residue &)
        """
        ...
    
    @overload
    def __init__(self, name: Union[bytes, str, String] , three_letter_code: Union[bytes, str, String] , one_letter_code: Union[bytes, str, String] , formula: EmpiricalFormula ) -> None:
        """
        Cython signature: void Residue(String name, String three_letter_code, String one_letter_code, EmpiricalFormula formula)
        """
        ...
    
    def getInternalToFull(self) -> EmpiricalFormula:
        """
        Cython signature: EmpiricalFormula getInternalToFull()
        """
        ...
    
    def getInternalToNTerm(self) -> EmpiricalFormula:
        """
        Cython signature: EmpiricalFormula getInternalToNTerm()
        """
        ...
    
    def getInternalToCTerm(self) -> EmpiricalFormula:
        """
        Cython signature: EmpiricalFormula getInternalToCTerm()
        """
        ...
    
    def getInternalToAIon(self) -> EmpiricalFormula:
        """
        Cython signature: EmpiricalFormula getInternalToAIon()
        """
        ...
    
    def getInternalToBIon(self) -> EmpiricalFormula:
        """
        Cython signature: EmpiricalFormula getInternalToBIon()
        """
        ...
    
    def getInternalToCIon(self) -> EmpiricalFormula:
        """
        Cython signature: EmpiricalFormula getInternalToCIon()
        """
        ...
    
    def getInternalToXIon(self) -> EmpiricalFormula:
        """
        Cython signature: EmpiricalFormula getInternalToXIon()
        """
        ...
    
    def getInternalToYIon(self) -> EmpiricalFormula:
        """
        Cython signature: EmpiricalFormula getInternalToYIon()
        """
        ...
    
    def getInternalToZIon(self) -> EmpiricalFormula:
        """
        Cython signature: EmpiricalFormula getInternalToZIon()
        """
        ...
    
    def getResidueTypeName(self, res_type: int ) -> Union[bytes, str, String]:
        """
        Cython signature: String getResidueTypeName(ResidueType res_type)
        Returns the ion name given as a residue type
        """
        ...
    
    def setName(self, name: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setName(String name)
        Sets the name of the residue
        """
        ...
    
    def getName(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getName()
        Returns the name of the residue
        """
        ...
    
    def setSynonyms(self, synonyms: Set[bytes] ) -> None:
        """
        Cython signature: void setSynonyms(libcpp_set[String] synonyms)
        Sets the synonyms
        """
        ...
    
    def addSynonym(self, synonym: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void addSynonym(String synonym)
        Adds a synonym
        """
        ...
    
    def getSynonyms(self) -> Set[bytes]:
        """
        Cython signature: libcpp_set[String] getSynonyms()
        Returns the sysnonyms
        """
        ...
    
    def setThreeLetterCode(self, three_letter_code: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setThreeLetterCode(String three_letter_code)
        Sets the name of the residue as three letter code
        """
        ...
    
    def getThreeLetterCode(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getThreeLetterCode()
        Returns the name of the residue as three letter code
        """
        ...
    
    def setOneLetterCode(self, one_letter_code: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setOneLetterCode(String one_letter_code)
        Sets the name as one letter code
        """
        ...
    
    def getOneLetterCode(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getOneLetterCode()
        Returns the name as one letter code
        """
        ...
    
    def addLossFormula(self, in_0: EmpiricalFormula ) -> None:
        """
        Cython signature: void addLossFormula(EmpiricalFormula)
        Adds a neutral loss formula
        """
        ...
    
    def setLossFormulas(self, in_0: List[EmpiricalFormula] ) -> None:
        """
        Cython signature: void setLossFormulas(libcpp_vector[EmpiricalFormula])
        Sets the neutral loss formulas
        """
        ...
    
    def addNTermLossFormula(self, in_0: EmpiricalFormula ) -> None:
        """
        Cython signature: void addNTermLossFormula(EmpiricalFormula)
        Adds N-terminal losses
        """
        ...
    
    def setNTermLossFormulas(self, in_0: List[EmpiricalFormula] ) -> None:
        """
        Cython signature: void setNTermLossFormulas(libcpp_vector[EmpiricalFormula])
        Sets the N-terminal losses
        """
        ...
    
    def getLossFormulas(self) -> List[EmpiricalFormula]:
        """
        Cython signature: libcpp_vector[EmpiricalFormula] getLossFormulas()
        Returns the neutral loss formulas
        """
        ...
    
    def getNTermLossFormulas(self) -> List[EmpiricalFormula]:
        """
        Cython signature: libcpp_vector[EmpiricalFormula] getNTermLossFormulas()
        Returns N-terminal loss formulas
        """
        ...
    
    def setLossNames(self, name: List[bytes] ) -> None:
        """
        Cython signature: void setLossNames(libcpp_vector[String] name)
        Sets the neutral loss molecule name
        """
        ...
    
    def setNTermLossNames(self, name: List[bytes] ) -> None:
        """
        Cython signature: void setNTermLossNames(libcpp_vector[String] name)
        Sets the N-terminal loss names
        """
        ...
    
    def addLossName(self, name: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void addLossName(String name)
        Adds neutral loss molecule name
        """
        ...
    
    def addNTermLossName(self, name: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void addNTermLossName(String name)
        Adds a N-terminal loss name
        """
        ...
    
    def getLossNames(self) -> List[bytes]:
        """
        Cython signature: libcpp_vector[String] getLossNames()
        Gets neutral loss name (if there is one, else returns an empty string)
        """
        ...
    
    def getNTermLossNames(self) -> List[bytes]:
        """
        Cython signature: libcpp_vector[String] getNTermLossNames()
        Returns the N-terminal loss names
        """
        ...
    
    def setFormula(self, formula: EmpiricalFormula ) -> None:
        """
        Cython signature: void setFormula(EmpiricalFormula formula)
        Sets empirical formula of the residue (must be full, with N and C-terminus)
        """
        ...
    
    @overload
    def getFormula(self, ) -> EmpiricalFormula:
        """
        Cython signature: EmpiricalFormula getFormula()
        Returns the empirical formula of the residue
        """
        ...
    
    @overload
    def getFormula(self, res_type: int ) -> EmpiricalFormula:
        """
        Cython signature: EmpiricalFormula getFormula(ResidueType res_type)
        """
        ...
    
    def setAverageWeight(self, weight: float ) -> None:
        """
        Cython signature: void setAverageWeight(double weight)
        Sets average weight of the residue (must be full, with N and C-terminus)
        """
        ...
    
    @overload
    def getAverageWeight(self, ) -> float:
        """
        Cython signature: double getAverageWeight()
        Returns average weight of the residue
        """
        ...
    
    @overload
    def getAverageWeight(self, res_type: int ) -> float:
        """
        Cython signature: double getAverageWeight(ResidueType res_type)
        """
        ...
    
    def setMonoWeight(self, weight: float ) -> None:
        """
        Cython signature: void setMonoWeight(double weight)
        Sets monoisotopic weight of the residue (must be full, with N and C-terminus)
        """
        ...
    
    @overload
    def getMonoWeight(self, ) -> float:
        """
        Cython signature: double getMonoWeight()
        Returns monoisotopic weight of the residue
        """
        ...
    
    @overload
    def getMonoWeight(self, res_type: int ) -> float:
        """
        Cython signature: double getMonoWeight(ResidueType res_type)
        """
        ...
    
    def getModification(self) -> ResidueModification:
        """
        Cython signature: const ResidueModification * getModification()
        """
        ...
    
    @overload
    def setModification(self, name: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setModification(String name)
        Sets the modification by name; the mod should be present in ModificationsDB
        """
        ...
    
    @overload
    def setModification(self, mod: ResidueModification ) -> None:
        """
        Cython signature: void setModification(const ResidueModification & mod)
        Sets the modification by a ResidueModification object; checks if present in ModificationsDB and adds if not.
        """
        ...
    
    def setModificationByDiffMonoMass(self, diffMonoMass: float ) -> None:
        """
        Cython signature: void setModificationByDiffMonoMass(double diffMonoMass)
        Sets the modification by monoisotopic mass difference in Da; checks if present in ModificationsDB with tolerance and adds a "user-defined" modification if not (for later lookups).
        """
        ...
    
    def getModificationName(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getModificationName()
        Returns the name of the modification to the modification
        """
        ...
    
    def setLowMassIons(self, low_mass_ions: List[EmpiricalFormula] ) -> None:
        """
        Cython signature: void setLowMassIons(libcpp_vector[EmpiricalFormula] low_mass_ions)
        Sets the low mass marker ions as a vector of formulas
        """
        ...
    
    def getLowMassIons(self) -> List[EmpiricalFormula]:
        """
        Cython signature: libcpp_vector[EmpiricalFormula] getLowMassIons()
        Returns a vector of formulas with the low mass markers of the residue
        """
        ...
    
    def setResidueSets(self, residues_sets: Set[bytes] ) -> None:
        """
        Cython signature: void setResidueSets(libcpp_set[String] residues_sets)
        Sets the residue sets the amino acid is contained in
        """
        ...
    
    def addResidueSet(self, residue_sets: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void addResidueSet(String residue_sets)
        Adds a residue set to the residue sets
        """
        ...
    
    def getResidueSets(self) -> Set[bytes]:
        """
        Cython signature: libcpp_set[String] getResidueSets()
        Returns the residue sets this residue is contained in
        """
        ...
    
    def hasNeutralLoss(self) -> bool:
        """
        Cython signature: bool hasNeutralLoss()
        True if the residue has neutral loss
        """
        ...
    
    def hasNTermNeutralLosses(self) -> bool:
        """
        Cython signature: bool hasNTermNeutralLosses()
        True if N-terminal neutral losses are set
        """
        ...
    
    def getPka(self) -> float:
        """
        Cython signature: double getPka()
        Returns the pka of the residue
        """
        ...
    
    def getPkb(self) -> float:
        """
        Cython signature: double getPkb()
        Returns the pkb of the residue
        """
        ...
    
    def getPkc(self) -> float:
        """
        Cython signature: double getPkc()
        Returns the pkc of the residue if it exists otherwise -1
        """
        ...
    
    def getPiValue(self) -> float:
        """
        Cython signature: double getPiValue()
        Calculates the isoelectric point using the pk values
        """
        ...
    
    def setPka(self, value: float ) -> None:
        """
        Cython signature: void setPka(double value)
        Sets the pka of the residue
        """
        ...
    
    def setPkb(self, value: float ) -> None:
        """
        Cython signature: void setPkb(double value)
        Sets the pkb of the residue
        """
        ...
    
    def setPkc(self, value: float ) -> None:
        """
        Cython signature: void setPkc(double value)
        Sets the pkc of the residue
        """
        ...
    
    def getSideChainBasicity(self) -> float:
        """
        Cython signature: double getSideChainBasicity()
        Returns the side chain basicity
        """
        ...
    
    def setSideChainBasicity(self, gb_sc: float ) -> None:
        """
        Cython signature: void setSideChainBasicity(double gb_sc)
        Sets the side chain basicity
        """
        ...
    
    def getBackboneBasicityLeft(self) -> float:
        """
        Cython signature: double getBackboneBasicityLeft()
        Returns the backbone basicitiy if located in N-terminal direction
        """
        ...
    
    def setBackboneBasicityLeft(self, gb_bb_l: float ) -> None:
        """
        Cython signature: void setBackboneBasicityLeft(double gb_bb_l)
        Sets the N-terminal direction backbone basicitiy
        """
        ...
    
    def getBackboneBasicityRight(self) -> float:
        """
        Cython signature: double getBackboneBasicityRight()
        Returns the C-terminal direction backbone basicitiy
        """
        ...
    
    def setBackboneBasicityRight(self, gb_bb_r: float ) -> None:
        """
        Cython signature: void setBackboneBasicityRight(double gb_bb_r)
        Sets the C-terminal direction backbone basicity
        """
        ...
    
    def isModified(self) -> bool:
        """
        Cython signature: bool isModified()
        True if the residue is a modified one
        """
        ...
    
    def isInResidueSet(self, residue_set: Union[bytes, str, String] ) -> bool:
        """
        Cython signature: bool isInResidueSet(String residue_set)
        True if the residue is contained in the set
        """
        ...
    
    def residueTypeToIonLetter(self, res_type: int ) -> Union[bytes, str, String]:
        """
        Cython signature: String residueTypeToIonLetter(ResidueType res_type)
        Helper for mapping residue types to letters for Text annotations and labels
        """
        ...
    
    def __richcmp__(self, other: Residue, op: int) -> Any:
        ...
    ResidueType : __ResidueType 


class ScanWindow:
    """
    Cython implementation of _ScanWindow

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1ScanWindow.html>`_
      -- Inherits from ['MetaInfoInterface']
    """
    
    begin: float
    
    end: float
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void ScanWindow()
        """
        ...
    
    @overload
    def __init__(self, in_0: ScanWindow ) -> None:
        """
        Cython signature: void ScanWindow(ScanWindow &)
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
    
    def __richcmp__(self, other: ScanWindow, op: int) -> Any:
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


class SwathMap:
    """
    Cython implementation of _SwathMap

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenSwath_1_1SwathMap.html>`_
    """
    
    lower: float
    
    upper: float
    
    center: float
    
    ms1: bool
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void SwathMap()
        Data structure to hold one SWATH map with information about upper / lower isolation window and whether the map is MS1 or MS2
        """
        ...
    
    @overload
    def __init__(self, in_0: SwathMap ) -> None:
        """
        Cython signature: void SwathMap(SwathMap &)
        """
        ...
    
    @overload
    def __init__(self, mz_start: float , mz_end: float , mz_center: float , is_ms1: bool ) -> None:
        """
        Cython signature: void SwathMap(double mz_start, double mz_end, double mz_center, bool is_ms1)
        """
        ... 


class TMTEighteenPlexQuantitationMethod:
    """
    Cython implementation of _TMTEighteenPlexQuantitationMethod

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1TMTEighteenPlexQuantitationMethod.html>`_
      -- Inherits from ['IsobaricQuantitationMethod']
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void TMTEighteenPlexQuantitationMethod()
        """
        ...
    
    @overload
    def __init__(self, in_0: TMTEighteenPlexQuantitationMethod ) -> None:
        """
        Cython signature: void TMTEighteenPlexQuantitationMethod(TMTEighteenPlexQuantitationMethod &)
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


class TMTTenPlexQuantitationMethod:
    """
    Cython implementation of _TMTTenPlexQuantitationMethod

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1TMTTenPlexQuantitationMethod.html>`_
      -- Inherits from ['IsobaricQuantitationMethod']
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void TMTTenPlexQuantitationMethod()
        """
        ...
    
    @overload
    def __init__(self, in_0: TMTTenPlexQuantitationMethod ) -> None:
        """
        Cython signature: void TMTTenPlexQuantitationMethod(TMTTenPlexQuantitationMethod &)
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


class ThresholdMower:
    """
    Cython implementation of _ThresholdMower

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1ThresholdMower.html>`_
      -- Inherits from ['DefaultParamHandler']
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void ThresholdMower()
        """
        ...
    
    @overload
    def __init__(self, in_0: ThresholdMower ) -> None:
        """
        Cython signature: void ThresholdMower(ThresholdMower &)
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


class TraMLFile:
    """
    Cython implementation of _TraMLFile

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1TraMLFile.html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void TraMLFile()
        """
        ...
    
    @overload
    def __init__(self, in_0: TraMLFile ) -> None:
        """
        Cython signature: void TraMLFile(TraMLFile &)
        """
        ...
    
    def load(self, filename: Union[bytes, str, String] , id: TargetedExperiment ) -> None:
        """
        Cython signature: void load(String filename, TargetedExperiment & id)
        Loads a map from a TraML file
        """
        ...
    
    def store(self, filename: Union[bytes, str, String] , id: TargetedExperiment ) -> None:
        """
        Cython signature: void store(String filename, TargetedExperiment & id)
        Stores a map in a TraML file
        """
        ...
    
    def isSemanticallyValid(self, filename: Union[bytes, str, String] , errors: List[bytes] , warnings: List[bytes] ) -> bool:
        """
        Cython signature: bool isSemanticallyValid(String filename, StringList & errors, StringList & warnings)
        Checks if a file is valid with respect to the mapping file and the controlled vocabulary
        
        :param filename: File name of the file to be checked
        :param errors: Errors during the validation are returned in this output parameter
        :param warnings: Warnings during the validation are returned in this output parameter
        """
        ... 


class TransformationDescription:
    """
    Cython implementation of _TransformationDescription

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS::TransformationDescription_1_1TransformationDescription.html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void TransformationDescription()
        """
        ...
    
    @overload
    def __init__(self, in_0: TransformationDescription ) -> None:
        """
        Cython signature: void TransformationDescription(TransformationDescription &)
        """
        ...
    
    def getDataPoints(self) -> List[TM_DataPoint]:
        """
        Cython signature: libcpp_vector[TM_DataPoint] getDataPoints()
        Returns the data points
        """
        ...
    
    @overload
    def setDataPoints(self, data: List[TM_DataPoint] ) -> None:
        """
        Cython signature: void setDataPoints(libcpp_vector[TM_DataPoint] & data)
        Sets the data points. Removes the model that was previously fitted to the data (if any)
        """
        ...
    
    @overload
    def setDataPoints(self, data: List[List[float, float]] ) -> None:
        """
        Cython signature: void setDataPoints(libcpp_vector[libcpp_pair[double,double]] & data)
        Sets the data points (backwards-compatible overload). Removes the model that was previously fitted to the data (if any)
        """
        ...
    
    def apply(self, in_0: float ) -> float:
        """
        Cython signature: double apply(double)
        Applies the transformation to `value`
        """
        ...
    
    @overload
    def fitModel(self, model_type: Union[bytes, str, String] , params: Param ) -> None:
        """
        Cython signature: void fitModel(String model_type, Param params)
        Fits a model to the data
        """
        ...
    
    @overload
    def fitModel(self, model_type: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void fitModel(String model_type)
        Fits a model to the data
        """
        ...
    
    def getModelType(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getModelType()
        Gets the type of the fitted model
        """
        ...
    
    def getModelParameters(self) -> Param:
        """
        Cython signature: Param getModelParameters()
        Returns the model parameters
        """
        ...
    
    def invert(self) -> None:
        """
        Cython signature: void invert()
        Computes an (approximate) inverse of the transformation
        """
        ...
    
    def getDeviations(self, diffs: List[float] , do_apply: bool , do_sort: bool ) -> None:
        """
        Cython signature: void getDeviations(libcpp_vector[double] & diffs, bool do_apply, bool do_sort)
        Get the deviations between the data pairs
        
        :param diffs: Output
        :param do_apply: Get deviations after applying the model?
        :param do_sort: Sort `diffs` before returning?
        """
        ...
    
    def getStatistics(self) -> TransformationStatistics:
        """
        Cython signature: TransformationStatistics getStatistics()
        """
        ...
    
    getModelTypes: __static_TransformationDescription_getModelTypes 


class TransformationStatistics:
    """
    Cython implementation of _TransformationStatistics

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS::TransformationDescription_1_1TransformationStatistics.html>`_
    """
    
    xmin: float
    
    xmax: float
    
    ymin: float
    
    ymax: float
    
    percentiles_before: Dict[int, float]
    
    percentiles_after: Dict[int, float]
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void TransformationStatistics()
        """
        ...
    
    @overload
    def __init__(self, in_0: TransformationStatistics ) -> None:
        """
        Cython signature: void TransformationStatistics(TransformationStatistics &)
        """
        ... 


class _Interfaces_BinaryDataArray:
    """
    Cython implementation of _BinaryDataArray

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS::Interfaces_1_1BinaryDataArray.html>`_
    """
    
    data: List[float]
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void _Interfaces_BinaryDataArray()
        """
        ...
    
    @overload
    def __init__(self, in_0: _Interfaces_BinaryDataArray ) -> None:
        """
        Cython signature: void _Interfaces_BinaryDataArray(_Interfaces_BinaryDataArray &)
        """
        ... 


class _Interfaces_Chromatogram:
    """
    Cython implementation of _Chromatogram

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS::Interfaces_1_1Chromatogram.html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void _Interfaces_Chromatogram()
        """
        ...
    
    @overload
    def __init__(self, in_0: _Interfaces_Chromatogram ) -> None:
        """
        Cython signature: void _Interfaces_Chromatogram(_Interfaces_Chromatogram &)
        """
        ... 


class _Interfaces_Spectrum:
    """
    Cython implementation of _Spectrum

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS::Interfaces_1_1Spectrum.html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void _Interfaces_Spectrum()
        """
        ...
    
    @overload
    def __init__(self, in_0: _Interfaces_Spectrum ) -> None:
        """
        Cython signature: void _Interfaces_Spectrum(_Interfaces_Spectrum &)
        """
        ... 


class __AcquisitionMode:
    None
    ACQMODENULL : int
    PULSECOUNTING : int
    ADC : int
    TDC : int
    TRANSIENTRECORDER : int
    SIZE_OF_ACQUISITIONMODE : int

    def getMapping(self) -> Dict[int, str]:
       ... 


class __Averagines:
    None
    C : int
    H : int
    N : int
    O : int
    S : int
    AVERAGINE_NUM : int

    def getMapping(self) -> Dict[int, str]:
       ... 


class DriftTimeUnit:
    None
    NONE : int
    MILLISECOND : int
    VSSC : int
    FAIMS_COMPENSATION_VOLTAGE : int
    SIZE_OF_DRIFTTIMEUNIT : int

    def getMapping(self) -> Dict[int, str]:
       ... 


class IMFormat:
    None
    NONE : int
    CONCATENATED : int
    MULTIPLE_SPECTRA : int
    MIXED : int
    SIZE_OF_IMFORMAT : int

    def getMapping(self) -> Dict[int, str]:
       ... 


class __PeptideSearchEngineFIAlgorithm_ExitCodes:
    None
    EXECUTION_OK : int
    INPUT_FILE_EMPTY : int
    UNEXPECTED_RESULT : int
    UNKNOWN_ERROR : int
    ILLEGAL_PARAMETERS : int

    def getMapping(self) -> Dict[int, str]:
       ... 


class __ProcessingAction:
    None
    DATA_PROCESSING : int
    CHARGE_DECONVOLUTION : int
    DEISOTOPING : int
    SMOOTHING : int
    CHARGE_CALCULATION : int
    PRECURSOR_RECALCULATION : int
    BASELINE_REDUCTION : int
    PEAK_PICKING : int
    ALIGNMENT : int
    CALIBRATION : int
    NORMALIZATION : int
    FILTERING : int
    QUANTITATION : int
    FEATURE_GROUPING : int
    IDENTIFICATION_MAPPING : int
    FORMAT_CONVERSION : int
    CONVERSION_MZDATA : int
    CONVERSION_MZML : int
    CONVERSION_MZXML : int
    CONVERSION_DTA : int
    IDENTIFICATION : int
    ION_MOBILITY_BINNING : int
    SIZE_OF_PROCESSINGACTION : int

    def getMapping(self) -> Dict[int, str]:
       ... 


class __ResidueType:
    None
    Full : int
    Internal : int
    NTerminal : int
    CTerminal : int
    AIon : int
    BIon : int
    CIon : int
    XIon : int
    YIon : int
    ZIon : int
    Precursor_ion : int
    BIonMinusH20 : int
    YIonMinusH20 : int
    BIonMinusNH3 : int
    YIonMinusNH3 : int
    NonIdentified : int
    Unannotated : int
    SizeOfResidueType : int

    def getMapping(self) -> Dict[int, str]:
       ... 


class __Type_IonDetector:
    None
    TYPENULL : int
    ELECTRONMULTIPLIER : int
    PHOTOMULTIPLIER : int
    FOCALPLANEARRAY : int
    FARADAYCUP : int
    CONVERSIONDYNODEELECTRONMULTIPLIER : int
    CONVERSIONDYNODEPHOTOMULTIPLIER : int
    MULTICOLLECTOR : int
    CHANNELELECTRONMULTIPLIER : int
    CHANNELTRON : int
    DALYDETECTOR : int
    MICROCHANNELPLATEDETECTOR : int
    ARRAYDETECTOR : int
    CONVERSIONDYNODE : int
    DYNODE : int
    FOCALPLANECOLLECTOR : int
    IONTOPHOTONDETECTOR : int
    POINTCOLLECTOR : int
    POSTACCELERATIONDETECTOR : int
    PHOTODIODEARRAYDETECTOR : int
    INDUCTIVEDETECTOR : int
    ELECTRONMULTIPLIERTUBE : int
    SIZE_OF_TYPE : int

    def getMapping(self) -> Dict[int, str]:
       ... 


class XRefType_CVTerm_ControlledVocabulary:
    None
    XSD_STRING : int
    XSD_INTEGER : int
    XSD_DECIMAL : int
    XSD_NEGATIVE_INTEGER : int
    XSD_POSITIVE_INTEGER : int
    XSD_NON_NEGATIVE_INTEGER : int
    XSD_NON_POSITIVE_INTEGER : int
    XSD_BOOLEAN : int
    XSD_DATE : int
    XSD_ANYURI : int
    NONE : int

    def getMapping(self) -> Dict[int, str]:
       ... 

