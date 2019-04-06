Name     'Gnank'
Icon     'gnank.ico'
OutFile  '..\..\gnank.exe'

SetCompressor  /SOLID  'lzma'
SetCompressorDictSize  64
SetDatablockOptimize   ON

SilentInstall silent
RequestExecutionLevel user

Section
	InitPluginsDir
	SetOutPath '$PLUGINSDIR'
	File /r '..\..\dist\*.*'
	SetOutPath '$EXEDIR'
	ExecWait '$PLUGINSDIR\gnank.exe'
SectionEnd
