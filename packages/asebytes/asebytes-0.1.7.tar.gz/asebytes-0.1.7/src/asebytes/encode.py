import ase
import msgpack
import msgpack_numpy as m
import numpy as np


def encode(atoms: ase.Atoms) -> dict[bytes, bytes]:
    """
    Serialize an ASE Atoms object into a dictionary of bytes.

    Parameters
    ----------
    atoms : ase.Atoms
        Atoms object to serialize.

    Returns
    -------
    dict[bytes, bytes]
        Dictionary with byte keys and msgpack-serialized byte values.

    Raises
    ------
    TypeError
        If input is not an ase.Atoms object.
    """
    if not isinstance(atoms, ase.Atoms):
        raise TypeError("Input must be an ase.Atoms object.")
    data: dict[bytes, bytes] = {}
    cell: np.ndarray = atoms.get_cell().array
    data[b"cell"] = msgpack.packb(cell, default=m.encode)
    data[b"pbc"] = msgpack.packb(atoms.get_pbc(), default=m.encode)

    for key in atoms.arrays:
        data[f"arrays.{key}".encode()] = msgpack.packb(
            atoms.arrays[key], default=m.encode
        )
    for key in atoms.info:
        value = atoms.info[key]
        data[f"info.{key}".encode()] = msgpack.packb(value, default=m.encode)
    if atoms.calc is not None:
        for key in atoms.calc.results:
            value = atoms.calc.results[key]
            data[f"calc.{key}".encode()] = msgpack.packb(value, default=m.encode)

    # Serialize constraints
    if atoms.constraints:
        constraints_data = []
        for constraint in atoms.constraints:
            if isinstance(constraint, ase.constraints.FixConstraint):
                constraints_data.append(constraint.todict())
        if constraints_data:
            data[b"constraints"] = msgpack.packb(constraints_data, default=m.encode)

    return data
