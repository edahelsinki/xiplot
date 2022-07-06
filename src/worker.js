importScripts("pyodide.js");


async function loadPyodideAndPackages() {
  self.pyodide = await loadPyodide({
    homedir: "/",
    indexURL: "",
  });
  await self.pyodide.loadPackage(["pandas", "numpy", "dash", "dash-uploader", "plotly", "sklearn", "matplotlib", "dashapp-0.1.0-py3-none-any.whl"], postConsoleMessage, postConsoleMessage);

  self.pyodide.FS.mkdir("data");

  for (const dataset of [
    "autompg-B.csv", "autompg.csv", "auto-mpg.data",
    "Wang-B.csv", "Wang-dataframe.csv",
  ]) {
    self.pyodide.FS.createLazyFile("data", dataset, "data/" + dataset, true, false);
  }
}

let pyodideReadyPromise = loadPyodideAndPackages();

function fileSystemCall(msgType, param) {
  console.log("fileSystemCall()", msgType, param);
  const output = pyodide._module.FS[msgType](param);
  return output;
}

function generateResponseObject(pythonResponse) {
  const responseBody = pythonResponse.get_data((as_text = true)) || null;
  const headerKeys = pythonResponse.headers.keys();
  const responseStatus = pythonResponse.status_code;
  const returnObject = {
    response: responseBody,
    status: responseStatus,
    headers: Array.from(headerKeys).reduce(
      (acc, val) => ((acc[val] = pythonResponse.headers.get(val)), acc),
      {}
    ),
  };

  // Clean up Proxy Object so we don't leak memory
  headerKeys.destroy();
  pythonResponse.destroy();

  return returnObject;
}

function handleFsCommands(fsCommands) {
  const { msgType, param } = fsCommands;
  try {
    const result = fileSystemCall(msgType, param);
    msgType === "readFile"
      ? postMessageTransferable(result, [result.buffer])
      : postMessageRegular(result);
  } catch (error) {
    postMessageRegular(error);
  }
}

async function handlePythonCode(python) {
  // Load any imports
  await self.pyodide.loadPackagesFromImports(python, console.log, console.err);

  let result = await self.pyodide.runPython(python);

  // Processing Proxy objects before sending.
  if (pyodide.isPyProxy(result)) {
    result = generateResponseObject(result);
  }

  try {
    postMessageRegular(result);
  } catch (error) {
    postMessageError(error);
  }
}

onmessage = async (event) => {
  // Making sure we don't arrive early at the party.
  await pyodideReadyPromise;

  const { python, fsCommands, ...context } = event.data;

  // Uncomment for debugging pureposes
  console.log("[3. Worker onmessage]");

  if (fsCommands) {
    handleFsCommands(fsCommands);
  } else {
    // The worker copies the context in its own "memory" (an object mapping name to values)
    for (const key of Object.keys(context)) {
      self[key] = context[key];
    }
    handlePythonCode(python);
  }
};

/**
 * Message post functions.
 */

function postMessageRegular(object) {
  console.log("postMessageRegular");
  self.postMessage({
    results: object,
  });
}

function postMessageTransferable(object, transferable) {
  self.postMessage(
    {
      results: object,
    },
    transferable
  );
}

function postMessageError(error) {
  self.postMessage({
    error: error.message,
  });
}

function postConsoleMessage(consoleMessage) {
  self.postMessage({
    consoleMessage,
  });
}