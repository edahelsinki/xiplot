/**
 * Based on Itay Dafna's https://github.com/ibdafna/webdash/releases/tag/0.0.3
 *
 * BSD 3-Clause License
 *
 * Copyright (c) 2021, Bloomberg LP
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 *
 * 1. Redistributions of source code must retain the above copyright notice, this
 *    list of conditions and the following disclaimer.
 *
 * 2. Redistributions in binary form must reproduce the above copyright notice,
 *    this list of conditions and the following disclaimer in the documentation
 *    and/or other materials provided with the distribution.
 *
 * 3. Neither the name of the copyright holder nor the names of its
 *    contributors may be used to endorse or promote products derived from
 *    this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
 * AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
 * DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
 * FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
 * DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
 * SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
 * CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
 * OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
 * OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */

importScripts("https://cdn.jsdelivr.net/pyodide/v0.24.0/full/pyodide.js");

/**
 * Handler receiving message events from the WorkerManager.
 *
 * @param event the message
 */
onmessage = async (event: MessageEvent) => {
  const { uuid, python, ...context } = event.data;

  try {
    const pyodide = await maybe_pyodide;

    const python_code: string = python;

    // The worker copies the context in its own "memory" (an object mapping name to values)
    for (const key of Object.keys(context)) {
      self[key] = context[key];
    }

    // Load imported packages into the Pyodide interpreter
    await pyodide.loadPackagesFromImports(
      python_code,
      { messageCallback: postConsoleMessage, errorCallback: postConsoleError }
    );

    let result;

    while (true) {
      try {
        // Execute the Python code
        result = await pyodide.runPython(python_code);
        break;
      } catch (error) {
        // Check if an import error occurred, if so get the package name
        const package: string = await pyodide.runPython(
          "import sys; None if not isinstance(sys.last_value, ImportError) else sys.last_value.name"
        );

        // Re-throw non-import errors
        if (!package) {
          throw error;
        }

        await pyodide.loadPackage(
          package,
          { messageCallback: postConsoleMessage, errorCallback: postConsoleError }
        );
      }
    }

    // Check if the result is a PyProxy, if so convert it into a response object
    if (result instanceof pyodide.ffi.PyProxy) {
      result = responseObjectFromPython(result);
    }

    postResponseMessage(uuid, result);
  } catch (error) {
    postErrorMessage(uuid, error.message);
  }
};

/**
 * The global Pyodide interpreter interface.
 */
const maybe_pyodide: Promise<PyodideInterface> = loadPyodide({
  fullStdLib: false,
  stdout: postConsoleMessage,
  stderr: postConsoleError,
});

/**
 * Transforms a `PyProxy` response from Flask into an object
 * containing the response headers, body, and status code.
 *
 * @param python_response the `PyProxy` response
 *
 * @returns the response object
 */
function responseObjectFromPython(python_response: PyProxy): {
  response: string | Uint8Array | null;
  status: number;
  headers: { [key: string]: string };
} {
  let as_text;
  const js_response = python_response.get_data((as_text = false)).toJs();

  const decoder = new TextDecoder("utf-8", { fatal: true });

  // Attempt to decode the message as a string, otherwise leave it as is
  let response: string | Uint8Array | null = null;
  if (js_response) {
    try {
      response = decoder.decode(js_response);
    } catch (_) {
      response = js_response;
    }
  }
  // Empty responses, e.g. for 204, must be null
  response = response || null;

  const status: number = python_response.status_code;

  const header_keys: PyProxy & Iterable<string> =
    python_response.headers.keys();
  const headers = Array.from(header_keys).reduce(
    (acc: object, val: string) => (
      (acc[val] = python_response.headers.get(val)), acc
    ),
    {}
  );

  // Clean up the PyProxy objects to avoid a memory leak
  header_keys.destroy();
  python_response.destroy();

  return {
    response,
    status,
    headers,
  };
}

/**
 * Post a response message to the WorkerManager.
 *
 * @param results the response
 */
function postResponseMessage(uuid: string, results: any) {
  self.postMessage({
    uuid,
    results,
  });
}

/**
 * Post an error message to the WorkerManager.
 *
 * @param error the error message
 */
function postErrorMessage(uuid: string, error: any) {
  self.postMessage({
    uuid,
    error,
  });
}

/**
 * Post a message to `console.log`
 *
 * @param consoleMessage the string message
 */
function postConsoleMessage(consoleMessage: string) {
  self.postMessage({
    consoleMessage,
  });
}

/**
 * Post a message to `console.error`
 *
 * @param consoleError the string error message
 */
function postConsoleError(consoleError: string) {
  self.postMessage({
    consoleError,
  });
}

/*
 * Reduced minimal type declarations for Pyodide.
 *
 * Extracted from pyodide.d.ts in
 * https://github.com/pyodide/pyodide/releases/tag/0.21.0a3
 */

declare function loadPyodide(options?: {
  indexURL?: string;
  fullStdLib?: boolean;
  stdout?: (msg: string) => void;
  stderr?: (msg: string) => void;
}): Promise<PyodideInterface>;

declare type PyodideInterface = {
  loadPackagesFromImports: (
    code: string,
    options: {
      messageCallback?: (message: string) => void;
      errorCallback?: (message: string) => void;
      checkIntegrity?: boolean;
    },
    errorCallbackDeprecated?: (message: string) => void
  ) => Promise<void>;
  loadPackage: (
    name: string,
    options: {
      messageCallback?: (message: string) => void;
      errorCallback?: (message: string) => void;
      checkIntegrity?: boolean;
    },
    errorCallbackDeprecated?: (message: string) => void
  ) => Promise<void>;
  runPython: (code: string) => any;
  runPythonAsync: (code: string) => Promise<any>;
  ffi: { PyProxy: any };
};

declare type PyProxy = PyProxyClass & {
  [x: string]: any;
};

declare class PyProxyClass {
  destroy(): void;
  toJs(): any;
}
