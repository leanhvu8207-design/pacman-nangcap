"""Mô hình hóa bài toán đối kháng Pacman vs Ghosts và hàm đánh giá trạng thái."""

from collections import deque
from src.pacman.game_state import GameState


class AdvProblem:
    _MAZE_DIST_CACHE = {}

    def __init__(self, spawn, ghost_positions, target, game_map):
        self.pacman_spawn = spawn
        self.ghost_positions = list(ghost_positions)
        self.target = target
        self.game_map = game_map
        self.goal_distance_map = self._compute_bfs_distances(self.target)

    def _compute_bfs_distances(self, target_pos):
        if target_pos is None:
            return {}

        distance_map = {}
        distance_map[target_pos] = 0

        queue = deque()
        queue.append(target_pos)
        move_directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        while len(queue) > 0:
            current_pos = queue.popleft()
            curr_r = current_pos[0]
            curr_c = current_pos[1]
            current_dist = distance_map[current_pos]

            for dr, dc in move_directions:
                next_r = curr_r + dr
                next_c = curr_c + dc

                if next_r >= 0 and next_r < len(self.game_map):
                    if next_c >= 0 and next_c < len(self.game_map[next_r]):
                        cell_char = self.game_map[next_r][next_c]
                        neighbor = (next_r, next_c)

                        if cell_char != '#':
                            if neighbor not in distance_map:
                                distance_map[neighbor] = current_dist + 1
                                queue.append(neighbor)

        return distance_map

    def _count_exits(self, position):
        r = position[0]
        c = position[1]
        exits_count = 0
        move_directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        for dr, dc in move_directions:
            nr = r + dr
            nc = c + dc
            if nr >= 0 and nr < len(self.game_map):
                if nc >= 0 and nc < len(self.game_map[nr]):
                    if self.game_map[nr][nc] != '#':
                        exits_count = exits_count + 1

        return exits_count

    def get_num_ghosts(self):
        return len(self.ghost_positions)

    def get_start_state(self):
        initial_food_set = set()
        initial_score = 0
        ghost_copy = list(self.ghost_positions)
        initial_state = GameState(self.pacman_spawn, ghost_copy, initial_food_set, initial_score, self.game_map)
        return initial_state

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
        if pos1 == pos2:
            return 0

        map_key = tuple(self.game_map)
        if map_key not in AdvProblem._MAZE_DIST_CACHE:
            AdvProblem._MAZE_DIST_CACHE[map_key] = {}

        cache_for_map = AdvProblem._MAZE_DIST_CACHE[map_key]
        if pos1 not in cache_for_map:
            cache_for_map[pos1] = self._compute_bfs_distances(pos1)

        distances_from_pos1 = cache_for_map[pos1]
        distance = distances_from_pos1.get(pos2, 999)
        return distance

    def evaluate(self, state, depth=0):
        if state.check_pacman_caught():
            terminal_lose_score = -100000 - depth * 1000
            return terminal_lose_score

        if state.pacman_position == self.target:
            terminal_win_score = 100000 + depth * 1000
            return terminal_win_score

        dist_to_goal = self.goal_distance_map.get(state.pacman_position, 999)
        total_eval_score = -dist_to_goal * 40

        if len(state.ghost_positions) > 0:
            min_ghost_dist = float('inf')
            blocking_ghost_dist = float('inf')
            chasing_ghost_dist = float('inf')

            for ghost_pos in state.ghost_positions:
                dist_to_ghost = self.get_maze_distance(state.pacman_position, ghost_pos)
                if dist_to_ghost < min_ghost_dist:
                    min_ghost_dist = dist_to_ghost

                ghost_dist_to_goal = self.goal_distance_map.get(ghost_pos, 999)
                if ghost_dist_to_goal <= dist_to_goal:
                    if dist_to_ghost < blocking_ghost_dist:
                        blocking_ghost_dist = dist_to_ghost
                elif dist_to_ghost < chasing_ghost_dist:
                    chasing_ghost_dist = dist_to_ghost

            if min_ghost_dist <= 1:
                has_safe_escape = False
                move_directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
                pm_r = state.pacman_position[0]
                pm_c = state.pacman_position[1]

                for dr, dc in move_directions:
                    nr = pm_r + dr
                    nc = pm_c + dc
                    if 0 <= nr < len(self.game_map) and 0 <= nc < len(self.game_map[0]):
                        is_not_wall = (self.game_map[nr][nc] != '#')
                        is_not_ghost = ((nr, nc) not in state.ghost_positions)
                        if is_not_wall and is_not_ghost:
                            neighbor_dist_to_goal = self.goal_distance_map.get((nr, nc), 999)
                            if neighbor_dist_to_goal < dist_to_goal:
                                has_safe_escape = True
                                break

                if not has_safe_escape:
                    total_eval_score = total_eval_score - 50000
                else:
                    total_eval_score = total_eval_score - 500

            if blocking_ghost_dist == 2:
                total_eval_score = total_eval_score - 15000
            elif blocking_ghost_dist == 3:
                total_eval_score = total_eval_score - 4000
            elif blocking_ghost_dist == 4:
                total_eval_score = total_eval_score - 1000

            if chasing_ghost_dist >= 2:
                bonus_distance = min(chasing_ghost_dist, 6)
                total_eval_score = total_eval_score + bonus_distance * 10

        return total_eval_score

    def get_successors_for_agent(self, state, agent):
        if agent == 0:
            pacman_successors = state.get_pacman_successors()
            return pacman_successors

        ghost_index = agent - 1
        ghost_successors = state.get_ghost_successors(ghost_index)
        return ghost_successors

    def get_game_result(self, state):
        if state.check_pacman_caught():
            return 'LOSE'
        if state.pacman_position == self.target:
            return 'WIN'
        return 'PLAYING'
