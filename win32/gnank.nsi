Name            'Gnank'
SetCompressor   'lzma'
Icon            'gnank.ico'
OutFile         '..\Gnank.exe'

SilentInstall silent

Section
    InitPluginsDir
    SetOutPath '$PLUGINSDIR'
    File /r '..\dist\*.*'
    SetOutPath '$EXEDIR'
    nsExec::Exec $PLUGINSDIR\gnank.exe
SectionEnd
