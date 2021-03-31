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

import optparse
import os
import sys
import re


sys.setrecursionlimit(10000000)


statsDict = {
    'arith_add': long(0),
    'logic_and': long(0),
    'logic_xor': long(0),
    'move': long(0),
    'cmp':long(0),
    'load':long(0),
}

treeList = []
all_insts =[]
regtable = {}

instout = open('insts.out', 'w')
treeout = open('tree.out', 'w')

def simply_insts(seqinsts, seqrequest):

    
    global all_insts
    global regtable
    global loadinstnum
    global statsDict

    index = 0 # index number in all_insts
    for i in xrange(len(seqinsts)):
        inst = {
            'assembly': None,     # assembly code to print.
            'seqnum': 0,          # sequence number
            'opcode': None,
            'src1': None, 
            'src2': None,         
            'dest': None,          
            'index': {}, 
            'cim': False,

            'arith_add': False,
            'logic_and': False,
            'logic_xor': False,

            'move': False,
            'cmp': False,
            'load': False,
            'leftleaf': False,    # there is not leaf node
            'rightleaf': False,    # there is not right node
            'intree': False,
        }
        #fields = seqinsts[i].split()
        fields = re.split('[ ,]', seqinsts[i])
        while '' in fields:
            fields.remove('')
        if re.match('v', fields[0]): continue
        
        inst['opcode'] = str(fields[0])
        inst['seqnum'] = str(fields[-1])

        if len(fields) == 2: continue   # branch instructions [bl seq_num]

        inst['assembly'] = ' '.join(seqinsts[i].split()[:-1])

        # process source operands
        src = fields[2:-1]
        if src is None:
            inst['src1'] = None
            inst['src2'] = None
            inst['leftleaf'] = True
            inst['rightleaf'] = True
        elif len(src) == 1:
            if re.match('#', fields[2]) is None:
                inst['src1'] = fields[2]
                inst['leftleaf'] = False
            else:
                inst['src1'] = '#'
                inst['leftleaf'] = True
            inst['src2'] = None
            inst['rightleaf'] = True
        elif len(src) == 2:
            inst['src1'] = str(src[0]).strip('[]')
            inst['leftleaf'] = False
            if re.match('#', fields[3]) is None:
                inst['src2'] = fields[3].strip('[]')
                inst['rightleaf'] = False
            else:
                inst['src2'] = '#'
                inst['rightleaf'] = True
        elif len(src) == 3:
            inst['src1'] = str(src[0]).strip('[]')
            inst['leftleaf'] = False
            if re.match('#', src[2]):
                if re.match('\w\w\w', src[1]):
                    inst['src2'] = None
                    inst['rightleaf'] = True
            else:
                inst['src2'] = str(src[1]).strip('[]')
                inst['rightleaf'] = False
        elif len(src) > 3:
            inst['src1'] = str(src[0]).strip('[]')
            inst['src2'] = str(src[1]).strip('[]')
            inst['leftleaf'] = False
            inst['rightleaf'] = False

        # process destination data
        if re.match('#', fields[1]):
            inst['dest'] = None
        else:
            inst['dest'] = str(fields[1])

        if re.match("str", inst['opcode']):
            inst['src1'] = None
            inst['src2'] = None
            inst['dest'] = None


        inst['cim'] = False
        if re.match('add', inst['opcode']) or re.match('sub', inst['opcode']):
            inst['arith_add'] = True
            inst['cim'] = True
            statsDict['arith_add']+=long(1)
        elif re.match('and',inst['opcode']) or re.match('orr',inst['opcode']):
            inst['logic_and'] = True
            inst['cim'] = True
            statsDict['logic_and']+=long(1)
        elif re.match('eor',inst['opcode']) or re.match('bic',inst['opcode']):
            inst['logic_xor'] = True
            inst['cim'] = True
            statsDict['logic_xor']+=long(1)

        elif re.match('mov', inst['opcode']) or re.match('mvn', inst['opcode']):
            inst['move'] = True
            statsDict['move']+=long(1)    
        elif re.match('cmp', inst['opcode']) or re.match('cmn', inst['opcode']) or re.match('tst', inst['opcode']) or re.match('teq', inst['opcode']) :
            inst['cmp'] = True
            statsDict['cmp']+=long(1)
        elif re.match('ldr', inst['opcode']):
            inst['load'] = True
            statsDict['load']+=long(1)


        reglist = regtable.keys()  # return the length of key list of dictionary
        for i in range(len(reglist)):
            inst['index'][reglist[i]] = len(regtable[reglist[i]])
        # regtable = {'r0':[], 'r1':[],... 'pc':[], 'lr':[],...}
        if not re.match('str', inst['opcode']):
            if inst['dest'] not in regtable.keys():
                regtable[inst['dest']] = []
                regtable[inst['dest']].append(index)
            elif inst['dest'] in regtable.keys():
                regtable[inst['dest']].append(index)

        index += 1
        
        instout.write('%s %s %s\n' % (inst['assembly'], inst['seqnum'], inst['cim']))
  
        all_insts.append(inst)


def gene_tree(tree_en, outfile):

    global all_insts
    global regtable

    treenum = 0
    global treeout

    for i in range(len(all_insts)):
        # satisfy CiM operation type, check whether operands are
        # accessed from or stored in memory
        if all_insts[i]['cim'] == False: continue
        
        all_insts[i]['intree'] = True
        preTree = Tree(all_insts[i])
        
        flag = False
        while flag == False:
            preTree.createTree()
            flag = preTree.completeTree(preTree)

        treenum = treenum + 1     
        #print treenum

        if tree_en:
            treeout.write('%s' % (
                ("#" + str(treenum)).ljust(15),
            ))
            treeout.write('\n')
            postorderTraverse(preTree, treeout)
# define binary tree, the root node is CIM operation type instruction
class Tree(object):
    def __init__(self, data):
        self.data = data
        self.left = None
        self.right = None

    def createTree(self):
        if self.data['leftleaf'] and self.data['rightleaf']:
            return
        # when src1 is equal to src2, only insert one side
        if self.data['src1'] is not None and self.data['src2'] is not None:
            if self.data['src1'] == self.data['src2']:
                self.data['rightleaf'] = True

        
        if self.left is None and self.data['leftleaf'] == False:
            self.insertLeftNode()
        if self.right is None and self.data['rightleaf'] == False:
            self.insertRightNode()


        if self.left is not None:
            self.left.createTree()
        if self.right is not None:
            self.right.createTree()

        return

    def insertLeftNode(self):

        global all_insts
        global regtable

        if self.data['src1'] not in self.data['index'].keys():
            self.data['leftleaf'] = True
            return
        forwardListLength = self.data['index'][self.data['src1']]   # list of src1 register 
                                                                    # when it is served as destination data 
                                                                    # of other instrucitons
        if forwardListLength == 0:
            self.data['leftleaf'] = True
            return

        newNodeIndex = regtable[self.data['src1']][forwardListLength-1]
        newNode = all_insts[newNodeIndex]

        if newNode['intree']:   # this node has been prior trees
            self.data['leftleaf'] = True
        elif re.match("ldr", newNode['opcode']):
            all_insts[newNodeIndex]['leftleaf'] = True
            all_insts[newNodeIndex]['rightleaf'] = True
            all_insts[newNodeIndex]['intree'] = True
            self.left = Tree(all_insts[newNodeIndex])
        else:
            all_insts[newNodeIndex]['intree'] = True
            self.left = Tree(all_insts[newNodeIndex])

        return

    def insertRightNode(self):

        global all_insts
        global regtable
        
        if self.data['src2'] not in self.data['index'].keys():
            self.data['rightleaf'] = True
            return
        forwardListLength = self.data['index'][self.data['src2']]   # list of src2 register 
                                                                    # when it is served as destination data 
                                                                    # of other instrucitons
        
        if forwardListLength == 0:
            self.data['rightleaf'] = True
            return
        newNodeIndex = regtable[self.data['src2']][forwardListLength-1]
        newNode = all_insts[newNodeIndex]

        

        if newNode['intree']:   # this node has been prior trees
            self.data['rightleaf'] = True
        elif re.match("ldr", newNode['opcode']):
            all_insts[newNodeIndex]['leftleaf'] = True
            all_insts[newNodeIndex]['rightleaf'] = True
            all_insts[newNodeIndex]['intree'] = True
            self.right = Tree(all_insts[newNodeIndex])
        else:
            all_insts[newNodeIndex]['intree'] = True
            self.right = Tree(all_insts[newNodeIndex])
        
        return

    def completeTree(self, root):
        if root is None:
            return True
        elif root.left is None and root.right is None:
            return root.data['leftleaf'] and root.data['rightleaf']
        else:
            return (self.completeTree(root.left) and self.completeTree(root.right))

def postorderTraverse(tree, outfile):

    global treeList

    if tree is None: return
    postorderTraverse(tree.left, outfile)
    postorderTraverse(tree.right, outfile)
    if type(tree.data) == type({}):
        treeList.append(
            {'assembly': tree.data['assembly'],
            'seqnum': tree.data['seqnum'],
            'cim': tree.data['cim'],
            'arith_add': tree.data['arith_add'],
            'logic_and': tree.data['logic_and'],
            'logic_xor': tree.data['logic_xor'],
            'move': tree.data['move'],
            'cmp': tree.data['cmp'],
            'load': tree.data['load']}
            )
        outfile.write('%s %s %s' % (
            " ".ljust(15),
            tree.data['assembly'].ljust(40),
            str(tree.data['seqnum']).rjust(15)
        ))
        outfile.write('\n')
