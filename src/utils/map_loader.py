import logging
from src.utils.map_check_valid import check_map

logger = logging.getLogger(__name__)

def load_map(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            raw_lines = []
            for line in file:
                raw_lines.append(line.rstrip("\r\n"))

        
        while len(raw_lines) > 0 and raw_lines[-1].strip() == "":
            raw_lines.pop()

        game_map = raw_lines

        if check_map(game_map) == False:
            logger.warning("Bản đồ không hợp lệ: %s", file_path)
            return None
        return game_map

    except FileNotFoundError:
        logger.error("Không tìm thấy file chứa map: %s", file_path)
        print(" *** Khong tim thay file chua map: " + str(file_path) + " *** ")
        return None