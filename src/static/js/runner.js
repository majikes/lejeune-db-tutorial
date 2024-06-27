const { validate, validateQuit } = require("./validate.js");
const fs = require("fs");

async function main() {
  var input = fs.readFileSync(process.argv[2]).toString();
  var { answers, rubrics } = JSON.parse(input);
  let outputs = {};
  for (const tag of Object.keys(rubrics)) {
    try {
      outputs[tag] = await validate(answers[tag], rubrics[tag]);
    } catch (e) {
      console.error("error", tag, answers[tag], e.message);
    }
  }
  var outputJSON = JSON.stringify(outputs, null, "    ");
  fs.writeFileSync(process.argv[3], outputJSON);
  validateQuit();
}

main();
