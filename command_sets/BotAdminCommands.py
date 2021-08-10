import asyncio
from forever.Database import DB_API
from models.Server import Server
import discord
from models.EmbedTemplate import EmbedTemplate
from models.Commands import Commands, Command
from forever.Utilities import Args
import subprocess
import re

class BotAdminCommands(Commands):
    def __init__(self, module_name : str, description : str, command_key : str, client : discord.Client, database : DB_API):

        self.client = client
        self.database = database
        command_list = self.fetch_commands(command_key)
        super().__init__(module_name, command_list, description, command_key)

    def fetch_commands(self, command_key):
        command_list = {}
        command_list["eval"] = EvalCommand(command_key, self.client)
        command_list["shell"] = ShellCommand(command_key, self.client)
        command_list["createtable"] = CreateTable(command_key, self.client, self.database)
        command_list["dbquery"] = DBQuery(command_key, self.database)
        return command_list
    async def parse(self, message, server):
        if message.author.id == 132166600513159168:
            await super().parse(message, server)
class ShellCommand(Command):
    def __init__(self, command_key, client):
        self.client = client
        super().__init__(command_key, "shell", """Shell""", f"{command_key} shell *shell command*", ['bash', 'sh'])
        self.args = Args(shell=Args.ANY_ARG)
        self.args.set_pattern(command_key, self.aliases)
    async def run(self, message, server):
        parse = self.args.parse(message.content)
        if parse:
            splitted = parse["shell"].split(" ")
            output = subprocess.run(splitted, stdout=subprocess.PIPE, text=True, universal_newlines=True)
            if output.returncode == 0:
                if len(output.stdout) < 1975:
                    await message.reply(f"""```{output.stdout}```""")
                else:
                    fo = open("tmp.txt", "w+")
                    fo.write(output.stdout)
                    fo.close()
                    await message.reply(file=discord.File("tmp.txt"))
            else:
                await message.reply(f"Error from shell command: {output.stderr}")
class EvalCommand(Command):
    def __init__(self, command_key : str, client : discord.Client) -> None:
        self.client = client
        super().__init__(command_key, "eval", """Eval""", f"{command_key} eval *evaled statement*", ['ev'])
        self.args = Args(shell=Args.ANY_ARG)
        self.args.set_pattern(command_key, self.aliases)
    async def run(self, message : discord.Message, server : Server) -> None:
        parse = self.args.parse(message.content)
        if parse:
            output = str(eval(parse["shell"]))
            if len(output) < 1975:
                await message.reply(f"""```{output}```""")
            else:
                fo = open("tmp.txt", "w+")
                fo.write(output)
                fo.close()
                await message.reply(file=discord.File("tmp.txt"))
class CreateTable(Command):
    def __init__(self, command_key, client : discord.Client, database : DB_API):
        self.database = database
        self.client = client
        super().__init__(command_key, "createtable", """Create table""", f"{command_key} createtable *tablename*", [])
        self.args = Args(table_name=Args.STRING_ARG)
        self.args.set_pattern(command_key, self.aliases)
    
    async def run(self, message : discord.Message, server : Server) -> None:
        def check_author(m : discord.Message):
            if message.author == m.author:
                return True
            return False
        parse = self.args.parse(message.content)
        if parse:
            table_name = parse['table_name']
            i = 1
            columns = []
            while True:
                em = EmbedTemplate(title=f"Column {i}", description=f"syntax: \*column name\*:\*column type\*:\*extra detail\*\nExtra detail is for example, PRIMARY, not null etc.\nType 'END;' to stop")
                em.add_field(name="Data types", value="https://www.postgresql.org/docs/9.5/datatype.html")
                await message.channel.send(embed=em)
                msg = await self.client.wait_for('message', timeout=120.0, check=check_author)
                if msg:
                    content = msg.content
                    if content == 'END;':
                        break
                    splitted = content.split(":")
                    merged = f"{' '.join(splitted)}"
                    columns.append(merged)
                    i+= 1
                else:
                    break
            if columns:
                nl = ',\n'
                query = f"CREATE TABLE {table_name} IF NOT EXISTS (\n{f'{nl}'.join(columns)}\n);"
                sql = f"```sql\n{query}\n```"
                await message.channel.send(sql)
                await message.channel.send("Is this ok ? Y for Yes, anything for No")
                msg = await self.client.wait_for('message', timeout=60.0)
                if msg:
                    if "y" in msg.content.lower():
                        await self.database.query(query)
class DBQuery(Command):
    def __init__(self, command_key : str, database : DB_API):
        self.database = database
        super().__init__(command_key, "dbquery", """Query to DB""", f"{command_key} dbquery *query*", ["query"])
        self.args = Args(query=Args.ANY_ARG)
        self.args.set_pattern(command_key, self.aliases)
    async def run(self, message : discord.Message, server : Server) -> None:
        parse = self.args.parse(message.content)
        if parse:
            qr = parse['query']
            data = await self.database.query(qr)
            await message.channel.send(f"{data}")
