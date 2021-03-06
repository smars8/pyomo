#  _________________________________________________________________________
#
#  Pyomo: Python Optimization Modeling Objects
#  Copyright (c) 2014 Sandia Corporation.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  This software is distributed under the BSD License.
#  _________________________________________________________________________

#
# Test the mpec_minlp solver
#

import sys
import os
from os.path import abspath, dirname, normpath, join
currdir = dirname(abspath(__file__))
exdir = normpath(join(currdir,'..','..','..','examples','mpec'))

import pyutilib.th as unittest

import pyomo.opt
import pyomo.scripting.pyomo_main as pyomo_main
from pyomo.scripting.util import cleanup
from pyomo.environ import *

from six import iteritems

try:
    import yaml
    yaml_available=True
except ImportError:
    yaml_available=False

solver = pyomo.opt.load_solvers('cplex', 'glpk')

class CommonTests:

    solve = True
    solver='mpec_minlp'

    def run_solver(self, *_args, **kwds):
        if self.solve:
            args = ['solve']
            if 'solver' in kwds:
                _solver = kwds.get('solver','glpk')
                args.append('--solver='+self.solver)
                args.append('--solver-options="solver=%s"' % _solver)
            args.append('--save-results=result.yml')
            args.append('--results-format=yaml')
        else:
            args = ['convert']
        args.append('-c')

        # These were being ignored by the solvers for this package,
        # which now causes a helpful error message.
        #args.append('--symbolic-solver-labels')
        #args.append('--file-determinism=2')

        if False:
            args.append('--stream-solver')
            args.append('--tempdir='+currdir)
            args.append('--keepfiles')
            args.append('--logging=debug')

        args = args + list(_args)
        os.chdir(currdir)

        print('***')
        #print(' '.join(args))
        try:
            output = pyomo_main.main(args)
        except SystemExit:
            output = None
        except:
            output = None
            raise
        cleanup()
        print('***')
        return output

    def referenceFile(self, problem, solver):
        return join(currdir, problem+'.txt')

    def getObjective(self, fname):
        FILE = open(fname,'r')
        data = yaml.load(FILE)
        FILE.close()
        solutions = data.get('Solution', [])
        ans = []
        for x in solutions:
            ans.append(x.get('Objective', {}))
        return ans

    def updateDocStrings(self):
        for key in dir(self):
            if key.startswith('test'):
                getattr(self,key).__doc__ = " (%s)" % getattr(self,key).__name__

    def test_linear1(self):
        self.problem='test_linear1'
        self.run_solver( join(exdir,'linear1.py') )
        self.check( 'linear1', self.solver )

    def test_scholtes4(self):
        self.problem='test_scholtes4'
        self.run_solver( join(exdir,'scholtes4.py') )
        self.check( 'scholtes4', self.solver )

    def check(self, problem, solver):
        refObj = self.getObjective(self.referenceFile(problem,solver))
        ansObj = self.getObjective(join(currdir,'result.yml'))
        self.assertEqual(len(refObj), len(ansObj))
        for i in range(len(refObj)):
            self.assertEqual(len(refObj[i]), len(ansObj[i]))
            for key,val in iteritems(refObj[i]):
                self.assertAlmostEqual(val['Value'], ansObj[i].get(key,None)['Value'], places=3)


@unittest.skipIf(not yaml_available, "YAML is not available")
@unittest.skipIf(solver['glpk'] is None, "The 'glpk' executable is not available")
class Solve_GLPK(unittest.TestCase, CommonTests):

    def tearDown(self):
        if os.path.exists(os.path.join(currdir,'result.yml')):
            os.remove(os.path.join(currdir,'result.yml'))

    def run_solver(self,  *args, **kwds):
        kwds['solver'] = 'glpk'
        CommonTests.run_solver(self, *args, **kwds)


@unittest.skipIf(not yaml_available, "YAML is not available")
@unittest.skipIf(solver['cplex'] is None, "The 'cplex' executable is not available")
class Solve_CPLEX(unittest.TestCase, CommonTests):

    def tearDown(self):
        if os.path.exists(os.path.join(currdir,'result.yml')):
            os.remove(os.path.join(currdir,'result.yml'))

    def run_solver(self,  *args, **kwds):
        kwds['solver'] = 'cplex'
        CommonTests.run_solver(self, *args, **kwds)


if __name__ == "__main__":
    unittest.main()
