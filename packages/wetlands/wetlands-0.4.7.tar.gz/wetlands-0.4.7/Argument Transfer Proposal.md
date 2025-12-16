# Wetlands Argument Transfer Proposal

This document proposes a flexible, extensible **argument transfer system** for Wetlands.
Its goal is to allow functions executed inside isolated Conda environments to receive arguments using different transport mechanisms (pickle, shared memory, temporary files, image formats, user-defined serializers, etc.).

The system is designed to be:

* **Simple for users** (pickle by default)
* **Extensible** (plug in new strategies easily)
* **Type-aware** (NumPy arrays, images, etc. can auto-select the right strategy)
* **Explicit when needed** (per-call overrides)

---

# 1. Overview

When Wetlands executes a function inside an isolated Conda environment:

```python
result = env.execute("example.py", "segment", arg)
```

the argument `arg` must be transferred from the main process to the environment.
Currently, transfer is done through pickling. This proposal introduces a robust architecture supporting multiple transfer mechanisms.

---

# 2. Argument Transfer Strategies

Wetlands defines a base class:

```python
class ArgumentTransferStrategy:
    name: str  # unique identifier for the strategy

    def prepare_arg(self, arg) -> object:
        """Serialize or convert `arg` into a pickleable object."""

    def restore_arg(self, prepared: object):
        """Reconstruct the argument inside the isolated environment."""
```

A strategy consists of two steps:

| Stage           | Responsibility                                         |
| --------------- | ------------------------------------------------------ |
| **prepare_arg** | Runs in user environment → yields a pickleable object  |
| **restore_arg** | Runs inside isolated environment → rebuilds the object |

Each strategy has a **name**, which is used everywhere in the API.

---

# 3. Built-In Strategies

Wetlands ships with three core transfer strategies:

| Strategy               | Name              | Use Case                                |
| ---------------------- | ----------------- | --------------------------------------- |
| `PickleTransfer`       | `"pickle"`        | Default behavior for pickleable objects |
| `SharedMemoryTransfer` | `"shared_memory"` | NumPy-like arrays.             |
| `FileTransfer`         | `"file"`          | NumPy arrays (`np.load()` and `np.save()`), binary files (with python std lib) )  |

These are registered automatically.

---

# 4. Strategy Registry

Wetlands exposes a global registry for:

* registering new strategies
* associating Python types with strategy names
* looking up strategies during execution

```python
class ArgumentTransferRegistry:
    def register_strategy(self, strategy: ArgumentTransferStrategy):
        ...

    def unregister_strategy(self, name: str, *, force: bool = False):
    """
    If the strategy is still referenced by type mappings:
    - If force=False: raise an error.
    - If force=True: remove it and delete all associated type mappings.
    """
        ...

    def register_type(self, type_: type, strategy_name: str):
        ...

    def unregister_type(self, type: type):
        ...

    def get_strategy_by_name(self, name: str) -> ArgumentTransferStrategy:
        ...

    def resolve_for_arg(self, arg) -> ArgumentTransferStrategy:
        ...
```

### Example

```python
from wetlands.transfer import registry
from wetlands.transfer.strategies import FileTransfer
import numpy as np

registry.register_strategy(FileTransfer())
registry.register_type(np.ndarray, "file")
```

From this point forward, any NumPy array automatically uses the `"file"` strategy.

---

# 5. Environment Execution API

Wetlands uses this API to execute Python functions inside isolated environments:

```python
result = env.execute("example_module.py", "segment", args, transfer=None)
```

### Parameter: `transfer`

* **`None`** (default):
  Automatically choose the strategy based on the argument’s type.

* **Strategy name** (`"pickle"`, `"shared_memory"`, `"file"`, …):
  Explicitly select a strategy for this call.

### Per-Environment Default

Environments may specify a default transfer strategy:

```python
env = environmentManager.create(
    "myenv",
    deps={...},
    default_transfer="pickle"
)
```

This default applies when the strategy cannot be resolved via type-based rules.

---

# 6. Custom Strategies

Users can define custom strategies for new data types.

### Example: Image transfer using `imageio`

```python
from wetlands.transfer import ArgumentTransferStrategy, registry
import imageio, uuid

class ImageIOTransfer(ArgumentTransferStrategy):
    name = "imageio"

    def prepare_arg(self, image):
        path = f"/tmp/{uuid.uuid4().hex}.png"
        imageio.imwrite(path, image)
        return path

    def restore_arg(self, path):
        return imageio.imread(path)

registry.register_strategy(ImageIOTransfer())
registry.register_type(ImageClass, "imageio")
```

Now Wetlands automatically handles images using PNG encoding.

---

# 7. Full Example

```python
import numpy as np
from wetlands.environment_manager import EnvironmentManager
from wetlands.transfer import registry
from wetlands.transfer.strategies import FileTransfer

# Register a new strategy and associate numpy arrays with it
registry.register_strategy(FileTransfer())
registry.register_type(np.ndarray, "file")

# Create and launch isolated environment
env = EnvironmentManager().create("numpy_env", {"pip": ["numpy"]})
env.launch()

# Execute a function, transferring the ndarray via temporary file
result = env.execute(
    "example_module.py",
    "sum",
    np.array([1, 2, 3]),
    transfer=None
)

print(result)
env.exit()
```

---

# 8. Advantages

### ✔️ Extensible

Users can add new transfer mechanisms without modifying Wetlands itself.

### ✔️ Predictable

Strategy resolution is deterministic:
**per-call → per-type → environment default → pickle fallback**

### ✔️ Efficient

Large data can be sent via shared memory or temporary files instead of pickling.

### ✔️ Easy to use

Most users never need to worry about strategies—defaults work automatically.

---

# 9. Summary

This proposal introduces:

* A named `ArgumentTransferStrategy` base class
* Built-in transfer strategies (`pickle`, `shared_memory`, `file`)
* A registry for mapping types → strategies
* Per-environment and per-call strategy selection
* A clean API that integrates directly with Wetlands’ existing execution model:

  ```
  env.execute(module, function, arg, transfer="file")
  ```

The system is flexible, composable, and aligns with Wetlands’ design goals:
**isolated, reproducible, dynamic code execution with zero dependency conflicts.**













Problems:

Below is a clean **design for cleanup hooks** in your transfer-strategy API.
It is consistent with the rest of your proposal, keeps module boundaries clean, and guarantees that both **per-call temporary resources** and **global resources** are properly released.

---

# ✅ Design Goals

1. **Every transfer strategy can create temporary resources**
   (shared memory blocks, temp files, pipes, …)
   → It must be able to clean them.

2. **Cleanup must be reliable**

   * automatic whenever possible
   * manually invokable when executable modules want to be explicit
   * registry must support global cleanup if a strategy allocates global state

3. **Cleanup must not break sandboxing**
   → no implicit access to external runtime objects

4. **Hooks must be uniform across all strategies**
   → consistent for user-defined strategies

---

# 🎯 Proposal: Two Cleanup Hooks

We introduce **two cleanup layers**:

1. **Per-transfer cleanup**
   For temporary resources tied to a single execution of a function.

2. **Global strategy cleanup**
   For global resources created when a strategy is initialized or registered.

These correspond to:

```python
class TransferStrategy:
    def cleanup_transfer(self, handle: TransferHandle) -> None:
        ...

    def cleanup_global(self) -> None:
        ...
```

---

# 🔧 API: TransferHandle

When `prepare(...)` is called, the strategy **returns a handle** that contains all data needed for cleanup:

```python
@dataclass
class TransferHandle:
    payload: dict       # data passed to the callee
    resources: dict     # metadata needed to clean resources
```

The environment (`Wetlands`) ensures:

* It calls `cleanup_transfer(handle)` after the module finishes.
* It also offers `env.cleanup(handle)` for manual calls.

---

# 🧩 Full Strategy Interface

```python
class TransferStrategy(Protocol):

    def prepare(self, args: dict) -> TransferHandle:
        """
        Prepares arguments for transfer and returns both
        the payload and metadata for later cleanup.
        """
        ...

    def finalize(self, result_payload: dict) -> Any:
        """
        Converts the result payload back into Python objects.
        """
        ...

    def cleanup_transfer(self, handle: TransferHandle) -> None:
        """
        Cleans temporary resources created during prepare().
        """
        ...

    def cleanup_global(self) -> None:
        """
        Cleans global resources created by the strategy.
        Called when unregistering the strategy.
        """
        ...
```

---

# 🗄️ Registry with Cleanup

```python
class ArgumentTransferRegistry:

    def __init__(self):
        self._strategies = {}

    def register_strategy(self, name: str, strategy: TransferStrategy):
        self._strategies[name] = strategy

    def unregister_strategy(self, name: str, *, force=False):
        strategy = self._strategies.pop(name)
        strategy.cleanup_global()
```

---

# 🎮 Wetlands Runtime Responsibilities

### Automatic cleanup:

```python
handle = strategy.prepare(args)

try:
    result = env.execute(..., handle.payload)
finally:
    strategy.cleanup_transfer(handle)
```

### Manual cleanup:

```python
env.cleanup(handle)
```

---

# 🧹 Why This Works

| Problem                        | Solved by                     |
| ------------------------------ | ----------------------------- |
| Temporary shared memory blocks | `cleanup_transfer()`          |
| Temporary files                | `cleanup_transfer()`          |
| Global fd pools / shm managers | `cleanup_global()`            |
| User-defined strategies        | same consistent API           |
| Strategy unregistration leaks  | `cleanup_global()`            |
| Crashes or exception safety    | `finally: cleanup_transfer()` |

---

# 📝 Example: SharedMemoryTransfer Cleanup

```python
class SharedMemoryTransfer(TransferStrategy):

    def __init__(self):
        self._manager = multiprocessing.shared_memory._SharedMemoryTracker()

    def prepare(self, args):
        block = create_shared_block(args)
        return TransferHandle(
            payload={"shm_name": block.name},
            resources={"name": block.name}
        )

    def cleanup_transfer(self, handle):
        name = handle.resources["name"]
        try:
            shm = shared_memory.SharedMemory(name=name)
            shm.close()
            shm.unlink()
        except FileNotFoundError:
            pass

    def cleanup_global(self):
        self._manager.cleanup()   # or no-op if not needed
```

---

# 📝 Example: FileTransfer Cleanup

```python
class FileTransfer(TransferStrategy):

    def prepare(self, args):
        tmp = write_tempfile(args)
        return TransferHandle(
            payload={"path": tmp},
            resources={"path": tmp}
        )

    def cleanup_transfer(self, handle):
        try:
            os.remove(handle.resources["path"])
        except FileNotFoundError:
            pass

    def cleanup_global(self):
        pass  # nothing global
```

---

# ✔️ Summary

### You now have:

* Per-call cleanup
* Global cleanup
* Automatic cleanup by the environment
* Manual cleanup when needed
* Cleanup tied to a **TransferHandle** for reliability
* Safe unregistration of strategies
* Consistent API for user strategies

---

If you'd like, I can produce a **formal Markdown spec**, update the **proposal.md**, or generate **concrete implementations** for all default strategies.
