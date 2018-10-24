from carca_socket import CarcaSocket
from carca_packet import CarcaPacket
import utils
from random import randint
from time import sleep


class CarcaServer():
    def __init__(self, carca_socket, data, mss=2):
        self._data = data
        self._socket = carca_socket
        self._send_base = 0
        self._last_byte_read = 0
        self._last_packet_received = None
        self._byte_list = []
        self._mss = mss
        
    def listen(self, server_address):
        self._socket.bind(server_address)
            
    def receive_data(self):
        while True:
            client_packet, client_address = self._socket.recvfrom(4096)
            if client_packet._seq_number > self._last_byte_read:
                self._last_byte_read = client_packet._seq_number
                self._byte_list.append(client_packet._payload)
                self._last_packet_received = client_packet
                
                confirm_packet = CarcaPacket(seq_number=client_packet._ack_number,
                                     ack_number=client_packet._seq_number + client_packet._mss)

                self._socket.sendto(confirm_packet, client_address)
            else:
                confirm_packet = CarcaPacket(seq_number=self._last_packet_received._ack_number,
                                     ack_number=self._last_packet_received._seq_number + client_packet._mss)
                self._socket.sendto(confirm_packet, client_address)
            if client_packet._FIN == 1: 
                return self._byte_list