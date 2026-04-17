#!/data/data/com.termux/files/usr/bin/bash

clear
echo "======================================"
echo "   EL CIENCO STALKER PRO v2.0"
echo "   Instagram & TikTok OSINT"
echo "======================================"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "[!] Python3 tidak ditemukan. Install dengan:"
    echo "    pkg install python"
    exit 1
fi

# Install dependencies
echo "[*] Menginstall dependencies..."
pip install flask flask-cors instaloader beautifulsoup4 requests pillow --quiet

# Get local IP
LOCAL_IP=$(ifconfig wlan0 2>/dev/null | grep 'inet ' | awk '{print $2}')
if [ -z "$LOCAL_IP" ]; then
    LOCAL_IP="127.0.0.1"
fi

echo ""
echo "[✓] Dependencies terinstall"
echo ""
echo "======================================"
echo "  AKSES WEB INTERFACE"
echo "======================================"
echo "  Local:  http://127.0.0.1:5000"
echo "  Network: http://$LOCAL_IP:5000"
echo "======================================"
echo ""
echo "[*] Menjalankan El Cienco Stalker Pro..."
echo "[*] Tekan CTRL+C untuk berhenti"
echo ""

# Run backend
cd backend
python3 server.py
