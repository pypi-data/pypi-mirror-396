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

def __static_FeatureMapping_assignMS2IndexToFeature(spectra: MSExperiment , fm_info: FeatureMapping_FeatureMappingInfo , precursor_mz_tolerance: float , precursor_rt_tolerance: float , ppm: bool ) -> FeatureMapping_FeatureToMs2Indices:
    """
    Cython signature: FeatureMapping_FeatureToMs2Indices assignMS2IndexToFeature(MSExperiment & spectra, FeatureMapping_FeatureMappingInfo & fm_info, double precursor_mz_tolerance, double precursor_rt_tolerance, bool ppm)
    """
    ...

def __static_File_basename(file: Union[bytes, str, String] ) -> Union[bytes, str, String]:
    """
    Cython signature: String basename(String file)
    """
    ...

def __static_PrecursorCorrection_correctToHighestIntensityMS1Peak(exp: MSExperiment , mz_tolerance: float , ppm: bool , delta_mzs: List[float] , mzs: List[float] , rts: List[float] ) -> Set[int]:
    """
    Cython signature: libcpp_set[size_t] correctToHighestIntensityMS1Peak(MSExperiment & exp, double mz_tolerance, bool ppm, libcpp_vector[double] & delta_mzs, libcpp_vector[double] & mzs, libcpp_vector[double] & rts)
    """
    ...

def __static_PrecursorCorrection_correctToNearestFeature(features: FeatureMap , exp: MSExperiment , rt_tolerance_s: float , mz_tolerance: float , ppm: bool , believe_charge: bool , keep_original: bool , all_matching_features: bool , max_trace: int , debug_level: int ) -> Set[int]:
    """
    Cython signature: libcpp_set[size_t] correctToNearestFeature(FeatureMap & features, MSExperiment & exp, double rt_tolerance_s, double mz_tolerance, bool ppm, bool believe_charge, bool keep_original, bool all_matching_features, int max_trace, int debug_level)
    """
    ...

def __static_PrecursorCorrection_correctToNearestMS1Peak(exp: MSExperiment , mz_tolerance: float , ppm: bool , delta_mzs: List[float] , mzs: List[float] , rts: List[float] ) -> Set[int]:
    """
    Cython signature: libcpp_set[size_t] correctToNearestMS1Peak(MSExperiment & exp, double mz_tolerance, bool ppm, libcpp_vector[double] & delta_mzs, libcpp_vector[double] & mzs, libcpp_vector[double] & rts)
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

def __static_ExperimentalDesign_fromConsensusMap(c: ConsensusMap ) -> ExperimentalDesign:
    """
    Cython signature: ExperimentalDesign fromConsensusMap(ConsensusMap c)
    """
    ...

def __static_ExperimentalDesign_fromFeatureMap(f: FeatureMap ) -> ExperimentalDesign:
    """
    Cython signature: ExperimentalDesign fromFeatureMap(FeatureMap f)
    """
    ...

def __static_ExperimentalDesign_fromIdentifications(proteins: List[ProteinIdentification] ) -> ExperimentalDesign:
    """
    Cython signature: ExperimentalDesign fromIdentifications(const libcpp_vector[ProteinIdentification] & proteins)
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

def __static_PrecursorCorrection_getPrecursors(exp: MSExperiment , precursors: List[Precursor] , precursors_rt: List[float] , precursor_scan_index: List[int] ) -> None:
    """
    Cython signature: void getPrecursors(MSExperiment & exp, libcpp_vector[Precursor] & precursors, libcpp_vector[double] & precursors_rt, libcpp_vector[size_t] & precursor_scan_index)
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

def __static_PrecursorCorrection_writeHist(out_csv: String , delta_mzs: List[float] , mzs: List[float] , rts: List[float] ) -> None:
    """
    Cython signature: void writeHist(String & out_csv, libcpp_vector[double] & delta_mzs, libcpp_vector[double] & mzs, libcpp_vector[double] & rts)
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


class Attachment:
    """
    Cython implementation of _Attachment

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS::QcMLFile_1_1Attachment.html>`_
    """
    
    name: Union[bytes, str, String]
    
    id: Union[bytes, str, String]
    
    value: Union[bytes, str, String]
    
    cvRef: Union[bytes, str, String]
    
    cvAcc: Union[bytes, str, String]
    
    unitRef: Union[bytes, str, String]
    
    unitAcc: Union[bytes, str, String]
    
    binary: Union[bytes, str, String]
    
    qualityRef: Union[bytes, str, String]
    
    colTypes: List[bytes]
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void Attachment()
        """
        ...
    
    @overload
    def __init__(self, in_0: Attachment ) -> None:
        """
        Cython signature: void Attachment(Attachment &)
        """
        ...
    
    def toXMLString(self, indentation_level: int ) -> Union[bytes, str, String]:
        """
        Cython signature: String toXMLString(unsigned int indentation_level)
        """
        ...
    
    def toCSVString(self, separator: Union[bytes, str, String] ) -> Union[bytes, str, String]:
        """
        Cython signature: String toCSVString(String separator)
        """
        ...
    
    def __richcmp__(self, other: Attachment, op: int) -> Any:
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


class ConsensusIDAlgorithmRanks:
    """
    Cython implementation of _ConsensusIDAlgorithmRanks

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1ConsensusIDAlgorithmRanks.html>`_
      -- Inherits from ['ConsensusIDAlgorithmIdentity']
    """
    
    def __init__(self) -> None:
        """
        Cython signature: void ConsensusIDAlgorithmRanks()
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


class ElutionModelFitter:
    """
    Cython implementation of _ElutionModelFitter

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1ElutionModelFitter.html>`_
      -- Inherits from ['DefaultParamHandler']
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void ElutionModelFitter()
        Helper class for fitting elution models to features
        """
        ...
    
    @overload
    def __init__(self, in_0: ElutionModelFitter ) -> None:
        """
        Cython signature: void ElutionModelFitter(ElutionModelFitter &)
        """
        ...
    
    def fitElutionModels(self, features: FeatureMap ) -> None:
        """
        Cython signature: void fitElutionModels(FeatureMap & features)
        Fit models of elution profiles to all features (and validate them)
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


class ExperimentalDesign:
    """
    Cython implementation of _ExperimentalDesign

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1ExperimentalDesign.html>`_

    Representation of an experimental design in OpenMS. Instances can be loaded with the ExperimentalDesignFile class
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void ExperimentalDesign()
        """
        ...
    
    @overload
    def __init__(self, in_0: ExperimentalDesign ) -> None:
        """
        Cython signature: void ExperimentalDesign(ExperimentalDesign &)
        """
        ...
    
    def getMSFileSection(self) -> List[ExperimentalDesign_MSFileSectionEntry]:
        """
        Cython signature: libcpp_vector[ExperimentalDesign_MSFileSectionEntry] getMSFileSection()
        """
        ...
    
    def setMSFileSection(self, msfile_section: List[ExperimentalDesign_MSFileSectionEntry] ) -> None:
        """
        Cython signature: void setMSFileSection(libcpp_vector[ExperimentalDesign_MSFileSectionEntry] msfile_section)
        """
        ...
    
    def getSampleSection(self) -> ExperimentalDesign_SampleSection:
        """
        Cython signature: ExperimentalDesign_SampleSection getSampleSection()
        Returns the Sample Section of the experimental design file
        """
        ...
    
    def setSampleSection(self, sample_section: ExperimentalDesign_SampleSection ) -> None:
        """
        Cython signature: void setSampleSection(ExperimentalDesign_SampleSection sample_section)
        Sets the Sample Section of the experimental design file
        """
        ...
    
    def getNumberOfSamples(self) -> int:
        """
        Cython signature: unsigned int getNumberOfSamples()
        Returns the number of samples measured (= highest sample index)
        """
        ...
    
    def getNumberOfFractions(self) -> int:
        """
        Cython signature: unsigned int getNumberOfFractions()
        Returns the number of fractions (= highest fraction index)
        """
        ...
    
    def getNumberOfLabels(self) -> int:
        """
        Cython signature: unsigned int getNumberOfLabels()
        Returns the number of labels per file
        """
        ...
    
    def getNumberOfMSFiles(self) -> int:
        """
        Cython signature: unsigned int getNumberOfMSFiles()
        Returns the number of MS files (= fractions * fraction_groups)
        """
        ...
    
    def getNumberOfFractionGroups(self) -> int:
        """
        Cython signature: unsigned int getNumberOfFractionGroups()
        Allows to group fraction ids and source files. Return the number of fraction_groups
        """
        ...
    
    def getSample(self, fraction_group: int , label: int ) -> int:
        """
        Cython signature: unsigned int getSample(unsigned int fraction_group, unsigned int label)
        Returns sample index (depends on fraction_group and label)
        """
        ...
    
    def isFractionated(self) -> bool:
        """
        Cython signature: bool isFractionated()
        Returns whether at least one fraction_group in this experimental design is fractionated
        """
        ...
    
    def sameNrOfMSFilesPerFraction(self) -> bool:
        """
        Cython signature: bool sameNrOfMSFilesPerFraction()
        Returns if each fraction number is associated with the same number of fraction_group
        """
        ...
    
    fromConsensusMap: __static_ExperimentalDesign_fromConsensusMap
    
    fromFeatureMap: __static_ExperimentalDesign_fromFeatureMap
    
    fromIdentifications: __static_ExperimentalDesign_fromIdentifications 


class ExperimentalDesign_MSFileSectionEntry:
    """
    Cython implementation of _ExperimentalDesign_MSFileSectionEntry

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1ExperimentalDesign_MSFileSectionEntry.html>`_
    """
    
    path: bytes
    
    fraction_group: int
    
    fraction: int
    
    label: int
    
    sample: int
    
    def __init__(self) -> None:
        """
        Cython signature: void ExperimentalDesign_MSFileSectionEntry()
        """
        ... 


class ExperimentalDesign_SampleSection:
    """
    Cython implementation of _ExperimentalDesign_SampleSection

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1ExperimentalDesign_SampleSection.html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void ExperimentalDesign_SampleSection()
        """
        ...
    
    @overload
    def __init__(self, in_0: ExperimentalDesign_SampleSection ) -> None:
        """
        Cython signature: void ExperimentalDesign_SampleSection(ExperimentalDesign_SampleSection)
        """
        ...
    
    def getSamples(self) -> Set[bytes]:
        """
        Cython signature: libcpp_set[String] getSamples()
        Returns a set of all samples that are present in the sample section
        """
        ...
    
    def getFactors(self) -> Set[bytes]:
        """
        Cython signature: libcpp_set[String] getFactors()
        Returns a set of all factors (column names) that were defined for the sample section
        """
        ...
    
    def hasSample(self, sample: int ) -> bool:
        """
        Cython signature: bool hasSample(unsigned int sample)
        Checks whether sample section has row for a sample number
        """
        ...
    
    def hasFactor(self, factor: String ) -> bool:
        """
        Cython signature: bool hasFactor(String & factor)
        Checks whether Sample Section has a specific factor (i.e. column name)
        """
        ...
    
    def getFactorValue(self, sample: int , factor: String ) -> Union[bytes, str, String]:
        """
        Cython signature: String getFactorValue(unsigned int sample, String & factor)
        Returns value of factor for given sample and factor name
        """
        ... 


class ExperimentalSettings:
    """
    Cython implementation of _ExperimentalSettings

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1ExperimentalSettings.html>`_
      -- Inherits from ['DocumentIdentifier', 'MetaInfoInterface']

    Description of the experimental settings, provides meta-information
    about an LC-MS/MS injection.
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void ExperimentalSettings()
        """
        ...
    
    @overload
    def __init__(self, in_0: ExperimentalSettings ) -> None:
        """
        Cython signature: void ExperimentalSettings(ExperimentalSettings &)
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
    
    def __richcmp__(self, other: ExperimentalSettings, op: int) -> Any:
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


class GNPSMetaValueFile:
    """
    Cython implementation of _GNPSMetaValueFile

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1GNPSMetaValueFile.html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void GNPSMetaValueFile()
        """
        ...
    
    @overload
    def __init__(self, in_0: GNPSMetaValueFile ) -> None:
        """
        Cython signature: void GNPSMetaValueFile(GNPSMetaValueFile &)
        """
        ...
    
    def store(self, consensus_map: ConsensusMap , output_file: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void store(const ConsensusMap & consensus_map, const String & output_file)
        Write meta value table (tsv file) from a list of mzML files. Required for GNPS FBMN.
        
        This will produce the minimal required meta values and can be extended manually.
        
        :param consensus_map: Input ConsensusMap from which the input mzML files will be determined.
        :param output_file: Output file path for the meta value table.
        """
        ... 


class IMSElement:
    """
    Cython implementation of _IMSElement

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS::ims::IMSElement_1_1IMSElement.html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void IMSElement()
        Represents a chemical atom with name and isotope distribution
        """
        ...
    
    @overload
    def __init__(self, in_0: IMSElement ) -> None:
        """
        Cython signature: void IMSElement(IMSElement &)
        """
        ...
    
    @overload
    def __init__(self, name: bytes , isotopes: IMSIsotopeDistribution ) -> None:
        """
        Cython signature: void IMSElement(libcpp_string & name, IMSIsotopeDistribution & isotopes)
        """
        ...
    
    @overload
    def __init__(self, name: bytes , mass: float ) -> None:
        """
        Cython signature: void IMSElement(libcpp_string & name, double mass)
        """
        ...
    
    @overload
    def __init__(self, name: bytes , nominal_mass: int ) -> None:
        """
        Cython signature: void IMSElement(libcpp_string & name, unsigned int nominal_mass)
        """
        ...
    
    def getName(self) -> bytes:
        """
        Cython signature: libcpp_string getName()
        Gets element's name
        """
        ...
    
    def setName(self, name: bytes ) -> None:
        """
        Cython signature: void setName(libcpp_string & name)
        Sets element's name
        """
        ...
    
    def getSequence(self) -> bytes:
        """
        Cython signature: libcpp_string getSequence()
        Gets element's sequence
        """
        ...
    
    def setSequence(self, sequence: bytes ) -> None:
        """
        Cython signature: void setSequence(libcpp_string & sequence)
        Sets element's sequence
        """
        ...
    
    def getNominalMass(self) -> int:
        """
        Cython signature: unsigned int getNominalMass()
        Gets element's nominal mass
        """
        ...
    
    def getMass(self, index: int ) -> float:
        """
        Cython signature: double getMass(int index)
        Gets mass of element's isotope 'index'
        """
        ...
    
    def getAverageMass(self) -> float:
        """
        Cython signature: double getAverageMass()
        Gets element's average mass
        """
        ...
    
    def getIonMass(self, electrons_number: int ) -> float:
        """
        Cython signature: double getIonMass(int electrons_number)
        Gets ion mass of element. By default ion lacks 1 electron, but this can be changed by setting other 'electrons_number'
        """
        ...
    
    def getIsotopeDistribution(self) -> IMSIsotopeDistribution:
        """
        Cython signature: IMSIsotopeDistribution getIsotopeDistribution()
        Gets element's isotope distribution
        """
        ...
    
    def setIsotopeDistribution(self, isotopes: IMSIsotopeDistribution ) -> None:
        """
        Cython signature: void setIsotopeDistribution(IMSIsotopeDistribution & isotopes)
        Sets element's isotope distribution
        """
        ...
    
    def __richcmp__(self, other: IMSElement, op: int) -> Any:
        ... 


class InspectOutfile:
    """
    Cython implementation of _InspectOutfile

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1InspectOutfile.html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void InspectOutfile()
        This class serves to read in an Inspect outfile and write an idXML file
        """
        ...
    
    @overload
    def __init__(self, in_0: InspectOutfile ) -> None:
        """
        Cython signature: void InspectOutfile(InspectOutfile &)
        """
        ...
    
    def load(self, result_filename: Union[bytes, str, String] , peptide_identifications: PeptideIdentificationList , protein_identification: ProteinIdentification , p_value_threshold: float , database_filename: Union[bytes, str, String] ) -> List[int]:
        """
        Cython signature: libcpp_vector[size_t] load(const String & result_filename, PeptideIdentificationList & peptide_identifications, ProteinIdentification & protein_identification, double p_value_threshold, const String & database_filename)
        Load the results of an Inspect search
        
        
        :param result_filename: Input parameter which is the file name of the input file
        :param peptide_identifications: Output parameter which holds the peptide identifications from the given file
        :param protein_identification: Output parameter which holds the protein identifications from the given file
        :param p_value_threshold:
        :param database_filename:
        :raises:
          Exception: FileNotFound is thrown if the given file could not be found
        :raises:
          Exception: ParseError is thrown if the given file could not be parsed
        :raises:
          Exception: FileEmpty is thrown if the given file is empty
        """
        ...
    
    def getWantedRecords(self, result_filename: Union[bytes, str, String] , p_value_threshold: float ) -> List[int]:
        """
        Cython signature: libcpp_vector[size_t] getWantedRecords(const String & result_filename, double p_value_threshold)
        Loads only results which exceeds a given p-value threshold
        
        
        :param result_filename: The filename of the results file
        :param p_value_threshold: Only identifications exceeding this threshold are read
        :raises:
          Exception: FileNotFound is thrown if the given file could not be found
        :raises:
          Exception: FileEmpty is thrown if the given file is empty
        """
        ...
    
    def compressTrieDB(self, database_filename: Union[bytes, str, String] , index_filename: Union[bytes, str, String] , wanted_records: List[int] , snd_database_filename: Union[bytes, str, String] , snd_index_filename: Union[bytes, str, String] , append: bool ) -> None:
        """
        Cython signature: void compressTrieDB(const String & database_filename, const String & index_filename, libcpp_vector[size_t] & wanted_records, const String & snd_database_filename, const String & snd_index_filename, bool append)
        Generates a trie database from another one, using the wanted records only
        """
        ...
    
    def generateTrieDB(self, source_database_filename: Union[bytes, str, String] , database_filename: Union[bytes, str, String] , index_filename: Union[bytes, str, String] , append: bool , species: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void generateTrieDB(const String & source_database_filename, const String & database_filename, const String & index_filename, bool append, const String species)
        Generates a trie database from a given one (the type of database is determined by getLabels)
        """
        ...
    
    def getACAndACType(self, line: Union[bytes, str, String] , accession: String , accession_type: String ) -> None:
        """
        Cython signature: void getACAndACType(String line, String & accession, String & accession_type)
        Retrieve the accession type and accession number from a protein description line
        """
        ...
    
    def getLabels(self, source_database_filename: Union[bytes, str, String] , ac_label: String , sequence_start_label: String , sequence_end_label: String , comment_label: String , species_label: String ) -> None:
        """
        Cython signature: void getLabels(const String & source_database_filename, String & ac_label, String & sequence_start_label, String & sequence_end_label, String & comment_label, String & species_label)
        Retrieve the labels of a given database (at the moment FASTA and Swissprot)
        """
        ...
    
    def getSequences(self, database_filename: Union[bytes, str, String] , wanted_records: Dict[int, int] , sequences: List[bytes] ) -> List[int]:
        """
        Cython signature: libcpp_vector[size_t] getSequences(const String & database_filename, libcpp_map[size_t,size_t] & wanted_records, libcpp_vector[String] & sequences)
        Retrieve sequences from a trie database
        """
        ...
    
    def getExperiment(self, exp: MSExperiment , type_: String , in_filename: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void getExperiment(MSExperiment & exp, String & type_, const String & in_filename)
        Get the experiment from a file
        """
        ...
    
    def getSearchEngineAndVersion(self, cmd_output: Union[bytes, str, String] , protein_identification: ProteinIdentification ) -> bool:
        """
        Cython signature: bool getSearchEngineAndVersion(const String & cmd_output, ProteinIdentification & protein_identification)
        Get the search engine and its version from the output of the InsPecT executable without parameters. Returns true on success, false otherwise
        """
        ...
    
    def readOutHeader(self, filename: Union[bytes, str, String] , header_line: Union[bytes, str, String] , spectrum_file_column: int , scan_column: int , peptide_column: int , protein_column: int , charge_column: int , MQ_score_column: int , p_value_column: int , record_number_column: int , DB_file_pos_column: int , spec_file_pos_column: int , number_of_columns: int ) -> None:
        """
        Cython signature: void readOutHeader(const String & filename, const String & header_line, int & spectrum_file_column, int & scan_column, int & peptide_column, int & protein_column, int & charge_column, int & MQ_score_column, int & p_value_column, int & record_number_column, int & DB_file_pos_column, int & spec_file_pos_column, size_t & number_of_columns)
        Read the header of an inspect output file and retrieve various information
        """
        ...
    
    def __richcmp__(self, other: InspectOutfile, op: int) -> Any:
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


class MSSpectrum:
    """
    Cython implementation of _MSSpectrum

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1MSSpectrum.html>`_
      -- Inherits from ['SpectrumSettings', 'RangeManagerMzInt']

    The representation of a 1D spectrum.
    Raw data access is proved by `get_peaks` and `set_peaks`, which yields numpy arrays
    Iterations yields access to underlying peak objects but is slower
    Extra data arrays can be accessed through getFloatDataArrays / getIntegerDataArrays / getStringDataArrays
    See help(SpectrumSettings) for information about meta-information
    
    Usage:
    
    .. code-block:: python
    
      ms_level = spectrum.getMSLevel()
      rt = spectrum.getRT()
      mz, intensities = spectrum.get_peaks()
    
    
    Usage:
    
    .. code-block:: python
    
      from pyopenms import *
    
      spectrum = MSSpectrum()
      spectrum.setDriftTime(25) # 25 ms
      spectrum.setRT(205.2) # 205.2 s
      spectrum.setMSLevel(3) # MS3
      p = Precursor()
      p.setIsolationWindowLowerOffset(1.5)
      p.setIsolationWindowUpperOffset(1.5)
      p.setMZ(600) # isolation at 600 +/- 1.5 Th
      p.setActivationEnergy(40) # 40 eV
      p.setCharge(4) # 4+ ion
      spectrum.setPrecursors( [p] )
    
      # Add raw data to spectrum
      spectrum.set_peaks( ([401.5], [900]) )
    
      # Additional data arrays / peak annotations
      fda = FloatDataArray()
      fda.setName("Signal to Noise Array")
      fda.push_back(15)
      sda = StringDataArray()
      sda.setName("Peak annotation")
      sda.push_back("y15++")
      spectrum.setFloatDataArrays( [fda] )
      spectrum.setStringDataArrays( [sda] )
    
      # Add spectrum to MSExperiment
      exp = MSExperiment()
      exp.addSpectrum(spectrum)
    
      # Add second spectrum and store as mzML file
      spectrum2 = MSSpectrum()
      spectrum2.set_peaks( ([1, 2], [1, 2]) )
      exp.addSpectrum(spectrum2)
    
      MzMLFile().store("testfile.mzML", exp)
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void MSSpectrum()
        """
        ...
    
    @overload
    def __init__(self, in_0: MSSpectrum ) -> None:
        """
        Cython signature: void MSSpectrum(MSSpectrum &)
        """
        ...
    
    def getRT(self) -> float:
        """
        Cython signature: double getRT()
        Returns the absolute retention time (in seconds)
        """
        ...
    
    def setRT(self, in_0: float ) -> None:
        """
        Cython signature: void setRT(double)
        Sets the absolute retention time (in seconds)
        """
        ...
    
    def getDriftTime(self) -> float:
        """
        Cython signature: double getDriftTime()
        Returns the drift time (-1 if not set)
        """
        ...
    
    def setDriftTime(self, in_0: float ) -> None:
        """
        Cython signature: void setDriftTime(double)
        Sets the drift time (-1 if not set)
        """
        ...
    
    def getDriftTimeUnit(self) -> int:
        """
        Cython signature: DriftTimeUnit getDriftTimeUnit()
        """
        ...
    
    def getDriftTimeUnitAsString(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getDriftTimeUnitAsString()
        """
        ...
    
    def setDriftTimeUnit(self, dt: int ) -> None:
        """
        Cython signature: void setDriftTimeUnit(DriftTimeUnit dt)
        """
        ...
    
    def getIMFormat(self) -> int:
        """
        Cython signature: IMFormat getIMFormat()
        Returns the ion mobility format
        """
        ...
    
    def setIMFormat(self, im_format: int ) -> None:
        """
        Cython signature: void setIMFormat(IMFormat im_format)
        Sets the ion mobility format
        """
        ...
    
    def containsIMData(self) -> bool:
        """
        Cython signature: bool containsIMData()
        """
        ...
    
    def getMSLevel(self) -> int:
        """
        Cython signature: unsigned int getMSLevel()
        Returns the MS level
        """
        ...
    
    def setMSLevel(self, in_0: int ) -> None:
        """
        Cython signature: void setMSLevel(unsigned int)
        Sets the MS level
        """
        ...
    
    def getName(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getName()
        """
        ...
    
    def setName(self, in_0: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setName(String)
        """
        ...
    
    def size(self) -> int:
        """
        Cython signature: size_t size()
        Returns the number of peaks in the spectrum
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
    
    def __getitem__(self, in_0: int ) -> Peak1D:
        """
        Cython signature: Peak1D & operator[](size_t)
        """
        ...
    def __setitem__(self, key: int, value: Peak1D) -> None:
        """Cython signature: Peak1D & operator[](size_t)"""
        ...
    
    def updateRanges(self) -> None:
        """
        Cython signature: void updateRanges()
        """
        ...
    
    def clear(self, clear_meta_data: bool ) -> None:
        """
        Cython signature: void clear(bool clear_meta_data)
        Clears all data (and meta data if clear_meta_data is true)
        """
        ...
    
    def push_back(self, in_0: Peak1D ) -> None:
        """
        Cython signature: void push_back(Peak1D)
        Append a peak
        """
        ...
    
    def isSorted(self) -> bool:
        """
        Cython signature: bool isSorted()
        Returns true if the spectrum is sorte by m/z
        """
        ...
    
    @overload
    def findNearest(self, mz: float ) -> int:
        """
        Cython signature: int findNearest(double mz)
        Returns the index of the closest peak in m/z
        """
        ...
    
    @overload
    def findNearest(self, mz: float , tolerance: float ) -> int:
        """
        Cython signature: int findNearest(double mz, double tolerance)
        Returns the index of the closest peak in the provided +/- m/z tolerance window (-1 if none match)
        """
        ...
    
    @overload
    def findNearest(self, mz: float , tolerance_left: float , tolerance_right: float ) -> int:
        """
        Cython signature: int findNearest(double mz, double tolerance_left, double tolerance_right)
        Returns the index of the closest peak in the provided abs. m/z tolerance window to the left and right (-1 if none match)
        """
        ...
    
    def findHighestInWindow(self, mz: float , tolerance_left: float , tolerance_right: float ) -> int:
        """
        Cython signature: int findHighestInWindow(double mz, double tolerance_left, double tolerance_right)
        Returns the index of the highest peak in the provided abs. m/z tolerance window to the left and right (-1 if none match)
        """
        ...
    
    def select(self, indices: List[int] ) -> MSSpectrum:
        """
        Cython signature: MSSpectrum select(const libcpp_vector[size_t] & indices)
        Subset the spectrum by indices. Also applies to associated data arrays if present.
        """
        ...
    
    def calculateTIC(self) -> float:
        """
        Cython signature: double calculateTIC()
        Returns the total ion current (=sum) of peak intensities in the spectrum
        """
        ...
    
    def sortByIntensity(self, reverse: bool ) -> None:
        """
        Cython signature: void sortByIntensity(bool reverse)
        """
        ...
    
    def sortByPosition(self) -> None:
        """
        Cython signature: void sortByPosition()
        """
        ...
    
    def getFloatDataArrays(self) -> List[FloatDataArray]:
        """
        Cython signature: libcpp_vector[FloatDataArray] getFloatDataArrays()
        Returns the additional float data arrays to store e.g. meta data
        """
        ...
    
    def getIntegerDataArrays(self) -> List[IntegerDataArray]:
        """
        Cython signature: libcpp_vector[IntegerDataArray] getIntegerDataArrays()
        Returns the additional int data arrays to store e.g. meta data
        """
        ...
    
    def getStringDataArrays(self) -> List[StringDataArray]:
        """
        Cython signature: libcpp_vector[StringDataArray] getStringDataArrays()
        Returns the additional string data arrays to store e.g. meta data
        """
        ...
    
    def setFloatDataArrays(self, fda: List[FloatDataArray] ) -> None:
        """
        Cython signature: void setFloatDataArrays(libcpp_vector[FloatDataArray] fda)
        Sets the additional float data arrays to store e.g. meta data
        """
        ...
    
    def setIntegerDataArrays(self, ida: List[IntegerDataArray] ) -> None:
        """
        Cython signature: void setIntegerDataArrays(libcpp_vector[IntegerDataArray] ida)
        Sets the additional int data arrays to store e.g. meta data
        """
        ...
    
    def setStringDataArrays(self, sda: List[StringDataArray] ) -> None:
        """
        Cython signature: void setStringDataArrays(libcpp_vector[StringDataArray] sda)
        Sets the additional string data arrays to store e.g. meta data
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
    
    def __richcmp__(self, other: MSSpectrum, op: int) -> Any:
        ...
    
    def __iter__(self) -> Peak1D:
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


class MzMLSqliteHandler:
    """
    Cython implementation of _MzMLSqliteHandler

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS::Internal_1_1MzMLSqliteHandler.html>`_
    """
    
    @overload
    def __init__(self, filename: Union[bytes, str, String] , run_id: int ) -> None:
        """
        Cython signature: void MzMLSqliteHandler(String filename, uint64_t run_id)
        """
        ...
    
    @overload
    def __init__(self, in_0: MzMLSqliteHandler ) -> None:
        """
        Cython signature: void MzMLSqliteHandler(MzMLSqliteHandler &)
        """
        ...
    
    def readExperiment(self, exp: MSExperiment , meta_only: bool ) -> None:
        """
        Cython signature: void readExperiment(MSExperiment & exp, bool meta_only)
        Read an experiment into an MSExperiment structure
        
        
        :param exp: The result data structure
        :param meta_only: Only read the meta data
        """
        ...
    
    def readSpectra(self, exp: List[MSSpectrum] , indices: List[int] , meta_only: bool ) -> None:
        """
        Cython signature: void readSpectra(libcpp_vector[MSSpectrum] & exp, libcpp_vector[int] indices, bool meta_only)
        Read a set of spectra (potentially restricted to a subset)
        
        
        :param exp: The result data structure
        :param indices: A list of indices restricting the resulting spectra only to those specified here
        :param meta_only: Only read the meta data
        """
        ...
    
    def readChromatograms(self, exp: List[MSChromatogram] , indices: List[int] , meta_only: bool ) -> None:
        """
        Cython signature: void readChromatograms(libcpp_vector[MSChromatogram] & exp, libcpp_vector[int] indices, bool meta_only)
        Read a set of chromatograms (potentially restricted to a subset)
        
        
        :param exp: The result data structure
        :param indices: A list of indices restricting the resulting spectra only to those specified here
        :param meta_only: Only read the meta data
        """
        ...
    
    def getNrSpectra(self) -> int:
        """
        Cython signature: size_t getNrSpectra()
        Returns number of spectra in the file, reutrns the number of spectra
        """
        ...
    
    def getNrChromatograms(self) -> int:
        """
        Cython signature: size_t getNrChromatograms()
        Returns the number of chromatograms in the file
        """
        ...
    
    def setConfig(self, write_full_meta: bool , use_lossy_compression: bool , linear_abs_mass_acc: float ) -> None:
        """
        Cython signature: void setConfig(bool write_full_meta, bool use_lossy_compression, double linear_abs_mass_acc)
        Sets file configuration
        
        
        :param write_full_meta: Whether to write a complete mzML meta data structure into the RUN_EXTRA field (allows complete recovery of the input file)
        :param use_lossy_compression: Whether to use lossy compression (ms numpress)
        :param linear_abs_mass_acc: Accepted loss in mass accuracy (absolute m/z, in Th)
        """
        ...
    
    def getSpectraIndicesbyRT(self, RT: float , deltaRT: float , indices: List[int] ) -> List[int]:
        """
        Cython signature: libcpp_vector[size_t] getSpectraIndicesbyRT(double RT, double deltaRT, libcpp_vector[int] indices)
        Returns spectral indices around a specific retention time
        
        :param RT: The retention time
        :param deltaRT: Tolerance window around RT (if less or equal than zero, only the first spectrum *after* RT is returned)
        :param indices: Spectra to consider (if empty, all spectra are considered)
        :return: The indices of the spectra within RT +/- deltaRT
        """
        ...
    
    def writeExperiment(self, exp: MSExperiment ) -> None:
        """
        Cython signature: void writeExperiment(MSExperiment exp)
        Write an MSExperiment to disk
        """
        ...
    
    def createTables(self) -> None:
        """
        Cython signature: void createTables()
        Create data tables for a new file
        """
        ...
    
    def writeSpectra(self, spectra: List[MSSpectrum] ) -> None:
        """
        Cython signature: void writeSpectra(libcpp_vector[MSSpectrum] spectra)
        Writes a set of spectra to disk
        """
        ...
    
    def writeChromatograms(self, chroms: List[MSChromatogram] ) -> None:
        """
        Cython signature: void writeChromatograms(libcpp_vector[MSChromatogram] chroms)
        Writes a set of chromatograms to disk
        """
        ...
    
    def writeRunLevelInformation(self, exp: MSExperiment , write_full_meta: bool ) -> None:
        """
        Cython signature: void writeRunLevelInformation(MSExperiment exp, bool write_full_meta)
        Write the run-level information for an experiment into tables
        
        This is a low level function, do not call this function unless you know what you are doing
        
        
        :param exp: The result data structure
        :param meta_only: Only read the meta data
        """
        ...
    
    def getRunID(self) -> int:
        """
        Cython signature: uint64_t getRunID()
        Extract the `RUN` ID from the sqMass file
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


class PrecursorCorrection:
    """
    Cython implementation of _PrecursorCorrection

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1PrecursorCorrection.html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void PrecursorCorrection()
        """
        ...
    
    @overload
    def __init__(self, in_0: PrecursorCorrection ) -> None:
        """
        Cython signature: void PrecursorCorrection(PrecursorCorrection &)
        """
        ...
    
    correctToHighestIntensityMS1Peak: __static_PrecursorCorrection_correctToHighestIntensityMS1Peak
    
    correctToNearestFeature: __static_PrecursorCorrection_correctToNearestFeature
    
    correctToNearestMS1Peak: __static_PrecursorCorrection_correctToNearestMS1Peak
    
    getPrecursors: __static_PrecursorCorrection_getPrecursors
    
    writeHist: __static_PrecursorCorrection_writeHist 


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


class ProteaseDigestion:
    """
    Cython implementation of _ProteaseDigestion

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1ProteaseDigestion.html>`_
      -- Inherits from ['EnzymaticDigestion']

    Class for the enzymatic digestion of proteins
    
    Digestion can be performed using simple regular expressions, e.g. [KR] | [^P] for trypsin.
    Also missed cleavages can be modeled, i.e. adjacent peptides are not cleaved
    due to enzyme malfunction/access restrictions. If n missed cleavages are allowed, all possible resulting
    peptides (cleaved and uncleaved) with up to n missed cleavages are returned.
    Thus no random selection of just n specific missed cleavage sites is performed.
    If specificity is set to semi-specific, digestion also returns semi-specific products,
    i.e. with only one end at actual cleavage sites.
    
    Usage:
    
    .. code-block:: python
    
          from pyopenms import *
          from urllib.request import urlretrieve
          #
          urlretrieve ("http://www.uniprot.org/uniprot/P02769.fasta", "bsa.fasta")
          #
          dig = ProteaseDigestion()
          dig.setEnzyme('Lys-C')
          bsa_string = "".join([l.strip() for l in open("bsa.fasta").readlines()[1:]])
          bsa_oms_string = String(bsa_string) # convert python string to OpenMS::String for further processing
          #
          minlen = 6
          maxlen = 30
          #
          # Using AASequence and digest
          result_digest = []
          result_digest_min_max = []
          bsa_aaseq = AASequence.fromString(bsa_oms_string)
          dig.digest(bsa_aaseq, result_digest)
          dig.digest(bsa_aaseq, result_digest_min_max, minlen, maxlen)
          print(result_digest[4].toString()) # GLVLIAFSQYLQQCPFDEHVK
          print(len(result_digest)) # 57 peptides
          print(result_digest_min_max[4].toString()) # LVNELTEFAK
          print(len(result_digest_min_max)) # 42 peptides
          #
          # Semi-specific digestion
          result_semispecific = []
          dig.setSpecificity(EnzymaticDigestion.SPEC_SEMI)
          dig.digest(bsa_aaseq, result_semispecific)
          #
          # Using digestUnmodified without the need for AASequence from the EnzymaticDigestion base class
          result_digest_unmodified = []
          dig.digestUnmodified(StringView(bsa_oms_string), result_digest_unmodified, minlen, maxlen)
          print(result_digest_unmodified[4].getString()) # LVNELTEFAK
          print(len(result_digest_unmodified)) # 42 peptides
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void ProteaseDigestion()
        """
        ...
    
    @overload
    def __init__(self, in_0: ProteaseDigestion ) -> None:
        """
        Cython signature: void ProteaseDigestion(ProteaseDigestion &)
        """
        ...
    
    @overload
    def setEnzyme(self, name: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setEnzyme(String name)
        Sets the enzyme for the digestion (by name)
        """
        ...
    
    @overload
    def setEnzyme(self, enzyme: DigestionEnzyme ) -> None:
        """
        Cython signature: void setEnzyme(DigestionEnzyme * enzyme)
        Sets the enzyme for the digestion
        """
        ...
    
    @overload
    def digest(self, protein: AASequence , output: List[AASequence] ) -> int:
        """
        Cython signature: size_t digest(AASequence & protein, libcpp_vector[AASequence] & output)
        """
        ...
    
    @overload
    def digest(self, protein: AASequence , output: List[AASequence] , min_length: int , max_length: int ) -> int:
        """
        Cython signature: size_t digest(AASequence & protein, libcpp_vector[AASequence] & output, size_t min_length, size_t max_length)
          Performs the enzymatic digestion of a protein.
        
        
          :param protein: Sequence to digest
          :param output: Digestion products (peptides)
          :param min_length: Minimal length of reported products
          :param max_length: Maximal length of reported products (0 = no restriction)
          :return: Number of discarded digestion products (which are not matching length restrictions)
        """
        ...
    
    def peptideCount(self, protein: AASequence ) -> int:
        """
        Cython signature: size_t peptideCount(AASequence & protein)
        Returns the number of peptides a digestion of protein would yield under the current enzyme and missed cleavage settings
        """
        ...
    
    @overload
    def isValidProduct(self, protein: AASequence , pep_pos: int , pep_length: int , ignore_missed_cleavages: bool , methionine_cleavage: bool ) -> bool:
        """
        Cython signature: bool isValidProduct(AASequence protein, size_t pep_pos, size_t pep_length, bool ignore_missed_cleavages, bool methionine_cleavage)
          Variant of EnzymaticDigestion::isValidProduct() with support for n-term protein cleavage and random D|P cleavage
        
          Checks if peptide is a valid digestion product of the enzyme, taking into account specificity and the flags provided here
        
        
          :param protein: Protein sequence
          :param pep_pos: Starting index of potential peptide
          :param pep_length: Length of potential peptide
          :param ignore_missed_cleavages: Do not compare MC's of potential peptide to the maximum allowed MC's
          :param allow_nterm_protein_cleavage: Regard peptide as n-terminal of protein if it starts only at pos=1 or 2 and protein starts with 'M'
          :param allow_random_asp_pro_cleavage: Allow cleavage at D|P sites to count as n/c-terminal
          :return: True if peptide has correct n/c terminals (according to enzyme, specificity and above flags)
        """
        ...
    
    @overload
    def isValidProduct(self, protein: Union[bytes, str, String] , pep_pos: int , pep_length: int , ignore_missed_cleavages: bool , methionine_cleavage: bool ) -> bool:
        """
        Cython signature: bool isValidProduct(String protein, size_t pep_pos, size_t pep_length, bool ignore_missed_cleavages, bool methionine_cleavage)
        Forwards to isValidProduct using protein.toUnmodifiedString()
        """
        ...
    
    @overload
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


class RNaseDigestion:
    """
    Cython implementation of _RNaseDigestion

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1RNaseDigestion.html>`_
      -- Inherits from ['EnzymaticDigestion']

    Class for the enzymatic digestion of RNA
    
    Usage:
    
    .. code-block:: python
    
          from pyopenms import *
          oligo = NASequence.fromString("pAUGUCGCAG");
    
          dig = RNaseDigestion()
          dig.setEnzyme("RNase_T1")
    
          result = []
          dig.digest(oligo, result)
          for fragment in result:
            print (fragment)
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void RNaseDigestion()
        """
        ...
    
    @overload
    def __init__(self, in_0: RNaseDigestion ) -> None:
        """
        Cython signature: void RNaseDigestion(RNaseDigestion &)
        """
        ...
    
    @overload
    def setEnzyme(self, name: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setEnzyme(String name)
        Sets the enzyme for the digestion (by name)
        """
        ...
    
    @overload
    def setEnzyme(self, enzyme: DigestionEnzyme ) -> None:
        """
        Cython signature: void setEnzyme(DigestionEnzyme * enzyme)
        Sets the enzyme for the digestion
        """
        ...
    
    @overload
    def digest(self, rna: NASequence , output: List[NASequence] ) -> None:
        """
        Cython signature: void digest(NASequence & rna, libcpp_vector[NASequence] & output)
        """
        ...
    
    @overload
    def digest(self, rna: NASequence , output: List[NASequence] , min_length: int , max_length: int ) -> None:
        """
        Cython signature: void digest(NASequence & rna, libcpp_vector[NASequence] & output, size_t min_length, size_t max_length)
        Performs the enzymatic digestion of a (potentially modified) RNA
        
        :param rna: Sequence to digest
        :param output: Digestion productsq
        :param min_length: Minimal length of reported products
        :param max_length: Maximal length of reported products (0 = no restriction)
        :returns: Number of discarded digestion products (which are not matching length restrictions)
        Performs the enzymatic digestion of all RNA parent molecules in IdentificationData (id_data)
        
        :param id_data: IdentificationData object which includes sequences to digest
        :param min_length: Minimal length of reported products
        :param max_length: Maximal length of reported products (0 = no restriction)
        :returns: Number of discarded digestion products (which are not matching length restrictions)
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


class Sample:
    """
    Cython implementation of _Sample

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1Sample.html>`_
      -- Inherits from ['MetaInfoInterface']
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void Sample()
        """
        ...
    
    @overload
    def __init__(self, in_0: Sample ) -> None:
        """
        Cython signature: void Sample(Sample &)
        """
        ...
    
    def getName(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getName()
        """
        ...
    
    def setName(self, name: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setName(String name)
        """
        ...
    
    def getOrganism(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getOrganism()
        """
        ...
    
    def setOrganism(self, organism: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setOrganism(String organism)
        """
        ...
    
    def getNumber(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getNumber()
        Returns the sample number
        """
        ...
    
    def setNumber(self, number: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setNumber(String number)
        Sets the sample number (e.g. sample ID)
        """
        ...
    
    def getComment(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getComment()
        Returns the comment (default "")
        """
        ...
    
    def setComment(self, comment: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setComment(String comment)
        Sets the comment (may contain newline characters)
        """
        ...
    
    def getState(self) -> int:
        """
        Cython signature: SampleState getState()
        Returns the state of aggregation (default SAMPLENULL)
        """
        ...
    
    def setState(self, state: int ) -> None:
        """
        Cython signature: void setState(SampleState state)
        Sets the state of aggregation
        """
        ...
    
    def getMass(self) -> float:
        """
        Cython signature: double getMass()
        Returns the mass (in gram) (default 0.0)
        """
        ...
    
    def setMass(self, mass: float ) -> None:
        """
        Cython signature: void setMass(double mass)
        Sets the mass (in gram)
        """
        ...
    
    def getVolume(self) -> float:
        """
        Cython signature: double getVolume()
        Returns the volume (in ml) (default 0.0)
        """
        ...
    
    def setVolume(self, volume: float ) -> None:
        """
        Cython signature: void setVolume(double volume)
        Sets the volume (in ml)
        """
        ...
    
    def getConcentration(self) -> float:
        """
        Cython signature: double getConcentration()
        Returns the concentration (in g/l) (default 0.0)
        """
        ...
    
    def setConcentration(self, concentration: float ) -> None:
        """
        Cython signature: void setConcentration(double concentration)
        Sets the concentration (in g/l)
        """
        ...
    
    def getSubsamples(self) -> List[Sample]:
        """
        Cython signature: libcpp_vector[Sample] getSubsamples()
        Returns a reference to the vector of subsamples that were combined to create this sample
        """
        ...
    
    def setSubsamples(self, subsamples: List[Sample] ) -> None:
        """
        Cython signature: void setSubsamples(libcpp_vector[Sample] subsamples)
        Sets the vector of subsamples that were combined to create this sample
        """
        ...
    
    @staticmethod
    def getAllNamesOfSampleState() -> List[bytes]:
        """
        Cython signature: libcpp_vector[String] getAllNamesOfSampleState()
        Returns all sample state names known to OpenMS
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
    
    def __richcmp__(self, other: Sample, op: int) -> Any:
        ...
    SampleState : __SampleState 


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


class SequestOutfile:
    """
    Cython implementation of _SequestOutfile

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1SequestOutfile.html>`_

    Representation of a Sequest output file
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void SequestOutfile()
        Representation of a Sequest output file
        """
        ...
    
    @overload
    def __init__(self, in_0: SequestOutfile ) -> None:
        """
        Cython signature: void SequestOutfile(SequestOutfile &)
        """
        ...
    
    def load(self, result_filename: Union[bytes, str, String] , peptide_identifications: PeptideIdentificationList , protein_identification: ProteinIdentification , p_value_threshold: float , pvalues: List[float] , database: Union[bytes, str, String] , ignore_proteins_per_peptide: bool ) -> None:
        """
        Cython signature: void load(const String & result_filename, PeptideIdentificationList & peptide_identifications, ProteinIdentification & protein_identification, double p_value_threshold, libcpp_vector[double] & pvalues, const String & database, bool ignore_proteins_per_peptide)
        Loads data from a Sequest outfile
        
        :param result_filename: The file to be loaded
        :param peptide_identifications: The identifications
        :param protein_identification: The protein identifications
        :param p_value_threshold: The significance level (for the peptide hit scores)
        :param pvalues: A list with the pvalues of the peptides (pvalues computed with peptide prophet)
        :param database: The database used for the search
        :param ignore_proteins_per_peptide: This is a hack to deal with files that use a suffix like "+1" in column "Reference", but do not actually list extra protein references in subsequent lines
        """
        ...
    
    def getColumns(self, line: Union[bytes, str, String] , substrings: List[bytes] , number_of_columns: int , reference_column: int ) -> bool:
        """
        Cython signature: bool getColumns(const String & line, libcpp_vector[String] & substrings, size_t number_of_columns, size_t reference_column)
        Retrieves columns from a Sequest outfile line
        """
        ...
    
    def getACAndACType(self, line: Union[bytes, str, String] , accession: String , accession_type: String ) -> None:
        """
        Cython signature: void getACAndACType(String line, String & accession, String & accession_type)
        Retrieves the accession type and accession number from a protein description line
        """
        ...
    
    def __richcmp__(self, other: SequestOutfile, op: int) -> Any:
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


class SpectrumAccessOpenMSInMemory:
    """
    Cython implementation of _SpectrumAccessOpenMSInMemory

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1SpectrumAccessOpenMSInMemory.html>`_
      -- Inherits from ['ISpectrumAccess']
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void SpectrumAccessOpenMSInMemory()
        """
        ...
    
    @overload
    def __init__(self, in_0: SpectrumAccessOpenMS ) -> None:
        """
        Cython signature: void SpectrumAccessOpenMSInMemory(SpectrumAccessOpenMS &)
        """
        ...
    
    @overload
    def __init__(self, in_0: SpectrumAccessOpenMSCached ) -> None:
        """
        Cython signature: void SpectrumAccessOpenMSInMemory(SpectrumAccessOpenMSCached &)
        """
        ...
    
    @overload
    def __init__(self, in_0: SpectrumAccessOpenMSInMemory ) -> None:
        """
        Cython signature: void SpectrumAccessOpenMSInMemory(SpectrumAccessOpenMSInMemory &)
        """
        ...
    
    @overload
    def __init__(self, in_0: SpectrumAccessQuadMZTransforming ) -> None:
        """
        Cython signature: void SpectrumAccessOpenMSInMemory(SpectrumAccessQuadMZTransforming &)
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


class SpectrumAlignmentScore:
    """
    Cython implementation of _SpectrumAlignmentScore

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1SpectrumAlignmentScore.html>`_
      -- Inherits from ['DefaultParamHandler']

    Similarity score via spectra alignment
    
    This class implements a simple scoring based on the alignment of spectra. This alignment
    is implemented in the SpectrumAlignment class and performs a dynamic programming alignment
    of the peaks, minimizing the distances between the aligned peaks and maximizing the number
    of peak pairs
    
    The scoring is done via the simple formula score = sum / (sqrt(sum1 * sum2)). sum is the
    product of the intensities of the aligned peaks, with the given exponent (default is 2)
    sum1 and sum2 are the sum of the intensities squared for each peak of both spectra respectively
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void SpectrumAlignmentScore()
        """
        ...
    
    @overload
    def __init__(self, in_0: SpectrumAlignmentScore ) -> None:
        """
        Cython signature: void SpectrumAlignmentScore(SpectrumAlignmentScore &)
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


class Tagger:
    """
    Cython implementation of _Tagger

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1Tagger.html>`_

    Constructor for Tagger
    
    The parameter `max_charge_` should be >= `min_charge_`
    Also `max_tag_length` should be >= `min_tag_length`
    
    :param min_tag_length: The minimal sequence tag length
    :param ppm: The tolerance for matching residue masses to peak delta masses
    :param max_tag_length: The maximal sequence tag length
    :param min_charge: Minimal fragment charge considered for each sequence tag
    :param max_charge: Maximal fragment charge considered for each sequence tag
    :param fixed_mods: A list of modification names. The modified residues replace the unmodified versions
    :param var_mods: A list of modification names. The modified residues are added as additional entries to the list of residues
    """
    
    @overload
    def __init__(self, in_0: Tagger ) -> None:
        """
        Cython signature: void Tagger(Tagger &)
        """
        ...
    
    @overload
    def __init__(self, min_tag_length: int , ppm: float , max_tag_length: int , min_charge: int , max_charge: int , fixed_mods: List[bytes] , var_mods: List[bytes] ) -> None:
        """
        Cython signature: void Tagger(size_t min_tag_length, double ppm, size_t max_tag_length, size_t min_charge, size_t max_charge, const StringList & fixed_mods, const StringList & var_mods)
        """
        ...
    
    @overload
    def getTag(self, mzs: List[float] , tags: List[Union[bytes, str]] ) -> None:
        """
        Cython signature: void getTag(const libcpp_vector[double] & mzs, libcpp_vector[libcpp_utf8_string] & tags)
        Generate tags from mass vector `mzs`
        
        The parameter `tags` is filled with one string per sequence tag
        It uses the standard residues from ResidueDB including
        the fixed and variable modifications given to the constructor
        
        :param mzs: A vector of mz values, containing the mz values from a centroided fragment spectrum
        :param tags: The vector of tags, that is filled with this function
        """
        ...
    
    @overload
    def getTag(self, spec: MSSpectrum , tags: List[Union[bytes, str]] ) -> None:
        """
        Cython signature: void getTag(const MSSpectrum & spec, libcpp_vector[libcpp_utf8_string] & tags)
        Generate tags from an MSSpectrum
        
        The parameter `tags` is filled with one string per sequence tag
        It uses the standard residues from ResidueDB including
        the fixed and variable modifications given to the constructor
        
        :param spec: A centroided fragment spectrum
        :param tags: The vector of tags, that is filled with this function
        """
        ...
    
    def setMaxCharge(self, max_charge: int ) -> None:
        """
        Cython signature: void setMaxCharge(size_t max_charge)
        Change the maximal charge considered by the tagger
        
        Allows to change the maximal considered charge e.g. based on a spectra
        precursor charge without calling the constructor multiple times
        
        :param max_charge: The new maximal charge
        """
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


class __CombinationsLogic:
    None
    OR : int
    AND : int
    XOR : int

    def getMapping(self) -> Dict[int, str]:
       ... 


class __IntensityThresholdCalculation:
    None
    MANUAL : int
    AUTOMAXBYSTDEV : int
    AUTOMAXBYPERCENT : int

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


class __RequirementLevel:
    None
    MUST : int
    SHOULD : int
    MAY : int

    def getMapping(self) -> Dict[int, str]:
       ... 


class __SampleState:
    None
    SAMPLENULL : int
    SOLID : int
    LIQUID : int
    GAS : int
    SOLUTION : int
    EMULSION : int
    SUSPENSION : int
    SIZE_OF_SAMPLESTATE : int

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

