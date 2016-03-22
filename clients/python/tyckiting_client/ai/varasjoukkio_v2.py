import random, math

from tyckiting_client.ai import base
from tyckiting_client import actions, messages


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

class BotModes(object):
    mode = 0
    mode_timer = 0
    target_position = None

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

    def get_edge_positions_in_range(self, x=0, y=0, radius=1):
        positions = list()
        for dx in xrange(-radius, radius+1):
            for dy in xrange(max(-radius, -dx-radius), min(radius, -dx+radius)+1):
                if dx == -radius or dx == radius or dy == max(-radius, -dx-radius) or dy == min(radius, -dx+radius):
                    if math.sqrt((dx+x)**2 + (dy+y)**2) < self.config.field_radius:
                        positions.append(messages.Pos(dx+x, dy+y))
        print len(positions)
        return positions    
                        #yield messages.Pos(dx+x, dy+y)

    def escape(self, bot):
        zigzag = False
        if self.bots[bot.bot_id].mode_timer % 2 == 0:
            zigzag = True
        positions = self.get_edge_positions_in_range(bot.pos.x, bot.pos.y, self.config.move)
        tentative_position = bot.pos
        for pos in positions:
            if self.bots[bot.bot_id].target_position.x < bot.pos.x:
                if self.bots[bot.bot_id].target_position.y < bot.pos.y:
                    if pos.x < bot.pos.x and pos.y < bot.pos.y:
                        tentative_position = pos
                else:
                    if pos.x < bot.pos.x and pos.y > bot.pos.y:
                        tentative_position = pos
            else:
                if self.bots[bot.bot_id].target_position.y < bot.pos.y:
                    if pos.x > bot.pos.x and pos.y < bot.pos.y:
                        tentative_position = pos
                else:
                    if pos.x > bot.pos.x and pos.y > bot.pos.y:
                        tentative_position = pos
        move_pos = tentative_position
        if zigzag:
            adjust = Node()
            yofs = abs(move_pos.y - bot.pos.y)
            xofs = abs(move_pos.x - bot.pos.x)
            if xofs > yofs:
                if move_pos.y < bot.pos.y:
                    adjust.y += yofs * 2
                else:
                    adjust.y -= yofs * 2
            else:
                if move_pos.x < bot.pos.x:
                    adjust.x += xofs * 2
                else:
                    adjust.x -= xofs * 2
            move_pos = messages.Pos(move_pos.x + adjust.x, move_pos.y + adjust.y)
        #print move_pos, bot.pos, self.bots[bot.bot_id].target_position.x, self.bots[bot.bot_id].target_position.y
        action = actions.Move(bot_id=bot.bot_id,            
                                     x=move_pos.x,
                                     y=move_pos.y)
        self.bots[bot.bot_id].mode_timer -= 1
        if self.bots[bot.bot_id].mode_timer < 0:
            self.bots[bot.bot_id].mode_timer = 0
            self.bots[bot.bot_id].mode = Modes.ROAM
        return action

    def find_legal_escape_node(self, bot):
        target_x = 0
        target_y = 0
        pos =  random.choice(self.get_edge_positions_in_range(bot.pos.x, bot.pos.y, self.config.move * self.bots[bot.bot_id].mode_timer))
        target_x, target_y = pos.x, pos.y
        print "moving to ", target_x, ", " , target_y
        return Node(x=target_x, y=target_y)

    """
    Intelligent bot that destroys all opponents
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
                self.bots[bot.bot_id] = BotModes()

        detection = False
        for ev in events:
            if ev.event == "see":
                if not ev.bot_id in alive_bots: # not ours
                    self.enemy_position = Node(ev.pos.x, ev.pos.y)
                    self.enemy_sighted = True
            if ev.event == "radarEcho":
                self.enemy_position = Node(ev.pos.x, ev.pos.y)
                self.enemy_sighted = True
            if ev.event == "die":
                if self.scan_for_remains:
                    if not ev.bot_id in [bot.bot_id for bot in bots]:
                        self.scan_for_remains = False # guess we killed it
            if ev.event == "detected":
                if ev.bot_id in alive_bots:
                    if not self.enemy_sighted: # if enemy has been sighted, let's just fight.  if not, escape
                        for b in bots:
                            if b.bot_id == ev.bot_id:
                                self.bots[b.bot_id].mode = Modes.ESCAPE
                                self.bots[b.bot_id].mode_timer = 3 # ESCAPE for five turns
                                self.bots[b.bot_id].target_position = self.find_legal_escape_node(b)
            if ev.event == "damaged" and ev.bot_id in alive_bots:
                for b in bots:
                    if b.bot_id == ev.bot_id:
                        self.bots[b.bot_id].mode = Modes.ESCAPE
                        self.bots[b.bot_id].mode_timer = 3 # ESCAPE for five turns
                        self.bots[b.bot_id].target_position = self.find_legal_escape_node(b)


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
            #print self.bots[bot.bot_id].mode
            if self.bots[bot.bot_id].mode == Modes.ESCAPE:
                action = self.escape(bot)
                response.append(action)
                continue
            
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
                shootAgain = False
                for ev in events:
                    if ev.event == "hit" and ev.source == bot.bot_id and ev.bot_id not in alive_bots:
                        shootAgain = True
                        break

                if shootAgain:
                    target_x = self.enemy_position.x + random.choice([self.config.cannon, -self.config.cannon])
                    target_y = self.enemy_position.y + random.choice([self.config.cannon, -self.config.cannon])
                    action = actions.Cannon(bot_id=bot.bot_id, x=target_x, y=target_y)
                else:
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

            random.shuffle(self.game_map["uncharted"])
        except AttributeError:
            raise




        
