# net_points_predictor.py - Python Package
# Alexis Perumal, Venkat Pinnika, Young You, 1/5/2020
# 
# Scope: Provide a function to calculate predictions across a range of gamedates with # a specified lookback amount of days. Prediction results returned.
#
# Derived from "baseball-predictor.ipynb" which was derived from
# "hello-worldpredictor.ipynb"
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


# Create a DF to hold team stats starting at the beginning of the lookback window.
def build_netpoints_dfs(games_df, start_date, end_date, lookback_n, gdays):
    start_processing = datetime.datetime.now()
    print(f"  {start_processing}: Starting build of net runs rolling average tables.")

    # Determine lookback dates for first game day.
    lookback_start_day = gamedays_offset(gdays, start_date, -lookback_n)
    lookback_end_day = gamedays_offset(gdays, start_date, -1)
    
    # Update gamedays to the dates we care about (prediction range and lookback)
    gdays = gdays.loc[((gdays >= lookback_start_day) & (gdays <= end_date))]

    # Create home and visitor tables to hold net points, by team and gameday.
    # Start with the visiting teams.
    v_teams = games_df['Visiting Team'].unique()
    v_teams.sort()
    v_np_df = pd.DataFrame(columns=v_teams, index=gdays) # Visiting net points by day
    v_ng_df = pd.DataFrame(columns=v_teams, index=gdays) # Visiting # games by day

    # Calculate the home team net points.
    h_teams = games_df['Home Team'].unique()
    h_teams.sort()
    h_np_df = pd.DataFrame(columns=h_teams, index=gdays) # Home net points by day
    h_ng_df = pd.DataFrame(columns=h_teams, index=gdays) # Home # games by day

    # Now populate the visiting and home team net points by game day dataframe
    for day in v_np_df.index:
        for team in v_np_df.columns: # Visiting Team Data
            net_runs = games_df.loc[((games_df['Visiting Team']==team)&
                       (games_df['Date']==day)),:]['V NetRuns'].sum()
            num_games = games_df.loc[((games_df['Visiting Team']==team)&
                        (games_df['Date']==day)),:]['V NetRuns'].count()
            v_np_df.at[day, team] = net_runs
            v_ng_df.at[day, team] = num_games

        for team in h_np_df.columns: # Home Team Data
            net_runs = games_df.loc[((games_df['Home Team']==team)&
                                     (games_df['Date']==day)),:]['H NetRuns'].sum()
            num_games = games_df.loc[((games_df['Home Team']==team)&
                               (games_df['Date']==day)),:]['H NetRuns'].count()
            h_np_df.at[day, team] = net_runs
            h_ng_df.at[day, team] = num_games

    # Now populate the visiting team net points rolling averages dataframe
    # Avg = sum of net points divided by # of games
    v_ra_np_df = v_np_df.rolling(lookback_n).sum() / \
        v_ng_df.rolling(lookback_n).sum()  # Rolling average of mean net points
    h_ra_np_df = h_np_df.rolling(lookback_n).sum() / \
        h_ng_df.rolling(lookback_n).sum()  # Rolling average of mean net points

    end_processing = datetime.datetime.now()
    duration = end_processing - start_processing
    print(f'  {end_processing}: Net point tables calculated in {duration} hr/min/sec.')

    return (v_ra_np_df, h_ra_np_df)


# Now calculate the predictions and results on a rolling basis
def calc_predictions(games_df, v_ra_np_df, h_ra_np_df, start_date, end_date, \
                     lookback_n, gdays):
    start_processing = datetime.datetime.now()

    # Go through all the games and make the predictions
    results_df = games_df.loc[((games_df['Date'] >= start_date) &
                               (games_df['Date'] <= end_date)) \
                             ].copy(deep=True)
    results_df['Predict Home Wins?'] = ""
    # results_df['Prediction Correct?'] = ""
    print(f"  Results table of length {len(results_df)}")

    for game in results_df.index:
        game_day = results_df.loc[game,'Date']
        v_team = results_df.loc[game, "Visiting Team"]
        h_team = results_df.loc[game, "Home Team"]
        v_avg_np = v_ra_np_df.loc[game_day, v_team]
        h_avg_np = h_ra_np_df.loc[game_day, v_team]
        results_df.at[game, 'Predict Home Wins?'] = h_avg_np >= v_avg_np # Tie goes to home because home bats last

    # results_df.loc['Prediction Correct?'] = results_df['Predict Home Wins?'] == results_df['Home Winner']
    results_df['Prediction Correct?'] = results_df['Predict Home Wins?'] == results_df['Home Winner']

    # print(train_df.tail())

    end_processing = datetime.datetime.now()
    duration = end_processing - start_processing
    print(f'  {end_processing}: Predictions calculated in {duration} hr/min/sec.')
    print("")
    return results_df


def derive_metrics(results_df):
    num_games = len(results_df)
    num_correct = results_df['Prediction Correct?'].values.sum()
    percent_correct = num_correct/num_games*100.
    return (num_games, num_correct, percent_correct)
    
    
# Predictor to be called by the harness, passed in the lookback_n and season (year).
# lookback_n indicates how many prior game days to consider when calculating net
# points (runs) for prediction purposes.
def net_points_predictor(lookback_n, season):
    games_df = read_source_data()
    gamedays = pd.Series(games_df['Date'].unique())  # Series with gamedays.
    start_date, end_date = date_range(gamedays, season)
    
    print(f"  Analyzing {season} season: {date_str(start_date)}", end='')
    print(f" - {date_str(end_date)}, with {lookback_n} day lookback.")
#     print("")
#     print(f"Starting games_df length: {len(games_df)}")
    (v_ra_np_df, h_ra_np_df) = build_netpoints_dfs(games_df, start_date, end_date, \
                                                  lookback_n, gamedays)
#     print(f"Ending games_df length: {len(games_df)}")
    
    results_df = calc_predictions(games_df, v_ra_np_df, h_ra_np_df, start_date, \
                                  end_date, lookback_n, gamedays)
    
    return derive_metrics(results_df)
