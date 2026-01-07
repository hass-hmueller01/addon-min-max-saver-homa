<!-- https://developers.home-assistant.io/docs/add-ons/presentation#keeping-a-changelog -->
# Changelog

All changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [1.1.0] - 2026-01-07
### Changed
- Using addon.py from git (https://github.com/hass-hmueller01/hass-addon-helper.git)
- Using Python venv (instead breaking system packages)

## [1.0.0] - 2025-12-08
- Removed armhf, armv7, i386 architectures as removed in home-assistant/builder 2025.11.0

## [0.1.5] - 2025-10-04
- Added icon

## [0.1.4] - 2025-10-03
- Load Home Assistant options only once (refactored mqtt_config.py and renamed to config.py)
- Updated setup.py script

## [0.1.3] - 2025-10-03
- Using debug setting from Home Assistant config

## [0.1.2] - 2025-07-31

## [0.1.1] - 2025-07-28

## [0.1.0] - 2025-07-27
- Initial release
