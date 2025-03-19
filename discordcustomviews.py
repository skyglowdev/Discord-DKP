import discord
from discord.ui import Button, View

import config
import MyDBInterface

DISCORD_SELECT_MAX = 5
DISCORD_SELECT_OPTIONS_MAX = 5
DISCORD_BUTTON_MAX = 25

def func_DefaultInteraction(interaction: discord.Interaction):
    return True

'''
ViewButtonNumberedWithCustomId
'''

class CustomButton(discord.ui.Button):
    def __init__(self, label: str, function, param, style=discord.ButtonStyle.primary):
        if config.DEBUG:
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
    def __init__(self, button_param, function_interaction_check = func_DefaultInteraction):
        if config.DEBUG:
            print ("ViewButtonNumberedWithCustomId param")
            print (button_param)
        super().__init__()
        print ("ViewButtonNumberedWithCustomId button_param")
        print (button_param)
        self.function_interaction_check = function_interaction_check
        i = 0
        while i < len(button_param):
            if config.DEBUG :
                print(button_param[i])
            self.add_item (CustomButton( label=button_param[i]["label"], style=discord.ButtonStyle.primary, function=button_param[i]["func"], param=button_param[i]["func_param"] ) )
            i+=1

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return self.function_interaction_check(interaction)

'''
ViewSelectWithCustomId
'''
class CustomSelect(discord.ui.Select):
    def __init__(self, placeholder: str, select_param: list, function, func_param):
        self.func = function
        self.func_param = func_param

        if config.DEBUG:
            print ("CustomSelect select_param")
            print (select_param)

        i = 0
        options = []
        while i < len(select_param):
            #print ("CustomSelect i "+str(i))
            #if config.DEBUG :
            # print(select_param[i])
            if not select_param[i]["emoji"] == None:
                options.append( discord.SelectOption(value=select_param[i]["id"], label=select_param[i]["label"], description=select_param[i]["description"], emoji=select_param[i]["emoji"]) )
            else:
                options.append( discord.SelectOption(value=select_param[i]["id"], label=select_param[i]["label"], description=select_param[i]["description"]) )
            i+=1

        super().__init__(placeholder=placeholder,options=options, max_values=1)

        '''        options = [
            discord.SelectOption(label="Opzione 1", description="Descrizione 1"),
            discord.SelectOption(label="Opzione 2", description="Descrizione 2"),
            discord.SelectOption(label="Opzione 3", description="Descrizione 3"),
        ]
        '''
    async def callback(self, interaction: discord.Interaction):
        await self.func(interaction, self.func_param, self)

class ViewSelectWithCustomId(View):
    def __init__(self, view_param, function_interaction_check = func_DefaultInteraction):

        super().__init__()
        
        if config.DEBUG:
            print ("ViewSelectWithCustomId view_param")
            print (view_param)
        super().__init__()
        test_select = discord.ui.Select(placeholder="Test", options=[
            discord.SelectOption(label="Opzione 1", value="id_1"),
            discord.SelectOption(label="Opzione 2", value="id_2")
            ])
        if config.DEBUG:
            print("test_select " + str(test_select))
        self.function_interaction_check = function_interaction_check
        #i= 0
        i = 0
        if config.DEBUG:
            print("ViewSelectWithCustomId len(view_param) "+str(len(view_param)))
        DISCORD_SELECT_MAX
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