# 📡 WiFi Analyser

A local web-based network analysis tool with a clean dashboard UI. Built with Python (Flask) + vanilla JS. Run it locally — open your browser and analyse your network in one click.

> **Author:** Alex Philip | MSc Information Security, Royal Holloway (NCSC/GCHQ-accredited)  
> **Skills:** Network Forensics · Penetration Testing · Security Monitoring

---

## Features

| Feature | Description |
|---------|-------------|
| 🔍 **Device Discovery** | ARP scan — finds every device on your subnet with IP, MAC, and hostname |
| 🔢 **Device Count** | Instantly shows how many devices are connected |
| 🎛 **Adjustable Range** | Set any CIDR range (e.g. `192.168.1.0/24`, `10.0.0.0/24`) |
| 📶 **WiFi Networks** | Scans nearby SSIDs with signal strength and security type |
| 🏓 **Ping / Latency** | Tests all discovered devices in parallel |
| 🔓 **Port Scanner** | Checks 10 common ports per device using raw sockets |
| 🚨 **Security Flags** | Auto-flags insecure ports (FTP, Telnet) and open WiFi |
| ⬇ **CSV Export** | Download full scan results as a spreadsheet |
| 🌐 **Web Dashboard** | Clean dark-theme UI — no terminal needed after launch |

---

## Screenshots

> Dashboard shows live stats, device table, WiFi signal bars, ping status, and port results.

---

## Quick Start

### Prerequisites
- Python 3.8+
- Linux (Kali/Ubuntu recommended) or macOS
- `sudo` access (required for ARP scanning)

### Install & Run

```bash
# 1. Clone the repo
git clone https://github.com/AlexPhilip01/wifi-analyser.git
cd wifi-analyser

# 2. Install dependencies
pip3 install -r requirements.txt

# 3. Launch (use sudo for full ARP scanning)
sudo python3 app.py

# OR use the launch script
bash run.sh
```

### Open the Dashboard

```
http://localhost:5000
```

---

## Usage

1. **Set IP Range** — Enter your subnet CIDR (e.g. `192.168.1.0/24`) in the top bar
2. **Click FULL SCAN** — Runs all modules automatically
3. **Or run individually** — Use the action buttons for specific scans
4. **Export** — Download results as CSV

### Finding Your Subnet
```bash
# Linux
ip route | grep src

# macOS
ipconfig getifaddr en0

# Output example: 192.168.1.105 → your range is 192.168.1.0/24
```

---

## Ports Scanned

| Port | Service |
|------|---------|
| 21 | FTP |
| 22 | SSH |
| 23 | Telnet |
| 25 | SMTP |
| 53 | DNS |
| 80 | HTTP |
| 443 | HTTPS |
| 3306 | MySQL |
| 8080 | HTTP-Alt |
| 8443 | HTTPS-Alt |

---

## Project Structure

```
wifi-analyser/
├── app.py              # Flask backend (scanning logic + API routes)
├── templates/
│   └── index.html      # Web dashboard (HTML + CSS + JS, single file)
├── requirements.txt    # Python dependencies
├── run.sh              # One-click launch script (Linux/macOS)
└── README.md
```

---

## Legal & Ethical Notice

> This tool is intended for **use on networks you own or have explicit permission to scan**.  
> Unauthorized scanning of networks is illegal under the Computer Fraud and Abuse Act (CFAA) and equivalent laws worldwide.  
> The author is not responsible for misuse.

---

## Tech Stack

- **Backend:** Python 3, Flask, Scapy, Socket
- **Frontend:** HTML5, CSS3, Vanilla JS (no frameworks)
- **Export:** CSV via Python `csv` module

---

## License

MIT License — free to use, modify, and distribute with attribution.

---

*Built as part of a cybersecurity portfolio. Feedback welcome via Issues or LinkedIn.*
