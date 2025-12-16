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

def __static_MRMRTNormalizer_chauvenet(residuals: List[float] , pos: int ) -> bool:
    """
    Cython signature: bool chauvenet(libcpp_vector[double] residuals, int pos)
    """
    ...

def __static_MRMRTNormalizer_chauvenet_probability(residuals: List[float] , pos: int ) -> float:
    """
    Cython signature: double chauvenet_probability(libcpp_vector[double] residuals, int pos)
    """
    ...

def __static_MRMRTNormalizer_computeBinnedCoverage(rtRange: List[float, float] , pairs: List[List[float, float]] , nrBins: int , minPeptidesPerBin: int , minBinsFilled: int ) -> bool:
    """
    Cython signature: bool computeBinnedCoverage(libcpp_pair[double,double] rtRange, libcpp_vector[libcpp_pair[double,double]] & pairs, int nrBins, int minPeptidesPerBin, int minBinsFilled)
    """
    ...

def __static_FileHandler_computeFileHash(filename: Union[bytes, str, String] ) -> Union[bytes, str, String]:
    """
    Cython signature: String computeFileHash(const String & filename)
    """
    ...

def __static_VersionDetails_create(in_0: Union[bytes, str, String] ) -> VersionDetails:
    """
    Cython signature: VersionDetails create(String)
    """
    ...

def __static_VersionInfo_getBranch() -> Union[bytes, str, String]:
    """
    Cython signature: String getBranch()
    """
    ...

def __static_VersionInfo_getRevision() -> Union[bytes, str, String]:
    """
    Cython signature: String getRevision()
    """
    ...

def __static_VersionInfo_getTime() -> Union[bytes, str, String]:
    """
    Cython signature: String getTime()
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

def __static_VersionInfo_getVersion() -> Union[bytes, str, String]:
    """
    Cython signature: String getVersion()
    """
    ...

def __static_VersionInfo_getVersionStruct() -> VersionDetails:
    """
    Cython signature: VersionDetails getVersionStruct()
    """
    ...

def __static_FileHandler_hasValidExtension(filename: Union[bytes, str, String] , type_: int ) -> bool:
    """
    Cython signature: bool hasValidExtension(const String & filename, FileType type_)
    """
    ...

def __static_FileHandler_isSupported(type_: int ) -> bool:
    """
    Cython signature: bool isSupported(FileType type_)
    """
    ...

def __static_MRMRTNormalizer_removeOutliersIterative(pairs: List[List[float, float]] , rsq_limit: float , coverage_limit: float , use_chauvenet: bool , outlier_detection_method: bytes ) -> List[List[float, float]]:
    """
    Cython signature: libcpp_vector[libcpp_pair[double,double]] removeOutliersIterative(libcpp_vector[libcpp_pair[double,double]] & pairs, double rsq_limit, double coverage_limit, bool use_chauvenet, libcpp_string outlier_detection_method)
    """
    ...

def __static_MRMRTNormalizer_removeOutliersRANSAC(pairs: List[List[float, float]] , rsq_limit: float , coverage_limit: float , max_iterations: int , max_rt_threshold: float , sampling_size: int ) -> List[List[float, float]]:
    """
    Cython signature: libcpp_vector[libcpp_pair[double,double]] removeOutliersRANSAC(libcpp_vector[libcpp_pair[double,double]] & pairs, double rsq_limit, double coverage_limit, size_t max_iterations, double max_rt_threshold, size_t sampling_size)
    """
    ...

def __static_PeptideProteinResolution_run(proteins: List[ProteinIdentification] , peptides: PeptideIdentificationList ) -> None:
    """
    Cython signature: void run(libcpp_vector[ProteinIdentification] & proteins, PeptideIdentificationList & peptides)
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


class AccurateMassSearchEngine:
    """
    Cython implementation of _AccurateMassSearchEngine

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1AccurateMassSearchEngine.html>`_
      -- Inherits from ['DefaultParamHandler', 'ProgressLogger']
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void AccurateMassSearchEngine()
        """
        ...
    
    @overload
    def __init__(self, in_0: AccurateMassSearchEngine ) -> None:
        """
        Cython signature: void AccurateMassSearchEngine(AccurateMassSearchEngine &)
        """
        ...
    
    def queryByMZ(self, observed_mz: float , observed_charge: int , ion_mode: Union[bytes, str, String] , in_3: List[AccurateMassSearchResult] , observed_adduct: EmpiricalFormula ) -> None:
        """
        Cython signature: void queryByMZ(double observed_mz, int observed_charge, String ion_mode, libcpp_vector[AccurateMassSearchResult] &, EmpiricalFormula & observed_adduct)
        """
        ...
    
    def queryByFeature(self, feature: Feature , feature_index: int , ion_mode: Union[bytes, str, String] , in_3: List[AccurateMassSearchResult] ) -> None:
        """
        Cython signature: void queryByFeature(Feature feature, size_t feature_index, String ion_mode, libcpp_vector[AccurateMassSearchResult] &)
        """
        ...
    
    def queryByConsensusFeature(self, cfeat: ConsensusFeature , cf_index: int , number_of_maps: int , ion_mode: Union[bytes, str, String] , results: List[AccurateMassSearchResult] ) -> None:
        """
        Cython signature: void queryByConsensusFeature(ConsensusFeature cfeat, size_t cf_index, size_t number_of_maps, String ion_mode, libcpp_vector[AccurateMassSearchResult] & results)
        """
        ...
    
    @overload
    def run(self, in_0: FeatureMap , in_1: MzTab ) -> None:
        """
        Cython signature: void run(FeatureMap &, MzTab &)
        """
        ...
    
    @overload
    def run(self, in_0: FeatureMap , in_1: MzTabM ) -> None:
        """
        Cython signature: void run(FeatureMap &, MzTabM &)
        """
        ...
    
    @overload
    def run(self, in_0: ConsensusMap , in_1: MzTab ) -> None:
        """
        Cython signature: void run(ConsensusMap &, MzTab &)
        """
        ...
    
    def init(self) -> None:
        """
        Cython signature: void init()
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


class ChargePair:
    """
    Cython implementation of _ChargePair

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1ChargePair.html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void ChargePair()
        """
        ...
    
    @overload
    def __init__(self, in_0: ChargePair ) -> None:
        """
        Cython signature: void ChargePair(ChargePair &)
        """
        ...
    
    @overload
    def __init__(self, index0: int , index1: int , charge0: int , charge1: int , compomer: Compomer , mass_diff: float , active: bool ) -> None:
        """
        Cython signature: void ChargePair(size_t index0, size_t index1, int charge0, int charge1, Compomer compomer, double mass_diff, bool active)
        """
        ...
    
    def getCharge(self, pairID: int ) -> int:
        """
        Cython signature: int getCharge(unsigned int pairID)
        Returns the charge (for element 0 or 1)
        """
        ...
    
    def setCharge(self, pairID: int , e: int ) -> None:
        """
        Cython signature: void setCharge(unsigned int pairID, int e)
        Sets the charge (for element 0 or 1)
        """
        ...
    
    def getElementIndex(self, pairID: int ) -> int:
        """
        Cython signature: size_t getElementIndex(unsigned int pairID)
        Returns the element index (for element 0 or 1)
        """
        ...
    
    def setElementIndex(self, pairID: int , e: int ) -> None:
        """
        Cython signature: void setElementIndex(unsigned int pairID, size_t e)
        Sets the element index (for element 0 or 1)
        """
        ...
    
    def getCompomer(self) -> Compomer:
        """
        Cython signature: Compomer getCompomer()
        Returns the Id of the compomer that explains the mass difference
        """
        ...
    
    def setCompomer(self, compomer: Compomer ) -> None:
        """
        Cython signature: void setCompomer(Compomer & compomer)
        Sets the compomer id
        """
        ...
    
    def getMassDiff(self) -> float:
        """
        Cython signature: double getMassDiff()
        Returns the mass difference
        """
        ...
    
    def setMassDiff(self, mass_diff: float ) -> None:
        """
        Cython signature: void setMassDiff(double mass_diff)
        Sets the mass difference
        """
        ...
    
    def getEdgeScore(self) -> float:
        """
        Cython signature: double getEdgeScore()
        Returns the ILP edge score
        """
        ...
    
    def setEdgeScore(self, score: float ) -> None:
        """
        Cython signature: void setEdgeScore(double score)
        Sets the ILP edge score
        """
        ...
    
    def isActive(self) -> bool:
        """
        Cython signature: bool isActive()
        Is this pair realized?
        """
        ...
    
    def setActive(self, active: bool ) -> None:
        """
        Cython signature: void setActive(bool active)
        """
        ... 


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


class ConsensusIDAlgorithmBest:
    """
    Cython implementation of _ConsensusIDAlgorithmBest

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1ConsensusIDAlgorithmBest.html>`_
      -- Inherits from ['ConsensusIDAlgorithmIdentity']
    """
    
    def __init__(self) -> None:
        """
        Cython signature: void ConsensusIDAlgorithmBest()
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


class CubicSpline2d:
    """
    Cython implementation of _CubicSpline2d

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1CubicSpline2d.html>`_
    """
    
    @overload
    def __init__(self, x: List[float] , y: List[float] ) -> None:
        """
        Cython signature: void CubicSpline2d(libcpp_vector[double] x, libcpp_vector[double] y)
        """
        ...
    
    @overload
    def __init__(self, in_0: CubicSpline2d ) -> None:
        """
        Cython signature: void CubicSpline2d(CubicSpline2d &)
        """
        ...
    
    @overload
    def __init__(self, m: Dict[float, float] ) -> None:
        """
        Cython signature: void CubicSpline2d(libcpp_map[double,double] m)
        """
        ...
    
    def eval(self, x: float ) -> float:
        """
        Cython signature: double eval(double x)
        Evaluates the cubic spline
        """
        ...
    
    def derivatives(self, x: float , order: int ) -> float:
        """
        Cython signature: double derivatives(double x, unsigned int order)
        Returns first, second or third derivative of cubic spline
        """
        ... 


class DataFilter:
    """
    Cython implementation of _DataFilter

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1DataFilter.html>`_
    """
    
    field: int
    
    op: int
    
    value: float
    
    value_string: Union[bytes, str, String]
    
    meta_name: Union[bytes, str, String]
    
    value_is_numerical: bool
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void DataFilter()
        """
        ...
    
    @overload
    def __init__(self, in_0: DataFilter ) -> None:
        """
        Cython signature: void DataFilter(DataFilter &)
        """
        ...
    
    def toString(self) -> Union[bytes, str, String]:
        """
        Cython signature: String toString()
        """
        ...
    
    def fromString(self, filter_: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void fromString(const String & filter_)
        """
        ...
    
    def __str__(self) -> Union[bytes, str, String]:
        """
        Cython signature: String toString()
        """
        ...
    
    def __richcmp__(self, other: DataFilter, op: int) -> Any:
        ... 


class DataFilters:
    """
    Cython implementation of _DataFilters

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1DataFilters.html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void DataFilters()
        """
        ...
    
    @overload
    def __init__(self, in_0: DataFilters ) -> None:
        """
        Cython signature: void DataFilters(DataFilters &)
        """
        ...
    
    def size(self) -> int:
        """
        Cython signature: size_t size()
        """
        ...
    
    def __getitem__(self, in_0: int ) -> DataFilter:
        """
        Cython signature: DataFilter operator[](size_t)
        """
        ...
    
    def add(self, filter_: DataFilter ) -> None:
        """
        Cython signature: void add(DataFilter & filter_)
        """
        ...
    
    def remove(self, index: int ) -> None:
        """
        Cython signature: void remove(size_t index)
        """
        ...
    
    def replace(self, index: int , filter_: DataFilter ) -> None:
        """
        Cython signature: void replace(size_t index, DataFilter & filter_)
        """
        ...
    
    def clear(self) -> None:
        """
        Cython signature: void clear()
        """
        ...
    
    def setActive(self, is_active: bool ) -> None:
        """
        Cython signature: void setActive(bool is_active)
        """
        ...
    
    def isActive(self) -> bool:
        """
        Cython signature: bool isActive()
        """
        ...
    
    @overload
    def passes(self, feature: Feature ) -> bool:
        """
        Cython signature: bool passes(Feature & feature)
        """
        ...
    
    @overload
    def passes(self, consensus_feature: ConsensusFeature ) -> bool:
        """
        Cython signature: bool passes(ConsensusFeature & consensus_feature)
        """
        ...
    
    @overload
    def passes(self, spectrum: MSSpectrum , peak_index: int ) -> bool:
        """
        Cython signature: bool passes(MSSpectrum & spectrum, size_t peak_index)
        """
        ...
    FilterOperation : __FilterOperation
    FilterType : __FilterType 


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


class EnzymaticDigestion:
    """
    Cython implementation of _EnzymaticDigestion

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1EnzymaticDigestion.html>`_

      Class for the enzymatic digestion of proteins
    
      Digestion can be performed using simple regular expressions, e.g. [KR] | [^P] for trypsin.
      Also missed cleavages can be modeled, i.e. adjacent peptides are not cleaved
      due to enzyme malfunction/access restrictions. If n missed cleavages are allowed, all possible resulting
      peptides (cleaved and uncleaved) with up to n missed cleavages are returned.
      Thus no random selection of just n specific missed cleavage sites is performed.
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void EnzymaticDigestion()
        """
        ...
    
    @overload
    def __init__(self, in_0: EnzymaticDigestion ) -> None:
        """
        Cython signature: void EnzymaticDigestion(EnzymaticDigestion &)
        """
        ...
    
    def getMissedCleavages(self) -> int:
        """
        Cython signature: size_t getMissedCleavages()
        Returns the max. number of allowed missed cleavages for the digestion
        """
        ...
    
    def setMissedCleavages(self, missed_cleavages: int ) -> None:
        """
        Cython signature: void setMissedCleavages(size_t missed_cleavages)
        Sets the max. number of allowed missed cleavages for the digestion (default is 0). This setting is ignored when log model is used
        """
        ...
    
    def countInternalCleavageSites(self, sequence: Union[bytes, str, String] ) -> int:
        """
        Cython signature: size_t countInternalCleavageSites(String sequence)
        Returns the number of internal cleavage sites for this sequence.
        """
        ...
    
    def getEnzymeName(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getEnzymeName()
        Returns the enzyme for the digestion
        """
        ...
    
    def setEnzyme(self, enzyme: DigestionEnzyme ) -> None:
        """
        Cython signature: void setEnzyme(DigestionEnzyme * enzyme)
        Sets the enzyme for the digestion
        """
        ...
    
    def getSpecificity(self) -> int:
        """
        Cython signature: Specificity getSpecificity()
        Returns the specificity for the digestion
        """
        ...
    
    def setSpecificity(self, spec: int ) -> None:
        """
        Cython signature: void setSpecificity(Specificity spec)
        Sets the specificity for the digestion (default is SPEC_FULL)
        """
        ...
    
    def getSpecificityByName(self, name: Union[bytes, str, String] ) -> int:
        """
        Cython signature: Specificity getSpecificityByName(String name)
        Returns the specificity by name. Returns SPEC_UNKNOWN if name is not valid
        """
        ...
    
    def digestUnmodified(self, sequence: StringView , output: List[StringView] , min_length: int , max_length: int ) -> int:
        """
        Cython signature: size_t digestUnmodified(StringView sequence, libcpp_vector[StringView] & output, size_t min_length, size_t max_length)
        Performs the enzymatic digestion of an unmodified sequence\n
        By returning only references into the original string this is very fast
        
        
        :param sequence: Sequence to digest
        :param output: Digestion products
        :param min_length: Minimal length of reported products
        :param max_length: Maximal length of reported products (0 = no restriction)
        :return: Number of discarded digestion products (which are not matching length restrictions)
        """
        ...
    
    def isValidProduct(self, sequence: Union[bytes, str, String] , pos: int , length: int , ignore_missed_cleavages: bool ) -> bool:
        """
        Cython signature: bool isValidProduct(String sequence, int pos, int length, bool ignore_missed_cleavages)
        Boolean operator returns true if the peptide fragment starting at position `pos` with length `length` within the sequence `sequence` generated by the current enzyme\n
        Checks if peptide is a valid digestion product of the enzyme, taking into account specificity and the MC flag provided here
        
        
        :param protein: Protein sequence
        :param pep_pos: Starting index of potential peptide
        :param pep_length: Length of potential peptide
        :param ignore_missed_cleavages: Do not compare MC's of potential peptide to the maximum allowed MC's
        :return: True if peptide has correct n/c terminals (according to enzyme, specificity and missed cleavages)
        """
        ...
    Specificity : __Specificity 


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


class GaussFilter:
    """
    Cython implementation of _GaussFilter

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1GaussFilter.html>`_
      -- Inherits from ['DefaultParamHandler', 'ProgressLogger']
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void GaussFilter()
        This class represents a Gaussian lowpass-filter which works on uniform as well as on non-uniform profile data
        """
        ...
    
    @overload
    def __init__(self, in_0: GaussFilter ) -> None:
        """
        Cython signature: void GaussFilter(GaussFilter &)
        """
        ...
    
    @overload
    def filter(self, spectrum: MSSpectrum ) -> None:
        """
        Cython signature: void filter(MSSpectrum & spectrum)
        Smoothes an MSSpectrum containing profile data
        """
        ...
    
    @overload
    def filter(self, chromatogram: MSChromatogram ) -> None:
        """
        Cython signature: void filter(MSChromatogram & chromatogram)
        """
        ...
    
    def filterExperiment(self, exp: MSExperiment ) -> None:
        """
        Cython signature: void filterExperiment(MSExperiment & exp)
        Smoothes an MSExperiment containing profile data
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


class IsotopeLabelingMDVs:
    """
    Cython implementation of _IsotopeLabelingMDVs

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1IsotopeLabelingMDVs.html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void IsotopeLabelingMDVs()
        """
        ...
    
    @overload
    def __init__(self, in_0: IsotopeLabelingMDVs ) -> None:
        """
        Cython signature: void IsotopeLabelingMDVs(IsotopeLabelingMDVs &)
        """
        ...
    
    def isotopicCorrection(self, normalized_feature: Feature , corrected_feature: Feature , correction_matrix: MatrixDouble , correction_matrix_agent: int ) -> None:
        """
        Cython signature: void isotopicCorrection(const Feature & normalized_feature, Feature & corrected_feature, MatrixDouble & correction_matrix, const DerivatizationAgent & correction_matrix_agent)
        This function performs an isotopic correction to account for unlabeled abundances coming from
        the derivatization agent (e.g., tBDMS) using correction matrix method and is calculated as follows:
        
        
        :param normalized_feature: Feature with normalized values for each component and unlabeled chemical formula for each component group
        :param correction_matrix: Square matrix holding correction factors derived either experimentally or theoretically which describe how spectral peaks of naturally abundant 13C contribute to spectral peaks that overlap (or convolve) the spectral peaks of the corrected MDV of the derivatization agent
        :param correction_matrix_agent: Name of the derivatization agent, the internally stored correction matrix if the name of the agent is supplied, only "TBDMS" is supported for now
        :return: corrected_feature: Feature with corrected values for each component
        """
        ...
    
    def isotopicCorrections(self, normalized_featureMap: FeatureMap , corrected_featureMap: FeatureMap , correction_matrix: MatrixDouble , correction_matrix_agent: int ) -> None:
        """
        Cython signature: void isotopicCorrections(const FeatureMap & normalized_featureMap, FeatureMap & corrected_featureMap, MatrixDouble & correction_matrix, const DerivatizationAgent & correction_matrix_agent)
        This function performs an isotopic correction to account for unlabeled abundances coming from
        the derivatization agent (e.g., tBDMS) using correction matrix method and is calculated as follows:
        
        
        :param normalized_featuremap: FeatureMap with normalized values for each component and unlabeled chemical formula for each component group
        :param correction_matrix: Square matrix holding correction factors derived either experimentally or theoretically which describe how spectral peaks of naturally abundant 13C contribute to spectral peaks that overlap (or convolve) the spectral peaks of the corrected MDV of the derivatization agent
        :param correction_matrix_agent: Name of the derivatization agent, the internally stored correction matrix if the name of the agent is supplied, only "TBDMS" is supported for now
        :return corrected_featuremap: FeatureMap with corrected values for each component
        """
        ...
    
    def calculateIsotopicPurity(self, normalized_feature: Feature , experiment_data: List[float] , isotopic_purity_name: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void calculateIsotopicPurity(const Feature & normalized_feature, const libcpp_vector[double] & experiment_data, const String & isotopic_purity_name)
        This function calculates the isotopic purity of the MDV using the following formula:
        isotopic purity of tracer (atom % 13C) = n / [n + (M + n-1)/(M + n)],
        where n in M+n is represented as the index of the result
        The formula is extracted from "High-resolution 13C metabolic flux analysis",
        Long et al, doi:10.1038/s41596-019-0204-0
        
        
        :param normalized_feature: Feature with normalized values for each component and the number of heavy labeled e.g., carbons. Out is a Feature with the calculated isotopic purity for the component group
        :param experiment_data: Vector of experiment data in percent
        :param isotopic_purity_name: Name of the isotopic purity tracer to be saved as a meta value
        """
        ...
    
    def calculateMDVAccuracy(self, normalized_feature: Feature , feature_name: Union[bytes, str, String] , fragment_isotopomer_theoretical_formula: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void calculateMDVAccuracy(const Feature & normalized_feature, const String & feature_name, const String & fragment_isotopomer_theoretical_formula)
        This function calculates the accuracy of the MDV as compared to the theoretical MDV (only for 12C quality control experiments)
        using average deviation to the mean. The result is mapped to the meta value "average_accuracy" in the updated feature
        
        
        :param normalized_feature: Feature with normalized values for each component and the chemical formula of the component group. Out is a Feature with the component group accuracy and accuracy for the error for each component
        :param fragment_isotopomer_measured: Measured scan values
        :param fragment_isotopomer_theoretical_formula: Empirical formula from which the theoretical values will be generated
        """
        ...
    
    def calculateMDVAccuracies(self, normalized_featureMap: FeatureMap , feature_name: Union[bytes, str, String] , fragment_isotopomer_theoretical_formulas: Dict[Union[bytes, str], Union[bytes, str]] ) -> None:
        """
        Cython signature: void calculateMDVAccuracies(const FeatureMap & normalized_featureMap, const String & feature_name, const libcpp_map[libcpp_utf8_string,libcpp_utf8_string] & fragment_isotopomer_theoretical_formulas)
        This function calculates the accuracy of the MDV as compared to the theoretical MDV (only for 12C quality control experiments)
        using average deviation to the mean
        
        
        param normalized_featuremap: FeatureMap with normalized values for each component and the chemical formula of the component group. Out is a FeatureMap with the component group accuracy and accuracy for the error for each component
        param fragment_isotopomer_measured: Measured scan values
        param fragment_isotopomer_theoretical_formula: A map of ProteinName/peptideRef to Empirical formula from which the theoretical values will be generated
        """
        ...
    
    def calculateMDV(self, measured_feature: Feature , normalized_feature: Feature , mass_intensity_type: int , feature_name: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void calculateMDV(const Feature & measured_feature, Feature & normalized_feature, const MassIntensityType & mass_intensity_type, const String & feature_name)
        """
        ...
    
    def calculateMDVs(self, measured_featureMap: FeatureMap , normalized_featureMap: FeatureMap , mass_intensity_type: int , feature_name: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void calculateMDVs(const FeatureMap & measured_featureMap, FeatureMap & normalized_featureMap, const MassIntensityType & mass_intensity_type, const String & feature_name)
        """
        ... 


class LPWrapper:
    """
    Cython implementation of _LPWrapper

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1LPWrapper.html>`_
    """
    
    def __init__(self) -> None:
        """
        Cython signature: void LPWrapper()
        """
        ...
    
    @overload
    def addRow(self, row_indices: List[int] , row_values: List[float] , name: Union[bytes, str, String] ) -> int:
        """
        Cython signature: int addRow(libcpp_vector[int] row_indices, libcpp_vector[double] row_values, const String & name)
        Adds a row to the LP matrix, returns index
        """
        ...
    
    @overload
    def addRow(self, row_indices: List[int] , row_values: List[float] , name: Union[bytes, str, String] , lower_bound: float , upper_bound: float , type_: int ) -> int:
        """
        Cython signature: int addRow(const libcpp_vector[int] & row_indices, const libcpp_vector[double] & row_values, const String & name, double lower_bound, double upper_bound, LPWrapper_Type type_)
        Adds a row with boundaries to the LP matrix, returns index
        """
        ...
    
    @overload
    def addColumn(self, ) -> int:
        """
        Cython signature: int addColumn()
        Adds an empty column to the LP matrix, returns index
        """
        ...
    
    @overload
    def addColumn(self, column_indices: List[int] , column_values: List[float] , name: Union[bytes, str, String] ) -> int:
        """
        Cython signature: int addColumn(libcpp_vector[int] column_indices, libcpp_vector[double] column_values, const String & name)
        Adds a column to the LP matrix, returns index
        """
        ...
    
    @overload
    def addColumn(self, column_indices: List[int] , column_values: List[float] , name: Union[bytes, str, String] , lower_bound: float , upper_bound: float , type_: int ) -> int:
        """
        Cython signature: int addColumn(const libcpp_vector[int] & column_indices, const libcpp_vector[double] & column_values, const String & name, double lower_bound, double upper_bound, LPWrapper_Type type_)
        Adds a column with boundaries to the LP matrix, returns index
        """
        ...
    
    def deleteRow(self, index: int ) -> None:
        """
        Cython signature: void deleteRow(int index)
        Delete index-th row
        """
        ...
    
    def setColumnName(self, index: int , name: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setColumnName(int index, const String & name)
        Sets name of the index-th column
        """
        ...
    
    def getColumnName(self, index: int ) -> Union[bytes, str, String]:
        """
        Cython signature: String getColumnName(int index)
        Returns name of the index-th column
        """
        ...
    
    def getRowName(self, index: int ) -> Union[bytes, str, String]:
        """
        Cython signature: String getRowName(int index)
        Sets name of the index-th row
        """
        ...
    
    def getRowIndex(self, name: Union[bytes, str, String] ) -> int:
        """
        Cython signature: int getRowIndex(const String & name)
        Returns index of the row with name
        """
        ...
    
    def getColumnIndex(self, name: Union[bytes, str, String] ) -> int:
        """
        Cython signature: int getColumnIndex(const String & name)
        Returns index of the column with name
        """
        ...
    
    def getColumnUpperBound(self, index: int ) -> float:
        """
        Cython signature: double getColumnUpperBound(int index)
        Returns column's upper bound
        """
        ...
    
    def getColumnLowerBound(self, index: int ) -> float:
        """
        Cython signature: double getColumnLowerBound(int index)
        Returns column's lower bound
        """
        ...
    
    def getRowUpperBound(self, index: int ) -> float:
        """
        Cython signature: double getRowUpperBound(int index)
        Returns row's upper bound
        """
        ...
    
    def getRowLowerBound(self, index: int ) -> float:
        """
        Cython signature: double getRowLowerBound(int index)
        Returns row's lower bound
        """
        ...
    
    def setRowName(self, index: int , name: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setRowName(int index, const String & name)
        Sets name of the index-th row
        """
        ...
    
    def setColumnBounds(self, index: int , lower_bound: float , upper_bound: float , type_: int ) -> None:
        """
        Cython signature: void setColumnBounds(int index, double lower_bound, double upper_bound, LPWrapper_Type type_)
        Sets column bounds
        """
        ...
    
    def setRowBounds(self, index: int , lower_bound: float , upper_bound: float , type_: int ) -> None:
        """
        Cython signature: void setRowBounds(int index, double lower_bound, double upper_bound, LPWrapper_Type type_)
        Sets row bounds
        """
        ...
    
    def setColumnType(self, index: int , type_: int ) -> None:
        """
        Cython signature: void setColumnType(int index, VariableType type_)
        Sets column/variable type.
        """
        ...
    
    def getColumnType(self, index: int ) -> int:
        """
        Cython signature: VariableType getColumnType(int index)
        Returns column/variable type.
        """
        ...
    
    def setObjective(self, index: int , obj_value: float ) -> None:
        """
        Cython signature: void setObjective(int index, double obj_value)
        Sets objective value for column with index
        """
        ...
    
    def getObjective(self, index: int ) -> float:
        """
        Cython signature: double getObjective(int index)
        Returns objective value for column with index
        """
        ...
    
    def setObjectiveSense(self, sense: int ) -> None:
        """
        Cython signature: void setObjectiveSense(Sense sense)
        Sets objective direction
        """
        ...
    
    def getObjectiveSense(self) -> int:
        """
        Cython signature: Sense getObjectiveSense()
        Returns objective sense
        """
        ...
    
    def getNumberOfColumns(self) -> int:
        """
        Cython signature: int getNumberOfColumns()
        Returns number of columns
        """
        ...
    
    def getNumberOfRows(self) -> int:
        """
        Cython signature: int getNumberOfRows()
        Returns number of rows
        """
        ...
    
    def setElement(self, row_index: int , column_index: int , value: float ) -> None:
        """
        Cython signature: void setElement(int row_index, int column_index, double value)
        Sets the element
        """
        ...
    
    def getElement(self, row_index: int , column_index: int ) -> float:
        """
        Cython signature: double getElement(int row_index, int column_index)
        Returns the element
        """
        ...
    
    def readProblem(self, filename: Union[bytes, str, String] , format_: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void readProblem(String filename, String format_)
        Read LP from file
        
        
        :param filename: Filename where to store the LP problem
        :param format: LP, MPS or GLPK
        """
        ...
    
    def writeProblem(self, filename: Union[bytes, str, String] , format_: int ) -> None:
        """
        Cython signature: void writeProblem(const String & filename, WriteFormat format_)
        Write LP formulation to a file
        
        
        :param filename: Output filename, if the filename ends with '.gz' it will be compressed
        :param format: MPS-format is supported by GLPK and COIN-OR; LP and GLPK-formats only by GLPK
        """
        ...
    
    def solve(self, solver_param: SolverParam , verbose_level: int ) -> int:
        """
        Cython signature: int solve(SolverParam & solver_param, size_t verbose_level)
        Solve problems, parameters like enabled heuristics can be given via solver_param\n
        
        The verbose level (0,1,2) determines if the solver prints status messages and internals
        
        
        :param solver_param: Parameters of the solver introduced by SolverParam
        :param verbose_level: Sets verbose level
        :return: solver dependent
        """
        ...
    
    def getStatus(self) -> int:
        """
        Cython signature: SolverStatus getStatus()
        Returns solution status
        
        
        :return: status: 1 - undefined, 2 - integer optimal, 3- integer feasible (no optimality proven), 4- no integer feasible solution
        """
        ...
    
    def getObjectiveValue(self) -> float:
        """
        Cython signature: double getObjectiveValue()
        """
        ...
    
    def getColumnValue(self, index: int ) -> float:
        """
        Cython signature: double getColumnValue(int index)
        """
        ...
    
    def getNumberOfNonZeroEntriesInRow(self, idx: int ) -> int:
        """
        Cython signature: int getNumberOfNonZeroEntriesInRow(int idx)
        """
        ...
    
    def getMatrixRow(self, idx: int , indexes: List[int] ) -> None:
        """
        Cython signature: void getMatrixRow(int idx, libcpp_vector[int] & indexes)
        """
        ...
    
    def getSolver(self) -> int:
        """
        Cython signature: SOLVER getSolver()
        Returns currently active solver
        """
        ...
    LPWrapper_Type : __LPWrapper_Type
    SOLVER : __SOLVER
    Sense : __Sense
    SolverStatus : __SolverStatus
    VariableType : __VariableType
    WriteFormat : __WriteFormat 


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


class LinearResamplerAlign:
    """
    Cython implementation of _LinearResamplerAlign

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1LinearResamplerAlign.html>`_
      -- Inherits from ['LinearResampler']
    """
    
    def __init__(self, in_0: LinearResamplerAlign ) -> None:
        """
        Cython signature: void LinearResamplerAlign(LinearResamplerAlign &)
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


class MRMFeature:
    """
    Cython implementation of _MRMFeature

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1MRMFeature.html>`_
      -- Inherits from ['Feature']

    A multi-chromatogram MRM (Multiple Reaction Monitoring) feature representing a peak group
    
    An MRMFeature represents a detected signal across multiple chromatograms in targeted proteomics
    experiments (MRM/SRM). It contains corresponding features from individual transitions, where each
    transition is represented as a Feature object. This class is essential for analyzing peak groups
    in targeted MS experiments.
    
    The MRMFeature stores:
    
    - Individual transition features (via addFeature/getFeature)
    - Precursor features for MS1 data (via addPrecursorFeature/getPrecursorFeature)
    - Quality scores for the peak group (via getScores/setScores)
    
    Example usage:
    
    .. code-block:: python
    
       mrm_feature = oms.MRMFeature()
       # Add a transition feature with its native ID
       feature = oms.Feature()
       feature.setRT(100.5)
       feature.setMZ(500.25)
       feature.setIntensity(10000.0)
       mrm_feature.addFeature(feature, "transition_1")
       # Retrieve the feature by its ID
       retrieved_feature = mrm_feature.getFeature("transition_1")
       print(retrieved_feature.getRT())  # Should print 100.5
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void MRMFeature()
        """
        ...
    
    @overload
    def __init__(self, in_0: MRMFeature ) -> None:
        """
        Cython signature: void MRMFeature(MRMFeature &)
        """
        ...
    
    def getScores(self) -> OpenSwath_Scores:
        """
        Cython signature: OpenSwath_Scores getScores()
        Returns the peak group quality scores
        
        :return: An object containing various quality metrics for the peak group, such as library correlation, signal-to-noise ratio, and other OpenSWATH scoring metrics
        """
        ...
    
    def setScores(self, s: OpenSwath_Scores ) -> None:
        """
        Cython signature: void setScores(OpenSwath_Scores s)
        Sets the peak group quality scores
        
        :param s: An OpenSwath_Scores object containing quality metrics for this peak group
        """
        ...
    
    def getFeature(self, key: Union[bytes, str, String] ) -> Feature:
        """
        Cython signature: Feature getFeature(String key)
        Retrieves a transition feature by its native ID
        
        :param key: The native ID of the transition (e.g., "transition_1" or a TRAML identifier)
        :return: The Feature object corresponding to this transition
        
        Raises an exception if the key is not found
        """
        ...
    
    def addFeature(self, f: Feature , key: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void addFeature(Feature & f, String key)
        Adds a transition feature to this MRM feature
        
        :param f: A Feature object representing the signal from a single transition chromatogram
        :param key: The native ID for this transition (should match the transition ID from your method)
        
        Each transition in an MRM experiment produces one chromatogram, which is represented as a Feature
        """
        ...
    
    def getFeatures(self) -> List[Feature]:
        """
        Cython signature: libcpp_vector[Feature] getFeatures()
        Returns all transition features in this MRM feature
        
        :return: A list of all transition features that have been added to this peak group
        """
        ...
    
    def getFeatureIDs(self, result: List[bytes] ) -> None:
        """
        Cython signature: void getFeatureIDs(libcpp_vector[String] & result)
        Retrieves the native IDs of all transition features
        
        :param result: Output parameter that will be filled with the native IDs of all transitions
        
        This is an output parameter. Pass an empty list and it will be populated with IDs
        """
        ...
    
    def getPrecursorFeature(self, key: Union[bytes, str, String] ) -> Feature:
        """
        Cython signature: Feature getPrecursorFeature(String key)
        Retrieves a precursor feature by its native ID
        
        :param key: The native ID of the precursor
        :return: The Feature object for the precursor (MS1 signal)
        
        Precursor features represent the MS1 signal for the peptide, if available
        """
        ...
    
    def addPrecursorFeature(self, f: Feature , key: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void addPrecursorFeature(Feature & f, String key)
        Adds a precursor feature to this MRM feature
        
        :param f: A Feature object representing the MS1 precursor signal
        :param key: The native ID for this precursor
        
        Precursor features are optional and represent MS1-level information
        """
        ...
    
    def getPrecursorFeatureIDs(self, result: List[bytes] ) -> None:
        """
        Cython signature: void getPrecursorFeatureIDs(libcpp_vector[String] & result)
        Retrieves the native IDs of all precursor features
        
        :param result: Output parameter that will be filled with precursor IDs
        
        This is an output parameter. Pass an empty list and it will be populated with IDs
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
    
    def __richcmp__(self, other: MRMFeature, op: int) -> Any:
        ... 


class MRMIonSeries:
    """
    Cython implementation of _MRMIonSeries

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1MRMIonSeries.html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void MRMIonSeries()
        """
        ...
    
    @overload
    def __init__(self, in_0: MRMIonSeries ) -> None:
        """
        Cython signature: void MRMIonSeries(MRMIonSeries &)
        """
        ...
    
    def annotateTransitionCV(self, tr: ReactionMonitoringTransition , annotation: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void annotateTransitionCV(ReactionMonitoringTransition & tr, String annotation)
        Annotates transition with CV terms
        
        
        :param tr: The transition to annotate
        :param annotation: The fragment ion annotation
        """
        ...
    
    def annotateTransition(self, tr: ReactionMonitoringTransition , peptide: Peptide , precursor_mz_threshold: float , product_mz_threshold: float , enable_reannotation: bool , fragment_types: List[bytes] , fragment_charges: List[int] , enable_specific_losses: bool , enable_unspecific_losses: bool , round_decPow: int ) -> None:
        """
        Cython signature: void annotateTransition(ReactionMonitoringTransition & tr, Peptide peptide, double precursor_mz_threshold, double product_mz_threshold, bool enable_reannotation, libcpp_vector[String] fragment_types, libcpp_vector[size_t] fragment_charges, bool enable_specific_losses, bool enable_unspecific_losses, int round_decPow)
        Annotates transition
        
        
        :param tr: The transition to annotate
        :param peptide: The corresponding peptide
        :param precursor_mz_threshold: The m/z threshold for annotation of the precursor ion
        :param product_mz_threshold: The m/z threshold for annotation of the fragment ion
        :param enable_reannotation: Whether the original (e.g. SpectraST) annotation should be used or reannotation should be conducted
        :param fragment_types: The fragment ion types for reannotation
        :param fragment_charges: The fragment ion charges for reannotation
        :param enable_specific_losses: Whether specific neutral losses should be considered
        :param enable_unspecific_losses: Whether unspecific neutral losses (H2O1, H3N1, C1H2N2, C1H2N1O1) should be considered
        :param round_decPow: Round precursor and product m/z values to decimal power (default: -4)
        """
        ... 


class MRMRTNormalizer:
    """
    Cython implementation of _MRMRTNormalizer

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1MRMRTNormalizer.html>`_
    """
    
    chauvenet: __static_MRMRTNormalizer_chauvenet
    
    chauvenet_probability: __static_MRMRTNormalizer_chauvenet_probability
    
    computeBinnedCoverage: __static_MRMRTNormalizer_computeBinnedCoverage
    
    removeOutliersIterative: __static_MRMRTNormalizer_removeOutliersIterative
    
    removeOutliersRANSAC: __static_MRMRTNormalizer_removeOutliersRANSAC 


class MSDataStoringConsumer:
    """
    Cython implementation of _MSDataStoringConsumer

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1MSDataStoringConsumer.html>`_

    Consumer class that simply stores the data
    
    This class is able to keep spectra and chromatograms passed to it in memory
    and the data can be accessed through getData()
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void MSDataStoringConsumer()
        """
        ...
    
    @overload
    def __init__(self, in_0: MSDataStoringConsumer ) -> None:
        """
        Cython signature: void MSDataStoringConsumer(MSDataStoringConsumer &)
        """
        ...
    
    def setExperimentalSettings(self, exp: ExperimentalSettings ) -> None:
        """
        Cython signature: void setExperimentalSettings(ExperimentalSettings & exp)
        Sets experimental settings
        """
        ...
    
    def setExpectedSize(self, expectedSpectra: int , expectedChromatograms: int ) -> None:
        """
        Cython signature: void setExpectedSize(size_t expectedSpectra, size_t expectedChromatograms)
        Sets expected size
        """
        ...
    
    def consumeSpectrum(self, s: MSSpectrum ) -> None:
        """
        Cython signature: void consumeSpectrum(MSSpectrum & s)
        """
        ...
    
    def consumeChromatogram(self, in_0: MSChromatogram ) -> None:
        """
        Cython signature: void consumeChromatogram(MSChromatogram &)
        """
        ...
    
    def getData(self) -> MSExperiment:
        """
        Cython signature: MSExperiment getData()
        """
        ... 


class MapAlignmentAlgorithmIdentification:
    """
    Cython implementation of _MapAlignmentAlgorithmIdentification

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1MapAlignmentAlgorithmIdentification.html>`_
      -- Inherits from ['DefaultParamHandler', 'ProgressLogger']
    """
    
    def __init__(self) -> None:
        """
        Cython signature: void MapAlignmentAlgorithmIdentification()
        """
        ...
    
    @overload
    def align(self, in_0: List[FeatureMap] , in_1: List[TransformationDescription] , in_2: int ) -> None:
        """
        Cython signature: void align(const libcpp_vector[FeatureMap] &, libcpp_vector[TransformationDescription] &, int)
        """
        ...
    
    @overload
    def align(self, in_0: List[ConsensusMap] , in_1: List[TransformationDescription] , in_2: int ) -> None:
        """
        Cython signature: void align(const libcpp_vector[ConsensusMap] &, libcpp_vector[TransformationDescription] &, int)
        """
        ...
    
    @overload
    def setReference(self, in_0: FeatureMap ) -> None:
        """
        Cython signature: void setReference(FeatureMap &)
        """
        ...
    
    @overload
    def setReference(self, in_0: ConsensusMap ) -> None:
        """
        Cython signature: void setReference(ConsensusMap &)
        """
        ...
    
    @overload
    def setReference(self, in_0: PeptideIdentificationList ) -> None:
        """
        Cython signature: void setReference(PeptideIdentificationList &)
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


class MapAlignmentAlgorithmKD:
    """
    Cython implementation of _MapAlignmentAlgorithmKD

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1MapAlignmentAlgorithmKD.html>`_

    An efficient reference-free feature map alignment algorithm for unlabeled data
    
    This algorithm uses a kd-tree to efficiently compute conflict-free connected components (CCC)
    in a compatibility graph on feature data. This graph is comprised of nodes corresponding
    to features and edges connecting features f and f' iff both are within each other's tolerance
    windows (wrt. RT and m/z difference). CCCs are those CCs that do not contain multiple features
    from the same input map, and whose features all have the same charge state
    
    All CCCs above a user-specified minimum size are considered true sets of corresponding features
    and based on these, LOWESS transformations are computed for each input map such that the average
    deviation from the mean retention time within all CCCs is minimized
    """
    
    @overload
    def __init__(self, num_maps: int , param: Param ) -> None:
        """
        Cython signature: void MapAlignmentAlgorithmKD(size_t num_maps, Param & param)
        """
        ...
    
    @overload
    def __init__(self, in_0: MapAlignmentAlgorithmKD ) -> None:
        """
        Cython signature: void MapAlignmentAlgorithmKD(MapAlignmentAlgorithmKD &)
        """
        ...
    
    def addRTFitData(self, kd_data: KDTreeFeatureMaps ) -> None:
        """
        Cython signature: void addRTFitData(KDTreeFeatureMaps & kd_data)
        Compute data points needed for RT transformation in the current `kd_data`, add to `fit_data_`
        """
        ...
    
    def fitLOWESS(self) -> None:
        """
        Cython signature: void fitLOWESS()
        Fit LOWESS to fit_data_, store final models in `transformations_`
        """
        ...
    
    def transform(self, kd_data: KDTreeFeatureMaps ) -> None:
        """
        Cython signature: void transform(KDTreeFeatureMaps & kd_data)
        Transform RTs for `kd_data`
        """
        ... 


class MapAlignmentEvaluationAlgorithmRecall:
    """
    Cython implementation of _MapAlignmentEvaluationAlgorithmRecall

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1MapAlignmentEvaluationAlgorithmRecall.html>`_
      -- Inherits from ['MapAlignmentEvaluationAlgorithm']
    """
    
    def __init__(self) -> None:
        """
        Cython signature: void MapAlignmentEvaluationAlgorithmRecall()
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


class MetaInfoDescription:
    """
    Cython implementation of _MetaInfoDescription

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1MetaInfoDescription.html>`_
      -- Inherits from ['MetaInfoInterface']
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void MetaInfoDescription()
        """
        ...
    
    @overload
    def __init__(self, in_0: MetaInfoDescription ) -> None:
        """
        Cython signature: void MetaInfoDescription(MetaInfoDescription &)
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
    
    def __richcmp__(self, other: MetaInfoDescription, op: int) -> Any:
        ... 


class MetaInfoRegistry:
    """
    Cython implementation of _MetaInfoRegistry

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1MetaInfoRegistry.html>`_

    Registry which assigns unique integer indices to strings
    
    When registering a new name an index >= 1024 is assigned.
    Indices from 1 to 1023 are reserved for fast access and will never change:
    1 - isotopic_range
    2 - cluster_id
    3 - label
    4 - icon
    5 - color
    6 - RT
    7 - MZ
    8 - predicted_RT
    9 - predicted_RT_p_value
    10 - spectrum_reference
    11 - ID
    12 - low_quality
    13 - charge
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void MetaInfoRegistry()
        """
        ...
    
    @overload
    def __init__(self, in_0: MetaInfoRegistry ) -> None:
        """
        Cython signature: void MetaInfoRegistry(MetaInfoRegistry &)
        """
        ...
    
    def registerName(self, name: Union[bytes, str, String] , description: Union[bytes, str, String] , unit: Union[bytes, str, String] ) -> int:
        """
        Cython signature: unsigned int registerName(const String & name, const String & description, const String & unit)
        Registers a string, stores its description and unit, and returns the corresponding index. If the string is already registered, it returns the index of the string
        """
        ...
    
    @overload
    def setDescription(self, index: int , description: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setDescription(unsigned int index, const String & description)
        Sets the description (String), corresponding to an index
        """
        ...
    
    @overload
    def setDescription(self, name: Union[bytes, str, String] , description: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setDescription(const String & name, const String & description)
        Sets the description (String), corresponding to a name
        """
        ...
    
    @overload
    def setUnit(self, index: int , unit: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setUnit(unsigned int index, const String & unit)
        Sets the unit (String), corresponding to an index
        """
        ...
    
    @overload
    def setUnit(self, name: Union[bytes, str, String] , unit: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setUnit(const String & name, const String & unit)
        Sets the unit (String), corresponding to a name
        """
        ...
    
    def getIndex(self, name: Union[bytes, str, String] ) -> int:
        """
        Cython signature: unsigned int getIndex(const String & name)
        Returns the integer index corresponding to a string. If the string is not registered, returns UInt(-1) (= UINT_MAX)
        """
        ...
    
    def getName(self, index: int ) -> Union[bytes, str, String]:
        """
        Cython signature: String getName(unsigned int index)
        Returns the corresponding name to an index
        """
        ...
    
    @overload
    def getDescription(self, index: int ) -> Union[bytes, str, String]:
        """
        Cython signature: String getDescription(unsigned int index)
        Returns the description of an index
        """
        ...
    
    @overload
    def getDescription(self, name: Union[bytes, str, String] ) -> Union[bytes, str, String]:
        """
        Cython signature: String getDescription(const String & name)
        Returns the description of a name
        """
        ...
    
    @overload
    def getUnit(self, index: int ) -> Union[bytes, str, String]:
        """
        Cython signature: String getUnit(unsigned int index)
        Returns the unit of an index
        """
        ...
    
    @overload
    def getUnit(self, name: Union[bytes, str, String] ) -> Union[bytes, str, String]:
        """
        Cython signature: String getUnit(const String & name)
        Returns the unit of a name
        """
        ... 


class Mobilogram:
    """
    Cython implementation of _Mobilogram

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1Mobilogram.html>`_
      -- Inherits from ['RangeManagerMobInt']

    The representation of a 1D ion mobilogram.
    Raw data access is proved by `get_peaks` and `set_peaks`, which yields numpy arrays
    Iterations yields access to underlying peak objects but is slower
    Extra data arrays can be accessed through getFloatDataArrays / getIntegerDataArrays / getStringDataArrays
    
    Usage:
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void Mobilogram()
        """
        ...
    
    @overload
    def __init__(self, in_0: Mobilogram ) -> None:
        """
        Cython signature: void Mobilogram(Mobilogram &)
        """
        ...
    
    def getRT(self) -> float:
        """
        Cython signature: double getRT()
        Returns the retention time (in seconds)
        """
        ...
    
    def setRT(self, in_0: float ) -> None:
        """
        Cython signature: void setRT(double)
        Sets the retention time (in seconds)
        """
        ...
    
    def getDriftTimeUnit(self) -> int:
        """
        Cython signature: DriftTimeUnit getDriftTimeUnit()
        Returns the ion mobility drift time unit
        """
        ...
    
    def getDriftTimeUnitAsString(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getDriftTimeUnitAsString()
        Returns the ion mobility drift time unit as string
        """
        ...
    
    def setDriftTimeUnit(self, dt: int ) -> None:
        """
        Cython signature: void setDriftTimeUnit(DriftTimeUnit dt)
        Sets the ion mobility drift time unit
        """
        ...
    
    def size(self) -> int:
        """
        Cython signature: size_t size()
        Returns the number of peaks in the mobilogram
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
    
    def __getitem__(self, in_0: int ) -> MobilityPeak1D:
        """
        Cython signature: MobilityPeak1D & operator[](size_t)
        """
        ...
    def __setitem__(self, key: int, value: MobilityPeak1D) -> None:
        """Cython signature: MobilityPeak1D & operator[](size_t)"""
        ...
    
    def updateRanges(self) -> None:
        """
        Cython signature: void updateRanges()
        """
        ...
    
    def clear(self) -> None:
        """
        Cython signature: void clear()
        Clears all data and ranges
        
        Will delete (clear) all peaks contained in the mobilogram
        """
        ...
    
    def push_back(self, in_0: MobilityPeak1D ) -> None:
        """
        Cython signature: void push_back(MobilityPeak1D)
        Append a peak
        """
        ...
    
    def isSorted(self) -> bool:
        """
        Cython signature: bool isSorted()
        Checks if all peaks are sorted with respect to ascending mobility
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
        Lexicographically sorts the peaks by their position (mobility)
        
        
        The mobilogram is sorted with respect to position (mobility). Meta data arrays will be sorted accordingly
        """
        ...
    
    def findNearest(self, in_0: float ) -> int:
        """
        Cython signature: int findNearest(double)
        Binary search for the peak nearest to a specific mobility
        :note: Make sure the mobilogram is sorted with respect to mobility! Otherwise the result is undefined
        
        
        :param mb: The searched for mobility value
        :return: Returns the index of the peak.
        :raises:
          Exception: Precondition is thrown if the mobilogram is empty (not only in debug mode)
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
    
    def calculateTIC(self) -> float:
        """
        Cython signature: float calculateTIC()
        Compute the total ion count (sum of all peak intensities)
        """
        ...
    
    def getMinMobility(self) -> float:
        """
        Cython signature: double getMinMobility()
        Returns the minimum mobility
        """
        ...
    
    def getMaxMobility(self) -> float:
        """
        Cython signature: double getMaxMobility()
        Returns the maximum mobility
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
    
    def __iter__(self) -> MobilityPeak1D:
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


class MorphologicalFilter:
    """
    Cython implementation of _MorphologicalFilter

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1MorphologicalFilter.html>`_
      -- Inherits from ['DefaultParamHandler', 'ProgressLogger']
    """
    
    def __init__(self) -> None:
        """
        Cython signature: void MorphologicalFilter()
        """
        ...
    
    def filter(self, spectrum: MSSpectrum ) -> None:
        """
        Cython signature: void filter(MSSpectrum & spectrum)
        Applies the morphological filtering operation to an MSSpectrum
        
        If the size of the structuring element is given in 'Thomson', the number of data points for
        the structuring element is computed as follows:
        """
        ...
    
    def filterExperiment(self, exp: MSExperiment ) -> None:
        """
        Cython signature: void filterExperiment(MSExperiment & exp)
        Applies the morphological filtering operation to an MSExperiment
        
        The size of the structuring element is computed for each spectrum individually, if it is given in 'Thomson'
        See the filtering method for MSSpectrum for details
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


class Normalizer:
    """
    Cython implementation of _Normalizer

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1Normalizer.html>`_
      -- Inherits from ['DefaultParamHandler']

    Normalizes the peak intensities spectrum-wise
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void Normalizer()
        """
        ...
    
    @overload
    def __init__(self, in_0: Normalizer ) -> None:
        """
        Cython signature: void Normalizer(Normalizer)
        """
        ...
    
    def filterSpectrum(self, spec: MSSpectrum ) -> None:
        """
        Cython signature: void filterSpectrum(MSSpectrum & spec)
        Normalizes the spectrum
        """
        ...
    
    def filterPeakSpectrum(self, spec: MSSpectrum ) -> None:
        """
        Cython signature: void filterPeakSpectrum(MSSpectrum & spec)
        Normalizes the peak spectrum
        """
        ...
    
    def filterPeakMap(self, exp: MSExperiment ) -> None:
        """
        Cython signature: void filterPeakMap(MSExperiment & exp)
        Normalizes the peak map
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


class OSSpectrumMeta:
    """
    Cython implementation of _OSSpectrumMeta

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenSwath_1_1OSSpectrumMeta.html>`_
    """
    
    index: int
    
    id: bytes
    
    RT: float
    
    ms_level: int
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void OSSpectrumMeta()
        """
        ...
    
    @overload
    def __init__(self, in_0: OSSpectrumMeta ) -> None:
        """
        Cython signature: void OSSpectrumMeta(OSSpectrumMeta &)
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


class OpenSwathScoring:
    """
    Cython implementation of _OpenSwathScoring

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1OpenSwathScoring.html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void OpenSwathScoring()
        """
        ...
    
    @overload
    def __init__(self, in_0: OpenSwathScoring ) -> None:
        """
        Cython signature: void OpenSwathScoring(OpenSwathScoring &)
        """
        ...
    
    def initialize(self, rt_normalization_factor: float , add_up_spectra: int , spacing_for_spectra_resampling: float , merge_spectra_by_peak_width_fraction: float , drift_extra: float , su: OpenSwath_Scores_Usage , spectrum_addition_method: bytes , spectrum_merge_method_type: bytes , use_ms1_ion_mobility: bool , apply_im_peak_picking: bool ) -> None:
        """
        Cython signature: void initialize(double rt_normalization_factor, int add_up_spectra, double spacing_for_spectra_resampling, double merge_spectra_by_peak_width_fraction, double drift_extra, OpenSwath_Scores_Usage su, libcpp_string spectrum_addition_method, libcpp_string spectrum_merge_method_type, bool use_ms1_ion_mobility, bool apply_im_peak_picking)
        Initialize the scoring object\n
        Sets the parameters for the scoring
        
        
        :param rt_normalization_factor: Specifies the range of the normalized retention time space
        :param add_up_spectra: How many spectra to add up (default 1)
        :param spacing_for_spectra_resampling: Spacing factor for spectra addition
        :param merge_spectra_by_peak_width_fraction: Fraction of peak width to construct the number of spectra to add
        :param drift_extra: Extend the extraction window to gain a larger field of view beyond drift_upper - drift_lower (in percent)
        :param su: Which scores to actually compute
        :param spectrum_addition_method: Method to use for spectrum addition (valid: "simple", "resample")
        :param spectrum_merge_method_type: Type of method to use for spectrum addition. (valid: "fixed", "dynamic")
        :param use_ms1_ion_mobility: Use MS1 ion mobility extraction in DIA scores
        :param apply_im_peak_picking: Apply peak picking to the  extracted ion mobilograms
        """
        ...
    
    def getNormalized_library_intensities_(self, transitions: List[LightTransition] , normalized_library_intensity: List[float] ) -> None:
        """
        Cython signature: void getNormalized_library_intensities_(libcpp_vector[LightTransition] transitions, libcpp_vector[double] normalized_library_intensity)
        """
        ... 


class OpenSwath_Scores:
    """
    Cython implementation of _OpenSwath_Scores

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1OpenSwath_Scores.html>`_
    """
    
    elution_model_fit_score: float
    
    library_corr: float
    
    library_norm_manhattan: float
    
    library_rootmeansquare: float
    
    library_sangle: float
    
    norm_rt_score: float
    
    isotope_correlation: float
    
    isotope_overlap: float
    
    massdev_score: float
    
    xcorr_coelution_score: float
    
    xcorr_shape_score: float
    
    yseries_score: float
    
    bseries_score: float
    
    log_sn_score: float
    
    weighted_coelution_score: float
    
    weighted_xcorr_shape: float
    
    weighted_massdev_score: float
    
    ms1_xcorr_coelution_score: float
    
    ms1_xcorr_coelution_contrast_score: float
    
    ms1_xcorr_coelution_combined_score: float
    
    ms1_xcorr_shape_score: float
    
    ms1_xcorr_shape_contrast_score: float
    
    ms1_xcorr_shape_combined_score: float
    
    ms1_ppm_score: float
    
    ms1_isotope_correlation: float
    
    ms1_isotope_overlap: float
    
    ms1_mi_score: float
    
    ms1_mi_contrast_score: float
    
    ms1_mi_combined_score: float
    
    library_manhattan: float
    
    library_dotprod: float
    
    intensity: float
    
    total_xic: float
    
    nr_peaks: float
    
    sn_ratio: float
    
    mi_score: float
    
    weighted_mi_score: float
    
    rt_difference: float
    
    normalized_experimental_rt: float
    
    raw_rt_score: float
    
    dotprod_score_dia: float
    
    manhatt_score_dia: float
    
    def __init__(self) -> None:
        """
        Cython signature: void OpenSwath_Scores()
        """
        ...
    
    def get_quick_lda_score(self, library_corr_: float , library_norm_manhattan_: float , norm_rt_score_: float , xcorr_coelution_score_: float , xcorr_shape_score_: float , log_sn_score_: float ) -> float:
        """
        Cython signature: double get_quick_lda_score(double library_corr_, double library_norm_manhattan_, double norm_rt_score_, double xcorr_coelution_score_, double xcorr_shape_score_, double log_sn_score_)
        """
        ...
    
    def calculate_lda_prescore(self, scores: OpenSwath_Scores ) -> float:
        """
        Cython signature: double calculate_lda_prescore(OpenSwath_Scores scores)
        """
        ...
    
    def calculate_swath_lda_prescore(self, scores: OpenSwath_Scores ) -> float:
        """
        Cython signature: double calculate_swath_lda_prescore(OpenSwath_Scores scores)
        """
        ... 


class OpenSwath_Scores_Usage:
    """
    Cython implementation of _OpenSwath_Scores_Usage

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1OpenSwath_Scores_Usage.html>`_
    """
    
    use_coelution_score_: bool
    
    use_shape_score_: bool
    
    use_rt_score_: bool
    
    use_library_score_: bool
    
    use_elution_model_score_: bool
    
    use_intensity_score_: bool
    
    use_total_xic_score_: bool
    
    use_total_mi_score_: bool
    
    use_nr_peaks_score_: bool
    
    use_sn_score_: bool
    
    use_mi_score_: bool
    
    use_dia_scores_: bool
    
    use_ms1_correlation: bool
    
    use_ms1_fullscan: bool
    
    use_ms1_mi: bool
    
    use_uis_scores: bool
    
    def __init__(self) -> None:
        """
        Cython signature: void OpenSwath_Scores_Usage()
        """
        ... 


class ParamCTDFile:
    """
    Cython implementation of _ParamCTDFile

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1ParamCTDFile.html>`_
    """
    
    def __init__(self) -> None:
        """
        Cython signature: void ParamCTDFile()
        """
        ...
    
    def store(self, filename: Union[bytes, str] , param: Param , tool_info: ToolInfo ) -> None:
        """
        Cython signature: void store(libcpp_utf8_string filename, Param param, ToolInfo tool_info)
        """
        ... 


class PeakTypeEstimator:
    """
    Cython implementation of _PeakTypeEstimator

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1PeakTypeEstimator.html>`_

    Estimates if the data of a spectrum is raw data or peak data
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void PeakTypeEstimator()
        """
        ...
    
    @overload
    def __init__(self, in_0: PeakTypeEstimator ) -> None:
        """
        Cython signature: void PeakTypeEstimator(PeakTypeEstimator &)
        """
        ... 


class PeptideAndProteinQuant:
    """
    Cython implementation of _PeptideAndProteinQuant

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1PeptideAndProteinQuant.html>`_
      -- Inherits from ['DefaultParamHandler']
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void PeptideAndProteinQuant()
        Helper class for peptide and protein quantification based on feature data annotated with IDs
        """
        ...
    
    @overload
    def __init__(self, in_0: PeptideAndProteinQuant ) -> None:
        """
        Cython signature: void PeptideAndProteinQuant(PeptideAndProteinQuant &)
        """
        ...
    
    @overload
    def readQuantData(self, map_in: FeatureMap , ed: ExperimentalDesign ) -> None:
        """
        Cython signature: void readQuantData(FeatureMap & map_in, ExperimentalDesign & ed)
        Read quantitative data from a feature map
        
        Parameters should be set before using this method, as setting parameters will clear all results
        """
        ...
    
    @overload
    def readQuantData(self, map_in: ConsensusMap , ed: ExperimentalDesign ) -> None:
        """
        Cython signature: void readQuantData(ConsensusMap & map_in, ExperimentalDesign & ed)
        Read quantitative data from a consensus map
        
        Parameters should be set before using this method, as setting parameters will clear all results
        """
        ...
    
    @overload
    def readQuantData(self, proteins: List[ProteinIdentification] , peptides: PeptideIdentificationList , ed: ExperimentalDesign ) -> None:
        """
        Cython signature: void readQuantData(libcpp_vector[ProteinIdentification] & proteins, PeptideIdentificationList & peptides, ExperimentalDesign & ed)
        Read quantitative data from identification results (for quantification via spectral counting)
        
        Parameters should be set before using this method, as setting parameters will clear all results
        """
        ...
    
    def quantifyPeptides(self, peptides: PeptideIdentificationList ) -> None:
        """
        Cython signature: void quantifyPeptides(PeptideIdentificationList & peptides)
        Compute peptide abundances
        
        Based on quantitative data for individual charge states (in member `pep_quant_`), overall abundances for peptides are computed (and stored again in `pep_quant_`)
        Quantitative data must first be read via readQuantData()
        Optional (peptide-level) protein inference information (e.g. from Fido or ProteinProphet) can be supplied via `peptides`. In that case, peptide-to-protein associations - the basis for protein-level quantification - will also be read from `peptides`!
        """
        ...
    
    def quantifyProteins(self, proteins: ProteinIdentification ) -> None:
        """
        Cython signature: void quantifyProteins(ProteinIdentification & proteins)
        Compute protein abundances
        
        Peptide abundances must be computed first with quantifyPeptides(). Optional protein inference information (e.g. from Fido or ProteinProphet) can be supplied via `proteins`
        """
        ...
    
    def getStatistics(self) -> PeptideAndProteinQuant_Statistics:
        """
        Cython signature: PeptideAndProteinQuant_Statistics getStatistics()
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


class PeptideAndProteinQuant_PeptideData:
    """
    Cython implementation of _PeptideAndProteinQuant_PeptideData

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1PeptideAndProteinQuant_PeptideData.html>`_
    """
    
    accessions: Set[bytes]
    
    psm_count: int
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void PeptideAndProteinQuant_PeptideData()
        """
        ...
    
    @overload
    def __init__(self, in_0: PeptideAndProteinQuant_PeptideData ) -> None:
        """
        Cython signature: void PeptideAndProteinQuant_PeptideData(PeptideAndProteinQuant_PeptideData &)
        """
        ... 


class PeptideAndProteinQuant_ProteinData:
    """
    Cython implementation of _PeptideAndProteinQuant_ProteinData

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1PeptideAndProteinQuant_ProteinData.html>`_
    """
    
    psm_count: int
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void PeptideAndProteinQuant_ProteinData()
        """
        ...
    
    @overload
    def __init__(self, in_0: PeptideAndProteinQuant_ProteinData ) -> None:
        """
        Cython signature: void PeptideAndProteinQuant_ProteinData(PeptideAndProteinQuant_ProteinData &)
        """
        ... 


class PeptideAndProteinQuant_Statistics:
    """
    Cython implementation of _PeptideAndProteinQuant_Statistics

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1PeptideAndProteinQuant_Statistics.html>`_
    """
    
    n_samples: int
    
    quant_proteins: int
    
    too_few_peptides: int
    
    quant_peptides: int
    
    total_peptides: int
    
    quant_features: int
    
    total_features: int
    
    blank_features: int
    
    ambig_features: int
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void PeptideAndProteinQuant_Statistics()
        """
        ...
    
    @overload
    def __init__(self, in_0: PeptideAndProteinQuant_Statistics ) -> None:
        """
        Cython signature: void PeptideAndProteinQuant_Statistics(PeptideAndProteinQuant_Statistics &)
        """
        ... 


class PeptideProteinResolution:
    """
    Cython implementation of _PeptideProteinResolution

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1PeptideProteinResolution.html>`_

    Resolves shared peptides based on protein scores
    
    Resolves connected components of the bipartite protein-peptide graph based
    on protein probabilities/scores and adds them as additional protein_groups
    to the protein identification run processed.
    Thereby greedily assigns shared peptides in this component uniquely to the
    proteins of the current @em best @em indistinguishable protein group, until
    every peptide is uniquely assigned. This effectively allows more peptides to
    be used in ProteinQuantifier at the cost of potentially additional noise in
    the peptides quantities.
    In accordance with most state-of-the-art protein inference tools, only the
    best hit (PSM) for a peptide ID is considered.  Probability ties are
    currently resolved by taking the protein with larger number of peptides
    
    The class could provide iterator for ConnectedComponents in the
    future. One could extend the graph to include all PeptideHits (not only the
    best). It becomes a tripartite graph with larger connected components then.
    Maybe extend it to work with MS1 features. Separate resolution and adding
    groups to output
    """
    
    @overload
    def __init__(self, statistics: bool ) -> None:
        """
        Cython signature: void PeptideProteinResolution(bool statistics)
        """
        ...
    
    @overload
    def __init__(self, in_0: PeptideProteinResolution ) -> None:
        """
        Cython signature: void PeptideProteinResolution(PeptideProteinResolution &)
        """
        ...
    
    def buildGraph(self, protein: ProteinIdentification , peptides: PeptideIdentificationList ) -> None:
        """
        Cython signature: void buildGraph(ProteinIdentification & protein, PeptideIdentificationList & peptides)
        Initialize and store the graph (= maps), needs sorted groups for
        correct functionality. Therefore sorts the indist. protein groups
        if not skipped
        
        
        :param protein: ProteinIdentification object storing IDs and groups
        :param peptides: Vector of ProteinIdentifications with links to the proteins
        :param skip_sort: Skips sorting of groups, nothing is modified then
        """
        ...
    
    def resolveGraph(self, protein: ProteinIdentification , peptides: PeptideIdentificationList ) -> None:
        """
        Cython signature: void resolveGraph(ProteinIdentification & protein, PeptideIdentificationList & peptides)
        Applies resolveConnectedComponent to every component of the graph and
        is able to write statistics when specified. Parameters will
        both be mutated in this method
        
        
        :param protein: ProteinIdentification object storing IDs and groups
        :param peptides: vector of ProteinIdentifications with links to the proteins
        """
        ...
    
    def findConnectedComponent(self, root_prot_grp: int ) -> PeptideProteinResolution_ConnectedComponent:
        """
        Cython signature: PeptideProteinResolution_ConnectedComponent findConnectedComponent(size_t & root_prot_grp)
        Does a BFS on the two maps (= two parts of the graph; indist. prot. groups
        and peptides), switching from one to the other in each step
        
        
        :param root_prot_grp: Starts the BFS at this protein group index
        :return: Returns a Connected Component as set of group and peptide indices
        """
        ...
    
    def resolveConnectedComponent(self, conn_comp: PeptideProteinResolution_ConnectedComponent , protein: ProteinIdentification , peptides: PeptideIdentificationList ) -> None:
        """
        Cython signature: void resolveConnectedComponent(PeptideProteinResolution_ConnectedComponent & conn_comp, ProteinIdentification & protein, PeptideIdentificationList & peptides)
        Resolves connected components based on posterior probabilities and adds them
        as additional protein_groups to the output idXML.
        Thereby greedily assigns shared peptides in this component uniquely to
        the proteins of the current BEST INDISTINGUISHABLE protein group,
        ready to be used in ProteinQuantifier then.
        This is achieved by removing all other evidence from the input
        PeptideIDs and iterating until each peptide is uniquely assigned.
        In accordance with Fido only the best hit (PSM) for an ID is considered.
        Probability ties resolved by taking protein with largest number of peptides
        
        
        :param conn_comp: The component to be resolved
        :param protein: ProteinIdentification object storing IDs and groups
        :param peptides: Vector of ProteinIdentifications with links to the proteins
        """
        ...
    
    run: __static_PeptideProteinResolution_run 


class PeptideProteinResolution_ConnectedComponent:
    """
    Cython implementation of _PeptideProteinResolution_ConnectedComponent

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1PeptideProteinResolution_ConnectedComponent.html>`_
    """
    
    prot_grp_indices: Set[int]
    
    pep_indices: Set[int]
    
    def __init__(self) -> None:
        """
        Cython signature: void PeptideProteinResolution_ConnectedComponent()
        """
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


class Product:
    """
    Cython implementation of _Product

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1Product.html>`_

    This class describes the product isolation window for special scan types, such as MRM
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void Product()
        """
        ...
    
    @overload
    def __init__(self, in_0: Product ) -> None:
        """
        Cython signature: void Product(Product &)
        """
        ...
    
    def getMZ(self) -> float:
        """
        Cython signature: double getMZ()
        Returns the target m/z
        """
        ...
    
    def setMZ(self, in_0: float ) -> None:
        """
        Cython signature: void setMZ(double)
        Sets the target m/z
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
    
    def __richcmp__(self, other: Product, op: int) -> Any:
        ... 


class ProteinHit:
    """
    Cython implementation of _ProteinHit

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1ProteinHit.html>`_
      -- Inherits from ['MetaInfoInterface']

    Represents a single protein identification hit from a database search
    
    A ProteinHit stores information about a protein that was identified based on
    peptide evidence. Each hit contains:
    
    - Protein accession (database identifier)
    - Score from protein inference
    - Rank among protein candidates
    - Protein sequence (optional)
    - Sequence coverage percentage
    
    Multiple ProteinHit objects are stored in a ProteinIdentification, typically
    sorted by score to show the most confident identifications first.
    
    Example usage:
    
    .. code-block:: python
    
       protein_hit = oms.ProteinHit()
       protein_hit.setAccession("P12345")
       protein_hit.setScore(150.5)
       protein_hit.setRank(1)
       protein_hit.setCoverage(45.2)  # 45.2% coverage
       protein_hit.setDescription("Example protein")
       # Access information
       print(f"Accession: {protein_hit.getAccession()}")
       print(f"Score: {protein_hit.getScore()}, Coverage: {protein_hit.getCoverage()}%")
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void ProteinHit()
        """
        ...
    
    @overload
    def __init__(self, score: float , rank: int , accession: Union[bytes, str, String] , sequence: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void ProteinHit(double score, unsigned int rank, String accession, String sequence)
        """
        ...
    
    @overload
    def __init__(self, in_0: ProteinHit ) -> None:
        """
        Cython signature: void ProteinHit(ProteinHit &)
        """
        ...
    
    def getScore(self) -> float:
        """
        Cython signature: float getScore()
        Returns the protein inference score
        
        :return: Score from protein inference algorithm
        """
        ...
    
    def getRank(self) -> int:
        """
        Cython signature: unsigned int getRank()
        Returns the rank of this protein hit
        
        :return: Rank (1 = best hit, 2 = second best, etc.)
        """
        ...
    
    def getSequence(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getSequence()
        Returns the protein sequence
        
        :return: Full amino acid sequence of the protein (if available)
        """
        ...
    
    def getAccession(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getAccession()
        Returns the protein accession
        
        :return: Database accession/identifier (e.g., "P12345" for UniProt)
        """
        ...
    
    def getDescription(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getDescription()
        Returns the protein description
        
        :return: Human-readable protein name/description from database
        """
        ...
    
    def getCoverage(self) -> float:
        """
        Cython signature: double getCoverage()
        Returns the sequence coverage percentage
        
        :return: Percentage of protein sequence covered by identified peptides
        
        Value is in range 0-100 (e.g., 45.2 means 45.2% coverage)
        """
        ...
    
    def setScore(self, in_0: float ) -> None:
        """
        Cython signature: void setScore(float)
        Sets the protein inference score
        
        :param score: Score to set
        """
        ...
    
    def setRank(self, in_0: int ) -> None:
        """
        Cython signature: void setRank(unsigned int)
        Sets the rank
        
        :param rank: Rank among all protein candidates
        """
        ...
    
    def setSequence(self, in_0: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setSequence(String)
        Sets the protein sequence
        
        :param sequence: Full amino acid sequence
        """
        ...
    
    def setAccession(self, in_0: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setAccession(String)
        Sets the protein accession
        
        :param accession: Database accession/identifier
        """
        ...
    
    def setDescription(self, description: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setDescription(String description)
        Sets the protein description
        
        :param description: Human-readable protein name/description
        """
        ...
    
    def setCoverage(self, in_0: float ) -> None:
        """
        Cython signature: void setCoverage(double)
        Sets the sequence coverage percentage
        
        :param coverage: Percentage (0-100) of sequence covered by peptides
        """
        ...
    
    def isDecoy(self) -> bool:
        """
        Cython signature: bool isDecoy()
        Checks if this is a decoy protein hit
        
        :return: True if this is a decoy hit from target-decoy search
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
    
    def __richcmp__(self, other: ProteinHit, op: int) -> Any:
        ... 


class ProteinProteinCrossLink:
    """
    Cython implementation of _ProteinProteinCrossLink

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS::OPXLDataStructs_1_1ProteinProteinCrossLink.html>`_
    """
    
    alpha: AASequence
    
    beta: AASequence
    
    cross_link_position: List[int, int]
    
    cross_linker_mass: float
    
    cross_linker_name: Union[bytes, str, String]
    
    term_spec_alpha: int
    
    term_spec_beta: int
    
    precursor_correction: int
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void ProteinProteinCrossLink()
        """
        ...
    
    @overload
    def __init__(self, in_0: ProteinProteinCrossLink ) -> None:
        """
        Cython signature: void ProteinProteinCrossLink(ProteinProteinCrossLink &)
        """
        ...
    
    def getType(self) -> int:
        """
        Cython signature: ProteinProteinCrossLinkType getType()
        """
        ...
    
    def __richcmp__(self, other: ProteinProteinCrossLink, op: int) -> Any:
        ... 


class SolverParam:
    """
    Cython implementation of _SolverParam

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1SolverParam.html>`_
    """
    
    message_level: int
    
    branching_tech: int
    
    backtrack_tech: int
    
    preprocessing_tech: int
    
    enable_feas_pump_heuristic: bool
    
    enable_gmi_cuts: bool
    
    enable_mir_cuts: bool
    
    enable_cov_cuts: bool
    
    enable_clq_cuts: bool
    
    mip_gap: float
    
    time_limit: int
    
    output_freq: int
    
    output_delay: int
    
    enable_presolve: bool
    
    enable_binarization: bool
    
    def __init__(self) -> None:
        """
        Cython signature: void SolverParam()
        Hold the parameters of the LP solver
        """
        ... 


class SpectrumRangeManager:
    """
    Cython implementation of _SpectrumRangeManager

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1SpectrumRangeManager.html>`_

    Advanced range manager for MS spectra with separate ranges for each MS level
    
    This class extends the basic RangeManager to provide separate range tracking for different MS levels
    (MS1, MS2, etc.). It manages four types of ranges:
    - m/z (mass-to-charge ratio)
    - intensity
    - retention time (RT)
    - ion mobility
    
    A global range is tracked for all MS levels, and additional ranges are maintained for each specific MS level.
    This allows for efficient querying of ranges for specific MS levels, which is useful for visualization,
    filtering, and processing operations that need to work with specific MS levels.
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void SpectrumRangeManager()
        """
        ...
    
    @overload
    def __init__(self, in_0: SpectrumRangeManager ) -> None:
        """
        Cython signature: void SpectrumRangeManager(SpectrumRangeManager &)
        """
        ...
    
    def clearRanges(self) -> None:
        """
        Cython signature: void clearRanges()
        """
        ...
    
    def getMSLevels(self) -> Set[int]:
        """
        Cython signature: libcpp_set[unsigned int] getMSLevels()
        """
        ...
    
    def extendRT(self, rt: float , ms_level: int ) -> None:
        """
        Cython signature: void extendRT(double rt, unsigned int ms_level)
        """
        ...
    
    def extendMZ(self, mz: float , ms_level: int ) -> None:
        """
        Cython signature: void extendMZ(double mz, unsigned int ms_level)
        """
        ...
    
    def extendUnsafe(self, spectrum: MSSpectrum , ms_level: int ) -> None:
        """
        Cython signature: void extendUnsafe(const MSSpectrum & spectrum, unsigned int ms_level)
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
    
    def getMinMobility(self) -> float:
        """
        Cython signature: double getMinMobility()
        """
        ...
    
    def getMaxMobility(self) -> float:
        """
        Cython signature: double getMaxMobility()
        """
        ...
    
    def __richcmp__(self, other: SpectrumRangeManager, op: int) -> Any:
        ... 


class SplineInterpolatedPeaks:
    """
    Cython implementation of _SplineInterpolatedPeaks

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1SplineInterpolatedPeaks.html>`_
    """
    
    @overload
    def __init__(self, mz: List[float] , intensity: List[float] ) -> None:
        """
        Cython signature: void SplineInterpolatedPeaks(libcpp_vector[double] mz, libcpp_vector[double] intensity)
        """
        ...
    
    @overload
    def __init__(self, raw_spectrum: MSSpectrum ) -> None:
        """
        Cython signature: void SplineInterpolatedPeaks(MSSpectrum raw_spectrum)
        """
        ...
    
    @overload
    def __init__(self, raw_chromatogram: MSChromatogram ) -> None:
        """
        Cython signature: void SplineInterpolatedPeaks(MSChromatogram raw_chromatogram)
        """
        ...
    
    @overload
    def __init__(self, in_0: SplineInterpolatedPeaks ) -> None:
        """
        Cython signature: void SplineInterpolatedPeaks(SplineInterpolatedPeaks &)
        """
        ...
    
    def getPosMin(self) -> float:
        """
        Cython signature: double getPosMin()
        """
        ...
    
    def getPosMax(self) -> float:
        """
        Cython signature: double getPosMax()
        """
        ...
    
    def size(self) -> int:
        """
        Cython signature: int size()
        """
        ...
    
    def getNavigator(self, scaling: float ) -> SplineSpectrum_Navigator:
        """
        Cython signature: SplineSpectrum_Navigator getNavigator(double scaling)
        """
        ... 


class SplineSpectrum_Navigator:
    """
    Cython implementation of _SplineSpectrum_Navigator

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1SplineSpectrum_Navigator.html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void SplineSpectrum_Navigator()
        """
        ...
    
    @overload
    def __init__(self, in_0: SplineSpectrum_Navigator ) -> None:
        """
        Cython signature: void SplineSpectrum_Navigator(SplineSpectrum_Navigator)
        """
        ...
    
    @overload
    def __init__(self, packages: List[SplinePackage] , posMax: float , scaling: float ) -> None:
        """
        Cython signature: void SplineSpectrum_Navigator(libcpp_vector[SplinePackage] * packages, double posMax, double scaling)
        """
        ...
    
    def eval(self, pos: float ) -> float:
        """
        Cython signature: double eval(double pos)
        """
        ...
    
    def getNextPos(self, pos: float ) -> float:
        """
        Cython signature: double getNextPos(double pos)
        """
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


class ToolInfo:
    """
    Cython implementation of _ToolInfo

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1ToolInfo.html>`_
    """
    
    def __init__(self, in_0: ToolInfo ) -> None:
        """
        Cython signature: void ToolInfo(ToolInfo)
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


class VersionDetails:
    """
    Cython implementation of _VersionDetails

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1VersionDetails.html>`_
    """
    
    version_major: int
    
    version_minor: int
    
    version_patch: int
    
    pre_release_identifier: Union[bytes, str, String]
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void VersionDetails()
        """
        ...
    
    @overload
    def __init__(self, in_0: VersionDetails ) -> None:
        """
        Cython signature: void VersionDetails(VersionDetails &)
        """
        ...
    
    def __richcmp__(self, other: VersionDetails, op: int) -> Any:
        ...
    
    create: __static_VersionDetails_create 


class VersionInfo:
    """
    Cython implementation of _VersionInfo

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1VersionInfo.html>`_
    """
    
    getBranch: __static_VersionInfo_getBranch
    
    getRevision: __static_VersionInfo_getRevision
    
    getTime: __static_VersionInfo_getTime
    
    getVersion: __static_VersionInfo_getVersion
    
    getVersionStruct: __static_VersionInfo_getVersionStruct 


class WindowMower:
    """
    Cython implementation of _WindowMower

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1WindowMower.html>`_
      -- Inherits from ['DefaultParamHandler']
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void WindowMower()
        """
        ...
    
    @overload
    def __init__(self, in_0: WindowMower ) -> None:
        """
        Cython signature: void WindowMower(WindowMower &)
        """
        ...
    
    def filterPeakSpectrumForTopNInSlidingWindow(self, spectrum: MSSpectrum ) -> None:
        """
        Cython signature: void filterPeakSpectrumForTopNInSlidingWindow(MSSpectrum & spectrum)
        Sliding window version (slower)
        """
        ...
    
    def filterPeakSpectrumForTopNInJumpingWindow(self, spectrum: MSSpectrum ) -> None:
        """
        Cython signature: void filterPeakSpectrumForTopNInJumpingWindow(MSSpectrum & spectrum)
        Jumping window version (faster)
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


class __DerivatizationAgent:
    None
    NOT_SELECTED : int
    TBDMS : int
    SIZE_OF_DERIVATIZATIONAGENT : int

    def getMapping(self) -> Dict[int, str]:
       ...
    DerivatizationAgent : __DerivatizationAgent 


class DriftTimeUnit:
    None
    NONE : int
    MILLISECOND : int
    VSSC : int
    FAIMS_COMPENSATION_VOLTAGE : int
    SIZE_OF_DRIFTTIMEUNIT : int

    def getMapping(self) -> Dict[int, str]:
       ... 


class __FilterOperation:
    None
    GREATER_EQUAL : int
    EQUAL : int
    LESS_EQUAL : int
    EXISTS : int

    def getMapping(self) -> Dict[int, str]:
       ... 


class __FilterType:
    None
    INTENSITY : int
    QUALITY : int
    CHARGE : int
    SIZE : int
    META_DATA : int

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


class __LPWrapper_Type:
    None
    UNBOUNDED : int
    LOWER_BOUND_ONLY : int
    UPPER_BOUND_ONLY : int
    DOUBLE_BOUNDED : int
    FIXED : int

    def getMapping(self) -> Dict[int, str]:
       ... 


class __MassIntensityType:
    None
    NORM_MAX : int
    NORM_SUM : int
    SIZE_OF_MASSINTENSITYTYPE : int

    def getMapping(self) -> Dict[int, str]:
       ...
    MassIntensityType : __MassIntensityType 


class __SOLVER:
    None
    SOLVER_GLPK : int

    def getMapping(self) -> Dict[int, str]:
       ... 


class __Sense:
    None
    MIN : int
    MAX : int

    def getMapping(self) -> Dict[int, str]:
       ... 


class __SolverStatus:
    None
    UNDEFINED : int
    OPTIMAL : int
    FEASIBLE : int
    NO_FEASIBLE_SOL : int

    def getMapping(self) -> Dict[int, str]:
       ... 


class __Specificity:
    None
    SPEC_NONE : int
    SPEC_SEMI : int
    SPEC_FULL : int
    SPEC_UNKNOWN : int
    SPEC_NOCTERM : int
    SPEC_NONTERM : int
    SIZE_OF_SPECIFICITY : int

    def getMapping(self) -> Dict[int, str]:
       ... 


class __VariableType:
    None
    CONTINUOUS : int
    INTEGER : int
    BINARY : int

    def getMapping(self) -> Dict[int, str]:
       ... 


class __WriteFormat:
    None
    FORMAT_LP : int
    FORMAT_MPS : int
    FORMAT_GLPK : int

    def getMapping(self) -> Dict[int, str]:
       ... 

