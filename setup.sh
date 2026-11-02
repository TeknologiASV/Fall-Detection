sudo apt update
sudo apt upgrade
pip3 install --upgrade numpy
pip3 install pandas -U
pip3 install mmWave -U
sudo apt-get install libcblas-dev
sudo apt-get install libhdf5-dev
sudo apt-get install libhdf5-serial-dev
sudo apt-get install libatlas-base-dev
sudo apt-get install libjasper-dev 
sudo apt-get install libqtgui4 
sudo apt-get install libqt4-test
sudo chmod +777 /dev/ttyUSB0
sudo chmod +777 /dev/ttyUSB1
sudo chmod +777 /dev/ttyAMA0
sudo systemctl disable hciuart.service
sudo systemctl disable bluealsa.service
sudo systemctl disable bluetooth.service
sudo apt-get install python3-dev libmysqlclient-dev libmariadb-dev-compat libmariadb-dev
pip3 install mysqlclient
sudo reboot
