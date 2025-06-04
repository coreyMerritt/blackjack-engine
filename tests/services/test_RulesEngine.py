import unittest
from unittest.mock import patch
from services.CardCountingEngine import CardCountingEngine


class TestCardCountingEngine(unittest.TestCase):
  def setUp(self):
    self.engine = CardCountingEngine(skill_level=50)

  @patch('random.randint')
  def test_low_card_high_accuracy(self, mock_randint):
    mock_randint.return_value = 90
    result = self.engine.get_count_adjustment(2)
    self.assertEqual(result, 1)

  @patch('random.randint')
  def test_high_card_high_accuracy(self, mock_randint):
    mock_randint.return_value = 90
    result = self.engine.get_count_adjustment(10)
    self.assertEqual(result, -1)

  @patch('random.randint')
  def test_mid_card_high_accuracy(self, mock_randint):
    mock_randint.return_value = 90
    result = self.engine.get_count_adjustment(8)
    self.assertEqual(result, 0)

  @patch('random.randint')
  def test_low_card_medium_accuracy(self, mock_randint):
    mock_randint.return_value = 50
    result = self.engine.get_count_adjustment(3)
    self.assertEqual(result, 0)

  @patch('random.randint')
  def test_high_card_medium_accuracy(self, mock_randint):
    mock_randint.return_value = 50
    result = self.engine.get_count_adjustment(10)
    self.assertEqual(result, 0)

  @patch('random.randint')
  def test_mid_card_medium_accuracy_even(self, mock_randint):
    mock_randint.side_effect = [50, 0]
    result = self.engine.get_count_adjustment(8)
    self.assertEqual(result, 1)

  @patch('random.randint')
  def test_mid_card_medium_accuracy_odd(self, mock_randint):
    mock_randint.side_effect = [50, 1]
    result = self.engine.get_count_adjustment(8)
    self.assertEqual(result, -1)

  @patch('random.randint')
  def test_low_card_low_accuracy(self, mock_randint):
    mock_randint.return_value = 20
    result = self.engine.get_count_adjustment(2)
    self.assertEqual(result, -1)

  @patch('random.randint')
  def test_high_card_low_accuracy(self, mock_randint):
    mock_randint.return_value = 20
    result = self.engine.get_count_adjustment(10)
    self.assertEqual(result, 1)

  @patch('random.randint')
  def test_mid_card_low_accuracy_even(self, mock_randint):
    mock_randint.side_effect = [20, 0]
    result = self.engine.get_count_adjustment(8)
    self.assertEqual(result, 1)

  @patch('random.randint')
  def test_mid_card_low_accuracy_odd(self, mock_randint):
    mock_randint.side_effect = [20, 1]
    result = self.engine.get_count_adjustment(8)
    self.assertEqual(result, -1)

if __name__ == '__main__':
  unittest.main()
