# PlantEye/Vision

PlantEye/Vision is a tool for data collection.\
Shortly, PlantEye/Vision requests data from different data sources (data inlets) that are given in the configuration file.\
Afterwards, the aggregated data are provided via a defined interface (shell). It might be a RESTAPI interface or local storage, wherein the data will be saved as files.

## Usage
To run the script be sure that config-file (config.yaml) is proper and then run the script:
```bash
python main.py
```

## Configure
Create a config file according to the following structure:
```yaml
---
inlet:
  camera:
    type: local_camera_cv2 #baumer_camera_neoapi
    access:
      device_id: 0
    parameters:
      Width: 720
      ExposureTime: 720
    metadata:
      '010F': Raspberry Pi # Manufacturer of recording equipment
      '0110': HQ Camera v1.1 # The model name or model number of the equipment
      'A432': 6mm f/1.2 # Lens specification.
      'A433': RPIZ # Lens manufacturer.
      'A434': PT361060M3MP12 # Lens model.
      '013B': P2O-Lab # This tag records the name of the camera owner, photographer or image creator.
      '0131': PlantEye/Vision, 1.0.0 # This tag records the name and version of the software.
      '9208': Vessel light, 2.5 W # The kind of light source.
      '9206': undefined # The distance to the subject, given in meters.
      '0140': undefined  # A color map for palette color images.
      '0112': 1 # The image orientation
      '829D': 1.2 # The F number.
      '8827': 100 # This tag indicates the ISO speed value of a camera or input device that is defined in ISO 12232.
      '9201': 1/8000 # Shutter speed.
      '9202': 1.2 # The lens aperture.
      '920A': 6 # The actual focal length of the lens, in mm.
  light_conditions:
    type: static_variable
    value: natural
    metadata:
      unit: none
      interpretation: no artificial light switched on
      description: light conditions during experiment
  flow_regime:
    type: static_variable
    value: 0
    metadata:
      unit: none
      interpretation: flooded
      description: flow regime in reactor
  stirrer_rotational_speed:
    type: opcua_variable
    access:
      server: 'opc.tcp://opcuademo.sterfive.com:26543'
      username:
      password:
      node_ns: 8
      node_id: Scalar_Simulation_Float
    metadata:
      unit: none
      interpretation: none
      description: a selected opcua variable
#shell:
#  local:
#    type: local
#    access:
#      storage_path: ../data
#      time_interval: 1000
shell:
  rest_api:
    type: rest_api
    access:
      host: 0.0.0.0
      port: 5000
      name: 'PlantEye-Vision'
      endpoint: '/get_frame'
```
Further metadata, tags and labels can be added.
Some example configurations can be found in ../res/

### Supported data inlet types

#### local_camera_cv2
Use value "local_camera_cv2" in the field capturing_device.type for a local camera, e.g. USB or built-in camera.
In this case the package opencv will be used to capture the frame.

#### baumer_camera_neoapi
This inlet type allows to use smart cameras manufactured by Baumer.
This inlet type is supported to be run only withing the camera hardware itself.
Access to the camera hardware is via neoAPI. To able to use this inlet type neoAPI for python is to install via pip in advance:
```bash
pip3 install wheel_file.whl
```
Please find information on how to get neoAPI on the official webpage of Baumer.

#### static_variable
A static value can be specified by giving its value in the configuration file.

#### opcua_variable
This inlet type allows to link an opcua variable.
In this case the opcua node will be requested via a poll request and its value will be provided.

### Supported shell types
#### local
This shell type requests data from data inlets according to a given regular time basis.
The data will be stored on the local disk as a pair of files: image_file (if any camera inlet is specified) and json file.

#### rest_api
This shell type starts a RestAPI endpoint that provides data in the form of a json response. Data from camera inlets are encoded as base64.
The standard endpoint is:
```html
/get_frame
```
The endpoint can be changed in the configuration file.

Method:
GET

URL Params:
No parameters needed

Response example:
```json
{
   "camera":{
      "inlet_type":"local_camera_cv2",
      "inlet_name":"camera",
      "inlet_access_data":{
         "device_id":0
      },
      "data":{
         "frame": frame_encoded_as_base64
      },
      "metadata":{
         "timestamp":1637942511818,
         "colormap":"BGR",
         "shape":[
            480,
            640,
            3
         ],
         "010F":"Raspberry Pi",
         "0110":"HQ Camera v1.1",
         "A432":"6mm f/1.2",
      },
      "status":{
         "Frame capturing":{
            "code":0,
            "message":"Frame captured"
         }
      }
   },
   "light_conditions":{
      "inlet_type":"static_variable",
      "inlet_name":"light_conditions",
      "inlet_access_data":{
         
      },
      "data":{
         "light_conditions":"natural"
      },
      "metadata":{
         "unit":"none",
         "interpretation":"no artificial light switched on",
         "description":"light conditions during experiment"
      },
      "status":{
         
      }
   },
   "flow_regime":{
      "inlet_type":"static_variable",
      "inlet_name":"flow_regime",
      "inlet_access_data":{
         
      },
      "data":{
         "flow_regime":0
      },
      "metadata":{
         "unit":"none",
         "interpretation":"flooded",
         "description":"flow regime in reactor"
      },
      "status":{
         
      }
   }
}
```
The response consists of a list of so-called data chunks (e.g. "camera", "light_conditions" and "flow_regimes").
Data chunks have the same inner structure consisting of inlet_type, inlet_name, inlet_access_data, data, metadata and status.

### Inlet type
inlet_type defines the type of the data inlet.

### Inlet name
inlet_name denotes a unique name of the data inlet. It shadows the name of the corresponding key it belongs to.

### Inlet access data
inlet_access_data contains the data used to connect to the data inlet.

### Data
data includes data values. The value or values are collected depending on the specified type of the data inlet.

### Metadata
metadata is a structure, which contains metadata to collected value/values, e.g. unit, measurement range or resolution of the captured image.

### Status
status has information on data collection and processing steps.

## Requirements
To install requirements use the following command:
```bash
pip3 install -r requirements.txt
```

## License
Valentin Khaydarov (valentin.khaydarov@tu-dresden.de)\
Process-To-Order-Lab (https://tu-dresden.de/ing/forschung/bereichs-labs/P2O-Lab)\
TU Dresden\
