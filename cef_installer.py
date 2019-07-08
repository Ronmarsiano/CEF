#! /usr/local/bin/python3
import subprocess
import time
import sys

rsyslog_daemon_name = "rsyslog"
syslog_ng_daemon_name = "syslog-ng"
oms_agent_file_name = "onboard_agent.sh"
oms_agent_url = "https://raw.githubusercontent.com/Microsoft/OMS-Agent-for-Linux/master/installer/scripts/" + oms_agent_file_name
help_text = "Optional arguments for the python script are:\n\t-T: for TCP\n\t-U: for UDP which is the default value.\n\t-F: for no facility restrictions.\n\t-p: for changing default port from 25226"
omsagent_default_incoming_port = "25226"
daemon_default_incoming_port = "514"
rsyslog_daemon_forwarding_configuration_path = "/etc/rsyslog.d/security-config-omsagent.conf"
syslog_ng_daemon_forwarding_configuration_path = "/etc/syslog-ng/conf.d/security-config-omsagent.conf"
rsyslog_conf_path = "/etc/rsyslog.conf"
rsyslog_module_udp_content = "# provides UDP syslog reception\nmodule(load=\"imudp\")\ninput(type=\"imudp\" port=\"" + daemon_default_incoming_port + "\")\n"
rsyslog_module_tcp_content = "# provides TCP syslog reception\nmodule(load=\"imtcp\")\ninput(type=\"imtcp\" port=\"" + daemon_default_incoming_port + "\")\n"

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
    :return: True if downloaded successfully
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
    print("Installing omsagent")
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


def create_daemon_forwarding_configuration(omsagent_incoming_port, daemon_configuration_path, daemon_name):
    '''
    Create the daemon configuration to forward messages over TCP to the
    oms agent
    :param omsagent_incoming_port: port for communication between the omsagent the the daemon
    :param daemon_configuration_path: path of the configuration file
    :param daemon_name: name of the daemon
    :return:
    '''
    print("Creating " + daemon_name + " daemon configuration.")
    print("Configuration is changed to forward daemon incoming syslog messages into the omsagent.")
    print("Every command containing \'CEF\' string will be forwarded.")
    print("Path:")
    print_notice(daemon_configuration_path)
    file_content = get_daemon_configuration_content(daemon_name, omsagent_incoming_port)
    command_tokens = ["sudo", "bash", "-c", "printf '" + file_content + "' > " + daemon_configuration_path]
    print_notice("Writing configuration - "+" ".join(command_tokens))
    set_daemon_configuration = subprocess.Popen(command_tokens, stdout=subprocess.PIPE)
    o, e = set_daemon_configuration.communicate()
    time.sleep(3)
    if e is not None:
        error_output = e.decode('ascii')
        print_error("Could not change " + daemon_name + " daemon configuration.")
        print_error(error_output)
        return False
    print_ok("Configuration for " + daemon_name + " daemon was changed successfully.")
    return True


def set_omsagent_configuration(workspace_id, omsagent_incoming_port):
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
    if change_omsagent_protocol(configuration_path=configuration_path):
        print_ok("Finished changing omsagent configuration")
        return True
    else:
        print_error("Could not change the omsagent configuration")
        return False


def rsyslog_red_hat_mod_load_tcp(fout, line):
    if "ModLoad" in line and "imtcp" in line:
        if "#" in line:
            fout.write(line.replace("#", ""))
        else:
            fout.write(line)
        return True
    elif "TCPServerRun" in line and daemon_default_incoming_port in line:
        if "#" in line:
            fout.write(line.replace("#", ""))
        else:
            fout.write(line)
        return True
    return False


def rsyslog_red_hat_mod_load_udp(fout, line):
    if "ModLoad" in line and "imudp" in line:
        if "#" in line:
            fout.write(line.replace("#", ""))
        else:
            fout.write(line)
        return True
    elif "UDPServerRun" in line and daemon_default_incoming_port in line:
        if "#" in line:
            fout.write(line.replace("#", ""))
        else:
            fout.write(line)
        return True
    return False


# def rsyslog_configuration_enable_old_configuration(protocl):
#     with open(rsyslog_conf_path, "rt") as fin:
#         for line in fin:
#             if "imudp" in line and "#




def set_rsyslog_configuration():
    '''
    Set the configuration for rsyslog
    we support from version 7 and above
    :return:
    '''
    udp_enabled = False
    # tcp_enabled = False
    # # old configuration using ModLoad
    # old_rsyslog_configuration = False
    # # new configuration using module load
    # new_rsyslog_configuration = False
    #
    # print("Trying to change rsyslog configuration")
    # print_command_response("Content should contain:")
    # print_command_response(rsyslog_module_udp_content)
    # print_command_response(rsyslog_module_tcp_content)
    # print_notice(rsyslog_conf_path)
    # print_warning("Supported rsyslog version is \"7\" to rsyslog 8.1905.0")
    # with open(rsyslog_conf_path, "rt") as fin:
    #         for line in fin:
    #             if "$ModLoad" in line:
    #                 old_rsyslog_configuration = True
    #             elif "module" in line and "load" in line:
    #                 new_rsyslog_configuration = True
    #
    #
    #             if "imudp" in line and ("module" in line or "input" in line):
    #                 if "#" in line:
    #                     fout.write(line.replace("#", ""))
    #                 else:
    #                     fout.write(line)
    #                 if daemon_default_incoming_port in line:
    #                     udp_enabled = True
    #             elif "imtcp" in line and ("module" in line or "input" in line):
    #                 if "#" in line:
    #                     fout.write(line.replace("#", ""))
    #                 else:
    #                     fout.write(line)
    #                 if daemon_default_incoming_port in line:
    #                     tcp_enabled = True
    #             elif rsyslog_red_hat_mod_load_tcp(fout, line):
    #                 tcp_enabled = True
    #             elif rsyslog_red_hat_mod_load_udp(fout, line):
    #                 udp_enabled = True
    #             else:
    #                 fout.write(line)
    #         if not udp_enabled:
    #             fout.write(rsyslog_module_udp_content)
    #         if not tcp_enabled:
    #             fout.write(rsyslog_module_tcp_content)
    # command_tokens = ["sudo", "mv", "tmp.txt", rsyslog_conf_path]
    # write_new_content = subprocess.Popen(command_tokens, stdout=subprocess.PIPE)
    # time.sleep(3)
    # o, e = write_new_content.communicate()
    # if e is not None:
    #     error_output = e.decode('ascii')
    #     print_error("Error: could not change omsagent configuration port in ." + rsyslog_conf_path)
    #     print_error(error_output)
    #     return False
    # print_ok("Omsagent configuration was changed to fit required protocol - " + rsyslog_conf_path)
    # return True


def change_omsagent_protocol(configuration_path):
    '''
    Changing the omsagent protocol, since the protocol type is set on the omsagent
    configuration file
    :param configuration_path:
    '''
    with open(configuration_path, "rt") as fin:
        with open("tmp.txt", "wt") as fout:
            for line in fin:
                if "protocol_type" in line and "udp" in line:
                    fout.write(line.replace("udp", "tcp"))
                    print_notice("Changing protocol type from udp to tcp in "+configuration_path)
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
    Restart the Rsyslog daemon
    '''
    print("Restarting rsyslog daemon.")
    command_tokens = ["sudo", "service", "rsyslog", "restart"]
    print_notice(" ".join(command_tokens))
    restart_rsyslog_command = subprocess.Popen(command_tokens, stdout=subprocess.PIPE)
    time.sleep(3)
    o, e = restart_rsyslog_command.communicate()
    if e is not None:
        error_output = e.decode('ascii')
        print_error("Could not restart rsyslog daemon")
        print_error(error_output)
        return False
    print_ok("Rsyslog daemon restarted successfully")
    return True


def restart_syslog_ng():
    '''
    Restart the syslog-ng daemon
    '''
    print("Restarting syslog-ng daemon.")
    command_tokens = ["sudo", "service", "syslog-ng", "restart"]
    print_notice(" ".join(command_tokens))
    restart_rsyslog_command = subprocess.Popen(command_tokens, stdout=subprocess.PIPE)
    time.sleep(3)
    o, e = restart_rsyslog_command.communicate()
    if e is not None:
        error_output = e.decode('ascii')
        print_error("Could not restart syslog-ng daemon")
        print_error(error_output)
        return False
    print_ok("Syslog-ng daemon restarted successfully")
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


def get_daemon_configuration_content(daemon_name, omsagent_incoming_port):
    '''
    Return the correct configuration according to the daemon name
    :param daemon_name:
    :param omsagent_incoming_port:
    :return:
    '''
    if daemon_name is rsyslog_daemon_name:
        return get_rsyslog_daemon_configuration_content(omsagent_incoming_port)
    elif daemon_name is syslog_ng_daemon_name:
        return get_syslog_ng_damon_configuration_content(omsagent_incoming_port)
    else:
        print_error("Could not create daemon configuration.")
        return False


def get_rsyslog_daemon_configuration_content(omsagent_incoming_port):
    '''Rsyslog accept every message containing CEF'''
    rsyslog_daemon_configuration_content = ":msg, contains, \"CEF\"  ~\n*.* @@127.0.0.1:"
    print("Rsyslog daemon configuration content:")
    content = rsyslog_daemon_configuration_content + omsagent_incoming_port
    print_command_response(content)
    return content


def get_syslog_ng_damon_configuration_content(omsagent_incoming_port):
    part_1 = "filter f_oms_cef { match(\"CEF\" value(\"MESSAGE\"));};\ndestination security_oms { tcp(\"127.0.0.1\" port("
    part_2 = "));};\nlog { source(s_src); filter(f_oms_cef); destination(security_oms); };"
    content = part_1 + omsagent_incoming_port + part_2
    print("Syslog-ng configuration for forwarding CEF messages to omsagent content is:")
    print_command_response(content)
    return content


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
    return process_check(syslog_ng_daemon_name) > 1


def main():
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
                if "-p" in sys.argv[index]:
                    port_argument = True
                elif port_argument:
                    omsagent_incoming_port = sys.argv[index]
                    print_notice("Notice: omsagent incoming port was changed to " + sys.argv[index])
                    port_argument = False
                elif "-help" in sys.argv[index]:
                    print(help_text)
                    return
    if download_omsagent():
        install_omsagent(workspace_id=workspace_id, primary_key=primary_key)
        set_omsagent_configuration(workspace_id=workspace_id, omsagent_incoming_port=omsagent_incoming_port)
    if is_rsyslog():
        print("Located rsyslog daemon running on the machine")
        create_daemon_forwarding_configuration(omsagent_incoming_port=omsagent_incoming_port,
                                               daemon_configuration_path=rsyslog_daemon_forwarding_configuration_path,
                                               daemon_name=rsyslog_daemon_name)
        #set_rsyslog_configuration()
        restart_rsyslog()
    elif is_syslog_ng():
        print("Located syslog-ng daemon running on the machine")
        create_daemon_forwarding_configuration(omsagent_incoming_port=omsagent_incoming_port,
                                               daemon_configuration_path=syslog_ng_daemon_forwarding_configuration_path,
                                               daemon_name=syslog_ng_daemon_name)
        restart_syslog_ng()
    restart_omsagent(workspace_id=workspace_id)


main()
