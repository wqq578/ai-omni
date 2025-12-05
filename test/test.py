import requests
import os
from datetime import datetime

def download_with_progress(url, filename):
    """带进度显示的下载函数"""
    try:
        print("📡 正在发送请求... (设置超时30秒)")
        response = requests.get(url, timeout=30, stream=True)
        print(f"📊 状态码: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ 请求失败，状态码: {response.status_code}")
            print(f"📝 响应内容: {response.text[:200]}...")
            return False
        
        # 检查内容类型
        content_type = response.headers.get('content-type', '')
        print(f"📄 内容类型: {content_type}")
        
        # 获取文件大小
        total_size = int(response.headers.get('content-length', 0))
        if total_size == 0:
            # 如果无法获取文件大小，先下载到内存
            print("📥 正在下载文件...")
            content = response.content
            total_size = len(content)
            print(f"📦 文件大小: {total_size} 字节 ({total_size/1024/1024:.2f} MB)")
            
            print("💾 正在保存文件...")
            with open(filename, 'wb') as f:
                f.write(content)
        else:
            print(f"📦 文件大小: {total_size} 字节 ({total_size/1024/1024:.2f} MB)")
            print("📥 开始下载...")
            
            downloaded = 0
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        # 显示进度
                        if total_size > 0:
                            percent = (downloaded / total_size) * 100
                            print(f"\r📥 下载进度: {percent:.1f}% ({downloaded}/{total_size} 字节)", end='', flush=True)
            
            print()  # 换行
        
        # 检查文件是否成功保存
        try:
            if os.path.exists(filename):
                saved_size = os.path.getsize(filename)
                print(f"✅ PDF 下载成功！")
                print(f"📄 文件名: {filename}")
                print(f"📊 实际保存大小: {saved_size} 字节 ({saved_size/1024/1024:.2f} MB)")
                return True
            else:
                print("❌ 文件保存失败 - 文件不存在")
                return False
        except Exception as e:
            print(f"❌ 文件检查失败: {e}")
            return False
            
    except Exception as e:
        print(f"\n❌ 下载过程中出现错误: {e}")
        return False

# 目标PDF的URL
url = "https://arxiv.org/pdf/1911.09750v2.pdf"

# 本地保存的文件名
filename = "paper_1911.09750v2.pdf"

print(f"📥 开始下载PDF文件...")
print(f"🌐 目标URL: {url}")
print(f"📂 保存位置: {filename}")
print(f"🕒 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# 发送GET请求下载PDF
try:
    success = download_with_progress(url, filename)
    if success:
        print(f"🕒 完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        print("❌ 下载失败")

except requests.exceptions.Timeout:
    print("⏰ 请求超时，请检查网络连接或增加超时时间")
except requests.exceptions.ConnectionError:
    print("� 连接错误，请检查网络连接")
except requests.exceptions.RequestException as e:
    print(f"❌ 下载失败: {e}")
except Exception as e:
    print(f"❌ 其他错误: {e}")

print("🏁 脚本执行完成")
