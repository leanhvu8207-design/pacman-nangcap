from collections import deque
from src.pacman.game_state import GameState


class AdvProblem:
    """
    Bài toán đối kháng: Pacman (MAX agent) vs các Ghost (MIN / CHANCE agents).
    Thứ tự lượt đi: Pacman (agent 0) -> Ghost 0 (agent 1) -> ... -> Ghost k-1 -> Pacman.
    Được tối ưu hóa với bộ nhớ đệm cấu trúc bản đồ O(1) (khoảng cách BFS, độ sâu ngõ cụt,
    số lối thoát tại mỗi ô) và sắp xếp nước đi thông minh (Move Ordering).
    """

    # Bộ nhớ đệm khoảng cách mê cung BFS: {map_key: {pos: {other_pos: dist}}}
    _MAZE_DIST_CACHE = {}
    # Bộ nhớ đệm cấu trúc mê cung: {map_key: {"exits": dict, "dead_end_depth": dict}}
    _MAP_STRUCTURE_CACHE = {}

    def __init__(self, spawn, ghost_positions, target, game_map):
        self.pacman_spawn = spawn
        self.ghost_positions = list(ghost_positions)
        self.target = target
        self.game_map = game_map
        self._map_key = tuple(game_map) if game_map else ()

        # Khởi tạo hoặc lấy từ cache cấu trúc bản đồ và khoảng cách tới target O(1)
        self._ensure_map_structure()
        self.goal_distance_map = self.get_distance_map(self.target)

    def _ensure_map_structure(self):
        """
        Phân tích trước cấu trúc mê cung 1 lần duy nhất cho mỗi bản đồ:
        - exits[pos]: số lối rẽ hợp lệ tại mỗi ô (phục vụ phát hiện ngã ba/ngã tư thoát hiểm).
        - dead_end_depth[pos]: độ sâu của ô nếu nằm trong nhánh ngõ cụt (phục vụ né bẫy ngõ cụt).
        """
        if not self.game_map:
            self._exits_map = {}
            self._dead_end_map = {}
            return

        if self._map_key in AdvProblem._MAP_STRUCTURE_CACHE:
            cached = AdvProblem._MAP_STRUCTURE_CACHE[self._map_key]
            self._exits_map = cached["exits"]
            self._dead_end_map = cached["dead_end_depth"]
            return

        rows = len(self.game_map)
        adj = {}
        exits = {}

        for r in range(rows):
            cols = len(self.game_map[r])
            for c in range(cols):
                if self.game_map[r][c] == "#":
                    continue
                pos = (r, c)
                neighbors = []
                for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < rows and 0 <= nc < len(self.game_map[nr]):
                        if self.game_map[nr][nc] != "#":
                            neighbors.append((nr, nc))
                adj[pos] = neighbors
                exits[pos] = len(neighbors)

        # Tỉa ngõ cụt (dead-end peeling) để xác định các ô nằm trong hẻm cụt và độ sâu của chúng
        deg = dict(exits)
        queue = deque(pos for pos, d in deg.items() if d <= 1)
        peeled_order = []
        in_peeled = set(queue)
        parent_in_tree = {}

        while queue:
            u = queue.popleft()
            peeled_order.append(u)
            for v in adj[u]:
                if v not in in_peeled:
                    parent_in_tree[u] = v
                    deg[v] -= 1
                    if deg[v] <= 1:
                        in_peeled.add(v)
                        queue.append(v)

        dead_end_depth = {pos: 0 for pos in adj}
        for u in reversed(peeled_order):
            p = parent_in_tree.get(u)
            if p is not None:
                dead_end_depth[u] = dead_end_depth.get(p, 0) + 1
            else:
                dead_end_depth[u] = 1

        AdvProblem._MAP_STRUCTURE_CACHE[self._map_key] = {
            "exits": exits,
            "dead_end_depth": dead_end_depth,
        }
        self._exits_map = exits
        self._dead_end_map = dead_end_depth

    def _compute_bfs_distances(self, target_pos):
        """
        Tính khoảng cách đường đi ngắn nhất thực tế bằng BFS từ target_pos đến mọi ô trống.
        """
        if target_pos is None or not self.game_map:
            return {}
        distance_map = {target_pos: 0}
        queue = deque([target_pos])
        rows = len(self.game_map)

        while queue:
            curr_r, curr_c = queue.popleft()
            current_dist = distance_map[(curr_r, curr_c)]

            for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                next_r = curr_r + dr
                next_c = curr_c + dc
                if 0 <= next_r < rows and 0 <= next_c < len(self.game_map[next_r]):
                    if self.game_map[next_r][next_c] != "#":
                        neighbor = (next_r, next_c)
                        if neighbor not in distance_map:
                            distance_map[neighbor] = current_dist + 1
                            queue.append(neighbor)

        return distance_map

    def get_distance_map(self, pos):
        """Lấy bảng khoảng cách BFS từ `pos` tới mọi ô (được lưu cache O(1) theo bản đồ)"""
        if pos is None:
            return {}
        if self._map_key not in AdvProblem._MAZE_DIST_CACHE:
            AdvProblem._MAZE_DIST_CACHE[self._map_key] = {}
        cache = AdvProblem._MAZE_DIST_CACHE[self._map_key]
        if pos not in cache:
            cache[pos] = self._compute_bfs_distances(pos)
        return cache[pos]

    def _count_exits(self, position):
        """Đếm số lối thoát hợp lệ quanh một vị trí (tra cứu O(1) từ cache)"""
        if position in self._exits_map:
            return self._exits_map[position]
        r, c = position
        exits = 0
        for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < len(self.game_map) and 0 <= nc < len(self.game_map[nr]):
                if self.game_map[nr][nc] != "#":
                    exits += 1
        return exits

    def get_num_ghosts(self):
        return len(self.ghost_positions)

    def get_start_state(self):
        return GameState(self.pacman_spawn, self.ghost_positions.copy(), set(), 0, self.game_map)

    def get_next_agent(self, current_agent):
        num_ghosts = self.get_num_ghosts()
        if num_ghosts == 0:
            return 0
        if current_agent == 0:
            return 1
        if current_agent < num_ghosts:
            return current_agent + 1
        return 0

    def is_terminal(self, state):
        if state.check_pacman_caught():
            return True
        if state.pacman_position == self.target:
            return True
        return False

    def get_maze_distance(self, pos1, pos2):
        """Lấy khoảng cách mê cung thực tế giữa 2 ô (tra cứu O(1) từ cache)"""
        if pos1 == pos2:
            return 0
        dist_map = self.get_distance_map(pos1)
        return dist_map.get(pos2, 999)

    def evaluate(self, state, depth=0):
        """
        Hàm đánh giá trạng thái đối kháng nâng cao cho Pacman (MAX agent):
        - Ưu tiên tiến về mục tiêu theo khoảng cách BFS thực tế trong mê cung.
        - Phân loại Ghost chặn đầu (blocking) và Ghost đuổi sau (chasing).
        - Phát hiện thế gọng kìm khi có nhiều Ghost vây ép và thưởng khi đứng ở ngã giao nhiều lối thoát.
        - Tránh chui vào các nhánh ngõ cụt (dead-end pocket) khi có Ghost ở gần.
        """
        # 1. Trạng thái kết thúc: Pacman bị bắt -> phạt nặng hơn nếu chết sớm
        if state.check_pacman_caught():
            return -100000 - depth * 1000

        # 2. Trạng thái kết thúc: Pacman tới đích -> thưởng chiến thắng sớm hơn
        pac_pos = state.pacman_position
        if pac_pos == self.target:
            return 100000 + depth * 1000

        # 3. Khoảng cách mê cung thực tế từ Pacman đến mục tiêu
        dist_goal = self.goal_distance_map.get(pac_pos, 999)
        score = -dist_goal * 40

        # 4. Đánh giá chiến thuật đối kháng với các Ghost
        ghosts = state.ghost_positions
        if ghosts:
            min_ghost_dist = float("inf")
            second_ghost_dist = float("inf")
            blocking_dist = float("inf")
            chasing_dist = float("inf")

            pac_dist_map = self.get_distance_map(pac_pos)
            for ghost_pos in ghosts:
                dist = pac_dist_map.get(ghost_pos, 999)
                if dist < min_ghost_dist:
                    second_ghost_dist = min_ghost_dist
                    min_ghost_dist = dist
                elif dist < second_ghost_dist:
                    second_ghost_dist = dist

                ghost_to_goal = self.goal_distance_map.get(ghost_pos, 999)
                if ghost_to_goal <= dist_goal:
                    if dist < blocking_dist:
                        blocking_dist = dist
                else:
                    if dist < chasing_dist:
                        chasing_dist = dist

            # 4a. Nguy cơ va chạm trực tiếp trong bước kế tiếp (khoảng cách <= 1)
            if min_ghost_dist <= 1:
                has_escape = False
                r, c = pac_pos
                for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < len(self.game_map) and 0 <= nc < len(self.game_map[nr]):
                        if self.game_map[nr][nc] != "#" and (nr, nc) not in ghosts:
                            if self.goal_distance_map.get((nr, nc), 999) < dist_goal:
                                has_escape = True
                                break
                if not has_escape:
                    score -= 50000
                else:
                    score -= 500

            # 4b. Ghost chặn trước mặt / ở gần Goal hơn Pacman (nguy cơ bị chặn họng)
            if blocking_dist == 2:
                score -= 15000
            elif blocking_dist == 3:
                score -= 4000
            elif blocking_dist == 4:
                score -= 1000

            # 4c. Ghost bám đuổi phía sau (Pacman đang dẫn trước trong cuộc đua về đích)
            if chasing_dist >= 2:
                score += min(chasing_dist, 6) * 10

            # 4d. Tránh bẫy ngõ cụt (Dead-end trap) nếu mục tiêu không nằm trong ngõ cụt đó
            dead_depth = self._dead_end_map.get(pac_pos, 0)
            target_dead_depth = self._dead_end_map.get(self.target, 0) if self.target else 0
            if dead_depth > 0 and target_dead_depth == 0:
                if min_ghost_dist <= dead_depth * 2 + 2:
                    score -= 8000 + dead_depth * 1500

            # 4e. Chống thế gọng kìm (Pincer Avoidance) khi có từ 2 Ghost trở lên áp sát
            if len(ghosts) >= 2 and min_ghost_dist <= 4 and second_ghost_dist <= 5:
                exits = self._count_exits(pac_pos)
                if exits <= 2:
                    score -= (10 - min_ghost_dist - second_ghost_dist) * 250
                elif exits >= 3:
                    score += 120

        return score

    def get_successors_for_agent(self, state, agent):
        if agent == 0:
            return state.get_pacman_successors()
        ghost_index = agent - 1
        return state.get_ghost_successors(ghost_index)

    def get_ordered_successors(self, state, agent):
        """
        Sắp xếp thứ tự duyệt các nước đi (Move Ordering) để tối đa hóa hiệu quả cắt tỉa Alpha-Beta:
        - Với Pacman (MAX, agent=0): thử nước đi tiến gần đích và xa Ghost trước.
        - Với Ghost (MIN, agent>0): thử nước đi rút ngắn khoảng cách tới Pacman trước.
        """
        successors = self.get_successors_for_agent(state, agent)
        if len(successors) <= 1:
            return successors

        if agent == 0:
            ghosts = state.ghost_positions
            def pac_sort_key(item):
                next_state = item[0]
                npos = next_state.pacman_position
                if npos in ghosts:
                    return 100000
                d_goal = self.goal_distance_map.get(npos, 999)
                if ghosts:
                    d_map = self.get_distance_map(npos)
                    min_g = min(d_map.get(gp, 999) for gp in ghosts)
                    if min_g <= 1:
                        return d_goal + 5000
                    return d_goal - min(min_g, 5) * 0.5
                return d_goal

            return sorted(successors, key=pac_sort_key)
        else:
            ghost_idx = agent - 1
            pac_dist_map = self.get_distance_map(state.pacman_position)
            return sorted(
                successors,
                key=lambda item: pac_dist_map.get(item[0].ghost_positions[ghost_idx], 999)
            )

    def get_game_result(self, state):
        if state.check_pacman_caught():
            return "LOSE"
        if state.pacman_position == self.target:
            return "WIN"
        return "PLAYING"
