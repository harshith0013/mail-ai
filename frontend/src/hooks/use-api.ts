import { useState, useEffect, useCallback } from 'react';

interface UseApiResult<T> {
  data: T | null;
  isLoading: boolean;
  error: Error | null;
  refetch: () => Promise<void>;
}

export function useApi<T>(
  apiFunc: () => Promise<T>,
  deps: any[] = [],
  lazy: boolean = false
): UseApiResult<T> {
  const [data, setData] = useState<T | null>(null);
  const [isLoading, setIsLoading] = useState(!lazy);
  const [error, setError] = useState<Error | null>(null);

  const fetchData = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const result = await apiFunc();
      setData(result);
    } catch (err: any) {
      setError(err instanceof Error ? err : new Error(err?.response?.data?.detail || err?.message || 'An unknown error occurred'));
    } finally {
      setIsLoading(false);
    }
  }, [apiFunc]);

  useEffect(() => {
    if (!lazy) {
      fetchData();
    }
  }, deps); // deps array intentionally separate

  return { data, isLoading, error, refetch: fetchData };
}
