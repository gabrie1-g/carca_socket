from server import CarcaServer
from carca_socket import CarcaSocket
import utils

def main():
    data = "abcdefghijklmnopqrstuvxz"
    server_address = ('localhost', 6000)
    socket = CarcaSocket()
    server = CarcaServer(socket, data)
    server.listen(server_address)
    server.receive_data()

    
if __name__ == '__main__':
    main()

