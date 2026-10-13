import unittest
from src.utils.map_loader import load_map
from src.utils.map_info import get_map_info
from src.search.pm_search_problem import PMSearchProblem
from src.search.multi_goal_search import MultiGoal
from src.search.bfs import BFS
from src.search.dfs import DFS
from src.search.ucs import UCS
from src.search.greedy import Greedy
from src.search.a_star import AStar

class TestClassicalSearch(unittest.TestCase):
    """
    Kiểm thử hồi quy (Regression Test) cho các thuật toán tìm kiếm cổ điển đơn tác tử.
    Đảm bảo việc cải tiến phần Minimax không làm ảnh hưởng đến các thuật toán cũ.
    """

    def setUp(self):
        """
        Khởi tạo dữ liệu bản đồ cho các ca kiểm thử.
        """
        self.small_map = load_map("maps/adversarial_small.txt")
        self.spawn, self.goals, _ = get_map_info(self.small_map)
        self.problem = PMSearchProblem(self.spawn, self.goals[0], self.small_map)

    def test_bfs_finds_optimal_path(self):
        """
        Kiểm tra BFS tìm được đường đi ngắn nhất (16 bước trên adversarial_small.txt).
        """
        searcher = BFS(self.problem)
        actions = searcher.search()
        self.assertIsNotNone(actions)
        self.assertEqual(len(actions), 16)
        self.assertEqual(actions, ["LEFT"] * 16)
        self.assertGreater(searcher.expanded_count, 0)

    def test_dfs_finds_path(self):
        """
        Kiểm tra DFS tìm được đường đi hợp lệ đến đích.
        """
        searcher = DFS(self.problem)
        actions = searcher.search()
        self.assertIsNotNone(actions)
        self.assertGreater(len(actions), 0)

    def test_ucs_finds_optimal_path(self):
        """
        Kiểm tra UCS tìm được đường đi có chi phí tối ưu (16 bước).
        """
        searcher = UCS(self.problem)
        actions = searcher.search()
        self.assertIsNotNone(actions)
        self.assertEqual(len(actions), 16)
        self.assertEqual(actions, ["LEFT"] * 16)

    def test_greedy_finds_path(self):
        """
        Kiểm tra Greedy Best-First Search tìm được đường đi đến đích.
        """
        searcher = Greedy(self.problem)
        actions = searcher.search()
        self.assertIsNotNone(actions)
        self.assertGreater(len(actions), 0)

    def test_a_star_finds_optimal_path(self):
        """
        Kiểm tra A* tìm được đường đi tối ưu (16 bước).
        """
        searcher = AStar(self.problem)
        actions = searcher.search()
        self.assertIsNotNone(actions)
        self.assertEqual(len(actions), 16)
        self.assertEqual(actions, ["LEFT"] * 16)

    def test_multi_goal_search(self):
        """
        Kiểm tra bài toán MultiGoal giải quyết được nhiều mục tiêu Food bằng BFS.
        """
        multi_map = load_map("maps/multi_goal_test.txt")
        m_spawn, m_goals, _ = get_map_info(multi_map)
        multi_problem = MultiGoal(m_spawn, tuple(m_goals), multi_map)

        searcher = BFS(multi_problem)
        actions = searcher.search()
        self.assertIsNotNone(actions)
        self.assertGreater(len(actions), 0)

    def test_multi_goal_with_food_and_final_goal(self):
        """
        Kiểm tra MultiGoal bắt buộc ăn hết toàn bộ Food (.) và về đích Goal (G).
        """
        s, goals, _, foods = get_map_info(self.small_map, return_foods=True)
        self.assertGreater(len(foods), 0)
        self.assertGreater(len(goals), 0)

        mg_problem = MultiGoal(s, tuple(foods), self.small_map, goal=goals[0])
        searcher = BFS(mg_problem)
        actions = searcher.search()
        self.assertIsNotNone(actions)
        self.assertGreater(len(actions), 0)

        curr_state = mg_problem.get_pacman_spawn()
        for act in actions:
            curr_state = curr_state.move(act)
        self.assertEqual(len(curr_state.food), 0, "Pacman phải ăn hết toàn bộ food")
        self.assertEqual(curr_state.pacman_position, goals[0], "Pacman phải kết thúc tại ô Goal G")

    def test_unsolvable_map_returns_none(self):
        """
        Kiểm tra bản đồ không có lời giải (no_solution_map.txt): các thuật toán phải trả về None an toàn.
        """
        no_sol_map = load_map("maps/no_solution_map.txt")
        self.assertIsNotNone(no_sol_map)
        s, goals, _ = get_map_info(no_sol_map)
        prob = PMSearchProblem(s, goals[0], no_sol_map)

        self.assertIsNone(BFS(prob).search())
        self.assertIsNone(DFS(prob).search())
        self.assertIsNone(UCS(prob).search())
        self.assertIsNone(Greedy(prob).search())
        self.assertIsNone(AStar(prob).search())

    def test_a_star_zero_heuristic_equivalence_to_ucs(self):
        """
        Kiểm tra A* với h(n) = 0 mở rộng số node tương đương và cho cùng chi phí như UCS.
        """
        prob_ucs = PMSearchProblem(self.spawn, self.goals[0], self.small_map)
        prob_a0 = PMSearchProblem(self.spawn, self.goals[0], self.small_map, heuristic_fn=lambda st: 0)

        ucs_act = UCS(prob_ucs).search()
        a0_act = AStar(prob_a0).search()

        self.assertEqual(len(ucs_act), len(a0_act))
        self.assertEqual(prob_ucs.measure_path_cost(ucs_act), prob_a0.measure_path_cost(a0_act))

    def test_large_map_search(self):
        """
        Kiểm tra tìm kiếm trên bản đồ lớn (maps/large_map.txt).
        A* phải tìm đường tối ưu (24 bước) và mở rộng ít node hơn hẳn BFS.
        """
        lg_map = load_map("maps/large_map.txt")
        s, goals, _ = get_map_info(lg_map)
        prob = PMSearchProblem(s, goals[0], lg_map)

        bfs_searcher = BFS(prob)
        bfs_act = bfs_searcher.search()

        astar_searcher = AStar(prob)
        astar_act = astar_searcher.search()

        self.assertIsNotNone(bfs_act)
        self.assertIsNotNone(astar_act)
        self.assertEqual(len(bfs_act), len(astar_act))
        self.assertLess(astar_searcher.expanded_count, bfs_searcher.expanded_count)

    def test_non_uniform_step_cost(self):
        """
        Kiểm tra cơ chế trọng số di chuyển không đồng nhất (Non-uniform cost).
        """
        def weighted_cost(pos):
            r, c = pos
            return 5 if c > 5 else 1

        prob = PMSearchProblem(self.spawn, self.goals[0], self.small_map, cost_fn=weighted_cost)
        ucs_searcher = UCS(prob)
        actions = ucs_searcher.search()
        self.assertIsNotNone(actions)
        total_cost = prob.measure_path_cost(actions)
        self.assertGreater(total_cost, len(actions))

if __name__ == "__main__":
    unittest.main()
