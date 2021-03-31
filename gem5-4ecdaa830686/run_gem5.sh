#!/bin/bash
#

# Firstly, build gem5 correctly. Please refer to http://www.gem5.org/documentation/learning_gem5/gem5_101/
# Secondly, install cross compiler for ARM architecture. Please refer to http://old.gem5.org/Compiling_workloads.html 

############ DIRECTORY VARIABLES: MODIFY ACCORDINGLY #############
GEM5_DIR="/home/data/gd/gem5-4ecdaa830686"                           # Install location of gem5
##################################################################


# Get command line input. We will need to check these.
OUTPUT_DIR=$1                  # Directory to place run output (e.g. trace file). Make sure this exists!
APP_DIR=$2					   # Directory to place the binary compiled from the application (e.g. C, C++).
##################################################################

# Check OUTPUT_DIR existence
if [[ !(-d "$OUTPUT_DIR") ]]; then
    echo "Output directory $OUTPUT_DIR does not exist! Exiting."
    exit 1
fi


#################### LAUNCH GEM5 SIMULATION ######################
# Actually launch gem5!
$GEM5_DIR/build/ARM/gem5.opt --debug-flags=InstProbe,PipeProbe,LoadFlag,HitFlag --debug-file=trace --outdir=$OUTPUT_DIR $GEM5_DIR/configs/example/se.py -F 100000 --warmup-insts=50000 -I 20000 --caches --l2cache --l1d_size=1MB --l1d_assoc=8 --l2_size=8MB --l2_assoc=16 --mem-size=4096MB --cpu-type=DerivO3CPU -c $APP_DIR 

