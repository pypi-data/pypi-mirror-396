import os
import platform
import requests
import zipfile
import shutil
import json
from blues_lib.util.BluesFiler import BluesFiler

class CFTInstaller:
  '''
  Chrome for testing: https://googlechromelabs.github.io/chrome-for-testing/#stable
  此网页由google官方提供了国内可直接下载的 chrome chromedriver chrome-headless-shell zip下载链接
  - chrome不会自动升级
  - chromedriver与chrome版本号一致且完全匹配
  - 国内可以直接下载

  比如：Version: 141.0.7390.54 (r1509326)
  chrome下载地址：
  linux64 https://storage.googleapis.com/chrome-for-testing-public/141.0.7390.54/linux64/chrome-linux64.zip
  mac-arm64	https://storage.googleapis.com/chrome-for-testing-public/141.0.7390.54/mac-arm64/chrome-mac-arm64.zip
  mac-x64	https://storage.googleapis.com/chrome-for-testing-public/141.0.7390.54/mac-x64/chrome-mac-x64.zip
  win64	https://storage.googleapis.com/chrome-for-testing-public/141.0.7390.54/win64/chrome-win64.zip
  win32	https://storage.googleapis.com/chrome-for-testing-public/141.0.7390.54/win32/chrome-win32.zip
  
  chromedriver下载地址：
  linux64	https://storage.googleapis.com/chrome-for-testing-public/141.0.7390.54/linux64/chromedriver-linux64.zip
  mac-arm64	https://storage.googleapis.com/chrome-for-testing-public/141.0.7390.54/mac-arm64/chromedriver-mac-arm64.zip
  mac-x64	https://storage.googleapis.com/chrome-for-testing-public/141.0.7390.54/mac-x64/chromedriver-mac-x64.zip
  win64	https://storage.googleapis.com/chrome-for-testing-public/141.0.7390.54/win64/chromedriver-win64.zip
  win32	https://storage.googleapis.com/chrome-for-testing-public/141.0.7390.54/win32/chromedriver-win32.zip
  
  可以看到地址格式是规范的，只要有2个变量：
  - 系统
  - 版本号
  可以基于这些固定的下载地址，创建方法，按照版本号和系统下载到指定目录。
  '''

  _VERSION = '141.0.7390.54' # 下载目标版本
  _LOCATION = os.environ.get('SELENIUM_CFT') or BluesFiler.get_cft_path()
  # official download url
  _OFFICIAL_URL = 'https://storage.googleapis.com/chrome-for-testing-public'
  # 国内镜像地址（来自npmmirror镜像站）
  _MIRROR_URL = 'https://npmmirror.com/mirrors/chrome-for-testing'

  @classmethod
  def _check_installed(cls, version: str, location: str, os_type: str) -> tuple[bool, dict]:
    '''检查是否已存在相同版本的安装'''    
    installed_json_path = os.path.join(location, 'installed.json')
    if os.path.exists(installed_json_path):
      try:
        with open(installed_json_path, 'r', encoding='utf-8') as f:
          installed_info = json.load(f)
        
        # 检查版本是否一致，并且可执行文件是否存在
        if (installed_info.get('version') == version and 
            installed_info.get('os') == os_type and 
            os.path.exists(installed_info.get('chrome_path', '')) and 
            os.path.exists(installed_info.get('driver_path', ''))):
          return True, installed_info
      except (json.JSONDecodeError, Exception) as e:
        print(f"读取installed.json文件失败: {str(e)}，将重新安装。")
    return False, {}
  
  @classmethod
  def _create_or_clean_dir(cls, location: str) -> None:
    '''创建目录'''    
    if not os.path.exists(location):
      os.makedirs(location, exist_ok=True)
    else:
      cls._clean_dir(location)
      
  @classmethod  
  def _clean_dir(cls, location: str) -> None:
    '''清空目录'''    
    print(f"清空安装目录: {location}")
    for item in os.listdir(location):
      item_path = os.path.join(location, item)
      if os.path.isfile(item_path):
        os.remove(item_path)
      elif os.path.isdir(item_path):
        shutil.rmtree(item_path)
        
  @classmethod
  def _save_install_info(cls, location: str, install_info: dict) -> None:
    '''保存安装信息到json文件'''    
    installed_json_path = os.path.join(location, 'installed.json')
    try:
      with open(installed_json_path, 'w', encoding='utf-8') as f:
        json.dump(install_info, f, ensure_ascii=False, indent=2)
      print(f"已将安装信息保存到 {installed_json_path}")
    except Exception as e:
      print(f"保存installed.json文件失败: {str(e)}")
      
  @classmethod
  def install(cls, version: str = '', location: str = '') -> dict:
    f'''
    根据系统/版本下载chrome和chromedriver到指定目录

    @param {str} version : 版本号，如果为空使用 _VERSION
    @param {str} location : 下载目录的决定路径，如果为空使用 _LOCATION
    
    @returns {dict} : 包含安装路径信息的字典
    '''
    try:
      # 使用提供的值或默认值
      version = version if version else cls._VERSION
      location = location if location else cls._LOCATION
      os_type = cls.get_os()
      
      # 验证系统类型
      valid_os_types = ['linux64', 'win64', 'win32', 'mac-x64', 'mac-arm64']
      if os_type not in valid_os_types:
        raise ValueError(f"不支持的系统类型: {os_type}")
      
      # 检查是否已经安装过相同版本
      is_installed, installed_info = cls._check_installed(version, location, os_type)
      if is_installed:
        print(f"已检测到版本 {version} 的Chrome和ChromeDriver已安装，直接返回安装信息。")
        return installed_info
      
      # 创建下载目录或清空目录
      cls._create_or_clean_dir(location)

      # 构建下载URL - 优先使用国内镜像地址
      print(f"使用国内镜像地址下载: {cls._MIRROR_URL}")
      chrome_url = f"{cls._MIRROR_URL}/{version}/{os_type}/chrome-{os_type}.zip"
      driver_url = f"{cls._MIRROR_URL}/{version}/{os_type}/chromedriver-{os_type}.zip"
      
      # 下载并解压Chrome
      chrome_dir = os.path.join(location, f"chrome-{os_type}")
      cls._download_extract(chrome_url, location, f"chrome-{os_type}.zip", chrome_dir)
      
      # 下载并解压ChromeDriver
      driver_dir = os.path.join(location, f"chromedriver-{os_type}")
      cls._download_extract(driver_url, location, f"chromedriver-{os_type}.zip", driver_dir)
      
      # 查找可执行文件
      chrome_exe = cls._find_exe(chrome_dir, "chrome")
      driver_exe = cls._find_exe(driver_dir, "chromedriver")
      
      # 构建安装信息
      install_info = {
        'location': location,
        'version': version,
        'os': os_type,
        'chrome_path': chrome_exe,
        'driver_path': driver_exe
      }
      
      # 保存安装信息
      cls._save_install_info(location, install_info)
      
      return install_info
      
    except Exception as e:
      print(f"安装失败: {str(e)}")
      return {
        'error': str(e)
      }
  
  @classmethod
  def get_os(cls)->str:
    f'''
    获取当前系统标识: 可用值有：linux64 win64 win32 mac-x64 mac-arm64
    @returns {str} : 系统标识字符串
    '''
    system = platform.system().lower()
    architecture = platform.architecture()[0]
    machine = platform.machine().lower()
    
    # 处理Windows系统
    if system == 'windows':
      if '64' in architecture or 'amd64' in machine or 'x86_64' in machine:
        return 'win64'
      else:
        return 'win32'
    
    # 处理macOS系统
    elif system == 'darwin':
      if 'arm' in machine or 'aarch64' in machine:
        return 'mac-arm64'
      else:
        return 'mac-x64'
    
    # 处理Linux系统
    elif system == 'linux':
      if '64' in architecture or 'amd64' in machine or 'x86_64' in machine:
        return 'linux64'
      else:
        # 假设Linux只有64位版本可用
        return 'linux64'
    
    # 不支持的系统
    else:
      raise NotImplementedError(f"不支持的操作系统: {system}")
  
  @classmethod
  def _download_extract(cls, url: str, save_dir: str, zip_filename: str, extract_dir: str):
    '''下载并解压文件'''    
    # 下载文件
    zip_path = os.path.join(save_dir, zip_filename)
    print(f"下载 {url} 到 {zip_path}")
    
    response = requests.get(url, stream=True)
    response.raise_for_status()
    
    with open(zip_path, 'wb') as f:
      for chunk in response.iter_content(chunk_size=8192):
        f.write(chunk)
    
    # 解压文件
    print(f"解压 {zip_path} 到 {extract_dir}")
    
    if os.path.exists(extract_dir):
      shutil.rmtree(extract_dir)
    
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
      zip_ref.extractall(save_dir)
    
    # 清理zip文件
    os.remove(zip_path)
  
  @classmethod
  def _find_exe(cls, directory: str, base_name: str) -> str:
    '''在目录中查找可执行文件'''
    
    is_windows = platform.system() == 'Windows'
    is_macos = platform.system() == 'Darwin'
    extension = '.exe' if is_windows else ''
    
    print(f"正在查找 {base_name} 可执行文件，目录: {directory}")
    
    # 首先检查目录是否存在
    if not os.path.exists(directory):
      print(f"警告: 目录 {directory} 不存在")
      # 尝试使用绝对路径
      if os.path.exists(os.path.abspath(directory)):
        directory = os.path.abspath(directory)
        print(f"尝试使用绝对路径: {directory}")
    
    # 首先检查是否直接提供了完整路径
    if os.path.exists(directory) and os.path.isfile(directory) and os.access(directory, os.X_OK):
      print(f"找到可执行文件: {directory}")
      return directory
    
    # 定义可能的文件名模式，特别是针对Chrome for Testing
    possible_names = []
    if base_name == 'chrome':
      # Chrome可能的文件名变体
      possible_names = [
        'chrome', 'Google Chrome', 'Google Chrome for Testing', 
        'chrome.exe', 'Google Chrome.exe', 'Google Chrome for Testing.exe'
      ]
    elif base_name == 'chromedriver':
      # Chromedriver可能的文件名变体
      possible_names = [
        'chromedriver', 'chromedriver.exe'
      ]
    else:
      # 其他情况使用基本名称
      possible_names = [base_name, base_name + extension]
    
    # 遍历目录查找文件
    found_files = []
    for root, _, files in os.walk(directory):
      for file in files:
        # 记录所有找到的文件用于调试
        found_files.append(os.path.join(root, file))
        
        # 检查是否匹配任何可能的文件名模式（不区分大小写）
        file_lower = file.lower()
        for possible_name in possible_names:
          if file_lower == possible_name.lower():
            exe_path = os.path.join(root, file)
            # 在非Windows系统上设置可执行权限
            if not is_windows:
              try:
                os.chmod(exe_path, 0o755)
                # 对于macOS上的Chrome应用，还需要确保整个应用包有正确的权限
                if is_macos and base_name == 'chrome':
                  # 获取应用包的根目录
                  app_bundle_path = exe_path.split('/Contents/MacOS/')[0]
                  if app_bundle_path.endswith('.app'):
                    print(f"设置应用包 {app_bundle_path} 的权限")
                    # 递归设置应用包的权限
                    for app_root, _, app_files in os.walk(app_bundle_path):
                      for app_file in app_files:
                        try:
                          os.chmod(os.path.join(app_root, app_file), 0o755)
                        except (OSError, PermissionError):
                          pass  # 忽略无法设置权限的文件
              except (OSError, PermissionError) as e:
                print(f"警告: 无法设置 {exe_path} 的可执行权限: {str(e)}")
            print(f"找到可执行文件: {exe_path}")
            return exe_path
    
    # 调试信息：打印找到的所有文件
    print(f"在目录 {directory} 中找到的文件列表:")
    for i, file_path in enumerate(found_files[:10]):  # 只打印前10个文件
      print(f"  {i+1}. {file_path}")
    if len(found_files) > 10:
      print(f"  ... 还有 {len(found_files) - 10} 个文件未显示")
    
    # 对于Chrome for Testing，尝试特定的路径模式
    if base_name == 'chrome' and is_macos:
      # 从调试输出中看到的实际路径模式
      chrome_testing_paths = [
        os.path.join(directory, 'Google Chrome for Testing.app', 'Contents', 'MacOS', 'Google Chrome for Testing'),
        os.path.join(directory, 'chrome-mac-x64', 'Google Chrome for Testing.app', 'Contents', 'MacOS', 'Google Chrome for Testing'),
        os.path.join(directory, 'chrome-mac-arm64', 'Google Chrome for Testing.app', 'Contents', 'MacOS', 'Google Chrome for Testing'),
        # 其他可能的变体
        os.path.join(directory, 'Chrome.app', 'Contents', 'MacOS', 'Chrome'),
        os.path.join(directory, 'Google Chrome.app', 'Contents', 'MacOS', 'Google Chrome')
      ]
      for path in chrome_testing_paths:
        if os.path.exists(path):
          print(f"在macOS特定路径找到Chrome for Testing: {path}")
          # 确保有可执行权限
          if not is_windows:
            try:
              os.chmod(path, 0o755)
            except (OSError, PermissionError):
              pass
          return path
    
    # 对于chromedriver，尝试特定的路径模式
    if base_name == 'chromedriver':
      driver_paths = [
        os.path.join(directory, 'chromedriver'),
        os.path.join(directory, 'chromedriver-mac-x64', 'chromedriver'),
        os.path.join(directory, 'chromedriver-mac-arm64', 'chromedriver'),
        os.path.join(directory, 'chromedriver.exe'),
        os.path.join(directory, 'chromedriver-mac-x64', 'chromedriver.exe'),
        os.path.join(directory, 'chromedriver-mac-arm64', 'chromedriver.exe')
      ]
      for path in driver_paths:
        if os.path.exists(path):
          print(f"找到chromedriver: {path}")
          # 确保有可执行权限
          if not is_windows:
            try:
              os.chmod(path, 0o755)
            except (OSError, PermissionError):
              pass
          return path
    
    raise FileNotFoundError(f"未找到 {base_name} 可执行文件")
    
  @classmethod
  def get_chrome_launch_args(cls) -> list:
    '''
    获取运行Chrome for Testing所需的启动参数
    这些参数可以解决GPU相关的崩溃问题
    
    关于Windows不遇到GPU问题的说明：
    1. Windows和macOS的GPU处理架构不同，Windows上的Chrome通常有更好的兼容性
    2. Windows上的GPU驱动通常更稳定，与Chrome的交互问题较少
    3. macOS的Metal图形API与Chrome的集成在某些版本可能存在兼容性问题
    4. 在无头服务器环境中，Windows通常不会尝试初始化真实GPU，而macOS可能会尝试
    5. Windows上的Chrome for Testing版本通常经过更好的优化测试
    '''
    if platform.system() == 'Darwin':
      return [
        # --no-sandbox: 禁用沙箱模式，在macOS上运行Chrome for Testing时通常必需
        # 沙箱在某些权限受限的环境中可能导致启动失败
        '--no-sandbox',
        
        # --disable-gpu: 禁用GPU加速，解决GPU进程崩溃问题
        # 在macOS上，特别是在虚拟环境或无头模式下，GPU初始化可能失败
        '--disable-gpu',
        
        # --disable-software-rasterizer: 禁用软件光栅化器
        # 当GPU被禁用时，Chrome会使用软件渲染，此参数可以避免某些渲染问题
        '--disable-software-rasterizer',
        
        # --disable-dev-shm-usage: 禁用使用/dev/shm
        # 在某些Linux和macOS环境中，/dev/shm空间不足可能导致Chrome崩溃
        '--disable-dev-shm-usage',
        
        # --disable-features=Metal: 禁用Metal图形API
        # macOS上的Metal API与某些版本的Chrome存在兼容性问题，禁用可以避免崩溃
        '--disable-features=Metal',
        
        # --disable-features=VizDisplayCompositor: 禁用Viz显示合成器
        # 这是Chrome的新显示合成器，在某些环境中可能不稳定
        '--disable-features=VizDisplayCompositor',
        
        # --remote-debugging-port=9222: 启用远程调试端口
        # 方便调试和监控Chrome实例
        '--remote-debugging-port=9222'
      ]
    else:  # Windows和其他系统
      return [
        # --no-sandbox: 在某些环境中禁用沙箱以避免权限问题
        '--no-sandbox',
        
        # --disable-dev-shm-usage: 解决共享内存问题
        # 主要针对Linux环境，但也可能在某些Windows环境中有所帮助
        '--disable-dev-shm-usage'
        # Windows通常不需要额外的GPU相关参数，因为其GPU处理架构更加稳定
      ]
    
  @classmethod
  def create_selenium_options(cls, options=None) -> 'webdriver.ChromeOptions':
    '''
    创建配置了正确启动参数的Selenium ChromeOptions对象
    @param options: 已有的ChromeOptions对象（可选）
    @return: 配置好的ChromeOptions对象
    '''
    try:
      from selenium import webdriver
      
      if options is None:
        options = webdriver.ChromeOptions()
      
      # 添加必要的启动参数
      for arg in cls.get_chrome_launch_args():
        options.add_argument(arg)
      
      # 在无头模式下运行（可选）
      # options.add_argument('--headless')
      
      return options
    except ImportError:
      print("警告: 未安装selenium库，无法创建ChromeOptions对象")
      return None