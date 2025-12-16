#!/usr/bin/env python3
# pyrotoolbox, a collection of tools to work with PyroScience GmbH data.
# Copyright (C) 2025, Christoph Staudinger
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""Tools for phase-calculation, dlr and other stuff. Angles are in ° in this lib"""

import numpy as np


def cot(dPhi):
    """calculate cot of an angle in °"""
    return 1 / np.tan(np.radians(dPhi))


def demudulation(tau, f):
    """calculate demodulation

    :param tau: lifetime in s
    :param f: modulation frequency in Hz
    """
    return 1 / np.sqrt((2 * np.pi) ** 2 * tau**2)


def calc_tau(dPhi, f):
    """calculate lifetime from phase angle and modulation frequency

    :param dPhi: phase angle in °
    :param f: modulation frequency
    """
    return np.tan(np.radians(dPhi)) / 2 / np.pi / f


tau = calc_tau  # legacy


def calc_dphi(tau, f):
    """calculate phase angle from lifetime and modulation frequency

    :param tau: lifetime in s
    :param f: modulation frequency
    :return: phase angle in °
    """
    return np.rad2deg(np.arctan(tau * 2 * np.pi * f))


def calc_background(signal, dPhi_meas, dPhi_true):
    """calculate background from a measurement if a true dPhi is known

    :param signal: measured amplitude
    :param dPhi_meas: measured dPhi
    :param dPhi_true: true dPhi without background
    """
    # convert to radians
    dPhi_meas = np.radians(dPhi_meas)
    dPhi_true = np.radians(dPhi_true)
    return signal * np.cos(dPhi_meas) - signal * np.sin(dPhi_meas) / np.tan(dPhi_true)


def subtract_bg(dPhi, amp, bg_amp, bg_dPhi=0):
    """corrects the supplied dPhi values from the given background

    :param dPhi: dPhi value with background
    :param amp: amplitude value with background
    :param bg_amp: amplitude of background
    :param bg_dPhi: dPhi of background (default 0)
    """
    return np.rad2deg(
        np.arctan(
            (amp * np.sin(np.radians(dPhi)) - bg_amp * np.sin(np.radians(bg_dPhi)))
            / (amp * np.cos(np.radians(dPhi)) - bg_amp * np.cos(np.radians(bg_dPhi)))
        )
    )


def subtract_bg_signal(dPhi, amp, bg_amp, bg_dPhi=0):
    """corrects the supplied dPhi values from the given background and returns the real amplitude

    :param dPhi: dPhi value with background
    :param amp: amplitude value with background
    :param bg_amp: amplitude of background
    :param bg_dPhi: dPhi of background (default 0)
    """
    return np.sqrt(
        (amp * np.sin(np.radians(dPhi)) - bg_amp * np.sin(np.radians(bg_dPhi))) ** 2
        + (amp * np.cos(np.radians(dPhi)) - bg_amp * np.cos(np.radians(bg_dPhi))) ** 2
    )


def calc_R(dPhi, dPhiref):
    """Calculate R (ratio between fluorescence and phosphorescence)

    :param dPhi: in °
    :param dPhiref: in °
    :return: R-value
    """
    return (cot(dPhi) - cot(dPhiref)) * np.sin(np.radians(dPhiref))


def R_to_dPhi(R, dPhiref):
    """Reverse function of calc_R

    :param R:
    :param dPhiref: in °
    :return: dPhi in °
    """
    return np.rad2deg(np.arctan(1 / (R / np.sin(np.radians(dPhiref)) + cot(dPhiref))))
