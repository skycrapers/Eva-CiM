/*
 * Copyright (c) 2001, 2003-2005 The Regents of The University of Michigan
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are
 * met: redistributions of source code must retain the above copyright
 * notice, this list of conditions and the following disclaimer;
 * redistributions in binary form must reproduce the above copyright
 * notice, this list of conditions and the following disclaimer in the
 * documentation and/or other materials provided with the distribution;
 * neither the name of the copyright holders nor the names of its
 * contributors may be used to endorse or promote products derived from
 * this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
 * "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
 * LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
 * A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
 * OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
 * SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
 * LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
 * DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
 * THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
 * OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 *
 * Authors: Steve Raasch
 *          Nathan Binkert
 */


#include "cpu/o3/pipe_monitor.hh"


void pipeMonitor()
{    
    itemNum++;
    for (map<long, string>::iterator it = PipeAccessMap.begin(); it != PipeAccessMap.end(); it++)
    {
        // pipeUnitRecords[itemNum%maxDumpItems-1].seqnum = it->first
        int sn = it->first;
        iter = pipeUnitRecords.find(sn);
        if (iter==pipeUnitRecords.end()) {
            PipeUnit cur_pipeaccess{};
            if (it->second == "inst_window_reads")
                cur_pipeaccess.iwreads += 1;
            else if (it->second == "inst_window_writes")
                cur_pipeaccess.iwwrites += 1;
            else if (it->second == "rename_reads")
                cur_pipeaccess.rreads += 1;
            else if (it->second == "rename_writes")
                cur_pipeaccess.rwrites += 1;
            else if (it->second == "int_regfile_reads")
                cur_pipeaccess.irreads += 1;
            else if (it->second == "int_regfile_writes")
                cur_pipeaccess.irwrites += 1;
            else if (it->second == "ialu_accesses")
                cur_pipeaccess.ialuaccess += 1;
            else if (it->second == "ROB_reads")
                cur_pipeaccess.robreads += 1;
            else if (it->second == "ROB_writes")
                cur_pipeaccess.robwrites += 1;
            
            pipeUnitRecords.insert(make_pair(sn, cur_pipeaccess));
        }

        else {
            if (it->second == "inst_window_reads")
                pipeUnitRecords[sn].iwreads += 1;
            else if (it->second == "inst_window_writes")
                pipeUnitRecords[sn].iwwrites += 1;
            else if (it->second == "rename_reads")
                pipeUnitRecords[sn].rreads += 1;
            else if (it->second == "rename_writes")
                pipeUnitRecords[sn].rwrites += 1;
            else if (it->second == "int_regfile_reads")
                pipeUnitRecords[sn].irreads += 1;
            else if (it->second == "int_regfile_writes")
                pipeUnitRecords[sn].irwrites += 1;
            else if (it->second == "ialu_accesses")
                pipeUnitRecords[sn].ialuaccess += 1;
            else if (it->second == "ROB_reads")
                pipeUnitRecords[sn].robreads += 1;
            else if (it->second == "ROB_writes")
                pipeUnitRecords[sn].robwrites += 1;
        }

    }

    if (itemNum % maxDumpItems == 0)
        dumpPipeRecords();

}


void dumpPipeRecords()
{
    for (iter = pipeUnitRecords.begin(); iter != pipeUnitRecords.end(); iter++) {
        DPRINTF(PipeTrace, "%lli: %d %d %d %d %d %d %d %d %d\n",
            iter->first,
            iter->second.iwreads,
            iter->second.iwwrites,
            iter->second.rreads,
            iter->second.rwrites,
            iter->second.irreads,
            iter->second.irwrites,
            iter->second.ialuaccess,
            iter->second.robreads,
            iter->second.robwrites);
    }

}

