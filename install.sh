#!/data/data/com.termux/files/usr/bin/bash

echo -e "\e[34m🔐 Starting Password Vault setup...\e[0m"

# مرحله 1: بررسی نصب بودن پایتون
if ! command -v python > /dev/null 2>&1; then
    echo -e "\e[33m📦 Python not found. Installing...\e[0m"
    pkg update -y && pkg install -y python || {
        echo -e "\e[31m❌ Failed to install Python. Exiting.\e[0m"
        exit 1
    }
else
    echo -e "\e[32m✅ Python already installed.\e[0m"
fi

# مرحله 2: بررسی نصب emoji
if ! pip show emoji > /dev/null 2>&1; then
    echo -e "\e[33m📦 Installing emoji library...\e[0m"
    pip install emoji || {
        echo -e "\e[31m❌ Failed to install emoji. Exiting.\e[0m"
        exit 1
    }
else
    echo -e "\e[32m✅ emoji already installed.\e[0m"
fi

# مرحله 3: ساخت دایرکتوری مخفی برای فایل‌ها
VAULT_DIR="$HOME/.vault"
mkdir -p "$VAULT_DIR"
echo -e "\e[32m📁 Vault directory created at $VAULT_DIR\e[0m"

# مرحله 4: دریافت فایل پایتون
echo -e "\e[33m📥 Downloading file...\e[0m"
curl -fsSL https://raw.githubusercontent.com/Sinaksh0/passwordvault/main/vault.py -o "$VAULT_DIR/vault.py" || {
    echo -e "\e[31m❌ Failed to download vault.py. Exiting.\e[0m"
    exit 1
}

# مرحله 5: اجرای فایل
echo -e "\e[36m🚀 Launching file...\e[0m"
python "$VAULT_DIR/vault.py" || {
    echo -e "\e[31m❌ Python script failed to run. Exiting.\e[0m"
    exit 1
}

echo -e "\e[32m🎉 Vault setup complete. All data stays inside Termux.\e[0m"
