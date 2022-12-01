

from telnetlib import LOGOUT
from tokenize import generate_tokens

from django.shortcuts import render,redirect

import os, sys
import platform
import psutil
import requests
import speedtest
from django.contrib import messages
import subprocess
import time
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from urllib3 import HTTPResponse




def home(request):
    return render(request, "whelper/landing.html")

def faq(request):
    return render(request,"whelper/faq.html")

#def home(request):
 #   return render(request,"whelper/homey.html")


def sysinfo1(request):
    return render(request, "whelper/sysinfo.html")

def sysinfo(request):
    os_type = sys.platform.lower()
    if("win" in os_type):
        command = "wmic bios get serialnumber"
    elif "linux" in os_type:
        command = "hal-get-property --udi /org/freedesktop/Hal/devices/computer --key system.hardware.uuid"
    elif "darwin" in os_type:
        command = "ioreg -l | grep IOPlatformSerialNumber"
    my_system = platform.uname()
    context={"result": os.popen(command).read().replace("\n","").replace("	","").replace(" ",""),
    "system":my_system.system,"node_name":my_system.node,"release":my_system.release,
    "version":my_system.version,"machine":my_system.machine,"processor":my_system.processor}
    return render(request,"whelper/S1.html",context)
    



def sys_health(request):
    virtual_memory=psutil.virtual_memory()
    disk_usage=psutil.disk_usage('/')
    ios_stats=psutil.net_io_counters()
    battery_info=psutil.sensors_battery()
    cpu_times=psutil.cpu_times()
    user_time=round(cpu_times.user/3600)
    system_time=round(cpu_times.system/3600)
    idle_time=round(cpu_times.idle/3600)
    context={"r1":psutil.cpu_percent(),
    "r2":psutil.cpu_count(),
    "r3":psutil.cpu_freq().current,
    "r4":virtual_memory.total,
    "r5":virtual_memory.available,
    "r6":virtual_memory.used,
    "r7":virtual_memory.percent,
    "r8":psutil.disk_partitions(),
    "r9":disk_usage.total,
    "r10":disk_usage.free,
    "r11":disk_usage.used,
    "r12":disk_usage.percent,
    "r13":ios_stats.bytes_sent,
    "r14":ios_stats.bytes_recv,
    "r15":battery_info.percent,
    "r16":battery_info.secsleft,
    "r17":user_time,
    "r18":system_time,
    "r19":idle_time}
    return render(request,"whelper/rest_sys_info.html",context)

def internet_speed(request):
    st = speedtest.Speedtest()
    servernames =[]
    st.get_servers(servernames)  
    context={"d":st.download(),
    "u":st.upload(), "p":st.results.ping}
    return render(request,"whelper/internet_speed.html",context)

def url_status_input(request):
    return render(request,"whelper/url_status_input.html")

def url_status(request):
    if request.method=="POST":
        URL=request.POST.get('message')
    try:
        response = requests.head(URL)
    except Exception as e:
         context={"e":str(e)}
         messages.error(request,"Enter valid URL")
         return render(request,"whelper/url_status.html",context)
    if response.status_code == 200:
        context={"status":response.status_code}
        return render(request,"whelper/url_status.html",context)
    else:
        context={"status":response.status_code}
        return render(request,"whelper/url_status.html",context)
        
def internet_block_input(request):
    return render(request,"whelper/internet_block_input.html")

def website_block_input(request):
     return render(request,"whelper/website_block_input.html")


def internet_block(request):
    if request.method == "POST":
        t = request.POST.get("t")
    wifi=subprocess.check_output("netsh interface show interface",stderr=subprocess.STDOUT, shell=True)
    lines=wifi.splitlines()
    for i in range(len(lines)):
        if 'Connected'.encode() in lines[i]:
            interface=lines[i].split(None, 3)
            interface=interface[3]
            interface=interface.decode("utf-8")
            print(interface)
            os.popen('netsh interface set interface '+interface+' disabled')
            time.sleep(int(t))
            os.popen('netsh interface set interface '+interface+' enabled')
    return render(request,"whelper/internet_block_input.html")

def website_block(request):
    if request.method == "POST":
        url=request.POST.get("url")
        ti = request.POST.get("ti")
    hosts_path = "C:\Windows\System32\drivers\etc\hosts"
    redirect = "127.0.0.1"   
    lookup=redirect + " " + url + "\n" 
    with open(hosts_path, 'a') as file:
        file.write(redirect + " " + url + "\n")
        file.close()
    time.sleep(int(ti))            
    with open(hosts_path,"r+") as f:
        new_f = f.readlines()
        f.seek(0)
        for line in new_f:
            if lookup not in line:
                f.write(line)
        f.truncate()
    return render(request,"whelper/website_block_input.html")


        



def index(request):
       return render(request,"whelper/homey.html")   

def signup(request):
    if request.method=="POST":
        username=request.POST['username']
        fname=request.POST['fname']
        lname=request.POST['lname']
        email=request.POST['email']
        pass1=request.POST['pass1']
        pass2=request.POST['pass2']
        if User.objects.filter(username=username):
            messages.error(request, "Username already exist! Please try some other username.")
            return redirect('index')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email Already Registered!!")
            return redirect('index')
        
        if len(username)>20:
            messages.error(request, "Username must be under 20 charcters!!")
            return redirect('index')
        
        if pass1 != pass2:
            messages.error(request, "Passwords didn't matched!!")
            return redirect('index')
        
        if not username.isalnum():
            messages.error(request, "Username must be Alpha-Numeric!!")
            return redirect('index')
        myuser=User.objects.create_user(username,email,pass1)
        myuser.firstname=fname
        myuser.lastname=lname
        myuser.save()
        messages.success(request,"Your account has been successfully created.We have sent you a confirmation email")
        
        return redirect("signin")
    return render(request,"whelper/signup.html")




def signin(request):
    if request.method=="POST":
        username=request.POST["username"]
        pass1=request.POST["pass1"]
        user=authenticate(username=username, password=pass1)
        if user is not None:
            login(request, user)
            fname=user.first_name
            messages.success(request, "Logged In Sucessfully!!")
            return render(request,"whelper/homey.html",{'fname':fname})
        else:
            messages.error(request,"Bad credentials")
            return redirect("index")
    return render(request,"whelper/signin.html")

def signout(request):
        logout(request)
        messages.success(request,"Logged out Successfully")
        return redirect("signin")