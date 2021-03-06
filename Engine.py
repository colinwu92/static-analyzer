import multiprocessing 
import time
import subprocess 
import os 
import shutil  
import Utils

class Engine:  

    #tried to avoid linux sepcific commands   

    def __init__(self, location, schedule):    
        self.__location = location 
        self.__schedule = schedule 

    #Overall workflow of Enigne 
        #public interfacing function run 
        #copies files to be scanned and puts into temp repo 
        #for each task in schedule, makes a new process to run static analyzer on files  
        #exits when all processes are done 
    def run(self):

        #cloning repo  
        try: 
            excps = []
            shutil.copytree(self.__location, "temp")  
        except FileExistsError as excp:
            Utils.printErrorMessage(message="TEMP ALREADY EXISTES PLEASE RENAME OR DELETE") 
            exit(1) 
        except FileNotFoundError as excp: 
            Utils.printErrorMessage(message="PATH TO SRC DOSEN'T EXIST") 
            exit(1)
        except shutil.Error as excp: 
            Utils.printErrorMessage(message ="CHOULDN'T COPY FILES TO SCAN") 
            exit(1) 
        
        os.chdir("temp") 

        #run static analyzers 
        self.__invokeTools(schedule=self.__schedule)

        #delete repo when processes and scans are done 
        os.chdir(os.path.dirname(os.getcwd()))  
        shutil.rmtree("temp")

       


    #makes a process for each task and runs the task
    def __invokeTools(self, schedule): 

        procs = []    
        Utils.printNotiMessage("BOOTING STATIC ANALYZERS...") 

        for task in schedule: 
            #make and start new process
            
            p = multiprocessing.Process(target = self.__invokeTool(task=task))  
            p.start() 
            procs.append(p) 

    

        #wait for all threads to finish   
        for proc in procs: 
            proc.join() 
        Utils.printNotiMessage("SCANS DONE")

    #invokes the tool via provided command (absolute path)
    def __invokeTool(self, task): 
        Utils.printNotiMessage("RUNNING " + task.getToolName() + "...") 
        command = task.getCommand().split(" ") 
        #potential security input check??
        retCode = subprocess.run(command).returncode     
        if (retCode != 0): 
            Utils.printErrorMessage(task.getToolName() + " SCAN FAILED; CHECK ITS LOGS") 
        else:
            Utils.printNotiMessage(task.getToolName() + " SCAN SUCESSFUL")  
        