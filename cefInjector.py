#! /usr/local/bin/python3
import sys
import subprocess
import time
import datetime


fixed_message_p1 = "0|Test "
fixed_message_p2 = "|PAN-OS|cef-test|end|TRAFFIC|1|rt=$cefformatted-receive_time deviceExternalId=0002D01655 src=1.1.1.1 dst=2.2.2.2 sourceTranslatedAddress=1.1.1.1 destinationTranslatedAddress=3.3.3.3 cs1Label=Rule cs1=InternetDNS |"


def send_cef_message(ip, port, start_millis, message_to_send):
    message = message_to_send+" Message="+str(start_millis)
    logger = subprocess.Popen(["logger", "-p", "local4.warn", "-t", "CEF:", message, "-P", str(port), "-d", "-n", str(ip)], stdout=subprocess.PIPE)
    o, e = logger.communicate()
    if e is None:
        return
    else:
        print("Error could not send cef message")


def stream_message(ip, port, message_per_second, time_in_second, message_to_send):
    for curr_second in range(0, int(time_in_second)):
        start_millis = int(round(time.time() * 1000))
        for curr_message in range(0, int(message_per_second)):
            send_cef_message(ip, port, start_millis, message_to_send)
        end_millis = int(round(time.time() * 1000))

        time_send_took = end_millis - start_millis
        if time_send_took < 1000:
            print("sleeping")
            time.sleep((1000 - time_send_took)/1000)


def distribute_message(ip, port, amount, messages_per_second, message_to_send):
    # time in seconds
    delta = 1000 / messages_per_second
    for index in range(0, amount):
        start_millis = int(round(time.time() * 1000))
        send_cef_message(ip, port, start_millis, message_to_send)
        end_millis = int(round(time.time() * 1000))
        diff_millis = end_millis - start_millis
        sleep_time_millis = delta - diff_millis
        if sleep_time_millis > 0:
            print("sleeping for :" + str(sleep_time_millis))
            time.sleep(sleep_time_millis/1000)


def main():
    start_millis = int(round(time.time() * 1000))
    if len(sys.argv) != 6:
        print("The script is expecting 4 arguments:")
        print("1) destination ip")
        print("2) destination port")
        print("3) amount of messages in second")
        print("4) amount of seconds")
        print("5) test index")

        return
    else:
        ip = sys.argv[1]
        port = sys.argv[2]
        messages_per_second = sys.argv[3]
        amount_of_seconds = sys.argv[4]
        test_index = sys.argv[5]
        message_to_send = fixed_message_p1 + test_index + fixed_message_p2
        # distribute_message(ip, port, int(messages_per_second) * int(amount_of_seconds), int(messages_per_second), message_to_send)
        stream_message(ip, port, messages_per_second, amount_of_seconds, message_to_send)
        print("Done - " + str(int(messages_per_second) * int(amount_of_seconds)))
    end_millis = int(round(time.time() * 1000))
    print("Time[seconds]: " + str((end_millis-start_millis)/1000))

main()
