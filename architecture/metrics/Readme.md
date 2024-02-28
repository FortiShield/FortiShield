<!---
Copyright (C) 2015, Fortishield Inc.
Created by Fortishield, Inc. <info@fortishield.github.io>.
This program is free software; you can redistribute it and/or modify it under the terms of GPLv2
-->

# Metrics

## Index

- [Metrics](#metrics)
  - [Index](#index)
  - [Purpose](#purpose)
  - [Sequence diagram](#sequence-diagram)

## Purpose

Fortishield includes some metrics to understand the behavior of its components, which allow to investigate errors and detect problems with some configurations. This feature has multiple actors: `fortishield-remoted` for agent interaction messages, `fortishield-analysisd` for processed events.

## Sequence diagram

The sequence diagram shows the basic flow of metric counters. These are the main flows:

1. Messages received by `fortishield-remoted` from agents.
2. Messages that `fortishield-remoted` sends to agents.
3. Events received by `fortishield-analysisd`.
4. Events processed by `fortishield-analysisd`.
