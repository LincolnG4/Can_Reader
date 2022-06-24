# BIRA_2.0

Software for raspberry pi 3B+ to collect and read CAN Bus data in J1939 protocol



  The project consist in a Raspberry Pi 3B+ (OS Lite 4.9.80-v7) + module Can Bus Mcp2515 Tja1050 to collect extended 29bits J1939 messages in real vehicle 

<h2>1 - SETUP<h2> 

**1.1 - HARDWARE MCP2515 SETUP**


<img src="http://domoticx.com/wp-content/uploads/2020/12/CAN-bus-SPI-module-met-MCP2515-TJA1050-overview.jpg"  width="300">



<table style="width:100%">
  <tr>
    <th>MCP2515's PIN</th>
    <th>Raspberry Pi's PIN</th> 
  </tr>
  <tr>
    <td>VCC</td>
    <td>1 (3V3)</td>
  </tr>
  <tr>
    <td>GND</td>
    <td>6 (GND)</td>
  </tr>
  <tr>
    <td>CS</td>
    <td>24</td>
  </tr>
  <tr>
    <td>MISO</td>
    <td>21</td>
  </tr>
  <tr>
    <td>MOSI</td>
    <td>19</td>
  </tr>
  <tr>
    <td>SCK</td>
    <td>23</td>
  </tr>
  <tr>
    <td>INT</td>
    <td>22</td>
  </tr>

</table>



**1.2 - SOFTWARE SETUP**


Installing on linux 




_1.2.1._  Drag all files of `./setup` git folder in your hardware;
Files needed:  
-  code.tar (Create a compress file '.tar' with of all codes,services,dbc,... inside 'code' folder)  
_see a example code.tar on ./setup. Check if the files are updated_  
-  installer.sh  
-  requirements_linux.list  
-  requirements_python.txt  


_1.2.2._ run `sudo chmod u+x installer.sh`  

_1.2.3._ run `./installer.sh`, wait for the end



_1.2.4._ With GPS disconnected, run `ls /dev`  
_1.2.5._ With GPS connected, run `ls /dev`  
_1.2.6._ Find the device connected  
 
_1.2.7._ run `sudo nano /lib/systemd/system/gpsd.socket ` and change the second `ListenStream` value to `0.0.0.0:2947`  
  
_1.2.8._ run `sudo killall gpsd`  
_1.2.9._ run `sudo gpsd /dev/ttyACM0 -F /var/run/gpsd.sock ` (Change `ttyACM0` if the the value found in step 1.2.6 of GPS setup )  
_1.2.10._ Reboot the system  
_1.2.11._ Test the GPS connection running `gpsmon`  
  




**1.3 - TEST WITH _Vector Canalyzer_**
With Canalyzer setup and generating messages:
On terminal,

`candump can0` 





<h2>2 - SOFTWARE<h2>

**2.1 - SERVICES FLOWCHART**

 

The Bira_2.0 is based on the services: `starter_mf4`,`measure`,`dbc_decoder`,`zip_sd`, `CLOUD`

All services are managed by `config.init` & `bash.config`

  -   `config.init` - Configure Python script  
  -   `bash.config` - Configure Bash scripts




**2.2 - starter_mf4:**
  This service is responsable to start/check the workflow of the system. It runs the `start.sh` file, which, first, send a 1kb-dummy-file to `./measure` folder. This file active the workflow which try to push old files stucked on folders. Second, it checks the size of all folders, if the folder size is greater than the limit configured, 'start.sh' will delete last file in the folder to try to free space.

- `starter_mf4` run every boot
- `starter_mf4` restart every 300 seconds (restart time can be configure in the service)
- Limit size can be configure in `start.sh` file 
- The `start.sh` is configured by `bash.config`

**2.3 - measure:**
 This service is the main service, it is responsable to start the measurement. It runs the `can_mf4.py` file, which is responsable to read the CAN-BUS, GPS and generate the MF4 files.

- `measure` run every boot
- `measure` restart every 5 seconds if `can_mf4.py` stop (restart time can be configure in the service)
- The `can_mf4.py` is configured by `config.init`

**2.4 - dbc_decoder:**
 This service is responsable to apply/not apply the dbc file in the measure. It runs the `dbc_decoder.py` file, which is responsable to translate the mf4 for human readble  in `./measure` folder to `./sort` folder. Also, the dbc apply can be desactivated in `config.init`, which will allow only send raw file from `./measure` folder to `./sort` folder. 

- `dbc_decoder` run every boot
- `dbc_decoder` restart every 10 seconds if `dbc_decoder.py` stop (restart time can be configure in the service)
- The `dbc_decoder.py` is configured by `config.init`


**2.5 - zip_sd:**
 This service is responsable to zip files and management the pendrive storage. It runs the `zip_sort.sh` file, which is responsable to zip the mf4, save on `pendrive`, if pendrive is full the files will be store in raspberry pi. Also, the `pendrive` storage can be desactivated in `bash.config`, which will allow only send to cloud without save files in raspbery pi/pendrive.

- `zip_sd` run every boot
- `zip_sd` restart every 10 seconds if `zip_sort.sh` stop (restart time can be configure in the service)
- The `zip_sort.sh` is configured by `bash.config`

**2.6 - cloud:**

 This service is responsable to send the zip files to the cloud. It runs the `cloud.py` file, which is responsable to management Azure blob input.

- `cloud` run every boot
- `cloud` restart every 10 seconds if `cloud.py` stop (restart time can be configure in the service)
- The `cloud.py` is configured by  `config.init` & `bash.config`

**2.7 - CONFIG.INIT:**

All services are managed by `config.init` or `bash.config`. Be aware when you change the standard of the file.

You can grab a base file in `./examples/config.init`. All variables need to be filled.

The `config.init` is structure in blocks: 

**[DEFAULT]**

```
[DEFAULT]
enable_decoder = False
timer = 10
root_path = /home/pi/code
```
- **enable_decoder:** _True_ (Measure will be decoded with DBC) / _False_ 
- **timer:** measure time per file
- **root_path:**: Default

__________________


**[GPS]**

```
[GPS]
port= /dev/ttyACM0
baudrate = 115200
```
- **port:** usb port on system
- **baudare:** see on your gps's datasheet


__________________

**[CAN]**

```
[CAN]
can_interface = can0
bustype = socketcan
enable_filtering = True
can_filters = CF00400,18FEE900
```

- **can_interface:** can port configured on topic 1.3 & 1.4
- **bustype:** `socketcan` is default for this case (don't change)
- **enable_filtering:** _True_ (Filter to messages will be apply / _False_ (All messages will came on can broadcasting)
- **can_filters:** Apply filtering to all messages received by this Bus.

  All messages that match at least one filter are returned. If filters is None or a zero length sequence, all messages are matched.

  So:
  ```
  # The following just equals zero
  0xCF00400 & 0 == 0 # True

  # The following equals 0xCF00400 (217056256 in decimal) exactly
  0xCF00400 & 0xFFFFFFF == 0xCF00400 # True
  0xCF00400 & 0xFFFFFFF == 217056256 # True

  # The following can_id would not get through the filter + mask:
  0x18fee500 & 0xFFFFFFF == 0xCF00400 & 0xFFFFFFF # False

  # The following obviously would get through the filter + mask:
  0xCF00400 & 0xFFFFFFF == 0xCF00400 & 0xFFFFFFF # True
  ```

  Example how to configure:

  ```
  # just 0xCF00400 and 0x18fee927 will be grab
  can_filters = CF00400,18fee927
  ```

__________________

**[MEASURE]**


```
[MEASURE]
path: ${DEFAULT:root_path}/measure
output_file_name : Vehicle_001_measure_CAN_1_
path_decoded:${DEFAULT:root_path}/sort
```

- **path:** default
- **out_file_name:** Name of the measure file (free to change; all files will filled by the timestamp on the end of the name)
- **path_decoded:** default

__________________

**[CLOUD]**


```
[CLOUD]
path=./send
connection = your_azure_container_string
container = demo
```

- **path:** Default
- **connection:** string name to connect on Azure container
- **container:** container's name


__________________

**[LOG]**


```
[LOG]
path = ${DEFAULT:root_path}/log
enable_log = True  
file_name: Bira
```
- **path:** Default
- **enable_log:** _True_ / _False_
- **file_name:** Log Filename 


__________________

**[DBC]**


```
[DBC]
path: ${DEFAULT:root_path}/dbc
files: j1939.dbc, Startstop.dbc
```
- **path:** Default
- **files:** name of dbc files (in `./dbc`) to be apply in decode



**2.8 - BASH.CONFIG:**

```
{
  "Startfile": "/home/pi/code/start.mf4",
  "Measurefolder":"/home/pi/code/measure/start.mf4",
  "enable_save_on_sd":"True",
  "enable_save_on_cloud":"False"
}
```

- **Startfile:** Default
- **Measurefolder:** Default
- **enable_save_on_sd:** _True_ (Zip files will be also storage in PenDrive) / _False_
- **enable_save_on_cloud:** _True_ (Zip files will be send to './cloud' folder) / _False_


<h2>3 - TOOLS<h2>

**3.1 - Log file to MDF**

 The code `log2mf.py` on folder `./src/ `creates a MF4 file based on a log file.
 
the log file needs to be formated as below:

`<Time> <Tx/Rx> <Channel> <CAN ID> <Type> <DLC> <DataBytes>`

`12:20:37:6601 Rx 1 0x254 s 8 02 00 F3 01 C0 00 53 7D `

As example, you can download the `can.log` on folder `./example`;


**HOW TO USE:**
 
- Drag and drop the '_.log_' file on the `log2mf.py` code
- Open the file in ASAMMDF 
- In ASAMMDF, in the menu click on 'CAN logging'
- Apply the DBC and select 'Ignore invalid signal'
- Click on 'export'

