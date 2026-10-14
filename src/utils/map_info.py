"""Trích xuất tọa độ Pacman, Goal, Ghost và Food từ ma trận bản đồ."""


def get_map_info(game_map, return_foods=False):
    spawn_position = None
    goal_positions = []
    ghost_positions = []
    food_positions = []

    total_rows = len(game_map)

    for row_idx in range(total_rows):
        current_row = game_map[row_idx]
        total_cols = len(current_row)

        for col_idx in range(total_cols):
            char = current_row[col_idx]
            current_coordinate = (row_idx, col_idx)

            if char == 'P':
                spawn_position = current_coordinate
            elif char == 'G':
                goal_positions.append(current_coordinate)
            elif char == '@':
                ghost_positions.append(current_coordinate)
            elif char == '.':
                food_positions.append(current_coordinate)

    if return_foods:
        return (spawn_position, goal_positions, ghost_positions, food_positions)

    if len(goal_positions) == 0 and len(food_positions) > 0:
        return (spawn_position, food_positions, ghost_positions)

    return (spawn_position, goal_positions, ghost_positions)
