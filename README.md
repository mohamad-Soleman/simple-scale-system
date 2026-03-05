# POS Scale App

Touch-friendly weighing and label printing app for a butcher shop. Reads live weight from a serial scale (Windows COM port), lets you select products or use a "Generic Item" with custom price per kg, and prints labels to the Windows default (thermal) printer.

## Requirements

- Python 3.11
- Windows (serial scale + default printer)

## Setup

1. Clone the repo and create a virtual environment:

   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Running

From the project root:

```bash
python main.py
```

- **Weight** appears at the top (live from scale on COM6 @ 9600).
- **Products** are loaded from `products.db` in the same folder as the script (or EXE). If the file is missing, the app creates an empty DB; add rows manually (see below).
- **Generic Item**: select it, then click "Set price per kg" to open the numeric keypad and enter price (₪).
- **Print**: select a product (or Generic Item with a set price), then click Print to send a label to the default Windows printer.

**Shortcuts**

- **F11**: Toggle full screen.
- **Escape**: Close app.

## Building the EXE (PyInstaller)

Build on Windows with Python 3.11 and dependencies installed.

**One-folder (recommended for PyQt6 + pywin32):**

```bash
pyinstaller scale_app.spec
```

Output: `dist/ScaleApp/ScaleApp.exe` plus DLLs and dependencies. Copy the whole `ScaleApp` folder to the scale machine.

**What to ship next to the EXE**

- Place `products.db` in the **same folder** as `ScaleApp.exe` (or the app will create an empty one on first run).
- Optional: `config.ini` to override COM port, baud, currency, or printer font (see below).
- **Logs**: `scale_app.log` is written in the same folder as the EXE.

### Building a release via GitHub Actions

1. Go to **Actions** → **Build and release** → **Run workflow**.
2. Enter a **version tag** (e.g. `v1.0.0`) and run.
3. When the workflow finishes, open **Releases**; the new release will have two ZIPs:
   - **Windows:** `POS-Scale-App-<tag>-windows.zip` — extract and run `ScaleApp.exe`.
   - **Mac:** `POS-Scale-App-<tag>-mac.zip` — extract and run the `ScaleApp` binary (e.g. `./ScaleApp` in Terminal). Set the serial port in `config.ini` (e.g. `/dev/cu.usbserial-*`). Printing is Windows-only unless a Mac printer path is added.
4. Both ZIPs include the app, `products.db` (empty schema), and `config.ini` (sample).

**One-file (single EXE)**  
You can switch the spec to onefile; the DB and log are still read/written in the directory where the EXE lives (not inside the bundle). Onefile may be slower on first run and can trigger antivirus; onedir is more reliable.

## Configuration (optional)

Create `config.ini` next to the script or EXE:

```ini
[serial]
port = COM6
baud = 9600

[app]
currency = ₪

[printer]
font_height = 120
```

## Editing the SQLite database (products)

There is no in-app UI for adding/editing products. Edit `products.db` manually with any SQLite tool (e.g. [DB Browser for SQLite](https://sqlitebrowser.org/)).

**Schema**

```sql
CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    price_per_kg REAL NOT NULL,
    category TEXT,
    is_active INTEGER NOT NULL DEFAULT 1
);
```

- **name**: Display name (e.g. "Chicken Breast").
- **price_per_kg**: Price in ILS per kg.
- **category**: Optional (for future grouping).
- **is_active**: `1` = show in grid, `0` = hide.

Add or update rows, then restart the app (or it will pick up changes on next launch).

## Troubleshooting

### COM port / scale not connecting

- Close any other app using the scale (e.g. PuTTY, another terminal).
- Check Device Manager for the correct COM port and that the scale driver is installed.
- Set `port` in `config.ini` if your scale uses a different COM port.

### Printer not working

- Set the thermal label printer as the **Windows default printer**.
- Check that the printer driver is installed and the device is online.
- Errors are written to `scale_app.log`; check that file for details.
- If labels look wrong (size/position), adjust `font_height` in `config.ini` or in the printer driver’s label size settings.

### Logs

- **Location**: `scale_app.log` in the same directory as the script or EXE.
- Use it to debug serial errors, print failures, and DB issues.

## Project layout

```
app/
  config.py         # Paths, COM, currency, label font
  models/           # Product dataclass
  scale/             # Serial reader + weight parser
  printer/           # Label printer (Windows GDI)
  database/         # SQLite product repository
  services/          # Price calculation
  ui/                # Main window, keypad dialog
main.py              # Entry point
requirements.txt
scale_app.spec       # PyInstaller spec
```

## License

Open source; see repository license.
