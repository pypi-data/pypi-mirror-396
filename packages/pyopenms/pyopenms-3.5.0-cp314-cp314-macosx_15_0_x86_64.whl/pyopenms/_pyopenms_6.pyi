from __future__ import annotations
from typing import overload, Any, List, Dict, Tuple, Set, Sequence, Union
from pyopenms import *  # pylint: disable=wildcard-import; lgtm(py/polluting-import)
import numpy as _np

from enum import IntEnum as _PyEnum


def __static_PercolatorInfile_store(pin_file: Union[bytes, str, String] , peptide_ids: PeptideIdentificationList , feature_set: List[bytes] , in_3: bytes , min_charge: int , max_charge: int ) -> None:
    """
    Cython signature: void store(String pin_file, PeptideIdentificationList peptide_ids, StringList feature_set, libcpp_string, int min_charge, int max_charge)
    """
    ...


class BilinearInterpolation:
    """
    Cython implementation of _BilinearInterpolation[double,double]

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS::Math_1_1BilinearInterpolation[double,double].html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void BilinearInterpolation()
        """
        ...
    
    @overload
    def __init__(self, in_0: BilinearInterpolation ) -> None:
        """
        Cython signature: void BilinearInterpolation(BilinearInterpolation &)
        """
        ...
    
    def value(self, arg_pos_0: float , arg_pos_1: float ) -> float:
        """
        Cython signature: double value(double arg_pos_0, double arg_pos_1)
        """
        ...
    
    def addValue(self, arg_pos_0: float , arg_pos_1: float , arg_value: float ) -> None:
        """
        Cython signature: void addValue(double arg_pos_0, double arg_pos_1, double arg_value)
        Performs bilinear resampling. The arg_value is split up and added to the data points around arg_pos. ("forward resampling")
        """
        ...
    
    def getData(self) -> MatrixDouble:
        """
        Cython signature: MatrixDouble getData()
        """
        ...
    
    def setData(self, data: MatrixDouble ) -> None:
        """
        Cython signature: void setData(MatrixDouble & data)
        Assigns data to the internal random access container storing the data. SourceContainer must be assignable to ContainerType
        """
        ...
    
    def empty(self) -> bool:
        """
        Cython signature: bool empty()
        """
        ...
    
    def key2index_0(self, pos: float ) -> float:
        """
        Cython signature: double key2index_0(double pos)
        The transformation from "outside" to "inside" coordinates
        """
        ...
    
    def index2key_0(self, pos: float ) -> float:
        """
        Cython signature: double index2key_0(double pos)
        The transformation from "inside" to "outside" coordinates
        """
        ...
    
    def key2index_1(self, pos: float ) -> float:
        """
        Cython signature: double key2index_1(double pos)
        The transformation from "outside" to "inside" coordinates
        """
        ...
    
    def index2key_1(self, pos: float ) -> float:
        """
        Cython signature: double index2key_1(double pos)
        The transformation from "inside" to "outside" coordinates
        """
        ...
    
    def getScale_0(self) -> float:
        """
        Cython signature: double getScale_0()
        """
        ...
    
    def setScale_0(self, scale: float ) -> None:
        """
        Cython signature: void setScale_0(double & scale)
        """
        ...
    
    def getScale_1(self) -> float:
        """
        Cython signature: double getScale_1()
        """
        ...
    
    def setScale_1(self, scale: float ) -> None:
        """
        Cython signature: void setScale_1(double & scale)
        """
        ...
    
    def getOffset_0(self) -> float:
        """
        Cython signature: double getOffset_0()
        Accessor. "Offset" is the point (in "outside" units) which corresponds to "Data(0,0)"
        """
        ...
    
    def setOffset_0(self, offset: float ) -> None:
        """
        Cython signature: void setOffset_0(double & offset)
        """
        ...
    
    def getOffset_1(self) -> float:
        """
        Cython signature: double getOffset_1()
        Accessor. "Offset" is the point (in "outside" units) which corresponds to "Data(0,0)"
        """
        ...
    
    def setOffset_1(self, offset: float ) -> None:
        """
        Cython signature: void setOffset_1(double & offset)
        """
        ...
    
    @overload
    def setMapping_0(self, scale: float , inside: float , outside: float ) -> None:
        """
        Cython signature: void setMapping_0(double & scale, double & inside, double & outside)
        """
        ...
    
    @overload
    def setMapping_0(self, inside_low: float , outside_low: float , inside_high: float , outside_high: float ) -> None:
        """
        Cython signature: void setMapping_0(double & inside_low, double & outside_low, double & inside_high, double & outside_high)
        """
        ...
    
    @overload
    def setMapping_1(self, scale: float , inside: float , outside: float ) -> None:
        """
        Cython signature: void setMapping_1(double & scale, double & inside, double & outside)
        """
        ...
    
    @overload
    def setMapping_1(self, inside_low: float , outside_low: float , inside_high: float , outside_high: float ) -> None:
        """
        Cython signature: void setMapping_1(double & inside_low, double & outside_low, double & inside_high, double & outside_high)
        """
        ...
    
    def getInsideReferencePoint_0(self) -> float:
        """
        Cython signature: double getInsideReferencePoint_0()
        """
        ...
    
    def getInsideReferencePoint_1(self) -> float:
        """
        Cython signature: double getInsideReferencePoint_1()
        """
        ...
    
    def getOutsideReferencePoint_0(self) -> float:
        """
        Cython signature: double getOutsideReferencePoint_0()
        """
        ...
    
    def getOutsideReferencePoint_1(self) -> float:
        """
        Cython signature: double getOutsideReferencePoint_1()
        """
        ...
    
    def supportMin_0(self) -> float:
        """
        Cython signature: double supportMin_0()
        Lower boundary of the support, in "outside" coordinates
        """
        ...
    
    def supportMin_1(self) -> float:
        """
        Cython signature: double supportMin_1()
        Lower boundary of the support, in "outside" coordinates
        """
        ...
    
    def supportMax_0(self) -> float:
        """
        Cython signature: double supportMax_0()
        Upper boundary of the support, in "outside" coordinates
        """
        ...
    
    def supportMax_1(self) -> float:
        """
        Cython signature: double supportMax_1()
        Upper boundary of the support, in "outside" coordinates
        """
        ... 


class Biosaur2Algorithm:
    """
    Cython implementation of _Biosaur2Algorithm

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1Biosaur2Algorithm.html>`_

    C++ implementation of the Biosaur2 feature detection workflow.
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void Biosaur2Algorithm()
        Instantiate the Biosaur2 feature finding algorithm
        """
        ...
    
    @overload
    def __init__(self, in_0: Biosaur2Algorithm ) -> None:
        """
        Cython signature: void Biosaur2Algorithm(Biosaur2Algorithm &)
        Copy constructor
        """
        ...
    
    def setMSData(self, ms_data: MSExperiment ) -> None:
        """
        Cython signature: void setMSData(const MSExperiment & ms_data)
        Set the MS data used for feature detection (copy version)
        """
        ...
    
    @overload
    def getMSData(self, ) -> MSExperiment:
        """
        Cython signature: MSExperiment & getMSData()
        Get non-const reference to MS data
        """
        ...
    
    @overload
    def getMSData(self, ) -> MSExperiment:
        """
        Cython signature: const MSExperiment & getMSData()
        Get const reference to MS data
        """
        ...
    
    def run(self, feature_map: FeatureMap ) -> None:
        """
        Cython signature: void run(FeatureMap & feature_map)
        Run the algorithm storing only the resulting features
        """
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


class ConsensusIDAlgorithmAverage:
    """
    Cython implementation of _ConsensusIDAlgorithmAverage

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1ConsensusIDAlgorithmAverage.html>`_
      -- Inherits from ['ConsensusIDAlgorithmIdentity']
    """
    
    def __init__(self) -> None:
        """
        Cython signature: void ConsensusIDAlgorithmAverage()
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


class ConsensusIDAlgorithmPEPIons:
    """
    Cython implementation of _ConsensusIDAlgorithmPEPIons

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1ConsensusIDAlgorithmPEPIons.html>`_
      -- Inherits from ['ConsensusIDAlgorithmSimilarity']
    """
    
    def __init__(self) -> None:
        """
        Cython signature: void ConsensusIDAlgorithmPEPIons()
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


class CrossLinkSpectrumMatch:
    """
    Cython implementation of _CrossLinkSpectrumMatch

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS::OPXLDataStructs_1_1CrossLinkSpectrumMatch.html>`_
    """
    
    cross_link: ProteinProteinCrossLink
    
    scan_index_light: int
    
    scan_index_heavy: int
    
    score: float
    
    rank: int
    
    xquest_score: float
    
    pre_score: float
    
    percTIC: float
    
    wTIC: float
    
    wTICold: float
    
    int_sum: float
    
    intsum_alpha: float
    
    intsum_beta: float
    
    total_current: float
    
    precursor_error_ppm: float
    
    match_odds: float
    
    match_odds_alpha: float
    
    match_odds_beta: float
    
    log_occupancy: float
    
    log_occupancy_alpha: float
    
    log_occupancy_beta: float
    
    xcorrx_max: float
    
    xcorrc_max: float
    
    matched_linear_alpha: int
    
    matched_linear_beta: int
    
    matched_xlink_alpha: int
    
    matched_xlink_beta: int
    
    num_iso_peaks_mean: float
    
    num_iso_peaks_mean_linear_alpha: float
    
    num_iso_peaks_mean_linear_beta: float
    
    num_iso_peaks_mean_xlinks_alpha: float
    
    num_iso_peaks_mean_xlinks_beta: float
    
    ppm_error_abs_sum_linear_alpha: float
    
    ppm_error_abs_sum_linear_beta: float
    
    ppm_error_abs_sum_xlinks_alpha: float
    
    ppm_error_abs_sum_xlinks_beta: float
    
    ppm_error_abs_sum_linear: float
    
    ppm_error_abs_sum_xlinks: float
    
    ppm_error_abs_sum_alpha: float
    
    ppm_error_abs_sum_beta: float
    
    ppm_error_abs_sum: float
    
    precursor_correction: int
    
    precursor_total_intensity: float
    
    precursor_target_intensity: float
    
    precursor_signal_proportion: float
    
    precursor_target_peak_count: int
    
    precursor_residual_peak_count: int
    
    frag_annotations: List[PeptideHit_PeakAnnotation]
    
    peptide_id_index: int
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void CrossLinkSpectrumMatch()
        """
        ...
    
    @overload
    def __init__(self, in_0: CrossLinkSpectrumMatch ) -> None:
        """
        Cython signature: void CrossLinkSpectrumMatch(CrossLinkSpectrumMatch &)
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


class DRange1:
    """
    Cython implementation of _DRange1

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1DRange1.html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void DRange1()
        """
        ...
    
    @overload
    def __init__(self, in_0: DRange1 ) -> None:
        """
        Cython signature: void DRange1(DRange1 &)
        """
        ...
    
    def united(self, other_range: DRange1 ) -> DRange1:
        """
        Cython signature: DRange1 united(DRange1 other_range)
        """
        ...
    
    def isIntersected(self, range_: DRange1 ) -> bool:
        """
        Cython signature: bool isIntersected(DRange1 & range_)
        """
        ...
    
    def isEmpty(self) -> bool:
        """
        Cython signature: bool isEmpty()
        """
        ...
    
    def __richcmp__(self, other: DRange1, op: int) -> Any:
        ... 


class DRange2:
    """
    Cython implementation of _DRange2

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1DRange2.html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void DRange2()
        """
        ...
    
    @overload
    def __init__(self, in_0: DRange2 ) -> None:
        """
        Cython signature: void DRange2(DRange2 &)
        """
        ...
    
    @overload
    def __init__(self, lower: Union[Sequence[int], Sequence[float]] , upper: Union[Sequence[int], Sequence[float]] ) -> None:
        """
        Cython signature: void DRange2(DPosition2 lower, DPosition2 upper)
        """
        ...
    
    @overload
    def __init__(self, minx: float , miny: float , maxx: float , maxy: float ) -> None:
        """
        Cython signature: void DRange2(double minx, double miny, double maxx, double maxy)
        """
        ...
    
    def united(self, other_range: DRange2 ) -> DRange2:
        """
        Cython signature: DRange2 united(DRange2 other_range)
        """
        ...
    
    def isIntersected(self, range_: DRange2 ) -> bool:
        """
        Cython signature: bool isIntersected(DRange2 & range_)
        """
        ...
    
    def isEmpty(self) -> bool:
        """
        Cython signature: bool isEmpty()
        """
        ...
    
    def __richcmp__(self, other: DRange2, op: int) -> Any:
        ... 


class DTA2DFile:
    """
    Cython implementation of _DTA2DFile

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1DTA2DFile.html>`_
      -- Inherits from ['ProgressLogger']
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void DTA2DFile()
        """
        ...
    
    @overload
    def __init__(self, in_0: DTA2DFile ) -> None:
        """
        Cython signature: void DTA2DFile(DTA2DFile &)
        """
        ...
    
    def storeTIC(self, filename: Union[bytes, str, String] , peakmap: MSExperiment ) -> None:
        """
        Cython signature: void storeTIC(String filename, MSExperiment & peakmap)
        """
        ...
    
    def store(self, filename: Union[bytes, str, String] , peakmap: MSExperiment ) -> None:
        """
        Cython signature: void store(String filename, MSExperiment & peakmap)
        """
        ...
    
    def load(self, filename: Union[bytes, str, String] , peakmap: MSExperiment ) -> None:
        """
        Cython signature: void load(String filename, MSExperiment & peakmap)
        """
        ...
    
    def getOptions(self) -> PeakFileOptions:
        """
        Cython signature: PeakFileOptions getOptions()
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


class Date:
    """
    Cython implementation of _Date

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1Date.html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void Date()
        """
        ...
    
    @overload
    def __init__(self, in_0: Date ) -> None:
        """
        Cython signature: void Date(Date &)
        """
        ...
    
    def set(self, date: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void set(const String & date)
        """
        ...
    
    def today(self) -> Date:
        """
        Cython signature: Date today()
        """
        ...
    
    def get(self) -> Union[bytes, str, String]:
        """
        Cython signature: String get()
        """
        ...
    
    def clear(self) -> None:
        """
        Cython signature: void clear()
        """
        ... 


class ElementDB:
    """
    Cython implementation of _ElementDB

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1ElementDB.html>`_
    """
    
    @overload
    def getElement(self, name: Union[bytes, str, String] ) -> Element:
        """
        Cython signature: const Element * getElement(const String & name)
        """
        ...
    
    @overload
    def getElement(self, atomic_number: int ) -> Element:
        """
        Cython signature: const Element * getElement(unsigned int atomic_number)
        """
        ...
    
    def addElement(self, name: bytes , symbol: bytes , an: int , abundance: Dict[int, float] , mass: Dict[int, float] , replace_existing: bool ) -> None:
        """
        Cython signature: void addElement(libcpp_string name, libcpp_string symbol, unsigned int an, libcpp_map[unsigned int,double] abundance, libcpp_map[unsigned int,double] mass, bool replace_existing)
        """
        ...
    
    @overload
    def hasElement(self, name: Union[bytes, str, String] ) -> bool:
        """
        Cython signature: bool hasElement(const String & name)
        Returns true if the db contains an element with the given name, else false
        """
        ...
    
    @overload
    def hasElement(self, atomic_number: int ) -> bool:
        """
        Cython signature: bool hasElement(unsigned int atomic_number)
        Returns true if the db contains an element with the given atomic_number, else false
        """
        ... 


class FeatureDeconvolution:
    """
    Cython implementation of _FeatureDeconvolution

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1FeatureDeconvolution.html>`_
      -- Inherits from ['DefaultParamHandler']
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void FeatureDeconvolution()
        """
        ...
    
    @overload
    def __init__(self, in_0: FeatureDeconvolution ) -> None:
        """
        Cython signature: void FeatureDeconvolution(FeatureDeconvolution &)
        """
        ...
    
    def compute(self, input: FeatureMap , output: FeatureMap , cmap1: ConsensusMap , cmap2: ConsensusMap ) -> None:
        """
        Cython signature: void compute(FeatureMap & input, FeatureMap & output, ConsensusMap & cmap1, ConsensusMap & cmap2)
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
    CHARGEMODE_FD : __CHARGEMODE_FD 


class FeatureFinderMultiplexAlgorithm:
    """
    Cython implementation of _FeatureFinderMultiplexAlgorithm

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1FeatureFinderMultiplexAlgorithm.html>`_
      -- Inherits from ['DefaultParamHandler']
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void FeatureFinderMultiplexAlgorithm()
        """
        ...
    
    @overload
    def __init__(self, in_0: FeatureFinderMultiplexAlgorithm ) -> None:
        """
        Cython signature: void FeatureFinderMultiplexAlgorithm(FeatureFinderMultiplexAlgorithm &)
        """
        ...
    
    def run(self, exp: MSExperiment , progress: bool ) -> None:
        """
        Cython signature: void run(MSExperiment & exp, bool progress)
        Main method for feature detection
        """
        ...
    
    def getFeatureMap(self) -> FeatureMap:
        """
        Cython signature: FeatureMap getFeatureMap()
        """
        ...
    
    def getConsensusMap(self) -> ConsensusMap:
        """
        Cython signature: ConsensusMap getConsensusMap()
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


class FileTypes:
    """
    Cython implementation of _FileTypes

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1FileTypes.html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void FileTypes()
        Centralizes the file types recognized by FileHandler
        """
        ...
    
    @overload
    def __init__(self, in_0: FileTypes ) -> None:
        """
        Cython signature: void FileTypes(FileTypes &)
        """
        ...
    
    def typeToName(self, t: int ) -> Union[bytes, str, String]:
        """
        Cython signature: String typeToName(FileType t)
        Returns the name/extension of the type
        """
        ...
    
    def typeToMZML(self, t: int ) -> Union[bytes, str, String]:
        """
        Cython signature: String typeToMZML(FileType t)
        Returns the mzML name
        """
        ...
    
    def nameToType(self, name: Union[bytes, str, String] ) -> int:
        """
        Cython signature: FileType nameToType(String name)
        Converts a file type name into a Type
        
        
        :param name: A case-insensitive name (e.g. FASTA or Fasta, etc.)
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


class IDMapper:
    """
    Cython implementation of _IDMapper

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1IDMapper.html>`_
      -- Inherits from ['DefaultParamHandler']
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void IDMapper()
        Annotates an MSExperiment, FeatureMap or ConsensusMap with peptide identifications
        """
        ...
    
    @overload
    def __init__(self, in_0: IDMapper ) -> None:
        """
        Cython signature: void IDMapper(IDMapper &)
        """
        ...
    
    @overload
    def annotate(self, map_: AnnotatedMSRun , ids: PeptideIdentificationList , protein_ids: List[ProteinIdentification] , clear_ids: bool , mapMS1: bool ) -> None:
        """
        Cython signature: void annotate(AnnotatedMSRun & map_, PeptideIdentificationList & ids, libcpp_vector[ProteinIdentification] & protein_ids, bool clear_ids, bool mapMS1)
        Mapping method for peak maps\n
        
        The identifications stored in a PeptideIdentification instance can be added to the
        corresponding spectrum
        Note that a PeptideIdentication is added to ALL spectra which are within the allowed RT and MZ boundaries
        
        
        :param map: AnnotatedMSRun to receive the identifications
        :param peptide_ids: PeptideIdentification for the MSExperiment
        :param protein_ids: ProteinIdentification for the MSExperiment
        :param clear_ids: Reset peptide and protein identifications of each scan before annotating
        :param map_ms1: Attach Ids to MS1 spectra using RT mapping only (without precursor, without m/z)
        :raises:
          Exception: MissingInformation is thrown if entries of 'peptide_ids' do not contain 'MZ' and 'RT' information
        """
        ...
    
    @overload
    def annotate(self, map_: AnnotatedMSRun , fmap: FeatureMap , clear_ids: bool , mapMS1: bool ) -> None:
        """
        Cython signature: void annotate(AnnotatedMSRun & map_, FeatureMap & fmap, bool clear_ids, bool mapMS1)
        Mapping method for peak maps\n
        
        Add peptide identifications stored in a feature map to their
        corresponding spectrum
        This function converts the feature map to a vector of peptide identifications (all peptide IDs from each feature are taken)
        and calls the respective annotate() function
        RT and m/z are taken from the peptides, or (if missing) from the feature itself
        
        
        :param map: AnnotatedMSRun to receive the identifications
        :param fmap: FeatureMap with PeptideIdentifications for the MSExperiment
        :param clear_ids: Reset peptide and protein identifications of each scan before annotating
        :param map_ms1: Attach Ids to MS1 spectra using RT mapping only (without precursor, without m/z)
        """
        ...
    
    @overload
    def annotate(self, map_: FeatureMap , ids: PeptideIdentificationList , protein_ids: List[ProteinIdentification] , use_centroid_rt: bool , use_centroid_mz: bool , spectra: MSExperiment ) -> None:
        """
        Cython signature: void annotate(FeatureMap & map_, PeptideIdentificationList & ids, libcpp_vector[ProteinIdentification] & protein_ids, bool use_centroid_rt, bool use_centroid_mz, MSExperiment & spectra)
        Mapping method for peak maps\n
        
        If all features have at least one convex hull, peptide positions are matched against the bounding boxes of the convex hulls by default. If not, the positions of the feature centroids are used. The respective coordinates of the centroids are also used for matching (in place of the corresponding ranges from the bounding boxes) if 'use_centroid_rt' or 'use_centroid_mz' are true\n
        
        In any case, tolerance in RT and m/z dimension is applied according to the global parameters 'rt_tolerance' and 'mz_tolerance'. Tolerance is understood as "plus or minus x", so the matching range is actually increased by twice the tolerance value\n
        
        If several features (incl. tolerance) overlap the position of a peptide identification, the identification is annotated to all of them
        
        
        :param map: MSExperiment to receive the identifications
        :param ids: PeptideIdentification for the MSExperiment
        :param protein_ids: ProteinIdentification for the MSExperiment
        :param use_centroid_rt: Whether to use the RT value of feature centroids even if convex hulls are present
        :param use_centroid_mz: Whether to use the m/z value of feature centroids even if convex hulls are present
        :param spectra: Whether precursors not contained in the identifications are annotated with an empty PeptideIdentification object containing the scan index
        :raises:
          Exception: MissingInformation is thrown if entries of 'ids' do not contain 'MZ' and 'RT' information
        """
        ...
    
    @overload
    def annotate(self, map_: ConsensusMap , ids: PeptideIdentificationList , protein_ids: List[ProteinIdentification] , measure_from_subelements: bool , annotate_ids_with_subelements: bool , spectra: MSExperiment ) -> None:
        """
        Cython signature: void annotate(ConsensusMap & map_, PeptideIdentificationList & ids, libcpp_vector[ProteinIdentification] & protein_ids, bool measure_from_subelements, bool annotate_ids_with_subelements, MSExperiment & spectra)
        Mapping method for peak maps\n
        
        If all features have at least one convex hull, peptide positions are matched against the bounding boxes of the convex hulls by default. If not, the positions of the feature centroids are used. The respective coordinates of the centroids are also used for matching (in place of the corresponding ranges from the bounding boxes) if 'use_centroid_rt' or 'use_centroid_mz' are true\n
        
        In any case, tolerance in RT and m/z dimension is applied according to the global parameters 'rt_tolerance' and 'mz_tolerance'. Tolerance is understood as "plus or minus x", so the matching range is actually increased by twice the tolerance value\n
        
        If several features (incl. tolerance) overlap the position of a peptide identification, the identification is annotated to all of them
        
        
        :param map: MSExperiment to receive the identifications
        :param ids: PeptideIdentification for the MSExperiment
        :param protein_ids: ProteinIdentification for the MSExperiment
        :param measure_from_subelements: Boolean operator set to true if distance estimate from FeatureHandles instead of Centroid
        :param annotate_ids_with_subelements: Boolean operator set to true if store map index of FeatureHandle in peptide identification
        :param spectra: Whether precursors not contained in the identifications are annotated with an empty PeptideIdentification object containing the scan index
        :raises:
          Exception: MissingInformation is thrown if entries of 'ids' do not contain 'MZ' and 'RT' information
        """
        ...
    
    @overload
    def annotate(self, map_: AnnotatedMSRun , ids: PeptideIdentificationList , protein_ids: List[ProteinIdentification] , clear_ids: bool , map_ms1: bool ) -> None:
        """
        Cython signature: void annotate(AnnotatedMSRun & map_, PeptideIdentificationList & ids, libcpp_vector[ProteinIdentification] & protein_ids, bool clear_ids, bool map_ms1)
        Mapping method using PeptideIdentificationList\n
        
        The identifications stored in a PeptideIdentificationList instance can be added to the
        corresponding spectrum
        
        
        :param map_: AnnotatedMSRun to receive the identifications
        :param ids: PeptideIdentificationList for the MSExperiment
        :param protein_ids: ProteinIdentification for the MSExperiment
        :param clear_ids: Reset peptide and protein identifications of each scan before annotating
        :param map_ms1: Attach Ids to MS1 spectra using RT mapping only (without precursor, without m/z)
        """
        ...
    
    @overload
    def annotate(self, map_: FeatureMap , ids: PeptideIdentificationList , protein_ids: List[ProteinIdentification] , use_centroid_rt: bool , use_centroid_mz: bool , spectra: MSExperiment ) -> None:
        """
        Cython signature: void annotate(FeatureMap & map_, PeptideIdentificationList & ids, libcpp_vector[ProteinIdentification] & protein_ids, bool use_centroid_rt, bool use_centroid_mz, MSExperiment & spectra)
        Mapping method using PeptideIdentificationList\n
        
        :param map_: FeatureMap to receive the identifications
        :param ids: PeptideIdentificationList for the FeatureMap
        :param protein_ids: ProteinIdentification for the FeatureMap
        :param use_centroid_rt: Whether to use the RT value of feature centroids even if convex hulls are present
        :param use_centroid_mz: Whether to use the m/z value of feature centroids even if convex hulls are present
        :param spectra: [Optional] Provide the underlying mass spectra, which allows adding an empty PeptideIdentification object containing the MS2 scan index to each Feature that covers an MS/MS spectrum (irrespective if it already has an ID).
        """
        ...
    
    @overload
    def annotate(self, map_: ConsensusMap , ids: PeptideIdentificationList , protein_ids: List[ProteinIdentification] , measure_from_subelements: bool , annotate_ids_with_subelements: bool , spectra: MSExperiment ) -> None:
        """
        Cython signature: void annotate(ConsensusMap & map_, PeptideIdentificationList & ids, libcpp_vector[ProteinIdentification] & protein_ids, bool measure_from_subelements, bool annotate_ids_with_subelements, MSExperiment & spectra)
        Mapping method using PeptideIdentificationList\n
        
        :param map_: ConsensusMap to receive the identifications
        :param ids: PeptideIdentificationList for the ConsensusMap
        :param protein_ids: ProteinIdentification for the ConsensusMap
        :param measure_from_subelements: Boolean operator set to true if distance estimate from FeatureHandles instead of Centroid
        :param annotate_ids_with_subelements: Boolean operator set to true if store map index of FeatureHandle in peptide identification
        :param spectra: [Optional] Provide the underlying mass spectra, which allows adding an empty PeptideIdentification object containing the MS2 scan index to each ConsensusFeature that covers an MS/MS spectrum (irrespective if it already has an ID).
        """
        ...
    
    @overload
    def mapPrecursorsToIdentifications(self, spectra: MSExperiment , ids: PeptideIdentificationList , mz_tol: float , rt_tol: float ) -> IDMapper_PeptideIdentificationListState:
        """
        Cython signature: IDMapper_PeptideIdentificationListState mapPrecursorsToIdentifications(MSExperiment spectra, PeptideIdentificationList & ids, double mz_tol, double rt_tol)
        Mapping of peptide identifications to spectra\n
        This helper function partitions all spectra into those that had:
        - no precursor (e.g. MS1 spectra),
        - at least one identified precursor,
        - or only unidentified precursor
        
        
        :param spectra: The mass spectra
        :param ids: The peptide identifications
        :param mz_tol: Tolerance used to map to precursor m/z
        :param rt_tol: Tolerance used to map to spectrum retention time
        :return: A struct of vectors holding spectra indices of the partitioning
        """
        ...
    
    @overload
    def mapPrecursorsToIdentifications(self, spectra: MSExperiment , ids: PeptideIdentificationList , mz_tol: float , rt_tol: float ) -> IDMapper_PeptideIdentificationListState:
        """
        Cython signature: IDMapper_PeptideIdentificationListState mapPrecursorsToIdentifications(MSExperiment spectra, PeptideIdentificationList & ids, double mz_tol, double rt_tol)
        Mapping of PeptideIdentificationList to spectra\n
        This helper function partitions all spectra into those that had:
        - no precursor (e.g. MS1 spectra),
        - at least one identified precursor,
        - or only unidentified precursor
        
        
        :param spectra: The mass spectra
        :param ids: The PeptideIdentificationList
        :param mz_tol: Tolerance used to map to precursor m/z
        :param rt_tol: Tolerance used to map to spectrum retention time
        :return: A struct of vectors holding spectra indices of the partitioning
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


class IDMapper_PeptideIdentificationListState:
    """
    Cython implementation of _IDMapper_PeptideIdentificationListState

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1IDMapper_PeptideIdentificationListState.html>`_
    """
    
    no_precursors: List[int]
    
    identified: List[int]
    
    unidentified: List[int]
    
    def __init__(self) -> None:
        """
        Cython signature: void IDMapper_PeptideIdentificationListState()
        """
        ... 


class IDRipper:
    """
    Cython implementation of _IDRipper

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS::IDRipper_1_1IDRipper.html>`_
      -- Inherits from ['DefaultParamHandler']
    """
    
    def __init__(self) -> None:
        """
        Cython signature: void IDRipper()
        Ripping protein/peptide identification according their file origin
        """
        ...
    
    def rip(self, rfis: List[RipFileIdentifier] , rfcs: List[RipFileContent] , proteins: List[ProteinIdentification] , peptides: PeptideIdentificationList , full_split: bool , split_ident_runs: bool ) -> None:
        """
        Cython signature: void rip(libcpp_vector[RipFileIdentifier] & rfis, libcpp_vector[RipFileContent] & rfcs, libcpp_vector[ProteinIdentification] & proteins, PeptideIdentificationList & peptides, bool full_split, bool split_ident_runs)
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


class IdXMLFile:
    """
    Cython implementation of _IdXMLFile

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1IdXMLFile.html>`_
    """
    
    def __init__(self) -> None:
        """
        Cython signature: void IdXMLFile()
        Used to load and store idXML files
        """
        ...
    
    @overload
    def load(self, filename: Union[bytes, str, String] , protein_ids: List[ProteinIdentification] , peptide_ids: PeptideIdentificationList ) -> None:
        """
        Cython signature: void load(String filename, libcpp_vector[ProteinIdentification] & protein_ids, PeptideIdentificationList & peptide_ids)
        Loads the identifications of an idXML file without identifier
        """
        ...
    
    @overload
    def load(self, filename: Union[bytes, str, String] , protein_ids: List[ProteinIdentification] , peptide_ids: PeptideIdentificationList ) -> None:
        """
        Cython signature: void load(String filename, libcpp_vector[ProteinIdentification] & protein_ids, PeptideIdentificationList & peptide_ids)
        Loads the identifications of an idXML file without identifier using PeptideIdentificationList
        """
        ...
    
    @overload
    def load(self, filename: Union[bytes, str, String] , protein_ids: List[ProteinIdentification] , peptide_ids: PeptideIdentificationList , document_id: String ) -> None:
        """
        Cython signature: void load(String filename, libcpp_vector[ProteinIdentification] & protein_ids, PeptideIdentificationList & peptide_ids, String & document_id)
        Loads the identifications of an idXML file with identifier using PeptideIdentificationList
        """
        ...
    
    @overload
    def store(self, filename: Union[bytes, str, String] , protein_ids: List[ProteinIdentification] , peptide_ids: PeptideIdentificationList , document_id: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void store(String filename, libcpp_vector[ProteinIdentification] & protein_ids, PeptideIdentificationList & peptide_ids, String document_id)
        Stores the data in an idXML file
        """
        ...
    
    @overload
    def store(self, filename: Union[bytes, str, String] , protein_ids: List[ProteinIdentification] , peptide_ids: PeptideIdentificationList ) -> None:
        """
        Cython signature: void store(String filename, libcpp_vector[ProteinIdentification] & protein_ids, PeptideIdentificationList & peptide_ids)
        """
        ...
    
    @overload
    def store(self, filename: Union[bytes, str, String] , protein_ids: List[ProteinIdentification] , peptide_ids: PeptideIdentificationList , document_id: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void store(String filename, libcpp_vector[ProteinIdentification] & protein_ids, PeptideIdentificationList & peptide_ids, String document_id)
        Stores the data in an idXML file using PeptideIdentificationList
        """
        ... 


class IdentificationRuns:
    """
    Cython implementation of _IdentificationRuns

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS::IDRipper_1_1IdentificationRuns.html>`_
    """
    
    def __init__(self, prot_ids: List[ProteinIdentification] ) -> None:
        """
        Cython signature: void IdentificationRuns(libcpp_vector[ProteinIdentification] & prot_ids)
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


class IntegerDataArray:
    """
    Cython implementation of _IntegerDataArray

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS::DataArrays_1_1IntegerDataArray.html>`_
      -- Inherits from ['MetaInfoDescription']

    The representation of extra integer data attached to a spectrum or chromatogram.
    Raw data access is proved by `get_peaks` and `set_peaks`, which yields numpy arrays
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void IntegerDataArray()
        """
        ...
    
    @overload
    def __init__(self, in_0: IntegerDataArray ) -> None:
        """
        Cython signature: void IntegerDataArray(IntegerDataArray &)
        """
        ...
    
    def size(self) -> int:
        """
        Cython signature: size_t size()
        """
        ...
    
    def resize(self, n: int ) -> None:
        """
        Cython signature: void resize(size_t n)
        """
        ...
    
    def reserve(self, n: int ) -> None:
        """
        Cython signature: void reserve(size_t n)
        """
        ...
    
    def clear(self) -> None:
        """
        Cython signature: void clear()
        """
        ...
    
    def push_back(self, in_0: int ) -> None:
        """
        Cython signature: void push_back(int)
        """
        ...
    
    def getName(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getName()
        Returns the name of the peak annotations
        """
        ...
    
    def setName(self, name: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setName(String name)
        Sets the name of the peak annotations
        """
        ...
    
    def getDataProcessing(self) -> List[DataProcessing]:
        """
        Cython signature: libcpp_vector[shared_ptr[DataProcessing]] getDataProcessing()
        Returns a reference to the description of the applied processing
        """
        ...
    
    def setDataProcessing(self, in_0: List[DataProcessing] ) -> None:
        """
        Cython signature: void setDataProcessing(libcpp_vector[shared_ptr[DataProcessing]])
        Sets the description of the applied processing
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
    
    def __richcmp__(self, other: IntegerDataArray, op: int) -> Any:
        ... 


class IsotopeFitter1D:
    """
    Cython implementation of _IsotopeFitter1D

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1IsotopeFitter1D.html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void IsotopeFitter1D()
        Isotope distribution fitter (1-dim.) approximated using linear interpolation
        """
        ...
    
    @overload
    def __init__(self, in_0: IsotopeFitter1D ) -> None:
        """
        Cython signature: void IsotopeFitter1D(IsotopeFitter1D &)
        """
        ... 


class LinearResampler:
    """
    Cython implementation of _LinearResampler

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1LinearResampler.html>`_
      -- Inherits from ['DefaultParamHandler', 'ProgressLogger']

    Annotates and filters transitions in a TargetedExperiment
    
    
    :param exp: The input, unfiltered transitions
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void LinearResampler()
        """
        ...
    
    @overload
    def __init__(self, in_0: LinearResampler ) -> None:
        """
        Cython signature: void LinearResampler(LinearResampler &)
        """
        ...
    
    def raster(self, input: MSSpectrum ) -> None:
        """
        Cython signature: void raster(MSSpectrum & input)
        Applies the resampling algorithm to an MSSpectrum
        """
        ...
    
    def rasterExperiment(self, input: MSExperiment ) -> None:
        """
        Cython signature: void rasterExperiment(MSExperiment & input)
        Resamples the data in an MSExperiment
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


class LowessSmoothing:
    """
    Cython implementation of _LowessSmoothing

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1LowessSmoothing.html>`_
      -- Inherits from ['DefaultParamHandler']
    """
    
    def __init__(self) -> None:
        """
        Cython signature: void LowessSmoothing()
        """
        ...
    
    def smoothData(self, x: List[float] , y: List[float] , y_smoothed: List[float] ) -> None:
        """
        Cython signature: void smoothData(libcpp_vector[double] x, libcpp_vector[double] y, libcpp_vector[double] & y_smoothed)
        Smoothing method that receives x and y coordinates (e.g., RT and intensities) and computes smoothed intensities
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


class MS2File:
    """
    Cython implementation of _MS2File

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1MS2File.html>`_
      -- Inherits from ['ProgressLogger']
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void MS2File()
        """
        ...
    
    @overload
    def __init__(self, in_0: MS2File ) -> None:
        """
        Cython signature: void MS2File(MS2File &)
        """
        ...
    
    def load(self, filename: Union[bytes, str, String] , exp: MSExperiment ) -> None:
        """
        Cython signature: void load(const String & filename, MSExperiment & exp)
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


class MSChromatogram:
    """
    Cython implementation of _MSChromatogram

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1MSChromatogram.html>`_
      -- Inherits from ['ChromatogramSettings', 'RangeManagerRtInt']

    The representation of a chromatogram.
    Raw data access is proved by `get_peaks` and `set_peaks`, which yields numpy arrays
    Iterations yields access to underlying peak objects but is slower
    Extra data arrays can be accessed through getFloatDataArrays / getIntegerDataArrays / getStringDataArrays
    See help(ChromatogramSettings) for information about meta-information
    
    Usage:
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void MSChromatogram()
        """
        ...
    
    @overload
    def __init__(self, in_0: MSChromatogram ) -> None:
        """
        Cython signature: void MSChromatogram(MSChromatogram &)
        """
        ...
    
    def getMZ(self) -> float:
        """
        Cython signature: double getMZ()
        Returns the mz of the product entry, makes sense especially for MRM scans
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
        Cython signature: void setName(String)
        Sets the name
        """
        ...
    
    def size(self) -> int:
        """
        Cython signature: size_t size()
        """
        ...
    
    def reserve(self, n: int ) -> None:
        """
        Cython signature: void reserve(size_t n)
        """
        ...
    
    def resize(self, n: int ) -> None:
        """
        Cython signature: void resize(size_t n)
        Resize the peak array
        """
        ...
    
    def __getitem__(self, in_0: int ) -> ChromatogramPeak:
        """
        Cython signature: ChromatogramPeak & operator[](size_t)
        """
        ...
    def __setitem__(self, key: int, value: ChromatogramPeak) -> None:
        """Cython signature: ChromatogramPeak & operator[](size_t)"""
        ...
    
    def updateRanges(self) -> None:
        """
        Cython signature: void updateRanges()
        """
        ...
    
    def clear(self, in_0: int ) -> None:
        """
        Cython signature: void clear(int)
        Clears all data and meta data
        
        
        :param clear_meta_data: If true, all meta data is cleared in addition to the data
        """
        ...
    
    def push_back(self, in_0: ChromatogramPeak ) -> None:
        """
        Cython signature: void push_back(ChromatogramPeak)
        Append a peak
        """
        ...
    
    def isSorted(self) -> bool:
        """
        Cython signature: bool isSorted()
        Checks if all peaks are sorted with respect to ascending RT
        """
        ...
    
    def sortByIntensity(self, reverse: bool ) -> None:
        """
        Cython signature: void sortByIntensity(bool reverse)
        Lexicographically sorts the peaks by their intensity
        
        
        Sorts the peaks according to ascending intensity. Meta data arrays will be sorted accordingly
        """
        ...
    
    def sortByPosition(self) -> None:
        """
        Cython signature: void sortByPosition()
        Lexicographically sorts the peaks by their position
        
        
        The chromatogram is sorted with respect to position. Meta data arrays will be sorted accordingly
        """
        ...
    
    def findNearest(self, in_0: float ) -> int:
        """
        Cython signature: int findNearest(double)
        Binary search for the peak nearest to a specific RT
        :note: Make sure the chromatogram is sorted with respect to RT! Otherwise the result is undefined
        
        
        :param rt: The searched for mass-to-charge ratio searched
        :return: Returns the index of the peak.
        :raises:
          Exception: Precondition is thrown if the chromatogram is empty (not only in debug mode)
        """
        ...
    
    def getFloatDataArrays(self) -> List[FloatDataArray]:
        """
        Cython signature: libcpp_vector[FloatDataArray] getFloatDataArrays()
        Returns a reference to the float meta data arrays
        """
        ...
    
    def getIntegerDataArrays(self) -> List[IntegerDataArray]:
        """
        Cython signature: libcpp_vector[IntegerDataArray] getIntegerDataArrays()
        Returns a reference to the integer meta data arrays
        """
        ...
    
    def getStringDataArrays(self) -> List[StringDataArray]:
        """
        Cython signature: libcpp_vector[StringDataArray] getStringDataArrays()
        Returns a reference to the string meta data arrays
        """
        ...
    
    def setFloatDataArrays(self, fda: List[FloatDataArray] ) -> None:
        """
        Cython signature: void setFloatDataArrays(libcpp_vector[FloatDataArray] fda)
        Sets the float meta data arrays
        """
        ...
    
    def setIntegerDataArrays(self, ida: List[IntegerDataArray] ) -> None:
        """
        Cython signature: void setIntegerDataArrays(libcpp_vector[IntegerDataArray] ida)
        Sets the integer meta data arrays
        """
        ...
    
    def setStringDataArrays(self, sda: List[StringDataArray] ) -> None:
        """
        Cython signature: void setStringDataArrays(libcpp_vector[StringDataArray] sda)
        Sets the string meta data arrays
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
    
    def getMinRT(self) -> float:
        """
        Cython signature: double getMinRT()
        Returns the minimum RT
        """
        ...
    
    def getMaxRT(self) -> float:
        """
        Cython signature: double getMaxRT()
        Returns the maximum RT
        """
        ...
    
    def getMinIntensity(self) -> float:
        """
        Cython signature: double getMinIntensity()
        Returns the minimum intensity
        """
        ...
    
    def getMaxIntensity(self) -> float:
        """
        Cython signature: double getMaxIntensity()
        Returns the maximum intensity
        """
        ...
    
    def clearRanges(self) -> None:
        """
        Cython signature: void clearRanges()
        Resets all range dimensions as empty
        """
        ...
    
    def __richcmp__(self, other: MSChromatogram, op: int) -> Any:
        ...
    
    def __iter__(self) -> ChromatogramPeak:
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


class MassDecomposition:
    """
    Cython implementation of _MassDecomposition

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1MassDecomposition.html>`_

    Class represents a decomposition of a mass into amino acids
    
    This class represents a mass decomposition into amino acids. A
    decomposition are amino acids given with frequencies which add
    up to a specific mass.
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void MassDecomposition()
        """
        ...
    
    @overload
    def __init__(self, in_0: MassDecomposition ) -> None:
        """
        Cython signature: void MassDecomposition(MassDecomposition &)
        """
        ...
    
    @overload
    def __init__(self, deco: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void MassDecomposition(const String & deco)
        """
        ...
    
    def toString(self) -> Union[bytes, str, String]:
        """
        Cython signature: String toString()
        Returns the decomposition as a string
        """
        ...
    
    def toExpandedString(self) -> Union[bytes, str, String]:
        """
        Cython signature: String toExpandedString()
        Returns the decomposition as a string; instead of frequencies the amino acids are repeated
        """
        ...
    
    def getNumberOfMaxAA(self) -> int:
        """
        Cython signature: size_t getNumberOfMaxAA()
        Returns the max frequency of this composition
        """
        ...
    
    def containsTag(self, tag: Union[bytes, str, String] ) -> bool:
        """
        Cython signature: bool containsTag(const String & tag)
        Returns true if tag is contained in the mass decomposition
        """
        ...
    
    def compatible(self, deco: MassDecomposition ) -> bool:
        """
        Cython signature: bool compatible(MassDecomposition & deco)
        Returns true if the mass decomposition if contained in this instance
        """
        ...
    
    def __str__(self) -> Union[bytes, str, String]:
        """
        Cython signature: String toString()
        Returns the decomposition as a string
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


class MsInspectFile:
    """
    Cython implementation of _MsInspectFile

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1MsInspectFile.html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void MsInspectFile()
        """
        ...
    
    @overload
    def __init__(self, in_0: MsInspectFile ) -> None:
        """
        Cython signature: void MsInspectFile(MsInspectFile &)
        """
        ...
    
    def load(self, filename: Union[bytes, str, String] , feature_map: FeatureMap ) -> None:
        """
        Cython signature: void load(const String & filename, FeatureMap & feature_map)
        Loads a MsInspect file into a featureXML
        
        The content of the file is stored in `features`
        :raises:
          Exception: FileNotFound is thrown if the file could not be opened
        :raises:
          Exception: ParseError is thrown if an error occurs during parsing
        """
        ...
    
    def store(self, filename: Union[bytes, str, String] , spectrum: MSSpectrum ) -> None:
        """
        Cython signature: void store(const String & filename, MSSpectrum & spectrum)
        Stores a featureXML as a MsInspect file
        """
        ... 


class OMSSAXMLFile:
    """
    Cython implementation of _OMSSAXMLFile

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1OMSSAXMLFile.html>`_
      -- Inherits from ['XMLFile']

    Used to load OMSSAXML files
    
    This class is used to load documents that implement
    the schema of OMSSAXML files
    """
    
    def __init__(self) -> None:
        """
        Cython signature: void OMSSAXMLFile()
        """
        ...
    
    def load(self, filename: Union[bytes, str, String] , protein_identification: ProteinIdentification , id_data: PeptideIdentificationList , load_proteins: bool , load_empty_hits: bool ) -> None:
        """
        Cython signature: void load(const String & filename, ProteinIdentification & protein_identification, PeptideIdentificationList & id_data, bool load_proteins, bool load_empty_hits)
        Loads data from a OMSSAXML file
        
        
        :param filename: The file to be loaded
        :param protein_identification: Protein identifications belonging to the whole experiment
        :param id_data: The identifications with m/z and RT
        :param load_proteins: If this flag is set to false, the protein identifications are not loaded
        :param load_empty_hits: Many spectra will not return a hit. Report empty peptide identifications?
        """
        ...
    
    def setModificationDefinitionsSet(self, rhs: ModificationDefinitionsSet ) -> None:
        """
        Cython signature: void setModificationDefinitionsSet(ModificationDefinitionsSet rhs)
        Sets the valid modifications
        """
        ...
    
    def getVersion(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getVersion()
        Return the version of the schema
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


class ParamXMLFile:
    """
    Cython implementation of _ParamXMLFile

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1ParamXMLFile.html>`_

    The file pendant of the Param class used to load and store the param
    datastructure as paramXML
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void ParamXMLFile()
        """
        ...
    
    @overload
    def __init__(self, in_0: ParamXMLFile ) -> None:
        """
        Cython signature: void ParamXMLFile(ParamXMLFile &)
        """
        ...
    
    def load(self, filename: Union[bytes, str, String] , param: Param ) -> None:
        """
        Cython signature: void load(String filename, Param & param)
        Read XML file
        
        
        :param filename: The file from where to read the Param object
        :param param: The param object where the read data should be stored
        :raises:
          Exception: FileNotFound is thrown if the file could not be found
        :raises:
          Exception: ParseError is thrown if an error occurs during parsing
        """
        ...
    
    def store(self, filename: Union[bytes, str, String] , param: Param ) -> None:
        """
        Cython signature: void store(String filename, Param & param)
        Write XML file
        
        
        :param filename: The filename where the param data structure should be stored
        :param param: The Param class that should be stored in the file
        """
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


class PercolatorInfile:
    """
    Cython implementation of _PercolatorInfile

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1PercolatorInfile.html>`_

    Class for storing Percolator tab-delimited input files
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void PercolatorInfile()
        """
        ...
    
    @overload
    def __init__(self, in_0: PercolatorInfile ) -> None:
        """
        Cython signature: void PercolatorInfile(PercolatorInfile &)
        """
        ...
    
    store: __static_PercolatorInfile_store 


class Precursor:
    """
    Cython implementation of _Precursor

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1Precursor.html>`_
      -- Inherits from ['Peak1D', 'CVTermList']

    Precursor meta information
    
    This class contains precursor information:
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void Precursor()
        """
        ...
    
    @overload
    def __init__(self, in_0: Precursor ) -> None:
        """
        Cython signature: void Precursor(Precursor &)
        """
        ...
    
    def getActivationMethods(self) -> Set[_PyActivationMethod]:
        """
        Cython signature: libcpp_set[ActivationMethod] getActivationMethods()
        Returns the activation methods
        """
        ...
    
    def getActivationMethodsAsString(self) -> List[bytes]:
        """
        Cython signature: libcpp_vector[String] getActivationMethodsAsString()
        Returns the full names (e.g., "Collision-induced dissociation") of the activation methods set on this instance
        """
        ...
    
    def getActivationMethodsAsShortString(self) -> List[bytes]:
        """
        Cython signature: libcpp_vector[String] getActivationMethodsAsShortString()
        Returns the abbreviations (e.g., "CID") of the activation methods set on this instance
        """
        ...
    
    def setActivationMethods(self, activation_methods: Set[_PyActivationMethod] ) -> None:
        """
        Cython signature: void setActivationMethods(libcpp_set[ActivationMethod] activation_methods)
        Sets the activation methods
        """
        ...
    
    @staticmethod
    def getAllNamesOfActivationMethods() -> List[bytes]:
        """
        Cython signature: libcpp_vector[String] getAllNamesOfActivationMethods()
        Returns the full names (e.g., "Collision-induced dissociation") of ALL possible activation methods, not just those set on this instance
        """
        ...
    
    @staticmethod
    def getAllShortNamesOfActivationMethods() -> List[bytes]:
        """
        Cython signature: libcpp_vector[String] getAllShortNamesOfActivationMethods()
        Returns the abbreviations (e.g., "CID") of ALL possible activation methods, not just those set on this instance
        """
        ...
    
    def getActivationEnergy(self) -> float:
        """
        Cython signature: double getActivationEnergy()
        Returns the activation energy (in electronvolt)
        """
        ...
    
    def setActivationEnergy(self, activation_energy: float ) -> None:
        """
        Cython signature: void setActivationEnergy(double activation_energy)
        Sets the activation energy (in electronvolt)
        """
        ...
    
    def getIsolationWindowLowerOffset(self) -> float:
        """
        Cython signature: double getIsolationWindowLowerOffset()
        Returns the lower offset from the target m/z
        """
        ...
    
    def setIsolationWindowLowerOffset(self, bound: float ) -> None:
        """
        Cython signature: void setIsolationWindowLowerOffset(double bound)
        Sets the lower offset from the target m/z
        """
        ...
    
    def getDriftTime(self) -> float:
        """
        Cython signature: double getDriftTime()
        Returns the ion mobility drift time in milliseconds (-1 means it is not set)
        """
        ...
    
    def setDriftTime(self, drift_time: float ) -> None:
        """
        Cython signature: void setDriftTime(double drift_time)
        Sets the ion mobility drift time in milliseconds
        """
        ...
    
    def getIsolationWindowUpperOffset(self) -> float:
        """
        Cython signature: double getIsolationWindowUpperOffset()
        Returns the upper offset from the target m/z
        """
        ...
    
    def setIsolationWindowUpperOffset(self, bound: float ) -> None:
        """
        Cython signature: void setIsolationWindowUpperOffset(double bound)
        Sets the upper offset from the target m/z
        """
        ...
    
    def getDriftTimeWindowLowerOffset(self) -> float:
        """
        Cython signature: double getDriftTimeWindowLowerOffset()
        Returns the lower offset from the target ion mobility in milliseconds
        """
        ...
    
    def setDriftTimeWindowLowerOffset(self, drift_time: float ) -> None:
        """
        Cython signature: void setDriftTimeWindowLowerOffset(double drift_time)
        Sets the lower offset from the target ion mobility
        """
        ...
    
    def getDriftTimeWindowUpperOffset(self) -> float:
        """
        Cython signature: double getDriftTimeWindowUpperOffset()
        Returns the upper offset from the target ion mobility in milliseconds
        """
        ...
    
    def setDriftTimeWindowUpperOffset(self, drift_time: float ) -> None:
        """
        Cython signature: void setDriftTimeWindowUpperOffset(double drift_time)
        Sets the upper offset from the target ion mobility
        """
        ...
    
    def getCharge(self) -> int:
        """
        Cython signature: int getCharge()
        Returns the charge
        """
        ...
    
    def setCharge(self, charge: int ) -> None:
        """
        Cython signature: void setCharge(int charge)
        Sets the charge
        """
        ...
    
    def getPossibleChargeStates(self) -> List[int]:
        """
        Cython signature: libcpp_vector[int] getPossibleChargeStates()
        Returns the possible charge states
        """
        ...
    
    def setPossibleChargeStates(self, possible_charge_states: List[int] ) -> None:
        """
        Cython signature: void setPossibleChargeStates(libcpp_vector[int] possible_charge_states)
        Sets the possible charge states
        """
        ...
    
    def getUnchargedMass(self) -> float:
        """
        Cython signature: double getUnchargedMass()
        Returns the uncharged mass of the precursor, if charge is unknown, i.e. 0 best guess is its doubly charged
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
    
    def setCVTerms(self, terms: List[CVTerm] ) -> None:
        """
        Cython signature: void setCVTerms(const libcpp_vector[CVTerm] & terms)
        Sets the CV terms
        """
        ...
    
    def replaceCVTerm(self, term: CVTerm ) -> None:
        """
        Cython signature: void replaceCVTerm(CVTerm & term)
        Replaces the specified CV term
        """
        ...
    
    def replaceCVTerms(self, cv_terms: List[CVTerm] , accession: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void replaceCVTerms(libcpp_vector[CVTerm] cv_terms, String accession)
        """
        ...
    
    def consumeCVTerms(self, cv_term_map: Dict[bytes,List[CVTerm]] ) -> None:
        """
        Cython signature: void consumeCVTerms(libcpp_map[String,libcpp_vector[CVTerm]] cv_term_map)
        Merges the given map into the member map, no duplicate checking
        """
        ...
    
    def getCVTerms(self) -> Dict[bytes,List[CVTerm]]:
        """
        Cython signature: libcpp_map[String,libcpp_vector[CVTerm]] getCVTerms()
        Returns the accession string of the term
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
        Cython signature: bool hasCVTerm(String accession)
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
    
    def __richcmp__(self, other: Precursor, op: int) -> Any:
        ...
    ActivationMethod : _PyActivationMethod 


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


class RansacModelQuadratic:
    """
    Cython implementation of _RansacModelQuadratic

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS::Math_1_1RansacModelQuadratic.html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void RansacModelQuadratic()
        """
        ...
    
    @overload
    def __init__(self, in_0: RansacModelQuadratic ) -> None:
        """
        Cython signature: void RansacModelQuadratic(RansacModelQuadratic &)
        """
        ... 


class RipFileContent:
    """
    Cython implementation of _RipFileContent

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS::IDRipper_1_1RipFileContent.html>`_
    """
    
    def __init__(self, prot_idents: List[ProteinIdentification] , pep_idents: PeptideIdentificationList ) -> None:
        """
        Cython signature: void RipFileContent(libcpp_vector[ProteinIdentification] & prot_idents, PeptideIdentificationList & pep_idents)
        """
        ...
    
    def getProteinIdentifications(self) -> List[ProteinIdentification]:
        """
        Cython signature: libcpp_vector[ProteinIdentification] getProteinIdentifications()
        """
        ...
    
    def getPeptideIdentifications(self) -> PeptideIdentificationList:
        """
        Cython signature: PeptideIdentificationList getPeptideIdentifications()
        """
        ... 


class RipFileIdentifier:
    """
    Cython implementation of _RipFileIdentifier

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS::IDRipper_1_1RipFileIdentifier.html>`_
    """
    
    def __init__(self, id_runs: IdentificationRuns , pep_id: PeptideIdentification , file_origin_map: Dict[Union[bytes, str, String], int] , origin_annotation_fmt: int , split_ident_runs: bool ) -> None:
        """
        Cython signature: void RipFileIdentifier(IdentificationRuns & id_runs, PeptideIdentification & pep_id, libcpp_map[String,unsigned int] & file_origin_map, OriginAnnotationFormat origin_annotation_fmt, bool split_ident_runs)
        """
        ...
    
    def getIdentRunIdx(self) -> int:
        """
        Cython signature: unsigned int getIdentRunIdx()
        """
        ...
    
    def getFileOriginIdx(self) -> int:
        """
        Cython signature: unsigned int getFileOriginIdx()
        """
        ...
    
    def getOriginFullname(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getOriginFullname()
        """
        ...
    
    def getOutputBasename(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getOutputBasename()
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


class SiriusFragmentAnnotation:
    """
    Cython implementation of _SiriusFragmentAnnotation

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1SiriusFragmentAnnotation.html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void SiriusFragmentAnnotation()
        """
        ...
    
    @overload
    def __init__(self, in_0: SiriusFragmentAnnotation ) -> None:
        """
        Cython signature: void SiriusFragmentAnnotation(SiriusFragmentAnnotation &)
        """
        ...
    
    def extractAnnotationsFromSiriusFile(self, path_to_sirius_workspace: String , max_rank: int , decoy: bool , use_exact_mass: bool ) -> List[MSSpectrum]:
        """
        Cython signature: libcpp_vector[MSSpectrum] extractAnnotationsFromSiriusFile(String & path_to_sirius_workspace, size_t max_rank, bool decoy, bool use_exact_mass)
        """
        ...
    
    def extractAndResolveSiriusAnnotations(self, sirius_workspace_subdirs: List[bytes] , score_threshold: float , use_exact_mass: bool , decoy_generation: bool ) -> List[SiriusFragmentAnnotation_SiriusTargetDecoySpectra]:
        """
        Cython signature: libcpp_vector[SiriusFragmentAnnotation_SiriusTargetDecoySpectra] extractAndResolveSiriusAnnotations(libcpp_vector[String] & sirius_workspace_subdirs, double score_threshold, bool use_exact_mass, bool decoy_generation)
        """
        ...
    
    def extract_columnname_to_columnindex(self, csvfile: CsvFile ) -> Dict[bytes, int]:
        """
        Cython signature: libcpp_map[libcpp_string,size_t] extract_columnname_to_columnindex(CsvFile & csvfile)
        """
        ... 


class SiriusFragmentAnnotation_SiriusTargetDecoySpectra:
    """
    Cython implementation of _SiriusFragmentAnnotation_SiriusTargetDecoySpectra

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1SiriusFragmentAnnotation_SiriusTargetDecoySpectra.html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void SiriusFragmentAnnotation_SiriusTargetDecoySpectra()
        """
        ...
    
    @overload
    def __init__(self, in_0: SiriusFragmentAnnotation_SiriusTargetDecoySpectra ) -> None:
        """
        Cython signature: void SiriusFragmentAnnotation_SiriusTargetDecoySpectra(SiriusFragmentAnnotation_SiriusTargetDecoySpectra &)
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


class TM_DataPoint:
    """
    Cython implementation of _TM_DataPoint

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1TM_DataPoint.html>`_
    """
    
    first: float
    
    second: float
    
    note: Union[bytes, str, String]
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void TM_DataPoint()
        """
        ...
    
    @overload
    def __init__(self, in_0: float , in_1: float ) -> None:
        """
        Cython signature: void TM_DataPoint(double, double)
        """
        ...
    
    @overload
    def __init__(self, in_0: float , in_1: float , in_2: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void TM_DataPoint(double, double, const String &)
        """
        ...
    
    def __richcmp__(self, other: TM_DataPoint, op: int) -> Any:
        ... 


class TSE_Match:
    """
    Cython implementation of _TSE_Match

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1TSE_Match.html>`_
    """
    
    spectrum: MSSpectrum
    
    score: float
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void TSE_Match()
        """
        ...
    
    @overload
    def __init__(self, in_0: TSE_Match ) -> None:
        """
        Cython signature: void TSE_Match(TSE_Match &)
        """
        ...
    
    @overload
    def __init__(self, spectrum: MSSpectrum , score: float ) -> None:
        """
        Cython signature: void TSE_Match(MSSpectrum & spectrum, double score)
        """
        ... 


class TargetedSpectraExtractor:
    """
    Cython implementation of _TargetedSpectraExtractor

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1TargetedSpectraExtractor.html>`_
      -- Inherits from ['DefaultParamHandler']
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void TargetedSpectraExtractor()
        """
        ...
    
    @overload
    def __init__(self, in_0: TargetedSpectraExtractor ) -> None:
        """
        Cython signature: void TargetedSpectraExtractor(TargetedSpectraExtractor &)
        """
        ...
    
    def getDefaultParameters(self, in_0: Param ) -> None:
        """
        Cython signature: void getDefaultParameters(Param &)
        """
        ...
    
    @overload
    def annotateSpectra(self, in_0: List[MSSpectrum] , in_1: TargetedExperiment , in_2: List[MSSpectrum] , in_3: FeatureMap ) -> None:
        """
        Cython signature: void annotateSpectra(libcpp_vector[MSSpectrum] &, TargetedExperiment &, libcpp_vector[MSSpectrum] &, FeatureMap &)
        """
        ...
    
    @overload
    def annotateSpectra(self, in_0: List[MSSpectrum] , in_1: TargetedExperiment , in_2: List[MSSpectrum] ) -> None:
        """
        Cython signature: void annotateSpectra(libcpp_vector[MSSpectrum] &, TargetedExperiment &, libcpp_vector[MSSpectrum] &)
        """
        ...
    
    @overload
    def annotateSpectra(self, in_0: List[MSSpectrum] , in_1: FeatureMap , in_2: FeatureMap , in_3: List[MSSpectrum] ) -> None:
        """
        Cython signature: void annotateSpectra(libcpp_vector[MSSpectrum] &, FeatureMap &, FeatureMap &, libcpp_vector[MSSpectrum] &)
        """
        ...
    
    def searchSpectrum(self, in_0: FeatureMap , in_1: FeatureMap , in_2: bool ) -> None:
        """
        Cython signature: void searchSpectrum(FeatureMap &, FeatureMap &, bool)
        """
        ...
    
    def pickSpectrum(self, in_0: MSSpectrum , in_1: MSSpectrum ) -> None:
        """
        Cython signature: void pickSpectrum(MSSpectrum &, MSSpectrum &)
        """
        ...
    
    @overload
    def scoreSpectra(self, in_0: List[MSSpectrum] , in_1: List[MSSpectrum] , in_2: FeatureMap , in_3: List[MSSpectrum] ) -> None:
        """
        Cython signature: void scoreSpectra(libcpp_vector[MSSpectrum] &, libcpp_vector[MSSpectrum] &, FeatureMap &, libcpp_vector[MSSpectrum] &)
        """
        ...
    
    @overload
    def scoreSpectra(self, in_0: List[MSSpectrum] , in_1: List[MSSpectrum] , in_2: List[MSSpectrum] ) -> None:
        """
        Cython signature: void scoreSpectra(libcpp_vector[MSSpectrum] &, libcpp_vector[MSSpectrum] &, libcpp_vector[MSSpectrum] &)
        """
        ...
    
    @overload
    def selectSpectra(self, in_0: List[MSSpectrum] , in_1: FeatureMap , in_2: List[MSSpectrum] , in_3: FeatureMap ) -> None:
        """
        Cython signature: void selectSpectra(libcpp_vector[MSSpectrum] &, FeatureMap &, libcpp_vector[MSSpectrum] &, FeatureMap &)
        """
        ...
    
    @overload
    def selectSpectra(self, in_0: List[MSSpectrum] , in_1: List[MSSpectrum] ) -> None:
        """
        Cython signature: void selectSpectra(libcpp_vector[MSSpectrum] &, libcpp_vector[MSSpectrum] &)
        """
        ...
    
    @overload
    def extractSpectra(self, in_0: MSExperiment , in_1: TargetedExperiment , in_2: List[MSSpectrum] , in_3: FeatureMap , in_4: bool ) -> None:
        """
        Cython signature: void extractSpectra(MSExperiment &, TargetedExperiment &, libcpp_vector[MSSpectrum] &, FeatureMap &, bool)
        """
        ...
    
    @overload
    def extractSpectra(self, in_0: MSExperiment , in_1: TargetedExperiment , in_2: List[MSSpectrum] ) -> None:
        """
        Cython signature: void extractSpectra(MSExperiment &, TargetedExperiment &, libcpp_vector[MSSpectrum] &)
        """
        ...
    
    @overload
    def extractSpectra(self, in_0: MSExperiment , in_1: FeatureMap , in_2: List[MSSpectrum] ) -> None:
        """
        Cython signature: void extractSpectra(MSExperiment &, FeatureMap &, libcpp_vector[MSSpectrum] &)
        """
        ...
    
    def constructTransitionsList(self, in_0: FeatureMap , in_1: FeatureMap , in_2: TargetedExperiment ) -> None:
        """
        Cython signature: void constructTransitionsList(FeatureMap &, FeatureMap &, TargetedExperiment &)
        """
        ...
    
    def storeSpectraMSP(self, in_0: Union[bytes, str, String] , in_1: MSExperiment ) -> None:
        """
        Cython signature: void storeSpectraMSP(const String &, MSExperiment &)
        """
        ...
    
    def mergeFeatures(self, in_0: FeatureMap , in_1: FeatureMap ) -> None:
        """
        Cython signature: void mergeFeatures(FeatureMap &, FeatureMap &)
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


class TransformationXMLFile:
    """
    Cython implementation of _TransformationXMLFile

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1TransformationXMLFile.html>`_
    """
    
    def __init__(self) -> None:
        """
        Cython signature: void TransformationXMLFile()
        """
        ...
    
    def load(self, in_0: Union[bytes, str, String] , in_1: TransformationDescription , fit_model: bool ) -> None:
        """
        Cython signature: void load(String, TransformationDescription &, bool fit_model)
        """
        ...
    
    def store(self, in_0: Union[bytes, str, String] , in_1: TransformationDescription ) -> None:
        """
        Cython signature: void store(String, TransformationDescription)
        """
        ... 


class UniqueIdGenerator:
    """
    Cython implementation of _UniqueIdGenerator

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1UniqueIdGenerator.html>`_
    """
    
    def getUniqueId(self) -> int:
        """
        Cython signature: uint64_t getUniqueId()
        """
        ...
    
    def setSeed(self, in_0: int ) -> None:
        """
        Cython signature: void setSeed(uint64_t)
        """
        ...
    
    def getSeed(self) -> int:
        """
        Cython signature: uint64_t getSeed()
        """
        ... 


class XFDRAlgorithm:
    """
    Cython implementation of _XFDRAlgorithm

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1XFDRAlgorithm.html>`_
      -- Inherits from ['DefaultParamHandler']
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void XFDRAlgorithm()
        """
        ...
    
    @overload
    def __init__(self, in_0: XFDRAlgorithm ) -> None:
        """
        Cython signature: void XFDRAlgorithm(XFDRAlgorithm &)
        """
        ...
    
    def run(self, peptide_ids: PeptideIdentificationList , protein_id: ProteinIdentification ) -> int:
        """
        Cython signature: XFDRAlgorithm_ExitCodes run(PeptideIdentificationList & peptide_ids, ProteinIdentification & protein_id)
        """
        ...
    
    def validateClassArguments(self) -> int:
        """
        Cython signature: XFDRAlgorithm_ExitCodes validateClassArguments()
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
    XFDRAlgorithm_ExitCodes : __XFDRAlgorithm_ExitCodes 


class XQuestResultXMLFile:
    """
    Cython implementation of _XQuestResultXMLFile

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1XQuestResultXMLFile.html>`_
      -- Inherits from ['XMLFile']
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void XQuestResultXMLFile()
        """
        ...
    
    @overload
    def __init__(self, in_0: XQuestResultXMLFile ) -> None:
        """
        Cython signature: void XQuestResultXMLFile(XQuestResultXMLFile &)
        """
        ...
    
    def load(self, filename: Union[bytes, str, String] , pep_ids: PeptideIdentificationList , prot_ids: List[ProteinIdentification] ) -> None:
        """
        Cython signature: void load(const String & filename, PeptideIdentificationList & pep_ids, libcpp_vector[ProteinIdentification] & prot_ids)
        Load the content of the xquest.xml file into the provided data structures
        
        :param filename: Filename of the file which is to be loaded
        :param pep_ids: Where the spectra with identifications of the input file will be loaded to
        :param prot_ids: Where the protein identification of the input file will be loaded to
        """
        ...
    
    def store(self, filename: Union[bytes, str, String] , poid: List[ProteinIdentification] , peid: PeptideIdentificationList ) -> None:
        """
        Cython signature: void store(const String & filename, libcpp_vector[ProteinIdentification] & poid, PeptideIdentificationList & peid)
        Stores the identifications in a xQuest XML file
        """
        ...
    
    def getNumberOfHits(self) -> int:
        """
        Cython signature: int getNumberOfHits()
        Returns the total number of hits in the file
        """
        ...
    
    def getMinScore(self) -> float:
        """
        Cython signature: double getMinScore()
        Returns minimum score among the hits in the file
        """
        ...
    
    def getMaxScore(self) -> float:
        """
        Cython signature: double getMaxScore()
        Returns maximum score among the hits in the file
        """
        ...
    
    @overload
    def writeXQuestXMLSpec(self, out_file: Union[bytes, str, String] , base_name: Union[bytes, str, String] , preprocessed_pair_spectra: OPXL_PreprocessedPairSpectra , spectrum_pairs: List[List[int, int]] , all_top_csms: List[List[CrossLinkSpectrumMatch]] , spectra: MSExperiment , test_mode: bool ) -> None:
        """
        Cython signature: void writeXQuestXMLSpec(const String & out_file, const String & base_name, OPXL_PreprocessedPairSpectra preprocessed_pair_spectra, libcpp_vector[libcpp_pair[size_t,size_t]] spectrum_pairs, libcpp_vector[libcpp_vector[CrossLinkSpectrumMatch]] all_top_csms, MSExperiment spectra, const bool & test_mode)
        Writes spec.xml output containing matching peaks between heavy and light spectra after comparing and filtering
        
        :param out_file: Path and filename for the output file
        :param base_name: The base_name should be the name of the input spectra file without the file ending. Used as part of an identifier string for the spectra
        :param preprocessed_pair_spectra: The preprocessed spectra after comparing and filtering
        :param spectrum_pairs: Indices of spectrum pairs in the input map
        :param all_top_csms: CrossLinkSpectrumMatches, from which the IDs were generated. Only spectra with matches are written out
        :param spectra: The spectra, that were searched as a PeakMap. The indices in spectrum_pairs correspond to spectra in this map
        """
        ...
    
    @overload
    def writeXQuestXMLSpec(self, out_file: Union[bytes, str, String] , base_name: Union[bytes, str, String] , all_top_csms: List[List[CrossLinkSpectrumMatch]] , spectra: MSExperiment , test_mode: bool ) -> None:
        """
        Cython signature: void writeXQuestXMLSpec(const String & out_file, const String & base_name, libcpp_vector[libcpp_vector[CrossLinkSpectrumMatch]] all_top_csms, MSExperiment spectra, const bool & test_mode)
        Writes spec.xml output containing spectra for visualization. This version of the function is meant to be used for label-free linkers
        
        :param out_file: Path and filename for the output file
        :param base_name: The base_name should be the name of the input spectra file without the file ending. Used as part of an identifier string for the spectra
        :param all_top_csms: CrossLinkSpectrumMatches, from which the IDs were generated. Only spectra with matches are written out
        :param spectra: The spectra, that were searched as a PeakMap
        """
        ...
    
    def getVersion(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getVersion()
        Return the version of the schema
        """
        ... 


class XTandemXMLFile:
    """
    Cython implementation of _XTandemXMLFile

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1XTandemXMLFile.html>`_
    """
    
    def __init__(self) -> None:
        """
        Cython signature: void XTandemXMLFile()
        """
        ...
    
    def load(self, filename: Union[bytes, str, String] , protein_identification: ProteinIdentification , id_data: PeptideIdentificationList , mod_def_set: ModificationDefinitionsSet ) -> None:
        """
        Cython signature: void load(String filename, ProteinIdentification & protein_identification, PeptideIdentificationList & id_data, ModificationDefinitionsSet & mod_def_set)
        """
        ... 


class _PyActivationMethod(_PyEnum):
    """
        Enum for activation/fragmentation methods of mass spectra
    
    - CID: Collision-induced dissociation (MS:1000133) (also CAD; parent term, but unless otherwise stated often used as synonym for trap-type CID)
    - PSD: Post-source decay
    - PD: Plasma desorption
    - SID: Surface-induced dissociation
    - BIRD: Blackbody infrared radiative dissociation
    - ECD: Electron capture dissociation (MS:1000250)
    - IMD: Infrared multiphoton dissociation
    - SORI: Sustained off-resonance irradiation
    - HCID: High-energy collision-induced dissociation
    - LCID: Low-energy collision-induced dissociation
    - PHD: Photodissociation
    - ETD: Electron transfer dissociation
    - ETciD: Electron transfer and collision-induced dissociation (MS:1003182)
    - EThcD: Electron transfer and higher-energy collision dissociation (MS:1002631)
    - PQD: Pulsed q dissociation (MS:1000599)
    - TRAP: trap-type collision-induced dissociation (MS:1002472)
    - HCD: beam-type collision-induced dissociation (MS:1000422)
    - INSOURCE: in-source collision-induced dissociation (MS:1001880)
    - LIFT: Bruker proprietary method (MS:1002000)
    """
    CID : int
    PSD : int
    PD : int
    SID : int
    BIRD : int
    ECD : int
    IMD : int
    SORI : int
    HCID : int
    LCID : int
    PHD : int
    ETD : int
    ETciD : int
    EThcD : int
    PQD : int
    TRAP : int
    HCD : int
    INSOURCE : int
    LIFT : int
    SIZE_OF_ACTIVATIONMETHOD : int 


class __CHARGEMODE_FD:
    None
    QFROMFEATURE : int
    QHEURISTIC : int
    QALL : int

    def getMapping(self) -> Dict[int, str]:
       ... 


class __CombinationsLogic:
    None
    OR : int
    AND : int
    XOR : int

    def getMapping(self) -> Dict[int, str]:
       ... 


class DRangeIntersection:
    None
    Disjoint : int
    Intersects : int
    Inside : int

    def getMapping(self) -> Dict[int, str]:
       ... 


class FileType:
    None
    UNKNOWN : int
    DTA : int
    DTA2D : int
    MZDATA : int
    MZXML : int
    FEATUREXML : int
    IDXML : int
    CONSENSUSXML : int
    MGF : int
    INI : int
    TOPPAS : int
    TRANSFORMATIONXML : int
    MZML : int
    CACHEDMZML : int
    MS2 : int
    PEPXML : int
    PROTXML : int
    MZIDENTML : int
    QCML : int
    GELML : int
    TRAML : int
    MSP : int
    OMSSAXML : int
    MASCOTXML : int
    PNG : int
    XMASS : int
    TSV : int
    PEPLIST : int
    HARDKLOER : int
    KROENIK : int
    FASTA : int
    EDTA : int
    CSV : int
    TXT : int
    OBO : int
    HTML : int
    XML : int
    ANALYSISXML : int
    XSD : int
    PSQ : int
    MRM : int
    SQMASS : int
    PQP : int
    OSW : int
    PSMS : int
    PARAMXML : int
    SIZE_OF_TYPE : int

    def getMapping(self) -> Dict[int, str]:
       ... 


class Measure:
    None
    MEASURE_PPM : int
    MEASURE_DA : int

    def getMapping(self) -> Dict[int, str]:
       ... 


class OriginAnnotationFormat:
    None
    FILE_ORIGIN : int
    MAP_INDEX : int
    ID_MERGE_INDEX : int
    UNKNOWN_OAF : int
    SIZE_OF_ORIGIN_ANNOTATION_FORMAT : int

    def getMapping(self) -> Dict[int, str]:
       ... 


class __PeakMassType:
    None
    MONOISOTOPIC : int
    AVERAGE : int
    SIZE_OF_PEAKMASSTYPE : int

    def getMapping(self) -> Dict[int, str]:
       ... 


class __RequirementLevel:
    None
    MUST : int
    SHOULD : int
    MAY : int

    def getMapping(self) -> Dict[int, str]:
       ... 


class __XFDRAlgorithm_ExitCodes:
    None
    EXECUTION_OK : int
    ILLEGAL_PARAMETERS : int
    UNEXPECTED_RESULT : int

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

