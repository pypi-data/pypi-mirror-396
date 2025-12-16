import requests
import os
from tqdm import tqdm  # شريط تحميل للملفات الكبيرة

# ملاحظة: غير الرابط هنا لرابط موقعك الحقيقي عند النشر (https://oneurai.com/api)
BASE_URL = "https://amosb.fun/api"

class OneuraiAPI:
    def __init__(self):
        self.token = None
        self.headers = {}

    def login(self, token):
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json"
        }
        # تجربة اتصال سريع
        try:
            r = requests.get(f"{BASE_URL}/user/me", headers=self.headers, timeout=5)
            if r.status_code == 200:
                print(f"✅ تم تسجيل الدخول: {r.json().get('username', 'User')}")
            else:
                print(f"⚠️ تنبيه: التوكن قد يكون غير صالح. كود: {r.status_code}")
        except Exception as e:
            print(f"⚠️ فشل الاتصال بالسيرفر: {e}")

    def push_file(self, repo_id, file_path):
        """رفع ملف إلى السيرفر"""
        if not self.token: raise Exception("يجب تسجيل الدخول أولاً: one.login()")
        
        username, repo_name = repo_id.split('/')
        url = f"{BASE_URL}/repos/{username}/{repo_name}/upload"
        
        print(f"🚀 جاري رفع {os.path.basename(file_path)}...")
        try:
            with open(file_path, 'rb') as f:
                response = requests.post(url, headers=self.headers, files={'file': f})
            
            if response.status_code == 201:
                print("✅ تم الرفع بنجاح!")
            else:
                print(f"❌ خطأ في الرفع: {response.text}")
        except Exception as e:
            print(f"❌ خطأ غير متوقع: {e}")

    def download_file(self, repo_id, filename, save_path):
        """تحميل ملف من السيرفر (ميزة جديدة)"""
        if not self.token: raise Exception("يجب تسجيل الدخول أولاً.")
        
        username, repo_name = repo_id.split('/')
        # نفترض وجود رابط تحميل في لارفيل (سنحتاج لبرمجته لاحقاً في الموقع)
        url = f"{BASE_URL}/repos/{username}/{repo_name}/download/{filename}"
        
        print(f"⬇️ جاري تحميل {filename} من {repo_id}...")
        try:
            with requests.get(url, headers=self.headers, stream=True) as r:
                r.raise_for_status()
                total_size = int(r.headers.get('content-length', 0))
                
                with open(save_path, 'wb') as f, tqdm(total=total_size, unit='B', unit_scale=True) as bar:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
                        bar.update(len(chunk))
            print("✅ اكتمل التحميل.")
            return True
        except Exception as e:
            print(f"❌ فشل التحميل (تأكد أن الملف موجود في الموقع): {e}")
            return False

api_client = OneuraiAPI()