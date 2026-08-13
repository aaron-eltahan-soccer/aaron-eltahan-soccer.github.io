# 1A Soccer Schedule Scraper

Scrapes your personal soccer schedule from [1A Soccer on EZFacility](https://1asoccer.ezfacility.com/Sessions).

## Setup

```bash
pip install -r requirements.txt
playwright install chromium
```

## Usage

### Option 1: Command-line arguments

```bash
python scrape_1a_soccer.py --username your@email.com --password yourpassword
```

### Option 2: Environment variables

```bash
export EZFACILITY_USERNAME="your@email.com"
export EZFACILITY_PASSWORD="yourpassword"
python scrape_1a_soccer.py
```

### Options

| Flag | Description |
|------|-------------|
| `--username`, `-u` | Your EZFacility login email |
| `--password`, `-p` | Your EZFacility password |
| `--output`, `-o` | Output file path (default: `schedule.json`) |
| `--no-headless` | Show the browser window while scraping |

## Output

The scraper produces a `schedule.json` file containing:

- **my_schedule** — Your personally booked/upcoming sessions
- **available_sessions** — Sessions available to book
- **api_data** — Any raw JSON data captured from network requests

## How It Works

1. Launches a headless Chromium browser via Playwright
2. Navigates to the 1A Soccer EZFacility portal
3. Logs in with your credentials
4. Intercepts network responses containing schedule data
5. Navigates to "My Schedule" and scrapes session details
6. Navigates to "Sessions" to capture available classes
7. Outputs everything to JSON

## Troubleshooting

- **Login fails**: Double-check your email/password. Try with `--no-headless` to watch what happens.
- **Empty results**: The site may load data via XHR calls — the scraper captures those too. Check the `api_data` field in the output.
- **Timeouts**: The site can be slow; the script includes generous wait times but you can increase them if needed.
