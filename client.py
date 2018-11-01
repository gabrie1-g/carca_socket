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
        self._window_backup = {}
        self._server_address = server_address
        self._cwnd = 4 * mss
        self.window_setup_ini()
        self.create_segments()

    def window_setup_ini(self):
        global window_state
        global current_window
        window_state = self._cwnd
        current_window = [self._send_base, self._cwnd]
        
    def create_segments(self):
        global segments_list
        byte_string = utils.serialize_to_string(self._data)
        segments_list = utils.string_to_segments(byte_string, self._mss)
        
    def listen(self, client_address):
        self._socket.bind(client_address)
        
    def resend_packet(self, packet):
        #self._socket.sendto(self._last_sent, self._server_address)
        self._socket.sendto(packet, self._server_address)
        
    def send_packet(self):
        global index
        global window_state       
        ws_lock.acquire()
        if index == 0:
            packet = CarcaPacket(seq_number=1)
            packet._payload = segments_list[index]
            self._window_backup[str(packet._seq_number)] = packet
            index += 1
            window_state -= self._mss
            self._send_base = packet._seq_number
            timeout_verifier = Thread(target=self.verify, args=(packet,))
            self._socket.sendto(packet, self._server_address)
            timeout_verifier.start()
            timeout_verifier.join()
        for i in range(0, (int) (window_state / self._mss)):
            packet = CarcaPacket(seq_number=self._send_base + self._mss)
            if index == len(segments_list) - 1:
                packet._FIN = 1
            packet._payload = segments_list[index]
            self._window_backup[str(packet._seq_number)] = packet
            index += 1
            window_state -= self._mss
            self._send_base = packet._seq_number
            timeout_verifier = Thread(target=self.verify, args=(packet,))
            self._socket.sendto(packet, self._server_address)
            timeout_verifier.start()
            timeout_verifier.join()
        ws_lock.release()
        
            
    def process_ack(self, packet):
        global window_state
        global current_window
        ws_lock.acquire()
        if packet._ack_number - self._mss > current_window[0] and packet._ack_number - self._mss < current_window[1]:
            del self._window_backup[str(packet._ack_number - self._mss)]
            current_window[0] += self._mss
            current_window[1] += self._mss
            window_state += self._mss
        ws_lock.release()
            
    def verify(self, packet):
        global flag
        global timeout
        start = time()
        end = time()
        while end - start < timeout:
            end = time()
            if flag: break
        if flag == False: 
            thread = Thread(target = self.resend_packet, args=(packet,))
            thread.start()
            #thread.join()
            
            
    def send_segment(self):
        global flag
        global index
        global aux
        
        send_thread = Thread(target=self.send_packet)
        send_thread.start()

        ws_lock.acquire()
        while index < len(segments_list):
            if not aux: 
              ws_lock.release() 
              aux = True
            server_packet, _ = self._socket.recvfrom(4096)
            print(server_packet._ack_number)
            if send_thread.is_alive(): send_thread.join()
            if server_packet._FIN == 1: break
            if server_packet._ack_number > self._send_base:
                self.process_ack(server_packet)
            send_thread = Thread(target=self.send_packet)
            send_thread.start()