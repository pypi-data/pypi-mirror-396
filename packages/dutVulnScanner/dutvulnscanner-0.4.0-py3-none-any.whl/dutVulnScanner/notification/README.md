# Notification Module

Module thông báo cho DUTVulnScanner hỗ trợ gửi thông báo toast và Discord webhook.

## Tính năng

- **Toast Notification**: Gửi thông báo hệ thống sử dụng thư viện `plyer`
- **Discord Webhook**: Gửi thông báo đến Discord channel qua webhook
- **Notification Manager**: Quản lý nhiều loại thông báo cùng lúc
- **Flexible Configuration**: Dễ dàng cấu hình và mở rộng

## Cài đặt

Dependencies cần thiết đã được thêm vào `pyproject.toml`:

```toml
plyer = ">=2.1.0,<3.0.0"
requests = ">=2.31.0,<3.0.0"
```

### Cài đặt đặc biệt cho Kali Linux

Để toast notifications hoạt động trên Kali Linux, cần cài đặt thêm `python3-dbus`:

```bash
# Cài đặt DBus support
sudo apt install python3-dbus -y

# Tạo virtual environment với system site packages
python3 -m venv .venv --system-site-packages

# Kích hoạt venv và cài plyer
source .venv/bin/activate
pip install plyer
```

**Lưu ý:** Toast notifications trên Linux yêu cầu desktop environment (GNOME, KDE, XFCE) và DBus service đang chạy.

## Sử dụng cơ bản

### 1. Import và tạo NotificationManager

```python
from dutVulnScanner.notification import NotificationManager, NotificationType

# Tạo manager
manager = NotificationManager()

# Thêm toast notification
manager.add_toast_notification()

# Thêm Discord notification (nếu có webhook)
manager.add_discord_notification("https://discord.com/api/webhooks/...")

# Gửi thông báo
manager.send_notification("Tiêu đề", "Nội dung thông báo")
```

### 2. Sử dụng factory function

```python
from dutVulnScanner.notification import create_notification_manager

# Tạo manager với cấu hình nhanh
manager = create_notification_manager(
    discord_webhook="https://discord.com/api/webhooks/...",
    enable_toast=True,
    app_name="MyApp"
)

# Gửi thông báo
manager.send_notification("Scan hoàn tất", "Phát hiện 3 lỗ hổng")
```

### 3. Gửi từng loại riêng biệt

```python
# Gửi toast notification
manager.send_toast("Tiêu đề", "Nội dung")

# Gửi Discord notification
manager.send_discord("Tiêu đề", "Nội dung")

# Gửi Discord message đơn giản (không embed)
manager.send_discord_simple("Message text")
```

## Cấu hình Discord

### Tạo Webhook URL

1. Vào Server Settings > Integrations > Webhooks
2. Click "New Webhook" hoặc "Add Webhook"
3. Chọn channel để gửi thông báo
4. Copy Webhook URL

### Sử dụng Environment Variable

```bash
export DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_WEBHOOK_TOKEN"
```

Sau đó sử dụng trong code:

```python
import os
webhook_url = os.getenv('DISCORD_WEBHOOK_URL')
if webhook_url:
    manager.add_discord_notification(webhook_url)
```

## Discord Notification Options

### Embed Message (mặc định)

```python
manager.send_discord(
    title="Scan Report",
    message="Scan completed successfully",
    color=0x00FF00,  # Màu xanh lá
    fields=[
        {"name": "Vulnerabilities", "value": "5 found", "inline": True},
        {"name": "Critical", "value": "2", "inline": True}
    ]
)
```

### Simple Text Message

```python
manager.send_discord_simple("🔔 **Alert**: Scan completed!")
```

### Advanced Report (Báo cáo scan chi tiết)

```python
# Gửi báo cáo advanced với format responsive
manager.send_advanced_report(
    target="critical-target.com",
    vuln_count=18,
    duration="12m 45s",
    vulnerabilities=[
        {"severity": "Critical", "count": 2, "description": "Remote Code Execution"},
        {"severity": "High", "count": 3, "description": "SQL Injection"}
    ],
    stats={"Critical": 2, "High": 3, "Total_Scanned": 1000},
    report_url="https://example.com/full-report.pdf",
    mention="@security-team",
    simple_mode=False  # Full mode với emoji và markdown
)
```

**Tính năng WOW của Advanced Report:**

### Full Mode (mặc định):
- 🎨 Format đẹp mắt với emoji và markdown
- 📊 List vulnerabilities chi tiết với emoji severity
- ⚠️ Risk assessment tự động với màu sắc
- 📈 Quick statistics với emoji
- 🎯 Next steps recommendations
- 📄 Link download full report
- 👥 Mention team members

### Simple Mode (mobile-friendly):
- 📱 Format đơn giản, tương thích mobile
- 🚨 List vulnerabilities với emoji severity
- ⚠️ Risk level indicator
- 📊 Statistics dạng text
- 📄 Report download link

**Chọn mode phù hợp:**
```python
# Full mode với ASCII art (desktop app)
manager.send_advanced_report(target="...", vuln_count=5, simple_mode=False)

# Simple mode (mobile, Discord mobile app)
manager.send_advanced_report(target="...", vuln_count=5, simple_mode=True)
```

**Chọn mode phù hợp:**
```python
# Full mode với emoji và markdown (desktop)
manager.send_advanced_report(target="...", vuln_count=5, simple_mode=False)

# Simple mode (mobile, Discord mobile app)
manager.send_advanced_report(target="...", vuln_count=5, simple_mode=True)
```

**Tính năng WOW của Advanced Report:**

### Full Mode (mặc định - Desktop enhanced):
- 🎨 Format đẹp mắt với emoji và markdown
- 📊 List vulnerabilities chi tiết với emoji severity
- ⚠️ Risk assessment tự động với màu sắc
- 📈 Quick statistics với emoji
- 🎯 Next steps recommendations (khi có vulnerabilities)
- 📄 Link download full report
- 👥 Mention team members

### Simple Mode (mobile-friendly):
- 📱 Format đơn giản, tương thích mobile
- 🚨 List vulnerabilities với emoji severity
- ⚠️ Risk level indicator
- 📊 Statistics dạng text
- 📄 Report download link

## Toast Notification Options

```python
manager.send_toast(
    title="DUTVulnScanner",
    message="Scan completed",
    timeout=5,  # Thời gian hiển thị (giây)
    icon_path="/path/to/custom/icon.png"  # Icon tùy chỉnh
)
```

**Yêu cầu hệ thống:**
- **Linux:** Cần desktop environment (GNOME, KDE, XFCE) và DBus service
- **Windows:** Hoạt động tự nhiên
- **macOS:** Hoạt động tự nhiên

**Troubleshooting Linux:**
- Nếu không thấy toast: Kiểm tra có đang chạy trong desktop environment không
- Nếu có lỗi DBus: Cài đặt `python3-dbus` và sử dụng `--system-site-packages` khi tạo venv

## Xử lý lỗi

Module tự động xử lý lỗi và log warnings:

- Nếu `plyer` không có sẵn → Toast notification bị vô hiệu hóa
- Nếu `requests` không có sẵn → Discord notification bị vô hiệu hóa
- Nếu webhook URL không hợp lệ → Discord notification bị vô hiệu hóa

## Ví dụ hoàn chỉnh

Xem file `test_notify.py` để có ví dụ sử dụng đầy đủ.

## Mở rộng

Để thêm loại notification mới:

1. Tạo class kế thừa từ `Notification`
2. Implement phương thức `send()`
3. Thêm vào `NotificationType` enum
4. Cập nhật `NotificationManager` để hỗ trợ loại mới
