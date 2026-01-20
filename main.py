import requests
from bs4 import BeautifulSoup

def get_ip():
    """
    从指定的 URL 解析 HTML，并获取第一个优选 IP 地址。
    此版本更健壮，可以处理星号和 IP 在不同单元格中的情况。
    """
    url = "https://ip.164746.xyz/"
    try:
        response = requests.get(url, timeout=10) # 增加超时设置
        response.raise_for_status()  # 确保请求成功
        
        soup = BeautifulSoup(response.text, 'lxml') # 使用 lxml 解析器
        
        # 寻找表格主体中的所有行
        # 假设数据在 <tbody> 标签内，这可以帮助避开表头
        table_body = soup.find('tbody')
        if not table_body:
            # 如果没有 tbody, 就退回到查找整个 table
            table = soup.find('table')
            if not table:
                print("错误：在页面上未找到 <table>。")
                return None
            rows = table.find_all('tr')
        else:
            rows = table_body.find_all('tr')

        # 遍历每一行
        for row in rows:
            cells = row.find_all('td')
            # 确保行中有足够的单元格，并且第一个单元格包含星号
            if len(cells) > 1 and '★' in cells[0].text:
                # IP 地址现在被假定在第二个单元格中
                ip_address = cells[1].text.strip()
                # 确认提取的字符串看起来像一个 IP
                if '.' in ip_address:
                    print(f"成功获取优选 IP 地址: {ip_address}")
                    return ip_address
                    
        print("未在表格中找到带星号的优选 IP。")
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

