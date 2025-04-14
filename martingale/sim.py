import random
import pandas as pd
import numpy as np
from tqdm import tqdm
import logging
import math
import json

logging.basicConfig(level=logging.DEBUG)  # Change to DEBUG level for more detailed logs

def simulate_martingale(initial_balance, bet_pct, win_probability, max_cumulative_bets):
    balance = initial_balance
    cumulative_bets = 0
    bet_count = 0
    rounds_data = {}
    next_bet = None 

    while balance > 0 and cumulative_bets < max_cumulative_bets:
        start_balance = balance
        if next_bet is None: 
            bet = math.ceil(bet_pct * balance)
        else:
            bet = next_bet
        outcome = None
        if random.random() < win_probability:
            balance += bet
            next_bet = None
            outcome = "W"
        else:
            balance -= bet
            next_bet = min(bet * 2, balance)
            outcome = "L"
        cumulative_bets += bet
        bet_count += 1
        rounds_data[f"round_{bet_count}"]=({
            "round": bet_count,
            "start_balance": start_balance,
            "bet": bet,
            "outcome": outcome,
            "end_balance": balance,
            "cumulative_bets": cumulative_bets
        })
        #logging.debug(f"Round {bet_count}: start_balance={start_balance}, bet={bet}, outcome={outcome}, end_balance={balance}, cumulative_bets={cumulative_bets}")

    success = balance > 0 and cumulative_bets >= max_cumulative_bets
    return balance, bet_count, cumulative_bets, success, rounds_data

def run_simulations(num_simulations, initial_balance, bet_pct, win_probability, max_cumulative_bets):
    results = []
    for i in tqdm(range(num_simulations), desc="Running simulations", mininterval=0.1):
        try:
            final_balance, bet_count, total_bets, success, rounds_data = simulate_martingale(initial_balance, bet_pct, win_probability, max_cumulative_bets)
            if bet_count > max_cumulative_bets:
                logging.warning(f"Simulation {i + 1} got stuck: bet_count={bet_count}")
            results.append({
                "simulation": i + 1,
                "final_balance": final_balance,
                "bet_count": bet_count,
                "cumulative_bets": total_bets,
                "success": success,
                "rounds_data": rounds_data
            })
            #logging.debug(f"Simulation {i + 1}: final_balance={final_balance}, bet_count={bet_count}, cumulative_bets={total_bets}, success={success}")
        except Exception as e:
            logging.error(f"Error in simulation {i + 1}: {e}")
    return pd.DataFrame(results)

def main():
    result = run_simulations(10000, 400, 0.05, 0.5, 10000)
    result.to_csv("simulation_results.csv", index=False)
    
    # Save rounds_data to a JSON file
    with open("rounds_data.json", "w") as json_file:
        #json.dump(round_dict, json_file, indent=4)
        json.dump(result.iloc[0]["rounds_data"], json_file, indent=4)
    #print(result)

if __name__ == "__main__":
    main()