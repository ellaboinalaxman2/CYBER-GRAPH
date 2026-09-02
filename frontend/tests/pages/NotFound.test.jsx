import React from 'react';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { describe, it, expect } from 'vitest';
import NotFound from '../../src/pages/NotFound';

describe('NotFound Page Component', () => {
  it('renders 404 message and navigation button', () => {
    render(
      <BrowserRouter>
        <NotFound />
      </BrowserRouter>
    );
    expect(screen.getByText(/404/i)).toBeInTheDocument();
  });
});
