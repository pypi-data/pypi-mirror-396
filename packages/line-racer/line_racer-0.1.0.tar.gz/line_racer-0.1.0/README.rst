==========
line racer
==========

**line racer: An easy-to-use Python package for calculating (high-resolution) opacities from molecular line lists for atmospheric modeling**

Welcome to the **line racer** repository! line racer is a Python package designed to compute high-resolution opacities from molecular
(and in the future atomic) line lists. It combines two methods to calculate the line profiles:
A direct calculation method using the Humlicek algorithm (`Humlícek, 1982 <https://www.sciencedirect.com/science/article/pii/0022407382900784?via%3Dihub>`_) and a
speedup for calculating the line wings based on `Mollière et al. (2015) <https://iopscience.iop.org/article/10.1088/0004-637X/813/1/47>`_
to calculate the lines with the most intensity.
A sampling technique of the line profiles based on `Min (2017) <https://www.aanda.org/articles/aa/pdf/2017/11/aa31612-17.pdf>`_
for an ultra fast calculation of the lower intensity lines.
The opacities can directly be output in the pRT format used by the petitRADTRANS code (`Mollière et al., 2019, <https://www.aanda.org/articles/aa/full_html/2019/07/aa35470-19/aa35470-19.html>`_
`Blain et al., 2024 <https://joss.theoj.org/papers/10.21105/joss.07028.pdf>`_).
The opacities calculated with line racer can be directly used in atmospheric modeling and retrieval codes.

Documentation
=============

The code documentation, installation guide, and tutorial can be found `here <https://line-racer.readthedocs.io/en/latest/index.html>`_

Attribution
===========

If you use line racer in your work, please cite the following article:


License
=======

Copyright 2025 David Hägele and Paul Mollière

line racer is available under the MIT license.
See the LICENSE file for more information.