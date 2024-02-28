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

#include "wazuhDBQueryBuilder_test.hpp"
#include "wazuhDBQueryBuilder.hpp"
#include <string>

TEST_F(FortishieldDBQueryBuilderTest, GlobalTest)
{
    std::string message = FortishieldDBQueryBuilder::builder().global().selectAll().fromTable("agent").build();
    EXPECT_EQ(message, "global sql SELECT * FROM agent ");
}

TEST_F(FortishieldDBQueryBuilderTest, AgentTest)
{
    std::string message = FortishieldDBQueryBuilder::builder().agent("0").selectAll().fromTable("sys_programs").build();
    EXPECT_EQ(message, "agent 0 sql SELECT * FROM sys_programs ");
}

TEST_F(FortishieldDBQueryBuilderTest, WhereTest)
{
    std::string message = FortishieldDBQueryBuilder::builder()
                              .agent("0")
                              .selectAll()
                              .fromTable("sys_programs")
                              .whereColumn("name")
                              .equalsTo("bash")
                              .build();
    EXPECT_EQ(message, "agent 0 sql SELECT * FROM sys_programs WHERE name = 'bash' ");
}

TEST_F(FortishieldDBQueryBuilderTest, WhereAndTest)
{
    std::string message = FortishieldDBQueryBuilder::builder()
                              .agent("0")
                              .selectAll()
                              .fromTable("sys_programs")
                              .whereColumn("name")
                              .equalsTo("bash")
                              .andColumn("version")
                              .equalsTo("1")
                              .build();
    EXPECT_EQ(message, "agent 0 sql SELECT * FROM sys_programs WHERE name = 'bash' AND version = '1' ");
}

TEST_F(FortishieldDBQueryBuilderTest, WhereOrTest)
{
    std::string message = FortishieldDBQueryBuilder::builder()
                              .agent("0")
                              .selectAll()
                              .fromTable("sys_programs")
                              .whereColumn("name")
                              .equalsTo("bash")
                              .orColumn("version")
                              .equalsTo("1")
                              .build();
    EXPECT_EQ(message, "agent 0 sql SELECT * FROM sys_programs WHERE name = 'bash' OR version = '1' ");
}

TEST_F(FortishieldDBQueryBuilderTest, WhereIsNullTest)
{
    std::string message = FortishieldDBQueryBuilder::builder()
                              .agent("0")
                              .selectAll()
                              .fromTable("sys_programs")
                              .whereColumn("name")
                              .isNull()
                              .build();
    EXPECT_EQ(message, "agent 0 sql SELECT * FROM sys_programs WHERE name IS NULL ");
}

TEST_F(FortishieldDBQueryBuilderTest, WhereIsNotNullTest)
{
    std::string message = FortishieldDBQueryBuilder::builder()
                              .agent("0")
                              .selectAll()
                              .fromTable("sys_programs")
                              .whereColumn("name")
                              .isNotNull()
                              .build();
    EXPECT_EQ(message, "agent 0 sql SELECT * FROM sys_programs WHERE name IS NOT NULL ");
}

TEST_F(FortishieldDBQueryBuilderTest, InvalidValue)
{
    EXPECT_THROW(FortishieldDBQueryBuilder::builder()
                     .agent("0")
                     .selectAll()
                     .fromTable("sys_programs")
                     .whereColumn("name")
                     .equalsTo("bash'")
                     .build(),
                 std::runtime_error);
}

TEST_F(FortishieldDBQueryBuilderTest, InvalidColumn)
{
    EXPECT_THROW(FortishieldDBQueryBuilder::builder()
                     .agent("0")
                     .selectAll()
                     .fromTable("sys_programs")
                     .whereColumn("name'")
                     .equalsTo("bash")
                     .build(),
                 std::runtime_error);
}

TEST_F(FortishieldDBQueryBuilderTest, InvalidTable)
{
    EXPECT_THROW(FortishieldDBQueryBuilder::builder()
                     .agent("0")
                     .selectAll()
                     .fromTable("sys_programs'")
                     .whereColumn("name")
                     .equalsTo("bash")
                     .build(),
                 std::runtime_error);
}

TEST_F(FortishieldDBQueryBuilderTest, GlobalGetCommand)
{
    std::string message = FortishieldDBQueryBuilder::builder().globalGetCommand("agent-info 1").build();
    EXPECT_EQ(message, "global get-agent-info 1 ");
}

TEST_F(FortishieldDBQueryBuilderTest, GlobalFindCommand)
{
    std::string message = FortishieldDBQueryBuilder::builder().globalFindCommand("agent 1").build();
    EXPECT_EQ(message, "global find-agent 1 ");
}

TEST_F(FortishieldDBQueryBuilderTest, GlobalSelectCommand)
{
    std::string message = FortishieldDBQueryBuilder::builder().globalSelectCommand("agent-name 1").build();
    EXPECT_EQ(message, "global select-agent-name 1 ");
}

TEST_F(FortishieldDBQueryBuilderTest, AgentGetOsInfoCommand)
{
    std::string message = FortishieldDBQueryBuilder::builder().agentGetOsInfoCommand("1").build();
    EXPECT_EQ(message, "agent 1 osinfo get ");
}

TEST_F(FortishieldDBQueryBuilderTest, AgentGetHotfixesCommand)
{
    std::string message = FortishieldDBQueryBuilder::builder().agentGetHotfixesCommand("1").build();
    EXPECT_EQ(message, "agent 1 hotfix get ");
}

TEST_F(FortishieldDBQueryBuilderTest, AgentGetPackagesCommand)
{
    std::string message = FortishieldDBQueryBuilder::builder().agentGetPackagesCommand("1").build();
    EXPECT_EQ(message, "agent 1 package get ");
}
