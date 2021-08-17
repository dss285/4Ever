import psycopg2
import psycopg2.extras
import discord
from models.BotMention import BotMention
from models.UpdatedMessage import UpdatedMessage
from forever.Steam import Steam_API, Dota_Match, Dota_Match_Player
from forever.Utilities import run_in_executor, log
from forever.Warframe import CetusMessage, FissureMessage, SortieMessage, NightwaveMessage, InvasionMessage, SolSystem
from forever.Newswire import NewswireMessage

from models.Server import Server
from forever.Arknights import Formula, Item, Stage
from forever.GFL import Doll, Fairy
class Database:
	def __init__(self, host : str, user : str, password : str, database : str, client : discord.Client=None) -> None:
		self.host = host
		self.user = user
		self.password = password
		self.database = database
		self.shared = "shared"
		self.forever = "forever"
		self.tables = {
			"forever" : {
				'discord_images',
				'discord_servers',
				'discord_notifications',
				'discord_joinable_roles',
				'discord_role_messages',
				'discord_updated_messages',
			},
			"shared" : {
				"arknights_items",
				"arknights_stages",
				"arknights_formulas",
				"dota_heroes",
				"dota_matches",
				"dota_matches_players",
				'gfl_dolls',
				'gfl_equipment',
				'wf_builds',
				'wf_builds_images',
				'wf_items',
				'wf_missions',
				'wf_nightwave',
				'wf_solsystem_nodes',
				'wf_solsystem_planets',
				'wf_sorties'
			}
		}
		self.query_formats = {
			"delete_where" : 'DELETE FROM \"{schema}\".{table} WHERE {column}={value}',
			"delete_where_and" : 'DELETE FROM \"{schema}\".{table} WHERE {column_1}={value_1} AND {column_2}={value_2}',
			"delete_where_custom" : 'DELETE FROM \"{schema}\".{table} WHERE {custom}',
			"insert_into" : "INSERT INTO \"{schema}\".{table} ({columns}) VALUES ({values})"
		}
		self.connection = psycopg2.connect(host=self.host,
								  user=self.user,
								  password=self.password,
								  database=self.database,
								  port=5432)
	
	def query(self, sql : str) -> None:
		try:
			data = None
			with self.connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
				cursor.execute(sql)
				if "SELECT" in sql:
					data = cursor.fetchall()
			self.connection.commit()
			if data:
				return data
		except Exception as e:
			print(e)
			self.connection.rollback()
	def get_data(self,) -> dict[str, dict]:
		results = {}
		for i, j in self.tables.items():
			for x in j:
				results[x] = self.get_table_rows(f'\"{i}\".{x}')
		return results
	def get_table_rows(self, tabletype : str) -> dict:
		results = None
		with self.connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
			cursor.execute(f"SELECT * FROM {tabletype}")
			results = cursor.fetchall()
		self.connection.commit()
		return results
class DB_API(Database):
	def __init__(self, host :str, user:str, password:str, database:str, client) -> None:
		super().__init__(host, user, password, database)
		self.client = client
		self.runtime = {}
		self.saved_messages = set()
		self.mentions = []
		self.init_done = False
	def __getitem__(self, item):
		return self.runtime[item]
	def structure(self,) -> None:
		self.runtime["warframe"] = {}
		self.runtime["warframe"]["nightwave"] = []
		self.runtime["warframe"]["invasions"] = []
		self.runtime["warframe"]["sorties"] = None
		self.runtime["warframe"]["translate"] = {}
		self.runtime["warframe"]["translate"]["missions"] = {}
		self.runtime["warframe"]["translate"]["nightwave"] = {}
		self.runtime["warframe"]["translate"]["sorties"] = {}
		self.runtime["warframe"]["translate"]["items"] = {}
		self.runtime["warframe"]["translate"]["solsystem"] = {}
		self.runtime["warframe"]["translate"]["solsystem"]["planets"] = []
		self.runtime["warframe"]["translate"]["solsystem"]["nodes"] = []
		self.runtime["arknights"] = {}
		self.runtime["arknights"]["formulas"] = {}
		self.runtime["arknights"]["items"] = {}
		self.runtime["arknights"]["stages"] = {}
		self.runtime["arknights"]["items"]["ids"] = {}
		self.runtime["arknights"]["items"]["names"] = {}
		self.runtime["arknights"]["stages"]["ids"] = {}
		self.runtime["arknights"]["stages"]["codes"] = {}
		self.runtime["gfl"] = {}
		self.runtime["gfl"]["dolls"] = {}
		self.runtime["gfl"]["dolls"]["aliases"] = {}
		self.runtime["gfl"]["dolls"]["names"] = {}
		self.runtime["gfl"]["equipment"] = {}
		self.runtime["dota"] = {}
		self.runtime["droptables"] = {}
		self.runtime["servers"] = {}
	@run_in_executor
	def query(self, sql : str) -> None:
		return super().query(sql)
	@run_in_executor
	def get_data(self,) -> dict[str, dict]:
		return super().get_data()
	async def get_server(self, server_id, data : dict[str, dict]) -> None:
		log_id = next((i["logchannel_id"] for i in data["discord_servers"] if i["server_id"] == server_id), None)
		discord_server = self.client.get_guild(server_id)
		logchannel = self.client.get_channel(log_id) if log_id else None
		updated_messages = {}
		joinable_roles = set()
		role_messages = {}
		notifications = []
		for x in data["discord_role_messages"]:
			if x["server_id"] == server_id:
				channel = self.client.get_channel(x["channel_id"])
				message = None
				try:
					message = await channel.fetch_message(x["message_id"])
				except discord.NotFound:
					await self.delete_role_message(x["message_id"])
					await self.delete_updated_message(x["message_id"])
					continue
				if message:
					role_messages[message.id] = {
						"message" : message,
						"emoji" : x["emoji"],
						"role_id" : x["role_id"] 
					}
		for x in data["discord_joinable_roles"]:
			if x["server_id"] == server_id:
				role = discord_server.get_role(x["role_id"])
				if role:
					joinable_roles.add(role)
				else:
					await self.delete_joinable_role(x["role_id"])
		for x in data["discord_notifications"]:
			if x["server_id"] == server_id:
				role = discord_server.get_role(x["role_id"])
				if role:
					bot_mention = BotMention(x["notification_name"], role)
					notifications.append(bot_mention)
				else:
					await self.delete_notification(x["notification_name"], x["server_id"])
		for x in data["discord_updated_messages"]:
			if x["server_id"] == server_id:
				channel = self.client.get_channel(x["channel_id"])
				if channel:
					message = None
					try:
						message = await channel.fetch_message(x["message_id"])
					except discord.NotFound:
						await self.delete_role_message(x["message_id"])
						await self.delete_updated_message(x["message_id"])
						message = None
					if message:
						message_type = x["message_type"]
						if message_type == "nightwave":
							updated_messages[message_type] = NightwaveMessage(message)
						elif message_type == "invasions":
							updated_messages[message_type] = InvasionMessage(message, [])
						elif message_type == "fissures":
							updated_messages[message_type] = FissureMessage(message, [])
						elif message_type == "sorties":
							updated_messages[message_type] = SortieMessage(message)
						elif message_type == "poe":
							mention = next((i for i in notifications if i.name == "poe_night"), None)
							updated_messages[message_type] = CetusMessage(message, mention, self.client)
						elif message_type == "gtanw":
							updated_messages[message_type] = NewswireMessage(message)
		server = Server(server_id, discord_server, logchannel, updated_messages, notifications, joinable_roles, role_messages)
		self.runtime["servers"][server_id] = server
	async def update_runtime(self,) -> None:
		data = self.get_data()

		if "gfl" in self.runtime:
			self.gfl(data)
		if "warframe" in self.runtime:
			self.warframe(data)
		if "droptables" in self.runtime:
			self.droptables(data)
	def arknights(self, data : dict[str, dict]) -> None:
		formulas = data.get("arknights_formulas")
		stages = data.get("arknights_stages")
		items = data.get("arknights_items")
		for i in items:
			tmp = Item(i["id"], i["name"], i["description"], i["rarity"], i["icon_id"], i["usage"])
			tmp._stage_drop_list_str = i["stage_drop_list"]
			self.runtime["arknights"]["items"]["ids"][i["id"]] = tmp
			self.runtime["arknights"]["items"]["names"][tmp.name] = tmp
		for f in formulas:
			costs = []
			if f["costs"] != "":
				tmp = f["costs"].split(" ")
				for c in tmp:
					splitted = c.split("|")
					item_id = splitted[0]
					amount = splitted[1]
					costs.append({
						"item" : self.runtime["arknights"]["items"]["ids"][item_id],
						"amount" : amount
					})
			tmp = Formula(f["id"], self.runtime["arknights"]["items"]["ids"][f["item_id"]], f["count"], costs, f["room"])
			self.runtime["arknights"]["items"]["ids"][f["item_id"]].set_formula(tmp)
			self.runtime["arknights"]["formulas"][f"{f['id']}_{f['room']}"] = tmp
		for s in stages:
			drops = []
			if s["drops"] != "":
				tmp = s["drops"].split(" ")
				for x in tmp:
					splitted = x.split("|")
					itemid = splitted[0]
					droptype = splitted[1]
					occurence = splitted[2]
					item = self.runtime["arknights"]["items"].get(itemid)
					if item is None:
						item = itemid
					drops.append({
						"item" : item,
						"drop_type" : droptype,
						"occurence" : occurence
					})
			sta = Stage(s["id"], s["code"], s["name"], s["description"], s["sanity_cost"], drops)
			self.runtime["arknights"]["stages"]["ids"][s["id"]] = sta
			self.runtime["arknights"]["stages"]["codes"][sta.code] = sta
		for itemid, item in self.runtime["arknights"]["items"]["ids"].items():
			stage_drop_list = []
			if item._stage_drop_list_str not in ["", "-"]:
				tmp = item._stage_drop_list_str.split(" ")
				for i in tmp:
					splitted = i.split("|")
					stageid = splitted[0]
					occurence = splitted[1]
					stage = self.runtime["arknights"]["stages"]["ids"][stageid]
					stage_drop_list.append({
						"stage" : stage,
						"occurence" : occurence
					})
				item.set_stage_drop_list(stage_drop_list)
	
	def gfl(self, data : dict[str, dict]) -> None:
		for d in data["gfl_dolls"]:
			aliases = d["aliases"].split("|") if d["aliases"] else []
			doll = Doll(d["id"], d["name"], 
			d["type"], 
			d["rarity"], 
			d["formation_bonus"], 
			d["formation_tiles"],
			d["skill"],
			aliases,
			d["production_timer"])
			self.runtime["gfl"]["dolls"]["names"][d["name"].lower()] = doll
			for x in aliases:
				self.runtime["gfl"]["dolls"]["aliases"][x.lower()] = doll
	def warframe(self, data : dict[str, dict]) -> None:
		self.runtime["warframe"]["translate"]["solsystem"]["planets"].clear()
		self.runtime["warframe"]["translate"]["solsystem"]["nodes"].clear()
		for item in data["wf_missions"]:
			self.runtime["warframe"]["translate"]["missions"][item["code_name"]]    = item["name"]
		for item in data["wf_nightwave"]:
			self.runtime["warframe"]["translate"]["nightwave"][item["code_name"]]   = item["name"]
		for item in data["wf_sorties"]:
			self.runtime["warframe"]["translate"]["sorties"][item["code_name"]]     = item["name"]
		for item in data["wf_items"]:
			self.runtime["warframe"]["translate"]["items"][item["code_name"]]       = item["name"]
		for item in data["wf_solsystem_planets"]:
			self.runtime["warframe"]["translate"]["solsystem"]["planets"].append(SolSystem.SolPlanet(item["planet_id"], item["name"]))
		for item in data["wf_solsystem_nodes"]:
			self.runtime["warframe"]["translate"]["solsystem"]["nodes"].append(SolSystem.SolNode(item["node_id"], item["name"],
			next(planet for planet in self.runtime["warframe"]["translate"]["solsystem"]["planets"] if planet.id == item["planet_id"])))
	def dota(self, data : dict[str, dict]) -> None:
		match_players = {}
		dota_heroes = {"id" : {}, "name" : {}}
		for i in data["dota_heroes"]:
			dota_heroes["id"][i["id"]] = i["name"]
			dota_heroes["name"][i["name"]] = i["id"]
		for i in data["dota_matches_players"]:
			if i["match_id"] not in match_players:
				match_players[i["match_id"]] = {"players" : {"dire" : {}, "radiant" : {}}, "radiant_team_ids" : set(), "dire_team_ids" : set()}
			player_slot = i["player_slot"]
			if i["team"] == "dire":
				player_slot -= 128
				match_players[i["match_id"]]["dire_team_ids"].add(i["id"])
			elif i["team"] == "radiant":
				match_players[i["match_id"]]["radiant_team_ids"].add(i["id"])
			match_players[i["match_id"]]["players"][i["team"]][player_slot] = Dota_Match_Player(
						i["id"],
						i["player_slot"],
						i["hero_id"],
						i["kills"],
						i["deaths"],
						i["assists"],
						i["last_hits"],
						i["denies"],
						i["gpm"],
						i["xpm"],
						i["level"],
						i["hero_dmg"],
						i["building_dmg"],
						i["healing"],
						i["networth"]
					)
		for i in data["dota_matches"]:
			dire_team_ids = match_players[i["id"]]["dire_team_ids"]
			radiant_team_ids = match_players[i["id"]]["radiant_team_ids"]
			players = match_players[i["id"]]["players"]
			dota_match = Dota_Match(
				i["id"],
				players,
				i["game_mode"],
				i["duration"],
				i["start_time"],
				i["radiant_win"],
				i["radiant_kills"],
				i["dire_kills"],
				radiant_team_ids,
				dire_team_ids
			)
			Steam_API.cache.add(f"match_details_{dota_match.id}", dota_match)
		self.runtime["dota"]["heroes"] = dota_heroes
	def droptables(self, data : dict[str, dict]) -> None:
		return
		# for i in data['droptables']:
		#     if i['droptable_name'] not in self.runtime["droptables"]:
		#         self.runtime["droptables"][i["droptable_name"]] = DropTable()
		#     self.runtime["droptables"][i["droptable_name"]].add(i["weight"], i["item_name"])
	async def init_runtime(self,) -> None:
		self.structure()
		data = await self.get_data()
		#Server Translation
		for i in data["discord_servers"]:
			await self.get_server(i["server_id"], data)
		#GFL Translation
		self.gfl(data)
		#WF Translation
		self.warframe(data)
		#dota matches
		self.dota(data)
		#AK Translation
		self.arknights(data)
		self.init_done = True
	def delete_joinable_role(self, role_id : int) -> None:
		self.query(self.query_formats["delete_where"].format(
			schema=self.forever,
			table="discord_joinable_roles",
			column="role_id",
			value=role_id
		))
	async def delete_updated_message(self, message_id : int) -> None:
		await self.query(self.query_formats["delete_where"].format(
			schema=self.forever,
			table="discord_updated_messages",
			column="message_id",
			value=message_id
		))
	async def delete_role_message(self, message_id : int=None, role_id : int=None) -> None:
		query = None
		if message_id and role_id:
			query = self.query_formats["delete_where_and"].format(
				schema=self.forever,
				table="discord_role_messages",
				column_1="message_id",
				value_1=message_id,
				column_2="role_id",
				value_2=role_id
			)
		elif message_id:
			query = self.query_formats["delete_where"].format(
				schema=self.forever,
				table="discord_role_messages",
				column="message_id",
				value=message_id
			)
		elif role_id:
			query = self.query_formats["delete_where"].format(
				schema=self.forever,
				table="discord_role_messages",
				column="role_id",
				value=role_id
			)
		if query:
			await self.query(query)
	async def delete_notification(self, notification_name : str, server_id : int) -> None:
		await self.query(self.query_formats["delete_where_and"].format(
			schema=self.forever,
			table="discord_notifications",
			column_1="name",
			value_1=f"\"{notification_name}\"",
			column_2="server_id",
			value_2=server_id
		))
	async def delete_server(self, server_id : int) -> None:
		await self.query(self.query_formats["delete_where"].format(
			schema=self.forever,
			table="discord_servers",
			column="server_id",
			value=server_id
		))
	async def create_joinable_role(self, role_id : int, server_id : int) -> None:
		await self.query(self.query_formats["insert_into"].format(
			schema=self.forever,
			table="discord_joinable_roles",
			columns="role_id, server_id",
			values=f"{role_id}, {server_id}"
		))
	async def create_updated_message(self, server_id : int, message_type : str, channel_id : int, message_id : int) -> None:
		await self.query(self.query_formats["insert_into"].format(
			schema=self.forever,
			table="discord_updated_messages",
			columns="server_id, message_type, channel_id, message_id",
			values=f"{server_id}, \"{message_type}\", {channel_id}, {message_id}"
		))
	async def create_role_message(self, role_id : int, message_id : int, channel_id : int, emoji, server_id : int) -> None:
		await self.query(self.query_formats["insert_into"].format(
			schema=self.forever,
			table="discord_role_messages",
			columns="role_id, message_id, channel_id, emoji, server_id",
			values=f"{role_id}, {message_id}, {channel_id}, \"{emoji}\", {server_id}"
		))
	async def create_notification(self, notification_name : str, role_id : int, server_id : int) -> None:
		await self.query(self.query_formats["insert_into"].format(
			schema=self.forever,
			table="discord_notifications",
			columns="notification_name, role_id, server_id",
			values=f"\"{notification_name}\", {role_id}, {server_id}"
		))
	async def create_server(self, server_id : int) -> None:
		await self.query(self.query_formats["insert_into"].format(
			schema=self.forever,
			table="discord_servers",
			columns="server_id",
			values=f"{server_id}"
		))
	async def create_dota_match(self, dota_match : Dota_Match) -> None:
		query_match = self.query_formats["insert_into"]
		query_player = self.query_formats["insert_into"]
		query_match = query_match.format(
			schema=self.shared,
			table="dota_matches",
			columns="id, game_mode, start_time, radiant_win, radiant_kills, dire_kills,  duration",
			values=f"{dota_match.id}, {dota_match.game_mode}, {dota_match.start_time}, {dota_match.radiant_win}, {dota_match.radiant_kills}, {dota_match.dire_kills}, {dota_match.duration}"
		)
		await self.query(query_match)
		for team, players in dota_match.players.items():
			for player_slot, player in players.items():
				await self.query(
					query_player.format(
						schema=self.shared,
						table="dota_matches_players",
						columns="id, match_id, player_slot, hero_id, kills, deaths, assists, last_hits, denies, gpm, xpm, level, hero_dmg, building_dmg, healing, networth, team",
						values="{}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, '{}'".format(
							player.id or "null",
							dota_match.id,
							player.player_slot,
							player.hero_id,
							player.kills,
							player.deaths,
							player.assists,
							player.last_hits,
							player.denies,
							player.gpm,
							player.xpm,
							player.level,
							player.hero_dmg or "null",
							player.building_dmg or "null",
							player.healing or "null",
							player.networth or "null",
							team
						)
					)
				)