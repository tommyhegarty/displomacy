import move_adjudicator
import unittest

class TestMoveAdjudicator(unittest.TestCase):

    def test_adjacent_move(self):
        self.assertEqual(move_adjudicator.valid_move("A","KIE","HOL"),"VALID","Failed to mark move as valid")
    def test_fleet_invalid(self):
        self.assertEqual(move_adjudicator.valid_move("F","BEL","RUH"),"INVALID","Failed to detect fleet move to landlock")
    def test_army_invalid(self):
        self.assertEqual(move_adjudicator.valid_move("A","HOL","NTH"),"INVALID","Failed to detect army move to sea")
    def test_convoy_possible(self):
        self.assertEqual(move_adjudicator.valid_move("A","HOL","LON"),"CONVOY","Failed to detect possibility of convoy")

if __name__ == '__main__':
    unittest.main()