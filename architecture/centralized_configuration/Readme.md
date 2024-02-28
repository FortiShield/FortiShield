<!---
Copyright (C) 2015, Fortishield Inc.
Created by Fortishield, Inc. <info@fortishield.github.io>.
This program is free software; you can redistribute it and/or modify it under the terms of GPLv2
-->

# Centralized Configuration
## Index
- [Centralized Configuration](#centralized-configuration)
  - [Index](#index)
  - [Purpose](#purpose)
  - [Sequence diagram](#sequence-diagram)

## Purpose

One of the key features of Fortishield as a EDR is the Centralized Configuration, allowing to deploy configurations, policies, rootcheck descriptions or any other file from Fortishield Manager to any Fortishield Agent based on their grouping configuration. This feature has multiples actors: Fortishield Cluster (Master and Worker nodes), with `fortishield-remoted` as the main responsible from the managment side, and Fortishield Agent with `fortishield-agentd` as resposible from the client side.


## Sequence diagram
Sequence diagram shows the basic flow of Centralized Configuration based on the configuration provided. There are mainly three stages:
1. Fortishield Manager Master Node (`fortishield-remoted`) creates every `remoted.shared_reload` (internal) seconds the files that need to be synchronized with the agents.
2. Fortishield Cluster as a whole (via `fortishield-clusterd`) continuously synchronize files between Fortishield Manager Master Node and Fortishield Manager Worker Nodes
3. Fortishield Agent `fortishield-agentd` (via ) sends every `notify_time` (ossec.conf) their status, being `merged.mg` hash part of it. Fortishield Manager Worker Node (`fortishield-remoted`) will check if agent's `merged.mg` is out-of-date, and in case this is true, the new `merged.mg` will be pushed to Fortishield Agent.