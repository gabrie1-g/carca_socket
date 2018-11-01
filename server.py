from carca_socket import CarcaSocket
from carca_packet import CarcaPacket
import utils
from random import randint
from time import sleep


class CarcaServer():
    def __init__(self, carca_socket, data):
        self._data = data
        self._socket = carca_socket
        self._last_acked = 0
        self._byte_list = []
        #self._mss = mss
        self._window_backup = []
        
    def listen(self, server_address):
        self._socket.bind(server_address)

    def receive_data(self):
        while True:
            client_packet, client_address = self._socket.recvfrom(4096)
            print(client_packet._seq_number)
            if client_packet._seq_number == self._last_acked: continue
            elif client_packet._seq_number > self._last_acked and client_packet._FIN == 0:
                self._last_acked = client_packet._seq_number
                self._byte_list.append(client_packet._payload)
                confirm_packet = CarcaPacket(ack_number=client_packet._seq_number + client_packet._mss)
                sleep(2)
                self._socket.sendto(confirm_packet, client_address)
            elif client_packet._FIN == 1:
                endcnn_packet = CarcaPacket(ack_number=client_packet._seq_number + client_packet._mss)
                endcnn_packet._FIN = 1
                self._byte_list.append(client_packet._payload)
                self._socket.sendto(endcnn_packet, client_address)
                self.show_data() 
                self.reset_server()
                
    def show_data(self):
      encoded_data = self._byte_list
      encoded_data = utils.string_from_segments(encoded_data)
      decoded_data = utils.parse_from_string(encoded_data)
      print(decoded_data)

      
    def reset_server(self):
        self._last_acked = 0
        self._byte_list = [] 
