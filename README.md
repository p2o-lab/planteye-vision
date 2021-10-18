# PlantEye/Vision

PlantEye/Vision is a tool for image data collection that acquires data from a camera, combines it with metadata, and provides it via REST API interface for further usage.
Further usage might include saving files locally (i.e. via PlantEye/Wolverine) or ingest them directly onto Dataverse cloud (by means of PlantEye/Wanda).

## Usage
To run the script be sure that config-file (config.yaml) is proper and then run the script:
```bash
python3 vision.py
```

## Description of REST API interface
### Get frame
This request captures a single frame and returns json data with string encoded frame, metadata and labels.

URL:
```html
/get_frame
```
The endpoint can be changed in the conifuguration file.

Method:
GET

URL Params:
No parameters needed

Response:
```json
{
  "frame": {
    "frame": "frame_serialised_as_string",
    "frame_shape": [
      480,
      640,
      3
    ],
    "frame_colormap": "BGR"
  },
  "data_source": {
    "configuration": {
      "type": "local_camera_cv2",
      "connection": {
        "device_id": 1
      },
      "parameters": {
        "Width": 720,
        "ExposureTime": 720
      }
    },
    "parameters": {},
    "details": {
      "id": 1,
      "model_name": "Generic OpenCV camera",
      "serial_number": "no data",
      "vendor_name": "no data"
    }
  },
  "metadata": {
    "exif": {
      "8827": 100,
      "9201": "1/8000"
    },
    "tags": {
      "light_condition": {
        "source": "static",
        "value": "natural",
        "unit": "-"
      },
      "stirrer_rotational_speed": {
        "source": "opcua",
        "access_data": {
          "server": "opc.tcp://opcuademo.sterfive.com:26543",
          "username": null,
          "password": null,
          "node_ns": 8,
          "node_id": "Scalar_Simulation_Float"
        },
        "unit": "rpm",
        "value": -275.49285888671875
      },
      "flow_regime": {
        "source": "static",
        "value": 0,
        "description": "flooded"
      }
    }
  },
  "status": {
    "frame_capturing": {
      "code": 200,
      "message": "Frame captured"
    },
    "frame_conversion_to_str": {
      "code": 200,
      "message": "Conversion frame to str successful"
    },
    "metadata_collection": {
      "code": 200,
      "message": "Metadata extraction/polling successful"
    }
  }
}
```

## Configure
Create a config file (config.yaml) according to the following structure:
```yaml
data_source:
  type: local_camera_cv2
  connection:
    device_id: 0
  parameters:
    CAP_PROP_FRAME_HEIGHT: 1280
    CAP_PROP_FRAME_WIDTH: 720
    CAP_PROP_FPS: 30
data_sink:
  name: PlantEye/Vision
  endpoint: /get_frame
  url: localhost
  port: 5000
metadata:
  'exif':
    '010F': Raspberry Pi # Manufacturer of recording equipment
    '0110': HQ Camera v1.1 # The model name or model number of the equipment
...
  'tags':
    'light_condition':
      'source': static
      'value': 'natural'
      'unit': '-'
    'stirrer_rotational_speed':
      'source': opcua
      'access_data':
        'server': 'opc.tcp://10.6.51.23:4840'
        'username': admin
        'password': wago
        'node_ns': 8
        'node_id': Scalar_Simulation_Float
      'unit': rpm
...
      'flow_regime':
        'source': static
        'value': 0
        'description': 'flooded'
...
```
Further metadata, tags and labels can be added.

### Supported data sources types
Use value "local_camera_cv2" in the field capturing_device.type for a local camera, e.g. USB or built-in camera.
In this case the package opencv will be used to capture the frame.

Use value "baumer_camera_neoapi" to connect to a Baumer camera via neoAPI.

### Metadata and labels
There are two possible sources of metadata and labels: static value from the configuration file and opc ua server.
The source 'static' is used to provide a constant value.

The source 'opcua' provides functionality to poll the process value directly from the given opc ua server.
The poll routine is executed every time the request '/get_frame' incomes.

In case the opc ua server does not require username and password, please leave corresponding fields empty.

## Requirements
To install requirements use the following command:
```bash
pip3 install -r requirements.txt
```
To be able to use Baumer cameras, neoAPI is required. neoAPI is to install via pip
```bash
pip3 install wheel_file.whl
```
Please find information on how to get neoAPI on the official webpage of Baumer.

## License
Valentin Khaydarov (valentin.khaydarov@tu-dresden.de)\
Process-To-Order-Lab (https://tu-dresden.de/ing/forschung/bereichs-labs/P2O-Lab)\
TU Dresden\
