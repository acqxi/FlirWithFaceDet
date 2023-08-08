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
### calibration
先確定已經下載好這份git
```bash
git clone https://github.com/acqxi/FlirWithFaceDet.git FLIR
```
接著執行雙相機拍照程式
```bash
cd FLIR/thermal-pi/02-calibration
python3 camera_preview.py
```
在確定相機與熱像儀畫面皆是清晰的輪廓時，在彈出的相機視窗中按下 'c' 來儲存照片，按下 'q' 退出。
接著使用給你的隨機生成檔名(應該是一串數字如 `1630947343`)校正相機
```bash
python3 registration.py -i [FILE]
```
`[FILE]`是剛剛說到的檔名(無須副檔名)
等到出現校正結果後，校正就完成了，他應該會自動儲存到父目錄的 `fusion.conf` 檔案中，如果沒有或是想要微調的話可從這裡調整。

# Usage
請參考檔案中的 PowerPoint 文件 FLIR.pdf
### Run
最後透過以下指令執行以編寫好的程式 (須確定已經校正相機位置)
``` bash
git clone https://github.com/acqxi/FlirWithFaceDet.git FLIR
cd FLIR/thermal-pi/04-application/
python3 thermometer.py
```
### arguments
此程式有以下參數可以設定
```yaml
python3 thermometer.py -h

usage: thermometer.py [-h] [--show SHOW] [--confidence CONFIDENCE]
                      [--fontscale FONTSCALE] [--screenscale SCREENSCALE]
                      [--fontthick FONTTHICK] [--adjust ADJUST]
                      [--modeldeploy MODELDEPLOY] [--caffemodel CAFFEMODEL]

optional arguments:
  -h, --help            show this help message and exit
  --show SHOW, -s SHOW  show real-time pic be taken from device
  --confidence CONFIDENCE, -cf CONFIDENCE
                        confidence df: .5
  --fontscale FONTSCALE, -fs FONTSCALE
                        font scale df: 1
  --screenscale SCREENSCALE, -ss SCREENSCALE
                        screen scale df: 1
  --fontthick FONTTHICK, -ft FONTTHICK
                        font thickness df: 2
  --adjust ADJUST, -ad ADJUST
                        adjust temp + ?
  --modeldeploy MODELDEPLOY, -md MODELDEPLOY
                        model's deploy text file df: deploy.prototxt.txt
  --caffemodel CAFFEMODEL, -cm CAFFEMODEL
                        caffe model file df: res10_300x300_ssd_iter_140000.caffemodel
```
- show
    控制是否要輸出畫面，預設是輸出
- confidence
    控制信賴度，調整以決定模型需要多少信賴度才會將物體辨識為人臉，越低越容易將物體視為人臉，預設 0.5
- fontscale
    輸出的圖片中字體大小，預設 1
- screenscale
    輸出的圖片大小，預設 1
- fontthick
    輸出的圖片中字體粗細，預設 2
- adjust
    調整溫度偏移，填寫2將會把偵測到的數值增加兩度，請依場域使用，預設 1.5
- modeldeploy
    如果想使用別的 caffe 模型時，請將 deploy 文字檔路徑填在這
- caffemodel
    如果想使用別的 caffe 模型時，請將 .caffemodel 檔路徑填在這

### TrobleShooting
1. Q : 熱像儀影像與RGB影像不批配。
    - A : 請重新校正雙相機，PDF p.160。
2. Q : 判讀溫度與實際溫度不符。
    - A1 : 請盡量移除錄攝環境中不相關的熱源。
    - A2 : 有時熱像儀會受當時氣溫或光線而產生讀取值偏移，可以透過參數 --adjust 進行校正微調。
    - A3 : 有時候目標經太陽久曬或因其他原因可能在臉部造成不正常熱源而導致溫度讀數偏差，建議此時可以透過人工良量測額溫、耳溫來複查。
3. Q : 無法偵測到目標人臉。
    - A : 請確認環境光照良好，且目標臉部遮擋盡量減少後重試。

### warning
本應用可能存在以下問題發生的風險，必要時請安排人員複檢。
- 由於環境或目標個人因素導致檢測體溫失常。
- 由於環境或目標個人因素導致人臉偵測失敗。
