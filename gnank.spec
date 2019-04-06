# -*- mode: python -*-

block_cipher = None

a = Analysis(
	['src/main.py'],
	pathex=[],
	binaries=[],
	datas=[('src/ajuda.txt', '.'), ('src/gnank.png', '.'), ('src/web.png', '.')],
	hiddenimports=[],
	hookspath=[],
	runtime_hooks=[],
	excludes=[],
	win_no_prefer_redirects=False,
	win_private_assemblies=False,
	cipher=block_cipher,
	noarchive=False
)
pyz = PYZ(
	a.pure,
	a.zipped_data,
	cipher=block_cipher
)
exe = EXE(
	pyz,
	a.scripts,
	[],
	exclude_binaries=True,
	name='gnank',
	debug=False,
	bootloader_ignore_signals=False,
	strip=False,
	upx=True,
	console=False,
	icon='paquets/win32/gnank.ico'
)
coll = COLLECT(
	exe,
	a.binaries,
	a.zipfiles,
	a.datas,
	strip=False,
	upx=True,
	name='gnank'
)
