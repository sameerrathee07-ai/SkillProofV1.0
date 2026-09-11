import { useCallback, useEffect, useRef, useState } from "react";

/**
 * Runs an async loader on mount and tracks {data, loading, error}.
 *
 * Every data view in the app needs the same three states, and each of them
 * needs a real empty/error branch rather than a silent blank. `deps` behaves
 * like a useEffect dep list; `reload` re-runs on demand.
 */
export function useApi(loader, deps = []) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Avoid setting state after unmount, and ignore a stale response that lands
  // after a newer one. `alive` is re-armed in the setup, not only cleared in the
  // cleanup: React StrictMode runs cleanup then setup again on the same
  // instance, and a flag that was only ever cleared would leave every loader
  // permanently unable to store its result in development.
  const runId = useRef(0);
  const alive = useRef(true);
  useEffect(() => {
    alive.current = true;
    return () => { alive.current = false; };
  }, []);

  const run = useCallback(async () => {
    const id = ++runId.current;
    setLoading(true);
    setError(null);
    try {
      const result = await loader();
      if (alive.current && id === runId.current) setData(result);
      return result;
    } catch (err) {
      if (alive.current && id === runId.current) setError(err);
      return undefined;
    } finally {
      if (alive.current && id === runId.current) setLoading(false);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);

  useEffect(() => { run(); }, [run]);

  return { data, loading, error, reload: run, setData };
}
