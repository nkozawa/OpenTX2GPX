# OpenTX2GPX
OpenTX2GPX converts OpenTX Log file contains GPS telemetry data to GPX file. OpenTX2GPX reads timestamp, GPS coordinate, speed, altitude, number of GPS satelites from OpenTX log and exports to GPX track points.

## Setup and running OpenTX2GPX
### Python environment
If you have Python 3.x environment, just you need to do following.
- pip install gpxpy
- python3 OpenTXGPX.py
### MacOS
Download and extract OpenTX2GPXMac.zip. OpenTX2GPX is MacOS executable.
### Windows
Download and extract OpenTX2GPXMac.zip. OpenTX2GPX.exe is Windows executable. 
Some of antivirus program may show trojan alert. I hope that you can setup antivirus software to ignore/bypass OpenTX2GPX.

## Additional Informatios
- OpenTX is open source firmware for RC radio trasnmitter. It has ability to logging telemtry data from RC receiver on the drone or plane. If GPS device is available on the drone or plane, we will have GPS coordinate, speed and altitude. OpenTX log is stored on the SD card of RC radio as CSV format.
- GPX (GPS Exchange Format) is supported by various softwares and web sites. This is most convinent data format to carry GPS log entries.
