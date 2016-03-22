import random

from tyckiting_client.ai import base
from tyckiting_client import actions


class Ai(base.BaseAi):
    """
    Smart bot that kills.
    """
    def move(self, bots, events):
        """
        Defeat the enemy bot

        Args:
            bots: List of bot states for own team
            events: List of events form previous round

        Returns:
            List of actions to perform this round.
        """
        response = []
        for bot in bots:
            if not bot.alive:
                continue

            move_pos = random.choice(list(self.get_valid_moves(bot)))
            response.append(actions.Move(bot_id=bot.bot_id,
                                         x=move_pos.x,
                                         y=move_pos.y))
        return response
