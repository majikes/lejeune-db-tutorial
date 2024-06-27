var CM_arr;  // Code added by rslutz

function cm_run() {
    let textareas = document.getElementsByClassName('sqlcode');
    CM_arr = new Array(textareas.length);
    for (let i=0; i<textareas.length; i++) {
        let codemirror = CodeMirror.fromTextArea(textareas[i], {value: textareas[i].value, tabSize: 2, indentUnit: 2, smartIndent: true, mode:"sql", autoCloseBrackets: true, placeholder: "Your code goes here", attributes: {name: textareas[i].getAttribute('name')}});
        textareas[i].setAttribute("codeMirrorNumber", i);
        document.getElementsByClassName('CodeMirror')[i].dataset.correct = textareas[i].dataset.correct;
        CM_arr[i] = codemirror;
        codemirror.on('inputRead', (cm, event) => {
          if (event.origin == "paste") {
             let removeMineRegEx = new RegExp(myform.dataset.z, 'g');
             let any = new RegExp(/[\u200B-\u200F]/, 'g');
             const nodeName = cm.options.attributes.name;
             const lineNum = event.from.line;
             const chNum = event.from.ch;
             const targetNode = document.getElementsByName(nodeName)[0];

             event.text.forEach((text, i) => {
                 if ((myform.dataset.focus === "1") && !any.exec(text)) {
                     // no unicode focus
                     const fd = new FormData(myform);
                     fd.set("_submit", "no_unicode");
                     fd.set("_paste_text", text);
                     fd.set("_nodeName", nodeName);
                     fetch(myform.action, {
                       method: "POST",
                       body: fd,
                     });
                 }
                 let textWithoutZWSP = text.replaceAll(removeMineRegEx, '');
                 if (any.exec(textWithoutZWSP)) {
                     const fd = new FormData(myform);
                     fd.set("_submit", "--- field='" + nodeName + "' pasted:" + textWithoutZWSP);
                     fetch(myform.action, {
                       method: "POST",
                       body: fd,
                     });
                 };
                 textWithoutZWSP = textWithoutZWSP.
                                      replace(/[\u200B-\u200F]/g, '').
                                      replace(/\xA0/g, " ");  // CodeMirror uses 0xA0 which kills SQL-wasm
               
                 if (i == 0) {
                    cm.replaceRange(textWithoutZWSP, {line: lineNum, ch: chNum},
                                                     {line: lineNum, ch: chNum + text.length});
                 } else {
                    cm.replaceRange(textWithoutZWSP, {line: lineNum + i, ch: 0},
                                                     {line: lineNum + i, ch: text.length});
                 }
             });

             cm.save()
             cm.refresh();
             targetNode.value = cm.getValue();
          }
        });
        codemirror.on("blur", function(cm) {
            document.getElementsByName(cm.options.attributes.name)[0].value = cm.getValue();
            document.getElementsByName(cm.options.attributes.name)[0].dispatchEvent(new Event("change", { bubbles: true}));
        });
    }
}  // code added by rslutz
