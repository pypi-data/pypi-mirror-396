# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.3] - 2025-12-12

### Changed

- Fix bug with custom soup objects in python3.14
- Fix bug with make rule for bumping

## [0.1.2] - 2025-10-30

### Added

- This changelog file.

### Changed

- Remove page number parsing when generating a page list. This allows for
  non-numeric page identifiers ("roman" or "special", as the spec would call
  them).
