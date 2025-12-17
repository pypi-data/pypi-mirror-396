#include <gtest/gtest.h>
#include <gmock/gmock.h>
#include <tdscontrol/tds.hpp>
#include <tdscontrol/roots.hpp>

GTEST_TEST(roots, scalar) {
    tds::tds sys ({1, -1}, {0, 1});
    auto roots = tds::roots(sys, 10);
    EXPECT_EQ(roots.size(), 11);
}

