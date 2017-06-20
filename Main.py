##########################################################################################################################
#
#                              ####                                                                                   #### 
#                              ####                                                                                   #### 
#                              ####                                                                                   #### 
#                              ####                                                                                   #### 
#                              ########################################################################################### 
#                              ########################################################################################### 
#                              ########################################################################################### 
#                              ########################################################################################### 
#                              ########################################################################################### 
#                              ########################################################################################### 
#                              ########################################################################################### 
#                              ########################################################################################### 
#                              ########################################################################################### 
#                              ####                                              ####                                 #### 
#                              ####                                              ####                                 #### 
#                              ####                                              ####                                 #### 
#                              ####                                              ####                                 #### 
#                              ####                                              ####                                 #### 
#                              ####                                              ####                                 #### 
#                              ####                                              ####                                 #### 
#                              ####                                              ####                                 #### 
#                              ####                                              ####                                 #### 
#                              ####                                              ####                                 #### 
#                              ####                                              #####                               ##### 
#                              #####                                            ######                               ##### 
#                              #####                                            ######                               ##### 
#                              ######                                          ########                             ###### 
#                               ######                                        #########                             ###### 
#                               #######                                      ###########                           ###### 
#                               ########                                    ##############                       ######## 
#                                ########                                  ################                     ######### 
#                                #########                                ###################                 ########## 
#                                 ##########                            ########################           ############# 
#                                 #############                      ############   ################################### 
#                                  ################              ###############     ################################# 
#                                   ###########################################       ############################### 
#                                    #########################################         ############################# 
#                                     #######################################            ######################### 
#                                      #####################################               ##################### 
#                                        #################################                    ############### 
#                                          #############################                         ######### 
#                                             ######################## 
#                                                ################ 
#
############################################################################################################################
#                By Kaburu                                              #
############################################################################################################################


import subprocess
import os
import ConfigParser
import sys
"""
Read the Config file and return a config object
"""





def configs():
    config = ConfigParser.ConfigParser()
    config.read('config.ini')
    return config




def mapconfig(config,section):
    confdict = {}

    for option in config.options(section):
        confdict[option]=config.get(section,option)

    return confdict





def RunCommands(command):
    res = subprocess.call(command,shell=True)
    return res






def addCron(cron,ssh,backupdir,location):
        fileName =location.replace('/','_')
        bc_sh_content =  "tt=(\`date +%Y-%b-%d-%H-%M-%S\`) ;"+"cd "+ location +" ;"+"bfile="+backupdir+"/"+fileName+"_\$tt.tar.gz; tar --exclude ./bc.sh  -zcvf \$bfile . ;  scp \$bfile "+MainConfigs['username']+"@"+MainConfigs['backupserver']+":"
        bcfile = location+"/bc.sh"
        createshCommand = ssh + " 'cd "+location+ "  && echo \""+bc_sh_content+"\" > "+bcfile+"' "
        createsh = RunCommands(createshCommand)
        if createsh == 0:
            createCronCm = ssh + " \" crontab -l > tmp ; echo '"+cron+" bash "+location+"/bc.sh' >> tmp ; crontab tmp ; rm -rf tmp \""
            cronRes = RunCommands(createCronCm)
            if cronRes == 0:
                print bcfile+" ::Cron installed successfully"
            else:
                print "Unable to install the cron for ::: "+bcfile
        else:
            print "We are unable to generate bc.sh file on the server, check the permissions maybe: Here is the response::: \n"+createsh







def process(server,configs,ssh):
    print server +": processing ... \n"
    serverConfigs = mapconfig(configs,server)
    dirs = serverConfigs['datadirs'].split(",")
    for directory in dirs:
        cronTime = directory[directory.find("[")+1:directory.find("]")]
        Cdirectory = directory.split('[')[0]
        stringCron = cronTime + " cd  "+Cdirectory+'/bc.sh'
        escapedStars = Cdirectory+'/bc.sh'

        command  = ssh + " 'crontab -l | grep \""+escapedStars +"\" ' "
        checkCron = RunCommands(command)
        if checkCron == 1:
                addCron(cronTime,ssh,serverConfigs['backuplocation'],Cdirectory)
        
        else:
            print "The cron exists"


           







def init():
    Os = os.uname()
    if Os[0] != 'Linux':
        sys.exit('This only runs on Linux based servers')
        
    Configurations = configs()
    global MainConfigs
    MainConfigs = mapconfig(Configurations,"main")

    servers = Configurations.sections()
    servers.remove("main")
    for server in servers:
        ssh = "ssh "+MainConfigs['username']+"@"+server
        process(server,Configurations,ssh)

if __name__ ==  "__main__" :
    init()


