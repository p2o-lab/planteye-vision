# vkhaydarov-planteye-vision

PlantEye/Vision is a tool for image data collection that acquires data from a camera, combines it with metadata, and provides it via REST API interface for further usage.
Further usage might include saving files locally (i.e. via PlantEye/Wolverine) or ingest them directly onto Dataverse cloud (by means of PlantEye/Wanda).

## Usage
To run the script be sure that config-file (config.yaml) is proper and then run the script:
```bash
python3 main.py
```

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
  '010F': RaspPi # Manufacturer of recording equipment
  '0110': HQ Camera v1.1 # The model name or model number of the equipment
  'A432': 6mm f/1.2 # Lens specification.
  'A433': RPIZ # Lens manufacturer.
  'A434': PT361060M3MP12 # Lens model. 
  '013B': P2O-Lab # This tag records the name of the camera owner, photographer or image creator.
  '0131': PlantEye/Vision, 1.0.0 # This tag records the name and version of the software.
  '9208': Vessel light, 2.5 W # The kind of light source.
  '9206': 0.03 # The distance to the subject, given in meters.
  '0140': HSV  # A color map for palette color images. 
  '0112': 1 # The image orientation
  '829D': 1.2 # The F number.
  '8827': 100 # This tag indicates the ISO speed value of a camera or input device that is defined in ISO 12232. 
  '9201': 1/8000 # Shutter speed.
  '9202': 1.2 # The lens aperture.
  '9203': 50 # The value of brightness.
  '920A': 6 # The actual focal length of the lens, in mm.
  'A407': 1.0 # Image gain adjustment.
  'A408': 0 # Contrast.
  'A409': 0 # Saturation.
  'A40A': 0 # Sharpness.
  'Beleuchtung': 'natural'

```
Further nodeIds can be added in the section with Metrics.
In order to generate conform config-files for Process Equipment Assemblies based on MTP-files, please use https://github.com/vkhaydarov/planteye-mtp2cfg.

## Requirements
To install requirements use the following command:
```bash
pip3 install -r requirements.txt
```

## License
Valentin Khaydarov (valentin.khaydarov@tu-dresden.de)\
Process-To-Order-Lab\
TU Dresden