# SPDX-License-Identifier: GPL-2.0-only
# This file is part of Scapy
# See https://scapy.net/ for more information
# Copyright (C) Guillaume Valadon <guillaume@valadon.net>

"""
Scapy eBPF native support - programs that retrieve process information
"""

from scapy.all import *

from .process_information import KprobeProcessInformation


@conf.commands.register
def sniff(*args, **kwargs):
    # type: (*Any, **Any) -> PacketList

    kprobe = None
    if "process_information" in kwargs:
        del kwargs["process_information"]

        if LINUX:
            kprobe = KprobeProcessInformation()
            kprobe.start()

            user_prn = lambda p: None
            if "prn" in kwargs:
                user_prn = kwargs["prn"]

            def _prn(packet):
                kprobe.lookup(packet)
                user_prn(packet)

            kwargs["prn"] = _prn
        else:
            warning("'process_information' is only support on Linux!")

    sniffer = AsyncSniffer()
    sniffer._run(*args, **kwargs)
    if kprobe:
        kprobe.stop()
        kprobe.join()
    return cast(PacketList, sniffer.results)


if __name__ == "__main__":
    print("Scapy + eBPF = <3")

    packets = sniff(count=10, filter="ip and not port 22",
                    process_information=True)

    for p in packets:
        print(p.comment, p.summary())
