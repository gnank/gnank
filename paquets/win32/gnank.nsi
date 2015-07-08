Name            'Gnank'
SetCompressor   'lzma'
Icon            'gnank.ico'
OutFile         '..\..\gnank.exe'

SilentInstall silent
RequestExecutionLevel user

Section
    InitPluginsDir
    SetOutPath '$PLUGINSDIR'
    File /r '..\..\dist\*.*'
    SetOutPath '$EXEDIR'
    ExecWait '$PLUGINSDIR\gnank.exe'
SectionEnd
