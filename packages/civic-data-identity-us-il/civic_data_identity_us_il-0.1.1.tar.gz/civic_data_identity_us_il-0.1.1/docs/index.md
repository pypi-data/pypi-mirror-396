# Illinois Identity Dataset (Chicago Contracts)

This repository provides a curated, publication-ready subset of the Chicago
Contracts dataset, formatted for use in **Civic Interconnect** identity
experiments.  
Its primary purpose is to support evaluation of the **SNFEI** entity-identity
algorithm across heterogeneous civic data sources.

The data and metadata in this package allow Civic Interconnect users to:

- Reproduce a fixed snapshot of a large public dataset.
- Evaluate the stability of **legal name normalization** rules.
- Measure false-split and false-merge rates for entity identity clustering.
- Test adapter implementations against real, messy, high-value data.
- Integrate provenance and citation into record envelopes (CEP and CEE).

---

## What This Package Contains

```
data/
  raw/
    chicago_contracts_2025-12-11.csv    # full snapshot from Chicago Open Data

data-out/
  chicago_contracts_vendors_sample_20k.csv
  index.json                             # machine-readable dataset registry
  manifest.json                          # provenance and generation metadata
```

The `data-out/` directory contains **versioned, stable artifacts** intended for:

- SNFEI testing
- adapter development
- entity-normalization experiments
- cross-domain identity resolution research
- training examples for documentation

The **raw file** under `data/raw/` is preserved as-is to support:

- reproducibility
- hash checking
- independent recomputation of derived samples

---

## Why Chicago Contracts?

Chicago's procurement dataset contains:

- hundreds of thousands of records
- many repeated vendors
- variations in capitalization, punctuation, abbreviations, and corporate suffixes
- misspellings and data-entry inconsistencies
- rich attributes (department, amounts, contract type, dates, vendor identifiers)

This makes it an ideal **stress-test corpus** for:

- organization-name canonicalization
- SNFEI projection stability
- cross-year cluster consistency
- partial or malformed vendor identifiers

---

## How the 20k Identity Sample Was Generated

The sample in `data-out/chicago_contracts_vendors_sample_20k.csv` was produced using:

```
uv run python src/civic_data_identity_us_il/make_chicago_identity_sample.py --overwrite
```

The script:

1. Loads the raw CSV snapshot.
2. Selects the vendor-name column and related fields.
3. Deduplicates, cleans, and slices a reproducible subset of 20,000 rows.
4. Writes both:
   - the derived sample
   - a PROV-style manifest documenting inputs, outputs, timestamp, and generator

Both `index.json` and `manifest.json` are generated automatically.

All transformations are deterministic.

---

## Provenance & Reproducibility

This dataset provides **two layers of provenance**, aligned with CEP's CEE model:

### 1. Manifest Provenance (`data-out/manifest.json`)

Describes:

- exact raw input file(s)
- checksum-stable paths
- software and script used
- generation timestamp
- license and citation of the upstream data source

### 2. PROV-YAML (`provenance/chicago_contracts.prov.yaml`)

Describes:

- Entity → Activity → Agent
- how the sample file was produced
- claims suitable for embedding in CEP record envelopes

---

## Citation

If you use this dataset in research, testing, documentation, or software:

```
City of Chicago. "Contracts Dataset." Accessed via
https://data.cityofchicago.org/Administration-Finance/Contracts/rsxa-ify5.

Civic Interconnect. "Illinois Identity Dataset (Chicago Contracts)." v0.1.0.
https://github.com/civic-interconnect/civic-data-identity-us-il.
```

A machine-readable citation is also embedded in:

- `CITATION.cff`
- `data-out/index.json`

---

## Status and Versioning

This repository follows:

- **Semantic Versioning** for published dataset package versions
- **Keep a Changelog** conventions
- **setuptools_scm** for automated tagging

---

## Relationship to Civic Interconnect

This dataset is _not_ part of CEP itself.  
It is a **companion dataset** supporting:

- SNFEI design validation
- Adapter testing
- Text normalization tuning
- Reference examples for CEP documentation
- Realistic cross-domain identity experiments

---

## Contributing

Contributions welcome, including:

- additional identity benchmarks
- domain-specific normalization tests
- enhancements to the sampling script
- improved provenance annotations

Please open issues or PRs on GitHub.

---

## License: Upstream Data

The raw Chicago Contracts dataset is released by the City of Chicago under
the **Chicago Open Data Portal Terms of Use**, which functionally place the
data in the **public domain**.

Source:
https://data.cityofchicago.org/Administration-Finance/Contracts/rsxa-ify5

---

## License: This Repository

All code, scripts, derived datasets, and documentation in this repository
(`civic-data-identity-us-il`) are released under the **MIT License**.

This allows:

- reuse in academic, civic-technology, and commercial settings
- embedding into the broader **Civic Interconnect** ecosystem
- distribution through PyPI or other registries

The MIT license used here is intentionally compatible with:

- **Apache-2.0** (the license for Civic Interconnect core repositories), and
- other permissive licenses commonly used for data-oriented packages.

Nothing in this repository overrides the upstream public-domain data rights.
Generated artifacts combine MIT-licensed code with public data and are
therefore MIT-licensed.
