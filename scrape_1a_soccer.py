#!/usr/bin/env python3
"""
1A Soccer Schedule Scraper
Scrapes your personal schedule from https://1asoccer.ezfacility.com

Usage:
    python scrape_1a_soccer.py --username YOUR_EMAIL --password YOUR_PASSWORD
    python scrape_1a_soccer.py  # (uses env vars EZFACILITY_USERNAME / EZFACILITY_PASSWORD)

Output:
    - Prints schedule to console
    - Saves to schedule.json
"""

import argparse
import json
import os
import sys
from datetime import datetime

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from bs4 import BeautifulSoup


BASE_URL = "https://1asoccer.ezfacility.com"
MY_SCHEDULE_URL = f"{BASE_URL}/MySchedule"
SESSIONS_URL = f"{BASE_URL}/Sessions"


def login(page, username: str, password: str) -> bool:
    """Log into the EZFacility portal."""
    page.goto(SESSIONS_URL, wait_until="networkidle")
    page.wait_for_timeout(2000)

    try:
        page.click("a:has-text('Login')", timeout=5000)
        page.wait_for_timeout(1000)
    except PlaywrightTimeout:
        pass

    try:
        page.fill("input#Username", username, timeout=5000)
        page.fill("input#Password", password)
    except PlaywrightTimeout:
        page.fill("input[name='Username']", username)
        page.fill("input[name='Password']", password)

    page.click("button:has-text('Log In')")

    try:
        page.wait_for_selector("a:has-text('Logout')", timeout=15000)
        return True
    except PlaywrightTimeout:
        page.wait_for_timeout(3000)
        if page.query_selector("a:has-text('Logout')"):
            return True
        print("ERROR: Login failed. Check your credentials.", file=sys.stderr)
        return False


def scrape_my_schedule_page(page) -> list[dict]:
    """Navigate to My Schedule and scrape the HTML content."""
    page.goto(MY_SCHEDULE_URL, wait_until="networkidle")
    page.wait_for_timeout(4000)

    content = page.content()
    soup = BeautifulSoup(content, "html.parser")

    sessions = []

    selectors = [
        "table tbody tr",
        ".schedule-item",
        ".session-item",
        ".list-group-item",
        ".card",
        "[class*='schedule']",
        "[class*='booking']",
        "[class*='event']",
        ".panel-body",
    ]

    for selector in selectors:
        elements = soup.select(selector)
        for el in elements:
            text = el.get_text(separator=" | ", strip=True)
            if text and len(text) > 15 and "Login" not in text and "Username" not in text:
                sessions.append(parse_element(el, text))

    return deduplicate(sessions)


def parse_element(element, text: str) -> dict:
    """Parse an HTML element into a session dict."""
    entry = {"raw_text": text}

    for link in element.find_all("a", href=True):
        entry.setdefault("link", link["href"])

    for el in element.find_all(class_=lambda c: c and any(k in (c or "").lower() for k in ["date", "when"])):
        entry["date"] = el.get_text(strip=True)

    for el in element.find_all(class_=lambda c: c and "time" in (c or "").lower()):
        entry["time"] = el.get_text(strip=True)

    for el in element.find_all(class_=lambda c: c and any(k in (c or "").lower() for k in ["title", "name"])):
        entry["title"] = el.get_text(strip=True)

    return entry


def deduplicate(sessions: list[dict]) -> list[dict]:
    """Remove duplicate entries based on raw_text."""
    seen = set()
    unique = []
    for s in sessions:
        key = s.get("raw_text", "")
        if key not in seen:
            seen.add(key)
            unique.append(s)
    return unique


def format_api_session(session: dict) -> dict:
    """Format a raw API session object into a clean, readable dict."""
    start = session.get("start", "")
    end = session.get("end", "")

    start_dt = None
    end_dt = None
    if start:
        try:
            clean = start.split(".")[0] if "." in start else start
            start_dt = datetime.fromisoformat(clean)
        except (ValueError, AttributeError):
            pass
    if end:
        try:
            clean = end.split(".")[0] if "." in end else end
            end_dt = datetime.fromisoformat(clean)
        except (ValueError, AttributeError):
            pass

    instructors = []
    for instr in session.get("instructors", []):
        instructors.append(instr.get("Name", ""))

    spots_left = None
    class_size = session.get("classSize")
    current = session.get("currentClassSize")
    if class_size is not None and current is not None:
        spots_left = class_size - current

    return {
        "id": session.get("id"),
        "title": session.get("title", ""),
        "description": session.get("description", ""),
        "date": start_dt.strftime("%A, %B %d, %Y") if start_dt else "",
        "start_time": start_dt.strftime("%I:%M %p") if start_dt else "",
        "end_time": end_dt.strftime("%I:%M %p") if end_dt else "",
        "timezone": session.get("timeZoneAbbreviation", ""),
        "coach": session.get("resourceName", ""),
        "instructors": instructors,
        "class_size": class_size,
        "spots_left": spots_left,
        "venues": [v.get("Name", v) if isinstance(v, dict) else v for v in session.get("venues", [])],
        "can_cancel": session.get("canCancelReservation", False),
    }


def capture_network_data(page) -> tuple[list[dict], list[dict]]:
    """
    Intercept XHR responses that contain schedule/session JSON data.
    Returns (all_sessions, my_bookings).
    """
    all_sessions = []
    my_bookings = []

    def handle_response(response):
        url = response.url.lower()
        if response.status != 200:
            return

        relevant_keywords = ["session", "schedule", "booking", "reservation", "calendar", "myschedule"]
        if not any(kw in url for kw in relevant_keywords):
            return

        try:
            body = response.json()
        except Exception:
            return

        is_personal = any(kw in url for kw in ["myschedule", "mybooking", "myreservation"])

        if isinstance(body, list):
            for item in body:
                if isinstance(item, dict) and ("title" in item or "start" in item):
                    if is_personal:
                        my_bookings.append(item)
                    else:
                        all_sessions.append(item)
        elif isinstance(body, dict):
            items = body.get("data", body.get("items", body.get("sessions", [body])))
            if isinstance(items, list):
                for item in items:
                    if isinstance(item, dict) and ("title" in item or "start" in item):
                        if is_personal:
                            my_bookings.append(item)
                        else:
                            all_sessions.append(item)

    page.on("response", handle_response)
    return all_sessions, my_bookings


def print_schedule(sessions: list[dict], header: str):
    """Pretty-print a list of formatted sessions."""
    print(f"\n{'─'*60}")
    print(f"  {header}")
    print(f"{'─'*60}")

    if not sessions:
        print("  (none found)")
        return

    current_date = None
    for s in sessions:
        date = s.get("date", "")
        if date != current_date:
            current_date = date
            print(f"\n  📅 {date}")

        title = s.get("title", "Unknown")
        start = s.get("start_time", "")
        end = s.get("end_time", "")
        coach = s.get("coach", "")
        spots = s.get("spots_left")

        time_str = f"{start} - {end}" if start and end else ""
        coach_str = f" with {coach}" if coach else ""
        spots_str = f" ({spots} spots left)" if spots is not None else ""

        print(f"     ⚽ {title}")
        if time_str:
            print(f"        🕐 {time_str} {s.get('timezone', '')}")
        if coach_str:
            print(f"        👤{coach_str}")
        if spots_str:
            print(f"        📊{spots_str}")


def main():
    parser = argparse.ArgumentParser(description="Scrape 1A Soccer schedule from EZFacility")
    parser.add_argument("--username", "-u", help="EZFacility username/email")
    parser.add_argument("--password", "-p", help="EZFacility password")
    parser.add_argument("--output", "-o", default="schedule.json", help="Output JSON file")
    parser.add_argument("--no-headless", action="store_true", help="Show browser window")
    parser.add_argument("--available-only", action="store_true",
                        help="Only fetch available sessions (no login needed)")
    args = parser.parse_args()

    username = args.username or os.environ.get("EZFACILITY_USERNAME", "")
    password = args.password or os.environ.get("EZFACILITY_PASSWORD", "")

    need_login = not args.available_only
    if need_login and (not username or not password):
        print("ERROR: Provide credentials via --username/--password or env vars", file=sys.stderr)
        print("       EZFACILITY_USERNAME and EZFACILITY_PASSWORD", file=sys.stderr)
        print("       Or use --available-only to skip login", file=sys.stderr)
        sys.exit(1)

    headless = not args.no_headless

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        )
        page = context.new_page()

        all_sessions_raw, my_bookings_raw = capture_network_data(page)

        logged_in = False
        if need_login:
            print(f"Logging in as {username}...")
            logged_in = login(page, username, password)
            if not logged_in:
                print("Continuing without login (public data only)...", file=sys.stderr)

        if logged_in:
            print("Login successful! Fetching your schedule...")
            my_schedule_html = scrape_my_schedule_page(page)
        else:
            my_schedule_html = []

        print("Fetching available sessions...")
        page.goto(SESSIONS_URL, wait_until="networkidle")
        page.wait_for_timeout(4000)

        browser.close()

    all_formatted = sorted(
        [format_api_session(s) for s in all_sessions_raw
         if s.get("start") and s.get("title") and "T" in str(s.get("start", ""))],
        key=lambda x: x.get("date", "")
    )
    my_formatted = sorted(
        [format_api_session(s) for s in my_bookings_raw
         if s.get("start") and s.get("title") and "T" in str(s.get("start", ""))],
        key=lambda x: x.get("date", "")
    )

    result = {
        "scraped_at": datetime.now().isoformat(),
        "my_booked_sessions": my_formatted,
        "my_schedule_page": my_schedule_html,
        "available_sessions": all_formatted,
        "raw_api_data": {
            "my_bookings": my_bookings_raw,
            "all_sessions": all_sessions_raw,
        },
    }

    with open(args.output, "w") as f:
        json.dump(result, f, indent=2, default=str)

    print_schedule(my_formatted, "YOUR BOOKED SESSIONS")
    print_schedule(all_formatted[:30], f"AVAILABLE SESSIONS (showing first 30 of {len(all_formatted)})")

    print(f"\n{'='*60}")
    print(f"  SCRAPE COMPLETE")
    print(f"{'='*60}")
    print(f"  Your booked sessions: {len(my_formatted)}")
    print(f"  Available sessions:   {len(all_formatted)}")
    print(f"  Output saved to:      {args.output}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
