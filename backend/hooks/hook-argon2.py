from PyInstaller.utils.hooks import collect_all

# This hook ensures all necessary dynamic and compiled components
# of argon2-cffi are correctly bundled by PyInstaller.
def hook(hook_api):
    packages = ['argon2']
    # FIX: Pass the item as a string (packages[0]) instead of a list (packages)
    datas, binaries, hiddenimports = collect_all(packages[0]) 
    return {
        'datas': datas,
        'binaries': binaries,
        'hiddenimports': hiddenimports,
    }