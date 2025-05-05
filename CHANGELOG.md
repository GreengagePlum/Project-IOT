# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

### Changed

### Deprecated

### Removed

### Fixed

### Security

## [1.0.0] - 2025-05-11

### Added

* MQTT communications specification
* SQLite database
  * Schema, tables and constraint triggers
* Server side MQTT client
* Web UI (frontend work)
  * Jinja2 templates
  * Home page
  * Real time page
    * Browser MQTT client for direct access to sensor updates
  * History page (10 latest values recorded for each ESP32)
* Web server
  * Serve dynamic page
  * Respond to AJAX requests that demand details on a particular sensor from the database
* Web server -> server side MQTT client communications via POSIX pipe (FIFO to relay LED commands coming from the web UI to the ESP32s)

## [0.0.1] - 2025-04-03

### Added

* Initialized git repo with base files

[unreleased]: https://github.com/GreengagePlum/Project-IOT/compare/v1.0.0...HEAD

[1.0.0]: https://github.com/GreengagePlum/Project-IOT/compare/v0.0.1...v1.0.0

[0.0.1]: https://github.com/GreengagePlum/Project-IOT/releases/tag/v0.0.1
