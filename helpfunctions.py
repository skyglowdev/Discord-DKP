import discord

import config
import discordcustomviews
import MyDBInterface
import shared_data

'''
FUNZIONI GENERICHE
'''
def checkRole(roles):
    if config.DEBUG_VERBOSE:
        print("checkRole")
    for role in roles:
        if role.id == config.ADMIN_ROLE_ID:
            return True
    return False

def checkChannel(interaction: discord.Interaction):
    return interaction.channel.id == config.CHANNEL_ID

async def updateDKP():
    if config.DEBUG_VERBOSE:
        print("updateDKP")
    dkplist = await MyDBInterface.getAllDKP()
    if dkplist == -1:
        return False
    dkp_rankings = []
    for row in dkplist:
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
    
    data = await MyDBInterface.requestWishItem(param["id"], obj.values[0])
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
    await interaction.response.send_message(message, view=discordcustomviews.ViewButtonNumberedWithCustomId(button_params), ephemeral=True)

async def callbackDropChooseItemReason(interaction: discord.Interaction, param: dict):
    if config.DEBUG_VERBOSE:
        print("callbackDropChooseItemReason param")
        print(param)
    playerId = await MyDBInterface.getMemberId(str(interaction.user.id))
    ret = await MyDBInterface.requestAvailableItem(playerId, param["itemId"], param["reason"])
    if ret == None:
        await interaction.response.send_message("❌ La richiesta non è andata a buon fine contatta un amministratore", ephemeral=True)  # Assicura una risposta
    else:
        await interaction.response.send_message(f"✅ La richiesta oggetti numero {ret["idDroppedItemsRequests"]} è stata inserita", ephemeral=True)  # Assicura una risposta
