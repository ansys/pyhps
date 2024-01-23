Job management service
======================

Ansys REP includes Job Management Service (JMS), which is the main service for storing and evaluating jobs using multiple heterogeneous compute resources. 

The Python subpackage ``ansys.hps.core.jms`` wraps around the JMS service REST API available at ``https://hostname:port/rep/jms/api``.

APIs
----

JMS API
^^^^^^^
.. autoclass:: ansys.hps.core.jms.JmsApi
   :members:
   :undoc-members:

Project API
^^^^^^^^^^^
.. autoclass:: ansys.hps.core.jms.ProjectApi
   :members:
   :undoc-members:


Resources
---------

File
^^^^
 
.. autoclass:: ansys.hps.core.jms.File
   :members:

Project
^^^^^^^
 
.. autoclass:: ansys.hps.core.jms.Project
   :members:
   :undoc-members:
   :exclude-members: Meta

Fitness definition
^^^^^^^^^^^^^^^^^^
 
.. autoclass:: ansys.hps.core.jms.FitnessTermDefinition
   :members:

.. autoclass:: ansys.hps.core.jms.FitnessDefinition
   :members:


Parameters
^^^^^^^^^^

.. autoclass:: ansys.hps.core.jms.FloatParameterDefinition
   :members:

.. autoclass:: ansys.hps.core.jms.BoolParameterDefinition
   :members:

.. autoclass:: ansys.hps.core.jms.IntParameterDefinition
   :members:

.. autoclass:: ansys.hps.core.jms.StringParameterDefinition
   :members:

.. autoclass:: ansys.hps.core.jms.ParameterMapping
   :members:

Task definition
^^^^^^^^^^^^^^^

.. autoclass:: ansys.hps.core.jms.Software
   :members:

.. autoclass:: ansys.hps.core.jms.ResourceRequirements
   :members:

.. autoclass:: ansys.hps.core.jms.SuccessCriteria
   :members:

.. autoclass:: ansys.hps.core.jms.Licensing
   :members:

.. autoclass:: ansys.hps.core.jms.TaskDefinition
   :members:


Job definition
^^^^^^^^^^^^^^

.. autoclass:: ansys.hps.core.jms.JobDefinition
   :members:
   :undoc-members:
   :exclude-members: Meta

Task
^^^^

.. autoclass:: ansys.hps.core.jms.Task
   :members:


Job
^^^

.. autoclass:: ansys.hps.core.jms.Job
   :members:


Job selection
^^^^^^^^^^^^^

.. autoclass:: ansys.hps.core.jms.JobSelection
   :members:


Design exploration algorithm
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: ansys.hps.core.jms.Algorithm
   :members:


Evaluator
^^^^^^^^^

.. autoclass:: ansys.hps.core.jms.Evaluator
   :members:


Task definition template
^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: ansys.hps.core.jms.TemplateProperty
   :members:

.. autoclass:: ansys.hps.core.jms.TemplateResourceRequirements
   :members:

.. autoclass:: ansys.hps.core.jms.TemplateInputFile
   :members:

.. autoclass:: ansys.hps.core.jms.TemplateOutputFile
   :members:

.. autoclass:: ansys.hps.core.jms.TaskDefinitionTemplate
   :members:

Permissions
^^^^^^^^^^^

.. autoclass:: ansys.hps.core.jms.Permission
   :members: