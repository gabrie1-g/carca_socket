from carca_socket import CarcaSocket
from carca_packet import CarcaPacket
from random import randint
from time import sleep, time
from threading import Thread, Lock
import utils
#initial timeout
index = 0
timeout = 1;
flag = False
window_state = None
current_window = None
ws_lock = Lock()
aux = False
segments_list = []       

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
        self._cwnd = 4 * mss
        self.window_setup_ini()
        self.create_segments()
        
    def window_setup_ini(self):
        global window_state
        global current_state
        window_state = self._cwnd
        current_window = self._send_base, self._cwnd
        
    def create_segments(self):
        global segments_list
        byte_string = utils.serialize_to_string(self._data)
        segments_list = utils.string_to_segments(byte_string, self._mss)
        
    def listen(self, client_address):
        self._socket.bind(client_address)
        
    def resend_packet(self):
        self._socket.sendto(self._last_sent, self._server_address)
    
    def send_packet(self, packet):
        global index
        global window_state       
        ws_lock.acquire()
        if index == 0:
            packet._payload = segments_list[index]
            index += 1
            window_state -= self._mss
            self._send_base = packet._seq_number
            self._socket.sendto(packet, self._server_address)
            print("enviei")
        for i in range(0, (int) (window_state / self._mss)):
            packet = CarcaPacket(seq_number=self._send_base + self._mss)
            packet._payload = segments_list[index]
            self._socket.sendto(packet, self._server_address) 
            index += 1
            window_state -= self._mss
            self._send_base = packet._seq_number
            print("enviei")
        ws_lock.release()
        
            
    def process_ack(self, packet):
        ws_lock.acquire()
        window_state += self._mss
        #if packet._ack_number > self._send_base and packet._ack_number < self._cwnd:
            
        ws_lock.release()
            
    def verify(self):
        global flag
        global timeout
        start = time()
        end = time()
        while end - start < timeout:
            end = time()
            if flag: break
        if flag == False: 
            thread = Thread(target = self.resend_packet())
            thread.start()
            thread.join()
        
    def send_segment(self):
        global flag
        global index
        global aux
        self._last_sent = packet = CarcaPacket(seq_number=1)
        self._send_base = packet._seq_number
        
        
        send_thread = Thread(target=self.send_packet, args=(packet,))
        send_thread.start()
        
        #self._last_sent = packet = CarcaPacket(seq_number=1, ack_number=0, payload=segments_list[0])
        #self._send_base = packet._seq_number
        timeout_verifier = Thread(target = self.verify)        
        #self._socket.sendto(packet, self._server_address)
        timeout_verifier.start()
        #i = 0
        ws_lock.acquire()
        while index < len(segments_list):
            if not aux: 
              ws_lock.release() 
              aux = True
            server_packet, _ = self._socket.recvfrom(4096)
            print(server_packet._ack_number)
            if timeout_verifier.is_alive(): 
                if flag == False: flag = True
            if server_packet._FIN == 1: break
            if server_packet._ack_number > self._send_base:
                self._send_base = server_packet._ack_number
                #i += 1
            #self._last_sent = packet = CarcaPacket(ack_number=server_packet._seq_number + 1, payload=segments_list[i])
            if index == len(segments_list) - 1:
                packet._FIN = 1
            thread = Thread(target = self.verify)
            flag = False
            self._socket.sendto(packet, self._server_address)
            thread.start()    
        cwnd_verifier.join()      
