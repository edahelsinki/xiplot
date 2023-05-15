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

import { v4 as uuidv4 } from "uuid";

import { log } from "./webdash";

/**
 * The WorkerManager manages the interaction between the WebFlask and WebDash
 * frontend and the Pyodide web worker backend.
 *
 * It exposes an async interface and provides message passing and error handling.
 */
export class WorkerManager {
  private callbacks: Map<string, Callback>;
  private worker: Worker;

  /**
   * Initialises the Pyodide interpreter inside a web worker.
   */
  public constructor() {
    this.callbacks = new Map();

    this.worker = new Worker("./worker.ts");
    this.worker.onmessage = this.processMessage.bind(this);
    this.worker.onerror = (error) =>
      console.error("INTERNAL WORKER ERROR", error);
  }

  /**
   * Executes the given Python code in the Pyodide interpreter
   * inside a web worker.
   *
   * Returns an untyped response.
   *
   * @param python_code stringified python code to run
   * @param context optional additional arguments
   * @returns any response type
   */
  public async executeWithAnyResponse(
    python_code: string,
    context: Payload
  ): Promise<any> {
    return await new Promise(
      (on_success: Function, on_error: Function) => {
        this.execute(python_code, context, on_success, on_error);
      }
    );
  }

  /**
   * Executes the given Python code in the Pyodide interpreter
   * inside a web worker.
   *
   * Returns a `string` response or throws a `TypeError`.
   *
   * @param python_code stringified python code to run
   * @param context optional additional arguments
   *
   * @returns string response
   */
  public async executeWithStringResponse(
    python_code: string,
    context: Payload
  ): Promise<string> {
    const result: any = await this.executeWithAnyResponse(python_code, context);

    if (result as string) {
      return result as string;
    }

    throw TypeError("Unexpected WebFlask response type, expected string");
  }

  /**
   * Executes the given Python code in the Pyodide interpreter
   * inside a web worker.
   *
   * @param python_code stringified python code to run
   * @param context optional additional arguments
   *
   * @param on_success callback function that is run on success.
   * @param on_error callback function that is run in case of failure.
   */
  private execute(
    python_code: string,
    context: Payload,
    on_success: Function,
    on_error: Function
  ) {
    const uuid = uuidv4();

    this.callbacks.set(uuid, { on_success, on_error });

    this.worker.postMessage({
      ...context,
      uuid,
      python: python_code,
    });
  }

  /**
   * Process console, results, and error messages from the Pyodide worker.
   *
   * @param event Message object
   */
  private processMessage(event: MessageEvent) {
    log("[4. Message received from worker]");

    // Forward console messages to the status tracker or `console.log`
    if (event.data.consoleMessage) {
      if (event.data.consoleMessage.startsWith("pyodide-eval:")) {
        try {
          eval(event.data.consoleMessage.slice("pyodide-eval:".length))
        } catch (error) {
          console.error(error);
        }

        return;
      }

      const statusBar = document.querySelector(".status");

      if (statusBar) {
        const message = document.createElement("div");
        message.className = "stdout";
        message.innerText = event.data.consoleMessage;

        statusBar.appendChild(message);
      } else {
        console.log(event.data.consoleMessage);
      }

      return;
    }

    // Forward error messages to the error tracker or `console.error`
    if (event.data.consoleError) {
      const statusBar = document.querySelector(".status");

      if (statusBar) {
        const error = document.createElement("div");
        error.className = "stderr";
        error.innerText = event.data.consoleError;

        statusBar.appendChild(error);
      } else {
        console.error(event.data.consoleError);
      }

      return;
    }

    const callback = this.callbacks.get(event.data.uuid);

    // Unpaired responses are unexpected
    if (!callback) {
      return console.error("UNPAIRED WORKER MESSAGE", event);
    }

    this.callbacks.delete(event.data.uuid);

    // Resolve the callback with the results or the error
    if (event.data.error) {
      console.error("WORKER ERROR CALLBACK", event.data.error);

      return callback.on_error(event.data.error);
    } else {
      return callback.on_success(event.data.results);
    }
  }
}

type Payload = { [key: string]: any };

type Callback = {
  on_success: Function;
  on_error: Function;
};
