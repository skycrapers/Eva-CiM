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
import copy
from time import time
import profile
sys.setrecursionlimit(100000)

# Temporary storage for instructions. The queue is filled in out-of-order
# until it reaches 'max_threshold' number of instructions. It is then
# sorted out and instructions are printed out until their number drops to
# 'min_threshold'.
# It is assumed that the instructions are not out of order for more then
# 'min_threshold' places - otherwise they will appear out of order.


CiM_set = []
all_insts = []

ALUOp = ['add', 'sub', 'and', 'or']

# define tree node
'''class Node(object):
    def __init__(self, data, left, right):
        self.data = data # dict type ['op', 'dest', 'src1', 'src2', 'seq']
        self.left = left
        self.right = right'''

# define binary tree, the root node is CIM operation type instruction
class Tree(object):
    def __init__(self, data):
        self.data = data
        self.left = None
        self.right = None

    

    def createTree(self, newNode):
        if self.data['leftFlag'] and self.data['rightFlag']:
            return
        # when src1 is equal to src2, only insert one side
        if self.data['src1'] is not None and self.data['src2'] is not None:
            fields = self.data['src2'].split(' ')
            if fields[0] == self.data['src1']:
                self.data['rightFlag'] = True

        insertLeft = insertRight = False
        '''leftNode = rightNode = False'''

        if self.left is None:
            if self.data['leftFlag'] == False:
                insertLeft = self.insertLeftNode(newNode)
                '''if insertLeft:
                    leftNode = self.left.data['leftFlag'] and self.left.data['rightFlag']'''
        if self.right is None:
            if self.data['rightFlag'] == False:
                insertRight = self.insertRightNode(newNode)
                '''if insertRight:
                    rightNode = self.right.data['leftFlag'] and self.right.data['rightFlag']'''


        if insertLeft is False:
            if self.left is not None:
                self.left.createTree(newNode)
        if insertRight is False:
            if self.right is not None:
                self.right.createTree(newNode)

        return


    def completeTree(self, root):
        if root is None:
            return False
        elif root.left is None and root.right is None:
            return root.data['leftFlag'] and root.data['rightFlag']
        else:
            return (self.completeTree(root.left) and self.completeTree(root.right))

    def insertLeftNode(self, newNode):
        if newNode['src1'] is None: return

        pattern = str(newNode['dest'])
        if len(pattern) != len(self.data['src1']):
            pattern += ","
        if pattern is None: return

        if self.data['src1'].find(pattern) != -1:
            if newNode['opcode'][0] == 'v': # floating point instructions
                self.data['leftFlag'] = True
            elif newNode['opcode'].find('ldr') != -1:
                newNode['leftFlag'] = newNode['rightFlag'] = True
                self.left = Tree(newNode)
            elif self.checkLeafNode(newNode):
                self.data['leftFlag'] = True
            else:
                newNode['leftFlag'] = self.checkImmediate(newNode, True)
                newNode['rightFlag'] = self.checkImmediate(newNode, False)
                self.left = Tree(newNode)
            return True

        return False

    def insertRightNode(self, newNode):
        if newNode['src2'] is None: return
        pattern = str(newNode['dest'])
        if len(pattern) != len(self.data['src2']):
            pattern += ","
        if pattern is None: return

        if self.data['src2'].find(pattern) != -1:
            if newNode['opcode'][0] == 'v':
                self.data['rightFlag'] = True
            elif newNode['opcode'].find('ldr') != -1:
                newNode['leftFlag'] = newNode['rightFlag'] = True
                self.right = Tree(newNode)
            elif self.checkLeafNode(newNode):
                self.data['rightFlag'] = True
            else:
                newNode['leftFlag'] = self.checkImmediate(newNode, True)
                newNode['rightFlag'] = self.checkImmediate(newNode, False)
                self.right = Tree(newNode)
            return True

        return False

    def checkLeafNode(self, newNode):    # check whether the current is the leaf node
        for type in range(len(ALUOp)):
            if newNode['opcode'].find(ALUOp[type]) == -1: continue
            return True
        return False

    def checkImmediate(self, newNode, left):
        if left:
            if newNode['src1'] is None: return True
            else:
                if newNode['src1'].find('#') != -1: return True
        else:
            if newNode['src2'] is None: return True
            else:
                fields = newNode['src2'].split(' ')
                if len(fields) == 1:
                    if fields[0].find('#') != -1:
                        return True
        return False

    '''def findDestNode(self, newNode):
        pattern = self.data['dest']
        if newNode['src1'] == None: return False
        if newNode['src2'] is None:
            if newNode['src1'].find(pattern) != -1:
                return True
        if newNode['src2'] is not None:
            if newNode['src1'].find(pattern) != -1 or newNode['src2'].find(pattern) != -1:
                return True
        return False

    def findStoreNode(self, newNode):
        pattern = self.data['dest']
        if newNode['opcode'].find('str') != -1:
            if newNode['dest'].find(pattern) != -1:
                return True
        return False'''

def postorderTraverse(tree, outfile):
    if tree is None: return
    postorderTraverse(tree.left, outfile)
    postorderTraverse(tree.right, outfile)
    if type(tree.data) == type({}):
        inst = tree.data['opcode'] + " "
        if tree.data['opcode'].find('str') != -1:
            inst += tree.data['src1']
            inst += " "
            inst += tree.data['dest']
            inst += ", "
        else:
            if 'dest' in tree.data.keys() and tree.data['dest'] is not None:
                inst += tree.data['dest']
                inst += ", "
            if 'src1' in tree.data.keys() and tree.data['src1'] is not None:
                inst += tree.data['src1']
                inst += " "
        if 'src2' in tree.data.keys() and tree.data['src2'] is not None:
            inst += tree.data['src2']
            inst += "  "
        outfile.write('%s %s %s' % (
            " ".ljust(15),
            inst.ljust(40),
            tree.data['seq'].rjust(15)
        ))
        outfile.write('\n')


'''def destNode(newNode, outfile):
    inst = newNode['opcode'] + " "
    if 'dest' in newNode.keys() and newNode['dest'] is not None:
        inst += newNode['dest']
        inst += ", "
    if 'src1' in newNode.keys() and newNode['src1'] is not None:
        inst += newNode['src1']
        inst += " "
    if 'src2' in newNode.keys() and newNode['src2'] is not None:
        inst += newNode['src2']
        inst += "  "
    outfile.write('%s %s' % (
        inst.ljust(30),
        newNode['seq'].rjust(10)
    ))
    outfile.write('\n')'''

def process_trace(trace, outfile):

    t = time()

    line = None
    fields = None

    # Skip lines up to the starting tick
    line = trace.readline()
    if not line: return
    fields = line.split()

    alu_num = 0
    ldr_num = 0
    str_num = 0

    while True:
        inst = {
            'opcode': None,
            'dest': None,
            'src1': None,
            'src2': None,
            'seq': 0,
            'CiM': False
        }
        line = trace.readline()
        if not line: break
        # parse current instruction, find the opcode, source and destination
        # operands, check whether the opcode is the CiM operaiton type
        fields = line.split()
        inst['opcode'] = str(fields[0])
        inst['seq'] = str(fields[-1])

        if len(fields) != 2:
            inst['dest'] = str((fields[1].split(','))[0])
            # process source operands
            src = fields[2:-1]
            if src is None:
                inst['src1'] = None
                inst['src2'] = None
            elif len(src) == 1:
                inst['src1'] = fields[2]
                inst['src2'] = None
            elif len(src) > 1:
                inst['src1'] = str(src[0])
                inst['src2'] = str(' '.join(src[1:]))

            # count different instruction number
            '''if inst['opcode'].find('ldr') != -1: ldr_num += 1
            elif inst['opcode'].find('str') != -1:
                temp = inst['src1']
                inst['src1'] = inst['dest']
                inst['dest'] = temp
                str_num += 1
            else:
                for type in range(len(ALUOp)):
                    if inst['opcode'].find(ALUOp[type]) == -1: continue
                    if inst['opcode'][0] == 'v': continue
                    alu_num += 1 
                    inst['CiM'] = True
                    break'''

        for type in range(len(ALUOp)):
            if inst['opcode'].find(ALUOp[type]) == -1: continue
            if inst['opcode'][0] == 'v': continue
            inst['CiM'] = True
            break

        # append pre-parsing instructions this set
        all_insts.append(inst)

    replace_pattern = 0


    for i in range(len(all_insts)):
        # satisfy CiM operation type, check whether operands are
        # accessed from or stored in memory
        cur_inst = all_insts[i]
        if cur_inst['CiM'] == False: continue

        # construct the root node of CiM tree, ['op', 'dest', 'src1', 'src2', 'seq', 'CiM']
        # pre-tree for detecting whether the source operands satisfy the rule
        cur_inst['leftFlag'] = cur_inst['rightFlag'] = False
        if cur_inst['src1'] is None: cur_inst['leftFlag'] = cur_inst['rightFlag'] = True
        elif cur_inst['src1'].find('#') != -1: cur_inst['leftFlag'] = True
        if cur_inst['src2'] is None: cur_inst['rightFlag'] = True
        else:
            fields = cur_inst['src2'].split(' ')
            if len(fields) == 1 and fields[0].find('#') != -1:
                cur_inst['rightFlag'] = True

        preTree = Tree(cur_inst)
        t = i
        flag = False

        while t > 1 and flag == False:
            t = t - 1
            all_insts[t]['leftFlag'] = all_insts[t]['rightFlag'] = False
            preTree.createTree(all_insts[t])
            flag = preTree.completeTree(preTree)

        replace_pattern = long(replace_pattern + 1)
        outfile.write('%s' % (
            ("#" + str(replace_pattern)).ljust(15),
        ))
        outfile.write('\n')


        postorderTraverse(preTree, outfile)


        '''flag = False
        t = i
        while flag == False:
            t = t + 1
            flag1 = postTree.findDestNode(all_insts[t])
            flag2 = postTree.findStoreNode(all_insts[i])
            flag = flag1 or flag2
        destNode(all_insts[t], outfile)'''

    print (time()-t)



def main():
    # Parse options
    usage = ('%prog [OPTION]... TRACE_FILE')
    parser = optparse.OptionParser(usage=usage)
    parser.add_option(
        '-o',
        dest='outfile',
        default=os.path.join(os.getcwd(), 'tree.out'),
        help="output file (default: '%default')")
    (options, args) = parser.parse_args()

    # recognize the pattern
    print 'parse trace... recognize pattern...',
    with open(args[0], 'r') as trace:
        with open(options.outfile, 'w') as out:
            process_trace(trace, out)

    print 'done!'


if __name__ == '__main__':
    sys.path.append(os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            '..', 'src', 'python'))
    main()
    #profile.run("main()")