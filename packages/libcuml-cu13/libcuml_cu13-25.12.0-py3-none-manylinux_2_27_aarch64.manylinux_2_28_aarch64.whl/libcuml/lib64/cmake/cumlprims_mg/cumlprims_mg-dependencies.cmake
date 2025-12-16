#=============================================================================
# SPDX-FileCopyrightText: Copyright (c) 2025, NVIDIA CORPORATION.
# SPDX-License-Identifier: Apache-2.0
#=============================================================================

include(CMakeFindDependencyMacro)

find_dependency(CUDAToolkit)

find_package(raft 25.12.00 QUIET)
find_dependency(raft)


set(rapids_global_targets raft::raft)


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
