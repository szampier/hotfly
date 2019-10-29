import re

class fitscard:
    def __init__(self, keyword=None, value=None, type=None, comment=None, image=None):
        self._keyword = keyword
        self._value = value
        self._type = type
        self._comment = comment
        self._image = image
        if self._image: self._parse()
    
    def _parse(self):
        self._keyword, value_and_comment = map(lambda x : x.strip(), self._image.split('=', 1))
        
        if value_and_comment[0] in ['T', 'F']:
            self._type = 'B'
            self._value = value_and_comment[0]
            self._parse_comment(value_and_comment[1:])
        elif value_and_comment[0] == "'":
            self._type = 'C'
            self._parse_string_value_and_comment(value_and_comment)
        else:
            self._type = 'F'
            self._value, self._comment = map(lambda x : x.strip(), value_and_comment.split('/', 1))
    
    def _parse_comment(self, comment):
        try:
            self._comment = comment.split('/', 1)[1].strip()
        except:
            pass

    def _parse_string_value_and_comment(self, value_and_comment):
        m = re.search("([^']|'')*", value_and_comment[1:])
        self._value = m.group(0).replace("''", "'")
        self._parse_comment(value_and_comment[len(self._value)+2:])

    def format(self):
        card = None
        format = None
        string_format = "%-8s= %-20s"
        number_format = "%-8s= %20s"
        hierarch_format = "%s = %s"

        self._keyword = self._keyword.upper()
        if self._keyword == 'CONTINUE':
            card = self._keyword + ' ' + self._comment
        elif self._keyword in ['COMMENT','HISTORY']:
            card = self._keyword + ' ' + self._value
        else:
            is_string = True if self._type in ['C', 'T'] else False
            is_hierarch = True if self._keyword[:8] == 'HIERARCH' else False
            
            if is_string:
                self._value = "'%-8s'" % self._value.replace("'", "''")
                format = string_format
            else:
                self._value = self._value.upper()
                format = number_format

            if is_hierarch:
                format = hierarch_format

            card = format % (self._keyword, self._value)
            card = "%s / %s" % (card, self._comment) if self._comment
    
        return card[:80].ljust(80)
