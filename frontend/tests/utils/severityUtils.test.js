import { describe, it, expect } from 'vitest';
import { getSeverityConfig, getSeverityColor } from '../../src/utils/severityUtils';

describe('severityUtils', () => {
  it('returns appropriate config for CRITICAL severity', () => {
    const config = getSeverityConfig('CRITICAL');
    expect(config.label).toBe('Critical');
    expect(config.color).toBe('#ef4444');
    expect(config.priority).toBe(5);
  });

  it('falls back to INFO config for unknown severity', () => {
    const config = getSeverityConfig('UNKNOWN_SEV');
    expect(config.label).toBe('Info');
  });

  it('returns hex color for severity', () => {
    expect(getSeverityColor('HIGH')).toBe('#f97316');
  });
});
