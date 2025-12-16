Oxygen Calculation Tools
========================
A collection of functions to re-calculate results from measurements.

Function to calculate oxygen partial pressure from raw data
-----------------------------------------------------------
The following functions can be used to calculate oxygen partial pressures from the phase angle dphi. All other oxygen
units can be calculated from the partial pressure.

.. automodule:: pyrotoolbox.oxygen
    :members: calculate_pO2, calculate_pO2_from_calibration


Functions for unit conversions
------------------------------
The following functions are used to convert between oxygen units. The partial pressure of oxygen (in hPa) is the central
unit. All units can be converted toward pO2 and all units can be calculated from pO2. It is also the measured unit on
all devices.

.. automodule:: pyrotoolbox.oxygen
    :members: i_only_think_in_hpa, i_have_a_fireplate_and_still_only_think_in_hPa, convert_to_hPa, hPa_to_torr, hPa_to_percentO2, hPa_to_percent_airsat, hPa_to_uM, hPa_to_mgL

Helper functions for oxygen calculations
----------------------------------------
The following functions are implemented do to the above documented calculations. They might still be useful for your
own unit conversions

.. automodule:: pyrotoolbox.oxygen
    :noindex:
    :members: vapour_pressure_water, calc_pressure_and_water_corrected_pO2, calc_oxygen_solubility

Examples
---------

.. toctree::
    Demo2

.. toctree::
    Demo4 O2 unit conversion
