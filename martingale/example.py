
import random
import pandas as pd
from tqdm import tqdm
import logging
import time

logging.basicConfig(level=logging.ERROR)

def simulate_martingale(initial_balance, bet_pct, win_probability, max_cumulative_bets):
    balance = initial_balance
    cumulative_bets = 0
    bet_count = 0
    rounds_data = []
    next_bet = None 

    while balance > 0 and cumulative_bets < max_cumulative_bets:
        start_balance = balance
        if next_bet is None: 
            bet = round(bet_pct * balance, 0)
        else:
            bet = next_bet
        outcome = None
        if random.random() < win_probability:
            balance += bet
            next_bet = None
            outcome = 'W'
        else:
            balance -= bet
            next_bet =min(bet * 2, balance)
            outcome = 'L'
        cumulative_bets += bet
        bet_count += 1
        rounds_data.append({
            'round': bet_count,
            'start_balance': start_balance,
            'bet': bet,
            'outcome': outcome,
            'end_balance': balance,
            'cumulative_bets': cumulative_bets
        })
        

    success = balance > 0 and cumulative_bets >= max_cumulative_bets
    return balance, bet_count, cumulative_bets, success, rounds_data

def run_simulations(num_simulations, initial_balance, bet_pct, win_probability, max_cumulative_bets):
    results = []
    for i in tqdm(range(num_simulations), desc="Running simulations"):
        
        try:
            final_balance, bet_count, total_bets, success, rounds_data = simulate_martingale(initial_balance, bet_pct, win_probability, max_cumulative_bets)
            if bet_count > max_cumulative_bets:
                logging.error(f"Simulation {i + 1} got stuck: bet_count={bet_count}")
            results.append({
                'simulation': i + 1,
                'final_balance': final_balance,
                'bet_count': bet_count,
                'cumulative_bets': total_bets,
                'success': success,
                'rounds_data': rounds_data
            })
            time.sleep(1e-6)
        except Exception as e:
            logging.error(f"Error in simulation {i + 1}: {e}")
    return pd.DataFrame(results)