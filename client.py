from carca_socket import CarcaSocket
from carca_packet import CarcaPacket
from random import randint
from time import sleep, time
from threading import Thread
import utils
#initial timeout
timeout = 1;
flag = False

class CarcaClient():
    def __init__(self, carca_socket, data, server_address, mss=2):
        self._socket = carca_socket
        self._last_byte_read = 0
        self._send_base = 0
        self._data = data
        self._last_sent = None
        self._mss = mss
        self._byte_list = []
        self._server_address = server_address
        
    def listen(self, client_address):
        self._socket.bind(client_address)
        
    def resend_packet(self):
        thread = Thread(target = self.verify)
        self._socket.sendto(self._last_sent, self._server_address)
        thread.start()
            
    def verify(self):
        global flag
        global timeout
        start = time()
        end = time()
        while end - start < timeout:
            end = time()
            if flag: break
        if flag == False: 
          print('haha timeout')
          self.resend_packet()
        
    def send_segment(self):
        global flag
        byte_string = utils.serialize_to_string(self._data)
        segments_list = utils.string_to_segments(byte_string, self._mss)

        _last_sent = packet = CarcaPacket(seq_number=1, ack_number=0, payload=segments_list[0])
        self._send_base = packet._seq_number
        thread = Thread(target = self.verify)        
        self._socket.sendto(packet, self._server_address)
        thread.start()
        i = 0
        while i < len(segments_list):
            server_packet, _ = self._socket.recvfrom(4096)
            if thread.is_alive(): flag = True

            if server_packet._ack_number > self._send_base:
                self._send_base = server_packet._ack_number
                i += 1
            if i == len(segments_list): 
                print(i)
                break
            packet = CarcaPacket(seq_number=server_packet._ack_number, ack_number=server_packet._seq_number + 1,      payload=segments_list[i])
            if i == len(segments_list) - 1:
                packet._FIN = 1
            thread = Thread(target = self.verify)
            self._socket.sendto(packet, self._server_address)
            flag = False
            thread.start()
                      
