Job Management Service
===========================

Ansys REP includes Job Management Service (JMS), which is the main service for storing and evaluating jobs using multiple heterogeneous compute resources. 

The Python subpackage ``ansys.rep.client.jms`` wraps around the JMS service REST API available at ``https://hostname:port/rep/jms/api``.

APIs
--------------------------------------

JMS Api
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. autoclass:: ansys.rep.client.jms.JmsApi
   :members:
   :undoc-members:

Project Api
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. autoclass:: ansys.rep.client.jms.ProjectApi
   :members:
   :undoc-members:


Resources
--------------------------------------

File
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
 
.. autoclass:: ansys.rep.client.jms.File
   :members:

Project
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
 
.. autoclass:: ansys.rep.client.jms.Project
   :members:
   :undoc-members:
   :exclude-members: Meta

Fitness Definition
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
 
.. autoclass:: ansys.rep.client.jms.FitnessTermDefinition
   :members:

.. autoclass:: ansys.rep.client.jms.FitnessDefinition
   :members:


Parameters
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

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

Task Definition
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: ansys.rep.client.jms.Software
   :members:

.. autoclass:: ansys.rep.client.jms.ResourceRequirements
   :members:

.. autoclass:: ansys.rep.client.jms.SuccessCriteria
   :members:

.. autoclass:: ansys.rep.client.jms.Licensing
   :members:

.. autoclass:: ansys.rep.client.jms.TaskDefinition
   :members:


Job Definition
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: ansys.rep.client.jms.JobDefinition
   :members:
   :undoc-members:
   :exclude-members: Meta

Task
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: ansys.rep.client.jms.Task
   :members:


Job
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: ansys.rep.client.jms.Job
   :members:


Job Selection
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: ansys.rep.client.jms.JobSelection
   :members:


Design Exploration Algorithm
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: ansys.rep.client.jms.Algorithm
   :members:


Evaluator
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: ansys.rep.client.jms.Evaluator
   :members:


Task Definition Template
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: ansys.rep.client.jms.TemplateProperty
   :members:

.. autoclass:: ansys.rep.client.jms.TemplateResourceRequirements
   :members:

.. autoclass:: ansys.rep.client.jms.TemplateInputFile
   :members:

.. autoclass:: ansys.rep.client.jms.TemplateOutputFile
   :members:

.. autoclass:: ansys.rep.client.jms.TaskDefinitionTemplate
   :members:

Permissions
^^^^^^^^^^^

.. autoclass:: ansys.rep.client.jms.Permission
   :members: