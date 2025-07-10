import requests
import concurrent.futures
import time, sys

# Đọc proxy từ file
def load_proxies_from_file(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]

# Lấy quốc gia của IP
def get_country(ip):
    try:
        r = requests.get(f"http://ip-api.com/json/{ip}", timeout=2)
        data = r.json()
        return data.get("country", "Unknown")
    except:
        return "Unknown"

# Hàm kiểm tra proxy
def check_proxy(proxy_raw):
    proxy_url = f"http://{proxy_raw}"
    try:
        start = time.time()
        response = requests.get(
            "http://httpbin.org/ip",
            proxies={"http":proxy_url,
                     "https":proxy_url},
            timeout=3
        )
        elapsed = (time.time() - start) * 1000  # ms
        if response.status_code == 200:
            ip = response.json().get("origin", "")
            country = get_country(ip)
            speed = round(elapsed, 2)
            print(f"[OK] {proxy_raw} - {speed} ms - 🌍 {country}")
            if speed < 5000:
                return proxy_raw, speed, country
        else:
            print(f"[FAIL] {proxy_raw} - Status: {response.status_code}")
    except:
        print(f"[ERR] {proxy_raw} - Timeout/Error")
    return None

# Kiểm tra song song
def filter_fast_proxies(proxy_list):
    fast_proxies = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=300) as executor:
        results = executor.map(check_proxy, proxy_list)
        for result in results:
            if result:
                fast_proxies.append(result)
    return fast_proxies

# Ghi ra file
def save_to_file(proxy_list, filename="proxy.txt"):
    with open(filename, 'w') as f:
        for proxy, speed, country in proxy_list:
            f.write(f"{proxy}\n")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Sử dụng: python proxyScan.py {input.txt} {output.txt}")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    print(f"🧪 Đang kiểm tra proxy từ '{input_file}'...\n")
    proxies = load_proxies_from_file(input_file)
    fast_ones = filter_fast_proxies(proxies)

    print(f"\n✅ Proxy phản hồi < 5000ms:")
    for proxy, speed, country in fast_ones:
        print(f"{proxy} - {speed} ms - 🌍 {country}")

    save_to_file(fast_ones, output_file)
    print(f"\n💾 Đã lưu {len(fast_ones)} proxy vào '{output_file}'")