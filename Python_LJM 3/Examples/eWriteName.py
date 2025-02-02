"""
Demonstrates how to use the labjack.ljm.eWriteName (LJM_eWriteName)
function.

"""

from labjack import ljm


# Open first found LabJack
handle = ljm.open(ljm.constants.dtANY, ljm.constants.ctANY, "ANY")
#handle = ljm.openS("ANY", "ANY", "ANY")

info = ljm.getHandleInfo(handle)
print("Opened a LabJack with Device type: %i, Connection type: %i,\n" \
    "Serial number: %i, IP address: %s, Port: %i,\nMax bytes per MB: %i" % \
    (info[0], info[1], info[2], ljm.numberToIP(info[3]), info[4], info[5]))

# Setup and call eWriteName to write a value to the LabJack.
name = "DAC0"
value = 2.5 # 2.5 V
ljm.eWriteName(handle, name, value)

print("\neWriteName: ")
print("    Name - %s, value : %f" % (name, value))

# Close handle
ljm.close(handle)
