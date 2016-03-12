# -*- coding: utf-8 -*-
import SocketServer
from ServerMessageParser import ServerMessageParser
import threading
import socket
import json

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
        try:

            while True:
                payload = self.connection.recv(4096)
                parsed_payload = self.request_parser.parse(payload)
                request = parsed_payload[0]
                content = parsed_payload[1]
                request_is_valid = parsed_payload[2]
                json_response = parsed_payload[3]

                # LOGIN
                if self.request_parser.is_login(request) and request_is_valid:
                    self.login_user(content)
                    print "User " + self.username + " logged in."
                    self.connection.sendall(json_response)
                    is_log, history_response = self.request_parser.get_history_response_json()
                    if is_log:
                        self.connection.sendall(history_response)

                # LOGOUT
                elif self.request_parser.is_logout(request) and request_is_valid:
                    self.connection.sendall(json_response)
                    self.logout_user()
                    print "User " + self.username + " logged out."

                elif self.request_parser.is_message(request) and request_is_valid:
                    self.send_message_to_all_clients(json_response)
                    self.log_message(json_response, self.server.log_write_lock, self.server.log_file_path)

                else:
                    self.connection.sendall(json_response)

        except socket.error:
            print "Client with IP: " + self.ip + " disconnected."
        finally:
            if self.logged_in:
                self.logout_user()
            self.connection.close()


    def login_user(self, username):
        self.username = username
        self.logged_in = True
        with self.server.logged_in_clients_lock:
            # Adding the client to the set of logged in clients
            self.server.logged_in_clients[self.username] = self.connection
        logged_in_json = self.request_parser.user_logged_in_json()
        for client in self.server.logged_in_clients:
            if not client == self.username:
                client_connection = self.server.logged_in_clients[client]
                client_connection.sendall(logged_in_json)

    def logout_user(self):
        self.logged_in = False
        self.remove_client(self.username)

    # Sends a message to all connected clients.
    # If one of the clients are disconnected, the client is removed and all other clients will be notified
    def send_message_to_all_clients(self, message_json):
        with self.server.logged_in_clients_lock:
            for client in self.server.logged_in_clients:
                client_user = client
                client_connection = self.server.logged_in_clients[client]
                try:
                    client_connection.sendall(message_json)
                except socket.error:
                    print client_user + "was disconnected."
                    self.remove_client(client_user)

    def remove_client(self, username):
        for client in self.server.logged_in_clients:
            if username == client:
                self.server.logged_in_clients.pop(username)
                self.notify_clients_on_client_logout(username)
                break

    def notify_clients_on_client_logout(self, logout_username):
        logged_out_json = self.request_parser.user_logged_out_json(logout_username)
        for client in self.server.logged_in_clients:
            client_connection = self.server.logged_in_clients[client]
            client_connection.sendall(logged_out_json)

    def log_message(self, message_json, lock, path):
        message = json.loads(message_json)
        timestamp = message['timestamp']
        sender = message['sender']
        content = message['content']
        log_string =  sender + ": " + timestamp + "\n" + content + "\n\n"
        with lock:
            with open(path, "a") as log:
                log.write(log_string)






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

    log_file_path = "/Users/Lars/Code/ktn-chat-application/Log/message_history.log"
    log_write_lock = threading.Lock()




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








