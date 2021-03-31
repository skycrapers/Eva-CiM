#! /usr/bin/env python2

# Copyright (c) 3011 ARM Limited
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
import re
from tree import statsDict
from time import time


def parse_output(treeList, cimtreefile, pipestage, conf, outfile):

    conf = int(conf)

    treeout = open(cimtreefile, 'w')
    treenum = 0
    treeout.write('%s' % (
                ("#" + str(treenum)).ljust(20),
            ))
    treeout.write('\n')
    for i in range(len(treeList)):
        if treeList[i]['cim'] is False:
            if treeList[i]['load']:
                treeout.write('%s %s %s %s\n' % (
                    " ".ljust(20),
                    treeList[i]['assembly'].ljust(40),
                    str(treeList[i]['seqnum']).ljust(20),
                    treeList[i]['level'].ljust(20)
                ))
            else:
                treeout.write('%s %s %s\n' % (
                    " ".ljust(20),
                    treeList[i]['assembly'].ljust(40),
                    str(treeList[i]['seqnum']).ljust(20)
                ))
        else:
            treeout.write('%s %s %s\n' % (
                    " ".ljust(20),
                    treeList[i]['assembly'].ljust(40),
                    str(treeList[i]['seqnum']).ljust(20)
            ))
            treenum += 1
            treeout.write('%s\n' % (
                ("#" + str(treenum)).ljust(20),
            ))    


    l1_access = 0
    l2_access = 0
    l3_access = 0
    dram_access = 0
    L1_exe = True
    L2_exe = False
    L3_exe = False
    dram_exe = False

    real_l1_cim = {
        'arith_add': 0,
        'logic_and': 0,
        'logic_xor': 0
    }
    real_l2_cim = {
        'arith_add': 0,
        'logic_and': 0,
        'logic_xor': 0
    }
    real_l3_cim = {
        'arith_add': 0,
        'logic_and': 0,
        'logic_xor': 0
    }
    real_dram_cim = {
        'arith_add': 0,
        'logic_and': 0,
        'logic_xor': 0
    }


    pipeCounters = {
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


    for i in range(len(treeList)):

        if L1_exe:            
            if treeList[i]['load']:
                if treeList[i]['level'] == 'l2':
                    L2_exe = True
                    L1_exe = L3_exe = dram_exe = False
                    if conf == 0 or conf == 2:
                        l2_access += 1
                        if treeList[i+1]['arith_add']: real_l2_cim['arith_add']+=1
                        elif treeList[i+1]['logic_and']: real_l2_cim['logic_and']+=1
                        elif treeList[i+1]['logic_xor']: real_l2_cim['logic_xor']+=1
                        elif treeList[i+1]['cmp']: real_l2_cim['arith_add']+=1

                elif treeList[i]['level'] == 'l3':
                    L3_exe = True
                    
                    L1_exe = L2_exe = dram_exe = False
                    if conf == 0 or conf == 3:
                        l3_access += 1
                        if treeList[i+1]['arith_add']: real_l3_cim['arith_add']+=1
                        elif treeList[i+1]['logic_and']: real_l3_cim['logic_and']+=1
                        elif treeList[i+1]['logic_xor']: real_l3_cim['logic_xor']+=1
                        elif treeList[i+1]['cmp']: real_l3_cim['arith_add']+=1

                elif treeList[i]['level'] == 'dram':
                    dram_exe = True
                    
                    L1_exe = L2_exe = L3_exe = False
                    if conf == 0 or conf == 2:
                        dram_access += 1
                        if treeList[i+1]['arith_add']: real_dram_cim['arith_add']+=1
                        elif treeList[i+1]['logic_and']: real_dram_cim['logic_and']+=1
                        elif treeList[i+1]['logic_xor']: real_dram_cim['logic_xor']+=1
                        elif treeList[i+1]['cmp']: real_dram_cim['arith_add']+=1

                else:
                    if conf == 0 or conf == 1:
                        l1_access += 1
                        if treeList[i+1]['arith_add']: real_l1_cim['arith_add']+=1
                        elif treeList[i+1]['logic_and']: real_l1_cim['logic_and']+=1
                        elif treeList[i+1]['logic_xor']: real_l1_cim['logic_xor']+=1
                        elif treeList[i+1]['cmp']: real_l1_cim['arith_add']+=1

            elif treeList[i]['cim'] or treeList[i]['move'] or treeList[i]['cmp']:
                if conf == 0 or conf == 1:
                    sn = str(treeList[i]['seqnum'])       
                    if sn in pipestage.keys():
                        pipeCounters['rename_reads'] += pipestage[sn][0]
                        pipeCounters['rename_writes'] += pipestage[sn][1]
                        pipeCounters['inst_window_reads'] += pipestage[sn][2]
                        pipeCounters['inst_window_writes'] += pipestage[sn][3]
                        pipeCounters['int_regfile_reads'] += pipestage[sn][4]
                        pipeCounters['int_regfile_writes'] += pipestage[sn][5]
                        pipeCounters['ialu_accesses'] += pipestage[sn][6]
                        pipeCounters['ROB_reads'] += pipestage[sn][7]
                        pipeCounters['ROB_writes'] += pipestage[sn][8]


        elif L2_exe:
            if treeList[i]['load']:
                if treeList[i]['level'] == 'dcache':
                    L1_exe = True
                    
                    L2_exe = L3_exe = dram_exe = False
                    if conf == 0 or conf == 1:
                        l1_access += 1
                        if treeList[i+1]['arith_add']: real_l1_cim['arith_add']+=1
                        elif treeList[i+1]['logic_and']: real_l1_cim['logic_and']+=1
                        elif treeList[i+1]['logic_xor']: real_l1_cim['logic_xor']+=1
                        elif treeList[i+1]['cmp']: real_l1_cim['arith_add']+=1

                elif treeList[i]['level'] == 'l3':
                    L3_exe = True
                    
                    L1_exe = L2_exe = dram_exe = False
                    if conf == 0 or conf == 3:
                        l3_access += 1
                        if treeList[i+1]['arith_add']: real_l3_cim['arith_add']+=1
                        elif treeList[i+1]['logic_and']: real_l3_cim['logic_and']+=1
                        elif treeList[i+1]['logic_xor']: real_l3_cim['logic_xor']+=1
                        elif treeList[i+1]['cmp']: real_l3_cim['arith_add']+=1

                elif treeList[i]['level'] == 'dram':
                    dram_exe = True
                    
                    L1_exe = L2_exe = L3_exe = False
                    if conf == 0 or conf == 2:
                        dram_access += 1
                        if treeList[i+1]['arith_add']: real_dram_cim['arith_add']+=1
                        elif treeList[i+1]['logic_and']: real_dram_cim['logic_and']+=1
                        elif treeList[i+1]['logic_xor']: real_dram_cim['logic_xor']+=1
                        elif treeList[i+1]['cmp']: real_dram_cim['arith_add']+=1

                else:
                    if conf == 0 or conf == 2:
                        l2_access += 1
                        if treeList[i+1]['arith_add']: real_l2_cim['arith_add']+=1
                        elif treeList[i+1]['logic_and']: real_l2_cim['logic_and']+=1
                        elif treeList[i+1]['logic_xor']: real_l2_cim['logic_xor']+=1
                        elif treeList[i+1]['cmp']: real_l2_cim['arith_add']+=1

            elif treeList[i]['cim'] or treeList[i]['move'] or treeList[i]['cmp']:
                if conf == 0 or conf == 2:
                    sn = str(treeList[i]['seqnum'])       
                    if sn in pipestage.keys():
                        pipeCounters['rename_reads'] += pipestage[sn][0]
                        pipeCounters['rename_writes'] += pipestage[sn][1]
                        pipeCounters['inst_window_reads'] += pipestage[sn][2]
                        pipeCounters['inst_window_writes'] += pipestage[sn][3]
                        pipeCounters['int_regfile_reads'] += pipestage[sn][4]
                        pipeCounters['int_regfile_writes'] += pipestage[sn][5]
                        pipeCounters['ialu_accesses'] += pipestage[sn][6]
                        pipeCounters['ROB_reads'] += pipestage[sn][7]
                        pipeCounters['ROB_writes'] += pipestage[sn][8]


        elif L3_exe:
            if treeList[i]['load']:
                if treeList[i]['level'] == 'dcache':
                    L1_exe = True
                    
                    L2_exe = L3_exe = dram_exe = False
                    if conf == 0 or conf == 1:
                        l1_access += 1
                        if treeList[i+1]['arith_add']: real_l1_cim['arith_add']+=1
                        elif treeList[i+1]['logic_and']: real_l1_cim['logic_and']+=1
                        elif treeList[i+1]['logic_xor']: real_l1_cim['logic_xor']+=1
                        elif treeList[i+1]['cmp']: real_l1_cim['arith_add']+=1

                elif treeList[i]['level'] == 'l2':
                    L2_exe = True
                    
                    L1_exe = L3_exe = dram_exe = False
                    if conf == 0 or conf == 2:
                        l2_access += 1
                        if treeList[i+1]['arith_add']: real_l2_cim['arith_add']+=1
                        elif treeList[i+1]['logic_and']: real_l2_cim['logic_and']+=1
                        elif treeList[i+1]['logic_xor']: real_l2_cim['logic_xor']+=1
                        elif treeList[i+1]['cmp']: real_l2_cim['arith_add']+=1

                elif treeList[i]['level'] == 'dram':
                    dram_exe = True
                    
                    L1_exe = L2_exe = L3_exe = False
                    if conf == 0 or conf == 2:
                        if treeList[i+1]['arith_add']: real_dram_cim['arith_add']+=1
                        elif treeList[i+1]['logic_and']: real_dram_cim['logic_and']+=1
                        elif treeList[i+1]['logic_xor']: real_dram_cim['logic_xor']+=1
                        elif treeList[i+1]['cmp']: real_dram_cim['arith_add']+=1

                else:
                    if conf == 0 or conf == 3:
                        l3_access += 1
                        if treeList[i+1]['arith_add']: real_l3_cim['arith_add']+=1
                        elif treeList[i+1]['logic_and']: real_l3_cim['logic_and']+=1
                        elif treeList[i+1]['logic_xor']: real_l3_cim['logic_xor']+=1
                        elif treeList[i+1]['cmp']: real_l3_cim['arith_add']+=1

            elif treeList[i]['cim'] or treeList[i]['move'] or treeList[i]['cmp']:
                if conf == 0 or conf == 3:
                    sn = str(treeList[i]['seqnum'])       
                    if sn in pipestage.keys():
                        pipeCounters['rename_reads'] += pipestage[sn][0]
                        pipeCounters['rename_writes'] += pipestage[sn][1]
                        pipeCounters['inst_window_reads'] += pipestage[sn][2]
                        pipeCounters['inst_window_writes'] += pipestage[sn][3]
                        pipeCounters['int_regfile_reads'] += pipestage[sn][4]
                        pipeCounters['int_regfile_writes'] += pipestage[sn][5]
                        pipeCounters['ialu_accesses'] += pipestage[sn][6]
                        pipeCounters['ROB_reads'] += pipestage[sn][7]
                        pipeCounters['ROB_writes'] += pipestage[sn][8]


        elif dram_exe:
            if treeList[i]['load']:
                if treeList[i]['level'] == 'dcache':
                    L1_exe = True
                    
                    L2_exe = L3_exe = dram_exe = False
                    if conf == 0 or conf == 1:
                        l1_access += 1
                        if treeList[i+1]['arith_add']: real_l1_cim['arith_add']+=1
                        elif treeList[i+1]['logic_and']: real_l1_cim['logic_and']+=1
                        elif treeList[i+1]['logic_xor']: real_l1_cim['logic_xor']+=1
                        elif treeList[i+1]['cmp']: real_l1_cim['arith_add']+=1

                elif treeList[i]['level'] == 'l2':
                    L2_exe = True
                    
                    L1_exe = L3_exe = dram_exe = False
                    if conf == 0 or conf == 2:
                        l2_access += 1
                        if treeList[i+1]['arith_add']: real_l2_cim['arith_add']+=1
                        elif treeList[i+1]['logic_and']: real_l2_cim['logic_and']+=1
                        elif treeList[i+1]['logic_xor']: real_l2_cim['logic_xor']+=1
                        elif treeList[i+1]['cmp']: real_l2_cim['arith_add']+=1

                elif treeList[i]['level'] == 'l3':
                    L3_exe = True
                    
                    L1_exe = L2_exe = dram_exe = False
                    if conf == 0 or conf == 3:
                        l3_access += 1
                    if treeList[i+1]['arith_add']: real_l3_cim['arith_add']+=1
                    elif treeList[i+1]['logic_and']: real_l3_cim['logic_and']+=1
                    elif treeList[i+1]['logic_xor']: real_l3_cim['logic_xor']+=1
                    elif treeList[i+1]['cmp']: real_l3_cim['arith_add']+=1

                else:
                    if conf == 0 or conf == 2:
                        dram_access += 1
                        if treeList[i+1]['arith_add']: real_dram_cim['arith_add']+=1
                        elif treeList[i+1]['logic_and']: real_dram_cim['logic_and']+=1
                        elif treeList[i+1]['logic_xor']: real_dram_cim['logic_xor']+=1
                        elif treeList[i+1]['cmp']: real_dram_cim['arith_add']+=1

            elif treeList[i]['cim'] or treeList[i]['move'] or treeList[i]['cmp']:
                if conf == 0 or conf == 2:
                    sn = str(treeList[i]['seqnum'])       
                    if sn in pipestage.keys():
                        pipeCounters['rename_reads'] += pipestage[sn][0]
                        pipeCounters['rename_writes'] += pipestage[sn][1]
                        pipeCounters['inst_window_reads'] += pipestage[sn][2]
                        pipeCounters['inst_window_writes'] += pipestage[sn][3]
                        pipeCounters['int_regfile_reads'] += pipestage[sn][4]
                        pipeCounters['int_regfile_writes'] += pipestage[sn][5]
                        pipeCounters['ialu_accesses'] += pipestage[sn][6]
                        pipeCounters['ROB_reads'] += pipestage[sn][7]
                        pipeCounters['ROB_writes'] += pipestage[sn][8]


    outfile.write('##### counters'.ljust(30) + 'increment'.center(20) + 'value'.ljust(20) + 'pdf #####'.ljust(20) + '\n')
    print statsDict
    print '\n'
    memoryAccess = l1_access  + l2_access + l3_access + dram_access
    outfile.write('memory_access: '.ljust(30) + '-'.center(20) + str(memoryAccess).ljust(20))
    outfile.write('%.2f%%' % (memoryAccess / statsDict['load'] * 100) + '\n')
    ################ DCache Access ###############
    outfile.write('dcache_access: '.ljust(30) + '-'.center(20) + str(l1_access).ljust(20))
    outfile.write('%.2f%%' % (l1_access / memoryAccess * 100) + '\n')
    outfile.write('compute_dcache_arith_add: '.ljust(30) + '+'.center(20) + str(real_l1_cim['arith_add']) + '\n' )
    outfile.write('compute_dcache_logic_and: '.ljust(30) + '+'.center(20) + str(real_l1_cim['logic_and']) + '\n' )
    outfile.write('compute_dcache_logic_xor: '.ljust(30) + '+'.center(20) + str(real_l1_cim['logic_xor']) + '\n' )
    #outfile.write('compute_dcache_access: '.ljust(30) + '+'.center(20) + str(real_l1_cim['logic']+real_l1_cim['arith']) + '\n')
    ################ L2Cache Access ###############
    outfile.write('l2_access: '.ljust(30) + '-'.center(20) + str(l2_access).ljust(20))
    outfile.write('%.2f%%' % (l2_access / memoryAccess * 100) + '\n')
    outfile.write('compute_l2_arith_add: '.ljust(30) + '+'.center(20) + str(real_l2_cim['arith_add']) + '\n' )
    outfile.write('compute_l2_logic_and: '.ljust(30) + '+'.center(20) + str(real_l2_cim['logic_and']) + '\n' )
    outfile.write('compute_l2_logic_xor: '.ljust(30) + '+'.center(20) + str(real_l2_cim['logic_xor']) + '\n' )
    #outfile.write('compute_l2_access: '.ljust(30) + '+'.center(20) + str(real_l2_cim['logic']+real_l2_cim['arith']) + '\n')
    ################ L3 Access ###############
    outfile.write('l3_access: '.ljust(30) + '-'.center(20) + str(l3_access).ljust(20))
    outfile.write('%.2f%%' % (l3_access / memoryAccess * 100) + '\n')
    outfile.write('compute_l3_arith_add: '.ljust(30) + '+'.center(20) + str(real_l3_cim['arith_add']) + '\n' )
    outfile.write('compute_l3_logic_and: '.ljust(30) + '+'.center(20) + str(real_l3_cim['logic_and']) + '\n' )
    outfile.write('compute_l3_logic_xor: '.ljust(30) + '+'.center(20) + str(real_l3_cim['logic_xor']) + '\n' )
    #outfile.write('compute_l3_access: '.ljust(30) + '+'.center(20) + str(real_l3_cim['logic']+real_l3_cim['arith']) + '\n')
    ################ DRAM Access ###############
    outfile.write('dram_access: '.ljust(30) + '-'.center(20) + str(dram_access).ljust(20))
    outfile.write('%.2f%%' % (dram_access / memoryAccess * 100) + '\n')
    outfile.write('compute_dram_arith_add: '.ljust(30) + '+'.center(20) + str(real_dram_cim['arith_add']) + '\n' )
    outfile.write('compute_dram_logic_and: '.ljust(30) + '+'.center(20) + str(real_dram_cim['logic_and']) + '\n' )
    outfile.write('compute_dram_logic_xor: '.ljust(30) + '+'.center(20) + str(real_dram_cim['logic_xor']) + '\n' )
    #outfile.write('compute_dram_access: '.ljust(30) + '+'.center(20) + str(real_dram_cim['logic']+real_dram_cim['arith']) + '\n')
    ################ Pipeline Stage ##############
    outfile.write("rename_reads: ".ljust(30) + '-'.center(20) + str(pipeCounters['rename_reads']).ljust(20) + '\n')
    outfile.write("rename_writes: ".ljust(30) + '-'.center(20) + str(pipeCounters['rename_writes']).ljust(20) + '\n')
    outfile.write("inst_window_reads: ".ljust(30) + '-'.center(20) + str(pipeCounters['inst_window_reads']).ljust(20) + '\n')
    outfile.write("inst_window_writes: ".ljust(30) + '-'.center(20) + str(pipeCounters['inst_window_writes']).ljust(20) + '\n')
    outfile.write("int_regfile_reads: ".ljust(30) + '-'.center(20) + str(pipeCounters['int_regfile_reads']).ljust(20) + '\n')
    outfile.write("int_regfile_writes: ".ljust(30) + '-'.center(20) + str(pipeCounters['int_regfile_writes']).ljust(20) + '\n')
    outfile.write("ialu_accesses: ".ljust(30) + '-'.center(20) + str(pipeCounters['ialu_accesses']).ljust(20) + '\n')
    outfile.write("ROB_reads: ".ljust(30) + '-'.center(20) + str(pipeCounters['ROB_reads']).ljust(20) + '\n')
    outfile.write("ROB_writes: ".ljust(30) + '-'.center(20) + str(pipeCounters['ROB_writes']).ljust(20) + '\n')

