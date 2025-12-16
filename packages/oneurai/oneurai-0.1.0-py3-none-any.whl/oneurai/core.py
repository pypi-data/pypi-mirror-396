import torch

class Tensor:
    def __init__(self, data):
        if isinstance(data, torch.Tensor):
            self._data = data
        else:
            # تحويل ذكي للبيانات (يضمن أنها Float للحسابات)
            self._data = torch.tensor(data).float()

    def __repr__(self):
        return f"OneTensor(shape={tuple(self._data.shape)}, data=\n{self._data.tolist()})"

    @property
    def shape(self):
        return list(self._data.shape)

    # --- دوال إنشاء (Factory Methods) مثل NumPy ---
    @staticmethod
    def zeros(shape):
        """إنشاء مصفوفة أصفار: one.Tensor.zeros((3,3))"""
        return Tensor(torch.zeros(shape))

    @staticmethod
    def ones(shape):
        """إنشاء مصفوفة آحاد: one.Tensor.ones((2,2))"""
        return Tensor(torch.ones(shape))

    @staticmethod
    def random(shape):
        """إنشاء مصفوفة أرقام عشوائية"""
        return Tensor(torch.rand(shape))

    # --- عمليات متقدمة ---
    def reshape(self, *shape):
        return Tensor(self._data.reshape(*shape))

    def dot(self, other):
        val = other._data if isinstance(other, Tensor) else other
        return Tensor(torch.matmul(self._data, val))

    def transpose(self):
        return Tensor(self._data.t())

    def to_list(self):
        return self._data.tolist()

    # --- العمليات الحسابية الأساسية ---
    def __add__(self, other): return self._op(other, torch.add)
    def __sub__(self, other): return self._op(other, torch.sub)
    def __mul__(self, other): return self._op(other, torch.mul)
    def __truediv__(self, other): return self._op(other, torch.div)

    def _op(self, other, func):
        val = other._data if isinstance(other, Tensor) else other
        return Tensor(func(self._data, val))