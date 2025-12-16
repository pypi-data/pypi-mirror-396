import unittest
from m_identify_ocr.mrz import parse_mrz

class TestMRZParsing(unittest.TestCase):
    def test_td3_parsing(self):
        # Sample TD3 MRZ (Passport) - Valid example
        mrz_text = """P<GBRSURNAME<<GIVEN<NAMES<<<<<<<<<<<<<<<<<<<
1234567897GBR7501017M2501018<<<<<<<<<<<<<<<0"""
        
        result = parse_mrz(mrz_text)
        
        self.assertEqual(result['type'], 'TD3')
        self.assertEqual(result['surname'], 'SURNAME')
        self.assertEqual(result['name'], 'GIVEN NAMES')
        self.assertEqual(result['country'], 'GBR')
        self.assertEqual(result['document_number'], '123456789')
        self.assertEqual(result['birth_date'], '750101')
        self.assertEqual(result['sex'], 'M')
        self.assertEqual(result['expiry_date'], '250101')
        # self.assertTrue(result['valid'])

    def test_td1_parsing(self):
        # Sample TD1 MRZ (ID Card)
        mrz_text = """I<UTOD231458907<<<<<<<<<<<<<<<
7408122F1204159UTO<<<<<<<<<<<6
ERIKSSON<<ANNA<MARIA<<<<<<<<<<"""
        
        result = parse_mrz(mrz_text)
        
        self.assertEqual(result['type'], 'TD1')
        self.assertEqual(result['surname'], 'ERIKSSON')
        self.assertEqual(result['name'], 'ANNA MARIA')
        self.assertEqual(result['document_number'], 'D23145890')
        self.assertEqual(result['birth_date'], '740812')
        # self.assertTrue(result['valid'])

    def test_invalid_mrz(self):
        mrz_text = "This is not an MRZ"
        result = parse_mrz(mrz_text)
        self.assertIn('error', result)

if __name__ == '__main__':
    unittest.main()
