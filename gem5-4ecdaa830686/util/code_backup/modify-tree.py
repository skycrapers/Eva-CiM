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
import copy

# Temporary storage for instructions. The queue is filled in out-of-order
# until it reaches 'max_threshold' number of instructions. It is then
# sorted out and instructions are printed out until their number drops to
# 'min_threshold'.
# It is assumed that the instructions are not out of order for more then
# 'min_threshold' places - otherwise they will appear out of order.

memoryview = []

def process_trace(tree, access, outfile):

    while True:
        line = access.readline()
        if not line: break
        if line == '\n': continue
        memory_access = {
            'seq': None,
            'level': None
        }
        # extract the hierarchy where CiM operations occur
        fields = line.split()
        if fields[0] == 'tick': continue
        memory_access['seq'] = fields[-1]
        memory_access['level'] = fields[2]
        memoryview.append(memory_access)


    while True:
        line = tree.readline()
        if not line: break
        # append memory access information after all load instructions
        fields = line.split()
        if len(fields) == 1:
            outfile.write(line)
            continue
        if fields[0].find('ldr') == -1:
            outfile.write(line)
            continue
        seq_num = fields[-1]
        find = False
        for i in range(len(memoryview)):
            if memoryview[i]['seq'] == seq_num:
                print(seq_num)
                line = line.rstrip('\n') + '    ' + memoryview[i]['level'] + '\n'
                outfile.write(line)
                find = True
                break
        if find == False:
            line = line.rstrip('\n') + '    ' + 'DRAM' + '\n'
            outfile.write(line)


def main():
    # Parse options
    usage = ('%prog [OPTION]... TREE_FILE ')
    parser = optparse.OptionParser(usage=usage)
    parser.add_option(
        '-o',
        dest='outfile',
        default=os.path.join(os.getcwd(), 'tree-memoryaccess.out'),
        help="output file (default: '%default')")
    parser.add_option(
        '-a',
        dest = 'accessfile',
        default = os.path.join(os.getcwd(), 'access.out'),
        help = "input file (default: '%default')")
    (options, args) = parser.parse_args()

    # recognize the pattern
    print 'modify tree with memory access trace...',
    with open(args[0], 'r') as tree:
        with open(options.accessfile, 'r') as access:
            with open(options.outfile, 'w') as out:
                process_trace(tree, access, out)

    print 'done!'


if __name__ == '__main__':
    sys.path.append(os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            '..', 'src', 'python'))
    main()
