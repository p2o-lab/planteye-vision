# set base image (host OS)
FROM python:3.8

# set the working directory in the container
WORKDIR /vision

# update and install components
RUN apt-get update -y
RUN apt install libgl1-mesa-glx -y
RUN apt-get install 'ffmpeg'\
    'libsm6'\
    'libxext6'  -y

# install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# copy files into the working directory
COPY src/ src/
COPY config.yaml .
COPY main.py .

# command to run on container start
CMD [ "python", "main.py" ]
