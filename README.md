# Caribou x Moose Dietary Partitioning Analysis

A Python-based analysis exploring dietary partitioning between caribou (*Rangifer tarandus*) and moose (*Alces alces*) using simulated metabarcoding data. This project mimics the type of data generated from fecal DNA metabarcoding studies and applies ecological analysis and visualization techniques to quantify dietary overlap and niche partitioning.

---

## Background

Dietary partitioning occurs when two species sharing the same habitat reduce competition by consuming different food resources. Caribou and moose co-occur across boreal and subarctic landscapes in Canada, making them an ideal system to study niche differentiation. This project simulates OTU (Operational Taxonomic Unit) tables -- the standard output of plant metabarcoding pipelines -- and analyzes diet composition across species and seasons.

---

## Project Structure

caribou-moose-diet-analysis/
├── data/
│   └── mock_otu_table.csv        # Simulated metabarcoding OTU table
├── figures/
│   └── diet_composition.png      # Mean diet composition bar chart
├── Caribou_X_Moose.py            # Main analysis script
└── README.md

---

## Methods

### Mock Data Generation
- 40 fecal samples simulated across two species (Caribou, Moose) and two seasons (Winter, Summer)
- 8 plant taxa included based on known dietary preferences from the literature
- Read counts generated using numpy.random.multinomial with biologically informed weight profiles per species/season combination
- 1000 reads simulated per sample to mimic real sequencing depth

### Plant Taxa

Taxa | Ecological Role
Cladonia spp. | Lichen -- caribou winter staple
Salix spp. | Willow -- moose browse
Betula spp. | Birch -- moose browse
Carex spp. | Sedge -- shared resource
Poaceae | Grasses -- shared resource
Aquatic plants | Moose summer resource
Forbs | Shared resource
Mosses | Minor resource

### Normalization
Raw read counts were normalized to relative proportions per sample (row sums to 1.0) to account for variation in sequencing depth across samples.

---

## Results

### Diet Composition
Mean relative proportions per species across all seasons reveal clear dietary partitioning:
- Caribou show strong reliance on Cladonia spp. (lichens), consistent with known lichen-dominated winter diets
- Moose diet is dominated by Salix spp. (willow) and Betula spp. (birch), reflecting their browsing ecology
- Carex spp. and Poaceae show similar proportions between species, representing shared dietary resources

---

## Dependencies

numpy
pandas
matplotlib
seaborn
scipy
scikit-learn

Install with:
pip install numpy pandas matplotlib seaborn scipy scikit-learn

---

## In Progress

- Seasonal comparison plots (winter vs summer per species)
- Pianka's dietary overlap index
- Heatmap of full proportions table
- PCoA ordination

---

## Author
Hadi | M.Sc. Bioinformatics, University of Guelph