
code = """
class A:
    def f():
        '''
        Doc-string.
        '''
        a = '''
  asdfasdf
'''

"""

from adtools import PyProgram

code = PyProgram.from_text(code)
print(code)