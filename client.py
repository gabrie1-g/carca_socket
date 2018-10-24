from carca_socket import CarcaSocket
from carca_packet import CarcaPacket
from random import randint
from time import sleep
import utils


class CarcaClient():
    def __init__(self, carca_socket, data, mss=2):
        self._socket = carca_socket
        self._last_byte_read = 0
        self._send_base = 0
        self._data = data
        self._last_packet_sent = None
        self._mss = mss
        self._byte_list = []
        
    def listen(self, client_address):
        self._socket.bind(client_address)
       
    def send_segment(self, server_address):
        
        byte_string = utils.serialize_to_string(self._data)
        segments_list = utils.string_to_segments(byte_string, self._mss)

        packet = CarcaPacket(seq_number=1, ack_number=0, payload=segments_list[0])
        self._send_base = packet._seq_number
        self._socket.sendto(packet, server_address)
        
        i = 0
        while i < len(segments_list) - 1:
            server_packet, _ = self._socket.recvfrom(4096)
            if server_packet._ack_number > self._send_base:
                self._send_base = server_packet._ack_number
                i += 1
            packet = CarcaPacket(seq_number=server_packet._ack_number, ack_number=server_packet._seq_number + 1, payload=segments_list[i])
            if i == len(segments_list) - 1:
                packet._FIN = 1
            self._socket.sendto(packet, server_address)          