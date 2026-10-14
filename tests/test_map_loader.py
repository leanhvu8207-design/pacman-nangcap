import unittest
from src.utils.map_loader import load_map
from src.utils.map_info import get_map_info
from src.utils.map_check_valid import check_map


class TestMapLoader(unittest.TestCase):
    def test_load_valid_map(self):
        game_map = load_map("maps/adversarial_small.txt")
        self.assertIsNotNone(game_map)
        self.assertEqual(len(game_map), 11)
        self.assertEqual(len(game_map[0]), 21)

        test_map = load_map("maps/multi_goal_test.txt")
        self.assertIsNotNone(test_map)
        self.assertEqual(len(test_map), 9)
        self.assertEqual(len(test_map[0]), 15)

    def test_load_invalid_map(self):
        game_map = load_map("maps/bad_map.txt")
        self.assertIsNone(game_map)

    def test_load_nonexistent_file(self):
        game_map = load_map("maps/khong_ton_tai.txt")
        self.assertIsNone(game_map)

    def test_get_map_info(self):
        game_map = load_map("maps/adversarial_small.txt")
        spawn, goals, ghosts = get_map_info(game_map)

        self.assertEqual(spawn, (9, 17))
        self.assertEqual(goals, [(9, 1)])
        self.assertEqual(ghosts, [(9, 15)])

        # Kiểm tra trích xuất foods (.)
        s, g, gh, foods = get_map_info(game_map, return_foods=True)
        self.assertEqual(foods, [(5, 19), (9, 2)])

    def test_load_large_map(self):
        lg_map = load_map("maps/large_map.txt")
        self.assertIsNotNone(lg_map)
        self.assertEqual(len(lg_map), 22)
        self.assertEqual(len(lg_map[0]), 19)

    def test_load_no_solution_map(self):
        ns_map = load_map("maps/no_solution_map.txt")
        self.assertIsNotNone(ns_map)
        self.assertEqual(len(ns_map), 9)
        self.assertEqual(len(ns_map[0]), 9)


if __name__ == "__main__":
    unittest.main()
