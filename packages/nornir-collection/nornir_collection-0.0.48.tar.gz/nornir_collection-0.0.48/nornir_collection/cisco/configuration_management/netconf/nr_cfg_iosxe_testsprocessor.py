#!/usr/bin/env python3
"""
This module runs the same Nornir TestsProcessor as during the complete configuration management workflow for
Cisco IOS-XE devices. It's intended to be used as regression test after a configuration change to ensure that
the device is still working as expected. The Main function is intended to import and execute by other scripts.
"""

import argparse
from nornir.core.filter import F
from nornir_collection.nornir_plugins.inventory.utils import init_nornir
from nornir_collection.cisco.configuration_management.processor import (
    nr_testprocessor,
    nb_update_device_config_status,
    create_testprocessor_pipeline_artifacts,
)
from nornir_collection.utils import (
    print_task_title,
    task_name,
    task_info,
    task_error,
    exit_info,
    exit_error,
)


__author__ = "Willi Kubny"
__maintainer__ = "Willi Kubny"
__version__ = "1.0"
__license__ = "MIT"
__email__ = "willi.kubny@dreyfusbank.ch"
__status__ = "Production"


def main(nr_config: str, args: argparse.Namespace) -> None:
    """
    Main function is intended to import and execute by other scripts.
    It initialize Nornir and runs the custom TestsProcessor on Cisco IOS-XE devices.

    * Args:
        * nr_config (str): Path to the Nornir config file.
        * args (argparse.Namespace): Command-line arguments parsed by argparse.

    * Steps:
        * Initialize Nornir
        * Verify that all filtered devices that have the tag slug 'cfg-mgmt'
        * Run Nornir TestsProcessor for regression testing
        * Update the NetBox device config-status custom fields
        * Print the final overall result message

    * Exits:
        * It exits with appropriate messages and statuses based on the success or failure of each step.
    """

    #### Initialize Script and Nornir #######################################################################

    # Initialize, transform and filter the Nornir inventory are return the filtered Nornir object
    # Define data to load from NetBox in addition to the base Nornir inventory plugin
    add_netbox_data = {"load_virtual_chassis_data": True, "load_interface_data": True, "load_vlan_data": True}
    nr = init_nornir(config_file=nr_config, args=args, add_netbox_data=add_netbox_data)

    # Filter the Nornir inventory again only with devices that have the tag name 'CFG-MGMT' and compare the
    # filtered inventory with the original inventory to prevent the script from running on devices that are
    # not intended for config management
    print_task_title(title="Verify Nornir inventory filter for CFG-MGMT")
    task_text = "NORNIR verify inventory filter for CFG-MGMT"
    print(task_name(text=task_text))
    # Filter the Nornir inventory with devices that have the tag 'CFG-MGMT'
    nr_cfg_mgmt = nr.filter(F(tags__contains="CFG-MGMT"))
    # Exit the script if the filtered inventory does not match the original inventory
    if len(nr.inventory.hosts) != len(nr_cfg_mgmt.inventory.hosts):
        print(task_error(text=task_text, changed=False))
        print(f"'{task_text}' -> NornirResult <Success: False>")
        exit_error(
            task_text=task_text,
            text="ALERT: INVENTORY FILTER MISMATCH FOR CFG-MGMT!",
            msg=[
                "-> The filtered inventory does not match the original inventory",
                "-> Ensure all devices intended for config management are tagged with 'CFG-MGMT'",
            ],
        )
    print(task_info(text=task_text, changed=False))
    print(f"'{task_text}' -> NornirResponse <Success: True>")
    print("-> All filtered devices are tagged with 'CFG-MGMT'")

    #### Run Nornir TestsProcessor Regression-Test ##########################################################

    # Run the Nornir TestsProcessor test suite
    title = "Run Nornir TestsProcessor regression-test"
    cfgtp_status, cfgtp_results = nr_testprocessor(nr=nr, title=title, after_config=False)

    ### Update NetBox Config-Status with the TestsProcessor Results ########################################

    # Update the NetBox device config-status custom fields with the TestsProcessor Results
    nb_status = nb_update_device_config_status(
        nr=nr, cfgtp_results=cfgtp_results, args=args, after_config=False
    )

    # The cfgtp_status is True only if all TestsProcessor tests have passed successfully.
    # Therefor first check that the update of the NetBox config-status was successful and then
    # return the overall status.
    if not nb_status:
        task_text = "Verify NetBox device config-status"
        print_task_title(title=task_text)
        print(f"{task_name(text=task_text)}")
        exit_error(
            task_text=task_text,
            text="BAD NEWS! NETBOX CONFIG-STATUS UPDATE HAVE FAILED!",
            msg=[
                "-> NetBox API device config-status update have failed",
                "-> Check the NetBox API response for more details",
            ],
        )

    ### Create Pipeline Artifacts ###########################################################################

    # Create the TestProcessor pipeline artifacts if the argument is set.
    # Artifacts will be created in the working directory with the subfolder name of the argument value.
    # This is intended to be used for Pipeline-to-Pipeline data sharing in Azure DevOps.
    if args.artifact:
        create_testprocessor_pipeline_artifacts(nr=nr, cfgtp_results=cfgtp_results, args=args)

    ### Print the final overall result message ##############################################################

    # Print the final message about the overall results of the TestProcessor regression testing
    task_text = "Verify Nornir TestsProcessor regression-tests"
    print_task_title(title=task_text)
    print(f"{task_name(text=task_text)}")
    if cfgtp_status:
        exit_info(
            task_text=task_text,
            text="GOOD NEWS! ALL TESTS HAVE PASSED SUCCESSFULLY & NETBOX CONFIG-STATUS IS UPDATED!",
            msg=[
                "-> The NetBox device config-status is updated",
                "-> The device configuration is sync with NetBox and Git",
            ],
        )
    else:
        exit_error(
            task_text=task_text,
            text="BAD NEWS! NETBOX CONFIG-STATUS IS UPDATED, BUT SOME TESTS HAVE FAILED!",
            msg=[
                "-> The NetBox device config-status is updated",
                "-> The device configuration is not in sync with NetBox and Git",
                "-> The failed tests must be investigated and the device needs a CFG-MGMT pipeline re-run",
            ],
            fail_soft=True,  # Do not exit with error code 1 to not fail CI/CD pipelines
        )
