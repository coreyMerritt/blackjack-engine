
# Blackjack Engine

A modular and extensible backend engine for simulating and managing Blackjack games. This project supports AI and human players, implements basic strategy and card counting, exposes a REST API for game and simulation interaction, and allows for configurable rule sets. It can be used for multi-player gameplay and for card counting research.

## Features

- **Simulation Engine**: This is the most well-supported and well-tested feature. Blackjack Engine can simulation hundreds of thousands of years of Blackjack per day on most consumer hardware, making it extremely good at testing the RoI under various conditions.
- **Basic Strategy & Card Counting**: Includes rule-based and counting-based decision engines.
- **REST API**: Interact with the engine via a RESTful API for game flow and simulations.
- **Live Game Management**: Supports real-time game sessions.
- **AI and Human Player Support**: Register human and AI players into sessions.
- **Dockerized Setup**: Use `docker` and `docker-compose` for easy deployment.
- **Customizable Rules**: Plug in different game rules, betting rules, dealer behavior, and more.

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


## License

[GPLv3](LICENSE.md)

© 2025 Corey Merritt
