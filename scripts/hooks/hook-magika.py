# PyInstaller hook for magika
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Collect all magika data files (models)
datas = collect_data_files("magika")

# Collect all magika submodules
hiddenimports = collect_submodules("magika")

# Add onnxruntime dependency
hiddenimports.append("onnxruntime")
