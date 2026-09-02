import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import Button from '../../src/components/common/Button';

describe('Button Component', () => {
  it('renders button with label and responds to clicks', () => {
    const handleClick = vi.fn();
    render(<Button onClick={handleClick}>Inspect Node</Button>);
    const btn = screen.getByText('Inspect Node');
    expect(btn).toBeInTheDocument();
    fireEvent.click(btn);
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('disables button when disabled prop is set', () => {
    render(<Button disabled>Loading Telemetry</Button>);
    const btn = screen.getByRole('button');
    expect(btn).toBeDisabled();
  });
});
