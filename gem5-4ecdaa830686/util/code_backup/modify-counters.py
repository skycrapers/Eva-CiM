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

from __future__ import division
import optparse
import os
import sys
import re
import copy

# Temporary storage for instructions. The queue is filled in out-of-order
# until it reaches 'max_threshold' number of instructions. It is then
# sorted out and instructions are printed out until their number drops to
# 'min_threshold'.
# It is assumed that the instructions are not out of order for more then
# 'min_threshold' places - otherwise they will appear out of order.

counter_pairs = {
    'total_instructions': 0,
    'load_instructions': 0,
    'committed_int_instructions': 0,
    'dcache.read_accesses': 0,
    'L20.read_accesses': 0,
    'L30.read_accesses': 0,
    'mc.memory_accesses': 0,
    'mc.memory_reads': 0,
    ### pipeline stage ###
    'rename_reads': 0,
    'rename_writes': 0,
    'inst_window_reads': 0,
    'inst_window_writes': 0,
    'int_regfile_reads': 0,
    'int_regfile_writes': 0,
    'ialu_accesses': 0,
    'ROB_reads': 0
}

pipeline_counters = {
        'rename_reads': 0,
        'rename_writes': 0,
        'inst_window_reads': 0,
        'inst_window_writes': 0,
        'int_regfile_reads': 0,
        'int_regfile_writes': 0,
        'ialu_accesses': 0,
        'ROB_reads': 0
    }

def process_trace(xml, replacement, outfile):

    dcache = False
    l2 = False
    l3 = False
    dram = False
    pipeline = False

    while True:
        line = replacement.readline()
        if not line: break
        if line == '\n': continue
        fields = line.split()
        if fields[0] == 'CiM': continue

        if fields[1] == 'pipeline':
            pipeline = True
            continue

        if pipeline:
            counter = fields[0].rstrip(':')
            value = int(fields[1])
            pipeline_counters[counter] = value

        if len(fields) > 4:
            if fields[0] == 'Saving':
                if fields[1] == 'memory':
                    counter_pairs['load_instructions'] -= int(fields[3].rstrip(','))
                elif fields[1] == 'DCache':
                    counter_pairs['dcache.read_accesses'] -= int(fields[3].rstrip(','))
                    dcache = True
                    l2 = l3 = dram = False
                elif fields[1] == 'L2':
                    counter_pairs['L20.read_accesses'] -= int(fields[3].strip(','))
                    l2 = True
                    dcache = l3 = dram = False
                elif fields[1] == 'L3':
                    counter_pairs['L30.read_accesses'] -= int(fields[3].rstrip(','))
                    l3 = True
                    dcache = l2 = dram = False
                elif fields[1] == 'DRAM':
                    counter_pairs['mc.memory_accesses'] -= int(fields[3].rstrip(','))
                    counter_pairs['mc.memory_reads'] -= int(fields[3].rstrip(','))
                    dram = True
                    dcache = l2 = l3 = False

            elif fields[0] == 'ADD':
                continue

            else:
                if dcache:
                    dcache_alu = (long(fields[0]) +
                                  long(fields[2]) +
                                  long(fields[4]) +
                                  long(fields[6]))
                    counter_pairs['dcache.read_accesses'] += dcache_alu
                elif l2:
                    l2_alu = (long(fields[0]) +
                              long(fields[2]) +
                              long(fields[4]) +
                              long(fields[6]))
                    counter_pairs['L20.read_accesses'] += l2_alu
                elif l3:
                    l3_alu = (long(fields[0]) +
                              long(fields[2]) +
                              long(fields[4]) +
                              long(fields[6]))
                    counter_pairs['L30.read_accesses'] += l3_alu
                elif dram:
                    dram_alu = (long(fields[0]) +
                                long(fields[2]) +
                                long(fields[4]) +
                                long(fields[6]))
                    counter_pairs['mc.memory_accesses'] += dram_alu
                    counter_pairs['mc.memory_reads'] += dram_alu

    # count all the counters
    counter_pairs['total_instructions'] = -(dcache_alu + l2_alu + l3_alu + dram_alu)
    counter_pairs['committed_instructions'] = -(dcache_alu + l2_alu + l3_alu + dram_alu)

    counter_pairs['rename_reads'] = -pipeline_counters['rename_reads']
    counter_pairs['rename_writes'] = -pipeline_counters['rename_writes']
    counter_pairs['inst_window_reads'] = -pipeline_counters['inst_window_reads']
    counter_pairs['inst_window_writes'] = -pipeline_counters['inst_window_writes']
    counter_pairs['int_regfile_reads'] = -pipeline_counters['int_regfile_reads']
    counter_pairs['int_regfile_writes'] = -pipeline_counters['int_regfile_writes']
    counter_pairs['ialu_accesses'] = -pipeline_counters['ialu_accesses']
    counter_pairs['ROB_reads'] = -pipeline_counters['ROB_reads']

    dcache = False
    l2 = False
    l3 = False
    mc = False

    print('\n')

    while True:
        line = xml.readline()
        if not line: break
        if line == '\n': break
        fields = line.split()
        # </component>
        if len(fields) == 1:
            outfile.write(line)
            continue
        # <component id="system.core0.dcache" name="dcache">
        if fields[0] == '<component':
            name = eval(fields[2].split('=')[1].rstrip('>'))
            if name == 'dcache':
                dcache = True
                l2 = l3 = mc = False
            elif name == 'L20':
                l2 = True
                dcache = l3 = mc = False
            elif name == 'L30':
                l3 = True
                dcache = l2 = mc = False
            elif name == 'mc':
                mc = True
                dcache = l2 = l3 = False
            else:
                dcache = l2 = l3 = mc = False
            outfile.write(line)
            continue

        # compare counter and keys in counter_pairs
        counter_name = eval(fields[1].split('=')[1].rstrip('>'))
        if dcache:
            counter_name = 'dcache' + '.' + counter_name
        elif l2:
            counter_name = 'L20' + '.' + counter_name
        elif l3:
            counter_name = 'L30' + '.' + counter_name
        elif mc:
            counter_name = 'mc' + '.' + counter_name

        for key in counter_pairs.keys():
            if counter_name != key:
                continue
            old_value = eval(fields[2].split('=')[1].rstrip('/>'))
            new_value = int(old_value)
            new_value += counter_pairs[key]
            new_value = str(new_value)
            print('old_value = %s, new_value = %s' % (old_value, new_value))
            line.rstrip()
            p = re.compile(old_value)
            line = re.sub(p, new_value, line)
            #line.replace(old_value, str(new_value))
            print(line)
            break

        outfile.write(line)



def main():
    # Parse options
    usage = ('%prog [OPTION]... XML... FILE')
    parser = optparse.OptionParser(usage=usage)
    parser.add_option(
        '-o',
        dest='outfile',
        default=os.path.join(os.getcwd(), 'mcpat-cim-in.xml'),
        help="output file (default: '%default')")
    parser.add_option(
        '-r',
        dest = 'replacementfile',
        default = os.path.join(os.getcwd(), 'replace-results.out'),
        help = "input file (default: '%default')")
    (options, args) = parser.parse_args()

    # recognize the pattern
    print 'parse trace... recognize pattern...',
    with open(args[0], 'r+') as counter:
        with open(options.replacementfile, 'r+') as replacement:
            with open(options.outfile, 'w') as out:
                process_trace(counter, replacement, out)

    print 'done!'


if __name__ == '__main__':
    sys.path.append(os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            '..', 'src', 'python'))
    main()
