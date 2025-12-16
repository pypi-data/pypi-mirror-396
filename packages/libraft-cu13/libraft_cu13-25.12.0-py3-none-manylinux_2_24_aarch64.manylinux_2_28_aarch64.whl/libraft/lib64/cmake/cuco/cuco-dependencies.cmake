#=============================================================================
# SPDX-FileCopyrightText: Copyright (c) 2025, NVIDIA CORPORATION.
# SPDX-License-Identifier: Apache-2.0
#=============================================================================

include(CMakeFindDependencyMacro)

set(CCCL_ROOT "${CMAKE_CURRENT_LIST_DIR}/../../rapids/cmake/cccl")
find_dependency(CUDAToolkit)

find_package(CCCL 3.1.3 QUIET)
find_dependency(CCCL)

if(CCCL_FOUND)
    target_compile_definitions(CCCL::CCCL INTERFACE CUB_DISABLE_NAMESPACE_MAGIC)
    target_compile_definitions(CCCL::CCCL INTERFACE CUB_IGNORE_NAMESPACE_MAGIC_ERROR)
    target_compile_definitions(CCCL::CCCL INTERFACE THRUST_DISABLE_ABI_NAMESPACE)
    target_compile_definitions(CCCL::CCCL INTERFACE THRUST_IGNORE_ABI_NAMESPACE_ERROR)
    target_compile_definitions(CCCL::CCCL INTERFACE CCCL_DISABLE_PDL)
    

endif()

set(rapids_global_targets CCCL;CCCL::CCCL;CCCL::CUB;CCCL::libcudacxx;CCCL::cudax)


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
