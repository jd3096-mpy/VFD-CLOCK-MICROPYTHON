import framebuf,time,ntptime,network,_thread,json,gc,machine
from machine import Pin,freq,SPI,RTC,Timer,ADC,I2C
from font5x7 import font
from drivers import VFD,Button,BLESimplePeripheral,PCF8563
import urequests,json,network,socket,smartconfig,machine,bluetooth

class VFDCLOCK():
    def __init__(self):
        self.timezone=8
        self.tzlist=[3155673600,3155670000,3155666400,3155662800,3155659200,3155655600,3155652000,3155648400,3155644800,3155641200,3155637600,3155634000,3155630400,3155677200,3155680800,3155684400,3155688000,3155691600,3155695200,3155698800,3155702400,3155706000,3155709600,3155713200,3155716800]
        self.btcb=0
        self.func=0
        self.clock_timer=True
        self.ani_last=True
        self.SSID='dundundun'
        self.PASSWORD='30963096'
        self.bl=150
        self.light=ADC(Pin(6),atten=ADC.ATTN_11DB)
        self.countday=(2025,6,1,0,0,0,0,0)
        self.rtc=RTC()
        self.spi = SPI(2, 1000000,sck=Pin(10),mosi=Pin(9),miso=Pin(15))  #sck-clk mosi-din
        self.en = Pin(13)
        self.rst = Pin(12)
        self.cs = Pin(11)
        self.display = VFD(self.spi, self.rst, self.cs, self.en)
        self.btl = Button(17,pull=Pin.PULL_UP,trigger=Pin.IRQ_FALLING)
        self.btr = Button(16,pull=Pin.PULL_UP,trigger=Pin.IRQ_FALLING)
        self.btm = Button(15,pull=Pin.PULL_UP,trigger=Pin.IRQ_FALLING)
        self.btb = Button(0,pull=Pin.PULL_UP,trigger=Pin.IRQ_FALLING)
        self.btn_list=[self.btl,self.btr,self.btm,self.btb]
        for btn in self.btn_list:
            btn.connect(self.bt_callback)
            btn.setEnable(True)
        self.lasth1=self.lasth2=self.lastm1=self.lastm2=self.lasts1=self.lasts2=0
        self.menu=['DATETIME',
                  'XGO2-DOG',
                  'COUNTDAY',
                  'TIMEZONE',
                  'NTPTIME',
                  'BRIGHT',
                  'BLE->NET',
                  'UPDATE',
                  'SYS INFO',
                  'MUSIC'
                ]
        self.menu_len=len(self.menu)
        self.menu_fb_list=[]
        for m in self.menu:
            fb=self.screen_fb(m)
            self.menu_fb_list.append(fb)
        self.numbuf=[
                    bytearray(b'\x7f\x7f\x41\x7f\x7f'),
                    bytearray(b'\x00\x06\x7f\x7f\x00'),
                    bytearray(b'\x79\x79\x49\x4f\x4f'),
                    bytearray(b'\x49\x49\x49\x7f\x7f'),
                    bytearray(b'\x0f\x0f\x08\x7f\x7f'),
                    bytearray(b'\x4f\x4f\x49\x79\x79'),
                    bytearray(b'\x7f\x7f\x49\x79\x78'),
                    bytearray(b'\x01\x01\x71\x7f\x0f'),
                    bytearray(b'\x7f\x7f\x49\x7f\x7f'),
                    bytearray(b'\x4f\x4f\x49\x7f\x7f')
                    ]
        self.load()
        if self.bl==0 or self.bl==255:
            self.display.set_display_dimming(100)
        else:
            self.display.set_display_dimming(self.bl)
    def bt_callback(self,pin,msg):
        #0:short press 1:long press 2:hold 3:release
        #1:left 2:middle 3:right 4:boot
        if msg == 0 or msg==1 or msg==2 or msg==3: 
            if pin==17:  #button left
                self.btcb=2+msg*10
            elif pin==16:  #button middle
                self.btcb=1+msg*10
            elif pin==15:  #button right
                self.btcb=3+msg*10
            elif pin==0:  #button boot
                self.btcb=4+msg*10
    def save(self):
        cjson={'ssid':self.SSID,'password':self.PASSWORD,'bl':self.bl,'countday':self.countday,'timezone':self.timezone}
        cstr=json.dumps(cjson)
        print(cstr)
        with open("config.vfd", "w") as f:  
            f.write(cstr)  
    def load(self):
        try:
            print('load config')
            with open("config.vfd", "r") as f:  
                cstr=f.read()
            cjson=json.loads(cstr)
            print(cjson)
            self.SSID=cjson['ssid']
            self.PASSWORD=cjson['password']
            self.bl=cjson['bl']
            self.countday=cjson['countday']
            self.timezone=cjson['timezone']
        except:
            pass
    def ani_num(self,addr,num,speed):
        if num==0:
            a=0
            b=9
        else:
            a=num
            b=num-1
        bufl = self.numbuf[b]
        fbufl = framebuf.FrameBuffer(bufl, 5, 7, framebuf.MONO_VLSB)
        bufn = self.numbuf[a]
        fbufn = framebuf.FrameBuffer(bufn, 5, 7, framebuf.MONO_VLSB)
        buf=bytearray(5)
        fbuf = framebuf.FrameBuffer(buf, 5, 7, framebuf.MONO_VLSB)
        for i in range(0,9):
            fbuf.fill(0)
            fbuf.blit(fbufl,0,0-i)
            fbuf.blit(fbufn,0,8-i)
            self.display.display_custom(addr,buf)
            time.sleep_ms(speed)
    def ani_wait_addr(self,addr):   #单位等待旋转动画
        fbl=[bytearray(b'\x02\x04\x08\x10\x20'),
             bytearray(b'\x04\x04\x08\x10\x10'),
             bytearray(b'\x08\x08\x08\x08\x08'),
             bytearray(b'\x10\x10\x08\x04\x04'),
             bytearray(b'\x20\x10\x08\x04\x02'),
             bytearray(b'\x00\x30\x08\x06\x00'),
             bytearray(b'\x00\x00\x3e\x00\x00'),
             bytearray(b'\x00\x06\x08\x30\x00'),
             ]
        while self.ani_last:
            for i in range(0,8):
                self.display.display_custom(addr,fbl[i])
                time.sleep_ms(33)
    def esp2rtc(self):
        try:
            i2c = I2C(scl=Pin(42), sda=Pin(41))
            r = PCF8563(i2c)
            print('rtc time')
            print(r.datetime())
            time.sleep(0.2)
            print('sync system to pcf8563')
            r.write_now()
            return True
        except:
            return False
    def rtc2esp(self):
        try:
            i2c = I2C(scl=Pin(42), sda=Pin(41))
            r = PCF8563(i2c)
            print('rtc time')
            print(r.datetime())
            #(year, month, day, weekday, hours, minutes, seconds, subseconds)
            esptime=(r.year()+2000,r.month(),r.date(),r.day(),r.hours(),r.minutes(),r.seconds(),0)
            print(esptime)
            self.rtc.datetime(esptime)
            print('esp32 time')
            print(self.rtc.datetime())
            return True
        except:
            return False 
    def ntp_get(self):
        self.ani_last=True
        _thread.start_new_thread(self.ani_wait,())
        if self.wifi_connect():
            for i in range(6):
                try:            
                    ntptime.settime(timezone=self.tzlist[self.timezone])      
                    print("ntp time(BeiJing): ",self.rtc.datetime())
                    self.ani_last=False
                    self.blink()
                    self.texts("NTP DONE")
                    self.esp2rtc()
                    return True
                except:
                    print("Can not get time!")
                time.sleep_ms(500)
            self.ani_last=False
            self.blink()
            self.texts("ERROR:2")
        else:
            self.ani_last=False
            self.blink()
            self.texts("ERROR:1")         
        time.sleep_ms(500)
    def texts(self,text):      #整屏字符串显示，使用自定义py字库
        self.display.fill(0)
        x=0
        for s in text:
            buf = font[ord(s)-32]
            fbuf = framebuf.FrameBuffer(buf, 5, 7, framebuf.MONO_VLSB)
            self.display.blit(fbuf,x,0)
            x+=5
        self.display.show()   
    def text_fb(self,text):   #返回字符串fb，根据字符串长自动设置fb长度
        x=0
        l=len(text)
        bufl=bytearray(5*l)
        fbufl=framebuf.FrameBuffer(bufl, 5*l, 7, framebuf.MONO_VLSB)
        for s in text:
            buf = font[ord(s)-32]
            fbuf = framebuf.FrameBuffer(buf, 5, 7, framebuf.MONO_VLSB)
            fbufl.blit(fbuf,x,0)
            x+=5
        return fbufl
    def screen_fb(self,text): #同上 不过强制最长8字符，也就是强制使用一个屏幕
        x=0
        if len(text)>7:
            text=text[0:8]
        bufl=bytearray(5*8)
        fbufl=framebuf.FrameBuffer(bufl, 5*8, 7, framebuf.MONO_VLSB)
        for s in text:
            buf = font[ord(s)-32]
            fbuf = framebuf.FrameBuffer(buf, 5, 7, framebuf.MONO_VLSB)
            fbufl.blit(fbuf,x,0)
            x+=5
        return fbufl
    def show_date(self):    #日期加星期 0125 TUE
        rdt=self.rtc.datetime()
        ww=rdt[3]
        if ww==0:
            weekday='MON'
        elif ww==1:
            weekday='TUE'
        elif ww==2:
            weekday='WED'
        elif ww==3:
            weekday='THU'
        elif ww==4:
            weekday='FRI'
        elif ww==5:
            weekday='SAT'
        elif ww==6:
            weekday='SUN'
        mm=str(rdt[1])
        dd=str(rdt[2])
        if len(mm)==1:
            mm='0'+mm
        if len(dd)==1:
            dd='0'+dd
        datestr=mm+'-'+dd+weekday
        self.display.display_str(0,datestr)
    def show_time(self,t):   #带动画时间 使用加粗数字字体，需要用计时器每秒调用一次 + 背光自动调节
        if self.bl==0 or self.bl==255:
            light=self.light.read()
            self.display.set_display_dimming(int(light/4095*254+1))
        if self.clock_timer==True:
            rdt=self.rtc.datetime()
            dd=str(rdt[0])+'-'+str(rdt[1])+'-'+str(rdt[2])
            hh=str(rdt[4])
            mm=str(rdt[5])
            ss=str(rdt[6])
            if len(hh)==1:
                hh='0'+hh
            if len(mm)==1:
                mm='0'+mm
            if len(ss)==1:
                ss='0'+ss
            if self.lasth1!=hh[0]:
                _thread.start_new_thread(self.ani_num,(0,int(hh[0]),20))
            else:
                self.display.display_custom(0,self.numbuf[int(hh[0])])
            if self.lasth2!=hh[1]:
                _thread.start_new_thread(self.ani_num,(1,int(hh[1]),20))
            else:
                self.display.display_custom(1,self.numbuf[int(hh[1])])
            self.display.display_str(2, '-')
            if self.lastm1!=mm[0]:
                _thread.start_new_thread(self.ani_num,(3,int(mm[0]),20))
            else:
                self.display.display_custom(3,self.numbuf[int(mm[0])])
            if self.lastm2!=mm[1]:
                _thread.start_new_thread(self.ani_num,(4,int(mm[1]),20))
            else:
                self.display.display_custom(4,self.numbuf[int(mm[1])])
            self.display.display_str(5, '-')
            if self.lasts1!=ss[0]:
                _thread.start_new_thread(self.ani_num,(6,int(ss[0]),20))
            else:
                self.display.display_custom(6,self.numbuf[int(ss[0])])
            if self.lasts2!=ss[1]:
                _thread.start_new_thread(self.ani_num,(7,int(ss[1]),20))
            else:
                self.display.display_custom(7,self.numbuf[int(ss[1])])
            self.lasth1=hh[0]
            self.lasth2=hh[1]
            self.lastm1=mm[0]
            self.lastm2=mm[1]
            self.lasts1=ss[0]
            self.lasts2=ss[1]
        else:
            pass
    def count_day(self):     #倒计日
        cttime=self.countday
        nowtime=time.mktime(time.localtime())
        rt=self.rtc.datetime()
        rtctime=(rt[0],rt[1],rt[2],rt[3],rt[4],rt[5],rt[6],314)
        rtctimestamp=time.mktime(rtctime)
        cttimestamp=time.mktime(cttime)
        cj=(cttimestamp-rtctimestamp)/3600/24
        if cj>9999:
            cj=9999
        if cj<0:
            self.display.display_str(0,'TIMECOME')
        else:
            self.display.display_str(0,str(int(cj)))
            self.display.display_str(4,'days')
    def wifi_connect(self):
        start_time=time.time()
        sta_if = network.WLAN(network.STA_IF)
        print('network status1:', sta_if.status())
        if not sta_if.isconnected():
            print('connecting to network...')
            sta_if.active(True)
            sta_if.connect(self.SSID, self.PASSWORD)
            print('network status2:', sta_if.status())
            while not sta_if.isconnected():
                time.sleep_ms(200)
                if time.time()-start_time > 11:
                    break
        print('network status3:', sta_if.status())
        if sta_if.isconnected():
            return True
        else:
            return False
    def scoll_menu(self,n,direction):   #动画显示菜单  带方向
        if not direction:
            if n==0:
                b=self.menu_len-1
            else:
                b=n-1
            fbl = self.menu_fb_list[b]
            fbn = self.menu_fb_list[n]
            for i in range(0,9):
                self.display.fill(0)
                self.display.blit(fbl,0,i)
                self.display.blit(fbn,0,-8+i)
                self.display.show()
                time.sleep_ms(15)
        else:
            if n>=self.menu_len-1:
                b=0
            else:
                b=n+1
            fbl = self.menu_fb_list[b]
            fbn = self.menu_fb_list[n]
            for i in range(0,9):
                self.display.fill(0)
                self.display.blit(fbl,0,0-i)
                self.display.blit(fbn,0,8-i)
                self.display.show()
                time.sleep_ms(15)    
    def blink(self):
        if self.bl==0 or self.bl==255:
            nowlight=int(self.light.read()/4095*254+1)
        else:
            nowlight=self.bl
        for i in range(0,nowlight):
            self.display.set_display_dimming(nowlight-i)
            time.sleep_ms(3)
        for i in range(0,nowlight):
            self.display.set_display_dimming(i)
            time.sleep_ms(3)    
    def ani_wait(self):
        arrow=bytearray(b'\x41\x22\x14\x08\x00\x41\x22\x14\x08\x00\x41\x22\x14\x08\x00\x41\x22\x14\x08\x00\x41\x22\x14\x08\x00\x41\x22\x14\x08\x00\x41\x22\x14\x08\x00\x41\x22\x14\x08\x00')
        fb_arrow = framebuf.FrameBuffer(arrow, 5*8, 7, framebuf.MONO_VLSB)
        self.display.fill(0)
        self.display.blit(fb_arrow,0,0)
        self.display.show()
        while self.ani_last:
            for i in range(0,5):
                self.display.fill(0)
                self.display.blit(fb_arrow,i,0)
                self.display.blit(fb_arrow,-40+i,0)
                self.display.show()
                time.sleep_ms(55)
    def OTA(self):
        self.display.display_str(0,'YES'+'  NO'+'\x0b')
        select=0
        self.btcb=0
        while 1:
            time.sleep_ms(3)
            if self.btcb==1:
                self.display.display_str(0,'YES'+'\x0b'+' NO ')
                select=1
            elif self.btcb==3:
                self.display.display_str(0,'YES'+'  NO'+'\x0b')
                select=0
            elif self.btcb==2:
                break
            self.btcb=0
        if select==1:
            self.texts('OTA.')
            if self.wifi_connect():
                self.clock_timer=False
                self.texts('OTA..')
                file1='https://gitee.com/jd3096/vfd-clock-wiki/raw/master/CLOCK.py'
                file2='https://gitee.com/jd3096/vfd-clock-wiki/raw/master/tools.py'
                file3='https://gitee.com/jd3096/vfd-clock-wiki/raw/master/main.py'
                gc.collect()
                a=urequests.get(file1)
                with open('CLOCK.py', "w") as f:
                    f.write(a.text)
                self.texts('OTA...')
                gc.collect()
                a=urequests.get(file2)
                with open('tools.py', "w") as f:
                    f.write(a.text)
                self.texts('OTA....')
                gc.collect()
                a=urequests.get(file3)
                with open('main.py', "w") as f:
                    f.write(a.text)
                self.texts('SUCCESS!')   
            else:
                self.ani_last=False
                self.blink()
                self.texts("ERROR:1")
            return 1
        else:
            return 0
    def xgo_people(self):
        if self.wifi_connect():
            try:
                headers={"api-key":"VqL9j56HfXisdr8nOvGT=iLl95g="}
                url='http://api.heclouds.com/devices/1039865113/datastreams'
                res=urequests.get(headers=headers,url=url)
                rjson=json.loads(res.text)
                print(rjson)
                people=rjson['data'][1]['current_value']
                money=rjson['data'][0]['current_value']
                self.texts(' '+str(money)+'$')
                while 1:
                    time.sleep_ms(10)
                    if self.btcb==22:
                        break
                    elif self.btcb==3:
                        self.texts(str(people)+' STAR')
                        self.btcb=0  
                    elif self.btcb==1:
                        self.texts(' '+str(money)+'$')
                        self.btcb=0
            except:
                self.texts("ERROR:2")
        else:
            self.texts("ERROR:1")
    def inet_pton(self,ip_str:str):
        '''convert ip address from string to bytes'''
        ip_bytes = b''
        ip_segs = ip_str.split('.')
        for seg in ip_segs:
            ip_bytes += int(seg).to_bytes(1, 'little')
        return ip_bytes
    def send_ack(self,local_ip, local_mac):
        '''sent ack_done event to phone'''
        udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        data = smartconfig.info()[3].to_bytes(1, 'little') + local_mac
        port = 10000 # airkiss port
        if smartconfig.info()[2] == smartconfig.TYPE_ESPTOUCH:
            data += self.inet_pton(local_ip)
            port = 18266 # esptouch port
        print(
    f"""- sending ack:
        type: {'esptouch' if smartconfig.info()[2] == smartconfig.TYPE_ESPTOUCH else 'airkiss'}
        port: {port}
        data: {data}
        length: {len(data)}
    """
        )
        for _ in range(20):
            time.sleep(0.1)
            try:
                udp.sendto(data, ('255.255.255.255', port))
            except OSError:
                pass
        print('- ack was sent')
    def airkiss(self):
        station = network.WLAN(network.STA_IF)
        station.active(False)
        time.sleep(1)
        station.active(True)
        print('- start smartconfig...')
        smartconfig.start()
        print('- waiting for success...')
        self.texts('AIRKISS')
        self.ani_last=True
        _thread.start_new_thread(self.ani_wait_addr,(7,))
        while not smartconfig.success():
            time.sleep(0.5)
        self.ani_last=True
        print('- got smartconfig info')
        ssid, password, sc_type, token = smartconfig.info()
        print(smartconfig.info())
        print('- connecting to wifi...')
        self.texts('CONNECT..')
        station.connect(ssid, password)
        while not station.isconnected():
            time.sleep(0.5)
        print('- wifi connected')
        while station.ifconfig()[0] == '0.0.0.0':
            time.sleep(0.5)
        print('- got ip')
        print(station.ifconfig())
        self.send_ack(station.ifconfig()[0], station.config('mac'))
        self.SSID=ssid
        self.PASSWORD=password
        self.save()
        self.ani_last=False
        time.sleep_ms(300)
        self.texts('DONE!   ')
        time.sleep(2)
        self.texts('RESET 3')
        time.sleep(1)
        self.texts('RESET 2')
        time.sleep(1)
        self.texts('RESET 1')
        time.sleep(1)
        machine.reset()
    def on_rx(self,v):
        data=v.decode()
        print("Receive_data:",data)
        if data[0]=='s':
            print('ssid')
            ssid=data[1:]
            self.SSID=ssid
        elif data[0]=='p':
            print('password')
            pwd=data[1:]
            self.PASSWORD=pwd
        print(self.SSID,self.PASSWORD)
    def ble_ap(self):
        self.texts('BLE ON')
        self.ani_last=True
        _thread.start_new_thread(self.ani_wait_addr,(7,))
        b = bluetooth.BLE()
        p = BLESimplePeripheral(b)
        p.on_write(self.on_rx)
        while 1:
            if p.command:
                break
            time.sleep_ms(100)
        self.ani_last=False
        time.sleep_ms(300)
        self.texts('NET SAVE')
        self.save()
        
    def info(self):         #显示系统信息 滚轮控制左右
        infostr='VER:1.04 HARDWARE:eggfly SOFTWARE:jd3096 MPY1.191 ESP32-S3 VX:jd3096'
        infofb=self.text_fb(infostr)
        min_val=0
        max_val=len(infostr)-8
        val=0
        self.display.fill(0)
        self.display.blit(infofb,0,0)
        self.display.show()
        while True:
            if self.btcb==22:
                break
            if self.btcb==3:
                if val==max_val:
                    pass
                else:
                    val+=1
                self.btcb=0
            elif self.btcb==1:
                if val==0:
                    pass
                else:
                    val-=1
                self.btcb=0
            elif self.btcb==23:
                while 1:
                    if self.btcb==33:
                        break
                    else:
                        time.sleep_ms(33)
                        if val==max_val:
                            pass
                        else:
                            val+=1
                        self.display.fill(0)
                        self.display.blit(infofb,0-val*5,0)
                        self.display.show()
                self.btcb=0
            elif self.btcb==21:
                while 1:
                    if self.btcb==31:
                        break
                    else:
                        time.sleep_ms(33)
                        if val==0:
                            pass
                        else:
                            val-=1
                        self.display.fill(0)
                        self.display.blit(infofb,0-val*5,0)
                        self.display.show()
                self.btcb=0
            self.display.fill(0)
            self.display.blit(infofb,0-val*5,0)
            self.display.show()



        





