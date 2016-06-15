import sys
sys.path.append("./PowerSupplyControl/")
import powersupply
import numpy as np
import time
import uncertainties as u
from labjack import ljm # import labjack library
import matplotlib.pyplot as plt

# analog input to read from the labjack
analogInputName = 'AIN0'

# assign the correct port address to each supply
xCoil = powersupply.PowerSupply('/dev/tty.usbserial-FTBZ1G1B')
yCoil = powersupply.PowerSupply('/dev/tty.usbserial-FTBYZZIN')
zCoil = powersupply.PowerSupply('/dev/tty.usbserial-FTFBPHDT')

# preliminary calibration data:
xFieldGain = u.ufloat(42.24e-6, 0.08e-6) # T/A
yFieldGain = u.ufloat(45.99e-6, 0.09e-6) # T/A
zFieldGain = u.ufloat(132.16e-6, 0.08e-6) # T/A

# field to current gain for the adustment coils (extrapolated from the large coil calibration)
xAFieldGain = xFieldGain / 25 # T/A
yAFieldgain = yFieldGain / 20 # T/A

# power supply current command limits 
maxPowerSupplyCurrent = 0.9999 # A
minPowerSupplyCurrent = 0.0010 # A

# preliminary rough estimate feild values
xFieldOffset = 13.883e-6 # T
yFieldOffset = 13.883e-6 # T
zFieldOffset = 48.9e-6 # T

#Maximum possible field to be produced by coils
xAppliedMaxField = xFieldGain.n * maxPowerSupplyCurrent
yAppliedMaxField = yFieldGain.n * maxPowerSupplyCurrent
zAppliedMaxField = zFieldGain.n * maxPowerSupplyCurrent

#minimum possible field to be produced by coils
xAppliedMinField = xFieldGain.n * minPowerSupplyCurrent
yAppliedMinField = yFieldGain.n * minPowerSupplyCurrent
zAppliedMinField = zFieldGain.n * minPowerSupplyCurrent

#torsionalZero = 
#torsionConstant = 

def fine_field_cart(aFieldGain):
    '''
    set the large and small coils to obtain a certin field value
    use the small coils with the labjack in command response mode.
    
    only adust the large coil if the small DACs are out of range. 
    '''
    # should we make a powersupply like class to handel the dacs on the labjack?
    
    DAC_VOLTS_PER_AMP_GAIN = 1 / u.ufloat(250.00, 0.03) # Vin/I = 1/R where R = 250.00 +- 0.03 ohms
    DAC_VOLTS_PER_TESLA = DAC_VOLTS_PER_AMP_GAIN / aFieldGain
    

def field_polar(fieldMagnitude, fieldDirection):
    '''
    sets the field in the coils using the calibration data with polar coridinates as inputs
    does not allow the field to be greater than the smallest field offset.
    '''    
    angleRad = np.radians(fieldDirection) # ((np.pi)/(180))*angle
    
    # convert to cartesian 
    xField = xFieldOffset + (fieldMagnitude * np.sin(angleRad))
    yField = yFieldOffset + (fieldMagnitude * np.cos(angleRad))
    
    # devide the field-component by the axis gain to get the desired current for each coil
    xCurrent = xField / xFieldGain
    yCurrent = yField / yFieldGain
    
    xCoil.current(xCurrent.n*1e3) # set to the nominal value of the current
    yCoil.current(yCurrent.n*1e3) # with the .n (from the uncertinties package)
    
    return

def field_cart(xField, yField):
    '''
    sets the field in the coils using the calibration data with cartesian coordinates as input
    '''
    
    # devide the field-component by the axis gain to get the desired current for each coil
    xCurrent = xField / xFieldGain
    yCurrent = yField / yFieldGain
    
    print(xCurrent.n*1e3, yCurrent.n*1e3)
    xCoil.current(xCurrent.n*1e3) # set to the nominal value of the current
    yCoil.current(yCurrent.n*1e3) # with the .n (from the uncertinties package)
    
    return