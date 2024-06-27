const { hash } = require("./myhash.js");

/** @typedef {Object} LiteralRubric
 * @property {"text"|"decimal"|"hex"|"binary"|"table"} kind
 * @property {string} [solution]
 * @property {number} [points]
 * @property {boolean} [preserveCase]
 * @property {boolean} [preserveZeros]
 * @property {boolean} [preserveSpaces]
 * @property {string} [expectedHash]
 * @property {string} [result]
 * @property {string} [resultHash]
 * @property {boolean} [correct]
 * @property {string} [error]
 */

/** @typedef {Object} RubricTest
 * @property {Object} context
 * @property {string} [resultHash]
 * @property {string} [expectedHash]
 * @property {boolean} [correct]
 * @property {string} [result]
 */

/** @typedef {Object} ExpressionRubric
 * @property {"expression"|"function"} kind
 * @property {string} [solution]
 * @property {number} [points]
 * @property {RubricTest[]} tests
 * @property {boolean} [correct]
 * @property {string} [error]
 */

/** @typedef {Object} SQLTest
 * @property {string} db
 * @property {string} [resultHash]
 * @property {string} [expectedHash]
 * @property {boolean} [correct]
 * @property {import("./sqlWorker.js").dbResult[]} [result]
 */

/** @typedef {Object} SQLRubric
 * @property {"sql"} kind
 * @property {string} [solution]
 * @property {number} [points]
 * @property {SQLTest[]} tests
 * @property {boolean} [sort]
 * @property {number} [timeout]
 * @property {boolean} [correct]
 * @property {string} [error]
 */

/** @typedef {Object} SelectRubric
 * @property {"select"|"checkbox"} kind
 * @property {string} [solution]
 * @property {number} [points]
 * @property {string[]} [choices]
 * @property {boolean} [correct]
 */

/** @typedef {LiteralRubric | ExpressionRubric | SQLRubric | SelectRubric } Rubric
 */

/** @typedef {Object} CheckResult
 * @property {string} [expectedHash]
 * @property {string} [resultHash]
 * @property {boolean} [correct]
 */

/** format results for checking or constructing answers
 * @param {string} expectedHash
 * @param {string} resultHash
 * @returns {CheckResult}
 */
function check(expectedHash, resultHash) {
  let correct = expectedHash == resultHash;
  if (typeof expectedHash == "string") {
    return { correct, expectedHash, resultHash };
  } else {
    return { expectedHash: resultHash };
  }
}

/** include correct if all tests include it
 * @typedef {Object} testResult
 * @property {boolean} [correct]
 * @property {any} [result] - why do I need this?

 * checkTests - see if all the tests passed
 * @param {testResult[]} tests
 * @returns {Object}
 * @property {boolean} [correct]
 */
function checkTests(tests) {
  if (tests.every((t) => "correct" in t)) {
    return { correct: tests.every((t) => t.correct) };
  }
  return {};
}

/** validate user inputs for mypoll
 * @param {string} input
 * @param {Rubric} rubric
 * @returns {Promise<Rubric>}
 */
async function validate(input, rubric) {
  let normalized = input || '';   // Handle undefined
  normalized = normalized.trim();
  if (!normalized.length) {
    return { ...rubric, correct: false };
  }
  switch (rubric.kind) {
    case "text":
      if (!rubric.preserveCase) {
        normalized = normalized.toUpperCase();
      }
      if (!rubric.preserveSpaces) {
        normalized = normalized.replace(/\s+/g, "");
      }
      return {
        ...rubric,
        result: normalized,
        ...check(rubric.expectedHash, hash(normalized)),
      };
    case "decimal":
    case "hex":
    case "binary":
      let pattern = {
        decimal: /^[\d.]+$/,
        hex: /^[0-9A-F.]+$/,
        binary: /^[01.]+$/,
      }[rubric.kind];
      normalized = input.toUpperCase();
      if (!pattern.test(normalized)) {
        return { ...rubric, error: "invalid character" };
      }
      if (!rubric.preserveZeros) {
        // replace 0's before first nonzero digit
        normalized = normalized.replace(/^0+(?=.)/, "");
        // drop .0* from the right end
        normalized = normalized.replace(/\.0*$/, "");
        // drop trailing 0's after a point
        normalized = normalized.replace(/(\..*)0+/, "$1");
      }
      return {
        ...rubric,
        result: normalized,
        ...check(rubric.expectedHash, hash(normalized)),
      };

    case "select":
    case "checkbox":
      if ("solution" in rubric) {
        return { ...rubric, correct: input == rubric.solution };
      }
      return { ...rubric, correct: null };
    case "table":
      return { ...rubric, ...check(rubric.expectedHash, hash(input)) };

    case "expression":
      return validateExpression(input, rubric);

    case "function":
      return validateFunction(input, rubric);

    case "sql":
      return validateSQL(input, rubric);
  }
}

const Babel = require("babel-core");
/** validate user expression in context
 * @param {string} expr
 * @param {ExpressionRubric} rubric
 * @returns {Rubric}
 */
function validateExpression(expr, rubric) {
  // some functions that are always available
  const functions = {
    log: Math.log,
    log10: Math.log10,
    log2: Math.log2,
    sqrt: Math.sqrt,
    ceil: Math.ceil,
    floor: Math.floor,
    abs: Math.abs,
  };

  // Remove the ZWSP from expression
  expr = expr.replace(/[\u200B-\u200F]/g, '');

  const tests = []; // outgoing test results
  for (const test of rubric.tests) {
    let context = Object.assign({}, functions, test.context);

    // hacked from https://medium.com/@bvjebin/js-infinite-loops-killing-em-e1c2f5f2db7f
    let transformer = () => {
      function notAllowed(path) {
        throw path.buildCodeFrameError("Not allowed");
      }
      return {
        visitor: {
          WhileStatement: notAllowed,
          DoWhileStatement: notAllowed,
          ForStatement: notAllowed,
          MemberExpression: notAllowed,
          ObjectExpression: notAllowed,
          NewExpression: notAllowed,
          AssignmentExpression: notAllowed,
          ArrowFunctionExpression: notAllowed,
          BlockStatement: notAllowed,
          ConditionalExpression: notAllowed,
          // prevent global variables
          Identifier(path) {
            let name = path.node.name;
            if (name in context || path.scope.hasBinding(name)) {
              return;
            }
            throw path.buildCodeFrameError("No globals");
          },
        },
      };
    };

    // transform the user's code
    try {
      var tfunc = Babel.transform(`(${expr})`, { plugins: [transformer] }).code;
    } catch (e) {
      return { ...rubric, error: "" + e.message };
    }
    tfunc = `return ${tfunc}`;
    try {
      var result = new Function(...Object.keys(context), tfunc)(
        ...Object.values(context)
      );
    } catch (e) {
      return { ...rubric, error: e.message };
    }

    // round if requested
    let toHash = result;
    if (typeof result == "number") {
      if (result == Math.floor(result)) {
        toHash = result.toString();
      } else {
        toHash = result.toPrecision(context._digits || 3);
      }
    }
    tests.push({
      ...test,
      result: toHash,
      ...check(test.expectedHash, hash(toHash)),
    });
  }
  return { ...rubric, tests, ...checkTests(tests) };
}

/*
 * run student code in a context
 * prevent infinite loops
 * count iterations
 */

/** validate user expression in context
 * @param {string} func
 * @param {ExpressionRubric} rubric
 * @returns {Rubric}
 */
function validateFunction(func, rubric) {
  // some functions that are always available
  const functions = {
    log: Math.log,
    log10: Math.log10,
    log2: Math.log2,
    sqrt: Math.sqrt,
    ceiling: Math.ceil,
    floor: Math.floor,
    abs: Math.abs,
  };

  // Remove the ZWSP from function
  func = func.replace(/[\u200B-\u200F]/g, '');

  const tests = [];
  for (const test of rubric.tests) {
    let context = Object.assign({}, functions, test.context);
    const args = context._args;
    delete context._args;

    // hacked from https://medium.com/@bvjebin/js-infinite-loops-killing-em-e1c2f5f2db7f
    let transformer = (babel) => {
      var t = babel.types;
      // transform a loop by adding our callback
      function loopTransform(path) {
        if ("_loop" in context) {
          path
            .get("body")
            .pushContainer(
              "body",
              t.expressionStatement(t.callExpression(t.identifier("_loop"), []))
            );
        }
      }

      return {
        visitor: {
          // prevent endless loops
          WhileStatement: loopTransform,
          DoWhileStatement: loopTransform,
          ForStatement: loopTransform,
          // prevent member access
          MemberExpression(path) {
            // example of disallowing member access
            throw path.buildCodeFrameError("Not allowed");
          },
          // prevent object creation
          ObjectExpression(path) {
            // no objects allowed
            throw path.buildCodeFrameError("Not allowed");
          },
          // prevent calling new
          NewExpression(path) {
            throw path.buildCodeFrameError("Not allowed");
          },
          // prevent global variables
          Identifier(path) {
            let name = path.node.name;
            if (name in context || path.scope.hasBinding(name)) {
              return;
            }
            throw path.buildCodeFrameError("No globals");
          },
        },
      };
    };

    // transform the user's code
    try {
      var tfunc = Babel.transform(func, { plugins: [transformer] }).code;
    } catch (e) {
      return { ...rubric, error: e.message };
    }
    // we should handle the insertion of the return better
    // could the transformer somehow do it?
    // jamming it on at the front is making lots of assumptions about the
    // shape of their code. We could put one at the end returning a specific
    // name, perhaps specified as an argument? Or maybe we use the transformer
    // code to fetch the name of the function defined in the code? Suppose they
    // define more than one? Which one to call?
    if ("_return" in context) {
      tfunc = tfunc + `\nreturn ${context._return}`;
    } else {
      tfunc = "return " + tfunc;
    }
    try {
      var result = new Function(...Object.keys(context), tfunc)(
        ...Object.values(context)
      );
    } catch (e) {
      return { ...rubric, error: e.message };
    }

    // if the result is a function and we got _args in the context, then
    // call the function
    if (Array.isArray(args) && result instanceof Function) {
      try {
        result = result(...args);
      } catch (e) {
        return { ...rubric, error: e.message };
      }
    }
    // round if requested
    let toHash = result;
    if (typeof result == "number") {
      // 64 ** (1/4) is different in lowest digits in Node vs JS
      toHash = +Number.parseFloat(result).toFixed(context._digits || 3);
    }
    tests.push({ ...test, result, ...check(test.expectedHash, hash(toHash)) });
  }
  return { ...rubric, tests, ...checkTests(tests) };
}

const workerpool = require("workerpool");

let wpath =
  typeof window !== "undefined"
    ? "/static/js/sqlWorker.js"
    : "./static/js/sqlWorker.js";

let pool = null;

class WorkerPoolError extends Error {
  constructor(message) {
     super(message);
     this.name = "WorkerPoolError";
  }
}

/** validateSQL validate user sql
 * @param {string} query
 * @param {SQLRubric} rubric
 * @returns {Promise<SQLRubric>}
 */
async function validateSQL(query, rubric) {
  if (!pool) {
    pool = workerpool.pool(wpath, { maxWorkers: 1 });
  }
  const tests = [];
  for (const test of rubric.tests) {
    // prefetch the db so that time isn't counted in the timeout below
    await pool.exec("prefetch", [test.db]);
    try {
      /** @type {import("./sqlWorker.js").evalSQLresult} r */
      let cmd = test.ic ? test.ic : query;
      const r = await pool
           .exec("evalSQL", ["PRAGMA FOREIGN_KEYS=ON;" + cmd, test.db, rubric.sort])
           .catch(function (result) {
                  console.log('IC Err: ' + result);
                  throw new WorkerPoolError(result.message);
           })
           .timeout(rubric.timeout);
      tests.push({
        ...test,
        result: r.result,
        ...check(test.expectedHash, r.hash),
      });
    } catch (e) {
      if (test.ic) {
         // Integrity Constraints can have exceptions
         // Make CHECK constraint failed messages generic because
         // user may have named the constraint differently
         let message = e.message.startsWith('CHECK constraint failed:') ?
                           'CHECK constraint failed:' : e.message;
         tests.push({
           ...test,
           result: message,
           ...check(test.expectedHash, hash(message)),
         });
      } else {
         return { ...rubric, error: "Error "+e.message };
      }
    }
  }

  return { ...rubric, tests, ...checkTests(tests) };
}

function validateQuit() {
  if (pool) {
    pool.terminate();
  }
}

exports.validate = validate;
exports.validateQuit = validateQuit;
exports.validateSQL = validateSQL;

async function test() {
  console.log(
    await validate("A+B", {
      kind: "expression",
      tests: [{ context: { A: 3, B: 4 }, expectedHash: "320ca3f6" }],
    })
  );
  console.log(
    await validate("000deadbeef.0", {
      kind: "hex",
      expectedHash: "53fd34f5",
    })
  );
  /*
  console.log(validateExpression("A=A+B", { A: 3, B: 4 }));
  console.log(validateExpression("A=1;B=2;A+B", { A: 3, B: 4 }));
  console.log(validateExpression("A;A+B", { A: 3, B: 4 }));
  console.log(validateExpression("A ? B : A", { A: 3, B: 4 }));
  console.log(validateExpression("A.toString()", { A: 3, B: 4 }));
  console.log(validateExpression("log(1)", {}));
  */
}

/* test(); */
