import csv
import datetime
from collections import defaultdict
import os

def calculate_points_and_update_csv():
    # Step 1: Calculate points before matches (similar to original function)
    matches = []
    all_rows = []  # Store all rows including headers for rewriting
    
    # Read the CSV file and parse match data
    with open('PremierLeagueMatches.csv', 'r', newline='') as file:
        csv_reader = csv.DictReader(file)
        headers = csv_reader.fieldnames
        
        # Add new columns if they don't exist
        if 'PrevHomePoints' not in headers:
            headers.append('PrevHomePoints')
        if 'PrevAwayPoints' not in headers:
            headers.append('PrevAwayPoints')
        
        # Store all rows for later processing
        for row in csv_reader:
            all_rows.append(row)
            
            try:
                match_date = datetime.datetime.strptime(row['Date'], '%Y-%m-%d')
                matches.append({
                    'date': match_date,
                    'matchday': int(row['Matchday']),
                    'home_team': row['Home Team'],
                    'away_team': row['Away Team'],
                    'home_score': int(row['homeScore']),
                    'away_score': int(row['awayScore']),
                    'result': row['Result'],
                    'row_index': len(matches)  # Store the index of this row
                })
            except (ValueError, KeyError) as e:
                print(f"Error parsing row: {row}. Error: {e}")
                continue

    # Sort matches by date to ensure chronological order
    matches.sort(key=lambda x: x['date'])
    
    # Identify season transitions
    seasons = []
    current_season = []
    
    for i, match in enumerate(matches):
        # Start of data or matchday 1 after summer break indicates new season
        if i == 0 or (match['matchday'] == 1 and len(current_season) > 0):
            if current_season:
                seasons.append(current_season)
            current_season = [match]
        else:
            current_season.append(match)
    
    # Add the last season
    if current_season:
        seasons.append(current_season)
    
    # Process each season and calculate points
    points_mapping = {}  # Store points by date, home team and away team
    
    for season in seasons:
        # Reset points for the new season
        team_points = defaultdict(int)
        
        for match in season:
            # Get points before the match
            home_team = match['home_team']
            away_team = match['away_team']
            home_points = team_points[home_team]
            away_points = team_points[away_team]
            
            # Store the points for this match
            match_date = match['date'].strftime('%Y-%m-%d')
            
            # Create a unique key for each match
            key = (match_date, home_team, away_team)
            points_mapping[key] = {
                'home_points': home_points,
                'away_points': away_points
            }
            
            # Update points based on match result
            if match['result'] == 'H':  # Home win
                team_points[home_team] += 3
            elif match['result'] == 'A':  # Away win
                team_points[away_team] += 3
            elif match['result'] == 'D':  # Draw
                team_points[home_team] += 1
                team_points[away_team] += 1
    
    # Step 2: Update CSV file with points
    # Create a temporary file
    temp_filename = 'PremierLeagueMatches_updated.csv'
    
    with open(temp_filename, 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        
        for row in all_rows:
            date = row['Date']
            home_team = row['Home Team']
            away_team = row['Away Team']
            
            # Look up points for this match
            key = (date, home_team, away_team)
            if key in points_mapping:
                row['PrevHomePoints'] = str(points_mapping[key]['home_points'])
                row['PrevAwayPoints'] = str(points_mapping[key]['away_points'])
            else:
                row['PrevHomePoints'] = '0'
                row['PrevAwayPoints'] = '0'
            
            writer.writerow(row)
    
    # Replace the original file with the updated one
    os.replace(temp_filename, 'PremierLeagueMatches.csv')
    
    return len(all_rows), len(seasons)

# Execute the function
total_matches, num_seasons = calculate_points_and_update_csv()

# Print summary
print(f"Total matches updated: {total_matches}")
print(f"Total seasons identified: {num_seasons}")
print(f"The 'PrevHomePoints' and 'PrevAwayPoints' columns have been added to 'PremierLeagueMatches.csv'")