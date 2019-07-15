#!/usr/bin/env python

from struct import pack

f_CENTER=434000 # in kHz (only used by rptix command)
f_OFF=-1000000 # in Hz (can be tuned)
f_ON=0 # in Hz (can be tuned)

BUFSIZE = 4000 * 4 # rpitx buffer size (don't change)

VOID = 10 # leave rptix some time to get ready before sending the payload (don't change)

INTERPOLATE = 10 # symbol interpolation

BAUDRATE = 930 # baudrate of original signal

# payload of the FSK signal to be generated
# 1 for ONE symbol
# 0 for ZERO symbol

payload_CMD =  [ 1, 0, 1, 1, 1, 1, 0, 1, 0, 0, 0, 0, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 0, 0, 0, 1, 0, 0, 1, 1, 0, 0, 1, 1 ]

FILENAME = 'fake-ook-CMD.rf'


BEGIN_ON = 14
BEGIN_OFF = 4

SEP_OFF = 21

ZERO_ON = 1
ZERO_OFF = 2

ONE_ON = 2
ONE_OFF = 1

REPEAT = 2

sr = BAUDRATE * INTERPOLATE * (ZERO_ON + ZERO_OFF) # sample rate to be used

def write_VOID(f,INTERPOLATE):
  for i in range( VOID * INTERPOLATE ):
    f.write(pack('dxxxxxxxx',f_OFF))

  return VOID * INTERPOLATE

def write_BEGIN(f,INTERPOLATE):
  for i in range(BEGIN_ON * INTERPOLATE):
    f.write(pack('dxxxxxxxx',f_ON))
  for i in range(BEGIN_OFF * INTERPOLATE):
    f.write(pack('dxxxxxxxx',f_OFF))

  return (BEGIN_ON + BEGIN_OFF) * INTERPOLATE
  

def write_SEP(f,INTERPOLATE):
  for i in range( SEP_OFF * INTERPOLATE ):
    f.write(pack('dxxxxxxxx',f_OFF))

  return SEP_OFF * INTERPOLATE


def write_ZERO(f,INTERPOLATE):
  for i in range(ZERO_ON * INTERPOLATE):
    f.write(pack('dxxxxxxxx',f_ON))
  for i in range(ZERO_OFF * INTERPOLATE):
    f.write(pack('dxxxxxxxx',f_OFF))

  return (ZERO_ON + ZERO_OFF) * INTERPOLATE

def write_ONE(f,INTERPOLATE):
  for i in range(ONE_ON * INTERPOLATE):
    f.write(pack('dxxxxxxxx',f_ON))
  for i in range(ONE_OFF * INTERPOLATE):
    f.write(pack('dxxxxxxxx',f_OFF))
  
  return (ONE_ON + ONE_OFF) * INTERPOLATE

def write_PAYLOAD(f,INTERPOLATE,payload,repeat=2):
  count = 0
  for i in range(repeat):
    count += write_BEGIN(f,INTERPOLATE)
    for j,bit in enumerate(payload):
      if bit == 0:
        count += write_ZERO(f,INTERPOLATE)
      else:
        count += write_ONE(f,INTERPOLATE)

  return count

f=open( FILENAME ,'wb')

count = 0

count += write_VOID(f,INTERPOLATE)

for i in range(REPEAT):
  count += write_PAYLOAD(f,INTERPOLATE,payload_CMD,1)
  count += write_SEP(f,INTERPOLATE)

# generate void so that the buffer is filled enough for rpitx (sending f0 frequency)
padding = -count

while padding < 0:
  padding += BUFSIZE


# NOTE: padding + 1 is needed to trigger the sending of last buffer received in rpitx. Without this one buffer is missed :)
for i in range( padding + 1):
    f.write(pack('dxxxxxxxx',f_OFF))
f.close()

print("run: sudo rpitx -i %s -m RF -s %d -f %d" % (FILENAME,sr,f_CENTER))
