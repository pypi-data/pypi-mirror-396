import requests
import json
import os
import torch
import torch.nn as nn
import torch.optim as optim
from tqdm import tqdm

# =====================================================
# 🎨 Design & Colors (Visuals)
# =====================================================
class Colors:
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    ENDC = '\033[0m'

ONEURAI_BANNER = f"""{Colors.CYAN}{Colors.BOLD}
   ____                             _ 
  / __ \                           (_)
 | |  | |_ __   ___ _   _ _ __ __ _ _   
 | |  | | '_ \ / _ \ | | | '__/ _` | |  
 | |__| | | | |  __/ |_| | | | (_| | |  
  \____/|_| |_|\___|\__,_|_|  \__,_|_|  
                                        
      {Colors.GREEN}>> AI & MLOps Library <<{Colors.ENDC}
"""

def print_banner():
    print(ONEURAI_BANNER)

# =====================================================
# Global Variables
# =====================================================
API_TOKEN = None
# تأكد أن هذا الرابط هو الصحيح لموقعك
BASE_URL = "https://amosb.fun/api"

# =====================================================
# 1. Authentication
# =====================================================
def login(token):
    print_banner()
    global API_TOKEN
    API_TOKEN = token
    
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Accept": "application/json"
    }
    
    print(f"{Colors.CYAN}📡 Connecting to backend...{Colors.ENDC}")

    try:
        # فحص التوكن للتأكد من صحته
        response = requests.get(f"{BASE_URL}/user", headers=headers)
        if response.status_code == 200:
            user_data = response.json()
            username = user_data.get('username') or user_data.get('name')
            print(f"{Colors.GREEN}✅ Logged in successfully as: {Colors.BOLD}{username}{Colors.ENDC}")
        else:
            print(f"{Colors.RED}❌ Login failed: {response.status_code}{Colors.ENDC}")
            print(f"{Colors.YELLOW}💡 Tip: Use the token format 'ID|Token' (e.g. 5|abcdef...){Colors.ENDC}")
            API_TOKEN = None
    except Exception as e:
        print(f"{Colors.RED}❌ Connection error: {e}{Colors.ENDC}")
        API_TOKEN = None

# =====================================================
# 2. Help System
# =====================================================
def help():
    print_banner()
    help_text = f"""
    {Colors.BOLD}Oneurai Commands:{Colors.ENDC}
    
    1. Login:
       >>> one.login("YOUR_TOKEN")
       
    2. Create & Train:
       >>> model = one.create_model([2, 4, 1])
       >>> model.train(X, y)
       
    3. Upload (Must use 'username/project'):
       >>> model.push_to_hub("ksa/my-project")
       
    4. Download:
       >>> model = one.load_model("ksa/my-project", [2, 4, 1])
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
        for _ in tqdm(range(epochs), desc="Training", colour='green'):
            optimizer.zero_grad()
            outputs = self(X_tensor)
            loss = criterion(outputs, y_tensor)
            loss.backward()
            optimizer.step()
        print(f"{Colors.GREEN}✅ Training completed.{Colors.ENDC}")

    def save(self, path):
        torch.save({'state_dict': self.state_dict(), 'config': self.config}, path)

    def load(self, path):
        checkpoint = torch.load(path)
        self.load_state_dict(checkpoint['state_dict'])
        self.config = checkpoint['config']
        self.eval()

# Wrapper Class
class Model:
    def __init__(self, layers_config):
        self.engine = SimpleNN(layers_config)
        self.config = layers_config
        print(f"🛠️  Model initialized: {layers_config}")

    def train(self, X, y, epochs=1000):
        self.engine.train_model(X, y, epochs)

    def predict(self, input_data):
        input_tensor = torch.tensor(input_data, dtype=torch.float32)
        with torch.no_grad():
            return self.engine(input_tensor).tolist()

    # ---------------------------------------------------------
    # ☁️ وظيفة الرفع (متوافقة مع كود Laravel)
    # ---------------------------------------------------------
    def push_to_hub(self, repo_id):
        if not API_TOKEN:
            print(f"{Colors.RED}❌ Error: Please login first.{Colors.ENDC}")
            return
        
        # التحقق من أن المستخدم أدخل الاسم بالصيغة username/project
        if "/" not in repo_id:
            print(f"{Colors.RED}❌ Error: Repo ID must be in format 'username/project_name'{Colors.ENDC}")
            print(f"{Colors.YELLOW}👉 Example: model.push_to_hub('ksa/xor-model'){Colors.ENDC}")
            return

        filename = f"{repo_id.split('/')[-1]}.pt"
        self.engine.save(filename)
        
        # بناء الرابط ليطابق مسار Laravel: /repos/{username}/{repo_name}/upload
        url = f"{BASE_URL}/repos/{repo_id}/upload"
        
        headers = {"Authorization": f"Bearer {API_TOKEN}"}
        
        print(f"☁️  Uploading to {Colors.BOLD}{repo_id}{Colors.ENDC}...")
        try:
            # المفتاح هنا هو 'file' ليطابق $request->file('file') في السيرفر
            with open(filename, 'rb') as f:
                response = requests.post(url, headers=headers, files={'file': f})
            
            if response.status_code in [200, 201]:
                print(f"{Colors.GREEN}✅ Upload successful!{Colors.ENDC}")
            elif response.status_code == 403:
                print(f"{Colors.RED}❌ Upload failed (403): Username mismatch.{Colors.ENDC}")
                print(f"{Colors.YELLOW}👉 Make sure the username in '{repo_id}' matches your token account.{Colors.ENDC}")
            else:
                print(f"{Colors.RED}❌ Upload failed: {response.text}{Colors.ENDC}")

        except Exception as e:
            print(f"{Colors.RED}❌ Connection error: {e}{Colors.ENDC}")
        finally:
            if os.path.exists(filename): os.remove(filename)

def create_model(layers):
    return Model(layers)

def load_model(repo_id, layers_config):
    if not API_TOKEN:
        print(f"{Colors.RED}❌ Login required.{Colors.ENDC}")
        return None

    filename = f"{repo_id.split('/')[-1]}.pt"
    # بناء رابط التحميل ليطابق مسار Laravel
    url = f"{BASE_URL}/repos/{repo_id}/download/{filename}"
    headers = {"Authorization": f"Bearer {API_TOKEN}"}

    print(f"⬇️  Downloading model...")
    try:
        response = requests.get(url, headers=headers, stream=True)
        if response.status_code == 200:
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            model = Model(layers_config)
            model.engine.load(filename)
            print(f"{Colors.GREEN}✅ Model loaded!{Colors.ENDC}")
            os.remove(filename)
            return model
        else:
            print(f"{Colors.RED}❌ Download failed: {response.text}{Colors.ENDC}")
            return None
    except Exception as e:
        print(f"{Colors.RED}❌ Error: {e}{Colors.ENDC}")
        return None