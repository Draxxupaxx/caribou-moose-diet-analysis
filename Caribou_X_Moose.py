import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

np.random.seed(42)  # for reproducibility

plants = [
    "Cladonia_spp",  # lichen -- caribou staple
    "Salix_spp",  # willow -- moose staple
    "Betula_spp",  # birch -- moose
    "Carex_spp",  # sedge -- both
    "Poaceae",  # grasses -- both
    "Aquatic_plants",  # aquatic -- moose
    "Forbs",  # forbs -- both
    "Mosses",  # mosses -- low in both
]

caribou_winter = [70, 20, 5, 10, 15, 0, 5, 5]  # mostly lichens
caribou_summer = [30, 40, 20, 25, 30, 5, 15, 10]  # more variety in summer

moose_winter = [10, 50, 30, 20, 25, 5, 10, 5]  # mostly willows and birch
moose_summer = [5, 40, 35, 25, 30, 10, 20, 5]  # more aquatic plants in summer


def generate_samples(profile, n_sample, species, season):
    # generate random samples based on the profile proportions
    probs = np.array(profile) / sum(profile)

    rows = []
    for i in range(n_sample):
        counts = np.random.multinomial(100, probs)  # simulate 100 plant "units"

        rows.append(
            {
                "sample_id": f"{species}_{season}_{i + 1}",
                "species": species,
                "season": season,
                **dict(zip(plants, counts)),  # add plant counts as columns
            }
        )
    return rows


all_samples = []
all_samples.extend(generate_samples(caribou_winter, 10, "Caribou", "Winter"))
all_samples.extend(generate_samples(caribou_summer, 10, "Caribou", "Summer"))
all_samples.extend(generate_samples(moose_winter, 10, "Moose", "Winter"))
all_samples.extend(generate_samples(moose_summer, 10, "Moose", "Summer"))

df = pd.DataFrame(all_samples)
df = df.set_index("sample_id")  # set sample_id as index for easier viewing
print(df.shape)
print(df.head())

metadata = df[["species", "season"]]
counts = df.drop(columns=["species", "season"])

proportions = counts.div(counts.sum(axis=1), axis=0)
print(proportions.head())
print(proportions.sum(axis=1).head())  # should all be 1.0

proportions["species"] = metadata["species"]
proportions["season"] = metadata["season"]

# Calculate mean proportion per species per plant
mean_diet = proportions.groupby("species")[plants].mean()

# Plot
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

mean_seasonal = proportions.groupby(["species", "season"])[plants].mean()
print(mean_seasonal)

fig, axes = plt.subplots(1, 2, figsize=(16, 6), sharey=True)

species_list = ["Caribou", "Moose"]
colors = ["#4C72B0", "#DD8452"]

for i, species in enumerate(species_list):
    # Pull out just this species from the grouped table
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


def pianka_overlap(diet1, diet2):
    # Calculate Pianka's overlap index
    numerator = np.sum(diet1 * diet2)
    denominator = np.sqrt(np.sum(diet1**2) * np.sum(diet2**2))
    return numerator / denominator if denominator > 0 else 0


groups = mean_seasonal.to_dict(orient="index")  # convert to dict for easier access

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

proportions_sorted = proportions.sort_values(["species", "season"])

heatmap_data = proportions_sorted.drop(columns=["species", "season"])

row_colors = proportions_sorted["species"].map(
    {"Caribou": "#4C72B0", "Moose": "#DD8452"}
)

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
