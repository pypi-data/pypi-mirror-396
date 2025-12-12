line racer documentation
========================

Welcome to the **line racer** documentation. line racer is a Python package designed to compute high-resolution opacities from molecular
(and in the future atomic) line lists. It combines two methods to calculate the line profiles:
A direct calculation method using the Humlicek algorithm (`Humlícek, 1982 <https://www.sciencedirect.com/science/article/pii/0022407382900784?via%3Dihub>`_) and a
speedup for calculating the line wings based on `Mollière et al. (2015) <https://iopscience.iop.org/article/10.1088/0004-637X/813/1/47>`_
to calculate the lines with the most intensity.
A sampling technique of the line profiles based on `Min (2017) <https://www.aanda.org/articles/aa/pdf/2017/11/aa31612-17.pdf>`_
for an ultra fast calculation of the lower intensity lines.
The opacities can directly be output in the pRT format used by the petitRADTRANS code (`Mollière et al., 2019, <https://www.aanda.org/articles/aa/full_html/2019/07/aa35470-19/aa35470-19.html>`_
`Blain et al., 2024 <https://joss.theoj.org/papers/10.21105/joss.07028.pdf>`_).
The opacities calculated with line racer can be directly used in atmospheric modeling and retrieval codes.


**To get started with some examples on how to run line racer, see our** `"line racer tutorial" <content/notebooks/line_racer_notebook_example.html>`_.
**Before that, make sure you download the line lists and other required data correctly as described in the** `"downloading line list tutorial" <content/downloading_line_list_data.html>`_.
**If you want to run line racer on a cluster, have a look at the** `cluster calculation tutorial <content/line_racer_on_cluster.html>`_.

**If you are interested in how the line calculations are performed in detail, check out our** `"explain line calculation notebook" <content/notebooks/explain_line_calculation.html>`_.

line racer is available under the MIT License

Please cite `Hägele & Mollière (2025) <https://ui.adsabs.harvard.edu/abs/2025JOSS...stillinprep/abstract>`_ when making use of line racer in your research.

.. _contact: molliere@mpia.de

This documentation webpage contains an `installation guide <content/installation.html>`_, a
`general tutorial <content/notebooks/line_racer_notebook_example.html>`_, a `tutorial to run on clusters <content/notebooks/line_racer_on_cluster.html>`_ , a `explanation of the physical background <content/notebooks/explain_line_calculation.html>`_, `community guidelines for contributions  <content/contributing.html>`_, and an `API documentation <autoapi/index.html>`_.

Developers
__________

- David Hägele and Paul Mollière

Contributors
____________



.. toctree::
   :maxdepth: 3
   :caption: Content:

   content/installation
   content/downloading_line_list_data
   content/notebooks/line_racer_notebook_example
   content/line_racer_on_cluster
   content/notebooks/explain_line_calculation
   content/contributing

.. toctree::
   :maxdepth: 2
   :caption: Code documentation
