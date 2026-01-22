import requests
import re

def fetch_and_save_ips():
    url = "https://ip.164746.xyz/ipTop10.html"
    try:
        response = requests.get(url)
        response.raise_for_status()
        content = response.text
        
        # The user described the format as a comma separated list in the content
        # Example: 172.64.53.208,108.162.198.188,...
        # We can extract all IPs using regex to be safe and robust
        ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
        ips = re.findall(ip_pattern, content)
        
        if not ips:
            print("No IPs found in the response.")
            return

        formatted_ips = []
        for ip in ips:
            formatted_ips.append(f"{ip}:443#US")
        
        # Join with newlines or just write them? 
        # The user said "combine ip:443#US", usually these lists are one per line or separated.
        # Given "put into ip.txt", standard list format is usually newline separated.
        # "all combination data" -> let's put one per line as it's cleaner for most tools.
        output_content = "\n".join(formatted_ips)
        
        with open("ip.txt", "w") as f:
            f.write(output_content)
            
        print(f"Successfully saved {len(formatted_ips)} IPs to ip.txt")
        
    except Exception as e:
        print(f"Error occurred: {e}")

if __name__ == "__main__":
    fetch_and_save_ips()
