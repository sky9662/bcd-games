// SPDX-License-Identifier: GPL-3.0-only
// Copyright 2026 thebcd69 (BCD)
// BCD Material: additional terms under GPL-3.0 section 7 apply; see LICENSE-BCD.md.
#ifndef BCD_VT_INTERP_TEST_CLOCK_H
#define BCD_VT_INTERP_TEST_CLOCK_H
#include <stdint.h>
#include <stdatomic.h>

// Only the simulated game advances this clock. Worker scheduling and GPU/model
// waits remain real, and cannot change the FPS that a test is asking to model.
static _Atomic uint64_t g_vti_test_ns = 1000000000ull;
static uint64_t vti_test_absolute_time(void) { return atomic_load(&g_vti_test_ns); }
static double vti_test_seconds(void) { return (double)vti_test_absolute_time() / 1e9; }
static void vti_test_advance_us(uint64_t us) { atomic_fetch_add(&g_vti_test_ns, us * 1000ull); }
#endif
