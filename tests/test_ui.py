import unittest
import os
import pygame
from ui.controller import GameController
from ui.renderer import MazeRenderer
from ui.theme import init_fonts, GHOST_COLORS, COLOR_PACMAN


class TestUIController(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        init_fonts()

    def setUp(self):
        self.logs = []
        self.controller = GameController(log_callback=lambda txt, col: self.logs.append(txt))

    def test_map_scanning(self):
        self.assertTrue(len(self.controller.map_files) >= 3)
        self.assertIn("maps/adversarial_small.txt", self.controller.map_files)

    def test_load_valid_map(self):
        self.controller.set_map_file("maps/adversarial_small.txt")
        self.assertEqual(self.controller.status, "READY")
        self.assertIsNotNone(self.controller.spawn)
        self.assertTrue(len(self.controller.ghosts) >= 1)
        self.assertTrue(len(self.controller.goals) >= 1)

    def test_load_bad_map_graceful_handling(self):
        self.controller.set_map_file("maps/bad_map.txt")
        self.assertEqual(self.controller.status, "ERROR")

    def test_classic_search_astar(self):
        self.controller.set_map_file("maps/single_small_few_solvable.txt")
        self.controller.set_algorithm("A*")
        # Chạy trực tiếp hàm search
        self.controller._run_classic_search()
        self.assertEqual(self.controller.status, "WIN")
        self.assertIsNotNone(self.controller.expanded_count)
        self.assertTrue(self.controller.expanded_count > 0)
        self.assertIsNotNone(self.controller.time_used)
        self.assertTrue(self.controller.steps_taken > 0)

    def test_adversarial_step_decision(self):
        self.controller.set_map_file("maps/adversarial_small.txt")
        self.controller.set_algorithm("ALPHA-BETA")
        self.controller.set_depth(2)
        self.controller.set_adv_mode("STEP")
        self.controller._run_adversarial_search()
        self.assertIsNotNone(self.controller.last_value)
        self.assertIsNotNone(self.controller.expanded_count)

    def test_color_rules(self):
        # Kiểm tra quy tắc bắt buộc: Pacman vàng, không có ghost nào màu vàng
        self.assertEqual(COLOR_PACMAN, (255, 214, 10))
        for g_color in GHOST_COLORS:
            self.assertNotEqual(g_color, COLOR_PACMAN)
            # Kiểm tra không ghost nào thuộc họ vàng thuần
            self.assertFalse(g_color[0] > 200 and g_color[1] > 200 and g_color[2] < 50)


    def test_path_trail_recording(self):
        self.controller.set_map_file("maps/single_small_few_solvable.txt")
        self.controller.set_algorithm("A*")
        self.controller._run_classic_search()
        self.assertTrue(len(self.controller.path_trail) > 1)
        self.assertEqual(self.controller.path_trail[0], self.controller.spawn)
        self.assertEqual(self.controller.path_trail[-1], self.controller.goals[0])

    def test_render_path_trail(self):
        viewport = pygame.Rect(0, 0, 400, 400)
        renderer = MazeRenderer(viewport)
        renderer.compute_layout(self.controller.game_map)
        surf = pygame.Surface((400, 400))
        # Test vẽ trail khi đang chạy và khi win
        sample_trail = [(1, 1), (1, 2), (2, 2), (3, 2)]
        renderer.draw_path_trail(surf, sample_trail, is_win=False)
        renderer.draw_path_trail(surf, sample_trail, is_win=True)
        # Không có ngoại lệ nào xảy ra


if __name__ == "__main__":
    unittest.main()
