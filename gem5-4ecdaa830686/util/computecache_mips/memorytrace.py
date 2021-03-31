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
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOTd
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

seqrequest = {}  # {'sn':'level', ....}
all_access = []

requestout = open('request.out', 'w')
#accessout = open('access.out', 'w')

def process_memory_access(requestProbe, accessProbe):

    line = None
    fields = None
    global all_access

    # read all cache access trace, detect key information only for read memory request:
    # (#tick, #hierarchy, #packet, #hit/miss flag)
    for i in range(len(accessProbe)):
        access = {
            'tick': 0,
            'level': None,
            'pkt': None,
            'flag': None,
        }
        fields = accessProbe[i].split()

        if len(fields) == 4:
            access['tick'] = long(fields[0].rstrip(':'))
            access['level'] = (fields[1].split('.')[-1]).rstrip(':')
            access['pkt'] = fields[-1]
            access['flag'] = 'update'
            all_access.append(access)
            continue

        request_type = fields[3]
        if request_type == 'WriteReq': continue
        access['tick'] = long(fields[0].rstrip(':'))
        access['level'] = (fields[1].split('.')[-1]).rstrip(':')
        access['pkt'] = fields[4]
        if (' '.join(fields[5::])).find('miss') == -1:
            access['flag'] = 'hit'
        else:
            access['flag'] = 'miss'

        '''accessout.write('%s %s\n' % (
            str(access['level']).ljust(15),
            access['flag'].ljust(10)
            ))'''

        all_access.append(access)
    
    last_tick_seq = 0
    global seqrequest

    for i in range(len(requestProbe)):
        request = {
            'tick': 0,
            'pkt': None,
            'sn': 0,
            'level': None  # L1, L2, L3, DRAM
        }

        fields = requestProbe[i].split()

        request['tick'] = long(fields[0].rstrip(':'))
        request['pkt'] = fields[4]
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
                            request['level'] = 'dram'
                            break
                        else:
                            i = i + 1
                    else:
                        i = i + 1
                        continue

            break

        if request['level'] == None: 
            request['level'] = 'dram'

        seqrequest[str(request['sn'])] = request['level']

        requestout.write('%s %s\n' % (
            str(request['sn']).ljust(15),
            request['level'].ljust(10)
            ))


    '''cachetrace = open(cachefile, 'r')
    requesttrace = open(requestfile, 'r')

    while True:
        access = {
            'tick': 0,
            'level': None,
            'pkt': None,
            'flag': None,
        }
        line = cachetrace.readline()
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

    last_tick_seq = 0


    global seqrequest

    while True:
        request = {
            'tick': 0,
            'pkt': None,
            'sn': 0,
            'level': None  # L1, L2, L3, DRAM
        }

        line = requesttrace.readline()
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
                            request['level'] = 'dram'
                            break
                        else:
                            i = i + 1
                    else:
                        i = i + 1
                        continue

            break

        if request['level'] == None: 
            request['level'] = 'dram'


        requestout.write('%s %s %s %s\n' % (
            str(request['tick']).ljust(15),
            (request['pkt'].ljust(15)),
            (request['level']).ljust(10),
            str((request['sn'])).rjust(10)
        ))

        #seqrequest.append(request)
        # seqrequest: turn list type into dict type for quick lookup
        seqrequest[str(request['sn'])] = request['level']
        requestout.write('%s %s\n' % (
            str(request['sn']).ljust(15),
            request['level'].ljust(10)
            ))'''
