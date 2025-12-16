#!/usr/bin/env python3
"""
This module contains functions regarding Nornir run with Processor.

The functions are ordered as followed:
- Helper Functions
- Nornir Processor Task in Functions
- Nornir Processor Print Functions
"""

import sys
import json
import time
import argparse
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from colorama import Style, init
from beautifultable import BeautifulTable
from nornir.core import Nornir
from nornir.core.task import AggregatedResult
from nornir_salt.plugins.processors import TestsProcessor
from nornir_salt.plugins.tasks import scrapli_send_commands
from nornir_collection.netbox.utils import nb_patch_data
from nornir_collection.utils import (
    print_task_title,
    task_name,
    print_task_name,
    task_host,
    task_info,
    task_result,
    list_flatten,
    load_multiple_yaml_files_to_string,
    print_result,
)

init(autoreset=True, strip=False)


#### Helper Functions #######################################################################################


def _filter_failed(cfgtp_result: AggregatedResult) -> dict[str, list]:
    """
    Return only failed test results per host.
    """
    return {
        host: [r for r in results if r.result != "PASS"] for host, results in cfgtp_result.items() if results
    }


def _testsprocessor_aggregated_result_to_dict(cfgtp_results: AggregatedResult) -> dict:
    output = {}
    for host, multi in cfgtp_results.items():
        output[host] = []
        for r in multi:
            # Set the required fields for each result, handling missing attributes gracefully
            output[host].append(
                {
                    "name": getattr(r, "name", None),
                    "task": getattr(r, "task", None),
                    "result": getattr(r, "result", None),
                    "criteria": getattr(r, "criteria", None),
                    "changed": getattr(r, "changed", False),
                    "failed": getattr(r, "failed", False),
                }
            )
    return output


#### Nornir Processor Task in Functions #####################################################################


def nr_testprocessor(nr: Nornir, title: str, after_config: bool) -> bool:
    """
    Executes a series of tests that can be used during a NETCONF commit-confirm timeout period or as
    as regression testing. This function starts a timer, runs tests using the Nornir TestsProcessor, and
    prints the results along with the time taken to complete the tests. If the tests are not successful, it
    waits for the specified confirm timeout period to expire.
    """

    # Start a timer to check how long the Nornir TestProcessor Task need
    timer_start = time.time()
    cfg_status = True

    print_task_title(title)

    if after_config:
        # Sleep for some seconds to allow the device to get into a stable state before the testing
        # e.g. Spanning-Tree convergence, OSPF adjacencies, etc.
        # Print a overall TestsProcessor result
        task_text = "PYTHON sleep some seconds before run TestsProcessor"
        print(task_name(text=task_text))
        print(task_result(text=task_text, changed=False, level_name="INFO"))
        print(f"'{task_text}' -> PythonResponse <Success: True>")
        print("-> Sleep 60s seconds before run the Nornir TestsProcessor ...")
        time.sleep(60)

    # Run Nornir TestsProcessor for Unit, Integration, and System tests. All tests files with the inventory
    # key starting with the prefix "cfgtp_{name}_" and are loaded from the inventory.
    # Run the Nornir TestsProcessor Task
    # fmt: off
    cfg_status_unit, cfgtp_result_unit = run_nr_testsprocessor(nr=nr, name="Unit", inv_key="cfgtp_unit_")
    cfg_status_integration, cfgtp_result_integration = run_nr_testsprocessor(nr=nr, name="Integration", inv_key="cfgtp_integration_")  # noqa: E501
    cfg_status_system, cfgtp_result_system = run_nr_testsprocessor(nr=nr, name="System", inv_key="cfgtp_system_")  # noqa: E501
    # fmt: on

    # Combine the three cfg_status results into one overall cfg_status
    if not cfg_status_unit or not cfg_status_integration or not cfg_status_system:
        cfg_status = False

    print_task_title(title="Verify Nornir TestsProcessor")

    # Print a overall TestsProcessor result
    task_text = "NORNIR overall TestsProcessor result"
    print(task_name(text=task_text))
    print(task_result(text=task_text, changed=False, level_name="INFO" if cfg_status else "ERROR"))
    print(f"'{task_text}' -> NornirResponse <Success: {'True' if cfg_status else 'False'}>")
    # Print the time which Nornir TestsProcessor needed
    exeeded_time = round(time.time() - timer_start, 1)
    print(f"-> Nornir TestsProcessor finished in: {exeeded_time}s")

    # Print a succcess message if all tests were successful and return
    if cfg_status:
        print("-> All TestsProcessor tests were successful ✅")
        # Return as no further details are needed
        return cfg_status, [cfgtp_result_unit, cfgtp_result_integration, cfgtp_result_system]

    # If tests failed then print all failed test results
    task_text = "NORNIR failed TestsProcessor result"
    print(task_name(text=task_text))

    # Create a dict of all TestsProcessor results grouped by suite
    suites = {
        "Unit": cfgtp_result_unit,
        "Integration": cfgtp_result_integration,
        "System": cfgtp_result_system,
    }
    # Filter the TestsProcessor results to contain only failed tests, grouped by suite
    failed_by_suite = {name: _filter_failed(res) for name, res in suites.items()}

    # Print only failed results, grouped by host and suite
    for host in nr.inventory.hosts.keys():
        has_failures = any(failed_by_suite[name].get(host) for name in failed_by_suite)
        if not has_failures:
            continue

        print(task_host(host=str(host), changed=False))
        for name, failed in failed_by_suite.items():
            if failed.get(host):
                print_testsprocessor_results(cfgtp_result=failed, name=name, print_host=host)

    # Return the overall status boolean and the list of all TestsProcessor results
    return cfg_status, [cfgtp_result_unit, cfgtp_result_integration, cfgtp_result_system]


def run_nr_testsprocessor(nr: Nornir, name: str, inv_key: str) -> bool:
    """
    This function filters the Nornir object by the string of the argument filter_tag and searches all values
    of the Nornir inventory which starts with the string of the argument inv_key. These values can be a
    string or a list of strings which are the TestProcessor test suite yaml files.
    As Nornir with processors works on the nr object level and not on the task level, it have to be ensured
    that all filtered hosts have access to all files or the TestsProcessor task will fail.
    The test suite yaml file supports all NornirSalt TestsProcessor values including Jinja2 host templating.
    """

    task_text = f"NORNIR prepare TestsProcessor '{name}'"
    print_task_name(task_text)

    # Create a list with the values of all inventory keys starting with a specific string
    file_list = []
    for host in nr.inventory.hosts.values():
        file_list += [value for key, value in host.items() if key.startswith(inv_key)]

    # Flatten the file_list if it contains lists of lists
    file_list = list_flatten(file_list)
    # Create a union of the files in the file_list -> no duplicate items
    file_list = list(set().union(file_list))

    # Load the test suite yaml files from file_list as one string to render jinja2 host inventory data
    yaml_string = load_multiple_yaml_files_to_string(file_list=file_list, silent=False)
    # Return False if the yaml_string is empty
    if not yaml_string:
        return False

    task_text = f"NORNIR run TestsProcessor '{name}'"
    print_task_name(task_text)

    # Add the nornir salt TestsProcessor processor
    # TestsProcessor expects a list, therefor each yaml string needs to be packed into a list
    # TestsProcessor templates the yaml string with Jinja2 and loads the yaml string into a dict
    nr_with_testsprocessor = nr.with_processors(
        [TestsProcessor(tests=[yaml_string], build_per_host_tests=True)]
    )

    # Collect output from the devices using scrapli send_commands task plugin
    try:
        cfgtp_result = nr_with_testsprocessor.run(task=scrapli_send_commands, on_failed=True)
    except ValueError:
        print(task_info(text=task_text, changed=False))
        print(f"'{task_text}' -> NornirResponse <Success: True>")
        print("-> Test files have no tests or are empty")
        return True

    # Print the TestsProcessor results
    cfg_status = print_testsprocessor_results(cfgtp_result=cfgtp_result, name=name)

    # Return the overall status boolean and the detailed Nornir TestsProcessor result
    return cfg_status, cfgtp_result


def nb_update_device_config_status(
    nr: Nornir, cfgtp_results: AggregatedResult, args: argparse.Namespace, after_config: bool
) -> bool:
    """
    This function updates the NetBox device config-status custom fields after a configuration or
    testprocessor run.
    If after_config is True, the function updates the fields:
        - config_uptodate: True
        - last_config: timestamp of the config
        - last_config_by: user who ran the config
    If after_config is False, the function only updates the field:
        - config_uptodate: True/False based on the TestsProcessor result
    """
    task_text = "Update NetBox device config-status"
    print_task_title(title=task_text)
    print(f"{task_name(text=task_text)}")

    # Set the timestamp for the last_config custom field
    timestamp = datetime.now(ZoneInfo("Europe/Zurich")).isoformat(timespec="seconds")
    timestamp_print = datetime.now(ZoneInfo("Europe/Zurich")).strftime("%Y-%m-%d %H:%M:%S")

    payload = []
    for host, inventory in nr.inventory.hosts.items():
        data = {}
        data["id"] = inventory.data["id"]
        data["custom_fields"] = {}
        config_uptodate = True
        # Check if all TestsProcessor tests have passed successfully
        if not after_config:
            for cfgtp_result in cfgtp_results:
                # Set config_uptodate based on the TestsProcessor result
                status = all("PASS" in result.result for result in cfgtp_result[host])
                if not status:
                    config_uptodate = False
                    break
        # Set the custom fields to update in NetBox
        data["custom_fields"]["config_uptodate"] = config_uptodate
        # Add config_uptodate to the host inventory data for further usage
        inventory.data["config_uptodate"] = config_uptodate
        # After config set the last_config and last_config_by custom fields; After test only config_uptodate
        # The timestamp is set to now with the user who ran the config.
        if after_config:
            data["custom_fields"]["last_config"] = timestamp
            data["custom_fields"]["last_config_by"] = args.user
            # Add last_config and last_config_by to the host inventory data for further usage
            inventory.data["last_config"] = timestamp
            inventory.data["last_config_by"] = args.user
        # Append the device data to the payload list
        payload.append(data)

    # Call the function to patch the device data in NetBox
    response, result = nb_patch_data(
        task_text=task_text,
        url=f"{nr.config.inventory.options['nb_url']}/api/dcim/devices/",
        payload=payload,
        text=None,
        verbose=args.verbose,
    )

    # Print the failed result if the response status code is not 200 and return False
    if response.status_code != 200:
        print(result)
        # Return False as the update have failed
        return False

    # Print the overall success result if after_config is True (meaning CFG-MGMT config was successful)
    if after_config:
        print(result)
        print(
            "-> Updated all configured devices custom fields in NetBox:\n",
            "   - 'config_uptodate': ✅ (True)\n",
            f"   - 'last_config': {timestamp_print} (config timestamp)\n",
            f"   - 'last_config_by': {args.user} (user who ran the config)",
        )
        # Return True as the update was successful
        return True

    # Else print the result for each device (meaning CFG-MGMT testprocessor run without config)
    for host in nr.inventory.hosts.keys():
        print(task_host(host=host, changed=False))
        print(result)
        print("-> Updated device custom fields in NetBox:")
        if nr.inventory.hosts[host].data["config_uptodate"]:
            print("   - 'config_uptodate': ✅ (True)")
        else:
            print("   - 'config_uptodate': ❌ (False)")

    # Return True as the update was successful
    return True


def create_testprocessor_pipeline_artifacts(
    nr: Nornir, cfgtp_results: list[AggregatedResult], args: argparse.Namespace
) -> None:
    """
    TBD
    """
    # Print the task title and name
    task_text = "Create Pipeline Artifacts"
    print_task_title(title=task_text)
    print(task_name(text=task_text))

    artifacts = {}
    for host, inventory in nr.inventory.hosts.items():
        # Initialize the artifacts dictionary for the host
        artifacts[host] = {}

        # Add some base information to the artifacts
        # fmt: off
        base_info = [
            "id", "url", "name", "device_type", "role", "tenant", "platform", "serial", "site",
            "location", "rack", "position", "status", "primary_ip", "virtual_chassis", "description",
            "comments", "tags"
        ]
        # fmt: on
        for item in base_info:
            artifacts[host][item] = inventory.data[item]

        # Add the interface name and its template to the artifacts
        artifacts[host]["interfaces"] = [
            {"name": interface["name"], "int_template": interface["int_template"]}
            for interface in inventory.data["interfaces"]
        ]

        # Add the config status to the artifacts
        artifacts[host]["config_uptodate"] = inventory.data["config_uptodate"]
        artifacts[host]["last_config"] = inventory.data["last_config"]
        artifacts[host]["last_config_by"] = inventory.data["last_config_by"]

        # Create a dictionary from the Nornir TestsProcessor AggregatedResult to enable JSON serialization
        cfgtp_unit_result_dict = _testsprocessor_aggregated_result_to_dict(cfgtp_results[0])
        cfgtp_integration_result_dict = _testsprocessor_aggregated_result_to_dict(cfgtp_results[1])
        cfgtp_system_result_dict = _testsprocessor_aggregated_result_to_dict(cfgtp_results[2])
        # Add the TestsProcessor results to the artifacts
        artifacts[host]["testsprocessor_results"] = {}
        artifacts[host]["testsprocessor_results"]["unit"] = cfgtp_unit_result_dict[host]
        artifacts[host]["testsprocessor_results"]["integration"] = cfgtp_integration_result_dict[host]
        artifacts[host]["testsprocessor_results"]["system"] = cfgtp_system_result_dict[host]

    # Base directory = directory of the main script being executed
    script_dir = Path(sys.argv[0]).resolve().parent
    artifacts_dir = script_dir / "artifacts" / "cfgtp_iosxe"
    artifacts_dir.mkdir(parents=True, exist_ok=True)  # nosec
    # Save JSON under the artifacts directory
    filename = f"testsprocessor_{args.artifact}.json"
    with open(artifacts_dir / filename, "w") as f:
        json.dump(artifacts, f, indent=4)

    # Print info message about the created artifact
    print(task_result(text=task_text, changed=False, level_name="INFO"))
    print(f"-> Created Pipeline Artifact: 'artifacts/cfgtp_iosxe/{filename}' for {len(artifacts)} devices")
    print(
        f"{Style.DIM}\x1b[3m\n"
        "Pipeline Artifact are used for Pipeline-to-Pipeline data sharing in Azure DevOps.\n"
        "This artifact contains all device information from NetBox and the Nornir TestsProcessor \n"
        "results to create the Zensical 'Switch CFG-MGMT Config-State' documentation page."
    )


#### Print Functions ########################################################################################


def print_testsprocessor_results(cfgtp_result: AggregatedResult, name: str, print_host: str = None) -> None:
    """
    This function prints a NornirSalt TestsProcessor result in a nice table with the library rich
    """
    # Track if the overall task has failed
    cfg_status = True

    # Print for each host a table with the Nornir testsprocessor result
    for host, multiresult in cfgtp_result.items():
        # Continue if a specific host is requested and it does not match the current host
        if print_host and host != print_host:
            continue
        if not print_host:
            # Print the host
            print(task_host(host=str(host), changed=False))
        # Print the overal TestsProcessor task result as INFO is all tests are successful, else ERROR
        level_name = "INFO" if all("PASS" in result.result for result in multiresult) else "ERROR"
        print(task_result(text=f"NORNIR run TestsProcessor '{name}'", changed=False, level_name=level_name))
        # Update the overall task status if the level name if ERROR
        if level_name == "ERROR":
            cfg_status = False

        try:
            # Create a table with the Python library beautifultable
            table = BeautifulTable()
            table.set_style(BeautifulTable.STYLE_NONE)
            table.columns.width = [50, 25, 10]
            table.columns.header = [
                f"{Style.BRIGHT}Name / Task",
                f"{Style.BRIGHT}Criteria / Test",
                f"{Style.BRIGHT}Result",
            ]
            # Create a custom table styling
            table.columns.header.separator = "-"
            table.columns.separator = "|"
            table.rows.separator = "-"
            table.columns.alignment = BeautifulTable.ALIGN_LEFT
            # Add a row for each test result
            for result in multiresult:
                # Expression test using evan have an empty criteria in the Nornir result
                if result.criteria:
                    criteria = f"{Style.DIM}\x1b[3m({result.test})\n{result.criteria}"
                else:
                    criteria = f"{Style.DIM}\x1b[3mCritera not available\n"
                    criteria += f"{Style.DIM}\x1b[3mfor this test"
                table.rows.append(
                    [
                        f"{Style.DIM}\x1b[3m({result.task})\n{result.name}",
                        f"{criteria}",
                        f"{result.result} ✅" if result.result == "PASS" else f"{result.result} ❌",
                    ]
                )
            # Print the TestProcessor result as beautifultable
            print(f"\n{table}")
        except:  # noqa: E722
            # Print the Nornir result to stdout
            print_result(multiresult)

    # Return a config status boolian True if all tests were successful or False if not
    return cfg_status
