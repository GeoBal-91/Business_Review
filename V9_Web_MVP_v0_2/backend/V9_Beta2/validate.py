"""Run the saved regression suite and write reviewable validation evidence."""
import unittest
import io
import json
import sys
import platform
from pathlib import Path
from importlib.metadata import version


def main():
    root=Path(__file__).resolve().parent
    output=root/'validation';output.mkdir(exist_ok=True)
    suite=unittest.defaultTestLoader.discover(str(root/'tests'))
    stream=io.StringIO()
    class Results(unittest.TextTestResult):
        records=[]
        def addSuccess(self,test):
            super().addSuccess(test); self.records.append({'test':test.id(),'result':'PASS'})
        def addFailure(self,test,err):
            super().addFailure(test,err); self.records.append({'test':test.id(),'result':'FAIL'})
        def addError(self,test,err):
            super().addError(test,err); self.records.append({'test':test.id(),'result':'ERROR'})
    result=unittest.TextTestRunner(stream=stream,verbosity=2,resultclass=Results).run(suite)
    (output/'regression.log').write_text(stream.getvalue())
    report={'tests_run':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),
            'passed':result.testsRun-len(result.failures)-len(result.errors)-len(result.skipped),'skipped':len(result.skipped),
            'python':platform.python_version(),'platform':platform.platform(),'dependencies':{x:version(x) for x in ['pandas','numpy','openpyxl','python-pptx','matplotlib','Pillow']},
            'cases':result.records,'limits':'New saved regression fixtures; unavailable original TC51–TC100 fixtures were not rerun.'}
    (output/'regression_results.json').write_text(json.dumps(report,indent=2))
    print(stream.getvalue())
    return 0 if result.wasSuccessful() else 1

if __name__=='__main__': sys.exit(main())
