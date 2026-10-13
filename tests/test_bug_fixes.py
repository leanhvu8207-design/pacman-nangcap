import unittest
import pygame

from src.pacman.game_state import GameState
from src.ghost.ghost import Ghost
from src.search.multi_goal_search import MultiGoal
from src.search.pm_search_problem import PMSearchProblem
from src.search.bfs import BFS
from src.search.dfs import DFS
from src.search.ucs import UCS
from src.search.greedy import Greedy
from src.search.a_star import AStar
from main import plan_multi_food_path
from ui.controller import GameController
from ui.theme import init_fonts

class TestBugFixes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        init_fonts()

    def test_bug_01_food_at_spawn_consumed(self):
        """BUG-01: MultiGoal phải tự động hấp thu thức ăn tại vị trí xuất phát của Pacman."""
        isolated_map = ["###", "#P#", "###"]
        mg = MultiGoal((1, 1), [(1, 1)], isolated_map)
        spawn_state = mg.get_pacman_spawn()
        self.assertNotIn((1, 1), spawn_state.food, "Thức ăn tại spawn phải được loại bỏ khỏi state.food")
        self.assertEqual(spawn_state.score, 10, "Điểm phải được cộng khi ăn thức ăn tại spawn")

        searcher = BFS(mg)
        actions = searcher.search()
        self.assertIsNotNone(actions)
        self.assertEqual(actions, [])
        self.assertEqual(searcher.expanded_count, 0)

    def test_bug_02_main_multi_food_planning_does_not_break_early(self):
        """BUG-02: plan_multi_food_path trong main.py không bị ngắt sớm khi có thức ăn tại spawn."""
        simple_map = ["#####", "#   #", "#####"]
        actions, nodes, time_used = plan_multi_food_path("BFS", (1, 1), [(1, 1), (1, 2)], simple_map)
        self.assertEqual(actions, ["RIGHT"], "Pacman phải ăn viên (1, 1) và đi tiếp sang (1, 2)")
        self.assertGreater(nodes, 0)

    def test_bug_03_ui_controller_multi_food_planning(self):
        """BUG-03: _plan_multi_food_tour trong GameController không bị dừng đột ngột."""
        controller = GameController()
        controller.game_map = ["#####", "#   #", "#####"]
        controller.spawn = (1, 1)
        controller.foods = [(1, 1), (1, 2)]
        actions, nodes, time_used = controller._plan_multi_food_tour("BFS")
        self.assertEqual(actions, ["RIGHT"])

    def test_bug_04_ui_controller_path_cost_zero_at_goal(self):
        """BUG-04: GameController hiển thị path_cost = 0 thay vì None khi start == goal."""
        controller = GameController()
        controller.game_map = ["###", "# #", "###"]
        controller.spawn = (1, 1)
        controller.goals = [(1, 1)]
        controller.foods = []
        controller.set_algorithm("BFS")
        controller._run_classic_search()
        self.assertEqual(controller.path_cost, 0, "path_cost phải bằng 0 khi start == goal")
        self.assertEqual(controller.steps_taken, 0)

    def test_bug_05_ui_controller_step_mode_win(self):
        """BUG-05: Chế độ Adversarial STEP chuyển trạng thái thành WIN khi Pacman bước vào Goal."""
        controller = GameController()
        controller.game_map = ["#####", "#   #", "#####"]
        controller.spawn = (1, 1)
        controller.goals = [(1, 2)]
        controller.remaining_goals = [(1, 2)]
        controller.foods = []
        controller.remaining_foods = set()
        controller.ghosts = [(1, 3)]
        controller.set_adv_mode("STEP")
        controller.set_depth(1)
        controller._run_adversarial_search()
        self.assertEqual(controller.status, "WIN", "Status phải là WIN khi bước vào Goal trong STEP mode")

    def test_bug_06_expanded_count_zero_when_start_is_goal(self):
        """BUG-06: Số node mở rộng expanded_count phải bằng 0 khi start == goal trên tất cả thuật toán."""
        prob = PMSearchProblem((1, 1), (1, 1), ["###", "# #", "###"])
        algos = [("BFS", BFS), ("DFS", DFS), ("UCS", UCS), ("Greedy", Greedy), ("AStar", AStar)]
        for name, cls in algos:
            searcher = cls(prob)
            actions = searcher.search()
            self.assertEqual(actions, [], f"{name} phải trả về actions = []")
            self.assertEqual(searcher.expanded_count, 0, f"{name} phải có expanded_count = 0 khi start == goal")

    def test_bug_07_game_state_eq_and_hash_ignores_score(self):
        """BUG-07: GameState __eq__ và __hash__ không phụ thuộc vào score để tránh phân mảnh trạng thái."""
        gmap = ["###", "# #", "###"]
        s1 = GameState((1, 1), [(1, 2)], {(1, 3)}, 10, gmap)
        s2 = GameState((1, 1), [(1, 2)], {(1, 3)}, 990, gmap)

        self.assertEqual(s1, s2, "Hai GameState cùng vị trí và food phải bằng nhau bất kể score")
        self.assertEqual(hash(s1), hash(s2), "Hash của hai GameState phải trùng khớp bất kể score")
        self.assertIn(s1, {s2}, "s1 phải nằm trong tập set chứa s2")

    def test_bug_08_ghost_choose_action_at_pacman_pos(self):
        """BUG-08: Ghost choose_action không trả về None khi ở cùng ô với Pacman."""
        ghost = Ghost((1, 1))
        gmap = ["#####", "#   #", "#####"]
        action = ghost.choose_action(gmap, (1, 1))
        self.assertIsNotNone(action, "Ghost không được trả về None khi ở cùng ô với Pacman")
        self.assertIn(action, ["LEFT", "RIGHT"], "Ghost phải chọn hành động hợp lệ")

if __name__ == "__main__":
    unittest.main()
