import pandas as pd
import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt
import os 
import glob
from shapely.geometry import Point, MultiPolygon
import sys
from datetime import datetime
from scipy.optimize import curve_fit
import warnings
from IPython.display import display
from plotnine import *

display_graphs = True
# Linear plateau model
def linear_plateau(x, b0, b1, x_break):
    y = np.where(x < x_break, b0 + b1 * x, b0 + b1 * x_break)
    return y

 
def calc_r2_rmse(y_true, y_pred):
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else np.nan
    rmse = np.sqrt(np.mean((y_true - y_pred) ** 2))
    return r2, rmse

def compute_aic(y_true, y_pred, k):
    n = len(y_true)
    rss = np.sum((y_true - y_pred) ** 2)
    if rss <= 0 or n <= k:
        return np.nan
    return n * np.log(rss / n) + 2 * k

def fit_linear_plateau(group_df, y_var, x_var="rtotn_kgha", min_points=5):
    # Unpack group info
    field = group_df["FieldID"].iloc[0]

    data_df = group_df[[x_var, y_var]].dropna().copy()
    if len(group_df) < min_points:
        return {
            "b0": np.nan,
            "b1": np.nan,
            "x_break": np.nan,
            "y_plateau": np.nan,
            "r2": np.nan,
            "rmse": np.nan,
        }

    x = pd.to_numeric(data_df[x_var]).values
    y = pd.to_numeric(data_df[y_var]).values

    # Initial guess:
    # slope/intercept from linear fit, x_break at 80th percentile
    coeffs = np.polyfit(x, y, 1)
    b1_init, b0_init = coeffs
    x_break_init = np.percentile(x, 80)

    p0 = [b0_init, b1_init, x_break_init]

    # Ensure initial guess are within data range
    p0[0] = np.clip(p0[0], np.min(y), np.max(y))
    p0[1] = np.clip(p0[1], 0, np.inf)

    # Bounds: int any, slope >= 0, break any
    # I don't want to limit x break, if it's outside range, we'll handle later
    lower_bounds = [-np.inf, -np.inf, -np.inf]
    upper_bounds = [np.inf, np.inf, np.inf]

    try:
        popt, _ = curve_fit(
            linear_plateau,
            x,
            y,
            p0=p0,
            bounds=(lower_bounds, upper_bounds),
            maxfev=10000,
        )
        b0, b1, x_break = popt
        y_plateau = b0 + b1 * x_break

        # Ensure x_break inside range
        if x_break < np.min(x) or x_break > np.max(x):
            # raise RuntimeError("x_break outside range")
            warnings.warn(f"x_break ({x_break:.2f}) outside observed range.")
        # add a graph for linear plateau
        if display_graphs:
            # Generate a smooth x grid for plotting
            x_grid = np.linspace(data_df[x_var].min(), data_df[x_var].max(), 20)

            # Linear from initial guess
            b0_init, b1_init, x_break_init = p0
            y_lin_init = linear_plateau(x_grid, b0_init, b1_init, x_break_init)
            fit_init_df = pd.DataFrame({x_var: x_grid, y_var: y_lin_init})
            fit_init_df["source"] = "Initial linear"

            # Linear plateau from final fit (only if valid)
            if not np.isnan(b0):
                y_plateau_fit = linear_plateau(x_grid, b0, b1, x_break)
                fit_final_df = pd.DataFrame({x_var: x_grid, y_var: y_plateau_fit})
                fit_final_df["source"] = "Final plateau"
            else:
                fit_final_df = pd.DataFrame(columns=[x_var, y_var, "source"])

            # Observed data
            data_df["source"] = "Observed"

            # Combine all for plotting
            plot_df = pd.concat([data_df, fit_init_df, fit_final_df], ignore_index=True)

            g = (
                ggplot(
                    plot_df,
                    aes(x=x_var, y=y_var, color="source", linetype="source"),
                )
                + geom_point(data=data_df)
                + geom_line(data=fit_init_df)
                + geom_line(data=fit_final_df)
                + ggtitle(f"{y_var} Field: {field}")
                # + theme_ff()
            )

            display(g)
            file_path = f"/workspace/workflow/_9GTDpreparation/figure.png"
            g.save(file_path, dpi=300)

        # Predictions
        y_pred = linear_plateau(x, *popt)
        r2, rmse = calc_r2_rmse(y, y_pred)

        residuals = y - y_pred
        ss_res = np.sum(residuals**2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        r2 = 1 - ss_res / ss_tot if ss_tot > 0 else np.nan
        rmse = np.sqrt(np.mean(residuals**2))

        # AIC (k = 3 parameters: b0, b1, x_break)
        aic = compute_aic(y, y_pred, k=3)

        return {
            "b0": b0,
            "b1": b1,
            "x_break": x_break,
            "y_plateau": y_plateau,
            "r2": r2,
            "rmse": rmse,
            "aic": aic,
        }

    except RuntimeError:
        return {
            "b0": np.nan,
            "b1": np.nan,
            "x_break": np.nan,
            "y_plateau": np.nan,
            "r2": np.nan,
            "rmse": np.nan,
            "aic": np.nan,
        }

