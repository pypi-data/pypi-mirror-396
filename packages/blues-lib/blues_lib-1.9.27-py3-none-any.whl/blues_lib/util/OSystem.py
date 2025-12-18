import sys

class OSystem():

  @classmethod
  def get_os_type(cls):
    is_windows = sys.platform.startswith('win')
    is_linux = sys.platform.startswith('linux')
    is_mac = sys.platform.startswith('darwin')
    if is_windows:
      return 'windows'
    elif is_linux:
      return 'linux'
    elif is_mac:
      return 'mac'
    else:
      return 'unknown'
 