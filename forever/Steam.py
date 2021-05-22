#from models.EmbedTemplate import EmbedTemplate
#import config
import datetime
import aiohttp
import asyncio
import time
import json
from forever.Utilities import Cache

class Steam_Account():
    steam_img_url = "https://steamcdn-a.akamaihd.net/steamcommunity/public/images/avatars"
    def __init__(self, id, name, profile_url, avatar_hash, time_created):
        self.id = id
        self.name = name
        self.profile_url = profile_url
        self.avatar_hash = avatar_hash
        self.time_created = time_created
    def get_full_avatar(self,):
        return "{}/{}/{}_full.jpg".format(Steam_Account.steam_img_url, self.avatar_hash[:2], self.avatar_hash)
    def get_medium_avatar(self,):
        return "{}/{}/{}_medium.jpg".format(Steam_Account.steam_img_url, self.avatar_hash[:2], self.avatar_hash)
    def get_avatar(self,):
        return "{}/{}/{}.jpg".format(Steam_Account.steam_img_url, self.avatar_hash[:2], self.avatar_hash)
class Dota_Bare_Match():
    def __init__(self, id, players, lobby_type, timestamp):
        self.id = id
        self.players = players
        self.lobby_type = lobby_type
        self.timestamp = timestamp
class Dota_Bare_Match_Player():
    def __init__(self, account_id, player_slot, hero_id):
        self.account_id = account_id
        self.player_slot = player_slot
        self.hero_id = hero_id
class Dota_Match():
    def __init__(self, id, players, game_mode, duration, start_time, radiant_win, radiant_kills, dire_kills, radiant_team, dire_team):
        self.id = id
        self.players = players
        self.game_mode = game_mode
        self.duration = duration
        self.start_time = start_time
        self.radiant_win = radiant_win
        self.radiant_kills = radiant_kills
        self.dire_kills = dire_kills
        self.radiant_team = radiant_team
        self.dire_team = dire_team
class Dota_Match_Player():
    def __init__(self, id, player_slot, hero_id, kills, deaths, assists, last_hits, denies, gpm, xpm, level, hero_dmg, building_dmg, healing, networth):
        self.id = id
        self.player_slot = player_slot
        self.hero_id = hero_id
        self.kills = kills
        self.deaths = deaths
        self.assists = assists
        self.last_hits = last_hits
        self.denies = denies
        self.gpm = gpm
        self.xpm = xpm
        self.level = level
        self.hero_dmg = hero_dmg
        self.building_dmg = building_dmg
        self.healing = healing
        self.networth = networth
        if isinstance(self.networth, tuple):
            gold_spent, gold = self.networth
            if gold_spent is None and gold is None:
                self.networth = None
            elif gold_spent is not None and gold is not None:
                self.networth = gold_spent+gold
            else:
                if gold is not None and gold_spent is None:
                    self.networth = gold
                else:
                    self.networth = gold_spent
class Dota_Match_History():
    def __init__(self, matches, wins, losses):
        self.matches = matches
        self.total_matches = len(self.matches)
        self.wins = wins
        self.losses = losses

    def __len__(self):
        return self.total_matches
class Complete_Account():
    def __init__(self, steam_profile, match_history):
        self.steam_profile = steam_profile
        self.match_history = match_history
    def win_rate(self,):
        return self.match_history.wins/len(self.match_history)
class Steam_API():
    cache = Cache()
    def __init__(self, api_url, api_key):
        self.last_request_timestamp = 0
        self.lock = asyncio.Lock()
        self.api_url = api_url
        self.api_key = api_key
    def steam_32bit_id_to_64bit(self, steam_32id):
        return int(steam_32id) + 76561197960265728
    def steam_64bit_id_to_32bit(self, steam_64id):
        return int(steam_64id) - 76561197960265728
    async def request(self, endpoint, params):
        async with self.lock:
            tmp = time.time() - self.last_request_timestamp
            if tmp < 1.1:
                await asyncio.sleep(1.1-tmp)
            params["key"] = self.api_key
            self.last_request_timestamp = time.time()
            async with aiohttp.ClientSession() as sess:
                async with sess.get("{}/{}".format(self.api_url, endpoint), params=params) as resp:
                    if resp.status == 200:
                        data = json.loads(await resp.text())
                        return data
                    else:
                        return None
    @cache.async_cached(3600)
    async def resolve_vanity_url(self, vanity_url):
        data = await self.request("ISteamUser/ResolveVanityURL/v0001/", {"vanityurl":vanity_url})
        if data and "response" in data and "steamid" in data["response"]:
            return int(data["response"]["steamid"])
        return None
    @cache.async_cached(3600)
    async def get_steam_profile(self, steam_64id):
        data = await self.request("ISteamUser/GetPlayerSummaries/v0002/", {"steamids": steam_64id})
        data = data["response"]["players"]
        if data:
            data = data[0]
            return Steam_Account(data["steamid"], data["personaname"], data["profileurl"], data["avatarhash"], data["timecreated"])
        return None
    @cache.async_cached(600)
    async def get_dota_last_matches(self, steam_32id, starting_match_id=None, hero_id=None, game_mode=None):
        params = {"account_id" : steam_32id, "matches_requested" : 500}
        if game_mode is not None:
            params["game_mode"] = game_mode
        if starting_match_id is not None:
            params["start_at_match_id"] = starting_match_id
        if hero_id is not None:
            params["hero_id"] = hero_id
        data = await self.request("IDOTA2Match_570/GetMatchHistory/V001/", params=params) 
        if data:
            is_there_more = True
            if data["result"]["results_remaining"] == 0 and data["result"]["num_results"] == 0:
                is_there_more = False

            matches = []
            for i in data["result"]["matches"]:
                players = []
                for x in players:
                    players.append(
                        Dota_Bare_Match_Player(x["account_id"], x["player_slot"], x["hero_id"])
                    )
                matches.append(
                    Dota_Bare_Match(
                        i["match_id"],
                        players,
                        i["lobby_type"],
                        i["start_time"]
                    )
                )
            return (matches, is_there_more)
    async def get_dota_player_match_history(self, steam_32id, hero_id=None, game_mode=None):
        matches = []
        new_matches = []
        matches, is_there_more = await self.get_dota_last_matches(steam_32id, None, hero_id, game_mode)
        while is_there_more:
            tmp, is_there_more = await self.get_dota_last_matches(steam_32id, matches[len(matches)-1].id-1, hero_id, game_mode)
            matches.extend(tmp)
        wins = 0
        key = "match_details_{}"
        for i in range(len(matches)):
            tmp = None
            if key.format(matches[i].id) not in Steam_API.cache:
                tmp = await self.get_dota_match_details(matches[i].id)
                Steam_API.cache.add(key.format(matches[i].id), tmp)
                new_matches.append(tmp)

            else:
                tmp = Steam_API.cache.get(key.format(matches[i].id))["function"]
            if steam_32id in tmp.dire_team and not tmp.radiant_win:
                wins += 1
            if steam_32id in tmp.radiant_team and tmp.radiant_win:
                wins += 1
            matches[i] = tmp
        losses = len(matches)-wins
        match_history = Dota_Match_History(matches, wins, losses)
        return (match_history, new_matches)
    async def get_dota_match_details(self, match_id):
        data = await self.request("IDOTA2Match_570/GetMatchDetails/v1", {"match_id":match_id})
        data = data.get("result")
        if data and "players" in data and len(data["players"]) > 1:
            players = {"dire" : {}, "radiant" : {}}
            dire_team_ids = set()
            radiant_team_ids = set()
            for i in data["players"]:
                key = "radiant"
                player_slot = i["player_slot"]

                if i["player_slot"] >= 128:
                    player_slot -= 128
                    key = "dire"
                    dire_team_ids.add(i.get("account_id"))
                else:
                    radiant_team_ids.add(i.get("account_id"))
                
                players[key][player_slot] = Dota_Match_Player(
                        id=i.get("account_id"),
                        player_slot=i["player_slot"],
                        hero_id=i["hero_id"],
                        kills=i["kills"],
                        deaths=i["deaths"],
                        assists=i["assists"],
                        last_hits=i["last_hits"],
                        denies=i["denies"],
                        gpm=i["gold_per_min"],
                        xpm=i["xp_per_min"],
                        level=i["level"],
                        hero_dmg=i.get("hero_damage"),
                        building_dmg=i.get("tower_damage"),
                        healing=i.get("hero_healing"),
                        networth=(i.get("gold_spent"),i.get("gold"))
                    )
                
            match = Dota_Match(
                id=data["match_id"],
                players=players,
                game_mode=data["game_mode"],
                duration=data["duration"],
                start_time=data["start_time"],
                radiant_win=data["radiant_win"],
                radiant_kills=data["radiant_score"],
                dire_kills=data["dire_score"],
                dire_team=dire_team_ids,
                radiant_team=radiant_team_ids
            )
            return match
        return None
    async def get_complete_account(self, steam_64id, hero_id=None, turbo_only=True):
        steam_32id = self.steam_64bit_id_to_32bit(steam_64id)
        match_history, new_matches = await self.get_dota_player_match_history(steam_32id, hero_id, 23 if turbo_only else None)
        steam_profile = await self.get_steam_profile(steam_64id)
        return (Complete_Account(steam_profile, match_history), new_matches)
