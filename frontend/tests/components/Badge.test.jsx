import React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import Badge from '../../src/components/common/Badge';

describe('Badge Component', () => {
  it('renders children text correctly', () => {
    render(<Badge>CRITICAL THREAT</Badge>);
    expect(screen.getByText('CRITICAL THREAT')).toBeInTheDocument();
  });

  it('renders severity styles for HIGH severity', () => {
    render(<Badge severity="HIGH">High Alert</Badge>);
    const badge = screen.getByText('High Alert');
    expect(badge).toBeInTheDocument();
  });
});
