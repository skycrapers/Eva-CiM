1. 
	'HitFlag': cache.trace
	'LoadFlag': request.trace
	'Pipeline': pipeline.out
	'O3PipeView': trace.out

2.
	./parse-trace.py trace.out -o o3-trace.out

3.
	./gene_tree.py o3-trace.out -o tree.out

4.
	./parse-memory-access.py request.trace --cache cache.trace -o access.out

5. 
	./modify-tree.py tree.out -a access.out -o tree-memoryaccess.out

6.
	./gene_replace_result.py tree-memoryaccess.out --trace o3-trace.out -p pipeline.out -o replace-results.out

7. 
	./modify-counters.py macpt-in.xml -r replace-results.out -o mcpat-cim-in.xml

runspec --action=build --config=my-arm.cfg --tune=base bzip2
< full path >
sudo ./run_gem5_arm_spec06_benchmark.sh bzip2  /home/gd/gem5/gem5-4ecdaa830686/m5out/spec/bzip2 

