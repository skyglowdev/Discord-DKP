import discord

import config
import discordcustomviews
import MyDBInterface
import shared_data

'''
FUNZIONI GENERICHE
'''
def get_build_number():
    try:
        with open(".build-counter", "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return "0"  # Valore predefinito se il file non esiste

def checkRole(roles):
    if config.DEBUG_VERBOSE:
        print("checkRole")
    for role in roles:
        if role.id == config.ADMIN_ROLE_ID:
            return True
    return False

def checkChannel(interaction: discord.Interaction):
    return interaction.channel.id == config.CHANNEL_ID

def ItemListRemoveDuplicates(l: list):
    list_items = []
    list_names = []
    for row in l:
        if config.DEBUG_VERBOSE:
            print(row)
        if not row["itemName"] in list_names:
            list_items.append({"itemName": row["itemName"], "itemId": row["itemId"], "tier": row["tier"]})
            list_names.append(row["itemName"])
    return list_items


async def updateItemList():
    if config.DEBUG_VERBOSE:
        print("updateItems")
    list_items = await MyDBInterface.listItems()
    if list_items == -1:
        return False
    shared_data.list_items = ItemListRemoveDuplicates(list_items)
    return True

def returnItemListT2():
    t2data = []
    for row in shared_data.list_items:
        if config.DEBUG_VERBOSE:
            print (row)
        if row["tier"] == 2:
            t2data.append({"itemId": row["itemId"], "itemName": row["itemName"]})
    return t2data

def returnItemListArchboss():
    t2data = []
    for row in shared_data.list_items:
        if config.DEBUG_VERBOSE:
            print (row)
        if row["tier"] == 0:
            t2data.append({"itemId": row["itemId"], "itemName": row["itemName"]})
    return t2data

async def updateDKP():
    if config.DEBUG_VERBOSE:
        print("updateDKP")
    dkplist = await MyDBInterface.getAllDKP()
    if dkplist == -1:
        return False
    shared_data.dkp_rankings = []
    for row in dkplist:
        if config.DEBUG_VERBOSE:
            print(row)
        shared_data.dkp_rankings.append({"playerId": row["idMember"], "playerName": row["name"], "points": row["totalePunti"]}) #row["id"],
    return True

def myDKP(playerName: str):
    if config.DEBUG_VERBOSE:
        print("myDKP")
    for row in shared_data.dkp_rankings:
        if config.DEBUG_VERBOSE:
            print("row[playerId] "+ str(row["playerId"]))
            print("row[playerName] "+ str(row["playerName"]))
            print("playerName "+ str(playerName))
        if row["playerId"] == playerName:
            return row["points"]
    return 0
'''
FUNZIONI PER GESTIRE LE INTERAZIONI
'''
'''async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"Hai selezionato: {self.values[0]}", ephemeral=True)
'''
async def callbackWishChooseItem(interaction: discord.Interaction,  obj: discordcustomviews.CustomSelect, param: dict):
    if config.DEBUG_VERBOSE:
        print("callbackWishChooseItem param")
        print(param)
    print("callbackWishChooseItem param")
    print(param)

    list_requested = await MyDBInterface.listPlayerWishItems(param["playerId"])
    if ( len(list_requested) > config.MAX_REQUEST_ITEMS_NORMAL+config.MAX_REQUEST_ITEMS_ARCHBOSS ):
        await interaction.response.send_message(f"Sono già stati richiesti il massimo numero di oggetti.\nIn caso di problemi contattare un admin", ephemeral=True)
        return

    data = await MyDBInterface.requestWishItem(param["playerId"], obj.values[0])
    message = f"E' stata inserita la richiesta numero {data["idItemRequest"]}\n"
    await interaction.response.send_message(message, ephemeral=True)


async def callbackDropChooseItemType(interaction: discord.Interaction, param: dict):
    if config.DEBUG_VERBOSE:
        print("callbackDropChooseItemType param")
        print(param)
    if not myDKP(await MyDBInterface.getMemberId(str(interaction.user.id))) >= config.MINIMUM_DKP_POINTS_PER_ITEM:
        await interaction.response.send_message("Non si posseggono abbastanza DKP", ephemeral=True)
        return

    message = f"E' stato scelto l'oggetto **{param["itemName"]}**.\n" + "Qual'è il motivo della tua richiesta?\n"
    button_params = []
    button_params.append({"label": "BIS WISH", "func": callbackDropChooseItemReason, "func_param": { "itemId": param["id"], "reason": "BIS WISH" } })
    button_params.append({"label": "BIS non WISHLIST", "func": callbackDropChooseItemReason, "func_param": { "itemId": param["id"], "reason": "BIS non WISHLIST" } })
    button_params.append({"label": "TRATTO", "func": callbackDropChooseItemReason, "func_param": { "itemId": param["id"], "reason": "TRATTO" } })
    view = discordcustomviews.ViewButtonNumberedWithCustomId(button_params)
    await interaction.response.send_message(message, view=view, ephemeral=True)
    view.message = await interaction.original_response()

async def callbackDropChooseItemReason(interaction: discord.Interaction, param: dict):
    if config.DEBUG_VERBOSE:
        print("callbackDropChooseItemReason param")
        print(param)
    playerId = await MyDBInterface.getMemberId(str(interaction.user.id))
    ret = await MyDBInterface.requestAvailableItem(playerId, param["itemId"], param["reason"])
    if ret == None:
        await interaction.response.send_message("❌ La richiesta non è andata a buon fine contatta un amministratore", ephemeral=True)  # Assicura una risposta
    elif ret == 409:
        await interaction.response.send_message("❌ La richiesta è un duplicato", ephemeral=True)  # Assicura una risposta
    else:
        await interaction.response.send_message(f"✅ La richiesta oggetti numero {ret["idDroppedItemsRequests"]} è stata inserita", ephemeral=True)  # Assicura una risposta
