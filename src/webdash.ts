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

import { WebFlask } from "./webflask";
import { WorkerManager } from "./manager";

declare global {
  export interface Window {
    web_dash: WebDash;
  }
}

const dev = process.env.NODE_ENV === "development";

/**
* Log function that swallows messages in production
* and forwards them to `console.log` in development.
*
* @param args arguments for `console.log`
*/
export function log(...args) {
  if (dev) {
    console.log(...args);
  }
}

/**
* The entry point for WebDash.
*
* It initialises the virtual Flask server running
* inside Pyodide, bootstraps the Dash app and its
* renderer, and coordinates communication between
* the Dash frontend and the Flask server backend.
*/
class WebDash {
  private worker_manager: WorkerManager;
  private web_flask: WebFlask;

  /**
  * Initialises and bootstraps WebDash.
  */
  public constructor() {
    this.worker_manager = new WorkerManager();
    this.web_flask = new WebFlask(this.worker_manager);

    this.bootstrap();
  }

  private async bootstrap() {
    await this.initialiseDashApp();

    await this.injectDashHeaders(document.head);
    await this.injectDashReactEntryPoint(document.body);

    const footer = await this.injectDashAppConfig(document.body);

    await this.injectDashScripts(footer);
    await this.injectDashRenderer(footer);
  }

  private async initialiseDashApp() {
    log("Initialising and bootstrapping the dash app");

    const bootstrap_python: string = await this.web_flask
      .nativeFetch("bootstrap.py")
      .then((response) => response.text());
    const url_base_pathname: string = window.location.pathname.replace(
      /\/(?:[^\/]+?\.[^\/]*?|index)$/,
      "/"
    );

    await this.worker_manager.executeWithAnyResponse(
      dedent`
        ${bootstrap_python}

        # Initialise and bootstrap the dash app
        app = bootstrap_dash_app("${url_base_pathname}")
      `,
      {}
    );
  }

  private async injectDashHeaders(head: HTMLElement) {
    log("Patching in dash's head tag");

    const meta_tags = await this.worker_manager.executeWithStringResponse(
      "app._generate_meta_html()",
      {}
    );

    const title = await this.worker_manager.executeWithStringResponse(
      "app.title",
      {}
    );
    const title_tag = `<title>${title}</title>`;

    const favicon = await this.worker_manager.executeWithStringResponse(
      "app.get_asset_url(app._favicon)",
      {}
    );
    const favicon_tag = `<link rel="icon" type="image/x-icon" href="${favicon}">`;

    const script_tags_timed =
      await this.worker_manager.executeWithStringResponse(
        "app._generate_css_dist_html()",
        {}
      );
    // Remove dash-generated ?m=<timestamp> fingerprints from href
    const script_tags = script_tags_timed.replace(
      /href="(?<href>[^"?]+?)(?:\?[^"]*)?"/g,
      'href="$1"'
    );

    head.innerHTML = `${meta_tags}\n${title_tag}\n${favicon_tag}\n${script_tags}`;
  }

  private async injectDashReactEntryPoint(body: HTMLElement) {
    log("Patching in dash's body tag with the react entry point");

    const react_entry_point =
      await this.worker_manager.executeWithStringResponse(
        "dash.dash._app_entry",
        {}
      );

    body.innerHTML = react_entry_point;
  }

  private async injectDashAppConfig(body: HTMLElement): Promise<HTMLElement> {
    log("Injecting the footer tag with the initial config of the dash app");

    const app_config = await this.worker_manager.executeWithStringResponse(
      "app._generate_config_html()",
      {}
    );

    const footer = document.createElement("footer");
    footer.innerHTML = app_config;

    body.appendChild(footer);

    return footer;
  }

  private async injectDashScripts(footer: HTMLElement) {
    log("Injecting the dash script tags");

    const script_tags = await this.worker_manager.executeWithStringResponse(
      "app._generate_scripts_html()",
      {}
    );

    for (const script of script_tags.split("</script>")) {
      // Remove dash-generated ?m=<timestamp> fingerprints from src
      const src = script.match(/src="(?<src>[^"?]+?)(?:\?[^"]*)?"/)?.groups
        ?.src;
      const content = script.replace("<script>", "");

      // Skip empty whitespace after the last script tag
      if (content.replace(/\s/, "").length == 0) {
        continue;
      }

      const loaded = new Promise((resolve, reject) => {
        if (src) {
          log(`Injecting the script tag with src ${src}`);
        }
        {
          log(`Injecting an inline script tag`);
        }

        const script_tag = document.createElement("script");
        script_tag.type = "text/javascript";

        if (src) {
          script_tag.src = src;
        } else {
          script_tag.text = content;
        }

        script_tag.onerror = (err) => reject(err);

        let ready = false;
        script_tag.onload = function () {
          if (!ready) {
            ready = true;
            resolve(null);
          }
        };

        footer.appendChild(script_tag);

        // Only script tags with a src must be loaded
        if (!src) {
          resolve(null);
        }
      });

      await loaded;
    }

    log("Successfully injected all dash script tags");
  }

  private async injectDashRenderer(footer: HTMLElement) {
    log("Injecting the ignition for the dash renderer");

    const render_script = await this.worker_manager.executeWithStringResponse(
      "app.renderer",
      {}
    );

    const renderer_script_tag = document.createElement("script");
    renderer_script_tag.id = "_dash-renderer";
    renderer_script_tag.type = "application/javascript";
    renderer_script_tag.text = render_script;

    footer.appendChild(renderer_script_tag);
  }
}

window.web_dash = new WebDash();
 