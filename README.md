# Eva-CiM
Code of "Eva-CiM: A System-Level Performance and Energy Evaluation Framework for Computing-in-Memory Architectures", TCAD 2020

We assume the users are familiar with gem5 and mcpat:
1.	build and test gem5 correctly, make sure $GEM5_DIR/build/ARM/gem5.opt exists;
2.	install and test cross compiler (we use arm-linux-gnueabihf);
3.	build gem5-mcpat-parser, make sure $GEM5_DIR/power_tool/gem5-mcpat-parser/gem5-mcpat-parser exists;
4.	build mcpat, make sure $GEM5_DIR/power_tool/mcpat/mcpat exists.

Then, get started with Eva-CiM.
1.	Run gem5:
./$GEM5_DIR/run_gem5.sh $OUTPUT_DIR $APP_DIR
Then output the trace file, config.ini, stats.txt in $OUTPUT_DIR.
2.	Run traceTool:
python $GEM5_DIR/computecache/traceTool.py trace
Then output the counter.out file, which lists the incremental values of different instructions. 
3.	Run gem5-mcpat-parser to get the mcpat-cim-in.xml:
./$GEM5_DIR/power_tool/gem5-mcpat-parser/gem5-mcpat-parser
-x ./$GEM5_DIR/power_tool/gem5-mcpat-parser/ARM_A9_2GHz.xml
-c $OUTPUT_DIR/config.ini
-s $OUTPUT_DIR/stats.txt
-o mcpat-cim-in.xml
4.	Modify the performance counters in mcpat-cim-in.xml:
	python $GEM5_DIR/computecache/modify-counters.py 
	mcpat-cim-in.xml
	-i $OUTPUT_DIR/counter.out
	-o mcpat-cim-out.xml
	Then output mcpat-cim-in.xml to be fed to McPAT.
5.	Run McPAT to evaluate the energy:
	./$GEM5_DIR/power_tool/mcpat/mcpat
	-infile mcpat-cim-out.xml
