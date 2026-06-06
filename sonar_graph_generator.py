import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from scipy import stats

# --- CONFIGURATION ---
INPUT_FILE = "sonar_journal_data.json"
FIG1_FILENAME = "figure_1_longitudinal_divergence.png"
FIG2_FILENAME = "figure_2_distribution_boxplot.png"

# Style settings for academic publication
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_context("paper", font_scale=1.5)

def load_data():
    data = []
    try:
        with open(INPUT_FILE, "r") as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    # We only care about the metrics for the graph
                    data.append({
                        "Mode": entry.get("mode", "UNKNOWN"),
                        "Cycle": entry.get("cycle"),
                        "Divergence": entry.get("ontological_divergence")
                    })
                except:
                    continue
    except FileNotFoundError:
        print(f"ERROR: Could not find {INPUT_FILE}. Make sure the batch run is finished.")
        return pd.DataFrame()

    df = pd.DataFrame(data)
    
    # Filter out Cycle 0 or weird data points if any
    df = df[df["Cycle"] > 0]
    return df

def generate_figure_1(df):
    """
    Line Graph: Shows the divergence over time (Cycles).
    Red Line = Control (Ablated)
    Blue Line = SONAR (Full)
    Shaded Region = 95% Confidence Interval
    """
    plt.figure(figsize=(10, 6))
    
    # Create the Line Plot with Confidence Intervals
    sns.lineplot(
        data=df, 
        x="Cycle", 
        y="Divergence", 
        hue="Mode", 
        style="Mode",
        markers=True, 
        dashes=False,
        palette={"FULL": "#2ecc71", "ABLATED": "#e74c3c"}, # Green for Health, Red for Collapse
        linewidth=2.5
    )

    # Add the "Stasis Threshold" line
    plt.axhline(y=0.10, color='gray', linestyle='--', alpha=0.7, label="Stasis Threshold (τ=0.10)")

    plt.title("Impact of Homeostatic Entropy Injection on Semantic Plasticity", fontsize=16, pad=20)
    plt.xlabel("Recursive Cycle Count", fontsize=12)
    plt.ylabel("Ontological Divergence ($D_o$)", fontsize=12)
    plt.legend(title="Protocol Mode", loc='upper right')
    plt.ylim(0, 0.25) # Scale to focus on the critical area
    
    plt.tight_layout()
    plt.savefig(FIG1_FILENAME, dpi=300)
    print(f">>> Generated {FIG1_FILENAME}")

def generate_figure_2(df):
    """
    Box Plot: Aggregates the 'Semantic Health' of all runs.
    """
    plt.figure(figsize=(8, 6))
    
    # We aggregate by taking the MEAN divergence per run, 
    # OR we can just plot all data points to show distribution.
    # Let's plot the distribution of divergence scores for Cycles > 2 (where collapse happens)
    
    late_stage_df = df[df["Cycle"] >= 2]
    
    sns.boxplot(
        data=late_stage_df,
        x="Mode",
        y="Divergence",
        palette={"FULL": "#2ecc71", "ABLATED": "#e74c3c"},
        width=0.5
    )
    
    plt.title("Distribution of Divergence (Cycles 2-6)", fontsize=16)
    plt.ylabel("Ontological Divergence ($D_o$)", fontsize=12)
    plt.xlabel("Experimental Group", fontsize=12)
    
    # Add statistical annotation (Mean)
    means = late_stage_df.groupby("Mode")["Divergence"].mean()
    for i, mode in enumerate(["ABLATED", "FULL"]):
        if mode in means:
            plt.text(i, means[mode], f"μ={means[mode]:.3f}", 
                     horizontalalignment='center', color='black', weight='bold')

    plt.tight_layout()
    plt.savefig(FIG2_FILENAME, dpi=300)
    print(f">>> Generated {FIG2_FILENAME}")

def print_stats(df):
    print("\n" + "="*40)
    print("FINAL SCIENTIFIC STATISTICS")
    print("="*40)
    
    # Group by Mode
    stats = df.groupby("Mode")["Divergence"].describe()
    print(stats)
    
    # Calculate the Delta
    try:
        mean_full = stats.loc["FULL", "mean"]
        mean_abl = stats.loc["ABLATED", "mean"]
        delta = ((mean_full - mean_abl) / mean_abl) * 100
        print(f"\n>>> PERFORMANCE DELTA: SONAR provides a +{delta:.1f}% increase in semantic novelty.")
    except:
        pass

if __name__ == "__main__":
    print("Reading data from logs...")
    df = load_data()
    
    if not df.empty:
        print(f"Data Loaded: {len(df)} data points found.")
        generate_figure_1(df)
        generate_figure_2(df)
        print_stats(df)
    else:
        print("No data found. Is the batch run finished?")
