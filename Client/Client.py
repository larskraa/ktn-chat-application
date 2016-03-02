# -*- coding: utf-8 -*-
import socket
import time
from MessageReceiver import MessageReceiver
from ClientMessageParser import ClientMessageParser
from MessageSender import MessageSender


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
        self.message_sender_thread = MessageSender
        self.message_receiver_thread = MessageReceiver
        self.run()

    def run(self):
        # Initiate the connection to the server
        self.connection.connect(self.server_address)

        # Instantiate the message receiver class as a new thread and start the thread
        self.message_receiver_thread = MessageReceiver(self, self.connection)
        self.message_receiver_thread.start()

        # Instantiate the message sender class as a new thread and start the thread
        self.message_sender_thread = MessageSender(self, self.connection)
        self.message_sender_thread.start()

        # Run until the user sets exit to False
        try:
            while not self.exit:
                payload = raw_input("")
                print "\n"
                if payload == 'exit':
                    self.exit = True
                    break
                elif self.input_is_valid(payload):
                    encoded_message = self.client_message_parser.parse_user_input(payload)
                    self.message_sender_thread.queue_payload_for_sending(encoded_message)
        finally:
            # Have to wait for the logout message to actually be sent
            self.disconnect()
            print "Disconnected from server."

    def disconnect(self):
        self.connection.close()

    def input_is_valid(self, payload):
        return not len(payload.strip()) == 0



if __name__ == '__main__':
    """
    This is the main method and is executed when you type "python Client.py"
    in your terminal.

    No alterations are necessary
    """
    client = Client('localhost', 10005)
