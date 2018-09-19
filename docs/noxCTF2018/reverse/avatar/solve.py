from z3 import *
import os
solver = Solver()
source = BitVec('source', 64)
x = Int('x')

solver.add((((14 * (((source | 0x40) - 87254612 + 123456) | 0x10000) >> 1) - 999534204) & 0xFFFFFFFFFFFF7FFF ^ 0x6E988) == 1983969333457)
solver.add(source != 283654106647)
print("Solving...")
print solver.check()
print solver.model()
# flag: noxCTF{Fu11_M00n-Th3_Bl1nd_0n3-420B1A2E17-B41dy}
