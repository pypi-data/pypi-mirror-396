# gate/ext/google_sheets.py
import requests

from google_oauth import get_auth_headers

SHEETS_API_BASE = "https://sheets.googleapis.com/v4"
DRIVE_API_BASE = "https://www.googleapis.com/drive/v3"


def _authorized_headers():
    """Return Authorization headers for Google APIs using the hosted auth service."""
    return get_auth_headers()


def list_drive_spreadsheets(page_size: int = 50):
    """List user drive files that are Google Sheets."""
    headers = _authorized_headers()
    params = {
        "q": "mimeType='application/vnd.google-apps.spreadsheet'",
        "pageSize": page_size,
        "fields": "files(id,name,modifiedTime),nextPageToken",
    }
    r = requests.get(f"{DRIVE_API_BASE}/files", headers=headers, params=params, timeout=10)
    r.raise_for_status()
    return r.json()


def get_spreadsheet(spreadsheet_id: str):
    headers = _authorized_headers()
    r = requests.get(f"{SHEETS_API_BASE}/spreadsheets/{spreadsheet_id}", headers=headers, timeout=10)
    r.raise_for_status()
    return r.json()


def read_values(spreadsheet_id: str, range_a1: str):
    headers = _authorized_headers()
    r = requests.get(
        f"{SHEETS_API_BASE}/spreadsheets/{spreadsheet_id}/values/{range_a1}",
        headers=headers,
        timeout=10,
    )
    r.raise_for_status()
    return r.json()


def append_values(spreadsheet_id: str, range_a1: str, values: list, value_input_option: str = "RAW"):
    headers = _authorized_headers()
    params = {"valueInputOption": value_input_option}
    body = {"values": values}
    r = requests.post(
        f"{SHEETS_API_BASE}/spreadsheets/{spreadsheet_id}/values/{range_a1}:append",
        headers=headers,
        params=params,
        json=body,
        timeout=10,
    )
    r.raise_for_status()
    return r.json()


def update_values(spreadsheet_id: str, range_a1: str, values: list, value_input_option: str = "RAW"):
    headers = _authorized_headers()
    body = {"values": values}
    params = {"valueInputOption": value_input_option}
    r = requests.put(
        f"{SHEETS_API_BASE}/spreadsheets/{spreadsheet_id}/values/{range_a1}",
        headers=headers,
        params=params,
        json=body,
        timeout=10,
    )
    r.raise_for_status()
    return r.json()


def clear_values(spreadsheet_id: str, range_a1: str):
    headers = _authorized_headers()
    r = requests.post(
        f"{SHEETS_API_BASE}/spreadsheets/{spreadsheet_id}/values/{range_a1}:clear",
        headers=headers,
        timeout=10,
    )
    r.raise_for_status()
    return r.json()
