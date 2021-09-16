; Yogyui Web Browser
; MakeSetup NSIS Script

; --- Define ------------------------------------------------------------------------------------------------------------------------------
!define APP_CLASSNAME		"YWebBrowser"
!define APP_VERSION			"1.0.0"
!define LINK_NAME			"YWeb"
!define INSTALLER_NAME		"${APP_CLASSNAME}"
!define PRODUCT_NAME		"${APP_CLASSNAME}"
!define PRODUCT_PUBLISHER	"Yogyui"
!define PRODUCT_WEB_SITE	"https://yogyui.tistory.com/"

!include "MUI2.nsh"

Name 					"${INSTALLER_NAME}"
OutFile					".\${APP_CLASSNAME} Setup.exe"
InstallDir				C:\${APP_CLASSNAME}
XPStyle					on
RequestExecutionLevel 	admin
; -----------------------------------------------------------------------------------------------------------------------------------------

; --- Pages -------------------------------------------------------------------------------------------------------------------------------
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_COMPONENTS
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH
; -----------------------------------------------------------------------------------------------------------------------------------------

; --- Interface ---------------------------------------------------------------------------------------------------------------------------
!define MUI_ABORTWARNING
ShowInstDetails show
Icon Setup.ico
; -----------------------------------------------------------------------------------------------------------------------------------------

; --- Languages ---------------------------------------------------------------------------------------------------------------------------
!insertmacro MUI_LANGUAGE "English"
!insertmacro MUI_LANGUAGE "Korean"
; -----------------------------------------------------------------------------------------------------------------------------------------

; --- Reserve Files -----------------------------------------------------------------------------------------------------------------------
!insertmacro MUI_RESERVEFILE_LANGDLL
; -----------------------------------------------------------------------------------------------------------------------------------------

; --- Section Define ----------------------------------------------------------------------------------------------------------------------
Section "${APP_CLASSNAME}" g1o1
	SetOutPath $INSTDIR
	CreateDirectory $INSTDIR
	; delete pre-installed .py files if possible
	RMDir /r $INSTDIR\Include
	RMDir /r $INSTDIR\Library
	; compile all files
	File /r .\dist\${APP_CLASSNAME}\*.*

	; link-file functions
	Delete "$DESKTOP\${LINK_NAME}.lnk"
	CreateShortCut "$DESKTOP\${LINK_NAME}.lnk" "$INSTDIR\${APP_CLASSNAME}.exe"
	RMDir /r $SMPROGRAMS
	CreateDirectory "$SMPROGRAMS"
	CreateShortCut "$SMPROGRAMS\${LINK_NAME}.lnk" "$INSTDIR\${APP_CLASSNAME}.exe"

	; uninstaller functions
	WriteUninstaller "$INSTDIR\Uninstaller.exe"
	; register uninstaller to control panel
	WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_CLASSNAME}" "DisplayName" "${LINK_NAME}"
	WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_CLASSNAME}" "DisplayIcon" "$INSTDIR\${APP_CLASSNAME}.exe"
	WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_CLASSNAME}" "DisplayVersion" "${APP_VERSION}"
	WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_CLASSNAME}" "Publisher" "${PRODUCT_PUBLISHER}"
	WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_CLASSNAME}" "URLInfoAbout" "${PRODUCT_WEB_SITE}"
	WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_CLASSNAME}" "NoModify" 1
	WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_CLASSNAME}" "NoRepair" 1
	WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_CLASSNAME}" "UninstallString" "$INSTDIR\Uninstaller.exe"
SectionEnd
; -----------------------------------------------------------------------------------------------------------------------------------------

; --- Section Description -----------------------------------------------------------------------------------------------------------------
!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
	!insertmacro MUI_DESCRIPTION_TEXT ${g1o1} "${APP_CLASSNAME}"
!insertmacro MUI_FUNCTION_DESCRIPTION_END
; -----------------------------------------------------------------------------------------------------------------------------------------

; --- Installer Functions -----------------------------------------------------------------------------------------------------------------
Function .onInit
	!insertmacro MUI_LANGDLL_DISPLAY
	StrCpy $1 ${g1o1}
FunctionEnd

Function .onSelChange
	!insertmacro StartRadioButtons $1
		!insertmacro RadioButton ${g1o1}
	!insertmacro EndRadioButtons
FunctionEnd
; -----------------------------------------------------------------------------------------------------------------------------------------

; --- Uninstaller -------------------------------------------------------------------------------------------------------------------------
Section "Uninstall"
	Delete "$INSTDIR\*.*"
	Delete "$DESKTOP\${LINK_NAME}.lnk"
	RMDIR /r $INSTDIR
	RMDIR /r $SMPROGRAMS
	; register uninstaller to control panel
	DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_CLASSNAME}"
SectionEnd
; -----------------------------------------------------------------------------------------------------------------------------------------
