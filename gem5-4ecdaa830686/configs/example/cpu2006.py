#Mybench.py

import m5
from m5.objects import *
m5.util.addToPath('../common')

binary_dir = '/home/gd/gem5/installspec06/benchspec/CPU2006/'
data_dir = '/home/gd/gem5/installspec06/benchspec/CPU2006/'

#====================
#400.perlbench
perlbench = Process()
perlbench.executable =  binary_dir+'400.perlbench/exe/perlbench_base.gcc41-64bit'
data=data_dir+'400.perlbench/data/test/input/makerand.pl'
perlbench.cmd = [perlbench.executable] + [data]
perlbench.output = 'attrs.out'

#401.bzip2
bzip2 = Process()
bzip2.executable =  binary_dir+'401.bzip2/exe/bzip2_base.gcc41-64bit'
data=data_dir+'401.bzip2/data/all/input/input.program'
bzip2.cmd = [bzip2.executable] + [data, '1']
bzip2.output = 'input.program.out'

#====================
#403.gcc
gcc = Process()
gcc.executable =  binary_dir+'403.gcc/exe/gcc_base.gcc41-64bit'
data=data_dir+'403.gcc/data/test/input/cccp.i'
output='/home/wyj/installspec2006/benchspec/CPU2006/403.gcc/data/test/output/cccp.s'
gcc.cmd = [gcc.executable] + [data]+['-o',output]
gcc.output = 'ccc.out'

#410.bwaves
bwaves = Process()
bwaves.executable =  binary_dir+'410.bwaves/exe/bwaves_base.gcc41-64bit'
data=data_dir+'410.bwaves/data/test/input/bwaves.in'
bwaves.cmd = [bwaves.executable]

#====================
#416.gamess
gamess=Process()
gamess.executable =  binary_dir+'416.gamess/exe/gamess_base.gcc41-64bit'
gamess.cmd = [gamess.executable]
gamess.input='exam29.config'
gamess.output='exam29.output'

#429.mcf
mcf = Process()
mcf.executable =  binary_dir+'429.mcf/exe/mcf_base.gcc41-64bit'
data=data_dir+'429.mcf/data/test/input/inp.in'
mcf.cmd = [mcf.executable] + [data]
mcf.output = 'inp.out'

#====================
#433.milc
milc=Process()
milc.executable = binary_dir+'433.milc/exe/milc_base.gcc41-64bit'
stdin=data_dir+'433.milc/data/test/input/su3imp.in'
milc.cmd = [milc.executable]
milc.input=stdin
milc.output='su3imp.out'

#====================
#434.zeusmp
zeusmp=Process()
zeusmp.executable =  binary_dir+'434.zeusmp/exe/zeusmp_base.gcc41-64bit'
zeusmp.cmd = [zeusmp.executable]
zeusmp.output = 'zeusmp.stdout'

#====================
#435.gromacs
gromacs = Process()
gromacs.executable =  binary_dir+'435.gromacs/exe/gromacs_base.gcc41-64bit'
data=data_dir+'435.gromacs/data/test/input/gromacs.tpr'
gromacs.cmd = [gromacs.executable] + ['-silent','-deffnm',data,'-nice','0']

#====================
#436.cactusADM
cactusADM = Process()
cactusADM.executable =  binary_dir+'436.cactusADM/exe/cactusADM_base.gcc41-64bit'
data=data_dir+'436.cactusADM/data/test/input/benchADM.par'
cactusADM.cmd = [cactusADM.executable] + [data]
cactusADM.output = 'benchADM.out'

#437.leslie3d
leslie3d=Process()
leslie3d.executable =  binary_dir+'437.leslie3d/exe/leslie3d_base.gcc41-64bit'
stdin=data_dir+'437.leslie3d/data/test/input/leslie3d.in'
leslie3d.cmd = [leslie3d.executable]
leslie3d.input=stdin
leslie3d.output='leslie3d.stdout'

#444.namd
namd = Process()
namd.executable =  binary_dir+'444.namd/exe/namd_base.gcc41-64bit'
input=data_dir+'444.namd/data/all/input/namd.input'
namd.cmd = [namd.executable] + ['--input',input,'--iterations','1','--output','namd.out']
namd.output='namd.stdout'

#445.gobmk
gobmk=Process()
gobmk.executable =  binary_dir+'445.gobmk/exe/gobmk_base.gcc41-64bit'
stdin=data_dir+'445.gobmk/data/test/input/capture.tst'
gobmk.cmd = [gobmk.executable]+['--quiet','--mode','gtp']
gobmk.input=stdin
gobmk.output='capture.out'

#====================
#447.dealII
dealII=Process()
dealII.executable =  binary_dir+'447.dealII/exe/dealII_base.gcc41-64bit'
dealII.cmd = [gobmk.executable]+['8']
dealII.output='log'


#450.soplex
soplex=Process()
soplex.executable =  binary_dir+'450.soplex/exe/soplex_base.gcc41-64bit'
data=data_dir+'450.soplex/data/test/input/test.mps'
soplex.cmd = [soplex.executable]+['-m10000',data]
soplex.output = 'test.out'

#453.povray
povray=Process()
povray.executable =  binary_dir+'453.povray/exe/povray_base.gcc41-64bit'
data=data_dir+'453.povray/data/test/input/SPEC-benchmark-test.ini'
#povray.cmd = [povray.executable]+['SPEC-benchmark-test.ini']
povray.cmd = [povray.executable]+[data]
povray.output = 'SPEC-benchmark-test.stdout'

#454.calculix
calculix=Process()
calculix.executable =  binary_dir+'454.calculix/exe/calculix_base.gcc41-64bit'
data=data_dir+'454.calculix/data/test/input/beampic'
calculix.cmd = [calculix.executable]+['-i',data]
calculix.output = 'beampic.log'

#456.hmmer
hmmer=Process()
hmmer.executable =  binary_dir+'456.hmmer/exe/hmmer_base.gcc41-64bit'
data=data_dir+'456.hmmer/data/test/input/bombesin.hmm'
hmmer.cmd = [hmmer.executable]+['--fixed', '0', '--mean', '325', '--num', '5000', '--sd', '200', '--seed', '0', data]
hmmer.output = 'bombesin.out'

#458.sjeng
sjeng=Process()
sjeng.executable =  binary_dir+'458.sjeng/exe/sjeng_base.gcc41-64bit'
data=data_dir+'458.sjeng/data/test/input/test.txt'
sjeng.cmd = [sjeng.executable]+[data]
sjeng.output = 'test.out'

#459.GemsFDTD
GemsFDTD=Process()
GemsFDTD.executable =  binary_dir+'459.GemsFDTD/exe/GemsFDTD_base.gcc41-64bit'
GemsFDTD.cmd = [GemsFDTD.executable]
GemsFDTD.output = 'test.log'

#462.libquantum
libquantum=Process()
libquantum.executable =  binary_dir+'462.libquantum/exe/libquantum_base.gcc41-64bit'
libquantum.cmd = [libquantum.executable],'33','5'
libquantum.output = 'test.out'

#464.h264ref
h264ref=Process()
h264ref.executable =  binary_dir+'464.h264ref/exe/h264ref_base.gcc41-64bit'
data=data_dir+'464.h264ref/data/test/input/foreman_test_encoder_baseline.cfg'
h264ref.cmd = [h264ref.executable]+['-d',data]
h264ref.output = 'foreman_test_encoder_baseline.out'

#470.lbm
lbm=Process()
lbm.executable =  binary_dir+'470.lbm/exe/lbm_base.gcc41-64bit'
data=data_dir+'470.lbm/data/test/input/100_100_130_cf_a.of'
lbm.cmd = [lbm.executable]+['20', 'reference.dat', '0', '1' ,data]
lbm.output = 'lbm.out'

#471.omnetpp
omnetpp=Process()
omnetpp.executable =  binary_dir+'471.omnetpp/exe/omnetpp_base.gcc41-64bit'
data=data_dir+'471.omnetpp/data/test/input/omnetpp.ini'
omnetpp.cmd = [omnetpp.executable]+[data]
omnetpp.output = 'omnetpp.log'

#====================
#473.astar
astar=Process()
astar.executable =  binary_dir+'473.astar/exe/astar_base.gcc41-64bit'
astar.cmd = [astar.executable]+['lake.cfg']
astar.output = 'lake.out'

#====================
#481.wrf
wrf=Process()
wrf.executable =  binary_dir+'481.wrf/exe/wrf_base.gcc41-64bit'
wrf.cmd = [wrf.executable]+['namelist.input']
wrf.output = 'rsl.out.0000'

#482.sphinx
sphinx3=Process()
sphinx3.executable =  binary_dir+'482.sphinx3/exe/sphinx_livepretend_base.gcc41-64bit'
sphinx3.cmd = [sphinx3.executable]+['ctlfile', '.', 'args.an4']
sphinx3.output = 'an4.out'

#483.xalancbmk
xalancbmk=Process()
xalancbmk.executable =  binary_dir+'483.xalancbmk/exe/Xalan_base.gcc41-64bit'
xalancbmk.cmd = [xalancbmk.executable]+['-v','test.xml','xalanc.xsl']
xalancbmk.output = 'test.out'

#998.specrand
specrand_i=Process()
specrand_i.executable = binary_dir+'998.specrand/exe/specrand_base.gcc41-64bit'
specrand_i.cmd = [specrand_i.executable] + ['324342','24239']
specrand_i.output = 'rand.24239.out'

#999.specrand
specrand_f=Process()
specrand_f.executable = binary_dir+'999.specrand/exe/specrand_base.gcc41-64bit'
specrand_f.cmd = [specrand_i.executable] + ['324342','24239']
specrand_f.output = 'rand.24239.out'