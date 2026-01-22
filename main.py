import requests
import re
import json

# Simple mapping for common country codes to Chinese names to maintain the requested format
COUNTRY_MAP = {
    'US': '美国', 'CA': '加拿大', 'CN': '中国', 'HK': '香港', 'TW': '台湾',
    'JP': '日本', 'KR': '韩国', 'SG': '新加坡', 'GB': '英国', 'DE': '德国',
    'FR': '法国', 'NL': '荷兰', 'RU': '俄罗斯', 'IN': '印度', 'AU': '澳大利亚',
    'MY': '马来西亚', 'TH': '泰国', 'VN': '越南', 'ID': '印度尼西亚',
    'BR': '巴西', 'IT': '意大利', 'ES': '西班牙'
}

def fetch_ips_from_url(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        content = response.text
        # Use a generic IP regex to capture IPs from various formats
        # This handles both "📊 [x/y] IP" and "[x/y] IP" and just plain IPs
        ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
        ips = re.findall(ip_pattern, content)
        print(f"Fetched {len(ips)} IPs from {url}")
        return ips
    except Exception as e:
        print(f"Error fetching from {url}: {e}")
        return []

def fetch_and_save_ips():
    urls = [
        "https://ip.164746.xyz/ipTop10.html",
        "https://raw.githubusercontent.com/rong2er/IP666/refs/heads/main/Ranking.txt"
    ]
    
    all_ips = set()
    
    for url in urls:
        ips = fetch_ips_from_url(url)
        all_ips.update(ips)
    
    if not all_ips:
        print("No IPs found from any source.")
        return

    unique_ips = list(all_ips)
    print(f"Total unique IPs to process: {len(unique_ips)}")

    # GeoIP Lookup using ipinfo.io (Batch)
    # Token provided: 6f75ff6b8f013b
    # Batch endpoint: https://ipinfo.io/batch?token=...
    # Supports up to 1000 IPs in a single batch? 
    # Standard limitation is usually higher than ip-api.com. Let's stick to chunks of 100 for safety.
    
    formatted_ips = []
    chunk_size = 100
    token = "6f75ff6b8f013b"
    
    for i in range(0, len(unique_ips), chunk_size):
        chunk = unique_ips[i:i + chunk_size]
        api_url = f"https://ipinfo.io/batch?token={token}"
        
        try:
            # ipinfo batch expects a list of IPs or a dict of filtered lookups like {"path": "ip"}
            # It also accepts a simple list of strings for full details.
            response = requests.post(api_url, json=chunk, timeout=20)
            response.raise_for_status()
            geo_data = response.json()
            
            # geo_data is a dict: {"8.8.8.8": {...info...}}
            
            for ip in chunk:
                info = geo_data.get(ip)
                if info and 'country' in info:
                    cc = info['country']
                    # Map code to Name if possible
                    cn_name = COUNTRY_MAP.get(cc, '')
                    location = f"{cc}{cn_name}"
                    formatted_ips.append(f"{ip}:443#{location}")
                else:
                    formatted_ips.append(f"{ip}:443#Unknown")
                    
        except Exception as e:
            print(f"GeoIP lookup failed for chunk {i}: {e}")
            # Fallback for this chunk
            for ip in chunk:
                formatted_ips.append(f"{ip}:443#Unknown")

    output_content = "\n".join(formatted_ips)
    
    with open("ip.txt", "w") as f:
        f.write(output_content)
        
    print(f"Successfully saved {len(formatted_ips)} IPs to ip.txt with geolocation.")

if __name__ == "__main__":
    fetch_and_save_ips()
