#!/usr/bin/env python2

import logging
import sys

import smpplib.gsm
import smpplib.client
import smpplib.consts

# This is a small script using https://github.com/podshumok/python-smpplib
# to generate some SMS load on OsmoNITB via its SMPP interface

# if you want to know what's happening
logging.basicConfig(level='DEBUG')

def send_message(dest, string):
    parts, encoding_flag, msg_type_flag = smpplib.gsm.make_parts(string)

    print 'Sending SMS "%s" to %s' % (string, dest)
    for part in parts:
        pdu = client.send_message(
            source_addr_ton=smpplib.consts.SMPP_TON_INTL,
            source_addr_npi=smpplib.consts.SMPP_NPI_ISDN,
            source_addr='3802',
            dest_addr_ton=smpplib.consts.SMPP_TON_INTL,
            dest_addr_npi=smpplib.consts.SMPP_NPI_ISDN,
            destination_addr=dest,
            short_message=part,
            data_coding=encoding_flag,
            #esm_class=msg_type_flag,
            esm_class=smpplib.consts.SMPP_MSGMODE_FORWARD,
            registered_delivery=False,
    )
    print(pdu.sequence)


client = smpplib.client.Client('127.0.0.1', 2775)

# Print when obtain message_id
client.set_message_sent_handler(
    lambda pdu: sys.stdout.write('sent {} {}\n'.format(pdu.sequence, pdu.message_id)))
client.set_message_received_handler(
    lambda pdu: sys.stdout.write('delivered {}\n'.format(pdu.receipted_message_id)))

client.connect()
client.bind_transceiver(system_id='test', password='test')

destinations = ('3802', '7839', '3807', '3811', '3806', '3805', '3804', '3809', '3812', '3815', '3814', '3803', '3813')

for dest in destinations:
    send_message(dest, 'Mahlzeit')

client.listen()
