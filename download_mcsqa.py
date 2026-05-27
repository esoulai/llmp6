import os
import requests

proxies = {
    'https': 'http://127.0.0.1:7897',
    'http': 'http://127.0.0.1:7897'
}

base_url = 'https://hf-mirror.com/yusuke1997/mCSQA/resolve/main'
files = ['train.parquet', 'test.parquet', 'dev.parquet']

os.makedirs('experiments/data/mCSQA', exist_ok=True)

for f in files:
    url = f'{base_url}/{f}'
    print(f'下载: {url}')
    try:
        response = requests.get(url, proxies=proxies, timeout=60, stream=True)
        print(f'  状态码: {response.status_code}')
        if response.status_code == 200:
            filepath = f'experiments/data/mCSQA/{f}'
            with open(filepath, 'wb') as wf:
                for chunk in response.iter_content(chunk_size=8192):
                    wf.write(chunk)
            size = os.path.getsize(filepath)
            print(f'  ✅ 保存到: {filepath} ({size} bytes)')
        else:
            print(f'  ❌ 下载失败')
    except Exception as e:
        print(f'  ❌ 错误: {e}')
    print()