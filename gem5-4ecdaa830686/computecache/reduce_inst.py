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

def reduce_inst(cimtreefile):

    line = None
    fields = None
    instNum = 0

    while True:
        line = cimtreefile.readline()
        if not line: break
        fields = line.split()
        if re.match('#', fields[0]): continue
        if re.match('dcache', fields[-1]): continue
        if re.match('l2', fields[-1]): continue
        if re.match('l3', fields[-1]): continue
        if re.match('dram', fields[-1]): continue
        instNum += 1

    print(instNum)
   
def main():
    # Parse options
    usage = ('%prog [OPTION]... TRACE_FILE')
    parser = optparse.OptionParser(usage=usage)

    (options, args) = parser.parse_args()

    # Process trace
    with open(args[0], 'r') as cimtreefile:
        reduce_inst(cimtreefile)


if __name__ == '__main__':
    sys.path.append(os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            '..', 'src', 'python'))
    main()
