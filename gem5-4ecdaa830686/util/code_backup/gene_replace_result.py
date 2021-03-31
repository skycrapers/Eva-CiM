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



def process_trace(tree, trace, pipeline, outfile):


    add_num = 0
    sub_num = 0
    and_num = 0
    or_num = 0
    ldr_num = 0
    l1_num = {
        'add': 0,
        'sub': 0,
        'and': 0,
        'or': 0,
        'other': 0
    }
    l2_num = {
        'add': 0,
        'sub': 0,
        'and': 0,
        'or': 0,
        'other': 0
    }
    l3_num = {
        'add': 0,
        'sub': 0,
        'and': 0,
        'or': 0,
        'other': 0
    }
    dram_num = {
        'add': 0,
        'sub': 0,
        'and': 0,
        'or': 0,
        'other': 0
    }

    while True:

        line = trace.readline()
        if not line: break

        # parse current instruction, find the opcode, source and destination
        # operands, check whether the opcode is the CiM operaiton type
        fields = line.split()
        if fields[0].find('add') != -1: add_num += 1
        elif fields[0].find('sub') != -1: sub_num += 1
        elif fields[0].find('and') != -1: and_num += 1
        elif fields[0].find('or') != -1: or_num += 1
        elif fields[0].find('ldr') != -1: ldr_num += 1
        else: continue


    outfile.write('\nCiM type (add, sub, mul, cmp) instructions: #' + str(add_num+sub_num+and_num+or_num) + '\n')
    outfile.write('ADD instructions: #' + str(add_num) + '\n')
    outfile.write('SUB instructions: #' + str(sub_num) + '\n')
    outfile.write('AND instructions: #' + str(and_num) + '\n')
    outfile.write('OR instructions: #' + str(or_num) + '\n')
    outfile.write('read memory instructions: #' + str(ldr_num) + '\n\n')

    replace_l1_num = 0
    replace_l2_num = 0
    replace_l3_num = 0
    replace_dram_num = 0
    L1_exe = True
    L2_exe = False
    L3_exe = False
    DRAM_exe = False

    ################### pipeline counter quantity with CiM replacement ####################
    '''
    rename stage: 'rename_reads', 'rename_writes'
    issue stage: 'inst_window_reads', 'inst_window_writes'
    IEW stage: 'int_regfile_reads', 'int_regfile_writes', 'ialu_accesses'
    commit stage: 'ROB_reads'
    '''
    pipestage = {'': [0, 0, 0, 0, 0, 0, 0, 0]}
    while True:
        line = pipeline.readline()
        if not line: break
        if line == "\n": continue
        fields = line.split()
        sn = fields[-1].split(':')[-1].rstrip(']')
        if pipestage.has_key(sn):
            unit = fields[2].rstrip(':')
            if unit == 'rename_reads':
                pipestage[sn][0] += 1
            elif unit == 'rename_writes':
                pipestage[cn][1] += 1
            elif unit == 'inst_window_reads':
                pipestage[sn][2] += 1
            elif unit == 'inst_window_writes':
                pipestage[sn][3] += 1
            elif unit == 'int_regfile_reads':
                pipestage[sn][4] += 1
            elif unit == 'int_regfile_writes':
                pipestage[sn][5] += 1
            elif unit == 'ialu_accesses':
                pipestage[sn][6] += 1
            elif unit == 'ROB_reads':
                pipestage[sn][7] += 1
        else:
            sn = fields[-1].split(':')[-1].rstrip(']')
            pipestage[sn] = [0, 0, 0, 0, 0, 0, 0, 0]
            unit = fields[2].rstrip(':')
            if unit == 'rename_reads':
                pipestage[sn][0] += 1
            elif unit == 'rename_writes':
                pipestage[cn][1] += 1
            elif unit == 'inst_window_reads':
                pipestage[sn][2] += 1
            elif unit == 'inst_window_writes':
                pipestage[sn][3] += 1
            elif unit == 'int_regfile_reads':
                pipestage[sn][4] += 1
            elif unit == 'int_regfile_writes':
                pipestage[sn][5] += 1
            elif unit == 'ialu_accesses':
                pipestage[sn][6] += 1
            elif unit == 'ROB_reads':
                pipestage[sn][7] += 1


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

    while True:
        line = tree.readline()
        if not line: break
        if line == "\n": continue
        if line[0] == '#': continue
        # parse current instruction, find the opcode, source and destination
        # operands, check whether the opcode is the CiM operaiton type
        fields = line.split()


        if fields[0].find('add') != -1 or \
            fields[0].find('sub') != -1 or \
            fields[0].find('and') != -1 or \
            fields[0].find('or') != -1 or \
            fields[0].find('ldr') != -1:

            if fields[-1] == 'DRAM' or fields[-1] == 'dcache' or fields[-1] == 'l2' or fields[-1] == 'l3' :
                seqNum = fields[-2]
            else:
                seqNum = fields[-1]
            if pipestage.has_key(seqNum):
                pipeline_counters['rename_reads'] += pipestage[seqNum][0]
                pipeline_counters['rename_writes'] += pipestage[seqNum][1]
                pipeline_counters['inst_window_reads'] += pipestage[seqNum][2]
                pipeline_counters['inst_window_writes'] += pipestage[seqNum][3]
                pipeline_counters['int_regfile_reads'] += pipestage[seqNum][4]
                pipeline_counters['int_regfile_writes'] += pipestage[seqNum][5]
                pipeline_counters['ialu_accesses'] += pipestage[seqNum][6]
                pipeline_counters['ROB_reads'] += pipestage[seqNum][7]

        if L1_exe:
            if fields[0].find('add') != -1: l1_num['add'] += 1
            elif fields[0].find('sub') != -1: l1_num['sub'] += 1
            elif fields[0].find('and') != -1: l1_num['and'] += 1
            elif fields[0].find('or') != -1: l1_num['or'] += 1
            elif fields[0].find('ldr') != -1:
                if fields[-1] == 'l2':
                    L2_exe = True
                    replace_l2_num += 1
                    L1_exe = L3_exe = DRAM_exe = False
                elif fields[-1] == 'l3':
                    L3_exe = True
                    replace_l3_num += 1
                    L1_exe = L2_exe = DRAM_exe = False
                elif fields[-1] == 'DRAM':
                    DRAM_exe = True
                    replace_dram_num += 1
                    L1_exe = L2_exe = L3_exe = False
                else:
                    replace_l1_num += 1
            else: l1_num['other'] += 1

        elif L2_exe:
            if fields[0].find('add') != -1: l2_num['add'] += 1
            elif fields[0].find('sub') != -1: l2_num['sub'] += 1
            elif fields[0].find('and') != -1: l2_num['and'] += 1
            elif fields[0].find('or') != -1: l2_num['or'] += 1
            elif fields[0].find('ldr') != -1:
                if fields[-1] == 'dcache':
                    L1_exe = True
                    replace_l1_num += 1
                    L2_exe = L3_exe = DRAM_exe = False
                elif fields[-1] == 'l3':
                    L3_exe = True
                    replace_l3_num += 1
                    L1_exe = L2_exe = DRAM_exe = False
                elif fields[-1] == 'DRAM':
                    DRAM_exe = True
                    replace_dram_num += 1
                    L1_exe = L2_exe = L3_exe = False
                else:
                    replace_l2_num += 1
            else: l2_num['other'] += 1

        elif L3_exe:
            if fields[0].find('add') != -1: l3_num['add'] += 1
            elif fields[0].find('sub') != -1: l3_num['sub'] += 1
            elif fields[0].find('and') != -1: l3_num['and'] += 1
            elif fields[0].find('or') != -1: l3_num['or'] += 1
            elif fields[0].find('ldr') != -1:
                if fields[-1] == 'dcache':
                    L1_exe = True
                    replace_l1_num += 1
                    L2_exe = L3_exe = DRAM_exe = False
                elif fields[-1] == 'l2':
                    L2_exe = True
                    replace_l2_num += 1
                    L1_exe = L3_exe = DRAM_exe = False
                elif fields[-1] == 'DRAM':
                    DRAM_exe = True
                    replace_dram_num += 1
                    L1_exe = L2_exe = L3_exe = False
                else:
                    replace_l3_num += 1
            else: l3_num['other'] += 1

        elif DRAM_exe:
            if fields[0].find('add') != -1: dram_num['add'] += 1
            elif fields[0].find('sub') != -1: dram_num['sub'] += 1
            elif fields[0].find('and') != -1: dram_num['and'] += 1
            elif fields[0].find('or') != -1: dram_num['or'] += 1
            elif fields[0].find('ldr') != -1:
                if fields[-1] == 'dcache':
                    L1_exe = True
                    replace_l1_num += 1
                    L2_exe = L3_exe = DRAM_exe = False
                elif fields[-1] == 'l2':
                    L2_exe = True
                    replace_l2_num += 1
                    L1_exe = L3_exe = DRAM_exe = False
                elif fields[-1] == 'l3':
                    L3_exe = True
                    replace_l3_num += 1
                    L1_exe = L2_exe = DRAM_exe = False
                else:
                    replace_dram_num += 1
            else: dram_num['other'] += 1


    replace_ldr_num = replace_l1_num + replace_l2_num + replace_l3_num + replace_dram_num
    outfile.write('Saving memory access: ' + str(replace_ldr_num) + ', ')
    outfile.write('%.2f%%' % (replace_ldr_num / ldr_num * 100) + '\n\n')



    ################ DCache Access ###############
    outfile.write("Saving DCache access: " + str(replace_l1_num) + ', ' +
                  '%.2f%%' % (replace_l1_num / replace_ldr_num * 100) + ', ' +
                  "instructions in tree performed in DCache:\n")
    outfile.write("ADD".center(10) + " | " +
                  "SUB".center(10) + " | " +
                  "AND".center(10) + " | " +
                  "OR".center(10) + " | " +
                  "OTHER".center(10) + " | " +
                  "TOTAL".center(10) +
                  '\n')
    outfile.write(
        str(l1_num['add']).center(10) + " | " +
        str(l1_num['sub']).center(10) + " | " +
        str(l1_num['and']).center(10) + " | " +
        str(l1_num['or']).center(10) +  " | " +
        str(l1_num['other']).center(10) + " | " +
        str(l1_num['add'] + l1_num['sub'] + l1_num['and'] + l1_num['or'] + l1_num['other']).center(10) +
        '\n\n')
    ################ L2Cache Access ###############
    outfile.write("Saving L2 access: " + str(replace_l2_num) + ', ' +
                  '%.2f%%' % (replace_l2_num / replace_ldr_num * 100) + ', ' +
                  "instructions in tree performed in L2Cache:\n")
    outfile.write("ADD".center(10) + " | " +
                  "SUB".center(10) + " | " +
                  "AND".center(10) + " | " +
                  "OR".center(10) + " | " +
                  "OTHER".center(10) + " | " +
                  "TOTAL".center(10) +
                  '\n')
    outfile.write(
        str(l2_num['add']).center(10) + " | " +
        str(l2_num['sub']).center(10) + " | " +
        str(l2_num['and']).center(10) + " | " +
        str(l2_num['or']).center(10) + " | " +
        str(l2_num['other']).center(10) + " | " +
        str(l2_num['add'] + l2_num['sub'] + l2_num['and'] + l2_num['or'] + l2_num['other']).center(10) +
        '\n\n')
    ################ L3Cache Access ###############
    '''outfile.write("Saving L3 access: " + str(replace_l3_num) + ', ' +
                  '%.2f%%' % (replace_l3_num / replace_ldr_num * 100) + ', ' +
                  "instructions in tree performed in L3Cache:\n")
    outfile.write("ADD".center(10) + " | " +
                  "SUB".center(10) + " | " +
                  "AND".center(10) + " | " +
                  "OR".center(10) + " | " +
                  "OTHER".center(10) + " | " +
                  "TOTAL".center(10) +
                  '\n')
    outfile.write(
        str(l3_num['add']).center(10) + " | " +
        str(l3_num['sub']).center(10) + " | " +
        str(l3_num['and']).center(10) + " | " +
        str(l3_num['or']).center(10) + " | " +
        str(l3_num['other']).center(10) + " | " +
        str(l3_num['add'] + l3_num['sub'] + l3_num['and'] + l3_num['or'] + l3_num['other']).center(10) +
        '\n\n')'''
    ################ DRAM Access ###############
    outfile.write("Saving DRAM access: " + str(replace_dram_num) + ', ' +
                  '%.2f%%' % (replace_dram_num / replace_ldr_num * 100) + ', ' +
                  "instructions in tree performed in DRAM:\n")
    outfile.write("ADD".center(10) + " | " +
                  "SUB".center(10) + " | " +
                  "AND".center(10) + " | " +
                  "OR".center(10) + " | " +
                  "OTHER".center(10) + " | " +
                  "TOTAL".center(10) +
                  '\n')
    outfile.write(
        str(dram_num['add']).center(10) + " | " +
        str(dram_num['sub']).center(10) + " | " +
        str(dram_num['and']).center(10) + " | " +
        str(dram_num['or']).center(10) + " | " +
        str(dram_num['other']).center(10) + " | " +
        str(dram_num['add'] + dram_num['sub'] + dram_num['and'] + dram_num['or'] + dram_num['other']).center(10) +
        '\n\n')

    ################ Pipeline Stage ##############
    outfile.write("Saving pipeline stages:\n")
    outfile.write("rename_reads: ".ljust(20) + str(pipeline_counters['rename_reads']).ljust(20) + '\n')
    outfile.write("rename_writes: ".ljust(20) + str(pipeline_counters['rename_writes']).ljust(20) + '\n')
    outfile.write("inst_window_reads: ".ljust(20) + str(pipeline_counters['inst_window_reads']).ljust(20) + '\n')
    outfile.write("inst_window_writes: ".ljust(20) + str(pipeline_counters['inst_window_writes']).ljust(20) + '\n')
    outfile.write("int_regfile_reads: ".ljust(20) + str(pipeline_counters['int_regfile_reads']).ljust(20) + '\n')
    outfile.write("int_regfile_writes: ".ljust(20) + str(pipeline_counters['int_regfile_writes']).ljust(20) + '\n')
    outfile.write("ialu_accesses: ".ljust(20) + str(pipeline_counters['ialu_accesses']).ljust(20) + '\n')
    outfile.write("ROB_reads: ".ljust(20) + str(pipeline_counters['ROB_reads']).ljust(20) + '\n\n')

def main():
    # Parse options
    usage = ('%prog [OPTION]... TREE_FILE ')
    parser = optparse.OptionParser(usage=usage)
    parser.add_option(
        '-o',
        dest='outfile',
        default=os.path.join(os.getcwd(), 'replace-results.out'),
        help="output file (default: '%default')")
    parser.add_option(
        '--trace',
        dest = 'tracefile',
        default = os.path.join(os.getcwd(), 'o3-trace.out'),
        help = "input file (default: '%default')")
    parser.add_option(
        '-p',
        dest='pipelinefile',
        default=os.path.join(os.getcwd(), 'pipeline.out'),
        help="input file (default: '%default')")
    (options, args) = parser.parse_args()

    # recognize the pattern
    print 'parse trace... recognize pattern...',
    with open(args[0], 'r') as tree:
        with open(options.tracefile, 'r') as trace:
            with open(options.pipelinefile, 'r') as pipeline:
                with open(options.outfile, 'w') as out:
                    process_trace(tree, trace, pipeline, out)

    print 'done!'


if __name__ == '__main__':
    sys.path.append(os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            '..', 'src', 'python'))
    main()
