importScripts("pyodide.js");


async function initialisePyodide() {
  self.pyodide = await loadPyodide({
    homedir: "/",
    indexURL: "",
  });
}

let pyodideReadyPromise = initialisePyodide();

function generateResponseObject(pythonResponse) {
  const responseBytes = pythonResponse.get_data((as_text = false)).toJs();
  const decoder = new TextDecoder("utf-8", {fatal: true});
  let responseBody
  if (responseBytes) {
    try {
      responseBody = decoder.decode(responseBytes);
    } catch (_) {
      responseBody = responseBytes;
    }
  }
  const headerKeys = pythonResponse.headers.keys();
  const responseStatus = pythonResponse.status_code;
  const returnObject = {
    response: responseBody || null,
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

async function handlePythonCode(python) {
  console.debug(`wasm: handlePythonCode(...)`);

  // Load any imports
  await self.pyodide.loadPackagesFromImports(python, postConsoleMessage, postConsoleMessage);

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

  const { python, ...context } = event.data;

  console.debug("wasm: onmessage");

  // The worker copies the context in its own "memory" (an object mapping name to values)
  for (const key of Object.keys(context)) {
    self[key] = context[key];
  }
  handlePythonCode(python);
};

/**
 * Message post functions.
 */

function postMessageRegular(object) {
  console.debug("wasm: postMessageRegular");

  self.postMessage({
    results: object,
  });
}

function postMessageTransferable(object, transferable) {
  console.debug("wasm: postMessageTransferable");

  self.postMessage(
    {
      results: object,
    },
    transferable
  );
}

function postMessageError(error) {
  console.debug("wasm: postMessageError");

  self.postMessage({
    error: error.message,
  });
}

function postConsoleMessage(consoleMessage) {
  console.debug("wasm: postConsoleMessage");

  self.postMessage({
    consoleMessage,
  });
}
