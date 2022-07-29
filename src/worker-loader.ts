import { log } from "./webdash";
/**
 * A small queue where we queue "OnSuccess" functions
 * for each request sent. For each request, a success
 * function gets queued. Upon each incoming message,
 * we dequeue and execute the "OnSuccess function".
 *
 * TODO: Implement a more efficient queuing system.
 */
class ResponseQueue {
  constructor() {
    this.queue = [];
  }
  enqueue(onSuccessFn: Function) {
    return this.queue.push(onSuccessFn);
  }
  dequeue() {
    return this.queue.shift();
  }

  queue: Array<Function>;
}

type Payload = { [key: string]: any };

/**
 * This class is used as an intermediary between
 * the WebWorker and the application client.
 * It currently supports two main message types:
 *
 *  1. HTTP Request/Response objects.
 *  2. binary file transfers.
 */
export class WorkerManager {
  queue: ResponseQueue;
  worker: Worker;

  constructor() {
    this.queue = new ResponseQueue();
    this.worker = new Worker("./worker.js");
  }

  /**
   * Runs Python code on the WebWorker.
   * @param script python script
   * @param context additional payload
   * @param onSuccess callback function if executed successfully
   * @param onError callback function for if errored
   */
  run(
    script: string,
    context: Payload,
    onSuccess: Function,
    onError: Function
  ): void {
    this.queue.enqueue(onSuccess);
    this.worker.onerror = (e) => onError(e);
    this.worker.onmessage = this.processMessage.bind(this);
    this.worker.postMessage({
      ...context,
      python: script,
    });
  }

  /**
   * Processes messages received by the 'run' function.
   * This includes console.log messages for the intitial
   * bootstrap phase.
   * @param e Message object
   * @returns void or resolved promise
   */
  processMessage(e): Function | void {
    log("[4. Message received from worker]");

    // Update status tracker if this is a console.log message
    if (e.data.consoleMessage) {
      const statusBar = document.querySelector(".status");
      if (statusBar) {
        statusBar.innerHTML = e.data.consoleMessage;
      }
      return;
    }

    // Otherwise this is a response for dash-renderer
    // and we should act on it.
    const success = this.queue.dequeue()!;
    return success(e.data.results);
  }

  /**
   * Runs a Python script on the WebWorker.
   * @param script python script to run
   * @param context optional additional arguments
   * @returns BlobPart or string
   */
  async executeWithAnyResponse(script: string, context: Payload): Promise<any> {
    return await (new Promise(
      (onSuccess: Function, onError: (e: ErrorEvent) => any) => {
        this.run(script, context, onSuccess, onError);
      }
    ));
  }

  /**
   * Runs a Python script on the WebWorker.
   * @param script python script to run
   * @param context optional additional arguments
   * @returns BlobPart
   */
  async executeWithBinaryResponse(script: string, context: Payload): Promise<BlobPart> {
    const result: any = await this.executeWithAnyResponse(script, context);

    if (result as BlobPart) {
      return result as BlobPart;
    }

    throw TypeError("Expected binary WebFlask response but received String");
  }

  /**
   * Runs a Python script on the WebWorker.
   * @param script python script to run
   * @param context optional additional arguments
   * @returns string
   */
  async executeWithStringResponse(script: string, context: Payload): Promise<string> {
    const result: any = await this.executeWithAnyResponse(script, context);

    if (result as string) {
      return result as string;
    }

    throw TypeError("Expected String WebFlask response but received binary");
  }
}
