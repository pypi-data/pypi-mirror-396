from __future__ import annotations
from typing import overload, Any, List, Dict, Tuple, Set, Sequence, Union
from pyopenms import *  # pylint: disable=wildcard-import; lgtm(py/polluting-import)
import numpy as _np

from enum import IntEnum as _PyEnum


def __static_MZTrafoModel_enumToName(mt: int ) -> bytes:
    """
    Cython signature: libcpp_string enumToName(MZTrafoModel_MODELTYPE mt)
    """
    ...

def __static_MZTrafoModel_findNearest(tms: List[MZTrafoModel] , rt: float ) -> int:
    """
    Cython signature: size_t findNearest(libcpp_vector[MZTrafoModel] & tms, double rt)
    """
    ...

def __static_SpectralDeconvolution_getCosine(a: List[float] , a_start: int , a_end: int , b: IsotopeDistribution , offset: int , min_iso_len: int ) -> float:
    """
    Cython signature: float getCosine(libcpp_vector[float] & a, int a_start, int a_end, IsotopeDistribution & b, int offset, int min_iso_len)
    """
    ...

def __static_TransformationModelLowess_getDefaultParameters(params: Param ) -> None:
    """
    Cython signature: void getDefaultParameters(Param & params)
    """
    ...

def __static_TransformationModelBSpline_getDefaultParameters(params: Param ) -> None:
    """
    Cython signature: void getDefaultParameters(Param & params)
    """
    ...

def __static_SpectralDeconvolution_getIsotopeCosineAndIsoOffset(mono_mass: float , per_isotope_intensities: List[float] , offset: int , avg: PrecalAveragine , iso_int_shift: int , window_width: int , excluded_masses: List[float] ) -> float:
    """
    Cython signature: float getIsotopeCosineAndIsoOffset(double mono_mass, libcpp_vector[float] & per_isotope_intensities, int & offset, PrecalAveragine & avg, int iso_int_shift, int window_width, libcpp_vector[double] & excluded_masses)
    """
    ...

def __static_CalibrationData_getMetaValues() -> List[bytes]:
    """
    Cython signature: StringList getMetaValues()
    """
    ...

def __static_SpectralDeconvolution_getNominalMass(mass: float ) -> int:
    """
    Cython signature: int getNominalMass(double mass)
    """
    ...

def __static_MZTrafoModel_isValidModel(trafo: MZTrafoModel ) -> bool:
    """
    Cython signature: bool isValidModel(MZTrafoModel & trafo)
    """
    ...

def __static_MZTrafoModel_nameToEnum(name: bytes ) -> int:
    """
    Cython signature: MZTrafoModel_MODELTYPE nameToEnum(libcpp_string name)
    """
    ...

def __static_DateTime_now() -> DateTime:
    """
    Cython signature: DateTime now()
    """
    ...

def __static_MZTrafoModel_setCoefficientLimits(offset: float , scale: float , power: float ) -> None:
    """
    Cython signature: void setCoefficientLimits(double offset, double scale, double power)
    """
    ...

def __static_MZTrafoModel_setRANSACParams(p: RANSACParam ) -> None:
    """
    Cython signature: void setRANSACParams(RANSACParam p)
    """
    ...


class AASeqWithMass:
    """
    Cython implementation of _AASeqWithMass

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1AASeqWithMass.html>`_
    """
    
    peptide_mass: float
    
    peptide_seq: AASequence
    
    position: int
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void AASeqWithMass()
        """
        ...
    
    @overload
    def __init__(self, in_0: AASeqWithMass ) -> None:
        """
        Cython signature: void AASeqWithMass(AASeqWithMass &)
        """
        ... 


class AScore:
    """
    Cython implementation of _AScore

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1AScore.html>`_
      -- Inherits from ['DefaultParamHandler']
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void AScore()
        """
        ...
    
    @overload
    def __init__(self, in_0: AScore ) -> None:
        """
        Cython signature: void AScore(AScore &)
        """
        ...
    
    def compute(self, hit: PeptideHit , real_spectrum: MSSpectrum ) -> PeptideHit:
        """
        Cython signature: PeptideHit compute(PeptideHit & hit, MSSpectrum & real_spectrum)
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


class AverageLinkage:
    """
    Cython implementation of _AverageLinkage

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1AverageLinkage.html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void AverageLinkage()
        """
        ...
    
    @overload
    def __init__(self, in_0: AverageLinkage ) -> None:
        """
        Cython signature: void AverageLinkage(AverageLinkage &)
        """
        ... 


class BayesianProteinInferenceAlgorithm:
    """
    Cython implementation of _BayesianProteinInferenceAlgorithm

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1BayesianProteinInferenceAlgorithm.html>`_
      -- Inherits from ['DefaultParamHandler', 'ProgressLogger']

    Performs a Bayesian protein inference on Protein/Peptide identifications or ConsensusMap.
    
    - Filters for best n PSMs per spectrum.
    - Calculates and filters for best peptide per spectrum.
    - Builds a k-partite graph from the structures.
    - Finds and splits into connected components by DFS
    - Extends the graph by adding layers from indist. protein groups, peptides with the same parents and optionally
      some additional layers (peptide sequence, charge, replicate -> extended model = experimental)
    - Builds a factor graph representation of a Bayesian network using the Evergreen library
      See model param section. It is based on the Fido noisy-OR model with an option for
      regularizing the number of proteins per peptide.
    - Performs loopy belief propagation on the graph and queries protein, protein group and/or peptide posteriors
      See loopy_belief_propagation param section.
    - Learns best parameters via grid search if the parameters were not given in the param section.
    - Writes posteriors to peptides and/or proteins and adds indistinguishable protein groups to the underlying
      data structures.
    - Can make use of OpenMP to parallelize over connected components.
    
    Usage:
    
    .. code-block:: python
    
      from pyopenms import *
      from urllib.request import urlretrieve
      urlretrieve("https://raw.githubusercontent.com/OpenMS/OpenMS/develop/src/tests/class_tests/openms/data/BayesianProteinInference_test.idXML", "BayesianProteinInference_test.idXML")
      proteins = []
      peptides = []
      idf = IdXMLFile()
      idf.load("BayesianProteinInference_test.idXML", proteins, peptides)
      bpia = BayesianProteinInferenceAlgorithm()
      p = bpia.getParameters()
      p.setValue("update_PSM_probabilities", "false")
      bpia.setParameters(p)
      bpia.inferPosteriorProbabilities(proteins, peptides)
      #
      print(len(peptides)) # 9
      print(peptides[0].getHits()[0].getScore()) # 0.6
      print(proteins[0].getHits()[0].getScore()) # 0.624641
      print(proteins[0].getHits()[1].getScore()) # 0.648346
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void BayesianProteinInferenceAlgorithm()
        """
        ...
    
    @overload
    def __init__(self, debug_lvl: int ) -> None:
        """
        Cython signature: void BayesianProteinInferenceAlgorithm(unsigned int debug_lvl)
        """
        ...
    
    @overload
    def inferPosteriorProbabilities(self, proteinIDs: List[ProteinIdentification] , peptideIDs: PeptideIdentificationList , greedy_group_resolution: bool ) -> None:
        """
        Cython signature: void inferPosteriorProbabilities(libcpp_vector[ProteinIdentification] & proteinIDs, PeptideIdentificationList & peptideIDs, bool greedy_group_resolution)
        Optionally adds indistinguishable protein groups with separate scores, too
        Currently only takes first proteinID run and all peptides
        
        
        :param proteinIDs: Vector of protein identifications
        :param peptideIDs: Vector of peptide identifications
        :return: Writes its results into protein and (optionally also) peptide hits (as new score)
        """
        ...
    
    @overload
    def inferPosteriorProbabilities(self, proteinIDs: List[ProteinIdentification] , peptideIDs: PeptideIdentificationList , greedy_group_resolution: bool , exp_des: ExperimentalDesign ) -> None:
        """
        Cython signature: void inferPosteriorProbabilities(libcpp_vector[ProteinIdentification] & proteinIDs, PeptideIdentificationList & peptideIDs, bool greedy_group_resolution, ExperimentalDesign exp_des)
        Writes its results into protein and (optionally also) peptide hits (as new score).
        Optionally adds indistinguishable protein groups with separate scores, too
        Currently only takes first proteinID run and all peptides
        Experimental design can be used to create an extended graph with replicate information. (experimental)
        
        
        :param proteinIDs: Vector of protein identifications
        :param peptideIDs: Vector of peptide identifications
        :param exp_des: Experimental Design
        :return: Writes its results into protein and (optionally also) peptide hits (as new score)
        """
        ...
    
    @overload
    def inferPosteriorProbabilities(self, cmap: ConsensusMap , greedy_group_resolution: bool ) -> None:
        """
        Cython signature: void inferPosteriorProbabilities(ConsensusMap & cmap, bool greedy_group_resolution)
        Writes its results into protein and (optionally also) peptide hits (as new score)
        Optionally adds indistinguishable protein groups with separate scores, too
        Loops over all runs in the ConsensusMaps' protein IDs (experimental)
        
        
        :param cmap: ConsensusMaps with protein IDs
        :param greedy_group_resolution: Adds indistinguishable protein groups with separate scores
        :return: Writes its protein ID results into the ConsensusMap
        """
        ...
    
    @overload
    def inferPosteriorProbabilities(self, cmap: ConsensusMap , greedy_group_resolution: bool , exp_des: ExperimentalDesign ) -> None:
        """
        Cython signature: void inferPosteriorProbabilities(ConsensusMap & cmap, bool greedy_group_resolution, ExperimentalDesign exp_des)
        Writes its results into protein and (optionally also) peptide hits (as new score)
        Optionally adds indistinguishable protein groups with separate scores, too
        Loops over all runs in the ConsensusMaps' protein IDs (experimental)
        
        
        :param cmap: ConsensusMaps with protein IDs.
        :param greedy_group_resolution: Adds indistinguishable protein groups with separate scores
        :param exp_des: Experimental Design
        :return: Writes its protein ID results into the ConsensusMap
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


class BinnedSpectrum:
    """
    Cython implementation of _BinnedSpectrum

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1BinnedSpectrum.html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void BinnedSpectrum()
        """
        ...
    
    @overload
    def __init__(self, in_0: BinnedSpectrum ) -> None:
        """
        Cython signature: void BinnedSpectrum(BinnedSpectrum &)
        """
        ...
    
    @overload
    def __init__(self, in_0: MSSpectrum , size: float , unit_ppm: bool , spread: int , offset: float ) -> None:
        """
        Cython signature: void BinnedSpectrum(MSSpectrum, float size, bool unit_ppm, unsigned int spread, float offset)
        """
        ...
    
    def getBinSize(self) -> float:
        """
        Cython signature: float getBinSize()
        Returns the bin size
        """
        ...
    
    def getBinSpread(self) -> int:
        """
        Cython signature: unsigned int getBinSpread()
        Returns the bin spread
        """
        ...
    
    def getBinIndex(self, mz: float ) -> int:
        """
        Cython signature: unsigned int getBinIndex(float mz)
        Returns the bin index of a given m/z position
        """
        ...
    
    def getBinLowerMZ(self, i: int ) -> float:
        """
        Cython signature: float getBinLowerMZ(size_t i)
        Returns the lower m/z of a bin given its index
        """
        ...
    
    def getBinIntensity(self, mz: float ) -> float:
        """
        Cython signature: float getBinIntensity(double mz)
        Returns the bin intensity at a given m/z position
        """
        ...
    
    def getPrecursors(self) -> List[Precursor]:
        """
        Cython signature: libcpp_vector[Precursor] getPrecursors()
        """
        ...
    
    def isCompatible(self, a: BinnedSpectrum , b: BinnedSpectrum ) -> bool:
        """
        Cython signature: bool isCompatible(BinnedSpectrum & a, BinnedSpectrum & b)
        """
        ...
    
    def getOffset(self) -> float:
        """
        Cython signature: float getOffset()
        Returns offset
        """
        ...
    
    def __richcmp__(self, other: BinnedSpectrum, op: int) -> Any:
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


class ConsensusMapNormalizerAlgorithmMedian:
    """
    Cython implementation of _ConsensusMapNormalizerAlgorithmMedian

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS::ConsensusMapNormalizerAlgorithmMedian_1_1ConsensusMapNormalizerAlgorithmMedian.html>`_
    """
    
    def __init__(self) -> None:
        """
        Cython signature: void ConsensusMapNormalizerAlgorithmMedian()
        """
        ...
    
    def computeMedians(self, input_map: ConsensusMap , medians: List[float] , acc_filter: Union[bytes, str, String] , desc_filter: Union[bytes, str, String] ) -> int:
        """
        Cython signature: size_t computeMedians(ConsensusMap & input_map, libcpp_vector[double] & medians, const String & acc_filter, const String & desc_filter)
        Computes medians of all maps and returns index of map with most features
        """
        ...
    
    def normalizeMaps(self, input_map: ConsensusMap , method: int , acc_filter: Union[bytes, str, String] , desc_filter: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void normalizeMaps(ConsensusMap & input_map, NormalizationMethod method, const String & acc_filter, const String & desc_filter)
        Normalizes the maps of the consensusMap
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


class DataValue:
    """
    Cython implementation of _DataValue

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1DataValue.html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void DataValue()
        """
        ...
    
    @overload
    def __init__(self, in_0: DataValue ) -> None:
        """
        Cython signature: void DataValue(DataValue &)
        """
        ...
    
    @overload
    def __init__(self, in_0: bytes ) -> None:
        """
        Cython signature: void DataValue(char *)
        """
        ...
    
    @overload
    def __init__(self, in_0: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void DataValue(const String &)
        """
        ...
    
    @overload
    def __init__(self, in_0: int ) -> None:
        """
        Cython signature: void DataValue(int)
        """
        ...
    
    @overload
    def __init__(self, in_0: float ) -> None:
        """
        Cython signature: void DataValue(double)
        """
        ...
    
    @overload
    def __init__(self, in_0: List[bytes] ) -> None:
        """
        Cython signature: void DataValue(StringList)
        """
        ...
    
    @overload
    def __init__(self, in_0: List[int] ) -> None:
        """
        Cython signature: void DataValue(IntList)
        """
        ...
    
    @overload
    def __init__(self, in_0: List[float] ) -> None:
        """
        Cython signature: void DataValue(DoubleList)
        """
        ...
    
    @overload
    def __init__(self, in_0: Union[int, float, bytes, str, List[int], List[float], List[bytes]] ) -> None:
        """
        Cython signature: void DataValue(ParamValue)
        """
        ...
    
    def toStringList(self) -> List[bytes]:
        """
        Cython signature: StringList toStringList()
        """
        ...
    
    def toDoubleList(self) -> List[float]:
        """
        Cython signature: libcpp_vector[double] toDoubleList()
        """
        ...
    
    def toIntList(self) -> List[int]:
        """
        Cython signature: libcpp_vector[int] toIntList()
        """
        ...
    
    def toString(self) -> Union[bytes, str, String]:
        """
        Cython signature: String toString()
        """
        ...
    
    def toBool(self) -> bool:
        """
        Cython signature: bool toBool()
        """
        ...
    
    def valueType(self) -> int:
        """
        Cython signature: DataType valueType()
        """
        ...
    
    def isEmpty(self) -> int:
        """
        Cython signature: int isEmpty()
        """
        ...
    
    def getUnitType(self) -> int:
        """
        Cython signature: UnitType getUnitType()
        """
        ...
    
    def setUnitType(self, u: int ) -> None:
        """
        Cython signature: void setUnitType(UnitType u)
        """
        ...
    
    def hasUnit(self) -> bool:
        """
        Cython signature: bool hasUnit()
        """
        ...
    
    def getUnit(self) -> int:
        """
        Cython signature: int getUnit()
        """
        ...
    
    def setUnit(self, unit_id: int ) -> None:
        """
        Cython signature: void setUnit(int unit_id)
        """
        ...
    
    def __str__(self) -> Union[bytes, str, String]:
        """
        Cython signature: String toString()
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


class FeatureFileOptions:
    """
    Cython implementation of _FeatureFileOptions

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1FeatureFileOptions.html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void FeatureFileOptions()
        Options for loading files containing features.
        """
        ...
    
    @overload
    def __init__(self, in_0: FeatureFileOptions ) -> None:
        """
        Cython signature: void FeatureFileOptions(FeatureFileOptions &)
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
    
    def setSizeOnly(self, in_0: bool ) -> None:
        """
        Cython signature: void setSizeOnly(bool)
        Sets whether or not to load only feature count
        """
        ...
    
    def getSizeOnly(self) -> bool:
        """
        Cython signature: bool getSizeOnly()
        Returns whether or not to load only meta data
        """
        ...
    
    def setLoadConvexHull(self, in_0: bool ) -> None:
        """
        Cython signature: void setLoadConvexHull(bool)
        Sets whether or not to load convex hull
        """
        ...
    
    def getLoadConvexHull(self) -> bool:
        """
        Cython signature: bool getLoadConvexHull()
        Returns whether or not to load convex hull
        """
        ...
    
    def setLoadSubordinates(self, in_0: bool ) -> None:
        """
        Cython signature: void setLoadSubordinates(bool)
        Sets whether or not load subordinates
        """
        ...
    
    def getLoadSubordinates(self) -> bool:
        """
        Cython signature: bool getLoadSubordinates()
        Returns whether or not to load subordinates
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


class FeatureGroupingAlgorithmLabeled:
    """
    Cython implementation of _FeatureGroupingAlgorithmLabeled

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1FeatureGroupingAlgorithmLabeled.html>`_
      -- Inherits from ['FeatureGroupingAlgorithm']
    """
    
    def __init__(self) -> None:
        """
        Cython signature: void FeatureGroupingAlgorithmLabeled()
        """
        ...
    
    def group(self, maps: List[FeatureMap] , out: ConsensusMap ) -> None:
        """
        Cython signature: void group(libcpp_vector[FeatureMap] & maps, ConsensusMap & out)
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


class FloatDataArray:
    """
    Cython implementation of _FloatDataArray

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS::DataArrays_1_1FloatDataArray.html>`_
      -- Inherits from ['MetaInfoDescription']

    The representation of extra float data attached to a spectrum or chromatogram.
    Raw data access is proved by `get_peaks` and `set_peaks`, which yields numpy arrays
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void FloatDataArray()
        """
        ...
    
    @overload
    def __init__(self, in_0: FloatDataArray ) -> None:
        """
        Cython signature: void FloatDataArray(FloatDataArray &)
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
    
    def push_back(self, in_0: float ) -> None:
        """
        Cython signature: void push_back(float)
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
    
    def __richcmp__(self, other: FloatDataArray, op: int) -> Any:
        ... 


class GNPSQuantificationFile:
    """
    Cython implementation of _GNPSQuantificationFile

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1GNPSQuantificationFile.html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void GNPSQuantificationFile()
        """
        ...
    
    @overload
    def __init__(self, in_0: GNPSQuantificationFile ) -> None:
        """
        Cython signature: void GNPSQuantificationFile(GNPSQuantificationFile &)
        """
        ...
    
    def store(self, consensus_map: ConsensusMap , output_file: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void store(const ConsensusMap & consensus_map, const String & output_file)
        Write feature quantification table (txt file) from a ConsensusMap. Required for GNPS FBMN.
        
        The table contains map information on the featureXML files from which the ConsensusMap was generated as well as
        a row for every consensus feature with information on rt, mz, intensity, width and quality. The same information is
        added for each original feature in the consensus feature.
        
        :param consensus_map: Input ConsensusMap annotated with IonIdentityMolecularNetworking.annotateConsensusMap.
        :param output_file: Output file path for the feature quantification table.
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


class IMSWeights:
    """
    Cython implementation of _IMSWeights

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS::ims::Weights_1_1IMSWeights.html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void IMSWeights()
        """
        ...
    
    @overload
    def __init__(self, in_0: IMSWeights ) -> None:
        """
        Cython signature: void IMSWeights(IMSWeights)
        """
        ...
    
    def size(self) -> int:
        """
        Cython signature: int size()
        Gets size of a set of weights
        """
        ...
    
    def getWeight(self, i: int ) -> int:
        """
        Cython signature: unsigned int getWeight(int i)
        Gets a scaled integer weight by index
        """
        ...
    
    def setPrecision(self, precision: float ) -> None:
        """
        Cython signature: void setPrecision(double precision)
        Sets a new precision to scale double values to integer
        """
        ...
    
    def getPrecision(self) -> float:
        """
        Cython signature: double getPrecision()
        Gets precision.
        """
        ...
    
    def back(self) -> int:
        """
        Cython signature: unsigned int back()
        Gets a last weight
        """
        ...
    
    def getAlphabetMass(self, i: int ) -> float:
        """
        Cython signature: double getAlphabetMass(int i)
        Gets an original (double) alphabet mass by index
        """
        ...
    
    def getParentMass(self, decomposition: List[int] ) -> float:
        """
        Cython signature: double getParentMass(libcpp_vector[unsigned int] & decomposition)
        Returns a parent mass for a given `decomposition`
        """
        ...
    
    def swap(self, index1: int , index2: int ) -> None:
        """
        Cython signature: void swap(int index1, int index2)
        Exchanges weight and mass at index1 with weight and mass at index2
        """
        ...
    
    def divideByGCD(self) -> bool:
        """
        Cython signature: bool divideByGCD()
        Divides the integer weights by their gcd. The precision is also adjusted
        """
        ...
    
    def getMinRoundingError(self) -> float:
        """
        Cython signature: double getMinRoundingError()
        """
        ...
    
    def getMaxRoundingError(self) -> float:
        """
        Cython signature: double getMaxRoundingError()
        """
        ... 


class IsobaricChannelExtractor:
    """
    Cython implementation of _IsobaricChannelExtractor

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1IsobaricChannelExtractor.html>`_
      -- Inherits from ['DefaultParamHandler']
    """
    
    @overload
    def __init__(self, in_0: IsobaricChannelExtractor ) -> None:
        """
        Cython signature: void IsobaricChannelExtractor(IsobaricChannelExtractor &)
        """
        ...
    
    @overload
    def __init__(self, quant_method: ItraqEightPlexQuantitationMethod ) -> None:
        """
        Cython signature: void IsobaricChannelExtractor(ItraqEightPlexQuantitationMethod * quant_method)
        """
        ...
    
    @overload
    def __init__(self, quant_method: ItraqFourPlexQuantitationMethod ) -> None:
        """
        Cython signature: void IsobaricChannelExtractor(ItraqFourPlexQuantitationMethod * quant_method)
        """
        ...
    
    @overload
    def __init__(self, quant_method: TMTSixPlexQuantitationMethod ) -> None:
        """
        Cython signature: void IsobaricChannelExtractor(TMTSixPlexQuantitationMethod * quant_method)
        """
        ...
    
    @overload
    def __init__(self, quant_method: TMTTenPlexQuantitationMethod ) -> None:
        """
        Cython signature: void IsobaricChannelExtractor(TMTTenPlexQuantitationMethod * quant_method)
        """
        ...
    
    def extractChannels(self, ms_exp_data: MSExperiment , consensus_map: ConsensusMap ) -> None:
        """
        Cython signature: void extractChannels(MSExperiment & ms_exp_data, ConsensusMap & consensus_map)
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


class KDTreeFeatureMaps:
    """
    Cython implementation of _KDTreeFeatureMaps

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1KDTreeFeatureMaps.html>`_
      -- Inherits from ['DefaultParamHandler']
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void KDTreeFeatureMaps()
        Stores a set of features, together with a 2D tree for fast search
        """
        ...
    
    @overload
    def __init__(self, maps: List[FeatureMap] , param: Param ) -> None:
        """
        Cython signature: void KDTreeFeatureMaps(const libcpp_vector[FeatureMap] & maps, const Param & param)
        """
        ...
    
    @overload
    def __init__(self, maps: List[ConsensusMap] , param: Param ) -> None:
        """
        Cython signature: void KDTreeFeatureMaps(const libcpp_vector[ConsensusMap] & maps, const Param & param)
        """
        ...
    
    @overload
    def addMaps(self, maps: List[FeatureMap] ) -> None:
        """
        Cython signature: void addMaps(const libcpp_vector[FeatureMap] & maps)
        Add `maps` and balance kd-tree
        """
        ...
    
    @overload
    def addMaps(self, maps: List[ConsensusMap] ) -> None:
        """
        Cython signature: void addMaps(const libcpp_vector[ConsensusMap] & maps)
        """
        ...
    
    def rt(self, i: int ) -> float:
        """
        Cython signature: double rt(size_t i)
        """
        ...
    
    def mz(self, i: int ) -> float:
        """
        Cython signature: double mz(size_t i)
        """
        ...
    
    def intensity(self, i: int ) -> float:
        """
        Cython signature: float intensity(size_t i)
        """
        ...
    
    def charge(self, i: int ) -> int:
        """
        Cython signature: int charge(size_t i)
        """
        ...
    
    def mapIndex(self, i: int ) -> int:
        """
        Cython signature: size_t mapIndex(size_t i)
        """
        ...
    
    def size(self) -> int:
        """
        Cython signature: size_t size()
        """
        ...
    
    def treeSize(self) -> int:
        """
        Cython signature: size_t treeSize()
        """
        ...
    
    def numMaps(self) -> int:
        """
        Cython signature: size_t numMaps()
        """
        ...
    
    def clear(self) -> None:
        """
        Cython signature: void clear()
        """
        ...
    
    def optimizeTree(self) -> None:
        """
        Cython signature: void optimizeTree()
        """
        ...
    
    def getNeighborhood(self, index: int , result_indices: List[int] , rt_tol: float , mz_tol: float , mz_ppm: bool , include_features_from_same_map: bool , max_pairwise_log_fc: float ) -> None:
        """
        Cython signature: void getNeighborhood(size_t index, libcpp_vector[size_t] & result_indices, double rt_tol, double mz_tol, bool mz_ppm, bool include_features_from_same_map, double max_pairwise_log_fc)
        Fill `result` with indices of all features compatible (wrt. RT, m/z, map index) to the feature with `index`
        """
        ...
    
    def queryRegion(self, rt_low: float , rt_high: float , mz_low: float , mz_high: float , result_indices: List[int] , ignored_map_index: int ) -> None:
        """
        Cython signature: void queryRegion(double rt_low, double rt_high, double mz_low, double mz_high, libcpp_vector[size_t] & result_indices, size_t ignored_map_index)
        """
        ...
    
    def applyTransformations(self, trafos: List[TransformationModelLowess] ) -> None:
        """
        Cython signature: void applyTransformations(const libcpp_vector[TransformationModelLowess *] & trafos)
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


class MSDataCachedConsumer:
    """
    Cython implementation of _MSDataCachedConsumer

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1MSDataCachedConsumer.html>`_

    Transforming and cached writing consumer of MS data
    
    Is able to transform a spectrum on the fly while it is read using a
    function pointer that can be set on the object. The spectra is then
    cached to disk using the functions provided in CachedMzMLHandler.
    """
    
    @overload
    def __init__(self, filename: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void MSDataCachedConsumer(String filename)
        """
        ...
    
    @overload
    def __init__(self, filename: Union[bytes, str, String] , clear: bool ) -> None:
        """
        Cython signature: void MSDataCachedConsumer(String filename, bool clear)
        """
        ...
    
    def consumeSpectrum(self, s: MSSpectrum ) -> None:
        """
        Cython signature: void consumeSpectrum(MSSpectrum & s)
        Write a spectrum to the output file
        
        May delete data from spectrum (if clearData is set)
        """
        ...
    
    def consumeChromatogram(self, c: MSChromatogram ) -> None:
        """
        Cython signature: void consumeChromatogram(MSChromatogram & c)
        Write a chromatogram to the output file
        
        May delete data from chromatogram (if clearData is set)
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


class MZTrafoModel:
    """
    Cython implementation of _MZTrafoModel

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1MZTrafoModel.html>`_

    Create and apply models of a mass recalibration function
    
    The input is a list of calibration points (ideally spanning a wide m/z range to prevent extrapolation when applying to model)
    
    Models (LINEAR, LINEAR_WEIGHTED, QUADRATIC, QUADRATIC_WEIGHTED) can be trained using CalData points (or a subset of them)
    Calibration points can have different retention time points, and a model should be build such that it captures
    the local (in time) decalibration of the instrument, i.e. choose appropriate time windows along RT to calibrate the
    spectra in this RT region
    From the available calibrant data, a model is build. Later, any uncalibrated m/z value can be fed to the model, to obtain
    a calibrated m/z
    
    The input domain can either be absolute mass differences in [Th], or relative differences in [ppm]
    The models are build based on this input
    
    Outlier detection before model building via the RANSAC algorithm is supported for LINEAR and QUADRATIC models
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void MZTrafoModel()
        """
        ...
    
    @overload
    def __init__(self, in_0: MZTrafoModel ) -> None:
        """
        Cython signature: void MZTrafoModel(MZTrafoModel &)
        """
        ...
    
    @overload
    def __init__(self, in_0: bool ) -> None:
        """
        Cython signature: void MZTrafoModel(bool)
        """
        ...
    
    def isTrained(self) -> bool:
        """
        Cython signature: bool isTrained()
        Returns true if the model have coefficients (i.e. was trained successfully)
        """
        ...
    
    def getRT(self) -> float:
        """
        Cython signature: double getRT()
        Get RT associated with the model (training region)
        """
        ...
    
    def predict(self, mz: float ) -> float:
        """
        Cython signature: double predict(double mz)
        Apply the model to an uncalibrated m/z value
        
        Make sure the model was trained (train()) and is valid (isValidModel()) before calling this function!
        
        Applies the function y = intercept + slope*mz + power*mz^2
        and returns y
        
        
        :param mz: The uncalibrated m/z value
        :return: The calibrated m/z value
        """
        ...
    
    @overload
    def train(self, cd: CalibrationData , md: int , use_RANSAC: bool , rt_left: float , rt_right: float ) -> bool:
        """
        Cython signature: bool train(CalibrationData cd, MZTrafoModel_MODELTYPE md, bool use_RANSAC, double rt_left, double rt_right)
        Train a model using calibrant data
        
        If the CalibrationData was created using peak groups (usually corresponding to mass traces),
        the median for each group is used as a group representative. This
        is more robust, and reduces the number of data points drastically, i.e. one value per group
        
        Internally, these steps take place:
        - apply RT filter
        - [compute median per group] (only if groups were given in 'cd')
        - set Model's rt position
        - call train() (see overloaded method)
        
        
        :param cd: List of calibrants
        :param md: Type of model (linear, quadratic, ...)
        :param use_RANSAC: Remove outliers before computing the model?
        :param rt_left: Filter 'cd' by RT; all calibrants with RT < 'rt_left' are removed
        :param rt_right: Filter 'cd' by RT; all calibrants with RT > 'rt_right' are removed
        :return: True if model was build, false otherwise
        """
        ...
    
    @overload
    def train(self, error_mz: List[float] , theo_mz: List[float] , weights: List[float] , md: int , use_RANSAC: bool ) -> bool:
        """
        Cython signature: bool train(libcpp_vector[double] error_mz, libcpp_vector[double] theo_mz, libcpp_vector[double] weights, MZTrafoModel_MODELTYPE md, bool use_RANSAC)
        Train a model using calibrant data
        
        Given theoretical and observed mass values (and corresponding weights),
        a model (linear, quadratic, ...) is build
        Outlier removal is applied before
        The 'obs_mz' can be either given as absolute masses in [Th] or relative deviations in [ppm]
        The MZTrafoModel must be constructed accordingly (see constructor). This has no influence on the model building itself, but
        rather on how 'predict()' works internally
        
        Outlier detection before model building via the RANSAC algorithm is supported for LINEAR and QUADRATIC models
        
        Internally, these steps take place:
        - [apply RANSAC] (depending on 'use_RANSAC')
        - build model and store its parameters internally
        
        
        :param error_mz: Observed Mass error (in ppm or Th)
        :param theo_mz: Theoretical m/z values, corresponding to 'error_mz'
        :param weights: For weighted models only: weight of calibrants; ignored otherwise
        :param md: Type of model (linear, quadratic, ...)
        :param use_RANSAC: Remove outliers before computing the model?
        :return: True if model was build, false otherwise
        """
        ...
    
    def getCoefficients(self, intercept: float , slope: float , power: float ) -> None:
        """
        Cython signature: void getCoefficients(double & intercept, double & slope, double & power)
        Get model coefficients
        
        Parameters will be filled with internal model parameters
        The model must be trained before; Exception is thrown otherwise!
        
        
        :param intercept: The intercept
        :param slope: The slope
        :param power: The coefficient for x*x (will be 0 for linear models)
        """
        ...
    
    @overload
    def setCoefficients(self, in_0: MZTrafoModel ) -> None:
        """
        Cython signature: void setCoefficients(MZTrafoModel)
        Copy model coefficients from another model
        """
        ...
    
    @overload
    def setCoefficients(self, in_0: float , in_1: float , in_2: float ) -> None:
        """
        Cython signature: void setCoefficients(double, double, double)
        Manually set model coefficients
        
        Can be used instead of train(), so manually set coefficients
        It must be exactly three values. If you want a linear model, set 'power' to zero
        If you want a constant model, set slope to zero in addition
        
        
        :param intercept: The offset
        :param slope: The slope
        :param power: The x*x coefficient (for quadratic models)
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
    
    enumToName: __static_MZTrafoModel_enumToName
    
    findNearest: __static_MZTrafoModel_findNearest
    
    isValidModel: __static_MZTrafoModel_isValidModel
    
    nameToEnum: __static_MZTrafoModel_nameToEnum
    
    setCoefficientLimits: __static_MZTrafoModel_setCoefficientLimits
    
    setRANSACParams: __static_MZTrafoModel_setRANSACParams 


class MapAlignmentTransformer:
    """
    Cython implementation of _MapAlignmentTransformer

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1MapAlignmentTransformer.html>`_

    This class collects functions for applying retention time transformations to data structures
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void MapAlignmentTransformer()
        """
        ...
    
    @overload
    def __init__(self, in_0: MapAlignmentTransformer ) -> None:
        """
        Cython signature: void MapAlignmentTransformer(MapAlignmentTransformer &)
        """
        ...
    
    @overload
    def transformRetentionTimes(self, in_0: MSExperiment , in_1: TransformationDescription , in_2: bool ) -> None:
        """
        Cython signature: void transformRetentionTimes(MSExperiment &, TransformationDescription &, bool)
        Applies the given transformation to a peak map
        """
        ...
    
    @overload
    def transformRetentionTimes(self, in_0: FeatureMap , in_1: TransformationDescription , in_2: bool ) -> None:
        """
        Cython signature: void transformRetentionTimes(FeatureMap &, TransformationDescription &, bool)
        Applies the given transformation to a feature map
        """
        ...
    
    @overload
    def transformRetentionTimes(self, in_0: ConsensusMap , in_1: TransformationDescription , in_2: bool ) -> None:
        """
        Cython signature: void transformRetentionTimes(ConsensusMap &, TransformationDescription &, bool)
        Applies the given transformation to a consensus map
        """
        ...
    
    @overload
    def transformRetentionTimes(self, in_0: PeptideIdentificationList , in_1: TransformationDescription , in_2: bool ) -> None:
        """
        Cython signature: void transformRetentionTimes(PeptideIdentificationList &, TransformationDescription &, bool)
        Applies the given transformation to peptide identifications
        """
        ... 


class MapConversion:
    """
    Cython implementation of _MapConversion

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1MapConversion.html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void MapConversion()
        """
        ...
    
    @overload
    def __init__(self, in_0: MapConversion ) -> None:
        """
        Cython signature: void MapConversion(MapConversion &)
        """
        ...
    
    @overload
    def convert(self, input_map_index: int , input_map: FeatureMap , output_map: ConsensusMap , n: int ) -> None:
        """
        Cython signature: void convert(uint64_t input_map_index, FeatureMap input_map, ConsensusMap & output_map, size_t n)
        """
        ...
    
    @overload
    def convert(self, input_map_index: int , input_map: MSExperiment , output_map: ConsensusMap , n: int ) -> None:
        """
        Cython signature: void convert(uint64_t input_map_index, MSExperiment & input_map, ConsensusMap & output_map, size_t n)
        """
        ...
    
    @overload
    def convert(self, input_map: ConsensusMap , keep_uids: bool , output_map: FeatureMap ) -> None:
        """
        Cython signature: void convert(ConsensusMap input_map, bool keep_uids, FeatureMap & output_map)
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


class NonNegativeLeastSquaresSolver:
    """
    Cython implementation of _NonNegativeLeastSquaresSolver

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1NonNegativeLeastSquaresSolver.html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void NonNegativeLeastSquaresSolver()
        """
        ...
    
    @overload
    def __init__(self, in_0: NonNegativeLeastSquaresSolver ) -> None:
        """
        Cython signature: void NonNegativeLeastSquaresSolver(NonNegativeLeastSquaresSolver &)
        """
        ...
    
    def solve(self, A: MatrixDouble , b: MatrixDouble , x: MatrixDouble ) -> int:
        """
        Cython signature: int solve(MatrixDouble & A, MatrixDouble & b, MatrixDouble & x)
        """
        ...
    RETURN_STATUS : __RETURN_STATUS 


class OPXLDataStructs:
    """
    Cython implementation of _OPXLDataStructs

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1OPXLDataStructs.html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void OPXLDataStructs()
        """
        ...
    
    @overload
    def __init__(self, in_0: OPXLDataStructs ) -> None:
        """
        Cython signature: void OPXLDataStructs(OPXLDataStructs &)
        """
        ...
    PeptidePosition : __PeptidePosition
    ProteinProteinCrossLinkType : __ProteinProteinCrossLinkType 


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


class OSWFile:
    """
    Cython implementation of _OSWFile

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1OSWFile.html>`_

    This class serves for reading in and writing OpenSWATH OSW files
    
    See OpenSwathOSWWriter for more functionality
    
    The reader and writer returns data in a format suitable for PercolatorAdapter.
    OSW files have a flexible data structure. They contain all peptide query
    parameters of TraML/PQP files with the detected and quantified features of
    OpenSwathWorkflow (feature, feature_ms1, feature_ms2 & feature_transition)
    
    The OSWFile reader extracts the feature information from the OSW file for
    each level (MS1, MS2 & transition) separately and generates Percolator input
    files. For each of the three Percolator reports, OSWFile writer adds a table
    (score_ms1, score_ms2, score_transition) with the respective confidence metrics.
    These tables can be mapped to the corresponding feature tables, are very similar
    to PyProphet results and can thus be used interchangeably
    """
    
    @overload
    def __init__(self, filename: Union[bytes, str] ) -> None:
        """
        Cython signature: void OSWFile(const libcpp_utf8_string filename)
        """
        ...
    
    @overload
    def __init__(self, in_0: OSWFile ) -> None:
        """
        Cython signature: void OSWFile(OSWFile &)
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


class ParamValue:
    """
    Cython implementation of _ParamValue

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1ParamValue.html>`_

    Class to hold strings, numeric values, vectors of strings and vectors of numeric values using the stl types
    
    - To choose one of these types, just use the appropriate constructor
    - Automatic conversion is supported and throws Exceptions in case of invalid conversions
    - An empty object is created with the default constructor
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void ParamValue()
        """
        ...
    
    @overload
    def __init__(self, in_0: ParamValue ) -> None:
        """
        Cython signature: void ParamValue(ParamValue &)
        """
        ...
    
    @overload
    def __init__(self, in_0: bytes ) -> None:
        """
        Cython signature: void ParamValue(char *)
        """
        ...
    
    @overload
    def __init__(self, in_0: Union[bytes, str] ) -> None:
        """
        Cython signature: void ParamValue(const libcpp_utf8_string &)
        """
        ...
    
    @overload
    def __init__(self, in_0: int ) -> None:
        """
        Cython signature: void ParamValue(int)
        """
        ...
    
    @overload
    def __init__(self, in_0: float ) -> None:
        """
        Cython signature: void ParamValue(double)
        """
        ...
    
    @overload
    def __init__(self, in_0: List[Union[bytes, str]] ) -> None:
        """
        Cython signature: void ParamValue(libcpp_vector[libcpp_utf8_string])
        """
        ...
    
    @overload
    def __init__(self, in_0: List[int] ) -> None:
        """
        Cython signature: void ParamValue(libcpp_vector[int])
        """
        ...
    
    @overload
    def __init__(self, in_0: List[float] ) -> None:
        """
        Cython signature: void ParamValue(libcpp_vector[double])
        """
        ...
    
    def toStringVector(self) -> List[bytes]:
        """
        Cython signature: libcpp_vector[libcpp_string] toStringVector()
        Explicitly convert ParamValue to string vector
        """
        ...
    
    def toDoubleVector(self) -> List[float]:
        """
        Cython signature: libcpp_vector[double] toDoubleVector()
        Explicitly convert ParamValue to DoubleList
        """
        ...
    
    def toIntVector(self) -> List[int]:
        """
        Cython signature: libcpp_vector[int] toIntVector()
        Explicitly convert ParamValue to IntList
        """
        ...
    
    def toBool(self) -> bool:
        """
        Cython signature: bool toBool()
        Converts the strings 'true' and 'false' to a bool
        """
        ...
    
    def valueType(self) -> int:
        """
        Cython signature: ValueType valueType()
        """
        ...
    
    def isEmpty(self) -> int:
        """
        Cython signature: int isEmpty()
        Test if the value is empty
        """
        ... 


class PeakGroup:
    """
    Cython implementation of _PeakGroup

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1PeakGroup.html>`_

    Class describing a deconvolved mass.
    A mass contains multiple (LogMz) peaks of different charges and isotope indices.
    PeakGroup is the set of such peaks representing a single monoisotopic mass.
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void PeakGroup()
        """
        ...
    
    @overload
    def __init__(self, in_0: PeakGroup ) -> None:
        """
        Cython signature: void PeakGroup(PeakGroup &)
        """
        ...
    
    @overload
    def __init__(self, min_abs_charge: int , max_abs_charge: int , is_positive: bool ) -> None:
        """
        Cython signature: void PeakGroup(int min_abs_charge, int max_abs_charge, bool is_positive)
        """
        ...
    
    def getMonoMass(self) -> float:
        """
        Cython signature: double getMonoMass()
        Returns the monoisotopic mass
        """
        ...
    
    def getIntensity(self) -> float:
        """
        Cython signature: float getIntensity()
        Returns the summed intensity
        """
        ...
    
    def getQscore(self) -> float:
        """
        Cython signature: double getQscore()
        Returns the quality score (0-1)
        """
        ...
    
    def getQscore2D(self) -> float:
        """
        Cython signature: double getQscore2D()
        Returns the 2D quality score incorporating feature-level information
        """
        ...
    
    def getIsotopeCosine(self) -> float:
        """
        Cython signature: float getIsotopeCosine()
        Returns the isotope cosine score
        """
        ...
    
    def getChargeScore(self) -> float:
        """
        Cython signature: float getChargeScore()
        Returns the charge fit score
        """
        ...
    
    def getSNR(self) -> float:
        """
        Cython signature: float getSNR()
        Returns the signal-to-noise ratio
        """
        ...
    
    def getRepAbsCharge(self) -> int:
        """
        Cython signature: int getRepAbsCharge()
        Returns the representative charge
        """
        ...
    
    def getIsotopeIntensities(self) -> List[float]:
        """
        Cython signature: libcpp_vector[float] getIsotopeIntensities()
        Returns per-isotope intensities
        """
        ...
    
    def getScanNumber(self) -> int:
        """
        Cython signature: int getScanNumber()
        Returns the scan number
        """
        ...
    
    def getIndex(self) -> int:
        """
        Cython signature: unsigned int getIndex()
        Returns the peak group index
        """
        ...
    
    def getFeatureIndex(self) -> int:
        """
        Cython signature: unsigned int getFeatureIndex()
        Returns the feature index
        """
        ...
    
    def getQvalue(self) -> float:
        """
        Cython signature: float getQvalue()
        Returns the q-value for FDR
        """
        ...
    
    def getTargetDecoyType(self) -> int:
        """
        Cython signature: TargetDecoyType getTargetDecoyType()
        Returns target/decoy type
        """
        ...
    
    def isPositive(self) -> bool:
        """
        Cython signature: bool isPositive()
        Returns true if positive ionization mode
        """
        ...
    
    def isTargeted(self) -> bool:
        """
        Cython signature: bool isTargeted()
        Returns true if this peak group was targeted
        """
        ...
    
    def getPeakOccupancy(self) -> float:
        """
        Cython signature: float getPeakOccupancy()
        Returns peak occupancy (0-1)
        """
        ...
    
    def getAvgPPMError(self) -> float:
        """
        Cython signature: float getAvgPPMError()
        Returns average ppm error
        """
        ...
    
    def getAvgDaError(self) -> float:
        """
        Cython signature: float getAvgDaError()
        Returns average Da error
        """
        ...
    
    def getChargeIntensity(self, abs_charge: int ) -> float:
        """
        Cython signature: float getChargeIntensity(int abs_charge)
        Returns intensity for given charge
        """
        ...
    
    def getChargeSNR(self, abs_charge: int ) -> float:
        """
        Cython signature: float getChargeSNR(int abs_charge)
        Returns SNR for given charge
        """
        ...
    
    def getChargeIsotopeCosine(self, abs_charge: int ) -> float:
        """
        Cython signature: float getChargeIsotopeCosine(int abs_charge)
        Returns isotope cosine for given charge
        """
        ...
    
    def getIsotopeDaDistance(self) -> float:
        """
        Cython signature: double getIsotopeDaDistance()
        Returns distance between consecutive isotopes
        """
        ...
    
    def getMinNegativeIsotopeIndex(self) -> int:
        """
        Cython signature: int getMinNegativeIsotopeIndex()
        Returns minimum negative isotope index
        """
        ...
    
    def getMassErrors(self, ppm: bool ) -> List[float]:
        """
        Cython signature: libcpp_vector[float] getMassErrors(bool ppm)
        Returns mass errors per isotope
        """
        ...
    
    def setScanNumber(self, scan_number: int ) -> None:
        """
        Cython signature: void setScanNumber(int scan_number)
        Sets the scan number
        """
        ...
    
    def setMonoisotopicMass(self, mono_mass: float ) -> None:
        """
        Cython signature: void setMonoisotopicMass(double mono_mass)
        Sets the monoisotopic mass
        """
        ...
    
    def setIsotopeCosine(self, cos: float ) -> None:
        """
        Cython signature: void setIsotopeCosine(float cos)
        Sets the isotope cosine score
        """
        ...
    
    def setChargeScore(self, charge_score: float ) -> None:
        """
        Cython signature: void setChargeScore(float charge_score)
        Sets the charge fit score
        """
        ...
    
    def setSNR(self, snr: float ) -> None:
        """
        Cython signature: void setSNR(float snr)
        Sets the SNR
        """
        ...
    
    def setQscore(self, qscore: float ) -> None:
        """
        Cython signature: void setQscore(double qscore)
        Sets the quality score
        """
        ...
    
    def setQscore2D(self, fqscore: float ) -> None:
        """
        Cython signature: void setQscore2D(double fqscore)
        Sets the 2D quality score
        """
        ...
    
    def setQvalue(self, q: float ) -> None:
        """
        Cython signature: void setQvalue(double q)
        Sets the q-value
        """
        ...
    
    def setRepAbsCharge(self, max_snr_abs_charge: int ) -> None:
        """
        Cython signature: void setRepAbsCharge(int max_snr_abs_charge)
        Sets the representative charge
        """
        ...
    
    def setIndex(self, i: int ) -> None:
        """
        Cython signature: void setIndex(unsigned int i)
        Sets the peak group index
        """
        ...
    
    def setFeatureIndex(self, findex: int ) -> None:
        """
        Cython signature: void setFeatureIndex(unsigned int findex)
        Sets the feature index
        """
        ...
    
    def setTargetDecoyType(self, index: int ) -> None:
        """
        Cython signature: void setTargetDecoyType(TargetDecoyType index)
        Sets the target/decoy type
        """
        ...
    
    def setTargeted(self) -> None:
        """
        Cython signature: void setTargeted()
        Marks this peak group as targeted
        """
        ...
    
    def setIsotopeDaDistance(self, d: float ) -> None:
        """
        Cython signature: void setIsotopeDaDistance(double d)
        Sets isotope distance
        """
        ...
    
    def setChargeIsotopeCosine(self, abs_charge: int , cos: float ) -> None:
        """
        Cython signature: void setChargeIsotopeCosine(int abs_charge, float cos)
        Sets isotope cosine for given charge
        """
        ...
    
    def setChargeSNR(self, abs_charge: int , c_snr: float ) -> None:
        """
        Cython signature: void setChargeSNR(int abs_charge, float c_snr)
        Sets SNR for given charge
        """
        ...
    
    def setAvgPPMError(self, error: float ) -> None:
        """
        Cython signature: void setAvgPPMError(float error)
        Sets average ppm error
        """
        ...
    
    def size(self) -> int:
        """
        Cython signature: size_t size()
        Returns number of LogMzPeaks
        """
        ...
    
    def empty(self) -> bool:
        """
        Cython signature: bool empty()
        Returns true if no peaks
        """
        ...
    
    def push_back(self, pg: LogMzPeak ) -> None:
        """
        Cython signature: void push_back(LogMzPeak & pg)
        Adds a LogMzPeak
        """
        ...
    
    def reserve(self, n: int ) -> None:
        """
        Cython signature: void reserve(size_t n)
        Reserves space for n peaks
        """
        ...
    
    def sort(self) -> None:
        """
        Cython signature: void sort()
        Sorts peaks by log m/z
        """
        ...
    
    def __getitem__(self, i: int ) -> LogMzPeak:
        """
        Cython signature: LogMzPeak operator[](size_t i)
        """
        ...
    
    def __richcmp__(self, other: PeakGroup, op: int) -> Any:
        ...
    
    def __iter__(self) -> LogMzPeak:
       ...
    TargetDecoyType : __TargetDecoyType 


class PeakIndex:
    """
    Cython implementation of _PeakIndex

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1PeakIndex.html>`_

    Index of a peak or feature
    
    This struct can be used to store both peak or feature indices
    """
    
    peak: int
    
    spectrum: int
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void PeakIndex()
        """
        ...
    
    @overload
    def __init__(self, in_0: PeakIndex ) -> None:
        """
        Cython signature: void PeakIndex(PeakIndex &)
        """
        ...
    
    @overload
    def __init__(self, peak: int ) -> None:
        """
        Cython signature: void PeakIndex(size_t peak)
        """
        ...
    
    @overload
    def __init__(self, spectrum: int , peak: int ) -> None:
        """
        Cython signature: void PeakIndex(size_t spectrum, size_t peak)
        """
        ...
    
    def isValid(self) -> bool:
        """
        Cython signature: bool isValid()
        Returns if the current peak ref is valid
        """
        ...
    
    def clear(self) -> None:
        """
        Cython signature: void clear()
        Invalidates the current index
        """
        ...
    
    def getFeature(self, map_: FeatureMap ) -> Feature:
        """
        Cython signature: Feature getFeature(FeatureMap & map_)
        Returns the feature (or consensus feature) corresponding to this index
        
        This method is intended for arrays of features e.g. FeatureMap
        
        The main advantage of using this method instead accessing the data directly is that range
        check performed in debug mode
        
        :raises:
          Exception: Precondition is thrown if this index is invalid for the `map` (only in debug mode)
        """
        ...
    
    def getPeak(self, map_: MSExperiment ) -> Peak1D:
        """
        Cython signature: Peak1D getPeak(MSExperiment & map_)
        Returns a peak corresponding to this index
        
        This method is intended for arrays of DSpectra e.g. MSExperiment
        
        The main advantage of using this method instead accessing the data directly is that range
        check performed in debug mode
        
        :raises:
          Exception: Precondition is thrown if this index is invalid for the `map` (only in debug mode)
        """
        ...
    
    def getSpectrum(self, map_: MSExperiment ) -> MSSpectrum:
        """
        Cython signature: MSSpectrum getSpectrum(MSExperiment & map_)
        Returns a spectrum corresponding to this index
        
        This method is intended for arrays of DSpectra e.g. MSExperiment
        
        The main advantage of using this method instead accessing the data directly is that range
        check performed in debug mode
        
        :raises:
          Exception: Precondition is thrown if this index is invalid for the `map` (only in debug mode)
        """
        ...
    
    def __richcmp__(self, other: PeakIndex, op: int) -> Any:
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


class ProbablePhosphoSites:
    """
    Cython implementation of _ProbablePhosphoSites

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1ProbablePhosphoSites.html>`_
    """
    
    first: int
    
    second: int
    
    seq_1: int
    
    seq_2: int
    
    peak_depth: int
    
    AScore: int
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void ProbablePhosphoSites()
        """
        ...
    
    @overload
    def __init__(self, in_0: ProbablePhosphoSites ) -> None:
        """
        Cython signature: void ProbablePhosphoSites(ProbablePhosphoSites &)
        """
        ... 


class ReactionMonitoringTransition:
    """
    Cython implementation of _ReactionMonitoringTransition

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1ReactionMonitoringTransition.html>`_
      -- Inherits from ['CVTermList']

    This class stores a SRM/MRM transition
    
    This class is capable of representing a <Transition> tag in a TraML
    document completely and contains all associated information
    
    The default values for precursor m/z is 0.0 which indicates that it is
    uninitialized
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void ReactionMonitoringTransition()
        """
        ...
    
    @overload
    def __init__(self, in_0: ReactionMonitoringTransition ) -> None:
        """
        Cython signature: void ReactionMonitoringTransition(ReactionMonitoringTransition &)
        """
        ...
    
    def getName(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getName()
        """
        ...
    
    def getNativeID(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getNativeID()
        """
        ...
    
    def getPeptideRef(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getPeptideRef()
        """
        ...
    
    def setName(self, name: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setName(String name)
        """
        ...
    
    def setNativeID(self, name: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setNativeID(String name)
        """
        ...
    
    def setPeptideRef(self, peptide_ref: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setPeptideRef(String peptide_ref)
        """
        ...
    
    def getProductMZ(self) -> float:
        """
        Cython signature: double getProductMZ()
        """
        ...
    
    def setProductMZ(self, in_0: float ) -> None:
        """
        Cython signature: void setProductMZ(double)
        """
        ...
    
    def getPrecursorMZ(self) -> float:
        """
        Cython signature: double getPrecursorMZ()
        Returns the precursor mz (Q1 value)
        """
        ...
    
    def setPrecursorMZ(self, in_0: float ) -> None:
        """
        Cython signature: void setPrecursorMZ(double)
        Sets the precursor mz (Q1 value)
        """
        ...
    
    def getDecoyTransitionType(self) -> int:
        """
        Cython signature: DecoyTransitionType getDecoyTransitionType()
        Returns the type of transition (target or decoy)
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
    
    def hasPrecursorCVTerms(self) -> bool:
        """
        Cython signature: bool hasPrecursorCVTerms()
        Returns true if precursor CV Terms exist (means it is safe to call getPrecursorCVTermList)
        """
        ...
    
    def setPrecursorCVTermList(self, list_: CVTermList ) -> None:
        """
        Cython signature: void setPrecursorCVTermList(CVTermList & list_)
        Sets a list of precursor CV Terms
        """
        ...
    
    def addPrecursorCVTerm(self, cv_term: CVTerm ) -> None:
        """
        Cython signature: void addPrecursorCVTerm(CVTerm & cv_term)
        Adds precursor CV Term
        """
        ...
    
    def getPrecursorCVTermList(self) -> CVTermList:
        """
        Cython signature: CVTermList getPrecursorCVTermList()
        Obtains the list of CV Terms for the precursor
        """
        ...
    
    def addProductCVTerm(self, cv_term: CVTerm ) -> None:
        """
        Cython signature: void addProductCVTerm(CVTerm & cv_term)
        """
        ...
    
    def getIntermediateProducts(self) -> List[TraMLProduct]:
        """
        Cython signature: libcpp_vector[TraMLProduct] getIntermediateProducts()
        """
        ...
    
    def addIntermediateProduct(self, product: TraMLProduct ) -> None:
        """
        Cython signature: void addIntermediateProduct(TraMLProduct product)
        """
        ...
    
    def setIntermediateProducts(self, products: List[TraMLProduct] ) -> None:
        """
        Cython signature: void setIntermediateProducts(libcpp_vector[TraMLProduct] & products)
        """
        ...
    
    def setProduct(self, product: TraMLProduct ) -> None:
        """
        Cython signature: void setProduct(TraMLProduct product)
        """
        ...
    
    def getProduct(self) -> TraMLProduct:
        """
        Cython signature: TraMLProduct getProduct()
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
    
    def setPrediction(self, prediction: Prediction ) -> None:
        """
        Cython signature: void setPrediction(Prediction & prediction)
        Sets prediction
        """
        ...
    
    def addPredictionTerm(self, prediction: CVTerm ) -> None:
        """
        Cython signature: void addPredictionTerm(CVTerm & prediction)
        Adds prediction term
        """
        ...
    
    def hasPrediction(self) -> bool:
        """
        Cython signature: bool hasPrediction()
        Returns true if a Prediction object exists (means it is safe to call getPrediction)
        """
        ...
    
    def getPrediction(self) -> Prediction:
        """
        Cython signature: Prediction getPrediction()
        Obtains the Prediction object
        """
        ...
    
    def setDecoyTransitionType(self, d: int ) -> None:
        """
        Cython signature: void setDecoyTransitionType(DecoyTransitionType & d)
        Sets the type of transition (target or decoy)
        """
        ...
    
    def getLibraryIntensity(self) -> float:
        """
        Cython signature: double getLibraryIntensity()
        Returns the library intensity (ion count or normalized ion count from a spectral library)
        """
        ...
    
    def setLibraryIntensity(self, intensity: float ) -> None:
        """
        Cython signature: void setLibraryIntensity(double intensity)
        Sets the library intensity (ion count or normalized ion count from a spectral library)
        """
        ...
    
    def getProductChargeState(self) -> int:
        """
        Cython signature: int getProductChargeState()
        Returns the charge state of the product
        """
        ...
    
    def isProductChargeStateSet(self) -> bool:
        """
        Cython signature: bool isProductChargeStateSet()
        Returns true if charge state of product is already set
        """
        ...
    
    def isDetectingTransition(self) -> bool:
        """
        Cython signature: bool isDetectingTransition()
        """
        ...
    
    def setDetectingTransition(self, val: bool ) -> None:
        """
        Cython signature: void setDetectingTransition(bool val)
        """
        ...
    
    def isIdentifyingTransition(self) -> bool:
        """
        Cython signature: bool isIdentifyingTransition()
        """
        ...
    
    def setIdentifyingTransition(self, val: bool ) -> None:
        """
        Cython signature: void setIdentifyingTransition(bool val)
        """
        ...
    
    def isQuantifyingTransition(self) -> bool:
        """
        Cython signature: bool isQuantifyingTransition()
        """
        ...
    
    def setQuantifyingTransition(self, val: bool ) -> None:
        """
        Cython signature: void setQuantifyingTransition(bool val)
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
    
    def __richcmp__(self, other: ReactionMonitoringTransition, op: int) -> Any:
        ... 


class SpectralDeconvolution:
    """
    Cython implementation of _SpectralDeconvolution

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1SpectralDeconvolution.html>`_
      -- Inherits from ['DefaultParamHandler']

    Spectral deconvolution algorithm for top-down MS.
    From MSSpectrum, this class outputs DeconvolvedSpectrum.
    Deconvolution takes three steps:
      i) decharging and select candidate masses - speed up via binning
      ii) collecting isotopes from the candidate masses and deisotoping
      iii) scoring and filter out low scoring masses
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void SpectralDeconvolution()
        """
        ...
    
    @overload
    def __init__(self, in_0: SpectralDeconvolution ) -> None:
        """
        Cython signature: void SpectralDeconvolution(SpectralDeconvolution &)
        """
        ...
    
    def performSpectrumDeconvolution(self, spec: MSSpectrum , scan_number: int , precursor_peak_group: PeakGroup ) -> None:
        """
        Cython signature: void performSpectrumDeconvolution(MSSpectrum & spec, int scan_number, PeakGroup & precursor_peak_group)
        Main deconvolution function that generates the deconvolved spectrum.
        :param spec: The original spectrum
        :param scan_number: Scan number from input spectrum
        :param precursor_peak_group: Precursor peak group (for MS2+)
        """
        ...
    
    def getDeconvolvedSpectrum(self) -> DeconvolvedSpectrum:
        """
        Cython signature: DeconvolvedSpectrum getDeconvolvedSpectrum()
        """
        ...
    
    def getAveragine(self) -> PrecalAveragine:
        """
        Cython signature: PrecalAveragine getAveragine()
        """
        ...
    
    def setAveragine(self, avg: PrecalAveragine ) -> None:
        """
        Cython signature: void setAveragine(PrecalAveragine & avg)
        """
        ...
    
    def setTargetMasses(self, masses: List[float] , exclude: bool ) -> None:
        """
        Cython signature: void setTargetMasses(libcpp_vector[double] & masses, bool exclude)
        """
        ...
    
    def calculateAveragine(self, use_RNA_averagine: bool ) -> None:
        """
        Cython signature: void calculateAveragine(bool use_RNA_averagine)
        """
        ...
    
    def setToleranceEstimation(self) -> None:
        """
        Cython signature: void setToleranceEstimation()
        """
        ...
    
    def setTargetDecoyType(self, target_decoy_type: int , target_dspec: DeconvolvedSpectrum ) -> None:
        """
        Cython signature: void setTargetDecoyType(TargetDecoyType target_decoy_type, DeconvolvedSpectrum & target_dspec)
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
    
    getCosine: __static_SpectralDeconvolution_getCosine
    
    getIsotopeCosineAndIsoOffset: __static_SpectralDeconvolution_getIsotopeCosineAndIsoOffset
    
    getNominalMass: __static_SpectralDeconvolution_getNominalMass 


class SqrtScaler:
    """
    Cython implementation of _SqrtScaler

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1SqrtScaler.html>`_
      -- Inherits from ['DefaultParamHandler']

    Scales the intensity of peaks to the sqrt
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void SqrtScaler()
        """
        ...
    
    @overload
    def __init__(self, in_0: SqrtScaler ) -> None:
        """
        Cython signature: void SqrtScaler(SqrtScaler &)
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


class TMTSixPlexQuantitationMethod:
    """
    Cython implementation of _TMTSixPlexQuantitationMethod

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1TMTSixPlexQuantitationMethod.html>`_
      -- Inherits from ['IsobaricQuantitationMethod']
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void TMTSixPlexQuantitationMethod()
        """
        ...
    
    @overload
    def __init__(self, in_0: TMTSixPlexQuantitationMethod ) -> None:
        """
        Cython signature: void TMTSixPlexQuantitationMethod(TMTSixPlexQuantitationMethod &)
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


class TargetedExperiment:
    """
    Cython implementation of _TargetedExperiment

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1TargetedExperiment.html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void TargetedExperiment()
        """
        ...
    
    @overload
    def __init__(self, in_0: TargetedExperiment ) -> None:
        """
        Cython signature: void TargetedExperiment(TargetedExperiment &)
        """
        ...
    
    def __add__(self: TargetedExperiment, other: TargetedExperiment) -> TargetedExperiment:
        ...
    
    def __iadd__(self: TargetedExperiment, other: TargetedExperiment) -> TargetedExperiment:
        ...
    
    def clear(self, clear_meta_data: bool ) -> None:
        """
        Cython signature: void clear(bool clear_meta_data)
        """
        ...
    
    def sortTransitionsByProductMZ(self) -> None:
        """
        Cython signature: void sortTransitionsByProductMZ()
        """
        ...
    
    def setCVs(self, cvs: List[CV] ) -> None:
        """
        Cython signature: void setCVs(libcpp_vector[CV] cvs)
        """
        ...
    
    def getCVs(self) -> List[CV]:
        """
        Cython signature: libcpp_vector[CV] getCVs()
        """
        ...
    
    def addCV(self, cv: CV ) -> None:
        """
        Cython signature: void addCV(CV cv)
        """
        ...
    
    def setContacts(self, contacts: List[Contact] ) -> None:
        """
        Cython signature: void setContacts(libcpp_vector[Contact] contacts)
        """
        ...
    
    def getContacts(self) -> List[Contact]:
        """
        Cython signature: libcpp_vector[Contact] getContacts()
        """
        ...
    
    def addContact(self, contact: Contact ) -> None:
        """
        Cython signature: void addContact(Contact contact)
        """
        ...
    
    def setPublications(self, publications: List[Publication] ) -> None:
        """
        Cython signature: void setPublications(libcpp_vector[Publication] publications)
        """
        ...
    
    def getPublications(self) -> List[Publication]:
        """
        Cython signature: libcpp_vector[Publication] getPublications()
        """
        ...
    
    def addPublication(self, publication: Publication ) -> None:
        """
        Cython signature: void addPublication(Publication publication)
        """
        ...
    
    def setTargetCVTerms(self, cv_terms: CVTermList ) -> None:
        """
        Cython signature: void setTargetCVTerms(CVTermList cv_terms)
        """
        ...
    
    def getTargetCVTerms(self) -> CVTermList:
        """
        Cython signature: CVTermList getTargetCVTerms()
        """
        ...
    
    def addTargetCVTerm(self, cv_term: CVTerm ) -> None:
        """
        Cython signature: void addTargetCVTerm(CVTerm cv_term)
        """
        ...
    
    def setTargetMetaValue(self, name: Union[bytes, str, String] , value: Union[int, float, bytes, str, List[int], List[float], List[bytes]] ) -> None:
        """
        Cython signature: void setTargetMetaValue(String name, DataValue value)
        """
        ...
    
    def setInstruments(self, instruments: List[TargetedExperiment_Instrument] ) -> None:
        """
        Cython signature: void setInstruments(libcpp_vector[TargetedExperiment_Instrument] instruments)
        """
        ...
    
    def getInstruments(self) -> List[TargetedExperiment_Instrument]:
        """
        Cython signature: libcpp_vector[TargetedExperiment_Instrument] getInstruments()
        """
        ...
    
    def addInstrument(self, instrument: TargetedExperiment_Instrument ) -> None:
        """
        Cython signature: void addInstrument(TargetedExperiment_Instrument instrument)
        """
        ...
    
    def setSoftware(self, software: List[Software] ) -> None:
        """
        Cython signature: void setSoftware(libcpp_vector[Software] software)
        """
        ...
    
    def getSoftware(self) -> List[Software]:
        """
        Cython signature: libcpp_vector[Software] getSoftware()
        """
        ...
    
    def addSoftware(self, software: Software ) -> None:
        """
        Cython signature: void addSoftware(Software software)
        """
        ...
    
    def setProteins(self, proteins: List[Protein] ) -> None:
        """
        Cython signature: void setProteins(libcpp_vector[Protein] proteins)
        """
        ...
    
    def getProteins(self) -> List[Protein]:
        """
        Cython signature: libcpp_vector[Protein] getProteins()
        """
        ...
    
    def getProteinByRef(self, ref: Union[bytes, str, String] ) -> Protein:
        """
        Cython signature: Protein getProteinByRef(String ref)
        """
        ...
    
    def hasProtein(self, ref: Union[bytes, str, String] ) -> bool:
        """
        Cython signature: bool hasProtein(String ref)
        """
        ...
    
    def addProtein(self, protein: Protein ) -> None:
        """
        Cython signature: void addProtein(Protein protein)
        """
        ...
    
    def setCompounds(self, rhs: List[Compound] ) -> None:
        """
        Cython signature: void setCompounds(libcpp_vector[Compound] rhs)
        """
        ...
    
    def getCompounds(self) -> List[Compound]:
        """
        Cython signature: libcpp_vector[Compound] getCompounds()
        """
        ...
    
    def addCompound(self, rhs: Compound ) -> None:
        """
        Cython signature: void addCompound(Compound rhs)
        """
        ...
    
    def hasCompound(self, ref: Union[bytes, str, String] ) -> bool:
        """
        Cython signature: bool hasCompound(String ref)
        """
        ...
    
    def getCompoundByRef(self, ref: Union[bytes, str, String] ) -> Compound:
        """
        Cython signature: Compound getCompoundByRef(String ref)
        """
        ...
    
    def setPeptides(self, rhs: List[Peptide] ) -> None:
        """
        Cython signature: void setPeptides(libcpp_vector[Peptide] rhs)
        """
        ...
    
    def getPeptides(self) -> List[Peptide]:
        """
        Cython signature: libcpp_vector[Peptide] getPeptides()
        """
        ...
    
    def hasPeptide(self, ref: Union[bytes, str, String] ) -> bool:
        """
        Cython signature: bool hasPeptide(String ref)
        """
        ...
    
    def getPeptideByRef(self, ref: Union[bytes, str, String] ) -> Peptide:
        """
        Cython signature: Peptide getPeptideByRef(String ref)
        """
        ...
    
    def addPeptide(self, rhs: Peptide ) -> None:
        """
        Cython signature: void addPeptide(Peptide rhs)
        """
        ...
    
    def setTransitions(self, transitions: List[ReactionMonitoringTransition] ) -> None:
        """
        Cython signature: void setTransitions(libcpp_vector[ReactionMonitoringTransition] transitions)
        """
        ...
    
    def getTransitions(self) -> List[ReactionMonitoringTransition]:
        """
        Cython signature: libcpp_vector[ReactionMonitoringTransition] getTransitions()
        """
        ...
    
    def addTransition(self, transition: ReactionMonitoringTransition ) -> None:
        """
        Cython signature: void addTransition(ReactionMonitoringTransition transition)
        """
        ...
    
    def setIncludeTargets(self, targets: List[IncludeExcludeTarget] ) -> None:
        """
        Cython signature: void setIncludeTargets(libcpp_vector[IncludeExcludeTarget] targets)
        """
        ...
    
    def getIncludeTargets(self) -> List[IncludeExcludeTarget]:
        """
        Cython signature: libcpp_vector[IncludeExcludeTarget] getIncludeTargets()
        """
        ...
    
    def addIncludeTarget(self, target: IncludeExcludeTarget ) -> None:
        """
        Cython signature: void addIncludeTarget(IncludeExcludeTarget target)
        """
        ...
    
    def setExcludeTargets(self, targets: List[IncludeExcludeTarget] ) -> None:
        """
        Cython signature: void setExcludeTargets(libcpp_vector[IncludeExcludeTarget] targets)
        """
        ...
    
    def getExcludeTargets(self) -> List[IncludeExcludeTarget]:
        """
        Cython signature: libcpp_vector[IncludeExcludeTarget] getExcludeTargets()
        """
        ...
    
    def addExcludeTarget(self, target: IncludeExcludeTarget ) -> None:
        """
        Cython signature: void addExcludeTarget(IncludeExcludeTarget target)
        """
        ...
    
    def setSourceFiles(self, source_files: List[SourceFile] ) -> None:
        """
        Cython signature: void setSourceFiles(libcpp_vector[SourceFile] source_files)
        """
        ...
    
    def getSourceFiles(self) -> List[SourceFile]:
        """
        Cython signature: libcpp_vector[SourceFile] getSourceFiles()
        """
        ...
    
    def addSourceFile(self, source_file: SourceFile ) -> None:
        """
        Cython signature: void addSourceFile(SourceFile source_file)
        """
        ...
    
    def containsInvalidReferences(self) -> bool:
        """
        Cython signature: bool containsInvalidReferences()
        """
        ...
    
    def __richcmp__(self, other: TargetedExperiment, op: int) -> Any:
        ... 


class TheoreticalSpectrumGeneratorXLMS:
    """
    Cython implementation of _TheoreticalSpectrumGeneratorXLMS

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1TheoreticalSpectrumGeneratorXLMS.html>`_
      -- Inherits from ['DefaultParamHandler']
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void TheoreticalSpectrumGeneratorXLMS()
        """
        ...
    
    @overload
    def __init__(self, in_0: TheoreticalSpectrumGeneratorXLMS ) -> None:
        """
        Cython signature: void TheoreticalSpectrumGeneratorXLMS(TheoreticalSpectrumGeneratorXLMS &)
        """
        ...
    
    def getLinearIonSpectrum(self, spectrum: MSSpectrum , peptide: AASequence , link_pos: int , frag_alpha: bool , charge: int , link_pos_2: int ) -> None:
        """
        Cython signature: void getLinearIonSpectrum(MSSpectrum & spectrum, AASequence peptide, size_t link_pos, bool frag_alpha, int charge, size_t link_pos_2)
            Generates fragment ions not containing the cross-linker for one peptide
        
            B-ions are generated from the beginning of the peptide up to the first linked position,
            y-ions are generated from the second linked position up the end of the peptide.
            If link_pos_2 is 0, a mono-link or cross-link is assumed and the second position is the same as the first position.
            For a loop-link two different positions can be set and link_pos_2 must be larger than link_pos
            The generated ion types and other additional settings are determined by the tool parameters
        
            :param spectrum: The spectrum to which the new peaks are added. Does not have to be empty, the generated peaks will be pushed onto it
            :param peptide: The peptide to fragment
            :param link_pos: The position of the cross-linker on the given peptide
            :param frag_alpha: True, if the fragmented peptide is the Alpha peptide. Used for ion-name annotation
            :param charge: The maximal charge of the ions
            :param link_pos_2: A second position for the linker, in case it is a loop link
        """
        ...
    
    @overload
    def getXLinkIonSpectrum(self, spectrum: MSSpectrum , peptide: AASequence , link_pos: int , precursor_mass: float , frag_alpha: bool , mincharge: int , maxcharge: int , link_pos_2: int ) -> None:
        """
        Cython signature: void getXLinkIonSpectrum(MSSpectrum & spectrum, AASequence peptide, size_t link_pos, double precursor_mass, bool frag_alpha, int mincharge, int maxcharge, size_t link_pos_2)
            Generates fragment ions containing the cross-linker for one peptide
        
            B-ions are generated from the first linked position up to the end of the peptide,
            y-ions are generated from the beginning of the peptide up to the second linked position.
            If link_pos_2 is 0, a mono-link or cross-link is assumed and the second position is the same as the first position.
            For a loop-link two different positions can be set and link_pos_2 must be larger than link_pos.
            Since in the case of a cross-link a whole second peptide is attached to the other side of the cross-link,
            a precursor mass for the two peptides and the linker is needed.
            In the case of a loop link the precursor mass is the mass of the only peptide and the linker.
            Although this function is more general, currently it is mainly used for loop-links and mono-links,
            because residues in the second, unknown peptide cannot be considered for possible neutral losses.
            The generated ion types and other additional settings are determined by the tool parameters
        
            :param spectrum: The spectrum to which the new peaks are added. Does not have to be empty, the generated peaks will be pushed onto it
            :param peptide: The peptide to fragment
            :param link_pos: The position of the cross-linker on the given peptide
            :param precursor_mass: The mass of the whole cross-link candidate or the precursor mass of the experimental MS2 spectrum.
            :param frag_alpha: True, if the fragmented peptide is the Alpha peptide. Used for ion-name annotation.
            :param mincharge: The minimal charge of the ions
            :param maxcharge: The maximal charge of the ions, it should be the precursor charge and is used to generate precursor ion peaks
            :param link_pos_2: A second position for the linker, in case it is a loop link
        """
        ...
    
    @overload
    def getXLinkIonSpectrum(self, spectrum: MSSpectrum , crosslink: ProteinProteinCrossLink , frag_alpha: bool , mincharge: int , maxcharge: int ) -> None:
        """
        Cython signature: void getXLinkIonSpectrum(MSSpectrum & spectrum, ProteinProteinCrossLink crosslink, bool frag_alpha, int mincharge, int maxcharge)
            Generates fragment ions containing the cross-linker for a pair of peptides
        
            B-ions are generated from the first linked position up to the end of the peptide,
            y-ions are generated from the beginning of the peptide up to the second linked position.
            This function generates neutral loss ions by considering both linked peptides.
            Only one of the peptides, decided by @frag_alpha, is fragmented.
            This function is not suitable to generate fragments for mono-links or loop-links.
            This simplifies the function, but it has to be called twice to get all fragments of a peptide pair.
            The generated ion types and other additional settings are determined by the tool parameters
        
            :param spectrum: The spectrum to which the new peaks are added. Does not have to be empty, the generated peaks will be pushed onto it
            :param crosslink: ProteinProteinCrossLink to be fragmented
            :param link_pos: The position of the cross-linker on the given peptide
            :param precursor_mass: The mass of the whole cross-link candidate or the precursor mass of the experimental MS2 spectrum
            :param frag_alpha: True, if the fragmented peptide is the Alpha peptide
            :param mincharge: The minimal charge of the ions
            :param maxcharge: The maximal charge of the ions, it should be the precursor charge and is used to generate precursor ion peaks
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


class TransformationModelLowess:
    """
    Cython implementation of _TransformationModelLowess

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1TransformationModelLowess.html>`_
      -- Inherits from ['TransformationModel']
    """
    
    def __init__(self, data: List[TM_DataPoint] , params: Param ) -> None:
        """
        Cython signature: void TransformationModelLowess(libcpp_vector[TM_DataPoint] & data, Param & params)
        """
        ...
    
    def getDefaultParameters(self, in_0: Param ) -> None:
        """
        Cython signature: void getDefaultParameters(Param &)
        """
        ...
    
    def evaluate(self, value: float ) -> float:
        """
        Cython signature: double evaluate(double value)
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
    
    getDefaultParameters: __static_TransformationModelLowess_getDefaultParameters 


class XTandemInfile:
    """
    Cython implementation of _XTandemInfile

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1XTandemInfile.html>`_
    """
    
    def __init__(self) -> None:
        """
        Cython signature: void XTandemInfile()
        """
        ...
    
    def setFragmentMassTolerance(self, tolerance: float ) -> None:
        """
        Cython signature: void setFragmentMassTolerance(double tolerance)
        """
        ...
    
    def getFragmentMassTolerance(self) -> float:
        """
        Cython signature: double getFragmentMassTolerance()
        """
        ...
    
    def setPrecursorMassTolerancePlus(self, tol: float ) -> None:
        """
        Cython signature: void setPrecursorMassTolerancePlus(double tol)
        """
        ...
    
    def getPrecursorMassTolerancePlus(self) -> float:
        """
        Cython signature: double getPrecursorMassTolerancePlus()
        """
        ...
    
    def setPrecursorMassToleranceMinus(self, tol: float ) -> None:
        """
        Cython signature: void setPrecursorMassToleranceMinus(double tol)
        """
        ...
    
    def getPrecursorMassToleranceMinus(self) -> float:
        """
        Cython signature: double getPrecursorMassToleranceMinus()
        """
        ...
    
    def setPrecursorErrorType(self, mono_isotopic: int ) -> None:
        """
        Cython signature: void setPrecursorErrorType(MassType mono_isotopic)
        """
        ...
    
    def getPrecursorErrorType(self) -> int:
        """
        Cython signature: MassType getPrecursorErrorType()
        """
        ...
    
    def setFragmentMassErrorUnit(self, unit: int ) -> None:
        """
        Cython signature: void setFragmentMassErrorUnit(ErrorUnit unit)
        """
        ...
    
    def getFragmentMassErrorUnit(self) -> int:
        """
        Cython signature: ErrorUnit getFragmentMassErrorUnit()
        """
        ...
    
    def setPrecursorMassErrorUnit(self, unit: int ) -> None:
        """
        Cython signature: void setPrecursorMassErrorUnit(ErrorUnit unit)
        """
        ...
    
    def getPrecursorMassErrorUnit(self) -> int:
        """
        Cython signature: ErrorUnit getPrecursorMassErrorUnit()
        """
        ...
    
    def setNumberOfThreads(self, threads: int ) -> None:
        """
        Cython signature: void setNumberOfThreads(unsigned int threads)
        """
        ...
    
    def getNumberOfThreads(self) -> int:
        """
        Cython signature: unsigned int getNumberOfThreads()
        """
        ...
    
    def setModifications(self, mods: ModificationDefinitionsSet ) -> None:
        """
        Cython signature: void setModifications(ModificationDefinitionsSet & mods)
        """
        ...
    
    def getModifications(self) -> ModificationDefinitionsSet:
        """
        Cython signature: ModificationDefinitionsSet getModifications()
        """
        ...
    
    def setOutputFilename(self, output: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setOutputFilename(const String & output)
        """
        ...
    
    def getOutputFilename(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getOutputFilename()
        """
        ...
    
    def setInputFilename(self, input_file: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setInputFilename(const String & input_file)
        """
        ...
    
    def getInputFilename(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getInputFilename()
        """
        ...
    
    def setTaxonomyFilename(self, filename: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setTaxonomyFilename(const String & filename)
        """
        ...
    
    def getTaxonomyFilename(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getTaxonomyFilename()
        """
        ...
    
    def setDefaultParametersFilename(self, filename: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setDefaultParametersFilename(const String & filename)
        """
        ...
    
    def getDefaultParametersFilename(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getDefaultParametersFilename()
        """
        ...
    
    def setTaxon(self, taxon: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setTaxon(const String & taxon)
        """
        ...
    
    def getTaxon(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getTaxon()
        """
        ...
    
    def setMaxPrecursorCharge(self, max_charge: int ) -> None:
        """
        Cython signature: void setMaxPrecursorCharge(int max_charge)
        """
        ...
    
    def getMaxPrecursorCharge(self) -> int:
        """
        Cython signature: int getMaxPrecursorCharge()
        """
        ...
    
    def setNumberOfMissedCleavages(self, missed_cleavages: int ) -> None:
        """
        Cython signature: void setNumberOfMissedCleavages(unsigned int missed_cleavages)
        """
        ...
    
    def getNumberOfMissedCleavages(self) -> int:
        """
        Cython signature: unsigned int getNumberOfMissedCleavages()
        """
        ...
    
    def setOutputResults(self, result: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setOutputResults(String result)
        """
        ...
    
    def getOutputResults(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getOutputResults()
        """
        ...
    
    def setMaxValidEValue(self, value: float ) -> None:
        """
        Cython signature: void setMaxValidEValue(double value)
        """
        ...
    
    def getMaxValidEValue(self) -> float:
        """
        Cython signature: double getMaxValidEValue()
        """
        ...
    
    def setSemiCleavage(self, semi_cleavage: bool ) -> None:
        """
        Cython signature: void setSemiCleavage(bool semi_cleavage)
        """
        ...
    
    def setAllowIsotopeError(self, allow_isotope_error: bool ) -> None:
        """
        Cython signature: void setAllowIsotopeError(bool allow_isotope_error)
        """
        ...
    
    def write(self, filename: Union[bytes, str, String] , ignore_member_parameters: bool , force_default_mods: bool ) -> None:
        """
        Cython signature: void write(String filename, bool ignore_member_parameters, bool force_default_mods)
        """
        ...
    
    def setCleavageSite(self, cleavage_site: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setCleavageSite(String cleavage_site)
        """
        ...
    
    def getCleavageSite(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getCleavageSite()
        """
        ...
    ErrorUnit : __ErrorUnit
    MassType : __MassType 


class DataType:
    None
    STRING_VALUE : int
    INT_VALUE : int
    DOUBLE_VALUE : int
    STRING_LIST : int
    INT_LIST : int
    DOUBLE_LIST : int
    EMPTY_VALUE : int

    def getMapping(self) -> Dict[int, str]:
       ... 


class DecoyTransitionType:
    None
    UNKNOWN : int
    TARGET : int
    DECOY : int

    def getMapping(self) -> Dict[int, str]:
       ... 


class __ErrorUnit:
    None
    DALTONS : int
    PPM : int

    def getMapping(self) -> Dict[int, str]:
       ... 


class MZTrafoModel_MODELTYPE:
    None
    LINEAR : int
    LINEAR_WEIGHTED : int
    QUADRATIC : int
    QUADRATIC_WEIGHTED : int
    SIZE_OF_MODELTYPE : int

    def getMapping(self) -> Dict[int, str]:
       ... 


class __MassType:
    None
    MONOISOTOPIC : int
    AVERAGE : int

    def getMapping(self) -> Dict[int, str]:
       ... 


class NormalizationMethod:
    None
    NM_SCALE : int
    NM_SHIFT : int

    def getMapping(self) -> Dict[int, str]:
       ... 


class __PeptidePosition:
    None
    INTERNAL : int
    C_TERM : int
    N_TERM : int

    def getMapping(self) -> Dict[int, str]:
       ... 


class __ProteinProteinCrossLinkType:
    None
    CROSS : int
    MONO : int
    LOOP : int
    NUMBER_OF_CROSS_LINK_TYPES : int

    def getMapping(self) -> Dict[int, str]:
       ... 


class __RETURN_STATUS:
    None
    SOLVED : int
    ITERATION_EXCEEDED : int

    def getMapping(self) -> Dict[int, str]:
       ... 


class __TargetDecoyType:
    None
    target : int
    noise_decoy : int
    signal_decoy : int

    def getMapping(self) -> Dict[int, str]:
       ... 


class UnitType:
    None
    UNIT_ONTOLOGY : int
    MS_ONTOLOGY : int
    OTHER : int

    def getMapping(self) -> Dict[int, str]:
       ... 


class ValueType:
    None
    STRING_VALUE : int
    INT_VALUE : int
    DOUBLE_VALUE : int
    STRING_LIST : int
    INT_LIST : int
    DOUBLE_LIST : int
    EMPTY_VALUE : int

    def getMapping(self) -> Dict[int, str]:
       ... 

