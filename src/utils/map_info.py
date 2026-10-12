def get_map_info(game_map, return_foods=False):
    """
    Trích xuất thông tin bản đồ:
    - spawn: vị trí Pacman (P)
    - goals: danh sách tọa độ Goal (G)
    - ghosts: danh sách tọa độ Ghost (@)
    - foods: danh sách tọa độ Food (.)

    Nếu return_foods=True: trả về (spawn, goals, ghosts, foods)
    Nếu return_foods=False: trả về (spawn, goals, ghosts) để tương thích ngược.
    Đặc biệt: nếu map chỉ có '.' mà không có 'G', và return_foods=False,
    thì tự động coi các điểm '.' là goals để các thuật toán cũ không bị thiếu đích.
    """
    spawn = None
    goals = []
    ghosts = []
    foods = []
    for i in range(len(game_map)):
        for j in range(len(game_map[i])):
            char = game_map[i][j]
            if char == "P":
                spawn = (i, j)
            elif char == "G":
                goals.append((i, j))
            elif char == "@":
                ghosts.append((i, j))
            elif char == ".":
                foods.append((i, j))

    if return_foods:
        return spawn, goals, ghosts, foods

    # Nếu không yêu cầu tách foods riêng và map không có G nhưng có .
    if len(goals) == 0 and len(foods) > 0:
        return spawn, foods, ghosts

    return spawn, goals, ghosts

        