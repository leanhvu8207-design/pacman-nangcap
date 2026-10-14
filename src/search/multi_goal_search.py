from src.pacman.game_state import GameState

class MultiGoal:
    
    def __init__(self, spawn, food, game_map, goal=None, cost_fn=None, heuristic_fn=None):
        self.pacman_spawn = spawn
        self.food = food
        self.game_map = game_map
        self.goal = goal
        self.cost_fn = cost_fn
        self.heuristic_fn = heuristic_fn
        self._mst_cache = {}
    
    def get_pacman_spawn(self):
        initial_food = set(self.food)
        initial_score = 0
        if self.pacman_spawn in initial_food:
            initial_food.remove(self.pacman_spawn)
            initial_score += 10
        return GameState(self.pacman_spawn, [], initial_food,
                        initial_score, self.game_map)
    
    def reached_target(self, state: GameState):
        if len(state.food) > 0:
            return False
        if self.goal is not None:
            return state.pacman_position == self.goal
        return True
    
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
        actions = ["UP", "DOWN", "LEFT", "RIGHT"]
        for action in actions:
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
    
    def _compute_mst_cost(self, foods):
        """
        Tính chi phí Cây khung nhỏ nhất (MST) qua danh sách các điểm thức ăn bằng Prim.
        """
        n = len(foods)
        if n <= 1:
            return 0
        if n == 2:
            return abs(foods[0][0] - foods[1][0]) + abs(foods[0][1] - foods[1][1])

        in_tree = [False] * n
        in_tree[0] = True
        min_dist = [abs(foods[0][0] - foods[i][0]) + abs(foods[0][1] - foods[i][1]) for i in range(n)]
        total_cost = 0

        for _ in range(n - 1):
            best_idx = -1
            best_val = float("inf")
            for i in range(n):
                if not in_tree[i] and min_dist[i] < best_val:
                    best_val = min_dist[i]
                    best_idx = i

            if best_idx == -1:
                break

            in_tree[best_idx] = True
            total_cost += best_val

            for i in range(n):
                if not in_tree[i]:
                    d = abs(foods[best_idx][0] - foods[i][0]) + abs(foods[best_idx][1] - foods[i][1])
                    if d < min_dist[i]:
                        min_dist[i] = d

        return total_cost

    def heuristic(self, state: GameState):
        """
        Heuristic tối ưu Admissible và Consistent cho bài toán nhiều mục tiêu:
        h(state) = min_dist(Pacman, food) + MST_cost(remaining_foods) + min_dist(food, Goal)
        """
        if self.heuristic_fn is not None:
            return self.heuristic_fn(state)
        if self.reached_target(state):
            return 0

        pm_r, pm_c = state.pacman_position

        if len(state.food) == 0:
            if self.goal is not None:
                gr, gc = self.goal
                return abs(pm_r - gr) + abs(pm_c - gc)
            return 0

        min_dist_to_food = min(abs(pm_r - fr) + abs(pm_c - fc) for fr, fc in state.food)

        food_key = frozenset(state.food)
        if food_key not in self._mst_cache:
            self._mst_cache[food_key] = self._compute_mst_cost(list(state.food))
        mst_cost = self._mst_cache[food_key]

        total_h = min_dist_to_food + mst_cost

        if self.goal is not None:
            gr, gc = self.goal
            min_food_to_goal = min(abs(fr - gr) + abs(fc - gc) for fr, fc in state.food)
            total_h += min_food_to_goal

        return total_h
