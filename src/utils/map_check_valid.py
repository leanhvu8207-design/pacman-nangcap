def check_map(game_map):
    """
    Check Map rỗng
    """
    if len(game_map)==0:
        return False
    
    """
    Check cấu trúc map hợp lệ
    """
    
    for line in game_map: 
        if len(line) != len(game_map[0]):
            return False
    
    
    """
    Check ký tự hợp lệ trong map
    # : Tường
    . : Food
    P : Pacman
    G : Goal
    @ : Ghost
    " " : Khoảng trống
    """
    allowed_char = "#.PG@ "
    for line in game_map:  
        for char in line:
            if char not in allowed_char:
                return False
            
    
    """
    Bản đồ phải có:
    - Đúng 1 Pacman (P)
    - Ít nhất 1 mục tiêu: có thể là Goal (G) hoặc Food (.) hoặc cả hai
    """
    p_count = 0
    g_count = 0
    food_count = 0
    for line in game_map:
        p_count += line.count("P")
        g_count += line.count("G")
        food_count += line.count(".")
        
    if p_count != 1:
        return False
    if g_count + food_count < 1:
        return False
    
    return True


