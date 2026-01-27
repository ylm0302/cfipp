import requests
import re
import json

def fetch_ips_from_url(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        content = response.text
        # Use a combined regex to capture IPs in order of appearance
        # IPv4 pattern | IPv6 pattern
        ip_pattern = r'(?:\d{1,3}\.){3}\d{1,3}|(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}'
        
        matches = re.finditer(ip_pattern, content)
        all_found_ips = [m.group(0) for m in matches]
        
        # Filter valid IPs (simple regex might catch version numbers, though specific patterns helps)
        # The previous patterns were wrapped in \b, let's restore that for safety
        ipv4_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
        ipv6_pattern = r'\b(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}\b'
        
        final_ips = []
        for item in all_found_ips:
            if re.match(ipv4_pattern, item) or re.match(ipv6_pattern, item):
                final_ips.append(item)
        
        print(f"Fetched {len(final_ips)} IPs from {url}")
        return final_ips
    except Exception as e:
        print(f"Error fetching from {url}: {e}")
        return []

def fetch_and_save_ips():
    urls = [
        "https://ip.164746.xyz/ipTop10.html",
        # "https://raw.githubusercontent.com/rong2er/IP666/refs/heads/main/Ranking.txt",
        # "https://ipdb.api.030101.xyz/?type=bestcf&country=true",
        "https://api.uouin.com/cloudflare.html"
    ]
    
    # Use a list to preserve insertion order if we want to prioritize
    # specific high-quality sources, but 'set' is used for uniqueness.
    # We will simply add them to a list first.
    collected_ips = []
    
    for url in urls:
        ips = fetch_ips_from_url(url)
        
        # User request: Get top 30 fastest IPs from api.uouin.com/cloudflare.html
        # The source is sorted by speed, so we take the first 30.
        if "api.uouin.com/cloudflare.html" in url:
            print("Limiting uouin.com result to top 30 fastest IPs.")
            ips = ips[:40]
            
        collected_ips.extend(ips)
    
    # Remove duplicates while preserving order (optional, but good for stability)
    unique_ips = []
    seen = set()
    for ip in collected_ips:
        if ip not in seen:
            unique_ips.append(ip)
            seen.add(ip)
    # Remove duplicates while preserving order (optional, but good for stability)
    unique_ips = []
    seen = set()
    for ip in collected_ips:
        if ip not in seen:
            unique_ips.append(ip)
            seen.add(ip)
    
    import time
    import socket

    print(f"Total unique IPs to process: {len(unique_ips)}")

    # GeoIP Lookup using ip-api.com (return country code only)
    # URL: http://ip-api.com/line/{ip}?fields=countryCode
    
    formatted_ips = []
    
    print("Starting Country Code lookup and Speed Test...")
    
    def get_country_code(ip):
        try:
            # ip-api.com free tier: 45 requests per minute
            # Using 'line' format for minimal bandwidth
            url = f'http://ip-api.com/line/{ip}?fields=countryCode'
            resp = requests.get(url, timeout=5)
            if resp.status_code == 200:
                # The API returns the country code simply as text, e.g., "US"
                # Strip specifically removes newlines
                return resp.text.strip() or 'ZZ'
            else:
                return 'ZZ'
        except Exception as e:
            print(f"Failed to query country_code for IP {ip}: {e}")
            return 'ZZ'

    def get_tcp_latency(ip, port=443, timeout=3):
        """
        Measure TCP latency to a specific IP and port.
        Returns latency in milliseconds (int) or None if failed.
        """
        try:
            start_time = time.time()
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            sock.connect((ip, port))
            end_time = time.time()
            sock.close()
            latency = int((end_time - start_time) * 1000)
            return latency
        except Exception:
            return None

    for i, ip in enumerate(unique_ips):
        # Add delay to respect rate limit (45 req/min => ~1.33s per req)
        # To be safe, we'll use 1.5 seconds delay between requests
        if i > 0:
            time.sleep(1.5)
            
        country_code = get_country_code(ip)
        latency = get_tcp_latency(ip)
        
        # Format speed string
        speed_str = f"_{latency}ms" if latency is not None else "_Timeout"
        
        print(f"IP: {ip} -> {country_code} | Latency: {latency}ms")
        formatted_ips.append(f"{ip}:443#{country_code}{speed_str}")

    output_content = "\n".join(formatted_ips)
    
    with open("ip.txt", "w") as f:
        f.write(output_content)
        
    print(f"Successfully saved {len(formatted_ips)} IPs to ip.txt with country codes and speed.")

if __name__ == "__main__":
    fetch_and_save_ips()
