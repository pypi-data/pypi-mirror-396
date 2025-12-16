"""
Device capability discovery and kernel strategy selection.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

try:
    import pyopencl as cl  # type: ignore
except ImportError:  # pragma: no cover
    cl = None

NETCL_KERNEL_STRATEGY = os.environ.get("NETCL_KERNEL_STRATEGY", "").lower()


@dataclass(frozen=True)
class DeviceProfile:
    name: str
    vendor: str
    device_type: str
    compute_units: int
    max_work_group_size: int
    max_work_item_sizes: tuple[int, int, int]
    global_mem_size: int
    local_mem_size: int
    preferred_vector_width_float: int
    extensions: tuple[str, ...]
    opencl_c_version: str
    has_fp16: bool
    has_subgroups: bool
    is_cpu: bool
    tiny_local_mem: bool
    fast_atomics: bool
    supports_fp16: bool = False


_PROFILE_CACHE: dict[str, DeviceProfile] = {}


def device_profile(device) -> DeviceProfile:
    if cl is None:
        raise ImportError("pyopencl required for capability discovery")
    key = getattr(device, "hash", None)
    if key is None:
        key = getattr(device, "name", "unknown")
    if key in _PROFILE_CACHE:
        return _PROFILE_CACHE[key]
    vendor = device.vendor
    name = device.name
    device_type = str(device.type)
    compute_units = int(device.max_compute_units)
    max_work_group_size = int(device.max_work_group_size)
    max_work_item_sizes = tuple(int(x) for x in device.max_work_item_sizes)
    global_mem_size = int(device.global_mem_size)
    local_mem_size = int(device.local_mem_size)
    preferred_vector_width_float = int(device.preferred_vector_width_float)
    extensions = tuple(device.extensions.strip().split())
    opencl_c_version = device.opencl_c_version
    has_fp16 = any("fp16" in ext.lower() for ext in extensions) or "cl_khr_fp16" in extensions
    has_subgroups = any("subgroup" in ext.lower() for ext in extensions)
    is_cpu = "cpu" in device_type.lower()
    tiny_local_mem = local_mem_size < 24 * 1024
    fast_atomics = any(ext in extensions for ext in ("cl_khr_int64_base_atomics", "cl_khr_int64_extended_atomics"))
    profile = DeviceProfile(
        name=name,
        vendor=vendor,
        device_type=device_type,
        compute_units=compute_units,
        max_work_group_size=max_work_group_size,
        max_work_item_sizes=max_work_item_sizes,  # type: ignore[arg-type]
        global_mem_size=global_mem_size,
        local_mem_size=local_mem_size,
        preferred_vector_width_float=preferred_vector_width_float,
        extensions=extensions,
        opencl_c_version=opencl_c_version,
        has_fp16=has_fp16,
        has_subgroups=has_subgroups,
        is_cpu=is_cpu,
        tiny_local_mem=tiny_local_mem,
        fast_atomics=fast_atomics,
        supports_fp16=has_fp16,
    )
    _PROFILE_CACHE[key] = profile
    return profile


def kernel_strategy(profile: DeviceProfile) -> str:
    """
    Decide between 'portable' and 'optimized'.
    Env override: NETCL_KERNEL_STRATEGY=portable/optimized/auto.
    """
    if NETCL_KERNEL_STRATEGY in ("portable", "optimized"):
        return NETCL_KERNEL_STRATEGY
    # auto
    if profile.is_cpu or profile.tiny_local_mem:
        return "portable"
    if profile.has_subgroups or profile.has_fp16 or profile.vendor.lower() in ("nvidia", "advanced micro devices", "amd"):
        return "optimized"
    return "portable"
