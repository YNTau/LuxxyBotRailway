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

def get_prefix(client,message):

    with open("prefixes.json", "r") as f:
        prefixes = json.load(f)
        
    prefix = prefixes[str(message.guild.id)]

    return prefixes[str(message.guild.id)]

client = commands.Bot(command_prefix = get_prefix,intents = discord.Intents.all())
rs = RandomStuffV2(async_mode = True)

client.remove_command("help")

@client.event
async def on_ready():
    print("Ready")
    staminaup.start()
    print("Berhasil meloop stamina refill")
    
@client.event
async def on_guild_join(guild):

    with open("prefixes.json", "r") as f:
        prefixes = json.load(f)

    prefixes[str(guild.id)] = "L "

    with open("prefixes.json", "w") as f:
        json.dump(prefixes,f)

@client.command(description = "Help Command & List Command")
async def help(ctx):
    with open("prefixes.json", "r") as f:
        prefixes = json.load(f)
        
    prefix = prefixes[str(ctx.guild.id)]
    em = discord.Embed(title="Command List", color = discord.Color.blue())
    for command in client.walk_commands():
        description = command.description     
        aliases = command.aliases
        if aliases == []:
            aliases = ''
        aliases = ", ".join(aliases)
        if aliases != '':
            aliases = f"Aliases = {aliases}"
        print(aliases)
        if not description or description is None or description == "":
            description = 'Tidak ada Deskripsi'
        em.add_field(name=f"`{prefix}{command.name} {command.signature if command.signature is not None else ''} {aliases}`", value=f"**{description}**,", inline = False)
        em.set_thumbnail(url=ctx.author.avatar.url)
    await ctx.send(embed=em)

@client.command(aliases = ['changeprefix','gantiprefix'], description = "Command untuk mengganti Prefix bot (Jangan sampai lupa prefix yang sudah diubah!)", category = "Config")
@commands.has_permissions(administrator = True)
async def setprefix(ctx, prefix=None):

    if prefix == None:
        await ctx.send("Prefix baru tidak boleh kosong!")
        return

    with open("prefixes.json", "r") as f:
        prefixes = json.load(f)

    prefixes[str(ctx.guild.id)] = prefix

    with open("prefixes.json", "w") as f:
        json.dump(prefixes,f)    

    await ctx.send(f"Prefix Luxxy Bot berhasil diubah ke {prefix}")

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
    
@client.command(aliases = ['botchat'], description = "Command untuk set channel Chat Bot, On/Off fitur Chat Bot ( Command setchannel harus di kirim di channel yang ingin di set )", category = "Config")
@commands.has_permissions(administrator = True)
async def chatbot(ctx, option, channel:discord.TextChannel = None):
    await open_data(ctx.guild)
    with open("chatbot.json", "r") as f:
        data = json.load(f)
        
    if option == "on":
        channelid = data[str(ctx.guild.id)]["channelid"]
        if channelid == 0:
            await ctx.send("Chat Bot Channel belum kamu set!")
            return
        await ctx.send("Fitur Chat Bot di server ini berhasil dihidupkan")
        data[str(ctx.guild.id)]["mode"] = 1
        with open("chatbot.json","w") as f:
            json.dump(data,f,indent=4)
        return
        
    if option == "off":
        channelid = data[str(ctx.guild.id)]["channelid"]
        if channelid == 0:
            await ctx.send("Chat Bot Channel belum kamu set!")
            return
        await ctx.send("Fitur Chat Bot di server ini berhasil dimatikan")
        data[str(ctx.guild.id)]["mode"] = 0
        with open("chatbot.json","w") as f:
            json.dump(data,f,indent=4)
        return
    if option == "setchannel":
        if channel == None:
            await ctx.send("Anda belum me mention channel yang ingin di set!")
            return
        await ctx.send(f"Channel **{channel.name}** telah berhasil diset sebagai Chat Bot Channel")
        data[str(ctx.guild.id)]["channelid"] = channel.id
        with open("chatbot.json","w") as f:
            json.dump(data,f,indent=4)
        return       
    else:
        await ctx.send("Pilihan tidak valid, setchannel untuk set Chat Bot Channel, on atau off untuk menghidupkan atau mematikan fitur Chat Bot di server ini!")
        return

@client.event
async def on_message(message):
    if client.user == message.author:
        return

    await open_data(message.guild)
    with open("chatbot.json", "r") as f:
        data = json.load(f)
    chnya = data[str(message.guild.id)]["channelid"]
    if message.channel.id == chnya:  
        mode = data[str(message.guild.id)]["mode"]
        if mode == 1:
            response = await rs.get_ai_response(message.content)
            await message.reply(response["message"])
            return
        
    await client.process_commands(message)

allshop = [{"name":"Nasi_Ayam","price":27600,"heal":99, "kategori":"food","deskripsi":"Nasi dengan ayam goyeng"}, 
           {"name":"Nasi_Goreng","price":15300,"heal":49, "kategori":"food","deskripsi":"Nasi goreng angkel muthu"}, 
           {"name":"Bakwan","price":8500,"heal":25, "kategori":"food","deskripsi":"Bakwan sedap renyah uwah"},
           {"name":"Tempe","price":5000,"heal":11, "kategori":"food","deskripsi":"Tempe buatan emak-emak arisan"},
           {"name":"Roti","price":2500,"heal":5, "kategori":"food","deskripsi":"Roti bakar"},
           {"name":"Cokelat","price":1000,"heal":2, "kategori":"food","deskripsi":"Cokelat SilverKing"},
           {"name":"Permen","price":500,"heal":1, "kategori":"food","deskripsi":"Permen masa kecil"},
           {"name":"Feather_Helmets","price":27000,"bagian":"helmets","deskripsi":"Helm pelindung","hp":50, "kategori":"armor"},
           {"name":"Feather_Chestplates","price":65250,"bagian":"chestplates","deskripsi":"Baju pelindung","hp":100, "kategori":"armor"},
           {"name":"Feather_Leggings","price":43500,"bagian":"leggings","deskripsi":"Celana pelindung","hp":25, "kategori":"armor"},
           {"name":"Feather_Boots","price":15250,"bagian":"boots","deskripsi":"Sepatu pelindung","hp":10, "kategori":"armor"},
           {"name":"Stone_Helmets","price":40500,"bagian":"helmets","deskripsi":"Helm pelindung","hp":75, "kategori":"armor"},
           {"name":"Stone_Chestplates","price":97875,"bagian":"chestplates","deskripsi":"Baju pelindung","hp":150, "kategori":"armor"},
           {"name":"Stone_Leggings","price":65250,"bagian":"leggings","deskripsi":"Celana pelindung","hp":37, "kategori":"armor"},
           {"name":"Stone_Boots","price":22875,"bagian":"boots","deskripsi":"Sepatu pelindung","hp":15, "kategori":"armor"},
           {"name":"Copper_Helmets","price":60750,"bagian":"helmets","deskripsi":"Helm pelindung","hp":112, "kategori":"armor"},
           {"name":"Copper_Chestplates","price":146812,"bagian":"chestplates","deskripsi":"Baju pelindung","hp":225, "kategori":"armor"},
           {"name":"Copper_Leggings","price":97875,"bagian":"leggings","deskripsi":"Celana pelindung","hp":55, "kategori":"armor"},
           {"name":"Copper_Boots","price":34312,"bagian":"boots","deskripsi":"Sepatu pelindung","hp":22, "kategori":"armor"},
           {"name":"Platinum_Helmets","price":91125,"bagian":"helmets","deskripsi":"Helm pelindung","hp":168, "kategori":"armor"},
           {"name":"Platinum_Chestplates","price":220218,"bagian":"chestplates","deskripsi":"Baju pelindung","hp":337, "kategori":"armor"},
           {"name":"Platinum_Leggings","price":146812,"bagian":"leggings","deskripsi":"Celana pelindung","hp":82, "kategori":"armor"},
           {"name":"Platinum_Boots","price":51468,"bagian":"boots","deskripsi":"Sepatu pelindung","hp":33, "kategori":"armor"},   
           {"name":"Stone_Axe","price":25500,"damage":65, "kategori":"sword","deskripsi":"Pedang buat battle"},
           {"name":"Platinum_Sword","price":38250,"damage":97, "kategori":"sword","deskripsi":"Pedang buat battle"},
           {"name":"Katana","price":57375,"damage":145, "kategori":"sword","deskripsi":"Pedang buat battle"}]                    

foodshop = [{"name":"Nasi_Ayam","price":27600,"heal":99, "kategori":"food","deskripsi":"Nasi dengan ayam goyeng"}, 
            {"name":"Nasi_Goreng","price":15300,"heal":49, "kategori":"food","deskripsi":"Nasi goreng angkel muthu"}, 
            {"name":"Bakwan","price":8500,"heal":25, "kategori":"food","deskripsi":"Bakwan sedap renyah uwah"},
            {"name":"Tempe","price":5000,"heal":11, "kategori":"food","deskripsi":"Tempe buatan emak-emak arisan"},
            {"name":"Roti","price":2500,"heal":5, "kategori":"food","deskripsi":"Roti bakar"},
            {"name":"Cokelat","price":1000,"heal":2, "kategori":"food","deskripsi":"Cokelat SilverKing"},
            {"name":"Permen","price":500,"heal":1, "kategori":"food","deskripsi":"Permen masa kecil"}]
    
armorshop = [{"name":"Feather_Helmets","price":27000,"bagian":"helmets","deskripsi":"Helm pelindung","hp":50, "kategori":"armor"},
            {"name":"Feather_Chestplates","price":65250,"bagian":"chestplates","deskripsi":"Baju pelindung","hp":100, "kategori":"armor"},
            {"name":"Feather_Leggings","price":43500,"bagian":"leggings","deskripsi":"Celana pelindung","hp":25, "kategori":"armor"},
            {"name":"Feather_Boots","price":15250,"bagian":"boots","deskripsi":"Sepatu pelindung","hp":10, "kategori":"armor"},
            {"name":"Stone_Helmets","price":40500,"bagian":"helmets","deskripsi":"Helm pelindung","hp":75, "kategori":"armor"},
            {"name":"Stone_Chestplates","price":97875,"bagian":"chestplates","deskripsi":"Baju pelindung","hp":150, "kategori":"armor"},
            {"name":"Stone_Leggings","price":65250,"bagian":"leggings","deskripsi":"Celana pelindung","hp":37, "kategori":"armor"},
            {"name":"Stone_Boots","price":22875,"bagian":"boots","deskripsi":"Sepatu pelindung","hp":15, "kategori":"armor"},
            {"name":"Copper_Helmets","price":60750,"bagian":"helmets","deskripsi":"Helm pelindung","hp":112, "kategori":"armor"},
            {"name":"Copper_Chestplates","price":146812,"bagian":"chestplates","deskripsi":"Baju pelindung","hp":225, "kategori":"armor"},
            {"name":"Copper_Leggings","price":97875,"bagian":"leggings","deskripsi":"Celana pelindung","hp":55, "kategori":"armor"},
            {"name":"Copper_Boots","price":34312,"bagian":"boots","deskripsi":"Sepatu pelindung","hp":23, "kategori":"armor"},
            {"name":"Platinum_Helmets","price":91125,"bagian":"helmets","deskripsi":"Helm pelindung","hp":168, "kategori":"armor"},
            {"name":"Platinum_Chestplates","price":220218,"bagian":"chestplates","deskripsi":"Baju pelindung","hp":337, "kategori":"armor"},
            {"name":"Platinum_Leggings","price":146812,"bagian":"leggings","deskripsi":"Celana pelindung","hp":82, "kategori":"armor"},
            {"name":"Platinum_Boots","price":51468,"bagian":"boots","deskripsi":"Sepatu pelindung","hp":35, "kategori":"armor"}]
            
swordshop = [{"name":"Stone_Axe","price":25500,"damage":65, "kategori":"sword","deskripsi":"Pedang buat battle"},
             {"name":"Platinum_Sword","price":38250,"damage":97, "kategori":"sword","deskripsi":"Pedang buat battle"},
             {"name":"Katana","price":57375,"damage":145, "kategori":"sword","deskripsi":"Pedang buat battle"}]
             
mainshop = [{"name":"Kapak","price":15000,"deskripsi":"Alat untuk menebang pohon","kategori":"normal","ketahanan":40},
            {"name":"Sekop","price":20000,"deskripsi":"Alat untuk menggali","kategori":"normal","ketahanan":50},
            {"name":"Tiket","price":7500,"deskripsi":"Tiket untuk lotre","kategori":"normal","ketahanan":0}]

@client.command(aliases = ['memes'], description = "Command untuk melihat meme yang diposting di Reddit, ( Kamu bisa kustom subreddit dengan menulis subreddit yang ingin di lihat )", category = "Config")
async def meme(ctx,meme="indonesia"):
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
            await interaction.response.send_message("Oy! Jangan tekan punya orang", ephemeral=True)
            return False
        else:
            return True

@client.command(aliases = ['bt'], description = "Command untuk bertarung!", category = "Economy")
async def battle(ctx):
    await open_account(ctx.author)
    users = await get_bank_data()
    user = ctx.author

    bal = await update_bank(ctx.author)
    polisi = await update_bank(ctx.author)

    stam = users[str(user.id)]["stamina"]
    if stam < 30:
        await ctx.send("Stamina mu tidak cukup untuk bertarung, perlu 30 stamina untuk battle.")
        
    proseskerja = users[str(user.id)]["proseskerja"]
    if proseskerja==1:
        await ctx.send(f"**{ctx.author.name}**, Anda sedang bekerja, mohon tunggu sampai anda selesai bekerja!")
        return
    proseshack = users[str(user.id)]["prosesrampok"]
    if proseshack==1:
        await ctx.send(f"**{ctx.author.name}**, Anda sedang merampok, mohon tunggu sampai anda selesai merampok!")
        return
    prosespenjara = users[str(user.id)]["prosespenjara"]
    if prosespenjara==1:
        await ctx.send(f"**{ctx.author.name}**, Anda sedang dalam penjara, mohon tunggu sampai anda dibebaskan!")
        return

    prosesngemis = users[str(user.id)]["prosesngemis"]
    if prosesngemis==1:
        await ctx.send(f"**{ctx.author.name}**, Anda sedang mengemis, mohon tunggu sampai anda selesai mengemis!")
        return         

    enemy = ["Uzumaki Naruto","Uzumaki Kushina","Namikaze Minato","Uchiha Madara","Uchiha Obito","Uchiha Sasuke","Uchiha Itachi","Might Guy","Hatake Kakashi","Uzumaki Boruto","Haruno Sakura","Uchiha Sarada","Orochimaru","Jiraiya","Senju Tsunade","Hyuuga Hinata","Yamanaka Ino","Akimichi Choji","Nara Shikamaru","Inuzuka Kiba","Sai","Aburame Shino","Hyuuga Neji","Sarutobi Asuma","Akimichi ChoCho","Rock Lee","Tenten","Temari","Yakushi Kabuto","Akimichi Choza","Yuhi Kurenai","Kankuro","Sarutobi Konohamaru","Gaara","Sarutobi Hiruzen"]
    
    en = random.choice(enemy)
    
    users[str(user.id)]["enemyname"] = en
    with open("mainbank.json","w") as f:
        json.dump(users,f,indent=4)

    en = users[str(user.id)]["enemyname"]
    ehp = users[str(user.id)]["enemyhp"]
    esh = users[str(user.id)]["enemysh"]
    etk = users[str(user.id)]["enemytk"]
    esp = users[str(user.id)]["enemysp"]
    
    uhp = users[str(user.id)]["health"]
    ush = users[str(user.id)]["shield"]
    utk = users[str(user.id)]["damage"]
    usp = users[str(user.id)]["speed"]
    
    em = discord.Embed(title = en, color = discord.Color.red())
    em.add_field(name = "Enemy Health", value = f"Health : {ehp}")
    em.add_field(name = "Enemy Shield", value = f"Shield : {esh}")
    em.add_field(name = "Enemy Damage", value = f"Damage : {etk}")
    em.add_field(name = "Enemy Speed", value = f"Speed : {esp}")
    await ctx.send(embed = em)

    view = BView(ctx)
    await ctx.send(f"Apakah kamu mau melawan {en}?", view = view)
    
async def lawan(ctx):
    await open_account(ctx.author)
    users = await get_bank_data()
    user = ctx.author
    en = users[str(user.id)]["enemyname"]
    esp = users[str(user.id)]["enemysp"]
    etk = users[str(user.id)]["enemytk"]    
    usp = users[str(user.id)]["speed"]
    ehp = users[str(user.id)]["enemyhp"]    
    uhp = users[str(user.id)]["health"]
    users[str(user.id)]["buhp"] = int(uhp)
    users[str(user.id)]["betk"] = int(etk)
    users[str(user.id)]["behp"] = int(ehp)
    users[str(user.id)]["besp"] = int(esp)
    with open("mainbank.json","w") as f:
        json.dump(users,f,indent=4)
        
    if esp > usp:
        em = discord.Embed(title = f"{en} VS {user.name}", color = discord.Color.red())
        em.add_field(name = f"{en} Health :", value = f"{ehp}")
        em.add_field(name = f"{user.name} Health :", value = f"{uhp}")
        em.add_field(name = f"Riwayat Serangan :", value = f"{en} lebih cepat dan mendapat giliran menyerang.")
        em.set_thumbnail(url=user.avatar.url)
        msg = await ctx.send(embed = em)
        await asyncio.sleep(5)
        await eronde(ctx, msg)        
        
    if usp > esp:
        em = discord.Embed(title = f"{en} VS {user.name}", color = discord.Color.red())
        em.add_field(name = f"{en} Health :", value = f"{ehp}")
        em.add_field(name = f"{user.name} Health :", value = f"{uhp}")
        em.add_field(name = f"Riwayat Serangan :", value = f"{user.name} lebih cepat dan mendapat giliran menyerang.")
        em.set_thumbnail(url=user.avatar.url)
        msg = await ctx.send(embed = em)
        await asyncio.sleep(5)
        await uronde(ctx, msg)
        
async def eronde(ctx, msg):
    await open_account(ctx.author)
    users = await get_bank_data()
    user = ctx.author
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
    em.add_field(name = f"{en} Health :", value = f"{ehp}")
    em.add_field(name = f"{user.name} Health :", value = f"{uhp}")
    em.set_thumbnail(url=user.avatar.url)
    em.add_field(name = f"Riwayat Serangan :", value = f"{en} menyerang {user.name} dan menimbulkan {reatk} Damage!")
    msg = await msg.edit(embed = em)
    await asyncio.sleep(4)
    if uhp < 1:
        em = discord.Embed(title = "Hasil Pertandingan",description = f"Maaf, {user.name} anda kalah dalam pertandingan")
        expd = random.randrange(10, 20)
        expd = int(expd)
        em.set_footer(text = f"Stamina -30 | Exp +{expd}")
        await ctx.send(embed = em)
        await asyncio.sleep(2)
        await mati(ctx)
        users[str(user.id)]["enemyhp"] = behp
        users[str(user.id)]["enemytk"] = betk
        users[str(user.id)]["enemysp"] = besp
        users[str(user.id)]["stamina"] -= 30
        users[str(user.id)]["exp"] += expd
        with open("mainbank.json","w") as f:
            json.dump(users,f,indent=4)
        return
    await uronde(ctx, msg)
    
async def mati(ctx):
    users = await get_bank_data()
    user = ctx.author
    
    await ctx.send("~{ctx.author.name} pingsan dan tidak sadarkan diri, kamu terbangun di rumah sakit dan membayar biaya perawatan sebesar Rp.20000!~")
    users[str(user.id)]["wallet"] -= 20000
    mh = users[str(user.id)]["maxhealth"]
    mh = int(mh)
    users[str(user.id)]["health"] = mh
    
async def uronde(ctx, msg):
    await open_account(ctx.author)
    users = await get_bank_data()
    user = ctx.author
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
    em.add_field(name = f"{en} Health :", value = f"{ehp}")
    em.add_field(name = f"{user.name} Health :", value = f"{uhp}")
    em.set_thumbnail(url=user.avatar.url)
    em.add_field(name = f"Riwayat Serangan :", value = f"{user.name} menyerang {en} dan menimbulkan {ruatk} Damage!")
    msg = await msg.edit(embed = em)
    await asyncio.sleep(4)
    if ehp < 1:
        expd = random.randrange(20, 40)
        expd = int(expd)
        earnings = random.randrange(55000, 71000)
        earnings = int(earnings)
        em = discord.Embed(title = "Hasil Pertandingan",description = f"Selamat, {user.name} anda menang dalam pertandingan")
        em.set_footer(text = f"Uang +{earnings} | Stamina -30 | Exp +{expd}")
        await ctx.send(embed = em)
        users[str(user.id)]["stamina"] -= 30
        users[str(user.id)]["exp"] += expd
        users[str(user.id)]["wallet"] += earnings
        behp = int(behp) * 1.5
        betk = int(betk) * 1.5
        besp = int(besp) * 1.5
        behp = int(behp)
        betk = int(betk)
        besp = int(besp)
        users[str(user.id)]["enemyhp"] = behp
        users[str(user.id)]["enemytk"] = betk
        users[str(user.id)]["enemysp"] = besp
        with open("mainbank.json","w") as f:
            json.dump(users,f,indent=4)
        return
    await eronde(ctx, msg)

@client.command(aliases = ['pakai','pasang'], description = "Command untuk memakai armor yang sudah kamu beli, unequip / lepas untuk melepas armor yang sudah dipakai", category = "Economy")
async def equip(ctx,item_name):
    await open_account(ctx.author)
    users = await get_bank_data()
    user = ctx.author

    polisi = await update_bank(ctx.author)


    proseskerja = users[str(user.id)]["proseskerja"]
    if proseskerja==1:
        await ctx.send(f"**{ctx.author.name}**, Anda sedang bekerja, mohon tunggu sampai anda selesai bekerja!")
        return
    proseshack = users[str(user.id)]["prosesrampok"]
    if proseshack==1:
        await ctx.send(f"**{ctx.author.name}**, Anda sedang merampok, mohon tunggu sampai anda selesai merampok!")
        return
    prosespenjara = users[str(user.id)]["prosespenjara"]
    if prosespenjara==1:
        await ctx.send(f"**{ctx.author.name}**, Anda sedang dalam penjara, mohon tunggu sampai anda dibebaskan!")
        return

    prosesngemis = users[str(user.id)]["prosesngemis"]
    if prosesngemis==1:
        await ctx.send(f"**{ctx.author.name}**, Anda sedang mengemis, mohon tunggu sampai anda selesai mengemis!")
        return

    item_name = item_name.lower()
    name_ = None
    try:
        bag = users[str(user.id)]["bag"]
    except:
        bag = []
    for item in bag:
        name = item["item"].lower()
        if name == item_name:
            name_ = name
            category = item["kategori"]
            break

    if name_ == None:
        await ctx.send(f"Kamu tidak punya {item_name}.")
        return
        
    if category == "food":
        await ctx.send("Kamu tidak bisa memakai makanan, makanan kan buat di makan :/")
        return

    if category == "sword":
        res = await equip_sword(ctx.author,item_name)

        if not res[0]:
            if res[1]==1:
                await ctx.send("Kamu sedang memakai item lain, lepaslah item lain terlebih dahulu!")
                return
            if res[1]==2:
                await ctx.send(f"Kamu tidak punya 1 {item_name} di tasmu!")
                return
            if res[1]==3:
                await ctx.send(f"Kamu tidak punya {item_name} di tas mu!")
                return
        
    if category == "armor":
        res = await equip_armor(ctx.author,item_name)

        if not res[0]:
            if res[1]==1:
                await ctx.send("Kamu sedang memakai item lain, lepaslah item lain terlebih dahulu!")
                return
            if res[1]==2:
                await ctx.send(f"Kamu tidak punya 1 {item_name} di tasmu!")
                return
            if res[1]==3:
                await ctx.send(f"Kamu tidak punya {item_name} di tas mu!")
                return

    await ctx.send(f"Kamu berhasil memakai {item_name}.")

async def equip_sword(user,item_name):
    item_name = item_name.lower()
    name_ = None
    try:
        bag = users[str(user.id)]["bag"]
    except:
        bag = []
    for item in bag:
        name = item["item"].lower()
        damage = item["damage"]
        if name == item_name:
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
            n = thing["item"]
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
    users[str(user.id)]["sword"] = item_name.lower()
    users[str(user.id)]["dmgsword"] = damage
    with open("armor.json","w") as f:
        json.dump(users,f,indent=4)
    users = await get_bank_data()
    users[str(user.id)]["damage"] += damage
    with open("mainbank.json","w") as f:
        json.dump(users,f,indent=4)

    return [True,"Worked"]
    
async def equip_armor(user,item_name):
    item_name = item_name.lower()
    name_ = None
    try:
        bag = users[str(user.id)]["bag"]
    except:
        bag = []
    for item in bag:
        name = item["item"].lower()
        bagian = item["bagian"]
        bonushp = item["bonushp"]
        if name == item_name:
            name_ = name
            break

    users = await get_armor_data()
    bal = await update_bank(user)
    armor = users[str(user.id)][bagian]

    if armor != "nothing":
        return [False,1]

    users = await get_bank_data()
    
    try:
        index = 0
        t = None
        for thing in users[str(user.id)]["bag"]:
            n = thing["item"]
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
    users[str(user.id)][bagian] = item_name.lower()
    users[str(user.id)][f"hp{bagian}"] = bonushp
    with open("armor.json","w") as f:
        json.dump(users,f,indent=4)
    users = await get_bank_data()
    users[str(user.id)]["maxhealth"] += bonushp
    with open("mainbank.json","w") as f:
        json.dump(users,f,indent=4)

    return [True,"Worked"]    

@client.command(aliases = ['lepas'], description = "Command untuk melepas armor yang sudah kamu pasang, equip / pakai / pasang untuk memakai armor yang sudah dilepas", category = "Economy")
async def unequip(ctx,item_name):
    await open_account(ctx.author)
    users = await get_bank_data()
    user = ctx.author

    polisi = await update_bank(ctx.author)


    proseskerja = users[str(user.id)]["proseskerja"]
    if proseskerja==1:
        await ctx.send(f"**{ctx.author.name}**, Anda sedang bekerja, mohon tunggu sampai anda selesai bekerja!")
        return
    proseshack = users[str(user.id)]["prosesrampok"]
    if proseshack==1:
        await ctx.send(f"**{ctx.author.name}**, Anda sedang merampok, mohon tunggu sampai anda selesai merampok!")
        return
    prosespenjara = users[str(user.id)]["prosespenjara"]
    if prosespenjara==1:
        await ctx.send(f"**{ctx.author.name}**, Anda sedang dalam penjara, mohon tunggu sampai anda dibebaskan!")
        return

    prosesngemis = users[str(user.id)]["prosesngemis"]
    if prosesngemis==1:
        await ctx.send(f"**{ctx.author.name}**, Anda sedang mengemis, mohon tunggu sampai anda selesai mengemis!")
        return

    item_name = item_name.lower()
    try:
        bag = users[str(user.id)]["bag"]
    except:
        bag = []
    name_ = None
    for item in bag:
        name = item["item"].lower()
        if name == item_name:
            category = item["kategori"]
            name_ = name
            break

    if name_ == None:
        await ctx.send("Kamu sedang tidak memakai {item_name}.")
        return

    if category == "food":
        await ctx.send("Kamu sedang tidak memakai {item_name}.")
        return

    if category == "sword":
        res = await unequip_sword(ctx.author,item_name)

        if not res[0]:
            if res[1]==1:
                await ctx.send("Kamu tidak sedang memakai {item_name}.")
                return
        
    if category == "armor":
        res = await unequip_armor(ctx.author,item_name)

        if not res[0]:
            if res[1]==1:
                await ctx.send("Kamu tidak sedang memakai {item_name}.")
                return

    await ctx.send(f"Kamu berhasil melepas {item_name}.")

async def unequip_sword(user,item_name):
    item_name = item_name.lower()
    name_ = None
    try:
        bag = users[str(user.id)]["bag"]
    except:
        bag = []
    for item in bag:
        name = item["name"].lower()
        if name == item_name:
            name_ = name
            price = item["price"]
            damage = item["damage"]
            kategori = item["kategori"]
            break
        
    users = await get_armor_data()
    sword = users[str(user.id)]["sword"]
    if sword != item_name.lower():
        return [False,1]
                    
    users = await get_bank_data()       
    bal = await update_bank(user)            
            
    try:
        index = 0
        t = None
        for thing in users[str(user.id)]["bag"]:
            n = thing["item"]
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
    item_name = item_name.lower()
    name_ = None
    try:
        bag = users[str(user.id)]["bag"]
    except:
        bag = []
    for item in bag:
        name = item["item"].lower()
        if name == item_name:
            name_ = name
            bagian = item["bagian"]
            bonushp = item["bonushp"]
            price = item["price"]
            kategori = item["kategori"]
            break

    users = await get_armor_data()
    equip = users[str(user.id)][bagian]
    if equip != item_name.lower():
        return [False,1]
                    
    users = await get_bank_data()       
    bal = await update_bank(user)            
            
    try:
        index = 0
        t = None
        for thing in users[str(user.id)]["bag"]:
            n = thing["item"]
            if n == item_name:
                old_amt = thing["amount"]
                new_amt = old_amt + 1
                users[str(user.id)]["bag"][index]["amount"] = new_amt
                t = 1
                break
            index+=1
        if t == None:
            obj = {"item":item_name , "amount" : amount , "bagian":bagian , "bonushp":bonushp, "price":0.9*price, "kategori":kategori}
            users[str(user.id)]["bag"].append(obj)
    except:
        obj = obj = {"item":item_name , "amount" : amount , "bagian":bagian , "bonushp":bonushp, "price":0.9*price, "kategori":kategori}
        users[str(user.id)]["bag"] = [obj]

    with open("mainbank.json","w") as f:
        json.dump(users,f,indent=4)
    users = await get_armor_data()
    users[str(user.id)][category] = "nothing"
    users[str(user.id)][f"hp{category}"] = 0
    with open("armor.json","w") as f:
        json.dump(users,f,indent=4)
                       
    users = await get_bank_data()
    users[str(user.id)]["maxhealth"] -= bonushp
    with open("mainbank.json","w") as f:
        json.dump(users,f,indent=4)      
             
    return [True,"Worked"]

@client.command(aliases = ['armor','sword','avatar','eq','perlengkapan'], description = "Command untuk mengecek armor yang dipakai", category = "Economy")
async def equipment(ctx, user:discord.Member = None):
    if user == None:
        user = ctx.author

    await open_armor(user)
    users = await get_armor_data()   
    helmet = users[str(user.id)]["helmets"]
    chestplate = users[str(user.id)]["chestplates"]
    legging = users[str(user.id)]["leggings"]
    boot = users[str(user.id)]["boots"]
    sword = users[str(user.id)]["sword"]    
    hph = users[str(user.id)]["hphelmets"]
    hpc = users[str(user.id)]["hpchestplates"]
    hpl = users[str(user.id)]["hpleggings"]
    hpb = users[str(user.id)]["hpboots"]
    dsword = users[str(user.id)]["dmgsword"]
    thp = int(hph)+int(hpc)+int(hpl)+int(hpb)
    
    em = discord.Embed(title = f"**Equipment {user.name}**",color = discord.Color.red())
    em.add_field(name = "**Helmet**",value = f"{helmet}, Max <​:health:922441419166212177>HP +{hph}")
    em.add_field(name = "**Chestplate**",value = f"{chestplate}, Max <​:health:922441419166212177>HP +{hpc}")
    em.add_field(name = "**Leggings**",value = f"{legging}, Max <​:health:922441419166212177>HP +{hpl}")
    em.add_field(name = "**Boots**",value = f"{boot}, Max <​:health:922441419166212177>HP +{hpb}")
    em.add_field(name = "**Sword**", value = f"{sword}, Damage +{dsword}")
    em.add_field(name = "**Total HP**",value = f"Bonus Max HP Seluruh Armor = {thp}")
    await ctx.send(embed = em)
    
@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"Command Cooldown!, mohon tunggu {error.retry_after:.2f} detik sampai limit mu direset!.")

@tasks.loop(seconds=90)
async def staminaup():
    users = await get_bank_data()
    for user in users:
        name = int(user)
        if users[user]["stamina"] >= users[user]["mstamina"]:
             return
        users[user]["stamina"] += 1
        with open("mainbank.json","w") as f:
            json.dump(users,f,indent=4)

@client.command(aliases = ['duit','bal','balance'], description = "Command untuk mengecek uang", category = "Economy")
async def uang(ctx, user:discord.Member = None):
    if user == None:
        user = ctx.author
    await open_account(user)
    users = await get_bank_data()    
    dompet = users[str(user.id)]["wallet"]
    bank = users[str(user.id)]["bank"]
    tiket = users[str(user.id)]["ticket"]
    
    em = discord.Embed(title = f"Informasi Uang {user.name}",color = discord.Color.red())
    em.add_field(name = "<​:rupiah:920954420617941032>Uang Dompet",value = dompet)
    em.add_field(name = "<​:rupiah:920954420617941032>Saldo Bank",value = bank)
    em.add_field(name = "<​:tiket:922432835288195152>Ticket Lotre",value = tiket)
    await ctx.send(embed = em)
    
@client.command(description = "Command untuk mengecek info akun", category = "Economy")
async def info(ctx, user:discord.Member = None):
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
    
    em = discord.Embed(title = f"Informasi Akun **{user.name}**",color = discord.Color.red())
    em.add_field(name = "<​:health:922441419166212177>Health",value = f"{health} / {mhealth}")
    em.add_field(name = "<​:damage:922440838699712542>Damage",value = f"{damage}")
    em.add_field(name = "<​:level:922439376552734820>Level",value = f"{level}")
    em.add_field(name = "<​:exp:922433918613991465>Exp",value = f"{exp} / {mexp}")
    em.add_field(name = "<​:rupiah:920954420617941032>Uang Dompet",value = dompet)
    em.add_field(name = "<​:rupiah:920954420617941032>Saldo Bank",value = bank)
    em.add_field(name = "<​:tiket:922432835288195152>Ticket Gacha",value = tiket)
    em.add_field(name = "<​:stamina:922441479861968928>Stamina",value = f"{stamina} / {mstam}")
    await ctx.send(embed = em)

@client.command(aliases = ['beg'], description = "Command untuk ngemis, bisa gagal dan berhasil, tidak berbahaya", category = "Economy")
async def ngemis(ctx):
    await open_account(ctx.author)
    user = ctx.author
    users = await get_bank_data()
    polisi = await update_bank(ctx.author)
    bal = await update_bank(ctx.author)


    proseskerja = users[str(user.id)]["proseskerja"]
    if proseskerja==1:
        await ctx.send(f"**{ctx.author.name}**, Anda sedang bekerja, mohon tunggu sampai anda selesai bekerja!")
        return
    proseshack = users[str(user.id)]["prosesrampok"]
    if proseshack==1:
        await ctx.send(f"**{ctx.author.name}**, Anda sedang merampok, mohon tunggu sampai anda selesai merampok!")
        return
    prosespenjara = users[str(user.id)]["prosespenjara"]
    if prosespenjara==1:
        await ctx.send(f"**{ctx.author.name}**, Anda sedang dalam penjara, mohon tunggu sampai anda dibebaskan!")
        return

    prosesngemis = users[str(user.id)]["prosesngemis"]
    if prosesngemis==1:
        await ctx.send(f"**{ctx.author.name}**, Anda sedang mengemis, mohon tunggu sampai anda selesai mengemis!")
        return
    if bal[3]<5:
        await ctx.send(f"**{ctx.author.name}**, Anda harus mempunyai 5 Stamina atau lebih untuk mengemis!")
        return
    
    ngemis = 6
    await ctx.send(f"Sedang mengemis... Mohon tunggu {ngemis} detik!")
    users[str(user.id)]["prosesngemis"] = 1
    with open("mainbank.json","w") as f:
        json.dump(users,f,indent=4)
    await asyncio.sleep(ngemis)
    kois = [1,2,3]
    bisa = random.choice(kois)
    print(bisa)

    if bisa == 3:
        gagaltext = ["Pengemis gila, sana pergi, jijik gua!","Kasian masih muda jadi pengemis hiuh!","Apaan luh, orang gila!"]
        gagalorang = ["Makiy Suzzuron","Wibey Tezy","Hangker Bakellas"]
        text = random.choice(gagaltext)
        orang = random.choice(gagalorang)
        
        em = discord.Embed(title = orang, description = text)
        gambar = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTNHFQM-QRF-H6Mc4E7CBfueV4NbEn5icna-g&usqp=CAU"
        em.set_image(url=gambar)
        em.set_footer(text = "Kamu gagal ngemis :(")
        await ctx.send(embed = em)
        users[str(user.id)]["prosesngemis"] = 0
        users[str(user.id)]["stamina"] -= 5
        with open("mainbank.json","w") as f:
            json.dump(users,f,indent=4)
        return

    if bisa == 2:
        gagaltext = ["Duit gw lg dikit sih, nih gw kasih tiket aja ya","Watashi sedang tidak ada duit","Dunia Sementara Mobile Legend Sementara!!!"]
        earnings = random.randrange(1, 2)
        earnings = int(earnings)
        gagalorang = ["Jasuke Muchiha","Mama Lemon","Paskol Punjabi-tan"]
        text = random.choice(gagaltext)
        orang = random.choice(gagalorang)
        
        em = discord.Embed(title = orang, description = text)
        gambar = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRGCZEZhHeMTv9463yhxaQJbGcGtiwCidOOCg&usqp=CAU"
        em.set_image(url=gambar)
        em.set_footer(text = f"Kamu berhasil ngemis dan mendapat {earnings} Tiket, <​:exp:922433918613991465>Exp +10!")
        await ctx.send(embed = em)
        users[str(user.id)]["ticket"] += earnings
        users[str(user.id)]["prosesngemis"] = 0
        users[str(user.id)]["stamina"] -= 5    
        users[str(user.id)]["exp"] += 10 
        with open("mainbank.json","w") as f:
            json.dump(users,f,indent=4)
        res = await uplevel(ctx.author)
    
        if not res[0]:
            if res[1]==1:
                return

        await ctx.send(f"**{ctx.author.name}**, Kamu naik level!")
        return

    if bisa == 1:
        gagaltext = ["Kasian banget, nih gua kasih","Nih, tapi kalau masih sehat jangan ngemis karena itu tidak baik :)","Haha Well Played Bro!"]
        earnings = random.randrange(10000)
        earnings = int(earnings)
        gagalorang = ["Sunarto Suzumaki","Mama Lia","Gaybal"]
        text = random.choice(gagaltext)
        orang = random.choice(gagalorang)
        
        em = discord.Embed(title = orang, description = text)
        gambar = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRGCZEZhHeMTv9463yhxaQJbGcGtiwCidOOCg&usqp=CAU"
        em.set_image(url=gambar)
        em.set_footer(text = f"Kamu berhasil ngemis dan mendapat <​:rupiah:920954420617941032>Rp.{earnings}, <​:exp:922433918613991465>Exp +10!")
        await ctx.send(embed = em)
        users[str(user.id)]["wallet"] += earnings
        users[str(user.id)]["prosesngemis"] = 0
        users[str(user.id)]["stamina"] -= 5
        users[str(user.id)]["exp"] += 10 
        with open("mainbank.json","w") as f:
            json.dump(users,f,indent=4)
        res = await uplevel(ctx.author)
    
        if not res[0]:
            if res[1]==1:
                return

        await ctx.send(f"**{ctx.author.name}**, Kamu naik level!")
        return   
        
@client.command(aliases = ['work'], description = "Command untuk bekerja", category = "Economy")
async def kerja(ctx):
    await open_account(ctx.author)
    user = ctx.author
    users = await get_bank_data()
    polisi = await update_bank(ctx.author)
    bal = await update_bank(ctx.author)


    proseskerja = users[str(user.id)]["proseskerja"]
    if proseskerja==1:
        await ctx.send(f"**{ctx.author.name}**, Anda sedang bekerja, mohon tunggu sampai anda selesai bekerja!")
        return
    proseshack = users[str(user.id)]["prosesrampok"]
    if proseshack==1:
        await ctx.send(f"**{ctx.author.name}**, Anda sedang merampok, mohon tunggu sampai anda selesai merampok!")
        return
    prosespenjara = users[str(user.id)]["prosespenjara"]
    if prosespenjara==1:
        await ctx.send(f"**{ctx.author.name}**, Anda sedang dalam penjara, mohon tunggu sampai anda dibebaskan!")
        return

    prosesngemis = users[str(user.id)]["prosesngemis"]
    if prosesngemis==1:
        await ctx.send(f"**{ctx.author.name}**, Anda sedang mengemis, mohon tunggu sampai anda selesai mengemis!")
        return

    if bal[3]<5:
        await ctx.send(f"**{ctx.author.name}**, Anda harus mempunyai 5 Stamina atau lebih untuk mengemis!")
        return

    earnings = random.randrange(25000, 30000)
    earnings = int(earnings)
    
    defkerja = 60
    minstam = 10
    kekuatan = users[str(user.id)]["kekuatan"]
    kerja = defkerja/kekuatan
    plusexp = 20
    
    await ctx.send(f"**{ctx.author.name}**, Kamu sedang bekerja, Mohon tunggu {kerja} detik!")
    users[str(user.id)]["proseskerja"] = 1
    with open("mainbank.json","w") as f:
        json.dump(users,f,indent=4)
    await asyncio.sleep(kerja)
    em = discord.Embed(title = "Berhasil Kerja!")
    gambar = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRGCZEZhHeMTv9463yhxaQJbGcGtiwCidOOCg&usqp=CAU"
    em.set_image(url=gambar)
    em.set_footer(text = f"Kamu berhasil bekerja dan digaji <​:rupiah:920954420617941032>Rp.{earnings}, <​:exp:922433918613991465>Exp +20, <​:stamina:922441479861968928>Stamina -10!")
    await ctx.send(embed = em)
    users[str(user.id)]["proseskerja"] = 0
    with open("mainbank.json","w") as f:
        json.dump(users,f,indent=4)
    await update_bank(ctx.author,-1*minstam,"stamina")
    await update_bank(ctx.author,+1*earnings)
    await update_bank(ctx.author,+1*plusexp,"exp")
    res = await uplevel(ctx.author)
    
    if not res[0]:
        if res[1]==1:
            return

    await ctx.send(f"**{ctx.author.name}**, Kamu naik level!")
  
async def uplevel(user):
    users = await get_bank_data()
    bal = await update_bank(user)
    
    reqexp = users[str(user.id)]["mexp"]
    if bal[7]<bal[8]:
        return [False,1]

    exp = users[str(user.id)]["exp"]
    mexp = users[str(user.id)]["mexp"]
    pluslevel = 1
    plusmexp = mexp*0.5
    plusmstam = 5
    level = users[str(user.id)]["level"]
    await update_bank(ctx.author,-1*mexp,"exp")
    await update_bank(ctx.author,+1*plusmexp,"mexp")
    await update_bank(ctx.author,+1*pluslevel,"level")
    await update_bank(ctx.author,+1*plusmstam,"mstamina")
    nlevel = int(level) + 1
    await ctx.send(f"Kamu naik level {nlevel}!")
    return [True,"Worked"]
   
@client.command(aliases = ['withdraw','wd'], description = "Command untuk menarik saldo bank", category = "Economy")
async def tarikbank(ctx,amount = None):
    await open_account(ctx.author)
    users = await get_bank_data()
    user = ctx.author
    polisi = await update_bank(ctx.author)


    proseskerja = users[str(user.id)]["proseskerja"]
    if proseskerja==1:
        await ctx.send(f"**{ctx.author.name}**, Anda sedang bekerja, mohon tunggu sampai anda selesai bekerja!")
        return
    proseshack = users[str(user.id)]["prosesrampok"]
    if proseshack==1:
        await ctx.send(f"**{ctx.author.name}**, Anda sedang merampok, mohon tunggu sampai anda selesai merampok!")
        return
    prosespenjara = users[str(user.id)]["prosespenjara"]
    if prosespenjara==1:
        await ctx.send(f"**{ctx.author.name}**, Anda sedang dalam penjara, mohon tunggu sampai anda dibebaskan!")
        return

    prosesngemis = users[str(user.id)]["prosesngemis"]
    if prosesngemis==1:
        await ctx.send(f"**{ctx.author.name}**, Anda sedang mengemis, mohon tunggu sampai anda selesai mengemis!")
        return

    if amount == None:
        await ctx.reply("Tolong tulis nominal Saldo Bank yang ingin di withdraw.")
        return
    
    bal = await update_bank(ctx.author)
    if amount == "all":
        amount = bal[1]
        
    if amount == "max":
        amount = bal[1]
        
    amount = int(amount)
    if amount>bal[1]:
        await ctx.reply("Kamu tidak memiliki Rp.{amount} di Bankmu.")
        return
    if amount<1:
        await ctx.reply("Saldo Bank yang ingin diwithdraw harus lebih dari 0.")
        return

    await update_bank(ctx.author,amount)
    await update_bank(ctx.author,-1*amount,"bank")
    
    await ctx.reply(f"Anda berhasil withdraw Rp.{amount} ke Akun Bankmu.")

@client.command(aliases = ['deposit','dep','depo'], description = "Command untuk mendeposit uang ke bank", category = "Economy")
async def isibank(ctx,amount = None):
    await open_account(ctx.author)
    users = await get_bank_data()
    user = ctx.author
    polisi = await update_bank(ctx.author)


    proseskerja = users[str(user.id)]["proseskerja"]
    if proseskerja==1:
        await ctx.send(f"**{ctx.author.name}**, Anda sedang bekerja, mohon tunggu sampai anda selesai bekerja!")
        return
    proseshack = users[str(user.id)]["prosesrampok"]
    if proseshack==1:
        await ctx.send(f"**{ctx.author.name}**, Anda sedang merampok, mohon tunggu sampai anda selesai merampok!")
        return
    prosespenjara = users[str(user.id)]["prosespenjara"]
    if prosespenjara==1:
        await ctx.send(f"**{ctx.author.name}**, Anda sedang dalam penjara, mohon tunggu sampai anda dibebaskan!")
        return

    prosesngemis = users[str(user.id)]["prosesngemis"]
    if prosesngemis==1:
        await ctx.send(f"**{ctx.author.name}**, Anda sedang mengemis, mohon tunggu sampai anda selesai mengemis!")
        return

    if amount == None:
        await ctx.reply("Tolong tulis nominal uang yang ingin di deposit ke Bank.")
        return
    
    bal = await update_bank(ctx.author)
    if amount == "all":
        amount = bal[0]
        
    if amount == "max":
        amount = bal[0]
    
    amount = int(amount)
    if amount>bal[0]:
        await ctx.reply("Kamu tidak memiliki Rp.{amount} di dompetmu.")
        return
    if amount<1:
        await ctx.reply("Uang yang ingin di deposit harus lebih dari 0.")
        return

    await update_bank(ctx.author,-1*amount)
    await update_bank(ctx.author,amount,"bank")
    
    await ctx.reply(f"Anda berhasil deposit Rp.{amount} ke Akun Bankmu.")
    
    
@client.command(aliases = ['kasih','give','tf','kirim'], description = "Command untuk mentransfer saldo bank ke player lain ( lewat mention )", category = "Economy")
async def transfer(ctx,member:discord.Member,amount = None):
    await open_account(ctx.author)
    await open_account(member)
    users = await get_bank_data()
    user = ctx.author
    polisi = await update_bank(ctx.author)


    proseskerja = users[str(user.id)]["proseskerja"]
    if proseskerja==1:
        await ctx.send(f"**{ctx.author.name}**, Anda sedang bekerja, mohon tunggu sampai anda selesai bekerja!")
        return
    proseshack = users[str(user.id)]["prosesrampok"]
    if proseshack==1:
        await ctx.send(f"**{ctx.author.name}**, Anda sedang merampok, mohon tunggu sampai anda selesai merampok!")
        return
    prosespenjara = users[str(user.id)]["prosespenjara"]
    if prosespenjara==1:
        await ctx.send(f"**{ctx.author.name}**, Anda sedang dalam penjara, mohon tunggu sampai anda dibebaskan!")
        return

    prosesngemis = users[str(user.id)]["prosesngemis"]
    if prosesngemis==1:
        await ctx.send(f"**{ctx.author.name}**, Anda sedang mengemis, mohon tunggu sampai anda selesai mengemis!")
        return
    
    if amount == None:
        await ctx.reply("Tolong tulis jumlah uang yang ingin di kirim!")
        return
    
    bal = await update_bank(ctx.author)
    if amount == "all":
        amount = bal[0]
        
    if amount == "max":
        amount = bal[0]
    
    amount = int(amount)
    if amount>bal[1]:
        await ctx.reply("Kamu tidak memiliki Rp.{amount} di Bank mu.")
        return
    if amount<1:
        await ctx.reply("Saldo yang ingin ditransfer harus melebihi 0!")
        return

    await update_bank(ctx.author,-1*amount,"bank")
    await update_bank(member,amount,"bank")
    
    await ctx.reply(f"Kamu berhasil memberi {member.name} Rp.{amount}.")
    
@client.command(aliases = ['kasihtiket','kasihticket','kirimtiket','givetiket','kirimticket'], description = "Command untuk memberi tiket lotre ke player lain ( lewat mention )", category = "Economy")
async def giveticket(ctx,member:discord.Member,amount = None):
    await open_account(ctx.author)
    await open_account(member)
    users = await get_bank_data()
    user = ctx.author
    polisi = await update_bank(ctx.author)


    proseskerja = users[str(user.id)]["proseskerja"]
    if proseskerja==1:
        await ctx.send(f"**{ctx.author.name}**, Anda sedang bekerja, mohon tunggu sampai anda selesai bekerja!")
        return
    proseshack = users[str(user.id)]["prosesrampok"]
    if proseshack==1:
        await ctx.send(f"**{ctx.author.name}**, Anda sedang merampok, mohon tunggu sampai anda selesai merampok!")
        return
    prosespenjara = users[str(user.id)]["prosespenjara"]
    if prosespenjara==1:
        await ctx.send(f"**{ctx.author.name}**, Anda sedang dalam penjara, mohon tunggu sampai anda dibebaskan!")
        return

    prosesngemis = users[str(user.id)]["prosesngemis"]
    if prosesngemis==1:
        await ctx.send(f"**{ctx.author.name}**, Anda sedang mengemis, mohon tunggu sampai anda selesai mengemis!")
        return
    
    bal = await update_bank(ctx.author)
    if amount == "all":
        amount = bal[2]
        
    if amount == "max":
        amount = bal[2]
    
    amount = int(amount)
    if amount>bal[1]:
        await ctx.reply(f"Kamu tidak memiliki {amount} Tiket!")
        return
    if amount<1:
        await ctx.reply("Tiket yg dikirim harus lebih dari 0!")
        return

    await update_bank(ctx.author,-1*amount,"ticket")
    await update_bank(member,amount,"ticket")
    
    await ctx.reply(f"Kamu berhasil memberi {member.name} {amount} Tiket.")
    
@client.command(aliases = ['rampokbank','bobolbank','rampok'], description = "Command untuk merampok bank, kamu akan ditangkap jika melakukannya dengan berlebihan", category = "Economy")
async def bankrob(ctx):
    await open_account(ctx.author)
    users = await get_bank_data()
    user = ctx.author
    bal = await update_bank(ctx.author)
    polisi = await update_bank(ctx.author)
    earnings = random.randrange(40000, 50000)
    earnings = int(earnings)
    jahat = earnings*0.0001
    jahat = int(jahat)
    oldjahat = users[str(user.id)]["kejahatan"]
    newjahat = jahat+oldjahat
    
    proseskerja = users[str(user.id)]["proseskerja"]
    if proseskerja==1:
        await ctx.send(f"**{ctx.author.name}**, Anda sedang bekerja, mohon tunggu sampai anda selesai bekerja!")
        return
    proseshack = users[str(user.id)]["prosesrampok"]
    if proseshack==1:
        await ctx.send(f"**{ctx.author.name}**, Anda sedang merampok, mohon tunggu sampai anda selesai merampok!")
        return
    prosespenjara = users[str(user.id)]["prosespenjara"]
    if prosespenjara==1:
        await ctx.send(f"**{ctx.author.name}**, Anda sedang dalam penjara, mohon tunggu sampai anda dibebaskan!")
        return

    prosesngemis = users[str(user.id)]["prosesngemis"]
    if prosesngemis==1:
        await ctx.send(f"**{ctx.author.name}**, Anda sedang mengemis, mohon tunggu sampai anda selesai mengemis!")
        return
    proseshack = users[str(user.id)]["prosesrampok"]
    if proseshack==1:
        await ctx.send(f"**{ctx.author.name}**, Anda sedang merampok, mohon tunggu sampai anda selesai merampok!")
        return
    prosespenjara = users[str(user.id)]["prosespenjara"]
    if prosespenjara==1:
        await ctx.send(f"**{ctx.author.name}**, Anda sedang dalam penjara, mohon tunggu sampai anda dibebaskan!")
        return
    
    minstam = 22
    kekuatan = users[str(user.id)]["kekuatan"]
    proses = 90
    hack = kekuatan*proses
    await ctx.send(f"Kamu sedang membobol Bank, mohon tunggu {hack} detik lagi!")
    users[str(user.id)]["prosesrampok"] = 1
    with open("mainbank.json","w") as f:
        json.dump(users,f,indent=4)    
    await asyncio.sleep(hack)
    await ctx.reply(f"Anda berhasil merampok dan mendapat <​:rupiah:920954420617941032>Rp.{earnings}, <​:exp:922433918613991465>Exp +31!")
    users[str(user.id)]["prosesrampok"] = 0
    with open("mainbank.json","w") as f:
        json.dump(users,f,indent=4)   
    await update_bank(ctx.author,+1*jahat,"kejahatan")
    await update_bank(ctx.author,+1*earnings)
    await update_bank(ctx.author,-1*minstam,"stamina")
    await update_bank(ctx.author,-1*31,"exp")
    await uplevel(ctx.author)
    
    if polisi[5]>polisi[6]:
        await penjara(ctx)
        return    
       
@client.command(aliases = ['gacha','lottery'], description = "Command untuk lotre atau gacha, Jika kalah hadiah akan berupa exp, Hanya dapat lotre 5 kali sehari!", category = "Economy")
@commands.cooldown(5, 86400, commands.BucketType.user)
async def lotre(ctx):
    await open_account(ctx.author)
    users = await get_bank_data()
    user = ctx.author
    polisi = await update_bank(ctx.author)


    proseskerja = users[str(user.id)]["proseskerja"]
    if proseskerja==1:
        await ctx.send(f"**{ctx.author.name}**, Anda sedang bekerja, mohon tunggu sampai anda selesai bekerja!")
        return
    proseshack = users[str(user.id)]["prosesrampok"]
    if proseshack==1:
        await ctx.send(f"**{ctx.author.name}**, Anda sedang merampok, mohon tunggu sampai anda selesai merampok!")
        return
    prosespenjara = users[str(user.id)]["prosespenjara"]
    if prosespenjara==1:
        await ctx.send(f"**{ctx.author.name}**, Anda sedang dalam penjara, mohon tunggu sampai anda dibebaskan!")
        return

    prosesngemis = users[str(user.id)]["prosesngemis"]
    if prosesngemis==1:
        await ctx.send(f"**{ctx.author.name}**, Anda sedang mengemis, mohon tunggu sampai anda selesai mengemis!")
        return
    
    bal = await update_bank(ctx.author)
    
    if 1>bal[2]:
        await ctx.reply("Kamu tidak memiliki tiket lotre")
        return

    final = []
    for i in range(3):
        a = random.choice(["🍌","🍊","💵"])
        
        final.append(a)
                
    await ctx.reply(str(final))

    if final[0] == final[1] or final[0] == final[2] or final[2] == final[1]:        
        menang = random.randrange(20000)
        await update_bank(ctx.author,+earnings*1, "wallet")
        await update_bank(ctx.author,-1*amount,"ticket")
        await ctx.reply("Kamu menang, kamu mendapat <​:rupiah:920954420617941032>Rp.{menang}!")
    else:
        dapetexp = random.randrange(50)
        await update_bank(ctx.author,+dapetexp*amount, "bank")
        await update_bank(ctx.author,-1*1,"ticket")
        await ctx.reply(f"Kamu kalah, kamu mendapat {dapetexp} <​:exp:922433918613991465>Exp.")                
        
@client.command(aliases = ['beliticket','buytiket','belitiket'], description = "Command untuk membeli tiket lotre", category = "Economy")
async def buyticket(ctx, amount = 1):
    amount = int(amount)
    await open_account(ctx.author)
    users = await get_bank_data()
    user = ctx.author
    bal = await update_bank(ctx.author)
    harga = 7500
    biaya = amount*harga
        
    if amount < 1:
        await ctx.reply(f"Hmm, anda serius mau membeli {amount} ticket?.")

    if bal[0] < biaya:
        await ctx.reply(f"Uang di dompet anda tidak cukup untuk membeli {amount} tiket lotre, {amount} ticket lotre <​:rupiah:920954420617941032>Rp.{biaya}!")
        return

    polisi = await update_bank(ctx.author)

    proseskerja = users[str(user.id)]["proseskerja"]
    if proseskerja==1:
        await ctx.send(f"**{ctx.author.name}**, Anda sedang bekerja, mohon tunggu sampai anda selesai bekerja!")
        return
    proseshack = users[str(user.id)]["prosesrampok"]
    if proseshack==1:
        await ctx.send(f"**{ctx.author.name}**, Anda sedang merampok, mohon tunggu sampai anda selesai merampok!")
        return
    prosespenjara = users[str(user.id)]["prosespenjara"]
    if prosespenjara==1:
        await ctx.send(f"**{ctx.author.name}**, Anda sedang dalam penjara, mohon tunggu sampai anda dibebaskan!")
        return

    prosesngemis = users[str(user.id)]["prosesngemis"]
    if prosesngemis==1:
        await ctx.send(f"**{ctx.author.name}**, Anda sedang mengemis, mohon tunggu sampai anda selesai mengemis!")
        return
        
    await update_bank(ctx.author,-1*biaya)
    await update_bank(ctx.author,+1*amount,"ticket")    
    await ctx.reply(f"Anda berhasil membeli {amount} <​:tiket:922432835288195152>Ticket")

@client.command(aliases = ['sogok'], description = "Command untuk menyogok polisi ( mengurangi nilai kejahatan )", category = "Economy")
async def sogokpolisi(ctx,amount = 1):
    amount = int(amount)
    await open_account(ctx.author)
    users = await get_bank_data()
    user = ctx.author
    bal = await update_bank(ctx.author)
    biaya = amount*15000

    proseskerja = users[str(user.id)]["proseskerja"]
    if proseskerja==1:
        await ctx.send(f"**{ctx.author.name}**, Anda sedang bekerja, mohon tunggu sampai anda selesai bekerja!")
        return
    proseshack = users[str(user.id)]["prosesrampok"]
    if proseshack==1:
        await ctx.send(f"**{ctx.author.name}**, Anda sedang merampok, mohon tunggu sampai anda selesai merampok!")
        return
    prosespenjara = users[str(user.id)]["prosespenjara"]
    if prosespenjara==1:
        await ctx.send(f"**{ctx.author.name}**, Anda sedang dalam penjara, mohon tunggu sampai anda dibebaskan!")
        return

    prosespenjara = users[str(user.id)]["prosespenjara"]
    if prosespenjara==1:
        await ctx.send(f"**{ctx.author.name}**, Anda sedang dalam penjara, mohon tunggu sampai anda dibebaskan!")
        return


    if bal[0] < biaya:
        await ctx.reply(f"Uang di dompet anda tidak cukup untuk menyogok {amount} Nilai Kejahatan, sogok {amount} Nilai Kejahatan Rp.{biaya}.")
        return

    if amount > bal[5]:
        await ctx.reply("Hey tenang, Kamu tidak memiliki Nilai Kejahatan sebanyak itu.")
        return

    if amount < 1:
        await ctx.reply("Nilai Kejahatan yang ingin dikurangi harus lebih dari 0.")
        return
        
    await ctx.reply(f"Anda membayar <​:rupiah:920954420617941032>Rp.{biaya} dan berhasil menyogok polisi, Nilai Kejahatan mu dikurangi sebanyak {amount}.")
    await update_bank(ctx.author,-1*biaya)
    await update_bank(ctx.author,-1*amount,"kejahatan")    
   
async def penjara(ctx):
    await open_account(ctx.author)
    user = ctx.author
    users = await get_bank_data()
    polisi = await update_bank(ctx.author)
    bal = await update_bank(ctx.author)
    
    jahat = users[str(user.id)]["kejahatan"]
    penjara = 180*jahat
    menit = penjara/60
    
    await ctx.send(f"**{ctx.author.name}**, Kamu telah ditangkap dan dimasukkan ke sel tahanan, mohon tunggu selama {menit} menit sebelum kamu dibebaskan!")
    users[str(user.id)]["prosespenjara"] = 1
    with open("mainbank.json","w") as f:
        json.dump(users,f,indent=4)
    await asyncio.sleep(penjara)
    await ctx.send("Polisi : Kamu telah bebas dari masa kurungan, semoga tidak berbuat kejahatan lagi!")
    users[str(user.id)]["prosespenjara"] = 0
    users[str(user.id)]["kejahatan"] = 0
    with open("mainbank.json","w") as f:
        json.dump(users,f,indent=4)

@client.command(aliases = ['beli'], description = "Command untuk membeli barang yang dijual di shop", category = "Economy")
async def buy(ctx, item_name, amount = 1):
    amount = int(amount)
    await open_account(ctx.author)
    users = await get_bank_data()
    polisi = await update_bank(ctx.author)
    user = ctx.author
    
    if amount < 1:
        await ctx.send("Hmm, anda serius mau beli {amount} {item_name}?")
        return


    proseskerja = users[str(user.id)]["proseskerja"]
    if proseskerja==1:
        await ctx.send(f"**{ctx.author.name}**, Anda sedang bekerja, mohon tunggu sampai anda selesai bekerja!")
        return
    proseshack = users[str(user.id)]["prosesrampok"]
    if proseshack==1:
        await ctx.send(f"**{ctx.author.name}**, Anda sedang merampok, mohon tunggu sampai anda selesai merampok!")
        return
    prosespenjara = users[str(user.id)]["prosespenjara"]
    if prosespenjara==1:
        await ctx.send(f"**{ctx.author.name}**, Anda sedang dalam penjara, mohon tunggu sampai anda dibebaskan!")
        return

    prosesngemis = users[str(user.id)]["prosesngemis"]
    if prosesngemis==1:
        await ctx.send(f"**{ctx.author.name}**, Anda sedang mengemis, mohon tunggu sampai anda selesai mengemis!")
        return

    item_name = item_name.lower()
    name_ = None
    for item in allshop:
        name = item["name"].lower()
        if name == item_name:
            name_ = name
            category = item["kategori"]
            break

    if name_ == None:
        await ctx.send("Item yang kamu ketik invalid, mohon mengecek nya kembali")
        return        
    if category == "food":
        res = await buy_food(ctx.author,item_name,amount)
    
        if not res[0]:
            if res[1]==1:
                await ctx.send(f"Uang mu yang di dompet tidak cukup untuk membeli {amount}")
                return

        await ctx.send(f"Kamu berhasil membeli {amount} {item}")        
    if category == "armor":
        res = await buy_armor(ctx.author,item_name,amount)
    
        if not res[0]:
            if res[1]==1:
                await ctx.send(f"Uang mu yang di dompet tidak cukup untuk membeli {amount}")
                return

        await ctx.send(f"Kamu berhasil membeli {amount} {item}")        
    if category == "sword":
        res = await buy_sword(ctx.author,item_name,amount)
    
        if not res[0]:
            if res[1]==1:
                await ctx.send(f"Uang mu yang di dompet tidak cukup untuk membeli {amount}")
                return

        await ctx.send(f"Kamu berhasil membeli {amount} {item}")     
    return

async def buy_armor(user,item_name,amount):
    item_name = item_name.lower()
    for item in armorshop:
        name = item["name"].lower()
        if name == item_name:
            price = 0.9 * item["price"]
            bagian = item["bagian"]
            bonushp = item["hp"]
            kategori = item["kategori"]
            break
            
    cost = price*amount

    users = await get_bank_data()
        
    bal = await update_bank(user)
        
    if bal[0]<cost:
        return [False,1]
            
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
            obj = {"item":item_name , "amount" : amount , "bagian":bagian , "bonushp":bonushp, "price":price, "kategori":kategori}
            users[str(user.id)]["bag"].append(obj)
    except:
        obj = {"item":item_name , "amount" : amount , "bagian":bagian , "bonushp":bonushp, "price":price, "kategori":kategori}
        users[str(user.id)]["bag"] = [obj]
            
    with open("mainbank.json","w") as f:
        json.dump(users,f,indent=4)
                       
    await update_bank(user,cost*-1,"wallet")
             
    return [True,"Worked"]

async def buy_food(user,item_name,amount):
    item_name = item_name.lower()
    for item in foodshop:
        name = item["name"].lower()
        if name == item_name:
            price = 0.9 * item["price"]
            heal = item["heal"]
            kategori = item["kategori"]
            break

    cost = price*amount

    users = await get_bank_data()

    bal = await update_bank(user)

    if bal[0]<cost:
        return [False,1]

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
            obj = {"item":item_name , "amount" : amount, "heal":heal, "price":price, "kategori":kategori}
            users[str(user.id)]["bag"].append(obj)
    except:
        obj = {"item":item_name , "amount" : amount, "heal":heal, "price":price, "kategori":kategori}
        users[str(user.id)]["bag"] = [obj]        

    with open("mainbank.json","w") as f:
        json.dump(users,f)

    await update_bank(user,cost*-1,"wallet")

    return [True,"Worked"]
    
async def buy_sword(user,item_name,amount):
    item_name = item_name.lower()
    for item in swordshop:
        name = item["name"].lower()
        if name == item_name:
            price = 0.9 * item["price"]
            damage = item["damage"]
            kategori = item["kategori"]
            break

    cost = price*amount

    users = await get_bank_data()

    bal = await update_bank(user)

    if bal[0]<cost:
        return [False,1]

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
            obj = {"item":item_name , "amount" : amount , "damage":damage, "price":price, "kategori":kategori}
            users[str(user.id)]["bag"].append(obj)
    except:
        obj = {"item":item_name , "amount" : amount , "damage":damage, "price":price, "kategori":kategori}
        users[str(user.id)]["bag"] = [obj]        

    with open("mainbank.json","w") as f:
        json.dump(users,f)

    await update_bank(user,cost*-1,"wallet")

    return [True,"Worked"]    

@client.command(aliases = ['tas','inv','inventory'], description = "Command untuk mengecek isi tas", category = "Economy")
async def bag(ctx):
    await open_account(ctx.author)
    user = ctx.author
    users = await get_bank_data()

    try:
        bag = users[str(user.id)]["bag"]
    except:
        bag = []

    foodem = discord.Embed(title = f"Tas Ransel {user.name}", color = discord.Color.blue())
        
    for item in bag:
        kategori = item["kategori"]
        if kategori == "food":
            name = item["item"]
            amount = item["amount"]
            price = item["price"]
            heal = item["heal"]
            foodem.add_field(name = name, value = f"Jumlah : {amount} | Healing {heal} <​:health:922441419166212177>HP | Harga Jual : {price}")
        if kategori == "armor":
            name = item["item"]
            amount = item["amount"]
            price = item["price"]
            bonushp = item["bonushp"]
            bagian = item["bagian"]
            foodem.add_field(name = name, value = f"Jumlah : {amount} | Bagian : {bagian} | Max <​:health:922441419166212177>Health +{bonushp} | Harga Jual : {price}")
        if kategori == "sword":
            name = item["item"]
            amount = item["amount"]
            price = item["price"]
            damage = item["damage"]
            foodem.add_field(name = name, value = f"Jumlah : {amount} | <​:damage:922440838699712542>Damage +{damage} | Harga Jual : {price}")
            break
    await ctx.send(embed = foodem)
    return

@client.command(aliases = ['toko'], description = "Command untuk mengecek barang yang di jual di Shop", category = "Economy")
async def shop(ctx):
    foodem = discord.Embed(title = "Toko Makanan", description = "Tekan reaction dibawah untuk berpindah halaman!", color = discord.Color.red())
    armorem = discord.Embed(title = "Toko Armor", description = "Tekan reaction dibawah untuk berpindah halaman!", color = discord.Color.yellow())
    swordem = discord.Embed(title = "Toko Pedang", description = "Tekan reaction dibawah untuk berpindah halaman!", color = discord.Color.green())
    for item in allshop:
        kategori = item["kategori"]
        if kategori == "food":
            name = item["name"]
            price = item["price"]
            heal = item["heal"]
            desk = item["deskripsi"]
            foodem.add_field(name = f"{name} <​:coin:920954420617941032>Rp.{price}", value = f"Healing {heal} <​:health:922441419166212177>HP | {desk}")
        if kategori == "armor":
            name = item["name"]
            price = item["price"]
            bonushp = item["hp"]
            bagian = item["bagian"]
            desk = item["deskripsi"]
            armorem.add_field(name = f"{name} <​:coin:920954420617941032>Rp.{price}", value = f"Max <​:health:922441419166212177>Health +{bonushp} | Bagian : {bagian} | {desk}")
        if kategori == "sword":
            name = item["name"]
            price = item["price"]
            damage = item["damage"]
            desk = item["deskripsi"]
            swordem.add_field(name = f"{name} <​:coin:920954420617941032>Rp.{price}", value = f"<​:damage:922440838699712542>Damage +{damage} | {desk}")
    client.shop_pages = [foodem, armorem, swordem]
    buttons = [u"\u23EA", u"\u2B05", u"\u27A1", u"\u23E9"]
    current = 0
    msg = await ctx.send(embed=client.shop_pages[current])

    for button in buttons:
        await msg.add_reaction(button)
       
    while True:
        try:
            reaction, user = await client.wait_for("reaction_add", check=lambda reaction, user: user == ctx.author and reaction.emoji in buttons, timeout=60.0)

        except asyncio.TimeoutError:
            return print("test")

        else:
            if reaction.emoji == u"\u23EA":
                current = 0 
                await msg.edit(embed=client.shop_pages[current])
            elif reaction.emoji == u"\u2B05":
                if current > 0:
                    current -= 1
                    await msg.edit(embed=client.shop_pages[current])
            elif reaction.emoji == u"\u27A1":      
                if current < len(client.shop_pages)-1:
                    current += 1
                    await msg.edit(embed=client.shop_pages[current])
            elif reaction.emoji == u"\u23E9":
                current = len(client.shop_pages)-1
                await msg.edit(embed=client.shop_pages[current])
                
            for button in buttons:
                await msg.remove_reaction(button, ctx.author)                
                        
@client.command(aliases = ['jual'], description = "Command untuk menjual item", category = "Economy")
async def sell(ctx,item,amount = 1):
    amount = int(amount)
    await open_account(ctx.author)
    users = await get_bank_data()
    user = ctx.author

    polisi = await update_bank(ctx.author)


    proseskerja = users[str(user.id)]["proseskerja"]
    if proseskerja==1:
        await ctx.send(f"**{ctx.author.name}**, Anda sedang bekerja, mohon tunggu sampai anda selesai bekerja!")
        return
    proseshack = users[str(user.id)]["prosesrampok"]
    if proseshack==1:
        await ctx.send(f"**{ctx.author.name}**, Anda sedang merampok, mohon tunggu sampai anda selesai merampok!")
        return
    prosespenjara = users[str(user.id)]["prosespenjara"]
    if prosespenjara==1:
        await ctx.send(f"**{ctx.author.name}**, Anda sedang dalam penjara, mohon tunggu sampai anda dibebaskan!")
        return

    prosesngemis = users[str(user.id)]["prosesngemis"]
    if prosesngemis==1:
        await ctx.send(f"**{ctx.author.name}**, Anda sedang mengemis, mohon tunggu sampai anda selesai mengemis!")
        return

    res = await sell_this(ctx.author,item,amount)

    if not res[0]:
        if res[1]==1:
            await ctx.send(f"Kamu tidak punya {item}.")
            return
        if res[1]==2:
            await ctx.send(f"Kamu tidak punya {amount} {item}.")
            return
        if res[1]==3:
            await ctx.send(f"Kamu tidak punya {item} di tas mu.")
            return

    await ctx.send(f"Kamu berhasil menjual {amount} {item}, cek uang anda.")

async def sell_this(user,item_name,amount,price = None):
    users = await get_bank_data()
    item_name = item_name.lower()
    try:
        bag = users[str(user.id)]["bag"]
    except:
        bag = []
    name_ = None
    for item in bag:
        name = item["name"].lower()
        if name == item_name:
            name_ = name
            if price==None:
                price = item["price"]
            break

    if name_ == None:
        return [False,1]
        
    cost = price*amount

    users = await get_bank_data()

    bal = await update_bank(user)

    try:
        index = 0
        t = None
        for thing in users[str(user.id)]["bag"]:
            n = thing["item"]
            if n == item_name:
                old_amt = thing["amount"]
                new_amt = old_amt - amount
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

    await update_bank(user,cost,"wallet")

    return [True,"Worked"]
    
@client.command(aliases = ['makan'], description = "Command untuk memakan makanan yang sudah dibeli", category = "Economy")
async def eat(ctx,item,amount = 1):
    await open_account(ctx.author)

    res = await eat_this(ctx.author,item,amount)

    if not res[0]:
        if res[1]==1:
            await ctx.send("Makanan itu tidak valid!")
            return
        if res[1]==2:
            await ctx.send(f"Kamu tidak dapat makan {amount} {item} saat ini karena health mu akan melebihi batas!.")
            return
        if res[1]==3:
            await ctx.send(f"Kamu gak punya {amount} {item}!.")
            return
        if res[1]==4:
            await ctx.send(f"Kamu gak punya {item}!.")
            return

    await ctx.send(f"Kamu berhasil memakan {amount} {item}.")

async def eat_this(user,item_name,amount):
    item_name = item_name.lower()
    name_ = None
    for item in foodshop:
        name = item["name"].lower()
        if name == item_name:
            name_ = name
            heal = amount * item["heal"]
            break

    if name_ == None:
        return [False,1]

    users = await get_bank_data()
    health = users[str(user.id)]["health"]
    maxhealth = users[str(user.id)]["maxhealth"]
    maxheal = maxhealth - health
    if heal > maxheal:
        return [False,2]

    try:
        index = 0
        t = None
        for thing in users[str(user.id)]["food"]:
            n = thing["item"]
            if n == item_name:
                old_amt = thing["amount"]
                new_amt = old_amt - amount
                if new_amt < 0:
                    return [False,3]
                users[str(user.id)]["food"][index]["amount"] = new_amt
                t = 1
                break
            index+=1 
        if t == None:
            return [False,4]
    except:
        return [False,4]    

    users[str(user.id)]["health"] += heal
    with open("mainbank.json","w") as f:
        json.dump(users,f)

    return [True,"Worked"]
    
@client.command(aliases = ["lb"], description = "Command untuk mengecek leaderboard top orang terkaya", category = "Economy")
async def leaderboard(ctx,x = 5):
    users = await get_bank_data()
    leader_board = {}
    total = []
    for user in users:
        name = int(user)
        total_amount = users[user]["wallet"] + users[user]["bank"]
        leader_board[total_amount] = name
        total.append(total_amount)

    total = sorted(total,reverse=True)    

    em = discord.Embed(title = f"Top {x} Orang Terkaya" , description = "Ini adalah kumpulan beberapa orang terkaya yang paling banyak memiliki uang",color = discord.Color(0xfa43ee))
    index = 1
    for amt in total:
        id_ = leader_board[amt]
        member = client.get_user(id_)
        name = member.name
        em.add_field(name = f"{index}. {name}" , value = f"Rp.{amt}",  inline = False)
        if index == x:
            break
        else:
            index += 1

    await ctx.send(embed = em)

@client.command(description = "Command untuk menghapus semua chat yang ada di channel", category = "Config")
@commands.has_permissions(administrator = True)
async def nuke(ctx, channel: discord.TextChannel = None):
    if channel == None: 
        await ctx.send("Kamu belum mention channel yang mau dinuke!")
        return

    nuke_channel = discord.utils.get(ctx.guild.channels, name=channel.name)

    if nuke_channel is not None:
        new_channel = await nuke_channel.clone(reason="Telah di nuke!")
        await nuke_channel.delete()
        await new_channel.send("Channel ini telah di nuke!")
        await ctx.send(f"Berhasil nuke {channel.name}!")

    else:
        await ctx.send(f"Channel {channel.name} tidak bisa ditemukan!")

@client.command(description = "Command untuk membersihkan chat secara cepat dalam jumlah besar", category = "Config")
@commands.has_permissions(manage_messages = True)
async def clear(ctx,amount=1):
    ramount = amount + 1
    await ctx.channel.purge(limit = ramount)
    await ctx.send(f"Berhasil membersihkan {amount} chat", delete_after=4)
    
@client.command(description = "Command untuk kick member dari server", category = "Config")
@commands.has_permissions(kick_members = True)
async def kick(ctx, member:discord.Member, *, reason="Tidak dituliskan"):
    if member == ctx.author:
        await ctx.send("Apakah kamu yakin ingin kick dirimu sendiri?")
        return
    await member.send(f"{member.name} kamu telah di kick dari {ctx.guild.name} dengan alasan : {reason}")
    await ctx.send(f"{member.name} telah dikeluarkan dari {ctx.guild.name}.")
    await member.kick(reason=reason)
    
@client.command(description = "Command untuk ban member dari server", category = "Config")
@commands.has_permissions(ban_members = True)
async def ban(ctx, member:discord.Member, *, reason="Tidak dituliskan"):
    if member == ctx.author:
        await ctx.send("Apakah kamu yakin ingin banned dirimu sendiri?")
        return
    await member.send(f"{member.name} kamu telah di banned dari {ctx.guild.name} dengan alasan : {reason}")
    await ctx.send(f"{member.name} telah dibanned dari {ctx.guild.name}.")
    await member.ban(reason=reason)
    
@client.command(description = "Command untuk unban member", category = "Config")
async def unban(ctx, *, member):
	banned_users = await ctx.guild.bans()
	
	member_name, member_discriminator = member.split('#')
	for ban_entry in banned_users:
		user = ban_entry.user
		
		if (user.name, user.discriminator) == (member_name, member_discriminator):
 			await ctx.guild.unban(user)
 			await ctx.channel.send(f"Unbanned: {user.mention}")    
    
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
        users[str(user.id)]["wallet"] = 10000
        users[str(user.id)]["bank"] = 0
        users[str(user.id)]["ticket"] = 1
        users[str(user.id)]["stamina"] = 50
        users[str(user.id)]["mstamina"] = 50
        users[str(user.id)]["kejahatan"] = 0
        users[str(user.id)]["mkejahatan"] = 10
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
   

    with open("mainbank.json","w") as f:
        json.dump(users,f,indent=4)
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
        users[str(user.id)]["chestplates"] = "nothing"
        users[str(user.id)]["leggings"] = "nothing"
        users[str(user.id)]["boots"] = "nothing"
        users[str(user.id)]["hphelmets"] = 0
        users[str(user.id)]["hpchestplates"] = 0
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

client.run("ODk5NjAzNzQ2MDI2MzAzNTA5.YW1LRg.2bq8lKbwoXPerUrQfn6ZM_DCXy4")