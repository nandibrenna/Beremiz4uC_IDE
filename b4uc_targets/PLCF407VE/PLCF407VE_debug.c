#include "iec_types_all.h"
#include "POUS.h"
#include <string.h>
#include <stdio.h>
#include <stdbool.h>

// Global variables declaration from resources and configuration
#pragma GCC diagnostic ignored "-Wdiscarded-qualifiers"

// Programs declaration
%(programs_declarations)s

// External variables declaration from resources and configuration
%(extern_variables_declarations)s

// Debug variables descriptor index type
typedef unsigned int dbgvardsc_index_t;

// Debug variables descriptor structure
typedef struct {
    void *ptr; // Pointer to variable
    __IEC_types_enum type; // Variable type
} dbgvardsc_t;

// Debug variables descriptor array
const dbgvardsc_t dbgvardsc[] = {
	%(variable_decl_array)s
};

// Retain variables descriptor index array
const dbgvardsc_index_t retain_list[] = {
	%(retain_vardsc_index_array)s
};

#define __Unpack_desc_type dbgvardsc_t

// Functions imported from RTE
void rte_log_inf(const char* fmt, ...);
void printk(const char *fmt, ...);

// Functions exported to RTE
void trace_reset(void);
void set_trace(size_t idx, bool forced, void *val);
void force_var(size_t idx, bool forced, void *val);
int GetDebugVariable(dbgvardsc_index_t idx, void** value_p, size_t *size);
int SetDebugVariable(dbgvardsc_index_t idx, void** value_p, size_t *size);

// Placeholder for variable access code
%(var_access_code)s

// Define the number of variables
#define NUM(a) (sizeof(a) / sizeof(*a))
size_t var_count = NUM(dbgvardsc);

// Disable optimizations for debugging code
#pragma GCC push_options
#pragma GCC optimize("O0")

/*
Temporary workaround for a data relocation issue, affecting access to debug_vars[].ptr.
This function provides provisional access to debug variables. Further investigation required.
*/
void *get_debug_var_ptr(size_t idx)
{
    void *ptr[var_count];

    %(dbg_ptr_cnt)s
    if (idx < var_count) 
    {
        return ptr[idx];
    }
    else
    {
        return NULL;
    }
}

// Forces a variable to a given value based on index
void force_var(size_t idx, bool force, void *val)
{
    dbgvardsc_t *dsc = &dbgvardsc[idx];
    dsc->ptr = get_debug_var_ptr(idx);
    void *varp = dsc->ptr;
    __IEC_types_enum vartype = dsc->type;

    // Placeholder for force variable implementation
    __ANY(__ForceVariable_case_t)
    __ANY(__ForceVariable_case_p)
    {;}
}

// Gets a debug variable value
int GetDebugVariable(dbgvardsc_index_t idx, void** value_p, size_t *size) 
{
    int error_code = 0;
    if (idx >= 0 && idx < var_count) 
    {
        dbgvardsc_t *dsc = &dbgvardsc[idx];
        void *varp = get_debug_var_ptr(idx);
        dsc->ptr = varp;
        error_code = UnpackVar(dsc, value_p, NULL, size);
        if(__Is_a_string(dsc))
        {
            *size = (size_t) (int8_t) ((__IEC_STRING_t *)varp)->value.len + 1;
        }
        return error_code;
    }
    return -1;
}

// Re-enables optimizations
#pragma GCC pop_options

// Resets all debug variables
void trace_reset(void)
{
    for (size_t i = 0; i < var_count; i++) 
    {
        force_var(i, false, NULL);
    }
}

// Sets or forces a debug variable to a given value
void set_trace(size_t idx, bool forced, void *val)
{
    if (idx >= 0 && idx < var_count) 
    {
        force_var(idx, forced, val);
    }
}
