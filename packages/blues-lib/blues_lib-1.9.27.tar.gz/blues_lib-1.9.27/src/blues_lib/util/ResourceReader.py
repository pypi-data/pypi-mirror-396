from importlib import resources
from blues_lib.util.FileReader import FileReader

class ResourceReader:
  """
  Universal package resource reader supporting JSON/JSON5/YAML formats.
  Accepts both package objects and string package paths as input.
  Requires Python 3.9+ and installed dependencies: json5, pyyaml.
  Encoding is fixed to utf-8.
  """

  @classmethod
  def _get_package_name(cls, package):
    if hasattr(package, "__name__"):
      return package.__name__
    elif isinstance(package, str):
      return package
    raise TypeError("package must be a package object or string package path")

  @classmethod
  def get_file_path(cls, package, resource_path):
    '''
    Get the absolute file path of a resource within a package.
    @param package: The package object or string package path.
      - use from blues_lib.util.mock import mock to get the package object.
      - use 'blues_lib.util.mock' to get the string package path.
    @param resource_path: The relative path to the resource within the package. such as 'tests/mock/command/llm-loop-urls/def.conf'
    @return: The absolute file path of the resource.
    @raises FileNotFoundError: If the resource does not exist in the package.
    '''
    package_name = cls._get_package_name(package)
    pkg_dir = resources.files(package)
    file_path = pkg_dir.joinpath(resource_path)
    if not file_path.exists():
      raise FileNotFoundError(f"Resource not found in package [{package_name}]: {resource_path}")
    return file_path

  @classmethod
  def read_hocon(cls, package, resource_path):
    file_path = cls.get_file_path(package, resource_path)
    return FileReader.read_hocon(file_path)

  @classmethod
  def read_text(cls, package, resource_path):
    file_path = cls.get_file_path(package, resource_path)
    return FileReader.read_text(file_path)

  @classmethod
  def read_json(cls, package, resource_path):
    file_path = cls.get_file_path(package, resource_path)
    return FileReader.read_json(file_path)

  @classmethod
  def read_json5(cls, package, resource_path):
    file_path = cls.get_file_path(package, resource_path)
    return FileReader.read_json5(file_path)

  @classmethod
  def read_yaml(cls, package, resource_path):
    file_path = cls.get_file_path(package, resource_path)
    return FileReader.read_yaml(file_path)

  @classmethod
  def read_csv(cls, package, resource_path):
    file_path = cls.get_file_path(package, resource_path)
    return FileReader.read_csv(file_path)

  @classmethod
  def read_binary(cls, package, resource_path):
    file_path = cls.get_file_path(package, resource_path)
    return file_path.read_bytes()
  
  