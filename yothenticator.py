#!/usr/bin/env python
'''Server and Handler classes for a Yothenticator server, an HTTP server
accepting GET requests with a username parameter to authenticate against the
servers authorized users.
:Author: Samuel Bostock
'''
import urlparse
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer


def try_to_call(obj):
    '''If obj is callable, call it; otherwise, do nothing.'''
    if hasattr(obj, '__call__'):
        obj()


class YothenticatorServer(HTTPServer):

    '''HTTPServer using YOs from authorized users as a means of triggering some
    action.
    '''

    def __init__(self, server_address, RequestHandlerClass, user_list,
                 **kwargs):
        '''Accept the list of authorized users, and action functions, then
        forward remaining arguments to HTTPServer init.

        Actions functions are provided using the following keyword arguments:
        action_success -- the function to execute on successful authentication
        action_ignore  -- the function to execute on bad authentication format
        action_fail    -- the function to execute on authentication failure
        '''
        self.user_list = [user.strip().upper() for user in user_list]
        self.action_success_function = kwargs.pop('action_success', None)
        self.action_ignore_function = kwargs.pop('action_ignore', None)
        self.action_fail_function = kwargs.pop('action_fail', None)
        HTTPServer.__init__(self, server_address, RequestHandlerClass, **kwargs
                            )

    def action_success(self):
        '''Attempt to call the action on success function.'''
        try_to_call(self.action_success_function)

    def action_ignore(self):
        '''Attempt to call the action on ignore function.'''
        try_to_call(self.action_ignore_function)

    def action_fail(self):
        '''Attempt to call the action on fail function.'''
        try_to_call(self.action_fail_function)


class YothenticatorRequestHandler (BaseHTTPRequestHandler):

    '''GET Request Handler for YothenticatorServer, which verifies username
    query parameter against server's user list.
    '''

    def authenticate(self, user):
        '''Verify the user against the server's user list, and set the status
        code appropriately.

        User in list     -> Authentication Success -> 200 OK
        User == None     -> Authentication Missing -> 400 Bad Request
        User not in list -> Authentication Failure -> 401 Unauthorized
        '''
        if user is None:
            self.status = 400  # bad request, no user provided
        elif user.strip().upper() in self.server.user_list:
            self.status = 200  # OK, authorized
        else:
            self.status = 401  # forbidden, user not authorized

    def extract_user(self):
        '''Extract a single username parameter from the URL query string.
        Returns the username, or None for missing or multiple username
        parameters.
        '''
        user = None
        query_parameters = urlparse.parse_qs(
            urlparse.urlparse(self.path).query)

        if 'username' in query_parameters:
            usernames = query_parameters['username']
            if len(usernames) == 1:
                user = usernames[0]
            # Else leave user as None.
            # Multiple usernames mean badly formated request.

        return user

    def status_message(self):
        '''Build a status message for HTTP codes 200, 400, and 401, depending
        on authentication status.
        '''
        if self.status == 200:
            message = "Access Granted."
        elif self.status == 400:
            message = "Just YO."
        elif self.status == 401:
            message = "Access Denied."
        else:  # This should never happen!
            self.status = 500
            print "500 INTERNAL SERVER ERROR!"
            message = "Something broke..."
        return message

    # TODO Add username as parameter to action.
    # e.g. use case: >>> print 'Access granted to ' + user
    def take_action(self):
        '''Take the action specified in the server, for the current
        authentication status.
        '''
        if self.status == 200:
            self.server.action_success()
        elif self.status == 400:
            self.server.action_ignore()
        elif self.status == 401:
            self.server.action_fail()
        else:  # This should never happen!
            self.status == 500
            print "500 INTERNAL SERVER ERROR!"

    # Handler for the GET requests sent by YO's API
    def do_GET(self):
        '''Handler for GET requests, which attempts to authenticate YO user,
        and tell server to perform appropriate action.
        '''
        # Extract user and authenticate
        self.authenticate(self.extract_user())

        # Build the html message
        message = self.status_message()

        # Build the response
        self.send_response(self.status)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        # Send it
        self.wfile.write(
            "<!DOCTYPE html><html><head><title>YO</title><body><h1>YO</h1><p>"
            + message
            + "</p></body></html>")
        # Take action, depending on status
        self.take_action()

if __name__ == '__main__':
    try:
        def p(arg):
            '''Function to allow printing in lambdas bellow.'''
            print arg

        # Create a dummy web server and define the handler to manage the
        # incoming request. Only username accepted is 'bob'.
        PORT_NUMBER = 8000
        server = YothenticatorServer(('', PORT_NUMBER),
                                     YothenticatorRequestHandler, ['bob'],
                                     action_success=lambda: p('success'),
                                     action_ignore=lambda: p('ignore'),
                                     action_fail=lambda: p('failure')
                                     )
        print 'Started httpserver on port ', PORT_NUMBER

        # Wait forever for incoming http requests
        server.serve_forever()

    except (KeyboardInterrupt, SystemExit):
        print 'Shutting down.'
        server.socket.close()
