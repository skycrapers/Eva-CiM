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

# Pipeline activity viewer for the O3 CPU model.

import optparse
import os
import sys
import copy
import operator
# Temporary storage for instructions. The queue is filled in out-of-order
# until it reaches 'max_threshold' number of instructions. It is then
# sorted out and instructions are printed out until their number drops to
# 'min_threshold'.
# It is assumed that the instructions are not out of order for more then
# 'min_threshold' places - otherwise they will appear out of order.
'''insts = {
    'queue': [] ,         # Instructions to print.
    'max_threshold':2000, # Instructions are sorted out and printed when
                          # their number reaches this threshold.
    'min_threshold':1000, # Printing stops when this number is reached.
}'''
    
# instProbe --> seqinst
seqinsts = []
instQueue = {}
traceout = open('inst.out', 'w')
    
def process_trace(instProbe, o3trace_out):
    global seqinsts
    global traceout
    if o3trace_out:
        traceout.write('  ' + 'disasm'.ljust(30) +
                      '  ' + 'seq_num'.center(10) + '\n')

    line = None
    fields = None
    curr_inst = {}

    for i in range(len(instProbe)):
        fields = instProbe[i].split(':')
        curr_inst['sn'] = int(fields[-2])
        curr_inst['disasm'] = fields[-1].strip()

        instQueue[curr_inst['sn']] = curr_inst['disasm']


        #queue_inst(o3trace_out, curr_inst)

    new_instQueue = sorted(instQueue.iteritems(), key=operator.itemgetter(0))

    #eqinsts.append(print_item['disasm'] + ' ' + str(print_item['sn']))

    for i in range(len(new_instQueue)):
        #print new_instQueue[i]
        seqinsts.append(new_instQueue[i][1] + ' ' + str(new_instQueue[i][0]))

    if o3trace_out:
        for i in range(len(seqinsts)):
            traceout.write('%s' % (
                seqinsts[i],
                ))
            traceout.write('\n')


#Sorts out instructions according to sequence number
'''def compare_by_sn(a, b):
    return cmp(a['sn'], b['sn'])'''

# Puts new instruction into the print queue.
# Sorts out and prints instructions when their number reaches threshold value
'''def queue_inst(o3trace_out, inst):
    global insts
    global seqinsts
    l_copy = copy.deepcopy(inst)
    insts['queue'].append(l_copy)

    if len(insts['queue']) > insts['max_threshold']:
        print_insts(traceout, insts['min_threshold'])'''

# Sorts out and prints instructions in print queue
'''def print_insts(o3trace_out, lower_threshold):
    global insts
    insts['queue'].sort(compare_by_sn)
    while len(insts['queue']) > lower_threshold:
        print_item=insts['queue'].pop(0)
    
        seqinsts.append(print_item['disasm'] + ' ' + str(print_item['sn']))

        if o3trace_out:
            traceout.write('%s %s' % (
                print_item['disasm'].ljust(30),
                str(print_item['sn']).rjust(10)))
            traceout.write('\n')'''


