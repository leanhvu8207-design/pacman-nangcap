from src.utils.map_check_valid import check_map
def load_map(file_path):
    try:
        with open(file_path, "r") as file:
            game_map = [line.rstrip("\n") for line in file]
            
        if check_map(game_map) == False:
            return None
        return game_map
    
    except FileNotFoundError:
        print(" *** Không tìm thấy file chứa map *** ")
        return None