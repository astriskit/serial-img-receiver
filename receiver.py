import serial
import datetime
import sys
import signal

# module is use-case specific pyserial based tool to read from the a serial port(input)
# and look for 'ffd8' and 'ffd9' markers to decide for image boundary
# and finally save it with a format based on time.

file_id = 0; # number of times the file has been saved.
corrupt_counter = 0; # number of times corruption was found.
corrupt_bytes = 0; # number of bytes corrupted, which were flushed.

def gracefully_exit(sig, frame):
	'''for handling Ctrl+C'''
	global file_id, corrupt_counter
	print('Program is shutting down!')
	print('Stats uptill now are:\n Total files written:{0}\n Total corruption found till now:{1}\n'.format(file_id, corrupt_counter))
	sys.exit(0)

signal.signal(signal.SIGINT, gracefully_exit)

def receiver(port='COM4', baudrate=115200):
	'''Starts the receiver and listens for the data. And passes data for saving, if end markers are found.'''
	try:
		print('opening port: '+port+' with baudrate= '+str(baudrate))
		receiver = serial.Serial(port, baudrate, bytesize=8) # should start listening
		print('listening for data...')
		data = bytes()
		while True: #listen forever until the program is closed
			bytes_to_read = receiver.in_waiting
			if bytes_to_read == 0:
				continue
			received_data = receiver.read(bytes_to_read)
			if('ffd9' in received_data.hex()):
				end_marker = received_data.hex().index('ffd9')
				save_data = data.hex() + received_data.hex()[:end_marker+4]
				print('Trying to save data :\n Initial-hex-10:'+save_data[:10]+'\n Last-hex-10: '+save_data[len(save_data)-10:])
				save_file(save_data)
				data = received_data[end_marker+4:]
			else:
				data += received_data
	except serial.SerialException as err:
		print('Error while connection to port' + str(err))
	except Exception as err:
		print('Exception occurred in receiver function')
		raise

def save_file(hex_data):
	'''saves the data according to start and end'''
	global file_id, corrupt_bytes, corrupt_counter
	if hex_data.startswith('ffd8') and hex_data.endswith('ffd9'):
		file_name = datetime.datetime.now().strftime("%y%m%d%H%M%S") + '.jpg'
		file_id +=1
		print('file count: {0}'.format(file_id))
		with open(file_name, "wb") as fd:
			fd.write(bytes.fromhex(hex_data))
	else:
		# possible corrupt data
		corrupt_counter += 1
		print('Flushing data :\n Initial-hex-10:'+hex_data[:10]+'\n Last-hex-10: '+hex_data[len(hex_data)-10:])

if(__name__ == '__main__'):
	port = input('Enter port/just press enter :) (default:COM4):')
	baudrate = input('Enter baudrate/just press enter (default:115200):')
	if not port:
		port = 'COM4'
	if not baudrate:
		baudrate = 115200
	try:
		receiver(port, baudrate)
	except IOError as err:
		file_id -= 1
		print("Error while doing I/O" + str(err))
		# raise
	except Exception as err:
		print("Error occurred: "+str(err))
		raise
else:
	print('Run receiver.receiver :)')
