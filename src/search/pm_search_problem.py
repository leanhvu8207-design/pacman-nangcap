from src.pacman.game_state import GameState

class PMSearchProblem:
    def __init__(self, spawn, target, game_map, cost_fn=None, heuristic_fn=None):
        self.pacman_spawn = spawn
        self.target = target
        self.game_map = game_map
        self.cost_fn = cost_fn
        self.heuristic_fn = heuristic_fn

    def get_pacman_spawn(self):
        return GameState(self.pacman_spawn, [], set(), 0, self.game_map)

    def reached_target(self, state: GameState):
        return state.pacman_position == self.target

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
        for action in ["UP", "DOWN", "LEFT", "RIGHT"]:
            next_state = state.move(action)
            if next_state is not None:
                step_cost = self.get_step_cost(next_state.pacman_position)
                successors.append((next_state, action, step_cost))
        return successors

    def measure_path_cost(self, actions):
        if actions is None:
            return 0
        curr = self.get_pacman_spawn()
        total_cost = 0
        for act in actions:
            curr = curr.move(act)
            if curr:
                total_cost += self.get_step_cost(curr.pacman_position)
        return total_cost

    def heuristic(self, state: GameState):
        if self.heuristic_fn is not None:
            return self.heuristic_fn(state)
        row, col = state.pacman_position
        target_row, target_col = self.target
        return abs(row - target_row) + abs(col - target_col)
