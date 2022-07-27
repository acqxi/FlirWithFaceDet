# Install
你需要先安裝以下套件才能開始使用本模型
### QT
由於 QT4 已經被 QT5 替換不再提供下載，所以我們改裝 QT5
由於我們使用的系統已經過時，因此更新需附加上參數 --allow-releaseinfo-change
```bash
sudo apt-get update --allow-releaseinfo-change 
sudo apt install qtbase5-dev
```
### OpenCV
必要套件
```bash
sudo apt-get update
sudo apt-get install -y python3-dev python3-pip
sudo apt-get install -y build-essential cmake pkg-config
sudo apt-get install -y libjpeg-dev libtiff5-dev libjasper-dev libpng-dev
sudo apt-get install -y libavcodec-dev libavformat-dev libswscale-dev libv4l-dev
sudo apt-get install -y libxvidcore-dev libx264-dev
sudo apt-get install -y libfontconfig1-dev libcairo2-dev
sudo apt-get install -y libgdk-pixbuf2.0-dev libpango1.0-dev
sudo apt-get install -y libgtk2.0-dev libgtk-3-dev
sudo apt-get install -y libatlas-base-dev gfortran
sudo apt-get install -y libhdf5-dev libhdf5-103
sudo apt-get install -y libqtgui4 libqtwebkit4 libqt4-test python3-pyqt5
```
下載 OpenCV4.1 和 contrib
```bash
cd ~
wget https://github.com/opencv/opencv_contrib/archive/4.1.1.tar.gz -O opencv_contrib-4.1.1.tar.gz
tar zxvf opencv_contrib-4.1.1.tar.gz
wget https://github.com/opencv/opencv/archive/4.1.1.tar.gz
tar -zxvf 4.1.1.tar.gz 
cd opencv-4.1.1
mkdir build
cd build
```
編譯安裝 OpenCV4.1
```bash
cmake -D CMAKE_BUILD_TYPE=RELEASE \
 -D CMAKE_INSTALL_PREFIX=/usr/local \
 -D OPENCV_EXTRA_MODULES_PATH=/home/pi/opencv_contrib-4.1.1/modules \
 -D ENABLE_NEON=ON \
 -D ENABLE_VFP3=ON \
 -D BUILD_TESTS=OFF \
 -D INSTALL_C_EXAMPLES=ON \
 -D INSTALL_PYTHON_EXAMPLES=ON \
 -D BUILD_EXAMPLES=ON \
 -D OPENCV_ENABLE_NONFREE=ON \
 -D CMAKE_SHARED_LINKER_FLAGS=-latomic ..
time make -j4 VERBOSE=1
sudo make install
```
### V4L2
安裝編譯 v4l2loopback 必要軟體
```bash
sudo apt-get update
sudo apt-get install -y bc flex bison  libncurses5-dev
sudo wget  https://raw.githubusercontent.com/notro/rpi-source/master/rpi-source -O /usr/bin/rpi-source && sudo chmod +x /usr/bin/rpi-source  && /usr/bin/rpi-source -q --tag-update
rpi-source
```
編譯 v4l2loopback 虛擬裝置節點
```bash
cd ~
git clone  https://github.com/umlaeute/v4l2loopback
cd ~/v4l2loopback
sudo make
sudo make install
```
安裝 V4L2 Kernel Module （ *每次開機都需要重新啟用* ）
```bash
sudo depmod -a
sudo modprobe v4l2loopback
lsmod | grep v4l2loopback
```
### pylepton
安裝
```bash
cd ~
git clone  https://github.com/groupgets/pylepton -b lepton3-dev
cd ~/pylepton
sudo python3 setup.py install
```
測試看看是否正常
```bash
cd ~/pylepton
./pylepton_capture output.jpg
gpicview output.jpg
```

# Usage
請參考檔案中的 PowerPoint 文件 (FLIR+Camera)toDetBodyTemp.pptx