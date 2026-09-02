import { describe, it, expect } from 'vitest';
import { authApi } from '../../src/services/authApi';

describe('authApi Service', () => {
  it('authenticates user and returns JWT token in mock fallback mode', async () => {
    const res = await authApi.login({ email: 'analyst@cybergraph.security', password: 'password123' });
    expect(res.success).toBe(true);
    expect(res.token).toBeDefined();
    expect(res.user.email).toBe('analyst@cybergraph.security');
  });

  it('retrieves current authenticated user session', async () => {
    const res = await authApi.getCurrentUser();
    expect(res.success).toBe(true);
    expect(res.user).toBeDefined();
  });
});
