from bs4 import BeautifulSoup
import requests
import re
import sys
import requests

def is_ranked(game_object):
    class_of_game = game_object.find("div",class_="Content").find("div",class_="GameStats").find("div",class_="GameType").text.strip()
    return class_of_game == "Ranked Solo"

def is_remake(game_object):
    game_result = game_object.find("div",class_="Content").find("div",class_="GameStats").find("div",class_="GameResult").text.strip()
    return game_result == "Remake"

def get_team_color_and_victory(team_object):
    information = team_object.find("thead",class_="Header").find("tr",class_="Row").find("th",class_="HeaderCell").text.strip().split("\n")
    information = [x.replace("\t","") for x in information]
    if information[0] == "Sejr" and "Blå" in information[1]:
        information[0] = 1
    else:
        information[0] = 0
    if "Blå" in information[1]:
        information[1] = "Blue"
    else:
        information[1] = "Red"
    return information

def generate_game_id(game_data):
    big_list = []
    for team in sorted(game_data.keys()):
        if team != "Result":
            sorted_keys = sorted(game_data[team].keys())
            for attribute in sorted_keys:
                big_list += game_data[team][attribute]
    big_string = "_".join([str(x) for x in big_list])
    return abs(hash(big_string))


def get_player_database(all_game_data):
    player_database = dict()
    # Adding data to the player database
    for game in all_game_data:
        for team in all_game_data[game].keys():
            if team != "Result":
                for i,summoner_name in enumerate(all_game_data[game][team]["Summonernames"]):
                    if summoner_name not in player_database.keys():
                        player_database[summoner_name] = []
                        player_database[summoner_name].append(all_game_data[game][team]["Champions"][i])
                    else:
                        player_database[summoner_name].append(all_game_data[game][team]["Champions"][i])
    return player_database


def get_game_data_from_html(summoner_name):
    all_game_data = dict()
    number_of_games = 0
    with open("html_files/"+"{}.html".format(summoner_name)) as html_of_website:
        soup = BeautifulSoup(html_of_website, "lxml")
        # Getting the list of games
        all_lists_of_games = soup.find_all("div",class_="GameItemList")
        for list_of_games in all_lists_of_games:
            # Finding the container of each game.
            all_containers = list_of_games.find_all("div",class_="GameItemWrap")
            for i,game_container in enumerate(all_containers):
                # Isolate each game
                game = game_container.find("div",{'class': re.compile(r'GameItem')})

                # Sanity checks
                if not is_ranked(game):
                    continue
                if is_remake(game):
                    continue
                
                # Get the game details
                game_details = game.find("div","GameDetail")
                game_detail_wrap = game_details.find("div","GameDetailTableWrap")
                # A single game did not contain the wrapping 
                if game_detail_wrap is None:
                    continue

                # Getting the teams from each game
                teams = game_detail_wrap.find_all("table",{'class': re.compile(r'GameDetailTable Result')})

                # Storing the game data
                game_data = dict()
                blackflag = None
                for j,team in enumerate(teams):
                    # Getting the team color and who won.
                    team_color_and_victory = get_team_color_and_victory(team)
                    # Reading the database structures
                    game_data["Result"] = team_color_and_victory[0]
                    game_data[team_color_and_victory[1]] = dict()
                    game_data[team_color_and_victory[1]]["Champions"] = []
                    game_data[team_color_and_victory[1]]["Summonernames"] = []
                    game_data[team_color_and_victory[1]]["Rankings"] = []
                    game_data[team_color_and_victory[1]]["champ_winrate"] = []
                    game_data[team_color_and_victory[1]]["champ_total_games"] = []

                    team_content = team.find("tbody","Content")
                    players = team_content.find_all("tr",{'class': re.compile(r'Row')})
                    for player in players:
                        # Get the information from each player
                        champion_name = player.find("td","ChampionImage Cell").text.strip().split("\n")[0]
                        summoner_name = player.find("td","SummonerName Cell").text.strip()
                        summoner_rank = player.find("td",{'class': re.compile(r'Tier Cell')}).text.strip()
                        try:
                            winrate,games_played = get_winrate_and_games_on_champ(summoner_name,champion_name)
                        except KeyError:
                            winrate,games_played = "nan","nan"
                        
                        if winrate == "nan" and games_played == "nan":
                            blackflag = True
                            break

                        # Add the information to the dictionary
                        game_data[team_color_and_victory[1]]["Champions"].append(champion_name)
                        game_data[team_color_and_victory[1]]["Summonernames"].append(summoner_name)
                        game_data[team_color_and_victory[1]]["Rankings"].append(summoner_rank)
                        game_data[team_color_and_victory[1]]["champ_winrate"].append(winrate)
                        game_data[team_color_and_victory[1]]["champ_total_games"].append(games_played)

                game_id = generate_game_id(game_data)
                if game_id not in all_game_data.keys() and not blackflag:
                    all_game_data[game_id] = game_data.copy()
                    number_of_games += 1
                    print("Game saved:", number_of_games)
    return all_game_data

def get_winrate_and_games_on_champ(summoner_name,champion):
    summoner_query = summoner_name.replace(" ","%20").lower()
    champion_stats = dict()
    # website = "https://www.leagueofgraphs.com/summoner/champions/eune/{}".format(summoner_query)
    print(summoner_query)
    website="https://u.gg/lol/profile/eun1/{}/champion-stats".format(summoner_query)
    print(website)
    source = requests.get(website).text
    soup = BeautifulSoup(source,"lxml")
    try:
        content = soup.find("div",class_="summoner-profile_champion-stats").div.find("div",class_="rt-tbody")
    except AttributeError:
        return "nan","nan"
    rows_in_content = content.find_all("div",class_="rt-tr-group")
    for row in rows_in_content:
        champion_name = row.div.find("div",{'class': re.compile(r'rt-td champion-cell')}).find("span",class_="champion-name").text.strip()
        winrate_cell = row.div.find("div",{'class': re.compile(r'rt-td win-rate-cell')})
        numbers = "0123456789 "
        winrate_text = "".join([x for x in winrate_cell.find("div",class_="champion-rates").text if x in numbers]).split()
        winrate  = int(winrate_text[0])/100
        total_games = int(winrate_text[1]) + int(winrate_text[2])
        champion_stats[champion_name] = (winrate,total_games)

    return champion_stats[champion]

if __name__ == "__main__":
    # all_game_data = get_game_data_from_html("Young Peder")
    # player_database = get_player_database(all_game_data)
    # print("Number of games:",len(all_game_data.keys()))
    # for player in player_database:
    #     print(player,player_database[player])
    # get_winrate_and_games_on_champ("Young Peder")
    get_winrate_and_games_on_champ("BMW SirAirmaster","Aatrox")

