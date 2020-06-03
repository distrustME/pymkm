"""
Python unittest
"""
import io
import json
import unittest
from unittest.mock import MagicMock, Mock, mock_open, patch

import requests
from requests_oauthlib import OAuth1Session

from pymkm.pymkmapi import PyMkmApi, NoResultsError
from pymkm.pymkm_app import PyMkmApp
from test.test_common import TestCommon


class TestPyMkmApiCalls(TestCommon):

    api = None

    def setUp(self):
        super(TestPyMkmApiCalls, self).setUp()

        self.api = PyMkmApi(self.config)

    def test_no_results(self):
        mock_oauth = Mock(spec=OAuth1Session)
        mock_oauth.get = MagicMock(
            return_value=self.MockResponse(None, 204, "testing ok")
        )
        with self.assertLogs(level="ERROR") as cm:
            empty_response = self.api.get_expansions(1, mock_oauth)
            log_record_message = cm.records[0].message
            self.assertEqual(log_record_message, "No results found.")

    def test_get_language_code_from_string(self):
        language_code = self.api.get_language_code_from_string("English")
        self.assertEqual(language_code, 1)
        with self.assertRaises(Exception):
            self.api.get_language_code_from_string("Elvish")

    def test_file_not_found2(self):
        open_name = "%s.open" % __name__
        with patch("builtins.open", mock_open(read_data="data")) as mocked_open:
            mocked_open.side_effect = FileNotFoundError

            # Assert that an error is logged
            with self.assertRaises(SystemExit):
                with self.assertLogs(level="ERROR") as cm:
                    PyMkmApi()
                    log_record_level = cm.records[0].levelname
                    self.assertEqual(log_record_level, "ERROR")

    def test_get_account(self):
        mock_oauth = Mock(spec=OAuth1Session)

        mock_oauth.get = MagicMock(
            return_value=self.MockResponse("test", 200, "testing ok")
        )
        self.assertEqual(self.api.get_account(mock_oauth), "test")
        mock_oauth.get.assert_called()

        mock_oauth.get = MagicMock(
            return_value=self.MockResponse("", 401, "Unauthorized")
        )
        with self.assertLogs(level="ERROR") as cm:
            self.api.get_account(mock_oauth)
            self.assertGreater(len(cm.records), 0)

    def test_get_stock(self):
        mock_oauth = Mock(spec=OAuth1Session)
        mock_oauth.get = MagicMock(
            return_value=self.MockResponse(
                TestCommon.cardmarket_get_stock_result, 200, "testing ok"
            )
        )
        stock = self.api.get_stock(None, mock_oauth)
        self.assertEqual(stock[0]["comments"], "x")

    def test_get_games(self):
        test_json = json.loads('{"test": "test"}')
        mock_oauth = Mock(spec=OAuth1Session)
        mock_oauth.get = MagicMock(
            return_value=self.MockResponse(test_json, 200, "testing ok")
        )
        self.assertEqual(self.api.get_games(mock_oauth), test_json)

    def test_get_expansions(self):
        test_json = json.loads('{"test": "test"}')
        mock_oauth = Mock(spec=OAuth1Session)
        mock_oauth.get = MagicMock(
            return_value=self.MockResponse(test_json, 200, "testing ok")
        )
        game_id = 1
        self.assertEqual(self.api.get_expansions(game_id, mock_oauth), test_json)

    def test_get_cards_in_expansion(self):
        test_json = json.loads('{"test": "test"}')
        mock_oauth = Mock(spec=OAuth1Session)
        mock_oauth.get = MagicMock(
            return_value=self.MockResponse(test_json, 200, "testing ok")
        )
        expansion_id = 1
        self.assertEqual(
            self.api.get_cards_in_expansion(expansion_id, mock_oauth), test_json
        )

    def test_get_product(self):
        test_json = json.loads('{"test": "test"}')
        mock_oauth = Mock(spec=OAuth1Session)
        mock_oauth.get = MagicMock(
            return_value=self.MockResponse(test_json, 200, "testing ok")
        )
        product_id = 1
        self.assertEqual(self.api.get_product(product_id, mock_oauth), test_json)

    def test_find_product(self):
        mock_oauth = Mock(spec=OAuth1Session)
        mock_oauth.get = MagicMock(
            return_value=self.MockResponse(
                TestCommon.fake_product_response, 200, "testing ok"
            )
        )
        search_string = "test"
        result = self.api.find_product(search_string, mock_oauth)
        self.assertEqual(result, TestCommon.fake_product_response)

    def test_find_stock_article(self):
        mock_oauth = Mock(spec=OAuth1Session)
        mock_oauth.get = MagicMock(
            return_value=self.MockResponse(
                TestCommon.cardmarket_find_user_articles_result, 200, "testing ok"
            )
        )
        name = "test"
        game_id = 1
        result = self.api.find_stock_article(name, game_id, mock_oauth)
        self.assertEqual(result[0]["comments"], "x")

    def test_get_articles_in_shoppingcarts(self):
        test_json = json.loads('{"test": "test"}')
        mock_oauth = Mock(spec=OAuth1Session)
        mock_oauth.get = MagicMock(
            return_value=self.MockResponse(test_json, 200, "testing ok")
        )

        self.assertEqual(self.api.get_articles_in_shoppingcarts(mock_oauth), test_json)

    def test_get_articles(self):
        mock_oauth = Mock(spec=OAuth1Session)
        mock_oauth.get = MagicMock(
            return_value=self.MockResponse(
                TestCommon.cardmarket_find_user_articles_result, 200, "testing ok"
            )
        )
        product_id = 1

        result = self.api.get_articles(product_id, 0, mock_oauth)
        self.assertEqual(result[0]["comments"], "x")

        mock_oauth.get = MagicMock(
            return_value=self.MockResponse(
                TestCommon.cardmarket_find_user_articles_result, 206, "partial content"
            )
        )
        product_id = 1

        result = self.api.get_articles(product_id, 0, mock_oauth)
        self.assertEqual(result[0]["comments"], "x")

    def test_find_user_articles(self):

        mock_oauth = Mock(spec=OAuth1Session)
        mock_oauth.get = MagicMock(
            return_value=self.MockResponse(
                TestCommon.cardmarket_find_user_articles_result, 200, "testing ok"
            )
        )
        user_id = 1
        game_id = 1

        result = self.api.find_user_articles(user_id, game_id, 0, mock_oauth)
        self.assertEqual(result[0]["comments"], "x")

        mock_oauth.get = MagicMock(
            return_value=self.MockResponse(
                TestCommon.cardmarket_find_user_articles_result, 206, "partial content"
            )
        )

        result = self.api.find_user_articles(user_id, game_id, 0, mock_oauth)
        self.assertEqual(result[0]["comments"], "x")

    def test_set_vacation_status(self):
        mock_oauth = Mock(spec=OAuth1Session)
        mock_oauth.put = MagicMock(
            return_value=self.MockResponse(
                TestCommon.fake_account_data, 200, "testing ok"
            )
        )
        vacation_status = True

        result = self.api.set_vacation_status(vacation_status, mock_oauth)
        self.assertEqual(result["message"], "Successfully set the account on vacation.")
        self.assertEqual(result["account"]["onVacation"], vacation_status)

    def test_set_display_language(self):
        mock_oauth = Mock(spec=OAuth1Session)
        mock_oauth.put = MagicMock(
            return_value=self.MockResponse(
                TestCommon.fake_account_data, 200, "testing ok"
            )
        )
        display_language = 1

        result = self.api.set_display_language(display_language, mock_oauth)
        self.assertEqual(
            result["account"]["idDisplayLanguage"], str(display_language).lower()
        )

    def test_add_stock(self):
        mock_oauth = Mock(spec=OAuth1Session)
        mock_oauth.post = MagicMock(
            return_value=self.MockResponse(
                TestCommon.get_stock_result, 200, "testing ok"
            )
        )

        result = self.api.add_stock(TestCommon.get_stock_result, mock_oauth)
        self.assertEqual(len(result), 3)

    def test_set_stock(self):
        mock_oauth = Mock(spec=OAuth1Session)
        mock_oauth.put = MagicMock(
            return_value=self.MockResponse(
                TestCommon.get_stock_result, 200, "testing ok"
            )
        )

        result = self.api.set_stock(TestCommon.get_stock_result, mock_oauth)
        self.assertEqual(len(result), 3)

    def test_delete_stock(self):
        mock_oauth = Mock(spec=OAuth1Session)
        mock_oauth.delete = MagicMock(
            return_value=self.MockResponse(
                TestCommon.get_stock_result, 200, "testing ok"
            )
        )

        result = self.api.delete_stock(TestCommon.get_stock_result, mock_oauth)
        self.assertEqual(len(result), 3)

    def test_get_wantslists(self):
        mock_oauth = Mock(spec=OAuth1Session)
        mock_oauth.get = MagicMock(
            return_value=self.MockResponse(
                TestCommon.cardmarket_get_wantslists, 200, "testing ok"
            )
        )
        result = self.api.get_wantslists(mock_oauth)
        self.assertEqual(result, TestCommon.get_wantslists)

    def test_get_wantslist_items(self):
        mock_oauth = Mock(spec=OAuth1Session)
        mock_oauth.get = MagicMock(
            return_value=self.MockResponse(
                TestCommon.cardmarket_get_wantslist_items, 200, "testing ok"
            )
        )
        wantslist_id = 2789285
        result = self.api.get_wantslist_items(wantslist_id, mock_oauth)
        self.assertEqual(result, TestCommon.get_wantslist_items)


if __name__ == "__main__":
    unittest.main()