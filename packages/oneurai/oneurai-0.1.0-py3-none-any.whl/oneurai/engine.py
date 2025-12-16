from .api import api_client
from .core import Tensor
import torch
import torch.nn as nn
import os
from tqdm import tqdm

class Model:
    def __init__(self, backend_model=None):
        self._model = backend_model
        self.optimizer = None
        self.criterion = nn.MSELoss() # الافتراضي (يمكن تغييره)

    @classmethod
    def create(cls, layers_config: list, activation='relu'):
        """
        إنشاء مودل مخصص. مثال: one.create_model([2, 10, 1])
        """
        print(f"🛠️ بناء مودل جديد: {layers_config}")
        layers = []
        for i in range(len(layers_config) - 1):
            layers.append(nn.Linear(layers_config[i], layers_config[i+1]))
            if i < len(layers_config) - 2:
                if activation == 'relu': layers.append(nn.ReLU())
                elif activation == 'sigmoid': layers.append(nn.Sigmoid())
                elif activation == 'tanh': layers.append(nn.Tanh())
        
        return cls(backend_model=nn.Sequential(*layers))

    @classmethod
    def from_hub(cls, model_id, architecture_config=None):
        """
        تحميل مودل من Oneurai Hub.
        model_id: 'username/repo_name'
        architecture_config: قائمة الطبقات لإعادة بناء المودل [Input, Hidden, Output]
        """
        # 1. تحديد اسم الملف
        filename = f"{model_id.split('/')[-1]}.pt"
        
        # 2. تحميل الملف باستخدام API
        if not os.path.exists(filename):
            success = api_client.download_file(model_id, filename, filename)
            if not success:
                # إذا فشل التحميل (مثلاً المودل غير موجود)، نرجع مودل فارغ للتدريب الجديد
                if architecture_config:
                    print("⚠️ لم يتم العثور على ملف، سيتم إنشاء مودل جديد بناءً على الإعدادات.")
                    return cls.create(architecture_config)
                raise Exception("فشل تحميل المودل ولم يتم توفير إعدادات للبناء.")

        # 3. تحميل الأوزان (Weights)
        print("🔓 جاري تحميل الأوزان...")
        try:
            # نحتاج نعرف هيكلية المودل أولاً. 
            # للتبسيط هنا: نفترض أن المستخدم يمرر الهيكلية، أو نستخدم هيكلية محفوظة داخل الملف
            # (الحل الاحترافي: حفظ الهيكلية داخل ملف JSON منفصل، لكن سنبسطها الآن)
            state_dict = torch.load(filename)
            
            if architecture_config:
                instance = cls.create(architecture_config)
            else:
                # محاولة استنتاج الهيكلية (صعب بدون ميتا داتا، لذا نطلب الكونفق)
                raise Exception("يجب تمرير 'architecture_config' عند تحميل مودل لأول مرة.")
            
            instance._model.load_state_dict(state_dict)
            print("✅ تم استعادة المودل بنجاح!")
            return instance
            
        except Exception as e:
            print(f"❌ الملف معطوب أو غير متوافق: {e}")
            return None

    def _prepare(self, data):
        """تحويل أي نوع بيانات إلى Oneurai Tensor داخلي"""
        if isinstance(data, list): return torch.tensor(data).float()
        if isinstance(data, Tensor): return data._data.float()
        return data

    def train(self, inputs, targets, epochs=10, lr=0.01, batch_size=None):
        if not self._model: raise Exception("المودل غير جاهز.")
        
        X = self._prepare(inputs)
        Y = self._prepare(targets)
        if len(Y.shape) == 1: Y = Y.unsqueeze(1)

        self.optimizer = torch.optim.Adam(self._model.parameters(), lr=lr)
        
        print(f"\n🚀 تدريب ({epochs} Epochs)...")
        pbar = tqdm(range(epochs))
        
        self._model.train()
        for _ in pbar:
            self.optimizer.zero_grad()
            preds = self._model(X)
            loss = self.criterion(preds, Y)
            loss.backward()
            self.optimizer.step()
            pbar.set_postfix({'Loss': f"{loss.item():.4f}"})
            
    def predict(self, inputs):
        self._model.eval()
        with torch.no_grad():
            return self._model(self._prepare(inputs)).tolist()

    def evaluate(self, inputs, targets):
        """حساب نسبة الدقة (تقريبي)"""
        self._model.eval()
        X, Y = self._prepare(inputs), self._prepare(targets)
        if len(Y.shape) == 1: Y = Y.unsqueeze(1)
        
        with torch.no_grad():
            preds = self._model(X)
            # MSE (Mean Squared Error)
            loss = self.criterion(preds, Y).item()
            # Accuracy Percentage (for regression roughly)
            accuracy = max(0, 100 - (loss * 100)) 
            print(f"📊 التقييم: Loss={loss:.4f} | Accuracy ~{accuracy:.1f}%")

    def save_local(self, filename):
        torch.save(self._model.state_dict(), filename)
        print(f"💾 تم الحفظ محلياً: {filename}")

    def push_to_hub(self, repo_id):
        """حفظ المودل ورفعه بضغطة زر"""
        filename = f"{repo_id.split('/')[-1]}.pt"
        self.save_local(filename)
        api_client.push_file(repo_id, filename)
        # خيار: حذف الملف المحلي بعد الرفع للتنظيف
        # os.remove(filename)