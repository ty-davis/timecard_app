# Launching Timecard Miniclient

## Windows (Start Menu)

### Option 1: Using PowerShell script (Completely hidden - Recommended)

1. **Create a shortcut:**
   - Right-click on `launch_timecard.ps1`
   - Select "Create shortcut"
   - Right-click the shortcut → Properties
   - In the "Target:" field, prefix with: `powershell.exe -WindowStyle Hidden -File `
   - Full target should look like: `powershell.exe -WindowStyle Hidden -File "C:\path\to\launch_timecard.ps1"`
   - Click "Change Icon" (optional: add a custom icon)
   - Click OK

2. **First-time setup (if needed):**
   - If scripts won't run, open PowerShell as Administrator and run:
   - `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser`

### Option 2: Using BAT file with hidden window

1. **Create a shortcut:**
   - Right-click on `launch_timecard.bat`
   - Select "Create shortcut"
   - Right-click the shortcut → Properties
   - In the "Run:" dropdown, select **"Minimized"**
   - Click "Change Icon" (optional: add a custom icon)
   - Click OK

   Note: "Minimized" will briefly show the window. For completely hidden, use Option 1 or 3.

### Option 3: Using VBS script (Completely hidden window)

1. **Create a shortcut:**
   - Right-click on `launch_timecard.vbs`
   - Select "Create shortcut"
   - Right-click the shortcut → Properties
   - Click "Change Icon" (optional: add a custom icon)
   - Click OK

2. **Add to Start Menu:**
   - Press `Win + R`, type `shell:programs` and press Enter
   - Copy the shortcut to this folder
   - The app will now appear in your Start Menu

3. **Pin to Start (Windows 10/11):**
   - Open Start Menu
   - Find "launch_timecard"
   - Right-click → "Pin to Start"

## Linux (.desktop file)

1. **Edit the .desktop file:**
   ```bash
   cd /path/to/timecard_app/miniclient
   
   # Replace %INSTALL_PATH% with the actual path
   sed -i "s|%INSTALL_PATH%|$(pwd)|g" timecard.desktop
   
   # Make it executable
   chmod +x timecard.desktop
   ```

2. **Install for current user:**
   ```bash
   # Copy to local applications
   cp timecard.desktop ~/.local/share/applications/
   
   # Update desktop database
   update-desktop-database ~/.local/share/applications/
   ```

3. **Install system-wide (requires sudo):**
   ```bash
   sudo cp timecard.desktop /usr/share/applications/
   sudo update-desktop-database /usr/share/applications/
   ```

4. **Optional: Add an icon:**
   - Place an icon file (PNG recommended) in the miniclient folder as `icon.png`
   - Or update the Icon= line in timecard.desktop with the full path to your icon

## Notes

- The virtual environment must be set up first: `python -m venv venv && venv/Scripts/activate && pip install -r requirements.txt` (Windows) or `python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt` (Linux)
- Make sure the .env file is configured with the correct API_URL
- On Linux, if the app doesn't appear immediately, try logging out and back in
