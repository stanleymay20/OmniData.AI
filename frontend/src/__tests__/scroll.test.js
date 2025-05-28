import { render, screen, fireEvent } from '@testing-library/react';
import Scroll from '../scroll';

test('Scroll Scribe chatbot sends and receives messages', async () => {
  render(<Scroll />);
  const input = screen.getByPlaceholderText('Type your message...');
  fireEvent.change(input, { target: { value: 'test' } });
  fireEvent.keyPress(input, { key: 'Enter', code: 'Enter' });
  const response = await screen.findByText('Scroll Scribe received: test');
  expect(response).toBeInTheDocument();
}); 