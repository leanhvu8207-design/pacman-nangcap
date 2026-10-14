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

    # Mặc định chọn h(n) theo Manhattan; có thể truyền heuristic_fn tùy biến
    def heuristic(self, state: GameState):
        if self.heuristic_fn is not None:
            return self.heuristic_fn(state)
        row, col = state.pacman_position
        target_row, target_col = self.target
        return abs(row - target_row) + abs(col - target_col)

