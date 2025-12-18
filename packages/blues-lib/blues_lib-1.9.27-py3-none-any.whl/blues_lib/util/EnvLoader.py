import os
import platform
from dotenv import load_dotenv

class EnvLoader:
  """
  Environment variable loader, used to load environment variable configuration files in the project
  Supports loading common configuration files and system-specific configuration files

  os.environ 本质是 Python 进程启动时创建的一个全局字典，用于存储当前进程的所有环境变量（包括系统环境变量和 load_dotenv() 注入的 .env 配置）。
  这个字典的关键特性是：一旦在某个模块中被修改（比如 load_dotenv() 往里面添加了新键值对），所有其他模块通过 import os 访问到的 os.environ 都是同一个对象—— 就像一个 “共享的白板”，任何模块写的内容，其他模块都能看到。
  因此，你只需要在程序启动的最早阶段（主文件开头） 执行一次 load_dotenv()，就能让整个项目的所有模块共享这份配置。
  """
  
  # Private static fields for environment file names
  __BASE_ENV_FILE = ".env"
  __WINDOWS_ENV_FILE = ".env.windows"
  __MACOS_ENV_FILE = ".env.macos"
  
  # Static variable to track if environment has been loaded
  __is_loaded = False
  
  @classmethod
  def load(cls):
    """
    Load environment variable configuration files.
    First load .env file, then load system-specific configuration file based on current OS.
    System-specific configuration will override common configuration.
    
    @return {bool} - Whether at least one configuration file was successfully loaded
    """
    # Check if already loaded
    if cls.__is_loaded:
      print("Environment variables already loaded. Skipping reloading.")
      return True
      
    loaded = False
    
    # 1. Load common configuration
    if os.path.exists(cls.__BASE_ENV_FILE):
      load_dotenv(cls.__BASE_ENV_FILE)
      loaded = True
      print(f"Loaded base configuration file: {cls.__BASE_ENV_FILE}")
    else:
      print(f"Warning: Base configuration file {cls.__BASE_ENV_FILE} not found.")
    
    # 2. Dynamically detect OS and load system-specific configuration
    os_name = platform.system()
    if os_name == "Windows":
      env_file = cls.__WINDOWS_ENV_FILE
    elif os_name == "Darwin":  # macOS
      env_file = cls.__MACOS_ENV_FILE
    else:
      print(f"Warning: Unsupported operating system type {os_name}.")
      # Mark as loaded after successful execution
      cls.__is_loaded = True
      return loaded
    
    if os.path.exists(env_file):
      load_dotenv(env_file, override=True)  # override=True ensures system configuration can override base configuration
      loaded = True
      print(f"Loaded and overridden system configuration file: {env_file}")
    else:
      print(f"Warning: System configuration file {env_file} not found.")
    
    # Mark as loaded after successful execution
    cls.__is_loaded = True
    return loaded