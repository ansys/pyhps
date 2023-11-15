import logging
from typing import List

from ansys.rep.client.client import Client
from ansys.rep.client.rms.models import EvaluatorRegistration

from .base import get_objects

log = logging.getLogger(__name__)


class RmsApi(object):
    """Wraps around the Resource Management Service root endpoints.

    Parameters
    ----------
    client : Client
        A REP client object.
    """

    def __init__(self, client: Client):
        self.client = client
        self._fs_url = None

    @property
    def url(self) -> str:
        """Returns the API url"""
        return f"{self.client.rep_url}/rms/api/v1"

    def get_api_info(self):
        """Return info like version, build date etc of the RMS API the client is connected to"""
        r = self.client.session.get(self.url)
        return r.json()

    ################################################################
    # Evaluators
    def get_evaluators(self, as_objects=True, **query_params) -> List[EvaluatorRegistration]:
        """Return a list of evaluators, optionally filtered by given query parameters"""
        return get_objects(
            self.client.session, self.url, EvaluatorRegistration, as_objects, **query_params
        )

    # def update_evaluators(
    #     self, evaluators: List[Evaluator], as_objects=True, **query_params
    # ) -> List[Evaluator]:
    #     """Update evaluators

    #     Examples
    #     --------

    #     You can request multiple evaluators configuration updates at once.
    #     This example shows how to set a custom resource property
    #     on all Linux evaluators that were active in the past 60 seconds.

    #     >>> import datetime
    #     >>> from ansys.rep.client import Client
    #     >>> from ansys.rep.client.jms import JmsApi, EvaluatorConfigurationUpdate
    #     >>> cl = Client(
    #     ...     rep_url="https://localhost:8443/rep", username="repuser", password="repuser"
    #     ... )
    #     >>> jms_api = JmsApi(cl)
    #     >>> query_params = {
    #     ...     "platform" : "linux",
    #     ...     "update_time.gt" : datetime.datetime.utcnow() - datetime.timedelta(seconds=60)
    #     ... }
    #     >>> evaluators = jms_api.get_evaluators(fields=["id", "host_id"], **query_params)
    #     >>> config_update = EvaluatorConfigurationUpdate(
    #     ...    custom_resource_properties={"disk_type" : "SSD"}
    #     ... )
    #     >>> for ev in evaluators:
    #     ...     ev.configuration_updates = config_update
    #     >>> evaluators = jms_api.update_evaluators(evaluators)

    #     """
    #     return update_objects(
    #         self.client.session, self.url, evaluators, Evaluator, as_objects, **query_params
    #     )
