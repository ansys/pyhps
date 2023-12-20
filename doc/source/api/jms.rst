Job Management Service
===========================

Ansys REP includes Job Management Service (JMS), which is the main service for storing and evaluating jobs using multiple heterogeneous compute resources. 

The Python subpackage ``ansys.hps.client.jms`` wraps around the JMS service REST API available at ``https://hostname:port/hps/jms/api``.

APIs
--------------------------------------

JMS Api
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. autoclass:: ansys.hps.client.jms.JmsApi
   :members:
   :undoc-members:

Project Api
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. autoclass:: ansys.hps.client.jms.ProjectApi
   :members:
   :undoc-members:


Resources
--------------------------------------

File
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
 
.. autoclass:: ansys.hps.client.jms.File
   :members:

Project
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
 
.. autoclass:: ansys.hps.client.jms.Project
   :members:
   :undoc-members:
   :exclude-members: Meta

Fitness Definition
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
 
.. autoclass:: ansys.hps.client.jms.FitnessTermDefinition
   :members:

.. autoclass:: ansys.hps.client.jms.FitnessDefinition
   :members:


Parameters
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: ansys.hps.client.jms.FloatParameterDefinition
   :members:

.. autoclass:: ansys.hps.client.jms.BoolParameterDefinition
   :members:

.. autoclass:: ansys.hps.client.jms.IntParameterDefinition
   :members:

.. autoclass:: ansys.hps.client.jms.StringParameterDefinition
   :members:

.. autoclass:: ansys.hps.client.jms.ParameterMapping
   :members:

Task Definition
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: ansys.hps.client.jms.Software
   :members:

.. autoclass:: ansys.hps.client.jms.ResourceRequirements
   :members:

.. autoclass:: ansys.hps.client.jms.SuccessCriteria
   :members:

.. autoclass:: ansys.hps.client.jms.Licensing
   :members:

.. autoclass:: ansys.hps.client.jms.TaskDefinition
   :members:


Job Definition
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: ansys.hps.client.jms.JobDefinition
   :members:
   :undoc-members:
   :exclude-members: Meta

Task
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: ansys.hps.client.jms.Task
   :members:


Job
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: ansys.hps.client.jms.Job
   :members:


Job Selection
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: ansys.hps.client.jms.JobSelection
   :members:


Design Exploration Algorithm
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: ansys.hps.client.jms.Algorithm
   :members:


Evaluator
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: ansys.hps.client.jms.Evaluator
   :members:


Task Definition Template
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: ansys.hps.client.jms.TemplateProperty
   :members:

.. autoclass:: ansys.hps.client.jms.TemplateResourceRequirements
   :members:

.. autoclass:: ansys.hps.client.jms.TemplateInputFile
   :members:

.. autoclass:: ansys.hps.client.jms.TemplateOutputFile
   :members:

.. autoclass:: ansys.hps.client.jms.TaskDefinitionTemplate
   :members:

Permissions
^^^^^^^^^^^

.. autoclass:: ansys.hps.client.jms.Permission
   :members: