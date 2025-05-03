/*
 ============================================================================
Title: svdb_typedef.h

 Copyright (c) 2016-2025 IC Verimeter. All rights reserved.

               Licensed under the MIT License.

               See LICENSE file in the project root for full license information.

Description : common includes typedef, #defines Svdb settings
  ============================================================================
 */
#ifndef SVDB_TYPEDEF_H
#define SVDB_TYPEDEF_H

//Title: Common defines

#ifdef __cplusplus
#define INLINE inline
#else
#define INLINE
#endif

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <errno.h>
#include <string.h>
#include <sys/types.h>
#include <time.h>
#include <stdarg.h>
#include <stdint.h>
#include <fcntl.h>
#include <signal.h>
#include <time.h>
#include <sys/time.h>

/* Use the custom SQLite path if defined, otherwise try standard path */
#ifdef SQLITE_CUSTOM_PATH
#include SQLITE_CUSTOM_PATH
#else
#include <sqlite3.h>
#endif

#ifdef SVDB_SVDPI
#include "svdpi.h"
#else
#ifndef INCLUDED_SVDPI
typedef uint8_t svScalar;
typedef svScalar svLogic; /* scalar */
typedef svScalar svBit; /* scalar */
typedef uint32_t svBitVecVal;
typedef void* svOpenArrayHandle;

typedef struct t_vpi_vecval {
  uint32_t aval;
  uint32_t bval;
} s_vpi_vecval, *p_vpi_vecval;
typedef s_vpi_vecval svLogicVecVal;
#endif
#endif



/*
Variable: svdb_long_t
typedef 64 bit variable , default value is "long long"
*/

#ifndef  svdb_long_t
typedef long long svdb_long_t;
#endif


/* -----\/----- EXCLUDED -----\/-----
#if __BYTE_ORDER__ == __ORDER_LITTLE_ENDIAN__
typedef struct cs_tlm_axi3_extension_payload_header_t {
  shunt_long_t  xSTRB;
  shunt_long_t  xRESP;
  shunt_long_t  AxSIZE;
  shunt_long_t  AxPROT;
  shunt_long_t  AxLOCK;
  shunt_long_t  AxLEN;
  shunt_long_t  AxID;
  shunt_long_t  AxCACHE;
  shunt_long_t  AxBURST;
} cs_tlm_axi3_extension_payload_header;
#endif
 -----/\----- EXCLUDED -----/\----- */
  
#endif //define SVDB_TYPEDEF_H
  

