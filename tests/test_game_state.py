import unittest

try:
    from src.difference import BrightnessDifference
    from src.game_state import GameState
except ModuleNotFoundError as exc:
    if exc.name == "cv2":
        raise unittest.SkipTest("OpenCV is not installed") from exc
    raise


class GameStateTests(unittest.TestCase):
    def make_differences(self):
        return [
            BrightnessDifference(10, 10, width=20, height=20),
            BrightnessDifference(80, 10, width=20, height=20),
        ]

    def test_new_round_resets_round_values_but_keeps_total_found(self):
        state = GameState()
        first_round = self.make_differences()
        state.new_round(first_round)
        state.register_find(first_round[0])
        state.register_mistake()

        state.new_round(self.make_differences())

        self.assertEqual(state.total_found, 1)
        self.assertEqual(state.mistakes, 0)
        self.assertFalse(state.locked)
        self.assertEqual(state.remaining(), 2)

    def test_register_find_marks_difference_and_updates_score(self):
        state = GameState()
        differences = self.make_differences()
        state.new_round(differences)

        state.register_find(differences[0])

        self.assertTrue(differences[0].found)
        self.assertEqual(state.total_found, 1)
        self.assertEqual(state.remaining(), 1)

    def test_find_hit_returns_unfound_matching_difference(self):
        state = GameState()
        differences = self.make_differences()
        state.new_round(differences)

        hit = state.find_hit(20, 20)

        self.assertIs(hit, differences[0])

    def test_find_hit_ignores_already_found_difference(self):
        state = GameState()
        differences = self.make_differences()
        state.new_round(differences)
        state.register_find(differences[0])

        hit = state.find_hit(20, 20)

        self.assertIsNone(hit)

    def test_register_mistake_locks_after_maximum_mistakes(self):
        state = GameState()
        state.new_round(self.make_differences())

        self.assertFalse(state.register_mistake())
        self.assertFalse(state.register_mistake())
        self.assertTrue(state.register_mistake())
        self.assertTrue(state.locked)
        self.assertEqual(state.mistakes_remaining(), 0)

    def test_all_found_is_true_only_after_every_difference_is_found(self):
        state = GameState()
        differences = self.make_differences()
        state.new_round(differences)

        self.assertFalse(state.all_found())
        state.register_find(differences[0])
        state.register_find(differences[1])

        self.assertTrue(state.all_found())


if __name__ == "__main__":
    unittest.main()
