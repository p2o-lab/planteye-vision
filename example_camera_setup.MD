# vkhaydarov-planteye-vision setup
This documents describes simple usage scenarios of PlantEye.

## Saving file locally
Required components: PlantEye/Vision, PlantEye/Wolverine.

* Install PlantEye/Vision by means of cloning corresponding GitHub repository and installing requirements on an edge node which the capturing device connected to.
* Adjust the PlantEye/Vision configuration file according to your setup.
* Run PlantEye/Vision. You can check whether PlantEye/Vision works properly by opening a webpage:
```bash
localhost:5000/get_frame
```
where localhost and 5000 are api/url and api/port from the configuration

* Install PlantEye/Wolverine by means of cloning corresponding GitHub repository and installing requirements on an edge node which the capturing device connected to.
* Adjust the PlantEye/Wolverine configuration file according to your setup.
* Run PlantEye/Wolverine.

Now Plant/Wolverine must begin creating a pair of files with png images and json metadata files with a given time interval.

Tip: in case you run both components on one edge node, you can use localhost as api url for both configurations within PlantEye/Vision and PlantEye/Wolverine

  
