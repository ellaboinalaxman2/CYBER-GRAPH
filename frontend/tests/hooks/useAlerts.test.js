import { describe, it, expect } from 'vitest';
import { useAlerts } from '../../src/hooks/useAlerts';

describe('useAlerts Hook', () => {
  it('is defined as a function', () => {
    expect(typeof useAlerts).toBe('function');
  });
});
