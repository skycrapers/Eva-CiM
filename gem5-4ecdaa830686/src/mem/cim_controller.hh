/**
 * Authors: Di Gao
 * @file
 * CIMController declaration
 */

#include "base/types.hh"
#include "mem/dram_ctrl.hh"
#include "mem/mem_object.hh"
#include <iostream>
#include "params/CIMController.hh"

#ifndef __MEM_CIM_CONTROLLER_HH__
#define __MEM_CIM_CONTROLLER_HH__


class CIMController 
{
public:

    //CIMController(const CIMControllerParams *p);

    Addr src1;
    Addr src2;
    void print_src_addr(void);

};

#endif //__MEM_HMC_CONTROLLER_HH__
