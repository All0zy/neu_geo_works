"""
 static test for PPP (IGS)
"""
from copy import deepcopy
import matplotlib.pyplot as plt
import matplotlib.dates as md
import numpy as np
from os.path import exists
from sys import stdout, exit
import csv
from datetime import datetime

import gnss as gn
from gnss import ecef2pos, Nav
from gnss import time2doy, time2str, timediff, epoch2time, sat2prn, time2epoch
from gnss import rSigRnx, uGNSS
from gnss import sys2str
from peph import atxdec, searchpcv
from peph import peph, biasdec
from pppssr import pppos
from rinex import rnxdec

# Start epoch and number of epochs

ep = [2026, 2, 22, 0, 0, 0]
let = 'Y'
xyz_ref = [-2994429.4511, 4951309.9057, 2674497.1692]

time = epoch2time(ep)
year = ep[0]
doy = int(time2doy(time))

nep = 1440

pos_ref = ecef2pos(xyz_ref)

navfile = '../hkcl/COD0MGXFIN_20260170000_01D_30S_ATT.OBX'
obsfile = '../hkcl/HKCL00HKG_R_20260170000_01D_CN.rnx'

# ac = 'COD0OPSFIN'
ac = 'COD0MGXFIN'

# Function to count satellites by system
def count_sat_by_system(sat_array):
    """
    Count satellites by GNSS system
    Returns: (n_gps, n_gal, n_bds)
    """
    n_gps = 0
    n_gal = 0
    n_bds = 0
    
    for sat in sat_array:
        sys, prn = sat2prn(sat)
        if sys == uGNSS.GPS:
            n_gps += 1
        elif sys == uGNSS.GAL:
            n_gal += 1
        elif sys == uGNSS.BDS:
            n_bds += 1
    
    return n_gps, n_gal, n_bds

orbfile = '../hkcl/COD0MGXFIN_20260170000_01D_05M_ORB.SP3'

clkfile = '../hkcl/COD0MGXFIN_20260170000_01D_30S_CLK.CLK'

bsxfile = '../hkcl/COD0MGXFIN_20260170000_01D_01D_OSB.BIA'

if not exists(clkfile):
    orbfile = orbfile.replace('COD0OPSFIN', 'COD0OPSRAP')
    clkfile = clkfile.replace('COD0OPSFIN', 'COD0OPSRAP')
    bsxfile = bsxfile.replace('COD0OPSFIN', 'COD0OPSRAP')
if not exists(orbfile):
    orbfile = orbfile.replace('_05M_', '_15M_')

# Define signals to be processed

gnss = "GCE"
sigs = []
if 'G' in gnss:
    sigs.extend([rSigRnx("GC1C"), rSigRnx("GC2W"),
                 rSigRnx("GL1C"), rSigRnx("GL2W"),
                 rSigRnx("GS1C"), rSigRnx("GS2W")])
if 'E' in gnss:
    sigs.extend([rSigRnx("EC1C"), rSigRnx("EC5Q"),
                 rSigRnx("EL1C"), rSigRnx("EL5Q"),
                 rSigRnx("ES1C"), rSigRnx("ES5Q")])
if 'C' in gnss:
    sigs.extend([rSigRnx("CC2I"), rSigRnx("CC6I"),
                 rSigRnx("CL2I"), rSigRnx("CL6I"),
                 rSigRnx("CS2I"), rSigRnx("CS6I")])

rnx = rnxdec()
rnx.setSignals(sigs)

nav = Nav()
orb = peph()

# Positioning mode
# 0:static, 1:kinematic
#
nav.pmode = 0

# Decode RINEX NAV data
#
nav = rnx.decode_nav(navfile, nav)

# Load precise orbits and clock offsets
#
nav = orb.parse_sp3(orbfile, nav)
nav = rnx.decode_clk(clkfile, nav)

# Load code and phase biases from Bias-SINEX
#
bsx = biasdec()
bsx.parse(bsxfile)

# Load ANTEX data for satellites and stations
#
if time > epoch2time([2022, 11, 27, 0, 0, 0]):
    atxfile = '../data/I20.ATX'
elif time > epoch2time([2021, 5, 2, 0, 0, 0]):
    atxfile = '../data/M20.ATX'
else:
    atxfile = '../data/M14.ATX'

atx = atxdec()
atx.readpcv(atxfile)

# Intialize data structures for results
#
t = np.zeros(nep)
enu = np.ones((nep, 3))*np.nan
sol = np.zeros((nep, 4))
ztd = np.zeros((nep, 1))
smode = np.zeros(nep, dtype=int)

# Logging level
#
nav.monlevel = 1  # TODO: enabled for testing!

# Load RINEX OBS file header
#
if rnx.decode_obsh(obsfile) >= 0:

    # Auto-substitute signals
    #
    rnx.autoSubstituteSignals()

    # Initialize position
    #
    ppp = pppos(nav, rnx.pos, 'test_pppigs.log')
    nav.ephopt = 4  # IGS
    nav.armode = 3

    # 禁用C/N0检查，因为RINEX文件中No signal strength data
    nav.cnr_min = 0.0
    nav.cnr_min_gpy = 0.0
    
    nav.elmin = np.deg2rad(5.0)
    nav.thresar = 2.0

    # Get equipment information
    #
    nav.fout.write("FileName: {}\n".format(obsfile))
    nav.fout.write("Start   : {}\n".format(time2str(rnx.ts)))
    if rnx.te is not None:
        nav.fout.write("End     : {}\n".format(time2str(rnx.te)))
    nav.fout.write("Receiver: {}\n".format(rnx.rcv))
    nav.fout.write("Antenna : {}\n".format(rnx.ant))
    nav.fout.write("\n")

    if 'UNKNOWN' in rnx.ant or rnx.ant.strip() == "":
        nav.fout.write("ERROR: missing antenna type in RINEX OBS header!\n")

    # Set PCO/PCV information
    #
    nav.sat_ant = atx.pcvs
    nav.rcv_ant = searchpcv(atx.pcvr, rnx.ant,  rnx.ts)
    if nav.rcv_ant is None:
        nav.fout.write("ERROR: missing antenna type <{}> in ANTEX file!\n"
                       .format(rnx.ant))

    # Print available signals
    #
    nav.fout.write("Available signals\n")
    for sys, sigs in rnx.sig_map.items():
        txt = "{:7s} {}\n".format(sys2str(sys),
                                  ' '.join([sig.str() for sig in sigs.values()]))
        nav.fout.write(txt)
    nav.fout.write("\n")

    nav.fout.write("Selected signals\n")
    for sys, tmp in rnx.sig_tab.items():
        txt = "{:7s} ".format(sys2str(sys))
        for _, sigs in tmp.items():
            txt += "{} ".format(' '.join([sig.str() for sig in sigs]))
        nav.fout.write(txt+"\n")
    nav.fout.write("\n")

    # Skip epochs until start time
    #
    obs = rnx.decode_obs()
    while time > obs.t and obs.t.time != 0:
        obs = rnx.decode_obs()

    # Open CSV file for results
    #
    csv_filename = 'test_pppigs_results.csv'
    csv_file = open(csv_filename, 'w', newline='')
    csv_writer = csv.writer(csv_file)
    
    # Write CSV header
    csv_writer.writerow(['Date', 'Time', 'ECEF_X(m)', 'ECEF_Y(m)', 'ECEF_Z(m)',
                         'East(m)', 'North(m)', 'Up(m)', 'Horizontal_2D(m)',
                         'Mode', 'Total_Satellites', 'GPS_Count', 'Galileo_Count', 'BDS_Count'])
    
    # Loop over number of epoch from file start
    #
    for ne in range(nep):

        # Set initial epoch
        #
        if ne == 0:
            nav.t = deepcopy(obs.t)
            t0 = deepcopy(obs.t)

        # Call PPP module with IGS products
        #
        ppp.process(obs, orb=orb, bsx=bsx)

        # Save output
        #
        t[ne] = timediff(nav.t, t0)/86400.0

        sol = nav.xa[0:3] if nav.smode == 4 else nav.x[0:3]
        enu[ne, :] = gn.ecef2enu(pos_ref, sol-xyz_ref)

        ztd[ne] = nav.xa[ppp.IT(nav.na)] \
            if nav.smode == 4 else nav.x[ppp.IT(nav.na)]
        smode[ne] = nav.smode

        nav.fout.write("{} {:14.4f} {:14.4f} {:14.4f} "
                       "ENU {:7.3f} {:7.3f} {:7.3f}, 2D {:6.3f}, mode {:1d}\n"
                       .format(time2str(obs.t),
                               sol[0], sol[1], sol[2],
                               enu[ne, 0], enu[ne, 1], enu[ne, 2],
                               np.sqrt(enu[ne, 0]**2+enu[ne, 1]**2),
                               smode[ne]))

        # Count satellites by system for CSV output
        n_gps, n_gal, n_bds = count_sat_by_system(obs.sat)
        total_sat = len(obs.sat)
        
        # Convert GPS time to epoch and extract date/time
        utc_time = time2epoch(obs.t)
        date_str = '{:04d}-{:02d}-{:02d}'.format(int(utc_time[0]), int(utc_time[1]), int(utc_time[2]))
        time_str = '{:02d}:{:02d}:{:05.2f}'.format(int(utc_time[3]), int(utc_time[4]), utc_time[5])
        
        # Write to CSV file
        horizontal_2d = np.sqrt(enu[ne, 0]**2 + enu[ne, 1]**2)
        csv_writer.writerow([date_str, time_str, 
                            f'{sol[0]:.4f}', f'{sol[1]:.4f}', f'{sol[2]:.4f}',
                            f'{enu[ne, 0]:.3f}', f'{enu[ne, 1]:.3f}', f'{enu[ne, 2]:.3f}',
                            f'{horizontal_2d:.3f}', 
                            smode[ne], total_sat, n_gps, n_gal, n_bds])

        # Log to standard output
        #
        stdout.write('\r {} ENU {:7.3f} {:7.3f} {:7.3f}, 2D {:6.3f}, mode {:1d}'
                     .format(time2str(obs.t),
                             enu[ne, 0], enu[ne, 1], enu[ne, 2],
                             np.sqrt(enu[ne, 0]**2+enu[ne, 1]**2),
                             smode[ne]))

        # Get new epoch, exit after last epoch
        #
        obs = rnx.decode_obs()
        if obs.t.time == 0:
            break

    # Send line-break to stdout
    #
    stdout.write('\n')

    # Close RINEX observation file
    #
    rnx.fobs.close()

    # Close output files
    #
    if nav.fout is not None:
        nav.fout.close()
    
    csv_file.close()
    print(f'\nCSV results saved to: {csv_filename}')

fig_type = 1
ylim = 1.0

idx4 = np.where(smode == 4)[0]
idx5 = np.where(smode == 5)[0]
idx0 = np.where(smode == 0)[0]

fig = plt.figure(figsize=[7, 9])
fig.set_rasterized(True)

fmt = '%H:%M'

if fig_type == 1:

    lbl_t = ['East [m]', 'North [m]', 'Up [m]']

    for k in range(3):
        plt.subplot(4, 1, k+1)
        plt.plot(t[idx0], enu[idx0, k], 'r.')
        plt.plot(t[idx5], enu[idx5, k], 'y.')
        plt.plot(t[idx4], enu[idx4, k], 'g.')

        plt.ylabel(lbl_t[k])
        plt.grid()
        plt.ylim([-ylim, ylim])
        plt.gca().xaxis.set_major_formatter(md.DateFormatter(fmt))

    plt.subplot(4, 1, 4)
    plt.plot(t[idx0], ztd[idx0]*1e2, 'r.', markersize=8, label='none')
    plt.plot(t[idx5], ztd[idx5]*1e2, 'y.', markersize=8, label='float')
    plt.plot(t[idx4], ztd[idx4]*1e2, 'g.', markersize=8, label='fix')
    plt.ylabel('ZTD [cm]')
    plt.grid()
    plt.gca().xaxis.set_major_formatter(md.DateFormatter(fmt))

    plt.xlabel('Time [HH:MM]')
    plt.legend()

elif fig_type == 2:

    ax = fig.add_subplot(111)

    # plt.plot(enu[idx0, 0], enu[idx0, 1], 'r.', label='stdpos')
    plt.plot(enu[idx5, 0], enu[idx5, 1], 'y.', label='float')
    plt.plot(enu[idx4, 0], enu[idx4, 1], 'g.', label='fix')

    plt.xlabel('Easting [m]')
    plt.ylabel('Northing [m]')
    plt.grid()
    plt.axis('equal')
    plt.legend()
    # ax.set(xlim=(-ylim, ylim), ylim=(-ylim, ylim))

plotFileFormat = 'png'
plotFileName = '.'.join(('test_pppigs', plotFileFormat))

plt.savefig(plotFileName, format=plotFileFormat, bbox_inches='tight', dpi=300)
plt.show()
