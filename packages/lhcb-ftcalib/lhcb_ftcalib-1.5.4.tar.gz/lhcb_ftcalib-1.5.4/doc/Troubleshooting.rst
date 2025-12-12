Troubleshooting
---------------

**Problem**: The minimization does not converge
...............................................

**Solution(s)**:
    1. Do you have enough data for the minimization?
        * Check the number of tagged events of a tagger, either in the raw
          tagger statistics table or by ``mytagger.stats.Nt``. Only those events
          actually define the likelihood.
    2. Did you choose the identity link?
        * For underflowing mistags the mistag (i.e. identity) link can be problematic. 
          Try choosing ``ft.link.logit`` instead.
    3. The content of the provided B meson id is crucial, check whether this branch was correctly given and filled.
    4. If you use the command line tool ``ftcalib`` run it with the ``-i`` flag to see what tagger branches are actually being read.


**Problem**: The calibration result is significantly different to the EspressoPerformanceMonitor.
.................................................................................................

**Solution(s)**:
    0. Read chapter "Comparing calibration results to the EPM".
    1. Is the calibration mode set correctly?
    2. Did you use the right decay time unit?

        * The API expects ps by default, the command line tool expects ns
          (since the latter is an LHCb convention)
    3. Do you use higher order calibrations, like 3rd degree polynomials or more?

       * The GLM calibration function is constructed in such a way that higher
         order powers of the mistag contribute less and less if the data does
         not need to be described by these powers. The sensitivity for a
         parameter like :math:`p_4` may therefore be extremely limited. Even
         though the calibration result may be a bit different for higher order
         parameters, the calibration curve should be as good as the EPM one.
         Compare tagging powers instead: If those are close it should not truly
         matter which calibration is used.
