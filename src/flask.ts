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

import { WorkerManager } from "./worker-loader";
import { log } from "./webdash";

/**
 * A small, virtual web server wrapping the Flask server in Pyodide.
 *
 * It intercepts `fetch` requests and reroutes the ones targeted at
 * the dash app to Pyodide, while letting others pass through.
 */
export class WebFlask {
  worker: WorkerManager;
  originalFetch: (request: any, response: any) => Promise<Response>;

  constructor(workerManager) {
    this.worker = workerManager;

    this.originalFetch = window.fetch;
    window.fetch = this.fetch.bind(this);
  }

  /**
   * Generates the stringified Python code to be run in Pyodide
   * to perform a request on the Flask server backend.
   *
   * Note: assumes request payload is either `null` or `json`.
   *
   * @param req Request Object
   * @param init request payload
   *
   * @returs stringified Python code
   */
  generateRequestPythonCode(req, init) {
    let data;
    if (init && init.body) {
      data = `r"""${init.body}"""`;
    } else {
      data = "None";
    }

    let content_type;
    if (init && init.body) {
      content_type = `"application/json"`;
    } else {
      content_type = "None";
    }

    return `
    with app.server.app_context():
      with app.server.test_client() as client:
        response = client.open('${req}',
          data=${data},
          content_type=${content_type},
          method="${(init && init.method) || "GET"}",
        )
    response`;
  }

  /**
   * Executes the given stringified Python code in Pyodide
   * against the Flask server backend and converts the
   * response to a an equivalent `Response` object.
   *
   * @param requestPythonCode stringified Python code
   *
   * @returns JavaScript `Response` object
   */
  async executeFlaskRequest(requestPythonCode): Promise<Response> {
    log("[2. Flask Request Generated]");

    const flaskResponse = await this.worker.executeWithAnyResponse(requestPythonCode, {});

    log("[4. Flask Response Received]");

    const options = {};
    if (flaskResponse["headers"]) {
      options["headers"] = flaskResponse["headers"];
    }
    if (flaskResponse["status"]) {
      options["status"] = flaskResponse["status"];
    }

    return new Response(flaskResponse["response"], options);
  }

  /**
   * A custom `fetch` function which intercepts requests to
   * the Flask server running the dash app, reroutes them to
   * the wasm-side Flask server in Pyodide, and then converts
   * the response to a JavaScript `Response`.
   *
   * Requests going to a different origin or route are passed
   * through to the native `window.fetch` implementation.
   *
   * @param req JavaScript `Request` object
   * @param init JavaScript `RequestInit` payload
   *
   * @returns JavaScript `Response` object
   */
  async fetch(
    req: Request,
    init?: RequestInit | null | undefined
  ): Promise<Response> {
    const url = new URL(new Request(req).url);

    log(`[1. Request ${url.pathname} intercepted]`);

    // Extract the route of the current window.location
    const windowLocationRoute = window.location.href.replace(
      /\/(?:[^\/]+?\.[^\/]*?|index)$/,
      "/"
    );

    if (url.href.startsWith(windowLocationRoute)) {
      const response = await this.executeFlaskRequest(
        this.generateRequestPythonCode(req, init)
      );

      log(`[5. Request ${url.pathname} done]`);

      return response;
    } else {
      log(`[2. Request ${url.pathname} passthrough]`);

      return this.originalFetch.apply(window, [req, init]);
    }
  }
}
