# coding=UTF-8

"""
### Igor Shagadeev
### shagastr@gmail.com

"""

# Tornado modules.
import tornado.web
import tornado.escape

# Import application modules.
from auth_middleware import BaseHandler

# General modules.
import logging


import urllib
import urllib2







class RegHandler(BaseHandler):
    """
    Save new user( registered) - to redis
    """
    @tornado.web.asynchronous
    def get(self):
        """
        get method
        """

        if self.get_argument("start_direct_auth", None):
            # Get form inputs.
            try:
                user = dict()
                user["name"] = self.get_argument("name", default="")
                user["room"] = self.get_argument("room", default="")
                user["unit_type"] = self.get_argument("unit_type", default="3")
            except Exception:
                # Send an error back to client.
                content = "<p>There was an input error. Fill in all fields!</p>"
                self.render_default("index.html", content=content)

            # If user has not filled in all fields.
            # TODO send just message
            if not user["name"] or not user["room"]:
                content = ('<h2>2. Direct Login</h2>'\
                '<p>Fill in both fields!</p>'\
                '<form class="form-inline" action="/login" method="get"> '\
                '<input type="hidden" name="start_direct_auth" value="1">'\
                '<input class="form-control" type="text" name="name"'\
                'placeholder="Your Name" value="' + str(user["name"]) + '"> '\
                '<input class="form-control" type="text" name="room"'\
                'placeholder="room" value="' + str(user["room"]) + '"> '\
                '<input type="submit" class="btn btn-default" value="Sign in">'\
                '</form>')
                self.render_default("index.html", content=content)
            # All data given. Log user in!
            else:
                #print user["name"], user["room"]
                self._reg(user)

        else:

            ##self.render_default("index.html", content=content, user = {})
            self.render_default("room_game.html", content='', user={})

    def _reg(self, user):
        """
        Callback for third party authentication (last step).
        """

        # Save user id in cookie.
        # if ecrypted cookie need - use set_secure_cookie instead of get_cookie
        code = random_code()
        user["_hash"] = code
        self.set_cookie("user_name", urllib.quote(user["name"]))
        self.set_cookie("user__hash", urllib.quote(user["_hash"]))
        self.set_cookie("room", urllib.quote(user["room"]))


        u_str = 'user:' + user["name"] + ':' + user["_hash"]
        room_str = 'room:' + str(user["room"])

        #get 'rooms' list
        rooms = self.application.client.lrange('rooms', 0, -1)
        print 'rooms', rooms

        # check if string (key) 'room:user["room"]' exists or
        #create new in list 'rooms'

        try:
            if room_str in rooms:
                print 'exists'
            else:
                self.application.client.lpush('rooms', room_str)
        except TypeError:
            self.application.client.lpush('rooms', room_str)

        #create and push to list 'room:user["room"]'
        #user name string 'user:user_name:user__hash'
        #create and push to object user as _hash named 'user:user_name:user__hash'
        #try:
        self.application.client.lpush(room_str, u_str)
        self.application.client.hmset(u_str, user)


        # and  - put all in game class
        self.application.game.add_player(user["name"], user["_hash"], 3)


        #TODO here we should write to db

        # Closed client connection
        if self.request.connection.stream.closed():
            logging.warning("Waiter disappeared")
            return

        #self.redirect("/")
        self.redirect("/room/" + str(user["room"]))










class LogoutHandler(BaseHandler):
    """
    LogoutHandler
    """

    def get(self):
        """
        get method
        """
        print 'logout'

        try:
            room = urllib2.unquote(self.get_cookie("room"))
            user_name = urllib2.unquote(self.get_cookie("user_name"))
            user__hash = urllib2.unquote(self.get_cookie("user__hash"))

        except AttributeError:
            logging.warning("no cookie on logout")
            room = None

        if room:
            room_str = 'room:' + room
            u_str = 'user:' + user_name + ':' + user__hash
            self.application.client.lrem(room_str, u_str)



        self.clear_cookie('user_name')
        self.clear_cookie('user__hash')
        self.clear_cookie('room')
        self.redirect("/")



import random
CODE_SYMBOLS_EN_SMALL = '0123456789qwertyuiopasdfghjklzxcvbnm'
def random_code(i=8):
    """ create random code """
    code = ''
    while i >= 0:
        i -= 1
        code += random.choice(CODE_SYMBOLS_EN_SMALL)
    return code







