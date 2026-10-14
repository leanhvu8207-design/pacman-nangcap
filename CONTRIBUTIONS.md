# BẢNG PHÂN CÔNG CÔNG VIỆC VÀ ĐÓNG GÓP THÀNH VIÊN
**Dự án 1 — Pacman: Tìm kiếm và trò chơi đối kháng**  
**Học phần:** Biểu diễn tri thức và tìm kiếm nâng cao (UET.AI2014)  
**Nhóm:** Nhóm 07  

---

## 1. Bảng Phân Công Công Việc

| STT | Thành viên | Mã SV | Nhiệm vụ đảm nhiệm | Tỉ lệ đóng góp |
|:---:|:---|:---:|:---|:---:|
| 1 | [Họ Tên Thành Viên 1] | [MSV 1] | - Kiến trúc hệ thống, nạp và kiểm tra tính hợp lệ của bản đồ (`src/utils`).<br>- Cài đặt bài toán tìm kiếm cơ sở (`PMSearchProblem`, `GameState`).<br>- Cài đặt và tối ưu các thuật toán Classic Search: DFS, BFS, UCS, Greedy Best-First, A* Search.<br>- Biên soạn báo cáo phần 1, 2, 4. | 25% |
| 2 | [Họ Tên Thành Viên 2] | [MSV 2] | - Cài đặt bài toán gom nhiều thức ăn / mục tiêu (`MultiGoal`).<br>- **Phần mở rộng 1:** Thiết kế và chứng minh Heuristic MST (Prim Cây khung nhỏ nhất) cho bài toán Multi-Goal Search.<br>- Thực nghiệm đánh giá Heuristic (UCS vs A*(h=0) vs A*(h)).<br>- Biên soạn báo cáo phần 3, 5. | 25% |
| 3 | [Họ Tên Thành Viên 3] | [MSV 3] | - Cài đặt bài toán tìm kiếm đối kháng (`AdvProblem`, `Ghost`).<br>- Cài đặt thuật toán Minimax và Alpha–Beta Pruning có giới hạn độ sâu.<br>- **Phần mở rộng 2:** Cải tiến hàm đánh giá (`evaluation function`) với cơ chế né bẫy ngõ cụt, phân loại ma và bộ đệm khoảng cách BFS O(1).<br>- Biên soạn báo cáo phần 6, 8. | 25% |
| 4 | [Họ Tên Thành Viên 4] | [MSV 4] | - Thiết kế và xây dựng giao diện đồ họa Vintage Arcade Neon bằng Pygame (`ui/`).<br>- Xây dựng kịch bản chạy thực nghiệm tự động (`benchmark.py`) và xuất file kết quả csv, txt (`results/`).<br>- Xây dựng bộ kiểm thử tự động 43 Unit Tests (`tests/`).<br>- Hoàn thiện `main.py`, `README.md` và biên soạn báo cáo phần 7, 9, 10, 11. | 25% |

---

## 2. Khai Báo Sử Dụng Công Cụ Trợ Giúp (AI Disclosure)
Tuân thủ quy định tại Mục 9 của đề bài về Liêm chính học thuật và sử dụng AI:
- **Công cụ hỗ trợ:** Claude 3.5 Sonnet / ChatGPT.
- **Mục đích sử dụng:**
  - Hỗ trợ rà soát cú pháp, gợi ý cấu trúc boilerplate cho các file test (`unittest`).
  - Hỗ trợ tối ưu hóa cấu trúc hiển thị bảng số liệu CLI và format báo cáo Markdown.
  - Hỗ trợ tra cứu tham khảo thuật toán Prim MST và giải thuật cắt tỉa Alpha-Beta lý thuyết.
- **Cam kết:**
  - Toàn bộ logic cốt lõi của Pacman, không gian trạng thái, thiết kế hàm heuristic, thuật toán đối kháng và giao diện Pygame do các thành viên nhóm tự nghiên cứu, làm chủ 100% và sẵn sàng trả lời vấn đáp chi tiết trước hội đồng chấm thi.
