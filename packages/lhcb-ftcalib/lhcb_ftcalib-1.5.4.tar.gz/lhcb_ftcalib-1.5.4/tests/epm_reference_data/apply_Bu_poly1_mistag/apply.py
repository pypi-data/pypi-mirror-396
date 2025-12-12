OS_Muon_CalibrationArchive  = "../ExampleCalibration.xml"
datafile  = "../reference.root"
TupleName = "BU_POLY1_MISTAG"
DBGLEVEL  = 5
Nmax      = -1
DoCalibrations = 0

CalibrationMode   = "Bu"
CalibrationLink   = "MISTAG"
CalibrationDegree = 1
CalibrationModel  = "POLY"
UseNewtonRaphson  = 0

OS_Muon_Use        = 1
OS_Muon_Write      = 1
OS_Muon_BranchDec  = "TOY0_DEC"
OS_Muon_BranchProb = "TOY0_ETA"

WriteCalibratedMistagBranches = 1
CalibratedOutputFile = "output.root"
