#! /usr/bin/env python2

# Copyright (c) 2011 ARM Limited
# All rights reserved
#
# The license below extends only to copyright in the software and shall
# not be construed as granting a license to any other intellectual
# property including but not limited to intellectual property relating
# to a hardware implementation of the functionality of the software
# licensed hereunder.  You may use the software subject to the license
# terms below provided that you ensure that this notice is replicated
# unmodified and in its entirety in all distributions of the software,
# modified or unmodified, in source code or in binary form.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met: redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer;
# redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution;
# neither the name of the copyright holders nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# Authors: Di Gao

import optparse
import os
import sys
import copy
import numpy as np
from numpy import *
np.seterr(divide='ignore',invalid='ignore')
import matplotlib.pyplot as plt
from matplotlib import rc


stats_dict = [
    'system.cpu.dcache.ReadReq_hits::total',
    'system.cpu.dcache.ReadReq_miss_rate::total',
    'system.l2.overall_hits::total',
    'system.l2.overall_miss_rate::total',
    'system.mem_ctrls.num_reads::total',
    'system.mem_ctrls.readReqs'

]


def gene_stage_access(stats, outfile):

    line = None
    fields = None
    statSet = {
        'final_tick':0,
        'sim_insts':0,
        'system.cpu.dcache.ReadReq_hits::total': 0,
        'system.cpu.dcache.ReadReq_miss_rate::total': 0,
        'system.l2.overall_hits::total': 0,
        'system.l2.overall_miss_rate::total': 0,
        'system.mem_ctrls.num_reads::total': 0,
        'system.mem_ctrls.readReqs': 0
    }
    length = 0 
    statsList = np.empty(shape=[5,0], dtype=int64)
    rateList = np.empty(shape=[2,0], dtype=float64)

    while True:

        line = stats.readline()
        if not line: break
        if line == '\n': continue
        fields = line.split()

        if fields[0].find('---') != -1:
            if fields[1].find('Begin') != -1:
                statSet = {
                    'final_tick':0,
                    'sim_insts':0,
                    'system.cpu.dcache.ReadReq_hits::total': 0,
                    'system.cpu.dcache.ReadReq_miss_rate::total': 0,
                    'system.l2.overall_hits::total': 0,
                    'system.l2.overall_miss_rate::total': 0,
                    'system.mem_ctrls.num_reads::total': 0,
                    'system.mem_ctrls.readReqs': 0
                }      
                continue
            if fields[1].find('End') != -1:
                # save the current set
                outfile.write('%s %s %s %s %s %s %s %s\n' % (
                str(statSet['final_tick']),
                str(statSet['sim_insts']),
                str(statSet['system.cpu.dcache.ReadReq_hits::total']),
                str(statSet['system.cpu.dcache.ReadReq_miss_rate::total']),
                str(statSet['system.l2.overall_hits::total']),
                str(statSet['system.l2.overall_miss_rate::total']),
                str(statSet['system.mem_ctrls.num_reads::total']),
                str(statSet['system.mem_ctrls.readReqs'])
                ))
                curStats = np.array([
                    statSet['final_tick'],
                    statSet['sim_insts'],
                    statSet['system.cpu.dcache.ReadReq_hits::total'],
                    statSet['system.l2.overall_hits::total'],
                    statSet['system.mem_ctrls.num_reads::total'],
                    #statSet['system.mem_ctrls.readReqs']
                ])
                curRate = np.array([
                    statSet['system.cpu.dcache.ReadReq_miss_rate::total'],
                    statSet['system.l2.overall_miss_rate::total']
                    ])
                length += 1

                statsList = np.c_[statsList, curStats]
                rateList = np.c_[rateList, curRate]

                del statSet
                continue


        name = fields[0]

        if name == 'final_tick':
            statSet['final_tick'] = long(fields[1])
            continue
        if name == 'sim_insts':
            statSet['sim_insts'] = long(fields[1])
        #print name
        elif name == stats_dict[0]:
            statSet['system.cpu.dcache.ReadReq_hits::total'] = long(fields[1])
        elif name == stats_dict[1]:
            statSet['system.cpu.dcache.ReadReq_miss_rate::total'] = float(fields[1])
        elif name == stats_dict[2]:
            statSet['system.l2.overall_hits::total'] = long(fields[1])
        elif name == stats_dict[3]:
            statSet['system.l2.overall_miss_rate::total'] = float(fields[1])
        elif name == stats_dict[4]:
            statSet['system.mem_ctrls.num_reads::total'] = long(fields[1])
        elif name == stats_dict[5]:
            statSet['system.mem_ctrls.readReqs'] = long(fields[1])


    print type(statsList)
    print statsList.dtype

    print statsList.shape


    np.save('bzip2.npy', statsList.T)
    np.save('bzip2_.npy', rateList.T)

  


def main():
    # Parse options
    usage = ('%prog [OPTION]... STATS_FILE')
    parser = optparse.OptionParser(usage=usage)
    parser.add_option(
        '-o',
        dest='outfile',
        default=os.path.join(os.getcwd(), 'memoryStat.out'),
        help="output file (default: '%default')")

    (options, args) = parser.parse_args()

    # recognize the pattern
    print
    'parse request packet and hit/miss states... ...',
    with open(args[0], 'r') as stats:
        with open(options.outfile, 'w') as out:
            gene_stage_access(stats, out)

    print
    'done!'


if __name__ == '__main__':
    sys.path.append(os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        '..', 'src', 'python'))
    main()
