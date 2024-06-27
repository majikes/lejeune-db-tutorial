const { validate } = require("./validate.js");

// include this to get sql support, commenting it out should be OK
require("./mysql.js");

window.addEventListener("load", () => {
  // I encode the baseURL on the body
  const baseURL = document.body.dataset.root;
  if (!baseURL) {
    return;
  }
  const Window = /** @type {any} */ (window);
  // get the rubric from the page
  const Rubrics = /** @type {Object.<string, import("./validate.js").Rubric>}*/ (Window._rubrics);

  // set the title
  const h1 = document.getElementsByTagName("h1")[0];
  if (h1) {
    document.title = h1.innerText;
  }

  // display the user id
  fetch(baseURL + "api/onyen")
    .then((resp) => resp.json())
    .then((data) => {
      const user = document.getElementById("onyen");
      if (onyen) {
        onyen.innerHTML = data.onyen;
      }
    });

  // enable the logout button if present
  const logout = document.getElementById("logout");
  if (logout) {
    logout.addEventListener("click", () => {
      const headers = new Headers({
        Aurhorization: "Basic " + window.btoa("nouser:nopass"),
      });
      document.cookie = "user=; Max-Age=-99999999;";
      fetch(baseURL + "logout", { headers, credentials: "include" }).then(
        () => {
          fetch(baseURL, { headers, credentials: "include" }).then(() => {
            location.reload();
          });
        }
      );
    });
  }

  const myform = document.getElementById("myform");
  if (!(myform instanceof HTMLFormElement)) {
    // bail out if we're not handling a form
    return;
  }
  const key = "mypoll-" + myform.dataset.key;

  // Add to copy
  myform.addEventListener("copy", (event) => {
    if (myform.dataset.key == 'fe-vaccination') {
        event.preventDefault(); // default behaviour is to copy any selected text
        return false;
    }
    if ( event == null || event.srcElement == null ||  event.srcElement.id == null ){
        return;
    }
    let value = document.getSelection().toString();
    if (value === '') {
      // Firefox has a 20-year-old bug where document.getSelection() doesn't
      // work on textareas. Firefox, I like you, but wow...
      // https://bugzilla.mozilla.org/show_bug.cgi?id=85686
      // Anyway, here's a fallback if that didn't work.
      const node = event.target;
      value = node.value.substring(node.selectionStart, node.selectionEnd)
    }
    value +=  myform.dataset.z;
    value = value.replace(/\n/g, myform.dataset.z + "\n");
    value = value.replace(/\u00A0\u00A0/g, myform.dataset.z + "\u00A0\u00A0");
    value = value.replace(/  /g, myform.dataset.z + "  ");
    // copy altered value instead of raw selection
    event.clipboardData.setData('text/plain', value);
    event.preventDefault(); // don't overwrite altered value with raw value
  });

  // Add to paste
  myform.addEventListener("paste", (event) => {
    if ((myform.dataset.key == 'worksheetxc') || (myform.dataset.key == 'm1-inception')) {
        event.preventDefault();
        return false;
    }
    if ( event == null || event.srcElement == null ||  event.srcElement.id == null ){
        return;
    }
    const node = event.target;
    const name = node.dataset.name || node.name;
    let pastedText = event.clipboardData.getData('text');
    pastedText = pastedText.replace(new RegExp(/[\u200B-\u200F]/, 'g'), '');
    event.clipboardData.setData('text/plain', pastedText);
    if (!(name in Rubrics)) return;  // static/codemirror/cm_run.js handles CodeMirror paste
    window.setTimeout(function() {
      postPasteCheck(node, pastedText);
    }, 0);
  });
 
  function postPasteCheck(node, pastedText) {
    const mine = myform.dataset.z;
    let any = new RegExp(/[\u200B-\u200F]/g, '');
    let position = node.selectionStart;
    if ( !any.exec(pastedText) ) {
       // no z's
       const fd = new FormData(myform);
      fd.set("_submit", "++ field='" + node.name +"' paste=:" + pastedText);
       fetch(myform.action, {
         method: "POST",
         body: fd,
       });
    }
    if (pastedText.endsWith(mine)) position -= mine.length;
    // FIXME: undo history is erased because we're assigning to node.value
    // From what I can tell, this is not trivial to fix.
    // See the commit message that added this line for more details.
    node.value = node.value.replace(new RegExp(mine, 'g'), '');
    node.setSelectionRange(position, position);
    if (any.exec(node.value)) {
       // found
       const fd = new FormData(myform);
       fd.set("_submit", "--- field='" + node.name + "' pasted:" + pastedText);
       fetch(myform.action, {
         method: "POST",
         body: fd,
       });
    }
    node.value = node.replace(/[\u200B-\u200F]/g, '').replace(/xA0/g, ' ');
  }

  // make Enter on inputs simulate a change event for ease of entry
  myform.addEventListener("keypress", (event) => {
    if (event.keyCode === 13 && event.target instanceof HTMLInputElement) {
      event.preventDefault();
      event.target.dispatchEvent(new Event("change", { bubbles: true }));
      return false;
    }
  });

  // setup autosave if requested
  if (myform.dataset.interval && myform.dataset.interval !== "0") {
    const interval = parseInt(myform.dataset.interval, 10);
    setInterval(() => {
      if (valuesChanged) {
        const fd = new FormData(myform);
        fd.set("_submit", "");
        fetch(myform.action, {
          method: "POST",
          body: fd,
        });
        valuesChanged = false;
      }
    }, interval * (60 * 1000));
  }

  // setup browser state if requested
  if (myform.dataset.focus === "1") {
    // append a hidden blur message to the body for use later
    const blurmsg = document.createElement("div");
    blurmsg.id = "blur";
    blurmsg.innerHTML = "You must not leave the window";
    document.body.appendChild(blurmsg);
    // get the url of the focus report
    const url = baseURL + "browser/";
    // note if we're leaving the page because of submit
    let isSubmit = false;
    myform.addEventListener("submit", () => (isSubmit = true));
    // handle focus related events
    /** @param {Event} e */
    function fb(e) {
      // prevent leaving the page by accident
      if (!isSubmit && e.type === "beforeunload") {
        e.preventDefault();
        e.returnValue = true;
      }
      // let the backend know of the focus change
      fetch(url + e.type, { method: "POST" });
      document
        .getElementsByTagName("body")[0]
        .classList.toggle("blur", e.type === "blur");
      if (valuesChanged) {
         const fd = new FormData(myform);
         fd.set("_submit", "focus");
         fetch(myform.action, {
            method: "POST",
            body: fd,
         });
         valuesChanged = false;
      }
    }
    window.addEventListener("blur", fb);
    window.addEventListener("focus", fb);
    window.addEventListener("beforeunload", fb);
    // disable some keys so they don't lose focus
    window.addEventListener("keydown", (event) => {
      const ctrl = event.ctrlKey || event.metaKey;
      if (
        (ctrl && event.shiftKey && event.code === "KeyI") || // C-S-I
        event.key.match(/F\d+/)
      ) {
        // Function keys
        event.preventDefault();
      }
    });

    const fsbutton = document.getElementById("fullscreen");
    if (fsbutton) {
      window.addEventListener("resize", () => {
        // check for fullscreen
        if (
          Math.abs(outerWidth / innerWidth - outerHeight / innerHeight) < 0.05
        ) {
          fsbutton.style.display = "none";
          fetch(url + "fullscreen", { method: "POST" });
        } else {
          fsbutton.style.display = "block";
          fetch(url + "partscreen", { method: "POST" });
        }
      });
      fsbutton.addEventListener("click", () => {
        document.documentElement.requestFullscreen();
      });
    }
  }

  // setup timer if requested
  const elapsed = document.getElementById("elapsed");
  if (elapsed instanceof HTMLInputElement) {
    const skey = key + "-elapsed-start";
    const start = localStorage[skey] || Date.now();
    localStorage[skey] = start.toString();
    setInterval(() => {
      const now = Date.now();
      let interval = now - start;
      interval = Math.floor(interval / 1000);
      const seconds = Math.floor((now - start) / 1000);
      const minutes = Math.floor(seconds / 60);
      const s = minutes + ":" + (seconds % 60).toString().padStart(2, "0");
      elapsed.value = s;
    }, 1000);
  }

  // include a field indicating which problems were displayed as correct
  const checkNode = document.querySelector("input[name='_check']");
  /** correct
   * @param {HTMLElement} node
   * @param {boolean} condition
   */
  function correct(node, condition) {
    node.dataset.correct = condition ? "1" : "0";
    // If this is a CodeMirror node, set the corresponding textarea's correct value from the validation
    if (node.hasAttribute('codeMirrorNumber')) {
       let codeMirrorNumber = parseInt(node.getAttribute('codeMirrorNumber'))
       document.getElementsByClassName('CodeMirror')[codeMirrorNumber].dataset.correct = node.dataset.correct;
    }
    if (checkNode instanceof HTMLInputElement) {
      checkNode.value = Array.from(document.querySelectorAll("[data-correct]"))
        .map((/** @type {HTMLElement}*/ n) => n.dataset.correct)
        .join("");
    }
  }

  // check inputs against supplied answers
  myform.addEventListener("change", async (e) => {
    if (!(e.target instanceof HTMLInputElement)) return;
    if (e.target.type == "checkbox") return;
    const node = e.target;
    const name = node.name;
    if (name in Rubrics) {
      const rubric = Rubrics[name];
      // these are handled on button click
      if (rubric.kind == "sql") return;

      const resp = await validate(node.value, rubric);
      // BEGIN CODE CHANGED BY rslutz
      let msg = node.nextSibling;
      if (typeof msg.CodeMirror !== 'undefined') {
          msg = node.nextSibling.nextSibling;  // unless next sibling is CodeMirror
      }
      // const msg = node.nextSibling;
      // END CODE CHANGED BY rslutz
      if (msg instanceof HTMLSpanElement) {
        msg.innerText = "";
        if ("error" in resp) {
          msg.innerText = resp.error;
        } else if (!resp.correct && (resp.hasOwnProperty('partial_credit') && resp.partial_credit)) {
          const number_correct = resp.tests.filter((obj) => obj.correct == true).length;
          if (number_correct) {
            const number_tests = resp.tests.length;
            msg.innerText = 'Partially correct. ' + number_correct + ' of ' + number_tests + ' correct.\r';
          }   
        }  
        if (name.startsWith('_calculator') && !resp.correct) {
          // This is a calculator
          msg.innerText = resp.tests[0].result;
        }   
      }
      correct(node, resp.correct);
    }
  });

  // validate truth tables and such
  /** @param {HTMLTableElement} node */
  async function validateTable(node) {
    const name = node.dataset.name;
    if (name in Rubrics) {
      const rubric = Rubrics[name];
      const value = Array.from(node.querySelectorAll("select"))
        .map((e) => e.value)
        .join("-");
      const save_node = document.getElementsByName(name)[0];
      if (save_node instanceof HTMLInputElement) {
        save_node.value = value;
      }
      const resp = await validate(value, rubric);
      correct(node, resp.correct);
    }
  }
  myform.addEventListener("change", (e) => {
    if (e.target instanceof HTMLSelectElement) {
      const node = e.target.closest("table");
      if (node) {
        validateTable(node);
      }
    }
  });

  let preview = document.getElementById("preview");
  if (preview instanceof HTMLInputElement && preview.type == "file") {
    preview.addEventListener("change", (e) => {
      console.log("preview change");
      if (e.target instanceof HTMLInputElement && e.target.files[0]) {
        console.log("preview file");
        let form = document.getElementById("myform");
        if (form instanceof HTMLFormElement) {
          console.log("preview submit");
          form.submit();
        }
      }
    });
  }

  // save all values when any change
  let valuesChanged = false;
  myform.addEventListener("change", () => {
    valuesChanged = true;
    const v = {};
    for (const e of Array.from(myform.elements)) {
      const f = /** @type {HTMLFormElement}*/ (e);
      if (f.name) {
        v[f.name] =
          ["checkbox", "radio"].indexOf(f.type) >= 0 ? +f.checked : f.value;
      }
    }
    localStorage[key] = JSON.stringify(v);
  });

  // restore values on load
  const values = JSON.parse(localStorage[key] || "{}");
  for (const e of Array.from(myform.elements)) {
    const f = /** @type {HTMLFormElement}*/ (e);
    if (f.name && f.name in values && !f.readOnly && f.type != "file") {
      if (["checkbox", "radio"].indexOf(f.type) >= 0) {
        f.checked = values[f.name] === 1;
      } else {
        f.value = values[f.name];
      }
      f.dispatchEvent(new Event("change", { bubbles: true }));
    }
  }

  // render equations
  for (const m of /** @type {HTMLElement[]}*/ (Array.from(
    document.getElementsByClassName("math")
  ))) {
    // @ts-ignore
    katex.render(m.innerText, m);
  }
});
