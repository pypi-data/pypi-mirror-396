from __future__ import annotations
from typing import overload, Any, List, Dict, Tuple, Set, Sequence, Union
from pyopenms import *  # pylint: disable=wildcard-import; lgtm(py/polluting-import)
import numpy as _np

from enum import IntEnum as _PyEnum


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


class AbsoluteQuantitationMethod:
    """
    Cython implementation of _AbsoluteQuantitationMethod

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1AbsoluteQuantitationMethod.html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void AbsoluteQuantitationMethod()
        """
        ...
    
    @overload
    def __init__(self, in_0: AbsoluteQuantitationMethod ) -> None:
        """
        Cython signature: void AbsoluteQuantitationMethod(AbsoluteQuantitationMethod &)
        """
        ...
    
    def setLLOD(self, llod: float ) -> None:
        """
        Cython signature: void setLLOD(double llod)
        """
        ...
    
    def setULOD(self, ulod: float ) -> None:
        """
        Cython signature: void setULOD(double ulod)
        """
        ...
    
    def getLLOD(self) -> float:
        """
        Cython signature: double getLLOD()
        """
        ...
    
    def getULOD(self) -> float:
        """
        Cython signature: double getULOD()
        """
        ...
    
    def setLLOQ(self, lloq: float ) -> None:
        """
        Cython signature: void setLLOQ(double lloq)
        """
        ...
    
    def setULOQ(self, uloq: float ) -> None:
        """
        Cython signature: void setULOQ(double uloq)
        """
        ...
    
    def getLLOQ(self) -> float:
        """
        Cython signature: double getLLOQ()
        """
        ...
    
    def getULOQ(self) -> float:
        """
        Cython signature: double getULOQ()
        """
        ...
    
    def checkLOD(self, value: float ) -> bool:
        """
        Cython signature: bool checkLOD(double value)
        """
        ...
    
    def checkLOQ(self, value: float ) -> bool:
        """
        Cython signature: bool checkLOQ(double value)
        """
        ...
    
    def setComponentName(self, component_name: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setComponentName(const String & component_name)
        """
        ...
    
    def setISName(self, IS_name: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setISName(const String & IS_name)
        """
        ...
    
    def setFeatureName(self, feature_name: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setFeatureName(const String & feature_name)
        """
        ...
    
    def getComponentName(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getComponentName()
        """
        ...
    
    def getISName(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getISName()
        """
        ...
    
    def getFeatureName(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getFeatureName()
        """
        ...
    
    def setConcentrationUnits(self, concentration_units: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setConcentrationUnits(const String & concentration_units)
        """
        ...
    
    def getConcentrationUnits(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getConcentrationUnits()
        """
        ...
    
    def setTransformationModel(self, transformation_model: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setTransformationModel(const String & transformation_model)
        """
        ...
    
    def setTransformationModelParams(self, transformation_model_param: Param ) -> None:
        """
        Cython signature: void setTransformationModelParams(Param transformation_model_param)
        """
        ...
    
    def getTransformationModel(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getTransformationModel()
        """
        ...
    
    def getTransformationModelParams(self) -> Param:
        """
        Cython signature: Param getTransformationModelParams()
        """
        ...
    
    def setNPoints(self, n_points: int ) -> None:
        """
        Cython signature: void setNPoints(int n_points)
        """
        ...
    
    def setCorrelationCoefficient(self, correlation_coefficient: float ) -> None:
        """
        Cython signature: void setCorrelationCoefficient(double correlation_coefficient)
        """
        ...
    
    def getNPoints(self) -> int:
        """
        Cython signature: int getNPoints()
        """
        ...
    
    def getCorrelationCoefficient(self) -> float:
        """
        Cython signature: double getCorrelationCoefficient()
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


class CVReference:
    """
    Cython implementation of _CVReference

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1CVReference.html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void CVReference()
        """
        ...
    
    @overload
    def __init__(self, in_0: CVReference ) -> None:
        """
        Cython signature: void CVReference(CVReference &)
        """
        ...
    
    def setName(self, name: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setName(const String & name)
        Sets the name of the CV reference
        """
        ...
    
    def getName(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getName()
        Returns the name of the CV reference
        """
        ...
    
    def setIdentifier(self, identifier: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setIdentifier(const String & identifier)
        Sets the CV identifier which is referenced
        """
        ...
    
    def getIdentifier(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getIdentifier()
        Returns the CV identifier which is referenced
        """
        ...
    
    def __richcmp__(self, other: CVReference, op: int) -> Any:
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


class ConvexHull2D:
    """
    Cython implementation of _ConvexHull2D

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1ConvexHull2D.html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void ConvexHull2D()
        """
        ...
    
    @overload
    def __init__(self, in_0: ConvexHull2D ) -> None:
        """
        Cython signature: void ConvexHull2D(ConvexHull2D &)
        """
        ...
    
    def clear(self) -> None:
        """
        Cython signature: void clear()
        Removes all points
        """
        ...
    
    def compress(self) -> int:
        """
        Cython signature: size_t compress()
        Allows to reduce the disk/memory footprint of a hull
        """
        ...
    
    def expandToBoundingBox(self) -> None:
        """
        Cython signature: void expandToBoundingBox()
        Expand a convex hull to its bounding box.
        """
        ...
    
    def addPoint(self, point: Union[Sequence[int], Sequence[float]] ) -> bool:
        """
        Cython signature: bool addPoint(DPosition2 point)
        Adds a point to the hull if it is not already contained. Returns if the point was added. This will trigger recomputation of the outer hull points (thus points set with setHullPoints() will be lost)
        """
        ...
    
    def addPoints(self, points: '_np.ndarray[Any, _np.dtype[_np.float32]]' ) -> None:
        """
        Cython signature: void addPoints(libcpp_vector[DPosition2] points)
        Adds points to the hull if it is not already contained. This will trigger recomputation of the outer hull points (thus points set with setHullPoints() will be lost)
        """
        ...
    
    def encloses(self, in_0: Union[Sequence[int], Sequence[float]] ) -> bool:
        """
        Cython signature: bool encloses(DPosition2)
        Returns if the `point` lies in the feature hull
        """
        ...
    
    def getHullPoints(self) -> '_np.ndarray[Any, _np.dtype[_np.float32]]':
        """
        Cython signature: libcpp_vector[DPosition2] getHullPoints()
        Accessor for the outer points
        """
        ...
    
    def setHullPoints(self, in_0: '_np.ndarray[Any, _np.dtype[_np.float32]]' ) -> None:
        """
        Cython signature: void setHullPoints(libcpp_vector[DPosition2])
        Accessor for the outer(!) points (no checking is performed if this is actually a convex hull)
        """
        ...
    
    def getBoundingBox(self) -> DBoundingBox2:
        """
        Cython signature: DBoundingBox2 getBoundingBox()
        Returns the bounding box of the feature hull points
        """
        ...
    
    def __richcmp__(self, other: ConvexHull2D, op: int) -> Any:
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


class FIAMSDataProcessor:
    """
    Cython implementation of _FIAMSDataProcessor

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1FIAMSDataProcessor.html>`_
      -- Inherits from ['DefaultParamHandler']

      ADD PYTHON DOCUMENTATION HERE
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void FIAMSDataProcessor()
        Data processing for FIA-MS data
        """
        ...
    
    @overload
    def __init__(self, in_0: FIAMSDataProcessor ) -> None:
        """
        Cython signature: void FIAMSDataProcessor(FIAMSDataProcessor &)
        """
        ...
    
    def run(self, experiment: MSExperiment , n_seconds: float , output: MzTab , load_cached_spectrum: bool ) -> bool:
        """
        Cython signature: bool run(MSExperiment & experiment, float & n_seconds, MzTab & output, bool load_cached_spectrum)
        Run the full analysis for the experiment for the given time interval\n
        
        The workflow steps are:
        - the time axis of the experiment is cut to the interval from 0 to n_seconds
        - the spectra are summed into one along the time axis with the bin size determined by mz and instrument resolution
        - data is smoothed by applying the Savitzky-Golay filter
        - peaks are picked
        - the accurate mass search for all the picked peaks is performed
        
        The intermediate summed spectra and picked peaks can be saved to the filesystem.
        Also, the results of the accurate mass search and the signal-to-noise information
        of the resulting spectrum is saved.
        
        
        :param experiment: Input MSExperiment
        :param n_seconds: Input number of seconds
        :param load_cached_spectrum: Load the cached picked spectrum if exists
        :param output: Output of the accurate mass search results
        :return: A boolean indicating if the picked spectrum was loaded from the cached file
        """
        ...
    
    def extractPeaks(self, input_: MSSpectrum ) -> MSSpectrum:
        """
        Cython signature: MSSpectrum extractPeaks(MSSpectrum & input_)
        Pick peaks from the summed spectrum
        
        
        :param input: Input vector of spectra
        :return: A spectrum with picked peaks
        """
        ...
    
    def convertToFeatureMap(self, input_: MSSpectrum ) -> FeatureMap:
        """
        Cython signature: FeatureMap convertToFeatureMap(MSSpectrum & input_)
        Convert a spectrum to a feature map with the corresponding polarity\n
        
        Applies `SavitzkyGolayFilter` and `PeakPickerHiRes`
        
        
        :param input: Input a picked spectrum
        :return: A feature map with the peaks converted to features and polarity from the parameters
        """
        ...
    
    def trackNoise(self, input_: MSSpectrum ) -> MSSpectrum:
        """
        Cython signature: MSSpectrum trackNoise(MSSpectrum & input_)
        Estimate noise for each peak\n
        
        Uses `SignalToNoiseEstimatorMedianRapid`
        
        
        :param input: Input a picked spectrum
        :return: A spectrum object storing logSN information
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


class IsobaricQuantifier:
    """
    Cython implementation of _IsobaricQuantifier

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1IsobaricQuantifier.html>`_
      -- Inherits from ['DefaultParamHandler']
    """
    
    @overload
    def __init__(self, in_0: IsobaricQuantifier ) -> None:
        """
        Cython signature: void IsobaricQuantifier(IsobaricQuantifier &)
        """
        ...
    
    @overload
    def __init__(self, quant_method: ItraqFourPlexQuantitationMethod ) -> None:
        """
        Cython signature: void IsobaricQuantifier(ItraqFourPlexQuantitationMethod * quant_method)
        """
        ...
    
    @overload
    def __init__(self, quant_method: ItraqEightPlexQuantitationMethod ) -> None:
        """
        Cython signature: void IsobaricQuantifier(ItraqEightPlexQuantitationMethod * quant_method)
        """
        ...
    
    @overload
    def __init__(self, quant_method: TMTSixPlexQuantitationMethod ) -> None:
        """
        Cython signature: void IsobaricQuantifier(TMTSixPlexQuantitationMethod * quant_method)
        """
        ...
    
    @overload
    def __init__(self, quant_method: TMTTenPlexQuantitationMethod ) -> None:
        """
        Cython signature: void IsobaricQuantifier(TMTTenPlexQuantitationMethod * quant_method)
        """
        ...
    
    def quantify(self, consensus_map_in: ConsensusMap , consensus_map_out: ConsensusMap ) -> None:
        """
        Cython signature: void quantify(ConsensusMap & consensus_map_in, ConsensusMap & consensus_map_out)
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


class ItraqFourPlexQuantitationMethod:
    """
    Cython implementation of _ItraqFourPlexQuantitationMethod

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1ItraqFourPlexQuantitationMethod.html>`_
      -- Inherits from ['IsobaricQuantitationMethod']
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void ItraqFourPlexQuantitationMethod()
        iTRAQ 4 plex quantitation to be used with the IsobaricQuantitation
        """
        ...
    
    @overload
    def __init__(self, in_0: ItraqFourPlexQuantitationMethod ) -> None:
        """
        Cython signature: void ItraqFourPlexQuantitationMethod(ItraqFourPlexQuantitationMethod &)
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


class MascotXMLFile:
    """
    Cython implementation of _MascotXMLFile

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1MascotXMLFile.html>`_
      -- Inherits from ['XMLFile']
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void MascotXMLFile()
        """
        ...
    
    @overload
    def __init__(self, in_0: MascotXMLFile ) -> None:
        """
        Cython signature: void MascotXMLFile(MascotXMLFile &)
        """
        ...
    
    def load(self, filename: Union[bytes, str, String] , protein_identification: ProteinIdentification , id_data: PeptideIdentificationList , rt_mapping: SpectrumMetaDataLookup ) -> None:
        """
        Cython signature: void load(const String & filename, ProteinIdentification & protein_identification, PeptideIdentificationList & id_data, SpectrumMetaDataLookup & rt_mapping)
        Loads data from a Mascot XML file
        
        
        :param filename: The file to be loaded
        :param protein_identification: Protein identifications belonging to the whole experiment
        :param id_data: The identifications with m/z and RT
        :param lookup: Helper object for looking up spectrum meta data
        :raises:
          Exception: FileNotFound is thrown if the file does not exists
        :raises:
          Exception: ParseError is thrown if the file does not suit to the standard
        """
        ...
    
    def initializeLookup(self, lookup: SpectrumMetaDataLookup , experiment: MSExperiment , scan_regex: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void initializeLookup(SpectrumMetaDataLookup & lookup, MSExperiment & experiment, const String & scan_regex)
        Initializes a helper object for looking up spectrum meta data (RT, m/z)
        
        
        :param lookup: Helper object to initialize
        :param experiment: Experiment containing the spectra
        :param scan_regex: Optional regular expression for extracting information from references to spectra
        """
        ...
    
    def getVersion(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getVersion()
        Return the version of the schema
        """
        ... 


class MetaInfo:
    """
    Cython implementation of _MetaInfo

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1MetaInfo.html>`_

    A Type-Name-Value tuple class
    
    MetaInfo maps an index (an integer corresponding to a string) to
    DataValue objects.  The mapping of strings to the index is performed by
    the MetaInfoRegistry, which can be accessed by the method registry()
    
    There are two versions of nearly all members. One which operates with a
    string name and another one which operates on an index. The index version
    is always faster, as it does not need to look up the index corresponding
    to the string in the MetaInfoRegistry
    
    If you wish to add a MetaInfo member to a class, consider deriving that
    class from MetaInfoInterface, instead of simply adding MetaInfo as
    member. MetaInfoInterface implements a full interface to a MetaInfo
    member and is more memory efficient if no meta info gets added
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void MetaInfo()
        """
        ...
    
    @overload
    def __init__(self, in_0: MetaInfo ) -> None:
        """
        Cython signature: void MetaInfo(MetaInfo &)
        """
        ...
    
    @overload
    def getValue(self, name: Union[bytes, str, String] ) -> Union[int, float, bytes, str, List[int], List[float], List[bytes]]:
        """
        Cython signature: DataValue getValue(String name)
        Returns the value corresponding to a string
        """
        ...
    
    @overload
    def getValue(self, index: int ) -> Union[int, float, bytes, str, List[int], List[float], List[bytes]]:
        """
        Cython signature: DataValue getValue(unsigned int index)
        Returns the value corresponding to an index
        """
        ...
    
    @overload
    def getValue(self, name: Union[bytes, str, String] , default_value: Union[int, float, bytes, str, List[int], List[float], List[bytes]] ) -> Union[int, float, bytes, str, List[int], List[float], List[bytes]]:
        """
        Cython signature: DataValue getValue(String name, DataValue default_value)
        Returns the value corresponding to a string
        """
        ...
    
    @overload
    def getValue(self, index: int , default_value: Union[int, float, bytes, str, List[int], List[float], List[bytes]] ) -> Union[int, float, bytes, str, List[int], List[float], List[bytes]]:
        """
        Cython signature: DataValue getValue(unsigned int index, DataValue default_value)
        Returns the value corresponding to an index
        """
        ...
    
    @overload
    def exists(self, name: Union[bytes, str, String] ) -> bool:
        """
        Cython signature: bool exists(String name)
        Returns if this MetaInfo is set
        """
        ...
    
    @overload
    def exists(self, index: int ) -> bool:
        """
        Cython signature: bool exists(unsigned int index)
        Returns if this MetaInfo is set
        """
        ...
    
    @overload
    def setValue(self, name: Union[bytes, str, String] , value: Union[int, float, bytes, str, List[int], List[float], List[bytes]] ) -> None:
        """
        Cython signature: void setValue(String name, DataValue value)
        Sets the DataValue corresponding to a name
        """
        ...
    
    @overload
    def setValue(self, index: int , value: Union[int, float, bytes, str, List[int], List[float], List[bytes]] ) -> None:
        """
        Cython signature: void setValue(unsigned int index, DataValue value)
        Sets the DataValue corresponding to an index
        """
        ...
    
    @overload
    def removeValue(self, name: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void removeValue(String name)
        Removes the DataValue corresponding to `name` if it exists
        """
        ...
    
    @overload
    def removeValue(self, index: int ) -> None:
        """
        Cython signature: void removeValue(unsigned int index)
        Removes the DataValue corresponding to `index` if it exists
        """
        ...
    
    def getKeys(self, keys: List[bytes] ) -> None:
        """
        Cython signature: void getKeys(libcpp_vector[String] & keys)
        Fills the given vector with a list of all keys for which a value is set
        """
        ...
    
    def getKeysAsIntegers(self, keys: List[int] ) -> None:
        """
        Cython signature: void getKeysAsIntegers(libcpp_vector[unsigned int] & keys)
        """
        ...
    
    def empty(self) -> bool:
        """
        Cython signature: bool empty()
        Returns if the MetaInfo is empty
        """
        ...
    
    def clear(self) -> None:
        """
        Cython signature: void clear()
        Removes all meta values
        """
        ...
    
    def registry(self) -> MetaInfoRegistry:
        """
        Cython signature: MetaInfoRegistry registry()
        """
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


class MzTab:
    """
    Cython implementation of _MzTab

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1MzTab.html>`_

    Data model of MzTab files
    
    Please see the official MzTab specification at https://code.google.com/p/mztab/
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void MzTab()
        """
        ...
    
    @overload
    def __init__(self, in_0: MzTab ) -> None:
        """
        Cython signature: void MzTab(MzTab &)
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


class PeakPickerIterative:
    """
    Cython implementation of _PeakPickerIterative

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1PeakPickerIterative.html>`_
      -- Inherits from ['DefaultParamHandler', 'ProgressLogger']
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void PeakPickerIterative()
        """
        ...
    
    @overload
    def __init__(self, in_0: PeakPickerIterative ) -> None:
        """
        Cython signature: void PeakPickerIterative(PeakPickerIterative &)
        """
        ...
    
    def pick(self, input: MSSpectrum , output: MSSpectrum ) -> None:
        """
        Cython signature: void pick(MSSpectrum & input, MSSpectrum & output)
        This will pick one single spectrum. The PeakPickerHiRes is used to
        generate seeds, these seeds are then used to re-center the mass and
        compute peak width and integrated intensity of the peak
        
        Finally, other peaks that would fall within the primary peak are
        discarded
        
        The output are the remaining peaks
        """
        ...
    
    def pickExperiment(self, input: MSExperiment , output: MSExperiment ) -> None:
        """
        Cython signature: void pickExperiment(MSExperiment & input, MSExperiment & output)
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


class RangeIntensity:
    """
    Cython implementation of _RangeIntensity

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1RangeIntensity.html>`_
      -- Inherits from ['RangeBase']
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void RangeIntensity()
        """
        ...
    
    @overload
    def __init__(self, in_0: RangeIntensity ) -> None:
        """
        Cython signature: void RangeIntensity(RangeIntensity &)
        """
        ...
    
    def setMinIntensity(self, min: float ) -> None:
        """
        Cython signature: void setMinIntensity(double min)
        """
        ...
    
    def setMaxIntensity(self, max: float ) -> None:
        """
        Cython signature: void setMaxIntensity(double max)
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
    
    def extendIntensity(self, value: float ) -> None:
        """
        Cython signature: void extendIntensity(double value)
        Extend the range such that it includes the given @p value
        """
        ...
    
    def containsIntensity(self, value: float ) -> bool:
        """
        Cython signature: bool containsIntensity(double value)
        Is value within [min, max]?
        """
        ...
    
    def setMin(self, min: float ) -> None:
        """
        Cython signature: void setMin(double min)
        """
        ...
    
    def setMax(self, max: float ) -> None:
        """
        Cython signature: void setMax(double max)
        """
        ...
    
    def getMin(self) -> float:
        """
        Cython signature: double getMin()
        """
        ...
    
    def getMax(self) -> float:
        """
        Cython signature: double getMax()
        """
        ...
    
    def extend(self, value: float ) -> None:
        """
        Cython signature: void extend(double value)
        Extend the range such that it includes the given @p value
        """
        ...
    
    def contains(self, value: float ) -> bool:
        """
        Cython signature: bool contains(double value)
        Is value within [min, max]?
        """
        ... 


class RangeMZ:
    """
    Cython implementation of _RangeMZ

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1RangeMZ.html>`_
      -- Inherits from ['RangeBase']
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void RangeMZ()
        """
        ...
    
    @overload
    def __init__(self, in_0: RangeMZ ) -> None:
        """
        Cython signature: void RangeMZ(RangeMZ &)
        """
        ...
    
    def setMinMZ(self, min: float ) -> None:
        """
        Cython signature: void setMinMZ(double min)
        """
        ...
    
    def setMaxMZ(self, max: float ) -> None:
        """
        Cython signature: void setMaxMZ(double max)
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
    
    def extendMZ(self, value: float ) -> None:
        """
        Cython signature: void extendMZ(double value)
        Extend the range such that it includes the given @p value
        """
        ...
    
    def containsMZ(self, value: float ) -> bool:
        """
        Cython signature: bool containsMZ(double value)
        Is value within [min, max]?
        """
        ...
    
    def setMin(self, min: float ) -> None:
        """
        Cython signature: void setMin(double min)
        """
        ...
    
    def setMax(self, max: float ) -> None:
        """
        Cython signature: void setMax(double max)
        """
        ...
    
    def getMin(self) -> float:
        """
        Cython signature: double getMin()
        """
        ...
    
    def getMax(self) -> float:
        """
        Cython signature: double getMax()
        """
        ...
    
    def extend(self, value: float ) -> None:
        """
        Cython signature: void extend(double value)
        Extend the range such that it includes the given @p value
        """
        ...
    
    def contains(self, value: float ) -> bool:
        """
        Cython signature: bool contains(double value)
        Is value within [min, max]?
        """
        ... 


class RangeMobility:
    """
    Cython implementation of _RangeMobility

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1RangeMobility.html>`_
      -- Inherits from ['RangeBase']
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void RangeMobility()
        """
        ...
    
    @overload
    def __init__(self, in_0: RangeMobility ) -> None:
        """
        Cython signature: void RangeMobility(RangeMobility &)
        """
        ...
    
    def setMinMobility(self, min: float ) -> None:
        """
        Cython signature: void setMinMobility(double min)
        """
        ...
    
    def setMaxMobility(self, max: float ) -> None:
        """
        Cython signature: void setMaxMobility(double max)
        """
        ...
    
    def getMinMobility(self) -> float:
        """
        Cython signature: double getMinMobility()
        Returns the minimum Mobility
        """
        ...
    
    def getMaxMobility(self) -> float:
        """
        Cython signature: double getMaxMobility()
        Returns the maximum Mobility
        """
        ...
    
    def extendMobility(self, value: float ) -> None:
        """
        Cython signature: void extendMobility(double value)
        Extend the range such that it includes the given @p value
        """
        ...
    
    def containsMobility(self, value: float ) -> bool:
        """
        Cython signature: bool containsMobility(double value)
        Is value within [min, max]?
        """
        ...
    
    def setMin(self, min: float ) -> None:
        """
        Cython signature: void setMin(double min)
        """
        ...
    
    def setMax(self, max: float ) -> None:
        """
        Cython signature: void setMax(double max)
        """
        ...
    
    def getMin(self) -> float:
        """
        Cython signature: double getMin()
        """
        ...
    
    def getMax(self) -> float:
        """
        Cython signature: double getMax()
        """
        ...
    
    def extend(self, value: float ) -> None:
        """
        Cython signature: void extend(double value)
        Extend the range such that it includes the given @p value
        """
        ...
    
    def contains(self, value: float ) -> bool:
        """
        Cython signature: bool contains(double value)
        Is value within [min, max]?
        """
        ... 


class RangeRT:
    """
    Cython implementation of _RangeRT

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1RangeRT.html>`_
      -- Inherits from ['RangeBase']
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void RangeRT()
        """
        ...
    
    @overload
    def __init__(self, in_0: RangeRT ) -> None:
        """
        Cython signature: void RangeRT(RangeRT &)
        """
        ...
    
    def setMinRT(self, min: float ) -> None:
        """
        Cython signature: void setMinRT(double min)
        """
        ...
    
    def setMaxRT(self, max: float ) -> None:
        """
        Cython signature: void setMaxRT(double max)
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
    
    def extendRT(self, value: float ) -> None:
        """
        Cython signature: void extendRT(double value)
        Extend the range such that it includes the given @p value
        """
        ...
    
    def containsRT(self, value: float ) -> bool:
        """
        Cython signature: bool containsRT(double value)
        Is value within [min, max]?
        """
        ...
    
    def setMin(self, min: float ) -> None:
        """
        Cython signature: void setMin(double min)
        """
        ...
    
    def setMax(self, max: float ) -> None:
        """
        Cython signature: void setMax(double max)
        """
        ...
    
    def getMin(self) -> float:
        """
        Cython signature: double getMin()
        """
        ...
    
    def getMax(self) -> float:
        """
        Cython signature: double getMax()
        """
        ...
    
    def extend(self, value: float ) -> None:
        """
        Cython signature: void extend(double value)
        Extend the range such that it includes the given @p value
        """
        ...
    
    def contains(self, value: float ) -> bool:
        """
        Cython signature: bool contains(double value)
        Is value within [min, max]?
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


class SourceFile:
    """
    Cython implementation of _SourceFile

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1SourceFile.html>`_
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void SourceFile()
        Description of a file location, used to store the origin of (meta) data
        """
        ...
    
    @overload
    def __init__(self, in_0: SourceFile ) -> None:
        """
        Cython signature: void SourceFile(SourceFile &)
        """
        ...
    
    def getNameOfFile(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getNameOfFile()
        Returns the file name
        """
        ...
    
    def setNameOfFile(self, in_0: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setNameOfFile(String)
        Sets the file name
        """
        ...
    
    def getPathToFile(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getPathToFile()
        Returns the file path
        """
        ...
    
    def setPathToFile(self, in_0: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setPathToFile(String)
        Sets the file path
        """
        ...
    
    def getFileSize(self) -> float:
        """
        Cython signature: float getFileSize()
        Returns the file size in MB
        """
        ...
    
    def setFileSize(self, in_0: float ) -> None:
        """
        Cython signature: void setFileSize(float)
        Sets the file size in MB
        """
        ...
    
    def getFileType(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getFileType()
        Returns the file type
        """
        ...
    
    def setFileType(self, in_0: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setFileType(String)
        Sets the file type
        """
        ...
    
    def getChecksum(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getChecksum()
        Returns the file's checksum
        """
        ...
    
    def setChecksum(self, in_0: Union[bytes, str, String] , in_1: int ) -> None:
        """
        Cython signature: void setChecksum(String, ChecksumType)
        Sets the file's checksum
        """
        ...
    
    def getChecksumType(self) -> int:
        """
        Cython signature: ChecksumType getChecksumType()
        Returns the checksum type
        """
        ...
    
    def getNativeIDType(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getNativeIDType()
        Returns the native ID type of the spectra
        """
        ...
    
    def setNativeIDType(self, in_0: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setNativeIDType(String)
        Sets the native ID type of the spectra
        """
        ...
    
    def getNativeIDTypeAccession(self) -> Union[bytes, str, String]:
        """
        Cython signature: String getNativeIDTypeAccession()
        Returns the nativeID of the spectra
        """
        ...
    
    def setNativeIDTypeAccession(self, accesssion: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void setNativeIDTypeAccession(const String & accesssion)
        Sets the native ID of the spectra
        """
        ...
    
    @staticmethod
    def getAllNamesOfChecksumType() -> List[bytes]:
        """
        Cython signature: libcpp_vector[String] getAllNamesOfChecksumType()
        Returns all checksum type names known to OpenMS
        """
        ... 


class SpectrumAccessOpenMS:
    """
    Cython implementation of _SpectrumAccessOpenMS

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS_1_1SpectrumAccessOpenMS.html>`_
      -- Inherits from ['ISpectrumAccess']

    An implementation of the OpenSWATH Spectrum Access interface using OpenMS
    """
    
    @overload
    def __init__(self, ) -> None:
        """
        Cython signature: void SpectrumAccessOpenMS()
        """
        ...
    
    @overload
    def __init__(self, in_0: SpectrumAccessOpenMS ) -> None:
        """
        Cython signature: void SpectrumAccessOpenMS(SpectrumAccessOpenMS &)
        """
        ...
    
    @overload
    def __init__(self, ms_experiment: MSExperiment ) -> None:
        """
        Cython signature: void SpectrumAccessOpenMS(shared_ptr[MSExperiment] & ms_experiment)
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


class XMLHandler:
    """
    Cython implementation of _XMLHandler

    Original C++ documentation is available `here <http://www.openms.de/current_doxygen/html/classOpenMS::Internal_1_1XMLHandler.html>`_
    """
    
    def __init__(self, filename: Union[bytes, str, String] , version: Union[bytes, str, String] ) -> None:
        """
        Cython signature: void XMLHandler(const String & filename, const String & version)
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
    ActionMode : __ActionMode 


class __ActionMode:
    None
    LOAD : int
    STORE : int

    def getMapping(self) -> Dict[int, str]:
       ... 


class ChecksumType:
    None
    UNKNOWN_CHECKSUM : int
    SHA1 : int
    MD5 : int
    SIZE_OF_CHECKSUMTYPE : int

    def getMapping(self) -> Dict[int, str]:
       ... 


class __PeakMassType:
    None
    MONOISOTOPIC : int
    AVERAGE : int
    SIZE_OF_PEAKMASSTYPE : int

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

