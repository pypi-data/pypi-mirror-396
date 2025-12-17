import requests
import os
import torch
import torch.nn as nn
import torch.optim as optim
from tqdm import tqdm

# =====================================================
# 🎨 المظهر والشعار
# =====================================================
class Colors:
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    ENDC = '\033[0m'

def print_banner():
    print(f"""{Colors.CYAN}{Colors.BOLD}
   ____                                  _ 
  / __ \                                (_)
 | |  | |_ __   ___ _   _ _ __ __ _ _   
 | |  | | '_ \ / _ \ | | | '__/ _` | |  
 | |__| | | | |  __/ |_| | | | (_| | |  
  \____/|_| |_|\___|\__,_|_|  \__,_|_|  
                                        
      {Colors.GREEN}>> AI & MLOps Library <<{Colors.ENDC}
""")

# =====================================================
# إعدادات الاتصال
# =====================================================
API_TOKEN = None
BASE_URL = "https://amosb.fun/api"

# =====================================================
# 1. الدخول (Authentication) - المعدلة ✅
# =====================================================
def login(token):
    print_banner()
    global API_TOKEN
    API_TOKEN = token
    
    headers = {"Authorization": f"Bearer {API_TOKEN}", "Accept": "application/json"}
    print(f"{Colors.CYAN}📡 Checking connection...{Colors.ENDC}")
    
    try:
        response = requests.get(f"{BASE_URL}/user", headers=headers)
        
        if response.status_code == 200:
            user = response.json()
            name = user.get('username') or user.get('name')
            print(f"{Colors.GREEN}✅ Connected successfully as: {name}{Colors.ENDC}")
        else:
            # هنا التعديل الذكي: لا نوقف البرنامج، بل نعطي تحذير فقط
            print(f"{Colors.YELLOW}⚠️  Warning: Could not fetch username (Code {response.status_code}).{Colors.ENDC}")
            print(f"{Colors.YELLOW}👉 Continuing anyway... Upload might still work if token is valid.{Colors.ENDC}")
            
    except Exception as e:
        print(f"{Colors.RED}❌ Connection Warning: {e}{Colors.ENDC}")

# =====================================================
# 2. نظام المساعدة
# =====================================================
def help():
    print_banner()
    print("""
    Available Commands:
    1. one.login("YOUR_TOKEN")
    2. model = one.create_model([2, 4, 1])
    3. model.train(X, y)
    4. model.push_to_hub("username/project_name")
    5. model = one.load_model("username/project_name", [2, 4, 1])
    """)

# =====================================================
# 3. محرك الذكاء الاصطناعي
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

    def train_model(self, X, y, epochs=1000):
        criterion = nn.BCELoss()
        optimizer = optim.Adam(self.parameters(), lr=0.01)
        X_t = torch.tensor(X, dtype=torch.float32)
        y_t = torch.tensor(y, dtype=torch.float32)
        
        print("\n🚀 Training...")
        for _ in tqdm(range(epochs), desc="Epochs", colour='green'):
            optimizer.zero_grad()
            outputs = self(X_t)
            loss = criterion(outputs, y_t)
            loss.backward()
            optimizer.step()
        print(f"{Colors.GREEN}✅ Done.{Colors.ENDC}")

    def save(self, path):
        torch.save({'state_dict': self.state_dict(), 'config': self.config}, path)

    def load(self, path):
        checkpoint = torch.load(path)
        self.load_state_dict(checkpoint['state_dict'])
        self.config = checkpoint['config']
        self.eval()

# واجهة المستخدم (Wrapper)
class Model:
    def __init__(self, layers):
        self.engine = SimpleNN(layers)
    
    def train(self, X, y, epochs=1000):
        self.engine.train_model(X, y, epochs)

    def predict(self, val):
        with torch.no_grad():
            return self.engine(torch.tensor(val, dtype=torch.float32)).tolist()

    # -------------------------------------------------------------
    # ☁️ دالة الرفع
    # -------------------------------------------------------------
    def push_to_hub(self, full_repo_name):
        if "/" not in full_repo_name:
            print(f"{Colors.RED}❌ Format Error: Use 'username/project_name'{Colors.ENDC}")
            return
            
        username, repo_name = full_repo_name.split("/", 1)
        filename = f"{repo_name}.pt"
        self.engine.save(filename)

        url = f"{BASE_URL}/repos/{username}/{repo_name}/upload"
        headers = {"Authorization": f"Bearer {API_TOKEN}"}
        
        print(f"☁️ Uploading to {url} ...")
        
        try:
            with open(filename, 'rb') as f:
                response = requests.post(url, headers=headers, files={'file': f})
            
            if response.status_code in [200, 201]:
                print(f"{Colors.GREEN}✅ Upload Successful!{Colors.ENDC}")
                print(f"   Saved at: {response.json().get('path')}")
            else:
                print(f"{Colors.RED}❌ Server Error ({response.status_code}):{Colors.ENDC}")
                print(f"   {response.text}")
                
        except Exception as e:
            print(f"{Colors.RED}❌ Connection Failed: {e}{Colors.ENDC}")
        finally:
            if os.path.exists(filename): os.remove(filename)

def create_model(layers):
    return Model(layers)

def load_model(full_repo_name, layers):
    username, repo_name = full_repo_name.split("/", 1)
    filename = f"{repo_name}.pt"
    url = f"{BASE_URL}/repos/{full_repo_name}/download/{filename}"
    headers = {"Authorization": f"Bearer {API_TOKEN}"}
    
    print(f"⬇️ Downloading...")
    try:
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            with open(filename, 'wb') as f: f.write(r.content)
            m = Model(layers)
            m.engine.load(filename)
            print(f"{Colors.GREEN}✅ Loaded.{Colors.ENDC}")
            os.remove(filename)
            return m
        else:
            print(f"{Colors.RED}❌ Failed: {r.text}{Colors.ENDC}")
    except Exception as e:
        print(f"{Colors.RED}❌ Error: {e}{Colors.ENDC}")