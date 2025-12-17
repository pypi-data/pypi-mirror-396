
code = """
class A:
    def f():
        '''
        Doc-string.
        '''
        a = '''
 asdfasdf
'''
        '''
  asdfasdf
        asdfasdf
        asdfasdf
        '''

"""

from adtools import PyProgram

code = PyProgram.from_text(code)
print(code)
print(code.classes[0].functions[0])