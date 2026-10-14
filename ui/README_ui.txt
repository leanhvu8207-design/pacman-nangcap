====================================================================
           HỆ THỐNG GIAO DIỆN VINTAGE ARCADE - PACMAN AI SEARCH
                          NHÓM 07 - UET
====================================================================

1. TỔNG QUAN
Folder `ui/` chứa toàn bộ mã nguồn giao diện phong cách Vintage Arcade
thập niên 80-90 cho đồ án Pacman AI Search.
- Thiết kế Retro Arcade: Màn hình Bezel, bảng điều khiển arcade cabinet.
- Nhân vật: Pacman vàng cổ điển há miệng, Ghost đa sắc màu (không có màu vàng),
  thức ăn màu kem, điểm đích Goal xanh mint.
- Tương tác chuột 100%: Click chọn map, chọn thuật toán, điều chỉnh depth,
  bắt đầu, tạm dừng, đi từng bước, reset, cuộn nhật ký.

2. CẤU TRÚC MODULE
- `ui/theme.py`: Bảng màu retro, quản lý font chữ monospaced, hàm vẽ bevel.
- `ui/components.py`: Thư viện nút bấm, tab, bộ chọn số, bộ chọn map, log box.
- `ui/renderer.py`: Render mê cung, food, goal, vẽ vector Pacman & Ghost.
- `ui/controller.py`: Điều phối thuật toán backend và luồng chạy không nghẽn UI.
- `ui/main.py`: Vòng lặp Pygame, đón sự kiện chuột và phím, render toàn bộ UI.

3. HƯỚNG DẪN KHỞI CHẠY
- Chạy qua cờ --ui từ main:
    python main.py --ui
- Hoặc chạy trực tiếp module ui:
    python -m ui.main

4. PHÍM TẮT HỖ TRỢ
- [Enter] : Bắt đầu chạy (Start)
- [Space] : Tạm dừng / Tiếp tục (Pause / Resume)
- [S]     : Đi duy nhất 1 bước (Step)
- [R]     : Đặt lại trạng thái ban đầu (Reset)
- [Esc]   : Thoát ứng dụng
- Cuộn chuột: Xem lịch sử nhật ký hoạt động
====================================================================
