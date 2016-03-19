import unittest

from tyckiting_client.ai import varasjoukkio_v2
from tyckiting_client import messages


class VarasAiTest(unittest.TestCase):

    def setUp(self):
        self.ai = varasjoukkio_v2.Ai(1)

    def test_calculate_map_without_config(self):
        self.ai = varasjoukkio_v2.Ai(1)
        self.assertRaises(AttributeError, self.ai.generate_map)

    def test_generate_map(self):
        self.ai = varasjoukkio_v2.Ai(1, messages.Config())
        self.ai.generate_map()
        space_map = self.ai.game_map
        expected_map = set((
            
            ))
        self.assertEqual(space_map)

    def test_get_positions_in_origo_range(self):
        positions = set(self.ai.get_positions_in_range(x=0, y=0, radius=1))
        expected_positions = set((
            messages.Pos(x=0, y=0),
            messages.Pos(x=0, y=-1),
            messages.Pos(x=1, y=-1),
            messages.Pos(x=1, y=0),
            messages.Pos(x=0, y=1),
            messages.Pos(x=-1, y=1),
            messages.Pos(x=-1, y=0),
        ))
        self.assertEqual(positions, expected_positions)

    def test_get_positions_in_zero_origo_range(self):
        positions = set(self.ai.get_positions_in_range(x=0, y=0, radius=0))
        expected_positions = set((
            messages.Pos(x=0, y=0),
        ))
        self.assertEqual(positions, expected_positions)

    def test_get_positions_in_non_origo_range(self):
        positions = set(self.ai.get_positions_in_range(x=2, y=-3, radius=1))
        expected_positions = set((
            messages.Pos(x=2, y=-3),
            messages.Pos(x=2, y=-4),
            messages.Pos(x=3, y=-4),
            messages.Pos(x=3, y=-3),
            messages.Pos(x=2, y=-2),
            messages.Pos(x=1, y=-2),
            messages.Pos(x=1, y=-3),
        ))
        self.assertEqual(positions, expected_positions)
