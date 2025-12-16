from __future__ import annotations
from typing import overload, Any, List, Dict, Tuple, Set, Sequence, Union
from pyopenms import *  # pylint: disable=wildcard-import; lgtm(py/polluting-import)
import numpy as _np

from enum import IntEnum as _PyEnum


def __static_IonIdentityMolecularNetworking_annotateConsensusMap(consensus_map: ConsensusMap ) -> None:
    """
    Cython signature: void annotateConsensusMap(ConsensusMap & consensus_map)
        Annotate ConsensusMap for ion identity molecular networking (IIMN) workflow by GNPS.
        
        Adds meta values Constants::UserParams::IIMN_ROW_ID (unique index for each feature), Constants::UserParams::IIMN_ADDUCT_PARTNERS (related features row IDs)
        and Constants::UserParams::IIMN_ANNOTATION_NETWORK_NUMBER (all related features with different adduct states) get the same network number).
        This method requires the features annotated with the Constants::UserParams::IIMN_LINKED_GROUPS meta value.
        If at least one of the features has an annotation for Constants::UserParam::IIMN_LINKED_GROUPS, annotate ConsensusMap for IIMN.
        
        
        :param consensus_map: Input ConsensusMap without IIMN annotations.
    """
    ...

def __static_NASequence_fromString(s: Union[bytes, str, String] ) -> NASequence:
    """
    Cython signature: NASequence fromString(const String & s)
    """
    ...

def __static_TransformationModelBSpline_getDefaultParameters(params: Param ) -> None:
    """
    Cython signature: void getDefaultParameters(Param & params)
    """
    ...

def __static_DateTime_now() -> DateTime:
    """
    Cython signature: DateTime now()
    """
    ...

def __static_IonIdentityMolecularNetworking_writeSupplementaryPairTable(consensus_map: ConsensusMap , output_file: Union[bytes, str, String] ) -> None:
    """
    Cython signature: void writeSupplementaryPairTable(const ConsensusMap & consensus_map, const String & output_file)
        Write supplementary pair table (csv file) from a ConsensusMap with edge annotations for connected features. Required for GNPS IIMN.
        
        The table contains the columns "ID 1" (row ID of first feature), "ID 2" (row ID of second feature), "EdgeType" (MS1/2 annotation),
        "Score" (the number of direct partners from both connected features) and "Annotation" (adducts and delta m/z between two connected features).
        
        
        :param consensus_map: Input ConsensusMap annotated with IonIdentityMolecularNetworking.annotateConsensusMap.
        :param output_file: Output file path for the supplementary pair table.
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


class ChromatogramExtractorAlgorithm:
    """
    Cython implementation of _ChromatogramExtractorAlgorithm

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1ChromatogramExtractorAlgorithm.html>`_
      -- Inherits from ['ProgressLogger']
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void ChromatogramExtractorAlgorithm()
        """
        ...
    
    @overload
    def __init__(self, in_0: ChromatogramExtractorAlgorithm ) -> None:
        """
        Cython signature: void ChromatogramExtractorAlgorithm(ChromatogramExtractorAlgorithm &)
        """
        ...
    
    def extractChromatograms(self, input: SpectrumAccessOpenMS , output: List[OSChromatogram] , extraction_coordinates: List[ExtractionCoordinates] , mz_extraction_window: float , ppm: bool , im_extraction_window: float , filter: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void extractChromatograms(shared_ptr[SpectrumAccessOpenMS] input, libcpp_vector[shared_ptr[OSChromatogram]] & output, libcpp_vector[ExtractionCoordinates] extraction_coordinates, double mz_extraction_window, bool ppm, double im_extraction_window, String filter)
          Extract chromatograms at the m/z and RT defined by the ExtractionCoordinates
        
        
        :param input: Input spectral map
        :param output: Output chromatograms (XICs)
        :param extraction_coordinates: Extracts around these coordinates (from
         rt_start to rt_end in seconds - extracts the whole chromatogram if
         rt_end - rt_start < 0).
        :param mz_extraction_window: Extracts a window of this size in m/z
          dimension in Th or ppm (e.g. a window of 50 ppm means an extraction of
          25 ppm on either side)
        :param ppm: Whether mz_extraction_window is in ppm or in Th
        :param filter: Which function to apply in m/z space (currently "tophat" only)
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


class Element:
    """
    Cython implementation of _Element

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1Element.html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void Element()
        """
        ...
    
    @overload
    def __init__(self, in_0: Element ) -> None:
        """
        Cython signature: void Element(Element &)
        """
        ...
    
    @overload
    def __init__(self, name: Union[bytes, str, String] , symbol: Union[bytes, str, String] , atomic_number: int , average_weight: float , mono_weight: float , isotopes: IsotopeDistribution ) -> None:
        """
        Cython signature: void Element(String name, String symbol, unsigned int atomic_number, double average_weight, double mono_weight, IsotopeDistribution isotopes)
        """
        ...
    
    def setAtomicNumber(self, atomic_number: int ) -> None:
        """
        Cython signature: void setAtomicNumber(unsigned int atomic_number)
        Sets unique atomic number
        """
        ...
    
    def getAtomicNumber(self) -> int:
        """
        Cython signature: unsigned int getAtomicNumber()
        Returns the unique atomic number
        """
        ...
    
    def setAverageWeight(self, weight: float ) -> None:
        """
        Cython signature: void setAverageWeight(double weight)
        Sets the average weight of the element
        """
        ...
    
    def getAverageWeight(self) -> float:
        """
        Cython signature: double getAverageWeight()
        Returns the average weight of the element
        """
        ...
    
    def setMonoWeight(self, weight: float ) -> None:
        """
        Cython signature: void setMonoWeight(double weight)
        Sets the mono isotopic weight of the element
        """
        ...
    
    def getMonoWeight(self) -> float:
        """
        Cython signature: double getMonoWeight()
        Returns the mono isotopic weight of the element
        """
        ...
    
    def setIsotopeDistribution(self, isotopes: IsotopeDistribution ) -> None:
        """
        Cython signature: void setIsotopeDistribution(IsotopeDistribution isotopes)
        Sets the isotope distribution of the element
        """
        ...
    
    def getIsotopeDistribution(self) -> IsotopeDistribution:
        """
        Cython signature: IsotopeDistribution getIsotopeDistribution()
        Returns the isotope distribution of the element
        """
        ...
    
    def setName(self, name: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setName(String name)
        Sets the name of the element
        """
        ...
    
    def getName(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getName()
        Returns the name of the element
        """
        ...
    
    def setSymbol(self, symbol: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setSymbol(String symbol)
        Sets symbol of the element
        """
        ...
    
    def getSymbol(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getSymbol()
        Returns symbol of the element
        """
        ... 


class EmpiricalFormula:
    """
    Cython implementation of _EmpiricalFormula

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1EmpiricalFormula.html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void EmpiricalFormula()
        Representation of an empirical formula
        """
        ...
    
    @overload
    def __init__(self, in_0: EmpiricalFormula ) -> None:
        """
        Cython signature: void EmpiricalFormula(EmpiricalFormula &)
        """
        ...
    
    @overload
    def __init__(self, in_0: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void EmpiricalFormula(String)
        EmpiricalFormula Constructor from string
        """
        ...
    
    @overload
    def __init__(self, number: int , element: Element , charge: int ) -> None:
        """
        Cython signature: void EmpiricalFormula(ptrdiff_t number, Element * element, ptrdiff_t charge)
        EmpiricalFormula Constructor with element pointer and number
        """
        ...
    
    def getMonoWeight(self) -> float:
        """
        Cython signature: double getMonoWeight()
        Returns the mono isotopic weight of the formula (includes proton charges)
        """
        ...
    
    def getAverageWeight(self) -> float:
        """
        Cython signature: double getAverageWeight()
        Returns the average weight of the formula (includes proton charges)
        """
        ...
    
    def estimateFromWeightAndComp(self, average_weight: float , C: float , H: float , N: float , O: float , S: float , P: float ) -> bool:
        """
        Cython signature: bool estimateFromWeightAndComp(double average_weight, double C, double H, double N, double O, double S, double P)
        Fills this EmpiricalFormula with an approximate elemental composition for a given average weight and approximate elemental stoichiometry
        """
        ...
    
    def estimateFromWeightAndCompAndS(self, average_weight: float , S: int , C: float , H: float , N: float , O: float , P: float ) -> bool:
        """
        Cython signature: bool estimateFromWeightAndCompAndS(double average_weight, unsigned int S, double C, double H, double N, double O, double P)
        Fills this EmpiricalFormula with an approximate elemental composition for a given average weight, exact number of sulfurs, and approximate elemental stoichiometry
        """
        ...
    
    @overload
    def getIsotopeDistribution(self, in_0: CoarseIsotopePatternGenerator ) -> IsotopeDistribution:
        """
        Cython signature: IsotopeDistribution getIsotopeDistribution(CoarseIsotopePatternGenerator)
        Computes the isotope distribution of an empirical formula using the CoarseIsotopePatternGenerator or the FineIsotopePatternGenerator method
        """
        ...
    
    @overload
    def getIsotopeDistribution(self, in_0: FineIsotopePatternGenerator ) -> IsotopeDistribution:
        """
        Cython signature: IsotopeDistribution getIsotopeDistribution(FineIsotopePatternGenerator)
        """
        ...
    
    def getConditionalFragmentIsotopeDist(self, precursor: EmpiricalFormula , precursor_isotopes: Set[int] , method: CoarseIsotopePatternGenerator ) -> IsotopeDistribution:
        """
        Cython signature: IsotopeDistribution getConditionalFragmentIsotopeDist(EmpiricalFormula & precursor, libcpp_set[unsigned int] & precursor_isotopes, CoarseIsotopePatternGenerator method)
        """
        ...
    
    def getNumberOfAtoms(self) -> int:
        """
        Cython signature: size_t getNumberOfAtoms()
        Returns the total number of atoms
        """
        ...
    
    def getCharge(self) -> int:
        """
        Cython signature: ptrdiff_t getCharge()
        Returns the total charge
        """
        ...
    
    def setCharge(self, charge: int ) -> None:
        """
        Cython signature: void setCharge(ptrdiff_t charge)
        Sets the charge
        """
        ...
    
    def toString(self) -> Union[bytes, str, String]:
        """
        Cython signature: String toString()
        Returns the formula as a string (charges are not included)
        """
        ...
    
    def getElementalComposition(self) -> Dict[bytes, int]:
        """
        Cython signature: libcpp_map[libcpp_string,int] getElementalComposition()
        Get elemental composition as a hash {'Symbol' -> NrAtoms}
        """
        ...
    
    def isEmpty(self) -> bool:
        """
        Cython signature: bool isEmpty()
        Returns true if the formula does not contain a element
        """
        ...
    
    def isCharged(self) -> bool:
        """
        Cython signature: bool isCharged()
        Returns true if charge is not equal to zero
        """
        ...
    
    def hasElement(self, element: Element ) -> bool:
        """
        Cython signature: bool hasElement(Element * element)
        Returns true if the formula contains the element
        """
        ...
    
    def contains(self, ef: EmpiricalFormula ) -> bool:
        """
        Cython signature: bool contains(EmpiricalFormula ef)
        Returns true if all elements from `ef` ( empirical formula ) are LESS abundant (negative allowed) than the corresponding elements of this EmpiricalFormula
        """
        ...
    
    def __add__(self: EmpiricalFormula, other: EmpiricalFormula) -> EmpiricalFormula:
        ...
    
    def __sub__(self: EmpiricalFormula, other: EmpiricalFormula) -> EmpiricalFormula:
        ...
    
    def __iadd__(self: EmpiricalFormula, other: EmpiricalFormula) -> EmpiricalFormula:
        ...
    
    def __isub__(self: EmpiricalFormula, other: EmpiricalFormula) -> EmpiricalFormula:
        ...
    
    def calculateTheoreticalIsotopesNumber(self) -> float:
        """
        Cython signature: double calculateTheoreticalIsotopesNumber()
        """
        ...
    
    def __str__(self) -> Union[bytes, str, String]:
        """
        Cython signature: String toString()
        Returns the formula as a string (charges are not included)
        """
        ...
    
    def __richcmp__(self, other: EmpiricalFormula, op: int) -> Any:
        ... 


class ExtractionCoordinates:
    """
    Cython implementation of _ExtractionCoordinates

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1ExtractionCoordinates.html>`_
    """
    
    mz: float
    
    mz_precursor: float
    
    rt_start: float
    
    rt_end: float
    
    ion_mobility: float
    
    id: bytes
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void ExtractionCoordinates()
        """
        ...
    
    @overload
    def __init__(self, in_0: ExtractionCoordinates ) -> None:
        """
        Cython signature: void ExtractionCoordinates(ExtractionCoordinates)
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


class FeatureMap:
    """
    Cython implementation of _FeatureMap

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1FeatureMap.html>`_
      -- Inherits from ['UniqueIdInterface', 'DocumentIdentifier', 'RangeManagerRtMzInt', 'MetaInfoInterface']

    A container for LC-MS features with metadata and identification information
    
    FeatureMap is one of the core data structures in OpenMS for storing detected features
    from LC-MS experiments. A feature represents a detected chemical entity (peptide, protein,
    metabolite, etc.) with its elution profile and mass information.
    
    Key capabilities:
    
    - Store and manage Feature objects (detected analytes)
    - Associate protein and peptide identifications with features
    - Sort features by various criteria (RT, m/z, intensity, quality)
    - Store experimental metadata and data processing information
    - Support direct iteration and indexing in Python
    
    Example usage:
    
    .. code-block:: python
    
       feature_map = oms.FeatureMap()
       # Add a feature
       feature = oms.Feature()
       feature.setRT(1234.5)
       feature.setMZ(445.678)
       feature.setIntensity(100000.0)
       feature_map.push_back(feature)
       # Access features
       print(f"Number of features: {feature_map.size()}")
       first_feature = feature_map[0]
       # Sort by RT
       feature_map.sortByRT()
       # Iterate over features
       for feat in feature_map:
           print(f"RT: {feat.getRT()}, m/z: {feat.getMZ()}")
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void FeatureMap()
        """
        ...
    
    @overload
    def __init__(self, in_0: FeatureMap ) -> None:
        """
        Cython signature: void FeatureMap(FeatureMap &)
        """
        ...
    
    def size(self) -> int:
        """
        Cython signature: int size()
        Returns the number of features in the map
        
        :return: Number of features stored in this container
        """
        ...
    
    def __getitem__(self, in_0: int ) -> Feature:
        """
        Cython signature: Feature & operator[](size_t)
        """
        ...
    def __setitem__(self, key: int, value: Feature) -> None:
        """Cython signature: Feature & operator[](size_t)"""
        ...
    
    @overload
    def push_back(self, spec: Feature ) -> None:
        """
        Cython signature: void push_back(Feature spec)
        Adds a Feature to the map
        
        :param spec: The feature to add to the map
        """
        ...
    
    @overload
    def push_back(self, spec: MRMFeature ) -> None:
        """
        Cython signature: void push_back(MRMFeature spec)
        Adds an MRMFeature to the map
        
        :param spec: The MRM feature to add to the map
        """
        ...
    
    @overload
    def sortByIntensity(self, ) -> None:
        """
        Cython signature: void sortByIntensity()
        Sorts features by ascending intensity
        
        After sorting, features can be accessed in order from lowest to highest intensity
        """
        ...
    
    @overload
    def sortByIntensity(self, reverse: bool ) -> None:
        """
        Cython signature: void sortByIntensity(bool reverse)
        Sorts features by intensity with optional reverse order
        
        :param reverse: If True, sorts in descending order (highest to lowest intensity)
        """
        ...
    
    def sortByPosition(self) -> None:
        """
        Cython signature: void sortByPosition()
        Sorts features by position using lexicographical comparison
        
        Compares RT first, then m/z for features with the same RT
        """
        ...
    
    def sortByRT(self) -> None:
        """
        Cython signature: void sortByRT()
        Sorts features by retention time (RT) in ascending order
        
        This is useful for time-based analysis or visualization
        """
        ...
    
    def sortByMZ(self) -> None:
        """
        Cython signature: void sortByMZ()
        Sorts features by mass-to-charge ratio (m/z) in ascending order
        
        Useful for mass-based grouping or analysis
        """
        ...
    
    def sortByOverallQuality(self) -> None:
        """
        Cython signature: void sortByOverallQuality()
        Sorts features by overall quality score in ascending order
        
        Higher quality scores indicate better feature detection confidence
        """
        ...
    
    def swap(self, in_0: FeatureMap ) -> None:
        """
        Cython signature: void swap(FeatureMap &)
        """
        ...
    
    def swapFeaturesOnly(self, swapfrom: FeatureMap ) -> None:
        """
        Cython signature: void swapFeaturesOnly(FeatureMap swapfrom)
        Swaps the feature content (plus its range information) of this map
        """
        ...
    
    @overload
    def clear(self, ) -> None:
        """
        Cython signature: void clear()
        Clears all feature data and metadata
        
        After calling this, the map will be empty (size() returns 0)
        """
        ...
    
    @overload
    def clear(self, clear_meta_data: bool ) -> None:
        """
        Cython signature: void clear(bool clear_meta_data)
        Clears feature data and optionally metadata
        
        :param clear_meta_data: If True, also clears all metadata; if False, keeps metadata
        """
        ...
    
    def __add__(self: FeatureMap, other: FeatureMap) -> FeatureMap:
        ...
    
    def __iadd__(self: FeatureMap, other: FeatureMap) -> FeatureMap:
        ...
    
    def updateRanges(self) -> None:
        """
        Cython signature: void updateRanges()
        """
        ...
    
    def getProteinIdentifications(self) -> List[ProteinIdentification]:
        """
        Cython signature: libcpp_vector[ProteinIdentification] getProteinIdentifications()
        Returns the protein identification runs stored in this map
        
        :return: Protein identification data from database searches
        
        Protein identifications contain metadata about search parameters and protein hits
        """
        ...
    
    def setProteinIdentifications(self, in_0: List[ProteinIdentification] ) -> None:
        """
        Cython signature: void setProteinIdentifications(libcpp_vector[ProteinIdentification])
        Sets the protein identifications for this map
        
        :param protein_ids: Protein identification results to associate with this map
        """
        ...
    
    def getUnassignedPeptideIdentifications(self) -> PeptideIdentificationList:
        """
        Cython signature: PeptideIdentificationList getUnassignedPeptideIdentifications()
        Returns peptide identifications that are not assigned to any feature
        
        :return: Unassigned peptide identification results
        
        These are peptide IDs that could not be matched to features, possibly due to feature detection issues or filtering
        """
        ...
    
    def setUnassignedPeptideIdentifications(self, in_0: PeptideIdentificationList ) -> None:
        """
        Cython signature: void setUnassignedPeptideIdentifications(PeptideIdentificationList)
        Sets the unassigned peptide identifications
        
        :param peptide_ids: Peptide IDs not assigned to features
        """
        ...
    
    def getDataProcessing(self) -> List[DataProcessing]:
        """
        Cython signature: libcpp_vector[DataProcessing] getDataProcessing()
        """
        ...
    
    def setDataProcessing(self, in_0: List[DataProcessing] ) -> None:
        """
        Cython signature: void setDataProcessing(libcpp_vector[DataProcessing])
        Sets the description of the applied data processing
        """
        ...
    
    @overload
    def setPrimaryMSRunPath(self, s: List[bytes] ) -> None:
        """
        Cython signature: void setPrimaryMSRunPath(StringList & s)
        Sets the file path to the primary MS run (usually the mzML file obtained after data conversion from raw files)
        """
        ...
    
    @overload
    def setPrimaryMSRunPath(self, s: List[bytes] , e: MSExperiment ) -> None:
        """
        Cython signature: void setPrimaryMSRunPath(StringList & s, MSExperiment & e)
        Sets the file path to the primary MS run using the mzML annotated in the MSExperiment argument `e`
        """
        ...
    
    def getPrimaryMSRunPath(self, toFill: List[bytes] ) -> None:
        """
        Cython signature: void getPrimaryMSRunPath(StringList & toFill)
        Returns the file path to the first MS run
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
    
    def getMinMZ(self) -> float:
        """
        Cython signature: double getMinMZ()
        Returns the minimum m/z
        """
        ...
    
    def getMaxMZ(self) -> float:
        """
        Cython signature: double getMaxMZ()
        Returns the maximum m/z
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
    
    def __richcmp__(self, other: FeatureMap, op: int) -> Any:
        ...
    
    def __iter__(self) -> Feature:
       ... 


class HPLC:
    """
    Cython implementation of _HPLC

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1HPLC.html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void HPLC()
        Representation of a HPLC experiment
        """
        ...
    
    @overload
    def __init__(self, in_0: HPLC ) -> None:
        """
        Cython signature: void HPLC(HPLC &)
        """
        ...
    
    def getInstrument(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getInstrument()
        Returns a reference to the instument name
        """
        ...
    
    def setInstrument(self, instrument: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setInstrument(String instrument)
        Sets the instument name
        """
        ...
    
    def getColumn(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getColumn()
        Returns a reference to the column description
        """
        ...
    
    def setColumn(self, column: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setColumn(String column)
        Sets the column description
        """
        ...
    
    def getTemperature(self) -> int:
        """
        Cython signature: int getTemperature()
        Returns the temperature (in degree C)
        """
        ...
    
    def setTemperature(self, temperature: int ) -> None:
        """
        Cython signature: void setTemperature(int temperature)
        Sets the temperature (in degree C)
        """
        ...
    
    def getPressure(self) -> int:
        """
        Cython signature: unsigned int getPressure()
        Returns the pressure (in bar)
        """
        ...
    
    def setPressure(self, pressure: int ) -> None:
        """
        Cython signature: void setPressure(unsigned int pressure)
        Sets the pressure (in bar)
        """
        ...
    
    def getFlux(self) -> int:
        """
        Cython signature: unsigned int getFlux()
        Returns the flux (in microliter/sec)
        """
        ...
    
    def setFlux(self, flux: int ) -> None:
        """
        Cython signature: void setFlux(unsigned int flux)
        Sets the flux (in microliter/sec)
        """
        ...
    
    def getComment(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getComment()
        Returns the comments
        """
        ...
    
    def setComment(self, comment: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setComment(String comment)
        Sets the comments
        """
        ...
    
    def getGradient(self) -> Gradient:
        """
        Cython signature: Gradient getGradient()
        Returns a mutable reference to the used gradient
        """
        ...
    
    def setGradient(self, gradient: Gradient ) -> None:
        """
        Cython signature: void setGradient(Gradient gradient)
        Sets the used gradient
        """
        ... 


class HyperScore:
    """
    Cython implementation of _HyperScore

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1HyperScore.html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void HyperScore()
        An implementation of the X!Tandem HyperScore PSM scoring function
        """
        ...
    
    @overload
    def __init__(self, in_0: HyperScore ) -> None:
        """
        Cython signature: void HyperScore(HyperScore &)
        """
        ...
    
    def compute(self, fragment_mass_tolerance: float , fragment_mass_tolerance_unit_ppm: bool , exp_spectrum: MSSpectrum , theo_spectrum: MSSpectrum ) -> float:
        """
        Cython signature: double compute(double fragment_mass_tolerance, bool fragment_mass_tolerance_unit_ppm, MSSpectrum & exp_spectrum, MSSpectrum & theo_spectrum)
        Compute the (ln transformed) X!Tandem HyperScore\n
        
        1. the dot product of peak intensities between matching peaks in experimental and theoretical spectrum is calculated
        2. the HyperScore is calculated from the dot product by multiplying by factorials of matching b- and y-ions
        
        
        :note: Peak intensities of the theoretical spectrum are typically 1 or TIC normalized, but can also be e.g. ion probabilities
        :param fragment_mass_tolerance: Mass tolerance applied left and right of the theoretical spectrum peak position
        :param fragment_mass_tolerance_unit_ppm: Unit of the mass tolerance is: Thomson if false, ppm if true
        :param exp_spectrum: Measured spectrum
        :param theo_spectrum: Theoretical spectrum Peaks need to contain an ion annotation as provided by TheoreticalSpectrumGenerator
        """
        ... 


class IDDecoyProbability:
    """
    Cython implementation of _IDDecoyProbability

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1IDDecoyProbability.html>`_
      -- Inherits from ['DefaultParamHandler']
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void IDDecoyProbability()
        IDDecoyProbability calculates probabilities using decoy approach
        """
        ...
    
    @overload
    def __init__(self, in_0: IDDecoyProbability ) -> None:
        """
        Cython signature: void IDDecoyProbability(IDDecoyProbability)
        """
        ...
    
    @overload
    def apply(self, prob_ids: PeptideIdentificationList , fwd_ids: PeptideIdentificationList , rev_ids: PeptideIdentificationList ) -> None:
        """
        Cython signature: void apply(PeptideIdentificationList & prob_ids, PeptideIdentificationList & fwd_ids, PeptideIdentificationList & rev_ids)
        Converts the forward and reverse identification into probabilities
        
        
        :param prob_ids: Output of the algorithm which includes identifications with probability based scores
        :param fwd_ids: Input parameter which represents the identifications of the forward search
        :param rev_ids: Input parameter which represents the identifications of the reversed search
        """
        ...
    
    @overload
    def apply(self, ids: PeptideIdentificationList ) -> None:
        """
        Cython signature: void apply(PeptideIdentificationList & ids)
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


class IMSAlphabet:
    """
    Cython implementation of _IMSAlphabet

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS::ims::IMSAlphabet_1_1IMSAlphabet.html>`_

    Holds an indexed list of bio-chemical elements.\n
    
    Presents an indexed list of bio-chemical elements of type (or derived from
    type) 'Element'. Due to indexed structure 'Alphabet' can be used similar
    to std::vector, for example to add a new element to 'Alphabet' function
    push_back(element_type) can be used. Elements or their properties (such
    as element's mass) can be accessed by index in a constant time. On the other
    hand accessing elements by their names takes linear time. Due to this and
    also the fact that 'Alphabet' is 'heavy-weighted' (consisting of
    'Element' -s or their derivatives where the depth of derivation as well is
    undefined resulting in possibly 'heavy' access operations) it is recommended
    not use 'Alphabet' directly in operations where fast access to
    'Element' 's properties is required. Instead consider to use
    'light-weighted' equivalents, such as 'Weights'
    
    
    :param map: MSExperiment to receive the identifications
    :param fmap: FeatureMap with PeptideIdentifications for the MSExperiment
    :param clear_ids: Reset peptide and protein identifications of each scan before annotating
    :param map_ms1: Attach Ids to MS1 spectra using RT mapping only (without precursor, without m/z)
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void IMSAlphabet()
        """
        ...
    
    @overload
    def __init__(self, in_0: IMSAlphabet ) -> None:
        """
        Cython signature: void IMSAlphabet(IMSAlphabet &)
        """
        ...
    
    @overload
    def __init__(self, elements: List[IMSElement] ) -> None:
        """
        Cython signature: void IMSAlphabet(libcpp_vector[IMSElement] & elements)
        """
        ...
    
    @overload
    def getElement(self, name: bytes ) -> IMSElement:
        """
        Cython signature: IMSElement getElement(libcpp_string & name)
        Gets the element with 'index' and returns element with the given index in alphabet
        """
        ...
    
    @overload
    def getElement(self, index: int ) -> IMSElement:
        """
        Cython signature: IMSElement getElement(int index)
        Gets the element with 'index'
        """
        ...
    
    def getName(self, index: int ) -> bytes:
        """
        Cython signature: libcpp_string getName(int index)
        Gets the symbol of the element with an 'index' in alphabet
        """
        ...
    
    @overload
    def getMass(self, name: bytes ) -> float:
        """
        Cython signature: double getMass(libcpp_string & name)
        Gets mono isotopic mass of the element with the symbol 'name'
        """
        ...
    
    @overload
    def getMass(self, index: int ) -> float:
        """
        Cython signature: double getMass(int index)
        Gets mass of the element with an 'index' in alphabet
        """
        ...
    
    def getMasses(self, isotope_index: int ) -> List[float]:
        """
        Cython signature: libcpp_vector[double] getMasses(int isotope_index)
        Gets masses of elements isotopes given by 'isotope_index'
        """
        ...
    
    def getAverageMasses(self) -> List[float]:
        """
        Cython signature: libcpp_vector[double] getAverageMasses()
        Gets average masses of elements
        """
        ...
    
    def hasName(self, name: bytes ) -> bool:
        """
        Cython signature: bool hasName(libcpp_string & name)
        Returns true if there is an element with symbol 'name' in the alphabet, false - otherwise
        """
        ...
    
    @overload
    def push_back(self, name: bytes , value: float ) -> None:
        """
        Cython signature: void push_back(libcpp_string & name, double value)
        Adds a new element with 'name' and mass 'value'
        """
        ...
    
    @overload
    def push_back(self, element: IMSElement ) -> None:
        """
        Cython signature: void push_back(IMSElement & element)
        Adds a new 'element' to the alphabet
        """
        ...
    
    def clear(self) -> None:
        """
        Cython signature: void clear()
        Clears the alphabet data
        """
        ...
    
    def sortByNames(self) -> None:
        """
        Cython signature: void sortByNames()
        Sorts the alphabet by names
        """
        ...
    
    def sortByValues(self) -> None:
        """
        Cython signature: void sortByValues()
        Sorts the alphabet by mass values
        """
        ...
    
    def load(self, fname: String ) -> None:
        """
        Cython signature: void load(String & fname)
        Loads the alphabet data from the file 'fname' using the default parser. If there is no file 'fname', throws an 'IOException'
        """
        ...
    
    def size(self) -> int:
        """
        Cython signature: int size()
        """
        ...
    
    def setElement(self, name: bytes , mass: float , forced: bool ) -> None:
        """
        Cython signature: void setElement(libcpp_string & name, double mass, bool forced)
        Overwrites an element in the alphabet with the 'name' with a new element constructed from the given 'name' and 'mass'
        """
        ...
    
    def erase(self, name: bytes ) -> bool:
        """
        Cython signature: bool erase(libcpp_string & name)
        Removes the element with 'name' from the alphabet
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


class IonIdentityMolecularNetworking:
    """
    Cython implementation of _IonIdentityMolecularNetworking

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1IonIdentityMolecularNetworking.html>`_

    Includes the necessary functions to generate filed required for GNPS ion identity molecular networking (IIMN).
    """
    
    def __init__(self) -> None:
        """
        Cython signature: void IonIdentityMolecularNetworking()
        """
        ...
    
    annotateConsensusMap: __static_IonIdentityMolecularNetworking_annotateConsensusMap
    
    writeSupplementaryPairTable: __static_IonIdentityMolecularNetworking_writeSupplementaryPairTable 


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


class IsotopePattern:
    """
    Cython implementation of _IsotopePattern

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS::FeatureFinderAlgorithmPickedHelperStructs_1_1IsotopePattern.html>`_
    """
    
    spectrum: List[int]
    
    intensity: List[float]
    
    mz_score: List[float]
    
    theoretical_mz: List[float]
    
    theoretical_pattern: TheoreticalIsotopePattern
    
    @overload
    def __init__(self, size: int ) -> None:
        """
        Cython signature: void IsotopePattern(size_t size)
        """
        ...
    
    @overload
    def __init__(self, in_0: IsotopePattern ) -> None:
        """
        Cython signature: void IsotopePattern(IsotopePattern &)
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


class MRMTransitionGroupPicker:
    """
    Cython implementation of _MRMTransitionGroupPicker

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1MRMTransitionGroupPicker.html>`_
      -- Inherits from ['DefaultParamHandler']
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void MRMTransitionGroupPicker()
        """
        ...
    
    @overload
    def __init__(self, in_0: MRMTransitionGroupPicker ) -> None:
        """
        Cython signature: void MRMTransitionGroupPicker(MRMTransitionGroupPicker &)
        """
        ...
    
    @overload
    def pickTransitionGroup(self, transition_group: LightMRMTransitionGroupCP ) -> None:
        """
        Cython signature: void pickTransitionGroup(LightMRMTransitionGroupCP transition_group)
        """
        ...
    
    @overload
    def pickTransitionGroup(self, transition_group: MRMTransitionGroupCP ) -> None:
        """
        Cython signature: void pickTransitionGroup(MRMTransitionGroupCP transition_group)
        """
        ...
    
    def createMRMFeature(self, transition_group: LightMRMTransitionGroupCP , picked_chroms: List[MSChromatogram] , smoothed_chroms: List[MSChromatogram] , chr_idx: int , peak_idx: int ) -> MRMFeature:
        """
        Cython signature: MRMFeature createMRMFeature(LightMRMTransitionGroupCP transition_group, libcpp_vector[MSChromatogram] & picked_chroms, libcpp_vector[MSChromatogram] & smoothed_chroms, const int chr_idx, const int peak_idx)
        """
        ...
    
    def remove_overlapping_features(self, picked_chroms: List[MSChromatogram] , best_left: float , best_right: float ) -> None:
        """
        Cython signature: void remove_overlapping_features(libcpp_vector[MSChromatogram] & picked_chroms, double best_left, double best_right)
        """
        ...
    
    def findLargestPeak(self, picked_chroms: List[MSChromatogram] , chr_idx: int , peak_idx: int ) -> None:
        """
        Cython signature: void findLargestPeak(libcpp_vector[MSChromatogram] & picked_chroms, int & chr_idx, int & peak_idx)
        """
        ...
    
    def findWidestPeakIndices(self, picked_chroms: List[MSChromatogram] , chrom_idx: int , point_idx: int ) -> None:
        """
        Cython signature: void findWidestPeakIndices(libcpp_vector[MSChromatogram] & picked_chroms, int & chrom_idx, int & point_idx)
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


class MassTrace:
    """
    Cython implementation of _MassTrace

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS::FeatureFinderAlgorithmPickedHelperStructs_1_1MassTrace.html>`_
    """
    
    max_rt: float
    
    theoretical_int: float
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void MassTrace()
        """
        ...
    
    @overload
    def __init__(self, in_0: MassTrace ) -> None:
        """
        Cython signature: void MassTrace(MassTrace &)
        """
        ...
    
    def getConvexhull(self) -> ConvexHull2D:
        """
        Cython signature: ConvexHull2D getConvexhull()
        """
        ...
    
    def updateMaximum(self) -> None:
        """
        Cython signature: void updateMaximum()
        """
        ...
    
    def getAvgMZ(self) -> float:
        """
        Cython signature: double getAvgMZ()
        """
        ...
    
    def isValid(self) -> bool:
        """
        Cython signature: bool isValid()
        """
        ... 


class MassTraces:
    """
    Cython implementation of _MassTraces

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS::FeatureFinderAlgorithmPickedHelperStructs_1_1MassTraces.html>`_
    """
    
    max_trace: int
    
    baseline: float
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void MassTraces()
        """
        ...
    
    @overload
    def __init__(self, in_0: MassTraces ) -> None:
        """
        Cython signature: void MassTraces(MassTraces &)
        """
        ...
    
    def getPeakCount(self) -> int:
        """
        Cython signature: size_t getPeakCount()
        """
        ...
    
    def isValid(self, seed_mz: float , trace_tolerance: float ) -> bool:
        """
        Cython signature: bool isValid(double seed_mz, double trace_tolerance)
        """
        ...
    
    def getTheoreticalmaxPosition(self) -> int:
        """
        Cython signature: size_t getTheoreticalmaxPosition()
        """
        ...
    
    def updateBaseline(self) -> None:
        """
        Cython signature: void updateBaseline()
        """
        ...
    
    def getRTBounds(self) -> List[float, float]:
        """
        Cython signature: libcpp_pair[double,double] getRTBounds()
        """
        ... 


class MasstraceCorrelator:
    """
    Cython implementation of _MasstraceCorrelator

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1MasstraceCorrelator.html>`_
      -- Inherits from ['DefaultParamHandler', 'ProgressLogger']
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void MasstraceCorrelator()
        """
        ...
    
    @overload
    def __init__(self, in_0: MasstraceCorrelator ) -> None:
        """
        Cython signature: void MasstraceCorrelator(MasstraceCorrelator &)
        """
        ...
    
    def createPseudoSpectra(self, map_: ConsensusMap , pseudo_spectra: MSExperiment , min_peak_nr: int , min_correlation: float , max_lag: int , max_rt_apex_difference: float ) -> None:
        """
        Cython signature: void createPseudoSpectra(const ConsensusMap & map_, MSExperiment & pseudo_spectra, size_t min_peak_nr, double min_correlation, int max_lag, double max_rt_apex_difference)
        Compute pseudo-spectra from a set of (MS2) masstraces
        
        This function will take a set of masstraces (consensus map) as input and
        produce a vector of pseudo spectra as output (pseudo_spectra result
        vector).
        
        It basically makes an all-vs-all comparison of all masstraces against
        each other and scores them on how similar they are in their mass traces.
        
        This assumes that the consensus feature is only from one (SWATH) map
        This assumes that the consensus map is sorted by intensity
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


class MultiplexDeltaMassesGenerator:
    """
    Cython implementation of _MultiplexDeltaMassesGenerator

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1MultiplexDeltaMassesGenerator.html>`_
      -- Inherits from ['DefaultParamHandler']
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void MultiplexDeltaMassesGenerator()
        """
        ...
    
    @overload
    def __init__(self, in_0: MultiplexDeltaMassesGenerator ) -> None:
        """
        Cython signature: void MultiplexDeltaMassesGenerator(MultiplexDeltaMassesGenerator &)
        """
        ...
    
    @overload
    def __init__(self, labels: Union[bytes, str, String] , missed_cleavages: int , label_mass_shift: Dict[Union[bytes, str, String], float] ) -> None:
        """
        Cython signature: void MultiplexDeltaMassesGenerator(String labels, int missed_cleavages, libcpp_map[String,double] label_mass_shift)
        """
        ...
    
    def generateKnockoutDeltaMasses(self) -> None:
        """
        Cython signature: void generateKnockoutDeltaMasses()
        """
        ...
    
    def getDeltaMassesList(self) -> List[MultiplexDeltaMasses]:
        """
        Cython signature: libcpp_vector[MultiplexDeltaMasses] getDeltaMassesList()
        """
        ...
    
    def getLabelShort(self, label: Union[bytes, str, String] ) -> Union[bytes, str, String]:
        """
        Cython signature: String getLabelShort(String label)
        """
        ...
    
    def getLabelLong(self, label: Union[bytes, str, String] ) -> Union[bytes, str, String]:
        """
        Cython signature: String getLabelLong(String label)
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


class MultiplexDeltaMassesGenerator_Label:
    """
    Cython implementation of _MultiplexDeltaMassesGenerator_Label

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1MultiplexDeltaMassesGenerator_Label.html>`_
    """
    
    short_name: Union[bytes, str, String]
    
    long_name: Union[bytes, str, String]
    
    description: Union[bytes, str, String]
    
    delta_mass: float
    
    def __init__(self, sn: Union[bytes, str, String] , ln: Union[bytes, str, String] , d: Union[bytes, str, String] , dm: float ) -> None:
        """
        Cython signature: void MultiplexDeltaMassesGenerator_Label(String sn, String ln, String d, double dm)
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


class NoopMSDataWritingConsumer:
    """
    Cython implementation of _NoopMSDataWritingConsumer

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1NoopMSDataWritingConsumer.html>`_

    Consumer class that perform no operation
    
    This is sometimes necessary to fulfill the requirement of passing an
    valid MSDataWritingConsumer object or pointer but no operation is
    required
    """
    
    def __init__(self, filename: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void NoopMSDataWritingConsumer(String filename)
        """
        ...
    
    def consumeSpectrum(self, s: MSSpectrum ) -> None:
        """
        Cython signature: void consumeSpectrum(MSSpectrum & s)
        """
        ...
    
    def consumeChromatogram(self, c: MSChromatogram ) -> None:
        """
        Cython signature: void consumeChromatogram(MSChromatogram & c)
        """
        ...
    
    def setExperimentalSettings(self, exp: ExperimentalSettings ) -> None:
        """
        Cython signature: void setExperimentalSettings(ExperimentalSettings & exp)
        """
        ...
    
    def setExpectedSize(self, expectedSpectra: int , expectedChromatograms: int ) -> None:
        """
        Cython signature: void setExpectedSize(size_t expectedSpectra, size_t expectedChromatograms)
        """
        ...
    
    def addDataProcessing(self, d: DataProcessing ) -> None:
        """
        Cython signature: void addDataProcessing(DataProcessing d)
        """
        ...
    
    def getNrSpectraWritten(self) -> int:
        """
        Cython signature: size_t getNrSpectraWritten()
        """
        ...
    
    def getNrChromatogramsWritten(self) -> int:
        """
        Cython signature: size_t getNrChromatogramsWritten()
        """
        ... 


class OMSSACSVFile:
    """
    Cython implementation of _OMSSACSVFile

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1OMSSACSVFile.html>`_

    File adapter for OMSSACSV files
    
    The files contain the results of the OMSSA algorithm in a comma separated manner. This file adapter is able to
    load the data from such a file into the structures of OpenMS
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void OMSSACSVFile()
        """
        ...
    
    @overload
    def __init__(self, in_0: OMSSACSVFile ) -> None:
        """
        Cython signature: void OMSSACSVFile(OMSSACSVFile &)
        """
        ...
    
    def load(self, filename: Union[bytes, str, String] , protein_identification: ProteinIdentification , id_data: PeptideIdentificationList ) -> None:
        """
        Cython signature: void load(const String & filename, ProteinIdentification & protein_identification, PeptideIdentificationList & id_data)
        Loads a OMSSA file
        
        The content of the file is stored in `features`
        
        
        :param filename: The name of the file to read from
        :param protein_identification: The protein ProteinIdentification data
        :param id_data: The peptide ids of the file
        :raises:
          Exception: FileNotFound is thrown if the file could not be opened
        :raises:
          Exception: ParseError is thrown if an error occurs during parsing
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


class OSBinaryDataArray:
    """
    Cython implementation of _OSBinaryDataArray

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenSwath_1_1OSBinaryDataArray.html>`_
    """
    
    data: List[float]
    
    description: bytes
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void OSBinaryDataArray()
        """
        ...
    
    @overload
    def __init__(self, in_0: OSBinaryDataArray ) -> None:
        """
        Cython signature: void OSBinaryDataArray(OSBinaryDataArray &)
        """
        ... 


class OSChromatogram:
    """
    Cython implementation of _OSChromatogram

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenSwath_1_1OSChromatogram.html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void OSChromatogram()
        """
        ...
    
    @overload
    def __init__(self, in_0: OSChromatogram ) -> None:
        """
        Cython signature: void OSChromatogram(OSChromatogram &)
        """
        ... 


class OSChromatogramMeta:
    """
    Cython implementation of _OSChromatogramMeta

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenSwath_1_1OSChromatogramMeta.html>`_
    """
    
    index: int
    
    id: bytes
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void OSChromatogramMeta()
        """
        ...
    
    @overload
    def __init__(self, in_0: OSChromatogramMeta ) -> None:
        """
        Cython signature: void OSChromatogramMeta(OSChromatogramMeta &)
        """
        ... 


class OSSpectrum:
    """
    Cython implementation of _OSSpectrum

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenSwath_1_1OSSpectrum.html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void OSSpectrum()
        """
        ...
    
    @overload
    def __init__(self, in_0: OSSpectrum ) -> None:
        """
        Cython signature: void OSSpectrum(OSSpectrum &)
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


class OpenSwathDataAccessHelper:
    """
    Cython implementation of _OpenSwathDataAccessHelper

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1OpenSwathDataAccessHelper.html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void OpenSwathDataAccessHelper()
        """
        ...
    
    @overload
    def __init__(self, in_0: OpenSwathDataAccessHelper ) -> None:
        """
        Cython signature: void OpenSwathDataAccessHelper(OpenSwathDataAccessHelper &)
        """
        ...
    
    def convertToOpenMSSpectrum(self, sptr: OSSpectrum , spectrum: MSSpectrum ) -> None:
        """
        Cython signature: void convertToOpenMSSpectrum(shared_ptr[OSSpectrum] sptr, MSSpectrum & spectrum)
        Converts a SpectrumPtr to an OpenMS Spectrum
        """
        ...
    
    def convertToOpenMSChromatogram(self, cptr: OSChromatogram , chromatogram: MSChromatogram ) -> None:
        """
        Cython signature: void convertToOpenMSChromatogram(shared_ptr[OSChromatogram] cptr, MSChromatogram & chromatogram)
        Converts a ChromatogramPtr to an OpenMS Chromatogram
        """
        ...
    
    def convertToOpenMSChromatogramFilter(self, chromatogram: MSChromatogram , cptr: OSChromatogram , rt_min: float , rt_max: float ) -> None:
        """
        Cython signature: void convertToOpenMSChromatogramFilter(MSChromatogram & chromatogram, shared_ptr[OSChromatogram] cptr, double rt_min, double rt_max)
        """
        ...
    
    def convertTargetedExp(self, transition_exp_: TargetedExperiment , transition_exp: LightTargetedExperiment ) -> None:
        """
        Cython signature: void convertTargetedExp(TargetedExperiment & transition_exp_, LightTargetedExperiment & transition_exp)
        Converts from the OpenMS TargetedExperiment to the OpenMs LightTargetedExperiment
        """
        ...
    
    def convertPeptideToAASequence(self, peptide: LightCompound , aa_sequence: AASequence ) -> None:
        """
        Cython signature: void convertPeptideToAASequence(LightCompound & peptide, AASequence & aa_sequence)
        Converts from the LightCompound to an OpenMS AASequence (with correct modifications)
        """
        ...
    
    def convertTargetedCompound(self, pep: Peptide , p: LightCompound ) -> None:
        """
        Cython signature: void convertTargetedCompound(Peptide pep, LightCompound & p)
        Converts from the OpenMS TargetedExperiment Peptide to the LightTargetedExperiment Peptide
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


class ParamEntry:
    """
    Cython implementation of _ParamEntry

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS::Param_1_1ParamEntry.html>`_
    """
    
    name: bytes
    
    description: bytes
    
    value: Union[int, float, bytes, str, List[int], List[float], List[bytes]]
    
    tags: Set[bytes]
    
    valid_strings: List[bytes]
    
    max_float: float
    
    min_float: float
    
    max_int: int
    
    min_int: int
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void ParamEntry()
        """
        ...
    
    @overload
    def __init__(self, in_0: ParamEntry ) -> None:
        """
        Cython signature: void ParamEntry(ParamEntry &)
        """
        ...
    
    @overload
    def __init__(self, n: bytes , v: Union[int, float, bytes, str, List[int], List[float], List[bytes]] , d: bytes , t: List[bytes] ) -> None:
        """
        Cython signature: void ParamEntry(libcpp_string n, ParamValue v, libcpp_string d, libcpp_vector[libcpp_string] t)
        """
        ...
    
    @overload
    def __init__(self, n: bytes , v: Union[int, float, bytes, str, List[int], List[float], List[bytes]] , d: bytes ) -> None:
        """
        Cython signature: void ParamEntry(libcpp_string n, ParamValue v, libcpp_string d)
        """
        ...
    
    def __richcmp__(self, other: ParamEntry, op: int) -> Any:
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


class PeakPickerIM:
    """
    Cython implementation of _PeakPickerIM

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1PeakPickerIM.html>`_

    Peak picking algorithm for ion mobility data
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void PeakPickerIM()
        """
        ...
    
    @overload
    def __init__(self, in_0: PeakPickerIM ) -> None:
        """
        Cython signature: void PeakPickerIM(PeakPickerIM &)
        """
        ...
    
    def pickIMTraces(self, s: MSSpectrum ) -> None:
        """
        Cython signature: void pickIMTraces(MSSpectrum & s)
        Use trace detection for IM peak picking.
        """
        ...
    
    def pickIMCluster(self, s: MSSpectrum ) -> None:
        """
        Cython signature: void pickIMCluster(MSSpectrum & s)
        Use clustering for IM peak picking.
        """
        ...
    
    def pickIMElutionProfiles(self, s: MSSpectrum ) -> None:
        """
        Cython signature: void pickIMElutionProfiles(MSSpectrum & s)
        Use elution profile detection for IM peak picking.
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


class PlainMSDataWritingConsumer:
    """
    Cython implementation of _PlainMSDataWritingConsumer

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1PlainMSDataWritingConsumer.html>`_
    """
    
    def __init__(self, filename: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void PlainMSDataWritingConsumer(String filename)
        """
        ...
    
    def consumeSpectrum(self, s: MSSpectrum ) -> None:
        """
        Cython signature: void consumeSpectrum(MSSpectrum & s)
        """
        ...
    
    def consumeChromatogram(self, c: MSChromatogram ) -> None:
        """
        Cython signature: void consumeChromatogram(MSChromatogram & c)
        """
        ...
    
    def setExperimentalSettings(self, exp: ExperimentalSettings ) -> None:
        """
        Cython signature: void setExperimentalSettings(ExperimentalSettings & exp)
        Set experimental settings for the whole file
        
        
        :param exp: Experimental settings to be used for this file (from this and the first spectrum/chromatogram, the class will deduce most of the header of the mzML file)
        """
        ...
    
    def setExpectedSize(self, expectedSpectra: int , expectedChromatograms: int ) -> None:
        """
        Cython signature: void setExpectedSize(size_t expectedSpectra, size_t expectedChromatograms)
        Set expected size of spectra and chromatograms to be written
        
        These numbers will be written in the spectrumList and chromatogramList
        tag in the mzML file. Therefore, these will contain wrong numbers if
        the expected size is not set correctly
        
        
        :param expectedSpectra: Number of spectra expected
        :param expectedChromatograms: Number of chromatograms expected
        """
        ...
    
    def addDataProcessing(self, d: DataProcessing ) -> None:
        """
        Cython signature: void addDataProcessing(DataProcessing d)
        Optionally add a data processing method to each chromatogram and spectrum
        
        The provided DataProcessing object will be added to each chromatogram
        and spectrum written to to the mzML file
        
        
        :param d: The DataProcessing object to be added
        """
        ...
    
    def getNrSpectraWritten(self) -> int:
        """
        Cython signature: size_t getNrSpectraWritten()
        Returns the number of spectra written
        """
        ...
    
    def getNrChromatogramsWritten(self) -> int:
        """
        Cython signature: size_t getNrChromatogramsWritten()
        Returns the number of chromatograms written
        """
        ...
    
    def setOptions(self, opt: PeakFileOptions ) -> None:
        """
        Cython signature: void setOptions(PeakFileOptions opt)
        """
        ...
    
    def getOptions(self) -> PeakFileOptions:
        """
        Cython signature: PeakFileOptions getOptions()
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


class RNaseDB:
    """
    Cython implementation of _RNaseDB

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1RNaseDB.html>`_
    """
    
    def getEnzyme(self, name: Union[bytes, str, String] ) -> DigestionEnzymeRNA:
        """
        Cython signature: const DigestionEnzymeRNA * getEnzyme(const String & name)
        """
        ...
    
    def getEnzymeByRegEx(self, cleavage_regex: Union[bytes, str, String] ) -> DigestionEnzymeRNA:
        """
        Cython signature: const DigestionEnzymeRNA * getEnzymeByRegEx(const String & cleavage_regex)
        """
        ...
    
    def getAllNames(self, all_names: List[bytes] ) -> None:
        """
        Cython signature: void getAllNames(libcpp_vector[String] & all_names)
        """
        ...
    
    def hasEnzyme(self, name: Union[bytes, str, String] ) -> bool:
        """
        Cython signature: bool hasEnzyme(const String & name)
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


class Seed:
    """
    Cython implementation of _Seed

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS::FeatureFinderAlgorithmPickedHelperStructs_1_1Seed.html>`_
    """
    
    spectrum: int
    
    peak: int
    
    intensity: float
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void Seed()
        """
        ...
    
    @overload
    def __init__(self, in_0: Seed ) -> None:
        """
        Cython signature: void Seed(Seed &)
        """
        ...
    
    def __richcmp__(self, other: Seed, op: int) -> Any:
        ... 


class SemanticValidator:
    """
    Cython implementation of _SemanticValidator

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS::Internal_1_1SemanticValidator.html>`_
    """
    
    def __init__(self, mapping: CVMappings , cv: ControlledVocabulary ) -> None:
        """
        Cython signature: void SemanticValidator(CVMappings mapping, ControlledVocabulary cv)
        """
        ...
    
    def validate(self, filename: Union[bytes, str, String] , errors: List[bytes] , warnings: List[bytes] ) -> bool:
        """
        Cython signature: bool validate(String filename, StringList errors, StringList warnings)
        """
        ...
    
    def locateTerm(self, path: Union[bytes, str, String] , parsed_term: SemanticValidator_CVTerm ) -> bool:
        """
        Cython signature: bool locateTerm(String path, SemanticValidator_CVTerm & parsed_term)
        Checks if a CVTerm is allowed in a given path
        """
        ...
    
    def setTag(self, tag: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setTag(String tag)
        Sets the CV parameter tag name (default 'cvParam')
        """
        ...
    
    def setAccessionAttribute(self, accession: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setAccessionAttribute(String accession)
        Sets the name of the attribute for accessions in the CV parameter tag name (default 'accession')
        """
        ...
    
    def setNameAttribute(self, name: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setNameAttribute(String name)
        Sets the name of the attribute for accessions in the CV parameter tag name (default 'name')
        """
        ...
    
    def setValueAttribute(self, value: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setValueAttribute(String value)
        Sets the name of the attribute for accessions in the CV parameter tag name (default 'value')
        """
        ...
    
    def setCheckTermValueTypes(self, check: bool ) -> None:
        """
        Cython signature: void setCheckTermValueTypes(bool check)
        Sets if CV term value types should be check (enabled by default)
        """
        ...
    
    def setCheckUnits(self, check: bool ) -> None:
        """
        Cython signature: void setCheckUnits(bool check)
        Sets if CV term units should be check (disabled by default)
        """
        ...
    
    def setUnitAccessionAttribute(self, accession: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setUnitAccessionAttribute(String accession)
        Sets the name of the unit accession attribute (default 'unitAccession')
        """
        ...
    
    def setUnitNameAttribute(self, name: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setUnitNameAttribute(String name)
        Sets the name of the unit name attribute (default 'unitName')
        """
        ... 


class SemanticValidator_CVTerm:
    """
    Cython implementation of _SemanticValidator_CVTerm

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS::Internal_1_1SemanticValidator_CVTerm.html>`_
    """
    
    accession: Union[bytes, str, String]
    
    name: Union[bytes, str, String]
    
    value: Union[bytes, str, String]
    
    has_value: bool
    
    unit_accession: Union[bytes, str, String]
    
    has_unit_accession: bool
    
    unit_name: Union[bytes, str, String]
    
    has_unit_name: bool
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void SemanticValidator_CVTerm()
        """
        ...
    
    @overload
    def __init__(self, in_0: SemanticValidator_CVTerm ) -> None:
        """
        Cython signature: void SemanticValidator_CVTerm(SemanticValidator_CVTerm &)
        """
        ... 


class SpectrumSettings:
    """
    Cython implementation of _SpectrumSettings

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1SpectrumSettings.html>`_
      -- Inherits from ['MetaInfoInterface']
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void SpectrumSettings()
        """
        ...
    
    @overload
    def __init__(self, in_0: SpectrumSettings ) -> None:
        """
        Cython signature: void SpectrumSettings(SpectrumSettings &)
        """
        ...
    
    def unify(self, in_0: SpectrumSettings ) -> None:
        """
        Cython signature: void unify(SpectrumSettings)
        """
        ...
    
    def getType(self) -> int:
        """
        Cython signature: int getType()
        Returns the spectrum type (centroided (PEAKS) or profile data (RAW))
        """
        ...
    
    def setType(self, in_0: int ) -> None:
        """
        Cython signature: void setType(SpectrumType)
        Sets the spectrum type
        """
        ...
    
    def getNativeID(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getNativeID()
        Returns the native identifier for the spectrum, used by the acquisition software
        """
        ...
    
    def setNativeID(self, in_0: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setNativeID(String)
        Sets the native identifier for the spectrum, used by the acquisition software
        """
        ...
    
    def getComment(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getComment()
        Returns the free-text comment
        """
        ...
    
    def setComment(self, in_0: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setComment(String)
        Sets the free-text comment
        """
        ...
    
    def getInstrumentSettings(self) -> InstrumentSettings:
        """
        Cython signature: InstrumentSettings getInstrumentSettings()
        Returns a const reference to the instrument settings of the current spectrum
        """
        ...
    
    def setInstrumentSettings(self, in_0: InstrumentSettings ) -> None:
        """
        Cython signature: void setInstrumentSettings(InstrumentSettings)
        Sets the instrument settings of the current spectrum
        """
        ...
    
    def getAcquisitionInfo(self) -> AcquisitionInfo:
        """
        Cython signature: AcquisitionInfo getAcquisitionInfo()
        Returns a const reference to the acquisition info
        """
        ...
    
    def setAcquisitionInfo(self, in_0: AcquisitionInfo ) -> None:
        """
        Cython signature: void setAcquisitionInfo(AcquisitionInfo)
        Sets the acquisition info
        """
        ...
    
    def getSourceFile(self) -> SourceFile:
        """
        Cython signature: SourceFile getSourceFile()
        Returns a const reference to the source file
        """
        ...
    
    def setSourceFile(self, in_0: SourceFile ) -> None:
        """
        Cython signature: void setSourceFile(SourceFile)
        Sets the source file
        """
        ...
    
    def getPrecursors(self) -> List[Precursor]:
        """
        Cython signature: libcpp_vector[Precursor] getPrecursors()
        Returns a const reference to the precursors
        """
        ...
    
    def setPrecursors(self, in_0: List[Precursor] ) -> None:
        """
        Cython signature: void setPrecursors(libcpp_vector[Precursor])
        Sets the precursors
        """
        ...
    
    def getProducts(self) -> List[Product]:
        """
        Cython signature: libcpp_vector[Product] getProducts()
        Returns a const reference to the products
        """
        ...
    
    def setProducts(self, in_0: List[Product] ) -> None:
        """
        Cython signature: void setProducts(libcpp_vector[Product])
        Sets the products
        """
        ...
    
    def getDataProcessing(self) -> List[DataProcessing]:
        """
        Cython signature: libcpp_vector[shared_ptr[DataProcessing]] getDataProcessing()
        """
        ...
    
    def setDataProcessing(self, in_0: List[DataProcessing] ) -> None:
        """
        Cython signature: void setDataProcessing(libcpp_vector[shared_ptr[DataProcessing]])
        """
        ...
    
    @staticmethod
    def getAllNamesOfSpectrumType() -> List[bytes]:
        """
        Cython signature: libcpp_vector[String] getAllNamesOfSpectrumType()
        Returns all spectrum type names known to OpenMS
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
    
    def __richcmp__(self, other: SpectrumSettings, op: int) -> Any:
        ...
    SpectrumType : __SpectrumType 


class String:
    """
    Cython implementation of _String

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1String.html>`_
    """
    
    def __init__(self) -> None:
        """
        Cython signature: void String()
        """
        ...
    
    def __richcmp__(self, other: String, op: int) -> Any:
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


class TheoreticalIsotopePattern:
    """
    Cython implementation of _TheoreticalIsotopePattern

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS::FeatureFinderAlgorithmPickedHelperStructs_1_1TheoreticalIsotopePattern.html>`_
    """
    
    intensity: List[float]
    
    optional_begin: int
    
    optional_end: int
    
    max: float
    
    trimmed_left: int
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void TheoreticalIsotopePattern()
        """
        ...
    
    @overload
    def __init__(self, in_0: TheoreticalIsotopePattern ) -> None:
        """
        Cython signature: void TheoreticalIsotopePattern(TheoreticalIsotopePattern &)
        """
        ...
    
    def size(self) -> int:
        """
        Cython signature: size_t size()
        """
        ... 


class TheoreticalSpectrumGenerator:
    """
    Cython implementation of _TheoreticalSpectrumGenerator

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1TheoreticalSpectrumGenerator.html>`_
      -- Inherits from ['DefaultParamHandler']
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void TheoreticalSpectrumGenerator()
        """
        ...
    
    @overload
    def __init__(self, in_0: TheoreticalSpectrumGenerator ) -> None:
        """
        Cython signature: void TheoreticalSpectrumGenerator(TheoreticalSpectrumGenerator &)
        """
        ...
    
    def getSpectrum(self, spec: MSSpectrum , peptide: AASequence , min_charge: int , max_charge: int ) -> None:
        """
        Cython signature: void getSpectrum(MSSpectrum & spec, AASequence & peptide, int min_charge, int max_charge)
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


class XQuestScores:
    """
    Cython implementation of _XQuestScores

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1XQuestScores.html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void XQuestScores()
        """
        ...
    
    @overload
    def __init__(self, in_0: XQuestScores ) -> None:
        """
        Cython signature: void XQuestScores(XQuestScores &)
        """
        ...
    
    @overload
    def preScore(self, matched_alpha: int , ions_alpha: int , matched_beta: int , ions_beta: int ) -> float:
        """
        Cython signature: float preScore(size_t matched_alpha, size_t ions_alpha, size_t matched_beta, size_t ions_beta)
        Compute a simple and fast to compute pre-score for a cross-link spectrum match
        
        :param matched_alpha: Number of experimental peaks matched to theoretical linear ions from the alpha peptide
        :param ions_alpha: Number of theoretical ions from the alpha peptide
        :param matched_beta: Number of experimental peaks matched to theoretical linear ions from the beta peptide
        :param ions_beta: Number of theoretical ions from the beta peptide
        """
        ...
    
    @overload
    def preScore(self, matched_alpha: int , ions_alpha: int ) -> float:
        """
        Cython signature: float preScore(size_t matched_alpha, size_t ions_alpha)
        Compute a simple and fast to compute pre-score for a mono-link spectrum match
        
        :param matched_alpha: Number of experimental peaks matched to theoretical linear ions from the alpha peptide
        :param ions_alpha: Number of theoretical ions from the alpha peptide
        """
        ...
    
    def matchOddsScore(self, theoretical_spec: MSSpectrum , fragment_mass_tolerance: float , fragment_mass_tolerance_unit_ppm: bool , is_xlink_spectrum: bool , n_charges: int ) -> float:
        """
        Cython signature: double matchOddsScore(MSSpectrum & theoretical_spec, double fragment_mass_tolerance, bool fragment_mass_tolerance_unit_ppm, bool is_xlink_spectrum, size_t n_charges)
        Compute the match-odds score, a score based on the probability of getting the given number of matched peaks by chance
        
        :param theoretical_spec: Theoretical spectrum, sorted by position
        :param matched_size: Alignment between the theoretical and the experimental spectra
        :param fragment_mass_tolerance: Fragment mass tolerance of the alignment
        :param fragment_mass_tolerance_unit_ppm: Fragment mass tolerance unit of the alignment, true = ppm, false = Da
        :param is_xlink_spectrum: Type of cross-link, true = cross-link, false = mono-link
        :param n_charges: Number of considered charges in the theoretical spectrum
        """
        ...
    
    def logOccupancyProb(self, theoretical_spec: MSSpectrum , matched_size: int , fragment_mass_tolerance: float , fragment_mass_tolerance_unit_ppm: bool ) -> float:
        """
        Cython signature: double logOccupancyProb(MSSpectrum theoretical_spec, size_t matched_size, double fragment_mass_tolerance, bool fragment_mass_tolerance_unit_ppm)
        Compute the logOccupancyProb score, similar to the match_odds, a score based on the probability of getting the given number of matched peaks by chance
        
        :param theoretical_spec: Theoretical spectrum, sorted by position
        :param matched_size: Number of matched peaks between experimental and theoretical spectra
        :param fragment_mass_tolerance: The tolerance of the alignment
        :param fragment_mass_tolerance_unit: The tolerance unit of the alignment, true = ppm, false = Da
        """
        ...
    
    def weightedTICScoreXQuest(self, alpha_size: int , beta_size: int , intsum_alpha: float , intsum_beta: float , total_current: float , type_is_cross_link: bool ) -> float:
        """
        Cython signature: double weightedTICScoreXQuest(size_t alpha_size, size_t beta_size, double intsum_alpha, double intsum_beta, double total_current, bool type_is_cross_link)
        """
        ...
    
    def weightedTICScore(self, alpha_size: int , beta_size: int , intsum_alpha: float , intsum_beta: float , total_current: float , type_is_cross_link: bool ) -> float:
        """
        Cython signature: double weightedTICScore(size_t alpha_size, size_t beta_size, double intsum_alpha, double intsum_beta, double total_current, bool type_is_cross_link)
        """
        ...
    
    def matchedCurrentChain(self, matched_spec_common: List[List[int, int]] , matched_spec_xlinks: List[List[int, int]] , spectrum_common_peaks: MSSpectrum , spectrum_xlink_peaks: MSSpectrum ) -> float:
        """
        Cython signature: double matchedCurrentChain(libcpp_vector[libcpp_pair[size_t,size_t]] & matched_spec_common, libcpp_vector[libcpp_pair[size_t,size_t]] & matched_spec_xlinks, MSSpectrum & spectrum_common_peaks, MSSpectrum & spectrum_xlink_peaks)
        """
        ...
    
    def totalMatchedCurrent(self, matched_spec_common_alpha: List[List[int, int]] , matched_spec_common_beta: List[List[int, int]] , matched_spec_xlinks_alpha: List[List[int, int]] , matched_spec_xlinks_beta: List[List[int, int]] , spectrum_common_peaks: MSSpectrum , spectrum_xlink_peaks: MSSpectrum ) -> float:
        """
        Cython signature: double totalMatchedCurrent(libcpp_vector[libcpp_pair[size_t,size_t]] & matched_spec_common_alpha, libcpp_vector[libcpp_pair[size_t,size_t]] & matched_spec_common_beta, libcpp_vector[libcpp_pair[size_t,size_t]] & matched_spec_xlinks_alpha, libcpp_vector[libcpp_pair[size_t,size_t]] & matched_spec_xlinks_beta, MSSpectrum & spectrum_common_peaks, MSSpectrum & spectrum_xlink_peaks)
        """
        ...
    
    def xCorrelation(self, spec1: MSSpectrum , spec2: MSSpectrum , maxshift: int , tolerance: float ) -> List[float]:
        """
        Cython signature: libcpp_vector[double] xCorrelation(MSSpectrum & spec1, MSSpectrum & spec2, int maxshift, double tolerance)
        """
        ...
    
    def xCorrelationPrescore(self, spec1: MSSpectrum , spec2: MSSpectrum , tolerance: float ) -> float:
        """
        Cython signature: double xCorrelationPrescore(MSSpectrum & spec1, MSSpectrum & spec2, double tolerance)
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


class __PeptideSearchEngineFIAlgorithm_ExitCodes:
    None
    EXECUTION_OK : int
    INPUT_FILE_EMPTY : int
    UNEXPECTED_RESULT : int
    UNKNOWN_ERROR : int
    ILLEGAL_PARAMETERS : int

    def getMapping(self) -> Dict[int, str]:
       ... 


class QuotingMethod:
    None
    NONE : int
    ESCAPE : int
    DOUBLE : int

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


class __SpectrumType:
    None
    UNKNOWN : int
    CENTROID : int
    PROFILE : int
    SIZE_OF_SPECTRUMTYPE : int

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

