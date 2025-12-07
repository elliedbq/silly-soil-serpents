#!/usr/bin/env python3
"""
sssdash.py
Dashboard for the soil-analyzing snake experiments.

Features (aligned with user spec):
- Two buttons only: "Start Experiment" and "Stop Experiment".
- Each Start→Stop pair becomes an experiment: Experiment 1, then 2, then 3 (Option A).
- Reads:
    live.csv with columns: timestamp, capacitance, moisture_pct, temperature_c
    imu.csv with columns: timestamp, ax.., gx.., mx.., imu_temp_c, pos_x_m, pos_y_m
- For each experiment:
    * Duration in whole seconds (no decimals).
    * Average temperature (°C) over the window.
    * Average moisture (%) over the window.
    * Wildfire risk category based on moisture:
        - Low:    moisture > 40
        - Medium: 20 <= moisture <= 40
        - High:   moisture < 20
- UI:
    * Non-serif font (Arial).
    * Bordered table showing Experiment, Duration, Avg Temp, Avg Moisture, Risk.
    * Risk key box with Low/Medium/High ranges.
    * Scatter plot that includes BOTH temperature and moisture (separate marker series).
    * Two 2D heatmaps (Temperature & Moisture) with titles and dots marking
      where Experiments 1, 2, 3 are geographically (local IMU coords).
- Layout:
    * All content arranged in a landscape-style single page (no scrolling
      required on a typical laptop display): graphs are kept small.
"""

import time
import os

import numpy as np
import pandas as pd

from dash import Dash, dcc, html, Input, Output, State, callback_context
from dash import dash_table
import plotly.graph_objects as go

LIVE_CSV = "live.csv"
IMU_CSV = "imu.csv"

# ---------- Helpers for reading data ----------

def read_live():
    if not os.path.exists(LIVE_CSV):
        return pd.DataFrame(columns=["timestamp", "capacitance", "moisture_pct", "temperature_c"])
    df = pd.read_csv(LIVE_CSV)
    # Ensure correct types & ordering
    if "timestamp" in df.columns:
        df["timestamp"] = df["timestamp"].astype(float)
        df = df.sort_values("timestamp")
    return df


def read_imu():
    if not os.path.exists(IMU_CSV):
        return pd.DataFrame(
            columns=[
                "timestamp", "ax", "ay", "az", "gx", "gy", "gz",
                "mx", "my", "mz", "imu_temp_c", "pos_x_m", "pos_y_m"
            ]
        )
    df = pd.read_csv(IMU_CSV)
    if "timestamp" in df.columns:
        df["timestamp"] = df["timestamp"].astype(float)
        df = df.sort_values("timestamp")
    return df


# ---------- Wildfire risk rule (placeholder moisture-based thresholds) ----------

def risk_from_moisture(m):
    """
    Placeholder rule:
        moisture > 40  -> Low
        20 <= m <= 40  -> Medium
        m < 20         -> High
    """
    if m is None or pd.isna(m):
        return "Unknown"
    if m < 20.0:
        return "High"
    if m <= 40.0:
        return "Medium"
    return "Low"


# ---------- Dash app setup ----------

app = Dash(__name__)
server = app.server

# Store:
# {
#   "experiments": [
#       {
#           "id": 1,
#           "start": float,
#           "stop": float,
#           "duration_sec": int,
#           "avg_temp": float or None,
#           "avg_moist": float or None,
#           "risk": str
#       }, ...
#   ],
#   "current_start": float or None
# }
app.layout = html.Div(
    style={
        "fontFamily": "Arial, sans-serif",
        "padding": "10px"
    },
    children=[
        html.H2("SSS Experiment Dashboard"),

        # Controls
        html.Div(
            style={"marginBottom": "10px"},
            children=[
                html.Button("Start Experiment", id="start-btn", n_clicks=0),
                html.Button(
                    "Stop Experiment",
                    id="stop-btn",
                    n_clicks=0,
                    style={"marginLeft": "10px"}
                ),
                html.Span(id="status-text", style={"marginLeft": "20px"})
            ]
        ),

        # Hidden state store
        dcc.Store(
            id="exp-store",
            data={"experiments": [], "current_start": None}
        ),

        # Main landscape layout: table + risk key + scatter + heatmaps
        html.Div(
            style={
                "display": "flex",
                "flexDirection": "row",
                "justifyContent": "space-between",
                "alignItems": "flex-start",
                "gap": "10px",
                "height": "600px"  # encourage landscape / one-screen layout
            },
            children=[
                # Left column: table + risk key
                html.Div(
                    style={
                        "flex": "1",
                        "minWidth": "250px"
                    },
                    children=[
                        html.H4("Experiment Results"),
                        dash_table.DataTable(
                            id="results-table",
                            columns=[
                                {"name": "Experiment", "id": "experiment"},
                                {"name": "Duration", "id": "duration"},
                                {"name": "Avg Temp (°C)", "id": "avg_temp"},
                                {"name": "Avg Moisture (%)", "id": "avg_moist"},
                                {"name": "Wildfire Risk", "id": "risk"}
                            ],
                            data=[],
                            style_table={
                                "border": "1px solid #ccc",
                                "maxHeight": "400px",
                                "overflowY": "auto"
                            },
                            style_cell={
                                "border": "1px solid #ccc",
                                "padding": "4px",
                                "fontFamily": "Arial, sans-serif",
                                "fontSize": "12px"
                            },
                            style_header={
                                "backgroundColor": "#f0f0f0",
                                "fontWeight": "bold",
                                "border": "1px solid #ccc"
                            },
                        ),
                        html.Div(
                            style={
                                "marginTop": "10px",
                                "padding": "8px",
                                "border": "1px solid #ccc",
                                "borderRadius": "4px",
                                "fontSize": "12px"
                            },
                            children=[
                                html.Strong("Wildfire Risk Key (by moisture):"),
                                html.Ul(
                                    style={"paddingLeft": "20px", "margin": "4px 0"},
                                    children=[
                                        html.Li("Low: moisture > 40%"),
                                        html.Li("Medium: 20% ≤ moisture ≤ 40%"),
                                        html.Li("High: moisture < 20%"),
                                    ]
                                )
                            ]
                        )
                    ]
                ),

                # Middle column: scatter plot (temp & moisture)
                html.Div(
                    style={
                        "flex": "1.1",
                        "minWidth": "300px"
                    },
                    children=[
                        html.H4("Experiment Points: Temperature & Moisture"),
                        dcc.Graph(
                            id="scatter-plot",
                            style={"height": "260px"}
                        ),
                    ]
                ),

                # Right column: heatmaps stacked
                html.Div(
                    style={
                        "flex": "1.4",
                        "minWidth": "350px"
                    },
                    children=[
                        html.H4("IMU-based 2D Heatmaps"),
                        dcc.Graph(
                            id="temp-heatmap",
                            style={"height": "250px", "marginBottom": "10px"}
                        ),
                        dcc.Graph(
                            id="moist-heatmap",
                            style={"height": "250px"}
                        ),
                    ]
                ),
            ]
        )
    ]
)


# ---------- Callback: handle Start/Stop, build experiments list ----------

@app.callback(
    Output("exp-store", "data"),
    Output("status-text", "children"),
    Input("start-btn", "n_clicks"),
    Input("stop-btn", "n_clicks"),
    State("exp-store", "data"),
    prevent_initial_call=False
)
def handle_start_stop(start_clicks, stop_clicks, store):
    """
    Option A behavior:
    - Each Start→Stop pair yields one experiment in order.
    - Only up to 3 experiments are stored.
    """
    if store is None:
        store = {"experiments": [], "current_start": None}

    experiments = store.get("experiments", [])
    current_start = store.get("current_start", None)

    ctx = callback_context
    if not ctx.triggered:
        status = "Idle"
        # status reflection of current state
        if current_start is not None:
            status = "Experiment running..."
        elif len(experiments) > 0:
            status = f"{len(experiments)} experiment(s) completed."
        return {"experiments": experiments, "current_start": current_start}, status

    button_id = ctx.triggered[0]["prop_id"].split(".")[0]

    # Start button
    if button_id == "start-btn":
        current_start = time.time()
        status = "Experiment started. Waiting for Stop..."
        return {"experiments": experiments, "current_start": current_start}, status

    # Stop button
    if button_id == "stop-btn":
        if current_start is None:
            # Stop pressed without start: no change
            status = "No experiment in progress to stop."
            return {"experiments": experiments, "current_start": current_start}, status

        if len(experiments) >= 3:
            status = "Already have 3 experiments stored. Additional runs ignored."
            return {"experiments": experiments, "current_start": None}, status

        stop_time = time.time()
        duration_sec = int(round(stop_time - current_start))

        # Compute averages from live.csv
        live_df = read_live()
        sel = live_df[
            (live_df["timestamp"] >= current_start) &
            (live_df["timestamp"] <= stop_time)
        ]
        if sel.empty:
            avg_temp = None
            avg_moist = None
        else:
            avg_temp = float(sel["temperature_c"].mean())
            avg_moist = float(sel["moisture_pct"].mean())

        risk = risk_from_moisture(avg_moist)

        new_exp = {
            "id": len(experiments) + 1,
            "start": current_start,
            "stop": stop_time,
            "duration_sec": duration_sec,
            "avg_temp": None if avg_temp is None else round(avg_temp, 2),
            "avg_moist": None if avg_moist is None else round(avg_moist, 2),
            "risk": risk
        }
        experiments.append(new_exp)
        status = f"Experiment {new_exp['id']} completed (duration {duration_sec} seconds)."

        return {"experiments": experiments, "current_start": None}, status

    # Fallback
    return {"experiments": experiments, "current_start": current_start}, "Idle"


# ---------- Callback: update table, scatter, and heatmaps ----------

@app.callback(
    Output("results-table", "data"),
    Output("scatter-plot", "figure"),
    Output("temp-heatmap", "figure"),
    Output("moist-heatmap", "figure"),
    Input("exp-store", "data")
)
def update_visuals(store):
    if store is None:
        store = {"experiments": [], "current_start": None}

    experiments = store.get("experiments", [])

    # ----- Results table data -----
    table_data = []
    for exp in experiments:
        duration_str = (
            f"{exp['duration_sec']} seconds" if exp.get("duration_sec") is not None else ""
        )
        table_data.append({
            "experiment": f"Experiment {exp['id']}",
            "duration": duration_str,
            "avg_temp": "" if exp.get("avg_temp") is None else exp["avg_temp"],
            "avg_moist": "" if exp.get("avg_moist") is None else exp["avg_moist"],
            "risk": exp.get("risk", "")
        })

    # ----- Scatter plot (both temperature & moisture) -----
    if experiments:
        exp_ids = [e["id"] for e in experiments]
        temps = [e["avg_temp"] for e in experiments]
        moist = [e["avg_moist"] for e in experiments]

        fig_scatter = go.Figure()
        fig_scatter.add_trace(go.Scatter(
            x=exp_ids,
            y=temps,
            mode="markers",
            name="Avg Temperature (°C)",
            marker=dict(symbol="circle", size=10)
        ))
        fig_scatter.add_trace(go.Scatter(
            x=exp_ids,
            y=moist,
            mode="markers",
            name="Avg Moisture (%)",
            marker=dict(symbol="square", size=10)
        ))
        fig_scatter.update_layout(
            xaxis=dict(
                title="Experiment",
                tickmode="array",
                tickvals=exp_ids,
                ticktext=[f"{i}" for i in exp_ids]
            ),
            yaxis=dict(title="Value"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
            margin=dict(l=40, r=10, t=30, b=40),
            height=260
        )
    else:
        fig_scatter = go.Figure()
        fig_scatter.update_layout(
            title="No experiments yet.",
            margin=dict(l=40, r=10, t=30, b=40),
            height=260
        )

     # ----- Heatmaps -----
    # Build merged sample data across all experiments to:
    # - create temperature and moisture heatmaps
    # - compute mean position per experiment for markers
    live_df = read_live()
    imu_df = read_imu()

    temp_heatmap_fig = go.Figure()
    moist_heatmap_fig = go.Figure()

    if experiments and not live_df.empty and not imu_df.empty:
        all_merged = []
        exp_positions = []  # to store mean position of each experiment

        for exp in experiments:
            start = exp["start"]
            stop = exp["stop"]

            live_sel = live_df[
                (live_df["timestamp"] >= start) &
                (live_df["timestamp"] <= stop)
            ][["timestamp", "moisture_pct", "temperature_c"]].copy()

            if live_sel.empty:
                continue

            imu_sel = imu_df[["timestamp", "pos_x_m", "pos_y_m"]].copy()
            if imu_sel.empty:
                continue

            # ensure float timestamp for merge_asof
            live_sel["timestamp"] = live_sel["timestamp"].astype(float)
            imu_sel["timestamp"] = imu_sel["timestamp"].astype(float)

            merged = pd.merge_asof(
                live_sel.sort_values("timestamp"),
                imu_sel.sort_values("timestamp"),
                on="timestamp",
                direction="nearest",
                tolerance=0.2  # seconds
            )
            merged["experiment_id"] = exp["id"]
            merged = merged.dropna(subset=["pos_x_m", "pos_y_m"])

            if merged.empty:
                continue

            all_merged.append(merged)

            # mean position for experiment marker
            exp_positions.append({
                "id": exp["id"],
                "x": merged["pos_x_m"].mean(),
                "y": merged["pos_y_m"].mean()
            })

        if all_merged:
            merged_all = pd.concat(all_merged, ignore_index=True)

            x = merged_all["pos_x_m"].values
            y = merged_all["pos_y_m"].values
            temp_vals = merged_all["temperature_c"].values
            moist_vals = merged_all["moisture_pct"].values

            # Define grid for binning
            x_min, x_max = float(np.min(x)), float(np.max(x))
            y_min, y_max = float(np.min(y)), float(np.max(y))

            # avoid degenerate grids
            if x_min == x_max:
                x_min -= 0.5
                x_max += 0.5
            if y_min == y_max:
                y_min -= 0.5
                y_max += 0.5

            nx, ny = 25, 25
            x_edges = np.linspace(x_min, x_max, nx + 1)
            y_edges = np.linspace(y_min, y_max, ny + 1)

            # Helper to compute average per bin
            def make_grid(values):
                sum_grid = np.zeros((ny, nx))
                count_grid = np.zeros((ny, nx))

                x_idx = np.clip(
                    np.digitize(x, x_edges) - 1,
                    0, nx - 1
                )
                y_idx = np.clip(
                    np.digitize(y, y_edges) - 1,
                    0, ny - 1
                )

                for xi, yi, val in zip(x_idx, y_idx, values):
                    sum_grid[yi, xi] += val
                    count_grid[yi, xi] += 1

                with np.errstate(divide="ignore", invalid="ignore"):
                    avg_grid = sum_grid / count_grid
                    avg_grid[count_grid == 0] = np.nan
                return avg_grid

            temp_grid = make_grid(temp_vals)
            moist_grid = make_grid(moist_vals)

            x_centers = 0.5 * (x_edges[:-1] + x_edges[1:])
            y_centers = 0.5 * (y_edges[:-1] + y_edges[1:])

            # Temperature heatmap
            temp_heatmap_fig = go.Figure(
                data=go.Heatmap(
                    z=temp_grid,
                    x=x_centers,
                    y=y_centers,
                    colorbar=dict(title="Temperature (°C)"),
                    hovertemplate="x=%{x:.2f} m<br>y=%{y:.2f} m<br>T=%{z:.2f} °C<extra></extra>"
                )
            )
            temp_heatmap_fig.update_layout(
                title="Temperature Heatmap (local IMU coordinates)",
                xaxis_title="pos_x_m (m)",
                yaxis_title="pos_y_m (m)",
                margin=dict(l=40, r=10, t=30, b=40),
                height=250
            )

            # Moisture heatmap
            moist_heatmap_fig = go.Figure(
                data=go.Heatmap(
                    z=moist_grid,
                    x=x_centers,
                    y=y_centers,
                    colorbar=dict(title="Moisture (%)"),
                    hovertemplate="x=%{x:.2f} m<br>y=%{y:.2f} m<br>M=%{z:.2f} %<extra></extra>"
                )
            )
            moist_heatmap_fig.update_layout(
                title="Moisture Heatmap (local IMU coordinates)",
                xaxis_title="pos_x_m (m)",
                yaxis_title="pos_y_m (m)",
                margin=dict(l=40, r=10, t=30, b=40),
                height=250
            )

            # Add markers for experiment 1/2/3 positions on BOTH heatmaps
            if exp_positions:
                marker_x = [ep["x"] for ep in exp_positions]
                marker_y = [ep["y"] for ep in exp_positions]
                marker_text = [str(ep["id"]) for ep in exp_positions]

                marker_trace = go.Scatter(
                    x=marker_x,
                    y=marker_y,
                    mode="markers+text",
                    text=marker_text,
                    textposition="top center",
                    marker=dict(symbol="x", size=10, color="black"),
                    name="Experiment positions"
                )

                temp_heatmap_fig.add_trace(marker_trace)
                moist_heatmap_fig.add_trace(marker_trace)
        else:
            temp_heatmap_fig.update_layout(
                title="Temperature Heatmap: no matched IMU/soil data",
                margin=dict(l=40, r=10, t=30, b=40),
                height=250
            )
            moist_heatmap_fig.update_layout(
                title="Moisture Heatmap: no matched IMU/soil data",
                margin=dict(l=40, r=10, t=30, b=40),
                height=250
            )
    else:
        temp_heatmap_fig.update_layout(
            title="Temperature Heatmap: waiting for experiments/data",
            margin=dict(l=40, r=10, t=30, b=40),
            height=250
        )
        moist_heatmap_fig.update_layout(
            title="Moisture Heatmap: waiting for experiments/data",
            margin=dict(l=40, r=10, t=30, b=40),
            height=250
        )

    return table_data, fig_scatter, temp_heatmap_fig, moist_heatmap_fig 


if __name__ == "__main__":
    if not os.path.exists(LIVE_CSV):
        print(f"[sssdash] Warning: {LIVE_CSV} not found. Start makesencsv.py to generate data.")
    if not os.path.exists(IMU_CSV):
        print(f"[sssdash] Warning: {IMU_CSV} not found. Start makeimucsv.py to generate data.")
    app.run(debug=True, port=8050)
