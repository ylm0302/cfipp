import requests
import re
import json

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

    # GeoIP Lookup using ip-api.com (Batch)
    # The API supports up to 100 IPs per batch. We need to chunk if > 100.
    # User examples show ~38 per file, so ~76 total, likely < 100.
    # But for safety, let's process in chunks of 100.
    
    formatted_ips = []
    chunk_size = 100
    
    for i in range(0, len(unique_ips), chunk_size):
        chunk = unique_ips[i:i + chunk_size]
        api_url = "http://ip-api.com/batch?fields=query,countryCode,country&lang=zh-CN"
        
        try:
            geo_response = requests.post(api_url, json=chunk, timeout=20)
            geo_response.raise_for_status()
            geo_data = geo_response.json()
            
            # Map IP to Geo info
            ip_map = {item['query']: item for item in geo_data}
            
            for ip in chunk:
                geo = ip_map.get(ip)
                if geo and 'countryCode' in geo and 'country' in geo:
                    location = f"{geo['countryCode']}{geo['country']}"
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
