import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Paper,
  TextField,
  Button,
  Typography,
  CircularProgress,
  List,
  ListItem,
  ListItemText,
  Divider
} from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import axiosInstance from '../utils/axios';

interface Message {
  id: string;
  content: string;
  timestamp: string;
  isAI: boolean;
  forecast?: {
    prediction: string;
    confidence: number;
    timeframe: string;
  };
}

const ScrollChat: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<null | HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      content: input,
      timestamp: new Date().toISOString(),
      isAI: false
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await axiosInstance.post('/prophecy/chat', {
        message: input
      });

      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: response.data.response,
        timestamp: new Date().toISOString(),
        isAI: true,
        forecast: response.data.forecast
      };

      setMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Paper sx={{ flex: 1, overflow: 'auto', p: 2, mb: 2 }}>
        <List>
          {messages.map((message) => (
            <React.Fragment key={message.id}>
              <ListItem
                alignItems="flex-start"
                sx={{
                  flexDirection: message.isAI ? 'row' : 'row-reverse',
                  mb: 2
                }}
              >
                <Paper
                  sx={{
                    p: 2,
                    maxWidth: '70%',
                    bgcolor: message.isAI ? 'primary.light' : 'secondary.light',
                    color: message.isAI ? 'primary.contrastText' : 'secondary.contrastText'
                  }}
                >
                  <ListItemText
                    primary={message.content}
                    secondary={
                      message.forecast && (
                        <Box sx={{ mt: 1 }}>
                          <Typography variant="subtitle2">
                            Forecast: {message.forecast.prediction}
                          </Typography>
                          <Typography variant="caption">
                            Confidence: {message.forecast.confidence}%
                          </Typography>
                          <Typography variant="caption" display="block">
                            Timeframe: {message.forecast.timeframe}
                          </Typography>
                        </Box>
                      )
                    }
                  />
                </Paper>
              </ListItem>
              <Divider />
            </React.Fragment>
          ))}
          <div ref={messagesEndRef} />
        </List>
      </Paper>

      <Box sx={{ display: 'flex', gap: 1 }}>
        <TextField
          fullWidth
          variant="outlined"
          placeholder="Ask for a prophecy..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSend()}
          disabled={loading}
        />
        <Button
          variant="contained"
          color="primary"
          endIcon={loading ? <CircularProgress size={20} /> : <SendIcon />}
          onClick={handleSend}
          disabled={loading}
        >
          Send
        </Button>
      </Box>
    </Box>
  );
};

export default ScrollChat; 