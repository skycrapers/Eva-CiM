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
# Authors: Giacomo Gabrielli

# find load-load-op-store pattern for the whole trace

import optparse
import os
import sys
import copy
sys.setrecursionlimit(100000)

# Temporary storage for instructions. The queue is filled in out-of-order
# until it reaches 'max_threshold' number of instructions. It is then
# sorted out and instructions are printed out until their number drops to
# 'min_threshold'.
# It is assumed that the instructions are not out of order for more then
# 'min_threshold' places - otherwise they will appear out of order.


all_access = []
all_request = []


def process_memory_access(request_trace, cache, outfile):

    line = None
    fields = None

    # read all cache access trace, detect key information only for read memory request:
    # (#tick, #hierarchy, #packet, #hit/miss flag)

    # remove the cache hit/miss trace when warmup

    '''line = request_trace.readline()
    fields = line.split()
    warmup_tick = long(fields[0].rstrip(':'))
    print(warmup_tick)'''

    while True:
        access = {
            'tick': 0,
            'level': None,
            'pkt': None,
            'flag': None,
        }
        line = cache.readline()
        if not line: break
        fields = line.split()

        #if long(fields[0].rstrip(':')) < warmup_tick: continue

        if len(fields) == 3:
            access['tick'] = long(fields[0].rstrip(':'))
            access['level'] = (fields[1].split('.')[-1]).rstrip(':')
            access['pkt'] = fields[-1]
            access['flag'] = 'update'
            all_access.append(access)
            continue

        request_type = fields[2]
        if request_type == 'WriteReq': continue
        access['tick'] = long(fields[0].rstrip(':'))
        access['level'] = (fields[1].split('.')[-1]).rstrip(':')
        access['pkt'] = fields[3]
        if (' '.join(fields[4::])).find('miss') == -1:
            access['flag'] = 'hit'
        else:
            access['flag'] = 'miss'

        all_access.append(access)

    print(len(all_access))

    '''for i in range(len(all_access)):
        outfile.write('%s %s %s %s\n' % (
            (str(all_access[i]['tick'])).ljust(15),
            (all_access[i]['level'].ljust(15)),
            (all_access[i]['pkt'].ljust(20)),
            (all_access[i]['flag'].rjust(10))
        ))'''

    last_tick_seq = 0

    outfile.write('%s %s %s %s\n' % (
        "tick".ljust(15),
        "packet".ljust(15),
        "hierarchy".ljust(10),
        "seq_num".rjust(10)
    ))
    outfile.write('\n')

    while True:
        request = {
            'tick': 0,
            'pkt': None,
            'sn': 0,
            'level': None  # L1, L2, L3, DRAM
        }

        line = request_trace.readline()
        if not line: break

        fields = line.split()

        request['tick'] = long(fields[0].rstrip(':'))
        request['pkt'] = fields[3]
        request['sn'] = long((fields[-1].split(':'))[-1].rstrip(']'))

        # find hit/miss information of the current packet
        ini_tick = request['tick']
        i = last_tick_seq - 1
        # record the search sequence numeber

        while i < len(all_access):
            i = i + 1
            if all_access[i]['tick'] < ini_tick: continue
            last_tick_seq = i

            start_ref_address = long(request['pkt'].split(':')[0].strip('['), 16)
            end_ref_address = long(request['pkt'].split(':')[1].strip(']'), 16)

            # address align processing
            if start_ref_address & (~0x3f) != end_ref_address & (~0x3f):
                # data access is divided into two parts
                end_ref_address = (end_ref_address & (~0x3f)) - 1

            # detect the pkt from this tick
            while i < (last_tick_seq+10):

                if all_access[i]['flag'] == 'update':
                    blk_addr = long(all_access[i]['pkt'], 16)
                    if blk_addr == start_ref_address & (~0x3f):
                        request['level'] = all_access[i]['level']
                        break
                    else:
                        i = i + 1
                        continue
                else:
                    start_address = long(all_access[i]['pkt'].split(':')[0].strip('['), 16)
                    end_address = long(all_access[i]['pkt'].split(':')[1].strip(']'), 16)

                    if (start_address <= start_ref_address) and (end_address >= end_ref_address):
                        if all_access[i]['flag'] == 'hit':
                            request['level'] = all_access[i]['level']
                            break
                        elif all_access[i]['level'] == 'l2':
                            request['level'] = 'DRAM'
                            break
                        else:
                            i = i + 1
                    else:
                        i = i + 1
                        continue

            break

        if request['level'] == None: 
            request['level'] = 'DRAM'

        all_request.append(request)
        outfile.write('%s %s %s %s\n' % (
            str(request['tick']).ljust(15),
            (request['pkt'].ljust(15)),
            (request['level']).ljust(10),
            str((request['sn'])).rjust(10)
        ))



def main():
    # Parse options
    usage = ('%prog [OPTION]... REQUEST_PACKET... CACHE_TRACE')
    parser = optparse.OptionParser(usage=usage)
    parser.add_option(
        '-o',
        dest='outfile',
        default=os.path.join(os.getcwd(), 'access.out'),
        help="output file (default: '%default')")
    parser.add_option(
        '--cache',
        dest='cachefile',
        default=os.path.join(os.getcwd(), 'cache.trace'),
        help="cache trace file (default: '%default')")
    (options, args) = parser.parse_args()

    # recognize the pattern
    print 'parse request packet and hit/miss states... ...',
    with open(args[0], 'r') as request:
        with open(options.cachefile, 'r') as cache:
            with open(options.outfile, 'w') as out:
                process_memory_access(request, cache, out)

    print 'done!'


if __name__ == '__main__':
    sys.path.append(os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            '..', 'src', 'python'))
    main()
