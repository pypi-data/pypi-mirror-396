"""Functions for film thickness calculation"""

import math as m


NQ = 1.668e5  # Hz*cm  Frequency const of AT-cut quartz
RQ = 2.648  # g/cm^3 Density of quartz
MQ = 2.947e11  # g/(cm*s^2) Shear modulus of quartz

NRQ = 140593.14771292824  # NQ * RQ / m.pi [Hz * g / cm^2]


def freq_change_to_mass_per_cm2(f0, f1, z):
    """Calculate film mass per cm2 (g / cm^2)"""
    return NRQ / (z * f1) * m.atan(z * m.tan(m.pi * (f0 - f1) / f0))  # g / cm^2


def freq_change_to_thickness(f0, f1, rho, z):
    """Calculate film thickness (A)"""
    m_per_cm2 = freq_change_to_mass_per_cm2(f0, f1, z)
    return m_per_cm2 / rho * 1e8  # Angstrom
