# coding=UTF-8

"""
boilerplate for mmo game
Igor Shagadeev
shagastr@gmail.com
"""


# General modules
import os, os.path
import logging
import sys
#from threading import Timer
#import string
#import random

# Tornado modules
import tornado
import tornado.ioloop
import tornado.web
import tornado.websocket
import tornado.auth
import tornado.options
import tornado.escape

from tornado import gen

# Redis modules
import tornadoredis

# Import application modules
from auth_middleware import BaseHandler
from auth import LogoutHandler, RegHandler

from game import Game

import urllib2


# Define port from command line parameter.
tornado.options.define("port", default=8888, help="run on the given port", type=int)






class MainHandler(BaseHandler):
    """
    Main request handler for the root path and for chat rooms.
    """

    def initialize(self):
        """
        overwright initialize
        """
        super(MainHandler, self).initialize()
        self._current_user = None
        self.room_name = None
        self.room = None
        self.room_name = None
        self.room_chat = None
        self.room_users_list = None



    @tornado.web.asynchronous
    def get(self, room=None):
        """
        get method
        """
        self.room = 'room:' + str(room)
        self.room_name = room
        self.room_chat = 'room:'+ str(room) + ':chat'

        self.room_users_list = None

        # Get the current user.
        self._get_current_user(callback=self.on_auth)


    def on_auth(self, user):
        """
        callback
        """
        if not user:
            # Redirect to login if not authenticated.
            print 'redirect to login'
            self.redirect("/login")
            return

        # here we go to room number self.room
        if not self.room:
            self.room = 'room:' + str(user["room"])
            self.room_name = user["room"]
            self.redirect("/room/" + self.room_name)


        # populate game session
        # maybe make it in game.py
        # now get here all stored in Redis data about players in this room
        #
        self.application.client.lrange(self.room, 0, -1, self.add_players)

        print "render room_game, game id", self.application.game.id
        self.render_default("room_game.html", content={}, chat=1)


    def add_players(self, stored_users):
        """
        add_players
        """
        print 'stored_users ', stored_users
        # take all user: keys from room

        def on_get_user(u):
            """
            callback when trying to get user from redis
            """
            try:
                if int(u['health']) <= 0:
                    return
            except KeyError:
                return
            except TypeError:
                return

            print 'redis_user ', u
            # save user in game session
            self.application.game.add_player_fromdict(u)

        # take every user object in Redis by key
        # and save in game session
        if stored_users:
            print 'work on stored_users :'
            for u in stored_users:
                print 'redis_user_key :', u
                self.application.client.hgetall(u, on_get_user)
        else:
            print 'pass it'







class ChatSocketHandler(tornado.websocket.WebSocketHandler):
    """
    Handler for dealing with websockets. It receives, stores
    and distributes new messages.

    Not proper authentication handling!
    """
    def initialize(self):
        """
        overwright initialize
        """
        super(ChatSocketHandler, self).initialize()
        self.client = None
        self.room_name = None
        self.room = None
        self.subscribed = None

    # W:141, 0: Method 'data_received' is abstract
    # in class 'RequestHandler' but is not overridden (abstract-method)

    @gen.engine
    def open(self, room='root'):
        """
        Called when socket is opened. It will subscribe for the
        given chat room based on Redis Pub/Sub.
        """
        # Check if room is set.
        if not room:
            self.write_message({'error': 1, 'textStatus': 'Error: No room specified'})
            self.close()
            return

        # TODO not only messages
        #self.room = 'room:' + str(room)
        #self.room_chat = 'room:'+str(room) + ':chat'
        self.room_name = str(room)
        self.room = 'room:' + str(room) + ':chat'
        print 'room', room

        #self.new_message_send = False

        # Create a Redis connection.
        self.client = redis_connect()

        # simple subscribe
        yield gen.Task(self.client.subscribe, self.room)

        # Subscribe to the given chat room.
        self.subscribed = True

        logging.info('New user connected to chat room ' + room)

        self.client.listen(self.on_messages_published)
        self.on_ws_open()


    def on_ws_open(self):
        """
        #print 'on_ws_open xxx'
        # try to send message to append new user to clients
        """

        print "render room_game, game id", self.application.game.id

        messages = []

        # send array of players
        players = self.application.game.players
        for p in players:
            try:
                message = {
                    'type' :'add_user',
                    'start_position': p.get_position(),
                    'field_size': self.application.game.get_field_size(),
                    'user_name': p.name,
                    'user__hash': p._hash,
                    'health': p.health,
                }

                # Convert to JSON-literal.
                message_encoded = tornado.escape.json_encode(message)
                print 'message_encoded', message_encoded
                messages.append(message_encoded)
            except Exception, err:
                e = str(sys.exc_info()[0])
                print 'message_error', e
        try:
            for m in messages:
                self.write_message(m)
            # self.application.client.publish(self.room, {"messages":messages})
        except Exception, err:
            e = str(sys.exc_info()[0])
            self.write_message({'error': 1, 'textStatus': 'Error writing to db: ' + str(err) + e})


    def on_messages_published(self, message):
        """
        Callback for listening to subscribed chat room based on
        Redis Pub/Sub. When a new message is stored
        in the given Redis chanel this method will be called.
        """
        # print 'recieved from redis channel', message.body
        try:
            # Decode message
            m = tornado.escape.json_decode(message.body)
            # Send messages to other clients
            # self.write_message(dict(messages=[m]))
            self.write_message(m)
        except ValueError:
            try:
                msg_list = message.body['messages']
                for m in msg_list:
                    self.write_message(m)
            except TypeError:
                pass
        except TypeError:
            m = str(message.body)
            print 'error with json_decode', m


    def on_message(self, data):
        """
        Callback when new message received vie the socket.

        /*
        * In js client Function to create a new message
        */
        function postTextMessage(data) {
            var message = {data:data};
            message._xsrf = user._xsrf;
            // Send message using websocket.
            ws.send(JSON.stringify(message));

        }
        """
        logging.info('Received new message %r', data)
        #print 'sended new message', self

        try:
            # Parse input to message dict.
            datadecoded = tornado.escape.json_decode(data)
            #print 'datadecoded message', datadecoded

            user_name = urllib2.unquote(self.get_cookie('user_name'))
            user__hash = urllib2.unquote(self.get_cookie('user__hash'))

            #get player
            #get user from game session ?
            player = self.application.game.get_player(
                name=user_name,
                _hash=user__hash)
            if not player:
                self.close()

            # calculate game round for player
            self.application.game.game_round(player)

            #
            # If health < 0 kill and render popup
            #remove form players in game session
            # remove from redis

            if player.health < 0:
                self.application.game.player_dead(player)

                room_str = 'room:' + self.room_name
                u_str = 'user:' + user_name + ':' + user__hash
                self.application.client.lrem(room_str, u_str)

                message = {
                    'type' :'dead',
                    'user_name': user_name,
                    'user__hash': user__hash,
                    'room': self.room_name,
                }

                # invoke modal on client
                self.write_message(message)

                # Convert to JSON-literal.
                message_encoded = tornado.escape.json_encode(message)
                # tell about excluding dead one to all
                self.application.client.publish(self.room, message_encoded)


            #change velocity and position
            new_pos = player.calc_new_position(datadecoded["data"])


            # write message
            message = {
                'type' :'move',
                'user_name': urllib2.unquote(self.get_cookie('user_name')),
                'user__hash': urllib2.unquote(self.get_cookie('user__hash')),
                'room': urllib2.unquote(self.get_cookie('room')),
                #'data': datadecoded["data"],
                'position' : new_pos,
                'velocity' : player.get_velocity(),
                'health' : player.health,
            }
            if not message['user__hash']:
                logging.warning("Error: Authentication missing Not Posting")
                return

            print 'ws received msg from ', message['user_name']
            #print 'sended new message', message

            #save to redis
            # get current user in redis hget - not need
            # set HMSET new _hash to redis - overwrite all fields if
            # key exists otherwise write new _hash
            self.application.client.hmset(player.get_hash_key(), player.get_hash_dict())

        except Exception, err:
            print str(err)
            #self.write_message({'error': 1, 'textStatus': 'Bad input data ' + str(err) + data})
            #self.write_message(str(err))
            return

        # Save message and publish in Redis.
        try:
            # Convert to JSON-literal.
            message_encoded = tornado.escape.json_encode(message)

            # Persistently store message in Redis.
            #self.application.client.rpush(self.room, message_encoded)
            # Publish message in Redis channel.
            self.application.client.publish(self.room, message_encoded)

        except Exception, err:
            e = str(sys.exc_info()[0])
            # Send an error back to client.
            self.write_message({'error': 1, 'textStatus': 'Error writing to db: ' + str(err) + e})
            return

        ## Send message through the socket to indicate a successful operation.
        # self.write_message(message)
        return


    def on_close(self):
        """
        Callback when the socket is closed. Frees up resource related to this socket.
        """
        logging.info("socket closed, cleaning up resources now")

        print 'closed by web-client'

        if hasattr(self, 'client'):
            # Unsubscribe if not done yet.
            if self.subscribed:
                self.client.unsubscribe(self.room)
                self.subscribed = False
                self.client.disconnect()



class Application(tornado.web.Application):
    """
    Main Class for this application holding everything together.
    """
    def __init__(self):
        # Settings:
        settings = dict(
            cookie_secret="43osdETzKXasd666aYdkL5gEmGeJJFjYh7EQnp2XdTP1o/Vo=",
            login_url="/login",
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            xsrf_cookies=True,
            autoescape="xhtml_escape",

            debug=True,
            auto_reload=True,

            ## Set this to your desired database name.
            #db_name = 'wisps',
        )


        # Handlers defining the url routing.
        handlers = [
            (r"/", MainHandler),
            (r"/room/([a-zA-Z0-9]*)$", MainHandler),

            (r"/login", RegHandler),
            (r"/logout", LogoutHandler),

            (r"/socket", ChatSocketHandler),
            (r"/socket/([a-zA-Z0-9]*)$", ChatSocketHandler),

            #(r'/static/(.*)', StaticFileHandler, {'path': settings['static_path']}),
        ]



        # Call super constructor.
        tornado.web.Application.__init__(self, handlers, **settings)

        # start game object to store current game data
        self.game = Game()

        # Connect to Redis.
        self.client = redis_connect()

        self.client.lpush('rooms', '')


def redis_connect():
    """
    Established an asynchronous resi connection.
    """

    client = tornadoredis.Client(host='127.0.0.1', port=6379)
    client.connect()
    return client


# u can make it faster with per_core loops - look tornado docs
def main():
    """
    Main function to run the chat application.
    """
    app = Application()

    app.listen(tornado.options.options.port)
    tornado.ioloop.IOLoop.instance().start()

main()





















