# Concrete Sample Generator

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

A Blender add-on for generating geometrical models of concrete and other multiphase granular materials, intended for **mesoscale modelling**. It uses Blender's rigid-body physics engine to simulate the gravitational settling, collision and vibration-assisted compaction of particles inside a user-defined mold. The output is a dense, interlocked particle skeleton that can be exported to numerical simulation software.

## Features

The add-on interface has three modules:

1. **Mold generator**
   Creates a mold of user-defined shape and dimensions. You can remove the top and bottom covers with one click so that particles can fall into the mold.

2. **Rigid body settings**
   Sets the physical parameters of the mold and the particles before the simulation. Particle mass can be either
   - user-defined, or
   - calculated from each object's volume and a given density.

   This lets you adapt the packing simulation to different materials and use cases.

3. **Vibration settings**
   Applies a sinusoidal vibration to the mold to improve compaction. You can set the vibration's
   - direction,
   - amplitude,
   - frequency,
   - offset,

   as well as the frame range of the simulation.

## Requirements

- Blender <!-- TODO: tested version, e.g. 3.6 LTS / 4.x -->

## Installation

1. Download the add-on from the [latest release](../../releases) (`.zip` file; do not unzip it).
2. In Blender, open **Edit → Preferences → Add-ons → Install…**, then select the `.zip` file.
3. Enable **Concrete Sample Generator** in the add-on list.
4. Open the panel at <!-- TODO: e.g. 3D Viewport → Sidebar (N) → "Concrete Generator" tab -->.

## Basic workflow

1. Import or generate the aggregate particles (e.g. with the [Digital Aggregate Generator](https://github.com/ShayHu-Git/Digital-aggregate-generator)).
2. Create the mold in the **Mold generator** module and remove the top cover.
3. Assign rigid-body properties and masses in **Rigid body settings**.
4. Define the vibration and the frame range in **Vibration settings**.
5. Run the simulation. When the particles have settled, apply the final transforms and export the packed geometry for mesoscale analysis.

## Citation

If you use this tool in your research, please cite:

> Hu, X., Wan-Wendner, L., Molkens, T., & Gruyaert, E. (2025). Statistical generation of 3D mesoscale model for recycled aggregate concrete. *Construction and Building Materials*, 476, 141096. https://doi.org/10.1016/j.conbuildmat.2025.141096

```bibtex
@article{Hu2025RAC,
  author  = {Hu, Xingyi and Wan-Wendner, Lin and Molkens, Tom and Gruyaert, Elke},
  title   = {Statistical generation of 3D mesoscale model for recycled aggregate concrete},
  journal = {Construction and Building Materials},
  volume  = {476},
  pages   = {141096},
  year    = {2025},
  doi     = {10.1016/j.conbuildmat.2025.141096}
}
```

## License

Released under the MIT License. See [LICENSE](LICENSE).

## Contact

Xingyi Hu, KU Leuven, xingyi.hu@kuleuven.be or huxingyi3148@gmail.com
