/******************************************************************************************************************
* Modified the switch/case statements to if/else constructs to avoid reliance on compiler-specific 
* functions like __gnu_thumb1_case_uhi. This change was necessary because acquiring and exporting 
* the address of such functions to a dynamically linked PLC module using udynlink proved to be problematic.
******************************************************************************************************************/

#define __ReForceOutput_case_p(TYPENAME)                                         \
	if (dsc->type == TYPENAME##_ENUM) {                                          \
		((__IEC_##TYPENAME##_t *) value_p)->value   = *((TYPENAME *) val);       \
		((__IEC_##TYPENAME##_t *) value_p)->flags  |= __IEC_FORCE_FLAG;          \
	} else                                                                       \
	if (dsc->type == TYPENAME##_P_ENUM) {                                        \
		  ((__IEC_##TYPENAME##_p *)value_p)->value  = (TYPENAME *) val;          \
		  ((__IEC_##TYPENAME##_p *)value_p)->flags |= __IEC_FORCE_FLAG;          \
	} else                                                                       \
	if (dsc->type == TYPENAME##_O_ENUM) {                                        \
		*(((__IEC_##TYPENAME##_p *) value_p)->value) = *((TYPENAME *) val);      \
		  ((__IEC_##TYPENAME##_p *) value_p)->flags |= __IEC_FORCE_FLAG;         \
	} else

// force var (type)
#define __ForceVariable_case_t(TYPENAME)                                         \
	if (vartype == TYPENAME##_ENUM) {                                            \
		if(force) {                                                              \
			((__IEC_##TYPENAME##_t *)varp)->flags |= __IEC_FORCE_FLAG;           \
			((__IEC_##TYPENAME##_t *)varp)->value = *((TYPENAME *)val);          \
		}                                                                        \
		else                                                                     \
			((__IEC_##TYPENAME##_t *)varp)->flags &= ~__IEC_FORCE_FLAG;          \
	} else

// force var (pointer)
#define __ForceVariable_case_p(TYPENAME)                                         \
	if (vartype == TYPENAME##_P_ENUM || vartype == TYPENAME##_O_ENUM) {          \
		if(force) {                                                              \
			((__IEC_##TYPENAME##_p *)varp)->flags |= __IEC_FORCE_FLAG;           \
			if (vartype == TYPENAME##_P_ENUM)                                    \
				((__IEC_##TYPENAME##_p *)varp)->value = (TYPENAME *)val;         \
			if (vartype == TYPENAME##_O_ENUM)                                    \
				*(((__IEC_##TYPENAME##_p *)varp)->value) = *((TYPENAME *)val);   \
		}                                                                        \
		else                                                                     \
			((__IEC_##TYPENAME##_p *)varp)->flags &= ~__IEC_FORCE_FLAG;          \
		                                                                         \
	} else

// get var
#define __Unpack_case_t(TYPENAME)                                                \
	if (vartype == TYPENAME##_ENUM) {                                            \
		if(flags) *flags = ((__IEC_##TYPENAME##_t *)varp)->flags;                \
		if(value_p) *value_p = &((__IEC_##TYPENAME##_t *)varp)->value;           \
		if(size) *size = sizeof(TYPENAME);                                       \
	} else

#define __Unpack_case_p(TYPENAME)                                                \
	if (vartype == TYPENAME##_O_ENUM || vartype == TYPENAME##_P_ENUM) {          \
		if(flags) *flags = ((__IEC_##TYPENAME##_p *)varp)->flags;                \
		if(value_p) *value_p = ((__IEC_##TYPENAME##_p *)varp)->value;            \
		if(size) *size = sizeof(TYPENAME);                                       \
	} else

// string
#define __Is_a_string(dsc) (dsc->type == STRING_ENUM)   ||                       \
						   (dsc->type == STRING_P_ENUM) ||                       \
						   (dsc->type == STRING_O_ENUM)

#pragma GCC push_options
#pragma GCC optimize("O0")
static int UnpackVar(__Unpack_desc_type *dsc, void **value_p, char *flags, size_t *size)
{
	void *varp = dsc->ptr;
	__IEC_types_enum vartype = dsc->type;
	__ANY(__Unpack_case_t)
	__ANY(__Unpack_case_p)
	{
		return 1; // type not found
	}
	return 0;
}
#pragma GCC pop_options