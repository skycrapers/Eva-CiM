/**
 * Authors: Di Gao
 * @file
 * CIMController declaration
 */

#include "base/types.hh"
#ifndef __MEM_CIM_CONTROLLER_HH__
#define __MEM_CIM_CONTROLLER_HH__

#include 

class CIMController : public DRAMCtrl
{
public:
    Addr src1;
    Addr src2;
    void print_src_addr();

};

#endif //__MEM_HMC_CONTROLLER_HH__
