from collections import deque
from src.pacman.game_state import GameState


class AdvProblem:
    """
    Bài toán đối kháng: Pacman (MAX agent) vs các Ghost (MIN agents).
    Thứ tự lượt đi: Pacman (agent 0) -> Ghost 0 (agent 1) -> ... -> Ghost k-1 -> Pacman
    """

    def __init__(self, spawn, ghost_positions, target, game_map):
        self.pacman_spawn = spawn
        self.ghost_positions = list(ghost_positions)
        self.target = target
        self.game_map = game_map

        # Tính trước bảng khoảng cách mê cung (BFS) từ target tới mọi ô trống
        self.goal_distance_map = self._compute_bfs_distances(self.target)

    def _compute_bfs_distances(self, target_pos):
        """
        Tính khoảng cách đường đi ngắn nhất thực tế bằng BFS từ target_pos đến mọi ô trống.
        Đầu vào: target_pos (tuple (r, c)).
        Đầu ra: dict lưu khoảng cách từ mỗi ô tới target_pos.
        """
        if target_pos is None:
            return {}
        distance_map = {}
        distance_map[target_pos] = 0

        queue = deque()
        queue.append(target_pos)

        while len(queue) > 0:
            current_pos = queue.popleft()
            curr_r, curr_c = current_pos
            current_dist = distance_map[current_pos]

            # Thử 4 hướng di chuyển: lên, xuống, trái, phải
            directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
            for dr, dc in directions:
                next_r = curr_r + dr
                next_c = curr_c + dc

                # Kiểm tra biên bản đồ
                if next_r >= 0 and next_r < len(self.game_map):
                    if next_c >= 0 and next_c < len(self.game_map[next_r]):
                        # Không đi vào tường
                        if self.game_map[next_r][next_c] != "#":
                            neighbor = (next_r, next_c)
                            if neighbor not in distance_map:
                                distance_map[neighbor] = current_dist + 1
                                queue.append(neighbor)

        return distance_map

    def _count_exits(self, position):
        """
        Đếm số lối thoát hợp lệ (không phải tường) quanh một vị trí.
        Đầu vào: position (tuple (r, c)).
        Đầu ra: số lượng hướng đi khả dụng (int).
        """
        r, c = position
        exits = 0
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        for dr, dc in directions:
            nr = r + dr
            nc = c + dc
            if nr >= 0 and nr < len(self.game_map):
                if nc >= 0 and nc < len(self.game_map[nr]):
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

    # Bộ nhớ đệm khoảng cách mê cung BFS để tra cứu tức thì O(1)
    _MAZE_DIST_CACHE = {}

    def get_maze_distance(self, pos1, pos2):
        """
        Lấy khoảng cách mê cung thực tế giữa 2 ô (có tính tường vật cản).
        """
        if pos1 == pos2:
            return 0
        map_key = tuple(self.game_map)
        if map_key not in AdvProblem._MAZE_DIST_CACHE:
            AdvProblem._MAZE_DIST_CACHE[map_key] = {}
        cache = AdvProblem._MAZE_DIST_CACHE[map_key]
        if pos1 not in cache:
            cache[pos1] = self._compute_bfs_distances(pos1)
        return cache[pos1].get(pos2, 999)

    def evaluate(self, state, depth=0):
        """
        Đánh giá giá trị của trạng thái đối với Pacman (MAX agent).
        Đầu vào: state (đối tượng GameState), depth (độ sâu còn lại).
        Đầu ra: điểm số đánh giá (float / int). Điểm càng cao càng có lợi cho Pacman.
        """
        # Trạng thái kết thúc: Pacman bị bắt -> phạt nặng hơn nếu chết sớm
        if state.check_pacman_caught():
            return -100000 - depth * 1000

        # Trạng thái kết thúc: Pacman tới đích -> thưởng chiến thắng sớm hơn
        if state.pacman_position == self.target:
            return 100000 + depth * 1000

        pacman_r, pacman_c = state.pacman_position

        # Khoảng cách mê cung thực tế từ Pacman đến mục tiêu
        dist_goal = self.goal_distance_map.get(state.pacman_position, 999)

        # Điểm cơ sở theo khoảng cách tới mục tiêu (trọng số cao để ưu tiên tiến về đích)
        score = -dist_goal * 40

        # Tính toán ảnh hưởng của Ghost nếu có Ghost trên bản đồ
        if len(state.ghost_positions) > 0:
            min_ghost_dist = float("inf")
            blocking_dist = float("inf")
            chasing_dist = float("inf")

            for ghost_pos in state.ghost_positions:
                dist = self.get_maze_distance(state.pacman_position, ghost_pos)
                if dist < min_ghost_dist:
                    min_ghost_dist = dist
                ghost_to_goal = self.goal_distance_map.get(ghost_pos, 999)
                if ghost_to_goal <= dist_goal:
                    if dist < blocking_dist:
                        blocking_dist = dist
                else:
                    if dist < chasing_dist:
                        chasing_dist = dist

            # 1. Nguy cơ va chạm trực tiếp trong bước kế tiếp (khoảng cách <= 1)
            if min_ghost_dist <= 1:
                # Kiểm tra xem Pacman có lối thoát hợp lệ hướng về đích không
                has_escape = False
                for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nr, nc = state.pacman_position[0] + dr, state.pacman_position[1] + dc
                    if 0 <= nr < len(self.game_map) and 0 <= nc < len(self.game_map[0]):
                        if self.game_map[nr][nc] != "#" and (nr, nc) not in state.ghost_positions:
                            if self.goal_distance_map.get((nr, nc), 999) < dist_goal:
                                has_escape = True
                                break
                if not has_escape:
                    score -= 50000
                else:
                    # Pacman đang dẫn trước và có lối thoát mở về phía đích -> chỉ trừ nhẹ để không hoảng loạn quay đầu
                    score -= 500

            # 2. Ghost chặn trước mặt / ở gần Goal hơn Pacman (nguy cơ bị chặn họng)
            if blocking_dist == 2:
                score -= 15000
            elif blocking_dist == 3:
                score -= 4000
            elif blocking_dist == 4:
                score -= 1000

            # 3. Ghost bám đuổi phía sau (Pacman đang dẫn trước trong cuộc đua về đích)
            if chasing_dist >= 2:
                score += min(chasing_dist, 6) * 10

        return score

    def get_successors_for_agent(self, state, agent):
        if agent == 0:
            return state.get_pacman_successors()
        ghost_index = agent - 1
        return state.get_ghost_successors(ghost_index)

    def get_game_result(self, state):
        if state.check_pacman_caught():
            return "LOSE"
        if state.pacman_position == self.target:
            return "WIN"
        return "PLAYING"
