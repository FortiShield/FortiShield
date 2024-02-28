/*
 * Fortishield Syscheck
 * Copyright (C) 2015, Fortishield Inc.
 * December 31, 2021.
 *
 * This program is free software; you can redistribute it
 * and/or modify it under the terms of the GNU General Public
 * License (version 2) as published by the FSF - Free Software
 * Foundation.
 */

#include "dbTest.h"
#include "db.h"
#include "db.hpp"


const auto insertRegistryKeyStatement1 = R"({
        "checksum":"a2fbef8f81af27155dcee5e3927ff6243593b91a", "gid":"0", "group_name":"root", "arch":1,
        "last_event":1596489275, "mode":0, "mtime":1578075431, "path":"HKEY_LOCAL_MACHINE\\SOFTWARE\\regtest1", "perm":"-rw-rw-r--",
        "scanned":1, "uid":"0", "user_name":"fakeUser", "hash_full_path":"00a7ee53218b25b5364c8773f37a38c93eae3880"
    }
)"_json;

const auto insertRegistryValueStatement1 = R"({
        "name":"testRegistry1", "scanned":1, "last_event":1596489275, "checksum":"a2fbef8f81af27155dcee5e3927ff6243593b91a",
        "mode":0, "size":4925, "type":0, "hash_md5":"4b531524aa13c8a54614100b570b3dc7",
        "hash_sha1":"7902feb66d0bcbe4eb88e1bfacf28befc38bd58b",
        "hash_sha256":"e403b83dd73a41b286f8db2ee36d6b0ea6e80b49f02c476e0a20b4181a3a062a",
        "arch":0, "path":"HKEY_LOCAL_MACHINE\\SOFTWARE\\regtest1", "hash_full_path":"00a7ee53218b25b5364c8773f37a38c93eae3880"
    }
)"_json;

const auto insertRegistryKeyStatement2 = R"({
        "checksum":"a2fbef8f81af27155dcee5e3927ff6243593b91a", "gid":"0", "group_name":"root", "arch":1,
        "last_event":1596489275, "mode":0, "mtime":1578075431, "path":"HKEY_LOCAL_MACHINE\\SOFTWARE\\regtest2", "perm":"-rw-rw-r--",
        "scanned":1, "uid":"0", "user_name":"fakeUser", "hash_full_path":"00a7ee53218b25b5364c8773f37a38c93eae3880"
    }
)"_json;

const auto insertRegistryValueStatement2 = R"({
        "name":"testRegistry2", "scanned":1, "last_event":1596489275, "checksum":"a2fbef8f81af27155dcee5e3927ff6243593b91a",
        "mode":0, "size":4925, "type":0, "hash_md5":"4b531524aa13c8a54614100b570b3dc7",
        "hash_sha1":"7902feb66d0bcbe4eb88e1bfacf28befc38bd58b",
        "hash_sha256":"e403b83dd73a41b286f8db2ee36d6b0ea6e80b49f02c476e0a20b4181a3a062a",
        "arch":0, "path":"HKEY_LOCAL_MACHINE\\SOFTWARE\\regtest2", "hash_full_path":"00a7ee53218b25b5364c8773f37a38c93eae3880"
    }
)"_json;

void transaction_callback( __attribute__((unused)) ReturnTypeCallback resultType,
                           __attribute__((unused)) const cJSON* result_json,
                           __attribute__((unused)) void* user_data){}

TEST_F(DBTestFixture, TestFimDBGetCountRegistryEntry)
{
    EXPECT_NO_THROW(
    {
        auto result = fim_db_get_count_registry_key();
        ASSERT_EQ(result, 0);

        // FIRST "SCAN"
        // Transaction start
        auto handler = fim_db_transaction_start(FIMDB_REGISTRY_KEY_TXN_TABLE, transaction_callback, &txn_ctx);
        ASSERT_TRUE(handler);

        // First update
        const auto registryKeyFIMTest1 { std::make_unique<RegistryKey>(insertRegistryKeyStatement1) };
        result = fim_db_transaction_sync_row(handler, registryKeyFIMTest1->toFimEntry());
        ASSERT_EQ(result, FIMDB_OK);

        result = fim_db_get_count_registry_key();
        ASSERT_EQ(result, 1);

        // Second update
        const auto registryKeyFIMTest2 { std::make_unique<RegistryKey>(insertRegistryKeyStatement2) };
        result = fim_db_transaction_sync_row(handler, registryKeyFIMTest2->toFimEntry());
        ASSERT_EQ(result, FIMDB_OK);

        result = fim_db_get_count_registry_key();
        ASSERT_EQ(result, 2);

        // End of transaction
        result = fim_db_transaction_deleted_rows(handler, transaction_callback, &txn_ctx);
        ASSERT_EQ(result, FIMDB_OK);

        result = fim_db_get_count_registry_key();
        ASSERT_EQ(result, 2);

        // SECOND "SCAN"
        // Transaction start
        handler = fim_db_transaction_start(FIMDB_REGISTRY_KEY_TXN_TABLE, transaction_callback, &txn_ctx);
        ASSERT_TRUE(handler);

        result = fim_db_get_count_registry_key();
        ASSERT_EQ(result, 2);

        // End of transaction
        result = fim_db_transaction_deleted_rows(handler, transaction_callback, &txn_ctx);
        ASSERT_EQ(result, FIMDB_OK);

        result = fim_db_get_count_registry_key();
        ASSERT_EQ(result, 0);
    });
}

TEST_F(DBTestFixture, TestFimDBGetCountRegistryValueEntry)
{
    EXPECT_NO_THROW(
    {
        auto result = fim_db_get_count_registry_data();
        ASSERT_EQ(result, 0);

        // FIRST "SCAN"
        // Transaction start
        auto handler = fim_db_transaction_start(FIMDB_REGISTRY_VALUE_TXN_TABLE, transaction_callback, &txn_ctx);
        ASSERT_TRUE(handler);

        // First update
        const auto registryValueFIMTest1 { std::make_unique<RegistryValue>(insertRegistryValueStatement1) };
        result = fim_db_transaction_sync_row(handler, registryValueFIMTest1->toFimEntry());
        ASSERT_EQ(result, FIMDB_OK);

        result = fim_db_get_count_registry_data();
        ASSERT_EQ(result, 1);

        // Second update
        const auto registryValueFIMTest2 { std::make_unique<RegistryValue>(insertRegistryValueStatement2) };
        result = fim_db_transaction_sync_row(handler, registryValueFIMTest2->toFimEntry());
        ASSERT_EQ(result, FIMDB_OK);

        result = fim_db_get_count_registry_data();
        ASSERT_EQ(result, 2);

        // End of transaction
        result = fim_db_transaction_deleted_rows(handler, transaction_callback, &txn_ctx);
        ASSERT_EQ(result, FIMDB_OK);

        result = fim_db_get_count_registry_data();
        ASSERT_EQ(result, 2);

        // SECOND "SCAN"
        // Transaction start
        handler = fim_db_transaction_start(FIMDB_REGISTRY_VALUE_TXN_TABLE, transaction_callback, &txn_ctx);
        ASSERT_TRUE(handler);

        result = fim_db_get_count_registry_data();
        ASSERT_EQ(result, 2);

        // End of transaction
        result = fim_db_transaction_deleted_rows(handler, transaction_callback, &txn_ctx);
        ASSERT_EQ(result, FIMDB_OK);

        result = fim_db_get_count_registry_data();
        ASSERT_EQ(result, 0);
    });
}
