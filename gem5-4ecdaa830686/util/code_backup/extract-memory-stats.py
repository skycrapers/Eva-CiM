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


stats_dict = [
    'system.dcache.ReadReq_hits::total',
    'system.dcache.ReadReq_miss_rate::total',
    'system.l2.overall_hits::total',
    'system.l2_overall_miss_rate::total',
    'system.mem_ctrls.num_reads::total',
    'system.mem_ctrls.readReqs',
    'system.cpu.commit.loads',
    'system.cpu.commit.committedInsts',
    'system.cpu.commit.committedOps',
    'system.cpu.commit.int_insts'
]
stats = []



def gene_stage_access(stats, outfile):

    line = None
    fields = None
    statSet = []

    while True:

        line = stats.readline()
        if not line: break
        print line 
        if line == None: continue

        if fields[0].find('---') != -1:
            if fields[1].find('Begin') != -1:
                # a new set of stats
                statSet = []
                continue
            elif fields[1].find('End') != -1:
                # save the current set
                stats.append(statSet)
                continue

        for i in range(len(stats_dict)):
            if fields[0] != stats_dict[i]: continue
            if fields[0] == stats_dict[i]:
                statSet[i] = int(fields[1])

        output.write(set)


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
