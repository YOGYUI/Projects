#define _AFXDLL
#include <iostream>
#include <afxwin.h>
#include <SetupAPI.h>
#include <locale.h>
#include <vector>

#pragma comment(lib, "setupapi.lib")

void test() {
	HDEVINFO hDevInfo;
	SP_DEVINFO_DATA stDevInfoData = SP_DEVINFO_DATA();

	hDevInfo = SetupDiGetClassDevs(
		0L,
		0L,
		0L,
		DIGCF_PRESENT | DIGCF_ALLCLASSES | DIGCF_PROFILE
	);

	if (hDevInfo == INVALID_HANDLE_VALUE)
		return;

	stDevInfoData.cbSize = sizeof(SP_DEVINFO_DATA);
	for (DWORD i = 0; SetupDiEnumDeviceInfo(hDevInfo, i, &stDevInfoData); i++) {
		TCHAR szInstanceId[MAX_PATH] = { 0 };
		TCHAR szClassName[MAX_PATH] = { 0 };
		TCHAR szFriendlyName[MAX_PATH] = { 0 };
		TCHAR szClassDescription[MAX_PATH] = { 0 };
		TCHAR szDeviceDescription[MAX_PATH] = { 0 };

		// Get Device Instance ID
		BOOL bResult = SetupDiGetDeviceInstanceId(
			hDevInfo,
			&stDevInfoData,
			szInstanceId,
			_countof(szInstanceId),
			0
		);

		if (!bResult) {
			_tprintf(_T("Failed to get device instance ID\n"));
			continue;
		}

		(VOID)SetupDiGetDeviceRegistryProperty(
			hDevInfo,
			&stDevInfoData,
			SPDRP_CLASS,
			0,
			(PBYTE)szClassName,
			_countof(szClassName),
			0
		);

		(VOID)SetupDiGetDeviceRegistryProperty(
			hDevInfo,
			&stDevInfoData,
			SPDRP_DEVICEDESC,
			0,
			(PBYTE)szDeviceDescription,
			_countof(szDeviceDescription),
			0
		);

		(VOID)SetupDiGetDeviceRegistryProperty(
			hDevInfo,
			&stDevInfoData,
			SPDRP_FRIENDLYNAME,
			0,
			(PBYTE)szFriendlyName,
			_countof(szFriendlyName),
			0
		);

		(VOID)SetupDiGetClassDescription(
			&stDevInfoData.ClassGuid,
			szClassDescription,
			_countof(szClassDescription),
			0
		);

		_tprintf(_T("[%d]\n"), i);
		_tprintf(_T("-- Class: %s\n"), szClassName);
		_tprintf(_T("-- Friendly Name: %s\n"), szFriendlyName);
		_tprintf(_T("-- Instance ID: %s\n"), szInstanceId);
		_tprintf(_T("-- Class Description: %s\n"), szClassDescription);
		_tprintf(_T("-- Device Description: %s\n"), szDeviceDescription);
		_tprintf(_T("\n"));
	}

	SetupDiDestroyDeviceInfoList(hDevInfo);
}


void test2(std::vector<CString>& avecDesc)
{
	HDEVINFO hDevInfo;
	SP_DEVINFO_DATA stDevInfoData = SP_DEVINFO_DATA();

	hDevInfo = SetupDiGetClassDevs(
		0L,
		0L,
		0L,
		DIGCF_PRESENT | DIGCF_ALLCLASSES | DIGCF_PROFILE
	);

	if (hDevInfo == INVALID_HANDLE_VALUE)
		return;

	stDevInfoData.cbSize = sizeof(SP_DEVINFO_DATA);
	for (DWORD i = 0; SetupDiEnumDeviceInfo(hDevInfo, i, &stDevInfoData); i++) {
		TCHAR szDeviceDescription[MAX_PATH] = { 0 };

		(VOID)SetupDiGetDeviceRegistryProperty(
			hDevInfo,
			&stDevInfoData,
			SPDRP_DEVICEDESC,
			0,
			(PBYTE)szDeviceDescription,
			_countof(szDeviceDescription),
			0
		);

		// _tprintf(_T("%s\n"), szDeviceDescription);
		avecDesc.push_back(szDeviceDescription);
	}

	SetupDiDestroyDeviceInfoList(hDevInfo);
}


int main() {
	setlocale(LC_ALL, "korean");
	_wsetlocale(LC_ALL, L"korean");

	test();

	/*
	LARGE_INTEGER	liStart;
	LARGE_INTEGER	liEnd;
	LARGE_INTEGER	liFreq;

	QueryPerformanceFrequency(&liFreq);

	QueryPerformanceCounter(&liStart);
	std::vector<CString> vecDev;
	test2(vecDev);

	QueryPerformanceCounter(&liEnd);
	double fTimeElapsedMs = (double)(liEnd.QuadPart - liStart.QuadPart) / (double)liFreq.QuadPart * 1000;
	_tprintf(_T("Total Device Count: %lld, Elapsed: %f msec\n"), vecDev.size(), fTimeElapsedMs);

	auto idx = std::find(vecDev.begin(), vecDev.end(), _T("FTDI FT601 USB 3.0 Bridge Device"));
	if (idx == vecDev.end()) {
		_tprintf(_T("Cannot find device"));
	}
	else {
		_tprintf(_T("Found device (index: %lld)"), idx - vecDev.begin());
	}
	*/
}
