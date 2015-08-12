# coding=UTF-8

"""
### Igor Shagadeev
### shagastr@gmail.com
"""

# Tornado modules.
import tornado.web

# General modules.
import logging

import urllib2


#TODO list


#1. add user and generate random _hash to identify him - save _hash to cookie - not id?
 #maybe save user to database&


#2. save room name to database
#save it and its id to redis

#3. append user to room

#user_name
#user__hash





class BaseHandler(tornado.web.RequestHandler):
    """
    A base request Handler providing user authentication.
    It also provides a render_default() method
    which passes arguments to render()
    with additional default arguments for the menu, user...
    """


    def initialize(self):
        self._current_user = None
        self.room_name = None

    def _get_current_user(self, callback):
        """
        An async method to load the current user object.
        The callback function will receive the current user object or None
        as the parameter 'user'.
        """
        # Get the user_id by cookie.
        # if ecrypted cookie need - use get_secure_cookie instead of get_cookie
        user = dict()
        try:
            user["name"] = urllib2.unquote(self.get_cookie("user_name"))
            user["_hash"] = urllib2.unquote(self.get_cookie("user__hash"))
            user["room"] = urllib2.unquote(self.get_cookie("room"))
        except AttributeError:
            logging.warning("Cookie not found")
            callback(user=None)
            return


        u_str = 'user:' + user["name"] + ':' + user["_hash"]
        room_str = 'room:' + str(user["room"])
        user["u_str"] = u_str
        user["room_str"] = room_str


        def query_callback(result):
            """
            # Define a callback for the db query.
            """
            if result == "null" or not result:
                logging.warning("User not found")
                user = {}
            else:
                #user = tornado.escape.json_decode(result)
                user = result

            self._current_user = user
            callback(user=user)

        # Load user object from redis and pass query_callback as callback.
        u_str = 'user:' + user["name"] + ':' + user["_hash"]
        self.application.client.hgetall(u_str, query_callback)

        return


    def render_default(self, template_name, **kwargs):
        """
        # Set default variables and render template.
        """
        #if not hasattr(self, '_current_user'):
            #self._current_user = None
        kwargs['user'] = self._current_user
        kwargs['path'] = self.request.path
        kwargs['room'] = self.room_name

        #if hasattr(self, 'room_name'):
            ##@ wtf - why int? Oo
            ##kwargs['room'] = int(self.room)
            #kwargs['room'] = self.room_name
        #else:
            #kwargs['room'] = None


        #if hasattr(self, 'room_users_list'):
            ##kwargs['room_users_list'] = self.room_users_list
            #kwargs['room_users_list'] = map(lambda x: x.split(':')[1], self.room_users_list)
        #else:
            #kwargs['room_users_list'] = None


        kwargs['room_users_list'] = self.application.game.players



        if not self.request.connection.stream.closed():
            self.render(template_name, **kwargs)



    #W: 36, 0: Method 'data_received' is abstract in class 'RequestHandler'
    #but is not overridden (abstract-method)
    #def data_received():
        #pass











