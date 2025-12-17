import requests
import json
import os
import torch
import torch.nn as nn
import torch.optim as optim
from tqdm import tqdm

# =====================================================
# 🎨 Design & Colors (Visuals) - NEW SECTION ✨
# =====================================================
class Colors:
    """ANSI color codes for professional terminal output."""
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    ENDC = '\033[0m' # Reset color

# شعار المكتبة الاحترافي (ASCII Art)
ONEURAI_BANNER = f"""{Colors.CYAN}{Colors.BOLD}
   ____                                  _ 
  / __ \                                (_)
 | |  | |_ __   ___ _   _ _ __ __ _ _   
 | |  | | '_ \ / _ \ | | | '__/ _` | |  
 | |__| | | | |  __/ |_| | | | (_| | |  
  \____/|_| |_|\___|\__,_|_|  \__,_|_|  
                                        
      {Colors.GREEN}>> AI & MLOps Library <<{Colors.ENDC}
"""

def print_banner():
    """Prints theOneurai logo in the terminal."""
    print(ONEURAI_BANNER)

# =====================================================
# Global Variables
# =====================================================
API_TOKEN = None
BASE_URL = "https://amosb.fun/api"

# =====================================================
# 1. Authentication & Setup
# =====================================================
def login(token):
    """Authenticates the user and displays the banner."""
    print_banner() # ✅ إظهار الشعار عند تسجيل الدخول
    global API_TOKEN
    API_TOKEN = token
    
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Accept": "application/json"
    }
    
    print(f"{Colors.CYAN}📡 Connecting to backend...{Colors.ENDC}")

    try:
        response = requests.get(f"{BASE_URL}/user", headers=headers)
        if response.status_code == 200:
            user_data = response.json()
            # محاولة جلب الاسم أو اليوزرنيم
            username = user_data.get('username') or user_data.get('name') or "User"
            print(f"{Colors.GREEN}✅ Logged in successfully as: {Colors.BOLD}{username}{Colors.ENDC}")
        else:
            print(f"{Colors.RED}❌ Login failed: {response.status_code} - Unauthenticated.{Colors.ENDC}")
            print(f"{Colors.YELLOW}💡 Tip: Ensure your token is correct and includes the leading ID number (e.g., '3|xxxxx').{Colors.ENDC}")
            API_TOKEN = None
    except Exception as e:
        print(f"{Colors.RED}❌ Connection error: {e}{Colors.ENDC}")
        API_TOKEN = None

# =====================================================
# 2. Help System
# =====================================================
def help():
    """Displays the official documentation with the banner."""
    print_banner() # ✅ إظهار الشعار في المساعدة
    
    help_text = f"""
    {Colors.BOLD}Welcome to the Oneurai Help Menu!{Colors.ENDC}
    Here are the available commands to speed up your workflow:

    {Colors.CYAN}1️⃣  Authentication:{Colors.ENDC}
        >>> import oneurai as one
        >>> one.login("YOUR_API_TOKEN")

    {Colors.CYAN}2️⃣  Creating a Model:{Colors.ENDC}
        >>> model = one.create_model([Input, Hidden, Output])
        Example: model = one.create_model([2, 4, 1]) (XOR Gate)

    {Colors.CYAN}3️⃣  Training:{Colors.ENDC}
        >>> model.train(X_data, y_data, epochs=100)
        
    {Colors.CYAN}4️⃣  Prediction:{Colors.ENDC}
        >>> result = model.predict([0, 1])
        
    {Colors.CYAN}5️⃣  Cloud Upload (Save to Server):{Colors.ENDC}
        >>> model.push_to_hub("username/project-name")
        
    {Colors.CYAN}6️⃣  Cloud Download (Load from Server):{Colors.ENDC}
        >>> model = one.load_model("username/project-name", [2, 4, 1])

    {Colors.YELLOW}For full documentation and support, visit: https://amosb.fun{Colors.ENDC}
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
        
        # Adding Progress Bar with color
        for _ in tqdm(range(epochs), desc="Training", colour='green'):
            optimizer.zero_grad()
            outputs = self(X_tensor)
            loss = criterion(outputs, y_tensor)
            loss.backward()
            optimizer.step()
            
        print(f"{Colors.GREEN}✅ Training completed successfully.{Colors.ENDC}")

    def save(self, path):
        torch.save({'state_dict': self.state_dict(), 'config': self.config}, path)

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
        print(f"🛠️  Model created with architecture: {Colors.BOLD}{layers_config}{Colors.ENDC}")

    def train(self, X, y, epochs=1000):
        self.engine.train_model(X, y, epochs)

    def predict(self, input_data):
        input_tensor = torch.tensor(input_data, dtype=torch.float32)
        with torch.no_grad():
            return self.engine(input_tensor).tolist()

    def push_to_hub(self, repo_id):
        if not API_TOKEN:
            print(f"{Colors.RED}❌ Error: You must login first using one.login(){Colors.ENDC}")
            return
        
        filename = f"{repo_id.split('/')[-1]}.pt"
        self.engine.save(filename)
        # print(f"💾 Saved locally as: {filename}") # اختياري لتقليل الازعاج

        url = f"{BASE_URL}/repos/{repo_id}/upload"
        headers = {"Authorization": f"Bearer {API_TOKEN}"}
        
        print(f"☁️  Uploading to {Colors.BOLD}{repo_id}{Colors.ENDC}...")
        try:
            with open(filename, 'rb') as f:
                response = requests.post(url, headers=headers, files={'file': f})
            
            if response.status_code in [200, 201]:
                print(f"{Colors.GREEN}✅ Upload successful! Your model is now on the cloud.{Colors.ENDC}")
            else:
                print(f"{Colors.RED}❌ Upload failed: {response.text}{Colors.ENDC}")
        except Exception as e:
            print(f"{Colors.RED}❌ Connection error: {e}{Colors.ENDC}")
        finally:
            if os.path.exists(filename):
                os.remove(filename)

def create_model(layers):
    return Model(layers)

# =====================================================
# 4. Loading Models from Hub
# =====================================================
def load_model(repo_id, layers_config):
    if not API_TOKEN:
        print(f"{Colors.RED}❌ Error: Login required.{Colors.ENDC}")
        return None

    filename = f"{repo_id.split('/')[-1]}.pt"
    url = f"{BASE_URL}/repos/{repo_id}/download/{filename}"
    headers = {"Authorization": f"Bearer {API_TOKEN}"}

    print(f"⬇️  Downloading model from {Colors.BOLD}{repo_id}{Colors.ENDC}...")
    try:
        response = requests.get(url, headers=headers, stream=True)
        if response.status_code == 200:
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            model = Model(layers_config)
            model.engine.load(filename)
            print(f"{Colors.GREEN}✅ Model loaded successfully!{Colors.ENDC}")
            
            os.remove(filename)
            return model
        else:
            print(f"{Colors.RED}❌ Download failed: {response.text}{Colors.ENDC}")
            return None
    except Exception as e:
        print(f"{Colors.RED}❌ Error: {e}{Colors.ENDC}")
        return None