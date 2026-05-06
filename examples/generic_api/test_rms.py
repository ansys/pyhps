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

"""
Example to submit a nonlinear tire analysis job to HPS.

This is the Ansys Parametric Design Language (APDL) Tire Performance Simulation example included
in the technology demonstration guide (td-57).
"""

import argparse
import logging
import time
from datetime import datetime

from ansys.hps.client import Client, HPSError
from ansys.hps.client.jms import Project
from ansys.hps.client.rms import ClusterInfo, ComputeResourceSet, RmsApi

log = logging.getLogger(__name__)


def filter_dict(input_dict, desired_keys=None):
    """
    Filters the input dictionary to only include the keys in desired_keys.

    Args:
    input_dict (dict): The dictionary to filter.
    desired_keys (list): A list of keys to retain in the filtered dictionary.

    Returns:
    dict: A new dictionary containing only the desired keys.
    """
    if desired_keys is None:
        desired_keys = ["evaluated", "pending", "failed", "running", "timeout"]
    return {key: input_dict[key] for key in desired_keys if key in input_dict}


def find_by_id(object_list, target_id):
    """
    Find an object in a list by its ID.

    :param object_list: List of objects (dictionaries or custom objects) to search.
    :param target_id: The ID to search for.
    :return: The object if found, otherwise None.
    """
    for obj in object_list:
        if isinstance(obj, dict) and "id" in obj:
            if obj["id"] == target_id:
                return obj
        elif hasattr(obj, "id"):
            if obj.id == target_id:
                return obj
    return None


# write
def show_rms_data(client: Client, verbose: bool, filter: str) -> Project:
    rms_api = RmsApi(client)
    broken_sets: dict[str, dict[str, tuple[ComputeResourceSet, ClusterInfo]]] = {}
    working_sets: dict[str, dict[str, tuple[ComputeResourceSet, ClusterInfo]]] = {}
    matched_sets = []
    try:
        if filter is not None:
            log.debug(f"Filtering CRS Sets based on name/id/config including: '{filter}'")

        scalers = rms_api.get_scalers()
        log.debug("=== Scalers")
        # pprint(scalers)
        crs_sets = rms_api.get_compute_resource_sets()
        log.debug("")
        log.debug("=== SCALERS ===")
        for scaler in scalers:
            broken_sets[scaler.id] = {}
            working_sets[scaler.id] = {}
            log.debug(
                f"    === Scaler info: {scaler.id}: {scaler.host_id}"
                + f" {scaler.host_name} version={scaler.build_info['version']}"
            )
            for crs in crs_sets:
                if crs.scaler_id == scaler.id:
                    print_crs_info(crs, rms_api, crs.scaler_id, verbose, broken_sets, working_sets)
                    matched_sets.append(crs)

        log.debug("")
        log.debug("=== Unmatched CRS Sets ===")
        for crs in crs_sets:
            if crs.id in [matched_set.id for matched_set in matched_sets]:
                continue  # already processed in the loop above

            log.debug(f"    === Scaler info: {crs.scaler_id}: NOT FOUND")

    except HPSError as e:
        log.error(str(e))
        log.error(e.response.content)

    log.debug("")
    log.debug("")
    log.debug("=== Failed RMS sets")
    duplicate_crs_sets = {}
    for scaler_id, crs_dict in broken_sets.items():
        # if the crs_dict is empty it means we didn't find any broken sets for the scaler.
        if not crs_dict:
            continue
        # If the working sets is > 0 it means there are multiple CRS sets for the scaler
        # and another one has properly configured queues.
        if any(working_sets[scaler_id]):
            duplicate_crs_sets[scaler_id] = crs_dict
            continue

        scaler = find_by_id(scalers, scaler_id)
        log.debug(
            f"    === Scaler info: {scaler.id}: {scaler.host_id} {scaler.host_name}"
            + f" version={scaler.build_info['version']}"
        )
        for _, (crs, info) in crs_dict.items():
            log.debug(f"     === {crs.name}: {crs.id}")
            if info:
                if info.queues:
                    for queue in info.queues:
                        log.debug(f"        === {queue.name}:")
                        for prop in queue.additional_props:
                            log.debug(f"            {prop}: {queue.additional_props[prop]}")
                else:
                    log.debug("        No queues available")
            else:
                log.debug("        No cluster info available")

        log.debug("")

    log.debug("")
    log.debug("")
    log.debug("=== Duplicate RMS sets")
    for scaler_id, crs_dict in duplicate_crs_sets.items():
        scaler = find_by_id(scalers, scaler_id)
        log.debug(
            f"    === Scaler info: {scaler.id}: {scaler.host_id} {scaler.host_name}"
            + f" version={scaler.build_info['version']}"
        )
        log.debug(
            "     === Multiple CRS sets found for this scaler, "
            + "but some without any queues presently configured."
        )
        for _, (crs, info) in crs_dict.items():
            log.debug(f"     === {crs.name}: {crs.id}")
            if info:
                if info.queues:
                    for queue in info.queues:
                        log.debug(f"        === {queue.name}:")
                        for prop in queue.additional_props:
                            log.debug(f"            {prop}: {queue.additional_props[prop]}")
                else:
                    log.debug("        No queues available")
            else:
                log.debug("        No cluster info available")

        log.debug("")

    log.debug("")


def print_crs_info(
    crs: ComputeResourceSet,
    rms_api,
    scaler_id,
    verbose,
    broken_sets: dict[str, dict[str, tuple[ComputeResourceSet, ClusterInfo]]],
    working_sets: dict[str, dict[str, tuple[ComputeResourceSet, ClusterInfo]]],
):
    # log.debug(f"   Config: {crs.backend.json()}")
    try:
        info: ClusterInfo = rms_api.get_cluster_info(crs.id)
        log.debug(f"       Cluster info: {crs.name}: {crs.id}")
    except Exception:
        log.warning(f"       Cluster info not available for {crs.name}")
        log.debug("")
        broken_sets[scaler_id][crs.id] = (crs, None)
        return

    for queue in info.queues:
        # Find all the node names in the queues node groups...
        all_node_names = set()
        for group in queue.node_groups:
            all_node_names.update(group.node_names)

        total_cores = 0
        reserved_cores = 0
        # Loop over all the node data and summarize the ones from this node group.
        for node in info.nodes:
            if node.name in all_node_names:
                if node.total_cores is not None and node.total_cores > 0:
                    total_cores += node.total_cores
                    if node.reserved_cores is not None and node.reserved_cores > 0:
                        reserved_cores += node.reserved_cores

        log.debug(f"        === {queue.name} -> {reserved_cores}/{total_cores}")
        if (
            "max_nodes" not in queue.additional_props
            or "supported_products" not in queue.additional_props
        ):
            broken_sets[scaler_id][crs.id] = (crs, info)
        else:
            working_sets[scaler_id][crs.id] = (crs, info)
        if verbose:
            for prop in queue.additional_props:
                log.debug(f"            {prop}: {queue.additional_props[prop]}")


def _main(log, show_rms_data, args):
    for url in args.urls:
        accounts = args.accounts
        if not any(args.accounts):
            accounts = [None]
        for account in accounts:
            if args.token:
                token = args.token
                client = Client(
                    url=url, access_token=token, verify=False if args.skip_verify else True
                )
                if account:
                    client.session.headers.update({"accountid": account})
            else:
                client = Client(
                    url=url,
                    username=args.username,
                    password=args.password,
                    verify=False if args.skip_verify else True,
                )

            try:
                log.info("")
                log.info(f"=== Url Specified     : {client.url}")
                log.info(f"=== Account Specified : {account}")
                show_rms_data(client=client, verbose=args.verbose, filter=args.filter)

            except HPSError as e:
                log.error(str(e))


def run_main_and_monitor(log, show_rms_data, _main, args):
    errors = {}
    while True:
        try:
            _main(log, show_rms_data, args)
        except Exception as e:
            exception = str(e)
            log.error(exception)
            key = exception[:150]
            # if key in errors:
            errors[key][str(datetime.now())] = exception
            # else:
            #    errors[key] = {str(datetime.now()): exception}

        log.info("")
        log.info("=== Logged errors")
        for _error, times in errors.items():
            log.info(f"---> {next(times.items())}")
            log.info(f"---> ---> {len(times)} times @ {times}")
        time.sleep(10)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-U", "--urls", nargs="+", default="https://localhost:8443/hps")
    parser.add_argument("-u", "--username", default="repuser")
    parser.add_argument("-p", "--password", default="repuser")
    parser.add_argument("-t", "--token", default="")
    parser.add_argument("-a", "--accounts", nargs="+", default="")
    parser.add_argument("-v", "--verbose", default=False)
    parser.add_argument("-m", "--monitor", default=False)
    parser.add_argument("-l", "--limited_monitor", default=False)
    parser.add_argument("-i", "--user_id", default="")
    parser.add_argument("-f", "--filter", default=None)
    parser.add_argument("-r", "--remove", default=None)

    parser.add_argument("--skip_verify", default=True, action=argparse.BooleanOptionalAction)

    args = parser.parse_args()

    logger = logging.getLogger()
    logging.basicConfig(format="[%(asctime)s | %(levelname)s] %(message)s", level=logging.DEBUG)

    if args.monitor or args.limited_monitor:
        run_main_and_monitor(log, show_rms_data, _main, args)
    else:
        _main(log, show_rms_data, args)
