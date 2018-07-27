#!/usr/bin/python3

import argparse
import datetime
import ephem
import sys
import requests

# parse them args, matey ---------------------------------------------------------------------
parser = argparse.ArgumentParser(description='Argparser for sat tracker')
parser.add_argument('--lat', action='store', dest='lat')
parser.add_argument('--lon', action='store', dest='lon')
args = parser.parse_args()

# smart printing function --------------------------------------------------------------------
def print_smart(txt, log=False, debug=False, newline=True):
    if debug:
        sys.stdout.write('[DEBUG] ')
    elif log:
        sys.stdout.write('[ LOG ] ')
    sys.stdout.write(str(txt))
    if newline:
        sys.stdout.write('\n')

# util functions -----------------------------------------------------------------------------
def create_sats():
    # the ephem objects that will be returned
    noaa15 = {'name': '', 'line1': '', 'line2': ''}
    noaa18 = {'name': '', 'line1': '', 'line2': ''}
    noaa19 = {'name': '', 'line1': '', 'line2': ''}

    # make a call to the celestrak website where the TLEs are found
    resp = requests.get('https://www.celestrak.com/NORAD/elements/noaa.txt')

    # parse the response
    resp = resp.text.split('\r\n')
    for (i, line) in enumerate(resp):
        if 'NOAA 15' in line:
            noaa15['name'] = resp[i]
            noaa15['line1'] = resp[i+1]
            noaa15['line2'] = resp[i+2]
        elif 'NOAA 18' in line:
            noaa18['name'] = resp[i]
            noaa18['line1'] = resp[i+1]
            noaa18['line2'] = resp[i+2]
        elif 'NOAA 19' in line:
            noaa19['name'] = resp[i]
            noaa19['line1'] = resp[i+1]
            noaa19['line2'] = resp[i+2]

    # compute the ephem objects using the found TLEs
    noaa15_ephem = ephem.readtle(noaa15['name'], noaa15['line1'], noaa15['line2'])
    noaa18_ephem = ephem.readtle(noaa18['name'], noaa18['line1'], noaa18['line2'])
    noaa19_ephem = ephem.readtle(noaa19['name'], noaa19['line1'], noaa19['line2'])

    return (noaa15_ephem, noaa18_ephem, noaa19_ephem)

# --------------------------------------------------------------------------------------------
def main():
    # get lat and lon if not provided already
    if not args.lat:
        print_smart('Enter your current latitude: ', newline=False)
        lat = input()
    else:
        lat = args.lat
    if not args.lon:
        print_smart('Enter your current longitude: ', newline=False)
        lon = input()
    else:
        lon = args.lon

    # create ground station
    gs = ephem.Observer()
    gs.lat = lat
    gs.lon = lon
    gs.date = datetime.datetime.utcnow()
    
    # create the satellites from TLEs
    sats = create_sats()

    # compute based on gs
    print_smart('Current Look Angles:', log=True)
    for sat in sats:
        sat.compute(gs)
        print_smart('    ' + str(sat.name) + ' alt: ' + str(sat.alt) + ', az: ' + str(sat.az), log=True)

    # next passes
    print_smart('Next Pass Rise Times:', log=True)
    for sat in sats:
        info = gs.next_pass(sat)
        print_smart('    ' + str(sat.name) + ' ' + str(ephem.localtime(info[0])), log=True)

if __name__ == '__main__':
    main()
    sys.exit()
