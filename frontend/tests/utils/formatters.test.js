import { describe, it, expect } from 'vitest';
import { formatPercentage, formatRiskScore, truncateHash } from '../../src/utils/formatters';

describe('formatters utility functions', () => {
  it('formats decimal numbers as percentages', () => {
    expect(formatPercentage(0.94)).toBe('94%');
    expect(formatPercentage(0.5)).toBe('50%');
    expect(formatPercentage(94)).toBe('94%');
  });

  it('formats risk scores', () => {
    expect(formatRiskScore(88)).toBe('88 / 100');
    expect(formatRiskScore(0.88)).toBe('88 / 100');
  });

  it('truncates blockchain hashes correctly', () => {
    const hash = '0xabc123789fed456123456789abcdef0123456789abcdef0123456789abcdef01';
    const truncated = truncateHash(hash, 8, 6);
    expect(truncated).toBe('0xabc123...cdef01');
  });
});
