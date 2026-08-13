#!/usr/bin/env python3
"""
1A Soccer Schedule Scraper
Scrapes your personal schedule from https://1asoccer.ezfacility.com

Uses Firefox + in-browser fetch for reCAPTCHA bypass, then intercepts
the FullCalendar XHR responses to capture booked sessions.
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timedelta

from playwright.sync_api import sync_playwright

BASE_URL = "https://1asoccer.ezfacility.com"


def main():
    parser = argparse.ArgumentParser(description="Scrape 1A Soccer schedule")
    parser.add_argument("--username", "-u")
    parser.add_argument("--password", "-p")
    parser.add_argument("--output", "-o", default="schedule.json")
    parser.add_argument("--retries", type=int, default=15)
    args = parser.parse_args()

    username = args.username or os.environ.get("EZFACILITY_USERNAME", "")
    password = args.password or os.environ.get("EZFACILITY_PASSWORD", "")

    if not username or not password:
        print("ERROR: Provide credentials via --username/--password or env vars", file=sys.stderr)
        sys.exit(1)

    all_bookings = []
    all_available = []

    with sync_playwright() as p:
        browser = p.firefox.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1280, "height": 800},
            locale="en-US",
            timezone_id="America/Chicago",
        )
        page = context.new_page()

        # Capture JSON responses
        captured = []
        def on_response(response):
            if "1asoccer" not in response.url or response.status != 200:
                return
            ct = response.headers.get("content-type", "")
            if "json" not in ct:
                return
            try:
                captured.append({"url": response.url, "body": response.json()})
            except Exception:
                pass
        page.on("response", on_response)

        # Load Sessions page first (establishes location context)
        print("Loading Sessions page...")
        page.goto(f"{BASE_URL}/Sessions", wait_until="networkidle")
        page.wait_for_timeout(3000)

        # Grab available sessions from the initial load
        for c in captured:
            body = c["body"]
            if isinstance(body, list) and body and isinstance(body[0], dict) and "title" in body[0]:
                all_available.extend(body)

        # Login
        logged_in = False
        for i in range(1, args.retries + 1):
            print(f"Login attempt {i}/{args.retries}...", end=" ", flush=True)
            page.goto(f"{BASE_URL}/Login", wait_until="networkidle")
            page.wait_for_timeout(4000)

            result = page.evaluate("""([u, p]) => {
                return new Promise((resolve) => {
                    const csrf = document.querySelector('input[name="__RequestVerificationToken"]');
                    const siteKey = document.querySelector('#RecaptchaSiteKey');
                    if (!csrf || !siteKey) { resolve({error: 'missing'}); return; }
                    function doLogin(t) {
                        const fd = new URLSearchParams();
                        fd.append('__RequestVerificationToken', csrf.value);
                        fd.append('Username', u); fd.append('Password', p);
                        fd.append('RememberMe', 'true'); fd.append('LoginFromPublicView', 'false');
                        fd.append('g-recaptcha-response', t); fd.append('g-recaptcha-number', '');
                        fetch('/Login/_LoginForm', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                                      'X-Requested-With': 'XMLHttpRequest'},
                            body: fd.toString(), credentials: 'same-origin',
                        }).then(r => r.json().then(b => resolve({status: r.status, body: b})))
                          .catch(e => resolve({error: e.message}));
                    }
                    if (typeof grecaptcha !== 'undefined' && grecaptcha.execute)
                        grecaptcha.execute(siteKey.value, {action: 'login'}).then(doLogin).catch(() => doLogin(''));
                    else doLogin('');
                });
            }""", [username, password])

            if result and result.get("status") == 200 and "login failed" not in json.dumps(result.get("body", {})).lower():
                try:
                    name = json.loads(result["body"]["data"]["data"]).get("clientName", "Unknown")
                except Exception:
                    name = "Unknown"
                print(f"SUCCESS → {name}")
                logged_in = True
                break
            else:
                print("failed (reCAPTCHA)")
                time.sleep(2)

        if not logged_in:
            print("All login attempts failed. Try running from a non-cloud environment.")
            browser.close()
            sys.exit(1)

        # Navigate to MySchedule and capture booked sessions
        captured.clear()
        print("Loading My Schedule...")
        page.goto(f"{BASE_URL}/MySchedule", wait_until="networkidle")
        page.wait_for_timeout(8000)

        if "login" in page.url.lower():
            print("Session lost — redirected to login.")
            browser.close()
            sys.exit(1)

        # Process initial page load responses
        booked_url_template = None
        for c in captured:
            if "GetBookedReservations" in c["url"]:
                booked_url_template = c["url"]

        # Collect booked reservations from captured responses
        for c in captured:
            if "BookedReservations" in c["url"] or "FilterResults" in c["url"]:
                body = c["body"]
                if isinstance(body, list):
                    for item in body:
                        if isinstance(item, dict) and item.get("title"):
                            all_bookings.append(item)

        print(f"  Current week from page load: {len(all_bookings)} session(s)")

        # Navigate calendar using the correct button selectors
        print("\nScanning future weeks...")
        for week in range(6):
            captured.clear()
            try:
                btn = page.query_selector(".calendar-next")
                if btn:
                    btn.click()
                    page.wait_for_timeout(5000)
                    count = 0
                    for c in captured:
                        if "BookedReservations" in c["url"]:
                            body = c["body"]
                            if isinstance(body, list):
                                for item in body:
                                    if isinstance(item, dict) and item.get("title"):
                                        all_bookings.append(item)
                                        count += 1
                    print(f"  Week +{week+1}: {count} session(s)")
                else:
                    print(f"  Week +{week+1}: next button not found")
                    break
            except Exception as e:
                print(f"  Week +{week+1}: error - {e}")

        # Go back to today
        try:
            today_btn = page.query_selector(".calendar-today")
            if today_btn:
                today_btn.click()
                page.wait_for_timeout(3000)
        except Exception:
            pass

        print("Scanning past weeks...")
        for week in range(4):
            captured.clear()
            try:
                btn = page.query_selector(".calendar-prev")
                if btn:
                    btn.click()
                    page.wait_for_timeout(5000)
                    count = 0
                    for c in captured:
                        if "BookedReservations" in c["url"]:
                            body = c["body"]
                            if isinstance(body, list):
                                for item in body:
                                    if isinstance(item, dict) and item.get("title"):
                                        all_bookings.append(item)
                                        count += 1
                    print(f"  Week -{week+1}: {count} session(s)")
                else:
                    print(f"  Week -{week+1}: prev button not found")
                    break
            except Exception as e:
                print(f"  Week -{week+1}: error - {e}")

        browser.close()

    # Deduplicate bookings by ID
    seen = set()
    unique_bookings = []
    for s in all_bookings:
        sid = s.get("id", str(s))
        if sid not in seen:
            seen.add(sid)
            unique_bookings.append(s)

    # Format and display
    def fmt(s):
        start_dt = end_dt = None
        for raw, which in [(s.get("start", ""), "s"), (s.get("end", ""), "e")]:
            if raw and "T" in str(raw):
                try:
                    dt = datetime.fromisoformat(raw.split(".")[0])
                    if which == "s": start_dt = dt
                    else: end_dt = dt
                except Exception:
                    pass
        spots = None
        if s.get("classSize") is not None and s.get("currentClassSize") is not None:
            spots = s["classSize"] - s["currentClassSize"]
        return {
            "title": s.get("title", ""),
            "date": start_dt.strftime("%A, %B %d, %Y") if start_dt else "",
            "sort_key": start_dt.isoformat() if start_dt else "",
            "start_time": start_dt.strftime("%I:%M %p") if start_dt else "",
            "end_time": end_dt.strftime("%I:%M %p") if end_dt else "",
            "tz": s.get("timeZoneAbbreviation", ""),
            "coach": s.get("resourceName", ""),
            "spots_left": spots,
            "can_cancel": s.get("canCancelReservation", False),
        }

    booked = sorted([fmt(s) for s in unique_bookings if s.get("title")], key=lambda x: x["sort_key"])

    print(f"\n{'─'*60}")
    print(f"  YOUR BOOKED SESSIONS ({len(booked)})")
    print(f"{'─'*60}")
    if not booked:
        print("  (none found)")
    else:
        cur_date = None
        for s in booked:
            if s["date"] != cur_date:
                cur_date = s["date"]
                print(f"\n  📅 {cur_date}")
            coach = f" with {s['coach']}" if s["coach"] else ""
            cancel = " ✅ Can Cancel" if s.get("can_cancel") else ""
            print(f"     ⚽ {s['title']}")
            if s["start_time"]:
                print(f"        🕐 {s['start_time']} – {s['end_time']} {s['tz']}")
            if coach:
                print(f"        👤{coach}")
            if cancel:
                print(f"        {cancel}")

    # Save
    with open(args.output, "w") as f:
        json.dump({
            "scraped_at": datetime.now().isoformat(),
            "my_booked_sessions": booked,
            "raw_bookings": unique_bookings,
        }, f, indent=2, default=str)

    print(f"\n{'='*60}")
    print(f"  Booked sessions: {len(booked)}")
    print(f"  Saved to {args.output}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
