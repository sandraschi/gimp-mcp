!macro KillFleetProcesses
  DetailPrint "Stopping gimp-mcp processes..."
  ExecWait 'taskkill /F /IM gimp-mcp-backend.exe /T' $0
  ExecWait 'taskkill /F /IM gimp-mcp-native.exe /T' $0
  !if "${INSTALLMODE}" == "currentUser"
    nsis_tauri_utils::KillProcessCurrentUser "gimp-mcp-backend.exe"
    Pop $0
    nsis_tauri_utils::KillProcessCurrentUser "gimp-mcp-native.exe"
    Pop $0
  !else
    nsis_tauri_utils::KillProcess "gimp-mcp-backend.exe"
    Pop $0
    nsis_tauri_utils::KillProcess "gimp-mcp-native.exe"
    Pop $0
  !endif
  Sleep 2000
!macroend

!macro NSIS_HOOK_PREINSTALL
  !insertmacro KillFleetProcesses
!macroend

!macro NSIS_HOOK_PREUNINSTALL
  !insertmacro KillFleetProcesses
!macroend
