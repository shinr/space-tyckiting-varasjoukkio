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
    SCAN = 0
    SHOOT = 1
    ESCAPE = 2

class Ai(base.BaseAi):
    """
    Smart bot that kills.
    """
    
    def __init__(self, team_id, config=None):
        base.BaseAi.__init__(self, team_id, config=config)
        self.mode = Modes.SCAN
        if config:
            pass
            #self.generate_map()
    
    def move(self, bots, events):
        """
        Defeat the enemy bot

        Args:
            bots: List of bot states for own team
            events: List of events form previous round

        Returns:
            List of actions to perform this round.
        """

        aliveBots = [bot.bot_id for bot in bots if bot.alive]
        
        response = []
        for bot in bots:
            if not bot.alive:
                continue
            
            for e in events:
                if e.event == "detected" and e.bot_id == bot.bot_id:
                    self.mode = Modes.ESCAPE
                if e.event == "hit" and e.bot_id == bot.bot_id:
                    self.mode = Modes.ESCAPE

            #if self.mode == Modes.SCAN:
                #Randomi paikka 1-max steps?
            move_pos = random.choice(list(self.get_valid_moves(bot)))
            action = actions.Move(bot_id=bot.bot_id,
                                         x=move_pos.x, y=move_pos.y)

            response.append(action)
            
        return response
