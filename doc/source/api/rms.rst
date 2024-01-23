Resource management service
===========================

Ansys REP includes the Resource Management Service (RMS), which is the main service for managing heterogeneous compute resources. 

The Python subpackage ``ansys.hps.core.rms`` wraps around the RMS service REST API available at ``https://hostname:port/rep/rms/api``.

APIs
--------------------------------------

RMS API
^^^^^^^
.. autoclass:: ansys.hps.core.rms.RmsApi
   :members:
   :undoc-members:


Resources
---------

Evaluator registration
^^^^^^^^^^^^^^^^^^^^^^
 
.. autopydantic_model:: ansys.hps.core.rms.EvaluatorRegistration

Evaluator configuration
^^^^^^^^^^^^^^^^^^^^^^^
 
.. autopydantic_model:: ansys.hps.core.rms.EvaluatorConfiguration

Evaluator configuration update
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
 
.. autopydantic_model:: ansys.hps.core.rms.EvaluatorConfigurationUpdate

Scaler configuration
^^^^^^^^^^^^^^^^^^^^
 
.. autopydantic_model:: ansys.hps.core.rms.ScalerRegistration

Compute resource set
^^^^^^^^^^^^^^^^^^^^
 
.. autopydantic_model:: ansys.hps.core.rms.ComputeResourceSet
