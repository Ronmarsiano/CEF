
#! /usr/local/bin/python3
from xml.etree import ElementTree as et
import os
import sys
import subprocess


# workspace id + primary key + secondary key can be taken from the CEF configuration page in the sentinel page
# in azure portal
def download_install_oms_agent(workspace_id , primary_key , secondary_key):
    '''
    This will try to download 'onboard_agent.sh' from github if succeed it will be installed
    else check locally if the installation file is present if so install else will exit.
    :param workspace_id:
    :param primary_key:
    :param secondary_key:
    :return:
    '''
    file_name = "onboard_agent.sh"
    url = "https://raw.githubusercontent.com/Microsoft/OMS-Agent-for-Linux/master/installer/scripts/" + file_name
    download = subprocess.Popen(["wget", url], stdout=subprocess.PIPE)
    o,e = download.communicate()
    if e is not None:
        print("Could not download omsagent from: "+url)
        print("Checking file installation file[\""+file_name + "\"] in current directory ")
        if not check_file_in_directory(file_name):
            print("Could not locate installation file, program will exit.")
            sys.exit()
    install_oms_agent(workspace_id, primary_key, secondary_key, file_name)


def install_oms_agent(workspace_id , primary_key , secondary_key, file_name):
    '''
    Function will install the filename under the assumption that is is located in the current directory
    :param workspace_id:
    :param primary_key:
    :param secondary_key:
    :param file_name:
    :return: void
    '''
    sh = subprocess.Popen(["sh", file_name, "-w", workspace_id, "-s", primary_key, "-d", "opinsights.azure.com"])
    o, e = sh.communicate()
    if e is not None:
        error = e.decode('ascii')
        print("Could not install \"omsagent\" error:")
        print(error)


def check_file_in_directory(file_name):
    '''
    Check if the given file is found in the current directory.
    :param file_name:
    :return: return True if it is found elsewhere False
    '''
    current_dir = subprocess.Popen(["ls", "-ltrh"], stdout=subprocess.PIPE)
    grep = subprocess.Popen(["grep", "-i", file_name], stdin=current_dir.stdout, stdout=subprocess.PIPE)
    o, e = grep.communicate()
    output = o.decode('ascii')
    if e is not None and file_name in output:
        print("Found \"" + file_name + "\".")
        return True
    print("Could not find \"" + file_name + "\".")
    return False


def locate_check(process_name):
    '''
    Check if the process_name is installed using the locate command
    :param process_name:
    :return: True if locate has returned a valid value else False
    '''
    locate = subprocess.Popen(["locate", process_name], stdout=subprocess.PIPE)
    o, e = locate.communicate()
    response = o.decode('ascii')
    if e is not None:
        print("Could not execute \'locate\' command.")
        print("To install locate command - \"sudo yum install mlocate[On CentOS/RHEL]\" or \"sudo apt"
              " install mlocate[On Debian/Ubuntu] \"")
    elif response == "":
        print("Could not locate \'omsagent\' trying to validate by checking the process.\n")
        return False
    else:
        print("located \'omsagent\'")
        return True


def omsagent_process_check(oms_process_name):
    tokens = process_check(oms_process_name)
    if len(tokens) > 1:
        for single_token in tokens:
            if "opt/microsoft/omsagent" in single_token:
                print("Found omsagent process running on this machine.")
                return True
    print("Could not find omsagent process running on this machine.")

    return False


def process_check(process_name):
    '''
    function who check using the ps -ef command if the 'process_name' is running
    :param process_name:
    :return: True if the process is running else False
    '''
    p1 = subprocess.Popen(["ps", "-ef"], stdout=subprocess.PIPE)
    p2 = subprocess.Popen(["grep", "-i", process_name], stdin=p1.stdout, stdout=subprocess.PIPE)
    o, e = p2.communicate()
    tokens = o.decode('ascii').split('\n')
    tokens.remove('')
    return tokens


def check_oms_agent_and_install(workspace_id, primary_key, secondary_key):
    '''
    function to check if the OMS agent is instlalled if not it will
    try to download or locate a local installation file in the same directory as this script
    and install it.
    the parameters can be fetched from the azure portal
    :param workspace_id:
    :param primary_key:
    :param secondary_key:
    :return: Void
    '''
    if not check_oms_agent_status():
        print("Downloading and installing omsagent")
    download_install_oms_agent(workspace_id, primary_key, secondary_key)


def check_oms_agent_status():
    '''
        Checking if the OMS agent is installed and running this is done by:
        1. using the locate command if one is installed
        2. using pe -ef - will check if the agent is running

        :return: True if the process is installed and/or running false elsewhere
    '''
    agent_name = "omsagent"
    is_located = locate_check(agent_name)
    is_process_running = process_check(agent_name)

    if not is_located and not is_process_running:
        print("Oms agent is not installed or running on this machine")
        return False
    else:
        return True


def is_rsyslog():
    tokens = process_check("rsyslog")
    if len(tokens) > 1 :
        for single_token in tokens:
            if "/usr/sbin/rsyslog" in single_token:
                print("Found rsyslog process running on this machine.")
                return True
    return False


def main():
    if len(sys.argv) != 4:
        print("The installation script is expecting 3 arguments:")
        print("1) workspace id")
        print("2) primary key")
        print("3) secondary key")
        return
    else:
        workspace_id = sys.argv[1]
        primary_key = sys.argv[2]
        secondary_key = sys.argv[3]

    print("enter the following:")
    print("1 - install")
    print("2 - troubleshooting")
    print("0 - exit")
    while True:
        try:
            user_choice = input("Enter number of choice:\n")
            if isinstance(user_choice, int):
                if user_choice == 1:
                    check_oms_agent_and_install(workspace_id, primary_key, secondary_key)
                elif user_choice == 2:
                    check_oms_agent_status()
                elif user_choice == 0:
                    return
        except NameError:
            print("Enter a valid number.")

main()