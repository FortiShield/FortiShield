/*
 * Fortishield shared modules utils
 * Copyright (C) 2015, Fortishield Inc.
 * Nov 1, 2023.
 *
 * This program is free software; you can redistribute it
 * and/or modify it under the terms of the GNU General Public
 * License (version 2) as published by the FSF - Free Software
 * Foundation.
 */

#ifndef _FORTISHIELD_DB_QUERY_BUILDER_TEST_HPP
#define _FORTISHIELD_DB_QUERY_BUILDER_TEST_HPP

#include "gtest/gtest.h"

class FortishieldDBQueryBuilderTest : public ::testing::Test
{
protected:
    FortishieldDBQueryBuilderTest() = default;
    virtual ~FortishieldDBQueryBuilderTest() = default;

    void SetUp() override {};
    void TearDown() override {};
};

#endif // _FORTISHIELD_DB_QUERY_BUILDER_TEST_HPP
