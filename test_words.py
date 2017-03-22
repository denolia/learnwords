from unittest.mock import patch, MagicMock, Mock

import pytest
import telepot
from telepot.namedtuple import InlineKeyboardMarkup

from enums import Mode
from words import check_how_many_to_mode


class TestClass:
    @pytest.mark.parametrize("mode", [Mode.learn, Mode.repeat])
    @patch('words.compose_kbd_start_mode')
    @patch('words.count_words_to_mode')
    def test_check_how_many_to_mode(self, count_words_to_mode_mock, compose_kbd_start_mode_mock, mode):
        bot_mock = telepot.Bot('12345')
        bot_mock.sendMessage = MagicMock(name='sendMessage')
        count_words_to_mode_mock.return_value = 5
        kbd = InlineKeyboardMarkup()
        compose_kbd_start_mode_mock.return_value = kbd
        check_how_many_to_mode(bot_mock, 123, 'user', mode)
        bot_mock.sendMessage.assert_called_once_with(123,
                                                     'There are 5 words to {mode}'.format(mode=mode.name),
                                                     reply_markup=kbd)

    @pytest.mark.parametrize("mode", [Mode.learn, Mode.repeat])
    @patch('words.compose_kbd_start_mode')
    @patch('words.count_words_to_mode')
    def test_check_how_many_to_mode_zero(self, count_words_to_mode_mock, compose_kbd_start_mode_mock, mode):
        bot_mock = telepot.Bot('12345')
        bot_mock.sendMessage = MagicMock(name='sendMessage')
        count_words_to_mode_mock.return_value = 0
        kbd = InlineKeyboardMarkup()
        compose_kbd_start_mode_mock.return_value = kbd
        check_how_many_to_mode(bot_mock, 123, 'user', mode)
        bot_mock.sendMessage.assert_called_once_with(123, 'There are no words to {mode}'.format(mode=mode.name))

    @pytest.mark.parametrize("mode", [Mode.learn, Mode.repeat])
    @patch('words.compose_kbd_start_mode')
    @patch('words.count_words_to_mode')
    def test_check_how_many_to_mode_except(self, count_words_to_mode_mock, compose_kbd_start_mode_mock, mode):
        bot_mock = telepot.Bot('12345')
        bot_mock.sendMessage = MagicMock(name='sendMessage')
        count_words_to_mode_mock.side_effect = Mock(side_effect=KeyError("Test"))
        kbd = InlineKeyboardMarkup()
        compose_kbd_start_mode_mock.return_value = kbd
        with pytest.raises(KeyError):
            check_how_many_to_mode(bot_mock, 123, 'user', mode)

        bot_mock.sendMessage.assert_called_once_with(123, "Cannot count words to {mode} 'Test'".format(mode=mode.name))
