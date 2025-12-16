from setuptools import setup, find_packages

setup(
    name="oneurai",
    version="0.1.0",
    description="Oneurai AI: All-in-one AI Library (Dataset, Training, Hub)",
    author="Oneurai Team & Mtma",
    author_email="mtma.1@hotmail.com",
    packages=find_packages(),
    install_requires=[
        "requests",  # عشان نتواصل مع موقعكم
        "torch",     # سنستخدمه في الخلفية (Backend) ونسوي عليه تجريد
        "tqdm"       # لشريط التحميل (Progress bar)
    ],
    python_requires=">=3.7",
)