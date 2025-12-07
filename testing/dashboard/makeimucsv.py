#!/usr/bin/env python3
"""
makeimucsv.py
Simulates the Adafruit ICM-20948 IMU (MPU-9250 upgrade) and writes to `imu.csv`.

Key points / assumptions:
- The real ICM-20948 provides:
    - 3-axis accelerometer (m/s^2)
    - 3-axis gyroscope (°/s)
    - 3-axis magnetometer (uT)
    - on-chip temperature (°C)
  It does NOT provide absolute geographic coordinates (no GPS). Position recovery from IMU-only
  is possible in principle but quickly drifts — for mapping in the dashboard we simulate a short-range
  local position by integrating acceleration with damping.
- We sample at 50 Hz here (SAMPLE_HZ = 50). Justification: IMU sensors support high rates; 50 Hz
  is a reasonable compromise for a slowly moving/stationary robot head insertion and gives enough
  temporal resolution for mapping to soil samples.
- Each row written: timestamp, ax, ay, az, gx, gy, gz, mx, my, mz, imu_temp_c, pos_x_m, pos_y_m
- Positions pos_x_m, pos_y_m are meters in a local coordinate frame (origin at start). They are simulated
  by low-noise integration with damping to avoid runaway drift.
- The dashboard will merge imu.csv with live.csv by timestamp to map moisture to positions.

Run:
    python3 makeimucsv.py
"""
import csv
import time
import os
import random
import math

OUTFILE = 'imu.csv'
SAMPLE_HZ = 50.0
SAMPLE_INTERVAL = 1.0 / SAMPLE_HZ

# Simple simulation parameters
GRAVITY = 9.80665  # m/s^2
damping = 0.8      # velocity damping to limit drift when integrating accel

# Initial state
pos_x = 0.0
pos_y = 0.0
vel_x = 0.0
vel_y = 0.0

def ensure_header():
    if not os.path.exists(OUTFILE) or os.stat(OUTFILE).st_size == 0:
        with open(OUTFILE, 'w', newline='') as csvfile:
            fieldnames = [
                'timestamp',
                'ax', 'ay', 'az',
                'gx', 'gy', 'gz',
                'mx', 'my', 'mz',
                'imu_temp_c',
                'pos_x_m', 'pos_y_m'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

ensure_header()
print(f"[makeimucsv] Writing samples to {OUTFILE} at {SAMPLE_HZ:.0f} Hz. Ctrl-C to stop.")

try:
    while True:
        t = time.time()

        # Simulate small accelerations: when "robot" is stationary the only accel is gravity with small noise
        # We'll simulate small random jerks occasionally to represent robot movement.
        jerk_chance = 0.005
        if random.random() < jerk_chance:
            ax = random.uniform(-1.0, 1.0)
            ay = random.uniform(-1.0, 1.0)
        else:
            ax = random.gauss(0, 0.02)  # near-zero lateral accelerations
            ay = random.gauss(0, 0.02)

        # az includes gravity; assume z-axis aligned with gravity for simplicity
        az = -GRAVITY + random.gauss(0, 0.05)

        # Gyroscope simulated in deg/s
        gx = random.gauss(0, 0.5)
        gy = random.gauss(0, 0.5)
        gz = random.gauss(0, 0.5)

        # Magnetometer (uT) — simulate Earth's field around 25 to 60 uT with small noise
        mx = random.gauss(30.0, 1.0)
        my = random.gauss(-5.0, 1.0)
        mz = random.gauss(-40.0, 1.0)

        imu_temp = 30.0 + random.gauss(0, 0.3)  # plausible IMU chip temp (°C)

        # Integrate acceleration -> velocity -> position (simple, with damping)
        vel_x = (vel_x + ax * SAMPLE_INTERVAL) * damping
        vel_y = (vel_y + ay * SAMPLE_INTERVAL) * damping
        pos_x += vel_x * SAMPLE_INTERVAL
        pos_y += vel_y * SAMPLE_INTERVAL

        with open(OUTFILE, 'a', newline='') as csvfile:
            fieldnames = [
                'timestamp',
                'ax', 'ay', 'az',
                'gx', 'gy', 'gz',
                'mx', 'my', 'mz',
                'imu_temp_c',
                'pos_x_m', 'pos_y_m'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writerow({
                'timestamp': t,
                'ax': round(ax, 5),
                'ay': round(ay, 5),
                'az': round(az, 5),
                'gx': round(gx, 4),
                'gy': round(gy, 4),
                'gz': round(gz, 4),
                'mx': round(mx, 3),
                'my': round(my, 3),
                'mz': round(mz, 3),
                'imu_temp_c': round(imu_temp, 3),
                'pos_x_m': round(pos_x, 4),
                'pos_y_m': round(pos_y, 4)
            })

        time.sleep(SAMPLE_INTERVAL)

except KeyboardInterrupt:
    print("\n[makeimucsv] Stopped by user.")
