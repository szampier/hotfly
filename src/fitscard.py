import re


class fitscard:

    def __init__(self, keyword=None, value=None, type=None, comment=None, image=None):
        self._keyword = keyword
        self._value = value
        self._type = type
        self._comment = comment.strip() if comment is not None else None
        self._image = image
        if self._image:
            self._parse()

    def _parse(self):
        kwd = self._image[:8].strip()
        if kwd == 'CONTINUE':
            self._keyword = kwd
            self._comment = self._image[8:].strip()
        elif kwd == 'HISTORY' or kwd == 'COMMENT':
            self._keyword = kwd
            self._value = self._image[8:].strip()
        else:
            self._keyword, value_and_comment = map(lambda x: x.strip(), self._image.split('=', 1))
            firstchar = value_and_comment[0]
            if firstchar in ['T', 'F']:
                self._type = 'B'
                self._value = firstchar
                self._parse_comment(value_and_comment)
            elif firstchar == "'":
                self._type = 'C'
                self._parse_string_value_and_comment(value_and_comment)
            else:
                self._type = 'F'
                self._value = value_and_comment.split('/', 1)[0].strip()
                self._parse_comment(value_and_comment)

    def _parse_comment(self, value_and_comment):
        try:
            self._comment = value_and_comment.split('/', 1)[1].strip()
        except Exception:
            pass

    def _parse_string_value_and_comment(self, value_and_comment):
        m = re.search("([^']|'')*", value_and_comment[1:])
        self._value = m.group(0).replace("''", "'")
        self._parse_comment(value_and_comment[len(self._value) + 2:])

    def keyword(self):
        return self._keyword

    def value(self):
        return self._value

    def type(self):
        return self._type

    def comment(self):
        return self._comment

    def format(self):
        card = None
        format = None
        string_format = "%-8s= %-20s"
        number_format = "%-8s= %20s"

        self._keyword = self._keyword.upper()
        if self._keyword == 'CONTINUE':
            card = self._keyword + ' ' + self._comment
        elif self._keyword in ['COMMENT', 'HISTORY']:
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
                if len(self._keyword) + len(self._value) == 78:
                    format = "%s= %s"
                else:
                    format = "%s = %s"

            card = format % (self._keyword, self._value)
            if self._comment:
                card = "%s / %s" % (card, self._comment)

        return card[:80].ljust(80)
