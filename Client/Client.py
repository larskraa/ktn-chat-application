# -*- coding: utf-8 -*-
import socket
from MessageReceiver import MessageReceiver
from ClientMessageParser import ClientMessageParser


class Client:
    """
    This is the chat client class
    """

    # Set to True if you wish to exit the chat client
    exit = False

    def __init__(self, host, server_port):
        """
        This method is run when creating a new Client object
        """

        # Set up the socket connection to the server
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = (host, server_port)

        # Initiate the message parser class
        self.client_message_parser = ClientMessageParser()
        self.run()

    def run(self):
        # Initiate the connection to the server
        self.connection.connect(self.server_address)

        # Initiate the message receiver class as a new thread and start the thread
        message_receiver_thread = MessageReceiver(self, self.connection)
        message_receiver_thread.start()

        # Run until the user sets exit to False
        while not self.exit:
            payload = raw_input(">")
            if payload == 'exit':
                self.exit = True
                break
            encoded_message = self.client_message_parser.parse_user_input(payload)
            if not encoded_message[0]:
                print encoded_message[1]
            else:
                print encoded_message[1]
                self.send_payload(encoded_message[1])

        self.disconnect()
        print "Disconnected from server."
        # TODO: handle logouts with exit?


    def disconnect(self):
        # TODO: Handle disconnection
        self.connection.close()

    def receive_message(self, message):
        # TODO: Handle incoming message, is it problematic to run this from another thread?
        print message

    def send_payload(self, data):
        # TODO: Handle sending of a payload
        self.connection.send(data)


if __name__ == '__main__':
    """
    This is the main method and is executed when you type "python Client.py"
    in your terminal.

    No alterations are necessary
    """
    client = Client('localhost', 9998)
