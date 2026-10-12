from src.pacman.game_state import GameState

class MultiGoal:
    
    def __init__(self, spawn, food, game_map, goal=None, cost_fn=None, heuristic_fn=None):
        self.pacman_spawn = spawn
        self.food = food
        self.game_map = game_map
        self.goal = goal
        self.cost_fn = cost_fn
        self.heuristic_fn = heuristic_fn
    
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
    
    def heuristic(self, state: GameState):
        if self.heuristic_fn is not None:
            return self.heuristic_fn(state)
        if self.reached_target(state):
            return 0
        
        pm_r, pm_c = state.pacman_position

        # Nếu đã ăn hết thức ăn nhưng chưa tới đích Goal G
        if len(state.food) == 0:
            if self.goal is not None:
                gr, gc = self.goal
                return abs(pm_r - gr) + abs(pm_c - gc)
            return 0
        
        # Nếu vẫn còn thức ăn
        max_dist_to_food = max(abs(pm_r - fr) + abs(pm_c - fc) for fr, fc in state.food)
        
        # Nếu có thêm đích Goal G sau khi ăn hết food
        if self.goal is not None:
            gr, gc = self.goal
            dist_to_goal = abs(pm_r - gr) + abs(pm_c - gc)
            return max(max_dist_to_food, dist_to_goal)

        return max_dist_to_food