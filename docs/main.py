from machine import Timer
from CLOCK import VFDCLOCK
import time,machine,gc
from tools import song1,song2,song3,song4,song5,song6,song7,song8
from drivers import music
from time import sleep
from machine import Pin,PWM

def menu():
    clock.btcb=0
    clock.clock_timer=False
    while 1:
        clock.texts(clock.menu[clock.func])
        time.sleep_ms(30)
        #print(clock.btcb,clock.func)
        if clock.btcb!=0:
            if clock.btcb==1 or clock.btcb==11:
                if clock.func==0:
                    clock.func=clock.menu_len-1
                else:
                    clock.func-=1
                clock.scoll_menu(clock.func,True)
            elif clock.btcb==2:
                break
            elif clock.btcb==3 or clock.btcb==13:
                if clock.func==clock.menu_len-1:
                    clock.func=0
                else:
                    clock.func+=1
                clock.scoll_menu(clock.func,False)
            clock.btcb=0
        else:
            time.sleep_ms(30)
    if clock.func==0:
        datetime()
    elif clock.func==1:
        xgo()
    elif clock.func==2:
        countday()
    elif clock.func==3:
        timezone()
    elif clock.func==4:
        ntptime()
    elif clock.func==5:
        backlight()
    elif clock.func==6:
        airkiss()
    elif clock.func==7:
        tim.deinit()
        if clock.OTA():
            time.sleep(2)
            clock.texts('RESET 3')
            time.sleep(1)
            clock.texts('RESET 2')
            time.sleep(1)
            clock.texts('RESET 1')
            time.sleep(1)
            machine.reset()
        else:
            menu()
    elif clock.func==8:
        info()
    elif clock.func==9:
        playmusic()
            
def datetime():
    gc.collect()
    print('datetime')
    clock.clock_timer=True
    while 1:
        time.sleep_ms(50)
        if clock.btcb==22:
            break
        elif clock.btcb==1:
            clock.blink()
            while 1:
                time.sleep_ms(20)
                if clock.btcb==3:
                    break
                clock.clock_timer=False
                clock.show_date()
            clock.clock_timer=True
            clock.btcb=0
            clock.blink()
        elif clock.btcb==3:
            clock.blink()
            clock.display.display_str(0,'        ')
            while 1:
                time.sleep_ms(20)
                if clock.btcb==1:
                    break
                clock.clock_timer=False
                clock.count_day()
            clock.clock_timer=True
            clock.btcb=0
            clock.blink()
        else:
            pass
    if clock.btcb==22:
        menu()
    clock.clock_timer=False
    
def xgo():
    clock.xgo_people()
    menu()
    
def countday():
    clock.btcb=0
    yy=clock.countday[0]
    mm=clock.countday[1]
    dd=clock.countday[2]
    clock.texts('YEAR'+str(yy))
    while 1:
        if clock.btcb==2:
            break
        elif clock.btcb==1:
            if yy>2023:
                yy-=1
        elif clock.btcb==3:
            if yy<2100:
                yy+=1
        elif clock.btcb==23:
            while 1:
                if clock.btcb==33:
                    break
                else:
                    if yy<2100:
                        yy+=1
                    clock.texts('YEAR'+str(yy))
            clock.btcb=0
        elif clock.btcb==21:
            while 1:
                if clock.btcb==31:
                    break
                else:
                    if yy>2023:
                        yy-=1
                    clock.texts('YEAR'+str(yy))
            clock.btcb=0
        clock.btcb=0
        clock.texts('YEAR'+str(yy))
    clock.texts('MONTH:'+str(mm))
    clock.btcb=0
    while 1:
        if clock.btcb==2:
            break
        elif clock.btcb==1:
            if mm>1:
                mm-=1
        elif clock.btcb==3:
            if mm<12:
                mm+=1
        elif clock.btcb==23:
            while 1:
                if clock.btcb==33:
                    break
                else:
                    if mm<12:
                        mm+=1
                    clock.texts('MONTH:'+str(mm))
            clock.btcb=0
        elif clock.btcb==21:
            while 1:
                if clock.btcb==31:
                    break
                else:
                    if mm>1:
                        mm-=1
                    clock.texts('MONTH:'+str(mm))
            clock.btcb=0
        clock.btcb=0
        clock.texts('MONTH:'+str(mm))
    clock.texts(' DAY:'+str(dd))
    clock.btcb=0
    if mm==1 or mm==3 or mm==5 or mm==7 or mm==8 or mm==10 or mm==12:
        d_max=31
    elif mm==2:
        if (yy % 4) == 0:
           if (yy % 100) == 0:
               if (yy % 400) == 0:
                   d_max=29  
               else:
                   d_max=28
           else:
               d_max=29     
        else:
           d_max=28
    else:
        d_max=30
    while 1:
        if clock.btcb==2:
            break
        elif clock.btcb==1:
            if dd>1:
                dd-=1
        elif clock.btcb==3:
            if dd<d_max:
                dd+=1
        elif clock.btcb==23:
            while 1:
                if clock.btcb==33:
                    break
                else:
                    if dd<d_max:
                        dd+=1
                    clock.texts(' DAY:'+str(dd))
            clock.btcb=0
        elif clock.btcb==21:
            while 1:
                if clock.btcb==31:
                    break
                else:
                    if dd>1:
                        dd-=1
                    clock.texts(' DAY:'+str(dd))
            clock.btcb=0
        clock.btcb=0
        clock.texts(' DAY:'+str(dd))
    clock.texts(' SAVED!')
    clock.countday=(yy,mm,dd,0,0,0,0,0)
    clock.save()
    time.sleep(1)
    menu()
    
def ntptime():
    clock.ntp_get()
    time.sleep(1)
    menu()
    
def bl_set():
    if clock.bl==0 or clock.bl==255:
        clock.display.set_display_dimming(100)
        clock.texts('BL:'+' '+'AUTO')
    else:
        clock.texts('BL:'+' '+str(clock.bl))
        clock.display.set_display_dimming(clock.bl)
    
def backlight():
    clock.btcb=0
    clock.texts('BL:'+' '+str(clock.bl))
    max_val=255
    while True:
        if clock.btcb==22 or clock.btcb==2:
            break
        if clock.btcb==3:
            if clock.bl==max_val:
                pass
            else:
                clock.bl+=1
            clock.btcb=0
        elif clock.btcb==1:
            if clock.bl==0:
                pass
            else:
                clock.bl-=1
            clock.btcb=0
        elif clock.btcb==23:
            while 1:
                if clock.btcb==33:
                    break
                else:
                    if clock.bl==max_val:
                        pass
                    else:
                        clock.bl+=1
                    bl_set()
            clock.btcb=0
        elif clock.btcb==21:
            while 1:
                if clock.btcb==31:
                    break
                else:
                    if clock.bl==0:
                        pass
                    else:
                        clock.bl-=1
                    bl_set()
            clock.btcb=0
        bl_set()
    clock.texts(" SAVED!")
    clock.bl=clock.bl
    clock.save()
    time.sleep(1)
    menu()
    
def timezone():
    clock.btcb=0
    tzstr=['  UTC',' UTC+1',' UTC+2',' UTC+3',' UTC+4',' UTC+5',' UTC+6',' UTC+7',' UTC+8',' UTC+9',' UTC+10',' UTC+11',' UTC+12',' UTC-1',' UTC-2',' UTC-3',' UTC-4',' UTC-5',' UTC-6',' UTC-7',' UTC-8',' UTC-9',' UTC-10',' UTC-11',' UTC-12']
    tznow=clock.timezone
    clock.texts(tzstr[tznow])
    while 1:
        if clock.btcb==2:
            break
        elif clock.btcb==1:
            if tznow>0:
                tznow-=1
        elif clock.btcb==3:
            if tznow<24:
                tznow+=1
        elif clock.btcb==23:
            while 1:
                if clock.btcb==33:
                    break
                else:
                    if tznow<24:
                        tznow+=1
                        clock.texts(tzstr[tznow])
            clock.btcb=0
        elif clock.btcb==21:
            while 1:
                if clock.btcb==31:
                    break
                else:
                    if tznow>0:
                        tznow-=1
                        clock.texts(tzstr[tznow])
            clock.btcb=0
        clock.btcb=0
        clock.texts(tzstr[tznow])
    clock.texts(' SAVED!')
    clock.timezone=tznow
    clock.save()
    time.sleep(1)
    ntptime()

def airkiss():
    clock.ble_ap()
    time.sleep(2)
    clock.texts('RESET 3')
    time.sleep(1)
    clock.texts('RESET 2')
    time.sleep(1)
    clock.texts('RESET 1')
    time.sleep(1)
    machine.reset()
    
def info():
    clock.info()
    menu()

def playsong(song,speed):
    mySong = music(song, pins=[Pin(8)])
    while True:
        if clock.btcb==2:
            break
        mySong.tick()
        sleep(speed)
    pwm=PWM(Pin(8))
    pwm.deinit()
    clock.btcb=0
    
def playmusic():
    songlist=['Tetris','Tele','Fantasy','Chocobo','JOJO','Castle','Mario','Nokia']
    clock.texts(songlist[0])
    select=0
    while 1:
        time.sleep_ms(2)
        if clock.btcb==3:
            if select==len(songlist)-1:
                select=0
            else:
                select+=1
            clock.texts(songlist[select])
        elif clock.btcb==1:
            if select==0:
                select=len(songlist)-1
            else:
                select-=1
            clock.texts(songlist[select])
        elif clock.btcb==2:
            clock.btcb=0
            if select==0:
                playsong(song1,0.035)
            elif select==1:
                playsong(song2,0.03)
            elif select==2:
                playsong(song3,0.055)
            elif select==3:
                playsong(song4,0.033)
            elif select==4:
                playsong(song5,0.034)
            elif select==5:
                playsong(song6,0.036)
            elif select==6:
                playsong(song7,0.028)
            elif select==7:
                playsong(song8,0.043)
        elif clock.btcb==22:
            break
        clock.btcb=0
    clock.btcb=0
    menu()
            

#---------MAIN PROGRAM------------
clock=VFDCLOCK()
if clock.rtc2esp():
    pass
else:
    clock.ntp_get()
tim=Timer(-1)
tim.init(period=1000, callback=clock.show_time)
datetime()

#clock.rtc2esp()



















