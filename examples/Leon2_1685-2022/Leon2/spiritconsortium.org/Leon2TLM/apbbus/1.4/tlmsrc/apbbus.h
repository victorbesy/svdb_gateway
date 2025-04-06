// 
// Revision:    $Revision: 1506 $
// Date:        $Date: 2009-04-25 23:51:56 -0700 (Sat, 25 Apr 2009) $
// 
// Copyright (c) 2005, 2006, 2007, 2008, 2009 The SPIRIT Consortium.
// 
// This work forms part of a deliverable of The SPIRIT Consortium.
// 
// Use of these materials are governed by the legal terms and conditions
// outlined in the disclaimer available from www.spiritconsortium.org.
// 
// This source file is provided on an AS IS basis.  The SPIRIT
// Consortium disclaims any warranty express or implied including
// any warranty of merchantability and fitness for use for a
// particular purpose.
// 
// The user of the source file shall indemnify and hold The SPIRIT
// Consortium and its members harmless from any damages or liability.
// Users are requested to provide feedback to The SPIRIT Consortium
// using either mailto:feedback@lists.spiritconsortium.org or the forms at 
// http://www.spiritconsortium.org/about/contact_us/
// 
// This file may be copied, and distributed, with or without
// modifications; but this notice must be included on any copy.

 /*------------------------------------------------------------------------------
 * Simple Leon2 TLM APB bus
 *------------------------------------------------------------------------------*/

#ifndef __APBBUS_H__
#define __APBBUS_H__

#include <systemc.h>
#include "pv_router.h"
#include "user_types.h"

typedef pv_router< ADDRESS_TYPE , DATA_TYPE > basic_router;


// this class has 1 target port (target_port) and 8 initiator ports (r_port[x])
// the number of initiator ports is computed at elaboration time (based on 
// this bus interconnection).
class apbbus : public basic_router
{
 public:
  apbbus (sc_module_name module_name,  const char* mapFile)
    : basic_router (module_name, mapFile)
  {}
  void end_of_elaboration() {
    basic_router::end_of_elaboration();
    cout << name() << " constructed." << endl;
  }
};

#endif
