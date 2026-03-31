import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from scipy.spatial.distance import braycurtis
from sklearn.manifold import MDS

# Set seed so results are reproducible every run
np.random.seed(42)

# Plant taxa used in the analysis -- chosen based on known caribou and moose dietary preferences
plants = [
    "Cladonia_spp",  # lichen -- main caribou winter food source
    "Salix_spp",  # willow -- key moose browse
    "Betula_spp",  # birch -- moose browse
    "Carex_spp",  # sedge -- eaten by both species
    "Poaceae",  # grasses -- eaten by both species
    "Aquatic_plants",  # aquatic vegetation -- mainly moose in summer
    "Forbs",  # forbs -- eaten by both species
    "Mosses",  # mosses -- minor component for both
]

# Diet profiles as weights per species and season
# Higher weight = higher probability of reads coming from that plant
# Based on known ecology: caribou rely heavily on lichen in winter,
# moose are consistent browsers of woody shrubs year round
caribou_winter = [70, 20, 5, 10, 15, 0, 5, 5]
caribou_summer = [30, 40, 20, 25, 30, 5, 15, 10]
moose_winter = [10, 50, 30, 20, 25, 5, 10, 5]
moose_summer = [5, 40, 35, 25, 30, 10, 20, 5]


def generate_samples(profile, n_sample, species, season):
    """
    Simulate fecal metabarcoding samples for a given species and season.
    Weights are converted to probabilities and used to distribute
    sequencing reads across plant taxa using a multinomial distribution.
    """
    # Convert weights to probabilities that sum to 1
    probs = np.array(profile) / sum(profile)

    rows = []
    for i in range(n_sample):
        # Distribute 100 reads across plant taxa based on diet probabilities
        # Multinomial mimics real sequencing by adding biological variation
        counts = np.random.multinomial(100, probs)

        rows.append(
            {
                "sample_id": f"{species}_{season}_{i + 1}",
                "species": species,
                "season": season,
                **dict(zip(plants, counts)),
            }
        )
    return rows


# Generate 10 samples per species/season combination -- 40 samples total
all_samples = []
all_samples.extend(generate_samples(caribou_winter, 10, "Caribou", "Winter"))
all_samples.extend(generate_samples(caribou_summer, 10, "Caribou", "Summer"))
all_samples.extend(generate_samples(moose_winter, 10, "Moose", "Winter"))
all_samples.extend(generate_samples(moose_summer, 10, "Moose", "Summer"))

# Build the OTU table and set sample ID as the row index
df = pd.DataFrame(all_samples)
df = df.set_index("sample_id")
print(df.shape)
print(df.head())

# Separate metadata from plant count columns
metadata = df[["species", "season"]]
counts = df.drop(columns=["species", "season"])

# Normalize raw counts to relative proportions
# Each row now sums to 1.0 -- makes samples comparable regardless of sequencing depth
proportions = counts.div(counts.sum(axis=1), axis=0)
print(proportions.head())
print(proportions.sum(axis=1).head())  # sanity check -- all should be 1.0

# Add metadata back for grouping in downstream analysis
proportions["species"] = metadata["species"]
proportions["season"] = metadata["season"]


# ── Figure 1: Mean Diet Composition by Species ─────────────────────────────

# Average diet proportions across all seasons per species
mean_diet = proportions.groupby("species")[plants].mean()

# Transpose so plants are on x-axis and species are the bars
ax = mean_diet.T.plot(
    kind="bar", figsize=(12, 6), color=["#4C72B0", "#DD8452"], width=0.7
)

plt.title("Mean Diet Composition: Caribou vs Moose", fontsize=14)
plt.xlabel("Plant Taxa", fontsize=12)
plt.ylabel("Mean Relative Proportion", fontsize=12)
plt.xticks(rotation=45, ha="right")
plt.legend(title="Species")
plt.tight_layout()
plt.savefig("figures/diet_composition.png", dpi=150)
plt.show()


# ── Figure 2: Seasonal Diet Comparison ────────────────────────────────────

# Group by both species and season to get 4 groups
mean_seasonal = proportions.groupby(["species", "season"])[plants].mean()
print(mean_seasonal)

# Side by side subplots -- one panel per species, sharey for direct comparison
fig, axes = plt.subplots(1, 2, figsize=(16, 6), sharey=True)

species_list = ["Caribou", "Moose"]
colors = ["#4C72B0", "#DD8452"]

for i, species in enumerate(species_list):
    # Pull winter and summer rows for this species
    species_data = mean_seasonal.loc[species]

    species_data.T.plot(kind="bar", ax=axes[i], color=colors, width=0.7)

    axes[i].set_title(f"{species} Diet by Season", fontsize=13)
    axes[i].set_xlabel("Plant Taxa", fontsize=11)
    axes[i].set_ylabel("Mean Relative Proportion", fontsize=11)
    axes[i].tick_params(axis="x", rotation=45)
    axes[i].legend(title="Season")

plt.suptitle("Seasonal Diet Composition: Caribou vs Moose", fontsize=15)
plt.tight_layout()
plt.savefig("figures/seasonal_comparison.png", dpi=150)
plt.show()


# ── Pianka's Dietary Overlap Index ────────────────────────────────────────


def pianka_overlap(diet1, diet2):
    """
    Calculate Pianka's overlap index between two diet vectors.
    Returns a value between 0 (no overlap) and 1 (identical diets).
    Numerator: sum of element-wise products across all plant taxa.
    Denominator: geometric mean of each diet's squared proportions -- scales result to [0,1].
    """
    numerator = np.sum(diet1 * diet2)
    denominator = np.sqrt(np.sum(diet1**2) * np.sum(diet2**2))
    return numerator / denominator if denominator > 0 else 0


# Convert grouped table to dict for easy lookup by (species, season) key
groups = mean_seasonal.to_dict(orient="index")

# Define pairs to compare -- between species and within species across seasons
comparisons = [
    ("Caribou", "Summer", "Moose", "Summer"),
    ("Caribou", "Winter", "Moose", "Winter"),
    ("Caribou", "Summer", "Caribou", "Winter"),
    ("Moose", "Summer", "Moose", "Winter"),
]

print("Diet Overlap (Pianka's Index):")
print("-" * 40)

for sp1, se1, sp2, se2 in comparisons:
    diet1 = np.array(list(groups[(sp1, se1)].values()))
    diet2 = np.array(list(groups[(sp2, se2)].values()))
    overlap = pianka_overlap(diet1, diet2)
    print(f"{sp1} {se1} vs {sp2} {se2}: {overlap:.3f}")


# ── Figure 3: Heatmap of All Samples ──────────────────────────────────────

# Sort so caribou and moose samples are visually grouped together
proportions_sorted = proportions.sort_values(["species", "season"])
heatmap_data = proportions_sorted.drop(columns=["species", "season"])

# Color scale: yellow = low proportion, red = high proportion
plt.figure(figsize=(12, 10))
sns.heatmap(
    heatmap_data,
    cmap="YlOrRd",
    linewidths=0.3,
    linecolor="grey",
    cbar_kws={"label": "Relative Proportion"},
    yticklabels=True,
)

plt.title("Diet Composition Heatmap: All Samples", fontsize=14)
plt.xlabel("Plant Taxa", fontsize=12)
plt.ylabel("Sample ID", fontsize=12)
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig("figures/heatmap.png", dpi=150)
plt.show()


# ── Figure 4: PCoA Ordination ──────────────────────────────────────────────

# Drop metadata -- distance matrix only needs plant proportions
pcoa_data = proportions.drop(columns=["species", "season"])

# Build a 40x40 Bray-Curtis distance matrix
# Bray-Curtis is standard for dietary and microbiome compositional data
# Values range from 0 (identical) to 1 (completely different)
n = len(pcoa_data)
bc_matrix = np.zeros((n, n))

for i in range(n):
    for j in range(n):
        bc_matrix[i, j] = braycurtis(pcoa_data.iloc[i], pcoa_data.iloc[j])

print(bc_matrix.shape)
print(bc_matrix[:3, :3])  # diagonal should be 0 -- sample vs itself

# Run PCoA by passing the precomputed distance matrix into MDS
# Compresses 8-dimensional diet space down to 2D for visualization
mds = MDS(n_components=2, dissimilarity="precomputed", random_state=42)
coords = mds.fit_transform(bc_matrix)

# Plot -- color = species, marker shape = season
fig, ax = plt.subplots(figsize=(10, 7))

plot_groups = {
    "Caribou Summer": ("#4C72B0", "o"),
    "Caribou Winter": ("#4C72B0", "^"),
    "Moose Summer": ("#DD8452", "o"),
    "Moose Winter": ("#DD8452", "^"),
}

for idx, row in proportions.iterrows():
    sp = row["species"]
    se = row["season"]
    label = f"{sp} {se}"
    color, marker = plot_groups[label]
    sample_idx = list(proportions.index).index(idx)

    ax.scatter(
        coords[sample_idx, 0],
        coords[sample_idx, 1],
        c=color,
        marker=marker,
        s=80,
        label=label,
    )

# Remove duplicate legend entries from the loop
handles, labels = ax.get_legend_handles_labels()
by_label = dict(zip(labels, handles))
ax.legend(by_label.values(), by_label.keys(), title="Group")

ax.set_xlabel("PCoA Axis 1", fontsize=12)
ax.set_ylabel("PCoA Axis 2", fontsize=12)
ax.set_title("PCoA of Dietary Composition (Bray-Curtis)", fontsize=14)
ax.axhline(0, color="grey", linewidth=0.5, linestyle="--")
ax.axvline(0, color="grey", linewidth=0.5, linestyle="--")
plt.tight_layout()
plt.savefig("figures/pcoa.png", dpi=150)
plt.show()
