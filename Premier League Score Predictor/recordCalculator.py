import csv
import datetime
from collections import defaultdict

with open('PremierLeagueMatches.csv', 'r', newline='') as file:
    myReader = csv.DictReader(file)
    headers = myReader.fieldnames
    allRows = list(myReader)

if 'PrevHomePoints' not in headers:
    headers.append('PrevHomePoints')
if 'PrevAwayPoints' not in headers:
    headers.append('PrevAwayPoints')

# Parse matches
matches = []
for i, row in enumerate(allRows):
    try:
        matchDate = datetime.datetime.strptime(row['Date'], '%d/%m/%Y')
        matches.append({
            'date': matchDate,
            'matchday': int(row['Matchday']),
            'homeTeam': row['Home Team'],
            'awayTeam': row['Away Team'],
            'result': row['Result'],
            'rowIndex': i
        })
    except (ValueError, KeyError) as e:
        print(f"Error processing row {i}: {e}")

# Sort by date and then by matchday to ensure chronological order
matches.sort(key=lambda x: (x['date'], x['matchday']))

# Detect season transitions
seasons = []
currentSzn = []
currentSznStart = None

for i, match in enumerate(matches):
    mD = match['date']
    
    # Detect new season: first match or big gap between matches
    if i == 0 or (currentSzn and (mD - currentSzn[-1]['date']).days > 50):
        if currentSzn:
            seasons.append(currentSzn)
        currentSzn = [match]
        currentSznStart = mD
    else:
        currentSzn.append(match)

# Add the last season
if currentSzn:
    seasons.append(currentSzn)

rowToPoints = {}

for season in seasons:
    print(f"Processing season starting {season[0]['date'].strftime('%Y-%m-%d')}")
    teamPoints = defaultdict(int)
    
    for match in season:
        homeTeam = match['homeTeam']
        awayTeam = match['awayTeam']
        
        # Store pre-match points
        rowToPoints[match['rowIndex']] = {
            'homePoints': teamPoints[homeTeam],
            'awayPoints': teamPoints[awayTeam]
        }
        
        if match['result'] == 'H':
            teamPoints[homeTeam] += 3
        elif match['result'] == 'A':
            teamPoints[awayTeam] += 3
        elif match['result'] == 'D':
            teamPoints[homeTeam] += 1
            teamPoints[awayTeam] += 1

# Write updated data back to file
newFilename = 'PremierLeagueMatchesUpdated.csv'

with open(newFilename, 'w', newline='') as file:
    myWriter = csv.DictWriter(file, fieldnames=headers)
    myWriter.writeheader()
    
    for i, row in enumerate(allRows):
        if i in rowToPoints:
            row['PrevHomePoints'] = str(rowToPoints[i]['homePoints'])
            row['PrevAwayPoints'] = str(rowToPoints[i]['awayPoints'])
        else:
            row['PrevHomePoints'] = '0'
            row['PrevAwayPoints'] = '0'
        
        myWriter.writerow(row)