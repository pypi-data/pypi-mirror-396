from __future__ import annotations
from typing import overload, Any, List, Dict, Tuple, Set, Sequence, Union
from pyopenms import *  # pylint: disable=wildcard-import; lgtm(py/polluting-import)
import numpy as _np

from enum import IntEnum as _PyEnum


def __static_FeatureMapping_assignMS2IndexToFeature(spectra: MSExperiment , fm_info: FeatureMapping_FeatureMappingInfo , precursor_mz_tolerance: float , precursor_rt_tolerance: float , ppm: bool ) -> FeatureMapping_FeatureToMs2Indices:
    """
    Cython signature: FeatureMapping_FeatureToMs2Indices assignMS2IndexToFeature(MSExperiment & spectra, FeatureMapping_FeatureMappingInfo & fm_info, double precursor_mz_tolerance, double precursor_rt_tolerance, bool ppm)
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

def __static_FLASHHelperClasses_getChargeMass(positive_ionization_mode: bool ) -> float:
    """
    Cython signature: float getChargeMass(bool positive_ionization_mode)
    """
    ...

def __static_FLASHHelperClasses_getLogMz(mz: float , positive: bool ) -> float:
    """
    Cython signature: double getLogMz(double mz, bool positive)
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

def __static_PercolatorInfile_store(pin_file: Union[bytes, str, String] , peptide_ids: PeptideIdentificationList , feature_set: List[bytes] , in_3: bytes , min_charge: int , max_charge: int ) -> None:
    """
    Cython signature: void store(String pin_file, PeptideIdentificationList peptide_ids, StringList feature_set, libcpp_string, int min_charge, int max_charge)
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


class BasicProteinInferenceAlgorithm:
    """
    Cython implementation of _BasicProteinInferenceAlgorithm

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1BasicProteinInferenceAlgorithm.html>`_
      -- Inherits from ['DefaultParamHandler', 'ProgressLogger']

    Algorithm class that implements simple protein inference by aggregation of peptide scores.
    
    It has multiple parameter options like the aggregation method, when to distinguish peptidoforms,
    and if you want to use shared peptides ("use_shared_peptides").
    First, the best PSM per spectrum is used, then only the best PSM per peptidoform is aggregated.
    Peptidoforms can optionally be distinguished via the treat_X_separate parameters:
    - Modifications (modified sequence string)
    - Charge states
    The algorithm assumes posteriors or posterior error probabilities and converts to posteriors initially.
    Possible aggregation methods that can be set via the parameter "aggregation_method" are:
    - "best" (default)
    - "sum"
    - "product" (ignoring zeroes)
    Annotation of the number of peptides used for aggregation can be disabled (see parameters).
    Supports multiple runs but goes through them one by one iterating over the full PeptideIdentification vector.
    Warning: Does not "link" the peptides to the resulting protein run. If you wish to do that you have to do
    it manually.
    
    Usage:
    """
    
    def __init__(self) -> None:
        """
        Cython signature: void BasicProteinInferenceAlgorithm()
        """
        ...
    
    @overload
    def run(self, pep_ids: PeptideIdentificationList , prot_ids: List[ProteinIdentification] ) -> None:
        """
        Cython signature: void run(PeptideIdentificationList & pep_ids, libcpp_vector[ProteinIdentification] & prot_ids)
        Performs basic aggregation-based inference per ProteinIdentification run. See class help.
        
        
        :param pep_ids: Vector of peptide identifications
        :param prot_ids: Vector of protein identification runs. Scores will be overwritten and groups added.
        :return: Writes its results into prot_ids
        """
        ...
    
    @overload
    def run(self, pep_ids: PeptideIdentificationList , prot_id: ProteinIdentification ) -> None:
        """
        Cython signature: void run(PeptideIdentificationList & pep_ids, ProteinIdentification & prot_id)
        Performs basic aggregation-based inference on single ProteinIdentification run. See class help.
        
        
        :param pep_ids: Vector of peptide identifications
        :param prot_id: ProteinIdentification run with possible proteins. Scores will be overwritten and groups added.
        :return: Writes its results into prot_ids
        """
        ...
    
    @overload
    def run(self, cmap: ConsensusMap , prot_id: ProteinIdentification , include_unassigned: bool ) -> None:
        """
        Cython signature: void run(ConsensusMap & cmap, ProteinIdentification & prot_id, bool include_unassigned)
        Performs basic aggregation-based inference on identifications in a ConsensusMap. See class help.\n
        `prot_id` should contain the union of all proteins in the map. E.g. use ConsensusMapMergerAlgorithm and
        then pass the first=merged run.
        
        
        :param cmap: ConsensusMap = Consensus features with metadata and peptide identifications
        :param prot_id: ProteinIdentification run with possible proteins. Scores will be overwritten and groups added.
        :return: Writes its results into prot_ids
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
    AggregationMethod : __AggregationMethod 


class CVMappingFile:
    """
    Cython implementation of _CVMappingFile

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1CVMappingFile.html>`_
    """
    
    def __init__(self) -> None:
        """
        Cython signature: void CVMappingFile()
        """
        ...
    
    def load(self, filename: Union[bytes, str, String] , cv_mappings: CVMappings , strip_namespaces: bool ) -> None:
        """
        Cython signature: void load(const String & filename, CVMappings & cv_mappings, bool strip_namespaces)
        Loads CvMappings from the given file
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


class DistanceMatrix:
    """
    Cython implementation of _DistanceMatrix[float]

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1DistanceMatrix[float].html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void DistanceMatrix()
        """
        ...
    
    @overload
    def __init__(self, in_0: DistanceMatrix ) -> None:
        """
        Cython signature: void DistanceMatrix(DistanceMatrix &)
        """
        ...
    
    @overload
    def __init__(self, dimensionsize: int , value: float ) -> None:
        """
        Cython signature: void DistanceMatrix(size_t dimensionsize, float value)
        """
        ...
    
    def getValue(self, i: int , j: int ) -> float:
        """
        Cython signature: float getValue(size_t i, size_t j)
        """
        ...
    
    def setValue(self, i: int , j: int , value: float ) -> None:
        """
        Cython signature: void setValue(size_t i, size_t j, float value)
        """
        ...
    
    def setValueQuick(self, i: int , j: int , value: float ) -> None:
        """
        Cython signature: void setValueQuick(size_t i, size_t j, float value)
        """
        ...
    
    def clear(self) -> None:
        """
        Cython signature: void clear()
        """
        ...
    
    def resize(self, dimensionsize: int , value: float ) -> None:
        """
        Cython signature: void resize(size_t dimensionsize, float value)
        """
        ...
    
    def reduce(self, j: int ) -> None:
        """
        Cython signature: void reduce(size_t j)
        """
        ...
    
    def dimensionsize(self) -> int:
        """
        Cython signature: size_t dimensionsize()
        """
        ...
    
    def updateMinElement(self) -> None:
        """
        Cython signature: void updateMinElement()
        """
        ...
    
    def getMinElementCoordinates(self) -> List[int, int]:
        """
        Cython signature: libcpp_pair[size_t,size_t] getMinElementCoordinates()
        """
        ...
    
    def __richcmp__(self, other: DistanceMatrix, op: int) -> Any:
        ... 


class EmgModel:
    """
    Cython implementation of _EmgModel

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1EmgModel.html>`_
      -- Inherits from ['InterpolationModel']
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void EmgModel()
        Exponentially modified gaussian distribution model for elution profiles
        """
        ...
    
    @overload
    def __init__(self, in_0: EmgModel ) -> None:
        """
        Cython signature: void EmgModel(EmgModel &)
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


class EmgScoring:
    """
    Cython implementation of _EmgScoring

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1EmgScoring.html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void EmgScoring()
        Helps in scoring of an elution peak using an exponentially modified gaussian distribution model
        """
        ...
    
    @overload
    def __init__(self, in_0: EmgScoring ) -> None:
        """
        Cython signature: void EmgScoring(EmgScoring &)
        """
        ...
    
    def setFitterParam(self, param: Param ) -> None:
        """
        Cython signature: void setFitterParam(Param param)
        """
        ...
    
    def getDefaults(self) -> Param:
        """
        Cython signature: Param getDefaults()
        """
        ...
    
    def elutionModelFit(self, current_section: '_np.ndarray[Any, _np.dtype[_np.float32]]' , smooth_data: bool ) -> float:
        """
        Cython signature: double elutionModelFit(libcpp_vector[DPosition2] current_section, bool smooth_data)
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


class FIAMSScheduler:
    """
    Cython implementation of _FIAMSScheduler

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1FIAMSScheduler.html>`_

      ADD PYTHON DOCUMENTATION HERE
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void FIAMSScheduler()
        Scheduler for FIA-MS data batches. Works with FIAMSDataProcessor
        """
        ...
    
    @overload
    def __init__(self, in_0: FIAMSScheduler ) -> None:
        """
        Cython signature: void FIAMSScheduler(FIAMSScheduler &)
        """
        ...
    
    @overload
    def __init__(self, filename: Union[bytes, str, String] , base_dir: Union[bytes, str, String] , load_cached_: bool ) -> None:
        """
        Cython signature: void FIAMSScheduler(String filename, String base_dir, bool load_cached_)
        """
        ...
    
    def run(self) -> None:
        """
        Cython signature: void run()
        Run the FIA-MS data analysis for the batch defined in the @filename_
        """
        ...
    
    def getBaseDir(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getBaseDir()
        Returns the base directory for the relevant paths from the csv file
        """
        ... 


class FLASHHelperClasses:
    """
    Cython implementation of _FLASHHelperClasses

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1FLASHHelperClasses.html>`_

    Wrapper struct for all the structs needed by FLASHDeconv.
    Contains: PrecalculatedAveragine, MassFeature, IsobaricQuantities, LogMzPeak
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void FLASHHelperClasses()
        """
        ...
    
    @overload
    def __init__(self, in_0: FLASHHelperClasses ) -> None:
        """
        Cython signature: void FLASHHelperClasses(FLASHHelperClasses &)
        """
        ...
    
    getChargeMass: __static_FLASHHelperClasses_getChargeMass
    
    getLogMz: __static_FLASHHelperClasses_getLogMz 


class FeatureGroupingAlgorithmKD:
    """
    Cython implementation of _FeatureGroupingAlgorithmKD

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1FeatureGroupingAlgorithmKD.html>`_
      -- Inherits from ['FeatureGroupingAlgorithm', 'ProgressLogger']
    """
    
    def __init__(self) -> None:
        """
        Cython signature: void FeatureGroupingAlgorithmKD()
        A feature grouping algorithm for unlabeled data
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


class FeatureMapping:
    """
    Cython implementation of _FeatureMapping

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1FeatureMapping.html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void FeatureMapping()
        """
        ...
    
    @overload
    def __init__(self, in_0: FeatureMapping ) -> None:
        """
        Cython signature: void FeatureMapping(FeatureMapping &)
        """
        ...
    
    assignMS2IndexToFeature: __static_FeatureMapping_assignMS2IndexToFeature 


class FeatureMapping_FeatureMappingInfo:
    """
    Cython implementation of _FeatureMapping_FeatureMappingInfo

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1FeatureMapping_FeatureMappingInfo.html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void FeatureMapping_FeatureMappingInfo()
        """
        ...
    
    @overload
    def __init__(self, in_0: FeatureMapping_FeatureMappingInfo ) -> None:
        """
        Cython signature: void FeatureMapping_FeatureMappingInfo(FeatureMapping_FeatureMappingInfo &)
        """
        ... 


class FeatureMapping_FeatureToMs2Indices:
    """
    Cython implementation of _FeatureMapping_FeatureToMs2Indices

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1FeatureMapping_FeatureToMs2Indices.html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void FeatureMapping_FeatureToMs2Indices()
        """
        ...
    
    @overload
    def __init__(self, in_0: FeatureMapping_FeatureToMs2Indices ) -> None:
        """
        Cython signature: void FeatureMapping_FeatureToMs2Indices(FeatureMapping_FeatureToMs2Indices &)
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


class GridBasedCluster:
    """
    Cython implementation of _GridBasedCluster

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1GridBasedCluster.html>`_
    """
    
    @overload
    def __init__(self, centre: Union[Sequence[int], Sequence[float]] , bounding_box: DBoundingBox2 , point_indices: List[int] , property_A: int , properties_B: List[int] ) -> None:
        """
        Cython signature: void GridBasedCluster(DPosition2 centre, DBoundingBox2 bounding_box, libcpp_vector[int] point_indices, int property_A, libcpp_vector[int] properties_B)
        """
        ...
    
    @overload
    def __init__(self, centre: Union[Sequence[int], Sequence[float]] , bounding_box: DBoundingBox2 , point_indices: List[int] ) -> None:
        """
        Cython signature: void GridBasedCluster(DPosition2 centre, DBoundingBox2 bounding_box, libcpp_vector[int] point_indices)
        """
        ...
    
    @overload
    def __init__(self, in_0: GridBasedCluster ) -> None:
        """
        Cython signature: void GridBasedCluster(GridBasedCluster &)
        """
        ...
    
    def getCentre(self) -> Union[Sequence[int], Sequence[float]]:
        """
        Cython signature: DPosition2 getCentre()
        Returns cluster centre
        """
        ...
    
    def getBoundingBox(self) -> DBoundingBox2:
        """
        Cython signature: DBoundingBox2 getBoundingBox()
        Returns bounding box
        """
        ...
    
    def getPoints(self) -> List[int]:
        """
        Cython signature: libcpp_vector[int] getPoints()
        Returns indices of points in cluster
        """
        ...
    
    def getPropertyA(self) -> int:
        """
        Cython signature: int getPropertyA()
        Returns property A
        """
        ...
    
    def getPropertiesB(self) -> List[int]:
        """
        Cython signature: libcpp_vector[int] getPropertiesB()
        Returns properties B of all points
        """
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


class IsobaricQuantities:
    """
    Cython implementation of _IsobaricQuantities

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1IsobaricQuantities.html>`_

    Isobaric quantities from isobaric quantification.
    """
    
    scan: int
    
    rt: float
    
    precursor_mz: float
    
    precursor_mass: float
    
    quantities: List[float]
    
    merged_quantities: List[float]
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void IsobaricQuantities()
        """
        ...
    
    @overload
    def __init__(self, in_0: IsobaricQuantities ) -> None:
        """
        Cython signature: void IsobaricQuantities(IsobaricQuantities &)
        """
        ...
    
    def empty(self) -> bool:
        """
        Cython signature: bool empty()
        Returns true if no quantities stored
        """
        ... 


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


class LogMzPeak:
    """
    Cython implementation of _LogMzPeak

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1LogMzPeak.html>`_

    Log transformed peak from original peak.
    Contains information such as charge, isotope index, and uncharged mass.
    """
    
    mz: float
    
    intensity: float
    
    logMz: float
    
    mass: float
    
    abs_charge: int
    
    is_positive: bool
    
    isotopeIndex: int
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void LogMzPeak()
        """
        ...
    
    @overload
    def __init__(self, in_0: LogMzPeak ) -> None:
        """
        Cython signature: void LogMzPeak(LogMzPeak &)
        """
        ...
    
    @overload
    def __init__(self, peak: Peak1D , positive: bool ) -> None:
        """
        Cython signature: void LogMzPeak(Peak1D & peak, bool positive)
        Constructor from Peak1D
        """
        ...
    
    def getUnchargedMass(self) -> float:
        """
        Cython signature: double getUnchargedMass()
        Get uncharged mass (0 if no charge set)
        """
        ...
    
    def __richcmp__(self, other: LogMzPeak, op: int) -> Any:
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


class MRMFQC_ComponentGroupPairQCs:
    """
    Cython implementation of _MRMFQC_ComponentGroupPairQCs

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1MRMFQC_ComponentGroupPairQCs.html>`_
    """
    
    component_group_name: Union[bytes, str, String]
    
    resolution_pair_name: Union[bytes, str, String]
    
    resolution_l: float
    
    resolution_u: float
    
    rt_diff_l: float
    
    rt_diff_u: float
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void MRMFQC_ComponentGroupPairQCs()
        """
        ...
    
    @overload
    def __init__(self, in_0: MRMFQC_ComponentGroupPairQCs ) -> None:
        """
        Cython signature: void MRMFQC_ComponentGroupPairQCs(MRMFQC_ComponentGroupPairQCs &)
        """
        ... 


class MRMFQC_ComponentGroupQCs:
    """
    Cython implementation of _MRMFQC_ComponentGroupQCs

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1MRMFQC_ComponentGroupQCs.html>`_
    """
    
    component_group_name: Union[bytes, str, String]
    
    retention_time_l: float
    
    retention_time_u: float
    
    intensity_l: float
    
    intensity_u: float
    
    overall_quality_l: float
    
    overall_quality_u: float
    
    n_heavy_l: int
    
    n_heavy_u: int
    
    n_light_l: int
    
    n_light_u: int
    
    n_detecting_l: int
    
    n_detecting_u: int
    
    n_quantifying_l: int
    
    n_quantifying_u: int
    
    n_identifying_l: int
    
    n_identifying_u: int
    
    n_transitions_l: int
    
    n_transitions_u: int
    
    ion_ratio_pair_name_1: Union[bytes, str, String]
    
    ion_ratio_pair_name_2: Union[bytes, str, String]
    
    ion_ratio_l: float
    
    ion_ratio_u: float
    
    ion_ratio_feature_name: Union[bytes, str, String]
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void MRMFQC_ComponentGroupQCs()
        """
        ...
    
    @overload
    def __init__(self, in_0: MRMFQC_ComponentGroupQCs ) -> None:
        """
        Cython signature: void MRMFQC_ComponentGroupQCs(MRMFQC_ComponentGroupQCs &)
        """
        ... 


class MRMFQC_ComponentQCs:
    """
    Cython implementation of _MRMFQC_ComponentQCs

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1MRMFQC_ComponentQCs.html>`_
    """
    
    component_name: Union[bytes, str, String]
    
    retention_time_l: float
    
    retention_time_u: float
    
    intensity_l: float
    
    intensity_u: float
    
    overall_quality_l: float
    
    overall_quality_u: float
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void MRMFQC_ComponentQCs()
        """
        ...
    
    @overload
    def __init__(self, in_0: MRMFQC_ComponentQCs ) -> None:
        """
        Cython signature: void MRMFQC_ComponentQCs(MRMFQC_ComponentQCs &)
        """
        ... 


class MRMFeatureQC:
    """
    Cython implementation of _MRMFeatureQC

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1MRMFeatureQC.html>`_
    """
    
    component_qcs: List[MRMFQC_ComponentQCs]
    
    component_group_qcs: List[MRMFQC_ComponentGroupQCs]
    
    component_group_pair_qcs: List[MRMFQC_ComponentGroupPairQCs]
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void MRMFeatureQC()
        """
        ...
    
    @overload
    def __init__(self, in_0: MRMFeatureQC ) -> None:
        """
        Cython signature: void MRMFeatureQC(MRMFeatureQC &)
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


class MSExperiment:
    """
    Cython implementation of _MSExperiment

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1MSExperiment.html>`_
      -- Inherits from ['ExperimentalSettings']

    In-Memory representation of a mass spectrometry experiment.
    
    Contains the data and metadata of an experiment performed with an MS (or
    HPLC and MS). This representation of an MS experiment is organized as list
    of spectra and chromatograms and provides an in-memory representation of
    popular mass-spectrometric file formats such as mzXML or mzML. The
    meta-data associated with an experiment is contained in
    ExperimentalSettings (by inheritance) while the raw data (as well as
    spectra and chromatogram level meta data) is stored in objects of type
    MSSpectrum and MSChromatogram, which are accessible through the getSpectrum
    and getChromatogram functions.
    
    Spectra can be accessed by direct iteration or by getSpectrum(),
    while chromatograms are accessed through getChromatogram().
    See help(ExperimentalSettings) for information about meta-data.
    
    Usage:
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void MSExperiment()
        """
        ...
    
    @overload
    def __init__(self, in_0: MSExperiment ) -> None:
        """
        Cython signature: void MSExperiment(MSExperiment &)
        """
        ...
    
    def getExperimentalSettings(self) -> ExperimentalSettings:
        """
        Cython signature: ExperimentalSettings getExperimentalSettings()
        """
        ...
    
    def __getitem__(self, in_0: int ) -> MSSpectrum:
        """
        Cython signature: MSSpectrum & operator[](size_t)
        """
        ...
    def __setitem__(self, key: int, value: MSSpectrum) -> None:
        """Cython signature: MSSpectrum & operator[](size_t)"""
        ...
    
    def addSpectrum(self, spec: MSSpectrum ) -> None:
        """
        Cython signature: void addSpectrum(MSSpectrum spec)
        """
        ...
    
    def setSpectra(self, spectra: List[MSSpectrum] ) -> None:
        """
        Cython signature: void setSpectra(libcpp_vector[MSSpectrum] & spectra)
        """
        ...
    
    def getSpectra(self) -> List[MSSpectrum]:
        """
        Cython signature: libcpp_vector[MSSpectrum] getSpectra()
        """
        ...
    
    def aggregateFromMatrix(self, ranges: MatrixDouble , ms_level: int , mz_agg: bytes ) -> List[List[float]]:
        """
        Cython signature: libcpp_vector[libcpp_vector[double]] aggregateFromMatrix(MatrixDouble & ranges, unsigned int ms_level, libcpp_string mz_agg)
        Aggregates intensity values for multiple m/z and RT ranges specified in a matrix
        """
        ...
    
    def extractXICsFromMatrix(self, ranges: MatrixDouble , ms_level: int , mz_agg: bytes ) -> List[MSChromatogram]:
        """
        Cython signature: libcpp_vector[MSChromatogram] extractXICsFromMatrix(MatrixDouble & ranges, unsigned int ms_level, libcpp_string mz_agg)
        Extracts XIC chromatograms for multiple m/z and RT ranges specified in a matrix
        """
        ...
    
    def addChromatogram(self, chromatogram: MSChromatogram ) -> None:
        """
        Cython signature: void addChromatogram(MSChromatogram chromatogram)
        """
        ...
    
    def setChromatograms(self, chromatograms: List[MSChromatogram] ) -> None:
        """
        Cython signature: void setChromatograms(libcpp_vector[MSChromatogram] chromatograms)
        """
        ...
    
    def getChromatograms(self) -> List[MSChromatogram]:
        """
        Cython signature: libcpp_vector[MSChromatogram] getChromatograms()
        """
        ...
    
    def calculateTIC(self) -> MSChromatogram:
        """
        Cython signature: MSChromatogram calculateTIC()
        Returns the total ion chromatogram
        """
        ...
    
    def clear(self, clear_meta_data: bool ) -> None:
        """
        Cython signature: void clear(bool clear_meta_data)
        Clear all spectra data and meta data (if called with True)
        """
        ...
    
    def updateRanges(self) -> None:
        """
        Cython signature: void updateRanges()
        Recalculate global ranges for both spectra and chromatrograms after changes to the data has been made.
        """
        ...
    
    def reserveSpaceSpectra(self, s: int ) -> None:
        """
        Cython signature: void reserveSpaceSpectra(size_t s)
        """
        ...
    
    def reserveSpaceChromatograms(self, s: int ) -> None:
        """
        Cython signature: void reserveSpaceChromatograms(size_t s)
        """
        ...
    
    def getSize(self) -> int:
        """
        Cython signature: uint64_t getSize()
        Returns the total number of peaks
        """
        ...
    
    def size(self) -> int:
        """
        Cython signature: int size()
        """
        ...
    
    def resize(self, s: int ) -> None:
        """
        Cython signature: void resize(size_t s)
        """
        ...
    
    def empty(self) -> bool:
        """
        Cython signature: bool empty()
        """
        ...
    
    def reserve(self, s: int ) -> None:
        """
        Cython signature: void reserve(size_t s)
        """
        ...
    
    def getNrSpectra(self) -> int:
        """
        Cython signature: size_t getNrSpectra()
        Returns the number of MS spectra
        """
        ...
    
    def getNrChromatograms(self) -> int:
        """
        Cython signature: size_t getNrChromatograms()
        Returns the number of chromatograms
        """
        ...
    
    @overload
    def sortSpectra(self, sort_mz: bool ) -> None:
        """
        Cython signature: void sortSpectra(bool sort_mz)
        Sorts spectra by RT. If sort_mz=True also sort each peak in a spectrum by m/z
        """
        ...
    
    @overload
    def sortSpectra(self, ) -> None:
        """
        Cython signature: void sortSpectra()
        """
        ...
    
    @overload
    def sortChromatograms(self, sort_rt: bool ) -> None:
        """
        Cython signature: void sortChromatograms(bool sort_rt)
        Sorts chromatograms by m/z. If sort_rt=True also sort each chromatogram RT
        """
        ...
    
    @overload
    def sortChromatograms(self, ) -> None:
        """
        Cython signature: void sortChromatograms()
        """
        ...
    
    @overload
    def isSorted(self, check_mz: bool ) -> bool:
        """
        Cython signature: bool isSorted(bool check_mz)
        Checks if all spectra are sorted with respect to ascending RT
        """
        ...
    
    @overload
    def isSorted(self, ) -> bool:
        """
        Cython signature: bool isSorted()
        """
        ...
    
    def getPrimaryMSRunPath(self, toFill: List[bytes] ) -> None:
        """
        Cython signature: void getPrimaryMSRunPath(StringList & toFill)
        References to the first MS file(s) after conversions. Used to trace results back to original data.
        """
        ...
    
    def swap(self, in_0: MSExperiment ) -> None:
        """
        Cython signature: void swap(MSExperiment)
        """
        ...
    
    def reset(self) -> None:
        """
        Cython signature: void reset()
        """
        ...
    
    def clearMetaDataArrays(self) -> bool:
        """
        Cython signature: bool clearMetaDataArrays()
        """
        ...
    
    def getPrecursorSpectrum(self, zero_based_index: int ) -> int:
        """
        Cython signature: int getPrecursorSpectrum(int zero_based_index)
        Returns the index of the precursor spectrum for spectrum at index @p zero_based_index
        """
        ...
    
    def spectrumRanges(self) -> SpectrumRangeManager:
        """
        Cython signature: SpectrumRangeManager spectrumRanges()
        Returns a reference to the spectrum range manager
        """
        ...
    
    def chromatogramRanges(self) -> ChromatogramRangeManager:
        """
        Cython signature: ChromatogramRangeManager chromatogramRanges()
        Returns a reference to the chromatogram range manager
        """
        ...
    
    def getMinRT(self) -> float:
        """
        Cython signature: double getMinRT()
        Get the minimum RT value from the combined ranges
        """
        ...
    
    def getMaxRT(self) -> float:
        """
        Cython signature: double getMaxRT()
        Get the maximum RT value from the combined ranges
        """
        ...
    
    def getMinMZ(self) -> float:
        """
        Cython signature: double getMinMZ()
        Get the minimum m/z value from the combined ranges
        """
        ...
    
    def getMaxMZ(self) -> float:
        """
        Cython signature: double getMaxMZ()
        Get the maximum m/z value from the combined ranges
        """
        ...
    
    def getMinIntensity(self) -> float:
        """
        Cython signature: double getMinIntensity()
        Get the minimum intensity value from the combined ranges
        """
        ...
    
    def getMaxIntensity(self) -> float:
        """
        Cython signature: double getMaxIntensity()
        Get the maximum intensity value from the combined ranges
        """
        ...
    
    def getMinMobility(self) -> float:
        """
        Cython signature: double getMinMobility()
        Get the minimum mobility value from the combined ranges
        """
        ...
    
    def getMaxMobility(self) -> float:
        """
        Cython signature: double getMaxMobility()
        Get the maximum mobility value from the combined ranges
        """
        ...
    
    def clearRanges(self) -> None:
        """
        Cython signature: void clearRanges()
        Clear all ranges in all range managers
        """
        ...
    
    def getSourceFiles(self) -> List[SourceFile]:
        """
        Cython signature: libcpp_vector[SourceFile] getSourceFiles()
        Returns a reference to the source data file
        """
        ...
    
    def setSourceFiles(self, source_files: List[SourceFile] ) -> None:
        """
        Cython signature: void setSourceFiles(libcpp_vector[SourceFile] source_files)
        Sets the source data file
        """
        ...
    
    def getDateTime(self) -> DateTime:
        """
        Cython signature: DateTime getDateTime()
        Returns the date the experiment was performed
        """
        ...
    
    def setDateTime(self, date_time: DateTime ) -> None:
        """
        Cython signature: void setDateTime(DateTime date_time)
        Sets the date the experiment was performed
        """
        ...
    
    def getSample(self) -> Sample:
        """
        Cython signature: Sample getSample()
        Returns a reference to the sample description
        """
        ...
    
    def setSample(self, sample: Sample ) -> None:
        """
        Cython signature: void setSample(Sample sample)
        Sets the sample description
        """
        ...
    
    def getContacts(self) -> List[ContactPerson]:
        """
        Cython signature: libcpp_vector[ContactPerson] getContacts()
        Returns a reference to the list of contact persons
        """
        ...
    
    def setContacts(self, contacts: List[ContactPerson] ) -> None:
        """
        Cython signature: void setContacts(libcpp_vector[ContactPerson] contacts)
        Sets the list of contact persons
        """
        ...
    
    def getInstrument(self) -> Instrument:
        """
        Cython signature: Instrument getInstrument()
        Returns a reference to the MS instrument description
        """
        ...
    
    def setInstrument(self, instrument: Instrument ) -> None:
        """
        Cython signature: void setInstrument(Instrument instrument)
        Sets the MS instrument description
        """
        ...
    
    def getHPLC(self) -> HPLC:
        """
        Cython signature: HPLC getHPLC()
        Returns a reference to the description of the HPLC run
        """
        ...
    
    def setHPLC(self, hplc: HPLC ) -> None:
        """
        Cython signature: void setHPLC(HPLC hplc)
        Sets the description of the HPLC run
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
    
    def getFractionIdentifier(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getFractionIdentifier()
        Returns fraction identifier
        """
        ...
    
    def setFractionIdentifier(self, fraction_identifier: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setFractionIdentifier(String fraction_identifier)
        Sets the fraction identifier
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
    
    def __richcmp__(self, other: MSExperiment, op: int) -> Any:
        ...
    
    def __iter__(self) -> MSSpectrum:
       ... 


class MSPGenericFile:
    """
    Cython implementation of _MSPGenericFile

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1MSPGenericFile.html>`_
      -- Inherits from ['DefaultParamHandler']
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void MSPGenericFile()
        """
        ...
    
    @overload
    def __init__(self, in_0: MSPGenericFile ) -> None:
        """
        Cython signature: void MSPGenericFile(MSPGenericFile &)
        """
        ...
    
    @overload
    def __init__(self, filename: Union[bytes, str, String] , library: MSExperiment ) -> None:
        """
        Cython signature: void MSPGenericFile(const String & filename, MSExperiment & library)
        """
        ...
    
    def load(self, filename: Union[bytes, str, String] , library: MSExperiment ) -> None:
        """
        Cython signature: void load(const String & filename, MSExperiment & library)
        Load the file's data and metadata, and save it into an `MSExperiment`
        
        
        :param filename: Path to the MSP input file
        :param library: The variable into which the extracted information will be saved
        :raises:
          Exception: FileNotFound If the file could not be found
        """
        ...
    
    def store(self, filename: Union[bytes, str, String] , library: MSExperiment ) -> None:
        """
        Cython signature: void store(const String & filename, const MSExperiment & library)
        Save data and metadata into a file
        
        
        :param filename: Path to the MSP input file
        :param library: The variable from which extracted information will be saved
        :raises:
          Exception: FileNotWritable If the file is not writable
        """
        ...
    
    def getDefaultParameters(self, params: Param ) -> None:
        """
        Cython signature: void getDefaultParameters(Param & params)
        Returns the class' default parameters
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


class MassFeature_FDHS:
    """
    Cython implementation of _MassFeature_FDHS

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1MassFeature_FDHS.html>`_

    Mass feature (Deconvolved masses in spectra are traced to generate mass features).
    Similar to LC-MS features but for deconvolved masses.
    """
    
    index: int
    
    mt: Kernel_MassTrace
    
    per_charge_intensity: List[float]
    
    per_isotope_intensity: List[float]
    
    iso_offset: int
    
    scan_number: int
    
    min_scan_number: int
    
    max_scan_number: int
    
    rep_charge: int
    
    avg_mass: float
    
    min_charge: int
    
    max_charge: int
    
    charge_count: int
    
    isotope_score: float
    
    qscore: float
    
    rep_mz: float
    
    is_decoy: bool
    
    ms_level: int
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void MassFeature_FDHS()
        """
        ...
    
    @overload
    def __init__(self, in_0: MassFeature_FDHS ) -> None:
        """
        Cython signature: void MassFeature_FDHS(MassFeature_FDHS &)
        """
        ...
    
    def __richcmp__(self, other: MassFeature_FDHS, op: int) -> Any:
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


class MzDataFile:
    """
    Cython implementation of _MzDataFile

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1MzDataFile.html>`_
      -- Inherits from ['ProgressLogger']
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void MzDataFile()
        File adapter for MzData files
        """
        ...
    
    @overload
    def __init__(self, in_0: MzDataFile ) -> None:
        """
        Cython signature: void MzDataFile(MzDataFile &)
        """
        ...
    
    def load(self, filename: Union[bytes, str, String] , map: MSExperiment ) -> None:
        """
        Cython signature: void load(const String & filename, MSExperiment & map)
        Loads a map from a MzData file
        
        
        :param filename: Directory of the file with the file name
        :param map: It has to be a MSExperiment or have the same interface
        :raises:
          Exception: FileNotFound is thrown if the file could not be opened
        :raises:
          Exception: ParseError is thrown if an error occurs during parsing
        """
        ...
    
    def store(self, filename: Union[bytes, str, String] , map: MSExperiment ) -> None:
        """
        Cython signature: void store(const String & filename, MSExperiment & map)
        Stores a map in a MzData file
        
        
        :param filename: Directory of the file with the file name
        :param map: It has to be a MSExperiment or have the same interface
        :raises:
          Exception: UnableToCreateFile is thrown if the file could not be created
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
    
    def isSemanticallyValid(self, filename: Union[bytes, str, String] , errors: List[bytes] , warnings: List[bytes] ) -> bool:
        """
        Cython signature: bool isSemanticallyValid(const String & filename, StringList & errors, StringList & warnings)
        Checks if a file is valid with respect to the mapping file and the controlled vocabulary
        
        
        :param filename: File name of the file to be checked
        :param errors: Errors during the validation are returned in this output parameter
        :param warnings: Warnings during the validation are returned in this output parameter
        :raises:
          Exception: FileNotFound is thrown if the file could not be opened
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


class MzIdentMLFile:
    """
    Cython implementation of _MzIdentMLFile

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1MzIdentMLFile.html>`_
      -- Inherits from ['ProgressLogger']
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void MzIdentMLFile()
        """
        ...
    
    @overload
    def __init__(self, in_0: MzIdentMLFile ) -> None:
        """
        Cython signature: void MzIdentMLFile(MzIdentMLFile &)
        """
        ...
    
    def load(self, filename: Union[bytes, str, String] , poid: List[ProteinIdentification] , peid: PeptideIdentificationList ) -> None:
        """
        Cython signature: void load(String filename, libcpp_vector[ProteinIdentification] & poid, PeptideIdentificationList & peid)
        Loads the identifications from a MzIdentML file
        
        
        :param filename: File name of the file to be checked
        :raises:
          Exception: FileNotFound is thrown if the file could not be opened
        :raises:
          Exception: ParseError is thrown if an error occurs during parsin
        """
        ...
    
    def store(self, filename: Union[bytes, str, String] , poid: List[ProteinIdentification] , peid: PeptideIdentificationList ) -> None:
        """
        Cython signature: void store(String filename, libcpp_vector[ProteinIdentification] & poid, PeptideIdentificationList & peid)
        Stores the identifications in a MzIdentML file
        
        
        :raises:
          Exception: UnableToCreateFile is thrown if the file could not be created
        """
        ...
    
    def isSemanticallyValid(self, filename: Union[bytes, str, String] , errors: List[bytes] , warnings: List[bytes] ) -> bool:
        """
        Cython signature: bool isSemanticallyValid(String filename, StringList errors, StringList warnings)
        Checks if a file is valid with respect to the mapping file and the controlled vocabulary
        
        
        :param filename: File name of the file to be checked
        :param errors: Errors during the validation are returned in this output parameter
        :param warnings: Warnings during the validation are returned in this output parameter
        :raises:
          Exception: FileNotFound is thrown if the file could not be opened
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


class Param:
    """
    Cython implementation of _Param

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1Param.html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void Param()
        """
        ...
    
    @overload
    def __init__(self, in_0: Param ) -> None:
        """
        Cython signature: void Param(Param &)
        """
        ...
    
    @overload
    def setValue(self, key: Union[bytes, str] , val: Union[int, float, bytes, str, List[int], List[float], List[bytes]] , desc: Union[bytes, str] , tags: List[Union[bytes, str]] ) -> None:
        """
        Cython signature: void setValue(libcpp_utf8_string key, ParamValue val, libcpp_utf8_string desc, libcpp_vector[libcpp_utf8_string] tags)
        """
        ...
    
    @overload
    def setValue(self, key: Union[bytes, str] , val: Union[int, float, bytes, str, List[int], List[float], List[bytes]] , desc: Union[bytes, str] ) -> None:
        """
        Cython signature: void setValue(libcpp_utf8_string key, ParamValue val, libcpp_utf8_string desc)
        """
        ...
    
    @overload
    def setValue(self, key: Union[bytes, str] , val: Union[int, float, bytes, str, List[int], List[float], List[bytes]] ) -> None:
        """
        Cython signature: void setValue(libcpp_utf8_string key, ParamValue val)
        """
        ...
    
    def getValue(self, key: Union[bytes, str] ) -> Union[int, float, bytes, str, List[int], List[float], List[bytes]]:
        """
        Cython signature: ParamValue getValue(libcpp_utf8_string key)
        """
        ...
    
    def getValueType(self, key: Union[bytes, str] ) -> int:
        """
        Cython signature: ValueType getValueType(libcpp_utf8_string key)
        """
        ...
    
    def getEntry(self, in_0: Union[bytes, str] ) -> ParamEntry:
        """
        Cython signature: ParamEntry getEntry(libcpp_utf8_string)
        """
        ...
    
    def exists(self, key: Union[bytes, str] ) -> bool:
        """
        Cython signature: bool exists(libcpp_utf8_string key)
        """
        ...
    
    def addTag(self, key: Union[bytes, str] , tag: Union[bytes, str] ) -> None:
        """
        Cython signature: void addTag(libcpp_utf8_string key, libcpp_utf8_string tag)
        """
        ...
    
    def addTags(self, key: Union[bytes, str] , tags: List[Union[bytes, str]] ) -> None:
        """
        Cython signature: void addTags(libcpp_utf8_string key, libcpp_vector[libcpp_utf8_string] tags)
        """
        ...
    
    def hasTag(self, key: Union[bytes, str] , tag: Union[bytes, str] ) -> int:
        """
        Cython signature: int hasTag(libcpp_utf8_string key, libcpp_utf8_string tag)
        """
        ...
    
    def getTags(self, key: Union[bytes, str] ) -> List[bytes]:
        """
        Cython signature: libcpp_vector[libcpp_string] getTags(libcpp_utf8_string key)
        """
        ...
    
    def clearTags(self, key: Union[bytes, str] ) -> None:
        """
        Cython signature: void clearTags(libcpp_utf8_string key)
        """
        ...
    
    def getDescription(self, key: Union[bytes, str] ) -> str:
        """
        Cython signature: libcpp_utf8_output_string getDescription(libcpp_utf8_string key)
        """
        ...
    
    def setSectionDescription(self, key: Union[bytes, str] , desc: Union[bytes, str] ) -> None:
        """
        Cython signature: void setSectionDescription(libcpp_utf8_string key, libcpp_utf8_string desc)
        """
        ...
    
    def getSectionDescription(self, key: Union[bytes, str] ) -> str:
        """
        Cython signature: libcpp_utf8_output_string getSectionDescription(libcpp_utf8_string key)
        """
        ...
    
    def addSection(self, key: Union[bytes, str] , desc: Union[bytes, str] ) -> None:
        """
        Cython signature: void addSection(libcpp_utf8_string key, libcpp_utf8_string desc)
        """
        ...
    
    def size(self) -> int:
        """
        Cython signature: size_t size()
        """
        ...
    
    def empty(self) -> bool:
        """
        Cython signature: bool empty()
        """
        ...
    
    def clear(self) -> None:
        """
        Cython signature: void clear()
        """
        ...
    
    def insert(self, prefix: Union[bytes, str] , param: Param ) -> None:
        """
        Cython signature: void insert(libcpp_utf8_string prefix, Param param)
        """
        ...
    
    def remove(self, key: Union[bytes, str] ) -> None:
        """
        Cython signature: void remove(libcpp_utf8_string key)
        """
        ...
    
    def removeAll(self, prefix: Union[bytes, str] ) -> None:
        """
        Cython signature: void removeAll(libcpp_utf8_string prefix)
        """
        ...
    
    @overload
    def copy(self, prefix: Union[bytes, str] , in_1: bool ) -> Param:
        """
        Cython signature: Param copy(libcpp_utf8_string prefix, bool)
        """
        ...
    
    @overload
    def copy(self, prefix: Union[bytes, str] ) -> Param:
        """
        Cython signature: Param copy(libcpp_utf8_string prefix)
        """
        ...
    
    def merge(self, toMerge: Param ) -> None:
        """
        Cython signature: void merge(Param toMerge)
        """
        ...
    
    @overload
    def setDefaults(self, defaults: Param , prefix: Union[bytes, str] , showMessage: bool ) -> None:
        """
        Cython signature: void setDefaults(Param defaults, libcpp_utf8_string prefix, bool showMessage)
        """
        ...
    
    @overload
    def setDefaults(self, defaults: Param , prefix: Union[bytes, str] ) -> None:
        """
        Cython signature: void setDefaults(Param defaults, libcpp_utf8_string prefix)
        """
        ...
    
    @overload
    def setDefaults(self, defaults: Param ) -> None:
        """
        Cython signature: void setDefaults(Param defaults)
        """
        ...
    
    @overload
    def checkDefaults(self, name: Union[bytes, str] , defaults: Param , prefix: Union[bytes, str] ) -> None:
        """
        Cython signature: void checkDefaults(libcpp_utf8_string name, Param defaults, libcpp_utf8_string prefix)
        """
        ...
    
    @overload
    def checkDefaults(self, name: Union[bytes, str] , defaults: Param ) -> None:
        """
        Cython signature: void checkDefaults(libcpp_utf8_string name, Param defaults)
        """
        ...
    
    def getValidStrings(self, key: Union[bytes, str] ) -> List[Union[bytes, str]]:
        """
        Cython signature: libcpp_vector[libcpp_utf8_string] getValidStrings(libcpp_utf8_string key)
        """
        ...
    
    def setValidStrings(self, key: Union[bytes, str] , strings: List[Union[bytes, str]] ) -> None:
        """
        Cython signature: void setValidStrings(libcpp_utf8_string key, libcpp_vector[libcpp_utf8_string] strings)
        """
        ...
    
    def setMinInt(self, key: Union[bytes, str] , min: int ) -> None:
        """
        Cython signature: void setMinInt(libcpp_utf8_string key, int min)
        """
        ...
    
    def setMaxInt(self, key: Union[bytes, str] , max: int ) -> None:
        """
        Cython signature: void setMaxInt(libcpp_utf8_string key, int max)
        """
        ...
    
    def setMinFloat(self, key: Union[bytes, str] , min: float ) -> None:
        """
        Cython signature: void setMinFloat(libcpp_utf8_string key, double min)
        """
        ...
    
    def setMaxFloat(self, key: Union[bytes, str] , max: float ) -> None:
        """
        Cython signature: void setMaxFloat(libcpp_utf8_string key, double max)
        """
        ...
    
    def __richcmp__(self, other: Param, op: int) -> Any:
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


class PepXMLFileMascot:
    """
    Cython implementation of _PepXMLFileMascot

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1PepXMLFileMascot.html>`_

    Used to load Mascot PepXML files
    
    A schema for this format can be found at http://www.matrixscience.com/xmlns/schema/pepXML_v18/pepXML_v18.xsd
    """
    
    def __init__(self) -> None:
        """
        Cython signature: void PepXMLFileMascot()
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


class PrecalAveragine:
    """
    Cython implementation of _PrecalAveragine

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1PrecalAveragine.html>`_

    Averagine patterns pre-calculated for speed up.
    Used for fast isotope cosine calculation.
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void PrecalAveragine()
        """
        ...
    
    @overload
    def __init__(self, min_mass: float , max_mass: float , delta: float , generator: CoarseIsotopePatternGenerator , use_RNA_averagine: bool ) -> None:
        """
        Cython signature: void PrecalAveragine(double min_mass, double max_mass, double delta, CoarseIsotopePatternGenerator & generator, bool use_RNA_averagine)
        """
        ...
    
    @overload
    def __init__(self, min_mass: float , max_mass: float , delta: float , generator: CoarseIsotopePatternGenerator , use_RNA_averagine: bool , decoy_iso_distance: float ) -> None:
        """
        Cython signature: void PrecalAveragine(double min_mass, double max_mass, double delta, CoarseIsotopePatternGenerator & generator, bool use_RNA_averagine, double decoy_iso_distance)
        """
        ...
    
    @overload
    def __init__(self, in_0: PrecalAveragine ) -> None:
        """
        Cython signature: void PrecalAveragine(PrecalAveragine &)
        """
        ...
    
    def get(self, mass: float ) -> IsotopeDistribution:
        """
        Cython signature: IsotopeDistribution get(double mass)
        Get isotope distribution for given mass
        """
        ...
    
    def getMaxIsotopeIndex(self) -> int:
        """
        Cython signature: size_t getMaxIsotopeIndex()
        Get max isotope index
        """
        ...
    
    def setMaxIsotopeIndex(self, index: int ) -> None:
        """
        Cython signature: void setMaxIsotopeIndex(int index)
        Set max isotope index
        """
        ...
    
    def getLeftCountFromApex(self, mass: float ) -> int:
        """
        Cython signature: size_t getLeftCountFromApex(double mass)
        Get isotope count left of apex
        """
        ...
    
    def getRightCountFromApex(self, mass: float ) -> int:
        """
        Cython signature: size_t getRightCountFromApex(double mass)
        Get isotope count right of apex
        """
        ...
    
    def getApexIndex(self, mass: float ) -> int:
        """
        Cython signature: size_t getApexIndex(double mass)
        Get apex isotope index
        """
        ...
    
    def getLastIndex(self, mass: float ) -> int:
        """
        Cython signature: size_t getLastIndex(double mass)
        Get last isotope index
        """
        ...
    
    def getAverageMassDelta(self, mass: float ) -> float:
        """
        Cython signature: double getAverageMassDelta(double mass)
        Get mass diff between avg and mono
        """
        ...
    
    def getMostAbundantMassDelta(self, mass: float ) -> float:
        """
        Cython signature: double getMostAbundantMassDelta(double mass)
        Get mass diff between most abundant and mono
        """
        ...
    
    def getSNRMultiplicationFactor(self, mass: float ) -> float:
        """
        Cython signature: double getSNRMultiplicationFactor(double mass)
        Get SNR multiplication factor
        """
        ... 


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


class RealMassDecomposer:
    """
    Cython implementation of _RealMassDecomposer

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS::ims_1_1RealMassDecomposer.html>`_
    """
    
    @overload
    def __init__(self, in_0: RealMassDecomposer ) -> None:
        """
        Cython signature: void RealMassDecomposer(RealMassDecomposer)
        """
        ...
    
    @overload
    def __init__(self, weights: IMSWeights ) -> None:
        """
        Cython signature: void RealMassDecomposer(IMSWeights & weights)
        """
        ...
    
    def getNumberOfDecompositions(self, mass: float , error: float ) -> int:
        """
        Cython signature: uint64_t getNumberOfDecompositions(double mass, double error)
        Gets a number of all decompositions for amass with an error
        allowed. It's similar to thegetDecompositions(double,double) function
        but less space consuming, since doesn't use container to store decompositions
        
        
        :param mass: Mass to be decomposed
        :param error: Error allowed between given and result decomposition
        :return: Number of all decompositions for a given mass and error
        """
        ... 


class Ribonucleotide:
    """
    Cython implementation of _Ribonucleotide

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS::Ribonucleotide_1_1Ribonucleotide.html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void Ribonucleotide()
        """
        ...
    
    @overload
    def __init__(self, in_0: Ribonucleotide ) -> None:
        """
        Cython signature: void Ribonucleotide(Ribonucleotide &)
        """
        ...
    
    @overload
    def __init__(self, name: Union[bytes, str, String] , code: Union[bytes, str, String] , new_code: Union[bytes, str, String] , html_code: Union[bytes, str, String] , formula: EmpiricalFormula , origin: bytes , mono_mass: float , avg_mass: float , term_spec: int , baseloss_formula: EmpiricalFormula ) -> None:
        """
        Cython signature: void Ribonucleotide(String name, String code, String new_code, String html_code, EmpiricalFormula formula, char origin, double mono_mass, double avg_mass, TermSpecificityNuc term_spec, EmpiricalFormula baseloss_formula)
        """
        ...
    
    def getCode(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getCode()
        Returns the short name
        """
        ...
    
    def setCode(self, code: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setCode(String code)
        Sets the short name
        """
        ...
    
    def setName(self, name: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setName(String name)
        Sets the name of the ribonucleotide
        """
        ...
    
    def getName(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getName()
        Returns the name of the ribonucleotide
        """
        ...
    
    def setFormula(self, formula: EmpiricalFormula ) -> None:
        """
        Cython signature: void setFormula(EmpiricalFormula formula)
        Sets empirical formula of the ribonucleotide (must be full, with N and C-terminus)
        """
        ...
    
    def getFormula(self) -> EmpiricalFormula:
        """
        Cython signature: EmpiricalFormula getFormula()
        Returns the empirical formula of the residue
        """
        ...
    
    def setAvgMass(self, avg_mass: float ) -> None:
        """
        Cython signature: void setAvgMass(double avg_mass)
        Sets average mass of the ribonucleotide
        """
        ...
    
    def getAvgMass(self) -> float:
        """
        Cython signature: double getAvgMass()
        Returns average mass of the ribonucleotide
        """
        ...
    
    def setMonoMass(self, mono_mass: float ) -> None:
        """
        Cython signature: void setMonoMass(double mono_mass)
        Sets monoisotopic mass of the ribonucleotide
        """
        ...
    
    def getMonoMass(self) -> float:
        """
        Cython signature: double getMonoMass()
        Returns monoisotopic mass of the ribonucleotide
        """
        ...
    
    def getNewCode(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getNewCode()
        Returns the new code
        """
        ...
    
    def setNewCode(self, code: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setNewCode(String code)
        Sets the new code
        """
        ...
    
    def getOrigin(self) -> bytes:
        """
        Cython signature: char getOrigin()
        Returns the code of the unmodified base (e.g., "A", "C", ...)
        """
        ...
    
    def setOrigin(self, origin: bytes ) -> None:
        """
        Cython signature: void setOrigin(char origin)
        Sets the code of the unmodified base (e.g., "A", "C", ...)
        """
        ...
    
    def setHTMLCode(self, html_code: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setHTMLCode(String html_code)
        Sets the HTML (RNAMods) code
        """
        ...
    
    def getHTMLCode(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getHTMLCode()
        Returns the HTML (RNAMods) code
        """
        ...
    
    def setTermSpecificity(self, term_spec: int ) -> None:
        """
        Cython signature: void setTermSpecificity(TermSpecificityNuc term_spec)
        Sets the terminal specificity
        """
        ...
    
    def getTermSpecificity(self) -> int:
        """
        Cython signature: TermSpecificityNuc getTermSpecificity()
        Returns the terminal specificity
        """
        ...
    
    def getBaselossFormula(self) -> EmpiricalFormula:
        """
        Cython signature: EmpiricalFormula getBaselossFormula()
        Returns sum formula after loss of the nucleobase
        """
        ...
    
    def setBaselossFormula(self, formula: EmpiricalFormula ) -> None:
        """
        Cython signature: void setBaselossFormula(EmpiricalFormula formula)
        Sets sum formula after loss of the nucleobase
        """
        ...
    
    def isModified(self) -> bool:
        """
        Cython signature: bool isModified()
        True if the ribonucleotide is a modified one
        """
        ...
    
    def __richcmp__(self, other: Ribonucleotide, op: int) -> Any:
        ...
    TermSpecificityNuc : __TermSpecificityNuc 


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


class SiriusMSFile:
    """
    Cython implementation of _SiriusMSFile

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1SiriusMSFile.html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void SiriusMSFile()
        """
        ...
    
    @overload
    def __init__(self, in_0: SiriusMSFile ) -> None:
        """
        Cython signature: void SiriusMSFile(SiriusMSFile &)
        """
        ... 


class SiriusMSFile_AccessionInfo:
    """
    Cython implementation of _SiriusMSFile_AccessionInfo

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1SiriusMSFile_AccessionInfo.html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void SiriusMSFile_AccessionInfo()
        """
        ...
    
    @overload
    def __init__(self, in_0: SiriusMSFile_AccessionInfo ) -> None:
        """
        Cython signature: void SiriusMSFile_AccessionInfo(SiriusMSFile_AccessionInfo &)
        """
        ... 


class SiriusMSFile_CompoundInfo:
    """
    Cython implementation of _SiriusMSFile_CompoundInfo

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1SiriusMSFile_CompoundInfo.html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void SiriusMSFile_CompoundInfo()
        """
        ...
    
    @overload
    def __init__(self, in_0: SiriusMSFile_CompoundInfo ) -> None:
        """
        Cython signature: void SiriusMSFile_CompoundInfo(SiriusMSFile_CompoundInfo &)
        """
        ... 


class SpectraMerger:
    """
    Cython implementation of _SpectraMerger

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1SpectraMerger.html>`_
      -- Inherits from ['DefaultParamHandler']
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void SpectraMerger()
        Merges blocks of MS or MS2 spectra
        """
        ...
    
    @overload
    def __init__(self, in_0: SpectraMerger ) -> None:
        """
        Cython signature: void SpectraMerger(SpectraMerger &)
        """
        ...
    
    def mergeSpectraBlockWise(self, exp: MSExperiment ) -> None:
        """
        Cython signature: void mergeSpectraBlockWise(MSExperiment & exp)
        """
        ...
    
    def mergeSpectraPrecursors(self, exp: MSExperiment ) -> None:
        """
        Cython signature: void mergeSpectraPrecursors(MSExperiment & exp)
        Merges spectra with similar precursors (must have MS2 level)
        """
        ...
    
    def average(self, exp: MSExperiment , average_type: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void average(MSExperiment & exp, String average_type)
        Average over neighbouring spectra
        
        :param exp: Experimental data to be averaged
        :param average_type: Averaging type to be used ("gaussian" or "tophat")
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


class SpectraSTSimilarityScore:
    """
    Cython implementation of _SpectraSTSimilarityScore

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1SpectraSTSimilarityScore.html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void SpectraSTSimilarityScore()
        """
        ...
    
    @overload
    def __init__(self, in_0: SpectraSTSimilarityScore ) -> None:
        """
        Cython signature: void SpectraSTSimilarityScore(SpectraSTSimilarityScore &)
        """
        ...
    
    def preprocess(self, spec: MSSpectrum , remove_peak_intensity_threshold: float , cut_peaks_below: int , min_peak_number: int , max_peak_number: int ) -> bool:
        """
        Cython signature: bool preprocess(MSSpectrum & spec, float remove_peak_intensity_threshold, unsigned int cut_peaks_below, size_t min_peak_number, size_t max_peak_number)
        Preprocesses the spectrum
        
        The preprocessing removes peak below a intensity threshold, reject spectra that does
        not have enough peaks, and cuts peaks exceeding the max_peak_number most intense peaks
        
        :returns: true if spectrum passes filtering
        """
        ...
    
    def transform(self, spec: MSSpectrum ) -> BinnedSpectrum:
        """
        Cython signature: BinnedSpectrum transform(MSSpectrum & spec)
        Spectrum is transformed into a binned spectrum with bin size 1 and spread 1 and the intensities are normalized
        """
        ...
    
    def dot_bias(self, bin1: BinnedSpectrum , bin2: BinnedSpectrum , dot_product: float ) -> float:
        """
        Cython signature: double dot_bias(BinnedSpectrum & bin1, BinnedSpectrum & bin2, double dot_product)
        Calculates how much of the dot product is dominated by a few peaks
        
        :param dot_product: If -1 this value will be calculated as well.
        :param bin1: First spectrum in binned representation
        :param bin2: Second spectrum in binned representation
        """
        ...
    
    def delta_D(self, top_hit: float , runner_up: float ) -> float:
        """
        Cython signature: double delta_D(double top_hit, double runner_up)
        Calculates the normalized distance between top_hit and runner_up
        
        :param top_hit: Is the best score for a given match
        :param runner_up: A match with a worse score than top_hit, e.g. the second best score
        :returns: normalized distance
        """
        ...
    
    def compute_F(self, dot_product: float , delta_D: float , dot_bias: float ) -> float:
        """
        Cython signature: double compute_F(double dot_product, double delta_D, double dot_bias)
        Computes the overall all score
        
        :param dot_product: dot_product of a match
        :param delta_D: delta_D should be calculated after all dot products for a unidentified spectrum are computed
        :param dot_bias: the bias
        :returns: The SpectraST similarity score
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


class TraceInfo:
    """
    Cython implementation of _TraceInfo

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1TraceInfo.html>`_
    """
    
    name: bytes
    
    description: bytes
    
    opened: bool
    
    @overload
    def __init__(self, n: Union[bytes, str] , d: Union[bytes, str] , o: bool ) -> None:
        """
        Cython signature: void TraceInfo(libcpp_utf8_string n, libcpp_utf8_string d, bool o)
        """
        ...
    
    @overload
    def __init__(self, in_0: TraceInfo ) -> None:
        """
        Cython signature: void TraceInfo(TraceInfo)
        """
        ... 


class UnimodXMLFile:
    """
    Cython implementation of _UnimodXMLFile

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1UnimodXMLFile.html>`_
      -- Inherits from ['XMLFile']
    """
    
    def __init__(self) -> None:
        """
        Cython signature: void UnimodXMLFile()
        """
        ...
    
    def getVersion(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getVersion()
        Return the version of the schema
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


class streampos:
    """
    Cython implementation of _streampos

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classstd_1_1streampos.html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void streampos()
        """
        ...
    
    @overload
    def __init__(self, in_0: streampos ) -> None:
        """
        Cython signature: void streampos(streampos &)
        """
        ... 


class __AggregationMethod:
    """
          Aggregation method
    """
    PROD : int
    SUM : int
    BEST : int

    def getMapping(self) -> Dict[int, str]:
       ... 


class DRangeIntersection:
    None
    Disjoint : int
    Intersects : int
    Inside : int

    def getMapping(self) -> Dict[int, str]:
       ... 


class __DerivatizationAgent:
    None
    NOT_SELECTED : int
    TBDMS : int
    SIZE_OF_DERIVATIZATIONAGENT : int

    def getMapping(self) -> Dict[int, str]:
       ...
    DerivatizationAgent : __DerivatizationAgent 


class __ErrorUnit:
    None
    DALTONS : int
    PPM : int

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


class __MassIntensityType:
    None
    NORM_MAX : int
    NORM_SUM : int
    SIZE_OF_MASSINTENSITYTYPE : int

    def getMapping(self) -> Dict[int, str]:
       ...
    MassIntensityType : __MassIntensityType 


class __MassType:
    None
    MONOISOTOPIC : int
    AVERAGE : int

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


class __PercolatorOutfile_ScoreType:
    None
    QVALUE : int
    POSTERRPROB : int
    SCORE : int
    SIZE_OF_SCORETYPE : int

    def getMapping(self) -> Dict[int, str]:
       ... 


class __RETURN_STATUS:
    None
    SOLVED : int
    ITERATION_EXCEEDED : int

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


class __TermSpecificityNuc:
    None
    ANYWHERE : int
    FIVE_PRIME : int
    THREE_PRIME : int
    NUMBER_OF_TERM_SPECIFICITY : int

    def getMapping(self) -> Dict[int, str]:
       ... 

