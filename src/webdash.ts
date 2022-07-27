import { WebFlask } from "./flask";
import { WorkerManager } from "./worker-loader";

declare global {
  export interface Window {
    fetch: Function;
    workerManager: WorkerManager;
    dashApp: string;
    webDash: WebDash;
    log: Function;
  }
}

/**
 * Enables debug logs for development environments.
 */
export let dev = false;
if (process.env.NODE_ENV === "development") {
  dev = true;
}

export function log(...args) {
  if (dev) {
    console.log(...args);
  }
}

/**
 * The entry point for WebDash. It is responsible for
 * instantiating and coordinating the different
 * components which make up the communication
 * between the Dash frontend and the virtual
 * Flask backend running in WASM.
 */
class WebDash {
  constructor() {
    this.workerManager = new WorkerManager();
    window.workerManager = this.workerManager;
    this.webFlask = new WebFlask();

    this.main();
  }

  async main() {
    log("Initialising dash app");
    await this.initialiseDashApp();

    log("Starting book sequence");
    await this.startBootSequence();
    log("Finished boot sequence");
  }

  async initialiseDashApp() {
    return this.workerManager.asyncRun(
      `
import dash
import re

cache_regex = re.compile(r"^v[\\w-]+$")
version_clean = re.compile(r"[^\\w-]")

def new_build_fingerprint(path, version, _hash_value):
  path_parts = path.split("/")
  filename, extension = path_parts[-1].split(".", 1)
  file_path = "/".join(path_parts[:-1] + [filename])
  v_str = re.sub(version_clean, "_", str(version))

  return f"{file_path}.v{v_str}.{extension}"


def new_check_fingerprint(path):
  path_parts = path.split("/")
  name_parts = path_parts[-1].split(".")

  # Check if the resource has a fingerprint
  if len(name_parts) > 2 and cache_regex.match(name_parts[1]):
    original_name = ".".join([name_parts[0]] + name_parts[2:])
    return "/".join(path_parts[:-1] + [original_name]), True

  return path, False

dash.fingerprint.build_fingerprint = new_build_fingerprint
dash.dash.build_fingerprint = new_build_fingerprint

dash.fingerprint.check_fingerprint = new_check_fingerprint
dash.dash.check_fingerprint = new_check_fingerprint

URL_BASE_PATHNAME = "${window.location.pathname.replace(/\/(?:[^\/]+?\.[^\/]*?|index)$/, '/')}";

${window.dashApp}
      `,
      {}
    );
  }

  async startBootSequence() {
    // Inject the meta, title, and css tags
    document.head.innerHTML = `
${await this.workerManager.asyncRun("app._generate_meta_html()", {})}
<title>${await this.workerManager.asyncRun("app.title", {})}</title>
<link rel="icon" type="image/x-icon" href="favicon.ico">
${await this.workerManager.asyncRun("app._generate_css_dist_html()", {})}
    `;

    // Inject the react entry point
    document.body.innerHTML = `${await self.workerManager.asyncRun("dash.dash._app_entry", {})}`;

    // Inject the initial app config
    const footer = document.createElement("footer");
    footer.innerHTML = await self.workerManager.asyncRun("app._generate_config_html()", {});
    document.body.appendChild(footer);

    const scriptChunk = await this.workerManager.asyncRun("app._generate_scripts_html()", {});

    for (const script of scriptChunk.split("</script>")) {
      let src = script.match(/src="(?<src>[^"]+)"/);
      if (src) {
        src = src.groups.src;
      }
      let content = script.replace("<script>", "");

      if (content.replace(/\s/, "").length == 0) {
        continue;
      }

      const promise = new Promise((resolve, reject) => {
        log(`Parsing script tag with src ${src}`);

        const scriptTag = document.createElement("script");

        scriptTag.type = 'text/javascript';

        if (src) {
          scriptTag.src = src;
        } else {
          scriptTag.text = content;
        }

        scriptTag.onerror = (err) => reject(err);

        let r = false;
        scriptTag.onload = scriptTag.onreadystatechange = function() {
          if (!r && (!this.readyState || this.readyState == 'complete')) {
            log(`Successfully loaded the script tag with src ${src}`)
            r = true;
            resolve(null);
          }
        };

        footer.appendChild(scriptTag);

        if (!src) {
          resolve(null);
        }
      });

      await promise;
    }

    log("Successfully loaded all script tags");

    // Inject the app render kickoff
    const rendererScriptTag = document.createElement("script");
    rendererScriptTag.id = "_dash-renderer";
    rendererScriptTag.type = "application/javascript";
    rendererScriptTag.text = await self.workerManager.asyncRun("app.renderer", {});
    footer.appendChild(rendererScriptTag);
  }

  workerManager: WorkerManager;
  webFlask: WebFlask;
  dev: boolean;
}

window.webDash = new WebDash();
