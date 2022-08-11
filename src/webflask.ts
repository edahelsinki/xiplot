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

import { dedent } from "ts-dedent";

import { WorkerManager } from "./manager";
import { log } from "./webdash";

/**
* A small, virtual web server wrapping the Flask server in Pyodide.
*
* It intercepts `fetch` requests and reroutes the ones targeted at
* the dash app to Pyodide, while letting others pass through.
*/
export class WebFlask {
  private worker: WorkerManager;
  private original_fetch: (
    input: URL | RequestInfo,
    init?: RequestInit | undefined
  ) => Promise<Response>;

  public constructor(workerManager) {
    this.worker = workerManager;

    this.original_fetch = window.fetch;
    window.fetch = this.fetch.bind(this);
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
  * @param info `URL` or `string` or `Request` object
  * @param init optionally `RequestInit`
  *
  * @returns JavaScript `Response` object
  */
  public async fetch(
    info: URL | RequestInfo,
    init?: RequestInit | undefined
  ): Promise<Response> {
    const url = new URL(new Request(info).url);

    log(`[1. Request ${url.pathname} intercepted]`);

    // Extract the route of the current window.location
    const window_location_route = window.location.href.replace(
      /\/(?:[^\/]+?\.[^\/]*?|index)$/,
      "/"
    );

    if (url.href.startsWith(window_location_route)) {
      const response = await this.webflaskFetch(info, init);

      log(`[5. Request ${url.pathname} done]`);

      return response;
    } else {
      log(`[2. Request ${url.pathname} passthrough]`);

      return this.nativeFetch(info, init);
    }
  }

  /**
  * A custom `fetch` function which reroutes requests to
  * the wasm-side Flask server in Pyodide, and then converts
  * the response to a JavaScript `Response`.
  *
  * @param info `URL` or `string` or `Request` object
  * @param init optionally `RequestInit`
  *
  * @returns JavaScript `Response` object
  */
  public async webflaskFetch(
    info: URL | RequestInfo,
    init?: RequestInit | undefined
  ): Promise<Response> {
    return await this.executeFlaskRequest(
      this.generateRequestPythonCode(info, init)
    );
  }

  /**
  * A custom `fetch` function which passes the request
  * through to the native `window.fetch` implementation.
  *
  * @param info `URL` or `string` or `Request` object
  * @param init optionally `RequestInit`
  *
  * @returns JavaScript `Response` object
  */
  public async nativeFetch(
    info: URL | RequestInfo,
    init?: RequestInit | undefined
  ): Promise<Response> {
    return this.original_fetch.apply(window, [info, init]);
  }

  /**
  * Executes the given stringified Python code in Pyodide
  * against the Flask server backend and converts the
  * response to a an equivalent `Response` object.
  *
  * @param request_python_code stringified Python code
  *
  * @returns JavaScript `Response` object
  */
  private async executeFlaskRequest(
    request_python_code: string
  ): Promise<Response> {
    log("[2. Flask Request Generated]");

    const flask_response = await this.worker.executeWithAnyResponse(
      request_python_code,
      {}
    );

    log("[4. Flask Response Received]");

    const options = {};
    if (flask_response["headers"]) {
      options["headers"] = flask_response["headers"];
    }
    if (flask_response["status"]) {
      options["status"] = flask_response["status"];
    }

    return new Response(flask_response["response"], options);
  }

  /**
  * Generates the stringified Python code to be run in Pyodide
  * to perform a request on the Flask server backend.
  *
  * Note: assumes request payload is either `null` or `json`.
  *
  * @param info `URL` or `string` or `Request` object
  * @param init optionally `RequestInit`
  *
  * @returs stringified Python code
  */
  private generateRequestPythonCode(
    info: URL | RequestInfo,
    init?: RequestInit | undefined
  ): string {
    let data = "None";
    if (init && init.body) {
      data = `r"""${init.body}"""`;
    }

    let content_type = "None";
    if (init && init.body) {
      content_type = `"application/json"`;
    }

    let method = "GET";
    if (init && init.method) {
      method = init.method;
    }

    return dedent`
      with app.server.app_context():
        with app.server.test_client() as client:
          response = client.open('${info}',
            data=${data},
            content_type=${content_type},
            method="${method}",
          )
      if response.status_code == 424:
        __import__(response.get_data(as_text=True))
      response
    `;
  }
}
 