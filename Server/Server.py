# -*- coding: utf-8 -*-
import SocketServer
from ServerMessageParser import ServerMessageParser
import threading
import socket

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
        """
        Setup() is run by __init__ in BaseRequestHandler
        """
        self.ip = self.client_address[0]
        self.port = self.client_address[1]
        self.connection = self.request
        self.server = server
        self.username = ""
        self.logged_in = False
        self.request_parser = ServerMessageParser(self)




    def handle(self):
        """
        This method handles the connection between a client and the server.
        """
        print "Client connected on IP: " + self.ip


        #  Loop that listens for messages from the client
        try:

            while True:
                payload = self.connection.recv(4096)
                parsed_payload = self.request_parser.parse(payload)
                request = parsed_payload[0]
                content = parsed_payload[1]
                request_is_valid = parsed_payload[2]
                json_response = parsed_payload[3]


                # LOGIN

                if not self.logged_in:
                    if self.request_parser.is_login(request) and request_is_valid:
                        self.username = content
                        self.logged_in = True
                        with self.server.logged_in_clients_lock:
                            # Adding the client to the set of logged in clients
                            self.server.logged_in_clients[self.username] = self.connection
                        logged_out_json = self.request_parser.user_logged_in_json()
                        for client in self.server.logged_in_clients:
                            if not client == self.username:
                                client_connection = self.server.logged_in_clients[client]
                                client_connection.sendall(logged_out_json)
                        print "User " + self.username + " logged in."
                        self.connection.sendall(json_response)
                        # self.connection.sendall(self.request_parser.history_response())
                        #  TODO: Send history response, from a history log somewhere, added method but not complete
                    elif self.request_parser.is_login(request) and not request_is_valid:
                        self.connection.sendall(json_response)

                    elif self.request_parser.is_help(request) and request_is_valid:
                        self.connection.send(json_response)

                    else:
                        self.connection.sendall(self.request_parser.not_logged_in_json())

                elif self.logged_in and self.request_parser.is_login(request) and not request_is_valid:
                    # The case when the user is logged in, but is still trying to login
                    self.connection.sendall(json_response)


                # LOGOUT

                elif self.request_parser.is_logout(request) and request_is_valid:
                    self.connection.sendall(json_response)
                    self.logged_in = False
                    self.server.logged_in_clients.pop(self.username)
                    logged_out_json = self.request_parser.user_logged_out_json()
                    for client in self.server.logged_in_clients:
                        client_connection = self.server.logged_in_clients[client]
                        client_connection.sendall(logged_out_json)
                    print "User " + self.username + " logged out."

                elif self.request_parser.is_logout(request) and not request_is_valid:
                    self.connection.sendall(json_response)


                # MESSAGE

                elif self.request_parser.is_message(request) and request_is_valid:
                    with self.server.logged_in_clients_lock:
                            for client in self.server.logged_in_clients:
                                client_user = client
                                client_connection = self.server.logged_in_clients[client]
                                try:
                                    client_connection.sendall(json_response)
                                except socket.error:
                                    print "Something went wrong when sending to client " + client_user

                elif self.request_parser.is_message(request) and not request_is_valid:
                    # Send only to the requesting client. This will be an error message.
                    self.connection.sendall(json_response)


                # NAMES

                elif self.request_parser.is_names(request) and request_is_valid:
                    self.connection.sendall(json_response)

                elif self.request_parser.is_names(request) and not request_is_valid:
                    self.connection.sendall(json_response)


                # HELP

                elif self.request_parser.is_help(request) and request_is_valid:
                    self.connection.sendall(json_response)

                elif self.request_parser.is_help(request) and not request_is_valid:
                    self.connection.sendall(json_response)


                # IF NO VALID REQUEST

                else:
                    # General message that tells the client that the received request is not valid
                    self.connection.sendall(self.request_parser.request_not_valid_json())

        finally:
            self.connection.close()
            print "Client with IP: " + self.ip + " disconnected."







class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    """
    This class is present so that each client connected will be ran as a own
    thread. In that way, all clients will be served by the server.

    No alterations are necessary
    """
    allow_reuse_address = True

    # Hold all logged in clients
    logged_in_clients = {}
    logged_in_clients_lock = threading.Lock()





if __name__ == "__main__":
    """
    This is the main method and is executed when you type "python Server.py"
    in your terminal.

    No alterations are necessary
    """
    HOST, PORT = 'localhost', 10005
    print "Server running..."
    # Set up and initiate the TCP server
    server = ThreadedTCPServer
    try:
        server = ThreadedTCPServer((HOST, PORT), ClientHandler)
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        print "Server shutdown..."
        server.shutdown()
        server.server_close()








