import heapq
from src.pacman.game_state import GameState
from src.utils.map_info import get_tile_cost


class MultiGoal:

    def __init__(self, spawn, food, game_map, goal=None, cost_fn=None, heuristic_fn=None):
        self.pacman_spawn = spawn
        self.food = food
        self.game_map = game_map
        self.goal = goal
        if cost_fn is None:
            self.cost_fn = lambda pos: get_tile_cost(pos, self.game_map)
        else:
            self.cost_fn = cost_fn
        self.heuristic_fn = heuristic_fn
        self._mst_cache = {}
        self._dist_to = {}
        self._cached_cost_fn = None

    def get_pacman_spawn(self):
        return GameState(self.pacman_spawn, [], set(self.food),
                        0, self.game_map)

    def reached_target(self, state: GameState):
        # 1. Bắt buộc phải ăn hết toàn bộ thức ăn
        if len(state.food) > 0:
            return False
        # 2. Nếu có đích đến cuối cùng Goal (G), Pacman phải tới vị trí đó
        if self.goal is not None:
            return state.pacman_position == self.goal
        return True

    def expand_pacman_moves(self, state: GameState):
        successors = []
        actions = ["UP", "DOWN", "LEFT", "RIGHT"]
        for action in actions:
            next_state = state.move(action)
            if next_state is not None:
                step_cost = self.cost_fn(next_state.pacman_position) if self.cost_fn else 1
                successors.append((next_state, action, step_cost))
        return successors

    def measure_path_cost(self, actions):
        if not self.cost_fn:
            return len(actions)
        curr = self.get_pacman_spawn()
        total_cost = 0
        for act in actions:
            curr = curr.move(act)
            if curr:
                total_cost += self.cost_fn(curr.pacman_position)
        return total_cost

    def _reverse_dijkstra(self, target):
        """
        Tính chi phí đường đi ngắn nhất chính xác từ mọi ô hợp lệ trên bản đồ tới ô `target`
        bằng thuật toán Dijkstra ngược (xét cả tường '#' và chi phí địa hình cost_fn).
        """
        dist = {target: 0}
        pq = [(0, target)]
        rows = len(self.game_map)

        while pq:
            d, curr = heapq.heappop(pq)
            if d > dist.get(curr, float("inf")):
                continue

            r, c = curr
            step_into_curr = self.cost_fn(curr) if self.cost_fn else 1

            for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < len(self.game_map[nr]):
                    if self.game_map[nr][nc] != "#":
                        prev_pos = (nr, nc)
                        new_d = d + step_into_curr
                        if new_d < dist.get(prev_pos, float("inf")):
                            dist[prev_pos] = new_d
                            heapq.heappush(pq, (new_d, prev_pos))

        return dist

    def _build_heuristic_cache(self):
        """
        Tiền xử lý bảng khoảng cách mê cung/địa hình tới tất cả các điểm thức ăn và Goal,
        đồng thời làm mới bộ nhớ đệm MST khi hàm chi phí thay đổi.
        """
        self._mst_cache.clear()
        self._dist_to.clear()
        if self.game_map is None:
            return

        targets = set(self.food)
        if self.goal is not None:
            targets.add(self.goal)

        for t in targets:
            self._dist_to[t] = self._reverse_dijkstra(t)

    def _get_dist(self, src, dst):
        if src == dst:
            return 0
        dist_map = self._dist_to.get(dst)
        if dist_map is not None and src in dist_map:
            return dist_map[src]
        return abs(src[0] - dst[0]) + abs(src[1] - dst[1])

    def _compute_mst(self, food_key: frozenset):
        """
        Tính trọng số Cây khung nhỏ nhất (Minimum Spanning Tree - thuật toán Prim)
        trên tập các viên thức ăn còn lại dựa trên khoảng cách đường đi ngắn nhất trong mê cung.
        Kết quả được lưu cache theo frozenset(food) để truy xuất O(1).
        """
        if food_key in self._mst_cache:
            return self._mst_cache[food_key]

        nodes = list(food_key)
        n = len(nodes)
        if n <= 1:
            self._mst_cache[food_key] = 0
            return 0

        in_mst = [False] * n
        min_edge = [float("inf")] * n
        min_edge[0] = 0
        mst_weight = 0

        for _ in range(n):
            u = -1
            best = float("inf")
            for i in range(n):
                if not in_mst[i] and min_edge[i] < best:
                    best = min_edge[i]
                    u = i

            if u == -1:
                break

            in_mst[u] = True
            mst_weight += best
            pos_u = nodes[u]

            for v in range(n):
                if not in_mst[v]:
                    pos_v = nodes[v]
                    w = min(self._get_dist(pos_u, pos_v), self._get_dist(pos_v, pos_u))
                    if w < min_edge[v]:
                        min_edge[v] = w

        self._mst_cache[food_key] = mst_weight
        return mst_weight

    def heuristic(self, state: GameState):
        if self.heuristic_fn is not None:
            return self.heuristic_fn(state)
        if self.reached_target(state):
            return 0

        if self._cached_cost_fn is not self.cost_fn:
            self._build_heuristic_cache()
            self._cached_cost_fn = self.cost_fn

        pm_pos = state.pacman_position
        foods = state.food
        num_foods = len(foods)

        # 1. Nếu đã ăn hết thức ăn nhưng chưa tới đích Goal G
        if num_foods == 0:
            if self.goal is not None:
                return self._get_dist(pm_pos, self.goal)
            return 0

        # 2. Nếu chỉ còn đúng 1 viên thức ăn: đường đi tối ưu bắt buộc là pm -> f1 (-> goal)
        if num_foods == 1:
            f1 = next(iter(foods))
            cost = self._get_dist(pm_pos, f1)
            if self.goal is not None:
                cost += self._get_dist(f1, self.goal)
            return cost

        # 3. Nếu còn đúng 2 viên thức ăn: xét cả 2 thứ tự (pm -> f1 -> f2) và (pm -> f2 -> f1)
        if num_foods == 2:
            f1, f2 = tuple(foods)
            if self.goal is not None:
                path1 = self._get_dist(pm_pos, f1) + self._get_dist(f1, f2) + self._get_dist(f2, self.goal)
                path2 = self._get_dist(pm_pos, f2) + self._get_dist(f2, f1) + self._get_dist(f1, self.goal)
            else:
                path1 = self._get_dist(pm_pos, f1) + self._get_dist(f1, f2)
                path2 = self._get_dist(pm_pos, f2) + self._get_dist(f2, f1)
            return min(path1, path2)

        # 4. Nếu còn >= 3 viên thức ăn: kết hợp khoảng cách nối vào tập Food + MST(Food) + khoảng cách thoát về Goal
        food_key = frozenset(foods)
        mst_cost = self._compute_mst(food_key)

        if self.goal is not None:
            # Điểm ăn đầu tiên và điểm ăn cuối cùng trước khi về Goal trong tập >= 3 viên phải khác nhau
            min_entry_exit = min(
                self._get_dist(pm_pos, f_in) + self._get_dist(f_out, self.goal)
                for f_in in foods
                for f_out in foods
                if f_in != f_out
            )
            return mst_cost + min_entry_exit

        min_to_food = min(self._get_dist(pm_pos, f) for f in foods)
        return min_to_food + mst_cost