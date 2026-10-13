# DỰ ÁN 1 — PACMAN: TÌM KIẾM VÀ TRÒ CHƠI ĐỐI KHÁNG
**Học phần:** Biểu diễn tri thức và tìm kiếm nâng cao (UET.AI2014)  
**Đơn vị:** Trường Đại học Công nghệ – Đại học Quốc gia Hà Nội (VNU-UET)  
**Nhóm thực hiện:** Nhóm 07  

---

## 1. Danh sách thành viên nhóm

| STT | Họ và tên | Mã sinh viên | Email | Vai trò chính trong dự án | Tỷ lệ đóng góp |
| :---: | :--- | :---: | :--- | :--- | :---: |
| 1 | **Vũ Thanh Thanh Tùng** | *(Trưởng nhóm)* | vuthanhthanhtung16112007@gmail.com | Kiến trúc hệ thống, Tìm kiếm đối kháng (Minimax, Alpha-Beta), Giao diện Pygame Retro Arcade | 100% |
| 2 | **Bùi Chí Thành** | 25023046 | chithanhbui100@gmail.com | Thuật toán tìm kiếm có thông tin & Heuristic MST cho Multi-Goal (A*, Greedy, MultiGoal) | 100% |
| 3 | **Lê Anh Vũ** | *(Thành viên)* | leanhvu8207@gmail.com | Thuật toán tìm kiếm không thông tin (DFS, BFS, UCS), Tầng tiền xử lý bản đồ & Game State | 100% |
| 4 | **Thành viên Nhóm 07** | *(Thành viên)* | uet.nhom07@vnu.edu.vn | Xây dựng bộ ca kiểm thử tự động (Unit Tests), Thực nghiệm Benchmark & Biên soạn báo cáo | 100% |

---

## 2. Môi trường và Yêu cầu hệ thống

- **Ngôn ngữ:** Python 3.10 – 3.13 (đã kiểm thử và chạy ổn định trên Python 3.13.x và 3.10.x).
- **Hệ điều hành:** Độc lập nền tảng — Hoạt động mượt mà trên **Windows 10/11**, **Ubuntu / Linux**, và **macOS**.
- **Thư viện phụ thuộc:**
  - `pygame >= 2.5.0` (phục vụ giao diện đồ họa Vintage Arcade tương tác).
  - Không sử dụng thêm bất kỳ thư viện bên ngoài phức tạp nào khác; các cấu trúc dữ liệu cốt lõi sử dụng thư viện chuẩn của Python (`heapq`, `collections.deque`, `threading`, `time`, `argparse`).

---

## 3. Hướng dẫn cài đặt

Khuyến nghị khởi tạo và sử dụng môi trường ảo Python (Virtual Environment):

```bash
# 1. Tạo môi trường ảo (tùy chọn)
python -m venv .venv

# Kích hoạt trên Windows:
.venv\Scripts\activate
# Kích hoạt trên Linux/macOS:
source .venv/bin/activate

# 2. Cài đặt các thư viện yêu cầu
pip install -r requirements.txt
```

---

## 4. Cấu trúc thư mục chương trình

```text
P1_Nhom07/
├── src/                            # Mã nguồn logic cốt lõi và thuật toán AI
│   ├── ghost/                      # Trí tuệ nhân tạo của tác tử Ma
│   │   └── ghost.py                # Thuật toán né ma, BFS truy đuổi và cự ly
│   ├── logic_ghost/                # Thuật toán đối kháng Pacman vs Ghost
│   │   ├── adv_problem.py          # Không gian đối kháng AdvProblem & Hàm đánh giá evaluate()
│   │   ├── minimax.py              # Thuật toán Minimax giới hạn độ sâu
│   │   └── alpha_beta.py           # Thuật toán Alpha-Beta Pruning cắt tỉa
│   ├── pacman/                     # Mô hình trạng thái Game
│   │   └── game_state.py           # Trạng thái bất biến GameState, chuyển trạng thái & va chạm
│   ├── search/                     # Các thuật toán tìm đường (Path Planning)
│   │   ├── pm_search_problem.py    # Không gian tìm kiếm đơn mục tiêu PMSearchProblem & Manhattan
│   │   ├── multi_goal_search.py    # Bài toán nhiều mục tiêu MultiGoal & Heuristic Prim MST
│   │   ├── dfs.py                  # Depth-First Search
│   │   ├── bfs.py                  # Breadth-First Search
│   │   ├── ucs.py                  # Uniform-Cost Search
│   │   ├── greedy.py               # Greedy Best-First Search
│   │   └── a_star.py               # A* Search
│   └── utils/                      # Công cụ phụ trợ và đo lường
│       ├── map_check_valid.py      # Kiểm tra tính toàn vẹn cú pháp bản đồ
│       ├── map_loader.py           # Đọc và chuẩn hóa bản đồ từ file .txt
│       ├── map_info.py             # Trích xuất vị trí Pacman, Goal, Ghost, Food
│       └── benchmark.py            # Script thực nghiệm tự động xuất kết quả
├── ui/                             # Giao diện đồ họa Vintage Arcade (Pygame)
│   ├── components.py               # Các widget: Button, ButtonGroup, Stepper, LogBox
│   ├── controller.py               # Bộ điều khiển trung tâm GameController & Đa luồng (Threading)
│   ├── main.py                     # Cửa sổ chính của UI đồ họa
│   ├── map_browser.py              # Modal duyệt và xem trước toàn cảnh bản đồ
│   ├── renderer.py                 # Bộ vẽ mê cung phong cách Neon CRT Vintage
│   └── theme.py                    # Bảng màu hoài cổ và hệ thống font chữ
├── assets/                         # Tài nguyên âm thanh/hình ảnh bổ trợ (nếu có)
├── maps/                           # Thư mục chứa 22 bản đồ kiểm nghiệm đa dạng
│   ├── classic_pacman_arcade.txt   # Bản đồ Pacman truyền thống kinh điển chuẩn 1980
│   ├── adversarial_*.txt           # Các bản đồ kịch bản đối kháng
│   ├── single_goal_*.txt           # Các bản đồ 1 mục tiêu
│   ├── multi_*.txt                 # Các bản đồ nhiều mục tiêu
│   └── no_solution_map.txt         # Bản đồ không có lời giải
├── tests/                          # Bộ 35 ca kiểm thử tự động (Unit Tests)
│   ├── test_search_classic.py      # Test 5 thuật toán tìm kiếm cổ điển
│   ├── test_adversarial.py         # Test tính tương đương Minimax vs Alpha-Beta
│   ├── test_extension.py          # Test phần mở rộng: Heuristic MST & Cải tiến Evaluation
│   ├── test_map_loader.py          # Test nạp bản đồ và xử lý lỗi
│   └── test_ui.py                  # Test tích hợp bộ điều khiển giao diện
├── results/                        # Kết quả thực nghiệm đo đạc (CSV và TXT)
│   ├── search_benchmark.txt/.csv   # Bảng số liệu tìm kiếm đơn tác tử
│   ├── adversarial_benchmark.*     # Bảng số liệu đối kháng và tỷ lệ cắt tỉa
│   └── heuristic_evaluation.txt    # Bảng đánh giá Heuristic MST vs UCS / A*(h=0)
├── main.py                         # Điểm vào chính của toàn bộ chương trình
├── requirements.txt                # Danh sách thư viện cần thiết
├── README.md                       # Tài liệu hướng dẫn sử dụng chi tiết
├── CONTRIBUTIONS.md                # Báo cáo phân công công việc & Liêm chính học thuật
└── report.pdf                      # Báo cáo kỹ thuật chi tiết của đồ án (25% điểm)
```

---

## 5. Hướng dẫn khởi động và sử dụng

### 5.1. Chạy Giao diện Đồ họa Tương tác (GUI - Pygame Arcade)

Khởi động giao diện người dùng tương tác hoàn chỉnh:

```bash
python main.py --ui
```
*(hoặc chạy trực tiếp: `python -m ui.main`)*

**Tính năng nổi bật trên giao diện:**
- **Thao tác chuột 100%:** Chọn bản đồ từ danh sách dropdown hoặc bấm vào nút **[MAPS]** để mở Modal duyệt toàn cảnh bản đồ với Mini-map preview.
- **Lựa chọn thuật toán trực quan:**
  - Hàng cổ điển: `DFS`, `BFS`, `UCS`, `GREEDY`, `A*`.
  - Hàng đối kháng: `MINIMAX`, `ALPHA-BETA`.
- **Điều khiển thời gian thực:**
  - Nút **▶ START**: Bắt đầu thực thi thuật toán.
  - Nút **⏸ PAUSE / ▶ RESUME**: Tạm dừng hoặc tiếp tục mô phỏng.
  - Nút **⏭ STEP**: Cho phép thực thi từng bước một để quan sát kỹ thuật toán ra quyết định.
  - Nút **↺ RESET**: Khôi phục lại trạng thái ban đầu của bàn cờ.
- **Tốc độ mô phỏng:** Tùy chỉnh 5 mức tốc độ: `0.5x`, `1.0x`, `2.0x`, `4.0x`, `Max`.
- **Bảng chỉ số AI (Metrics):** Cập nhật dữ liệu thực thời gian thực: *Số node đã mở rộng, Thời gian chạy, Điểm đánh giá (Eval), Số bước, Chi phí đường đi, Điểm số*.
- **Nhật ký hoạt động (Log Box):** Cuộn xem lịch sử từng bước đi và hành động của Pacman và các Ghost.
- **Phím tắt nhanh:**
  - `Enter`: Bắt đầu (Start).
  - `Space`: Tạm dừng / Tiếp tục (Pause/Resume).
  - `S`: Chạy 1 bước (Step).
  - `R`: Khởi động lại (Reset).
  - `M`: Mở modal xem trước bản đồ.
  - `Esc`: Thoát chương trình.

---

### 5.2. Chạy trên Console Dòng Lệnh Tương tác (CLI Interactive)

Nếu không cài đặt thư viện đồ họa hoặc muốn chạy nhanh trên terminal:

```bash
python main.py
```
Hệ thống sẽ hiển thị menu tương tác bằng số:
1. Chọn bản đồ từ danh sách (bao gồm bản đồ Pacman truyền thống, bản đồ nhỏ, lớn, đối kháng, ngõ cụt...).
2. Chọn thuật toán mong muốn (1-7).
3. Nếu chọn đối kháng: Nhập độ sâu tìm kiếm `depth` (mặc định: 2 hoặc 3) và chọn chế độ:
   - Chế độ 1: Tính nước đi tối ưu ở bước đầu tiên.
   - Chế độ 2: Mô phỏng toàn bộ trận đấu từng bước tới khi Thắng/Thua.

---

### 5.3. Chạy trực tiếp qua tham số dòng lệnh (Non-interactive CLI)

Hỗ trợ tự động hóa, kiểm tra nhanh và tái hiện kết quả mà không cần tương tác bàn phím:

```bash
# 1. Chạy tìm đường A* trên bản đồ Pacman truyền thống:
python main.py --map maps/classic_pacman_arcade.txt --algo ASTAR

# 2. Chạy BFS trên bản đồ nhiều mục tiêu:
python main.py --map maps/multi_food_four_corners.txt --algo BFS

# 3. Chạy đối kháng Alpha-Beta độ sâu 3 (mô phỏng trận đấu):
python main.py --map maps/test_map.txt --algo ALPHABETA --depth 3 --mode match

# 4. Chạy Minimax tính nước đi đầu tiên tại độ sâu 2:
python main.py --map maps/adversarial_small.txt --algo MINIMAX --depth 2 --mode step
```

---

## 6. Hướng dẫn Chạy Kiểm thử Tự động (Unit Tests)

Dự án trang bị bộ **35 unit tests** tự động, bao phủ toàn bộ các tầng logic từ tiền xử lý, thuật toán tìm kiếm, đối kháng, giao diện đến phần mở rộng:

```bash
# Chạy toàn bộ 35 unit test:
python -m unittest discover tests

# Hoặc chạy kiểm thử riêng từng module:
python -m unittest tests/test_search_classic.py    # 10 tests tìm kiếm cổ điển
python -m unittest tests/test_adversarial.py       # 5 tests đối kháng & tương đương
python -m unittest tests/test_extension.py         # 5 tests phần mở rộng (MST & Eval)
python -m unittest tests/test_map_loader.py        # 7 tests nạp map và kiểm định lỗi
python -m unittest tests/test_ui.py                # 8 tests điều khiển giao diện
```

---

## 7. Các lệnh tái tạo kết quả thực nghiệm chính

Để tự động đo đạc, so sánh toàn bộ các thuật toán trên toàn bộ 22 bản đồ và xuất kết quả vào thư mục `results/`:

```bash
python -m src.utils.benchmark
```

Sau khi chạy xong, kết quả số liệu sẽ được tự động lưu lại vào:
1. `results/search_benchmark.txt` & `results/search_benchmark.csv`: So sánh DFS, BFS, UCS, Greedy, A* theo Số bước, Chi phí, Node mở rộng và Thời gian chạy.
2. `results/heuristic_evaluation.txt`: So sánh UCS vs A*(h=0) vs A* Heuristic đề xuất (Manhattan và Prim MST).
3. `results/adversarial_benchmark.txt` & `results/adversarial_benchmark.csv`: So sánh Minimax và Alpha-Beta ở các độ sâu 1, 2, 3; chứng minh tính tương đương 100% về hành động và hiệu quả cắt tỉa từ 30% đến 82%.

---

## 8. Phần mở rộng của nhóm (Mục 3.7)

Nhóm đã nghiên cứu, cài đặt và kiểm nghiệm 2 nội dung mở rộng thuật toán:

1. **Heuristic Cây khung nhỏ nhất (Prim MST) cho Bài toán Nhiều mục tiêu (`src/search/multi_goal_search.py`):**
   - Áp dụng thuật toán Prim để tính chi phí cây khung nhỏ nhất nối tất cả các viên thức ăn còn lại trong không gian trạng thái.
   - Kết hợp: $h(s) = \text{dist}(Pacman, food_{nearest}) + \text{MST}(Foods) + \text{dist}(food_{nearest}, Goal)$.
   - **Lập luận toán học:** Heuristic không âm ($h \ge 0$), $h(goal) = 0$, Admissible (bất kỳ hành trình nào đi qua hết các điểm cũng phải có chi phí $\ge$ cây khung nhỏ nhất nối các điểm đó) và Consistent.
   - **Thực nghiệm:** Giảm từ **51.2% đến 78.9%** số node mở rộng so với UCS / A*(h=0), duy trì 100% tính tối ưu của đường đi.

2. **Evaluation Function Cải tiến cho Tìm kiếm Đối kháng (`src/logic_ghost/adv_problem.py`):**
   - **Khoảng cách mê cung thực tế BFS O(1):** Sử dụng bộ nhớ đệm `_MAZE_DIST_CACHE` để tính chính xác khoảng cách giữa Pacman, Ma và Đích (có tính đến tường chắn), tránh việc dùng cự ly đường chim bay Manhattan khiến Pacman bị ngộ nhận có lối đi qua tường.
   - **Phân loại Ghost:** Phạt nặng Ghost đang ở vị trí chặn đường tới Goal; thưởng điểm nếu Ghost bám đuổi phía sau và Pacman đang dẫn trước trong cuộc đua về đích.
   - **Cơ chế Né bẫy ngõ cụt (`_count_exits`):** Pacman phát hiện các hành lang chỉ có 1 lối thoát khi Ghost ở cự ly nguy hiểm, phạt nặng điểm số để tuyệt đối không tự chui đầu vào rọ.
   - **Cơ chế Chống giằng co lặp chu kỳ (`recent_positions`):** Phạt các ô vừa đi qua nhiều lần trong các bước gần nhất, loại bỏ triệt để hiện tượng Pacman dao động qua lại giữa 2 ô trống khi bị ma uy hiếp.

---

## 9. Các giới hạn và hướng phát triển

- **Bùng nổ tổ hợp với số lượng thức ăn cực lớn:** Bài toán Multi-Goal Search tối ưu có không gian trạng thái kích thước $|V| \times 2^{|Food|}$. Khi số lượng thức ăn vượt quá 12–15 viên, việc tìm kiếm tối ưu toàn cục sẽ tiêu tốn bộ nhớ lớn. Khi đó, hệ thống tự động chuyển đổi sang chiến lược lập kế hoạch cục bộ theo tham lam viên thức ăn gần nhất (Nearest-Neighbor Tour) để đảm bảo thời gian phản hồi tức thì.
- **Độ sâu tìm kiếm đối kháng khi có nhiều hơn 3 Ghost:** Khi có nhiều tác tử Ghost cùng di chuyển, hệ số phân nhánh của cây trò chơi tăng theo cấp số nhân ($b \approx b_{pacman} \times b_{ghost_1} \times \dots \times b_{ghost_k}$). Để giữ thời gian tính toán $< 0.1$ giây/bước, độ sâu khuyến nghị trong thực tế là $depth \in [2, 3]$.

---
*Bản quyền thuộc về Nhóm 07 — UET.AI2014 — Học kỳ 1, Năm học 2026.*
