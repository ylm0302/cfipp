import requests
import re
import json

def fetch_ips_from_url(url):
    try:
        response = requests.get(url, timeout=50)
        response.raise_for_status()
        content = response.text
        # Use regex to capture both IPv4 and IPv6 addresses
        # IPv4 pattern: matches standard IPv4 addresses
        ipv4_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
        # IPv6 pattern: matches standard IPv6 addresses
        ipv6_pattern = r'\b(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}\b'
        
        ips = re.findall(ipv4_pattern, content)
        ipv6s = re.findall(ipv6_pattern, content)
        
        # Combine both IPv4 and IPv6 addresses
        all_ips = ips + ipv6s
        print(f"Fetched {len(all_ips)} IPs ({len(ips)} IPv4, {len(ipv6s)} IPv6) from {url}")
        return all_ips
    except Exception as e:
        print(f"Error fetching from {url}: {e}")
        return []

def fetch_and_save_ips():
    urls = [
        "https://ip.164746.xyz/ipTop10.html",
        "https://raw.githubusercontent.com/rong2er/IP666/refs/heads/main/Ranking.txt",
        "https://ipdb.api.030101.xyz/?type=bestcf&country=true"
       # "https://api.uouin.com/cloudflare.html"
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

    # GeoIP Lookup using ip-api.com (Single query)
    # Free version only supports single queries, not batch.
    # We'll query each IP individually with a small delay to avoid rate limiting.
    
    formatted_ips = []
    
    for ip in unique_ips:
        api_url = f"http://ip-api.com/json/{ip}"
        
        try:
            geo_response = requests.get(api_url, timeout=50)
            geo_response.raise_for_status()
            geo_data = geo_response.json()
            
            if geo_data and 'countryCode' in geo_data and 'country' in geo_data:
                location = f"{geo_data['countryCode']}{geo_data['country']}"
                formatted_ips.append(f"{ip}:443#{location}")
            else:
                formatted_ips.append(f"{ip}:443#Unknown")
                
        except Exception as e:
            print(f"GeoIP lookup failed for {ip}: {e}")
            formatted_ips.append(f"{ip}:443#Unknown")

    output_content = "\n".join(formatted_ips)
    
    with open("ip.txt", "w") as f:
        f.write(output_content)
        
    print(f"Successfully saved {len(formatted_ips)} IPs to ip.txt with geolocation.")

if __name__ == "__main__":
    fetch_and_save_ips()
