# Copyright (C) 2022 - 2026 ANSYS, Inc. and/or its affiliates.
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

import logging

from ansys.hps.client.rms import RmsApi

log = logging.getLogger(__name__)


def test_scaler_integration(client):
    rms_api = RmsApi(client)
    scalers = rms_api.get_scalers(limit=1000)

    if scalers:
        log.debug(f"Found {len(scalers)} scalers")
        assert scalers[0].id is not None

    num_scalers = rms_api.get_scalers_count(limit=1000)
    assert num_scalers == len(scalers)

    scalers = rms_api.get_scalers(as_objects=False)
    if scalers:
        assert scalers[0]["id"] is not None

    scalers = rms_api.get_scalers(as_objects=True, fields=["host_name", "last_modified"])

    if scalers:
        assert scalers[0].host_name is not None
        assert scalers[0].last_modified is not None
        # todo: double check
        # assert scalers[0].id is None


def test_crs_integration(client):
    rms_api = RmsApi(client)
    resource_sets = rms_api.get_compute_resource_sets(limit=1000)

    if resource_sets:
        log.debug(f"Found {len(resource_sets)} resource sets")
        assert resource_sets[0].id is not None

    num_crs = rms_api.get_compute_resource_sets_count(limit=1000)
    assert num_crs == len(resource_sets)

    resource_sets = rms_api.get_compute_resource_sets(as_objects=False)
    if resource_sets:
        assert resource_sets[0]["id"] is not None
        assert resource_sets[0]["scaler_id"] is not None
        assert resource_sets[0]["last_modified"] is not None

    resource_sets = rms_api.get_compute_resource_sets(
        as_objects=True, fields=["id", "scaler_id", "last_modified"]
    )

    if resource_sets:
        assert resource_sets[0].scaler_id is not None
        assert resource_sets[0].last_modified is not None
        # todo: double check
        # assert resource_sets[0].name is None

        rs = rms_api.get_compute_resource_set(resource_sets[0].id)
        assert rs.scaler_id == resource_sets[0].scaler_id

        cluster_info = rms_api.get_cluster_info(rs.id)
        assert cluster_info.crs_id == rs.id
        if cluster_info.queues is not None and len(cluster_info.queues) > 0:
            for queue in cluster_info.queues:
                assert queue.name is not None
                log.info(f"Compute resource set {rs.name} has queue {queue.name}")
