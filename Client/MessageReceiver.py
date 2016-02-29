# -*- coding: utf-8 -*-
from threading import Thread
from ClientMessageParser import ClientMessageParser


class MessageReceiver(Thread):
    """
    This is the message receiver class. The class inherits Thread, something that
    is necessary to make the MessageReceiver start a new thread, and it allows
    the chat client to both send and receive messages at the same time
    """

    def __init__(self, client, connection):
        """
        This method is executed when creating a new MessageReceiver object
        """
        Thread.__init__(self)
        # Flag to run thread as a deamon
        self.daemon = True
        self.client = client
        self.connection = connection
        self.client_message_parser = ClientMessageParser()

        # TODO: Finish initialization of MessageReceiver

    def run(self):
        # TODO: Make MessageReceiver receive and handle payloads
        while True:
            payload = self.connection.recv(4096)
            message = self.client_message_parser.parse(payload)
            self.client.receive_message(message)
            # TODO: handle large payloads




