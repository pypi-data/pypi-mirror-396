#!/usr/bin/env python3
"""
This module contains complete NETCONF config workflows from multiple nornir_collection functions.

The functions are ordered as followed:
- Complete NETCONF config workflows
"""

import time
from nornir.core import Nornir, Task
from nornir_collection.utils import (
    print_task_title,
    task_name,
    exit_info,
    task_error,
    exit_error,
)
from nornir_collection.cisco.configuration_management.restconf.config_workflow import rc_replace_config
from nornir_collection.cisco.configuration_management.netconf.config_tasks import (
    nc_cfg_cleanup,
    nc_cfg_tpl,
    nc_cfg_tpl_int,
)
from nornir_collection.cisco.configuration_management.netconf.ops_tasks import (
    # nc_lock,
    # nc_unlock,
    nc_validate,
    nc_discard,
    nc_commit,
)
from nornir_collection.cisco.configuration_management.restconf.cisco_rpc import (
    rc_cisco_rpc_is_syncing,
    rc_cisco_rpc_save_config,
)
from nornir_collection.cisco.configuration_management.processor import nr_testprocessor
from nornir_collection.cisco.configuration_management.cli.config_tasks import cli_confirm_or_revert_config


#### NETCONF config Workflow Helper #########################################################################


def _nc_exit_dry_run(nr: Task, cfg_status: bool, verbose: bool) -> None:
    """
    Handles the exit process for a NETCONF dry-run operation.
    This function performs the following steps:
    1. Discards all changes on the NETCONF candidate datastore.
    2. Unlocks the NETCONF datastore.
    3. Verifies the NETCONF dry-run status of the config results.
    4. Exits the script with an appropriate message based on the config status.

    !!! NETCONF lock/unlock rpc have been commented out as the unlock fails since 17.12.X !!!
    """

    # Discard all changes on the NETCONF candidate datastore
    nc_discard(nr=nr, verbose=verbose)

    # Unlock the NETCONF datastore
    # nc_unlock(nr=nr, verbose=verbose)

    # Verify NETCONF dry-run status of the config results and exit the script with a proper message
    task_text = "Verify NETCONF dry-run config results"
    msg = "-> The remaining tasks have been omitted due to the NETCONF dry-run execution"
    print_task_title(title=task_text)
    print(task_name(text=task_text))

    if cfg_status:
        text = "GOOD NEWS! ALL CONFIGS HAVE BEEN RENDERED AND VALIDATED SUCCESSFUL!"
        exit_info(task_text=task_text, text=text, msg=msg)
    else:
        text = "ALERT: ONE OR MORE CONFIGS HAVE FAILED!"
        exit_error(task_text=task_text, text=text, msg=msg)


def _verify_confirm_timeout(timer_start: float, confirm_timeout: int) -> bool:
    """
    TBD
    """
    # Set the end timer and calculate the remaining confirm-timeout
    timer_end = round(time.time() - timer_start, 1)
    remaining_timout = round(confirm_timeout - timer_end, 1)

    # If the remaining confirm-timeout is already over after or during the commit then most likely the
    # connection to the device was lost and the config-rollback happened.
    if remaining_timout <= 0:
        task_text = "NETCONF verify commit results"
        print(task_name(text=task_text))
        print(task_error(text=task_text, changed=False))
        print(f"'{task_text}' -> NornirResult <Success: False>")
        print(f"-> The remaining confirm-timeout is: {remaining_timout}s")
        print("  - The config confirm-timeout timed out after the commit!")
        print("  - Most likely the connection to the device was lost and the config-rollback happened!")
        print("  - The device is now in the previous state before the commit!")

        # Return False as the config-rollback timeout was already over after or during the commit
        return False

    # Return True and print nothing as everything is fine
    return True


#### NETCONF config Workflow ################################################################################


def nc_cfg_iosxe_netconf_config(
    nr: Nornir,
    rebuild: str = "golden-config",
    no_commit_confirm: bool = False,
    confirm_timeout: int = 120,
    dry_run: bool = False,
    verbose: bool = False,
) -> bool:
    """
    Configures an IOS-XE device using NETCONF. This function performs a series of config steps on an
    IOS-XE device using NETCONF. It handles locking the candidate datastore, applying different
    config templates, validating, and committing the changes. It also supports commit-confirm
    operations to run Nornir TestsProcessor device testing and dry-runs without commiting the config.

    !!! NETCONF lock/unlock rpc have been commented out as the unlock fails since 17.12.X !!!
    """
    print_task_title("Cleanup NETCONF candidate config")

    # Checks if a datastore sync in ongoing and wait until is finish. Default cfg_status argument is True
    cfg_status = rc_cisco_rpc_is_syncing(nr=nr, verbose=verbose)

    ########################################### WORKAROUND ##################################################
    ### It seems that since 17.12.4 the NETCONF server implementation has a bug !                         ###
    ### - The lock/unlock rpc is not working as expected.                                                 ###
    ### - The unlock rpc fails with an error message / The lock rpc is working as expected                ###
    ### - The lock is not needed for the config workflow. The lock is only needed for the rollback.       ###
    ### - There the NETCONF rollback-on-error is not working as expected.                                 ###
    ### -> Themporary workaround is to comment out the lock/unlock rpc and implement a rollback by CLI    ###
    #########################################################################################################
    # Lock the NETCONF candidate datastore
    # if not nc_lock(nr=nr, cfg_status=cfg_status, verbose=verbose):
    # return False

    # Cleanup configs which can't be done efficient with the Jinja2 template concept
    cfg_status = nc_cfg_cleanup(nr=nr, cfg_status=cfg_status, verbose=verbose)

    if cfg_status:
        print_task_title("Configure NETCONF candidate config")

    # Create a dict with the template startswith string and the task text as key-value pairs
    cfg_tasks = {
        "tpl_base": "NETCONF configure base system payload template",
        "tpl_sys": "NETCONF configure general system payload template",
    }
    # Configure NETCONF system config if cfg_status is still True
    cfg_status = nc_cfg_tpl(nr=nr, cfg_tasks=cfg_tasks, cfg_status=cfg_status, verbose=verbose)

    # Create a dict with the template startswith string and the task text as key-value pairs
    cfg_tasks = {
        "tpl_portchannel": "NETCONF configure portchannel interface payload template",
        "tpl_int": "NETCONF configure general interface payload template",
        "tpl_svi": "NETCONF configure vlan interface payload template",
    }
    # Continue NETCONF interface config if cfg_status is still True
    cfg_status = nc_cfg_tpl_int(nr=nr, cfg_tasks=cfg_tasks, cfg_status=cfg_status, verbose=verbose)

    # Print the task title basesd on the no_commit_confirm argument and set the commit variable
    if no_commit_confirm:
        print_task_title("Commit or discard NETCONF candidate config")
    else:
        print_task_title("Commit-confirm or discard NETCONF candidate config")

    # Validate NETCONF config if cfg_status is still True
    cfg_status = nc_validate(nr=nr, cfg_status=cfg_status, verbose=verbose)

    if dry_run:
        _nc_exit_dry_run(nr=nr, cfg_status=cfg_status, verbose=verbose)

    ########################################### WORKAROUND ##################################################
    # If its a commit-confirm and the cfg_status is True
    if not no_commit_confirm and cfg_status:
        # Replace the config with a revert-timer right before the commit
        cfg_status = rc_replace_config(nr=nr, rebuild=rebuild, verbose=verbose, revert_timer=confirm_timeout)
    #########################################################################################################

    # Start a timer to check how long the commit takes.
    timer_start = time.time()

    ########################################### WORKAROUND ##################################################
    ### Set confirm to 'False' with the RESTCONF workaround                                               ###
    #########################################################################################################
    # Commit all changes on the NETCONF candidate datastore if cfg_status is still True
    cfg_status = nc_commit(
        nr=nr,
        confirm=False,
        confirm_timeout=confirm_timeout,
        cfg_status=cfg_status,
        verbose=verbose,
    )

    # If the revert-timer is already over after or during the commit, then most likely the connection to the
    # device was lost and the config-rollback happened.
    if not no_commit_confirm:
        if not _verify_confirm_timeout(timer_start=timer_start, confirm_timeout=confirm_timeout):
            # Return False as the config-rollback timeout was already over after or during the commit
            # Return None as no cfgtp_results is available
            return False, None

    # Run some tests if its a commit-confirm no error happend on the commit
    if not no_commit_confirm and cfg_status:
        # Run the Nornir TestsProcessor test suite
        title = "Run Nornir TestsProcessor during NETCONF commit-confirm timeout"
        cfg_status, cfgtp_results = nr_testprocessor(nr=nr, title=title, after_config=True)

        print_task_title("Commit or discard NETCONF candidate config")

        ########################################### WORKAROUND ##############################################
        ### The is_syncing rpc and the second commit is not needed with the RESTCONF workaround           ###
        #####################################################################################################
        # Checks if an active datastore sync in ongoing and wait until is finish if cfg_status is True
        # cfg_status = rc_cisco_rpc_is_syncing(nr=nr, cfg_status=cfg_status, verbose=verbose)

        # Commit all changes on the NETCONF candidate datastore if cfg_status is still True
        # cfg_status = nc_commit(nr=nr, confirm=False, cfg_status=cfg_status, verbose=verbose)

        ########################################### WORKAROUND ##############################################
        # Confirm the revert-timer right after the commit
        cfg_status = cli_confirm_or_revert_config(
            nr=nr, action="confirm", cfg_status=cfg_status, verbose=verbose
        )
        #####################################################################################################

    # Discard the NETCONF config if there happen an error on the commit or commit confirm
    if not cfg_status:
        # Discard all changes on the NETCONF candidate datastore
        nc_discard(nr=nr, verbose=verbose)

        ########################################### WORKAROUND ##############################################
        # Revert the config right after the discard
        cli_confirm_or_revert_config(nr=nr, action="revert", cfg_status=True, verbose=verbose)
        #####################################################################################################
        # Unlock the NETCONF datastore
        # nc_unlock(nr=nr, verbose=verbose)

        # Return the cfg_status and None as no cfgtp_results is available
        return cfg_status, None

    # Unlock the NETCONF datastore
    # cfg_status = nc_unlock(nr=nr, cfg_status=cfg_status, verbose=verbose)

    # Checks if an active datastore sync in ongoing and wait until is finish if cfg_status is True
    cfg_status = rc_cisco_rpc_is_syncing(nr=nr, cfg_status=cfg_status, verbose=verbose)

    # Send the Cisco save config RESTCONF RPC if cfg_status is True
    cfg_status = rc_cisco_rpc_save_config(nr=nr, cfg_status=cfg_status, verbose=verbose)

    # Return the final cfg_status and the cfgtp_results dict
    return cfg_status, cfgtp_results
