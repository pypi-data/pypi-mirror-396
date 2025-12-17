# EitaaSender

EitaaSender یک کتابخانه پایتون ساده برای ارسال پیام و فایل به کانال‌ها و گروه‌های ایتا است.  
با استفاده از این کتابخانه می‌توانید به راحتی از API ایتا پیام ارسال کنید یا فایل آپلود کنید.

## نصب

```bash
pip install eitaa_sender
```
نحوه استفاده

from EitaaSender import EitaaSender

TOKEN = "توکن_خود_را_اینجا_قرار_دهید"
sender = EitaaSender(TOKEN)

# ارسال پیام متنی
sender.send_message("YourChannelId", "سلام دنیا!")

# ارسال فایل
sender.send_file("YourChannelId", "D:\\Eitaa\\pic.png", "این یک تصویر است!")


ارتباط با ما
https://t.me/MyCodeStore

گیت هاب:
https://github.com/alireza-sadeghian/EitaaSender