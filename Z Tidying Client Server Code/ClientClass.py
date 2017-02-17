
import socket
import select
import ssl
import sys
import struct

# Message format is:
#   4 bytes unsigned type
#   4 bytes unsigned length
#   Message data

class Client:


    def __init__(self, HOST, PORT):
        try:
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.ssl_socket = ssl.wrap_socket(server_socket, ca_certs="server.crt", cert_reqs=ssl.CERT_REQUIRED)
            self.ssl_socket.connect((HOST, PORT))

        except Exception as e:
            print(e)
            print("Completed with Exception1.", "\n")
            pass


    def listening(self):

        while True:

            # 6. check if input has been received from stdin or the server_socket
            available_streams, _, _ = select.select([sys.stdin, self.ssl_socket], [], [], 1)

            # 7. if sys.stdin is available to read, read from it and send the message
            if sys.stdin in available_streams:
                msg_text = sys.stdin.readline()
                Message.send_msg(self, Message.TYPES["NORMAL"], msg_text, self.ssl_socket)
                continue

            # 8. if the server socket is available to read, read from it and print the message
            if self.ssl_socket in available_streams:
                msg_type, msg_text = Message.receive_msg_from(self, self.ssl_socket)
                Message.print_message(self, msg_type, msg_text)



    def raw_receive(self, sock, length):
        """This function receives length bytes of raw data from a socket, returning the data."""

        chunks = []
        bytes_rx = 0

        while bytes_rx < length:
            chunk = sock.recv(length - bytes_rx)
            if chunk == b'':
                raise RuntimeError("Socket connection broken")
            chunks.append(chunk)
            bytes_rx += len(chunk)
        return b''.join(chunks)


    def raw_send(self, sock, length, data):
        """ This function sends raw data on a socket."""

        total_sent = 0

        while total_sent < length:
            sent = sock.send(data[total_sent:])
            if sent == 0:
                raise RuntimeError("Socket send failure")
            total_sent = total_sent + sent






class Message:

    TYPES = {"NORMAL": 0,          #0
             "JOIN": 1,            #1
             "USER": 2,            #2
             "PASS": 3,            #3
             "DIRECT": 4,          #4
             "COMMAND": 5,         #5
             "SERVER": 6}          #6
    HEADER_LENGTH = 8

    def __init__(self):
        pass


    def send_msg(self, msg_type, msg_text, sock):
        """This function sends a message to a socket."""

        #print("sending ", msg_text)
        full_msg = struct.pack('!LL', msg_type, len(msg_text) - 1) + bytes(msg_text.strip().encode("utf-8"))  # cut off a newline

        Client.raw_send(self, sock, len(full_msg), full_msg)


    def receive_msg_from(self, sock):
        """This function waits for a message on a socket and returns the message type and text."""

        header = Client.raw_receive(self, sock, Message.HEADER_LENGTH)
        (msg_type, msg_length) = struct.unpack('!LL', header)

        try:
            msg_text = Client.raw_receive(self, sock, msg_length).decode("utf-8")
            return msg_type, msg_text

        except MemoryError as err:
            print("MemoryError: " + err.message)
            return None


    def print_message(self, msg_type, msg_text):
        """This function prints a message with the text length in a nice format."""

        print((next(iter({k for k, v in Message.TYPES.items() if v == msg_type}))), len(msg_text), msg_text)



