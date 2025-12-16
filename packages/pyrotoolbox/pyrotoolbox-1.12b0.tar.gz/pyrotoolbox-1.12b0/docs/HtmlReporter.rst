PyroHtmlReporter
=================

*PyroHtmlReporter is still in active development. Anything might change!*

A tool to generate html reports of measurement data. The report contains a summary of the measurement, the settings
and calibration registers and an interactive plot of the most important data.
The reports have the filename of the input file with an additional "_report.html".
If more than one file is passed at once the data is combined into a "summary.html" file.

This tool is intended to:
    - create short shareable reports of measurements
    - to have a quick look on measurement data
    - quick debugging

The reports are standalone html files and can be viewed in any browser.

Example usage
--------------

.. code-block:: python

    PyroHtmlReporter my_measurement_data.txt

This results in a file "my_measurement_data_report.html".

.. code-block:: python

    PyroHtmlReporter my_measurement_data1.txt my_measurement_data2.txt

This results in the files "my_measurement_data1_report.html", "my_measurement_data2_report.html" and "summary.html".
