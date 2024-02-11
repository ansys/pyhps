Resource Management Service (RMS)
=================================

Ansys HPS includes the Resource Management Service (RMS), which is the main service
for managing heterogeneous compute resources. 

The ``ansys.hps.client.rms`` Python subpackage wraps around the RMS REST API, which
is available at ``https://hostname:port/hps/rms/api``.

APIs
----

RMS API
^^^^^^^
.. autoclass:: ansys.hps.client.rms.RmsApi
   :members:
   :undoc-members:


Resources
---------

Evaluator registration
^^^^^^^^^^^^^^^^^^^^^^
 
.. autopydantic_model:: ansys.hps.client.rms.EvaluatorRegistration
   :model-show-json: False
   :model-show-config-summary: False
   :model-show-validator-members: False
   :model-show-validator-summary: False

Evaluator configuration
^^^^^^^^^^^^^^^^^^^^^^^
 
.. autopydantic_model:: ansys.hps.client.rms.EvaluatorConfiguration
   :model-show-json: False
   :model-show-config-summary: False
   :model-show-validator-members: False
   :model-show-validator-summary: False

Evaluator configuration update
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
 
.. autopydantic_model:: ansys.hps.client.rms.EvaluatorConfigurationUpdate
   :model-show-json: False
   :model-show-config-summary: False
   :model-show-validator-members: False
   :model-show-validator-summary: False

Scaler configuration
^^^^^^^^^^^^^^^^^^^^
 
.. autopydantic_model:: ansys.hps.client.rms.ScalerRegistration
   :model-show-json: False
   :model-show-config-summary: False
   :model-show-validator-members: False
   :model-show-validator-summary: False

Compute resource set
^^^^^^^^^^^^^^^^^^^^
 
.. autopydantic_model:: ansys.hps.client.rms.ComputeResourceSet
   :model-show-json: False
   :model-show-config-summary: False
   :model-show-validator-members: False
   :model-show-validator-summary: False

Cluster info
^^^^^^^^^^^^^^^^^^^^
 
.. autopydantic_model:: ansys.hps.client.rms.ClusterInfo
   :model-show-json: False
   :model-show-config-summary: False
   :model-show-validator-members: False
   :model-show-validator-summary: False
