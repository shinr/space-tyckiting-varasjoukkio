import random

from tyckiting_client.ai import base
from tyckiting_client import actions


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



    def __init__(self, team_id, config=None):
        base.BaseAi.__init__(self, team_id, config=config)

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
        response = []
        for bot in bots:
            print bot.bot_id
            if not bot.alive:
                continue

            move_pos = random.choice(list(self.get_valid_moves(bot)))
            response.append(actions.Move(bot_id=bot.bot_id,
                                         x=move_pos.x,
                                         y=move_pos.y))
        return response


    def generate_map(self):
        try:
            for i in xrange(self.config.field_radius):
                pass
        except:
            raise


        