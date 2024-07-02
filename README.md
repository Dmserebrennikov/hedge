# PROJECT HEDGE: developed to hedge positions in MT5 forex brokers

## Architecture

There are three modules that should be run locally on your machine: `decision_center`, `client` and `hedge_broker`. One additional module `tumbler_broker` should be run on the server where Java application should be closed right after the signal (for "spike" users only).

As soon as a trading signal is issued, the system analyzes the opening of a position in each broker-client. Upon opening a position, the system immediately sends the corresponding information to the decision center. Almost simultaneously, the tumbler module closes the Java application on the server (ensure that the brokers requiring hedging are running on this server). In the hedge_broker, the closing of the position is tracked. As soon as at least one of the positions is closed, the system requests information about the trades requiring hedging from the decision center and opens the corresponding positions in the hedge_broker.

### DECISION CENTER

The main module, `decision_center.py`, serves as the 'brain' of the project, where all key decisions are made. In fact, the decision center is a database where information about all positions is stored and retrieved. The decision center is built using the FastAPI framework and currently consists of only two endpoints:

- **"/new_position/"** - adding a new trade to the database that needs to be hedged
- **"/all_positions/"** - returns a list of positions that need to be hedged

### CLIENT

This module runs an instance of the MT5 terminal with an account that requires hedging of positions. The script tracks the number of open positions and, if there is a new one, sends detailed information about the relevant position to the decision center. Each new account requires a new `client` instance to be run.

### HEDGE BROKER

This module runs an instance of the MT5 terminal with an account where all hedging positions will be opened.
The script operates in the following way:

- Track the number of open trades.
- Update the number of open trades if a new one is detected.
- If one of the positions is closed, the script requests information about the positions that require hedging and then opens corresponding positions

### TUMBLER BROKER

Additional module for "spike" users. This module runs an instance of the MT5 terminal with an account that requires hedging of positions (as well as `client`) on the server, where the Java application should be closed. Using this script it's possible to track the incoming signal (open position signal) and close the Java application to prevent the positions from being closed by the 'central close signal'.

## Usage

Navigate to the base folder in the command line and run the three modules:

```
python decision_center.py
```

```
python hedge_broker.py <path> <login> <password> <server> <prefix> <exec_mode> [<symbols> ...]
```

```
python client.py <path> <login> <password> <server> <prefix> <exec_mode> [<symbols> ...]
```
