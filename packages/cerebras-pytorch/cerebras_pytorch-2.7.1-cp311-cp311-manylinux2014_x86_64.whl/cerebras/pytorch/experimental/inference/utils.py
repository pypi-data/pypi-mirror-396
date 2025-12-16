# Copyright 2016-2024 Cerebras Systems
# SPDX-License-Identifier: BSD-3-Clause

import enum
import functools
from typing import Callable, Optional

import torch

import cerebras.pytorch as cstorch
import cerebras.pytorch.nn.functional as F
from cerebras.pytorch.lib import cerebras_pytorch_lib


def hoist_function(func: Callable) -> Callable:
    """Decorator to add hints for compiler to hoist function.

    Name of the hoisted function should be unique. Nested hoisting is not
    allowed. The checks are not thread-safe but it is okay as tracing is not
    multithreaded.
    """
    magic_str = f"FUNC_{func.__name__}"
    if magic_str in hoist_function.hoisted:
        raise ValueError(
            f"There is already a hoisted function of the same name '{func.__name__}'."
        )
    hoist_function.hoisted.add(magic_str)

    def collect_tensors(args, kwargs):
        tensors = []

        def append_tensor(arg):
            if isinstance(arg, torch.Tensor):
                tensors.append(arg)
            return arg

        torch.utils._pytree.tree_map(append_tensor, (args, kwargs))
        return tensors

    def map_tensors(tensors, replacements, args, kwargs):
        d = dict(zip(tensors, replacements))

        def map_fn(arg):
            if isinstance(arg, torch.Tensor):
                return d.get(arg, arg)
            return arg

        return torch.utils._pytree.tree_map(map_fn, (args, kwargs))

    def enter_scope(*args, **kwargs):
        if not cstorch.use_cs():
            return args, kwargs

        tensors = collect_tensors(args, kwargs)
        replacements = cstorch.cirh.ScopeBoundary(
            tensors, boundary_type=F.BEGIN_FORWARD, scope_name=magic_str
        )

        return map_tensors(tensors, replacements, args, kwargs)

    def exit_scope(args):
        if not cstorch.use_cs():
            return args

        tensors = collect_tensors(args, {})
        replacements = cstorch.cirh.ScopeBoundary(
            tensors, boundary_type=F.END_FORWARD, scope_name=magic_str
        )

        args, _ = map_tensors(tensors, replacements, args, {})
        return args

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if hoist_function.hoisting is not None:
            raise ValueError(
                f"Nested hoisting of '{func.__name__}' under '{hoist_function.hoisting}' is not allowed."
            )

        hoist_function.hoisting = func.__name__
        args, kwargs = enter_scope(*args, **kwargs)
        results = exit_scope(func(*args, **kwargs))
        hoist_function.hoisting = None
        return results

    return wrapper


hoist_function.hoisted = set()  # Set of hoisted function names.
hoist_function.hoisting = None  # Current function begin hoisted.


class TensorID(enum.IntEnum):
    """Special IDs expected by the runtime.

    Keep in sync with src/ws/stack/ws-run/Inference/InferenceCommon.h -
    InferenceConstants.
    """

    DATA = 0
    METADATA = 1
    EMBEDDING = 6
    DEEMBEDDING = 7
    NORM = 8
    OUT_OFFSET = 10
    TOP_K_INTERLEAVED = 996


def register_id(tensor: torch.Tensor, tensor_id: Optional[TensorID] = None):
    """Register tensor id.

    NOTE: Use only with block args or def ops producing single output.

    For inputs use before first use. For outputs use before last use.
    """
    if not cstorch.use_cs():
        return
    if tensor_id is not None:
        cerebras_pytorch_lib.set_attribute(
            tensor, "cs.inf_tensor_id_override", tensor_id.value
        )


def register_id_with_op(tensor: torch.Tensor, tensor_id: TensorID):
    """Register tensor id.

    NOTE: set_attribute on a tensor approach doesn't work when the defining op
    is producing multiple outputs. The attr on the defining op will be overwritten.

    Insert an identity op, set attr on it and return the new tensor.

    For inputs use before first use. For outputs use before last use.
    """
    if not cstorch.use_cs():
        return tensor

    (tensor,) = cstorch.cirh.ScopeBoundary(
        (tensor,),
        boundary_type=cstorch.nn.functional.BEGIN_FORWARD,
        scope_name="_tensor_attrs",
    )
    cerebras_pytorch_lib.set_attribute(
        tensor,
        "cs.internal",
        {"cs.inf_tensor_id_override": tensor_id.value},
    )
    return tensor


def register_weight(tensor: torch.Tensor, tensor_id: Optional[TensorID] = None):
    """
    Forcing ws_km.load_input for weights.
    """
    if not cstorch.use_cs():
        return
    cerebras_pytorch_lib.set_attribute(tensor, "cs.static_input", True)
    register_id(tensor, tensor_id)  # Safe as weights are block args.


def register_state(tensor: torch.Tensor):
    """
    Forcing ws_km.load_state for nn.Module buffer.
    """
    if not cstorch.use_cs():
        return
    cerebras_pytorch_lib.set_attribute(tensor, "cs.state_buffer", True)


def register_kv_cache(tensor: torch.Tensor):
    """
    Forcing ws_km.load_state for nn.Module buffer.
    Also setting kvCacheContentType and s_dim_axis attributes.
    """
    if not cstorch.use_cs():
        return
    register_state(tensor)
    cerebras_pytorch_lib.set_attribute(tensor, "cs.kvCacheContentType", True)
    cerebras_pytorch_lib.set_attribute(tensor, "cs.s_dim_axis", 1)
