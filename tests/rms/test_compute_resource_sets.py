import logging
import unittest

from ansys.rep.client.rms import RmsApi
from tests.rep_test import REPTestCase

log = logging.getLogger(__name__)


class ComputeResourceSetTest(REPTestCase):
    def test_scaler_integration(self):

        client = self.client
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

    def test_crs_integration(self):

        client = self.client
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


if __name__ == "__main__":
    unittest.main()
