// SPDX-License-Identifier: GPL-3.0-only
#ifndef BCD_VT_INTERP_QUEUE_GATE_H
#define BCD_VT_INTERP_QUEUE_GATE_H
#include <dispatch/dispatch.h>
#include <stdio.h>
#include <stdlib.h>

// Insert ahead of the production jobs, not inside a copy or model call:
// madeira_vti_job samples backlog before either of those calls.
static dispatch_semaphore_t vti_test_hold_worker(dispatch_queue_t queue) {
  dispatch_semaphore_t gate = dispatch_semaphore_create(0);
  if (!gate) abort();
  dispatch_async(queue, ^{
    if (dispatch_semaphore_wait(gate, dispatch_time(DISPATCH_TIME_NOW, 10 * NSEC_PER_SEC))) {
      fputs("FAIL: timed out waiting for the test to release the worker queue\n", stderr);
      abort();
    }
  });
  return gate;
}
#endif
