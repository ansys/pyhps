Resource Management Service
===========================

Ansys REP includes the Resource Management Service (JMS), which is the main service for managing heterogeneous compute resources. 

The Python subpackage ``ansys.hps.client.rms`` wraps around the RMS service REST API available at ``https://hostname:port/hps/rms/api``.

APIs
--------------------------------------

RMS Api
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. autoclass:: ansys.hps.client.rms.RmsApi
   :members:
   :undoc-members:


Resources
--------------------------------------

Evaluator Registration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
 
.. autopydantic_model:: ansys.hps.client.rms.EvaluatorRegistration

Evaluator Configuration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
 
.. autopydantic_model:: ansys.hps.client.rms.EvaluatorConfiguration

Evaluator Configuration Update
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
 
.. autopydantic_model:: ansys.hps.client.rms.EvaluatorConfigurationUpdate

Scaler Configuration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
 
.. autopydantic_model:: ansys.hps.client.rms.ScalerRegistration

Compute Resource Set
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
 
.. autopydantic_model:: ansys.hps.client.rms.ComputeResourceSet
