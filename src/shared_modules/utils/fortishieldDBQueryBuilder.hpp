/*
 * Fortishield DB Query Builder
 * Copyright (C) 2015, Fortishield Inc.
 * October 31, 2023.
 *
 * This program is free software; you can redistribute it
 * and/or modify it under the terms of the GNU General Public
 * License (version 2) as published by the FSF - Free Software
 * Foundation.
 */

#ifndef _FORTISHIELD_DB_QUERY_BUILDER_HPP
#define _FORTISHIELD_DB_QUERY_BUILDER_HPP

#include "builder.hpp"
#include "stringHelper.h"
#include <string>

constexpr auto FORTISHIELD_DB_ALLOWED_CHARS {"-_ "};

class FortishieldDBQueryBuilder final : public Utils::Builder<FortishieldDBQueryBuilder>
{
private:
    std::string m_query;

public:
    FortishieldDBQueryBuilder& global()
    {
        m_query += "global sql ";
        return *this;
    }

    FortishieldDBQueryBuilder& agent(const std::string& id)
    {
        if (!Utils::isNumber(id))
        {
            throw std::runtime_error("Invalid agent id");
        }

        m_query += "agent " + id + " sql ";
        return *this;
    }

    FortishieldDBQueryBuilder& selectAll()
    {
        m_query += "SELECT * ";
        return *this;
    }

    FortishieldDBQueryBuilder& fromTable(const std::string& table)
    {
        if (!Utils::isAlphaNumericWithSpecialCharacters(table, FORTISHIELD_DB_ALLOWED_CHARS))
        {
            throw std::runtime_error("Invalid table name");
        }
        m_query += "FROM " + table + " ";
        return *this;
    }

    FortishieldDBQueryBuilder& whereColumn(const std::string& column)
    {
        if (!Utils::isAlphaNumericWithSpecialCharacters(column, FORTISHIELD_DB_ALLOWED_CHARS))
        {
            throw std::runtime_error("Invalid column name");
        }
        m_query += "WHERE " + column + " ";
        return *this;
    }

    FortishieldDBQueryBuilder& isNull()
    {
        m_query += "IS NULL ";
        return *this;
    }

    FortishieldDBQueryBuilder& isNotNull()
    {
        m_query += "IS NOT NULL ";
        return *this;
    }

    FortishieldDBQueryBuilder& equalsTo(const std::string& value)
    {
        if (!Utils::isAlphaNumericWithSpecialCharacters(value, FORTISHIELD_DB_ALLOWED_CHARS))
        {
            throw std::runtime_error("Invalid value");
        }
        m_query += "= '" + value + "' ";
        return *this;
    }

    FortishieldDBQueryBuilder& andColumn(const std::string& column)
    {
        if (!Utils::isAlphaNumericWithSpecialCharacters(column, FORTISHIELD_DB_ALLOWED_CHARS))
        {
            throw std::runtime_error("Invalid column name");
        }
        m_query += "AND " + column + " ";
        return *this;
    }

    FortishieldDBQueryBuilder& orColumn(const std::string& column)
    {
        if (!Utils::isAlphaNumericWithSpecialCharacters(column, FORTISHIELD_DB_ALLOWED_CHARS))
        {
            throw std::runtime_error("Invalid column name");
        }
        m_query += "OR " + column + " ";
        return *this;
    }

    FortishieldDBQueryBuilder& globalGetCommand(const std::string& command)
    {
        if (!Utils::isAlphaNumericWithSpecialCharacters(command, FORTISHIELD_DB_ALLOWED_CHARS))
        {
            throw std::runtime_error("Invalid command");
        }
        m_query += "global get-" + command + " ";
        return *this;
    }

    FortishieldDBQueryBuilder& globalFindCommand(const std::string& command)
    {
        if (!Utils::isAlphaNumericWithSpecialCharacters(command, FORTISHIELD_DB_ALLOWED_CHARS))
        {
            throw std::runtime_error("Invalid command");
        }
        m_query += "global find-" + command + " ";
        return *this;
    }

    FortishieldDBQueryBuilder& globalSelectCommand(const std::string& command)
    {
        if (!Utils::isAlphaNumericWithSpecialCharacters(command, FORTISHIELD_DB_ALLOWED_CHARS))
        {
            throw std::runtime_error("Invalid command");
        }
        m_query += "global select-" + command + " ";
        return *this;
    }

    FortishieldDBQueryBuilder& agentGetOsInfoCommand(const std::string& id)
    {
        if (!Utils::isNumber(id))
        {
            throw std::runtime_error("Invalid agent id");
        }
        m_query += "agent " + id + " osinfo get ";
        return *this;
    }

    FortishieldDBQueryBuilder& agentGetHotfixesCommand(const std::string& id)
    {
        if (!Utils::isNumber(id))
        {
            throw std::runtime_error("Invalid agent id");
        }
        m_query += "agent " + id + " hotfix get ";
        return *this;
    }

    FortishieldDBQueryBuilder& agentGetPackagesCommand(const std::string& id)
    {
        if (!Utils::isNumber(id))
        {
            throw std::runtime_error("Invalid agent id");
        }
        m_query += "agent " + id + " package get ";
        return *this;
    }

    std::string build()
    {
        return m_query;
    }
};

#endif /* _FORTISHIELD_DB_QUERY_BUILDER_HPP */
