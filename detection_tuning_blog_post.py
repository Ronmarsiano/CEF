#! /usr/local/bin/python3
import sys
import subprocess
import time
import random


fixed_message_p1 = "0|Palo Alto Networks"
fixed_message_p2 = "|PAN-OS|common=event-format-test|end|TRAFFIC|1|deviceExternalId=0001A01234 dpt=49510 suid=BarryAllen@contoso77.com suser=BarryAllen@contoso77.com dst=166.118.0.2 src=204.128.0.2  proto=TCP dvchost=PaloAltoDevice app=incomplete reason=tcp-rst-from-server act=ack sourceTranslatedAddress=211.0.17.10 destinationTranslatedAddress=3.4.6.3 testIndex="
cisco_message = "Inbound TCP connection denied from 183.60.23.164/58098 to 131.107.193.171/23 flags SYN  on interface inet"


def send_cef_message_remote(ip, port, start_millis, message_to_send, is_cef, rfc5424):
    message = message_to_send + "msg=Bla" + str(start_millis) + " Random=" + str(
        random.randint(0, 50000))+ " " if is_cef is True else message_to_send
    if rfc5424 is False:
        command_tokens = ["logger","rfc3164", "-p", "local4.warn", "-t", "CEF:" if is_cef is True else "%ASA-2-106001:", message, "-P", str(port), "-T", "-n", str(ip)]
    else:
        command_tokens = ["logger", "--rfc5424=notime,nohost,notq", "-p",  "local4.warn", "-t", "CEF:" if is_cef is True else "%ASA-2-106001:", message, "-P", str(port), "-T", "-n", str(ip)]
    logger = subprocess.Popen(command_tokens, stdout=subprocess.PIPE)
    o, e = logger.communicate()
    if e is None:
        return
    else:
        print("Error could not send cef message")


def send_cef_message_local(port, start_millis, message_to_send, is_cef, rfc5424):
    message = message_to_send + str(start_millis) + " Random=" + str(
        random.randint(0, 50000))+ " " if is_cef is True else message_to_send
    if rfc5424 is False:
        command_tokens = ["logger","rfc3164" ,"-p", "local4.warn", "-t", "CEF:" if is_cef is True else "%ASA-2-106001:", message, "-P", str(port), "-n", "127.0.0.1"]
    else:
        command_tokens = ["logger","--rfc5424=notime,nohost,notq", "-p",  "local4.warn", "-t", "CEF:" if is_cef is True else "%ASA-2-106001:", message, "-P", str(port), "-n", "127.0.0.1"]
    logger = subprocess.Popen(command_tokens, stdout=subprocess.PIPE)
    o, e = logger.communicate()
    if e is None:
        return
    else:
        print("Error could not send cef message")


def stream_message(ip, port, message_per_second, time_in_second, message_to_send, is_cef, rfc_5424):
    for curr_second in range(0, int(time_in_second)):
        start_millis = int(round(time.time() * 1000))
        print("Message per second: " + str(message_per_second))
        for curr_message in range(0, int(message_per_second)):
            message_arr = build_mesages(str(curr_message))
            ind = random.randint(0, len(message_arr)-1)
            message_to_send = message_arr[ind]
            if "127.0.0.1" in ip:
                send_cef_message_local(port, start_millis, message_to_send, is_cef=is_cef, rfc5424=rfc_5424)
            else:
                send_cef_message_remote(ip, port, start_millis, message_to_send, is_cef=is_cef, rfc5424=rfc_5424)
        end_millis = int(round(time.time() * 1000))
        time_send_took = end_millis - start_millis
        if time_send_took < 1000:
            time_to_sleep = float(1000 - time_send_took) / 1000
            time.sleep(time_to_sleep)
            print("stream")


def build_mesages(test_index):
    return [
        (fixed_message_p1 + "|PAN-OS|common=event-format-test|end|TRAFFIC|1|deviceExternalId=0001A01234 dpt=49510 suid=FlashBarryAllen@contoso77.com suser=FlashBarryAllen@contoso77.com dst=156.118.0.2 src=204.124.0.2  proto=TCP dvchost=PaloAltoDevice app=incomplete reason=tcp-rst-from-server act=ack sourceTranslatedAddress=311.0.17.10 destinationTranslatedAddress=3.4.45.3 testIndex="+ test_index),
        (fixed_message_p1 + "|PAN-OS|common=event-format-test|end|TRAFFIC|1|deviceExternalId=0001A01234 dpt=49510 suid=SupermanClarkJosephKent@contoso77.com suser=SupermanClarkJosephKent@contoso77.com dst=166.128.3.2 src=204.128.0.1  proto=TCP dvchost=PaloAltoDevice app=incomplete reason=tcp-rst-from-server act=ack sourceTranslatedAddress=111.0.17.10 destinationTranslatedAddress=3.4.6.43 testIndex="+ test_index),
        (fixed_message_p1 + "|PAN-OS|common=event-format-test|end|TRAFFIC|1|deviceExternalId=0001A01234 dpt=49510 suid=FlashBarryAllen@contoso77.com suser=FlashBarryAllen@contoso77.com dst=166.118.0.2 src=204.128.1.2  proto=TCP dvchost=PaloAltoDevice app=incomplete reason=tcp-rst-from-server act=ack sourceTranslatedAddress=211.1.17.10 destinationTranslatedAddress=3.4.5.3 testIndex="+ test_index),
        (fixed_message_p1 + "|PAN-OS|common=event-format-test|end|TRAFFIC|1|deviceExternalId=0001A01234 dpt=49510 suid=SupermanClarkJosephKent@contoso77.com suser=SupermanClarkJosephKent@contoso77.com dst=166.118.0.22 src=204.128.2.2  proto=TCP dvchost=PaloAltoDevice app=incomplete reason=tcp-rst-from-server act=ack sourceTranslatedAddress=211.20.17.10 destinationTranslatedAddress=3.4.63.3 testIndex="+ test_index),
        

        (fixed_message_p1 + "|PAN-OS|common=event-format-test|end|TRAFFIC|1|deviceExternalId=0001A01234 dpt=49510 suid=Thanos@contoso77.com suser=Thanos@contoso77.com dst=156.118.0.2 src=204.124.0.2  proto=TCP dvchost=PaloAltoDevice app=incomplete reason=tcp-rst-from-server act=ack sourceTranslatedAddress=311.0.17.10 destinationTranslatedAddress=3.4.45.3 testIndex="+ test_index),
        (fixed_message_p1 + "|PAN-OS|common=event-format-test|end|TRAFFIC|1|deviceExternalId=0001A01234 dpt=49510 suid=Magneto@contoso77.com suser=Magneto@contoso77.com dst=166.128.3.2 src=204.128.0.1  proto=TCP dvchost=PaloAltoDevice app=incomplete reason=tcp-rst-from-server act=ack sourceTranslatedAddress=111.0.17.10 destinationTranslatedAddress=3.4.6.43 testIndex="+ test_index),
        (fixed_message_p1 + "|PAN-OS|common=event-format-test|end|TRAFFIC|1|deviceExternalId=0001A01234 dpt=49510 suid=Thanos@contoso77.com suser=Thanos@contoso77.com dst=166.118.0.2 src=204.128.1.2  proto=TCP dvchost=PaloAltoDevice app=incomplete reason=tcp-rst-from-server act=ack sourceTranslatedAddress=211.1.17.10 destinationTranslatedAddress=3.4.5.3 testIndex="+ test_index),
        (fixed_message_p1 + "|PAN-OS|common=event-format-test|end|TRAFFIC|1|deviceExternalId=0001A01234 dpt=49510 suid=Magneto@contoso77.com suser=Magneto@contoso77.com dst=166.118.0.22 src=204.128.2.2  proto=TCP dvchost=PaloAltoDevice app=incomplete reason=tcp-rst-from-server act=ack sourceTranslatedAddress=211.20.17.10 destinationTranslatedAddress=3.4.63.3 testIndex="+ test_index),
        # (fixed_message_p1 + "|PAN-OS|common=event-format-test|end|TRAFFIC|1|deviceExternalId=0001A01234 dpt=49510 suid=BarryAllen@contoso77.com suser=BarryAllen@contoso77.com dst=166.118.0.2 src=204.148.0.2  proto=TCP dvchost=PaloAltoDevice app=incomplete reason=tcp-rst-from-server act=ack sourceTranslatedAddress=211.0.17.50 destinationTranslatedAddress=3.4.6.3 testIndex="+ test_index),
        # (fixed_message_p1 + "|PAN-OS|common=event-format-test|end|TRAFFIC|1|deviceExternalId=0001A01234 dpt=49510 suid=ClarkJosephKent@contoso77.com suser=ClarkJosephKent@contoso77.com dst=166.118.0.=1 src=224.128.0.2  proto=TCP dvchost=PaloAltoDevice app=incomplete reason=tcp-rst-from-server act=ack sourceTranslatedAddress=215.0.17.10 destinationTranslatedAddress=3.47.6.3 testIndex="+ test_index),

        # (fixed_message_p1 + "|PAN-OS|common=event-format-test|end|TRAFFIC|1|deviceExternalId=0001A01234 dpt=49510 suid=RobertBruceBanner@contoso77.com suser=RobertBruceBanner@contoso77.com dst=122.118.0.2 src=204.128.0.2  proto=TCP dvchost=PaloAltoDevice app=incomplete reason=tcp-rst-from-server act=ack sourceTranslatedAddress=211.0.17.10 destinationTranslatedAddress=3.4.6.3 testIndex="+ test_index),
        # (fixed_message_p1 + "|PAN-OS|common=event-format-test|end|TRAFFIC|1|deviceExternalId=0001A01234 dpt=49510 suid=HankPym@contoso77.com suser=HankPym@contoso77.com dst=16.118.0.2 src=204.12.0.2  proto=TCP dvchost=PaloAltoDevice app=incomplete reason=tcp-rst-from-server act=ack sourceTranslatedAddress=211.0.17.10 destinationTranslatedAddress=3.4.6.3 testIndex="+ test_index),
        # (fixed_message_p1 + "|PAN-OS|common=event-format-test|end|TRAFFIC|1|deviceExternalId=0001A01234 dpt=49510 suid=TonyStark@contoso77.com suser=TonyStark@contoso77.com dst=166.117.0.2 src=204.128.0.3  proto=TCP dvchost=PaloAltoDevice app=incomplete reason=tcp-rst-from-server act=ack sourceTranslatedAddress=211.0.17.10 destinationTranslatedAddress=3.4.6.3 testIndex="+ test_index),
        # (fixed_message_p1 + "|PAN-OS|common=event-format-test|end|TRAFFIC|1|deviceExternalId=0001A01234 dpt=49510 suid=StevenRogers@contoso77.com suser=StevenRogers@contoso77.com dst=166.11.0.2 src=204.128.4.2  proto=TCP dvchost=PaloAltoDevice app=incomplete reason=tcp-rst-from-server act=ack sourceTranslatedAddress=211.0.17.10 destinationTranslatedAddress=3.4.6.3 testIndex="+ test_index),
        # (fixed_message_p1 + "|PAN-OS|common=event-format-test|end|TRAFFIC|1|deviceExternalId=0001A01234 dpt=49510 suid=ClintonBarton@contoso77.com suser=ClintonBarton@contoso77.com dst=166.11.0.2 src=204.128.1.2  proto=TCP dvchost=PaloAltoDevice app=incomplete reason=tcp-rst-from-server act=ack sourceTranslatedAddress=211.0.17.10 destinationTranslatedAddress=3.4.6.3 testIndex="+ test_index),
        # (fixed_message_p1 + "|PAN-OS|common=event-format-test|end|TRAFFIC|1|deviceExternalId=0001A01234 dpt=49510 suid=StevenRogers@contoso77.com suser=StevenRogers@contoso77.com dst=166.11.0.3 src=204.128.0.3  proto=TCP dvchost=PaloAltoDevice app=incomplete reason=tcp-rst-from-server act=ack sourceTranslatedAddress=211.0.17.10 destinationTranslatedAddress=3.4.6.3 testIndex="+ test_index),

        # (fixed_message_p1 + "|PAN-OS|common=event-format-test|end|TRAFFIC|1|deviceExternalId=0001A01234 dpt=49510 suid=BillyBatson@contoso77.com suser=BillyBatson@contoso77.com dst=166.118.0.2 src=204.128.0.2  proto=TCP dvchost=PaloAltoDevice app=incomplete reason=tcp-rst-from-server act=ack sourceTranslatedAddress=211.0.17.10 destinationTranslatedAddress=3.4.6.3 testIndex="+ test_index),
        # (fixed_message_p1 + "|PAN-OS|common=event-format-test|end|TRAFFIC|1|deviceExternalId=0001A01234 dpt=49510 suid=BruceWayne@contoso77.com suser=BruceWayne@contoso77.com dst=166.118.0.2 src=204.128.0.2  proto=TCP dvchost=PaloAltoDevice app=incomplete reason=tcp-rst-from-server act=ack sourceTranslatedAddress=211.0.17.10 destinationTranslatedAddress=3.4.6.3 testIndex="+ test_index),
        # (fixed_message_p1 + "|PAN-OS|common=event-format-test|end|TRAFFIC|1|deviceExternalId=0001A01234 dpt=49510 suid=BillyBatson@contoso77.com suser=BillyBatson@contoso77.com dst=166.118.0.2 src=204.128.0.2  proto=TCP dvchost=PaloAltoDevice app=incomplete reason=tcp-rst-from-server act=ack sourceTranslatedAddress=211.0.17.10 destinationTranslatedAddress=3.4.6.3 testIndex="+ test_index),
        # (fixed_message_p1 + "|PAN-OS|common=event-format-test|end|TRAFFIC|1|deviceExternalId=0001A01234 dpt=49510 suid=BruceWayne@contoso77.com suser=BruceWayne@contoso77.com dst=166.118.0.2 src=204.128.0.2  proto=TCP dvchost=PaloAltoDevice app=incomplete reason=tcp-rst-from-server act=ack sourceTranslatedAddress=211.0.17.10 destinationTranslatedAddress=3.4.6.3 testIndex="+ test_index),
        # (fixed_message_p1 + "|PAN-OS|common=event-format-test|end|TRAFFIC|1|deviceExternalId=0001A01234 dpt=49510 suid=BillyBatson@contoso77.com suser=BillyBatson@contoso77.com dst=166.118.0.2 src=204.128.0.2  proto=TCP dvchost=PaloAltoDevice app=incomplete reason=tcp-rst-from-server act=ack sourceTranslatedAddress=211.0.17.10 destinationTranslatedAddress=3.4.6.3 testIndex="+ test_index),
        # (fixed_message_p1 + "|PAN-OS|common=event-format-test|end|TRAFFIC|1|deviceExternalId=0001A01234 dpt=49510 suid=BruceWayne@contoso77.com suser=BruceWayne@contoso77.com dst=166.118.0.2 src=204.128.0.2  proto=TCP dvchost=PaloAltoDevice app=incomplete reason=tcp-rst-from-server act=ack sourceTranslatedAddress=211.0.17.10 destinationTranslatedAddress=3.4.6.3 testIndex="+ test_index),

        # (fixed_message_p1 + "|PAN-OS|common=event-format-test|end|TRAFFIC|1|deviceExternalId=0001A01234 dpt=49510 suid=LexLuthor@contoso77.com suser=LexLuthor@contoso77.com dst=166.118.0.2 src=204.128.0.2  proto=TCP dvchost=PaloAltoDevice app=incomplete reason=tcp-rst-from-server act=ack sourceTranslatedAddress=211.0.17.10 destinationTranslatedAddress=3.4.6.3 testIndex="+ test_index),
        # (fixed_message_p1 + "|PAN-OS|common=event-format-test|end|TRAFFIC|1|deviceExternalId=0001A01234 dpt=49510 suid=EobardThawne@contoso77.com suser=EobardThawne@contoso77.com dst=166.118.0.2 src=204.128.0.2  proto=TCP dvchost=PaloAltoDevice app=incomplete reason=tcp-rst-from-server act=ack sourceTranslatedAddress=211.0.17.10 destinationTranslatedAddress=3.4.6.3 testIndex="+ test_index),
        # (fixed_message_p1 + "|PAN-OS|common=event-format-test|end|TRAFFIC|1|deviceExternalId=0001A01234 dpt=49510 suid=OttoOctavius@contoso77.com suser=OttoOctavius@contoso77.com dst=166.118.0.2 src=204.128.0.2  proto=TCP dvchost=PaloAltoDevice app=incomplete reason=tcp-rst-from-server act=ack sourceTranslatedAddress=211.0.17.10 destinationTranslatedAddress=3.4.6.3 testIndex="+ test_index),
        # (fixed_message_p1 + "|PAN-OS|common=event-format-test|end|TRAFFIC|1|deviceExternalId=0001A01234 dpt=49510 suid=NormanOsborn@contoso77.com suser=NormanOsborn@contoso77.com dst=166.118.0.2 src=204.128.0.2  proto=TCP dvchost=PaloAltoDevice app=incomplete reason=tcp-rst-from-server act=ack sourceTranslatedAddress=211.0.17.10 destinationTranslatedAddress=3.4.6.3 testIndex="+ test_index),
        # (fixed_message_p1 + "|PAN-OS|common=event-format-test|end|TRAFFIC|1|deviceExternalId=0001A01234 dpt=49510 suid=UlyssesKlaue@contoso77.com suser=UlyssesKlaue@contoso77.com dst=166.118.0.2 src=204.128.0.2  proto=TCP dvchost=PaloAltoDevice app=incomplete reason=tcp-rst-from-server act=ack sourceTranslatedAddress=211.0.17.10 destinationTranslatedAddress=3.4.6.3 testIndex="+ test_index),
        # (fixed_message_p1 + "|PAN-OS|common=event-format-test|end|TRAFFIC|1|deviceExternalId=0001A01234 dpt=49510 suid=ObadiahStane@contoso77.com suser=ObadiahStane@contoso77.com dst=166.118.0.2 src=204.128.0.2  proto=TCP dvchost=PaloAltoDevice app=incomplete reason=tcp-rst-from-server act=ack sourceTranslatedAddress=211.0.17.10 destinationTranslatedAddress=3.4.6.3 testIndex="+ test_index),
        # (fixed_message_p1 + "|PAN-OS|common=event-format-test|end|TRAFFIC|1|deviceExternalId=0001A01234 dpt=49510 suid=ErikKillmonger@contoso77.com suser=ErikKillmonger@contoso77.com dst=166.118.0.2 src=204.128.0.2  proto=TCP dvchost=PaloAltoDevice app=incomplete reason=tcp-rst-from-server act=ack sourceTranslatedAddress=211.0.17.10 destinationTranslatedAddress=3.4.6.3 testIndex="+ test_index)
    ]

def distribute_message(ip, port, amount, messages_per_second, message_to_send, is_cef):
    # time in seconds
    delta = 1000 / messages_per_second
    for index in range(0, amount):
        start_millis = int(round(time.time() * 1000))
        send_cef_message_remote(ip, port, start_millis, message_to_send, is_cef=is_cef)
        end_millis = int(round(time.time() * 1000))
        diff_millis = end_millis - start_millis
        sleep_time_millis = delta - diff_millis
        if sleep_time_millis > 0:
            print("sleeping for :" + str(sleep_time_millis))
            time.sleep(sleep_time_millis/1000)
            print("slept")


def main():
    start_millis = int(round(time.time() * 1000))
    if len(sys.argv) < 7:
        print("The script is expecting 4 arguments:")
        print("1) destination ip")
        print("2) destination port")
        print("3) amount of messages in second")
        print("4) amount of seconds")
        print("5) test index")
        print("6) CEF/CISCO")
        print("7) Optional - rfc5424")

        return
    else:
        ip = sys.argv[1]
        port = sys.argv[2]
        messages_per_second = sys.argv[3]
        amount_of_seconds = sys.argv[4]
        test_index = sys.argv[5]
        is_cef = True if "CEF" in sys.argv[6] else False

        if len(sys.argv) >= 7:
            rfc_5424 = True
        else:
            rfc_5424 = False
        print("rfc_5424="+str(rfc_5424))


        message_to_send = (fixed_message_p1 + fixed_message_p2+ test_index) if is_cef is True else cisco_message
        # distribute_message(ip, port, int(messages_per_second) * int(amount_of_seconds), int(messages_per_second), message_to_send)
        # message_arr = build_mesages(test_index)
        # ind = random.randint(0, len(message_arr))
        # message_to_send = message_arr[ind]
        stream_message(ip, port, messages_per_second, amount_of_seconds, message_to_send, is_cef=is_cef, rfc_5424=rfc_5424)
        print("Done - " + str(int(messages_per_second) * int(amount_of_seconds)))
    end_millis = int(round(time.time() * 1000))
    print("Time[seconds]: " + str((end_millis-start_millis)/1000))

main()

