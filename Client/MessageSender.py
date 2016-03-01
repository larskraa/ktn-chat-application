# -*- coding: utf-8 -*-
from threading import Thread
from ClientMessageParser import ClientMessageParser
from Queue import Queue


class MessageSender(Thread):

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
        self.payload_queue = Queue()



    def run(self):
        while True:
            if not self.payload_queue.empty():
                payload = self.payload_queue.get()
                self.send_payload_from_queue(payload)



    def queue_payload_for_sending(self, payload):
        self.payload_queue.put(payload)



    def send_payload_from_queue(self, payload):
        self.connection.sendall(payload)
