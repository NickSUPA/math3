# -*- coding: utf-8 -*-
"""
Local Web Server for Math III Study System
Allows accessing the study system from any mobile device, tablet, or laptop.
"""

import http.server
import socketserver
import socket
import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

PORT = 8000
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

def get_ip_addresses():
    ips = []
    # Try hostname resolution
    try:
        hostname = socket.gethostname()
        for ip in socket.gethostbyname_ex(hostname)[2]:
            if not ip.startswith("127.") and not ip.startswith("169.254."):
                ips.append(ip)
    except Exception:
        pass
    
    # Try connecting to external dummy address to get primary outbound IP
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        primary = s.getsockname()[0]
        s.close()
        if primary not in ips:
            ips.insert(0, primary)
    except Exception:
        pass
    
    return ips

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def end_headers(self):
        # Enable CORS and disable aggressive caching so edits reflect immediately
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        super().end_headers()

def main():
    os.chdir(DIRECTORY)
    ips = get_ip_addresses()
    primary_ip = ips[0] if ips else "127.0.0.1"
    
    # Check for Tailscale IP
    ts_ip = None
    for ip in ips:
        if ip.startswith("100."):
            ts_ip = ip
            break

    url = f"http://{primary_ip}:{PORT}"
    
    print("=" * 60)
    print("  MATH III - LOCAL SERVER RUNNING")
    print("=" * 60)
    print(" เข้าใช้งานจากเครื่องนี้ (This PC):")
    print(f"   👉 http://localhost:{PORT}")
    print()
    print("📱 เข้าใช้งานจากมือถือ / iPad / แท็บเล็ต (Wi-Fi เดียวกัน):")
    print(f"   👉 {url}")
    print()
    if ts_ip:
        print("🌍 เข้าใช้งานจากทุกที่ผ่าน Tailscale (นอกบ้าน / เน็ตมือถือ 4G/5G):")
        print(f"   👉 http://{ts_ip}:{PORT}")
        print()
    print("=" * 60)

    # Try generating terminal QR Code and image
    try:
        import qrcode
        qr = qrcode.QRCode(box_size=1, border=2)
        qr.add_data(url)
        qr.make(fit=True)
        print("📷 สแกน QR Code ด้านล่างนี้ด้วยกล้องมือถือเพื่อเปิดทันที:")
        qr.print_ascii(invert=True)
        print("=" * 60)
        
        # Also save image
        img = qrcode.make(url)
        img.save(os.path.join(DIRECTORY, "server_qr.png"))
    except Exception as e:
        pass

    print(f"Server is serving directory: {DIRECTORY}")
    print("Press Ctrl+C to stop the server.")
    print("-" * 60)
    sys.stdout.flush()

    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("0.0.0.0", PORT), Handler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server...")
            httpd.server_close()

if __name__ == "__main__":
    main()
