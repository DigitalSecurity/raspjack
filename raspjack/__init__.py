"""
Nordic Semiconductor NRF24L01+ Hijacking framework
(MouseJack port for Raspberry Pi 1 & 2)

This module provides the `RaspJack` class in order to scan, sniff and
transmit payloads over NRF24L01+. It uses a trick discovered by Travis
Goodspeed (http://travisgoodspeed.blogspot.fr/2011/02/promiscuity-is-nrf24l01s-duty.html)
to enable pseudo-promiscuous mode. The packet validation code is borrowed from
the original MouseJack code (https://github.com/RFStorm/mousejack).

This module relies on `pynrf24` for driving NRF24 on Raspberry Pi.

Author: Damien "virtualabs" Cauquil <damien.cauquil@digitalsecurity.fr>
"""

import sys
from time import time, sleep
from nrf24 import NRF24
from struct import unpack

class NrfPacket(object):
    """
    NRF24 Packet.
    """
    def __init__(self, channel=0, address=None, payload=None):
        self.channel = channel
        self.address = address
        self.payload = payload

class RaspJack(object):
    """
    NRF24 Hijacker for Raspberry Pi.
    """
    def __init__(self, version=2):
        """
        Init radio.

        @param version int  Specifies Raspberry Pi version (1 for Raspberry Pi Model A/B, 2 for Raspberry Pi 2+)
        """
        self.pipes = [ [0xaa, 0x00, 0x00, 0x00, 0x00]]
        self.channel = 0
        self.radio = NRF24()
        # check raspberry PI version
        if version == 2:
            # RaspPi 2
            self.radio.begin(0,0,25,24)
        else:
            # RaspPi 1
            self.radio.begin(1,0,25,24)

    def addr2bytes(self, addr):
        """
        Convert an address into a series of bytes.
        """
        addr = addr.replace(':','')
        addr_bytes = []
        addr_len = len(addr)
        if addr_len % 2 == 0:
            for i in range(addr_len/2):
                addr_bytes.append(ord(addr[i*2:(i+1)*2].decode('hex')))
            return addr_bytes[::-1]
        else:
            return None

    def crc_update(self, crc, byte, bits):
        """
        Update CRC16 CCITT
        """
        crc = crc ^(byte << 8)
        while bits>0:
            if (crc & 0x8000) == 0x8000:
                crc = (crc << 1) ^ 0x1021
            else:
                crc = crc << 1
            bits -= 1
        crc = crc & 0xFFFF
        return crc

    def shift_payload(self, p):
        """
        Shift payload left by one bit
        """
        for x in range(0,len(p)-1):
            if x<26:
                p[x] = (p[x]<<1)&0xff | (p[x+1]&0x80)>>7
            else:
                p[x] = p[x]<<1
        return p

    def unshift_payload(self, p):
        """
        Shift payload right by one bit
        """
        for x in range(len(p)-1,-1,-1):
            if x > 0:
                p[x] = (p[x-1]<<7)&0xff | p[x]>>1
            else:
                p[x] = p[x]>>1
        return p

    def set_crc_length(self, length):
        """
        Set CRC length.
        """
        constants = {
            8: self.radio.CRC_8,
            16: self.radio.CRC_16
        }
        if length in constants:
            self.radio.setCRCLength(constants[length])
            return True
        else:
            return False

    def set_channel(self, channel):
        """
        Set NRF24 channel.
        """
        self.channel = channel
        self.radio.setChannel(channel)

    def init_tx(self, channel, address):
        """
        Prepare NRF24 to transmit.
        """
        self.radio.setRetries(15, 15)

        # configure address
        self.radio.setAddressWidth(5)
        self.radio.openReadingPipe(0,self.addr2bytes(address))
        self.radio.openWritingPipe(self.addr2bytes(address))

        # enable dynamic payload length
        self.radio.enableDynamicPayloads()
        self.radio.setAutoAck(False)

        self.radio.setCRCLength(self.radio.CRC_16)
        self.radio.setPALevel(NRF24.PA_MAX)
        self.radio.setDataRate(NRF24.BR_2MBPS)
        self.radio.setChannel(channel)
        self.channel = channel
        self.radio.startListening()

    def transmit(self, payload):
        """
        Transmit a payload over a channel to a specified address.
        """
        self.radio.stopListening()
        res = self.radio.write(payload)
        self.radio.startListening()
        return res

    def init_scan(self):
        """
        Set NRF24 state into scanning mode.
        """
        self.radio.setAutoAck(False)
        self.radio.setPALevel(NRF24.PA_MIN)
        self.radio.setDataRate(NRF24.BR_2MBPS)
        self.radio.setPayloadSize(32)
        self.radio.setChannel(self.channel)
        self.radio.write_register(0x02, 0x00)
        self.radio.write_register(0x03, 0x00)
        self.radio.openReadingPipe(0, self.pipes[0])
        self.radio.disableCRC()
        self.radio.startListening()

    def resume_scan(self):
        """
        Restore NRF24 state into scanning mode.

        Use this method when you want to resume scanning
        after transmitted some payload.
        """
        # disable dynamic payloads
        self.radio.write_register(self.radio.FEATURE, 0)
        self.radio.write_register(self.radio.DYNPD, 0)
        self.radio.setAutoAck(False)
        self.radio.setDataRate(NRF24.BR_2MBPS)
        self.radio.setPayloadSize(32)
        self.radio.write_register(0x02, 0x00)
        self.radio.write_register(0x03, 0x00)
        self.radio.openReadingPipe(0, self.pipes[0])
        self.radio.disableCRC()
        self.radio.startListening()

    def resume_sniff(self, address):
        """
        Restore NRF24 state into scanning mode.

        Use this method when you want to resume scanning
        after transmitted some payload.
        """
        # disable dynamic payloads
        self.radio.write_register(self.radio.FEATURE, 0)
        self.radio.write_register(self.radio.DYNPD, 0)
        self.radio.setAutoAck(False)
        self.radio.setDataRate(NRF24.BR_2MBPS)
        self.radio.setPayloadSize(32)
        # configure address
        self.radio.write_register(0x02, 0x00)
        self.radio.setAddressWidth(5)
        self.radio.openReadingPipe(0,self.addr2bytes(address))
        self.radio.disableCRC()
        self.radio.startListening()

    def scan(self, channel_timeout=0.1):
        """
        Scanning method.

        It takes some time to go through all the available channels and to
        identify all the available devices, so don't expect great performances
        with this full python implementation.

        This method should only be used to identify potential targets, not for
        sniffing.

        Yields `NrfPacket` objects as they are sniffed.
        """
        self.init_scan()
        wait = channel_timeout
        while True:
            if self.channel > 80:
                self.channel = 3
            self.radio.setChannel(self.channel)
            start = time()
            while (time() - start) < wait:
                if self.radio.available([0]):
                    recv_buffer = []
                    self.radio.read(recv_buffer, 32)
                    payload = list(recv_buffer)
                    if len(payload) > 0:
                        # try to find a valid packet
                        # (mousejack code ported to Python)
                        for i in range(2):
                            if i == 1:
                                # shift the payload right
                                payload = self.unshift_payload(payload)

                            # shift payload
                            addr = ':'.join(['%02x' % c for c in payload[:5]])
                            packet = self.shift_payload(payload[5:])

                            # retrieve packet len
                            packet_len = (packet[0]>>3)
                            if packet_len < 24:
                                # ensure CRC is valid
                                crc_expected = packet[packet_len+2]<<8 | packet[packet_len+1]
                                if packet[packet_len+3] & 0x80:
                                    crc_expected |= 0x100
                                bin_packet = ''.join(map(chr, payload))
                                crc = 0xFFFF
                                for x in range(6+packet_len):
                                    crc = self.crc_update(crc, ord(bin_packet[x]), 8)
                                crc = self.crc_update(crc, ord(bin_packet[6+packet_len])&0x80,1)
                                crc = ((crc<<8) | (crc>>8))&0xffff
                                if crc == crc_expected:
                                    # CRC valid, yield a NrfPacket instance
                                    yield NrfPacket(self.channel,  addr, packet[1:packet_len+1])

                        # Flush RX FIFO buffer.
                        self.radio.flush_rx()
            self.channel += 1


    def sniff(self, target):
        """
        Sniff packets from a given target, automatically handles channel hopping.
        """
        # force address
        self.radio.openReadingPipe(0, self.addr2bytes(target))
        #self.radio.openWritingPipe(self.addr2bytes(target))
        # enable dynamic payload length
        self.radio.enableDynamicPayloads()
        self.radio.setAutoAck(False)
        # 2MBPS rate, 16-bit CRC, PA MAX
        self.radio.setCRCLength(self.radio.CRC_16)
        #self.radio.disableCRC()
        self.radio.setPALevel(NRF24.PA_MIN)
        self.radio.setDataRate(NRF24.BR_2MBPS)
        # Enable RX
        self.radio.startListening()

        timeout=2.0
        locked = time()-10.0
        channel = 3
        channel_locked = 3
        self.set_channel(channel)
        while True:
            if self.radio.available([0]):
                channel_locked = channel
                locked = time()
                recv_buffer = []
                self.radio.read(recv_buffer, 32)
                payload = list(recv_buffer)
                yield NrfPacket(self.channel, target, payload)
            if time() - locked > timeout:
                if channel_locked is not None:
                    channel_locked = None
                channel += 1
                if channel > 80:
                    channel = 3
                self.set_channel(channel)
                sleep(0.01)


if __name__ == '__main__':
    hijacker = RaspJack()
    for packet in hijacker.scan():
        print '%02d'%packet.channel + ' | '+packet.address+' | '+' '.join(['%02x' % c for c in packet.payload])
