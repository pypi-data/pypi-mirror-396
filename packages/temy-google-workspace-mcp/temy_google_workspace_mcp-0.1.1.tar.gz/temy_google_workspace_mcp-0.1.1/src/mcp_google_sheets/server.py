#!/usr/bin/env python
"""
Google Spreadsheet MCP Server
A Model Context Protocol (MCP) server built with FastMCP for interacting with Google Sheets.
"""

import base64
import os
import sys
from typing import List, Dict, Any, Optional, Union
import json
from dataclasses import dataclass
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

# MCP imports
from mcp.server.fastmcp import FastMCP, Context

# Google API imports
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import google.auth

# Constants
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/documents'
]
CREDENTIALS_CONFIG = os.environ.get('CREDENTIALS_CONFIG')
TOKEN_PATH = os.environ.get('TOKEN_PATH', 'token.json')
CREDENTIALS_PATH = os.environ.get('CREDENTIALS_PATH', 'credentials.json')
SERVICE_ACCOUNT_PATH = os.environ.get('SERVICE_ACCOUNT_PATH', 'service_account.json')
DRIVE_FOLDER_ID = os.environ.get('DRIVE_FOLDER_ID', '')  # Working directory in Google Drive

@dataclass
class SpreadsheetContext:
    """Context for Google Spreadsheet and Docs services"""
    sheets_service: Any
    drive_service: Any
    docs_service: Any
    folder_id: Optional[str] = None


@asynccontextmanager
async def spreadsheet_lifespan(server: FastMCP) -> AsyncIterator[SpreadsheetContext]:
    """Manage Google Spreadsheet API connection lifecycle"""
    # Authenticate and build the service
    creds = None

    if CREDENTIALS_CONFIG:
        creds = service_account.Credentials.from_service_account_info(json.loads(base64.b64decode(CREDENTIALS_CONFIG)), scopes=SCOPES)
    
    # Check for explicit service account authentication first (custom SERVICE_ACCOUNT_PATH)
    if not creds and SERVICE_ACCOUNT_PATH and os.path.exists(SERVICE_ACCOUNT_PATH):
        try:
            # Regular service account authentication
            creds = service_account.Credentials.from_service_account_file(
                SERVICE_ACCOUNT_PATH,
                scopes=SCOPES
            )
            print("Using service account authentication")
            print(f"Working with Google Drive folder ID: {DRIVE_FOLDER_ID or 'Not specified'}")
        except Exception as e:
            print(f"Error using service account authentication: {e}")
            creds = None
    
    # Fall back to OAuth flow if service account auth failed or not configured
    if not creds:
        print("Trying OAuth authentication flow")
        if os.path.exists(TOKEN_PATH):
            with open(TOKEN_PATH, 'r') as token:
                creds = Credentials.from_authorized_user_info(json.load(token), SCOPES)
                
        # If credentials are not valid or don't exist, get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    print("Attempting to refresh expired token...")
                    creds.refresh(Request())
                    print("Token refreshed successfully")
                    # Save the refreshed token
                    with open(TOKEN_PATH, 'w') as token:
                        token.write(creds.to_json())
                except Exception as refresh_error:
                    print(f"Token refresh failed: {refresh_error}")
                    print("Triggering reauthentication flow...")
                    creds = None  # Clear creds to trigger OAuth flow below

            # If refresh failed or creds don't exist, run OAuth flow
            if not creds:
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
                    creds = flow.run_local_server(port=0)

                    # Save the credentials for the next run
                    with open(TOKEN_PATH, 'w') as token:
                        token.write(creds.to_json())
                    print("Successfully authenticated using OAuth flow")
                except Exception as e:
                    print(f"Error with OAuth flow: {e}")
                    creds = None
    
    # Try Application Default Credentials if no creds thus far
    # This will automatically check GOOGLE_APPLICATION_CREDENTIALS, gcloud auth, and metadata service
    if not creds:
        try:
            print("Attempting to use Application Default Credentials (ADC)")
            print("ADC will check: GOOGLE_APPLICATION_CREDENTIALS, gcloud auth, and metadata service")
            creds, project = google.auth.default(
                scopes=SCOPES
            )
            print(f"Successfully authenticated using ADC for project: {project}")
        except Exception as e:
            print(f"Error using Application Default Credentials: {e}")
            raise Exception("All authentication methods failed. Please configure credentials.")
    
    # Build the services
    sheets_service = build('sheets', 'v4', credentials=creds)
    drive_service = build('drive', 'v3', credentials=creds)
    docs_service = build('docs', 'v1', credentials=creds)
    
    try:
        # Provide the service in the context
        yield SpreadsheetContext(
            sheets_service=sheets_service,
            drive_service=drive_service,
            docs_service=docs_service,
            folder_id=DRIVE_FOLDER_ID if DRIVE_FOLDER_ID else None
        )
    finally:
        # No explicit cleanup needed for Google APIs
        pass


# Initialize the MCP server with lifespan management
# Resolve host/port from environment variables with flexible names
_resolved_host = os.environ.get('HOST') or os.environ.get('FASTMCP_HOST') or "0.0.0.0"
_resolved_port_str = os.environ.get('PORT') or os.environ.get('FASTMCP_PORT') or "8000"
try:
    _resolved_port = int(_resolved_port_str)
except ValueError:
    _resolved_port = 8000

# Initialize the MCP server with explicit host/port to ensure binding as configured
mcp = FastMCP("Google Spreadsheet",
              dependencies=["google-auth", "google-auth-oauthlib", "google-api-python-client"],
              lifespan=spreadsheet_lifespan,
              host=_resolved_host,
              port=_resolved_port)


@mcp.tool()
def get_sheet_data(spreadsheet_id: str, 
                   sheet: str,
                   range: Optional[str] = None,
                   include_grid_data: bool = False,
                   ctx: Context = None) -> Dict[str, Any]:
    """
    Get data from a specific sheet in a Google Spreadsheet.
    
    Args:
        spreadsheet_id: The ID of the spreadsheet (found in the URL)
        sheet: The name of the sheet
        range: Optional cell range in A1 notation (e.g., 'A1:C10'). If not provided, gets all data.
        include_grid_data: If True, includes cell formatting and other metadata in the response.
            Note: Setting this to True will significantly increase the response size and token usage
            when parsing the response, as it includes detailed cell formatting information.
            Default is False (returns values only, more efficient).
    
    Returns:
        Grid data structure with either full metadata or just values from Google Sheets API, depending on include_grid_data parameter
    """
    sheets_service = ctx.request_context.lifespan_context.sheets_service

    # Construct the range - keep original API behavior
    if range:
        full_range = f"{sheet}!{range}"
    else:
        full_range = sheet
    
    if include_grid_data:
        # Use full API to get all grid data including formatting
        result = sheets_service.spreadsheets().get(
            spreadsheetId=spreadsheet_id,
            ranges=[full_range],
            includeGridData=True
        ).execute()
    else:
        # Use values API to get cell values only (more efficient)
        values_result = sheets_service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=full_range
        ).execute()
        
        # Format the response to match expected structure
        result = {
            'spreadsheetId': spreadsheet_id,
            'valueRanges': [{
                'range': full_range,
                'values': values_result.get('values', [])
            }]
        }

    return result

@mcp.tool()
def get_sheet_formulas(spreadsheet_id: str,
                       sheet: str,
                       range: Optional[str] = None,
                       ctx: Context = None) -> List[List[Any]]:
    """
    Get formulas from a specific sheet in a Google Spreadsheet.
    
    Args:
        spreadsheet_id: The ID of the spreadsheet (found in the URL)
        sheet: The name of the sheet
        range: Optional cell range in A1 notation (e.g., 'A1:C10'). If not provided, gets all formulas from the sheet.
    
    Returns:
        A 2D array of the sheet formulas.
    """
    sheets_service = ctx.request_context.lifespan_context.sheets_service
    
    # Construct the range
    if range:
        full_range = f"{sheet}!{range}"
    else:
        full_range = sheet  # Get all formulas in the specified sheet
    
    # Call the Sheets API
    result = sheets_service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=full_range,
        valueRenderOption='FORMULA'  # Request formulas
    ).execute()
    
    # Get the formulas from the response
    formulas = result.get('values', [])
    return formulas

@mcp.tool()
def update_cells(spreadsheet_id: str,
                sheet: str,
                range: str,
                data: List[List[Any]],
                ctx: Context = None) -> Dict[str, Any]:
    """
    Update cells in a Google Spreadsheet.
    
    Args:
        spreadsheet_id: The ID of the spreadsheet (found in the URL)
        sheet: The name of the sheet
        range: Cell range in A1 notation (e.g., 'A1:C10')
        data: 2D array of values to update
    
    Returns:
        Result of the update operation
    """
    sheets_service = ctx.request_context.lifespan_context.sheets_service
    
    # Construct the range
    full_range = f"{sheet}!{range}"
    
    # Prepare the value range object
    value_range_body = {
        'values': data
    }
    
    # Call the Sheets API to update values
    result = sheets_service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=full_range,
        valueInputOption='USER_ENTERED',
        body=value_range_body
    ).execute()
    
    return result


@mcp.tool()
def batch_update_cells(spreadsheet_id: str,
                       sheet: str,
                       ranges: Dict[str, List[List[Any]]],
                       ctx: Context = None) -> Dict[str, Any]:
    """
    Batch update multiple ranges in a Google Spreadsheet.
    
    Args:
        spreadsheet_id: The ID of the spreadsheet (found in the URL)
        sheet: The name of the sheet
        ranges: Dictionary mapping range strings to 2D arrays of values
               e.g., {'A1:B2': [[1, 2], [3, 4]], 'D1:E2': [['a', 'b'], ['c', 'd']]}
    
    Returns:
        Result of the batch update operation
    """
    sheets_service = ctx.request_context.lifespan_context.sheets_service
    
    # Prepare the batch update request
    data = []
    for range_str, values in ranges.items():
        full_range = f"{sheet}!{range_str}"
        data.append({
            'range': full_range,
            'values': values
        })
    
    batch_body = {
        'valueInputOption': 'USER_ENTERED',
        'data': data
    }
    
    # Call the Sheets API to perform batch update
    result = sheets_service.spreadsheets().values().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body=batch_body
    ).execute()
    
    return result


@mcp.tool()
def add_rows(spreadsheet_id: str,
             sheet: str,
             count: int,
             start_row: Optional[int] = None,
             ctx: Context = None) -> Dict[str, Any]:
    """
    Add rows to a sheet in a Google Spreadsheet.
    
    Args:
        spreadsheet_id: The ID of the spreadsheet (found in the URL)
        sheet: The name of the sheet
        count: Number of rows to add
        start_row: 0-based row index to start adding. If not provided, adds at the beginning.
    
    Returns:
        Result of the operation
    """
    sheets_service = ctx.request_context.lifespan_context.sheets_service
    
    # Get sheet ID
    spreadsheet = sheets_service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    sheet_id = None
    
    for s in spreadsheet['sheets']:
        if s['properties']['title'] == sheet:
            sheet_id = s['properties']['sheetId']
            break
            
    if sheet_id is None:
        return {"error": f"Sheet '{sheet}' not found"}
    
    # Prepare the insert rows request
    request_body = {
        "requests": [
            {
                "insertDimension": {
                    "range": {
                        "sheetId": sheet_id,
                        "dimension": "ROWS",
                        "startIndex": start_row if start_row is not None else 0,
                        "endIndex": (start_row if start_row is not None else 0) + count
                    },
                    "inheritFromBefore": start_row is not None and start_row > 0
                }
            }
        ]
    }
    
    # Execute the request
    result = sheets_service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body=request_body
    ).execute()
    
    return result


@mcp.tool()
def add_columns(spreadsheet_id: str,
                sheet: str,
                count: int,
                start_column: Optional[int] = None,
                ctx: Context = None) -> Dict[str, Any]:
    """
    Add columns to a sheet in a Google Spreadsheet.
    
    Args:
        spreadsheet_id: The ID of the spreadsheet (found in the URL)
        sheet: The name of the sheet
        count: Number of columns to add
        start_column: 0-based column index to start adding. If not provided, adds at the beginning.
    
    Returns:
        Result of the operation
    """
    sheets_service = ctx.request_context.lifespan_context.sheets_service
    
    # Get sheet ID
    spreadsheet = sheets_service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    sheet_id = None
    
    for s in spreadsheet['sheets']:
        if s['properties']['title'] == sheet:
            sheet_id = s['properties']['sheetId']
            break
            
    if sheet_id is None:
        return {"error": f"Sheet '{sheet}' not found"}
    
    # Prepare the insert columns request
    request_body = {
        "requests": [
            {
                "insertDimension": {
                    "range": {
                        "sheetId": sheet_id,
                        "dimension": "COLUMNS",
                        "startIndex": start_column if start_column is not None else 0,
                        "endIndex": (start_column if start_column is not None else 0) + count
                    },
                    "inheritFromBefore": start_column is not None and start_column > 0
                }
            }
        ]
    }
    
    # Execute the request
    result = sheets_service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body=request_body
    ).execute()
    
    return result


@mcp.tool()
def list_sheets(spreadsheet_id: str, ctx: Context = None) -> List[str]:
    """
    List all sheets in a Google Spreadsheet.
    
    Args:
        spreadsheet_id: The ID of the spreadsheet (found in the URL)
    
    Returns:
        List of sheet names
    """
    sheets_service = ctx.request_context.lifespan_context.sheets_service
    
    # Get spreadsheet metadata
    spreadsheet = sheets_service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    
    # Extract sheet names
    sheet_names = [sheet['properties']['title'] for sheet in spreadsheet['sheets']]
    
    return sheet_names


@mcp.tool()
def copy_sheet(src_spreadsheet: str,
               src_sheet: str,
               dst_spreadsheet: str,
               dst_sheet: str,
               ctx: Context = None) -> Dict[str, Any]:
    """
    Copy a sheet from one spreadsheet to another.
    
    Args:
        src_spreadsheet: Source spreadsheet ID
        src_sheet: Source sheet name
        dst_spreadsheet: Destination spreadsheet ID
        dst_sheet: Destination sheet name
    
    Returns:
        Result of the operation
    """
    sheets_service = ctx.request_context.lifespan_context.sheets_service
    
    # Get source sheet ID
    src = sheets_service.spreadsheets().get(spreadsheetId=src_spreadsheet).execute()
    src_sheet_id = None
    
    for s in src['sheets']:
        if s['properties']['title'] == src_sheet:
            src_sheet_id = s['properties']['sheetId']
            break
            
    if src_sheet_id is None:
        return {"error": f"Source sheet '{src_sheet}' not found"}
    
    # Copy the sheet to destination spreadsheet
    copy_result = sheets_service.spreadsheets().sheets().copyTo(
        spreadsheetId=src_spreadsheet,
        sheetId=src_sheet_id,
        body={
            "destinationSpreadsheetId": dst_spreadsheet
        }
    ).execute()
    
    # If destination sheet name is different from the default copied name, rename it
    if 'title' in copy_result and copy_result['title'] != dst_sheet:
        # Get the ID of the newly copied sheet
        copy_sheet_id = copy_result['sheetId']
        
        # Rename the copied sheet
        rename_request = {
            "requests": [
                {
                    "updateSheetProperties": {
                        "properties": {
                            "sheetId": copy_sheet_id,
                            "title": dst_sheet
                        },
                        "fields": "title"
                    }
                }
            ]
        }
        
        rename_result = sheets_service.spreadsheets().batchUpdate(
            spreadsheetId=dst_spreadsheet,
            body=rename_request
        ).execute()
        
        return {
            "copy": copy_result,
            "rename": rename_result
        }
    
    return {"copy": copy_result}


@mcp.tool()
def rename_sheet(spreadsheet: str,
                 sheet: str,
                 new_name: str,
                 ctx: Context = None) -> Dict[str, Any]:
    """
    Rename a sheet in a Google Spreadsheet.
    
    Args:
        spreadsheet: Spreadsheet ID
        sheet: Current sheet name
        new_name: New sheet name
    
    Returns:
        Result of the operation
    """
    sheets_service = ctx.request_context.lifespan_context.sheets_service
    
    # Get sheet ID
    spreadsheet_data = sheets_service.spreadsheets().get(spreadsheetId=spreadsheet).execute()
    sheet_id = None
    
    for s in spreadsheet_data['sheets']:
        if s['properties']['title'] == sheet:
            sheet_id = s['properties']['sheetId']
            break
            
    if sheet_id is None:
        return {"error": f"Sheet '{sheet}' not found"}
    
    # Prepare the rename request
    request_body = {
        "requests": [
            {
                "updateSheetProperties": {
                    "properties": {
                        "sheetId": sheet_id,
                        "title": new_name
                    },
                    "fields": "title"
                }
            }
        ]
    }
    
    # Execute the request
    result = sheets_service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet,
        body=request_body
    ).execute()
    
    return result


@mcp.tool()
def get_multiple_sheet_data(queries: List[Dict[str, str]], 
                            ctx: Context = None) -> List[Dict[str, Any]]:
    """
    Get data from multiple specific ranges in Google Spreadsheets.
    
    Args:
        queries: A list of dictionaries, each specifying a query. 
                 Each dictionary should have 'spreadsheet_id', 'sheet', and 'range' keys.
                 Example: [{'spreadsheet_id': 'abc', 'sheet': 'Sheet1', 'range': 'A1:B5'}, 
                           {'spreadsheet_id': 'xyz', 'sheet': 'Data', 'range': 'C1:C10'}]
    
    Returns:
        A list of dictionaries, each containing the original query parameters 
        and the fetched 'data' or an 'error'.
    """
    sheets_service = ctx.request_context.lifespan_context.sheets_service
    results = []
    
    for query in queries:
        spreadsheet_id = query.get('spreadsheet_id')
        sheet = query.get('sheet')
        range_str = query.get('range')
        
        if not all([spreadsheet_id, sheet, range_str]):
            results.append({**query, 'error': 'Missing required keys (spreadsheet_id, sheet, range)'})
            continue

        try:
            # Construct the range
            full_range = f"{sheet}!{range_str}"
            
            # Call the Sheets API
            result = sheets_service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=full_range
            ).execute()
            
            # Get the values from the response
            values = result.get('values', [])
            results.append({**query, 'data': values})

        except Exception as e:
            results.append({**query, 'error': str(e)})
            
    return results


@mcp.tool()
def get_multiple_spreadsheet_summary(spreadsheet_ids: List[str],
                                   rows_to_fetch: int = 5, 
                                   ctx: Context = None) -> List[Dict[str, Any]]:
    """
    Get a summary of multiple Google Spreadsheets, including sheet names, 
    headers, and the first few rows of data for each sheet.
    
    Args:
        spreadsheet_ids: A list of spreadsheet IDs to summarize.
        rows_to_fetch: The number of rows (including header) to fetch for the summary (default: 5).
    
    Returns:
        A list of dictionaries, each representing a spreadsheet summary. 
        Includes spreadsheet title, sheet summaries (title, headers, first rows), or an error.
    """
    sheets_service = ctx.request_context.lifespan_context.sheets_service
    summaries = []
    
    for spreadsheet_id in spreadsheet_ids:
        summary_data = {
            'spreadsheet_id': spreadsheet_id,
            'title': None,
            'sheets': [],
            'error': None
        }
        try:
            # Get spreadsheet metadata
            spreadsheet = sheets_service.spreadsheets().get(
                spreadsheetId=spreadsheet_id,
                fields='properties.title,sheets(properties(title,sheetId))'
            ).execute()
            
            summary_data['title'] = spreadsheet.get('properties', {}).get('title', 'Unknown Title')
            
            sheet_summaries = []
            for sheet in spreadsheet.get('sheets', []):
                sheet_title = sheet.get('properties', {}).get('title')
                sheet_id = sheet.get('properties', {}).get('sheetId')
                sheet_summary = {
                    'title': sheet_title,
                    'sheet_id': sheet_id,
                    'headers': [],
                    'first_rows': [],
                    'error': None
                }
                
                if not sheet_title:
                    sheet_summary['error'] = 'Sheet title not found'
                    sheet_summaries.append(sheet_summary)
                    continue
                    
                try:
                    # Fetch the first few rows (e.g., A1:Z5)
                    # Adjust range if fewer rows are requested
                    max_row = max(1, rows_to_fetch) # Ensure at least 1 row is fetched
                    range_to_get = f"{sheet_title}!A1:{max_row}" # Fetch all columns up to max_row
                    
                    result = sheets_service.spreadsheets().values().get(
                        spreadsheetId=spreadsheet_id,
                        range=range_to_get
                    ).execute()
                    
                    values = result.get('values', [])
                    
                    if values:
                        sheet_summary['headers'] = values[0]
                        if len(values) > 1:
                            sheet_summary['first_rows'] = values[1:max_row]
                    else:
                        # Handle empty sheets or sheets with less data than requested
                        sheet_summary['headers'] = []
                        sheet_summary['first_rows'] = []

                except Exception as sheet_e:
                    sheet_summary['error'] = f'Error fetching data for sheet {sheet_title}: {sheet_e}'
                
                sheet_summaries.append(sheet_summary)
            
            summary_data['sheets'] = sheet_summaries
            
        except Exception as e:
            summary_data['error'] = f'Error fetching spreadsheet {spreadsheet_id}: {e}'
            
        summaries.append(summary_data)
        
    return summaries


@mcp.resource("spreadsheet://{spreadsheet_id}/info")
def get_spreadsheet_info(spreadsheet_id: str) -> str:
    """
    Get basic information about a Google Spreadsheet.
    
    Args:
        spreadsheet_id: The ID of the spreadsheet
    
    Returns:
        JSON string with spreadsheet information
    """
    # Access the context through mcp.get_lifespan_context() for resources
    context = mcp.get_lifespan_context()
    sheets_service = context.sheets_service
    
    # Get spreadsheet metadata
    spreadsheet = sheets_service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    
    # Extract relevant information
    info = {
        "title": spreadsheet.get('properties', {}).get('title', 'Unknown'),
        "sheets": [
            {
                "title": sheet['properties']['title'],
                "sheetId": sheet['properties']['sheetId'],
                "gridProperties": sheet['properties'].get('gridProperties', {})
            }
            for sheet in spreadsheet.get('sheets', [])
        ]
    }
    
    return json.dumps(info, indent=2)


@mcp.tool()
def create_spreadsheet(title: str, folder_id: Optional[str] = None, ctx: Context = None) -> Dict[str, Any]:
    """
    Create a new Google Spreadsheet.
    
    Args:
        title: The title of the new spreadsheet
        folder_id: Optional Google Drive folder ID where the spreadsheet should be created.
                  If not provided, uses the configured default folder or creates in root.
    
    Returns:
        Information about the newly created spreadsheet including its ID
    """
    drive_service = ctx.request_context.lifespan_context.drive_service
    # Use provided folder_id or fall back to configured default
    target_folder_id = folder_id or ctx.request_context.lifespan_context.folder_id

    # Create the spreadsheet
    file_body = {
        'name': title,
        'mimeType': 'application/vnd.google-apps.spreadsheet',
    }
    if target_folder_id:
        file_body['parents'] = [target_folder_id]
    
    spreadsheet = drive_service.files().create(
        supportsAllDrives=True,
        body=file_body,
        fields='id, name, parents'
    ).execute()

    spreadsheet_id = spreadsheet.get('id')
    parents = spreadsheet.get('parents')
    folder_info = f" in folder {target_folder_id}" if target_folder_id else " in root"
    print(f"Spreadsheet created with ID: {spreadsheet_id}{folder_info}")

    return {
        'spreadsheetId': spreadsheet_id,
        'title': spreadsheet.get('name', title),
        'folder': parents[0] if parents else 'root',
    }


@mcp.tool()
def create_sheet(spreadsheet_id: str, 
                title: str, 
                ctx: Context = None) -> Dict[str, Any]:
    """
    Create a new sheet tab in an existing Google Spreadsheet.
    
    Args:
        spreadsheet_id: The ID of the spreadsheet
        title: The title for the new sheet
    
    Returns:
        Information about the newly created sheet
    """
    sheets_service = ctx.request_context.lifespan_context.sheets_service
    
    # Define the add sheet request
    request_body = {
        "requests": [
            {
                "addSheet": {
                    "properties": {
                        "title": title
                    }
                }
            }
        ]
    }
    
    # Execute the request
    result = sheets_service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body=request_body
    ).execute()
    
    # Extract the new sheet information
    new_sheet_props = result['replies'][0]['addSheet']['properties']
    
    return {
        'sheetId': new_sheet_props['sheetId'],
        'title': new_sheet_props['title'],
        'index': new_sheet_props.get('index'),
        'spreadsheetId': spreadsheet_id
    }


@mcp.tool()
def list_spreadsheets(folder_id: Optional[str] = None, ctx: Context = None) -> List[Dict[str, str]]:
    """
    List all spreadsheets in the specified Google Drive folder.
    If no folder is specified, uses the configured default folder or lists from 'My Drive'.
    
    Args:
        folder_id: Optional Google Drive folder ID to search in.
                  If not provided, uses the configured default folder or searches 'My Drive'.
    
    Returns:
        List of spreadsheets with their ID and title
    """
    drive_service = ctx.request_context.lifespan_context.drive_service
    # Use provided folder_id or fall back to configured default
    target_folder_id = folder_id or ctx.request_context.lifespan_context.folder_id
    
    query = "mimeType='application/vnd.google-apps.spreadsheet'"
    
    # If a specific folder is provided or configured, search only in that folder
    if target_folder_id:
        query += f" and '{target_folder_id}' in parents"
        print(f"Searching for spreadsheets in folder: {target_folder_id}")
    else:
        print("Searching for spreadsheets in 'My Drive'")
    
    # List spreadsheets
    results = drive_service.files().list(
        q=query,
        spaces='drive',
        includeItemsFromAllDrives=True,
        supportsAllDrives=True,
        fields='files(id, name)',
        orderBy='modifiedTime desc'
    ).execute()
    
    spreadsheets = results.get('files', [])
    
    return [{'id': sheet['id'], 'title': sheet['name']} for sheet in spreadsheets]


@mcp.tool()
def share_spreadsheet(spreadsheet_id: str, 
                      recipients: List[Dict[str, str]],
                      send_notification: bool = True,
                      ctx: Context = None) -> Dict[str, List[Dict[str, Any]]]:
    """
    Share a Google Spreadsheet with multiple users via email, assigning specific roles.
    
    Args:
        spreadsheet_id: The ID of the spreadsheet to share.
        recipients: A list of dictionaries, each containing 'email_address' and 'role'.
                    The role should be one of: 'reader', 'commenter', 'writer'.
                    Example: [
                        {'email_address': 'user1@example.com', 'role': 'writer'},
                        {'email_address': 'user2@example.com', 'role': 'reader'}
                    ]
        send_notification: Whether to send a notification email to the users. Defaults to True.

    Returns:
        A dictionary containing lists of 'successes' and 'failures'. 
        Each item in the lists includes the email address and the outcome.
    """
    drive_service = ctx.request_context.lifespan_context.drive_service
    successes = []
    failures = []
    
    for recipient in recipients:
        email_address = recipient.get('email_address')
        role = recipient.get('role', 'writer') # Default to writer if role is missing for an entry
        
        if not email_address:
            failures.append({
                'email_address': None,
                'error': 'Missing email_address in recipient entry.'
            })
            continue
            
        if role not in ['reader', 'commenter', 'writer']:
             failures.append({
                'email_address': email_address,
                'error': f"Invalid role '{role}'. Must be 'reader', 'commenter', or 'writer'."
            })
             continue

        permission = {
            'type': 'user',
            'role': role,
            'emailAddress': email_address
        }
        
        try:
            result = drive_service.permissions().create(
                fileId=spreadsheet_id,
                body=permission,
                sendNotificationEmail=send_notification,
                fields='id'
            ).execute()
            successes.append({
                'email_address': email_address, 
                'role': role, 
                'permissionId': result.get('id')
            })
        except Exception as e:
            # Try to provide a more informative error message
            error_details = str(e)
            if hasattr(e, 'content'):
                try:
                    error_content = json.loads(e.content)
                    error_details = error_content.get('error', {}).get('message', error_details)
                except json.JSONDecodeError:
                    pass # Keep the original error string
            failures.append({
                'email_address': email_address,
                'error': f"Failed to share: {error_details}"
            })
            
    return {"successes": successes, "failures": failures}


@mcp.tool()
def list_folders(parent_folder_id: Optional[str] = None, ctx: Context = None) -> List[Dict[str, str]]:
    """
    List all folders in the specified Google Drive folder.
    If no parent folder is specified, lists folders from 'My Drive' root.
    
    Args:
        parent_folder_id: Optional Google Drive folder ID to search within.
                         If not provided, searches the root of 'My Drive'.
    
    Returns:
        List of folders with their ID, name, and parent information
    """
    drive_service = ctx.request_context.lifespan_context.drive_service
    
    query = "mimeType='application/vnd.google-apps.folder'"
    
    # If a specific parent folder is provided, search only within that folder
    if parent_folder_id:
        query += f" and '{parent_folder_id}' in parents"
        print(f"Searching for folders in parent folder: {parent_folder_id}")
    else:
        # Search in root of My Drive (folders that don't have any parent folders)
        query += " and 'root' in parents"
        print("Searching for folders in 'My Drive' root")
    
    # List folders
    results = drive_service.files().list(
        q=query,
        spaces='drive',
        includeItemsFromAllDrives=True,
        supportsAllDrives=True,
        fields='files(id, name, parents)',
        orderBy='name'
    ).execute()
    
    folders = results.get('files', [])
    
    return [
        {
            'id': folder['id'], 
            'name': folder['name'],
            'parent': folder.get('parents', ['root'])[0] if folder.get('parents') else 'root'
        } 
        for folder in folders
    ]


@mcp.tool()
def batch_update(spreadsheet_id: str,
                 requests: List[Dict[str, Any]],
                 ctx: Context = None) -> Dict[str, Any]:
    """
    Execute a batch update on a Google Spreadsheet using the full batchUpdate endpoint.
    This provides access to all batchUpdate operations including adding sheets, updating properties,
    inserting/deleting dimensions, formatting, and more.
    
    Args:
        spreadsheet_id: The ID of the spreadsheet (found in the URL)
        requests: A list of request objects. Each request object can contain any valid batchUpdate operation.
                 Common operations include:
                 - addSheet: Add a new sheet
                 - updateSheetProperties: Update sheet properties (title, grid properties, etc.)
                 - insertDimension: Insert rows or columns
                 - deleteDimension: Delete rows or columns
                 - updateCells: Update cell values and formatting
                 - updateBorders: Update cell borders
                 - addConditionalFormatRule: Add conditional formatting
                 - deleteConditionalFormatRule: Remove conditional formatting
                 - updateDimensionProperties: Update row/column properties
                 - and many more...
                 
                 Example requests:
                 [
                     {
                         "addSheet": {
                             "properties": {
                                 "title": "New Sheet"
                             }
                         }
                     },
                     {
                         "updateSheetProperties": {
                             "properties": {
                                 "sheetId": 0,
                                 "title": "Renamed Sheet"
                             },
                             "fields": "title"
                         }
                     },
                     {
                         "insertDimension": {
                             "range": {
                                 "sheetId": 0,
                                 "dimension": "ROWS",
                                 "startIndex": 1,
                                 "endIndex": 3
                             }
                         }
                     }
                 ]
    
    Returns:
        Result of the batch update operation, including replies for each request
    """
    sheets_service = ctx.request_context.lifespan_context.sheets_service
    
    # Validate input
    if not requests:
        return {"error": "requests list cannot be empty"}
    
    if not all(isinstance(req, dict) for req in requests):
        return {"error": "Each request must be a dictionary"}
    
    # Prepare the batch update request body
    request_body = {
        "requests": requests
    }
    
    # Execute the batch update
    result = sheets_service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body=request_body
    ).execute()
    
    return result


def _extract_text_from_document(document: Dict[str, Any], include_formatting: bool = False) -> Union[str, List[Dict[str, Any]]]:
    """
    Extract content from a Google Docs document structure.
    
    Args:
        document: The document object from Google Docs API
        include_formatting: If True, returns structured data with formatting info.
                           If False, returns plain text.
        
    Returns:
        Plain text string if include_formatting=False,
        List of structured elements with formatting if include_formatting=True
    """
    body = document.get('body', {})
    content = body.get('content', [])
    
    if not include_formatting:
        # Plain text extraction (original behavior)
        text_parts = []
        for element in content:
            if 'paragraph' in element:
                paragraph = element['paragraph']
                for elem in paragraph.get('elements', []):
                    if 'textRun' in elem:
                        text_parts.append(elem['textRun'].get('content', ''))
            elif 'table' in element:
                table = element['table']
                for row in table.get('tableRows', []):
                    row_texts = []
                    for cell in row.get('tableCells', []):
                        cell_text = []
                        for cell_content in cell.get('content', []):
                            if 'paragraph' in cell_content:
                                for elem in cell_content['paragraph'].get('elements', []):
                                    if 'textRun' in elem:
                                        cell_text.append(elem['textRun'].get('content', '').strip())
                        row_texts.append(' '.join(cell_text))
                    text_parts.append('\t'.join(row_texts) + '\n')
        return ''.join(text_parts)
    
    # Structured extraction with formatting
    structured_content = []
    
    for element in content:
        start_index = element.get('startIndex', 0)
        end_index = element.get('endIndex', 0)
        
        if 'paragraph' in element:
            paragraph = element['paragraph']
            para_style = paragraph.get('paragraphStyle', {})
            named_style = para_style.get('namedStyleType', 'NORMAL_TEXT')
            
            # Extract text runs with their formatting
            text_runs = []
            for elem in paragraph.get('elements', []):
                if 'textRun' in elem:
                    text_run = elem['textRun']
                    text_style = text_run.get('textStyle', {})
                    
                    run_info = {
                        'text': text_run.get('content', ''),
                        'startIndex': elem.get('startIndex', 0),
                        'endIndex': elem.get('endIndex', 0),
                    }
                    
                    # Only include style properties if they're set
                    if text_style.get('bold'):
                        run_info['bold'] = True
                    if text_style.get('italic'):
                        run_info['italic'] = True
                    if text_style.get('underline'):
                        run_info['underline'] = True
                    if 'fontSize' in text_style:
                        run_info['fontSize'] = text_style['fontSize'].get('magnitude')
                    
                    text_runs.append(run_info)
            
            para_info = {
                'type': 'paragraph',
                'startIndex': start_index,
                'endIndex': end_index,
                'style': named_style,
                'textRuns': text_runs
            }
            structured_content.append(para_info)
            
        elif 'table' in element:
            table = element['table']
            table_info = {
                'type': 'table',
                'startIndex': start_index,
                'endIndex': end_index,
                'rows': table.get('rows', 0),
                'columns': table.get('columns', 0)
            }
            structured_content.append(table_info)
    
    return structured_content


@mcp.tool()
def create_document(title: str, 
                    content: Optional[str] = None,
                    folder_id: Optional[str] = None, 
                    ctx: Context = None) -> Dict[str, Any]:
    """
    Create a new Google Doc.
    
    Args:
        title: The title of the new document
        content: Optional initial text content to add to the document
        folder_id: Optional Google Drive folder ID where the document should be created.
                  If not provided, uses the configured default folder or creates in root.
    
    Returns:
        Information about the newly created document including its ID
    """
    drive_service = ctx.request_context.lifespan_context.drive_service
    docs_service = ctx.request_context.lifespan_context.docs_service
    
    # Use provided folder_id or fall back to configured default
    target_folder_id = folder_id or ctx.request_context.lifespan_context.folder_id

    # Create the document using Drive API
    file_body = {
        'name': title,
        'mimeType': 'application/vnd.google-apps.document',
    }
    if target_folder_id:
        file_body['parents'] = [target_folder_id]
    
    document = drive_service.files().create(
        supportsAllDrives=True,
        body=file_body,
        fields='id, name, parents'
    ).execute()

    document_id = document.get('id')
    parents = document.get('parents')
    
    # If content is provided, insert it into the document
    if content:
        requests = [
            {
                'insertText': {
                    'location': {
                        'index': 1  # Start of document body
                    },
                    'text': content
                }
            }
        ]
        docs_service.documents().batchUpdate(
            documentId=document_id,
            body={'requests': requests}
        ).execute()

    folder_info = f" in folder {target_folder_id}" if target_folder_id else " in root"
    print(f"Document created with ID: {document_id}{folder_info}")

    return {
        'documentId': document_id,
        'title': document.get('name', title),
        'folder': parents[0] if parents else 'root',
    }


@mcp.tool()
def list_documents(folder_id: Optional[str] = None, ctx: Context = None) -> List[Dict[str, str]]:
    """
    List all Google Docs in the specified Google Drive folder.
    If no folder is specified, uses the configured default folder or lists from 'My Drive'.
    
    Args:
        folder_id: Optional Google Drive folder ID to search in.
                  If not provided, uses the configured default folder or searches 'My Drive'.
    
    Returns:
        List of documents with their ID and title
    """
    drive_service = ctx.request_context.lifespan_context.drive_service
    # Use provided folder_id or fall back to configured default
    target_folder_id = folder_id or ctx.request_context.lifespan_context.folder_id
    
    query = "mimeType='application/vnd.google-apps.document'"
    
    # If a specific folder is provided or configured, search only in that folder
    if target_folder_id:
        query += f" and '{target_folder_id}' in parents"
        print(f"Searching for documents in folder: {target_folder_id}")
    else:
        print("Searching for documents in 'My Drive'")
    
    # List documents
    results = drive_service.files().list(
        q=query,
        spaces='drive',
        includeItemsFromAllDrives=True,
        supportsAllDrives=True,
        fields='files(id, name)',
        orderBy='modifiedTime desc'
    ).execute()
    
    documents = results.get('files', [])
    
    return [{'id': doc['id'], 'title': doc['name']} for doc in documents]


@mcp.tool()
def format_range(document_id: str,
                 start_index: int,
                 end_index: int,
                 heading_level: Optional[int] = None,
                 bold: Optional[bool] = None,
                 italic: Optional[bool] = None,
                 underline: Optional[bool] = None,
                 font_size: Optional[int] = None,
                 ctx: Context = None) -> Dict[str, Any]:
    """
    Apply formatting to a range of text in a Google Doc.
    
    Args:
        document_id: The ID of the document (found in the URL)
        start_index: The start index of the range to format (1 is document start)
        end_index: The end index of the range to format (exclusive)
        heading_level: Optional heading level (1-6 for HEADING_1 to HEADING_6, 
                      0 for NORMAL_TEXT to remove heading)
        bold: Set to True for bold, False to remove bold, None to leave unchanged
        italic: Set to True for italic, False to remove italic, None to leave unchanged
        underline: Set to True for underline, False to remove underline, None to leave unchanged
        font_size: Optional font size in points (e.g., 12, 14, 18)
    
    Returns:
        Result of the formatting operation
    """
    docs_service = ctx.request_context.lifespan_context.docs_service
    
    requests = []
    
    # Build text style request if any text styling is specified
    text_style = {}
    text_style_fields = []
    
    if bold is not None:
        text_style['bold'] = bold
        text_style_fields.append('bold')
    
    if italic is not None:
        text_style['italic'] = italic
        text_style_fields.append('italic')
    
    if underline is not None:
        text_style['underline'] = underline
        text_style_fields.append('underline')
    
    if font_size is not None:
        text_style['fontSize'] = {
            'magnitude': font_size,
            'unit': 'PT'
        }
        text_style_fields.append('fontSize')
    
    if text_style_fields:
        requests.append({
            'updateTextStyle': {
                'range': {
                    'startIndex': start_index,
                    'endIndex': end_index
                },
                'textStyle': text_style,
                'fields': ','.join(text_style_fields)
            }
        })
    
    # Build paragraph style request if heading level is specified
    if heading_level is not None:
        heading_map = {
            0: 'NORMAL_TEXT',
            1: 'HEADING_1',
            2: 'HEADING_2',
            3: 'HEADING_3',
            4: 'HEADING_4',
            5: 'HEADING_5',
            6: 'HEADING_6'
        }
        named_style = heading_map.get(heading_level, 'NORMAL_TEXT')
        
        requests.append({
            'updateParagraphStyle': {
                'range': {
                    'startIndex': start_index,
                    'endIndex': end_index
                },
                'paragraphStyle': {
                    'namedStyleType': named_style
                },
                'fields': 'namedStyleType'
            }
        })
    
    if not requests:
        return {
            'documentId': document_id,
            'error': 'No formatting options specified'
        }
    
    result = docs_service.documents().batchUpdate(
        documentId=document_id,
        body={'requests': requests}
    ).execute()
    
    return {
        'documentId': document_id,
        'range': {'startIndex': start_index, 'endIndex': end_index},
        'appliedStyles': {
            'heading': heading_level,
            'bold': bold,
            'italic': italic,
            'underline': underline,
            'fontSize': font_size
        },
        'replies': result.get('replies', [])
    }


@mcp.tool()
def replace_text(document_id: str,
                 find_text: str,
                 replace_with: str,
                 match_case: bool = True,
                 ctx: Context = None) -> Dict[str, Any]:
    """
    Find and replace text in a Google Doc.
    
    Args:
        document_id: The ID of the document (found in the URL)
        find_text: The text to find
        replace_with: The text to replace with
        match_case: Whether to match case when finding text (default: True)
    
    Returns:
        Result of the operation including number of replacements made
    """
    docs_service = ctx.request_context.lifespan_context.docs_service
    
    requests = [
        {
            'replaceAllText': {
                'containsText': {
                    'text': find_text,
                    'matchCase': match_case
                },
                'replaceText': replace_with
            }
        }
    ]
    
    result = docs_service.documents().batchUpdate(
        documentId=document_id,
        body={'requests': requests}
    ).execute()
    
    # Extract the number of occurrences replaced
    replies = result.get('replies', [])
    occurrences_changed = 0
    if replies and 'replaceAllText' in replies[0]:
        occurrences_changed = replies[0]['replaceAllText'].get('occurrencesChanged', 0)
    
    return {
        'documentId': document_id,
        'findText': find_text,
        'replaceWith': replace_with,
        'occurrencesChanged': occurrences_changed
    }


@mcp.tool()
def insert_text(document_id: str, 
                text: str, 
                index: int = -1, 
                ctx: Context = None) -> Dict[str, Any]:
    """
    Insert text into a Google Doc at a specific position.
    
    Args:
        document_id: The ID of the document (found in the URL)
        text: The text to insert
        index: The position to insert at. Use 1 for the beginning of the document,
               or -1 (default) to append at the end.
    
    Returns:
        Result of the operation
    """
    docs_service = ctx.request_context.lifespan_context.docs_service
    
    # If index is -1, we need to find the end of the document
    if index == -1:
        document = docs_service.documents().get(documentId=document_id).execute()
        # Get the end index from the document content
        body = document.get('body', {})
        content = body.get('content', [])
        if content:
            # The last element's endIndex gives us the document length
            index = content[-1].get('endIndex', 1) - 1
        else:
            index = 1
    
    requests = [
        {
            'insertText': {
                'location': {
                    'index': index
                },
                'text': text
            }
        }
    ]
    
    result = docs_service.documents().batchUpdate(
        documentId=document_id,
        body={'requests': requests}
    ).execute()
    
    return {
        'documentId': document_id,
        'insertedAt': index,
        'textLength': len(text),
        'replies': result.get('replies', [])
    }


@mcp.tool()
def get_document_content(document_id: str, 
                         include_formatting: bool = False,
                         ctx: Context = None) -> Dict[str, Any]:
    """
    Get the content of a Google Doc as plain text.
    
    Args:
        document_id: The ID of the document (found in the URL, e.g., 
                     https://docs.google.com/document/d/{document_id}/edit)
        include_formatting: If True, returns structured content with formatting info
                           (paragraph styles like HEADING_1, text styles like bold/italic).
                           If False (default), returns plain text content.
    
    Returns:
        Dictionary containing the document title and plain text content
    """
    docs_service = ctx.request_context.lifespan_context.docs_service
    
    # Get the document
    document = docs_service.documents().get(documentId=document_id).execute()
    
    # Extract title and content
    title = document.get('title', 'Untitled')
    content = _extract_text_from_document(document, include_formatting=include_formatting)
    
    return {
        'documentId': document_id,
        'title': title,
        'content': content
    }


def main():
    # Run the server
    transport = "stdio"
    for i, arg in enumerate(sys.argv):
        if arg == "--transport" and i + 1 < len(sys.argv):
            transport = sys.argv[i + 1]
            break

    mcp.run(transport=transport)
