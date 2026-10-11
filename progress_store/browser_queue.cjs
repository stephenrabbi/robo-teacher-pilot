/* Isolated browser queue prototype. Not imported into production classroom. */
(function (root, factory) {
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  else root.RoboTeacherSyntheticSync = api;
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  "use strict";
  const STORAGE_KEY = "roboTeacherSyntheticPending:v1";
  const MAX_EVENTS = 200;

  function read(storage) {
    try {
      const raw = storage.getItem(STORAGE_KEY);
      if (!raw) return [];
      const parsed = JSON.parse(raw);
      if (!Array.isArray(parsed) || parsed.length > MAX_EVENTS) throw Error("Invalid queue");
      if (!parsed.every(x => x && typeof x.id === "string" && x.id.length > 0 &&
          x.event && typeof x.event === "object" && x.event.event_id === x.id))
        throw Error("Invalid queue entry");
      return parsed;
    } catch (_) {
      // Malformed local state is not silently erased: fail closed for recovery.
      throw Error("Pending progress requires recovery");
    }
  }
  function save(storage, queue) {
    if (queue.length > MAX_EVENTS) throw Error("Pending progress limit reached");
    storage.setItem(STORAGE_KEY, JSON.stringify(queue));
  }
  function enqueue(storage, event) {
    if (!event || typeof event.event_id !== "string" || !event.event_id) throw Error("Invalid event");
    const queue = read(storage);
    const found = queue.find(x => x.id === event.event_id);
    if (found) {
      if (JSON.stringify(found.event) !== JSON.stringify(event)) throw Error("Conflicting event ID");
      return queue.length;
    }
    queue.push({ id: event.event_id, event: structuredClone(event) });
    save(storage, queue);
    return queue.length;
  }
  async function flush(storage, submit) {
    const queue = read(storage);
    let acknowledged = 0;
    for (const entry of queue) {
      let accepted;
      try {
        accepted = await submit(structuredClone(entry.event));
      } catch (_) {
        return { acknowledged, pending: read(storage).length, synchronized: false };
      }
      if (accepted !== true && accepted !== false) {
        return { acknowledged, pending: read(storage).length, synchronized: false };
      }
      const latest = read(storage);
      const index = latest.findIndex(x => x.id === entry.id);
      if (index < 0) throw Error("Pending event changed during sync");
      latest.splice(index, 1);
      save(storage, latest);
      acknowledged += 1;
    }
    return { acknowledged, pending: read(storage).length, synchronized: true };
  }
  return { STORAGE_KEY, read, enqueue, flush };
});
