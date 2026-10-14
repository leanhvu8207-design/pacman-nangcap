"""Bài toán thu thập nhiều thức ăn kết hợp cây khung nhỏ nhất (MST)."""

from src.pacman.game_state import GameState


class MultiGoal:
    def __init__(self, spawn, food, game_map, goal=None, cost_fn=None, heuristic_fn=None):
        self.pacman_spawn = spawn
        self.food = list(food)
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
            initial_score = initial_score + 10

        ghost_positions = []
        initial_state = GameState(self.pacman_spawn, ghost_positions, initial_food, initial_score, self.game_map)
        return initial_state

    def reached_target(self, state: GameState):
        if len(state.food) > 0:
            return False

        if self.goal is not None:
            is_at_final_goal = (state.pacman_position == self.goal)
            return is_at_final_goal

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

    def _compute_mst_cost(self, foods):
        num_foods = len(foods)
        if num_foods <= 1:
            return 0
        if num_foods == 2:
            r1 = foods[0][0]
            c1 = foods[0][1]
            r2 = foods[1][0]
            c2 = foods[1][1]
            return abs(r1 - r2) + abs(c1 - c2)

        in_tree = [False] * num_foods
        in_tree[0] = True
        min_dist = []
        root_r = foods[0][0]
        root_c = foods[0][1]

        for i in range(num_foods):
            target_r = foods[i][0]
            target_c = foods[i][1]
            distance = abs(root_r - target_r) + abs(root_c - target_c)
            min_dist.append(distance)

        total_mst_cost = 0

        for _ in range(num_foods - 1):
            best_index = -1
            best_distance = float('inf')

            for i in range(num_foods):
                if not in_tree[i]:
                    if min_dist[i] < best_distance:
                        best_distance = min_dist[i]
                        best_index = i

            if best_index == -1:
                break

            in_tree[best_index] = True
            total_mst_cost = total_mst_cost + best_distance

            new_node_r = foods[best_index][0]
            new_node_c = foods[best_index][1]

            for i in range(num_foods):
                if not in_tree[i]:
                    curr_r = foods[i][0]
                    curr_c = foods[i][1]
                    dist_to_new_node = abs(new_node_r - curr_r) + abs(new_node_c - curr_c)
                    if dist_to_new_node < min_dist[i]:
                        min_dist[i] = dist_to_new_node

        return total_mst_cost

    def heuristic(self, state: GameState):
        if self.heuristic_fn is not None:
            return self.heuristic_fn(state)

        if self.reached_target(state):
            return 0

        pacman_r = state.pacman_position[0]
        pacman_c = state.pacman_position[1]

        if len(state.food) == 0:
            if self.goal is not None:
                goal_r = self.goal[0]
                goal_c = self.goal[1]
                return abs(pacman_r - goal_r) + abs(pacman_c - goal_c)
            return 0

        min_dist_to_food = float('inf')
        for food_pos in state.food:
            food_r = food_pos[0]
            food_c = food_pos[1]
            dist = abs(pacman_r - food_r) + abs(pacman_c - food_c)
            if dist < min_dist_to_food:
                min_dist_to_food = dist

        food_key = frozenset(state.food)
        if food_key not in self._mst_cache:
            food_list = list(state.food)
            computed_mst = self._compute_mst_cost(food_list)
            self._mst_cache[food_key] = computed_mst

        mst_cost = self._mst_cache[food_key]
        total_h = min_dist_to_food + mst_cost

        if self.goal is not None:
            goal_r = self.goal[0]
            goal_c = self.goal[1]
            min_food_to_goal = float('inf')

            for food_pos in state.food:
                food_r = food_pos[0]
                food_c = food_pos[1]
                dist_to_goal = abs(food_r - goal_r) + abs(food_c - goal_c)
                if dist_to_goal < min_food_to_goal:
                    min_food_to_goal = dist_to_goal

            total_h = total_h + min_food_to_goal

        return total_h
