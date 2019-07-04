#! /usr/local/bin/python3
import subprocess
import time
import sys, getopt
import fileinput

rsyslog_daemon_name = "rsyslog"
syslogng_daemon_name = "syslog-ng"
oms_agent_file_name = "onboard_agent.sh"
oms_agent_url = "https://raw.githubusercontent.com/Microsoft/OMS-Agent-for-Linux/master/installer/scripts/" + oms_agent_file_name
help_text = "Optional arguments for the python script are:\n\t-T: for TCP\n\t-U: for UDP which is the default value.\n\t-F: for no facility restrictions.\n\t-p: for changing default port from 25226"
omsagent_default_incoming_port = "25226"


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


def print_warning(input_str):
    '''
    Print given text in yellow color for warning text
    :param input_str:
    '''
    print("\033[1;33;40m" + input_str + "\033[0m")


def print_notice(input_str):
    '''
    Print given text in white background
    :param input_str:
    '''
    print("\033[0;30;47m" + input_str + "\033[0m")


def print_command_response(input_str):
    '''
    Print given text in green color for Ok text
    :param input_str:
    '''
    print("\033[1;34;40m" + input_str + "\033[0m")


def download_omsagent():
    '''
    Download omsagent this downloaded file would be installed
    :return: True if downloaded sccessfully
    '''
    print("Trying to download the omsagent.")
    print_notice("wget " + oms_agent_url)
    download_command = subprocess.Popen(["wget", oms_agent_url], stdout=subprocess.PIPE)
    o, e = download_command.communicate()
    time.sleep(3)
    if e is not None:
        error_output = e.decode('ascii')
        print_error("Error: could not download omsagent.")
        print_error(error_output)
        return False
    print_ok("Downloaded omsagent successfully.")
    return True


def install_omsagent(workspace_id, primary_key):
    '''
    Installing the downloaded omsagent
    :param workspace_id:
    :param primary_key:
    :return:
    '''
    command_tokens = ["sh", oms_agent_file_name, "-w", workspace_id, "-s", primary_key, "-d", "opinsights.azure.com"]
    print_notice(" ".join(command_tokens))
    install_omsagent_command = subprocess.Popen(command_tokens, stdout=subprocess.PIPE)
    o, e = install_omsagent_command.communicate()
    time.sleep(3)
    if e is not None:
        error_output = e.decode('ascii')
        print_error("Error: could not install omsagent.")
        print_error(error_output)
        return False
    print_ok("Installed omsagent successfully.")
    return True


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


def create_rsyslog_daemon_forwarding_configuration(facility_restrictions, omsagent_incoming_port):
    print("Creating rsyslog daemon configuration.")
    print("Configuration is changed to forward daemon incoming syslog messages into the omsagent.")
    time.sleep(3)
    if facility_restrictions:
        command_tokens = ["sudo", "bash", "-c", "printf 'local4.debug @127.0.0.1:" + omsagent_incoming_port + "' > /etc/rsyslog.d/security-config-omsagent.conf"]
        print_notice("Writing configuration - "+" ".join(command_tokens))
    else:
        command_tokens = ["sudo", "bash", "-c", "printf '*.* @127.0.0.1:" + omsagent_incoming_port + "' > /etc/rsyslog.d/security-config-omsagent.conf"]
        print_notice("Writing configuration with no facility restrictions - " + " ".join(command_tokens))
    set_daemon_configuration = subprocess.Popen(command_tokens, stdout=subprocess.PIPE)
    o, e = set_daemon_configuration.communicate()
    if e is not None:
        error_output = e.decode('ascii')
        print_error("Error: could not change daemon configuration.")
        print_error(error_output)
        return False
    print_ok("Configuration for rsyslog daemon was changed successfully..")
    return True


def set_omsagent_configuration(workspace_id, omsagent_incoming_port, tcp, udp):
    '''
    Download the omsagent configuration and then change the omsagent incoming port
    if required and change the protocol if required
    :param workspace_id:
    :param omsagent_incoming_port:
    :param tcp:
    :param udp:
    :return:
    '''
    configuration_path = "/etc/opt/microsoft/omsagent/" + workspace_id + "/conf/omsagent.d/security_events.conf"
    print("Creating omsagent configuration to listen to syslog daemon forwarding port - " + omsagent_incoming_port)
    print("Configuration location is - " + configuration_path)
    command_tokens = ["sudo", "wget", "-O", configuration_path, "https://aka.ms/syslog-config-file-linux"]
    print("Download configuration into the correct directory")
    print_notice(" ".join(command_tokens))
    time.sleep(3)
    set_omsagent_configuration_command = subprocess.Popen(command_tokens, stdout=subprocess.PIPE)
    o, e = set_omsagent_configuration_command.communicate()
    if e is not None:
        error_output = e.decode('ascii')
        print_error("Error: could not download omsagent configuration.")
        print_error(error_output)
        return False
    print_ok("Configuration for omsagent downloaded successfully.")
    print("Trying to changed omsagent configuration")
    if omsagent_incoming_port is not omsagent_default_incoming_port:
        if change_omsagent_configuration_port(omsagent_incoming_port=omsagent_incoming_port, configuration_path=configuration_path):
            print_ok("Incoming port for omsagent was changed to " + omsagent_incoming_port)
        else:
            print_error("Could not change omsagent incoming port")
    if change_omsagent_protocol(tcp=tcp, udp=udp, configuration_path=configuration_path):
        print_ok("Finished changing omsagent configuration")
        return True
    else:
        print_error("Could not change the omsagent configuration")
        return False


def change_omsagent_protocol(tcp, udp, configuration_path):
    '''
    Changing the omsagent protocol, since the protocol type is set on the omsagent
    configuration file
    :param tcp:
    :param udp:
    :param configuration_path:
    '''
    with open(configuration_path, "rt") as fin:
        with open("tmp.txt", "wt") as fout:
            for line in fin:
                if "protocol_type" in line and tcp is True and "tcp" not in line:
                    fout.write(line.replace("udp", "tcp"))
                    print_notice("Changing protocol type from udp to tcp in "+configuration_path)
                    print("Line changed: " + line)
                elif "protocol_type" in line and udp is True and "udp" not in line:
                    fout.write(line.replace("tcp", "udp"))
                    print_notice("Changing protocol type from tcp to udp in " + configuration_path)
                    print("Line changed: " + line)
                elif "bind" in line and tcp is True and "0.0.0.0" not in line:
                    fout.write(line.replace("127.0.0.1", "0.0.0.0"))
                    print_notice("Changing bind property for tcp protocol in " + configuration_path)
                    print("Line changed: " + line)
                elif "bind" in line and udp is True and "127.0.0.1" not in line:
                    fout.write(line.replace("0.0.0.0", "127.0.0.1"))
                    print_notice("Changing bind property for udp protocol in " + configuration_path)
                    print("Line changed: " + line)
                else:
                    fout.write(line)
    command_tokens = ["sudo", "mv", "tmp.txt", configuration_path]
    write_new_content = subprocess.Popen(command_tokens, stdout=subprocess.PIPE)
    time.sleep(3)
    o, e = write_new_content.communicate()
    if e is not None:
        error_output = e.decode('ascii')
        print_error("Error: could not change omsagent configuration port in ." + configuration_path)
        print_error(error_output)
        return False
    print_ok("Omsagent configuration was changed to fit required protocol - " + configuration_path)
    return True


def change_omsagent_configuration_port(omsagent_incoming_port, configuration_path):
    '''
    Changing the omsagent configuration port if required
    :param omsagent_incoming_port:
    :param configuration_path:
    '''
    with open(configuration_path, "rt") as fin:
        with open("tmp.txt", "wt") as fout:
            for line in fin:
                fout.write(line.replace(omsagent_default_incoming_port, omsagent_incoming_port))
    command_tokens = ["sudo", "mv", "tmp.txt", configuration_path]
    write_new_content = subprocess.Popen(command_tokens, stdout=subprocess.PIPE)
    time.sleep(3)
    o, e = write_new_content.communicate()
    if e is not None:
        error_output = e.decode('ascii')
        print_error("Error: could not change omsagent configuration port in ." + configuration_path)
        print_error(error_output)
        return False
    print_ok("Omsagent incoming port was changed in configuration - " + configuration_path)
    return True


def restart_rsyslog():
    '''
    Restart the resyslog daemon
    '''
    print("Restarting rsyslog daemon.")
    command_tokens = ["sudo", "service", "rsyslog", "restart"]
    print_notice(" ".join(command_tokens))
    restart_rsyslog_command = subprocess.Popen(command_tokens, stdout=subprocess.PIPE)
    time.sleep(3)
    o, e = restart_rsyslog_command.communicate()
    if e is not None:
        error_output = e.decode('ascii')
        print_error("Error: could not restart rsyslog daemon")
        print_error(error_output)
        return False
    print_ok("Rsyslog daemon restarted successfully")
    return True


def restart_omsagent(workspace_id):
    '''
    Restart the omsagent
    :param workspace_id:
    '''
    print("Trying to restart omsagent")
    command_tokens = ["sudo", "/opt/microsoft/omsagent/bin/service_control", "restart", workspace_id]
    print_notice(" ".join(command_tokens))
    restart_omsagent_command = subprocess.Popen(command_tokens, stdout=subprocess.PIPE)
    time.sleep(3)
    o, e = restart_omsagent_command.communicate()
    if e is not None:
        error_output = e.decode('ascii')
        print_error("Error: could not restart omsagent")
        print_error(error_output)
        return False
    print_ok("Omsagent restarted successfully")
    return True


def is_rsyslog():
    '''
    Returns True if the daemon is 'Rsyslog'
    '''
    # Meaning ps -ef | grep "daemon name" has returned more then the grep result
    return process_check(rsyslog_daemon_name) > 1


def is_syslog_ng():
    '''
    Returns True if the daemon is 'Syslogng'
    '''
    # Meaning ps -ef | grep "daemon name" has returned more then the grep result
    return process_check(syslogng_daemon_name) > 1


def main():
    tcp = False
    udp = False
    facility_restrictions = True
    omsagent_incoming_port = omsagent_default_incoming_port
    port_argument = False
    if len(sys.argv) < 3:
        print_error("Error: The installation script is expecting 2 arguments:")
        print_error("\t1) workspace id")
        print_error("\t2) primary key")
        return
    else:
        workspace_id = sys.argv[1]
        primary_key = sys.argv[2]
        print("Workspace ID: " + workspace_id)
        print("Primary key: " + primary_key)
        if len(sys.argv) > 3:
            for index in range(3, len(sys.argv)):
                if "-T" in sys.argv[index]:
                    print_notice("Notice: selected communication protocol is TCP")
                    tcp = True
                elif "-U" in sys.argv[index]:
                    print_notice("Notice: selected communication protocol is UDP")
                    udp = True
                elif "-F" in sys.argv[index]:
                    print_notice("Notice: no facility restrictions")
                    facility_restrictions = False
                elif "-p" in sys.argv[index]:
                    port_argument = True
                elif port_argument:
                    omsagent_incoming_port = sys.argv[index]
                    print_notice("Notice: omsagent incoming port was changed to " + sys.argv[index])
                    port_argument = False
                elif "-help" in sys.argv[index]:
                    print(help_text)
                    return
    if udp is True and tcp is True:
        print_error("Can not have both TCP and UDP on as communication protocol")
        return
    if udp is False and tcp is False:
        udp = True
    if download_omsagent():
        install_omsagent(workspace_id=workspace_id, primary_key=primary_key)
    if is_rsyslog():
        print("Located rsyslog daemon running on the machine")
        if create_rsyslog_daemon_forwarding_configuration(facility_restrictions=facility_restrictions, omsagent_incoming_port=omsagent_incoming_port) and \
                set_omsagent_configuration(workspace_id=workspace_id, omsagent_incoming_port=omsagent_incoming_port, tcp=tcp, udp=udp):
            restart_rsyslog()
            restart_omsagent(workspace_id=workspace_id)
    elif is_syslog_ng():
        print("Located syslog-ng daemon running on the machine")



main()
