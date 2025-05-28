import { render, screen, fireEvent } from '@testing-library/react';
import { ScrollSeal } from '../components/ScrollSeal';
import { MiniScrollSeal } from '../components/MiniScrollSeal';
import { ScrollSpinner } from '../components/ScrollSpinner';
import { ScrollScene } from '../components/ScrollScene';

// Mock GSAP
jest.mock('gsap', () => ({
  context: jest.fn(() => ({ revert: jest.fn() })),
  fromTo: jest.fn(),
  to: jest.fn(),
}));

// Mock ScrollTrigger
jest.mock('gsap/ScrollTrigger', () => ({
  registerPlugin: jest.fn(),
}));

describe('Scroll Components', () => {
  describe('ScrollSeal', () => {
    it('renders with default size', () => {
      render(<ScrollSeal />);
      const seal = screen.getByAltText('Scroll Seal');
      expect(seal).toBeInTheDocument();
      expect(seal).toHaveAttribute('width', '80');
      expect(seal).toHaveAttribute('height', '80');
    });

    it('renders with custom size', () => {
      render(<ScrollSeal size={40} />);
      const seal = screen.getByAltText('Scroll Seal');
      expect(seal).toHaveAttribute('width', '40');
      expect(seal).toHaveAttribute('height', '40');
    });
  });

  describe('MiniScrollSeal', () => {
    it('renders with default size', () => {
      render(<MiniScrollSeal />);
      const seal = screen.getByAltText('Scroll Seal');
      expect(seal).toBeInTheDocument();
      expect(seal).toHaveAttribute('width', '24');
      expect(seal).toHaveAttribute('height', '24');
    });

    it('applies hover animation class when animateOnHover is true', () => {
      render(<MiniScrollSeal animateOnHover={true} />);
      const container = screen.getByRole('img').parentElement;
      expect(container).toHaveClass('hover:animate-scroll-spin');
    });
  });

  describe('ScrollSpinner', () => {
    it('renders with default size', () => {
      render(<ScrollSpinner />);
      const spinner = screen.getByRole('img');
      expect(spinner).toBeInTheDocument();
      expect(spinner.parentElement).toHaveClass('w-64');
    });

    it('renders with custom size', () => {
      render(<ScrollSpinner size={32} />);
      const spinner = screen.getByRole('img');
      expect(spinner.parentElement).toHaveClass('w-32');
    });
  });

  describe('ScrollScene', () => {
    it('renders children and seal', () => {
      render(
        <ScrollScene>
          <div data-testid="test-content">Test Content</div>
        </ScrollScene>
      );

      expect(screen.getByTestId('test-content')).toBeInTheDocument();
      expect(screen.getByAltText('Scroll Seal')).toBeInTheDocument();
    });

    it('hides seal when showSeal is false', () => {
      render(
        <ScrollScene showSeal={false}>
          <div>Test Content</div>
        </ScrollScene>
      );

      expect(screen.queryByAltText('Scroll Seal')).not.toBeInTheDocument();
    });
  });
}); 