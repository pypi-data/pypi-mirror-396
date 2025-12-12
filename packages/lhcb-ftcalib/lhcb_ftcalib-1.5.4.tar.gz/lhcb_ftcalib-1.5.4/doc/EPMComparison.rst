Comparing calibration results to the EPM
========================================
``lhcb-ftcalib`` uses mostly the same conventions for the flavour tagging
likelihood and performance numbers and its calibration results will be very
close to those of the EspressoPerformanceMonitor. To get even more similar
results, one needs to set the oscillation parameters to the older values which
the EPM uses:

.. code-block:: python

   import lhcb_ftcalib as ft

   ft.constants.DeltaM_d = 0.51
   ft.constants.DeltaM_s = 17.761
   ft.constants.DeltaGamma_d = 0
   ft.constants.DeltaGamma_s = 0.0913
   ft.constants.ignore_mistag_asymmetry_for_apply = True  # Should be the default anyway
   ft.constants.CovarianceCorrectionMethod = "SquaredHesse" # Should be the default anyway

   # Continue with calibrations...

.. warning::
   The name of a combined branch in ``lhcb-ftcalib`` is always ``XYZ_ETA`` which
   differs w.r.t. the EspressoPerformanceMonitor where a combined branch is named ``XYZ_OMEGA``.
   The reasoning behind this change is that a combined tagging decision normally still needs
   to be calibrated and is therefore usually treated as a raw tagging decision.
  

Remaining differences can be attributed to rounding imprecision as the
EspressoPerformanceMonitor and ftcalib use very different routines to sum and
multiply the provided data and the order in which the arrays are processed
differs.

It is ensured that ``lhcb-ftcalib`` and the EspressoPerformanceMonitor give
very similar results through unit tests where the output of both programs for
the same data compared.

