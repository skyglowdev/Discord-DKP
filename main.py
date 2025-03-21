import asyncio
import discord
import json
from discord import app_commands
from discord.ext import commands
from discord.ui import Button, View

import discordcustomviews
import MyDBInterface
import config
import helpfunctions
import shared_data

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
    if config.DEBUG_VERBOSE:
        print(f"Message from {message.author}: {message.content}")
    # Check if the message is in the target channel
    if message.channel.id == config.CHANNEL_ID:
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
        if config.DEBUG_VERBOSE:
            print("trova il discordId -> esiste già l'utente")
        await interaction.response.send_message("❌ Questo account discord è già stato registrato.", ephemeral=True)
    else:   # non trova il discordId -> controllare se esiste il playername
        if config.DEBUG_VERBOSE:
            print("non trova il discordId -> controllare se esiste il playername")
        playerId = await MyDBInterface.getPlayerIdFromName(playername)
        if playerId != -1:
            if config.DEBUG_VERBOSE:
                print("aggiungi (secondo) discord al membro")
            ret = await MyDBInterface.postPlayerName2(playerId, playername, await MyDBInterface.getDiscordId1(playername), str_discordId)
            if ret != -1:
                await interaction.response.send_message(f"✅ Secondo account discord {str_discordId} registato al giocatore {playername} numero {playerId}", ephemeral=True)
            else:
                await interaction.response.send_message("❌ Errore registrazione secondo account discord.", ephemeral=True)
        else:
            if config.DEBUG_VERBOSE:
                print("crea membro")
            playerId = await MyDBInterface.CreateAccount(playername, str_discordId)
            await interaction.response.send_message(f"✅ Account discord {playerId} registato al giocatore {playername} con discord id {str_discordId}", ephemeral=True)

@bot.tree.command(name="showdkp", description="Mostra la classifica DKP")
async def showdkp(interaction: discord.Interaction):
    membername = await MyDBInterface.getMemberName(str(interaction.user.id))
    if config.DEBUG_VERBOSE:
        print("membername "+str(membername))
    message = "**🏆 Classifica DKP 🏆**\n"
    i = 0
    while i < len(shared_data.dkp_rankings):
        if not membername == shared_data.dkp_rankings[i]["playerName"]:
            message += f"{i}. {shared_data.dkp_rankings[i]["playerName"]} - [{shared_data.dkp_rankings[i]["points"]}] punti\n"
        else:
            message += f"{i}. **{shared_data.dkp_rankings[i]["playerName"]} - [{shared_data.dkp_rankings[i]["points"]}] punti**\n"
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
    if config.DEBUG_VERBOSE:
        print("droplist")
    #if not helpfunctions.checkRole(interaction.user.roles):
    #    await interaction.response.send_message("❌ Non hai i permessi per eseguire questo comando.", ephemeral=True)
    #    return
    playerId = await MyDBInterface.getMemberId(str(interaction.user.id))
    if config.DEBUG_VERBOSE:
        print(playerId)
    if playerId == -1:
        await interaction.response.send_message(f"Non sei registrato alla piattaforma utilizza /register **NomeInGioco**!", ephemeral=True)
        return

    await interaction.response.defer(thinking=True, ephemeral=True)

    list_items = await MyDBInterface.listT2Items()
    if config.DEBUG_VERBOSE:
        print("T2 len(list_items) "+str(len(list_items)))
        print("T2 list_items \n"+json.dumps(list_items, indent=4))

    message= "Scegliere un oggetto T2 dalle liste sottostanti\n"
    placeholder= "Scegli un oggetto da inserire nella lista desideri"
    l = []
    for m in list_items:
        l.append({ "id": m["itemId"], "label": m["itemName"],
            "description": "" , "emoji": None}) #"emoji": "🔥"})
    await discordcustomviews.SplitSelectOptionsOnViews(interaction, message, placeholder, l, helpfunctions.callbackWishChooseItem, {"playerId": playerId})

    message= ":fire: Scegliere un arma archboss dalla lista: :fire:\n"
    list_items = await MyDBInterface.listArchbossItems()
    if config.DEBUG_VERBOSE:
        print("ARCHBOSS len(list_items) "+str(len(list_items)))
        print("ARCHBOSS list_items \n"+json.dumps(list_items, indent=4))
    l = []
    for m in list_items:
        l.append({ "id": m["itemId"], "label": m["itemName"],
            "description": "" , "emoji": None}) #"emoji": "🔥"})
    await discordcustomviews.SplitSelectOptionsOnViews(interaction, message, placeholder, l, helpfunctions.callbackWishChooseItem, {"playerId": playerId})

@bot.tree.command(name="wishlist", description="Mostra la lista desideri")
async def wishlist(interaction: discord.Interaction):
    playerId = await MyDBInterface.getMemberId(str(interaction.user.id))
    if config.DEBUG_VERBOSE:
        print(playerId)
    if playerId == -1:
        await interaction.response.send_message(f"Non sei registrato alla piattaforma utilizza /register **NomeInGioco**!", ephemeral=True)
        return
    #if not helpfunctions.checkRole(interaction.user.roles):
    #    await interaction.response.send_message("❌ Non hai i permessi per eseguire questo comando.", ephemeral=True)
    #    return
    listrequests = await MyDBInterface.listPlayerWishItems(playerId)
    if config.DEBUG_VERBOSE:
        print(len(listrequests))
        print(listrequests)
    message =["Hai richiesto i seguenti oggetti:\n"]
    button_params = []
    i = 0
    while i < len(listrequests):
        # Creiamo il messaggio dinamico con le opzioni
        message.append( f"{listrequests[i]["idItemRequest"]} ** {listrequests[i]["itemName"]} **\n" )
        i += 1
    await interaction.response.send_message("".join(message), ephemeral=True)

'''
DROPS
'''
@bot.tree.command(name="droplist", description="Mostra tutti gli oggetti richiedibili")
async def droplist(interaction: discord.Interaction):
    if config.DEBUG_VERBOSE:
        print("droplist")
    playerId = await MyDBInterface.getMemberId(str(interaction.user.id))
    if config.DEBUG_VERBOSE:
        print(playerId)
    if playerId == -1:
        await interaction.response.send_message(f"Non sei registrato alla piattaforma utilizza /register **NomeInGioco** !", ephemeral=True)
        return
    list_items = await MyDBInterface.listAvailableItems()
    if config.DEBUG_VERBOSE:
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
    view = discordcustomviews.ViewButtonNumberedWithCustomId(button_params)
    message = await interaction.response.send_message("".join(message), view=view, ephemeral=True)
    view.message = await interaction.original_response()  # Ottieni il messaggio per modificarlo dopo il timeout

@bot.tree.command(name="droprequests", description="Mostra tutti gli oggetti richiesti")
async def droprequests(interaction: discord.Interaction):    
    if config.DEBUG_VERBOSE:
        print("droplist")
    list_itemrequest = await MyDBInterface.listAvailableItemsRequested(interaction.user.id)
    print(list_itemrequest)

    message =[]
    button_params = []
    i = 0
    for item_request in list_itemrequest:
        # Creiamo il messaggio dinamico con le opzioni
        message.append( f"{i+1}️⃣ ** {item_request["id"]} {item_request["description"]} {item_request["reason"]} richiesto il {item_request["requestDate"]} **\n" )
#        # Creiamo una View con le opzioni dinamiche
#        button_params.append( {"label": str(i+1), "itemName": list_items[i]["idItemNavigation"]["itemName"], 
#            "func": helpfunctions.ChooseItemType, "func_param": { "itemName": list_items[i]["idItemNavigation"]["itemName"], "id": list_items[i]["id"] }} )
        i += 1
    if len(message) == 0:
        message.append("Non sono stati richiesti item!")
    await interaction.response.send_message("".join(message), ephemeral=True)

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
