# asebytes

Efficient serialization and storage for ASE Atoms objects using LMDB.

## API

- **`encode(atoms)`** - Encode an ASE Atoms object to a dict of bytes
- **`decode(data)`** - Decode bytes back into an ASE Atoms object
- **`BytesIO(file, prefix)`** - LMDB-backed list-like storage for bytes dictionaries
- **`ASEIO(file, prefix)`** - LMDB-backed list-like storage for ASE Atoms objects

## Examples

```python
from asebytes import ASEIO, BytesIO, encode, decode
import molify

# Generate conformers from SMILES
ethanol = molify.smiles2conformers("CCO", numConfs=100)

# Serialize/deserialize single molecule
data = encode(ethanol[0])
atoms_restored = decode(data)

# High-level: Store Atoms objects directly
db = ASEIO("conformers.lmdb")
db.extend(ethanol)  # Add all conformers
mol = db[0]         # Returns ase.Atoms

# Low-level: BytesIO stores serialized data
bytes_db = BytesIO("conformers.lmdb")
bytes_db.append(encode(ethanol[0]))      # Manual serialization
data = bytes_db[0]                       # Returns dict[bytes, bytes]
mol = decode(data)                       # Manual deserialization

# ASEIO = BytesIO + automatic encode/decode
```
