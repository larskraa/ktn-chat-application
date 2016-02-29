import json
import time

"""
    Contains methods for
    - parsing payloads from clients,
    - error handling,
    - generating json responses that can be sent to clients,
    etc.
"""


class ServerMessageParser:

    def __init__(self, server):

        self.server_name = "Chat-server"
        self.server = server  # Hopefully we can get usernames etc. from here

        """
            Possible responds from server to clients
        """
        self.error_response = 'error'
        self.info_response = 'info'
        self.message_response = 'message'
        self.history_response = 'history'

        """
            Possible requests from client to server
        """
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

    def parse(self, payload):
        # Assumes that the payload is in json format
        # Converts the json to a python dictionary
        payload = json.loads(payload)

        if payload['request'] in self.possible_requests:
            return self.possible_requests[payload['request']](payload)
        else:
            # invalid request (feedback to client: use 'help')
            return self.request_not_valid_json()

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
        valid_request = self.verify_login_request(payload)
        return payload['request'], payload['content'], valid_request[0], \
               self.login_response(valid_request)

    def parse_logout(self, payload):
        valid_request = self.verify_logout_request(payload)
        return payload['request'], payload['content'], valid_request[0], \
               self.logout_response(valid_request)

    def parse_msg(self, payload):
        valid_request = self.verify_msg_request(payload)
        return payload['request'], payload['content'], valid_request[0], \
               self.message_response(" ", payload['content'], valid_request)
    #TODO: Fix this error message

    def parse_names(self, payload):
        valid_request = self.verify_names_request(payload)
        return payload['request'], payload['content'], valid_request[0], \
               self.names_response([], valid_request)  #  TODO: WHERE DO WE GLOBALLY STORE LOGGED IN USERS AND CONNECTIONS??

    def parse_help(self, payload):
        valid_request = self.verify_help_request(payload)
        return payload['request'], payload['content'], valid_request[0], \
               self.help_response(valid_request)

    """
        Methods for coding json response messages
    """
    def login_response(self, verified_request):
        valid = verified_request[0]
        error_message = verified_request[1]
        if not valid:
            response = self.error_response
            content = error_message
        else:
            response = self.info_response
            content = "Login successful. Welcome to the chat."
        return self.encode_response_to_json(self.server_name, response, content)

    def logout_response(self, verified_request):
        valid = verified_request[0]
        error_message = verified_request[1]
        if not valid:
            response = self.error_response
            content = error_message
        else:
            response = self.info_response
            content = "Logout successful. Bye."
        return self.encode_response_to_json(self.server_name, response, content)

    def message_response(self, sender, content, verified_request):
        valid = verified_request[0]
        error_message = verified_request[1]
        if not valid:
            response = self.error_response
            content = error_message
        else:
            response = self.message_response
        return self.encode_response_to_json(sender, response, content)

    def names_response(self, usernames, verified_request):
        valid = verified_request[0]
        error_message = verified_request[1]
        if not valid:
            response = self.error_response
            content = error_message
        else:
            response = self.info_response
            content = usernames
        return self.encode_response_to_json(self.server_name, response, content)

    def help_response(self, verified_request):
        valid = verified_request[0]
        error_message = verified_request[1]
        if not valid:
            response = self.error_response
            content = error_message
        else:
            response = self.info_response
            content = 'Possible requests:\n' \
                '- login <username>\n' \
                '- logout\n' \
                '- msg <content>\n' \
                '- names\n' \
                '- help\n'
        return self.encode_response_to_json(self.server_name, response, content)

    def history_response(self, history_file_path):
        pass  # Read from file and return history as json

    """
        Methods for checking request validity
        Each method should check if the payload is valid for that specific request,
        and create an appropriate error message is not valid.
        E.g. if it is not valid False should be returned with an error message as a tuple
        Respond with tuple (True, "") or (False, "error message")
    """
    #  TODO: implement logic here
    def verify_login_request(self, payload):
        # Check if username contains only allowed characters
        # Check if username is not taken
        # Respond with tuple (True, "") or (False, "error message")
        return True, ""

    def verify_logout_request(self, payload):
        # Should return false if there is actual content attached
        # with the "logout" keyword
        return True, ""

    def verify_msg_request(self, payload):
        # Currently no need to check the message content for validity
        return True, ""

    def verify_names_request(self, payload):
        # Should return false if there is actual content attached
        # with the "names" keyword
        return True, ""

    def verify_help_request(self, payload):
        # Should return false if there is actual content attached
        # with the "help" keyword
        return True, ""

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

    def is_login(self, request):
        return request == self.login_request

    def is_logout(self, request):
        return request == self.logout_request

    def is_message(self, request):
        return request == self.message_request

    def is_help(self, request):
        return request == self.help_request

    def not_logged_in_json(self):
        # Local time in format 'Tue Jan 13 10:17:09 2009'
        localtime = time.asctime(time.localtime(time.time()))
        response_message = \
            {
                'timestamp': localtime,
                'sender': self.server_name,
                'response': self.error_response,
                'content': "You are not logged in. Enter 'login <username>' to log in."
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