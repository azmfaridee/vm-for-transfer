from compilerexception import CompilerException
from compiler import Compiler

if __name__ == '__main__':
    #inputfile = 'input-compiler/set1.t1x'
    #inputfile = 'apertium-en-ca.en-ca.t1x'
    inputfile = 'apertium-en-ca.ca-en.t1x'
    #inputfile = 'input-compiler/macro_conj_verb1.t1x'

    try:
        compiler = Compiler(inputfile)
        compiler.compile()
        compiler.optimize()
        #print compiler.def_cats
        #print compiler.variables
        #print compiler.def_attrs
        #print compiler.def_lists
        compiler.printCode()
        #compiler.printLabels()

        #print compiler.symbolTable.symbolList
        #pprint(compiler.symbolTable.childList)
    except CompilerException, ex:
        print ex
