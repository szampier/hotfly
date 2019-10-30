import unittest
from fitscard import fitscard

class TestFitsCard(unittest.TestCase):

    def test_boolean(self):
        img = "SIMPLE  =                    T / Written by IDL"
        card = fitscard(image = img)
        self.assertEqual(card.keyword(), 'SIMPLE')
        self.assertEqual(card.value(), 'T')
        self.assertEqual(card.type(), 'B')
        self.assertEqual(card.comment(), 'Written by IDL')
        
    def test_boolean_nocomment(self):
        img = "SIMPLE  =                    F"
        card = fitscard(image = img)
        self.assertEqual(card.keyword(), 'SIMPLE')
        self.assertEqual(card.value(), 'F')
        self.assertEqual(card.type(), 'B')
        self.assertIsNone(card.comment())

    def test_number(self):
        img = "BITPIX  =                    8 / Comment"
        card = fitscard(image = img)
        self.assertEqual(card.keyword(), 'BITPIX')
        self.assertEqual(card.value(), '8')
        self.assertEqual(card.type(), 'F')
        self.assertEqual(card.comment(), 'Comment')

    def test_number_nocomment(self):
        img = "BITPIX  =                    8     "
        card = fitscard(image = img)
        self.assertEqual(card.keyword(), 'BITPIX')
        self.assertEqual(card.value(), '8')
        self.assertEqual(card.type(), 'F')
        self.assertIsNone(card.comment())
        
    def test_string(self):
        img = "ORIGIN  = 'ESO-LASILLA'        / Origin"
        card = fitscard(image = img)
        self.assertEqual(card.keyword(), 'ORIGIN')
        self.assertEqual(card.value(), 'ESO-LASILLA')
        self.assertEqual(card.type(), 'C')
        self.assertEqual(card.comment(), 'Origin')

    def test_string_nocomment(self):
        img = "ORIGIN  = 'ESO-LASILLA'"
        card = fitscard(image = img)
        self.assertEqual(card.keyword(), 'ORIGIN')
        self.assertEqual(card.value(), 'ESO-LASILLA')
        self.assertEqual(card.type(), 'C')
        self.assertIsNone(card.comment())
        
    def test_string_with_quotes(self):
        img = "ORIGIN  = 'ESO''LASILLA'        / Origin"
        card = fitscard(image = img)
        self.assertEqual(card.keyword(), 'ORIGIN')
        self.assertEqual(card.value(), "ESO'LASILLA")
        self.assertEqual(card.type(), 'C')
        self.assertEqual(card.comment(), 'Origin')
         
    def test_string_with_equals_slash(self):
        img = "ORIGIN  = 'ESO=LASILLA/'        / Origin"
        card = fitscard(image = img)
        self.assertEqual(card.keyword(), 'ORIGIN')
        self.assertEqual(card.value(), "ESO=LASILLA/")
        self.assertEqual(card.type(), 'C')
        self.assertEqual(card.comment(), 'Origin')

    def test_comment(self):
        img = "COMMENT this is a comment"
        card = fitscard(image = img)
        self.assertEqual(card.keyword(), 'COMMENT')
        self.assertEqual(card.value(), "this is a comment")
        self.assertIsNone(card.comment())

    def test_history(self):
        img = "HISTORY this is history"
        card = fitscard(image = img)
        self.assertEqual(card.keyword(), 'HISTORY')
        self.assertEqual(card.value(), "this is history")
        self.assertIsNone(card.comment())
        
    def test_continue(self):
        img = "CONTINUE 'long string'"
        card = fitscard(image = img)
        self.assertEqual(card.keyword(), 'CONTINUE')
        self.assertEqual(card.comment(), "'long string'")
        self.assertIsNone(card.value())

    def test_hierarch(self):
        img = "HIERARCH ESO DPR TYPE = 'OBJECT  ' / Observation type"
        card = fitscard(image = img)
        self.assertEqual(card.keyword(), 'HIERARCH ESO DPR TYPE')
        self.assertEqual(card.value(), 'OBJECT  ')
        self.assertEqual(card.type(), 'C')
        self.assertEqual(card.comment(), 'Observation type')
        
if __name__ == '__main__':
    unittest.main()
