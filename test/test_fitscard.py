import unittest
from fitscard import fitscard


class TestFitsCard(unittest.TestCase):

    def test_parse_boolean(self):
        img = "SIMPLE  =                    T / Written by IDL"
        card = fitscard(image=img)
        self.assertEqual(card.keyword(), 'SIMPLE')
        self.assertEqual(card.value(), 'T')
        self.assertEqual(card.type(), 'B')
        self.assertEqual(card.comment(), 'Written by IDL')

    def test_parse_boolean_nocomment(self):
        img = "SIMPLE  =                    F"
        card = fitscard(image=img)
        self.assertEqual(card.keyword(), 'SIMPLE')
        self.assertEqual(card.value(), 'F')
        self.assertEqual(card.type(), 'B')
        self.assertIsNone(card.comment())

    def test_parse_number(self):
        img = "BITPIX  =                    8 / Comment"
        card = fitscard(image=img)
        self.assertEqual(card.keyword(), 'BITPIX')
        self.assertEqual(card.value(), '8')
        self.assertEqual(card.type(), 'F')
        self.assertEqual(card.comment(), 'Comment')

    def test_parse_number_nocomment(self):
        img = "BITPIX  =                    8     "
        card = fitscard(image=img)
        self.assertEqual(card.keyword(), 'BITPIX')
        self.assertEqual(card.value(), '8')
        self.assertEqual(card.type(), 'F')
        self.assertIsNone(card.comment())

    def test_parse_string(self):
        img = "ORIGIN  = 'ESO-LASILLA'        / Origin"
        card = fitscard(image=img)
        self.assertEqual(card.keyword(), 'ORIGIN')
        self.assertEqual(card.value(), 'ESO-LASILLA')
        self.assertEqual(card.type(), 'C')
        self.assertEqual(card.comment(), 'Origin')

    def test_parse_string_nocomment(self):
        img = "ORIGIN  = 'ESO-LASILLA'"
        card = fitscard(image=img)
        self.assertEqual(card.keyword(), 'ORIGIN')
        self.assertEqual(card.value(), 'ESO-LASILLA')
        self.assertEqual(card.type(), 'C')
        self.assertIsNone(card.comment())

    def test_parse_string_with_quotes(self):
        img = "ORIGIN  = 'ESO''LASILLA'        / Origin"
        card = fitscard(image=img)
        self.assertEqual(card.keyword(), 'ORIGIN')
        self.assertEqual(card.value(), "ESO'LASILLA")
        self.assertEqual(card.type(), 'C')
        self.assertEqual(card.comment(), 'Origin')

    def test_parse_string_with_equals_slash(self):
        img = "ORIGIN  = 'ESO=LASILLA/'        / Origin"
        card = fitscard(image=img)
        self.assertEqual(card.keyword(), 'ORIGIN')
        self.assertEqual(card.value(), "ESO=LASILLA/")
        self.assertEqual(card.type(), 'C')
        self.assertEqual(card.comment(), 'Origin')

    def test_parse_comment(self):
        img = "COMMENT this is a comment"
        card = fitscard(image=img)
        self.assertEqual(card.keyword(), 'COMMENT')
        self.assertEqual(card.value(), "this is a comment")
        self.assertIsNone(card.comment())

    def test_parse_history(self):
        img = "HISTORY this is history"
        card = fitscard(image=img)
        self.assertEqual(card.keyword(), 'HISTORY')
        self.assertEqual(card.value(), "this is history")
        self.assertIsNone(card.comment())

    def test_parse_continue(self):
        img = "CONTINUE 'long string'"
        card = fitscard(image=img)
        self.assertEqual(card.keyword(), 'CONTINUE')
        self.assertEqual(card.comment(), "'long string'")
        self.assertIsNone(card.value())

    def test_parse_hierarch(self):
        img = "HIERARCH ESO DPR TYPE = 'OBJECT  ' / Observation type"
        card = fitscard(image=img)
        self.assertEqual(card.keyword(), 'HIERARCH ESO DPR TYPE')
        self.assertEqual(card.value(), 'OBJECT  ')
        self.assertEqual(card.type(), 'C')
        self.assertEqual(card.comment(), 'Observation type')

    def test_format_boolean(self):
        card = fitscard('SIMPLE', 'T', 'B', 'conforms to FITS standard')
        expected = self.pad_to_80("SIMPLE  =                    T / conforms to FITS standard")
        self.assertEqual(card.format(), expected)

    def test_format_number(self):
        card = fitscard('BITPIX', '-64', 'I', 'array data type')
        expected = self.pad_to_80("BITPIX  =                  -64 / array data type")
        self.assertEqual(card.format(), expected)

    def test_format_number_nocomment(self):
        card = fitscard('NAXIS1', '100', 'I')
        expected = self.pad_to_80("NAXIS1  =                  100")
        self.assertEqual(card.format(), expected)

    def test_format_string(self):
        card = fitscard('OBSERVER', 'Edwin Hubble', 'C', 'Mount Wilson Observatory')
        expected = self.pad_to_80("OBSERVER= 'Edwin Hubble'       / Mount Wilson Observatory")
        self.assertEqual(card.format(), expected)

    def test_format_hierarch_string(self):
        card = fitscard('HIERARCH ESO DRS DARKCOR', '/sciproc/HAWKI/calib/2019-03-22', 'C')
        expected = self.pad_to_80("HIERARCH ESO DRS DARKCOR = '/sciproc/HAWKI/calib/2019-03-22'")
        self.assertEqual(card.format(), expected)

    def test_format_hierarch_string_long(self):
        card = fitscard('HIERARCH ESO DRS DARKCOR', '/sciproc/HAWKI/calib/2019-03-22/HI_MDRK_190322A_10.0', 'C')
        expected = "HIERARCH ESO DRS DARKCOR= '/sciproc/HAWKI/calib/2019-03-22/HI_MDRK_190322A_10.0'"
        self.assertEqual(card.format(), expected)

    def pad_to_80(self, str):
        if len(str) >= 80:
            return str
        else:
            return '%s%s' % (str, ' ' * (80 - len(str)))


if __name__ == '__main__':
    unittest.main()
