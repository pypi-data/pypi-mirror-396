import requests
import json
import os
import torch
import torch.nn as nn
import torch.optim as optim
from tqdm import tqdm  # شريط التقدم

# Global variable to store token
API_TOKEN = None
BASE_URL = "https://amosb.fun/api"  # تأكد من الدومين حقك

# =====================================================
# 1. Authentication & Setup
# =====================================================
def login(token):
    global API_TOKEN
    API_TOKEN = token
    
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Accept": "application/json"
    }
    
    try:
        response = requests.get(f"{BASE_URL}/user", headers=headers)
        if response.status_code == 200:
            user_data = response.json()
            print(f"✅ Logged in successfully as: {user_data.get('username') or user_data.get('name')}")
        else:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            API_TOKEN = None
    except Exception as e:
        print(f"❌ Connection error: {e}")
        API_TOKEN = None

# =====================================================
# 2. Help System (New Feature 🆕)
# =====================================================
def help():
    """
    Displays the official documentation and available commands in the terminal.
    """
    help_text = """
    ==================================================
    🤖 ONEURAI LIBRARY - HELP MENU (v0.1.1)
    ==================================================
    
    Welcome to Oneurai! Here are the available commands:

    1️⃣  Authentication:
        >>> import oneurai as one
        >>> one.login("YOUR_API_TOKEN")

    2️⃣  Creating a Model:
        >>> model = one.create_model([Input, Hidden, Output])
        Example: model = one.create_model([2, 4, 1]) (XOR Gate)

    3️⃣  Training:
        >>> model.train(X_data, y_data, epochs=100)
        
    4️⃣  Prediction:
        >>> result = model.predict([0, 1])
        
    5️⃣  Cloud Upload (Save to Server):
        >>> model.push_to_hub("username/project-name")
        
    6️⃣  Cloud Download (Load from Server):
        >>> model = one.load_model("username/project-name", [2, 4, 1])

    For more support, visit: https://amosb.fun
    ==================================================
    """
    print(help_text)

# =====================================================
# 3. Neural Network Engine
# =====================================================
class SimpleNN(nn.Module):
    def __init__(self, layers_config):
        super(SimpleNN, self).__init__()
        layers = []
        for i in range(len(layers_config) - 1):
            layers.append(nn.Linear(layers_config[i], layers_config[i+1]))
            if i < len(layers_config) - 2:
                layers.append(nn.ReLU())
            else:
                layers.append(nn.Sigmoid())
        self.model = nn.Sequential(*layers)
        self.config = layers_config

    def forward(self, x):
        return self.model(x)

    def train_model(self, X, y, epochs=1000, learning_rate=0.01):
        criterion = nn.BCELoss()
        optimizer = optim.Adam(self.parameters(), lr=learning_rate)
        
        X_tensor = torch.tensor(X, dtype=torch.float32)
        y_tensor = torch.tensor(y, dtype=torch.float32)

        print(f"\n🚀 Starting training ({epochs} Epochs)...")
        
        # Adding Progress Bar
        for _ in tqdm(range(epochs), desc="Training"):
            optimizer.zero_grad()
            outputs = self(X_tensor)
            loss = criterion(outputs, y_tensor)
            loss.backward()
            optimizer.step()
            
        print("✅ Training completed successfully.")

    def save(self, path):
        torch.save({
            'state_dict': self.state_dict(),
            'config': self.config
        }, path)

    def load(self, path):
        checkpoint = torch.load(path)
        self.load_state_dict(checkpoint['state_dict'])
        self.config = checkpoint['config']
        self.eval()

# Wrapper Class for better UX
class Model:
    def __init__(self, layers_config):
        self.engine = SimpleNN(layers_config)
        self.config = layers_config
        print(f"🛠️  Model created with architecture: {layers_config}")

    def train(self, X, y, epochs=1000):
        self.engine.train_model(X, y, epochs)

    def predict(self, input_data):
        input_tensor = torch.tensor(input_data, dtype=torch.float32)
        with torch.no_grad():
            return self.engine(input_tensor).tolist()

    def push_to_hub(self, repo_id):
        if not API_TOKEN:
            print("❌ Error: You must login first using one.login()")
            return
        
        # 1. Save locally first
        filename = f"{repo_id.split('/')[-1]}.pt"
        self.engine.save(filename)
        print(f"💾 Saved locally as: {filename}")

        # 2. Upload
        url = f"{BASE_URL}/repos/{repo_id}/upload"
        headers = {"Authorization": f"Bearer {API_TOKEN}"}
        
        print(f"☁️  Uploading to {repo_id}...")
        try:
            with open(filename, 'rb') as f:
                response = requests.post(url, headers=headers, files={'file': f})
            
            if response.status_code in [200, 201]:
                print("✅ Upload successful! Your model is now on the cloud.")
            else:
                print(f"❌ Upload failed: {response.text}")
        except Exception as e:
            print(f"❌ Connection error: {e}")
        finally:
            if os.path.exists(filename):
                os.remove(filename)

# Factory Function
def create_model(layers):
    return Model(layers)

# =====================================================
# 4. Loading Models from Hub
# =====================================================
def load_model(repo_id, layers_config):
    if not API_TOKEN:
        print("❌ Error: Login required.")
        return None

    filename = f"{repo_id.split('/')[-1]}.pt"
    url = f"{BASE_URL}/repos/{repo_id}/download/{filename}"
    headers = {"Authorization": f"Bearer {API_TOKEN}"}

    print(f"⬇️  Downloading model from {repo_id}...")
    try:
        response = requests.get(url, headers=headers, stream=True)
        if response.status_code == 200:
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Reconstruct model
            model = Model(layers_config)
            model.engine.load(filename)
            print("✅ Model loaded successfully!")
            
            os.remove(filename) # Cleanup
            return model
        else:
            print(f"❌ Download failed: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None