# Theia Technologies lens IQ(TM)
[Theia Technologies](https://www.theiatech.com) offers a [MCR600 motor control board](https://www.theiatech.com/lenses/accessories/mcr/) for interfacing with Theia's motorized lenses.  This board controls focus, zoom, iris, and IRC filter motors.  It can be connected to a host computer by USB, UART, or I2C connection.  This lensIQ module allows the user to easily convert from engineering units (meters, degrees) to motor steps applicable to Theia's motorized lenses.  For sending these motor steps to the control board via the virtual com port, install the additional package TheiaMCR ([TheiaMCR on Github](https://github.com/cliquot22/TheiaMCR))

# Features
<img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/python/python-original.svg" alt="python" width="20" height="20"/> Engineering units can be converted to motor steps and vice versa.  The calculations use the design data for the lens but it is possible to load a specific lens calibration data file as well.  Some conversion examples are: 
- field of view to zoom motor steps
- object distance to focus motor steps
- zoom motor steps to focal length
- F/# or numeric aperture value to iris steps
- calculate depth of field at the focal length and object distance
And there are other calculations as well.  Refer to the [wiki](https://github.com/cliquot22/lensIQ/wiki) page for more detailed descriptions of the functions.  

# Quick start
The software module can be loaded into Python using pip:  
`pip install lensIQ`  
Once installed, it is required to initialize the class before using any functions.  This is done by importing and then loading the default lens data.  
``` 
import lensIQ

def app():
    # initialize lensIQ
    IQ = lensIQ.lensIQ()

    # read the default lens data
    success = lensIQ.loadDataFile(JSON_formatted_data)
```   
After initializing it is possible to use the functions to convert from engineering units to motor steps and back.  The zoom motor step can be calculated from a requested focal length.  And the focus motor step can be calcualted from a requested object distance at that set focal length.  
``` 
    # calculate zoom step for focal length 15mm
    FL = 15
    zoomStep, err = IQ.FL2ZoomStep(FL)

    # calculate the best focus step for zoom 15mm and 10m object distance
    objectDist = 10
    focusStep, err = IQ.OD2FocusStep(objectDist, zoomStep)
```   

# Class variables and constants
There are constants for error/results values returned from the functions.  More can be found on the [wiki](https://github.com/cliquot22/lensIQ/wiki) page.  

The `engValues` variable is where the results of calculations and motor step positions are stored.  It is a list with format:  
``` 
        {
            'tsLatest': (timestamp value), 
            (type): 
            {
                'value': (number), 
                'min': (number), 
                'max': (number), 
                'ts': (timestamp)
            }
        }
```  
- 'tsLatest' is the integer id for the latest update after a calculation set.  Each configuration (see below) of the lens has a local 'ts' that can be compared to see if the configuration is potentially out of date.  The 'ts' value for the engineering type ('FOV', 'AOV', etc) should be equal or greater than the zoom, focus, or iris ('irisStep' etc) motor 'ts' value depending on which of these three motor step positions affect the engineering value.  
- 'type' includes ['AOV', 'FOV', 'DOF', 'FL', 'OD', 'FNum', 'NA', 'zoomStep', 'focusStep', 'irisStep'].  Each type has 'value', 'min', 'max', and 'ts'.  'min' and 'max' may not always make sense (zoomStep for instance).  
- Object distance type 'OD' can be string value 'NA (near)' or 'NA (far)' as well as float value of the set object distance. 
- Depth of field type 'DOFMin' and 'DOFMax' are the minimum and maximum object distances that are in the depth of field. 
- Types 'zoomStep', 'focusStep', and 'irisStep' are the current motor step positions.  These are used for the engineering unit calculations.  

# Logging
There are logging commands in the module using Python's logging libray.  These are set by default to log WARNING and higher levels.  To see other log prints, initialize the class with `IQ = lensIQ.lensIQ(degubLog=True)` or manually set the logging level with `lensIQ.log.setLevel(logging.INFO)`.  

# Camera back focal length calibration
Due to tolerances in the lens mount surface to image sensor (the back focal length or BFL), the focus step needs to be adjusted for the exact camera being used.  This module includes functions to set this BFL calibration.  See Theia's application note [AN004](https://www.theiatech.com/lenses/calibrated-lenses/) for more information on this procedure.  

Functions that set or get the focus motor position will used this BFL correction value.  Once the BFL correction curve is calculated the function `BFLCorrection(self, FL:float, OD:float=1000000) -> int` will calculate the focus step adjustment for any focal length.  This is then passed to the function that sets or gets the focus motor position.  

# License
Theia Technologies proprietary license
Copyright 2023-2025 Theia Technologies

# Contact information
For more information contact: 
Mark Peterson at Theia Technologies
[mpeterson@theiatech.com](mailto://mpeterson@theiatech.com)

# Revision
v.1.6.0