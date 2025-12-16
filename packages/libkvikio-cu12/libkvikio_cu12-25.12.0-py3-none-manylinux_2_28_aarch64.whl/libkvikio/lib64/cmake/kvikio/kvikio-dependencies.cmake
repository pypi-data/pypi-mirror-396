#=============================================================================
# SPDX-FileCopyrightText: Copyright (c) 2025, NVIDIA CORPORATION.
# SPDX-License-Identifier: Apache-2.0
#=============================================================================

include(CMakeFindDependencyMacro)

find_dependency(Threads)

find_dependency(CUDAToolkit)

find_package(nvtx3 3.2.0 QUIET)
find_dependency(nvtx3)

find_package(bs_thread_pool 4.1.0 QUIET)
find_dependency(bs_thread_pool)


set(rapids_global_targets nvtx3-c;nvtx3-cpp;rapids_bs_thread_pool)


foreach(target IN LISTS rapids_global_targets)
  if(TARGET ${target})
    get_target_property(_is_imported ${target} IMPORTED)
    get_target_property(_already_global ${target} IMPORTED_GLOBAL)
    if(_is_imported AND NOT _already_global)
        set_target_properties(${target} PROPERTIES IMPORTED_GLOBAL TRUE)
    endif()
  endif()
endforeach()

unset(rapids_global_targets)
unset(rapids_clear_cpm_cache)
