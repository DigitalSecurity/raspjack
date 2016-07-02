#!/usr/bin/env python

"""
RaspJack sniffer command-line utility

Author: Damien "virtualabs" Cauquil <damien.cauquil@digitalsecurity.fr>
"""

import argparse
from raspjack import RaspJack

def disp_packet(packet):
    """
    Display packet
    """
    payload = ' '.join(['%02x'%c for c in packet.payload])
    print('%02d | %s | %s' % (packet.channel, packet.address, payload))


def sniffer():
    """
    rj-sniffer command-line utility.
    """
    parser = argparse.ArgumentParser(description='RaspJack CLI sniffer')
    parser.add_argument('--target', '-t', dest='target', type=str, required=True,help='target NRF24 MAC (11:22:33:44:55)')
    args = parser.parse_args()
    pkt_count = 0
    try:
        sniffer = RaspJack()
        for packet in sniffer.sniff(args.target):
            disp_packet(packet)
            pkt_count += 1
    except KeyboardInterrupt as exc:
        print '[i] %d packets sniffed.' % pkt_count
    except:
        print '[!] Cannot initialize sniffer. Check your setup.'

def scanner():
    """
    rj-scanner command-line utility.
    """
    parser = argparse.ArgumentParser(description='RaspJack CLI scanner')
    parser.add_argument('--timeout', '-t', dest='timeout', type=float, default=0.4,help='time per channel for discovery')
    args = parser.parse_args()
    pkt_count = 0
    try:
        sniffer = RaspJack()
        for packet in sniffer.scan(args.timeout):
            disp_packet(packet)
            pkt_count += 1
    except KeyboardInterrupt as exc:
        print '[i] %d packets captured.' % pkt_count
    except Exception as exc:
        print exc
        print '[!] Cannot initialize scanner. Check your setup.'

