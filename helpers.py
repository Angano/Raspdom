import models
import config
import datetime, random, time

from models import ConfigBcm, Bus
from sqlalchemy import or_
import gpio as pyApp_gpio
try:
    import RPi.GPIO as pyApp_gpio

except Exception as e:
    print(e, "erreur import Rpi")
    pass
#Numérotation automatique des entrées et sorties





def nameIO(mode, i, gpios_list):

    listOutput = [(data.nom) for data in gpios_list if data.mode=='Output']
    listInput = [(data.nom) for data in gpios_list if data.mode=='Input']

    nom = list()
    c = 0
    c2 = 0
    if mode =='Output':
        while c2<i:
            while 'A'+str(c) in listOutput:
                c= c+1
            nom.append('A'+str(c))
            listOutput.append('A'+str(c))
            c2 = c2 +1


    elif mode =='Input':
        while c2<i:
            while 'I'+str(c) in listInput:
                c= c+1
            nom.append('I'+str(c))
            listInput.append('I'+str(c))
            c2 = c2 + 1

    return nom

def update_time():
    try:
        status = models.Status.query.filter_by(identifiant='now_time').first()

        if status == None:
            status = models.Status()
            status.identifiant = 'now_time'
            config.db.session.add(status)
        status.time_now = datetime.datetime.today()
        config.db.session.commit()
    except:
        pass
    return

def configBcm():

    if ConfigBcm.query.first() == None:
        init = True

    else:
        init = False
    if init:
        bus_list = ['I2C1','SPI0','SPI1']
        for bus in bus_list:
            bus_add = Bus()
            bus_add.name = bus
            config.db.session.add(bus_add)
        config.db.session.commit()

    datas_bank1 = getrevision()['banck_gpio_1']
    datas_bank2 = getrevision()['banck_gpio_2']

    if init:
        for pin,name,alt,classe,class2,bus in datas_bank1:
            try:
                configbcm = ConfigBcm.query.filter_by(pin=pin).first()


            except Exception:
                configbcm = ConfigBcm()


            if configbcm == None:
                configbcm = ConfigBcm()


            configbcm.pin = pin
            configbcm.name=name
            configbcm.alt_fct_name=alt
            configbcm.class1 = classe
            configbcm.class2 = class2
            configbcm.bus = bus
            if "Gpio_" in name and 'Relais' not in alt:
                configbcm.mode = 'Input'
            elif "Gpio_" in name and 'Relais' in alt:
                configbcm.mode = 'Output'
            try:
                configbcm.bus_id = Bus.query.filter_by(name=bus).first().id
            except Exception:
                pass
            config.db.session.add(configbcm)

        for pin, name, alt, classe, class2, bus in datas_bank2:
            try:
                configbcm = ConfigBcm.query.filter_by(pin=pin).first()

            except Exception:
                configbcm = ConfigBcm()

            if configbcm == None:
                configbcm = ConfigBcm()
            configbcm.pin = pin
            configbcm.name = name
            configbcm.alt_fct_name = alt
            configbcm.class1 = classe
            configbcm.class2 = class2
            configbcm.bus = bus
            if "Gpio_" in name and 'Relais' not in alt:
                configbcm.mode = 'Input'
            elif "Gpio_" in name and 'Relais' in alt:
                configbcm.mode = 'Output'
            try:
                configbcm.bus_id = Bus.query.filter_by(name=bus).first().id
            except Exception:
                pass
            config.db.session.add(configbcm)

        config.db.session.commit()
        return

def getrevision():
    '''
    Model and PCB Revision                          +++  RAM       +++ Revision   +++ Pi Revision Code from cpuinfo +++ Version connecteur gpio
    Model B Rev 1                                   +++  256MB     +++            +++ 0002                          +++ 26
    Model B Rev 1 ECN0001 (no fuses, D14 removed)   +++ 256MB      +++            +++ 0003                          +++ 26
    Model B Rev 2                                   +++ 256MB      +++            +++ 0004, 0005, 0006              +++ 26
    Model A                                         +++ 256MB      +++            +++ 0007, 0008, 0009              +++ 26
    Model B Rev 2                                   +++ 512MB      +++            +++ 000d, 000e, 000f              +++ 26
    Model B+                                        +++ 512MB      +++            +++ 0010,0013,900032              +++ 26
    Compute Module                                  +++ 512MB      +++            +++ 0011                          +++ 40
    Compute Module                                  +++ 512MB      +++            +++ 0014 (Embest, China)          +++ 40
    Model A+                                        +++ 256MB      +++            +++ 0012                          +++ 26
    Model A+                                        +++ 256MB      +++            +++ 0015 (Embest, China)          +++ 26
    Model A+                                        +++ 512MB      +++            +++ 0015 (Embest, China)          +++ 26
    Pi 2 Model B v1.1                               +++ 1GB        +++            +++ a01041 (Sony, UK)             +++ 40
    Pi 2 Model B v1.1                               +++ 1GB        +++            +++ a21041 (Embest, China)        +++ 40
    Pi 2 Model B v1.2                               +++ 1GB        +++ 1.2        +++ a22042                        +++ 40
    Pi Zero v1.2                                    +++ 512MB      +++ 1.2        +++ 900092                        +++ 40
    Pi Zero v1.3                                    +++ 512MB      +++ 1.3        +++ 900093                        +++ 40
    Pi Zero W                                       +++ 512MB      +++ 1.1        +++ 9000C1                        +++ 40
    Pi 3 Model B                                    +++ 1GB        +++ 1.2        +++ a02082 (Sony, UK)             +++ 40
    Pi 3 Model B                                    +++ 1GB        +++ 1.2        +++ a22082 (Embest, China)        +++ 40
    Pi 3 Model B+                                   +++ 1GB        +++ 1.3       +++ a020d3 (Sony, UK)              +++ 40
    Pi 4                                            +++ 1GB        +++ 1.1        +++ a03111 (Sony, UK)             +++ 40
    Pi 4                                            +++ 2GB        +++ 1.1        +++ b03111 (Sony, UK)             +++ 40
    Pi 4                                            +++	2GB        +++ 1.2        +++ b03112 (Sony, UK)             +++ 40
    Pi 4                                            +++ 2GB	       +++ 1.4        +++ b03114 (Sony, UK)             +++ 40
    Pi 4                                            +++ 4GB        +++ 1.1        +++ c03111 (Sony, UK)             +++ 40
    Pi 4                                            +++ 4GB        +++ 1.2        +++ c03112 (Sony, UK)             +++ 40
    Pi 4                                            +++ 4GB	       +++ 1.4        +++ c03114 (Sony, UK)             +++ 40
    Pi 4                                            +++ 8GB        +++ 1.4        +++ d03114 (Sony, UK)             +++ 40
    Pi 400                                          +++ 4GB        +++ 1.0        +++ c03130 (Sony, UK)             +++ 40
    Pi Zero 2 W                                     +++ 1GB        +++ 1.0        +++ 902120 (Sony, UK)             +++ 40
        '''

    Gpio_init_26 = [2,3,4,17,27,22,10,9,11,14,15,18,23,24,25,8,7] # 17
    Gpio_init_40 = [2,3,4,17,27,22,10,9,11,5,6,13,19,26,14,15,18,23,24,25,8,7,12,16,20,21] # 26

    # [Model and PCB Revision, Ram, Révision, Version connecteur gpio, Pi Revision Code from cpuinfo]
    datas = {
        '0000':['<b>Mode developpeur</b>',None,None,26,'0000'],
        '0002':['Model B Rev 1','256Mb',None,260,'0002'],
        '0003':['Model B Rev 1 ECN0001 (no fuses, D14 removed)','256M',None,260,'0003'],
        '0004': ['Model B Rev 2','256MB',None,26,'0004'],
        '0005': ['Model B Rev 2', '256MB',None,26,'0005'],
        '0006': ['Model B Rev 2', '256MB',None,26,'0006'],
        '0007': ['Model A', '256MB',None,26,'0007' ],
        '0008': ['Model A', '256MB',None,26,'0008' ],
        '0009': ['Model A ', '256MB',None ,26,'0009'],
        '000d': ['Model B Rev 2', '512MB',None,26,'000d' ],
        '000e': ['Model B Rev 2', '512MB',None,26,'000e' ],
        '000f': ['Model B Rev 2', '512MB',None,26,'000f' ],
        '0010': ['Model B+', '512MB',None,26,'0010' ],
        '0013': ['Model B+', '512MB', None,26,'0013' ],
        '900032': ['Model B+', '512MB', None,26,'900032'],
        '0011': [' Compute Module', '512MB', None,40,'0011' ],
        '0014': ['Compute Module (Embest, China)', '512MB',None,40,'0014'],
        '0012': ['Model A+', '256MB', None,26,'0012'],
        'a01041': ['Pi 2 Model B v1.1 (Sony, UK)', '1GB', None,40,'a01041'],
        'a21041': ['Pi 2 Model B v1.1 (Embest, China)', '1GB',None,40,'a21041' ],
        'a22042': ['Pi 2 Model B v1.2', '1GB','1.2',40,'a22042' ],
        '900092': ['Pi Zero v1.2', '512MB','1.2',40,'900092'],
        '900093': ['Pi Zero v1.3', '512MB','1.3',40,'900093'],
        '9000C1': ['Pi Zero W', '512MB', '1.1',40,'9000C1'],
        'a02082': ['Pi 3 Model B (Sony, UK)', '1GB','1.2',40 ,'a02082'],
        'a22082': ['Pi 3 Model B', '1GB ','1.2',40,'a22082' ],
        'a020d3': ['Pi 3 Model B+ (Sony, UK)', '1GB','1.3',40,'a020d3' ],
        'a03111': ['Pi 4 (Sony, UK)', '1GB','1.1',40,'a03111' ],
        'b03111': ['Pi 4 (Sony, UK)', '2GB','1.2',40,'b03111' ],
        'b03112': ['Pi 4 (Sony, UK)', '2GB', '1.3',40,'b03112'],
        'b03114': ['Pi 4 (Sony, UK)', '2GB','1.1',40,'b03114' ],
        'c03111': ['Pi 4 (Sony, UK)', '4GB','1.1',40,'c03111' ],
        'c03112': ['Pi 4 (Sony, UK)', '4GB','1.2',40,'c03112' ],
        'c03114': ['Pi 4 (Sony, UK)', '4GB','1.4',40,'c03114' ],
        'd03114': ['Pi 4 (Sony, UK)', '8GB','1.4',40,'d03114' ],
        'c03130': ['Pi 400 (Sony, UK)', '4GB','1.0',40,'c03130' ],
        '902120': ['Pi Zero 2 W  (Sony, UK)', '1GB','1.0',40,'902120' ]
    }

    # Extract board revision from cpuinfo file
    myrevision = "0000"
    try:
        f = open('/proc/cpuinfo', 'r')
        for line in f:
            if line[0:8] == 'Revision':
                length = len(line)
                myrevision = line[11:length - 1]
        f.close()
    except:
        myrevision = "0000"

    datas_bank_deve_1 = [
        (1, '3.3V PWR', '', 'PWR3V', '', ''),
        (3, 'Gpio_2', 'I2C1 SDA', 'btn-warning', 'btn-primary', 'I2C1'),
        (5, 'Gpio_3', 'I2C1 SCL', 'btn-warning', 'btn-primary', 'I2C1'),
        (7, 'Gpio_4', '1-Wire', 'btn-warning', 'btn-primary', 'GPCLK0'),
        (9, 'GND', '', 'btn-dark', '', ''),
    ]
    datas_bank_deve_2 = [
        (2, '5V PWR', '', 'btn-danger', '', ''),
        (4, '5V PWR', '', 'btn-danger', '', ''),
        (6, 'GND', '', 'btn-dark', '', ''),
        (8, 'Gpio_14', '', 'btn-success', '', 'UART0 TX'),
        (10, 'Gpio_15', '', 'btn-success', '', 'UART0 RX'),
    ]
    datas_bank_26_1 = [
        (1, '3.3V PWR'  ,''     ,''                      ,''             ,''                     ,''                 ,''             ,''             ,''             ,''                 ,''                    ,''     ),
        (3, 'Gpio_2'    ,'Input','I2C Data'              ,'I2C1 SDA'     ,'SMI SA3'              ,'DPI VSYNC'        ,'AVEOUT VSYNC' ,'AVEIN VSYNC'  ,''             ,'btn-warning'      ,'md-i2c'              ,'I2C'  ),
        (5, 'Gpio_3'    ,'Input','I2C Clock'             ,'I2C1 SCL'     ,'SMI SA2'              ,'DPI HSYNC'        ,'AVEOUT HSYNC' ,'AVEIN HSYNC'  ,''             ,'btn-warning'      ,'md-i2c'              ,'I2C'  ),
        (7, 'Gpio_4'    ,'Input',None                    ,'GPCLK0'       ,'SMI SA1'              ,'DPI D0'           ,'AVEOUT VID0'  ,'AVEIN VID0'   ,'JTAG TDI'     ,'btn-warning'      ,'md-gpio'             ,'GPIO' ),
        (9, 'GND'       ,''     ,''                      ,''             ,''                     ,''                 ,''             ,''             ,''             ,''                 ,''                    ,''     ),
        (11, 'Gpio_17'  ,'Input',None                    ,'FL1'          ,'SMI SD9'              ,'DPI D13'          ,'UART0 RTS'    ,'SPI1 CE1'     ,'UART1 RTS'    ,'btn-warning'      ,'md-gpio'             ,'GPIO' ),
        (13, 'Gpio_27'  ,'Input',None                    ,'SD0 DAT3'     ,'TE1'                  ,'DPI D23'          ,'SD1 DAT3'     ,'JTAG TMS'     ,''             ,'btn-warning'      ,'md-gpio'             ,'GPIO' ),
        (15, 'Gpio_22'  ,'Input',None                    , 'SD0 CLK'     ,'SMI SD14'             ,'DPI D18'          ,'SD1 CLK'      ,'JTAG TRST'    ,''             ,'btn-warning'      ,'md-gpio'             ,'GPIO' ),
        (17, '3.3V PWR' ,''     ,None                    , ''            ,''                     ,''                 ,''             ,''             ,''             ,''                 ,''                    ,''     ),
        (19, 'Gpio_10'  ,'Input',None                    ,'SPI0 MOSI'    , 'SMI SD2'             ,'DPI D6'           ,'AVEOUT VID6'  ,'AVEIN VID6'   ,''             ,'btn-warning'      ,'md-spi'              ,'SPI'  ),
        (21, 'Gpio_9'   ,'Input',None                    , 'SPI0 MISO'   ,'SMI SD1'              ,'DPI D5'           ,'AVEOUT VID5'  ,'AVEIN VID5'   ,''             ,'btn-warning'      ,'md-spi'              ,'SPI'  ),
        (23, 'Gpio_11'  ,'Input',None                    , 'SPI0 SCLK'   ,'SMI SD3'              ,'DPI D7'           ,'AVEOUT VID7'  ,'AVEIN VID7'   ,''             ,'btn-warning'      ,'md-spi'              ,'SPI'  ),
        (25, 'GND'      ,''     ,''                      ,''             ,''                     ,''                 ,''             ,''             ,''             ,''                 ,''                    ,''     ),
    ]
    datas_bank_26_2 = [
        (2,  '5V PWR'   ,''         ,''                     ,''             ,''                     ,''         ,''                     ,''             ,''         ,'btn-danger'       ,''                     ,''     ),
        (4,  '5V PWR'   ,''         ,''                     ,''             ,''                     ,''         ,''                     ,''             ,''         ,'btn-danger'       ,''                     ,''     ),
        (6,  'GND'      ,''         ,''                     ,''             ,''                     ,''         ,''                     ,''             ,''         ,'btn-dark'         ,''                     ,''     ),
        (8,  'Gpio_14'  ,'Input'    ,'UART Transmit'        ,'UART0 TXD'    ,'SMI SD6'              ,'DSI D10'  ,'AVEOUT VID10'         ,'AVEIN VID10'  ,'UART1 TXD','btn-warning'      ,'md-uart'              ,'UART' ),
        (10, 'Gpio_15'  ,'Input'    ,'UART Receive'         ,'UART0 RXD'    ,'SMI SD7'              ,'DPI D11'  ,'AVEOUT VID11'         ,'AVEIN VID11'  ,'UART1 RXD','btn-warning'      ,'md-uart'              ,'UART' ),
        (12, 'Gpio_18'  ,'Input'    ,'PCM Clock'            ,'PCM CLK'      ,'SMI SD10'             ,'DPI D14'  ,'I2CSL SDA / MOSI'     ,'SPI1 CE0'     ,'PWM0'     ,'btn-warning'      ,'md-pcm'               ,'PCM'  ),
        (14, 'GND'      , ''        ,''                     ,''             ,''                     ,''         ,''                     ,''             ,''         ,'btn-dark'         , ''                    ,''     ),
        (16, 'Gpio_23'  ,'Input'    ,None                   ,'SD0 CMD'      ,'SMI SD15'             ,'DPI D19'  ,'SD1 CMD'              ,'JTAG RTCK'    ,''         ,'btn-warning'      ,'md-gpio'              ,'GPIO' ),
        (18, 'Gpio_24'  ,'Input'    ,None                   ,'SD0 DAT0'     ,'SMI SD16'             ,'DPI D20'  ,'SD1 DAT0'             ,'JTAG TDO'     ,''         ,'btn-warning'      ,'md-gpio'              ,'GPIO' ),
        (20, 'GND'      ,''         ,''                     ,''             ,''                     ,''         ,''                     ,''             ,''         ,'btn-dark'         ,''                     ,''     ),
        (22, 'Gpio_25'  ,'Input'    ,None                   ,'SD0 DAT1'     ,'SMI SD17'             ,'DPI D21'  ,'SD1 DAT1'             ,'JTAG TCK'     ,''         ,'btn-warning'      ,'md-gpio'              ,'GPIO' ),
        (24, 'Gpio_8'   ,'Input'    ,'SPI Chip Select 0'    ,'SPI0 CE0'     ,'SMI SD0'              ,'DPI D4'   ,'AVEOUT VID4'          ,'AVEIN VID4'   ,''         ,'btn-warning'      ,'md-spi'               ,'SPI'  ),
        (26, 'Gpio_7'   ,'Input'    ,'SPI Chip Select 1'    ,'SPI0 CE1'     ,'SMI SWE_N / SRW_N'    ,'DPI D3'   ,'AVEOUT VID3'          ,'AVEIN VID3'   ,''         ,'btn-warning'      ,'md-spi'               ,'SPI'  ),
    ]

    datas_bank_40_1 = [
        (1, '3.3V PWR'  ,''     ,''                      ,''             ,''                     ,''                 ,''             ,''             ,''             ,''                 ,''                    ,''     ),
        (3, 'Gpio_2'    ,'Input','I2C Data'              ,'I2C1 SDA'     ,'SMI SA3'              ,'DPI VSYNC'        ,'AVEOUT VSYNC' ,'AVEIN VSYNC'  ,''             ,'btn-warning'      ,'md-i2c'              ,'I2C'  ),
        (5, 'Gpio_3'    ,'Input','I2C Clock'             ,'I2C1 SCL'     ,'SMI SA2'              ,'DPI HSYNC'        ,'AVEOUT HSYNC' ,'AVEIN HSYNC'  ,''             ,'btn-warning'      ,'md-i2c'              ,'I2C'  ),
        (7, 'Gpio_4'    ,'Input',None                    ,'GPCLK0'       ,'SMI SA1'              ,'DPI D0'           ,'AVEOUT VID0'  ,'AVEIN VID0'   ,'JTAG TDI'     ,'btn-warning'      ,'md-gpio'             ,'GPIO' ),
        (9, 'GND'       ,''     ,''                      ,''             ,''                     ,''                 ,''             ,''             ,''             ,''                 ,''                    ,''     ),
        (11, 'Gpio_17'  ,'Input',None                    ,'FL1'          ,'SMI SD9'              ,'DPI D13'          ,'UART0 RTS'    ,'SPI1 CE1'     ,'UART1 RTS'    ,'btn-warning'      ,'md-gpio'             ,'GPIO' ),
        (13, 'Gpio_27'  ,'Input',None                    ,'SD0 DAT3'     ,'TE1'                  ,'DPI D23'          ,'SD1 DAT3'     ,'JTAG TMS'     ,''             ,'btn-warning'      ,'md-gpio'             ,'GPIO' ),
        (15, 'Gpio_22'  ,'Input',None                    , 'SD0 CLK'     ,'SMI SD14'             ,'DPI D18'          ,'SD1 CLK'      ,'JTAG TRST'    ,''             ,'btn-warning'      ,'md-gpio'             ,'GPIO' ),
        (17, '3.3V PWR' ,''     ,None                    , ''            ,''                     ,''                 ,''             ,''             ,''             ,''                 ,''                    ,''     ),
        (19, 'Gpio_10'  ,'Input',None                    ,'SPI0 MOSI'    , 'SMI SD2'             ,'DPI D6'           ,'AVEOUT VID6'  ,'AVEIN VID6'   ,''             ,'btn-warning'      ,'md-spi'              ,'SPI'  ),
        (21, 'Gpio_9'   ,'Input',None                    , 'SPI0 MISO'   ,'SMI SD1'              ,'DPI D5'           ,'AVEOUT VID5'  ,'AVEIN VID5'   ,''             ,'btn-warning'      ,'md-spi'              ,'SPI'  ),
        (23, 'Gpio_11'  ,'Input',None                    , 'SPI0 SCLK'   ,'SMI SD3'              ,'DPI D7'           ,'AVEOUT VID7'  ,'AVEIN VID7'   ,''             ,'btn-warning'      ,'md-spi'              ,'SPI'  ),
        (25, 'GND'      ,''     ,''                      ,''             ,''                     ,''                 ,''             ,''             ,''             ,''                 ,''                    ,''     ),
        (27, 'Gpio0'    ,'Input','HAT EEPROM i2c Data'   , 'I2C0 SDA'    ,'SMI SA5'              ,'DPI CLK'          ,'AVEOUT VCLK'  ,'AVEIN VCLK'   ,''             ,'btn-secondary'    ,'md-i2c'              ,'I2C'  ),
        (29, 'Gpio_5'   ,'Input',None                    ,'GPCLK1'       ,'SMI SA0'              ,'DPI D1'           ,'AVEOUT VID1'  ,'AVEIN VID1'   ,'JTAG TDO'     ,'btn-warning'      ,'md-gpio'             ,'GPIO' ),
        (31, 'Gpio_6'   ,'Input',None                    , 'GPCLK2'      ,'SMI SOE_N / SE'       ,'DPI D2'           ,'AVEOUT VID2'  ,'AVEIN VID2'   ,'JTAG RTCK'    ,'btn-warning'      ,'md-gpio'             ,'GPIO' ),
        (33, 'Gpio_13'  ,'Input','PWM1'                  ,'PWM1'         ,'SMI SD5','DPI D9'     ,'AVEOUT VID9'      ,'AVEIN VID9'   ,'JTAG TCK'     ,''             ,'btn-secondary'    ,'md-gpio'             ,'GPIO' ),
        (35, 'Gpio_19'  ,'Input','PCM Frame Sync'        , 'PCM FS'      ,'SMI SD11','DPI D15'   ,'I2CSL SCL / SCLK' ,'SPI1 MISO'    ,'PWM1'         ,''             ,'bg-danger-subtle' ,'md-pcm'              ,'PCM'  ),
        (37, 'Gpio_26'  ,'Input',None                    , 'SD0 DAT2'    ,'TE0'                  ,'DPI D22'          ,'SD1 DAT2'     ,'JTAG TDI'     ,''             ,'btn-warning'      ,'md-gpio'             ,'GPIO' ),
        (39, 'GND'      ,''     ,''                      ,''             ,''                     ,''                 ,''             ,''             ,''             ,''                 ,''                    ,''     ),

    ]
    datas_bank_40_2 = [
        (2,  '5V PWR'   ,''         ,''                     ,''             ,''                     ,''         ,''                     ,''             ,''         ,'btn-danger'       ,''                     ,''     ),
        (4,  '5V PWR'   ,''         ,''                     ,''             ,''                     ,''         ,''                     ,''             ,''         ,'btn-danger'       ,''                     ,''     ),
        (6,  'GND'      ,''         ,''                     ,''             ,''                     ,''         ,''                     ,''             ,''         ,'btn-dark'         ,''                     ,''     ),
        (8,  'Gpio_14'  ,'Input'    ,'UART Transmit'        ,'UART0 TXD'    ,'SMI SD6'              ,'DSI D10'  ,'AVEOUT VID10'         ,'AVEIN VID10'  ,'UART1 TXD','btn-warning'      ,'md-uart'              ,'UART' ),
        (10, 'Gpio_15'  ,'Input'    ,'UART Receive'         ,'UART0 RXD'    ,'SMI SD7'              ,'DPI D11'  ,'AVEOUT VID11'         ,'AVEIN VID11'  ,'UART1 RXD','btn-warning'      ,'md-uart'              ,'UART' ),
        (12, 'Gpio_18'  ,'Input'    ,'PCM Clock'            ,'PCM CLK'      ,'SMI SD10'             ,'DPI D14'  ,'I2CSL SDA / MOSI'     ,'SPI1 CE0'     ,'PWM0'     ,'btn-warning'      ,'md-pcm'               ,'PCM'  ),
        (14, 'GND'      , ''        ,''                     ,''             ,''                     ,''         ,''                     ,''             ,''         ,'btn-dark'         , ''                    ,''     ),
        (16, 'Gpio_23'  ,'Input'    ,None                   ,'SD0 CMD'      ,'SMI SD15'             ,'DPI D19'  ,'SD1 CMD'              ,'JTAG RTCK'    ,''         ,'btn-warning'      ,'md-gpio'              ,'GPIO' ),
        (18, 'Gpio_24'  ,'Input'    ,None                   ,'SD0 DAT0'     ,'SMI SD16'             ,'DPI D20'  ,'SD1 DAT0'             ,'JTAG TDO'     ,''         ,'btn-warning'      ,'md-gpio'              ,'GPIO' ),
        (20, 'GND'      ,''         ,''                     ,''             ,''                     ,''         ,''                     ,''             ,''         ,'btn-dark'         ,''                     ,''     ),
        (22, 'Gpio_25'  ,'Input'    ,None                   ,'SD0 DAT1'     ,'SMI SD17'             ,'DPI D21'  ,'SD1 DAT1'             ,'JTAG TCK'     ,''         ,'btn-warning'      ,'md-gpio'              ,'GPIO' ),
        (24, 'Gpio_8'   ,'Input'    ,'SPI Chip Select 0'    ,'SPI0 CE0'     ,'SMI SD0'              ,'DPI D4'   ,'AVEOUT VID4'          ,'AVEIN VID4'   ,''         ,'btn-warning'      ,'md-spi'               ,'SPI'  ),
        (26, 'Gpio_7'   ,'Input'    ,'SPI Chip Select 1'    ,'SPI0 CE1'     ,'SMI SWE_N / SRW_N'    ,'DPI D3'   ,'AVEOUT VID3'          ,'AVEIN VID3'   ,''         ,'btn-warning'      ,'md-spi'               ,'SPI'  ),
        (28, 'Gpio_1'   ,'Input'    ,'HAT EEPROM i2c Clock' ,'I2C0 SCL'     ,'SMI SA4'              ,'DPI DEN'  ,'AVEOUT DSYNC'         ,'AVEIN DSYNC'  ,''         ,'btn-secondary'    ,'md-i2c'               ,'I2C'  ),
        (30, 'GND'      ,''         ,''                     ,''             ,''                     ,''         ,''                     ,''             ,''         ,'btn-dark'         ,'md-gpio'              ,'GPIO' ),
        (32, 'Gpio_12'  ,'Input'    ,'PWM0'                 ,'PWM0'         ,'SMI SD4'              ,'DPI D8'   ,'AVEOUT VID8'          ,'AVEIN VID8'   ,'JTAG TMS' ,'btn-warning'      ,'md-gpio'              ,'GPIO' ),
        (34, 'GND'      ,''         ,''                     ,''             ,''                     ,''         ,''                     ,''             ,''         ,'btn-dark'         ,''                     ,''     ),
        (36, 'Gpio_16'  ,''         ,None                   ,'FL0'          ,'SMI SD8'              ,'DPI D12'  ,'UART0 CTS'            ,'SPI1 CE2'     ,'UART1 CTS','btn-warning'      ,'md-gpio'              ,'GPIO' ),
        (38, 'Gpio_20'  ,''         ,'PCM Data-In'          ,'PCM DIN'      ,'SMI SD12'             ,'DPI D16'  ,'I2CSL MISO'           ,'SPI1 MOSI'    ,'GPCLK0'   ,'btn-warning'      ,'md-pcm'               ,'PCM'  ),
        (40, 'Gpio_21'  ,''         ,'PCM Data-Out'         ,'PCM DOUT'     ,'SMI SD13'             ,'DPI D17'  ,'I2CSL CE'             ,'SPI1 SCLK'    ,'GPCLK1'   ,'btn-warning'      ,'md-pcm'               ,'PCM'  ),
    ]

    if datas[myrevision][3]==26:
        datas[myrevision].append(datas_bank_26_1)
        datas[myrevision].append(datas_bank_26_2)
        datas[myrevision].append(Gpio_init_26)
    elif datas[myrevision][3] == 40:
        datas[myrevision].append(datas_bank_40_1)
        datas[myrevision].append(datas_bank_40_2)
        datas[myrevision].append(Gpio_init_40)
    else:
        datas[myrevision].append(datas_bank_deve_1)
        datas[myrevision].append(datas_bank_deve_2)
        datas[myrevision].append(Gpio_init_26)

    my_gpio_1 = []
    if datas[myrevision][5]:
        for i  in datas[myrevision][5] :
            if 'Gpio_' in i[1]:
                my_gpio_1.append((i[0],i[1],i[2]))
    else:
        datas[myrevision][5] = None

    my_gpio_2 = []
    if datas[myrevision][6]:
        for i in datas[myrevision][6]:
            if 'Gpio_' in i[1]:
                my_gpio_2.append((i[0], i[1], i[2]))
    else:
        datas[myrevision][6] = None
    # sauvegarde config en base de donnée
    if len(ConfigBcm.query.all())==0:
        save_bank(datas[myrevision][5])
        save_bank(datas[myrevision][6])

    result = {
        'raspberry_version':datas[myrevision][0],
        'ram':datas[myrevision][1],
        'revision':datas[myrevision][2],
        'version_gpio':datas[myrevision][3],
        'cpu_info':datas[myrevision][4],
        'banck_gpio_1':datas[myrevision][5],
        'banck_gpio_2': datas[myrevision][6],
        'my_gpio_1':my_gpio_1,
        'my_gpio_2':my_gpio_2,
        'gpio_for_init':datas[myrevision][7]
    }
    return result

def save_bank(bank):

    for data in bank:
        config_bcm = ConfigBcm()
        config_bcm.pin = data[0]
        config_bcm.gpio = []
        config_bcm.name = data[1]
        config_bcm.alt_fct = False
        config_bcm.alt_fct_name = data[3]
        config_bcm.alt_fct_0 = data[4]
        config_bcm.alt_fct_1 = data[5]
        config_bcm.alt_fct_2 = data[6]
        config_bcm.alt_fct_3 = data[7]
        config_bcm.alt_fct_4 = data[8]
        config_bcm.alt_fct_5 = data[9]
        config_bcm.alt_fct_name_other = ''
        config_bcm.class1 = data[10]
        config_bcm.class2 = data[11]
        config_bcm.bus = data[12]
        config_bcm.mode = data[2]

        config.db.session.add(config_bcm)
        config.db.session.commit()
    return

def run_manuel():
    init_gpio()
    gpios = ConfigBcm.query.filter(ConfigBcm.mode=='Output').all()
    for gpio in gpios:
        try:
            #pyApp_gpio.setup(int(gpio.name.split('_')[1]), pyApp_gpio.OUT)
            pyApp_gpio.output(int(gpio.name.split('_')[1]), bool(int(gpio.write_status)))
        except Exception as e:
            print(e, 'je ne suis pas sur un rasberry', ' helpers.py run manuel')
    return

def read_status():

    gpios_all = ConfigBcm.query.filter(or_(ConfigBcm.mode=='Output',ConfigBcm.mode=='Input')).all()
    for gpio in gpios_all:
        try:
            if gpio.mode == 'Input':
                pyApp_gpio.setup(int(gpio.name.split('_')[1]),pyApp_gpio.IN)
            elif gpio.mode == 'Output':
                pyApp_gpio.setup(int(gpio.name.split('_')[1]), pyApp_gpio.OUT)
            gpio.read_status = pyApp_gpio.input(int(gpio.name.split('_')[1]))
        except Exception as e:
            print(e, 'je ne suis pas sur un rasberry', ' helpers.py read_status manuel')
    config.db.session.commit()
    return

def init_gpio():
    gpios_all = ConfigBcm.query.filter(or_(ConfigBcm.mode == 'Output', ConfigBcm.mode == 'Input')).all()
    for gpio in gpios_all:
        try:
            if gpio.mode == 'Input':
                pyApp_gpio.setup(int(gpio.name.split('_')[1]),pyApp_gpio.IN)
            elif gpio.mode == 'Output':
                pyApp_gpio.setup(int(gpio.name.split('_')[1]), pyApp_gpio.OUT)
            else:
                print('nothing')
        except Exception as e:
            print(e, 'je ne suis pas sur un rasberry', ' helpers.py init_gpio')

    return