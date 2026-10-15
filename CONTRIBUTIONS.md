# BÁO CÁO PHÂN CÔNG CÔNG VIỆC VÀ ĐÓNG GÓP CỦA CÁC THÀNH VIÊN

**Dự án 1 – Pacman: Tìm kiếm và trò chơi đối kháng**  
**Môn học:** Biểu diễn tri thức và tìm kiếm nâng cao (UET.AI2014_5)  
**Đơn vị:** Trường Đại học Công nghệ – Đại học Quốc gia Hà Nội (UET-VNU)  
**Nhóm thực hiện:** Nhóm 07  

---

## 1. Danh sách thành viên

| STT |     Họ và tên       |   MSV    |   Vai trò   |
|:---:|:-------------------:|:--------:|:-----------:|
|  1  | Bùi Chí Thành       | 25023046 | Thành viên  |
|  2  | Khúc Hữu Trung      | 25023062 | Thành viên  |
|  3  | Vũ Thành Thanh Tùng | 25023040 | Thành viên  |
|  4  | Lê Anh Vũ           | 25023077 | Trưởng nhóm |

---

## 2. Phân công công việc cá nhân

### 2.1. Bùi Chí Thành
- Xây dựng cấu trúc ban đầu của dự án theo hướng đối tượng (OOP).
- Viết lớp quản lý trạng thái trò chơi trong `game_state.py` và tổ chức luồng chạy chính trong `main.py`.
- Bổ sung bài toán tìm kiếm có chi phí địa hình, trong đó ô Nước (`~`) có chi phí 2 và ô Đầm lầy (`S`) có chi phí 3.
- Tổng hợp nội dung và viết file `CONTRIBUTIONS.md`.
- **Trạng thái:** Hoàn thành.

### 2.2. Khúc Hữu Trung
- Viết lớp mô hình hóa bài toán tìm kiếm đối kháng trong `adv_problem.py`, bao gồm không gian trạng thái, cơ chế luân phiên lượt đi giữa Pacman và Ghost, sinh các nước đi hợp lệ và kiểm tra điều kiện kết thúc bằng `is_terminal`.
- Cài đặt hai thuật toán Minimax và Alpha-Beta Pruning có giới hạn độ sâu trong các file `minimax.py` và `alpha_beta.py`.
- Tổng hợp nội dung và viết báo cáo đồ án trong file `report.pdf`.
- **Trạng thái:** Hoàn thành.

### 2.3. Vũ Thành Thanh Tùng
- Viết các file `map_loader.py`, `map_info.py` và `map_check_valid.py` để đọc bản đồ, lấy thông tin về vị trí các đối tượng và kiểm tra tính hợp lệ của bản đồ.
- Cài đặt năm thuật toán tìm kiếm cổ điển gồm DFS, BFS, UCS, Greedy và A* trong thư mục `src/search/`.
- Viết tài liệu hướng dẫn sử dụng `README.md` và tạo file `requirements.txt` để liệt kê các thư viện cần thiết cho dự án.
- **Trạng thái:** Hoàn thành.

### 2.4. Lê Anh Vũ
- Phân công nhiệm vụ, theo dõi tiến độ và nhắc nhở các thành viên về thời hạn hoàn thành công việc.
- Lập trình cơ chế di chuyển của Ghost bằng thuật toán BFS trong `ghost.py`.
- Xây dựng giao diện đồ họa bằng Pygame trong thư mục `ui/`.
- Phát triển chức năng xem trước bản đồ trong `map_browser.py` và sửa lỗi giao diện bị khựng do khởi tạo font chữ liên tục khi chạy ở 60 FPS.
- **Trạng thái:** Hoàn thành.

---

## 3. Các công việc phối hợp nhóm

Bên cạnh nhiệm vụ cá nhân, các thành viên cùng trao đổi, tích hợp và kiểm tra những phần có liên quan để chương trình hoạt động thống nhất.

### 3.1. Xử lý tình trạng Ghost đi trùng vị trí và tích hợp tìm đường
- **Thành viên tham gia:** Vũ Thành Thanh Tùng, Bùi Chí Thành.
- Cùng tìm cách hạn chế tình trạng nhiều Ghost di chuyển đến cùng một ô khi đuổi theo Pacman.
- Kết nối phần đọc bản đồ `map_loader.py`, trạng thái trò chơi trong `game_state.py` với các thuật toán tìm kiếm và chương trình chính `main.py`.

### 3.2. Tìm kiếm đối kháng và điều chỉnh hàm heuristic
- **Thành viên tham gia:** Khúc Hữu Trung, Bùi Chí Thành.
- Cùng điều chỉnh hàm đánh giá trong `adv_problem.py` và kiểm tra cách cập nhật giá trị alpha tại nút gốc của Alpha-Beta Pruning khi sử dụng điểm phạt cho việc quay lại ô đã đi qua.
- Chạy thử và xem xét hành vi của Ghost để phân biệt cách di chuyển giữa Ghost có xu hướng chặn đường và Ghost bám theo Pacman.

### 3.3. Tính khoảng cách trong mê cung và viết cơ sở lý thuyết
- **Thành viên tham gia:** Khúc Hữu Trung, Vũ Thành Thanh Tùng.
- Cùng xây dựng hàm `_compute_bfs_distances` để tính khoảng cách thực tế giữa các vị trí trong mê cung, phục vụ việc đánh giá trạng thái trong `adv_problem.py`.
- Phối hợp viết phần cơ sở lý thuyết về các thuật toán được sử dụng trong báo cáo `report.pdf`.

### 3.4. Kết hợp thuật toán đối kháng với chuyển động của Ghost
- **Thành viên tham gia:** Khúc Hữu Trung, Lê Anh Vũ.
- Cùng kiểm tra hoạt động của Minimax và Alpha-Beta Pruning với cơ chế di chuyển của Ghost trên giao diện mô phỏng.
- Đối chiếu kết quả tính toán của thuật toán với các nước đi thực tế để phát hiện và sửa những điểm chưa thống nhất.

### 3.5. Xây dựng bản đồ, kiểm thử và sửa lỗi
- **Thành viên tham gia:** Toàn bộ nhóm gồm Bùi Chí Thành, Khúc Hữu Trung, Vũ Thành Thanh Tùng và Lê Anh Vũ.
- Cùng tạo và chạy thử hơn 20 bản đồ trong thư mục `maps/`, với các bố cục và tình huống khác nhau.
- Xây dựng và chạy hơn 30 trường hợp kiểm thử bằng `unittest` để kiểm tra hoạt động của các thuật toán và những thành phần chính trong chương trình.
- Cùng kiểm tra, sửa lỗi phát sinh trong quá trình tích hợp, chẳng hạn như Pacman đi đến Goal khi chưa ăn hết Food và tình trạng giao diện bị khựng khi chạy.

---

## 4. Tuyên bố sử dụng trí tuệ nhân tạo (AI)

Trong quá trình thực hiện đồ án, nhóm có sử dụng ChatGPT, Gemini và Claude để tra cứu cú pháp Python, tìm hiểu cách triển khai một số thành phần và hỗ trợ xác định nguyên nhân gây lỗi.

Các công cụ này được sử dụng trong quá trình tham khảo và trao đổi kỹ thuật. Nhóm lựa chọn, điều chỉnh và kiểm tra các giải pháp trước khi đưa vào dự án.

### 4.1. Phạm vi thực hiện và trách nhiệm của nhóm
Nhóm nghiên cứu và cài đặt các thuật toán DFS, BFS, UCS, Greedy, A*, Multi-Goal Search, Minimax và Alpha-Beta Pruning dựa trên kiến thức môn học và tài liệu tham khảo.

Trong quá trình lập trình, nhóm có tham khảo AI về một số ý tưởng và cách sử dụng thư viện. Mã nguồn được điều chỉnh để phù hợp với cấu trúc của dự án và được kiểm tra thông qua các trường hợp thử nghiệm. Các thành viên chịu trách nhiệm về phần công việc được phân công, mã nguồn tích hợp và kết quả được trình bày trong báo cáo.

### 4.2. Các nội dung có tham khảo AI

#### a. Tìm hiểu cách tổ chức chương trình theo OOP trong Python (Claude)
Do các thành viên đã quen với C++, nhóm tham khảo Claude để tìm hiểu thêm về cách tổ chức chương trình hướng đối tượng trong Python. Nội dung trao đổi gồm các phương thức `__hash__` và `__eq__` để hỗ trợ quản lý trạng thái trong quá trình tìm kiếm, cách tổ chức lớp `GameState` và cách phân chia mã nguồn giữa hai thư mục `src/` và `ui/`.

#### b. Tham khảo hướng cải thiện heuristic cho Multi-Goal Search (Gemini)
Ban đầu, nhóm sử dụng khoảng cách Manhattan lớn nhất làm heuristic cho bài toán tìm kiếm nhiều mục tiêu. Qua quá trình chạy thử, nhóm nhận thấy số node mở rộng còn tương đối lớn nên tìm hiểu thêm về hướng tiếp cận dựa trên cây khung nhỏ nhất (Minimum Spanning Tree – MST).

Sau khi trao đổi với Gemini, nhóm tìm hiểu cách áp dụng MST cho bài toán nới lỏng, sau đó cài đặt thuật toán Prim và sử dụng bộ nhớ đệm `_mst_cache` để hạn chế tính toán lặp lại. Nhóm cũng xem xét tính admissible và consistent của heuristic để đưa vào phần giải thích thuật toán trong báo cáo. Theo kết quả thực nghiệm của nhóm, số node mở rộng giảm khoảng 51% trong điều kiện so sánh tương ứng.

#### c. Tham khảo cách xử lý hành vi di chuyển của Ghost (Gemini và Claude)
Trong quá trình chạy thử, nhóm nhận thấy Ghost đôi khi di chuyển qua lại giữa các ô hoặc nhiều Ghost cùng hướng đến một vị trí. Nhóm tham khảo một số hướng xử lý từ AI, sau đó điều chỉnh logic di chuyển bằng cách kết hợp BFS với cơ chế lọc các hành động an toàn thông qua `safe_actions`. Mục đích là hạn chế tình trạng Ghost đi trùng vị trí và cải thiện hành vi di chuyển trong quá trình mô phỏng.

#### d. Hỗ trợ tìm nguyên nhân và sửa lỗi chương trình (ChatGPT và Claude)
- **Lỗi giao diện:** Khi chạy ở 60 FPS, giao diện đôi lúc bị khựng. Nhóm kiểm tra quá trình vẽ giao diện và nhận thấy đối tượng `pygame.font.Font` được khởi tạo nhiều lần trong các frame. Nhóm chuyển sang lưu lại các font đã tạo để sử dụng lại, giảm việc khởi tạo đối tượng không cần thiết.
- **Lỗi trong Alpha-Beta Pruning:** Nhóm tham khảo AI để rà soát logic tìm kiếm khi Pacman có xu hướng đi vào ô có Ghost. Qua quá trình kiểm tra, nhóm xem xét lại cách kết hợp điểm phạt quay lại ô đã đi qua với việc cập nhật giá trị alpha tại nút gốc. Kết quả của Alpha-Beta Pruning được đối chiếu với Minimax để kiểm tra tính nhất quán.
- **Điều kiện thắng:** Nhóm kiểm tra lại điều kiện kết thúc trò chơi trên các bản đồ có cả Food và Goal, điều chỉnh logic để Pacman phải ăn hết thức ăn trước khi đi đến ô đích và hoàn thành màn chơi.

#### e. Tham khảo cách xây dựng công cụ chạy thử và kiểm thử (Gemini và ChatGPT)
Nhóm tham khảo cách sử dụng `argparse` để thiết lập tham số dòng lệnh trong `main.py`, phục vụ việc chạy chương trình với các thuật toán và cấu hình khác nhau. Nhóm cũng tìm hiểu cách sử dụng `time` để đo thời gian thực thi và `unittest` để tổ chức kiểm thử tự động.

Các kết quả chạy thử được sử dụng để so sánh thuật toán thông qua những chỉ số như thời gian chạy, số bước đi và số node mở rộng.

---

## 5. Xác nhận đóng góp của các thành viên

Các thành viên đã thống nhất về nội dung phân công công việc và phần đóng góp được trình bày trong báo cáo này. Mỗi thành viên chịu trách nhiệm đối với phần việc của mình và phối hợp với các thành viên khác trong quá trình tích hợp, kiểm thử chương trình.