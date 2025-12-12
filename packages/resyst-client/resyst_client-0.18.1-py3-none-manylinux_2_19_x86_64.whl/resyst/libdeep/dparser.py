# -*- coding: utf-8 -*-

# Copyright (C) 2025 by European Synchrotron Radiation Facility
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the “Software”), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so.
#
# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.

from __future__ import absolute_import, print_function

import re


__all__ = ['DParser',
           'DParserProxy',
           'DParserError',
           'ParserNotReadyError',
           'StringParsingError',
           'defaultparname',
           'defaultpartialparsing']


class DParserError(Exception):  pass
class ParserNotReadyError(DParserError):  pass
class StringParsingError(DParserError):  pass

_parameter_string = None


class FieldParser(object):
    FLG_TOPGROUP  = 0x001
    FLG_IGNOREOUT = 0x002
    FLG_UNSIGNED  = 0x004
    FLG_POSITIVE  = 0x008
    FLG_UPPERMODE = 0x010
    FLG_LOWERMODE = 0x020
    FLG_CASESENS  = 0x040
    FLG_DEBUGMODE = 0x080

    FLG_UPPERGLOB = 0x100
    FLG_LOWERGLOB = 0x200
    FLG_IGNOREGLOB= 0x400

    FLG_COMMON    = FLG_DEBUGMODE | FLG_IGNOREOUT | FLG_IGNOREGLOB | FLG_UPPERGLOB | FLG_LOWERGLOB
    FLG_NUMBERTYP = FLG_UNSIGNED | FLG_POSITIVE
    FLG_CASEMODES = FLG_UPPERMODE | FLG_LOWERMODE | FLG_CASESENS

    validfflags = FLG_COMMON

    isgroup = False


    def parse_exception(self, errmsg, pstr=''):
        if self.fflags & self.FLG_DEBUGMODE:
            errmsg += ' [{} {!r}: {!r}]'.format(self.fielddesc, str(self), pstr)
        return StringParsingError(errmsg)

    fielddef_xmarker = '```'
    special_chars = '])}|+_-'
    expr_string = r'[^ \n\])}|\+_-]*'
    expr_parser = None


    @classmethod
    def find_fieldstring(cls, pstring):
        if not cls.expr_parser:
            # compile cls.expr_string only once
            cls.expr_parser = re.compile(cls.expr_string)

        match = cls.expr_parser.match(pstring)

        if not match:
            return '', pstring
        else:
            return match.group(), pstring[match.end():]


    @classmethod
    def parse_fieldstring(cls, pstring, field=None):
        parsed, remain = cls.find_fieldstring(pstring)

        if parsed:
            return parsed, remain
        else:
            if field:
                raise field.parse_exception('missing or badly formed parameter', pstring)
            else:
                raise ValueError('missing or badly formed parameter')


    @classmethod
    def create(cls, parsedef, fflags, nrep):
        id = _field_ids[cls]
        if parsedef:
            newid = id + parsedef[0]
            if newid in _field_types:
                cls = _field_types[newid]
                parsedef = parsedef[1:]
                id = newid

        if not parsedef.startswith('#'):
            if cls.needsdef:
                raise ValueError('missing field definition {!r}'.format(id))
            return cls(fflags, nrep, id, ''), parsedef

        else:
            prefix = id + '#'
            parsedef = parsedef[1:]
            if issubclass(cls, NumberParser):
                field = cls(fflags, nrep, prefix, parsedef)
                remain = parsedef[len(field.fieldtag)-len(prefix):]
            else:
                if parsedef.startswith(cls.fielddef_xmarker):
                    fielddef, remain = parsedef[len(cls.fielddef_xmarker):].split(cls.fielddef_xmarker, 1)
                else:
                    fielddef, remain = FieldParser.parse_fieldstring(parsedef)

                field = cls(fflags, nrep, prefix, fielddef)
            return field, remain


    def __init__(self, fflags, nrep, prefix='', fielddef=''):
        if fflags != (fflags & self.validfflags):
            raise ValueError('no valid flags for this field')
        self.fflags = fflags
        if fflags & self.FLG_UPPERGLOB: self._to_case = str.upper
        elif fflags & self.FLG_LOWERGLOB: self._to_case = str.lower

        self.nrep = nrep
        self.separator = None
        self.fieldpfx = prefix
        self.fieldtag = prefix + fielddef
        self.listname = None
        self.unitfield = None


    def lists(self, listtype):
        if listtype == 'unit':
                yield self.listname
        else:
            if self.listname:
                yield self.listname


    def setlist(self, name, list, isunit):
        if not isunit and self.listname == name:
            self.list = list
            self.update_list_content()

    @staticmethod
    def _to_case(string):  # this method may be replaced by str.upper() or str.lower()
        return string

    def to_case(self, string):
        return self._to_case(string)


    def update_list_content(self):
        self.list = [self.to_case(elem) for elem in self.list]
        self.listlongest = max([len(elem) for elem in self.list])


    def check_spacing(self, remain, othersep='-'):
        isspaced = True
        if remain:
            if remain[0].isspace():
                remain = remain.lstrip()
            else:
                isspaced = False

        ex = None
        if self.separator == '-' and othersep == '-':
            if isspaced:
                ex = self.parse_exception('unexpected space after parameter', remain)
        elif self.separator in [None, '+'] or othersep in [None, '+']:
            if not isspaced:
                ex = self.parse_exception('missing space after parameter', remain)

        return remain, ex


    def _nrepstr(self):
        i = 'i' if self.fflags & self.FLG_IGNOREOUT else ''
        if self.nrep == 0:
            return i + 'n'
        elif self.nrep > 0:
            return i + str(self.nrep)
        else:
            return i


    def __str__(self):
        pfx = self._nrepstr()
        if self.fflags & self.FLG_POSITIVE:
            pfx += 'p'
        elif self.fflags & (self.FLG_UNSIGNED | self.FLG_UPPERMODE):
            pfx += 'u'
        elif self.fflags & self.FLG_LOWERMODE:
            pfx += 'l'
        elif self.fflags & self.FLG_CASESENS:
            pfx += 'c'
        return pfx + self.fieldtag


    def parse_one(self, remain):
        raise NotImplementedError()


    def parse(self, remain0):
        if self.nrep < 0:
            value, remain = self.parse_one(remain0)
            self.notrep = True
            return value, remain
        else:
            remain = remain0
            valuelist = []
            while not self.nrep or len(valuelist) < self.nrep:
                if valuelist:  #skip the first one, and then force spacing (sure?)
                    before, sepex = self.check_spacing(remain, '+')
                else:
                    before, sepex = remain, None
                try:
                    value, after = self.parse_one(before)
                    valuelist.append(value)
                    if after is not before:
                        if sepex:
                            break
                        remain = after
                    else:
                        if self.nrep == 0:
                            break

                except StringParsingError:
                    break

            if sepex:
                raise sepex
            nrep = len(valuelist)
            if nrep == 0 or self.nrep > 0 and self.nrep != nrep:
                raise self.parse_exception('insufficient number of parameters', remain0)
            self.notrep = False
            return valuelist, remain


    def getempty(self):
        return None



field_flags = {'p': FieldParser.FLG_POSITIVE,
               'u': FieldParser.FLG_UNSIGNED,  # this flag character shared with FLG_UPPERMODE
               'l': FieldParser.FLG_LOWERMODE,
               'c': FieldParser.FLG_CASESENS,
             }

field_separators = ['|', '-', '_', '+']


# base class for numeric fields
# not intended to be used directly
#
class NumberParser(FieldParser):
    isinteger = False
    needsdef = False
    validfflags = FieldParser.FLG_COMMON | FieldParser.FLG_NUMBERTYP

    @staticmethod
    def do_find_number(remain0, field=None):
        numstr, remain = FloatParser.do_find_number(remain0, field)
        if numstr and int(numstr) == 0 and remain[0] in 'xXoObB':
            numstr, remain = IntegerStrictParser.do_find_number(remain0, field)
        return numstr, remain

    @staticmethod
    def do_parse_number(remain0, field=None):
        numstr, remain = FloatParser.do_find_number(remain0, field)
        if numstr:
            if numstr[-1] == '0' and (remain and remain[0] in 'xXoObB') and numstr[:-1] in '+-':
                value, remain = IntegerStrictParser.do_parse_number(remain0, field)
            else:
                value = float(numstr)
                if value.is_integer():
                    value = int(value)
            return value, remain
        else:
            return None, remain0


    def __init__(self, fflags, nrep, prefix, parsedef):
        self.fflags = fflags # needed before __init__()
        self.minval, self.maxval, remain = self.do_extract_min_max(parsedef)
        fielddef = parsedef[:-len(remain)]
        super(NumberParser, self).__init__(fflags, nrep, prefix, fielddef)


    def do_extract_min_max(self, parstr):
        if not parstr:
            return None, None, parstr

        first, remain = NumberParser.do_parse_number(parstr)
        if first is None:
            min, max = None, None
        elif not remain.startswith(':'):
            min, max = (None, first) if first <= 0 else (-first, first)
        else:
            last, remain = NumberParser.do_parse_number(remain[1:])
            if last is None:
                raise ValueError('bad or missing number range values', parstr)
            else:
                min, max = first, last
                if min > max:
                    raise ValueError('minimum field value {} is greater than maximum {}'.format(min, max), parstr)
        return min, max, remain


    def check_number_value(self, value, remain0):
        if self.fflags & self.FLG_UNSIGNED and value < 0:
            raise self.parse_exception('invalid negative value {}'.format(value), remain0)
        elif self.fflags & self.FLG_POSITIVE and value <= 0:
            raise self.parse_exception('invalid non positive value {}'.format(value), remain0)
        elif self.minval is not None and value < self.minval:
            raise self.parse_exception('value {} below the minimum ({})'.format(value, self.minval), remain0)
        elif self.maxval is not None and value > self.maxval:
            raise self.parse_exception('value {} above the maximum ({})'.format(value, self.maxval), remain0)


    def parse_one(self, remain0):
        value, remain = self.do_parse_number(remain0, self)
        self.check_number_value(value, remain0)
        return value, remain



class IntegerStrictParser(NumberParser):
    isinteger = True
    expr_string = r'[-+]?0[xX][0-9a-fA-F]+|[-+]?0[bB][01]+|[-+]?0[oO][0-7]+|[-+]?\d+'
    expr_parser = None
    fielddesc = 'integer value'


    @classmethod
    def do_find_number(cls, remain, field=None):
        return cls.parse_fieldstring(remain, field)


    @staticmethod
    def do_convert_integer(parstr):
        if 'x' in parstr or 'X' in parstr:
            intvalue = int(parstr, base=16)
        elif 'o' in parstr or 'O' in parstr:
            intvalue = int(parstr, base=8)
        elif 'b' in parstr or 'B' in parstr:
            intvalue = int(parstr, base=2)
        else:
            intvalue = int(parstr)
        return intvalue

    @classmethod
    def do_parse_number(cls, remain, field=None):
        parstr, remain = cls.do_find_number(remain, field)
        return cls.do_convert_integer(parstr), remain



class DecimalParser(IntegerStrictParser):
    expr_string = r'[-+]?\d+'
    expr_parser = None
    fielddesc = 'decimal value'

class HexadecimalParser(IntegerStrictParser):
    expr_string = r'[-+]?0[xX][0-9a-fA-F]+'
    expr_parser = None
    fielddesc = 'hexadecimal value'

class OctalParser(IntegerStrictParser):
    expr_string = r'[-+]?0[oO][0-7]+'
    expr_parser = None
    fielddesc = 'octal value'

class BinaryParser(IntegerStrictParser):
    expr_string = r'[-+]?0[bB][01]+'
    expr_parser = None
    fielddesc = 'binary value'



class FloatParser(NumberParser):
    isinteger = False
    expr_string = r'[-+]?\d+(\.\d+)?([eE][-+]?\d+)?|nan|NAN|[-+]?inf|[-+]?INF'
    expr_parser = None
    fielddesc = 'floating point value'

    @classmethod
    def do_find_number(cls, remain, field=None):
        return cls.parse_fieldstring(remain, field)

    @classmethod
    def do_parse_number(cls, remain, field=None):
        parstr, remain = cls.do_find_number(remain, field)
        floatvalue = float(parstr)
        return floatvalue, remain


class IntegerParser(NumberParser):
    fielddesc = 'integer value'

    @classmethod
    def do_parse_number(cls, remain, field=None):
        floatvalue, remain = super(IntegerParser, cls).do_parse_number(remain, field)
        return int(round(floatvalue)), remain



class LabelParser(FieldParser):
    expr_string = r'[a-zA-Z]\w*'
    expr_parser = None
    fielddesc = 'label'
    needsdef = False
    validfflags = FieldParser.FLG_COMMON | FieldParser.FLG_CASEMODES
    istag = False

    def __init__(self, fflags, nrep, prefix, fielddef):
        super(LabelParser, self).__init__(fflags, nrep, prefix, fielddef)
        """ L#<reg_expr>
        """
        if fielddef:
            # check if fielddef is a simple alphanumeric string
            tag, remain = LabelParser.find_fieldstring(fielddef)
            if not remain:
                self.istag = True
                fielddef = self.to_case(fielddef)
                self.fieldtag = self.fieldpfx + fielddef

            self.expr_string = fielddef
            self.expr_parser = None


    def parse_one(self, remain0):
        if self.istag:
            taglen = len(self.expr_string)
            if self.fflags & (self.FLG_UPPERGLOB | self.FLG_LOWERGLOB):
                refstring = self.to_case(remain0[:taglen]) if taglen <= len(remain0) else ''
            else:
                refstring = remain0

            if refstring.startswith(self.expr_string):
                return True, remain0[taglen:]
            else:
                raise self.parse_exception('unmatched label/tag', remain0)
        else:
            if self.expr_string == self.__class__.expr_string:
                label, remain = self.parse_fieldstring(remain0, self)
                return self.to_case(label), remain

            if not self.expr_parser:  # compile self.expr_string if needed
                self.expr_parser = re.compile(self.expr_string)

            match = self.expr_parser.match(remain0)
            if not match:
                raise self.parse_exception('missing or badly formed parameter', remain0)
            else:
                return self.to_case(match.group()), remain0[match.end():]


class LabelGenericParser(LabelParser):
    expr_string = r'\S*'
    expr_parser = None



class StringParser(FieldParser):
    expr_string = r'\'[^\']*\'|"[^"]*"|[^\'"]*$'
    expr_parser = None
    fielddesc = 'string'
    needsdef = False
    validfflags = FieldParser.FLG_COMMON | FieldParser.FLG_CASEMODES

    def __init__(self, fflags, nrep, prefix, fielddef):
        super(StringParser, self).__init__(fflags, nrep, prefix, fielddef)
        """ S
        """
        if fielddef:
            raise ValueError('string field {!r} does not accept field arguments'.format(self.fieldtag))


    def parse_one(self, remain0):
        string, remain = self.parse_fieldstring(remain0, self)
        if not string:
            raise self.parse_exception('missing or badly formed string', remain0)

        if string[0] in '\'"':
            string = string[1:-1]
        return self.to_case(string), remain


class StringQuotedParser(StringParser):
    expr_string = r'\'[^\']*\'|"[^"]*"'
    expr_parser = None



class TagParser(LabelParser):
    fielddesc = 'tag'
    needsdef = True

    def parse_one(self, remain0):
        try:
            return super(TagParser, self).parse_one(remain0)
        except:
            return False, remain0



class ChoiceIndexParser(FieldParser):
    fielddesc = 'choice'
    needsdef = True
    validfflags = FieldParser.FLG_COMMON | FieldParser.FLG_CASEMODES

    def __init__(self, fflags, nrep, prefix, fielddef):
        super(ChoiceIndexParser, self).__init__(fflags, nrep, prefix, fielddef)
        """ C#<listname> or C#:jksdfhjk:jsdhhksdh:kdhskhkfs
        """
        if ':' in fielddef:
            self.listname = None
            self.list = fielddef.split(':')
            while self.list and not self.list[0]: del self.list[0]
            while self.list and not self.list[-1]: del self.list[-1]
            self.update_list_content()

            self.fieldtag = self.fieldpfx
            for token in self.list: self.fieldtag += token + ':'
        else:
            self.listname = fielddef
            self.list = None


    def find_in_tokenlist(self, remain0, tokenlist, maxlength):
        results = (-1, None, remain0)
        maxlen = 0
        if self.fflags & (self.FLG_UPPERGLOB | self.FLG_LOWERGLOB):
            refstring = self.to_case(remain0[:maxlength]) if len(remain0) > maxlength else self.to_case(remain0)
        else:
            refstring = remain0

        for idx, token in enumerate(tokenlist):
            if refstring.startswith(token):
                tklen = len(token)
                if tklen > maxlen:
                    remain = remain0[tklen:]
                    results = (idx, token, remain)
                    if remain and remain[0].isspace():
                        break
                    maxlen = tklen
        return results


    def parse_one(self, remain0):
        idx, token, remain = self.find_in_tokenlist(remain0, self.list, self.listlongest)
        if idx < 0:
            raise self.parse_exception('parameter not one of the valid choices', remain0)
        else:
            return idx, remain


class ChoiceTokenParser(ChoiceIndexParser):

    def parse_one(self, remain0):
        idx, remain = super(ChoiceTokenParser, self).parse_one(remain0)
        return self.list[idx], remain



class FlaglistIndexParser(ChoiceIndexParser):
    fielddesc = 'flag list'

    def parse_one(self, remain):
        flagidx = []
        while remain:
            remain0 = remain
            idx, token, remain = self.find_in_tokenlist(remain0, self.list, self.listlongest)
            if idx < 0:
                break
            if remain:
                if not remain[0].isspace():
                    remain = remain0
                    break
                remain = remain.lstrip()

            if idx not in flagidx:
                flagidx.append(idx)

        flagidx.sort()
        return flagidx, remain


class FlaglistTokenParser(FlaglistIndexParser):

    def parse_one(self, remain0):
        flagidx, remain = super(FlaglistTokenParser, self).parse_one(remain0)
        return [self.list[idx] for idx in flagidx], remain


class FlagMaskParser(FlaglistIndexParser):

    def parse_one(self, remain0):
        flagidx, remain = super(FlagMaskParser, self).parse_one(remain0)
        flagmask = 0
        for idx in flagidx:
            flagmask |= (1 << idx)
        return flagmask, remain



class BooleanParser(ChoiceIndexParser):
    fielddesc = 'boolean'
    needsdef = False

    def __init__(self, fflags, nrep, prefix, parsedef):
        if not parsedef:
            parsedef = 'Off/On:No/Yes:0/1:False/True'
        super(BooleanParser, self).__init__(fflags, nrep, prefix, parsedef)
        """ B#:<false>/<true>:
        """

        if self.listname and '/' in self.listname:
            self.list = [self.listname]
            self.listname = None

        if self.list:
            self.update_boolean_lists(self.list)
            self.fieldtag = self.fieldpfx
            blist = self.list
            while blist:
                fals, tru = blist[:2]
                self.fieldtag += '{}/{}:'.format(fals, tru)
                blist = blist[2:]


    def update_boolean_lists(self, list):
        if not list:
            raise ValueError('empty???')

        if '/' not in list[0]:
            self.list = list
        else:
            blist = []
            for entry in list:
                try:
                    fals, tru = entry.split('/', 1)
                except ValueError:
                    raise ValueError('bad format or boolean \'False/True\' entry {!r} in field {!r}'.format(entry, self.fieldtag))
                blist += [fals, tru]
            self.list = blist

        if len(self.list) & 1:
            raise ValueError('bad list {} of boolean definition(s) in field {!r}'.format(self.list, self.fieldtag))

        self.update_list_content()


    def lists(self, listtype):
        if listtype in ['bool', 'list'] and self.listname:
            yield self.listname


    def setlist(self, name, list, isunit):
        if not isunit and name == self.listname:
            self.update_boolean_lists(list)


    def parse_one(self, remain0):
        idx, remain = super(BooleanParser, self).parse_one(remain0)
        return (True if idx & 1 else False), remain


class UnitParser(ChoiceIndexParser):
    fielddesc = 'unit'
    needsdef = True

    def __init__(self, fflags, nrep, prefix, parsedef):
        super(UnitParser, self).__init__(fflags, nrep, prefix, parsedef)
        """U#<listname>[@refunit]
        """
        if '@' in self.listname:
            self.listname, self.refunitname = self.listname.split('@', 1)
            if not self.refunitname:
                ValueError('bad or missing reference unit for field {!r}'.format(self.fieldtag))
            self.reffactor = None
        else:
            self.refunitname = None
            self.reffactor = 1


    def lists(self, listtype):
        if listtype == 'unit':
            yield self.listname


    def setlist(self, name, list, isunit):
        if not isunit or name != self.listname:
            return

        self.list = [unit for unit, val in list]
        self.update_list_content()
        self.factors = [val for unit, val in list]
        if self.refunitname:
            try:
                idx = self.list.index(self.to_case(self.refunitname))
                self.reffactor = self.factors[idx]
            except ValueError:
                self.reffactor = self.list = self.factors = None
                raise ParserNotReadyError('unit list does not contain the reference unit {!r}'.format(self.refunitname))


    def parse_one(self, remain0):
        if self.reffactor is None:
            raise ParserNotReadyError('unit {!r} not initialised'.format(self.fieldtag))
        idx, remain0 = super(UnitParser, self).parse_one(remain0)
        self.unitfactor = self.factors[idx] / self.reffactor
        return self.unitfactor, remain0


    def recalcvalue(self, value):
        if self.targetclass.isinteger:
            return round(value * self.unitfactor)
        else:
            return value * self.unitfactor


    def getempty(self):
        # This may help prevent wong corrections
        self.unitfactor = 1.0
        return None



# SortedGroupParser is the base class for the other field groups

class SortedGroupParser(FieldParser):
    fielddesc = 'group'
    isgroup = True
    isexclusive = False
    validfflags = FieldParser.FLG_COMMON | FieldParser.FLG_TOPGROUP

    endchar = ')'

    @classmethod
    def create(cls, parsedef, fflags, nrep):
        parsedef = parsedef.lstrip()

        group = cls(fflags, nrep)
        group.fieldlist = []
        next_field = None
        fieldlist = []
        while True:
            next_field, parsedef = group.extract_next_field(parsedef, next_field, fflags)
            if next_field is None:
                break
            fieldlist.append(next_field)

        cls.check_unit_fields(fieldlist)
        fieldlist = cls.regroup_fields(fieldlist, '_-+', fflags)
        group.fieldlist = cls.regroup_fields(fieldlist, '|', fflags)

        nfields = len(group.fieldlist)
        group.isempty = (nfields == 0)
        if nfields == 1:
            inner_field = group.fieldlist[0]

            nrep = -(group.nrep * inner_field.nrep)
            if nrep < -1:
                nrep = -nrep

            if cls is OptionalGroupParser and not isinstance(inner_field, TagParser):
                if inner_field.isgroup: # if a group contains another group
                    if inner_field.__class__ is not UnsortedGroupParser and inner_field.nrep == -1:
                        group.fieldlist = inner_field.fieldlist
                        group.isexclusive = inner_field.isexclusive
                    # if inner_field is UnsortedGroupParser, do nothing
            elif inner_field.isgroup or not (fflags & cls.FLG_TOPGROUP):
                group = inner_field
                group.nrep = nrep
                if fflags & cls.FLG_IGNOREOUT:
                    group.fflags |= cls.FLG_IGNOREOUT

        return group, parsedef


    @staticmethod
    def check_unit_fields(fieldlist):

        def get_unitfield(field):
            if isinstance(field, UnitParser):
                return field
            elif field.isgroup:
                return get_unitfield(field.fieldlist[0])
            else:
                return None

        if len(fieldlist) < 2:
            return

        prevfield = None
        for field in fieldlist:
            if prevfield:
                unitfield = get_unitfield(field)
                if unitfield:
                    if not isinstance(prevfield, NumberParser):
                        raise ValueError('unit {!r} does not follow a numeric field'.format(str(unitfield)))
                    if prevfield.nrep >= 0:
                        raise ValueError('cannot repeat field {!r} when using units'.format(str(prevfield)))
                    if prevfield.separator == '|':
                        raise ValueError('exclusivity separator \'|\' cannot be user with unit field {!r}'.format(unitfield))
                    if not prevfield.separator:
                        prevfield.separator = '_'
                    unitfield.fflags |= field.FLG_IGNOREGLOB
                    unitfield.targetclass = prevfield.__class__
                    prevfield.unitfield = unitfield
            prevfield = field


    @staticmethod
    def regroup_fields(fieldlist, separators, fflags):
        topfieldlist = []
        subgroup = None
        for field in fieldlist:
            if field.separator and field.separator in separators:
                if not subgroup:
                    subgroup = SortedGroupParser(fflags, -1)
                    subgroup.isexclusive = ('|' in separators)
                    subgroup.fieldlist = [field]
                    subgroup.isempty = False
                    topfieldlist.append(subgroup)
                else:
                    subgroup.fieldlist.append(field)
            elif subgroup:
                subgroup.fieldlist.append(field)
                subgroup = None
            else:
                topfieldlist.append(field)
        return topfieldlist


    @classmethod
    def extract_next_field(cls, parsedef, prev_field, fflags):
        if not parsedef:
            return None, ''

        #extract optional ignore flag and preserve global case, ignore and debug modes
        fflags &= (cls.FLG_DEBUGMODE | cls.FLG_IGNOREGLOB | cls.FLG_UPPERGLOB | cls.FLG_LOWERGLOB)
        if parsedef[0] == 'i':
            fflags |= cls.FLG_IGNOREOUT | cls.FLG_IGNOREGLOB
            parsedef = parsedef[1:]

        #extract optional nrep
        if parsedef[0] == 'n':
            nrep = 0
            parsedef = parsedef[1:]
        else:
            try:
                nrep, parsedef = IntegerStrictParser.do_parse_number(parsedef)
                if nrep < 0:
                    raise ValueError('negative repetition prefix?')
                if nrep == 1:
                    nrep = -1
            except ValueError:
                nrep = -1

        #extract additional optional field flags
        while parsedef:
            if parsedef[0] not in field_flags:
                break
            fflags |= field_flags[parsedef[0]]
            parsedef = parsedef[1:]

        try:
            while parsedef:
                fldkey = parsedef[0]
                if fldkey.islower() and len(parsedef) > 1:
                    fldkey = parsedef[0:2]
                fieldtype = _field_types[fldkey]
                parsedef = parsedef[len(fldkey):]

                if (fflags & cls.FLG_UNSIGNED) and (fieldtype.validfflags & cls.FLG_UPPERMODE):
                    fflags = (fflags & ~cls.FLG_UNSIGNED) | cls.FLG_UPPERMODE
                if fflags & cls.FLG_CASESENS:
                    fflags &= ~(cls.FLG_UPPERGLOB | cls.FLG_LOWERGLOB | cls.FLG_UPPERMODE | cls.FLG_LOWERMODE)
                elif fflags & cls.FLG_UPPERMODE:
                    fflags &= ~(cls.FLG_LOWERGLOB | cls.FLG_LOWERMODE)
                    fflags |= cls.FLG_UPPERGLOB
                elif fflags & cls.FLG_LOWERMODE:
                    fflags &= ~cls.FLG_UPPERGLOB
                    fflags |= cls.FLG_LOWERGLOB

                if fieldtype.isgroup:
                    next_field, parsedef = fieldtype.create(parsedef, fflags, nrep)
                    if next_field.isgroup and next_field.isempty:
                        continue  # skip empty group and extract next one
                else:
                    next_field, parsedef = fieldtype.create(parsedef, fflags, nrep)
                    parsedef = parsedef.lstrip()

                #extract optional separator
                if parsedef and parsedef[0] in field_separators:
                    next_field.separator = parsedef[0]
                    parsedef = parsedef[1:].lstrip()
                return next_field, parsedef

            return None, parsedef

        except KeyError:
            if parsedef[0] == cls.endchar:
                if prev_field and prev_field.separator:
                    raise ValueError('unexpected separator {!r} before group closing character {!r}'.format(prev_field.separator, cls.endchar))
                else:
                    return None, parsedef[1:].lstrip()
            else:
                raise ValueError('missing end bracket {!r} or bad parsing definition string {!r}'.format(cls.endchar, parsedef))


    def parse_one_complete(self, remain):
        values = []
        prevfield = None
        unitfield = None
        othersep = '-'

        for field in self.fieldlist:
            if prevfield:
                before, ex = prevfield.check_spacing(remain, othersep)
                needsspace = True
            else:
                before, ex = remain, None

            fieldvalue, after = field.parse(before)

            if after is not before:
                if ex: raise ex
                remain = after
                prevfield = field
                othersep = '-'
            elif prevfield:
                if field.separator in [None, '+'] or (field.separator == '_' and othersep == '-'):
                    othersep = field.separator

            if unitfield:
                values[-1] = unitfield.recalcvalue(values[-1])
                unitfield = None

            if field.fflags & self.FLG_IGNOREGLOB:
                continue

            if field.isgroup and field.notrep:
                values += fieldvalue
            else:
                values.append(fieldvalue)
                unitfield = field.unitfield

        if (self.fflags & self.FLG_TOPGROUP) and prevfield:
            remain, ex = prevfield.check_spacing(remain, othersep)
            if ex: raise ex

        return values, remain


    def parse_one_exclusive(self, remain0):
        remain = remain0
        values = []
        isnotfound = True
        for field in self.fieldlist:
            isempty = True
            if isnotfound:
                try:
                    fieldvalue, remain = field.parse(remain)
                    isnotfound = isempty = False
                except StringParsingError:
                    fieldvalue = field.getempty()
            else:
                fieldvalue = field.getempty()

            if field.fflags & self.FLG_IGNOREGLOB:
                continue

            if field.isgroup and (field.notrep or isempty):
                values += fieldvalue
            else:
                values.append(fieldvalue)
        if isnotfound:
            raise self.parse_exception('parameter not found', remain0)
        return values, remain


    def parse_one(self, remain):
        if self.isexclusive:
            return self.parse_one_exclusive(remain)
        else:
            return self.parse_one_complete(remain)


    def __str__(self):
        parsedef = self._nrepstr() + _field_ids[self.__class__]
        sep = ''
        for field in self.fieldlist:
            parsedef += sep + str(field)
            if field.separator == '|':
                sep = ' | '
            elif field.separator and field.separator != '+':
                sep = field.separator
            else:
                sep = ' '
        parsedef += self.endchar
        return parsedef


    def getempty(self):
        arglist = []
        for field in self.fieldlist:
            emptyval = field.getempty()  # call even 'ignored' Unit fields
            if field.fflags & self.FLG_IGNOREGLOB:
                continue
            if isinstance(emptyval, list):
                arglist += emptyval
            else:
                arglist.append(emptyval)
        self.notrep = True
        return arglist


    def lists(self, listtype):
        for field in self.fieldlist:
            for name in field.lists(listtype):
                yield name


    def setlist(self, name, list, isunit=False):
        for field in self.fieldlist:
            field.setlist(name, list, isunit)



class OptionalGroupParser(SortedGroupParser):
    endchar = ']'

    @classmethod
    def create(cls, parsedef, fflags, nrep):
        if nrep != -1:
            raise ValueError('optional group cannot be repeated')
        return super(OptionalGroupParser, cls).create(parsedef, fflags, -1)


    def parse_one(self, remain):
        try:
            return super(OptionalGroupParser, self).parse_one(remain)
        except StringParsingError as ex:
            return self.getempty(), remain



class UnsortedGroupParser(SortedGroupParser):
    endchar = '}'

    def parse_one(self, remain0):
        # separators are not possible in unsorted groups
        remain = remain0.lstrip()

        nfields = len(self.fieldlist)
        valuelist = nfields * [None]
        parsedlist = nfields * [False]
        nparsed = last_nparsed = 0
        while nparsed < nfields:
            npending = 0
            for i, field in enumerate(self.fieldlist):
                if parsedlist[i]:
                    continue
                try:
                    before = remain.lstrip()
                    valuelist[i], after = field.parse(before)
                    if after is before:
                        npending += 1
                        continue
                    else:
                        remain = after
                    parsedlist[i] = True
                    nparsed += 1
                except StringParsingError:
                    continue

            if nparsed != last_nparsed:
                last_nparsed = nparsed
            else:
                nparsed += npending
                break
        if nparsed != nfields:
            raise self.parse_exception('missing parameters', remain0)

        values = []
        for field, fieldvalue in zip(self.fieldlist, valuelist):
            if field.fflags & self.FLG_IGNOREGLOB:
                continue

            if field.isgroup and field.notrep:
                values += fieldvalue
            else:
                values.append(fieldvalue)

        return values, remain



_field_types = {'I' : IntegerParser,
                'Is': IntegerStrictParser,
                'Id': DecimalParser,
                'Ix': HexadecimalParser,
                'Io': OctalParser,
                'Ib': BinaryParser,
                'F' : FloatParser,
                'N' : NumberParser,
                'U' : UnitParser,
                'L' : LabelParser,
                'Lg': LabelGenericParser,
                'S' : StringParser,
                'Sq': StringQuotedParser,
                'B' : BooleanParser,
                'T' : TagParser,
                'Cx': ChoiceIndexParser,
                'C' : ChoiceTokenParser,
                'Gx': FlaglistIndexParser,
                'G' : FlaglistTokenParser,
                'Gm': FlagMaskParser,
                '(': SortedGroupParser,
                '[': OptionalGroupParser,
                '{': UnsortedGroupParser,
                }



_field_ids = {cls:id for id, cls in _field_types.items()}



_default_parname = None     # None = default value (i.e. 'parameter')
_default_partial = False


def defaultparname(parname=None):
    global _default_parname

    if parname is not None:
        _default_parname = str(parname).strip()
        if _default_parname == 'parameter':
            _default_parname = None

    return _default_parname if _default_parname else 'parameter'


def defaultpartialparsing(partialparsing=None):
    global _default_partial

    if partialparsing is not None:
        _default_partial = bool(partialparsing)

    return _default_partial



class DParser(object):
    def __init__(self, parsedef, lists={},
                                 units={},
                                 parname=None,
                                 partialparsing=None,
                                 casemode=None,
                                 pdebug=False,
                                 defshowtrace=False):
        fflags = FieldParser.FLG_TOPGROUP
        if pdebug:
            fflags |= FieldParser.FLG_DEBUGMODE
        if casemode:
            cmode = str(casemode).upper()
            if cmode == 'UPPER' :   fflags |= FieldParser.FLG_UPPERGLOB
            elif cmode == 'LOWER' : fflags |= FieldParser.FLG_LOWERGLOB
            else:
                raise ValueError('{!r} is not a valid case mode'.format(casemode))

        nrep = -1

        parsedef = '({})'.format(parsedef.strip())
        fieldtype = _field_types[parsedef[0]]
        self._parser, _ = fieldtype.create(parsedef, fflags, nrep)

        self._boollists = [lname for lname in self._parser.lists('bool')]
        self._lists  = {lname:None for lname in self._parser.lists('list')}
        self._units  = {lname:None for lname in self._parser.lists('unit')}

        for lname, list in lists.items():
            if lname in self._boollists or lname in self._lists:
                self.loadlist(lname, list)

        for uname, list in system_units.items():
            if uname in self._units:
                self.loadunit(uname, list)

        for uname, list in units.items():
            if uname in self._units:
                self.loadunit(uname, list)

        self._parname = _default_parname if parname is None else str(parname).strip()
        self._partial = _default_partial if partialparsing is None else bool(partialparsing)
        self._defshowtrace = bool(defshowtrace)


    def __str__(self):
        return str(self._parser)


    def __repr__(self):
        reprstr = 'DParser {} {!r}'.format('partial' if self._partial else 'full', str(self))
        if self._parname:
            reprstr += ' parname={!r}'.format(self._parname)
        return reprstr


    def __eq__(self, other):
        if other is self:
            return True
        elif str(self) != str(other):
            return False
        elif not isinstance(other, DParser):
            return True
        else:
            return other._parname == self._parname and other._partial == self._partial


    def __call__(self, string, showtrace=None):
        try:
            args, remain = self._parser.parse(string.strip())
            errmsg = None
        except StringParsingError as ex:
            errmsg = ex.args[0]
            if self._parname:
                errmsg = errmsg.replace('parameter', self._parname)
            if showtrace or showtrace is None and self._defshowtrace:
                ex.args = (errmsg,)
                raise ex

        if errmsg:
            raise StringParsingError(errmsg)

        elif self._partial:
            return args, remain
        else:
            if remain:
                parname = self._parname if self._parname else 'parameter'
                raise self._parser.parse_exception('too many {}s'.format(parname), remain)
            return args


    def getlists(self, missing=False, boolean=None):
        lists = {}
        for name, list in self._lists.items():
            if missing and list is not None:
                continue
            isbool = name in self._boollists
            if boolean is False and isbool or boolean is True and not isbool:
                continue
            lists[name] = list
        return lists


    def getunits(self, missing=False):
        units = {}
        for name, list in self._units.items():
            if missing is True and list or missing is False and not list:
                continue
            units[name] = list
        return units


    def loadlist(self, listname, tokenlist, silent=False):
        if listname not in self._lists:
            if not silent:
                raise ValueError('token list {!r} not declared in this parser instance'.format(listname))
        else:
            self._parser.setlist(listname, tokenlist, isunit=False)
            self._lists[listname] = tokenlist
            # update full boolean list (in case it was changed...)
            self._boollists = [name for name in self._parser.lists('bool')]


    def loadunit(self, unitname, unitlist, silent=False):
        if unitname not in self._units:
            if not silent:
                raise ValueError('unit definition {!r} not declared in this parser instance'.format(unitname))
        else:
            self._parser.setlist(unitname, unitlist, isunit=True)
            self._units[unitname] = unitlist




class DParserProxy(object):
    def __init__(self, parname=None, partialparsing=None, **kwargs):

        # try a duumy parser to check that the keyword arguments are fine
        parser = DParser('', **kwargs)

        # and store them (updating the module-level defaults dependent)
        kwargs['parname'] = parser._parname
        kwargs['partialparsing'] = parser._partial

        self._parserkwargs = kwargs

        self._ptable_defstr = {}
        self._ptable_parstr = {}
        self._parserlist = []
        self._usagecounters = []


    def parser(self, defstring):
        try:
            parser = self._ptable_defstr[defstring]
            parserindex = self._parserlist.index(parser)
            isnew = False
        except KeyError:
            parser = DParser(defstring, **self._parserkwargs)
            parserindex = -1
            try:
                oldparser = self._ptable_parstr[str(parser)]
                if parser == oldparser:
                    parser = oldparser
                    parserindex = self._parserlist.index(parser)
                    isnew = False
            except KeyError:
                pass

        if parserindex < 0:  # if is new
            self._parserlist.append(parser)
            self._usagecounters.append(0)

        self._ptable_defstr[defstring] = parser
        self._ptable_parstr[str(parser)] = parser
        self._usagecounters[parserindex] += 1

        return parser


    def __call__(self, defstring, inpstring, **kwargs):
        parser = self.parser(defstring)
        return parser(inpstring, **kwargs)


    def nparsers(self):
        return len(self._parserlist)


    def nusages(self):
        return sum(self._usagecounters)


    def showusage(self):
        print('\nDParser Proxy')
        print(' - {} parser(s) in memory'.format(self.nparsers()))
        print(' - {} different definition string(s)'.format(len(self._ptable_defstr)))
        print(' - {} parser call(s)'.format(self.nusages()))
        print('Usage (per parser):')
        for idx, parser in enumerate(self._parserlist):
            nusages = self._usagecounters[idx]
            parsestr = str(parser)
            print('  #{:<3}: {:5} call(s): {}'.format(idx, nusages, parsestr))


#---------------------------------------------------

system_units = {'TIME': [('sec', 1.0),
                         ('s',   1.0),
                         ('ms',  1e-3),
                         ('us',  1e-6),
                         ('ns',  1e-9),
                         ('ps',  1e-12),
                         ('fs',  1e-15),
                         ('as',  1e-18),
                         ('min',    60),
                         ('m',      60),
                         ('hour', 3600),
                         ('h',    3600),
                         ('day',  24*3600),
                         ('d',    24*3600),
                         ('year', 365*24*3600),
                         ('y',    365*24*3600),
                        ],

            'FREQUENCY': [('Hz',  1.0),
                          ('kHz', 1e+3),
                          ('MHz', 1e+6),
                          ('GHz', 1e+9),
                          ('THz', 1e+12),
                         ],

            'DISTANCE': [('m',  1.0),
                         ('mm', 1e-3),
                         ('mm', 1e-3),
                         ('um', 1e-6),
                         ('nm', 1e-9),
                         ('pm', 1e-12),
                         ('fm', 1e-15),
                         ('am', 1e-18),
                         ('km', 1e+3),
                        ],

            'VOLTAGE': [('V',  1.0),
                        ('mV', 1e-3),
                        ('uV', 1e-6),
                        ('nV', 1e-9),
                        ('pV', 1e-12),
                        ('fV', 1e-15),
                        ('aV', 1e-18),
                        ('kV', 1e+3),
                        ('MV', 1e+6),
                       ],

            'CURRENT': [('A',  1.0),
                        ('mA', 1e-3),
                        ('uA', 1e-6),
                        ('nA', 1e-9),
                        ('pA', 1e-12),
                        ('fA', 1e-15),
                        ('aA', 1e-18),
                        ('kA', 1e+3),
                        ('MA', 1e+6),
                       ],

            'CAPACITY': [('F',  1.0),
                        ('mF', 1e-3),
                        ('uF', 1e-6),
                        ('nF', 1e-9),
                        ('pF', 1e-12),
                        ('fF', 1e-15),
                        ('aF', 1e-18),
                       ],
    }

