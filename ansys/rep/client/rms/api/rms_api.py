import logging
from typing import List

from ansys.rep.client.client import Client
from ansys.rep.client.rms.models import (
    Cluster,
    ComputeResourceSet,
    EvaluatorConfiguration,
    EvaluatorConfigurationUpdate,
    EvaluatorRegistration,
    ScalerRegistration,
)

from .base import create_objects, get_object, get_objects, get_objects_count

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
    def get_evaluators_count(self, **query_params) -> int:
        """Return the number of evaluators (optionally filtered by given query parameters)"""
        return get_objects_count(
            self.client.session, self.url, EvaluatorRegistration, **query_params
        )

    def get_evaluators(self, as_objects=True, **query_params) -> List[EvaluatorRegistration]:
        """Return a list of evaluators, optionally filtered by given query parameters.

        Note: by default the server only returns the first 10 objects (limit=10).
        """
        return get_objects(
            self.client.session, self.url, EvaluatorRegistration, as_objects, **query_params
        )

    def get_evaluator_configuration(self, id: str, as_object=True) -> EvaluatorConfiguration:
        """Return an evaluator's configuration"""
        return get_object(
            self.client.session,
            f"{self.url}/evaluators/{id}/configuration",
            EvaluatorConfiguration,
            id=id,
            as_object=as_object,
        )

    def update_evaluator_configuration(
        self, id: str, configuration: EvaluatorConfigurationUpdate, as_object=True
    ) -> EvaluatorConfigurationUpdate:
        """Update evaluators

        Examples
        --------

        This example shows how to set a custom resource property
        on a Linux evaluator that was active in the past 60 seconds.

        >>> import datetime
        >>> from ansys.rep.client import Client
        >>> from ansys.rep.client.jms import RmsApi, EvaluatorConfigurationUpdate
        >>> cl = Client(
        ...     rep_url="https://localhost:8443/rep", username="repuser", password="repuser"
        ... )
        >>> rms_api = RmsApi(cl)
        >>> query_params = {
        ...     "platform" : "linux",
        ...     "update_time.gt" : datetime.datetime.utcnow() - datetime.timedelta(seconds=60)
        ... }
        >>> evaluator = rms_api.get_evaluators(fields=["id", "host_id"], **query_params)[0]
        >>> config_update = EvaluatorConfigurationUpdate(
        ...    custom_resource_properties={"disk_type" : "SSD"}
        ... )
        >>> rms_api.update_evaluator_configuration(ev.id, config_update)

        """
        return create_objects(
            self.client.session, f"{self.url}/evaluators/{id}", [configuration], as_object
        )[0]

    ################################################################
    # Scalers
    def get_scalers_count(self, **query_params) -> int:
        """Return the number of scalers (optionally filtered by given query parameters)"""
        return get_objects_count(self.client.session, self.url, ScalerRegistration, **query_params)

    def get_scalers(self, as_objects=True, **query_params) -> List[ScalerRegistration]:
        """Return a list of scalers, optionally filtered by given query parameters.

        Note: by default the server only returns the first 10 objects (limit=10).
        """
        return get_objects(
            self.client.session, self.url, ScalerRegistration, as_objects, **query_params
        )

    ################################################################
    # Compute resource sets
    def get_compute_resource_sets_count(self, **query_params) -> int:
        """Return the number of compute resource sets

        Optionally filtered by given query parameters.
        """
        return get_objects_count(self.client.session, self.url, ComputeResourceSet, **query_params)

    def get_compute_resource_sets(
        self, as_objects=True, **query_params
    ) -> List[ComputeResourceSet]:
        """Return a list of compute resource sets.

        Optionally filtered by given query parameters.
        Note: by default the server only returns the first 10 objects (limit=10).
        """
        return get_objects(
            self.client.session, self.url, ComputeResourceSet, as_objects, **query_params
        )

    def get_compute_resource_set(self, id, as_object=True) -> ComputeResourceSet:
        """Returns a compute resource set."""
        return get_object(
            self.client.session,
            f"{self.url}/compute_resource_sets/{id}",
            ComputeResourceSet,
            as_object,
            from_collection=True,
        )

    def get_compute_resurce_set_cluster_info(self, id, as_object=True) -> Cluster:
        """Returns cluster info of a compute resource set."""

        clusters = get_objects(
            self.client.session,
            self.url,
            ComputeResourceSet,
            as_object,
            crs_id=id,
        )
        return clusters[0]
