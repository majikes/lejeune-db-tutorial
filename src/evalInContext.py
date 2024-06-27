import json
import time
import tempfile
from subprocess import Popen, PIPE, TimeoutExpired, run
from datetime import datetime
import re
import sys
from collections import namedtuple

# Worker pool exceptions
WorkerpoolExceptions = namedtuple('WorkerpoolExceptions', 'key onyen id, question value')
workerpoolExceptions = [
   WorkerpoolExceptions(key='game-nuclear-4',           id=24532, onyen='neil557', question='Sabotage.Part.4.0', value=False),
   WorkerpoolExceptions(key='m1-farm-example-scale-34', id=16283, onyen='amayak', question='No.teams.2', value=False),
   WorkerpoolExceptions(key='m1-farm-example-scale-34', id=16100, onyen='arvind10', question='Stadiums.2', value=False),
   WorkerpoolExceptions(key='m1-farm-example-scale-34', id=16096, onyen='asenthil', question='Stadiums.1', value=False),
   WorkerpoolExceptions(key='m1-farm-example-scale-34', id=15473, onyen='choinier', question='Wins.Above.Bubble.2', value=False),
   WorkerpoolExceptions(key='m1-farm-example-scale-34', id=16247, onyen='elvisrc',  question='Stadiums.3',          value=False),
   WorkerpoolExceptions(key='m1-farm-example-scale-34', id=16249, onyen='gigicole',  question='Wins.Above_Bubble.2', value=False),
   WorkerpoolExceptions(key='m1-farm-example-scale-34', id=16249, onyen='gigicole',  question='List.names.2', value=True),
   WorkerpoolExceptions(key='m1-farm-example-scale-34', id=16230, onyen='gtsun',     question='_scratch_sql_queries.1', value=False),
   WorkerpoolExceptions(key='m1-farm-example-scale-34', id=16092, onyen='kvgzz',    question='Conference.Player.No.1', value=False),
   WorkerpoolExceptions(key='m1-farm-example-scale-34', id=16122, onyen='victorar', question='Wins.Above.Bubble_1', value=False),

    WorkerpoolExceptions(key='m2-store-cloudy-yogurt-26', id=26757, onyen='jmajikes', question='Jobs.4', value=False),
    WorkerpoolExceptions(key='m2-store-cloudy-yogurt-26', id=26439, onyen='ssofia', question='Age.4', value=True),
   WorkerpoolExceptions(key='m2-store-cloudy-yogurt-26', id=26415, onyen='jykim1', question='Jobs.3', value=False),
   WorkerpoolExceptions(key='m2-store-cloudy-yogurt-26', id=26361, onyen='joeykim', question='Jobs.3', value=False),
   WorkerpoolExceptions(key='m2-store-cloudy-yogurt-26', id=26466, onyen='hptaylor', question='Age.2', value=False),
   WorkerpoolExceptions(key='m2-store-cloudy-yogurt-26', id=28989, onyen='hptaylor', question='Age.2', value=True),
   WorkerpoolExceptions(key='m2-store-cloudy-yogurt-26', id=24103, onyen='mia23', question='Jobs.2', value=False),
   WorkerpoolExceptions(key='game-nuclear-2',         id=23079, onyen='chenpy',   question='Company.all.parts.0.0', value=False),
   WorkerpoolExceptions(key='game-nuclear-3',         id=23229, onyen='fdahnoun', question='Employee.Door.Counts.0.2', value=False),
   WorkerpoolExceptions(key='game-nuclear-3',         id=23387, onyen='ira01',    question='Employee.rooms.0.0', value=False),
   WorkerpoolExceptions(key='m1-body-group-it-70',    id=13877, onyen='cooperhc', question='List.Games.1',       value=False),
   WorkerpoolExceptions(key='m1-body-group-it-70',    id=13861, onyen='harinkim', question='Schools.With.Roster.Size.1',  value=False),
   WorkerpoolExceptions(key='m1-body-group-it-70',    id=13828, onyen='vlalitha', question='Schools.With.Roster.Size.1',  value=False),
   WorkerpoolExceptions(key='m1-dear-more-too-63',    id=7522,  onyen='aer',      question=None,                 value=None),
   WorkerpoolExceptions(key='m1-dear-more-too-63',    id=7584,  onyen='harley87', question=' Number.Senators.2', value=False),
   WorkerpoolExceptions(key='m1-dear-more-too-63',    id=7589,  onyen='kiing17',  question=' Name.2',            value=False),
   WorkerpoolExceptions(key='m1-dear-more-too-63',    id=7535,  onyen='conglu',   question=None,                 value=None),
   WorkerpoolExceptions(key='m1-dear-more-too-63',    id=7641,  onyen='phazel',   question=None,                 value=None),
   WorkerpoolExceptions(key='m1-dear-more-too-63',    id=7664,  onyen='quadland', question=None,                 value=None),
   WorkerpoolExceptions(key='m1-dear-more-too-63',    id=7594,  onyen='richard3', question=None,                 value=None),
   WorkerpoolExceptions(key='m1-dear-more-too-63',    id=7595,  onyen='sagana',   question=None,                 value=None),
   WorkerpoolExceptions(key='m1-dear-more-too-63',    id=7499,  onyen='sbs9642',  question=None,                 value=None),
   WorkerpoolExceptions(key='m1-dear-more-too-63',    id=7662,  onyen='narivi',   question=' Name.3',            value=False),
   WorkerpoolExceptions(key='m2-were-garage-fish-81', id=14466, onyen='bgatts',   question=None,                 value=None),
   WorkerpoolExceptions(key='m2-were-garage-fish-81', id=15364, onyen='bgatts',   question=None,                 value=None),
   WorkerpoolExceptions(key='m2-were-garage-fish-81', id=14329, onyen='mjaynes',  question=None,                 value=None),

    WorkerpoolExceptions(key='fe-length-tell-mix-38',  id=23260, onyen='djfrisby', question=None,                 value=None),
    WorkerpoolExceptions(key='fe-length-tell-mix-38',  id=22956, onyen='ryanspru', question='Author.Category.3',  value=True),
    WorkerpoolExceptions(key='fe-root-necessary-serve-61', id=38748, onyen='arogya', question='Author.Category.3',  value=False),
    WorkerpoolExceptions(key='fe-root-necessary-serve-61', id=38724, onyen='jgwang', question='Author.Category.3',  value=False),
    WorkerpoolExceptions(key='fe-root-necessary-serve-61', id=39279, onyen='ayanam', question='State.Population.1', value=False),

                       ]


def json_converter(obj):
    if isinstance(obj, datetime):
       return str(obj)


def evalInContext(code, context):
    """Use node to evaluate the javascript code"""
    start = time.time()
    input = json.dumps({"code": code, "context": context}, default=json_converter).encode("utf-8")
    try:
         proc = Popen(["node", "runner.js"],
                      stdin=PIPE, stdout=PIPE, stderr=PIPE)
         output, error = proc.communicate(input=input, timeout=10)
         output = output.decode("utf-8")
         error  = error.decode("utf-8")
    except TimeoutExpired:
        proc.kill()
        output, error = proc.communciate(timeout=10)
        output = output.decode("utf-8")
        error  = error.decode("utf-8")
        print(f"Popen timeout: input={input}")
        print(f"               output={output}")
        print(f"               stderr={error}")
        raise
    except Exception as e:
        print(f"execInNode input={input}" + str(e))
        raise

    if error:
        print("Error while calling runner.js from EvalInContext.py\n")
        print(error)
    try:
       decoded = json.loads(output)
    except:
       print("probably have console.log statements in evalInContext.js")
       print(output)
       raise
    print("elapsed: ", time.time() - start)
    return decoded

def NTF():
    """Return a temporary file"""
    return tempfile.NamedTemporaryFile(mode="w+t")

def evalMultiple(answers, rubrics, key=None, onyen=None, id=None):
    """Use node to evaluate answers to multiple questions,
    key and onyen used to fix known problems with workerpool
    See ljacob23 m1-dear-more-too-63 Positions.Held.13"""
    start = time.time()
    answers = {k:v.replace('λ', 'lambda') if isinstance(v, str) else v for k,v in answers.items()}
    # create temporary files for communication with node
    with NTF() as ifile, NTF() as ofile:
        # write the inputs to the temporary file
        json.dump({"answers": answers, "rubrics": rubrics}, ifile, default=json_converter)
        # flush to make sure node sees it
        ifile.flush()
        #invoke node to run the tests
        result = run(
           ["node", "--experimental-worker", "static/js/runner.js", ifile.name, ofile.name],
            capture_output=True)
        # print anything logged by the node code
        stdout = result.stdout.decode("utf-8")
        if stdout:
            print(stdout, file=sys.stdout)
        stderr = result.stderr.decode("utf-8")
        corrections = dict()
        if stderr:
            known_error = [(' Positions.Held.13', "SELECT DISTINCT P.firstname, P.lastname, T1.termtype\r\nFROM Politicians P, Terms T1, Terms T2, Terms T3\r\nWHERE T1.bioid=T2.bioid and T2.bioid=T3.bioid and P.bioid=T1.bioid and T1.termtype!=T2.termtype and T2.termtype!=T3.termtype and T3.termtype!=T1.termtype", True),
                           (' Name.2', 'SELECT firstname\r\nFROM Politicians p\r\nWHERE p.firstname LIKE ("%a") AND p.firstname LIKE ("%l%") ', False)]
            for wpe in workerpoolExceptions:
               if key==wpe.key and id==wpe.id and onyen==wpe.onyen:
                   if wpe.question and wpe.value:
                      corrections = rubrics[wpe.question].copy()
                      corrections[wpe.question] = dict(correct=wpe.value)
                   break
            else:
                if len(answers.keys()) == 1:
                    field = list(answers.keys())[0]
                    print(f'Exception key={key} onyen={onyen} id={id} field={field}')
                    output = json.load(ofile)
                    output[field]['correct'] = False
                    return {field:output[field]}
                    # evalMultiple called with one answer and failed, just say false
                # Evaluate answers one at a time
                print(f'Due to stderr, must evaluate key={key}, onyen={onyen}, post_id={id} manually')
                output = {}
                for k,v in answers.items():
                    if k not in rubrics:
                        continue  # This key is not an answer
                    try:
                        result = evalMultiple({k:v}, rubrics, key, onyen, id)
                        output.update({k:result[k]})
                    except Exception as e:
                        print('Must handle this manually')
                        import pdb; pdb.set_trace()
                        print(stderr, file=sys.stderr)
                return output
        try:
            output = json.load(ofile)
            output.update(corrections)
        except json.JSONDecodeError as err:
            print(output, file=sys.stderr)
            output = {}
    return output

def checkForErrors(output):
    """Check the output of evalMultiple for errors"""
    errors = [
        f"{tag}: {output[tag]['error']}" for tag in output if "error" in output[tag]
    ]
    return errors

if __name__ == "__main__":
    test = evalInContext("3 * A", {"A": 4})
    print(test)
    test = evalInContext(
        "function f(A) { return len(A); }", {"_return": "f", "_args": [[1, 2, 3]]}
    )
    print(test)
