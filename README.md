# DỰ ÁN 1 — PACMAN: TÌM KIẾM VÀ TRÒ CHƠI ĐỐI KHÁNG
**Học phần:** Biểu diễn tri thức và tìm kiếm nâng cao (UET.AI2014)  
**Nhóm thực hiện:** Nhóm 07  

---

## 1. Danh Sách Thành Viên (Nhóm 07)
| STT | Họ và Tên | Mã Sinh Viên | Vai trò / Phân công |
|---|---|---|---|
| 1 | [Họ Tên Thành Viên 1] | [MSV 1] | Nhóm trưởng, Thiết kế kiến trúc & Classic Search (DFS, BFS, UCS, Greedy, A*) |
| 2 | [Họ Tên Thành Viên 2] | [MSV 2] | Multi-Goal Search & Heuristic MST (Phần mở rộng 1) |
| 3 | [Họ Tên Thành Viên 3] | [MSV 3] | Adversarial Search (Minimax, Alpha-Beta) & Cải tiến Eval Function (Phần mở rộng 2) |
| 4 | [Họ Tên Thành Viên 4] | [MSV 4] | Giao diện đồ họa Pygame Vintage Arcade, Benchmark & Kiểm thử (Unit Tests) |

---

## 2. Yêu Cầu Môi Trường & Cài Đặt
- **Phiên bản Python:** Python 3.10 trở lên (khuyến nghị Python 3.11, 3.12 hoặc 3.13).
- **Hệ điều hành:** Đã kiểm thử hoạt động ổn định trên Windows 10/11, macOS và Linux.
- **Cài đặt thư viện:**
  ```bash
  pip install -r requirements.txt
  ```
  *(Các thư viện chính bao gồm: `pygame>=2.6.0` cho giao diện đồ họa, `reportlab>=4.0.0` xuất báo cáo).*

---

## 3. Cấu Trúc Mã Nguồn
```text
P1_Nhom07/
├── src/                                  # Mã nguồn logic & thuật toán AI
│   ├── pacman/
│   │   └── game_state.py                 # Biểu diễn trạng thái GameState
│   ├── ghost/
│   │   └── ghost.py                      # Logic tác tử Ghost
│   ├── search/                           # Thuật toán tìm kiếm kinh điển (Mục 3.2, 3.3, 3.4)
│   │   ├── pm_search_problem.py          # Bài toán tìm đường đơn mục tiêu
│   │   ├── multi_goal_search.py          # Bài toán gom nhiều thức ăn / Multi-Goal (MST)
│   │   ├── dfs.py                        # Depth-First Search
│   │   ├── bfs.py                        # Breadth-First Search
│   │   ├── ucs.py                        # Uniform-Cost Search
│   │   ├── greedy.py                     # Greedy Best-First Search
│   │   └── a_star.py                     # A* Search
│   ├── logic_pacman_vs_ghost/            # Tìm kiếm đối kháng (Mục 3.5)
│   │   ├── adv_problem.py                # Bài toán đối kháng & Hàm đánh giá Evaluation
│   │   ├── minimax.py                    # Minimax có giới hạn độ sâu
│   │   └── alpha_beta.py                 # Alpha–Beta Pruning
│   └── utils/
│       ├── map_loader.py                 # Tải và tiền xử lý ma trận bản đồ
│       ├── map_info.py                   # Trích xuất vị trí P, G, @, .
│       ├── map_check_valid.py            # Kiểm định tính hợp lệ của bản đồ
│       └── benchmark.py                  # Kịch bản tự động chạy thực nghiệm (Mục 5)
├── ui/                                   # Giao diện đồ họa Vintage Arcade (Pygame)
│   ├── main.py                           # Điểm kích hoạt Pygame UI
│   ├── controller.py                     # Điều phối luồng và thuật toán
│   ├── renderer.py                       # Vẽ mê cung, Pacman, ma và hiệu ứng
│   ├── components.py                     # Nút bấm, panel chỉ số
│   └── theme.py                          # Bảng màu Neon Arcade
├── maps/                                 # Tập dữ liệu bản đồ thử nghiệm
│   ├── test_map.txt                      # Bản đồ tiêu chuẩn có 2 Ghost
│   ├── large_map.txt                     # Bản đồ lớn 19x22
│   ├── multi_goal_test.txt               # Bản đồ nhiều mục tiêu (Multi-Goal)
│   ├── multi_food_and_final_goal.txt     # Bản đồ gom thức ăn và về đích
│   ├── terrain_cost_map.txt              # Bản đồ địa hình chi phí không đồng nhất (~, S)
│   ├── adversarial_small.txt             # Bản đồ đối kháng nhỏ (1 Ghost)
│   ├── adversarial_dead_end_trap.txt     # Bản đồ bẫy ngõ cụt kiểm thử né ma
│   ├── no_solution_map.txt               # Bản đồ ngõ cụt bít kín (Unreachable)
│   └── bad_map.txt                       # Bản đồ định dạng lỗi (Test validation)
├── tests/                                # Bộ 43 Unit Tests tự động
├── results/                              # Kết quả thực nghiệm (.csv, .txt)
├── main.py                               # Điểm bắt đầu chính của chương trình
├── requirements.txt                      # Thư viện phụ thuộc
└── README.md                             # Hướng dẫn chi tiết
```

---

## 4. Hướng Dẫn Khởi Động & Sử Dụng Chương Trình

Chương trình cung cấp 3 phương thức thực thi linh hoạt:

### 4.1. Chạy Menu tương tác trực quan (Interactive Terminal)
Chạy lệnh đơn giản nhất không cần tham số:
```bash
python main.py
```
Hệ thống sẽ hiển thị menu điều hướng:
1. **Chạy thuật toán trực quan trên Terminal:** Tự động quét toàn bộ bản đồ trong thư mục `maps/` hoặc cho phép nhập file map bất kỳ; chọn thuật toán tìm kiếm hoặc đối kháng; hiển thị chi tiết số bước, chi phí, số node duyệt, thời gian và bản đồ minh họa đường đi.
2. **Khởi động Giao diện Đồ họa Arcade (Pygame UI):** Trải nghiệm giao diện tương tác trực quan.
3. **Chạy toàn bộ Thực nghiệm Benchmark:** Tự động đo đạc số liệu theo Mục 5 đề bài.

---

### 4.2. Khởi động Giao diện Đồ họa (GUI Pygame)
Khởi động trực tiếp giao diện đồ họa bằng cờ `--ui`:
```bash
python main.py --ui
```
**Tính năng giao diện:**
- Chọn bản đồ linh hoạt (hỗ trợ kéo duyệt hoặc thêm bản đồ mới).
- Chọn thuật toán tìm đường: DFS, BFS, UCS, Greedy, A* (Heuristic đề xuất), A* (h=0).
- Chọn thuật toán đối kháng: Minimax, Alpha-Beta (chỉnh được độ sâu depth 1–5).
- Các nút điều khiển: **Start**, **Pause**, **Step** (chạy từng bước để phân tích), **Reset**, **Tăng/Giảm tốc độ**.
- Bảng hiển thị thông số thời gian thực: Trạng thái (WIN/LOSE/RUNNING), Số bước, Chi phí đường đi, Số trạng thái mở rộng, Thời gian tính toán.

---

### 4.3. Chạy Dòng Lệnh Không Giao Diện (CLI Mode)
Dành cho người chấm hoặc tự động hóa kiểm thử mà không cần thao tác tay:

#### A. Tìm kiếm kinh điển (Classic Search):
```bash
# A* Search trên bản đồ chuẩn
python main.py --map maps/test_map.txt --algo ASTAR

# A* Search với h=0 (Baseline đối chứng với UCS theo Mục 5.2)
python main.py --map maps/test_map.txt --algo ASTAR_H0

# Uniform-Cost Search (UCS)
python main.py --map maps/test_map.txt --algo UCS

# Breadth-First Search (BFS)
python main.py --map maps/test_map.txt --algo BFS

# Depth-First Search (DFS)
python main.py --map maps/test_map.txt --algo DFS

# Greedy Best-First Search
python main.py --map maps/test_map.txt --algo GREEDY

# Kiểm tra bản đồ không có lời giải (Unreachable)
python main.py --map maps/no_solution_map.txt --algo ASTAR

# Kiểm tra bản đồ chi phí địa hình không đồng nhất (~, S)
python main.py --map maps/terrain_cost_map.txt --algo UCS
```

#### B. Tìm kiếm đối kháng (Adversarial Search):
Hỗ trợ 2 chế độ:
- `--mode step`: Ra quyết định tối ưu ở bước đầu tiên (đo độ sâu, node xét, điểm eval, thời gian theo Mục 4).
- `--mode match`: Mô phỏng toàn bộ trận đấu Pacman vs Ghost từng bước cho đến khi Thắng/Thua.

```bash
# Minimax ở độ sâu 2 (Step mode)
python main.py --map maps/adversarial_small.txt --algo MINIMAX --depth 2 --mode step

# Alpha-Beta Pruning ở độ sâu 2 (Step mode)
python main.py --map maps/adversarial_small.txt --algo ALPHABETA --depth 2 --mode step

# Alpha-Beta Pruning ở độ sâu 3 trên bản đồ 2 Ghost
python main.py --map maps/test_map.txt --algo ALPHABETA --depth 3 --mode step

# Mô phỏng cả trận đấu Pacman đối đầu Ghost
python main.py --map maps/adversarial_small.txt --algo ALPHABETA --depth 2 --mode match
```

---

## 5. Tái Tạo Kết Quả Thực Nghiệm (Mục 5 Đề Bài)
Để tái tạo toàn bộ số liệu thực nghiệm theo yêu cầu của Đề bài:
```bash
python main.py --benchmark
# hoặc
python src/utils/benchmark.py
```
Lệnh trên sẽ tự động chạy 3 phần thực nghiệm bắt buộc:
1. **Mục 5.1:** So sánh DFS, BFS, UCS, Greedy, A* trên 6 dạng bản đồ (nhỏ, lớn, nhiều vật cản, ngõ cụt, không lời giải, chi phí không đồng nhất).
2. **Mục 5.2:** Đánh giá Heuristic: So sánh UCS, A*(h=0) và A*(h đề xuất - MST/Manhattan), chứng minh tính tương đương UCS $\equiv$ A*(h=0) và độ cắt giảm node vượt trội của Heuristic đề xuất (giảm từ 10.3% đến 79.2% số node).
3. **Mục 5.3:** Đánh giá Tìm kiếm đối kháng: So sánh Minimax và Alpha-Beta tại các mức độ sâu 1, 2, 3 trên 4 bản đồ khác nhau. Chứng minh tính tương đương về nước đi và điểm đánh giá (`MATCH`), cùng hiệu quả tỉ lệ cắt tỉa của Alpha-Beta lên đến **82%** số trạng thái.

Kết quả được tự động lưu ra các file:
- `results/search_benchmark.csv` & `results/search_benchmark.txt`
- `results/heuristic_evaluation.txt`
- `results/adversarial_benchmark.csv` & `results/adversarial_benchmark.txt`

---

## 6. Chạy Kiểm Thử (Unit Tests)
Dự án được xây dựng với bộ 43 bài test tự động bao quát toàn bộ chức năng:
```bash
python -m unittest discover tests
```
Tất cả 43 test đều vượt qua (`OK`).

---

## 7. Các Phần Mở Rộng Của Nhóm (Mục 3.7)
Nhóm 07 đã lựa chọn và cài đặt hoàn chỉnh **2 nội dung mở rộng thuật toán**:
1. **Heuristic Cây khung nhỏ nhất (Prim MST) cho bài toán gom nhiều mục tiêu (Multi-Goal Search):**
   - Đảm bảo tính **Admissible** và **Consistent**.
   - Giúp A* giảm tới **79.2%** số node mở rộng so với UCS / A*(h=0).
2. **Cải tiến Hàm đánh giá (Evaluation Function) trong Tìm kiếm đối kháng:**
   - Bộ nhớ đệm khoảng cách mê cung BFS O(1) (`_MAZE_DIST_CACHE`).
   - Nhận diện và phạt nặng nguy cơ rẽ vào bẫy ngõ cụt cụt đầu khi có Ghost bám đuổi.
   - Phân loại Ghost chặn đầu mục tiêu và Ghost truy kích sau lưng.

---

## 8. Trả Lời Về Cơ Chế Thức Ăn Đặc Biệt (Capsule) & Đề Bài
- **Cơ chế capsule (ăn thức ăn đặc biệt để ma hóa xanh và Pacman quay lại ăn ma):**  
  Theo **Mục 1 & Mục 2** của Đề bài, đề bài nêu rõ:  
  > *"Không yêu cầu tái tạo đầy đủ trò chơi Pacman nguyên bản. Nhóm có thể bổ sung trọng số di chuyển, capsule, nhiều loại Ghost... nhưng các phần mở rộng không được làm thay đổi yêu cầu cốt lõi."*  
  Do đó, việc ăn thức ăn đặc biệt để săn lại ma **hoàn toàn KHÔNG BẮT BUỘC**. Yêu cầu đối kháng cốt lõi là giải quyết bài toán Minimax, Alpha-Beta Pruning với giới hạn độ sâu và hàm đánh giá trạng thái né ma - ăn mục tiêu, đã được nhóm cài đặt hoàn chỉnh và chính xác.
