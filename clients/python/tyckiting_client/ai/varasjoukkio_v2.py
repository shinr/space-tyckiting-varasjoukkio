import random

from tyckiting_client.ai import base
from tyckiting_client import actions


class Node(object):
    x = 0
    y = 0
    age = 0
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

class Modes(object):
    ESCAPE = 0
    ROAM = 1
    BATTLE = 2


class Ai(base.BaseAi):
    """
    Bots tracks our bots by id, keeping track of last actions so we know what happens
    """
    bots = {}
    """
    Game Map contains what we know of the world.  It is basically a node tree calculated
    with map size and scan size.
    Node can have a state of uncharted or charted.  Node also knows how many turns 
    ago it was charted.  If the turns ago is greater than a threshold, a node
    is considered ancients and returned into uncharted node set.
    """
    game_map = {}
    current_scanner = -1
    enemy_sighted = False
    enemy_position = None
    volley_fired = False
    reversed_x = False
    firing_offset = 0
    bots_inactive = 0
    bot_modes = []
    modes = Modes()
    def __init__(self, team_id, config=None):
        base.BaseAi.__init__(self, team_id, config=config)
        if config:
            self.generate_map()

    """
    Dummy bot that moves randomly around the board.
    """
    def move(self, bots, events):
        """
        Move the bot to a random legal positon.

        Args:
            bots: List of bot states for own team
            events: List of events form previous round

        Returns:
            List of actions to perform this round.
        """
        for ev in events.events:
            print ev.event
            if ev.event == "see":
                self.enemy_position = Node(ev.pos.x, ev.pos.y)
                self.enemy_sighted = True
            if ev.event == "radarEcho":
                self.enemy_position = Node(ev.pos.x, ev.pos.y)
                self.enemy_sighted = True

        response = []
        for bot in bots:
            if not bot.alive:
                continue

            if "detected" in events.events:
                print "i was detected"

            move_pos = random.choice(list(self.get_valid_moves(bot)))
            action = actions.Move(bot_id=bot.bot_id,
                                         x=move_pos.x,
                                         y=move_pos.y)

            if self.enemy_sighted:
                target_x = self.enemy_position.x + firing_offset
                target_y = self.enemy_position.y + firing_offset
                action = actions.Cannon(bot_id=bot.bot_id, x=target_x, y=target_y)
                self.volley_fired = True
            
            elif self.current_scanner == bot.bot_id or self.current_scanner < 0:
                node = self.game_map["uncharted"].pop()
                self.current_scanner = random.choice([b.bot_id for b in bots if bot.alive])
                action = actions.Radar(bot_id=bot.bot_id, x=node.x, node.y)
                self.game_map["uncharted"].insert(node)

            response.append(action)

        if self.enemy_sighted and self.volley_fired:
            self.enemy_sighted = False
            self.volley_fired = False
            self.enemy_position = None

        return response


    def generate_map(self):
        self.game_map["uncharted"] = list()
        self.game_map["charted"] = list()
        try:
            for x in xrange(-self.config.field_radius + self.config.radar, self.config.field_radius + 1, self.config.radar):
                for y in xrange(max(-self.config.field_radius + self.config.radar, -x-self.config.field_radius + self.config.radar), min(self.config.field_radius - self.config.radar, -x+self.config.field_radius) + 1, self.config.radar):
                    self.game_map["uncharted"].append(Node(x=x, y=y))
            print self.game_map
        except AttributeError:
            raise




        