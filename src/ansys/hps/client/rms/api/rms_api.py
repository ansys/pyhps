# Copyright (C) 2022 - 2025 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
"""Module wrapping around RMS root endpoints."""

import logging

from ansys.hps.client.client import Client
from ansys.hps.client.exceptions import ClientError
from ansys.hps.client.rms.models import (
    AnalyzeRequirements,
    AnalyzeResponse,
    ClusterInfo,
    ComputeResourceSet,
    EvaluatorConfiguration,
    EvaluatorConfigurationUpdate,
    EvaluatorRegistration,
    ScalerRegistration,
)

from .base import create_objects, get_object, get_objects, get_objects_count, object_to_json

log = logging.getLogger(__name__)


class RmsApi:
    """Wraps around the RMS root endpoints.

    Parameters
    ----------
    client : Client
        HPS client object.

    """

    def __init__(self, client: Client):
        """Initialize the ``RmsApi`` object."""
        self.client = client
        self._api_info = None

    @property
    def url(self) -> str:
        """URL of the API."""
        return f"{self.client.url}/rms/api/v1"

    def get_api_info(self):
        """Get information on the RMS API the client is connected to.

        The information includes the version and build date.
        """
        if self._api_info is None:
            r = self.client.session.get(self.url)
            self._api_info = r.json()
        return self._api_info

    @property
    def version(self) -> str:
        """API version."""
        return self.get_api_info()["build"]["version"]

    ################################################################
    # Evaluators
    def get_evaluators_count(self, **query_params) -> int:
        """Get the number of evaluators, optionally filtered by query parameters."""
        return get_objects_count(
            self.client.session, self.url, EvaluatorRegistration, **query_params
        )

    def get_evaluators(self, as_objects=True, **query_params) -> list[EvaluatorRegistration]:
        """Get a list of evaluators, optionally filtered by query parameters.

        The server only returns the first 10 objects (``limit=10``) by default.
        """
        return get_objects(
            self.client.session, self.url, EvaluatorRegistration, as_objects, **query_params
        )

    def get_evaluator_configuration(self, id: str, as_object=True) -> EvaluatorConfiguration:
        """Get an evaluator's configuration."""
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
        """Update an evaluator configuration.

        Examples
        --------
        Set a custom resource property on a Linux evaluator that was active in the past 60 seconds.

        >>> import datetime
        >>> from ansys.hps.client import Client
        >>> from ansys.hps.client.jms import RmsApi, EvaluatorConfigurationUpdate
        >>> cl = Client(
        ...     url="https://localhost:8443/hps", username="repuser", password="repuser"
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
        """Get the number of scalers, optionally filtered by query parameters."""
        return get_objects_count(self.client.session, self.url, ScalerRegistration, **query_params)

    def get_scalers(self, as_objects=True, **query_params) -> list[ScalerRegistration]:
        """Get a list of scalers, optionally filtered by query parameters.

        The server only returns the first 10 objects (``limit=10``) by default.
        """
        return get_objects(
            self.client.session, self.url, ScalerRegistration, as_objects, **query_params
        )

    ################################################################
    # Compute resource sets
    def get_compute_resource_sets_count(self, **query_params) -> int:
        """Get the number of compute resource sets, optionally filtered by query parameters."""
        return get_objects_count(self.client.session, self.url, ComputeResourceSet, **query_params)

    def get_compute_resource_sets(
        self, as_objects=True, **query_params
    ) -> list[ComputeResourceSet]:
        """Get a list of compute resource sets, optionally filtered by query parameters.

        The server only returns the first 10 objects (``limit=10``) by default.
        """
        return get_objects(
            self.client.session, self.url, ComputeResourceSet, as_objects, **query_params
        )

    def get_compute_resource_set(self, id, as_object=True) -> ComputeResourceSet:
        """Get a compute resource set."""
        return get_object(
            self.client.session,
            f"{self.url}/compute_resource_sets/{id}",
            ComputeResourceSet,
            as_object,
            from_collection=True,
        )

    def get_cluster_info(self, compute_resource_set_id, as_object=True) -> ClusterInfo:
        """Get the cluster information of a compute resource set."""
        return get_object(
            self.client.session,
            f"{self.url}/compute_resource_sets/{compute_resource_set_id}/cluster_info",
            ClusterInfo,
            as_object=as_object,
        )

    ################################################################
    # Analyze

    def analyze(
        self, requirements: AnalyzeRequirements, analytics: bool = False, as_object: bool = True
    ) -> AnalyzeResponse:
        """Compare resource requirements against available compute resources."""
        if requirements is None:
            raise ClientError("Requirements can't be None.")

        r = self.client.session.post(
            f"{self.url}/analyze",
            data=object_to_json(requirements),
            params={"analytics": analytics},
        )

        data = r.json()
        if not as_object:
            return data

        return AnalyzeResponse(**data)
