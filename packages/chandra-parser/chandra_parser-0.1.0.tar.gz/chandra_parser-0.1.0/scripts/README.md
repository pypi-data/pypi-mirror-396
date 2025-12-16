# macOS Quick Action Setup

This guide will help you add a right-click menu option to parse PDFs directly from Finder. No coding experience required!

## Before You Start

You'll need:

1. **A Datalab API key** (required) — Get one free at [datalab.to](https://www.datalab.to)
2. **An OpenAI API key** (optional) — Only needed if you want to filter out logos and decorative images. Get one at [platform.openai.com](https://platform.openai.com)
3. **uv installed** — A Python package manager. Install it by opening Terminal and running:
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

## Step 1: Download Chandra Parser

1. Open **Terminal** (press `Cmd + Space`, type "Terminal", press Enter)

2. Copy and paste this command, then press Enter:
   ```bash
   cd ~/Documents && git clone https://github.com/resoai/chandra-parser.git
   ```
   This downloads Chandra Parser to your Documents folder.

3. Install dependencies:
   ```bash
   cd ~/Documents/chandra-parser && uv sync
   ```

## Step 2: Add Your API Keys

1. In Terminal, run this command to create your configuration file:
   ```bash
   nano ~/Documents/chandra-parser/.env
   ```

2. Type the following (replace with your actual keys):
   ```
   DATALAB_API_KEY=your_datalab_key_here
   OPENAI_API_KEY=your_openai_key_here
   ```

3. Save the file: Press `Ctrl + O`, then `Enter`, then `Ctrl + X`

## Step 3: Make the Script Executable

Run this command in Terminal:

```bash
chmod +x ~/Documents/chandra-parser/scripts/parse_pdf.sh
```

## Step 4: Create the Quick Action in Automator

1. Open **Automator** (press `Cmd + Space`, type "Automator", press Enter)

2. Click **New Document**

3. Select **Quick Action** and click **Choose**

4. At the top of the window, configure the workflow:
   - Change "Workflow receives current" to **PDF files**
   - Make sure "in" is set to **Finder**
   - The "Image" dropdown is optional (you can pick an icon)

5. In the left sidebar, search for "Run Shell Script"

6. Drag **Run Shell Script** to the right side of the window

7. In the "Run Shell Script" box that appears:
   - Change "Pass input" dropdown to **as arguments**
   - Delete any existing text in the script box
   - Paste this exactly:
     ```bash
     for f in "$@"; do
         "$HOME/Documents/chandra-parser/scripts/parse_pdf.sh" "$f" &
     done
     ```

8. Save the Quick Action:
   - Press `Cmd + S`
   - Name it: `Parse PDF with Chandra`
   - Click **Save**

9. Close Automator

## Step 5: Test It Out

1. Find any PDF file in Finder

2. Right-click (or Control-click) the PDF

3. Look for **Quick Actions** → **Parse PDF with Chandra**

4. You'll see notifications:
   - "Processing: filename" when it starts
   - "Complete!" when finished (the output folder will open automatically)
   - "Failed" if there's an error

The parsed output will appear in the same folder as your PDF, in a new folder named `yourfile_parsed/`.

## Troubleshooting

### Quick Action doesn't appear in the menu

1. Open **System Settings** (click the Apple menu → System Settings)
2. Click **Privacy & Security** in the left sidebar
3. Scroll down and click **Extensions**
4. Click **Finder**
5. Make sure **Parse PDF with Chandra** is checked
6. Restart Finder: Open Terminal and run `killall Finder`

### "Processing" notification appears but nothing happens

Your API keys might not be set up correctly. To check:

1. Open Terminal
2. Run: `cat ~/Documents/chandra-parser/.env`
3. Verify your keys are there and have no extra spaces

### Error: "command not found: uv"

The uv tool isn't installed. Run this in Terminal:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```
Then close and reopen Terminal.

### Parser runs but output is poor quality

Make sure you have a valid Datalab API key. The free tier has usage limits — check your account at [datalab.to](https://www.datalab.to).

### I installed Chandra somewhere else

If you didn't install to `~/Documents/chandra-parser`, you need to update the path in two places:

1. **The Automator script** — Open Automator, find the Quick Action, and update the path
2. **The parse_pdf.sh script** — Edit line 8 to point to your installation:
   ```bash
   CHANDRA_DIR="/your/actual/path/to/chandra-parser"
   ```

## Updating Chandra Parser

To get the latest version:

1. Open Terminal
2. Run:
   ```bash
   cd ~/Documents/chandra-parser && git pull && uv sync
   ```
