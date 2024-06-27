const { validateSQL } = require("./validate.js");

window.addEventListener("load", () => {
  const Window = /** @type {any} */ (window);
  // get the rubric from the page
  const Rubrics = /** @type {import("./validate.js").Rubric}*/ (Window._rubrics);

  /** escape table entries
   * @param {string} s
   */
  function esc(s) {
    s = "" + s;
    return s.replace(/</g, "&lt;").replace(/>/g, "&gt;");
  }

  /** format a db result
   * @param {import("./sqlWorker.js").dbResult[]} data
   * @param {boolean} correct
   */
  function datatable(data, correct) {
    const tbl = document.createElement("table");
    tbl.className = "datatable";
    if (correct) {
      tbl.style.background = "palegreen";
    }
    const n = data.length;
    if (!n) {
      const empty = document.createTextNode("Empty");
      tbl.appendChild(empty);
      return tbl;
    }
    if (data instanceof Array === false) {
      const sql_exception = document.createTextNode(data);
      tbl.appendChild(sql_exception);
      return tbl;
    }

    const header_labels = data[n - 1].columns;
    for (let idx = 0; idx < header_labels.length; idx++) {
      const col = document.createElement("col");
      col.className = esc(header_labels[idx]);
      tbl.appendChild(col);
    }

    // create header row
    const thead = tbl.createTHead();
    const row = thead.insertRow(0);
    for (let idx = 0; idx < header_labels.length; idx++) {
      const cell = row.insertCell(idx);
      cell.innerHTML = esc(header_labels[idx]);
    }

    // fill table body
    const tbody = document.createElement("tbody");
    for (let row_idx in data[n - 1]["values"]) {
      const body_row = tbody.insertRow();
      for (let header_idx in header_labels) {
        const body_cell = body_row.insertCell();
        body_cell.appendChild(
          document.createTextNode(
            "" + data[n - 1]["values"][row_idx][header_idx]
          )
        );
      }
    }
    tbl.appendChild(tbody);
    return tbl;
  }
  /** validateSql - check an sql query
   * @param {Element} node
   */
  async function validateSqlNode(node) {
    const area = node.querySelector("textarea");
    const name = area.name;
    const rubric = Rubrics[name];
    if (!rubric || rubric.kind != "sql") {
      return;
    }
    const output = node.querySelector("div.sqloutput");
    // clear the output
    while (output != null && output.firstChild) {
      output.removeChild(output.firstChild);
    }
    const code = area.value.trim();
    if (!code) {
      return;
    }

    const resp = await validateSQL(code, rubric);
    if ("error" in resp) {
      const msg = document.createElement("div");
      msg.className = "sqlerror";
      msg.appendChild(document.createTextNode(resp.error));
      output.appendChild(msg);
      return;
    }
    for (const test of resp.tests) {
      const result = test.result;
      const table = datatable(result, test.correct);
      output.appendChild(table);
    }
  }
  document.addEventListener("click", (e) => {
    if (
      e.target instanceof HTMLButtonElement &&
      e.target.matches(".sql button") &&
      e.target.innerText == "Minimize Output"
    ) {
      const node = e.target.closest("fieldset.sql");
      Array.from(node.children).forEach(function(s_element) {
        if (s_element instanceof HTMLDivElement &&
            s_element.classList.contains('sqloutput')) {
           Array.from(s_element.children).forEach(function(t_element) {
             if (t_element instanceof HTMLTableElement) {
               // Hide everything but the table header and five rows
               for (var i=6; i<t_element.rows.length; i++) {
                  t_element.rows[i].hidden=true;
               }
             }
           });
        }
      });
    }
    if (
      e.target instanceof HTMLButtonElement &&
      e.target.matches(".sql button") &&
      e.target.innerText == "Execute"
    ) {
      const node = e.target.closest("fieldset.sql");
      validateSqlNode(node);
    }
  });
});
