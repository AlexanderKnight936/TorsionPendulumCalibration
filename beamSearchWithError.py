import sys
sys.path.append("./PowerSupplyControl/")
import powersupply
import numpy as np
import time
import uncertainties as u
# import labjack library
from labjack import ljm
import matplotlib.pyplot as plt

# analog input to read from the labjack
analogInputName = 'AIN1'

# assign the correct port address to each supply
xCoil = powersupply.PowerSupply('/dev/tty.usbserial-FTBZ1G1B')
yCoil = powersupply.PowerSupply('/dev/tty.usbserial-FTBYZZIN')
zCoil = powersupply.PowerSupply('/dev/tty.usbserial-FTFBPHDT')

# preliminary calibration data:
xFieldGain = u.ufloat(42.24e-6, 0.08e-6) # T/A
yFieldGain = u.ufloat(45.99e-6, 0.09e-6) # T/A
zFieldGain = u.ufloat(132.16e-6, 0.08e-6) # T/A

# field to current gain for the adustment coils (extrapolated from the large coil calibration)
xAFieldGain = xFieldGain / 25
yAFieldgain = yFieldGain / 20

# power supply current command limits
maxPowerSupplyCurrent = 0.9999 #A
minPowerSupplyCurrent = 0.0010 #A

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

def TotalFieldBeamSearch():
    '''
    Checks the entire field space for zero crossings
    '''

    # open the powersupply ports
    xCoil.openPort()
    yCoil.openPort()
    zCoil.openPort()

    #open the labjack
    handle = ljm.open(ljm.constants.dtANY, ljm.constants.ctANY, "ANY")

    # check labjack connection
    info = ljm.getHandleInfo(handle)
    print("Opened a LabJack with Device type: %i, Connection type: %i,\n" \
        "Serial number: %i, IP address: %s, Port: %i,\nMax bytes per MB: %i" % \
        (info[0], info[1], info[2], ljm.numberToIP(info[3]), info[4], info[5]))

    ##############
    steps = 1000
    Bx = np.linspace(xAppliedMinField, xAppliedMaxField, 40)
    By = np.linspace(yAppliedMinField, yAppliedMaxField, 1000)
    Bz = np.linspace(56.0, 62.0, 200)



    minSumSignal = 3.0

    sumSignal = []

    for i in range(len(Bx)):
        if i % 2:
            for j in range(len(By)):
                field_cart(Bx[i],By[j])
                #time.sleep(0.1)
                result = float(ljm.eReadName(handle,analogInputName))
                if result > minSumSignal:
                    sumSignal.append([Bx[i],By[j]])
        else:

            for j in range(len(By)):
                field_cart(Bx[i],By[-(j+1)])
                #time.sleep(0.1)
                result = float(ljm.eReadName(handle,analogInputName))
                if result > minSumSignal:
                    sumSignal.append([Bx[i],By[-(j+1)]])

    # close the labjack connection
    ljm.close(handle)

    # close the powersupply conections
    xCoil.closePort()
    yCoil.closePort()
    zCoil.closePort()


    # plot the data

    # generate timestamp
    timeStamp = time.strftime('%m_%d_%y_%H_%M_%S')

    for i in range(len(sumSignal)):
        plt.scatter(sumSignal[i][0],sumSignal[i][1])
    np.savetxt(timeStamp+'quadtrantSearchData.txt', sumSignal)
    plt.savefig(timeStamp + 'quadrantSearch.png')
    plt.show()
    ##############

def find_nearest(array, value):
    '''Finds the index of the element in an array that is closest to a value
    '''
    idx = (np.abs(array-value)).argmin()
    return idx


def beamSearch(searchAxis, steps=1000, minSumSignal):
    '''
    This function takes a value in x or y axis and adjusts the other until a
    high sum signal is reached, then returns the values at which optical zeroi
    is seen.
    '''

    # open the powersupply ports
    xCoil.openPort()
    yCoil.openPort()
    zCoil.openPort()

    #open the labjack
    handle = ljm.open(ljm.constants.dtANY, ljm.constants.ctANY, "ANY")

    # check labjack connection
    info = ljm.getHandleInfo(handle)
    print("Opened a LabJack with Device type: %i, Connection type: %i,\n" \
        "Serial number: %i, IP address: %s, Port: %i,\nMax bytes per MB: %i" % \
        (info[0], info[1], info[2], ljm.numberToIP(info[3]), info[4], info[5]))

    ##############
    #steps = 1000
    #Bx = np.linspace(xAppliedMinField, xAppliedMaxField, 40)
    #By = np.linspace(yAppliedMinField, yAppliedMaxField, 1000)
    #Bz = np.linspace(56.0, 62.0, 200)

    if searchAxis == 'x':

        Bx = np.linspace(xAppliedMinField, xAppliedMaxField, steps)
        By = xyz.yCoil.getLargeCoilField()
        Bz = xyz.zCoil.getLargeCoilField()

        BxInit = xyz.xCoil.getLargeCoilField()
        BxInitIndex = find_nearest(Bx, BxInit)

        for x in Bx[BxInitIndex:]:
            xyz.fine_field_cart(x,By, Bz, handle)
            #time.sleep(0.1)
            result = float(ljm.eReadName(handle,analogInputName))
            if result > minSumSignal:
                return [x, By, Bz]
        for x in reversed(Bx):
            xyz.fine_field_cart(x, By, Bz, handle)
            result = float(ljm.eReadName(handle,analogInputName))
            if result > minSumSignal:
                return [x, By, Bz]


    elif searchAxis == 'y':
        Bx = xyz.xCoil.getLargeCoilField()
        By = np.linspace(yAppliedMinField, yAppliedMaxField, steps)
        Bz = xyz.zCoil.getLargeCoilField()

        ByInit = xyz.yCoil.getLargeCoilField()
        ByInitIndex = find_nearest(By, ByInit)

        for y in By[ByInitIndex:]:
            xyz.fine_field_cart(Bx,y, Bz, handle)
            #time.sleep(0.1)
            result = float(ljm.eReadName(handle,analogInputName))
            if result > minSumSignal:
                return [Bx, y, Bz]
        for y in reversed(By):
            xyz.fine_field_cart(Bx, y, Bz, handle)
            result = float(ljm.eReadName(handle,analogInputName))
            if result > minSumSignal:
                return [Bx, y, Bz]

    else:
        Bx = xyz.xCoil.getLargeCoilField()
        By = xyz.yCoil.getLargeCoilField()
        Bz = np.linspace(zAppliedMinField, zAppliedMaxField, steps)

        BzInit = xyz.zCoil.getLargeCoilField()
        BzInitIndex = find_nearest(Bz, BzInit)

        for z in Bz[BzInitIndex:]:
            xyz.fine_field_cart(Bx,By, z, handle)
            #time.sleep(0.1)
            result = float(ljm.eReadName(handle,analogInputName))
            if result > minSumSignal:
                return [Bx, By, z]
        for z in reversed(Bz):
            xyz.fine_field_cart(Bx, By, z, handle)
            result = float(ljm.eReadName(handle,analogInputName))
            if result > minSumSignal:
                return [Bx, By, z]
