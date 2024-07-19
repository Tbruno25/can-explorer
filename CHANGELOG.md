# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

---
## [0.2.1] - 2024-07-19

### Fixed

- Message buffer slider bug 

---
## [0.2.0] - 2024-07-19

### Changed

- Re-implemented using MVC design pattern

### Added

- Prevent user from applying new settings while active

### Removed

- Internal global variables
- Support for python versions older than 3.10

---
## [0.1.8] - 2024-06-26

### Fixed

- Main button toggle state

---
## [0.1.7] - 2023-08-03

### Fixed

- Extra scrollbar issue when run on windows

---
## [0.1.6] - 2023-08-02

### Fixed

- Re-release with `ic_sim.log` included

---
## [0.1.5] - 2023-07-31

### Added

- `--demo` command line flag
- Gui functional test and resources

---
## [0.1.4] - 2023-05-02

### Fixed

- App slider when app is not running

---
## [0.1.3] - 2023-04-29

### Added

- CAN id format setting

---
## [0.1.2] - 2023-04-25

### Added

- Alternate method to launch app via `python -m can_explorer`
- Light theme GUI setting

---
## [0.1.1] - 2023-04-21

### Fixed

- Runtime errors encountered when testing app with `ICSim`

### Added

- Project logo and demo resources
- README

---
## [0.1.0] - 2023-04-20

### Added

- Reimplementation using DearPyGui
