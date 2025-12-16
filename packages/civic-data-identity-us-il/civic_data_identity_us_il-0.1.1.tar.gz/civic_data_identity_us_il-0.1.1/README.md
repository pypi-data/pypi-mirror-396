# civic-data-identity-us-il

This repository hosts **raw and processed Illinois datasets** used for validating
entity identity, canonicalization, and adapter behavior in the
[Civic Interconnect](https://github.com/civic-interconnect/civic-interconnect)
project.

The primary dataset is the **City of Chicago Contracts Dataset**, which provides
182,000+ procurement records used to test:

- **SNFEI identity stability** across messy vendor names  
- **EFS v1 name normalization**  
- **Adapter correctness** for procurement verticals  
- **Cross-record entity consolidation** (e.g., same vendor appearing many times)  
- **Address normalization** (Chicago-specific conventions)  
- **Exchange construction** (buyer → seller → contract mapping)  

This repository contains both the full raw dataset and curated subsets
designed as identity test fixtures.

---

## Repository

### `data/raw/`
Unmodified raw datasets retrieved directly from official public sources.
Contains large files (up to ~50 MB).  
These files are **not** stored in the main Civic Interconnect repo to avoid
repository bloat.

### `data/identity/`
Curated, size-limited datasets (~5k–20k rows) used for:

- testing SNFEI convergence  
- evaluating string normalization  
- training adapters on realistic noise patterns  

These subsets are suitable for inclusion as examples in the main CEP spec repo.

### `docs/provenance/`
Contains PROV-YAML metadata files describing dataset lineage, publishers, and
retrieval activities. These files follow **W3C PROV-DM** conventions.

### `scripts/`
Utility scripts for extracting and shaping subsets from raw data. The provided
Python tool generates deterministic, identity-rich samples.

---

## Data Source

### City of Chicago – Contracts Dataset

- URL: https://data.cityofchicago.org/Administration-Finance/Contracts/rsxa-ify5  
- Publisher: City of Chicago  
- License: Public Domain  
- Fields include procurement descriptions, award amounts, departments, vendor
  names, addresses, and contract timeline fields.
- Used to test:
  - identity resolution  
  - canonicalization  
  - adapters for procurement verticals  

Full provenance is provided in  
[`docs/provenance/chicago_contracts.prov.yaml`](docs/provenance/chicago_contracts.prov.yaml).

---

## Citation

If you use this repository, please cite **both**:

1. This repository (see `CITATION.cff`)  
2. The original City of Chicago dataset (automatically included in references)

---

## Relationship to `civic-interconnect`

This repository serves as a data companion to the main specification and
implementation in:

https://github.com/civic-interconnect/civic-interconnect

Only smaller derived files (e.g., 5k–20k row identity samples) are copied into
the main repository under:

```
examples/identity/us_il_chicago/
```

The separation keeps CEP maintainable and free of large artifacts
while preserving full reproducibility.

---

## License

Raw public datasets retain their original license (Public Domain for Chicago
Open Data).  
All derived outputs, scripts, and documentation in this repository are licensed
under the **MIT License** unless otherwise noted.

