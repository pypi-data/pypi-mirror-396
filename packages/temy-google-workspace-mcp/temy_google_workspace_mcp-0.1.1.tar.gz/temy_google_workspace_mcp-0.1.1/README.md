<div align="center">
  <!-- Main Title Link -->
  <b>temy-google-workspace-mcp</b>

  <!-- Description Paragraph -->
  <p align="center">
    <i>Your AI Assistant's Gateway to Google Workspace! </i>📊📝
  </p>

[![PyPI - Version](https://img.shields.io/pypi/v/temy-google-workspace-mcp)](https://pypi.org/project/temy-google-workspace-mcp/)
![GitHub License](https://img.shields.io/github/license/yardobr/mcp-google-sheets)
</div>

---

## 🤔 What is this?

`temy-google-workspace-mcp` is a Python-based MCP server that acts as a bridge between any MCP-compatible client (like Claude Desktop, Cursor) and Google Workspace APIs. It allows you to interact with **Google Sheets** and **Google Docs** using a defined set of tools, enabling powerful automation and data manipulation workflows driven by AI.

### What's Included

- **Google Sheets**: Full CRUD operations, formatting, sharing, batch operations
- **Google Docs**: Read documents, create/edit documents, insert/format text, find & replace

---

## 🚀 Quick Start (Using `uvx`)

Essentially the server runs in one line: `uvx temy-google-workspace-mcp@latest`. 

This command will automatically download the latest code and run it. **We recommend always using `@latest`** to ensure you have the newest version with the latest features and bug fixes.

_Refer to the [ID Reference Guide](#-id-reference-guide) for more information about the IDs used below._

1.  **☁️ Prerequisite: Google Cloud Setup**
    *   You **must** configure Google Cloud Platform credentials and enable the necessary APIs first. We strongly recommend using a **Service Account**.
    *   ➡️ Jump to the [**Detailed Google Cloud Platform Setup**](#-google-cloud-platform-setup-detailed) guide below.

2.  **🐍 Install `uv`**
    *   `uvx` is part of `uv`, a fast Python package installer and resolver. Install it if you haven't already:
        ```bash
        # macOS / Linux
        curl -LsSf https://astral.sh/uv/install.sh | sh
        # Windows
        powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
        # Or using pip:
        # pip install uv
        ```
        *Follow instructions in the installer output to add `uv` to your PATH if needed.*

3.  **🔑 Set Essential Environment Variables (Service Account Recommended)**
    *   You need to tell the server how to authenticate. Set these variables in your terminal:
    *   **(Linux/macOS)**
        ```bash
        # Replace with YOUR actual path and folder ID from the Google Setup step
        export SERVICE_ACCOUNT_PATH="/path/to/your/service-account-key.json"
        export DRIVE_FOLDER_ID="YOUR_DRIVE_FOLDER_ID"
        ```
    *   **(Windows CMD)**
        ```cmd
        set SERVICE_ACCOUNT_PATH="C:\path\to\your\service-account-key.json"
        set DRIVE_FOLDER_ID="YOUR_DRIVE_FOLDER_ID"
        ```
    *   **(Windows PowerShell)**
        ```powershell
        $env:SERVICE_ACCOUNT_PATH = "C:\path\to\your\service-account-key.json"
        $env:DRIVE_FOLDER_ID = "YOUR_DRIVE_FOLDER_ID"
        ```
    *   ➡️ See [**Detailed Authentication & Environment Variables**](#-authentication--environment-variables-detailed) for other options (OAuth, `CREDENTIALS_CONFIG`).

4.  **🏃 Run the Server!**
    *   `uvx` will automatically download and run the latest version:
        ```bash
        uvx temy-google-workspace-mcp@latest
        ```
    *   The server will start and print logs indicating it's ready.
    *   
    *   > **💡 Pro Tip:** Always use `@latest` to ensure you get the newest version with bug fixes and features. Without `@latest`, `uvx` may use a cached older version.

5.  **🔌 Connect your MCP Client**
    *   Configure your client (e.g., Claude Desktop, Cursor) to connect to the running server.
    *   Depending on the client you use, you might not need step 4 because the client can launch the server for you. But it's a good practice to test run step 4 anyway to make sure things are set up properly.
    *   ➡️ See [**Usage with Claude Desktop**](#-usage-with-claude-desktop) for examples.

You're ready! Start issuing commands via your MCP client.

---

## ✨ Key Features

*   **Seamless Integration:** Connects directly to Google Drive, Google Sheets, and Google Docs APIs.
*   **Comprehensive Tools:** Offers a wide range of operations for both Sheets and Docs.
*   **Flexible Authentication:** Supports **Service Accounts (recommended)**, OAuth 2.0, and direct credential injection via environment variables.
*   **Easy Deployment:** Run instantly with `uvx` (zero-install feel) or clone for development using `uv`.
*   **AI-Ready:** Designed for use with MCP-compatible clients, enabling natural language interaction with your documents.

---

## 🛠️ Available Tools & Resources

### Google Sheets Tools

_Refer to the [ID Reference Guide](#-id-reference-guide) for more information about the IDs used below._

*(Input parameters are typically strings unless otherwise specified)*

*   **`list_spreadsheets`**: Lists spreadsheets in the configured Drive folder (Service Account) or accessible by the user (OAuth).
    *   `folder_id` (optional string): Google Drive folder ID to search in. Get from its URL. If omitted, uses the configured default folder or searches 'My Drive'.
    *   _Returns:_ List of objects `[{id: string, title: string}]`
*   **`create_spreadsheet`**: Creates a new spreadsheet.
    *   `title` (string): The desired title for the spreadsheet. Example: "Quarterly Report Q4".
    *   `folder_id` (optional string): Google Drive folder ID where the spreadsheet should be created. Get from its URL. If omitted, uses configured default or root.
    *   _Returns:_ Object with spreadsheet info, including `spreadsheetId`, `title`, and `folder`.
*   **`get_sheet_data`**: Reads data from a range in a sheet/tab.
    *   `spreadsheet_id` (string): The spreadsheet ID (from its URL).
    *   `sheet` (string): Name of the sheet/tab (e.g., "Sheet1").
    *   `range` (optional string): A1 notation (e.g., `'A1:C10'`, `'Sheet1!B2:D'`). If omitted, reads the whole sheet/tab specified by `sheet`.
    *   `include_grid_data` (optional boolean, default `False`): If `True`, returns full grid data including formatting and metadata (much larger). If `False`, returns values only (more efficient).
*   **`get_sheet_formulas`**: Reads formulas from a range in a sheet/tab.
*   **`update_cells`**: Writes data to a specific range. Overwrites existing data.
*   **`batch_update_cells`**: Updates multiple ranges in one API call.
*   **`add_rows`**: Adds (inserts) empty rows to a sheet/tab at a specified index.
*   **`add_columns`**: Adds (inserts) empty columns to a sheet/tab at a specified index.
*   **`list_sheets`**: Lists all sheet/tab names within a spreadsheet.
*   **`create_sheet`**: Adds a new sheet/tab to a spreadsheet.
*   **`copy_sheet`**: Duplicates a sheet/tab from one spreadsheet to another.
*   **`rename_sheet`**: Renames an existing sheet/tab.
*   **`get_multiple_sheet_data`**: Fetches data from multiple ranges across potentially different spreadsheets in one call.
*   **`get_multiple_spreadsheet_summary`**: Gets titles, sheet/tab names, headers, and first few rows for multiple spreadsheets.
*   **`share_spreadsheet`**: Shares a spreadsheet with specified users/emails and roles.
*   **`batch_update`**: Execute a batch update on a Google Spreadsheet using the full batchUpdate endpoint.

### Google Docs Tools

*   **`list_documents`**: Lists all Google Docs in the specified Google Drive folder.
    *   `folder_id` (optional string): Google Drive folder ID to search in. If omitted, uses configured default or searches 'My Drive'.
    *   _Returns:_ List of objects `[{id: string, title: string}]`
*   **`get_document_content`**: Get the content of a Google Doc.
    *   `document_id` (string): The ID of the document (found in the URL).
    *   `include_formatting` (optional boolean, default `False`): If `True`, returns structured content with formatting info (paragraph styles like HEADING_1, text styles like bold/italic). If `False`, returns plain text.
    *   _Returns:_ Dictionary with `documentId`, `title`, and `content` (plain text or structured data).
*   **`create_document`**: Create a new Google Doc.
    *   `title` (string): The title of the new document.
    *   `content` (optional string): Initial text content to add to the document.
    *   `folder_id` (optional string): Google Drive folder ID where the document should be created.
    *   _Returns:_ Object with `documentId`, `title`, and `folder`.
*   **`insert_text`**: Insert text into a Google Doc at a specific position.
    *   `document_id` (string): The ID of the document.
    *   `text` (string): The text to insert.
    *   `index` (integer, default `-1`): Position to insert at. Use `1` for beginning, `-1` to append at end.
    *   _Returns:_ Result of the operation including `insertedAt` and `textLength`.
*   **`replace_text`**: Find and replace text in a Google Doc.
    *   `document_id` (string): The ID of the document.
    *   `find_text` (string): The text to find.
    *   `replace_with` (string): The text to replace with.
    *   `match_case` (optional boolean, default `True`): Whether to match case.
    *   _Returns:_ Result including `occurrencesChanged` count.
*   **`format_range`**: Apply formatting to a range of text in a Google Doc.
    *   `document_id` (string): The ID of the document.
    *   `start_index` (integer): Start index of range to format.
    *   `end_index` (integer): End index of range to format (exclusive).
    *   `heading_level` (optional integer): 1-6 for HEADING_1 to HEADING_6, 0 for NORMAL_TEXT.
    *   `bold`, `italic`, `underline` (optional boolean): Set to `True`/`False` to apply/remove.
    *   `font_size` (optional integer): Font size in points (e.g., 12, 18).
    *   _Returns:_ Result of the formatting operation.

### Drive Tools

*   **`list_folders`**: List all folders in the specified Google Drive folder.

### MCP Resources

*   **`spreadsheet://{spreadsheet_id}/info`**: Get basic metadata about a Google Spreadsheet.

---

## ☁️ Google Cloud Platform Setup (Detailed)

This setup is **required** before running the server.

1.  **Create/Select a GCP Project:** Go to the [Google Cloud Console](https://console.cloud.google.com/).
2.  **Enable APIs:** Navigate to "APIs & Services" -> "Library". Search for and enable:
    *   `Google Sheets API`
    *   `Google Drive API`
    *   `Google Docs API` ⬅️ **NEW**
3.  **Configure Credentials:** You need to choose *one* authentication method below (Service Account is recommended).

---

## 🔑 Authentication & Environment Variables (Detailed)

The server needs credentials to access Google APIs. Choose one method:

_Refer to the [ID Reference Guide](#-id-reference-guide) for more information about the IDs used below._

### Method A: Service Account (Recommended for Servers/Automation) ✅

*   **Why?** Headless (no browser needed), secure, ideal for server environments. Doesn't expire easily.
*   **Steps:**
    1.  **Create Service Account:** In GCP Console -> "IAM & Admin" -> "Service Accounts".
        *   Click "+ CREATE SERVICE ACCOUNT". Name it (e.g., `mcp-workspace-service`).
        *   Grant Roles: Add `Editor` role for broad access, or more granular roles (like `roles/drive.file` and specific Sheets/Docs roles) for stricter permissions.
        *   Click "Done". Find the account, click Actions (⋮) -> "Manage keys".
        *   Click "ADD KEY" -> "Create new key" -> **JSON** -> "CREATE".
        *   **Download and securely store** the JSON key file.
    2.  **Create & Share Google Drive Folder:**
        *   In [Google Drive](https://drive.google.com/), create a folder (e.g., "AI Managed Workspace").
        *   Note the **Folder ID** from the URL: `https://drive.google.com/drive/folders/THIS_IS_THE_FOLDER_ID`.
        *   Right-click the folder -> "Share" -> "Share".
        *   Enter the Service Account's email (from the JSON file `client_email`).
        *   Grant **Editor** access. Uncheck "Notify people". Click "Share".
    3.  **Set Environment Variables:**
        *   `SERVICE_ACCOUNT_PATH`: Full path to the downloaded JSON key file.
        *   `DRIVE_FOLDER_ID`: The ID of the shared Google Drive folder.
        *(See [Quick Start](#-quick-start-using-uvx) for OS-specific examples)*

### Method B: OAuth 2.0 (Interactive / Personal Use) 🧑‍💻

*   **Why?** For personal use or local development where interactive browser login is okay.
*   **Steps:**
    1.  **Configure OAuth Consent Screen:** In GCP Console -> "APIs & Services" -> "OAuth consent screen". Select "External", fill required info, add scopes (`.../auth/spreadsheets`, `.../auth/drive`, `.../auth/documents`), add test users if needed.
    2.  **Create OAuth Client ID:** In GCP Console -> "APIs & Services" -> "Credentials". "+ CREATE CREDENTIALS" -> "OAuth client ID" -> Type: **Desktop app**. Name it. "CREATE". **Download JSON**.
    3.  **Set Environment Variables:**
        *   `CREDENTIALS_PATH`: Path to the downloaded OAuth credentials JSON file (default: `credentials.json`).
        *   `TOKEN_PATH`: Path to store the user's refresh token after first login (default: `token.json`). Must be writable.

### Method C: Direct Credential Injection (Advanced) 🔒

*   **Why?** Useful in environments like Docker, Kubernetes, or CI/CD where managing files is hard, but environment variables are easy/secure. Avoids file system access.
*   **How?** Instead of providing a *path* to the credentials file, you provide the *content* of the file, encoded in Base64, directly in an environment variable.
*   **Steps:**
    1.  **Get your credentials JSON file** (either Service Account key or OAuth Client ID file). Let's call it `your_credentials.json`.
    2.  **Generate the Base64 string:**
        *   **(Linux/macOS):** `base64 -w 0 your_credentials.json`
        *   **(Windows PowerShell):**
            ```powershell
            $filePath = "C:\path\to\your_credentials.json"; # Use actual path
            $bytes = [System.IO.File]::ReadAllBytes($filePath);
            $base64 = [System.Convert]::ToBase64String($bytes);
            $base64 # Copy this output
            ```
        *   **(Caution):** Avoid pasting sensitive credentials into untrusted online encoders.
    3.  **Set the Environment Variable:**
        *   `CREDENTIALS_CONFIG`: Set this variable to the **full Base64 string** you just generated.
            ```bash
            # Example (Linux/macOS) - Use the actual string generated
            export CREDENTIALS_CONFIG="ewogICJ0eXBlIjogInNlcnZpY2VfYWNjb..."
            ```

### Method D: Application Default Credentials (ADC) 🌐

*   **Why?** Ideal for Google Cloud environments (GKE, Compute Engine, Cloud Run) and local development with `gcloud auth application-default login`. No explicit credential files needed.
*   **How?** Uses Google's Application Default Credentials chain to automatically discover credentials from multiple sources.
*   **ADC Search Order:**
    1.  `GOOGLE_APPLICATION_CREDENTIALS` environment variable (path to service account key) - **Google's standard variable**
    2.  `gcloud auth application-default login` credentials (local development)
    3.  Attached service account from metadata server (GKE, Compute Engine, etc.)
*   **Setup:**
    *   **Local Development:** 
        1. Run `gcloud auth application-default login --scopes=https://www.googleapis.com/auth/cloud-platform,https://www.googleapis.com/auth/spreadsheets,https://www.googleapis.com/auth/drive,https://www.googleapis.com/auth/documents` once
        2. Set a quota project: `gcloud auth application-default set-quota-project <project_id>` (replace `<project_id>` with your Google Cloud project ID)
    *   **Google Cloud:** Attach a service account to your compute resource
    *   **Environment Variable:** Set `GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json` (Google's standard)
*   **No additional environment variables needed** - ADC is used automatically as a fallback when other methods fail.

**Note:** `GOOGLE_APPLICATION_CREDENTIALS` is Google's official standard environment variable, while `SERVICE_ACCOUNT_PATH` is specific to this MCP server. If you set `GOOGLE_APPLICATION_CREDENTIALS`, ADC will find it automatically.

### Authentication Priority & Summary

The server checks for credentials in this order:

1.  `CREDENTIALS_CONFIG` (Base64 content)
2.  `SERVICE_ACCOUNT_PATH` (Path to Service Account JSON)
3.  `CREDENTIALS_PATH` (Path to OAuth JSON) - triggers interactive flow if token is missing/expired
4.  **Application Default Credentials (ADC)** - automatic fallback

**Environment Variable Summary:**

| Variable                         | Method(s)                   | Description                                                      | Default            |
|:---------------------------------|:----------------------------|:-----------------------------------------------------------------|:-------------------|
| `SERVICE_ACCOUNT_PATH`           | Service Account             | Path to the Service Account JSON key file (MCP server specific). | -                  |
| `GOOGLE_APPLICATION_CREDENTIALS` | ADC                         | Path to service account key (Google's standard variable).        | -                  |
| `DRIVE_FOLDER_ID`                | Service Account             | ID of the Google Drive folder shared with the Service Account.   | -                  |
| `CREDENTIALS_PATH`               | OAuth 2.0                   | Path to the OAuth 2.0 Client ID JSON file.                       | `credentials.json` |
| `TOKEN_PATH`                     | OAuth 2.0                   | Path to store the generated OAuth token.                         | `token.json`       |
| `CREDENTIALS_CONFIG`             | Service Account / OAuth 2.0 | Base64 encoded JSON string of credentials content.               | -                  |

---

## ⚙️ Running the Server (Detailed)

_Refer to the [ID Reference Guide](#-id-reference-guide) for more information about the IDs used below._

### Method 1: Using `uvx` (Recommended for Users)

As shown in the [Quick Start](#-quick-start-using-uvx), this is the easiest way. Set environment variables, then run:

```bash
uvx temy-google-workspace-mcp@latest
```
`uvx` handles fetching and running the package temporarily.

### Method 2: For Development (Cloning the Repo)

If you want to modify the code:

1.  **Clone:** `git clone https://github.com/yardobr/mcp-google-sheets.git && cd mcp-google-sheets`
2.  **Set Environment Variables:** As described above.
3.  **Run using `uv`:** (Uses the local code)
    ```bash
    uv run temy-google-workspace-mcp
    ```

---

## 🔌 Usage with Claude Desktop

Add the server config to `claude_desktop_config.json` under `mcpServers`. Choose the block matching your setup:

_Refer to the [ID Reference Guide](#-id-reference-guide) for more information about the IDs used below._

**⚠️ Important Notes:**
- **🍎 macOS Users:** use the full path: `"/Users/yourusername/.local/bin/uvx"` instead of just `"uvx"`

<details>
<summary>🔵 Config: uvx + Service Account (Recommended)</summary>

```json
{
  "mcpServers": {
    "google-workspace": {
      "command": "uvx",
      "args": ["temy-google-workspace-mcp@latest"],
      "env": {
        "SERVICE_ACCOUNT_PATH": "/full/path/to/your/service-account-key.json",
        "DRIVE_FOLDER_ID": "your_shared_folder_id_here"
      }
    }
  }
}
```

**🍎 macOS Note:** If you get a `spawn uvx ENOENT` error, use the full path to `uvx`:
```json
{
  "mcpServers": {
    "google-workspace": {
      "command": "/Users/yourusername/.local/bin/uvx",
      "args": ["temy-google-workspace-mcp@latest"],
      "env": {
        "SERVICE_ACCOUNT_PATH": "/full/path/to/your/service-account-key.json",
        "DRIVE_FOLDER_ID": "your_shared_folder_id_here"
      }
    }
  }
}
```
*Replace `yourusername` with your actual username.*
</details>

<details>
<summary>🔵 Config: uvx + OAuth 2.0</summary>

```json
{
  "mcpServers": {
    "google-workspace": {
      "command": "uvx",
      "args": ["temy-google-workspace-mcp@latest"],
      "env": {
        "CREDENTIALS_PATH": "/full/path/to/your/credentials.json",
        "TOKEN_PATH": "/full/path/to/your/token.json"
      }
    }
  }
}
```
*Note: A browser may open for Google login on first use. Ensure TOKEN_PATH is writable.*

**🍎 macOS Note:** If you get a `spawn uvx ENOENT` error, replace `"command": "uvx"` with `"command": "/Users/yourusername/.local/bin/uvx"` (replace `yourusername` with your actual username).
</details>

<details>
<summary>🟡 Config: Development (Running from cloned repo)</summary>

```json
{
  "mcpServers": {
    "temy-google-workspace-local": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/path/to/your/mcp-google-sheets",
        "temy-google-workspace-mcp"
      ],
      "env": {
        "SERVICE_ACCOUNT_PATH": "/path/to/your/mcp-google-sheets/service_account.json",
        "DRIVE_FOLDER_ID": "your_drive_folder_id_here"
      }
    }
  }
}
```
*Note: Use `--directory` flag to specify the project path, and adjust paths to match your actual workspace location.*
</details>

---

## 💬 Example Prompts for Claude

Once connected, try prompts like:

**Google Sheets:**
*   "List all spreadsheets I have access to."
*   "Create a new spreadsheet titled 'Quarterly Sales Report Q3 2024'."
*   "In the 'Quarterly Sales Report' spreadsheet, get the data from Sheet1 range A1 to E10."
*   "In my 'Project Tasks' spreadsheet, Sheet 'Tasks', update cell B2 to 'In Progress'."

**Google Docs:**
*   "List all documents in my workspace folder."
*   "Create a new document called 'Meeting Notes' with the heading 'Team Sync - Dec 15'."
*   "Read the content of document with ID `abc123xyz`."
*   "In document `abc123xyz`, find 'Q4 2024' and replace with 'Q1 2025'."
*   "Get the formatted content of document `abc123xyz` showing headings and styles."
*   "Insert text 'Next Steps:\n1. Review feedback\n2. Update timeline' at the end of document `abc123xyz`."
*   "Format text from index 1 to 20 in document `abc123xyz` as HEADING_1 and bold."

---

## 🆔 ID Reference Guide

Use the following reference guide to find the various IDs referenced throughout the docs:

```
Google Cloud Project ID:
  https://console.cloud.google.com/apis/dashboard?project=sheets-mcp-server-123456
                                                          └───── Project ID ─────┘

Google Drive Folder ID:
  https://drive.google.com/drive/u/0/folders/1xcRQCU9xrNVBPTeNzHqx4hrG7yR91WIa
                                             └────────── Folder ID ──────────┘

Google Sheets Spreadsheet ID:
  https://docs.google.com/spreadsheets/d/25_-_raTaKjaVxu9nJzA7-FCrNhnkd3cXC54BPAOXemI/edit
                                         └───────────── Spreadsheet ID ─────────────┘

Google Docs Document ID:
  https://docs.google.com/document/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit
                                     └────────────── Document ID ──────────────┘
```

---

## 🤝 Contributing

Contributions are welcome! Please open an issue to discuss bugs or feature requests. Pull requests are appreciated.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Credits

*   Built with [FastMCP](https://github.com/cognitiveapis/fastmcp).
*   Forked from [xing5/mcp-google-sheets](https://github.com/xing5/mcp-google-sheets) with Google Docs integration added.
*   Uses Google API Python Client libraries.
