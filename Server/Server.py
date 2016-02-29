# -*- coding: utf-8 -*-
import SocketServer
from ServerMessageParser import ServerMessageParser

"""
Variables and functions that must be used by all the ClientHandler objects
must be written here (e.g. a dictionary for connected clients)
"""


class ClientHandler(SocketServer.BaseRequestHandler):

    """
    This is the ClientHandler class. Everytime a new client connects to the
    server, a new ClientHandler object will be created. This class represents
    only connected clients, and not the server itself. If you want to write
    logic for the server, you must write it outside this class
    """

    def setup(self):
        self.ip = self.client_address[0]
        self.port = self.client_address[1]
        self.connection = self.request
        self.request_parser = ServerMessageParser(self)
        self.client_username = ""
        self.logged_in = False

    def handle(self):
        """
        This method handles the connection between a client and the server.
        """
        print "Client connected on IP: " + self.ip

        #  Loop that listens for messages from the client
        while True:
            #  TODO: handle large payloads properly. (E.g. add /r/n in client message and check for it)
            payload = self.connection.recv(4096)
            parsed_payload = self.request_parser.parse(payload)
            request = parsed_payload[0]
            content = parsed_payload[1]
            request_is_valid = parsed_payload[2]
            json_response = parsed_payload[3]
            #  TODO: Might want to clean up connections every iteration (e.g. check if connection is still up)
            if not self.logged_in:
                if self.request_parser.is_login(request) and request_is_valid:
                    self.logged_in = True
                    self.connection.send(json_response)
                    # self.connection.send(self.request_parser.history_response())
                    #  TODO: Send history response, from a history log somewhere, added method but not complete
                    #  TODO: Add connection + username to list of connected clients. But how?
                elif self.request_parser.is_help(request) and request_is_valid:
                    self.connection.send(json_response)
                else:
                    self.connection.send(self.request_parser.not_logged_in_json())
                    #  TODO: close connection
            elif self.request_parser.is_logout(request) and request_is_valid:
                self.connection.send(json_response)
                self.logged_in = False
                # TODO: Handle removal of user
            elif self.request_parser.is_message(request) and request_is_valid:
                self.connection.send(json_response)
                #  TODO: send to all connected clients, log the response in a file (history)
            elif self.request_parser.is_message(request) and not request_is_valid:
                # Send only to the requesting client. This will be an error message.
                self.connection.send(json_response)
            elif request_is_valid:
                # If the request is parsed and valid according to the rules in ServerMessageParser
                # The 'names' and 'help' request will currently be responded here
                # Only send to the client that asked
                self.connection.send(json_response)
            else:
                # General message that tells the client that the received request is not valid
                self.connection.send(self.request_parser.request_not_valid_json())


class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    """
    This class is present so that each client connected will be ran as a own
    thread. In that way, all clients will be served by the server.

    No alterations are necessary
    """
    allow_reuse_address = True


if __name__ == "__main__":
    """
    This is the main method and is executed when you type "python Server.py"
    in your terminal.

    No alterations are necessary
    """
    HOST, PORT = 'localhost', 9998
    print 'Server running...'

    # Set up and initiate the TCP server
    server = ThreadedTCPServer((HOST, PORT), ClientHandler)
    server.serve_forever()
