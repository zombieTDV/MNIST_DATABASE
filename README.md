# Using DataBase cia Python

Tổ chức dữ liệu (MNIST) thành các class (python). Lưu trữ xuống dưới CSDL (SQL server). Sử dụng Microsoft SQL Server

## Installation Guide

### Prerequisites
- Python 3.8 or higher

### Step 1: Clone the Repository
```bash
git clone https://github.com/zombieTDV/MNIST_DATABASE.git
cd MNIST_DATABASE
```
### Step 2: Create Virtual Environment
```bash
# Create virtual environment
python -m venv ENV
```

# Activate virtual environment
#### On Windows:
```bash
ENV\Scripts\activate.bat
```
#### On macOS/Linux:
```bash
source ENV/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Set up correct configuration for database in config\config.yaml
#### No SQL Server?
    You can download it via Docker: 
```bash    
docker pull mcr.microsoft.com/mssql/server:2022-latest
```
    Check out for more information about download and use Miscrosoft SQL Server via Internet.

### Step 5: Create DataBase and table by running Query.sql
### Step 6: Run the Application
```bash
python main.py
```

## Project Structure
```
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
```