#! /usr/local/bin/python3
# ----------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ----------------------------------------------------------------------------
# This script is used to install CEF agent on a linux machine an configure the
# syslog daemon on the linux machine.
# Supported OS:
#   64-bit
#       CentOS 6 and 7
#       Amazon Linux 2017.09
#       Oracle Linux 6 and 7
#       Red Hat Enterprise Linux Server 6 and 7
#       Debian GNU/Linux 8 and 9
#       Ubuntu Linux 14.04 LTS, 16.04 LTS and 18.04 LTS
#       SUSE Linux Enterprise Server 12
#   32-bit
#       CentOS 6
#       Oracle Linux 6
#       Red Hat Enterprise Linux Server 6
#       Debian GNU/Linux 8 and 9
#       Ubuntu Linux 14.04 LTS and 16.04 LTS
# For more information please check the OMS-Agent-for-Linux documentation.
#
# Daemon versions:
#   Syslog-ng: 2.1 - 3.22.1
#   Rsyslog: v8
import subprocess
import time
import sys


oms_agent_configuration_url = "https://raw.githubusercontent.com/microsoft/OMS-Agent-for-Linux/master/installer/conf/omsagent.d/security_events.conf"


def print_error(input_str):
    '''
    Print given text in red color for Error text
    :param input_str:
    '''
    print("\033[1;31;40m" + input_str + "\033[0m")


def print_ok(input_str):
    '''
    Print given text in green color for Ok text
    :param input_str:
    '''
    print("\033[1;32;40m" + input_str + "\033[0m")


def print_notice(input_str):
    '''
    Print given text in white background
    :param input_str:
    '''
    print("\033[0;30;47m" + input_str + "\033[0m")


def handle_error(e, error_response_str):
    error_output = e.decode('ascii')
    print_error(error_response_str)
    print_error(error_output)
    return False


def replace_filter_syslog_security():
    download_command = subprocess.Popen(["sudo", "wget", "-O", "/opt/microsoft/omsagent/plugin/filter_syslog_security.rb", "https://raw.githubusercontent.com/microsoft/OMS-Agent-for-Linux/master/source/code/plugins/filter_syslog_security.rb"], stdout=subprocess.PIPE)
    o, e = download_command.communicate()
    time.sleep(3)
    if e is not None:
        handle_error(e, error_response_str="Error: could not change filter_syslog_security.")
    else:
        print_ok("Replaced filter_syslog_security")


def replace_security_lib():
    download_command = subprocess.Popen(["sudo", "wget", "-O", "/opt/microsoft/omsagent/plugin/security_lib.rb", "https://raw.githubusercontent.com/microsoft/OMS-Agent-for-Linux/master/source/code/plugins/security_lib.rb"], stdout=subprocess.PIPE)
    o, e = download_command.communicate()
    time.sleep(3)
    if e is not None:
        handle_error(e, error_response_str="Error: could not change security_lib.")
    else:
        print_ok("Replaced security_lib")


def replace_files():
    replace_filter_syslog_security()
    replace_security_lib()


def set_omsagent_configuration(workspace_id):
    configuration_path = "/etc/opt/microsoft/omsagent/" + workspace_id + "/conf/omsagent.d/security_events.conf"
    command_tokens = ["sudo", "wget", "-O", configuration_path, oms_agent_configuration_url]
    set_omsagent_configuration_command = subprocess.Popen(command_tokens, stdout=subprocess.PIPE)
    o, e = set_omsagent_configuration_command.communicate()
    if e is not None:
        handle_error(e, error_response_str="Error: could not download omsagent configuration.")
        return False
    print_ok("Configuration for omsagent downloaded successfully.")


def restart_omsagent(workspace_id):
    print("Trying to restart omsagent")
    command_tokens = ["sudo", "/opt/microsoft/omsagent/bin/service_control", "restart", workspace_id]
    print_notice(" ".join(command_tokens))
    restart_omsagent_command = subprocess.Popen(command_tokens, stdout=subprocess.PIPE)
    time.sleep(3)
    o, e = restart_omsagent_command.communicate()
    if e is not None:
        handle_error(e, error_response_str="Error: could not restart omsagent")
        return False
    print_ok("Omsagent restarted successfully")
    return True


def main():
    if len(sys.argv) < 2:
        print_error("Error: The installation script is expecting 1 argument:")
        print_error("\t1) workspace id")
        return
    else:
        workspace_id = sys.argv[1]
        print("Workspace ID: " + workspace_id)
    replace_files()
    set_omsagent_configuration(workspace_id=workspace_id)
    restart_omsagent(workspace_id=workspace_id)
    print_ok("Installation completed")


main()
