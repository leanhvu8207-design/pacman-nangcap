"""Hàm đọc bản đồ mê cung từ file text và kiểm tra tính hợp lệ."""

import logging
from src.utils.map_check_valid import check_map

logger = logging.getLogger(__name__)


def load_map(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file_handle:
            raw_lines = []
            for line_content in file_handle:
                cleaned_line = line_content.rstrip('\r\n')
                raw_lines.append(cleaned_line)

        while len(raw_lines) > 0:
            last_line = raw_lines[-1]
            if last_line.strip() == '':
                raw_lines.pop()
            else:
                break

        game_map = raw_lines
        is_map_valid = check_map(game_map)

        if not is_map_valid:
            logger.warning('Bản đồ không hợp lệ: %s', file_path)
            return None

        return game_map

    except FileNotFoundError:
        logger.error('Không tìm thấy file chứa map: %s', file_path)
        print(' *** Khong tim thay file chua map: ' + str(file_path) + ' *** ')
        return None
