# Pythagoras Vocabulary (Glossary)

This glossary defines the key terms used in the Pythagoras project and API.

- Portal: A long-lived object encapsulating a working environment, storage, and execution policies. Different portal types add capabilities progressively (basic → ordinary → data → logging → safe → autonomous → protected → pure → swarming).

- BasicPortal: The foundational portal class that manages lifecycle and registration of portal-aware objects.

- OrdinaryCodePortal: Extends BasicPortal to work with decorated ordinary functions (no persistence/logging yet).

- DataPortal: Extends OrdinaryCodePortal with persistent storage for inputs, outputs, and metadata using persidict.

- LoggingCodePortal: Extends DataPortal with application-level and function-level logging (events, crashes, frames), capturing stdout/stderr and execution environment summaries.

- SafeCodePortal: Extends LoggingCodePortal with safer defaults for argument handling and execution bookkeeping.

- AutonomousCodePortal: Extends SafeCodePortal to enable self-scheduling and autonomous execution primitives.

- ProtectedCodePortal: Extends AutonomousCodePortal with validation and guards around function execution (pre/post validation hooks).

- PureCodePortal: Extends ProtectedCodePortal to support pure functions with deterministic caching keyed by code and arguments.

- SwarmingPortal: Extends PureCodePortal to provide asynchronous, distributed execution ("swarming") across processes or machines.

- PortalAwareClass: A base class for objects that need access to a portal instance and are intentionally not picklable.

- NotPicklableClass: A mixin/base class that prevents instances from being pickled for safety and correctness.

- PersiDict: A persistent dictionary abstraction used by portals to store parameters, execution results, requests, logs, and other data on disk or remote storage.

- Function Decorators: A family of decorators that create portal-bound callable wrappers with progressively more features:
  - ordinary: Basic wrapper around a Python function.
  - storable: Adds persistence of inputs/outputs (DataPortal).
  - logging: Adds execution logging and output capture (LoggingCodePortal).
  - safe: Safer execution defaults (SafeCodePortal).
  - autonomous: Enables autonomous scheduling (AutonomousCodePortal).
  - protected: Adds validation hooks and guards (ProtectedCodePortal).
  - pure: Declares a function as pure (deterministic, side-effect free) with persistent result caching (PureCodePortal).

- OrdinaryFn / StorableFn / LoggingFn / SafeFn / AutonomousFn / ProtectedFn / PureFn: The function wrapper classes created by the corresponding decorators. PureFn is the most feature-rich and is the typical user-facing class for deterministic computation.

- PureFnExecutionResultAddr: An address that uniquely identifies cached results of a PureFn call based on function identity, code, and packed arguments.

- HashAddr: A base address type that represents a hash-keyed location in persistent storage.

- ValueAddr: An address type for values stored in persistent storage.

- Call Signature (…FnCallSignature): An immutable description of a specific function call (function identity plus normalized/packed keyword arguments) used for caching, addressing, and logging.

- KwArgs / PackedKwArgs / UnpackedKwArgs: Utility classes that hold keyword arguments; PackedKwArgs is a normalized, canonical representation suitable for hashing and addressing.

- Validation (Validators): Functions and decorators used to enforce preconditions and postconditions around execution. Examples include:
  - pre_validators: Checks before running a function (e.g., resource availability).
  - post validators: Checks after running a function.
  - recursive_parameters: A helper indicating which parameters are recursive in mutual recursion scenarios.

- ValidationSuccessFlag (VALIDATION_SUCCESSFUL): A singleton marker object signaling that validation passed.

- Swarming: An asynchronous execution model where pure-function calls are enqueued and may be executed later by any available worker. Guarantees at least once eventual execution but not ordering or single execution.

- swarm(): A method on PureFn that queues an asynchronous execution request and returns an address for the future result.

- ready(address): A top-level API function to check if the result at a given address is available.

- get(address): A top-level API function to retrieve a result by its address (blocks or fails if not yet available, depending on configuration).

- fix_kwargs(...): A method on function wrappers (e.g., PureFn) that partially applies named arguments, returning a new callable with those parameters fixed.

- get_portal(root): A top-level API function that returns a portal instance bound to a storage root (local folder, S3, etc.).

- describe(): A method on portals returning a pandas DataFrame snapshot of the portal state (e.g., cached results, queues, workers).

- Execution Results: The persistent records storing outputs of function calls, typically under execution_results in PureCodePortal.

- Execution Requests: The persistent queue of requests to execute a function call (used by swarming to distribute work).

- Execution Environment Summary: A structured snapshot (OS, Python, packages, resources) captured for logging/troubleshooting.

- Compute Node: An entry representing a worker or process capable of executing queued requests within a SwarmingPortal.

Notes
- Only named arguments are allowed for decorated functions to ensure canonical argument packing and deterministic addressing.
- Source code changes in pure functions are tracked; changing code invalidates cache for the new version while preserving older results.
