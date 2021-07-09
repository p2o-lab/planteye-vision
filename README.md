# vkhaydarov-planteye-vision

PlantEye/Vision is a tool for image data collection that acquires data from a camera, combines it with metadata, and provides it via REST API interface for further usage.
Further usage might include saving files locally (i.e. via PlantEye/Wolverine) or ingest them directly onto Dataverse cloud (by means of PlantEye/Wanda).

## Usage
To run the script be sure that config-file (config.yaml) is proper and then run the script:
```bash
python3 main.py
```

## Description of REST API interface
### Get frame
This request captures a single frame and returns json data with string encoded frame, metadata and labels.

URL:
/get_frame

Method:
GET

URL Params:
No parameters needed

Success Response:
Code: 200
Content:
{
    "frame": {
        "colorspace": "BGR", "frame": "frame encoded as string", "frame_shape": [2000, 2500, 3]
            },
    "labels": {
        "flow_regime": {"description": "flooded", "value": 0}
            },
    "metadata": {
        "exif": {"010F": "Raspberry Pi"},
        "tags": {"light_condition": {"unit": "-", "value": "natural"}, "stirrer_rotational_speed": {"unit": "rpm", "value": 100}
        }
    },
    "status": {"code": 200, "message": "frame captured"},
    "timestamp": 1625820453946
}

## Configure
Create a config file (config.yaml) according to the following structure:
```yaml
capturing_device:
  type: local_camera_cv2
  connection:
    device_id: 0
  parameters:
    CAP_PROP_FRAME_HEIGHT: 1280
    CAP_PROP_FRAME_WIDTH: 720
    CAP_PROP_FPS: 30
api:
  url: localhost
  port: 5000
metadata:
  'exif':
    '010F': Raspberry Pi # Manufacturer of recording equipment
    '0110': HQ Camera v1.1 # The model name or model number of the equipment
...
  'tags':
    'light_condition':
      'value': 'natural'
      'unit': '-'
...
'labels':
  'flow_regime':
    'value': 0
    'description': 'flooded'
...
```
Further metadata, tags and labels can be added.

## Requirements
To install requirements use the following command:
```bash
pip3 install -r requirements.txt
```

## License
Valentin Khaydarov (valentin.khaydarov@tu-dresden.de)\
Process-To-Order-Lab\
TU Dresden