"""Mô hình hóa bài toán tìm kiếm đường đi cho Pacman trong mê cung."""

from src.pacman.game_state import GameState


class PMSearchProblem:
    def __init__(self, spawn, target, game_map, cost_fn=None, heuristic_fn=None):
        self.pacman_spawn = spawn
        self.target = target
        self.game_map = game_map
        self.cost_fn = cost_fn
        self.heuristic_fn = heuristic_fn

    def get_pacman_spawn(self):
        ghost_positions = []
        food_set = set()
        initial_score = 0
        initial_state = GameState(self.pacman_spawn, ghost_positions, food_set, initial_score, self.game_map)
        return initial_state

    def reached_target(self, state: GameState):
        is_at_target = (state.pacman_position == self.target)
        return is_at_target

    def get_step_cost(self, position):
        if self.cost_fn is not None:
            return self.cost_fn(position)

        r, c = position
        if 0 <= r < len(self.game_map) and 0 <= c < len(self.game_map[r]):
            tile = self.game_map[r][c]
            if tile == '~':
                return 2
            if tile == 'S':
                return 3

        return 1

    def expand_pacman_moves(self, state: GameState):
        successors = []
        valid_actions = ['UP', 'DOWN', 'LEFT', 'RIGHT']

        for action in valid_actions:
            next_state = state.move(action)
            if next_state is not None:
                step_cost = self.get_step_cost(next_state.pacman_position)
                successor_entry = (next_state, action, step_cost)
                successors.append(successor_entry)

        return successors

    def measure_path_cost(self, actions):
        if actions is None:
            return 0

        current_state = self.get_pacman_spawn()
        total_cost = 0

        for action in actions:
            current_state = current_state.move(action)
            if current_state is not None:
                cost_of_step = self.get_step_cost(current_state.pacman_position)
                total_cost = total_cost + cost_of_step

        return total_cost

    def heuristic(self, state: GameState):
        if self.heuristic_fn is not None:
            return self.heuristic_fn(state)

        pacman_row = state.pacman_position[0]
        pacman_col = state.pacman_position[1]
        target_row = self.target[0]
        target_col = self.target[1]

        row_diff = abs(pacman_row - target_row)
        col_diff = abs(pacman_col - target_col)
        manhattan_distance = row_diff + col_diff
        return manhattan_distance
