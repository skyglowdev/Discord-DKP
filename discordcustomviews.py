import discord
from discord.ui import Button, View
import typing

import config
import MyDBInterface

DISCORD_VIEW_MAX_ELEMENTS = 25
DISCORD_SELECT_MAX = 5
DISCORD_SELECT_OPTIONS_MAX = 25
DISCORD_BUTTON_MAX = 25

def func_DefaultInteraction(interaction: discord.Interaction):
    return True

'''
ViewButtonNumberedWithCustomId
'''

class CustomButton(discord.ui.Button):
    def __init__(self, label: str, function, param, style=discord.ButtonStyle.primary):
        if config.DEBUG_VERBOSE:
            print ("CustomButton param")
            print (param)
        super().__init__(label=label, style=style, custom_id=str(param)) 
        self.func = function
        self.param = param

    async def callback(self, interaction: discord.Interaction):
        await self.func(interaction, self.param)
#        await interaction.response.send_message(f"Hai premuto: {self.label}", ephemeral=True)

#button_param = [{"label": "nome label", "func": funzione_ per_l'azione, "func_param": parametro_funzione}]
class ViewButtonNumberedWithCustomId(View):
    def __init__(self, button_param, timeout = config.DISCORD_INTERACTION_TIMEOUT, function_interaction_check = func_DefaultInteraction):
        if config.DEBUG_VERBOSE:
            print ("ViewButtonNumberedWithCustomId param")
            print (button_param)

        super().__init__(timeout=timeout)  # Imposta un timeout di 10 secondi
        self.message = None
        if config.DEBUG_VERBOSE:
            print ("ViewButtonNumberedWithCustomId button_param")
            print (button_param)
        self.function_interaction_check = function_interaction_check
        i = 0
        while i < len(button_param):
            if config.DEBUG_VERBOSE :
                print(button_param[i])
            self.add_item (CustomButton( label=button_param[i]["label"], style=discord.ButtonStyle.primary, function=button_param[i]["func"], param=button_param[i]["func_param"] ) )
            i+=1

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return self.function_interaction_check(interaction)

    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
            if self.message:
                try:
                    await self.message.edit(view=self)
                except discord.NotFound:
                    pass


'''
ViewSelectWithCustomId
'''
class CustomSelect(discord.ui.Select):
    def __init__(self, placeholder: str, select_param: list, function, func_param,timeout = config.DISCORD_INTERACTION_TIMEOUT):
        self.func = function
        self.func_param = func_param

        if config.DEBUG_VERBOSE:
            print ("CustomSelect select_param")
            print (select_param)

        i = 0
        options = []
        while i < len(select_param):
            #print ("CustomSelect i "+str(i))
            #if config.DEBUG :
            # print(select_param[i])
            #if not select_param[i]["emoji"] == None:
            options.append( discord.SelectOption(value=select_param[i]["id"], label=select_param[i]["label"], description=select_param[i]["description"], emoji=select_param[i]["emoji"]) )
            #else:
            #    options.append( discord.SelectOption(value=select_param[i]["id"], label=select_param[i]["label"], description=select_param[i]["description"]) )
            i+=1

        super().__init__(placeholder=placeholder,options=options, max_values=1)

    async def callback(self, interaction: discord.Interaction):
        await self.func(interaction, self, self.func_param)

class ViewSelectWithCustomId(View):
    def __init__(self, view_param, timeout = config.DISCORD_INTERACTION_TIMEOUT, function_interaction_check = func_DefaultInteraction):
        if config.DEBUG_VERBOSE:
            print ("ViewSelectWithCustomId view_param")
            print (view_param)
        super().__init__(timeout=timeout)  # Imposta un timeout di 10 secondi
        self.message = None
        self.function_interaction_check = function_interaction_check
        i = 0
        if config.DEBUG_VERBOSE:
            print("ViewSelectWithCustomId len(view_param) "+str(len(view_param)))
        
        while i < len(view_param):
            #print ("ViewSelectWithCustomId i "+str(i))
            itemx= CustomSelect(
                placeholder=view_param[i]["placeholder"], select_param=view_param[i]["select_param"],
                function=view_param[i]["func"], func_param=view_param[i]["func_param"]
                )
            #print("itemx " + str(itemx))
        
            #print("len(self.children)"+ str(len(self.children)))
            self.add_item( itemx )
            i+=1

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return self.function_interaction_check(interaction)

    async def on_timeout(self):
        for child in self.children:
            child.disabled = True

        if self.message:
            try:
                await self.message.edit(view=self)
            except discord.NotFound:
                pass

#
# la funzione chiamante deve avere await interaction.response.defer(thinking=True, ephemeral=True)  # Mostra un "sta pensando..."
async def SplitSelectOptionsOnViews(interaction: discord.Interaction , message: str, placeholder: str, l: list, f: typing.Callable, func_param: dict):
    len_l = len(l)
    if len_l == 0:
        raise Exception("Si deve passare almeno un opzione")

    k = 0
    j = 0
    i= 0
    while i+j*DISCORD_SELECT_OPTIONS_MAX+k*DISCORD_SELECT_MAX*DISCORD_SELECT_OPTIONS_MAX < len_l:
        # view di 5 select
        viewcustom_params = []
        while i+j*DISCORD_SELECT_OPTIONS_MAX+k*DISCORD_SELECT_MAX*DISCORD_SELECT_OPTIONS_MAX < len_l and j < DISCORD_SELECT_MAX:
            #select di 25 options
            selectcustom_params = []
            while i+j*DISCORD_SELECT_OPTIONS_MAX+k*DISCORD_SELECT_MAX*DISCORD_SELECT_OPTIONS_MAX < len_l and i < DISCORD_SELECT_OPTIONS_MAX:
                pointer = i+j*DISCORD_SELECT_OPTIONS_MAX+k*DISCORD_SELECT_MAX*DISCORD_SELECT_OPTIONS_MAX
                selectcustom_params.append({ "id": l[pointer]["id"], "label": l[pointer]["label"],
                    "description": "" , "emoji": l[pointer]["emoji"]})
                i+=1
            viewcustom_params.append( { "placeholder": placeholder + str(k*DISCORD_SELECT_MAX+j+1),
                "select_param": selectcustom_params, "func": f, "func_param": func_param })
            i=0
            j+=1
        #if k == 0: else:
        tmp_view = ViewSelectWithCustomId(viewcustom_params)
        tmp_view.message = await interaction.followup.send(message,view=tmp_view, ephemeral=True)
        #tmp_view.message = await interaction.original_response()  # Ottieni il messaggio per modificarlo dopo il timeout
        j=0
        k+=1



'''
class GenericView(discord.ui.View):
    def __init__(self, func_interaction ):
        super().__init__(timeout=timeout)
        self.func_interaction = func_interaction

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return function_interaction(interaction)


class ViewButtonChoiceList(View):
    def __init__(self, list_items, func1, func2, discordId):
        super().__init__()

        self.list_items = list_items
        self.func1 = func1
        self.func2 = func2
        self.playerId = MyDBInterface.getMemberId(discordId)
        print(self.playerId)
        # Aggiungiamo i pulsanti dinamicamente
        print("list_items[i]")
        for i, option in enumerate(list_items):
            print(list_items[i])
            self.add_item(Button(label=str(i+1), style=discord.ButtonStyle.primary, custom_id=str(self.list_items[i]["id"])))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        # Risponde dinamicamente a seconda del pulsante premuto
        itemId = int(interaction.data["custom_id"])
        # Chiama la funzione con l'oggetto richiesto
        self.func1()
        i = 0
        flag = 1
        description = ""
        while i < len(self.list_items) and flag:
            if self.list_items[i]["id"] == itemId:
                description=self.list_items[i]["idItemNavigation"]["itemName"]
                flag = 0
            i+=1
        await interaction.response.send_message(f"Hai scelto l'item **{description}**! Qual'è il motivo della tua richiesta?", ephemeral=True)
        for i, option in enumerate(list_items):
            print(list_items[i])
            self.add_item(Button(label=str(i+1), style=discord.ButtonStyle.primary, custom_id=str(self.list_items[i]["id"])))

        if self.playerId == -1:
            await interaction.response.send_message(f"Non sei registrato alla piattaforma utilizza /register **NomeInGioco**!", ephemeral=True)
            return -1
        else:
            return self.func2(self.playerId, int(itemId), "prova di loretta")

        list_request_options = [ "BIS WISH", "BIS non WISHLIST", "TRATTO" ]

class LetterButton(discord.ui.Button):
    def __init__(self, letter: str):
        discord.ui.Button(label=letter, custom_id="numerobottone"+letter, style=discord.ButtonStyle.primary)
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"Hai cliccato la lettera **{self.label}** numero **{self.custom_id}**!", ephemeral=True)
'''