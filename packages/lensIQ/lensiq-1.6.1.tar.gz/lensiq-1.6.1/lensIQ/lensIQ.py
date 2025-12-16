# Theia IQ Smart lens calculations and motor control functions
# (c)2023-2024 Theia Technologies

import numpy.polynomial.polynomial as nppp
import numpy as np
from scipy import optimize
import logging
import json

# create a logger instance for this module
log = logging.getLogger(__name__)
log.setLevel(logging.WARNING)
log.addHandler(logging.NullHandler())

# These functions are ease of use functions for setting and getting motor step positions
# and relating them to engineering units.
# Initialize the class to access the variables.  Then call the loadData function to add the calibration data
# for use in all the calculations
class lensIQ():
    DEFAULT_SPEED = 1000                # default motor (focus/zoom) speed
    DEFAULT_REL_STEP = 1000             # default number of relative steps
    DEFAULT_SPEED_IRIS = 100            # default iris motor speed
    DEFAULT_IRIS_STEP = 10              # default number of iris relative steps
    INFINITY = 1000                     # [m] infinite object distance
    OD_MIN_DEFAULT = 2                  # default minimum object distance is not specified in the calibration data file
    COC = 0.020                         # circle of confusion for DoF calcualtion

    # error list
    OK = 'OK'
    ERR_NO_CAL = 'no cal data'          # no calibration data loaded
    ERR_FL_MIN = 'FL min'               # minimum focal length exceeded
    ERR_FL_MAX = 'FL max'               # maximum focal length exceeded
    ERR_OD_MIN = 'OD min'               # minimum object distance exceeded
    ERR_OD_MAX = 'OD max'               # maximum object distance (1000 (infinity)) exceeded
    ERR_OD_VALUE = 'OD value'           # OD not specified
    ERR_NA_MIN = 'NA min'               # minimum numerical aperture exceeded
    ERR_NA_MAX = 'NA max'               # maximum numerical aperture exceeded
    ERR_RANGE_MIN = 'out of range-min'  # out of allowable range
    ERR_RANGE_MAX = 'out of range-max'  # out of allowable range
    ERR_CALC = 'calculation error'      # calculation error (infinity or divide by zero or other)
    ERR_NAN = 'string value'            # string value returned when number value is expected
    WARN_VALUE = 'value warning'        # warning if value seems extreme, possible unit conversion issue

    ### setup functions ###
    def __init__(self, debugLog:bool=False):
        '''
        Theia lens IQ calculations and motor control functions.  These functions allow ease of use when converting
        from engineering units (meters, degrees, etc.) to motor step positions and back.  After initializing the 
        class, call loadData to add any calibrated lens data.  

        ### input
        - debugLog (optional boolean: False): Set true to turn on the debug logging stream
        ### class variables 
        - COC (optional: 0.020): circle of confusion for calculating depth of field (in mm)
        - sensorWd (optional: read from default data): image sensor width (in mm)
        - engValues: 
        {
            'tsLatest': (timestamp value), 
            (config): 
            {
                'value': (number), 
                'min': (number), 
                'max': (number), 
                'ts': (timestamp)
            }
        }
            - 'tsLatest' is the id for the latest update after a calculation set.  Each configuation ('config') of the lens has a local 'ts' that can be compared 
            to see if the configuration is potentially out of date.  The 'ts' value for the engineering units ('FOV', 'AOV', etc) should be equal or greater than the zoom, 
            focus, or iris ('irisStep' etc) motor 'ts' value depending on which of these three motor step positions affect the engineering value.  
            - 'config' includes ['AOV', 'FOV', 'DOF', 'FL', 'OD', 'FNum', 'NA', 'zoomStep', 'focusStep', 'irisStep'].  Each configuration value has 'value', 'min', 
            'max', and 'ts'.  'min' and 'max' may not always make sense (zoomStep for instance).  
            - Configuration 'OD' can be string error 'NA (near)' or 'NA (far)' as well as float value of the set object distance. 
            - Configurations 'DOFMin' and 'DOFMax' are the minimum and maximum object distances that are in the depth of field. 
            - Configurations 'zoomStep', 'focusStep', and 'irisStep' are the current motor step positions.  These are used for the engineering unit calcuations.  
        - BFLCorrectionValues: the difference between best measured focus and predicted focus.  Values are stored in [FL, difference, OD]
        - BFLCorrectionCoeffs: the quadratic coefficients for the BFL correction.  This curve is teh difference between the best measured
        and predicted focus values.  
        ### class constants
        These are possible return values and note values.  
        - OK = 'OK'
        - ERR_NO_CAL = 'no cal data'          # no calibration data loaded
        - ERR_FL_MIN = 'FL min'               # minimum focal length exceeded
        - ERR_FL_MAX = 'FL max'               # maximum focal length exceeded
        - ERR_OD_MIN = 'OD min'               # minimum object distance exceeded
        - ERR_OD_MAX = 'OD max'               # maximum object distance (1000 (infinity)) exceeded
        - ERR_OD_VALUE = 'OD value'           # OD not specified
        - ERR_NA_MIN = 'NA min'               # minimum numerical aperture exceeded
        - ERR_NA_MAX = 'NA max'               # maximum numerical aperture exceeded
        - ERR_RANGE_MIN = 'out of range-min'  # out of allowable range
        - ERR_RANGE_MAX = 'out of range-max'  # out of allowable range
        - ERR_CALC = 'calculation error'      # calculation error (infinity or divide by zero or other)
        - WARN_VALUE = 'value warning'        # warning if value seems extreme, possible unit conversion issue
        - ERR_NAN = 'string value'       # string value returned when number value is expected

        (c)2023 Theia Technologies
        www.TheiaTech.com
        '''
        if debugLog:
            log.setLevel(logging.DEBUG)
        else:
            log.setLevel(logging.WARNING)

        self.calData = {}
        self.COC = lensIQ.COC
        self.sensorWd = 0
        self.sensorRatio = 0.8

        # back focal length correction values
        self.BFLCorrectionValues = []
        self.BFLCorrectionCoeffs = []

        # store the lens configuration
        # tsLatest is the id for the latest update after a calculation set.  Each configuation of the lens
        # has a local 'ts' that can be compared to see if the configuration is potentially out of date.  The ts value
        # for the engineering units should be equal or greater than the zoom, focus, or iris motor ts value depenging
        # on which of these three affect the engineering value.  
        # Configuration includes ['AOV', 'FOV', 'DOF', 'FL', 'OD', 'FNum', 'NA', 'zoomStep', 'focusStep', 'irisStep']
        # which has 'value', 'min', 'max', and 'ts'.  'min' and 'max' may not always make sense (zoomStep for instance).  
        # 'OD' can be string error 'NA (near)' or 'NA (far)' as well as float value. 
        # DOFMin and DOFMax are the min and max object distances that are in the depth of field. 
        # Also, the current motor steps are stored.  These are used for the calcuations.  
        self.engValues = {'tsLatest': 0}
        for f in ['AOV', 'FOV', 'DOF', 'FL', 'OD', 'FNum', 'NA', 'zoomStep', 'focusStep', 'irisStep']:
            self.engValues[f] = {'value':0, 'min':0, 'max':0, 'ts':0}
        self.engValues['OD']['min'] = self.OD_MIN_DEFAULT
        self.engValues['OD']['max'] = self.INFINITY
        log.info('lensIQ class initilized')
    
    # load and validate a calibration data file
    def loadDataFile(self, fileName:str):
        '''
        Read the file contents and validate that the manufacturer key is present and is "Theia Technologies".
        ### input:
        - fileName: the path and name of the JSON data file to read
        ### return
        ['OK' | 'no cal data']
        '''
        MANUF_NAME_KEY = "manufName"  # the key in the JSON file with manufacturer's name
        MANUF_NAME = "Theia Technologies"  # manufacturer name for JSON file validation
        with open(fileName, "r") as f:
            data = json.load(f)

        if MANUF_NAME_KEY not in data:
            log.warning(f'"{MANUF_NAME_KEY}" no found in JSON calibration datafile')
            return lensIQ.ERR_NO_CAL

        if (data[MANUF_NAME_KEY] != MANUF_NAME):
            log.warning(f'JSON calibration datafile formatting isn\'t garanteed becuase manufacturer is not {MANUF_NAME}')
            return lensIQ.ERR_NO_CAL

        err = self.loadData(data)
        return err

    # load the calibration data
    def loadData(self, calData) -> str:
        '''
        Validate that the calibration data set is okay.  This function also updates the 
        maximum focus and zoom steps in 'engValues' and the 'sensorWd' class variable.  
        The input parameter is the json data which can be read from a file with: 

        with open(fname, 'r') as f:
            data = json.load(f)

        ### input
        - calData: the calibration data set (loaded from default data or calibrated data)
        ### return
        ['OK' | 'no cal data']
        '''
        self.calData = calData
        if calData == {}:
            log.warning('Calibration data formatting error')
            return lensIQ.ERR_NO_CAL
        
        # save initial step values
        self.engValues['zoomStep']['value'] = calData['zoomPI']
        self.engValues['focusStep']['value'] = calData['focusPI']
        self.sensorWd = self.sensorRatio * calData['ihMax']
        log.info('Calibration datafile loaded')
        return lensIQ.OK

    # load a circle of confusion value 
    def loadCOC(self, COC) -> str:
        '''
        Load a circle of confusion value to overwrite the default 0.020mm.
        A value outside the reasonable range can be set.  The function will return a warning but not prevent it.
        ### input
        - COC: the circle of confusion (in mm)
        ### return
        ['OK' | 'value warning']
        '''
        self.COC = COC
        # check for validity, expecting a value between extremes 0.005mm and 0.100mm
        if COC < 0.005 or COC > 0.100:
            return lensIQ.WARN_VALUE
        return lensIQ.OK
    
    # load a custom sensor width
    def loadSensorWidth(self, width:float, ratio:float=0) -> str:
        '''
        Load the sensor width.  
        If only one parameter is sent to the function it will be the sensor width (in mm).  
        If 2 parameters are sent, the first will be the sensor diagonal (in mm) and the second the width to diagonal ratio.  
        By default, the ratio is 0.8 for a 4x3 sensor.  
        ### input
        - width: sensor width or diagonal (in mm)
        - ratio: (optional): the width to diagonal ratio
        ### return
        ['OK' | ']
        '''
        if isinstance(width, str):
            try:
                float(width)
            except:
                # do not update sensor width value
                return lensIQ.ERR_NAN
        width = float(width)
        if ratio == 0:
            # first parameter is sensor width
            self.sensorWd = width
        else:
            # first parameter is the sensor diagonal
            self.sensorRatio = ratio
            self.sensorWd = width * self.sensorRatio
        return lensIQ.OK

    # Clear engineering values
    def clearEngValues(self):        
        self.engValues['tsLatest'] += 1
        ts = self.engValues['tsLatest']
        for f in ['AOV', 'FOV', 'DOF', 'FL', 'OD', 'FNum', 'NA', 'zoomStep', 'focusStep', 'irisStep']:
            self.engValues[f] = {'value':0, 'min':0, 'max':0, 'ts':ts}
        self.engValues['OD']['min'] = self.OD_MIN_DEFAULT
        self.engValues['OD']['max'] = self.INFINITY


    ### ----------------------------------------------- ###
    ### convert motor step numbers to engineering units ###
    ### ----------------------------------------------- ###

    # calculate the focal length from zoom step
    def zoomStep2FL(self, zoomStep:int) -> tuple[float, str, float, float]:
        '''
        Calculate the focal length from zoom step number. 
        If the calculated focal length is outside the min/max range the value may not be accurate due to curve
        fitting extrapolation.  The returned note string will indicate min/max limits are exceeded.
        'FLMin' and 'FLMax' are read from the calibration data file or default calibration data.  They are not calculated.
        ### input
        - zoomStep: zoom motor step number
        ### return
        [calculated focal length, note, FL Min, FL Max]
        'note' string value can be: ['OK', 'no cal data', 'FL min', 'FL max']
        '''
        if 'FL' not in self.calData.keys(): return 0, lensIQ.ERR_NO_CAL, 0, 0

        # extract the inverse polynomial coefficients
        coef = self.calData['FL']['coefInv'][0]

        # calculate the result
        FL = nppp.polyval(zoomStep, coef)

        # validate the response
        err = lensIQ.OK
        flMin = self.calData['flMin']
        flMax = self.calData['flMax']
        if (FL < flMin):
            err = lensIQ.ERR_FL_MIN
        elif (FL > flMax):
            err = lensIQ.ERR_FL_MAX
        
        # save the results
        self._updateEngValues('FL', FL, flMin, flMax)
        log.info(f'Zoom step {zoomStep} -> FL {FL:0.2f}')
        return FL, err, flMin, flMax

    # calculate the object distance from the focus step
    def focusStep2OD(self, focusStep:int, zoomStep:int, BFL:int=0) -> tuple[float, str, float, float]:
        '''
        Calculate the object distance from the focus step.  
        If the calculated OD is not close to the nomial range, return out of bounds errors or else
        calculate the value and validate for out of bounds errors (this method should avoid curve fitting anomnolies)
        if the min/max limits are exceeded the OD reported may not be accurate.  The returned note string will
        indicate a min/max OD exceeded error.
        'ODmin' is read from the calibration data file or default calibration data.  It is not calculated.
        ### input
        - focusStep: focus motor step number
        - zoomStep: zoom motor step number
        - BFL (optional: 0): back focus correction in focus steps
        ### return
        [calculated object distance, note, OD min, OD max]
        'note' string value can be: ['OK', 'no cal data', 'OD min', 'OD max']
        '''
        if 'tracking' not in self.calData.keys(): return 0, lensIQ.ERR_NO_CAL, 0, 0
        # calculation range limit constants, don't calculate outside these limits to avoid curve fitting wrap-around
        DONT_CALC_MAX_OVER = 100
        DONT_CALC_MIN_UNDER = 400

        # extract the polynomial coefficients
        cp1List = self.calData['tracking']['cp1']
        coefList = self.calData['tracking']['coef']

        # calculate the focus step at different object distances for the zoom step
        # add the BFL correction factor
        focusStepList = []
        for cp1, _val in enumerate(cp1List):
            focusStepList.append(nppp.polyval(zoomStep, coefList[cp1]) + BFL)

        # validate the focus step to make sure it is within the valid focus range
        err = lensIQ.OK
        OD = 0
        ODMin = self.calData['odMin'] if 'odMin' in self.calData.keys() else lensIQ.OD_MIN_DEFAULT
        ODMax = self.calData['odMax'] if 'odMax' in self.calData.keys() else lensIQ.INFINITY

        #   range goes from infinity focus [0] to minimum focus [len(cp1)]
        if focusStep > focusStepList[0] + DONT_CALC_MAX_OVER:
            # likely outside valid focus range
            err = lensIQ.ERR_OD_MAX
            OD = 'NA (far)'
        elif focusStep < focusStepList[-1] - DONT_CALC_MIN_UNDER:
            # likely outside valid focus range
            err = lensIQ.ERR_OD_MIN
            OD = 'NA (near)'
        else:
            # fit the focusStepList/cp1List to find the object distance
            coef = nppp.polyfit(focusStepList, cp1List, 3)
            OD = 1000 / nppp.polyval(focusStep, coef)
            # validate OD
            if OD < 0:
                # points >infinity are calculaed as negative
                err = lensIQ.ERR_OD_MAX
                OD = self.INFINITY
            elif OD < ODMin:
                err = lensIQ.ERR_OD_MIN

        # save the results
        self._updateEngValues('OD', OD, ODMin, ODMax)
        log.info(f'Focus step {focusStep} -> OD {OD}')
        return OD, err, ODMin, ODMax

    # calculate the numeric aperture from iris motor step
    def irisStep2NA(self, irisStep:int, FL:float, rangeLimit:bool=True) -> tuple[float, str, float, float]:
        '''
        Calculate the numeric aperture from iris motor step. 
        If the calculated numeric aperture (NA) is outside the range, return the calculated value but set the note error 
        to indicate min/max exceeded. 
        ### input
        - irisStep: iris motor step number
        - FL: focal length
        - rangeLimit (optional: True): limit the calcuated value to the range
        ### return
        [NA, note, NAMin, NAMax]
        'note' string value can be: ['OK', 'no cal data', 'NA max', 'NA min']
        '''
        if 'AP' not in self.calData.keys(): return 0, lensIQ.ERR_NO_CAL, 0, 0

        # extract data from calibration data file
        NA = self._interpolate(self.calData['AP']['coef'], self.calData['AP']['cp1'], FL, irisStep)

        # calculate min/max values
        NAMin = self._interpolate(self.calData['AP']['coef'], self.calData['AP']['cp1'], FL, self.calData['irisSteps'])
        NAMax = self._interpolate(self.calData['AP']['coef'], self.calData['AP']['cp1'], FL, 0)

        # validate the results
        NAMaxCal = (1/(2 * self.calData['fnum']))

        # set the maximum NA to lesser of calculated value from the curve or calibration data value from the file
        NAMax = min(NAMax, NAMaxCal)
        NAMin = max(NAMin, 0.01)
        err = lensIQ.OK
        if NA > NAMax:
            err = lensIQ.ERR_NA_MAX
            if rangeLimit: NA = NAMax
        elif NA < NAMin:
            err = lensIQ.ERR_NA_MIN
            if rangeLimit: NA = NAMin

        # save the results
        self._updateEngValues('NA', NA, NAMin, NAMax)
        log.info(f'Iris step {irisStep} -> NA {NA:0.3f}')
        return NA, err, NAMin, NAMax

    # calculate the F/# from the iris motor step
    def irisStep2FNum(self, irisStep:int, FL:float, returnNA:bool=False) -> tuple[float, str, float, float]:
        '''
        Calculate the F/# from the iris motor step.  
        Calculations are propogated using numeric aperture to avoid division by zero so this 
        function calculates NA first and inverts the results. 
        ### input
        - irisStep: iris motor step number
        - FL: focal length
        ### return
        [FNum, note, FNumMin, FNumMax]
        'note' string value can be: ['OK', 'no cal data', 'NA max', 'NA min']
        '''
        if 'AP' not in self.calData.keys(): return 0, lensIQ.ERR_NO_CAL, 0, 0
        NA, err, NAMin, NAMax = self.irisStep2NA(irisStep, FL)
        fNum = self._NA2FNum(NA)
        fNumMin = self._NA2FNum(NAMin)
        fNumMax = self._NA2FNum(NAMax)

        # save the results
        self._updateEngValues('FNum', fNum, fNumMin, fNumMax)
        log.info(f'Iris step {irisStep} -> F/# {fNum:0.2f}')
        return fNum, err, fNumMin, fNumMax


    ### ----------------------------------------------- ###
    ### convert engineering units to motor step numbers ###
    ### ----------------------------------------------- ###

    # calculate the zoom step from the focal length
    def FL2ZoomStep(self, FL:float) -> tuple[int, str]:
        '''
        Calculate the zoom step from the focal length. 
        Keep the zoom step in the available range.
        ### input
        - FL: focal length
        ### return
        [zoomStep, note]
        'note' string value can be: ['OK' | 'no cal data' | 'out of range-min' | 'out of range-max']
        '''
        if 'FL' not in self.calData.keys(): return 0, lensIQ.ERR_NO_CAL
        err = lensIQ.OK

        # validate input value
        zoomStepMax = self.calData['zoomSteps']
        FLTolerance = 2     # tolerance beyond FL range
        if FL < self.calData['flMin'] - FLTolerance:
            err = lensIQ.ERR_RANGE_MIN
            zoomStep = zoomStepMax
        elif FL > self.calData['flMax'] + FLTolerance:
            err = lensIQ.ERR_RANGE_MAX
            zoomStep = 0
        else:
            # extract the polynomial coefficients
            coef = self.calData['FL']['coef'][0]

            # calculate the result
            zoomStep = int(nppp.polyval(FL, coef))

        # validate the response
        if (zoomStep < 0):
            err = lensIQ.ERR_RANGE_MIN
            zoomStep = 0
        elif (zoomStep > zoomStepMax):
            err = lensIQ.ERR_RANGE_MAX
            zoomStep = zoomStepMax

        # save the results
        self._updateEngValues('zoomStep', zoomStep)
        log.info(f'FL {FL:0.2f} -> zoom step {zoomStep}')
        return zoomStep, err

    # calculate focus motor step from object distance and zoom step
    def zoomStep2FocusStep(self, zoomStep:int, OD:float, BFL:int=0) -> tuple[int, str]:
        '''
        Calculate focus motor step from object distance and zoom step. 
        The focus motor step number will be limited to the available range.
        Maximum object distance input can be 1000m (infinity).  Minimum object distance
        can be 0 but focus motor step may not support this minimum.  Also, the focus/zoom
        calculation can cause fitting errors outside the acceptable range.
        ### input
        - zoomStep: current zoom motor step position
        - OD: object distance
        - BFL (optional: 0): back focus step adjustment
        ### return
        [focusStep, note]
        'note' string value can be: ['OK' | 'no cal data' | 'out of range-min' | 'out of range-max' | 'no OD set' | 'not a number']
        '''
        focusStep, err = self.OD2FocusStep(OD, zoomStep, BFL)
        return focusStep, err
    
    # calculate focus motor step from object distance and zoom step (alternate)
    def OD2FocusStep(self, OD:float, zoomStep:int, BFL:int=0) -> tuple[int, str]:
        '''
        Calculate focus motor step from object distance and zoom step. 
        The focus motor step number will be limited to the available range.
        Maximum object distance input can be 1000m (infinity).  Minimum object distance
        can be 0 but focus motor step may not support this minimum.  Also, the focus/zoom
        calculation can cause fitting errors outside the acceptable range.
        ### input
        - OD: object distance in meters
        - zoomStep: current zoom motor step position
        - BFL (optional: 0): back focus step adjustment
        ### return
        [focusStep, note]
        'note' string value can be: ['OK' | 'no cal data' | 'out of range-min' | 'out of range-max' | 'no OD set' | 'not a number']
        '''
        if 'tracking' not in self.calData.keys(): return 0, lensIQ.ERR_NO_CAL
        try:
            float(OD)
        except:
            # OD is not a number
            log.info(f'OD is not a number ({OD})')
            return None, lensIQ.ERR_NAN

        # extract the focus/zoom tracking polynomial data and interpolate to OD
        if OD == 0:
            # OD not set
            log.info('OD is not set')
            return 0, lensIQ.ERR_OD_VALUE
        invOD = 1000 / OD
        focusStep = int(self._interpolate(self.calData['tracking']['coef'], self.calData['tracking']['cp1'], invOD, zoomStep))
        focusStep += BFL

        # validate the result
        err = lensIQ.OK
        focusStepMax = self.calData['focusSteps']
        if focusStep < 0:
            err = lensIQ.ERR_RANGE_MIN
            focusStep = 0
        elif focusStep > focusStepMax:
            err = lensIQ.ERR_RANGE_MAX
            focusStep = focusStepMax

        # save the results
        self._updateEngValues('focusStep', focusStep)
        log.info(f'Tracking curve: zoom step {zoomStep}, focus step {focusStep} at OD {OD:0.2f}')
        return focusStep, err

    # calculate object distance from focus motor step
    def ODFL2FocusStep(self, OD:float, FL:float, BFL:int=0) -> tuple[int, str]:
        '''
        Calculate the focus motor step from object distance and focal length.  
        If the zoom step is known, use OD2FocusStep instead to increase the accuracy of the prediction.  
        The focus motor step will be limited to the available range.  
        If the calculation is out of focus step range, there will be note value.  
        Mzximum object distance input can be 1000m (infinity).  Minimum object distance
        can be 0 but focus motor step may not support this minimum.  
        ### input
        - OD: object distance in meters
        - FL: focal length
        - BFL (optional: 0): back focus step adjustment
        ### return
        [focusStep, note]
        'note' string value can be: ['OK' | 'no cal data' | 'out of range-min' | 'out of range-max']
        '''
        if self.calData == {}: return 0, lensIQ.ERR_NO_CAL
        # get the zoom step
        zoomStep, _err = self.FL2ZoomStep(FL)
        focusStep, err = self.OD2FocusStep(OD, zoomStep, BFL)
        return focusStep, err

    # calculate iris step from numeric aperture
    def NA2IrisStep(self, NA:float, FL:float) -> tuple[int, str]:
        '''
        Calculate iris step from numeric aperture.
        If the numeric aperture is not supported for the current focal length, return the
        min/max iris step position and the out of range error.
        ### input
        - NA: numeric aperture
        - FL: current focal length
        ### return
        [iris motor step, note]
        'note' string value can be: ['OK' | 'no cal data' | 'NA min' | 'NA max']
        '''
        if 'AP' not in self.calData.keys(): return 0, lensIQ.ERR_NO_CAL

        # find 2 closest focal lengths in the calibrated data file to the target
        FLList = np.subtract(self.calData['AP']['cp1'], FL)

        # sort the FL differences from 0 (root) and save the list indexes
        FLIdx = np.argsort(np.abs(FLList))
        closestFL = np.add(np.array(FLList)[np.sort(FLIdx[:2])], FL)

        # define the merit function (NA v. irisStep) for the root finding
        def merit(x, coef, target):
            return nppp.polyval(x, coef) - target

        # find the coefficients for each focal length and calcualte the iris step for the target NA
        err = lensIQ.OK
        coef = []
        stepValueList = []
        for f in closestFL:
            idx = self.calData['AP']['cp1'].index(f)
            coef = self.calData['AP']['coef'][idx]
            NAMax = nppp.polyval(0, coef)
            if NA < NAMax:
                try:
                    stepValue = optimize.newton(merit, 20, args=(coef, NA,))
                except RuntimeError as e:
                    # no convergence due to excessively negative NA value
                    stepValue = self.calData['irisSteps']
                    err = lensIQ.ERR_NA_MIN
            else:
                stepValue = 0
                err = lensIQ.ERR_NA_MAX
            stepValueList.append(stepValue)

        # interpolate between step values
        interpolationFactor = (FL - closestFL[0]) / (closestFL[1] - closestFL[0])
        irisStep = int(stepValueList[0] + interpolationFactor * (stepValueList[1] - stepValueList[0]))
        
        # save the results
        self._updateEngValues('irisStep', irisStep)
        log.info(f'NA {NA:0.3f} -> iris step {irisStep} at FL {FL:0.2f}')
        return irisStep, err

    # calcualted the iris motor step from F/#
    def fNum2IrisStep(self, fNum:float, FL:float) -> tuple[int, str]:
        '''
        Calcualte the iris motor step from F/#.
        ### input
        - fNum: F/#
        - FL: current focal length
        ### return
        [iris motor step, note]
        'note' string value can be: ['OK' | 'no cal data' | 'NA min' | 'NA max']
        '''
        if 'AP' not in self.calData.keys(): return 0, lensIQ.ERR_NO_CAL

        # calcualte the NA
        NA = self._FNum2NA(fNum)

        irisStep, err = self.NA2IrisStep(NA, FL)
        return irisStep, err

    # Angle of view to motor steps
    def AOV2MotorSteps(self, AOV:float, sensorWd:float, OD:float=1000000, BFL:int=0) -> tuple[int, int, float, str]:
        '''
        Angle of view to motor steps
        Calculate the zoom motor step that allows the input angle of view.  If the focal length range
        doesn't support the FOV, return an out of range error.
        Also calculate the focus motor step to keep the lens in focus.
        If the object distance is not specified, use infinity. If OD < 0 or OD type is a string, do not calculate focus motor step position. 
        ### input
        - AOV: field of view in degrees
        - sensorWd: image sensor width
        - OD (optional: infinity): object distance
        - BFL (optional: 0): back focal length adjustment for focus motor
        ### return
        [focusStep, zoomStep, calculated focal length, note]
        'note' string value can be: ['OK' | 'no cal data' | 'out of range-min' | 'out of range-max' | 'OD value']
        '''
        if 'dist' not in self.calData.keys(): return 0, 0, 0, lensIQ.ERR_NO_CAL

        # get the maximum angle of view for each focal length in the calibration data file
        FLLower = None
        FLUpper = None
        FLList = np.sort(self.calData['dist']['cp1'])
        for FL in FLList:
            AOVMax, _err = self.calcAOV(sensorWd, FL)
            if AOVMax > AOV:
                FLLower = [FL, AOVMax]
            elif FLUpper == None:
                FLUpper = [FL, AOVMax]

        # check if AOV is greater than maximum AOV for the lens (not wide angle enough)
        if FLLower == None:
            # re-calculate to extrapolate focal length
            FLLower = FLUpper
            FL = FLList[1]
            AOVMax, _err = self.calcAOV(sensorWd, FL)
            FLUpper = [FL, AOVMax]

        # check if AOV is less than the minimum AOV for the lens (not telephoto enough)
        if FLUpper == None:
            # recalcualte to extrapolate focal length
            FLUpper = FLLower
            FL = FLList[-2]
            AOVMax, _err = self.calcAOV(sensorWd, FL)
            FLLower = [FL, AOVMax]

        # interpolate to get the focal length value
        interpolationFactor = (AOV - FLLower[1]) / (FLUpper[1] - FLLower[1])
        FLValue = FLLower[0] + interpolationFactor * (FLUpper[0] - FLLower[0])

        # validate FL range
        err = lensIQ.OK
        if FLValue < self.calData['flMin']:
            err = lensIQ.ERR_RANGE_MIN
        elif FLValue > self.calData['flMax']:
            err = lensIQ.ERR_RANGE_MAX

        # calculate zoom step from focal length
        zoomStep, err = self.FL2ZoomStep(FLValue)
        self._updateEngValues('zoomStep', zoomStep)
        self._updateEngValues('FL', FLValue)

        # check if object distance is valid
        if isinstance(OD, str):
            err = lensIQ.ERR_OD_VALUE
            focusStep = 0
        elif OD <= 0:
            err = lensIQ.ERR_OD_VALUE
            focusStep = 0
        else:
            # calculate focus step using focus/zoom curve
            focusStep, err = self.OD2FocusStep(OD, zoomStep, BFL)
        self._updateEngValues('focusStep', focusStep)
        log.info(f'AOV {AOV:0.2f} -> zoom step {zoomStep}, focus step {focusStep}')
        return focusStep, zoomStep, FLValue, err

    # field of view to motor steps
    def FOV2MotorSteps(self, FOV:float, IH:float, OD:float=1000000, BFL:int=0) -> tuple[int, int, float, str]:
        '''
        Field of view to motor steps. 
        Calculate the zoom motor step that allows the field of view.  If the focal length
        is out of range, return a range error but also the calculated focal length.
        The zoom and focus motor steps won't exceed the limits.
        If OD < 0 or OD type is a string, do not calculate focus motor step position.
        ### input
        - FOV: field of view in meters
        - IH: image height (sensor width)
        - OD (optional: infinity): object distance in meters
        - BFL (optional: 0): back focus step adjustment
        ### return
        [focusStep, zoomStep, calcualted FL, note]
        'note' string value can be: ['OK' | 'no cal data' | 'out of range-min' | 'out of range-max' | 'calculation error' | 'OD value']
        '''
        if 'dist' not in self.calData.keys(): return 0, 0, 0, lensIQ.ERR_NO_CAL
        AOV = self._FOV2AOV(FOV, OD)
        if AOV == 0:
            return 0, 0, 0, lensIQ.ERR_CALC
        focusStep, zoomStep, FLValue, err = self.AOV2MotorSteps(AOV, IH, OD, BFL)
        return focusStep, zoomStep, FLValue, err


    ### --------------------------------------- ###
    ### complex calculations, engineering units ###
    ### --------------------------------------- ###

    # calculate angle of view
    def calcAOV(self, sensorWd:float, FL:float, saveAOV:bool=True) -> tuple[float, str]:
        '''
        Calculate angle of view (full angle).  Optionally update the engineering values data structure.  
        ### input
        - sensorWd: width of sensor for horizontal AOV
        - FL: focal length
        - saveAOV (optional: True): save the calculated AOV to the data structure
        ### return
        [full angle of view (deg), note]
        'note' string value can be: ['OK', 'no cal data']
        '''
        if 'dist' not in self.calData.keys(): return 0, lensIQ.ERR_NO_CAL
        semiWd = sensorWd / 2

        # extract the object angle value
        semiAOV = abs(self._interpolate(self.calData['dist']['coef'], self.calData['dist']['cp1'], FL, semiWd))
        AOV = 2 * semiAOV

        # save the results
        if saveAOV: self._updateEngValues('AOV', AOV)
        return AOV, lensIQ.OK
    
    # calculate the AOV limits for the lens (minimum and maximum)
    def calcAOVLimits(self) -> tuple[float, float, str]:
        '''
        Calculate the AOV limits for the lens (minimum and maximum). AOV is related to focal length.  
        'flMin' and 'flMax' are read from the calibration lens data or default calibration data.  
        Update the values data structure with min/max values.  
        ### input
        - none
        ### return
        [AOVMin, AOVMax, note]
        'note' string value can be: ['OK']
        '''
        flMin = self.calData['flMin']
        flMax = self.calData['flMax']

        self.engValues['AOV']['max'], _err = self.calcAOV(self.sensorWd, flMin, saveAOV=False)
        self.engValues['AOV']['min'], _err = self.calcAOV(self.sensorWd, flMax, saveAOV=False)

        return self.engValues['AOV']['min'], self.engValues['AOV']['max'], lensIQ.OK

    # calculate field of view
    def calcFOV(self, sensorWd:float, FL:float, OD:float=1000000, saveFOV:bool=True) -> tuple[float, str]:
        '''
        Calculate the full field of view width (in meters). Optionally update the engineering units data structure.  
        ### input
        - sensorWd: width of sensor for horizontal FOV
        - FL: focal length
        - OD (optional, infinity): object distance
        - saveFOV (optional, True): save the calculated FOV to the data structure
        ### return
        [full field of view (m), note]
        'note' string value can be: ['OK', 'no cal data']
        '''
        if 'dist' not in self.calData.keys(): return 0, lensIQ.ERR_NO_CAL
        AOV, _err  = self.calcAOV(sensorWd, FL, saveFOV)

        # calcualte the FOV at the object distance
        FOV = 2 * OD * np.tan(np.radians(AOV / 2))
        
        # save the results
        if saveFOV: self._updateEngValues('FOV', FOV)
        return FOV, lensIQ.OK
    
    # calculate the FOV limits for the lens (minimum and maximum)
    def calcFOVLimits(self) -> tuple[float, float, str]:
        '''
        Calculate the FOV limits for the lens (minimum and maximum). FOV is related to focal length and object distance.  
        'flMin' and 'flMax' are read from the calibration lens data or default calibration data.  
        Update the engineering units data structure with min/max values.  
        ### input
        - none
        ### return
        [FOVMin, FOVMax, note]
        'note' string value can be: ['OK']
        '''
        flMin = self.calData['flMin']
        flMax = self.calData['flMax']

        self.engValues['FOV']['max'], _err = self.calcFOV(self.sensorWd, flMin, self.engValues['OD']['value'], saveFOV=False)
        self.engValues['FOV']['min'], _err = self.calcFOV(self.sensorWd, flMax, self.engValues['OD']['value'], saveFOV=False)

        return self.engValues['FOV']['min'], self.engValues['FOV']['max'], lensIQ.OK

    # calcualte depth of field
    def calcDOF(self, irisStep:int, FL:float, OD:float=1000000) -> tuple[float, str, float, float]:
        '''
        Calcualte depth of field.
        Calcualte the minimum and maximum object distances.  The difference is the depth of field.
        All 3 values are returned becuase minimum object distance is probably the most useful.  
        ### input
        - irisStep: iris motor step position
        - FL: focal length
        - OD (optional: infinity): object distance
        ### return
        [depth of field, note, minimum object distance, maximum object distance]
        'note' string value can be: ['OK' | 'no cal data']
        '''
        if 'iris' not in self.calData.keys(): return 0, lensIQ.ERR_NO_CAL, 0, 0
        if OD >= lensIQ.INFINITY: return lensIQ.INFINITY, lensIQ.OK, lensIQ.INFINITY, lensIQ.INFINITY

        # extract the aperture size
        shortDiameter = self._interpolate(self.calData['iris']['coef'], self.calData['iris']['cp1'], FL, irisStep)

        # calculate the magnification
        OD = max(0.001, OD)
        magnification = (FL / 1000) / OD

        # calculate min and max object distances
        # denominator ratios are unitless so calculations are in the units of object distance
        ODMin = min(OD / (1 + self.COC / (shortDiameter * magnification)), lensIQ.INFINITY)
        ODMax = min(OD / (1 - self.COC / (shortDiameter * magnification)), lensIQ.INFINITY)
        if ODMax < 0: ODMax = lensIQ.INFINITY

        # calculate depth of field
        if ODMax == lensIQ.INFINITY:
            DOF = lensIQ.INFINITY
        else:
            DOF = ODMax - ODMin

        # save the results
        self._updateEngValues('DOF', DOF, ODMin, ODMax)
        return DOF, lensIQ.OK, ODMin, ODMax
    
    ### -------------------------------------- ###
    ### update additional engineering outputs  ###
    ### -------------------------------------- ###

    # updateAfterZoom
    def updateAfterZoom(self, zoomStep):
        '''
        Update after zoom.  
        After changing the zoom motor step number, update (recalculate if neccessary) the new
        values for focal length, F/# and numeric aperture, field of view, 
        and depth of focus.  Store the updated data in engValues.  
        There is limited error checking.  
        ### input
        - zoomStep: zoom step number
        ### return
        none
        '''
        self.engValues['tsLatest'] += 1
        self._updateEngValues('zoomStep', zoomStep)
        log.info('Update after zoom: FL, FOV, DOF, Iris')

        # set the new focal length 
        FL, _err, _flMin, _flMax = self.zoomStep2FL(zoomStep)

        # calculate the new focus step
        if not isinstance(self.engValues['OD']['value'], str) and self.engValues['OD']['value'] > 0:
            self.OD2FocusStep(self.engValues['OD']['value'], zoomStep)
            self.calcFOV(self.sensorWd, FL, OD=self.engValues['OD']['value'])
            self.calcFOVLimits()
            self.calcDOF(self.engValues['irisStep']['value'], FL, self.engValues['OD']['value'])
        self.calcAOV(self.sensorWd, FL)
        self.irisStep2FNum(self.engValues['irisStep']['value'], FL)

    # updateAfterFocus
    def updateAfterFocus(self, focusStep:int, updateOD:bool=True):
        '''
        Update after focus. 
        After changing the focus step number, update the new values for engineering units. The object distance, 
        field of view, and depth of focus are updated.  Store the updated data in the engValues.  
        There is limited error checking. 
        ### input
        - focusStep: focus step number
        - updateOD (optional: True): recalculate the object distance from the new focus step and save
        ### return
        none
        '''
        self.engValues['tsLatest'] += 1
        self._updateEngValues('focusStep', focusStep)
        log.info('Update after focus: OD, FOV, DOF')

        # calculate the object distance
        if updateOD:
            OD, _err, ODMin, ODMax= self.focusStep2OD(focusStep, self.engValues['zoomStep']['value'])
            self._updateEngValues('OD', OD, ODMin, ODMax)
        else:
            OD = self.engValues['OD']['value']

        if not isinstance(OD, str) and OD > 0:
            # calculate the field of view and depth of field
            self.calcFOV(self.sensorWd, self.engValues['FL']['value'], OD)
            self.calcFOVLimits()
            self.calcDOF(self.engValues['irisStep']['value'], self.engValues['FL']['value'], OD)

    # update after OD change
    def updateAfterODChange(self, OD:float):
        '''
        Update after object distance change.  At longer OD, the calcualted OD may be quite a long
        way off the requested OD.  Store the requested OD instead of the calcualted OD.  
        ### input: 
        - OD: object distance for calculation
        ### return
        none
        '''
        self.engValues['tsLatest'] += 1
        self._updateEngValues('OD', OD)
        log.info('Update after OD change: FOV, DOF')
        
        if not isinstance(OD, str) and OD > 0:
            # calculate the field of view and depth of field
            self.calcFOV(self.sensorWd, self.engValues['FL']['value'], OD)
            self.calcFOVLimits()
            self.calcDOF(self.engValues['irisStep']['value'], self.engValues['FL']['value'], OD)

    # updateAfterIris
    def updateAfterIris(self, irisStep:int):
        '''
        Update after iris move.  
        Update the engineering unit values after a change in lens aperture step.  F/#, numeric aperture, 
        and depth of focus are udpated.   Store the udpated data in the engValues.  
        There is limited error checking. 
        ### input
        - irisStep: the iris step number
        ### return
        none
        '''
        self.engValues['tsLatest'] += 1
        self._updateEngValues('irisStep', irisStep)
        log.info('Update after iris, DOF')

        # calculate F/# and numeric aperture
        self.irisStep2FNum(irisStep, self.engValues['FL']['value'])
        
        # update the field of view and angle of view
        if not isinstance(self.engValues['OD']['value'], str) and self.engValues['OD']['value'] > 0:
            self.calcDOF(irisStep, self.engValues['FL']['value'], self.engValues['OD']['value'])

    ### -------------------------------------- ###
    ### back focal length correction functions ###
    ### -------------------------------------- ###

    # back focal length correction factor
    ##### TBD add object distance OD; currently all OD will be included in the fitting together
    def BFLCorrection(self, FL:float, OD:float=1000000) -> int:
        '''
        Back focal length correction factor. 
        Whenever focus step is calculated, this function will calculate the correction value (in steps)
        for the focus motor position at the current focal length. 
        Tolerances in the lens to sensor position will cause an offset in the focus motor step position. 

        This function reads stored values from the global 'BFLCorrectionCoefs' to calculate the correction value.  

        NOTE: Current calculations do not take object distance into account.  All correction factors are based
        on the same object distance where the BFL correction points were stored.  
        ### input: 
        - FL: focal length
        - OD: **Not currently supported**
        ### return
        focus step difference
        '''
        if len(self.BFLCorrectionCoeffs) == 0:
            # no correction values set up yet
            return 0
        # calculate the correction step for the focal length
        correctionValue = nppp.polyval(FL, self.BFLCorrectionCoeffs)

        # calculate correction value for object distance
        #ODCorrection = self.ODFL2FocusStep(OD, FL, 0)
        #log.debug(f'  Focus step correction for BFL {correctionValue} and OD {ODCorrection}') ###############
        #correctionValue += ODCorrection

        log.debug(f'Focus step correction {correctionValue} at FL {FL:0.2f}')
        return int(correctionValue)

    # store data points for BFL correction
    def addBFLCorrectionByFL(self, FL:float, focusStep:int, OD:float=1000000) -> list:
        '''
        Store data points for BFL correction. 
        With the lens set to an object distance and focal length, the calculated focus step is compared
        to the set best focus position.  The difference is added to the BFL correction factor list.  
        Add a focus shift amount to the list and fit for focal length [[FL, focus shift], [...]]. 
        If the zoom motor step position is known, use addBFLCorrectionByZoomStep() instead to get a more
        accurate result due to not needing to calculate zoom step from focal length.  
        
        NOTE: all points are used for fitting regardless of the object distance.  Make sure the saved
        points all have the same object distance.  
        ### input
        - FL: current focal length
        - focusStep: focus step position for best focus
        - OD: (optional: infinity): current object distance in meters
        ### return
        [[FL, step, OD],[...]]
        Current set point BFL correction list 
        '''
        # find the default focus step for infinity object distance
        designFocusStep, _err = self.ODFL2FocusStep(OD, FL, BFL=0)

        # save the focus shift amount and re-fit the points
        self.addBFLCorrectionDelta(FL, focusStep - designFocusStep, OD)

        # return the values
        return self.BFLCorrectionValues

    # store data points for BFL correction
    def addBFLCorrectionByZoomStep(self, zoomStep:int, focusStep:int, OD:float=1000000) -> list:
        '''
        Store data points for BFL correction. 
        With the lens set to an object distance and focal length, the calculated focus step is compared
        to the set best focus position.  The difference is added to the BFL correction factor list.  
        Add a focus shift amount to the list and fit for focal length [[FL, focus shift], [...]]. 
        
        NOTE: all points are used for fitting regardless of the object distance.  Make sure the saved
        points all have the same object distance.  
        ### input
        - zoomStep: zoom motor step position
        - focusStep: focus step position for best focus
        - OD: (optional: infinity): current object distance in meters
        ### return
        [[FL, step, OD],[...]]
        Current set point BFL correction list 
        '''
        # find the default focus step for infinity object distance
        designFocusStep, _err = self.OD2FocusStep(OD, zoomStep, BFL=0)

        # save the focus shift amount and re-fit the points
        FL, _err, _flmin, _flmax = self.zoomStep2FL(zoomStep)
        self.addBFLCorrectionDelta(FL, focusStep - designFocusStep, OD)

        # return the values
        return self.BFLCorrectionValues

    # store data points for BFL correction
    def addBFLCorrectionDelta(self, FL:float, focusDelta:int, OD:float=1000000) -> list:
        '''
        Store data points for BFL correction. 
        With the lens set to an object distance and focal length, save the focus step
        difference from best focus position.  The difference is added to the BFL correction factor list.  
        Add a focus shift amount to the list and fit for focal length [[FL, focus shift], [...]]. 

        NOTE: all points are used for fitting regardless of the object distance.  Make sure the saved
        points all have the same object distance.  
        ### input
        - FL: current focal length
        - focusDelta: focus step difference from best focus
        - OD: (optional: infinity): current object distance in meters
        ### return
        [[FL, step, OD],[...]]
        Current set point BFL correction list 
        '''
        # save the focus shift amount
        self.BFLCorrectionValues.append([FL, focusDelta, OD])
        log.debug(f'Add BFL correction point {len(self.BFLCorrectionValues)}: FL {FL:0.2f}, delta steps {focusDelta}')

        # re-fit the data
        self.fitBFLCorrection()
        return self.BFLCorrectionValues
    
    # remove BFL correction point
    def removeBFLCorrectionByIndex(self, idx:int) -> list:
        '''
        Remove data points from the BFL correction list. 
        Remove the data point based on list index.  
        ### input
        - idx: index number (0-based) to remove from the list
        ### return
        [[FL, step, OD],[...]]
        Current set point BFL correction list 
        '''
        if idx < 0 or idx >= len(self.BFLCorrectionValues):
            return self.BFLCorrectionValues

        # delete the item
        del self.BFLCorrectionValues[idx]

        # re-fit the data
        self.fitBFLCorrection()
        return self.BFLCorrectionValues

    # curve fit the BFL correction list
    def fitBFLCorrection(self):
        '''
        Curve fit the BFL correction list.  Global list variable 'BFLCorrectionCoeffs' list is updated.  
        NOTE: all points are used for fitting regardless of the object distance.  Make sure the saved
        points all have the same object distance.  
        ### input
        none
        ### return
        none
        '''
        if len(self.BFLCorrectionValues) == 0:
            self.BFLCorrectionCoeffs = []
            return
        
        xy = np.transpose(self.BFLCorrectionValues)
        # fit the data
        if len(self.BFLCorrectionValues) == 1:
            # single data point, constant offset
            self.BFLCorrectionCoeffs = xy[1]
        elif len(self.BFLCorrectionValues) <= 3:
            # linear fit for up to 3 data points
            self.BFLCorrectionCoeffs = nppp.polyfit(xy[0], xy[1], 1)
        else:
            # quadratic fit for > 3 data points
            self.BFLCorrectionCoeffs = nppp.polyfit(xy[0], xy[1], 2)

    # reset BFL correction
    def resetBFLCorrection(self):
        '''
        Delete all the BFL correction values and coefficients.  Reset to default (pre-correction).  
        '''
        self.BFLCorrectionValues = []
        self.BFLCorrectionCoeffs = []

    ### ----------------- ###
    ### support functions ###
    ### ----------------- ###

    # calculate F/# from NA
    def _NA2FNum(self, NA:float) -> float:
        '''
        Calculate F/# from NA. 
        Use the simple inversion formula.  
        ### input
        - NA: numeric aperture
        ### return
        F/#
        '''
        if NA == 0:
            return 10000
        return 1 / (2 * NA)

    # calculate NA from F/#
    def _FNum2NA(self, fNum:float) -> float:
        '''
        Calculate NA from F/#. 
        Use the simple inversion formula.  
        ### input
        - F/#: numeric aperture
        ### return
        NA
        '''
        if fNum == 0:
            return 1    # max possible NA in air
        return 1 / (2 * fNum)

    # calcualte angle of view from field of view
    def _FOV2AOV(self, FOV:float, OD:float=1000000) -> float:
        '''
        Calcualte angle of view from field of view.
        ### input
        - FOV: field of view in meters
        - OD (optional: infinity): object distance
        ### return
        angle of view
        '''
        # check for 'infinity' input to FOV or OD
        if isinstance(FOV, str) or isinstance(OD, str) or (OD == 0) or (FOV == 0):
            return 0
        AOV = np.degrees(2 * np.arctan((FOV / 2) / OD))
        return AOV
    
    # store data in the lensConfig structure
    def _updateEngValues(self, key:str, value:tuple[float, int, str], min:tuple[float, int]=None, max:tuple[float, int]=None):
        '''
        Store data in the lensConfig list structure.
        ### input
        - key: key to store data to
        - value: data to store (may be error value for OD)
        - min, max (optional): data to store
        ### return
        none
        '''
        if key not in self.engValues:
            return
        self.engValues[key]['value'] = value
        if min: self.engValues[key]['min'] = min
        if max: self.engValues[key]['max'] = max
        self.engValues[key]['ts'] = self.engValues['tsLatest']
        return 

    # interpolate/ extrapolate between two values of control points
    def _interpolate(self, coefList:list, cp1List:list, cp1Target:float, xValue:float) -> float:
        '''
        Interpolate/ extrapolate between two values of control points. 
        This function has coefficients for a polynomial curve at each of the control points cp1.
        The curves for the two closest control points around the target are selected and the
        'xValue' is calculated for each.  Then the results are interpolated to get to the cp1 target.
        ### input
        - coefList: coefficient list of lists for all cp1 values
        - cp1List: cp1 control point 1 list corresponding to the coefficients
        - cp1Target: target control point target
        - xValue: x evaluation value
        ### return
        interpolated value
        '''
        # check for only one data set
        if len(cp1List) <= 1:
            return nppp.polyval(cp1Target, coefList[0])

        # Find the indices of the closest lower and upper cp1 values
        valList = np.subtract(cp1List, cp1Target)
        valIdx = np.argsort(np.abs(valList))

        # Extract the corresponding lower and upper coefficients
        lowerCoeffs = coefList[valIdx[0]]
        upperCoeffs = coefList[valIdx[1]]

        # calculate the values
        lowerValue = nppp.polyval(xValue, lowerCoeffs)
        upperValue = nppp.polyval(xValue, upperCoeffs)

        # Calculate the interpolation factor
        interpolation_factor = (cp1Target - cp1List[valIdx[0]]) / (cp1List[valIdx[1]] - cp1List[valIdx[0]])

        # Interpolate between the lower and upper coefficients
        interpolatedValue = lowerValue + interpolation_factor * (upperValue - lowerValue)

        return interpolatedValue