"""提供与`cst.asymptotic`的接口。

Collection of tools related to the Asymptotic solver.

Asymptotic Solver Overview
====

An asymptotic computation is an analysis in the frequency domain based on a 
so-called ray-tracing (shooting and bouncing rays, SBR) technique. The rays can 
be either independent or bundled together in so called ray tubes. This solver is 
typically used for scattering or antenna placement computations of electrically 
very large objects, which are difficult to handle by other EM solution methods. 
The mesh generation is very robust and quite insensitive to the quality of the 
CAD model.

Please note: The solver currently only supports vacuum background materials and 
open boundary conditions.

 

Areas of application
---

- Monostatic and bistatic scattering computations for electrically very large 
PEC, surface impedance, perfect absorbing or thin dielectric type structures
- Antenna placement calculations for electrically large structures using 
nearfield sources and farfield sources
- Range profile and sinogram computations
- Very efficient frequency sweep capabilities for imaging applications
- Calculation of farfields and RCS, RCS maps and visualization of Hotspots
- Structure design by using the optimizer or the parameter sweep
- Near-field scattering analysis with field monitors on 2D Planes and field 
probes (E-Field / H-Field)
- Antenna coupling calculation between nearfield sources and farfield sources
- Field of View analysis
- Channel simulation

Supported Materials
---
- PEC
- Complex surface impedance materials
- Coated materials (incl. frequency-dependent and angle-dependent properties)
- Thin panel material (incl. frequency-dependent and angle-dependent properties)
- Perfect absorber

For material information please see also Material Parameters.

How to start the solver
---

Before you start the solver you should make all necessary settings. See therefore the Asymptotic Solver Settings overview. The asymptotic solver can be started from the Asymptotic Solver Parameters dialog box.

Solver logfile
---

After the solver has finished you can view the logfile by clicking Post Processing: Manage Results > Logfile  in the main menu. The logfile contains information about solver settings, mesh summary, solver results and solver statistics.

"""

from . import raydata
