import config

playerlist = [
                {"PolloAlCarry" , "Ciao Puffo! Mi spiace ma posso solo mostrarti i DKP di PolloAlCarry"},
                {"TeoxJust" , "Grazie di essere il nostro miglior frontliner"},
                {"PippoFranchino" , "RAA-RAA-RAA"}
                ]

def easteregg(playerName: str):
    if not config.EASTER_EGG:
        return None
    for name, msg in playerlist:
         if name == playerName:
            return msg
    return None