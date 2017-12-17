 #!/usr/bin/env python3

# based on tutorials:
#   http://www.roman10.net/serial-port-communication-in-python/
#   http://www.brettdangerfield.com/post/raspberrypi_tempature_monitor_project/

import serial, time
import argparse
import msr605.msr605 as msr605

SERIALPORT = "/dev/ttyUSB0"

msr605 = msr605.MSR605(SERIALPORT, False, 1)

parser = argparse.ArgumentParser(description='This program is a toolbox to help the use of the MSR605 magnetic card reader/writer. Take a look at the MSR605 documentation for more details (http://www.triades.net/downloads/MSR605%20Programmer%27s%20Manual.pdf).We are also trying to respect the ISO7811 standard. Have fun and fork us on github.')
parser.add_argument('-r', '--read', action='store_true', help='set read mode. default mode.')
parser.add_argument('-w', '--write', action='store_true', help='set write mode. ignored if read mode is set.')
parser.add_argument('-e', '--erase', action='store', type=str, choices=['1', '2', '3', '12', '13', '23', '123'], help='set erase mode. ignored if read or write mode is set. its value determine wich track to erase; default erase all tracks.')
parser.add_argument('-t1', '--track1', action='store', type=str, help='data to write on track 1. alphanureic; see iso7811.')
parser.add_argument('-t2', '--track2', action='store', type=str, help='data to write on track 2. only numeric; see iso7811.')
parser.add_argument('-t3', '--track3', action='store', type=str, help='data to write on track 3. only numeric; see iso7811.')
parser.add_argument('-bpc', '--bpc', nargs=3, action='store', type=int, choices=range(5, 9), help='set bit per character for the 3 tracks. give the values with the order: track1 track2 track3')
parser.add_argument('-bpi', '--bpi', nargs=3, action='store', type=int, choices=[75, 210], help='set bit per inch for the 3 tracks. give the values with the order: track1 track2 track3')
parser.add_argument('-iso', '--iso', action='store_true', help='set iso format for read and write. default mode. overwrite -raw if both set')
parser.add_argument('-raw', '--raw', action='store_true', help='set raw format for read and write.')
parser.add_argument('--reset', action='store_true', help='only reset the MSR605.')
parser.add_argument('--com_test', action='store_true', help='only test the communication with the MSR605.')
parser.add_argument('--sensor_test', action='store_true', help='only run the sensor test on the MSR605.')
parser.add_argument('--ram_test', action='store_true', help='only run the ram test on the MSR605.')
parser.add_argument('--test', action='store_true', help='run communication, ram and sensor tests on the MSR605.')
parser.add_argument('--info', action='store_true', help='display device model and firmware version of the MSR605.')
parser.add_argument('--model', action='store_true', help='display device model of the MSR605.')
parser.add_argument('--firmware', action='store_true', help='display firmware version of the MSR605.')
parser.add_argument('-hi','--hico', action='store_true', help='set high-coercivity mode of the MSR605.')
parser.add_argument('-low','--lowco', action='store_true', help='set low-coercivity mode. ignored if high-coercivity mode is set.')
parser.add_argument('--info_coer', action='store_true', help='display coercivity status of the MSR605.')
parser.add_argument('--green', action='store_true', help='turn on green led, turn off red and yellow leds.')
parser.add_argument('--yellow', action='store_true', help='turn on yellow led, turn off green and red leds. overwrite --green argument')
parser.add_argument('--red', action='store_true', help='turn on red led and turn off green and yellow leds. overwrite --green and --yellow arguments')
parser.add_argument('--leds', action='store_true', help='turn all leds on. overwrite --green, --yellow, --red and --leds_off arguments')
parser.add_argument('--leds_off', action='store_true', help='turn all leds off. overwrite --green, --yellow and --red arguments')
parser.add_argument('-v', '--verbose', action='store_true', help='the tool is more verbatim')
args = parser.parse_args()

if args.verbose:
    print(args)

if msr605.isOpen():
    print('Communication opened with MSR605')

    try:

        if args.reset:
            print('reseting MSR605')
            msr605.reset()

        if args.erase:
            erase1 = '1' in args.erase
            erase2 = '2' in args.erase
            erase3 = '3' in args.erase
            msr605.erase_card(erase1, erase2, erase3)

        
        if args.write:
            if args.iso or not args.raw:
                msr605.write_iso(True, args.track1.encode('ascii'), args.track2.encode('ascii'), args.track3.encode('ascii'))
            else:
                msr605.write_raw(args.track1, args.track2, args.track3)
        

        if args.info:
            print('getting info...')
            version = msr605.get_firmware_version()
            model = msr605.get_device_model()
            print('firmware version: ' + version.decode('ascii'))
            print('device model: ' + model.decode('ascii'))

        if args.firmware:
            print('getting firmware version...')
            version = msr605.get_firmware_version()
            print('firmware version: ' + version.decode('ascii'))

        if args.model: 
            print('getting device model...')
            model = msr605.get_device_model()
            print('device model: ' + model.decode('ascii'))

        if args.com_test:
            print('testing communication...')
            msr605.communication_test()
            print('communication ok')

        if args.ram_test:
            print('testing ram...')
            msr605.ram_test()
            print('ram ok')

        if args.sensor_test:
            print('testing sensor...')
            msr605.sensor_test()
            print('sensor ok')

        if args.test:
            print('testing communication...')
            msr605.communication_test()
            print('communication ok')
            print('testing ram...')
            msr605.ram_test()
            print('ram ok')
            print('testing sensor...')
            msr605.sensor_test()
            print('sensor ok')

        if args.hico:
            print('setting coercivity to high...')
            msr605.set_hico()
            print('coercivity set to high')

        elif args.lowco:
            print('setting coercivity to low...')
            msr605.set_lowco()
            print('coercivity set to low')

        
        if args.info_coer:
            print('getting coercivity status...')
            status = msr605.get_co_status()

            coercivity = 'Hi-Co' if status == b'h' else 'Low-Co'
            print('coercivity status: ' + coercivity)

        if args.bpc:
            print('setting bpc values...')
            response = msr605.set_bpc(args.bpc[0], args.bpc[1], args.bpc[2])
            print('bpc values set to: track1=' + str(response[0]) + ', track2=' + str(response[1]) + ', track3=' + str(response[2]))

        if args.bpi:
            print('setting bpi...')
            t1 = args.bpi[0] == 210
            t2 = args.bpi[1] == 210
            t3 = args.bpi[2] == 210
            msr605.select_bpi(t1, t2, t3)
            print('bpi values set')

        if args.green and not args.leds_off:
            msr605.led_green_on()

        if args.yellow and not args.leds_off:
            msr605.led_yellow_on()

        if args.red and not args.leds_off:
            msr605.led_red_on()

        if args.leds:
            msr605.all_leds_on()

        if args.leds_off and not args.leds:
            msr605.all_leds_off()


        print('closing communication...')
        msr605.close()

    #except Exception as e:
    #    ser.close()
    #    print('error communicating...: ' + str(e))

    except KeyboardInterrupt:
        msr605.close()

    print('Communication closed with MSR605')
else:
    print('cannot open serial port')
