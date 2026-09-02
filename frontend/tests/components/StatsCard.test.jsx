import React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import StatsCard from '../../src/components/dashboard/StatsCard';

describe('StatsCard Component', () => {
  it('renders title and numerical metrics properly', () => {
    render(<StatsCard title="Total Assets" value={128} subtitle="Mapped in Neo4j" />);
    expect(screen.getByText('Total Assets')).toBeInTheDocument();
    expect(screen.getByText('128')).toBeInTheDocument();
    expect(screen.getByText('Mapped in Neo4j')).toBeInTheDocument();
  });
});
