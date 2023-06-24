# deprag_downloader
## Application
This ROS node allows to automatically download curves saved by a deprag screwdriver.
To do so simply call the provided ROS service with the corresponding number.

## Dependencies
This Package was developed using ROS Melodic other versions might work but are not tested.
Selenium for Python with a Firefox driver installed.

## Setup
After installing all dependencies change the "downloadDirectory" variable in deprag_downloader_node.py to 
the file path where the csv files should be saved.
Now change the folder name of the folder you cloned from git to "deprag_downloader"
Furthermore, change the "depragIP" variable to the address matching your deprag screwdriver.

## Usage
After making sure roscore is running start the deprag_downloader_node using
```
$ rosrun deprag_downloader deprag_downloader_node.py 
```
Now a curve can be saved by calling the "/deprag_download" service.
```
$ rosservice call /deprag_download arg
```

The number with which the service is called determines what curve is downloaded.
Notice that 0 will download all files available, therefore passing 1 will download the latest curve.

When calling with a value < 0 it will download the last curve and the corresponding programm parameters and publish both under /deprag/curves.
```
$ rostopic echo /deprag/curves
```
A json file containing the program parameters and the curve values is saved in the download directory the files name is determined by the current system time.

## json
The json contains all program information in accordance with the used deprag manual. The csv curve data is saved in a 
structure called "csv" where it is separated into different arrays.

"Zeit(0.001 ms)" represents the time passed since starting the programm in 0.001 ms

"Drehmoment Messsystem 1 (Nm)" is the torque messured by system 1 in Nm

"Winkel Messsystem 1" is the angle messured by system 1 

"Drehmoment Motor (Nm)" is the torque messured by the motor in Nm

"Winkel Motor" is the angle messured by the motor

"Drehzahl (U/min)" represents rpm

"Schritt" represents the steps taken

"Stromstaerke (A)" represents the amperage drawn in amps

"Temperatur (C)" represents the motor temperature in Celcius


## Acknowledgement
Sponsored by the Ministry of the Environment Baden-Württemberg, in the context of the Strategic Dialogue Automotive Industry, and supervised by the Project Management Agency Karlsruhe (PTKA). Funding number: L7520101

https://www.ipa.fraunhofer.de/de/referenzprojekte/DeMoBat.html

## Contact
For more information please feel free to contact: <br />
M.Sc. Anwar Al Assadi<br />
M.Sc. Balázs András Bálint<br />
Fraunhofer‐Institut für<br />
Produktionstechnik und Automatisierung IPA<br />
Abteilung Roboter- und Assistenzsysteme<br />
anwar.alassadi@ipa.fraunhofer.de<br />
