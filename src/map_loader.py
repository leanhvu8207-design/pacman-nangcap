def load_map(file_path):
    with open(file_path, "r") as file:
        game_map = [line.rstrip("\n") for line in file]

    return game_map