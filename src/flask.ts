import { WorkerManager } from "./worker-loader";
import { log } from "./webdash";

/**
 * A small, virtual web server emulating Flask (Python).
 */
export class WebFlask {
  constructor() {
    this.worker = window.workerManager;

    this.originalFetch = window.fetch;
    window.fetch = this.fetch.bind(this);
  }

  /**
   * Sends a POST request to the Python Flask backend.
   * @param req Request Object
   * @param init request payload
   */
  postRequest(req, init) {
    log("[POST Request]", req);

    let data;
    if (init.body) {
      data = `r"""${init.body}"""`
    } else {
      data = "None"
    }

    let content_type;
    if (init.body) {
      content_type = `"application/json"`
    } else {
      content_type = "None"
    }

    return `
    with app.server.app_context():
      with app.server.test_client() as client:
        x = client.open('${req}',
          data=${data},
          content_type=${content_type},
          method="${init.method}",
        )
    x`;
  }

  /**
   * Retrieves a Flask response object and converts it
   * to a compatible Response object.
   * @param codeWillRun stringified python code
   */
  async generateResponse(codeWillRun) {
    log("[2. Flask Request Generated]");
    const flaskRespone = await this.worker.asyncRun(codeWillRun, {});
    log("[5. Flask Response Received]");
    const options = {};
    if (flaskRespone["headers"]) {
      options["headers"] = flaskRespone["headers"];
    }
    if (flaskRespone["status"]) {
      options["status"] = flaskRespone["status"];
    }
    return new Response(flaskRespone["response"], options);
  }

  /**
   * A custom fetch function which intercepts Flask requests
   * and routes to the Python backend.
   * @param req Request object
   * @param init request payload
   */
  async fetch(
    req: Request,
    init?: RequestInit | null | undefined
  ): Promise<Response> {
    // TODO: handle raw requests in addition to strings
    log("[1. Request Intercepted]", req);
    const url = new URL(new Request(req).url);

    if (url.origin == window.location.origin) {
      const resp = await this.generateResponse(this.postRequest(req, init));
      log(`[6. ${url.pathname} done.]`);
      return resp;
    } else {
      log("[Passthrough Request]");
      return this.originalFetch.apply(this, [req, init]);
    }
  }

  worker: WorkerManager;
  originalFetch: (request: any, response: any) => Promise<Response>;
}
