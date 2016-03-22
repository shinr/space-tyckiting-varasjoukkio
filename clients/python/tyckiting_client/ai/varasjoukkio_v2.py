import random, math

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
    ROAM = 0
    BATTLE = 1
    SEARCH = 2
    ESCAPE = 3

class Ai(base.BaseAi):
    """
    Bots tracks our bots by id, keeping track of last actions so we know what happens
    """
    bots = {}
    """
    Game Map contains what we know of the world.
    """
    game_map = {}
    current_scanners = []
    scanners = 2
    enemy_sighted = False
    enemy_position = None
    volley_fired = False
    reversed_x = False
    firing_offset = 0
    bots_inactive = 0
    bot_modes = []
    modes = Modes()
    scan_for_remains = False
    set_scanners = False
    detection = False
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
        alive_bots = [bot.bot_id for bot in bots if bot.alive]
        if not self.bots:
            for bot in bots:
                self.bots["mode"] = Modes.ROAM

        detection = False
        for ev in events:
            if ev.event == "see":
                if not ev.bot_id in alive_bots: # not ours
                    self.enemy_position = Node(ev.pos.x, ev.pos.y)
                    self.enemy_sighted = True
            if ev.event == "radarEcho":
                if not ev.bot_id in alive_bots: # not ours
                    self.enemy_position = Node(ev.pos.x, ev.pos.y)
                    self.enemy_sighted = True
            if ev.event == "die":
                if self.scan_for_remains:
                    if not ev.bot_id in [bot.bot_id for bot in bots]:
                        self.scan_for_remains = False # guess we killed it
            if ev.event == "detected":
                if ev.bot_id in alive_bots:
                    self.bots["mode"] = Modes.ESCAPE
                self.detection = True

        if len(alive_bots) > 1:
            self.scanners = len(alive_bots)

        if self.scanners < 1:
            self.scanners = 1

        potential_scanners = alive_bots
        self.current_scanners = []
        for i in range(self.scanners):
            new_scanner = random.choice(potential_scanners)
            self.current_scanners.append(new_scanner)
            potential_scanners.remove(new_scanner)


        response = []
        for bot in bots:
            if not bot.alive:
                if bot.bot_id in self.current_scanners:
                    pass
                continue
            """
            if "detected" in events:
                print "i was detected"
            """
            move_pos = random.choice(list(self.get_valid_moves(bot)))
            action = actions.Move(bot_id=bot.bot_id,
                                         x=move_pos.x,
                                         y=move_pos.y)
            """
                scan if we fired
                if not, shoot if enemy has been enemy_sighted
                if not, scan if we're the scanner
                otherwise, move
            """
            if self.scan_for_remains:
                distance = math.floor(self.config.move)
                target_x = self.enemy_position.x + random.choice([distance, -distance])
                target_y = self.enemy_position.y + random.choice([distance, -distance])
                action = actions.Radar(bot_id=bot.bot_id, x=target_x, y=target_y)
                self.scan_for_remains = False

            elif self.enemy_sighted:  
                target_x = self.enemy_position.x + random.choice([self.config.cannon, -self.config.cannon])
                target_y = self.enemy_position.y + random.choice([self.config.cannon, -self.config.cannon])
                action = actions.Cannon(bot_id=bot.bot_id, x=target_x, y=target_y)
                self.volley_fired = True
            
            elif bot.bot_id in self.current_scanners or not self.current_scanners:
                node = self.game_map["uncharted"].pop()
                action = actions.Radar(bot_id=bot.bot_id, x=node.x, y=node.y)
                self.game_map["uncharted"].insert(0, node)

            response.append(action)

        if self.enemy_sighted and self.volley_fired:
            self.scan_for_remains = True
            self.enemy_sighted = False
            self.volley_fired = False

        return response


    def generate_map(self):
        self.game_map["uncharted"] = list()
        self.game_map["charted"] = list()
        reverse = True
        try:
            for x in xrange(-self.config.field_radius, self.config.field_radius + 1, self.config.radar):
                for y in xrange(max(-self.config.field_radius, -x-self.config.field_radius + self.config.radar), min(self.config.field_radius - self.config.radar, -x+self.config.field_radius) + 1, self.config.radar):
                    if reverse:
                        self.game_map["uncharted"].append(Node(x=x, y=y))
                    else:
                        self.game_map["uncharted"].insert(0, Node(x=x, y=y))
                    reverse = not reverse
                    print reverse,
        except AttributeError:
            raise




        
