import pandas as pd
import matplotlib.pyplot as plt

# =========================
# 1. Data
# =========================

data = {
    "Day": [0, 3, 8, 9, 10, 11, 12],

    "1": [8063, 5890, 6098, 5781, 5678, 5930, 5102],
    "2": [8184, 5850, 5962, 5882, 5593, 5642, 5423],
    "3": [8090, 5830, 5935, 5657, 5520, 5576, 5520],

    "X": [8142, 5567, 5725, 5541, 5523, 5255, 5080],
    "Y": [8063, 5115, 5651, 5505, 5720, 5620, 5116],
    "Z": [7969, 5314, 5425, 5243, 5077, 5329, 4996],

    "A": [8050, 5635, 5536, 5535, 5203, 5412, 5141],
    "B": [7950, 5492, 5620, 5790, 5667, 5845, 5026],
    "C": [8286, 5990, 5673, 5780, 5589, 5681, 5173],

    "alpha": [8023, 5619, 5419, 5525, 5701, 5163, 4894],
    "beta": [8171, 5934, 5725, 5451, 5472, 5538, 5382],
    "gamma": [7935, 5881, 5525, 5482, 5368, 5403, 5286],
}

df = pd.DataFrame(data)

# =========================
# 2. Groups
# =========================

groups = {
    "Silent": ["1", "2", "3"],
    "200 Hz": ["X", "Y", "Z"],
    "10,000 Hz": ["A", "B", "C"],
    "20,000 Hz": ["alpha", "beta", "gamma"]
}

colors = {
    "Silent": "teal",
    "200 Hz": "red",
    "10,000 Hz": "orange",
    "20,000 Hz": "black"
}

offsets = {
    "Silent": -0.18,
    "200 Hz": -0.06,
    "10,000 Hz": 0.06,
    "20,000 Hz": 0.18
}

# =========================
# 3. Average + Error Bar
# Error bar = Standard Error
# =========================

for group_name, columns in groups.items():
    df[group_name + " Avg"] = df[columns].mean(axis=1)
    df[group_name + " Error"] = df[columns].std(axis=1) / (len(columns) ** 0.5)

print(df[[
    "Day",
    "Silent Avg", "Silent Error",
    "200 Hz Avg", "200 Hz Error",
    "10,000 Hz Avg", "10,000 Hz Error",
    "20,000 Hz Avg", "20,000 Hz Error"
]])

# =========================
# 4. Plot
# =========================

plt.figure(figsize=(12, 7))

for group_name in groups.keys():
    x_values = df["Day"] + offsets[group_name]

    plt.errorbar(
        x_values,
        df[group_name + " Avg"],
        yerr=df[group_name + " Error"],
        marker="o",
        markersize=5,
        capsize=3,
        linewidth=2,
        elinewidth=1,
        color=colors[group_name],
        label=group_name
    )

# =========================
# 5. Style Like the Hand-Drawn Graph
# =========================

plt.title("Various Sound Frequencies on Algae Turbidity", fontsize=15)
plt.xlabel("Day of Experiment")
plt.ylabel("Lux")

plt.xticks(
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
    ["Initial", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"]
)

# Lower lux means more algae, so reverse y-axis
plt.gca().invert_yaxis()

plt.ylim(8500, 4500)

plt.grid(True, alpha=0.25)

# Vertical dashed lines
for x in [1, 2, 3, 4, 7, 8]:
    plt.axvline(
        x=x,
        linestyle="--",
        color="gray",
        alpha=0.5
    )

# No measurements labels
plt.text(
    2.4,
    7000,
    "NO MEASUREMENTS TAKEN",
    rotation=90,
    fontsize=11,
    ha="center",
    va="center"
)

plt.text(
    5.8,
    7000,
    "NO MEASUREMENTS TAKEN",
    rotation=90,
    fontsize=11,
    ha="center",
    va="center"
)

# Note on the right bottom
plt.text(
    12.45,
    8050,
    "* No treatment or\nlight was given to\nthe algae on days\n5 and 7",
    fontsize=10,
    va="center"
)

# Legend outside the graph
plt.legend(
    loc="center left",
    bbox_to_anchor=(1.02, 0.5),
    frameon=False
)

plt.tight_layout(rect=[0, 0, 0.82, 1])
plt.show()