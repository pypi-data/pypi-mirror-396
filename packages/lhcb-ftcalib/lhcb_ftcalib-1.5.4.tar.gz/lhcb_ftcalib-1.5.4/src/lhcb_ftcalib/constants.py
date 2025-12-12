# Oscillation parameters
DeltaM_d     = 0.5069
DeltaGamma_d = 0
DeltaM_s     = 17.765
DeltaGamma_s = 0.083

Lifetime_Bd  = 1.517  # in ps. Used for user warnings
Lifetime_Bs  = 1.516  # in ps. Used for user warnings
LifetimeToleranceFactor = 10  # Warning threshold

# Covariance scaling for weighted fits
CovarianceCorrectionMethod = "SquaredHesse"  # "SumW2", "None"

# Propgate uncertainties of the calibrated mistags through tagger combination
propagate_errors = False

# Calculate uncertainties of the calibrated mistags. May cost some time, so this is optional
calculate_omegaerr = True

# Use averaged representation of the calibration to write calibrated mistag to
# tuples. It is probably not optimal to never account for mistag asymmetries on
# calibration datasets, but this default mimics the EPM behaviour
ignore_mistag_asymmetry_for_apply = True
