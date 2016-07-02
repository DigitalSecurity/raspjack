from setuptools import setup

setup(
    name = 'raspjack',
    version = '1.0',
    author = 'Damien Cauquil',
    author_email = 'damien.cauquil@digitalsecurity.fr',
    description = 'RaspJack is a port of MouseJack for Raspberry Pi 1/2 and cheap NRF24L01+ modules.',
    license = 'MIT',
    keywords = 'nrf24 mousejack rasppi raspberry pi',
    packages = ['raspjack','bin'],
    entry_points = {
        'console_scripts':[
            'rj-sniffer = bin:sniffer',
            'rj-scanner = bin:scanner'
        ]
    }
)
