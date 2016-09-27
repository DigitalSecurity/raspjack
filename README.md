RaspJack, a port of MouseJack for Raspberry Pi 2
================================================

How to install
--------------

```
$ sudo python setup.py install
```

Raspberry Pi setup
------------------

Connect the following pins (rasp) to the associated pins (nrf24):

|RASP | NRF24L01|
|-----|---------|
| 17  |    2    |
| 18  |    8    |
| 19  |    6    |
| 20  |    1    |
| 21  |    7    |
| 22  |    3    |
| 23  |    5    |
| 24  |    4    |

Dependencies
------------

RaspJack relies on *pynrf24* to drive the NRF24L01+ module through SPI. This dependency is mandatory
and installed as follows:

```
$ git clone https://github.com/jpbarraca/pynrf24.git
$ cd pynrf24
$ sudo python setup.py install
```

How to use
----------

The *rj-scanner* tool may be used to identify available devices (40bits MAC address, channel and payloads), while *rj-sniffer* is able to sniff most of the packets sent to a specific device.

Examples:

    pi@raspberrypi:/tmp $ rj-scanner 
    08 | 37:48:9b:89:09 | 
    08 | 37:48:9b:89:09 | 00 c2 00 00 05 a0 ff 00 00 9a
    08 | 37:48:9b:89:09 | 00 c2 00 00 01 b0 ff 00 00 8e
    08 | 37:48:9b:89:09 | 00 c2 00 00 06 b0 ff 00 00 89
    08 | 37:48:9b:89:09 | 

    pi@raspberrypi:/tmp $ rj-sniffer -t 37:48:9b:89:09
    08 | 37:48:9b:89:09 | 00 c2 00 00 04 50 00 00 00 ea
    08 | 37:48:9b:89:09 | 72 c5 54 5b 02 10 49 40 56 01
    08 | 37:48:9b:89:09 | 00 c2 00 00 04 40 00 00 00 fa
    08 | 37:48:9b:89:09 | 00 c2 00 00 04 50 00 00 00 ea
    08 | 37:48:9b:89:09 | 00 c2 00 00 05 30 00 00 00 09
    08 | 37:48:9b:89:09 | 00 c2 00 00 04 40 00 00 00 fa
    08 | 37:48:9b:89:09 | 00 c2 00 00 05 10 00 00 00 29
    08 | 37:48:9b:89:09 | 00 c2 00 00 05 30 00 00 00 09
    08 | 37:48:9b:89:09 | 00 c2 00 00 06 10 00 00 00 28
    08 | 37:48:9b:89:09 | 00 c2 00 00 05 10 00 00 00 29
    08 | 37:48:9b:89:09 | 00 c2 00 00 06 00 00 00 00 38

