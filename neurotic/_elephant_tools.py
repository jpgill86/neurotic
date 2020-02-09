# -*- coding: utf-8 -*-
"""
The :mod:`neurotic._elephant_tools` module contains functions and classes
copied from the elephant package, which are included for convenience and to
eliminate dependency on that package. Original code that builds on this work
(e.g., a new kernel) is also contained in this module.

This module and the functions and classes it contains are not intended to be
part of neurotic's public API, so the module name begins with an underscore.
This module may be removed at a future date and replaced with dependence on the
elephant package.

elephant is licensed under BSD-3-Clause:

Copyright (c) 2014-2019, Elephant authors and contributors All rights reserved.

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this
* list of conditions and the following disclaimer. Redistributions in binary
* form must reproduce the above copyright notice, this list of conditions and
* the following disclaimer in the documentation and/or other materials provided
* with the distribution. Neither the names of the copyright holders nor the
* names of the contributors may be used to endorse or promote products derived
* from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

import warnings
import numpy as np
import scipy.signal
import scipy.special
import quantities as pq
from quantities import ms, mV, Hz, Quantity, dimensionless
import neo
from neo import SpikeTrain

import logging
logger = logging.getLogger(__name__)


###############################################################################
# elephant.kernels

def inherit_docstring(fromfunc, sep=""):
    """
    Decorator: Copy the docstring of `fromfunc`

    based on:
    http://stackoverflow.com/questions/13741998/
    is-there-a-way-to-let-classes-inherit-the-documentation-of-their-superclass-with
    """
    def _decorator(func):
        parent_doc = fromfunc.__doc__
        if func.__doc__ is None:
            func.__doc__ = parent_doc
        else:
            func.__doc__ = sep.join([parent_doc, func.__doc__])
        return func
    return _decorator

class Kernel(object):
    """
    This is the base class for commonly used kernels.

    General definition of kernel:
    A function :math:`K(x, y)` is called a kernel function if
    :math:`\\int K(x, y) g(x) g(y)\\ \\textrm{d}x\\ \\textrm{d}y
    \\ \\geq 0\\ \\ \\ \\forall\\ g \\in L_2`

    Currently implemented kernels are:
        - rectangular
        - triangular
        - epanechnikovlike
        - gaussian
        - laplacian
        - exponential (asymmetric)
        - alpha function (asymmetric)

    In neuroscience a popular application of kernels is in performing smoothing
    operations via convolution. In this case, the kernel has the properties of
    a probability density, i.e., it is positive and normalized to one. Popular
    choices are the rectangular or Gaussian kernels.

    Exponential and alpha kernels may also be used to represent the postynaptic
    current / potentials in a linear (current-based) model.

    Parameters
    ----------
    sigma : Quantity scalar
        Standard deviation of the kernel.
    invert: bool, optional
        If true, asymmetric kernels (e.g., exponential
        or alpha kernels) are inverted along the time axis.
        Default: False
    """

    def __init__(self, sigma, invert=False):

        if not (isinstance(sigma, pq.Quantity)):
            raise TypeError("sigma must be a quantity!")

        if sigma.magnitude < 0:
            raise ValueError("sigma cannot be negative!")

        if not isinstance(invert, bool):
            raise ValueError("invert must be bool!")

        self.sigma = sigma
        self.invert = invert

    def __call__(self, t):
        """
        Evaluates the kernel at all points in the array `t`.

        Parameter
        ---------
        t : Quantity 1D
            Interval on which the kernel is evaluated, not necessarily
            a time interval.

        Returns
        -------
            Quantity 1D
            The result of the kernel evaluations.
        """
        if not (isinstance(t, pq.Quantity)):
            raise TypeError("The argument of the kernel callable must be "
                            "of type quantity!")

        if t.dimensionality.simplified != self.sigma.dimensionality.simplified:
            raise TypeError("The dimensionality of sigma and the input array "
                            "to the callable kernel object must be the same. "
                            "Otherwise a normalization to 1 of the kernel "
                            "cannot be performed.")

        self._sigma_scaled = self.sigma.rescale(t.units)
        # A hidden variable _sigma_scaled is introduced here in order to avoid
        # accumulation of floating point errors of sigma upon multiple
        # usages of the __call__ - function for the same Kernel instance.

        return self._evaluate(t)

    def _evaluate(self, t):
        """
        Evaluates the kernel.

        Parameter
        ---------
        t : Quantity 1D
            Interval on which the kernel is evaluated, not necessarily
            a time interval.

        Returns
        -------
            Quantity 1D
            The result of the kernel evaluation.
        """
        raise NotImplementedError("The Kernel class should not be used directly, "
                                  "instead the subclasses for the single kernels.")

    def boundary_enclosing_area_fraction(self, fraction):
        """
        Calculates the boundary :math:`b` so that the integral from
        :math:`-b` to :math:`b` encloses a certain fraction of the
        integral over the complete kernel. By definition the returned value
        of the method boundary_enclosing_area_fraction is hence non-negative,
        even if the whole probability mass of the kernel is concentrated over
        negative support for inverted kernels.

        Parameter
        ---------
        fraction : float
            Fraction of the whole area which has to be enclosed.

        Returns
        -------
            Quantity scalar
            Boundary of the kernel containing area `fraction` under the
            kernel density.
        """
        self._check_fraction(fraction)
        sigma_division = 500            # arbitrary choice
        interval = self.sigma / sigma_division
        self._sigma_scaled = self.sigma
        area = 0
        counter = 0
        while area < fraction:
            area += (self._evaluate((counter + 1) * interval) +
                     self._evaluate(counter * interval)) * interval / 2
            area += (self._evaluate(-1 * (counter + 1) * interval) +
                     self._evaluate(-1 * counter * interval)) * interval / 2
            counter += 1
            if(counter > 250000):
                raise ValueError("fraction was chosen too close to one such "
                                 "that in combination with integral "
                                 "approximation errors the calculation of a "
                                 "boundary was not possible.")
        return counter * interval

    def _check_fraction(self, fraction):
        """
        Checks the input variable of the method boundary_enclosing_area_fraction
        for validity of type and value.

        Parameter
        ---------
        fraction : float or int
            Fraction of the area under the kernel function.
        """
        if not isinstance(fraction, (float, int)):
            raise TypeError("`fraction` must be float or integer!")
        if not 0 <= fraction < 1:
            raise ValueError("`fraction` must be in the interval [0, 1)!")

    def median_index(self, t):
        """
        Estimates the index of the Median of the kernel.
        This parameter is not mandatory for symmetrical kernels but it is
        required when asymmetrical kernels have to be aligned at their median.

        Parameter
        ---------
        t : Quantity 1D
            Interval on which the kernel is evaluated,

        Returns
        -------
            int
            Index of the estimated value of the kernel median.

        Remarks
        -------
        The formula in this method using retrieval of the sampling interval
        from t only works for t with equidistant intervals!
        The formula calculates the Median slightly wrong by the potentially
        ignored probability in the distribution corresponding to lower values
        than the minimum in the array t.
        """
        return np.nonzero(self(t).cumsum() *
                          (t[len(t) - 1] - t[0]) / (len(t) - 1) >= 0.5)[0].min()

    def is_symmetric(self):
        """
        In the case of symmetric kernels, this method is overwritten in the
        class SymmetricKernel, where it returns 'True', hence leaving the
        here returned value 'False' for the asymmetric kernels.
        """
        return False

class SymmetricKernel(Kernel):
    """
    Base class for symmetric kernels.

    Derived from:
    """
    __doc__ += Kernel.__doc__

    def is_symmetric(self):
        return True

class RectangularKernel(SymmetricKernel):
    """
    Class for rectangular kernels

    .. math::
        K(t) = \\left\\{\\begin{array}{ll} \\frac{1}{2 \\tau}, & |t| < \\tau \\\\
        0, & |t| \\geq \\tau \\end{array} \\right.

    with :math:`\\tau = \\sqrt{3} \\sigma` corresponding to the half width
    of the kernel.

    Besides the standard deviation `sigma`, for consistency of interfaces the
    parameter `invert` needed for asymmetric kernels also exists without
    having any effect in the case of symmetric kernels.

    Derived from:
    """
    __doc__ += SymmetricKernel.__doc__

    @property
    def min_cutoff(self):
        min_cutoff = np.sqrt(3.0)
        return min_cutoff

    @inherit_docstring(Kernel._evaluate)
    def _evaluate(self, t):
        return (0.5 / (np.sqrt(3.0) * self._sigma_scaled)) * \
               (np.absolute(t) < np.sqrt(3.0) * self._sigma_scaled)

    @inherit_docstring(Kernel.boundary_enclosing_area_fraction)
    def boundary_enclosing_area_fraction(self, fraction):
        self._check_fraction(fraction)
        return np.sqrt(3.0) * self.sigma * fraction

class TriangularKernel(SymmetricKernel):
    """
    Class for triangular kernels

    .. math::
        K(t) = \\left\\{ \\begin{array}{ll} \\frac{1}{\\tau} (1
        - \\frac{|t|}{\\tau}), & |t| < \\tau \\\\
         0, & |t| \\geq \\tau \\end{array} \\right.

    with :math:`\\tau = \\sqrt{6} \\sigma` corresponding to the half width of
    the kernel.

    Besides the standard deviation `sigma`, for consistency of interfaces the
    parameter `invert` needed for asymmetric kernels also exists without
    having any effect in the case of symmetric kernels.

    Derived from:
    """
    __doc__ += SymmetricKernel.__doc__

    @property
    def min_cutoff(self):
        min_cutoff = np.sqrt(6.0)
        return min_cutoff

    @inherit_docstring(Kernel._evaluate)
    def _evaluate(self, t):
        return (1.0 / (np.sqrt(6.0) * self._sigma_scaled)) * np.maximum(
            0.0,
            (1.0 - (np.absolute(t) /
                    (np.sqrt(6.0) * self._sigma_scaled)).magnitude))

    @inherit_docstring(Kernel.boundary_enclosing_area_fraction)
    def boundary_enclosing_area_fraction(self, fraction):
        self._check_fraction(fraction)
        return np.sqrt(6.0) * self.sigma * (1 - np.sqrt(1 - fraction))

class EpanechnikovLikeKernel(SymmetricKernel):
    """
    Class for epanechnikov-like kernels

    .. math::
        K(t) = \\left\\{\\begin{array}{ll} (3 /(4 d)) (1 - (t / d)^2),
        & |t| < d \\\\
        0, & |t| \\geq d \\end{array} \\right.

    with :math:`d = \\sqrt{5} \\sigma` being the half width of the kernel.

    The Epanechnikov kernel under full consideration of its axioms has a half
    width of :math:`\\sqrt{5}`. Ignoring one axiom also the respective kernel
    with half width = 1 can be called Epanechnikov kernel.
    ( https://de.wikipedia.org/wiki/Epanechnikov-Kern )
    However, arbitrary width of this type of kernel is here preferred to be
    called 'Epanechnikov-like' kernel.

    Besides the standard deviation `sigma`, for consistency of interfaces the
    parameter `invert` needed for asymmetric kernels also exists without
    having any effect in the case of symmetric kernels.

    Derived from:
    """
    __doc__ += SymmetricKernel.__doc__

    @property
    def min_cutoff(self):
        min_cutoff = np.sqrt(5.0)
        return min_cutoff

    @inherit_docstring(Kernel._evaluate)
    def _evaluate(self, t):
        return (3.0 / (4.0 * np.sqrt(5.0) * self._sigma_scaled)) * np.maximum(
            0.0,
            1 - (t / (np.sqrt(5.0) * self._sigma_scaled)).magnitude ** 2)

    @inherit_docstring(Kernel.boundary_enclosing_area_fraction)
    def boundary_enclosing_area_fraction(self, fraction):
        """
        For Epanechnikov-like kernels, integration of its density within
        the boundaries 0 and :math:`b`, and then solving for :math:`b` leads
        to the problem of finding the roots of a polynomial of third order.
        The implemented formulas are based on the solution of this problem
        given in https://en.wikipedia.org/wiki/Cubic_function,
        where the following 3 solutions are given:
            - :math:`u_1 = 1`: Solution on negative side
            - :math:`u_2 = \\frac{-1 + i\\sqrt{3}}{2}`: Solution for larger
              values than zero crossing of the density
            - :math:`u_3 = \\frac{-1 - i\\sqrt{3}}{2}`: Solution for smaller
              values than zero crossing of the density
        The solution :math:`u_3` is the relevant one for the problem at hand,
        since it involves only positive area contributions.
        """
        self._check_fraction(fraction)
        # Python's complex-operator cannot handle quantities, hence the
        # following construction on quantities is necessary:
        Delta_0 = complex(1.0 / (5.0 * self.sigma.magnitude**2), 0) / \
                  self.sigma.units**2
        Delta_1 = complex(2.0 * np.sqrt(5.0) * fraction /
                          (25.0 * self.sigma.magnitude**3), 0) / \
                  self.sigma.units**3
        C = ((Delta_1 + (Delta_1**2.0 - 4.0 * Delta_0**3.0)**(1.0 / 2.0)) /
             2.0)**(1.0 / 3.0)
        u_3 = complex(-1.0 / 2.0, -np.sqrt(3.0) / 2.0)
        b = -5.0 * self.sigma**2 * (u_3 * C + Delta_0 / (u_3 * C))
        return b.real

class GaussianKernel(SymmetricKernel):
    """
    Class for gaussian kernels

    .. math::
        K(t) = (\\frac{1}{\\sigma \\sqrt{2 \\pi}})
        \\exp(-\\frac{t^2}{2 \\sigma^2})

    with :math:`\\sigma` being the standard deviation.

    Besides the standard deviation `sigma`, for consistency of interfaces the
    parameter `invert` needed for asymmetric kernels also exists without
    having any effect in the case of symmetric kernels.

    Derived from:
    """
    __doc__ += SymmetricKernel.__doc__

    @property
    def min_cutoff(self):
        min_cutoff = 3.0
        return min_cutoff

    @inherit_docstring(Kernel._evaluate)
    def _evaluate(self, t):
        return (1.0 / (np.sqrt(2.0 * np.pi) * self._sigma_scaled)) * np.exp(
            -0.5 * (t / self._sigma_scaled).magnitude ** 2)

    @inherit_docstring(Kernel.boundary_enclosing_area_fraction)
    def boundary_enclosing_area_fraction(self, fraction):
        self._check_fraction(fraction)
        return self.sigma * np.sqrt(2.0) * scipy.special.erfinv(fraction)

class LaplacianKernel(SymmetricKernel):
    """
    Class for laplacian kernels

    .. math::
        K(t) = \\frac{1}{2 \\tau} \\exp(-|\\frac{t}{\\tau}|)

    with :math:`\\tau = \\sigma / \\sqrt{2}`.

    Besides the standard deviation `sigma`, for consistency of interfaces the
    parameter `invert` needed for asymmetric kernels also exists without
    having any effect in the case of symmetric kernels.

    Derived from:
    """
    __doc__ += SymmetricKernel.__doc__

    @property
    def min_cutoff(self):
        min_cutoff = 3.0
        return min_cutoff

    @inherit_docstring(Kernel._evaluate)
    def _evaluate(self, t):
        return (1 / (np.sqrt(2.0) * self._sigma_scaled)) * np.exp(
            -(np.absolute(t) * np.sqrt(2.0) / self._sigma_scaled).magnitude)

    @inherit_docstring(Kernel.boundary_enclosing_area_fraction)
    def boundary_enclosing_area_fraction(self, fraction):
        self._check_fraction(fraction)
        return -self.sigma * np.log(1.0 - fraction) / np.sqrt(2.0)

class ExponentialKernel(Kernel):
    """
    Class for exponential kernels

    .. math::
        K(t) = \\left\\{\\begin{array}{ll} (1 / \\tau) \\exp{(-t / \\tau)},
        & t > 0 \\\\
        0, & t \\leq 0 \\end{array} \\right.

    with :math:`\\tau = \\sigma`.

    Derived from:
    """
    __doc__ += Kernel.__doc__

    @property
    def min_cutoff(self):
        min_cutoff = 3.0
        return min_cutoff

    @inherit_docstring(Kernel._evaluate)
    def _evaluate(self, t):
        if not self.invert:
            kernel = (t >= 0) * (1. / self._sigma_scaled.magnitude) *\
                np.exp((-t / self._sigma_scaled).magnitude) / t.units
        elif self.invert:
            kernel = (t <= 0) * (1. / self._sigma_scaled.magnitude) *\
                np.exp((t / self._sigma_scaled).magnitude) / t.units
        return kernel

    @inherit_docstring(Kernel.boundary_enclosing_area_fraction)
    def boundary_enclosing_area_fraction(self, fraction):
        self._check_fraction(fraction)
        return -self.sigma * np.log(1.0 - fraction)

class AlphaKernel(Kernel):
    """
    Class for alpha kernels

    .. math::
        K(t) = \\left\\{\\begin{array}{ll} (1 / \\tau^2)
        \\ t\\ \\exp{(-t / \\tau)}, & t > 0 \\\\
        0, & t \\leq 0 \\end{array} \\right.

    with :math:`\\tau = \\sigma / \\sqrt{2}`.

    For the alpha kernel an analytical expression for the boundary of the
    integral as a function of the area under the alpha kernel function
    cannot be given. Hence in this case the value of the boundary is
    determined by kernel-approximating numerical integration, inherited
    from the Kernel class.

    Derived from:
    """
    __doc__ += Kernel.__doc__

    @property
    def min_cutoff(self):
        min_cutoff = 3.0
        return min_cutoff

    @inherit_docstring(Kernel._evaluate)
    def _evaluate(self, t):
        if not self.invert:
            kernel = (t >= 0) * 2. * (t / self._sigma_scaled**2).magnitude *\
                np.exp((
                    -t * np.sqrt(2.) / self._sigma_scaled).magnitude) / t.units
        elif self.invert:
            kernel = (t <= 0) * -2. * (t / self._sigma_scaled**2).magnitude *\
                np.exp((
                    t * np.sqrt(2.) / self._sigma_scaled).magnitude) / t.units
        return kernel

###############################################################################
# kernels unique to neurotic

class CausalAlphaKernel(AlphaKernel):
    """
    This modified version of :class:`elephant.kernels.AlphaKernel` shifts time
    such that convolution of the kernel with spike trains (as in
    :func:`elephant.statistics.instantaneous_rate`) results in alpha functions
    that begin rising at the spike time, not before. The entire area of the
    kernel comes after the spike, rather than half before and half after, as in
    :class:`AlphaKernel <elephant.kernels.AlphaKernel>`. Consequently,
    CausalAlphaKernel can be used in causal filters.

    Derived from:
    """
    __doc__ += AlphaKernel.__doc__

    def median_index(self, t):
        """
        In CausalAlphaKernel, "median_index" is a misnomer. Instead of
        returning the index into t that gives half area above and half below
        (median), it returns the index for the first non-negative time, which
        always corresponds to the start of the rise phase of the alpha
        function. This hack ensures that, when the kernel is convolved with a
        spike train, the entire alpha function is located to the right of each
        spike time.

        Overrides the following:
        """
        return np.nonzero(t >= 0)[0].min()
    median_index.__doc__ += AlphaKernel.median_index.__doc__

###############################################################################
# elephant.signal_processing

def butter(signal, highpass_freq=None, lowpass_freq=None, order=4,
           filter_function='filtfilt', fs=1.0, axis=-1):
    """
    Butterworth filtering function for neo.AnalogSignal. Filter type is
    determined according to how values of `highpass_freq` and `lowpass_freq`
    are given (see Parameters section for details).

    Parameters
    ----------
    signal : AnalogSignal or Quantity array or NumPy ndarray
        Time series data to be filtered. When given as Quantity array or NumPy
        ndarray, the sampling frequency should be given through the keyword
        argument `fs`.
    highpass_freq, lowpass_freq : Quantity or float
        High-pass and low-pass cut-off frequencies, respectively. When given as
        float, the given value is taken as frequency in Hz.
        Filter type is determined depending on values of these arguments:
            * highpass_freq only (lowpass_freq = None):    highpass filter
            * lowpass_freq only (highpass_freq = None):    lowpass filter
            * highpass_freq < lowpass_freq:    bandpass filter
            * highpass_freq > lowpass_freq:    bandstop filter
    order : int
        Order of Butterworth filter. Default is 4.
    filter_function : string
        Filtering function to be used. Available filters:
            * 'filtfilt': `scipy.signal.filtfilt()`;
            * 'lfilter': `scipy.signal.lfilter()`;
            * 'sosfiltfilt': `scipy.signal.sosfiltfilt()`.
        In most applications 'filtfilt' should be used, because it doesn't
        bring about phase shift due to filtering. For numerically stable
        filtering, in particular higher order filters, use 'sosfiltfilt'
        (see issue
        https://github.com/NeuralEnsemble/elephant/issues/220).
        Default is 'filtfilt'.
    fs : Quantity or float
        The sampling frequency of the input time series. When given as float,
        its value is taken as frequency in Hz. When the input is given as neo
        AnalogSignal, its attribute is used to specify the sampling
        frequency and this parameter is ignored. Default is 1.0.
    axis : int
        Axis along which filter is applied. Default is -1.

    Returns
    -------
    filtered_signal : AnalogSignal or Quantity array or NumPy ndarray
        Filtered input data. The shape and type is identical to those of the
        input.

    Raises
    ------
    ValueError
        If `filter_function` is not one of 'lfilter', 'filtfilt',
        or 'sosfiltfilt'.
        When both `highpass_freq` and `lowpass_freq` are None.

    """
    available_filters = 'lfilter', 'filtfilt', 'sosfiltfilt'
    if filter_function not in available_filters:
        raise ValueError("Invalid `filter_function`: {filter_function}. "
                         "Available filters: {available_filters}".format(
                          filter_function=filter_function,
                          available_filters=available_filters))
    # design filter
    if hasattr(signal, 'sampling_rate'):
        fs = signal.sampling_rate.rescale(pq.Hz).magnitude
    if isinstance(highpass_freq, pq.quantity.Quantity):
        highpass_freq = highpass_freq.rescale(pq.Hz).magnitude
    if isinstance(lowpass_freq, pq.quantity.Quantity):
        lowpass_freq = lowpass_freq.rescale(pq.Hz).magnitude
    Fn = fs / 2.
    # filter type is determined according to the values of cut-off
    # frequencies
    if lowpass_freq and highpass_freq:
        if highpass_freq < lowpass_freq:
            Wn = (highpass_freq / Fn, lowpass_freq / Fn)
            btype = 'bandpass'
        else:
            Wn = (lowpass_freq / Fn, highpass_freq / Fn)
            btype = 'bandstop'
    elif lowpass_freq:
        Wn = lowpass_freq / Fn
        btype = 'lowpass'
    elif highpass_freq:
        Wn = highpass_freq / Fn
        btype = 'highpass'
    else:
        raise ValueError(
            "Either highpass_freq or lowpass_freq must be given"
        )
    if filter_function == 'sosfiltfilt':
        output = 'sos'
    else:
        output = 'ba'
    designed_filter = scipy.signal.butter(order, Wn, btype=btype,
                                          output=output)

    # When the input is AnalogSignal, the axis for time index (i.e. the
    # first axis) needs to be rolled to the last
    data = np.asarray(signal)
    if isinstance(signal, neo.AnalogSignal):
        data = np.rollaxis(data, 0, len(data.shape))

    # apply filter
    if filter_function == 'lfilter':
        b, a = designed_filter
        filtered_data = scipy.signal.lfilter(b=b, a=a, x=data, axis=axis)
    elif filter_function == 'filtfilt':
        b, a = designed_filter
        filtered_data = scipy.signal.filtfilt(b=b, a=a, x=data, axis=axis)
    else:
        filtered_data = scipy.signal.sosfiltfilt(sos=designed_filter,
                                                 x=data, axis=axis)

    if isinstance(signal, neo.AnalogSignal):
        filtered_data = np.rollaxis(filtered_data, -1, 0)
        return signal.duplicate_with_new_data(filtered_data)
    elif isinstance(signal, pq.quantity.Quantity):
        return filtered_data * signal.units
    else:
        return filtered_data

def rauc(signal, baseline=None, bin_duration=None, t_start=None, t_stop=None):
    '''
    Calculate the rectified area under the curve (RAUC) for an AnalogSignal.

    The signal is optionally divided into bins with duration `bin_duration`,
    and the rectified signal (absolute value) is integrated within each bin to
    find the area under the curve. The mean or median of the signal or an
    arbitrary baseline may optionally be subtracted before rectification. If
    the number of bins is 1 (default), a single value is returned for each
    channel in the input signal. Otherwise, an AnalogSignal containing the
    values for each bin is returned along with the times of the centers of the
    bins.

    Parameters
    ----------
    signal : neo.AnalogSignal
        The signal to integrate. If `signal` contains more than one channel,
        each is integrated separately.
    bin_duration : quantities.Quantity
        The length of time that each integration should span. If None, there
        will be only one bin spanning the entire signal duration. If
        `bin_duration` does not divide evenly into the signal duration, the end
        of the signal is padded with zeros to accomodate the final,
        overextending bin.
        Default: None
    baseline : string or quantities.Quantity
        A factor to subtract from the signal before rectification. If `'mean'`
        or `'median'`, the mean or median value of the entire signal is
        subtracted on a channel-by-channel basis.
        Default: None
    t_start, t_stop : quantities.Quantity
        Times to start and end the algorithm. The signal is cropped using
        `signal.time_slice(t_start, t_stop)` after baseline removal. Useful if
        you want the RAUC for a short section of the signal but want the
        mean or median calculation (`baseline='mean'` or `baseline='median'`)
        to use the entire signal for better baseline estimation.
        Default: None

    Returns
    -------
    quantities.Quantity or neo.AnalogSignal
        If the number of bins is 1, the returned object is a scalar or
        vector Quantity containing a single RAUC value for each channel.
        Otherwise, the returned object is an AnalogSignal containing the
        RAUC(s) for each bin stored as a sample, with times corresponding to
        the center of each bin. The output signal will have the same number
        of channels as the input signal.

    Raises
    ------
    TypeError
        If the input signal is not a neo.AnalogSignal.
    TypeError
        If `bin_duration` is not None or a Quantity.
    TypeError
        If `baseline` is not None, `'mean'`, `'median'`, or a Quantity.
    '''

    if not isinstance(signal, neo.AnalogSignal):
        raise TypeError('Input signal is not a neo.AnalogSignal!')

    if baseline is None:
        pass
    elif baseline == 'mean':
        # subtract mean from each channel
        signal = signal - signal.mean(axis=0)
    elif baseline == 'median':
        # subtract median from each channel
        signal = signal - np.median(signal.as_quantity(), axis=0)
    elif isinstance(baseline, pq.Quantity):
        # subtract arbitrary baseline
        signal = signal - baseline
    else:
        raise TypeError(
            'baseline must be None, \'mean\', \'median\', '
            'or a Quantity: {}'.format(baseline))

    # slice the signal after subtracting baseline
    signal = signal.time_slice(t_start, t_stop)

    if bin_duration is not None:
        # from bin duration, determine samples per bin and number of bins
        if isinstance(bin_duration, pq.Quantity):
            samples_per_bin = int(np.round(
                bin_duration.rescale('s')/signal.sampling_period.rescale('s')))
            n_bins = int(np.ceil(signal.shape[0]/samples_per_bin))
        else:
            raise TypeError(
                'bin_duration must be a Quantity: {}'.format(bin_duration))
    else:
        # all samples in one bin
        samples_per_bin = signal.shape[0]
        n_bins = 1

    # store the actual bin duration
    bin_duration = samples_per_bin * signal.sampling_period

    # reshape into equal size bins, padding the end with zeros if necessary
    n_channels = signal.shape[1]
    sig_binned = signal.as_quantity().copy()
    sig_binned.resize(n_bins * samples_per_bin, n_channels, refcheck=False)
    sig_binned = sig_binned.reshape(n_bins, samples_per_bin, n_channels)

    # rectify and integrate over each bin
    rauc = np.trapz(np.abs(sig_binned), dx=signal.sampling_period, axis=1)

    if n_bins == 1:
        # return a single value for each channel
        return rauc.squeeze()

    else:
        # return an AnalogSignal with times corresponding to center of each bin
        rauc_sig = neo.AnalogSignal(
            rauc,
            t_start=signal.t_start.rescale(bin_duration.units)+bin_duration/2,
            sampling_period=bin_duration)
        return rauc_sig

###############################################################################
# elephant.spike_train_generation

def peak_detection(signal, threshold=0.0 * mV, sign='above', format=None):
    """
    Return the peak times for all events that cross threshold.
    Usually used for extracting spike times from a membrane potential.
    Similar to spike_train_generation.threshold_detection.

    Parameters
    ----------
    signal : neo AnalogSignal object
        'signal' is an analog signal.
    threshold : A quantity, e.g. in mV
        'threshold' contains a value that must be reached
        for an event to be detected.
    sign : 'above' or 'below'
        'sign' determines whether to count thresholding crossings that
        cross above or below the threshold. Default: 'above'.
    format : None or 'raw'
        Whether to return as SpikeTrain (None) or as a plain array
        of times ('raw'). Default: None.

    Returns
    -------
    result_st : neo SpikeTrain object
        'result_st' contains the spike times of each of the events
        (spikes) extracted from the signal.
    """
    assert threshold is not None, "A threshold must be provided"

    if sign == 'above':
        cutout = np.where(signal > threshold)[0]
        peak_func = np.argmax
    elif sign == 'below':
        cutout = np.where(signal < threshold)[0]
        peak_func = np.argmin
    else:
        raise ValueError("sign must be 'above' or 'below'")

    if len(cutout) <= 0:
        events_base = np.zeros(0)
    else:
        # Select thr crossings lasting at least 2 dtps, np.diff(cutout) > 2
        # This avoids empty slices
        border_start = np.where(np.diff(cutout) > 1)[0]
        border_end = border_start + 1
        borders = np.concatenate((border_start, border_end))
        borders = np.append(0, borders)
        borders = np.append(borders, len(cutout)-1)
        borders = np.sort(borders)
        true_borders = cutout[borders]
        right_borders = true_borders[1::2] + 1
        true_borders = np.sort(np.append(true_borders[0::2], right_borders))

        # Workaround for bug that occurs when signal goes below thr for 1 dtp,
        # Workaround eliminates empy slices from np. split
        backward_mask = np.absolute(np.ediff1d(true_borders, to_begin=1)) > 0
        forward_mask = np.absolute(np.ediff1d(true_borders[::-1],
                                              to_begin=1)[::-1]) > 0
        true_borders = true_borders[backward_mask * forward_mask]
        split_signal = np.split(np.array(signal), true_borders)[1::2]

        maxima_idc_split = np.array([peak_func(x) for x in split_signal])

        max_idc = maxima_idc_split + true_borders[0::2]

        events = signal.times[max_idc]
        events_base = events.magnitude

        if events_base is None:
            # This occurs in some Python 3 builds due to some
            # bug in quantities.
            events_base = np.array([event.magnitude for event in events])  # Workaround
    if format is None:
        result_st = SpikeTrain(events_base, units=signal.times.units,
                               t_start=signal.t_start, t_stop=signal.t_stop)
    elif 'raw':
        result_st = events_base
    else:
        raise ValueError("Format argument must be None or 'raw'")

    return result_st

###############################################################################
# elephant.statistics

def isi(spiketrain, axis=-1):
    """
    Return an array containing the inter-spike intervals of the SpikeTrain.

    Accepts a Neo SpikeTrain, a Quantity array, or a plain NumPy array.
    If either a SpikeTrain or Quantity array is provided, the return value will
    be a quantities array, otherwise a plain NumPy array. The units of
    the quantities array will be the same as spiketrain.

    Parameters
    ----------

    spiketrain : Neo SpikeTrain or Quantity array or NumPy ndarray
                 The spike times.
    axis : int, optional
           The axis along which the difference is taken.
           Default is the last axis.

    Returns
    -------

    NumPy array or quantities array.

    """
    if axis is None:
        axis = -1
    if isinstance(spiketrain, neo.SpikeTrain):
        intervals = np.diff(
            np.sort(spiketrain.times.view(pq.Quantity)), axis=axis)
    else:
        intervals = np.diff(np.sort(spiketrain), axis=axis)
    return intervals

def instantaneous_rate(spiketrain, sampling_period, kernel='auto',
                       cutoff=5.0, t_start=None, t_stop=None, trim=False):
    """
    Estimates instantaneous firing rate by kernel convolution.

    Parameters
    -----------
    spiketrain : neo.SpikeTrain or list of neo.SpikeTrain objects
        Neo object that contains spike times, the unit of the time stamps
        and t_start and t_stop of the spike train.
    sampling_period : Time Quantity
        Time stamp resolution of the spike times. The same resolution will
        be assumed for the kernel
    kernel : string 'auto' or callable object of :class:`Kernel` from module
        'kernels.py'. Currently implemented kernel forms are rectangular,
        triangular, epanechnikovlike, gaussian, laplacian, exponential,
        and alpha function.
        Example: kernel = kernels.RectangularKernel(sigma=10*ms, invert=False)
        The kernel is used for convolution with the spike train and its
        standard deviation determines the time resolution of the instantaneous
        rate estimation.
        Default: 'auto'. In this case, the optimized kernel width for the
        rate estimation is calculated according to [1] and with this width
        a gaussian kernel is constructed. Automatized calculation of the
        kernel width is not available for other than gaussian kernel shapes.
    cutoff : float
        This factor determines the cutoff of the probability distribution of
        the kernel, i.e., the considered width of the kernel in terms of
        multiples of the standard deviation sigma.
        Default: 5.0
    t_start : Time Quantity (optional)
        Start time of the interval used to compute the firing rate. If None
        assumed equal to spiketrain.t_start
        Default: None
    t_stop : Time Quantity (optional)
        End time of the interval used to compute the firing rate (included).
        If None assumed equal to spiketrain.t_stop
        Default: None
    trim : bool
        if False, the output of the Fast Fourier Transformation being a longer
        vector than the input vector by the size of the kernel is reduced back
        to the original size of the considered time interval of the spiketrain
        using the median of the kernel.
        if True, only the region of the convolved signal is returned, where
        there is complete overlap between kernel and spike train. This is
        achieved by reducing the length of the output of the Fast Fourier
        Transformation by a total of two times the size of the kernel, and
        t_start and t_stop are adjusted.
        Default: False

    Returns
    -------
    rate : neo.AnalogSignal
        Contains the rate estimation in unit hertz (Hz).
        Has a property 'rate.times' which contains the time axis of the rate
        estimate. The unit of this property is the same as the resolution that
        is given via the argument 'sampling_period' to the function.

    Raises
    ------
    TypeError:
        If `spiketrain` is not an instance of :class:`SpikeTrain` of Neo.
        If `sampling_period` is not a time quantity.
        If `kernel` is neither instance of :class:`Kernel` or string 'auto'.
        If `cutoff` is neither float nor int.
        If `t_start` and `t_stop` are neither None nor a time quantity.
        If `trim` is not bool.

    ValueError:
        If `sampling_period` is smaller than zero.

    Example
    --------
    kernel = kernels.AlphaKernel(sigma = 0.05*s, invert = True)
    rate = instantaneous_rate(spiketrain, sampling_period = 2*ms, kernel)

    References
    ----------
    ..[1] H. Shimazaki, S. Shinomoto, J Comput Neurosci (2010) 29:171–182.

    """
    # Merge spike trains if list of spike trains given:
    if isinstance(spiketrain, list):
        _check_consistency_of_spiketrainlist(
            spiketrain, t_start=t_start, t_stop=t_stop)
        if t_start is None:
            t_start = spiketrain[0].t_start
        if t_stop is None:
            t_stop = spiketrain[0].t_stop
        spikes = np.concatenate([st.magnitude for st in spiketrain])
        merged_spiketrain = SpikeTrain(np.sort(spikes), units=spiketrain[0].units,
                                       t_start=t_start, t_stop=t_stop)
        return instantaneous_rate(merged_spiketrain, sampling_period=sampling_period,
                                  kernel=kernel, cutoff=cutoff, t_start=t_start,
                                  t_stop=t_stop, trim=trim)

    # Checks of input variables:
    if not isinstance(spiketrain, SpikeTrain):
        raise TypeError(
            "spiketrain must be instance of :class:`SpikeTrain` of Neo!\n"
            "    Found: %s, value %s" % (type(spiketrain), str(spiketrain)))

    if not (isinstance(sampling_period, pq.Quantity) and
            sampling_period.dimensionality.simplified ==
            pq.Quantity(1, "s").dimensionality):
        raise TypeError(
            "The sampling period must be a time quantity!\n"
            "    Found: %s, value %s" % (type(sampling_period), str(sampling_period)))

    if sampling_period.magnitude < 0:
        raise ValueError("The sampling period must be larger than zero.")

    if kernel == 'auto':
        kernel_width = sskernel(spiketrain.magnitude, tin=None,
                                bootstrap=True)['optw']
        if kernel_width is None:
            raise ValueError(
                "Unable to calculate optimal kernel width for "
                "instantaneous rate from input data.")
        unit = spiketrain.units
        sigma = 1 / (2.0 * 2.7) * kernel_width * unit
        # factor 2.0 connects kernel width with its half width,
        # factor 2.7 connects half width of Gaussian distribution with
        #             99% probability mass with its standard deviation.
        kernel = GaussianKernel(sigma)
    elif not isinstance(kernel, Kernel):
        raise TypeError(
            "kernel must be either instance of :class:`Kernel` "
            "or the string 'auto'!\n"
            "    Found: %s, value %s" % (type(kernel), str(kernel)))

    if not (isinstance(cutoff, float) or isinstance(cutoff, int)):
        raise TypeError("cutoff must be float or integer!")

    if not (t_start is None or (isinstance(t_start, pq.Quantity) and
                                t_start.dimensionality.simplified ==
                                pq.Quantity(1, "s").dimensionality)):
        raise TypeError("t_start must be a time quantity!")

    if not (t_stop is None or (isinstance(t_stop, pq.Quantity) and
                               t_stop.dimensionality.simplified ==
                               pq.Quantity(1, "s").dimensionality)):
        raise TypeError("t_stop must be a time quantity!")

    if not (isinstance(trim, bool)):
        raise TypeError("trim must be bool!")

    # main function:
    units = pq.CompoundUnit(
        "%s*s" % str(sampling_period.rescale('s').magnitude))
    spiketrain = spiketrain.rescale(units)
    if t_start is None:
        t_start = spiketrain.t_start
    else:
        t_start = t_start.rescale(spiketrain.units)

    if t_stop is None:
        t_stop = spiketrain.t_stop
    else:
        t_stop = t_stop.rescale(spiketrain.units)

    time_vector = np.zeros(int((t_stop - t_start)) + 1)

    spikes_slice = spiketrain.time_slice(t_start, t_stop) \
        if len(spiketrain) else np.array([])

    for spike in spikes_slice:
        index = int((spike - t_start))
        time_vector[index] += 1

    if cutoff < kernel.min_cutoff:
        cutoff = kernel.min_cutoff
        warnings.warn("The width of the kernel was adjusted to a minimally "
                      "allowed width.")

    t_arr = np.arange(-cutoff * kernel.sigma.rescale(units).magnitude,
                      cutoff * kernel.sigma.rescale(units).magnitude +
                      sampling_period.rescale(units).magnitude,
                      sampling_period.rescale(units).magnitude) * units

    r = scipy.signal.fftconvolve(time_vector,
                                 kernel(t_arr).rescale(pq.Hz).magnitude, 'full')
    if np.any(r < 0):
        # warnings.warn("Instantaneous firing rate approximation contains "
        #               "negative values, possibly caused due to machine "
        #               "precision errors.")
        r = r.clip(0, None)  # replace negative values with 0

    if not trim:
        r = r[kernel.median_index(t_arr):-(kernel(t_arr).size -
                                           kernel.median_index(t_arr))]
    elif trim:
        r = r[2 * kernel.median_index(t_arr):-2 * (kernel(t_arr).size -
                                                   kernel.median_index(t_arr))]
        t_start += kernel.median_index(t_arr) * spiketrain.units
        t_stop -= (kernel(t_arr).size -
                   kernel.median_index(t_arr)) * spiketrain.units

    rate = neo.AnalogSignal(signal=r.reshape(r.size, 1),
                            sampling_period=sampling_period,
                            units=pq.Hz, t_start=t_start, t_stop=t_stop)

    return rate

def nextpow2(x):
    """ Return the smallest integral power of 2 that >= x """
    n = 2
    while n < x:
        n = 2 * n
    return n

def fftkernel(x, w):
    """

    y = fftkernel(x,w)

    Function `fftkernel' applies the Gauss kernel smoother to an input
    signal using FFT algorithm.

    Input argument
    x:    Sample signal vector.
    w: 	Kernel bandwidth (the standard deviation) in unit of
    the sampling resolution of x.

    Output argument
    y: 	Smoothed signal.

    MAY 5/23, 2012 Author Hideaki Shimazaki
    RIKEN Brain Science Insitute
    http://2000.jukuin.keio.ac.jp/shimazaki

    Ported to Python: Subhasis Ray, NCBS. Tue Jun 10 10:42:38 IST 2014

    """
    L = len(x)
    Lmax = L + 3 * w
    n = nextpow2(Lmax)
    X = np.fft.fft(x, n)
    f = np.arange(0, n, 1.0) / n
    f = np.concatenate((-f[:int(n / 2)], f[int(n / 2):0:-1]))
    K = np.exp(-0.5 * (w * 2 * np.pi * f)**2)
    y = np.fft.ifft(X * K, n)
    y = y[:L].copy()
    return y

def logexp(x):
    if x < 1e2:
        y = np.log(1 + np.exp(x))
    else:
        y = x
    return y

def ilogexp(x):
    if x < 1e2:
        y = np.log(np.exp(x) - 1)
    else:
        y = x
    return y

def cost_function(x, N, w, dt):
    """

    The cost function
    Cn(w) = sum_{i,j} int k(x - x_i) k(x - x_j) dx - 2 sum_{i~=j} k(x_i - x_j)

     """
    yh = np.abs(fftkernel(x, w / dt))  # density
    # formula for density
    C = np.sum(yh ** 2) * dt - 2 * np.sum(yh * x) * \
        dt + 2 / np.sqrt(2 * np.pi) / w / N
    C = C * N * N
    # formula for rate
    # C = dt*sum( yh.^2 - 2*yh.*y_hist + 2/sqrt(2*pi)/w*y_hist )
    return C, yh

def sskernel(spiketimes, tin=None, w=None, bootstrap=False):
    """

    Calculates optimal fixed kernel bandwidth.

    spiketimes: sequence of spike times (sorted to be ascending).

    tin: (optional) time points at which the kernel bandwidth is to be estimated.

    w: (optional) vector of kernel bandwidths. If specified, optimal
    bandwidth is selected from this.

    bootstrap (optional): whether to calculate the 95% confidence
    interval. (default False)

    Returns

    A dictionary containing the following key value pairs:

    'y': estimated density,
    't': points at which estimation was computed,
    'optw': optimal kernel bandwidth,
    'w': kernel bandwidths examined,
    'C': cost functions of w,
    'confb95': (lower bootstrap confidence level, upper bootstrap confidence level),
    'yb': bootstrap samples.

    If no optimal kernel could be found, all entries of the dictionary are set
    to None.


    Ref: Shimazaki, Hideaki, and Shigeru Shinomoto. 2010. Kernel
    Bandwidth Optimization in Spike Rate Estimation. Journal of
    Computational Neuroscience 29 (1-2):
    171-82. doi:10.1007/s10827-009-0180-4.

    """

    if tin is None:
        time = np.max(spiketimes) - np.min(spiketimes)
        isi = np.diff(spiketimes)
        isi = isi[isi > 0].copy()
        dt = np.min(isi)
        tin = np.linspace(np.min(spiketimes),
                          np.max(spiketimes),
                          min(int(time / dt + 0.5), 1000))  # The 1000 seems somewhat arbitrary
        t = tin
    else:
        time = np.max(tin) - np.min(tin)
        spiketimes = spiketimes[(spiketimes >= np.min(tin)) &
                                (spiketimes <= np.max(tin))].copy()
        isi = np.diff(spiketimes)
        isi = isi[isi > 0].copy()
        dt = np.min(isi)
        if dt > np.min(np.diff(tin)):
            t = np.linspace(np.min(tin), np.max(tin),
                            min(int(time / dt + 0.5), 1000))
        else:
            t = tin
    dt = np.min(np.diff(tin))
    yhist, bins = np.histogram(spiketimes, np.r_[t - dt / 2, t[-1] + dt / 2])
    N = np.sum(yhist)
    yhist = yhist / (N * dt)  # density
    optw = None
    y = None
    if w is not None:
        C = np.zeros(len(w))
        Cmin = np.inf
        for k, w_ in enumerate(w):
            C[k], yh = cost_function(yhist, N, w_, dt)
            if C[k] < Cmin:
                Cmin = C[k]
                optw = w_
                y = yh
    else:
        # Golden section search on a log-exp scale
        wmin = 2 * dt
        wmax = max(spiketimes) - min(spiketimes)
        imax = 20  # max iterations
        w = np.zeros(imax)
        C = np.zeros(imax)
        tolerance = 1e-5
        phi = 0.5 * (np.sqrt(5) + 1)  # The Golden ratio
        a = ilogexp(wmin)
        b = ilogexp(wmax)
        c1 = (phi - 1) * a + (2 - phi) * b
        c2 = (2 - phi) * a + (phi - 1) * b
        f1, y1 = cost_function(yhist, N, logexp(c1), dt)
        f2, y2 = cost_function(yhist, N, logexp(c2), dt)
        k = 0
        while (np.abs(b - a) > (tolerance * (np.abs(c1) + np.abs(c2))))\
                and (k < imax):
            if f1 < f2:
                b = c2
                c2 = c1
                c1 = (phi - 1) * a + (2 - phi) * b
                f2 = f1
                f1, y1 = cost_function(yhist, N, logexp(c1), dt)
                w[k] = logexp(c1)
                C[k] = f1
                optw = logexp(c1)
                y = y1 / (np.sum(y1 * dt))
            else:
                a = c1
                c1 = c2
                c2 = (2 - phi) * a + (phi - 1) * b
                f1 = f2
                f2, y2 = cost_function(yhist, N, logexp(c2), dt)
                w[k] = logexp(c2)
                C[k] = f2
                optw = logexp(c2)
                y = y2 / np.sum(y2 * dt)
            k = k + 1
    # Bootstrap confidence intervals
    confb95 = None
    yb = None
    # If bootstrap is requested, and an optimal kernel was found
    if bootstrap and optw:
        nbs = 1000
        yb = np.zeros((nbs, len(tin)))
        for ii in range(nbs):
            idx = np.floor(np.random.rand(N) * N).astype(int)
            xb = spiketimes[idx]
            y_histb, bins = np.histogram(
                xb, np.r_[t - dt / 2, t[-1] + dt / 2]) / dt / N
            yb_buf = fftkernel(y_histb, optw / dt).real
            yb_buf = yb_buf / np.sum(yb_buf * dt)
            yb[ii, :] = np.interp(tin, t, yb_buf)
        ybsort = np.sort(yb, axis=0)
        y95b = ybsort[np.floor(0.05 * nbs).astype(int), :]
        y95u = ybsort[np.floor(0.95 * nbs).astype(int), :]
        confb95 = (y95b, y95u)
    # Only perform interpolation if y could be calculated
    if y is not None:
        y = np.interp(tin, t, y)
    return {'y': y,
            't': tin,
            'optw': optw,
            'w': w,
            'C': C,
            'confb95': confb95,
            'yb': yb}

def _check_consistency_of_spiketrainlist(spiketrainlist, t_start=None, t_stop=None):
    for spiketrain in spiketrainlist:
        if not isinstance(spiketrain, SpikeTrain):
            raise TypeError(
                "spike train must be instance of :class:`SpikeTrain` of Neo!\n"
                "    Found: %s, value %s" % (type(spiketrain), str(spiketrain)))
        if t_start is None and not spiketrain.t_start == spiketrainlist[0].t_start:
            raise ValueError(
                "the spike trains must have the same t_start!")
        if t_stop is None and not spiketrain.t_stop == spiketrainlist[0].t_stop:
            raise ValueError(
                "the spike trains must have the same t_stop!")
        if not spiketrain.units == spiketrainlist[0].units:
            raise ValueError(
                "the spike trains must have the same units!")
    return None
