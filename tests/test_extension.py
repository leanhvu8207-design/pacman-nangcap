"""
Kiểm thử chuyên biệt cho Phần mở rộng thuật toán (Mục 3.7 Đề bài)
Học phần: Biểu diễn tri thức và tìm kiếm nâng cao (UET.AI2014) - Nhóm 07

Bao gồm:
1. Mở rộng 1: Heuristic Cây khung nhỏ nhất (Prim MST) cho bài toán Multi-Goal Search.
   - Kiểm tra tính Admissible: chi phí heuristic không bao giờ vượt quá chi phí thực tế.
   - Kiểm tra tính tối ưu: số bước di chuyển bằng với BFS / UCS.
   - Kiểm tra hiệu quả cắt giảm node mở rộng vượt trội so với Heuristic h=0.
2. Mở rộng 2: Evaluation Function cải tiến trong Adversarial Search.
   - Kiểm tra bộ nhớ đệm khoảng cách BFS O(1) (_MAZE_DIST_CACHE).
   - Kiểm tra cơ chế né ngõ cụt và phạt nguy cơ va chạm ma kề sát.
   - Kiểm tra phân loại ma chặn đầu Goal vs ma bám đuổi.
"""

import unittest
from src.utils.map_loader import load_map
from src.utils.map_info import get_map_info
from src.search.multi_goal_search import MultiGoal
from src.search.ucs import UCS
from src.search.a_star import AStar
from src.logic_pacman_vs_ghost.adv_problem import AdvProblem
from src.logic_pacman_vs_ghost.alpha_beta import AlphaBeta
from src.pacman.game_state import GameState

class TestAlgorithmExtensions(unittest.TestCase):
    def setUp(self):
        self.multi_map = load_map("maps/multi_goal_test.txt")
        self.m_spawn, self.m_goals, self.m_ghosts, self.m_foods = get_map_info(self.multi_map, return_foods=True)

        self.adv_trap_map = load_map("maps/adversarial_dead_end_trap.txt")
        self.trap_spawn, self.trap_goals, self.trap_ghosts = get_map_info(self.adv_trap_map)

    def test_extension_mst_heuristic_admissible(self):
        """
        Kiểm tra Heuristic MST là Admissible: h(start) <= path_cost thực tế.
        """
        target_food = self.m_foods if self.m_foods else self.m_goals
        prob = MultiGoal(self.m_spawn, tuple(target_food), self.multi_map)
        start_state = prob.get_pacman_spawn()
        h_val = prob.heuristic(start_state)

        searcher = AStar(prob)
        actions = searcher.search()
        self.assertIsNotNone(actions, "Phải tìm thấy lời giải")
        actual_cost = prob.measure_path_cost(actions)

        self.assertGreaterEqual(h_val, 0, "Heuristic phải không âm")
        self.assertLessEqual(h_val, actual_cost, "Heuristic MST phải Admissible (h <= h*)")

    def test_extension_mst_reduces_expanded_nodes(self):
        """
        Chứng minh Heuristic MST giúp A* giảm ít nhất 50% số node mở rộng so với UCS / A*(h=0).
        """
        target_food = self.m_foods if self.m_foods else self.m_goals
        prob_ucs = MultiGoal(self.m_spawn, tuple(target_food), self.multi_map)
        prob_astar = MultiGoal(self.m_spawn, tuple(target_food), self.multi_map)

        ucs = UCS(prob_ucs)
        ucs_acts = ucs.search()

        astar = AStar(prob_astar)
        astar_acts = astar.search()

        self.assertIsNotNone(ucs_acts)
        self.assertIsNotNone(astar_acts)
        self.assertEqual(len(ucs_acts), len(astar_acts))

        reduction = (1.0 - astar.expanded_count / ucs.expanded_count) * 100
        self.assertGreaterEqual(reduction, 50.0, f"MST Heuristic phải giảm >= 50% node (thực tế: {reduction:.1f}%)")

    def test_extension_bfs_maze_distance_caching(self):
        """
        Kiểm tra cơ chế đệm khoảng cách BFS O(1) tra cứu chính xác khoảng cách mê cung thực tế.
        """
        prob = AdvProblem(self.trap_spawn, self.trap_ghosts, self.trap_goals[0], self.adv_trap_map)
        
        d1 = prob.get_maze_distance(self.trap_spawn, self.trap_goals[0])
        d2 = prob.get_maze_distance(self.trap_spawn, self.trap_goals[0])

        self.assertEqual(d1, d2)
        self.assertGreater(d1, 0)
        manhattan = abs(self.trap_spawn[0] - self.trap_goals[0][0]) + abs(self.trap_spawn[1] - self.trap_goals[0][1])
        self.assertGreaterEqual(d1, manhattan)

    def test_extension_dead_end_and_collision_penalty(self):
        """
        Kiểm tra hàm evaluate() phạt nặng khi Ghost áp sát và phát hiện không có lối thoát an toàn.
        """
        target = self.trap_goals[0]
        prob = AdvProblem(self.trap_spawn, self.trap_ghosts, target, self.adv_trap_map)

        safe_state = GameState((1, 1), [(8, 8)], set(), 0, self.adv_trap_map)
        safe_eval = prob.evaluate(safe_state)

        danger_state = GameState((1, 1), [(1, 2)], set(), 0, self.adv_trap_map)
        danger_eval = prob.evaluate(danger_state)

        self.assertLess(danger_eval, safe_eval - 1000)

    def test_extension_alpha_beta_pruning_performance(self):
        """
        Kiểm tra thuật toán Alpha-Beta cắt tỉa hiệu quả và cho kết quả khớp 100% với Minimax.
        """
        from src.logic_pacman_vs_ghost.minimax import Minimax
        target = self.trap_goals[0]
        prob = AdvProblem(self.trap_spawn, self.trap_ghosts, target, self.adv_trap_map)

        mm = Minimax(prob, depth_limit=2)
        act_mm = mm.search()

        ab = AlphaBeta(prob, depth_limit=2)
        act_ab = ab.search()

        self.assertEqual(act_mm, act_ab, "Alpha-Beta và Minimax phải chọn cùng hành động tối ưu")
        self.assertEqual(mm.last_value, ab.last_value, "Giá trị đánh giá phải hoàn toàn tương đương")
        self.assertLessEqual(ab.expanded_count, mm.expanded_count, "Alpha-Beta phải duyệt số node <= Minimax")

if __name__ == "__main__":
    unittest.main()
