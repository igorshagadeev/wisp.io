# coding=UTF-8

"""
### Igor Shagadeev
### shagastr@gmail.com

    Why not make here auto update for game session from Redis or any db
"""

# a game
import random
import numpy as np
import math


from auth import random_code





class Game:
    '''
        Unic game session for connected web-client
    '''
    def __init__(self, field_size=(1000, 1000)):
        self.field_size = field_size
        self.left_corner = (300, 300)
        self.start_position = (0, 0)

        self.room = ''
        self.players = []
        #TODO pass redis connection here
        self.connection = ''
        self.id = random_code()


    def set_room(self, room):
        """
        set_room
        """
        self.room = room

    def get_field_size(self):
        """
        get_field_size
        """
        return str(self.field_size[0]) + ',' + str(self.field_size[1])

    def get_start_position(self):
        """
        get_start_position
        """
        return str(self.start_position[0]) + ',' + str(self.start_position[1])

    def add_player(self, name, _hash, unit_type):
        """
        add_player
        """
        player = Player(name, _hash, unit_type)
        player.set_position(self.field_size)
        self.players.append(player)
        print 'player_added'

    def add_player_fromdict(self, user):
        """
        add_player_fromdict of variables
        """

        #check if player exists
        if user['name'] in map(lambda x: x.name, self.players):
            if user['_hash'] in map(lambda x: x._hash, self.players):
                return
        # TODO construct from dict
        #player = Player(user)

        name = user['name']
        _hash = user['_hash']
        unit_type = user['unit_type']

        player = Player(name, _hash, unit_type)

        try:
            player.health = int(user['health'])
        except KeyError:
            pass
        try:
            pos = user['position'].split(',')
            player.position = np.array([float(pos[0]), float(pos[1])])
        except KeyError:
            pass

        self.players.append(player)
        print 'add_player_fromdict'

    def get_player(self, name, _hash):
        """
        get_player
        """
        for p in self.players:
            if p.name == name and p._hash == _hash:
                return p
        return None

    def update_session(self):
        """
        populate from redis - already done in app.py
        """
        # TODO need connection to access Redis
        pass


    def player_dead(self, player):
        """
        #check if player exists
        """
        self.players.remove(player)

    def game_round(self, player):
        '''
        Calculate all interaction between players
         - every mouse pos get
        '''

        #sudden death mode
        #just to test mmo engine boirelplate

        #player.health = player.health-1

        if player.health <= 0:
            return

        #//calculate interactions
        for unit in self.players:
            if player != unit:

                u_type = unit.unit_type

                #print 'types', player.unit_type, ' ', unit.unit_type

                if dist(player, unit) < (player.get_size()*4 + unit.get_size()*4) and unit.health > 1:
                    #//speed
                    if player.unit_type == 1:
                        #// speed with speed
                        if u_type == 1:
                            pass
                        #// speed vs dmg
                        elif u_type == 2:
                            player.health = player.health - 1
                        #// speed vs heal
                        elif u_type == 3:
                            player.health = player.health + 1

                    #//damage
                    elif player.unit_type == 2:
                        #// speed with speed
                        if u_type == 1:
                            player.health = player.health - 1
                        #// speed vs dmg
                        elif u_type == 2:
                            pass
                        #// speed vs heal
                        elif u_type == 3:
                            pass
                    #//heal
                    elif player.unit_type == 3:
                        #// speed with speed
                        if u_type == 1:
                            pass
                        #// speed vs dmg
                        elif u_type == 2:
                            player.health = player.health - 1
                        #// speed vs heal
                        elif u_type == 3:
                            player.health = player.health + 1
                            continue
        return






def dist(p1, p2):
    """
    calculate distance between 2 vectors
    """
    new_v = p1.position - p2.position
    return int(math.sqrt(sum(new_v*new_v)))















#
# Constants
#

MAX_SPEED = 10


class Player:
    """
    Player class
    """
    def __init__(self, name, _hash, unit_type=3):
        """ Create a new player instance"""
        self.name = name
        self._hash = _hash
        self.unit_type = unit_type
        self.position = np.array([0, 0])
        self.health = 200
        self.size = int(math.sqrt(self.health))
        self.velocity = np.array([0, 0])
        #print 'player_created'

    def set_position(self, field_size):
        """
        set_position
        """
        self.position = np.array([random.randint(1, field_size[0]),
                                  random.randint(1, field_size[1])])

    def get_position(self):
        """
        get_position
        """
        return str(self.position[0]) + ',' + str(self.position[1])

    def get_velocity(self):
        """
        get_velocity
        """
        return str(self.velocity[0]) + ',' + str(self.velocity[1])

    def get_size(self):
        """
        get_size
        """
        self.size = int(math.sqrt(self.health))
        return self.size

    def calc_new_position(self, mouse_pos):
        """
        calc_new_position
        # on js client srnding function
        #// Use pos.x and pos.y
            #var xy_data = {
                #x : pos.x,
                #y : pos.y
            #}
        """
        #make vector
        mouse_pos = np.array([mouse_pos['x'], mouse_pos['y']])

        #print mouse_pos, ' - ', self.position
        # mouse_pos v - unit_pos v
        new_vel = mouse_pos - self.position
        #print 'new velocity', new_vel

        new_vel_magnitude = math.sqrt(sum(new_vel*new_vel))
        #print new_vel_magnitude

        if new_vel_magnitude > MAX_SPEED:
            k = MAX_SPEED / new_vel_magnitude
            new_vel = new_vel * k
            #print k, new_vel
        else:
            k = new_vel_magnitude / MAX_SPEED
            new_vel = new_vel * k
            #print k, new_vel

        #normalize
        #new_vel_norm =
        #velocity  = new_velocity

        self.velocity = new_vel
        self.position = self.position + new_vel

        return str(self.position[0]) + ',' + str(self.position[1])

    def get_hash_dict(self):
        """
        return _hash_dict
        """
        d = {
            'name':self.name,
            '_hash':self._hash,
            'health':self.health,
            'unit_type':self.unit_type,
            'position':self.get_position(),
        }
        return d

    def get_hash_key(self):
        """
            return _hash key
        """
        return 'user:' + self.name + ':' + self._hash

    def __unicode__(self):
        return self.name


















































    