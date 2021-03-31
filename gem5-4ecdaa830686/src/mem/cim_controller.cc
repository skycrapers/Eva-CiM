/**
 * Authors: Di Gao
 * @file
 * CIMController defintion 
 **/

#include "mem/cim_controller.hh"
using namespace std;

//CIMController::CIMController(const CIMControllerParams* p):	DRAMCtrl(p) { }

void 
CIMController::print_src_addr(void) 
{
	cout << "src1 addr: " << "0x" << hex << src1 << endl;
	cout << "src2 addr: " << "0x" << hex << src2 << endl;
}
