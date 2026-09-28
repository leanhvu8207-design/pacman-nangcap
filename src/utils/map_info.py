def get_map_info(game_map):
    spawn = None
    goals = []
    ghosts = []
    for i in range(len(game_map)):
        for j in range(len(game_map[i])):
            if game_map[i][j] == "P":
                spawn = (i,j) 
            
            if game_map[i][j] == "G":
                goals.append((i,j))
                
            if game_map[i][j] == "@":
                ghosts.append((i,j))
    return spawn, goals, ghosts
        