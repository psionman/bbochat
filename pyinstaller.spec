from pathlib import Path
import sys
from PyInstaller.utils.hooks import collect_submodules
from PyInstaller.building.build_main import Analysis, PYZ, EXE

project_root = Path.cwd()
venv_site = Path(sys.prefix) / "Lib" / "site-packages"

main_script = project_root / "src" / "bbochat" / "main.py"

datas = [
    (str(venv_site / "psiutils" / "icons"), "psiutils/icons"),
]

hiddenimports = collect_submodules("psiutils")
block_cipher = None

a = Analysis(
    [str(main_script)],
    pathex=[str(project_root)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    name="bbochat",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    onefile=True,   # single EXE
    # <--- REMOVE exclude_binaries entirely
)
