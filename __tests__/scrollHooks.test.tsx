import { render, screen, fireEvent } from '@testing-library/react';
import { useInView } from 'react-intersection-observer';
import { ScrollSection } from '../components/ScrollSection';

// Mock the useInView hook
jest.mock('react-intersection-observer', () => ({
  useInView: jest.fn(),
}));

describe('ScrollSection', () => {
  beforeEach(() => {
    (useInView as jest.Mock).mockReturnValue([null, false]);
  });

  it('renders children correctly', () => {
    render(
      <ScrollSection>
        <div data-testid="test-content">Test Content</div>
      </ScrollSection>
    );

    expect(screen.getByTestId('test-content')).toBeInTheDocument();
  });

  it('applies snap classes when snap prop is true', () => {
    render(
      <ScrollSection snap={true}>
        <div>Test Content</div>
      </ScrollSection>
    );

    const section = screen.getByRole('region');
    expect(section).toHaveClass('snap-start');
    expect(section).toHaveClass('snap-always');
  });

  it('does not apply snap classes when snap prop is false', () => {
    render(
      <ScrollSection snap={false}>
        <div>Test Content</div>
      </ScrollSection>
    );

    const section = screen.getByRole('region');
    expect(section).not.toHaveClass('snap-start');
    expect(section).not.toHaveClass('snap-always');
  });

  it('triggers animation when in view', () => {
    (useInView as jest.Mock).mockReturnValue([null, true]);

    render(
      <ScrollSection>
        <div>Test Content</div>
      </ScrollSection>
    );

    const section = screen.getByRole('region');
    expect(section).toHaveClass('is-revealed');
  });
}); 