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
#                By Kaburu                                                                                                 #
############################################################################################################################

from datetime import datetime
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
        fileName =location.replace('/','_').strip()
        bc_sh_content =  "tt=(\`date +%Y-%b-%d-%H-%M-%S\`) ;"+"cd "+ location+" ;bfile="+backupdir+"/"+fileName +"_\$tt.tar.gz; tar   -zcvf \$bfile . ;  scp \$bfile "+MainConfigs['username']+"@"+MainConfigs['backupserver']+":"
        #We keep all the shell scripts on user's home directory. This is to avoid write/execute permmision issues.
        cronscriptsCommand = ssh + " ' cd ~ ; pwd  '"
        p = subprocess.Popen(cronscriptsCommand, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
        userHome = p.stdout.read()
       #Let's create the directory crons if it doesn't exist
        cronDir = str(userHome).strip()+"/crons/"
        createDIR = ssh +" 'if  [ ! -d "+cronDir+" ]; then  mkdir -p  "+cronDir +"; else exit 0 ; fi ' "
        if (RunCommands(createDIR) != 0):
            print "We are unable to create DIR : "+cronDir+" \n"
            sys.exit()
        
        bcfile = cronDir+fileName+".sh"
        createshCommand = ssh + " 'cd "+location+ "  && echo \""+bc_sh_content+"\" > "+bcfile+"' "
        createsh = RunCommands(createshCommand)
       
       
        if createsh == 0:
            createCronCm = ssh + " \" crontab -l > tmp ; echo '"+cron+" bash "+bcfile+" ' >> tmp ; crontab tmp ; rm -rf tmp \""
            cronRes = RunCommands(createCronCm)
            if cronRes == 0:
                print ttime+"| "+bcfile+" ::Cron installed successfully"
            else:
                print ttime+"|  Unable to install the cron for ::: "+bcfile
                sys.exit()
        else:
            print ttime+"| We are unable to generate "+bcfile+ " file on the server, check the permissions maybe: Here is the response::: \n"+createsh
            sys.exit()







def process(server,configs,ssh):
    print ttime+"| "+server +": processing ... \n"
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
            print ttime+"| The cron exists"


           







def init():
    Os = os.uname()
    if Os[0] != 'Linux':
        sys.exit('This only runs on Linux based servers')
        
    Configurations = configs()
    global MainConfigs
    MainConfigs = mapconfig(Configurations,"main")
    global ttime
    ttime = str(datetime.now())
    servers = Configurations.sections()
    servers.remove("main")
    for server in servers:
        ssh = "ssh "+MainConfigs['username']+"@"+server
        process(server,Configurations,ssh)

if __name__ ==  "__main__" :
    init()


