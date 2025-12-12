GLM Calibration Functions
=========================
This chapter is intended for those who would like to understand why Flavour
Tagging calibration functions are defined as they are, i.e., common questions
like,

* Why is the average mistag always being subtracted from the mistag, :math:`\eta-\langle\eta\rangle`?
* Why are :math:`p_0` and :math:`p_1` close to zero in ftcalib for the linear calibration, even though the function is almost the identity function?
* Why is :math:`\omega(\eta)=p_0+p_1(\eta-\langle\eta\rangle)+p_2(\eta-\langle\eta\rangle)^2` not the optimal second degree calibration model?
* How do I write the formula of my higher-order calibration function in my thesis?

Introduction
------------

The aim of FT calibrations is simple: Given a dataset of mistags :math:`\eta_i\in[0,\frac{1}{2}]` we want to fit a model :math:`\omega(\eta, p_0, p_1, \cdots)=\omega(\eta, \vec{p})` which maximizes the Flavour Tagging likelihood for some optimal parameters :math:`\vec{p}`

.. math::
    \displaystyle \mathcal{L}(\vec{p})=\prod_{i=1}^N \delta_{f,-d}\omega(\eta_i,\vec{p}) + \delta_{f,d} (1-\omega(\eta_i,\vec{p})),

where :math:`f` is the production flavour hypothesis and :math:`d` is the tagging decision. 
Here, really, any capable function :math:`\omega` would do, but we will look in the following at the polynomial calibrations, expressed in powers of the mistag, as this is the most straightforward and common calibration type.

The simplest choice for a polynomial calibration function is the one given in the monomial basis :math:`\{1,\eta,\eta^2,\ldots,\eta^m\}`

.. math::
   :label: monomialmodel

   \omega(\eta)=\sum_j^m p_j\eta^j,

and while it could describe our data accurately, the parameters :math:`p_j` will be highly correlated in general. For a generalized linear model (GLM), of which Eq. :eq:`monomialmodel` is an example, the covariance matrix of the calibration parameters is proportional to

.. math::
    \mathrm{Cov}(\vec{p}\vert X)\propto(X^\top X)^{-1}

with :math:`X` being the chosen design matrix of the form

.. math::
    X = \begin{bmatrix}
        1& \eta_1& \eta_1^2& \cdots\\
        1& \eta_2& \eta_2^2& \cdots\\
        1& \eta_3& \eta_3^2& \cdots\\
        \vdots & \vdots & \vdots & \ddots
    \end{bmatrix}\in \mathbb{R}^{N\times m}

(in the monimial basis) for :math:`N` data points and :math:`m` calibration parameters.
This gives us 

.. math::
    :label: monomial_moments

    X^\top X=
    \begin{bmatrix}
    N & \sum_i \eta_i & \sum_i \eta_i^2 & \cdots\\
    \sum_i \eta_i & \sum_i \eta_i^2 & \sum_i\eta_i^3 & \cdots\\
    \sum_i \eta_i^2 & \sum_i \eta_i^3 & \sum_i \eta_i^4 & \cdots\\
    \vdots &  \vdots &  \vdots & \ddots
    \end{bmatrix}\in \mathbb{R}^{m\times m}

for the monomial basis.
Observe that the off-diagonal elements in general are large, which will persist after inversion. 
Thus, correlations will in general be arbitrarily large between any two calibration parameters, depending on the data.
In the following subsections, we will derive a more suitable basis for polynomial calibrations in which the calibration parameters are uncorrelated.

Linear calibrations
-------------------

In the linear case where the calibration function is :math:`\omega(\eta)=p_0+p_1\eta`, we estimate the covariance matrix as before 

.. math::
    \mathrm{Cov}(\vec{p})  \propto (X^\top X)^{-1}
    =\begin{bmatrix}
        N & \sum_i\eta_i \\ \sum_i\eta_i & \sum_i\eta_i^2
    \end{bmatrix}^{-1} 
    =\frac{1}{N\sum_i\eta_i^2-(\sum_i\eta_i)^2}\begin{bmatrix}
        \sum_i\eta_i^2 & -\sum_i\eta_i \\ -\sum_i\eta_i & N
    \end{bmatrix}

and we see that the correlation (and the covariance) between :math:`p_0` and :math:`p_1` is proportional to

.. math::
    \mathrm{corr}(p_0, p_1)\propto \frac{\sum_i^N\eta_i}{N\sum_i\eta_i^2-(\sum_i\eta_i)^2}

We want this term to vanish and achieve this by transforming the coordinate :math:`\eta\mapsto\eta - \langle\eta\rangle` such that the sum of mistags is zero on average. Here, :math:`\langle\eta\rangle` is the average (weighted) mistag. We therefore obtain our classic, average-eta-subtracted form of the calibration function

.. math::
    \omega(\eta)=p_0+p_1(\eta-\langle\eta\rangle)

which is often shown in publications and where :math:`p_0` and :math:`p_1` are indeed uncorrelated.

Quadratic calibrations
----------------------
In the quadratic case, if we again naively assume the monomial basis :math:`\{1,\eta,\eta^2,\ldots,\eta^m\}=\{P_0,P_1,P_2,\ldots,P_m\}`, we have 

.. math::
    \mathrm{Cov}(p_0,p_1,p_2)\propto (X^\top X)^{-1}=\begin{pmatrix}
        N & \color{red}\sum_i\eta_i & \color{red}\sum_i\eta_i^2 \\
        \color{red}\sum_i\eta_i & \sum_i\eta_i^2 & \color{red}\sum_i\eta_i^3 \\
        \color{red}\sum_i\eta_i^2 & \color{red}\sum_i\eta_i^3 & \sum_i\eta_i^4 \\
    \end{pmatrix}^{-1}.

We can already see that to find a suitable transformation, i.e., a new basis of some kind, in which :math:`\mathrm{corr}(p_0,p_1)=\mathrm{corr}(p_1,p_2)=\mathrm{corr}(p_0,p_2)=0`, we will need to find an elaborate transformation in which the first, second, and third powers of our transformed coordinates, however they are defined, vanish.
This is a futile task in guessing, and therefore, we take a step back and redefine how we think about our GLM.
In the linear case, we could say that we found that a simple basis transformation :math:`B` of the form

.. math::
    \underbrace{
    \begin{bmatrix}
        1 & 0 \\ -\langle\eta\rangle & 1
    \end{bmatrix}}_{B}
    \begin{bmatrix}
        1 \\ \eta
    \end{bmatrix}=
    \begin{bmatrix}
        1 \\ \eta-\langle\eta\rangle
    \end{bmatrix}=
    \begin{bmatrix}
        \hat{P}_0(\eta) \\ \hat{P}_1(\eta)
    \end{bmatrix}

has given us a calibration function with uncorrelated parameters.
We can therefore reexpress our linear calibration function as 

.. math::
    \omega(\eta)=\sum_{j=0}^1p_j\hat{P}_j(\eta) = p_0 + p_1(\eta - \langle\eta\rangle)

which almost has the form of a GLM as it is defined in the literature, where it is defined as

.. math::
    \omega(\eta)=\eta + \sum_jp_j\hat{P}_j(\eta)

instead. The reason for adding :math:`\eta` to the function will become evident now, as something interesting happens if we do that:

.. math::
    \begin{align}
    \omega(\eta) &= \eta + p_0 + p_1(\eta - \langle\eta\rangle) \nonumber \\
                 &= \eta + p_0 + p_1(\eta - \langle\eta\rangle) + \langle\eta\rangle - \langle\eta\rangle\nonumber \\
                 &= \underbrace{p_0 + \langle\eta\rangle}_{\tilde{p_0}} + \underbrace{(1 + p_1)}_{\tilde{p_1}}(\eta - \langle\eta\rangle).\nonumber
    \end{align}

By adding an offset of :math:`\eta`, we therefore obtain effectively the same linear function, defined effectively by two parameters :math:`\tilde{p_0}` and :math:`\tilde{p_1}` that are still uncorrelated for the reason given above, but now, 
the meaning of :math:`p_0` and :math:`p_1` has changed, since now the identity is obtained if :math:`p_0=p_1=0`. This is the convention used by ftcalib, and it is arguably the best.
It is easy to convince oneself that this holds for calibrations of arbitrary polynomial order and thus :math:`p_i=0` corresponds to the identity calibration :math:`\omega(\eta)=\eta`.

To continue now with the quadratic case, we again need to find a matrix :math:`B` to transform the monomial basis into a basis of new polynomials :math:`\hat{P}_i(\eta)`:

.. math::
    \begin{bmatrix}
        a & 0 & 0 \\ b & c & 0 \\ d & e & f
    \end{bmatrix}
    \begin{bmatrix}
        1 \\ \eta \\ \eta^2
    \end{bmatrix}=
    \begin{bmatrix}
        \hat{P}_0(\eta) \\ \hat{P}_1(\eta) \\ \hat{P}_2(\eta)
    \end{bmatrix}

such that the covariance matrix, in analogy to :eq:`monomial_moments`

.. math::
    \mathrm{Cov}(p_0,p_1,p_2)\propto (X^\top X)^{-1}=\begin{pmatrix}
        \langle \hat{P}_0,\hat{P}_0\rangle & \langle \hat{P}_0,\hat{P}_1\rangle & \langle \hat{P}_0,\hat{P}_2\rangle \\
        \langle \hat{P}_1,\hat{P}_0\rangle & \langle \hat{P}_1,\hat{P}_1\rangle & \langle \hat{P}_1,\hat{P}_2\rangle \\
        \langle \hat{P}_2,\hat{P}_0\rangle & \langle \hat{P}_2,\hat{P}_1\rangle & \langle \hat{P}_2,\hat{P}_2\rangle \\
    \end{pmatrix}^{-1}

is diagonal. This is equivalent to finding a basis in which all calibration parameters are uncorrelated.
If we consider the fact that :math:`X^\top X` always has a non-vanishing diagonal, its inverse can only be diagonal if :math:`X^\top X` is diagonal in the first place.
A suitable polynomial basis is therefore found if :math:`\langle P_i,P_j\rangle=0` for :math:`i\neq j`. The inner product is defined as

.. math::
    \langle P_i,P_j\rangle = \sum_{k=1}^N P_i(\eta_k)P_j(\eta_k)

as before. Unsurprisingly, orthogonalization with Gram-Schmidt is exactly what needs to be done in the following, as what we need to find is an orthogonal set of :math:`\hat{P}_j(\eta)` basis vectors.

As is customary, we start with our non-orthogonal vectors :math:`\{P_0,P_1,P_2\}=\{1,\eta,\eta^2\}` and we set :math:`\hat{P}_0=1`, and successively subtract projections from our basis vectors according to the familiar algorithm

.. math::
    \begin{align}
    \hat{P}_1 &= P_1 - \frac{\langle \hat{P}_0,P_1\rangle}{\langle \hat{P}_0,\hat{P}_0\rangle} \hat{P}_0\nonumber\\
              &= \eta-\frac{\sum_i^N 1\cdot \eta_i}{N}\cdot 1=\eta - \langle\eta\rangle\nonumber \\
    \end{align}

our linear result! we continue

.. math::
    \begin{align}
    \hat{P}_2 &= P_2 - \frac{\langle\hat{P}_0,P_2\rangle}{\langle\hat{P_0},\hat{P_0}\rangle}P_0\nonumber
                     - \frac{\langle\hat{P}_1,P_2\rangle}{\langle\hat{P_1},\hat{P_1}\rangle}P_1\nonumber\\
              &= \eta^2-\frac{\sum_i^N 1\cdot\eta_i^2}{N}\cdot 1-\frac{\sum_i^N(\eta_i-\langle\eta\rangle)\eta_i^2}{\sum_i^N(\eta_i-\langle\eta\rangle)^2}\eta\nonumber \\
              &= \eta^2-\langle\eta^2\rangle-\frac{\langle\eta^3\rangle-\langle\eta\rangle\langle\eta^2\rangle}{\langle\eta^2\rangle-\langle\eta\rangle^2}\eta\nonumber
    \end{align}

Thus, we can write the quadratic calibration function that gives us uncorrelated calibration parameters as

.. math::
    \begin{align}
        \omega(\eta,p_0,p_1,p_2) &= \eta + \sum_{j=0}^2p_j\hat{P}_j(\eta)\nonumber\\
                            &= p_0 + \langle\eta\rangle\nonumber \\
                            &+ (1 + p_1)(\eta-\langle\eta\rangle)\nonumber\\
                            &+ p_2 \left(\eta^2-\frac{\langle\eta^3\rangle-\langle\eta\rangle\langle\eta^2\rangle}{\langle\eta^2\rangle-\langle\eta\rangle^2}\eta-\langle\eta^2\rangle\right)\nonumber
    \end{align}

In ftcalib, this calculation is not performed analytically, but numerically in an almost identical way.
If per-events weights are provided, all sums over mistags need to be understood as weighted sums.

Cubic calibrations
------------------
The cubic component of the calibration model can be derived in the same way as above, but at this point the expression is growing exponentially, which emphasizes the practicability of the numerical 
approach taken in ftcalib. The basis matrix :math:`B` can be otained from ftcalib with

.. code-block:: python

    import ftcalib as ft

    tagger = ft.Tagger("example", eta, dec, ID, "Bu", weight=weights)
    tagger.set_calibration(ft.PolynomialCalibration(npar=4, link=ft.link.identity))
    print(tagger.func.basis)


If we substitute :math:`\alpha=\frac{\langle\eta^3\rangle-\langle\eta\rangle\langle\eta^2\rangle}{\langle\eta^2\rangle-\langle\eta\rangle^2}` from before
then for cubic calibrations, the :math:`\hat{P}_3` polynomial is given by

.. math::
    \begin{align}
    \hat{P}_3 &= P_3 - \frac{\langle\hat{P}_0,P_3\rangle}{\langle\hat{P_0},\hat{P_0}\rangle}P_0
                     - \frac{\langle\hat{P}_1,P_3\rangle}{\langle\hat{P_1},\hat{P_1}\rangle}P_1
                     - \frac{\langle\hat{P}_2,P_3\rangle}{\langle\hat{P_2},\hat{P_2}\rangle}P_2\nonumber\\
              &= \eta^3-\frac{\sum_i^N 1\cdot\eta_i^3}{N}\cdot 1-\frac{\sum_i^N(\eta_i-\langle\eta\rangle)\eta_i^3}{\sum_i^N(\eta_i-\langle\eta\rangle)^2}\eta - \frac{\sum_i^N(\eta_i^2-\alpha \eta_i-\langle\eta^2\rangle)\eta_i^3}{\sum_i^N(\eta_i^2-\alpha \eta_i-\langle\eta^2\rangle)^2}\eta^2 \nonumber \\
              &= \eta^3-\langle\eta^3\rangle - \frac{\langle\eta^4\rangle-\langle\eta\rangle\langle\eta^3\rangle}{\langle\eta^2\rangle-\langle\eta\rangle^2}\eta
               - \frac{\langle\eta^5\rangle-\alpha\langle\eta^4\rangle-\langle\eta^3\rangle\langle\eta^2\rangle}{\langle\eta^2\rangle^2+2\langle\eta^2\rangle\alpha\langle\eta\rangle+(\alpha^2-2\langle\eta^2\rangle^2)-2\alpha\langle\eta^3\rangle+\langle\eta^4\rangle}\eta^2\nonumber
    \end{align}

The expression does not simplify when :math:`\alpha` is substituted back but it is interesting to note that for each order of the calibration function, the :math:`m`-th basis polynomial can be written as :math:`P_m(\eta)=\eta^m-\langle\eta^m\rangle-\mathcal{O}(\eta^{m-1})`, so intuitively, the data is centered around its mean.
