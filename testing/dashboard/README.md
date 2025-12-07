# Soil Analyzing Snake Dashboard
A three-part system for simulating soil sensor + IMU data and visualizing experiments through a Dash by Plotly dashboard.

This repository contains:
1. makesencsv.py - Simulates soil capacitance and temperature sensor.
2. makeimucsv.py - Simulates Adafruit ICM-20948 9-DoF IMU.
3. sssdash.py - Dashboard for running experiments and generating scatter + contour maps.

---

## File Overviews

### 1. makesencsv.py
Simulates readings from a soil moisture and temperature sensor.

- Generates capacitance readings at 10 Hz.
- Applies transfer function:
  moisture (%) = 0.1428 * capacitance – 82.2140
- Simulates slow environmental temperature drift.
- Writes continuously to live.csv with columns:
  timestamp, capacitance, moisture_pct, temperature_c

### 2. makeimucsv.py
Simulates a 9-DoF IMU and provides local 2D position estimates.

- Samples at 50 Hz.
- Generates accelerometer, gyroscope, and magnetometer readings.
- Integrates acceleration into pos_x_m, pos_y_m using damped integration.
- Writes continuously to imu.csv with columns:
  timestamp, ax, ay, az, gx, gy, gz, mx, my, mz, imu_temp_c, pos_x_m, pos_y_m

### 3. sssdash.py
Dash by Plotly interactive experiment dashboard.

Features:
- “Start Experiment” and “Stop Experiment” workflow (max three experiments).
- Computes:
  - duration (seconds)
  - average temperature
  - average moisture
  - wildfire risk classification (Low / Medium / High)
- Displays results in a bordered table.
- Scatter plot showing experiment temperatures and moistures.
- Smooth contour plots for temperature and moisture, based on merged IMU–sensor data.
- Experiment location markers placed on heatmaps.
- Single-page layout, non-serif font, optimized for landscape display.

---

## Libraries used
1. makesencsv.py - csv, random, time, os, math
2. makeimuscv.py - csv, random, time, os, math
3. sssdash.py - time, os, Dash, dash_table, Plotly (graph_objects), NumPy, Pandas

## Running the System

Open three split terminals:

### Terminal 1 — Soil Sensor Simulation
    python makesencsv.py

### Terminal 2 — IMU Simulation
    python makeimucsv.py

### Terminal 3 — Dashboard
    python sssdash.py

<img width="1640" height="297" alt="image" src="https://github.com/user-attachments/assets/8b0f458a-4b6f-410b-9fdc-b7de7fbd00f3" />

Then open:
    http://127.0.0.1:8050
    
<img width="1883" height="858" alt="image" src="https://github.com/user-attachments/assets/5aa9070b-86bb-463e-9a6e-681456955224" />


---

## Running an Experiment

1. Click “Start Experiment”.
2. Allow sensor simulators to generate data.
3. Click “Stop Experiment”.
4. Dashboard updates with:
   - duration
   - average temperature
   - average moisture
   - wildfire risk category
   - scatter plot points
   - temperature and moisture heatmaps

Up to 3 experiments are stored and displayed.

---

## Purpose

This system forms the foundation for a soil-analyzing snake robot. In the future:
- Real sensor hardware will replace simulators.
- Motion control via servos can be added with keyboard commands.


