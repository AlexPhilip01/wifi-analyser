"""
WiFi Analyser - Flask Backend
Author: Alex Philip | MSc Information Security, Royal Holloway
Run with: sudo python app.py  (sudo required for ARP scanning)
"""

from flask import Flask, render_template, jsonify, request
import subprocess
import socket
import os
import re
import platform
import ipaddress
import threading
from datetime import datetime
import csv
import io

app = Flask(__name__)

OS_TYPE = platform.system()

# ─────────────────────────────────────────────
# UTILITY FUNCTIONS
# ─────────────────────────────────────────────

def resolve_hostname(ip):
    try:
        return socket.gethostbyaddr(ip)[0]
    except (socket.herror, socket.gaierror):
        return "Unknown"


def validate_cidr(cidr):
    try:
        net = ipaddress.IPv4Network(cidr, strict=False)
        return True, net
    except ValueError as e:
        return False, str(e)


# ─────────────────────────────────────────────
# ARP SCAN — Device Discovery
# ─────────────────────────────────────────────

def arp_scan(target_range, timeout=2):
    devices = []
    try:
        from scapy.all import ARP, Ether, srp
        arp_request = ARP(pdst=target_range)
        broadcast   = Ether(dst="ff:ff:ff:ff:ff:ff")
        packet      = broadcast / arp_request
        answered, _ = srp(packet, timeout=timeout, verbose=0)

        for sent, received in answered:
            ip       = received.psrc
            mac      = received.hwsrc
            hostname = resolve_hostname(ip)
            devices.append({"ip": ip, "mac": mac, "hostname": hostname})

        devices.sort(key=lambda x: socket.inet_aton(x["ip"]))

    except PermissionError:
        return {"error": "Permission denied. Run with: sudo python app.py"}
    except Exception as e:
        return {"error": str(e)}

    return {"devices": devices, "count": len(devices)}


# ─────────────────────────────────────────────
# WIFI SCAN — Nearby Networks
# ─────────────────────────────────────────────

def scan_wifi():
    networks = []

    if OS_TYPE == "Linux":
        try:
            result = subprocess.run(
                ["nmcli", "-f", "SSID,SIGNAL,SECURITY,CHAN", "device", "wifi", "list"],
                capture_output=True, text=True, timeout=15
            )
            if result.returncode == 0:
                lines = result.stdout.strip().split("\n")[1:]
                for line in lines:
                    parts = line.split()
                    if len(parts) >= 2 and parts[0] != "--":
                        networks.append({
                            "ssid":     parts[0],
                            "signal":   int(parts[1]) if parts[1].isdigit() else 0,
                            "security": parts[2] if len(parts) > 2 else "?",
                            "channel":  parts[3] if len(parts) > 3 else "?"
                        })
                return {"networks": networks}
        except Exception:
            pass

        # Fallback: iwlist
        try:
            result = subprocess.run(
                ["sudo", "iwlist", "scan"],
                capture_output=True, text=True, timeout=15
            )
            ssids   = re.findall(r'ESSID:"(.+?)"', result.stdout)
            signals = re.findall(r'Signal level=(-?\d+)', result.stdout)
            for i, ssid in enumerate(ssids):
                sig = int(signals[i]) if i < len(signals) else -100
                # Convert dBm to percentage approx
                pct = max(0, min(100, (sig + 100) * 2))
                networks.append({
                    "ssid":     ssid,
                    "signal":   pct,
                    "security": "N/A",
                    "channel":  "N/A"
                })
            return {"networks": networks}
        except Exception as e:
            return {"error": str(e)}

    elif OS_TYPE == "Darwin":
        try:
            airport = "/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport"
            result  = subprocess.run([airport, "-s"], capture_output=True, text=True, timeout=15)
            lines   = result.stdout.strip().split("\n")[1:]
            for line in lines:
                parts = line.split()
                if len(parts) >= 3:
                    sig = int(parts[2]) if parts[2].lstrip("-").isdigit() else -100
                    pct = max(0, min(100, (sig + 100) * 2))
                    networks.append({
                        "ssid":     parts[0],
                        "signal":   pct,
                        "security": parts[-1],
                        "channel":  parts[3] if len(parts) > 3 else "?"
                    })
            return {"networks": networks}
        except Exception as e:
            return {"error": str(e)}

    return {"error": "WiFi scanning not supported on this OS"}


# ─────────────────────────────────────────────
# PING TEST
# ─────────────────────────────────────────────

def ping_host(ip, count=4):
    flag = "-n" if OS_TYPE == "Windows" else "-c"
    try:
        result = subprocess.run(
            ["ping", flag, str(count), "-W", "1", ip],
            capture_output=True, text=True, timeout=15
        )
        output = result.stdout

        match = re.search(r'(?:rtt|round-trip)[^=]+=\s*[\d.]+/([\d.]+)', output)
        if match:
            return {"ip": ip, "latency": float(match.group(1)), "status": "online"}

        match = re.search(r'Average = (\d+)ms', output)
        if match:
            return {"ip": ip, "latency": float(match.group(1)), "status": "online"}

        return {"ip": ip, "latency": None, "status": "offline"}

    except Exception:
        return {"ip": ip, "latency": None, "status": "offline"}


def ping_all(ips):
    results  = []
    threads  = []
    lock     = threading.Lock()

    def worker(ip):
        r = ping_host(ip)
        with lock:
            results.append(r)

    for ip in ips:
        t = threading.Thread(target=worker, args=(ip,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join(timeout=20)

    results.sort(key=lambda x: socket.inet_aton(x["ip"]))
    return {"results": results}


# ─────────────────────────────────────────────
# PORT SCANNER
# ─────────────────────────────────────────────

PORT_NAMES = {
    21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP",
    53: "DNS", 80: "HTTP", 443: "HTTPS",
    3306: "MySQL", 8080: "HTTP-Alt", 8443: "HTTPS-Alt"
}

DEFAULT_PORTS = [21, 22, 23, 25, 53, 80, 443, 3306, 8080, 8443]


def scan_ports(ip, ports=None, timeout=0.5):
    if ports is None:
        ports = DEFAULT_PORTS
    open_ports = []
    for port in ports:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            if sock.connect_ex((ip, port)) == 0:
                open_ports.append({"port": port, "service": PORT_NAMES.get(port, "Unknown")})
            sock.close()
        except Exception:
            pass
    return {"ip": ip, "open_ports": open_ports}


def scan_all_ports(ips, ports=None):
    results = []
    threads = []
    lock    = threading.Lock()

    def worker(ip):
        r = scan_ports(ip, ports)
        with lock:
            results.append(r)

    for ip in ips:
        t = threading.Thread(target=worker, args=(ip,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join(timeout=30)

    results.sort(key=lambda x: socket.inet_aton(x["ip"]))
    return {"results": results}


# ─────────────────────────────────────────────
# CSV EXPORT
# ─────────────────────────────────────────────

def build_csv(devices, ping_results, port_results):
    output  = io.StringIO()
    writer  = csv.writer(output)

    writer.writerow(["WiFi Analyser Report", datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
    writer.writerow([])

    writer.writerow(["IP", "Hostname", "MAC", "Status", "Latency (ms)", "Open Ports"])

    ping_map = {r["ip"]: r for r in ping_results}
    port_map = {r["ip"]: r for r in port_results}

    for dev in devices:
        ip       = dev["ip"]
        ping_r   = ping_map.get(ip, {})
        port_r   = port_map.get(ip, {})
        ports    = ", ".join([f"{p['port']}/{p['service']}" for p in port_r.get("open_ports", [])])
        latency  = ping_r.get("latency", "N/A")
        status   = ping_r.get("status", "unknown")
        writer.writerow([ip, dev["hostname"], dev["mac"], status, latency, ports])

    return output.getvalue()


# ─────────────────────────────────────────────
# FLASK ROUTES
# ─────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/scan/devices", methods=["POST"])
def api_scan_devices():
    data  = request.json or {}
    cidr  = data.get("range", "192.168.1.0/24")
    valid, net = validate_cidr(cidr)
    if not valid:
        return jsonify({"error": f"Invalid CIDR: {net}"}), 400
    return jsonify(arp_scan(cidr))


@app.route("/api/scan/wifi", methods=["GET"])
def api_scan_wifi():
    return jsonify(scan_wifi())


@app.route("/api/scan/ping", methods=["POST"])
def api_ping():
    data = request.json or {}
    ips  = data.get("ips", [])
    if not ips:
        return jsonify({"error": "No IPs provided"}), 400
    return jsonify(ping_all(ips))


@app.route("/api/scan/ports", methods=["POST"])
def api_ports():
    data  = request.json or {}
    ips   = data.get("ips", [])
    ports = data.get("ports", DEFAULT_PORTS)
    if not ips:
        return jsonify({"error": "No IPs provided"}), 400
    return jsonify(scan_all_ports(ips, ports))


@app.route("/api/export/csv", methods=["POST"])
def api_export_csv():
    from flask import Response
    data        = request.json or {}
    devices     = data.get("devices", [])
    ping_results = data.get("ping", [])
    port_results = data.get("ports", [])
    csv_data    = build_csv(devices, ping_results, port_results)
    filename    = f"wifi_scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    print("=" * 55)
    print("  WiFi Analyser - Starting...")
    print(f"  OS: {OS_TYPE}")
    print(f"  Port: {port}")
    print("=" * 55)
    app.run(debug=False, host="0.0.0.0", port=port)
