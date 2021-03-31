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


def gene_stage_access(stats, rate, outfile):

    access_data = np.load(stats)
    rate_data = np.load(rate)
    print access_data
    print rate_data
    print '\n'

    tick = access_data[0:,0]
    sim_insts = access_data[0:,1]
    dcache_hits = access_data[0:,2]
    l2_hits = access_data[0:,3]
    dram_reads = access_data[0:,4]
    dcache_miss_rate = rate_data[0:,0]
    l2_miss_rate = rate_data[0:,1]

    dcache_max = dcache_hits.argmax(axis=0)
    print 'dcache max access: ' + '%s: %s' % (tick[dcache_max], dcache_hits.max(axis=0))
    print 'sim_insts increment: ' + '%s ~ %s\n' % (sim_insts[dcache_max-1], sim_insts[dcache_max])

    l2_max = l2_hits.argmax(axis=0)
    print 'l2 max access: ' + '%s: %s' % (tick[l2_max], l2_hits.max(axis=0))
    print 'sim_insts increment: ' + '%s ~ %s\n' % (sim_insts[l2_max-1], sim_insts[l2_max])

    dram_max = dram_reads.argmax(axis=0)
    print 'dram max reads: ' + '%s: %s\n' % (tick[dram_max], dram_reads.max(axis=0))

    dcache_max_miss = dcache_miss_rate.argmax(axis=0)
    print 'dcache max miss: ' + '%s: %s' % (tick[dcache_max_miss], dcache_miss_rate.max(axis=0))
    print 'sim_insts increment: ' + '%s ~ %s\n' % (sim_insts[dcache_max_miss-1], sim_insts[dcache_max_miss])

    l2_max_miss = l2_miss_rate.argmax(axis=0)
    print 'l2 max miss: ' + '%s: %s' % (tick[l2_max_miss], l2_miss_rate.max(axis=0))
    print 'sim_insts increment: ' + '%s ~ %s\n' % (sim_insts[l2_max_miss-1], sim_insts[l2_max_miss])

    dcache_min_miss = dcache_miss_rate.argmin(axis=0)
    print 'dcache min miss: ' + '%s: %s' % (tick[dcache_min_miss], dcache_miss_rate.min(axis=0))
    print 'sim_insts increment: ' + '%s ~ %s\n' % (sim_insts[dcache_min_miss-1], sim_insts[dcache_min_miss])

    l2_min_miss = l2_miss_rate.argmin(axis=0)
    print 'l2 min miss: ' + '%s: %s' % (tick[l2_min_miss], l2_miss_rate.min(axis=0))
    print 'sim_insts increment: ' + '%s ~ %s' % (sim_insts[l2_min_miss-1], sim_insts[l2_min_miss])

    ax1 = plt.subplot(411)
    ax1.plot(dcache_hits, 'b')
    ax1.set_ylabel('dcache hits')

    ax2 = plt.subplot(412)
    ax2.plot(dcache_miss_rate, 'y')
    ax2.set_ylabel('dcache miss rates')

    ax3 = plt.subplot(413)
    ax3.plot(l2_hits, 'b')
    ax3.set_ylabel('l2 hits')

    ax4 = plt.subplot(414)
    ax4.plot(l2_miss_rate, 'y')
    ax4.set_ylabel('l2 miss rates')
    ax4.set_xlabel('time (0.1ms/point) ')

    plt.savefig('results.png')
    plt.show()


def main():
    # Parse options
    usage = ('%prog [OPTION]... STATS...FILE... RATE...FILE')
    parser = optparse.OptionParser(usage=usage)
    parser.add_option(
        '-o',
        dest='outfile',
        default=os.path.join(os.getcwd(), 'sample.txt'),
        help="output file (default: '%default')")

    (options, args) = parser.parse_args()

    # recognize the pattern
    print
    'parse request packet and hit/miss states... ...',
    with open(args[0], 'r') as stats:
        with open(args[1], 'r') as rate:
            with open(options.outfile, 'w') as out:
                gene_stage_access(stats, rate, out)

    print
    'done!'


if __name__ == '__main__':
    sys.path.append(os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        '..', 'src', 'python'))
    main()
