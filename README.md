# wlm-server
Server for controlling and monitoring High Finesse wavelength meter

[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=snu-quiqcl_wlm-server&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=snu-quiqcl_wlm-server)
[![Pylint](https://github.com/snu-quiqcl/wlm-server/actions/workflows/pylint.yml/badge.svg?branch=develop)](https://github.com/snu-quiqcl/wlm-server/actions/workflows/pylint.yml)

## Caution
- There must be at least one item in the Operation and Setting model for each channel.
- This server must be run in a single-process configuration (no multiple worker processes).
