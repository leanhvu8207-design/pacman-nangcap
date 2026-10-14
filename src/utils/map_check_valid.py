"""Kiểm tra tính hợp lệ của bản đồ Pacman (kích thước, ký tự, số lượng Pacman/Goal)."""


def check_map(game_map):
    if game_map is None:
        return False
    if len(game_map) == 0:
        return False

    first_line_width = len(game_map[0])
    if first_line_width == 0:
        return False

    for row_index in range(len(game_map)):
        current_line = game_map[row_index]
        current_line_width = len(current_line)
        if current_line_width != first_line_width:
            return False

    allowed_characters = set('#.PG@ ~S')
    pacman_count = 0
    target_count = 0

    for row_index in range(len(game_map)):
        current_line = game_map[row_index]
        for col_index in range(len(current_line)):
            char = current_line[col_index]
            if char not in allowed_characters:
                return False

            if char == 'P':
                pacman_count = pacman_count + 1
            elif char == 'G':
                target_count = target_count + 1
            elif char == '.':
                target_count = target_count + 1

    has_exact_one_pacman = (pacman_count == 1)
    has_at_least_one_target = (target_count >= 1)

    if has_exact_one_pacman and has_at_least_one_target:
        return True
    else:
        return False
