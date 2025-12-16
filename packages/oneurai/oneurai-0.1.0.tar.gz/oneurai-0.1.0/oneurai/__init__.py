from .api import api_client
from .core import Tensor
from .engine import Model

# --- دوال الواجهة الرئيسية ---

def login(token):
    """تسجيل الدخول لربط المكتبة بحسابك"""
    api_client.login(token)

def create_model(layers, activation='relu'):
    """إنشاء مودل جديد: one.create_model([2, 5, 1])"""
    return Model.create(layers, activation)

def load_model(repo_id, config):
    """تحميل مودل من الموقع: one.load_model('user/repo', [2,5,1])"""
    return Model.from_hub(repo_id, config)

def tensor(data):
    """اختصار لإنشاء مصفوفة"""
    return Tensor(data)