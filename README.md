
# Blackjack Engine

A modular and extensible backend engine for simulating and managing Blackjack games. This project supports AI and human players, implements basic strategy and card counting, exposes a REST API for game and simulation interaction, and allows for configurable rule sets. It can be used for multi-player gameplay and for card counting research.

## Features

- 📊 **Simulation Engine**: This is the most well-supported and well-tested feature. Blackjack Engine can simulation hundreds of thousands of years of Blackjack per day on most consumer hardware, making it extremely good at testing the RoI under various conditions.
- ♠️ **Basic Strategy & Card Counting**: Includes rule-based and counting-based decision engines.
- 🧪 **REST API**: Interact with the engine via a RESTful API for game flow and simulations.
- 🎮 **Live Game Management**: Supports real-time game sessions.
- 🧠 **AI and Human Player Support**: Register human and AI players into sessions.
- 🐳 **Dockerized Setup**: Use `docker` and `docker-compose` for easy deployment.
- 🔧 **Customizable Rules**: Plug in different game rules, betting rules, dealer behavior, and more.

## Getting Started

### Prerequisites

- Python 3.10+
- Docker (for containerized deployment)
- Supports Fedora and Ubuntu.

### Installation

```bash
git clone https://github.com/coreyMerritt/blackjack-engine.git
cd blackjack-engine
./install-deps.sh
```

### Running the App

```bash
docker-compose up --build -d
```

## API

The API provides endpoints for:

- Creating and starting a game session
- Registering players
- Placing bets, making moves (hit, stand, double, split, etc.)
- Running single and multi-game simulations
- Fetching formatted results and metadata

## Simulations

Use shell scripts in the [`zz-test-client/`](./zz-test-client) directory to trigger:

- Single and multi-game simulation runs
- Game benchmarking and automated tests
- End-to-end interaction flows

Example:

```bash
./zz-test-client/run-simulation.sh localhost 1080
```

## Configuration

Game rules and simulation parameters can be customized via request bodies, and if using the `zz-test-client`, can be configured using the JSON files `single.json` and/or `multi.json`.

# License
## GNU GENERAL PUBLIC LICENSE
Version 3, 29 June 2007

Copyright (C) 2007 Free Software Foundation, Inc.

Everyone is permitted to copy and distribute verbatim copies of this license document, but changing it is not allowed.

## Preamble

The GNU General Public License is a free, copyleft license for software and other kinds of works.

The licenses for most software and other practical works are designed to take away your freedom to share and change the works. By contrast, the GNU General Public License is intended to guarantee your freedom to share and change all versions of a program—to make sure it remains free software for all its users. We, the Free Software Foundation, use the GNU General Public License for most of our software; it applies also to any other work released this way by its authors.

## TERMS AND CONDITIONS

### 0. Definitions.

This License refers to version 3 of the GNU General Public License.

The "Program" refers to any copyrightable work licensed under this License.

"You" refers to the licensee.

### 1. Source Code.

The Program must be distributed in source code form.

### 2. Basic Permissions.

You may run the Program for any purpose, and you may modify and share it under the terms of this License.

### 3. Protecting Users' Legal Rights.

This License protects users from legal restrictions that would prevent their use of the software.

### 4. Conveying Verbatim Copies.

You may copy and distribute verbatim copies of the Program's source code.

### 5. Conveying Modified Source Versions.

You may distribute modified versions under the same license, provided certain conditions are met.

### 6. Conveying Non-Source Forms.

You may distribute object code or executable forms under specific conditions, including making the source code available.

### 7. Additional Terms.

You may not impose further restrictions on the rights granted by this License.

### 8. Termination.

Violating the terms automatically terminates your rights under this License.

### 9. Acceptance Not Required.

You are not required to accept this License just to run a copy.

### 10. Automatic Licensing.

Each time you convey the Program, the recipient automatically receives a license under these terms.

### 11. Patents.

You grant a license to use any patents necessary to exercise the rights under this License.

### 12. No Surrender of Freedom.

You must not impose restrictions that conflict with this License.

### 13. Use with the GNU Affero GPL.

You may use this License with the GNU Affero GPL under certain conditions.

### 14. Revised Versions of this License.

The Free Software Foundation may publish revised and/or new versions of the GPL.

### 15. Disclaimer of Warranty.

THE PROGRAM IS PROVIDED WITHOUT WARRANTY.

### 16. Limitation of Liability.

THE COPYRIGHT HOLDERS ARE NOT LIABLE FOR DAMAGES.

---

## How to Apply These Terms to Your Work

Include the following notice in each source file:

```
Copyright (C) 2025 Corey Merritt

This file is part of the Blackjack Engine project.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
```


