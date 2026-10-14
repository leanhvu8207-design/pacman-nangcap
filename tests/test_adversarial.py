import unittest
from src.utils.map_loader import load_map
from src.utils.map_info import get_map_info
from src.logic_ghost.adv_problem import AdvProblem
from src.logic_ghost.minimax import Minimax
from src.logic_ghost.alpha_beta import AlphaBeta
from src.pacman.game_state import GameState


class TestAdversarialSearch(unittest.TestCase):
    def setUp(self):
        self.small_map = load_map("maps/adversarial_small.txt")
        self.s_spawn, self.s_goals, self.s_ghosts = get_map_info(self.small_map)

        self.test_map = load_map("maps/test_map.txt")
        self.t_spawn, self.t_goals, self.t_ghosts = get_map_info(self.test_map)

    def test_minimax_and_alpha_beta_equivalence(self):
        for depth in [1, 2, 3]:
            problem = AdvProblem(self.s_spawn, self.s_ghosts, self.s_goals[0], self.small_map)
            mm = Minimax(problem, depth)
            act_mm = mm.search()
            ab = AlphaBeta(problem, depth)
            act_ab = ab.search()

            # Xác minh cùng hành động
            self.assertEqual(act_mm, act_ab, f"Hành động không khớp tại depth={depth}")
            # Xác minh cùng giá trị tối ưu
            self.assertEqual(mm.last_value, ab.last_value, f"Giá trị tối ưu không khớp tại depth={depth}")
            # Xác minh Alpha-Beta duyệt số node nhỏ hơn hoặc bằng Minimax
            self.assertLessEqual(ab.expanded_count, mm.expanded_count)

    def test_alpha_beta_pruning_efficiency_on_larger_map(self):
        problem = AdvProblem(self.t_spawn, self.t_ghosts, self.t_goals[0], self.test_map)
        mm = Minimax(problem, depth_limit=3)
        act_mm = mm.search()

        ab = AlphaBeta(problem, depth_limit=3)
        act_ab = ab.search()

        self.assertEqual(act_mm, act_ab)
        self.assertEqual(mm.last_value, ab.last_value)
        # Số node của Alpha-Beta phải giảm đáng kể so với Minimax
        self.assertLess(ab.expanded_count, mm.expanded_count)

    def test_pacman_wins_on_small_map_simulation(self):
        """
        Kiểm tra trong vòng lặp game thực tế (game loop), Pacman sử dụng Alpha-Beta thắng được game.
        """
        state = GameState(self.s_spawn, self.s_ghosts.copy(), set(), 0, self.small_map)
        target = self.s_goals[0]
        step_count = 0
        max_steps = 45

        while step_count < max_steps:
            step_count += 1
            problem = AdvProblem(state.pacman_position, state.ghost_positions, target, self.small_map)
            ab = AlphaBeta(problem, depth_limit=2)
            action = ab.search()
            self.assertIsNotNone(action)

            state = state.step(action, target)
            self.assertIsNotNone(state)

            if state.status in ["WIN", "LOSE"]:
                break

        self.assertEqual(state.status, "WIN", "Pacman phải chiến thắng trên bản đồ nhỏ!")

    def test_pacman_avoids_immediate_ghost_collision(self):
        """
        Kiểm tra Pacman tuyệt đối không đi vào ô có Ghost ngay bước đầu tiên nếu có lựa chọn khác.
        """
        # Giả lập tình huống Pacman ở kề Ghost
        problem = AdvProblem((1, 2), [(1, 3)], (1, 4), self.small_map)
        ab = AlphaBeta(problem, depth_limit=2)
        action = ab.search()

        # Pacman không được đi RIGHT (đâm vào Ghost tại (1, 3))
        self.assertNotEqual(action, "RIGHT", "Pacman không được đâm thẳng vào Ghost khi có lối khác!")

    def test_minimax_and_alpha_beta_equivalence_with_recent_positions(self):
        """
        Kiểm tra tính tương đương 100% giữa Minimax và Alpha-Beta ngay cả khi có phạt recent_positions.
        """
        problem = AdvProblem(self.t_spawn, self.t_ghosts, self.t_goals[0], self.test_map)
        rec = [self.t_spawn, (self.t_spawn[0], self.t_spawn[1] + 1)]
        for depth in [1, 2, 3]:
            mm = Minimax(problem, depth, recent_positions=rec)
            ab = AlphaBeta(problem, depth, recent_positions=rec)
            act_mm = mm.search()
            act_ab = ab.search()
            self.assertEqual(act_mm, act_ab, f"Hành động không khớp tại depth={depth} với recent_positions")
            self.assertEqual(mm.last_value, ab.last_value, f"Giá trị tối ưu không khớp tại depth={depth} với recent_positions")
            self.assertLessEqual(ab.expanded_count, mm.expanded_count)


if __name__ == "__main__":
    unittest.main()
