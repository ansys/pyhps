Job Management Service (JMS)
============================

Ansys HPS includes the Job Management Service (JMS), which is the main service for storing
and evaluating jobs using multiple heterogeneous compute resources. 

The ``ansys.hps.client.jms`` Python subpackage  wraps around the JMS REST API,
which is available at ``https://hostname:port/hps/jms/api``.

APIs
----

.. module:: ansys.hps.client.jms.api

.. autosummary::
   :toctree: _autosummary

   JmsApi
   ProjectApi

Resources
---------

.. module:: ansys.hps.client.jms

.. autosummary::
   :toctree: _autosummary

   File
   Project
   FitnessTermDefinition
   FitnessDefinition
   FloatParameterDefinition
   BoolParameterDefinition
   IntParameterDefinition
   StringParameterDefinition
   ParameterMapping
   Software
   HpcResources
   ResourceRequirements
   SuccessCriteria
   Licensing
   TaskDefinition
   JobDefinition
   Task
   Job
   JobSelection
   Algorithm
   TemplateProperty
   TemplateResourceRequirements
   TemplateInputFile
   TemplateOutputFile
   TaskDefinitionTemplate
   Permission
