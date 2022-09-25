from PySide6.QtCore import *
import subprocess, os, sys, re
from tools import *

ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')

def searchForPackage(signal: Signal, finishSignal: Signal) -> None:
    print("[   OK   ] Starting scoop search...")
    p = subprocess.Popen(' '.join(["powershell", "-Command", "scoop", "search"]), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE, cwd=os.getcwd(), env=os.environ, shell=True)
    output = []
    counter = 0
    while p.poll() is None:
        line = p.stdout.readline()
        line = line.strip()
        if line:
            if(counter > 1 and not b"---" in line):
                output.append(ansi_escape.sub('',                 #print(line, ansi_escape.sub('', str(line, encoding='utf-8', errors="ignore")))
str(line, encoding='utf-8', errors="ignore")))
            else:
                counter += 1
    counter = 0
    lc = getSettings("LowercaseScoopApps")
    for element in output:
        try:
            signal.emit(element.split(" ")[0].strip() if lc else element.split(" ")[0].strip().capitalize(), f"{element.split(' ')[0].strip()}", list(filter(None, element.split(" ")))[1].strip(), f"Scoop: {list(filter(None, element.split(' ')))[2].strip()}")
        except IndexError as e:
            print("IndexError: "+str(e))
    print("[   OK   ] Scoop search finished")
    finishSignal.emit("scoop")

def searchForInstalledPackage(signal: Signal, finishSignal: Signal) -> None:
    print("[   OK   ] Starting scoop search...")
    p = subprocess.Popen(' '.join(["powershell", "-Command", "scoop", "list"]), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE, cwd=os.getcwd(), env=os.environ, shell=True)
    output = []
    counter = 1
    while p.poll() is None:
        line = p.stdout.readline()
        line = line.strip()
        if line:
            if(counter > 1 and not b"---" in line):
                output.append(ansi_escape.sub('', str(line, encoding='utf-8', errors="ignore").strip()))
            else:
                counter += 1
    counter = 0
    lc = getSettings("LowercaseScoopApps")
    for element in output:
        try:
            items = list(filter(None, element.split(" ")))
            if(len(items)>=2):
                signal.emit(items[0] if lc else items[0].capitalize(), f"{items[0]}", items[1], "Scoop")
        except IndexError as e:
            print("IndexError: "+str(e))
        except Exception as e:
            print(e)
    print("[   OK   ] Scoop search finished")
    finishSignal.emit("scoop")

def searchForUpdates(signal: Signal, finishSignal: Signal) -> None:
    print("[   OK   ] Starting scoop search...")
    p = subprocess.Popen(' '.join(["powershell", "-Command", "scoop", "status"]), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE, cwd=os.getcwd(), env=os.environ, shell=True)
    output = []
    counter = 0
    while p.poll() is None:
        line = p.stdout.readline()
        line = line.strip()
        if line:
            if(counter > 1 and not b"---" in line):
                output.append(ansi_escape.sub('', str(line, encoding='utf-8', errors="ignore").strip()))
            else:
                counter += 1
    counter = 0
    lc = getSettings("LowercaseScoopApps")
    for element in output:
        if "WARN" in output:
            continue
        if "fatal" in output:
            continue
        try:
            signal.emit(element.split(" ")[0].strip() if lc else element.split(" ")[0].strip().capitalize(), f"{element.split(' ')[0].strip()}", list(filter(None, element.split(" ")))[1].strip(), list(filter(None, element.split(" ")))[2].strip(), "Scoop")
        except IndexError as e:
            print("IndexError: "+str(e))
        except Exception as e:
            print(e)
    print("[   OK   ] Scoop search finished")
    finishSignal.emit("scoop")

def getInfo(signal: Signal, title: str, id: str, goodTitle: bool) -> None:
    print(f"[   OK   ] Starting get info for title {title}")
    title = title.lower()
    p = subprocess.Popen(' '.join(["powershell", "-Command", "scoop", "info", f"{title}", "--verbose"]), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE, cwd=os.getcwd(), env=os.environ, shell=True)
    output = []
    appInfo = {
        "title": title,
        "id": id,
        "publisher": "Unknown",
        "author": "Unknown",
        "description": "Unknown",
        "homepage": "Unknown",
        "license": "Unknown",
        "license-url": "Unknown",
        "installer-sha256": "Unknown",
        "installer-url": "Unknown",
        "installer-type": "Scoop shim",
        "manifest": "Unknown",
        "versions": [],
    }
    while p.poll() is None:
        line = p.stdout.readline()
        line = line.strip()
        if line:
            output.append(ansi_escape.sub('', str(line, encoding='utf-8', errors="ignore")))
    manifest = False
    version = ""
    lc = getSettings("LowercaseScoopApps")
    for line in output:
        #print(line)
        if("Description" in line):
            appInfo["description"] = line.replace("Description", "").strip()[1:].strip()
        elif("Website" in line):
            appInfo["homepage"] = line.replace("Website", "").strip()[1:].strip()
        elif("Version" in line):
            version = line.replace("Version", "").strip()[1:].strip()
        elif("Updated by" in line):
            appInfo["publisher"] = line.replace("Updated by", "").strip()[1:].strip()
            appInfo["author"] = line.replace("Updated by", "").strip()[1:].strip()
        elif("License" in line):
            appInfo["license"] = line.replace("License", "").strip()[1:].strip().split("(")[0].strip()
            try:
                appInfo["license-url"] = line.replace("License", "").strip()[1:].strip().split("(")[1].strip().replace(")", "")
            except IndexError:
                pass
        elif("Manifest" in line):
            #print("ok")
            appInfo["manifest"] = line.replace("Manifest", "").strip()[1:].strip()
            try:
                print("ok")
                mfest = open(appInfo["manifest"])
                import json
                data = json.load(mfest)
                print("ok")
                try:
                    appInfo["installer-url"] = data["url"]
                    appInfo["installer-sha256"] = data["hash"]
                except KeyError:
                    appInfo["installer-url"] = data["architecture"]["64bit"]["url"]
                    appInfo["installer-sha256"] = data["architecture"]["64bit"]["hash"]
                appInfo["installer-type"] = "Scoop package"
                try:
                    appInfo["description"] = data["description"] if data["description"] != "" else appInfo["description"]
                except KeyError:
                    print("[  WARN  ] No description found in the manifest")
            except Exception as e:
                print(type(e), e)
    print(f"[  INFO  ] Scoop does not support specific version installs")
    appInfo["versions"] = [version]
    appInfo["title"] = appInfo["title"] if lc else appInfo["title"].capitalize()
    signal.emit(appInfo)
    
def installAssistant(p: subprocess.Popen, closeAndInform: Signal, infoSignal: Signal, counterSignal: Signal) -> None:
    print(f"[   OK   ] scoop installer assistant thread started for process {p}")
    outputCode = 1
    output = ""
    while p.poll() is None:
        line = p.stdout.readline()
        line = line.strip()
        line = str(line, encoding='utf-8', errors="ignore").strip()
        if line:
            if("Installing" in line):
                counterSignal.emit(1)
            elif("] 100%" in line or "Downloading" in line):
                counterSignal.emit(4)
            elif("was installed successfully!" in line):
                counterSignal.emit(6)
            infoSignal.emit(line)
            if("was installed successfully" in line):
                outputCode = 0
            elif ("is already installed" in line):
                outputCode = 0
            output += line+"\n"
    closeAndInform.emit(outputCode, output)

   
def uninstallAssistant(p: subprocess.Popen, closeAndInform: Signal, infoSignal: Signal, counterSignal: Signal) -> None:
    print(f"[   OK   ] scoop uninstaller assistant thread started for process {p}")
    outputCode = 1
    output = ""
    while p.poll() is None:
        line = p.stdout.readline()
        line = line.strip()
        line = str(line, encoding='utf-8', errors="ignore").strip()
        if line:
            if("Uninstalling" in line):
                counterSignal.emit(1)
            elif("Removing shim for" in line):
                counterSignal.emit(4)
            elif("was uninstalled" in line):
                counterSignal.emit(6)
            infoSignal.emit(line)
            if("was uninstalled" in line):
                outputCode = 0
            output += line+"\n"
    closeAndInform.emit(outputCode, output)



if(__name__=="__main__"):
    import __init__
