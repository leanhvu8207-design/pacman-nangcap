import unittest
import os
import pygame
from ui.controller import GameController
from ui.renderer import MazeRenderer
from ui.components import DirectionalPad
from ui.theme import init_fonts, GHOST_COLORS, COLOR_PACMAN
from src.pacman.player_controller import DirectionInputBuffer, PlayerSession


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

    def test_play_mode_switch_and_wasd_controls(self):
        """Kiểm tra chuyển đổi chế độ AI <-> PLAYER và điều khiển Pacman bằng WASD / Phím mũi tên"""
        self.controller.set_map_file("maps/single_small_few_solvable.txt")
        self.assertEqual(self.controller.play_mode, "AI")

        # Chuyển sang chế độ Người chơi
        self.controller.set_play_mode("PLAYER")
        self.assertEqual(self.controller.play_mode, "PLAYER")
        self.assertEqual(self.controller.status, "READY")
        self.assertEqual(self.controller.pacman_pos, (1, 1))

        # Điều khiển sang phải bằng phím D và xuống dưới bằng phím S
        self.controller.handle_player_key_down(pygame.K_d)
        self.assertEqual(self.controller.pacman_pos, (1, 2))
        self.assertEqual(self.controller.facing_dir, "RIGHT")
        self.assertEqual(self.controller.steps_taken, 1)
        self.assertEqual(self.controller.status, "RUNNING")

        # Reset cooldown để bước tiếp trong unit test
        self.controller._last_player_step_time = 0.0
        self.controller.handle_player_key_down(pygame.K_DOWN)
        self.assertEqual(self.controller.pacman_pos, (2, 2))
        self.assertEqual(self.controller.facing_dir, "DOWN")
        self.assertEqual(self.controller.steps_taken, 2)

        # Thử đi lên tường tại (1, 2) -> (0, 2) là '#' không được đi xuyên tường
        self.controller._last_player_step_time = 0.0
        self.controller.trigger_player_direction("UP")
        self.assertEqual(self.controller.pacman_pos, (1, 2))
        self.controller._last_player_step_time = 0.0
        self.controller.trigger_player_direction("UP")
        self.assertEqual(self.controller.pacman_pos, (1, 2))  # Chặn bởi tường hàng 0

    def test_dpad_component_rendering(self):
        """Kiểm tra component DirectionalPad hoạt động và render không lỗi"""
        triggered = []
        dpad = DirectionalPad(pygame.Rect(0, 0, 420, 80), on_direction=lambda act: triggered.append(act))
        dpad.sync_active_directions({"UP", "RIGHT"})
        self.assertTrue(dpad.btn_up.is_active)
        self.assertTrue(dpad.btn_right.is_active)
        self.assertFalse(dpad.btn_left.is_active)

        surf = pygame.Surface((420, 80))
        dpad.draw(surf, current_dir="UP")


if __name__ == "__main__":
    unittest.main()
