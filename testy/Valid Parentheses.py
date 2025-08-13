s = "]"


class Solution(object):
    def isValid(self, s):
        elements = list(s)
        len_el = len(elements)
        if len_el < 0:
            return False
        elif len_el % 2 != 0:
            return False
        if '(' in elements:
            try:
                index = elements.index(')') + 2
                index_2 = elements.index('(') + 2
                print(elements.index('('))
                print(elements.index(')'))
                value = index / index_2
                print(f'{value}, {index}, {index_2}')
                if value % 1 != 0:
                    print('Pass')
                    pass
                else:
                    print('False')
                    return False
            except ValueError:
                return False
        if '[' in elements:
            try:
                index = elements.index(']') + 2
                index_2 = elements.index('[') + 2
                value = index / index_2
                if value % 1 != 0:
                    pass
                else:
                    return False
            except ValueError:
                return False
        if '{' in elements:
            try:
                index = elements.index('}') + 2
                index_2 = elements.index('{') + 2
                value = index / index_2
                if value % 1 != 0:
                    pass
                else:
                    return False
            except ValueError:
                return False
        return True


sol = Solution()
print(sol.isValid(s))