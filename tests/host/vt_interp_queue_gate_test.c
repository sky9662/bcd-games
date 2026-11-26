// SPDX-License-Identifier: GPL-3.0-only
#include "vt_interp_queue_gate.h"
#include <stdatomic.h>
#include <unistd.h>
// The test driver inserts the actual madeira_vti_count from the production patch.
#include "vti_count.h"

static _Atomic int outstanding, busy, completed;
static void enqueue(dispatch_queue_t q) {
  atomic_fetch_add(&outstanding, 1);
  dispatch_async(q, ^{
    int backlog = atomic_load(&outstanding) - 1;
    if (!madeira_vti_count(1, .033, 120, backlog) && backlog > 0) atomic_fetch_add(&busy, 1);
    atomic_fetch_add(&completed, 1);
    atomic_fetch_sub(&outstanding, 1);
  });
}
int main(void) {
  dispatch_queue_t q = dispatch_queue_create("test", DISPATCH_QUEUE_SERIAL);
  for (int delay = 0; delay <= 130000; delay += 130000) {
    for (int i = 0; i < 12; i++) {
      atomic_store(&busy, 0); atomic_store(&completed, 0);
      dispatch_semaphore_t gate = vti_test_hold_worker(q);
      enqueue(q); usleep(delay); enqueue(q);
      if (atomic_load(&outstanding) != 2) return 1;
      dispatch_semaphore_signal(gate);
      dispatch_sync(q, ^{});
      if (atomic_load(&busy) != 1 || atomic_load(&completed) != 2 || atomic_load(&outstanding)) return 2;
      dispatch_release(gate);
    }
  }
  atomic_store(&busy, 0); atomic_store(&completed, 0);
  enqueue(q); dispatch_sync(q, ^{}); enqueue(q); dispatch_sync(q, ^{});
  if (atomic_load(&busy) != 0 || atomic_load(&completed) != 2) return 3;
  dispatch_release(q);
  puts("PASS: 24 gated two-frame queue trials (0/130 ms); ungated negative control has zero busy skips");
  return 0;
}
