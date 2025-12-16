# Changelog

All notable changes to this project will be documented in this file.

The format follows **[Keep a Changelog](https://keepachangelog.com/en/1.1.0/)**
and this project adheres to **[Semantic Versioning](https://semver.org/spec/v2.0.0.html)**.

---

## [Unreleased] - yyyy-mm-dd

### Added

### Changed

### Deleted

---

## [0.1.1] - 2025-12-11

### Minor

- Update CITATION.cff

---

## [0.1.0] - 2025-12-11

### Added

- Initial release of the Chicago identity dataset package.
- Raw Chicago contracts CSV (2025-12-11 snapshot).
- Processed vendor-name identity sample (20k rows).
- Manifest and index metadata under `data-out/`.
- Sample-generation script (`make_chicago_identity_sample.py`).
- PROV and citation metadata.
- Documentation and project scaffolding.

---

## Notes on versioning and releases

- **SemVer policy**
  - **MAJOR** - breaking API/schema or CLI changes.
  - **MINOR** - backward-compatible additions and enhancements.
  - **PATCH** - documentation, tooling, or non-breaking fixes.
- Versions are driven by git tags via `setuptools_scm`.
  Tag the repository with `vX.Y.Z` to publish a release.
- Documentation and badges are updated per tag and aliased to **latest**.

[Unreleased]: https://github.com/civic-interconnect/civic-interconnect/compare/v0.1.1...HEAD
[0.1.1]: https://github.com/civic-interconnect/civic-interconnect/releases/tag/v0.1.1
[0.1.0]: https://github.com/civic-interconnect/civic-interconnect/releases/tag/v0.1.0
