# PlantEye/Vision

PlantEye/Vision is a tool for data collection and processing.\
Shortly, PlantEye/Vision requests data from different data sources (data inlets) that are given in the configuration file.\
If any processor specified, then additional processed data will be generated.\
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
---
inlets:
  1:
    name: camera
    type: local_camera_cv2 #baumer_camera_neoapi
    hidden: False
    parameters:
      device_id: 0
      Width: 720
      ExposureTime: 720
    metadata:
      '010F': Raspberry Pi # Manufacturer of recording equipment
  2:
    name: light_conditions
    type: static_variable
    hidden: False
    parameters:
      value: natural
    metadata:
      unit: none
      interpretation: no artificial light switched on
      description: light conditions during experiment
  3:
    name: flow_regime
    type: static_variable
    hidden: False
    parameters:
      value: 0
    metadata:
      unit: none
      interpretation: flooded
      description: flow regime in reactor
  4:
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

### Supported processor types
Processors are design to execute short pipelines that include data preprocessing and model inference.
Please consider that each processor except input generates a data/status/metadata chunk that will be a part of the data saved locally or provided via Rest API.
#### input
Input processor is necessary to link further processor steps with a selected inlet.
Input inlet as parameters might contain one or more inputs.
But only compatible ones will be processed with processors.
Incompatible ones will be passed further unchanged.
#### image_resize
Resize processes is made to resize images.
#### image_crop
Resize processes crops images.
#### color_conversion
Convert color map of the image, as parameter it requires conversion type as in the opencv function cv2.cvtColor().
#### tf_inference
This processor uses a specified tensorflow model to run inference.
#### save_on_disk
This process saves results on disk.

### Supported shell types
#### periodical_local
This shell type requests data from data inlets and processes them according to a given regular time basis.

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
Data chunks have the same inner structure consisting of type, name, parameters, data, metadata and status.

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
