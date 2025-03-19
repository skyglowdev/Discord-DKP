len_list_items = 137
discordcustomviews.DISCORD_SELECT_MAX =5
discordcustomviews.DISCORD_SELECT_OPTIONS_MAX = 25
k = 0
j = 0
i= 0

#k = max1*max2
while i+j*discordcustomviews.DISCORD_SELECT_OPTIONS_MAX+k*discordcustomviews.DISCORD_SELECT_MAX*discordcustomviews.DISCORD_SELECT_OPTIONS_MAX < len_list_items:
    print("K "+str(k))
    while i+j*discordcustomviews.DISCORD_SELECT_OPTIONS_MAX+k*discordcustomviews.DISCORD_SELECT_MAX*discordcustomviews.DISCORD_SELECT_OPTIONS_MAX < len_list_items and j < discordcustomviews.DISCORD_SELECT_MAX:
        print("J "+str(j))
        while i+j*discordcustomviews.DISCORD_SELECT_OPTIONS_MAX+k*discordcustomviews.DISCORD_SELECT_MAX*discordcustomviews.DISCORD_SELECT_OPTIONS_MAX < len_list_items and i < discordcustomviews.DISCORD_SELECT_OPTIONS_MAX:
            print("i"+str(i))
            print("k = " +str(k)+" j = " +str(j)+" i = " +str(i))
            print ("i+j*max1+k*max1*max2 " + str(i+j*discordcustomviews.DISCORD_SELECT_OPTIONS_MAX+k*discordcustomviews.DISCORD_SELECT_MAX*discordcustomviews.DISCORD_SELECT_OPTIONS_MAX))
            i+=1
        i=0
        j+=1
    j=0
    k+=1