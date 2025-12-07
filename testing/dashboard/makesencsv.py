#!/usr/bin/env python3
"""
makesencsv.py
Simulates the Adafruit soil capacitance sensor and writes to `live.csv`.

Key points / assumptions:
- The real sensor reports capacitance (pF); the supplied transfer function is used:
    Moisture (%) = 0.1428 * Capacitance - 82.2140
  So we simulate capacitances that produce plausible moisture values (~0-100%).
- We sample at 10 Hz (every 0.1 s).
  Justification: capacitance-based soil sensors are relatively slow and stable;
  10 Hz gives enough samples for averaging without excessive CPU / disk load. The IMU will be sampled faster.
- Each row written: timestamp (unix float), capacitance (float), moisture (%), temperature (°C).
- Capacitance range chosen so moisture maps roughly to 0–100%:
    C = (Moisture + 82.2140) / 0.1428 => for moisture 0..100 => C ≈ 576 .. 1263
- Capacitance baseline slowly drifts between experiments; added Gaussian noise for realism.

Run:
    python makesencsv.py
"""
import csv
import random
import time
import os
import math

OUTFILE = 'live.csv'
SAMPLE_INTERVAL = 0.1   # seconds => 10 Hz

# Transfer function constants (from you)
A = 0.1428
B = -82.2140

# Helper to convert capacitance -> moisture %
def capacitance_to_moisture(cap):
    return A * cap + B

# Simulate a slowly varying baseline capacitance (to mimic moving between spots)
baseline = 800.0  # starting capacitance (pF-ish arbitrary units)
baseline_direction = 1

# Ensure header exists if file empty
def ensure_header():
    if not os.path.exists(OUTFILE) or os.stat(OUTFILE).st_size == 0:
        with open(OUTFILE, 'w', newline='') as csvfile:
            fieldnames = ['timestamp', 'capacitance', 'moisture_pct', 'temperature_c']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

ensure_header()
print(f"[makesencsv] Writing samples to {OUTFILE} at {1/SAMPLE_INTERVAL:.1f} Hz. Ctrl-C to stop.")

try:
    while True:
        # slowly vary baseline (simulate small changes between measurements)
        baseline += baseline_direction * random.uniform(0.0, 0.5)
        if baseline < 580:
            baseline = 580
            baseline_direction = 1
        if baseline > 1260:
            baseline = 1260
            baseline_direction = -1

        # Simulate one sample: capacitance = baseline + small noise + occasional transient
        noise = random.gauss(0, 2.0)  # small gaussian noise
        transient = 0.0
        if random.random() < 0.01:
            # 1% chance of a little poke or transient change
            transient = random.uniform(-10, 10)

        capacitance = baseline + noise + transient
        moisture = capacitance_to_moisture(capacitance)

        # Soil temperature (°C) — plausible range 2–35 °C depending on environment
        # We add small diurnal drift using sin of time for realism plus noise
        t = time.time()
        diurnal = 3.0 * math.sin(t / (3600 * 12.0))  # slow sinusoid (12-hour period mock)
        temperature = 15 + diurnal + random.gauss(0, 0.6)

        with open(OUTFILE, 'a', newline='') as csvfile:
            fieldnames = ['timestamp', 'capacitance', 'moisture_pct', 'temperature_c']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writerow({
                'timestamp': t,
                'capacitance': round(capacitance, 3),
                'moisture_pct': round(moisture, 3),
                'temperature_c': round(temperature, 3)
            })

        time.sleep(SAMPLE_INTERVAL)

except KeyboardInterrupt:
    print("\n[makesencsv] Stopped by user.")
