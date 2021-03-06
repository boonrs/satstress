#!python
"""Check to see that satstress gives the expected output from a series
of known calculations.

Calculates the stresses due to the L{NSR} and L{Diurnal} forcings at a series
of lat lon points on Europa, over the course of most of an orbit, and also at a
variety of different amounts of viscous relaxation.  Compares the calculated
values to those listed in the the test ouput file distributed with satstress
(test/SS_test_calc.pkl).

C{test.py} is called from the C{satstress Makefile}, when one does C{make
test}.  It also acts as a short demonstration of how to use the satstress
package.

"""
import sys
import os
import pickle
import scipy
from satstress import *

def main():
    satstress_test_dir = os.path.dirname(os.path.abspath(__file__))
    test_outfile       = os.path.join(satstress_test_dir, "test_nsr_diurnal.pkl")
    test_satellite     = os.path.join("input", "Europa.satellite")

    # Create a new satellite object, as defined by the input file:
    the_sat = satstress.Satellite(open(test_satellite,'r'))

    # Create a StressCalc object, that calculates both the NSR and Diurnal
    # stresses on the Satellite just instantiated:
    the_stresses = satstress.StressCalc([satstress.Diurnal(the_sat), satstress.NSR(the_sat)])

    # do a series of calculations, varying all the inputs at each iteration
    theta = 0.0
    phi   = 0.0
    t     = 0.0

    # a list to store the calculation results in for later checking
    Taulist = []

    while the_stresses.stresses[1].Delta() > 0.01 and t < 2.0*scipy.pi/the_sat.mean_motion():
        print("""Tau(theta = %g, phi = %g, time = %g, Delta = %g) = """ % (scipy.degrees(theta), scipy.degrees(phi), t, the_stresses.stresses[1].Delta()))
        Taulist.append(the_stresses.tensor(theta=theta, phi=phi, t=0))
        print Taulist[-1], "\n"
        theta = theta + scipy.pi/23.0
        phi   = phi   + scipy.pi/11.0
        t     = t     + (scipy.pi/11.0)/the_sat.mean_motion()

        # Re-construct the NSR stress (and the_stresses StressCalc object)
        # changing the forcing period, so that we can have the NSR stresses
        # vary with each iteration too.
        the_sat.nsr_period = the_sat.nsr_period / 1.5
        the_stresses = satstress.StressCalc([satstress.Diurnal(the_sat), satstress.NSR(the_sat)])

    # Now we want to compare this against reference output, just to make sure
    # that we're getting the right numbers...

    pickledTau = pickle.load(open(test_outfile, 'r'))
    for (tau1, tau2) in zip(Taulist, pickledTau):
        if tau1.all() != tau2.all():
            print("\nTest failed.  :(\n")
            sys.exit(1)

    print("\nTest passed! :)\n")
    sys.exit()

if __name__ == "__main__":
    main()
