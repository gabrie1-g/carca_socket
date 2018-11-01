from client import CarcaClient
from carca_socket import CarcaSocket


def main():
    #data = []
    #for i in range(0, 1000):
    #  data.append(i)
    data = 'abcdefghijlmnopqrstuvxz'
    server_address = ('localhost', 6000)
    socket = CarcaSocket()
    client = CarcaClient(socket, data, server_address)
    client.send_segment()

if __name__ == '__main__':
    main()
