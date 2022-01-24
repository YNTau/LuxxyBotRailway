import discord
from discord import Embed
from discord.ext import commands, tasks
from discord.ext.commands import cooldown, BucketType
from discord.ui import Button, View
import json
import os
import random
import time
import asyncio
import requests
import datetime
from prsaw import RandomStuffV2
import DiscordUtils
import asyncpg

def get_prefix(client,message):

    try:
        with open("prefixes.json", "r") as f:
            prefixes = json.load(f)         
        prefix = prefixes[str(message.guild.id)] 
        return prefixes[str(message.guild.id)]
    except:
        return "L "

client = commands.Bot(
    command_prefix = get_prefix,
    intents = discord.Intents.all())

rs = RandomStuffV2(async_mode = True)
client.remove_command("help")

curbank = None 
curarmor = None
curbot = None
curuse = None

async def create_db_pool():
    client.db = await asyncpg.create_pool(dsn = 'postgres://poxcpmeahxczjc:f9a51337d9bf1d5e13fc273a1c45b96e833508d64f4aea38b48feb3bd802ef38@ec2-3-216-113-109.compute-1.amazonaws.com:5432/d4n95ut8m970sc')
    print("Succes connek")
    await client.db.execute('CREATE TABLE IF NOT EXISTS database(index serial NOT NULL PRIMARY KEY, mainbank json NOT NULL, armor json NOT NULL, chatbot json NOT NULL, used json NOT NULL)')
    database = await client.db.fetch('SELECT * FROM database')
    if not database:
        await client.db.execute('INSERT INTO database(mainbank,armor,chatbot,used) VALUES ($1,$1,$1,$1)', '{}')

@client.event
async def on_ready():
    await client.change_presence(activity = discord.Game("Mention if you forget prefix"))
    maindata = await client.db.fetchrow('SELECT mainbank FROM database WHERE index = $1', 1)
    maindata = maindata[0]
    maindata = json.loads(maindata)
    armor = await client.db.fetchrow('SELECT armor FROM database WHERE index = $1', 1)
    armor = armor[0]
    armor = json.loads(armor)    
    chatbot = await client.db.fetchrow('SELECT chatbot FROM database WHERE index = $1', 1)
    chatbot = chatbot[0]
    chatbot = json.loads(chatbot)        
    used = await client.db.fetchrow('SELECT used FROM database WHERE index = $1', 1)
    used = used[0]
    used = json.loads(used)            
    users = await get_bank_data()
    users = maindata
    with open("mainbank.json","w") as f:
        json.dump(users,f,indent=4)
    with open("armor.json","r") as f:
        armors = json.load(f)
    armors = armor
    with open("armor.json","w") as f:
        json.dump(armors,f,indent=4)
    with open("chatbot.json","r") as f:
        chatbots = json.load(f)
    chatbots = chatbot
    with open("chatbot.json","w") as f:
        json.dump(chatbots,f,indent=4)        
    with open("used.json","r") as f:
        useds = json.load(f)
    useds = used
    with open("used.json","w") as f:
        json.dump(useds,f,indent=4)                
    try:
        for user in users:
            users[user]["proseskerja"] = 0
            users[user]["prosesrampok"] = 0
            users[user]["prosespenjara"] = 0
            users[user]["prosesngemis"] = 0
            with open("mainbank.json","w") as f:
                json.dump(users,f,indent=4)
    except:
        pass

    staminaup.start()
    print("Looped Stamina Refill")
    loadboost.start()
    print("Looped Load Boost")
    loadbank.start()
    print("Ready")
     
@tasks.loop(seconds=1)
async def loadbank():
    global curbank
    global curarmor
    global curbot
    global curuse
    with open("mainbank.json","r") as f:
        allbank = json.load(f)
    with open("armor.json","r") as f:
        allarmor = json.load(f)
    with open("chatbot.json","r") as f:
        allbot = json.load(f)
    with open("used.json","r") as f:
        alluse = json.load(f)        
    channel = client.get_channel(933980105959686155)
    allbank = json.dumps(allbank, indent=4)
    if curbank != allbank:    
        await channel.send(f"""File : mainbank.json
{allbank}""")
        curbank = allbank
        allbank = json.loads(allbank)
        allbank = json.dumps(allbank)
        await client.db.execute('UPDATE database SET mainbank = $1 WHERE "index" = $2', str(allbank), 1)
    allarmor = json.dumps(allarmor, indent=4)
    if curarmor != allarmor:
        await channel.send(f"""File : armor.json
{allarmor}""")
        curarmor = allarmor
        allarmor = json.loads(allarmor)
        allarmor = json.dumps(allarmor)
        await client.db.execute('UPDATE database SET armor = $1 WHERE "index" = $2', str(allarmor), 1)
    allbot = json.dumps(allbot, indent=4)
    if curbot != allbot:     
        await channel.send(f"""File : chatbot.json
{allbot}""")
        curbot = allbot
        allbot = json.loads(allbot)
        allbot = json.dumps(allbot)
        await client.db.execute('UPDATE database SET chatbot = $1 WHERE "index" = $2', str(allbot), 1)
    alluse = json.dumps(alluse, indent=4)
    if curuse != alluse:     
        await channel.send(f"""File : used.json
{alluse}""")
        curuse = alluse
        alluse= json.loads(alluse)
        alluse = json.dumps(alluse)
        await client.db.execute('UPDATE database SET used = $1 WHERE "index" = $2', str(alluse), 1)
    return  

@client.event
async def on_message(msg):            
    try:    
        if msg.mentions[0] == client.user:       
            with open("prefixes.json", "r") as f:
                prefixes = json.load(f)       
            prefix = prefixes[str(msg.guild.id)]
            await msg.channel.send(f"""My prefix in this server is `{prefix}`
Example : `{prefix}help`""")
    except:
        pass
 
    if client.user == msg.author:
        return

    await open_data(msg.guild)
    with open("chatbot.json", "r") as f:
        data = json.load(f)
    chnya = data[str(msg.guild.id)]["channelid"]
    if msg.channel.id == chnya:  
        mode = data[str(msg.guild.id)]["mode"]
        if mode == 1:
            response = await rs.get_ai_response(msg.content)
            await msg.reply(response["message"])
            
    await client.process_commands(msg)
            
@client.event
async def on_guild_join(guild):

    with open("prefixes.json", "r") as f:
        prefixes = json.load(f)

    prefixes[str(guild.id)] = "L "

    with open("prefixes.json", "w") as f:
        json.dump(prefixes,f,indent=4)

with open("allshop.json","r") as f:
    allshop = json.load(f)

@client.command(aliases = ['lottery','gamble'], description = "Command for slot lottery", category = "Economy")
@commands.cooldown(1, 120, commands.BucketType.user)
async def slot(ctx):
    emorupiah = discord.utils.get(client.emojis, id=926314665884156004)
    emodamage = discord.utils.get(client.emojis, id=926314853658951720)
    emohealth = discord.utils.get(client.emojis, id=926321297972133909)
    emostamina = discord.utils.get(client.emojis, id=926313999346335744)
    emoexp = discord.utils.get(client.emojis, id=922433918613991465)
    emolevel = discord.utils.get(client.emojis, id=922439376552734820)
    emoticket = discord.utils.get(client.emojis, id=926314047614361690)
    await open_account(ctx.author)
    users = await get_bank_data()
    user = ctx.author
    if users[str(user.id)]["prosesbattle"] == 1:
        await ctx.send(f"You are now in battle")
        return
    proseskerja = users[str(user.id)]["proseskerja"]
    if proseskerja==1:
        await ctx.send(f"You are working, wait until it's finished")
        return
    proseshack = users[str(user.id)]["prosesrampok"]
    if proseshack==1:
        await ctx.send(f"You're robbing a bank, wait until it's over")
        return
    prosespenjara = users[str(user.id)]["prosespenjara"]
    if prosespenjara==1:
        await ctx.send(f"You are in prison, wait until you are released")
        return
    prosesngemis = users[str(user.id)]["prosesngemis"]
    if prosesngemis==1:
        await ctx.send(f"You are begging, wait until it's finished")
        return
    
    bal = await update_bank(ctx.author)
    
    if 1>bal[2]:
        await ctx.reply("You don't have a ticket")
        return

    final = []
    for i in range(3):
        a = random.choice(["🍌","🍊","💵"])        
        final.append(a)
    bfinal = " ".join(final)
    await ctx.reply(bfinal)

    if final[0] == final[1] or final[0] == final[2] or final[2] == final[1]:        
        menang = random.randrange(80, 100)
        await update_bank(ctx.author,+menang*1, "wallet")
        await update_bank(ctx.author,-1*1,"ticket")
        await ctx.reply(f"You win, you get {emorupiah}{menang}.")
        print(final)
    else:
        dapetexp = random.randrange(20)
        await update_bank(ctx.author,+dapetexp*1, "exp")
        await update_bank(ctx.author,-1*1,"ticket")
        await ctx.reply(f"You lose, you get {dapetexp} {emoexp}exp.")
        print(final)
    await uplevel(ctx)

@client.command(aliases = ['botchat'], description = "ChatBot command, setchannel ( mention the channel you want to set ), on, off", category = "Config")
@commands.has_permissions(administrator = True)
@commands.cooldown(1, 3, commands.BucketType.guild)
async def chatbot(ctx, option, channel:discord.TextChannel = None):
    await open_data(ctx.guild)
    with open("chatbot.json", "r") as f:
        data = json.load(f)
        
    if option == "on":
        channelid = data[str(ctx.guild.id)]["channelid"]
        if channelid == 0:
            await ctx.send("The chat bot channel on this server has not been set yet")
            return
        await ctx.send("Chat bot has been successfully enabled")
        data[str(ctx.guild.id)]["mode"] = 1
        with open("chatbot.json","w") as f:
            json.dump(data,f,indent=4)
        return
        
    if option == "off":
        channelid = data[str(ctx.guild.id)]["channelid"]
        if channelid == 0:
            await ctx.send("The chat bot channel on this server has not been set yet")
            return
        await ctx.send("Chat bot has been successfully disabled")
        data[str(ctx.guild.id)]["mode"] = 0
        with open("chatbot.json","w") as f:
            json.dump(data,f,indent=4)
        return
    if option == "setchannel" or option == "changechannel":
        if channel == None:
            await ctx.send("Mention the channel you want to set as a chat bot channel.")
            return
        await ctx.send(f"Channel **{channel.name}** has been successfully set as chat bot channel")
        data[str(ctx.guild.id)]["channelid"] = channel.id
        with open("chatbot.json","w") as f:
            json.dump(data,f,indent=4)
        return       
    else:
        await ctx.send("Invalid, setchannel to set Chat bot channel, on or off to enable or disable the Chat bot on this server.")
        return

@client.command(description = "Help Command & List Command")
@commands.cooldown(1, 5, commands.BucketType.user)
async def help(ctx, command=None):
    try:
        with open("prefixes.json", "r") as f:
            prefixes = json.load(f)         
        prefix = prefixes[str(ctx.guild.id)] 
    except:
        prefix = "L "
    if command == None:
        em = discord.Embed(title="Command", color = discord.Color.blue())
        em.add_field(name = "Economy", value = "balance, bag, beg, work, bankrob, battle, fight, buy, sell, upgrade, evolve, shop, deposit, withdraw, transfer, equip, unequip, eat, slot, equipment, leaderboard")
        em.add_field(name = "Fun", value = "meme")
        em.add_field(name = "Config", value = "setprefix, chatbot")
        em.set_footer(text=f"{prefix}help <command> to see more detail.")
        em.set_thumbnail(url=client.user.avatar.url)
        await ctx.send(embed = em)
        return
    em = discord.Embed(title="Command", color = discord.Color.blue())
    name_ = None
    command = command.lower()
    for commands in client.walk_commands():
        name = commands.name
        if name.lower() == command:
            name_ = name.lower
            description = commands.description     
            aliases = commands.aliases
            signature = commands.signature        
            if aliases == []:
                aliases = ''
            aliases = ", ".join(aliases)
            if aliases != '':
                aliases = f"| alias = {aliases}"
            if not description or description is None or description == "":
                description = 'No description'
            em.add_field(name=f"`{prefix}{name} {signature if signature is not None else ''} {aliases}`", value=f"`{description}`", inline = False)
            break
    if name_ == None:
        await ctx.send(f"Command {command} not found")
        return
    em.set_thumbnail(url=client.user.avatar.url)
    await ctx.send(embed=em)

@client.command(aliases = ['changeprefix','gantiprefix'], description = "command to change the server prefix (don't forget the new prefix)", category = "Config")
@commands.cooldown(1, 5, commands.BucketType.guild)
@commands.has_permissions(administrator = True)
async def setprefix(ctx, prefix=None):

    if prefix == None:
        await ctx.send(f"New prefix can't empty!")
        return

    with open("prefixes.json", "r") as f:
        prefixes = json.load(f)

    prefixes[str(ctx.guild.id)] = prefix

    with open("prefixes.json", "w") as f:
        json.dump(prefixes,f,indent=4)    

    await ctx.send(f"This server prefix changed to {prefix}")


@client.command(aliases = ['memes'], description = "Command to get memes from reddit", category = "Config")
@commands.cooldown(1, 3, commands.BucketType.user)
async def meme(ctx,meme="meme"):
    meme = meme.lower()
    r = requests.get(f"https://meme-api.herokuapp.com/gimme/{meme}?sort=new")
    res = r.json()
    title = res["title"]
    ups = res["ups"]
    sub = res["subreddit"]
    em = discord.Embed(title = f"{title}, {sub}", color = discord.Color.red())
    em.set_image(url=res["url"])
    em.set_footer(text = f"👍{ups}")
    await ctx.send(embed = em)

class BView(View):
    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx
        self.value = None

    @discord.ui.button(label="Iya", style=discord.ButtonStyle.green, custom_id="iya")
    async def button_callback(self, button, interaction):
        iya = [x for x in self.children if x.custom_id=="iya"][0]
        iya.disabled = True
        tidak = [x for x in self.children if x.custom_id=="tidak"][0]
        tidak.disabled = True
        await interaction.response.edit_message(view=self)
        users = await get_bank_data()
        if users[str(self.ctx.author.id)]["prosesbattle"] == 1:
            return
        await lawan(self.ctx)
        self.stop()        

    @discord.ui.button(label="Tidak", style=discord.ButtonStyle.danger, custom_id="tidak")
    async def tidak_button_callback(self, button, interaction):
        tidak = [x for x in self.children if x.custom_id=="tidak"][0]
        tidak.disabled = True
        iya = [x for x in self.children if x.custom_id=="iya"][0]
        iya.disabled = True
        await interaction.response.edit_message(view=self)
        self.stop()

    async def interaction_check(self, interaction) -> bool:
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("Don't touch other people's buttons", ephemeral=True)
            return False
        else:
            return True

@client.command(aliases = ['duel'], description = "Fight command, can place bets (optional)", category = "Economy")
@commands.cooldown(1, 5, commands.BucketType.user)
async def fight(ctx, member:discord.Member, bet=None):
    if bet == 0:
        bet = None
    emorupiah = discord.utils.get(client.emojis, id=926314665884156004)
    emodamage = discord.utils.get(client.emojis, id=926314853658951720)
    emohealth = discord.utils.get(client.emojis, id=926321297972133909)
    emostamina = discord.utils.get(client.emojis, id=926313999346335744)
    emoexp = discord.utils.get(client.emojis, id=922433918613991465)
    emospeed = discord.utils.get(client.emojis, id=926312716086439946)
    await open_account(ctx.author)
    await open_account(member)    
    await open_armor(ctx.author)
    await open_armor(member)    
    users = await get_bank_data()
    user = ctx.author

    bal = await update_bank(ctx.author)

    if member == ctx.author:
        await ctx.send(f"Wow that member is you, you wanna fight with yourself?")
        return
    if users[str(user.id)]["prosesbattle"] == 1:
        await ctx.send(f"You are now in battle")
        return
    if users[str(member.id)]["prosesbattle"] == 1:
        await ctx.send(f"{member.name} are now in battle")
        return
    if bet != None:
        bet = int(bet)
        duit = users[str(user.id)]["wallet"]
        if int(duit) < bet:
            await ctx.send(f"Your money is less than bet")  
            return  
        duit = users[str(member.id)]["wallet"]
        if int(duit) < bet:
            await ctx.send(f"{member.name} money is less than bet")  
            return              
    en = member.name

    buttons = ["👍","👎"]
    betst = ""
    if bet != None:
        betst = f" with bet {bet}"
    msg = await ctx.send(f"<@{member.id}>, do you want to fight with {user.name}{betst}?")    
    for button in buttons:
        await msg.add_reaction(button)      
    while True:
        try:
            reaction, user = await client.wait_for("reaction_add", check=lambda reaction, user: user == member and reaction.emoji in buttons, timeout=60.0)
        except asyncio.TimeoutError:
            return
        else:
            
            if reaction.emoji == "👍":
                await flawan(ctx, member, bet)              
                return            
            elif reaction.emoji == "👎":
                await msg.delete()
                return    
    
async def flawan(ctx, member, bet):
    emorupiah = discord.utils.get(client.emojis, id=926314665884156004)
    emodamage = discord.utils.get(client.emojis, id=926314853658951720)
    emohealth = discord.utils.get(client.emojis, id=926321297972133909)
    emostamina = discord.utils.get(client.emojis, id=926313999346335744)
    emoexp = discord.utils.get(client.emojis, id=922433918613991465)
    emospeed = discord.utils.get(client.emojis, id=926312716086439946)
    emoshield = discord.utils.get(client.emojis, id=927094233419104286)    
    await open_account(ctx.author)
    users = await get_bank_data()
    user = ctx.author
    eim = member.avatar.url
    en = member.name
    ehp = users[str(member.id)]["health"]
    etk = users[str(member.id)]["damage"]
    esp = users[str(member.id)]["speed"]
    usp = users[str(user.id)]["speed"]
    uhp = users[str(user.id)]["health"]
    users[str(user.id)]["prosesbattle"] = 1
    users[str(member.id)]["prosesbattle"] = 1
    users[str(user.id)]["buhp"] = int(uhp)
    users[str(user.id)]["betk"] = int(etk)
    users[str(user.id)]["behp"] = int(ehp)
    users[str(user.id)]["besp"] = int(esp)
    with open("mainbank.json","w") as f:
        json.dump(users,f,indent=4)
 
    if esp > usp:
        em = discord.Embed(title = f"{en} VS {user.name}", color = discord.Color.red())
        em.add_field(name = f"{user.name} Health{emohealth} :", value = f"{uhp}")
        em.add_field(name = f"{en} Health{emohealth} :", value = f"{ehp}")
        em.add_field(name = f"Attack History :", value = f"{emospeed}Speed ​​*{en}* is faster and has a turn to attack.")
        em.set_image(url=eim)
        em.set_thumbnail(url=user.avatar.url)
        msg = await ctx.send(embed = em)
        await asyncio.sleep(5)
        await feronde(ctx, msg, member, bet)        
        
    if usp >= esp:
        print("C")
        em = discord.Embed(title = f"{en} VS {user.name}", color = discord.Color.red())
        em.add_field(name = f"{user.name} Health{emohealth} :", value = f"{uhp}")
        em.add_field(name = f"{en} Health{emohealth} :", value = f"{ehp}")
        em.add_field(name = f"Attack History :", value = f"{emospeed}Speed ​​*{user.name}* is faster and has a turn to attack.")
        em.set_image(url=eim)
        em.set_thumbnail(url=user.avatar.url)
        msg = await ctx.send(embed = em)
        await asyncio.sleep(5)
        await furonde(ctx, msg, member, bet)
        
async def feronde(ctx, msg, member, bet):
    emorupiah = discord.utils.get(client.emojis, id=926314665884156004)
    emodamage = discord.utils.get(client.emojis, id=926314853658951720)
    emohealth = discord.utils.get(client.emojis, id=926321297972133909)
    emostamina = discord.utils.get(client.emojis, id=926313999346335744)
    emoexp = discord.utils.get(client.emojis, id=922433918613991465)
    await open_account(ctx.author)
    users = await get_bank_data()
    user = ctx.author
    eim = member.avatar.url
    en = member.name
    ehp = users[str(member.id)]["health"]
    etk = users[str(member.id)]["damage"]
    esp = users[str(member.id)]["speed"]
    uhp = users[str(user.id)]["health"]
    ush = users[str(user.id)]["shield"]
    utk = users[str(user.id)]["damage"]
    usp = users[str(user.id)]["speed"]
    buhp = users[str(user.id)]["buhp"]
    betk = users[str(user.id)]["betk"]
    behp = users[str(user.id)]["behp"]
    besp = users[str(user.id)]["besp"]

    etk = int(etk)
    leatk = 0.8 * etk
    leatk = int(leatk)
    reatk = random.randrange(leatk, etk)
    if reatk > uhp:
         reatk = uhp
    users[str(user.id)]["health"] -= reatk
    with open("mainbank.json","w") as f:
        json.dump(users,f,indent=4)
    users = await get_bank_data()
    ehp = users[str(member.id)]["health"]
    uhp = users[str(user.id)]["health"]
    em = discord.Embed(title = f"{en} VS {user.name}", color = discord.Color.red())
    em.add_field(name = f"{user.name} Health{emohealth} :", value = f"{uhp}")
    em.add_field(name = f"{en} Health{emohealth} :", value = f"{ehp}")
    em.set_image(url=eim)
    em.set_thumbnail(url=user.avatar.url)
    em.add_field(name = f"Attack History :", value = f"{en} attacks {user.name} and deals {emodamage}{reatk} damage!")
    msg = await msg.edit(embed = em)
    await asyncio.sleep(4)
    if uhp < 1:   
        users[str(user.id)]["health"] = buhp
        users[str(member.id)]["health"] = behp
        betst = ""    
        if bet != None:
            betst = f", get {bet} from bet"
            users[str(member.id)]["wallet"] += bet
            users[str(user.id)]["wallet"] -= bet
        await ctx.send(f"Congratulations, {member.name} you won the match{betst}")       
        users[str(user.id)]["prosesbattle"] = 0
        users[str(member.id)]["prosesbattle"] = 0
        with open("mainbank.json","w") as f:
            json.dump(users,f,indent=4)
        return
    await furonde(ctx, msg, member, bet)
            
async def furonde(ctx, msg, member, bet):
    emorupiah = discord.utils.get(client.emojis, id=926314665884156004)
    emodamage = discord.utils.get(client.emojis, id=926314853658951720)
    emohealth = discord.utils.get(client.emojis, id=926321297972133909)
    emostamina = discord.utils.get(client.emojis, id=926313999346335744)
    emoexp = discord.utils.get(client.emojis, id=922433918613991465)
    await open_account(ctx.author)
    users = await get_bank_data()
    user = ctx.author
    eim = member.avatar.url
    en = member.name
    ehp = users[str(member.id)]["health"]
    etk = users[str(member.id)]["damage"]
    esp = users[str(member.id)]["speed"]
    uhp = users[str(user.id)]["health"]
    utk = users[str(user.id)]["damage"]
    usp = users[str(user.id)]["speed"]
    buhp = users[str(user.id)]["buhp"]
    betk = users[str(user.id)]["betk"]
    behp = users[str(user.id)]["behp"]
    besp = users[str(user.id)]["besp"]
    
    utk = int(utk)
    luatk = 0.8 * utk
    luatk = int(luatk)
    ruatk = random.randrange(luatk, utk)
    if ruatk > int(ehp):
         ruatk = int(ehp)
    users[str(member.id)]["health"] -= ruatk
    with open("mainbank.json","w") as f:
        json.dump(users,f,indent=4)
    users = await get_bank_data()
    ehp = users[str(member.id)]["health"]
    uhp = users[str(user.id)]["health"]
    em = discord.Embed(title = f"{en} VS {user.name}", color = discord.Color.red())
    em.add_field(name = f"{user.name} Health{emohealth} :", value = f"{uhp}")
    em.add_field(name = f"{en} Health{emohealth} :", value = f"{ehp}")
    em.set_image(url=eim)
    em.set_thumbnail(url=user.avatar.url)
    em.add_field(name = f"Attack History :", value = f"{user.name} attacks {en} and deals {emodamage}{ruatk} damage!")
    msg = await msg.edit(embed = em)
    await asyncio.sleep(4)
    if ehp < 1:           
        users[str(member.id)]["health"] = behp
        users[str(user.id)]["health"] = buhp
        betst = ""    
        if bet != None:
            betst = f", get {bet} from bet"
            users[str(user.id)]["wallet"] += bet
            users[str(member.id)]["wallet"] -= bet
        await ctx.send(f"Congratulations, {user.name} you won the match{betst}")       
        users[str(user.id)]["prosesbattle"] = 0
        users[str(member.id)]["prosesbattle"] = 0
        with open("mainbank.json","w") as f:
            json.dump(users,f,indent=4)
        return
    await feronde(ctx, msg, member, bet)
    await uplevel(ctx)

@client.command(aliases = ['bt'], description = "Battle command", category = "Economy")
@commands.cooldown(1, 5, commands.BucketType.user)
async def battle(ctx):
    emorupiah = discord.utils.get(client.emojis, id=926314665884156004)
    emodamage = discord.utils.get(client.emojis, id=926314853658951720)
    emohealth = discord.utils.get(client.emojis, id=926321297972133909)
    emostamina = discord.utils.get(client.emojis, id=926313999346335744)
    emoexp = discord.utils.get(client.emojis, id=922433918613991465)
    emospeed = discord.utils.get(client.emojis, id=926312716086439946)
    await open_account(ctx.author)
    await open_armor(ctx.author)
    users = await get_bank_data()
    user = ctx.author

    bal = await update_bank(ctx.author)
    polisi = await update_bank(ctx.author)

    if users[str(user.id)]["prosesbattle"] == 1:
        await ctx.send(f"You are now in battle")
        return
    stam = users[str(user.id)]["stamina"]
    if stam < 10:
        await ctx.send(f"Your stamina must be more than 10 to battle")    
        return
    duit = users[str(user.id)]["wallet"]
    if duit < 0:
        await ctx.send(f"Pay your debt first before the battle")  
        return  
    proseskerja = users[str(user.id)]["proseskerja"]
    if proseskerja==1:
        await ctx.send(f"You are working, wait until it's finished")
        return
    proseshack = users[str(user.id)]["prosesrampok"]
    if proseshack==1:
        await ctx.send(f"You're robbing a bank, wait until it's over")
        return
    prosespenjara = users[str(user.id)]["prosespenjara"]
    if prosespenjara==1:
        await ctx.send(f"You are in prison, wait until you are released")
        return

    prosesngemis = users[str(user.id)]["prosesngemis"]
    if prosesngemis==1:
        await ctx.send(f"You are begging, wait until it's finished")
        return         

    enemy = [
    {"name":"Rick Astley","url":"https://i.ibb.co/4jxch05/20220105-144211.png"},
    {"name":"Amogus","url":"https://c.tenor.com/PNPcRrIeLkwAAAAC/youtooz-among-us.gif"},
    {"name":"Rock","url":"https://i.ibb.co/dLtc2TX/images-7.jpg"},
    {"name":"John Cena","url":"https://i.ibb.co/2SMfKtr/20220105-150605.png"},
    {"name":"Mr Incredible","url":"https://i.ibb.co/6vzDztp/20220105-145054.png"},
    {"name":"Snotty Boy","url":"https://i.ibb.co/5v6gz35/20220105-150147.png"}
    ]
    
    enemd = random.choice(enemy)
    en = enemd["name"]
    eim = enemd["url"]
    
    users[str(user.id)]["enemyname"] = en
    users[str(user.id)]["enemyimg"] = eim
    with open("mainbank.json","w") as f:
        json.dump(users,f,indent=4)

    en = users[str(user.id)]["enemyname"]
    ehp = users[str(user.id)]["enemyhp"]
    etk = users[str(user.id)]["enemytk"]
    esp = users[str(user.id)]["enemysp"]    
    
    em = discord.Embed(title = en, color = discord.Color.red())
    em.add_field(name = f"Enemy {emohealth}Health", value = f"Health : {ehp}")
    em.add_field(name = f"Enemy {emodamage}Damage", value = f"Damage : {etk}")
    em.add_field(name = f"Enemy {emospeed}Speed", value = f"Speed : {esp}")
    em.set_thumbnail(url=user.avatar.url)
    em.set_image(url=eim)
    await ctx.send(embed = em)

    view = BView(ctx)
    await ctx.send(f"Do you want to fight {en}?", view = view)
    
async def lawan(ctx):
    emorupiah = discord.utils.get(client.emojis, id=926314665884156004)
    emodamage = discord.utils.get(client.emojis, id=926314853658951720)
    emohealth = discord.utils.get(client.emojis, id=926321297972133909)
    emostamina = discord.utils.get(client.emojis, id=926313999346335744)
    emoexp = discord.utils.get(client.emojis, id=922433918613991465)
    emospeed = discord.utils.get(client.emojis, id=926312716086439946)
    emoshield = discord.utils.get(client.emojis, id=927094233419104286)    
    await open_account(ctx.author)
    users = await get_bank_data()
    user = ctx.author
    eim = users[str(user.id)]["enemyimg"]
    en = users[str(user.id)]["enemyname"]
    esp = users[str(user.id)]["enemysp"]
    etk = users[str(user.id)]["enemytk"]    
    usp = users[str(user.id)]["speed"]
    ehp = users[str(user.id)]["enemyhp"]    
    uhp = users[str(user.id)]["health"]
    users[str(user.id)]["prosesbattle"] = 1
    users[str(user.id)]["buhp"] = int(uhp)
    users[str(user.id)]["betk"] = int(etk)
    users[str(user.id)]["behp"] = int(ehp)
    users[str(user.id)]["besp"] = int(esp)
    with open("mainbank.json","w") as f:
        json.dump(users,f,indent=4)
        
    if esp > usp:
        em = discord.Embed(title = f"{en} VS {user.name}", color = discord.Color.red())
        em.add_field(name = f"{en} Health{emohealth} :", value = f"{ehp}")
        em.add_field(name = f"{user.name} Health{emohealth} :", value = f"{uhp}")
        em.add_field(name = f"Attack History :", value = f"{emospeed}Speed ​​*{en}* is faster and has a turn to attack.")
        em.set_image(url=eim)
        em.set_thumbnail(url=user.avatar.url)
        msg = await ctx.send(embed = em)
        await asyncio.sleep(5)
        await eronde(ctx, msg)        
        
    if usp >= esp:
        em = discord.Embed(title = f"{en} VS {user.name}", color = discord.Color.red())
        em.add_field(name = f"{en} Health{emohealth} :", value = f"{ehp}")
        em.add_field(name = f"{user.name} Health{emohealth} :", value = f"{uhp}")
        em.add_field(name = f"Attack History :", value = f"{emospeed}Speed ​​*{user.name}* is faster and has a turn to attack.")
        em.set_image(url=eim)
        em.set_thumbnail(url=user.avatar.url)
        msg = await ctx.send(embed = em)
        await asyncio.sleep(5)
        await uronde(ctx, msg)
        
async def eronde(ctx, msg):
    emorupiah = discord.utils.get(client.emojis, id=926314665884156004)
    emodamage = discord.utils.get(client.emojis, id=926314853658951720)
    emohealth = discord.utils.get(client.emojis, id=926321297972133909)
    emostamina = discord.utils.get(client.emojis, id=926313999346335744)
    emoexp = discord.utils.get(client.emojis, id=922433918613991465)
    await open_account(ctx.author)
    users = await get_bank_data()
    user = ctx.author
    eim = users[str(user.id)]["enemyimg"]
    en = users[str(user.id)]["enemyname"]
    ehp = users[str(user.id)]["enemyhp"]
    esh = users[str(user.id)]["enemysh"]
    etk = users[str(user.id)]["enemytk"]
    esp = users[str(user.id)]["enemysp"]
    uhp = users[str(user.id)]["health"]
    ush = users[str(user.id)]["shield"]
    utk = users[str(user.id)]["damage"]
    usp = users[str(user.id)]["speed"]
    buhp = users[str(user.id)]["buhp"]
    betk = users[str(user.id)]["betk"]
    behp = users[str(user.id)]["behp"]
    besp = users[str(user.id)]["besp"]

    etk = int(etk)
    leatk = 0.8 * etk
    leatk = int(leatk)
    reatk = random.randrange(leatk, etk)
    if reatk > uhp:
         reatk = uhp
    users[str(user.id)]["health"] -= reatk
    with open("mainbank.json","w") as f:
        json.dump(users,f,indent=4)
    users = await get_bank_data()
    ehp = users[str(user.id)]["enemyhp"]
    uhp = users[str(user.id)]["health"]
    em = discord.Embed(title = f"{en} VS {user.name}", color = discord.Color.red())
    em.add_field(name = f"{en} Health{emohealth} :", value = f"{ehp}")
    em.add_field(name = f"{user.name} Health{emohealth} :", value = f"{uhp}")
    em.set_image(url=eim)
    em.set_thumbnail(url=user.avatar.url)
    em.add_field(name = f"Attack History :", value = f"{en} attacks {user.name} and deals {emodamage}{reatk} damage!")
    msg = await msg.edit(embed = em)
    await asyncio.sleep(4)
    if uhp < 1:
        expd = random.randrange(10, 20)
        if users[str(user.id)]["expboost"] == 1:
            expd = expd * 2
        expd = int(expd)
        em = discord.Embed(title = f"{user.name}, you lost the match", description = f"{emostamina}stamina -10 | {emoexp}exp +{expd}")      
        await ctx.send(embed = em)
        await asyncio.sleep(2)
        await ctx.send(f"**{ctx.author.name}** dying and losing unconscious, you wake up in the hospital and pay the treatment fee of {emorupiah}200")
        users[str(user.id)]["wallet"] -= 200
        mh = users[str(user.id)]["maxhealth"]
        mh = int(mh)
        users[str(user.id)]["health"] = mh
        users[str(user.id)]["prosesbattle"] = 0
        users[str(user.id)]["enemyhp"] = behp
        users[str(user.id)]["enemytk"] = betk
        users[str(user.id)]["enemysp"] = besp
        users[str(user.id)]["stamina"] -= 10
        users[str(user.id)]["exp"] += expd
        with open("mainbank.json","w") as f:
            json.dump(users,f,indent=4)
        await uplevel(ctx)
        return
    await uronde(ctx, msg)   
            
async def uronde(ctx, msg):
    emorupiah = discord.utils.get(client.emojis, id=926314665884156004)
    emodamage = discord.utils.get(client.emojis, id=926314853658951720)
    emohealth = discord.utils.get(client.emojis, id=926321297972133909)
    emostamina = discord.utils.get(client.emojis, id=926313999346335744)
    emoexp = discord.utils.get(client.emojis, id=922433918613991465)
    await open_account(ctx.author)
    users = await get_bank_data()
    user = ctx.author
    eim = users[str(user.id)]["enemyimg"]
    en = users[str(user.id)]["enemyname"]
    ehp = users[str(user.id)]["enemyhp"]
    esh = users[str(user.id)]["enemysh"]
    etk = users[str(user.id)]["enemytk"]
    esp = users[str(user.id)]["enemysp"]
    uhp = users[str(user.id)]["health"]
    ush = users[str(user.id)]["shield"]
    utk = users[str(user.id)]["damage"]
    usp = users[str(user.id)]["speed"]
    buhp = users[str(user.id)]["buhp"]
    betk = users[str(user.id)]["betk"]
    behp = users[str(user.id)]["behp"]
    besp = users[str(user.id)]["besp"]
    
    utk = int(utk)
    luatk = 0.8 * utk
    luatk = int(luatk)
    ruatk = random.randrange(luatk, utk)
    if ruatk > int(ehp):
         ruatk = int(ehp)
    users[str(user.id)]["enemyhp"] -= ruatk
    with open("mainbank.json","w") as f:
        json.dump(users,f,indent=4)
    users = await get_bank_data()
    ehp = users[str(user.id)]["enemyhp"]
    uhp = users[str(user.id)]["health"]
    em = discord.Embed(title = f"{en} VS {user.name}", color = discord.Color.red())
    em.add_field(name = f"{en} Health{emohealth} :", value = f"{ehp}")
    em.add_field(name = f"{user.name} Health{emohealth} :", value = f"{uhp}")
    em.set_image(url=eim)
    em.set_thumbnail(url=user.avatar.url)
    em.add_field(name = f"Attack History :", value = f"{user.name} attacks {en} and deals {emodamage}{ruatk} damage!")
    msg = await msg.edit(embed = em)
    await asyncio.sleep(4)
    if ehp < 1:           
        expd = random.randrange(20, 30)
        if users[str(user.id)]["expboost"] == 1:
            expd = expd * 2
        expd = int(expd)
        earnings = int(users[str(user.id)]["floor"]) * 100
        earnings = int(earnings) + 100
        em = discord.Embed(title = f"Congratulations, {user.name} you won the match", description = f"{emorupiah}Wallet balance +{earnings} | {emostamina}stamina -10 | {emoexp}exp +{expd}")
        await ctx.send(embed = em)
        users[str(user.id)]["prosesbattle"] = 0
        users[str(user.id)]["stamina"] -= 10
        users[str(user.id)]["exp"] += expd
        users[str(user.id)]["wallet"] += earnings
        behp = int(behp) * 1.2
        betk = int(betk) * 1.2
        besp = int(besp) * 1.2
        behp = int(behp)
        betk = int(betk)
        besp = int(besp)
        users[str(user.id)]["floor"] += 1
        users[str(user.id)]["enemyhp"] = behp
        users[str(user.id)]["enemytk"] = betk
        users[str(user.id)]["enemysp"] = besp
        with open("mainbank.json","w") as f:
            json.dump(users,f,indent=4)
        await uplevel(ctx)
        return
    await eronde(ctx, msg)
    
@client.command(aliases = ['pakai','pasang'], description = "Use this command to equip armor or sword", category = "Economy")
async def equip(ctx,item_id):
    user = ctx.author
    await open_armor(user)
    await open_account(user)
    users = await get_bank_data()
    try:
        item_id = int(item_id)
    except:
        await ctx.send(f"You need to use item id.")
        return
    if users[str(user.id)]["prosesbattle"] == 1:
        await ctx.send(f"You are now in battle")
        return
    proseskerja = users[str(user.id)]["proseskerja"]
    if proseskerja==1:
        await ctx.send(f"You are working, wait until it's finished")
        return
    proseshack = users[str(user.id)]["prosesrampok"]
    if proseshack==1:
        await ctx.send(f"You're robbing a bank, wait until it's over")
        return
    prosespenjara = users[str(user.id)]["prosespenjara"]
    if prosespenjara==1:
        await ctx.send(f"You are in prison, wait until you are released")
        return

    prosesngemis = users[str(user.id)]["prosesngemis"]
    if prosesngemis==1:
        await ctx.send(f"You are begging, wait until it's finished")
        return

    name_ = None
    try:
        bag = users[str(user.id)]["bag"]
    except:
        bag = []
    for item in bag:
        name = item["item"].lower()
        nid = item["id"]
        if nid == item_id:
            name_ = name
            category = item["kategori"]
            break

    if name_ == None:
        await ctx.send(f"You don't have item with id {item_id}.")
        return
        
    if category == "food":
        await ctx.send(f"Bruh, you can't equip food")
        return

    if category == "boost":
        await ctx.send(f"Exp booster to be used, not to equip")
        return

    if category == "sword":
        res = await equip_sword(ctx.author,item_id)

        if not res[0]:
            if res[1]==1:
                await ctx.send(f"You're equipping other armor.")
                return
            if res[1]==2:
                await ctx.send(f"You don't have 1 {name.capitalize()} in your bag")
                return
            if res[1]==3:
                await ctx.send(f"You don't have {name.capitalize()} in your bag")
                return
        
    if category == "armor":
        res = await equip_armor(ctx.author,item_id)

        if not res[0]:
            if res[1]==1:
                await ctx.send(f"You're equipping other armor.")
                return
            if res[1]==2:
                await ctx.send(f"You don't have 1 {name.capitalize()} in your bag")
                return
            if res[1]==3:
                await ctx.send(f"You don't have {name.capitalize()} in your bag")
                return

    await ctx.send(f"You equip {name.capitalize()}.")

async def equip_sword(user,item_name):
    await open_armor(user)
    await open_account(user)
    users = await get_bank_data()
    name_ = None
    try:
        bag = users[str(user.id)]["bag"]
    except:
        bag = []
    for item in bag:
        name = item["item"].lower()
        nid = item["id"]
        if nid == item_name:
            damage = item["damage"]
            name_ = name
            break

    users = await get_armor_data()
    sword = users[str(user.id)]["sword"]

    if sword != "nothing":
        return [False,1]

    bal = await update_bank(user)
    users = await get_bank_data()
    
    try:
        index = 0
        t = None
        for thing in users[str(user.id)]["bag"]:
            n = thing["id"]
            if n == item_name:
                old_amt = thing["amount"]
                new_amt = old_amt - 1
                if new_amt < 0:
                    return [False,2]
                users[str(user.id)]["bag"][index]["amount"] = new_amt
                t = 1
                break
            index+=1 
        if t == None:
            return [False,3]
    except:
        return [False,3]    

    with open("mainbank.json","w") as f:
        json.dump(users,f,indent=4)
    users = await get_armor_data()
    users[str(user.id)]["sword"] = item_name
    users[str(user.id)]["dmgsword"] = damage
    with open("armor.json","w") as f:
        json.dump(users,f,indent=4)
    users = await get_bank_data()
    users[str(user.id)]["damage"] += damage
    with open("mainbank.json","w") as f:
        json.dump(users,f,indent=4)

    return [True,"Worked"]
    
async def equip_armor(user,item_name):
    await open_armor(user)
    await open_account(user)
    users = await get_bank_data()
    name_ = None
    try:
        bag = users[str(user.id)]["bag"]
    except:
        bag = []
    for item in bag:
        name = item["item"].lower()
        nid = item["id"]
        if nid == item_name:
            speed = item["speed"]
            bagian = item["bagian"]
            bonushp = item["bonushp"]
            name_ = name
            break

    users = await get_armor_data()
    armor = users[str(user.id)][bagian]

    bal = await update_bank(user)
    
    if armor != "nothing":
        return [False,1]

    users = await get_bank_data()
    
    try:
        index = 0
        t = None
        for thing in users[str(user.id)]["bag"]:
            n = thing["id"]
            if n == item_name:
                old_amt = thing["amount"]
                new_amt = old_amt - 1
                if new_amt < 0:
                    return [False,2]
                users[str(user.id)]["bag"][index]["amount"] = new_amt
                t = 1
                break
            index+=1 
        if t == None:
            return [False,3]
    except:
        return [False,3]    

    with open("mainbank.json","w") as f:
        json.dump(users,f,indent=4)
    users = await get_armor_data()
    users[str(user.id)][bagian] = item_name
    users[str(user.id)][f"hp{bagian}"] = bonushp
    with open("armor.json","w") as f:
        json.dump(users,f,indent=4)
    users = await get_bank_data()
    users[str(user.id)]["speed"] += speed
    users[str(user.id)]["maxhealth"] += bonushp
    with open("mainbank.json","w") as f:
        json.dump(users,f,indent=4)

    return [True,"Worked"]    

@client.command(aliases = ['lepas'], description = "Command to unequip the armor that you use", category = "Economy")
async def unequip(ctx,item_id):
    user = ctx.author
    await open_armor(user)
    await open_account(user)
    users = await get_bank_data()
    try:
        item_id = int(item_id)
    except:
        await ctx.send(f"You need to use item id.")
        return
    if users[str(user.id)]["prosesbattle"] == 1:
        await ctx.send(f"You are now in battle")
        return
    proseskerja = users[str(user.id)]["proseskerja"]
    if proseskerja==1:
        await ctx.send(f"You are working, wait until it's finished")
        return
    proseshack = users[str(user.id)]["prosesrampok"]
    if proseshack==1:
        await ctx.send(f"You're robbing a bank, wait until it's over")
        return
    prosespenjara = users[str(user.id)]["prosespenjara"]
    if prosespenjara==1:
        await ctx.send(f"You are in prison, wait until you are released")
        return

    prosesngemis = users[str(user.id)]["prosesngemis"]
    if prosesngemis==1:
        await ctx.send(f"You are begging, wait until it's finished")
        return

    try:
        bag = users[str(user.id)]["bag"]
    except:
        bag = []
    name_ = None
    for item in bag:
        name = item["item"].lower()
        nid = item["id"]
        if nid == item_id:
            category = item["kategori"]
            name_ = name
            break

    if name_ == None:
        await ctx.send(f"You are not using item with id {item_id}.")
        return

    if category == "food":
        await ctx.send(f"You are not using item with id {item_id}.")
        return

    if category == "sword":
        res = await unequip_sword(ctx.author,item_id)

        if not res[0]:
            if res[1]==1:
                await ctx.send(f"You are not using {name.capitalize()}.")
                return
        
    if category == "armor":
        res = await unequip_armor(ctx.author,item_id)

        if not res[0]:
            if res[1]==1:
                await ctx.send(f"You are not using {name.capitalize()}.")
                return

    await ctx.send(f"You unequip {name.capitalize()}.")

async def unequip_sword(user,item_name):
    users = await get_bank_data()
    name_ = None
    try:
        bag = users[str(user.id)]["bag"]
    except:
        bag = []
    for item in bag:
        name = item["item"].lower()
        nid = item["id"]
        if nid == item_name:
            name_ = name
            price = item["price"]
            damage = item["damage"]
            kategori = item["kategori"]
            break
        
    users = await get_armor_data()
    sword = users[str(user.id)]["sword"]
    if sword != name.lower():
        return [False,1]
                    
    users = await get_bank_data()       
    bal = await update_bank(user)            
            
    try:
        index = 0
        t = None
        for thing in users[str(user.id)]["bag"]:
            n = thing["id"]
            if n == item_name:
                old_amt = thing["amount"]
                new_amt = old_amt + 1
                users[str(user.id)]["bag"][index]["amount"] = new_amt
                t = 1
                break
            index+=1
        if t == None:
            obj = {"item":item_name , "amount" : 1 , "damage":damage, "price":price, "kategori":kategori}
            users[str(user.id)]["bag"].append(obj)
    except:
        obj = {"item":item_name , "amount" : 1 , "damage":damage, "price":price, "kategori":kategori}
        users[str(user.id)]["bag"] = [obj]

    with open("mainbank.json","w") as f:
        json.dump(users,f,indent=4)
    users = await get_armor_data()
    users[str(user.id)]["sword"] = "nothing"
    users[str(user.id)]["dmgsword"] = 0
    with open("armor.json","w") as f:
        json.dump(users,f,indent=4)
                       
    users = await get_bank_data()
    users[str(user.id)]["damage"] -= damage
    with open("mainbank.json","w") as f:
        json.dump(users,f,indent=4)      
             
    return [True,"Worked"]
    
async def unequip_armor(user,item_name):
    users = await get_bank_data()
    name_ = None
    try:
        bag = users[str(user.id)]["bag"]
    except:
        bag = []
    for item in bag:
        name = item["item"].lower()
        nid = item["id"]
        if nid == item_name:
            name_ = name
            speed = item["speed"]
            bagian = item["bagian"]
            bonushp = item["bonushp"]
            price = item["price"]
            kategori = item["kategori"]
            break

    users = await get_armor_data()
    equip = users[str(user.id)][bagian]
    if equip != name.lower():
        return [False,1]
                    
    users = await get_bank_data()       
    bal = await update_bank(user)            
            
    try:
        index = 0
        t = None
        for thing in users[str(user.id)]["bag"]:
            n = thing["id"]
            if n == item_name:
                old_amt = thing["amount"]
                new_amt = old_amt + 1
                users[str(user.id)]["bag"][index]["amount"] = new_amt
                t = 1
                break
            index+=1
        if t == None:
            obj = {"item":item_name , "amount" : amount , "bagian":bagian , "bonushp":bonushp, "price":price, "kategori":kategori}
            users[str(user.id)]["bag"].append(obj)
    except:
        obj = obj = {"item":item_name , "amount" : amount , "bagian":bagian , "bonushp":bonushp, "price":price, "kategori":kategori}
        users[str(user.id)]["bag"] = [obj]

    with open("mainbank.json","w") as f:
        json.dump(users,f,indent=4)
    users = await get_armor_data()
    users[str(user.id)][category] = "nothing"
    users[str(user.id)][f"hp{category}"] = 0
    with open("armor.json","w") as f:
        json.dump(users,f,indent=4)                       
    users = await get_bank_data()
    users[str(user.id)]["speed"] -= speed
    users[str(user.id)]["maxhealth"] -= bonushp
    with open("mainbank.json","w") as f:
        json.dump(users,f,indent=4)      
    users = await get_bank_data()
    if users[str(user.id)]["maxhealth"] < users[str(user.id)]["health"]:
        users[str(user.id)]["health"] = int(users[str(user.id)]["maxhealth"])
        with open("mainbank.json","w") as f:
            json.dump(users,f,indent=4)      
    return [True,"Worked"]

@client.command(aliases = ['armor','sword','avatar','eq','perlengkapan'], description = "Check your equipment using this command", category = "Economy")
async def equipment(ctx, user:discord.Member = None):
    emodamage = discord.utils.get(client.emojis, id=926314853658951720)
    emohealth = discord.utils.get(client.emojis, id=926321297972133909)
    emospeed = discord.utils.get(client.emojis, id=926312716086439946)
    if user == None:
        user = ctx.author
    await open_armor(user)
    await open_account(user)    
    users = await get_armor_data()   
    helmet = users[str(user.id)]["helmets"]
    vest = users[str(user.id)]["vest"]
    legging = users[str(user.id)]["leggings"]
    boot = users[str(user.id)]["boots"]
    sword = users[str(user.id)]["sword"]    
    hph = users[str(user.id)]["hphelmets"]
    hpc = users[str(user.id)]["hpvest"]
    hpl = users[str(user.id)]["hpleggings"]
    hpb = users[str(user.id)]["hpboots"]
    dsword = users[str(user.id)]["dmgsword"]
    thp = int(hph)+int(hpc)+int(hpl)+int(hpb)
    users = await get_bank_data()
    speedb = users[str(user.id)]["speed"]
    speedb = int(speedb) - 50
    
    em = discord.Embed(title = f"**Equipment {user.name}**",color = discord.Color.red())
    em.add_field(name = f"**Helmet**",value = f"{helmet}, Max {emohealth}HP +{hph}")
    em.add_field(name = f"**Vest**",value = f"{vest}, Max {emohealth}HP +{hpc}")
    em.add_field(name = f"**Leggings**",value = f"{legging}, Max {emohealth}HP +{hpl}")
    em.add_field(name = f"**Boots**",value = f"{boot}, Max {emohealth}HP +{hpb}, Speed {emospeed}+{speedb}")
    em.add_field(name = f"**Sword**", value = f"{sword}, Damage +{dsword}")
    await ctx.send(embed = em)
    
@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"Slow bro, this command is on cooldown, try again in {error.retry_after:.2f} sec.")
        return
    raise error

@tasks.loop(seconds=100)
async def staminaup():
    users = await get_bank_data()
    try:
        for user in users:
            name = int(user)
            if users[user]["stamina"] >= users[user]["mstamina"]:
                return
            users[user]["stamina"] += 1
            with open("mainbank.json","w") as f:
                json.dump(users,f,indent=4)
    except:
        pass
    
@client.command(aliases = ['duit','bal','info','uang'], description = "Check your account information", category = "Economy")
async def balance(ctx, user:discord.Member = None):
    emorupiah = discord.utils.get(client.emojis, id=926314665884156004)
    emodamage = discord.utils.get(client.emojis, id=926314853658951720)
    emohealth = discord.utils.get(client.emojis, id=926321297972133909)
    emostamina = discord.utils.get(client.emojis, id=926313999346335744)
    emoexp = discord.utils.get(client.emojis, id=922433918613991465)
    emolevel = discord.utils.get(client.emojis, id=922439376552734820)
    emoticket = discord.utils.get(client.emojis, id=926314047614361690)
    emospeed = discord.utils.get(client.emojis, id=926312716086439946)    
    if user == None:
        user = ctx.author
    await open_account(user)        
    users = await get_bank_data()    
    dompet = users[str(user.id)]["wallet"]
    bank = users[str(user.id)]["bank"]
    tiket = users[str(user.id)]["ticket"]
    stamina = users[str(user.id)]["stamina"]
    mstam = users[str(user.id)]["mstamina"]
    exp = users[str(user.id)]["exp"]
    mexp = users[str(user.id)]["mexp"]
    level = users[str(user.id)]["level"]
    health = users[str(user.id)]["health"]
    mhealth = users[str(user.id)]["maxhealth"]
    damage = users[str(user.id)]["damage"]
    speed = users[str(user.id)]["speed"]       
    
    em = discord.Embed(title = f"**{user.name}** Account Information",color = discord.Color.red())
    em.add_field(name = f"{emorupiah}Wallet",value = dompet)
    em.add_field(name = f"{emorupiah}Bank",value = bank)
    em.add_field(name = f"{emoticket}Ticket",value = tiket)
    em.add_field(name = f"{emohealth}Health",value = f"{health} / {mhealth}")
    em.add_field(name = f"{emodamage}Damage",value = f"{damage}")
    em.add_field(name = f"{emospeed}Speed",value = f"{speed}")
    em.add_field(name = f"{emolevel}Level",value = f"{level}")
    em.add_field(name = f"{emoexp}Exp",value = f"{exp} / {mexp}")
    em.add_field(name = f"{emostamina}Stamina",value = f"{stamina} / {mstam}")
    if users[str(user.id)]["expboost"] == 1:
        if users[str(user.id)]["timeboost"] != 0:
            rtime = int(users[str(user.id)]["timeboost"])
            em.add_field(name = f"{emoexp}EXP Boost 2X", value = f"`Remaining time : {rtime} second`")
    await ctx.send(embed = em)

@client.command(aliases = ['ngemis'], description = "Beg command to earn wallet", category = "Economy")
@commands.cooldown(1, 5, commands.BucketType.user)
async def beg(ctx):
    emorupiah = discord.utils.get(client.emojis, id=926314665884156004)
    emodamage = discord.utils.get(client.emojis, id=926314853658951720)
    emohealth = discord.utils.get(client.emojis, id=926321297972133909)
    emostamina = discord.utils.get(client.emojis, id=926313999346335744)
    emoexp = discord.utils.get(client.emojis, id=922433918613991465)
    emolevel = discord.utils.get(client.emojis, id=922439376552734820)
    emoticket = discord.utils.get(client.emojis, id=926314047614361690)
    await open_account(ctx.author)
    user = ctx.author
    users = await get_bank_data()
    polisi = await update_bank(ctx.author)
    bal = await update_bank(ctx.author)

    if users[str(user.id)]["prosesbattle"] == 1:
        await ctx.send(f"You are now in battle")
        return

    proseskerja = users[str(user.id)]["proseskerja"]
    if proseskerja==1:
        await ctx.send(f"You are working, wait until it's finished")
        return
    proseshack = users[str(user.id)]["prosesrampok"]
    if proseshack==1:
        await ctx.send(f"You're robbing a bank, wait until it's over")
        return
    prosespenjara = users[str(user.id)]["prosespenjara"]
    if prosespenjara==1:
        await ctx.send(f"You are in prison, wait until you are released")
        return
    prosesngemis = users[str(user.id)]["prosesngemis"]
    if prosesngemis==1:
        await ctx.send(f"You are begging, wait until it's finished")
        return
    if bal[3]<5:
        await ctx.send(f"You need to have 5 stamina to beg")
        return
    
    ngemis = 10
    await ctx.send(f"Begging... Wait {ngemis} second!")
    users[str(user.id)]["prosesngemis"] = 1
    with open("mainbank.json","w") as f:
        json.dump(users,f,indent=4)
    await asyncio.sleep(ngemis)
    kois = [1,2,3]
    bisa = random.choice(kois)
    print(bisa)

    if bisa == 3:
        gagaltext = ["Crazy beggar, go away!","Still young but already begging, work!","Poor!"]
        gagalorang = ["Edhen Tobby","Vincent","Alinne"]
        gagaltext = random.choice(gagaltext)
        gagalorang = random.choice(gagalorang)
        
        em = discord.Embed(title = f"{gagalorang} : {gagaltext}")
        gambar = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTNHFQM-QRF-H6Mc4E7CBfueV4NbEn5icna-g&usqp=CAU"
        em.set_image(url=gambar)
        em.set_footer(text = "You fail to beg :(")
        await ctx.send(embed = em)
        users[str(user.id)]["prosesngemis"] = 0
        users[str(user.id)]["stamina"] -= 5
        with open("mainbank.json","w") as f:
            json.dump(users,f,indent=4)
        return

    if bisa == 2:
        expd = random.randrange(5, 10)
        if users[str(user.id)]["expboost"] == 1:
            expd = expd * 2
        gagaltext = ["I have no money, but i have tickets","I'll give you ticket","Sorry i don't have money but tickets"]
        earnings = random.randrange(1, 2)
        earnings = int(earnings)
        gagalorang = ["Dave Maguire","Alexander","Jack Kruger"]
        gagaltext = random.choice(gagaltext)
        gagalorang = random.choice(gagalorang)
        
        em = discord.Embed(title = f"{gagalorang} : {gagaltext}", description = f"You beg and get {emoticket}{earnings} ticket, {emoexp}exp +{expd}, {emostamina}stamina -5")
        gambar = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRGCZEZhHeMTv9463yhxaQJbGcGtiwCidOOCg&usqp=CAU"
        em.set_image(url=gambar)
        await ctx.send(embed = em)
        users[str(user.id)]["ticket"] += earnings
        users[str(user.id)]["prosesngemis"] = 0
        users[str(user.id)]["stamina"] -= 5   
        users[str(user.id)]["exp"] += expd
        with open("mainbank.json","w") as f:
            json.dump(users,f,indent=4)

    if bisa == 1:
        expd = random.randrange(5, 10)
        if users[str(user.id)]["expboost"] == 1:
            expd = expd * 2
        gagaltext = ["Sad, I'll give you some money","I'll give you money, but try to work :)","Take this money"]
        earnings = random.randrange(60, 100)
        earnings = int(earnings)
        gagalorang = ["James Holland","Michael","Robert"]
        gagaltext = random.choice(gagaltext)
        gagalorang = random.choice(gagalorang)
        
        em = discord.Embed(title = f"{gagalorang} : {gagaltext}", description = f"You beg and get {emorupiah}{earnings} coin, {emoexp}exp +{expd} {emostamina}stamina -5")
        gambar = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRGCZEZhHeMTv9463yhxaQJbGcGtiwCidOOCg&usqp=CAU"
        em.set_image(url=gambar)
        await ctx.send(embed = em)
        users[str(user.id)]["wallet"] += earnings
        users[str(user.id)]["prosesngemis"] = 0
        users[str(user.id)]["stamina"] -= 5
        users[str(user.id)]["exp"] += expd
        with open("mainbank.json","w") as f:
            json.dump(users,f,indent=4)
    await uplevel(ctx)            
        
@client.command(aliases = ['kerja'], description = "Work command to earn money", category = "Economy")
@commands.cooldown(1, 5, commands.BucketType.user)
async def work(ctx):
    emorupiah = discord.utils.get(client.emojis, id=926314665884156004)
    emodamage = discord.utils.get(client.emojis, id=926314853658951720)
    emohealth = discord.utils.get(client.emojis, id=926321297972133909)
    emostamina = discord.utils.get(client.emojis, id=926313999346335744)
    emoexp = discord.utils.get(client.emojis, id=922433918613991465)
    emolevel = discord.utils.get(client.emojis, id=922439376552734820)
    emoticket = discord.utils.get(client.emojis, id=926314047614361690)
    await open_account(ctx.author)
    user = ctx.author
    users = await get_bank_data()
    polisi = await update_bank(ctx.author)
    bal = await update_bank(ctx.author)
    if users[str(user.id)]["prosesbattle"] == 1:
        await ctx.send(f"You are now in battle")
        return
    proseskerja = users[str(user.id)]["proseskerja"]
    if proseskerja==1:
        await ctx.send(f"You are working, wait until it's finished")
        return
    proseshack = users[str(user.id)]["prosesrampok"]
    if proseshack==1:
        await ctx.send(f"You're robbing a bank, wait until it's over")
        return
    prosespenjara = users[str(user.id)]["prosespenjara"]
    if prosespenjara==1:
        await ctx.send(f"You are in prison, wait until you are released")
        return

    prosesngemis = users[str(user.id)]["prosesngemis"]
    if prosesngemis==1:
        await ctx.send(f"You are begging, wait until it's finished")
        return

    if bal[3]<7:
        await ctx.send(f"You need to have 7 stamina to work")
        return

    earnings = random.randrange(150, 200)
    earnings = int(earnings)
    
    defkerja = 30
    minstam = 7
    kekuatan = users[str(user.id)]["kekuatan"]
    kerja = defkerja/kekuatan
    plusexp = random.randrange(7, 10)
    if users[str(user.id)]["expboost"] == 1:
        plusexp = plusexp * 2
    await ctx.send(f"You are working, please wait {kerja} second")
    users[str(user.id)]["proseskerja"] = 1
    with open("mainbank.json","w") as f:
        json.dump(users,f,indent=4)
    await asyncio.sleep(kerja)
    em = discord.Embed(title = f"You work and get {emorupiah}{earnings} coin, {emoexp}exp +{plusexp} {emostamina}stamina -{minstam}")
    gambar = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRGCZEZhHeMTv9463yhxaQJbGcGtiwCidOOCg&usqp=CAU"
    em.set_image(url=gambar)
    await ctx.send(embed = em)
    users[str(user.id)]["proseskerja"] = 0
    with open("mainbank.json","w") as f:
        json.dump(users,f,indent=4)
    await update_bank(ctx.author,-1*minstam,"stamina")
    await update_bank(ctx.author,+1*earnings)
    await update_bank(ctx.author,+1*plusexp,"exp")
    await uplevel(ctx)
  
async def uplevel(ctx):
    user = ctx.author
    users = await get_bank_data()
    bal = await update_bank(user)
    if bal[7]<bal[8]:
        return
    exp = users[str(user.id)]["exp"]
    mexp = users[str(user.id)]["mexp"]
    pluslevel = 1
    plusmexp = mexp*0.5
    plusmexp = int(plusmexp)
    plusmstam = 5
    level = users[str(user.id)]["level"]
    users[str(user.id)]["stamina"] = int(users[str(user.id)]["mstamina"]) + 5
    with open("mainbank.json","w") as f:
        json.dump(users,f,indent=4)    
    await update_bank(user,-1*mexp,"exp")
    await update_bank(user,+1*plusmexp,"mexp")
    await update_bank(user,+1*pluslevel,"level")
    await update_bank(user,+1*plusmstam,"mstamina")
    nlevel = int(level) + 1
    await ctx.send(f"**{user.name}**, you level up to level {nlevel}")
   
@client.command(aliases = ['tarikbank','wd'], description = "Command to withdraw bank balance", category = "Economy")
@commands.cooldown(1, 5, commands.BucketType.user)
async def withdraw(ctx,amount = None):
    await open_account(ctx.author)
    users = await get_bank_data()
    user = ctx.author
    if users[str(user.id)]["prosesbattle"] == 1:
        await ctx.send(f"You are now in battle")
        return
    proseskerja = users[str(user.id)]["proseskerja"]
    if proseskerja==1:
        await ctx.send(f"You are working, wait until it's finished")
        return
    proseshack = users[str(user.id)]["prosesrampok"]
    if proseshack==1:
        await ctx.send(f"You're robbing a bank, wait until it's over")
        return
    prosespenjara = users[str(user.id)]["prosespenjara"]
    if prosespenjara==1:
        await ctx.send(f"You are in prison, wait until you are released")
        return

    prosesngemis = users[str(user.id)]["prosesngemis"]
    if prosesngemis==1:
        await ctx.send(f"You are begging, wait until it's finished")
        return

    if amount == None:
        await ctx.reply("Please write the amount of money you want to withdraw.")
        return
    
    bal = await update_bank(ctx.author)
    if amount == "all":
        amount = bal[1]
        
    if amount == "max":
        amount = bal[1]
        
    amount = int(amount)
    if amount>bal[1]:
        await ctx.reply(f"You don't have {amount} in your bank account.")
        return
    if amount<1:
        await ctx.reply("Balance you want to withdraw must be more than 0.")
        return

    await update_bank(ctx.author,amount)
    await update_bank(ctx.author,-1*amount,"bank")
    
    await ctx.reply(f"You withdraw {amount} from your bank account.")

@client.command(aliases = ['isibank','dep','depo'], description = "Command to deposit your wallet into your bank account", category = "Economy")
@commands.cooldown(1, 5, commands.BucketType.user)
async def deposit(ctx,amount = None):
    await open_account(ctx.author)
    users = await get_bank_data()
    user = ctx.author
    if users[str(user.id)]["prosesbattle"] == 1:
        await ctx.send(f"You are now in battle")
        return
    proseskerja = users[str(user.id)]["proseskerja"]
    if proseskerja==1:
        await ctx.send(f"You are working, wait until it's finished")
        return
    proseshack = users[str(user.id)]["prosesrampok"]
    if proseshack==1:
        await ctx.send(f"You're robbing a bank, wait until it's over")
        return
    prosespenjara = users[str(user.id)]["prosespenjara"]
    if prosespenjara==1:
        await ctx.send(f"You are in prison, wait until you are released")
        return

    prosesngemis = users[str(user.id)]["prosesngemis"]
    if prosesngemis==1:
        await ctx.send(f"You are begging, wait until it's finished")
        return

    if amount == None:
        await ctx.reply("Please write amount you want to deposit")
        return
    
    bal = await update_bank(ctx.author)
    if amount == "all":
        amount = bal[0]
        
    if amount == "max":
        amount = bal[0]
    
    amount = int(amount)
    if amount>bal[0]:
        await ctx.reply(f"You don't have {amount} in your wallet.")
        return
    if amount<1:
        await ctx.reply("Balance you want to deposit must be more than 0.")
        return

    await update_bank(ctx.author,-1*amount)
    await update_bank(ctx.author,amount,"bank")
    
    await ctx.reply(f"You deposit {amount} to your bank account.")
    
    
@client.command(aliases = ['give','tf','send','kirim'], description = "Command to transfer your bank balance to someone else's bank account", category = "Economy")
@commands.cooldown(1, 5, commands.BucketType.user)
async def transfer(ctx,member:discord.Member,amount = None):
    await open_account(ctx.author)
    await open_account(member)
    users = await get_bank_data()
    user = ctx.author
    if member == ctx.author:
        await ctx.send(f"Wow that member is you, you have a twin? xD")
        return
    if users[str(user.id)]["prosesbattle"] == 1:
        await ctx.send(f"You are now in battle")
        return
    proseskerja = users[str(user.id)]["proseskerja"]
    if proseskerja==1:
        await ctx.send(f"You are working, wait until it's finished")
        return
    proseshack = users[str(user.id)]["prosesrampok"]
    if proseshack==1:
        await ctx.send(f"You're robbing a bank, wait until it's over")
        return
    prosespenjara = users[str(user.id)]["prosespenjara"]
    if prosespenjara==1:
        await ctx.send(f"You are in prison, wait until you are released")
        return

    prosesngemis = users[str(user.id)]["prosesngemis"]
    if prosesngemis==1:
        await ctx.send(f"You are begging, wait until it's finished")
        return
    
    if amount == None:
        await ctx.reply("Please write the amount you want to transfer")
        return
    
    bal = await update_bank(ctx.author)
    if amount == "all":
        amount = bal[0]
        
    if amount == "max":
        amount = bal[0]
    
    amount = int(amount)
    if amount>bal[1]:
        await ctx.reply(f"You don't have {amount} in your bank account")
        return

    if amount<1:
        await ctx.reply("Balance you want to transfer must be more than 0.")
        return

    await update_bank(ctx.author,-1*amount,"bank")
    await update_bank(member,amount,"bank")
    
    await ctx.reply(f"You transfer {amount} to {member.name} bank account.")

@client.command(aliases = ['robbank','rampok','rob','rampokbank'], description = "Command to rob a bank", category = "Economy")
@commands.cooldown(1, 25, commands.BucketType.user)
async def bankrob(ctx):
    emorupiah = discord.utils.get(client.emojis, id=926314665884156004)
    emodamage = discord.utils.get(client.emojis, id=926314853658951720)
    emohealth = discord.utils.get(client.emojis, id=926321297972133909)
    emostamina = discord.utils.get(client.emojis, id=926313999346335744)
    emoexp = discord.utils.get(client.emojis, id=922433918613991465)
    emolevel = discord.utils.get(client.emojis, id=922439376552734820)
    emoticket = discord.utils.get(client.emojis, id=926314047614361690)
    await open_account(ctx.author)
    users = await get_bank_data()
    user = ctx.author
    bal = await update_bank(ctx.author)
    polisi = await update_bank(ctx.author)
    earnings = random.randrange(150, 200)
    earnings = int(earnings)
    jahat = earnings*0.01
    jahat = int(jahat)
    oldjahat = users[str(user.id)]["kejahatan"]
    newjahat = jahat+oldjahat
    if users[str(user.id)]["prosesbattle"] == 1:
        await ctx.send(f"You are now in battle")
        return
    proseskerja = users[str(user.id)]["proseskerja"]
    if proseskerja==1:
        await ctx.send(f"You are working, wait until it's finished")
        return
    proseshack = users[str(user.id)]["prosesrampok"]
    if proseshack==1:
        await ctx.send(f"You're robbing a bank, wait until it's over")
        return
    prosespenjara = users[str(user.id)]["prosespenjara"]
    if prosespenjara==1:
        await ctx.send(f"You are in prison, wait until you are released")
        return

    prosesngemis = users[str(user.id)]["prosesngemis"]
    if prosesngemis==1:
        await ctx.send(f"You are begging, wait until it's finished")
        return
    proseshack = users[str(user.id)]["prosesrampok"]
    if proseshack==1:
        await ctx.send(f"You're robbing a bank, wait until it's over")
        return
    prosespenjara = users[str(user.id)]["prosespenjara"]
    if prosespenjara==1:
        await ctx.send(f"You are in prison, wait until you are released")
        return
    if users[str(user.id)]["stamina"] < 10:
        await ctx.send(f"You need to have 10 stamina to work")
        return
    
    expd = random.randrange(10, 20)
    if users[str(user.id)]["expboost"] == 1:
        expd = expd * 2
    kekuatan = users[str(user.id)]["kekuatan"]
    proses = 60
    hack = proses/kekuatan
    await ctx.send(f"You are robbing a bank, wait {int(hack)} second")
    users[str(user.id)]["prosesrampok"] = 1
    with open("mainbank.json","w") as f:
        json.dump(users,f,indent=4)    
    await asyncio.sleep(int(hack))
    await ctx.reply(f"You rob bank and get {emorupiah}{earnings} coin, {emoexp}exp +{expd} {emostamina}stamina -10")
    users[str(user.id)]["prosesrampok"] = 0
    with open("mainbank.json","w") as f:
        json.dump(users,f,indent=4)   
    await update_bank(ctx.author,+1*jahat,"kejahatan")
    await update_bank(ctx.author,+1*earnings)
    await update_bank(ctx.author,-1*10,"stamina")
    await update_bank(ctx.author,+1*expd,"exp")
    await uplevel(ctx)
    
    if polisi[5]>polisi[6]:
        await penjara(ctx)
        return          
   
async def penjara(ctx):
    await open_account(ctx.author)
    user = ctx.author
    users = await get_bank_data()
    polisi = await update_bank(ctx.author)
    bal = await update_bank(ctx.author)
    
    jahat = users[str(user.id)]["kejahatan"]
    penjara = 180*jahat
    menit = penjara/60
    
    await ctx.send(f"**{ctx.author.name}** you have been arrested and imprisoned, wait {menit} minutes before you are released")
    users[str(user.id)]["prosespenjara"] = 1
    with open("mainbank.json","w") as f:
        json.dump(users,f,indent=4)
    await asyncio.sleep(penjara)
    await ctx.send(f"The police have released you, be careful next time")
    users[str(user.id)]["prosespenjara"] = 0
    users[str(user.id)]["kejahatan"] = 0
    with open("mainbank.json","w") as f:
        json.dump(users,f,indent=4)

@client.command(aliases = ['upgradeitem','upitem','itemupgrade','itemup'], description = "Command to upgrade item level")
@commands.cooldown(1, 3, commands.BucketType.user)
async def upgrade(ctx,item_id,amount = 1):
    await open_account(ctx.author)
    users = await get_bank_data()
    user = ctx.author
    proseskerja = users[str(user.id)]["proseskerja"]
    if users[str(user.id)]["prosesbattle"] == 1:
        await ctx.send(f"You are now in battle")
        return
    if proseskerja==1:
        await ctx.send(f"You are working, wait until it's finished")
        return
    proseshack = users[str(user.id)]["prosesrampok"]
    if proseshack==1:
        await ctx.send(f"You're robbing a bank, wait until it's over")
        return
    prosespenjara = users[str(user.id)]["prosespenjara"]
    if prosespenjara==1:
        await ctx.send(f"You are in prison, wait until you are released")
        return

    prosesngemis = users[str(user.id)]["prosesngemis"]
    if prosesngemis==1:
        await ctx.send(f"You are begging, wait until it's finished")
        return    
    try:
        item_id = int(item_id)
    except:
        await ctx.send(f"You need to use item id.")
        return
    int(amount)
    if amount < 1:
        await ctx.send(f"Amount of the upgrade you want to item cannot be less than 1")
        return
    for x in range(amount):
        mrange = int(amount) - 1
        await up_this(ctx,item_id,x,mrange)
                      
async def up_this(ctx,item_id,giliran,mgiliran,amount = 1):
    emorupiah = discord.utils.get(client.emojis, id=926314665884156004)
    await open_account(ctx.author)
    users = await get_bank_data()
    user = ctx.author
    try:
        bag = users[str(user.id)]["bag"]
    except:
        bag = []
    name_ = None
    for item in bag:
        name = item["item"].lower()
        nid = item["id"]
        if nid == item_id:
            name_ = name
            price = item["price"]
            kategori = item["kategori"]            
            if kategori == "food":
                if giliran != mgiliran:
                    return
                await ctx.send(f"You can't upgrade food")
                return
            iamount = item["amount"]
            level = item["level"]                
            evolve = item["evolve"]
            break

    if name_ == None:
        if giliran != mgiliran:
            return
        await ctx.send(f"Item with id {item_id} not in your bag.")
        return            
    if iamount < 1:
        if giliran != mgiliran:
            return
        await ctx.send(f"{name.capitalize()} not in your bag.")
        return
    mlevel = 20 * int(evolve)
    mlevel = int(mlevel)
    nlevel = int(level) + int(amount)
    if nlevel > mlevel:
        if giliran != mgiliran:
            return
        await ctx.send(f"{name.capitalize()} level max, evolve {name.capitalize()} to upgrade it again")
        return
    cost = price * 0.15
    if users[str(user.id)]["wallet"] < int(cost):
        if giliran != mgiliran:
            return
        await ctx.send(f"You don't have enough money in your wallet to upgrade {name.capitalize()}, you need {emorupiah}{cost}")
        return
    index = 0
    for item in bag:
        nid = item["id"]
        if nid == item_id:
            users[str(user.id)]["bag"][index]["level"] += 1
            users[str(user.id)]["wallet"] -= int(cost)
            if kategori == "sword":
                damage = users[str(user.id)]["bag"][index]["damage"]
                damage = int(damage) * 1.20
                users[str(user.id)]["bag"][index]["damage"] = int(damage)
            if kategori == "armor":
                bagian = users[str(user.id)]["bag"][index]["bagian"]
                if bagian == "boots":
                    speed = users[str(user.id)]["bag"][index]["speed"]
                    speed = int(speed) * 1.20
                    users[str(user.id)]["bag"][index]["speed"] = int(speed)
                bonushp = users[str(user.id)]["bag"][index]["bonushp"]
                bonushp = int(bonushp) * 1.20
                users[str(user.id)]["bag"][index]["bonushp"] = int(bonushp)     
            price = users[str(user.id)]["bag"][index]["price"]
            price = int(price) * 1.20
            users[str(user.id)]["bag"][index]["price"] = int(price)                            
            with open("mainbank.json","w") as f:
                json.dump(users,f,indent=4)
            break
        else:
            index += 1
    nowlev = int(level) + 1        
    await ctx.send(f"Successfully upgrade {name.capitalize()} to level {nowlev} for {emorupiah}{int(cost)}")        
    return

@client.command(aliases = ['evo'], description = "Command to evolve item")                      
@commands.cooldown(1, 3, commands.BucketType.user)
async def evolve(ctx,item_id):
    emorupiah = discord.utils.get(client.emojis, id=926314665884156004)
    await open_account(ctx.author)
    users = await get_bank_data()
    user = ctx.author
    if users[str(user.id)]["prosesbattle"] == 1:
        await ctx.send(f"You are now in battle")
        return
    proseskerja = users[str(user.id)]["proseskerja"]
    if proseskerja==1:
        await ctx.send(f"You are working, wait until it's finished")
        return
    proseshack = users[str(user.id)]["prosesrampok"]
    if proseshack==1:
        await ctx.send(f"You're robbing a bank, wait until it's over")
        return
    prosespenjara = users[str(user.id)]["prosespenjara"]
    if prosespenjara==1:
        await ctx.send(f"You are in prison, wait until you are released")
        return

    prosesngemis = users[str(user.id)]["prosesngemis"]
    if prosesngemis==1:
        await ctx.send(f"You are begging, wait until it's finished")
        return    
    try:
        item_id = int(item_id)
    except:
        await ctx.send(f"You need to use item id.")
        return
    try:
        bag = users[str(user.id)]["bag"]
    except:
        bag = []
    name_ = None
    for item in bag:
        name = item["item"].lower()
        nid = item["id"]
        if nid == item_id:
            name_ = name
            price = item["price"]
            kategori = item["kategori"]            
            if kategori == "food":
                if giliran != mgiliran:
                    return
                await ctx.send(f"You can't evolve food")
                return
            iamount = item["amount"]
            level = item["level"]                
            evolve = item["evolve"]
            break

    if name_ == None:
        await ctx.send(f"Item with id {item_id} not in your bag.")
        return            
    if iamount < 1:
        await ctx.send(f"{name.capitalize()} not in your bag.")
        return
    mlevel = 20 * int(evolve)
    mlevel = int(mlevel)
    if int(level) < mlevel:
        await ctx.send(f"{name.capitalize()} level is not max, upgrade {name.capitalize()} level first")
        return
    cost = price * 0.5
    if users[str(user.id)]["wallet"] < int(cost):
        await ctx.send(f"You don't have enough money in your wallet to upgrade {name.capitalize()}, you need {emorupiah}{cost}")
        return
    index = 0
    for item in bag:
        name = item["item"]
        nid = item["id"]
        if nid == item_id:
            users[str(user.id)]["bag"][index]["evolve"] += 1
            users[str(user.id)]["bag"][index]["level"] = 1
            users[str(user.id)]["wallet"] -= int(cost)
            if kategori == "sword":
                damage = users[str(user.id)]["bag"][index]["damage"]
                damage = int(damage) * 1.8
                users[str(user.id)]["bag"][index]["damage"] = int(damage)
            if kategori == "armor":
                bagian = users[str(user.id)]["bag"][index]["bagian"]
                if bagian == "boots":
                    speed = users[str(user.id)]["bag"][index]["speed"]
                    speed = int(speed) * 1.8
                    users[str(user.id)]["bag"][index]["speed"] = int(speed)
                bonushp = users[str(user.id)]["bag"][index]["bonushp"]
                bonushp = int(bonushp) * 1.8
                users[str(user.id)]["bag"][index]["bonushp"] = int(bonushp)     
            price = users[str(user.id)]["bag"][index]["price"]
            price = int(price) * 1.8
            users[str(user.id)]["bag"][index]["price"] = int(price)                            
            with open("mainbank.json","w") as f:
                json.dump(users,f,indent=4)
            break
        else:
            index += 1
    nowevo = int(evolve) + 1        
    await ctx.send(f"Successfully evolve {name.capitalize()} to evo {nowevo} for {emorupiah}{int(cost)}")        
    return

@client.command(aliases = ['beli'], description = "Command to buy item from shop", category = "Economy")
@commands.cooldown(1, 3, commands.BucketType.user)
async def buy(ctx, item_name, amount = 1):
    await open_used(ctx.author)
    amount = int(amount)
    await open_account(ctx.author)
    users = await get_bank_data()
    polisi = await update_bank(ctx.author)
    user = ctx.author
    
    if amount < 1:
        await ctx.send(f"Hmm, are you serious about buying {amount} {item_name}?")
        return

    if users[str(user.id)]["prosesbattle"] == 1:
        await ctx.send(f"You are now in battle")
        return

    proseskerja = users[str(user.id)]["proseskerja"]
    if proseskerja==1:
        await ctx.send(f"You are working, wait until it's finished")
        return
    proseshack = users[str(user.id)]["prosesrampok"]
    if proseshack==1:
        await ctx.send(f"You're robbing a bank, wait until it's over")
        return
    prosespenjara = users[str(user.id)]["prosespenjara"]
    if prosespenjara==1:
        await ctx.send(f"You are in prison, wait until you are released")
        return

    prosesngemis = users[str(user.id)]["prosesngemis"]
    if prosesngemis==1:
        await ctx.send(f"You are begging, wait until it's finished")
        return

    try:
        bag = users[str(user.id)]["bag"]
    except:
        bag = []
    item_name = item_name.lower()
    name_ = None
    for item in allshop:
        name = item["name"].lower()
        if name == item_name:
            name_ = name
            category = item["kategori"]
            break
    if name_ == None:
        await ctx.send(f"The item you entered is invalid, please check again")  
        return     
    if category == "food" or category == "boost":
        nomo = None
        for item in bag:
            nome = item["item"]
            if nome == name:
                nomo = nome
                break
        if nomo == None:
            nbag = len(bag) + 1
            if int(nbag) > 24:
                await ctx.send(f"Your bag can't load new {amount} {name.capitalize()}")    
                return
        res = await buy_food(ctx,item_name,amount)
    if len(bag) >= 24:
        await ctx.send(f"Your bag is full")
        return
    if category == "armor":
        nbag = len(bag) + amount
        if int(nbag) > 24:
            await ctx.send(f"Your bag can't load new {amount} {name.capitalize()}")
            return
        res = await buy_armor(ctx,item_name,amount)
    if category == "sword":
        nbag = len(bag) + amount
        if int(nbag) > 24:
            await ctx.send(f"Your bag can't load new {amount} {name.capitalize()}")
            return
        res = await buy_sword(ctx,item_name,amount)
        
async def buy_armor(ctx,item_name,amount):
    emorupiah = discord.utils.get(client.emojis, id=926314665884156004)
    user = ctx.author
    item_name = item_name.lower()
    for item in allshop:
        name = item["name"].lower()
        if name == item_name:
            price = item["price"]
            speed = item["speed"]
            bagian = item["bagian"]
            bonushp = item["hp"]
            kategori = item["kategori"]
            break
            
    cost = price*amount
    cost = int(cost)
    users = await get_bank_data()
        
    bal = await update_bank(user)
        
    if bal[0]<cost:
        await ctx.send(f"You don't have enough money in your wallet to buy {amount}")
        return
        
    for i in range(amount):
        rid = await randomid(ctx.author)
        obj = {"id":rid, "item":item_name , "amount" : 1 , "bagian":bagian , "bonushp":bonushp, "speed":speed, "price":price, "kategori":kategori, "level":1, "evolve":1}
        try:
            users[str(user.id)]["bag"].append(obj)
        except:
            users[str(user.id)]["bag"] = [obj]
            
    with open("mainbank.json","w") as f:
        json.dump(users,f,indent=4)
                       
    await update_bank(user,cost*-1,"wallet")
    await ctx.send(f"You have purchased {amount} {name.capitalize()} for {emorupiah}{cost}")
    return

async def randomid(user):
    used = await get_used_data()
    rid = max(used[str(user.id)])
    for use in used:
        if rid in used[str(user.id)]:
            rid += 1
        else:
            break
    used[str(user.id)].append(rid)
    with open("used.json","w") as f:
        json.dump(used,f,indent=4)
    return rid

async def buy_food(ctx,item_name,amount):
    emorupiah = discord.utils.get(client.emojis, id=926314665884156004)
    user = ctx.author
    item_name = item_name.lower()
    for item in allshop:
        name = item["name"].lower()
        if name == item_name:
            price = item["price"]
            heal = item["heal"]
            kategori = item["kategori"]
            break

    cost = price*amount
    cost = int(cost)
    users = await get_bank_data()

    bal = await update_bank(user)

    if bal[0]<cost:
        await ctx.send(f"You don't have enough money in your wallet to buy {amount}")
        return

    try:
        index = 0
        t = None
        for thing in users[str(user.id)]["bag"]:
            n = thing["item"]
            if n == item_name:
                old_amt = thing["amount"]
                new_amt = old_amt + amount
                users[str(user.id)]["bag"][index]["amount"] = new_amt
                t = 1
                break
            index+=1 
        if t == None:
            rid = await randomid(ctx.author)
            obj = {"id":rid, "item":item_name , "amount" : amount, "heal":heal, "price":price, "kategori":kategori}
            users[str(user.id)]["bag"].append(obj)
    except:
        rid = await randomid(ctx.author)
        obj = {"id":rid, "item":item_name , "amount" : amount, "heal":heal, "price":price, "kategori":kategori}
        users[str(user.id)]["bag"] = [obj]        

    with open("mainbank.json","w") as f:
        json.dump(users,f,indent=4)

    await update_bank(user,cost*-1,"wallet")
    await ctx.send(f"You have purchased {amount} {name.capitalize()} for {emorupiah}{cost}")
    return
    
async def buy_sword(ctx,item_name,amount):
    emorupiah = discord.utils.get(client.emojis, id=926314665884156004)
    user = ctx.author
    item_name = item_name.lower()
    for item in allshop:
        name = item["name"].lower()
        if name == item_name:
            price = item["price"]
            damage = item["damage"]
            kategori = item["kategori"]
            break

    cost = price*amount
    cost = int(cost)
    users = await get_bank_data()

    bal = await update_bank(user)

    if bal[0]<cost:
        await ctx.send(f"You don't have enough money in your wallet to buy {amount}")
        return

    for i in range(amount):
        rid = await randomid(ctx.author)
        obj = {"id":rid, "item":item_name , "amount" : 1 , "damage":damage, "price":price, "kategori":kategori, "level":1, "evolve":1}
        try:
            users[str(user.id)]["bag"].append(obj)
        except:
            users[str(user.id)]["bag"] = [obj]

    with open("mainbank.json","w") as f:
        json.dump(users,f,indent=4)

    await update_bank(user,cost*-1,"wallet")
    await ctx.send(f"You have purchased {amount} {name.capitalize()} for {emorupiah}{cost}")
    return

@client.command(aliases = ['tas','inv','inventory'], description = "Bag command", category = "Economy")
@commands.cooldown(1, 5, commands.BucketType.user)
async def bag(ctx):
    emorupiah = discord.utils.get(client.emojis, id=926314665884156004)
    emodamage = discord.utils.get(client.emojis, id=926314853658951720)
    emohealth = discord.utils.get(client.emojis, id=926321297972133909)
    emostamina = discord.utils.get(client.emojis, id=926313999346335744)
    emoexp = discord.utils.get(client.emojis, id=922433918613991465)
    emolevel = discord.utils.get(client.emojis, id=922439376552734820)
    emoticket = discord.utils.get(client.emojis, id=926314047614361690)
    emospeed = discord.utils.get(client.emojis, id=926312716086439946)
    await open_account(ctx.author)
    user = ctx.author
    users = await get_bank_data()

    try:
        bag = users[str(user.id)]["bag"]
    except:
        bag = []

    foodem = discord.Embed(title = f"**{user.name}** Bag", color = discord.Color.blue())

    for item in bag:
        kategori = item["kategori"]
        if kategori == "food" or kategori == "boost":
            rid = item["id"]
            name = item["item"]
            amount = item["amount"]
            price = item["price"]
            price = 0.9 * price
            price = int(price)
            heal = item["heal"]
            foodem.add_field(name = f"ID {rid} | {name.capitalize()}---[{amount}]", value = f"Healing {heal} {emohealth}HP | Sell Price : {emorupiah}{price}")
        if kategori == "armor":
            rid = item["id"]
            name = item["item"]
            amount = item["amount"]
            price = item["price"]
            price = 0.9 * price
            price = int(price)
            bonushp = item["bonushp"]
            bagian = item["bagian"]
            speed = item["speed"]
            level = item["level"]
            evolve = item["evolve"]
            fsped = f", {emospeed}Speed +{speed}"
            if speed == 0:
                fsped = ""
            foodem.add_field(name = f"ID {rid} | {name.capitalize()}---[{amount}]", value = f"Level {level} | Evo {evolve} | Max {emohealth}Health +{bonushp}{fsped} | Sell Price : {emorupiah}{price} ")
        if kategori == "sword":
            rid = item["id"]
            name = item["item"]
            amount = item["amount"]
            price = item["price"]
            price = 0.9 * price
            price = int(price)
            damage = item["damage"]
            level = item["level"]
            evolve = item["evolve"]
            foodem.add_field(name = f"ID {rid} | {name.capitalize()}---[{amount}]", value = f"Level {level} | Evo {evolve} | {emodamage}Damage +{damage} | Sell Price : {emorupiah}{price}")
    await ctx.send(embed = foodem)
    return

@client.command(aliases = ['toko'], description = "Shop command", category = "Economy")
@commands.cooldown(1, 5, commands.BucketType.user)
async def shop(ctx):
    emorupiah = discord.utils.get(client.emojis, id=926314665884156004)
    emodamage = discord.utils.get(client.emojis, id=926314853658951720)
    emohealth = discord.utils.get(client.emojis, id=926321297972133909)
    emostamina = discord.utils.get(client.emojis, id=926313999346335744)
    emoexp = discord.utils.get(client.emojis, id=922433918613991465)
    emolevel = discord.utils.get(client.emojis, id=922439376552734820)
    emoticket = discord.utils.get(client.emojis, id=926314047614361690)
    emospeed = discord.utils.get(client.emojis, id=926312716086439946)
    foodem = discord.Embed(title = "Food Shop", description = "Press reaction below to switch pages!", color = discord.Color.red())
    armorem = discord.Embed(title = "Armor Shop", description = "Press reaction below to switch pages!", color = discord.Color.yellow())
    swordem = discord.Embed(title = "Sword Shop", description = "Press reaction below to switch pages!", color = discord.Color.green())
    for item in allshop:
        kategori = item["kategori"]
        if kategori == "food" or kategori == "boost":          
            name = item["name"]
            price = item["price"]
            heal = item["heal"]
            desk = item["deskripsi"]
            foodem.add_field(name = f"{name} {emorupiah}{price}", value = f"Healing {heal} {emohealth}HP | {desk}")        
        if kategori == "armor":
            name = item["name"]
            price = item["price"]
            bonushp = item["hp"]
            bagian = item["bagian"]
            desk = item["deskripsi"]
            speed = item["speed"]
            fsped = f", {emospeed}Speed +{speed}"
            if speed == 0:
                fsped = ""            
            armorem.add_field(name = f"{name} {emorupiah}{price}", value = f"Max {emohealth}Health +{bonushp}{fsped} | Bagian : {bagian} | {desk}")
        if kategori == "sword":
            name = item["name"]
            price = item["price"]
            damage = item["damage"]
            desk = item["deskripsi"]
            swordem.add_field(name = f"{name} {emorupiah}{price}", value = f"{emodamage}Damage +{damage} | {desk}")
    paginator = DiscordUtils.Pagination.CustomEmbedPaginator(ctx, remove_reactions=True)
    paginator.add_reaction('⏮️', "first")
    paginator.add_reaction('⏪', "back")
    paginator.add_reaction('⏩', "next")
    paginator.add_reaction('⏭️', "last")
    embeds = [foodem, armorem, swordem]
    await paginator.run(embeds)    
                        
@client.command(aliases = ['jual'], description = "Command to sell item", category = "Economy")
@commands.cooldown(1, 3, commands.BucketType.user)
async def sell(ctx,item_id,amount = 1):
    amount = int(amount)
    await open_account(ctx.author)
    users = await get_bank_data()
    user = ctx.author

    if amount < 1:
        await ctx.send(f"You can't sell if amount is {amount}")
        return
    if users[str(user.id)]["prosesbattle"] == 1:
        await ctx.send(f"You are now in battle")
        return
    proseskerja = users[str(user.id)]["proseskerja"]
    if proseskerja==1:
        await ctx.send(f"You are working, wait until it's finished")
        return
    proseshack = users[str(user.id)]["prosesrampok"]
    if proseshack==1:
        await ctx.send(f"You're robbing a bank, wait until it's over")
        return
    prosespenjara = users[str(user.id)]["prosespenjara"]
    if prosespenjara==1:
        await ctx.send(f"You are in prison, wait until you are released")
        return

    prosesngemis = users[str(user.id)]["prosesngemis"]
    if prosesngemis==1:
        await ctx.send(f"You are begging, wait until it's finished")
        return

    if amount < 1:
        await ctx.send(f"The amount of the item you want to sell cannot be less than 1")
        return

    try:
        item_id = int(item_id)
    except:
        await ctx.send(f"You need to use item id.")
        return

    res = await sell_this(ctx,item_id,amount)

async def sell_this(ctx,item_id,amount,price = None):
    emorupiah = discord.utils.get(client.emojis, id=926314665884156004)
    users = await get_bank_data()
    user = ctx.author
    try:
        bag = users[str(user.id)]["bag"]
    except:
        bag = []
    name_ = None
    index = 0
    for item in bag:
        nid = item["id"]
        name = item["item"].lower()
        if nid == item_id:
            name_ = name
            price = 0.9 * item["price"]
            harga = item["price"]
            old_amt = item["amount"]
            break
        index += 1
    if name_ == None:
        await ctx.send(f"You don't have item with id {item_id}.")
        return        
    new_amt = old_amt - amount
    if new_amt < 0:
        await ctx.send(f"You don't have {amount} {name.capitalize()}.")
        return
    if new_amt == 0:
        obj = users[str(user.id)]["bag"][index]
        users[str(user.id)]["bag"].remove(obj)
    elif new_amt != 0:
        users[str(user.id)]["bag"][index]["amount"] = new_amt    
    with open("mainbank.json","w") as f:
        json.dump(users,f,indent=4)
    cost = price*amount
    cost = int(cost)
    pcost = harga*amount
    pcost = int(pcost)
    users = await get_bank_data()
    bal = await update_bank(user)
    await update_bank(user,cost,"wallet")
    pajak = pcost - cost
    await ctx.send(f"You sell {amount} {name.capitalize()} for {emorupiah}{cost}, already with tax {pajak}")
    
@client.command(aliases = ['use','makan'], description = "Command to eat food", category = "Economy")
async def eat(ctx,item_id,amount = 1):
    amount = int(amount)
    await open_account(ctx.author)
    users = await get_bank_data()
    user = ctx.author
    try:
        bag = users[str(user.id)]["bag"]
    except:
        bag = []
    try:
        item_id = int(item_id)
    except:
        await ctx.send(f"You need to use item id.")
        return
    name_ = None
    index = 0
    for item in bag:
        nid = item["id"]
        name = item["item"].lower()
        if nid == item_id:
            name_ = name            
            category = item["kategori"]
        index += 1
    if name_ == None:
        await ctx.send(f"You don't have item with id {item_id}.")
        return        

    if category == "boost":
        await eat_boost(ctx,item_id)
        return

    if category != "food":
        await ctx.send(f"The item is not food")
        return

    res = await eat_this(ctx,item_id,amount)

async def eat_boost(ctx,item_id):
    users = await get_bank_data()
    user = ctx.author
    if users[str(user.id)]["expboost"] == 1:
        await ctx.send(f"Your exp booster is still there")
        return
    try:
        bag = users[str(user.id)]["bag"]
    except:
        bag = []
    name_ = None
    index = 0
    for item in bag:
        name = item["item"].lower()
        nid = item["id"]
        if nid == item_id:
            name_ = name
            amount = item["amount"]
            break
        index += 1
    if name_ == None:
        await ctx.send(f"You don't have item with id {item_id} in your bag.")
        return        
    new_amt = amount - 1
    if new_amt < 0:
        await ctx.send(f"You don't have {amount} {n.capitalize()}.")
        return
    elif new_amt == 0:
        obj = users[str(user.id)]["bag"][index]
        users[str(user.id)]["bag"].remove(obj)
    elif new_amt != 0:
        users[str(user.id)]["bag"][index]["amount"] = new_amt
    users[str(user.id)]["expboost"] = 1
    users[str(user.id)]["timeboost"] = 600
    with open("mainbank.json","w") as f:
        json.dump(users,f,indent=4)
    await ctx.send(f"Your exp booster x2 has been active for 10 minutes")

@tasks.loop(seconds=1)
async def loadboost():
    users = await get_bank_data()
    try:
        for user in users:
            if users[user]["expboost"] == 1:
                if users[user]["timeboost"] != 0:
                    users[user]["timeboost"] -= 1
                    with open("mainbank.json","w") as f:
                        json.dump(users,f,indent=4)
                elif users[user]["timeboost"] == 0:
                    users[user]["expboost"] = 0
                    with open("mainbank.json","w") as f:
                        json.dump(users,f,indent=4)
    except:
        pass

async def eat_this(ctx,item_id,amount):
    emohealth = discord.utils.get(client.emojis, id=926321297972133909)
    user = ctx.author
    await open_account(user)
    users = await get_bank_data()
    try:
        bag = users[str(user.id)]["bag"]
    except:
        bag = []
    name_ = None
    index = 0
    for item in bag:
        name = item["item"].lower()
        nid = item["id"]
        if nid == item_id:
            name_ = name
            heal = amount * item["heal"]
            healas = item["heal"]            
            old_amt = item["amount"]
            break
        index += 1

    if users[str(user.id)]["prosesbattle"] == 1:
        await ctx.send(f"You are now in battle")
        return
    if name_ == None:
        await ctx.send(f"You don't have item with id {item_id} in your bag.")
        return
    users = await get_bank_data()
    health = users[str(user.id)]["health"]
    maxhealth = users[str(user.id)]["maxhealth"]
    maxheal = maxhealth - health
    if health >= maxhealth:
        await ctx.send(f"No need to eat now")
        return
    bamount = int(amount)
    if heal > maxheal:
        if amount != 1:
            for i in range(amount):
                if amount < 1:
                    await ctx.send(f"Can't eat {name.capitalize()} right now.")
                    return
                if heal <= maxheal:
                    if heal == maxheal:                        
                        break
                    amount += 1
                    heal = healas * amount
                    print(heal)
                    if heal > maxheal:
                        heal = int(maxheal)           
                    break
                amount -= 1
                heal = healas * amount
                print(heal)
        else:            
            heal = int(maxheal)
            print(heal)
    new_amt = old_amt - amount
    if new_amt < 0:
        await ctx.send(f"You don't have {amount} {n.capitalize()}.")
        return
    elif new_amt == 0:
        obj = users[str(user.id)]["bag"][index]
        users[str(user.id)]["bag"].remove(obj)
    elif new_amt != 0:
        users[str(user.id)]["bag"][index]["amount"] = new_amt
    uamount = int(bamount) - int(amount)
    if uamount != 0:
        await ctx.send(f"{uamount} {name.capitalize()} of {bamount} {name.capitalize()} is useless to eat, the amount to be eaten is reduced")
    users[str(user.id)]["health"] += heal
    with open("mainbank.json","w") as f:
        json.dump(users,f,indent=4)
    await ctx.send(f"You eat {amount} {name.capitalize()} and recovered {emohealth}{heal} HP, your health is now {emohealth}{health+heal} HP.")
    
@client.command(aliases = ["lb"], description = "Command to check richest people", category = "Economy")
async def leaderboard(ctx,x = 5):
    emorupiah = discord.utils.get(client.emojis, id=926314665884156004)
    users = await get_bank_data()
    leader_board = {}
    total = []
    for user in users:
        name = int(user)
        total_amount = users[user]["wallet"] + users[user]["bank"]
        leader_board[total_amount] = name
        total.append(total_amount)

    total = sorted(total,reverse=True)    

    em = discord.Embed(title = f"Top {x} Richest people" , description = "This is the richest people who have the most money",color = discord.Color(0xfa43ee))
    index = 1
    for amt in total:
        id_ = leader_board[amt]
        member = client.get_user(id_)
        name = member.name
        em.add_field(name = f"{index}. {name}" , value = f"{emorupiah}{amt}",  inline = False)
        if index == x:
            break
        else:
            index += 1

    await ctx.send(embed = em) 
    
async def open_account(user):

    users = await get_bank_data()
        
    if str(user.id) in users:
        return False
    else:
        users[str(user.id)] = {}
        users[str(user.id)]["health"] = 500
        users[str(user.id)]["maxhealth"] = 500
        users[str(user.id)]["damage"] = 100
        users[str(user.id)]["shield"] = 230
        users[str(user.id)]["speed"] = 50   
        users[str(user.id)]["wallet"] = 100
        users[str(user.id)]["bank"] = 0
        users[str(user.id)]["ticket"] = 1
        users[str(user.id)]["stamina"] = 50
        users[str(user.id)]["mstamina"] = 50
        users[str(user.id)]["kejahatan"] = 0
        users[str(user.id)]["mkejahatan"] = 20
        users[str(user.id)]["exp"] = 0
        users[str(user.id)]["mexp"] = 100
        users[str(user.id)]["level"] = 1
        users[str(user.id)]["kekuatan"] = 1
        users[str(user.id)]["proseskerja"] = 0
        users[str(user.id)]["prosesrampok"] = 0
        users[str(user.id)]["prosespenjara"] = 0
        users[str(user.id)]["prosesngemis"] = 0
        users[str(user.id)]["enemyhp"] = 250
        users[str(user.id)]["enemysh"] = 115
        users[str(user.id)]["enemytk"] = 50
        users[str(user.id)]["enemysp"] = 25  
        users[str(user.id)]["floor"] = 1
        users[str(user.id)]["expboost"] = 0
        users[str(user.id)]["timeboost"] = 0     
        users[str(user.id)]["prosesbattle"] = 0

    with open("mainbank.json","w") as f:
        json.dump(users,f,indent=4)
    return True

async def open_data(user):

    with open("chatbot.json", "r") as f:
        data = json.load(f)
        
    if str(user.id) in data:
        return False
    else:
        data[str(user.id)] = {}
        data[str(user.id)]["mode"] = 0
        data[str(user.id)]["channelid"] = 0

    with open("chatbot.json","w") as f:
        json.dump(data,f,indent=4)
    return True

async def open_used(user):

    used = await get_used_data()
        
    if str(user.id) in used:
        return False
    else:
        used[str(user.id)] = []
        used[str(user.id)].append(0)

    with open("used.json","w") as f:
        json.dump(used,f,indent=4)
    return True
        
async def get_bank_data():
    with open("mainbank.json","r") as f:
        users = json.load(f)
                
    return users

async def update_bank(user,change = 0,mode = "wallet"):
    users = await get_bank_data()
    
    users[str(user.id)][mode] += change

    with open("mainbank.json","w") as f:
        json.dump(users,f,indent=4)
        
#dompet = bal[0]
#bank = bal[1]
#tiket = bal[2]
#stamina = bal[3]
#mstam = bal[4]
#jahat = bal[5]
#mjahat = 6
#exp = 7
#mexp = 8
#lvl = 9
#health = 10
#mhealth = 11
    bal = [users[str(user.id)]["wallet"],users[str(user.id)]["bank"],users[str(user.id)]["ticket"],users[str(user.id)]["stamina"],users[str(user.id)]["mstamina"],users[str(user.id)]["kejahatan"],users[str(user.id)]["mkejahatan"],users[str(user.id)]["exp"],users[str(user.id)]["mexp"],users[str(user.id)]["level"],users[str(user.id)]["health"],users[str(user.id)]["maxhealth"]]
    return bal 
        
        
async def open_armor(user):

    users = await get_armor_data()
        
    if str(user.id) in users:
        return False
    else:
        users[str(user.id)] = {}
        users[str(user.id)]["helmets"] = "nothing"
        users[str(user.id)]["vest"] = "nothing"
        users[str(user.id)]["leggings"] = "nothing"
        users[str(user.id)]["boots"] = "nothing"
        users[str(user.id)]["hphelmets"] = 0
        users[str(user.id)]["hpvest"] = 0
        users[str(user.id)]["hpleggings"] = 0
        users[str(user.id)]["hpboots"] = 0
        users[str(user.id)]["sword"] = "nothing"
        users[str(user.id)]["dmgsword"] = 0
        
    with open("armor.json","w") as f:
        json.dump(users,f,indent=4)
    return True               
    
async def get_armor_data():
    with open("armor.json","r") as f:
        users = json.load(f)
        
    return users  
        
async def get_used_data():
    with open("used.json","r") as f:
        used = json.load(f)
        
    return used 


client.loop.run_until_complete(create_db_pool()) 
client.run("ODk5NjAzNzQ2MDI2MzAzNTA5.YW1LRg.HTgc8_fdsyjkrzu47H3yTArU6fc")