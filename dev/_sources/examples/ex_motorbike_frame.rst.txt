.. _example_mapdl_motorbike_frame:

MAPDL Motorbike Frame - Project Creation
=========================================

This example shows how to create from scratch a REP project consisting of an Ansys APDL beam model
of a tubular steel trellis motorbike-frame.
After creating the project job_definition, 10 design points with randomly 
chosen parameter values are created and set to pending.

.. image:: ../_static/motorbike_frame.jpg
    :scale: 50 %
    :align: center
    :alt: motorbike frame picture

The model is parametrized as follows:

- three custom tube types are defined whose radius and thickness can vary in a certain range;
- for each tube in the frame there is a string parameter specifying which custom type it should be made of;
- output parameters of interest are the weight, the torsion stiffness and the maximum von Mises stress for a breaking load case. 

For further details about the finite element model and its parametrization, see
"Using Evolutionary Methods with a Heterogeneous Genotype Representation 
for Design Optimization of a Tubular Steel Trellis Motorbike-Frame", 2003
by U. M. Fasel, O. Koenig, M. Wintermantel and P. Ermanni.

.. only:: builder_html

     The project setup script as well as the data files can be downloaded here :download:`MAPDL Motorbike Frame Project <../../../build/mapdl_motorbike_frame.zip>`.

.. literalinclude:: ../../../examples/mapdl_motorbike_frame/project_setup.py
    :language: python
    :caption: project_setup.py