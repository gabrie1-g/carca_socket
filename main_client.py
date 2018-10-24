from client import CarcaClient
from carca_socket import CarcaSocket


def main():
    data = "Isso foi mais complicado do que eu pensei carajo"
    server_address = ('localhost', 6000)
    socket = CarcaSocket()
    client = CarcaClient(socket, data)
    client.send_segment(server_address)

if __name__ == '__main__':
    main()
