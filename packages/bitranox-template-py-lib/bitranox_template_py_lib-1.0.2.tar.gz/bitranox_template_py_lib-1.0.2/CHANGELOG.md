# Changelog

All notable changes to this project will be documented in this file following
the [Keep a Changelog](https://keepachangelog.com/) format.

## [1.0.2] - 2025-12-15

### Changed
- Update CI/CD workflows to use latest GitHub Actions (cache@v5, upload-artifact@v6)
- Update dev dependencies: ruff 0.14.9, textual 6.9.0, import-linter 2.9
- Switch scripts to use rtoml for TOML parsing

### Added
- Add rtoml to dev dependencies

## [1.0.1] - 2025-12-08

### Changed
- Update dependencies to latest versions
- Update CI/CD workflows and configuration
- Convert docstrings to Google style
- Set coverage output to JSON to avoid SQL locks

## [1.0.0] - 2025-11-04
- Bootstrap `bitranox_template_py_lib`
