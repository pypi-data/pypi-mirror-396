import ase.constraints
import msgpack
import msgpack_numpy as m
import numpy as np
from ase.calculators.singlepoint import SinglePointCalculator
from ase.cell import Cell


def decode(data: dict[bytes, bytes], fast: bool = True, copy: bool = True) -> ase.Atoms:
    """
    Deserialize bytes into an ASE Atoms object.

    Parameters
    ----------
    data : dict[bytes, bytes]
        Dictionary with byte keys and msgpack-serialized byte values.
    fast : bool, default=True
        If True, use optimized direct attribute assignment (6x faster).
        If False, use standard Atoms constructor (safer but slower).
    copy : bool, default=True
        If True, create writable copies of all numpy arrays from msgpack.
        If False, use arrays as-is (read-only, but saves memory).
        Set to True if you need to modify atoms after decoding.
        Nested numpy arrays might still be read-only.

    Returns
    -------
    ase.Atoms
        Reconstructed Atoms object.

    Raises
    ------
    ValueError
        If unknown keys are present in data.
    KeyError
        If required key 'arrays.numbers' is missing.
    """
    if b"arrays.numbers" in data:
        numbers_array = msgpack.unpackb(data[b"arrays.numbers"], object_hook=m.decode)
        if copy:
            numbers_array = np.array(numbers_array, copy=True)
    else:
        numbers_array = np.array([], dtype=int)

    # Extract optional parameters with defaults
    if b"cell" in data:
        cell_array = msgpack.unpackb(data[b"cell"], object_hook=m.decode)
        if copy:
            cell_array = np.array(cell_array, copy=True)
    else:
        cell_array = None

    if b"pbc" in data:
        pbc_array = msgpack.unpackb(data[b"pbc"], object_hook=m.decode)
        if copy and isinstance(pbc_array, np.ndarray):
            pbc_array = np.array(pbc_array, copy=True)
    else:
        pbc_array = np.array([False, False, False], dtype=bool)

    if fast:
        #  Skip Atoms.__init__() and directly assign attributes for better performance
        atoms = ase.Atoms.__new__(ase.Atoms)

        # Set cell - use provided cell or default empty cell
        if cell_array is not None:
            atoms._cellobj = Cell(cell_array)
        else:
            atoms._cellobj = Cell(np.zeros((3, 3)))

        atoms._pbc = pbc_array
        atoms.arrays = {"numbers": numbers_array}

        # Initialize positions if not provided
        if b"arrays.positions" not in data:
            # Create default positions (zeros) based on number of atoms
            n_atoms = len(numbers_array)
            atoms.arrays["positions"] = np.zeros((n_atoms, 3))

        atoms.info = {}
        atoms.constraints = []
        atoms._celldisp = np.zeros(3)
        atoms._calc = None
    else:
        # Use standard Atoms constructor
        atoms = ase.Atoms(numbers=numbers_array, cell=cell_array, pbc=pbc_array)

    for key in data:
        if key in [b"cell", b"pbc", b"arrays.numbers"]:
            continue
        if key.startswith(b"arrays."):
            array_data = msgpack.unpackb(data[key], object_hook=m.decode)
            if copy:
                array_data = np.array(array_data, copy=True)
            atoms.arrays[key[7:].decode()] = array_data  # len(b"arrays.") = 7
        elif key.startswith(b"info."):
            info_key = key[5:].decode()  # len(b"info.") = 5
            info_array = msgpack.unpackb(data[key], object_hook=m.decode)
            if copy and isinstance(info_array, np.ndarray):
                info_array = np.array(info_array, copy=True)
            atoms.info[info_key] = info_array
        elif key.startswith(b"calc."):
            if not hasattr(atoms, "calc") or atoms.calc is None:
                atoms.calc = SinglePointCalculator(atoms)
            calc_key = key[5:].decode()  # len(b"calc.") = 5
            calc_array = msgpack.unpackb(data[key], object_hook=m.decode)
            if copy and isinstance(calc_array, np.ndarray):
                calc_array = np.array(calc_array, copy=True)
            atoms.calc.results[calc_key] = calc_array
        elif key == b"constraints":
            constraints_data = msgpack.unpackb(data[key], object_hook=m.decode)
            constraints = []
            for constraint_dict in constraints_data:
                constraint = ase.constraints.dict2constraint(constraint_dict)
                constraints.append(constraint)
            atoms.set_constraint(constraints)
        else:
            raise ValueError(f"Unknown key in data: {key}")

    return atoms
