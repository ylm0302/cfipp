import requests
from bs4 import BeautifulSoup

def get_ip():
    """
    从指定的 URL 解析 HTML，并获取第一个带星号的优选 IP 地址。
    """
    url = "https://ip.164746.xyz/"
    try:
        response = requests.get(url)
        response.raise_for_status()  # 确保请求成功
        
        # 使用 BeautifulSoup 解析 HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 寻找表格中的所有行
        rows = soup.find_all('tr')
        
        # 遍历每一行，寻找以 '★' 开头的行
        for row in rows:
            if row.text.strip().startswith('★'):
                # 提取该行的所有单元格
                cells = row.find_all('td')
                if len(cells) > 0:
                    # IP 地址通常是第一个有效数据，但这里根据页面结构，它在第一个单元格的文本中
                    # 文本内容是 "★ 172.64.53.248"，需要分割
                    ip_address = cells[0].text.strip().split(' ')[1]
                    print(f"成功获取优选 IP 地址: {ip_address}")
                    return ip_address
                    
        print("未找到带星号的优选 IP。")
        return None

    except requests.exceptions.RequestException as e:
        print(f"获取 IP 地址时发生错误: {e}")
        return None
    except Exception as e:
        print(f"解析 HTML 或提取 IP 时发生错误: {e}")
        return None


def save_ip_to_file(ip_address, filename="ip.txt"):
    """
    将 IP 地址保存到文件中。
    """
    if ip_address:
        with open(filename, "w") as f:
            f.write(ip_address)
        print(f"IP 地址已成功保存到 {filename}")

if __name__ == "__main__":
    ip = get_ip()
    save_ip_to_file(ip)
