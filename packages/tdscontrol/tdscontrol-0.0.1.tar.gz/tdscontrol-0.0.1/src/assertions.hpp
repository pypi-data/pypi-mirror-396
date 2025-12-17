#pragma once

#include <cassert>

#ifdef DISABLE_ASSERT_TDS_CONDTROL
#define TDS_CONTROL_PRECONDITION(cond, message)
#else
#define TDS_CONTROL_PRECONDITION(cond, message) \
    assert(cond)
#endif
