import webscraper as wb
import selenium_scripts as ss
import os
import json
import sys
import pandas as pd

def save_database(filename,dictionary):
    with open(filename, 'w') as fp:
        json.dump(dictionary, fp)

def load_database(filename):
    with open(filename, "r") as json_file:
        my_dict = json.load(json_file)
    return my_dict


def get_game_data(first_summoner,limit):
    print("Queing:",first_summoner)
    ss.get_html_code_from_summoner(first_summoner)
    all_game_data = wb.get_game_data_from_html(first_summoner)
    all_player_database = wb.get_player_database(all_game_data)

    print("Number of games in gamedatabase:",len(all_game_data))
    print("Number of players in database:",len(all_player_database))
    unique_players = sorted(list(all_player_database.keys()))


    i = 0
    while len(all_game_data) < limit:
        player = unique_players[i]
        players_qued = [x[:-5] for x in os.listdir("html_files/")]
        if player not in players_qued:
            print("Queing:",player)
            ss.get_html_code_from_summoner(player)
            game_data_player = wb.get_game_data_from_html(player)
            player_database = wb.get_player_database(game_data_player)

            for game in game_data_player.keys():
                if game not in all_game_data.keys():
                    all_game_data[game] = game_data_player[game]
            
            for player in player_database.keys():
                if player not in all_player_database.keys():
                    all_player_database[player] = player_database[player]

            print("Number of games in gamedatabase:",len(all_game_data.keys()))
            print("Number of players in database:",len(all_player_database.keys()))
            unique_players = sorted(list(all_player_database.keys()))
        i+=1
    return all_game_data, all_player_database

def calculate_elo(Rankings):
    tier_to_elo = {"Iron":100, "Bronze":200, "Silver":300, "Gold":400, "Platinum":500, "Diamond":600, "Master":700, "Grandmaster":800, "Challenger":900}
    division_to_elo = {"1":80, "2":60, "3":40, "4":20,"0":0}
    elos = []
    for ranking in Rankings:
        if len(ranking.split()) == 1:
            tier = ranking
            division = "0"
        else:
            tier, division = (str(x) for x in ranking.split())
        if tier == "Level":
            elo = 0
        else:
            elo = tier_to_elo[tier] + division_to_elo[division]
        elos.append(elo)
    return elos

def generate_dataset(all_game_data,save_name):
    features = ['Rankings', 'champ_winrate', 'champ_total_games']
    teams = ["Blue","Red"]
    dataset = []
    header = []

    # Creating the header
    roles = ["Top", "Jungle", "Mid", "ADC", "Support"]
    for feature in features:
        for team in teams:
            for role in roles:
                attribute = "{}_{}_{}".format(feature.lower(),team.lower(),role.lower())
                header.append(attribute)
    header += ["result"]

    # Adding the data
    for game in all_game_data.keys():
        entry = []
        for feature in features:
            for team in teams:
                if feature == "Rankings":
                    elos = calculate_elo(all_game_data[game][team][feature])
                    entry += elos.copy()
                else:
                    entry += all_game_data[game][team][feature]
        entry += [all_game_data[game]["Result"]]
        dataset.append(entry)

    data_frame = pd.DataFrame(dataset,columns=header)
    data_frame.to_csv(save_name)

if __name__ == "__main__":
    limit = 500
    # all_game_data, all_player_database = get_game_data("Young Peder",limit)
    # save_database("all_game_data_{}.json".format(limit),all_game_data)
    # save_database("all_player_database_{}.json".format(limit),all_player_database)
    all_game_data = load_database("all_game_data_500.json")
    generate_dataset(all_game_data,"500_game_data.csv")



