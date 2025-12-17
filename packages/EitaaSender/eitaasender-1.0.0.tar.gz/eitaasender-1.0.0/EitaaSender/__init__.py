import requests


# About: Created by Alireza .S
# Contact:
# Telegram | @Aliherfei
# GitHub: https://github.com/alireza-sadeghian/EitaaSender
# Faghat Heydar amiralmomenin ast.


class EitaaSender:

    """
    به کتابخانه ایتاسندر خوش آمدید
    ابتدا در وبسایت ایتایار ثبت نام نموده و یک توکن ای پی آی دریافت نمایید
     دقت داشته باشید برای ارسال پیام به کانال یا گروهتان، کلید ای پی آی باید متعلق به ادمین گروه یا کانال باشد و بهتر است کانال یا گروه مورد نظر در سامانه ایتایار ثبت شده باشد



     این کلاس اجرا کننده اصلی دستورات کتابخانه ایتاسندر می باشد. برای استفاده از این کلاس ابتدا یک آبجکت از این کلاس به شرح زیر بسازید:

     sender = EitaaSender(TOKEN)

     بعد میتوانید با استفاده از متد های موجود در این کلاس به قابلیت های این کلاس دسترسی داشته باشید:

     sender.get_me()

     sender.send_message(*args)

     sender.send_file(*args)
    
    
    """

    def __init__(self, token):
        self.TOKEN = token
        self.BASE_URL = f"https://eitaayar.ir/api/{self.TOKEN}"



    def get_me(self):
        """
        این تابع اطلاعات پایه ای درباره ای پی آی به صورت یک دیکشنری پایتون باز میگرداند
        
        """
        res = requests.get(f"{self.BASE_URL}/getme")
        return res.json()
    def send_message(self, chat_id, text, disable_notification=None, reply_to=None, date=None, pin=None,view_count_for_delete=None):
        """
        از این تابع برای ارسال پیام به کانال یا گروه خود استفاده کنید
        
        chat_id: شناسه عددی کانال. اگر شناسه عددی کانالتان را ندارید میتوانید در این قسمت یوزر نیم کانالتان را بدون @ وارد کنید
        text: متن مورد نظر برای ارسال
        disable_notification: اگر میخواهید پیام بدون اعلان ارسال شود این مقدار را برابر True قرار دهید
        reply_to: اگر میخواهید پیامتان در جواب پیام دیگری باشد آیدی پیام مورد نظر را در این قسمت وارد کنید
        date: زمان ارسال را مشخص کنید. این زمان باید بر اساس تعداد ثانیه های گذشته از تاریخ شروع ساعت هماهنگجهانی یعنی 00:00:00 اول ژانویه 1970 باشد
        pin: اگر میخواهید پیام شما در کانال یا گروهتان پین شود این گزینه را برابر True قرار دهید
        viewCountForDelete: تعداد بازدید برای حذف پیام
        
        مثال استفاده:

        sender.send_message("YourChannelId", "Hello", date=time.time() + 30)

        پیام 30 ثانیه بعد ارسال می شود
        """
        params={
            "chat_id": chat_id,
            "text": text
        }
        if disable_notification:
            params["notification_disable"] = 1
        if reply_to:
            params["reply_to_message_id"] = reply_to
        if date:
            params["date"] = date
        if pin:
            params["pin"] = 1
        if view_count_for_delete:
            params["viewCountForDelete"] = view_count_for_delete
        res = requests.post(f"{self.BASE_URL}/sendMessage", json=params)

        if res.json().get("error_code") == 400:
            raise Exception(f"error: {res.json().get("description")}")
            
    def send_file(self, chat_id, file, caption, disable_notification=None, reply_to=None, date=None, pin=None, view_count_for_delete=None):

        """
        برای ارسال انواع فایل ها مثل تصاویر یا هر فایل دیگر از این متد استفاده کنید.

        chat_id: یوزرنیم کانال بدون آیدی
        file: لوکیشن فایل. دقت کنید که آدرس اینترنتی فایل مورد قبول نمی باشد
        caption: کپشن پست

        مثال استفاده:

        sender.send_file("YourChannelId", "D:\Eitaa\pic.png", "This is a pic!")
        
        """


        params = {
            "chat_id": chat_id,
            # "file": file,
            "caption": caption   
        }

        if hasattr(file, "read"):
            files = {
                "file": ("file", file)
            }
            res= requests.post(f"{self.BASE_URL}/sendFile", data=params, files=files)


        else:
            with open(file, 'rb') as f:
                files = {
                    "file": ("file", f)
                }
                res= requests.post(f"{self.BASE_URL}/sendFile", data=params, files=files)


        if disable_notification:
            params["notification_disable"] = 1
        if reply_to:
            params["reply_to_message_id"] = reply_to
        if date:
            params["date"] = date
        if pin:
            params["pin"] = 1
        if view_count_for_delete:
            params["viewCountForDelete"] = view_count_for_delete

        if res.json().get("error_code") == 400:
            raise Exception(f"error: {res.json().get("description")}")