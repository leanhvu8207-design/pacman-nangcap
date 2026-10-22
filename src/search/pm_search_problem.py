from collections import deque
from src.pacman.game_state import GameState
from src.utils.map_info import get_tile_cost


class PMSearchProblem:
    def __init__(self, spawn, target, game_map, cost_fn=None, heuristic_fn=None):
        self.pacman_spawn = spawn
        self.target = target
        self.game_map = game_map
        # Nếu không truyền cost_fn, tự động dùng hàm tính chi phí theo địa hình bản đồ
        if cost_fn is None:
            self.cost_fn = lambda pos: get_tile_cost(pos, self.game_map)
        else:
            self.cost_fn = cost_fn
        self.heuristic_fn = heuristic_fn
        self._cached_cost_fn = None
        self._h_cache = {}

    # state = (row, col)
    def get_pacman_spawn(self):  # Lấy về địa chỉ của pacman
        return GameState(
            self.pacman_spawn, [], set(), 0, self.game_map
        )

    def reached_target(self, state: GameState):  # Check đã tới target chưa
        return state.pacman_position == self.target

    def expand_pacman_moves(self, state):
        successors = []
        actions = ["UP", "DOWN", "LEFT", "RIGHT"]

        for action in actions:
            next_state = state.move(action)
            if next_state is not None:
                step_cost = self.cost_fn(next_state.pacman_position) if self.cost_fn else 1
                successors.append((next_state, action, step_cost))

        return successors

    def measure_path_cost(self, actions):  # Tính chi phí dùng cho UCS và A*
        if not self.cost_fn:
            return len(actions)
        curr = self.get_pacman_spawn()
        total_cost = 0
        for act in actions:
            curr = curr.move(act)
            if curr:
                total_cost += self.cost_fn(curr.pacman_position)
        return total_cost

    def _build_heuristic_cache(self):
        """
        Xây dựng bảng heuristic nâng cao (Admissible & Consistent) cho bài toán đơn mục tiêu:
        1. Khoảng cách Manhattan cơ sở kết hợp chi phí bước vào ô đích.
        2. Cộng phạt vòng tránh (+2) khi có tường chắn trực tiếp trên cùng hàng/cột
           hoặc bị chặn góc chữ L về phía mục tiêu.
        3. Cắt tỉa nhánh ngõ cụt (dead-end peeling) và lan truyền chi phí hành lang hẹp (bậc <= 2)
           theo bất đẳng thức Bellman: h(u) = max(h(u), min_{v in N(u)} (cost(v) + h(v))).
        """
        self._h_cache = {}
        if self.target is None or self.game_map is None:
            return

        tr, tc = self.target
        rows = len(self.game_map)
        adj = {}
        tile_cost = {}

        def is_open(r, c):
            return 0 <= r < rows and 0 <= c < len(self.game_map[r]) and self.game_map[r][c] != "#"

        for r in range(rows):
            for c in range(len(self.game_map[r])):
                if not is_open(r, c):
                    continue
                u = (r, c)
                tile_cost[u] = self.cost_fn(u) if self.cost_fn else 1
                neighbors = []
                for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                    nr, nc = r + dr, c + dc
                    if is_open(nr, nc):
                        neighbors.append((nr, nc))
                adj[u] = neighbors

        target_extra = max(0, tile_cost.get(self.target, 1) - 1)

        # 1. Khởi tạo heuristic cơ sở: Manhattan + phạt vật cản trực tiếp
        h = {}
        for u in adj:
            if u == self.target:
                h[u] = 0
                continue
            r, c = u
            d = abs(r - tr) + abs(c - tc) + target_extra

            if r == tr:
                c_min, c_max = (c, tc) if c < tc else (tc, c)
                if any(self.game_map[r][cm] == "#" for cm in range(c_min + 1, c_max)):
                    d += 2
            elif c == tc:
                r_min, r_max = (r, tr) if r < tr else (tr, r)
                if any(self.game_map[rm][c] == "#" for rm in range(r_min + 1, r_max)):
                    d += 2
            else:
                dr = 1 if tr > r else -1
                dc = 1 if tc > c else -1
                if not is_open(r + dr, c) and not is_open(r, c + dc):
                    d += 2

            h[u] = d

        # 2. Tỉa ngõ cụt (dead-end peeling) từ lá về ngã rẽ
        deg = {u: len(neighbors) for u, neighbors in adj.items()}
        queue = deque(
            u for u, d in deg.items()
            if u != self.target and u != self.pacman_spawn and d <= 1
        )
        peeled_order = []
        in_peeled = set(queue)

        while queue:
            u = queue.popleft()
            peeled_order.append(u)
            for v in adj[u]:
                if v != self.target and v != self.pacman_spawn and v not in in_peeled:
                    deg[v] -= 1
                    if deg[v] <= 1:
                        in_peeled.add(v)
                        queue.append(v)

        # 3. Lan truyền cận dưới hợp lệ dọc theo các hành lang hẹp (bậc <= 2)
        corridor_nodes = [u for u in adj if u != self.target and len(adj[u]) <= 2]
        for _ in range(16):
            changed = False
            for u in corridor_nodes:
                if adj[u]:
                    best_step = min(tile_cost[v] + h[v] for v in adj[u])
                    if best_step > h[u]:
                        h[u] = best_step
                        changed = True
            if not changed:
                break

        # 4. Lan truyền chính xác từ ngã rẽ vào các nhánh ngõ cụt đã tỉa
        for u in reversed(peeled_order):
            if adj[u]:
                best_step = min(tile_cost[v] + h[v] for v in adj[u])
                if best_step > h[u]:
                    h[u] = best_step

        self._h_cache = h

    def heuristic(self, state: GameState):
        if self.heuristic_fn is not None:
            return self.heuristic_fn(state)
        if self.reached_target(state):
            return 0
        if self._cached_cost_fn is not self.cost_fn:
            self._build_heuristic_cache()
            self._cached_cost_fn = self.cost_fn

        pos = state.pacman_position
        if pos in self._h_cache:
            return self._h_cache[pos]

        row, col = pos
        target_row, target_col = self.target
        return abs(row - target_row) + abs(col - target_col)
