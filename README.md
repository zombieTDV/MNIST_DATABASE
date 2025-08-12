# Using DataBase cia Python

Tổ chức dữ liệu (MNIST) thành các class (python). Lưu trữ xuống dưới CSDL (SQL server).

## Installation Guide

### Prerequisites
- Python 3.8 or higher

### Step 1: Clone the Repository
```bash
git https://github.com/zombieTDV/MNIST_DataBase.git
cd MNIST_DataBase
```
### Step 2: Create Virtual Environment
```bash
# Create virtual environment
python -m venv ENV

# Activate virtual environment
# On Windows:
ENV\Scripts\activate.bat
# On macOS/Linux:
source ENV/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Run the Application
```bash
python main.py
```

## Project Structure

📦MNIST_DataBase
 ┣ 📂config
 ┃ ┣ 📜config.yaml
 ┃ ┗ 📜settings.py
 ┣ 📂mnist_data
 ┃ ┗ 📂MNIST
 ┃
 ┣ 📂src
 ┃ ┗ 📜utils.py
 ┣ 📜.gitignore
 ┣ 📜main.py
 ┣ 📜Query.sql
 ┗ 📜README.md