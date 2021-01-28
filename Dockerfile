# set base image (host OS)
#FROM arm32v7/python:3.8
FROM arm32v7/python:3.7-buster
#FROM arm32v7/python:3.9

# Instructions to compile OpenCV by Josip Janzic <josip@jjanzic.com>
RUN apt-get update \
    && apt-get install -y \
        build-essential \
        cmake \
        git \
        wget \
        unzip \
        yasm \
        pkg-config \
        libswscale-dev \
        libtbb2 \
        libtbb-dev \
        libjpeg-dev \
        libpng-dev \
        libtiff-dev \
        libavformat-dev \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*
RUN pip install numpy
RUN pip3 install opencv-python
WORKDIR /
ENV OPENCV_VERSION="4.5.0"
RUN wget https://github.com/opencv/opencv/archive/${OPENCV_VERSION}.zip \
&& unzip ${OPENCV_VERSION}.zip \
&& mkdir /opencv-${OPENCV_VERSION}/cmake_binary \
&& cd /opencv-${OPENCV_VERSION}/cmake_binary \
&& cmake -DBUILD_TIFF=ON \
  -DBUILD_opencv_java=OFF \
  -DWITH_CUDA=OFF \
  -DWITH_OPENGL=ON \
  -DWITH_OPENCL=ON \
  -DWITH_IPP=ON \
  -DWITH_TBB=ON \
  -DWITH_EIGEN=ON \
  -DWITH_V4L=ON \
  -DBUILD_TESTS=OFF \
  -DBUILD_PERF_TESTS=OFF \
  -DCMAKE_BUILD_TYPE=RELEASE \
  -DCMAKE_INSTALL_PREFIX=$(python3.9 -c "import sys; print(sys.prefix)") \
  -DPYTHON_EXECUTABLE=$(which python3.9) \
  -DPYTHON_INCLUDE_DIR=$(python3.9 -c "from distutils.sysconfig import get_python_inc; print(get_python_inc())") \
  -DPYTHON_PACKAGES_PATH=$(python3.9 -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())") \
  .. \
&& make install \
&& rm /${OPENCV_VERSION}.zip \
&& rm -r /opencv-${OPENCV_VERSION}
RUN ln -s \
  /usr/local/python/cv2/python-3.9/cv2.cpython-37m-x86_64-linux-gnu.so \
  /usr/local/lib/python3.9/site-packages/cv2.so

# set the working directory in the container
WORKDIR /vision

# update and install components TODO: check if needed
#RUN apt-get install libgl1-mesa-glx -y
#RUN apt-get install 'ffmpeg'\
#    'libsm6'\
#    'libxext6'  -y

# install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# copy files into the working directory
COPY src/ src/
#COPY config.yaml .
COPY main.py .

# command to run on container start
CMD [ "python", "main.py" ]
