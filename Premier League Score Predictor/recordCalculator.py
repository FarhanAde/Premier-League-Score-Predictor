import csv
import datetime
from collections import defaultdict

matches = []
allRows = []

with open('PremierLeagueMatches.csv', 'r', newline='') as file:
    myReader = csv.DictReader(file)
    headers = myReader.fieldnames
    
    if 'PrevHomePoints' not in headers:
        headers.append('PrevHomePoints')
    if 'PrevAwayPoints' not in headers:
        headers.append('PrevAwayPoints')
    
    for row in myReader:
        allRows.append(row)
        
        try:
            matchDate = datetime.datetime.strptime(row['Date'], '%d-%m-%Y')
            matches.append({
                'date': matchDate,
                'matchday': int(row['Matchday']),
                'homeTeam': row['Home Team'],
                'awayTeam': row['Away Team'],
                'homeScore': int(row['homeScore']),
                'awayScore': int(row['awayScore']),
                'result': row['Result'],
                'rowIndx': len(matches)
            })
        except (ValueError, KeyError) as e:
            continue

matches.sort(key=lambda x: x['date'])

# Identify season transitions
seasons = []
currentSzn = []

for i, match in enumerate(matches):
    # Start of data or matchday 1 indicates new season
    if i == 0 or (match['matchday'] == 1 and len(currentSzn) > 0):
        if currentSzn:
            seasons.append(currentSzn)
        currentSzn = [match]
    else:
        currentSzn.append(match)

if currentSzn:
    seasons.append(currentSzn)

# Process each season and calculate points
pointsMap = {}

for season in seasons:
    # Reset points for the new season
    teamPoints = defaultdict(int)
    
    for match in season:
        # Get points before the match
        homeTeam = match['homeTeam']
        awayTeam = match['awayTeam']
        homePoints = teamPoints[homeTeam]
        awayPoints = teamPoints[awayTeam]
        
        matchDate = match['date'].strftime('%d-%m-%Y')
        
        # Create a unique key for each match
        key = (matchDate, homeTeam, awayTeam)
        pointsMap[key] = {
            'homePoints': homePoints,
            'awayPoints': awayPoints
        }
        
        if match['result'] == 'H':
            teamPoints[homeTeam] += 3
        elif match['result'] == 'A':
            teamPoints[awayTeam] += 3
        elif match['result'] == 'D':
            teamPoints[homeTeam] += 1
            teamPoints[awayTeam] += 1

newFilename = 'PremierLeagueMatchesUpdated2.csv'

with open(newFilename, 'w', newline='') as file:
    myWriter = csv.DictWriter(file, fieldnames=headers)
    myWriter.writeheader()
    
    for row in allRows:
        date = row['Date']
        homeTeam = row['Home Team']
        awayTeam = row['Away Team']
        
        key = (date, homeTeam, awayTeam)
        if key in pointsMap:
            row['PrevHomePoints'] = str(pointsMap[key]['homePoints'])
            row['PrevAwayPoints'] = str(pointsMap[key]['awayPoints'])
        else:
            row['PrevHomePoints'] = '0'
            row['PrevAwayPoints'] = '0'
        
        myWriter.writerow(row)
