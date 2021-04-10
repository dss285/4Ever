import psycopg2
import psycopg2.extras
import discord
from models.BotMention import BotMention
from models.UpdatedMessage import UpdatedMessage
from warframe.CetusMessage import CetusMessage
from warframe.FissureMessage import FissureMessage
from warframe.SortieMessage import SortieMessage
from warframe.NightwaveMessage import NightwaveMessage
from warframe.InvasionMessage import InvasionMessage
from forever.NewswireMessage import NewswireMessage

from warframe.SolNode import SolNode
from warframe.SolPlanet import SolPlanet
from forever.Server import Server
from gfl.Doll import Doll
class Database:
    def __init__(self, host, user, password, database):
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
    def query(self, sql):
        with self.connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            cursor.execute(sql)
        self.connection.commit()
    def get_data(self,):
        results = {}
        for i, j in self.tables.items():
            for x in j:
                results[x] = self.get_table_rows('\"{}\".{}'.format(i, x))
        return results
    def get_table_rows(self, tabletype):
        results = None
        with self.connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            cursor.execute("SELECT * FROM {}".format(tabletype))
            results = cursor.fetchall()
        self.connection.commit()
        return results
class Database_Manager(Database):
    def __init__(self, host, user, password, database):
        super().__init__(host, user, password, database)
        self.runtime = {}
        self.saved_messages = set()
        self.mentions = []
    def structure(self,):
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
        self.runtime["gfl"] = {}
        self.runtime["gfl"]["dolls"] = []
        self.runtime["gfl"]["equipment"] = []
        self.runtime["servers"] = {}
    async def get_server(self, server_id, data, client):
        log_id = next((i["logchannel_id"] for i in data["discord_servers"] if i["server_id"] == server_id), None)
        discord_server = client.get_guild(server_id)
        logchannel = client.get_channel(log_id) if log_id else None
        updated_messages = {}
        joinable_roles = set()
        role_messages = {}
        notifications = []
        for x in data["discord_role_messages"]:
            if x["server_id"] == server_id:
                channel = client.get_channel(x["channel_id"])
                message = None
                try:
                    message = await channel.fetch_message(x["message_id"])
                except discord.NotFound:
                    self.delete_role_message(x["message_id"])
                    self.delete_updated_message(x["message_id"])
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
                    self.delete_joinable_role(x["role_id"])
        # for x in data["discord_notifications"]:
            # print("asd")
            # if x["server_id"] == server_id:
                # role = discord_server.get_role(x["role_id"])
                # if role:
                    # print("ok11")
                    # print(role)
                    # bot_mention = BotMention(x["name"], role)
                    # print("ok22")
                    # notifications.append(bot_mention)
                    # print("ok33")
                # else:
                    # print("ok")
                    # self.delete_notification(x["name"], x["server_id"])
        if not updated_messages:
            for x in data["discord_updated_messages"]:
                if x["server_id"] == server_id:
                    channel = client.get_channel(x["channel_id"])
                    if channel:
                        message = None
                        try:
                            message = await channel.fetch_message(x["message_id"])
                        except discord.NotFound:
                            self.delete_role_message(x["message_id"])
                            self.delete_updated_message(x["message_id"])
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
                                updated_messages[message_type] = CetusMessage(message, mention, client)
                            elif message_type == "gtanw":
                                updated_messages[message_type] = NewswireMessage(message)
        server = Server(server_id, discord_server, logchannel, updated_messages, notifications, joinable_roles, role_messages)
        self.runtime["servers"][server_id] = server
    async def update_runtime(self, client):
        data = self.get_data()

        if "gfl" in self.runtime:
            self.gfl(data)
        if "warframe" in self.runtime:
            self.warframe(data)
    def gfl(self, data):
        self.runtime["gfl"]["dolls"].clear()
        self.runtime["gfl"]["equipment"].clear()
        for d in data["gfl_dolls"]:
            doll = Doll(d["id"], d["name"], 
            d["type"], 
            d["rarity"], 
            d["formation_bonus"], 
            d["formation_tiles"],
            d["skill"],
            d["aliases"].split("|") if d["aliases"] else [],
            d["productiontimer"])
            self.runtime["gfl"]["dolls"].append(doll)
    def warframe(self, data):
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
            self.runtime["warframe"]["translate"]["solsystem"]["planets"].append(SolPlanet(item["planet_id"], item["name"]))
        for item in data["wf_solsystem_nodes"]:
            self.runtime["warframe"]["translate"]["solsystem"]["nodes"].append(SolNode(item["node_id"], item["name"],
            next(planet for planet in self.runtime["warframe"]["translate"]["solsystem"]["planets"] if planet.id == item["planet_id"])))
    async def init_runtime(self, client):
        self.structure()
        data = self.get_data()
        #Server Translation
        for i in data["discord_servers"]:
            await self.get_server(i["server_id"], data, client)
        #GFL Translation
        self.gfl(data)
        #WF Translation
        self.warframe(data)
    def delete_joinable_role(self, role_id):
        self.query(self.query_formats["delete_where"].format(
            schema=self.forever,
            table="discord_joinable_roles",
            column="role_id",
            value=role_id
        ))
    def delete_updated_message(self, message_id):
        self.query(self.query_formats["delete_where"].format(
            schema=self.forever,
            table="discord_updated_messages",
            column="message_id",
            value=message_id
        ))
    def delete_role_message(self, message_id=None, role_id=None):
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
            self.query(query)
    def delete_notification(self, notification_name, server_id):
        self.query(self.query_formats["delete_where_and"].format(
            schema=self.forever,
            table="discord_notifications",
            column_1="name",
            value_1="\"{}\"".format(name),
            column_2="server_id",
            value_2=server_id
        ))
    def delete_server(self, server_id):
        self.query(self.query_formats["delete_where"].format(
            schema=self.forever,
            table="discord_servers",
            column="server_id",
            value=server_id
        ))
    def create_joinable_role(self, role_id, server_id):
        self.query(self.query_formats["insert_into"].format(
            schema=self.forever,
            table="discord_joinable_roles",
            columns="role_id, server_id",
            values="{}, {}".format(role_id, server_id)
        ))
    def create_updated_message(self, server_id, message_type, channel_id, message_id):
        self.query(self.query_formats["insert_into"].format(
            schema=self.forever,
            table="discord_updated_messages",
            columns="server_id, message_type, channel_id, message_id",
            values="{}, \"{}\", {}, {}".format(server_id, message_type, channel_id, message_id)
        ))
    def create_role_message(self, role_id, message_id, channel_id, emoji, server_id):
        self.query(self.query_formats["insert_into"].format(
            schema=self.forever,
            table="discord_role_messages",
            columns="role_id, message_id, channel_id, emoji, server_id",
            values="{}, {}, {}, \"{}\", {}".format(role_id, message_id, channel_id, emoji, server_id)
        ))
    def create_notification(self, notification_name, role_id, server_id):
        self.query(self.query_formats["insert_into"].format(
            schema=self.forever,
            table="discord_notifications",
            columns="notification_name, role_id, server_id",
            values="\"{}\", {}, {}".format(notification_name, role_id, server_id)
        ))
    def create_server(self, server_id):
        self.query(self.query_formats["insert_into"].format(
            schema=self.forever,
            table="discord_servers",
            columns="server_id",
            values="{}".format(server_id)
        ))

if __name__ == "__main__":
    db = Database("localhost", "dss285", "aeon123", "aeon")
