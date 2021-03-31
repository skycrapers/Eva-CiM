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
import re


pipestage = {'': [0, 0, 0, 0, 0, 0, 0, 0, 0]}  # dictionary type

def parse_pipeline(pipeProbe):

    ################### pipeline counter quantity with CiM replacement ####################
    '''
    rename stage: 'rename_reads', 'rename_writes',
    issue stage: 'inst_window_reads', 'inst_window_writes'
    IEW stage: 'int_regfile_reads', 'int_regfile_writes', 'ialu_accesses'
    commit stage: 'ROB_reads', 'ROB_writes'
    '''
    global pipestage

    for i in range(len(pipeProbe)):
        fields = pipeProbe[i].split(':')
        sn = fields[2]
        unitAccess = fields[-1].split()
        if pipestage.has_key(sn):
            pipestage[sn][0] += int(unitAccess[0])
            pipestage[sn][1] += int(unitAccess[1])
            pipestage[sn][2] += int(unitAccess[2])
            pipestage[sn][3] += int(unitAccess[3])
            pipestage[sn][4] += int(unitAccess[4])
            pipestage[sn][5] += int(unitAccess[5])
            pipestage[sn][6] += int(unitAccess[6])
            pipestage[sn][7] += int(unitAccess[7])
            pipestage[sn][8] += int(unitAccess[8])

        else:
            pipestage[sn] = [0, 0, 0, 0, 0, 0, 0, 0, 0]
            pipestage[sn][0] += int(unitAccess[0])
            pipestage[sn][1] += int(unitAccess[1])
            pipestage[sn][2] += int(unitAccess[2])
            pipestage[sn][3] += int(unitAccess[3])
            pipestage[sn][4] += int(unitAccess[4])
            pipestage[sn][5] += int(unitAccess[5])
            pipestage[sn][6] += int(unitAccess[6])
            pipestage[sn][7] += int(unitAccess[7])
            pipestage[sn][8] += int(unitAccess[8])


    