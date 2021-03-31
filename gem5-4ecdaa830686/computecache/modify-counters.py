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

counter_pairs = {
    'total_instructions': 0,
    'load_instructions': 0,
    'committed_int_instructions': 0,

    'dcache.read_accesses': 0,

    'dcache.arith_add': 0,          # define new counter name 
    'dcache.logic_and': 0,          # define new counter name 
    'dcache.logic_xor': 0,          # define new counter name 

    'L20.read_accesses': 0,

    'L20.arith_add': 0,             # define new counter name
    'L20.logic_and': 0,             # define new counter name 
    'L20.logic_xor': 0,             # define new counter name 

    'L30.read_accesses': 0,

    'L30.arith_add': 0,             # define new counter name
    'L30.logic_and': 0,             # define new counter name
    'L30.logic_xor': 0,             # define new counter name
 
    ### pipeline stage ###
    'rename_reads': 0,
    'rename_writes': 0,
    'inst_window_reads': 0,
    'inst_window_writes': 0,
    'int_regfile_reads': 0,
    'int_regfile_writes': 0,
    'ialu_accesses': 0,
    'ROB_reads': 0,
    'ROB_writes': 0,
}

counterIncrement = {}

def modify_counters(xmlin, counter, xmlout):

    dcache = False
    l2 = False
    l3 = False
    dram = False
    pipeline = False
    L3_en = False

    while True:
        line = counter.readline()
        if not line: break
        fields = line.split()
        if re.match('#',fields[0]): continue
        if fields[1] == '-':
            counterIncrement[fields[0].rstrip(':')] = 0 - long(fields[2])
        else:
            counterIncrement[fields[0].rstrip(':')] = long(fields[2])

    # count all the counters
    counter_pairs['total_instructions'] = counterIncrement['dcache_access'] + counterIncrement['l2_access'] + counterIncrement['l3_access']
    counter_pairs['committed_int_instructions'] = counter_pairs['total_instructions']

    counter_pairs['dcache.read_accesses'] = counterIncrement['dcache_access'] 
    counter_pairs['dcache.arith_add'] = counterIncrement['compute_dcache_arith_add']
    counter_pairs['dcache.logic_and'] = counterIncrement['compute_dcache_logic_and']
    counter_pairs['dcache.logic_xor'] = counterIncrement['compute_dcache_logic_xor']

    counter_pairs['L20.read_accesses'] = counterIncrement['l2_access'] 
    counter_pairs['L20.arith_add'] = counterIncrement['compute_l2_arith_add']
    counter_pairs['L20.logic_and'] = counterIncrement['compute_l2_logic_and']
    counter_pairs['L20.logic_xor'] = counterIncrement['compute_l2_logic_xor']

    counter_pairs['L30.read_accesses'] = counterIncrement['l3_access'] 
    counter_pairs['L30.arith_add'] = counterIncrement['compute_l3_arith_add']
    counter_pairs['L30.logic_and'] = counterIncrement['compute_l3_logic_and']
    counter_pairs['L30.logic_xor'] = counterIncrement['compute_l3_logic_xor']

    if L3_en:
        counter_pairs['L30.arith_add'] += counterIncrement['compute_dram_arith_add']
        counter_pairs['L30.logic_and'] += counterIncrement['compute_dram_logic_and']
        counter_pairs['L30.logic_xor'] += counterIncrement['compute_dram_logic_xor']
    else:
        counter_pairs['L20.arith_add'] += counterIncrement['compute_dram_arith_add']
        counter_pairs['L20.logic_and'] += counterIncrement['compute_dram_logic_and']
        counter_pairs['L20.logic_xor'] += counterIncrement['compute_dram_logic_xor']
    
    counter_pairs['load_instructions'] = counterIncrement['memory_access'] - counterIncrement['dram_access'] 
    counter_pairs['rename_reads'] = counterIncrement['rename_reads']
    counter_pairs['rename_writes'] = counterIncrement['rename_writes']
    counter_pairs['inst_window_reads'] = counterIncrement['inst_window_reads']
    counter_pairs['inst_window_writes'] = counterIncrement['inst_window_writes']
    counter_pairs['int_regfile_reads'] = counterIncrement['int_regfile_reads']
    counter_pairs['int_regfile_writes'] = counterIncrement['int_regfile_writes']
    counter_pairs['ialu_accesses'] = counterIncrement['ialu_accesses']
    counter_pairs['ROB_reads'] = counterIncrement['ROB_reads']
    counter_pairs['ROB_writes'] = counterIncrement['ROB_writes']

    
    dcache = False
    l2 = False
    l3 = False

    print('\n')

    while True:
        line = xmlin.readline()
        if not line: break
        if line == '\n': break
        fields = line.split()
        # </component>
        if len(fields) == 1:
            xmlout.write(line)
            continue
        # <component id="system.core0.dcache" name="dcache">
        if fields[0] == '<component':
            name = eval(fields[2].split('=')[1].rstrip('>'))
            if name == 'dcache':
                dcache = True
                l2 = l3 = False
            elif name == 'L20':
                l2 = True
                dcache = l3 = False
            elif name == 'L30':
                l3 = True
                dcache = l2 = False
            else:
                dcache = l2 = l3 = False
            xmlout.write(line)
            continue

        # compare counter and keys in counter_pairs
        counter_name = eval(fields[1].split('=')[1].rstrip('>'))

        if dcache:
            counter_name = 'dcache' + '.' + counter_name
        elif l2:
            counter_name = 'L20' + '.' + counter_name
        elif l3:
            counter_name = 'L30' + '.' + counter_name

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
            #print(line)
            break
        xmlout.write(line)

        if re.match('dcache.read_accesses', counter_name):
            line.rstrip()
            p = re.compile('read_accesses')
            dcache_add_line = re.sub(p, 'arith_add', line)
            dcache_and_line = re.sub(p, 'logic_and', line)
            dcache_xor_line = re.sub(p, 'logic_xor', line)

            add_value = str(counter_pairs['dcache.arith_add'])
            and_value = str(counter_pairs['dcache.logic_and'])
            xor_value = str(counter_pairs['dcache.logic_xor'])

            p = re.compile(new_value)
            dcache_add_line = re.sub(p, add_value, dcache_add_line)
            xmlout.write(dcache_add_line)
            dcache_and_line = re.sub(p, and_value, dcache_and_line)
            xmlout.write(dcache_and_line)
            dcache_xor_line = re.sub(p, xor_value, dcache_xor_line)
            xmlout.write(dcache_xor_line)

       
        if re.match('L20.read_accesses', counter_name):
            line.rstrip()
            p = re.compile('read_accesses')
            dcache_add_line = re.sub(p, 'arith_add', line)
            dcache_and_line = re.sub(p, 'logic_and', line)
            dcache_xor_line = re.sub(p, 'logic_xor', line)

            add_value = str(counter_pairs['L20.arith_add'])
            and_value = str(counter_pairs['L20.logic_and'])
            xor_value = str(counter_pairs['L20.logic_xor'])

            p = re.compile(new_value)
            dcache_add_line = re.sub(p, add_value, dcache_add_line)
            xmlout.write(dcache_add_line)
            dcache_and_line = re.sub(p, and_value, dcache_and_line)
            xmlout.write(dcache_and_line)
            dcache_xor_line = re.sub(p, xor_value, dcache_xor_line)
            xmlout.write(dcache_xor_line)


        if re.match('L30.read_accesses', counter_name):
            line.rstrip()
            p = re.compile('read_accesses')
            dcache_add_line = re.sub(p, 'arith_add', line)
            dcache_and_line = re.sub(p, 'logic_and', line)
            dcache_xor_line = re.sub(p, 'logic_xor', line)

            add_value = str(counter_pairs['L30.arith_add'])
            and_value = str(counter_pairs['L30.logic_and'])
            xor_value = str(counter_pairs['L30.logic_xor'])

            p = re.compile(new_value)
            dcache_add_line = re.sub(p, add_value, dcache_add_line)
            xmlout.write(dcache_add_line)
            dcache_and_line = re.sub(p, and_value, dcache_and_line)
            xmlout.write(dcache_and_line)
            dcache_xor_line = re.sub(p, xor_value, dcache_xor_line)
            xmlout.write(dcache_xor_line)


def main():
    # Parse options
    usage = ('%prog [OPTION]... XML... FILE')
    parser = optparse.OptionParser(usage=usage)
    parser.add_option(
        '-o',
        dest='outfile',
        default=os.path.join(os.getcwd(), 'mcpat-cim-out.xml'),
        help="output file (default: '%default')")
    parser.add_option(
        '-i',
        dest = 'counterfile',
        default = os.path.join(os.getcwd(), 'counters.out'),
        help = "input file (default: '%default')")
    (options, args) = parser.parse_args()

    # recognize the pattern
    print 'modify counters...',
    with open(args[0], 'r+') as xmlin:
        with open(options.counterfile, 'r+') as counter:
            with open(options.outfile, 'w') as out:
                modify_counters(xmlin, counter, out)


if __name__ == '__main__':
    sys.path.append(os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            '..', 'src', 'python'))
    main()
