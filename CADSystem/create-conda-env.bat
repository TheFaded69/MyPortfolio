@ECHO OFF

echo Try create conda env

call conda create --name cadsi python=3.7 -y
echo Conda env create (name = cadsi)

call conda activate cadsi

echo Update pip
call python -m pip install --upgrade pip

echo Run root setup.py
call pip install .

echo Run libcore setup.py
call pip install libcore\.

echo Install psutil
call pip install psutil==5.8.0

echo Install pydicom
call pip install pydicom==1.4.0
call pip install pyqt5
call pip install h5py

call conda deactivate


echo Conda env created
echo Use 'conda activate cadsi' and 'python run.py'

PAUSE