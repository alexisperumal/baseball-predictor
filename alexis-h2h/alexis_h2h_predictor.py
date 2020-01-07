# alexis_h2h_predictor.py - Python Package
# Alexis Perumal, Venkat Pinnika, Young You, 1/6/2020
# 
# Scope: Provide a function to calculate predictions across a range of gamedates with # a specified lookback amount of days. Prediction results returned.
#
# Derived from "net_points_predictor.py" on 1/6/19
#
# Dataset origin:
#      The information used here was obtained free of
#      charge from and is copyrighted by Retrosheet.  Interested
#      parties may contact Retrosheet at "www.retrosheet.org".

# Modules
import os
import csv
import pprint
import pandas as pd
import glob
import pprint
import datetime


def read_source_data():
    def reader(f):
        df = pd.read_csv(f, index_col=False, header=None)  
        df.columns = [("Col_"+str(i)) for i in range(1,df.shape[1]+1)]       
        return df

    files = glob.glob("../datasets/Final_Data_Files/GL*.csv")
    files.sort()
    df = pd.concat([reader(f) for f in files])
    old_df_len = len(df)
    
    # Insert column headers
    df = df.rename(columns={'Col_1':'Date',
                            'Col_4':'Visiting Team',
                            'Col_5':'Visiting League',
                            'Col_7':'Home Team',
                            'Col_8':'Home League',
                            'Col_10':'Visiting Score',
                            'Col_11':'Home Score'})
    df = df[['Date', 'Visiting Team', 'Visiting League', 'Home Team', 'Home League',
                       'Visiting Score','Home Score']]
    
#     print(df.head(30))
    df = df.replace('FLO','MIA') # After the 2011 season, the Florida Marlins
                                 # rebranded themselves the Miami Marlins. This
                                 # search and replace makes the two the same.
#     print(df.head(30))
    
    # Drop all rows with missing information
    # print(df.head())
    df = df.dropna(how='any')
    if len(df) < old_df_len:
        print(f"Dropped {old_df_len-len(df)} rows due to missing data.")
    
    # Create new columns we'll need. 
    df['Home Winner'] = df['Home Score'] > df['Visiting Score']
    df['V NetRuns'] = df['Visiting Score'] - df['Home Score']
    df['H NetRuns'] = - df['V NetRuns']
    
    #     print(df.shape)
    print(f"Dataset loaded with {df.shape[0]} games, ", end='')
    print(f"{df.shape[1]} columns, {date_str(df.iloc[0, 0])} - ", end='')
    print(f"{date_str(df.iloc[-1,0])}")
    return df


def date_str(date: int):
    s = str(date)
    return f"{s[0:4]}-{s[4:6]}-{s[6:]}"


# Passed the gamedays series (YYYYMMDD) and season (year) return with the first
# and last game dates.
def date_range(gamedays, season):
    # Converts 'YYYY' string to an integer start date, YYYY0101 and end date YYYY1231
    def season_to_date(season): 
        return (int(season)*10000 + 101, int(season)*10000+1231)
        # Hack to shorten the season for dev purposes (faster analysis)
#         return (int(season)*10000 + 101, int(season)*10000+531)
    
    first_of_year, last_of_year = season_to_date(season)
    season_gamedays = gamedays.loc[((gamedays >= first_of_year) &
                                    (gamedays <= last_of_year))]
    return (season_gamedays.iloc[0], season_gamedays.iloc[-1])
    

# returns new game date offset by n. Passed in the gamedays series.
def gamedays_offset(gamedays, base_date, n): 
    if base_date not in gamedays.values:
        raise ValueError(f"{base_date}, not in the the gamedays series.")
    base_date_index = gamedays[gamedays==base_date].index[0]
    if ((n + base_date_index) < 0) or n + base_date_index >= len(gamedays):
        raise ValueError(f"Attempting to calculate a game date outside the dataset.")
        return(0)  # Out of range
    else:
        new_index = base_date_index + n
        return gamedays.iloc[new_index]


def build_h2h_results_df(games_df):
    h2h_df = games_df.copy(deep=True)
    h2h = games_df.groupby(['Visiting Team', 'Home Team']).mean()
    print(h2h.head())
    sys.exit()
    return h2h


# Return true if predict home wins based on prior head-to-head matchups.
def lookup_h2h(df, v_team, h_team, game_day, lookback_n, prioritize_wins=True):
    h2h_df = df.loc[((df['Date'] < game_day) & (df['Visiting Team']==v_team) & \
                     (df['Home Team']==h_team))]
    n_games = len(h2h_df)
    n_home_wins = h2h_df['Home Winner'].values.sum()
    n_h_net_runs = h2h_df['H NetRuns'].sum()
    n_v_net_runs = h2h_df['V NetRuns'].sum()
    
    if prioritize_wins:
        if n_home_wins == (n_games // 2):
            return n_h_net_runs >= n_v_net_runs # tie goes to the home team
        else:
            return n_home_wins > (n_games // 2)
    else:
        if n_h_net_runs == n_v_net_runs:
            return n_home_wins >= (n_games // 2) # tie goes to the home team
        else:
            return n_h_net_runs > n_v_net_runs

# Now calculate the predictions and results on a rolling basis
def calc_predictions(games_df, start_date, end_date, lookback_n, gdays):
    start_processing = datetime.datetime.now()
    
    results_df = games_df.loc[((games_df['Date'] >= start_date) &
                               (games_df['Date'] <= end_date)) \
                             ].copy(deep=True)
    
    for game in results_df.index:
        v_team = results_df.loc[game, 'Visiting Team']
        h_team = results_df.loc[game, 'Home Team']
        g_day = results_df.loc[game, 'Date']
        results_df.at[game, 'Predict Home Wins?'] = lookup_h2h(games_df, v_team, h_team, g_day, \
                                                               lookback_n)

    results_df['Prediction Correct?'] = results_df['Predict Home Wins?'] == results_df['Home Winner']

    end_processing = datetime.datetime.now()
    duration = end_processing - start_processing
    print(f'  {end_processing}: Predictions calculated in {duration} hr/min/sec.')
    # print("")
    return results_df


def derive_metrics(results_df):
    num_games = len(results_df)
    num_correct = results_df['Prediction Correct?'].values.sum()
    percent_correct = num_correct/num_games*100.
    return (num_games, num_correct, percent_correct)
    
    
# Predictor to be called by the harness, passed in the lookback_n and season (year).
# lookback_n indicates how many prior game days to consider when calculating net
# points (runs) for prediction purposes.
def h2h_predictor(lookback_n, season):
    games_df = read_source_data()
    gamedays = pd.Series(games_df['Date'].unique())  # Series with gamedays.
    start_date, end_date = date_range(gamedays, season)
    
    print(f"  Analyzing {season} season: {date_str(start_date)}", end='')
    print(f" - {date_str(end_date)}, with {lookback_n} day lookback.")
    
    # h2h = build_h2h_results_df(games_df)
    
    results_df = calc_predictions(games_df, start_date, end_date, lookback_n, gamedays)
    
    return derive_metrics(results_df)
