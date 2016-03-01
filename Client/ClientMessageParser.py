import json


class ClientMessageParser:

    def __init__(self):

        """
            Possible requests from client to server
        """
        self.possible_requests_without_content = \
            [
                'logout',
                'names',
                'help',
            ]

        """
            Possible responses from server
        """
        self.error_response = 'error'
        self.info_response = 'info'
        self.message_response = 'message'
        self.history_response = 'history'

        self.possible_responses = {
            self.error_response: self.parse_error,
            self.info_response: self.parse_info,
            self.message_response: self.parse_message,
            self.history_response: self.parse_history
        }
        self.possible_requests = {

        }

    def parse(self, payload):
        # Assumes that the payload is in json format
        payload = json.loads(payload)

        if payload['response'] in self.possible_responses:
            return self.possible_responses[payload['response']](payload)
        else:
            return self.response_not_valid()

    """
        Methods for parsing incoming responses from the chat server
    """

    def parse_error(self, payload):
        sender = payload['sender']  # In this case the server
        response = payload['response']
        content = payload['content']
        return content + "\n"

    def parse_info(self, payload):
        sender = payload['sender']  # In this case the server
        response = payload['response']
        content = payload['content']
        return content + "\n"

    def parse_message(self, payload):
        timestamp = payload['timestamp']
        sender = payload['sender']  # In this case the server
        response = payload['response']
        content = payload['content']
        return sender + ": " + timestamp + "\n" + content + "\n"

    def parse_history(self, payload):
        response = payload['response']
        content = payload['content']
        return response + ":\n" + content + "\n"

    def response_not_valid(self):
        return "Client:\n" + "The server attempted to send a response, but the response was invalid."

    def parse_user_input(self, user_input):
        if not len(user_input.strip()) == 0:
            request = user_input.split(' ')[0]
            content = user_input[len(request)+1:]
            if request in self.possible_requests_without_content:
                content = 'None'
            return True, self.encode_request_to_json(request, content)
        return False, ""



    @staticmethod
    def encode_request_to_json(request, content):
        request_payload = \
            {
                'request': request,
                'content': content
            }
        return json.dumps(request_payload)

    def request_is_valid(self, request):
        if len(self.possible_requests) == 0:
            return False
        for valid_request in self.possible_requests:
            if not request == valid_request:
                return False
        return True