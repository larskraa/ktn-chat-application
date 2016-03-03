import json
import time
import re

"""
    Contains methods for
    - parsing payloads from clients,
    - error handling,
    - generating json responses that can be sent to clients,
    etc.
"""


class ServerMessageParser:

    def __init__(self, client_handler_class):

        self.server_name = "Chat-server"
        self.client_handler_class = client_handler_class
        self.server = self.client_handler_class.server

        # Possible response from server to client
        self.error_response = 'error'
        self.info_response = 'info'
        self.message_response = 'message'
        self.history_response = 'history'

        # Possible requests from client to server
        self.login_request = 'login'
        self.logout_request = 'logout'
        self.message_request = 'msg'
        self.names_request = 'names'
        self.help_request = 'help'

        #  Used by parse() to access specific parsing methods
        self.possible_requests = {
            self.login_request: self.parse_login,
            self.logout_request: self.parse_logout,
            self.message_request: self.parse_msg,
            self.names_request: self.parse_names,
            self.help_request: self.parse_help
        }

        self.login_error_message = "You are not logged in. Enter 'login <username>' to log in.\n" \
                                   "<username> must be between 3 and 20 normal characters. [a-z, A-Z, 0-9, _]"


    def parse(self, payload):
        # Assumes that the payload is in json format
        payload = json.loads(payload)
        if payload['request'] in self.possible_requests:
            return self.possible_requests[payload['request']](payload)
        else:
            # invalid request (feedback to client: use 'help')
            return payload['request'], payload['content'], False, self.request_not_valid_json()


    """
        Each of the specific parse methods returns a tuple with:
            - request ('login', 'msg', etc.), as a string
            - content, as a string
            - validity, as a boolean
            - appropriate response message, as valid json
        The request and content may be used by the server logic for
        checking for valid requests etc.
        The validity attribute is True if there was nothing wrond with the data
        in the request.
        If the request is valid, the json response may be sent to the client(s)
    """

    def parse_login(self, payload):
        verified_request = self.verify_login_request(payload)
        request = payload['request']
        content = payload['content']
        valid_request = verified_request[0]
        json_response = self.get_login_response_json(verified_request, content)
        return request, content, valid_request, json_response

    def parse_logout(self, payload):
        verified_request = self.verify_logout_request(payload)
        request = payload['request']
        content = payload['content']
        valid_request = verified_request[0]
        json_response = self.get_logout_response_json(verified_request)
        return request, content, valid_request, json_response

    def parse_msg(self, payload):
        verified_request = self.verify_msg_request(payload)
        request = payload['request']
        content = payload['content']
        valid_request = verified_request[0]
        json_response = self.get_message_response_json(verified_request, content, self.client_handler_class.username)
        return request, content, valid_request, json_response

    def parse_names(self, payload):
        verified_request = self.verify_names_request(payload)
        request = payload['request']
        content = payload['content']
        valid_request = verified_request[0]
        json_response = self.get_names_response_json(self.server.logged_in_clients, verified_request)  # TODO: WHERE DO WE GLOBALLY STORE LOGGED IN USERS AND CONNECTIONS??
        return request, content, valid_request, json_response

    def parse_help(self, payload):
        verified_request = self.verify_help_request(payload)
        request = payload['request']
        content = payload['content']
        valid_request = verified_request[0]
        json_response = self.get_help_response_json(verified_request)
        return request, content, valid_request, json_response


    """
        Methods for coding json response messages
    """
    def get_login_response_json(self, verified_request, username):
        valid = verified_request[0]
        error_message = verified_request[1]
        if not valid:
            response = self.error_response
            content = error_message
        else:
            response = self.info_response
            content = "Login successful. Welcome to the chat " + username + "."
        return self.encode_response_to_json(self.server_name, response, content)

    def get_logout_response_json(self, verified_request):
        valid = verified_request[0]
        error_message = verified_request[1]
        if not valid:
            response = self.error_response
            content = error_message
        else:
            response = self.info_response
            content = "Logout successful. Bye."
        return self.encode_response_to_json(self.server_name, response, content)

    def get_message_response_json(self, verified_request, content, sender):
        valid = verified_request[0]
        error_message = verified_request[1]
        if not valid:
            response = self.error_response
            content = error_message
        else:
            response = self.message_response
        return self.encode_response_to_json(sender, response, content)

    def get_names_response_json(self, usernames, verified_request):
        # usernames is assumed to be a dictionary
        valid = verified_request[0]
        error_message = verified_request[1]
        if not valid:
            response = self.error_response
            content = error_message
        else:
            response = self.info_response
            content = "Logged in users:\n"
            for username in usernames:
                content += ("- " + username + "\n")
        return self.encode_response_to_json(self.server_name, response, content)

    def get_help_response_json(self, verified_request):
        valid = verified_request[0]
        error_message = verified_request[1]
        if not valid:
            response = self.error_response
            content = error_message
        else:
            response = self.info_response
            content = 'Possible requests:\n' \
                '- login <username>       3-20 normal characters (a-z, A-Z, 0-9, _)\n' \
                '- logout                 logout from the chat\n' \
                '- msg <content>          send a message to all logged in users\n' \
                '- names                  get a list of all logged in users\n' \
                '- help                   get a list of possible actions\n'
        return self.encode_response_to_json(self.server_name, response, content)

    def get_history_response_json(self, history_file_path):
        pass  # Read from file and return history as json



    """
        Methods for checking request validity
        Each method should check if the payload is valid for that specific request,
        and create an appropriate error message is not valid.
        E.g. if it is not valid False should be returned with an error message as a tuple
        Respond with tuple (True, "") or (False, "error message")
    """

    def verify_login_request(self, payload):
        # Check if username contains only allowed characters
        # Check if username is not taken
        # Respond with tuple (True, "") or (False, "error message")
        username = payload['content']
        valid = True
        error_message = ""
        username_taken = False
        for client in self.server.logged_in_clients:
            # Checking for valid usernames
            if username == client:
                username_taken = True
        if self.client_handler_class.logged_in:
            valid = False
            error_message = "You are already logged in."
        elif len(username) < 3 or len(username) > 20 or not re.match("^[a-zA-Z0-9_]*$", username):
            valid = False
            error_message = "If you are trying to log in, enter 'login <username>.'\n" \
                            "<username> must be between 3 and 20 normal characters. [a-z, A-Z, 0-9, _]"
        elif username_taken:
            valid = False
            error_message = "That username has already been taken. Try another one."
        return valid, error_message

    def verify_logout_request(self, payload):
        # Should return false if there is actual content attached
        # with the "logout" keyword
        if self.client_handler_class.logged_in:
            valid = True
            error_message = ""
            if not payload['content'] == 'None':
                valid = False
                error_message = "If you are trying to log out, enter 'logout' without additional content."
        else:
            valid = False
            error_message = self.login_error_message
        return valid, error_message

    def verify_msg_request(self, payload):
        if self.client_handler_class.logged_in:
            valid = True
            error_message = ""
        else:
            valid = False
            error_message = self.login_error_message
        return valid, error_message

    def verify_names_request(self, payload):
        # Should return false if there is actual content attached
        # with the "names" keyword
        if self.client_handler_class.logged_in:
            valid = True
            error_message = ""
            if not payload['content'] == 'None':
                valid = False
                error_message = "Enter 'names' without additional content to get a list og logged in users."
        else:
            valid = False
            error_message = self.login_error_message
        return valid, error_message

    def verify_help_request(self, payload):
        # Should return false if there is actual content attached
        # with the "help" keyword
        valid = True
        error_message = ""
        if not payload['content'] == 'None':
            valid = False
            error_message = "Enter 'help' without additional content for a list of possible actions."
        return valid, error_message




    """
        Methods for checking request type
    """

    def is_login(self, request):
        return request == self.login_request

    def is_logout(self, request):
        return request == self.logout_request

    def is_message(self, request):
        return request == self.message_request

    def is_help(self, request):
        return request == self.help_request

    def is_names(self, request):
        return request == self.names_request

    def is_possible_request(self, request):
        for possible_request in self.possible_requests:
            if self.possible_requests[possible_request] == request:
                return True
        return False



    """
        Methods for retrieving different kinds of json to be sent as a response to clients
        Protocol needs the json to include the following content and structure:

        {
            'timestamp': <time and date>
            'sender': <who sent the message>
            'response': <response type>
            'content': the content of the response displayed to the client user
        }
    """

    @staticmethod
    def encode_response_to_json(sender, response, content):
        # Encodes a server respond message into json
        # Local time in format 'Tue Jan 13 10:17:09 2009'
        localtime = time.asctime(time.localtime(time.time()))

        response_message = \
            {
                'timestamp': localtime,
                'sender': sender,
                'response': response,
                'content': content
            }

        return json.dumps(response_message)

    def not_logged_in_json(self):
        # Local time in format 'Tue Jan 13 10:17:09 2009'
        localtime = time.asctime(time.localtime(time.time()))
        response_message = \
            {
                'timestamp': localtime,
                'sender': self.server_name,
                'response': self.error_response,
                'content': "You are not logged in. Enter 'login <username>' to log in.\n"
                           "<username> must be between 3 and 20 normal characters. [a-z, A-Z, 0-9, _]"
            }
        return json.dumps(response_message)

    def request_not_valid_json(self):
        # Local time in format 'Tue Jan 13 10:17:09 2009'
        localtime = time.asctime(time.localtime(time.time()))
        response_message = \
            {
                'timestamp': localtime,
                'sender': self.server_name,
                'response': self.error_response,
                'content': "That request is not valid. Enter 'help' for a list of possible actions."
            }
        return json.dumps(response_message)

    def user_logged_out_json(self, username):
        # Local time in format 'Tue Jan 13 10:17:09 2009'
        localtime = time.asctime(time.localtime(time.time()))
        response_message = \
            {
                'timestamp': localtime,
                'sender': self.server_name,
                'response': self.info_response,
                'content': username + " logged out."
            }
        return json.dumps(response_message)

    def user_logged_in_json(self):
        # Local time in format 'Tue Jan 13 10:17:09 2009'
        localtime = time.asctime(time.localtime(time.time()))
        response_message = \
            {
                'timestamp': localtime,
                'sender': self.client_handler_class.username,
                'response': self.info_response,
                'content': self.client_handler_class.username + " logged in."
            }
        return json.dumps(response_message)

