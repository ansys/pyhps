Design Point Service
===========================

Ansys DCS includes Ansys Design Point Service (DPS), which is the main service for storing and evaluating thousands of design points using multiple heterogeneous compute resources. 

The DPS Python client wraps around the DPS service REST API available at ``https://hostname/dcs/dps/api``.

Connection module
------------------------------------------
.. automodule:: ansys.rep.client.connection
  :members:


Client object
------------------------------------
.. autoclass:: ansys.rep.client.jms.Client
   :members:


File
--------------------------------------
 
.. autoclass:: ansys.rep.client.jms.File
   :members:

Project
--------------------------------------
 
.. autoclass:: ansys.rep.client.jms.Project
   :members:
   :undoc-members:
   :exclude-members: Meta

Fitness Definition
--------------------------------------
 
.. autoclass:: ansys.rep.client.jms.FitnessTermDefinition
   :members:

.. autoclass:: ansys.rep.client.jms.FitnessDefinition
   :members:


Parameters
--------------------------------------

.. autoclass:: ansys.rep.client.jms.FloatParameterDefinition
   :members:

.. autoclass:: ansys.rep.client.jms.BoolParameterDefinition
   :members:

.. autoclass:: ansys.rep.client.jms.IntParameterDefinition
   :members:

.. autoclass:: ansys.rep.client.jms.StringParameterDefinition
   :members:

.. autoclass:: ansys.rep.client.jms.ParameterMapping
   :members:

Process Steps
--------------------------------------

.. autoclass:: ansys.rep.client.jms.SuccessCriteria
   :members:

.. autoclass:: ansys.rep.client.jms.Licensing
   :members:

.. autoclass:: ansys.rep.client.jms.TaskDefinition
   :members:


JobDefinition
--------------------------------------

.. autoclass:: ansys.rep.client.jms.JobDefinition
   :members:
   :undoc-members:
   :exclude-members: Meta

Task
-------------------------------------------

.. autoclass:: ansys.rep.client.jms.Task
   :members:


Design Point
-------------------------------------------

.. autoclass:: ansys.rep.client.jms.Job
   :members:


Design Point Selection
----------------------------------------

.. autoclass:: ansys.rep.client.jms.Selection
   :members:


Design Exploration Algorithm
----------------------------------------

.. autoclass:: ansys.rep.client.jms.Algorithm
   :members:


Evaluator
----------------------------------------

.. autoclass:: ansys.rep.client.jms.Evaluator
   :members:


Task Definition Template
----------------------------------------

.. autoclass:: ansys.rep.client.jms.TaskDefinitionTemplate
   :members: