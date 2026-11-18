# 📝 ToDo Task Web Application - Hướng Dẫn Triển Khai Production (Ubuntu Server 24.04)

Ứng dụng quản lý công việc cá nhân (ToDo Task) được phát triển bằng **Django 5** và **MySQL**, triển khai trực tiếp trên máy chủ **Ubuntu Server 24.04 LTS** sử dụng kiến trúc chuẩn Production: **Nginx (Reverse Proxy + Static Files) + Gunicorn (WSGI Application Server) + MySQL (Database)**, hoàn toàn không phụ thuộc vào Docker.

---

## 🎯 Tính Năng Chính Của Ứng Dụng

- 🔐 **Xác thực người dùng (Authentication):**
  - Đăng ký tài khoản (`UserCreationForm`), Đăng nhập, Đăng xuất an toàn.
  - Mật khẩu được băm (hash) tự động theo thuật toán PBKDF2 chuẩn của Django.
- 👤 **Phân quyền & Phân tách dữ liệu (User Isolation):**
  - Mỗi tài khoản người dùng chỉ có thể xem, tạo, cập nhật và xóa các công việc do chính mình sở hữu.
  - Toàn bộ các View CRUD được bảo vệ nghiêm ngặt bằng decorator `@login_required`.
- ✏️ **Quản lý công việc (Task CRUD):**
  - Thêm mới công việc với tiêu đề, mô tả.
  - Cập nhật thông tin công việc và đánh dấu Hoàn thành / Chưa hoàn thành.
  - Xóa công việc an toàn (yêu cầu phương thức POST và xác nhận trước khi xóa).
- ⚙️ **Bảo mật & Biến môi trường:**
  - Tách biệt hoàn toàn thông tin nhạy cảm (`SECRET_KEY`, thông tin MySQL, `DEBUG`) thông qua file `.env` với thư viện `python-dotenv`.
  - Phục vụ tệp tĩnh (Static files) tối ưu qua Nginx và `collectstatic`.

---

## 🏗️ Kiến Trúc Triển Khai Production

```
Client Browser (Người dùng)
       │ HTTP / HTTPS (Port 80 / 443)
       ▼
┌────────────────────────────────────────────────────────┐
│               Nginx Reverse Proxy                      │
│  ├─ /static/ ──► Phục vụ trực tiếp từ staticfiles/     │
│  └─ / ────────► Proxy pass tới Gunicorn (Port 8000)    │
└────────────────────────────────────────────────────────┘
       │ HTTP / Unix Socket
       ▼
┌────────────────────────────────────────────────────────┐
│            Gunicorn (WSGI Server - Systemd)            │
│         Chạy ứng dụng Django: Task.wsgi:application     │
└────────────────────────────────────────────────────────┘
       │ TCP (Port 3306)
       ▼
┌────────────────────────────────────────────────────────┐
│                   MySQL Server                         │
│             Database: todo_db (utf8mb4)                │
└────────────────────────────────────────────────────────┘
```

---

## 📁 Cấu Trúc Thư Mục Dự Án

```
ToDo-Task/
├── Task/                       # Cấu hình dự án Django
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py             # Đọc .env, cấu hình MySQL, Static files, Security
│   ├── urls.py                 # Điều hướng URL chính
│   └── wsgi.py                 # Điểm vào WSGI cho Gunicorn
├── todo/                       # Ứng dụng quản lý Task & Xác thực
│   ├── migrations/             # Lịch sử lược đồ Database
│   ├── admin.py                # Quản trị viên Django Admin
│   ├── apps.py
│   ├── forms.py                # TaskForm tùy biến giao diện
│   ├── models.py               # Model Task liên kết ForeignKey(User)
│   ├── urls.py                 # URL CRUD và Register/Login/Logout
│   ├── views.py                # Logic xử lý phân quyền và CRUD
│   └── templates/todo/         # Giao diện HTML của app
│       ├── create_task.html
│       ├── list_task.html
│       ├── login.html
│       ├── register.html
│       └── update_task.html
├── templates/                  # Thư mục template toàn cục dự án
│   ├── todo/                   # Template đồng bộ giao diện
│   └── todo_page.html
├── .env                        # File biến môi trường (KHÔNG commit lên Git)
├── .env.example                # File biến môi trường mẫu
├── .gitignore                  # Bỏ qua .env, venv, staticfiles, db.sqlite3...
├── manage.py                   # CLI quản lý Django
└── requirements.txt            # Danh sách thư viện Python cần thiết
```

---

## 🚀 Hướng Dẫn Cài Đặt Chi Tiết Từ Đầu Trên Ubuntu Server 24.04 LTS

### Bước 1: Cập nhật hệ điều hành và cài đặt các gói hệ thống cần thiết

Trên Ubuntu 24.04 LTS, thư viện `mysqlclient` cần các gói dev của MySQL và bộ công cụ biên dịch C:

```bash
# Cập nhật danh sách gói phần mềm
sudo apt update && sudo apt upgrade -y

# Cài đặt Python, venv, MySQL Server, Nginx, Git và các gói thư viện bắt buộc để build mysqlclient
sudo apt install -y python3-pip python3-venv python3-dev \
    default-libmysqlclient-dev pkg-config build-essential \
    nginx mysql-server git
```

> **Lưu ý:** Gói `default-libmysqlclient-dev` và `pkg-config` là bắt buộc trên Ubuntu 24.04 để cài đặt thành công `mysqlclient` qua `pip` mà không bị lỗi thiếu header C.

---

### Bước 2: Cài đặt và cấu hình cơ sở dữ liệu MySQL

1. Khởi động và kích hoạt dịch vụ MySQL:
```bash
sudo systemctl start mysql
sudo systemctl enable mysql
```

2. Đăng nhập vào MySQL với quyền root:
```bash
sudo mysql
```

3. Chạy các câu lệnh SQL sau để tạo Database và người dùng chuyên dụng:
```sql
-- Tạo Database hỗ trợ đầy đủ tiếng Việt và emoji (utf8mb4)
CREATE DATABASE todo_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Tạo User và mật khẩu mạnh (thay bằng mật khẩu của bạn nếu cần)
CREATE USER 'todo_user'@'localhost' IDENTIFIED BY 'ChangeMeStrong@2026';

-- Cấp toàn quyền cho User trên database todo_db
GRANT ALL PRIVILEGES ON todo_db.* TO 'todo_user'@'localhost';

-- Áp dụng thay đổi quyền
FLUSH PRIVILEGES;

-- Thoát MySQL
EXIT;
```

4. Kiểm tra đăng nhập với user vừa tạo:
```bash
mysql -u todo_user -p -e "SHOW DATABASES;"
# Nhập mật khẩu: ChangeMeStrong@2026
```

---

### Bước 3: Đưa mã nguồn lên VPS và tạo Virtual Environment

1. Di chuyển vào thư mục web (ví dụ `/var/www/` hoặc thư mục home của bạn):
```bash
# Ví dụ tạo thư mục dự án tại /var/www/todo-app
sudo mkdir -p /var/www/todo-app
sudo chown -R $USER:$USER /var/www/todo-app
cd /var/www/todo-app

# Clone dự án từ repository của bạn (hoặc copy mã nguồn lên thư mục này)
# git clone <URL_REPO_CUA_BAN> .
```

2. Tạo và kích hoạt môi trường ảo Python (Virtual Environment):
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Nâng cấp `pip` và cài đặt danh sách thư viện từ `requirements.txt`:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

### Bước 4: Cấu hình biến môi trường (`.env`)

1. Sao chép từ file mẫu `.env.example`:
```bash
cp .env.example .env
```

2. Chỉnh sửa nội dung file `.env` bằng `nano`:
```bash
nano .env
```

3. Điền các thông số thực tế của VPS:
```env
# Django Settings
SECRET_KEY=django-insecure-production-secret-key-change-this-in-production-2026
DEBUG=False
ALLOWED_HOSTS=127.0.0.1,localhost,192.168.100.10,YOUR_VPS_PUBLIC_IP

# Database Configuration (MySQL)
DB_NAME=todo_db
DB_USER=todo_user
DB_PASSWORD=ChangeMeStrong@2026
DB_HOST=127.0.0.1
DB_PORT=3306

# CSRF Trusted Origins (chứa IP VPS hoặc domain)
CSRF_TRUSTED_ORIGINS=http://127.0.0.1,http://localhost,http://YOUR_VPS_PUBLIC_IP
```
*(Bấm `Ctrl + O` để lưu, `Enter`, rồi `Ctrl + X` để thoát nano).*

---

### Bước 5: Chạy Database Migration và Gom tệp tĩnh (Collectstatic)

Đảm bảo môi trường ảo `venv` đang được kích hoạt:

1. Áp dụng toàn bộ migrations vào cơ sở dữ liệu MySQL:
```bash
python manage.py migrate
```

2. Gom toàn bộ CSS/JS/ảnh tĩnh vào thư mục `staticfiles/` để Nginx phục vụ:
```bash
python manage.py collectstatic --noinput
```

3. Tạo tài khoản quản trị tối cao (Superuser) cho trang Django Admin:
```bash
python manage.py createsuperuser
```
*(Nhập username, email, mật khẩu khi được yêu cầu).*

---

### Bước 6: Cấu hình Gunicorn chạy dưới dạng Systemd Service

Chạy Gunicorn dưới dạng dịch vụ nền của hệ điều hành giúp ứng dụng tự động khởi động cùng hệ thống và tự phục hồi khi có sự cố.

1. Tạo file cấu hình dịch vụ Systemd:
```bash
sudo nano /etc/systemd/system/gunicorn.service
```

2. Dán nội dung cấu hình sau vào file (thay `ubuntu` bằng tên user của bạn và đường dẫn thư mục tương ứng nếu khác):
```ini
[Unit]
Description=Gunicorn daemon for Django ToDo Application
After=network.target mysql.service

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/var/www/todo-app
ExecStart=/var/www/todo-app/venv/bin/gunicorn \
    --workers 3 \
    --bind 127.0.0.1:8000 \
    --access-logfile /var/log/gunicorn-access.log \
    --error-logfile /var/log/gunicorn-error.log \
    Task.wsgi:application

Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

3. Nạp lại cấu hình Systemd, khởi động và kích hoạt Gunicorn:
```bash
sudo systemctl daemon-reload
sudo systemctl start gunicorn
sudo systemctl enable gunicorn
```

4. Kiểm tra trạng thái hoạt động:
```bash
sudo systemctl status gunicorn
```
*(Nếu hiển thị `Active: active (running)` màu xanh lá cây là thành công).*

---

### Bước 7: Cấu hình Nginx làm Reverse Proxy & Static Files Server

1. Tạo file cấu hình virtual host cho Nginx:
```bash
sudo nano /etc/nginx/sites-available/todo
```

2. Dán cấu hình sau (thay `YOUR_VPS_IP` bằng IP tĩnh hoặc tên miền của bạn):
```nginx
server {
    listen 80;
    server_name YOUR_VPS_IP;

    client_max_body_size 20M;

    # Phục vụ tệp tĩnh trực tiếp qua Nginx để đạt hiệu năng tối đa
    location /static/ {
        alias /var/www/todo-app/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, no-transform";
    }

    # Bỏ qua favicon nếu không có
    location = /favicon.ico { 
        access_log off; 
        log_not_found off; 
    }

    # Chuyển tiếp toàn bộ request khác sang Gunicorn
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

3. Kích hoạt cấu hình bằng cách tạo symlink sang thư mục `sites-enabled`:
```bash
sudo ln -s /etc/nginx/sites-available/todo /etc/nginx/sites-enabled/
```

4. Xóa cấu hình mặc định nếu không dùng:
```bash
sudo rm -f /etc/nginx/sites-enabled/default
```

5. Kiểm tra tính đúng đắn của cú pháp Nginx:
```bash
sudo nginx -t
```
*(Nếu hiển thị `syntax is ok` và `test is successful` là chuẩn).*

6. Phân quyền thư mục staticfiles để Nginx (`www-data`) có quyền đọc:
```bash
sudo chmod -R 755 /var/www/todo-app/staticfiles
```

7. Khởi động lại Nginx:
```bash
sudo systemctl restart nginx
```

---

### Bước 8: Cấu hình tường lửa (UFW Firewall)

Mở các cổng cần thiết trên VPS:
```bash
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw enable
sudo ufw status
```

---

### Bước 9: Truy Cập & Kiểm Tra Ứng Dụng

Mở trình duyệt web và truy cập:
```
http://YOUR_VPS_PUBLIC_IP/
```
- Bạn sẽ được chuyển hướng tới trang Đăng nhập (`/todo/login/`).
- Bấm vào link **Register** để tạo tài khoản người dùng mới.
- Sau khi đăng ký thành công, hệ thống tự động đăng nhập và đưa bạn tới danh sách công việc (`/todo/list_task/`).
- Bạn có thể tạo, chỉnh sửa trạng thái, và xóa công việc của riêng mình.
- Bạn có thể đăng xuất và tạo một tài khoản thứ hai để kiểm chứng tính năng phân tách dữ liệu hoàn toàn giữa các User!
- Truy cập `http://YOUR_VPS_PUBLIC_IP/admin/` để đăng nhập bằng tài khoản Superuser quản trị.

---

## 🛠️ Hướng Dẫn Bảo Trì & Xử Lý Sự Cố (Troubleshooting)

### 1. Xem nhật ký lỗi Gunicorn
```bash
# Xem log qua journalctl
sudo journalctl -u gunicorn -n 50 --no-pager

# Hoặc xem file log đã cấu hình
sudo tail -f /var/log/gunicorn-error.log
```

### 2. Xem nhật ký lỗi Nginx
```bash
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log
```

### 3. Khởi động lại các dịch vụ sau khi cập nhật mã nguồn
Khi bạn cập nhật code từ Git:
```bash
cd /var/www/todo-app
source venv/bin/activate
git pull origin main
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart gunicorn
sudo systemctl reload nginx
```

### 4. Lỗi 502 Bad Gateway
- Nguyên nhân: Gunicorn chưa khởi động hoặc gặp lỗi crash khi khởi chạy Django.
- Cách xử lý: Kiểm tra `sudo systemctl status gunicorn` và chạy `sudo journalctl -u gunicorn -e` để xem nguyên nhân cụ thể (thường do sai thông số kết nối MySQL trong file `.env` hoặc thiếu thư viện).

### 5. Lỗi Giao diện mất CSS (Static files 403 Forbidden hoặc 404 Not Found)
- Nguyên nhân: Chưa chạy `collectstatic` hoặc Nginx không có quyền đọc thư mục `staticfiles`.
- Cách xử lý:
  ```bash
  python manage.py collectstatic --noinput
  sudo chmod -R 755 /var/www/todo-app/staticfiles
  sudo systemctl restart nginx
  ```
