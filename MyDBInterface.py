import requests

import config
import secret

'''
ACCOUNT MANAGEMENT
'''
async def getMemberName(discordId: str):
    if config.DEBUG_VERBOSE:
        print("getMemberName")
    url = secret.nGrokURI+"/MembersApi/GetAllMembers"

    response = requests.get(url)
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        return

    data = response.json()

    i = 0
    flag = 1
    ret = -1
    while i < len(data) and flag:
        if config.DEBUG_VERBOSE:
            print("getMemberName data" + str(data[i]))
        try:
            if data[i]["characterName"] == discordId or data[i]["secondaryCharacterName"] == discordId:
                ret = data[i]["name"]
                if config.DEBUG:
                    print(type(ret))
                    print("getMemberName ret"+ret)
                flag = 0
        except Exception as e:
                print(str(data[i]) + " record errato")
        finally:
            i += 1
    if config.DEBUG_VERBOSE:
        print ("ret " + str(ret))
    return ret

async def getMemberId(discordId: str):
    if config.DEBUG_VERBOSE:
        print("getMemberId")
    url = secret.nGrokURI+"/MembersApi/GetAllMembers"

    response = requests.get(url)
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        return

    data = response.json()

    i = 0
    flag = 1
    ret = -1
    while i < len(data) and flag:
        if config.DEBUG_VERBOSE:
            print(data[i])
        try:
            if data[i]["characterName"] == discordId or data[i]["secondaryCharacterName"] == discordId:
                ret = data[i]["idMembers"]
                flag = 0
        except Exception as e:
                print(str(data[i]) + " record errato")
        i += 1
    if config.DEBUG_VERBOSE:
        print ("ret " + str(ret))
    return ret

async def getPlayerIdFromName(playerName: str):
    if config.DEBUG_VERBOSE:
        print("getPlayerIdFromName")
    url = secret.nGrokURI+"/MembersApi/GetAllMembers"

    response = requests.get(url)

    if response.status_code != 200:
        if config.DEBUG:
            print(f"Error: {response.status_code}")

    data = response.json()
    if config.DEBUG_VERBOSE:
        print(data)

    i = 0
    flag = 1
    ret = -1
    while i < len(data) and flag:
        try:
            if data[i]["name"] == playerName:
                if config.DEBUG_VERBOSE:
                    print(data[i])
                ret = data[i]["idMembers"]
                flag = 0
                if config.DEBUG_VERBOSE:
                    print(f"getPlayerIdFromName id trovato: {ret}")
        except Exception as e:
                print(f"getPlayerIdFromName record errato: {str(data[i])}")
        finally:
            i += 1
    return int(ret)

async def CreateAccount(playerName: str, discordId: str):
    if config.DEBUG_VERBOSE:
        print("CreateAccount")
    url = secret.nGrokURI+"/MembersApi"
    data = { "name": playerName, "characterName": discordId}
#    if DEBUG:
    print(data)
    response = requests.post(url, json=data)

    if config.DEBUG_VERBOSE:
        print ("CreateAccount\n {response.json()}")
    ret = -1
    if response.status_code != 201:
        print(f"Error: {response.status_code}")
    else:
        print(f"Creato utente {response.json()["characterName"]} numero {response.json()["idMembers"]}")
        ret = response.json()["idMembers"]
    return ret

async def postPlayerName1(playerName: str, discordId: str):
    if config.DEBUG_VERBOSE:
        print("postPlayerName1")
    url = secret.nGrokURI+"/MembersApi"
    data = { "idMembers": playerName, "characterName": discordId }
    response = requests.post(url, json=data)

    if response.status_code != 200:
        print(f"postPlayerName1 Error: {response.status_code}")


async def getDiscordId1(playerName: str):
    if config.DEBUG_VERBOSE:
        print("getPlayerIdFromName")
    url = secret.nGrokURI+"/MembersApi/GetAllMembers"

    response = requests.get(url)

    if response.status_code != 200:
        print(f"getDiscordId1 Error: {response.status_code}")

    data = response.json()

    i = 0
    flag = 1
    ret = -1
    while i < len(data) and flag:
        try:
            if data[i]["name"] == playerName:
                ret = data[i]["characterName"]
                flag = 0
                if config.DEBUG_VERBOSE:
                    print(f"getDiscordId1 discordId trovato: {ret}")
        except Exception as e:
                print(f"getDiscordId1 record errato: {str(data[i])}")
        finally:
            i += 1
    return ret

async def postPlayerName2(playerId: int, playerName: str, discordId1: str, discordId2: str):
    if config.DEBUG_VERBOSE:
        print("postPlayerName2")
    url = secret.nGrokURI+"/MembersApi/"+str(playerId)
    if config.DEBUG_VERBOSE:
        print("URL: {url}")
                
    data =  { "idMembers": playerId, "name": playerName, "characterName": discordId1, "secondaryCharacterName": discordId2 }
    response = requests.put(url, json=data)

    if response.status_code != 204:
        print(f"postPlayerName2 Error: {response.status_code}")
        return -1
    return 0

'''
GENERIC
'''
async def getAllDKP():
    if config.DEBUG_VERBOSE:
        print("getAllDKP")
    url = secret.nGrokURI+"/ClassificaApi"
    response = requests.get(url)

    if response.status_code != 200:
        print(f"getAllDKP Error: {response.status_code}")
        return -1
    data = response.json()
    if config.DEBUG_VERBOSE:
        print (data)
    return data

'''
ALL ITEMS
'''
async def listItems():
    if config.DEBUG_VERBOSE:
        print("listItems")
    url = secret.nGrokURI+"/ItemsApi?pageNumber=0&pageSize=0"
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Error: {response.status_code}")
    data = response.json()
    if config.DEBUG_VERBOSE:
        print (data)
    itemdata = []
    for row in data:
        itemdata.append({"itemId": row["idItem"], "itemName": row["itemName"], "tier":row["tier"]})
    return itemdata

async def listArchbossItems():
    if config.DEBUG_VERBOSE:
        print("listArchbossItems")
    url = secret.nGrokURI+"/ItemsApi?pageNumber=0&pageSize=0"
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Error: {response.status_code}")
    data = response.json()
    if config.DEBUG_VERBOSE:
        print (data)
    archdata = []
    for row in data:
        if config.DEBUG_VERBOSE:
            print (f"listArchbossItems row {row}")
        if row["tier"] == 0:
            archdata.append({"itemId": row["idItem"], "itemName": row["itemName"]})
    return archdata

async def listT2Items():
    if config.DEBUG_VERBOSE:
        print("listT2Items")
    url = secret.nGrokURI+"/ItemsApi?pageNumber=0&pageSize=0"
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Error: {response.status_code}")
    data = response.json()
    if config.DEBUG_VERBOSE:
        print (data)
    t2data = []
    for row in data:
        if config.DEBUG_VERBOSE:
            print (row)
        if row["tier"] == 2:
            t2data.append({"itemId": row["idItem"], "itemName": row["itemName"], "idBoss": row["idBoss"]})
    return t2data

'''
AVAILABLE ITEMS
'''
async def listAvailableItems():
    if config.DEBUG_VERBOSE:
        print("listAvailableItems")
    url = secret.nGrokURI+"/DroppedItemsApi/AvailableDroppedItems"
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Error: {response.status_code}")
    elif response.status_code == 204:
        return False
    data = response.json()
    if config.DEBUG_VERBOSE:
        print (data)
    return data

async def requestAvailableItem(playerId: int, itemId: int, reason: str):
    if config.DEBUG_VERBOSE:
        print("requestAvailableItem")
    data = { "idMember": playerId, "idLeftItemInGuildStorage": itemId, "Reason": reason}
    #if config.DEBUG_VERBOSE:
    print (data)

    url = secret.nGrokURI+"/DroppeditemsrequestsApi"
    response = requests.post(url, json=data)

    ret = None
    if response.status_code == 201:
        ret = response.json()
    else:
        ret = response.status_code
    print (ret)
    if config.DEBUG_VERBOSE:
        print (ret)
    return ret


async def listAvailableItemsRequested(discordId: str):
    if config.DEBUG_VERBOSE:
        print("listAvailableItemsRequested")
    url = secret.nGrokURI+"/DroppeditemsrequestsApi"
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        return None
    if config.DEBUG_VERBOSE:
        print (response.json())
    ret = response.json()
    if config.DEBUG_VERBOSE:
        print("listAvailableItemsRequested ret")
        print (ret)
    if len(ret) == 0:  # non ci sono item richiesti (da nessuno)
        return ret

    playerId = await getMemberId(str(discordId))
    listrequests= []
    i = 0
    while i < len (ret):
        if ret[i]["idMember"] == playerId:
            if ret[i]["idLeftItemInGuildStorageNavigation"]["distributedDate"] == None:
                listrequests.append( { "id": ret[i]["idDroppedItemsRequests"], "idLeftItemInGuildStorage": ret[i]["idLeftItemInGuildStorage"], 
                    "description": ret[i]["idLeftItemInGuildStorageNavigation"]["idItemNavigation"]["itemName"], "reason": ret[i]["reason"], "requestDate": ret[i]["requestDate"]} )
        i+=1
    return listrequests

'''
WISH LIST
'''
async def requestWishItem(playerId: int, itemId: int):
    print("requestWishItem")
    data = { "itemId": itemId, "playerId": playerId }

    url = secret.nGrokURI+"/ItemRequestsApi"
    response = requests.post(url, json=data)

    if response.status_code != 201:
        print(f"Error: {response.status_code}")
        ret = None
    else:
        data = response.json()
    if config.DEBUG_VERBOSE:
        print (data)
    return data

async def listPlayerWishItems(playerId: int):
    print("listPlayerWishItems")
    url = secret.nGrokURI+"/ItemRequestsApi/GetItemRequestsByMemberIdApi/"+str(playerId)
    print (url)
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        return -1
    else:
        data = response.json()
    if config.DEBUG_VERBOSE:
        print (data)
    ret = []
    i = 0
    flag = 1
    while i < len(data) and flag:
        if data[i]["playerId"] == playerId:
            ret.append( { "idItemRequest": data[i]["idItemRequest"], "itemName": data[i]["item"]["itemName"] } )
        i+=1
    return ret

    '''    print("listPlayerWishItems")
    url = secret.nGrokURI+"/ItemRequestsApi?pageNumber=1&pageSize=999999"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
    else:
        data = response.json()
    if config.DEBUG:
        print (data)
    ret = []
    i = 0
    flag = 1
    while i < len(data) and flag:
        if data[i]["playerId"] == playerId:
            ret.append( { "idItemRequest": data[i]["idItemRequest"], "itemName": data[i]["item"]["itemName"] } )
        i+=1
    return ret
    '''
'''
TO DO

async def listPlayerWishItems(playerId: int):
    print("listPlayerWishItems")
    url = nGrokURI+"/ItemRequestsApi?pageNumber=1&pageSize=999999"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
    ret = []
    i = 0
    flag = 1
    while i < len(response.json) and flag:
        if response[i]["idMember"] == playerId:
            ret.append(response[i])
        i+=1
    return ret
'''
async def listRequestItems():
    print("listRequestItems")
    url = secret.nGrokURI+"/ItemRequestsApi?pageNumber=0&pageSize=0"
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Error: {response.status_code}")
    data = response.json()
    if config.DEBUG_VERBOSE:
        print (data)
    return data


def listItemRequests(int_itemId):
    print("listItemRequests")
    url = secret.nGrokURI+"/ItemRequestsApi/"+int_itemId
    response = requests.get(url)

    if response.status_code != 200:
        print(f"listItemRequests Error: {response.status_code}")
    data = response.json()
    if config.DEBUG_VERBOSE:
        print (data)
    return data

