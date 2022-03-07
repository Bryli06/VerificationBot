import discord
import sqlite3
from discord.utils import get
from discord.ext import commands
conn = sqlite3.connect("Database.db")
cursor = conn.cursor()
cursor.execute('''
        CREATE TABLE IF NOT EXISTS new_member(
                message_id INTEGER,
                user_id INTEGER
        )
''')
cursor.execute('''
        CREATE TABLE IF NOT EXISTS nickname(
                user_id INTEGER,
                nick TEXT
        )
''')
TOKEN = ('')
intents = discord.Intents.all()
client = commands.Bot(command_prefix='.', intents=intents)
emoji = "✅"

@client.event
async def on_ready():
    print(f'Logged in as {client.user}.\n-----------')


@client.command(pass_context=True)
@commands.has_role('Atoms')
async def freeze(ctx, member: discord.Member,arg):
	sql="SELECT * FROM nickname WHERE user_id=?"
	cursor.execute(sql,[int(member.id)])
	data=cursor.fetchall()
	if data: 
		sql="UPDATE nickname SET nick=? WHERE user_id=?"
		cursor.execute(sql,[str(arg),int(member.id)])
	else: 
		sql="INSERT INTO nickname VALUES (?,?)"
		cursor.execute(sql,[int(member.id),str(arg)])
	await client.get_channel(877698301414223882).send(f'{ctx.author.mention} froze {member.mention}\'s name to {arg}')
	await member.edit(nick=arg)
@client.command(pass_context=True)
@commands.has_role('Atoms')
async def unfreeze(ctx, member: discord.Member):
	sql="SELECT * FROM nickname WHERE user_id=?"
	cursor.execute(sql,[int(member.id)])
	data=cursor.fetchall()
	if data:
		sql="DELETE FROM nickname WHERE user_id=?"
		cursor.execute(sql,[int(member.id)])
		await client.get_channel(877698301414223882).send(f'{ctx.member.author.mention} unfroze {member.mention}\'s name')
@client.event
async def on_member_join(member):
	channel=client.get_channel(879098868913037352) 
	embedV = discord.Embed(title="New Member!", description=f'Do you know {member.mention}?', color=0x00ff00)
	embedV.add_field(name="If so", value="please react with the checkmark", inline=False)
	print("member joined:" + member.name)
	message = await channel.send(embed=embedV)
	await message.add_reaction(emoji)
	sql = "insert into new_member values (?,?)"
	cursor.execute(sql,[int(message.id),int(member.id)])
	conn.commit()
@client.event
async def on_reaction_add(reaction,user):
	if user!=client.user:
		if str(reaction.emoji) == emoji:
			sql="SELECT * FROM new_member WHERE message_id=?"
			cursor.execute(sql,[int(reaction.message.id)])
			data=cursor.fetchall()
			if data:
				guild = reaction.message.guild
				usr=guild.get_member(int(data[0][1]))
				if usr:
					role=get(guild.roles, id=877411379286523935)
					await usr.add_roles(role)
					await client.get_channel(877698301414223882).send(f'{user.mention} verified {usr.mention}')
					sql="DELETE FROM new_member WHERE message_id=?"
					cursor.execute(sql,[int(reaction.message.id)])

@client.event
async def on_member_update(before, after):
	sql="SELECT * FROM nickname WHERE user_id=?"
	cursor.execute(sql,[int(after.id)])
	data=cursor.fetchall()
	if data and after.display_name != data[0][1]:
		await after.edit(nick=data[0][1])
client.run(TOKEN) #runs the bot
