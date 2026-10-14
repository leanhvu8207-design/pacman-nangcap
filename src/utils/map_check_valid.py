def check_map(game_map):
    """
    Kiểm tra tính hợp lệ của bản đồ:
    - Không rỗng và có cấu trúc hình chữ nhật đồng nhất.
    - Ký tự hợp lệ: # (Tường), . (Food), P (Pacman), G (Goal), @ (Ghost), khoảng trắng.
    - Đúng 1 Pacman và ít nhất 1 mục tiêu (Goal hoặc Food).
    """
    if not game_map:
        return False

    width = len(game_map[0])
    for line in game_map:
        if len(line) != width:
            return False

    allowed_char = set("#.PG@ ~S")
    p_count = 0
    target_count = 0

    for line in game_map:
        for char in line:
            if char not in allowed_char:
                return False
            if char == "P":
                p_count += 1
            elif char in ("G", "."):
                target_count += 1

    return p_count == 1 and target_count >= 1
