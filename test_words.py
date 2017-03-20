from unittest.mock import patch, MagicMock, Mock

import pytest
import telepot
from telepot.namedtuple import InlineKeyboardMarkup

from words import check_how_many_to_learn, check_how_many_to_repeat


def count_words_to_learn(user):
    return 5;


class TestClass:
    @patch('words.compose_kbd_start_learning')
    @patch('words.count_words_to_learn')
    def test_check_how_many_to_learn(self, count_words_to_learn_mock, compose_kbd_start_learning_mock):
        # TOKEN = '371465282:AAGrzLhIuR1CFZEBVfC-0Gj2bL7Uq60Fv5g'
        bot_mock = telepot.Bot('12345')
        bot_mock.sendMessage = MagicMock(name='sendMessage')
        count_words_to_learn_mock.return_value = 5
        kbd = InlineKeyboardMarkup()
        compose_kbd_start_learning_mock.return_value = kbd
        check_how_many_to_learn(bot_mock, 123, 'user')
        bot_mock.sendMessage.assert_called_once_with(123, 'There are 5 words to learn', reply_markup=kbd)

    @patch('words.compose_kbd_start_learning')
    @patch('words.count_words_to_learn')
    def test_check_how_many_to_learn_zero(self, count_words_to_learn_mock, compose_kbd_start_learning_mock):
        # TOKEN = '371465282:AAGrzLhIuR1CFZEBVfC-0Gj2bL7Uq60Fv5g'
        bot_mock = telepot.Bot('12345')
        bot_mock.sendMessage = MagicMock(name='sendMessage')
        count_words_to_learn_mock.return_value = 0
        kbd = InlineKeyboardMarkup()
        compose_kbd_start_learning_mock.return_value = kbd
        check_how_many_to_learn(bot_mock, 123, 'user')
        bot_mock.sendMessage.assert_called_once_with(123, 'There are no words to learn. Add them using /word command')

    @patch('words.compose_kbd_start_learning')
    @patch('words.count_words_to_learn')
    def test_check_how_many_to_learn_except(self, count_words_to_learn_mock, compose_kbd_start_learning_mock):
        # TOKEN = '371465282:AAGrzLhIuR1CFZEBVfC-0Gj2bL7Uq60Fv5g'
        bot_mock = telepot.Bot('12345')
        bot_mock.sendMessage = MagicMock(name='sendMessage')
        count_words_to_learn_mock.side_effect = Mock(side_effect=KeyError("Test"))
        kbd = InlineKeyboardMarkup()
        compose_kbd_start_learning_mock.return_value = kbd
        with pytest.raises(KeyError):
            check_how_many_to_learn(bot_mock, 123, 'user')

        bot_mock.sendMessage.assert_called_once_with(123, "Cannot count words to repeat 'Test'")

    @patch('words.compose_kbd_start_repeat')
    @patch('words.count_words_to_repeat')
    def test_check_how_many_to_repeat(self, count_words_to_repeat_mock, compose_kbd_start_repeat_mock):
        # TOKEN = '371465282:AAGrzLhIuR1CFZEBVfC-0Gj2bL7Uq60Fv5g'
        bot_mock = telepot.Bot('12345')
        bot_mock.sendMessage = MagicMock(name='sendMessage')
        count_words_to_repeat_mock.return_value = 5
        kbd = InlineKeyboardMarkup()
        compose_kbd_start_repeat_mock.return_value = kbd
        check_how_many_to_repeat(bot_mock, 123, None, 'user')
        bot_mock.sendMessage.assert_called_once_with(123, 'There are 5 words to repeat', reply_markup=kbd)

    @patch('words.compose_kbd_start_repeat')
    @patch('words.count_words_to_repeat')
    def test_check_how_many_to_repeat_zero(self, count_words_to_learn_mock, compose_kbd_start_learning_mock):
        # TOKEN = '371465282:AAGrzLhIuR1CFZEBVfC-0Gj2bL7Uq60Fv5g'
        bot_mock = telepot.Bot('12345')
        bot_mock.sendMessage = MagicMock(name='sendMessage')
        count_words_to_learn_mock.return_value = 0
        kbd = InlineKeyboardMarkup()
        compose_kbd_start_learning_mock.return_value = kbd
        check_how_many_to_repeat(bot_mock, 123, None, 'user')
        bot_mock.sendMessage.assert_called_once_with(123, 'There are no words to repeat. Take a cup of tea')

    @patch('words.compose_kbd_start_repeat')
    @patch('words.count_words_to_repeat')
    def test_check_how_many_to_repeat_except(self, count_words_to_learn_mock, compose_kbd_start_learning_mock):
        # TOKEN = '371465282:AAGrzLhIuR1CFZEBVfC-0Gj2bL7Uq60Fv5g'
        bot_mock = telepot.Bot('12345')
        bot_mock.sendMessage = MagicMock(name='sendMessage')
        count_words_to_learn_mock.side_effect = Mock(side_effect=KeyError("Test"))
        kbd = InlineKeyboardMarkup()
        compose_kbd_start_learning_mock.return_value = kbd
        with pytest.raises(KeyError):
            check_how_many_to_repeat(bot_mock, 123, None, 'user')

        bot_mock.sendMessage.assert_called_once_with(123, "Cannot count words to repeat 'Test'")
