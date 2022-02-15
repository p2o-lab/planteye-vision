# PlantEye-Vision

PlantEye-Vision is a tool for building complex distributed pipelines in the field of data science and in particular machine learning.\
Shortly, PlantEye-Vision requests data from different data sources (data inlets) that are given in the configuration file.\
If any processor specified, they will be applied on data retrieved from the data inlets.\
After execution of the processors, their resulted data will be combined with data provided by the inlets. It will form the result body.\
Depending on the specified shell type, the result body is available for the end-user either per request or on a time regular basis.\

## Installation
Use the package manager [pip](https://pip.pypa.io/en/stable/) to install.

```bash
pip install planteye-vision
```

## Requirements
Depending on the current configuration, PlantEye-Vision might require installation of additional packages, e.g. opcua-python for opcua inlet.

## Usage
The PlantEye-Vision instance expects a configuration to be specified.
The easiest way is to create a separate yaml file with the configuration and load it as shown below:

```python
from planteye_vision.pipeline_execution.pipeline_executor import PipeLineExecutor
from planteye_vision.configuration.planteye_configuration import PlantEyeConfiguration
from yaml import safe_load

path_to_config_file = 'config_minimal_restapi.yaml'
with open(path_to_config_file) as config_file:
    config_dict = safe_load(config_file)

config = PlantEyeConfiguration()
config.read(config_dict)
PipeLineExecutor(config).run()
```

## Configuration
The configuration consists of three major sections: inlets, processors and shell.
Please use the following configuration as an example.
```yaml
---
inlets:
  1: # Step name, does not affect anything
    name: camera # inlet name, that will be stored in data structure together with the data
    type: local_camera_cv2 # inlet type (see further for more details)
    hidden: False # this flag specified whether this parameter is to hide from the end-user
    parameters: # here comes the list of inlet specific parameters required to configure data source
      device_id: 0
      Width: 720
      ExposureTime: 720
    metadata: # list of metadata that will be output to the end-user along with the data
      '010F': Raspberry Pi
  2:
    name: flow_regime
    type: static_variable
    hidden: False
    parameters:
      value: 0
    metadata:
      unit: none
      interpretation: flooded
      description: flow regime in reactor
  3:
    name: stirrer_rotational_speed
    type: opcua_variable
    parameters:
      server: 'opc.tcp://opcuademo.sterfive.com:26543'
      username:
      password:
      node_ns: 8
      node_id: Scalar_Simulation_Float
    metadata:
      unit: none
      interpretation: none
      description: a selected opcua variable
processors:
  0:
    name: image_input
    type: input
    input_inlets:
      - camera
  1:
    name: resize
    type: image_resize
    hidden: True
    parameters:
      width: 250
      height: 250
      interpolation: INTER_NEAREST
  2:
    name: crop
    type: image_crop
    hidden: True
    parameters:
      x_init: 2
      x_diff: 248
      y_init: 2
      y_diff: 248
  3:
    name: inference
    type: tf_inference
    hidden: False
    parameters:
      path_to_models: '../res/models/'
      model_name: 'dogs_vs_cats'
      model_version: '1.0'
shell:
  type: rest_api
  parameters:
    host: 0.0.0.0
    port: 5000
    endpoint: '/get_frame'
```
Some typical configurations can be also found in the folder /example

### Data inlets
Data inlets are data sources which provides data.
Each data inlet type has its specific configuration parameters, some of which are necessary to specify.
In case necessary parameters are not given, the inlet will be excluded during the initialisation phase.
If parameters are correct, but no connection with the data inlet can be temporarily established, the software will be trying to establish it every time a request incomes.

#### local_camera_cv2
This inlet type represents a generic capturing device without specific SDK or API.
In this case, opencv package will be used to access the frame feed.
Parameters:\
  device_id: identifier of the capturing device (see description to the opencv method cv2.VideoCapture(device_id)) 
  further parameters with corresponding values can be optionally specified, for full list of supported parameters please refer to https://docs.opencv.org/3.4/d4/d15/groupvideoioflagsbase.html Please omit prefix 'cv2.' specifying them in the configuration file.

This inlet type is recommended to use with usb or built-in cameras when the manufacturer provides no python api.

#### baumer_camera_neoapi
This inlet type represents a capturing device of company Baumer.
Comparing to generic camera, this inlet exploits neoAPI provided by Baumer.
Parameters:\
  device_id (optional, default: 0) identifier of the capturing device
  further parameters with corresponding values can be optionally specified, please refer to Baumer documentation to get more information about settable parameters

To able to use this inlet type, an additional python package neoAPI is to install via pip in advance:
```bash
pip3 install wheel_file.whl
```
This inlet type can be used ONLY with cameras that are compatible with Baumer's neoAPI.
Please find information on how to get neoAPI on the official webpage of Baumer.

#### static_variable
A static value can be specified by giving its value in the configuration file.
Parameters:\
  value (necessary): the value might be any data type supported by yaml
Use this inlet type for specifying values or additional information that are constant but is also of interest for the end-user, e.g. experiment id or/and conditions 

#### opcua_variable
This inlet type allows to link an opcua variable and poll values from the opcua node.
Parameters:\
  server (necessary): the value might be any data type supported by yaml
  username (optional, default None): username to connect to the opcua server, if required
  password (optional, default None): password to connect to the opcua server, if required
  node_ns (necessary): namespace of the opcua node
  node_id (necessary): id of the opcua node
Please bear in mind that currently every inlet of this type creates a session with the given opcua server, even if it is the same server.
As data access method polling is used.

#### restapi
This inlet type allows chaining several instances of PlantEye via rest api interface.
Parameters:\
  endpoint (necessary): use this parameter to specify a url of another PlantEye instance, from which the data are required. Correct format: http://127.0.0.1:5000/get_data
Because this inlet type can parse only a certain data model, please consider possible changes between PlantEye versions.

### Processors
Processors are designed to execute short pipelines directly in the PlantEye instance.
This might be beneficial to distribute calculations between different nodes.
For example camera node runs image acquisition and its preprocessing, while a more powerful node serves a ML model and classify image received from the first node via Rest API.
Every processor has its capability to process data of certain types.
In case the processor does not support data received from the last step, it will simply pass data further without changes.

#### input
Input processor is necessary to link further processor steps with a selected inlet(s).
Parameters:\
  list of inlets (necessary): list with names of inlet that will be passed to the further processors

#### image_resize
This processor resizes images to a given resolution by means of cv2.resize(). The image ratio is not preserved.
Parameters:\
  width (necessary): final width of the image
  height (neccesary): final height of the image
  interpolation (optional, default INTER_NEAREST): interpolation method, for more information see opencv documentation

#### image_resize
This processor crops images to a given area.
Parameters:\
  x_init (necessary): left bottom corner of the crop area
  y_init (necessary): left bottom corner of the crop area
  x_diff (necessary): width of the crop are
  y_diff (necessary): height of the crop are

#### color_conversion
This processes changes the image color map by means of cv2.cvtColor().
Parameters:\
  conversion (necessary): color transformation, please use documentation on cv2.cvtColor to get more information about possible transformations

#### tf_inference
This processor uses a specified tensorflow model to run inference.
The model should be saved as tensorflow model via model.save().
The model must be accessible locally by PlantEye and namely in .path_to_model/model_name/model_version
Parameters:\
  path_to_model (necessary): path to folder with models
  model_name (necessary): folder name of the specific model
  model_version (necessary): folder name of the specific model version

#### save_on_disk
This processor writes results on disk.
As a name for files, the current timestamp is used as a base name, which is extended with an inlet name.
Each image (acquired by data inlets or as a result from processors) is stored as a single png image in a given folder.
Other data types (values, string etc.) will be written in a single json file. This file also includes parameter, metadata etc. of images.
Parameters:\
  save_path (optional, default ../data/): common path where files will be saved

### Shells
Shell is an environment where data inlets and processors run.
They differ in terms how the end-user interact with PlantEye.

#### periodical_local
This shell type requests data from data inlets and run processors according to the given regular time basis.
Parameters:\
  time_interval (optional, default 1000): time interval for execution, in milliseconds
This shell type is recommended to use with save_on_disk processor. Thus, data will be requested and saved on disk periodically.

#### rest_api
This shell type starts a RestAPI endpoint that provides data in the form of a json response.
Parameters:\
  host (optional, default 0.0.0.0) - url of the webserver
  port (optional, default 5000) - port of the webserver
  endpoint (optional, default get_frame) - endpoint for the end-user to place get requests

Data of type image will be encoded as base64 (utf-8) to allow transfer via Rest API.

The end-user can then access data via Rest API by placing get requests.
Response example (might be outdated):
```json
{
   "camera":{
      "type":"local_camera_cv2",
      "name":"camera",
      "parameters":{
         "device_id":2,
         "Width":720,
         "ExposureTime":720
      },
      "data":{
         "name":"frame",
         "value":"frame encoded as base64",
         "type":"base64_png"
      },
      "metadata":{
         "timestamp":{
            "parameter":"timestamp",
            "value":1642344407561
         },
         "colormap":{
            "parameter":"colormap",
            "value":"BGR"
         },
         "shape":{
            "parameter":"shape",
            "value":[
               480,
               640,
               3
            ]
         },
         "010F": {
           "parameter": "010F",
           "value": "Raspberry Pi"
         }
      },
      "status":{
         "Frame capturing":{
            "code":0,
            "message":"Frame captured"
         }
      }
   },
   "light_conditions":{
      "type":"static_variable",
      "name":"light_conditions",
      "parameters":{
         "value":"natural"
      },
      "data":{
         "name":"static_value",
         "value":"natural",
         "data_type":"diverse"
      },
      "metadata":{
         "unit":{
            "parameter":"unit",
            "value":"none"
         },
         "interpretation":{
            "parameter":"interpretation",
            "value":"no artificial light switched on"
         },
         "description":{
            "parameter":"description",
            "value":"light conditions during experiment"
         }
      },
      "status":{
         
      }
   },
   "flow_regime":{
      "type":"static_variable",
      "name":"flow_regime",
      "parameters":{
         "value":0
      },
      "data":{
         "name":"static_value",
         "value":0,
         "data_type":"diverse"
      },
      "metadata":{
         "unit":{
            "parameter":"unit",
            "value":"none"
         },
         "interpretation":{
            "parameter":"interpretation",
            "value":"flooded"
         },
         "description":{
            "parameter":"description",
            "value":"flow regime in reactor"
         }
      },
      "status":{
         
      }
   },
   "stirrer_rotational_speed":{
      "type":"opcua_variable",
      "name":"stirrer_rotational_speed",
      "parameters":{
         "server":"opc.tcp://opcuademo.sterfive.com:26543",
         "username":null,
         "password":null,
         "node_ns":8,
         "node_id":"Scalar_Simulation_Float"
      },
      "data":{
         "name":"opcua_value",
         "value":-782.3922729492188,
         "data_type":"diverse"
      },
      "metadata":{
         "unit":{
            "parameter":"unit",
            "value":"none"
         },
         "interpretation":{
            "parameter":"interpretation",
            "value":"none"
         },
         "description":{
            "parameter":"description",
            "value":"a selected opcua variable"
         }
      },
      "status":{
         "Reading process value over OPC UA":{
            "code":0,
            "message":"Process value read"
         }
      }
   },
   "camera_resize":{
      "type":"image_resize",
      "name":"camera_resize",
      "parameters":{
         "width":250,
         "height":250,
         "interpolation":"INTER_NEAREST"
      },
      "data":{
         "name":"frame",
         "value":"frame encoded as base64",
         "type":"image"
      },
      "metadata":{
         
      },
      "status":{
         "Processor":{
            "code":0,
            "message":"Processing value successful"
         }
      }
   },
   "camera_resize_crop":{
      "type":"image_crop",
      "name":"camera_resize_crop",
      "parameters":{
         "x_init":2,
         "x_diff":248,
         "y_init":2,
         "y_diff":248
      },
      "data":{
         "name":"frame",
         "value":"frame encoded as base64",
         "type":"image"
      },
      "metadata":{
         
      },
      "status":{
         "Processor":{
            "code":0,
            "message":"Processing value successful"
         }
      }
   },
   "inference":{
      "type":"tf_inference",
      "name":"inference",
      "parameters":{
         "path_to_models":"../res/models/",
         "model_name":"dogs_vs_cats",
         "model_version":"1.0"
      },
      "data":{
         "name":"inference_result",
         "value":[
            1.0
         ],
         "data_type":"diverse"
      },
      "metadata":{
         
      },
      "status":{
         "Processor":{
            "code":0,
            "message":"Processing value successful"
         }
      }
   }
}
```
The response consists of a list of so-called data chunks (e.g. "camera", "light_conditions" and "flow_regimes").
Data chunks have same inner structure that consists of type, name, parameters, data, metadata and status.
type: defines the type of the data inlet.
name: denotes a unique name of the data inlet. It shadows the name of the corresponding key it belongs to.
parameters: contains parameters specified in the configuration file.
data: includes data values. The value or values are collected depending on the specified type of the data inlet.
metadata: is a structure, which contains metadata to collected value/values, e.g. unit, measurement range or resolution of the captured image.
status: contains information on data collection and processing steps.

The rest api shell also provides a possibility to update the configuration of running PlantEye dynamically.
This might be done by placing post requests with a new configuration.
The new configuration must have the same structure as the configuration file (except the shell part), but encoded in the json format.
Please take into account that the current configuration will be replaced completely and only if the new configuration is valid. 
