# Project brief

## Description

Three-panel multilingual Aurecon office clock with live weather and relative-time commentary for a 3840 × 804 gallery display.

## Build brief

Purpose:
Create a new independent version of the office triptych clock for NVIDIA Shield and Enplug playback.

Layout:
- Fixed 3840 × 804 canvas, three equal 1280px panels.
- Centre background #373A36.
- Side backgrounds #1C1B1C.
- 2px dividers #BBC6C3.
- Automatic mobile landscape scaling.

Title row:
- Always English city and country.
- Live local HH:MM:SS day and date on the left.
- Live current temperature and short weather condition aligned right.
- Weather from Open-Meteo current conditions with resilient fallback text and periodic refresh.

Messages:
- Three typed lines in every panel.
- First and third lines use the off-white text colour.
- Second line uses Aurecon green #89C925.
- Centre remains Melbourne and updates every minute.
- Side offices rotate every 30 seconds, with the right side offset by 15 seconds.
- Third line for Melbourne uses a short day/time-of-day/weather observation.
- Third line for side offices compares local time with Melbourne, including same-time, ahead and behind copy.
- Avoid identical wording across panels.

Fonts:
- Open Sans for all sans-serif title and utility text.
- PT Serif Bold for all serif message lines.
- Store both font files physically in assets/fonts in this repository with licence files.

Performance and privacy:
- Vanilla HTML/CSS/JavaScript only.
- No framework or WebGL.
- Visible fallback content before JavaScript runs.
- noindex, nofollow, noarchive and robots.txt Disallow: /.
- Weather failure must never blank the clock.

QC:
- Browser render at 3840 × 804 and 844 × 390.
- Confirm all three lines fit for all offices.
- Confirm live weather labels align right without collision.
- Confirm relative-time calculations across DST and half-hour differences.
- Confirm left/right 30-second rotation and 15-second offset.
- Confirm local fonts are loaded from repository assets.
