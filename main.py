import asyncio
import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import Button, View

import discordcustomviews
import MyDBInterface
#from config import DiscordItemDistribution
import config
import helpfunctions
import shared_data

#{playerId, points}

intents=discord.Intents.all()
'''
intents = discord.Intents.default()
intents.message_content = True  # Necessario per interagire con il contenuto dei messaggi
'''
bot = commands.Bot(command_prefix="!", intents=intents) # intents=discord.Intents.default()

'''
GESTIONE EVENTI
'''

# Event to handle messages
@bot.event
async def on_message(message):
    if config.DEBUG:
        print(f"Message from {message.author}: {message.content}")
    # Check if the message is in the target channel
    if message.channel.id == config.TARGET_CHANNEL_ID:
        # Ignore messages sent by the bot itself
        if message.author == bot.user:
            return

        # Now, you can process the message
#        print(f"Message from {message.author}: {message.content}")
    
    # Make sure to process commands if needed
    await bot.process_commands(message)

'''
##################
# COMANDI SLASH
##################
'''
@bot.tree.command(name="help", description="Fornisce l'help del bot")
async def help(interaction: discord.Interaction):
    message = "**:interrobang: HELP :interrobang:  **\n"
    message += "\n"
    message += "Lista comandi e descrizioni:\n"
    message += ":arrow_forward:  **/register NomeGiocatore**\n"
    message += "Registra l'utente sulla piattaforma. Cambiare NomeGiocatore con il nome desiderato. "
    message += "E' possibile registrare due account discord allo stesso nome\n"
    message += "\n"

    message += ":arrow_forward:  **/droplist**\n"
    message += "Restituisce la lista degli oggetti in attesa di distribuzione. "
    message += "Permette di richiedere l'oggetto e specificare l'uso che ne verrà fatto\n"
    message += "\n"
    message += ":arrow_forward:  **/droprequests**\n"
    message += "Mostra le proprie richieste oggetti in attesa di distribuzione\n"
    message += "\n"

    message += ":arrow_forward:  **/wish**\n"
    message += "Scelta oggetti della propria lista desideri\n"
    message += "\n"
    message += ":arrow_forward:  **/wishlist**\n"
    message += "Mostra la propria lista desideri\n"
    message += "\n"

    message += ":arrow_forward:  **/showdkp**\n"
    message += "Mostra la classifica punti DKP\n"
    message += "\n"

    if helpfunctions.checkRole(interaction.user.roles):
        message += "** SOLO PER ADMIN **\n"
        message += ":arrow_forward:  **/updatedkp**\n"
        message += "Cacha la classifica punti DKP\n"
        message += "\n"
        message += ":arrow_forward:  **/sync**\n"
        message += "Sincronizza i comandi del bot\n"
        message += "\n"

    await interaction.response.send_message(message, ephemeral=True)

@bot.tree.command(name="register", description="Registra il proprio discord nella lista membri")
@app_commands.describe(playername="Il nome del giocatore.")
async def register(interaction: discord.Interaction, playername: str):
#   tutta la parte di gestione della registrazione
    playerId = -1
    str_discordId = str(interaction.user.id)
    memberId = await MyDBInterface.getMemberId(str_discordId)
    print("memberId "+str(memberId))
    if memberId != -1:
        if config.DEBUG:
            print("trova il discordId -> esiste già l'utente")
        await interaction.response.send_message("❌ Questo account discord è già stato registrato.", ephemeral=True)
    else:   # non trova il discordId -> controllare se esiste il playername
        if config.DEBUG:
            print("non trova il discordId -> controllare se esiste il playername")
        playerId = await MyDBInterface.getPlayerIdFromName(playername)
        if playerId != -1:
            if config.DEBUG:
                print("aggiungi (secondo) discord al membro")
            ret = await MyDBInterface.postPlayerName2(playerId, playername, await MyDBInterface.getDiscordId1(playername), str_discordId)
            if ret != -1:
                await interaction.response.send_message(f"✅ Secondo account discord {str_discordId} registato al giocatore {playername} numero {playerId}", ephemeral=True)
            else:
                await interaction.response.send_message("❌ Errore registrazione secondo account discord.", ephemeral=True)
        else:
            if config.DEBUG:
                print("crea membro")
            playerId = await MyDBInterface.CreateAccount(playername, str_discordId)
            await interaction.response.send_message(f"✅ Account discord {playerId} registato al giocatore {playername} con discord id {str_discordId}", ephemeral=True)

@bot.tree.command(name="showdkp", description="Mostra la classifica DKP")
async def showdkp(interaction: discord.Interaction):
    if not helpfunctions.checkRole(interaction.user.roles):
        await interaction.response.send_message("❌ Non hai i permessi per eseguire questo comando.", ephemeral=True)
        return
    membername = await MyDBInterface.getMemberName(str(interaction.user.id))
    if config.DEBUG:
        print("membername "+str(membername))
    message = "**🏆 Classifica DKP 🏆**\n"
    i = 0
    while i < len(shared_data.dkp_rankings):
        if not membername == shared_data.dkp_rankings[i]["playerId"]:
            message += f"{i}. {shared_data.dkp_rankings[i]["playerId"]} - [{shared_data.dkp_rankings[i]["points"]}] punti\n"
        else:
            message += f"{i}. **{shared_data.dkp_rankings[i]["playerId"]} - [{shared_data.dkp_rankings[i]["points"]}] punti**\n"
        i+=1
    await interaction.response.send_message(message, ephemeral=True)

'''
ADMIN"discordId":
'''
@bot.tree.command(name="updatedkp", description="Cacha la classifica punti DKP")
async def updatedkp(interaction: discord.Interaction):
    if not helpfunctions.checkRole(interaction.user.roles): #interaction.user.id != config.MYDISCORDID:  # Sostituisci con il tuo ID
        await interaction.response.send_message("❌ Non hai i permessi per eseguire questo comando.", ephemeral=True)
        return
    if await helpfunctions.updateDKP():
        await interaction.response.send_message(f"✅ La classifica DKP è stata aggiornata correttamente", ephemeral=True)
    else:
        await interaction.response.send_message("❌ La classifica DKP non è stata aggiornata correttamente", ephemeral=True)

@bot.tree.command(name="sync", description="Sincronizza i comandi slash (solo per admin)")
async def sync(interaction: discord.Interaction):
    if not helpfunctions.checkRole(interaction.user.roles): #interaction.user.id != config.MYDISCORDID:  # Sostituisci con il tuo ID
        await interaction.response.send_message("❌ Non hai i permessi per eseguire questo comando.", ephemeral=True)
        return

    try:
        await bot.tree.sync(guild=discord.Object(id=config.GUILD_ID))  # Sincronizza solo per questo server
        await interaction.response.send_message("✅ Comandi sincronizzati con successo!", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ Errore: {e}", ephemeral=True)
#    await await_presence()

'''
WISHLIST
'''
@bot.tree.command(name="wish", description="Aggiunta oggetto a lista desideri")
async def wish(interaction: discord.Interaction):
    if config.DEBUG:
        print("droplist")
    playerId = await MyDBInterface.getMemberId(str(interaction.user.id))
    if config.DEBUG:
        print(playerId)
    if playerId == -1:
        await interaction.response.send_message(f"Non sei registrato alla piattaforma utilizza /register **NomeInGioco**!", ephemeral=True)
        return
    if not helpfunctions.checkRole(interaction.user.roles):
        await interaction.response.send_message("❌ Non hai i permessi per eseguire questo comando.", ephemeral=True)
        return
    list_items = await MyDBInterface.listT2Items()
    if config.DEBUG:
        print("len(list_items) "+str(len(list_items)))
        print("list_items "+str(list_items))

    # RIMUOVERE
    config.DEBUG = False

    len_list_items = len(list_items)
    discordcustomviews.DISCORD_SELECT_MAX =5
    discordcustomviews.DISCORD_SELECT_OPTIONS_MAX = 25
    k = 0
    j = 0
    i= 0
    while i+j*discordcustomviews.DISCORD_SELECT_OPTIONS_MAX+k*discordcustomviews.DISCORD_SELECT_MAX*discordcustomviews.DISCORD_SELECT_OPTIONS_MAX < len_list_items:
        # view di 5 select
        viewcustom_params = []
        while i+j*discordcustomviews.DISCORD_SELECT_OPTIONS_MAX+k*discordcustomviews.DISCORD_SELECT_MAX*discordcustomviews.DISCORD_SELECT_OPTIONS_MAX < len_list_items and j < discordcustomviews.DISCORD_SELECT_MAX:
            #select di 25 options
            selectcustom_params = []
            while i+j*discordcustomviews.DISCORD_SELECT_OPTIONS_MAX+k*discordcustomviews.DISCORD_SELECT_MAX*discordcustomviews.DISCORD_SELECT_OPTIONS_MAX < len_list_items and i < discordcustomviews.DISCORD_SELECT_OPTIONS_MAX:
                pointer = i+j*discordcustomviews.DISCORD_SELECT_OPTIONS_MAX+k*discordcustomviews.DISCORD_SELECT_MAX*discordcustomviews.DISCORD_SELECT_OPTIONS_MAX
                if config.DEBUG:
                    print ("wish pointer" + str(pointer))
                if True: #opzione per emoji
                    selectcustom_params.append({ "id": list_items[pointer]["idItem"], "label": list_items[pointer]["itemName"],
                        "description": "" , "emoji": None})
                else:
                    selectcustom_params.append({ "id": list_items[pointer]["idItem"], "label": list_items[pointer]["itemName"],
                        "description": "" , "emoji": "🔥"})
                i+=1
            viewcustom_params.append( { "placeholder": "Scegli un oggetto da inserire nella lista desideri" + str(k*discordcustomviews.DISCORD_SELECT_MAX+j+1), 
                "select_param": selectcustom_params, "func": helpfunctions.callbackWishChooseItem, "func_param": playerId })
            i=0
            j+=1
        message =[]
        message.append("BLABLABLA")
        if k == 0:
            await interaction.response.send_message("".join(message), view=discordcustomviews.ViewSelectWithCustomId(viewcustom_params), ephemeral=True)
        else:
            await interaction.followup.send(view=discordcustomviews.ViewSelectWithCustomId(viewcustom_params), ephemeral=True)
        j=0
        k+=1

@bot.tree.command(name="wishlist", description="Mostra la lista desideri")
async def wishlist(interaction: discord.Interaction):
    playerId = await MyDBInterface.getMemberId(str(interaction.user.id))
    if config.DEBUG:
        print(playerId)
    if playerId == -1:
        await interaction.response.send_message(f"Non sei registrato alla piattaforma utilizza /register **NomeInGioco**!", ephemeral=True)
        return
    if not helpfunctions.checkRole(interaction.user.roles):
        await interaction.response.send_message("❌ Non hai i permessi per eseguire questo comando.", ephemeral=True)
        return
    listrequests = await listPlayerItemRequests(playerId)
    if config.DEBUG:
        print(len(listrequests))
        print(listrequests)
    message =["Hai richiesto i seguenti oggetti:"]
    button_params = []
    i = 0
    while i < len(listrequests):
        # Creiamo il messaggio dinamico con le opzioni
        message.append( f"{i+1}️⃣ ** {listrequests[i]["idItemNavigation"]["itemName"]} droppato il {listrequests[i]["dropDate"]} **\n" )
        i += 1
    await interaction.response.send_message("".join(message), ephemeral=True)

'''
DROPS
'''
@bot.tree.command(name="droplist", description="Mostra tutti gli oggetti richiedibili")
async def droplist(interaction: discord.Interaction):
    if config.DEBUG:
        print("droplist")
    playerId = await MyDBInterface.getMemberId(str(interaction.user.id))
    if config.DEBUG:
        print(playerId)
    if playerId == -1:
        await interaction.response.send_message(f"Non sei registrato alla piattaforma utilizza /register **NomeInGioco** !", ephemeral=True)
        return
    list_items = await MyDBInterface.requestAvailableItem()
    if config.DEBUG:
        print(len(list_items))
        print(list_items)

    message =[]
    button_params = []
    i = 0
    while i < len(list_items):
        # Creiamo il messaggio dinamico con le opzioni
        message.append( f"{i+1}️⃣ ** {list_items[i]["idItemNavigation"]["itemName"]} droppato il {list_items[i]["dropDate"]} **\n" )
        # Creiamo una View con le opzioni dinamiche
        button_params.append( {"label": str(i+1), "itemName": list_items[i]["idItemNavigation"]["itemName"], 
            "func": helpfunctions.callbackDropChooseItemType, "func_param": { "itemName": list_items[i]["idItemNavigation"]["itemName"], "id": list_items[i]["id"] }} )
        i += 1
    await interaction.response.send_message("".join(message), view=discordcustomviews.ViewButtonNumberedWithCustomId(button_params), ephemeral=True)

@bot.tree.command(name="droprequests", description="Mostra tutti gli oggetti richiesti")
async def droprequests(interaction: discord.Interaction):    
    if config.DEBUG:
        print("droplist")
    list_itemrequest = await MyDBInterface.listAvailableItemsRequested(interaction.user.id)
    print(list_itemrequest)

    message =[]
    button_params = []
    i = 0
    while i < len(list_itemrequest):
        # Creiamo il messaggio dinamico con le opzioni
        message.append( f"{i+1}️⃣ ** {list_itemrequest[i]["id"]} {list_itemrequest[i]["description"]} {list_itemrequest[i]["reason"]} richiesto il {list_itemrequest[i]["requestDate"]} **\n" )
#        # Creiamo una View con le opzioni dinamiche
#        button_params.append( {"label": str(i+1), "itemName": list_items[i]["idItemNavigation"]["itemName"], 
#            "func": helpfunctions.ChooseItemType, "func_param": { "itemName": list_items[i]["idItemNavigation"]["itemName"], "id": list_items[i]["id"] }} )
        i += 1
    await interaction.response.send_message("".join(message), ephemeral=True)  #, view=discordviewbuttonchoices.ViewButtonNumberedWithCustomId(button_params), ephemeral=True)

# Evento in caso di connessione
@bot.event
async def on_ready():
    for guild in bot.guilds:
        print(f"Nome Server: {guild.name} - ID: {guild.id}")
    print(f"{bot.user} is ready!")
    try:
        await bot.tree.sync()  # Sincronizza i comandi
        print("✅ Comandi slash sincronizzati!")
    except Exception as e:
        print(f"❌ Errore nella sincronizzazione: {e}")
    commands = await bot.tree.fetch_commands()  # Recupera i comandi
    print(f"Registered commands: {commands}")  # Stampa i comandi registrati

asyncio.run(helpfunctions.updateDKP())
bot.run(config.TOKEN)
